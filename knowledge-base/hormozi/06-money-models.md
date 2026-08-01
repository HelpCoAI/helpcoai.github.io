# 06 — Money Models

> **Confidence note:** this is the most recent of the three frameworks (2025). The
> three-stage structure and the core metrics below are verified against public
> discussion. Where I'm reasoning from the shape of the argument rather than precise
> source detail, it's flagged inline.

## The central idea

A **money model** is the deliberate *sequence* of offers a customer moves through, designed
so that the cash a customer generates early exceeds what it cost to acquire and serve
them — fast enough that growth funds itself.

The reframe worth internalizing: most operators think about acquisition and monetization
as separate problems. They are one problem. **How you monetize determines what you can
afford to spend to acquire**, and therefore determines whether you can outbid competitors
for attention. The business that can profitably pay the most for a customer wins the
market, and how much you can pay is a function of your money model, not your ad skill.

## The metrics that run everything

**CAC — Customer Acquisition Cost.** Everything spent to acquire one customer: ad spend,
sales salaries and commission, tooling, the outreach labor. Fully loaded, not just media
spend. Understating CAC by excluding sales labor is the most common self-deception in
this whole area.

**LTGP — Lifetime Gross Profit.** Not lifetime revenue. Total gross profit — revenue minus
cost of delivery — over the customer's life. Using revenue instead of gross profit is the
second most common self-deception, and it's the one that kills companies, because it
makes an unprofitable business look like a scaling one.

**LTGP:CAC ratio.** The headline health metric.

| Ratio | Reading |
|---|---|
| < 1:1 | You lose money on every customer. Volume makes it worse. |
| 1–3:1 | Fragile. No room for error, no room to fund growth. |
| **3:1** | The commonly cited floor for a healthy business. |
| 3–10:1 | Healthy. |
| > 10:1 | You are almost certainly **under-spending on acquisition** and leaving growth on the table — or under-pricing. |

That last row is the counterintuitive one and it's important: an extremely high ratio is
not a trophy. It means you could be spending far more to acquire customers and growing
much faster. Most cautious founders sit here and mistake it for discipline.

**Payback period.** How long until a customer's cumulative gross profit repays their CAC.
This is the metric that determines *how fast you can grow*, because it determines how
quickly cash recycles. Two businesses with identical LTGP:CAC but payback periods of 30
days versus 12 months are not remotely the same business — the first can grow at almost
any rate it wants, the second needs outside capital to grow at all.

## The 30-day rule and client-financed acquisition

**Client-financed acquisition (CFA):** structure things so that gross profit collected
within the first 30 days covers the cost of acquiring the customer *and* the cost of
serving them, with margin left over.

When this holds, growth becomes self-funding: acquire a customer, get paid back inside a
month, redeploy that cash into acquiring the next one, repeat. Cash stops being the
constraint on growth. You are no longer choosing between growth and solvency.

A commonly cited target is for first-30-day gross profit to exceed roughly **2× (CAC +
cost of delivery)** — the extra margin covering variance, refunds, and the customers who
don't work out. Treat the specific multiple as a guideline rather than a law; the
principle is that you want meaningful headroom, not bare break-even, because bare
break-even collapses the moment your CAC ticks up.

The practical consequence for a subscription business is uncomfortable but important:
**pure low-priced monthly recurring revenue is a terrible money model for early-stage
growth.** If a customer pays $300/month and costs $900 to acquire, payback is three-plus
months on revenue and longer on gross profit — meaning every new customer makes your cash
position *worse* before it makes it better. Growth actively drains you. This is why
well-funded SaaS companies can grow and bootstrapped ones with identical products can't:
it's not the product, it's the payback period.

The fix is not to abandon recurring revenue. It's to **put something in front of it** that
collects real cash on day one.

## The three stages

### Stage I — Get Cash: Attraction Offers

The offer that converts a stranger into a paying customer, designed primarily to get cash
in the door and neutralize acquisition cost rather than to maximize profit. The goal is
to make the front end at least self-funding, so acquisition volume isn't capped by cash.

Common shapes:

- **Win-your-money-back offers** — pay upfront, earn it back through a defined action or
  result. Strong because the buyer's risk is low but *your* cash is real.
- **Paid diagnostics / audits / setup fees** — charge for the first step. Filters
  tire-kickers and produces day-one cash.
- **Free-plus-something** — free core, paid ancillary.
- **Discounted or trial entry into a continuity offer** — the classic, and the weakest on
  cash, because it defers everything.

Key insight: a *paid* attraction offer, even at a modest price, transforms the economics
versus a free one — not only because of the cash, but because paid customers convert to
the core offer at dramatically higher rates than free ones.

### Stage II — Get More Cash: Upsells and Downsells

**Upsells** raise gross profit per customer inside the payback window. The best upsells
solve a problem that the core offer *revealed* — which means they feel like a natural next
step rather than an extraction. Sequencing matters: the highest-converting moment for an
upsell is immediately after a purchase or immediately after a visible win, when
commitment and optimism are both at peak.

