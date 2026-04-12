"""
exp_09b_harmonic_analysis.py
Harmonic Spectrum Analysis of the A=1 CausalSession

PURPOSE:
Measure the actual frequency content of running sessions and compare against
theoretical predictions.  Any peak NOT in the theoretical list is a candidate
for emergent physics.

THEORETICAL FREQUENCIES (for a session with instruction frequency omega):
  f_zitt   = omega / (2*pi)       -- Zitterbewegung (psi_R <-> psi_L)
  f_vacuum = 0.5                  -- bipartite carrier (pi per tick)
  f_beat   = |0.5 - omega/(2*pi)| -- interference beat between particle + vacuum
  f_2nd    = 2 * omega / (2*pi)   -- second harmonic of Zitterbewegung

NOTE on degeneracies:
  At omega = pi/2 (prime qubit candidate): f_zitt = f_beat = 0.25 and
  f_2nd = f_vacuum = 0.5.  Only two distinct peaks predicted -- any extra
  peak at this omega is unambiguously emergent.
  At omega = 0 (photon) and omega = pi (max mass) all frequencies collapse
  to {0, 0.5}.

OBSERVABLES TRACKED (one time-series per tick):
  1. interior_fraction   -- mass proxy; should oscillate at f_zitt
  2. rgb_cmy_imbalance   -- charge/spin proxy (Bloch sphere z-axis)
  3. psi_R_total         -- right-handed sublattice amplitude sum
  4. psi_L_total         -- left-handed sublattice amplitude sum
  5. r_mean              -- probability-weighted mean orbital radius (confinement probe)

ANALYSIS:
  FFT each time series -> find peaks -> compare to theoretical list.
  Flag peaks > PEAK_THRESH sigma above noise floor that don't match theory.

QUBIT MODE ANALYSIS:
  For each omega the rgb_cmy_imbalance series IS the Bloch sphere z-axis.
  z_range measures natural oscillation between |psi_R> and |psi_L>.
  T2_ticks is the autocorrelation 1/e decay time -- the natural coherence time.
  omega = pi/2 is expected to be the best qubit: p_stay = 0.5, equal time on
  both sublattices, and the beat frequency is a rational fraction (1/4) of the
  vacuum carrier.

EXIT CODE:
  0  -- no emergent peaks found (theory confirmed, self-consistency check passes)
  1  -- emergent peaks found (investigate further; may indicate new physics)

Paper reference: notes/lattice_harmonics.md, notes/cone_modification_classes.md
"""

import sys, os, time
import numpy as np
from scipy import signal
from scipy.fft import rfft, rfftfreq

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession
from src.core.UnityConstraint import enforce_unity_spinor

# -- Configuration --------------------------------------------------------------

GRID       = 32          # larger grid to accommodate orbital radius
CENTER     = (16, 16, 16) # proton / well centre
N_TICKS    = 512         # power of 2 for clean FFT; more ticks = finer resolution
INTERIOR_R = 5           # radius for interior_fraction probe (near-proton density)
PEAK_THRESH = 3.0        # sigma above noise floor to call a peak "real"

# Coulomb confinement -- hydrogen-like well (calibrated in exp_12)
COULOMB_STRENGTH  = 30.0   # well depth (same as exp_12 hydrogen)
COULOMB_SOFTENING = 0.5    # softening radius (same as exp_12)
R1_APPROX         = 10     # approx ground-state orbital radius in nodes
BURN_IN           = 300    # ticks to let electron settle before recording

# Omega values to scan -- chosen to hit theoretically interesting points
OMEGA_SCAN = [
    0.0,             # photon (massless)
    np.pi / 6,       # light mass
    np.pi / 4,       # intermediate
    np.pi / 3,       # heavier
    np.pi / 2,       # p_stay=0.5, vacuum resonance candidate, best qubit
    2 * np.pi / 3,
    np.pi,           # maximum mass
]

# -- Core time series collector -------------------------------------------------

