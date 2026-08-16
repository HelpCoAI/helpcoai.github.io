# POUR — Build Prompt

**Paste everything below this line into a fresh Claude Code session on the local machine.**

---

# MISSION

You are building **Pour**, an iOS puzzle game, from scratch, with me (the human) as your
only teammate and your only pair of hands and ears. I test on a physical iPhone; you
cannot see the screen, hear the audio, or feel the haptics. Design every step around
that.

Pour is a **material-sorting puzzle**. It uses the proven water-sort / ball-sort loop
that currently sits at #1 on the US App Store free games chart, with one substantial
difference: you are not sorting *colors*, you are sorting *substances* — water, honey,
dry sand — and every substance has its own pour physics, its own **procedurally
synthesized** sound, and its own haptic texture. Nothing is a recorded audio sample.
The audio engine is the product.

Read this entire document before writing any code. It contains the research that
justifies the design decisions; do not "improve" the design in ways that contradict
the research section, because those specific mistakes are the ones that kill games in
this genre.

---

# PART 1 — WHY THIS GAME EXISTS (do not skip; this prevents drift)

This design came out of a market study of the US App Store in August 2026. The
findings below are load-bearing. Several of them are counterintuitive and you will be
tempted to violate them.

## 1.1 The chart data (first-hand, high confidence)

148 consecutive daily snapshots of the US iPhone Top Free Games chart, 12 Mar – 15 Aug
2026, pulled from mirrors of Apple's own chart endpoint and cross-checked against a
second independent scraper:

- **Sorting/organising mechanics accounted for 27.3% of all top-15 chart-time.** It is
  the single most represented mechanic on the chart.
- Top 10 on 15 Aug 2026: **1. Block Out! – Color Sort Puzzle** (Grand Games, Turkey),
  2. Smash Fest!, 3. Meowdoku!, 4. JoJo's Bizarre Adventure, **5. Magic Sort!** (Grand
  Games), 6. Roblox, 7. Bus Traffic Fever!, 8. 82-0.com, 9. Vita Mahjong,
  10. Whiteout Survival.
- Magic Sort! held a top-15 position on **all 148 days**. Block Blast!, Vita Mahjong
  and Roblox also held 100%.
- 86 distinct games passed through the top 15 in those 148 days. **Median tenure: 8
  days.** 49% of entrants lasted a week or less. The #1 spot changed hands 42 times.

**Implication:** the mechanic is proven and durable. The genre is also brutally
competitive and mostly bought (see 1.4).

## 1.2 The ASMR finding — this one matters most

The original idea behind this game was "an ASMR game." The research says that is a
trap, and the evidence is strong:

- Every one of the top 10 ASMR-themed mobile games across a ten-quarter census was
  hypercasual, published overwhelmingly by CrazyLabs and SayGames. "ASMR" is a
  marketing skin on hypercasual, not a genre with its own economics.
- **Hypercasual took 22.05 billion installs in 2025 and produced 1% of all mobile game
  revenue.** Midcore took 65%, casual 34%.
- CrazyLabs booked **73M installs against $2.2M of store revenue** in Q3 2025 — about
  three cents per install.
- *Soap Cutting*, the canonical ASMR title, has ~114M lifetime downloads. It held its
  peak of 14.6M/month for about three months, then decayed to under 1M.
- The trade term is "ultracasual," and the trade's own assessment is that it retains
  *worse* than hypercasual because it has less depth.

**The rule that follows, and you must hold it:** the sensory layer is a **hook** and a
**moment-to-moment feel enhancer**. It is *never* the reason someone returns on day 14.
The sort puzzle carries retention on its own merits. If you ever find yourself removing
puzzle depth to make room for more sensory spectacle, you are building the thing that
makes three cents per install.

Concretely, this means:
- **Do not put "ASMR" in the app name, subtitle, or keywords.** It signals the wrong
  genre to both users and Apple, and Apple's clone rule 4.3(b) explicitly names sound
  effects as a saturated category.
- Do not add an "ASMR mode," a sandbox, or a free-play sensory toy in v1.
- The pour must never be so long that it becomes an obstacle between the player and
  the next move. See 3.6.

## 1.3 The escape route this game is taking

The sensory impulse did survive commercially — by being absorbed into **IAP-monetized
sorting puzzles**, called "hybrid casual puzzle." These buy installs as cheaply as
hypercasual but monetize committed players like casual puzzle. Grand Games' two sort
titles did roughly **11M downloads and ~$11M of IAP in a single 30-day window** (April
2026), and the studio raised a $70M Series B in May 2026.

