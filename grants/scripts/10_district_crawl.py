#!/usr/bin/env python3
"""
District / education-foundation crawler.

Why this exists: the n=15 verification sample showed the BMF finds *organizations*
(40% of which turn out to run nothing a student can apply to), while school-district
and education-foundation pages enumerate *awards* -- already filtered for open,
local and current. This is the higher-yield channel and should run first.

Two stages, deliberately separate so a fetch failure never costs an LLM call and a
prompt change never costs a refetch:

    fetch    seeds -> cache/<sha>.html   (network, polite, robots-aware, resumable)
    extract  cache/*.html -> awards.csv  (LLM, batched, idempotent)

Usage:
    python3 10_district_crawl.py fetch    [--seeds data/district_seeds.json]
    python3 10_district_crawl.py extract  [--out data/07_district_awards.csv]
    python3 10_district_crawl.py status

Requires real egress. The build sandbox's proxy denies CONNECT to arbitrary hosts,
so `fetch` will report every seed as blocked there -- run it somewhere with network.
"""

import argparse
import hashlib
import json
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "cache" / "district"
SEEDS = ROOT / "data" / "district_seeds.json"

UA = ("ScholarshipFinderBot/0.1 (+https://example.org/bot; contact: hello@example.org) "
      "python-urllib")
DELAY_SECONDS = 2.0          # per-host politeness delay
TIMEOUT = 30

# RobotFileParser.read() calls urlopen with NO timeout, so a host that accepts the
# connection and then never responds hangs the whole crawl forever. A global socket
# default is the only way to bound it -- passing timeout= to our own urlopen calls
# does not reach inside robotparser.
socket.setdefaulttimeout(TIMEOUT)


# ------------------------------------------------------------------ fetch

def cache_path(url: str) -> Path:
    return CACHE / (hashlib.sha256(url.encode()).hexdigest()[:20] + ".html")


def meta_path(url: str) -> Path:
    return cache_path(url).with_suffix(".json")


IGNORE_ROBOTS = False       # set by --ignore-robots

_robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}


def robots_allows(url: str) -> bool:
    """
    Respect robots.txt by default.

    --ignore-robots disables this gate. It bypasses the DIRECTIVE only: the
    User-Agent still identifies the crawler honestly and the per-host politeness
    delay is unchanged, so this is not detection evasion and will not get past a
    WAF. Note also that Python's robotparser reports disallow-all when robots.txt
    itself returns 401/403, so a share of "robots" failures were never a stated
    preference at all -- just bot detection, which this flag does not defeat.
    """
    if IGNORE_ROBOTS:
        return True
    parts = urllib.parse.urlsplit(url)
    origin = f"{parts.scheme}://{parts.netloc}"
    if origin not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(origin + "/robots.txt")
        try:
            rp.read()
        except Exception:
            rp = None            # no robots.txt reachable -> default allow
        _robots[origin] = rp
        time.sleep(DELAY_SECONDS)
    rp = _robots[origin]
    return True if rp is None else rp.can_fetch(UA, url)


def decompress(body: bytes, encoding: str) -> bytes:
    """
    Undo Content-Encoding before anything tries to read the bytes as text.

    urllib does not do this. Most hosts only compress when asked, and we never
    send Accept-Encoding, so this went unnoticed for 400 pages. schema.org
    compresses regardless, and both schema.org harvests landed in the repo as
    73% non-printable bytes: a file that looks harvested, is committed, is
    greppable, and contains nothing. Worse than a failed fetch, which at least
    reports itself in the log.

    Unknown or absent encodings pass through untouched, and a body that fails to
    decode is returned as-is so a mislabelled header cannot lose the page.
    """
    enc = (encoding or "").lower().strip()
    try:
        if enc == "gzip":
            import gzip
            return gzip.decompress(body)
        if enc == "deflate":
            import zlib
            try:
                return zlib.decompress(body)
            except zlib.error:
                return zlib.decompress(body, -zlib.MAX_WBITS)   # raw deflate
        if enc == "br":
            import brotli                                       # optional
            return brotli.decompress(body)
    except Exception:
        return body
    return body


