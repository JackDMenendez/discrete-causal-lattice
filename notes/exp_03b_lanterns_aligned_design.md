# exp_03b: Lattice-Aligned Double-Slit (Design Note)

*Date: 2026-04-25*
*Status: **ABANDONED** (2026-04-26) -- design fails for thin z-grids; see
postmortem at the end.  The original axis-aligned `exp_03_lanterns` is
preferred.*

---

## Motivation

`exp_03_lanterns` (the current Huygens-lantern figure) places the slits
along the y-axis and propagates "forward" along +x, with the screen at
x = 40. On the bipartite $\mathcal{T}_\diamond^3$ lattice this fights
the geometry: the only allowed propagation directions per tick are the
six body-diagonal basis vectors $\mathbf{V}_1=(1,1,1)$,
$\mathbf{V}_2=(1,-1,-1)$, $\mathbf{V}_3=(-1,1,-1)$ and their CMY
negatives. Projected to the xy-plane these go at 45° to the +x axis,
so the wavefronts in the published figure travel diagonally and
slit B's beam exits the bottom of the frame before reaching the screen.

This is genuine lattice physics — not a bug — but it makes the figure a
poor advertisement for double-slit interference. The continuum
spherical Huygens wavefront is recovered only at $N \gg$ slit-separation,
not at the $N=55$ tick / 32-node propagation depth that the figure shows.

## Design

Rotate the entire experimental frame 45° counterclockwise so the "forward"
direction is along the *projected* body-diagonal:

- **Forward axis:** $\hat{\mathbf{n}}_\parallel = (\hat{\mathbf{x}} + \hat{\mathbf{y}})/\sqrt{2}$
  — this is $\mathbf{V}_1$ projected to xy-plane.
- **Slit-line axis:** $\hat{\mathbf{n}}_\perp = (\hat{\mathbf{x}} - \hat{\mathbf{y}})/\sqrt{2}$,
  perpendicular to forward in the xy-plane.
- **Slits:** point sources at $\pm (s/2)\,\hat{\mathbf{n}}_\perp$ from the
  origin, where $s$ is slit separation in lattice nodes.
- **Screen:** plane perpendicular to $\hat{\mathbf{n}}_\parallel$ at
  signed distance $L$ — i.e., the xy-line $x + y = L\sqrt{2}$.

## Why this is cleaner

- From each slit, the dominant amplitude propagates along $\mathbf{V}_1$
  (RGB tick) or $-\mathbf{V}_1$ (CMY tick) → projects to
  $\pm\hat{\mathbf{n}}_\parallel$ → directly *toward* (or away from)
  the screen. Neither slit's beam exits the frame perpendicular to
  the experimental axis.
- Path-length differences between the two slits to a screen point fall
  along basis-vector directions and resolve to integer-tick differences
  → clean Bragg-like fringe spacing without the
  half-wavelength-fits-in-a-zigzag-step pathology.
- The lattice anisotropy still shows up at small $N$, but it is
  **aligned with** the experimental axis rather than orthogonal to it,
  so the visible features in the figure correspond to the physics being
  measured.

## Implementation sketch

Roughly:

```python
# Coordinates in 3D lattice: (x, y, z); experiment runs in z = z0 slice.
# Slit positions:
n_perp = np.array([1, -1, 0]) / np.sqrt(2)
slit_A = origin + (s/2) * n_perp     # rounded to nearest lattice node
slit_B = origin - (s/2) * n_perp
# Screen plane: x + y = L * sqrt(2), i.e. nodes whose dot with n_par equals L.
n_par  = np.array([1, 1, 0]) / np.sqrt(2)
screen_nodes = [n for n in slice_nodes if abs(n @ n_par - L) < 0.5]
```

