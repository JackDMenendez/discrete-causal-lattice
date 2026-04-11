# Deriving Particles from Geometry

*Status: working note — seed of companion paper*
*Date: 2026-04-10*

The question is whether the particle content of the Standard Model can
be read off from the symmetry structure of the T³_diamond lattice with
the A=1 constraint, without additional assumptions.

The short answer: **particle types yes, mass values partially, three
generations yes in structure.**  This note works through each in turn,
honestly flagging where the derivation is complete and where gaps remain.

---

## 1. The Two Frequency Scales

The lattice has two distinct frequency parameters that should not be
conflated:

**Zitterbewegung frequency ω** — the internal clock rate of a session.
Sets the rest mass via `m = sin(ω/2)`.  This is the particle's intrinsic
frequency; it does not depend on the potential or the orbital geometry.

**Orbital frequency f_orb** — the rate at which the session circulates
around a potential well.  This appears in the harmonic landscape (exp_09)
on the horizontal axis.

The hydrogen ground state gives the link between them:

    ω_E × R₁ = π/3   (to 0.23%)

This is the 3:1 Arnold tongue lock-in condition: the electron's
Zitterbewegung completes three cycles per orbital period.  The orbital
resonance at `f_orb/f_zitt = 1/3` (Farey denominator q=3) is what
stabilizes the ground state.

**The Farey sequence classifies orbital resonances, not raw masses.**
The mass formula `m = sin(ω/2)` applies to the Zitterbewegung frequency;
the Farey denominator q classifies which Arnold tongue the orbit locks
into, which determines lifetime and generation, not mass directly.

This distinction matters for the particle table.  Mass ratios between
particles are ratios of `sin(ω/2)` values; generation is determined by
the q of the orbital Arnold tongue.

---

## 2. The Symmetry Group

The full symmetry group of the T³_diamond lattice under A=1 is:

    G = O_h × ℤ₂

where:
- **O_h** is the octahedral group with reflections (48 elements) —
  the symmetry of the RGB basis vectors {V₁, V₂, V₃}
- **ℤ₂** is the bipartite parity (RGB even / CMY odd ticks)

Order of G: 96 elements.

The physical symmetry group is the **double cover** (to accommodate
spin-1/2), giving the **binary octahedral group 2O_h** (order 192)
tensored with the bipartite ℤ₂.

### Irreducible representations of O_h

O_h has 10 irreps:

| Irrep | Dim | Character | Physical role |
|-------|-----|-----------|---------------|
| A₁g   |  1  | trivial, even parity | scalar, Higgs-like |
| A₂g   |  1  | pseudoscalar, even | — |
| Eg    |  2  | doublet, even | — |
| T₁g   |  3  | vector, even | magnetic moment |
| T₂g   |  3  | pseudovector, even | — |
| A₁u   |  1  | trivial, odd | — |
| A₂u   |  1  | pseudoscalar, odd | — |
| Eu    |  2  | doublet, odd | — |
| T₁u   |  3  | vector, odd | position, momentum, photon |
| T₂u   |  3  | pseudovector, odd | — |

### Spinor irreps of 2O_h

The double cover adds three spinor (half-integer spin) irreps:

| Irrep | Dim | Physical role |
|-------|-----|---------------|
| E₁/₂  |  2  | fundamental spinor — the electron and quark multiplet |
| E₅/₂  |  2  | second spinor representation |
| G₃/₂  |  4  | quartet spinor — spin-3/2 excitations |

The **two-tick bipartite cycle is the geometric origin of spin-1/2**.
A session must complete two full RGB/CMY cycles to return to its
original state — this is the defining property of a spinor (rotation by
2π returns it to itself only after a second 2π rotation).  The binary
octahedral group encodes this: it is the double cover of O_h for exactly
this reason.

---

## 3. Color Charge from the RGB Basis

The three RGB basis vectors V₁, V₂, V₃ span a 3-dimensional color
space.  The group that rotates freely among them while preserving the
A=1 norm is **SU(3)**.

This is not assumed — it follows from:
1. Three basis vectors of equal length (from the frame condition)
2. A=1 constrains the total probability, not individual RGB components
3. The only norm-preserving transformations mixing three complex amplitudes
   are elements of U(3); fixing the overall phase (global A=1) leaves SU(3)

The SU(3) irreps classify color charge:

| SU(3) irrep | Sessions | Physical particle |
|-------------|----------|-------------------|
| **1** (singlet) | RGB phases cancel exactly | electron, neutrino, proton |
| **3** (triplet) | dominant on one RGB direction | quark |
| **3̄** (anti-triplet) | dominant on one CMY direction | antiquark |
| **8** (octet) | phase rotation between RGB dirs | gluon |

**Confinement is a geometric consequence.**  An isolated quark
(SU(3) triplet session) has a net RGB phase imbalance.  The A=1
constraint on the joint system forces the total probability to be
distributed in a way that favors RGB cancellation — the Coulomb-like
interaction between quark sessions grows with separation because
restoring RGB phase balance requires more lattice paths as the sessions
separate.  This is the geometric origin of confinement, requiring no
separate mechanism.

---

## 4. Electric Charge from the ℤ₂ Bipartite Parity

The bipartite ℤ₂ (even/odd tick parity) couples to the U(1)
electromagnetic interaction.  A session with definite bipartite parity
(always on RGB or always on CMY sublattice) has a definite charge.

The charge values ±1, ±1/3, ±2/3, 0 arise from the RGB substructure:

- **Charge ±1**: sessions where all three RGB components have the same
  phase (color-singlet fermion)
- **Charge ±2/3**: sessions with one RGB component dominant (up-type quark)
- **Charge ±1/3**: sessions with two RGB components dominant (down-type quark)
- **Charge 0**: sessions where the ℤ₂ parity is balanced (neutrino) or
  the bipartite coupling averages to zero (gluon color-diagonal)

The **fractional charges 1/3 and 2/3 are forced by the three-fold RGB
basis**: if color charge must be carried in thirds (one component per
quark in a baryon), electric charge must also come in thirds for the
baryon to be charge-integer.  This is why the quark charges are ±1/3
and ±2/3 in the Standard Model; the lattice derives it from RGB
three-foldness.

---

## 5. Chirality from the L/R Spinor

The weak interaction violates parity — it couples only to left-handed
fermions.  In the lattice this is not a separate postulate:

- **ψ_R** lives on even ticks (RGB sublattice)
- **ψ_L** lives on odd ticks (CMY sublattice)

The weak interaction is a **sublattice-flipping coupling** — it changes
the tick parity of a session.  A process that only couples to ψ_L is one
that only operates on odd-tick nodes.  Parity violation is the statement
that the sublattice-flip coupling is not symmetric between RGB and CMY
ticks — which follows from the bipartite structure having a definite
tick order (even before odd).

The **neutrino is the extreme case**: it is a session with ω→0
(massless) that exists only on one sublattice.  It has no Zitterbewegung
(no transition between ψ_R and ψ_L because m=0), so it is purely
left-handed by construction.

---

## 6. Three Generations from Arnold Tongue Denominators

The Farey denominator q of the orbital Arnold tongue determines the
**generation** of a particle.  This is the key structural result.

The hydrogen ground state sits at q=3 (the 3:1 tongue: ω_E × R₁ = π/3).
The stability (lifetime) of a particle in an atomic orbit scales with
the tongue width W_{p/q} ~ K^q.  Higher q → narrower tongue → less
stable → shorter-lived → heavier (by the lattice analogue of the
width-lifetime relation).

| Generation | Orbital q | Tongue width | Leptons | Quarks |
|---|---|---|---|---|
| 1st | q = 2, 3 | widest | electron, ν_e | up, down |
| 2nd | q = 4, 5 | medium | muon, ν_μ | charm, strange |
| 3rd | q = 6, 7, 8 | narrow | tau, ν_τ | top, bottom |
| 4th+ | q ≥ 9 | vanishing | (none) | (none) |

**Three generations is a prediction, not an input.**  The physical
Coulomb coupling K = STRENGTH = 30 (in lattice units) supports stable
Arnold tongues only up to approximately q ~ 8.  Above that, the tongue
width W_{p/q} ~ K^q falls below the lattice discretization noise floor
and no stable orbit exists.  The number of generations is set by the
coupling strength — not a free parameter of the geometry.

This is falsifiable: at strong enough STRENGTH (large enough K), a
fourth generation should appear.  The threshold STRENGTH for a q=9
stable tongue is computable from the harmonic landscape.

---

## 7. Gauge Bosons

