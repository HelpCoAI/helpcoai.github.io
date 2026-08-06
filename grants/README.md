# Grants & Scholarships — Validation Project

Standalone business exploration. **Not part of the HelpCo AI product line** — this
lives on a non-default branch and is not published by GitHub Pages.

## What this is

Validating whether an AI-assisted scholarship discovery + form-autofill product is a
real business, before writing any product code. The full decision memo (market
history, technical feasibility, legal boundaries, business model, data strategy) is in
`docs/decision-memo.md`.

**Product concept being tested:** a student fills out one master profile; the app shows
scholarships they actually qualify for — including small local awards mined from public
foundation tax filings that the big national sites don't list — ranked by best odds per
hour of effort. A browser extension fills the repetitive fields on each application; the
student writes their own essay, reviews, and clicks submit.

**Explicitly not built:** AI-written essays, autonomous submission, anything touching
FAFSA or a student's FSA ID, CAPTCHA circumvention. See the memo for why each is
off the table.

## Test 1 — does the local data edge exist?

The whole thesis rests on one assumption: that real local scholarships exist which
Fastweb, Scholarships.com, and Bold.org don't carry. If false, the product is a
commodity competing against free incumbents with 25-year head starts.

**Pass bar:** 50+ verified, currently-open local awards absent from all three.

### Data source

GivingTuesday's public 990 data lake — `s3://gt990datalake-rawdata`. This is the
maintained successor to the IRS's own AWS dataset, which stopped updating in
December 2021.

The IRS Business Master File (`EfileData/BMF/`) lists every registered US nonprofit
with address, NTEE classification, assets, and filing requirements. Current file:
`IRS_BMF_2026_5_28_raw.csv`, ~324MB, 1,966,267 organizations.

Note: ProPublica's Nonprofit Explorer API, IRS.gov, and Grants.gov are all blocked by
this environment's egress policy. The S3 data lake is reachable and is the better
source anyway.

### Scripts

| Script | Purpose |
|---|---|
| `scripts/01_filter_bmf.py` | Filters the BMF to Sarasota/Manatee counties and scores organizations by likelihood of running a scholarship program (name patterns, NTEE codes, 990-PF filing status, foundation classification). |
| `scripts/02_funders_for_nonprofits.py` | Same source, opposite grant direction — local foundations that fund *organizations*. Seed data for the nonprofit-facing version of the product. |
| `scripts/03_compare_metros.py` | Re-runs both scans against median metros (Toledo, Wichita, Chattanooga) and normalizes per capita, to test whether the Sarasota result generalizes. |

```bash
# Fetch the master file (~10s)
curl -sS "https://gt990datalake-rawdata.s3.amazonaws.com/EfileData/BMF/IRS_BMF_2026_5_28_raw.csv" \
  -o /tmp/bmf.csv

python3 scripts/01_filter_bmf.py /tmp/bmf.csv data/01_candidates.csv 20
python3 scripts/02_funders_for_nonprofits.py /tmp/bmf.csv data/02_local_funders.csv 100000
```

### Results so far

| Metric | Value |
|---|---|
| Organizations scanned | 1,966,267 |
| Registered nonprofits in Sarasota/Manatee | 4,529 |
| Scored as plausible scholarship grantmakers | 834 |
| — with "SCHOLAR" in the legal name | 26 |
| — community foundations (each administers many named funds) | 12 |
| — service clubs (Rotary, Elks, Kiwanis, Lions, Sertoma…) | 95 |
| — 990-PF filers holding >$250K | 344 |
| Local grantmaking foundations (nonprofit route) | 412 |
| Their combined assets | $4.59B |

**Test 1 verdict: PASS.** 47 verified local scholarship programs covering 260+ named
awards; 45 of 47 absent from Fastweb, Scholarships.com, and Bold.org. Zero of ten named
local scholarships appeared on any national database. The gap is structural — all three
major databases filter no finer than state level.

See `docs/test-1-results.md` for the full verdict, including the three findings that
complicate the autofill half of the product.

### Does it generalize beyond Sarasota?

Sarasota/Manatee is a wealthy retirement region, so the scan was re-run against three
median metros to check whether the result is representative.

| Region | Nonprofits/100k | Scholarship orgs/100k | Grantmakers/100k | Foundation $/capita |
|---|---|---|---|---|
| Sarasota+Manatee, FL | 515 | 94.8 | 46.8 | $5,213 |
| Toledo, OH | 584 | 61.0 | 22.2 | $1,826 |
| Wichita, KS | 497 | 62.5 | 27.8 | $3,064 |
| Chattanooga, TN | 565 | 53.0 | 27.6 | $4,808 |

Sarasota is above average but not an outlier — 1.5-1.8x on scholarship density. The thesis
generalizes with a haircut, not a cliff. Note that overall nonprofit density is *higher* in
Toledo and Chattanooga: customers for a nonprofit-facing product are evenly distributed
nationally, while funders concentrate in wealthy regions.

## Nonprofit route assessment

Same technology, different customer. Full analysis in `docs/nonprofit-route-assessment.md`.

**Verdict: "cheaper Instrumentl" is dead** — Instrumentl raised $55M (Summit Partners, April
2025, $185M valuation), reviews 4.9-5.0/5, and at least five competitors already occupy the
cheap lane (GrantCopilot $24/mo, Grantable $25-50/mo, OpenGrants free, FundRobin, Vee). The
small-nonprofit segment's revealed clearing price is $8-17/mo and ~39% are all-volunteer with
no one to sell to.

**What is live:** a consultant-first, multi-client workspace seeded with hyperlocal 990-derived
funder data, sold to freelance grant writers (~2,500-3,100 GPA members, billing $35-250/hr,
already paying $449-699/yr for tools). Instrumentl has a documented, unfixed permissioning gap
against exactly this buyer.

Build effort: 3-4 months to first paying customer on a narrow MVP; 9-12+ months to parity.
The first hire is data/research ops, not an engineer — RFP freshness QA is the binding
constraint.

## Data files

| File | Contents |
|---|---|
| `data/01_candidates.csv` | Scored scholarship-grantmaker candidates. Columns: score, ein, name, city, county, zip, ntee, files_990pf, foundation_cd, assets, income, revenue, signals |
| `data/02_local_funders.csv` | Local grantmaking foundations for the nonprofit route. Columns: name, ein, city, county, type, ntee, files_990pf, assets, income, revenue |
| `data/03_verified_scholarships.csv` | 47 web-verified local scholarship programs. Columns: name, sponsor, county, amount, deadline, eligibility, apply_via, platform, essay, on_national_dbs, notes |
| `data/04_metro_comparison.csv` | Per-capita comparison of Sarasota against three median metros. |

Raw BMF files are not committed — they're 324MB each and re-downloadable in seconds.

## Legal note on the data

IRS Form 990 filings are public records. Factual data (organization name, assets,
grant amounts) is not copyrightable under *Feist v. Rural Telephone*. This project
does not scrape competitor databases — Fastweb and Scholarships.com are checked
only via public search results, never fetched directly.
