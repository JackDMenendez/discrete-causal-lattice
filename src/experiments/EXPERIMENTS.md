# Experiment Registry — A=1 Discrete Causal Lattice

Each experiment maps a physical phenomenon to a lattice mechanism
and a specific code module.  A row is PASS only when the result
emerges from genuine discrete lattice dynamics, not from analytical
formulas used as proxies.

---

## Registry

| ID | Phenomenon | Lattice Mechanism | Module | Status |
| --- | --- | --- | --- | --- |
| exp_00 | Speed of Light / Causal Cone | Topological adjacency (v_max = 1) | exp_00_causal_cone.py | PASS |
| exp_01 | Inertial Persistence | Phase gradient (U(1) stability); xz asymmetry is fundamental | exp_01_inertia.py | PASS |
| exp_02 | Gravity as Clock Density Gradient | div(φ) deformation; Gaussian well | exp_02_gravity_clock_density.py | PASS |
| exp_02b | Inverse-Square Law | a·r² constant to 20% across distances; F = GMm/r² | exp_02b_inverse_square.py | PASS |
| exp_03 | Quantum Interference | Discrete path count summation | exp_03_interference.py | PASS |
| exp_04 | Decoherence / Wavefunction Collapse | Observer clock phase scrambling | exp_04_decoherence.py | PASS |
| exp_05 | Observer-Dependent Outcomes | Tick sequence combinatorics; irreversibility | exp_05_observer_clock.py | PASS |
| exp_06 | Discrete Path Count Corrections | Exact path count vs Gaussian CLT; falsifiable 1/r² correction | exp_06_path_counting.py | PASS |
| exp_07 | Clock Density Conservation | Continuity equation from tick() | exp_07_clock_conservation.py | PASS |
| exp_08 | EM Deflection vs Gravity | curl(φ) vs div(φ); Peierls substitution; photon emission | exp_08_vacuum_twist.py | PASS |
| exp_09 | Lattice Harmonics / Photon Dispersion | Zitterbewegung spectrum; orbital resonance; 3x group velocity drop | exp_09_harmonics.py | PASS |
| exp_09b | Harmonic Spectrum Analysis | f_zitt / f_beat / f_vacuum measurement vs theory | exp_09b_harmonic_analysis.py | PASS |
| exp_09c | Harmonic Landscape Hi-Res | Arnold tongue / Farey structure; ω·R₁ = π/3 identity | exp_09c_harmonic_hires.py | PASS |
| exp_10 | Hydrogen Spectrum | Coulomb well orbital quantization; E_n ~ 1/n² (n=1..4, 4%) | exp_10_hydrogen_spectrum.py | PASS |
| exp_11 | Spontaneous Quantization | Arnold tongue lock-in; orbital PDF peak at k_Bohr | exp_11_quantization_scan.py | PASS (n=1); FLAT (n=2, expected) |
| exp_12 | Two-Body Hydrogen | Live proton session; k_min = 0.0970 vs k_Bohr = 0.0971 (4 sig figs) | exp_12_hydrogen_twobody.py | PASS |
| exp_12b | Golden Ratio Persistence | Max structural persistence at p_stay = φ⁻¹ ≈ 0.618 | exp_12_golden_decay.py | PASS |
| exp_13 | Three-Body Helium-Like | Three CausalSessions; two-electron orbit confirmed | exp_13_threebody_helium.py | PASS |
| exp_14 | Helium Two-Electron System | Two electrons + live proton; ground state confirmed | exp_14_helium.py | PASS |
| exp_15 | Dissipative Capture | Tangential phase drain | exp_15_dissipative_capture.py | ABANDONED — see note |
| exp_16 | Proton Mass Sweep | T_settle vs OMEGA_P; binding vs quantization regimes | exp_16_proton_mass_sweep.py | COMPLETE — see note |
| exp_17 | Pair Annihilation Efficiency | 2:1 fixed point at ω = π/2; particle = vacuum reflection | exp_17_pair_annihilation.py | NOT RUN |
| exp_18 | Tidal Ionization / Quantum Roche Limit | Gradient detuning of Arnold tongue; g_crit < 0.004 | exp_18_tidal_ionization.py | PASS |
| exp_19 | Photon Emission (v5) | Phase-rotation drain (A=1-compatible); orbital lock-in via dissipation | exp_19_photon_emission.py | READY TO RUN |
| exp_19b | Photon Emission (v9) | Phase-gradient mismatch coupling; positive control | exp_19b_photon_emission.py | IN PROGRESS |
| exp_20 | STRENGTH Sweep | ω·R₁ = π/3 identity vs calibration (H0/H1 test) | exp_20_strength_sweep.py | REDESIGNED, NOT RUN |

