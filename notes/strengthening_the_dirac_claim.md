# Strengthening the Central Claim

**Central claim:** Spin-1/2 and the Dirac equation emerge from the geometry of a
bipartite 3D lattice with three axioms (A=1, locality, U(1) phase).

Date: 2026-03-23

---

## The Gap

The tick rule *looks* like the Dirac equation. That is not the same as the Dirac
equation *emerging* from the tick rule. The paper needs a continuum limit derivation
to cross that line.

---

## 1. The Formal Derivation (most critical)

Show that as lattice spacing a -> 0, the bipartite tick rule converges to:

    (i*gamma^mu * d_mu - m) * psi = 0

Specifically:
- Taylor-expand the tick rule around a continuous field
- Identify which representation of the gamma matrices the RGB/CMY bipartite
  geometry produces
- Verify they satisfy the Clifford algebra: {gamma^mu, gamma^nu} = 2*g^mu^nu
- Show mass term m = sin(omega/2) / a in the a -> 0 limit

This is a mathematics problem, not a simulation problem. It is the difference
between "our model behaves like the Dirac equation" and "our model IS the Dirac
equation in the continuum limit." The paper lives or dies on this derivation.

---

## 2. Spontaneous Quantization (can be done computationally)

Currently the hydrogen simulation initializes packets with k = n/r -- the Bohr
condition imposed by hand. To strengthen the result, scan over k values and show
that only the Bohr values produce stable orbits:

    # Scan k from 0.03 to 0.25 in small steps
    # For each k, run 600 ticks
    # Measure stability (std/mean of last 200 ticks)
    # Plot stability vs k -- should show sharp minima at k = n/r_n

If the lattice *selects* k = n/r as the only stable solutions, that is quantization
emerging from dynamics, not initial conditions. This transforms the hydrogen result
from a consistency check into a genuine prediction.

---

## 3. exp_08 -- Electromagnetic Coupling

Without this, the framework has gravity (clock density = div deformation) but no
electromagnetism. The paper claims EM vs gravity = curl vs div of the phase field.
This needs to be demonstrated:

- Implement a charged particle in the vector potential A field
- Show the particle picks up the Aharonov-Bohm phase around a flux tube
- Show the Lorentz force F = q(E + v x B) emerges from the curl coupling
- Show EM and gravity are genuinely distinguishable (different symmetries)

This is the experiment that separates the framework from just being "a lattice Dirac
equation" -- the unification claim requires it.

---

## 4. Spontaneous Emission Rate

The simulation has shown n=2 -> n=1 decay occurring without being programmed. If
this is real:

- Measure the decay lifetime tau in ticks
- Compare to the Fermi golden rule prediction: tau ~ n^3 in natural units
- If the ratio matches, that is a quantitative prediction with no free parameters

This would be the strongest result in the paper -- deriving transition rates from
geometry alone, with no coupling constants put in by hand.

---

## Priority Order

| Task                          | Type          | Impact    | Effort |
|-------------------------------|---------------|-----------|--------|
| Continuum limit -> Dirac eq.  | Theory        | Essential | High   |
| Gamma matrix identification   | Theory        | Essential | Medium |
| Spontaneous quantization scan | Compute       | High      | Low    |
| exp_08 EM coupling            | Compute       | High      | Medium |
| Spontaneous emission rate     | Compute       | Very high | Medium |
| Dispersion relation E^2=p^2+m^2 | Theory/compute | Medium | Low  |

The spontaneous quantization scan is the lowest-hanging fruit -- a loop over k
values that could run overnight and would substantially upgrade the hydrogen result.
The continuum limit derivation is what a referee will demand before accepting the
central claim.

---

## What Changes With Each Result

**Without formal derivation:**
> "A bipartite 3D lattice with three axioms reproduces Dirac-like behavior and
> Bohr-like hydrogen orbits."

**With formal derivation:**
> "The Dirac equation and hydrogen spectrum emerge from lattice geometry."

That is a different paper.
