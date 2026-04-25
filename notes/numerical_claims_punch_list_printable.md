# Numerical Claims Needing Rigorous Calculation — Punch List

**Date:** 2026-04-25
**Purpose:** Items to address before promoting the paper from
Release Candidate to 1.0. Each entry identifies a specific numerical
claim in the manuscript that is currently an estimate, where it
sits, and what would sharpen it.

---

## High Priority — The Load-Bearing Numbers

### 1. Hydrogen tongue half-width Δω_tongue / ω_e at the 3:1 resonance

**Currently in the paper:**
  Δω_tongue / ω_e ~ 0.05  (read off harmonic-scan figure)

**Where it's used:**
  - §12.6 / P5: critical Stark field
  - §12.7 / P6: clock-density correction to emission rate
  - §12.9 / P8: quantum Roche limit gradient

**Why it matters:**
  This single number flows into three predictions. Sharpening it
  sharpens all three simultaneously.

**What's needed:**
  - A script that extracts the full-width-at-half-maximum of the 3:1
    Arnold tongue from the harmonic-scan power spectrum
  - Source data: data/exp_harmonic_hires_powermap.npy
    (per CLAUDE.md; saved by exp_09c_harmonic_hires.py)
  - Output: Δω_tongue with explicit uncertainty
  - Replace the ~0.05 estimate in §12.6 with the measured value

**Effort:** A few hours of analysis. The data exists; only the
extraction has to be written.

---

### 2. Critical Stark field E_crit^(n=1) in physical units

**Currently in the paper:**
  E_crit^(n=1) ~ 10^9 V/m  (Compton-calibration upper bound)

**Derivation in §12.6:**
  E_crit = c · Δω_tongue / (2 · e · R_1)

**Why it matters:**
  P5 is described in the paper as "the most testable near-term
  prediction." The number is used to claim laser-induced static
  fields can reach the threshold. If the formula has a missing
  factor of 2, π, or 4πε₀, the predicted threshold could be off by
  an order of magnitude.

**What's needed:**
  - Verify the dimensional analysis of E_crit = c · Δω_tongue / (2 · e · R_1)
    — units in SI vs lattice units, factors of ε₀ / 4π / etc.
  - Derive the relation from first principles (the perturbation to
    the orbital phase rate caused by an external E-field in the
    Peierls-substitution form of §9.3)
  - Substitute the sharpened Δω_tongue from item 1
  - Report the corrected E_crit at Compton-calibration upper bound
    and at the GRB-constrained calibration

**Effort:** A few hours once item 1 is in place. Mostly bookkeeping
on the dimensional analysis.

---

## Medium Priority — Order-of-Magnitude Estimates Flagged as Such

### 3. P4 muon-lifetime correction prefactor

**Currently in the paper:**
  Δτ/τ ~ (a/r_⊕)² × prefactor (assumed O(1))

**Where it sits:**
  §12.5 / P4