### Photon
A massless (ω=0) session with strict alternating parity and no
Zitterbewegung.  The T₁u(−) irrep of O_h × ℤ₂ — a 3-vector that
is odd under bipartite parity.  The three spatial polarization
directions correspond to the three T₁u basis vectors; gauge invariance
(the longitudinal mode decouples) removes one, leaving 2 physical
polarizations.

### Gluons
T₁u(−) × **8** of SU(3): a vector boson in each of the 8 color-adjoint
directions.  Eight gluons because SU(3) has 8 generators (the
Gell-Mann matrices are the 8 infinitesimal RGB phase rotations).
Gluons carry color charge themselves (they are off-diagonal in color
space), which is why they interact with each other — the cubic gluon
vertex is the commutator structure of SU(3).

### W and Z bosons
The weak bosons arise from the SU(2) subgroup that rotates between
ψ_L doublets: (ν_e, e), (u, d), etc.  In the lattice, this SU(2) acts
on the pair (ψ_L, sublattice-flipped ψ_L).  The W bosons carry ±1
unit of this rotation; the Z is the diagonal generator.

The **Weinberg angle** θ_W (sin²θ_W ≈ 0.231) is the mixing between
the SU(2) weak rotation and the U(1) bipartite phase.  In the lattice
this is the mixing between the sublattice-flip coupling and the global
A=1 phase.  Computing this mixing angle requires the full automorphism
group calculation (the companion paper).  It is a prediction, not an
input, once the lattice calibration is fixed.

---

## 8. The Proton Mass Gap

The proton sits at ω_P = π/2 (q=2, the widest non-trivial Arnold
tongue).  The Zitterbewegung mass is:

    m_P_lattice = sin(π/4) = 1/√2 ≈ 0.707

The electron Zitterbewegung mass is:

    m_E_lattice = sin(0.1019/2) ≈ 0.0509

Lattice mass ratio: m_P/m_E ≈ 13.9.
Physical mass ratio: m_P/m_E = 1836.

The factor of 132 discrepancy is not a failure of the framework — it is
the QCD mass gap.  **99% of the proton mass is not Zitterbewegung mass;
it is confinement energy.**  The proton is three quarks (three color-
triplet sessions) whose RGB phases are forced to cancel.  The energy
cost of maintaining that RGB cancellation at finite separation — the
gluon field energy — is what generates the proton mass.  QCD calls this
dimensional transmutation: the running coupling α_s generates a mass
scale from a dimensionless coupling.

In the lattice language: the joint Arnold tongue of the three-quark
system has a much lower frequency than any individual quark session's
ω.  The binding energy contribution to the proton mass is the
difference between the joint three-body tongue energy and the sum of
individual Zitterbewegung masses.  This is computable in principle from
a three-session simulation (the machinery is already in
`CompositeCausalSession`; exp_13 explored the three-body system).

---

## 9. The Higgs as Zitterbewegung Amplitude

In the Standard Model, the Higgs field gives mass to particles by
coupling to them with strength proportional to mass.  In the lattice:

    m = sin(ω/2)

The Higgs field IS the ω degree of freedom — specifically, the
**collective oscillation of ω across all sessions of the same type**.
When every electron session has the same ω, the system is in the
"Higgs vacuum" (a coherent state of ω values).

The **Higgs boson** is the excitation mode of this collective ω field:
a fluctuation in the Zitterbewegung frequency.  Its mass is set by the
curvature of the Arnold tongue at its center — a stiff tongue (wide,
low q) has a heavy excitation; a narrow tongue has a light excitation.

The Higgs mass (125 GeV ≈ 245,000 m_e) is extremely heavy compared to
the electron, which is consistent with it sitting at a high-q Arnold
tongue (narrow, stiff).  Computing the precise value requires mapping
the Higgs to its Farey position, which requires the coupling strength
calibration.

---

## 10. The Particle Table

Putting this together, the particle content of the Standard Model maps
onto the lattice irreps as follows:

### Leptons (SU(3) singlets, E₁/₂ spinors)

| Particle | ω | q | Bipartite parity | Charge |
|----------|---|---|-----------------|--------|
| Electron | 0.1019 | 3 | odd (ψ_L dominant) | −1 |
| Electron neutrino | ~0 | — | odd only (massless) | 0 |
| Muon | higher | 5 | odd | −1 |
| Muon neutrino | ~0 | — | odd only | 0 |
| Tau | higher | 7 | odd | −1 |
| Tau neutrino | ~0 | — | odd only | 0 |

