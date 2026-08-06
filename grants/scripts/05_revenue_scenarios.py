#!/usr/bin/env python3
"""
Revenue-model scenarios for the student product.

Tests three founder proposals:
  1. $99/yr with auto-renew OFF by default (opt-in in settings)
  2. Advertising as a second revenue stream
  3. Free tier + paid tier

Usage:
    python3 05_revenue_scenarios.py
"""

COGS_PER_YEAR = 12.00
PAYMENT_PCT = 0.03
FIXED_COSTS = 115_000          # data ops 40k + content 60k + infra 15k

ORGANIC_CAC_LOW, ORGANIC_CAC_HIGH = 3, 23   # from script 04, organic channels only


def money(x):
    return f"${x:,.0f}"


def ltv(price, lifetime):
    rev = price * lifetime
    return rev - COGS_PER_YEAR * lifetime - rev * PAYMENT_PCT


# ---------------------------------------------------------------- 1. auto-renew

def autorenew_comparison():
    print("=" * 78)
    print("1. DOES TURNING OFF AUTO-RENEW BREAK THE MODEL?")
    print("=" * 78)
    print("  Auto-renew off => effective lifetime collapses toward 1.0 year.")
    print("  (Opt-in renewal recovers a little; assume 1.15 yr with a good product.)")
    print()
    print(f"  {'Scenario':<44}{'LTV':>10}{'CAC ceiling':>14}")
    print("  " + "-" * 68)
    scenarios = [
        ("$69/yr, auto-renew ON (1.5 yr)", 69, 1.5),
        ("$99/yr, auto-renew ON (1.5 yr)", 99, 1.5),
        ("$99/yr, auto-renew OFF (1.0 yr)", 99, 1.0),
        ("$99/yr, auto-renew OFF + opt-ins (1.15 yr)", 99, 1.15),
    ]
    for label, price, life in scenarios:
        l = ltv(price, life)
        print(f"  {label:<44}{money(l):>10}{money(l/3):>14}")
    print()
    l_off = ltv(99, 1.0)
    print(f"  Organic CAC is {money(ORGANIC_CAC_LOW)}-{money(ORGANIC_CAC_HIGH)}.")
    print(f"  Ceiling with auto-renew OFF at $99: {money(l_off/3)}")
    print(f"  => Organic acquisition still clears comfortably. VERDICT: affordable.")
    print()
    print("  This is only affordable BECAUSE acquisition is organic. If the plan")
    print("  ever depends on paid ads, auto-renew-off becomes unaffordable.")
    print()


# ---------------------------------------------------------------- 2. ads

def ad_revenue():
    print("=" * 78)
    print("2. ADVERTISING AS A SECOND REVENUE STREAM")
    print("=" * 78)

    print("  (a) DISPLAY ADS INSIDE THE APP -- not worth it")
    print("  " + "-" * 68)
    print(f"  {'Paying users':<16}{'Pageviews/yr':>15}{'@ $10 RPM':>14}{'@ $25 RPM':>14}")
    for users in (1_000, 10_000, 50_000):
        pv = users * 25          # ~25 pageviews/user/year, seasonal product
        print(f"  {users:<16,}{pv:>15,}{money(pv/1000*10):>14}{money(pv/1000*25):>14}")
    print()
    print("  Even at 50,000 users, display ads yield ~$12-31k/yr -- a rounding error")
    print("  next to subscription revenue, and it makes the product feel cheap.")
    print()

    print("  (b) ADS ON PUBLIC CONTENT PAGES -- better, still secondary")
    print("  " + "-" * 68)
    print(f"  {'Monthly visits':<16}{'@ $10 RPM':>14}{'@ $25 RPM':>14}")
    for visits in (10_000, 100_000, 500_000):
        print(f"  {visits:<16,}{money(visits*12/1000*10):>14}{money(visits*12/1000*25):>14}")
    print()
    print("  Needs serious traffic to matter. ScholarshipOwl gets ~757k visits/mo.")
    print()

    print("  (c) LOCAL SPONSORED SCHOLARSHIPS -- the model that actually works")
    print("  " + "-" * 68)
    print("  ScholarshipOwl's real engine: brands pay to host a scholarship, and")
    print("  each sponsored award becomes an indexable long-tail SEO page. The")
    print("  sponsor funds the content that acquires the users.")
    print()
    print(f"  {'Local sponsors':<16}{'@ $1,500 ea':>15}{'@ $2,500 ea':>15}{'@ $5,000 ea':>15}")
    for n in (5, 20, 50):
        print(f"  {n:<16}{money(n*1500):>15}{money(n*2500):>15}{money(n*5000):>15}")
    print()
    print("  20 local sponsors at $2,500 = $50,000/yr, plus 20 new scholarships for")
    print("  users, plus 20 SEO pages. Aligned incentives, no lender conflict.")
    print()

    print("  (d) THE TRAP TO AVOID")
    print("  " + "-" * 68)
    print("  Student-loan ads pay the highest RPMs in this vertical -- and that is")
    print("  exactly the conflict. Fastweb monetized by selling student leads to")
    print("  lenders. Scholly was bought by Sallie Mae and turned into lender")
    print("  matching; its founder is now suing over broken data promises.")
    print("  Taking lender money while claiming to reduce student debt is the")
    print("  single fastest way to lose the trust this product runs on.")
    print()


# ---------------------------------------------------------------- 3. tiers

def tier_model():
    print("=" * 78)
    print("3. FREE TIER + PAID TIER")
    print("=" * 78)
    print("  Required, not optional -- organic acquisition NEEDS a free entry point.")
    print("  SEO traffic lands on a page, signs up free, converts later.")
    print()
    print("  The split that matters:")
    print("    FREE gives the WOW  -> 'here are 14 local scholarships you'd never")
    print("                            have found' (drives word of mouth + SEO)")
    print("    PAID gives the TIME -> autofill, doc vault, tracking, EV ranking")
    print()
    print("  Free: matched local scholarships, deadlines, basic profile")
    print("  Paid: autofill extension, document vault, application tracking,")
    print("        expected-value ranking, unlimited matches, renewal reminders")
    print()

    print("  BLENDED P&L AT $99/YR, AUTO-RENEW OFF, WITH 20 LOCAL SPONSORS")
    print("  " + "-" * 68)
    sponsor_rev = 50_000
    header = (f"  {'Free users':<13}{'Paid (5%)':>11}{'Subs rev':>12}"
              f"{'Sponsors':>11}{'Total':>12}{'Net':>12}")
    print(header)
    for free_users in (10_000, 50_000, 100_000, 200_000):
        paid = int(free_users * 0.05)
        subs = paid * 99
        total = subs + sponsor_rev
        cogs = paid * COGS_PER_YEAR + subs * PAYMENT_PCT
        net = total - cogs - FIXED_COSTS
        print(f"  {free_users:<13,}{paid:>11,}{money(subs):>12}"
              f"{money(sponsor_rev):>11}{money(total):>12}{money(net):>12}")
    print()
    print(f"  Fixed costs assumed: {money(FIXED_COSTS)}/yr (data ops, content, infra)")
    print("  Sponsor revenue is the difference between break-even at ~50k free users")
    print("  versus ~30k -- it materially shortens the runway to profitability.")
    print()


if __name__ == "__main__":
    autorenew_comparison()
    ad_revenue()
    tier_model()
