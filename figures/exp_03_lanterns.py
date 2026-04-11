"""
exp_03_lanterns.py
Double-slit interference figure: the Huygens Lantern.

Two panels on a white background:
  Left  -- coherent: two sources interfere, bright fringes glow like lanterns.
  Right -- decoherent: detector at slit A scrambles phase, fringes collapse.

Shows the full 2D probability density in the (x, y) plane at z=z_mid,
propagated via tick() from two coherent point sources.  No analytical
Huygens-Fresnel formula -- the pattern emerges from lattice dynamics alone.

Geometry tuned so that fringe spacing ~ 22 nodes, giving 2-3 visible fringes
within the grid:  lambda*L/d = (2pi/0.40)*42/30 ~ 22 nodes.

Run from repo root:
    python figures/exp_03_lanterns.py
Saves:
    figures/exp_03_lanterns.pdf
    figures/exp_03_lanterns.png
"""

import sys, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm
from scipy.ndimage import gaussian_filter

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core import OctahedralLattice, CausalSession, enforce_unity_spinor

_ROOT   = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT_DIR = os.path.join(_ROOT, 'figures')

# ── Geometry ──────────────────────────────────────────────────────────────────
# Slit separation d=58 (y=12 to y=70), propagation L=42, OMEGA=0.40
# Fringe spacing = lambda*L/d = 15.7*42/58 ~ 11 nodes  (3-4 visible fringes)
#
# GRID_Y=150: slit B's upward wavefront (y=70+t) hits boundary at t=80,
# well after it reaches the screen at t=42.  No boundary corruption.
# Display is clipped to y=0..DISPLAY_Y to keep the figure proportions.
GRID_X, GRID_Y, GRID_Z = 60, 150, 5
SRC_X    = 6
SLIT_Y1  = 12           # slit A (lower)
SLIT_Y2  = 70           # slit B (upper, as requested)
DISPLAY_Y_MIN = SLIT_Y1 - 8   # = 4  -- small margin below slit A
DISPLAY_Y     = SLIT_Y2 + 10  # = 80 -- small margin above slit B
SCREEN_X = 48           # propagation distance from slits = 42 nodes
Z_MID    = 2
OMEGA    = 0.40         # de Broglie wavelength ~15.7 nodes
TICKS    = 75           # wave reaches screen at t=42; 33 extra ticks to accumulate
SRC_W    = 5.0          # Gaussian source width in nodes

# ── Style ─────────────────────────────────────────────────────────────────────
C_BG     = '#ffffff'
C_PANEL  = '#f2f2f2'   # light grey panel background -- dark fringes show up
C_TEXT   = '#1a1a1a'

# Custom lantern colormap: light-grey -> pale yellow -> amber -> dark red
# Zero maps to C_PANEL (not white) so dark fringes are visible against the panel
from matplotlib.colors import LinearSegmentedColormap
LANTERN_COLORS = [
    (0.00, C_PANEL),    # zero amplitude -> panel grey (dark fringes visible)
    (0.06, '#fff8e0'),  # faint warm tint
    (0.20, '#fde68a'),  # pale gold
    (0.45, '#f5a000'),  # amber
    (0.70, '#c85000'),  # burnt orange
    (0.88, '#7a1f00'),  # dark red
    (1.00, '#3d0000'),  # deep red (peak)
]
cmap_lantern = LinearSegmentedColormap.from_list(
    'lantern', [(v, c) for v, c in LANTERN_COLORS])


# ── Session builder ───────────────────────────────────────────────────────────

def build_session(scramble_A=False, rng=None):
    """
    Initialise a two-source session at (SRC_X, SLIT_Y1) and (SRC_X, SLIT_Y2).
    scramble_A: if True, randomise phase at slit A (decoherence).
    """
    if rng is None:
        rng = np.random.default_rng(42)

    lattice = OctahedralLattice(GRID_X, GRID_Y, GRID_Z)
    session = CausalSession(lattice, (SRC_X, SLIT_Y1, Z_MID),
                            instruction_frequency=OMEGA, is_massless=False)
    session.psi_R[:] = 0.0
    session.psi_L[:] = 0.0

    for y in range(GRID_Y):
        for z in range(GRID_Z):
            rA = np.sqrt((y - SLIT_Y1)**2 + (z - Z_MID)**2)
            rB = np.sqrt((y - SLIT_Y2)**2 + (z - Z_MID)**2)
            val = (np.exp(-0.5 * (rA / SRC_W)**2) +
                   np.exp(-0.5 * (rB / SRC_W)**2))
            if val > 1e-4:
                session.psi_R[SRC_X, y, z] = val / np.sqrt(2.0) + 0j
                session.psi_L[SRC_X, y, z] = val / np.sqrt(2.0) + 0j

    if scramble_A:
        # Randomise phase at slit A only: local decoherence (observer at A)
        for y in range(GRID_Y):
            for z in range(GRID_Z):
                rA = np.sqrt((y - SLIT_Y1)**2 + (z - Z_MID)**2)
                if rA < SRC_W * 2.5:
                    phase = rng.uniform(0, 2 * np.pi)
                    session.psi_R[SRC_X, y, z] *= np.exp(1j * phase)
                    session.psi_L[SRC_X, y, z] *= np.exp(1j * phase)

    enforce_unity_spinor(session.psi_R, session.psi_L)
    return session