def fetch_one(url: str) -> tuple[str, str]:
    """-> (status, detail). status in {ok, cached, blocked, robots, error}"""
    if cache_path(url).exists():
        return "cached", f"{cache_path(url).stat().st_size:,} bytes"

    try:
        if not robots_allows(url):
            return "robots", "disallowed by robots.txt"
    except Exception as e:
        return "error", f"robots check failed: {e}"

    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read()
            ctype = r.headers.get("Content-Type", "")
            body = decompress(body, r.headers.get("Content-Encoding", ""))
    except urllib.error.HTTPError as e:
        return "error", f"HTTP {e.code}"
    except urllib.error.URLError as e:
        reason = str(e.reason)
        if "403" in reason or "CONNECT" in reason or "tunnel" in reason.lower():
            return "blocked", "egress proxy denied CONNECT"
        return "error", reason
    except Exception as e:
        return "error", str(e)
    finally:
        time.sleep(DELAY_SECONDS)

    CACHE.mkdir(parents=True, exist_ok=True)
    cache_path(url).write_bytes(body)
    meta_path(url).write_text(json.dumps({
        "url": url, "content_type": ctype, "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
    }, indent=2))
    return "ok", f"{len(body):,} bytes"


def cmd_fetch(seeds_path: Path):
    seeds = json.loads(seeds_path.read_text())["seeds"]
    tally: dict[str, int] = {}
    print(f"Fetching {len(seeds)} seeds (>= {DELAY_SECONDS}s between requests)\n")
    for s in seeds:
        status, detail = fetch_one(s["url"])
        tally[status] = tally.get(status, 0) + 1
        mark = {"ok": "  ok", "cached": "cach", "blocked": "BLOK",
                "robots": "ROBO", "error": " ERR"}[status]
        print(f"[{mark}] {s['county']:<18} {s['org'][:38]:<38} {detail}")

    print("\n" + "  ".join(f"{k}={v}" for k, v in sorted(tally.items())))
    if tally.get("blocked"):
        print("\nBlocked seeds mean this machine has no direct egress. The proxy denies")
        print("CONNECT to arbitrary hosts by policy -- run this where network is open")
        print("(your laptop, or a GitHub Actions runner) rather than working around it.")


# ------------------------------------------------------------------ extract

EXTRACT_PROMPT = """\
You are extracting scholarship records from a school district or education
foundation page. Return STRICT JSON: a list of objects, one per NAMED award.

For each award set: name, sponsor, amount_min, amount_max, deadline (ISO date or
null), eligibility_raw (verbatim), counties, high_schools, gpa_min, majors,
apply_url, platform (CommunityForce/AwardSpring/Scholarship America/Google Form/
paper/email/other/null), beneficiary_scope (open|members_only|employees_only|
nomination_only), essay_required (bool or null).

Rules:
- Use null for anything not stated. NEVER infer an amount or a deadline.
- Skip national awards (Coca-Cola, Gates, Bright Futures) -- local only.
- If one application covers many awards, emit each named award separately and give
  them all the same apply_url.
- Return [] if the page lists no named awards.
"""

TAG_STRIP = re.compile(rb"<(script|style)[^>]*>.*?</\1>", re.S | re.I)
TAGS = re.compile(rb"<[^>]+>")