Sensor Tower's State of Gaming 2026 puts hybrid-casual puzzle at roughly **59% IAP /
41% in-app advertising**.

**Implication: this is an IAP-led game, not an ad-led game.** The ad-led version of
this game is the 1%-of-revenue trap.

## 1.4 The economics that dictate strategy

- US iOS casual CPI is about **$1.41**.
- Planning-case lifetime revenue per download for a decent hybrid-casual puzzle is
  about **$0.35** (range $0.10 weak / $1.00 strong). *These are planning assumptions,
  not verified benchmarks.*
- **At $0.35 LTV against $1.41 CPI, every bought install loses roughly a dollar.**

**Implication:** this game is **organic-first**. We are not buying users, and we are
not going to chart — holding a US top-15 free games position needs roughly 20–40k US
downloads/day sustained, which is $30–50k/day of media at that CPI. That is not
available to us.

Our organic channel is **App Store search**. "Water sort", "color sort", "sort puzzle"
are high-volume searches where users go looking for this genre *by name*. That is the
entire acquisition plan for v1, and it is why we are entering a commodity genre
deliberately rather than inventing a new one.

## 1.5 The bar to beat (GameAnalytics 2026, 16,000+ games)

| Metric | Median | Top quartile | **Our go/no-go** |
|---|---|---|---|
| D1 retention | 22% | ~30% | **≥ 30%** |
| D7 retention | 4% | 6–7% | **≥ 7%** |
| D30 retention | 0.7% | — | — |
| Daily playtime | ~12 min | 22–24 min | **≥ 22 min** |
| Session length | 5–6 min | 8–9 min | — |

Ignore the genre retention tables you will find online (hypercasual 33/12/4, midcore
45/22/10). Those are recycled 2021–22 numbers running about double current medians and
will set an unreachable bar.

## 1.6 Engagement mechanics: what the evidence supports

**Use these:** a *forgiving* streak (Duolingo's wins came from making streaks gentler,
not harsher); a daily appointment with a shareable result; low-frequency personalized
push (assume ~half of iPhone users never opt in); skill-matched cohort leaderboards
rather than global ones.

**Do not use these — the evidence does not support them:** near-miss effects
(replication failure on persistence); loss aversion as a 2× multiplier (contested);
variable-ratio/randomized rewards (arousal and self-report evidence only, plus EU
regulatory exposure); endowed progress as a major lever (one 2006 study); viral invite
loops (no credible k-factor benchmark exists anywhere in the literature).

**None of these appear in v1 at all.** They are listed so you do not add them.

---

# PART 2 — STACK AND CONSTRAINTS

## 2.1 The human's environment

- **Windows PC.** No Mac, no Xcode locally. iOS builds go through **EAS Build** (cloud).
- Paid Apple Developer account, physical iPhone in developer mode, RevenueCat account.
- They have already shipped a React Native / Expo app (`react-native-purchases` 10.4.1,
  `expo-updates`, EAS Build, jest-expo, a custom `preflight.js` with store checks). They
  know this pipeline.

## 2.2 Stack for Pour

Create a **new Expo project on the latest SDK.** Do not pin to SDK 56 — that pin exists
in their other app only because `expo-speech-recognition` has no SDK 57 build, and it is
irrelevant here.

**Required:**
- React Native + Expo (latest SDK), TypeScript strict mode
- `expo-router` for navigation (matches their existing convention)
- **`@shopify/react-native-skia`** — all game rendering. Tubes, liquid, pour arc,
  settle. Do NOT use `react-native-svg` for the liquid; it will not hold 60fps.
- **`react-native-reanimated` (v4) + `react-native-worklets`** — animation on the UI
  thread
- **`react-native-audio-api`** (Software Mansion) — the synthesis engine. It is a full
  Web Audio API implementation with a C++ core on AVFoundation/CoreAudio. Requires an
  **Expo development build**; it does not work in Expo Go.
- `expo-haptics` — v1 haptics
- `react-native-purchases` — RevenueCat, **wired but dormant in v1** (see 6.1)

**Do not add** a game engine, a physics engine, a state-management library, a backend,
an analytics SDK, or an ad SDK. Ask before adding any dependency not listed here.

## 2.3 THE DAY-ONE GATE

Before writing any game code, verify that `react-native-audio-api` builds and runs on
the human's physical device through EAS. Ship them a dev build whose entire UI is one
button that plays a 440 Hz sine for 500ms, and a second that plays a synthesized
100-grain burst.

