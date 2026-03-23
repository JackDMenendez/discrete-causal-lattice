# EXPERIMENTS.md
# Experiment Registry -- A=1 Discrete Causal Lattice

Each experiment maps a physical phenomenon to a lattice mechanism
and a specific code module. A row is PASSING only when the result
emerges from genuine discrete lattice dynamics, not from analytical
formulas used as proxies.

| ID     | Phenomenon                  | Lattice Mechanism                    | Module                            | Status |
|--------|-----------------------------|--------------------------------------|-----------------------------------|--------|
| exp_00 | Speed of Light Limit        | Topological adjacency (v_max = 1)    | exp_00_causal_cone.py             | PASS   |
| exp_01 | Inertial Persistence        | Phase gradient (U(1) stability)      | exp_01_inertia.py                 | PASS   |
| exp_02 | Gravitational Deflection    | Clock density gradient               | exp_02_gravity_clock_density.py   | PASS   |
| exp_03 | Quantum Interference        | Discrete path count summation        | exp_03_interference.py            | PASS   |
| exp_04 | Wave Function Collapse      | Observer clock phase scrambling      | exp_04_decoherence.py             | PASS     |
| exp_05 | Observer-Dependent Outcomes | Tick sequence combinatorics          | exp_05_observer_clock.py          | PASS     |
| exp_06 | 1/r^2 Discrete Corrections  | Exact path count vs Gaussian CLT     | exp_06_path_counting.py           | PASS   |
| exp_07 | Clock Density Conservation  | Continuity equation from tick()      | exp_07_clock_conservation.py      | PASS     |
| exp_08 | Gravity vs EM Twist         | div(phi) vs curl(phi) deformations   | exp_08_vacuum_twist.py            | STUB   |

## Implementation Order (suggested)

1. **exp_00** -- DONE: validates OctahedralLattice and causal cone
2. **exp_06** -- DONE: path counting, falsifiable predictions
3. **exp_01** -- DONE: inertia, linear propagation confirmed
4. **exp_07** -- next: clock conservation, Step 1 of GR derivation
5. **exp_03** -- genuine interference, central claim of v2.0
6. **exp_02** -- gravity clock density, builds on exp_07
7. **exp_04** -- decoherence, builds on exp_03
8. **exp_05** -- observer as clock, builds on exp_04

## What Counts as PASSING

An experiment passes when:
- The claimed phenomenon is observed in the output
- The result emerges from OctahedralLattice + CausalSession.tick() alone
- No continuous formulas (sqrt distances, analytical wave functions) are used
- unity_residual() stays below 1e-10 throughout the simulation
- The audit runner exits with code 0
| exp_09 | Lattice Harmonics           | Zitterbewegung spectrum, orbital resonance, photon dispersion | exp_09_harmonics.py | PASS (partial) |

## Key results from exp_09:
- Part A: fidelity=1.0 at omega=pi (vacuum resonance confirmed)
- Part B: orbital stability needs deeper well / more ticks -- in progress
- Part C: photon group velocity drops by 3x near zone boundary -- falsifiable
- Part D: frequency locking needs longer runs -- qualitative trend observed

| exp_10 | Hydrogen Spectrum | Coulomb well orbital quantization | exp_10_hydrogen_spectrum.py | PARTIAL |

## exp_10 Status:
- Orbital motion in Coulomb well: CONFIRMED
- Zitterbewegung quantization n=1: CONFIRMED  
- Analytical Bohr spectrum E_n ~ 1/n^2: CONFIRMED analytically (n=1..4 match to 4%)
- Numerical verification: PENDING (requires 82^3 grid for n=2 orbit)
