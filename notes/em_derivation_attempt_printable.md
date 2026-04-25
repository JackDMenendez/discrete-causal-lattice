# EM Derivation from the Lattice — Working Note

**Date:** 2026-04-25
**Status:** Working pass. Half the derivation closes from the tick rule
alone; the other half requires a postulate (the Wilson gauge action)
that the existing tick rule does not strictly force. Honest scope
assessment at the end.

---

## 0. Goal and what would count as success

Section 7 of the paper derives Newton's law of gravity from the lattice
tick rule end-to-end:

  1. Hop probability p_hop = cos²(δφ/2) with δφ = ω + V.
  2. Weak-field expansion: p_hop ≈ p₀ − m·V.
  3. Equilibrium: ρ_clock ∝ exp(m·V).
  4. Linearise + lattice Laplacian: ∇²φ_Newton = 4πG ρ.

Every step uses the existing tick rule. No new field is introduced.

A parallel for EM would look like:

  1. Hop probability with Peierls: δp → δp + A·v.
  2. Weak-field expansion.
  3. Equilibrium-like condition.
  4. Reduction to Maxwell's equations.

The hope is the parallel works. The finding below: it works on the
matter side but not on the gauge side. The matter coupling is
genuinely derived. The gauge field's own dynamics has to be
postulated (Wilson action). With that postulate Maxwell falls out;
without it, only half the story does.

---

## 1. Setting: U(1) link variables

The lattice tick rule already includes Peierls substitution: when a
session hops from x to x + a·μ̂, its phase acquires a factor

    exp(i · a · A_μ(x))

in addition to the Zitterbewegung phase. This is in
CausalSession._kinetic_hop. CLAUDE.md notes "Peierls substitution: A·v
added to delta_p."

The natural object is the link variable

    U_μ(x) = exp(i · a · A_μ(x))   ∈ U(1)

living on the link from x to x + a·μ̂. Two structural facts:

- **U(1) is forced by the matter content.** Every session has a U(1)
  phase. The relative phase between sessions at adjacent nodes is
  naturally a U(1) element. Any other gauge group is inconsistent
  with the matter sector.

- **Link variables are forced by the hop structure.** The hop is the
  basic operation. The link variable is the most general U(1)-valued
  object that can act on a hop without breaking locality.

So the existence of a U(1) link variable is not postulated — it is
the most general gauge structure consistent with the framework. What
gets postulated, eventually, is that A_μ has its own dynamics.

---

## 2. Gauge covariance of the tick rule (DERIVED)

Local U(1) gauge transformation:

    ψ(x)     → exp(i·Λ(x)) · ψ(x)
    A_μ(x)   → A_μ(x) + ∂_μ Λ(x)
    U_μ(x)   → exp(i·Λ(x + a·μ̂)) · U_μ(x) · exp(−i·Λ(x))

(The U_μ rule follows from the definition U_μ = exp(i·a·A_μ) and
a·∂_μ Λ ≈ Λ(x + a·μ̂) − Λ(x).)

The matter tick rule (schematic):

    ψ(x + a·μ̂) = U_μ(x) · (tick ψ)(x)

Apply the transformation:

    ψ′(x + a·μ̂)
        = U′_μ(x) · (tick ψ′)(x)
        = exp(i·Λ(x+a·μ̂)) · U_μ(x) · exp(−i·Λ(x))
            · exp(i·Λ(x)) · (tick ψ)(x)
        = exp(i·Λ(x+a·μ̂)) · U_μ(x) · (tick ψ)(x)
        = exp(i·Λ(x+a·μ̂)) · ψ(x + a·μ̂)

The new ψ at x + a·μ̂ rotates by the local Λ at that node. The tick
rule is gauge covariant by construction; gauge invariance of physical
observables (|ψ|², phase differences) follows automatically.

**Status: derived from existing tick rule. No postulates.**

---

## 3. The plaquette is F_μν (DERIVED)

The smallest non-trivial closed loop on the lattice — a plaquette in
the (μ,ν) plane:

    x  →  x + a·μ̂  →  x + a·μ̂ + a·ν̂  →  x + a·ν̂  →  x

The U(1) holonomy around this loop is the Wilson loop:

    W_μν(x) = U_μ(x) · U_ν(x + a·μ̂)
              · U_μ*(x + a·ν̂) · U_ν*(x)

Expanding for small a, using A_μ(x + a·ν̂) ≈ A_μ(x) + a·∂_ν A_μ(x):

    log W_μν  ≈  i · a² · (∂_μ A_ν − ∂_ν A_μ)
              =  i · a² · F_μν(x)

So the lattice plaquette IS the field strength tensor times the
plaquette area, in the continuum limit:

    W_μν(x)  →  exp(i · a² · F_μν(x))    as a → 0

W_μν is gauge invariant: corner gauge transformations cancel pairwise
around the loop. So F_μν is gauge invariant in the continuum limit —
without postulating it.

**Status: derived. F_μν emerges as the smallest non-trivial gauge-
invariant lattice operator built from link variables.**

