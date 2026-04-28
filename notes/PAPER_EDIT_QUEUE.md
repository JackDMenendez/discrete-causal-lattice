<!-- markdownlint-disable MD022 MD024 MD032 MD047 MD056 MD060 -->
# Paper Edit Queue — Tracking Document

**Date:** 2026-04-28
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

## STRUCTURAL ENRICHMENTS (significant improvements)

These add new content derived in the recent work. Not corrections — the paper is correct without them, but stronger with them.

| Note | Sections | Edit type | Status | Priority |
|---|---|---|---|---|
| `zitterbewegung_as_recoil.md` | §6 (after Zitterbewegung intro) | Paragraph add (dual-hypothesis + experiment) | **Done** (2026-04-27) | Should |
| `lattice_birefringence_prediction.md` | abstract, conclusion | Reword (mention birefringence + optical axis) | Pending | Should |
| `crystal_rotation_picture.md` | end of Part II (new subsection) | Subsection add ("Crystal-Rotation Interpretation") | Pending | Should |
| `lie_group_framing.md` | §6, §14, conclusion | Paragraph adds (Lie-theoretic restatement) | Pending | Should |
| `virtual_sessions_as_gradient_field.md` | §7.2, §9 | Paragraph adds (virtual-cloud mechanism) | Pending | Should |
| `lorentz_arnold_correspondence.md` | §13, §15 | Paragraph adds (resonance ≡ Arnold-tongue) | Pending | Should |
| `lorentz_arnold_correspondence.md` | §11 (Observer as Clock) | Section rewrite (measurement deflation) | Pending | Should |
| `clock_density_uncertainty_and_entropy.md` | §7.5 (saturation) | Paragraph add (soft-precursor regime) | Pending | Could |

## NEW PREDICTIONS (testable forecasts)

Three new falsifiable predictions emerged. The §12 predictions section needs to absorb them.

| Source | What it predicts | §12 entry |
|---|---|---|
| `lattice_birefringence_prediction.md` | Direction-resolved photon dispersion bound; vacuum birefringence with optical axis $(1,1,-1)$ | New P9 (or refine P7) |
| `zitterbewegung_as_recoil.md` | Direction-dependent rest mass aligned with $(1,1,-1)$ | New P10 |
| `lorentz_arnold_correspondence.md` | Direction-dependent anomalous dispersion near atomic resonances | Sub-prediction of P9 |
| `clock_density_uncertainty_and_entropy.md` | Decoherence enhancement near compact objects scaling with $\rho_\text{clock}/\ell_P^{-3}$ | New P11 |

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

1. **Notation consistency.** Ensure $M$, $M_\text{eff}$, $M_\text{frame}$, $\Tdiamond$ are used consistently across §6, §7, abstract, conclusion. The frame matrix is now eigenvalues $\{4,4,1\}$ everywhere it appears.
2. **Optical axis cross-references.** Every mention of the optical axis $(1,1,-1)$ should resolve to the same thing — ideally a single label (e.g., `eq:optical_axis`) referenced from §6, §7, §12, and conclusion.
3. **Audit table updates.** [audit_table.tex](../paper/sections/audit_table.tex) should reflect: birefringence as a `PROG` prediction (numerical test pending), Zitterbewegung-source dual hypothesis as an `OPEN` row, exp_19c result update from yesterday's sweeps.
4. **Bibliography additions.** Citing the new predictions requires citing relevant existing literature: GRB time-of-flight bounds (Vasileiou 2013, already cited), Planck CMB (Planck 2020, already cited), Mössbauer recoil (would need a 1958+ reference), atomic-clock anisotropy tests (need a recent reference, e.g. Hees et al.).

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

## REMAINING WORK BEFORE v1.0

Listing in dependency order — earlier items unblock later ones:

1. **Correctness fixes** (§6 rewrite, abstract/conclusion update, §7 1/r² rewrite). About one focused day if done together.
2. **Structural enrichments** in §6 / §11 / §13 / §15 (most are paragraph adds, not section rewrites). About a half-day each.
3. **New predictions** in §12 (P9, P10, P11). One sitting, ~2 hours.
4. **Crystal-rotation interpretation subsection** at end of Part II. Half-day, but requires the structural enrichments to be in place first.
5. **Audit table update.** ~30 minutes once the prediction set is finalized.
6. **Final figure rendering** (3D toolkit deliverables). Highly variable depending on tooling depth.
7. **Bibliography update**. ~1 hour, can be done last.

Total estimate: 3–5 focused days for v1.0-ready text, before any external proofread.
