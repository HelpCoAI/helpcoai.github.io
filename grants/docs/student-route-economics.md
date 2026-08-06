# Student Route: Acquisition Economics

**Date:** 2026-08-06 · **Question:** can a $69/year consumer scholarship product be acquired profitably by a bootstrapped 1-3 person team?

---

## Two corrections to earlier analysis in this project

**1. "Students won't pay" was wrong.** ScholarshipOwl does **~$10.3M/yr from ~22,000 paying
subscribers** at $10-20/mo, self-funded, 36 employees. Students and parents demonstrably pay.
The dead competitors cited earlier — Scholly, Going Merry, Fastweb — were *free* products that
died from acquirer decisions, not from failing to convert. Scholly was reportedly **profitable**
at $2.99/mo before Sallie Mae bought it and made it free.

**2. The earlier P&L omitted customer acquisition cost entirely.** For a consumer product that
is usually the largest line. Corrected model: `scripts/04_unit_economics.py`.

The real question was never willingness to pay. It is: **can you acquire a customer for less
than they are worth?**

---

## The arithmetic at $69/year

| | |
|---|---|
| Lifetime revenue (1.5 yr) | $104 |
| Lifetime gross profit (LTV) | **$82** |
| Break-even CAC | $82 |
| Healthy CAC ceiling (3:1) | **$27** |
| Break-even scale | **2,094 paying users** |

### True CAC by channel

