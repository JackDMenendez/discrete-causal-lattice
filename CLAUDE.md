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
| exp_11 n=2 | NOT RUN | ~20 hr run, needs dedicated session |
| exp_12 | PASS | Two-body hydrogen: k_min=0.0970 vs k_Bohr=0.0971 (4 sig figs) |
| exp_13 | PASS | Three-body helium-like system |
| exp_14 | PASS | Helium two-electron system |
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

## exp_strength_sweep -- REDESIGNED (2026-03-30)

### The Problem That Was Discovered

The original dissipative capture design (electron enters from outside,
photon session drains energy) CANNOT work due to A=1 architecture:
- enforce_unity_spinor is called at the END of every tick() in CausalSession
- This renormalizes psi back to A=1 every tick
- The emission weight (1-rate)^t is pure bookkeeping -- has ZERO effect
  on electron dynamics
- Electron simply follows Coulomb well and collapses to well center
- Result: peak_r = innermost bin for all k values (confirmed by 8h run)

The TickScheduler._emission_weights machinery is still present but the
physical dissipation mechanism requires rethinking. Do NOT attempt to
run the dissipative version -- it cannot work without architectural
changes to CausalSession.

### The New Design (dual-initialization, proven mechanism)

Uses the exp_11/exp_12 mechanism (no dissipation needed).
Tests whether R1_H1 = pi/(3*omega) is stable for ALL STRENGTH values.

For each STRENGTH, two parallel k scans:
  Scan A: electron initialized at R1_H1 (fixed for all STRENGTH) -- tests H1
  Scan B: electron initialized at R1_H0 (Bohr scaling) -- tests H0

Score: inv_sharpness. Sharper PDF peak = more stable orbit.
Winner (lower inv_sh across all STRENGTH) tells us which hypothesis.

H1 prediction: Scan A wins for S=30, 45, 60 (R1_H1 stable everywhere)
H0 prediction: Scan B wins for S=45, 60 (R1_H0 is the stable radius there)

Runtime: ~5 hours (3 STRENGTH x 12 k x 2 inits x 8000 ticks on 35^3)
Command: python -u src/experiments/exp_strength_sweep.py

DO NOT restart until user says so (machine reboot pending).

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
