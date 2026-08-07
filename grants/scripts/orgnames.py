#!/usr/bin/env python3
"""
Chapter-name resolution.

The BMF lists most service clubs under their NATIONAL parent's name -- "ROTARY
INTERNATIONAL", "KIWANIS INTERNATIONAL INC", "LOYAL ORDER OF MOOSE". Searching
that name finds the national body and nothing local, which is why two orgs in the
n=15 verification sample looked like failures when they may run real programs.

The fix needs no new data: BMF's SORT_NAME column already carries the local
chapter, in one of three shapes.

    ROTARY INTERNATIONAL      SORT_NAME="TAMPA WESTCHASE ROTARY CLUB"   already complete
    KIWANIS INTERNATIONAL INC SORT_NAME="K09593 SAFETY HARBOR"          club no. + place
    BENEVOLENT ... ELKS       SORT_NAME="2495 SARASOTA"                 lodge no. + place

This module turns any of those into a name a search engine can actually find.
"""

import re

# NAME pattern -> (canonical suffix, how a chapter of this order is styled)
PARENTS = [
    (r"\bROTARY INTERNATIONAL\b",                      "Rotary Club"),
    (r"\bKIWANIS INTERNATIONAL\b",                     "Kiwanis Club"),
    (r"\b(?:INTERNATIONAL ASSOCIATION OF )?LIONS CLUB", "Lions Club"),
    (r"\bWOMEN OF THE MOOSE\b",                        "Women of the Moose Chapter"),
    (r"\bLOYAL ORDER OF MOOSE\b",                      "Moose Lodge"),
    (r"\bPROTECTIVE ORDER OF ELKS\b",                  "Elks Lodge"),
    (r"\bAMERICAN LEGION\b",                           "American Legion Post"),
    (r"\bVETERANS OF FOREIGN WARS\b",                  "VFW Post"),
    (r"\bKNIGHTS OF COLUMBUS\b",                       "Knights of Columbus Council"),
    (r"\bFRATERNAL ORDER OF EAGLES\b",                 "Eagles Aerie"),
    (r"\bSOROPTIMIST INTERNATIONAL\b",                 "Soroptimist International"),
    (r"\bZONTA INTERNATIONAL\b",                       "Zonta Club"),
    (r"\bALTRUSA INTERNATIONAL\b",                     "Altrusa Club"),
    (r"\bPILOT CLUB INTERNATIONAL\b",                  "Pilot Club"),
    (r"\bOPTIMIST INTERNATIONAL\b",                    "Optimist Club"),
    (r"\bCIVITAN INTERNATIONAL\b",                     "Civitan Club"),
    (r"\bEXCHANGE CLUB\b",                             "Exchange Club"),
    (r"\bAMERICAN ASSOCIATION OF UNIVERSITY WOMEN\b",  "AAUW Branch"),
    (r"\bJUNIOR LEAGUE\b",                             "Junior League"),
    (r"\bP\.?E\.?O\.? SISTERHOOD\b",                   "P.E.O. Chapter"),
    (r"\bDAUGHTERS OF THE AMERICAN REVOLUTION\b",      "DAR Chapter"),
    (r"\bBUSINESS & PROFESSIONAL WOMEN\b",             "BPW Club"),
    (r"\bAMVETS\b",                                    "AMVETS Post"),
    (r"\bORDER SONS OF ITALY\b",                       "Sons of Italy Lodge"),
]
PARENTS = [(re.compile(p), s) for p, s in PARENTS]

# "K09593 ", "64896 ", "2495 ", "321 " -- club/lodge/post number prefixes
LEADING_NUMBER = re.compile(r"^[A-Z]{0,2}\d{2,6}\b\s*")
TRAILING_NUMBER = re.compile(r"\s*\b[A-Z]{0,2}\d{2,6}$")

# Words that mean SORT_NAME is an administrative label, not a place
NOISE = re.compile(r"\b(?:E ?CLUB|DISTRICT|ZONE|REGION|AREA|DIV(?:ISION)?)\b")

# SORT_NAME that is a trustee/person/number rather than a place
PLACE_REJECT = re.compile(r"^\d+$|\b(?:TTEE|TRUSTEE|ESTATE|MEMORIAL|SCHOLARSHIP)\b")

# Structural and corporate words that carry no local identifying information.
# What survives stripping these from a NAME is the part that makes it local.
FILLER = re.compile(
    r"\b(?:INC|INCORPORATED|CORP|CORPORATION|CO|LLC|LTD|FOUNDATION|CHARITABLE|"
    r"CHARITIES|CHARITY|TRUST|FUND|ASSOCIATION|ASSN|SOCIETY|ORGANIZATION|"
    r"INTERNATIONAL|NATIONAL|AMERICA|AMERICAN|USA|UNITED|STATES|THE|OF|AND|"
    r"CLUB|LODGE|POST|CHAPTER|COUNCIL|AERIE|BRANCH|TEMPLE|CAMP|UNIT|AUXILIARY|"
    r"NO|NUMBER|BENEVOLENT|PROTECTIVE|IMPROVED|ORDER|LOYAL|FRATERNAL|GRAND|"
    r"SUPREME|SISTERHOOD|WOMEN|MEN|JUNIOR|LEAGUE)\b"
)

# Repeated structural nouns after composition ("Elks Lodge of X Lodge Y")
DUP_STRUCT = re.compile(r"\b(Lodge|Club|Post|Chapter|Council|Branch|Aerie)\b\s+",
                        re.IGNORECASE)