def run_and_capture(scramble_A=False):
    """
    Run TICKS ticks and return the 2D probability density summed over z,
    shape (GRID_X, GRID_Y).
    """
    session = build_session(scramble_A=scramble_A)
    for _ in range(TICKS):
        session.tick()
        session.advance_tick_counter()

    dens = (np.abs(session.psi_R)**2 + np.abs(session.psi_L)**2)
    dens_xy = dens.sum(axis=2)   # shape (GRID_X, GRID_Y)
    return dens_xy


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Running coherent interference (exp_03)...")
    dens_coherent = run_and_capture(scramble_A=False)
    print("Running decoherent (detector at slit A, exp_04)...")
    dens_decoherent = run_and_capture(scramble_A=True)

    # Normalise each x-column independently so the transverse fringe pattern
    # is visible at every propagation distance regardless of absolute amplitude.
    # (Global normalisation makes x>15 invisible because enforce_unity_spinor
    # spreads total probability across all nodes; per-column fixes this.)
    from scipy.ndimage import gaussian_filter1d

    def col_norm(a, y_sigma=1.2):
        """Normalise each propagation-distance column to [0,1] after mild y-smooth."""
        result = np.zeros_like(a, dtype=float)
        for ix in range(a.shape[0]):
            col = gaussian_filter1d(a[ix, :].astype(float), sigma=y_sigma)
            mx = col.max()
            if mx > 1e-12:
                result[ix, :] = col / mx
        return result

    coh = col_norm(dens_coherent)
    dec = col_norm(dens_decoherent)

    # Gentle 2-D bloom only on bright peaks
    def bloom(arr, sigma=0.8, strength=0.25):
        blurred = gaussian_filter(arr, sigma=sigma)
        return np.clip(arr + strength * blurred, 0, 1)

    coh = bloom(coh)
    dec = bloom(dec)

    # ── Figure layout ─────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(12, 6.0), facecolor=C_BG)

    # gamma=0.70: col_norm already lifts dim regions; keep some contrast
    imkw = dict(
        cmap=cmap_lantern,
        norm=PowerNorm(gamma=0.70),
        origin='lower',
        aspect='auto',
        interpolation='lanczos',
    )

    ax_coh = fig.add_axes([0.05, 0.10, 0.38, 0.82])
    ax_dec = fig.add_axes([0.46, 0.10, 0.38, 0.82])
    ax_bar = fig.add_axes([0.87, 0.10, 0.10, 0.82])

    ax_coh.imshow(coh.T, **imkw)
    ax_dec.imshow(dec.T, **imkw)

    # ── Annotations ───────────────────────────────────────────────────────────
    annot_kw = dict(color=C_TEXT, fontsize=9, alpha=0.85)

    def vline(ax, x, label, side='right'):
        ax.axvline(x, color='#888888', lw=0.7, alpha=0.7, ls='--')
        xoff = 0.5 if side == 'right' else -0.5
        ax.text(x + xoff, DISPLAY_Y - 0.5, label, va='top',
                ha='left' if side == 'right' else 'right', **annot_kw)

    def hline(ax, y, label):
        ax.axhline(y, color='#8090a0', lw=0.6, alpha=0.7, ls=':')
        ax.text(GRID_X * 0.02, y + 0.6, label, va='bottom', **annot_kw)

    for ax in (ax_coh, ax_dec):
        vline(ax, SRC_X,    'slits',  side='right')
        vline(ax, SCREEN_X, 'screen', side='right')
        hline(ax, SLIT_Y1, 'A')
        hline(ax, SLIT_Y2, 'B')
        ax.set_facecolor(C_PANEL)
        ax.tick_params(colors=C_TEXT, labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor('#aaaaaa')
        ax.set_xlabel('x  (propagation)', color=C_TEXT, fontsize=9)
        ax.set_ylabel('y  (transverse)',  color=C_TEXT, fontsize=9)
        ax.tick_params(axis='x', colors=C_TEXT)
        ax.tick_params(axis='y', colors=C_TEXT)
        ax.set_xlim(0, GRID_X - 1)
        ax.set_ylim(DISPLAY_Y_MIN, DISPLAY_Y)  # clip to slit window; grid extends to 150

    ax_coh.set_title('Coherent -- two open slits',
                     color=C_TEXT, fontsize=11, pad=8)
    ax_dec.set_title('Decoherent -- observer at slit A',
                     color=C_TEXT, fontsize=11, pad=8)

    # Screen profile insets overlaid on each 2D panel
    def add_profile_inset(parent_ax, dens_xy, x_pos, color='#ffd060'):
        profile = dens_xy[x_pos, DISPLAY_Y_MIN:DISPLAY_Y + 1]
        profile = profile / (profile.max() + 1e-30)
        for yi, val in enumerate(profile):
            y_data = DISPLAY_Y_MIN + yi
            if val > 0.02:
                parent_ax.barh(y_data, val * 5, left=x_pos,
                               height=0.9, color=color,
                               alpha=min(val * 2.0, 0.9))

    add_profile_inset(ax_coh, dens_coherent, SCREEN_X)
    add_profile_inset(ax_dec, dens_decoherent, SCREEN_X)

    # ── Third panel: 1D screen intensity ──────────────────────────────────────
    ax_bar.set_facecolor(C_BG)
    for spine in ax_bar.spines.values():
        spine.set_edgecolor('#aaaaaa')

    # Use only the displayed y-range for the screen profile
    prof_coh = dens_coherent[SCREEN_X, DISPLAY_Y_MIN:DISPLAY_Y + 1].copy()
    prof_dec = dens_decoherent[SCREEN_X, DISPLAY_Y_MIN:DISPLAY_Y + 1].copy()
    scale = prof_coh.max() + 1e-30
    prof_coh /= scale
    prof_dec /= scale   # same normalisation for honest comparison

    y_coords = np.arange(DISPLAY_Y_MIN, DISPLAY_Y + 1)

    ax_bar.fill_betweenx(y_coords, 0, prof_coh,
                         color='#f5a000', alpha=0.25)
    ax_bar.plot(prof_coh, y_coords,
                color='#c85000', lw=1.5, label='coherent')
    ax_bar.plot(prof_dec, y_coords,
                color='#2060a0', lw=1.0, ls='--', alpha=0.80,
                label='decoherent')

    # Mark coherent fringe peaks as lantern dots
    try:
        from scipy.signal import find_peaks as _fp
        peaks, _ = _fp(prof_coh, height=0.12, distance=4)
    except Exception:
        n = len(prof_coh)
        peaks = np.array([i for i in range(1, n - 1)
                          if prof_coh[i] > prof_coh[i-1]
                          and prof_coh[i] > prof_coh[i+1]
                          and prof_coh[i] > 0.12])

    for pk in peaks:
        y_data = y_coords[pk]
        ax_bar.scatter(prof_coh[pk], y_data, s=200, color='#f5a000',
                       alpha=0.30, zorder=4)
        ax_bar.scatter(prof_coh[pk], y_data, s=50,  color='#7a1f00',
                       alpha=0.95, zorder=5)

    ax_bar.axvline(0, color='#888888', lw=0.6)
    ax_bar.set_xlim(-0.05, 1.30)
    ax_bar.set_ylim(DISPLAY_Y_MIN, DISPLAY_Y)
    ax_bar.set_yticks([SLIT_Y1, SLIT_Y2])
    ax_bar.set_yticklabels(['A', 'B'], color=C_TEXT, fontsize=9)
    ax_bar.set_xticks([0, 0.5, 1.0])
    ax_bar.set_xticklabels(['0', '', '1'], color=C_TEXT, fontsize=7)
    ax_bar.set_title('screen\nfringes', color=C_TEXT, fontsize=8, pad=6)
    ax_bar.tick_params(colors=C_TEXT)
    ax_bar.set_xlabel('I', color=C_TEXT, fontsize=8)

    for sy in (SLIT_Y1, SLIT_Y2):
        ax_bar.axhline(sy, color='#405060', lw=0.6, ls=':')

    ax_bar.legend(loc='upper right', fontsize=6,
                  facecolor='#f8f8f8', edgecolor='#aaaaaa',
                  labelcolor=C_TEXT, framealpha=0.9)

    # ── Title ─────────────────────────────────────────────────────────────────
    fig.text(0.50, 0.98,
             'Double-Slit Interference on the $\\mathcal{T}^3_\\diamond$ Lattice '
             '(the Huygens Lantern)',
             ha='center', va='top', color=C_TEXT, fontsize=12, fontweight='bold')

    fig.text(0.50, 0.01,
             'Probability density $|\\psi_R|^2 + |\\psi_L|^2$  '
             'propagated via tick() from two coherent sources.  '
             'No analytical formula used.',
             ha='center', va='bottom', color=C_TEXT, alpha=0.65, fontsize=8)

    # ── Save ──────────────────────────────────────────────────────────────────
    pdf_path = os.path.join(OUT_DIR, 'exp_03_lanterns.pdf')
    png_path = os.path.join(OUT_DIR, 'exp_03_lanterns.png')
    fig.savefig(pdf_path, dpi=200, bbox_inches='tight', facecolor=C_BG)
    fig.savefig(png_path, dpi=200, bbox_inches='tight', facecolor=C_BG)
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")


if __name__ == '__main__':
    main()
