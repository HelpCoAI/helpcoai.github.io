# Measured yield, 2026-08-08

Two independent measurements, taken different ways, land on the same number.

## Method 1 — stratified enrichment sample

40 records drawn round-robin across 40 distinct source hosts, enriched by the model.

| verdict | n |
|---|---|
| award | 9 |
| everything else (aggregate_page, not_an_award, org_grant, recognition_only) | 31 |

Hand-audited all 9. Six are correct. Three are not:

- **Harpo Foundation "Impact Award"** — a grant for *under-recognized Native American
  contemporary visual artists*. Not a student. Not Florida.
- **Christopher Columbus HS "Tuition Scholarships"** — financial aid to attend that private
  high school. Students must be "ACCEPTED AND ENROLLED" there. Not a college scholarship.
- **George Snow "Year Scholarships"** — real fund, name truncated from "Four-Year Scholarships".

Both miscategorisations are the same failure: an award whose recipient is not a college-bound
student, phrased in scholarship language. `org_grant` catches the nonprofit case; neither the
artist-grant nor the private-school-tuition case is covered yet.

**6 usable of 40 blocks = 15%.**

## Method 2 — geographic reach, over all 364 records

Independent of the model. Regex over `eligibility_raw` asking what geography each award
actually restricts to.

| reach | n | share | worth |
|---|---|---|---|
| county-restricted | 53 | 15% | the differentiated asset |
| single school | 2 | 1% | more differentiated still |
| Florida statewide | 74 | 20% | Bright Futures territory |
| no geographic restriction | 235 | 65% | Fastweb already carries these |

**55 differentiated of 364 = 15%.**

## The two methods agree: ~55 usable local awards

For comparison, Apply Tampa Bay publishes 73 across 8 counties.

## Correction: district databases are high-volume, not high-value

I previously called Pasco's district scholarship database "10-30x more efficient" because one
page produced 69 blocks. Efficient at volume; worthless at differentiation. Of its 22 deduped
records:

- 13 clearly national (Ayn Rand Institute "open to students worldwide", College Board, Truist)
- 9 statewide-or-broader (FL Eastern Star: "one of the 67 counties"; Gotham Writers course seats)
- **0 county-level or city-level**

It is a curated list of the same national awards Fastweb already indexes. The differentiated
records come overwhelmingly from the *low*-yield channel instead: 44 of the 53 county-restricted
records come from individual foundation and club pages, not from district aggregators.

That inverts the crawl strategy. Volume and differentiation live in different places, and the
cheap channel is the one that produces the commodity.
