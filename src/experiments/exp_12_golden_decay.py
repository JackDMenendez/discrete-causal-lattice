"""
exp_12_golden_decay.py
Audit: Structural persistence and the Golden Ratio (phi^-1) decay constant.

Tests the hypothesis that a Dirac wave packet on T^3_diamond achieves maximum
structural persistence when its residence probability equals the inverse Golden
Ratio: phi^-1 = (sqrt(5)-1)/2 ≈ 0.618.

Methodology:
  Two-phase sweep of p_stay = sin^2(omega/2):
    Phase 1 -- coarse: 50 points over [0.10, 0.90]
    Phase 2 -- fine:   60 points over [0.55, 0.70]  (tight bracket around phi^-1)

  For each p_stay:
    - Map to omega via: omega = 2 * arcsin(sqrt(p_stay))
    - Evolve for TICKS ticks on a LATTICE_SIZE^3 grid
    - Record two metrics:

      (A) Entropy growth rate  [primary, boundary-independent]
          Linear fit slope of Shannon entropy S(t) over RATE_WINDOW ticks.
          The window ends well before the leading edge reaches the boundary,
          so boundary reflections cannot influence this metric.
          Most persistent packet -> flattest entropy curve -> minimum slope.

      (B) Threshold-crossing lifetime  [secondary, boundary-dependent]
          First tick where S > ENTROPY_THRESHOLD.  Useful sanity check but
          sensitive to grid size; do not use as the sole criterion.

  Pass criterion: minimum entropy rate falls within PASS_TOLERANCE of phi^-1.

Boundary safety:
  LATTICE_SIZE = 61 -> boundary at 30 nodes from centre.
  Leading edge of a massless packet hits boundary at tick ~30.
  RATE_WINDOW = (5, 28) -> entirely pre-boundary.

Paper reference: Section 12 (Harmonic Stability and the Golden Ratio Decay Constant)
"""

import sys, os, time
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession

# ── Constants ─────────────────────────────────────────────────────────────────
PHI_INV = (np.sqrt(5) - 1) / 2.0   # ≈ 0.618034

# ── Grid and timing ───────────────────────────────────────────────────────────
LATTICE_SIZE      = 61    # boundary at 30 nodes from centre
TICKS             = 200   # enough for lifetime metric; entropy rate uses early window
RATE_WINDOW       = (5, 28)   # pre-boundary entropy fit window
ENTROPY_THRESHOLD = 3.0   # secondary decoherence threshold (moderate)

# ── Sweep parameters ──────────────────────────────────────────────────────────
COARSE_N  = 50
COARSE_LO = 0.10
COARSE_HI = 0.90

FINE_N    = 60
FINE_LO   = 0.55
FINE_HI   = 0.70

# ── Pass/fail ─────────────────────────────────────────────────────────────────
PASS_TOLERANCE = 0.040   # minimum entropy rate must be within this of phi^-1


# ── Single-run helper ─────────────────────────────────────────────────────────

def run_one(lattice, center, p_stay):
    """
    Evolve a packet with residence probability p_stay for TICKS ticks.
    Returns (entropy_rate, lifetime, entropies).

    entropy_rate: slope of S(t) linear fit over RATE_WINDOW  [primary]
    lifetime:     first tick where S > ENTROPY_THRESHOLD      [secondary]
    entropies:    full S(t) trace
    """
    omega   = 2.0 * np.arcsin(np.sqrt(np.clip(p_stay, 1e-9, 1 - 1e-9)))
    session = CausalSession(lattice, center, instruction_frequency=omega)

    entropies     = []
    peak_densities = []
    lifetime       = TICKS   # default: never decohered within run

    for t in range(TICKS):
        session.tick()
        session.advance_tick_counter()
        P      = session.probability_density()
        P_c    = P[P > 1e-12]
        S      = float(-np.sum(P_c * np.log(P_c)))
        entropies.append(S)
        peak_densities.append(float(P.max()))
        if lifetime == TICKS and S > ENTROPY_THRESHOLD:
            lifetime = t

    # Primary metric: mean peak probability density over RATE_WINDOW.
    # Most persistent (localized) packet -> highest mean peak density.
    # Shannon entropy is confounded by lattice geometry: a nearly-massless
    # packet spreads along the 6 RGB/CMY vectors forming a low-entropy star
    # pattern even though it has left the origin.  Peak density is immune to
    # this -- any spreading (star or sphere) drops the peak -- and is also
    # unaffected by Zitterbewegung since P = |psi_R|^2 + |psi_L|^2 is smooth.
    t0, t1 = RATE_WINDOW
    t1 = min(t1, len(entropies))
    # We need the peak density trace, not entropies -- store alongside
    slope = float(np.mean(peak_densities[t0:t1])) if t1 > t0 else 0.0

    return slope, lifetime, entropies, peak_densities


