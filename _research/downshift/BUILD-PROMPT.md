# DOWNSHIFT — Build Prompt

**Paste everything below this line into a fresh Claude Code session on the local machine.**

---

# MISSION

You are building **Downshift**, an iOS app, from scratch, with me (the human) as your
only teammate and your only pair of hands. I test on a physical iPhone; you cannot see
the screen, hear the audio, or feel the haptics. Design every step around that.

Downshift is a **twenty-minute wind-down ritual**. The user lies down, holds the phone,
taps along with their own breathing for twenty seconds, and the phone begins a gentle
haptic pulse locked to their measured rate. Over the session that pulse slows, and a
generative audio bed — synthesized, never recorded — darkens in lockstep with it. At the
end, the pulse dissolves and the app tells them to put the phone down.

It is not a sleep tracker, not a meditation library, and not an all-night sleep aid.
It deliberately **ends before sleep onset**. That constraint is not a compromise; it is
forced by the platform (see 1.3) and it makes the product honest.

Read this entire document before writing code. The research sections exist to stop you
from redesigning this into something the evidence says fails.

---

# PART 1 — WHY THIS APP EXISTS, AND WHY IT IS SHAPED THIS WAY

## 1.1 Sleep is where the money is. ASMR is not.

From a market study of the US App Store, August 2026:

- **Health & Fitness leads every category** in RevenueCat's State of Subscription Apps
  2026 (115,000 apps, $16B revenue) on install LTV (**$1.21**) and D14 revenue per
  install (**$0.48**, roughly 6× Gaming). It is the most annual-skewed category at
  **68% annual plans**.
- Consumers demonstrably accept **$50–70/year** here. Price anchors: Calm and Headspace
  $69.99/yr, BetterSleep $59.99/yr, Endel ~$49.99/yr.
- The strongest single signal: **Calm spun sleep out into a standalone app** in
  September 2025 with its own separate $69.99/yr subscription, then raised prices in
  February 2026. The category leader validating sleep as a standalone paid product.

Against that:

- **ASMR responsiveness is only ~10–20% of the population**, which caps the addressable
  market before you start.
- **No ASMR-native app has ever reached commercial scale.** The venture-backed
  flagship, Tingles, peaked around 60K MAU and shut down.
- Every top-10 ASMR-themed *game* across a ten-quarter census was hypercasual;
  hypercasual took 22.05B installs in 2025 and produced **1% of mobile game revenue**.

**The rule:** this is a **sleep** product that happens to be sensory. It is not an ASMR
product. Do not put "ASMR" in the app name, subtitle, keywords, or marketing copy —
it signals a category that does not pay, and Apple's clone rule 4.3(b) explicitly names
sound effects as a saturated category where new submissions get refused.

## 1.2 The funnel math you are designing against

From RevenueCat 2026 — these numbers should shape the paywall, not decorate it:

| Metric | Value | Design consequence |
|---|---|---|
| Median D35 install→paid, North America | **2.6%** | Most installs never pay. Fine. |
| Trial→paid, **hard** paywall | **10.7%** | — |
| Trial→paid, freemium | **2.1%** | Hard paywall converts ~5× better |
| Median monthly churn | **13–14%** | — |
| Median **first** annual renewal | **23–40%** | See 1.5 — this is the real threat |
| Annual cancellers who ever return | **5%** | Churn is permanent |

**Consequence: use a hard paywall after a short, complete free trial of the actual
product** — not a crippled freemium tier. Details in Part 7.

## 1.3 The platform constraint that defines the product

This is the single most important technical fact in this document, and the original
version of this concept was **impossible** because of it:

> **Core Haptics is foreground-only.** The engine's `stoppedHandler` fires the moment
> the app backgrounds. `UIFeedbackGenerator` is inert when the app is not
> foreground-active. There is **no** haptic experience that survives screen-lock,
> backgrounding, or a pocket. Haptics are also suppressed in Low Power Mode, absent on
> all iPads, and you cannot detect whether the user has switched System Haptics off.

Background **audio** is fine (`.playback` category plus the `UIBackgroundModes: audio`
entitlement). Background **haptics** do not exist.

