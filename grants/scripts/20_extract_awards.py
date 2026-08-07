#!/usr/bin/env python3
"""
Turn cleaned pages into award records carrying the full filter schema.

This replaces the LLM extract path for the structured majority of the corpus.
It exists because the counselor bulletins -- the highest-yield pages we have --
are not prose. They are tables that survived HTML flattening:

    Name  Amount  Deadline  Requirements
    Miami-Dade County Fair and Exposition High School Scholarships $1,000 01/15
    Miami-Dade County graduating high school seniors with a minimum 3.0
    cumulative GPA and planning to attend an accredited college ...

A "$1,000 01/15" pair is a record boundary you can find without a model: text
before it is the award name, text after it is the eligibility prose, and the
next money+date pair ends the record. Everything downstream is regex over that
prose.

Two rules from docs/filter-schema.md are enforced here and must not be relaxed:

  eligibility_raw is verbatim. Structuring is lossy; the raw block is the audit
  trail, and it is what a student sees when they dispute a match.

  Absent means unknown, never false. A page that never mentions citizenship
  yields an EMPTY citizenship field, not "no requirement". Filtering a student
  OUT on an inferred requirement costs them an award they could have won -- the
  same failure mode as publishing a stale deadline, and less visible.

Fields that cannot be read off the text reliably (num_awards, applicants) are
left empty for the ranking pass rather than guessed, because expected value is
the product's whole claim and a fabricated denominator poisons it.

Usage:
    python3 20_extract_awards.py --pages 'data/clean/*' --out data/15_awards.csv
    python3 20_extract_awards.py --pages 'data/clean/*' --out /dev/null --stats
"""

import argparse
import csv
import glob
import json
import re
import sys
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------- segmentation

MONEY = r"\$\s?\d[\d,]*(?:\.\d{2})?(?:\s?[-–]\s?\$?\s?\d[\d,]*)?"
# The leading \b is load-bearing: without it "Sep[a-z]*" matched inside "Joseph
# 20" and produced a deadline of "seph 20". Same class of bug gave "July 23,
# 1925" -- a page listing a founding year, not a deadline; see sane_date().
DATE = (r"(?:\d{1,2}/\d{1,2}(?:/\d{2,4})?|"
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"(?:uary|ruary|ch|il|e|y|ust|tember|ober|ember)?\.?\s+\d{1,2}"
        r"(?:,?\s+\d{4})?)")
# The record boundary: an amount immediately followed by a deadline.
ANCHOR = re.compile(rf"({MONEY})\s+({DATE})", re.I)

# Fallback boundary for prose pages: a Title Case award name. Requires >=2
# capitalised words so "The Scholarship" in a sentence does not open a record.
NAME_ANCHOR = re.compile(
    r"((?:[A-Z][\w'’.\-]+\s+){1,7}"
    r"(?:Scholarship|Award|Grant|Fund|Prize|Bursary|Fellowship)s?)\b")

MAX_BLOCK = 2200          # chars; beyond this the "record" is really a page


def segment(body: str):
    """
    -> list of (name, raw_block). Table anchors first; name anchors otherwise.

    Table mode is preferred wherever it fires because the money+date pair is a
    far stronger boundary than capitalisation, which fires on every heading.
    """
    hits = list(ANCHOR.finditer(body))
    if len(hits) >= 2:
        out, prev_end = [], 0
        for i, m in enumerate(hits):
            name = body[prev_end:m.start()].strip(" .,-–—:|")
            tail_end = hits[i + 1].start() if i + 1 < len(hits) else len(body)
            # The next record's NAME sits between this record's prose and the
            # next anchor, so hand it back by trimming at the last sentence end.
            tail = body[m.end():tail_end]
            block = (f"{name} {m.group(0)} {tail}").strip()
            if len(name) > 3:
                out.append((_clean_name(name), block[:MAX_BLOCK]))
            prev_end = m.end() + len(tail)
        return out

    out, marks = [], list(NAME_ANCHOR.finditer(body))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        block = body[m.start():end].strip()
        if len(block) > 60:
            out.append((_clean_name(m.group(1)), block[:MAX_BLOCK]))
    return out


