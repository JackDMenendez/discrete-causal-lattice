"""
exp_harmonic_hires.py
High-resolution harmonic landscape scan -- Arnold tongue / Farey structure test

Runs 150 evenly-spaced omega values between 0 and pi and plots the spectral
power of rgb_cmy_imbalance as a heatmap.  At this resolution the Arnold tongue
structure (if present) should be visible as a fractal density pattern: bright
resonance bands getting smaller and more numerous near irrational omegas.

No Coulomb confinement, no burn-in -- free particle only, so each omega value
takes ~7s.  Total runtime: ~18 minutes.

Theoretical frequency overlays:
  f_zitt   = omega / (2*pi)       cyan dots
  f_vacuum = 0.5                  lime dots
  f_beat   = |0.5 - f_zitt|       yellow dots
  f_2nd    = 2 * f_zitt           orange dots
  f_3rd    = 3 * f_zitt           magenta squares

Resonance lock-in markers (white stars):
  omega = pi/4 : 4:1  f_3rd = f_beat = 3/8
  omega = pi/3 : 3:1  f_2nd = f_beat = 1/3
  omega = pi/2 : 2:1  f_zitt = f_beat = 1/4
"""

import sys, os, time
import numpy as np
from scipy.fft import rfft, rfftfreq

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession

# -- Configuration --------------------------------------------------------------

GRID        = 24
CENTER      = (12, 12, 12)
N_TICKS     = 512
N_OMEGA     = 150          # number of omega values between 0 and pi (exclusive)
_HERE       = os.path.dirname(os.path.abspath(__file__))
FIG_PATH    = os.path.join(_HERE, '..', '..', 'paper', 'figures', 'exp_harmonic_hires.pdf')

OMEGA_SCAN  = np.linspace(0.0, np.pi, N_OMEGA + 2)[1:-1]  # exclude 0 and pi endpoints

# Known resonance omegas for markers
RESONANCES = [
    (np.pi / 4, 3/8,  '4:1'),
    (np.pi / 3, 1/3,  '3:1'),
    (np.pi / 2, 0.25, '2:1'),
]

# -- Time series collector (free particle, rgb_cmy_imbalance only) -------------

def collect_imbalance(omega):
    lattice = OctahedralLattice(GRID, GRID, GRID)
    session = CausalSession(lattice, CENTER, instruction_frequency=omega)
    ts = np.zeros(N_TICKS)
    for t in range(N_TICKS):
        session.tick()
        session.advance_tick_counter()
        p_R = float(np.sum(np.abs(session.psi_R)**2))
        p_L = float(np.sum(np.abs(session.psi_L)**2))
        ts[t] = p_R - p_L
    return ts


# -- Main -----------------------------------------------------------------------

def run():
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
    except ImportError:
        print("matplotlib not available")
        return

    freqs   = rfftfreq(N_TICKS)
    n_freq  = len(freqs)
    power_map = np.zeros((N_OMEGA, n_freq))

    t_start = time.time()
    for i, omega in enumerate(OMEGA_SCAN):
        ts     = collect_imbalance(omega)
        ts    -= ts.mean()
        window = np.hanning(N_TICKS)
        spec   = np.abs(rfft(ts * window))**2
        power_map[i] = np.log10(spec + 1e-10)

        elapsed = time.time() - t_start
        eta     = elapsed / (i + 1) * (N_OMEGA - i - 1)
        print(f"  {i+1:3d}/{N_OMEGA}  omega/pi={omega/np.pi:.4f}  "
              f"elapsed={elapsed:.0f}s  eta={eta:.0f}s", flush=True)

    # -- Plot ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor('#111111')
    ax.set_facecolor('#111111')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    for spine in ax.spines.values():
        spine.set_edgecolor('white')

    im = ax.imshow(power_map, aspect='auto', origin='lower',
                   extent=[freqs[0], freqs[-1], 0, N_OMEGA],
                   cmap='inferno', interpolation='bilinear')
    plt.colorbar(im, ax=ax, label='log\u2081\u2080(spectral power)')

    # Y-axis: label every 10th omega row
    tick_idx  = np.arange(0, N_OMEGA, 10)
    tick_vals = OMEGA_SCAN[tick_idx]
    ax.set_yticks(tick_idx + 0.5)
    ax.set_yticklabels([f'{o/np.pi:.3f}\u03c0' for o in tick_vals],
                       color='white', fontsize=7)

    # Theoretical frequency dots
    dot_colors = {'f_zitt': 'cyan', 'f_vacuum': 'lime',
                  'f_beat': 'yellow', 'f_2nd': 'orange'}
    for i, omega in enumerate(OMEGA_SCAN):
        y       = i + 0.5
        f_zitt  = omega / (2 * np.pi)
        f_beat  = abs(0.5 - f_zitt)
        f_2nd   = 2 * f_zitt
        f_3rd   = 3 * f_zitt
        for name, f in [('f_zitt', f_zitt), ('f_vacuum', 0.5),
                        ('f_beat', f_beat), ('f_2nd', f_2nd)]:
            if 0 < f < 0.5:
                ax.plot(f, y, '.', color=dot_colors[name],
                        markersize=2, alpha=0.6, zorder=5)
        if 0 < f_3rd < 0.5:
            ax.plot(f_3rd, y, 's', color='magenta',
                    markersize=1.5, alpha=0.6, zorder=5)

    # Resonance stars
    for omega_res, f_lock, lbl in RESONANCES:
        # Find nearest row index
        i_res = int(np.argmin(np.abs(OMEGA_SCAN - omega_res)))
        y_res = i_res + 0.5
        ax.plot(f_lock, y_res, '*', color='white',
                markersize=12, zorder=6, alpha=0.95)
        ax.annotate(lbl,
                    xy=(f_lock, y_res),
                    xytext=(f_lock + 0.01, y_res + 1.2),
                    color='white', fontsize=8, alpha=0.95, zorder=7)

    legend_elements = [
        Line2D([0],[0], marker='.', color='w', markerfacecolor='cyan',
               label='f_zitt', markersize=6),
        Line2D([0],[0], marker='.', color='w', markerfacecolor='lime',
               label='f_vacuum (0.5)', markersize=6),
        Line2D([0],[0], marker='.', color='w', markerfacecolor='yellow',
               label='f_beat', markersize=6),
        Line2D([0],[0], marker='.', color='w', markerfacecolor='orange',
               label='f_2nd', markersize=6),
        Line2D([0],[0], marker='s', color='w', markerfacecolor='magenta',
               label='f_3rd', markersize=5),
        Line2D([0],[0], marker='*', color='w', markerfacecolor='white',
               label='resonance lock-in', markersize=10),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=8,
              facecolor='#222222', labelcolor='white', framealpha=0.8)

    ax.set_xlabel('Frequency (cycles / tick)', fontsize=11, color='white')
    ax.set_ylabel('Instruction frequency \u03c9', fontsize=11, color='white')
    ax.set_title(
        'Harmonic Fingerprint -- High Resolution Omega Scan  (N=150)\n'
        'rgb_cmy_imbalance spectral power  --  Arnold tongue / Farey structure test',
        fontsize=11, color='white'
    )

    plt.tight_layout()
    plt.savefig(FIG_PATH, dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    print(f"\nSaved: {FIG_PATH}")
    print(f"Total time: {time.time()-t_start:.0f}s")

    # Save raw data for overlay scripts
    data_path = os.path.join(_HERE, '..', '..', 'data', 'exp_harmonic_hires_powermap.npy')
    np.save(data_path, power_map)
    print(f"Saved power_map: {data_path}")


if __name__ == '__main__':
    run()
