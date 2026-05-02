<!-- markdownlint-disable MD022 MD024 MD032 MD047 MD060 -->
# exp_20_emission_operator.py

Three-arm controlled comparison of photon-emission operators on the
bipartite A=1 lattice.

## Overview

Tests the operation-algebra prediction (notes/lattice_operation_algebra.md,
notes/exp_20_emission_operator_and_clock_fluid.md) that the as-written
amplitude drain in `exp_19c` is non-unitary, and that a pointwise beam
splitter with **joint** A=1 enforcement is the correct emission operator.

The same exp_12 two-body initialisation, the same Coulomb-driven mask,
the same alternating-tick order. Only the emission operator differs
between arms.

## Physics background

The operation-algebra table (see `notes/lattice_operation_algebra.md`)
identifies three candidate emission operators:

| Row | Operator | Joint A=1? | Photon grows? |
|----:|---|:---:|:---:|
| 5 (A) | $\psi_e \mathrel{-}\!= m\psi_e;\ \psi_\gamma \mathrel{+}\!= m\psi_e$ | No -- $(1-2m+2m^2)$ | Masked by per-session enforce |
| 6 (B) | $\psi_e \mathrel{*}\!= \cos\theta;\ \psi_\gamma \mathrel{+}\!= \sin\theta\,\psi_e$ | Yes (pointwise) | Yes |
| 7 (C) | $\psi_e \mathrel{*}\!= e^{-i\alpha};\ \psi_\gamma \mathrel{*}\!= e^{+i\alpha}$ | Yes (per-session) | No |

Row 5 is what `exp_19c` v10 implements; the per-session
`enforce_unity_spinor` on both electron and photon resets each to unit
norm independently, masking the drain's non-unitarity. Row 6 is the
unitary 2-mode rotation that emission *should* be in the joint A=1
framework. Row 7 is `exp_19` v5 (phase-rotation drain): amplitudes are
preserved by construction but no amplitude is transferred to the
photon.

## Three arms

### Arm A (control) -- exp_19c reproduction

```text
psi_e -= m * psi_e
psi_gamma += m * psi_e
enforce_unity_spinor(psi_e)
enforce_unity_spinor(psi_gamma)
```

Per-session normalization on both electron and photon. The photon's
amplitude is reset to unit norm on the first emission tick, so
`amp_g = 1.0` immediately. The drain's non-unitarity is hidden by the
per-session reset.

**Predicted result:** orbit does not settle (reproduces `exp_19c`
NOT_SETTLED, max_streak ≤ 11). Photon amplitude artificially inflated
to ~1.0. `A_joint_drift_max ≈ 1.0`.

### Arm B (treatment) -- pointwise beam splitter + joint A=1 enforcement

```text
sin_theta = m
cos_theta = sqrt(1 - sin_theta^2)
psi_gamma += sin_theta * psi_e
psi_e *= cos_theta
enforce_joint_unity(psi_e, psi_gamma, target = ||psi_e0||^2 + ||psi_gamma0||^2)
```

The beam splitter is a pointwise unitary 2-mode rotation that preserves
$\lVert\psi_e\rVert^2 + \lVert\psi_\gamma\rVert^2$ pointwise under exact
dynamics. The bipartite tick rule with `normalize=False` introduces
small residual drift (the kinetic + residence step is only
approximately norm-preserving on the discrete lattice), so
`enforce_joint_unity` rescales both sessions by a common factor to
restore the joint amplitude to its initial value. Because the rescaling
is global (same factor on both), the beam splitter's amplitude ratio
$\lVert\psi_\gamma\rVert^2 / \lVert\psi_e\rVert^2$ is preserved -- only
the tick rule's residual drift is absorbed.

**Predicted result:** photon amplitude grows from ~0; orbital lock-in
achievable; `A_joint_drift_max ≈ 0` (preserved to numerical precision);
`rho_phi_drift_max ≈ Δm × (ω_γ − ω_e)` per emission tick (the genuine
emission energy transfer, not a violation).

### Arm C (alternative) -- phase-rotation drain (exp_19 v5 reproduction)

```text
psi_e *= exp(-i * alpha)
psi_gamma *= exp(+i * alpha)
enforce_unity_spinor(psi_e)
# psi_gamma is intentionally NOT renormalized
```