def _clean_name(name: str) -> str:
    """
    Recover the award title from the text preceding a table anchor.

    In table mode that text is the previous record's trailing prose followed by
    this record's title, with no separator that survived HTML flattening. Taking
    it whole produced names like "Resources Contact Us Explore MDCPS Bright
    Futures Scholarship" and "Florida. Award". So: prefer the LAST title-shaped
    phrase in the span, and fall back to the trailing words only if none exists.
    """
    name = re.sub(r"\s+", " ", name).strip(" .,-–—:|")
    # Table headers and surviving nav bleed into the head of a name, and
    # NAME_ANCHOR cannot help: its {1,7} repetition matches greedily from the
    # earliest position, so "Resources Contact Us Explore MDCPS Bright Futures
    # Scholarship" is one match, not a title preceded by junk. Peel the junk off
    # the front instead -- repeatedly, since it arrives in runs.
    while True:
        stripped = re.sub(
            r"^(?:Name|Amount|Awarded|Deadline|Requirements?|Description|"
            r"Provider|Overview|Criteria|Resources?|Contact|Us|Explore|Home|"
            r"Menu|Search|Download|Guidelines|Closed|More|Details|Apply|View|"
            r"Read|Click|Here|Link|Website|Info(?:rmation)?|List(?:ing)?s?|"
            r"Current|Available|Open|New|Our|Other|Additional|Various|and|the|"
            r"Senior|Spotlights?|Technical|School)\b[\s|:.,\-–—]*",
            "", name, flags=re.I)
        if stripped == name:
            break
        name = stripped
    if not name:
        return ""
    # A sentence end is a hard boundary -- everything before it is the prior record.
    tail = re.split(r"(?<=[a-z])[.!?]\s+(?=[A-Z])", name)[-1]

    marks = list(NAME_ANCHOR.finditer(tail))
    if marks:
        cand = marks[-1].group(1).strip(" .,-–—:|")
        # "One Scholarship" / "Various Award" are fragments of a longer sentence,
        # not titles; keep the fuller span when the match is that thin.
        if len(cand.split()) >= 2 and not re.fullmatch(
                r"(?:One|Various|The|A|An|This|Each|Annual)\s+\w+", cand):
            return cand[:140]
    words_ = tail.split()
    return " ".join(words_[-9:]).strip(" .,-–—:|")[:140]


# ------------------------------------------------------------ field extraction

def money_range(block):
    m = re.search(MONEY, block)
    if not m:
        return "", ""
    nums = [int(n.replace(",", "")) for n in re.findall(r"\d[\d,]*", m.group(0))]
    if not nums:
        return "", ""
    return min(nums), max(nums)


def sane_date(s: str) -> str:
    """
    Drop anything with a year outside the plausible application window.

    Pages are full of years that are not deadlines: founding dates, memorial
    dates, award histories. "July 23, 1925" was being published as a deadline.
    A year-less date ("04/15") is kept -- bulletins genuinely write them that
    way, and the season is inferable from the source.
    """
    if not s:
        return ""
    for y in re.findall(r"\b(\d{4})\b", s):
        if not 2020 <= int(y) <= 2030:
            return ""
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?", s.strip())
    if m and not (1 <= int(m.group(1)) <= 12 and 1 <= int(m.group(2)) <= 31):
        return ""
    return s


def first(pattern, block, group=1, flags=re.I):
    m = re.search(pattern, block, flags)
    return m.group(group).strip() if m else ""


def has(pattern, block):
    """-> True or '' . Never False: absent means unknown, not 'no requirement'."""
    return True if re.search(pattern, block, re.I) else ""


def find_all(pattern, block, group=1):
    seen, out = set(), []
    for m in re.finditer(pattern, block, re.I):
        v = re.sub(r"\s+", " ", m.group(group)).strip(" .,")
        k = v.lower()
        if v and k not in seen:
            seen.add(k)
            out.append(v)
    return out


FL_COUNTIES = ("Miami-Dade|Dade|Broward|Palm Beach|Hillsborough|Pinellas|Pasco|"
               "Manatee|Sarasota|Monroe|Collier|Lee|Orange|Osceola|Seminole|"
               "Duval|Polk|Brevard|Volusia|Charlotte|Martin|Indian River|"
               "St. Lucie|Okeechobee|Hendry|Highlands|Glades")

