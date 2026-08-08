# Solo Operator Plan

**Date:** 2026-08-06 · **Constraints:** full-time job, no industry relationships, no time for cold outreach, open to selling the business.

---

## What these constraints rule out

Earlier documents in this project recommended things that do not fit an operator with a day job
and no network. Stating them plainly so they stop being suggested:

| Ruled out | Why |
|---|---|
| Local sponsor sales | Pure relationship work. High time cost per dollar. |
| The nonprofit route | Fundraising is 40-60% of a founder's time, a second job, not a side project. |
| Grant-writer business | Relationship sale into an unfamiliar vertical. |
| Customer-discovery interviews at scale | Requires calendar time that does not exist. |
| Paid acquisition | Already dead on unit economics ($120-818 per paying customer vs. an $84 LTV). |

**What survives: build once, publish, let search traffic compound.** This is the only model that
fits. It is also, independently, the model the economics already pointed to.

---

## Corrected sponsor economics

An earlier version of this project proposed $2,500-5,000 per sponsorship with $1,000-2,000 reaching
the student. That is a **40-60% administrative fee.** Charity watchdogs flag overhead above
~25-35%, and Scholarship America, the professional administrator, charges roughly 12-20%.

**Defensible structure:** *"You fund the award, $1,000 minimum, you choose the amount. We charge a
flat $750 administration fee."* Transparent, sponsor-controlled, survives scrutiny.

**Revised expectation: 20 sponsors × $750 = $15,000/yr, not $50,000.** The earlier figure was
inflated by a fee split that would not survive a thoughtful sponsor asking where the money goes.

Sponsorship is also a *later* revenue line under these constraints, it requires outreach time.
Treat it as an option once traffic exists, not a launch assumption.

---

## The product

**Free tier, the wow, and the SEO engine**
- Matched local scholarships ranked by expected value per hour of effort
- Deadline calendar and reminders
- Basic profile

**Paid tier ($99/yr, auto-renew off by default), the time savings**
- Autofill browser extension
- Document vault (transcripts, essays, recommendation letters)
- Application tracking
- ROI meter, award × estimated odds ÷ effort, shown per scholarship
- No ads
- Renewal-scholarship reminders for multi-year awards

---

## Three changes to the founder's plan

### 1. Automate data freshness before building anything pretty

**This is the failure mode most likely to kill the product quietly.** Scholarships expire, deadlines
shift, programs go dormant. A stale database is a dead product, and worse, an actively harmful one
if a student misses a real deadline because of it.

Earlier models in this project carried a **$40,000/yr human data-verification line**. That is not
available here. It has to be a cron job:

- Daily: deadline-passed auto-expiry (trivial date comparison)
- Weekly: HTTP liveness check on every source URL; flag 404s, redirects-to-homepage, content-hash changes
- Monthly: LLM re-extraction of changed pages, ~$0.006/record at Haiku batch pricing
- Confidence decay: any record not re-verified in N days shows a lower confidence score rather than
  silently presenting as current; two consecutive failures auto-suppress pending review

At 20,000 records this runs roughly **$75-90/month in API cost.** Build it first.

### 2. Ship the free tier alone

The autofill extension is the hardest, most fragile, highest-maintenance component, 26% of local
awards are paper or counselor-mediated and can never be automated at all, and every portal UI change
breaks a flow silently.

Get search traffic first. Confirm people convert. **Then** build autofill.

### 3. Know the exit math

Micro-SaaS and content businesses sell for roughly **2.5-4x annual profit** on Acquire.com and
Flippa.

| Annual profit | Realistic sale price |
|---|---|
| $30,000 | $75,000-120,000 |
| $50,000 | $125,000-200,000 |
| $100,000 | $250,000-400,000 |

Buyers want: predictable organic traffic, low owner involvement, clean books, and documented
processes. **Two things follow directly**, keep operations automated (a buyer pays more for
something that doesn't need you), and keep clean records from month one.

---

## Realistic timeline for nights and weekends

| Phase | Duration | What happens |
|---|---|---|
| **Build** | 3-6 months part-time | Data pipeline + freshness automation, matching, EV ranking, free tier, 50-100 local landing pages |
| **SEO dead zone** | 6-12 months post-launch | Traffic near zero. This phase kills most side projects. Nothing is wrong. |
| **Compounding** | Months 12-24 | Long-tail pages start ranking; traffic and signups accelerate |
| **Revenue** | Months 18-30 | Paid tier converts meaningfully; ads become worth turning on |

**Expect ~18 months before the first meaningful revenue.** That is the honest cost of the only
acquisition channel available.

Seasonality compounds it: local deadlines cluster **December-March**. Launching in April means
waiting nine months for the first real demand cycle. **Build over summer, launch by September,
catch the November-March peak.**

---

## What actually has to be true

1. **Local pages rank.** ScholarshipOwl's long tail is topical (by major/field), not geographic.
   Nobody targets "scholarships for [county] students." If this fails, there is no business.
2. **Free converts to paid at 2-5%.** Break-even is ~2,000 paying users, implying ~40,000-100,000
   free users. That is a lot of organic traffic.
3. **Freshness stays automated.** If verification becomes manual, a part-time operator cannot
   sustain it and the data rots.

Assumption 1 is testable for under $100 without building the product, see below.

---

## The first thing to do

**Ten to twenty local landing pages, built from `data/03_verified_scholarships.csv`.** Static pages,
no app, no login. "Scholarships for Sarasota County Students, 2027." Real award names, amounts,
deadlines, and links.

Add an email capture. Wait 60-90 days. Measure whether they rank.

That single test validates the entire thesis, the only channel available, for the cost of a domain
and a few evenings. If those pages rank, everything else is worth building. If they don't, no amount
of product work saves it.

---

## Honest expected outcome

A successful version of this is a **$30,000-100,000/year profit business by year two or three**,
sellable for **$75,000-400,000**. It is not a full-time income for years, and it may never replace a
salary.

Under these constraints that is the realistic ceiling, and it is a genuinely good outcome for a
side project that also happens to help families find money they didn't know existed.
