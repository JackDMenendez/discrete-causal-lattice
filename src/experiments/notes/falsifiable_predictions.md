# falsifiable_predictions.md

## Discipline
Every prediction must be:
  (a) Derived from lattice rules alone -- no free parameters
  (b) Numerically specific -- a number, not a qualitative claim
  (c) Different from the standard QM/GR prediction
  (d) In principle measurable with known or near-future technology

## Prediction 1: Discrete 1/r^2 Corrections
The exact path count P(N, dx, dy, dz) deviates from Gaussian at small N.
This is a calculable correction to the standard 1/r^2 falloff.
The crossover scale (where correction drops below 1%) depends on calibration.
At Planck calibration: crossover at ~10 Planck lengths (unmeasurable).
At Compton calibration: crossover at ~10 Compton wavelengths (~10^-11 m).
Measurable via: precision hydrogen spectroscopy? Casimir effect?
STATUS: needs count_paths() implementation to get numbers.

## Prediction 2: Minimum Time Dilation Quantum
One extra clock = one tick_duration of additional scheduler overhead.
delta_t_min = tick_duration_s for chosen calibration.
Optical atomic clocks: ~10^-18 fractional sensitivity at mm separation.
At Planck calibration: delta_t_min = 5.4e-44 s (unmeasurable).
At Compton calibration: delta_t_min = ~8e-21 s (possibly within reach?).
STATUS: needs calibration table completion.

## Prediction 3: Octahedral Anisotropy
6 preferred axes break perfect isotropy at sub-crossover scales.
Observable as directional correlations in CMB or atomic clock comparisons
oriented along vs off principal axes.
STATUS: speculative, needs theoretical development.

## Prediction 4: Decay Rate Clock-Density Correction
Particle decay is timing-dependent in this framework.
Decay rates near massive objects should have a correction term
beyond the special-relativistic time dilation already confirmed.
Measurable via: precision lifetime measurements in different
gravitational potentials (satellite vs ground experiments).
STATUS: needs tick_scheduler decay model first.

## Calibration Target Strategy
The framework needs ONE calibration that puts a prediction
within the range of a real experiment.
Best candidate so far: Compton wavelength calibration.
Next step: run exp_06 to get actual numbers.