Each session is multiplied by a unit-modulus pointwise phase rotation.
Per-session amplitudes are preserved by the rotation itself
(|exp(iφ)| = 1). The electron is renormalized after the rotation to
absorb the bipartite tick rule's drift; the photon is *not*
renormalized -- it should stay at its near-zero seed amplitude under
arm C, and a unity enforcer would artificially inflate it (the same
mode of failure as arm A).

**Predicted result:** photon amplitude stays at ~0; per-session
amplitudes preserved exactly; orbital response indistinguishable from
the no-emission baseline. Tests whether *phase-coherence* transfer
without amplitude transfer can drive emission (it cannot, per the
operation-algebra prediction).

## Falsification matrix

| Outcome | Interpretation |
|---|---|
| A and B both fail to settle | Emission mechanism is something else entirely; algebra is wrong about row 6 being the fix. |
| A fails, B succeeds | Joint A=1 with unitary transfer is the correct emission physics, and per-session `enforce_unity_spinor` is the latent bug across `exp_15`, `exp_19` (v4), `exp_19c`. |
| A succeeds by `SETTLE_TOL = 0.15` and B doesn't differ | The streak metric is measuring proximity to $R_1$, not tongue residence. Audit-table observation about predicted tongue width 3.3% becomes the headline; rerun under `SETTLE_TOL = 0.033`. |
| C settles where A and B don't | Surprising; would imply phase-coherence transfer alone drives emission. Not predicted by the operation algebra. |

## Diagnostics

Two conservation diagnostics are logged at every check window:

- **`A_joint_drift_max`** -- the maximum deviation of $\sum_i \lVert\psi_i\rVert^2$
  from its initial value across all checks during the run. Arm A
  produces ~1.0 immediately (photon inflation); arm B produces ~0
  (joint enforce); arm C produces numerical-noise levels.

- **`rho_phi_drift_max`** -- the maximum deviation of
  $\rho_\phi^\text{proxy} = \sum_i \omega_i\,\lVert\psi_i\rVert^2$ from its
  initial value. This is the integrated form of the omega-weighted
  amplitude density, and it tracks energy conservation. Arm A produces
  drift dominated by the photon-inflation bug (~0.076 = $\omega_\gamma \times 1$);
  arm B produces drift at the genuine emission rate; arm C produces
  numerical-noise levels.

The two diagnostics together discriminate the three arms cleanly even
in short runs.

## Implementation

### Key parameters

| Parameter | Value | Source |
|---|---|---|
| `OMEGA_E` | 0.1019 | hydrogen Bohr from `exp_10` |
| `OMEGA_P` | π/2 | proton mass from `exp_16` |
| `OMEGA_G` | 0.75 × OMEGA_E | n=2 → n=1 transition proxy |
| `STRENGTH` | 30.0 | hydrogen Coulomb (exp_10) |
| `SOFTENING` | 0.5 | hydrogen Coulomb (exp_10) |
| `R1` | 10.3 | Bohr radius from `exp_10` / `exp_12` |
| `GRID` | 65 | from `exp_19c`, `exp_12` |
| `TICKS_TOTAL` | env `EXP20_TICKS` (default 100; settled run wants 6000) |
| `CHECK_EVERY` | 20 | window size for stability check |
| `SETTLE_TOL` | 0.15 | r_peak within 15% of R1 (loose; tongue-width 3.3% would be tighter) |
| `SUCCESS_STREAK` | 33 | 3× best two-session baseline |
| `DEFAULT_RATE` | env `EXP20_RATE` (default 0.05) |

### Emission rate parameterisation

The same Coulomb-driven mask is used by all three arms:

```text
emit_mask(x) = emission_rate * max(0, V(x) - V_ground) / |V_ground|
```

For arm A this is the linear drain rate $m$. For arm B it is
$\sin\theta(x)$, so $\cos\theta = \sqrt{1 - m^2}$. For arm C it is the
phase-rotation angle $\alpha(x)$ in radians. For small values, all
three operators agree linearly; differences appear at $O(m^2)$.

### `enforce_joint_unity` helper

```python
def enforce_joint_unity(s1, s2, target):
    current = session_amplitude(s1) + session_amplitude(s2)
    if current > 1e-12:
        scale = np.sqrt(target / current)
        s1.psi_R *= scale
        s1.psi_L *= scale
        s2.psi_R *= scale
        s2.psi_L *= scale
```

