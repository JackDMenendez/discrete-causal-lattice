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

## Full-run results (2026-05-04 to 2026-05-05, 6000 ticks per worker)

### Mode `init` (3 workers at 65³, ~3.1 h wall-clock)

| Variant | $r_\text{peak,min}$ | $r_\text{peak,max}$ | escape_tick | max_streak |
|---|---|---|---|---|
| `baseline` | 9.161 | 83.336 | 1919 | 5 |
| `zero_p_subtracted` | 7.979 | 78.833 | 299 | 5 |
| `sym_pair` | 7.428 | 77.813 | 1879 | 3 |

**Cause 2 (CoM-frame initial-condition residual) is ruled out.**
`baseline` and `sym_pair` (which has joint $\langle\mathbf{p}\rangle = 0$
by construction) escape at very similar times, so the escape is
intrinsic to the dynamics rather than driven by an
initial-condition residual.

The `zero_p_subtracted` variant escapes much earlier (tick 299) —
the uniform phase ramp applied to cancel the residual joint
momentum *destabilised* the orbit instead of fixing it.  Negative
result, but informative: it tells us the baseline init is more
delicately tuned than it looks, and arbitrary CoM-frame "fixes"
can make things worse.

### Mode `drift` (single instrumented worker at 65³, ~3.3 h wall-clock)

| Quantity | Value |
|---|---|
| Mean per-tick CoM drift (each component) | $+1$–$3 \times 10^{-3}$ nodes |
| Std per-tick CoM drift (each component) | $\sim 0.5$ nodes |
| Cumulative mean drift over 6000 ticks | $(+17.0, +7.0, +15.6)$ ≈ 24 nodes magnitude |
| Random-walk std after 6000 ticks (each component) | $\sqrt{6000} \times 0.5 \approx 39$ nodes |
| Mean per-tick amplitude drift, electron | $+1.9 \times 10^{-20}$ |
| Std per-tick amplitude drift, electron | $2.9 \times 10^{-16}$ (machine precision) |

**Cause 3 (systematic tick-rule outward bias) is NOT confirmed in
its strongest form.**  The per-tick mean drift is ~250× smaller
than the per-tick std — the CoM motion is dominated by stochastic
fluctuation.  There is a small systematic bias of order
$10^{-3}$ nodes/tick, but it does not dominate the dynamics.

Amplitude conservation is exact at machine precision.
`tick(normalize=True)` is doing its job perfectly.

### Mode `grid` (4 workers, ~8.3 h wall-clock; the 113³ worker dominates)

| Grid | $r_\text{peak}$ at tick 19 | escape_tick | $r_\text{peak}$ at tick 2019 | $r_\text{peak,max}$ |
|---|---|---|---|---|
| 65³  | 9.877  | **1919** | 72.1  | 83.3  |
| 81³  | 10.368 | **159**  | 68.6  | 96.5  |
| 97³  | 10.208 | **139**  | 61.5  | 115.7 |
| 113³ | 10.524 | **139**  | 63.9  | 141.6 |

**Cause 1 confirmed — but in the OPPOSITE direction from prediction.**
Larger grids escape *faster*, not slower.  All four grids start
with $r_\text{peak}$ near $R_1 \approx 10$ at tick 19.  The 65³
orbit holds for ~1900 ticks; the 81³ and larger orbits cross the
$r_\text{peak} > 30$ threshold within ~140 ticks.

This inverts the diagnosis given in `exp_12b`'s writeup.  The
correct interpretation is:

> *The 65³ "stable for ~2000 ticks" result was a finite-volume
> stabilisation artefact.  Whatever boundary conditions the
> bipartite octahedral lattice uses, they reflect or wrap outgoing
> flow back into the well, holding the wave packet's $r_\text{peak}$
> near $R_1$ on the small grid.  Once the box is large enough
> ($\ge 81^3$) for the boundary effects to stop reaching the orbit
> centre, the true bare-two-body orbital lifetime emerges:*
> ***~140 ticks***, *not ~2000 ticks.*

The dephasing is unitary throughout — $\mathcal{A}=1$ preserved
at machine precision (~$10^{-15}$) on all grids.

## Implications

1. **The bare two-body Bohr orbit on the bipartite lattice is
   short-lived in the chosen calibration window** (~140 ticks at
   $\ge 81^3$).  The framework's bound-state mechanism is real
   (the wave packet does sit near $R_1$ for that window), but
   the orbital lifetime is much shorter than `exp_12b` made it
   appear.

2. **`exp_12`'s 4-sig-fig PASS for $k_\text{min}$ is now suspect
   for grid-independence.**  `exp_12` runs at GRID=65³ and
   reports $k_\text{min} = 0.0970$ vs $k_\text{Bohr} = 0.0971$.  If
   the apparent resonance is itself partially a confinement effect,
   the same scan at 113³ might give a different $k_\text{min}$.
   This is the most important follow-up question — it touches the
   audit table's headline `Two-body hydrogen (4 sig figs)` PASS row.
   `exp_12d` is queued to test this directly.

3. **`exp_10`/`exp_11` may be similarly affected.**  Both run at
   65³ with fixed Coulomb wells.  Single-session experiments don't
   have proton recoil, but they do have boundaries.

4. **Emission and recoil claims are not directly threatened.**
   `exp_20` confirmed joint $\mathcal{A}=1$ at machine precision;
   that is a structural conservation, not an orbital-stability
   claim.  The orbital-settling question that was already open
   (audit-table row `Photon emission as A=1 necessity`, `PART`)
   stays open in roughly the same shape.

5. **The audit-table entry `Two-body long-horizon stability`
   (PART, `exp_12b`)** should be re-characterised in a v1.0 cycle:

   > *exp_12b's tick ~2000 escape on 65³ is a finite-volume
   > stabilisation artefact.  Bare two-body orbital lifetime is
   > ~140 ticks on grids $\ge 81^3$ at the chosen calibration.
   > Dephasing is unitary; A=1 preserved at machine precision.
   > The framework's lock-in mechanism may itself be
   > grid-dependent (exp_12d, queued).*

## Status

- **Implementation**: complete ✓
- **Full grid sweep**: complete ✓ (2026-05-05)
- **Full init variant**: complete ✓ (2026-05-04)
- **Full drift diagnostic**: complete ✓ (2026-05-04)
- **Diagnosis**: cause 2 ruled out; cause 3 not confirmed in its
  strongest form; cause 1 confirmed but inverted (small grid
  stabilises rather than destabilises).
- **Audit-table impact**: re-characterise the
  `Two-body long-horizon stability` row in a v1.0 cycle as above.
- **Next experimental step**: `exp_12d` to test whether `exp_12`'s
  $k_\text{min}$ resonance is grid-independent.

## References

- `notes/exp_20_emission_operator_and_clock_fluid.md` — names the
  three candidate causes
- `paper/sections/conclusion.tex` *What remains open* item 5 —
  cites this experiment as the next move
- `src/experiments/exp_12b_twobody_long_baseline.py` — the
  experiment whose result motivated this diagnosis