Conversion rate is the hinge. RevenueCat's 2026 benchmarks: freemium converts at **2.1-2.2%**,
hard paywalls ~12.1%, **trial-based flows 8-25%** (ScholarshipOwl's model). An earlier 5% guess
in this project matched neither.

| Channel | CAC @ 2.2% freemium | CAC @ 15% trial | Verdict |
|---|---|---|---|
| Organic SEO / local long-tail | $23 | $3 | **Viable** |
| Community orgs / churches | $23 | $3 | **Viable** |
| School & counselor distribution | $34 | $5 | Viable with trial flow |
| TikTok / YouTube organic | $45 | $7 | Viable with trial flow |
| Meta / Instagram paid | $818 | $120 | **Loses money** |
| Google Ads (scholarship keywords) | $1,591 | $233 | **Loses money** |

**Paid acquisition is dead at $69/yr under every assumption tested.** Not marginal — off by
4-100x. Education keywords are among the most expensive on Google ($40-50 CPC on degree and loan
terms) because student-loan lead-gen bids up the exact keyword space scholarship searches live in.
Meta's Q1 2026 teen-targeting restrictions made reaching students directly harder still.

Raising price does not rescue paid: even at $299/yr it fails a 3:1 bar.

### If organic works

| Paying users | Revenue | Net | Margin |
|---|---|---|---|
| 1,000 | $69,000 | −$60,070 | −87% |
| **2,094** | — | **break-even** | — |
| 5,000 | $345,000 | $159,650 | 46% |
| 10,000 | $690,000 | $434,300 | 63% |
| 22,000 *(ScholarshipOwl scale)* | $1,518,000 | $1,093,460 | 72% |

Fixed costs assumed: $40K data verification, $60K content production, $15K infrastructure.

---

## How ScholarshipOwl actually acquires — the finding that reframes this

**They are 56% paid search, 44% organic.** Not an organic-growth story. But the paid spend works
because of a structural advantage:

**Their B2B arm *is* the acquisition engine.** Brands pay ScholarshipOwl to host sponsored
scholarships (targeting "11 million Gen Z students," capturing zero-party data). Every sponsored
scholarship becomes a **unique, indexable, long-tail SEO page** — which is why their top organic
keywords include things like "nebraska speech pathology scholarships." Sponsors literally pay them
to create the content that ranks and pulls in students.

That is a two-sided flywheel: B2B revenue funds consumer acquisition, and consumer scale is what
they sell to B2B. A 1-3 person shop cannot replicate it without its own sponsorship sales motion.

Two more things their model reveals:

- **Their $120-240/yr pricing is roughly the minimum that makes paid acquisition pencil.** Working
  backwards: a realistic blended paid CAC of $150-300 needs $110-210/yr just to break even, and
  $310-460/yr for a healthy 3:1. Their pricing is not arbitrary — it is the floor.
- **A meaningful share of revenue rides on failure-to-cancel.** Trustpilot and BBB show a heavy
  pattern of "forgot to cancel," "charged after calling to cancel," "first transaction
  non-refundable." That is a liability, not a template — and the FTC's click-to-cancel rulemaking
  is narrowing it.

Rough blended efficiency: ~9.1M annual visits → 22,000 paying ≈ **one paying customer per ~400
visits.**

---

## Pricing headroom is real

Parents spend **$3,000-15,000** across junior and senior year on test prep, essay coaching, and
admissions help. Essay coaching alone runs **$500-3,000** per season. Against that, $69/yr is a
rounding error — the constraint on price is not family budget.

**No one currently sells a one-time seasonal fee.** A $79-99 "senior year season pass" would map
to actual usage (one application cycle), sidestep the auto-renewal complaint pattern that dogs
ScholarshipOwl, and price above the level that starves acquisition. This looks like genuine white
space worth testing on its own merits.

---

## Realistic trajectory, organic-only

| Year | Paying users | Revenue |
|---|---|---|
| 1 | low hundreds | $10-30K |
| 2 | 1,000-3,000 | $70-200K |
| 3 | 3,000-8,000 | $200-550K |

A real, profitable small business — but reaching ScholarshipOwl's scale requires either a B2B
sponsorship arm or paid spend the unit economics don't currently support.

**The binding risk is runway, not demand:** can 1-3 people sustain 12-24 months of near-zero
revenue while local SEO and community trust compound?

---

## The channel that fits the mission is the one least able to pay

Worth naming honestly. TRIO, GEAR UP, and community nonprofits serve low-income, first-generation
students — perfectly aligned with reducing student debt, free to access as a distribution channel,
and **the population least likely to pay $69/yr.** Any plan should decide deliberately whether
those users are served free and subsidized by paying families, or not served at all.

---

## The differentiator holds

ScholarshipOwl's long tail is **topical** (major/field-specific, generated by sponsor pages).
It is **not hyper-geographic**. Nobody is targeting "scholarships for [county] students" — which
is exactly what this project's 990 pipeline produces, and exactly the query a family actually
types. Low individual volume means low competition; it works only at volume (dozens to hundreds
of location pages), which takes months to compound.

---

## Cheapest next test — under $1,000, a few weeks, no product

Stand up **10-20 hyper-local scholarship landing pages** ("Scholarships for [County] Students,
2027") built from the verified data already in `data/03_verified_scholarships.csv`. Add email
capture and a **$69 pre-sale or waitlist offer**. Then measure:

1. Organic ranking and traffic at 60-90 days — does the local long-tail thesis hold?
2. Waitlist-to-paid conversion — will anyone actually pay $69?
3. Real CPC/CPA from a $200-500 test budget on the least competitive long-tail terms

This validates the two assumptions everything else rests on — that local pages can rank, and that
families will pay — **before building the product.**

---

## Sources

[Latka — ScholarshipOwl revenue](https://getlatka.com/companies/scholarshipowl) · [Similarweb traffic mix](https://www.similarweb.com/website/scholarshipowl.com/) · [ScholarshipOwl for Business](https://business.scholarshipowl.com/pricing) · [Trustpilot reviews](https://www.trustpilot.com/review/scholarshipowl.com) · [WordStream — most expensive keywords](https://www.wordstream.com/articles/most-expensive-keywords) · [Meta education CPM benchmarks](https://trymesha.com/benchmark/facebook/cpm-education/) · [Meta teen ad restrictions 2026](https://www.auditsocials.com/blog/meta-teen-ad-targeting-restrictions-parental-controls-2026-age-gated-campaigns) · [Freemium conversion benchmarks](https://www.artisangrowthstrategies.com/blog/freemium-conversion-rate-benchmarks) · [Inside Higher Ed — TikTok scholarship search](https://www.insidehighered.com/news/students/financial-aid/2026/04/14/students-turning-tiktok-find-scholarships) · [Forbes — Sallie Mae acquires Scholly](https://www.forbes.com/sites/annefield/2023/08/09/sallie-mae-buys-key-assets-of-scholarship-app-scholly/) · [Going Merry shutdown](https://www.earnest.com/blog/going-merry-closing-faqs)
