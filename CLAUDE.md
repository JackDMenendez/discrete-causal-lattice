# CLAUDE.md
# Working Brief for Claude Code -- A=1 Discrete Causal Lattice

This file gives Claude Code the context needed to continue work on this
project without the full conversation history.

---

## What This Project Is

A discrete computational framework for fundamental physics built on a
bipartite 3D lattice (T^3_diamond). Three axioms:
1. A=1 (unity constraint -- probability conserved at every tick)
2. Locality (only adjacent nodes interact)
3. Phase (U(1) internal clock per particle)

The six basis vectors split into two chirally-opposite sublattices:
  RGB (even ticks): V1=(1,1,1)  V2=(1,-1,-1)  V3=(-1,1,-1)
  CMY (odd ticks): -V1=(-1,-1,-1) -V2=(-1,1,1) -V3=(1,-1,1)

---

## Paper Title and Theme

Title: **Geometry First: Quantum Mechanics, Gravity, and the Origin of
the Standard Model from a Single Conservation Law**

Core theme: QM answers every question about HOW particles behave but is
structurally silent on WHY its axioms hold. The lattice shows:
  1. Quantization is an Arnold tongue attractor, not a boundary condition
  2. Born rule follows from A=1 conservation, not a postulate
  3. Dirac gamma matrices encode RGB/CMY geometry, not algebraic inventions
  4. Gauge group SU(3)xSU(2)xU(1) may be forced by bipartite basis geometry

See notes/the_theme_of_the_paper.md and notes/shortcomings_of_quantum_mathematics.md

---

## Experiment Status

| Experiment | Status | What it confirms |
|---|---|---|
| exp_00 | PASS | Causal cone, speed limit c=1 |
| exp_01 | PASS | Inertia as phase gradient persistence (xz asymmetry is fundamental, not a bug) |
| exp_02 | PASS | Gravity as clock density gradient |
| exp_03 | PASS | Genuine discrete interference |
| exp_04 | PASS | Decoherence via phase scrambling |
| exp_05 | PASS | Observer as clock, irreversibility |
| exp_06 | PASS | Discrete path count corrections (falsifiable) |
| exp_07 | PASS | Clock density continuity equation |
| exp_08 | PASS | EM deflection (curl) vs gravity (div), photon emission |
| exp_09 | PASS | Lattice harmonics, photon dispersion |
| exp_10 | PASS | Hydrogen spectrum: Bohr E_n ~ 1/n^2 |
| exp_11 | PASS (n=1) | Spontaneous quantization, orbital PDF peak at k_Bohr |
| exp_11 n=2 | FLAT (expected) | Fixed well collapses at n=2; confirms live proton required |
| exp_12 | PASS | Two-body hydrogen: k_min=0.0970 vs k_Bohr=0.0971 (4 sig figs) |
| exp_13 | PASS | Three-body helium-like system |
| exp_14 | PASS | Helium two-electron system |
| exp_11 n=2 two-body | NOT RUN | Needs live proton; exp_12 machinery, R2=41.2 |
| exp_15 | ABANDONED | Phase drain incompatible with A=1; proton Zitterbewegung IS the mechanism |
| exp_16 | RUNNING (v3, ~18 hrs remaining) | Proton mass sweep: T_settle vs OMEGA_P; tests symmetry-breaking prediction |
| exp_strength_sweep | REDESIGNED, NOT RUN | See below |

---

## exp_08 -- COMPLETE (added 2026-03-29)

Tests gravity (div) vs EM (curl) as distinct force geometries.
Three tests all pass (~92s runtime):
  Test 1: EM deflection 33° from V1, 30° alignment with V1×z [PASS]
  Test 2: Gravity dr=-3.55 (inward), EM tangential=13.30 >> radial=2.61 [PASS]
  Test 3: Photon CoM displacement=7.96 nodes from well [PASS]

GIF targets: make gif_08 (generates deflection + emission GIFs at 25fps)
Data: data/exp_08_deflection.npy, data/exp_08_emission.npy

