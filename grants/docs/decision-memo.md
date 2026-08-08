# Decision Memo: AI Scholarship Finder + Auto-Apply Agent

**Date:** 2026-08-06 · **Status:** Go/no-go, pre-build · **Standalone business** (not a HelpCo AI product line)

---

## Context

The proposed product: an app that (a) finds grants and scholarships a student qualifies for, then (b) drives a Chrome browser via an AI agent to fill out and submit the applications for them.

Five parallel research agents investigated market viability, technical feasibility, legal exposure, business model, and the data layer. This memo is the synthesis and the recommendation. You asked for an honest verdict before any building, that's what this is.

---

## Verdict

**Do not build the product as described.** The specific thing you described, a consumer app that finds scholarships and auto-submits applications, is the single most thoroughly-failed business model in edtech. It has killed better-funded teams repeatedly and recently.

**But two-thirds of the idea survives the research, and one adjacent version of it is a genuinely good business.** The recommendation is a 4-week, ~$0-cost validation sprint on three specific assumptions before writing product code, plus a serious look at pointing the same technology at a different customer who pays 10-100x more.

---

## What's true and false in the premise

**False, and this matters, because it's the emotional core of the pitch:** "billions in unclaimed scholarships." This traces to a misread 1976 study of an *employer tuition-benefit pool*, money restricted to specific companies' employees, never publicly available. Courts ruled the framing fraudulent decades ago. Essentially every real scholarship is oversubscribed. Building marketing on this claim walks straight into 30 years of FTC enforcement precedent.

**True, but you can't legally automate it:** there *is* a real unclaimed pool. NCAN estimates **$4.4B in unclaimed Pell Grants** for the class of 2024 alone, from ~830,000 eligible students who never filed a FAFSA. This is the single biggest real opportunity in the space, and Section "Never build" below explains why it is permanently off the table for automation.

**True and underexploited:** the scholarship data most students actually have a shot at, small local awards, is systematically discoverable from free public sources that no incumbent has bothered to mine. This is the one genuine opening.

---

## The four walls

### 1. Market, the graveyard is dense, recent, and well-funded

| Company | What happened |
|---|---|
| **Scholly** | Shark Tank hit, 4M users. Acquired for parts by Sallie Mae 2023, made free. Founder **suing Sallie Mae as of April 2026** over broken user-data-sharing promises. |
| **Going Merry** | Exactly this pitch (one profile → match → multi-submit). Owned by a real lender (Earnest/Navient). **Shut down March 2026**, no reason given, users lost saved applications. |
| **Frank** | FAFSA-simplification tool, sold to JPMorgan for $175M on **fabricated user numbers**. Founder sentenced to 7+ years. |
| **Mos** | Sequoia + Lux backed. 400,000 users, **<10% ever paid anything**. |
| **Fastweb** | 30-year incumbent, changed hands out of parent's **Chapter 11** in 2025. Sits at 2.1/5 stars. |
| **RaiseMe** | Survived only by abandoning B2C entirely and reselling to colleges as enrollment marketing. |

Nobody in that list died from lack of demand or failure to find scholarships, that part works fine. They died from **no viable consumer revenue**. Every major competitor is free. The category has trained students for 25 years that this costs nothing.

The one paid survivor, **ScholarshipOwl** ($10-69/mo, ~$10M revenue, self-funded), already does auto-apply, and its revenue leans visibly on trial-to-auto-renewal friction, with a matching trail of surprise-charge and can't-cancel complaints.

Compounding headwind: the **2026 enrollment cliff has arrived**. US high school graduates peaked in 2025 and decline ~13% through 2041. International enrollment is down 17%. Your core user base shrinks during your build-and-scale window.

### 2. Technical, harder than it looks, in a specific and important way

