"""
exp_02b_inverse_square.py
Numerical verification: gravitational force scales as 1/r²

Tests the prediction from newtonian_gravity_derivation.md:
  F = GMm/r²  =>  acceleration a = GM/r²

A zero-momentum Gaussian packet is initialized at distance r from a
point-source potential V(x) = -STRENGTH/(r + SOFTENING). The initial
acceleration is measured from the CoM displacement over the first few
ticks, before the packet has moved appreciably from its starting distance.

If the force law is 1/r², then a·r² should be constant across all r.

Distances tested: [8, 12, 16, 20, 24] nodes from well center.
All other parameters identical across runs.

Pass criterion: a·r² constant to within 20% across all distances.
(The finite packet width σ=2 contributes an effective radius correction
of order σ²/r², which is ~6% at r=8 and ~1% at r=24 -- within tolerance.)

Paper reference: notes/newtonian_gravity_derivation.md, Section 7 (gravity).
"""

import sys, os, time
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession, enforce_unity_spinor

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         '..', '..', 'data')

# ── Parameters ────────────────────────────────────────────────────────────────
GRID      = 65
OMEGA     = 0.2          # test particle mass (same for all runs)
WIDTH     = 2.0          # Gaussian packet width (nodes)
STRENGTH  = 2.0          # weak-field: V(r) = 2/r << omega=0.2 for r >> 10
SOFTENING = 0.5          # Planck-scale softening
TICKS     = 600          # long run: smooth out Zitterbewegung
WIN       = 20           # CoM averaging window (kills Zitterbewegung)
FIT_TICKS = 200          # parabola fit range: r changes < 5% in this window
DISTANCES = [15, 20, 25, 30, 35]  # weak-field regime: V/omega < 0.1 at all r

# Weak-field check: V(r)/omega should be << 1
# V(15)/0.2 = 2/15.5/0.2 = 0.65 -- borderline; V(20)/0.2 = 0.49 -- ok
# Use DISTANCES starting at 15 and check residuals at r=15 are not outliers.

