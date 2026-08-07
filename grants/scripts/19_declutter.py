#!/usr/bin/env python3
"""
Strip navigation chrome from harvested pages, without an LLM and without
per-site rules.

Why this exists: a harvested page is mostly menu. Cardinal Gibbons' alumni-awards
page is 7,600 characters, of which roughly 6,000 are the site's global nav
repeated twice ("About Gibbons Mission, Vision & Accolades Directory Map &
Directions Employment Admissions ..."). Every downstream step pays for that
noise -- a regex for award blocks matches menu items, a dollar-amount count
picks up tuition figures in the footer, and an LLM pass would burn 80% of its
tokens reading a menu it must then ignore.

The trick is that chrome is, by definition, the text that repeats. Two passes:

  HOST     an 8-gram appearing on >=60% of a host's pages (min 2 pages) is that
           site's furniture. This is the strong signal and it handles 58% of
           pages; it needs no knowledge of what a menu looks like.

  CORPUS   an 8-gram appearing on >=8 unrelated hosts is generic web furniture
           ("Skip to Main Content", "opens in new window/tab", cookie banners).
           Unrelated organisations do not share prose by accident.

The corpus pass is the dangerous one, because a genuinely popular award also
appears across many hosts -- Bright Futures shows up on nine counselor bulletins,
and that breadth is a signal we rank on, not noise to delete. So corpus stripping
is refused for any window carrying award signal: a dollar amount, a digit, or a
word from KEEP. "Facebook Twitter Instagram" is dropped; "Bright Futures
Scholarship" is not.

Nothing is deleted destructively -- cleaned text is written alongside the
original, and the reduction per page is reported so the pass can be audited.

Usage:
    python3 19_declutter.py --pages 'data/district_pages_*' --out data/clean
    python3 19_declutter.py --pages 'data/district_pages_*' --report-only
"""

import argparse
import glob
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

N = 8                    # shingle width, in words
HOST_FRAC = 0.60         # appear on this share of a host's pages -> chrome
HOST_MIN_PAGES = 2       # safe now that exact duplicates are collapsed first
CORPUS_HOSTS = 8         # appear on this many unrelated hosts -> generic chrome
MIN_RUN = 12             # never delete a run shorter than this many words
FLOOR = 0.15             # if cleaning would keep less than this, chrome detection
                         # has misfired for that host -- keep the original

# A window containing any of these is never stripped by the CORPUS pass, however
# often it repeats. These are the words that make a sentence worth reading.
KEEP = re.compile(
    r"scholarship|award|grant|bursary|fellowship|stipend|deadline|eligib|"
    r"applicant|apply|gpa|tuition|senior|graduat|recipient|nominat|essay|"
    r"transcript|fafsa|renewab|amount|criteri|requirement",
    re.I)

HEADER = re.compile(r"\A(URL: .*?\n(?:.*?\n)*?-{20,}\n)", re.M)


def protected(shingle: str) -> bool:
    """
    True for any window that reads like award content rather than furniture.

    Applied to BOTH passes, and the host pass needs it more than the corpus one.
    A school's counselor bulletins are re-posted monthly with much of the same
    list, so an award carried in the August, September and January bulletins
    appears on >60% of that host's pages and gets classified as chrome. Those
    bulletins are the single most valuable thing we harvested; deleting an award
    from them is the one error this script must not make. Guarding cost 21
    dollar-amounts before, and zero after.

    Menus do not quote dollar figures or say "eligibility", so the cost of the
    guard is some retained nav on pages whose menu happens to read "Scholarships"
    -- noise a later pass can ignore, unlike data it never receives.
    """
    return bool(KEEP.search(shingle)) or "$" in shingle or any(
        ch.isdigit() for ch in shingle)


def words(text):
    return text.split()


def shingles(ws, n=N):
    for i in range(len(ws) - n + 1):
        yield i, " ".join(ws[i:i + n]).lower()


def host_of(header):
    m = re.search(r"URL: https?://([^/\s]+)", header or "")
    return m.group(1).lower().removeprefix("www.") if m else "?"


def split_page(raw):
    """-> (header, body). The header carries URL/ORG/COUNTY and is preserved."""
    m = HEADER.match(raw)
    return (m.group(1), raw[m.end():]) if m else ("", raw)


def load(page_paths):
    """
    Load pages, collapsing exact body duplicates within a host.

    The crawler follows links, so a foundation's /scholarships page and the
    linked-doc it points at frequently come back byte-identical. Left in, they
    poison chrome detection catastrophically: with two identical pages every
    shingle appears on 100% of the host, so the entire page is classified as
    furniture and cleaned to nothing. Mas Family and four Rotary clubs were each
    stripped to 0% before this.
    """
    pages, seen = [], {}
    for p in page_paths:
        raw = p.read_text(encoding="utf-8", errors="replace")
        header, body = split_page(raw)
        host = host_of(header)
        key = (host, " ".join(body.split()))
        if key in seen:
            seen[key]["dupes"].append(p)
            continue
        pg = {"path": p, "header": header, "body": body,
              "host": host, "words": words(body), "dupes": []}
        seen[key] = pg
        pages.append(pg)
    return pages


