#!/usr/bin/env python3
"""
Florida-only build and operating scenario.

Real inputs measured from the IRS Business Master File (2026-05-28):
  113,644 registered FL nonprofits -> 15,423 scored scholarship candidates.

Models: one-time build, monthly operating cost, and P&L across user scales,
for a free + paid tier site covering every Florida county and major city.

Usage:
    python3 07_florida_scenario.py
"""

# ---------------------------------------------------------------- measured

FL_NONPROFITS = 113_644          # measured
FL_CANDIDATES = 15_423           # measured, score >= 20
TRUE_POSITIVE = 0.45             # measured in Sarasota/Manatee: 10 of 22 name-matches were real
FL_VERIFIED = int(FL_CANDIDATES * TRUE_POSITIVE)

FL_COUNTIES = 67
FL_MAJOR_CITIES = 100            # incorporated places worth a page
FL_HIGH_SCHOOLS = 1_000          # public + notable private
FL_HS_GRADS_PER_YEAR = 200_000   # the addressable pool

# ---------------------------------------------------------------- unit costs

COST_DISCOVER = 0.010            # find the org's website (search API)
COST_EXTRACT = 0.006             # LLM extraction, batch Haiku
COST_PER_CANDIDATE = COST_DISCOVER + COST_EXTRACT

VERIFY_LIVENESS_YR = 52 * 0.00005
VERIFY_EXTRACT_YR = 3 * 0.003

PRICE = 99.00
COGS_PER_PAID_USER = 3.31        # from script 06
PAYMENT_PCT = 0.03
FREE_TO_PAID = 0.03              # conservative; freemium benchmark is 2.2%, trial flows 8-25%


def money(x):
    return f"${x:,.0f}"


def money2(x):
    return f"${x:,.2f}"


def infra_monthly(users):
    if users < 5_000:
        return 80
    if users < 50_000:
        return 216
    return 750


def verification_yr(records):
    return records * (VERIFY_LIVENESS_YR + VERIFY_EXTRACT_YR)


# ---------------------------------------------------------------- report

print("=" * 78)
print("FLORIDA SCENARIO — free + paid tier, statewide")
print("=" * 78)
print()

print("MEASURED INPUTS (IRS Business Master File, 2026-05-28)")
print("-" * 78)
print(f"  Registered nonprofits in Florida        {FL_NONPROFITS:>10,}")
print(f"  Scored scholarship candidates           {FL_CANDIDATES:>10,}")
print(f"  Expected real programs (45% verified)   {FL_VERIFIED:>10,}")
print(f"  Florida counties                        {FL_COUNTIES:>10,}")
print(f"  Major cities worth a page               {FL_MAJOR_CITIES:>10,}")
print(f"  High schools worth a page               {FL_HIGH_SCHOOLS:>10,}")
print(f"  FL high school graduates per year       {FL_HS_GRADS_PER_YEAR:>10,}")
print()

# ---- startup
print("ONE-TIME BUILD COST")
print("-" * 78)
extract = FL_CANDIDATES * COST_PER_CANDIDATE
aggregators = 40 * 0.50          # district + education foundation + CF portal pages
portal_maps = 8 * 2.00           # field-map exploration for the platforms FL uses
domain = 15
legal = 0                        # ToS/privacy from a template at this stage
print(f"  Extract all {FL_CANDIDATES:,} candidates @ {money2(COST_PER_CANDIDATE)}   {money(extract):>10}")
print(f"    (website discovery {money2(COST_DISCOVER)} + LLM extraction {money2(COST_EXTRACT)})")
print(f"  Mine ~40 district / education-foundation lists      {money(aggregators):>10}")
print(f"  Build field-maps for ~8 application platforms       {money(portal_maps):>10}")
print(f"  Domain + SSL                                        {money(domain):>10}")
startup = extract + aggregators + portal_maps + domain
print(f"  {'TOTAL ONE-TIME':<52}{money(startup):>10}")
print()
pages = FL_COUNTIES + FL_MAJOR_CITIES + FL_HIGH_SCHOOLS + 1 + 50
print(f"  Static pages generated from this data: {pages:,}")
print(f"  ({FL_COUNTIES} county + {FL_MAJOR_CITIES} city + {FL_HIGH_SCHOOLS:,} high school + 1 state + ~50 major/identity)")
print(f"  Page generation cost: $0 — templated from the database")
print()

