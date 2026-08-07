#!/usr/bin/env python3
"""
Second pass over extracted awards: repair what regex got wrong, fill what it
could not reach, and throw out what is not an award at all.

This is the alternative to hand-reviewing every record. The expensive part is
already done -- 19_declutter and 20_extract compressed 353,000 words of pages
into a few hundred bounded blocks, each carrying its own verbatim eligibility
text. This pass reads only those blocks, so the whole corpus costs well under a
dollar and can be re-run on every refresh instead of once, heroically, by hand.

What it fixes, from a hand audit of the regex output:
  - name boundaries       "Purchase Tickets OPAL Awards" -> "OPAL Awards"
  - amounts from the wrong sentence   $15 for Native Forward Scholars Fund
  - records that are not awards       event tickets, donate buttons, alumni honours
  - every sparse field the page states in prose that no regex was going to catch

Three invariants, and the whole point of the design:

  eligibility_raw is NEVER rewritten. The model reads it and never replaces it.
  It is the audit trail; if a student disputes a match, the raw text is the
  answer, and an answer a model paraphrased is not an audit trail.

  Absent stays absent. The prompt says so and verify() enforces it: a field the
  block does not state comes back empty, not guessed and not defaulted to false.
  Filtering a student OUT on an invented requirement costs them an award they
  could have won.

  Every response is cached on a hash of (eligibility_raw, PROMPT_VERSION), so a
  re-run costs nothing for unchanged records and a prompt edit correctly
  invalidates everything.

Usage:
    export ANTHROPIC_API_KEY=...
    python3 21_enrich.py --in data/15_awards.csv --out data/16_awards_enriched.csv
    python3 21_enrich.py --dry-run          # plumbing + cost estimate, no API calls
    python3 21_enrich.py --limit 20         # cheap real sample before the full run
"""

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MODEL = "claude-haiku-4-5-20251001"
PROMPT_VERSION = "v3"          # bump to invalidate the cache deliberately
CACHE_DIR = Path("data/.enrich_cache")
MAX_WORKERS = 8

# Rough Haiku pricing, $/million tokens. Used only for the estimate printed
# before a run so nobody is surprised by the bill; never for billing itself.
PRICE_IN, PRICE_OUT = 1.00, 5.00

LIST_FIELDS = ["counties", "cities", "high_schools", "majors", "activities",
               "clubs_organizations", "college_plan", "citizenship", "heritage",
               "class_year", "enrollment_status", "destination_institutions"]
BOOL_FIELDS = ["need_based", "merit_based", "first_generation", "disability",
               "residency_required", "renewable", "essay_required",
               "transcript_required", "fafsa_required"]
SCALAR_FIELDS = ["name", "sponsor", "amount_min", "amount_max", "num_awards",
                 "deadline", "opens", "gpa_min", "gpa_scale", "gender",
                 "military_affiliation", "employer_affiliation", "income_max",
                 "renewal_years", "recommendation_letters", "beneficiary_scope",
                 "geo_scope", "estimated_effort_minutes"]

VERDICTS = {"award", "not_an_award", "recognition_only", "aggregate_page"}

SYSTEM = f"""You normalise scholarship records that a regex extractor pulled off
school and foundation web pages. The extractor is noisy: it mis-cuts award names,
grabs dollar figures from neighbouring sentences, and sometimes emits things that
are not awards at all (event tickets, donate buttons, alumni honours).

You are given ONE block of raw page text plus the extractor's guesses. Return
JSON only. No prose, no code fences.

THE ONE RULE THAT MATTERS: only state what the block states. If the block does
not mention a requirement, that field is null or []. Never infer, never default,
never fill a field because it is usually true of scholarships. A student filtered
OUT by a requirement you invented loses an award they could have won, and nobody
will ever find out. Leaving a field empty is always the safe answer.

Set "verdict":
  "award"            a scholarship/grant a student can apply for or be nominated for
  "recognition_only" an honour or prize given without an application (alumni
                     awards, hall of fame, teacher of the year)
  "aggregate_page"   describes a programme or a whole list, not one specific award
  "not_an_award"     anything else: event tickets, donation appeals, navigation

Fields:
  name          the award's actual title, trimmed of surrounding page text.
  sponsor       the organisation that funds or administers it.
  amount_min / amount_max   integer dollars for ONE award to ONE recipient.
                Never the programme total and never a four-year value unless the
                block says a single recipient receives it. null if unstated.
  num_awards    how many are given per cycle, if stated.
  deadline / opens   as written in the block; do not convert or guess a year.
  gpa_min, gpa_scale, income_max, renewal_years, recommendation_letters,
  estimated_effort_minutes   numbers; the last is your estimate of applicant
                effort from what is actually required (essay length, letters,
                forms). Null if the block says too little to judge.
  gender        "female" | "male" | "any" | null
  beneficiary_scope  "open" | "nomination_only" | "members_only" |
                "employees_only" | "closed" | null
  geo_scope     "national" | "state" | "county" | "city" | "school" | null --
                the tightest geography the block actually restricts to.
  booleans      true only if the block states it; otherwise null. NEVER false.
  lists         [] when unstated. Verbatim terms from the block, not synonyms.

Return exactly:
{{"verdict": "...", "confidence": 0.0-1.0, "name": "...", "sponsor": "...",
 "amount_min": null, "amount_max": null, "num_awards": null, "deadline": null,
 "opens": null, "gpa_min": null, "gpa_scale": null, "income_max": null,
 "renewal_years": null, "recommendation_letters": null,
 "estimated_effort_minutes": null, "gender": null, "beneficiary_scope": null,
 "geo_scope": null, "military_affiliation": null, "employer_affiliation": null,
 {", ".join(f'"{b}": null' for b in BOOL_FIELDS)},
 {", ".join(f'"{l}": []' for l in LIST_FIELDS)}}}
"""


