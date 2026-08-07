#!/usr/bin/env python3
"""
Attach websites to BMF candidates, from the 990 e-file index.

The BMF says an organization exists and probably runs a scholarship. It does not
say where to read about it. That was the missing link in the BMF channel: no URL,
nothing to crawl.

The GivingTuesday 990 index solves it. Its CSV carries a `Website` column already
extracted from each filing's XML, so no per-organization XML fetch and no search
API is needed -- one streaming pass over the index yields a URL per EIN.

The index is ~3.2GB, so it is streamed through stdin and filtered on the fly
rather than downloaded:

    curl -sS <index-url> | python3 15_bmf_websites.py candidates.csv out.csv

Multiple filings exist per EIN (one per year); the most recent filing carrying a
non-empty website wins.
"""

import csv
import sys
from pathlib import Path

csv.field_size_limit(10_000_000)


def norm_ein(e: str) -> str:
    return (e or "").strip().replace("-", "").lstrip("0")


def main(cand_path: str, out_path: str):
    cands = {}
    with open(cand_path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            k = norm_ein(r.get("ein", ""))
            if k:
                cands[k] = r
    print(f"{len(cands):,} candidate EINs loaded from {cand_path}", file=sys.stderr)

    best = {}      # ein -> (tax_year, website, org_name, filing_url)
    scanned = hits = 0

    reader = csv.DictReader(sys.stdin)
    for row in reader:
        scanned += 1
        if scanned % 2_000_000 == 0:
            print(f"  scanned {scanned:,} filings, {len(best):,} matched",
                  file=sys.stderr, flush=True)

        k = norm_ein(row.get("EIN", ""))
        if k not in cands:
            continue
        hits += 1

        site = (row.get("Website") or "").strip()
        if not site or site.lower() in {"n/a", "na", "none", "no", "-"}:
            continue
        year = (row.get("TaxYear") or "").strip()
        prev = best.get(k)
        if prev is None or year > prev[0]:
            best[k] = (year, site, (row.get("OrganizationName") or "").strip(),
                       (row.get("URL") or "").strip())

    rows = []
    for k, cand in cands.items():
        b = best.get(k)
        if not b:
            continue
        site = b[1]
        if not site.startswith(("http://", "https://")):
            site = "https://" + site.lstrip("/")
        rows.append({
            "ein": cand.get("ein", ""),
            "display_name": cand.get("display_name") or cand.get("name", ""),
            "priority": cand.get("priority", ""),
            "score": cand.get("score", ""),
            "city": cand.get("city", ""),
            "county": cand.get("county", ""),
            "signals": cand.get("signals", ""),
            "website": site,
            "filing_year": b[0],
            "filing_xml": b[3],
        })

    rows.sort(key=lambda r: (r["priority"], -int(r["score"] or 0)))

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["ein"])
        w.writeheader()
        w.writerows(rows)

    from collections import Counter
    by_pri = Counter(r["priority"] for r in rows)
    print(f"\nScanned {scanned:,} filings", file=sys.stderr)
    print(f"  {hits:,} filings matched a candidate EIN", file=sys.stderr)
    print(f"  {len(rows):,} candidates now have a website "
          f"({len(rows)/len(cands):.0%} of {len(cands):,})", file=sys.stderr)
    for p in "ABCD":
        if by_pri.get(p):
            print(f"    priority {p}: {by_pri[p]:>5,}", file=sys.stderr)
    print(f"\nWritten to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
