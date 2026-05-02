"""
exp_20_emission_operator.py
Three-arm operator comparison for photon emission on the bipartite A=1 lattice.

Tests the operation-algebra prediction (notes/lattice_operation_algebra.md,
notes/exp_20_emission_operator_and_clock_fluid.md) that the as-written
amplitude drain in exp_19c is non-unitary, and that a pointwise beam
splitter with joint A=1 enforcement is the correct emission operator.

Three parallel arms, identical in every respect except the emission
operator and the per-session normalisation rule for the electron and
photon during emission. The proton always uses tick(normalize=True);
arm-specific behaviour applies only to the electron / photon pair.

  Arm A (control)    -- Row 5 drain. Reproduces exp_19c.
                        psi_e -= m*psi_e ;  psi_gamma += m*psi_e
                        Per-session enforce_unity_spinor on electron AND photon.
                        Joint amplitude:  (1 - 2m + 2m^2)|psi_e|^2  -- NOT preserved.

  Arm B (treatment)  -- Row 6 pointwise beam splitter.
                        sin(theta) = m,  cos(theta) = sqrt(1 - m^2)
                        psi_e *= cos(theta) ;  psi_gamma += sin(theta)*psi_e
                        NO per-session enforce_unity_spinor on electron or photon.
                        Joint amplitude:  cos^2 + sin^2 = 1  pointwise.  Preserved.

  Arm C (alternative)-- Row 7 phase-rotation drain. Reproduces exp_19 v5.
                        psi_e *= exp(-i*alpha) ;  psi_gamma *= exp(+i*alpha)
                        |rot| = 1, so per-session amplitudes preserved trivially.
                        Photon does not gain observable amplitude.

Predictions (from the operation algebra):

  * Arm A:  amp_g clamped to ~1 by photon enforce_unity_spinor; orbit does not
            settle (reproduces exp_19c NOT_SETTLED, max_streak <= 11).
  * Arm B:  amp_e drifts down, amp_g grows from ~0; A_joint = amp_e + amp_g
            stays at the initial value; orbit lock-in achievable.
  * Arm C:  amp_e and amp_g stay near initial values; photon does not grow;
            orbit response indistinguishable from no-emission baseline.

Diagnostic (rho_phi-proxy drift):

  rho_phi_proxy(t) = sum_i omega_i * |psi_i|_session^2 across all three sessions.
  The three arms produce three distinct signatures:
    * Arm A:  large drift O(omega_gamma) -- photon artificially inflated to
              unit norm by per-session enforce; non-physical.
    * Arm B:  drift = (transferred amplitude) * (omega_gamma - omega_e), the
              genuine emission energy transfer.  Joint A_joint preserved to
              numerical precision by enforce_joint_unity.
    * Arm C:  drift at numerical precision -- no amplitude is transferred,
              only phase coherence.
"""

import sys, os, time
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import (OctahedralLattice, CausalSession, enforce_unity_spinor)

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         '..', '..', 'data')

# ── Fixed parameters (from exp_12, exp_16, exp_19c) ──────────────────────────
OMEGA_E   = 0.1019
OMEGA_P   = np.pi / 2.0
OMEGA_G_FRAC = 0.75      # photon omega = OMEGA_E * OMEGA_G_FRAC (n=2->n=1 proxy)
STRENGTH  = 30.0
SOFTENING = 0.5
WIDTH_E   = 1.5
WIDTH_P   = 0.5
R1        = 10.3
GRID      = 65

# ── Run parameters ───────────────────────────────────────────────────────────
# TICKS_TOTAL default is a smoke-test value; for a settled run override via
# the EXP20_TICKS env var (multi-thousand to clear SUCCESS_STREAK = 33 and
# resolve Arnold-tongue lock-in).
TICKS_TOTAL    = int(os.environ.get('EXP20_TICKS', '100'))
CHECK_EVERY    = 20      # ticks between stability checks
SETTLE_TOL     = 0.15    # r_peak within 15% of R1 (loose; tongue-width tighter)
SUCCESS_STREAK = 33      # 3x best two-session baseline

