# BUILD PLAN: Scholarship Discovery Site — Tampa Bay Pilot → Florida → National

**Date:** 2026-08-07 · Supersedes prior research phases (all findings preserved in `grants/docs/`).

---

## Context

Research across ~15 agent investigations validated: (1) local scholarships are structurally absent
from national databases (45 of 47 verified local awards on none of them); (2) students/parents do
pay (ScholarshipOwl: $10.3M/yr); (3) the only viable acquisition is organic/SEO; (4) costs are
trivial. The founder now wants to build: free + paid tiers from day one, pilot in Tampa Bay +
Sarasota/Manatee, national-capable architecture, Instrumentl-style tooling adapted for students
(and preserving a future pivot to grant-writers/consultants).

## Verified numbers (re-measured this session from the IRS BMF 2026-05-28)

| Metric | Florida | Pilot (Sarasota+Manatee+Hillsborough+Pinellas+Pasco) |
|---|---|---|
| Registered nonprofits | **113,644** ✓ reproduces | 18,839 |
| Scored candidates | **15,423** ✓ reproduces | **2,472** |
| Expected real programs (45% TP) | ~6,940 | **~1,112** |
| One-time data build | $298 | **$81** |
| Monthly floor (zero users) | $87 | **$81** |
| Break-even | 11 paying | **10 paying (~350 free @3%)** |
| Static pages generated | 1,218 | ~316 |
| HS grads/yr in region | ~200,000 | ~36,500 |
| Net @ 5,000 free users | — | ~$12,900/yr |
| Net @ 10,000 free users | ~$25,100/yr | ~$26,800/yr |

Pilot candidate counts by county: Hillsborough 813, Pinellas 653, Sarasota 652, Manatee 182,
Pasco 172.

Caveats that remain unvalidated until the pilot runs: the 45% true-positive rate (22-org sample)
and the 3% free→paid conversion (benchmark, not observed).

---

## PRODUCT PLAN

### Tech stack (solo, nights/weekends, fits the $87-160/mo envelope)

**Astro 5** (static generation for public pages, SSR only under `/app/*`) + **Cloudflare Pages/Workers**
($0-5/mo, free static bandwidth) + **Supabase** ($25/mo: Postgres + Auth + RLS + Storage + pg_cron)
+ **Stripe Checkout in `payment` mode** (not subscription — matches auto-renew-off) + **Resend**
(email, free tier at launch) + **GitHub Actions** (free cron for the data pipeline) + **Plausible or
Cloudflare Analytics** (no GA on a site for 17-year-olds). Total fixed: ~$40-60/mo infra + ~$50-75/mo
verification LLM spend.

