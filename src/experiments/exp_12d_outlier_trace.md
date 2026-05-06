<!-- markdownlint-disable MD022 MD024 MD032 MD047 MD060 -->
# exp_12d_outlier_trace.py

Trace the $r(t)$ evolution at the two `exp_12d_tight` outliers to
determine whether they are tail noise or a secondary instability.

## Why this experiment exists

`exp_12d_tight` (2026-05-05) ran a four-grid $k$-scan on a tight
pre-escape window (tick 30-119) and found two outliers among 40
trials:

- 81³ at $k = 0.101$: $r_\text{mean} = 15.88$, $r_\text{std} = 9.26$
- 113³ at $k = 0.101$: $r_\text{mean} = 15.76$, $r_\text{std} = 9.43$

Every other configuration had $r_\text{std} \in [1.1, 2.9]$.  The
proposed `exp_12d_tight` audit row claims the lock-in resonance is
grid-independent; the meaning of these two outliers determines
whether the claim is clean or noisy.

Two hypotheses, with different implications for the audit row:

- **Tail noise.**  The orbit briefly excursed outward then returned
  to $r \approx R_1$.  The std of $\sim 9$ reflects excursion height;
  the configurations are still locked, just rough.  Audit row stays
  clean.
- **Secondary instability.**  The orbit lost lock and walked outward.
  The std reflects the rate of escape.  Audit row needs a caveat
  about $k = 0.101$ being a special unstable point.

A time-averaged $r_\text{mean}$ with $\text{std} \sim 9$ doesn't
distinguish them.  Only the full $r(t)$ trace does.

## Design

Identical run-loop and helpers to `exp_12d_tight`, parameterised by
$(\text{grid}, k)$.  Records $r_\text{peak}$ at every $\text{CHECK\_EVERY} = 10$
ticks from $t = 0$ to $t = 199$ (extending past `exp_12d_tight`'s
tick-119 boundary).

Two configurations run in parallel:

```python
CONFIGS = [(81, 0.101), (113, 0.101)]
TICKS_TOTAL = 200
```

## Running

```bash
python src/experiments/exp_12d_outlier_trace.py
```

Wall clock: 720 s ≈ 12 min on a 4-core machine (113³ is the long
pole at 699 s; 81³ finished at 299 s).

## Results (2026-05-05)

### 81³ at $k = 0.101$

| tick | $r_\text{peak}$ | tick | $r_\text{peak}$ |
|---:|---:|---:|---:|
|   9 | 10.293 | 109 |  9.797 |
|  19 | 12.383 | **119** | **41.571** |
|  29 | 17.675 | 129 | 40.825 |
|  39 | 14.149 | 139 | 42.928 |
|  49 | 15.030 | 149 | 40.595 |
|  59 | 15.240 | 159 | 40.834 |
|  69 | 13.076 | 169 | 40.111 |
|  79 | 12.043 | 179 | 41.548 |
|  89 | 10.974 | 189 | 41.473 |
|  99 | 11.017 | 199 | 43.560 |

Three regimes:

- ticks 9-29: initial settling.  $r$ rises from 10.3 to 17.7 (overshoot).
- ticks 39-109: orbital oscillation.  $r$ in $[9.8, 15.2]$, slowly
  decaying back toward $R_1$.  At tick 109, $r = 9.80$ — within 5%
  of $R_1 = 10.3$.
- ticks 119-199: **escape**.  $r$ jumps to 41.6 at tick 119 and stays
  there.  Box-bounded at $r \sim 41$ (the 81³ grid boundary is at
  $\sim 40.5$ from centre).

### 113³ at $k = 0.101$

| tick | $r_\text{peak}$ | tick | $r_\text{peak}$ |
|---:|---:|---:|---:|
|   9 | 10.552 | 109 |  9.393 |
|  19 | 11.966 | **119** | **41.428** |
|  29 | 17.388 | 129 | 40.706 |
|  39 | 16.120 | 139 | 43.883 |
|  49 | 17.584 | 149 | 47.477 |
|  59 | 12.275 | 159 | 51.488 |
|  69 | 12.237 | 169 | 54.354 |
|  79 | 12.352 | 179 | 57.982 |
|  89 | 10.966 | 189 | 58.871 |
|  99 |  9.515 | 199 | 61.108 |

Same three regimes, but with the larger box the escape is not
box-bounded:

- ticks 9-29: settling, overshoot to $r = 17.4$.
- ticks 39-109: orbital oscillation.  $r$ in $[9.4, 17.6]$.  At tick
  109, $r = 9.39$ — within 9% of $R_1$.
- ticks 119-199: **escape, monotonic outward walk**.  $r$ jumps to
  41.4 at tick 119, then walks outward: $r$ at the last 5 windows
  averages 56.8, with $r = 61.1$ at the final tick (still growing).
  The 113³ grid supports $r$ up to $\sim 56.5$ from centre, so
  $r = 61$ is hitting boundary effects.

### Reading the result

Both traces show the same structure: settled orbital phase ($r$
oscillating around $R_1$) followed by an abrupt escape at tick 119.
The escape is **not a smooth drift** — it's a discrete jump from
$r \approx 10$ to $r \approx 41$ within one $\text{CHECK\_EVERY} = 10$
tick window.

This rules out the tail-noise hypothesis.  The orbit *does* escape
at $k = 0.101$ on these grids; the high $r_\text{std}$ in
`exp_12d_tight` was driven by the escape jump, not by a wider
oscillation amplitude.

It also rules out the secondary-instability hypothesis in its strong
form.  The escape mechanism is *not* a $k = 0.101$ resonance with
the lattice — the trace shape is identical to the generic late-time
escape that `exp_12c` documented (settled orbit, then sudden escape
to grid boundary).  The only special thing about $k = 0.101$ on
81/113³ is the *timing*: escape onset at tick 119 rather than the
$\sim 140$ that `exp_12c` measured for other configurations.

The right reading: the **escape-onset distribution has spread**.  On
$\geq 81^3$, the bare two-body orbit becomes metastable around
$\text{tick}_\text{escape} \in [\sim 110, \sim 140]$ depending on
(grid, $k$) configuration.  `exp_12c`'s $\sim 140$ estimate was the
typical value, not a strict lower bound.  The two outliers in
`exp_12d_tight` simply caught the early tail of this distribution
within the tick-30-119 measurement window.

### Implication for `exp_12d_tight`'s audit row

**Strengthened.**  The two outliers are now characterised: they are
the early-escape tail of the same generic metastable-orbit phenomenon,
not a resonance-shape feature at $k = 0.101$.  The lock-in
attractor's grid-independence (clean across the other 38 of 40
configurations) is undisturbed by the outliers; they tell us about
escape-onset variance, which is a separate fact.

The audit row's evidence column is updated to make this explicit (see
`exp_12d_tight.md`).  No change to the row's status (`PART`).

### Implication for `exp_12c`'s tick-140 finding

**Refined.**  `exp_12c` reported escape at tick $\sim 140$ on
$\geq 81^3$.  The two outlier traces show that the escape *onset* is
sometimes earlier (tick 119 here).  The exp_12c claim should be read
as "metastable, with escape onset typically around tick 140 but
ranging at least down to tick 110 in some (grid, $k$) configurations."

This is a small footnote in `exp_12c.md`'s grid-mode section, not a
substantive revision of its findings.

## Status

- **Implementation**: complete ✓
- **Run**: complete ✓ (2026-05-05, 12 min wall clock)
- **Result**: outliers are early-escape tail of `exp_12c`'s
  metastable-orbit mechanism, not tail noise and not a $k = 0.101$
  secondary instability
- **Audit-table consequence**: `exp_12d_tight`'s proposed PART row is
  cleaner, not weaker; the row's evidence column should mention
  "outliers traced to early-escape tail of metastable orbit, see
  `exp_12d_outlier_trace`"

## Relation to other experiments

- **vs `exp_12d_tight`**: this experiment characterises the two
  outliers of `exp_12d_tight`'s 40-trial sweep.
- **vs `exp_12c`**: refines `exp_12c`'s tick-140 escape estimate.
  The mechanism is the same; the onset has spread.

## References

- `src/experiments/exp_12d_tight_grid_independence_k_scan.md` — the
  parent experiment whose two outliers this traces
- `src/experiments/exp_12c_long_horizon_diagnosis.md` — established
  the metastable-orbit / late-time escape mechanism on $\geq 81^3$
- `data/exp_12d_outlier_trace_81_k0.1010.{npy,log}`,
  `data/exp_12d_outlier_trace_113_k0.1010.{npy,log}` — full traces
