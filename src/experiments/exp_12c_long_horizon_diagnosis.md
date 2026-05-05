<!-- markdownlint-disable MD022 MD024 MD032 MD047 MD060 -->
# exp_12c_long_horizon_diagnosis.py

Diagnose the source of the long-horizon two-body escape exposed by
`exp_12b`.

## The question

`exp_12b` showed the bare `exp_12` setup escaping from $r_\text{peak}
\sim R_1$ to grid edge by tick $\sim 2000$ over a 6000-tick horizon
at $\text{GRID}=65^3$.  The escape is *not* caused by the emission
operator (`exp_20` arms A/B/C all inherit it).  The v0.98-RC
conclusion's *What remains open* subsection (item 5) names three
candidate causes:

1. **Grid-size dependence.** The 65³ box may be too small; escape
   is a finite-volume artefact.
2. **CoM-frame initial-condition residual.** Discrete-grid placement
   may leave $\langle\mathbf{p}\rangle_\text{joint} \ne 0$, which
   compounds over 6000 ticks.
3. **Bipartite tick rule's near-unitary drift.** Cumulative
   $O(a^2)$ error in the kinetic+residence step may produce
   systematic outward drift even with `tick(normalize=True)`.

## The design

Three sub-modes under one script:

| Mode | What it varies | What it tests |
|---|---|---|
| `grid` | grid size $\in \{65, 81, 97, 113\}$ at fixed init | cause 1: does escape time scale with grid size? |
| `init` | initial-condition treatment at fixed grid | cause 2: does zeroing the residual joint momentum eliminate escape? |
| `drift` | single instrumented run logging per-tick amplitude + CoM drift | cause 3: is there a systematic outward bias in the tick rule? |

### Initial-condition variants (mode `init`)

- **`baseline`**: verbatim `exp_12b` initialisation. Reference.
- **`zero_p_subtracted`**: baseline init followed by a uniform phase
  ramp on both sessions to numerically cancel the residual joint
  momentum. Approach: compute
  $\mathbf{p}_\text{residual} = \langle\mathbf{p}_e\rangle + \langle\mathbf{p}_p\rangle$,
  apply $\exp(-i\,\mathbf{p}_\text{residual}/2 \cdot \mathbf{x})$
  to each session. Caveat: only cancels the gradient-expectation
  term; sub-leading effects (envelope-dominated) may survive.
- **`sym_pair`**: symmetric pair init with both wave packets
  carrying $|k| = 1/R_1$ in *opposite signs* along the same V₂
  direction, weighted by unit amplitude per session. Joint momentum
  is zero by construction (modulo finite-grid sampling). Differs
  from baseline in that the proton's $|k|$ is set equal to the
  electron's rather than scaled by $M_E/M_P$.

### Per-tick drift instrumentation (mode `drift`)

Logs a structured array indexed by tick with fields:

- `dA_e`, `dA_p`: change in session amplitude across the tick
- `dx_e`, `dy_e`, `dz_e`: electron CoM displacement across the tick

A *systematic* nonzero mean in the `dx_e`/`dy_e`/`dz_e` series
indicates cause 3 (the tick rule pushes outward by a fixed amount
each tick).  A *zero-mean fluctuating* series rules cause 3 out.

## Predicted falsification matrix

| Outcome | Lead cause | Next move |
|---|---|---|
| Escape tick scales with grid size (e.g., $\propto L^2$ or $\propto L$) | (1) Finite-volume artefact | Re-run all dynamic experiments at a larger grid; reconsider whether 65³ is sufficient anywhere in the paper. |
| Escape tick is grid-independent **and** `zero_p_subtracted` or `sym_pair` eliminates escape | (2) CoM residual | Fix the `make_sessions` initialisation in `exp_12`/`exp_12b`/`exp_19c`/`exp_20` to subtract the residual at init time. Audit-table evidence rows for affected experiments get refreshed. |
| Escape tick is grid-independent **and** all init variants escape **and** drift log shows systematic CoM drift | (3) Tick rule bias | Investigate the `_kinetic_hop` + residence step for an asymmetry between RGB and CMY hops; possibly fix or document. Largest impact on the framework's claims. |
| All three checks come back null | More fundamental | Either the bare two-body system is intrinsically metastable (paper-worthy finding), or there's a fourth cause we haven't enumerated. |

## Smoke-test results (2026-05-04, GRID=65³ where applicable, 20 ticks)

