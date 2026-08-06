#!/usr/bin/env python3
"""
Test 1, Step E: dual-purpose tagging.

Same IRS Business Master File, opposite grant direction. The scholarship table
(script 01) targets foundations that grant to INDIVIDUALS. This one targets
foundations that grant to ORGANIZATIONS -- the funder list a local nonprofit
would pay for, and the seed of the nonprofit-facing version of the product.

Output: local grantmaking foundations ranked by assets.
"""

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from importlib import import_module
_f = import_module("01_filter_bmf")

# Private-foundation classification codes in the BMF FOUNDATION field.
PRIVATE_FOUNDATION_CODES = {"02", "03", "04"}

# Grantmaking / philanthropy NTEE prefixes.
NTEE_GRANTMAKER = ("T20", "T21", "T22", "T23", "T30", "T31", "T99", "T12", "T70")

# Exclude entities whose "grants" are not open to nonprofit applicants.
RE_EXCLUDE = re.compile(
    r"\bCEMETERY\b|\bCONDOMINIUM\b|\bHOMEOWNERS\b|\bSCHOLARSHIP\b|"
    r"\bCHARITABLE REMAINDER\b|\bLEAD TRUST\b|\bANNUITY TRUST\b", re.I)


def main(bmf_path: str, out_path: str, min_assets: int = 100_000):
    rows = []
    with open(bmf_path, newline="", encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh):
            if r.get("STATE") != "FL":
                continue
            city = (r.get("CITY") or "").strip().upper()
            if city not in _f.TARGET_CITIES:
                continue

            name = (r.get("NAME") or "").strip()
            if RE_EXCLUDE.search(name):
                continue

            ntee = (r.get("NTEE_CD") or "").strip().upper()
            foundation_cd = (r.get("FOUNDATION") or "").strip()
            pf_filer = (r.get("PF_FILING_REQ_CD") or "").strip() == "1"

            is_grantmaker = (
                foundation_cd in PRIVATE_FOUNDATION_CODES
                or ntee.startswith(NTEE_GRANTMAKER)
                or pf_filer
            )
            if not is_grantmaker:
                continue

            def num(k):
                v = (r.get(k) or "").strip()
                return int(v) if v.lstrip("-").isdigit() else 0

            assets = num("ASSET_AMT")
            if assets < min_assets:
                continue

            kind = ("Community foundation" if _f.RE_COMMUNITY_FDN.search(name)
                    else "Private foundation" if foundation_cd in PRIVATE_FOUNDATION_CODES
                    else "Public grantmaker")

            rows.append({
                "name": name,
                "ein": (r.get("EIN") or "").strip(),
                "city": city.title(),
                "county": _f.county_for(city),
                "type": kind,
                "ntee": ntee,
                "files_990pf": "Y" if pf_filer else "",
                "assets": assets,
                "income": num("INCOME_AMT"),
                "revenue": num("REVENUE_AMT"),
            })

    rows.sort(key=lambda x: -x["assets"])
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    total_assets = sum(r["assets"] for r in rows)
    print(f"Local grantmaking foundations (assets >= ${min_assets:,}): {len(rows):,}")
    print(f"Combined assets: ${total_assets:,}")
    print(f"Written to: {out_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2],
         int(sys.argv[3]) if len(sys.argv) > 3 else 100_000)
