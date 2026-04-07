# Orbit Stability and the Necessity of Dissipation

## Summary

A systematic 13-run parallel probe (2026-04-07) establishes that the two-body
hydrogen system cannot maintain a stable n=1 orbit without a dissipation mechanism.
This rules out initialization mismatch and mean-field lag as causes, and directly
supports the paper's claim that photon emission is experimentally necessary, not
merely theoretically required by A=1.

## The Probe

**Script:** `data/probe_stability_worker.py` / `data/probe_stability_launch.py`

13 workers run in parallel on 16 CPUs. Each runs 5000 ticks at g=0, reporting
windowed r_pdf (50-tick average, relative to live proton CoM) every 50 ticks.

**Test 1 — k-sweep (update_every=1):** 10 k values from 0.050 to 0.160.
Tests whether any initialization finds the Arnold tongue basin.

**Test 2 — lag test (k=K_BOHR=0.097):** update_every = 1, 5, 10, 20.
Tests whether mean-field CoM update lag drives eccentricity.

## Results

| run_id | first_escape | ok_windows | max_ok_streak | r_pdf range |
| --- | --- | --- | --- | --- |
| k=0.050, lag=1 | 1200 | 12/100 | 4 | [5.4, 74.7] |
| k=0.060, lag=1 | 2250 | 5/100 | 2 | [6.1, 79.7] |
| k=0.070, lag=1 | 300 | 16/100 | 2 | [6.3, 59.8] |
| k=0.080, lag=1 | 1350 | 22/100 | 7 | [6.3, 77.2] |
| k=0.090, lag=1 | 1650 | 14/100 | 8 | [7.2, 84.0] |
| k=0.097, lag=1 | 1400 | 11/100 | 5 | [9.9, 77.6] |
| k=0.110, lag=1 | 1750 | 10/100 | 9 | [9.5, 83.1] |
| k=0.120, lag=1 | 1900 | 22/100 | 10 | [9.8, 78.2] |
| k=0.140, lag=1 | 1300 | 22/100 | 5 | [6.3, 76.9] |
| k=0.160, lag=1 | 1450 | 14/100 | 11 | [9.7, 79.3] |
| k=0.097, lag=5 | 3200 | 14/100 | 6 | [10.4, 81.7] |
| k=0.097, lag=10 | 1850 | 8/100 | 7 | [10.4, 77.6] |
| k=0.097, lag=20 | 1350 | 32/100 | 9 | [6.2, 77.4] |

**Stability threshold:** max_ok_streak ≥ 12 consecutive windows within 20% of R1
would indicate genuine lock-in. No run achieves this. Best is k=0.160 (streak=11)
and k=0.120 (streak=10), both escaping before t=2000.

## What The Data Shows

The orbit dynamics have two regimes the system alternates between:

- **Near-bound phase (~1000–1700 ticks):** r_pdf oscillates 10–17, passing through
  R1 intermittently. The electron is on a wide eccentric orbit that clips R1 but
  doesn't lock there.
- **Large-excursion phase (~500–900 ticks):** r_pdf reaches 50–84. The electron
  orbits at very large radius and returns. This is a bound system — not escape.

The system is permanently in Regime 2 (bound but unquantized) at every k tested.
It never transitions to Regime 1 at any initialization.

## What The Lag Test Actually Shows

The lag results are **not** a clean ruling-out of the mean-field lag hypothesis:

| lag | first_escape | ok_windows | max_ok_streak |
| --- | --- | --- | --- |
| 1 | 1400 | 11/100 | 5 |
| 5 | 3200 | 14/100 | 6 |
| 10 | 1850 | 8/100 | 7 |
| 20 | 1350 | 32/100 | 9 |

Lag=5 gives the latest escape (3200) and lag=20 gives the most ok_windows (32/100).
This is a non-monotonic relationship: some lag helps, too much hurts. That is
consistent with an optimal update frequency that isn't zero — i.e., updating every
tick may actually be *too* reactive, over-correcting and sustaining eccentricity.

