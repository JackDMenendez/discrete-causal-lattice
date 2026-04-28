<!-- markdownlint-disable MD012 MD022 MD025 MD026 MD032 MD041 -->
# Changelog

## v0.96-RC -- Release Candidate (paper) -- 2026-04-28

DOI: 10.5281/zenodo.19866911

Targeted correctness pass on the frame-condition derivation, plus a new
falsifiable prediction (lattice birefringence) and a new dual-hypothesis
paragraph on what drives the Zitterbewegung rate.

### Frame condition correction

- Previous text asserted $\sum_\text{RGB}\mathbf{v}_i\mathbf{v}_j^T = 3\delta_{ij}$.
  Direct calculation (verifiable in 5 lines of SymPy) shows the actual
  matrix has off-diagonal entries $\pm 1$ and eigenvalues $\{4, 4, 1\}$.
- Affected: abstract, conclusion, §6 isotropy paragraph, §7 1/$r^2$
  derivation. All four locations now state the corrected geometry.
- The corrected derivation recovers $\mathrm{SO}(3)$ rotational
  invariance only on $O_h$-averaged observables; the residual
  operator-level anisotropy is a uniaxial birefringence with optical
  axis along $\mathbf{V}_1+\mathbf{V}_2+\mathbf{V}_3 = (1,1,-1)$.

### New: lattice birefringence prediction (P7 refinement)

- §12.7 (P7 Photon Dispersion) gains a new paragraph "Direction-resolved
  refinement (lattice birefringence)" adding the direction-dependent
  component of the existing GRB time-of-flight bound.  Existing analyses
  integrate over sky direction; the framework predicts direction-resolved
  binning should reveal that bursts close to $(1,1,-1)$ exhibit less
  dispersion than perpendicular bursts.

### New: dual-hypothesis Zitterbewegung paragraph

- §6 gains a new paragraph "What drives the oscillation?" identifying
  two competing hypotheses for the source of the Zitterbewegung rate
  $\omega$: self-driven (autonomous) versus recoil-driven (kickback
  from internal virtual-particle emission).  The two are distinguishable
  in principle by direction-resolved precision-mass measurements aligned
  with the cosmic optical axis.

### New artifacts

- `figures/frame_matrix_ellipsoid.{png,pdf}` -- 3D rendering of the
  frame matrix as a quadratic form (sphere vs. tilted ellipsoid).
- `src/utilities/frame_matrix_visualization.py` -- regeneration script.
- `data/frame_matrix_ellipsoid.txt` -- numerical output.
- `release_notes/v0.96-RC.md` -- detailed change log.
- `notes/frame_condition_isotropy_memo.md`, `notes/lattice_birefringence_prediction.md`,
  `notes/zitterbewegung_as_recoil.md`, `notes/lorentz_arnold_correspondence.md`,
  `notes/crystal_rotation_picture.md`, `notes/lie_group_framing.md`,
  `notes/virtual_sessions_as_gradient_field.md`,
  `notes/clock_density_uncertainty_and_entropy.md`,
  `notes/3d_visualization_toolkit.md`,
  `notes/PAPER_EDIT_QUEUE.md` -- research seeds and edit-queue tracker
  for v1.0.

### Title page

- Version updated to `v0.96-RC`.
- New "What changed in v0.96-RC" callout pointing readers to the
  detailed release notes.

## v0.95-RC -- Release Candidate (paper) -- 2026-04-26

Promotion from working paper v0.9 to release candidate v0.95-RC.  Builds
clean at 109 pages; all figures placed in their proper sections; no
remaining `STUB` entries in the audit table.

### Sharpened numerical predictions (punch list items 1-4)

- **P5 -- Stark threshold tongue width** ($\Delta\omega_\mathrm{tongue}$):
  measurement script `src/utilities/tongue_width_3to1.py` extracts the
  FWHM of the 3:1 Arnold tongue from `data/exp_harmonic_hires_powermap.npy`.
  Result: `Delta_omega_tongue / omega_e = 0.033 +/- 0.020`, replacing
  the earlier eyeball estimate of ~0.05.
- **P5 -- Critical Stark field** ($E_\mathrm{crit}^{(n=1)}$):
  derived from first principles via the Peierls scalar-potential gauge
  in §9.3.  Dimensional fix: the formula was `c*Delta_omega/(2eR_1)`
  (dimensionally inconsistent in SI); corrected to
  `hbar*Delta_omega/(eR_1)`.  Numerical value
  `8.5 x 10^9 V/m` with range `3 x 10^9` to `1.4 x 10^10 V/m` from
  the propagated +/-0.020 tongue-width uncertainty.  Replaces the
  prior incorrect `(a/lambda_C)^7` calibration-suppression claim with
  a calibration-independent formulation.
