"""
exp_16_proton_mass_sweep.py
Proton mass sweep: settling time vs. OMEGA_P.

Tests the symmetry-breaking prediction from notes/proton_symmetry_breaking.md:

  The live proton's recoil breaks the spherical symmetry of the Coulomb
  potential, providing the perturbation that allows the electron to find
  the resonance attractor (Bohr orbit).  Heavier proton = less recoil =
  slower symmetry breaking = longer settling time.

  Prediction: T_settle increases monotonically with OMEGA_P (proton mass).

For each OMEGA_P the electron is initialized at R_INIT = R1(OMEGA_P) * 1.05
with K_INIT = K_BOHR in the two-body CoM frame (same as exp_15/exp_12).
T_settle is the first tick at which the time-averaged electron PDF peak
falls within SETTLE_TOL of R1.

The physical proton sits at OMEGA_P = pi/2 (maximum lattice mass).
Lighter OMEGA_P values test whether a less-massive nucleus settles faster.
Expected shape: T_settle ~ 1/recoil_amplitude ~ M_P ~ sin(OMEGA_P/2).

At very low OMEGA_P the proton becomes too mobile -- the two-body system
may become unbound.  The minimum OMEGA_P for stable orbital formation is
a structural prediction about why the proton mass has the value it does.

Paper reference: Section on two-body orbital dynamics and ground state selection.
"""

import sys, os, time
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession, enforce_unity_spinor
from src.core.TickScheduler import TickScheduler

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')

# ── Fixed parameters ───────────────────────────────────────────────────────────
OMEGA_E   = 0.1019
STRENGTH  = 30.0
SOFTENING = 0.5
WIDTH_E   = 1.5
WIDTH_P   = 0.5
R1_REF    = 10.3       # exp_12 two-body Bohr radius at OMEGA_P = pi/2
K_BOHR    = 1.0 / R1_REF

M_E = np.sin(OMEGA_E) / 2.0

GAMMA     = float(np.sin(OMEGA_E / 2.0)**2 * np.cos(OMEGA_E / 2.0)**2)

GRID      = 65
TICKS     = 16000
BURN_IN   = 500        # shorter burn-in: we want to detect early settling
N_BINS    = 100
SETTLE_TOL = 0.15      # PDF peak within 15% of R1 counts as settled

# OMEGA_P sweep: from light (fast recoil) to heavy (slow recoil).
# pi/2 is the physical proton (maximum lattice mass).
OMEGA_P_VALUES = [0.3, 0.5, 0.7, 0.9, 1.1, 1.3, np.pi / 2.0]


# ── Helpers ────────────────────────────────────────────────────────────────────

def r1_for_omega_p(omega_p):
    """
    Effective Bohr radius for a given proton mass.
    R1 scales with reduced mass: R1 ~ 1/mu = (M_E + M_P) / (M_E * M_P).
    Normalised to R1_REF at OMEGA_P = pi/2.
    """
    m_p     = np.sin(omega_p / 2.0)
    mu      = M_E * m_p / (M_E + m_p)
    mu_ref  = M_E * np.sin(np.pi / 4.0) / (M_E + np.sin(np.pi / 4.0))
    return R1_REF * mu_ref / mu


def coulomb_potential_array(grid, cx, cy, cz, strength, softening):
    x = np.arange(grid)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    r = np.sqrt((xx - cx)**2 + (yy - cy)**2 + (zz - cz)**2)
    return -strength / (r + softening)


def density_com(density):
    total = float(density.sum())
    if total < 1e-12:
        return (0.0, 0.0, 0.0)
    x = np.arange(density.shape[0])
    cx = float(np.einsum('ijk,i->', density, x) / total)
    cy = float(np.einsum('ijk,j->', density, np.arange(density.shape[1])) / total)
    cz = float(np.einsum('ijk,k->', density, np.arange(density.shape[2])) / total)
    return (cx, cy, cz)