**If this fails, stop and tell me.** Everything downstream depends on it. Do not build
the game first and integrate audio later.

## 2.4 The silent switch — a real design constraint

iOS games are expected to be silenced by the hardware mute switch, and a game that
blasts audio on silent earns one-star reviews. **Respect the silent switch** (do not
force the `playback` audio session category).

This creates a genuine tension you must design around: **the audio is our
differentiator, but a large share of players play muted.** Therefore:

1. The game must be completely playable and satisfying with **haptics + visuals alone**.
2. On first launch, show a single dismissible line — "sound on, or headphones, is worth
   it" — once, ever. Not a modal, not a nag.
3. Never gate progress or a reward on audio being audible.

## 2.5 Haptics reality

`expo-haptics` provides coarse impact/notification styles, **not** Core Haptics pattern
authoring. You cannot author a fine continuous texture with it. For v1, approximate
texture by firing `Light` impacts at a controlled rate (see 5.2), and accept the
ceiling.

If tuning shows haptic texture genuinely matters, the upgrade path is a small local
Expo native module wrapping Core Haptics — roughly a day of work. **Do not build this
in v1.** Note it and move on.

Relevant platform facts: Core Haptics is foreground-only (fine for a game — a game is
always foreground); haptics are suppressed in Low Power Mode; no iPad has haptics; you
cannot detect whether the user disabled System Haptics. Always provide an in-app
haptics toggle.

---

# PART 3 — GAME DESIGN SPECIFICATION

## 3.1 Core rules

Standard water-sort/ball-sort rules. Do not innovate on these; they are proven and
players already know them.

- The board is a set of **tubes**. Every tube has a capacity of **4 units**.
- Each unit is one of N **materials**.
- Tapping a tube **selects** it; the topmost contiguous run of a single material is the
  selection.
- Tapping a second tube **pours**, if and only if:
  - the destination is not the source, **and**
  - the destination is empty **or** its topmost unit is the same material as the
    selection, **and**
  - the destination has at least 1 free unit of space.
- A pour moves the **entire contiguous run**, limited by available space in the
  destination.
- Tapping the selected tube again **deselects**.
- An invalid destination tap plays a rejection (see 3.5) and **does not** cost anything.
- A tube is **complete** when it holds 4 units of a single material. It then locks.
- The level is **won** when every tube is either empty or complete.

## 3.2 What must NOT be in v1

No timer. No lives. No energy. No score. No stars. No combo multiplier. No fail state.
No shop. No currency. No daily reward. No loot boxes — ever, in any version.

The player can always undo (3.3) or restart. Getting stuck is not a punishment event.

## 3.3 Undo and restart

- **Undo**: unlimited in v1, single-tap, animates the pour in reverse at 1.6× speed.
  (In v2, undo becomes 3 free per level with a rewarded-video top-up. Build the undo
  stack now so that change is a config flip, not a refactor.)
- **Restart**: available from a menu, with a confirm.
- Maintain a full move history per level so both are trivial.

## 3.4 Materials — v1 ships exactly three

A sort puzzle needs at least three materials to be interesting. These three are chosen
to be maximally distinct across all three channels (visual, audio, haptic):

| Material | Visual | Pour character | Sound character |
|---|---|---|---|
| **Water** | translucent blue, bright meniscus, subtle caustics | fast, thin stream, splashes | bright, fast bubbles, high pitch-rise |
| **Honey** | opaque amber, thick domed meniscus, slow | slow, thick ribbon, sometimes breaks into a drip | low sparse "glugs," long envelopes, muffled |
| **Dry sand** | opaque pale ochre, grainy, flat top, no meniscus | granular stream, small conical pile | dry granular hiss, no bubbles at all |

**v2 material backlog** (do not build now): mercury, glass beads, milk, ink, molten wax.

## 3.5 Interaction detail — exact

**Select** (tap an unlocked, non-empty tube):
- The top run rises 6px out of the tube over 120ms, `easeOutCubic`
- A soft glow appears on the tube rim
- Haptic: `impactAsync(Light)`
- Audio: a short material-tinted "lift" tick (see 4.6)

**Deselect** (tap the same tube):
- Reverse of the above over 100ms
- No haptic, no sound

**Valid pour** (tap a legal destination):
1. Source tube **tilts** toward the destination: rotate to 52° over 180ms, `easeInOutCubic`
2. The **stream** appears from the source lip, arcing to the destination mouth. Stream
   width scales with material viscosity (water thin, honey thick).
3. Material **drains** from the source and **rises** in the destination, synchronized.
4. On landing, the destination surface **wobbles** (see 3.7).
5. Source tube **returns** to upright over 160ms.
6. Selection clears.

