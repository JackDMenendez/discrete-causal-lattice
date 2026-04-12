"""
phase_oscillator_diagram.py
Two-panel figure of the U(1) phase oscillator.

Left:  The group/algebra geometry — the oscillator as a clock hand on U(1),
       with the algebra generator omega as the arc between ticks.
Right: The probability geometry — how the half-angle delta_phi/2
       projects onto p_hop and p_stay, with three special cases marked.

Run from repo root:
    python src/utilities/phase_oscillator_diagram.py
Output: figures/phase_oscillator_diagram.pdf
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Arc, FancyArrowPatch
import matplotlib.patheffects as pe

# ── Style ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family':      'serif',
    'font.size':        11,
    'axes.linewidth':   0.8,
    'text.usetex':      False,
})

BLUE   = '#2166ac'
RED    = '#d6604d'
GREEN  = '#4dac26'
ORANGE = '#f4a582'
GREY   = '#888888'
BLACK  = '#111111'

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5.2))
fig.subplots_adjust(left=0.03, right=0.98, top=0.91, bottom=0.06, wspace=0.28)


# ═════════════════════════════════════════════════════════════════════════════
# LEFT PANEL: The U(1) clock — group element and algebra generator
# ═════════════════════════════════════════════════════════════════════════════

ax = ax1

# Unit circle
theta_full = np.linspace(0, 2*np.pi, 400)
ax.plot(np.cos(theta_full), np.sin(theta_full), color=GREY, lw=1.4, zorder=1)

# Axes (light)
ax.axhline(0, color=GREY, lw=0.6, ls='--', zorder=0)
ax.axvline(0, color=GREY, lw=0.6, ls='--', zorder=0)

# Current oscillator state r_n
phi_n = np.radians(55)
ax.plot([0, np.cos(phi_n)], [0, np.sin(phi_n)],
        color=BLUE, lw=2.2, zorder=3)
ax.plot(np.cos(phi_n), np.sin(phi_n), 'o',
        color=BLUE, ms=9, zorder=4, label=r'$r_n = e^{i\phi_n}$')

# Next oscillator state r_{n+1}
omega = np.radians(38)
phi_n1 = phi_n + omega
ax.plot([0, np.cos(phi_n1)], [0, np.sin(phi_n1)],
        color=BLUE, lw=2.2, ls='--', zorder=3, alpha=0.5)
ax.plot(np.cos(phi_n1), np.sin(phi_n1), 'o',
        color=BLUE, ms=9, zorder=4, mfc='white', mew=2,
        label=r'$r_{n+1} = e^{i(\phi_n+\omega)}$')

# Arc showing omega
arc_theta = np.linspace(phi_n, phi_n1, 60)
arc_r = 0.60
ax.plot(arc_r*np.cos(arc_theta), arc_r*np.sin(arc_theta),
        color=RED, lw=2.2, zorder=4)
# Arrow tip on arc
ax.annotate('', xy=(arc_r*np.cos(phi_n1-0.02), arc_r*np.sin(phi_n1-0.02)),
            xytext=(arc_r*np.cos(phi_n1-0.08), arc_r*np.sin(phi_n1-0.08)),
            arrowprops=dict(arrowstyle='->', color=RED, lw=2.0))
# omega label at arc midpoint
mid = (phi_n + phi_n1) / 2
ax.text(0.68*np.cos(mid), 0.68*np.sin(mid), r'$\omega$',
        color=RED, fontsize=14, ha='center', va='center', fontweight='bold')

# Tangent vector i*omega at r_n (Lie algebra lives in tangent space)
tang_angle = phi_n + np.pi/2   # tangent direction
tang_len   = 0.28
ax.annotate('', xy=(np.cos(phi_n) + tang_len*np.cos(tang_angle),
                    np.sin(phi_n) + tang_len*np.sin(tang_angle)),
            xytext=(np.cos(phi_n), np.sin(phi_n)),
            arrowprops=dict(arrowstyle='->', color=GREEN, lw=2.0))
ax.text(np.cos(phi_n) + (tang_len+0.10)*np.cos(tang_angle),
        np.sin(phi_n) + (tang_len+0.10)*np.sin(tang_angle),
        r'$i\omega \in \mathfrak{u}(1)$',
        color=GREEN, fontsize=10.5, ha='center', va='center')

# A=1 annotation on circle
ax.text(np.cos(np.radians(220))*1.11, np.sin(np.radians(220))*1.11,
        r'$|r|=1$  $(\mathcal{A}=1)$',
        color=GREY, fontsize=10, ha='center', va='center',
        style='italic')

# Labels for r_n and r_{n+1}
ax.text(np.cos(phi_n) + 0.13, np.sin(phi_n) + 0.09,
        r'$r_n$', color=BLUE, fontsize=12, fontweight='bold')
ax.text(np.cos(phi_n1) + 0.09, np.sin(phi_n1) + 0.11,
        r'$r_{n+1}$', color=BLUE, fontsize=11, alpha=0.7)

# phi_n angle arc (from real axis)
phi_arc = np.linspace(0, phi_n, 50)
ax.plot(0.22*np.cos(phi_arc), 0.22*np.sin(phi_arc), color=BLUE, lw=1.2, alpha=0.6)
ax.text(0.30, 0.10, r'$\phi_n$', color=BLUE, fontsize=10, alpha=0.7)

# Origin dot
ax.plot(0, 0, 'k.', ms=5, zorder=5)

ax.set_xlim(-1.45, 1.45)
ax.set_ylim(-1.45, 1.45)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('(a)  The U(1) oscillator\n'
             r'group element $e^{i\phi} \in \mathrm{U}(1)$,'
             r'  generator $\omega \in \mathfrak{u}(1)$',
             fontsize=11, pad=8)


# ═════════════════════════════════════════════════════════════════════════════
# RIGHT PANEL: The probability geometry — half-angle projection
# ═════════════════════════════════════════════════════════════════════════════

ax = ax2

# Unit circle
ax.plot(np.cos(theta_full), np.sin(theta_full), color=GREY, lw=1.4, zorder=1)

# Axes
ax.axhline(0, color=GREY, lw=0.6, ls='--', zorder=0)
ax.axvline(0, color=GREY, lw=0.6, ls='--', zorder=0)

# The half-angle point for a generic delta_phi
dphi = np.radians(68)       # representative delta_phi/2
half = dphi                  # we're plotting the half-angle directly

pt = np.array([np.cos(half), np.sin(half)])

# Radial line to the half-angle point
ax.plot([0, pt[0]], [0, pt[1]], color=BLACK, lw=2.0, zorder=3)
ax.plot(*pt, 'o', color=BLACK, ms=8, zorder=4)

# Projection onto real axis -> cos(delta_phi/2) -> p_hop
ax.plot([pt[0], pt[0]], [0, pt[1]], color=RED, lw=1.5, ls=':', zorder=2)
ax.plot([0, pt[0]], [0, 0], color=RED, lw=3.0, zorder=3, solid_capstyle='round')
ax.annotate('', xy=(pt[0], -0.18), xytext=(0, -0.18),
            arrowprops=dict(arrowstyle='<->', color=RED, lw=1.5))
ax.text(pt[0]/2, -0.30,
        r'$\cos\!\frac{\delta\phi}{2}$', color=RED,
        fontsize=11, ha='center', va='center')
ax.text(pt[0]/2, -0.47,
        r'$p_\mathrm{hop} = \cos^2\!\frac{\delta\phi}{2}$',
        color=RED, fontsize=10.5, ha='center', va='center')

# Projection onto imaginary axis -> sin(delta_phi/2) -> p_stay
ax.plot([pt[0], 0], [pt[1], pt[1]], color=BLUE, lw=1.5, ls=':', zorder=2)
ax.plot([0, 0], [0, pt[1]], color=BLUE, lw=3.0, zorder=3, solid_capstyle='round')
ax.annotate('', xy=(-0.20, pt[1]), xytext=(-0.20, 0),
            arrowprops=dict(arrowstyle='<->', color=BLUE, lw=1.5))
ax.text(-0.32, pt[1]/2,
        r'$\sin\!\frac{\delta\phi}{2}$',
        color=BLUE, fontsize=11, ha='center', va='center', rotation=90)
# p_stay label below the circle, left side
ax.text(0.10, -0.57,
        r'$p_\mathrm{stay} = \sin^2\!\!\frac{\delta\phi}{2}$',
        color=BLUE, fontsize=10.5, ha='center', va='center')

# Half-angle arc
half_arc = np.linspace(0, half, 60)
ax.plot(0.25*np.cos(half_arc), 0.25*np.sin(half_arc),
        color=BLACK, lw=1.5)
ax.annotate('', xy=(0.28*np.cos(half-0.03), 0.28*np.sin(half-0.03)),
            xytext=(0.28*np.cos(half-0.10), 0.28*np.sin(half-0.10)),
            arrowprops=dict(arrowstyle='->', color=BLACK, lw=1.3))
ax.text(0.35*np.cos(half/2), 0.35*np.sin(half/2)+0.05,
        r'$\delta\phi/2$', fontsize=10.5, ha='center', va='bottom')

# Three special cases
specials = [
    (0.0,      r'$\omega{=}0$: photon'+'\n'+r'$p_\mathrm{hop}{=}1$',
     RED,   0.06, -0.22),
    (np.pi/4,  r'$\omega{=}\pi/2$'+'\n'+r'$p_\mathrm{hop}{=}p_\mathrm{stay}{=}\frac{1}{2}$',
     GREEN, 0.22,  0.20),
    (np.pi/2,  r'$\omega{=}\pi$: frozen'+'\n'+r'$p_\mathrm{stay}{=}1$',
     BLUE,  0.25,  0.08),
]
for angle, label, color, dx, dy in specials:
    px, py = np.cos(angle), np.sin(angle)
    ax.plot(px, py, 'o', color=color, ms=10, zorder=5,
            mec='white', mew=1.5)
    ax.text(px+dx, py+dy, label, color=color, fontsize=9,
            ha='left', va='center', linespacing=1.5,
            bbox=dict(boxstyle='round,pad=0.25', fc='white', ec=color,
                      alpha=0.90, lw=0.9))

# Axis labels
ax.text(1.10, 0.05, r'$\mathrm{Re}$', fontsize=10, color=GREY)
ax.text(0.05, 1.10, r'$\mathrm{Im}$', fontsize=10, color=GREY)

# Origin
ax.plot(0, 0, 'k.', ms=5, zorder=5)

ax.set_xlim(-0.65, 1.75)
ax.set_ylim(-0.75, 1.35)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('(b)  The probability geometry\n'
             r'half-angle $\delta\phi/2$ projects onto $p_\mathrm{hop}$ and $p_\mathrm{stay}$',
             fontsize=11, pad=8)


# ── Save ──────────────────────────────────────────────────────────────────────
import os
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   '..', '..', 'figures', 'phase_oscillator_diagram.pdf')
fig.savefig(out, bbox_inches='tight', dpi=150)
print(f'Saved: {out}')

out_png = out.replace('.pdf', '.png')
fig.savefig(out_png, bbox_inches='tight', dpi=150)
print(f'Saved: {out_png}')
