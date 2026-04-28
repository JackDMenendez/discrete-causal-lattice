<!-- markdownlint-disable MD022 MD024 MD032 MD047 MD060 -->
# exp_19c_photon_emission.py
Photon emission with A=1 recoil mechanism.

## Overview

This experiment tests the hypothesis that A=1 conservation requires physical recoil effects when electron amplitude concentrates unphysically near the nucleus. It extends exp_19 by adding a recoil mechanism that detects dangerous amplitude concentrations and applies momentum-conserving kicks to maintain both probability and momentum conservation.

## Physics Background

### The Problem with Simple Renormalization
In exp_19, photon emission was implemented as a one-way amplitude drain from electron to photon, followed by renormalization of the electron session alone. While this maintained A=1 for the electron, it didn't address the physical requirement for momentum conservation when amplitude concentrates near massive particles.

### A=1 Requires Recoil
When electron wavefunction amplitude builds up near the proton (violating physical intuition), simple renormalization is unphysical. A=1 must enforce momentum conservation through actual physical recoil - transferring momentum between sessions to prevent unphysical probability concentrations.

## Implementation

### Core Mechanism
1. **Coulomb-Driven Emission**: Amplitude drains from electron to photon based on excess potential energy above ground state
2. **Recoil Detection**: Monitors electron concentration within RECOIL_RADIUS of proton
3. **Momentum Transfer**: Applies equal/opposite kicks to electron and proton when threshold exceeded
4. **Entanglement Breaking**: Adds phase randomization to prevent correlated unphysical states
5. **Session Normalization**: Maintains A=1 for all sessions after physical effects

### Key Parameters
- `RECOIL_THRESHOLD = 0.3`: Trigger when >30% of electron amplitude within RECOIL_RADIUS
- `RECOIL_RADIUS = 2.0`: Concentration zone around proton (nodes)
- `RECOIL_STRENGTH = 0.1`: Momentum transfer per recoil event
- `ENTANGLEMENT_BREAK = 0.05`: Phase randomization strength
- Emission rates: [0.01, 0.05, 0.1, 0.2, 0.5] - Coulomb-driven drain strength

### Technical Details
- Uses exp_12 two-body initialization in center-of-mass frame
- Alternating tick order prevents leading-order artifacts
- Photon session renormalized to maintain A=1 (unlike exp_19)
- Precomputed coordinate grids for performance
- Windowed density averaging for stability assessment

## Results

### Multi-rate sweep, 6000 ticks per rate (April 2026)

A full sweep across all five emission rates was run on 2026-04-26 with `EXP19C_TICKS=6000`. Companion runs of `exp_19_photon_emission.py` (v5, phase-rotation drain) were launched in parallel for cross-mechanism comparison.

Parameters (as committed):

| Parameter | Value |
|-----------|-------|
| RECOIL_THRESHOLD | 0.2 |
| RECOIL_RADIUS | 2.0 |
| RECOIL_STRENGTH | 0.2 |
| ENTANGLEMENT_BREAK | 0.05 |
| TICKS_TOTAL | 6000 |
| SUCCESS_STREAK target | 33 |
| GRID | 65³ |
| OMEGA_E, OMEGA_P, STRENGTH | 0.1019, π/2, 30.0 |

**exp_19c v10 results (per `data/exp_19c_rate_*.log`):**

| rate | result | max_streak | recoil_events |
|------|--------|------------|---------------|
| 0.01 | NOT_SETTLED | 9 | 0 |
| 0.05 | NOT_SETTLED | 10 | 0 |
| 0.10 | NOT_SETTLED | **11** | 0 |
| 0.20 | NOT_SETTLED | 6 | 0 |
| 0.50 | NOT_SETTLED | 8 | 0 |

Per-session unitarity (`amp_e = 1.0000`) was preserved throughout. No worker crashed; `.err` files contain only the standard numpy MINGW-W64 warning.

**For comparison, exp_19 v5 (phase-rotation drain, same rates):** all five rates also returned `NOT_SETTLED` with `max_streak ≤ 5`.

### Interpretation

Three findings stand out:

1. **No settled lock-in at any rate.** The target `SUCCESS_STREAK = 33` is roughly three times the best two-session baseline (streak = 11) reported in earlier work. None of the rates approached that threshold.

2. **The recoil channel never fires.** `recoil_events = 0` for every rate. The trigger condition (more than 20% of electron amplitude within 2.0 nodes of the proton) is not met during the dynamics. The mechanism is correctly implemented but lives in a regime the orbit does not reach.

3. **The recoil mechanism does not improve on the no-photon-emission baseline.** Best `max_streak = 11` matches the streak achieved by the bare two-session orbit (no emission channel). Tonight's data is consistent with the recoil channel being inert in this parameter regime — adding it neither helps nor hurts.