# ---- monthly
print("MONTHLY OPERATING COST")
print("-" * 78)
verify_mo = verification_yr(FL_VERIFIED) / 12
print(f"  {'Free users':<13}{'Paid':>8}{'Verify':>10}{'Infra':>9}{'COGS':>11}{'Total/mo':>12}")
for free in (0, 1_000, 10_000, 50_000, 150_000):
    paid = int(free * FREE_TO_PAID)
    cogs = paid * COGS_PER_PAID_USER / 12
    infra = infra_monthly(free)
    total = verify_mo + infra + cogs
    print(f"  {free:<13,}{paid:>8,}{money(verify_mo):>10}{money(infra):>9}"
          f"{money(cogs):>11}{money(total):>12}")
print()
print(f"  Verification is flat at {money(verify_mo)}/mo — it scales with RECORDS, not users.")
print(f"  Floor to keep the site alive with zero users: {money(verify_mo + 80)}/month")
print()

# ---- P&L
print("ANNUAL P&L  (at $99/yr, 3% free-to-paid, no sponsors, no ads)")
print("-" * 78)
print(f"  {'Free users':<13}{'Paid':>8}{'Revenue':>12}{'Costs':>11}{'Net':>12}{'Margin':>9}")
for free in (1_000, 5_000, 10_000, 25_000, 50_000, 150_000):
    paid = int(free * FREE_TO_PAID)
    rev = paid * PRICE
    costs = (verification_yr(FL_VERIFIED) + infra_monthly(free) * 12
             + paid * COGS_PER_PAID_USER + rev * PAYMENT_PCT)
    net = rev - costs
    margin = net / rev if rev else 0
    print(f"  {free:<13,}{paid:>8,}{money(rev):>12}{money(costs):>11}"
          f"{money(net):>12}{margin:>8.0%}")
print()

# break-even
fixed = verification_yr(FL_VERIFIED) + 80 * 12
contribution = PRICE - COGS_PER_PAID_USER - PRICE * PAYMENT_PCT
be_paid = fixed / contribution
print(f"  Break-even: {be_paid:.0f} paying users  "
      f"(~{be_paid/FREE_TO_PAID:,.0f} free users at 3% conversion)")
print(f"  Payback on the {money(startup)} build: {startup/contribution:.0f} paying users")
print()

# ---- market context
print("MARKET CONTEXT")
print("-" * 78)
print(f"  Florida HS graduates per year: {FL_HS_GRADS_PER_YEAR:,}")
for free in (10_000, 50_000, 150_000):
    print(f"    {free:>7,} free users = {free/FL_HS_GRADS_PER_YEAR:>5.1%} of one FL graduating class")
print()
print("  Reaching 5% of a state's graduating class is an aggressive but not absurd")
print("  target for a content site with several years of compounding SEO.")
print()

print("=" * 78)
print("SUMMARY")
print("=" * 78)
print(f"  Build the entire state, once:        {money(startup)}")
print(f"  Keep it alive, monthly, zero users:  {money(verify_mo + 80)}")
print(f"  Break even at:                       {be_paid:.0f} paying / ~{be_paid/FREE_TO_PAID:,.0f} free users")
print(f"  Net at 50,000 free users:            "
      f"{money(int(50_000*FREE_TO_PAID)*PRICE - (verification_yr(FL_VERIFIED) + infra_monthly(50_000)*12 + int(50_000*FREE_TO_PAID)*COGS_PER_PAID_USER + int(50_000*FREE_TO_PAID)*PRICE*PAYMENT_PCT))}/yr")
print()
print("  Excludes: your time, content production, and any marketing spend.")
