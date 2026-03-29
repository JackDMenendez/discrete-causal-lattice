"""
exp_14_helium.py
Helium-like system: fixed Z=2 nucleus + two electrons.

Builds directly on exp_13 (H-: Z=1 nucleus + two electrons).
Key difference: the nuclear charge is doubled (STRENGTH_PE = 2 * STRENGTH_BASE),
while the electron-electron repulsion keeps the single-charge strength
(STRENGTH_EE = STRENGTH_BASE).

The Z=2/Z=1 ratio tests whether the stronger nuclear attraction can:
  1. Pull the equilibrium radius inward vs the H- result (r_mean ~ 27 nodes)
  2. Break the classical symmetry: one electron pulled tighter, the other
     forced to a larger orbit by combined nuclear attraction + e-e repulsion-
  3. Produce the classical antipodal configuration (180 deg separation)-

Physical reference
------------------
Real helium: both electrons bind at n=1 with total energy ~ -79 eV.
Lattice analog: both sessions should find stable orbits at r < R1_APPROX.
The classical (mean-field, no antisymmetrisation) prediction:
  - Both electrons at the same radius (classical symmetry)
  - Angular separation -> 180 deg (e-e repulsion pushes them to opposite sides)
  - Equilibrium radius smaller than H- result because nuclear force is stronger

The critical question for the periodic table:
  If BOTH electrons bind tightly at n=1 (ratio ~ 1), then adding a THIRD
  electron (lithium) will require that electron to sit further out.
  Without antisymmetrisation, the third electron may also pile into n=1
  (wrong), which is the definitive test of where the framework's
  fermion physics breaks down.

Measurements
------------
  r_mean_e1, r_mean_e2    -- equilibrium orbital radii
  r_inner / r_outer       -- are they at the same orbit or different-
  angle_mean              -- mean angular separation (degrees) between
                             e1_com and e2_com relative to nucleus
                             Classical prediction: ~180 deg
                             Quantum (delocalized): no preferred angle

Tests
-----
  1. Single-electron He+: one electron in the Z=2 (STRENGTH_PE=60) well.
     Measures the effective He+ Bohr radius on this lattice.
     Expected: r_mean < R1_APPROX (tighter orbit than hydrogen, Z=2 pulls harder).

  2. Two-electron helium: both electrons + mutual e-e repulsion.
     Compares equilibrium to H- result (exp_13: r_mean ~ 27 nodes).
     Expected: smaller radius (nuclear force wins over repulsion for Z=2).

Paper reference: Section 11 (Spontaneous Quantization -- Helium and Shell Structure)
"""

import sys, os, time
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession, enforce_unity_spinor

# -- Physical parameters --------------------------------------------------------
OMEGA_E       = 0.1019        # electron instruction frequency
STRENGTH_BASE = 30.0          # single-charge Coulomb strength (from exp_10/11/12)
STRENGTH_PE   = 2 * STRENGTH_BASE   # = 60.0  proton-electron (Z=2 nucleus)
STRENGTH_EE   = STRENGTH_BASE       # = 30.0  electron-electron (one charge each)
SOFTENING     = 0.5
WIDTH_E       = 1.5

# -- Derived masses and geometry ------------------------------------------------
M_E = np.sin(OMEGA_E) / 2.0

# Use the hydrogen-calibrated k and R1 as starting point.
# With Z=2, the actual equilibrium radius will be smaller than R1_APPROX --
# the experiment measures where it actually settles.
K1_H         = 0.0971         # hydrogen k_min from exp_12
R1_H         = 10.3           # hydrogen Bohr radius (nodes)
R1_HE_THEORY = R1_H / 2.0    # unscreened He+ Bohr radius ~ 5.15 nodes

