# exp_04_decoherence.md

## Overview

**Experiment 04**: Tests wave function collapse as localized phase scrambling by observer clocks.

**Status**: PASS (core validation)

**Key Claim**: Measurement and decoherence emerge from clock interactions, not from manually applied noise. The observer is a CausalSession that scrambles local phase coherence.

## Physics Background

Quantum measurement causes wave function collapse and decoherence. In the $\mathcal{T}_\diamond^3$ framework, this emerges from:

- **Observer as Clock**: Measurement apparatus is a CausalSession with its own tick counter
- **Phase Scrambling**: When observer and particle share nodes, local phases randomize
- **Coherence Destruction**: Interference patterns collapse without manual noise terms
- **Clock Interaction**: Decoherence emerges from combinatorial tick scheduling

## Implementation

### Experimental Setup
- **Base Case**: Repeats exp_03 two-slit interference experiment
- **Observer**: CausalSession (detector) placed at various positions
- **Interaction**: Observer joins TickScheduler combinatorial space
- **Phase Effect**: Local phase scrambling when particle and observer coincide

### Test Cases
1. **Coherent Baseline**: No observer - fringes present with high contrast
2. **Detector at Source A**: Observer at slit position - fringes collapse
3. **Detector Far Away**: Control case - fringes unaffected

### Measurements
- **Fringe Contrast**: Ratio of bright/dark fringe intensities
- **Coherence Loss**: Transition from interference to particle-like behavior
- **Phase Scrambling**: Localized randomization at observer position
- **Clock Coupling**: Decoherence through tick scheduler interactions

## Results

### Decoherence Effects
- **Baseline**: High fringe contrast (>0.15) in coherent case
- **Collapse**: Near-zero contrast when observer at slit position
- **Locality**: No effect when observer far from interference region

### Clock-Based Mechanism
- **No Manual Noise**: Decoherence from legitimate clock interactions
- **Observer Reality**: Measurement apparatus as physical CausalSession
- **Phase Scrambling**: Local coherence destruction at measurement points

### Quantum Measurement
- **Wave Function Collapse**: Emergent from clock combinatorics
- **Observer Dependence**: Measurement outcomes depend on apparatus state
- **No Projection Postulate**: Collapse from phase interference dynamics

## Significance

This experiment validates the measurement theory foundation:

1. **Observer as Clock**: Measurement apparatus is a physical system
2. **Decoherence Mechanism**: Phase scrambling through clock interactions
3. **No Ad Hoc Collapse**: Wave function reduction emerges naturally
4. **Quantum-Classical Transition**: Clock combinatorics drives decoherence

**Core Validation**: Demonstrates that measurement is not a separate postulate but emerges from the lattice's clock structure and combinatorial scheduling.

## Files
- **Source**: `src/experiments/exp_04_decoherence.py`
- **Data**: Interference patterns with/without observers
- **Audit Function**: `run_decoherence_audit()`

## Related Experiments
- **exp_03**: Establishes baseline interference pattern
- **exp_05**: Observer effects on measurement irreversibility
- **exp_07**: Clock density effects on decoherence rates</content>
<parameter name="filePath">c:\dev\dcl\src\experiments\exp_04_decoherence.md