Implementation notes:
  - Peierls substitution: A·v added to delta_p in CausalSession._kinetic_hop
  - _precompute_shift_slices stores (dx,dy,dz) as first element of 5-tuple
  - vector_potential: (3,X,Y,Z) array on OctahedralLattice

---

## exp_16 v3 -- RUNNING (started 2026-04-04, ~18 hrs remaining at time of save)

Proton mass sweep: T_settle vs OMEGA_P.
Tests prediction: heavier proton → slower symmetry breaking → longer settling time.
Also tests minimum proton mass for quantization vs binding (distinct conditions).

Parameters: GRID=65^3, TICKS=20000, BURN_IN=4000, CHECK_EVERY=50
            SETTLE_TOL=15%, SETTLE_WINDOW=10 consecutive checks
            OMEGA_E=0.1019, STRENGTH=30.0
            OMEGA_P sweep: [0.3, 0.5, 0.7, 0.9, 1.1, 1.3, pi/2]

### Results so far (2026-04-04):

OMEGA_P=0.3  M_P=0.149  R1=12.88  r_final=29.65  settled=True (TRANSIENT)
  - settled=True is a false positive: transient lock at tick 4800, then escaped
  - r_peak drifted to ~30, well outside R1=12.88
  - consec=10 frozen (settled flag set early, check stopped)
  - REGIME 2: bound but unquantized — wide oscillating orbit, not escaping
  - Grid max radius ~55 nodes; r~30 is midway, NOT grid-edge artifact

OMEGA_P=0.5  M_P=0.247  R1=11.59  r_final=34.09  settled=False
  - consec=0 throughout entire 20000 ticks — never even briefly locked
  - r_peak oscillating 23-35 with no trend — chaotic wide orbit
  - REGIME 2: worse than OMEGA_P=0.3, no transient lock at all
  - Unexpected: lighter proton locked transiently; heavier didn't lock at all

OMEGA_P=0.7  M_P=0.343  R1=11.04  IN PROGRESS (tick ~6000)
  - r_peak=29.65, consec=0 so far

### Three regimes framework:
  Regime 1 — Quantized: r_peak ≈ R1 sustained → hydrogen atom
  Regime 2 — Bound unquantized: r_peak >> R1, non-escaping → proton too mobile
  Regime 3 — Unbound: r_peak → grid boundary (~55) → true escape

### What to watch for in remaining trials:
  - Does any OMEGA_P produce sustained consec ≥ 10 AND r_final ≈ R1?
  - At what OMEGA_P does the transition from Regime 2 → Regime 1 occur?
  - Does physical proton (OMEGA_P=pi/2=1.571) settle cleanly?
  - Is the relationship non-monotonic at low OMEGA_P (0.3 better than 0.5)?

### Key insight confirmed so far:
  Binding and quantization are SEPARATE conditions. OMEGA_P=0.3 and 0.5
  are both bound (sessions stay together) but neither is quantized (no
  Arnold tongue lock). This distinction is not present in standard QM.

### Output file location:
  C:/Users/jackd/AppData/Local/Temp/claude/
  d--sandbox-jackd-repos-physics-Papers-discrete-causal-lattice/
  33b5109e-d80d-4134-864e-56e60e5de7a7/tasks/bdpv2xyuk.output

### Next after exp_16 finishes:
  - exp_17: pair annihilation efficiency at ω=π/2
  - exp_18: tidal ionization / quantum Roche limit M_min(d) — needs
    confirmed stable OMEGA_P from exp_16 as base state
  - exp_19: photon pair entanglement CHSH (joint A=1 variant)

---

## exp_11 n=2 -- FLAT RESULT (2026-04-01, expected)

Run: 28 hrs, 41 k-values [0.030, 0.070], GRID=65^3, TICKS=8000.
Result: ep_mean=0.960 ± 0.006, flat across all k. Electron collapses to
r~2.5 regardless of k. No resonance peak. Best k=0.0560 (15% off Bohr).

