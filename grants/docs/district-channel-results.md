# District Channel — Actual Crawl Results

**Date:** 2026-08-07 · Two harvest runs on GitHub Actions · 9 of 17 seeds retrieved.

This supersedes the projections in `district-channel.md`, which estimated 400–600 awards from
~14 URLs at ~$0.20 and recommended this channel jump ahead of the BMF. **That recommendation was
wrong.** Here is what actually happened.

---

## 1. The region already has a free aggregator — and the school district links to it

Found inside the Pasco County Schools scholarship database, not by searching for competitors:

> **[Apply Tampa Bay](https://applytampabay.org/)** — "a free resource for college and workforce
> students in the Tampa Bay area. No login is required, and we don't ask for your personal
> information." Serves **Citrus, Hernando, Hillsborough, Manatee, Pasco, Pinellas, Polk, and
> Sarasota counties.** Personalized filters across local, regional, statewide and national awards.
> Nonprofit-hosted.

That is **all five pilot counties plus three more**, free, with filtering, endorsed enough that the
school district points students at it. The local-discovery leg of the product is occupied in exactly
the geography chosen for the pilot.

## 2. Six of the highest-value sites cannot be crawled

| Site | Result |
|---|---|
| Hillsborough Education Foundation | robots disallow |
| Pinellas Education Foundation | robots disallow |
| Pasco Education Foundation | robots disallow |
| Public Education Foundation of Manatee | robots disallow |
| LEAP Tampa Bay | robots disallow |
| Florida College Access Network *(the statewide meta-source)* | robots disallow |
| Community Foundation of Sarasota County | timed out |
| LaunchYourPlan | 1 character returned |

**Caveat on the robots results.** Python's `robotparser` sets *disallow-all* when `robots.txt`
returns 401/403 — so these six are either genuine disallows or bot-protection rejecting a
non-browser user agent. The two cases are ethically different but practically identical here: we
cannot fetch them, and we will not work around either. **The single most valuable target — FCAN's
statewide county-by-county directory, the cheap path from 5 counties to 67 — is among them.**

## 3. What did come back is contaminated and partly unusable

- **[Pasco County Schools database](https://www.pasco.k12.fl.us/scholarship_database)** (60KB, hit our
  truncation cap) — well structured: title, amount, grades, deadline, requirements, website. But it
  leads with Army ROTC and the Ayn Rand Institute. Its own text says "while most scholarships listed
  below are offered locally, there are many offered nationwide."
- **[Manatee Education Foundation](https://mefinfo.org/the-scholarship-source/)** (27KB) — the best
  result. A real directory of local service-club awards with consistent fields. Still mixes in
  national awards (ARTBA, Washington DC), and many entries read "Varies" or "view website for
  deadlines."
- **[Education Foundation of Sarasota County](https://edfoundationsrq.org/scholarships/)** (3.6KB) —
  the "Scholarships Database" is **JavaScript-rendered**. We got a search form and a handful of
  server-rendered rows. Reaching the real data needs a headless browser.
- **Zephyrhills HS counselor page** (31KB) — largely a link farm pointing students at Fastweb,
  Scholarships.com, Scholly and Scholarships360. Its local section reads "Local Scholarships will be
  posted as they become available."

The crawl did find its own next targets, which worked as designed: the Pasco district database, the
[Pasco-Hernando State College Foundation](https://phsc.academicworks.com/) (220+ endowed
scholarships behind one AcademicWorks application), and Manatee Community Foundation all came from
reading run one's output.

---

## Corrected assessment

| Claim made this morning | Reality |
|---|---|
| ~14 URLs → 400–600 awards | 9 pages retrieved; award count well below that, and not yet extracted |
| "Near 100% yield — the lists exist to be applied to" | Heavily mixed with national awards |
| "Hubs publish amounts and deadlines" | Partly. "Varies" and "see website" are common |
| "200x cheaper per award than the BMF" | Unquantified — the cost was never the obstacle; access was |
| "Crawl the FCAN meta-list first to reach 67 counties" | FCAN is robots-disallowed |
| "Promote this channel ahead of the BMF" | **Withdrawn** |

**The BMF channel is now the stronger of the two,** which inverts this morning's recommendation. It
needs no permission, has no robots problem, and — per the 58% non-B82 finding — surfaces orgs the
free directories cannot see.

## What this does to the business case

The local-discovery layer in the pilot region is free, nonprofit-run, and district-endorsed. Whatever
is left has to justify $99 on its own:

- expected-value / odds ranking (still unoccupied by anyone found so far)
- unified deadline tracking across sources
- one profile, assisted fill
- the independent awards that appear on no hub

That is a narrower bet than the plan was built on. It is not zero — Apply Tampa Bay is a search box,
not a ranking engine or a tracker — but the data moat under it is gone in this region.
