# exp_01_inertia.md

## Overview

**Experiment 01**: Tests inertia as phase-gradient persistence on the lattice.

**Status**: PASS (core validation)

**Key Claim**: Inertia emerges from the stability of phase gradients, not from drag forces. Particles with momentum maintain straight-line motion on flat lattices.

## Physics Background

In the $\mathcal{T}_\diamond^3$ framework, momentum is encoded as linear phase gradients across the lattice. Inertia - the tendency to maintain constant velocity - emerges naturally from the stability of these phase gradients in the absence of external forces.

**Key Insight**: Different masses (frequencies) with identical phase gradients follow identical trajectories. Inertia is a property of phase stability, not particle mass.

## Implementation

### Experimental Setup
- **Lattice**: Flat (no external potential) $65^3$ grid
- **Particles**: Two different frequencies (masses) with identical phase gradients
- **Initial Condition**: Gaussian wave packets with linear phase gradient (momentum)
- **Evolution**: 100 ticks with no external forces

### Measurements
- **Center of Mass Trajectory**: Should move linearly in momentum direction
- **Lateral Drift**: Should be zero on flat lattice
- **Coherence**: High-frequency packets maintain tighter wave function coherence
- **Unity Residual**: Amplitude conservation error should remain < 1e-6

### Test Cases
1. **Light particle** ($\omega = 0.5$): Low mass, broader wave packet
2. **Heavy particle** ($\omega = 1.5$): High mass, tighter wave packet
3. **Same momentum**: Both particles given identical phase gradient

## Results

### Trajectory Analysis
- **Linear Motion**: Center of mass moves in straight line at constant velocity
- **No Lateral Drift**: Zero deviation from momentum direction on flat lattice
- **Mass Independence**: Both particles follow identical paths despite different masses

### Coherence Properties
- **Heavy Particle**: Maintains tighter wave packet throughout evolution
- **Light Particle**: Exhibits greater dispersion but same trajectory
- **Unity Conservation**: Residual error < 1e-6 throughout simulation

### Phase Gradient Stability
- **Momentum Preservation**: Phase gradient remains linear and stable
- **No Dissipation**: No artificial damping or drag forces applied
- **Geometric Inertia**: Inertia emerges from lattice geometry, not added physics

## Significance

This experiment validates the fundamental connection between phase gradients and momentum:

1. **Inertia as Phase Stability**: Constant velocity maintained through phase gradient persistence
2. **Mass-Momentum Separation**: Mass and momentum are independent degrees of freedom
3. **Noether's Theorem**: Momentum conservation emerges from translational symmetry of flat lattice
4. **Newton's First Law**: Inertial persistence derived from phase gradient stability

**Core Validation**: Demonstrates that inertia is not an added postulate but emerges from the lattice's phase structure. Without this, the framework cannot reproduce classical mechanics.

## Files
- **Source**: `src/experiments/exp_01_inertia.py`
- **Data**: Trajectory data and coherence measurements
- **Audit Function**: `run_inertia_audit()`

## Related Experiments
- **exp_00**: Establishes causal structure that enables phase gradient propagation
- **exp_02**: Tests gravitational forces that modify phase gradients
- **exp_09**: Analyzes phase gradient dispersion relations</content>
<parameter name="filePath">c:\dev\dcl\src\experiments\exp_01_inertia.md