def cache_key(raw: str) -> str:
    return hashlib.sha256(f"{PROMPT_VERSION}\x00{MODEL}\x00{raw}".encode()).hexdigest()


def cached(key):
    p = CACHE_DIR / f"{key}.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError:
            p.unlink(missing_ok=True)
    return None


def put_cache(key, obj):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / f"{key}.json").write_text(json.dumps(obj))


def build_user_msg(rec):
    guesses = {k: rec.get(k, "") for k in
               ("name", "sponsor", "amount_min", "amount_max", "deadline", "gpa_min")}
    return (f"Extractor guesses (verify or correct all of them):\n"
            f"{json.dumps(guesses, indent=1)}\n\n"
            f"Source: {rec.get('source_url', '')}\n"
            f"Listing organisation: {rec.get('source_org', '')}\n\n"
            f"BLOCK:\n{rec['eligibility_raw'][:6000]}")


def parse_response(text):
    text = re.sub(r"^\s*```(?:json)?|```\s*$", "", text.strip(), flags=re.M).strip()
    obj = json.loads(text)
    if not isinstance(obj, dict):
        raise ValueError("not an object")
    return obj


def verify(obj, rec):
    """
    Coerce the model's answer into the schema and re-assert the invariants.

    The prompt asks for these; this function is what makes them true. A prompt is
    a request, and a request is not a guarantee -- notably 'never false', which
    models reach for constantly because most training data encodes absence as
    false.
    """
    out = {}
    if obj.get("verdict") not in VERDICTS:
        raise ValueError(f"bad verdict {obj.get('verdict')!r}")
    out["verdict"] = obj["verdict"]
    try:
        out["confidence"] = round(min(1.0, max(0.0, float(obj.get("confidence", 0)))), 2)
    except (TypeError, ValueError):
        out["confidence"] = ""

    for f in SCALAR_FIELDS:
        v = obj.get(f)
        out[f] = "" if v in (None, "", "null", "unknown", "N/A") else v
    for f in BOOL_FIELDS:
        v = obj.get(f)
        # true or unknown. Never false: absent means unstated, and a stored
        # false is indistinguishable downstream from a verified "not required".
        out[f] = True if v is True else ""
    for f in LIST_FIELDS:
        v = obj.get(f)
        out[f] = [str(x).strip() for x in v if str(x).strip()] if isinstance(v, list) else []

    for f in ("amount_min", "amount_max", "income_max", "num_awards",
              "renewal_years", "recommendation_letters", "estimated_effort_minutes"):
        if out[f] != "":
            m = re.search(r"\d[\d,]*", str(out[f]))
            out[f] = int(m.group(0).replace(",", "")) if m else ""
    if (out["amount_min"] != "" and out["amount_max"] != ""
            and out["amount_min"] > out["amount_max"]):
        out["amount_min"], out["amount_max"] = out["amount_max"], out["amount_min"]

    # Never rewritten, only carried through.
    out["eligibility_raw"] = rec["eligibility_raw"]
    for f in ("source_url", "source_org", "source_county", "source_file"):
        out[f] = rec.get(f, "")
    out["name_before_enrichment"] = rec.get("name", "")
    return out


