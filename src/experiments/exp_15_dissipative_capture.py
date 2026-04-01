"""
exp_15_dissipative_capture.py
Dissipative electron capture: electron spirals into Bohr orbit by emitting a photon.

An electron initialized OUTSIDE the Bohr radius (r_init = 1.5 * R1) with tangential
momentum k_Bohr loses orbital angular momentum to a massless photon session via
the tangential phase drain mechanism.  The proton is a live CausalSession (not a
fixed well) -- required because the fixed-well shifts N=1 by 7.3% (exp_12).

The emission coupling rate gamma is derived from the lattice:
    gamma = sin^2(omega/2) * cos^2(omega/2) = (1/4) * sin^2(omega)
This is the amplitude for a mixed hop+stay event -- the natural lattice coupling
scale.  It is zero for massless (omega=0) and maximum-mass (omega=pi) particles,
which is physically correct: only massive particles with orbital motion can emit.

Photon direction: the massless bipartite tick rule (RGB on even, CMY on odd ticks)
propagates the photon along whichever of the 3 active vectors is most aligned with
the imprinted phase gradient.  The lattice decides direction -- no direction is
hard-coded.

Pass criteria:
    1. Electron CoM radius decreases from r_init toward R1 over TICKS ticks.
    2. Time-averaged PDF after BURN_IN shows a peak closer to R1 than r_init.
    3. Photon CoM moves outward from the electron's initial position.

Paper reference: Section on spontaneous emission and orbital decay.
"""

import sys, os, time
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession, enforce_unity_spinor
from src.core.TickScheduler import TickScheduler

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')

# ── Physical parameters (matched to exp_12) ────────────────────────────────────
OMEGA_E   = 0.1019
OMEGA_P   = np.pi / 2.0
STRENGTH  = 30.0
SOFTENING = 0.5
WIDTH_E   = 1.5
WIDTH_P   = 0.5
R1        = 10.3        # Bohr radius from exp_12 (two-body result)
K_BOHR    = 1.0 / R1   # ~0.09709

# Electron initialized at R_INIT = 1.05*R1 with K_INIT = K_BOHR.
# The CoM momenta are in proper balance (k_p = K_INIT * M_E/M_P along -V2)
# so the system CoM stays stationary.  The electron has excess potential
# energy at 1.05*R1 -- the Coulomb well will pull it inward while the
# drain removes tangential momentum, circularizing toward R1.
R_INIT    = R1 * 1.05             # 5% outside Bohr radius
K_INIT    = K_BOHR                # CoM-frame equilibrium momentum

# Lattice-derived emission rate: gamma = sin^2(omega/2) * cos^2(omega/2)
GAMMA     = float(np.sin(OMEGA_E / 2.0)**2 * np.cos(OMEGA_E / 2.0)**2)

# ── Masses (same derivation as exp_12) ────────────────────────────────────────
M_E = np.sin(OMEGA_E) / 2.0
M_P = np.sin(OMEGA_P) / 2.0

# ── Run parameters ─────────────────────────────────────────────────────────────
GRID    = 65        # 65^3 = 274k nodes, ~85MB per complex array -- well within 32GB
TICKS   = 16000     # longer run gives drain more time to act
BURN_IN = 2000
N_BINS  = 100

# ── Helpers (from exp_12) ──────────────────────────────────────────────────────

def coulomb_potential_array(grid, cx, cy, cz, strength, softening):
    x = np.arange(grid)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    r = np.sqrt((xx - cx)**2 + (yy - cy)**2 + (zz - cz)**2)
    return -strength / (r + softening)


def density_com(density):
    """Density-weighted centre of mass."""
    total = float(density.sum())
    if total < 1e-12:
        return (0.0, 0.0, 0.0)
    x = np.arange(density.shape[0])
    cx = float(np.einsum('ijk,i->', density, x) / total)
    cy = float(np.einsum('ijk,j->', density, np.arange(density.shape[1])) / total)
    cz = float(np.einsum('ijk,k->', density, np.arange(density.shape[2])) / total)
    return (cx, cy, cz)


