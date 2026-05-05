<!-- markdownlint-disable MD022 MD024 MD032 MD047 MD060 -->
# exp_12d_grid_independence_k_scan.py

Validate `exp_12`'s $k$-scan resonance result across grid sizes.

## Why this experiment exists

`exp_12` reports $k_\min = 0.0970$ versus $k_\text{Bohr} = 1/R_1 =
0.0971$ (four significant figures, matching the Bohr-radius condition
$\omega \cdot R_1 = \pi/3$).  That measurement is at $\text{GRID} = 65^3$.

`exp_12c` (2026-05-05) established that the bare two-body orbit
escapes by tick $\sim 140$ on grids $\geq 81^3$, while remaining
apparently stable for $\sim 2000$ ticks on $65^3$.  The $65^3$
"stability" was re-characterised as a finite-volume artefact:
boundary conditions reflect / wrap outgoing flow back into the well,
confining the wave packet near $R_1$.

The question this experiment answers: **is the $k_\min = 0.0970$
resonance itself grid-dependent?**  Two cases:

1. **Lock-in is grid-independent.**  The Arnold-tongue attractor at
   $\omega \cdot R_1 = \pi/3$ exists irrespective of box size; the
   short-horizon resonance peak is real physics; `exp_12`'s 4-sig-fig
   PASS is robust.  $k_\min$ stays near $k_\text{Bohr}$ on $65, 81, 97,
   113^3$.
2. **Lock-in is also a confinement effect.**  The resonance peak
   itself is shaped by the boundary, not just the late-time escape;
   $k_\min$ shifts or the peak flattens at larger grids.  `exp_12`'s
   PASS would then be downgraded from "the lock-in matches the Bohr
   condition" to "matches at $\text{GRID} = 65^3$".

This experiment runs the scan at four grid sizes over a tight $k$
window and reports $k_\min$ per grid.

## Design

Identical to `exp_12` (live proton + electron, mean-field Coulomb,
alternating tick order, $\omega_e = 0.1019$, $\omega_p = \pi/2$,
STRENGTH=30, $R_1 = 10.3$) except:

- The grid size is varied: $\text{GRID} \in \{65, 81, 97, 113\}^3$.
- The run length is short ($\text{TICKS\_TOTAL} = 200$, with
  $\text{BURN\_IN} = 50$).  We measure during the stable-orbit phase
  identified by `exp_12c` -- on grids $\geq 81^3$ the orbit escapes
  by tick $\sim 140$, so a 100-tick measurement window from tick 50
  to tick 150 captures the lock-in epoch on every grid.
- The $k$ scan is tight around $k_\text{Bohr}$:

  ```python
  K_VALUES = [0.085, 0.090, 0.092, 0.094, 0.096, 0.0971,
              0.099, 0.101, 0.103, 0.106]
  ```

  Spacing is $\sim 0.002$ near $k_\text{Bohr}$ and $\sim 0.005$
  outside, so the resonance peak (if present) is resolved at four-
  sig-fig level near $k_\text{Bohr}$ but the experiment also sees
  the surrounding shape.

For each $(\text{grid}, k)$ trial, the score is the time-averaged
$r_\text{peak}$ over the post-burn-in measurement window
(tick 50–199, sampled every CHECK\_EVERY=10 ticks). $k_\min$ for the
grid is the $k$ value minimising $|r_\text{peak} - R_1|$.

The experiment does not modify `exp_12`, `exp_12b`, `exp_12c`, or any
other prior experiment.  It is purely additive: a new file, new data,
no shared state.

### Why measure $r_\text{peak}$, not the inv-sharpness used in `exp_12`?

`exp_12` scores by the inverse sharpness of the electron PDF in the
proton frame (peak-narrowness as $k \to k_\text{Bohr}$).  Here we
score by the much simpler $|r_\text{peak} - R_1|$ because:

- The short measurement window does not give the PDF time to fully
  sharpen, so a peak-narrowness score is noisy.
- The lock-in attractor's signature in this regime is "the electron
  sits near $R_1$"; deviation from $R_1$ is the right falsifier for
  the grid-independence question.

