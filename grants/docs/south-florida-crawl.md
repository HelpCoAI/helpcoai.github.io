# South Florida Crawl Results

**Date:** 2026-08-07 · 10 of 16 seeds harvested, against **6 of 14** for Tampa Bay.
**63% vs 43%** — and the difference is concentrated exactly where it matters.

---

## Miami-Dade is 5 for 5

| Source | Result |
|---|---|
| Coral Reef Senior High CAP Corner | ok — 11,776 chars |
| Coral Gables Community Foundation scholarships | ok — 14,459 chars |
| Coral Gables CF 2025 awards list | ok — 14,009 chars |
| The Miami Foundation scholarships | ok — 15,995 chars |
| Achieve Miami scholars portal | ok — 8,480 chars |

**The structural bet paid off.** Miami-Dade high schools run independent vanity domains
(`coralreefhighschool.net`) rather than `dadeschools.net` subdomains, so district robots policy
governs none of them. That was inference this morning; it is now measured.

Combined with the earlier finding that Miami-Dade — Florida's largest school district — has **no
public searchable local scholarship database at all**, this is the strongest region tested.

## Broward: 2 of 4 · Palm Beach: 2 of 5

| Source | Result |
|---|---|
| Community Foundation of Broward | ok — 3,253 chars |
| Broward Education Foundation | ok — 9,482 chars |
| George Snow Scholarship Fund (Broward + PB) | ok — 18,389 chars |
| Community Foundation for Palm Beach & Martin | ok — 12,468 chars |
| Palm Beach per-school bulletin on **Google Sites** | ok — 3,039 chars |
| Broward BRACE bulletin (`browardschools.com`) | **robots disallow** |
| Palm Beach district bulletin hub | **robots disallow** |
| Park Vista HS (`pvhs.palmbeachschools.org`) | **robots disallow** |
| Education Foundation of Palm Beach County | **robots disallow** |
| Viner Scholars | **robots disallow** |
| Broward League of Cities | timed out |

Two of the three structural predictions held, one failed:

- **Vanity domains escape district policy** — confirmed (Miami-Dade, 5/5).
- **Google Sites bulletins are crawlable** — confirmed. This is the template for per-school
  coverage in Palm Beach, where the district's own hub is closed.
- **School subdomains serve their own permissive robots.txt** — **false.** `pvhs.palmbeachschools.org`
  is disallowed just like the district root. Palm Beach schools on district infrastructure are
  closed; only the ones that migrated to Google Sites are reachable.

**The education-foundation picture is materially better than Tampa Bay**, where every single one was
blocked. Here, Broward Education Foundation, Community Foundation of Broward, Community Foundation
for Palm Beach & Martin, and George Snow all opened. Only Education Foundation PBC and Viner refused.

---

## The outcome-data thesis, confirmed on first contact

[Coral Gables Community Foundation's 2025 awards list](https://gablesfoundation.org/2025/05/05/scholarship-awards-list-2025/)
publishes, in plain HTML:

> **Total 2025 Awards: 207 Awards to 202 individuals, with total value of $3,250,000.**

…then breaks it down by named fund, with recipients and, for many, their high school:

- Coral Gables Community Foundation Four-Year Scholarship — 10 recipients
- Community Spirit Scholarship — 8 recipients, schools named (Miami High, ISPA, Coral Gables High)
- Coral Gables Culinary Arts Scholarship — 3 recipients
- …roughly 20 funds in total

That is **real `num_awards`** — the numerator of win probability — for ~20 programs, from one page,
requiring zero user cooperation. It is the channel described in the outcome-data discussion, working
on the first page we looked at.

**Privacy constraint, non-negotiable:** these pages name individual students, many of them minors.
Extract *counts* and *school names*. Never republish recipient names. The value is in
`num_awards` and the school distribution, not the identities.

---

## Bug found and fixed

The first South Florida run hung past 15 minutes and had to be cancelled. `RobotFileParser.read()`
calls `urlopen` with no timeout, so passing `timeout=` to our own requests never reached it — a host
that completed the TCP handshake and then went silent stalled the crawl indefinitely. Fixed with a
module-level `socket.setdefaulttimeout()`, which is the only thing that bounds it, plus a
25-minute job cap. Tampa Bay's 17 hosts had simply got lucky.

---

## Verdict

| | Tampa Bay | South Florida |
|---|---|---|
| Seeds harvested | 6/14 (43%) | **10/16 (63%)** |
| Best county | — | **Miami-Dade 5/5** |
| Education foundations reachable | 0 | 4 of 6 |
| Free regional aggregator competing | **Apply Tampa Bay (8 counties)** | none found |
| BMF candidates | 2,472 | **4,562** |
| Public award-count data found | none | **207 awards, ~20 funds, one page** |

**Pilot in Miami-Dade.** It is fully crawlable, has no aggregator, has the largest candidate pool,
and is the only county tested where a source publishes award counts outright.
