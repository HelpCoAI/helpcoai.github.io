# SEO / GEO / AEO — what the research said, and what we changed

Researched 2026-08-08. Three acronyms, three different surfaces:

| | target | what wins |
|---|---|---|
| **SEO** | ranked blue links | relevance, authority, crawlability |
| **AEO** | featured snippets, AI Overviews, voice | extractable question-answer pairs |
| **GEO** | being *cited* inside ChatGPT / Perplexity / Claude answers | quotable, statistic-dense, primary-sourced text |

`brewcitymarketing.com` and `schema.org` are both blocked by this sandbox's egress
proxy, so their pages were read through search-result summaries rather than fetched
directly. Everything below that is attributed to the Princeton study comes from
secondary reporting on it, not the paper itself.

## The one piece of controlled evidence

The Princeton GEO study (Aggarwal et al., KDD 2024) tested ~10,000 queries and found
content changes that moved AI visibility **22–41%**:

| technique | effect | do we already do it? |
|---|---|---|
| **Cite primary sources** | up to **+115%** for pages ranked ~5th | **yes** — every award links the sponsor's page |
| **Add statistics** | +30–40% | **yes** — every summary is assembled from counts |
| **Add quotations** | +30–40% | **yes** — sponsor's eligibility text, verbatim |
| Fluency / readability | +15–30% | partly |
| Keyword stuffing | no effect | no |

This is the useful finding for us: **three of the four highest-yield GEO tactics were
already structural properties of the product**, adopted for honesty reasons rather
than for ranking. Citing the sponsor is the audit trail. Statistics instead of prose
is the refusal to generate filler. Quoting verbatim is the dispute-resolution rule.

The citation result also cuts a specific way — it helped pages ranked around fifth
far more than pages already ranked first. A new site with no authority is exactly
the profile that benefits.

## What Brew City Marketing does

A Milwaukee agency, useful here as a working example of how the three disciplines get
packaged in practice. Their stated approach: content structure, schema, FAQs, entity
clarity, internal linking, and page organisation, aimed at "how AI tools understand
your business, not just how search engines rank keywords". Their three pillars are
topical authority and content depth, technical SEO and structured data, and authority
signals and brand trust.

Nothing exotic. The transferable part is the *ordering*: entity clarity and structured
data before content volume — which suits a site with 137 records rather than 137,000.

## What we changed

### 1. MonetaryGrant, replacing EducationalOccupationalProgram

A scholarship is a grant of money to a person. `MonetaryGrant` carries `funder`,
`amount` (as `MonetaryAmount`) and `areaServed` natively. Trade reporting on this
vertical specifically flags `MonetaryGrant` as the type most scholarship aggregators
are **not** using — the rare case where the semantically correct markup is also the
uncontested one.

### 2. One `@graph` per page, not scattered script tags

`Organization` → `WebSite` → the page's primary entity → `BreadcrumbList` → `FAQPage`,
cross-referenced by `@id`. The page reads as one connected entity description rather
than five disconnected assertions.

### 3. FAQPage, generated only from populated fields

`faqNode()` drops any question whose answer is empty. A page with no deadline emits no
deadline question.

**This is a correctness rule, not a formatting one.** Schema is invisible to us and
quotable by a model, so a fabricated answer there is worse than a fabricated answer in
the body — nobody would ever see it to complain.

County pages answer: how many awards, largest *local* award, how many need-based, how
many with no essay, and why local beats national. Award pages answer: how much, when
is the deadline, who can apply, how long it takes.

### 4. Answer-first opening sentence

Every award page opens with a generated sentence stating what the award is, its amount,
its sponsor, its deadline and its geography — assembled from fields, never written.
That sentence is what gets extracted, and it is also what a student triaging twenty
awards wants first.

### 5. `llms.txt`, `robots.txt` and `sitemap.xml` generated from `Astro.site`

Not static files. A hardcoded domain in any of them is wrong the moment the domain is
chosen and nobody notices.