**Invalid pour** (tap an illegal destination):
- Destination tube shakes horizontally: ±4px, 3 cycles, 220ms total
- Haptic: `notificationAsync(Warning)`
- Audio: a dull, short, low thud — deliberately unsatisfying, deliberately quiet
- The selection is **retained**, not cleared (this is important — clearing it punishes
  the player for a mis-tap)

**Tube complete**:
- A soft bloom of the material's color expands from the tube and fades, 400ms
- The material does a material-specific settle (3.7)
- Audio: a resolving tone at the material's characteristic pitch (see 4.6)
- Haptic: `notificationAsync(Success)`
- The tube dims very slightly and gains a subtle cap — it should read as "done" without
  shouting

**Level complete**:
- Tubes complete in whatever order the player finished them; do not re-animate
- After the last tube: a 700ms beat of silence, then a soft chord built from the
  characteristic pitches of the materials on that board
- Then the next level slides in from the right after 900ms total. **No interstitial
  screen, no star rating, no "Level Complete!" modal.** The next puzzle appears. This
  is critical for session length.

## 3.6 Pour timing — the most important tuning numbers in the game

The pour is the payoff, and it is also the thing standing between the player and their
next move. Too short and there is no product; too long and it is an obstacle. The
research is explicit that a mandatory satisfying payoff becomes dead weight by day 14.

**Starting values, per unit poured:**

| Material | ms per unit | Full 4-unit pour |
|---|---|---|
| Water | 320 | 1280 ms |
| Honey | 620 | 2480 ms |
| Sand | 400 | 1600 ms |

Plus tilt-in 180ms and tilt-out 160ms.

**Hard rules:**
- A **tap during a pour queues the next move**; it is never dropped. Players will
  outrun the animation and must never feel blocked.
- Add a **speed setting** in options: Normal / Fast (0.6×). Default Normal. Do not hide
  it. If the human's tuning says most people want Fast, that is a finding, not a
  failure.
- If a player taps to queue during a pour twice in a row, **auto-shorten** subsequent
  pours to 0.6× for the rest of that level. They are telling you they want speed.

## 3.7 Settle behavior

The 300–500ms after the stream stops is where most of the satisfaction lives. Do not
cut it.

- **Water**: surface wobbles as a damped sine, amplitude 5px decaying over 420ms,
  frequency ~7Hz; small caustic shimmer
- **Honey**: surface domes upward then relaxes over 700ms, `easeOutQuint`; the last of
  the stream forms a single drip that falls 180ms after the main pour ends
- **Sand**: forms a small cone that collapses over 260ms; a few individual grains
  bounce and settle

## 3.8 Level generation

**Generate by reverse moves so solvability is guaranteed by construction.** Do not
generate randomly and then test with a solver.

```
function generateLevel(materials: number, tubes: number, empties: number, shuffleDepth: number) {
  // 1. Start from the SOLVED state: `materials` tubes each holding 4 of one material,
  //    plus `empties` empty tubes.
  // 2. Repeat shuffleDepth times:
  //      pick a random non-empty source tube
  //      pick a random destination tube that has space (ignoring the color-match rule —
  //      we are moving BACKWARD, so we are allowed to create illegal-looking states)
  //      move 1..k units from source top to destination top
  // 3. Reject and retry if the result is already solved, or if any tube is still complete.
}
```

Because every reverse move is the inverse of a legal forward move, the forward solution
always exists.

**Difficulty curve:**

| Levels | Materials | Tubes | Empty tubes | Shuffle depth |
|---|---|---|---|---|
| 1–3 | 3 | 5 | 2 | 6 |
| 4–10 | 3 | 5 | 2 | 12 |
| 11–20 | 4 | 6 | 2 | 20 |
| 21–35 | 5 | 7 | 2 | 28 |
| 36–60 | 6 | 8 | 2 | 36 |
| 61+ | 7 | 9–10 | 2 | 44+ |

Levels 1–3 are the tutorial and must be solvable in 3–5 moves. **No tutorial text
beyond a single pointing hand on level 1.** The mechanic teaches itself.

Seed the generator per level index so level 7 is the same puzzle for every player. That
makes the game shareable and debuggable.

---

# PART 4 — THE AUDIO ENGINE (the heart of the product)

Everything here is **synthesized at runtime**. There are no recorded pour samples. This
is not a cost-saving compromise — it is the correct engineering choice, because the
sound must respond continuously to flow rate, tilt, and *how full the receiving tube
is*. A sample cannot do that. It is also the only part of this game a competitor cannot
copy by extracting your asset bundle.