| Mode | Variant | r_peak | A_drift_max | p_joint_initial (V₂ component) |
|---|---|---|---|---|
| `grid` | 65 | 9.877 | 4.4e-16 | 0.085 |
| `init` | `zero_p_subtracted` | 12.221 | 2.2e-16 | 0.036 (~58% reduction from baseline) |
| `drift` | `baseline` | 9.877 | 4.4e-16 | 0.085 (matches grid 65) |

**Already visible at smoke-test scale**: the baseline init carries
substantial residual joint momentum along V₂ ≈ (1, -1, -1). This is
*supporting evidence* (not yet confirmation) for cause 2. The
`zero_p_subtracted` variant reduces but does not zero the residual
— the gradient-expectation cancellation is incomplete because the
proton's tight envelope (WIDTH_P=0.5 vs WIDTH_E=1.5) makes its
gradient dominated by envelope falloff rather than phase ramp. The
`sym_pair` variant is designed to be exactly zero by construction.

The drift log saves correctly as a structured numpy array of length
TICKS_TOTAL (verified on smoke test at 20 ticks).

## Running the experiment

### Smoke test (~14 s per worker)

```bash
EXP12C_TICKS=20 python src/experiments/exp_12c_long_horizon_diagnosis.py grid 65
EXP12C_TICKS=20 python src/experiments/exp_12c_long_horizon_diagnosis.py init zero_p_subtracted
EXP12C_TICKS=20 python src/experiments/exp_12c_long_horizon_diagnosis.py drift baseline
```

### Full grid sweep (~7.6 h wall-clock, 4 parallel workers)

```bash
EXP12C_TICKS=6000 python src/experiments/exp_12c_long_horizon_diagnosis.py grid
```

Spawns one worker per grid size in `GRID_VARIANTS = [65, 81, 97, 113]`.
Per-tick cost scales as $N^3$, so the 113³ worker dominates wall-clock:

| Grid | Cells | Est. wall-clock at 6000 ticks |
|---|---:|---:|
| 65³ | 275 k | ~87 min |
| 81³ | 531 k | ~170 min |
| 97³ | 913 k | ~290 min |
| 113³ | 1.44 M | ~460 min |

### Full initial-condition variant (~90 min wall-clock, 3 parallel workers)

```bash
EXP12C_TICKS=6000 python src/experiments/exp_12c_long_horizon_diagnosis.py init
```

Three parallel workers at 65³, one per variant.

### Full drift diagnostic (~100 min, single instrumented run)

```bash
EXP12C_TICKS=6000 python src/experiments/exp_12c_long_horizon_diagnosis.py drift
```

Slightly slower than baseline due to per-tick CoM and amplitude
computation. Saves both the standard summary npy and a separate
drift-log npy.

## Output files

For each `(mode, variant)` combination:

- `data/exp_12c_<mode>_<variant>.log` — per-window progress log
- `data/exp_12c_<mode>_<variant>.npy` — summary array
  `[grid, ord(init[0]), settled, max_streak, T_settle, amp_e, amp_p, A_drift_max, r_peak_min, r_peak_max, escape_tick]`
- For drift mode only:
  `data/exp_12c_<mode>_<variant>_drift.npy` — structured array,
  shape `(TICKS_TOTAL,)`, dtype
  `[('tick', 'i4'), ('dA_e', 'f8'), ('dA_p', 'f8'),
  ('dx_e', 'f8'), ('dy_e', 'f8'), ('dz_e', 'f8')]`

## Implementation

`src/experiments/exp_12c_long_horizon_diagnosis.py` — self-contained,
no modifications to `exp_12`, `exp_12b`, `exp_19c`, or `exp_20`.
Three init functions and three modes; reuses no machinery from
`exp_12b` to keep that experiment unchanged. Run via parallel
launcher (one mode at a time) or single-worker mode for targeted
re-runs.

## Status

- **Implementation**: complete, smoke-tested ✓
- **Full grid sweep**: pending
- **Full init variant**: pending
- **Full drift diagnostic**: pending (run after grid + init)
- **Audit-table impact**: depends on outcome. If cause 2 is
  confirmed, the existing `Two-body long-horizon stability` row
  (`exp_12b`, `PART`) gets refined or moved toward `PASS`. If
  cause 1 is the lead, the row's wording shifts to "finite-volume
  artefact".  If cause 3, broader implications for all dynamic
  experiments.

## References

- `notes/exp_20_emission_operator_and_clock_fluid.md` — names the
  three candidate causes
- `paper/sections/conclusion.tex` *What remains open* item 5 —
  cites this experiment as the next move
- `src/experiments/exp_12b_twobody_long_baseline.py` — the
  experiment whose result motivated this diagnosis
