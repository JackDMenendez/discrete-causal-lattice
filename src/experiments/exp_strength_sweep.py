"""
exp_strength_sweep.py
STRENGTH sweep -- test whether omega * R1 = pi/3 is a lattice identity or calibration.

The hydrogen ground state satisfies omega * R1 = pi/3 to within 0.23% at STRENGTH=30.
Two hypotheses:

  H0 (calibration): omega * R1 = pi/3 only at STRENGTH=30.
                    Under standard Bohr scaling R1 ~ 1/STRENGTH, so
                    omega * R1 ~ 1/STRENGTH and varies freely.

  H1 (identity):    omega * R1 = pi/3 for ALL STRENGTH values.
                    The lattice actively enforces the 3:1 resonance lock
                    and the orbit radius self-adjusts.

Test: fix omega=0.1019, vary STRENGTH in [10, 15, 20, 30, 45, 60].
For each STRENGTH, run a focused k-scan around the predicted Bohr value,
find k_best, compute R1=1/k_best, and check omega*R1.

Standard Bohr prediction:  R1(S) = R1(30) * 30/S  ->  omega*R1(S) = (pi/3) * 30/S
Resonance lock prediction:  k_best = (3/pi)*omega  for all S  (R1 constant -- unphysical)

Expected outcome under H0:
  S=10:  omega*R1 ~ pi/3 * 3.0 = pi  ~ 3.14
  S=15:  omega*R1 ~ pi/3 * 2.0 = 2pi/3 ~ 2.09
  S=20:  omega*R1 ~ pi/3 * 1.5 = pi/2 ~ 1.57
  S=30:  omega*R1 ~ pi/3         ~ 1.05  (calibration point)
  S=45:  omega*R1 ~ pi/3 * 0.67 ~ 0.70
  S=60:  omega*R1 ~ pi/3 * 0.5  ~ 0.52

Each scan: ~15 k values, 1500 ticks (500 burn-in + 1000 record), PDF scoring.
"""

import sys, os, time
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession
from src.core.UnityConstraint import enforce_unity_spinor

# -- Fixed parameters -----------------------------------------------------------
OMEGA      = 0.1019
SOFTENING  = 0.5
WIDTH      = 1.5       # packet width
TICKS      = 1500
BURN_IN    = 500
N_BINS     = 60
N_K        = 15        # k values per STRENGTH scan

# Calibration reference: at STRENGTH=30, R1_ref=10.3
STRENGTH_REF = 30.0
R1_REF       = 10.3

# STRENGTH values to sweep
STRENGTHS = [10.0, 15.0, 20.0, 30.0, 45.0, 60.0]

_HERE    = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(_HERE, '..', '..', 'data', 'strength_sweep.npy')


# -- Helpers (minimal versions of exp_11) ---------------------------------------

def r1_expected(strength):
    """Bohr radius expected under standard 1/STRENGTH scaling."""
    return R1_REF * STRENGTH_REF / strength


def grid_for_r1(r1):
    """Minimum grid side to comfortably fit orbit at r1."""
    return max(24, 2 * (int(r1 / np.sqrt(3)) + 10) + 1)


def make_packet(lattice, wc, r1, k, omega, width):
    sz  = lattice.size_x
    dr  = int(round(r1 / np.sqrt(3)))
    start = tuple(min(wc[i] + dr, sz - 3) for i in range(3))
    s = CausalSession(lattice, start, instruction_frequency=omega)
    x = np.arange(sz)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    sx, sy, sz_ = start
    r_sq     = (xx-sx)**2 + (yy-sy)**2 + (zz-sz_)**2
    envelope = (np.exp(-0.5 * r_sq / width**2) *
                np.exp(1j * k * (xx - yy - zz))).astype(complex)
    amp = envelope / np.sqrt(2.0)
    s.psi_R = amp.copy()
    s.psi_L = amp.copy()
    enforce_unity_spinor(s.psi_R, s.psi_L)
    return s


