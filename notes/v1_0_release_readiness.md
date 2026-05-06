<!-- markdownlint-disable MD022 MD024 MD026 MD032 MD034 MD047 MD060 -->
# v1.0 release readiness summary (2026-05-05)

*Snapshot of the v1.0-track work since v0.98-RC (2026-05-03).  This
note is a checkpoint for deciding when to cut the v1.0 release; it
is not paper material and does not commit to a release date.*

## What landed since v0.98-RC

### Experimental work (closes outstanding questions)

| Experiment | What it answered | Audit-table consequence |
|---|---|---|
| `exp_12c` (long-horizon escape diagnosis) | The $65^3$ "stability" was a finite-volume artefact: bare two-body orbit escapes at tick $\sim 140$ on $\geq 81^3$ and tick $\sim 2000$ on $65^3$.  Init-mode and drift-mode controls rule out initial-condition and operator-drift causes. | New row "Long-horizon escape mechanism" (`PART`) |
| `exp_12d` (grid k-scan, full window) | Split outcome — resonance observable on $65^3$ only, others escape during the 50-199 measurement window.  Established that the proxy works but the window must stay inside the pre-escape phase. | Superseded by `exp_12d_tight`; documented in `exp_12d.md` |
| `exp_12d_tight` (grid k-scan, pre-escape window) | Lock-in resonance is grid-independent: $r$ at $k_\text{Bohr}$ in $[11.54, 12.30]$ across all four grids (65/81/97/113), three of four argmins within $\pm 0.003$ of $k_\text{Bohr}$, $r_\text{std}$ tight ($1.1$–$2.9$) on 38 of 40 trials. | New row "Lock-in resonance grid-independence" (`PART`) |
| `exp_12d_outlier_trace` (outlier characterisation) | The two outliers at $k = 0.101$ on 81/113³ are early-escape tail of `exp_12c`'s metastable-orbit mechanism, not tail noise and not a $k = 0.101$ instability.  The grid-independence claim is *strengthened*, not weakened. | Cited in the `exp_12d_tight` row |

### Theoretical work (Tier 1 + Tier 2 v1.0 proofs)

| Item | Note | Paper-section patch |
|---|---|---|
| Tier 1 — Born rule via Gleason | `notes/born_rule_gleason_uniqueness.md` | §10.7 inserted Gleason uniqueness subsubsection |
| Tier 2 — $g_{\mu\nu}$ from $\rho_\text{clock}$ | `notes/g_mu_nu_clock_density_identification.md` | §7.7 added "metric tensor from clock density" subsection |
| Tier 2 — Lie-algebra automorphism conjecture | `notes/lie_algebra_automorphism_proof_sketch.md` | §15 conjecture replaced with corrected four-bullet decomposition |

### Step 5 computational scaffolding (six scripts in `src/utilities/`)

| Script | Result |
|---|---|
| `automorphism_discrete.py` | Discrete $\mathrm{Aut}(\Gamma, V)$ has 48 elements ($B_3 \cong O_h$); only 12 are orthogonal in standard $\mathbb{R}^3$ |
| `automorphism_rgb_su3.py` | RGB symmetry contributes only $\mathbb{Z}_3 \subset SU(3)$; abelian $\to$ cannot generate non-abelian $SU(3)$ |
| `automorphism_direct_product.py` | Per-site $SU(2)$ generators on existing $\mathbb{C}^2$ are *the same matrices* as Lorentz rotation generators — not a separate factor |
| `automorphism_direct_product_extended.py` | On extended $\mathbb{C}^{12}$, all four conjecture factors commute pairwise; total dim 18 verified |
| `tick_rule_extended_consistency.py` | Trivial tensor extension of bipartite tick rule preserves $\mathcal{A}=1$, global $SU(2)_W \times SU(3)$, and bipartite parity |
| `tick_rule_gauge_invariance.py` | Gauge-coupled extension's matter bilinear and Wilson plaquette are gauge-invariant; bipartite plaquette identified as 4-link square $V_1, -V_2, -V_1, V_2$ |

### Documentation infrastructure

- Follow-on paper #16 ("SM gauge derivation: extended-amplitude
  direct-product construction") added to
  `notes/follow_on_implications.md` with four substantive
  open questions.  Index entry only; future draft material to live
  in the external research repo per established convention.
- Audit table now carries three new rows reflecting the recent
  experimental + theoretical work (`exp_12c`, `exp_12d_tight`, SM
  gauge automorphism conjecture).
- Paper page count: 138 (v0.98-RC) → 142 (v1.0-track) from the
  three Tier 1+2 paper-section patches and three new audit rows.

## What's structurally different from v0.98-RC

The v1.0-track work has substantively *refined* the SM-derivation
claim relative to v0.98-RC.  v0.98-RC's §15 stated the automorphism
conjecture programmatically.  v1.0-track has produced:

- A precise statement of the conjecture as a finite-dimensional
  Lie-algebra equality (dim 18).
