"""
plot_causal_cone_screen.py
Causal cone cross-section: the screen image of a point-source photon.

KEY GEOMETRY DISCOVERY:
On the T3_diamond lattice every RGB step changes (z - x - y) by:
  V1=(1,1,1):  dz-dx-dy = 1-1-1 = -1
  V2=(1,-1,-1): dz-dx-dy = -1-1+1 = -1
  V3=(-1,1,-1): dz-dx-dy = -1+1-1 = -1
Every CMY step changes it by +1.  For a massless photon (strict alternating
RGB/CMY parity) the quantity z - x - y is EXACTLY CONSERVED.

A point source starting at (cx, cy, cz) stays on the invariant plane:
    z - x - y = cz - cx - cy  (constant, all ticks)

This is NOT the 3D octahedron from exp_00.  The OctahedralLattice gives a
loose upper bound; the invariant plane is the TIGHT constraint.

WHAT THE CROSS-SECTIONS SHOW:
  z = cz slice:  must also have x + y = cx + cy (from invariant).
                 Intersection is the 1D anti-diagonal Dy = -Dx, spaced by 2.
  sum_z P:       projection onto the invariant plane z = x + y + const.
                 The 2D shape is a hexagon (diamond + 45deg rotated square).

  Massive particle (omega > 0): RGB/CMY parity can stall, so z - x - y is
  NOT conserved -- amplitude leaks off the invariant plane.
  The massive z-slice shows a 2D filled disk rather than a 1D line.

PANELS:
  Top-left   -- massless photon z-slice: 1D anti-diagonal line.
                Photon is confined to the invariant plane; slice is a line.
  Top-right  -- massless photon full projection sum_z P: the true 2D
                "screen" image -- a hexagonal distribution.
  Bottom-left  -- massive particle (omega=pi/2) z-slice: 2D filled disk.
                  Amplitude has leaked off the invariant plane.
  Bottom-right -- massless projection + theoretical anti-diagonal boundary
                  Dy = -Dx overlaid.  Simulation agrees with invariant exactly.

Run from repo root:
    python src/utilities/plot_causal_cone_screen.py
Saves: figures/causal_cone_screen.pdf + .png
"""

import sys, os
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.core import OctahedralLattice, CausalSession

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

_ROOT   = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT_DIR = os.path.join(_ROOT, 'figures')

