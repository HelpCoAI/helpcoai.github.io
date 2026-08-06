#!/usr/bin/env python3
"""
Unit economics for the student-facing scholarship product.

Corrects an earlier model that omitted customer acquisition cost entirely.
For a consumer product, CAC is usually the largest line -- leaving it out
made the business look far better than it is.

The central question is NOT "will students pay" -- ScholarshipOwl does ~$10.3M/yr
from ~22,000 paying subscribers, which settles that. The question is whether a
customer can be acquired for less than they are worth.

Usage:
    python3 04_unit_economics.py            # full report
    python3 04_unit_economics.py 99 2.0     # price=$99/yr, lifetime=2.0 years
"""

import sys

# ---------------------------------------------------------------- assumptions

PRICE_PER_YEAR = 69.00        # founder's proposed price
LIFETIME_YEARS = 1.5          # students apply for ~1-2 seasons, then graduate out
COGS_PER_YEAR = 12.00         # AI matching + autofill + hosting per active user
PAYMENT_PCT = 0.03            # Stripe et al.

# Fixed annual costs that do not scale per-user
DATA_OPS = 40_000             # part-time researcher: scholarship verification/freshness
INFRA = 15_000                # hosting, monitoring, tooling
CONTENT = 60_000             # organic content production (the only viable channel, see below)

# Channel cost per SIGNUP (not per paying customer) -- signups must be
# multiplied by the free-to-paid conversion rate to get true CAC.
CHANNEL_COST_PER_SIGNUP = {
    "Organic SEO / local long-tail": 0.50,
    "TikTok / YouTube organic": 1.00,
    "School & counselor distribution": 0.75,
    "Community orgs / churches / nonprofits": 0.50,
    "Meta / Instagram paid": 18.00,
    "Google Ads (scholarship keywords)": 35.00,
}

# RevenueCat 2026 State of Subscription Apps: freemium converts at 2.1-2.2%;
# hard paywalls ~12.1%; TRIAL-based flows 8-25% (this is ScholarshipOwl's model).
# The earlier 5% guess sat between the two and matched neither.
FREE_TO_PAID = 0.022          # freemium baseline -- override via argv[3]
FREE_TO_PAID_TRIAL = 0.15     # trial-based flow, midpoint of the 8-25% band


def money(x):
    return f"${x:,.0f}"


def report(price, lifetime):
    ltv_rev = price * lifetime
    ltv_cogs = COGS_PER_YEAR * lifetime
    ltv_fees = ltv_rev * PAYMENT_PCT
    ltv_gross = ltv_rev - ltv_cogs - ltv_fees

    print("=" * 74)
    print(f"UNIT ECONOMICS  --  ${price:.0f}/year, {lifetime} year average lifetime")
    print("=" * 74)
    print(f"  Lifetime revenue per customer      {money(ltv_rev):>12}")
    print(f"  Lifetime COGS                      {money(-ltv_cogs):>12}")
    print(f"  Payment processing                 {money(-ltv_fees):>12}")
    print(f"  {'Lifetime gross profit (LTV)':<34} {money(ltv_gross):>12}")
    print()
    print(f"  Break-even CAC (LTV 1:1)           {money(ltv_gross):>12}")
    print(f"  Healthy CAC ceiling (LTV:CAC 3:1)  {money(ltv_gross / 3):>12}   <-- the number that matters")
    print()

    # --- can each channel clear the bar?
    print("-" * 74)
    print(f"TRUE CAC BY CHANNEL  (assumes {FREE_TO_PAID:.0%} free-to-paid conversion)")
    print(f"  => every paying customer requires ~{int(1/FREE_TO_PAID)} signups")
    print("-" * 74)
    ceiling = ltv_gross / 3
    for channel, per_signup in sorted(CHANNEL_COST_PER_SIGNUP.items(), key=lambda kv: kv[1]):
        true_cac = per_signup / FREE_TO_PAID
        if true_cac <= ceiling:
            verdict = "VIABLE"
        elif true_cac <= ltv_gross:
            verdict = "marginal - no room for error"
        else:
            verdict = "LOSES MONEY ON EVERY CUSTOMER"
        print(f"  {channel:<42} {money(true_cac):>8}   {verdict}")
    print()

    # --- P&L at scale
    print("-" * 74)
    print("ANNUAL P&L AT SCALE  (organic-only acquisition)")
    print("-" * 74)
    header = f"  {'Paying users':<14}{'Revenue':>12}{'COGS':>11}{'Fixed':>11}{'Net':>13}{'Margin':>9}"
    print(header)
    for users in (1_000, 5_000, 10_000, 22_000, 50_000):
        rev = users * price
        cogs = users * COGS_PER_YEAR + rev * PAYMENT_PCT
        fixed = DATA_OPS + INFRA + CONTENT
        net = rev - cogs - fixed
        margin = net / rev if rev else 0
        note = "  <- ScholarshipOwl's scale" if users == 22_000 else ""
        print(f"  {users:<14,}{money(rev):>12}{money(-cogs):>11}{money(-fixed):>11}"
              f"{money(net):>13}{margin:>8.0%}{note}")
    print()

    breakeven_users = (DATA_OPS + INFRA + CONTENT) / (price - COGS_PER_YEAR - price * PAYMENT_PCT)
    print(f"  Break-even: {breakeven_users:,.0f} paying users at {money(price)}/yr")
    print()


def price_sensitivity(lifetime):
    print("-" * 74)
    print("WHAT PRICE MAKES PAID ACQUISITION POSSIBLE?")
    print("-" * 74)
    print(f"  {'Price/yr':<12}{'LTV':>10}{'CAC ceiling':>14}{'Meta paid CAC':>16}   Verdict")
    meta_cac = CHANNEL_COST_PER_SIGNUP["Meta / Instagram paid"] / FREE_TO_PAID
    for price in (69, 99, 149, 199, 299):
        ltv_rev = price * lifetime
        ltv_gross = ltv_rev - COGS_PER_YEAR * lifetime - ltv_rev * PAYMENT_PCT
        ceiling = ltv_gross / 3
        verdict = "paid works" if meta_cac <= ceiling else "organic only"
        print(f"  ${price:<11}{money(ltv_gross):>10}{money(ceiling):>14}{money(meta_cac):>16}   {verdict}")
    print()
    print("  Even at $299/yr, paid social does not clear a 3:1 bar at 5% conversion.")
    print("  Paid acquisition only works if conversion is far above 5%, or if the")
    print("  product is sold to someone who buys many seats at once (a school, a district).")
    print()


if __name__ == "__main__":
    price = float(sys.argv[1]) if len(sys.argv) > 1 else PRICE_PER_YEAR
    lifetime = float(sys.argv[2]) if len(sys.argv) > 2 else LIFETIME_YEARS
    if len(sys.argv) > 3:
        FREE_TO_PAID = float(sys.argv[3])
    report(price, lifetime)
    price_sensitivity(lifetime)

    print("=" * 74)
    print("SAME MODEL WITH A TRIAL-BASED FLOW (ScholarshipOwl's approach)")
    print("=" * 74)
    globals()["FREE_TO_PAID"] = FREE_TO_PAID_TRIAL
    report(price, lifetime)