- Computational verification that the conjecture's RHS is
  *achievable* as a direct product on an extended per-site
  $\mathbb{C}^{12}$ amplitude.
- An explicit identification of the structural extensions needed:
  per-site $\mathbb{C}^2$ isospin doublet for $SU(2)_W$, per-site
  $\mathbb{C}^3$ colour triplet for $SU(3)$.
- A closed-form Wilson action template using the bipartite-specific
  4-link plaquette $V_1, -V_2, -V_1, V_2$.
- Honest accounting of what's open: tick-rule extension consistency
  *partially* closed (trivial extension preserves invariants but
  gauge coupling open); exact equality vs containment in
  $\mathrm{Aut}_\text{extended}$ open; SM-chirality coupling open;
  explicit $1/g^2$ prefactors open.

The v1.0-track conjecture is *stronger* than v0.98-RC's because the
structural pieces are now concrete, computationally scaffolded, and
each open question is precisely scoped.

## Outstanding for v1.0 release

### Required (blocking)

- **dcl-claim-auditor pass**: at next session restart, audit the three
  new audit-table rows, the §10.7 / §7.7 / §15 paper-section
  patches, and the proof-sketch notes.  Confirm `PART` and `STUB`
  status assignments are honest.  Estimated: 1 session of audit work.

### Recommended (improves release quality)

- **§7.7 cross-references**: the new "metric tensor from
  $\rho_\text{clock}$" subsection references `eq:boltzmann_clock`
  and `eq:poisson_derive`.  Verify these resolve correctly in the
  built PDF (already verified by build, but a manual eyeball check
  on the rendered output would catch any prose-flow issues).
- **§10.7 cross-references**: the inserted Gleason subsubsection
  cites `gleason1957`.  Verify the citation appears correctly in
  the bibliography of the rendered output.
- **§15 cross-references**: the new automorphism conjecture cites
  `sympy_lie` and references `subsec:macro_tick`,
  `subsec:dirac_limit`, `sec:gravity`, `sec:kinematics`, and
  `subsec:born_rule_paths`.  Verified by build; eyeball check on
  the rendered output recommended.

### Optional (deferrable)

- **Step 5 question (ii)**: Lie-algebra enumeration to verify
  $\mathrm{Aut}_\text{extended}$ is *exactly* the four-factor
  product, not just $\supseteq$.  Tractable but not blocking
  for v1.0.
- **Step 5 question (iii)**: SM-chirality coupling (LH-only
  $SU(2)_W$).  Substantive structural problem; explicitly scoped
  for the follow-on paper.
- **1/g² prefactor calculation** for $SU(2)_W$ and $SU(3)$,
  generalising the existing U(1) calculation in
  `induced_gauge_action.tex`.  Research-stage work; flagged as open
  in the audit table row.

## Net assessment

**The v1.0-track is complete enough to release.**  The three
substantive deliverables — Tier 1 Born rule via Gleason, Tier 2
$g_{\mu\nu}$ explicit metric, Tier 2 Lie-algebra automorphism
precise statement — are all in the paper with honest accounting of
what's established and what remains open.  The grid-independence
work closes a question (whether `exp_12`'s `PASS` is robust across
grid sizes) that was unresolved at v0.98-RC, and it closes it
favourably.

The v1.0 release would be:

- A precise, computationally-scaffolded SM-derivation conjecture in
  §15 (replacing v0.98-RC's programmatic statement).
- Independent grid validation of `exp_12`'s lock-in result
  (paper-text cross-reference + audit table entry).
- A Boltzmann-form metric tensor formula in §7.7 that closes the
  "honest gap" of the gravity derivation programme.
- A Gleason uniqueness statement in §10.7 that addresses
  Reviewer-E's "where is the necessity argument?" concern.

What would *not* be in v1.0:

- The actual closing of the central open Lie-algebra calculation
  (deferred to follow-on paper #16).
- The explicit 1/g² prefactor for $SU(2)_W$ and $SU(3)$ (deferred).
- The SM-chirality coupling problem (deferred).

These are explicitly scoped as the follow-on paper #16 in
`notes/follow_on_implications.md`.

## Recommended next action

Either:

1. **Cut v1.0** after the dcl-claim-auditor pass.  Most of the
   v1.0-track work is already in the paper; an audit pass + sanity
   eyeball + Zenodo deposit would close the release.

2. **Continue Step 5 question (ii)** — verify exact equality of
   $\mathrm{Aut}_\text{extended}$ — before cutting v1.0.  This
   would tighten the §15 statement but is not blocking.

3. **Begin the 1/g² prefactor calculation** for $SU(2)_W$ and
   $SU(3)$ — generalise the U(1) calculation in
   `induced_gauge_action.tex`.  Research-stage work; outcomes
   could either tighten v1.0 or feed directly into follow-on #16.

The conservative path is (1).  The v1.0-track has produced enough
substantive content to justify a release; further work belongs to
the follow-on paper.
