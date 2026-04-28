<!-- markdownlint-disable MD022 MD024 MD032 MD047 MD060 -->
# Note: Clock Density, Uncertainty, and Entropy (Moore's Law Analogue)

**Date:** 2026-04-27
**Status:** Research seed. Not derived. Connects to existing §7.5 (scheduler saturation) and §7.6 (Bekenstein-Hawking).

## The seed

Moore's Law has been slowing for years not because transistors stopped getting smaller in principle, but because at high density they become *unreliable before they become impossible*. Tunneling, thermal noise, leakage, manufacturing variability all rise sharply as gate pitch approaches atomic scales. The hard density limit is preceded by a soft regime of probabilistic degradation.

If the lattice's session density is the physical analogue of transistor density, the same precursor regime should exist for $\mathcal{A}=1$. The paper already names a hard limit: scheduler saturation at $\rho_\text{clock} \to \ell_P^{-3}$, identified with the event horizon. What it does not yet say is that **the soft precursor regime should produce statistical uncertainty in $\mathcal{A}=1$ conservation** — not exact conservation any more, but conservation in expectation with variance scaling with $\rho_\text{clock}/\ell_P^{-3}$.

## Why this is more than analogy

In silicon, the "soft regime" arises because finite physical resources (gate area, supply voltage margin, thermal budget) are oversubscribed. Information that would be deterministic in a sparse circuit becomes probabilistic in a dense one.

In the lattice, finite physical resources are: the number of distinguishable nodes per unit volume ($\ell_P^{-3}$), and the amplitude budget at each node (each node carries a single complex spinor amplitude). When session density approaches the node-count limit, two sessions occupying overlapping volume must compete for the same amplitude bookkeeping channels. The bipartite tick rule's strict per-tick conservation $|\psi_R|^2 + |\psi_L|^2 = 1$ is well-defined for one session at a node; for $N$ sessions overlapping $V$ nodes, conservation is well-defined only if $V \gg N$.

Once $V \sim N$, the framework has to choose between:

1. **Exact conservation, lossy assignment** — discard whichever session can't be accommodated. Loses information.
2. **Statistical conservation, partial overlap** — allow approximate joint normalization. $\mathcal{A}=1$ holds in expectation but with variance.

Option 2 is the natural continuum-limit choice. It gives the soft precursor regime.

## Falsifiable predictions

If this is right, the deviation from exact $\mathcal{A}=1$ is a function of local clock density:

$$
\langle \Delta \mathcal{A}^2 \rangle \;\sim\; \frac{\rho_\text{clock}}{\ell_P^{-3}}
$$

This is observationally accessible:

- **Neutron star atmospheres.** Spectroscopic line widths near a neutron star surface should show *additional* broadening beyond gravitational redshift and thermal broadening. The mechanism is decoherence from clock-density-induced uncertainty in the atomic session's $\mathcal{A}=1$. The signal scales with surface density, distinguishing it from velocity broadening.

- **Approaching event horizons.** Decoherence rates of in-falling matter should rise as $r \to r_s$, with a power law set by the clock density profile. This is structurally different from Hawking radiation (which is at the horizon) — it is a *bulk* effect within a few Schwarzschild radii.

- **Big Bang cosmology.** Very early universe (clock density approaching the saturation bound) should show probabilistic deviations from exact conservation laws. Connection to inflation? unclear.

## Why this matters for entropy

The current §7.5 derivation of Bekenstein-Hawking entropy from boundary session counting at saturation is honest but implicit about the *mechanism* by which entropy increases at the boundary. The Moore's-law picture gives the mechanism explicitly:

> Entropy is the statistical residue of clock-density-induced uncertainty in $\mathcal{A}=1$ conservation.

In a sparse region, $\mathcal{A}=1$ is exact, and there is no irreversibility; the universe is unitary in expectation. In a dense region, $\mathcal{A}=1$ becomes statistical, and information is lost in the variance — irreversibility, entropy increase, time's arrow.

This is more primitive than thermodynamic entropy. Thermal entropy is one of the consequences of clock-density-induced uncertainty, not the source of it. Black hole entropy is the limiting case where the entire surface saturates — every cell is at $\rho_\text{clock} = \ell_P^{-3}$, every cell contributes maximal uncertainty.

## Open questions

1. **Order of magnitude.** Is the predicted variance large enough to be measurable? Need a back-of-envelope: at typical neutron-star densities ($\sim 10^{17}$ kg/m³), what is $\rho_\text{clock} / \ell_P^{-3}$? If the answer is $10^{-50}$, the prediction is unfalsifiable.

2. **Connection to Hawking radiation.** Hawking radiation already provides a thermal bath at the horizon; is the Moore's-law-style variance an *additional* contribution, or does it reproduce Hawking's spectrum from a different microscopic argument?

3. **Crossover scale.** Is there a critical density at which the framework switches from exact to statistical, or is the variance smooth in $\rho_\text{clock}$? Smooth is more attractive but harder to characterize.

4. **Connection to existing P2 (minimum time-dilation quantum).** P2 in `predictions.tex` already predicts a discrete time-dilation increment from session quantization. The Moore's-law uncertainty prediction is its statistical cousin — discreteness gives quantization, density gives variance.

## Where this connects to the paper

- §7.5 (Black Holes as Scheduler Saturation): currently states the hard limit. Could be extended with a soft-limit subsection.
- §7.6 (Connection to General Relativity): the "discrete corrections to Newton" prediction (P1 in `predictions.tex`) is the limit-of-low-density version of this. The high-density version (this note) is qualitatively different.
- Predictions section: candidate for a new prediction P9 (or merged with P2/P4) — "Clock-density-induced decoherence near compact objects".

## Action items if pursued

1. Compute $\rho_\text{clock}$ for typical astrophysical densities, check whether the predicted variance is observable.
2. Try to derive the variance scaling from the discrete tick rule directly (the Moore's-law argument is heuristic; a derivation would close the loop).
3. Decide whether this fits as an extension of §7.5 or as a separate "stress-test of $\mathcal{A}=1$" subsection.
