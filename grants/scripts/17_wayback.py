#!/usr/bin/env python3
"""
Recover pages the live web would not give us, from the Internet Archive.

Across every harvest run roughly 200 seeds failed: dead domains, DNS failures,
timeouts, WAF challenges that returned 1 byte, and robots.txt disallows. The
Archive very likely holds many of them from before they broke or locked down.

The scope split is deliberate and is the whole point of this script:

  RECOVER   dead domains, DNS failures, timeouts, and WAF/thin responses.
            Nobody's stated wishes are being overridden -- the site is gone, or a
            vendor's bot detection fired on repeated hits. Content is fetched.

  REPORT    robots.txt disallows. Content is NOT fetched. The script only asks the
            Archive what snapshots exist, so the founder can decide with real
            numbers instead of speculation. No request touches the origin server
            either way, but a robots directive is a stated preference and reading
            around it is a judgement call that is not mine to make silently.

Usage:
    python3 17_wayback.py --logs data/district_pages_*/_harvest_log.txt \\
        --pages data/district_pages_wayback --report data/13_wayback_report.csv
"""

import argparse
import csv
import json
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
_c = __import__("10_district_crawl")

socket.setdefaulttimeout(30)

CDX = "http://web.archive.org/cdx/search/cdx"
UA = ("ScholarshipFinderBot/0.1 (+https://example.org/bot; research; "
      "contact: hello@example.org)")
DELAY = 1.5          # the Archive is a nonprofit -- stay well under its limits

# [ status] Org name    detail  URL
LOG_LINE = re.compile(r"^\[\s*(\w+)\]\s+(.{1,42}?)\s{2,}(.*?)\s*(https?://\S+)\s*$")

RECOVERABLE = {"error", "thin"}
REPORT_ONLY = {"robots"}


def fetch(url, raw=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read(8_000_000)
    except Exception:
        return None
    finally:
        time.sleep(DELAY)


def snapshots(url, limit=8):
    """-> list of (timestamp, original) for 200-status captures, newest first."""
    q = urllib.parse.urlencode({
        "url": url, "output": "json", "limit": -limit,
        "filter": "statuscode:200", "collapse": "timestamp:6", "fl": "timestamp,original",
    })
    raw = fetch(f"{CDX}?{q}")
    if not raw:
        return []
    try:
        rows = json.loads(raw)
    except Exception:
        return []
    if not rows or len(rows) < 2:
        return []
    return [(r[0], r[1]) for r in rows[1:] if len(r) >= 2]


def parse_logs(paths):
    """-> list of (status, org, url) for every failed seed."""
    out = []
    for p in paths:
        for line in Path(p).read_text(encoding="utf-8", errors="replace").splitlines():
            m = LOG_LINE.match(line.strip())
            if not m:
                continue
            status, org, _detail, url = m.groups()
            if status in RECOVERABLE | REPORT_ONLY:
                out.append((status, org.strip(), url))
    # de-dup on url, preferring a recoverable classification
    best = {}
    for status, org, url in out:
        if url not in best or (status in RECOVERABLE and best[url][0] in REPORT_ONLY):
            best[url] = (status, org)
    return [(v[0], v[1], k) for k, v in best.items()]


def main(logs, pages_dir, report_path, limit):
    failures = parse_logs(logs)
    by_status = Counter(s for s, _, _ in failures)
    print(f"{len(failures)} failed seeds across {len(logs)} logs: {dict(by_status)}",
          file=sys.stderr)

    pages_dir = Path(pages_dir)
    pages_dir.mkdir(parents=True, exist_ok=True)
    rows, recovered = [], 0

    for i, (status, org, url) in enumerate(failures[:limit], 1):
        snaps = snapshots(url)
        row = {"status": status, "org": org, "url": url,
               "snapshots": len(snaps),
               "latest": snaps[0][0][:8] if snaps else "",
               "action": "", "chars": 0}

        if not snaps:
            row["action"] = "not archived"
        elif status in REPORT_ONLY:
            # robots-disallowed: availability only, deliberately no fetch
            row["action"] = "AVAILABLE - not fetched (robots)"
        else:
            ts, orig = snaps[0]
            raw = fetch(f"https://web.archive.org/web/{ts}id_/{orig}")
            text = _c.to_text(raw) if raw else ""
            if len(text) > 300:
                name = f"{_c.slugify(org)[:50]}--{ts[:8]}.txt"
                (pages_dir / name).write_text(
                    f"URL: {url}\nORG: {org}\nSOURCE: web.archive.org/{ts}\n"
                    f"{'-' * 70}\n{text}\n", encoding="utf-8")
                row["action"] = f"recovered -> {name}"
                row["chars"] = len(text)
                recovered += 1
            else:
                row["action"] = "snapshot empty"
        rows.append(row)
        print(f"  [{i:>3}/{min(len(failures), limit)}] {status:<7} "
              f"{row['action'][:44]:<44} {url[:56]}", file=sys.stderr, flush=True)

    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    avail = sum(1 for r in rows if r["action"].startswith("AVAILABLE"))
    none_ = sum(1 for r in rows if r["action"] == "not archived")
    print(f"\nRecovered {recovered} pages into {pages_dir}", file=sys.stderr)
    print(f"{avail} robots-disallowed pages ARE archived but were not fetched",
          file=sys.stderr)
    print(f"{none_} not archived at all", file=sys.stderr)
    print(f"Report -> {report_path}", file=sys.stderr)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--logs", nargs="+", required=True)
    ap.add_argument("--pages", default="data/district_pages_wayback")
    ap.add_argument("--report", default="data/13_wayback_report.csv")
    ap.add_argument("--limit", type=int, default=250)
    a = ap.parse_args()
    main(a.logs, a.pages, a.report, a.limit)
