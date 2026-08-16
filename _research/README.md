# App market research — August 2026

Research into what makes a phone app retain and monetize, the current US App Store
picture for apps and games, the viability of ASMR as a product mechanic, and six
concrete app/game concepts scored against the evidence.

> **Not part of the website.** This directory is prefixed with `_` so Jekyll
> excludes it from the GitHub Pages build. Nothing here is published to
> helpco.ai.

## Contents

| File | What it is |
|---|---|
| `app-market-research-2026-08.html` | The report. Open it in a browser. |
| `data/us-iphone-top-free-games-daily-2026-03-12_2026-08-15.json` | 148 daily snapshots of the US iPhone Top Free Games chart |
| `data/us-top-free-apps-monthly-2026.json` | Five monthly snapshots of Apple's US Top Free Apps RSS feed (Apr–Aug 2026) |

## Headline findings

1. **"Most addictive" and "most monetizable" point in opposite directions.**
   Hypercasual — the category ASMR games belong to — took 22.05B installs in 2025
   and produced 1% of mobile game revenue. CrazyLabs booked 73M installs against
   $2.2M of store revenue in Q3 2025.

2. **ASMR is a user-acquisition hook, not a retention mechanic.** Every top-10
   ASMR-themed game across a ten-quarter census was hypercasual. No ASMR-native
   app has ever reached commercial scale. Use it in the hook and feel slots; never
   make it the reason someone returns on day 14.

3. **The sensory impulse survived by becoming the sorting puzzle.** Sort/organise
   mechanics account for 27.3% of all US iPhone top-15 chart-time over the last
   five months, and hold #1 and #5 as of 15 Aug 2026.

4. **The games chart admits newcomers; the apps chart does not.** 86 distinct games
   passed through the top 15 in 148 days (median tenure 8 days, 42 changes at #1).
   Meanwhile 38 apps held a place in every monthly snapshot of the apps chart.

5. **Core Haptics is foreground-only**, and AirPods add 80–220ms of variable audio
   delay. Both kill a large class of otherwise obvious sensory designs.

## Provenance

The chart data in `data/` is first-hand: pulled and parsed from mirrors of Apple's
own chart feeds, cross-checked across two independent scrapers for the games chart.

Everything else is search-result synthesis of named industry sources. Outbound web
fetching was blocked by an egress policy for the whole session, so **no primary
report was opened**. Claims in the report are tagged Verified / Sourced /
Unverified accordingly. Re-verify anything tagged Sourced before committing money.

Known gap: no top-grossing/revenue rankings. The reachable mirrors carry downloads
only.

## Method

Three passes, 25 agents: eight parallel research agents (charts, engagement
mechanics, ASMR market, monetization, ASO, regulatory risk), two verification
agents tasked with refuting the chart claims, six gap-fill agents after the first
ASMR pass returned zero verified findings, three concept generators working from
different strategic angles, and six adversarial critics scoring all 18 candidate
concepts on market economics, build feasibility and day-14 user truth.