SMALL = {"of", "the", "and", "at", "de", "la"}


def titlecase(s: str) -> str:
    """Title-case a shouted place name without mangling initials or hyphenates."""
    out = []
    for i, w in enumerate(s.split()):
        if len(w) <= 2 and w.isalpha() and i > 0 and w.lower() in SMALL:
            out.append(w.lower())
        elif "-" in w:
            out.append("-".join(p.capitalize() for p in w.split("-")))
        elif len(w) <= 3 and w.isupper() and w.lower() not in SMALL and not w.isdigit():
            out.append(w if w in {"USA", "AAUW", "VFW", "DAR", "BPW"} else w.capitalize())
        else:
            out.append(w.capitalize())
    return " ".join(out)


def parent_of(name: str):
    """
    Return the canonical chapter styling only if NAME is a *bare* national parent.

    "ROTARY INTERNATIONAL" needs rewriting. "VENICE LIONS CLUB FOUNDATION INC"
    and "ENGLEWOOD LODGE NO 1933 LOYAL ORDER OF MOOSE" do not -- they already
    name their town, and the original is what the club actually calls itself.
    """
    n = (name or "").upper()
    for pat, suffix in PARENTS:
        if not pat.search(n):
            continue
        residual = FILLER.sub(" ", pat.sub(" ", n))
        residual = re.sub(r"[^A-Z ]", " ", residual)
        if not residual.split():          # nothing local left -> bare parent
            return suffix
        return None
    return None


def clean_sort(sort_name: str) -> str:
    s = (sort_name or "").strip().upper()
    s = LEADING_NUMBER.sub("", s)
    s = TRAILING_NUMBER.sub("", s)
    return s.strip()


def resolve(name: str, sort_name: str, city: str):
    """
    -> (display_name, search_name, resolved)

    display_name  what to show a human and store as the sponsor
    search_name   what to hand a search engine
    resolved      True if we rewrote a national parent into a local chapter
    """
    name = (name or "").strip()
    suffix = parent_of(name)
    if not suffix:
        return name, name, False

    place = clean_sort(sort_name)

    # Administrative label, trustee name, bare number, or empty -> use the BMF city
    if not place or NOISE.search(place) or PLACE_REJECT.search(place):
        place = (city or "").strip().upper()
    if not place or PLACE_REJECT.search(place):
        return name, name, False

    core = suffix.split()[0].upper()          # ROTARY, KIWANIS, MOOSE, ELKS...
    if core in place:
        # SORT_NAME is already a complete club name ("TAMPA WESTCHASE ROTARY CLUB")
        display = titlecase(place)
    else:
        display = f"{suffix} of {titlecase(place)}"
        # "Elks Lodge of Lakewood Ranch Lodge Sarasota" -> drop the repeat
        head, sep, tail = display.partition(" of ")
        display = head + sep + DUP_STRUCT.sub("", tail).strip()

    return display, display, True


def search_query(display_name: str, city: str, state: str = "FL") -> str:
    """The query that actually surfaces a local chapter's scholarship page."""
    return f'"{display_name}" {titlecase(city or "")} {state} scholarship application'


if __name__ == "__main__":
    # (name, sort_name, city, should_rewrite)
    CASES = [
        ("ROTARY INTERNATIONAL", "TAMPA WESTCHASE ROTARY CLUB", "TAMPA", True),
        ("ROTARY INTERNATIONAL", "", "HUDSON", True),
        ("ROTARY INTERNATIONAL", "WHITE J SHERWOOD TTEE", "ST PETERSBURG", True),
        ("KIWANIS INTERNATIONAL INC", "K09593 SAFETY HARBOR", "SAFETY HARBOR", True),
        ("KIWANIS INTERNATIONAL INC", "", "ZEPHYRHILLS", True),
        ("BENEVOLENT & PROTECTIVE ORDER OF ELKS OF THE USA", "2495 SARASOTA", "SARASOTA", True),
        ("BENEVOLENT & PROTECTIVE ORDER OF ELKS OF THE USA",
         "LAKEWOOD RANCH LODGE SARASOTA", "SARASOTA", True),
        ("INTERNATIONAL ASSOCIATION OF LIONS CLUB",
         "64896 PORT ST LUCIE DOWNTOWN", "PORT ST LUCIE", True),
        ("ROTARY INTERNATIONAL", "E CLUB OF SOUTHEAST USA AND CARIBBE", "WEBSTER", True),
        # already local -- must be left alone
        ("VENICE LIONS CLUB FOUNDATION INC", "", "VENICE", False),
        ("ENGLEWOOD LODGE NO 1933 LOYAL ORDER OF MOOSE", "1933", "ENGLEWOOD", False),
        ("BRADENTON CHAPTER NO 1072 WOMEN OF THE MOOSE", "1072 BRADENTON", "BRADENTON", False),
        ("JUNIOR LEAGUE OF TAMPA INC", "", "TAMPA", False),
        ("CATHOLIC COMMUNITY FOUNDATION OF SOUTHWEST FLORIDA INC", "", "VENICE", False),
    ]
    w = max(len(c[0]) for c in CASES)
    fails = 0
    for nm, sn, city, want in CASES:
        disp, _, res = resolve(nm, sn, city)
        ok = res == want
        fails += not ok
        print(f"{'ok ' if ok else 'FAIL'} {'REWRITE' if res else 'keep   '} "
              f"{nm[:w]:<{w}}  ->  {disp}")
    print(f"\n{len(CASES) - fails}/{len(CASES)} passed")
    raise SystemExit(1 if fails else 0)
