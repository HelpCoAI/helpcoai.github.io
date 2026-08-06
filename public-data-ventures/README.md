# Public Data Ventures

Side project. **Separate from the grants/scholarships work** in `../grants/`.

## The pattern being explored

The grants project proved something repeatable: **take a large, free, public, machine-readable
government dataset that nobody has productized, and build a business on the cleaning.**

The proven instance: pull the entire IRS Business Master File (1.97M nonprofits, 324MB) from
GivingTuesday's public S3 data lake in ~10 seconds, filter geographically, and surface small local
funders that Candid ($35-127/mo) and Instrumentl ($299-999/mo) structurally miss — because their
curation is built for large, well-known foundations.

This folder asks: **what other datasets have that same shape?**

## What was found

35 datasets across 9 domains, each tagged by competitive density. Full inventory with access
methods, licensing, and incumbents: **`docs/dataset-inventory.html`** (open in a browser).

### The genuinely open ones

| Dataset | What it is | Why it's open |
|---|---|---|
| **EPA ECHO** | 1.5M+ regulated facilities, inspections, violations, penalties. Free weekly bulk ZIP. | Thin commercial layer despite rising supply-chain diligence demand. EPA's registry doesn't map facilities to parent companies — **that linkage is the moat**. |
| **DOL OSHA + Wage & Hour** | 4M+ inspection/violation/penalty records since 1973, daily-updated free bulk CSV. | Almost no dedicated product layer, despite mapping directly onto insurance underwriting. Matching an establishment to the actual named-insured entity is the hard part. |
| **openFDA** | MAUDE device adverse events, FAERS drug events, all recall classes. Free REST API, no key. | No dominant commercial platform relative to its size and the legal/compliance demand around it. |
| **Federal Register + Regulations.gov** | Every proposed/final rule and public comment, daily. Free API. | Thin outside enterprise suites. Value is entirely filtering and summarization — which favors an AI-native small team. |
| **FCC ULS** | Every wireless/broadcast/spectrum license with coordinates and expirations. Free daily bulk. | Only small scraper-repackagers. No dominant player at the tower-leasing layer. |
| **State school report cards** | District/school test scores, funding, demographics. | GreatSchools owns consumer; no B2B layer. Cross-state school ID resolution is unsolved. |

### The ones to skip

**County property records** (ATTOM, CoreLogic, Regrid, Black Knight — mature, $10K-1M+/yr contracts).
**State business registries** (OpenCorporates, Middesk, D&B — saturated at national scope).
**Hospital price transparency** (Turquoise Health raised a $40M Series C in March 2026).
**State court records** (Trellis, UniCourt already cover the big states).
**SEC EDGAR** (sec-api.io, Intrinio, AlphaSense already repackage at $50-500/mo).

### The trap

**DMV vehicle records look public but are federally restricted** under the Driver's Privacy
Protection Act. Also flagged: county judgment records for debt collection (FCRA exposure), and
FollowTheMoney/OpenSecrets bulk data (free tier is explicitly non-commercial only).

## Access note

This environment's egress policy blocks most government hosts (sec.gov, api.sam.gov, data.cms.gov,
irs.gov, grants.gov, propublica.org). The GivingTuesday S3 data lake is reachable, which is why the
990 pipeline works here. **Endpoint behavior, rate limits, and current pricing all need
re-verification from an unrestricted network before committing engineering time.**

## Viability: five of six ideas died

Full teardown in **`docs/viability-assessment.md`**.

The top six ideas were adversarially stress-tested. **Five of six "no dominant incumbent" claims
were false** — in each case the first pass had searched the wrong category.

| Idea | Killed by |
|---|---|
| openFDA mass-tort radar | **Darrow.ai**: $63M raised, $26M revenue, 80 firms. Plus PharmaIntel, Pattern Data, LexGenius. |
| Credentialing cross-check | **Verisys and CertifyOS** already ship real-time PECOS. Plus near-certain FCRA exposure. **Refuse to build.** |
| OSHA/WHD underwriting feed | **ParseData** already sells this to workers-comp underwriters. FCRA live wire via sole proprietors. |
| BEAD broadband gap-filler | **CostQuest built the FCC's Location Fabric.** Timing window mostly closed as of mid-2026. |
| Funder warm-intro engine | **DonorSearch** ships "Inner Circle" board mapping — but bundled in $3-15K/yr suites. **Survives, narrowed.** |
| Vertical regulatory alerts | Enhesa PFAS Tracker, Metrc, mature AML RegTech — and free Federal Register alerts. **Survives, second.** |

### The lesson worth keeping

**Every one of these dies on distribution and incumbent trust, not data access.** "Strong AI
engineering, no domain expertise, no relationships" is a losing hand against trust-gated,
relationship-driven buyers — insurance underwriters, hospital credentialing offices, mass-tort
firms, telecom-infrastructure consultants.

### Verdict

**None of these beats the scholarship/grant business in `../grants/`, and it isn't close.** That
project already has the thing all six of these lack: a validated pipeline, real verified data, and
a distribution story. The funder warm-intro engine is the only genuine adjacent extension — same
990 pipeline, same nonprofit-facing distribution, same unregulated risk profile — and even it is a
*maybe*.

**Nothing here is validated. Do not build on it.**
