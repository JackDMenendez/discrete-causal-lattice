<!-- markdownlint-disable MD022 MD024 MD032 MD047 MD056 MD060 -->
# Paper Edit Queue — Tracking Document

**Date:** 2026-04-28 (last updated 2026-04-28 PM after `03bd385`)
**Purpose:** Track every research seed and finding from the 2026-04-26 → 2026-04-27 → 2026-04-28 work that has implications for the paper, so nothing gets lost in the editorial pass.
**Status:** Working document. Update as edits land.

## Convention

Each entry lists:
- **Note** — the research seed file in `notes/`
- **Paper sections affected** — where the edit lands
- **Edit type** — `Reword`, `Paragraph add`, `Subsection add`, `Subsection rewrite`, `Section rewrite`, or `Figure add`
- **Status** — `Done`, `Pending`, `Drafted`, `Started`, `Blocked`
- **Priority** — `Must` (correctness fix), `Should` (significant improvement), `Could` (optional enrichment)

## CORRECTNESS FIXES — LANDED IN v0.96-RC (2026-04-28)

| Note | Sections | Edit type | Status | Landed in |
|---|---|---|---|---|
| `frame_condition_isotropy_memo.md` (RESOLVED) | abstract, conclusion, §6 | Reword (drop `M = 3δ_ij` claim) | **Done** | v0.96-RC |
| `frame_condition_isotropy_memo.md` (RESOLVED) | §6 (rotational invariance argument) | Subsection rewrite | **Done** | v0.96-RC |
| `frame_condition_isotropy_memo.md` (RESOLVED) | §7 (1/r² recovery, tilted Laplacian) | Reword (qualify as $O_h$-averaged) | **Done** | v0.96-RC |
| `lattice_birefringence_prediction.md` | §12 P7 (photon dispersion) | Paragraph add (direction-resolved refinement) | **Done** | v0.96-RC |
| `zitterbewegung_as_recoil.md` | §6 (after Zitterbewegung intro) | Paragraph add (dual-hypothesis + experiment) | **Done** | v0.96-RC |
| Title page + front matter | `main.tex` | "What changed in v0.96-RC" callout | **Done** | v0.96-RC |
| Version metadata | `main.tex`, `CITATION.cff`, `CHANGELOG.md`, `release_notes/` | Bump to v0.96-RC | **Done** | v0.96-RC |

## INDUCED GAUGE ACTION — LANDED IN `03bd385` (2026-04-28 PM)

| Source | Sections | Edit type | Status | Landed in |
|---|---|---|---|---|
| `em_derivation_solution.md` | new Appendix B | Appendix add (structural form of $-\mathrm{Tr}\ln D_\text{lat}$) | **Done** | `03bd385` |
| Appendix B / `induced_gauge_action.py` | §9.6 honesty table | Reword (Wilson postulate → structural form derived) | **Done** | `03bd385` |
| Appendix B | §9.7 open program | Subsection rewrite (point to App B; narrow remaining work to numerical prefactor) | **Done** | `03bd385` |

**Side-effect:** Appendix B exposes a *gauge-sector* birefringence with the same optical axis $(1,1,-1)$ as P7. This is implicit in the appendix but not yet promoted to a named §12 prediction. Candidate for absorption into P9 below or a new sub-prediction.

## STRUCTURAL ENRICHMENTS (significant improvements)

These add new content derived in the recent work. Not corrections — the paper is correct without them, but stronger with them.

| Note | Sections | Edit type | Status | Priority |
|---|---|---|---|---|
| `zitterbewegung_as_recoil.md` | §6 (after Zitterbewegung intro) | Paragraph add (dual-hypothesis + experiment) | **Done** (2026-04-27) | Should |
| `lattice_birefringence_prediction.md` | abstract, conclusion | Reword (mention birefringence + optical axis) | **Done** (2026-04-28, v0.96-RC) | Should |
| `crystal_rotation_picture.md` | end of Part II (new subsection) | Subsection add ("Crystal-Rotation Interpretation") | Pending | Should |
| `lie_group_framing.md` | §6, §14, conclusion | Paragraph adds (Lie-theoretic restatement) | **Partial** — automorphism question in conclusion; full restatement not landed | Should |
| `virtual_sessions_as_gradient_field.md` | §7.2, §9 | Paragraph adds (virtual-cloud mechanism) | Pending | Should |
| `lorentz_arnold_correspondence.md` | §13, §15 | Paragraph adds (resonance ≡ Arnold-tongue) | Pending | Should |
| `lorentz_arnold_correspondence.md` | §11 (Observer as Clock) | Section rewrite (measurement deflation) | Pending | Should |
| `clock_density_uncertainty_and_entropy.md` | §7.5 (saturation) | Paragraph add (soft-precursor regime) | Pending | Could |