**Why it matters:**
  Without the prefactor the prediction is qualitative — direction and
  scaling are stated but not magnitude. The paper currently flags
  this explicitly ("prefactor we have not computed; assuming that
  prefactor is O(1)..."), so the language is honest, but a proper
  derivation would lift it from "qualitative" to "quantitative."

**What's needed:**
  - Derive the clock-density correction to the decay rate from the
    scheduler model of §4.5
  - Compute the prefactor in terms of the local clock-density gradient
    and the muon's internal frequency ω_μ
  - Substitute into the Earth-surface vs LEO comparison

**Effort:** Half a day to a day. Conceptually straightforward but
requires care with the discrete-vs-continuous relationship between
"scheduler load per macro-tick" and "decay rate per second."

---

### 4. P6 emission-rate corrections

**Currently in the paper:**
  Clock-density correction:  ΔΓ/Γ ~ 10^-10  (Lyman-α at Earth surface)
  Finite-lattice correction: ΔΓ/Γ ~ 10^-12  (visible light, Compton upper bound)

**Where it sits:**
  §12.7 / P6

**Why it matters:**
  Both inherit uncertainty from item 1 (the Δω_tongue estimate) and
  from item 3 (the prefactor problem in P4 generalised). The
  qualitative form (a clock-density correction with an r-dependence
  different from the gravitational redshift; a finite-lattice
  correction with λ-dependence) is right; the magnitudes are
  estimates.

**What's needed:**
  - Same prefactor calculation as item 3, applied to the emission-
    rate context
  - Cross-check that the clock-density and finite-lattice
    corrections are independent (they should be — the first is a
    detuning effect, the second is a phase-space effect)
  - Sharpen the numerical estimates with the rigour from items 1
    and 3

**Effort:** Once items 1 and 3 are in place, item 4 is mostly
substitution.

---

## Already Correct — No Action Needed

The following numerical claims are well-grounded and do not need
sharpening:

  P7  GRB constraint  a ≲ 10^-19 m
      Source: vasileiou2013 (Fermi-LAT GRB observations).
      Published, peer-reviewed, established.

  P2  t_tick ≈ 8 × 10^-21 s at Compton calibration
      Direct: t_tick = λ_C / c with λ_C the electron Compton wavelength.
      No estimate, no prefactor uncertainty.

  P1  N ~ L/a
      Order-of-magnitude lattice spacing scaling. Trivial.

  P3  Anisotropy amplitude ~ (a/λ)²
      Functional form derived from frame-condition analysis in §6.4.
      The CMB hexapole signature is calibration-independent.

  Hydrogen ground state ω × R_1 = π/3 to 0.23%
      Measured directly in exp_12 at the 4-significant-figure level.
      Reported as a measurement, not a prediction.

---

## Items the End-to-End Read Pass Should Catch

These are not numerical-rigour items but should be addressed in the
RC → 1.0 pass:

### Title page

  Currently:  "Working Paper -- Version 0.9"  (paper/main.tex:12)
  Decision needed:  bump to 1.0, or 0.95-RC, or hold at 0.9 until
                    verification is complete.

### Tone consistency

  The seven sections rewritten in this session (§4 Tick Scheduler,
  §5 Phase Propagation, §9 Vacuum Twist, §10 Interference,
  §12 Predictions, §13 Lattice Harmonics, §14.6 Photon Emission)
  share a recognisable voice with the following conventions:
    - Heavy use of \paragraph{...} subheaders within subsections
    - Explicit "honest scope" framing
    - "What is derived vs. what is postulated" tables
    - "Open program" / "deferred to Paper 2" closing subsections

  Earlier sections (§3 Causal Sessions, §6 Emergent Kinematics,
  §7 Gravity, §11 Observer, §14 Hydrogen Spectrum apart from 14.6)
  may use different conventions worth aligning. A read-through pass
  would identify any jarring style shifts.

### Build pass

  - pdflatex compilation has not been run
  - 158 \ref calls and 57 \cite calls statically resolve, but LaTeX
    can still surface issues at compile time:
      math-mode mismatches, package conflicts,
      \begin{itemize} placement, equation-numbering surprises
  - Until the PDF compiles cleanly, any "release-ready" claim is
    premature

### Tier 3 hygiene

  - Verify every \includegraphics points to an existing image file
  - Bibliography completeness audit: are there any results cited
    in prose that are missing references?
  - Remove the DOI placeholder in main.tex when the actual DOI
    is assigned

---

## Recommended order

  1. Title-page version metadata    (5 minutes — but commit to a number)
  2. Build pass + fix any errors    (~hour, will surface unknowns)
  3. End-to-end read pass            (1-2 evenings)
  4. Item 1 (tongue width)           (half day)
  5. Item 2 (E_crit verification)    (half day, depends on item 1)
  6. Item 3 (P4 prefactor)           (half day to a day)
  7. Item 4 (P6 corrections)         (substitution after items 1, 3)
  8. Tier 3 hygiene                  (an afternoon)
  9. Bump to 1.0

Estimated total: 3–5 days of focused work, depending on how much
of the rigorous calculation in items 1–4 is done now versus deferred
to a follow-on paper.

---

## Decision points

For each item, you have three options:

  (a) Compute it now            — paper becomes more rigorous
                                  before 1.0
  (b) Hedge more strongly       — flag as estimate; defer rigorous
                                  calculation to follow-on
  (c) Leave as is               — current language already flags
                                  most of these as estimates; the
                                  qualitative signatures are the
                                  load-bearing claims

The current paper takes option (b)/(c) for items 1–4, with the
calibration-question paragraph and the tongue-width estimate
flagged appropriately. (a) is required only if you want the
specific numerical predictions to be defensible to a referee asking
"where does this number come from?"

The most natural cut: do item 1 (tongue width) before 1.0, since it
flows into three predictions and is genuinely tractable from
existing data. Defer items 2–4 to a follow-on calculation paper, or
sharpen them only after item 1 is in hand.

---

*End of punch list.*
