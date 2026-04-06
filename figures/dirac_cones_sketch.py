"""
dirac_cones_sketch.py
Schematic of the three Dirac-like crossings in the (f, omega) harmonic landscape.

Three crossings where the n-th harmonic of f_zitt meets f_beat:
  2:1  f_zitt ∩ f_beat  ->  omega=pi/2,  f=1/4
  3:1  f_2nd  ∩ f_beat  ->  omega=pi/3,  f=1/3
  4:1  f_3rd  ∩ f_beat  ->  omega=pi/4,  f=3/8

Run from repo root:
  python figures/dirac_cones_sketch.py
Saves: figures/dirac_cones_sketch.pdf  +  .png
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Colour palette ─────────────────────────────────────────────────────────────
C_ZITT  = '#0077bb'   # blue        — f_zitt
C_BEAT  = '#cc6600'   # burnt orange — f_beat
C_2ND   = '#228833'   # green       — f_2nd
C_3RD   = '#aa2299'   # purple      — f_3rd
C_BG    = '#ffffff'   # white background (print-friendly)
C_GRID  = '#cccccc'
C_TEXT  = '#111111'

DIRAC_COLORS = ['#222222', '#228833', '#aa2299']   # 2:1, 3:1, 4:1

# ── Geometry ───────────────────────────────────────────────────────────────────
OM_MAX = np.pi          # y-axis max
F_MAX  = 0.5            # x-axis max

om = np.linspace(0, OM_MAX, 500)
f_zitt = om / (2 * np.pi)
f_beat = 0.5 - om / (2 * np.pi)
f_2nd  = 2 * om / (2 * np.pi)          # = om / pi
f_3rd  = 3 * om / (2 * np.pi)

# Mask lines to their valid domain (0 < f < 0.5)
def masked(f_arr):
    m = (f_arr >= 0) & (f_arr <= F_MAX)
    return np.where(m, f_arr, np.nan)

# ── Dirac crossing points (f, omega) ──────────────────────────────────────────
crossings = [
    dict(f=1/4,   om=np.pi/2, n='2:1',
         label='2:1\n$f_{\\mathrm{zitt}} = f_{\\mathrm{beat}}$\n$\\omega = \\pi/2$',
         lines=('f_zitt', 'f_beat'), color=DIRAC_COLORS[0]),
    dict(f=1/3,   om=np.pi/3, n='3:1',
         label='3:1\n$f_{\\mathrm{2nd}} = f_{\\mathrm{beat}}$\n$\\omega = \\pi/3$',
         lines=('f_2nd',  'f_beat'), color=DIRAC_COLORS[1]),
    dict(f=3/8,   om=np.pi/4, n='4:1',
         label='4:1\n$f_{\\mathrm{3rd}} = f_{\\mathrm{beat}}$\n$\\omega = \\pi/4$',
         lines=('f_3rd',  'f_beat'), color=DIRAC_COLORS[2]),
]

# ── Cone annotation helper ─────────────────────────────────────────────────────
def draw_cone(ax, fc, omc, slope_up, slope_dn, size=0.030, color='black', alpha=0.55):
    """
    Draw a shaded bowtie (Dirac cone cross-section) centred on (fc, omc).
    slope_up / slope_dn are d(omega)/d(f) for the two branches.
    size controls half-width in f units.
    Fills each triangular lobe with a gradient-like solid colour.
    """
    df = np.linspace(0, size, 80)

    # right lobe: between the two branches going right of centre
    f_r = fc + df
    ax.fill_between(f_r, omc + slope_up * df, omc + slope_dn * df,
                    color=color, alpha=alpha, linewidth=0)

    # left lobe: going left of centre (slopes reverse sign of df)
    f_l = fc - df
    ax.fill_between(f_l, omc - slope_up * df, omc - slope_dn * df,
                    color=color, alpha=alpha, linewidth=0)

    # draw the crossing arms with solid lines
    df_full = np.linspace(-size, size, 160)
    f_pts   = fc + df_full
    ax.plot(f_pts, omc + slope_up * df_full, color=color, lw=2.0, alpha=0.85)
    ax.plot(f_pts, omc + slope_dn * df_full, color=color, lw=2.0, alpha=0.85)

    # dot at crossing node
    ax.plot(fc, omc, 'o', color=color, markersize=6, zorder=7)


# ── Figure ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 6.5))
fig.patch.set_facecolor(C_BG)
ax.set_facecolor(C_BG)

# --- background grid ---
for fv in [0.125, 0.25, 0.375, 0.5]:
    ax.axvline(fv, color=C_GRID, lw=0.5, ls='--')
for ov in [np.pi/4, np.pi/3, np.pi/2, 2*np.pi/3, np.pi]:
    ax.axhline(ov, color=C_GRID, lw=0.5, ls='--')

# --- main dispersion lines ---
lw = 1.8
ax.plot(masked(f_zitt), om, color=C_ZITT,  lw=lw,
        label=r'$f_{\mathrm{zitt}} = \omega/2\pi$')
ax.plot(masked(f_beat),  om, color=C_BEAT,  lw=lw,
        label=r'$f_{\mathrm{beat}} = \frac{1}{2} - \omega/2\pi$')
ax.plot(masked(f_2nd),   om, color=C_2ND,   lw=lw,
        label=r'$f_{\mathrm{2nd}} = \omega/\pi$')
ax.plot(masked(f_3rd),   om, color=C_3RD,   lw=lw,
        label=r'$f_{\mathrm{3rd}} = 3\omega/2\pi$')

# f_vacuum vertical marker
ax.axvline(0.5, color='#555555', lw=1.0, ls=':', alpha=0.8,
           label=r'$f_{\mathrm{vacuum}} = 0.5$')

# --- cone shading and crossing markers ---
# slopes in (omega, f) space, i.e. d(omega)/d(f):
slope_zitt =  2 * np.pi   # df_zitt/dom = 1/(2pi) → dom/df = 2pi
slope_beat = -2 * np.pi
slope_2nd  =      np.pi   # df_2nd/dom = 1/pi → dom/df = pi
slope_3rd  =  2 * np.pi / 3

cone_slopes = [
    (slope_zitt, slope_beat),   # 2:1 crossing
    (slope_2nd,  slope_beat),   # 3:1 crossing
    (slope_3rd,  slope_beat),   # 4:1 crossing
]

for c, (s_up, s_dn) in zip(crossings, cone_slopes):
    draw_cone(ax, c['f'], c['om'], s_up, s_dn,
              size=0.032, color=c['color'], alpha=0.50)

# --- crossing labels ---
label_offsets = [
    (-0.10,  0.10),   # 2:1  — left+up
    (-0.10, -0.13),   # 3:1  — left+down
    (-0.10,  0.12),   # 4:1  — left+up (clear of the terminating line)
]
for c, (dff, dom) in zip(crossings, label_offsets):
    ax.annotate(c['label'],
                xy=(c['f'], c['om']),
                xytext=(c['f'] + dff, c['om'] + dom),
                color=c['color'],
                fontsize=8.5,
                ha='center', va='center',
                arrowprops=dict(arrowstyle='->', color=c['color'],
                                lw=0.9, alpha=0.7),
                bbox=dict(boxstyle='round,pad=0.3',
                          facecolor=C_BG, edgecolor=c['color'],
                          alpha=0.85, linewidth=0.8))

# --- axes cosmetics ---
ax.set_xlim(0, F_MAX)
ax.set_ylim(0, OM_MAX)

# y-axis ticks at meaningful omega values
y_ticks  = [np.pi/4, np.pi/3, np.pi/2, 2*np.pi/3, np.pi]
y_labels = [r'$\pi/4$', r'$\pi/3$', r'$\pi/2$', r'$2\pi/3$', r'$\pi$']
ax.set_yticks(y_ticks)
ax.set_yticklabels(y_labels, color=C_TEXT, fontsize=10)

x_ticks  = [0, 1/8, 1/4, 3/8, 1/2]
x_labels = [r'$0$', r'$\frac{1}{8}$', r'$\frac{1}{4}$', r'$\frac{3}{8}$', r'$\frac{1}{2}$']
ax.set_xticks(x_ticks)
ax.set_xticklabels(x_labels, color=C_TEXT, fontsize=10)

ax.tick_params(colors=C_TEXT, which='both')
for spine in ax.spines.values():
    spine.set_edgecolor('#888888')

ax.set_xlabel(r'Frequency $f$ (cycles / tick)', color=C_TEXT, fontsize=11)
ax.set_ylabel(r'Instruction frequency $\omega$', color=C_TEXT, fontsize=11)
ax.set_title('Dirac-like crossings in the harmonic landscape\n'
             r'each Arnold tongue lock-in $\equiv$ linear band crossing',
             color=C_TEXT, fontsize=11, pad=10)

# --- legend ---
leg = ax.legend(loc='upper left', fontsize=8.5,
                framealpha=0.9, facecolor=C_BG,
                edgecolor='#999999', labelcolor=C_TEXT)

# --- resonance order annotation (right margin) ---
for c in crossings:
    ax.annotate(c['n'], xy=(F_MAX, c['om']),
                xytext=(F_MAX + 0.012, c['om']),
                color=c['color'], fontsize=9, va='center',
                annotation_clip=False)

plt.tight_layout()

out_pdf = os.path.join(OUT_DIR, 'dirac_cones_sketch.pdf')
out_png = os.path.join(OUT_DIR, 'dirac_cones_sketch.png')
fig.savefig(out_pdf, dpi=150, bbox_inches='tight', facecolor=C_BG)
fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor=C_BG)
print(f'Saved: {out_pdf}')
print(f'Saved: {out_png}')
plt.close()