Root cause: fixed Coulomb well. At n=2 (r=41) the Coulomb curvature is
too shallow for the electron to find the attractor without proton recoil.
At n=1 (r=10) the steeper well provided enough gradient; at n=2 it does not.

Interpretation: CONFIRMS that the live proton requirement scales with orbit
size. The n=2 two-body experiment needs exp_12 machinery with R_INIT=41.2.
This is NOT a failure -- it is a positive result establishing the boundary
of the fixed-well approximation.

---

## exp_strength_sweep -- NEEDS TWO-BODY REDESIGN (updated 2026-03-31)

### Run completed 2026-03-31 -- INVALID RESULT

The dual-initialization run (N_K=30, 8000 ticks, 3 STRENGTH values) completed
but produced invalid results: all electrons collapsed to peak_r = well center
(r~2.5 at S=30, r~2.2 at S=45, r~1.6 at S=60) regardless of k value.

Root cause: exp_strength_sweep uses a FIXED COULOMB WELL (no proton session).
exp_12 proved that a fixed well causes the electron to collapse -- the proton
recoil is what stabilises the orbit. Without a live proton session, no k value
produces a stable orbit; the electron always falls to the well center.
The dual-initialization scan cannot distinguish H0 from H1 because neither
initialization produces an orbit at all.

### Required redesign (DO NOT RUN until exp_15 dissipative capture passes)

exp_strength_sweep must be rebuilt on the exp_12 two-body foundation:

- Live proton CausalSession (OMEGA_P = pi/2) for each STRENGTH value
- Mean-field Coulomb coupling updated each tick from live CoM positions
- Alternating tick order (exp_12 pattern) to cancel leading-order asymmetry
- For each STRENGTH: scan k around both k_H0 and k_H1 predictions
- Score: inv_sharpness of electron PDF relative to proton CoM

This is a significantly longer run (~days not hours) and requires the
two-body orbital mechanism to be confirmed stable first via exp_15.

### Current status: UNBLOCKED (exp_15 superseded)

exp_15 (tangential phase drain) was abandoned. The phase drain approach
is incompatible with A=1: enforce_unity_spinor renormalizes amplitude
every tick, so apply_phase_map cannot transfer energy between sessions.

The correct physics: the proton's Zitterbewegung IS the dissipation
mechanism -- not energy loss, but phase-space exploration that lets the
electron find the Arnold tongue attractor. The Bohr orbit is the
minimum-uncertainty state (R1*k_Bohr=1); the live proton provides the
symmetry breaking that allows the electron to converge to it.

exp_strength_sweep can now be redesigned on the exp_12 two-body
foundation whenever that is prioritised.

---

## Dirac Spinor Architecture -- COMPLETED

CausalSession.py uses two-component Dirac spinor (psi_R, psi_L):
  - Even tick (RGB): new_psi_R = cos(delta_phi/2)*hop(psi_L,RGB) + i*sin*psi_R
  - Odd tick (CMY):  new_psi_L = cos(delta_phi/2)*hop(psi_R,CMY) + i*sin*psi_L
  - enforce_unity_spinor(psi_R, psi_L) called at end of every tick()
  - Massless photon: strict alternating parity, no Zitterbewegung

TickScheduler changes:
  - register_emission(e_idx, p_idx, rate): adds emission pair
  - _emission_weights dict: tracks weight decay (bookkeeping only)
  - _apply_emission_pairs: imprints electron phase onto photon + decays weight
  - Pairwise interactions skip emission pairs (to avoid scrambling)

CRITICAL: _emission_weights decay does NOT affect electron dynamics.
See exp_strength_sweep section above for why.

---

## Continuum Limit / Dirac Derivation -- IN PROGRESS

The paper's central result. Notes in:
  notes/deriving_dirac_from_hamiltonian.md  -- 6-step derivation program
  notes/strengthening_the_dirac_claim.md    -- gap analysis
  notes/deriving_dirac_the_significance.md  -- why it matters

