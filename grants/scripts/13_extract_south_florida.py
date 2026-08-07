#!/usr/bin/env python3
"""
Structured awards extracted from the 10 harvested South Florida pages.

Extraction was done by reading the harvested text directly rather than via an API
call -- the pages are in the repo, so this is a transcription of what they say,
not an inference. Every row cites the page it came from.

PRIVACY: the Coral Gables awards list names individual recipients, many of them
minors. Only counts and school names are taken from it. No recipient name appears
in this file or its output, and none may appear on the site.

Usage:
    python3 13_extract_south_florida.py data/10_south_florida_awards.csv
"""

import csv
import sys
from pathlib import Path

CGCF = "https://gablesfoundation.org/scholarships/"
CGCF_AWARDS = "https://gablesfoundation.org/2025/05/05/scholarship-awards-list-2025/"
TMF = "https://miamifoundation.org/scholarships/"
CFB = "https://www.cfbroward.org/receive/community-foundation-administered-scholarships"
SNOW = "https://scholarship.org/scholarships/"
CFPBMC = "https://yourcommunityfoundation.org/scholarship-seekers/"
JHS = "https://sites.google.com/palmbeachschools.org/jhs-scholarship-bulletin/home"

# name, sponsor, hub, county, amount_min, amount_max, deadline, gpa_min,
# restriction, scope, platform, source
ROWS = [
    # ---------------- Coral Gables Community Foundation (hub, 25 funds) ----------
    ("Coral Gables Community Foundation Four-Year Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "Coral Gables Senior High", "open", "Foundant/GrantInterface", CGCF),
    ("Coral Gables Culinary Arts Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "Coral Gables Senior High; food service", "open", "Foundant/GrantInterface", CGCF),
    ("Dr. Thomas E. Deal Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "Coral Gables Senior High; healthcare/medicine", "open", "Foundant/GrantInterface", CGCF),
    ("Garcia Perseverance Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "Coral Gables Senior High", "open", "Foundant/GrantInterface", CGCF),
    ("Garcia Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "Any public or private high school in Miami-Dade", "open", "Foundant/GrantInterface", CGCF),
    ("Grant and Bridget Daugherty Nursing Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "Coral Gables Senior High; nursing", "open", "Foundant/GrantInterface", CGCF),
    ("Robert & Marian Fewell Memorial Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "Coral Gables Senior High", "open", "Foundant/GrantInterface", CGCF),
    ("Coral Gables Bar Association Scholarship in Memory of Ervin A. Gonzalez", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "Coral Gables Senior High; law", "open", "Foundant/GrantInterface", CGCF),
    ("1980 Cavaliers Boys Soccer State Championship Scholarship in Memory of Team Captain Bruce Hayes", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "Coral Gables Senior High; soccer", "open", "Foundant/GrantInterface", CGCF),
    ("High-Achieving 'HALI' Four-Year Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "Coral Gables Senior High and beyond", "open", "Foundant/GrantInterface", CGCF),
    ("Kerdyk Family Trust Music Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "Coral Gables resident or student at a school in Coral Gables; music", "open", "Foundant/GrantInterface", CGCF),
    ("Principal Ralph V. Moore Jr. Scholarship for Cavalier Excellence", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "Coral Gables Senior High", "open", "Foundant/GrantInterface", CGCF),
    ("Julian Perez Memorial Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "Coral Gables Senior High", "open", "Foundant/GrantInterface", CGCF),
    ("Dave Ragan Jr. Memorial Golf Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "golf", "open", "Foundant/GrantInterface", CGCF),
    ("Mitchell Zuniga Football Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "football", "open", "Foundant/GrantInterface", CGCF),
    ("Rotary Foundation of Coral Gables Scholarship Fund", "Rotary Club of Coral Gables", "CGCF", "Miami-Dade", 1000, 20000, "", "", "leadership", "open", "Foundant/GrantInterface", CGCF),
    ("Shine Bright Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "leadership", "open", "Foundant/GrantInterface", CGCF),
    ("Jeannett Slesnick Community Spirit Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "leadership; communications", "open", "Foundant/GrantInterface", CGCF),
    ("Lady Suzanna P. Tweed Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "leadership", "open", "Foundant/GrantInterface", CGCF),
    ("Luke Sturgill Memorial Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "vocational/technical", "open", "Foundant/GrantInterface", CGCF),
    ("Walter & Alma Vogel Memorial Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "music; science/technology", "open", "Foundant/GrantInterface", CGCF),
    ("Erickson Zoellers Engineering Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "engineering", "open", "Foundant/GrantInterface", CGCF),
    ("Raymond Bravo Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "Any MDCPS high school", "open", "Foundant/GrantInterface", CGCF),
    ("Coco Plum Woman's Club Scholarship in Memory of Max Gruver", "Coco Plum Woman's Club", "CGCF", "Miami-Dade", 1000, 20000, "", "", "Coral Gables area", "open", "Foundant/GrantInterface", CGCF),
    ("First-Generation Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 1000, 20000, "", "", "first-generation college students", "open", "Foundant/GrantInterface", CGCF),
    ("Stamps Family Scholarship", "Stamps Foundation", "CGCF", "Miami-Dade", 20000, 20000, "2026-03-20", "", "Selected Miami-Dade public and private schools; principal or CAP advisor invitation", "nomination_only", "Foundant/GrantInterface", CGCF),
    ("Chifles 'Beyond the Bag' Employee Scholarship", "Plantain Products Company (Chifles)", "CGCF", "Miami-Dade", 0, 25000, "2026-01-02", "", "Children/minor dependents of Chifles employees", "employees_only", "Foundant/GrantInterface", CGCF),
    ("RCG Fain Scholarship", "Royal Caribbean Group", "CGCF", "Miami-Dade", 0, 0, "", "", "Royal Caribbean Group employees", "employees_only", "own website", CGCF),
    ("Ev Clay / PRSA Miami Chapter Endowment Scholarship", "PRSA Miami Chapter", "CGCF", "Miami-Dade", 0, 0, "", "", "South Florida public relations students", "open", "Foundant/GrantInterface", CGCF),
    ("James Captain Memorial Summer Camp Tuition Scholarship", "Coral Gables Community Foundation", "CGCF", "Miami-Dade", 0, 0, "", "", "Elementary students in Coral Gables/Coconut Grove", "open", "Foundant/GrantInterface", CGCF),

    # ---------------- The Miami Foundation (9 public funds) ----------------------
    ("Venture Miami Scholarship (Creative Hub)", "The Miami Foundation", "TMF", "Miami-Dade", 0, 0, "2026-07-05", "", "City of Miami residents accepted to Creative Hub Academy", "open", "own portal", TMF),
    ("College Assistance Program (CAP) Scholarship", "The Miami Foundation / CAP Inc.", "TMF", "Miami-Dade", 0, 0, "2026-05-24", "", "MDCPS graduates with unmet financial need after all other aid", "open", "own portal", TMF),
    ("Ortega Foundation Scholarship", "Ortega Foundation", "TMF", "Miami-Dade", 0, 0, "2026-03-29", 3.5, "Miami-Dade County high school seniors", "open", "own portal", TMF),
    ("Alan R. Epstein 'Reach For The Stars' Scholarship", "Epstein family", "TMF", "Miami-Dade", 0, 0, "2026-04-05", "", "Miami-Dade seniors who have overcome significant adversity", "open", "own portal", TMF),
    ("Future Lawyers Scholarship", "DRRT", "TMF", "Miami-Dade,Broward", 5000, 15000, "2026-03-15", "", "Miami-Dade or Broward resident admitted to an ABA-accredited law school", "open", "own portal", TMF),
    ("Give Kids A Chance Scholarship", "Brian McDonough, Esq.", "TMF", "Miami-Dade", 0, 0, "2026-03-15", "", "Florida high school seniors from lower-income families", "open", "own portal", TMF),
    ("Judge Sidney M. Aronovitz Memorial Scholarship", "Aronovitz Family", "TMF", "Miami-Dade", 0, 0, "2026-03-15", "", "Miami-Dade minority students pursuing law or social justice", "open", "own portal", TMF),
    ("Kozyak Summer Fellowship Fund", "Kozyak Minority Mentoring Foundation", "TMF", "Miami-Dade", 5000, 5000, "2026-03-15", "", "Minority and first-generation law students at FL schools or FL residents; 10-12 fellowships in 2026", "open", "own portal", TMF),
    ("Liberty Square/Lincoln Gardens Student Scholarship Fund", "The Related Group", "TMF", "Miami-Dade", 0, 0, "2026-05-24", "", "Residents of Liberty Square or Lincoln Gardens", "open", "own portal", TMF),

    # ---------------- Community Foundation of Broward -----------------------------
    ("Fort Lauderdale Alumnae Panhellenic Scholarship", "Fort Lauderdale Alumnae Panhellenic", "CFB", "Broward", 0, 0, "2026-04-30", "", "Young women with strong academics and service", "open", "own portal", CFB),
    ("Ralph H. and Ruth Frank Gross Memorial Scholarship", "Community Foundation of Broward", "CFB", "Broward", 0, 0, "", "", "Government employees and their families", "open", "own portal", CFB),
    ("Mary Houliston MacDonald Scholarship for Women", "Community Foundation of Broward", "CFB", "Broward", 0, 0, "", "", "Women who are divorced, widowed or abandoned by their husbands", "open", "own portal", CFB),
    ("Tripp Family Fund for Educational Opportunity", "Norman Tripp family", "CFB", "Broward", 0, 0, "", "", "Women transferring from Broward College to FAU", "open", "own portal", CFB),

    # ---------------- George Snow Scholarship Fund --------------------------------
    ("George Snow High School Scholarships", "George Snow Scholarship Fund", "SNOW", "Broward,Palm Beach", 0, 0, "2026-02-01", "", "Seniors attending a Palm Beach or Broward County high school; financial need; NO minimum GPA; any accredited school; any major; home-schooled students zoned for a PBC/Broward high school qualify", "open", "own portal", SNOW),

    # ---------------- Community Foundation for Palm Beach & Martin ----------------
    ("Community Foundation for Palm Beach and Martin Counties Scholarships", "Community Foundation for Palm Beach and Martin Counties", "CFPBMC", "Palm Beach", 0, 0, "2026-03-04", 2.0, "Graduating senior in Palm Beach or Martin County; US citizen or permanent resident; one application matched to 120+ funds", "open", "own portal", CFPBMC),

    # ---------------- Jupiter HS counselor bulletin (Google Sites) ----------------
    ("Adele Marie Bradley Scholarship", "Adele Marie Bradley Fund", "", "Palm Beach", 3000, 3000, "2026-05-30", 3.5, "Seniors; merit plus essay on persevering through adversity", "open", "", JHS),
    ("Charles O'Meilia Scholarship", "Charles O'Meilia Fund", "", "Palm Beach", 1000, 1000, "2026-05-31", "", "Palm Beach County resident majoring in architecture, engineering, construction or public service", "open", "", JHS),
    ("PBC Friends of Youth Services Nursing Scholarship", "Palm Beach County Friends of Youth Services", "", "Palm Beach", 4500, 9000, "2026-06-01", "", "Palm Beach County resident pursuing a nursing program; $4,500/yr for two years", "open", "", JHS),
    ("Caden Ingram Foundation Scholarship", "Caden Ingram Foundation", "", "Palm Beach", 0, 0, "2026-06-01", "", "Service related; awareness of substances and societal problems", "open", "", JHS),
    ("Kantner Foundation Scholarship", "Kantner Foundation", "", "Palm Beach", 2000, 3000, "2026-06-30", "", "Florida resident seniors; academics, leadership and entrepreneurship", "open", "", JHS),
    ("Dave Davis Memorial Scholarship", "Dave Davis Memorial Fund", "", "Palm Beach", 0, 0, "2026-08-14", 3.0, "Palm Beach County senior; 300 service hours in one area; full-time college; leadership", "open", "", JHS),
    ("South Florida Business Aviation Association Scholarship", "South Florida Business Aviation Association", "", "Palm Beach", 0, 0, "2026-08-14", 3.0, "Palm Beach County senior attending an aviation-focused college; aviation career", "open", "", JHS),
    ("PBSC Presidential Honors Scholarship", "Palm Beach State College", "", "Palm Beach", 6000, 6000, "", 3.5, "Seniors only; college-ready scores; honors track", "open", "", JHS),
    ("PBSC Green & Gold Scholarship", "Palm Beach State College", "", "Palm Beach", 3000, 3000, "", 3.2, "Graduating seniors only; college-ready scores", "open", "", JHS),
    ("Finish4Free Scholarship", "Palm Beach State College", "", "Palm Beach", 0, 0, "", "", "Seniors with 30+ dual-enrollment credits; full tuition to complete an AA", "open", "", JHS),
    ("Dual2Degree Scholarship", "Palm Beach State College", "", "Palm Beach", 0, 0, "", 3.0, "Seniors who completed dual enrollment and a FAFSA", "open", "", JHS),
    ("Haitian Excellence in Business & Education Scholarship", "Haitian Excellence in Business & Education", "", "Palm Beach", 0, 0, "", "", "Essay; pursuing business or education", "open", "", JHS),
]

COLS = ["name", "sponsor", "hub", "counties", "amount_min", "amount_max", "deadline",
        "gpa_min", "eligibility_raw", "beneficiary_scope", "platform", "source_url"]


def main(out_path):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(COLS)
        w.writerows(ROWS)

    from collections import Counter
    by_county = Counter(r[3] for r in ROWS)
    by_scope = Counter(r[9] for r in ROWS)
    with_deadline = sum(1 for r in ROWS if r[6])
    with_amount = sum(1 for r in ROWS if r[5])
    hubs = len({r[2] for r in ROWS if r[2]})

    print(f"{len(ROWS)} awards extracted from 10 harvested pages -> {out_path}")
    print(f"  hubs represented:        {hubs}")
    print(f"  deadline published:      {with_deadline}/{len(ROWS)} ({with_deadline/len(ROWS):.0%})")
    print(f"  amount published:        {with_amount}/{len(ROWS)} ({with_amount/len(ROWS):.0%})")
    print()
    print("  By county:")
    for c, n in by_county.most_common():
        print(f"    {c:<22}{n:>4}")
    print("  By beneficiary scope:")
    for s, n in by_scope.most_common():
        print(f"    {s:<22}{n:>4}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/10_south_florida_awards.csv")
