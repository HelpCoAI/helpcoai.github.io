# The District Channel — and what it means for the product

**Date:** 2026-08-07 · Follows the n=15 verification sample (`data/06_tp_rate_sample.md`).

---

## What was found

Every county in the pilot region has a **single-application hub** run by its education foundation or
community foundation. Sizes, from published sources:

| County | Hub | Named awards | One application? | Notes |
|---|---|---|---|---|
| Pinellas | [Pinellas Education Foundation](https://pinellaseducation.org/students/) | **120+** | Yes | **$700,000/yr**, awards $500–$20,000 |
| Hillsborough | [Hillsborough Education Foundation](https://educationfoundation.com/resource/senior-scholarships/) | "**hundreds**" | Yes | $500–$20,000; opens Oct 1, closes ~Jan 31 |
| Sarasota | [Education Foundation of Sarasota County](https://edfoundationsrq.org/scholarships/) | — | Yes | Self-described "Scholarships Database" |
| Sarasota | [Community Foundation of Sarasota County](https://www.cfsarasota.org/students) | portfolio | Yes | "one application every year" for the whole College Fund portfolio |
| Manatee | [Manatee Education Foundation](https://mefinfo.org/the-scholarship-source/) | — | Likely | "The Scholarship Source" |
| Pasco | [Pasco Education Foundation](https://www.pascoeducationfoundation.org/) + per-school counselor lists | — | Partly | Per-school PDF opportunity lists |

Plus one statewide meta-source: the [Florida College Access Network's local scholarship
resources](https://floridacollegeaccess.org/initiatives/local-scholarship-resources/) — **a list of
these lists, by county, for all 67 counties.** That single URL is the cheapest path from a 5-county
pilot to statewide coverage.

Seeds are in `data/district_seeds.json`; the crawler is `scripts/10_district_crawl.py`.

---

## Why this channel should run first

| | BMF channel | District channel |
|---|---|---|
| Unit of discovery | Organizations | **Awards** |
| Pilot volume | 2,472 candidates → ~989 real orgs | ~14 URLs → est. **400–600 named awards** |
| Yield | 40% (measured) | Near 100% — the lists exist to be applied to |
| Cost to extract | ~$40 + heavy human review | **~$0.20** |
| Amount published | 47% (measured on 47 awards) | High — hubs state ranges |
| Deadline published | 45% (measured) | High — hubs run on a calendar |
| Beneficiary scope | Must be inferred | Stated |

Roughly **200x cheaper per award**, and it fixes the two worst gaps in the earlier 47-award sample
(amount 47%, deadline 45% — the fields orgs simply don't publish on their own sites, but that
foundations must publish to run an application cycle).

**Revised order:** district hubs → the FCAN meta-list → per-high-school counselor pages → BMF. The
BMF keeps two jobs it is uniquely good at: enriching sponsors with 990 financials (the
Instrumentl-style sponsor pages), and finding the independent awards that appear on no hub.

---

## The uncomfortable part: these hubs are also a competitor

The pitch has been "one profile, many applications." **Pinellas Education Foundation already does
that** — 120+ awards, one form, free, for any Pinellas senior. So does Hillsborough. So does the
Community Foundation of Sarasota County. Within a single county, a meaningful slice of the product's
value proposition is already solved, for free, by an incumbent with the school district's
endorsement.

That is not fatal, but it must change how the product is positioned. What genuinely remains:

1. **Discovery.** Students don't know these hubs exist. That is an SEO problem, and SEO is the plan's
   only viable acquisition channel anyway. Pointing a student to their county hub is real value
   delivered on the first visit.
2. **The awards no hub carries.** Every confirmed pass in the n=15 sample applies *directly*, not
   through a hub — Rotary Hudson, Trinity Rotary, Kiwanis St. Petersburg, Ye Mystic Krewe. The hubs
   cover their own portfolios only.
3. **Crossing hub boundaries.** A student near a county line, or applying to a hub plus four
   independent awards, still faces five applications. Autofill and one master profile matter exactly
   there.
4. **Odds and expected value.** No hub ranks by win probability. Rotary Hudson's 19-applicants → 5
   awards is not a number any foundation publishes in a comparable form.
5. **Deadlines across sources.** Hub cycles (Oct 1 → Jan 31) plus independent deadlines (Mar 25, Apr 1,
   Mar 1) is a calendar problem nobody solves for the student.

**Implication for the free/paid split.** The free tier should show the county hub prominently and
without a paywall — it is the single most useful thing a student can be told, it costs nothing, and
paywalling public information is the criticism this category attracts. The paid tier is the
cross-source layer: the independent awards, the ranking, the tracker, the unified deadline calendar,
and eventually autofill. That is a cleaner and more defensible line than "top 3 free."

**Implication for partnerships.** These foundations are potential distribution partners rather than
pure rivals — they want their awards claimed, and low application volume is a real problem for them.
That is a warm-intro path that does not require cold calling, though it is a Phase 2 concern.

---

## Status

The crawler is written and its `status`/`fetch`/`extract` stages run, but **no page has been
fetched**: this sandbox's egress proxy denies CONNECT to arbitrary hosts, and `fetch` correctly
reports all 14 seeds as blocked rather than failing quietly. Run it where network is open:

```bash
python3 scripts/10_district_crawl.py fetch      # polite, robots-aware, resumable
python3 scripts/10_district_crawl.py extract    # needs ANTHROPIC_API_KEY
```

Everything above about hub sizes comes from search results, not from fetched pages — the counts are
as published by the foundations, and should be treated as unconfirmed until the crawl runs.