# Default arms and rates for the parallel launcher.  Override via env vars
# EXP20_ARMS ("A,B,C") and EXP20_RATE (single float) if you want a custom run.
DEFAULT_ARMS  = ['A', 'B', 'C']
DEFAULT_RATE  = float(os.environ.get('EXP20_RATE', '0.05'))

M_E = np.sin(OMEGA_E / 2.0)
M_P = np.sin(OMEGA_P / 2.0)
OMEGA_G = OMEGA_E * OMEGA_G_FRAC


# ── Helpers (mirrors of exp_19c utilities) ───────────────────────────────────

def make_coords(grid):
    """Precompute integer coordinate grids once."""
    x = np.arange(grid, dtype=float)
    return np.meshgrid(x, x, x, indexing='ij')


def coulomb_potential_fast(xx, yy, zz, cx, cy, cz, strength, softening):
    """Coulomb potential using precomputed coordinate grids."""
    r = np.sqrt((xx-cx)**2 + (yy-cy)**2 + (zz-cz)**2)
    return -strength / (r + softening)


def density_com(density, xx, yy, zz):
    """Centre of mass using precomputed coordinate grids."""
    total = float(density.sum())
    if total < 1e-12:
        return (0.0, 0.0, 0.0)
    cx = float(np.sum(xx * density) / total)
    cy = float(np.sum(yy * density) / total)
    cz = float(np.sum(zz * density) / total)
    return (cx, cy, cz)


def session_amplitude(session):
    """Total probability in one session (A_session)."""
    return float(np.sum(
        np.abs(session.psi_R)**2 + np.abs(session.psi_L)**2
    ))


def joint_amplitude(*sessions):
    """Joint amplitude across sessions (A_joint integrated)."""
    return sum(session_amplitude(s) for s in sessions)


def rho_phi_proxy(sessions, omegas):
    """omega-weighted A_joint integral; proxy for spatial integral of rho_phi.
    Per notes/exp_20_emission_operator_and_clock_fluid.md the
    rho_phi continuity statement is local; the integrated form
    (this proxy) is preserved iff total amplitude is omega-weighted-preserved.
    """
    return sum(omega * session_amplitude(s)
               for s, omega in zip(sessions, omegas))


def enforce_joint_unity(s1, s2, target):
    """Rescale s1.psi_R/L and s2.psi_R/L by a common factor so that
       ||s1||^2 + ||s2||^2 = target.

    Used by arm B to enforce JOINT A=1 across the (electron, photon) pair.
    Because the rescaling is global (same factor on both sessions), the
    beam splitter's redistribution ratio amp_g/amp_e is preserved -- only
    the bipartite tick rule's residual drift is absorbed.
    """
    current = session_amplitude(s1) + session_amplitude(s2)
    if current > 1e-12:
        scale = np.sqrt(target / current)
        s1.psi_R *= scale
        s1.psi_L *= scale
        s2.psi_R *= scale
        s2.psi_L *= scale


def make_sessions(grid, wc, xx, yy, zz):
    """exp_12 two-body initialization in CoM frame, k_init = 1/R1.
    Photon session created with near-zero amplitude (1e-6 seed)."""
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

    lat_g = OctahedralLattice(sz, sz, sz)
    photon = CausalSession(lat_g, wc,
                            instruction_frequency=OMEGA_G,
                            is_massless=True)
    photon.psi_R *= 1e-6
    photon.psi_L *= 1e-6

    return electron, proton, photon


def r_peak_relative(density, p_com, xx, yy, zz, n_bins=80):
    """PDF peak of electron density relative to live proton CoM."""
    radii = np.sqrt((xx - p_com[0])**2 + (yy - p_com[1])**2 + (zz - p_com[2])**2)
    bins = np.linspace(0.0, float(radii.max()), n_bins + 1)
    P, _ = np.histogram(radii.ravel(), bins=bins, weights=density.ravel())
    if P.sum() < 1e-12:
        return 0.0
    r_centers = 0.5 * (bins[:-1] + bins[1:])
    return float(r_centers[int(np.argmax(P))])


# ── The three emission operators ─────────────────────────────────────────────