CITIES = ("Miami|Miami Beach|Miami Gardens|Miami Lakes|Hialeah|Coral Gables|"
          "Homestead|Doral|Aventura|Kendall|Pinecrest|Palmetto Bay|Cutler Bay|"
          "Fort Lauderdale|Hollywood|Pembroke Pines|Coral Springs|Plantation|"
          "Sunrise|Davie|Weston|Miramar|Pompano Beach|Deerfield Beach|"
          "West Palm Beach|Boca Raton|Delray Beach|Boynton Beach|Jupiter|"
          "Wellington|Palm Beach Gardens|Lake Worth|Tampa|St. Petersburg|"
          "Clearwater|Brandon|Riverview|Bradenton|Sarasota|Venice|Hudson|"
          "New Port Richey|Land O' Lakes|Wesley Chapel|Largo|Dunedin|Palmetto")

MAJORS = ("engineering|nursing|medicine|pre-med|education|teaching|business|"
          "accounting|finance|marketing|computer science|information technology|"
          "cybersecurity|law|criminal justice|journalism|communications|"
          "agriculture|environmental science|biology|chemistry|physics|"
          "mathematics|architecture|art|music|theat(?:er|re)|dance|film|"
          "culinary|hospitality|aviation|automotive|welding|construction|"
          "cosmetology|social work|psychology|veterinar|dental|pharmac|"
          "STEM|health care|healthcare|public health|trades")

ACTIVITIES = ("community service|volunteer(?:ing|ism)?|athletics?|varsity|"
              "band|marching band|orchestra|chorus|choir|debate|speech|"
              "student government|drama|theatre|robotics|yearbook|newspaper|"
              "mentoring|tutoring|leadership|work experience|internship")

CLUBS = ("Key Club|Beta Club|National Honor Society|NHS|Interact|Rotaract|"
         "4-H|FFA|FBLA|DECA|HOSA|SkillsUSA|FCCLA|TSA|JROTC|ROTC|Boy Scouts?|"
         "Girl Scouts?|Eagle Scout|Gold Award|Scouts BSA|Boys? (?:&|and) Girls? Club|"
         "AVID|Thespians?|Model UN|Mu Alpha Theta|Science National Honor Society")

CLASS_YEAR = ("graduating senior|high school senior|current senior|"
              "junior|sophomore|freshman|undergraduate|graduate student|"
              "college student|returning student|adult learner|transfer student")