**So the product splits cleanly along that seam, and this is the design:**

- **Phase 1 (0–20 min): foreground, screen on, haptics + audio.** The user is holding
  the phone, awake, doing the ritual. Haptics work perfectly here.
- **Phase 2 (optional, 20–40 min): audio only, screen off, backgrounded.** They put the
  phone down and the audio bed continues fading. No haptics — and none are needed,
  because they are no longer holding it.

Do not fight this boundary. Design to it.

## 1.4 The premise is a hypothesis, not a finding

State this plainly and keep it in mind: **a vibrating object in the hand is an
*arousing* stimulus for a meaningful fraction of people.** That it soothes is the
assumption the entire product rests on, and no research in this project validates it.

There is a second unvalidated behavioral assumption: most people put their phone on the
nightstand at night, and this app asks them to hold it. That is a behavior *change*,
not a behavior we are riding.

Both get tested in week one (Part 11), before we build the polished version.

## 1.5 The twelve-month problem — solve it in the architecture, not later

The most serious criticism of this concept: **there is one experience, and it is
identical on night 200.** The reason Calm and BetterSleep carry thousand-hour libraries
is not laziness — it is that an annual renewal needs something to have happened since
the user paid. With a median first-annual renewal of 23–40%, this is the thing most
likely to kill the business.

Two mitigations, both built in from the start (Part 8):
1. **The taper adapts** to accumulated nightly data, so the session genuinely changes
   over months rather than replaying a fixed curve.
2. **Seasonal audio beds** — four per year, not weekly. Enough to make renewal feel
   earned; few enough that it is not a content treadmill for a two-person team.

## 1.6 Mechanics: what the evidence supports