## 4.1 The physics: bubble acoustics

The sound of pouring liquid is almost entirely the acoustic emission of **resonating
bubbles**. This is well-established: Minnaert's 1933 paper is literally titled *On
musical air-bubbles and the sounds of running water*, and van den Doel's "Physically
Based Models for Liquid Sounds" (ACM TAP, 2005) gives a real-time stochastic model
built from single-bubble synthesis. Later work (Langlois et al., "Improved Water Sound
Synthesis using Coupled Bubbles", ACM TOG 2023) refines it. This is a solved,
documented technique for real-time interactive audio without samples.

**A single bubble** is a damped sinusoid with a *rising* pitch:

```
a(t) = A · e^(−d·t) · sin(2π · f(t) · t)
f(t) = f₀ · (1 + ξ · d · t)
```

**Minnaert resonance frequency** for a bubble of radius r metres in water at 1 atm:

```
f₀ ≈ 3.26 / r        (f₀ in Hz, r in metres)
```

So r = 1mm → f₀ ≈ 3260 Hz; r = 5mm → ≈ 652 Hz; r = 0.3mm → ≈ 10.9 kHz.

**Damping** (van den Doel's empirical fit):

```
d = 0.043 · f₀ + 0.0014 · f₀^1.5
```

**Pitch rise factor** ξ ≈ 0.1. This rising "bloop" is what makes a bubble sound like a
bubble rather than a beep. Do not omit it.

## 4.2 Implementation strategy — grain bank, not live oscillators

Creating thousands of `OscillatorNode`s is far too expensive. Instead:

**At app init**, synthesize a bank of **24 bubble grains** into `AudioBuffer`s:

```ts
// radii log-spaced from 0.25mm to 10mm
const radii = logSpace(0.00025, 0.010, 24);

for (const r of radii) {
  const f0 = 3.26 / r;
  const d  = 0.043 * f0 + 0.0014 * Math.pow(f0, 1.5);
  const xi = 0.1;
  const dur = Math.min(0.25, 6 / d);           // 6 time-constants, capped at 250ms
  const n   = Math.ceil(dur * sampleRate);
  const buf = ctx.createBuffer(1, n, sampleRate);
  const ch  = buf.getChannelData(0);
  for (let i = 0; i < n; i++) {
    const t  = i / sampleRate;
    const ft = f0 * (1 + xi * d * t);
    ch[i] = Math.exp(-d * t) * Math.sin(2 * Math.PI * ft * t);
  }
  bank.push({ r, f0, buffer: buf });
}
```

**At play time**, trigger grains via `AudioBufferSourceNode` with:
- `playbackRate` jitter of ±6% (so no two bubbles are identical)
- randomized gain, 0.25–1.0, weighted so small bubbles are quieter
- a `StereoPannerNode` at ±0.25 for width

**Pool and cap the nodes.** Maximum 48 concurrent grain voices. If the scheduler wants
more, drop the quietest. Never let node count grow unbounded — that is the #1 way this
engine will tank the frame rate.

## 4.3 The four-layer pour bus

Every pour is four layers into one bus:

```
[1] turbulence bed  ─┐
[2] bubble grains   ─┼──▶ [3] cavity peaking filter ──▶ busGain ──▶ compressor ──▶ limiter ──▶ destination
[4] impact/landing  ─┘
```

**Layer 1 — turbulence bed.** A looping white-noise `AudioBufferSourceNode` through a
bandpass. Gain proportional to flow rate. This is the "hiss" of falling liquid.
- Water: bandpass 800–4000 Hz, Q 0.7
- Honey: lowpass ~700 Hz — muffled, almost no hiss
- Sand: this layer *is* the sound; bandpass 2–9 kHz, high gain

**Layer 2 — bubble grains.** Scheduled as a **Poisson process** with rate λ ∝ flow rate.

```ts
// call each animation frame while pouring
const lambda = params.bubbleRateBase * flowRate;   // bubbles per second
const expected = lambda * dt;
let toSpawn = Math.floor(expected);
if (Math.random() < expected - toSpawn) toSpawn++;
for (let i = 0; i < toSpawn; i++) spawnGrain(pickRadius(material));
```

- **Water**: `bubbleRateBase` 260/s, radii sampled 0.25–3mm, weighted toward small
- **Honey**: `bubbleRateBase` 14/s, radii 4–10mm — sparse, large, low "glugs." Also
  apply a slow 2.5 Hz amplitude wobble to the whole bus to get viscous intermittency.
- **Sand**: **no bubble layer at all.** Instead, granular impulses: 2–5ms noise bursts,
  highpassed at 2 kHz, density ∝ flow rate, ~400/s at full flow.

**Layer 3 — the cavity resonance sweep. THIS IS THE MOST IMPORTANT PART OF THE ENGINE.**

As the receiving tube fills, the column of air above the liquid shortens, and its
resonant frequency rises. That rising pitch is the single most satisfying cue in the
entire interaction, and it is exactly what no sampled sort-puzzle on the chart has.

Model the receiving tube as a closed-open pipe:

```
f_cavity = c / (4 · L_air)          c = 343 m/s
L_air = tubeHeight · (1 − fillFraction)
```

With `tubeHeight` = 0.12 m:
- empty (fill 0.00) → L_air 0.120 → **714 Hz**
- half  (fill 0.50) → L_air 0.060 → **1429 Hz**
- 90%   (fill 0.90) → L_air 0.012 → **7146 Hz**

Implement as a `BiquadFilterNode` of type `'peaking'`, `Q` ≈ 4, `gain` ≈ +9 dB, with
`frequency` driven **every frame** from the live fill fraction using
`setTargetAtTime(f, ctx.currentTime, 0.02)` for a smooth glide.

Clamp the frequency to [400 Hz, 9000 Hz] so it never gets shrill at near-full.

Sand gets a much weaker version of this (gain +3 dB) — granular material does not
excite the air column the same way. Honey gets the full sweep but shifted down an
octave.

**Layer 4 — impact/landing.** A short burst when the stream first contacts the
destination surface. Two variants: hitting the empty tube *bottom* (harder, brighter)
vs hitting an existing liquid *surface* (softer, splashier). Retrigger on each unit
boundary at reduced gain.

## 4.4 Master chain

```
busGain → DynamicsCompressorNode(threshold −18dB, ratio 4, attack 3ms, release 120ms)
        → limiter (compressor, threshold −2dB, ratio 20)
        → destination
```

Keep headroom. With 48 grains overlapping, clipping is a real risk and it sounds awful.

## 4.5 Latency budget

**Tap → first audible sound must be under 60ms.** Measure it and tell me the number.
Pre-warm the AudioContext on first user interaction; never create it lazily mid-pour.

## 4.6 Non-pour sounds (also synthesized)

- **Lift tick** (on select): a single grain from the bank at the material's
  characteristic radius, at 0.3 gain
- **Rejection thud**: 120 Hz sine, 60ms, fast decay, lowpassed — deliberately dull
- **Tube complete**: a resolving tone at the material's characteristic pitch —
  water 880 Hz, honey 440 Hz, sand 660 Hz — with a soft attack and 600ms decay
- **Level complete**: a chord of the characteristic pitches of the materials on that
  board, root-position, 1.2s

**No music in v1.** Silence between pours is what makes the pours land.

---

# PART 5 — HAPTICS

## 5.1 Mapping

| Event | Haptic |
|---|---|
| Select | `impactAsync(Light)` |
| Pour (continuous) | rate-limited `Light` train, see 5.2 |
| Unit lands | `impactAsync(Medium)` |
| Invalid move | `notificationAsync(Warning)` |
| Tube complete | `notificationAsync(Success)` |
| Level complete | `Success` + two `Light` 90ms apart |

## 5.2 Approximating pour texture

`expo-haptics` cannot author a continuous texture. Approximate: fire `Light` impacts at
a rate proportional to the bubble/grain rate, **capped at 18/second** — iOS throttles
above roughly 20/s and it degrades into mush.

- Water: 18/s (feels like fizz)
- Honey: 5/s (feels like slow glugs)
- Sand: 14/s (feels like grain)

Provide a haptics **on/off toggle** in options, defaulted on. Respect it everywhere.

---

# PART 6 — MONETIZATION (built, dormant, in v1)

## 6.1 v1 ships with zero monetization visible

Wire `react-native-purchases` and confirm it initializes. Show nothing. No ads, no IAP,
no paywall. We are measuring retention first, and monetization noise corrupts that
measurement.

## 6.2 v2 plan — IAP-led, per the research

When it turns on:
- **"Quiet Pass"** — a non-consumable or subscription that removes interstitials and
  unlocks all materials. Primary revenue line.
- **Material packs** — deterministic, contents shown before purchase, permanent.
- **Rewarded video** — user-initiated only, for undo top-ups.
- **Interstitials** — at most one per 4 completed levels, never during a pour, never
  during the settle.

**Absolute rules, permanently:**
- **No randomized purchasables. Ever.** No loot boxes, no gacha, no mystery chests.
  This sidesteps Apple's 3.1.1 odds-disclosure regime and the EU/Brazil loot-box rules
  entirely, at zero design cost.
- Any interstitial must be dismissible with a large close button and an in-app ad report
  control (Apple guideline 2.5.18).
- Subscriptions need a 7-day minimum term and genuine ongoing value (3.1.2). Put "Cancel
  subscription" at the top level, routing straight to the system sheet. No retention maze.

The human qualifies for Apple's **Small Business Program** — 15% commission instead of
30%, up to $1M in proceeds per calendar year. Apple takes **nothing** from ad revenue.

---

# PART 7 — VISUAL DESIGN

The chart leaders are bright and candy-colored. We are going the other way: a deep,
quiet ground so the materials are the only saturated thing on screen. This reads as
premium, makes the liquid glow, and is a genuine differentiator in a genre where
everything looks the same.

**Palette:**
```
Background      #14171C, with a radial vignette to #0D0F13 at the edges
Tube glass fill rgba(255,255,255,0.06)
Tube rim        rgba(255,255,255,0.18)
Tube specular   a soft white streak down the upper-left edge, 0.12 opacity
Water           #3FA9E0 → #1E6FA8 (top → bottom), meniscus highlight #9BD8F5
Honey           #E39B2C → #B8701A, meniscus highlight #F6C669
Sand            #D9C08A → #B39A66, no meniscus, subtle grain noise overlay
UI text         #E8EAED primary, #8A9199 secondary
```

**Layout:** tubes centered, laid out in up to two rows, sized so the largest board (10
tubes) still has comfortable tap targets — minimum 56×140pt per tube with 16pt gaps.
Level number top-left, undo top-right, settings gear bottom-right. Nothing else.

**Type:** system font. Level number in tabular figures.

**Motion:** everything on the UI thread via Reanimated worklets. Target a locked 60fps.
Respect `prefers-reduced-motion` — reduce settle amplitudes to zero and shorten pours,
but never disable them entirely (the pour *is* the feedback).

---

# PART 8 — THE TUNING PANEL (build this; it is how we work together)

I cannot hear or feel anything. The human is my instrument. Give them direct control
instead of round-tripping a code change per tweak.

**Access:** five taps on the level number. Dev builds only — strip it from production
via `__DEV__` or an env flag.

**Every parameter below gets a live slider with its numeric value displayed.** Changes
apply immediately, without restarting the pour.

```
GLOBAL
  masterGain              0 – 1
  pourSpeedMultiplier     0.4 – 2.0
  hapticsEnabled          bool
  hapticRateCap           0 – 20 /s

PER MATERIAL (tab per material: Water / Honey / Sand)
  bubbleRateBase          0 – 500 /s
  bubbleRadiusMin         0.1 – 12 mm
  bubbleRadiusMax         0.1 – 12 mm
  radiusDistributionSkew  -2 – 2      (negative = favour small bubbles)
  grainGainMin            0 – 1
  grainGainMax            0 – 1
  pitchRiseXi             0 – 0.4
  dampingScale            0.3 – 3.0
  noiseBedGain            0 – 1
  noiseBedFreqLow         100 – 8000 Hz
  noiseBedFreqHigh        100 – 12000 Hz
  cavityGainDb            0 – 18 dB
  cavityQ                 0.5 – 12
  cavityFreqMin           200 – 2000 Hz
  cavityFreqMax           2000 – 12000 Hz
  msPerUnit               150 – 1200 ms
  tiltAngle               30 – 75 °
  settleDuration          100 – 1200 ms
  hapticRate              0 – 20 /s
```

**Include a "Copy config as JSON" button** that puts the whole parameter set on the
clipboard. The human pastes it back to me; that is our tuning protocol. Ship sensible
defaults from Part 4 so the first build already sounds close.

---

# PART 9 — BUILD PLAN

Work in this order. Do not reorder; each step de-risks the next.

**Day 1 — the gate.** New Expo project, TypeScript strict, EAS dev build profile.
Add `react-native-audio-api`. Ship a build with two buttons: play a 440 Hz sine, and
play a 100-grain bubble burst. Human confirms both are audible on device. Measure and
report tap→sound latency. **If this fails, stop.**

**Days 2–4 — the board.** Skia rendering of tubes and static material columns. Tap to
select/deselect. Legal-move validation. Pour with a simple linear fill animation, no
stream art yet. Level generator with the reverse-move algorithm. Levels 1–10 playable.
Undo. **The game should be logically complete and boring at the end of this step.**

**Days 5–8 — the audio engine.** Grain bank at init. The four-layer pour bus. The
cavity sweep driven by live fill fraction. All three materials differentiated. Master
chain with the limiter. Non-pour sounds. Report the concurrent-voice count under load.

**Days 9–10 — feel.** Stream rendering and the arc. Tilt. Settle behavior per material.
Haptics. The tuning panel with JSON export. Speed setting. Queued taps during pours.

**Then: the human plays five levels and answers three questions.**

## Acceptance criteria

- Sustained 60fps during a 4-unit honey pour with all four audio layers active, on the
  human's device
- Tap → first audible sound < 60ms
- Concurrent grain voices never exceed 48
- No audio clipping at master gain 1.0 with three simultaneous pours queued
- Every level 1–60 is solvable (assert this in a test that runs the generator 1,000
  times and verifies with a BFS solver)
- App fully playable and satisfying with sound off

## The go/no-go

Ask the human exactly these three questions after five levels:

1. Does the pitch rising as the tube fills read as satisfying, or as a gimmick?
2. Does the pour feel too slow by level five?
3. **Do you want to play a sixth level without me asking you to?**

Question 3 is the real gate. If the honest answer is no, we stop and reconsider — two
weeks spent instead of three months. That is a successful outcome for this phase, not a
failure.

---

# PART 10 — TESTING

- `jest-expo`, matching the human's existing convention.
- Unit tests for: move legality, the pour resolution (contiguous-run size and clamping),
  win detection, undo/redo correctness, and the level generator's solvability invariant.
- The solvability test is the important one: generate 1,000 levels per difficulty tier
  and prove each is solvable with a BFS solver. This test may be slow; mark it and run
  it in CI, not on every save.
- Snapshot-test the board reducer, not the Skia output.
- Do not attempt to unit-test the audio engine's output. Test that the graph builds,
  that the grain bank has 24 buffers, and that voice count stays capped.

---

# PART 11 — STORE AND ASO

Organic search is the entire acquisition plan, so this is not an afterthought.

- **Category:** Games → Puzzle. **Age rating 4+.**
- The title and subtitle must carry the genre words people actually search: "sort",
  "water sort", "color sort", "puzzle". Working title *Pour*, but the subtitle must do
  the discovery work.
- **Do not use "ASMR" anywhere in the metadata.**
- Screenshots must show the tubes and the materials clearly at thumbnail size. Mid-pour
  frames with the stream visible convert better than static boards.
- An app preview video is worth making: the pour with the rising pitch is the entire
  pitch, and it demonstrates in three seconds.
- Run the human's existing `preflight.js` conventions if portable.

---

# PART 12 — HOW TO WORK WITH ME (the human)

- I am on **Windows**. Never suggest anything requiring local Xcode. All device builds
  go through **EAS**.
- I test on a **physical iPhone**. Tell me explicitly when I need a new dev build versus
  when an OTA/Fast Refresh update is enough — dev builds are slow and I want to batch
  them.
- **You cannot hear or feel anything.** Never claim the audio "should sound good."
  Describe what you implemented in terms of parameters, and ask me what it actually
  sounds like.
- When something is a judgement call about feel, **give me a tuning slider rather than
  picking a value.**
- Ask before adding any dependency not listed in 2.2.
- Keep the tuning panel out of production builds.
- If you hit something in this document that turns out to be wrong on real hardware —
  especially the audio library's behavior, the latency budget, or the voice cap — **tell
  me it was wrong rather than quietly working around it.**

---

# APPENDIX — SOURCES FOR THE AUDIO MODEL

- Minnaert, M. (1933). *On musical air-bubbles and the sounds of running water.*
  Philosophical Magazine. — the resonance frequency relation
- van den Doel, K. (2005). *Physically Based Models for Liquid Sounds.* ACM
  Transactions on Applied Perception. https://dl.acm.org/doi/10.1145/1101530.1101554 —
  the real-time stochastic bubble model and the empirical damping fit
- Langlois, T. et al. (2023). *Improved Water Sound Synthesis using Coupled Bubbles.*
  ACM TOG. https://dl.acm.org/doi/10.1145/3592424
- UNC GAMMA, *Sounding Liquids: Automatic Sound Synthesis from Fluid Simulation.*
  http://gamma.cs.unc.edu/SoundingLiquids/
- React Native Audio API docs: https://docs.swmansion.com/react-native-audio-api/
