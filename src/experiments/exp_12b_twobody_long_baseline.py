"""
exp_12b_twobody_long_baseline.py
Long-duration two-body baseline -- no photon, no emission machinery.

Companion to exp_12 (which establishes the two-body hydrogen at the
4-sig-fig Bohr-radius level) and to exp_20 (which compares three
emission operators on top of the same two-body chassis).  exp_12b
isolates the question:

    Does the bare exp_12 two-body system stay bound at R_1 = 10.3
    over the same 6000-tick horizon used by exp_20?

If yes, the orbital instability seen in all three exp_20 arms
(r_peak escapes to 50+ by tick 2000) is caused by the emission
machinery.  If no, the instability is in the bare two-body dynamics
themselves and emission is not the headline question.

This experiment leaves exp_12_hydrogen_twobody.py unmodified and
gets its own audit-table row.

Design
------
Identical to exp_20 except:
  * No photon session is created.
  * No emission operator runs.
  * Only two diagnostics: r_peak and joint amplitude (e + p).
  * rho_phi proxy is the omega-weighted (e + p) integral; useful for
    detecting any unexpected energy drift independent of emission.

Same two-body init as exp_12:
  * Electron at wc + dr_e along V1, with momentum k_e ~ 1/R_1.
  * Proton at wc - dr_p along V1, with momentum k_p = k_e * m_e/m_p.
  * Mean-field Coulomb potential refreshed each tick from the live CoMs.
  * Alternating tick order to cancel leading-order asymmetry.
  * tick(normalize=True) on both sessions -- nothing should be drifting
    away from unit norm in the bare system.
"""

import sys, os, time
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import (OctahedralLattice, CausalSession, enforce_unity_spinor)

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         '..', '..', 'data')

# ── Fixed parameters (matched to exp_12 / exp_20) ─────────────────────────────
OMEGA_E   = 0.1019
OMEGA_P   = np.pi / 2.0
STRENGTH  = 30.0
SOFTENING = 0.5
WIDTH_E   = 1.5
WIDTH_P   = 0.5
R1        = 10.3
GRID      = 65

# ── Run parameters ────────────────────────────────────────────────────────────
TICKS_TOTAL    = int(os.environ.get('EXP12B_TICKS', '100'))
CHECK_EVERY    = 20
SETTLE_TOL     = 0.15           # r_peak within 15% of R1
SUCCESS_STREAK = 33

M_E = np.sin(OMEGA_E / 2.0)
M_P = np.sin(OMEGA_P / 2.0)


# ── Helpers (mirrors of exp_20 / exp_19c) ─────────────────────────────────────

def make_coords(grid):
    x = np.arange(grid, dtype=float)
    return np.meshgrid(x, x, x, indexing='ij')


def coulomb_potential_fast(xx, yy, zz, cx, cy, cz, strength, softening):
    r = np.sqrt((xx-cx)**2 + (yy-cy)**2 + (zz-cz)**2)
    return -strength / (r + softening)


def density_com(density, xx, yy, zz):
    total = float(density.sum())
    if total < 1e-12:
        return (0.0, 0.0, 0.0)
    cx = float(np.sum(xx * density) / total)
    cy = float(np.sum(yy * density) / total)
    cz = float(np.sum(zz * density) / total)
    return (cx, cy, cz)


def session_amplitude(session):
    return float(np.sum(
        np.abs(session.psi_R)**2 + np.abs(session.psi_L)**2
    ))


def make_sessions(grid, wc, xx, yy, zz):
    """exp_12 two-body initialization in CoM frame, k_init = 1/R1.
    No photon session is created here -- this is the bare baseline.
    """
    dr_e = R1 / np.sqrt(3.0)
    dr_p = R1 * M_E / (M_P * np.sqrt(3.0))
    k_e  = 1.0 / R1
    k_p  = k_e * M_E / M_P
    sz   = grid

    start_e = tuple(min(int(round(wc[i] + dr_e)), sz-2) for i in range(3))
    start_p = tuple(max(int(round(wc[i] - dr_p)), 1)    for i in range(3))

    sx, sy, sz_ = start_e
    env_e = (np.exp(-0.5*((xx-sx)**2+(yy-sy)**2+(zz-sz_)**2)/WIDTH_E**2)
             * np.exp(1j*k_e*(xx-yy-zz))).astype(complex)
    amp_e = env_e / np.sqrt(2.0)
    lat_e = OctahedralLattice(sz, sz, sz)
    electron = CausalSession(lat_e, start_e, instruction_frequency=OMEGA_E)
    electron.psi_R = amp_e.copy()
    electron.psi_L = amp_e.copy()
    enforce_unity_spinor(electron.psi_R, electron.psi_L)

    px, py, pz = start_p
    env_p = (np.exp(-0.5*((xx-px)**2+(yy-py)**2+(zz-pz)**2)/WIDTH_P**2)
             * np.exp(1j*k_p*(-xx+yy+zz))).astype(complex)
    amp_p = env_p / np.sqrt(2.0)
    lat_p = OctahedralLattice(sz, sz, sz)
    proton = CausalSession(lat_p, start_p, instruction_frequency=OMEGA_P)
    proton.psi_R = amp_p.copy()
    proton.psi_L = amp_p.copy()
    enforce_unity_spinor(proton.psi_R, proton.psi_L)

    return electron, proton


