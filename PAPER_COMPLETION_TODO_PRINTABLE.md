# Paper Completion Todo List
## Geometry First: Quantum Mechanics, Gravity, and the Origin of the Standard Model from a Single Conservation Law

**Date:** April 25, 2026 (revised after exp_19c completion + external review)
**Version:** Working Paper 0.9
**Status:** ~92% complete — major derivations done, exp_19c provides numerical proof of A=1-forced photon emission

---

## Revision Notes (2026-04-25)

This revision incorporates three external comments (`notes/comment_on_exp_19c.md`,
`notes/comment_on the_two_dimensional_arnold_tounges.md`, `notes/Comment_on_todo_list.md`)
and the completion of exp_19c. The major changes from the prior version:

1. **Photon emission as A=1 necessity** is no longer a low-priority audit-table stub.
   exp_19c provides the numerical proof; the derivation must move into Section 18.7
   as a Tier 1 writing task.
2. **A new falsifiable prediction** has been added: Arnold tongue *width* implies a
   calculable external-field threshold to depolarize a resonance, giving specific
   deviations from QED's Stark effect and Lamb shift.
3. **Tick Scheduler** and **Vacuum Twist Field Equations** have been promoted to
   Tier 1 alongside Predictions. They are load-bearing for the gravity, observer,
   and unification arguments and the paper cannot be released with them as stubs.
4. **Tone:** the paper has earned the right to state these mechanisms as derived
   results, not proposals. Writing tasks should use confident, declarative voice
   consistent with the new evidence.

---

## Tier 1: Publication Blockers

These are the remaining substantive obstacles to releasing the paper. Each must be
written before the paper is reviewable.

### 1. Predictions Section
**File:** `paper/sections/predictions.tex`
**Status:** STUB
**Why Tier 1:** The paper claims falsifiability throughout. This section is where
that claim is cashed out with explicit formulas, numerical scales, and proposed
experiments.

**Required for each prediction:**
- explicit formula
- explicit numerical scale (with calibration assumptions stated)
- proposed experimental signature
- what observation would falsify it

**Predictions to include:**

#### P1. Discrete 1/r² Corrections (path-count deviations from Gaussian)
- **Claim:** Exact path count P(N, dx, dy, dz) deviates from the Gaussian limit at small N.
- **Crossover scale:**
  - Planck calibration: ~10 Planck lengths (unmeasurable)
  - Compton calibration: ~10 Compton wavelengths (~10⁻¹¹ m)
- **Tests:** precision hydrogen spectroscopy, Casimir effect.
- **Outstanding:** needs `count_paths()` implementation to populate numbers.

#### P2. Minimum Time-Dilation Quantum
- **Claim:** Each additional registered clock costs one `tick_duration` of scheduler overhead.
- **Formula:** δt_min = tick_duration_s.
- **Scales:**
  - Planck: 5.4×10⁻⁴⁴ s (unmeasurable)
  - Compton: ~8×10⁻²¹ s (potentially within reach of optical-clock comparisons)
- **Tests:** atomic-clock comparisons across mm separations (~10⁻¹⁸ fractional sensitivity now).
- **Outstanding:** finalize calibration table.

#### P3. Octahedral Anisotropy
- **Claim:** Six preferred axes (RGB ∪ CMY) break perfect isotropy below the crossover.
- **Tests:** directional correlations in CMB; atomic-clock comparison along inequivalent axes.
- **Status:** speculative; needs theoretical sharpening.

#### P4. Decay-Rate Clock-Density Correction
- **Claim:** Particle decay rate depends on local clock density beyond SR's γ factor.
- **Tests:** precision lifetime measurements at different gravitational potentials.
- **Outstanding:** requires the tick-scheduler decay model from Section 6.

#### P5. Arnold Tongue Width → Stark/Lamb Corrections (NEW — from comment 2)
- **Claim:** Each phase-locking tongue has a calculable *width* in (ω, V) space.
  Quantization is preserved everywhere inside the tongue, not just on its central line.
- **Implication:** an external field of magnitude proportional to the tongue half-width
  is required to pop the electron out of resonance. This gives a specific, calculable
  deviation from the QED Stark effect and Lamb shift — measurable in precision atomic
  spectroscopy.
- **Outstanding:** extract tongue widths from exp_09 / exp_11 / exp_12 data and
  convert to field-strength thresholds. This is the most testable near-term prediction
  in the paper.

#### P6. Emission-Rate Corrections Near Mass Concentrations (from comment 1)
- **Claim:** Spontaneous emission is the three-session forced-recoil event proven
  numerically in exp_19c. Its rate inherits a clock-density correction near massive
  bodies and a finite-lattice-spacing correction at high frequency.
- **Outstanding:** quantify the two correction terms; compare against QED in flat space.

**Cross-references:** P5 and P6 should both cite Section 18.7 (the expanded photon-emission
derivation, see Tier 1 item 5 below).

---

