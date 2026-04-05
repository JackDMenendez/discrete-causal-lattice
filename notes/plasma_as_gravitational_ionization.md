# Plasma as Gravitational Ionization: Clock Density Gradient Disrupts Arnold Tongue

## Core Insight

In a *uniform* clock density region, gravitational time dilation shifts both
the proton and electron sessions together. Their effective instruction frequencies
scale identically, the frequency ratio is preserved, and the joint Arnold tongue
attractor survives. The orbit is unaffected.

In a strong clock density *gradient* — which a gravity well produces — the
proton and electron occupy different orbital heights and therefore different
clock densities. The session deeper in the well processes more causal events
per external tick. Their effective frequencies diverge:

    ω_eff(x) = ω · ρ̄ / ρ_clock(x)

The joint two-session Arnold tongue requires both sessions to lock onto a
shared resonance. If the clock density difference across the orbital radius R₁
detunes one session relative to the other by more than the Arnold tongue width,
the resonance is broken and the electron is ejected.

**This is gravitational ionization — not thermal, not pressure — but
resonance disruption by gradient-induced frequency detuning.**

## Critical Condition

Orbit stability requires:

    |Δρ_clock / ρ_clock| across R₁  <  Δω_tongue

where Δω_tongue is the width of the Arnold tongue basin (the basin of attraction
around the Bohr resonance). When the clock density gradient across the orbital
radius exceeds the Arnold tongue width, the orbit dissolves.

## Three Distinct Ionization Channels

Standard astrophysics recognises two:
1. **Thermal ionization**: kinetic energy exceeds binding energy (Saha equation)
2. **Pressure ionization**: Pauli exclusion in degenerate matter (white dwarf
   interiors, neutron star crusts)

This framework predicts a third:
3. **Resonance ionization**: clock density gradient across R₁ detunes the
   joint proton-electron Arnold tongue, dissolving the orbit without requiring
   high temperature or extreme density

Channel 3 becomes dominant near extreme mass concentrations — neutron star
surfaces, accretion disks — exactly where plasma is the observed state.
This may explain why stellar atmospheres ionize at lower temperatures near
compact objects than thermal models alone predict.

## Connection to the Clock Fluid

In the clock fluid language (Section 8), the condition is:

    |∇ρ_clock| · R₁ / ρ_clock  >  Δω_tongue

This is a condition on the *local pressure gradient* of the clock fluid
relative to the orbital radius. It relates directly to the momentum equation
(Payne-Whitham term): regions where the clock fluid is strongly compressed
are regions where atomic bound states cannot survive.

Plasma is the thermodynamic phase of matter in which the clock fluid gradient
exceeds the Arnold tongue width at all orbital radii. The plasma-neutral
boundary is a phase transition of the clock fluid.

## Arnold Tongue Compression and Quantum Number Dependence

Arnold tongues compress at higher quantum numbers. In the standard circle
map, the width of the tongue at resonance p/q scales as ~1/q². The orbital
series n=1,2,3... occupies progressively narrower basins:

    Δω_tongue(n) ~ 1/n²

Meanwhile the orbital radius grows as R_n ~ n², so the ionization
condition becomes:

    |∇ρ_clock| · R_n / ρ_clock  >  Δω_tongue(n)
    |∇ρ_clock| · n² / ρ_clock   >  1/n²
    |∇ρ_clock| / ρ_clock         >  1/n⁴

Both factors drive the same direction: excited states are doubly
vulnerable to gradient ionization. A gradient that cannot dislodge n=1
can easily push n=2 out of its tongue entirely.

This gives a natural account of the Lyman series ionization sequence in
stellar atmospheres — the observed progression in which higher lines
require progressively lower densities to be in absorption. In the lattice
picture that is not purely a temperature effect; it is Arnold tongue
compression. The ground state sits in the widest available tongue (the
3:1 resonance at ω·R₁=π/3) and is therefore the most robust
configuration in the universe.

## Falsifiable Predictions

1. **Ionization threshold vs. quantum number**: The gradient required to
   ionize orbital n scales as 1/n⁴. This predicts a specific departure
   from the Saha equation at low temperatures near strong gravity gradients:
   higher orbitals ionize first, at much lower gradients than thermal models
   predict.

2. **Ionization threshold vs. gravity gradient**: The ionization temperature
   should be *lower* near strong gravitational gradients than in flat space,
   by an amount computable from the Arnold tongue width and the local
   ρ_clock gradient.

3. **exp_strength_sweep proxy test**: Increasing Coulomb STRENGTH sharpens the
   clock density gradient across R₁. If settling probability decreases with
   increasing STRENGTH (at fixed proton mass), that is evidence for
   gradient-driven detuning as a distinct ionization channel.

4. **Minimum stable orbit radius near compact objects**: There exists an innermost
   stable atomic orbit (analogous to ISCO for test particles) below which the
   clock density gradient always exceeds the Arnold tongue width. Inside this
   radius, no neutral matter can exist — a structural prediction independent of
   temperature.

## Cosmological Connection

In the clock fluid picture, the early universe has high uniform ρ_clock
(large Hubble parameter). Recombination (z ≈ 1100) is when ρ_clock drops
to the point where the Arnold tongue width exceeds typical gradients — when
clock density gradients become shallow enough for resonances to form.
The recombination epoch is the phase transition of the clock fluid from
gradient-dominated (plasma) to resonance-stable (neutral hydrogen).

## Open Questions

- What is the analytic form of Δω_tongue as a function of STRENGTH and OMEGA_E?
  (Can be read off the Arnold tongue landscape from exp_09/exp_11.)
- Does the gradient ionization channel produce a different spectral signature
  than thermal ionization? (Broadening of lines vs. continuum opacity?)
- Does the minimum stable orbit radius near a Schwarzschild black hole
  agree with the photon sphere radius (r = 3GM/c²)?
