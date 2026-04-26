"""
exp_03b_lanterns_aligned.py

DEPRECATED -- the design fails for thin z-grids.  Three runs at increasing
parameter sizes (2026-04-26) all show the wavefront staying in the slit-line
region instead of propagating toward the screen.  Root cause: the rotation
re-aligns "forward" with V_1, whose 2-tick pairing (V_1 ↔ V_1) is the
zero-displacement Zitterbewegung; the productive xy-only pairing for thin
z-grids is V_2 ↔ V_3 along ±n_perp, which is now the slit-line direction.
See the postmortem in notes/exp_03b_lanterns_aligned_design.md for the full
analysis.

The script is left in place as a reference for the geometry-construction code
(make_geometry, screen_profile -- both correct and reusable) and as a worked
example of why this rotation does not produce the intended result.  The
paper continues to use exp_03_lanterns with an honest "Note on geometry"
caption acknowledging the lattice anisotropy.

================================================================
ORIGINAL DESIGN (preserved below):

Lattice-aligned double-slit interference on the bipartite T^3_diamond lattice.

The original exp_03 places slits along the y-axis with "forward" = +x.  On the
bipartite lattice this fights the geometry: every causal hop covers a body-
diagonal V_i, so amplitude from each slit propagates diagonally and slit B's
beam exits the bottom of the frame before reaching the screen.  See
notes/exp_03b_lanterns_aligned_design.md for the full design rationale.

This experiment rotates the entire frame 45 degrees counterclockwise so the
"forward" direction is the projected body-diagonal:

    n_par  = (x_hat + y_hat) / sqrt(2)    # forward (= projected V_1)
    n_perp = (x_hat - y_hat) / sqrt(2)    # slit-line, perpendicular to n_par

Both slits' dominant beams (along V_1 / -V_1, projected to n_par / -n_par)
travel directly toward (or away from) the screen.  Neither beam exits the
frame perpendicular to the experimental axis.  The fringe pattern at the
screen lies along n_perp.

CLI:
    python src/utilities/exp_03b_lanterns_aligned.py
    python src/utilities/exp_03b_lanterns_aligned.py --quick
    python src/utilities/exp_03b_lanterns_aligned.py --slits 60 --propagation 100 --ticks 120

Saves:
    figures/exp_03b_lanterns_aligned.pdf
    figures/exp_03b_lanterns_aligned.png

Runtime:
    Default parameters take roughly 10-30 minutes on a single CPU.
    Quick mode is a few minutes for a sanity-check geometry test.
    Larger runs (s=80, L=200, ticks=300 -- the design-note "continuum-limit"
    setup) are several hours.  Runtime is dominated by the kinetic hop.
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, PowerNorm
from scipy.ndimage import gaussian_filter, gaussian_filter1d

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.core import OctahedralLattice, CausalSession, enforce_unity_spinor


_ROOT   = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(_ROOT, "figures")

# ── Default geometry ─────────────────────────────────────────────────────────
# Sized to run in 10-30 min on a single CPU.  Larger values (closer to the
# continuum limit) are tunable via CLI; see the design note for guidance.
DEFAULT_SLIT_SEP    = 40    # slit separation along n_perp (lattice nodes)
DEFAULT_PROPAGATION = 60    # propagation along n_par (lattice nodes)
DEFAULT_TICKS       = 80    # ticks (each covers sqrt(2) along n_par for pure-V_1)
DEFAULT_OMEGA       = 0.30  # mass parameter; lambda ~ 2pi/omega ~ 21 nodes
DEFAULT_SRC_W       = 5.0   # Gaussian source width

# Quick mode: minimal grid for a fast geometry sanity check.
QUICK_SLIT_SEP    = 20
QUICK_PROPAGATION = 30
QUICK_TICKS       = 40
QUICK_OMEGA       = 0.30
QUICK_SRC_W       = 4.0

Z_MID = 2

# Rotated unit vectors in the xy-plane
N_PAR  = np.array([1.0,  1.0, 0.0]) / np.sqrt(2.0)
N_PERP = np.array([1.0, -1.0, 0.0]) / np.sqrt(2.0)

# ── Visual style (matches exp_03_lanterns) ───────────────────────────────────
C_BG    = "#ffffff"
C_PANEL = "#f2f2f2"
C_TEXT  = "#1a1a1a"

LANTERN_COLORS = [
    (0.00, C_PANEL),
    (0.06, "#fff8e0"),
    (0.20, "#fde68a"),
    (0.45, "#f5a000"),
    (0.70, "#c85000"),
    (0.88, "#7a1f00"),
    (1.00, "#3d0000"),
]
cmap_lantern = LinearSegmentedColormap.from_list(
    "lantern", [(v, c) for v, c in LANTERN_COLORS])


# ── Geometry ──────────────────────────────────────────────────────────────────

def make_geometry(slit_sep: float, propagation: float, ticks: int,
                  src_w: float, margin: int = 10) -> dict:
    """Compute lattice positions and grid size such that the wavefront
    from each slit stays well inside the grid for `ticks` ticks.

    The binding constraint is wavefront reach: after N ticks, amplitude from a
    slit can extend up to N nodes in any axis direction.  We size the grid so
    both wavefronts plus the screen position fit with `margin` to spare.
    """
    half_sep_xy  = slit_sep / (2.0 * np.sqrt(2.0))   # slit x/y offset from center
    half_prop_xy = propagation / np.sqrt(2.0)        # screen x/y offset from center

    extent = max(half_sep_xy + ticks, half_prop_xy + 5) + margin
    cx = int(round(extent))
    cy = cx
    grid_x = 2 * cx
    grid_y = grid_x
    grid_z = 5

    slit_A = np.array([cx + half_sep_xy, cy - half_sep_xy, Z_MID]
                      ).round().astype(int)
    slit_B = np.array([cx - half_sep_xy, cy + half_sep_xy, Z_MID]
                      ).round().astype(int)
    screen_center = np.array([cx + half_prop_xy, cy + half_prop_xy, Z_MID]
                             ).round().astype(int)
    center = np.array([cx, cy, Z_MID])

    return dict(
        grid_x=grid_x, grid_y=grid_y, grid_z=grid_z,
        center=center, slit_A=slit_A, slit_B=slit_B,
        screen_center=screen_center,
        slit_sep=slit_sep, propagation=propagation,
        src_w=src_w, ticks=ticks,
    )


# ── Session builder ──────────────────────────────────────────────────────────

def build_session(geom: dict, scramble_A: bool = False,
                  omega: float = DEFAULT_OMEGA,
                  rng: np.random.Generator | None = None) -> CausalSession:
    """Initialise a two-source session with 3D Gaussian envelopes at each slit.

    If `scramble_A` is True, randomise the phase within slit A's source region
    to model decoherence from a co-located observer (same mechanism as exp_03).
    """
    if rng is None:
        rng = np.random.default_rng(42)

    lattice = OctahedralLattice(geom["grid_x"], geom["grid_y"], geom["grid_z"])
    session = CausalSession(lattice,
                            tuple(geom["slit_A"].tolist()),
                            instruction_frequency=omega, is_massless=False)
    session.psi_R[:] = 0.0
    session.psi_L[:] = 0.0

    sw = geom["src_w"]
    sw2 = sw * sw

    xs, ys, zs = np.meshgrid(
        np.arange(geom["grid_x"]),
        np.arange(geom["grid_y"]),
        np.arange(geom["grid_z"]),
        indexing="ij",
    )
    rA2 = ((xs - geom["slit_A"][0])**2
         + (ys - geom["slit_A"][1])**2
         + (zs - geom["slit_A"][2])**2)
    rB2 = ((xs - geom["slit_B"][0])**2
         + (ys - geom["slit_B"][1])**2
         + (zs - geom["slit_B"][2])**2)

    val = np.exp(-0.5 * rA2 / sw2) + np.exp(-0.5 * rB2 / sw2)
    mask = val > 1e-4

    # Equal initial amplitude on both chiralities; A=1 enforced below.
    half_amp = (val[mask] / np.sqrt(2.0)).astype(np.complex128)
    session.psi_R[mask] = half_amp
    session.psi_L[mask] = half_amp

    if scramble_A:
        nearA = rA2 < (sw * 2.5)**2
        random_phases = rng.uniform(0, 2 * np.pi, size=session.psi_R.shape)
        rot = np.exp(1j * random_phases[nearA])
        session.psi_R[nearA] *= rot
        session.psi_L[nearA] *= rot

    enforce_unity_spinor(session.psi_R, session.psi_L)
    return session


def run_and_capture(geom: dict, scramble_A: bool = False,
                    omega: float = DEFAULT_OMEGA, verbose: bool = True
                    ) -> np.ndarray:
    """Run `geom['ticks']` ticks; return 2D probability density summed over z."""
    n_ticks = geom["ticks"]
    t0 = time.time()
    session = build_session(geom, scramble_A=scramble_A, omega=omega)

    label = "decoherent" if scramble_A else "coherent"
    print(f"  [{label}] grid {geom['grid_x']}x{geom['grid_y']}x{geom['grid_z']}, "
          f"{n_ticks} ticks", flush=True)

    for t in range(n_ticks):
        session.tick()
        session.advance_tick_counter()
        if verbose and (t + 1) % max(1, n_ticks // 10) == 0:
            elapsed = time.time() - t0
            eta = elapsed * (n_ticks - t - 1) / max(1, t + 1)
            print(f"    tick {t+1:4d}/{n_ticks}  elapsed {elapsed:.0f}s  "
                  f"eta {eta:.0f}s", flush=True)

    dens = (np.abs(session.psi_R)**2 + np.abs(session.psi_L)**2)
    return dens.sum(axis=2)   # shape (grid_x, grid_y)


# ── Screen profile ───────────────────────────────────────────────────────────

def screen_profile(dens_xy: np.ndarray, geom: dict,
                   profile_width: int = 2) -> tuple[np.ndarray, np.ndarray]:
    """Sample the 2D density along a line through the screen center,
    perpendicular to the propagation direction (along n_perp).

    Returns (offsets, profile) with offsets in lattice-unit n_perp coordinates.
    """
    cx, cy, _ = geom["screen_center"]
    grid_x, grid_y = geom["grid_x"], geom["grid_y"]

    max_offset = min(grid_x - cx, cx, grid_y - cy, cy) - 2
    offsets = np.arange(-max_offset, max_offset + 1)
    profile = np.zeros(len(offsets))

    sqrt2 = np.sqrt(2.0)
    for i, off in enumerate(offsets):
        # Sample along n_perp; average over a small width along n_par
        for w in range(-profile_width, profile_width + 1):
            x = int(round(cx + off / sqrt2 + w / sqrt2))
            y = int(round(cy - off / sqrt2 + w / sqrt2))
            if 0 <= x < grid_x and 0 <= y < grid_y:
                profile[i] += dens_xy[x, y]
        profile[i] /= (2 * profile_width + 1)

    return offsets, profile


# ── Plotting ─────────────────────────────────────────────────────────────────

def _col_norm_par(arr: np.ndarray, geom: dict, sigma: float = 1.2) -> np.ndarray:
    """Normalise the 2D density along *n_par-aligned columns* so the fringe
    pattern is visible at every propagation distance regardless of total
    amplitude.  Done by re-sampling onto the (u, v) rotated grid, smoothing
    and per-u-column normalising, then re-sampling back to (x, y) for display.

    For simplicity here: just per-x-column normalise as a rough proxy.  At 45°
    rotation the n_par projection mostly tracks +x, so this is good enough for
    visualisation.
    """
    result = np.zeros_like(arr, dtype=float)
    for ix in range(arr.shape[0]):
        col = gaussian_filter1d(arr[ix, :].astype(float), sigma=sigma)
        mx = col.max()
        if mx > 1e-12:
            result[ix, :] = col / mx
    return result


def _bloom(arr: np.ndarray, sigma: float = 0.8, strength: float = 0.25) -> np.ndarray:
    return np.clip(arr + strength * gaussian_filter(arr, sigma=sigma), 0, 1)


def plot_results(geom: dict, dens_coh: np.ndarray, dens_dec: np.ndarray,
                 omega: float, out_pdf: str, out_png: str) -> None:
    coh = _bloom(_col_norm_par(dens_coh, geom))
    dec = _bloom(_col_norm_par(dens_dec, geom))

    fig = plt.figure(figsize=(12, 6.5), facecolor=C_BG)
    imkw = dict(
        cmap=cmap_lantern,
        norm=PowerNorm(gamma=0.70),
        origin="lower",
        aspect="auto",
        interpolation="lanczos",
    )

    # Lower top by 6% so the suptitle has clear room above subplot titles.
    ax_coh = fig.add_axes([0.05, 0.12, 0.38, 0.74])
    ax_dec = fig.add_axes([0.46, 0.12, 0.38, 0.74])
    ax_bar = fig.add_axes([0.87, 0.12, 0.10, 0.74])

    ax_coh.imshow(coh.T, **imkw)
    ax_dec.imshow(dec.T, **imkw)

    sqrt2 = np.sqrt(2.0)
    cx, cy = int(geom["center"][0]), int(geom["center"][1])
    sx, sy = int(geom["screen_center"][0]), int(geom["screen_center"][1])

    for ax in (ax_coh, ax_dec):
        ax.set_facecolor(C_PANEL)
        ax.tick_params(colors=C_TEXT, labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor("#aaaaaa")
        ax.set_xlabel("x", color=C_TEXT, fontsize=9)
        ax.set_ylabel("y", color=C_TEXT, fontsize=9)
        ax.set_xlim(0, geom["grid_x"] - 1)
        ax.set_ylim(0, geom["grid_y"] - 1)

        # Mark slits
        for slit, lbl in ((geom["slit_A"], "A"), (geom["slit_B"], "B")):
            ax.plot(slit[0], slit[1], "o", mfc="none",
                    mec="#1a1a1a", ms=10, mew=1.5, alpha=0.75)
            ax.text(slit[0] + 4, slit[1] + 4, lbl,
                    fontsize=10, color=C_TEXT, alpha=0.9)

        # Slit-line (passes through both slits along n_perp)
        max_sep = geom["slit_sep"]
        ax.plot([cx + max_sep / sqrt2, cx - max_sep / sqrt2],
                [cy - max_sep / sqrt2, cy + max_sep / sqrt2],
                ":", color="#8090a0", lw=0.7, alpha=0.7)

        # Screen line (perpendicular to n_par at screen_center)
        max_off = min(geom["grid_x"] - sx, sx,
                      geom["grid_y"] - sy, sy) - 2
        ax.plot([sx + max_off / sqrt2, sx - max_off / sqrt2],
                [sy - max_off / sqrt2, sy + max_off / sqrt2],
                "--", color="#888888", lw=0.8, alpha=0.7)
        ax.text(sx + 2, sy + 2, "screen", fontsize=8,
                color=C_TEXT, alpha=0.85)

        # n_par reference arrow (forward direction)
        ax.annotate("", xy=(cx + 12, cy + 12),
                    xytext=(cx, cy),
                    arrowprops=dict(arrowstyle="->", color="#404040", lw=1.2))
        ax.text(cx + 14, cy + 14, "$\\hat{n}_\\parallel$",
                fontsize=9, color=C_TEXT, alpha=0.9)

    ax_coh.set_title("Coherent (lattice-aligned, $45^\\circ$-rotated)",
                     color=C_TEXT, fontsize=11, pad=8)
    ax_dec.set_title("Decoherent (observer at slit A)",
                     color=C_TEXT, fontsize=11, pad=8)

    # Screen-profile panel
    ax_bar.set_facecolor(C_BG)
    for spine in ax_bar.spines.values():
        spine.set_edgecolor("#aaaaaa")

    offs_coh, prof_coh = screen_profile(dens_coh, geom)
    _,        prof_dec = screen_profile(dens_dec, geom)
    scale = prof_coh.max() + 1e-30
    prof_coh = prof_coh / scale
    prof_dec = prof_dec / scale

    ax_bar.fill_betweenx(offs_coh, 0, prof_coh, color="#f5a000", alpha=0.25)
    ax_bar.plot(prof_coh, offs_coh, color="#c85000", lw=1.5, label="coherent")
    ax_bar.plot(prof_dec, offs_coh, color="#2060a0", lw=1.0, ls="--",
                alpha=0.8, label="decoherent")
    ax_bar.axvline(0, color="#888888", lw=0.6)
    ax_bar.set_xlim(-0.05, 1.30)
    ax_bar.set_ylabel(r"screen offset along $\hat{n}_\perp$ (nodes)",
                      color=C_TEXT, fontsize=8)
    ax_bar.set_xlabel("I (a.u.)", color=C_TEXT, fontsize=8)
    ax_bar.tick_params(colors=C_TEXT, labelsize=7)
    ax_bar.set_title("screen\nfringes", color=C_TEXT, fontsize=8, pad=6)
    ax_bar.legend(loc="upper right", fontsize=6,
                  facecolor="#f8f8f8", edgecolor="#aaaaaa",
                  labelcolor=C_TEXT, framealpha=0.9)

    fig.text(0.50, 0.965,
             "Lattice-Aligned Double-Slit (exp\\_03b): "
             "$45^\\circ$-Rotated Frame, "
             "$\\hat{n}_\\parallel = (\\hat{x}+\\hat{y})/\\sqrt{2}$",
             ha="center", va="top", color=C_TEXT,
             fontsize=11, fontweight="bold")
    fig.text(0.50, 0.025,
             f"$s={geom['slit_sep']}$, $L={geom['propagation']}$, "
             f"$\\omega={omega}$, $N={geom['ticks']}$ ticks. "
             "Forward direction tracks the projected $\\mathbf{V}_1$ "
             "body-diagonal.",
             ha="center", va="bottom", color=C_TEXT,
             alpha=0.65, fontsize=8)

    fig.savefig(out_pdf, dpi=200, bbox_inches="tight", facecolor=C_BG)
    fig.savefig(out_png, dpi=200, bbox_inches="tight", facecolor=C_BG)
    print(f"Saved: {out_pdf}")
    print(f"Saved: {out_png}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true",
                    help="Fast sanity-check run with smaller grid.")
    ap.add_argument("--slits", type=float, default=None,
                    help="Slit separation (lattice nodes along n_perp).")
    ap.add_argument("--propagation", type=float, default=None,
                    help="Propagation distance (lattice nodes along n_par).")
    ap.add_argument("--ticks", type=int, default=None,
                    help="Number of ticks to run per scenario.")
    ap.add_argument("--omega", type=float, default=None,
                    help="Mass parameter (instruction frequency).")
    ap.add_argument("--src-w", dest="src_w", type=float, default=None,
                    help="Gaussian source width.")
    ap.add_argument("--out-pdf", dest="out_pdf", default=None,
                    help="Output PDF path.")
    ap.add_argument("--out-png", dest="out_png", default=None,
                    help="Output PNG path.")
    args = ap.parse_args()

    defaults = (
        (QUICK_SLIT_SEP, QUICK_PROPAGATION, QUICK_TICKS, QUICK_OMEGA, QUICK_SRC_W)
        if args.quick else
        (DEFAULT_SLIT_SEP, DEFAULT_PROPAGATION, DEFAULT_TICKS,
         DEFAULT_OMEGA, DEFAULT_SRC_W)
    )

    slit_sep    = args.slits       or defaults[0]
    propagation = args.propagation or defaults[1]
    ticks       = args.ticks       or defaults[2]
    omega       = args.omega       or defaults[3]
    src_w       = args.src_w       or defaults[4]

    out_pdf = args.out_pdf or os.path.join(OUT_DIR, "exp_03b_lanterns_aligned.pdf")
    out_png = args.out_png or os.path.join(OUT_DIR, "exp_03b_lanterns_aligned.png")

    geom = make_geometry(slit_sep, propagation, ticks, src_w)

    print("=" * 64)
    print("exp_03b: lattice-aligned double-slit, 45-degree-rotated frame")
    print("=" * 64)
    print(f"  Grid           : {geom['grid_x']} x {geom['grid_y']} x {geom['grid_z']}")
    print(f"  Center         : {tuple(int(c) for c in geom['center'])}")
    print(f"  Slit A         : {tuple(int(c) for c in geom['slit_A'])}")
    print(f"  Slit B         : {tuple(int(c) for c in geom['slit_B'])}")
    print(f"  Screen centre  : {tuple(int(c) for c in geom['screen_center'])}")
    print(f"  s = {slit_sep}, L = {propagation}, omega = {omega}, "
          f"src_w = {src_w}, N = {ticks}")
    print("=" * 64)

    print("\nRun 1/2: coherent")
    dens_coh = run_and_capture(geom, scramble_A=False, omega=omega)
    print("\nRun 2/2: decoherent (detector at slit A)")
    dens_dec = run_and_capture(geom, scramble_A=True,  omega=omega)

    print("\nPlotting...")
    plot_results(geom, dens_coh, dens_dec, omega, out_pdf, out_png)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
