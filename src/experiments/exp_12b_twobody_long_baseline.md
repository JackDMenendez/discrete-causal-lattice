<!-- markdownlint-disable MD022 MD024 MD032 MD047 MD060 -->
# exp_12b_twobody_long_baseline.py

Long-duration two-body baseline -- bare exp_12 dynamics over the
exp_20 horizon, no emission machinery.

## Why this experiment exists

`exp_20` (three-arm emission operator comparison) found that none of
the three operators -- the as-written drain (Arm A), the unitary
beam splitter (Arm B), or the phase-rotation drain (Arm C) --
stabilises the orbit at $R_1 = 10.3$ over a 6000-tick horizon.
All three escape: in arm B the radial peak hits $r=53$ at tick 2019
before partly returning, in arm C it hits $r=69$ at tick 4019.

That result is consistent with two distinct hypotheses:

1. **Emission-mechanism hypothesis.**  None of the three operators is
   the right emission rule, and the orbital escape is the symptom.
2. **Baseline-instability hypothesis.**  The bare exp_12 two-body
   dynamics themselves are unstable on the 6000-tick horizon, so any
   emission operator inherits the instability.

`exp_12b` discriminates between these by running the bare two-body
system (no photon, no emission) over the same 6000 ticks and asking
whether the orbit stays at $R_1$ throughout.  If yes, hypothesis (1)
is the lead question and the next move is a rate sweep on arm B.  If
no, hypothesis (2) is the lead question and emission is downstream
of a more fundamental issue.

## Design

Identical to `exp_12` (live proton + electron, mean-field Coulomb,
alternating tick order, GRID = $65^3$, $\omega_e = 0.1019$,
$\omega_p = \pi/2$, STRENGTH=30, R1=10.3) except the run length is
extended to 6000 ticks to match `exp_20`.  Both sessions use
`tick(normalize=True)` -- the bare baseline has no emission to
disturb per-session unitarity, so the standard exp_12 normalisation
is appropriate.

Diagnostics logged at every check window (CHECK_EVERY=20):

- `r_peak` -- PDF peak of the electron density relative to the live
  proton CoM, the canonical orbital-radius estimator.
- `amp_e`, `amp_p` -- per-session amplitudes (should stay at 1.000
  with normalize=True).
- `A_joint_drift_max` -- maximum deviation of $\lVert\psi_e\rVert^2 + \lVert\psi_p\rVert^2$
  from initial.  In the baseline this is dominated by numerical
  precision (machine-epsilon) since both ticks normalise.
- `rho_phi_drift_max` -- omega-weighted drift of $\rho_\phi$ proxy.
- `r_peak_min`, `r_peak_max` -- range of orbital radius across the run.

## Predicted falsification matrix

| Outcome | Lead hypothesis | Next move |
|---|---|---|
| `r_peak` stays in $[R_1 \cdot (1-\text{TOL}), R_1 \cdot (1+\text{TOL})]$ across all 6000 ticks | Emission-mechanism hypothesis | Rate sweep on arm B of exp_20 (e.g. {0.01, 0.10, 0.20}); look for a rate where photon growth and orbit lock-in coincide. |
| `r_peak` escapes to $\geq 30$ at some tick | Baseline-instability hypothesis | Investigate the bare two-body dynamics: grid-size sensitivity, initial-condition sensitivity, the bipartite tick rule's long-horizon behaviour. |
| `r_peak` swings widely but returns near $R_1$ | Mixed | Both hypotheses partly true; the bare system is metastable and emission is one of several perturbations that destabilise it. |

## Running

### Smoke test (~14 s)

```bash
EXP12B_TICKS=20 python src/experiments/exp_12b_twobody_long_baseline.py
```

Confirms the wiring: r_peak ~ 9.88, amp_e = amp_p = 1.000, A_drift at
machine precision.

### Full baseline (~70 min)

```bash
EXP12B_TICKS=6000 python src/experiments/exp_12b_twobody_long_baseline.py
```

One worker, no parallelism needed -- there's only one configuration.

## Output files

- `data/exp_12b_baseline.log` -- per-window progress
- `data/exp_12b_baseline.npy` -- summary array
  `[settled, max_streak, T_settle, amp_e, amp_p, A_joint_drift_max, rho_phi_drift_max, r_peak_min, r_peak_max]`

## Smoke-test results (2026-05-02, GRID=65³, 20 ticks)

| Quantity | Value |
|---|---|
| r_peak (final window) | 9.877 |
| streak | 1 |
| amp_e, amp_p | 1.0000, 1.0000 |
| A_joint_drift_max | 4.4e-16 (machine precision) |
| rho_phi_drift_max | 6.7e-16 (machine precision) |

Per-tick cost: ~0.7 s on the win-cross-dev-env machine (faster than
exp_20 because there is no photon session).

