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

Web verification of actual application details, and the aggregator coverage check
that decides the test, are in progress.

## Data files

| File | Contents |
|---|---|
| `data/01_candidates.csv` | Scored scholarship-grantmaker candidates. Columns: score, ein, name, city, county, zip, ntee, files_990pf, foundation_cd, assets, income, revenue, signals |
| `data/02_local_funders.csv` | Local grantmaking foundations for the nonprofit route. Columns: name, ein, city, county, type, ntee, files_990pf, assets, income, revenue |

Raw BMF files are not committed — they're 324MB each and re-downloadable in seconds.

## Legal note on the data

IRS Form 990 filings are public records. Factual data (organization name, assets,
grant amounts) is not copyrightable under *Feist v. Rural Telephone*. This project
does not scrape competitor databases — Fastweb and Scholarships.com are checked
only via public search results, never fetched directly.