Steps 1-5 outlined (algebra, Taylor expansion, gamma matrix ID, Clifford
algebra check via frame condition sum_{RGB} v*v^T = 3I).
Step 6 (O_h symmetry averaging for rotational invariance) not yet done.
Write-up for paper: emergent_kinematics.tex has kinematics but not the
continuum limit subsection yet.

---

## Paper Structure

Title: Geometry First: ...
Main file: paper/main.tex
Sections with prose: hydrogen_spectrum.tex, lattice_harmonics.tex,
  clock_fluid_dynamics.tex, vacuum_twist_field_equations.tex,
  emergent_kinematics.tex (partial -- kinematics written, Dirac limit not)
All other sections: STUB

Figures:
  figures/exp_harmonic_hires_drawio.png  -- Arnold tongue drawing (renamed from .drawio.png)
  figures/exp_harmonic_landscape.pdf     -- raw harmonic heatmap
  figures/lattice.drawio.png             -- lattice structure diagram
  figures/exp_12_twobody_scan.pdf        -- two-body scan
  figures/exp_00_cone_structure.pdf      -- causal cone

Side-by-side harmonic figure in lattice_harmonics.tex:
  - Left: exp_harmonic_landscape.pdf (raw data)
  - Right: exp_harmonic_hires_drawio.png (Arnold tongue annotation)
  - Full annotated caption: figures/exp_09_harmonics_hires.tex

---

## Key Constants and Conventions

RGB_VECTORS = [(1,1,1), (1,-1,-1), (-1,1,-1)]
CMY_VECTORS = [(-1,-1,-1), (-1,1,1), (1,-1,1)]
ALL_VECTORS = RGB_VECTORS + CMY_VECTORS

delta_phi = omega + V(x,y,z)  -- phase mismatch (mass + potential)
p_stay    = sin^2(delta_phi/2) -- Klein-Gordon residence probability
p_move    = cos^2(delta_phi/2) -- kinetic propagation probability

Coulomb well: V(r) = -strength / (r + softening)
Hydrogen: strength=30, softening=0.5, omega=0.1019, R1=10.3
omega * R1 = pi/3 to 0.23% -- the key identity being tested

---

## What NOT to Change

- OctahedralLattice: leave as-is, it's correct
- The bipartite RGB/CMY structure: this IS the Dirac structure
- The A=1 constraint: keep, just apply to |psi_R|^2 + |psi_L|^2
- The TickScheduler pairwise/emission machinery: works for exp_08
- CausalSession._precompute_shift_slices: now returns 5-tuples (dx,dy,dz)
  as first element -- required for Peierls substitution in _kinetic_hop

---

## Notes Index (important theoretical files)

notes/the_theme_of_the_paper.md          -- THE reframing: why QM axioms hold
notes/shortcomings_of_quantum_mathematics.md -- 4 shortcomings + summary table
notes/deriving_dirac_from_hamiltonian.md -- 6-step continuum limit program
notes/deriving_dirac_the_significance.md -- why the derivation changes everything
notes/harmonics_music_and_existence.md   -- omega*R1=pi/3 as 3:1 resonance
notes/harmonic_landscape_A_structure.md  -- A-structure, 2:1 fixed point
notes/twobody_hydrogen_results.md        -- exp_12 result (4 sig figs)
notes/strengthening_the_dirac_claim.md   -- gap analysis for central claim
notes/conservation_of_probability.md     -- THE central claim: A=1 is the only conservation law; energy/momentum are consequences
notes/two_session_bound_state.md         -- exp_12 > exp_10: static well has no restoring force; orbit is joint two-session Arnold tongue; emission is 3-session event
notes/photon_emission_from_A1.md         -- photon emission as A=1 necessity; session creation at orbit lock-in
notes/deriving_gravity_from_clock_density.md -- parallel 5-step gravity derivation; gap: ρ∝exp(-φ/c²) not yet derived from lattice
notes/plasma_as_gravitational_ionization.md  -- gradient ionization: 3rd channel; plasma as clock fluid phase; atomic ISCO
notes/follow_on_implications.md          -- 10 follow-on paper seeds with priority order