**Use:** a *forgiving* streak — the only streak experiments with named provenance
(Duolingo's) won by making streaks **gentler**, not harsher. Low-frequency personalized
push; assume roughly half of iPhone users never opt in at all.

**Do not use:** punishing streaks, near-miss effects, loss aversion framing, randomized
rewards, endowed progress as a major lever, invite loops. The evidence does not support
any of them, and a guilt mechanic aimed at an insomniac is both cruel and
counterproductive.

**Specifically: never show a broken streak at night, and never send a shaming
notification.** A sleep product that makes you anxious about the sleep product has
failed at its only job.

---

# PART 2 — STACK AND CONSTRAINTS

## 2.1 The human's environment

- **Windows PC.** No Mac, no local Xcode. iOS builds via **EAS Build** (cloud).
- Paid Apple Developer account, physical iPhone in developer mode, RevenueCat account.
- Has already shipped a React Native / Expo app: `react-native-purchases` 10.4.1,
  `expo-sqlite`, `expo-notifications`, `expo-updates`, EAS Build, jest-expo, a custom
  `preflight.js` with store checks. They know this pipeline well.

## 2.2 Stack

New Expo project, **latest SDK**, TypeScript strict mode. Do not pin to SDK 56.

**Required:**
- React Native + Expo, `expo-router`
- **`react-native-audio-api`** (Software Mansion) — the generative audio engine. Full
  Web Audio implementation, C++ core on AVFoundation/CoreAudio. Requires an **Expo
  development build**; does not work in Expo Go.
- `react-native-reanimated` v4 + `react-native-worklets` — the pulse scheduler runs
  here, not on the JS thread (see 2.3)
- `expo-haptics` — v1 haptics, with a known ceiling (see Part 6)
- `expo-sqlite` — the nightly ledger, local only, no accounts, no server
- `expo-keep-awake` — the screen must not sleep during Phase 1
- `react-native-purchases` — RevenueCat
- `expo-notifications` — exactly one optional reminder, see 7.4
- `@shopify/react-native-skia` — only if the visuals in Part 9 need it; try plain
  Reanimated first, this app is nearly UI-less

**Do not add** a backend, accounts, analytics SDKs, ad SDKs, a health-data integration,
or HealthKit. Ask before adding anything not listed.

## 2.3 THE DAY-ONE GATE — haptic timing jitter

For Pour, the risk was whether audio synthesis worked at all. Here it is different and
sharper: **this product is a rhythm.** A heartbeat pulse with audible timing jitter
feels broken in a way a game never would. JS-thread `setTimeout` will not hold a steady
beat under any load.

**Before building anything else**, ship a dev build that does exactly one thing: pulse
`impactAsync(Medium)` at 60 BPM for 60 seconds, scheduled from a **Reanimated worklet
on the UI thread with a lookahead scheduler**, and log the actual inter-pulse intervals.

Report to me: mean interval, standard deviation, and worst-case deviation.

- **σ under ~8ms** → acceptable, proceed on `expo-haptics`.
- **σ above that, or audible/feelable unevenness** → we need a native module. Stop and
  tell me. The fix is a small local Expo module (Expo Modules API) wrapping
  `CHHapticEngine` with a pre-scheduled `CHHapticPattern`, which gets sample-accurate
  timing and continuous intensity control. That is roughly a day of work and it may be
  mandatory. **Do not build it speculatively; do not skip the measurement either.**

Also measure: does firing haptics at 0.2–1 Hz for 20 minutes cause any thermal or
battery issue worth noting? Report battery drain over one full session.

## 2.4 Audio session configuration

- **Phase 1** (foreground ritual): category `.playback` so the session is audible even
  with the silent switch on. Rationale differs from a game — someone deliberately
  starting a 20-minute sleep ritual expects sound, and their phone is very likely on
  silent at bedtime. If they wanted silence they would not have opened this.
  - **But**: show a volume/route hint on first run only, and make the ritual fully
    functional with the volume at zero (the haptics carry it).
- **Phase 2** (backgrounded fade): requires the `UIBackgroundModes: audio` entitlement.
  App Review actively polices this — it is only legitimate because we genuinely play
  continuous audible content in the background. Do not declare it for any other reason.
- Detect the output route via `AVAudioSession.currentRoute` equivalents so we know
  whether headphones are present. Note that `.bluetoothA2DP` cannot distinguish earbuds
  from a Bluetooth speaker.
- Handle interruptions (calls, alarms) by pausing gracefully and offering resume.

## 2.5 Headphones and the speaker mix

Binaural/HRTF rendering collapses to nothing on the built-in speaker. A large share of
bedtime users will not wear headphones.

**Therefore: do not build a binaural-dependent product.** Ship a single mix that works
on the phone speaker, and apply a subtle stereo widening only when headphones are
detected. The product must not feel broken without them. Do not nag about headphones.

---

# PART 3 — THE SESSION SPECIFICATION

## 3.1 Timeline (the whole product, in order)

| Time | What happens |
|---|---|
| 0:00 | App opens to a near-black screen. One word: **Down**. Nothing else. |
| 0:03 | Tap it. Text replaces it: *"tap each time you breathe out"* |
| 0:03–0:35 | **Calibration.** User taps 5 times on their own exhales. Take the **median** of the 4 intervals (median, not mean — one stray tap must not skew it). |
| 0:35 | Pulse begins at the measured rate. Audio bed fades in over 8s. |
| 0:35–4:00 | **Entrainment hold.** Tempo stays at the measured rate. The user must feel it *match* them before it can lead them. Do not taper yet. |
| 4:00–16:00 | **The taper.** Rate decreases by **0.5 breaths/min per minute**, floored at 6/min. Audio bed brightness decays in lockstep (Part 5). |
| 16:00–20:00 | **Floor.** Rate holds at 6/min. Haptic intensity ramps to zero over the final 4 minutes so the pulse *dissolves* rather than stopping. |
| 20:00 | Ritual ends. Screen shows one line: *"put the phone down."* Audio continues. |
| 20:00–40:00 | **Phase 2**, optional and default-on. Audio-only, app may background, screen off. Slow fade to silence. No haptics. |
| — | Session logged. **Nothing else happens tonight.** No summary, no score, no paywall, no notification. |

## 3.2 Rate model — get the units right

The pacer is in **breaths per minute**, not heart rate. Typical adult resting
respiration is 12–20/min. Slow-breathing practice commonly targets ~6/min.

- Measured start rate `R₀`: clamp to **[8, 24]** breaths/min. Outside that, the
  calibration failed — silently restart it once, then default to 14.
- Taper: `R(t) = max(6, R₀ − 0.5·(t − 4min))` for t in minutes.
- From R₀ = 14 the floor is reached at minute 20 — which is why the hold is 4 minutes
  and the taper 12.

## 3.3 The pulse shape

Each breath cycle is one pulse event pair:

- **Inhale mark**: `impactAsync(Light)` at cycle start
- **Exhale mark**: `impactAsync(Medium)` at 40% through the cycle

So a 14/min rate = one cycle every 4286ms, with marks at 0ms and 1714ms. At the 6/min
floor, one cycle every 10,000ms with marks at 0ms and 4000ms.

Inhale:exhale ratio of **40:60** — the longer exhale is the conventional shape for
wind-down pacing. Make the ratio a tuning parameter.

**Intensity taper** is the weak point of `expo-haptics`: only discrete styles are
available, so the final 4-minute fade must be approximated by dropping
`Medium → Light → Soft` and then thinning the pulses (skipping the inhale mark, then
alternating cycles). If the native module gets built, replace this with a true
continuous intensity ramp.

## 3.4 Screen behavior during Phase 1

- `expo-keep-awake` active for the whole ritual.
- Screen is **true black** (`#000000`) at **minimum brightness**, set programmatically
  if possible. Someone lying in the dark must not be lit up by their phone.
- A single dim indicator — a small circle that expands on inhale and contracts on
  exhale, at 8% opacity max. It exists so the user knows the app is alive and gives a
  visual pacing cue for people who prefer one. Nothing else on screen.
- Tapping anywhere shows a minimal pause/stop control for 3 seconds, then it fades.
- **No timer, no countdown, no progress bar.** Watching time pass is the opposite of
  the product.

## 3.5 The morning ledger

The **only** progress surface, and it is shown in the **morning**, never at night.

On the first foreground open after a completed session, show one screen:

```
Night 12

You started at 15 breaths a minute.
You finished at 6.

[ a small sparkline of start-rate over the last 30 nights ]

Nights down: 12 of the last 30
```

Then it dismisses to the **Down** button. That is the entire app.

**Rules:**
- "Nights down: 12 of the last 30" — an **x-of-last-30 counter, not a consecutive
  streak.** A consecutive-day mechanic on a sleep product punishes exactly the
  insomniac who bought it. Missed nights grey out; nothing ever resets to zero.
- Never say the app *caused* anything. See Part 10 on health claims.

---

# PART 4 — DATA MODEL

All local. `expo-sqlite`. No server, no accounts, no cloud sync in v1.

```sql
CREATE TABLE sessions (
  id              INTEGER PRIMARY KEY,
  started_at      INTEGER NOT NULL,      -- unix ms, local
  ended_at        INTEGER,
  start_rate      REAL NOT NULL,         -- breaths/min, measured
  floor_rate      REAL,                  -- reached
  completed       INTEGER NOT NULL,      -- 0/1 : did they reach 20:00
  abandoned_at_ms INTEGER,               -- if not completed
  phase2_ms       INTEGER,               -- audio-only continuation duration
  bed_id          TEXT NOT NULL,         -- which audio bed
  app_version     TEXT NOT NULL
);

CREATE TABLE prefs (key TEXT PRIMARY KEY, value TEXT NOT NULL);
```

`abandoned_at_ms` is the most valuable column in the app — it tells us exactly where
people bail. Surface it in the debug export (Part 11).

---

# PART 5 — THE AUDIO ENGINE

Everything is **synthesized at runtime** via `react-native-audio-api`. No recorded
audio files ship in the bundle. This is the right call for three reasons: the bed must
respond continuously to the taper, a 40-minute non-repeating bed cannot be shipped as a
sample without an enormous binary, and a synthesized bed cannot be extracted and copied.

## 5.1 The bed: three layers

```
[1] noise bed    ─┐
[2] droplets     ─┼──▶ [3] breath-synced swell ──▶ masterLowpass ──▶ gain ──▶ limiter ──▶ out
                  ┘
```

**Layer 1 — noise bed.** A looping buffer of **brown noise** (integrated white noise,
DC-blocked), through a bandpass. Brown, not white — white noise is hissy and alerting;
brown is the "rain on canvas" register.
- Generate ~30s of brown noise into an `AudioBuffer` at init, loop it with a random
  start offset each session so it never sounds identical.
- Bandpass centre ~500 Hz, Q 0.4.

**Layer 2 — droplets.** Sparse stochastic grains, giving the bed texture so it does not
read as a flat noise wash. Same grain-bank technique as any granular engine:
- Pre-render 16 droplet grains at init: a short filtered impulse with a resonant tail —
  a damped sinusoid at 300–1800 Hz, exponential decay 40–180ms, with a fast noise
  transient at onset.
- Schedule as a **Poisson process**, rate ~1.5–4 per second, jittered gain and pan.
- Rate scales *down* gently across the session (fewer events as it darkens).

**Layer 3 — the breath-synced swell.** A low sine drone at **55–75 Hz**, whose gain is
modulated **in phase with the pulse**: swelling on inhale, decaying on exhale. This is
what ties the audio to the haptics so they read as one thing rather than two.
- Modulation depth is a tuning parameter; start at 0.35.
- Use `setTargetAtTime` on the gain for smooth glides — never step it, steps click.

## 5.2 The master lowpass — the audible taper

**This is the single most important parameter in the engine**, the audio analogue of
the tempo taper. As the rate slows, the whole bed darkens.

```
cutoff(t) = lerp(2800 Hz, 380 Hz, taperProgress)
```

where `taperProgress` goes 0 → 1 across minutes 4 → 16. Apply as a `BiquadFilterNode`
of type `lowpass`, Q 0.7, driven every frame with `setTargetAtTime(f, now, 0.5)` — a
long time constant so the darkening is imperceptible moment-to-moment and obvious in
retrospect.

During Phase 2, continue sweeping from 380 Hz down to ~180 Hz while the master gain
fades to zero over the final 5 minutes.

## 5.3 Master chain

```
gain → DynamicsCompressor(threshold −20dB, ratio 3, attack 20ms, release 400ms)
     → limiter (threshold −3dB, ratio 20)
     → destination
```

Gentle. This is not a game; nothing should ever jump in level. **No sound in this app
may ever exceed the level established in the first 30 seconds.** A startle in a sleep
product is a catastrophic failure and a guaranteed one-star review.

## 5.4 Beds

Ship **three** beds in v1: *Rain on canvas*, *Ship's hull*, *Night field*. Each is a
parameter set over the same three-layer engine — different noise bandpass, different
droplet grain characteristics and rate, different drone pitch. **Not different audio
files.** Adding a bed must be a JSON change, not a recording session.

Seasonal beds (four per year) follow the same rule — that is what makes the renewal
promise in 1.5 affordable.

## 5.5 Latency

The pulse and the swell must be perceptually simultaneous. Report measured offset
between the haptic call and the audio swell onset. If it exceeds ~30ms, compensate by
scheduling the audio slightly early — the audio clock is the accurate one, so **derive
haptic timing from the audio clock**, not the reverse.

Note: wireless headphones add 80–220ms of variable, non-compensable audio delay. When
headphones are detected, the audio will lag the haptics and there is no fix. Reduce the
swell depth in that case so the mismatch is less noticeable, and never rely on tight
audio-haptic sync for the core experience.

---

# PART 6 — HAPTICS

Covered in 2.3 (the timing gate) and 3.3 (the pulse shape). Additional rules:

- **Haptics on/off toggle** in settings, default on. If off, the visual breathing
  indicator becomes slightly more prominent (18% opacity) to carry the pacing.
- Detect Low Power Mode if possible and warn once that haptics may be suppressed.
- No haptics whatsoever during Phase 2.
- Never fire a haptic on a notification, a paywall, or a settings change. The only
  haptic in this app is the pulse.

---

# PART 7 — ONBOARDING, PAYWALL, MONETIZATION

## 7.1 There is no onboarding

No carousel, no account, no questionnaire, no permission prompts on launch. First
launch goes **straight to the Down button**. The calibration teaches the product.

Request notification permission only if and when the user enables the optional reminder
(7.4). Never gate anything on it — Apple guideline 5.1.2(i) forbids requiring
notification opt-in for functionality.

## 7.2 The free trial is three complete nights

Sessions 1–3 are the **full, uncrippled product**: full taper, all three beds, Phase 2
included. No feature is withheld.

## 7.3 The paywall

- Appears **once**, on the **morning** after the third completed session, directly below
  the ledger.
- **Never at night. Never before a session. Never mid-session.** Asking a half-asleep
  person for money is both predatory and a terrible conversion context.
- It is a **hard paywall** — after session 3, the ritual requires a subscription. The
  RevenueCat data is clear that this converts roughly 5× better than a freemium tier
  (10.7% vs 2.1% trial→paid at D35), and a permanently-sufficient free tier on a
  single-experience product means nobody ever pays.
- **Price: $39.99/year and $6.99/month**, with a 7-day free trial on the annual tier.
  Not Calm-tier — we have one experience, not a thousand-hour library, and pricing like
  we do not is a conversion problem the paywall cannot argue its way out of.
- Display the **total annual amount** most prominently, per Apple guideline 3.1.2(c).
- Copy is plain and short. No countdown timers, no fake scarcity, no "97% off."

## 7.4 Notifications — exactly one, optional

A single wind-down reminder at a user-chosen time, off by default, offered *once* on
the morning ledger screen after session 2.

- **Never** a shaming message. Never "you broke your streak." Never "you haven't slept
  well."
- Copy is neutral: *"Wind down?"*
- One per day maximum. The one clean field experiment on push (n=17,500, five
  frequencies, seven weeks) found that raising non-personalized frequency **causally
  increased uninstalls** with no offsetting gain. Assume ~half of users never opt in.
- Marketing push requires separate explicit opt-in under Apple's rules and may not be
  monetized.

## 7.5 Cancellation

A top-level settings row labelled **"Cancel subscription"** that routes straight to
`showManageSubscriptions()`. No retention flow, no "are you sure," no discount
interception. Apple's 3.1.2 bans bait-and-switch subscription practices and cancel-flow
mazes are the single most legally exposed pattern in consumer subscription apps.

## 7.6 Small Business Program

The human qualifies: **15% commission** instead of 30%, up to $1M proceeds per calendar
year. Wire RevenueCat exactly as in their existing app.

---

# PART 8 — WHAT ACCRUES (solving the twelve-month problem)

Both of these are required in v1, not deferred. They are the answer to a 23–40% first
annual renewal.

## 8.1 The taper adapts

After 7 completed sessions, stop using the fixed `−0.5/min` taper and derive it from the
user's own history:

- Track the median rate at which they **abandon** sessions (from `abandoned_at_ms`
  cross-referenced with the rate at that time). If they consistently bail during the
  steep part, flatten the taper for them.
- Track their **start rate trend**. If their measured start rate is drifting down over
  weeks, lower the floor slightly (to a minimum of 5/min).
- Surface this once, plainly: *"Your taper has adjusted to you."*

This must be genuine adaptation to stored data, not a cosmetic message.

## 8.2 The record deepens

The sparkline on the ledger gains resolution with tenure: 7 nights, then 30, then 90,
then a full year view with month bands. At night 200 the user has an artifact that did
not exist at night 5. That is the renewal argument.

---

# PART 9 — VISUAL DESIGN

This app is almost UI-less, and that is the design. Restraint is the aesthetic.

```
Ritual background   #000000 (true black — OLED pixels off, minimum light in a dark room)
Ritual indicator    #FFFFFF at 8% opacity (18% if haptics are disabled)
Ledger background   #0B0D10
Ledger primary      #E8EAED
Ledger secondary    #7E858D
Sparkline           #6E8FB8 line, no fill, 2px, endpoint dot emphasized
Accent (paywall)    #6E8FB8
```

- Typography: system font. Large, light weight, generous line height. The word "Down"
  is the largest type in the app.
- Motion: the breathing indicator only. Everything else cross-fades at 240ms. No
  springs, no bounce, no confetti, no celebration — ever.
- Respect `prefers-reduced-motion`: the indicator stops scaling and instead fades
  gently between two opacities.
- Full VoiceOver support. This app is genuinely usable eyes-closed, which makes it
  strong for blind users — build to that standard properly rather than accidentally.

---

# PART 10 — COMPLIANCE (read carefully; this one has teeth)

## 10.1 Health claims — the hard rule

**Never claim a physiological or medical effect.** Not in the app, not in the store
listing, not in a screenshot, not in marketing.

**Banned:** "lowers your heart rate", "treats insomnia", "reduces anxiety", "improves
sleep quality", "clinically", "therapeutic", "reduces stress", any citation of a study
implying efficacy.

**Allowed:** "a twenty-minute wind-down ritual", "a pulse that slows", "for the twenty
minutes before you sleep."

Rationale: efficacy claims risk App Review rejection, invite regulated-medical-device
scrutiny, and create FTC exposure. Apple has been tightening on health claims. Stay
purely experiential. The ledger reports **what the app did** ("you started at 15"), never
what the user's body did.

Category: **Health & Fitness**. Age rating **4+**. Do not use HealthKit in v1 — it drags
in review scrutiny and a privacy surface we do not need.

## 10.2 Other platform rules

- Subscriptions: 7-day minimum term, demonstrable ongoing value (3.1.2). Our ongoing
  value is the adapting taper plus seasonal beds — make sure that is real.
- `UIBackgroundModes: audio` must be genuinely used for continuous audible playback.
- No randomized purchasables of any kind, ever. Nothing here needs them.
- Privacy: all data is local. Say so plainly on the store page and in a one-screen
  privacy policy. No tracking, no IDFA, no ATT prompt needed. **This is a marketing
  asset** — lead with it.
- Apple's 2025–26 age-rating overhaul added a mandatory Social Media capability
  declaration from September 2026. We have no UGC and no feed, so we answer no — which
  also keeps us outside iOS 27's parental Time Allowances category caps.

---

# PART 11 — BUILD PLAN

**Day 1 — the two gates.** New Expo project, EAS dev build.
  (a) Confirm `react-native-audio-api` runs on device; play a 60 Hz sine and a brown
      noise loop.
  (b) **The haptic jitter measurement from 2.3.** Report mean, σ, worst case.
  Also: a 3-minute paper-thin version of the ritual — pulse at a fixed 12/min, brown
  noise bed, no taper, no UI. **I lie down and hold it for three minutes and tell you
  whether being pulsed at feels calming or irritating.** That is the 1.4 hypothesis
  test, and it costs one day. If it feels irritating, stop and tell me.

**Days 2–4 — the ritual.** Calibration with median-of-4. The rate model and taper. The
full 20-minute session state machine. Keep-awake, true-black screen, breathing
indicator. Session persistence to SQLite. No audio polish yet.

**Days 5–7 — the audio engine.** Brown-noise bed, droplet grain bank, breath-synced
swell, the master lowpass taper. The three beds as parameter sets. Phase 2 background
continuation with the audio entitlement. Interruption handling.

**Days 8–9 — the ledger and the shell.** Morning ledger, sparkline, x-of-last-30
counter. Settings. RevenueCat wired, paywall built but behind a flag.

**Day 10 — the tuning panel** (Part 12), and the debug CSV export of the `sessions`
table.

**Then: I use it for seven consecutive nights** and we look at the data together.

## Acceptance criteria

- Haptic inter-pulse σ under 8ms across a full 20-minute session (or the native module
  is built and it is under 2ms)
- Audio↔haptic perceptual offset under 30ms on the built-in speaker
- Zero audio level increases at any point after the first 30 seconds
- Battery drain over a full 20-minute Phase 1 session reported and under 8%
- Screen stays on for all of Phase 1; audio survives backgrounding in Phase 2
- No crash across an interrupted session (incoming call mid-ritual)
- App fully usable with VoiceOver and with haptics disabled
- All data local; no network calls except RevenueCat

## The go/no-go

After seven nights, I answer:

1. Did being pulsed at feel calming, or irritating? *(the 1.4 hypothesis)*
2. Did you hold the phone, or did you want to put it on the nightstand? *(the posture
   hypothesis)*
3. On how many of the seven nights did you open it **without me reminding you**?
4. Did you ever finish the 20 minutes and want another 20?

Question 3 is the real gate. **Under 4 of 7 and we stop.** Better to learn that in ten
days than after three months of polish.

---

# PART 12 — THE TUNING PANEL

I cannot hear or feel anything; I am your instrument. Give me direct control.

**Access:** five taps on the "Night N" label on the ledger. Dev builds only.

Every parameter gets a live slider showing its numeric value, applying immediately
without restarting the session:

```
RITUAL
  holdDurationMin        0 – 10 min
  taperRatePerMin        0.1 – 2.0 breaths/min per min
  floorRate              4 – 10 breaths/min
  inhaleExhaleRatio      0.25 – 0.6
  totalDurationMin       10 – 40 min
  fadeOutDurationMin     1 – 8 min

HAPTICS
  hapticsEnabled         bool
  inhaleStyle            Light | Medium | Soft | Rigid | none
  exhaleStyle            Light | Medium | Soft | Rigid | none
  thinningStartPct       0 – 100 %   (when intensity taper begins)

AUDIO — per bed (tabs: Rain / Hull / Field)
  bedGain                0 – 1
  noiseBandpassHz        120 – 3000
  noiseBandpassQ         0.1 – 2
  dropletRate            0 – 12 /s
  dropletDecayMinMs      20 – 400
  dropletDecayMaxMs      20 – 400
  dropletFreqMinHz       150 – 3000
  dropletFreqMaxHz       150 – 3000
  dronePitchHz           40 – 120
  swellDepth             0 – 1
  swellAttackMs          100 – 3000
  lowpassStartHz         800 – 6000
  lowpassEndHz           120 – 1200
  lowpassGlideSec        0.05 – 2
```

**Include a "Copy config as JSON" button.** I paste it back to you; that is our tuning
protocol. Ship the Part 5 defaults so the first build already sounds close.

Also include **"Export sessions CSV"** — dumps the `sessions` table to the share sheet.
That is how we look at abandonment together.

---

# PART 13 — STORE AND ASO

Organic is the only channel — plausible CPI in sleep/meditation runs **$4–9** against
roughly $1–2 of gross per install, so **paid acquisition is unprofitable at any scale
we could run.** Do not plan for it.

- Category: Health & Fitness. Age 4+.
- Title/subtitle must carry the searched words: "wind down", "sleep", "breathing",
  "calm down". Working title *Downshift*; the subtitle does the discovery work.
- **No "ASMR" anywhere.** No health claims anywhere (Part 10).
- Screenshots: this is a nearly-black app, which is a genuine product-page conversion
  problem. Solve it with typographic screenshots that state what it does, plus one
  photo-real image of a hand holding a phone in the dark. Do not fake a UI that does
  not exist.
- An app preview video is worth making — the taper is a time-based idea and static
  images cannot convey it.
- **Lead with "all data stays on your phone."** In this category that is a real
  differentiator and it is free.

---

# PART 14 — HOW TO WORK WITH ME

- **Windows.** Never suggest local Xcode. Device builds go through **EAS**. Tell me
  explicitly when I need a new dev build versus an OTA update — dev builds are slow and
  I batch them.
- **You cannot hear or feel anything.** Never assert that the pulse "should feel
  calming" or the bed "should sound soothing." Describe parameters, then ask me.
- When something is a judgement call about feel, **give me a slider, not a value.**
- Ask before adding any dependency not in 2.2.
- Keep the tuning panel and CSV export out of production builds.
- If something in this document turns out to be wrong on real hardware — especially the
  haptic jitter, the audio library, or the background audio behavior — **tell me it was
  wrong** rather than quietly working around it.
- This app is used by someone lying in the dark trying to sleep. Every decision should
  be made in that context. When in doubt, do less.