def extract_fields(name, block, meta):
    lo, hi = money_range(block)
    gpa = first(r"(?:minimum|min\.?|at least|cumulative|weighted|unweighted|"
                r"gpa of|GPA)\D{0,18}(\d\.\d{1,2})", block)
    # A "4.0 scale" mention is the scale, not the requirement.
    if gpa and re.search(rf"{re.escape(gpa)}\s*(?:scale|point)", block, re.I):
        gpa = ""

    college_plan = []
    for pat, label in ((r"four[- ]year|4[- ]year|university|bachelor", "four_year"),
                       (r"two[- ]year|2[- ]year|community college|associate", "two_year"),
                       (r"trade school|technical (?:school|college)|apprentice", "trade"),
                       (r"vocational|voc[- ]?tech|certificate program", "vocational"),
                       (r"any accredited|accredited (?:post-?secondary|institution)", "any")):
        if re.search(pat, block, re.I):
            college_plan.append(label)

    gender = ""
    if re.search(r"\b(?:female|women|woman|girls?)\b", block, re.I):
        gender = "female"
    if re.search(r"\b(?:male|men|man|boys?)\b", block, re.I):
        gender = "male" if not gender else "any"

    scope = ""
    if re.search(r"\bnominat", block, re.I):
        scope = "nomination_only"
    elif re.search(r"member(?:s|ship)? of (?:the )?(?:our|this)?\s*\w*\s*"
                   r"(?:club|chapter|lodge|post|council)", block, re.I):
        scope = "members_only"
    elif re.search(r"child(?:ren)? of|dependent of|employee[s']? (?:of|and)", block, re.I):
        scope = "employees_only"
    elif re.search(r"open to|any student|all students|applicants must", block, re.I):
        scope = "open"

    renewal = first(r"renewable (?:for )?(?:up to )?(\d)\s*(?:year|yr)", block)

    return {
        "name": name[:140],
        "sponsor": meta.get("org", ""),
        "amount_min": lo,
        "amount_max": hi,
        "deadline": sane_date(first(rf"({DATE})", block)),
        "opens": sane_date(first(rf"(?:opens?|available|applications? open)"
                          rf"\D{{0,20}}({DATE})", block)),
        "gpa_min": gpa,
        "gpa_scale": first(r"(\d\.\d)\s*(?:point )?scale", block),

        "counties": find_all(rf"\b({FL_COUNTIES})\b(?=\s*(?:County|county|residents?|\b))", block),
        "cities": find_all(rf"\b({CITIES})\b", block),
        "high_schools": find_all(r"\b([A-Z][\w'.\-]+(?:\s+[A-Z][\w'.\-]+){0,4}\s+"
                                 r"(?:High School|Senior High|HS|Academy|Preparatory))\b",
                                 block),
        "majors": find_all(rf"\b({MAJORS})\b", block),
        "activities": find_all(rf"\b({ACTIVITIES})\b", block),
        "clubs_organizations": find_all(rf"\b({CLUBS})\b", block),
        "college_plan": college_plan,

        "need_based": has(r"financial need|need-based|need based|low[- ]income|"
                          r"EFC|Pell|free/reduced|free or reduced", block),
        "merit_based": has(r"\bmerit\b|academic (?:achievement|excellence|merit)|"
                           r"based on merit", block),
        "first_generation": has(r"first[- ]generation|first in (?:their|his|her|the) family",
                                block),
        "disability": has(r"disabilit|hearing loss|visually impaired|blind|deaf|"
                          r"wheelchair|special needs", block),
        "citizenship": find_all(r"\b(U\.?S\.? citizens?|permanent residents?|"
                                r"DACA|undocumented|eligible non-?citizens?)\b", block),
        "heritage": find_all(r"\b(African[- ]American|Black|Hispanic|Latino|Latina|"
                             r"Latinx|American Indian|Native American|Asian|"
                             r"Pacific Islander|Haitian|Cuban|Jewish|Italian[- ]American|"
                             r"Greek|Polish|Irish)\b", block),
        "gender": gender,
        "military_affiliation": first(r"\b(veterans?|active duty|military|"
                                      r"National Guard|Gold Star)\b", block),
        "employer_affiliation": first(r"(?:employees?|children of employees?) of "
                                      r"([A-Z][\w &.\-]{3,40})", block),

        "income_max": first(r"(?:household |family )?income (?:of |at or )?"
                            r"(?:below|under|less than|not exceed(?:ing)?)\s*\$?([\d,]+)",
                            block).replace(",", ""),
        "class_year": find_all(rf"\b({CLASS_YEAR})\b", block),
        "enrollment_status": find_all(r"\b(full[- ]time|part[- ]time)\b", block),
        "destination_institutions": find_all(
            r"\b((?:University|College) of [A-Z][\w .\-]{2,30}|"
            r"[A-Z][\w'.\-]+(?:\s+[A-Z][\w'.\-]+){0,3}\s+(?:University|College))\b", block),
        "residency_required": has(r"resid(?:e|ent|ing|ency) (?:in|of|within)", block),
        "renewable": True if renewal else has(r"renewab", block),
        "renewal_years": renewal,

        "essay_required": has(r"\bessays?\b|personal statement|written response", block),
        "recommendation_letters": first(r"(\d+)\s*(?:letters? of )?recommendation", block),
        "transcript_required": has(r"transcript", block),
        "fafsa_required": has(r"\bFAFSA\b", block),
        "beneficiary_scope": scope,

        "eligibility_raw": re.sub(r"\s+", " ", block).strip(),
        "source_url": meta.get("url", ""),
        "source_org": meta.get("org", ""),
        "source_county": meta.get("county", ""),
        "source_file": meta.get("file", ""),
    }


# ------------------------------------------------------------------- filtering