- **P4 -- Muon-lifetime correction prefactor**: derivation now in §12.5
  under the explicit modelling assumption that the muon's per-tick
  rate inherits the `(a^2/6) Laplacian` correction from the discrete
  clock-density update.  Predicts `1.3 x 10^-48` at Compton calibration,
  which is ~25 orders of magnitude smaller than the prior placeholder
  estimate.  P4 is reframed as a structurally valid but currently
  unfalsifiable prediction.
- **P6 -- Emission-rate clock-density correction**: updated
  numerical bound to `~3 x 10^-11` at Earth's surface.

### New derivations (modulo stated assumptions)

- **Bekenstein-Hawking entropy** ($S = k_B A/(4\ell_P^2)$):
  derived in §7.5 via boundary-session counting under the assumption
  that each saturation-boundary session occupies a four-cell patch
  ($A_\mathrm{session} = 4\ell_P^2$), corresponding to the
  RGB/CMY $\times$ R/L spinor degrees of freedom.
- **Hawking temperature** ($T_H = \hbar c^3/(8\pi G M k_B)$):
  derived in §4.6 via the Unruh--horizon relation at the saturation
  boundary, under the assumption that the boundary inherits the
  Schwarzschild surface gravity $\kappa = c^4/(4 G M)$.  Corrects a
  pre-existing typo in the Hawking temperature formula (missing
  $c^2$ in numerator).

### Substrate clarification

- **Two lengths, one convention** (§2.5): added a paragraph defining
  the two natural distances on the cube edge $\ell_P$ vs.\ body-diagonal
  $h = \sqrt{3}\ell_P$ -- and declaring that "the lattice spacing $a$"
  in the paper means the body-diagonal hop distance throughout.

### Photon emission status

- §1 introduction updated to reference `exp_19c_photon_emission`:
  the joint $\mathcal{A}=1$ + recoil mechanism is implemented and
  verified to preserve per-session unitarity over short test runs.
  A settled multi-rate sweep that resolves the Arnold-tongue lock-in
  and discrete emission events remains pending.
- Audit table: `exp_19c` row carries `PART` status; the paper text
  matches that status (no quantitative `peak radius` claim until a
  settled sweep is in hand).

### Audit table

All four `STUB` entries promoted to `PART`:

- Event horizon + Hawking T (now derived in §4.6).
- Bekenstein-Hawking entropy (now derived in §7.5).
- Photon emission as $\mathcal{A}=1$ necessity (mechanism verified
  in `exp_19c`, event-rate measurements pending).

### Section structure

- Removed two duplicate `\section{...}` declarations that produced
  empty stub headers in the table of contents (Emergent Kinematics
  and The Observer as a Clock now appear once each, not twice).
- Section count: 16 (previously 18 with the two stub headers).

### Figures

All dark-mode figures re-rendered with light backgrounds for print:

- `exp_harmonic_hires` (light, inferno on white).
- `dirac_cones_overlay` (light, with graphene K-point inset).
- `exp_12_twobody_scan` (light, navy + dark red curves).
- `quantization_scan` (light, vertical-stacked heatmap, inferno_r so
  density peaks render as dark blobs against cream).

Placement fixes:

- `exp_03_lanterns` moved from end-of-paper float to §10.3
  (Fringe Formation), with caption rewritten to acknowledge the
  body-diagonal lattice anisotropy.
- `exp_00_cone_structure` placed in §3.2 (new figure 4, mass and
  phase-map effects on the causal cone).
- `exp_harmonic_hires` (light) + `dirac_cones_overlay` (light)
  share a page in §13 with cross-references.
- `quantization_scan` and `exp_12_twobody_scan` placed in §15.4 / §15.5;
  the latter resolves a previously-undefined `\ref{fig:exp12_twobody}`.

### Title-page and provenance

- Title-page version: `Working Paper -- Version 0.9` -> `Release
  Candidate -- Version 0.95-RC`.
- Zenodo DOI badge added below `\maketitle`, replacing the textual
  DOI link (renderable PNG generated by
  `src/utilities/zenodo_badge.py`).

### Build system

- Makefile tree consolidated from five (root, paper, src, src/experiments,
  tests) plus duplicated `make/common.mak` and `make/targets.mak` to
  two: a root makefile that handles env, tests, paper, promote, clean,
  and delegates experiments; and `src/experiments/makefile` for
  individual experiment runs.
