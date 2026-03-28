"""
exp_11_quantization_scan.py
Scan: Spontaneous quantization from A=1 bipartite lattice.

Tests whether the lattice *selects* Bohr-quantized k values as the only
stable orbital solutions, rather than requiring them to be imposed.

For each k in a range around the Bohr condition k_n = n/r_n, a wave packet
is initialized at r_n and evolved for TICKS ticks.  Both metric sets are
computed and saved:

CoM scalar metrics (original):
  cv      -- coefficient of variation (std/mean of CoM radius trace)
  r_bias  -- |r_mean - r_n| / r_n
  score_com = cv + r_bias

Radial PDF metrics (new):
  After BURN_IN ticks the probability density is accumulated into a
  time-averaged radial PDF P(r).
  peak_error    -- |r_peak - r_n| / r_n: low = PDF peaks at Bohr radius
  inv_sharpness -- 1 / (P_peak * N_BINS): low = PDF is narrow
  score_pdf = peak_error + inv_sharpness

The PDF approach directly mirrors what is observed: the Dirac hydrogen
wavefunction predicts a radial probability density that peaks sharply at
the Bohr radius.  A stable lattice orbit at the correct k should reproduce
this signature.

Outputs per n-level:
  quantization_scan_n{n}.npy       -- (n_k x 8): k, r_mean, cv, r_bias,
                                      score_com, inv_sharpness, peak_error,
                                      score_pdf
  quantization_scan_n{n}_pdf.npy   -- (n_k x N_BINS): P(r) for each k
  quantization_scan_n{n}_rbins.npy -- (N_BINS,): radial bin centers

Runtime budget (estimated on 30^3 ~0.022 s/tick):
  n=1: 401 k values x 8000 ticks x 0.022 s  ~  19.6 hrs
  n=2:  41 k values x 8000 ticks x 0.215 s  ~  19.6 hrs  (65^3 grid)
  Each fits comfortably in a 24-hour run.

Paper reference: Section 11 (Spontaneous Quantization)
"""

import sys, os, time
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import (OctahedralLattice, CausalSession, enforce_unity_spinor)

# ── Coulomb well (same as exp_10) ─────────────────────────────────────────────
STRENGTH  = 30.0
SOFTENING = 0.5
OMEGA     = 0.1019    # particle mass (instruction frequency)
WIDTH     = 1.5       # packet width in nodes
R1_APPROX = 10.3      # n=1 Bohr radius in lattice units

TICKS    = 8000       # ticks per k value (was 1200)
BURN_IN  = 500        # ticks discarded before PDF accumulation begins
N_BINS   = 100        # radial bins for P(r)
N_EPOCHS = 5          # independent sub-windows for epoch-averaged scoring
                      # Each epoch is (TICKS-BURN_IN)//N_EPOCHS ticks.
                      # score_epoch_mean/std replace score_pdf as pass criterion:
                      # a genuine stable orbit scores consistently across epochs;
                      # a one-window artifact has high std.

# ── n=1 scan parameters ───────────────────────────────────────────────────────
# Focused on k_Bohr=0.0971; step 0.0002 gives ~401 values (~20 hrs on 30^3)
N1_K_MIN  = 0.060
N1_K_MAX  = 0.140
N1_K_STEP = 0.0002

# ── n=1 focused scan (--focused flag) ─────────────────────────────────────────
# Narrower range around k_Bohr, coarser step: ~26 values, ~2 hrs on 30^3.
# Use this to validate epoch scoring and locate the stable-orbit peak before
# committing to the full 20-hr scan.
N1_FOCUSED_K_MIN  = 0.085
N1_FOCUSED_K_MAX  = 0.110
N1_FOCUSED_K_STEP = 0.001

# ── n=2 scan parameters ───────────────────────────────────────────────────────
# Focused on k_Bohr=0.0485; step 0.001 gives ~41 values (~20 hrs on 65^3)
N2_K_MIN  = 0.030
N2_K_MAX  = 0.070
N2_K_STEP = 0.001