Used only by arm B. The proton is unaffected (it stays at unit norm via
its own `tick(normalize=True)`).

## Running the experiment

### Smoke test (~17 s per arm at GRID=65³)

```bash
EXP20_TICKS=20 python src/experiments/exp_20_emission_operator.py A 0.05
EXP20_TICKS=20 python src/experiments/exp_20_emission_operator.py B 0.05
EXP20_TICKS=20 python src/experiments/exp_20_emission_operator.py C 0.05
```

Verifies wiring; not enough ticks to test orbital lock-in.

### Single-arm full run

```bash
EXP20_TICKS=6000 python src/experiments/exp_20_emission_operator.py B 0.05
```

~100 minutes per arm at the per-tick cost observed during smoke test
(~1 s/tick on the user's win-cross-dev-env machine).

### Three-arm parallel sweep (one rate, three arms)

```bash
EXP20_TICKS=6000 python src/experiments/exp_20_emission_operator.py
```

Spawns three subprocess workers (one per arm) at the default rate.
Total wall-clock = ~100 minutes (the slowest arm).

### Multi-rate, three-arm sweep

```bash
EXP20_ARMS=A,B,C EXP20_TICKS=6000 EXP20_RATE=0.10 python ...
```

Repeat at multiple rates by re-invoking with different `EXP20_RATE`
values. Output files include the rate in the filename, so multiple
sweeps coexist in `data/`.

## Output files

For each `(arm, rate)` combination:

- `data/exp_20_arm_<arm>_r<rate>.log` -- per-window progress log
- `data/exp_20_arm_<arm>_r<rate>.npy` -- summary array
  `[ord(arm), rate, settled, max_streak, T_settle, amp_e, amp_p, amp_g, A_joint_drift_max, rho_phi_drift_max]`
- `data/exp_20_arm_<arm>_r<rate>.err` -- subprocess stderr (only when launched via `run_parallel`)

## Smoke test results (2026-05-02, GRID=65³, 20 ticks each)

| Arm | amp_e | amp_p | amp_g | A_joint_drift | rho_phi_drift | Notes |
|---|---|---|---|---|---|---|
| A | 1.000 | 1.000 | **1.000** | **1.0e+00** | 7.6e-02 | Photon inflated to unit norm by per-session enforce -- the exp_19c bug visible at first emission tick. |
| B | 0.995 | 1.000 | 0.0055 | **0.0e+00** | 1.4e-04 | Joint amplitude preserved exactly; rho_phi shift = 0.0055 × (ω_γ − ω_e), the genuine emission energy transfer. |
| C | 1.000 | 1.000 | 0.000 | 9.8e-13 | 7.5e-14 | No amplitude transfer; per-session amplitudes preserved at numerical precision. |

The diagnostics already discriminate the three arms cleanly at 20 ticks.
The settled-orbit-lock-in question requires the full 6000-tick run (or
longer); the smoke test only verifies wiring and unitarity claims.

## Status

- **Implementation**: complete, smoke-tested ✓
- **Full 6000-tick sweep**: pending (recommended next step; ~100 min/arm in parallel)
- **Audit-table update**: pending until a settled run is in hand
- **Documentation**: this file
- **Predecessor crossover**: leaves `exp_19c` untouched -- this is a new file, not a modification

## Relation to other experiments

- **vs `exp_12`**: same two-body initialisation; adds emission channel.
- **vs `exp_19c`**: arm A is the exp_19c reproduction (its current operator); arm B is the proposed correction.
- **vs `exp_19` v5**: arm C is the v5 phase-rotation drain reproduction.
- **Future audit-table impact**: if arm B settles, the row "Photon emission as $\mathcal{A}=1$ necessity" can move from `PART` to `PASS` -- but only on settled-orbit data, not on the smoke test.

## References

- `notes/lattice_operation_algebra.md` -- tag-balance table; row 5 vs row 6 distinction
- `notes/exp_20_emission_operator_and_clock_fluid.md` -- design rationale, clock-fluid identification, path-algebra reformulation
- `paper/sections/audit_table.tex` -- authority for current `exp_19c` PART status
- `src/experiments/exp_19c_photon_emission.py` -- predecessor; what arm A reproduces
- `src/experiments/exp_12_hydrogen_twobody.py` -- two-body foundation