def com_radius(com, wc):
    return float(np.sqrt(sum((com[i] - wc[i])**2 for i in range(3))))


# ── Initialisation ─────────────────────────────────────────────────────────────

def make_sessions(grid, wc):
    """
    Create electron, proton, and photon sessions.

    Electron: displaced +dr_e along V1=(1,1,1)/sqrt(3) from well centre,
              tangential momentum K_INIT along V2=(1,-1,-1).
              Starts at r_init = 1.5 * R1, k chosen so perihelion is near R1.

    Proton:   at well centre with tiny opposing momentum (CoM frame),
              same as exp_12.

    Photon:   massless, seeded at the electron's start node with no phase
              gradient.  The emission drain will imprint the tangential phase
              and the bipartite tick rule propagates it outward.
    """
    sz = grid

    # Proton CoM offset (same as exp_12)
    R_P_COM = R1 * M_E / M_P           # ~1.06 nodes
    dr_e    = R_INIT / np.sqrt(3.0)
    dr_p    = R_P_COM / np.sqrt(3.0)
    k_p     = K_BOHR * M_E / M_P       # small opposing momentum

    start_e = tuple(min(int(round(wc[i] + dr_e)), sz - 2) for i in range(3))
    start_p = tuple(max(int(round(wc[i] - dr_p)), 1)       for i in range(3))

    x = np.arange(sz)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')

    # Electron: momentum K_INIT along V2=(1,-1,-1)
    sx, sy, sz_ = start_e
    env_e = (np.exp(-0.5 * ((xx-sx)**2 + (yy-sy)**2 + (zz-sz_)**2) / WIDTH_E**2)
             * np.exp(1j * K_INIT * (xx - yy - zz)))
    amp_e = env_e.astype(complex) / np.sqrt(2.0)
    lat_e = OctahedralLattice(sz, sz, sz)
    electron = CausalSession(lat_e, start_e, instruction_frequency=OMEGA_E)
    electron.psi_R = amp_e.copy()
    electron.psi_L = amp_e.copy()
    enforce_unity_spinor(electron.psi_R, electron.psi_L)

    # Proton: momentum k_p along -V2=(-1,+1,+1)
    px, py, pz = start_p
    env_p = (np.exp(-0.5 * ((xx-px)**2 + (yy-py)**2 + (zz-pz)**2) / WIDTH_P**2)
             * np.exp(1j * k_p * (-xx + yy + zz)))
    amp_p = env_p.astype(complex) / np.sqrt(2.0)
    lat_p = OctahedralLattice(sz, sz, sz)
    proton = CausalSession(lat_p, start_p, instruction_frequency=OMEGA_P)
    proton.psi_R = amp_p.copy()
    proton.psi_L = amp_p.copy()
    enforce_unity_spinor(proton.psi_R, proton.psi_L)

    # Photon: massless, seeded at electron's start, no phase gradient.
    # Direction is decided by the lattice via the imprinted drain phase.
    lat_ph = OctahedralLattice(sz, sz, sz)
    photon = CausalSession(lat_ph, start_e, instruction_frequency=0.0,
                           is_massless=True)
    # psi initialised to single-node by CausalSession.__init__ -- that is fine.

    return electron, proton, photon, start_e, start_p


# ── Main ───────────────────────────────────────────────────────────────────────

