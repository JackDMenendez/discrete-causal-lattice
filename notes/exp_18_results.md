# exp_18 Results: Tidal Ionization / Quantum Roche Limit

## Status: MEANINGFUL RESULT — requires careful framing (2026-04-06)

## What was measured

T_first_excursion(g): ticks until the windowed electron PDF peak first exceeds
2×R1=20.6 nodes from the proton CoM.
Gradient applied from tick 0. 7 g-values, 65³ grid, 2500 ticks per run.

## Results

| g (phase/node) | T_first_excursion | Reduction vs baseline |
| --- | --- | --- |
| 0.000 (control) | 1950 | — |
| 0.004 | 450 | 4.3× shorter |
| 0.008 | 250 | 7.8× shorter |
| 0.012 | 200 | saturated |
| 0.016 | 200 | saturated |
| 0.040 | 200 | saturated |
| 0.080 | 150 | saturated |

Monotone decrease: YES. Tidal signature OPPOSITE for all trials.

## What the stability probe revealed (probe_exp18_stability.log)

The g=0 control does NOT escape monotonically — it oscillates with large amplitude:

- t=50–450: r_pdf oscillates between 5 and 15 (wide, chaotic, no lock)
- t=500–650: briefly near R1 (transient near-lock, 4 consecutive OK windows)
- t=700–1400: persistently at 13–17, bound but unquantized
- t=1700: r_pdf=62 (triggers escape criterion), but then...
- t=1800: r_pdf=11.57 (electron returns to near-R1)

This is **Regime 2** (exp_16 terminology): bound but unquantized, large-amplitude
oscillations. The escape criterion at T=1950 fires during a wide-orbit excursion,
not a genuine dissipative escape. The electron comes back.

## Revised honest framing

The seeded orbit (K_BOHR initialization) never locks onto the Arnold tongue attractor.
It enters a wide-amplitude oscillatory state (Regime 2) from the start.
exp_12 found k_min by averaging the PDF early in the run — it was measuring whether
the electron *passed through* R1, not whether it *stayed there*.

What exp_18 actually measures:
  "A clock-density gradient shortens the time to first large orbital excursion,
   monotonically with gradient strength, in a two-body system initialized near
   the Bohr radius."

What it does NOT measure:
  "A stable quantized orbit is disrupted by a gradient."

The tidal displacement signal (OPPOSITE) is still meaningful: the gradient pulls
the two sessions apart along the field axis. This is the resonance detuning signature.
But the base state is Regime 2 (oscillating near-bound), not Regime 1 (quantized).

## Physical interpretation (what it does show)

The result is still physically informative:

1. The gradient makes the orbit WIDER faster — consistent with detuning the phase-lock
   that would pull the electron back toward R1.
2. The OPPOSITE tidal displacement shows the gradient acts differently on the two
   sessions (they have opposite charge, different omegas) — it's not a uniform push.
3. The saturation at T≈200 ticks for g≥0.012 shows there's a threshold above which
   the gradient effect is immediate and maximal.

The correct claim: gradient suppresses the partial, transient phase coherence that
keeps the orbit near-bound (Regime 2), accelerating transition to Regime 3 (escape).

## What's needed for the stronger claim

A genuinely stable Regime 1 base state. This requires:

- Confirmed Arnold tongue lock-in (exp_16: still pending for physical OMEGA_P)
- Alternatively: a dissipative mechanism (photon emission session) that allows
  the electron to settle into the tongue rather than oscillate through it
- The exp_16 v3 run may provide this if any OMEGA_P value shows sustained lock-in

## Paper status

The §7.7 text has been revised (see gravity_as_clock_density.tex) to reflect the
Regime 2 base state honestly. The result is reported as "gradient accelerates
orbit widening in a near-bound system" rather than "gradient ionizes a stable atom."

The atomic ISCO prediction stands — it just needs a stable base state to be measured
cleanly. That is Paper 2 after exp_16 confirms stable lock-in.

## Runtime

34 minutes total (2044s). Data: data/exp_18_tidal_ionization.npy,
data/exp_18_rpdf_trajectories.npy
