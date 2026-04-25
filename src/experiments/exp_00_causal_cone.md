# exp_00_causal_cone.md

## Overview

**Experiment 00**: Tests the fundamental causal structure and speed limit of the $\mathcal{T}_\diamond^3$ octahedral lattice.

**Status**: PASS (core validation)

**Key Claim**: The lattice enforces a strict speed limit of 1 node/tick, with no information propagation outside the octahedral causal boundary.

## Physics Background

The discrete causal lattice implements special relativity's light cone structure geometrically. Each tick advances the wavefront by exactly one lattice spacing, establishing $c = 1$ in lattice units. The octahedral geometry ensures that:

- **Speed Limit**: No amplitude propagates faster than 1 node/tick
- **Causal Boundary**: Information is strictly confined within the octahedral cone
- **Mass-Energy Equivalence**: Particle mass determines the fraction of amplitude that remains at the origin vs. propagating outward

## Implementation

### Part A: Speed Limit Audit
- Initializes a delta function at lattice center
- Evolves for multiple ticks
- Verifies no amplitude appears outside the octahedral causal boundary
- Confirms maximum propagation speed = 1 node/tick

### Part B: Cone Shape Analysis
Compares three particles with different masses:
- **Photon** ($\omega = 0$): Fully propagates outward
- **Light particle** ($\omega = 1$): Mixed propagation/stationary behavior
- **Heavy particle** ($\omega = 2$): Mostly stationary with small outward component

For each particle, measures:
- `interior_fraction(t)`: Amplitude fraction within radius $r$ at tick $t$
- `cone_amplitude_profile`: Radial distribution at fixed tick

### Part C: Phase Engineering
- Applies linear phase gradient (momentum) to massless session
- Demonstrates cone tilting: amplitude profile becomes asymmetric
- Shows how momentum modifies the causal structure (Class 1 modification)

## Results

### Speed Limit Verification
- **PASS**: No amplitude detected outside octahedral boundary at any tick
- **Propagation Speed**: Confirmed $v_\text{max} = 1$ node/tick
- **Causal Structure**: Strict light cone enforcement

### Mass-Amplitude Relationship
For particle with frequency $\omega$:
- Stationary fraction: $p_\text{stay} = \sin^2(\omega/2)$
- Propagation fraction: $p_\text{fwd} = \cos^2(\omega/2)$
- **Mass Equivalence**: $m \propto p_\text{stay} = \sin^2(\omega/2)$

### Cone Tilting Effect
- **Linear Phase Gradient**: Causes asymmetric amplitude distribution
- **Momentum Visualization**: Cone tilts in direction of momentum vector
- **Geometric Interpretation**: Phase engineering modifies causal structure

## Significance

This experiment validates the fundamental causal structure underlying the entire framework:

1. **Speed of Light Emergence**: $c = 1$ node/tick emerges from lattice geometry
2. **Relativistic Causality**: Strict adherence to light cone structure
3. **Mass-Energy Equivalence**: Particle mass encoded in amplitude distribution
4. **Phase-Momentum Connection**: Momentum as phase gradients on the lattice

**Core Validation**: Without this causal structure, the entire framework fails. exp_00 confirms that the $\mathcal{T}_\diamond^3$ lattice correctly implements special relativistic causality at the discrete level.

## Files
- **Source**: `src/experiments/exp_00_causal_cone.py`
- **Data**: Various cone profiles and phase maps
- **Audit Function**: `run_causal_cone_audit()`

## Related Experiments
- **exp_01**: Builds on causal structure to test inertial persistence
- **exp_09**: Uses causal cones for harmonic analysis and dispersion relations</content>
<parameter name="filePath">c:\dev\dcl\src\experiments\exp_00_causal_cone.md