---

## 4. Coupling to bipartite matter and the Dirac current
(MOSTLY DERIVED)

The bipartite tick rule with Peierls couples matter to the gauge
field. To extract the matter current, expand the lattice Dirac action
around a smooth matter configuration.

Lattice Dirac operator with Peierls links:

    D_lat ψ(x) = (1/2a) · Σ_μ γ^μ
                  · [ U_μ(x) · ψ(x + a·μ̂)
                    − U_μ*(x − a·μ̂) · ψ(x − a·μ̂) ]

The γ^μ are the matrices derived in Section 6.4 from the bipartite
RGB/CMY structure. (This is the compact form; the alternating
RGB/CMY tick rule is equivalent in the continuum limit — Kogut and
Susskind 1975.)

Matter action:

    S_matter = Σ_x  a^4 · ψ̄(x) · D_lat · ψ(x)

Vary with respect to A_μ, using δU_μ = i·a·U_μ·δA_μ:

    δS_matter / δA_μ(x) = a^4 · ψ̄(x) γ^μ ψ(x) + O(a)

In the continuum limit:

    J^μ(x) = ψ̄(x) γ^μ ψ(x)        — the Dirac current.

**Status: derived modulo the standard staggered-fermion equivalence
between the alternating bipartite tick rule and the compact Dirac
operator (Kogut–Susskind). Section 6.4 already takes the two as
equivalent. The matter current is forced; not postulated.**

---

## 5. Vacuum dynamics for A_μ — WHERE IT GETS HARDER

We now have:

  - A gauge-covariant tick rule for matter.
  - A gauge-invariant field strength F_μν.
  - A matter current J^μ with the Dirac form.

To get Maxwell's equations ∂_ν F^νμ = J^μ, we need an equation of
motion for A_μ. That requires an action for the gauge field.

**This is the gap.** The existing framework specifies matter dynamics
through the tick rule but does not specify dynamics for A_μ. The
Peierls phase appears as an *externally specified* topological
background — the framework treats A_μ as given, not as a dynamical
variable with its own equations of motion.

To close the gap, postulate a gauge action. The natural choice — and
the one that produces standard QED in the continuum limit — is the
Wilson action:

    S_gauge = (1/g²) · Σ_plaquettes (1 − Re W_μν)

For small lattice fields:

    1 − Re W_μν  ≈  1 − cos(a² F_μν)
                 ≈  (a^4 / 2) · F_μν F^μν

Continuum limit:

    S_gauge  →  (1 / 2g²) · ∫ d^4x  F_μν F^μν

This is the Maxwell action up to sign convention. Varying
S_gauge + S_matter with respect to A_μ:

    ∂_ν F^νμ = J^μ        — inhomogeneous Maxwell.

The homogeneous equation ∂_[ρ F_μν] = 0 is automatic from
F_μν = ∂_μ A_ν − ∂_ν A_μ.

**Status of the Wilson action:** in standard lattice gauge theory it
is justified by locality, gauge invariance, lowest non-trivial order,
and reflection positivity. These uniquely fix it up to coupling. They
are reasonable physical postulates but external to the existing
tick rule.

**Possible escape route (research program, not a derivation):** define
the lattice path integral as a sum over session histories weighted by
their tick-rule probabilities, then integrate out the matter sessions
to induce an effective action for A_μ. The leading term in the
small-a expansion *is* the Wilson form, by the standard argument that
any gauge-invariant local term must be built from plaquettes. Whether
this argument can be made rigorous within the framework is a research
question — see §10 below.

---

## 6. Maxwell, with the gauge action assumed

With the Wilson action assumed, the full system is:

    Matter:      lattice Dirac with Peierls links     (existing)
    Gauge field: Wilson action                        (POSTULATED)
    Coupling:    Peierls substitution                 (existing)

In the continuum limit, varying the action gives:

    ∂_ν F^νμ = J^μ                  (inhomogeneous Maxwell)
    ∂_[ρ F_μν] = 0                  (homogeneous Maxwell, automatic)