**Downsells** recover the people who said no. The principle: a "no" is usually a no *to
this configuration*, not to the outcome. So change the configuration — payment terms, a
smaller scope, a slower timeline, fewer features — while protecting the core price
integrity of the main offer. A downsell that's simply "the same thing, cheaper" trains the
market to wait for discounts and cannibalizes your main offer. A downsell that's *less
scope at proportionally less money* doesn't.

### Stage III — Get the Most Cash: Continuity

Recurring revenue: subscriptions, retainers, memberships, consumables, service contracts.
Continuity is what makes LTGP large and makes the business worth something on exit, since
recurring revenue commands far higher valuation multiples than project revenue.

But — and this is the sequencing insight that ties the framework together — **continuity
is stage three for a reason.** Its cash arrives slowly. Built as the *only* offer, it
produces the payback-period problem described above. Built *behind* an attraction offer
and upsells that fund acquisition, it becomes the compounding asset it's supposed to be.

The retention lever matters as much as the acquisition lever here: churn reduction
increases LTGP with no increase in CAC, which improves the ratio from the other direction.
A percentage point of monthly churn is worth more than most people's entire conversion-rate
optimization program.

## Applied to HelpCo AI

### The structural problem to fix

Looking at the site, HelpCo is currently shaped as a **pure Stage III business** — monthly
subscriptions to AI front-desk services, with bundles and tiers. That's a good *destination*
and a poor *starting position*, for exactly the reason above: if acquiring a Gulf Coast
HVAC company costs meaningful outbound labor or ad spend, and they pay a few hundred a
month, the payback period runs months. Every sale makes cash tighter before it makes it
better, and growth is capped by whatever cash is on hand.

### The fix: put an attraction offer in front of the subscription

**The Database Reactivation Campaign is the ideal attraction offer**, and it's already in
the service lineup (`service-database-reactivation.html`). It deserves to be promoted from
"one of thirteen services" to **the front door of the entire business.**

Why it fits the criteria almost perfectly:

- **It produces revenue for the customer in week one.** You work their existing customer
  list — people who already bought from them and already trust them — and book jobs. For an
  HVAC company with 2,000 past customers, a well-run reactivation reliably books work.
- **That means it can be priced against results the customer can see immediately**, which
  means real cash on day one rather than a deferred subscription.
- **It annihilates the time-delay term** in the value equation. First result in days.
- **It makes the guarantee cheap to honor**, because the customer is usually ahead before
  the guarantee window is halfway through.
- **It's the perfect setup for the core offer.** After reactivation floods their phone with
  calls, the very next problem is *"we can't answer all these"* — which is precisely what
  the AI front desk solves. The upsell is not a pitch; it's the obvious consequence.

That last point is worth stating plainly: **reactivation creates the exact problem the
subscription solves.** That's a textbook money model sequence, and you already own both
halves of it.

### The proposed sequence

| Stage | Offer | Cash timing | Purpose |
|---|---|---|---|
| **Magnet** | Free Missed-Call Audit | — | Proof, engagement |
| **I — Attraction** | Database Reactivation Sprint — one-time fee, guaranteed to book more than it costs | Day 0 | Covers CAC immediately |
| **II — Upsell** | AI Front Desk + Missed-Call Text-Back, sold *while their phone is ringing from the reactivation* | Day 7–14 | Raises 30-day gross profit |
| **II — Upsell** | Review Engine, sold after the first wave of completed jobs | Day 30 | Raises 30-day gross profit |
| **II — Downsell** | Missed-Call Text-Back only, at a lower tier, for those who won't do the full front desk | Day 7–14 | Recovers the no's |
| **III — Continuity** | Full monthly stack — front desk, booking, reviews, CRM, get-paid-faster | Monthly | LTGP and enterprise value |

### The numbers to instrument before scaling

You cannot run this model on intuition. Before spending on acquisition, you need to know:

1. **Fully loaded CAC**, including your own outbound hours valued honestly.
2. **Gross margin per subscription customer** — after AI/telephony API costs, which are
   real and variable. This is the number most AI-wrapper businesses get wrong, because
   usage-based upstream costs scale with the customer's success.
3. **Monthly churn**, segmented by trade. Expect it to differ sharply.
4. **30-day gross profit per new customer** across the full sequence.
5. **Payback period**, computed on gross profit, not revenue.

Then the target: **30-day gross profit > 2× (CAC + delivery cost)**. If the reactivation
sprint alone clears that, acquisition stops being cash-constrained and the only remaining
question is how many businesses you can reach — which is a Core Four problem, not a
finance problem.

### One caution specific to AI businesses

Your cost of goods sold is *usage-based and scales with customer success*. A customer whose
call volume triples is a customer whose gross margin can compress. Model this explicitly,
price with usage bands or a fair-use ceiling, and re-check gross margin quarterly. A
business that measures LTGP using last year's API prices and this year's call volumes is
measuring fiction.

> **Previous:** [05 — Lead Magnets and Scale](05-lead-magnets-and-scale.md) · **Next:** [07 — The HelpCo Playbook](07-helpco-playbook.md)
