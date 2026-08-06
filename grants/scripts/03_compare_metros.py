#!/usr/bin/env python3
"""
Is Sarasota typical?

Sarasota/Manatee is a wealthy retirement region -- it may be top-decile for local
philanthropic infrastructure rather than representative. If so, Test 1's result
would not generalize to a national rollout.

This runs the identical scan against median-income metros of comparable population
and reports per-capita comparisons.

Usage:
    python3 03_compare_metros.py /tmp/bmf.csv data/04_metro_comparison.csv
"""

import csv
import sys
from pathlib import Path
from importlib import import_module

sys.path.insert(0, str(Path(__file__).parent))
_f = import_module("01_filter_bmf")
_g = import_module("02_funders_for_nonprofits")

# Comparison regions. Population figures are approximate county totals used only
# for per-capita normalization.
REGIONS = {
    "Sarasota+Manatee, FL": {
        "population": 880_000,
        "note": "wealthy retirement region (baseline)",
        "cities": _f.TARGET_CITIES,
    },
    "Lucas County (Toledo), OH": {
        "population": 428_000,
        "note": "median Rust Belt metro",
        "cities": {
            "TOLEDO", "MAUMEE", "SYLVANIA", "OREGON", "WATERVILLE", "HOLLAND",
            "SWANTON", "WHITEHOUSE", "BERKEY", "HARBOR VIEW", "OTTAWA HILLS",
            "POINT PLACE", "MONCLOVA",
        },
    },
    "Sedgwick County (Wichita), KS": {
        "population": 525_000,
        "note": "median plains metro",
        "cities": {
            "WICHITA", "DERBY", "HAYSVILLE", "PARK CITY", "VALLEY CENTER",
            "MAIZE", "ANDALE", "BEL AIRE", "CLEARWATER", "GODDARD", "MULVANE",
            "KECHI", "COLWICH", "GARDEN PLAIN", "CHENEY", "MOUNT HOPE",
        },
    },
    "Hamilton County (Chattanooga), TN": {
        "population": 370_000,
        "note": "median southern metro",
        "cities": {
            "CHATTANOOGA", "EAST RIDGE", "RED BANK", "SODDY DAISY", "SIGNAL MOUNTAIN",
            "COLLEGEDALE", "LAKESITE", "WALDEN", "LOOKOUT MOUNTAIN", "HARRISON",
            "OOLTEWAH", "HIXSON",
        },
    },
}

STATE_FOR = {
    "Sarasota+Manatee, FL": "FL",
    "Lucas County (Toledo), OH": "OH",
    "Sedgwick County (Wichita), KS": "KS",
    "Hamilton County (Chattanooga), TN": "TN",
}


def scan(bmf_path):
    """Single pass over the BMF, bucketing rows into every region at once."""
    results = {
        name: {
            "nonprofits": 0, "scholarship_candidates": 0, "scholar_named": 0,
            "community_foundations": 0, "service_clubs": 0,
            "grantmakers": 0, "grantmaker_assets": 0,
        }
        for name in REGIONS
    }

    with open(bmf_path, newline="", encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh):
            state = r.get("STATE")
            city = (r.get("CITY") or "").strip().upper()

            for region, cfg in REGIONS.items():
                if state != STATE_FOR[region] or city not in cfg["cities"]:
                    continue

                acc = results[region]
                acc["nonprofits"] += 1

                name = (r.get("NAME") or "").strip()
                if _f.RE_EXCLUDE.search(name):
                    continue

                ntee = (r.get("NTEE_CD") or "").strip().upper()
                pf_filer = (r.get("PF_FILING_REQ_CD") or "").strip() == "1"
                foundation_cd = (r.get("FOUNDATION") or "").strip()

                pts, why = _f.score(name, ntee, pf_filer, foundation_cd)
                if pts >= 20:
                    acc["scholarship_candidates"] += 1
                    if "name:scholarship" in why:
                        acc["scholar_named"] += 1
                    if "name:community-foundation" in why:
                        acc["community_foundations"] += 1
                    if "name:service-club" in why:
                        acc["service_clubs"] += 1

                # Grantmaker side (nonprofit route)
                if _g.RE_EXCLUDE.search(name):
                    continue
                is_grantmaker = (
                    foundation_cd in _g.PRIVATE_FOUNDATION_CODES
                    or ntee.startswith(_g.NTEE_GRANTMAKER)
                    or pf_filer
                )
                if not is_grantmaker:
                    continue
                assets_raw = (r.get("ASSET_AMT") or "").strip()
                assets = int(assets_raw) if assets_raw.lstrip("-").isdigit() else 0
                if assets >= 100_000:
                    acc["grantmakers"] += 1
                    acc["grantmaker_assets"] += assets

    return results


def main(bmf_path, out_path):
    res = scan(bmf_path)

    rows = []
    for region, acc in res.items():
        pop = REGIONS[region]["population"]
        per100k = lambda n: round(n / pop * 100_000, 1)
        rows.append({
            "region": region,
            "note": REGIONS[region]["note"],
            "population": pop,
            "nonprofits": acc["nonprofits"],
            "nonprofits_per_100k": per100k(acc["nonprofits"]),
            "scholarship_candidates": acc["scholarship_candidates"],
            "scholarship_candidates_per_100k": per100k(acc["scholarship_candidates"]),
            "scholar_named_orgs": acc["scholar_named"],
            "community_foundations": acc["community_foundations"],
            "service_clubs": acc["service_clubs"],
            "grantmakers": acc["grantmakers"],
            "grantmakers_per_100k": per100k(acc["grantmakers"]),
            "grantmaker_assets": acc["grantmaker_assets"],
            "grantmaker_assets_per_capita": round(acc["grantmaker_assets"] / pop),
        })

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    base = rows[0]
    print(f"{'REGION':<36} {'NPOs/100k':>10} {'Schol/100k':>11} {'Fndrs/100k':>11} {'$/capita':>12}")
    print("-" * 84)
    for r in rows:
        print(f"{r['region']:<36} {r['nonprofits_per_100k']:>10.1f} "
              f"{r['scholarship_candidates_per_100k']:>11.1f} "
              f"{r['grantmakers_per_100k']:>11.1f} "
              f"${r['grantmaker_assets_per_capita']:>11,}")
    print()
    for r in rows[1:]:
        ratio_s = base["scholarship_candidates_per_100k"] / max(r["scholarship_candidates_per_100k"], 0.1)
        ratio_a = base["grantmaker_assets_per_capita"] / max(r["grantmaker_assets_per_capita"], 1)
        print(f"Sarasota vs {r['region']}: "
              f"{ratio_s:.1f}x scholarship density, {ratio_a:.1f}x foundation assets/capita")
    print(f"\nWritten to: {out_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