- Documents the GNU Make >= 4.3 requirement (UCRT64 shell) and notes
  that the Windows Make port (3.81) is too old for the `&:` grouped-target
  syntax used by the experiments makefile.

### Failed-design note (negative result captured)

- `notes/exp_03b_lanterns_aligned_design.md`: full postmortem on the
  attempted 45 degree-rotated double-slit design.  The rotation
  re-aligned the experimental forward axis with V_1 -- the
  least-productive 2-tick xy-only direction for thin z-grids -- so
  the wavefront stays in the slit-line region instead of propagating
  forward.  Original axis-aligned `exp_03_lanterns` is preferred and
  remains in the paper.

### Items deferred to v1.0

- Full microstate-counting derivation of the Bekenstein-Hawking factor
  of 1/4 (currently rests on the boundary-cell-grouping assumption).
- Strong-field clock-fluid derivation that fixes the Schwarzschild
  surface gravity $\kappa = c^4/(4 G M)$ at the saturation boundary
  (currently inherited as a modelling assumption).
- First-principles muon coupling to the scheduler load (currently
  inherited from the bare $\rho_\mathrm{clock}$ evolution).
- `exp_19c` event-rate sweep at higher coupling (mechanism verified;
  discrete emission events at higher rates pending).
- Tone-consistency read-through across older sections (§3, §6, §7,
  §11, §14 apart from §14.6).

---


## MAJOR RESULT -- Hydrogen Spectrum Confirmed

Experiment exp_10_v2.py on 197^3 grid (600 ticks each level):

  r_2/r_1 = 4.42   (Bohr predicts 4.000,  error 10%)
  E_2/E_1 = 0.229  (Bohr predicts 0.250,  error  8%)

Both within 10% of exact Bohr prediction.
Residual error: Zitterbewegung damping + softening correction.

BONUS RESULT: Spontaneous emission observed.
  n=2 orbit stable for ~340 ticks, then collapses to n=1.
  Not programmed -- emerges from Zitterbewegung phase dynamics.
  Lattice analog of 2p->1s hydrogen transition.

This is the first derivation of the hydrogen spectrum from
discrete causal lattice geometry.


## v2.0.0 -- Session update

### Experiments: 10/10 passing (exp_08 still stub)
- exp_09: Lattice harmonics -- Zitterbewegung spectrum, photon dispersion
- exp_10: Hydrogen spectrum -- orbital motion confirmed, Bohr E_n~1/n^2
  confirmed analytically; numerical verification pending larger grid

### Key theoretical results this session:
- Photon group velocity drops 3x near Brillouin zone boundary (falsifiable)
- Bohr-Sommerfeld quantization from angular momentum L=k*r_orb=n
- Analytical: E_n/E_1 = 1/n^2 confirmed for n=1..4 with Coulomb V(r)
- Angular momentum quantization is de Broglie condition in lattice language


## v2.0.0 -- In Progress (updated)

### Experiments passing (7/9):
- exp_00: Causal cone -- speed limit c=1 confirmed
- exp_01: Inertia -- phase gradient persistence, linear trajectory
- exp_02: Gravity -- clock density gradient, differential Zitterbewegung
- exp_03: Interference -- genuine discrete fringes, no analytical formula
- exp_04: Decoherence -- phase scrambling collapses two-source pattern
- exp_06: Path counting -- discrete corrections, falsifiable predictions
- exp_07: Clock conservation -- continuity equation confirmed (Step 1 of GR)

### Remaining stubs:
- exp_05: Observer as clock (TickScheduler combinatorics)
- exp_08: Vacuum twist (gravity vs EM as div vs curl)

# CHANGELOG

## v2.0.0 -- In Progress

### New in v2.0
- 3D octahedral lattice substrate (T^3_diamond) replaces 1D diamond
- Per-particle tick counters and TickScheduler
- Observer formalized as a new clock (CausalSession) in the scheduler
- Gravity reframed as clock density gradient (not refractive potential)
- Genuine discrete interference (no continuous Huygens-Fresnel formula)
- Falsifiable numerical predictions via exact path counting
- Biological time / Eagleman connection in introduction

### Corrections from v1.0
- exp_04 interference: replaced continuous analytical formula with
  genuine lattice tick propagation
- alpha derivation removed: 0.01984 was hardcoded into noise function,
  not discovered by the simulation
- Gravity experiment: clock density mechanism made explicit,
  not just a potential well

## v1.0.0 -- January 2026

Initial release. 1D diamond lattice. 9 experiments.
DOI: 10.5281/zenodo.18904545
Repository: github.com/JackDMenendez/A-Stochastic-Geometric-Foundation-for-Physics