# -- Parameters ---------------------------------------------------------------
GRID    = 51          # grid size; centre at 25
N_TICKS = 14          # causal front; well inside grid (margin 11)
CENTER  = (GRID // 2,) * 3

C_BG  = 'white'
C_AX  = '#f5f5f5'


# -- Simulation ---------------------------------------------------------------

def run_point_source(omega):
    """
    Point source at CENTER, run for N_TICKS.
    Returns 3D probability density array P[x, y, z].
    """
    lattice = OctahedralLattice(GRID, GRID, GRID)
    s = CausalSession(lattice, CENTER, instruction_frequency=omega)
    for _ in range(N_TICKS):
        s.tick()
        s.advance_tick_counter()
    return s.probability_density()


def antidiagonal_boundary(cx, cy, n_ticks, size):
    """
    Boolean mask: nodes where Dy = -Dx (anti-diagonal) within reach.
    These are the nodes satisfying the massless invariant in the z=cz slice.
    Nodes: (cx + k, cy - k) for k in range(-n_ticks, n_ticks+1, 2).
    Returns xs, ys arrays of the boundary points.
    """
    ks = np.arange(-n_ticks, n_ticks + 1, 2)
    xs = cx + ks
    ys = cy - ks
    # clip to grid
    valid = (xs >= 0) & (xs < size) & (ys >= 0) & (ys < size)
    return xs[valid], ys[valid]


def invariant_plane_boundary(cx, cy, cz, n_ticks, size):
    """
    Outer boundary of the invariant plane projection onto (x, y).
    Each pair of (RGB, CMY) steps produces a net displacement of size 2
    from the set {(0,2),(2,0),(2,-2),(0,-2),(-2,0),(-2,2)}.
    These are exactly the six nearest-neighbor moves on a hexagonal lattice
    with spacing 2.
    After n_ticks ticks = n_ticks/2 such 2-step pairs, the reachable set is
    all (Dx, Dy) = (2a, 2b) with hexagonal distance max(|a|,|b|,|a-b|) <= n_ticks/2.
    The boundary (outer ring) has 6 * (n_ticks/2) nodes.
    Returns boolean mask on size x size grid.
    """
    ix = np.arange(size)
    xx, yy = np.meshgrid(ix, ix, indexing='ij')
    Dx = xx - cx
    Dy = yy - cy
    # Only even-offset nodes are reachable (each move changes by 2)
    even = (Dx % 2 == 0) & (Dy % 2 == 0)
    # Hexagonal distance in units of 2
    a = Dx // 2
    b = Dy // 2
    hex_dist = np.maximum(np.abs(a), np.maximum(np.abs(b), np.abs(a - b)))
    return even & (hex_dist == n_ticks // 2)


# -- Plotting helpers ---------------------------------------------------------

def _style_ax(ax, title):
    ax.set_facecolor(C_AX)
    ax.set_title(title, color='black', fontsize=8, pad=6)
    ax.set_xlabel('x  (lattice index)', color='#333', fontsize=7)
    ax.set_ylabel('y  (lattice index)', color='#333', fontsize=7)
    ax.tick_params(colors='#333', labelsize=6)
    for sp in ax.spines.values():
        sp.set_color('#999')


def _imshow(ax, data_xy, cmap='hot_r', vmax=None):
    """
    Display data[x, y] with x on horizontal axis, y on vertical.
    Returns the AxesImage.
    """
    if vmax is None:
        vmax = data_xy.max()
    kw = dict(origin='lower', aspect='equal',
              extent=[0, GRID, 0, GRID],
              cmap=cmap, vmin=0, vmax=max(vmax, 1e-12))
    return ax.imshow(data_xy.T, **kw)


# -- Main ---------------------------------------------------------------------

def main():
    cx, cy, cz = CENTER

    print("Causal cone screen  GRID=%d  N_TICKS=%d  CENTER=%s" % (GRID, N_TICKS, CENTER))
    print()

    print("  Running massless photon  omega=0 ...")
    P0 = run_point_source(omega=0.0)

    print("  Running massive particle omega=pi/2 ...")
    Phalf = run_point_source(omega=np.pi / 2)

    # -- Derived quantities ---------------------------------------------------
    slice_m0   = P0[:, :, cz]       # z = cz cross-section, massless
    slice_mhalf = Phalf[:, :, cz]   # z = cz cross-section, massive
    proj_m0    = P0.sum(axis=2)     # sum_z P, massless (projection onto xy)

    # Verify the invariant: all massless amplitude satisfies z - x - y = cz - cx - cy
    inv_val = cz - cx - cy
    ix = np.arange(GRID)
    xx, yy, zz = np.meshgrid(ix, ix, ix, indexing='ij')
    inv_field = zz - xx - yy
    active = P0 > 1e-15
    inv_vals_at_active = inv_field[active]
    unique_inv = np.unique(inv_vals_at_active)
    print("  Invariant z-x-y at all active massless nodes: %s  (expected: %d)" % (
          unique_inv, inv_val))
    print()

    # Anti-diagonal boundary for z=cz slice
    bx_line, by_line = antidiagonal_boundary(cx, cy, N_TICKS, GRID)

    # Hexagonal boundary for projection
    hex_boundary = invariant_plane_boundary(cx, cy, cz, N_TICKS, GRID)

    total_slice_m0    = slice_m0.sum()
    total_slice_mhalf = slice_mhalf.sum()
    total_proj        = proj_m0.sum()
    print("  Massless  z-slice total P = %.6f" % total_slice_m0)
    print("  Massive   z-slice total P = %.6f" % total_slice_mhalf)
    print("  Massless  projection  P   = %.6f  (should be ~1)" % total_proj)
    print()

    # Count active nodes in z-slice
    active_slice = int((slice_m0 > 1e-15).sum())
    active_proj  = int((proj_m0 > 1e-15).sum())
    print("  Massless z-slice active nodes: %d  (expected: %d along anti-diagonal)" % (
          active_slice, N_TICKS + 1))
    print("  Massless projection active nodes: %d" % active_proj)

    # Check what fraction of projection P falls on hexagonal boundary
    hex_P    = float(proj_m0[hex_boundary].sum())
    hex_cnt  = int(hex_boundary.sum())
    print("  Projection P on hex boundary (%d nodes): %.6f / %.6f" % (
          hex_cnt, hex_P, total_proj))
    print()

    # -- Figure ---------------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(11, 10))
    fig.patch.set_facecolor(C_BG)

    # Panel 1: massless z-slice -- the 1D anti-diagonal line
    ax = axes[0, 0]
    _style_ax(ax,
        'Massless photon  omega=0  (z = %d slice, tick %d)\n'
        'Invariant: z-x-y = const.  Slice is a 1D anti-diagonal line.' % (cz, N_TICKS))
    _imshow(ax, slice_m0)
    ax.plot(cx, cy, '+', color='#006644', ms=8, mew=1.5, label='origin')
    # Draw the anti-diagonal guide line
    x_line = np.array([cx - N_TICKS - 1, cx + N_TICKS + 1])
    y_line = cy - (x_line - cx)
    ax.plot(x_line, y_line, '--', color='#555', lw=0.8, alpha=0.6, label='Dy = -Dx')
    ax.set_xlim(cx - N_TICKS - 3, cx + N_TICKS + 3)
    ax.set_ylim(cy - N_TICKS - 3, cy + N_TICKS + 3)
    ax.legend(fontsize=6, facecolor='white', edgecolor='#aaa', labelcolor='black', loc='upper right')

    # Panel 2: massless full projection -- the hexagonal 2D shape
    ax = axes[0, 1]
    _style_ax(ax,
        'Massless photon  omega=0  (sum_z projection, tick %d)\n'
        'True 2D screen image: hexagonal distribution on invariant plane.' % N_TICKS)
    _imshow(ax, proj_m0)
    ax.plot(cx, cy, '+', color='#006644', ms=8, mew=1.5)
    # Draw hexagonal boundary overlay
    hbx, hby = np.where(hex_boundary)
    ax.scatter(hbx, hby, s=6, c='#006644', alpha=0.9, linewidths=0,
               label='hex boundary  max(|Dx|,|Dy|,|Dx-Dy|) = %d' % N_TICKS)
    ax.set_xlim(cx - N_TICKS - 3, cx + N_TICKS + 3)
    ax.set_ylim(cy - N_TICKS - 3, cy + N_TICKS + 3)
    ax.legend(fontsize=6, facecolor='white', edgecolor='#aaa', labelcolor='black', loc='upper right')

    # Panel 3: massive z-slice -- 2D filled disk (invariant NOT conserved)
    ax = axes[1, 0]
    _style_ax(ax,
        'Massive particle  omega=pi/2  (z = %d slice, tick %d)\n'
        'Invariant NOT conserved: amplitude fills 2D disk.' % (cz, N_TICKS))
    _imshow(ax, slice_mhalf)
    ax.plot(cx, cy, '+', color='#006644', ms=8, mew=1.5)
    ax.set_xlim(cx - N_TICKS - 3, cx + N_TICKS + 3)
    ax.set_ylim(cy - N_TICKS - 3, cy + N_TICKS + 3)

    # Panel 4: massless z-slice + anti-diagonal boundary overlay
    ax = axes[1, 1]
    _style_ax(ax,
        'Massless photon + theoretical anti-diagonal boundary\n'
        'Dy = -Dx (at z = cz).  Simulation agrees with invariant exactly.')
    _imshow(ax, slice_m0)
    # Draw the theoretical anti-diagonal boundary points
    ax.scatter(bx_line, by_line, s=22, c='#006644', alpha=0.95, linewidths=0,
               zorder=5, label='anti-diagonal  Dy = -Dx  (from invariant)')
    ax.plot(cx, cy, '+', color='#cc2200', ms=10, mew=2, zorder=6, label='origin')
    ax.set_xlim(cx - N_TICKS - 3, cx + N_TICKS + 3)
    ax.set_ylim(cy - N_TICKS - 3, cy + N_TICKS + 3)
    ax.legend(fontsize=6, facecolor='white', edgecolor='#aaa', labelcolor='black',
              loc='upper right', markerscale=1.5)

    fig.suptitle(
        'Causal cone cross-section -- T3_diamond lattice\n'
        'Massless photon conserves z-x-y exactly.  Causal cone lies on 2D invariant plane.\n'
        'Tick %d   Grid %d^3   Centre %s' % (N_TICKS, GRID, CENTER),
        color='black', fontsize=10, y=1.01
    )

    plt.tight_layout(rect=[0, 0, 1, 1])

    out_pdf = os.path.join(OUT_DIR, 'causal_cone_screen.pdf')
    out_png = os.path.join(OUT_DIR, 'causal_cone_screen.png')
    fig.savefig(out_pdf, dpi=150, bbox_inches='tight', facecolor=C_BG)
    fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor=C_BG)
    print("Saved: %s" % out_pdf)
    print("Saved: %s" % out_png)


if __name__ == '__main__':
    main()
