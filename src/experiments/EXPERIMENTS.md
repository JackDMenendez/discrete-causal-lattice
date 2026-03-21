# EXPERIMENTS.md
# Experiment Registry -- A=1 Discrete Causal Lattice

Each experiment maps a physical phenomenon to a lattice mechanism
and a specific code module. A row is PASSING only when the result
emerges from genuine discrete lattice dynamics, not from analytical
formulas used as proxies.

| ID     | Phenomenon                  | Lattice Mechanism                    | Module                            | Status |
|--------|-----------------------------|--------------------------------------|-----------------------------------|--------|
| exp_00 | Speed of Light Limit        | Topological adjacency (v_max = 1)    | exp_00_causal_cone.py             | STUB   |
| exp_01 | Inertial Persistence        | Phase gradient (U(1) stability)      | exp_01_inertia.py                 | STUB   |
| exp_02 | Gravitational Deflection    | Clock density gradient               | exp_02_gravity_clock_density.py   | STUB   |
| exp_03 | Quantum Interference        | Discrete path count summation        | exp_03_interference.py            | STUB   |
| exp_04 | Wave Function Collapse      | Observer clock phase scrambling      | exp_04_decoherence.py             | STUB   |
| exp_05 | Observer-Dependent Outcomes | Tick sequence combinatorics          | exp_05_observer_clock.py          | STUB   |
| exp_06 | 1/r^2 Discrete Corrections  | Exact path count vs Gaussian CLT     | exp_06_path_counting.py           | STUB   |

## Implementation Order (suggested)

1. **exp_00** first -- validates OctahedralLattice and CausalSession.tick()
2. **exp_06** second -- path_counter.py is pure math, no physics needed
3. **exp_01** -- validates momentum encoding in PhaseRotor
4. **exp_03** -- genuine interference, the central claim of v2.0
5. **exp_02** -- gravity, builds on interference mechanics
6. **exp_04** -- builds directly on exp_03
7. **exp_05** -- builds on TickScheduler and exp_04

## What Counts as PASSING

An experiment passes when:
- The claimed phenomenon is observed in the output
- The result emerges from OctahedralLattice + CausalSession.tick() alone
- No continuous formulas (sqrt distances, analytical wave functions) are used
- unity_residual() stays below 1e-10 throughout the simulation
- The audit runner exits with code 0