Special cases:

  No matter (J^μ = 0):
    □ A^μ − ∂^μ(∂·A) = 0
    Lorenz gauge ∂·A = 0:  □ A^μ = 0   (photon wave equation)
    Lattice photon dispersion (exp_09) confirms this in the long-
    wavelength limit.

  Static matter (∂_t = 0):
    ∇·E = ρ,  ∇×B = J        (Coulomb's law and Biot–Savart)

  Plane-wave A_μ:
    transverse photons, two polarisation states (the two RGB/CMY
    chiralities), spin-1, masslessness, gauge invariance — all
    structural consequences, not postulates.

---

## 7. Why this is asymmetric with the gravity derivation

Section 7 derives Newton from the existing tick rule alone. No new
field is introduced; clock density is already a feature of the
multi-session tick scheduler.

The EM derivation here introduces the link variable A_μ. That
variable is consistent with the existing Peierls phase but is not
currently treated as dynamical. To get its equation of motion, we
must postulate a gauge action. The Wilson action is the natural
postulate, and standard arguments (locality + gauge invariance +
minimality) uniquely fix it — but those arguments are external to the
tick rule.

**The asymmetry is real:**

  Gravity in this framework
    = derived effective theory of clock density
    on the existing tick rule.

  EM in this framework
    = separately postulated gauge theory whose matter coupling
    is forced by the existing tick rule, but whose gauge dynamics
    is added by hand.

The unification claim of the paper survives: both arise from the same
phase-field substrate. That claim is supported because the matter
coupling on both sides comes from the bipartite tick rule —
gravitational mass and electric charge are both expressions of the
same Zitterbewegung structure. But the *field equations* on each side
are derived from different sources: gravity from clock density, EM
from a postulated gauge action.

---

## 8. The vacuum twist field equation in the older notes —
does it survive?

The older notes/vacuum_twist_field_equations.md proposes a unified
scalar equation:

    □φ − sin²(φ/2)·φ = J_grav + J_em

with J_em = ε^μνρσ ∂_ν F_ρσ.

**Two problems with this as written:**

1. ε^μνρσ ∂_ν F_ρσ vanishes identically when F is the curl of A
   (Bianchi identity). The EM source as stated is identically zero
   in standard EM.

2. A *scalar* φ is the wrong object to carry the curl content of the
   gauge field. Curl is intrinsically a vector operation; you cannot
   get F_μν from a single scalar.

**The right framework, per the present derivation:**

  Scalar clock density ρ_clock sourcing gravity through ∇²ρ_clock
    → Newtonian potential.

  Vector gauge field A_μ sourcing EM through F_μν → Maxwell.

These are not two source terms for the same field. They are two
different fields on the lattice, each with its own equation of motion,
both arising from the bipartite tick rule.

The unification claim survives — both fields arise from the same
substrate, both couple to matter through Zitterbewegung — but the
unified scalar equation in the older note does not. The unification
is at the level of substrate and coupling, not at the level of a
single field equation.

The older note should be revised before being cited from the paper.

---

## 9. What the paper section can defensibly claim

CAN claim:

  1. The Peierls-substituted tick rule is U(1)-gauge-covariant.
     (Derived, §2.)
  2. The lattice plaquette is F_μν in the continuum limit.
     (Derived, §3.)
  3. The matter current is the Dirac current ψ̄γ^μψ, with γ^μ from
     the bipartite RGB/CMY structure.  (Derived, §4; relies on §6.4.)
  4. With the Wilson gauge action, the continuum limit reproduces
     Maxwell exactly.  (Standard, §5–6.)

CANNOT claim:

  1. Maxwell's equations are derived from the lattice tick rule alone.
     They are not. They require the Wilson action postulate.
  2. A unified scalar phase field φ governs both gravity and EM. The
     unification is at the level of substrate, not a single field
     equation.

The honest paper section: derivation of the matter side from the
tick rule, the gauge action as the standard postulate of lattice
gauge theory, and the unification claim restricted to substrate +
coupling rather than a single unified equation.

This is still a substantial unification — more than standard QED + GR
offer, because here both forces share the same matter substrate (the
bipartite Zitterbewegung) and the same coupling mechanism (Peierls /
clock-density gradient). But it is not a single-equation
unification.

---

## 10. Open: making the gauge action induced rather than postulated

The promising direction for closing the gap: define the lattice path
integral as a sum over session histories, integrate out matter, check
whether the induced effective action for A_μ is the Wilson form.

Schematically:

    Z = Σ_histories P_tick[ψ, A]  =  ∫ DA · exp(−S_eff[A])

with

    S_eff[A] = − log Σ_(ψ-histories) P_tick[ψ, A]

Expanding S_eff in powers of the lattice spacing and using gauge
invariance + locality should produce the Wilson form at leading
order, with computable coefficients. This calculation has not yet
been done in the framework but is well-defined and tractable.

If it works, the gauge action becomes induced rather than postulated,
and the EM derivation rises to the same level as the gravity
derivation. If it produces an unexpected form, that is itself a
falsifiable prediction.

Natural follow-on calculation for a future paper or for the
predictions section of the current one.

---

## Summary table

| Step                             | Status        | Source           |
|----------------------------------|---------------|------------------|
| U(1) link variable U_μ exists    | DERIVED       | matter U(1) +    |
|                                  |               | locality         |
| Gauge covariance of tick rule    | DERIVED       | §2 above         |
| Plaquette → F_μν                 | DERIVED       | §3 above         |
| Matter current J^μ = ψ̄γ^μψ      | DERIVED       | §4 above + §6.4  |
| Vacuum equation for A_μ          | POSTULATED    | Wilson action    |
| Maxwell ∂_ν F^νμ = J^μ           | DERIVED with  | §5–6 above       |
|                                  | Wilson action |                  |
| Unified single-equation form     | DOES NOT HOLD | §8 above         |
| Substrate + coupling unification | HOLDS         | this whole note  |

---

*End of note.*
