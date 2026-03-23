
## v2.0.0 -- In Progress (updated)

### Experiments passing (7/9):
- exp_00: Causal cone -- speed limit c=1 confirmed
- exp_01: Inertia -- phase gradient persistence, linear trajectory
- exp_02: Gravity -- clock density gradient, differential Zitterbewegung
- exp_03: Interference -- genuine discrete fringes, no analytical formula
- exp_04: Decoherence -- phase scrambling collapses two-source pattern
- exp_06: Path counting -- discrete corrections, falsifiable predictions
- exp_07: Clock conservation -- continuity equation confirmed (Step 1 of GR)

### Remaining stubs:
- exp_05: Observer as clock (TickScheduler combinatorics)
- exp_08: Vacuum twist (gravity vs EM as div vs curl)

# CHANGELOG

## v2.0.0 -- In Progress

### New in v2.0
- 3D octahedral lattice substrate (T^3_diamond) replaces 1D diamond
- Per-particle tick counters and TickScheduler
- Observer formalized as a new clock (CausalSession) in the scheduler
- Gravity reframed as clock density gradient (not refractive potential)
- Genuine discrete interference (no continuous Huygens-Fresnel formula)
- Falsifiable numerical predictions via exact path counting
- Biological time / Eagleman connection in introduction

### Corrections from v1.0
- exp_04 interference: replaced continuous analytical formula with
  genuine lattice tick propagation
- alpha derivation removed: 0.01984 was hardcoded into noise function,
  not discovered by the simulation
- Gravity experiment: clock density mechanism made explicit,
  not just a potential well

## v1.0.0 -- January 2026

Initial release. 1D diamond lattice. 9 experiments.
DOI: 10.5281/zenodo.18904545
Repository: github.com/JackDMenendez/A-Stochastic-Geometric-Foundation-for-Physics