class _LinkGrab(HTMLParser):
    """Collect (href, anchor text) pairs. Anchor text is what makes a link scoreable:
    the useful ones say 'Download CAP Scholarship Bulletin', not 'click here'."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self._href = None
        self._text = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href:
            self.links.append((self._href, " ".join(self._text).split() and
                               " ".join(" ".join(self._text).split())[:120] or ""))
            self._href = None


# What we are looking for
WANT = re.compile(r"scholarship|bursary|award|financial[-_ ]?aid|cap[-_ ]?corner", re.I)
# What looks like it but is not. "Curriculum Bulletin" is on nearly every MDCPS page.
AVOID = re.compile(
    r"curriculum|code of student conduct|handbook|calendar|lunch|menu|athletics|"
    r"immuniz|volunteer|climate survey|reading plan|dress code|transcript request|"
    r"facebook|twitter|instagram|youtube|login|privacy|accessibility", re.I)


def score_link(href: str, text: str) -> int:
    blob = f"{href} {text}"
    if AVOID.search(blob):
        return 0
    if not WANT.search(blob):
        return 0
    pts = 1
    if re.search(r"bulletin|list|opportunit", blob, re.I):
        pts += 3
    if href.lower().endswith((".pdf", ".doc", ".docx", ".xlsx")):
        pts += 3
    if re.search(r"scholarship", href, re.I):
        pts += 2
    return pts


def candidate_links(raw: bytes, base_url: str, limit: int = 3):
    """Rank the links on a page and return the most likely award documents."""
    if raw[:5] == b"%PDF-":
        return []
    try:
        p = _LinkGrab()
        p.feed(raw.decode("utf-8", errors="replace"))
    except Exception:
        return []

    seen, scored = set(), []
    for href, text in p.links:
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        full = urllib.parse.urljoin(base_url, href)
        if not full.startswith("http") or full in seen:
            continue
        seen.add(full)
        s = score_link(full, text)
        if s:
            scored.append((s, full, text))

    scored.sort(key=lambda t: -t[0])
    return [(u, t) for _, u, t in scored[:limit]]


def pdf_to_text(raw: bytes) -> str:
    """
    Counselor bulletins are frequently PDFs (SouthTech publishes a numbered series),
    and they are among the densest sources of named local awards. Without this the
    HTML path decodes a PDF to binary garbage and the page silently reads as 'thin'.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    import io
    try:
        reader = PdfReader(io.BytesIO(raw))
    except Exception:
        return ""

    # pypdf's default mode reconstructs text from glyph draw order and routinely
    # drops inter-word spaces, yielding "Raise.meMicro-Scholarship" and
    # "ThisHighSchoolScholarshipProgramisopento...". Layout mode uses glyph
    # positions instead and preserves the gaps, which matters because these
    # bulletins are TABLES -- name, award, eligibility, deadline -- and a run-on
    # column is unparseable. Fall back if the installed pypdf is too old.
    for kwargs in ({"extraction_mode": "layout"}, {}):
        try:
            out = "\n".join((p.extract_text(**kwargs) or "") for p in reader.pages)
        except TypeError:
            continue
        except Exception:
            return ""
        if out.strip():
            return out
    return ""


def to_text(raw: bytes, limit: int = 60_000) -> str:
    if raw[:5] == b"%PDF-":
        text = pdf_to_text(raw)
    else:
        body = TAGS.sub(b" ", TAG_STRIP.sub(b" ", raw))
        text = body.decode("utf-8", errors="replace")
    text = re.sub(r"&nbsp;?", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text[:limit]


def cmd_extract(seeds_path: Path, out_path: Path):
    try:
        from anthropic import Anthropic
    except ImportError:
        sys.exit("pip install anthropic")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set")

    seeds = json.loads(seeds_path.read_text())["seeds"]
    client = Anthropic()
    rows, skipped = [], 0

    for s in seeds:
        cp = cache_path(s["url"])
        if not cp.exists():
            skipped += 1
            continue
        text = to_text(cp.read_bytes())
        if len(text) < 400:
            skipped += 1
            continue

        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=8_000,
            system=EXTRACT_PROMPT,
            messages=[{"role": "user",
                       "content": f"Source: {s['url']}\nCounty: {s['county']}\n\n{text}"}],
        )
        blob = msg.content[0].text.strip()
        blob = re.sub(r"^```(?:json)?|```$", "", blob, flags=re.M).strip()
        try:
            awards = json.loads(blob)
        except json.JSONDecodeError:
            print(f"  ! unparseable JSON from {s['org']}")
            continue

        for a in awards:
            a["source_url"] = s["url"]
            a["source_org"] = s["org"]
            a["source_county"] = s["county"]
            rows.append(a)
        print(f"  {len(awards):>3} awards  {s['org']}")

    if not rows:
        sys.exit(f"No awards extracted ({skipped} seeds had no cached page — run `fetch` first)")

    import csv
    cols = sorted({k for r in rows for k in r})
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: (json.dumps(v) if isinstance(v, (list, dict)) else v)
                        for k, v in r.items()})
    print(f"\n{len(rows)} awards -> {out_path}  ({skipped} seeds skipped)")


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:60]


def _write_page(out_dir: Path, county, org, kind, url, text) -> str:
    # Join only the non-empty parts. Seeds with no county (the CT-enumerated
    # platform tenants and the BMF orgs) used to produce names starting with
    # "--", which every shell tool parses as an option: `grep pat --org.txt`
    # dies with "unrecognized option" and a naive file count returns zero.
    parts = [p for p in (slugify(county), slugify(org)) if p]
    name = ("--".join(parts) or "page") + ".txt"
    (out_dir / name).write_text(
        f"URL: {url}\nORG: {org}\nCOUNTY: {county}\nKIND: {kind}\n"
        f"{'-' * 70}\n{text}\n", encoding="utf-8")
    return name


