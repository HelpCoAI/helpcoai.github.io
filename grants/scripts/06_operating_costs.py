#!/usr/bin/env python3
"""
Full operating cost model -- what it actually costs to run the site, excluding marketing.

Answers: per-user COGS, fixed infrastructure, the data-verification cron, and the
AI autofill agent (the largest and most uncertain line).

Pricing as of 2026-08. Claude Haiku 4.5 $1/$5 per MTok; Sonnet 5 $3/$15 ($2/$10 intro
through 2026-08-31). Batch API applies a 50% discount to non-latency-sensitive work.

Usage:
    python3 06_operating_costs.py
    python3 06_operating_costs.py 50000 100000   # records, users
"""

import sys

# ---------------------------------------------------------------- LLM pricing

HAIKU_IN, HAIKU_OUT = 1.00, 5.00        # $ per million tokens
SONNET_IN, SONNET_OUT = 3.00, 15.00
BATCH_DISCOUNT = 0.50


def tok(n_in, n_out, price_in, price_out, batch=False):
    c = n_in / 1e6 * price_in + n_out / 1e6 * price_out
    return c * BATCH_DISCOUNT if batch else c


# ---------------------------------------------------------------- autofill

def autofill_cost(replay_hit_rate=0.70):
    """
    Two paths. A portal seen before replays a stored field-map deterministically
    (cheap). A novel portal needs vision-guided exploration (expensive).

    The replay cache is shared across ALL users, so hit rate climbs over time --
    this is the single biggest lever on COGS.
    """
    # Replay: verify the page matches the stored map, fill, screenshot the diff
    replay = tok(8_000, 500, HAIKU_IN, HAIKU_OUT)

    # Novel: ~40 vision steps, ~1,500 tok/screenshot + history, ~300 out
    novel = tok(40 * 3_000, 40 * 300, SONNET_IN, SONNET_OUT)

    blended = replay_hit_rate * replay + (1 - replay_hit_rate) * novel
    return replay, novel, blended


def matching_cost():
    """Profile -> ranked scholarships. Embed once, rerank shortlist with an LLM."""
    embed = 0.002                                    # profile + query embeddings
    rerank = tok(15_000, 2_000, HAIKU_IN, HAIKU_OUT)  # top-40 shortlist rerank
    return embed + rerank


# ---------------------------------------------------------------- fixed costs

def verification_cost(records):
    """
    The cron that keeps data from rotting. Weekly liveness is HTTP-only.
    Monthly re-extraction is the real spend, batch-priced.
    """
    liveness = records * 52 * 0.0000_5                       # compute only
    reextract = records * 12 * tok(3_000, 600, HAIKU_IN, HAIKU_OUT, batch=True)
    return liveness, reextract, liveness + reextract


def infra_monthly(users):
    """Hosting, DB, storage, email, auth, monitoring."""
    if users < 5_000:
        return {"hosting": 20, "database": 25, "storage": 5,
                "email": 20, "auth": 0, "monitoring": 0, "misc": 10}
    if users < 50_000:
        return {"hosting": 40, "database": 50, "storage": 20,
                "email": 35, "auth": 25, "monitoring": 26, "misc": 20}
    return {"hosting": 150, "database": 200, "storage": 80,
            "email": 90, "auth": 100, "monitoring": 80, "misc": 50}


def money(x):
    return f"${x:,.0f}"


def money2(x):
    return f"${x:,.2f}"


# ---------------------------------------------------------------- report