### Superseded variants (kept for reference, not in audit)

| Module | Superseded by | Notes |
| --- | --- | --- |
| exp_10_v2.py | exp_12 | Corrected approach; proton recoil not yet included |
| exp_10_large.py | exp_12 | Large-grid standalone; no live proton |
| exp_10_standalone.py | exp_12 | Numpy-only standalone; no live proton |
| exp_1000_zitterbewegung.py | — | Scratch calculation; no experiment structure |

---

## What Counts as PASSING

An experiment passes when:

- The claimed phenomenon is observed in the output
- The result emerges from OctahedralLattice + CausalSession.tick() alone
- No continuous formulas (sqrt distances, analytical wave functions) are used as proxies
- unity_residual() stays below 1e-10 throughout the simulation
- The audit runner exits with code 0

---

## Notes on Key Results

### exp_08 — PASS (2026-03-29)

Three tests: EM deflection 33° from V1 / 30° alignment with V1×z; gravity dr = −3.55
(inward), EM tangential = 13.30 >> radial = 2.61; photon CoM displacement = 7.96 nodes.
Peierls substitution wired in CausalSession._kinetic_hop.
GIF targets: `make gif_08`.  Data: `data/exp_08_deflection.npy`, `data/exp_08_emission.npy`.

### exp_11 n=2 — FLAT (expected, 2026-04-01)

28-hr run, 41 k-values, GRID=65³, TICKS=8000.  ep_mean = 0.960 ± 0.006, flat across all k.
Root cause: fixed Coulomb well.  At n=2 (r=41) the curvature is too shallow without proton
recoil.  Confirms live-proton requirement scales with orbit size.  Positive result: establishes
boundary of the fixed-well approximation.  n=2 two-body experiment needs exp_12 machinery
with R_INIT=41.2.

### exp_15 — ABANDONED

Phase drain (psi -= mask*psi) is not A=1-compatible.  enforce_unity_spinor renormalises
every tick, cancelling the drain.  Same mechanism killed exp_19 v4.  The correct
dissipation mechanism is proton Zitterbewegung (phase-space exploration), not energy
extraction.  The Bohr orbit is the minimum-uncertainty state R₁·k_Bohr = 1.

### exp_16 — COMPLETE (2026-04-04)

Proton mass sweep, OMEGA_P ∈ {0.3, 0.5, 0.7, 0.9, 1.1, 1.3, π/2}, GRID=65³, TICKS=20000.
All values: Regime 2 (bound, unquantized).  Key result: binding and quantization are
SEPARATE conditions — both OMEGA_P=0.3 and 0.5 are bound but neither is quantized.
No OMEGA_P value produced sustained Arnold tongue lock-in.  Physical proton (ω=π/2) also
Regime 2.  Quantization transition (if any) not found in this sweep.

### exp_18 — PASS (2026-04-07)

Gradient suppresses Arnold tongue lock-in.  T_escape monotone vs g.
g_crit < 0.004 → Δω_tongue < 0.041 rad (4× narrower than free particle).
Tidal signature = resonance detuning (not direct stripping).  Paper §7.7 written.

### exp_19 — READY TO RUN (v5, 2026-04-09)

v4 failed: amplitude drain cancelled by enforce_unity_spinor (amp_e = 1.0000 throughout).
v5 fix: phase-rotation drain via exp(−i·mask); |rot| = 1 exactly, A=1 preserved.
EMISSION_RATES = [0.001, 0.005, 0.010, 0.020, 0.050].  5 parallel workers, TICKS=6000.
SUCCESS criterion: any rate shows streak ≥ 33 (r_peak within 15% of R₁ sustained).
Run: `python -u src/experiments/exp_19_photon_emission.py > data/exp_19_parallel_launch.log &`

### exp_20 — REDESIGNED, NOT RUN

Previous run (2026-03-31) used fixed Coulomb well → all electrons collapsed to well
centre regardless of k.  Must be rebuilt on exp_12 two-body foundation: live proton,
mean-field coupling updated from live CoM each tick, k-scan around both H0 and H1
predictions.  Unblocked after exp_15 superseded; prioritise after exp_19 settles.
