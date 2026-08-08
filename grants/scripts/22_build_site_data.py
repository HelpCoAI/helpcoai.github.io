#!/usr/bin/env python3
"""
Turn the enriched CSV into the JSON the site builds from.

The site never reads the database at build time and never reads it at request
time either. It reads this file. That is deliberate: the public pages are the
SEO asset, and an outage in a database must not be able to take them down.

This is also where publishability is decided, in one place, so the rule cannot
drift between pages:

  A page is indexable only if it carries at least MIN_AWARDS real awards and
  enough populated fields to be worth a visit. Everything else is built but
  marked noindex.

That bar exists because Google's scaled-content-abuse policy is the single
largest technical risk to this plan. A few hundred templated pages with three
facts each is what the policy was written to catch, and the defence is not
cleverness -- it is refusing to publish the thin ones.

Usage:
    python3 22_build_site_data.py --in data/16_awards_enriched.csv \
        --out site/src/data/awards.json
"""

import argparse
import csv
import html
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

MIN_AWARDS = 3          # per geo page, to be indexable
MIN_FIELDS = 6          # populated fields for an award page to be indexable
MIN_RAW = 250           # chars of eligibility text, likewise

COUNTIES = ["Miami-Dade", "Broward", "Palm Beach", "Hillsborough", "Pinellas",
            "Pasco", "Manatee", "Sarasota"]

META = {"eligibility_raw", "name_before_enrichment", "source_url", "source_org",
        "source_county", "source_file", "verdict", "confidence"}

LIST_COLS = {"counties", "cities", "high_schools", "majors", "activities",
             "clubs_organizations", "college_plan", "citizenship", "heritage",
             "class_year", "enrollment_status", "destination_institutions"}


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:70]


def detok(s):
    """
    Decode HTML entities the text extractor left encoded.

    "Eda &amp; Cliff Viner" was rendering literally on the award page, along with
    &#8217; and &rsquo; for apostrophes -- 100+ occurrences across the corpus.
    This does not violate the verbatim rule: the sponsor's page displays an
    ampersand, and "&amp;" is the HTML encoding of it, not the text. Decoding
    makes the quote MORE faithful to what a student sees on the sponsor's site.
    Escaping for safe output is Astro's job at render time, not ours here.
    """
    if not isinstance(s, str):
        return s
    prev = None
    # entities occasionally survive double-encoded (&amp;#8217;)
    while s != prev:
        prev, s = s, html.unescape(s)
    return dedash(s)


def dedash(s: str) -> str:
    """
    House rule: no em dashes anywhere on the site.

    Enforced here rather than only in the templates because the last two the
    linter caught came from the DATA, not from anything written by hand. Crawled
    org names arrive as "Alonzo and Tracy Mourning Senior High — /cap-corner/",
    so a template-only fix would have left them on the page.

    Applies to our own fields. The sponsor's verbatim eligibility text is passed
    through untouched: it is quoted and attributed, and normalising someone's
    punctuation inside quotation marks is a small dishonesty for a style rule.
    """
    s = re.sub(r"\s*—\s*", ", ", s)
    return re.sub(r",\s*,", ",", s).strip(" ,")