# ── Packet initializer (identical to exp_10) ──────────────────────────────────

def make_orbital_packet(lattice, well_center, r_n, k_n, omega, width):
    """
    Gaussian wave packet at r_n with tangential momentum k_n along
    V2=(1,-1,-1).  Both Dirac spinor components initialized equally.
    """
    wc  = well_center
    dr  = int(round(r_n / np.sqrt(3)))
    sz  = lattice.size_x
    start = tuple(min(wc[i] + dr, sz - 3) for i in range(3))

    s = CausalSession(lattice, start, instruction_frequency=omega)

    x = np.arange(sz)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    sx, sy, sz_ = start
    r_sq    = (xx - sx)**2 + (yy - sy)**2 + (zz - sz_)**2
    phase   = k_n * (xx - yy - zz)           # tangential along V2=(1,-1,-1)
    envelope = (np.exp(-0.5 * r_sq / width**2) *
                np.exp(1j * phase)).astype(complex)

    amp = envelope / np.sqrt(2.0)
    s.psi_R = amp.copy()
    s.psi_L = amp.copy()
    enforce_unity_spinor(s.psi_R, s.psi_L)
    return s


# ── CoM scalar metrics (original approach) ───────────────────────────────────

def center_of_mass_radius(density, wc):
    """Density-weighted mean distance from well center."""
    total = density.sum()
    if total < 1e-12:
        return 0.0
    sx, sy, sz = density.shape
    x = np.arange(sx) - wc[0]
    y = np.arange(sy) - wc[1]
    z = np.arange(sz) - wc[2]
    cx = float(np.einsum('ijk,i->', density, x) / total)
    cy = float(np.einsum('ijk,j->', density, y) / total)
    cz = float(np.einsum('ijk,k->', density, z) / total)
    return float(np.sqrt(cx**2 + cy**2 + cz**2))


def stability_metrics(dists, r_n, settle):
    """cv, r_bias, score_com, r_mean from CoM radius trace."""
    tail   = np.array(dists[-settle:])
    r_mean = float(np.mean(tail))
    if r_mean < 0.5:
        return 1.0, 1.0, 2.0, r_mean
    cv     = float(np.std(tail) / r_mean)
    r_bias = abs(r_mean - r_n) / r_n
    return cv, r_bias, cv + r_bias, r_mean


# ── Radial PDF helpers ────────────────────────────────────────────────────────

def precompute_radii(grid, wc):
    """Precompute radial distance from well center for every voxel."""
    x = np.arange(grid)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    return np.sqrt((xx - wc[0])**2 + (yy - wc[1])**2 + (zz - wc[2])**2)


def pdf_metrics(avg_density, r_arr, r_n, bin_edges, r_centers):
    """
    Compute radial PDF P(r) from time-averaged density and return stability
    metrics.

    Returns:
      peak_error    -- |r_peak - r_n| / r_n
      inv_sharpness -- 1 / (P_peak * N_BINS)  (low = sharp peak)
      score         -- peak_error + inv_sharpness
      r_mean        -- density-weighted mean radius
      P             -- normalized radial PDF (length N_BINS)
    """
    n_bins  = len(r_centers)
    r_flat  = r_arr.ravel()
    d_flat  = avg_density.ravel()

    P, _ = np.histogram(r_flat, bins=bin_edges, weights=d_flat)
    total = P.sum()
    if total < 1e-12:
        return 1.0, 1.0, 2.0, 0.0, np.ones(n_bins) / n_bins

    P = P / total
    r_mean    = float(np.dot(r_centers, P))
    peak_idx  = int(np.argmax(P))
    r_peak    = r_centers[peak_idx]

    # peak_sharpness: ratio of peak height to uniform level (1 = flat)
    peak_sharpness = float(P[peak_idx] * n_bins)
    inv_sharpness  = 1.0 / max(peak_sharpness, 0.01)

    peak_error = abs(r_peak - r_n) / r_n
    score      = peak_error + inv_sharpness

    return peak_error, inv_sharpness, score, r_mean, P