### 2. Tick Scheduler Section — DONE (2026-04-25)
**File:** `paper/sections/tick_scheduler.tex`
**Status:** DONE — section rewritten from STUB to eight subsections covering the
full architectural apparatus.

**What landed:**
- 4.1 The Macro-Tick — three-step cycle (order, tick, couple) with the
  per-session A=1 invariant explicit.
- 4.2 The Combinatorial Clock Space — $|\Omega_n| = n!$, four shuffle schemes,
  exp_05 numerical verification of ordering-invariant probability conservation.
- 4.3 Pairwise Coupling and the Binding Dial — the $c_{ij} \in [0,1]$ parameter
  spans free particles (0) through observer/decoherence (~0.1) through atomic
  binding (~0.5) through composite phase-lock (1).
- 4.4 Three-Session Coupling and Emission — explicit emission triplet
  registration; tangential phase drain; forward ref to Section 14.6.
- 4.5 Clock Density and Time Dilation — pairwise step is not constant-cost;
  high-density regions impose more bookkeeping per macro-tick; gravitational
  time dilation as architectural consequence.
- 4.6 Queue Saturation and the Event Horizon — $\rho_{\max} = \ell_P^{-3}$ as
  computational deadlock; Hawking radiation as stochastic boundary queue-drop.
- 4.7 Architectural Irreversibility and the Arrow of Time — no
  `remove_session` method, $S = k_B \log(n!)$, second law as structural fact
  not statistical approximation.
- 4.8 Falsifiable Consequences — minimum time-dilation quantum
  $\delta t_{\min} = t_{\text{tick}}$ feeding into P2; queue-drop signature
  in Hawking spectra and Planck-density GW dispersion cutoff.

**Side fix:** added `\label{sec:phase}` to phase_propagation.tex (referenced
from the new section).

**Deferred (intentionally):** full Hawking-temperature derivation from
queue-drop rate is left to future work; the structural argument is in place
but the explicit $T_H = \hbar c/(8\pi G M k_B)$ recovery is a follow-on.

---

### 3. Vacuum Twist Field Equations Section
**File:** `paper/sections/vacuum_twist_field_equations.tex`
**Status:** STUB after subsection 7.4
**Why Tier 1:** This is the unification section. It currently stops just before the
payoff — without the explicit field equation and its reductions, the paper's
gravity/EM unification claim is hand-waved.

**Required content:**
- Explicit unified field equation
- Reduction to Maxwell (curl sector → EM)
- Reduction to linearized Einstein (div sector → gravity)
- Interpretation of curl vs div as the geometric origin of the two long-range forces
- Cross-reference to exp_08 (which numerically demonstrates the curl/div distinction)

---

### 4. Build System Fix
**Issue:** `makefile.mak` missing; build scripts failing.
**Required:** Repair `paper/makefile` and `build.cmd` / `build.sh` to match the current
directory structure. Goal: `main.pdf` compiles cleanly from a fresh checkout.
**Why Tier 1:** Cannot release a paper that doesn't compile.

---

### 5. Photon Emission as A=1 Necessity — DONE (2026-04-25)
**File:** `paper/sections/hydrogen_spectrum.tex`, `subsec:emission`
**Status:** DONE — section expanded from ~24 lines to a six-paragraph derivation;
audit table redirected from `\ref{sec:gravity}` STUB to `\ref{subsec:emission}` PASS
with `exp_19c` cited as the numerical demonstration.

**What landed:**
- "Why a single session cannot emit" — cross-references the exp_11 n=2 collapse to
  motivate the multi-session necessity.
- "The three-session necessity" — A=1 forbids re-absorption; only a third session
  can carry the inter-tongue phase gradient; recoil keeps the post-transition orbit
  inside the lower tongue.
- "Numerical demonstration (exp_19c)" — phase-rotation drain + recoil mechanism;
  per-session amplitudes hold to 1.0000 across tested rates; orbits sit at tongue
  boundaries.
- "Three threads unified" — Zitterbewegung (mass + symmetry breaking), Arnold-tongue
  lock-in (quantization), A=1 (forced session creation) as facets of one geometry.
- "Contrast with QED" — no separately quantized field, no vacuum fluctuations.
- "Falsifiable consequences" — clock-density correction to emission rates near
  mass; tongue-width correction to Stark/Lamb. Both feed Predictions P5/P6.