def parse_list(v):
    try:
        out = json.loads(v or "[]")
        return [str(x) for x in out] if isinstance(out, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def populated(rec):
    return sum(1 for k, v in rec.items()
               if k not in META and v not in ("", [], None, False))


def counties_of(row, rec):
    """
    Which county pages should list this award.

    Uses the structured field first, and falls back to matching the county name
    in the raw eligibility text -- the structured lists are only 31% populated,
    and an award that says "open to Broward County graduating seniors" in prose
    belongs on the Broward page whether or not the extractor tagged it.
    """
    found = {c for c in rec["counties"] if c in COUNTIES}
    hay = " ".join([row.get("eligibility_raw", ""), row.get("source_county", "")])
    for c in COUNTIES:
        if re.search(re.escape(c).replace(r"\-", "[- ]?"), hay, re.I):
            found.add(c)
    return sorted(found)


def main(in_path, out_path):
    rows = list(csv.DictReader(open(in_path, encoding="utf-8")))
    awards, seen_slugs = [], defaultdict(int)

    for row in rows:
        if row.get("verdict") and row["verdict"] != "award":
            continue
        rec = {}
        for k, v in row.items():
            if k in META:
                continue
            rec[k] = ([detok(x) for x in parse_list(v)] if k in LIST_COLS
                      else (detok(v) if v != "" else None))

        base = slugify(f"{rec.get('name') or 'award'}-{rec.get('sponsor') or ''}")
        seen_slugs[base] += 1
        rec["slug"] = base if seen_slugs[base] == 1 else f"{base}-{seen_slugs[base]}"

        rec["counties"] = counties_of(row, rec)
        # NOT dedashed: this is the sponsor speaking, in quotation marks.
        raw = row.get("eligibility_raw", "")
        prev = None
        while raw != prev:
            prev, raw = raw, html.unescape(raw)
        rec["eligibility_raw"] = raw
        rec["source_url"] = row.get("source_url", "")
        rec["source_org"] = detok(row.get("source_org", ""))
        rec["last_verified"] = date.today().isoformat()

        n = populated(rec)
        rec["fields_populated"] = n
        # Thin pages are still BUILT -- a student who lands on one deserves the
        # award's existence and its source link. They are just not offered to
        # Google as though they were substantive.
        rec["indexable"] = (n >= MIN_FIELDS
                            and len(rec["eligibility_raw"]) >= MIN_RAW)
        awards.append(rec)

    by_county = defaultdict(list)
    for a in awards:
        for c in a["counties"]:
            by_county[c].append(a["slug"])

    counties = []
    for c in COUNTIES:
        slugs = by_county.get(c, [])
        counties.append({
            "name": c, "slug": slugify(c), "award_slugs": slugs,
            "count": len(slugs),
            "indexable": len(slugs) >= MIN_AWARDS,
        })

    by_sponsor = defaultdict(list)
    for a in awards:
        if a.get("sponsor"):
            by_sponsor[a["sponsor"]].append(a["slug"])
    sponsors = [{"name": n, "slug": slugify(n), "award_slugs": s, "count": len(s),
                 # one award and nothing else is a stub, not a profile
                 "indexable": len(s) >= 2}
                for n, s in sorted(by_sponsor.items())]

    amounts = [int(a["amount_max"]) for a in awards
               if a.get("amount_max") and str(a["amount_max"]).isdigit()]
    payload = {
        "generated": date.today().isoformat(),
        "stats": {
            "awards": len(awards),
            "indexable_awards": sum(1 for a in awards if a["indexable"]),
            "counties_indexable": sum(1 for c in counties if c["indexable"]),
            "sponsors": len(sponsors),
            "sponsors_indexable": sum(1 for s in sponsors if s["indexable"]),
            "total_known_value": sum(amounts),
            "with_deadline": sum(1 for a in awards if a.get("deadline")),
        },
        "awards": awards, "counties": counties, "sponsors": sponsors,
    }

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(payload, indent=1), encoding="utf-8")
    s = payload["stats"]
    print(f"{s['awards']} awards ({s['indexable_awards']} indexable)", file=sys.stderr)
    print(f"{s['counties_indexable']} of {len(counties)} county pages indexable",
          file=sys.stderr)
    print(f"{s['sponsors']} sponsors ({s['sponsors_indexable']} indexable)",
          file=sys.stderr)
    print(f"total known award value ${s['total_known_value']:,}", file=sys.stderr)
    print(f"-> {out_path}", file=sys.stderr)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", default="data/16_awards_enriched.csv")
    ap.add_argument("--out", dest="out_path", default="site/src/data/awards.json")
    a = ap.parse_args()
    main(a.in_path, a.out_path)
