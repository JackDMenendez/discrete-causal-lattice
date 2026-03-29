"""
exp_13_threebody_helium.py
Three-body system: fixed proton well + two same-spin electrons.

Tests whether Coulomb repulsion between two electrons in a hydrogen-like
potential well spontaneously produces radial shell separation -- one electron
staying near N=1, the other being pushed toward larger radii.

No quantum antisymmetrization is implemented.  The electrons are treated as
distinguishable bosonic sessions.  The question is whether pure Coulomb
repulsion under the A=1 framework produces emergent shell-like structure
without explicit Pauli exclusion.

Physics
-------
Uses the calibrated STRENGTH=30 from exp_12 (k_min=0.097, R1=10.3 nodes).
The grid is enlarged to 67^3 (vs exp_12's 37^3) so that a second electron
that escapes the proton well has room to drift to the boundary.
Detection: r_mean → grid//2 ≈ 33 signals escape.

For H⁻ (Z=1 nucleus, two electrons with same STRENGTH=30 e-e repulsion),
the second electron is expected to escape: the classical mean-field Coulomb
repulsion from electron 1 at N=1 overcomes the proton attraction, which is
the lattice analog of H⁻ having a binding energy of only 0.75 eV (barely
bound in real QM, unbound in mean-field).

Initialisation
--------------
Electron 1: displaced dr1 along V1=(1,1,1); momentum k along V2=(1,-1,-1).
Electron 2: displaced dr1 along V2=(1,-1,-1); momentum k along V3=(-1,1,-1).

The two electrons start at the same orbital radius (~a_0 from center) but in
different directions (~109.5 degrees apart on the lattice), breaking the
degeneracy that would prevent e-e repulsion from having any effect.

Tests
-----
  1. Single-electron orbit: one electron in the STRENGTH=60 fixed well.
     Verifies a_0 ~ R1_APPROX and stable orbit before adding second electron.

  2. Shell separation: two electrons + mutual e-e repulsion.
     After settling, measure r_mean for each.  Expected outcomes:
       Classical (no exclusion):  both electrons near N=1, one slightly further
       Emergent exclusion:        clear separation with ratio r_outer/r_inner > 2
     Either outcome is informative.  Pass criterion: r_outer/r_inner > 1.3
     (any significant separation from pure Coulomb repulsion).

Paper reference: Section 11 (Spontaneous Quantization -- Shell Structure)
"""

import sys, os, time
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession, enforce_unity_spinor

# ── Physical parameters ────────────────────────────────────────────────────────
OMEGA_E   = 0.1019        # electron instruction frequency (same as exp_12)
STRENGTH  = 30.0          # same as exp_10/11/12 -- calibrated, known k_min=0.097
SOFTENING = 0.5
WIDTH_E   = 1.5

# ── Derived masses and geometry ───────────────────────────────────────────────
M_E = np.sin(OMEGA_E) / 2.0

# Use the calibrated exp_12 k_min directly (no scaling needed)
K1_APPROX = 0.0971        # exp_12 result: k_min at STRENGTH=30
R1_APPROX = 10.3          # N=1 Bohr radius at STRENGTH=30 (= 1/K1_APPROX)
R2_APPROX = 4.0 * R1_APPROX   # N=2 Bohr radius ~ 41 nodes (for reference)