def scan_one_strength(strength):
    r1_pred  = r1_expected(strength)
    k_center = 1.0 / r1_pred
    k_half   = 0.4 * k_center        # scan +/- 40% around predicted k
    k_values = np.linspace(k_center - k_half, k_center + k_half, N_K)

    grid = grid_for_r1(r1_pred)
    wc   = (grid//2,) * 3

    lat  = OctahedralLattice(grid, grid, grid)
    lat.set_coulomb_well(wc, strength, SOFTENING)

    x  = np.arange(grid)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    r_arr  = np.sqrt((xx-wc[0])**2 + (yy-wc[1])**2 + (zz-wc[2])**2)
    r_max  = float(r_arr.max())
    edges  = np.linspace(0, r_max, N_BINS+1)
    rctrs  = 0.5*(edges[:-1]+edges[1:])

    results = []
    for k in k_values:
        sess = make_packet(lat, wc, r1_pred, k, OMEGA, WIDTH)
        acc  = None
        for tick in range(TICKS):
            sess.tick()
            sess.advance_tick_counter()
            if tick >= BURN_IN:
                d = sess.probability_density()
                acc = d.copy() if acc is None else acc + d

        if acc is None:
            acc = sess.probability_density()

        # PDF score
        P, _ = np.histogram(r_arr.ravel(), bins=edges, weights=acc.ravel())
        P   /= (P.sum() + 1e-12)
        peak_r   = rctrs[np.argmax(P)]
        peak_err = abs(peak_r - r1_pred) / r1_pred
        inv_sh   = 1.0 / max(float(P.max() * N_BINS), 0.01)
        score    = peak_err + inv_sh
        results.append((float(k), peak_r, peak_err, inv_sh, score))

    return results, r1_pred, k_center


# -- Main -----------------------------------------------------------------------

def run():
    print("=" * 65)
    print("STRENGTH SWEEP -- omega * R1 = pi/3 identity test")
    print("=" * 65)
    print(f"  omega={OMEGA}  softening={SOFTENING}")
    print(f"  STRENGTHS: {STRENGTHS}")
    print(f"  Ticks/k: {TICKS}  burn-in: {BURN_IN}  k-values/STRENGTH: {N_K}")
    print(f"\n  H0 prediction: omega*R1 = (pi/3)*(30/S)  [varies with S]")
    print(f"  H1 prediction: omega*R1 = pi/3            [constant]")
    print()

    summary = []  # (strength, k_best, R1_best, omega_R1, H0_pred, dev_from_pi3)

    for strength in STRENGTHS:
        t0 = time.time()
        results, r1_pred, k_center = scan_one_strength(strength)

        best     = min(results, key=lambda x: x[4])
        k_best   = best[0]
        R1_best  = best[1]
        oR1      = OMEGA * R1_best
        H0_pred  = (np.pi/3) * (STRENGTH_REF / strength)
        dev_pi3  = (oR1 - np.pi/3) / (np.pi/3) * 100.0
        dev_H0   = (oR1 - H0_pred) / H0_pred * 100.0

        print(f"S={strength:5.1f}  k_pred={k_center:.4f}  k_best={k_best:.4f}  "
              f"R1={R1_best:.2f}  omega*R1={oR1:.4f}  "
              f"pi/3={np.pi/3:.4f}  H0={H0_pred:.4f}  "
              f"dev_pi3={dev_pi3:+.1f}%  dev_H0={dev_H0:+.1f}%  "
              f"[{time.time()-t0:.0f}s]")

        summary.append((strength, k_best, R1_best, oR1, H0_pred, dev_pi3))

    print()
    print("=" * 65)
    print("RESULT")
    print("=" * 65)
    arr = np.array(summary)
    oR1_vals = arr[:,3]
    H0_vals  = arr[:,4]

    dev_from_pi3 = np.abs(oR1_vals - np.pi/3) / (np.pi/3) * 100
    dev_from_H0  = np.abs(oR1_vals - H0_vals) / H0_vals * 100

    print(f"  Mean |dev from pi/3|: {dev_from_pi3.mean():.2f}%  "
          f"max: {dev_from_pi3.max():.2f}%")
    print(f"  Mean |dev from H0|:   {dev_from_H0.mean():.2f}%  "
          f"max: {dev_from_H0.max():.2f}%")
    print()

    if dev_from_pi3.mean() < 2.0:
        print("[RESULT: H1] omega*R1 ~ pi/3 across all STRENGTH values.")
        print("  The 3:1 resonance lock appears to be enforced by the lattice.")
        print("  EXTRAORDINARY -- the orbit self-selects to maintain the resonance.")
    elif dev_from_H0.mean() < 5.0:
        print("[RESULT: H0] omega*R1 follows standard Bohr scaling (1/STRENGTH).")
        print("  The pi/3 identity at STRENGTH=30 is a calibration coincidence.")
        print("  Note: STRENGTH=30 is still special -- it lands on the 3:1 resonance.")
    else:
        print("[RESULT: MIXED] Neither hypothesis fits cleanly.")
        print("  The lattice introduces corrections to standard Bohr scaling.")

    np.save(OUT_FILE, arr)
    print(f"\nSaved: {OUT_FILE}")
    print("  columns: strength, k_best, R1_best, omega*R1, H0_pred, dev_pi3_%")


if __name__ == '__main__':
    run()