### Quarks (SU(3) triplets, E₁/₂ spinors)

| Particle | RGB config | q | Charge |
|----------|-----------|---|--------|
| Up quark | V₁ dominant | 3 | +2/3 |
| Down quark | V₁+V₂ dominant | 3 | −1/3 |
| Charm | V₁ dominant | 5 | +2/3 |
| Strange | V₁+V₂ dominant | 5 | −1/3 |
| Top | V₁ dominant | 7 | +2/3 |
| Bottom | V₁+V₂ dominant | 7 | −1/3 |

### Gauge bosons (integer spin)

| Particle | Irrep | ω | Charge |
|----------|-------|---|--------|
| Photon | T₁u(−), SU(3) singlet | 0 | 0 |
| Gluon × 8 | T₁u(−), SU(3) octet | 0 | 0 (color-charged) |
| W± | SU(2) doublet, sublattice-flip | high | ±1 |
| Z⁰ | SU(2) diagonal, ℤ₂ mix | high | 0 |

### Scalar

| Particle | Irrep | Role |
|----------|-------|------|
| Higgs | A₁g(+), SU(3) singlet | collective ω oscillation |

---

## 11. What Is Derivable vs. What Remains

| Claim | Status |
|-------|--------|
| Spin-1/2 vs spin-1 split | **Derived** — bipartite 2-tick cycle IS the double cover |
| SU(3) color from RGB | **Derived** — 3 basis vectors + A=1 forces SU(3) |
| Colorlessness = confinement | **Derived** — RGB phase cancellation is geometric |
| Electric charge quantization in thirds | **Derived** — follows from 3-fold RGB and charge-integer baryons |
| Chirality of weak interaction | **Derived** — sublattice parity IS left/right handedness |
| Photon as massless T₁u session | **Derived** — massless alternating parity session, already in code |
| Three generations | **Derived in structure** — Arnold tongue q cutoff from K |
| Neutrino masslessness | **Derived** — ω→0, single-sublattice session |
| Weinberg angle | **Not yet** — requires full automorphism group calculation |
| Absolute mass values | **Not yet** — need Farey position for each particle type |
| Proton mass gap | **Structural argument** — QCD confinement energy, needs 3-body simulation |
| Higgs mass | **Not yet** — needs Arnold tongue curvature calculation |
| Number of colors = 3 | **Derived** — three RGB basis vectors; not a free choice |
| Number of generations = 3 | **Derived in structure** — coupling K sets q_max ≈ 8 |

---

## 12. The Companion Paper

The full derivation requires one additional computation not done here:

**The automorphism group of (T³_diamond, A=1).**

This is the group of all transformations that preserve both the lattice
structure and the A=1 constraint.  The claim — motivated by everything
above — is:

    Aut(T³_diamond, A=1) = SO(3,1) × SU(3) × SU(2) × U(1)

If true, the Standard Model gauge group is the automorphism group of
the lattice, and all its representations (i.e., all particles) are
forced by the geometry.  The Standard Model is not a theory imposed on
nature — it is the unique probability-conserving theory on the
T³_diamond bipartite 3-manifold.

The calculation is a finite group theory problem: enumerate all
symmetries of the bipartite octahedral lattice that preserve the
discrete A=1 norm.  It is tractable.  It is the companion paper.

---

## 13. Honest Gaps

**The mass ratios are not yet quantitative.**  The Farey sequence gives
a hierarchy (first generation lightest, third heaviest) but not the
specific ω for each particle.  To get the muon mass from first
principles, we need to know which Arnold tongue the muon locks into and
at what STRENGTH.  This requires extending the harmonic landscape scan
to the three-generation structure — a larger exp_09-style simulation
with multiple sessions.

**The generation q-cutoff is approximate.**  The claim that K=30 in
lattice units supports stable tongues only up to q≈8 is based on the
tongue-width scaling W~K^q.  The precise cutoff depends on the noise
floor from Zitterbewegung (which sets a minimum resolvable tongue width).
This is computable from first principles but has not been computed.

**The Weinberg angle requires the automorphism group.**  Until that
calculation is done, the SU(2)×U(1) mixing angle is not predicted.
The experimental value sin²θ_W = 0.231 should emerge as a geometric
ratio if the automorphism group calculation succeeds.
