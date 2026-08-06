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
| `scripts/04_unit_economics.py` | Consumer unit-economics model including CAC. Run with `[price] [lifetime] [conversion]` to pressure-test assumptions. |
| `scripts/05_revenue_scenarios.py` | Tests three pricing/revenue questions: auto-renew off, advertising as a second stream, and free/paid tiering. |

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

### Market sizing addendum — the IEC channel is disqualified

**IECs do not value small local scholarships.** Their service descriptions frame scholarship
help as a national-merit-aid add-on; none reference local awards. An IEC bills $140-400/hr and
clients pay $5,000-7,000 toward $70K/year schools — a $1,000 local award is immaterial to both.
Local-scholarship search is a *school counselor* concern serving lower/middle-income families,
not a fee-for-service IEC concern. **The student product has now lost its buyer twice.**

Market populations (both LOW-MODERATE confidence, no authoritative count exists):
freelance grant writers **8,000-20,000**; IECs **8,000-20,000**. Grant writers are the better
fit — finding funding *is* their job and they already pay $400-2,000/yr for that class of tool.

**Realistic year-3 outcome: 200-500 customers, $50K-$300K ARR.** A solid two-person business,
not venture scale. Benchmarks: TutorCruncher took ~11 years to $3.1M; GrantHub had 900+ orgs
and was discontinued in early 2026.

**Net position on the nonprofit route:** a validated data asset, a small addressable market, and
a modest ceiling. Next step there is 15-20 conversations with working grant writers.

## Student route economics — reopened

Two earlier claims in this project were wrong and are corrected in
`docs/student-route-economics.md`:

1. **"Students won't pay" was wrong.** ScholarshipOwl does ~$10.3M/yr from ~22,000 paying
   subscribers, self-funded. The dead competitors (Scholly, Going Merry, Fastweb) were *free*
   products that died from acquirer decisions. Scholly was reportedly profitable at $2.99/mo.
2. **The earlier P&L omitted customer acquisition cost entirely** — usually the largest line in
   a consumer model. Corrected in `scripts/04_unit_economics.py`.

**The real constraint is acquisition, not demand.** At $69/yr: LTV $82, healthy CAC ceiling $27,
break-even 2,094 paying users. Paid acquisition loses money under every assumption tested (Meta
~$120-818/customer, Google ~$233-1,591) because education keywords are among the most expensive
on the platform. Organic channels clear easily at $3-23.

**At 10,000 paying users: $690K revenue, $434K net, 63% margin** — a higher ceiling than the
nonprofit route. Realistic organic-only trajectory: year 3 at 3,000-8,000 users, $200-550K.

**Key competitive finding:** ScholarshipOwl is 56% *paid* search. It works because their B2B arm
is the acquisition engine — brands pay them to host sponsored scholarships, and each one becomes
an indexable long-tail SEO page. Their $120-240/yr pricing is roughly the minimum that makes paid
acquisition pencil at all; $69 is priced below that floor.

**Pricing headroom is real:** parents spend $3,000-15,000 on college prep, and essay coaching
alone runs $500-3,000/season. Nobody sells a one-time seasonal pass — likely white space.

**Cheapest next test (<$1,000, no product):** stand up 10-20 hyper-local landing pages from
`data/03_verified_scholarships.csv` with email capture and a $69 pre-sale. Measure ranking at
60-90 days and waitlist-to-paid conversion.

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


## Revenue model decisions (scripts/05_revenue_scenarios.py)

**Auto-renew OFF by default — affordable, and a real differentiator.** At $99/yr it cuts LTV
from $126 to $84 and the CAC ceiling from $42 to $28. Organic CAC is $3-23, so it still clears
comfortably. It also removes the single biggest complaint pattern against ScholarshipOwl
(surprise charges, hard cancellation) and sidesteps ROSCA, FTC click-to-cancel, CA AB 2863, and
NY GOL 5-903 entirely. **Only affordable because acquisition is organic** — if the plan ever
depends on paid ads, auto-renew-off becomes unaffordable.

**Advertising: display ads are not worth it; local sponsorships are.**

| Option | At realistic scale | Verdict |
|---|---|---|
| Display ads in-app | $2.5-31K/yr at 10-50k users | Rounding error; cheapens the product |
| Ads on public content pages | $12-30K/yr at 100k monthly visits | Secondary at best |
| **Local sponsored scholarships** | **$50K/yr at 20 sponsors × $2,500** | **The model that works** |

Sponsored scholarships replicate ScholarshipOwl's actual engine at local scale: a sponsor pays to
host an award, which simultaneously produces revenue, a real scholarship for users, and an
indexable long-tail SEO page. Aligned incentives, no conflict.

**The trap to avoid:** student-loan ads pay the highest RPMs in this vertical — and that is
precisely the conflict. Fastweb sold student leads to lenders. Scholly was bought by Sallie Mae
and converted to lender matching; its founder is now suing over broken data promises. Taking
lender money while claiming to reduce student debt destroys the trust the product runs on.

**Free + paid tiers: required, not optional.** Organic acquisition needs a free entry point —
SEO traffic lands, signs up free, converts later. The split that matters:

- **Free gives the WOW** — "here are 14 local scholarships you'd never have found." Drives word
  of mouth and SEO value, and serves the low-income families the mission targets.
