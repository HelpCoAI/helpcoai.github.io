#!/usr/bin/env python3
"""
District / education-foundation crawler.

Why this exists: the n=15 verification sample showed the BMF finds *organizations*
(40% of which turn out to run nothing a student can apply to), while school-district
and education-foundation pages enumerate *awards* -- already filtered for open,
local and current. This is the higher-yield channel and should run first.

Two stages, deliberately separate so a fetch failure never costs an LLM call and a
prompt change never costs a refetch:

    fetch    seeds -> cache/<sha>.html   (network, polite, robots-aware, resumable)
    extract  cache/*.html -> awards.csv  (LLM, batched, idempotent)

Usage:
    python3 10_district_crawl.py fetch    [--seeds data/district_seeds.json]
    python3 10_district_crawl.py extract  [--out data/07_district_awards.csv]
    python3 10_district_crawl.py status

Requires real egress. The build sandbox's proxy denies CONNECT to arbitrary hosts,
so `fetch` will report every seed as blocked there -- run it somewhere with network.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "cache" / "district"
SEEDS = ROOT / "data" / "district_seeds.json"

UA = ("ScholarshipFinderBot/0.1 (+https://example.org/bot; contact: hello@example.org) "
      "python-urllib")
DELAY_SECONDS = 2.0          # per-host politeness delay
TIMEOUT = 30


# ------------------------------------------------------------------ fetch

def cache_path(url: str) -> Path:
    return CACHE / (hashlib.sha256(url.encode()).hexdigest()[:20] + ".html")


def meta_path(url: str) -> Path:
    return cache_path(url).with_suffix(".json")


_robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}


def robots_allows(url: str) -> bool:
    """
    Respect robots.txt. This is not optional for a business that intends to crawl
    thousands of school and nonprofit sites -- it is the difference between a data
    pipeline and a liability.
    """
    parts = urllib.parse.urlsplit(url)
    origin = f"{parts.scheme}://{parts.netloc}"
    if origin not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(origin + "/robots.txt")
        try:
            rp.read()
        except Exception:
            rp = None            # no robots.txt reachable -> default allow
        _robots[origin] = rp
        time.sleep(DELAY_SECONDS)
    rp = _robots[origin]
    return True if rp is None else rp.can_fetch(UA, url)


def fetch_one(url: str) -> tuple[str, str]:
    """-> (status, detail). status in {ok, cached, blocked, robots, error}"""
    if cache_path(url).exists():
        return "cached", f"{cache_path(url).stat().st_size:,} bytes"

    try:
        if not robots_allows(url):
            return "robots", "disallowed by robots.txt"
    except Exception as e:
        return "error", f"robots check failed: {e}"

    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read()
            ctype = r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        return "error", f"HTTP {e.code}"
    except urllib.error.URLError as e:
        reason = str(e.reason)
        if "403" in reason or "CONNECT" in reason or "tunnel" in reason.lower():
            return "blocked", "egress proxy denied CONNECT"
        return "error", reason
    except Exception as e:
        return "error", str(e)
    finally:
        time.sleep(DELAY_SECONDS)

    CACHE.mkdir(parents=True, exist_ok=True)
    cache_path(url).write_bytes(body)
    meta_path(url).write_text(json.dumps({
        "url": url, "content_type": ctype, "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
    }, indent=2))
    return "ok", f"{len(body):,} bytes"


def cmd_fetch(seeds_path: Path):
    seeds = json.loads(seeds_path.read_text())["seeds"]
    tally: dict[str, int] = {}
    print(f"Fetching {len(seeds)} seeds (>= {DELAY_SECONDS}s between requests)\n")
    for s in seeds:
        status, detail = fetch_one(s["url"])
        tally[status] = tally.get(status, 0) + 1
        mark = {"ok": "  ok", "cached": "cach", "blocked": "BLOK",
                "robots": "ROBO", "error": " ERR"}[status]
        print(f"[{mark}] {s['county']:<18} {s['org'][:38]:<38} {detail}")

    print("\n" + "  ".join(f"{k}={v}" for k, v in sorted(tally.items())))
    if tally.get("blocked"):
        print("\nBlocked seeds mean this machine has no direct egress. The proxy denies")
        print("CONNECT to arbitrary hosts by policy -- run this where network is open")
        print("(your laptop, or a GitHub Actions runner) rather than working around it.")


# ------------------------------------------------------------------ extract

EXTRACT_PROMPT = """\
You are extracting scholarship records from a school district or education
foundation page. Return STRICT JSON: a list of objects, one per NAMED award.

For each award set: name, sponsor, amount_min, amount_max, deadline (ISO date or
null), eligibility_raw (verbatim), counties, high_schools, gpa_min, majors,
apply_url, platform (CommunityForce/AwardSpring/Scholarship America/Google Form/
paper/email/other/null), beneficiary_scope (open|members_only|employees_only|
nomination_only), essay_required (bool or null).

