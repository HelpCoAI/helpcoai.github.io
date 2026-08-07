# Filter Schema — what a student needs to answer "can I apply?"

Benchmarked against [Apply Tampa Bay](https://applytampabay.org/), the closest comparable
product. **Ours must be a strict superset of theirs.**

Apply Tampa Bay's dataset is **73 scholarships across 8 counties** (~9 per county) as of
2026-08-07, badged "EARLY RELEASE". Their interface is good and their data is thin — the inverse
of our position.

---

## Their filters, and our coverage

| Apply Tampa Bay | Our field | Status |
|---|---|---|
| GPA | `gpa_min`, `gpa_max`, `gpa_scale` | captured |
| FIELD OF STUDY | `majors[]`, `majors_excluded[]` | captured |
| CURRENT SCHOOL | `high_schools[]` | captured |
| HOMETOWN | `cities[]`, `counties[]` | **counties only — cities missing** |
| NEED & MERIT | `need_based`, `merit_based` | **missing** |
| ACTIVITIES | `activities[]` | **missing** |
| CLUBS & ORGANIZATIONS | `clubs_organizations[]` | **missing** |
| COLLEGE PLAN | `college_plan[]` | **missing** |
| Open & Coming Soon | `opens` | **missing** |
| Sort: Deadline / Open Date / Award / Organization | all present | — |

**They do not sort by odds or expected value.** That remains unoccupied by the closest
comparable product.

---

## Fields the running parse captures

`name` · `sponsor` · `amount_min` · `amount_max` · `num_awards` · `applicants_estimated` ·
`deadline` · `gpa_min` · `counties` · `high_schools` · `majors` · `apply_url` · `platform` ·
`essay_required` · `beneficiary_scope` · `geo_scope` · `eligibility_raw` · `source_file`

## Fields the enrichment pass must add

Derived from `eligibility_raw`, which is captured verbatim — so no re-crawling is needed.

### Matching Apply Tampa Bay
| Field | Type | Example from our data |
|---|---|---|
| `need_based` | bool | CFPBMC: "demonstrated financial need" |
| `merit_based` | bool | Adele Marie Bradley: "based on merit" |
| `activities[]` | list | Dave Davis: "300 hours to one area of service" |
| `clubs_organizations[]` | list | Gina Rose Montalto: "Girl Scout who achieves the Gold Award" |
| `college_plan[]` | enum list | `four_year` `two_year` `trade` `vocational` `any` — George Snow: "ANY accredited school" |
| `cities[]` | list | Venture Miami: "City of Miami and Little Haiti" |
| `opens` | date | Broward Education Foundation: Nov 1 |

### Beyond Apply Tampa Bay
| Field | Type | Example from our data |
|---|---|---|
| `citizenship[]` | list | CFPBMC: "US Citizen or Permanent Resident" |
| `first_generation` | bool | Coral Gables First-Generation Scholarship |
| `heritage[]` | list | ACS: "African-American/Black, Hispanic/Latino, or American Indian" |
| `gender` | enum | CF Broward: "women who are divorced, widowed or abandoned" |
| `military_affiliation` | enum | American Legion: "related to a veteran" |
| `disability` | bool | Sandra K. Lacey: "severe and profound hearing loss" |
| `income_max` | number | Stamps: household thresholds |
| `class_year[]` | list | most: "graduating senior" |
| `enrollment_status[]` | list | Coral Gables: "enroll full-time, without interruption" |
| `destination_institutions[]` | list | Jessica Costanzo: "attending Webber International" |
| `residency_required` | bool | George Snow: "reside **and** attend school in" — two different tests |
| `renewable` / `renewal_years` | bool / int | Coral Gables Four-Year; Kiwanis St Pete 4-year |
| `recommendation_letters` | int | ACS: "2 letters of recommendation" |
| `transcript_required` | bool | common |
| `fafsa_required` | bool | Dual2Degree: "must complete a FAFSA" |
| `employer_affiliation` | string | Gross Memorial: "government employees and their families" |
| `estimated_effort_minutes` | int | derived, feeds EV-per-hour ranking |

---

## Two rules that must not be relaxed

**`eligibility_raw` stays verbatim.** It is the audit trail. Every structured field must be
derivable from it, and when a student disputes a match, the raw text is the answer. Structuring is
lossy; the raw text is not.

**Absent means unknown, never false.** If a page does not mention citizenship, `citizenship` is
empty — not "no requirement". Filtering a student *out* on an inferred requirement costs them an
award they could have won, which is the same failure mode as a stale deadline.

## Why structuring is a separate pass

The extraction schema should change rarely; the filter schema will change constantly as we learn
what students actually filter on. Keeping them separate means a filter change costs one
re-processing run over stored text, not a re-crawl of 300 pages against sites that already
rate-limit us.

---

## Status of the enrichment pass (2026-08-07)

All fields above are now extracted by `scripts/20_extract_awards.py`, which runs over
`scripts/19_declutter.py` output. No field was dropped from the schema; the ones that are
sparse are sparse because the source pages do not state them, which is the correct outcome
under "absent means unknown".

Measured coverage over 364 extracted records:

| Band | Fields |
|---|---|
| >50% | deadline (68%), amount_min/max (53%) |
| 20-50% | majors, high_schools, destination_institutions, cities, college_plan, counties, activities |
| 5-20% | class_year, need_based, gender, beneficiary_scope, essay_required, gpa_min, opens, heritage, merit_based, transcript_required |
| <5% | citizenship, fafsa_required, enrollment_status, residency_required, military_affiliation, clubs_organizations, disability, first_generation, renewable, employer_affiliation, recommendation_letters |

`eligibility_raw` is present on 100% of records, so every sparse field can be re-derived
later without re-crawling — which is the entire reason for the two-pass split.

**Precision is the open problem, not coverage.** A 16-record hand sample read ~55% clean;
the rest are name-boundary artifacts ("Purchase Tickets OPAL Awards"), or amounts pulled
from the wrong sentence ($15 for Native Forward, $65,000 for "State Scholarship"). Regex
segmentation is at its ceiling here.
