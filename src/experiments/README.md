# discrete-causal-lattice

A discrete computational framework for fundamental physics.

Physics emerges from three axioms applied to a 3D octahedral lattice:
1. **Unity (A=1)**: amplitude is conserved at every tick
2. **Locality**: information propagates only between adjacent nodes
3. **Phase (U(1))**: each particle carries an internal clock

Every particle has its own tick counter. Gravity is clock density.
The observer is a clock. Measurement is irreversible because
you cannot un-add a clock.

## Structure

```
paper/          LaTeX source (main.tex + sections/)
src/core/       OctahedralLattice, CausalSession, PhaseOscillator,
                TickScheduler, UnityConstraint
src/experiments/ exp_00 through exp_06
src/utilities/  path_counter, lattice_calibrator, visualizer
notes/          working notes on key ideas
```

## Running the Audit

```bash
python audit_universe.py
```

## Status

Version 2.0 -- work in progress. All experiments currently STUB.
See src/experiments/EXPERIMENTS.md for implementation order.

## Citation

See CITATION.cff

## License

See LICENSE.md
