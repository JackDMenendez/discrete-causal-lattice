# exp_02_gravity_clock_density.md

## Overview

**Experiment 02**: Tests gravity as differential Zitterbewegung from clock density gradients.

**Status**: PASS (core validation)

**Key Claim**: Gravitational attraction emerges from clock density gradients causing differential Zitterbewegung, where closer regions lag behind due to higher phase costs.

## Physics Background

In the $\mathcal{T}_\diamond^3$ framework, gravity emerges from clock density gradients rather than force vectors. Regions with higher clock density have higher phase costs per tick, causing differential Zitterbewegung:

- **Clock Density**: Higher density = higher phase cost = higher $p_\text{stay}$
- **Differential Effect**: Near side of wave packet lags, far side advances
- **Net Acceleration**: Packet spontaneously steers toward higher clock density regions
- **No Force Vector**: Acceleration emerges from phase interference, not added forces

## Implementation

### Experimental Setup
- **Lattice**: $65^3$ grid with clock density well at center
- **Particles**: Two different frequencies (masses) with zero initial momentum
- **Clock Well**: Gaussian clock density profile creating gravitational potential
- **Evolution**: 200 ticks measuring spontaneous acceleration

### Measurements
- **Center of Mass Drift**: Should accelerate toward clock density well
- **Drift Rate**: Proportional to clock density gradient strength
- **Mass Dependence**: Heavier particles show less deflection (inertial resistance)
- **Unity Residual**: Amplitude conservation error < 1e-6

### Test Cases
1. **Light particle** ($\omega = 0.5$): Greater deflection, lower inertia
2. **Heavy particle** ($\omega = 1.5$): Lesser deflection, higher inertia
3. **Same well**: Both particles experience identical clock density gradient

## Results

### Gravitational Acceleration
- **Spontaneous Drift**: Zero-momentum packets accelerate toward clock wells
- **Gradient Proportionality**: Drift rate scales with clock density gradient
- **No External Force**: Acceleration emerges purely from phase interference

### Inertial Resistance
- **Mass Dependence**: Heavier particles deflect less per tick
- **Inertia Quantification**: Deflection inversely proportional to particle mass
- **Newtonian Limit**: Recovers $F = ma$ in continuum approximation

### Clock Density Effects
- **Phase Cost Mechanism**: Higher clock density increases $p_\text{stay}$
- **Differential Zitterbewegung**: Creates asymmetric wave packet evolution
- **Geometric Gravity**: Gravity as emergent property of clock distribution

## Significance

This experiment validates the core gravitational mechanism:

1. **Gravity from Clocks**: Gravitational potential encoded in clock density distribution
2. **Phase-Based Acceleration**: No force vectors - acceleration from phase interference
3. **Equivalence Principle**: Inertial and gravitational mass both emerge from $\sin(\omega)/2$
4. **General Relativity Foundation**: Clock density gradients as spacetime curvature

**Core Validation**: Demonstrates that gravity is not an added force but emerges from the lattice's clock structure. This provides the foundation for the equivalence principle and general relativistic effects.

## Files
- **Source**: `src/experiments/exp_02_gravity_clock_density.py`
- **Data**: Trajectory data, deflection measurements, clock density profiles
- **Audit Function**: `run_gravity_clock_density_audit()`

## Related Experiments
- **exp_01**: Establishes inertial persistence that gravity modifies
- **exp_07**: Tests clock density conservation (continuity equation)
- **exp_08**: Compares gravity (divergence) vs electromagnetism (curl)</content>
<parameter name="filePath">c:\dev\dcl\src\experiments\exp_02_gravity_clock_density.md