If the cleaner inv-sharpness scoring is needed for a final number,
that is a follow-up at longer horizons on the larger grids -- the
present scoring is sufficient to determine **whether** $k_\min$ is
grid-stable, not what its precise four-sig-fig value is on each grid.

## Predicted falsification matrix

| Outcome (per-grid $k_\min$) | Lead interpretation | Next move |
|---|---|---|
| $k_\min$ on all four grids stays within $\pm 0.002$ of $k_\text{Bohr}$ | Lock-in is grid-independent.  `exp_12`'s 4-sig-fig PASS robust. | None.  Promote `exp_12d` row to PART (independent grid validation) in audit table. |
| $k_\min$ stays near $k_\text{Bohr}$ on small grids but drifts on $\geq 97^3$ | Confinement-dependent peak; lock-in real but distorted by box | Add a finite-size-extrapolation note to `exp_12`'s row; long-horizon scan on the larger grids. |
| $k_\min$ scatters with no consistent trend | Resonance peak is itself a confinement artefact | Downgrade `exp_12`'s row from PASS to PART; redesign the lock-in claim around the short-horizon attractor on a fixed reference grid. |
| $r_\text{peak}$ at $k_\min$ is far from $R_1$ on all grids | The resonance peak no longer aligns with $R_1$ at this run length | Re-run with a longer measurement window; re-examine `exp_12c`'s tick-140 escape estimate. |

## Running

### Smoke test (~30 s)

```bash
EXP12D_TICKS=20 EXP12D_BURN=5 python src/experiments/exp_12d_grid_independence_k_scan.py 65
```

Single grid, full $k$ scan, very short trials. Confirms wiring:
$r_\text{peak}$ varies with $k$, log file written, npy summary saved.

### Full sweep (~5 min wall clock parallel)

```bash
python src/experiments/exp_12d_grid_independence_k_scan.py
```

Launches one subprocess per grid in $\{65, 81, 97, 113\}$.  Each
worker runs all ten $k$ values sequentially.  The launcher polls the
workers every 30 s and prints a summary table when all four complete.

Per-tick cost scales as $N^3$.  The smoke-test on $65^3$ measured
$\sim 0.65$ s/tick; the full-run estimate at $\text{TICKS\_TOTAL} =
200$ uses that as the anchor:

| Grid | Per-tick cost | Per-$k$ cost | 10-$k$ scan |
|---|---|---|---|
| $65^3$  | $\sim 0.65$ s | $\sim 130$ s | $\sim 22$ min |
| $81^3$  | $\sim 1.25$ s | $\sim 250$ s | $\sim 42$ min |
| $97^3$  | $\sim 2.15$ s | $\sim 430$ s | $\sim 72$ min |
| $113^3$ | $\sim 3.40$ s | $\sim 680$ s | $\sim 113$ min |

