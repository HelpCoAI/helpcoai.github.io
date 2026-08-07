#!/usr/bin/env python3
"""
Region-parameterised BMF extraction.

Generalises 08_pilot_extract.py so a pilot can move metros without editing code.
Same scoring, same A/B/C/D review tiers, same chapter-name resolution.

Usage:
    python3 12_region_extract.py south-florida /tmp/bmf.csv data/09_south_florida.csv
    python3 12_region_extract.py tampa-bay     /tmp/bmf.csv data/05_pilot_candidates.csv
"""

import csv
import sys
from collections import Counter
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
_f = import_module("01_filter_bmf")
_p = import_module("08_pilot_extract")
import orgnames
import regions


def main(region: str, bmf_path: str, out_path: str, min_score: int = 20):
    if region not in regions.REGIONS:
        sys.exit(f"Unknown region {region!r}. Known: {', '.join(regions.REGIONS)}")
    cfg = regions.REGIONS[region]
    want_cities = regions.cities(region)
    state = cfg["state"]

    rows, scanned, in_region = [], 0, 0

    with open(bmf_path, newline="", encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh):
            scanned += 1
            if r.get("STATE") != state:
                continue
            city = (r.get("CITY") or "").strip().upper()
            if city not in want_cities:
                continue
            in_region += 1

            name = (r.get("NAME") or "").strip()
            if _f.RE_EXCLUDE.search(name):
                continue

            ntee = (r.get("NTEE_CD") or "").strip().upper()
            pf = (r.get("PF_FILING_REQ_CD") or "").strip() == "1"
            fc = (r.get("FOUNDATION") or "").strip()

            pts, why = _f.score(name, ntee, pf, fc)
            if pts < min_score:
                continue

            def num(k):
                v = (r.get(k) or "").strip()
                return int(v) if v.lstrip("-").isdigit() else 0

            assets = num("ASSET_AMT")
            display, _, resolved = orgnames.resolve(
                name, (r.get("SORT_NAME") or "").strip(), city)

            rows.append({
                "priority": _p.review_priority(pts, why, assets),
                "score": pts,
                "name": name,
                "display_name": display,
                "chapter_resolved": "Y" if resolved else "",
                "search_query": orgnames.search_query(display, city, state),
                "city": city.title(),
                "county": regions.county_for(region, city),
                "ein": (r.get("EIN") or "").strip(),
                "assets": assets,
                "revenue": num("REVENUE_AMT"),
                "ntee": ntee,
                "files_990pf": "Y" if pf else "",
                "signals": ";".join(why),
                "verified": "", "has_website": "", "program_url": "",
                "award_amount": "", "deadline": "", "eligibility": "",
                "apply_via": "", "platform": "", "beneficiary_scope": "", "notes": "",
            })

    if not rows:
        sys.exit("No candidates found — check the region's city list against the BMF.")

    rows.sort(key=lambda x: (x["priority"], -x["score"], -x["assets"]))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    by_pri = Counter(r["priority"] for r in rows)
    by_cty = Counter(r["county"] for r in rows)
    b82 = sum(1 for r in rows if r["ntee"] == "B82")
    a_rows = [r for r in rows if r["priority"] == "A"]
    a_b82 = sum(1 for r in a_rows if r["ntee"] == "B82")

    print(f"Region: {region} ({state})")
    print(f"Scanned {scanned:,} BMF rows · {in_region:,} nonprofits in region")
    print(f"Candidates (score >= {min_score}): {len(rows):,}")
    print()
    print("Review priority (A = verify first):")
    for p in "ABCD":
        if by_pri.get(p):
            print(f"  {p}: {by_pri[p]:>5,}")
    print()
    print("By county:")
    for c, n in by_cty.most_common():
        print(f"  {c:<16}{n:>6,}")
    print()
    print(f"Chapter names resolved: {sum(1 for r in rows if r['chapter_resolved']):,}")
    if a_rows:
        print(f"Priority-A carrying NTEE B82: {a_b82}/{len(a_rows)} ({a_b82/len(a_rows):.0%})"
              f" — the other {1 - a_b82/len(a_rows):.0%} are invisible to "
              f"NTEE-filtered directories")
    print(f"\nWritten to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3],
         int(sys.argv[4]) if len(sys.argv) > 4 else 20)