Two coherent point-source CausalSessions registered at slit_A and
slit_B, then run for $N$ ticks; record $|\psi_R|^2 + |\psi_L|^2$ on
the screen line at the final tick. Decoherent variant: add a detector
session at slit_A that scrambles the local phase each tick (same as
exp_03's centre panel).

## Suggested run parameters

To actually approach the continuum-Huygens regime:

- $s$ = 80 nodes (slit separation; 3-4× the current 24)
- $L$ = 200 nodes along $\hat{\mathbf{n}}_\parallel$ (propagation; 6× the current 32)
- $N$ = 300 ticks (to let wavefronts homogenise; 5-6× the current 55)
- $\omega = 0.15$ unchanged

Approx grid size: needs to span at least $L\sqrt{2} \approx 280$ along
both x and y, so a $300^3$ grid. ~30M nodes. At ~1ms per kinetic hop on
a single-CPU run that's ~30 minutes per tick, ~150 hours for 300 ticks.
**Too slow without optimisation** — this run wants either:
- A 2D-only variant (fix z = z0 with a 2D restriction of the tick rule), or
- numba-jitted `_kinetic_hop` (the optimisation already noted in
  `CLAUDE.md` for exp_19 v5).

A 2D-only variant is probably the right move first — confirm the
geometry produces the expected fringes at modest cost, then port to 3D
if the headline figure warrants it.

## Output

- `figures/exp_03b_lanterns_aligned.pdf` — replaces (or accompanies) the
  current `exp_03_lanterns` figure on §10.3 / §10.4.
- Caption can drop the "Note on geometry" paragraph that the
  current figure needed; the aligned setup is self-explanatory.

## Related

- `paper/sections/interference.tex` — currently uses `exp_03_lanterns`
  with a caption acknowledging the geometric mismatch.
- `paper/sections/octahedral_substrate.tex` — the new "Two lengths, one
  convention" paragraph (2026-04-25) makes the body-diagonal hop
  distance explicit; this experiment is the natural visual counterpart.

---

## Postmortem (2026-04-26): why this design fails

The script was implemented and run at three parameter settings (--quick,
default, and --slits 50 --propagation 80 --ticks 150 --omega 0.40).
In every case the **dominant amplitude stays in the slit-line region
(±n_perp), not propagating toward the screen along +n_par**.  The screen
profile panel comes back essentially flat: the wavefront does not reach
the screen with usable amplitude on a thin z-grid.

The design analysis was 2D-only and missed a coupling to the z-axis.

### The 2-tick pairing analysis

Each macro-tick pair (RGB tick along V_i, then CMY tick along -V_j)
produces a net displacement V_i - V_j.  Sorted by xy/z behaviour:

| Pair                 | Net displacement | xy projection (magnitude)       | z drift |
|----------------------|------------------|---------------------------------|---------|
| V_i ↔ V_i            | (0, 0, 0)        | 0 (Zitterbewegung)              | 0       |
| V_2 ↔ V_3 (and rev.) | (±2, ∓2, 0)      | ±n_perp (2√2)                   | **0**   |
| V_1 ↔ V_2 (and rev.) | (0, ±2, ±2)      | ±2 along y                      | ±2      |
| V_1 ↔ V_3 (and rev.) | (±2, 0, ±2)      | ±2 along x                      | ±2      |

Of the 9 distinct 2-tick xy-only displacements (excluding z-drift):

- 3 give zero net motion (Zitterbewegung).
- 6 give ±n_perp motion (V_2↔V_3 family).
- **0 give net motion along ±n_par.**

Forward propagation along n_par requires V_1 ↔ V_1, which is the
zero-displacement Zitterbewegung pair.  All other "forward-with-V_1"
combinations (V_1 ↔ V_2, V_1 ↔ V_3) carry a ±2 z-drift, hitting the
boundaries of a thin z-grid (z = 0..4 here) within 2-3 tick-pairs and
losing their amplitude to boundary clipping.

### The original axis-aligned geometry by contrast

In axis-aligned exp_03 (forward = +x):

| Pair                  | Net x         | z drift |
|-----------------------|---------------|---------|
| V_2 ↔ V_3             | +2 (forward)  | 0       |
| V_3 ↔ V_2             | -2            | 0       |
| V_1 ↔ V_3             | +2 (forward)  | ±2      |
| etc.                  |               |         |

The V_2 ↔ V_3 pair gives **+2 along the forward axis with zero z-drift**.
This is the work-horse forward-propagation pairing on a thin z-grid, and
it is the reason the original exp_03 produces visible wavefronts toward
the screen on a 5-deep z grid.

### Why the rotation makes things worse, in one sentence

The rotation re-aligns "forward" with the axis (V_1) that has the
**least productive** 2-tick pairing for thin z-grids -- it's the
Zitterbewegung axis -- and re-aligns the slit-line with the
**most productive** xy-only pairing axis (V_2 ↔ V_3).  Result: the wave
goes sideways instead of forward.

### What would actually fix the visualization issue

The user's original concern -- "slit B's beam exits the bottom of the
frame" -- is fixable in the **original** geometry simply by:

1. Widening grid_y so the V_1/V_2-projected wavefronts from both slits
   stay in frame.
2. Optionally clipping display range tightly around the screen and the
   slits, hiding the regions where beams exit the boundary.

This was achievable without redesigning the experiment, and it preserves
the productive 2-tick pairings.  The rotated frame is theoretically
elegant ("forward = projected V_1") but the lattice's actual preferred
xy-direction in a thin z-grid is the V_2 ↔ V_3 diagonal, which the
original geometry already exploits.

### Status of the deliverables

- Script (`src/utilities/exp_03b_lanterns_aligned.py`) -- left in place
  with a deprecation header pointing back to this postmortem.  Useful
  reference for the geometry-construction code (which is correct and
  reusable) and for anyone thinking of trying the same rotation.
- Figures (`figures/exp_03b_lanterns_aligned.{pdf,png}`) -- can be
  removed; they will not be used in the paper.
- Paper section `interference.tex` -- unchanged; continues to use
  `exp_03_lanterns` with the "Note on geometry" caption that
  acknowledges the lattice anisotropy honestly.