# Grid: same as exp_13 -- 67^3, center at 33.
# He orbits are expected smaller than H, so the grid is more than adequate.
GRID = 67
WC   = (GRID // 2,) * 3      # = (33, 33, 33)

# -- Run parameters -------------------------------------------------------------
TICKS_ORBIT  = 1000   # Test 1: single-electron He+ orbit
TICKS_SHELLS = 1500   # Test 2: two-electron helium
BURN_IN      = 200
N_BINS       = 100

# -- Helpers (identical to exp_13) ---------------------------------------------

def make_electron_ic(lat, wc, k, disp_raw, mom_raw):
    """Initialise electron at R1_H from centre. Same convention as exp_12/13."""
    sz = lat.size_x
    dr = R1_H / np.sqrt(3.0)
    dv = np.array(disp_raw, dtype=float)
    mv = np.array(mom_raw,  dtype=float)
    centre = tuple(
        int(np.clip(round(wc[i] + dr * np.sign(dv[i])), 1, sz - 2))
        for i in range(3)
    )
    x  = np.arange(sz)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    cx, cy, cz = centre
    env = (np.exp(-0.5 * ((xx-cx)**2 + (yy-cy)**2 + (zz-cz)**2) / WIDTH_E**2)
           * np.exp(1j * k * (mv[0]*xx + mv[1]*yy + mv[2]*zz)))
    amp = env.astype(complex) / np.sqrt(2.0)
    sess = CausalSession(lat, centre, instruction_frequency=OMEGA_E)
    sess.psi_R = amp.copy()
    sess.psi_L = amp.copy()
    enforce_unity_spinor(sess.psi_R, sess.psi_L)
    return sess, centre


def coulomb_potential_array(grid, cx, cy, cz, strength, softening):
    x  = np.arange(grid)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    r  = np.sqrt((xx - cx)**2 + (yy - cy)**2 + (zz - cz)**2)
    return -strength / (r + softening)


def density_com(density):
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


def angular_separation_deg(com1, com2, wc):
    """Angle (degrees) between the two electron positions relative to nucleus."""
    v1 = np.array([com1[i] - wc[i] for i in range(3)], dtype=float)
    v2 = np.array([com2[i] - wc[i] for i in range(3)], dtype=float)
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 < 1e-6 or n2 < 1e-6:
        return 0.0
    cos_t = float(np.dot(v1, v2) / (n1 * n2))
    return float(np.degrees(np.arccos(np.clip(cos_t, -1.0, 1.0))))


def precompute_radii(grid, wc):
    x  = np.arange(grid)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    return np.sqrt((xx - wc[0])**2 + (yy - wc[1])**2 + (zz - wc[2])**2)


def radial_mean(density, r_arr):
    total = density.sum()
    if total < 1e-12:
        return 0.0
    return float((density * r_arr).sum() / total)


def tick_single(electron):
    electron.tick()
    electron.advance_tick_counter()


def tick_pair(e1, e2, proton_pot, grid, softening):
    """Tick two electrons: fixed nucleus (proton_pot) + mutual e-e repulsion."""
    e1_com = density_com(e1.probability_density())
    e2_com = density_com(e2.probability_density())
    # e-e repulsion: negative strength -> repulsive potential
    V_ee_on_e1 = coulomb_potential_array(grid, *e2_com, -STRENGTH_EE, softening)
    V_ee_on_e2 = coulomb_potential_array(grid, *e1_com, -STRENGTH_EE, softening)
    e1.lattice.topological_potential = proton_pot + V_ee_on_e1
    e2.lattice.topological_potential = proton_pot + V_ee_on_e2
    if e1.tick_counter % 2 == 0:
        e1.tick(); e1.advance_tick_counter()
        e2.tick(); e2.advance_tick_counter()
    else:
        e2.tick(); e2.advance_tick_counter()
        e1.tick(); e1.advance_tick_counter()
    return e1_com, e2_com


# -- Test 1: Single-electron He+ orbit -----------------------------------------

def run_single_electron_he():
    """
    One electron in the Z=2 (STRENGTH_PE=60) Coulomb well.
    Measures the effective He+ Bohr radius on this lattice.
    Reference: exp_13 H single electron gave r_mean=13.7 nodes.
    He+ (Z=2) should give r_mean < 13.7 (tighter nuclear binding).
    """
    print("\n[Test 1] Single-electron He+ orbit  (STRENGTH_PE=60)")
    print(f"  K1_H={K1_H:.4f}  R1_H={R1_H:.3f} nodes  (hydrogen reference)")
    print(f"  R1_He_theory={R1_HE_THEORY:.3f} nodes  (unscreened Z=2 prediction)")

    lat = OctahedralLattice(GRID, GRID, GRID)
    electron, start = make_electron_ic(lat, WC, K1_H, (1,1,1), (1,-1,-1))
    print(f"  start: {start}  r_start={com_radius(start, WC):.3f}")

    proton_pot = coulomb_potential_array(GRID, *WC, STRENGTH_PE, SOFTENING)
    lat.topological_potential = proton_pot

    r_arr = precompute_radii(GRID, WC)
    r_history = []
    t0 = time.time()

    for tick in range(TICKS_ORBIT):
        tick_single(electron)
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
    print(f"\n  He+ r_mean={r_mean:.3f}  r_std={r_std:.3f}")
    print(f"  H   r_mean=13.670  (exp_13 reference)")
    print(f"  Ratio He+/H = {r_mean/13.670:.3f}  (expected < 1.0 for tighter Z=2 binding)")

    # Pass: electron is bound (not escaped to boundary)
    in_range = r_mean < GRID // 2 - 4
    return in_range, r_mean


# -- Test 2: Two-electron helium ------------------------------------------------

def run_helium_twobody(r_single):
    """
    Two electrons in the Z=2 well with mutual e-e repulsion (STRENGTH_EE=30).
    Measures equilibrium radius and angular separation.

    Key comparisons:
      exp_13 H-:  r_mean ~ 27 nodes, ratio ~ 1.03, no separation
      exp_14 He:  expected smaller r (Z=2 pulls harder), ratio ~ 1- angle ~ 180 deg-
    """
    print(f"\n[Test 2] Two-electron helium  "
          f"(STRENGTH_PE={STRENGTH_PE:.0f}, STRENGTH_EE={STRENGTH_EE:.0f})")
    print(f"  e1: V1=(1,1,1) displacement, V2 momentum")
    print(f"  e2: V2=(1,-1,-1) displacement, V3 momentum  (~109.5 deg apart)")

    lat1 = OctahedralLattice(GRID, GRID, GRID)
    lat2 = OctahedralLattice(GRID, GRID, GRID)
    e1, start1 = make_electron_ic(lat1, WC, K1_H, (1, 1, 1), ( 1,-1,-1))
    e2, start2 = make_electron_ic(lat2, WC, K1_H, (1,-1,-1), (-1, 1,-1))
    print(f"  e1 start: {start1}  e2 start: {start2}")

    proton_pot = coulomb_potential_array(GRID, *WC, STRENGTH_PE, SOFTENING)
    lat1.topological_potential = proton_pot.copy()
    lat2.topological_potential = proton_pot.copy()

    r1_history    = []
    r2_history    = []
    angle_history = []
    t0 = time.time()

    for tick in range(TICKS_SHELLS):
        e1_com, e2_com = tick_pair(e1, e2, proton_pot, GRID, SOFTENING)
        r1_history.append(com_radius(e1_com, WC))
        r2_history.append(com_radius(e2_com, WC))
        angle_history.append(angular_separation_deg(e1_com, e2_com, WC))
        if (tick + 1) % 300 == 0:
            elapsed = time.time() - t0
            eta     = elapsed / (tick + 1) * (TICKS_SHELLS - tick - 1)
            print(f"    tick {tick+1:4d}/{TICKS_SHELLS}  "
                  f"r1={r1_history[-1]:.2f}  r2={r2_history[-1]:.2f}  "
                  f"angle={angle_history[-1]:.1f} deg  "
                  f"elapsed={elapsed:.0f}s  ETA={eta:.0f}s")

    r1_arr  = np.array(r1_history[BURN_IN:])
    r2_arr  = np.array(r2_history[BURN_IN:])
    ang_arr = np.array(angle_history[BURN_IN:])

    r1_mean    = float(np.mean(r1_arr))
    r2_mean    = float(np.mean(r2_arr))
    angle_mean = float(np.mean(ang_arr))
    angle_std  = float(np.std(ang_arr))

    r_inner = min(r1_mean, r2_mean)
    r_outer = max(r1_mean, r2_mean)
    ratio   = r_outer / max(r_inner, 0.1)

    print(f"\n  Electron 1:  r_mean={r1_mean:.3f}")
    print(f"  Electron 2:  r_mean={r2_mean:.3f}")
    print(f"  r_inner={r_inner:.3f}  r_outer={r_outer:.3f}  ratio={ratio:.3f}")
    print(f"  Angular separation:  mean={angle_mean:.1f} deg  std={angle_std:.1f} deg")
    print(f"    Classical prediction: ~180 deg (antipodal)")
    print(f"    Quantum (delocalized): uniform distribution, no preferred angle")
    print(f"\n  He equilibrium vs H- equilibrium:")
    print(f"    H-  (exp_13): r_mean ~ 27 nodes  (both at ~2.6 * R1_H)")
    print(f"    He  (exp_14): r_mean ~ {(r1_mean+r2_mean)/2:.1f} nodes  "
          f"(both at ~{(r1_mean+r2_mean)/2/10.3:.2f} * R1_H)")
    print(f"    He single:    r_mean = {r_single:.3f} nodes")
    print(f"    He two-body:  r_mean = {(r1_mean+r2_mean)/2:.3f} nodes  "
          f"(repulsion adds ~{(r1_mean+r2_mean)/2 - r_single:.1f} nodes)")

    # Pass: both electrons bounded and He radius smaller than H- radius
    both_bounded = r_outer < GRID // 2 - 4
    he_tighter   = (r1_mean + r2_mean) / 2 < 27.0   # smaller than H- result
    return (both_bounded and he_tighter), r1_mean, r2_mean, angle_mean, ratio


# -- Main -----------------------------------------------------------------------

def run_helium_audit(datadir=None):
    print("=" * 65)
    print("EXPERIMENT 14: Helium-Like System (Z=2 Nucleus + Two Electrons)")
    print("=" * 65)
    print(f"\n  omega_e      = {OMEGA_E:.4f}   M_E = {M_E:.4f}")
    print(f"  STRENGTH_PE  = {STRENGTH_PE:.1f}  (Z=2 nucleus: 2 * {STRENGTH_BASE:.0f})")
    print(f"  STRENGTH_EE  = {STRENGTH_EE:.1f}  (e-e repulsion: 1 * {STRENGTH_BASE:.0f})")
    print(f"  PE/EE ratio  = {STRENGTH_PE/STRENGTH_EE:.1f}  (nuclear charge dominates)")
    print(f"  Grid = {GRID}^3  wc = {WC}")
    print(f"\n  Comparison targets:")
    print(f"    H   single (exp_13): r_mean = 13.7 nodes")
    print(f"    H-  two-body (exp_13): r_mean ~ 27 nodes  (both at same radius)")
    print(f"    He  single (theory): r_mean ~ {R1_HE_THEORY:.1f} nodes  (Z=2, unscreened)")
    print(f"    He  two-body (classical): r_mean < 27-  angle ~ 180 deg-")

    t1_pass, r_single    = run_single_electron_he()
    t2_pass, r_e1, r_e2, angle, ratio = run_helium_twobody(r_single)

    if datadir is not None:
        os.makedirs(datadir, exist_ok=True)
        result = np.array([[r_single, r_e1, r_e2, angle, ratio,
                            STRENGTH_PE, STRENGTH_EE]])
        out = os.path.join(datadir, 'exp_14_helium.npy')
        np.save(out, result)
        print(f"\nSaved: {out}  columns: r_single, r_e1, r_e2, angle_mean, ratio, STRENGTH_PE, STRENGTH_EE")

    print("\n" + "=" * 65)
    all_pass = t1_pass and t2_pass
    r_avg_he = (r_e1 + r_e2) / 2
    print(f"[{'AUDIT PASSED' if all_pass else 'AUDIT PARTIAL'}] "
          f"Helium-like two-electron system.")
    print(f"  Test 1 (He+ single):    {'PASS' if t1_pass else 'FAIL'}  "
          f"r_mean={r_single:.3f}  (H reference: 13.7)")
    print(f"  Test 2 (He two-body):   {'PASS' if t2_pass else 'FAIL'}  "
          f"r_avg={r_avg_he:.3f}  angle={angle:.1f} deg  ratio={ratio:.3f}")
    print(f"\n  Nuclear charge effect:  He r_avg={r_avg_he:.1f}  vs  H- r_avg~27")
    if r_avg_he < 20:
        print(f"  STRONG nuclear binding: He pulls electrons significantly inward")
    elif r_avg_he < 27:
        print(f"  MODERATE nuclear binding: He pulls electrons inward vs H-")
    else:
        print(f"  WEAK nuclear binding: Z=2 nuclear charge not sufficient to pull inward")

    if angle > 150:
        print(f"  ANTIPODAL: electrons settle on opposite sides of nucleus (~180 deg)")
        print(f"  -> Classical mean-field confirmed; no quantum delocalization.")
    elif angle > 90:
        print(f"  PARTIAL ANTIPODAL: electrons prefer wide separation but not 180 deg")
    else:
        print(f"  NO PREFERRED ANGLE: consistent with quantum delocalization")

    return all_pass


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--datadir', default=None,
                    help='Directory to save exp_14_helium.npy')
    args = ap.parse_args()
    passed = run_helium_audit(datadir=args.datadir)
    sys.exit(0 if passed else 1)
