<!-- markdownlint-disable MD022 MD024 MD032 MD047 MD060 -->
# exp_12d_tight_grid_independence_k_scan.py

Validate `exp_12`'s $k$-scan resonance result inside the pre-escape
stable phase on every grid.

## Why this experiment exists

`exp_12d` (2026-05-05) ran the same scan with measurement window
tick 50–199 and got a **split outcome**:

- On $65^3$, the resonance was observable and consistent with
  $k_\text{Bohr} = 0.0971$: $r \approx 10.5$ across $k \in [0.096,
  0.103]$, $r_\text{std}$ in $[1, 2]$.
- On $\geq 81^3$, every $k$ value gave $r_\text{mean} \in [16, 35]$
  with $r_\text{std} \in [8, 23]$.  The orbit had escaped on every
  trial.

The cause is methodological.  `exp_12c` established that on grids
$\geq 81^3$ the orbit escapes around tick 140.  The `exp_12d`
measurement window (tick 50–199) extended 60+ ticks past that escape
onset, so $r_\text{mean}$ on those grids averaged predominantly
post-escape positions.  The resonance signature, if any, was buried
in the post-escape noise.

`exp_12d_tight` re-runs the same scan with a measurement window
**tick 30–119**, comfortably inside the tick-140 escape onset on
$\geq 81^3$.  This is the only methodological change.

## The question

When the measurement window is restricted to the pre-escape stable
phase, does the lock-in resonance appear at $k_\text{Bohr}$ on every
grid?

If yes, the resonance is grid-independent and `exp_12`'s PASS at 4
sig figs survives at $\geq 81^3$ on the proxy
$|r_\text{peak} - R_1|$.  If no, the resonance shifts with grid size
and the lock-in is partly a confinement effect.

## Design

Identical to `exp_12d` (live proton + electron, mean-field Coulomb,
alternating tick order, $\omega_e = 0.1019$, $\omega_p = \pi/2$,
STRENGTH=30, $R_1 = 10.3$) except:

- Run length: $\text{TICKS\_TOTAL} = 120$ (was 200).
- Burn-in: $\text{BURN\_IN} = 30$ (was 50).
- Measurement window: ticks 30–119 (was 50–199).
- All other parameters identical, including the $k$ values and grid
  sizes.

```python
K_VALUES = [0.085, 0.090, 0.092, 0.094, 0.096, 0.0971,
            0.099, 0.101, 0.103, 0.106]
GRID_VARIANTS = [65, 81, 97, 113]
```

The window 30–119 captures ~90 samples per trial (one every
$\text{CHECK\_EVERY}=10$ ticks).  It stops well before the tick-140
escape onset on $\geq 81^3$ and well within the long-stable phase
on $65^3$ (where exp_12c saw stability for ~2000 ticks).

Score: time-averaged $r_\text{peak}$.  $k_\min$ is the $k$ value
minimising $|r_\text{peak} - R_1|$.

## Predicted falsification matrix

| Outcome | Lead interpretation | Next move |
|---|---|---|
| $k_\min$ on all four grids stays within $\pm 0.002$ of $k_\text{Bohr}$ and $r$ at $k_\min$ within $\pm 0.5$ of $R_1$ | Lock-in is grid-independent; `exp_12`'s 4-sig-fig PASS survives at $\geq 81^3$ on this proxy | Promote `exp_12d_tight` row to PART (independent grid validation) in audit table |
| $k_\min$ stays near $k_\text{Bohr}$ on small grids but drifts on $\geq 97^3$ | Confinement-dependent peak; lock-in real but distorted | Add finite-size-extrapolation note to `exp_12`'s row |
| $k_\min$ scatters with no consistent trend, even within the pre-escape window | Resonance is itself a confinement artefact | Downgrade `exp_12`'s row from PASS to PART |
| Some grids still show $r_\text{std} > 5$ inside the tight window | Stable phase is shorter than 140 ticks; even tighter window needed | Re-run with window tick 30–80 or analyse per-tick $r_\text{peak}$ trace |

## Running

### Smoke test (~14 min on 65³)

```bash
EXP12DT_TICKS=20 EXP12DT_BURN=5 python src/experiments/exp_12d_tight_grid_independence_k_scan.py 65
```

Single grid, full $k$ scan, very short trials.  Confirms wiring.
Same per-tick cost as exp_12d (~0.65 s on 65³), so 10 k × 20 ticks
= ~130 s.

### Full sweep (~1 h 22 min wall clock parallel)

```bash
python src/experiments/exp_12d_tight_grid_independence_k_scan.py
```

Per-grid wall-clock estimate at $\text{TICKS\_TOTAL} = 120$ (scaling
0.6× from `exp_12d`'s measured 200-tick run):

| Grid | Per-$k$ cost | 10-$k$ scan |
|---|---|---|
| $65^3$  | $\sim 80$ s  | $\sim 13$ min |
| $81^3$  | $\sim 150$ s | $\sim 25$ min |
| $97^3$  | $\sim 260$ s | $\sim 43$ min |
| $113^3$ | $\sim 410$ s | $\sim 68$ min |

Parallel max wall clock $\approx 1$ h 22 min on a 4-core machine.

## Output files

For each grid in $\{65, 81, 97, 113\}$:

- `data/exp_12d_tight_grid_<G>.log`
- `data/exp_12d_tight_grid_<G>.npy`
- `data/exp_12d_tight_grid_<G>.err`

The launcher prints a four-row summary table at the end (same format
as exp_12d).

## Status

- **Implementation**: complete ✓
- **Smoke test**: skipped (uses identical run-loop and helpers as
  `exp_12d`, which is already smoke-tested)
- **Full sweep**: pending
- **Audit-table row**: deferred until results are in

## Relation to other experiments

- **vs `exp_12_hydrogen_twobody`**: validates `exp_12`'s $k_\min$
  result on a tight pre-escape window across grid sizes.  Does not
  modify `exp_12`.
- **vs `exp_12d`**: same chassis and $k$ scan, shorter measurement
  window (30–119 vs 50–199) to stay inside the pre-escape stable
  phase on $\geq 81^3$.
- **vs `exp_12c`**: uses `exp_12c`'s tick-140 escape onset finding
  to motivate the tight window.

## References

- `src/experiments/exp_12d_grid_independence_k_scan.md` — the
  long-window predecessor whose split outcome motivates this
- `src/experiments/exp_12c_long_horizon_diagnosis.md` — established
  the tick-140 escape onset on $\geq 81^3$
- `paper/sections/audit_table.tex` — target for any new audit row
