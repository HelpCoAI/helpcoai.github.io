#!/usr/bin/env python3
"""
Phase 0 pilot extraction — Tampa Bay + Sarasota/Manatee (5 counties).

Produces the ranked candidate list that feeds web verification. Reuses the
scoring logic from 01_filter_bmf.py and adds the three Tampa Bay counties.

Output columns are ordered for human review: the reviewer works top-down and
stops when the yield drops off.

Usage:
    python3 08_pilot_extract.py /tmp/bmf.csv data/05_pilot_candidates.csv
"""

import csv
import sys
from pathlib import Path
from importlib import import_module

sys.path.insert(0, str(Path(__file__).parent))
_f = import_module("01_filter_bmf")

# ---------------------------------------------------------------- region

HILLSBOROUGH = {
    "TAMPA", "PLANT CITY", "TEMPLE TERRACE", "BRANDON", "RIVERVIEW", "VALRICO",
    "LUTZ", "RUSKIN", "SUN CITY CENTER", "APOLLO BEACH", "SEFFNER", "WIMAUMA",
    "GIBSONTON", "DOVER", "THONOTOSASSA", "LITHIA", "ODESSA",
}
PINELLAS = {
    "ST PETERSBURG", "SAINT PETERSBURG", "CLEARWATER", "LARGO", "PINELLAS PARK",
    "DUNEDIN", "TARPON SPRINGS", "PALM HARBOR", "SEMINOLE", "SAFETY HARBOR",
    "OLDSMAR", "GULFPORT", "TREASURE ISLAND", "ST PETE BEACH", "SAINT PETE BEACH",
    "MADEIRA BEACH", "INDIAN ROCKS BEACH", "BELLEAIR", "KENNETH CITY",
    "CLEARWATER BEACH",
}
PASCO = {
    "NEW PORT RICHEY", "PORT RICHEY", "DADE CITY", "ZEPHYRHILLS", "LAND O LAKES",
    "WESLEY CHAPEL", "HUDSON", "HOLIDAY", "TRINITY", "SAN ANTONIO", "SPRING HILL",
}

PILOT_CITIES = _f.TARGET_CITIES | HILLSBOROUGH | PINELLAS | PASCO


def county_for(city: str) -> str:
    if city in HILLSBOROUGH:
        return "Hillsborough"
    if city in PINELLAS:
        return "Pinellas"
    if city in PASCO:
        return "Pasco"
    return _f.county_for(city) or "Unknown"


# Signals that predict a *verifiable, student-facing* program, learned from the
# Sarasota/Manatee round where 10 of 22 name-matches were real. Orgs that only
# score on generic foundation signals are far less likely to run open programs.
def review_priority(score: int, signals: list[str], assets: int) -> str:
    strong = {"name:scholarship", "name:community-foundation", "name:service-club",
              "ntee:B82"}
    if any(s in strong for s in signals):
        return "A"
    if "name:memorial-fund" in signals or "name:alumni/booster" in signals:
        return "B"
    if assets >= 1_000_000:
        return "C"
    return "D"


def main(bmf_path: str, out_path: str, min_score: int = 20):
    rows = []
    scanned = in_region = 0

    with open(bmf_path, newline="", encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh):
            scanned += 1
            if r.get("STATE") != "FL":
                continue
            city = (r.get("CITY") or "").strip().upper()
            if city not in PILOT_CITIES:
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
            rows.append({
                "priority": review_priority(pts, why, assets),
                "score": pts,
                "name": name,
                "city": city.title(),
                "county": county_for(city),
                "ein": (r.get("EIN") or "").strip(),
                "assets": assets,
                "revenue": num("REVENUE_AMT"),
                "ntee": ntee,
                "files_990pf": "Y" if pf else "",
                "signals": ";".join(why),
                # filled during verification
                "verified": "", "has_website": "", "program_url": "",
                "award_amount": "", "deadline": "", "eligibility": "",
                "apply_via": "", "platform": "", "notes": "",
            })

    rows.sort(key=lambda x: (x["priority"], -x["score"], -x["assets"]))

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    from collections import Counter
    by_pri = Counter(r["priority"] for r in rows)
    by_cty = Counter(r["county"] for r in rows)

    print(f"Scanned {scanned:,} BMF rows · {in_region:,} nonprofits in pilot region")
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
    print(f"Written to {out_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2],
         int(sys.argv[3]) if len(sys.argv) > 3 else 20)
