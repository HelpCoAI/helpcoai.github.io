# The Two Channels Are Complementary, Not Competing

**Date:** 2026-08-07 · Resolves the question I flip-flopped on all day: BMF or counselor pages?
**Answer: both, and they find different awards.** This is measured, not argued.

---

## Link-following fixed the counselor channel

| | Before second hop | After |
|---|---|---|
| Pages harvested | 27 of 52 | **65** (27 seeds + 38 followed links) |
| Pages with any award data | **4 of 27** | **21 of 61** |
| Distinct named awards | ~10 | **142** |

CAP landing pages never carried the awards, they link to a bulletin. Following the top-ranked
links from each page reached them. Richest: ISPA's CAP bulletin (95 dollar amounts), Felix Varela's
January 2026 bulletin (36), MAST Academy's deadlines-by-month list (16).

The bulletins are properly structured, `Name | Amount Awarded | Deadline | Requirements`, organised
by month.

## The finding that resolves the channel question

**Counselor bulletins contain almost no service-club awards.** Across 222KB of harvested bulletin
text:

| Term | Mentions |
|---|---|
| Rotary | **0** |
| Kiwanis | **0** |
| Elks | **0** |
| Chamber of Commerce | **0** |
| Miami / Dade | 77 / 112 |
| Broward | 54 |

Zero. Not scarce, absent. Meanwhile the BMF channel finds these and nothing else: the Englewood
BPO Elks trust, Rotary Club of Hudson (19 applicants, 5 awards), Kiwanis Club of St. Petersburg,
Trinity Rotary. Those were 4 of the 6 confirmed passes in the n=15 verification sample.

**So the channels do not overlap:**

| | BMF | Counselor bulletins |
|---|---|---|
| Finds | Service clubs, memorial funds, family foundations | Regional, state and national programs |
| Geography | Town and lodge level | County, state, national |
| Odds | **Best**, 19 applicants for 5 awards | Worse, thousands apply |
| Robots/WAF exposure | None (bulk government file) | High |
| Deterministic | Yes | No |

The awards with the best odds, the entire premise of expected-value ranking, are the ones
counselors do not list. Dropping either channel loses half the product.

## The breadth signal works on real data

`14_award_breadth.py` was written on theory. The bulletins now confirm it:

| Award | On N bulletins | Reads as |
|---|---|---|
| Suncoast Credit Union CTE | 9 | regional, rank down |
| South Florida Business Aviation | 9 | regional |
| Minority Teacher Education | 9 | state programme |
| Dave Davis Memorial | 9 | regional |
| Mas Family | **1** | **hyperlocal, rank up** |
| Nat Moore | **1** | **hyperlocal** |
| Coke Florida Refreshing Minds | **1** | hyperlocal |

A clean separation with no human judgement and no user survey, exactly the eligible-pool proxy the
ranking needs. Dave Davis Memorial also appeared independently on Jupiter High's page in Palm Beach,
which corroborates the count across counties.

## Corrected plan

1. **Counselor bulletins**, the volume channel. 142 awards from one metro, automated, second hop
   required. Re-crawl at most annually.
2. **BMF**, the *differentiation* channel. It is the only source of the hyperlocal, best-odds
   awards that make expected-value ranking worth paying for. Deterministic and unblockable.
3. **Public winner announcements**, `num_awards` for win probability.

I argued this morning that the district channel should displace the BMF, then reversed after the
robots and WAF failures. Both positions were wrong. They collect different things.

## Accuracy note

I projected 400–600 awards from district pages, then again from counselor pages, and was wrong both
times, each projection extrapolated from a single good example (the Manatee directory, then Jupiter
High). The measured figure is **142 distinct names from Miami-Dade**, before dedupe against the 57
already extracted and before filtering out national programmes. Treat that as the realistic per-metro
yield.
