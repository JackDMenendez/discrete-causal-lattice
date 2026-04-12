"""
exp_strength_sweep.py
STRENGTH sweep -- test whether omega * R1 = pi/3 is a lattice identity or calibration.

The hydrogen ground state satisfies omega * R1 = pi/3 to within 0.23% at STRENGTH=30.
Two hypotheses:

  H0 (calibration): omega * R1 = pi/3 only at STRENGTH=30.
                    Under standard Bohr scaling R1 ~ 1/STRENGTH, so
                    omega * R1 ~ 1/STRENGTH and varies freely.

  H1 (identity):    omega * R1 = pi/3 for ALL STRENGTH values.
                    The lattice enforces the 3:1 resonance lock
                    and the orbit radius self-adjusts.

Expected outcome under H0:
  S=30:  omega*R1 ~ pi/3          ~ 1.05  (calibration point)
  S=45:  omega*R1 ~ pi/3 * 0.67  ~ 0.70
  S=60:  omega*R1 ~ pi/3 * 0.50  ~ 0.52

Test design (dual-initialization, no dissipation required):

  For each STRENGTH, we run two parallel k scans:

    Scan A (test H1): electron initialized at R1_H1 = pi/(3*omega).
      If H1 is correct, some k value produces a sharp PDF peak AT R1_H1
      for every STRENGTH value.  The lattice "knows" this radius.

    Scan B (test H0): electron initialized at R1_H0 = R1_REF * S_REF / S.
      If H0 is correct, the Bohr radius is preferred and the PDF peak is
      sharp there.  H1 radius (R1_H1) will NOT be sharp for S=45, S=60
      because it's the wrong radius for those potential strengths.

  inv_sharpness is the score: lower = sharper peak = more stable orbit.
  The hypothesis that yields lower inv_sh (sharper peaks) across all
  STRENGTH values wins.

  This design uses the proven exp_11/exp_12 mechanism (no dissipation needed).
  The A=1 renormalization inside tick() makes dissipative capture impossible
  without major architectural changes; the dual-init test is both simpler
  and more directly falsifiable.

Runtime: ~5 hours (3 STRENGTH x 12 k x 2 inits x 8000 ticks on 35^3).
"""

import sys, os, time
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession
from src.core.UnityConstraint import enforce_unity_spinor

# -- Fixed parameters -----------------------------------------------------------
OMEGA      = 0.1019
SOFTENING  = 0.5
WIDTH      = 1.5        # packet width (nodes)
TICKS      = 8000       # ticks per k value
BURN_IN    = 500        # discard first BURN_IN ticks; record last 7500
N_BINS     = 100        # radial bins for electron P(r)
N_K        = 30         # k values per scan (step ~0.002, resolves ~0.002-wide resonance)

# Calibration reference (confirmed from exp_10, exp_12)
STRENGTH_REF = 30.0
R1_REF       = 10.3     # confirmed Bohr radius at STRENGTH=30

# R1 under H1: omega * R1 = pi/3  =>  R1_H1 = pi / (3 * omega)
R1_H1 = np.pi / (3.0 * OMEGA)   # ~10.27

# STRENGTH values to sweep.
# S=30: consistency check vs exp_10/exp_12 (H0 and H1 predictions coincide here).
# S=45, S=60: key measurements where H0 and H1 predictions diverge most.
STRENGTHS = [30.0, 45.0, 60.0]

GRID = 35   # fixed grid for all STRENGTH values (accommodates R1_H1 orbit)

_HERE    = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(_HERE, '..', '..', 'data', 'strength_sweep.npy')


# -- Helpers --------------------------------------------------------------------

def r1_bohr(strength):
    """Bohr radius expected under standard 1/STRENGTH scaling."""
    return R1_REF * STRENGTH_REF / strength


def make_packet(lattice, wc, init_r, k_tan, omega, width):
    """
    Wave packet at init_r along V1=(1,1,1) from well center,
    tangential momentum k_tan along V2=(1,-1,-1).
    Same initialization as exp_11 make_orbital_packet.
    """
    sz    = lattice.size_x
    dr    = int(round(init_r / np.sqrt(3)))
    start = tuple(int(np.clip(wc[i] + dr, 2, sz - 3)) for i in range(3))

    s = CausalSession(lattice, start, instruction_frequency=omega)
    x = np.arange(sz)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    sx, sy, sz_ = start
    r_sq     = (xx - sx)**2 + (yy - sy)**2 + (zz - sz_)**2
    phase    = k_tan * (xx - yy - zz)       # tangential along V2=(1,-1,-1)
    envelope = (np.exp(-0.5 * r_sq / width**2) *
                np.exp(1j * phase)).astype(complex)
    amp = envelope / np.sqrt(2.0)
    s.psi_R = amp.copy()
    s.psi_L = amp.copy()
    enforce_unity_spinor(s.psi_R, s.psi_L)
    return s


