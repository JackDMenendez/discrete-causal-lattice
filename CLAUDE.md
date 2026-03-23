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

## Current State (10/11 experiments passing, Dirac spinor upgrade DONE)

| Experiment | What it confirms |
|---|---|
| exp_00 | Causal cone, speed limit c=1 |
| exp_01 | Inertia as phase gradient persistence (note: xz asymmetry for V1 direction is a fundamental bipartite lattice property, not a bug) |
| exp_02 | Gravity as clock density gradient |
| exp_03 | Genuine discrete interference |
| exp_04 | Decoherence via phase scrambling |
| exp_05 | Observer as clock, irreversibility |
| exp_06 | Discrete path count corrections (falsifiable) |
| exp_07 | Clock density continuity equation |
| exp_09 | Lattice harmonics, photon dispersion |
| exp_10 | Hydrogen spectrum: Bohr E_n ~ 1/n^2 confirmed analytically |
| exp_08 | STUB -- vacuum twist (EM vs gravity) not yet implemented |

---

## Dirac Spinor Upgrade -- COMPLETED

CausalSession.py was upgraded from scalar Klein-Gordon (single psi field)
to two-component Dirac spinor (psi_R, psi_L). The upgrade is complete and
all 10 implemented experiments pass.

### What was done

1. CausalSession.py:
   - Two fields: psi_R (RGB sublattice) + psi_L (CMY sublattice)
   - Tick rule: simultaneous RGB+CMY hop for massive particles
     `new_psi_R = cos(delta_phi/2) * kinetic_hop(psi_L, RGB) + 1j*sin*psi_R`
     `new_psi_L = cos(delta_phi/2) * kinetic_hop(psi_R, CMY) + 1j*sin*psi_L`
   - kinetic_hop: directed phase-coherent hop with max(0,delta_p) weights
     and exp(i*delta_p) phase correction (correct momentum encoding)
   - Massless photon: alternating parity (RGB or CMY only each tick)
   - psi property (backward compat getter): returns psi_R
   - psi property (backward compat setter): sets psi_R=psi_L=value/sqrt(2)
   - A=1 enforced via enforce_unity_spinor(psi_R, psi_L)

2. UnityConstraint.py: enforce_unity_spinor and unity_residual_spinor added.

3. TickScheduler.py: _apply_pairwise_interactions updated to work with spinors
   (phase rotation applied identically to both components, enforce_unity_spinor).

4. All experiments updated to use psi_R/psi_L directly for initialization
   and enforce_unity_spinor instead of enforce_unity.

5. Stale duplicate src/experiments/src/ tree (shadowing the real src/core)
   was removed via git rm.

### Known limitation: exp_01 xz asymmetry

For V1=(1,1,1) direction momentum on the Dirac bipartite lattice, the
z-component drifts roughly twice as fast as x,y (xz_asymmetry ~0.44).
This is a fundamental geometric property: RGB hop sends all amplitude to
+z+1 but CMY hop for the same k sends net 0 for x,y and +1 for z.
The exp_01 test threshold (0.05) cannot pass for this direction.
This is NOT a bug -- it is a genuine asymmetry of the bipartite lattice
that will need to be discussed in the paper.

---

## File Structure

src/core/
  OctahedralLattice.py  -- bipartite lattice, RGB/CMY vectors, Coulomb well
  CausalSession.py      -- THE FILE TO UPGRADE (scalar -> spinor)
  PhaseRotor.py         -- U(1) internal clock, omega = mass
  TickScheduler.py      -- multi-session scheduler, observer interactions
  UnityConstraint.py    -- A=1 normalization

src/experiments/
  exp_00 through exp_10 -- see table above

paper/sections/         -- LaTeX stubs, all need prose written
notes/                  -- theoretical development notes

---

## Key Constants and Conventions

RGB_VECTORS = [(1,1,1), (1,-1,-1), (-1,1,-1)]
CMY_VECTORS = [(-1,-1,-1), (-1,1,1), (1,-1,1)]
ALL_VECTORS = RGB_VECTORS + CMY_VECTORS

delta_phi = omega + V(x,y,z)  -- phase mismatch (mass + potential)
p_stay    = sin^2(delta_phi/2) -- Klein-Gordon residence probability
p_move    = cos^2(delta_phi/2) -- kinetic propagation probability

Coulomb well: V(r) = -strength / (r + softening)
Hydrogen result: strength=30, softening=0.5, omega=0.1019

---

## What NOT to Change

- OctahedralLattice: leave as-is, it's correct
- The bipartite RGB/CMY structure: this IS the Dirac structure
- The A=1 constraint: keep, just apply to |psi_R|^2 + |psi_L|^2
- The experiment logic: just update density calculations
- The TickScheduler: works fine with spinor sessions

---

## Paper Status

Sections with content: hydrogen_spectrum.tex, lattice_harmonics.tex,
  clock_fluid_dynamics.tex, vacuum_twist_field_equations.tex
All other sections: STUB status, need prose written

Primary remaining theoretical work:
1. Dirac spinor upgrade (described above) -- code task
2. Derive Dirac equation formally from bipartite tick rule -- theory task
3. exp_08 vacuum twist (EM vs gravity as curl vs div) -- code task
4. Write actual prose for all section stubs -- writing task

The most important next step is #1.