# A block must look like a real award, not a donate button or an alumni honour.
REJECT_NAME = re.compile(
    r"^(?:make a |ways to |donate|give|gift|establish|endow|create a |support |"
    r"contact|about|home|search|menu|login|apply now|click here|learn more)",
    re.I)
ALUMNI_HONOUR = re.compile(
    r"distinguished alumni|hall of fame|lifetime achievement|"
    r"teacher of the year|employee of the (?:month|year)", re.I)


def keep(rec) -> tuple[bool, str]:
    if len(rec["name"]) < 6:
        return False, "name too short"
    if REJECT_NAME.match(rec["name"]):
        return False, "call to action, not an award"
    if ALUMNI_HONOUR.search(rec["name"]) or ALUMNI_HONOUR.search(rec["eligibility_raw"][:300]):
        return False, "recognition award, not student aid"
    if len(rec["eligibility_raw"]) < 80:
        return False, "no eligibility text"
    # An award with neither money nor a deadline is almost always a menu item.
    if not rec["amount_min"] and not rec["deadline"]:
        return False, "no amount and no deadline"
    return True, ""


def read_page(path: Path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    meta, body = {"file": path.name}, raw
    m = re.match(r"\A(URL: .*?\n(?:.*?\n)*?-{20,}\n)", raw, re.M)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                if k.strip().lower() in ("url", "org", "county", "kind"):
                    meta[k.strip().lower()] = v.strip()
        body = raw[m.end():]
    return meta, body


def main(patterns, out_path, stats_only, min_len):
    paths = []
    for pat in patterns:
        for d in sorted(glob.glob(pat)):
            dp = Path(d)
            paths += ([p for p in sorted(dp.glob("*.txt")) if not p.name.startswith("_")]
                      if dp.is_dir() else [dp])
    if not paths:
        sys.exit(f"no pages matched {patterns}")

    rows, rejects, per_page = [], Counter(), Counter()
    for p in paths:
        meta, body = read_page(p)
        if len(body) < min_len:
            continue
        for name, block in segment(body):
            rec = extract_fields(name, block, meta)
            ok, why = keep(rec)
            if ok:
                rows.append(rec)
                per_page[p.name] += 1
            else:
                rejects[why] += 1

    # de-dup on (normalised name, sponsor) -- keeping the richest block, since
    # the same award recurs across a school's monthly bulletins
    best = {}
    for r in rows:
        k = (re.sub(r"[^a-z0-9]", "", r["name"].lower())[:60], r["source_org"].lower())
        if k not in best or len(r["eligibility_raw"]) > len(best[k]["eligibility_raw"]):
            best[k] = r
    deduped = list(best.values())

    # Write BEFORE reporting. Piping this script's output through `head` sends
    # SIGPIPE partway through the coverage table, which killed the process
    # before it ever wrote the CSV -- and left a stale file that looked current.
    if not stats_only and deduped:
        cols = list(deduped[0].keys())
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for r in deduped:
                w.writerow({k: (json.dumps(v) if isinstance(v, list) else v)
                            for k, v in r.items()})
        print(f"{len(deduped)} awards -> {out_path}\n", file=sys.stderr)

    print(f"{len(paths)} pages -> {len(rows)} blocks kept -> {len(deduped)} unique awards",
          file=sys.stderr)
    print(f"rejected: {dict(rejects.most_common())}", file=sys.stderr)
    print(f"\ntop pages by award count:", file=sys.stderr)
    for n, c in per_page.most_common(10):
        print(f"  {c:>3}  {n[:66]}", file=sys.stderr)

    filled = Counter()
    for r in deduped:
        for k, v in r.items():
            if v not in ("", [], None):
                filled[k] += 1
    print(f"\nfield coverage over {len(deduped)} awards:", file=sys.stderr)
    for k, c in filled.most_common():
        print(f"  {c / len(deduped):>5.0%}  {k}", file=sys.stderr)



if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", nargs="+", default=["data/clean/*"])
    ap.add_argument("--out", default="data/15_awards.csv")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--min-len", type=int, default=200)
    a = ap.parse_args()
    main(a.pages, a.out, a.stats, a.min_len)
