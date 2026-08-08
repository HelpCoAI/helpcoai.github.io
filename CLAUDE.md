# Working notes

This file is loaded automatically at the start of every session. It exists so
that rules and hard-won lessons survive a context window, instead of being
rediscovered by repeating the mistake.

Add to it whenever something is learned the expensive way. Keep entries short and
concrete, and say *why*, because a rule without its reason gets dropped the first
time it is inconvenient.

---

## Two businesses in one repository

| | |
|---|---|
| `/` (root, `main`) | **HelpCo AI**, live at helpcoai.com. 60 hand-written HTML pages. AI receptionist and local SEO for Bradenton and Sarasota businesses. |
| `/grants/` | **Local scholarships**, in development. Crawlers, data pipeline, and an Astro site. Only on the feature branch. |

**Never write to the repository root for the scholarship project.** GitHub Pages
serves helpcoai.com from the root of `main`. Putting the scholarship site there
would take a running business offline.

---

## Writing rules

**Never use em dashes.** Not on the site, not in commit messages, not in replies.
Use a full stop, a comma, or a colon. Rewriting around one nearly always yields a
shorter sentence. `grants/site/scripts/copy-lint.mjs` fails the build on any that
reach the page, and `dedash()` in `22_build_site_data.py` strips them from
crawled data before it is rendered.

The one exception is text quoted from a sponsor. Their punctuation inside their
quotation marks is theirs.

**Say the thing, then stop.** A caveat that has already been made does not need
making again. Overcorrecting reads as hedging and buries the answer. When a
sentence is already honest and complete, adding "check with the sponsor before
assuming" makes it worse, not safer.

**No generated prose on the site.** Every user-facing sentence is assembled from
counted fields. If a claim cannot be derived from data, it does not get written.

---

## The standalone test

> Every sentence we publish must still be true when a machine lifts it out of the
> page and shows it to somebody who will never see what surrounded it.

Extraction strips caveats. If a caveat is what makes a sentence honest, the
sentence is not honest. Optimising for answer engines makes a page's *worst*
sentence expensive, because extraction picks one sentence and it need not be the
one you were proud of.

Enforced by `copy-lint.mjs`, which runs on every build. Rules: `absence-as-fact`,
`bare-total`, `eligibility-promise`, `ftc-red-flag`, `unscoped-superlative`,
`em-dash`, `invalid-json-ld`.

**A linter that cries wolf gets switched off.** The first version flagged 71
sentences to find 4 real ones. Tune for precision or the tool is worse than
nothing.

---

## Data rules for the scholarship project

**Absent means unknown, never false.** If a sponsor's page does not mention
citizenship, the field is empty. It does not mean there is no requirement.
Filtering a student *out* on an invented requirement costs them an award they
could have won, and nobody ever finds out. This is enforced in `verify()` in
`21_enrich.py` rather than merely requested in the prompt, because models default
absence to false constantly.

I have broken this rule myself, in the presentation layer, within an hour of
writing it down. Watch for it in derived counts: "27 awards do not require an
essay" was 27 *unknowns* counted as *noes*.

**`eligibility_raw` is never rewritten.** It is the audit trail and what a
student sees when they dispute a match. HTML entity decoding is allowed, because
the sponsor's page displays an ampersand and `&amp;` is its encoding, not its
text. Nothing else.

**Model confidence is not a quality filter.** Two records were kept as student
scholarships at confidence 0.92 and 0.95: an artist grant and a private high
school's own tuition aid. What fixed them was a worked example in the prompt, not
a threshold.

**Verify with the module, never a reimplementation.** A test that reimplements
the logic it is testing passes while the file is unchanged. This has happened
here more than once.

---

## Build and tooling gotchas

- **`git add a b` stages nothing when `b` is missing.** It aborts. A workflow
  step reported "no change" and silently discarded paid-for model output. Add
  paths one at a time.
- **Piping a script through `head` can kill it.** SIGPIPE arrived partway through
  a stats table and the process died before writing its CSV, leaving a stale file
  that looked current. Write output *before* reporting.
- **Astro's `getStaticPaths` runs in an isolated scope.** Module-level consts are
  not visible inside it. Fails at build time only.
- **A cancelled GitHub Actions step skips every step after it**, including the
  commit. Use `if: always()` and flush incrementally.
- **`pkill -f "astro preview"` can kill the shell running it.** Use a distinct
  port instead of killing by pattern.
- **Egress is proxied and many hosts are blocked**, including wikipedia,
  schema.org, and every scholarship competitor. `WebSearch` works, `WebFetch`
  often does not. Say which findings are second-hand.

---

## Web development notes

**Publishability is decided in one place.** `22_build_site_data.py` sets
`indexable` for every page: a county page needs 3+ awards, an award page needs 6+
populated fields and 250 characters of eligibility text. Thin pages are still
built and reachable, just `noindex`. Google's scaled-content-abuse policy is the
largest technical risk to a templated site, and the defence is refusing to
publish the thin ones.

**`indexable` is a required prop on the layout**, never a defaulted one. A silent
default is how thin pages get indexed by accident.

**The site reads a JSON snapshot, never a database.** The public pages are the
SEO asset and a database outage must not be able to take them down.

**Generate `robots.txt`, `llms.txt` and `sitemap.xml` from `Astro.site`.** A
hardcoded domain in any of them is wrong the moment the domain is chosen, and
nobody notices. The sitemap lists indexable URLs only: advertising a `noindex`
page sends two contradictory instructions about one URL.

---

## SEO, GEO and AEO

Full research and sources in `grants/docs/seo-geo-aeo.md`.

The one controlled study (Princeton, KDD 2024) found these move AI visibility:

| technique | effect |
|---|---|
| cite primary sources | up to +115% for pages ranked around fifth |
| add statistics | +30 to 40% |
| add quotations | +30 to 40% |
| fluency and readability | +15 to 30% |
| keyword stuffing | none |

Citing sources helps low-authority sites most and slightly *hurts* pages already
ranked first, which suits a new domain exactly.

Three of the four were already structural properties of this product, adopted for
honesty reasons rather than ranking ones. Citing the sponsor is the audit trail.
Statistics instead of prose is the refusal to generate filler. Quoting verbatim is
the dispute-resolution rule. **When the honest choice and the effective choice
coincide, that is worth noticing and defending.**

`MonetaryGrant` is the right schema type for a scholarship and is the one most
aggregators are not using. One `@graph` per page, not scattered script tags.
`FAQPage` questions are generated only from populated fields, because a fabricated
answer in schema is invisible to us and quotable by a model.

---

## Judgement calls to remember

- **Do not narrow the ask.** Deliver what was requested, flag concerns in a
  sentence or two, and keep building under stated assumptions.
- **Report the discount, not just the headline.** Yield has been over-projected
  here four times, always high. Give the honest number first.
- **Check the transcript instead of recalling it.** Claims about what was done
  earlier are verifiable at
  `/root/.claude/projects/-home-user-helpcoai-github-io/*.jsonl`.
- **Subagent tool calls are not recoverable.** Only their final reports come
  back, so their findings cannot be audited afterwards. Weigh that before
  treating a subagent result as measured fact.