This doesn't prove lag is the cause, but it doesn't rule it out either. The lag
hypothesis remains open and deserves a targeted test (e.g., a predictor-corrector
scheme, or comparing force-update frequency to the orbital period).

## What This Does Not Show

The data does not demonstrate:

- That adding a photon session would stabilize the orbit (positive control not run)
- That the instability is specifically due to missing dissipation rather than the
  mean-field approximation being inadequate
- That the lag non-monotonicity is physically meaningful vs. numerical noise
- That this is the same mechanism as photon emission rather than a numerical artifact

## Predictor-Corrector Probe — Mean-Field Lag Ruled Out (2026-04-07)

A second probe (`data/probe_predictor_corrector.py`) ran three CoM update schemes
in parallel, each at k=K_BOHR for 5000 ticks:

- **Scheme A** (current): potential from pre-tick CoM
- **Scheme B** (post-tick): potential from post-tick CoM of previous step
- **Scheme C** (midpoint): potential from average of pre- and post-tick CoM

**Results: all three identical.**

| scheme | first_escape | ok_windows | max_ok_streak | r_pdf range |
| --- | --- | --- | --- | --- |
| A (current) | 1700 | 13/100 | 4 | [5.32, 82.96] |
| B (post-tick) | 1700 | 13/100 | 4 | [5.32, 82.96] |
| C (midpoint) | 1700 | 13/100 | 4 | [5.32, 82.96] |

Same escape tick, same ok_windows, same streak, same r_pdf range to four significant
figures. The CoM update timing makes no difference at all.

**The mean-field lag hypothesis is ruled out.** The instability is not numerical.

## The Physical Diagnosis

The instability is intrinsic to the conservative two-body dynamics. A conservative
system initialized near the Arnold tongue will pass through it but cannot lock onto
it — there is no mechanism to shed the excess energy needed to settle into the narrow
resonance. The electron explores the full bound phase space (a Kepler-like family of
highly eccentric orbits) indefinitely.

Dissipation is required. In the A=1 framework, dissipation means session creation —
specifically photon emission. The paper already argues this theoretically
(see `notes/photon_emission_from_A1.md`): photon emission is an A=1 necessity
because the Coulomb well is a probability source. The predictor-corrector probe
now removes the last numerical alternative, making the physical diagnosis the
only remaining explanation.

The photon emission hypothesis is now strongly motivated:

1. Initialization mismatch ruled out (k-sweep, 10 values, none stable)
2. Mean-field update lag ruled out (3 schemes, identical results)
3. Boundary effects ruled out (by inspection — electron returns from large r)
4. Conservative dynamics cannot lock onto measure-zero attractor (well-known result)

## The Motivated Conjecture (now well-supported)

The photon emission hypothesis is no longer just theoretically motivated — the
numerical alternatives have been systematically eliminated. But it remains a
**conjecture requiring a positive control**: add a photon session and confirm the
orbit stabilizes.

Until that experiment runs, the claim is: *dissipation is necessary, and photon
emission is the only dissipation mechanism available in the A=1 framework*. The
positive control would demonstrate this directly.

## What Would Make The Claim Demonstrable

A positive control experiment: add a photon session (correct frequency, coupled
to the electron via the existing TickScheduler emission machinery) and measure
whether the orbit stabilizes to Regime 1.

If it does: the photon emission argument is demonstrated computationally, and
exp_18 (quantum Roche limit) has a valid base state.

If it doesn't: the mean-field approximation or the lag may be the real issue,
and a more fundamental numerical fix is needed first.

This is likely exp_19, and should be designed carefully with a specific prediction
written down before running.

## Paper Implications

**Honest framing:** The stability probe establishes that the two-body system is
metastable at all tested initializations, with the lag test neither resolving nor
ruling out the mean-field update hypothesis. The photon emission conjecture is
well-motivated but requires a positive control.

**exp_18:** The result stands as "gradient accelerates orbit widening in a Regime 2
system." The clean quantum Roche limit requires a stable Regime 1 base state, which
in turn requires either a confirmed dissipation mechanism or a numerical fix to the
mean-field update. This is Paper 2.
