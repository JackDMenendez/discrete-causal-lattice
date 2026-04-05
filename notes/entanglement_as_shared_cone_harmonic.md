# entanglement_as_shared_cone_harmonic.md
# Entanglement as Shared Light Cone Harmonic

## The Question

Is quantum entanglement a shared harmonic between two causal cones that
previously overlapped?

---

## The Kernel of Truth

When two CausalSessions interact (causal cones overlap), the TickScheduler's
pairwise phase exchange synchronises their internal clocks.  After separation,
their U(1) phases retain that correlation — the shared history is encoded in
their phase relationship.

So there IS a "shared light cone harmonic": two sessions that interacted will
have correlated f_zitt = omega/(2*pi) oscillations long after separation.
The correlation is set at the moment of interaction and persists in their
internal clocks.

---

## The Problem: Bell's Theorem

Simple U(1) phase correlation gives CLASSICAL correlations — it satisfies
Bell inequalities (CHSH ≤ 2).  Hidden variable models with pre-established
phase correlations cannot reproduce quantum entanglement.  Bell's theorem
closes this door for U(1) phase alone.

---

## Where It Gets Interesting: SU(2) Spinor Structure

The (psi_R, psi_L) pair is a full Bloch sphere — SU(2), not just U(1).
Correlations across all three Bloch axes simultaneously are richer than
classical phase correlation.

Tsirelson's bound (CHSH ≤ 2*sqrt(2) ≈ 2.83) is exactly what SU(2) algebra
produces.  If the lattice's bipartite spinor encodes correlations in all three
Bloch axes at once — set during the cone overlap period — the resulting
statistics may be quantum rather than classical.

The three axes:
  Z-axis: rgb_cmy_imbalance (psi_R dominance vs psi_L dominance)
  X-axis: Re(psi_R * conj(psi_L)) -- phase coherence between sublattices
  Y-axis: Im(psi_R * conj(psi_L)) -- quadrature coherence

A measurement that projects onto all three axes simultaneously has more
information than a U(1) phase alone.  This is the algebraic structure that
quantum mechanics requires to violate Bell inequalities.

---

## The A=1 Constraint as Nonlocality Candidate

Currently A=1 is enforced per-session independently.  But for an entangled
pair, the physically correct constraint might be:

  |psi_R_A|^2 + |psi_L_A|^2 + |psi_R_B|^2 + |psi_L_B|^2 = 1

i.e., the TOTAL probability of the entangled pair sums to 1, not each
session independently.  This joint normalisation is a form of nonlocality
that does not appear in the local hop rule — it couples the two sessions
instantaneously regardless of separation.

This may be the actual mechanism for quantum correlations in the framework:
not the hop rule (local), not the pre-established phase (classical), but
the global A=1 constraint applied jointly to the entangled subsystem.

---

## The Test: exp_15

Design:
  1. Initialise two sessions with overlapping causal cones (close together,
     interacting via pairwise_interactions for T_interact ticks).
  2. Separate them -- move their potential centres apart, stop pairwise
     interactions.
  3. Run both for T_measure ticks.
  4. Record rgb_cmy_imbalance(t) for each session -- the Bloch sphere z-axis.
  5. Compute cross-correlations C(theta_A, theta_B) for different measurement
     angles theta (phase map rotations on each session before readout).
  6. Compute CHSH value from the four correlation combinations.

Pass criteria:
  CHSH > 2.0  -->  classical bound violated  (quantum-like correlations)
  CHSH > 2*sqrt(2) ~ 2.83  -->  Tsirelson bound (genuine quantum)
  CHSH = 2.0  -->  classical (pre-established phase only)
  CHSH < 2.0  -->  sub-classical (decoherence during separation)

Two variants:
  A. Per-session A=1 (current implementation) -- expected CHSH ≤ 2.0
  B. Joint A=1 for entangled pair -- may give CHSH > 2.0

The difference between A and B IS the entanglement mechanism hypothesis.
If B exceeds 2.0 and A does not, the joint normalisation is confirmed as
the source of quantum correlations.

