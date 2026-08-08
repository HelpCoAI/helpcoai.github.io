# How Hubs Appear on the Site

**The question:** Pinellas Education Foundation runs 120+ named scholarships behind **one**
application. Do we list 120 awards that all link to the same form, or one hub that says "contains
120"?

**The answer: both, and the thing that decides which is a per-award property, not a global policy.**

Neither pure option survives contact with the constraints.

---

## Why "list all 120 individually" fails

**It misrepresents the work to the student.** A student who sees 120 rows in a match list believes
they face 120 applications. That is the exact fatigue this product exists to remove. Showing it that
way makes the product actively worse than the truth.

**It is the textbook scaled-content-abuse pattern.** 120 pages that differ only in a donor's name,
each saying "apply via the Pinellas common application, deadline Jan 31," is precisely what Google's
March 2024 policy targets, and the build plan already names that as the #1 technical risk to the
whole domain. Not worth it for 120 thin pages.

**It breaks the ranking math.** More on this below, but if 8 matched awards each carry 90 minutes of
effort, the hub scores as 12 hours of work instead of 90 minutes, and the single best opportunity
available to the student sorts to the bottom.

## Why "list the hub only" also fails

**It surrenders the long tail.** "Mary Fran Carroll Scholarship" is a real query with real intent.
List only the hub and the only query you compete for is "Pinellas Education Foundation
scholarships", which the foundation itself owns and will outrank you on forever. The named awards
are the queries nobody is serving well.

**It hides the eligibility that actually decides things.** Behind one application sit awards with
wildly different criteria: one is Sarasota County + 3.2 GPA, another is four named Catholic high
schools by nomination, another is a neuroscience major at one school. "120 scholarships" tells a
student nothing about which ones they can win.

---

## The rule

> **An award earns its own page when its eligibility differs from its hub's. Otherwise it is a row on
> the hub's page.**

That is the `Distinct Eligibility` checkbox in the Airtable Awards table, a reviewer judgment made
once, at verification time, that drives everything downstream.

| | Distinct eligibility | Same as hub |
|---|---|---|
| Example | "Bishop Verot senior, neuroscience major" | "The Smith Family Fund", same criteria, different donor |
| Own indexable URL | Yes | **No** |
| In the database | Yes | Yes |
| Can match a student profile | Yes | Yes |
| Where it renders | Own page + row on hub page | Row on hub page only |

The record always exists, matching needs it. What varies is whether it gets a URL Google can index.

---

## Page architecture

**The hub page is a strong page, not a stub.** `/scholarships/pinellas-education-foundation/`:

> **120+ scholarships. One application. $700,000 awarded each year.**
> Opens Oct 1 · closes Jan 31 · awards $500–$20,000 · any Pinellas County senior
> *[full table of all 120 named awards, with amounts and eligibility]*

That is dense, factual, genuinely unique content, the opposite of thin. It is also the single most
useful page on the site for a Pinellas student.

**County pages list the hub as one entry.** "Pinellas County: 120+ scholarships through one
application, plus 14 independent awards." A county page that is 120 rows of one foundation reads as
spam and buries the independent awards, which are the ones no one else lists.

**Awards with distinct eligibility get `/scholarships/{slug}/`** and link *both* to the hub page and
to the common application, always labelled: "Applied for through the Pinellas Education Foundation
common application, one form covers this and 119 others."

---

## In the product: the hub is one row, expanded

```
▸ Pinellas Education Foundation, one application, you match 8 awards
  $3,500–$18,000 · deadline Jan 31 · ~90 min · 
     Smith Family Scholarship      $2,000   your GPA + Largo HS
     Coastal Engineering Award     $5,000   your intended major
     ... 6 more
```

This is the best demo of the product's own value proposition the site will ever have: *eight awards,
one form.* It should be the first thing a free user sees.

## The ranking math, the part that is easy to get wrong

Effort attaches to the **hub**, once. Expected value **sums across matched children**.

```
hub_ev      = Σ (child.amount × child.win_probability)  for matched children
hub_effort  = hub.effort_minutes                        ← ONE application
rank_score  = hub_ev / hub_effort
```

Multiply effort by the number of matched children and you get the wrong answer by an order of
magnitude. Done correctly, **hubs rank at or near the top of nearly every student's list**, which is
right, because they genuinely are the highest-value-per-minute opportunity a student has.

**The tracker must agree.** One card, one deadline, one submission, not eight. A tracker that tells a
student to apply eight times to the same form destroys trust in one glance.

---

## Consequences worth stating

**This is consistent with giving the hub away free.** The county hub is the most useful single fact
you can hand a student, it costs nothing to surface, and paywalling public information is the
criticism this category attracts. Free tier: your county's hub plus your top matches. Paid: the
cross-hub layer, independent awards, ranking, tracker, unified deadlines.

**It bounds the page count honestly.** Florida's ~6,940 programs do not become 6,940 pages. Hub
children without distinct eligibility collapse into their parent, which is both better for the
student and the main defense against a sitewide penalty.

**One data caveat.** Many awards will share an `apply_url`. Store a `canonical_application_id` so
dedup, the tracker, and the effort model all key off the application rather than the award. Without
it, everything downstream double-counts.