def emit_arm_a(electron, photon, emit_mask, joint_target):
    """Row 5: linear amplitude drain (exp_19c reproduction).
    joint_target is accepted for signature uniformity and ignored.

    Joint amplitude AFTER one tick with photon initially zero:
        ||psi_e'||^2 + ||psi_gamma'||^2 = (1 - 2m + 2m^2) ||psi_e||^2
    Equals ||psi_e||^2 only at m in {0, 1}; non-unitary at every other rate.
    Per-session enforce_unity_spinor on electron AND photon then resets each
    to unit norm independently, masking the violation.
    """
    drain_R = electron.psi_R * emit_mask
    drain_L = electron.psi_L * emit_mask
    electron.psi_R -= drain_R
    electron.psi_L -= drain_L
    photon.psi_R   += drain_R
    photon.psi_L   += drain_L
    enforce_unity_spinor(electron.psi_R, electron.psi_L)
    enforce_unity_spinor(photon.psi_R, photon.psi_L)


def emit_arm_b(electron, photon, emit_mask, joint_target):
    """Row 6: pointwise beam splitter + JOINT A=1 enforcement.

    For sin(theta(x)) = emit_mask(x):
        psi_e'(x)     = cos(theta(x)) psi_e(x)
        psi_gamma'(x) = psi_gamma(x) + sin(theta(x)) psi_e(x)
    The beam splitter operation itself is pointwise unitary, so under
    exact dynamics ||psi_e||^2 + ||psi_gamma||^2 is preserved.

    The bipartite tick rule with normalize=False has small residual
    drift (the kinetic + residence step is only approximately norm-
    preserving in the discrete setting).  enforce_joint_unity rescales
    both psi_e and psi_gamma by a COMMON factor to bring the joint
    amplitude back to its initial value; because the rescaling is
    common, the beam splitter's amp_g/amp_e ratio is preserved.

    This is what notes/exp_20_emission_operator_and_clock_fluid.md
    means by "joint A=1 enforcement" -- not "no normalization at all"
    but "normalize the (e, gamma) pair as a unit, never each alone."
    """
    sin_t = emit_mask
    sin_t = np.minimum(sin_t, 1.0)
    cos_t = np.sqrt(np.maximum(0.0, 1.0 - sin_t * sin_t))
    transfer_R = sin_t * electron.psi_R
    transfer_L = sin_t * electron.psi_L
    electron.psi_R = cos_t * electron.psi_R
    electron.psi_L = cos_t * electron.psi_L
    photon.psi_R   += transfer_R
    photon.psi_L   += transfer_L
    enforce_joint_unity(electron, photon, joint_target)


def emit_arm_c(electron, photon, emit_mask, joint_target):
    """Row 7: phase-rotation drain (exp_19 v5 reproduction).
    joint_target is accepted for signature uniformity and ignored.

    Each session is multiplied by a unit-modulus pointwise phase rotation:
        psi_e     *= exp(-i*alpha(x))
        psi_gamma *= exp(+i*alpha(x))
    Per-session amplitudes are preserved by the rotation itself
    (|exp(i*phi)| = 1).  The bipartite tick rule with normalize=False
    has small residual drift, however, so the electron is
    enforce_unity_spinor-renormalised after the rotation to absorb that
    drift.  The photon is intentionally NOT renormalised -- it should
    stay at its near-zero seed amplitude under arm C, and a unity
    enforcer would artificially inflate it (the same mode of failure
    that makes arm A non-physical).
    """
    alpha = emit_mask
    rot_e = np.exp(-1j * alpha)
    rot_g = np.exp(+1j * alpha)
    electron.psi_R = electron.psi_R * rot_e
    electron.psi_L = electron.psi_L * rot_e
    photon.psi_R   = photon.psi_R   * rot_g
    photon.psi_L   = photon.psi_L   * rot_g
    enforce_unity_spinor(electron.psi_R, electron.psi_L)
    # Photon is intentionally NOT renormalised under arm C.


ARM_OPERATORS = {
    'A': emit_arm_a,
    'B': emit_arm_b,
    'C': emit_arm_c,
}

ARM_DESCRIPTIONS = {
    'A': 'control: row-5 drain + per-session enforce (exp_19c)',
    'B': 'treatment: row-6 beam splitter, no per-session enforce on e/gamma',
    'C': 'alternative: row-7 phase-rotation drain (exp_19 v5)',
}


# ── Single trial ─────────────────────────────────────────────────────────────