---

## Connection to the Harmonic Analysis (exp_harmonic)

The harmonic analysis measures the spectrum of a SINGLE session.  For
entanglement, extend to TWO sessions post-interaction:

  Cross-spectrum: FFT(imbalance_A) * conj(FFT(imbalance_B))

If the two sessions share a common harmonic (phase-locked f_zitt), the
cross-spectrum will show a sharp peak at f_zitt.  The PHASE of that peak
encodes the entanglement angle.

An entangled pair with phase difference (alpha - beta) = pi/2 at f_zitt
corresponds to the maximally entangled Bell state.  Rotating that phase
difference via phase maps is equivalent to rotating the measurement basis
in a Bell experiment.

---

## Connection to Qubit Engineering

If entanglement is a shared cone harmonic:

  - Creating entanglement = locking two sessions to the same f_zitt with
    a controlled phase difference
  - Reading entanglement = measuring the Bloch sphere projection at a
    chosen angle (phase map before readout)
  - Entanglement fidelity = sharpness of the cross-spectrum peak
  - Decoherence = broadening of the cross-spectrum peak over time
    (the two sessions drift from their shared harmonic)

The apply_phase_map() primitive is already the gate operation.  The
question is whether the lattice's natural harmonic locking is coherent
enough to sustain entangled correlations for a useful number of ticks.

---

## Prerequisites

- exp_harmonic_analysis: understand single-session spectrum first
- Two-session interaction via TickScheduler pairwise_interactions
- Phase map rotation primitive (apply_phase_map already exists)
- Bell inequality calculation from cross-correlations

---

## Why This Matters

If the A=1 framework reproduces quantum entanglement (CHSH > 2) from:
  - Local hop rule (causal, no FTL signalling)
  - Global joint normalisation (the nonlocal element)
  - Shared spinor harmonic (the correlation mechanism)

...then entanglement is not mysterious.  It is what happens when two
probability-conserving clocks share a normalisation constraint.  The
"spooky action" is the A=1 constraint applied jointly, not a violation
of locality in the hop dynamics.

This would be a foundational result: Bell nonlocality explained by a
global conservation law rather than by faster-than-light influence.

---

## The Stronger Case: Photon Pair Creation

Pair annihilation (electron + positron → two photons) is a cleaner
entanglement argument than post-interaction separation, because the
constraint is not just correlated — it is *structurally inseparable
from birth*.

Under A=1, the two photon sessions are created simultaneously from a
single joint normalization event. The total amplitude budget is divided
between them at the moment of session creation. The phase structure of
the annihilating electron session determines both photon sessions
simultaneously — not sequentially.

**This is stronger than the usual "common source" argument.** In the
A=1 framework it is structural: you cannot create two sessions from one
joint normalization event and have them be independent. The accounting
forbids it. The sessions were never separately normalized, so their
amplitudes are fundamentally not independent.

Specifically:

- The electron's (psi_R, psi_L) spinor at annihilation is split across two outgoing photon sessions
- The total amplitude of both photon sessions must equal the electron's amplitude at that tick
- A=1 applied to the pair jointly: |psi_A|² + |psi_B|² = 1
- Neither session has an independent A=1 constraint

This is joint normalization from birth — the operational definition of
entanglement in the A=1 language.

**The honest boundary:**
The argument above shows joint session creation forces correlations.
It does not automatically show those correlations are non-classical
(CHSH > 2). That requires:

1. Implementing joint A=1 normalization for the photon pair (variant B in the exp_15 design above)
2. Measuring CHSH from the two photon sessions after separation
3. Showing the result exceeds 2.0

The structural argument is compelling. Whether it crosses the classical
bound is still an open experimental question in the framework.

**Why photons are the cleanest test:**
Unlike the two-session post-interaction case, photon pair creation has
no ambiguity about when the joint constraint begins. It begins at the
tick of session creation and never ends. There is no "interaction
period" to characterise or "separation" to define. The joint A=1
constraint is the session creation event itself.

If any configuration in the framework produces CHSH > 2, it should be
this one.