def make_sessions(grid, wc, omega_p, r1):
    """Two-body CoM frame initialization, same as exp_12/exp_15."""
    m_p   = np.sin(omega_p / 2.0)
    r_p_com = r1 * M_E / m_p
    dr_e  = r1 * 1.05 / np.sqrt(3.0)
    dr_p  = r_p_com / np.sqrt(3.0)
    k_p   = K_BOHR * M_E / m_p

    sz = grid
    start_e = tuple(min(int(round(wc[i] + dr_e)), sz - 2) for i in range(3))
    start_p = tuple(max(int(round(wc[i] - dr_p)), 1)       for i in range(3))

    x = np.arange(sz)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')

    sx, sy, sz_ = start_e
    env_e = (np.exp(-0.5 * ((xx-sx)**2 + (yy-sy)**2 + (zz-sz_)**2) / WIDTH_E**2)
             * np.exp(1j * K_BOHR * (xx - yy - zz)))
    amp_e = env_e.astype(complex) / np.sqrt(2.0)
    lat_e = OctahedralLattice(sz, sz, sz)
    electron = CausalSession(lat_e, start_e, instruction_frequency=OMEGA_E)
    electron.psi_R = amp_e.copy()
    electron.psi_L = amp_e.copy()
    enforce_unity_spinor(electron.psi_R, electron.psi_L)

    px, py, pz = start_p
    env_p = (np.exp(-0.5 * ((xx-px)**2 + (yy-py)**2 + (zz-pz)**2) / WIDTH_P**2)
             * np.exp(1j * k_p * (-xx + yy + zz)))
    amp_p = env_p.astype(complex) / np.sqrt(2.0)
    lat_p = OctahedralLattice(sz, sz, sz)
    proton = CausalSession(lat_p, start_p, instruction_frequency=omega_p)
    proton.psi_R = amp_p.copy()
    proton.psi_L = amp_p.copy()
    enforce_unity_spinor(proton.psi_R, proton.psi_L)

    lat_ph = OctahedralLattice(sz, sz, sz)
    photon = CausalSession(lat_ph, start_e, instruction_frequency=0.0,
                           is_massless=True)

    return electron, proton, photon, start_e, start_p


