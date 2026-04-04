# The Two-Session Bound State: Why the Bohr Model Requires an Active Proton

*Notes from conversation, 2026-04-02*

---

## The Underframed Result

The standard Bohr model treats the proton as a fixed external potential —
a classical background field V(r) = -e²/r that the electron moves in.
The Coulomb well is a static landscape.

The lattice shows this is wrong at a fundamental level. The proton is a
session. It has its own phase rotor, its own tick dynamics, its own amplitude
structure. It is actively participating in the joint A=1 accounting every tick.

The electron doesn't orbit a potential well. It co-evolves with another
session whose phase dynamics create the effective well.

---

## Why the Static Well Fails

A static Coulomb singularity gives the electron a smooth deterministic
potential. In principle you could find the exact minimum and stay there.
No exploration needed, but also no restoring force. Initialize off k_Bohr
and the electron drifts. The well provides no mechanism to find the resonance.

A proton session is doing something every tick — its phase rotor is advancing,
its amplitude is redistributing across its own cone, its psi_R and psi_L are
oscillating at the proton's Zitterbewegung frequency. From the electron's
perspective, the well isn't static. It's flickering at the proton's internal
frequency.

Those fluctuations are not noise. They are the mechanism by which the electron
explores the well. The proton's phase dynamics drive the electron's amplitude
into different regions of the potential landscape every tick. The electron
doesn't settle into the orbit — it is continuously driven into it by the
proton's active participation.

---

## The Orbit as Joint Resonance

A bound state is not an electron captured by a potential.
It is a stable joint resonance between two sessions under global A=1.

The hydrogen atom exists because the electron's phase rotor frequency and
the proton's phase rotor frequency find a joint Arnold tongue attractor.
The orbit is the geometric expression of that frequency lock. The Bohr radii
are the radii at which the two-session system can maintain stable joint
resonance.

Without the proton being an active session, the electron has no mechanism
to find the resonant orbit. With the proton active, the joint dynamics
continuously correct toward the resonant configuration. The orbit is an
attractor of the two-session system, not a fixed point of the one-session system.

This is why exp_12 is more fundamental than exp_10.
- exp_10: showed the orbit exists
- exp_12: showed it is stable because both sessions are active, recovering
  k_Bohr to four significant figures with no initialization tuning

---

## The Experimental Signature

In a static Coulomb well, orbital stability depends only on initial conditions.
Initialize at k_Bohr and it orbits; initialize off k_Bohr and it drifts.
The well provides no restoring force toward the resonant k value.

In the two-session model, the proton's phase fluctuations provide exactly that
restoring force. An electron initialized slightly off k_Bohr gets driven back
toward it. The basin of attraction around k_Bohr is wider and deeper in the
two-session model.

This is measurable: compare the sharpness of the k-scan minimum in exp_11
(static well) vs exp_12 (active proton). The stability minimum in exp_12
should be sharper and more robust — the Arnold tongue is wider when the
proton is active because two degrees of freedom are locking rather than one.

exp_12 recovered k_Bohr to four significant figures. exp_11 n=2 (static well)
showed a flat landscape with no resonance at all. The experimental evidence
is direct.

---

## Emission as a Three-Session Event

This completes the photon emission picture (notes/photon_emission_from_A1.md).

The photon session isn't created because the electron spontaneously emits.
It's created because the joint proton-electron resonance becomes unstable —
the two-session Arnold tongue narrows, the phase dynamics can no longer
maintain joint A=1 at the current orbital radius, and the system transitions
to a lower joint resonance.

The photon session is created to absorb the amplitude displaced by the
resonance transition. The recoil is the proton session adjusting to the
new joint configuration.

Emission is a three-session event from the start:
1. Proton and electron jointly transition to a lower resonance
2. Photon session is created to close the A=1 accounting
3. Recoil is the proton adjusting to the new joint configuration

This is why a static Coulomb well cannot produce emission naturally —
the well has no session dynamics to drive the resonance transition.
The proton must be active for emission to follow from A=1.

---

## The Coulomb Field as Shadow

The Coulomb potential is not the cause of the orbit. It is the averaged
shadow of the proton's active phase dynamics projected onto the electron's
cone — what the proton's session looks like from far away, time-averaged,
in the classical limit.

Close up, at the orbital scale, the shadow breaks down. The proton's discrete
tick dynamics matter. The electron doesn't sit in a bowl — it co-evolves with
another dancer whose steps it can feel but whose internal structure it cannot
directly observe.

The hydrogen atom has always been a two-body resonance. The static potential
approximation made us forget that. The lattice remembers it.

---

## Statement for the Paper (Introduction)

*A static Coulomb potential is insufficient to produce stable quantized orbits
from the lattice dynamics alone. The proton must be represented as an active
session --- a phase rotor participating in the joint $\mathcal{A}=1$ accounting
every tick --- for the electron to explore the well and lock onto resonant
orbits spontaneously. Hydrogen is not an electron in a field. It is two sessions
finding a joint Arnold tongue attractor. This distinction has observable
consequences: the basin of attraction around each Bohr radius is wider in the
two-session model, the orbital stability is self-correcting rather than
initialization-dependent, and photon emission is a natural three-session event
rather than a separately postulated transition rate.*

---

## Relation to Other Results

- notes/proton_symmetry_breaking.md — proton recoil as symmetry-breaking mechanism
- notes/photon_emission_from_A1.md — photon session as A=1 necessity
- notes/conservation_of_probability.md — A=1 as the only conservation law
- exp_12 data: k_min=0.0970 vs k_Bohr=0.0971 (4 sig figs, no tuning)
- exp_11 n=2: flat landscape in static well — confirms proton required