4. **The 15% `SETTLE_TOL` is much wider than the predicted Arnold tongue.** The script's streak criterion accepts orbits within 15% of $R_1$, but the predicted tongue width from `data/exp_harmonic_hires_powermap.npy` is $\Delta\omega_\text{tongue} / \omega_e = 0.033 \pm 0.020$ (P5 in `predictions.tex`). Since $\omega \cdot R_1 = \pi/3$ to 0.23%, the corresponding tongue width in radius is $\Delta R / R_1 \approx 3.3\%$ — roughly **4–5× tighter** than the test's tolerance. A streak counted under `SETTLE_TOL = 0.15` therefore measures "near $R_1$," not "inside the tongue." Re-evaluated under a physics-honest tolerance (`SETTLE_TOL = 0.033`), tonight's streaks would be no larger than the values reported above and almost certainly smaller. **The negative result is stronger, not weaker, under tongue-width tolerance:** the orbit is not failing to lock onto $R_1$, it is failing to enter the tongue at all.

The smoke-test single-tick reading `r_peak = 10.280` from earlier short tests should not be cited as a settled measurement against $R_1 = 10.3$. The 6000-tick runs show the orbit ranges widely (`r_peak` between ~6 and ~55 across the sweep, depending on rate); a single-tick coincidence near $R_1$ is not a verification.

### Status

- **PARTIAL**: per-session $\mathcal{A}=1$ preserved; mechanism wired in correctly; multi-rate 6000-tick sweep complete and reported `NOT_SETTLED` at every rate.
- **Open**: whether the recoil channel is the right mechanism for the joint $\mathcal{A}=1$ + photon-emission claim. Tonight's data shows it is inert at the swept parameters and matches the no-emission baseline.
- **Open**: whether a different parameter regime, a different trigger geometry, or a different mechanism (e.g. exp_19 v5's phase-rotation drain) would settle. Both mechanisms tested so far returned `NOT_SETTLED`.
- **Open**: a quantitative claim against $R_1 = 10.3$ from a settled run.
- **Open**: tighten `SETTLE_TOL` from `0.15` to `0.033` to match the predicted Arnold tongue width before re-running. Under the current tolerance the streak counter measures proximity to $R_1$, not residence inside the tongue; any future "settled" result claimed under the loose tolerance is not a tongue-locking measurement.

The audit table row for "Photon emission as $\mathcal{A}=1$ necessity" remains at `PART`. The paper text in the abstract, introduction, and conclusion was tightened on 2026-04-26 to match this status (no quantitative `peak radius` claim is made until a settled sweep is in hand).

## Significance

### Theoretical Advance
Demonstrates that A=1 conservation requires physical recoil mechanisms beyond mathematical renormalization. This provides a concrete implementation of how fundamental conservation laws emerge from discrete lattice dynamics.

### Connection to Standard QM
The recoil mechanism implements the physical intuition that particles cannot "pile up" at nuclei without momentum transfer. This may explain why quantum mechanics requires both probability and momentum conservation as fundamental postulates.

### Arnold Tongue Insight
The experiment's results support the view that stable quantum states occur at resonance region boundaries, not exact resonance centers. This has implications for understanding how discrete systems give rise to continuous quantum behavior.

## Relation to Other Experiments

### vs exp_19
- Adds recoil mechanism to exp_19's emission framework
- Photon renormalization prevents instability
- Focus on A=1 as momentum conservation, not just probability

### vs exp_12
- Uses same two-body initialization
- Adds photon emission and recoil
- Tests stability under dissipative processes

### vs exp_16
- Proton mass from exp_16 (Ω_P = π/2)
- Electron frequency from hydrogen spectrum
- Combines quantization results with emission physics

## Future Directions

### Parameter Optimization
- Tune RECOIL_THRESHOLD, RECOIL_STRENGTH for different orbital regimes
- Test different RECOIL_RADIUS values
- Explore emission rate dependence

### Theoretical Extensions
- Investigate recoil statistics vs emission rate
- Study entanglement breaking effects
- Connect to gravitational ionization (exp_18)

### Experimental Validation
- Compare with exp_19 results
- Validate against exp_10/11 quantization
- Test edge cases (very high/low emission rates)

## Files
- `src/experiments/exp_19c_photon_emission.py`: Main experiment code
- `data/exp_19c_rate_*.npy`: Results for each emission rate
- `data/exp_19c_rate_*.log`: Detailed logs with progress and diagnostics

## Status
- **Implementation**: Complete ✓
- **Testing**: Single rates validated ✓
- **Parallel Sweep**: In progress
- **Documentation**: This file
- **Audit Table**: Ready for inclusion