def run_trial(emission_rate, arm, log_fn=None):
    """Run one (rate, arm) trial.  Returns dict with stabilization result and
    A_joint / rho_phi diagnostics."""
    if arm not in ARM_OPERATORS:
        raise ValueError(f"unknown arm: {arm!r} (expected one of {list(ARM_OPERATORS)})")
    if log_fn is None:
        log_fn = lambda s: None  # noqa: E731

    operator = ARM_OPERATORS[arm]
    wc = (GRID//2,) * 3
    xx, yy, zz = make_coords(GRID)

    electron, proton, photon = make_sessions(GRID, wc, xx, yy, zz)
    omegas = (OMEGA_E, OMEGA_P, OMEGA_G)

    # Initial Coulomb potentials.
    e_com = density_com(electron.probability_density(), xx, yy, zz)
    p_com = density_com(proton.probability_density(), xx, yy, zz)
    electron.lattice.topological_potential = coulomb_potential_fast(
        xx, yy, zz, *p_com, STRENGTH, SOFTENING)
    proton.lattice.topological_potential = coulomb_potential_fast(
        xx, yy, zz, *e_com, STRENGTH, SOFTENING)

    # Baseline diagnostics.
    A0_e = session_amplitude(electron)
    A0_p = session_amplitude(proton)
    A0_g = session_amplitude(photon)
    A0_joint = A0_e + A0_p + A0_g
    rho0 = rho_phi_proxy([electron, proton, photon], omegas)
    # Joint target for arm B: preserve the (electron, photon) pair sum
    # at its initial value (electron at unit norm + photon at near-zero
    # seed = ~1.0).  Arm A and arm C ignore this value.
    joint_eg_target = A0_e + A0_g

    consec_ok      = 0
    max_streak     = 0
    settled        = False
    T_settle       = None
    A_joint_drift_max = 0.0
    rho_phi_drift_max = 0.0

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

        # Tick all sessions in alternating order (electron / proton).
        # Proton uses normalize=True (no amplitude leaves it).
        # Electron and photon use normalize=False; the arm operator
        # decides whether/when to renormalize.
        if tick % 2 == 0:
            proton.tick();    proton.advance_tick_counter()
            electron.tick(normalize=False);  electron.advance_tick_counter()
        else:
            electron.tick(normalize=False);  electron.advance_tick_counter()
            proton.tick();    proton.advance_tick_counter()
        photon.tick(normalize=False); photon.advance_tick_counter()

        # Coulomb-driven emission mask:
        #   emit_mask(x) = emission_rate * max(0, V(x) - V_ground) / |V_ground|
        # Same form as exp_19c so the three arms differ only in how the
        # mask is applied, not in where emission is driven.
        V_field  = electron.lattice.topological_potential
        V_ground = -STRENGTH / (R1 + SOFTENING)
        excess   = V_field - V_ground
        scale    = abs(V_ground)
        emit_mask = emission_rate * np.maximum(0.0, excess) / scale

        # Apply the arm-specific emission operator.
        operator(electron, photon, emit_mask, joint_eg_target)

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

            if not settled:
                if abs(r_peak - R1) / R1 < SETTLE_TOL:
                    consec_ok += 1
                    max_streak = max(max_streak, consec_ok)
                    if consec_ok >= SUCCESS_STREAK:
                        settled  = True
                        T_settle = tick
                else:
                    consec_ok = 0

            # Conservation diagnostics.
            A_joint_now = joint_amplitude(electron, proton, photon)
            rho_now     = rho_phi_proxy([electron, proton, photon], omegas)
            A_drift     = abs(A_joint_now - A0_joint)
            rho_drift   = abs(rho_now - rho0)
            A_joint_drift_max = max(A_joint_drift_max, A_drift)
            rho_phi_drift_max = max(rho_phi_drift_max, rho_drift)

            # Progress log every ~2000 ticks (or every window in smoke test).
            log_period = max(1, (2000 // CHECK_EVERY))
            if (tick // CHECK_EVERY) % log_period == 0:
                elapsed = time.time() - t0
                ticks_done = tick + 1
                eta = elapsed / ticks_done * (TICKS_TOTAL - ticks_done) if ticks_done else 0
                amp_e = session_amplitude(electron)
                amp_p = session_amplitude(proton)
                amp_g = session_amplitude(photon)
                msg = (f"arm={arm} tick={tick:6d}  r_peak={r_peak:6.3f}"
                       f"  streak={consec_ok:3d}"
                       f"  amp_e={amp_e:.4f}  amp_p={amp_p:.4f}  amp_g={amp_g:.6f}"
                       f"  A_drift={A_drift:.2e}  rho_drift={rho_drift:.2e}"
                       f"  [{elapsed:.0f}s eta {eta:.0f}s]")
                log_fn(msg)

            win_dens  = None
            win_p_com = None

    # Final session amplitudes.
    final = {
        'arm':           arm,
        'emission_rate': emission_rate,
        'settled':       settled,
        'T_settle':      T_settle,
        'max_streak':    max_streak,
        'amp_e':         session_amplitude(electron),
        'amp_p':         session_amplitude(proton),
        'amp_g':         session_amplitude(photon),
        'A_joint_drift_max': A_joint_drift_max,
        'rho_phi_drift_max': rho_phi_drift_max,
        'A_joint_initial':   A0_joint,
        'rho_phi_initial':   rho0,
    }
    return final


# ── Single-arm worker (called as subprocess) ─────────────────────────────────

def run_single(arm, rate):
    """Run one (arm, rate) trial; write log and npy."""
    label = f"{arm}_r{rate:.4f}".replace('.', '_')
    log_path = os.path.join(_DATA_DIR, f'exp_20_arm_{label}.log')
    npy_path = os.path.join(_DATA_DIR, f'exp_20_arm_{label}.npy')

    with open(log_path, 'w') as logf:
        def out(s):
            print(s, flush=True)
            logf.write(s + '\n')
            logf.flush()

        out(f"exp_20  arm={arm}  emission_rate={rate}")
        out(f"  description: {ARM_DESCRIPTIONS[arm]}")
        out(f"OMEGA_E={OMEGA_E}  OMEGA_P={OMEGA_P:.4f}  OMEGA_G={OMEGA_G:.4f}  R1={R1}")
        out(f"STRENGTH={STRENGTH}  GRID={GRID}^3")
        out(f"TICKS_TOTAL={TICKS_TOTAL}  CHECK_EVERY={CHECK_EVERY}")
        out(f"SUCCESS_STREAK={SUCCESS_STREAK}  SETTLE_TOL={SETTLE_TOL}")
        out('-' * 60)

        result = run_trial(rate, arm, log_fn=out)

        status = 'SETTLED' if result['settled'] else 'NOT_SETTLED'
        out(f"result={status}")
        out(f"max_streak={result['max_streak']}")
        out(f"T_settle={result['T_settle']}")
        out(f"amp_e={result['amp_e']:.6f}")
        out(f"amp_p={result['amp_p']:.6f}")
        out(f"amp_g={result['amp_g']:.6f}")
        out(f"A_joint_initial={result['A_joint_initial']:.6f}")
        out(f"rho_phi_initial={result['rho_phi_initial']:.6f}")
        out(f"A_joint_drift_max={result['A_joint_drift_max']:.4e}")
        out(f"rho_phi_drift_max={result['rho_phi_drift_max']:.4e}")

    summary = np.array([
        ord(arm),
        result['emission_rate'],
        float(result['settled']),
        float(result['max_streak']),
        float(result['T_settle']) if result['T_settle'] else float(TICKS_TOTAL),
        result['amp_e'],
        result['amp_p'],
        result['amp_g'],
        result['A_joint_drift_max'],
        result['rho_phi_drift_max'],
    ])
    np.save(npy_path, summary)
    print(f"Saved: {npy_path}", flush=True)


# ── Parallel launcher ────────────────────────────────────────────────────────

def run_parallel():
    """Launch each arm at the canonical rate as a parallel subprocess.
    Override default arms / rate via EXP20_ARMS and EXP20_RATE env vars."""
    import subprocess, re

    arms = os.environ.get('EXP20_ARMS', ','.join(DEFAULT_ARMS)).split(',')
    arms = [a.strip().upper() for a in arms if a.strip()]
    for a in arms:
        if a not in ARM_OPERATORS:
            raise ValueError(f"EXP20_ARMS contains unknown arm: {a!r}")
    rate = DEFAULT_RATE

    print("=" * 70)
    print("EXP 20: Three-arm emission operator comparison")
    print("=" * 70)
    print(f"""
  Tests the operation-algebra prediction that the as-written exp_19c
  drain is non-unitary, and that a pointwise beam splitter with joint
  A=1 enforcement is the correct emission operator.

  Arms:""")
    for a in arms:
        print(f"    {a}: {ARM_DESCRIPTIONS[a]}")
    print(f"""
  Parameters:
    OMEGA_E={OMEGA_E}  OMEGA_P={OMEGA_P:.4f}  OMEGA_G={OMEGA_G:.4f}  R1={R1}
    STRENGTH={STRENGTH}  GRID={GRID}^3
    TICKS_TOTAL={TICKS_TOTAL}
    emission_rate={rate}
""")

    print(f"Launching {len(arms)} parallel workers (one per arm)...")
    procs = []
    err_files = []
    for arm in arms:
        label = f"{arm}_r{rate:.4f}".replace('.', '_')
        err_path = os.path.join(_DATA_DIR, f'exp_20_arm_{label}.err')
        err_f = open(err_path, 'w')
        err_files.append(err_f)
        cmd = [sys.executable, '-u', __file__, arm, str(rate)]
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=err_f)
        print(f"  arm={arm}  rate={rate}  PID={p.pid}  err={err_path}")
        procs.append((arm, p))

    print()
    t0 = time.time()
    while any(p.poll() is None for _, p in procs):
        done    = [a for a, p in procs if p.poll() is not None]
        running = [a for a, p in procs if p.poll() is None]
        print(f"[{time.time()-t0:.0f}s] running={running}  done={done}",
              flush=True)
        time.sleep(30)
    for f in err_files:
        f.close()

    print(f"\nAll done. Total time: {time.time()-t0:.0f}s")

    print(f"\n{'='*70}")
    print("RESULTS SUMMARY")
    print(f"{'='*70}")
    print(f"  {'arm':>4}  {'result':>12}  {'streak':>7}"
          f"  {'amp_e':>8}  {'amp_g':>10}"
          f"  {'A_drift':>9}  {'rho_drift':>9}")
    print(f"  {'-'*70}")

    n_settled = 0
    for arm, _ in procs:
        label = f"{arm}_r{rate:.4f}".replace('.', '_')
        log_path = os.path.join(_DATA_DIR, f'exp_20_arm_{label}.log')
        try:
            txt = open(log_path).read()
            def grab(pat, default='?'):
                m = re.search(pat, txt)
                return m.group(1) if m else default
            res     = grab(r'result=(\S+)')
            streak  = grab(r'max_streak=(\d+)')
            amp_e   = grab(r'amp_e=([\d.]+)')
            amp_g   = grab(r'amp_g=([\d.eE+-]+)')
            A_drift = grab(r'A_joint_drift_max=([\d.eE+-]+)')
            rho_drift = grab(r'rho_phi_drift_max=([\d.eE+-]+)')
            if res == 'SETTLED':
                n_settled += 1
            print(f"  {arm:>4}  {res:>12}  {streak:>7}  {amp_e:>8}  {amp_g:>10}"
                  f"  {A_drift:>9}  {rho_drift:>9}")
        except Exception as e:
            print(f"  {arm:>4}  ERROR reading log: {e}")

    print()
    print("Interpretation guide (per notes/exp_20_emission_operator_and_clock_fluid.md):")
    print("  Arm A predicted: amp_g clamped to ~1, NOT_SETTLED, A_drift > 0 from drain non-unitarity")
    print("  Arm B predicted: amp_g grows from ~0, possible SETTLED, A_drift ~ 0 (joint A=1 preserved)")
    print("  Arm C predicted: amp_g stays ~0, NOT_SETTLED, A_drift ~ 0 (phase rotation only)")


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) == 3:
        # Worker mode: arm rate
        arm = sys.argv[1].upper()
        rate = float(sys.argv[2])
        run_single(arm, rate)
    elif len(sys.argv) == 2:
        # Single-arm mode at default rate.
        arm = sys.argv[1].upper()
        run_single(arm, DEFAULT_RATE)
    else:
        run_parallel()