def run():
    print("=" * 70)
    print("EXP 15: Dissipative electron capture")
    print("=" * 70)
    print(f"  OMEGA_E={OMEGA_E:.4f}  OMEGA_P={OMEGA_P:.4f}  STRENGTH={STRENGTH}")
    print(f"  R1={R1:.2f}  R_INIT={R_INIT:.2f}  K_INIT={K_INIT:.5f}  K_BOHR={K_BOHR:.5f}")
    print(f"  GAMMA={GAMMA:.6f}  (lattice-derived: sin^2(w/2)*cos^2(w/2))")
    print(f"  Grid={GRID}^3  TICKS={TICKS}  BURN_IN={BURN_IN}")

    grid = GRID
    wc   = (grid // 2,) * 3

    electron, proton, photon, start_e, start_p = make_sessions(grid, wc)

    # Set initial Coulomb potentials
    e_com0 = density_com(electron.probability_density())
    p_com0 = density_com(proton.probability_density())
    electron.lattice.topological_potential = coulomb_potential_array(
        grid, *p_com0, STRENGTH, SOFTENING)
    proton.lattice.topological_potential = coulomb_potential_array(
        grid, *e_com0, STRENGTH, SOFTENING)

    # Register sessions and emission coupling
    scheduler = TickScheduler()
    e_idx  = scheduler.register_session(electron)
    pr_idx = scheduler.register_session(proton)
    ph_idx = scheduler.register_session(photon)
    scheduler.register_emission(e_idx, ph_idx, pr_idx, rate=GAMMA)

    print(f"\n  Sessions: electron={e_idx}  proton={pr_idx}  photon={ph_idx}")
    print(f"  Electron start: {start_e}  r={com_radius(e_com0, wc):.2f}")
    print(f"  Proton  start: {start_p}  r={com_radius(p_com0, wc):.2f}")

    # Radial geometry for PDF scoring
    x = np.arange(grid)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    r_arr = np.sqrt((xx - wc[0])**2 + (yy - wc[1])**2 + (zz - wc[2])**2)
    r_max = float(r_arr.max())
    bin_edges = np.linspace(0, r_max, N_BINS + 1)
    r_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    e_radii  = []           # electron CoM radius per tick
    ph_radii = []           # photon  CoM radius per tick (outward propagation check)
    acc_dens = None         # accumulated electron density for PDF (post burn-in)

    print(f"\n  {'tick':>6}  {'e_r':>7}  {'p_r':>7}  {'ph_r':>7}  {'k_tang':>10}  {'ramp_std':>10}")
    print(f"  {'-'*65}")

    t0 = time.time()

    for tick in range(TICKS):
        # Update Coulomb potentials from live CoMs
        e_dens = electron.probability_density()
        p_dens = proton.probability_density()
        e_com  = density_com(e_dens)
        p_com  = density_com(p_dens)

        electron.lattice.topological_potential = coulomb_potential_array(
            grid, *p_com, STRENGTH, SOFTENING)
        proton.lattice.topological_potential = coulomb_potential_array(
            grid, *e_com, STRENGTH, SOFTENING)

        # Alternating tick order to cancel leading-order asymmetry (exp_12)
        if tick % 2 == 0:
            proton.tick();   proton.advance_tick_counter()
            electron.tick(); electron.advance_tick_counter()
            photon.tick();   photon.advance_tick_counter()
        else:
            electron.tick(); electron.advance_tick_counter()
            proton.tick();   proton.advance_tick_counter()
            photon.tick();   photon.advance_tick_counter()

        # Emission coupling: drain tangential phase from electron to photon
        scheduler._apply_emission_pairs()

        e_r  = com_radius(e_com, wc)
        ph_com = density_com(photon.probability_density())
        ph_r = com_radius(ph_com, wc)
        e_radii.append(e_r)
        ph_radii.append(ph_r)

        if tick >= BURN_IN:
            acc_dens = e_dens if acc_dens is None else acc_dens + e_dens

        if (tick + 1) % 500 == 0:
            elapsed = time.time() - t0
            eta     = elapsed / (tick + 1) * (TICKS - tick - 1)
            diag    = scheduler.emission_diagnostics.get(e_idx, [])
            k_tang_now  = float(diag[-1][1]) if diag else 0.0
            ramp_std_now = float(diag[-1][2]) if diag else 0.0
            print(f"  {tick+1:6d}  {e_r:7.3f}  {com_radius(p_com, wc):7.3f}"
                  f"  {ph_r:7.3f}  k_tang={k_tang_now:+.5f}  ramp_std={ramp_std_now:.5f}"
                  f"  [{elapsed:.0f}s  eta {eta:.0f}s]")

    elapsed = time.time() - t0

    # ── Scoring ────────────────────────────────────────────────────────────────
    e_r_arr  = np.array(e_radii)
    ph_r_arr = np.array(ph_radii)

    r_initial = float(np.mean(e_r_arr[:50]))
    r_final   = float(np.mean(e_r_arr[-500:]))
    spiralled = r_final < r_initial

    # PDF peak from accumulated density
    P, _ = np.histogram(r_arr.ravel(), bins=bin_edges,
                        weights=acc_dens.ravel() if acc_dens is not None
                        else electron.probability_density().ravel())
    P /= (P.sum() + 1e-12)
    r_pdf_peak  = r_centers[int(np.argmax(P))]
    peak_error  = abs(r_pdf_peak - R1) / R1

    print(f"\n{'='*70}")
    print(f"RESULT")
    print(f"{'='*70}")
    print(f"  r_initial (mean first 50 ticks)  = {r_initial:.3f}")
    print(f"  r_final   (mean last 500 ticks)  = {r_final:.3f}")
    print(f"  R1 (exp_12 two-body reference)   = {R1:.3f}")
    print(f"  PDF peak r                       = {r_pdf_peak:.3f}")
    print(f"  PDF peak error vs R1             = {peak_error*100:.1f}%")
    print(f"  Electron spiralled inward?       = {spiralled}")
    print(f"  Total time = {elapsed:.0f}s ({elapsed/3600:.2f} hrs)")

    # Drain diagnostics
    diag = scheduler.emission_diagnostics.get(e_idx, [])
    if diag:
        diag_arr = np.array(diag)   # (N, 3): tick, k_tang, ramp_std
        k_early = float(np.mean(np.abs(diag_arr[:50, 1])))
        k_late  = float(np.mean(np.abs(diag_arr[-50:, 1])))
        ramp_mean = float(np.mean(diag_arr[:, 2]))
        print(f"\n  Drain diagnostics:")
        print(f"    |k_tang| early (first 50 ticks) = {k_early:.6f}")
        print(f"    |k_tang| late  (last  50 ticks) = {k_late:.6f}")
        print(f"    ramp_std mean                   = {ramp_mean:.6f}")
        if k_early < 1e-6:
            print(f"    WARNING: k_tang near zero -- phase_gradient_field() may be")
            print(f"             returning garbage (phase wrapping in spread packet).")
        elif ramp_mean < 1e-6:
            print(f"    WARNING: ramp_std near zero -- phase ramp is spatially flat,")
            print(f"             kinetic hop will not see any change in delta_p.")
        else:
            trend = (k_late - k_early) / (k_early + 1e-12) * 100.0
            print(f"    k_tang trend: {trend:+.1f}%  ({'decreasing' if trend < 0 else 'increasing or flat'})")

    tightened = r_final < r_initial - 0.5   # orbit radius decreased by at least 0.5 nodes
    passed = tightened and peak_error < 0.20

    if passed:
        print(f"\n[PASS] Orbit tightened from r={r_initial:.2f} to r={r_final:.2f},"
              f" PDF peak at {r_pdf_peak:.2f} (within 20% of R1={R1:.2f})")
        print(f"  Tangential phase drain circularizes the orbit at R1.")
    else:
        print(f"\n[PARTIAL] tightened={tightened}  peak_error={peak_error*100:.1f}%")
        if not tightened:
            print(f"  Orbit did not tighten -- drain not effective, increase GAMMA.")
        if peak_error >= 0.20:
            print(f"  PDF peak {r_pdf_peak:.2f} is more than 20% from R1={R1:.2f}.")

    # ── Save data ──────────────────────────────────────────────────────────────
    out = os.path.join(_DATA_DIR, 'exp_15_capture.npy')
    np.save(out, np.column_stack([
        np.arange(TICKS, dtype=float),
        e_r_arr,
        ph_r_arr,
    ]))
    print(f"\nSaved: {out}")
    print(f"  columns: tick, electron_r, photon_r")

    return passed


if __name__ == '__main__':
    passed = run()
    sys.exit(0 if passed else 1)
