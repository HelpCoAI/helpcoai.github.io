# Competitive Kill-Check — All Three Legs

**Date:** 2026-08-07 · Three independent adversarial searches, each told to try to kill the idea.
**Result: all three came back negative.** Key claims re-verified first-hand before acting on them.

---

## Leg 1 — AI auto-fills scholarship forms · **DEAD**

- **[Going Merry shut down March 5, 2026](https://www.earnest.com/blog/going-merry-closing-faqs)** (verified). It did exactly this pitch —
  one profile, auto-filled into applications, one form covering many awards. Free. Reached
  **3 of 4 US high schools and 1.8M students**. Owner (Earnest/Navient) killed it anyway, no
  public reason.
- **[ScholarshipOwl's ToS bans it](https://scholarshipowl.com/terms)** — disqualifies "bots or other automated processes to
  enter." Ascent Funding's terms match.
- **Autofill is table stakes** at Bold.org, Kaleidoscope, Scholarships360.
- **The adjacent market prices it at zero.** Simplify gives job-application autofill away free and
  monetizes AI resume tailoring at $39.99/mo. The founder's no-AI-essays rule removes the only
  layer anyone charges for.

**Legal correction.** Earlier reasoning leaned on scraping precedent (hiQ v. LinkedIn). That is
wrong: scraping is *reading* public data; this is **authenticated automated writing** into another
party's system. Many no-essay awards are legally sweepstakes with enforceable anti-automation
clauses. The failure mode is a 17-year-old losing a $20,000 award — in a category with a long
FTC/BBB scam-warning history, with minors as users.

---

## Leg 2 — Local scholarships are structurally invisible · **PREMISE FALSE**

**The earlier "45 of 47 awards appear on no national database" finding tested Fastweb,
Scholarships.com, and Bold.org. It never tested Unigo.**

- **[Lemon Bay American Legion Scholarship is listed on Unigo](https://www.unigo.com/scholarships/high-school-students/scholarships-for-high-school-seniors/lemon-bay-american-legion-scholarship)** (verified) — a single-high-school
  award, one of the 47, with full eligibility and GPA bar published.
- **[Michigan's state government runs a place-based scholarship database](https://www.michigan.gov/mistudentaid/students-families/mi-scholarship-search)** (verified) — awards tied to a
  Michigan school, county, city or region, searchable by county of residence. Free. NC's CFNC
  filters by county too.
- **Going Merry filtered at school level**, not state — a filter called "show scholarships for my
  school," plus a counselor tool that let schools upload their local packets, solving the
  supply-side problem by hand-collection.
- **[Florida College Access Network](https://floridacollegeaccess.org/initiatives/local-scholarship-resources/) already publishes a county-organized statewide directory.**
- **[Scholarship America's Dollars for Scholars](https://scholarshipamerica.org/sponsors/dollars-for-scholars/find-your-chapter/)** is a 60-year-old federated network of 400+ local
  chapters on shared national infrastructure — the "national layer above local chapters."

**The acquisition graveyard:** Scholly → Sallie Mae → dead ([founder sued alleging he was fired over
data-privacy objections about minors' data](https://thenextweb.com/news/scholly-founder-sues-sallie-mae-student-data)). Going Merry → Earnest → dead. Cappex and Appily
→ EAB. Fastweb → Monster. The durable operators are governments, community foundations, and
nonprofits — not companies.

---

## Leg 3 — 990 data as proprietary discovery · **NO MOAT, AND THE DATA IS UNFIT**

- **[Candid's Foundation Grants to Individuals](https://grantstoindividuals.org/) is this product, aimed at students, 25+ years old** —
  8,500–10,000 programs with application information, filterable by "Scholarships" and "Student
  aid." **Free at ~400 Funding Information Network libraries**, which is where counselors send
  students. Premium is $1,199/yr.
- **Free 990-derived directories already rank.** [philanthropy.org's "990 Scout"](https://philanthropy.org/990/nonprofits/scholarships-and-student-financial-aid/all) publishes **12,472
  scholarship & student-aid organizations** with per-state pages. [Cause IQ](https://www.causeiq.com/directory/scholarship-organizations-list/) publishes the same by state.
- **The pipeline is free and finished.** [Grantmakers.io](https://www.grantmakers.io/search/grants/) offers open-source faceted search over 3.3M
  990-PF grant records. GivingTuesday's data lake needs no auth. ProPublica indexes 1.8M filings.

### The data does not carry what the product needs

| Filing | What it actually gives you |
|---|---|
| **990 Schedule I Part III** (public charities — Rotary, Elks, Kiwanis, VFW, memorial funds) | **Aggregate only.** Type of grant, recipient count, dollar total, valuation method. Fifty $200 scholarships appear as one line reading "$10,000." No program name, no eligibility, no deadline. ([IRS instructions](https://www.irs.gov/pub/irs-pdf/i990si.pdf), verified) |
| **990-PF Part XV Line 2** (private foundations) | The only place with application address, deadlines, restrictions — but *conditional*: foundations funding only preselected orgs skip it. Unvalidated free text: "None," "See attached," "Contact foundation." |
| **990-PF Part XV Line 3** | Last year's *winners*. Retrospective, and republishing named individual recipients is a privacy problem. |

**Staleness is fatal.** 12–18 months from fiscal year end to availability; Candid itself warns of
1.5–3 year lag. A deadline surfaced from a 2-year-old filing is wrong by definition — you would ship
expired deadlines to teenagers.

**Net:** every enrichment pass must re-scrape the org's live website anyway, at which point the 990
was only a seed list — and free seed lists already exist. The moat was imagined.

---

## What survives all three checks

1. **Expected-value ranking.** No agent found anyone ranking scholarships by win probability.
   Rotary Hudson's 19 applicants → 5 awards (26%) vs Coca-Cola Scholars (0.15%) is real and
   unsurfaced by any incumbent. **This is a feature, not a business** — it still requires the
   undefensible data layer beneath it.
2. **The hub channel finding** — real, useful, and unrefuted. But it is crawling public lists.
3. **The Going Merry vacancy** — 1-in-5 US counselors orphaned in March 2026, actively being
   contested (Your Grad Path, Cirkled In, MeritPlaybook are running the play now, in Florida).

## What this cost to learn

Three agent searches, a few hours, roughly zero dollars — against a plan that was about to spend
evenings from August to Thanksgiving. The BMF pipeline, chapter resolver, and hub analysis are
reusable if the founder pivots.

## Corrections this session, all in the same direction

1. "45 of 47 on no national database" — tested an incomplete competitor set; false for at least one.
2. Autofill framed as the differentiator — it is a free feature elsewhere and contractually barred.
3. "990 Part III = grants to individuals" — true but materially misleading; it is a single number.

All three overstated the opportunity. Weight earlier optimism in this project accordingly.