def cmd_harvest(seeds_path: Path, out_dir: Path, follow: int = 0):
    """
    fetch + flatten to plain text, committed to the repo.

    Splitting this out of `extract` means the pages can be harvested by a machine
    that HAS network (a GitHub runner) and read by one that does not, with no API
    key anywhere in the loop.
    """
    seeds = json.loads(seeds_path.read_text())["seeds"]
    out_dir.mkdir(parents=True, exist_ok=True)
    ok = 0
    log = []

    for s in seeds:
        status, detail = fetch_one(s["url"])
        if status not in {"ok", "cached"}:
            line = f"[{status:>7}] {s['org'][:42]:<42} {detail}  {s['url']}"
            log.append(line)
            print(line)
            continue

        text = to_text(cache_path(s["url"]).read_bytes())
        if len(text) < 300:
            line = f"[   thin] {s['org'][:42]:<42} {len(text)} chars  {s['url']}"
            log.append(line)
            print(line)
            continue

        name = _write_page(out_dir, s["county"], s["org"], s["kind"], s["url"], text)
        ok += 1
        line = f"[     ok] {s['org'][:42]:<42} {len(text):,} chars -> {name}"
        log.append(line)
        print(line)

        # Second hop. CAP landing pages almost never carry the awards -- they link
        # to a bulletin. Only 4 of 27 Miami-Dade pages held a single dollar amount,
        # while 5 said "Download CAP Scholarship Bulletin". The awards are one click
        # further in, so follow the most promising links from each page.
        if follow:
            for url2, anchor in candidate_links(cache_path(s["url"]).read_bytes(),
                                                s["url"], follow):
                st2, det2 = fetch_one(url2)
                if st2 not in {"ok", "cached"}:
                    log.append(f"[{st2:>7}] .. {(anchor or url2)[:39]:<39} {det2}")
                    continue
                text2 = to_text(cache_path(url2).read_bytes())
                if len(text2) < 300:
                    log.append(f"[   thin] .. {(anchor or url2)[:39]:<39} {len(text2)} chars")
                    continue
                label = f"{s['org']} - {anchor or 'linked doc'}"
                n2 = _write_page(out_dir, s["county"], label, "linked", url2, text2)
                ok += 1
                l2 = f"[     ok] .. {(anchor or url2)[:39]:<39} {len(text2):,} chars -> {n2}"
                log.append(l2)
                print(l2)

    # Committed so failures are diagnosable from anywhere, without runner logs
    (out_dir / "_harvest_log.txt").write_text(
        f"{ok}/{len(seeds)} pages harvested\n" + "-" * 78 + "\n"
        + "\n".join(log) + "\n", encoding="utf-8")
    print(f"\n{ok}/{len(seeds)} pages harvested into {out_dir}")


def cmd_status(seeds_path: Path):
    seeds = json.loads(seeds_path.read_text())["seeds"]
    have = sum(1 for s in seeds if cache_path(s["url"]).exists())
    print(f"Seeds: {len(seeds)}   cached: {have}   missing: {len(seeds) - have}")
    for s in seeds:
        print(f"  [{'x' if cache_path(s['url']).exists() else ' '}] "
              f"{s['kind']:<5} {s['county']:<18} {s['org']}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["fetch", "harvest", "extract", "status"])
    p.add_argument("--seeds", type=Path, default=SEEDS)
    p.add_argument("--out", type=Path, default=ROOT / "data" / "07_district_awards.csv")
    p.add_argument("--pages", type=Path, default=ROOT / "data" / "district_pages")
    p.add_argument("--follow", type=int, default=0,
                   help="also fetch up to N ranked links from each harvested page")
    p.add_argument("--ignore-robots", action="store_true",
                   help="skip the robots.txt gate. User-Agent stays honest and the "
                        "politeness delay is unchanged; this bypasses the directive, "
                        "not the identification, and will not get past a WAF.")
    a = p.parse_args()
    if a.ignore_robots:
        globals()["IGNORE_ROBOTS"] = True
        print("robots.txt gate DISABLED for this run", file=sys.stderr)
    {"fetch": lambda: cmd_fetch(a.seeds),
     "harvest": lambda: cmd_harvest(a.seeds, a.pages, a.follow),
     "extract": lambda: cmd_extract(a.seeds, a.out),
     "status": lambda: cmd_status(a.seeds)}[a.command]()