def main(records=20_000, paid_users=10_000, apps_per_user=15):
    print("=" * 78)
    print("OPERATING COST MODEL  (excludes all marketing)")
    print(f"  {records:,} scholarship records · {paid_users:,} paid users · "
          f"{apps_per_user} applications/user/yr")
    print("=" * 78)
    print()

    # --- autofill, the dominant variable
    print("1. AI AUTOFILL AGENT  -- the largest and most uncertain line")
    print("-" * 78)
    print(f"  {'Replay-cache hit rate':<28}{'$/application':>16}{'$/user/yr':>14}{'Total/yr':>16}")
    for hit in (0.0, 0.30, 0.50, 0.70, 0.90):
        _, _, blended = autofill_cost(hit)
        per_user = blended * apps_per_user
        note = "  <- day one" if hit == 0.0 else ("  <- mature" if hit == 0.90 else "")
        print(f"  {hit:>19.0%}{money2(blended):>16}{money2(per_user):>14}"
              f"{money(per_user * paid_users):>16}{note}")
    replay, novel, _ = autofill_cost()
    print()
    print(f"  Replay path (portal seen before): {money2(replay)}/application")
    print(f"  Novel path (vision exploration):  {money2(novel)}/application  -- {novel/replay:.0f}x more")
    print()
    print("  The cache is SHARED across all users. The second student to hit a given")
    print("  AwardSpring instance replays the first student's exploration. This is why")
    print("  COGS falls as you grow -- and why the field-map library is the real asset.")
    print()

    # --- per-user
    _, _, blended = autofill_cost(0.70)
    af = blended * apps_per_user
    match = matching_cost() * 12
    print("2. PER PAID USER, PER YEAR  (at 70% cache hit)")
    print("-" * 78)
    for label, val in [("AI autofill", af), ("Matching + ranking (12 refreshes)", match),
                       ("Document storage", 0.30), ("Email/notifications", 0.15)]:
        print(f"  {label:<44}{money2(val):>12}")
    per_user = af + match + 0.45
    print(f"  {'TOTAL per paid user':<44}{money2(per_user):>12}")
    print()

    # --- fixed
    live, reext, verify_total = verification_cost(records)
    infra = infra_monthly(paid_users)
    infra_yr = sum(infra.values()) * 12
    print(f"3. FIXED COSTS PER YEAR")
    print("-" * 78)
    print(f"  Data verification cron ({records:,} records)")
    print(f"    weekly liveness checks{money(live):>34}")
    print(f"    monthly LLM re-extraction (batch){money(reext):>23}")
    print(f"    {'subtotal':<44}{money(verify_total):>12}")
    print(f"  Infrastructure ({money(sum(infra.values()))}/mo)")
    for k, v in infra.items():
        print(f"    {k:<20}{money(v * 12):>36}")
    print(f"    {'subtotal':<44}{money(infra_yr):>12}")
    print(f"  Domain, SSL, misc{money(200):>29}")
    fixed = verify_total + infra_yr + 200
    print(f"  {'TOTAL FIXED':<44}{money(fixed):>12}")
    print()

    # --- totals
    print("4. TOTAL ANNUAL OPERATING COST")
    print("-" * 78)
    variable = per_user * paid_users
    print(f"  {'Variable (paid users x per-user)':<44}{money(variable):>12}")
    print(f"  {'Fixed':<44}{money(fixed):>12}")
    print(f"  {'TOTAL':<44}{money(variable + fixed):>12}")
    print(f"  {'Per paid user, all-in':<44}{money2((variable + fixed)/paid_users):>12}")
    print()

    # --- scale table
    print("5. COST AT DIFFERENT SCALES  (70% cache hit, 20k records)")
    print("-" * 78)
    print(f"  {'Paid users':<13}{'Variable':>13}{'Fixed':>12}{'Total/yr':>13}"
          f"{'Total/mo':>12}{'$/user':>10}")
    for u in (100, 1_000, 5_000, 10_000, 50_000):
        v = per_user * u
        f_ = verification_cost(20_000)[2] + sum(infra_monthly(u).values()) * 12 + 200
        print(f"  {u:<13,}{money(v):>13}{money(f_):>12}{money(v + f_):>13}"
              f"{money((v + f_)/12):>12}{money2((v + f_)/u):>10}")
    print()

    print("6. THE HEADLINE NUMBERS")
    print("-" * 78)
    f_small = verification_cost(20_000)[2] + sum(infra_monthly(100).values()) * 12 + 200
    print(f"  Running the site with ~zero users:  {money(f_small/12)}/month  ({money(f_small)}/yr)")
    print(f"  That is the floor -- verification cron + hosting, before a single signup.")
    print()
    print(f"  At $99/yr with {money2(per_user)} per-user COGS, gross margin is "
          f"{(99 - per_user)/99:.0%}.")
    print(f"  Fixed costs are covered by {int(f_small/(99 - per_user)) + 1} paying users.")
    print()
    print("  NOTE: this excludes the ~$60k/yr content budget assumed in script 04.")
    print("  A solo operator writes that content themselves -- it is time, not cash.")


if __name__ == "__main__":
    r = int(sys.argv[1]) if len(sys.argv) > 1 else 20_000
    u = int(sys.argv[2]) if len(sys.argv) > 2 else 10_000
    main(r, u)