# ── Single-level scan ─────────────────────────────────────────────────────────

def run_scan(n, r_n, k_bohr, k_min, k_max, k_step, grid, wc, lattice,
             r_arr, bin_edges, r_centers):
    k_values  = np.arange(k_min, k_max + k_step * 0.5, k_step)
    results   = []
    settle    = TICKS - BURN_IN
    epoch_len = settle // N_EPOCHS

    print(f"\n{'k':>8}  {'r_mean':>8}  {'cv':>8}  {'r_bias':>8}  "
          f"{'s_com':>7}  {'inv_sh':>7}  {'pk_err':>7}  {'s_pdf':>7}  "
          f"{'ep_mean':>8}  {'ep_std':>7}  note")
    print("-" * 110)

    for k in k_values:
        session      = make_orbital_packet(lattice, wc, r_n, k, OMEGA, WIDTH)
        avg_density  = None
        epoch_accs   = [None] * N_EPOCHS
        dists        = []

        for tick in range(TICKS):
            session.tick()
            session.advance_tick_counter()
            d = session.probability_density()
            dists.append(center_of_mass_radius(d, wc))
            if tick >= BURN_IN:
                t_rel = tick - BURN_IN
                ep    = min(t_rel // epoch_len, N_EPOCHS - 1)
                if epoch_accs[ep] is None:
                    epoch_accs[ep] = d.copy()
                else:
                    epoch_accs[ep] += d
                if avg_density is None:
                    avg_density = d.copy()
                else:
                    avg_density += d

        if avg_density is None:
            avg_density = session.probability_density()

        cv, r_bias, score_com, r_mean = stability_metrics(dists, r_n, settle)
        peak_error, inv_sharpness, score_pdf, _, P = pdf_metrics(
            avg_density, r_arr, r_n, bin_edges, r_centers)

        # Epoch-averaged score: score each sub-window independently.
        # Low mean + low std = genuinely stable orbit.
        # Low mean + high std = one-window artifact.
        epoch_scores = []
        for acc in epoch_accs:
            if acc is not None:
                _, _, ep_score, _, _ = pdf_metrics(
                    acc, r_arr, r_n, bin_edges, r_centers)
                epoch_scores.append(ep_score)
        score_epoch_mean = float(np.mean(epoch_scores)) if epoch_scores else score_pdf
        score_epoch_std  = float(np.std(epoch_scores))  if epoch_scores else 0.0

        near = abs(k - k_bohr) < k_step * 0.6
        note = f' <- Bohr k_{n}' if near else ''

        print(f"  {k:6.4f}  {r_mean:8.3f}  {cv:8.5f}  {r_bias:8.5f}  "
              f"{score_com:7.4f}  {inv_sharpness:7.4f}  {peak_error:7.4f}  "
              f"{score_pdf:7.4f}  {score_epoch_mean:8.4f}  {score_epoch_std:7.4f}"
              f"{note}")

        results.append({
            'k': float(k), 'r_mean': r_mean,
            'cv': cv, 'r_bias': r_bias, 'score_com': score_com,
            'inv_sharpness': inv_sharpness, 'peak_error': peak_error,
            'score_pdf': score_pdf,
            'score_epoch_mean': score_epoch_mean,
            'score_epoch_std':  score_epoch_std,
            'P': P,
        })

    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def run_quantization_scan(n_level=1, datadir='.', focused=False):
    print("=" * 65)
    print("EXPERIMENT 11: Spontaneous Quantization Scan  (PDF mode)")
    print("=" * 65)

    r_n     = n_level**2 * R1_APPROX
    k_bohr  = n_level / r_n
    dr_n    = int(round(r_n / np.sqrt(3)))
    grid    = max(30, 2 * (dr_n + 8) + 1)
    wc      = (grid // 2,) * 3
    mem_mb  = grid**3 * 16 / 1e6

    if focused and n_level == 1:
        k_min, k_max, k_step = N1_FOCUSED_K_MIN, N1_FOCUSED_K_MAX, N1_FOCUSED_K_STEP
    elif n_level == 1:
        k_min, k_max, k_step = N1_K_MIN, N1_K_MAX, N1_K_STEP
    else:
        k_min, k_max, k_step = N2_K_MIN, N2_K_MAX, N2_K_STEP

    n_k = int(round((k_max - k_min) / k_step)) + 1

    epoch_len = (TICKS - BURN_IN) // N_EPOCHS
    print(f"\n  n              = {n_level}{'  [FOCUSED]' if focused else ''}")
    print(f"  r_n            = {r_n:.1f}  (Bohr radius in lattice units)")
    print(f"  k_Bohr         = {k_bohr:.5f}")
    print(f"  k scan         = [{k_min:.4f}, {k_max:.4f}]  step {k_step:.4f}  ({n_k} values)")
    print(f"  Grid           = {grid}^3  ({mem_mb:.0f} MB)")
    print(f"  Ticks/k        = {TICKS}   burn-in = first {BURN_IN}  PDF window = {TICKS-BURN_IN}")
    print(f"  Epochs         = {N_EPOCHS} x {epoch_len} ticks  (epoch-averaged scoring)")
    print(f"  Radial bins    = {N_BINS}")
    print(f"  V(r)           = -{STRENGTH}/(r+{SOFTENING})")
    print(f"  omega          = {OMEGA:.4f}")

    # Precompute radial geometry once (shared across all k values)
    r_arr     = precompute_radii(grid, wc)
    r_max     = float(r_arr.max())
    bin_edges = np.linspace(0, r_max, N_BINS + 1)
    r_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    lattice = OctahedralLattice(grid, grid, grid)
    lattice.set_coulomb_well(wc, STRENGTH, SOFTENING)

    t0 = time.time()
    results = run_scan(n_level, r_n, k_bohr, k_min, k_max, k_step,
                       grid, wc, lattice, r_arr, bin_edges, r_centers)
    elapsed = time.time() - t0

    # ── Summary ───────────────────────────────────────────────────────────────
    k_arr             = np.array([r['k']                for r in results])
    cv_arr            = np.array([r['cv']               for r in results])
    r_bias_arr        = np.array([r['r_bias']           for r in results])
    score_com_arr     = np.array([r['score_com']        for r in results])
    inv_shrp_arr      = np.array([r['inv_sharpness']    for r in results])
    peak_err_arr      = np.array([r['peak_error']       for r in results])
    score_pdf_arr     = np.array([r['score_pdf']        for r in results])
    score_epoch_mean  = np.array([r['score_epoch_mean'] for r in results])
    score_epoch_std   = np.array([r['score_epoch_std']  for r in results])

    for label, score_arr in [('CoM (cv+r_bias)',             score_com_arr),
                              ('PDF (peak_err+inv_sharpness)', score_pdf_arr),
                              ('Epoch mean (robust)',          score_epoch_mean)]:
        min_idx  = int(np.argmin(score_arr))
        k_stable = k_arr[min_idx]
        pct_err  = abs(k_stable - k_bohr) / k_bohr * 100.0
        extra    = (f'  epoch_std={score_epoch_std[min_idx]:.4f}'
                    if label.startswith('Epoch') else '')
        print(f"\n{'='*65}")
        print(f"RESULT [{label}]  (n={n_level})")
        print(f"{'='*65}")
        print(f"  Best k (min score) = {k_stable:.4f}")
        print(f"  Bohr k_{n_level}           = {k_bohr:.4f}")
        print(f"  Error              = {pct_err:.1f}%")
        print(f"  Score at best k    = {score_arr[min_idx]:.6f}{extra}")

    print(f"\n  Total time = {elapsed:.0f}s  ({elapsed/3600:.2f} hrs)")

    # Pass criterion: epoch_mean minimum closest to k_Bohr
    min_idx  = int(np.argmin(score_epoch_mean))
    k_stable = k_arr[min_idx]
    pct_err  = abs(k_stable - k_bohr) / k_bohr * 100.0
    passed   = pct_err < (1.5 * k_step / k_bohr * 100.0)

    if passed:
        print(f"\n[SCAN PASSED]")
        print(f"  Lattice selects k_{n_level} = {k_stable:.4f} spontaneously.")
        print(f"  epoch_std={score_epoch_std[min_idx]:.4f}  "
              f"(low = orbit stable across all time windows)")
        print(f"  Bohr quantization emerges from dynamics, not initial conditions.")
    else:
        print(f"\n[SCAN PARTIAL]")
        print(f"  Epoch-mean minimum at k={k_stable:.4f}, Bohr predicts {k_bohr:.4f} "
              f"({pct_err:.1f}% off).")
        print(f"  epoch_std={score_epoch_std[min_idx]:.4f}  "
              f"({'stable orbit, lattice correction?' if score_epoch_std[min_idx] < 0.1 else 'high variance -- artifact'})")
        print(f"  Consider: focused scan, longer TICKS, or nucleus cone.")

    # ── Save data ─────────────────────────────────────────────────────────────
    tag   = '_focused' if focused else ''
    fname = os.path.join(datadir, f'quantization_scan_n{n_level}{tag}.npy')
    # 10 columns: k, r_mean, cv, r_bias, score_com, inv_sharpness, peak_error,
    #             score_pdf, score_epoch_mean, score_epoch_std
    np.save(fname, np.column_stack([
        k_arr,
        [r['r_mean'] for r in results],
        cv_arr,
        r_bias_arr,
        score_com_arr,
        inv_shrp_arr,
        peak_err_arr,
        score_pdf_arr,
        score_epoch_mean,
        score_epoch_std,
    ]))
    print(f"\nSaved: {fname}")
    print(f"  columns: k, r_mean, cv, r_bias, score_com, inv_sharpness, "
          f"peak_error, score_pdf, score_epoch_mean, score_epoch_std")

    # Radial PDFs for each k
    pdf_arr     = np.array([r['P'] for r in results])
    pdf_fname   = os.path.join(datadir, f'quantization_scan_n{n_level}{tag}_pdf.npy')
    rbins_fname = os.path.join(datadir, f'quantization_scan_n{n_level}{tag}_rbins.npy')
    np.save(pdf_fname,   pdf_arr)
    np.save(rbins_fname, r_centers)
    print(f"Saved: {pdf_fname}   shape {pdf_arr.shape}  (n_k x N_BINS)")
    print(f"Saved: {rbins_fname}  shape {r_centers.shape}")

    # ASCII score profile (epoch mean score)
    print(f"\nEpoch-mean score profile  (lower = better, std shows stability)")
    print(f"{'k':>8}  {'ep_mean':>8}  {'ep_std':>7}  bar")
    print("-" * 60)
    sc_max = float(np.max(score_epoch_mean))
    bar_w  = 30
    for r in results:
        sc  = r['score_epoch_mean']
        std = r['score_epoch_std']
        bar_len = int(round(sc / sc_max * bar_w))
        marker  = '<' if abs(r['k'] - k_bohr) < k_step * 0.6 else ' '
        print(f"  {r['k']:6.4f}  {sc:8.4f}  {std:7.4f}  {'|' * bar_len}{marker}")

    return passed


if __name__ == '__main__':
    import argparse, sys
    ap = argparse.ArgumentParser()
    ap.add_argument('--n2', action='store_true',
                    help='Scan n=2 orbit (65^3 grid, ~20 hr run)')
    ap.add_argument('--focused', action='store_true',
                    help='Quick n=1 focused scan: k=[0.085,0.110] step=0.001 (~2 hrs)')
    ap.add_argument('--datadir', default='.',
                    help='Directory for .npy output files (default: cwd)')
    args = ap.parse_args()
    passed = run_quantization_scan(n_level=2 if args.n2 else 1,
                                   datadir=args.datadir,
                                   focused=args.focused)
    sys.exit(0 if passed else 1)