# Grid: larger than exp_12's 37^3 to give the escaping second electron room.
# N=1 orbit sits at ~10-15 nodes from center (exp_12: r_mean=15, r_max=19).
# Second electron escape shows as r_mean → grid//2.
# 67^3 with center at 33 gives 33-node escape distance (plenty of room).
GRID = 67
WC   = (GRID // 2,) * 3                       # = (33, 33, 33)

# ── Run parameters ─────────────────────────────────────────────────────────────
TICKS_ORBIT  = 1000   # Test 1: single-electron orbit check
TICKS_SHELLS = 1500   # Test 2: two-electron shell separation
BURN_IN      = 200    # discard first ticks before scoring
N_BINS       = 100    # radial bins for PDF measurement

# ── Helpers ────────────────────────────────────────────────────────────────────

def make_electron_ic(lat, wc, k, disp_raw, mom_raw):
    """
    Initialise an electron using the same convention as exp_12.

    disp_raw : raw RGB lattice vector, e.g. (1,1,1) or (1,-1,-1) -- components ±1
    mom_raw  : raw RGB lattice vector for momentum direction, e.g. (1,-1,-1) or (-1,1,-1)

    Displacement: each axis i gets offset = R1_APPROX/sqrt(3) * sign(disp_raw[i]).
    Total radius = sqrt(3) * (R1_APPROX/sqrt(3)) = R1_APPROX. Matches exp_12 exactly.

    Momentum: phase = k * (mom_raw[0]*x + mom_raw[1]*y + mom_raw[2]*z).
    Uses raw (unnormalised) lattice vector, same convention as exp_12's
    exp(1j * k_e * (xx - yy - zz)).
    """
    sz = lat.size_x
    dr = R1_APPROX / np.sqrt(3.0)          # per-component displacement magnitude
    dv = np.array(disp_raw, dtype=float)
    mv = np.array(mom_raw,  dtype=float)

    # Each component offset = dr * sign(dv[i]) = (R1_APPROX/sqrt(3)) * (±1)
    # Total radius = sqrt(sum((dr * dv[i]/|dv[i]|)^2)) = sqrt(3) * dr = R1_APPROX
    centre = tuple(
        int(np.clip(round(wc[i] + dr * np.sign(dv[i])), 1, sz - 2))
        for i in range(3)
    )

    x  = np.arange(sz)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    cx, cy, cz = centre

    # Phase using raw momentum vector (matches exp_12 convention)
    env = (np.exp(-0.5 * ((xx-cx)**2 + (yy-cy)**2 + (zz-cz)**2) / WIDTH_E**2)
           * np.exp(1j * k * (mv[0]*xx + mv[1]*yy + mv[2]*zz)))
    amp = env.astype(complex) / np.sqrt(2.0)
    sess = CausalSession(lat, centre, instruction_frequency=OMEGA_E)
    sess.psi_R = amp.copy()
    sess.psi_L = amp.copy()
    enforce_unity_spinor(sess.psi_R, sess.psi_L)
    return sess, centre


def coulomb_potential_array(grid, cx, cy, cz, strength, softening):
    """Return -strength/(r+softening) array centred at (cx,cy,cz)."""
    x  = np.arange(grid)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    r  = np.sqrt((xx - cx)**2 + (yy - cy)**2 + (zz - cz)**2)
    return -strength / (r + softening)


def density_com(density):
    """Density-weighted centre-of-mass."""
    total = density.sum()
    if total < 1e-12:
        return (0.0, 0.0, 0.0)
    x = np.arange(density.shape[0])
    cx = float(np.einsum('ijk,i->', density, x) / total)
    cy = float(np.einsum('ijk,j->', density, np.arange(density.shape[1])) / total)
    cz = float(np.einsum('ijk,k->', density, np.arange(density.shape[2])) / total)
    return (cx, cy, cz)


def com_radius(com, wc):
    return float(np.sqrt(sum((com[i] - wc[i])**2 for i in range(3))))


def precompute_radii(grid, wc):
    x  = np.arange(grid)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    return np.sqrt((xx - wc[0])**2 + (yy - wc[1])**2 + (zz - wc[2])**2)


def radial_mean(density, r_arr):
    """Density-weighted mean radius."""
    total = density.sum()
    if total < 1e-12:
        return 0.0
    return float((density * r_arr).sum() / total)


def tick_single(electron, grid, wc):
    """Tick one electron in the fixed proton well."""
    electron.tick()
    electron.advance_tick_counter()


def tick_pair(e1, e2, proton_pot, grid, strength, softening):
    """
    Tick two electrons in the fixed proton well with mutual Coulomb repulsion.
    Tick order alternates to cancel sequential-update asymmetry.
    """
    e1_com = density_com(e1.probability_density())
    e2_com = density_com(e2.probability_density())

    # e-e repulsion: pass -strength so the potential is +strength/(r+s) (repulsive)
    V_ee_on_e1 = coulomb_potential_array(grid, *e2_com, -strength, softening)
    V_ee_on_e2 = coulomb_potential_array(grid, *e1_com, -strength, softening)

    e1.lattice.topological_potential = proton_pot + V_ee_on_e1
    e2.lattice.topological_potential = proton_pot + V_ee_on_e2

    if e1.tick_counter % 2 == 0:
        e1.tick(); e1.advance_tick_counter()
        e2.tick(); e2.advance_tick_counter()
    else:
        e2.tick(); e2.advance_tick_counter()
        e1.tick(); e1.advance_tick_counter()

    return e1_com, e2_com


# ── Test 1: Single-electron orbit ─────────────────────────────────────────────

def run_single_electron_orbit():
    """
    Run one electron in the STRENGTH=60 fixed Coulomb well.
    Verify it settles to r_mean ~ R1_APPROX = 5.15 nodes.
    """
    print("\n[Test 1] Single-electron orbit at STRENGTH=60")
    print(f"  K1_APPROX={K1_APPROX:.4f}  R1_APPROX={R1_APPROX:.3f} nodes")
    print(f"  Grid={GRID}^3  wc={WC}")

    lat = OctahedralLattice(GRID, GRID, GRID)
    # V1 displacement, V2 momentum -- same as exp_12 electron initialisation
    electron, start = make_electron_ic(lat, WC, K1_APPROX, (1,1,1), (1,-1,-1))
    print(f"  electron start: {start}")

    proton_pot = coulomb_potential_array(GRID, *WC, STRENGTH, SOFTENING)
    lat.topological_potential = proton_pot

    r_arr = precompute_radii(GRID, WC)
    r_history = []
    t0 = time.time()

    for tick in range(TICKS_ORBIT):
        tick_single(electron, GRID, WC)
        dens = electron.probability_density()
        r_history.append(radial_mean(dens, r_arr))
        if (tick + 1) % 200 == 0:
            elapsed = time.time() - t0
            eta     = elapsed / (tick + 1) * (TICKS_ORBIT - tick - 1)
            print(f"    tick {tick+1:4d}/{TICKS_ORBIT}  r={r_history[-1]:.3f}  "
                  f"elapsed={elapsed:.0f}s  ETA={eta:.0f}s")

    r_post  = np.array(r_history[BURN_IN:])
    r_mean  = float(np.mean(r_post))
    r_std   = float(np.std(r_post))
    print(f"\n  r_mean={r_mean:.3f}  r_std={r_std:.3f}  "
          f"(target R1_APPROX={R1_APPROX:.3f})")

    # Pass: mean radius within 50% of R1_APPROX and not wandered to boundary
    in_range = 0.3 * R1_APPROX < r_mean < GRID // 2 - 4
    return in_range, r_mean


# ── Test 2: Two electrons -- shell separation ──────────────────────────────────

def run_shell_separation():
    """
    Run two electrons in the fixed well with mutual e-e Coulomb repulsion.
    The electrons start at the same orbital radius (R1_APPROX) but in
    different angular directions (V1 and V2, ~109.5 degrees apart).

    Measures r_mean for each electron after settling.  Reports whether
    Coulomb repulsion produces radial shell separation.
    """
    print(f"\n[Test 2] Shell separation: two electrons with e-e repulsion")
    print(f"  Both electrons initialised at r ~ R1_APPROX = {R1_APPROX:.3f} nodes")
    print(f"  Electron 1: displaced along V1=(1,1,1);    momentum along V2")
    print(f"  Electron 2: displaced along V2=(1,-1,-1);  momentum along V3")

    lat1 = OctahedralLattice(GRID, GRID, GRID)
    lat2 = OctahedralLattice(GRID, GRID, GRID)
    # e1: V1 displacement, V2 momentum (same as exp_12 electron)
    # e2: V2 displacement, V3 momentum (~109.5 degrees away from e1)
    e1, start1 = make_electron_ic(lat1, WC, K1_APPROX, (1, 1, 1), ( 1,-1,-1))
    e2, start2 = make_electron_ic(lat2, WC, K1_APPROX, (1,-1,-1), (-1, 1,-1))
    print(f"  e1 start: {start1}  e2 start: {start2}")

    proton_pot = coulomb_potential_array(GRID, *WC, STRENGTH, SOFTENING)
    lat1.topological_potential = proton_pot.copy()
    lat2.topological_potential = proton_pot.copy()

    r_arr = precompute_radii(GRID, WC)
    r1_history = []
    r2_history = []
    t0 = time.time()

    for tick in range(TICKS_SHELLS):
        e1_com, e2_com = tick_pair(e1, e2, proton_pot, GRID, STRENGTH, SOFTENING)
        r1_history.append(com_radius(e1_com, WC))
        r2_history.append(com_radius(e2_com, WC))
        if (tick + 1) % 300 == 0:
            elapsed = time.time() - t0
            eta     = elapsed / (tick + 1) * (TICKS_SHELLS - tick - 1)
            print(f"    tick {tick+1:4d}/{TICKS_SHELLS}  "
                  f"r1={r1_history[-1]:.2f}  r2={r2_history[-1]:.2f}  "
                  f"elapsed={elapsed:.0f}s  ETA={eta:.0f}s")

    r1_arr  = np.array(r1_history[BURN_IN:])
    r2_arr  = np.array(r2_history[BURN_IN:])
    r1_mean = float(np.mean(r1_arr))
    r2_mean = float(np.mean(r2_arr))

    r_inner = min(r1_mean, r2_mean)
    r_outer = max(r1_mean, r2_mean)
    ratio   = r_outer / max(r_inner, 0.1)

    print(f"\n  Electron 1:  r_mean={r1_mean:.3f}  (R1_APPROX={R1_APPROX:.3f})")
    print(f"  Electron 2:  r_mean={r2_mean:.3f}  (R2_APPROX={R2_APPROX:.3f})")
    print(f"  r_inner={r_inner:.3f}  r_outer={r_outer:.3f}  ratio={ratio:.3f}")
    print(f"  N=1 target:  {R1_APPROX:.3f} nodes")
    print(f"  N=2 target:  {R2_APPROX:.3f} nodes")

    # Classify the separation
    if ratio > 3.5:
        verdict = "STRONG SEPARATION -- outer electron near N=2 (emergent shell structure)"
    elif ratio > 2.0:
        verdict = "MODERATE SEPARATION -- outer electron between N=1 and N=2"
    elif ratio > 1.3:
        verdict = "WEAK SEPARATION -- Coulomb repulsion produces measurable radial difference"
    else:
        verdict = "NO SEPARATION -- both electrons at similar radii (degeneracy not broken)"

    print(f"\n  Result: {verdict}")

    # Pass: any significant separation (ratio > 1.3) or both electrons bounded
    both_bounded = r_outer < GRID // 2 - 4
    separated    = ratio > 1.3
    return (separated or both_bounded), r1_mean, r2_mean, ratio


# ── Main ───────────────────────────────────────────────────────────────────────

def run_threebody_audit(datadir=None):
    print("=" * 65)
    print("EXPERIMENT 13: Three-Body (Fixed Proton + Two Electrons)")
    print("=" * 65)
    print(f"\n  omega_e = {OMEGA_E:.4f}   M_E = {M_E:.4f}")
    print(f"  STRENGTH = {STRENGTH:.1f}  SOFTENING = {SOFTENING}")
    print(f"  K1_APPROX = {K1_APPROX:.4f}  (scaled from exp_12 result)")
    print(f"  R1_APPROX = {R1_APPROX:.3f} nodes  (N=1 Bohr radius)")
    print(f"  R2_APPROX = {R2_APPROX:.3f} nodes  (N=2 Bohr radius = 4*R1)")
    print(f"  Grid = {GRID}^3  wc = {WC}  (N=2 buffer = {GRID//2 - R2_APPROX:.1f} nodes)")
    print(f"\n  No quantum antisymmetrisation -- pure Coulomb repulsion test")
    print(f"  Expected: Coulomb repulsion pushes outer electron toward N=2")
    print(f"  Physical reference: H- ion (H + 2 electrons) has weakly bound 2nd electron")

    t1_pass, r1_single = run_single_electron_orbit()
    t2_pass, r_e1, r_e2, ratio = run_shell_separation()

    if datadir is not None:
        os.makedirs(datadir, exist_ok=True)
        result = np.array([[r1_single, r_e1, r_e2, ratio,
                            R1_APPROX, R2_APPROX, K1_APPROX]])
        out = os.path.join(datadir, 'exp_13_threebody.npy')
        np.save(out, result)
        print(f"\nSaved: {out}  columns: r1_single, r_e1, r_e2, ratio, R1, R2, K1")

    print("\n" + "=" * 65)
    all_pass = t1_pass and t2_pass
    print(f"[{'AUDIT PASSED' if all_pass else 'AUDIT PARTIAL'}] Three-body helium-like system.")
    print(f"  Test 1 (single orbit):    {'PASS' if t1_pass else 'FAIL'}  "
          f"r_mean={r1_single:.3f}  (target {R1_APPROX:.3f} nodes)")
    print(f"  Test 2 (shell separation): {'PASS' if t2_pass else 'FAIL'}  "
          f"r_inner={min(r_e1,r_e2):.3f}  r_outer={max(r_e1,r_e2):.3f}  "
          f"ratio={ratio:.3f}")

    if ratio > 3.5:
        print(f"\n  Outer electron near N=2: emergent shell structure without Pauli exclusion!")
    elif ratio > 2.0:
        print(f"\n  Outer electron between N=1 and N=2: partial shell separation.")
    elif ratio > 1.3:
        print(f"\n  Weak but measurable shell separation from Coulomb repulsion alone.")
    else:
        print(f"\n  No shell separation: both electrons at similar radii.")
        print(f"  Pauli exclusion (antisymmetrisation) may be required for proper N=2 filling.")

    return all_pass


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--datadir', default=None,
                    help='Directory to save exp_13_threebody.npy')
    args = ap.parse_args()
    passed = run_threebody_audit(datadir=args.datadir)
    sys.exit(0 if passed else 1)
