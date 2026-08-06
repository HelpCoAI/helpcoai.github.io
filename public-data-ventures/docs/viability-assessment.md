# Viability Assessment — Adversarial Stress-Test

**Date:** 2026-08-06 · **Method:** deliberately hostile second pass over six ideas an optimistic first pass rated promising.

---

## Headline

**Five of six "no dominant incumbent" claims were false.** In every case the first pass had
searched the wrong category — it checked grants databases but not wealth screening, checked
regulatory suites but not vertical-specific trackers, checked for an API gap without checking
whether competitors had already closed it.

**None of these beats the scholarship/grant business the team already has working.** Every one of
them dies primarily on **distribution and incumbent trust, not data access** — which is precisely
the asset the existing project already has and these do not.

---

## Idea-by-idea

### #1 Local Funder Warm-Intro Engine — **survives, narrowed**

**Incumbent claim: FALSE.** [DonorSearch](https://www.donorsearch.net/wealth-screening/) already
ships this exact feature — "Inner Circle" relationship mapping that flags connections through
nonprofit and corporate board service, updated weekly. iWave, WealthEngine, and Windfall do
overlapping board-network mapping. The first pass checked the grants-database category (Candid,
Instrumentl) and never looked at wealth screening.

**But the wedge is real, just narrower than claimed:** incumbents bundle this into $3,000-15,000/yr
wealth-screening suites the target buyer cannot afford. The pitch is "unbundled and affordable,"
not "nobody does this."

**Why it still ranks first:** lowest liability (a false connection wastes a phone call), no
regulatory exposure, self-serve buyer reachable without industry relationships, and it **reuses the
already-built 990 pipeline** — roughly 80% of the hard data engineering is done.

**Real weaknesses:** nonprofits under $2M rarely have a dedicated development director — it's the
ED wearing two hats. And $49-99/mo competes for a *second* software line item against Bloomerang
(~$139/mo) and DonorPerfect (~$200/mo) in an org whose whole identity is minimizing overhead.
990 data also lags 12-18 months, so board rosters go stale — a real problem for a "warm intro"
product where the contact may have rolled off.

### #2 openFDA Mass Tort Radar — **dead, most crowded on the list**

**Incumbent claim: emphatically FALSE.** [Darrow.ai](https://sacra.com/c/darrow/) has raised **$63M**,
did **$26M revenue in 2024** heading toward $120M, and has **80 law firms / 3,000 lawyers** on
platform. Plus [PharmaIntel AI](https://pharmaintelai.com/) (literally "search any drug or device,
instantly access FDA adverse event data"), [Pattern Data](https://patterndata.ai/solutions/screen),
and [LexGenius](https://feed.lexgenius.ai/).

This is a well-capitalized, actively consolidating niche. A team with no legal-industry
relationships has no path to win trust against a three-year head start.

Additional problem: MAUDE and FAERS are explicitly **unverified, voluntary** reports — the FDA warns
against inferring causation. An LLM layer that overstates signal feeds firms into expensive bad
case-acquisition spend.

### #3 OSHA/WHD Underwriting Feed — **near-dead, plus FCRA exposure**

**Incumbent claim: FALSE.** [ParseData](https://parsedata.io/industries/workers-comp-underwriting)
already sells exactly this — "helps workers' comp underwriters identify recurring OSHA compliance
issues... filter manufacturing companies carrying both an OSHA inspection and a DOL wage case." And
LexisNexis Risk publicly markets
[public records for micro-business underwriting](https://risk.lexisnexis.com/insights-resources/blog-post/leveraging-public-records-for-micro-business-underwriting),
directly contradicting the "priced only for large carriers" premise.

**The sharpest data-danger problem on the list.** This is fuzzy entity matching feeding a
**pricing/bind decision**. A false-positive match — wrong "ABC Construction LLC" flagged for a
competitor's violation — causes mispriced or wrongly-declined coverage. That's real financial harm
and E&O exposure flowing back to the vendor.

**FCRA is a live wire.** FCRA's "consumer" is an individual, not an entity — so scoring only LLCs is
likely outside it. **But wage-theft records frequently attach to sole proprietors**, and a
sole-prop named insured *is* an individual, dragging it back inside FCRA's insurance-underwriting
definition. Getting that wrong means operating as an unregistered consumer reporting agency.

### #4 Credentialing Cross-Check — **refuse to build as scoped**

**"PECOS has no public API, so reconstruction is the moat" — falsified twice over.**
[Verisys](https://verisys.com/solutions/eligibility/) delivers near-instantaneous results across
NPI, DEA, Medicare Opt-Out, exclusions, **PECOS**, and state boards in one product.
[CertifyOS](https://www.certifyos.com/resources/blog/api-future-of-provider-data) claims API-first
real-time PECOS/NPPES/CAQH/board integrations with 2M+ pre-verified NPIs. And CAQH ProView — used
by ~80% of physicians — is the utility the whole category sits on.

**FCRA almost certainly applies.** This is data about *individual* providers used for
*employment and credentialing decisions* — squarely inside FCRA's "employment purposes" definition.
Selling it without adverse-action notices, dispute processes, and §607(b) accuracy procedures
exposes the team to statutory damages.

**Stacked on patient-safety liability:** a wrong or stale PECOS status can put an excluded provider
in front of patients, or wrongly block a legitimate one from billing. And a "reconstructed"
non-primary-source feed is disqualifying for hospitals that need primary-source verification for
accreditation.

**Recommendation: do not build.** Re-scoping it as a non-decisioning research aid guts the value
proposition.

### #5 Vertical Regulatory Alert Line — **survives, second place**

**The only claim that partly held.** Enterprise incumbents (Thomson Reuters, Ascent RegTech at
$30-100K+/yr, Compliance.ai, Regology) genuinely have no small-business tier.

**But vertical tools already occupy each sub-vertical:** [Enhesa's PFAS Tracker](https://www.enhesa.com/product-intelligence-solution/pfas-tracker/)
exists with an active launch discount, cannabis has Metrc and ProCanna, and BSA-AML RegTech is
mature and crowded.

**The real competitor is free.** Federal Register and Regulations.gov both offer native free
email/RSS alerts by agency and topic. A price-sensitive 20-person company will ask why they should
pay $199-499/mo for filtered versions of something they already get free.

Upside: lowest-liability of the regulated ideas (alerts, not decisions), authoritative same-day
data, and a clear named buyer with signing authority under $500/mo.

### #6 BEAD Broadband Gap-Filler — **dead on timing and incumbency**

**[CostQuest](https://www.costquest.com/broadband-serviceable-location-fabric/) is not a competitor
to watch — it is the FCC's contracted vendor that built and controls the National Broadband
Serviceable Location Fabric**, the authoritative source this idea proposes to reprocess. There is
already a formal government-run challenge process for corrections.

**And the timing window has largely closed.** As of mid-2026 most states have final proposals
approved and are moving into contracting — the high-value "gap analysis for application" moment has
mostly passed.

Buyers are also cash-poor rural ISPs and co-ops that often can't pay $5-50K before grant funds land.

---

## Ranking for this team

| Rank | Idea | Verdict |
|---|---|---|
| **1** | Funder Warm-Intro Engine | Survives. Reuses existing pipeline, no regulatory risk, self-serve buyer. A *maybe*, not a clear win. |
| **2** | Vertical Regulatory Alerts | Plausible new line, but a cold start with no asset reuse and free substitutes. |
| 3 | BEAD Gap-Filler | Timing passed, incumbents embedded, buyers cash-poor. |
| 4 | OSHA/WHD Underwriting | Live competitor, FCRA ambiguity, severe wrong-match liability. |
| 5 | Credentialing Cross-Check | **Refuse.** FCRA + patient safety + falsified moat. |
| 6 | openFDA Mass Tort | Darrow at $63M/$26M revenue owns it. No path. |

---

## Cheapest tests for the two survivors

**Funder Warm-Intro Engine — ~$0-100, two weeks.** Build nothing new. Run the existing 990 pipeline
against 15-20 real Sarasota/Tampa nonprofits under $2M, hand-generate 3-5 connection reports each,
and cold-email the EDs with **the finding attached — not a pitch**. Offer the full map for $49.
**Kill signal:** fewer than 2 of 20 respond with real interest.

**Regulatory Alerts — ~$50-100, two weeks.** Pick PFAS (Enhesa's tracker proves paying demand exists
at enterprise price). Build a bare LLM-summarized weekly digest off Federal Register PFAS filings,
cold-email 30-50 compliance officers at small manufacturers, free 4-week trial with a $199/mo ask.
**Kill signal:** fewer than 3-5 convert or reply with real interest — meaning "we already get free
Federal Register alerts" wins.

---

## The bottom line

**None of these beats the scholarship business, and it isn't close.**

The team has a validated 990 pipeline and 47 verified local scholarships — distribution, data, and
product signal already proven. **Every one of these six ideas dies primarily on distribution and
incumbent trust, not data access.** Ideas #2, #3, #4, and #6 all require building credibility from
zero in industries the team has never touched (mass tort law, insurance underwriting, hospital
credentialing, telecom-infrastructure grant consulting) against funded, embedded incumbents.

Idea #1 is the only genuine adjacent extension — same pipeline, same nonprofit-facing distribution,
same unregulated risk profile.

**"Strong AI engineering, no domain expertise, no relationships" is a losing hand against
trust-gated, relationship-driven buyers.** That's the lesson worth keeping from this exercise.

---

*Method caveat: WebSearch only — WebFetch and curl are blocked for most .gov and vendor hosts by
this environment's egress policy. Vendor pricing is directional, not contractual.*