## Full-run results (2026-05-02, GRID=65³, 6000 ticks)

| Quantity | Value | Comment |
|---|---|---|
| `r_peak_min` | 9.161 | close to R₁ at the start, before escape |
| `r_peak_max` | **83.336** | grid-edge value — full escape |
| `r_peak` at tick 2019 | 72.102 | already escaped by 1/3 of the run |
| `r_peak` at tick 4019 | 73.854 | still escaped, no return |
| `max_streak` | 5 | well below SUCCESS_STREAK = 33 |
| `amp_e_final`, `amp_p_final` | 1.000000, 1.000000 | per-session unitarity preserved by `tick(normalize=True)` |
| `A_joint_drift_max` | 8.9e-16 | machine precision |
| `rho_phi_drift_max` | 1.3e-15 | machine precision |
| Run time | 5234 s ≈ 87 min | one worker |

**Outcome:** row 2 of the falsification matrix above. The orbit hits
$R_1$ briefly at the start (within 15% tolerance for one window),
then walks outward and never returns. By tick 2019 it is already at
$r \approx 72$; by tick 4019 it is at $r \approx 74$. The bare exp_12
two-body system on $\text{GRID}=65^3$ is **not stable over 6000
ticks**.

**Implication for exp_20:** the orbital escapes seen across all three
arms of `exp_20` (A: r_peak ~16, B: r_peak ~53, C: r_peak ~69) are
inherited from this baseline instability, not caused by the emission
operator. The conservation diagnostics in `exp_20` (joint A=1
preserved exactly under arm B, $\rho_\phi$-proxy drift at the
predicted level) remain valid; the "does the orbit settle?" question
is downstream of a more fundamental long-horizon stability problem.

**Implication for exp_12:** `exp_12`'s PASS at 4 sig figs is not
invalidated. `exp_12` is scored on a shorter run length (the
resonance peak in a $k$-scan), and `exp_12b` only refines the
temporal scope of the lock-in claim: the Bohr orbit is metastable on
the lattice, lasting hundreds of ticks but not thousands.

**What is not yet known** (deferred to a future experiment):

- Whether the escape is grid-size dependent (GRID=65³ may be too
  small to contain the late-time wavepacket; a larger grid would
  push the escape boundary outward).
- Whether the escape is initial-condition dependent (the CoM-frame
  alignment may carry residual asymmetry that compounds).
- Whether the escape is attributable to the bipartite tick rule's
  near-unitary approximation accumulating error over $\gtrsim 10^3$
  ticks.

## Proposed audit-table row (pending dcl-claim-auditor validation)

```latex
Two-body long-horizon stability
    & Bare \texttt{exp\_12} chassis at 6000-tick horizon, no emission
    & Standard QM treats Bohr orbits as stationary
    & \texttt{exp\_12b} 2026-05-02 single run at $\text{GRID}=65^3$,
      $r_\text{peak}$ escapes from $\sim R_1$ to grid edge ($\sim 83$)
      by tick 2019; $\mathcal{A}=1$ preserved at machine precision
      ($8.9\times 10^{-16}$); refines but does not invalidate
      \texttt{exp\_12}'s 4-sig-fig PASS, which is scored on a shorter
      $k$-scan resonance peak
    & \texttt{PART} \\
```

This row is *additive* — it does not modify the existing
`Two-body hydrogen (4 sig figs)` row (`exp_12`, PASS), which scores
a different claim (Bohr-radius matching at fixed $k$). The two rows
sit alongside each other in the audit table.

## Status

- **Implementation**: complete ✓
- **Full 6000-tick baseline**: complete ✓ (2026-05-02)
- **Result**: NOT_SETTLED -- bare two-body escapes; baseline-instability
  hypothesis confirmed
- **Audit-table row**: drafted above; pending dcl-claim-auditor
  validation and commit (deferred to a future session restart so the
  auditor agent loads from `.claude/agents/`)

## Relation to other experiments

- **vs `exp_12_hydrogen_twobody`**: `exp_12b` leaves `exp_12`
  unmodified.  The two share their two-body initialisation; `exp_12b`
  extends the run length to match `exp_20`'s horizon.
- **vs `exp_20_emission_operator`**: `exp_12b` is the no-emission
  control for the three-arm comparison.  Same chassis, same
  diagnostics, photon channel removed.
- **vs `exp_19c_photon_emission`**: same predecessor lineage.

## References

- `notes/exp_20_emission_operator_and_clock_fluid.md` -- emission-
  operator design and the question this baseline informs
- `paper/sections/audit_table.tex` -- target for the new audit row
- `src/experiments/exp_12_hydrogen_twobody.py` -- canonical two-body
  reference (kept intact)
- `src/experiments/exp_20_emission_operator.py` -- the experiment
  whose escape behaviour this baseline contextualises