Rejected: Next.js/Vercel (complexity + bandwidth pricing aimed at problems we don't have), Neon+Clerk
(assembling what Supabase bundles), vector search (eligibility is structured — SQL WHERE clauses are
also *explainable*, which embeddings are not). Public pages are built from a data snapshot — a DB
outage must never take down the SEO surface.

### Data model — the load-bearing decision is tenancy

**Account (tenant) → Membership (user↔account, role) → Profile (beneficiary)**. Every app row carries
`account_id` + `profile_id`, enforced by Supabase RLS. v1 ships family workspaces; the same schema
serves a counselor (school account, 200 student profiles) or a grant consultant (firm account,
`profile.kind='organization'`) with zero migration. `scholarships.opportunity_type` defaults to
'scholarship' — the pivot hook. Catalog tables (scholarships, sponsors, schools) are public-read;
geography as indexed arrays (`states[]`, `counties[]`, `cities[]` + a `scholarship_high_schools`
join table); every displayed claim cites a `scholarship_sources` row (990 / sponsor page / district
list, with URL + hash + verified date).

### Page architecture and the Google-penalty defenses

Public/static: home, `/florida/{county}/` (67), city pages (~100), `/high-schools/fl/{slug}/`
(~1,000), `/sponsors/{slug}/` (990-derived profiles — Instrumentl's flagship feature as SEO pages),
`/scholarships/{slug}/`, `/methodology` (the trust + link magnet), 10-20 written guides.
App/SSR/noindex: dashboard, intake, matches, tracker, calendar, vault, profiles, billing.

Scaled-content-abuse defenses (launch criteria, enforced in the build script):
1. A geo page is indexable ONLY with ≥3 matched scholarships + ~150 words of page-specific data;
   below threshold → `noindex,follow` or don't build.
2. No spinnable text — pages lead with computed facts ("14 scholarships totaling $23,500; earliest
   deadline Dec 1") + award tables. Hand-write 2-4 local sentences for top-20 pages.
3. Tiered rollout: county + scholarship + sponsor pages first; school pages flip from noindex in
   batches. Never a sudden 1,200-page sitemap on a fresh domain.
4. JSON-LD structured data; per-type sitemaps with real `lastmod` from `last_verified`.
5. "Last verified {date}" + confidence badges rendered on every award — freshness that's real.
6. Never cloak: full scholarship listings stay public (the SEO asset); what's paid is the
   personalized layer (ranking, tracker, vault) behind auth.

### Free → Paid mechanics

Funnel: SEO page → "See which of these you qualify for" → intake (no account to see the count) →
reveal: **"We found 14 scholarships worth $23,500 for you"** (free, shareable). Account to save.

| Free | Paid $99/yr (one-time, auto-renew off) |
|---|---|
| Top 10 matches by EV/effort, fully detailed | ALL matches, full ranked list |
| Count + total $ of what's behind the line ("9 more worth $8,750") | EV-per-hour scores with visible inputs |
| Public deadline data | Deadline + renewal reminders |
| 1 profile | Up to 5 profiles (family) |
| — | Tracker kanban, vault, dashboard, essay-outline assist (P2), autofill (P2) |

Stripe: Checkout `mode:"payment"`, $99 → webhook sets `plan_expires_at = +1yr`; expiry cron
downgrades to free but **retains tracker/vault data read-only** (deleting a family's documents earns
chargebacks and grudges). Renewal = T-30/T-7 emails with a fresh checkout link. Stripe Tax on from
day one. **Refunds: 14-day no-questions, stated on the pricing page** — worth more in parent
conversion than it costs, and pre-empts chargebacks.

### Build phases (honest hours at ~10 hrs/wk; it is Aug 7)

| Phase | Calendar | ~Hours | Ships | Gate |
|---|---|---|---|---|
| **0** | Aug 10 – Sep 15 | 50 | Pilot data extracted + hand-verified (~15 hrs — measures the real TP rate), Astro site on a **bought domain** (buy it this week; github.io can't 301), ~300 pages, email capture, freshness cron v1, GSC submitted | Pages live; the SEO clock starts at deploy |
| **1** | Sep 15 – Nov 25 | 100 | Tenancy schema, intake → SQL matching + reasons, free/paid split, Stripe, tracker, reminders, vault | **First payment. Paid live by Thanksgiving** — catches the whole Dec-Mar season. Pre-committed cut order if slipping: vault → calendar view → dashboard stats. Never cut: matching, paywall, tracker |
| **2** | Dec – May | 150+ | Rest of Florida (~$300), essay-outline assist (never prose — warning in the UI), autofill extension (5 hub platforms, only after paid conversion proven), outcome-reporting loop, sponsor page-claims | GSC impressions trending; ≥1% intake→paid |
| **3** | Spring+ | — | National, state-by-state, ordered by grads × candidate density × weak local aggregators (rerun `03_compare_metros.py` as the prioritizer) | Florida conversion proven; auto-verification precision high enough to review exceptions, not records |

Design-now-for-national (cheap): state segment in URLs from day one, sharded sitemaps, snapshot-per-
state builds, parameterized cron with cost logging. Defer: counselor UI (schema-ready; build when the
first counselor emails), queues/replicas/search infra, the national verification bottleneck.

### Tiers — monetized from day one

**FREE (the wow + the SEO engine)**
- Profile → matched local scholarships: **top 10 by ROI shown free** with the headline
  "We found N scholarships worth $X for you" (total N and $X shown; list capped)
- Public landing pages: county / city / high school / sponsor profiles
- Deadline calendar (view only)

**PAID — $99/yr, one-time payment, auto-renew OFF by default (opt-in in settings)**
- Full ranked match list with expected-value-per-effort scores and the "why this matches" rationale
- Application tracker (kanban: discovered → applying → submitted → won/lost)
- Document vault (transcripts, essays, letters)
- Deadline + renewal reminders (email)
- Performance dashboard ($ applied for, $ won)
- No ads anywhere in the app
- Phase 2 add: autofill browser extension; AI essay *outline/brainstorm* assistance (never writes essays)

### Instrumentl features adapted (and the pivot they preserve)

| Instrumentl feature | Student translation | Build phase |
|---|---|---|
| Funder 990 profiles | **Sponsor profile pages** (giving history, typical award, # awards/yr — from 990s, source-cited) | 1 — they're also SEO pages |
| Prospecting Assistant | Conversational intake → matches with rationale | 1 (simple form first, conversational later) |
| Pipeline management | Application tracker kanban | 1 |
| Deadline tracking | Calendar + email alerts | 1 |
| Apply (AI drafting) | Outline/brainstorm ONLY — never essay text | 2 |
| Award management | Renewal tracking (many local awards renew 4 yrs) | 2 |
| Reporting dashboard | $ applied / $ won per profile | 1 (basic) |
| Cited outputs | Every data point links to its 990 or source page | 1 — **architectural** |
| Multi-client workspace | **Multi-profile tenancy from day one**: parent+kids now; counselor with students later; grant-writer with nonprofit clients if pivoting | 1 — **architectural** |

The tenancy model is the pivot insurance: `account → workspace → profiles`, where v1 ships
family workspaces but the same schema serves a counselor (workspace with 200 student profiles)
or a consultant (workspace with 10 nonprofit clients) without rewrite.

### Build phases (nights/weekends, ~10 hrs/wk)

- **Phase 0 (weeks 1–4):** run the $81 pilot extraction; verify a sample by hand (measures the
  real TP rate); ship ~316 static landing pages + email capture. **Live by early September.**
- **Phase 1 (weeks 5–14):** accounts, profiles, matching + EV ranking, free/paid split, Stripe
  (payment mode, not subscription), tracker, vault, reminders. **Paid tier live by mid-October —
  ahead of the Dec–Mar deadline cluster.**
- **Phase 2 (Nov–Feb, during season):** autofill extension (5 platform field-maps first),
  essay outline assist, sponsor self-serve page claims, expand to full Florida ($298 total data).
- **Phase 3 (spring, if pilot converts):** national rollout state by state, prioritized by
  waitlist emails from uncovered counties.

### Kill/continue gates
- Phase 0 gate: do the landing pages get impressions/clicks in Search Console by ~60 days?
- Phase 1 gate: does ANYONE pay $99 by January? (Break-even is 10 people.)
- If pilot TP rate << 45% or conversion << 1%, stop and reassess before Florida-wide spend.

---

## WHAT YOU'RE NOT CONSIDERING (the pre-spend checklist)

1. **Google's scaled-content-abuse policy is the #1 technical risk to this whole plan.** (March
   2024 update, actively enforced.) 316–1,218 templated pages can get the entire domain
   suppressed if they look like thin programmatic spam. Mitigations are mandatory, not optional:
   publish a page ONLY when it has ≥3 verified scholarships; `noindex` thin pages; make every
   page's data genuinely unique (real award names, amounts, deadlines — which you have); add the
   county/school pages gradually, not 1,200 in one week.
2. **You're building for minors.** 13–17-year-olds are the core user. COPPA proper applies under
   13 (just don't allow under-13 signups), but you still need: age gate, parent-friendly privacy
   policy, minimal data collection (no SSN ever — already decided), and privacy-respecting
   analytics (Plausible ~$9/mo instead of GA4). A breach of teens' data is a business-ending
   event; store the minimum.
3. **Form an LLC before taking a dollar.** Florida LLC: $125 filing, $138.75/yr annual report.
   Separate bank account from day one. Florida does not generally tax electronically-delivered
   SaaS (confirm with an accountant at tax time). This is also what makes the "clean books for a
   future sale" goal real.
4. **Check the name before you fall in love with it.** USPTO TESS search + domain + social
   handles *before* building brand equity. The scholarship space is litigious about marks
   (Scholarship America, ScholarshipOwl etc. are registered).
5. **ToS + privacy policy at launch can be templates (~$0–200), but marketing copy cannot.**
   The FTC red-flag list is specific: never "guaranteed," never "you can't find this anywhere
   else," never money-back-if-no-scholarship. One bad headline puts you in a 30-year enforcement
   pattern. Counsel review (~$5K) is a Phase 2 expense once revenue exists — the marketing-claims
   discipline is free and starts at day one.
6. **One-time payment ≠ subscription law.** $99 with auto-renew off, charged via Stripe *payment*
   mode, mostly sidesteps ROSCA/click-to-cancel/state auto-renewal statutes. If you later add
   opt-in renewal, that flow must be ROSCA-clean. Publish a simple refund policy (e.g. 14 days,
   no questions) — it cuts chargebacks, and chargebacks at scale can kill a Stripe account.
7. **Email deliverability is infrastructure.** Deadline reminders that land in spam are a broken
   product promise. Dedicated sending domain, SPF/DKIM/DMARC from day one, warm up slowly,
   transactional and marketing streams separated (Resend/Postmark, ~$20/mo).
8. **The clock: it is August 7.** Phase 0 must ship in ~4 weeks and Phase 1 by mid-October or you
   miss the Dec–Mar deadline cluster and effectively wait a year for real demand. Scope discipline
   matters more than any feature: autofill is *deliberately* Phase 2.
9. **Wrong data is worse than no data.** A student who misses a real deadline because your record
   was stale will tell everyone. Ship the confidence-decay UI (verified date on every record,
   auto-suppress after 2 failed checks) in Phase 1, not later. Show "deadline not published —
   verify with sponsor" rather than guessing. This is the trust moat *and* the liability shield.
10. **Accessibility and honesty of the paywall.** Keep every scholarship's existence and sponsor
    link visible free (arguably a public good, and it's your SEO content); charge for the
    *ranking, tooling, and time-savings*. Never paywall the fact that an award exists — that
    would both gut SEO and invite the "paywalled public info" criticism this category attracts.
11. **Your evenings are the scarce resource, and the SEO dead zone will test you.** Expect
    near-zero traffic for 6–12 months post-launch. The plan's kill-gates exist so you decide on
    evidence, not on morale, and the $81/mo floor means waiting costs almost nothing in cash.
12. **Insurance and the future sale.** Defer E&O/cyber (~$1.5–4K/yr) until there's revenue, but
    keep automated ops + clean books from month one — micro-SaaS sells at 2.5–4x profit and
    buyers pay a premium for a business that runs without its founder.

---

## Verification

- Phase 0: Search Console impressions on landing pages; hand-verify 50 extracted records against
  sponsor sites to measure the true TP rate (replaces the 45% assumption with a measured one).
- Phase 1: first Stripe payment; conversion rate measured against the 3% assumption.
- All numbers in this plan are reproducible: `grants/scripts/01…07` + the pilot scan run this
  session.
