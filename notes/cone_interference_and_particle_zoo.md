# Cone Interference and the Particle Zoo

Source: conversation 2026-03-27. This is the central organizing principle of the framework.

## The Core Claim

Every particle's observable properties are the residual amplitude of its causal cone
after internal interference between its color components.

The Standard Model particle zoo is a classification of stable cone interference
patterns on T³_diamond.

---

## Every Particle Has a Cone

All CausalSessions propagate amplitude via the six basis vectors. The causal cone is
the fundamental structure of propagation — not a special property of photons.

What differs between particles is what happens INSIDE the cone:

| Particle    | p_move         | Cone filling                      |
|-------------|----------------|-----------------------------------|
| Photon      | 1 (ω=0)        | Complete — sharp wavefront        |
| Electron    | cos²(ω/2)      | Partial — amplitude hugs center   |
| Very massive| ≈ 0 (ω≈π)      | Minimal — almost stationary       |

---

## Particle Properties as Cone Interference

| Property         | Lattice origin                                              |
|------------------|-------------------------------------------------------------|
| Mass             | Fraction of cone amplitude that stays at nucleus (p_stay)  |
| Electric charge  | Net winding number of cone phase around color wheel         |
| Color charge     | Net RGB/CMY imbalance of cone amplitude                     |
| Spin             | Number of ticks for cone to return to original phase state  |
| Range of force   | Degree of cone cancellation at large r                      |
| Particle stability | Whether cone has a conserved structure preventing decay   |

---

## The Hierarchy of Cancellation

### Photon
- One chirality per tick (pure RGB or pure CMY)
- No phase cancellation — cone propagates at full speed
- Infinite range

### Electron
- Mixed ψ_R and ψ_L, net charge = 1 winding
- Partial cancellation — cone fills more slowly
- Infinite range (1/r² Coulomb falloff)

### Neutron (udd)
- Three color sessions RGB summing to white: ψ_R + ψ_G + ψ_B = 0
- Strong phase cancellation of color cones
- Finite range (exponential falloff beyond ~1 fm)
- Net EM cone: also cancelled (charge neutral)
- Residual: tiny magnetic moment from quark spin misalignment

### Proton (uud)
- Three color sessions RGB summing to white — same as neutron for color
- Color cone: exponentially confined
- Net EM cone: one unit of charge winding survives
- Result: confined color + infinite range EM

### Higgs boson
- Spin-0 — both ψ_R and ψ_L equal amplitude, no angular momentum
- No net color, no net charge
- Pure radial cone — spherically symmetric
- Decays quickly: no conserved quantum number to stabilize the cone

### Neutrino (left-handed, Standard Model)
- Nearly massless — very small δφ
- Purely left-handed: only ψ_L, no ψ_R
- Occupies CMY sublattice only
- Half-cone: amplitude propagates only via CMY vectors
- Tetrahedral cone — not octahedral
- No electric charge: no EM winding
- Couples only via color-complement flipping (weak interaction)

---

## The Confinement Argument

The three RGB color vectors do NOT sum to zero geometrically:

    V1 + V2 + V3 = (1,1,1) + (1,-1,-1) + (-1,1,-1) = (1, 1, -1) ≠ 0

However, for a color-neutral (white) baryon, the phases of the three color
sessions are correlated so that:

    ψ_R + ψ_G + ψ_B = 0    (destructive interference in color space)

The amplitudes add incoherently inside the confinement radius (where the three
quark cones overlap and reinforce each other). Outside the confinement radius,
the three wavefronts catch up with each other and interfere destructively.

Cone amplitude behavior vs. radius:

    r < r_confinement:   amplitude ~ 1/r²  (Coulomb-like, inside hadron)
    r > r_confinement:   amplitude ~ e^{-r/r_0}  (exponential suppression)

This is a lattice geometric derivation of color confinement — not postulated from
QCD, but arising from three-way phase cancellation of RGB sessions.

---

## The Neutrino Half-Cone

A standard model neutrino (left-handed) uses only CMY vectors:

    CMY vectors: (-1,-1,-1), (-1,1,1), (1,-1,1)

These span a tetrahedron. A right-handed neutrino (if it exists) would use only
RGB vectors — the dual tetrahedron. Together they make the full octahedron.

The Majorana condition (ψ_L = charge conjugate of ψ_R) in the lattice:
the CMY amplitude equals the complex conjugate of the RGB amplitude.
Two tetrahedral cones combining to make a full octahedral cone = a massive particle.

This is the lattice geometric picture of the Majorana mass term.

---

## Important Distinction: RGB as Direction vs. RGB as Color Charge

CURRENT MODEL: RGB refers to spatial direction vectors for even-tick hops.
ψ_R and ψ_L are the two chirality components.

NEW HYPOTHESIS: Quark color charge = which RGB basis vector the quark session
is associated with. Red quark ~ V1, Green ~ V2, Blue ~ V3.

This identification is speculative and goes beyond the current implementation.
It requires:
1. Three-component spinor (or three separate bound sessions per quark)
2. Correlated phases between the three color sessions
3. Explicit calculation of the interference falloff radius

This is the key theoretical development needed to make the confinement claim
rigorous. Until then it stands as a strong hypothesis.

---

## Paper Framing

Current framing: exp_00 establishes the speed limit; everything else follows.

Proposed reframing:

    The causal cone is the primary object.
    Every particle is a specific interference pattern within a cone.
    Mass, charge, spin, and force range are all properties of that interference.
    The Standard Model is a classification of stable cone interference patterns
    on T³_diamond.

This is Wheeler's "It from Bit" made geometric: every physical property of every
particle is an interference property of amplitude propagating on a bipartite
lattice. The particles are the patterns, not the substance.

Suggested new section: "The Cone Interference Classification" — between the
current exp_00 result and the Dirac spinor section. It frames the entire framework
before the technical development begins.