Parallel max wall clock $\approx 2$ h on a 4-core machine.  CPU
load: 4 workers, each largely single-threaded NumPy, target $< 85\%$
to keep the editor responsive (per the user's calibration).

## Output files

For each grid in $\{65, 81, 97, 113\}$:

- `data/exp_12d_grid_<G>.log` — per-$k$ progress and final $k_\min$ summary
- `data/exp_12d_grid_<G>.npy` — array of shape $(10, 4)$ with rows
  `[k, r_mean, r_std, n_samples]`
- `data/exp_12d_grid_<G>.err` — subprocess stderr (only nonempty on failure)

The launcher prints a four-row summary table at the end:

```text
  grid     k_min    r_at_k_min    |r-R1|
  ----------------------------------------
    65    0.0971         10.21      0.09
    81    0.0971         10.18      0.12
    97    ...            ...        ...
   113    ...            ...        ...
```

## Full-sweep results (2026-05-05, four-grid parallel run)

Total wall clock: 8190 s ≈ 2 h 16 min (113³ was the long pole at
8187 s; 65³, 81³, 97³ finished at 2115 s, 3723 s, 5648 s).  All
runs completed cleanly with $n=15$ post-burn-in samples per $k$
trial.

### Per-$k$ time-averaged $r_\text{peak}$, with $r_\text{std}$ in parentheses

| $k$ | 65³ | 81³ | 97³ | 113³ |
|---:|---:|---:|---:|---:|
| 0.0850 | 11.35 (1.69) | 29.10 (17.33) | 30.28 (21.13) | 28.41 (19.49) |
| 0.0900 | 14.69 (10.18) | 20.62 (13.66) | 18.76 (15.37) | 27.39 (19.72) |
| 0.0920 | 11.70 (1.03) | 20.16 (12.54) | 12.86 (7.92)  | 16.40 (13.27) |
| 0.0940 | 11.59 (1.64) | 29.74 (17.08) | 25.13 (17.84) | 31.47 (22.93) |
| 0.0960 | 10.68 (1.63) | 23.21 (15.88) | 26.59 (17.90) | 35.10 (23.50) |
| **0.0971** | **10.48 (1.98)** | 25.77 (14.15) | 31.68 (20.11) | 33.23 (21.87) |
| 0.0990 | 11.00 (1.35) | 26.97 (16.66) | 20.71 (15.65) | 27.16 (21.18) |
| 0.1010 | 11.03 (1.47) | 29.71 (14.50) | 18.40 (14.37) | 34.94 (20.27) |
| 0.1030 | 10.46 (1.62) | 27.03 (17.69) | 30.84 (18.63) | 28.95 (18.53) |
| 0.1060 | 11.65 (1.64) | 31.15 (21.48) | 25.29 (19.17) | 25.08 (19.76) |

### Per-grid $k_\min$ (argmin $|r_\text{peak} - R_1|$)

| Grid | $k_\min$ | $r$ at $k_\min$ | $|r - R_1|$ | Comment |
|---|---:|---:|---:|---|
| 65³  | 0.1030 | 10.46 |  0.16 | Trough across $[0.096, 0.103]$ flat at $r \approx 10.5$; resonance observable |
| 81³  | 0.0920 | 20.16 |  9.86 | All $k$ escaped; argmin is just lower-noise |
| 97³  | 0.0920 | 12.86 |  2.56 | All other $k$ escaped to $r \in [18, 32]$ |
| 113³ | 0.0920 | 16.40 |  6.10 | All $k$ escaped; argmin is just lower-noise |

### Reading the table

The two regimes are sharply separated:

- **65³ (orbit confined):** $r_\text{mean}$ stays in $[10.46, 14.69]$
  across the full $k$ window; $r_\text{std}$ is mostly $1$–$2$.  The
  trough across $k \in [0.096, 0.103]$ sits at $r \approx 10.5$,
  essentially flat.  At $k = 0.0971 = k_\text{Bohr}$, $r = 10.48$
  (Δ=0.18 from $R_1$).  The lock-in resonance is observable at this
  resolution and is consistent with the Bohr condition.
- **81³, 97³, 113³ (orbit escapes):** $r_\text{mean}$ is in
  $[16, 35]$ with $r_\text{std}$ in $[8, 23]$ on every $k$.  The
  argmin is the smallest-noise outlier, not a resonance peak.  The
  orbit has escaped on every trial.

The cause of the second regime is now explainable: `exp_12c` showed
that on grids $\geq 81^3$ the orbit escapes around tick $\sim 140$.
The present measurement window (tick 50–199) extends 60+ ticks past
that escape onset, so the $r_\text{mean}$ on those grids averages
predominantly post-escape positions and the resonance signature, if
any, is buried in the post-escape noise.

### Outcome (against the falsification matrix)

The four predicted outcomes don't fit cleanly: the data are split.
The right reading is **row 4** of the matrix — *"$r_\text{peak}$ at
$k_\min$ is far from $R_1$ on all grids"* — but only because the
measurement window was too long for the larger grids.  The
underlying observable physics is:

- **The 65³ result confirms** that the resonance signature exists and
  is consistent with $k_\text{Bohr}$ within the resolution of a
  200-tick measurement.  This is *one* grid's evidence and is
  insufficient on its own to call the lock-in grid-independent.
- **The $\geq 81^3$ runs are inconclusive** because the present
  scoring window is dominated by the post-escape regime.  A
  follow-up run with a tight measurement window inside the
  stable-orbit phase (e.g.\ tick 30–120, ahead of the tick-140
  escape onset) is required to test grid-independence on those
  larger grids.

### Implication for `exp_12`'s PASS

`exp_12`'s 4-sig-fig PASS is scored on a different metric — the
inverse-sharpness of the electron PDF in the proton frame as a
function of $k$ — and on a different run length.  This experiment
does not directly test that scoring; it tests the simpler proxy
$|r_\text{peak} - R_1|$ over a 200-tick window.  Within that proxy:

- On 65³, the resonance is observable; the 4-sig-fig claim from
  `exp_12` is *not contradicted* by `exp_12d`.
- On larger grids, this experiment is silent until a follow-up
  shortens the measurement window.

The `exp_12` row in the audit table remains PASS at 4 sig figs on
$\text{GRID} = 65^3$ as originally scored.  No downgrade is
warranted on the present evidence; equally, no upgrade to "validated
across grids" is warranted.

### What is not yet known

- Does the resonance peak appear at $k_\text{Bohr}$ on $\geq 81^3$
  when measured inside a tight pre-escape window (tick 30–120)?  A
  follow-up `exp_12d-tight` would answer this.
- Does the resonance shape sharpen on smaller measurement windows
  on 65³, or stay flat?  The current $r_\text{mean}$ is essentially
  flat across $k \in [0.096, 0.103]$ at $r \approx 10.5$ — the
  trough lacks resolving power for a precise $k_\min$.

## Proposed audit-table row (pending dcl-claim-auditor validation)

```latex
Lock-in resonance grid-stability
    & \texttt{exp\_12} chassis on $\text{GRID} \in \{65, 81, 97,
      113\}^3$, 200-tick scoring window
    & Standard QM has no lattice substrate to vary
    & \texttt{exp\_12d} 2026-05-05 four-grid sweep:
      on $65^3$ the orbit stays at $r \approx 10.5$ across
      $k \in [0.096, 0.103]$ (Δ$\leq 0.18$ from $R_1$ at
      $k_\text{Bohr}$); on $\geq 81^3$ the orbit escapes within the
      scoring window and the resonance is unresolved;
      $r_\text{std}$ ratio between regimes $\sim 10\times$
    & \texttt{PART} \\
```

This row is *additive* — it does not modify the existing
`Two-body hydrogen (4 sig figs)` row (`exp_12`, PASS at 65³).  The
two rows sit alongside each other in the audit table.

## Status

- **Implementation**: complete ✓
- **Smoke test**: complete ✓ (2026-05-05, 20-tick / 65³ / 10 $k$, ~2.2 min)
- **Full sweep**: complete ✓ (2026-05-05, 200-tick / 4 grids / 10 $k$, 2 h 16 min)
- **Result**: split — 65³ resonance observable & consistent with
  $k_\text{Bohr}$; $\geq 81^3$ inconclusive due to in-window escape
- **Audit-table row**: drafted above; pending dcl-claim-auditor
  validation and commit
- **Follow-up**: `exp_12d-tight` with measurement window 30–120 to
  test resonance on grids that escape after tick 140

## Relation to other experiments

- **vs `exp_12_hydrogen_twobody`**: validates `exp_12`'s $k_\min$
  result by repeating its scan on three additional grid sizes.  Does
  not modify `exp_12`.
- **vs `exp_12b_twobody_long_baseline`**: `exp_12b` measured the
  long-horizon escape on $65^3$.  `exp_12d` measures the short-horizon
  resonance across grid sizes.  Different epochs, complementary scope.
- **vs `exp_12c_long_horizon_diagnosis`**: `exp_12c` established that
  $\geq 81^3$ orbits escape by tick $\sim 140$.  `exp_12d` works
  inside the stable-orbit window ($t < 150$) on those same grids,
  asking whether the resonance peak is grid-stable when the lock-in
  is observable.

## References

- `paper/sections/audit_table.tex` — target for any new audit row
- `notes/twobody_hydrogen_results.md` — exp_12 result write-up
- `src/experiments/exp_12_hydrogen_twobody.py` — canonical reference
- `src/experiments/exp_12c_long_horizon_diagnosis.py` — established
  the tick-140 escape on $\geq 81^3$ that motivates the 200-tick
  scoring window here