**Side fixes also landed:** added `\label{sec:predictions}` to predictions.tex
(the new section's references depend on it).

---

## Tier 2: Required for Internal Consistency

These are not publication blockers in the same sense as Tier 1, but the paper will
have visible gaps without them.

### 6. Phase Propagation Section
**File:** `paper/sections/phase_propagation.tex`
**Status:** STUB after subsection 5.2
**Why Tier 2:** Ties the U(1) rotor to the lattice hop rule. Without it the Dirac
derivation appears to come out of nowhere.

### 7. Lattice Harmonics Section
**File:** `paper/sections/lattice_harmonics.tex`
**Status:** STUB
**Why Tier 2:** exp_09 is one of the strongest numerical results. The section must
connect:
- spectral peaks
- Arnold tongue boundaries
- Farey hierarchy
- fractal-dimension prediction
- **tongue *width*** (per comment 2 — feeds P5)

This section is also where the mass spectrum argument begins.

### 8. Interference Section
**File:** `paper/sections/interference.tex`
**Status:** PARTIAL (figure exists, prose is stub)
**Required:** Huygens-lantern interference theory tied to exp_03.

---

## Tier 3: Presentation and Infrastructure

### 9. Figure Verification
- Confirm every `.tex` in `figures/` references an existing image
- Spot-check: harmonic landscape, double-slit / lantern figure, Dirac cones double-pane
- Generate any figure referenced from a STUB section once that section is written

### 10. Bibliography Completion
**File:** `paper/paper-bib/references.bib`
- Verify every `\cite{}` resolves
- Add references introduced by Tier 1 sections (e.g., Susskind 1977 for staggered
  fermions; lattice-QCD reviews for the rotational-invariance argument)

### 11. Update Paper Version and Status
- Bump from "Working Paper 0.9" once Tier 1 lands
- Remove DOI placeholder before publication

---

## Tier 4: Optional but Strengthening

### 12. Bekenstein–Hawking Entropy Derivation
`paper/sections/audit_table.tex` line 108. Reasonable to defer to a follow-on paper.

### 13. Scheduler Saturation at Planck Density
`paper/sections/audit_table.tex` line 125. Connects to Tick Scheduler section but
not strictly required for the main argument.

### 14. Additional Figures
Phase rotor diagram, vacuum twist diagrams. Strengthen presentation; not blockers.

---

## Final Validation

### 15. Cross-Reference Validation
- All `\ref{}` resolve
- All `exp_XX` mentions match the actual experiment names and PASS/FAIL status
- All figure references point to existing files

### 16. Content Consistency
- Audit-table claims match experimental results
- CLAUDE.md status matches paper claims
- New Tier 1 content is consistent with `notes/conservation_of_probability.md`,
  `notes/two_session_bound_state.md`, `notes/photon_emission_from_A1.md`

### 17. Final Read-Through
- Grammar, clarity
- Mathematical notation consistency
- Figure captions and table formatting
- Tone: declarative for derived results, hedged only where genuinely uncertain

---

## Priority Summary

| Tier | Items | Reason |
|------|-------|--------|
| **Tier 1 (blockers)** | 1 Predictions, 2 Tick Scheduler, 3 Vacuum Twist, 4 Build, 5 Section 18.7 | Cannot release without these |
| **Tier 2 (consistency)** | 6 Phase Propagation, 7 Lattice Harmonics, 8 Interference | Visible gaps |
| **Tier 3 (presentation)** | 9 Figures, 10 Bibliography, 11 Versioning | Reviewer hygiene |
| **Tier 4 (optional)** | 12 BH entropy, 13 Scheduler saturation, 14 Figures | Strengthen but not required |
| **Final** | 15 Cross-refs, 16 Consistency, 17 Proofread | Last pass |

**Bottom line:** the paper is one Predictions section, one Tick Scheduler section,
one Vacuum Twist completion, and the expanded Section 18.7 away from being a
reviewable manuscript. The build fix is mechanical.

---

## Key Notes Files for Reference

**Essential for Tier 1 writing:**
- `notes/falsifiable_predictions.md` — base material for Predictions section
- `notes/comment_on_exp_19c.md` — text for Section 18.7 expansion
- `notes/comment_on the_two_dimensional_arnold_tounges.md` — basis for new prediction P5
- `notes/photon_emission_from_A1.md` — A=1 forcing of session creation
- `notes/two_session_bound_state.md` — why the static well is incomplete
- `notes/vacuum_twist_field_equations.md` — for Vacuum Twist section
- `notes/lattice_harmonics.md` — for Lattice Harmonics section

**Background:**
- `notes/the_theme_of_the_paper.md` — core reframing of QM axioms
- `notes/conservation_of_probability.md` — A=1 as the sole conservation law
- `notes/deriving_dirac_from_hamiltonian.md` — 6-step continuum limit
- `notes/deriving_dirac_the_significance.md` — why the derivation matters
- `notes/shortcomings_of_quantum_mathematics.md` — what the lattice fixes
- `notes/follow_on_implications.md` — future-paper material

---

## Tone Guidance for Tier 1 Writing

The paper now has the evidence to support confident, declarative framing for the
core mechanisms. Suggested voice:

- **Derived, not proposed:** "The photon session is forced by A=1 conservation"
  (not "we conjecture that...").
- **Topological / dynamical language:** "Arnold tongues are topological attractors
  in the joint phase space" (per comment 2).
- **Hedge only where genuinely uncertain:** speculative predictions (P3 octahedral
  anisotropy) should still be marked as such.
- **Cite the experiments inline:** every dynamical claim in Tier 1 sections should
  point to the exp_XX that demonstrates it.