def run_single(lattice, r_arr, edges, rctrs, wc, init_r, k_tan):
    """
    Run one (init_r, k_tan) trial for TICKS ticks.
    Returns (peak_r, inv_sharpness).
    """
    session = make_packet(lattice, wc, init_r, k_tan, OMEGA, WIDTH)

    acc = None
    for tick in range(TICKS):
        session.tick()
        session.advance_tick_counter()
        if tick >= BURN_IN:
            d   = session.probability_density()
            acc = d.copy() if acc is None else acc + d

    if acc is None:
        acc = session.probability_density()

    P, _   = np.histogram(r_arr.ravel(), bins=edges, weights=acc.ravel())
    P     /= (P.sum() + 1e-12)
    peak_r = rctrs[np.argmax(P)]
    inv_sh = 1.0 / max(float(P.max() * N_BINS), 0.01)
    return float(peak_r), float(inv_sh)


# -- Single-strength scan -------------------------------------------------------

def scan_one_strength(strength):
    r1_h0 = r1_bohr(strength)
    k_h0  = 1.0 / r1_h0
    k_h1  = 1.0 / R1_H1

    k_lo = min(k_h0, k_h1) * 0.7
    k_hi = max(k_h0, k_h1) * 1.3
    k_values = np.linspace(k_lo, k_hi, N_K)

    wc  = (GRID // 2,) * 3
    lat = OctahedralLattice(GRID, GRID, GRID)
    lat.set_coulomb_well(wc, strength, SOFTENING)

    x  = np.arange(GRID)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    r_arr = np.sqrt((xx - wc[0])**2 + (yy - wc[1])**2 + (zz - wc[2])**2)
    r_max = float(r_arr.max())
    edges = np.linspace(0, r_max, N_BINS + 1)
    rctrs = 0.5 * (edges[:-1] + edges[1:])

    print(f"\n  S={strength:.0f}  R1_H0={r1_h0:.2f}  R1_H1={R1_H1:.2f}"
          f"  k_H0={k_h0:.4f}  k_H1={k_h1:.4f}")
    print(f"  grid={GRID}^3  k scan [{k_lo:.4f}, {k_hi:.4f}]")
    print(f"\n  {'':10}  --- Scan A: init at R1_H1={R1_H1:.2f} ---"
          f"  --- Scan B: init at R1_H0={r1_h0:.2f} ---")
    print(f"  {'k_tan':>8}  {'A_peak':>8}  {'A_inv':>7}  {'A_oR1':>7}"
          f"  {'B_peak':>8}  {'B_inv':>7}  {'B_oR1':>7}  note")
    print(f"  {'-'*72}")

    results_A = []   # init at R1_H1 (test H1)
    results_B = []   # init at R1_H0 (test H0)

    for k in k_values:
        peak_A, inv_A = run_single(lat, r_arr, edges, rctrs, wc, R1_H1,  k)
        peak_B, inv_B = run_single(lat, r_arr, edges, rctrs, wc, r1_h0, k)

        oR1_A = OMEGA * peak_A
        oR1_B = OMEGA * peak_B

        near_h0 = abs(k - k_h0) < (k_hi - k_lo) / N_K * 0.6
        near_h1 = abs(k - k_h1) < (k_hi - k_lo) / N_K * 0.6
        note = (' H0' if near_h0 else '') + (' H1' if near_h1 else '')

        print(f"  {k:8.4f}  {peak_A:8.3f}  {inv_A:7.4f}  {oR1_A:7.4f}"
              f"  {peak_B:8.3f}  {inv_B:7.4f}  {oR1_B:7.4f} {note}")

        results_A.append((float(k), float(peak_A), float(inv_A)))
        results_B.append((float(k), float(peak_B), float(inv_B)))

    return results_A, results_B, r1_h0, k_h0


# -- Main -----------------------------------------------------------------------

def run():
    print("=" * 70)
    print("STRENGTH SWEEP -- omega * R1 = pi/3 identity test")
    print("Dual-initialization design (exp_11 mechanism, no dissipation)")
    print("=" * 70)
    print(f"  omega={OMEGA}  softening={SOFTENING}  R1_H1={R1_H1:.3f}")
    print(f"  STRENGTHS: {STRENGTHS}")
    print(f"  Ticks/k: {TICKS}  burn-in: {BURN_IN}"
          f"  recording: {TICKS-BURN_IN}  grid: {GRID}^3")
    print(f"\n  Scan A: electron initialized at R1_H1 (tests H1)")
    print(f"  Scan B: electron initialized at R1_H0 (tests H0)")
    print(f"\n  H0 prediction: omega*R1 = (pi/3)*(30/S)  [varies with S]")
    print(f"  H1 prediction: omega*R1 = pi/3 = {np.pi/3:.4f}  [constant]")

    summary = []

    for strength in STRENGTHS:
        t0 = time.time()
        results_A, results_B, r1_h0, k_h0 = scan_one_strength(strength)

        # Best k for each scan: lowest inv_sharpness
        best_A = min(results_A, key=lambda x: x[2])
        best_B = min(results_B, key=lambda x: x[2])

        k_A, peak_A, inv_A = best_A
        k_B, peak_B, inv_B = best_B
        oR1_A = OMEGA * peak_A
        oR1_B = OMEGA * peak_B

        H0_pred = (np.pi / 3) * (STRENGTH_REF / strength)
        dev_A   = (oR1_A - np.pi / 3) / (np.pi / 3) * 100.0
        dev_B   = (oR1_B - H0_pred)   / H0_pred      * 100.0

        elapsed = time.time() - t0
        print(f"\n  S={strength:5.1f}  [{elapsed:.0f}s]")
        print(f"    Scan A (H1 init r={R1_H1:.2f}): k_best={k_A:.4f}"
              f"  peak_r={peak_A:.2f}  omega*R1={oR1_A:.4f}"
              f"  dev_pi3={dev_A:+.1f}%  inv_sh={inv_A:.4f}")
        print(f"    Scan B (H0 init r={r1_h0:.2f}): k_best={k_B:.4f}"
              f"  peak_r={peak_B:.2f}  omega*R1={oR1_B:.4f}"
              f"  dev_H0={dev_B:+.1f}%   inv_sh={inv_B:.4f}")

        winner = 'A->H1' if inv_A < inv_B else 'B->H0'
        print(f"    Winner (sharper peak): {winner}")

        summary.append((strength, k_A, peak_A, oR1_A, inv_A,
                                   k_B, peak_B, oR1_B, inv_B, H0_pred))

    print()
    print("=" * 70)
    print("RESULT")
    print("=" * 70)
    arr = np.array(summary)

    print(f"\n  {'S':>6}  {'A_oR1':>8}  {'A_inv':>7}  {'B_oR1':>8}"
          f"  {'B_inv':>7}  {'H0_pred':>8}  winner")
    print(f"  {'-'*60}")
    for row in summary:
        s, k_A, peak_A, oR1_A, inv_A, k_B, peak_B, oR1_B, inv_B, H0_pred = row
        winner = 'H1' if inv_A < inv_B else 'H0'
        print(f"  {s:6.1f}  {oR1_A:8.4f}  {inv_A:7.4f}  {oR1_B:8.4f}"
              f"  {inv_B:7.4f}  {H0_pred:8.4f}  {winner}")

    H1_wins = sum(1 for row in summary if row[4] < row[8])  # inv_A < inv_B
    H0_wins = len(summary) - H1_wins

    print(f"\n  H1 wins: {H1_wins}/{len(summary)}  "
          f"H0 wins: {H0_wins}/{len(summary)}")
    print()

    if H1_wins == len(summary):
        print("[RESULT: H1] R1_H1 = pi/(3*omega) is stable across ALL STRENGTH values.")
        print("  omega * R1 = pi/3 is a lattice geometric identity, not calibration.")
        print("  EXTRAORDINARY.")
    elif H0_wins == len(summary):
        print("[RESULT: H0] R1_H0 (Bohr scaling) is preferred across all STRENGTH values.")
        print("  The pi/3 identity at STRENGTH=30 is a calibration coincidence.")
    else:
        print("[RESULT: MIXED] Results split between H0 and H1.")
        print("  Check per-STRENGTH winners above for details.")

    np.save(OUT_FILE, arr)
    print(f"\nSaved: {OUT_FILE}")
    print("  columns: strength, k_A, peak_A, oR1_A, inv_A,"
          "  k_B, peak_B, oR1_B, inv_B, H0_pred")


if __name__ == '__main__':
    run()
