# Comment on the EM Derivation Attempt — Working Note

**Date:** 2026-04-25
**Source:** External review of `notes/em_derivation_attempt.md`.
**Status:** Independent assessment of what was actually derived, where
the gap really sits, how this meshes with the "probability as
connection" thread from earlier, and what the paper should claim.

---

## 1. What you've actually derived

From the EM derivation note:

> "The existence of a U(1) link variable is not postulated — it is the
> most general gauge structure consistent with the framework."

> "The matter current is forced; not postulated."

You've genuinely got:

### U(1) structure forced by matter

  - Sessions carry a phase → relative phase on links → U(1) link
    variables U_μ(x).
  - Non-U(1) groups are incompatible with the matter sector as
    implemented.

### Gauge covariance of the tick rule

Local phase rotation ψ(x) → exp(i·Λ(x))·ψ(x) plus

    A_μ → A_μ + ∂_μ Λ
    U_μ(x) → exp(i·Λ(x + a·μ̂)) · U_μ(x) · exp(−i·Λ(x))

The tick rule is covariant; observables are gauge invariant. This is
baked into the hop structure, not added later.

### Plaquette as field strength

Wilson loop:

    W_μν(x) = U_μ(x) · U_ν(x + a·μ̂)
              · U_μ*(x + a·ν̂) · U_ν*(x)

Small-a expansion:

    log W_μν  ≈  i·a²·(∂_μ A_ν − ∂_ν A_μ)
              =  i·a²·F_μν(x)

The plaquette IS F_μν in the continuum limit, gauge invariant by
construction.

### Dirac current from varying the matter action

Lattice Dirac operator with Peierls links:

    D_lat ψ(x) = (1/2a) · Σ_μ γ^μ
                  · [ U_μ(x) · ψ(x + a·μ̂)
                    − U_μ*(x − a·μ̂) · ψ(x − a·μ̂) ]

Varying S_matter = Σ_x  a^4 · ψ̄ · D_lat · ψ  with respect to A_μ:

    δS_matter / δA_μ(x)  =  a^4 · ψ̄(x) γ^μ ψ(x) + O(a)

Continuum limit:

    J^μ = ψ̄ γ^μ ψ.

So matter + coupling + gauge kinematics are all forced by the tick
rule and locality. That is already a big unification win.

---

## 2. Where the gap really is (and isn't)

You've isolated the gap cleanly:

> "The Peierls phase appears as an externally specified topological
> background — the framework treats A_μ as given, not as a dynamical
> variable with its own equations of motion."

So:

  - You do **not** yet derive an equation of motion for A_μ.

  - You **do** derive:
      • what objects are allowed (U(1) links),
      • how they transform,
      • how they couple to matter,
      • what the gauge-invariant local building block is (plaquettes).

Then you bring in:

> "To close the gap, postulate a gauge action. The natural choice is
> the Wilson action."

and show:

  - Wilson action → Maxwell in the continuum.
  - With your already-derived matter sector, you get full QED-like
    structure.

So the asymmetry with gravity is honest and sharp:

    Gravity:  field equations from clock density + tick rule.
    EM:       field equations from Wilson action + tick-rule-forced
              coupling.

That is exactly the right way to phrase it in the paper.

---

## 3. How this meshes with the "probability as connection" thread

From earlier, we built the probability-induced connection

    A_μ = ∂_μ ln ρ

with curvature F_μν = 0 (pure gauge), and showed that the quantum
potential is essentially the scalar built from

    ∂_μ A^μ + A_μ A^μ.

Your EM note is doing the complementary thing:

  There, the nontrivial curvature lives in the plaquette
    W_μν ~ exp(i·a²·F_μν).

  Here, the nontrivial scalar lives in the clock density / probability
    sector and sources gravity.

So structurally:

  Scalar sector (clock density / probability):
    induces an effective connection with trivial curvature but
    nontrivial scalar "potential" → gravity.

  Vector sector (U(1) links):
    carries nontrivial curvature F_μν → EM.

That makes your §8 critique of the old "single scalar φ" even
stronger: you now have a clean split between

    "scalar-induced geometry"     (gravity)
    "vector gauge geometry"       (EM)

both sitting on the same substrate.

---

## 4. The obvious next technical move

You already sketched it in §10:

> "Define the lattice path integral as a sum over session histories
> weighted by their tick-rule probabilities, then integrate out the
> matter sessions to induce an effective action for A_μ."

That is the move that could promote

    "Wilson is postulated"   →   "Wilson is induced".

Concretely, the program would be:

### Step 1 — define a history weight

Define P_tick[ψ, A] from the tick rule. This is the nontrivial part:
making the stochastic tick dynamics into something path-integral-like.

### Step 2 — sum over matter histories

    Z[A] = Σ_(ψ histories) P_tick[ψ, A] = exp(−S_eff[A])

### Step 3 — expand S_eff[A]

Expand S_eff[A] in local, gauge-invariant operators built from
plaquettes.

### Step 4 — leading term

Show that the leading term is

    Σ_plaquettes (1 − Re W_μν)

with some effective coupling.

If that works, you get:

  - Gauge action induced from the same tick rule that gave you
    gravity.
  - EM field equations on the same footing as the Newtonian limit.

That is the "same level as gravity" bar you set in §10.

---

## 5. What to actually write in the paper

Something like (in your voice, but structurally):

### Claim 1
Given the bipartite tick rule with Peierls substitution, U(1) link
variables, gauge covariance, the plaquette as F_μν, and the Dirac
current J^μ are all derived.

### Claim 2
If one further assumes the standard Wilson gauge action, the
continuum limit reproduces Maxwell's equations with the usual matter
coupling.

### Non-claim (explicit)
The gauge field's vacuum dynamics is not yet derived from the tick
rule; it is assumed in the standard lattice way.

### Open program
Show that integrating out matter sessions induces an effective
Wilson-type action for A_μ.

---

## Summary

That is honest, sharp, and still quite a strong unification story:

  - same substrate (the bipartite lattice with $\mathcal{A}=1$),
  - same coupling mechanism (Peierls / clock-density gradient),
  - different emergent field equations (Maxwell vs. Newton),
  - clear path to possibly deriving the gauge action (the matter-
    integration program of §4 above).

The path forward is to either:

  (a) Write Section 9 as the scoped honest version (claims 1, 2, the
      non-claim, and the open program flagged). This is publishable
      as is.

  (b) Attempt the matter-integration calculation first. If it works,
      Section 9 becomes a much stronger claim. If it fails or
      surprises, that itself is a result worth reporting.

Recommendation: (a) for the current paper, with (b) flagged as
follow-on work. The honest scoped version is already substantial.

---

*End of note.*