WC = (GRID//2,) * 3     # well center = grid center


# ── Helpers ───────────────────────────────────────────────────────────────────

def grav_potential(grid, cx, cy, cz):
    """
    Gravitational clock density potential: V = +STRENGTH/r (positive near source).
    Higher V near source => higher p_stay => packet drifts toward source.
    This is the OPPOSITE sign from the Coulomb/EM potential (V = -STRENGTH/r).
    The standard Newton potential phi = -GM/r corresponds to V_lattice = +GM/r;
    the sign flip is because the lattice steers toward higher V (higher clock
    density), while Newton's law is F = -m grad phi (toward lower phi).
    """
    x = np.arange(grid, dtype=float)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    r = np.sqrt((xx-cx)**2 + (yy-cy)**2 + (zz-cz)**2)
    return +STRENGTH / (r + SOFTENING)


def density_com(density):
    total = float(density.sum())
    if total < 1e-12:
        return (0., 0., 0.)
    x = np.arange(density.shape[0], dtype=float)
    cx = float(np.einsum('ijk,i->', density, x) / total)
    cy = float(np.einsum('ijk,j->', density, np.arange(density.shape[1], dtype=float)) / total)
    cz = float(np.einsum('ijk,k->', density, np.arange(density.shape[2], dtype=float)) / total)
    return (cx, cy, cz)


def dist3(a, b):
    return float(np.sqrt(sum((a[i]-b[i])**2 for i in range(3))))


def make_packet(grid, start, omega, width):
    """Zero-momentum Gaussian spinor packet at start."""
    x = np.arange(grid, dtype=float)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    sx, sy, sz = start
    env = np.exp(-0.5*((xx-sx)**2+(yy-sy)**2+(zz-sz)**2)/width**2).astype(complex)
    psi = env / np.sqrt(2.0)   # split equally between R and L

    lat = OctahedralLattice(grid, grid, grid)
    sess = CausalSession(lat, start, instruction_frequency=omega)
    sess.psi_R = psi.copy()
    sess.psi_L = psi.copy()
    enforce_unity_spinor(sess.psi_R, sess.psi_L)

    # Set the gravitational clock density potential from the well at WC
    sess.lattice.topological_potential = grav_potential(grid, *WC)

    return sess


def measure_acceleration(r, verbose=False):
    """
    Initialize packet at distance r from WC along V1=(1,1,1) direction.
    Run TICKS ticks with windowed CoM smoothing (WIN-tick averages) to
    kill Zitterbewegung. Fit parabola to smoothed r(t) over FIT_TICKS
    to extract the initial acceleration a = d²r/dt²|_{t=0}.

    Returns (r, a, a*r², displacement_at_TICKS).
    """
    dr = r / np.sqrt(3.0)
    start = tuple(int(round(WC[i] + dr)) for i in range(3))
    start = tuple(max(2, min(GRID-3, s)) for s in start)

    sess = make_packet(GRID, start, OMEGA, WIDTH)

    # Windowed density accumulation
    win_dens  = None
    win_coms  = []   # one CoM per WIN-tick window

    r0 = dist3(density_com(sess.probability_density()), WC)

    for tick in range(TICKS):
        sess.tick()
        sess.advance_tick_counter()
        dens = sess.probability_density()
        win_dens = dens.astype(float) if win_dens is None else win_dens + dens

        if (tick + 1) % WIN == 0:
            com = density_com(win_dens)
            win_coms.append(dist3(com, WC))
            win_dens = None

    win_coms = np.array(win_coms)   # shape: (TICKS//WIN,)

    # Time axis in ticks (window centres)
    t_win = np.arange(1, len(win_coms) + 1, dtype=float) * WIN - WIN / 2.0

    # Fit parabola r(t) = r0 - (1/2)*|a|*t² over first FIT_TICKS ticks
    # Use only windows within the fit range
    fit_mask = t_win <= FIT_TICKS
    t_fit  = t_win[fit_mask]
    dr_fit = win_coms[fit_mask] - r0   # displacement (negative = toward well)

    # Least-squares fit: dr = (1/2)*a*t²  (v0=0 by construction)
    half_a = float(np.dot(dr_fit, t_fit**2) / np.dot(t_fit**2, t_fit**2))
    a = 2.0 * half_a   # acceleration (negative = toward well)

    displacement = r0 - win_coms[-1]   # positive = net motion toward well

    if verbose:
        print(f"  r={r:4d}  r0={r0:.3f}  a={a:+.7f}"
              f"  a*r²={a*r**2:+.5f}  disp={displacement:+.4f}"
              f"  V(r)/omega={STRENGTH/(r+SOFTENING)/OMEGA:.3f}")

    return r, a, a * r**2, displacement


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    print("=" * 65)
    print("EXP 02b: Inverse-square force law numerical verification")
    print("=" * 65)
    print(f"""
  Prediction: gravitational acceleration a = GM/r²
  Test: a·r² = constant across r = {DISTANCES}

  Parameters:
    GRID={GRID}^3  OMEGA={OMEGA}  WIDTH={WIDTH}
    STRENGTH={STRENGTH}  SOFTENING={SOFTENING}
    TICKS={TICKS}  (parabola fit over first 10 ticks)
""")

    t0 = time.time()
    results = []

    print(f"  {'r':>5}  {'V/omega':>8}  {'a':>12}  {'a*r²':>10}  {'disp':>8}")
    print(f"  {'-'*52}")

    for r in DISTANCES:
        r_val, a, ar2, disp = measure_acceleration(r, verbose=False)
        results.append((r_val, a, ar2, disp))
        vr = STRENGTH / (r + SOFTENING) / OMEGA
        print(f"  {r_val:5d}  {vr:8.3f}  {a:12.7f}  {ar2:10.5f}  {disp:8.4f}")

    # ── Pass criterion ────────────────────────────────────────────────
    ar2_values = np.array([r[2] for r in results])
    # All accelerations should be negative (toward well)
    # a*r² should be approximately constant
    # Use the mean of the middle three points as reference
    ref = float(np.mean(ar2_values[1:-1]))
    deviations = np.abs((ar2_values - ref) / ref)
    max_dev = float(deviations.max())

    print(f"\n  a*r² values: mean={ref:.4f}  max_deviation={max_dev:.3f} ({max_dev*100:.1f}%)")
    print(f"  All accelerations toward well: {all(a < 0 for _, a, _, _ in results)}")

    passed = (max_dev < 0.20 and all(a < 0 for _, a, _, _ in results))

    print(f"\n  {'='*65}")
    if passed:
        print(f"  [PASS] a*r² constant to {max_dev*100:.1f}% -- inverse-square law confirmed.")
        print(f"  Residual variation attributable to finite packet width")
        print(f"  (sigma/r correction of order (WIDTH/r)² ~ {(WIDTH/DISTANCES[0])**2*100:.0f}%"
              f" at r={DISTANCES[0]}, ~{(WIDTH/DISTANCES[-1])**2*100:.0f}% at r={DISTANCES[-1]}).")
    else:
        if not all(a < 0 for _, a, _, _ in results):
            print(f"  [FAIL] Some accelerations not toward well.")
        else:
            print(f"  [FAIL] a*r² variation {max_dev*100:.1f}% exceeds 20% threshold.")
            print(f"  Consider: more ticks for parabola fit, larger grid, or")
            print(f"  narrower packet (WIDTH) relative to r.")

    # Save
    out = os.path.join(_DATA_DIR, 'exp_02b_inverse_square.npy')
    np.save(out, np.array(results))
    print(f"\n  Saved: {out}")
    print(f"  columns: r, a, a*r², displacement@{TICKS}ticks")
    print(f"  Total time: {time.time()-t0:.1f}s")

    return passed


if __name__ == '__main__':
    passed = run()
    sys.exit(0 if passed else 1)
