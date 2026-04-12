"""
dirac_cones_doublepane.py
Double-pane figure:
  Left  — raw harmonic landscape (exp_harmonic_hires)
  Right — same heatmap with Dirac cone annotations + graphene inset

Requires: data/exp_harmonic_hires_powermap.npy

Run from repo root:
    python src/utilities/dirac_cones_doublepane.py
Saves: figures/dirac_cones_doublepane.pdf  +  .png
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

_ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_NPY = os.path.join(_ROOT, 'data', 'exp_harmonic_hires_powermap.npy')
OUT_DIR  = os.path.join(_ROOT, 'figures')

N_OMEGA = 150
N_TICKS = 512
C_BG    = '#111111'
C_TEXT  = 'white'

# ── Coordinate conversion ──────────────────────────────────────────────────────
def omega_to_y(omega):
    return omega * 151.0 / np.pi - 0.5

# ── Dispersion lines ───────────────────────────────────────────────────────────
f_arr = np.linspace(0, 0.5, 500)

lines = [
    dict(x=f_arr, y=302*f_arr - 0.5,
         color='#2299dd', lw=1.8, ls='-',
         label=r'$f_\mathrm{zitt} = \omega/2\pi$'),
    dict(x=f_arr, y=150.5 - 302*f_arr,
         color='#dd8800', lw=1.8, ls='-',
         label=r'$f_\mathrm{beat} = \frac{1}{2}-\omega/2\pi$'),
    dict(x=f_arr, y=151*f_arr - 0.5,
         color='#22aa44', lw=2.0, ls='--',
         label=r'$f_\mathrm{2nd} = \omega/\pi$'),
    dict(x=f_arr, y=(302/3)*f_arr - 0.5,
         color='#ee44ee', lw=2.0, ls=':',
         label=r'$f_\mathrm{3rd} = 3\omega/2\pi$'),
]
for ln in lines:
    mask = (ln['y'] >= 0) & (ln['y'] <= N_OMEGA)
    ln['x'] = ln['x'][mask]
    ln['y'] = ln['y'][mask]

# ── Crossing points ────────────────────────────────────────────────────────────
crossings = [
    dict(f=0.250, y=omega_to_y(np.pi/2),
         label='2:1\n$\\omega=\\pi/2$', color='white',
         lxy=(0.11, omega_to_y(np.pi/2) + 18)),
    dict(f=1/3,   y=omega_to_y(np.pi/3),
         label='3:1\n$\\omega=\\pi/3$', color='#88ff88',
         lxy=(0.13, omega_to_y(np.pi/3) - 16)),
    dict(f=3/8,   y=omega_to_y(np.pi/4),
         label='4:1\n$\\omega=\\pi/4$', color='#ffaaff',
         lxy=(0.46, omega_to_y(np.pi/4) - 14)),
]

# ── Cone specs ─────────────────────────────────────────────────────────────────
cone_specs = [
    dict(fc=0.250, yc=omega_to_y(np.pi/2), s1= 302,   s2=-302, size=0.020, color='white'),
    dict(fc=1/3,   yc=omega_to_y(np.pi/3), s1= 151,   s2=-302, size=0.020, color='#88ff88'),
    dict(fc=3/8,   yc=omega_to_y(np.pi/4), s1= 302/3, s2=-302, size=0.020, color='#ffaaff'),
]


def draw_cone(ax, fc, yc, s1, s2, size, color, alpha=0.32):
    df = np.linspace(0, size, 80)
    ax.fill_between(fc + df, yc + s1*df, yc + s2*df,
                    color=color, alpha=alpha, linewidth=0, zorder=4)
    ax.fill_between(fc - df, yc - s1*df, yc - s2*df,
                    color=color, alpha=alpha, linewidth=0, zorder=4)
    df_full = np.linspace(-size, size, 160)
    ax.plot(fc + df_full, yc + s1*df_full, color=color, lw=1.8, alpha=0.90, zorder=5)
    ax.plot(fc + df_full, yc + s2*df_full, color=color, lw=1.8, alpha=0.90, zorder=5)
    ax.plot(fc, yc, 'o', color=color, markersize=6, zorder=6,
            markeredgecolor='white', markeredgewidth=0.7)


def draw_graphene_inset(ax_main):
    ax_in = ax_main.inset_axes([0.67, 0.67, 0.31, 0.31])
    k = np.linspace(-1, 1, 200)
    ax_in.plot(k,  np.abs(k), color='#2299dd', lw=2.0)
    ax_in.plot(k, -np.abs(k), color='#dd8800', lw=2.0)
    ax_in.fill_between(k[k >= 0],  k[k >= 0], -k[k >= 0], alpha=0.18, color='white')
    ax_in.fill_between(k[k <= 0], -k[k <= 0],  k[k <= 0], alpha=0.18, color='white')
    ax_in.plot(0, 0, 'o', color='white', markersize=5, zorder=5)
    ax_in.axhline(0, color='#555555', lw=0.6, ls='--')
    ax_in.axvline(0, color='#555555', lw=0.6, ls='--')
    ax_in.annotate('Dirac\npoint', xy=(0.05, 0.05), xytext=(0.4, 0.42),
                   color='white', fontsize=6,
                   arrowprops=dict(arrowstyle='->', color='white', lw=0.7),
                   ha='center')
    ax_in.set_xlim(-1, 1);  ax_in.set_ylim(-1, 1)
    ax_in.set_xticks([-1, 0, 1])
    ax_in.set_xticklabels(['$-k$', '0', '$+k$'], color=C_TEXT, fontsize=6)
    ax_in.set_yticks([-1, 0, 1])
    ax_in.set_yticklabels(['$-E$', '0', '$+E$'], color=C_TEXT, fontsize=6)
    ax_in.tick_params(colors=C_TEXT, labelsize=6, length=2)
    ax_in.set_xlabel('$k$', color=C_TEXT, fontsize=7, labelpad=1)
    ax_in.set_ylabel('$E$', color=C_TEXT, fontsize=7, labelpad=1)
    ax_in.set_title('Graphene K-point\n(spin-½, 2 bands)', color=C_TEXT, fontsize=7, pad=3)
    ax_in.set_facecolor('#1a1a2e')
    for spine in ax_in.spines.values():
        spine.set_edgecolor('#8888aa')
        spine.set_linewidth(0.9)


def style_ax(ax, title):
    OMEGA_SCAN = np.linspace(0, np.pi, N_OMEGA + 2)[1:-1]
    tick_idx   = np.array([0, 25, 37, 50, 75, 100, 125, 149])
    ax.set_yticks(tick_idx + 0.5)
    ax.set_yticklabels([f'{OMEGA_SCAN[i]/np.pi:.3f}π' for i in tick_idx],
                       color=C_TEXT, fontsize=8)
    x_ticks  = [0, 0.125, 0.25, 1/3, 0.375, 0.5]
    x_labels = ['0', '⅛', '¼', '⅓', '⅜', '½']
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels, color=C_TEXT, fontsize=8)
    ax.tick_params(colors=C_TEXT, which='both')
    for spine in ax.spines.values():
        spine.set_edgecolor('#555555')
    ax.set_xlim(0, 0.5)
    ax.set_ylim(0, N_OMEGA)
    ax.set_xlabel('Frequency $f$ (cycles / tick)', color=C_TEXT, fontsize=10)
    ax.set_ylabel('Instruction frequency $\\omega$', color=C_TEXT, fontsize=10)
    ax.set_title(title, color=C_TEXT, fontsize=10, pad=6)


# ── Build figure ───────────────────────────────────────────────────────────────
if not os.path.exists(DATA_NPY):
    raise FileNotFoundError(f'Missing {DATA_NPY} — run exp_09c_harmonic_hires.py first')

from scipy.fft import rfftfreq
power_map = np.load(DATA_NPY)
freqs     = rfftfreq(N_TICKS)
vmin, vmax = np.percentile(power_map, [2, 98])   # consistent colour scale both panels

fig = plt.figure(figsize=(18, 8))
fig.patch.set_facecolor(C_BG)
gs  = fig.add_gridspec(1, 3, width_ratios=[1, 1, 0.04], wspace=0.08)
ax_L  = fig.add_subplot(gs[0])
ax_R  = fig.add_subplot(gs[1])
ax_cb = fig.add_subplot(gs[2])

for ax in (ax_L, ax_R):
    ax.set_facecolor(C_BG)
    im = ax.imshow(power_map, aspect='auto', origin='lower',
                   extent=[freqs[0], freqs[-1], 0, N_OMEGA],
                   cmap='inferno', interpolation='bilinear',
                   vmin=vmin, vmax=vmax, zorder=1)

# shared colourbar in its own column — both data panels stay equal width
cbar = fig.colorbar(im, cax=ax_cb,
                    label='log₁₀(probability density)  [A=1]')
cbar.ax.yaxis.label.set_color(C_TEXT)
cbar.ax.tick_params(colors=C_TEXT)

# ── LEFT panel — raw ──────────────────────────────────────────────────────────
style_ax(ax_L, '(a)  Raw harmonic landscape')
# resonance star markers only — no lines
for omega_res, f_lock in [(np.pi/2, 0.25), (np.pi/3, 1/3), (np.pi/4, 3/8)]:
    ax_L.plot(f_lock, omega_to_y(omega_res), '*',
              color='white', markersize=11, zorder=6, alpha=0.9)

# ── RIGHT panel — annotated ───────────────────────────────────────────────────
style_ax(ax_R, '(b)  Dirac-like band crossings')
ax_R.yaxis.set_ticklabels([])           # suppress duplicate y labels
ax_R.set_ylabel('')

for ln in lines:
    ax_R.plot(ln['x'], ln['y'], color=ln['color'], lw=ln['lw'],
              ls=ln['ls'], label=ln['label'], zorder=3, alpha=0.85)

for cs in cone_specs:
    draw_cone(ax_R, cs['fc'], cs['yc'], cs['s1'], cs['s2'], cs['size'], cs['color'])

for c in crossings:
    ax_R.annotate(c['label'],
                  xy=(c['f'], c['y']),
                  xytext=c['lxy'],
                  color=c['color'], fontsize=8.5, ha='center', va='center',
                  arrowprops=dict(arrowstyle='->', color=c['color'], lw=0.9),
                  bbox=dict(boxstyle='round,pad=0.3', facecolor=C_BG,
                            edgecolor=c['color'], alpha=0.88, linewidth=0.9),
                  zorder=7)

ax_R.legend(loc='upper left', fontsize=7.5, framealpha=0.75,
            facecolor=C_BG, edgecolor='#555555', labelcolor=C_TEXT)

draw_graphene_inset(ax_R)

# ── Save ───────────────────────────────────────────────────────────────────────
out_pdf = os.path.join(OUT_DIR, 'dirac_cones_doublepane.pdf')
out_png = os.path.join(OUT_DIR, 'dirac_cones_doublepane.png')
fig.savefig(out_pdf, dpi=150, facecolor=C_BG)
fig.savefig(out_png, dpi=150, facecolor=C_BG)
print(f'Saved: {out_pdf}')
print(f'Saved: {out_png}')
plt.close()
