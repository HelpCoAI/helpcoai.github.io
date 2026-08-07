#!/usr/bin/env python3
"""
Cross-source dedupe, and the breadth signal that falls out of it.

Harvesting many school counselor pages produces the same award repeatedly. That
repetition is not noise -- it is a free measurement of how widely an award is
available, which is the hardest input to win probability.

    listed on 1 school page      -> hyperlocal; eligible pool is one senior class
    listed on 2-5 school pages   -> a cluster of schools, or a feeder pattern
    listed on 6+ school pages    -> district-wide
    listed on most pages         -> regional, state, or national -- deprioritise

A counselor lists an award because their students can actually apply to it. So
breadth is both an eligibility proxy AND a relevance filter, obtained without
asking anyone anything and without a human verifying a single organization.

Usage:
    python3 14_award_breadth.py data/10_south_florida_awards.csv [more.csv ...]
"""

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

# Words that vary between listings of the same award and must not affect matching
NOISE = re.compile(
    r"\b(?:the|a|an|of|for|and|in|at|to|memorial|endowment|endowed|fund|funds|"
    r"scholarship|scholarships|award|awards|program|inc|foundation|trust|"
    r"annual|sr|jr)\b", re.I)
PUNCT = re.compile(r"[^a-z0-9 ]")
SPACES = re.compile(r"\s+")


def normalize(name: str) -> str:
    """A key that survives 'The Smith Family Memorial Scholarship Fund' vs 'Smith Family Scholarship'."""
    s = (name or "").lower()
    s = PUNCT.sub(" ", s)
    s = NOISE.sub(" ", s)
    return SPACES.sub(" ", s).strip()


def classify(n_sources: int, n_total: int) -> str:
    if n_sources <= 1:
        return "hyperlocal"
    if n_sources <= 5:
        return "school-cluster"
    if n_sources < max(6, n_total * 0.5):
        return "district-wide"
    return "broad"


def main(paths):
    rows = []
    for p in paths:
        with open(p, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                r["_file"] = Path(p).name
                rows.append(r)

    if not rows:
        sys.exit("No rows read.")

    groups = defaultdict(list)
    for r in rows:
        key = normalize(r.get("name", ""))
        if key:
            groups[key].append(r)

    # distinct source pages overall, for the "broad" threshold
    n_sources_total = len({r.get("source_url", r["_file"]) for r in rows})

    out = []
    for key, members in groups.items():
        srcs = {m.get("source_url", m["_file"]) for m in members}
        best = max(members, key=lambda m: sum(1 for v in m.values() if v))
        out.append({
            "name": best.get("name", ""),
            "sponsor": best.get("sponsor", ""),
            "counties": best.get("counties", ""),
            "amount_min": best.get("amount_min", ""),
            "amount_max": best.get("amount_max", ""),
            "deadline": best.get("deadline", ""),
            "beneficiary_scope": best.get("beneficiary_scope", ""),
            "listed_on_n_sources": len(srcs),
            "breadth": classify(len(srcs), n_sources_total),
            "duplicate_listings": len(members),
            "source_urls": ";".join(sorted(srcs)),
        })

    out.sort(key=lambda r: (-r["listed_on_n_sources"], r["name"]))

    out_path = Path(paths[0]).parent / "11_awards_deduped.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    from collections import Counter
    by_breadth = Counter(r["breadth"] for r in out)
    dupes = sum(1 for r in out if r["duplicate_listings"] > 1)

    print(f"{len(rows)} listings across {n_sources_total} source pages")
    print(f"  -> {len(out)} distinct awards ({len(rows) - len(out)} duplicate listings merged)")
    print(f"  {dupes} awards appear on more than one page")
    print()
    print("Breadth (the eligible-pool proxy):")
    for b in ("hyperlocal", "school-cluster", "district-wide", "broad"):
        if by_breadth.get(b):
            print(f"  {b:<16}{by_breadth[b]:>5}")
    print()
    print("Most widely listed (likely regional/national — rank these DOWN):")
    for r in out[:5]:
        if r["listed_on_n_sources"] > 1:
            print(f"  {r['listed_on_n_sources']:>2} pages  {r['name'][:60]}")
    print(f"\nWritten to {out_path}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["data/10_south_florida_awards.csv"])
