#!/usr/bin/env python3
"""
Find scholarship pages we never thought to guess, without more searching.

Two techniques, both cheap and both robots-respecting:

  sitemaps  Sites publish sitemap.xml specifically so crawlers can enumerate them.
            It is the most permission-aligned discovery there is, and we had never
            read a single one. Discovered via robots.txt's Sitemap: directive first,
            then the conventional locations.

  slugs     MDCPS schools run two CMS patterns with predictable scholarship paths.
            Probing three slugs against a known domain is far cheaper than
            searching for each school by name.

Output is a seed JSON the existing harvester consumes, so nothing downstream changes.

Usage:
    python3 16_discover_urls.py --seeds data/district_seeds_schools_miami_dade.json \\
        --out data/district_seeds_discovered.json --limit 35
"""

import argparse
import json
import re
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
_c = __import__("10_district_crawl")

KEYWORDS = re.compile(
    r"scholarship|cap[-_/]corner|college[-_]assistance|financial[-_]aid|"
    r"bulletin|college[-_]career|guidance|counsel|senior", re.I)

# Trimmed from six to the three most common MDCPS patterns. Each extra slug costs
# a request plus a politeness delay against every origin, and the long tail of
# patterns was not worth the minutes.
SLUGS = ["/cap-corner/", "/cap/", "/scholarships/"]

# Discovery probes speculative URLs, so most misses are dead hosts. At the crawler's
# 30s default a dead host costs 30 seconds; across ~30 dead origins that alone
# exceeded the job timeout. 8s is ample for a host that is actually alive.
import socket as _socket
PROBE_TIMEOUT = 8
_socket.setdefaulttimeout(PROBE_TIMEOUT)

LOC = re.compile(rb"<loc>\s*([^<\s]+)\s*</loc>", re.I)


def get(url):
    """Fetch respecting robots; returns bytes or None."""
    try:
        if not _c.robots_allows(url):
            return None
    except Exception:
        return None
    import urllib.request, urllib.error, time
    req = urllib.request.Request(url, headers={"User-Agent": _c.UA})
    try:
        with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT) as r:
            return r.read(5_000_000)
    except Exception:
        return None
    finally:
        time.sleep(_c.DELAY_SECONDS)


def sitemap_urls(origin):
    """Sitemap locations named by robots.txt, plus the conventional ones."""
    found = []
    raw = get(origin + "/robots.txt")
    if raw:
        for m in re.finditer(rb"(?im)^\s*sitemap:\s*(\S+)", raw):
            found.append(m.group(1).decode("utf-8", "replace").strip())
    found += [origin + p for p in
              ("/sitemap.xml", "/sitemap_index.xml", "/wp-sitemap.xml")]
    seen, out = set(), []
    for u in found:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def harvest_sitemap(origin, depth=0):
    """-> list of candidate page URLs matching our keywords."""
    hits = []
    for sm in sitemap_urls(origin):
        raw = get(sm)
        if not raw or b"<loc" not in raw:
            continue
        locs = [m.group(1).decode("utf-8", "replace") for m in LOC.finditer(raw)]
        # a sitemap index points at more sitemaps; follow one level
        nested = [u for u in locs if u.lower().endswith((".xml", ".xml.gz"))]
        pages = [u for u in locs if u not in nested]
        hits += [u for u in pages if KEYWORDS.search(u)]
        if depth == 0:
            for n in nested[:8]:
                raw2 = get(n)
                if not raw2:
                    continue
                hits += [m.group(1).decode("utf-8", "replace")
                         for m in LOC.finditer(raw2)
                         if KEYWORDS.search(m.group(1).decode("utf-8", "replace"))]
        if hits:
            break          # one working sitemap is enough per origin
    return hits


def probe_slugs(origin):
    out = []
    for s in SLUGS:
        url = origin + s
        raw = get(url)
        if raw and len(raw) > 2000 and re.search(rb"scholarship", raw, re.I):
            out.append(url)
    return out


def main(seed_paths, out_path, limit, do_slugs):
    origins = {}
    for p in seed_paths:
        for s in json.loads(Path(p).read_text())["seeds"]:
            u = urllib.parse.urlsplit(s["url"])
            if not u.netloc:
                continue
            origins.setdefault(f"{u.scheme}://{u.netloc}",
                               {"county": s.get("county", ""), "org": s.get("org", "")})

    origins = dict(list(origins.items())[:limit])
    print(f"{len(origins)} distinct origins to probe", file=sys.stderr)

    seeds, n_sm, n_sl = [], 0, 0
    for origin, meta in origins.items():
        found = harvest_sitemap(origin)
        n_sm += len(found)
        if do_slugs and not found:
            sl = probe_slugs(origin)
            n_sl += len(sl)
            found += sl
        for u in dict.fromkeys(found):
            seeds.append({"county": meta["county"],
                          "org": f"{meta['org']} — {urllib.parse.urlsplit(u).path[:48]}",
                          "url": u, "kind": "list",
                          "note": "discovered via sitemap or slug probe"})
        print(f"  {len(found):>3}  {origin}", file=sys.stderr, flush=True)

    # cap per origin so one huge sitemap cannot dominate the seed set
    by_origin, capped = {}, []
    for s in seeds:
        o = urllib.parse.urlsplit(s["url"]).netloc
        by_origin.setdefault(o, [])
        if len(by_origin[o]) < 12:
            by_origin[o].append(s)
            capped.append(s)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    json.dump({"_comment": [
        "URLs discovered from sitemaps and slug probes, not from search.",
        "Sitemaps are published so crawlers can enumerate a site -- the most",
        "permission-aligned discovery available, and previously unused here.",
        f"{n_sm} sitemap hits, {n_sl} slug hits, capped at 12 per origin."],
        "seeds": capped}, open(out_path, "w"), indent=2)

    print(f"\n{n_sm} from sitemaps, {n_sl} from slug probes", file=sys.stderr)
    print(f"{len(capped)} seeds written to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=35)
    ap.add_argument("--slugs", action="store_true")
    a = ap.parse_args()
    main(a.seeds, a.out, a.limit, a.slugs)