- **No scholarship backend anywhere has a submission API.** Not Blackbaud Award Management, not AwardSpring, not SmarterSelect, not Kaleidoscope, not Scholarship America, not Grants.gov, not FAFSA. Browser automation isn't a shortcut around a slower official path, it is the only path.
- **Realistic autonomous success on an unseen multi-page form with file uploads: 15-35%.** The honest benchmark isn't WebVoyager (saturated, ~90%+, gamed). It's Online-Mind2Web, where those same agents collapse to 40-61% on *simpler* live tasks, and OSWorld 2.0, where the best frontier system completes **20.6%** of long-horizon tasks. A scholarship application is exactly a long-horizon task.
- **The worst failure mode is silent.** Agents report success while a required field was skipped or a file didn't attach. For a deadline-driven product, an application the student believes was submitted but wasn't is catastrophic and unrecoverable.
- **Essays are a hard exclusion.** 85% of top-20 universities now require AI-use disclosure; scholarship programs run perplexity analysis to detect it. Undisclosed AI essays get awards **revoked**. Auto-generating essays would be building a machine that disqualifies your own users.
- **The Chrome extension model beats cloud headless on every axis** that matters here: bot detection (real user, real IP, real fingerprint), 2FA (codes land on the student's own phone), cost (no browser-hour billing), and liability (SSNs and tax docs never touch your servers).

**Cost per completed application: ~$2-4.50** with good engineering, $5-10+ without. At $10/mo, an active student in deadline season loses you money. The economics only close if a **record-once-replay-many cache** does most of the volume: an agent explores each portal once, emits a reusable deterministic Playwright script, and every subsequent student on that portal replays it for ~$0.05. That cache, not the LLM, is the actual product.

### 3. Legal, one bright line, one favorable surprise

**The bright line.** Federal Student Aid's own rule states a user "may not authorize a third party to use their User ID, password, or credentials, **including through a power of attorney**." That clause specifically pre-empts the consent architecture you'd otherwise use as a defense. **Any feature touching studentaid.gov with a student's FSA ID is permanently off the table**, no consent language cures it. ED and FinCEN launched a coordinated student-aid fraud crackdown in July 2026, and "many students' FSA IDs accessed from one automation platform" is precisely the signature it's built to catch.

**The favorable surprise.** In *Amazon v. Perplexity*, the **Ninth Circuit vacated Amazon's injunction this month** (August 2026), holding that an AI agent acting on a user's instructions with the user's own credentials is "a tool acting on the user's instructions," not an unauthorized visitor under the CFAA. This is the strongest available precedent for driving the student's own logged-in browser. Caveats: it's a preliminary-injunction reversal, not a final merits win, and breach-of-contract/ToS claims survive it entirely.

**Other hard constraints:**
- Every scholarship platform ToS surveyed prohibits automated access. Assume this universally.
- **Never build CAPTCHA circumvention.** It's independent DMCA §1201 exposure and, unlike CFAA, the "user authorized me" defense does not apply.
- E-SIGN makes an agent's actions **legally attributable to the student**. If the AI checks "I certify under penalty of perjury," that's the student's certification and the student's exposure. Per-application human review of every attestation is not a nice-to-have.
- CFPB fined a paid FAFSA-prep company **$5.2M** for exactly the subscription-billing pattern this product would default to. Build to ROSCA + CA AB 2863 + NY GOL §5-903 from day one.
- Counsel-reviewed launch package (ToS, privacy policy, consent architecture, GLBA security program, FTC marketing review): realistically **$15-40K**.

### 4. Data, the one place with a real, unexploited edge

This was expected to be the fatal bottleneck. It isn't.

- **IRS Form 990-PF is a free, legal, systematic goldmine.** Private foundations must itemize every grant paid, recipient, purpose, exact amount, in Part XV. GivingTuesday maintains a **live S3 data lake** of standardized 990 XML (the IRS's own AWS dataset froze in 2021). Filter by education/scholarship NTEE codes and you systematically surface thousands of small local grantors that no aggregator has hand-catalogued, because it doesn't serve their ad-supported volume model.
- **The "1.5M-3.7M scholarships" claims are inflated.** Realistic count of distinct, currently-open US scholarships: **50,000-150,000**. The rest is duplicates, dead listings never pruned, and one national program sliced 50 ways.
- **Scraping the incumbents is the worst path available**, Fastweb and Scholarships.com both 403 automated requests, they'll fight it, and it's the highest legal risk for the lowest-quality data. Build from primary sources instead. Facts (amount, deadline, GPA floor) aren't copyrightable under *Feist*; the provider's marketing prose is, extract structured facts, never republish their text.
- **90 days, two people, and low hundreds of dollars in API spend** gets you 15,000-20,000 verified, deduplicated, scam-filtered, currently-open records. The constraint is engineering hours, not data availability or licensing cost.

---

## What actually survives

Strip out everything the research kills, and a coherent product remains:

**1. Expected-value-per-effort ranking, the feature nobody offers.**
Coca-Cola Scholars: ~100,000 applicants for 150 awards. A **0.15% win rate** on an essay-heavy application. A local Rotary scholarship might have 12 applicants. Every existing tool sorts by award size, pushing students toward the worst possible odds. Ranking by `award × P(win) ÷ effort required` inverts this, and it's only possible if you have the local long-tail data, which the 990-PF pipeline gives you and the incumbents don't have.

**2. Human-confirm autofill, not autonomous submission.**
The AI fills every field, attaches every document, and shows the student a structured diff of exactly what's about to be submitted. The student clicks submit in their own browser. This converts a 15-35% raw autonomous success rate into something trustworthy, catches the silent-failure mode, tracks the *Perplexity* "tool acting on user instructions" framing, and keeps every perjury attestation in front of a human. It's slightly less magical and dramatically more defensible.

**3. The replay cache as the real moat.**
Not the database, that's the weakest possible moat and the layer general AI erodes fastest. The moat is (a) the portal field-map library that makes submission reliable and cheap, and (b) **submission outcome telemetry**: which applications actually win. A stateless ChatGPT session can never accumulate either.

**4. Sell through independent educational consultants, not to students.**
IECs bill $140-400/hour and serve 20-100 client families each. 2,800 IECA members is a directly addressable list. Forty seats at $79/mo is $3,160 MRR from forty relationships, versus ~16,700 consumer signups for the same money. Students are the volume engine; IECs are the revenue engine.

---

## The option you should seriously consider

Three of the five research agents independently flagged the same thing: **the identical technology stack, eligibility matching plus agentic form-filling, sold to nonprofits seeking grants instead of students seeking scholarships is a structurally better business.**

| | Students | Nonprofits seeking grants |
|---|---|---|
| ACV | $79/yr | **$2,148-5,988/yr** (Instrumentl: $179-499/mo) |
| Seasonality | 7-month window, dead Jun-Sep | Year-round grant cycles |
| Max customer lifetime | ~4 years | Indefinite |
| Minors / FERPA / COPPA | Yes | **No** |
| FAFSA bright line | Yes | **No** |
| FTC scam-category baggage | 30 years of it | **None** |
| Willingness to pay | Unsolved for 25 years | **Proven** |
| Buyer | Broke 17-year-old | Org with a grants budget |

Same matching engine. Same agentic form-fill. Same 990 data pipeline, pointed at funders instead of scholarships. Roughly 30x the revenue per customer, and every legal landmine in this memo disappears.

You asked about students, so this isn't a recommendation to abandon that. But it would be dishonest not to put it in front of you before you spend three months building.

---

## Recommended next step: a 4-week validation sprint

No product code. Three assumptions, each of which can kill the idea, ordered cheapest-first.

### Test 1, Does the data edge actually exist? (Week 1, ~$50)
Build the 990-PF extraction against GivingTuesday's S3 data lake, filtered to **Manatee and Sarasota counties only**. Target: 200-400 verified local scholarships.
- **Pass:** you find 100+ real, currently-open local awards that do *not* appear in Fastweb, Scholarships.com, or Bold.org.
- **Fail:** the incumbents already have them. Kill the data-moat thesis; the whole product is a commodity.

### Test 2, Does the agent actually work? (Weeks 2-3, ~$200)
Hand-catalog 30 real scholarship portals across the common backends (Blackbaud, AwardSpring, SmarterSelect, Google Forms). Build a throwaway extension-driven agent. Fill, **never submit**, all 30 and measure per-field accuracy and cost.
- **Pass:** >70% of fields correct with human review, under $3/application.
- **Fail:** unit economics don't close at any consumer price point. Product is dead as designed.

### Test 3, Will anyone pay? (Weeks 3-4, $0)
Two parallel probes, both founder-time only:
- Cold-outreach 30 IECs from the IECA directory. Offer free access for a 20-minute call. Ask the willingness-to-pay question directly at $79/mo.
- Show 20 local families (church, community org, school contacts) the Test 1 output, *their* kid's actual matched local scholarships, ranked by EV-per-effort, and ask for $79/yr.
- **Pass:** ≥5 IECs say yes to paid pilot, or ≥3 families pay real money.
- **Fail:** this is a free product forever. Everyone else already learned this.

**Kill criteria:** any test fails → stop, or pivot to the nonprofit-grants version, which reuses Tests 1 and 2 almost entirely.

Only after all three pass is it worth spending the $15-40K on legal and building the real thing.

---

## Never build these

Not "risky." Off the table.

1. **Anything using a student's FSA ID on studentaid.gov.** ED's rule voids the consent defense explicitly, POA included.
2. **CAPTCHA circumvention.** Independent DMCA §1201 exposure with no user-authorization defense.
3. **Autonomous submission of perjury attestations.** Every certification gets shown verbatim to the student, who clicks affirm. Never batch-approved.
4. **AI-generated essays submitted as the student's own work.** Gets your users' awards revoked.
5. **"Guaranteed scholarships," money-back guarantees, or "you can't find this anywhere else."** These are verbatim items on the FTC's published scam red-flag list.
6. **Success fees (% of scholarship won)** and **lead-gen to student lenders** as the founding revenue model. The former is unenforceable and trust-poisoning; the latter is how Scholly and Going Merry actually monetized, and both are now cautionary tales.

---

## Files

Nothing implemented yet, this is pre-build. If you want this memo committed for reference, it belongs in a new standalone repo, not `helpcoai.github.io`, since this is a separate business.

---

# Addendum (2026-08-06, after founder clarification)

## The clarified product

**One master profile → autofill the repeated fields on every scholarship form → student writes their own essay and clicks submit.** No AI essays, no autonomous submission. This is exactly the defensible configuration this memo recommends, the Simplify model (1M+ installs, 4.9 stars) rather than the LazyApply model (2.4 stars, platform bans). Every legal bright line above is respected by that design.

**Shape:** web app (profile, matched scholarships, deadlines, tracking, works on any phone browser) + Chrome extension (does the filling, inside the student's own logged-in session). Mobile app later if there's traction. No downloadable desktop software, nothing about this needs local compute. Pricing ~$6-10/mo equivalent, sold via own site with Stripe to avoid the 15-30% app-store cut.

**Data security posture** (also the marketing pitch): store the profile only, encrypted. Never store portal passwords, the student logs in themselves and the extension fills fields inside their session. Never collect full SSN. Documents stay on-device at first. Never sell data to lenders or advertisers, the exact thing this category keeps getting burned for.

**Rejected:** entering the job-application autofill market (crowded, free-dominated, platform-hostile).

## Correction on Instrumentl (verified 2026-08-06)

Instrumentl launched **"Apply"** (AI proposal drafting from your past applications) and a **Prospecting Assistant** (plain-language project description → matched funders with rationale) in 2025. They now cover discovery, tracking, AND drafting, 400K+ funder profiles, 33K+ active RFPs. The earlier "Instrumentl finds them, we finish them" differentiation is largely gone.

What remains for a nonprofit-version wedge: (a) **price segment**, their floor is $179/mo, leaving small nonprofits under ~$500K budget unserved at $49-99/mo; (b) **actual submission**, Apply drafts text, the nonprofit still copies it into the funder's portal by hand; (c) **local depth + done-with-you service**. Thinner edge than originally assessed.

---

# GAMEPLAN: Test 1, Does the local data edge exist?

**Why this first:** cheapest, fastest, most decisive, requires talking to nobody (addresses the idea-theft concern), and its output serves *both* the student and nonprofit versions, 990 data is funder data. If this fails, everything downstream is a commodity and we stop before spending real money.

**Critical discipline: do NOT build the pipeline yet.** Produce the first ~60 records semi-manually to see whether the data is actually there. Automate only after the signal is confirmed. Building infrastructure before knowing the answer is how three months disappear.

## Method

**Step A, Candidate discovery (free, no API key).**
Use the ProPublica Nonprofit Explorer API (public, keyless) rather than parsing the full bulk 990 corpus, dramatically faster to a first signal at county scale. Query Florida organizations with scholarship-related NTEE codes (B82 Scholarships/Student Financial Aid, plus adjacent B- and T-codes) filtered to Sarasota/Manatee cities: Sarasota, Bradenton, Venice, North Port, Palmetto, Osprey, Nokomis, Lakewood Ranch, Parrish, Ellenton, Longboat Key, Anna Maria, Holmes Beach.

Also seed known aggregator-entities directly: Community Foundation of Sarasota County, Manatee Community Foundation, local Rotary/Elks/Kiwanis/Lions chapters, Achieva and Suncoast credit unions, chambers of commerce, hospital and bar-association foundations. Community foundations are force multipliers, one filing can reveal 20-50 named scholarship funds.

**Step B, Financial verification.**
For each candidate, pull 990/990-PF data: does it actually pay scholarship grants to individuals, and how much? Drop the ones that don't. Separates real grantmakers from name-only matches.

**Step C, Application details.**
Fan out parallel research agents over surviving candidates to fetch each organization's website and extract: award amount, deadline, eligibility, application URL, essay required, currently open. Flag any upfront fee (scam filter).

**Step D, The competitive check, this is the actual test.**
For each verified local award, check whether it appears on Fastweb, Scholarships.com, or Bold.org. Those sites block automated fetching, so verify via search-engine queries on exact scholarship names. **The count that matters: verified, currently-open, local, and NOT on the big three.**

**Step E, Dual-purpose tagging (add-on, ~20% extra effort).**
While parsing the same filings, tag *both* grant directions. Form 990 Schedule I splits them: Part II = grants to organizations, Part III = grants to individuals. Part III feeds the student product (scholarships); Part II feeds the nonprofit product (local funders who fund nonprofits). Same download, same parser, same enrichment, only the filter and output schema differ. Produces a starter funder list for the nonprofit route at near-zero marginal cost, and hints at whether local funder data is also thin on Instrumentl.

## Deliverable

Two tables:
1. **Scholarships**, name, sponsor, amount, deadline, eligibility, application link, and present/absent on Fastweb / Scholarships.com / Bold.org.
2. **Local funders**, foundation, EIN, what they fund, typical grant size, recent grantees (starter data for the nonprofit route).

Plus a written verdict on whether the method scales beyond two counties.

Secondary value: table 1 is showable to a local family *without revealing the method*. A soft version of the payment test with zero disclosure risk.

## What this does and does not prove

**Transfers to both routes:** the ingestion pipeline, parser, entity resolution, website enrichment, scam filter, roughly 70% of the technical foundation. Instrumentl's own database is built from this same source.

**Decisive for the student route only.** The question "do local scholarships exist that the big aggregators miss?" is a student-market question. The nonprofit equivalent, "will small nonprofits pay $99/mo for a cheaper Instrumentl?", is a pricing/segment question that data mining cannot answer. Its true first test is **10 conversations with small local nonprofits** about current tooling and willingness to pay. That route cannot skip customer conversations the way the student route can defer them.

## Pass / fail

- **50+ verified local awards not on the big three** → data moat is real. Proceed to Test 2.
- **20-50** → ambiguous. Run one more metro before committing.
- **Under 20** → incumbents already have the long tail. Student product is a commodity; pivot the pipeline to the nonprofit-grants version.

## Cost and inputs

Effectively $0, ProPublica's API is free and keyless, web fetching is free, extraction happens in-session rather than through a paid pipeline. **Nothing needed from you to run it.** An Anthropic API key matters only at the automation stage, after a pass.

## Then, in order

- **Test 2** (2-3 weeks): hand-catalog 30 real portals across Blackbaud, AwardSpring, SmarterSelect, Google Forms. Build a throwaway extension-driven filler. Fill every field, **submit nothing**. Measure per-field accuracy and cost. Pass: >70% fields correct, under $3/application.
- **Test 3** (parallel, founder-led): show the Test 1 output to 20 local families, ask for $79/yr. Show output, never method. Pass: 3+ pay real money.

No product code, no repo changes, no legal spend until all three pass.