- **llms.txt** — the commonest audit failure is treating it as a second sitemap: every
  URL, no descriptions. Ours lists only pages worth fetching, describes each, and
  states the reading rules ("a blank field means the sponsor did not publish it; it
  never means the requirement is absent") so a model can quote us without
  misrepresenting the data. No AI vendor has publicly committed to reading llms.txt,
  so this is cheap insurance, not a strategy.
- **robots.txt** — GPTBot, ClaudeBot, PerplexityBot, OAI-SearchBot and Google-Extended
  are named and **allowed**. Many publishers block them. The calculation here is
  inverted: this is public information about public scholarships, students
  increasingly ask a chatbot before a search engine, and an award nobody can find
  helps nobody.
- **sitemap.xml** — indexable URLs only (148 of 251). A sitemap advertising `noindex`
  pages sends Google two contradictory instructions about one URL.

### 6. Internal linking

Award pages link four related awards (same county, then same sponsor). County pages
link five nearby counties. Deep pages were previously reachable only from one index.

## One bug this work exposed

The county FAQ originally answered *"What is the largest scholarship for Pasco County
students?"* with a **$65,000 Horatio Alger award open to the entire country**. True,
useless, and precisely the national-database answer a student can already get
anywhere — and it was the sentence an answer engine would have lifted as our summary
of the page. Now restricted to local awards: Pasco returns a $2,500 Tampa Bay Business
Coalition for the Arts scholarship.

Optimising for extraction makes a page's worst sentence far more expensive, because
extraction picks one sentence and it may not be the one you were proud of.

## Deliberately not done

- **No FAQ padding.** Only questions the data answers. Inventing five more per page
  would be the scaled-content failure mode wearing a schema costume.
- **No keyword stuffing** — measured at zero effect.
- **No `Review`/`AggregateRating` markup.** We have no reviews. Fabricating them is
  both a Google penalty and a lie.
- **No author/E-E-A-T bios yet.** Real once there is a real person behind the site;
  invented now, it is exactly the fake-expertise signal the guidelines target.

## Sources

- [Princeton GEO study, plain-English summary — DerivateX](https://derivatex.agency/blog/princeton-geo-paper-plain-english/)
- [The Princeton GEO Study: Methodology, Results and Critique — Blck Alpaca](https://blckalpaca.at/en/knowledge-base/seo-geo/geo-generative-engine-optimization/the-princeton-geo-study-methodology-results-and-critique)
- [GEO: Generative Engine Optimization (arXiv 2311.09735)](https://arxiv.org/pdf/2311.09735)
- [Brew City Marketing](https://brewcitymarketing.com/)
- [What is Answer Engine Optimization — Brew City Marketing](https://brewcitymarketing.com/ai/what-is-answer-engine-optimization-and-why-you-should-want-to-optimize-for-it/)
- [The 3 Pillars of SEO Success — Brew City Marketing](https://brewcitymarketing.com/seo/3-pillars-of-seo-success-from-a-milwaukee-seo-specialist/)
- [Structured Data for AEO and GEO: Schema Markup Guide 2026 — Kurieta](https://kurieta.com/schema-for-aeo-geo/)
- [SEO Sponsorships for Educational Opportunities — RankWithLinks](https://rankwithlinks.com/seo-sponsorships-for-educational-opportunities/)
- [The State of llms.txt in 2026 — aeo.press](https://ai.aeo.press/the-state-of-llms-txt-in-2026)
- [MonetaryGrant — Schema.org](https://schema.org/MonetaryGrant)

---

# The extraction-honesty problem

Optimising for extraction makes a page's worst sentence far more expensive,
because extraction picks one sentence and strips the context around it. The rule
that follows:

> **The standalone test.** Every sentence we generate must still be true when a
> machine lifts it out of the page and shows it to someone who will never see
> what surrounded it. Extraction removes your caveats. If a caveat is what makes
> a sentence honest, the sentence is not honest.

## This is not hypothetical — I broke it within the hour

Optimising the county pages for answer engines, I shipped:

> *"27 of the 43 awards we list do not mention an essay requirement."*

Of those 27, **zero** are known not to require an essay. All 27 are awards whose
sponsor never published the detail. The extraction pass enforces "absent means
unknown, never false". The enrichment pass enforces it in `verify()` rather than
trusting the prompt. I violated it in the presentation layer, in a sentence
written specifically to be extracted, because it was a genuinely good answer to a
question students ask.

Now:

> *"16 of the 43 awards state that an essay is required. The other 27 do not
> mention one, which means the sponsor did not publish that detail — not that
> there is no essay."*

Longer, less quotable, and true when lifted.

## The enforcement: `scripts/copy-lint.mjs`

Runs over `dist/` on every build and exits non-zero. Six rules:

| rule | catches |
|---|---|
| `absence-as-fact` | "does not require an essay" — we only know it was not published |
| `bare-total` | an aggregate dollar figure with no per-recipient anchor |
| `eligibility-promise` | "you qualify", "you are eligible" — only the sponsor decides |
| `ftc-red-flag` | "guaranteed", "can't find anywhere else", money-back-if-no-award |
| `unscoped-superlative` | "largest scholarship" with no scope for the reader to supply |
| `invalid-json-ld` | structured data that does not parse |

It lints the **JSON-LD as well as the prose**, walking the parsed object for
`name` / `description` / `text`. A false claim in schema is the least likely to
ever be noticed and the most likely to be quoted verbatim by a model.

It **excludes the sponsor's quoted eligibility text**, and that exclusion is the
point rather than a loophole. Those blockquotes are the sponsor's own words,
attributed. Rewriting them to satisfy a linter would destroy the audit trail the
product rests on. Tampa Bay BCA writing *"awarded over $280,000 to more than 102
students"* on their own page is their claim; repeating it unattributed would be
ours.

### What it found on the real site

Three genuine classes, 11 sentences:

- **The home page headline** ended *"at least $554,250 in known award value"* —
  the sum of 137 awards to 137 different people, reading as a pot one visitor
  could draw from. Now: *"individual awards of $500 to $15,000"*.
- **Nine sponsor pages** said *"worth at least $90,000 in total"*. Horatio Alger's
  is two awards to two people. Now: *"paying $25,000 to $65,000 per recipient,
  $90,000 a year across all recipients"*.
- **The essay FAQ**, above.

### Two rounds of tuning, both instructive

The first version flagged 71 sentences. Most were the sponsor's quoted text, and
most of the rest were card grids — which carry no full stops, so twenty awards
collapsed into one pseudo-sentence holding twenty dollar figures. Block-level
tags now terminate sentences before the tags are stripped.

The second version still flagged 47, nearly all a lone `$20,000.` in an award's
Amount field. Correctly labelled, not a total, not misleading. `bare-total` now
requires an aggregation cue — *total*, *together*, *combined*, *across all* —
before it fires. **A linter that cries wolf 47 times to find 4 real problems gets
switched off**, which would leave the real four shipped.
