# Replacing the 15 Hours of Human Review

**Supersedes** the Phase 0 line in `build-plan.md` that budgeted ~15 hours to hand-verify
priority-A BMF candidates.

---

## The objection

Verifying 626 organizations by hand does not scale. It is 15 hours for one metro, and the
national plan has fifty. A pilot whose method cannot survive its own success is not a pilot.

## What replaces it

**Harvest school counselor pages instead of verifying organizations.**

The evidence came from our own crawl. [Jupiter High's scholarship
bulletin](https://sites.google.com/palmbeachschools.org/jhs-scholarship-bulletin/home), one
counselor's Google Site, 3KB of text, listed **13 named local awards with amounts, GPA bars and
deadlines**. That is more usable award data than the entire 626-row BMF A-tier would yield per hour
of effort, and it required no verification at all.

**Counselors have already done the verification.** They list an award only if their students can
actually apply to it, they keep deadlines current because their job depends on it, and they drop
awards that have closed. That is precisely the work the 15 hours was buying.

| | BMF verification | Counselor-page harvest |
|---|---|---|
| Unit | Organization | Award |
| Yield | 40% are real, student-facing | ~100%, that is why they are listed |
| Amount / deadline | Often absent | Usually stated |
| Human time | ~15 hours per metro | Spot-check a sample |
| Scales by | Hiring people | Adding URLs |

## The bonus: breadth as a free eligibility measurement

Harvesting many school pages produces the same award repeatedly. That repetition is the signal, not
the noise:

| Listed on | Means | Ranking implication |
|---|---|---|
| 1 school page | Hyperlocal, eligible pool is one senior class | **Rank up.** Best odds available |
| 2–5 pages | School cluster or feeder pattern | Rank up |
| 6+ pages | District-wide | Neutral |
| Most pages | Regional, state or national | **Rank down.** Everyone can apply |

This is the hardest input to win probability, the size of the eligible pool, obtained for free, as
a by-product of collection, with no user cooperation and no human reviewer. `14_award_breadth.py`
computes it.

It is also a relevance filter. An award on 40 of 40 school pages is Bright Futures; an award on one
is the Kiwanis Club of that town. The student wants the second one, and the count tells us which is
which without reading a word of eligibility text.

## What the BMF is still for

Not discarded, retargeted. It keeps the two jobs it is uniquely good at:

1. **Sponsor enrichment.** 990 financials behind each award, for the Instrumentl-style sponsor pages
   that double as SEO surface.
2. **Finding what counselors miss.** The 45–58% of priority-A candidates carrying no B82 NTEE code
   are invisible to the free directories, and some will be invisible to counselors too. That is a
   long-tail sweep to run later, automated, not a prerequisite for launch.

## Remaining human time

Spot-check ~20 extracted awards against their source pages to measure extraction accuracy. Perhaps
an hour, once, not 15, and not per metro.
