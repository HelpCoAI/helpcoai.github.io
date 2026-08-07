#!/usr/bin/env python3
"""
Airtable staging base -- create, push, pull.

Airtable is the HUMAN REVIEW layer, not the database. A reviewer works the
priority-A queue top-down filling in what they find; verified records are pulled
back out into Postgres, which stays the single source of truth.

The sync is deliberately ONE-WAY: Airtable -> Postgres. Nothing is ever written
back from production into Airtable. Two writable copies of the same record is how
you end up unable to say which one is true.

Three tables, and the shape of them encodes the hub decision (see
docs/hub-representation.md):

    Candidates  the BMF review queue -- organizations, not awards
    Hubs        one application covering many named awards
    Awards      named awards; Hub link is nullable (null = applies directly)

Usage:
    export AIRTABLE_TOKEN=pat...            # needs schema.bases:write, data.records:*
    python3 11_airtable.py create-base --workspace wspXXXXXXXXXXXXXX
    export AIRTABLE_BASE=appXXXXXXXXXXXXXX  # printed by create-base
    python3 11_airtable.py push --priority A,B
    python3 11_airtable.py pull --out data/08_verified.csv
    python3 11_airtable.py status

Needs real egress; the build sandbox's proxy denies CONNECT.

CAPACITY NOTE. Airtable's record cap is per BASE, not per table: 1,000 free /
50,000 Team. Priority A+B is 580 candidates, so the review queue alone fits free --
but the district crawl is expected to add 400-600 awards plus hubs to the same base,
which lands right on the free ceiling. Assume the $20/mo Team plan from the point
awards start arriving. That is inside the budgeted operating floor and not worth
contorting the schema to avoid.
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.airtable.com/v0"
RATE_DELAY = 0.25          # Airtable hard-caps at 5 req/sec per base
BATCH = 10                 # records per write request

SCOPE_CHOICES = [
    {"name": "open", "color": "greenLight2"},
    {"name": "nomination_only", "color": "yellowLight2"},
    {"name": "members_only", "color": "orangeLight2"},
    {"name": "employees_only", "color": "redLight2"},
    {"name": "closed", "color": "grayLight2"},
    {"name": "unknown", "color": "grayLight1"},
]
PLATFORM_CHOICES = [{"name": n} for n in (
    "CommunityForce", "AwardSpring", "Scholarship America", "Foundant",
    "SmarterSelect", "Google Form", "own website", "email", "paper", "other")]
STATUS_CHOICES = [
    {"name": "Not started", "color": "grayLight2"},
    {"name": "In review", "color": "yellowLight2"},
    {"name": "Verified - has program", "color": "greenLight2"},
    {"name": "Verified - no program", "color": "redLight2"},
    {"name": "Can't determine", "color": "orangeLight2"},
    {"name": "Duplicate", "color": "grayLight1"},
]


def money(name, desc=""):
    return {"name": name, "type": "currency",
            "options": {"precision": 0, "symbol": "$"}, "description": desc}


def num(name, precision=0, desc=""):
    return {"name": name, "type": "number",
            "options": {"precision": precision}, "description": desc}


def check(name, desc=""):
    return {"name": name, "type": "checkbox",
            "options": {"icon": "check", "color": "greenBright"}, "description": desc}


def date(name, desc=""):
    return {"name": name, "type": "date",
            "options": {"dateFormat": {"name": "iso"}}, "description": desc}


def select(name, choices, desc=""):
    return {"name": name, "type": "singleSelect",
            "options": {"choices": choices}, "description": desc}


def text(name, desc="", long=False):
    return {"name": name, "type": "multilineText" if long else "singleLineText",
            "description": desc}


def url(name, desc=""):
    return {"name": name, "type": "url", "description": desc}


# --------------------------------------------------------------- schema

TABLES = [
    {
        "name": "Candidates",
        "description": ("BMF-derived review queue. One row per ORGANIZATION, not per "
                        "award. Work top-down by Priority; stop when yield drops off."),
        "fields": [
            text("Org Name", "Resolved display name. For bare national parents this is "
                             "the local chapter derived from BMF SORT_NAME."),
            text("BMF Name", "Verbatim IRS Business Master File name."),
            text("EIN", "Employer ID number. The upsert key -- do not edit."),
            select("Priority", [{"name": c} for c in "ABCD"],
                   "A = verify first. Score is NOT a good within-tier sort; the "
                   "highest-scoring org in the pilot was employees-only."),
            num("Score", 0, "BMF heuristic score. Weakly predictive inside tier A."),
            text("City"), text("County"),
            text("Search Query", "Paste into a search engine to start the review."),
            text("Signals", "Which scoring rules fired."),
            money("Assets"), money("Revenue"),
            check("Files 990PF"),
            check("Chapter Resolved", "Org Name was rewritten from a national parent."),
            select("Review Status", STATUS_CHOICES),
            url("Website URL"),
            url("Program URL", "Page describing the scholarship itself, not the homepage."),
            select("Beneficiary Scope", SCOPE_CHOICES,
                   "Only open and nomination_only belong in a student's match list."),
            text("Notes", long=True),
            date("Reviewed At"),
        ],
    },
    {
        "name": "Hubs",
        "description": ("One application covering many named awards -- education and "
                        "community foundations. Highest value per hour of review."),
        "fields": [
            text("Hub Name"),
            text("Organization"),
            text("Counties", "Comma-separated."),
            url("Apply URL", "The single common application."),
            select("Platform", PLATFORM_CHOICES),
            date("Opens"), date("Deadline"),
            num("Child Award Count", 0, "Named awards behind this application, as published."),
            money("Annual Dollars", "Total awarded per year, as published."),
            money("Amount Min"), money("Amount Max"),
            num("Effort Minutes", 0,
                "Time for the ONE application. Effort is attributed to the hub once, "
                "never multiplied by matched children -- that is what makes hubs rank "
                "correctly in expected-value-per-hour."),
            url("Source URL"),
            date("Verified At"),
            text("Notes", long=True),
        ],
    },
    {
        "name": "Awards",
        "description": "Named awards. Hub link empty means the student applies directly.",
        "fields": [
            text("Award Name"),
            money("Amount Min"), money("Amount Max"),
            num("Num Awards", 0),
            num("Applicants Estimated", 0,
                "Capture whenever a sponsor publishes it. Rotary Hudson published "
                "19 applicants for 5 awards -- a 26% win rate. This is the number "
                "the whole expected-value ranking rests on and no competitor has it."),
            date("Deadline"),
            select("Beneficiary Scope", SCOPE_CHOICES),
            check("Distinct Eligibility",
                  "TRUE = this award's criteria differ from its hub's (own GPA bar, "
                  "school list, major, or amount). Drives whether it earns its own "
                  "indexable page. FALSE = a named fund behind identical criteria; it "
                  "lives as a row on the hub page, never a standalone URL. This one "
                  "checkbox is the defense against scaled-content-abuse penalties."),
            text("Eligibility Raw", "Verbatim as published. Never paraphrase.", long=True),
            text("Counties"), text("High Schools"), text("Majors"),
            num("GPA Min", 2),
            url("Apply URL"),
            select("Platform", PLATFORM_CHOICES),
            check("Essay Required"),
            url("Source URL"),
            date("Verified At"),
        ],
    },
]

# Candidates CSV column -> Airtable field
PUSH_MAP = {
    "display_name": "Org Name", "name": "BMF Name", "ein": "EIN",
    "priority": "Priority", "score": "Score", "city": "City", "county": "County",
    "search_query": "Search Query", "signals": "Signals",
    "assets": "Assets", "revenue": "Revenue",
}


# --------------------------------------------------------------- http

def req(method, path, body=None, token=None):
    token = token or os.environ.get("AIRTABLE_TOKEN")
    if not token:
        sys.exit("AIRTABLE_TOKEN not set (create one at airtable.com/create/tokens)")
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(
        f"{API}{path}", data=data, method=method,
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=45) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:400]
        sys.exit(f"Airtable {e.code} on {method} {path}\n{detail}")
    except urllib.error.URLError as e:
        reason = str(e.reason)
        if "403" in reason or "tunnel" in reason.lower() or "CONNECT" in reason:
            sys.exit("Egress blocked by the proxy -- run this where network is open.")
        sys.exit(f"Network error: {reason}")
    finally:
        time.sleep(RATE_DELAY)


# --------------------------------------------------------------- commands

# Link fields cannot be declared at base-creation time -- they need table IDs that
# do not exist yet. Added in a second pass.
#   (table, field name, points at, description)
LINKS = [
    ("Awards", "Sponsor", "Candidates",
     "The organization behind this award."),
    ("Awards", "Hub", "Hubs",
     "Empty means the student applies directly to the sponsor. Set means this award "
     "is one of many behind a single common application -- the tracker must then "
     "count ONE application, not one per award."),
]


def cmd_create_base(workspace, name):
    out = req("POST", "/meta/bases", {
        "name": name, "workspaceId": workspace, "tables": TABLES})
    base_id = out["id"]
    ids = {t["name"]: t["id"] for t in out.get("tables", [])}

    print(f"Created base {name}\n  id: {base_id}")
    for t in out.get("tables", []):
        print(f"  {t['name']:<12} {t['id']}  ({len(t['fields'])} fields)")

    for tbl, field, target, desc in LINKS:
        req("POST", f"/meta/bases/{base_id}/tables/{ids[tbl]}/fields", {
            "name": field, "type": "multipleRecordLinks",
            "description": desc,
            "options": {"linkedTableId": ids[target]}})
        print(f"  link  {tbl}.{field} -> {target}")

    print(f"\n  https://airtable.com/{base_id}")
    print(f"\nexport AIRTABLE_BASE={base_id}")
    return base_id


def _table_id(base, name):
    for t in req("GET", f"/meta/bases/{base}/tables")["tables"]:
        if t["name"] == name:
            return t["id"]
    sys.exit(f"Table {name!r} not found in {base}")


def cmd_push(base, csv_path, priorities, limit):
    want = {p.strip().upper() for p in priorities.split(",")}
    rows = [r for r in csv.DictReader(open(csv_path))
            if r["priority"].upper() in want]
    if limit:
        rows = rows[:limit]
    if not rows:
        sys.exit("No rows matched")

    tbl = _table_id(base, "Candidates")
    sent = 0
    for i in range(0, len(rows), BATCH):
        chunk = rows[i:i + BATCH]
        records = []
        for r in chunk:
            f = {}
            for src, dst in PUSH_MAP.items():
                v = (r.get(src) or "").strip()
                if not v:
                    continue
                f[dst] = int(v) if dst in {"Score", "Assets", "Revenue"} and \
                    v.lstrip("-").isdigit() else v
            f["Files 990PF"] = r.get("files_990pf") == "Y"
            f["Chapter Resolved"] = r.get("chapter_resolved") == "Y"
            f["Review Status"] = "Not started"
            records.append({"fields": f})

        # Upsert on EIN so re-running never duplicates a row a human has edited
        req("PATCH", f"/{base}/{tbl}", {
            "performUpsert": {"fieldsToMergeOn": ["EIN"]},
            "records": records, "typecast": True})
        sent += len(chunk)
        print(f"  {sent}/{len(rows)}", end="\r", flush=True)

    print(f"\nUpserted {sent} candidates into {base}/Candidates")


def _all_records(base, tbl):
    out, offset = [], None
    while True:
        q = f"?pageSize=100" + (f"&offset={offset}" if offset else "")
        page = req("GET", f"/{base}/{tbl}{q}")
        out += page.get("records", [])
        offset = page.get("offset")
        if not offset:
            return out


def cmd_pull(base, out_path):
    hubs = {r["id"]: r["fields"] for r in _all_records(base, _table_id(base, "Hubs"))}
    awards = _all_records(base, _table_id(base, "Awards"))
    cands = {r["id"]: r["fields"] for r in _all_records(base, _table_id(base, "Candidates"))}

    rows = []
    for a in awards:
        f = dict(a["fields"])
        hub_ids = f.pop("Hub", []) or []
        spon_ids = f.pop("Sponsor", []) or []
        hub = hubs.get(hub_ids[0]) if hub_ids else None
        f["hub_name"] = hub.get("Hub Name") if hub else ""
        f["hub_apply_url"] = hub.get("Apply URL") if hub else ""
        f["hub_deadline"] = hub.get("Deadline") if hub else ""
        f["sponsor_ein"] = cands.get(spon_ids[0], {}).get("EIN", "") if spon_ids else ""
        f["airtable_id"] = a["id"]
        rows.append(f)

    if not rows:
        sys.exit("No awards in the base yet -- nothing to pull.")

    cols = sorted({k for r in rows for k in r})
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: (json.dumps(v) if isinstance(v, (list, dict)) else v)
                        for k, v in r.items()})

    indexable = sum(1 for r in rows if r.get("Distinct Eligibility"))
    open_scope = sum(1 for r in rows if r.get("Beneficiary Scope") == "open")
    print(f"{len(rows)} awards -> {out_path}")
    print(f"  {len(hubs)} hubs · {indexable} with distinct eligibility (own page) "
          f"· {open_scope} openly applicable")


def cmd_status(base):
    from collections import Counter
    cands = _all_records(base, _table_id(base, "Candidates"))
    by = Counter(r["fields"].get("Review Status", "Not started") for r in cands)
    done = sum(v for k, v in by.items() if k.startswith("Verified"))
    print(f"Candidates: {len(cands)}")
    for k, v in by.most_common():
        print(f"  {k:<26}{v:>5}")
    if cands:
        print(f"\nReviewed: {done}/{len(cands)} ({done/len(cands):.0%})")
    hubs = _all_records(base, _table_id(base, "Hubs"))
    awards = _all_records(base, _table_id(base, "Awards"))
    print(f"Hubs: {len(hubs)}   Awards: {len(awards)}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create-base")
    c.add_argument("--workspace", required=True, help="wspXXXXXXXXXXXXXX")
    c.add_argument("--name", default="Scholarship Verification (Pilot)")

    for nm in ("push", "pull", "status"):
        s = sub.add_parser(nm)
        s.add_argument("--base", default=os.environ.get("AIRTABLE_BASE"))
        if nm == "push":
            s.add_argument("--csv", default=str(ROOT / "data" / "05_pilot_candidates.csv"))
            s.add_argument("--priority", default="A,B")
            s.add_argument("--limit", type=int, default=0)
        if nm == "pull":
            s.add_argument("--out", default=str(ROOT / "data" / "08_verified.csv"))

    a = p.parse_args()
    if a.cmd == "create-base":
        cmd_create_base(a.workspace, a.name)
    else:
        if not a.base:
            sys.exit("--base or AIRTABLE_BASE required")
        if a.cmd == "push":
            cmd_push(a.base, a.csv, a.priority, a.limit)
        elif a.cmd == "pull":
            cmd_pull(a.base, a.out)
        else:
            cmd_status(a.base)