Rules:
- Use null for anything not stated. NEVER infer an amount or a deadline.
- Skip national awards (Coca-Cola, Gates, Bright Futures) -- local only.
- If one application covers many awards, emit each named award separately and give
  them all the same apply_url.
- Return [] if the page lists no named awards.
"""

TAG_STRIP = re.compile(rb"<(script|style)[^>]*>.*?</\1>", re.S | re.I)
TAGS = re.compile(rb"<[^>]+>")


def to_text(raw: bytes, limit: int = 60_000) -> str:
    body = TAGS.sub(b" ", TAG_STRIP.sub(b" ", raw))
    text = body.decode("utf-8", errors="replace")
    text = re.sub(r"&nbsp;?", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text[:limit]


def cmd_extract(seeds_path: Path, out_path: Path):
    try:
        from anthropic import Anthropic
    except ImportError:
        sys.exit("pip install anthropic")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set")

    seeds = json.loads(seeds_path.read_text())["seeds"]
    client = Anthropic()
    rows, skipped = [], 0

    for s in seeds:
        cp = cache_path(s["url"])
        if not cp.exists():
            skipped += 1
            continue
        text = to_text(cp.read_bytes())
        if len(text) < 400:
            skipped += 1
            continue

        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=8_000,
            system=EXTRACT_PROMPT,
            messages=[{"role": "user",
                       "content": f"Source: {s['url']}\nCounty: {s['county']}\n\n{text}"}],
        )
        blob = msg.content[0].text.strip()
        blob = re.sub(r"^```(?:json)?|```$", "", blob, flags=re.M).strip()
        try:
            awards = json.loads(blob)
        except json.JSONDecodeError:
            print(f"  ! unparseable JSON from {s['org']}")
            continue

        for a in awards:
            a["source_url"] = s["url"]
            a["source_org"] = s["org"]
            a["source_county"] = s["county"]
            rows.append(a)
        print(f"  {len(awards):>3} awards  {s['org']}")

    if not rows:
        sys.exit(f"No awards extracted ({skipped} seeds had no cached page — run `fetch` first)")

    import csv
    cols = sorted({k for r in rows for k in r})
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: (json.dumps(v) if isinstance(v, (list, dict)) else v)
                        for k, v in r.items()})
    print(f"\n{len(rows)} awards -> {out_path}  ({skipped} seeds skipped)")


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:60]


def cmd_harvest(seeds_path: Path, out_dir: Path):
    """
    fetch + flatten to plain text, committed to the repo.

    Splitting this out of `extract` means the pages can be harvested by a machine
    that HAS network (a GitHub runner) and read by one that does not, with no API
    key anywhere in the loop.
    """
    seeds = json.loads(seeds_path.read_text())["seeds"]
    out_dir.mkdir(parents=True, exist_ok=True)
    ok = 0

    for s in seeds:
        status, detail = fetch_one(s["url"])
        if status not in {"ok", "cached"}:
            print(f"[{status:>6}] {s['org'][:44]:<44} {detail}")
            continue

        text = to_text(cache_path(s["url"]).read_bytes())
        if len(text) < 300:
            print(f"[  thin] {s['org'][:44]:<44} {len(text)} chars")
            continue

        name = f"{slugify(s['county'])}--{slugify(s['org'])}.txt"
        (out_dir / name).write_text(
            f"URL: {s['url']}\nORG: {s['org']}\nCOUNTY: {s['county']}\n"
            f"KIND: {s['kind']}\n{'-' * 70}\n{text}\n", encoding="utf-8")
        ok += 1
        print(f"[    ok] {s['org'][:44]:<44} {len(text):,} chars -> {name}")

    print(f"\n{ok}/{len(seeds)} pages harvested into {out_dir}")


def cmd_status(seeds_path: Path):
    seeds = json.loads(seeds_path.read_text())["seeds"]
    have = sum(1 for s in seeds if cache_path(s["url"]).exists())
    print(f"Seeds: {len(seeds)}   cached: {have}   missing: {len(seeds) - have}")
    for s in seeds:
        print(f"  [{'x' if cache_path(s['url']).exists() else ' '}] "
              f"{s['kind']:<5} {s['county']:<18} {s['org']}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["fetch", "harvest", "extract", "status"])
    p.add_argument("--seeds", type=Path, default=SEEDS)
    p.add_argument("--out", type=Path, default=ROOT / "data" / "07_district_awards.csv")
    p.add_argument("--pages", type=Path, default=ROOT / "data" / "district_pages")
    a = p.parse_args()
    {"fetch": lambda: cmd_fetch(a.seeds),
     "harvest": lambda: cmd_harvest(a.seeds, a.pages),
     "extract": lambda: cmd_extract(a.seeds, a.out),
     "status": lambda: cmd_status(a.seeds)}[a.command]()