def build_chrome(pages):
    """-> (host_chrome: {host: set(shingle)}, corpus_chrome: set(shingle))"""
    by_host = defaultdict(list)
    for pg in pages:
        by_host[pg["host"]].append(pg)

    host_chrome, corpus_hosts = {}, defaultdict(set)
    for host, group in by_host.items():
        seen_in = Counter()
        for pg in group:
            for sh in {s for _, s in shingles(pg["words"])}:
                seen_in[sh] += 1
                corpus_hosts[sh].add(host)
        if len(group) >= HOST_MIN_PAGES:
            need = max(2, round(HOST_FRAC * len(group)))
            host_chrome[host] = {s for s, c in seen_in.items() if c >= need}

    corpus_chrome = set()
    for sh, hosts in corpus_hosts.items():
        if len(hosts) >= CORPUS_HOSTS and not protected(sh):
            corpus_chrome.add(sh)
    return host_chrome, corpus_chrome


def clean_page(pg, host_chrome, corpus_chrome):
    """-> (cleaned_body, n_words_dropped)"""
    ws = pg["words"]
    if len(ws) < N:
        return pg["body"], 0
    chrome = host_chrome.get(pg["host"], set())
    drop = [False] * len(ws)
    for i, sh in shingles(ws):
        if sh not in chrome and sh not in corpus_chrome:
            continue
        if protected(sh):
            continue
        for j in range(i, i + N):
            drop[j] = True

    # Only remove long runs. A stray flagged phrase inside real prose is far
    # more likely to be a coincidence than a menu, and cutting it mid-sentence
    # corrupts the eligibility text that everything else is derived from.
    out, i, dropped = [], 0, 0
    while i < len(ws):
        if not drop[i]:
            out.append(ws[i]); i += 1; continue
        j = i
        while j < len(ws) and drop[j]:
            j += 1
        if j - i >= MIN_RUN:
            dropped += j - i
        else:
            out.extend(ws[i:j])
        i = j

    # A page cleaned to almost nothing means chrome detection misfired for this
    # host, not that the page was empty. Prefer noisy text over no text.
    if (len(ws) - dropped) / len(ws) < FLOOR:
        return pg["body"], 0
    return " ".join(out), dropped


def main(patterns, out_dir, report_only, limit_report):
    page_paths = []
    for pat in patterns:
        for d in sorted(glob.glob(pat)):
            page_paths += [p for p in sorted(Path(d).glob("*.txt"))
                           if not p.name.startswith("_")]
    if not page_paths:
        sys.exit(f"no pages matched {patterns}")

    pages = load(page_paths)
    host_chrome, corpus_chrome = build_chrome(pages)
    print(f"{len(pages)} pages / {len({p['host'] for p in pages})} hosts", file=sys.stderr)
    print(f"chrome shingles: {sum(len(v) for v in host_chrome.values())} host-level "
          f"across {len(host_chrome)} hosts, {len(corpus_chrome)} corpus-level",
          file=sys.stderr)

    results, kept_total, orig_total = [], 0, 0
    for pg in pages:
        body, dropped = clean_page(pg, host_chrome, corpus_chrome)
        orig = len(pg["words"])
        orig_total += orig
        kept_total += orig - dropped
        results.append((pg, body, orig, dropped))
        if not report_only:
            dest = Path(out_dir) / pg["path"].parent.name
            dest.mkdir(parents=True, exist_ok=True)
            (dest / pg["path"].name).write_text(pg["header"] + body + "\n",
                                                encoding="utf-8")

    results.sort(key=lambda r: -(r[3] / max(1, r[2])))
    print(f"\nkept {kept_total:,} of {orig_total:,} words "
          f"({kept_total / max(1, orig_total):.0%}); "
          f"dropped {orig_total - kept_total:,} words of chrome\n", file=sys.stderr)
    print(f"{'page':<56} {'words':>7} {'kept':>6}", file=sys.stderr)
    for pg, _b, orig, dropped in results[:limit_report]:
        print(f"{pg['path'].name[:55]:<56} {orig:>7} "
              f"{(orig - dropped) / max(1, orig):>5.0%}", file=sys.stderr)
    if not report_only:
        print(f"\ncleaned pages -> {out_dir}", file=sys.stderr)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", nargs="+", default=["data/district_pages_*"])
    ap.add_argument("--out", default="data/clean")
    ap.add_argument("--report-only", action="store_true")
    ap.add_argument("--limit-report", type=int, default=15)
    a = ap.parse_args()
    main(a.pages, a.out, a.report_only, a.limit_report)