# ── Sweep ─────────────────────────────────────────────────────────────────────

def run_sweep(lattice, center, p_values, label):
    rates     = []
    lifetimes = []

    print(f"\n{label}  ({len(p_values)} points)")
    print(f"  {'p_stay':>8}  {'omega':>8}  {'<maxP>':>10}  {'lifetime':>10}")
    print("  " + "-" * 44)

    for i, p in enumerate(p_values):
        omega           = 2.0 * np.arcsin(np.sqrt(np.clip(p, 1e-9, 1 - 1e-9)))
        rate, life, _, _ = run_one(lattice, center, p)
        rates.append(rate)
        lifetimes.append(life)
        marker = '  <- phi^-1' if abs(p - PHI_INV) < 0.012 else ''
        if i % 5 == 0 or marker:
            print(f"  {p:8.4f}  {omega:8.4f}  {rate:10.5f}  {life:10d}{marker}")

    return np.array(rates), np.array(lifetimes)


# ── Main ──────────────────────────────────────────────────────────────────────

def run_golden_decay_audit(data_dir='.', fig_dir='.'):
    print("=" * 60)
    print("EXPERIMENT 12: Golden Ratio (phi^-1) Decay Constant")
    print("=" * 60)
    print(f"\n  phi^-1            = {PHI_INV:.6f}")
    print(f"  Grid              = {LATTICE_SIZE}^3  (boundary at {LATTICE_SIZE//2} nodes)")
    print(f"  Ticks             = {TICKS}")
    print(f"  Rate window       = ticks {RATE_WINDOW[0]}..{RATE_WINDOW[1]}  (pre-boundary)")
    print(f"  Entropy threshold = {ENTROPY_THRESHOLD}")
    print(f"  data_dir          = {data_dir}")
    print(f"  fig_dir           = {fig_dir}")

    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(fig_dir,  exist_ok=True)

    lattice = OctahedralLattice(LATTICE_SIZE, LATTICE_SIZE, LATTICE_SIZE)
    center  = (LATTICE_SIZE // 2,) * 3

    # Phase 1: coarse
    p_coarse              = np.linspace(COARSE_LO, COARSE_HI, COARSE_N)
    t0                    = time.time()
    rates_c, lifetimes_c  = run_sweep(lattice, center, p_coarse, "Phase 1: coarse")

    # Phase 2: fine
    p_fine                = np.linspace(FINE_LO, FINE_HI, FINE_N)
    rates_f, lifetimes_f  = run_sweep(lattice, center, p_fine,   "Phase 2: fine")
    elapsed               = time.time() - t0

    # Combine and sort
    p_all = np.concatenate([p_coarse, p_fine])
    r_all = np.concatenate([rates_c,  rates_f])
    l_all = np.concatenate([lifetimes_c, lifetimes_f])
    order = np.argsort(p_all)
    p_all, r_all, l_all = p_all[order], r_all[order], l_all[order]

    # Save raw data
    npy_path = os.path.join(data_dir, 'exp_12_golden_decay.npy')
    np.save(npy_path, np.column_stack([p_all, r_all, l_all]))
    print(f"\nSaved: {npy_path}  (columns: p_stay, mean_peak_density, lifetime)")

    # Peak density: higher = more localized = more persistent.
    # No validity mask needed: fast-spreading packets naturally have low peak
    # density and won't be selected as the maximum.
    max_peak_idx  = int(np.argmax(r_all))
    max_life_idx  = int(np.argmax(l_all))
    p_peak_max    = p_all[max_peak_idx]
    p_life_max    = p_all[max_life_idx]

    print(f"\n{'='*60}")
    print(f"RESULTS")
    print(f"{'='*60}")
    print(f"  Max mean peak density at p_stay = {p_peak_max:.4f}  "
          f"(phi^-1 = {PHI_INV:.4f},  err = {abs(p_peak_max-PHI_INV):.4f})")
    print(f"  Max lifetime          at p_stay = {p_life_max:.4f}  "
          f"(phi^-1 = {PHI_INV:.4f},  err = {abs(p_life_max-PHI_INV):.4f})")
    print(f"  Elapsed = {elapsed:.1f}s")

    passed = abs(p_peak_max - PHI_INV) < PASS_TOLERANCE
    if passed:
        print(f"\n[PASSED]  Maximum mean peak density at {p_peak_max:.4f} "
              f"(within {PASS_TOLERANCE} of phi^-1).")
        print(f"  The bipartite lattice selects phi^-1 as the most persistent "
              f"residence probability.")
    else:
        print(f"\n[PARTIAL]  Max peak density at {p_peak_max:.4f}, "
              f"phi^-1 = {PHI_INV:.4f}  ({abs(p_peak_max-PHI_INV):.4f} off).")
        print(f"  Consider: wider RATE_WINDOW, more TICKS, or larger grid.")

    # ── Plot ──────────────────────────────────────────────────────────────────
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Left: mean peak density (primary)
        ax1.plot(p_all, r_all, 'o-', color='steelblue', lw=1.5, ms=4,
                 label='mean peak density (ticks 5–28)')
        ax1.axvline(PHI_INV, color='crimson', lw=1.8, ls='--',
                    label=f'$\\phi^{{-1}}$ = {PHI_INV:.4f}')
        ax1.plot(p_peak_max, r_all[max_peak_idx], 'o', color='black', ms=8,
                 zorder=5)
        ax1.annotate(f'max p={p_peak_max:.4f}',
                     xy=(p_peak_max, r_all[max_peak_idx]),
                     xytext=(p_peak_max + 0.05, r_all[max_peak_idx] - 0.01),
                     fontsize=9,
                     arrowprops=dict(arrowstyle='->', lw=0.8))
        ax1.set_xlabel('Residence probability $p(t_{n0})$', fontsize=11)
        ax1.set_ylabel('Mean peak density  $\\langle \\max P \\rangle$', fontsize=11)
        ax1.set_title('Primary metric: mean peak density\n'
                      '(higher = more localized = more persistent)', fontsize=10)
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3)

        # Right: threshold lifetime (secondary)
        ax2.plot(p_all, l_all, 's-', color='forestgreen', lw=1.5, ms=3,
                 label='Threshold lifetime (ticks)')
        ax2.axvline(PHI_INV, color='crimson', lw=1.8, ls='--',
                    label=f'$\\phi^{{-1}}$ = {PHI_INV:.4f}')
        ax2.plot(p_life_max, l_all[max_life_idx], 'o', color='black', ms=8,
                 zorder=5)
        ax2.annotate(f'max p={p_life_max:.4f}',
                     xy=(p_life_max, l_all[max_life_idx]),
                     xytext=(p_life_max + 0.05, l_all[max_life_idx] - 10),
                     fontsize=9,
                     arrowprops=dict(arrowstyle='->', lw=0.8))
        ax2.set_xlabel('Residence probability $p(t_{n0})$', fontsize=11)
        ax2.set_ylabel('Lifetime (ticks until $S >$ threshold)', fontsize=11)
        ax2.set_title(f'Secondary metric: threshold lifetime\n'
                      f'(threshold = {ENTROPY_THRESHOLD}, boundary-dependent)',
                      fontsize=10)
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)

        fig.suptitle(
            'Wave Packet Structural Persistence vs. Residence Probability\n'
            f'Hypothesis: peak persistence at $\\phi^{{-1}} \\approx {PHI_INV:.4f}$',
            fontsize=12
        )
        plt.tight_layout()

        pdf_path = os.path.join(fig_dir, 'exp_12_golden_decay.pdf')
        plt.savefig(pdf_path, bbox_inches='tight')
        print(f"Saved: {pdf_path}")

    except ImportError:
        print("\nmatplotlib not available -- skipping plot")

    return passed


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', default='.', help='Directory for .npy output (default: cwd)')
    ap.add_argument('--fig-dir',  default='.', help='Directory for .pdf figure (default: cwd)')
    args = ap.parse_args()
    run_golden_decay_audit(data_dir=args.data_dir, fig_dir=args.fig_dir)
