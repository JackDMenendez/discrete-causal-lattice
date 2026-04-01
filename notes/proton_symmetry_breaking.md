# Proton Motion as Symmetry-Breaking Mechanism

*Notes from conversation, 2026-03-31*

---

## The Observation

In the fixed-well case the Coulomb potential is perfectly spherically symmetric.
Every orbit at radius R1 is equally valid and the electron has no way to
distinguish one from another. The system is overdetermined with symmetry and
the electron collapses to the center -- there is no preferred orbital plane,
no gradient to follow into the resonance basin.

The live proton breaks that symmetry dynamically. The proton recoils slightly
with each tick, its CoM drifting by fractions of a node. The Coulomb potential
is never perfectly centered -- it has a small, constantly changing asymmetry
that acts as a gentle stochastic perturbation on the electron:

- Breaks the perfect degeneracy of orbital orientations
- Provides a fluctuating radial force that kicks the electron into a preferred
  orbital plane
- Effectively samples the space of possible orbits until the system finds the
  resonance attractor

The perturbation is not random in the arbitrary sense -- the proton moves
according to the same A=1 tick rule. But it introduces a deterministic-but-complex
perturbation that functions like noise from the electron's perspective.

---

## Connection to Arnold Tongues

The stable orbit is not a single trajectory -- it is an attractor basin.
The proton's motion provides the perturbation that allows the electron to
*explore* the neighborhood of the attractor and fall into it. Without that
perturbation the electron is trapped in a perfectly symmetric potential
with no gradient to follow into the basin.

In standard quantum mechanics this is handled by saying the electron is in a
superposition of all orbital orientations simultaneously. The lattice does
something different and more interesting: the proton's dynamics *physically*
explores the orientation space through its own motion. The orbital orientation
emerges from two-body dynamics rather than being postulated as a superposition.

---

## Why the Fixed Well Fails

exp_12 showed that a fixed Coulomb well shifts N=1 by 7.3%. The explanation
was framed as a mass-ratio correction. But the deeper reason is this:

The fixed well is not just missing the mass correction -- it is missing the
symmetry-breaking mechanism entirely. The 7.3% shift is a symptom. The
collapse to the well center (observed in exp_strength_sweep) is the disease.
A live proton is not an optional refinement; it is the physical mechanism
by which a two-body system finds its ground state.

---

## Paper Note

*The live proton session plays an essential role beyond mass-ratio correction:
its recoil motion breaks the perfect spherical symmetry of the Coulomb
potential, providing a dynamic perturbation that allows the electron to explore
the neighborhood of the resonance attractor and fall into it. A fixed well,
being perfectly symmetric, offers no such mechanism -- the electron has no
gradient to follow into the orbital basin and collapses to the center. The
proton's motion is not noise in the pejorative sense; it is the symmetry-breaking
mechanism by which a two-body system finds its ground state.*

---

## Broader Implication

This may be a general principle: in the A=1 lattice framework, ground state
selection requires symmetry breaking by a second body. A perfectly isolated
particle in a perfectly symmetric potential has no mechanism to select a
ground state -- it is equally everywhere. The ground state is not a property
of the electron alone but of the electron-proton system.

This reframes the hydrogen ground state: it is not the lowest energy state
of a single particle in a central potential. It is the stable attractor of
a two-body resonance system where the proton's dynamics provides the
exploration mechanism that finds the basin.

Possible experiment: vary the proton mass (OMEGA_P) and measure how quickly
the electron finds the orbital attractor. Heavier proton = less recoil =
slower symmetry breaking = longer time to ground state. This is a falsifiable
prediction with no free parameters.
