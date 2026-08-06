# Hospital Price Transparency — Deep Dive

**Date:** 2026-08-06 · **Question:** is there a product here for a solo operator with a full-time job, no healthcare relationships, and self-serve distribution only?

---

## Verdict

**One narrow lane is open. It is not better than the scholarship business.**

Proactive price shopping is definitively dead — killed by both academic evidence and a corporate
corpse. Reactive bill review is where real behavior exists, but 8-9 near-identical AI bill-checkers
already occupy it, one with $16.3M in funding.

The genuinely underexploited mechanism: **"did this hospital bill me more than its own publicly
posted rate?"** — which none of the current competitors appears to lead with.

---

## Proactive price shopping is dead. Do not build it.

The evidence is overwhelming and consistent across independent sources:

| Finding | Source |
|---|---|
| CalPERS: **12.3%** of people offered a price tool used it once; **2.4%** used it 3+ times | [HealthExec](https://healthexec.com/topics/healthcare-management/healthcare-economics/few-patients-making-use-price-transparency-tools) |
| Aetna: tool offered to 94% of enrollees, used by **3.5%** | same |
| **1 in 10** high-deductible enrollees who *could* shop did; **no evidence of learning to shop** after two years | NBER/JAMA-adjacent |
| Price-tool access **not associated with reduced outpatient spending** | [JAMA](https://jamanetwork.com/journals/jama/fullarticle/2518264) |

**Castlight Health is the cautionary tale.** IPO'd 2014 on exactly this thesis — "consumer shops,
employer saves" — peaked near $1.7B, sold to Vera Whole Health for **$370M** in 2022 at $0.65/share,
a ~78% collapse. Healthcare Bluebook survived only by being absorbed into Vālenz Health. The
behavior the whole thesis depended on never materialized.

Note also *why* high-deductible plans reduce spending: not through shopping, but through people
**consuming less care, including valuable preventive care.**

---

## Where consumers actually engage

**After the bill arrives.** Pain is concrete, the dollar amount is known, and there's a deadline
before collections. That's why bill-negotiation and error-detection services have organic demand
while shopping tools don't.

But the honest numbers on negotiation are weaker than the industry advertises: peer-reviewed data
(AJMC) shows patients who *tried* negotiating succeeded **56%** of the time, and only **19%** of
eligible out-of-network bills were even attempted — against the 70-85% success rates vendors
market.

---

## The competitive reality

**The consumer lane is already forming into a red ocean.** At least 8-9 near-identical "upload your
bill, AI finds errors" products exist right now: Bill Shield, BillScan AI, MedBillAI, OvrCharged,
ClearBill, Defensive Health, TheBillCheck, BillReliefAI, Medical Bill Reader.

**MedBillAI has raised $16.3M.** Pricing across the category has converged on $9 one-time / $19 per
month / 20% success fee.

Meanwhile every well-funded player has moved *away* from consumers:

| Company | Raised | Sells to |
|---|---|---|
| Turquoise Health | $95M ($40M Series C, Mar 2026) | Payers, providers, health systems — consumer tool is lead-gen |
| Garner Health | ~$300M, $2.74B valuation | Self-insured employers — steerage, not transparency |
| Clarify Health | $411M | Enterprise |
| Sidecar Health | $328M | It's an insurance carrier, not a tool |
| FAIR Health | Nonprofit | Free to consumers, funded by data licensing |

**The clearest signal:** Claimable — the best-executed AI-native consumer play in the adjacent
prior-auth/denial space, backed by Mark Cuban — charges $50/case direct-to-consumer, and *their own
investor says the DTC model alone doesn't work at scale.* They make money on enterprise deals.

---

## The one lane that's arguably open

**"Did this bill exceed the hospital's own publicly posted rate?"**

Not the generic "AI finds errors" pitch. A specific, checkable claim: the hospital is federally
required to publish its rates, and you can diff the patient's itemized bill against that file,
line by line, CPT code by CPT code.

**Why this is tractable for a solo operator:**

- **A single hospital's CSV is megabytes, not terabytes.** Payer MRFs are genuinely enormous —
  Cigna network files exceed 200GB, Excellus's in-network file is ~2.5TB across ~400 files, and
  standard JSON parsers fail outright. That's a real moat favoring funded infrastructure players.
  But you don't need the national corpus. You need *one facility's file, on demand, when a customer
  brings you a bill from that facility.*
- **It sidesteps the out-of-pocket problem.** A negotiated rate isn't what you owe — that needs
  plan, deductible status, and coinsurance. But you're not computing benefits. You're asking a
  narrower, answerable question: did they bill more than they published?
- **It's a messy-public-data pipeline problem** — the exact thing already proven on the 990 data.

**Regulatory tailwind:** CMS closed the `999999999` placeholder loophole in May 2025 (over **90%**
of sampled files were using it), and a mandatory standardized schema (v3.0) takes effect
**April 1, 2026**. The files are getting more usable, not less.

### The constraint that limits it

**Only 36% of hospitals are fully compliant** (PatientRightsAdvocate, July 2025 — up from 24.5%,
but still under 4 in 10). And **only 14 hospitals have ever received a penalty.** So for roughly
two-thirds of bills, there may be no usable file to diff against. That's a hard ceiling on coverage
that no amount of engineering fixes.

Data quality is also genuinely poor where files do exist — KFF confirms rates that are
"questionably high or low," bundled episodes mapped to per-diem line items, and CMS itself says the
2025 updates won't fix all usability problems.

---

## Legal — lighter than expected

Three findings that materially lower the barrier:

- **HIPAA does not apply.** A consumer app receiving PHI because *the patient voluntarily uploaded
  it themselves* is neither a covered entity nor a business associate. You are still subject to
  state consumer health data laws (Washington's My Health My Data Act and successors), FTC Act
  Section 5, and breach notification — build with real security hygiene regardless.
- **No unauthorized-practice-of-law barrier** for reviewing a bill and drafting a dispute letter
  the patient sends themselves. The entire advocate industry operates this way without licenses.
  The line is holding yourself out as legal representation. Get it reviewed before charging money.
- **No mandatory state licensing** for patient or billing advocates. The BCPA credential is
  voluntary and reputational.

Also relevant: the CFPB rule banning medical debt from credit reports was **vacated July 11, 2025**.
The collections threat is still live, which modestly strengthens the "deal with this before it hits
your credit" pitch.

---

## Honest comparison to the scholarship business

| | Scholarships | Bill checker |
|---|---|---|
| Data | Tractable, already built, validated | Only 36% of hospitals compliant; quality poor where present |
| Competition | Structural gap — national DBs can't filter below state level | 8-9 direct competitors, one at $16.3M |
| Consumer behavior | Unproven but no graveyard | Proactive shopping has a graveyard; reactive is real but low base rate |
| Distribution | SEO on local long-tail, untargeted by anyone | SEO on bill-dispute terms, actively contested |
| Founder's proven asset | Directly reusable | Skills transfer; data does not |

**This is a plausible side-bet, not a pivot.** And with a full-time job, "secondary experiment"
realistically means "not now" — you have one evening budget, not two.

---

## If you ever test it — cheapest version

Two to four weekends, near zero cost:

1. Single-purpose tool: user uploads an itemized bill and names the hospital → pull that one
   hospital's public standard-charges CSV → line-item diff flagging charges above their own posted
   rates, duplicates, and NCCI bundling red flags.
2. One free landing page targeting long-tail SEO: *"[Hospital Name] bill overcharge checker,"*
   *"is my hospital bill wrong,"* state-specific dispute-letter content.
3. **Charge nothing** until ~20-30 real users have uploaded bills and you can see whether people
   find the flagged discrepancies credible and act on them.
4. **Kill fast** if organic traffic and upload-completion are low after 2-3 months. The base rate
   of consumers engaging with *any* healthcare cost tool is single digits — validate real usage
   before writing more code.

---

*Method caveat: WebFetch and curl blocked for most hosts by egress policy; built from WebSearch
snippets. Verify load-bearing figures before acting.*