def collect_time_series(omega: float, n_ticks: int = N_TICKS) -> dict:
    """
    Run a single CausalSession for n_ticks and record all observables.

    Uses a hydrogen-like Coulomb well (STRENGTH=30) to confine the electron so
    that r_mean oscillates stably.  The electron starts at (cx+R1_APPROX, cy, cz)
    and BURN_IN ticks are discarded before recording begins.

    Precomputes the radial grid once outside the tick loop.
    Returns a dict of 1D arrays of length n_ticks.
    """
    cx, cy, cz = CENTER

    lattice = OctahedralLattice(GRID, GRID, GRID)
    lattice.set_coulomb_well(CENTER, COULOMB_STRENGTH, COULOMB_SOFTENING)

    # Initialise electron displaced by R1_APPROX along x from the well centre
    electron_start = (cx + R1_APPROX, cy, cz)
    session = CausalSession(lattice, electron_start, instruction_frequency=omega)

    # Precompute radial distance grid from proton position
    idx = np.arange(GRID)
    xg, yg, zg = np.meshgrid(idx, idx, idx, indexing='ij')
    r_grid = np.sqrt((xg - cx)**2 + (yg - cy)**2 + (zg - cz)**2)
    interior_mask = r_grid <= INTERIOR_R

    # Burn-in: let electron settle into bound state before recording
    for _ in range(BURN_IN):
        session.tick()
        session.advance_tick_counter()

    ts = {
        'interior_fraction': np.zeros(n_ticks),
        'rgb_cmy_imbalance': np.zeros(n_ticks),
        'psi_R_total':       np.zeros(n_ticks),
        'psi_L_total':       np.zeros(n_ticks),
        'r_mean':            np.zeros(n_ticks),
    }

    for t in range(n_ticks):
        session.tick()
        session.advance_tick_counter()

        P   = session.probability_density()
        p_R = float(np.sum(np.abs(session.psi_R)**2))
        p_L = float(np.sum(np.abs(session.psi_L)**2))

        ts['interior_fraction'][t] = float(P[interior_mask].sum())
        ts['rgb_cmy_imbalance'][t] = p_R - p_L
        ts['psi_R_total'][t]       = p_R
        ts['psi_L_total'][t]       = p_L
        ts['r_mean'][t]            = float(np.sum(P * r_grid))

    return ts


# -- FFT peak finder ------------------------------------------------------------

def _theoretical_freqs(omega: float) -> dict:
    f_zitt = omega / (2 * np.pi)
    return {
        'f_zitt':   f_zitt,
        'f_vacuum': 0.5,
        'f_beat':   abs(0.5 - f_zitt),
        'f_2nd':    2 * f_zitt,
    }


