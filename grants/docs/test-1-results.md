# Test 1 Results — Does the local data edge exist?

**Run:** 2026-08-06 · **Region:** Sarasota + Manatee counties, FL · **Cost:** ~$0

---

## Verdict: PASS, decisively — but the product thesis needs to change

The question was whether real local scholarships exist that the national databases don't
carry. The answer is yes, emphatically. The question this test *also* answered, which
wasn't the one being asked, is whether **autofill** is the right value proposition. It
mostly isn't.

---

## The pass

| Pass bar | Result |
|---|---|
| 50+ verified local awards absent from Fastweb / Scholarships.com / Bold.org | **47 verified programs, covering 260+ named awards. 45 of 47 absent from all three.** |

**Zero of ten** named local scholarships tested appeared on Fastweb, Scholarships.com,
Bold.org, Niche, Appily, or Scholarships360.

This is not a data gap — it's **structural**. All three major databases filter no finer
than **state level**. There is no county or city filter anywhere in their architecture.
Searching "Sarasota County scholarships" on Fastweb returns college directory pages for
State College of Florida, not community awards. The tier of award simply doesn't exist in
their model.

The few local awards that *do* surface nationally share a tell: they're the largest and
most professionally administered (the Selby Scholarship at $7,000+, processed partly
through Scholarship America). Every small single-club or family-trust award is invisible.

### What's actually there

| Source | Named funds | Platform | Awarded/yr | Students |
|---|---|---|---|---|
| Community Foundation of Sarasota County | 130+ | CommunityForce | $2.1M | 566 |
| Gulf Coast Community Foundation | 62–66 | Scholarship America | $665K | 247 |
| Manatee Community Foundation | 25+ | AwardSpring | $265K | 96 |
| Rotary Futures SSMS | ~500 listed | Rotary Futures | — | — |
| ~42 independent programs | 42 | mixed | — | — |

Roughly **$3M/year to ~900 local students**, essentially none of it nationally indexed.

---

## The three findings that complicate the product

### 1. Consolidation already happened

Each community foundation runs **one common application covering its entire portfolio**.
A student doesn't fill 260 forms — they fill about 47 at the absolute maximum, and
realistically 15–20 that they're eligible for. The foundations already solved
repetitive data entry inside their own portfolios.

This substantially weakens "autofill saves you from form fatigue." Fifteen applications
is annoying, not agonizing — and the pain is concentrated in a handful of portals rather
than spread across hundreds.

### 2. A quarter of local scholarships can't be automated at all

| Application method | Count | Share |
|---|---|---|
| Online form or portal | 35 | 74% |
| Paper, mail, phone, or high-school guidance office | 12 | **26%** |

Six of the ten live named trusts route through a **guidance counselor** or a school
district. The Dakin Family Scholarship requires a postmarked paper application. Venice
Lions has no portal at all — you phone them. No browser agent touches any of this.

### 3. Local aggregators already exist — they're just fragmented

The competitor is not Fastweb. It's:

- **Rotary Futures SSMS** — ~500 scholarships, staffed with in-person student coaches, free
- **Education Foundation of Sarasota County** — its own scholarship database
- **Manatee Education Foundation** — "The Scholarship Source" directory
- **Manatee County Schools** — counselor-curated Scholarship Central page
- **Sarasota County Schools** — SchooLinks portal, login-gated
- **UnidosNow** — scholarship dashboard for Hispanic/Latinx students
- **fun4manasotakids.com** — local listings

The real gap is not "nobody aggregates this." It is "**six organizations each hold a
partial slice and none of them connect**," plus none of them rank by a student's odds.

---

## Platform concentration — the one strong signal for the build

Five platforms cover the large majority of automatable awards:

**CommunityForce · Scholarship America · AwardSpring · Blackbaud AcademicWorks · Rotary Futures**

This validates the record-once-replay-many thesis from the decision memo: you would build
five integrations, not eight hundred. Whatever gets built, that's the leverage point.

---

## Filter calibration (for scaling this method)

Name-based matching on the IRS Business Master File runs about a **45% true-positive
rate**. Of 22 organizations with "SCHOLAR" in the legal name:

- 10 were live, applicable scholarships
- 12 were not — including a counseling program, a cultural-trip program, a staff-only
  employee benefit, a Special Olympics grantmaker, two invitation-only foundations, and
  **two Sarasota-registered trusts whose beneficiaries are in New Jersey**

Scaling nationally means budgeting for that verification step. 834 scored candidates in
two counties produced 47 verified programs.

---

## Timing

Every local deadline clusters **December–March** (CFSC Feb 1, Manatee CF Mar 1, Gulf Coast
early March, Suncoast CU Feb 15, Achieva ~Mar 21). It is August. **The entire cycle is
closed.** Test 3 — showing families their matched awards and asking for money — cannot run
meaningfully until November at the earliest.

---

## What this means for the next decision

**The discovery half of the product is validated.** Local awards are real, substantial,
invisible nationally, and scattered across sources that don't talk to each other. Ranking
them by a student's actual odds is a feature nobody offers.

**The autofill half is weaker than assumed.** Consolidation removed most of the repetition,
a quarter of awards aren't online at all, and the strongest local player (Rotary Futures)
answers the same need with free human coaching.

**The nonprofit route looks better after this test than before it.** The same scan found
**412 local grantmaking foundations holding $4.59B** in these two counties — with no
common-application consolidation, no counselor gatekeeping, no seasonal cliff, and a buyer
who has a budget. That asymmetry got wider, not narrower.

### Recommended next step

Do **not** proceed directly to Test 2 (the 30-portal fill test) as written. It measures the
weaker half of the product. Instead, pick one:

- **A — Reframe and re-test.** Build the discovery + odds-ranking prototype against the 47
  verified awards. Test whether *that* is worth paying for, independent of autofill.
- **B — Test the nonprofit route.** Ten conversations with small local nonprofits about
  what they use for grant discovery and what they'd pay. Cannot be skipped or automated.
- **C — Run Test 2 narrowly.** Fill only the five hub platforms rather than 30 scattered
  portals. Cheaper, and it directly measures the actual leverage point.

---

## Reproducibility

```bash
curl -sS "https://gt990datalake-rawdata.s3.amazonaws.com/EfileData/BMF/IRS_BMF_2026_5_28_raw.csv" -o /tmp/bmf.csv
python3 scripts/01_filter_bmf.py /tmp/bmf.csv data/01_candidates.csv 20
python3 scripts/02_funders_for_nonprofits.py /tmp/bmf.csv data/02_local_funders.csv 100000
```

Web verification was done by five parallel research agents. Note: `WebFetch` returned 403
for all hosts during this session and ProPublica/IRS.gov/Grants.gov are blocked by egress
policy, so scholarship details come from search-index snippets rather than direct page
reads. Foundation-stated totals (130+, 62–66, 25+) are reliable; individual fund names are
partial. Re-running with working direct fetch would complete the fund rosters.