def r_peak_relative(density, p_com, xx, yy, zz, n_bins=80):
    """PDF peak of electron density relative to live proton CoM."""
    radii = np.sqrt((xx - p_com[0])**2 + (yy - p_com[1])**2 + (zz - p_com[2])**2)
    bins = np.linspace(0.0, float(radii.max()), n_bins + 1)
    P, _ = np.histogram(radii.ravel(), bins=bins, weights=density.ravel())
    if P.sum() < 1e-12:
        return 0.0
    r_centers = 0.5 * (bins[:-1] + bins[1:])
    return float(r_centers[int(np.argmax(P))])


# ── Single trial ──────────────────────────────────────────────────────────────

def run_trial(log_fn=None):
    """Run the bare two-body baseline.  No emission, no photon."""
    if log_fn is None:
        log_fn = lambda s: None  # noqa: E731

    wc = (GRID//2,) * 3
    xx, yy, zz = make_coords(GRID)
    electron, proton = make_sessions(GRID, wc, xx, yy, zz)
    omegas = (OMEGA_E, OMEGA_P)

    # Initial Coulomb potentials.
    e_com = density_com(electron.probability_density(), xx, yy, zz)
    p_com = density_com(proton.probability_density(), xx, yy, zz)
    electron.lattice.topological_potential = coulomb_potential_fast(
        xx, yy, zz, *p_com, STRENGTH, SOFTENING)
    proton.lattice.topological_potential = coulomb_potential_fast(
        xx, yy, zz, *e_com, STRENGTH, SOFTENING)

    A0_e = session_amplitude(electron)
    A0_p = session_amplitude(proton)
    A0_joint = A0_e + A0_p
    rho0 = OMEGA_E * A0_e + OMEGA_P * A0_p

    consec_ok      = 0
    max_streak     = 0
    settled        = False
    T_settle       = None
    A_drift_max    = 0.0
    rho_drift_max  = 0.0
    r_peak_max     = 0.0
    r_peak_min     = float('inf')

    win_dens  = None
    win_p_com = None

    t0 = time.time()
    r_peak = 0.0

    for tick in range(TICKS_TOTAL):

        # Update Coulomb potentials from live CoM.
        e_dens = electron.probability_density()
        p_dens = proton.probability_density()
        e_com  = density_com(e_dens, xx, yy, zz)
        p_com  = density_com(p_dens, xx, yy, zz)
        electron.lattice.topological_potential = coulomb_potential_fast(
            xx, yy, zz, *p_com, STRENGTH, SOFTENING)
        proton.lattice.topological_potential = coulomb_potential_fast(
            xx, yy, zz, *e_com, STRENGTH, SOFTENING)

        # Tick both sessions in alternating order, both with normalize=True
        # (no emission to muddy normalization in the baseline).
        if tick % 2 == 0:
            proton.tick();    proton.advance_tick_counter()
            electron.tick();  electron.advance_tick_counter()
        else:
            electron.tick();  electron.advance_tick_counter()
            proton.tick();    proton.advance_tick_counter()

        # Windowed electron density accumulation.
        tick_in_win = tick % CHECK_EVERY
        if win_dens is None:
            win_dens = e_dens.astype(float)
        else:
            win_dens += e_dens
        if tick_in_win == CHECK_EVERY // 2:
            win_p_com = density_com(p_dens, xx, yy, zz)

        # Stability + diagnostic check at end of each window.
        if tick_in_win == CHECK_EVERY - 1:
            if win_p_com is None:
                win_p_com = density_com(p_dens, xx, yy, zz)
            r_peak = r_peak_relative(win_dens, win_p_com, xx, yy, zz)
            r_peak_max = max(r_peak_max, r_peak)
            r_peak_min = min(r_peak_min, r_peak)

            if not settled:
                if abs(r_peak - R1) / R1 < SETTLE_TOL:
                    consec_ok += 1
                    max_streak = max(max_streak, consec_ok)
                    if consec_ok >= SUCCESS_STREAK:
                        settled  = True
                        T_settle = tick
                else:
                    consec_ok = 0

            amp_e_now = session_amplitude(electron)
            amp_p_now = session_amplitude(proton)
            A_now     = amp_e_now + amp_p_now
            rho_now   = OMEGA_E * amp_e_now + OMEGA_P * amp_p_now
            A_drift_max   = max(A_drift_max,   abs(A_now - A0_joint))
            rho_drift_max = max(rho_drift_max, abs(rho_now - rho0))

            log_period = max(1, (2000 // CHECK_EVERY))
            if (tick // CHECK_EVERY) % log_period == 0:
                elapsed = time.time() - t0
                ticks_done = tick + 1
                eta = elapsed / ticks_done * (TICKS_TOTAL - ticks_done) if ticks_done else 0
                msg = (f"tick={tick:6d}  r_peak={r_peak:6.3f}"
                       f"  streak={consec_ok:3d}"
                       f"  amp_e={amp_e_now:.4f}  amp_p={amp_p_now:.4f}"
                       f"  A_drift={abs(A_now - A0_joint):.2e}"
                       f"  rho_drift={abs(rho_now - rho0):.2e}"
                       f"  [{elapsed:.0f}s eta {eta:.0f}s]")
                log_fn(msg)

            win_dens  = None
            win_p_com = None

    return {
        'settled':       settled,
        'T_settle':      T_settle,
        'max_streak':    max_streak,
        'amp_e':         session_amplitude(electron),
        'amp_p':         session_amplitude(proton),
        'A_joint_initial':   A0_joint,
        'rho_phi_initial':   rho0,
        'A_joint_drift_max': A_drift_max,
        'rho_phi_drift_max': rho_drift_max,
        'r_peak_max':    r_peak_max,
        'r_peak_min':    r_peak_min,
    }


# ── Driver ────────────────────────────────────────────────────────────────────

def run_main():
    """Run a single baseline trial; write log and npy summary."""
    log_path = os.path.join(_DATA_DIR, 'exp_12b_baseline.log')
    npy_path = os.path.join(_DATA_DIR, 'exp_12b_baseline.npy')

    with open(log_path, 'w') as logf:
        def out(s):
            print(s, flush=True)
            logf.write(s + '\n')
            logf.flush()

        out(f"exp_12b  long-duration two-body baseline (no emission)")
        out(f"OMEGA_E={OMEGA_E}  OMEGA_P={OMEGA_P:.4f}  R1={R1}")
        out(f"STRENGTH={STRENGTH}  GRID={GRID}^3")
        out(f"TICKS_TOTAL={TICKS_TOTAL}  CHECK_EVERY={CHECK_EVERY}")
        out(f"SUCCESS_STREAK={SUCCESS_STREAK}  SETTLE_TOL={SETTLE_TOL}")
        out('-' * 60)

        result = run_trial(log_fn=out)

        status = 'SETTLED' if result['settled'] else 'NOT_SETTLED'
        out(f"result={status}")
        out(f"max_streak={result['max_streak']}")
        out(f"T_settle={result['T_settle']}")
        out(f"r_peak_min={result['r_peak_min']:.3f}")
        out(f"r_peak_max={result['r_peak_max']:.3f}")
        out(f"amp_e_final={result['amp_e']:.6f}")
        out(f"amp_p_final={result['amp_p']:.6f}")
        out(f"A_joint_initial={result['A_joint_initial']:.6f}")
        out(f"rho_phi_initial={result['rho_phi_initial']:.6f}")
        out(f"A_joint_drift_max={result['A_joint_drift_max']:.4e}")
        out(f"rho_phi_drift_max={result['rho_phi_drift_max']:.4e}")

    summary = np.array([
        float(result['settled']),
        float(result['max_streak']),
        float(result['T_settle']) if result['T_settle'] else float(TICKS_TOTAL),
        result['amp_e'],
        result['amp_p'],
        result['A_joint_drift_max'],
        result['rho_phi_drift_max'],
        result['r_peak_min'],
        result['r_peak_max'],
    ])
    np.save(npy_path, summary)
    print(f"Saved: {npy_path}", flush=True)


if __name__ == '__main__':
    run_main()