def enrich_one(client, rec, counters, lock):
    key = cache_key(rec["eligibility_raw"])
    hit = cached(key)
    if hit is not None:
        with lock:
            counters["cached"] += 1
        return verify(hit, rec)

    if client is None:                      # --dry-run
        with lock:
            counters["skipped_dry"] += 1
        return None

    last = None
    for attempt in range(3):
        try:
            msg = client.messages.create(
                model=MODEL, max_tokens=1600, system=SYSTEM,
                messages=[{"role": "user", "content": build_user_msg(rec)}])
            obj = parse_response(msg.content[0].text)
            row = verify(obj, rec)
            put_cache(key, obj)
            with lock:
                counters["fetched"] += 1
                counters["in_tok"] += msg.usage.input_tokens
                counters["out_tok"] += msg.usage.output_tokens
            return row
        except Exception as e:              # malformed JSON, rate limit, timeout
            last = e
    with lock:
        counters["failed"] += 1
        counters["errors"][type(last).__name__] += 1
    return None


def estimate(records):
    chars = sum(len(r["eligibility_raw"][:6000]) + len(SYSTEM) for r in records)
    in_tok = chars / 3.6
    out_tok = 320 * len(records)
    cost = in_tok / 1e6 * PRICE_IN + out_tok / 1e6 * PRICE_OUT
    return in_tok, out_tok, cost


def main(in_path, out_path, limit, dry_run, workers, only_awards):
    records = list(csv.DictReader(open(in_path, encoding="utf-8")))
    records = [r for r in records if r.get("eligibility_raw")]
    if limit:
        records = records[:limit]

    in_tok, out_tok, cost = estimate(records)
    n_cached = sum(1 for r in records if cached(cache_key(r["eligibility_raw"])))
    print(f"{len(records)} records, {n_cached} already cached", file=sys.stderr)
    print(f"estimate for the {len(records) - n_cached} uncached: "
          f"~{in_tok/1e6:.2f}M in + ~{out_tok/1e6:.2f}M out tokens, ~${cost:.2f}",
          file=sys.stderr)

    client = None
    if not dry_run:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            sys.exit("ANTHROPIC_API_KEY not set (use --dry-run to test the plumbing)")
        try:
            from anthropic import Anthropic
        except ImportError:
            sys.exit("pip install anthropic")
        client = Anthropic()

    counters = Counter({"errors": Counter()})
    counters["errors"] = Counter()
    lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(lambda r: enrich_one(client, r, counters, lock), records))
    rows = [r for r in rows if r]

    verdicts = Counter(r["verdict"] for r in rows)
    print(f"\nenriched {len(rows)}  "
          f"(cached {counters['cached']}, fetched {counters['fetched']}, "
          f"failed {counters['failed']}, dry-skipped {counters['skipped_dry']})",
          file=sys.stderr)
    if counters["errors"]:
        print(f"errors: {dict(counters['errors'])}", file=sys.stderr)
    print(f"verdicts: {dict(verdicts)}", file=sys.stderr)
    if counters["fetched"]:
        spent = (counters["in_tok"] / 1e6 * PRICE_IN
                 + counters["out_tok"] / 1e6 * PRICE_OUT)
        print(f"actual spend this run: ~${spent:.2f}", file=sys.stderr)

    if only_awards:
        rows = [r for r in rows if r["verdict"] == "award"]
        print(f"kept {len(rows)} with verdict=award", file=sys.stderr)
    if not rows:
        print("nothing to write", file=sys.stderr)
        return

    cols = (["verdict", "confidence"] + SCALAR_FIELDS + BOOL_FIELDS + LIST_FIELDS
            + ["eligibility_raw", "name_before_enrichment",
               "source_url", "source_org", "source_county", "source_file"])
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: (json.dumps(v) if isinstance(v, list) else v)
                        for k, v in r.items()})
    print(f"\n{len(rows)} rows -> {out_path}", file=sys.stderr)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", default="data/15_awards.csv")
    ap.add_argument("--out", dest="out_path", default="data/16_awards_enriched.csv")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true",
                    help="validate plumbing and print a cost estimate; no API calls")
    ap.add_argument("--workers", type=int, default=MAX_WORKERS)
    ap.add_argument("--only-awards", action="store_true",
                    help="drop rows the model judged not to be applicable awards")
    a = ap.parse_args()
    main(a.in_path, a.out_path, a.limit, a.dry_run, a.workers, a.only_awards)