- **Paid gives the TIME** — autofill, document vault, application tracking, expected-value
  ranking, renewal reminders.

Blended P&L at $99/yr, auto-renew off, 5% conversion, 20 local sponsors:

| Free users | Paid | Total revenue | Net |
|---|---|---|---|
| 10,000 | 500 | $99,500 | −$22,985 |
| 50,000 | 2,500 | $297,500 | $145,075 |
| 100,000 | 5,000 | $545,000 | $355,150 |
| 200,000 | 10,000 | $1,040,000 | $775,300 |

Sponsor revenue moves break-even from ~50k free users to ~30k.


## Should this be a nonprofit? (docs/nonprofit-structure-assessment.md)

**Not as the starting structure.** The path swaps an acquisition problem (inside your control) for
a fundraising problem (mostly outside it).

The precedents mislead: **Common App** runs on application fees, not philanthropy. **Scholarship
America's** $259.9M is 91.2% pass-through donor money. **ScholarSnapp** has been foundation-funded
for 15+ years without reaching scale. **Benefits Data Trust closed in 2024** despite Gates, Ballmer,
CZI and a $20M MacKenzie Scott gift. **Beyond12** runs a deficit with a real tech product. Nobody has
made small, diversified-grant-funded, tech-first scholarship discovery work.

Funding math at this stage: realistic first-year grants are **$5-50K** from local and family
foundations. The operation needs **$200-400K/yr**. National funders (Lumina $50K-1.8M, Kresge
$50K-5M, ECMC ~$40M/yr) fund solicited, established grantees — 2-4 years of relationship-building
away.

**Correction on local money:** the $4.59B in Sarasota/Manatee foundation assets is mostly earmarked
as *student scholarship dollars*, not operating capital for a nonprofit. A pitch must target their
much smaller capacity-building bucket.

**Government money survived but is closed:** TRIO ($1.2B) and GEAR UP ($388M) were preserved in the
FY2026 budget fight. But GEAR UP legally requires an LEA or IHE as lead applicant, and TRIO funds
direct-service caseload programs, not software.

**The real killer is founder time** — 40-60% on fundraising in years 1-3, taken directly from the
990 pipeline that is the actual edge. Founder salary caps at $50-70K. No equity, no exit, ever.

**Ads:** UBIT is 21%, but *qualified sponsorship acknowledgments are not taxed*. The local
sponsored-scholarship model therefore works **better** inside a nonprofit — sponsors get a
charitable deduction. Programmatic ad networks get taxed and invite scrutiny.

**The cheap test — weeks, not months.** Don't file Form 1023. Get a **fiscal sponsor** (~10% fee,
live in weeks), then make one narrow ask of 3-5 local funders: *"$15,000 to surface and pre-fill
every Sarasota-County-eligible scholarship for 200 graduating seniors this spring."* Use the 47
verified local awards as the proof point. If 5-10 warm local asks all decline, that's a fast signal
the fundraising motion is harder than the product motion.


## Solo operator plan (docs/solo-operator-plan.md)

Founder constraints clarified: **full-time job, no industry relationships, no time for cold
outreach, open to selling the business.** This invalidates several earlier recommendations.

**Ruled out:** local sponsor sales (relationship work), the nonprofit route (fundraising is 40-60%
of a founder's time), the grant-writer business (relationship sale), customer interviews at scale,
and paid acquisition (already dead on unit economics).

**What survives:** build once, publish, let organic search compound. The only model that fits — and
independently the one the economics already pointed to.

### Corrected sponsor economics

The earlier $2,500-5,000 sponsorship with $1,000-2,000 reaching the student is a **40-60% admin
fee** — above what charity watchdogs tolerate (~25-35%) and well above Scholarship America's 12-20%.
Defensible version: *"You fund the award, $1,000 minimum. We charge a flat $750 admin fee."*
**Revised: 20 sponsors = $15,000/yr, not $50,000.**

### Three changes to the plan

1. **Automate data freshness before building anything pretty.** The earlier $40K/yr human
   verification line isn't available to a part-time operator. Daily deadline expiry, weekly liveness
   checks, monthly LLM re-extraction, confidence decay — roughly $75-90/mo in API cost at 20k
   records. A stale database is a dead product.
2. **Ship the free tier alone first.** Autofill is the most fragile, highest-maintenance piece, and
   26% of local awards are paper/counselor-only anyway. Confirm traffic and conversion first.
3. **Know the exit math.** Micro-SaaS sells at 2.5-4x annual profit. $50K profit → $125-200K;
   $100K → $250-400K. Buyers pay more for automated operations and clean books — start both at
   month one.

### Timeline

Build 3-6 months part-time → **6-12 month SEO dead zone** (this is where side projects die) →
compounding months 12-24 → meaningful revenue months 18-30. Seasonality: local deadlines cluster
December-March, so **build over summer, launch by September**.

### Realistic ceiling

**$30-100K/yr profit by year 2-3, sellable for $75-400K.** Not a salary replacement for years.
A good outcome for a side project.

### First action

Ten to twenty static local landing pages from `data/03_verified_scholarships.csv` — no app, no
login, just real awards with an email capture. Wait 60-90 days, measure ranking. Cost: a domain and
a few evenings. That single test validates the only available channel before any product work.
