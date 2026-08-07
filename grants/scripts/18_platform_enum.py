#!/usr/bin/env python3
"""
Enumerate scholarship-platform tenants via certificate transparency logs.

Every scholarship platform we found is multi-tenant on a subdomain:

    phsc.academicworks.com          Pasco-Hernando State College Foundation
    broward.scholarships.ngwebsolutions.com
    <org>.awardspring.com / .communityforce.com / .foundant.com

Finding those tenants by searching is hopeless -- you have to already know the
org's name. But every TLS certificate ever issued is published to public
certificate transparency logs by design, and crt.sh exposes them. Querying
"%.academicworks.com" returns the tenant list directly.

This is public infrastructure metadata, not scraping: no origin server is touched
and nothing is bypassed. It is the difference between guessing which Florida
foundations use AwardSpring and simply reading the list.

Tenants are filtered to Florida-relevant names, then emitted as harvester seeds
pointed at each platform's conventional public opportunity listing.

Usage:
    python3 18_platform_enum.py --out data/district_seeds_platforms.json
"""

import argparse
import json
import re
import socket
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

socket.setdefaulttimeout(45)

UA = ("ScholarshipFinderBot/0.1 (+https://example.org/bot; research; "
      "contact: hello@example.org)")
DELAY = 3.0          # crt.sh is free and slow; be generous

# platform root -> path template for its PUBLIC opportunity listing
PLATFORMS = {
    "academicworks.com":   "/opportunities",
    "awardspring.com":     "/",
    "communityforce.com":  "/",
    "scholarships.ngwebsolutions.com": "/Scholarships/Search",
    "smapply.io":          "/",
    "submittable.com":     "/",
}

# A tenant is worth crawling if its subdomain names a Florida place or a
# plausible Florida institution. Deliberately broad -- a false positive costs
# one fetch, a false negative loses a whole foundation.
FL = re.compile(
    r"miami|dade|broward|palmbeach|palm-beach|pbc|hialeah|hollywood|"
    r"lauderdale|boca|delray|jupiter|wellington|coral|homestead|doral|"
    r"tampa|hillsborough|pinellas|pasco|manatee|sarasota|stpete|clearwater|"
    r"orlando|orange|osceola|seminole|volusia|brevard|jacksonville|duval|"
    r"tallahassee|leon|gainesville|alachua|ocala|marion|naples|collier|"
    r"lee|charlotte|polk|lakeland|pensacola|escambia|florida|\bfl\b|fla",
    re.I)

SKIP = re.compile(r"^\*|test|staging|demo|dev\.|sandbox|preview", re.I)


def crtsh(domain):
    """-> sorted set of subdomains seen in certificate transparency logs."""
    url = ("https://crt.sh/?" +
           urllib.parse.urlencode({"q": f"%.{domain}", "output": "json"}))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            rows = json.loads(r.read(60_000_000))
    except Exception as e:
        print(f"  ! crt.sh failed for {domain}: {e}", file=sys.stderr)
        return set()
    finally:
        time.sleep(DELAY)

    names = set()
    for row in rows:
        for n in (row.get("name_value") or "").split("\n"):
            n = n.strip().lower()
            if n.endswith("." + domain) and not SKIP.search(n):
                names.add(n)
    return names


def select(names, all_tenants, cap):
    """
    Place-name filtering alone loses acronym tenants. phsc.academicworks.com is
    Pasco-Hernando State College Foundation -- 220+ scholarships, a known target --
    and it matches no Florida keyword. So take every place-name match, then fill the
    remaining budget with unmatched tenants rather than discarding them. A false
    positive costs one fetch; a false negative loses a whole foundation.
    """
    if all_tenants:
        return sorted(names)
    matched = sorted(n for n in names if FL.search(n))
    rest = sorted(n for n in names if not FL.search(n))
    return matched + rest[:max(0, cap - len(matched))]


def main(out_path, all_tenants, cap):
    seeds, stats = [], {}
    for domain, path in PLATFORMS.items():
        names = crtsh(domain)
        keep = select(names, all_tenants, cap)
        n_fl = sum(1 for n in keep if FL.search(n))
        stats[domain] = (len(names), len(keep))
        print(f"  {domain:<36} {len(names):>5} tenants -> {len(keep):>4} kept "
              f"({n_fl} by place name, {len(keep) - n_fl} acronym/unnamed)",
              file=sys.stderr, flush=True)
        for host in keep:
            seeds.append({
                "county": "",
                "org": f"{host.split('.')[0]} ({domain.split('.')[0]})",
                "url": f"https://{host}{path}",
                "kind": "hub",
                "note": f"tenant of {domain}, found via certificate transparency",
            })

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    json.dump({"_comment": [
        "Scholarship-platform tenants found via certificate transparency logs.",
        "Every TLS certificate is published to public CT logs by design, so",
        "querying crt.sh for %.academicworks.com returns the tenant list outright.",
        "No origin server is touched to build this list and nothing is bypassed --",
        "it is public infrastructure metadata.",
        "Every place-name match is kept, plus a capped fill of acronym tenants --",
        "phsc.academicworks.com (Pasco-Hernando State College, 220+ scholarships)",
        "matches no Florida keyword, so name filtering alone loses real targets.",
        "Tenant counts per platform: "
        + ", ".join(f"{d}: {v[1]}/{v[0]}" for d, v in stats.items())],
        "seeds": seeds}, open(out_path, "w"), indent=2)

    print(f"\n{len(seeds)} platform seeds -> {out_path}", file=sys.stderr)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/district_seeds_platforms.json")
    ap.add_argument("--all", action="store_true",
                    help="keep every tenant, not just Florida-relevant ones")
    ap.add_argument("--cap", type=int, default=120,
                    help="per-platform ceiling once place-name matches are taken")
    a = ap.parse_args()
    main(a.out, a.all, a.cap)
