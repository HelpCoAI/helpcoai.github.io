# Scholarship Record Schema

The eligibility fields are not optional detail — **they are the product.** Every page type the
site generates (state, county, high school, major, demographic) is a query against these fields.
Get the schema wrong and you cannot generate the pages, cannot match students, and cannot rank by
odds.

---

## Why geography needs four levels, not one

Real eligibility language from the 47 verified awards:

| Award | Eligibility as written | Geographic level |
|---|---|---|
| Englewood BPO Elks | "Lemon Bay HS seniors" | **Single high school** |
| Jessica Costanzo | "Venice HS senior attending Webber International" | **Single high school + destination college** |
| Lindsey Maibach | "Booker/North Port/Riverview/Sarasota/Venice HS" | **Named list of five schools** |
| Kiwanis Bradenton | "Manatee County public HS senior" | **County + school type** |
| St Andrew Scottish Society | "Sarasota/Manatee seniors + Lemon Bay HS" | **Two counties + one extra school** |
| Dakin Family | "Manatee seniors in Animal Science project at County Fair" | **County + activity** |
| Florida Elks HOPE | "FL HS senior" | **State** |

A single `location` string cannot represent any of this. The schema needs **state, county, city, and
an explicit array of named high schools**, because awards restrict at every level and often at
several simultaneously.

---

## Schema

```json
{
  "id": "uuid",
  "name": "Englewood BPO Elks Scholarship",
  "sponsor": { "name": "Englewood BPO Elks Lodge 2378", "ein": "59-1234567", "type": "service_club" },

  "award": {
    "amount_min": 3000, "amount_max": 3000,
    "amount_type": "fixed",
    "renewable": true, "renewal_years": 4,
    "num_awards": 15
  },

  "deadline": {
    "date": "2027-03-01",
    "type": "fixed",
    "opens": "2027-01-02",
    "confidence": "verified"
  },

  "eligibility": {
    "geography": {
      "states": ["FL"],
      "counties": ["Sarasota"],
      "cities": ["Englewood"],
      "high_schools": ["Lemon Bay High School"],
      "school_districts": ["Sarasota County Schools"],
      "residency_required": true
    },
    "academic": {
      "gpa_min": 3.0, "gpa_max": null, "gpa_scale": "unweighted",
      "class_year": ["senior"],
      "enrollment_status": ["high_school_senior"],
      "majors": [], "majors_excluded": [],
      "destination_institutions": []
    },
    "personal": {
      "citizenship": ["us_citizen", "permanent_resident"],
      "income_max": null,
      "first_generation": null,
      "gender": null,
      "heritage": [],
      "military_affiliation": null,
      "disability": null
    },
    "other_criteria": "Must have participated in a school activity",
    "raw_text": "verbatim eligibility text as published"
  },

  "application": {
    "url": "https://...",
    "platform": "paper_counselor",
    "essay_required": true, "essay_prompts": ["..."],
    "recommendation_letters": 2,
    "transcript_required": true,
    "fafsa_required": false,
    "estimated_effort_minutes": 90,
    "autofillable": false
  },

  "competition": {
    "applicants_estimated": 40,
    "applicants_source": "heuristic",
    "eligible_pool_estimated": 380,
    "win_probability": 0.375
  },

  "provenance": {
    "discovered_via": "irs_bmf",
    "source_url": "https://...",
    "source_hash": "sha256:...",
    "first_seen": "2026-08-06",
    "last_verified": "2026-08-06",
    "verification_status": "live",
    "confidence": 0.92
  },

  "risk": { "scam_score": 2, "fee_required": false, "flags": [] }
}
```

---

## The fields that produce pages

Each generates a distinct set of SEO landing pages from the same records:

| Field | Page template | Approx. page count |
|---|---|---|
| `high_schools[]` | "Scholarships for [School] Students" | **~24,000** US public high schools |
| `counties[]` | "Scholarships for [County] Students" | ~3,000 |
| `cities[]` | "Scholarships in [City]" | ~19,000 incorporated places |
| `states[]` | "[State] Scholarships" | 50 |
| `majors[]` | "Scholarships for [Major] Majors" | ~200 |
| `heritage[]`, `military_affiliation`, `first_generation` | Identity-based pages | ~50 |

**High-school pages are the most precise match to how these awards restrict eligibility, and there
are eight times more of them than county pages.** Students also know their school name with total
certainty, which counties cannot claim. Whether that translates to search volume is unverified —
build both and measure.

---

## The field that makes ROI ranking possible

`competition.win_probability` is what differentiates the product. Estimating it:

- **When disclosed** — some providers publish "over 1,000 apply for 5 awards." Use it directly.
- **Heuristic otherwise:** eligible pool ≈ (students at the named schools or in the county) ×
  (fraction meeting GPA and other filters). Applicants ≈ 10-30% of that pool for local awards, far
  lower for national ones. Then `win_probability ≈ num_awards / applicants_estimated`.
- **Calibrate over time** with your own users' reported outcomes. That data is proprietary and
  compounds — no competitor can copy it.

Ranking is then `expected_value = amount × win_probability`, and the displayed sort is
`expected_value ÷ estimated_effort_minutes`. Always show the inputs, never just a score — an
unexplained "73% match" destroys trust the first time it's visibly wrong.

---

## Verification cadence

**The expensive mistake is re-extracting everything on a schedule.** Scholarship pages change once
or twice a year. Detect change, then extract.

| Check | Frequency | Cost | Mechanism |
|---|---|---|---|
| Deadline passed | **Daily** | ~free | Date comparison. Auto-expire. |
| URL alive | **Weekly** | ~free | HTTP HEAD. Flag 404s and redirects-to-homepage. |
| Content changed | **Weekly** | ~free | SHA-256 of the main content block vs. `source_hash` |
| **LLM re-extraction** | **Only when the hash changes** | $0.006/record | ~2x/year per record in practice |
| Full re-extraction regardless | **Annually**, staggered | $0.006/record | Safety net against silent drift |

Hash-gated extraction runs roughly **3 extractions per record per year** instead of 12 — a **4x
cost reduction** over a naive monthly schedule.

**Confidence decay:** a record not verified within 60 days displays a lower confidence badge rather
than silently presenting as current. Two consecutive liveness failures auto-suppress it pending
review. A student missing a real deadline because the data was stale is the failure mode that ends
a trust-based product.

---

## Where each field comes from

| Stage | Source | Fields populated |
|---|---|---|
| 1 | IRS Business Master File | sponsor name, EIN, address, NTEE, assets |
| 2 | 990 / 990-PF XML | confirms grants to individuals, amounts, `num_awards` |
| 3 | **The sponsor's own website** | **everything in `eligibility` and `application`** |
| 4 | School district and education foundation pages | awards with no independent web presence |
| 5 | Community foundation portals (CommunityForce, AwardSpring, Scholarship America) | named funds behind a common application |

**Stage 3 is the work.** There is no database of eligibility requirements — if there were, Fastweb
would have bought it twenty years ago. Assembling stages 3-5 into structured records *is* the
product.