def find_peaks_fft(time_series: np.ndarray, label: str,
                   omega: float, n_ticks: int = N_TICKS,
                   verbose: bool = True) -> list:
    """
    FFT the time series, find peaks above noise floor, classify each as
    KNOWN (matches a theoretical frequency) or EMERGENT (does not).

    Returns list of (frequency, power, sigma, classification) tuples.
    """
    ts = time_series - time_series.mean()
    window   = np.hanning(n_ticks)
    spectrum = np.abs(rfft(ts * window))**2
    freqs    = rfftfreq(n_ticks)

    noise_floor = np.median(spectrum)
    noise_sigma = np.std(spectrum[spectrum < 10 * noise_floor])

    peak_idx, _ = signal.find_peaks(
        spectrum,
        height   = noise_floor + PEAK_THRESH * noise_sigma,
        distance = max(1, n_ticks // 128),
    )

    known     = _theoretical_freqs(omega)
    tolerance = 5.0 / n_ticks   # two frequency bin widths (allows slight peak shifts)

    results = []
    for idx in peak_idx:
        f     = freqs[idx]
        power = spectrum[idx]
        sigma = (power - noise_floor) / (noise_sigma + 1e-30)

        match = None
        for name, f_theory in known.items():
            if abs(f - f_theory) < tolerance:
                match = name
                break

        cls = match if match else 'EMERGENT'
        results.append((f, power, sigma, cls))

    if verbose:
        print(f"\n  [{label}]  omega/pi={omega/np.pi:.3f}")
        if not results:
            print("    (no peaks above threshold)")
        for f, power, sigma, cls in sorted(results, key=lambda x: -x[1]):
            flag = '  *** EMERGENT ***' if cls == 'EMERGENT' else ''
            print(f"    f={f:.4f} cyc/tick  sigma={sigma:.1f}  [{cls}]{flag}")

    return results


# -- Qubit mode analysis --------------------------------------------------------

def qubit_mode_analysis(omega: float, ts: dict,
                        verbose: bool = True) -> dict:
    """
    Identify the two dominant harmonic modes at this omega using an already-
    collected time series (passed in to avoid recomputing).

    The rgb_cmy_imbalance series IS the Bloch sphere z-axis:
      |0> = psi_R-dominant (RGB sublattice)
      |1> = psi_L-dominant (CMY sublattice)

    T2_ticks: autocorrelation 1/e decay time of the imbalance oscillation.
    z_range:  max - min of imbalance (0 = no qubit flip, 1 = full flip).
    """
    imbalance = ts['rgb_cmy_imbalance']
    z_range   = float(imbalance.max() - imbalance.min())
    z_mean    = float(imbalance.mean())

    # Autocorrelation decay -> T2
    ac = np.correlate(imbalance - z_mean, imbalance - z_mean, mode='full')
    ac = ac[len(ac) // 2:]
    ac /= (ac[0] + 1e-12)
    T2 = N_TICKS
    for i, v in enumerate(ac):
        if v < 1.0 / np.e:
            T2 = i
            break

    peaks      = find_peaks_fft(imbalance, 'imbalance', omega, verbose=False)
    top_modes  = sorted(peaks, key=lambda x: -x[1])[:2]
    p_stay     = float(np.sin(omega / 2)**2)
    cone_deg   = float(np.degrees(np.arcsin(np.cos(omega / 2))))

    result = {
        'omega':          omega,
        'z_mean':         z_mean,
        'z_range':        z_range,
        'T2_ticks':       T2,
        'top_modes':      top_modes,
        'p_stay':         p_stay,
        'cone_angle_deg': cone_deg,
    }

    if verbose:
        print(f"\n  QUBIT  omega/pi={omega/np.pi:.3f}  "
              f"p_stay={p_stay:.4f}  cone={cone_deg:.1f} deg")
        print(f"    Bloch z range = {z_range:.4f}  "
              f"({'full flip' if z_range > 0.5 else 'partial' if z_range > 0.05 else 'no flip'})")
        print(f"    T2 estimate   = {T2} ticks  "
              f"({'stable' if T2 == N_TICKS else 'decaying'})")
        if top_modes:
            for f, power, sigma, cls in top_modes:
                print(f"    dominant mode  f={f:.4f}  sigma={sigma:.1f}  [{cls}]")

    return result


# -- Main scan ------------------------------------------------------------------

def run_harmonic_scan(verbose: bool = True) -> tuple:
    """
    Full harmonic scan across all omega values.
    Reports all peaks, flags emergent ones, runs qubit mode analysis.
    Returns (all_emergent, qubit_summary).
    """
    print("=" * 65)
    print("EXPERIMENT: Harmonic Analysis -- A=1 CausalSession Spectral Scan")
    print("=" * 65)
    print(f"  Grid: {GRID}^3   N_ticks: {N_TICKS}   "
          f"freq resolution: {1/N_TICKS:.5f} cyc/tick")
    print(f"  Peak threshold: {PEAK_THRESH} sigma above noise floor")
    print(f"  Observables: interior_fraction, rgb_cmy_imbalance, "
          f"psi_R_total, r_mean")

    all_emergent  = []
    qubit_summary = []
    t_total       = time.time()

    for omega in OMEGA_SCAN:
        t0 = time.time()
        print(f"\n{'-'*55}")
        print(f"  omega = {omega:.4f}  ({omega/np.pi:.3f}*pi)  "
              f"p_stay = {np.sin(omega/2)**2:.4f}")

        # Collect time series ONCE per omega -- reused for all analyses
        ts = collect_time_series(omega)
        print(f"  [burn-in {BURN_IN} + recorded {N_TICKS} ticks in {time.time()-t0:.1f}s]")

        # FFT each observable -- reuse ts
        for obs_name in ['interior_fraction', 'rgb_cmy_imbalance',
                         'psi_R_total', 'r_mean']:
            peaks    = find_peaks_fft(ts[obs_name], obs_name, omega,
                                      verbose=verbose)
            emergent = [(omega, obs_name, f, power, sigma)
                        for f, power, sigma, cls in peaks
                        if cls == 'EMERGENT']
            all_emergent.extend(emergent)

        # Qubit analysis reuses same ts
        qr = qubit_mode_analysis(omega, ts, verbose=verbose)
        qubit_summary.append(qr)

    elapsed = time.time() - t_total

    # -- Summary ---------------------------------------------------------------
    print("\n" + "=" * 65)
    print("EMERGENT PEAK SUMMARY  (peaks not matching theory)")
    print("=" * 65)
    if not all_emergent:
        print("  None found -- lattice harmonics match theory exactly.")
        print("  (Positive result: framework is spectrally self-consistent.)")
    else:
        print(f"  Found {len(all_emergent)} emergent peak(s):\n")
        for omega, obs, f, power, sigma in sorted(all_emergent,
                                                   key=lambda x: -x[3]):
            print(f"  omega/pi={omega/np.pi:.3f}  obs={obs:22s}  "
                  f"f={f:.4f}  sigma={sigma:.1f}")
        print("\n  Candidates for:")
        print("    - Higher-order lattice resonances (geometric harmonics)")
        print("    - Sublattice cross-coupling (nonlinear mixing)")
        print("    - Precursors to phase transitions at specific omega values")

    print("\n" + "=" * 65)
    print("QUBIT ENGINEERING SUMMARY")
    print("=" * 65)
    print(f"  {'omega/pi':>8}  {'p_stay':>7}  {'cone_deg':>9}  "
          f"{'z_range':>8}  {'T2_ticks':>9}")
    print("  " + "-" * 50)
    for qr in qubit_summary:
        stable = '*' if qr['T2_ticks'] == N_TICKS else ' '
        print(f"  {qr['omega']/np.pi:8.3f}  {qr['p_stay']:7.4f}  "
              f"{qr['cone_angle_deg']:9.2f}  "
              f"{qr['z_range']:8.4f}  {qr['T2_ticks']:9d} {stable}")
    print(f"\n  * = coherence maintained full {N_TICKS}-tick run")
    print(f"  z_range ~ 1.0  -> full psi_R/psi_L flip (natural qubit)")
    print(f"  z_range ~ 0.0  -> no flip (photon or max-mass state)")
    print(f"\n  Total time: {elapsed:.0f}s")

    if all_emergent:
        print("\n[AUDIT PARTIAL] Emergent peaks found -- see summary above.")
    else:
        print("\n[AUDIT PASSED] No emergent peaks; theory confirmed.")

    return all_emergent, qubit_summary


# -- Harmonic landscape plot ----------------------------------------------------

def plot_harmonic_landscape(fig_path: str = None,
                            cached_ts: dict = None) -> None:
    """
    Heatmap of spectral power vs (omega, frequency) across the full omega scan.
    Each row is one omega value; bright spots are peaks; theoretical
    frequencies overlaid as coloured markers.

    cached_ts: dict mapping omega -> time_series dict (avoids recomputation).
    If None, time series are collected fresh (slow -- use when plotting only).
    """
    try:
        import matplotlib
        if fig_path:
            matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
    except ImportError:
        print("matplotlib not available -- pip install matplotlib")
        return

    n_omega = len(OMEGA_SCAN)
    freqs   = rfftfreq(N_TICKS)
    n_freq  = len(freqs)
    power_map = np.zeros((n_omega, n_freq))

    for i, omega in enumerate(OMEGA_SCAN):
        if cached_ts is not None and omega in cached_ts:
            ts = cached_ts[omega]
        else:
            ts = collect_time_series(omega)
        obs    = ts['rgb_cmy_imbalance'] - ts['rgb_cmy_imbalance'].mean()
        window = np.hanning(N_TICKS)
        spec   = np.abs(rfft(obs * window))**2
        power_map[i] = np.log10(spec + 1e-10)

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#111111')
    ax.set_facecolor('#111111')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    for spine in ax.spines.values():
        spine.set_edgecolor('white')

    im = ax.imshow(power_map, aspect='auto', origin='lower',
                   extent=[freqs[0], freqs[-1], 0, n_omega],
                   cmap='inferno', interpolation='bilinear')
    plt.colorbar(im, ax=ax, label='log\u2081\u2080(spectral power)')

    ax.set_yticks(np.arange(n_omega) + 0.5)
    ax.set_yticklabels([f'{o/np.pi:.3f}\u03c0' for o in OMEGA_SCAN],
                       color='white')

    for i, omega in enumerate(OMEGA_SCAN):
        y = i + 0.5
        tf = _theoretical_freqs(omega)
        colors = {'f_zitt': 'cyan', 'f_vacuum': 'lime',
                  'f_beat': 'yellow', 'f_2nd': 'orange'}
        for name, f in tf.items():
            if 0 <= f <= 0.5:
                ax.plot(f, y, 'o', color=colors[name],
                        markersize=6, alpha=0.85, zorder=5)
        # f_3rd = 3 * f_zitt
        f_3rd = 3 * omega / (2 * np.pi)
        if 0 <= f_3rd <= 0.5:
            ax.plot(f_3rd, y, 's', color='magenta',
                    markersize=5, alpha=0.75, zorder=5)

    # -- Resonance lock-in bands and markers ------------------------------------
    # omega = pi/4 : 4:1 resonance -- f_vacuum = 4*f_zitt, f_3rd = f_beat = 3/8
    # omega = pi/3 : 3:1 resonance -- f_vacuum = 3*f_zitt, f_2nd = f_beat = 1/3
    # Lock-in coincidence stars
    lock_points = [
        (3/8,  2.5, '4:1'),   # pi/4: f_3rd = f_beat
        (1/3,  3.5, '3:1'),   # pi/3: f_2nd = f_beat
        (0.5,  3.5, ''),      # pi/3: f_3rd = f_vac (already on f_vac dot)
    ]
    for f_lock, y_lock, lbl in lock_points:
        ax.plot(f_lock, y_lock, '*', color='white',
                markersize=14, zorder=6, alpha=0.9)
        if lbl:
            ax.annotate(lbl,
                        xy=(f_lock, y_lock),
                        xytext=(f_lock + 0.012, y_lock + 0.14),
                        color='white', fontsize=8, alpha=0.9, zorder=7)

    legend_elements = [
        Line2D([0],[0], marker='o', color='w', markerfacecolor='cyan',
               label='f_zitt (\u03c9/(2\u03c0))', markersize=7),
        Line2D([0],[0], marker='o', color='w', markerfacecolor='lime',
               label='f_vacuum (0.5)', markersize=7),
        Line2D([0],[0], marker='o', color='w', markerfacecolor='yellow',
               label='f_beat (|\u00bd\u2212f_zitt|)', markersize=7),
        Line2D([0],[0], marker='o', color='w', markerfacecolor='orange',
               label='f_2nd (2\u03c9/(2\u03c0))', markersize=7),
        Line2D([0],[0], marker='s', color='w', markerfacecolor='magenta',
               label='f_3rd (3\u03c9/(2\u03c0))', markersize=6),
        Line2D([0],[0], marker='*', color='w', markerfacecolor='white',
               label='harmonic lock-in', markersize=10),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=9,
              facecolor='#222222', labelcolor='white', framealpha=0.8)

    ax.set_xlabel('Frequency (cycles / tick)', fontsize=11, color='white')
    ax.set_ylabel('Instruction frequency \u03c9', fontsize=11, color='white')
    ax.set_title(
        'Harmonic Fingerprint of A=1 CausalSession\n'
        'Spectral power of rgb\\_cmy\\_imbalance(t)  --  '
        'coloured dots = theoretical frequencies',
        fontsize=11, color='white'
    )

    plt.tight_layout()
    if fig_path:
        plt.savefig(fig_path, dpi=150, bbox_inches='tight',
                    facecolor=fig.get_facecolor())
        print(f"Saved: {fig_path}")
    else:
        plt.show()


# -- Entry point ----------------------------------------------------------------

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--fig', default=None,
                    help='Save harmonic landscape plot to this path')
    ap.add_argument('--quiet', action='store_true',
                    help='Suppress per-peak output (summary only)')
    args = ap.parse_args()

    emergent, qubit_data = run_harmonic_scan(verbose=not args.quiet)

    if args.fig:
        print(f"\nGenerating harmonic landscape plot...")
        # Build cache from a fresh run so plot_harmonic_landscape
        # does not recompute all time series a third time.
        ts_cache = {}
        for omega in OMEGA_SCAN:
            ts_cache[omega] = collect_time_series(omega)
        plot_harmonic_landscape(fig_path=args.fig, cached_ts=ts_cache)

    # 0 = no emergent peaks (theory confirmed)
    # 1 = emergent peaks found (investigate)
    sys.exit(1 if emergent else 0)