def run_one(omega_p):
    """
    Run one OMEGA_P trial.  Returns (T_settle, r_final, settled).
    T_settle = first tick where PDF peak is within SETTLE_TOL of R1,
               or TICKS if never settled.
    """
    r1  = r1_for_omega_p(omega_p)
    m_p = np.sin(omega_p / 2.0)
    wc  = (GRID // 2,) * 3

    electron, proton, photon, start_e, start_p = make_sessions(GRID, wc, omega_p, r1)

    e_com0 = density_com(electron.probability_density())
    p_com0 = density_com(proton.probability_density())
    electron.lattice.topological_potential = coulomb_potential_array(
        GRID, *p_com0, STRENGTH, SOFTENING)
    proton.lattice.topological_potential = coulomb_potential_array(
        GRID, *e_com0, STRENGTH, SOFTENING)

    scheduler = TickScheduler()
    e_idx  = scheduler.register_session(electron)
    pr_idx = scheduler.register_session(proton)
    ph_idx = scheduler.register_session(photon)
    scheduler.register_emission(e_idx, ph_idx, pr_idx, rate=GAMMA)

    x = np.arange(GRID)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    r_arr = np.sqrt((xx - wc[0])**2 + (yy - wc[1])**2 + (zz - wc[2])**2)
    r_max = float(r_arr.max())
    bin_edges = np.linspace(0, r_max, N_BINS + 1)
    r_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    T_settle  = TICKS   # default: never settled
    settled   = False
    acc_dens  = None
    r_final   = 0.0

    for tick in range(TICKS):
        e_dens = electron.probability_density()
        p_dens = proton.probability_density()
        e_com  = density_com(e_dens)
        p_com  = density_com(p_dens)

        electron.lattice.topological_potential = coulomb_potential_array(
            GRID, *p_com, STRENGTH, SOFTENING)
        proton.lattice.topological_potential = coulomb_potential_array(
            GRID, *e_com, STRENGTH, SOFTENING)

        if tick % 2 == 0:
            proton.tick();   proton.advance_tick_counter()
            electron.tick(); electron.advance_tick_counter()
            photon.tick();   photon.advance_tick_counter()
        else:
            electron.tick(); electron.advance_tick_counter()
            proton.tick();   proton.advance_tick_counter()
            photon.tick();   photon.advance_tick_counter()

        scheduler._apply_emission_pairs()

        if tick >= BURN_IN:
            acc_dens = e_dens if acc_dens is None else acc_dens + e_dens

            # Check settling: PDF peak within SETTLE_TOL of r1
            if not settled:
                P, _ = np.histogram(r_arr.ravel(), bins=bin_edges,
                                    weights=acc_dens.ravel())
                P /= (P.sum() + 1e-12)
                r_peak = r_centers[int(np.argmax(P))]
                if abs(r_peak - r1) / r1 < SETTLE_TOL:
                    T_settle = tick
                    settled  = True

    if acc_dens is not None:
        P, _ = np.histogram(r_arr.ravel(), bins=bin_edges,
                            weights=acc_dens.ravel())
        P /= (P.sum() + 1e-12)
        r_final = float(r_centers[int(np.argmax(P))])

    return T_settle, r_final, settled, r1


# ── Main ───────────────────────────────────────────────────────────────────────

def run():
    print("=" * 70)
    print("EXP 16: Proton mass sweep -- settling time vs. OMEGA_P")
    print("=" * 70)
    print(f"  Prediction: T_settle increases monotonically with OMEGA_P")
    print(f"  Physical proton: OMEGA_P = pi/2 = {np.pi/2:.4f}")
    print(f"  OMEGA_E={OMEGA_E}  STRENGTH={STRENGTH}  GAMMA={GAMMA:.6f}")
    print(f"  Grid={GRID}^3  TICKS={TICKS}  SETTLE_TOL={SETTLE_TOL*100:.0f}%")
    print(f"\n  {'OMEGA_P':>8}  {'M_P':>7}  {'R1':>7}  {'T_settle':>9}"
          f"  {'r_final':>8}  {'settled':>8}")
    print(f"  {'-'*60}")

    results = []
    t0_total = time.time()

    for omega_p in OMEGA_P_VALUES:
        m_p = float(np.sin(omega_p / 2.0))
        t0 = time.time()
        T_settle, r_final, settled, r1 = run_one(omega_p)
        elapsed = time.time() - t0
        marker = ' <- physical proton' if abs(omega_p - np.pi/2) < 0.01 else ''
        print(f"  {omega_p:8.4f}  {m_p:7.4f}  {r1:7.3f}  {T_settle:9d}"
              f"  {r_final:8.3f}  {str(settled):>8}  [{elapsed:.0f}s]{marker}")
        results.append((omega_p, m_p, r1, T_settle, r_final, int(settled)))

    total_elapsed = time.time() - t0_total

    print(f"\n{'='*70}")
    print(f"RESULT")
    print(f"{'='*70}")

    arr = np.array(results)
    omega_p_arr  = arr[:, 0]
    m_p_arr      = arr[:, 1]
    t_settle_arr = arr[:, 3]
    settled_arr  = arr[:, 5]

    # Check monotonicity
    settled_mask = settled_arr.astype(bool)
    if settled_mask.sum() >= 2:
        t_settled = t_settle_arr[settled_mask]
        op_settled = omega_p_arr[settled_mask]
        monotone = bool(np.all(np.diff(t_settled) >= 0))
        print(f"\n  Settled runs: {int(settled_mask.sum())}/{len(OMEGA_P_VALUES)}")
        print(f"  T_settle monotonically increasing with OMEGA_P: {monotone}")
        corr = float(np.corrcoef(op_settled, t_settled)[0, 1])
        print(f"  Correlation(OMEGA_P, T_settle) = {corr:.4f}  (expect > 0)")
    else:
        print(f"\n  Only {int(settled_mask.sum())} run(s) settled -- insufficient for trend.")
        print(f"  Increase TICKS or SETTLE_TOL.")

    passed = (settled_mask.sum() >= 3 and
              (not settled_mask.sum() >= 2 or
               bool(np.all(np.diff(t_settle_arr[settled_mask]) >= 0))))

    if passed:
        print(f"\n[PASS] Settling time increases with proton mass.")
        print(f"  Proton recoil is the symmetry-breaking mechanism for ground state selection.")
    else:
        print(f"\n[PARTIAL] Trend not confirmed -- see per-OMEGA_P results above.")

    print(f"\n  Total time = {total_elapsed:.0f}s ({total_elapsed/3600:.2f} hrs)")

    out = os.path.join(_DATA_DIR, 'exp_16_proton_mass_sweep.npy')
    np.save(out, arr)
    print(f"\nSaved: {out}")
    print(f"  columns: omega_p, m_p, r1, T_settle, r_final, settled")

    return passed


if __name__ == '__main__':
    passed = run()
    sys.exit(0 if passed else 1)
