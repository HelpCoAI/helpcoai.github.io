#!/usr/bin/env python3
"""
Test 1, Step A: find candidate scholarship-granting organizations in
Sarasota and Manatee counties, FL, from the IRS Business Master File.

Source: GivingTuesday 990 data lake
  https://gt990datalake-rawdata.s3.amazonaws.com/EfileData/BMF/

Input:  IRS BMF raw CSV (~324MB, ~1.97M organizations)
Output: candidates CSV, scored by likelihood of running a scholarship program
"""

import csv
import re
import sys
from pathlib import Path

# Sarasota County + Manatee County municipalities and CDPs as they appear
# in IRS mailing addresses. ENGLEWOOD straddles Sarasota/Charlotte; kept and
# flagged rather than dropped.
SARASOTA_CITIES = {
    "SARASOTA", "VENICE", "NORTH PORT", "OSPREY", "NOKOMIS",
    "LONGBOAT KEY", "ENGLEWOOD", "LAUREL", "SIESTA KEY", "VAMO",
}
MANATEE_CITIES = {
    "BRADENTON", "BRADENTON BEACH", "PALMETTO", "ANNA MARIA",
    "HOLMES BEACH", "ELLENTON", "PARRISH", "MYAKKA CITY",
    "LAKEWOOD RANCH", "CORTEZ", "TERRA CEIA", "DUETTE", "ONECO",
}
TARGET_CITIES = SARASOTA_CITIES | MANATEE_CITIES

# NTEE codes that signal grantmaking or student aid.
NTEE_STRONG = {"B82"}                      # Scholarships & Student Financial Aid
NTEE_GRANTMAKER_PREFIXES = ("T20", "T21", "T22", "T23", "T30", "T31", "T99", "T12")
NTEE_EDU_PREFIXES = ("B",)                 # Education generally

# Name patterns. Scholarship funds are frequently named for a person and
# carry no useful NTEE code, so name matching carries real weight here.
RE_SCHOLARSHIP = re.compile(r"\bSCHOLAR", re.I)
RE_MEMORIAL_FUND = re.compile(r"\bMEMORIAL\b.*\bFUND\b|\bFUND\b.*\bMEMORIAL\b", re.I)
RE_SERVICE_CLUB = re.compile(
    r"\b(ROTARY|ELKS|KIWANIS|LIONS CLUB|OPTIMIST|JAYCEES|MOOSE|SERTOMA|EXCHANGE CLUB|"
    r"ALTRUSA|ZONTA|PILOT CLUB|SOROPTIMIST|JUNIOR LEAGUE)\b", re.I)
RE_FOUNDATION = re.compile(r"\bFOUNDATION\b|\bCHARITABLE TRUST\b|\bENDOWMENT\b", re.I)
RE_EDU = re.compile(r"\bEDUCATION|\bSTUDENT|\bCOLLEGE\b|\bACADEM|\bLEARNING\b", re.I)
RE_ALUMNI = re.compile(r"\bALUMNI\b|\bBOOSTER|\bPTA\b|\bPTO\b|\bPARENT TEACHER\b", re.I)
RE_COMMUNITY_FDN = re.compile(r"\bCOMMUNITY FOUNDATION\b", re.I)

# Names that look like grantmakers but essentially never run open,
# publicly-applicable scholarship programs.
RE_EXCLUDE = re.compile(
    r"\bCEMETERY\b|\bCONDOMINIUM\b|\bHOMEOWNERS\b|\bCONDO\b|\bPROPERTY OWNERS\b", re.I)


def county_for(city: str) -> str:
    if city in SARASOTA_CITIES and city in MANATEE_CITIES:
        return "Both"
    if city in SARASOTA_CITIES:
        return "Sarasota"
    if city in MANATEE_CITIES:
        return "Manatee"
    return ""


def score(name: str, ntee: str, pf_filer: bool, foundation_cd: str):
    """Return (score, list-of-reasons). Higher score = more likely to grant scholarships."""
    pts, why = 0, []

    if RE_SCHOLARSHIP.search(name):
        pts += 50
        why.append("name:scholarship")
    if ntee in NTEE_STRONG:
        pts += 45
        why.append(f"ntee:{ntee}")
    if RE_COMMUNITY_FDN.search(name):
        # Community foundations administer many named scholarship funds each --
        # one filing can reveal dozens of distinct awards.
        pts += 40
        why.append("name:community-foundation")
    if RE_SERVICE_CLUB.search(name):
        pts += 30
        why.append("name:service-club")
    if RE_MEMORIAL_FUND.search(name):
        pts += 25
        why.append("name:memorial-fund")
    if ntee.startswith(NTEE_GRANTMAKER_PREFIXES):
        pts += 20
        why.append(f"ntee-grantmaker:{ntee}")
    if pf_filer:
        pts += 20
        why.append("files-990PF")
    if foundation_cd in {"02", "03", "04"}:
        pts += 10
        why.append(f"private-foundation:{foundation_cd}")
    if RE_FOUNDATION.search(name):
        pts += 10
        why.append("name:foundation")
    if RE_ALUMNI.search(name):
        pts += 10
        why.append("name:alumni/booster")
    if ntee.startswith(NTEE_EDU_PREFIXES):
        pts += 8
        why.append(f"ntee-education:{ntee}")
    if RE_EDU.search(name):
        pts += 5
        why.append("name:education")

    return pts, why


def main(bmf_path: str, out_path: str, min_score: int = 20):
    total = in_area = kept = 0
    rows = []

    with open(bmf_path, newline="", encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh):
            total += 1
            if r.get("STATE") != "FL":
                continue
            city = (r.get("CITY") or "").strip().upper()
            if city not in TARGET_CITIES:
                continue
            in_area += 1

            name = (r.get("NAME") or "").strip()
            if RE_EXCLUDE.search(name):
                continue

            ntee = (r.get("NTEE_CD") or "").strip().upper()
            pf_filer = (r.get("PF_FILING_REQ_CD") or "").strip() == "1"
            foundation_cd = (r.get("FOUNDATION") or "").strip()

            pts, why = score(name, ntee, pf_filer, foundation_cd)
            if pts < min_score:
                continue

            def num(k):
                v = (r.get(k) or "").strip()
                return int(v) if v.lstrip("-").isdigit() else 0

            kept += 1
            rows.append({
                "score": pts,
                "ein": (r.get("EIN") or "").strip(),
                "name": name,
                "city": city.title(),
                "county": county_for(city),
                "zip": (r.get("ZIP") or "").split("-")[0],
                "ntee": ntee,
                "files_990pf": "Y" if pf_filer else "",
                "foundation_cd": foundation_cd,
                "assets": num("ASSET_AMT"),
                "income": num("INCOME_AMT"),
                "revenue": num("REVENUE_AMT"),
                "signals": ";".join(why),
            })

    rows.sort(key=lambda x: (-x["score"], -x["assets"]))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"BMF rows scanned      : {total:,}")
    print(f"In Sarasota/Manatee   : {in_area:,}")
    print(f"Candidates (score>={min_score}): {kept:,}")
    print(f"Written to            : {out_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2],
         int(sys.argv[3]) if len(sys.argv) > 3 else 20)
