# State of the Data

**Date:** 2026-08-07 · Consolidates every collection run. Supersedes the yield figures in
`district-channel.md`, `no-human-review.md` and `two-channels.md`.

---

## What exists now

| Channel | Sources | Pages with award data | Awards |
|---|---|---|---|
| South Florida foundations | 16 seeded → 10 harvested | 6 | **57 extracted** |
| Miami-Dade counselor bulletins | 52 seeded → 65 harvested (38 via link-following) | 21 of 61 | **142 distinct names** |
| BMF organizations | 145 seeded → 67 harvested | **13 of 65** | ~15–25, all hyperlocal |
| Palm Beach / Broward schools | 22 seeded → 8 harvested | 5 | small |
| Tampa Bay (superseded) | 17 seeded → 9 harvested | 6 | folded into the 57 |

**Realistic distinct total after dedupe and after stripping national programmes: roughly 150–200
for one metro.** Not the 400–600 projected twice this morning.

## The two channels are confirmed complementary

Counselor bulletins, 222KB of text:

| Rotary | Kiwanis | Elks | Chamber of Commerce |
|---|---|---|---|
| 0 | 0 | 0 | 0 |

BMF organization crawl, same region: **48 of the 145 seeds are service clubs.** The channels have
near-zero overlap by construction.

| | Counselor bulletins | BMF organizations |
|---|---|---|
| Volume | High, 142 from one metro | Low, 13 usable pages of 65 |
| Award type | Regional, state, national | **Hyperlocal** |
| Odds | Poor (thousands apply) | **Best** (Rotary Hudson: 19 applicants, 5 awards) |
| Robots / WAF exposure | High | Moderate |
| Determinism | Poor | Discovery is deterministic; the crawl is not |

**Bulletins are the volume. The BMF is the differentiation.** Dropping either halves the product.

## What the BMF channel actually produced

Best examples, none of which appear on any counselor bulletin or national database:

- **Gina Rose Montalto Memorial Foundation**, $5,000 for a student in the Arts, and $2,500 annually
  to *one Girl Scout who achieves the Gold Award from the Southeast Florida service unit*. Three
  separate pages harvested.
- **Wellington Community Foundation**, village-level, with a deadline.
- **I Think Community Foundation**, **Miramar-Pembroke Pines Regional Chamber of Commerce**,
  **Common Knowledge Scholarship Foundation**.

**A caution on measuring this channel:** counting dollar amounts overcounts. Rotary club pages
quote grants they make *to organizations* and global Rotary statistics ($291M invested) that have
nothing to do with students. Filtering for a dollar amount within ~120 characters of
scholarship/student/senior language cut 16 pages to **13 genuinely student-facing**.

## Enrichment is solved

The BMF channel was blocked for weeks on a missing URL, it names organizations but not where to
read about them, and finding 626 homepages looked like it needed a paid search API.

It did not. The GivingTuesday 990 index CSV carries a `Website` column already extracted from each
filing's XML. One streaming pass over 3.2GB matched 4,562 candidates against **7,344,896 filings**:

- 776 had a website → **670 after normalization** → **150 in priority A**
- **17% match rate**, well under the 30–50% guessed. Small clubs file on paper or leave it blank.

Normalization was not cosmetic. Filers type the field by hand, so it arrives as `WWW.EXAMPLE.ORG`
and `HTTPS://WWW.Q81.ORG/`; a lowercase `startswith("https://")` check missed uppercase schemes and
produced `https://HTTPS://WWW.Q81.ORG/`, which fetches nothing and looks like a dead site rather
than a mangled URL.

## Collection is partial and non-deterministic, plan for it

Across every run: **~35 robots blocks, plus WAF challenges, JS-only pages, dead domains and DNS
failures.** Sites that returned 14KB on the first pass returned 1 byte on the fourth after we
crawled them repeatedly. The harvester now skips already-harvested sets by default for exactly this
reason.

Any plan assuming "crawl N sources, get N sources" is wrong. Assume **40–60%** and design the
indexability rules around it.

## Accuracy record

Yield was over-projected three times, each from a single good example:

| Projection | Basis | Actual |
|---|---|---|
| 400–600 awards from district pages | Manatee directory | ~57 |
| 400–600 from counselor pages | Jupiter High | 142 names, many national |
| 30–50% website match | none | **17%** |

The competitive findings held up better, because they came from independent checks rather than
extrapolation: ~6 of 50 states have sub-state scholarship search, Miami-Dade has none, CampusReel's
county pages are templated (four counties, identical totals), and the vendor ecosystem has a
structural reason not to close the gap.
