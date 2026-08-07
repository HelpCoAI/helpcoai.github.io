# Measured True-Positive Rate — Priority-A Sample (n=15)

**Date:** 2026-08-07 · **Source:** `05_pilot_candidates.csv`, systematic sample across the 548
priority-A rows (every ~39th row by rank, so the sample spans score 143 down to score 30).

This replaces the **assumed 45%** true-positive rate that scripts 04–07 and the build plan were
costed against.

---

## Result

| Outcome | n | Share |
|---|---|---|
| **Clear pass** — real, student-facing, locally-scoped award | **6** | **40%** |
| Edge — real award but geography or membership mismatch | 2 | 13% |
| Fail | 7 | 47% |

**40% clear / 53% listable.** On n=15 the 95% confidence interval is roughly 16–68%, which brackets
the 45% assumption. **The plan's economics do not change.** Costs scale with candidates scanned, not
with candidates that pass, so a lower TP rate raises cost-per-verified-record but not total spend.

---

## The sample

| # | Org (BMF name) | Score | Verdict | Note |
|---|---|---|---|---|
| 1 | Ann & Lars Lewander Scholarship Foundation | 143 | **Fail** | Closed — employees/dependents of the sponsoring company only |
| 2 | Dorothy Brown Scholarship & Community Dev. Fund | 103 | Pass | Real (via DS4K); email-only application, weak web presence |
| 3 | Mini Friends Foundation | 93 | **Fail** | Animal farm for special-needs children. No scholarship of any kind |
| 4 | Memorial Scholarship Program of Freedom Village | 70 | **Fail** | Real $15k/yr award — but for *nursing-home staff*, not students |
| 5 | Maggi Gives Back Foundation | 63 | **Fail** | Pays housing costs for families in hardship. Not a scholarship |
| 6 | Trinity Rotary Charitable Foundation | 60 | Pass | Pasco HS seniors; mail-in; deadline Mar 25 |
| 7 | Ye Mystic Krewe of Gasparilla Community Fund | 53 | Pass | $1.1M awarded; Hillsborough grads — *principal nomination only* |
| 8 | Barbara L. Higgins Legacy | 53 | Edge | Real scholarship org, but serves Alachua County. BMF address is Riverview |
| 9 | Catholic Community Foundation of SW Florida | 50 | **Pass (best)** | 7 scholarships, online portal, Mar 1 deadline, Sarasota County |
| 10 | Rotary Club of Largo Charitable Foundation | 40 | **Fail** | No evidence of a scholarship program |
| 11 | St Petersburg Lodge No 1145, Loyal Order of Moose | 30 | Edge | Moose scholarships are national and require a family member's membership; the lodge runs none |
| 12 | Kiwanis International Inc (St Petersburg) | 30 | **Pass (best)** | Any St Pete HS senior; Apr 1 deadline; 4-year awards, $30k/yr pool |
| 13 | Rotary International (Hudson) | 30 | **Pass (best)** | Hudson HS seniors; **19 applicants → 5 awards of $3,000** |
| 14 | Bradenton Chapter No 1072, Women of the Moose | 30 | **Fail** | No evidence of a scholarship program |
| 15 | Kiwanis International Inc (Zephyrhills) | 30 | **Fail** | Club exists (Facebook only); no local program found |

---

## What the sample taught us that the score cannot

### 1. Score is barely predictive *within* the A tier — and is inverted at the top

The highest-scoring org in the entire 2,472-row pilot (**143**) failed. Three of the six clear passes
scored **30**, the A-tier floor. `name contains "SCHOLARSHIP"` is necessary but not sufficient: it
reliably catches **closed family and corporate foundations**, which look identical to open programs
in the BMF and are worthless to a student.

**Action:** review order inside tier A should not be by score. Sort by *organization type* instead —
service clubs and community foundations first, named-person foundations last.

### 2. Three failure modes the model never accounted for

| Mode | Example | Frequency in sample |
|---|---|---|
| **Closed / restricted-beneficiary** — real money, no public applicants | Lewander (employees), Freedom Village (staff), Moose (members' families) | 3 of 15 |
| **Name mismatch** — BMF name is the national parent, not the local club | "KIWANIS INTERNATIONAL INC" *is* the Kiwanis Club of St. Petersburg | affects most service-club rows |
| **Geography mismatch** — mailing address ≠ service area | Barbara Higgins: Riverview address, Alachua County program | 1 of 15 |

The name-mismatch mode is the fixable one and it is **suppressing measured yield at the bottom of
tier A**. The extractor must resolve `parent org + city → local chapter name` before searching, or it
searches for a national body and finds nothing. Two of the seven failures (Rotary Largo, Kiwanis
Zephyrhills) may well be false negatives for exactly this reason.

### 3. School-district pages are a better discovery channel than the BMF

Every Pasco-area search surfaced district-run scholarship aggregations:
`connectplus.pasco.k12.fl.us`, `ghs.pasco.k12.fl.us`, `pascoeducationfoundation.org`. These are
counselor-maintained lists of awards **students can actually apply to** — already filtered for the
open/local/current criteria that cost us 60% of the BMF funnel.

The BMF finds *organizations*. District pages find *awards*. **Stage 4 of the schema doc should be
promoted ahead of Stage 3** for the pilot: crawl ~15 district and education-foundation lists first,
then use the BMF to enrich sponsors and to find awards the districts missed.

### 4. The competition thesis is now evidenced, not assumed

**Rotary Club of Hudson: 19 applicants, 5 awards, $3,000 each — a 26% win rate.**

Coca-Cola Scholars is ~0.15%. That is a **170x** difference in odds, on a real, named, verifiable
local award. This is the single number the entire expected-value ranking feature rests on, and it is
the first time we have observed it directly rather than inferred it.

---

## Effect on the plan

- **Do not re-cost.** 40% vs 45% is inside the noise on n=15 and does not move break-even (10 paying
  users) or the $81 pilot build.
- **Re-order the work.** District/education-foundation crawl first; BMF second. This raises yield per
  hour of review substantially.
- **Add chapter-name resolution** to the extractor before running the full A tier.
- **Add a `beneficiary_scope` field** to the schema (`open` / `members_only` / `employees_only` /
  `nomination_only`) — 5 of 15 orgs here needed it, and shipping "apply now" on a closed award is
  precisely the trust failure the plan calls business-ending.
- **Capture `applicants_estimated` whenever a sponsor publishes it.** Rotary Hudson published theirs
  in a press release. That data is free, it is the product's differentiator, and no competitor has it.