## NEW PREDICTIONS (testable forecasts)

| Source | What it predicts | §12 entry | Status |
|---|---|---|---|
| `lattice_birefringence_prediction.md` | Direction-resolved photon dispersion bound; vacuum birefringence with optical axis $(1,1,-1)$ | Refined P7 (kinematic-sector birefringence) | **Done** (v0.96-RC, P7 direction-resolved refinement paragraph) |
| Appendix B (`induced_gauge_action.tex`) | Gauge-sector birefringence: anisotropic photon kinetic term with same $(1,1,-1)$ axis | Sub-prediction of P9 or refinement of P7 | Pending (not yet promoted to §12) |
| `zitterbewegung_as_recoil.md` | Direction-dependent rest mass aligned with $(1,1,-1)$ | New P10 | Pending |
| `lorentz_arnold_correspondence.md` | Direction-dependent anomalous dispersion near atomic resonances | Sub-prediction of P9 | Pending |
| `clock_density_uncertainty_and_entropy.md` | Decoherence enhancement near compact objects scaling with $\rho_\text{clock}/\ell_P^{-3}$ | New P11 | Pending |

## FIGURES TO ADD

| Source | Figure | Status |
|---|---|---|
| (already done) | `frame_matrix_ellipsoid.{png,pdf}` (sphere vs. tilted ellipsoid) | **Done** (2026-04-27) |
| `crystal_rotation_picture.md` + `3d_visualization_toolkit.md` | 3D rotating-crystal animation showing screw motion + birefringence + screen pattern | Pending |
| `3d_visualization_toolkit.md` | Brillouin zone with Dirac cones (3D, not 2D projection) | Pending |
| `3d_visualization_toolkit.md` | Two-tick propagator eigenvalue surface $|\lambda_\pm(\mathbf{k})|$ over Brillouin zone | Pending |
| `lattice_birefringence_prediction.md` | Direction-resolved dispersion polar plot ($E$ vs. direction) | Pending |

## RESEARCH SEEDS (philosophical / interpretive — leave in notes for now)

These are valuable but speculative. They sharpen the framework's interpretation but aren't ready for paper inclusion.

| Note | Why it stays in notes (for now) |
|---|---|
| Determinism implications (deistic / interventionist / self-projector readings) | Philosophical positions; framework permits all three. Discussing in paper invites pushback without strengthening the core claims. |
| Within-universe technological participation | Speculative engineering; useful for talks but not for v0.95-RC. |
| Substrate-currency cost (planet-moving energy bookkeeping) | Sharp observation that the framework permits richer cost-accounting than standard physics. Promote to paper only after a concrete derivation. |
| Holographic depth identification ($(1,1,-1)$ as RG flow direction) | Strong interpretive claim. Could justify a paper subsection but requires a more careful derivation than we have. |

## PAPER-LEVEL CHECKS NEEDED

Before submission, verify:

1. **Notation consistency.** Ensure $M$, $M_\text{eff}$, $M_\text{frame}$, $\Tdiamond$ are used consistently across §6, §7, abstract, conclusion, and Appendix B. The frame matrix is now eigenvalues $\{4,4,1\}$ everywhere it appears. Status: Pending.
2. **Optical axis cross-references.** Every mention of the optical axis $(1,1,-1)$ should resolve to the same thing — ideally a single label (e.g., `eq:optical_axis`) referenced from §6, §7, §12, conclusion, and Appendix B. Status: Pending.
3. **Audit table updates.** [audit_table.tex](../paper/sections/audit_table.tex) should reflect: birefringence (kinematic + gauge-sector) as `STUB` rows, Zitterbewegung-source dual hypothesis as `STUB`, induced gauge action as `PART` (structural form derived in App B; numerical prefactor open), exp_16 status reword, exp_19c result update from sweep logs. Status: Pending. (See conversation 2026-04-28 for the agreed must-fix scope.)
4. **Bibliography additions.** Citing the new predictions requires citing relevant existing literature: GRB time-of-flight bounds (Vasileiou 2013, already cited), Planck CMB (Planck 2020, already cited), Mössbauer recoil (would need a 1958+ reference), atomic-clock anisotropy tests (need a recent reference, e.g. Hees et al.). Status: Pending.
5. **Residual obsolete claims in §6 structural-consequences enumeration.** [emergent_kinematics.tex:363-366, 374-377](../paper/sections/emergent_kinematics.tex#L363) still contains "$\sum_\text{RGB} \mathbf{v}\mathbf{v}^T = 3I$" and "isotropic by the frame condition, without symmetry averaging" — both are pre-v0.96-RC language that contradicts the corrected isotropy paragraph at lines 263-321. Status: Pending. Priority: **Must** (correctness — internal contradiction).

## DAILY UPDATE LOG

### 2026-04-26
- LaTeX hygiene pass: 78 → 1 warning, notation cleanup, orphan files resolved
- Anticipated Objections subsection drafted in conclusion
- Code & Data Appendix A drafted
- Abstract/intro tightened to remove `peak radius 10.28` overclaim

### 2026-04-27
- Frame condition false claim verified by SymPy; resolution memo written
- Birefringence prediction derived from eigenvalue calculation
- Frame ellipsoid figure rendered (`figures/frame_matrix_ellipsoid.{png,pdf}`)
- Crystal-rotation picture note + Lie-group framing note + virtual-sessions note + 3D toolkit note + clock-density saturation note + Zitterbewegung-as-recoil note
- §6 emergent_kinematics.tex: dual-hypothesis Zitterbewegung paragraph **landed**

### 2026-04-28
- Lorentz–Arnold correspondence note
- This tracking document created
- v0.96-RC release commit pushed (frame-condition correction + birefringence prediction)
- Release-notes file `release_notes/v0.96-RC-release-message.md` added
- Sweep logs `data/exp_19{,c}_*.log` (17 files) tracked under fixed `.gitignore` ordering
- **Appendix B "The Induced Gauge Action" added** (`03bd385`):
  symbolic SymPy derivation of the leading induced action's tensor coefficient
  ($\mathbf{Q}$ with eigenvalues $\{4, 4, 16\}$, optical axis $(1,1,-1)$ in
  F-space dualising to spatial $(1,1,-1) = V_1+V_2+V_3$); §9.6/§9.7 rewritten
  to point to App B and narrow the open work to the numerical prefactor
  $c = 1/g^2$. PDF rebuilt to 123 pages.

## REMAINING WORK BEFORE v1.0

Listing in dependency order — earlier items unblock later ones:

1. ~~**Correctness fixes** (§6 rewrite, abstract/conclusion update, §7 1/r² rewrite).~~ **Done in v0.96-RC.** Residual: §6 structural-consequences enumeration at lines 363–377 still has obsolete "$\sum_\text{RGB} v v^T = 3I$" and "isotropic without symmetry averaging" language — short fix, **Must** priority.
2. **Audit table update.** Discussed and scoped 2026-04-28; not yet applied. ~30 minutes; would land: birefringence (kinematic + gauge-sector) rows, Zitterbewegung-source row, exp_16 reword to PART, induced-gauge-action row referencing App B.
3. **Structural enrichments** in §6 / §11 / §13 / §15 (most are paragraph adds, not section rewrites). About a half-day each.
4. **New predictions** in §12 (P10 rest-mass anisotropy; P11 compact-object decoherence; promote App B's gauge-sector birefringence as P9 sub-prediction or refine P7 again). One sitting, ~2 hours.
5. **Crystal-rotation interpretation subsection** at end of Part II. Half-day, but requires the structural enrichments to be in place first.
6. **Final figure rendering** (3D toolkit deliverables). Highly variable depending on tooling depth.
7. **Bibliography update**. ~1 hour, can be done last.
8. **Notation + optical-axis label sweep** (PAPER-LEVEL CHECKS 1, 2). ~30 minutes once §12 settles.
9. **Consider shortening the paper by moving content to appendices.** Paper is at 131 pages as of `c642848` (2026-04-29) and growing. Candidate moves to evaluate:
   - **§14.6 "Music, Hofstadter, and the Temperament Problem"** (~50 lines) — interpretive flavour subsection; could become Appendix C without weakening the argument.
   - **§7 step-by-step Newton derivation** (Step 1: Force from phase mismatch through Step 3: 1/r² force from Poisson) — could move computational details to an appendix and keep a 1-paragraph sketch in main text. Risk: §7 is the gravity end-to-end derivation; cutting it weakens the main thrust.
   - **§15 Two-Body Hydrogen Four Significant Figures** detailed numerics — could move the detailed numerical comparison to App C; keep the headline result in main text.
   - **§13.7 "Music, Hofstadter, and the Temperament Problem"** — already flagged; flavour content that could pair with §14.6 in a single "Mathematical context" appendix.
   - **App A "Code and Data"** is already an appendix; that's fine.
   - **App B "Induced Gauge Action"** is already an appendix.
   - Detailed exp_09c tongue-width measurement procedure (currently in §13.5 P5 derivation) — could become App D leaving the bottom-line measurement in main.
   The right time to do this is after the structural enrichments land but before final proofreading. The structural enrichments themselves add to length; the appendix-shortening pass should come *after* them so we can see what content is actually load-bearing in the main narrative.

Updated estimate: 2–3 focused days for v1.0-ready text (correctness fixes plus the high-leverage audit-table and §12 predictions edits unlock the rest), plus an additional half-day for the appendix-shortening pass before final proofread.
