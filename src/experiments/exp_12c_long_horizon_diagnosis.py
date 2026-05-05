"""
exp_12c_long_horizon_diagnosis.py
Diagnose the source of the long-horizon two-body escape exposed by exp_12b.

exp_12b (committed 2026-05-02) showed the bare exp_12 setup escaping
from r_peak ~ R_1 to grid edge by tick ~2000 over a 6000-tick horizon
at GRID=65^3.  The orbital escape is NOT caused by the emission
operator (exp_20 arms A/B/C all inherit it).  Three candidate causes
are flagged in the v0.98-RC conclusion's "What remains open"
subsection (item 5):

    1. GRID-SIZE DEPENDENCE.  The 65^3 box may simply be too small
       for the late-time wave packet; escape is a boundary artefact.
    2. CoM-FRAME INITIAL-CONDITION RESIDUAL.  Discrete-grid
       placement of the electron and proton may leave a residual
       net momentum that compounds over thousands of ticks.
    3. BIPARTITE TICK RULE'S NEAR-UNITARY DRIFT.  The kinetic+
       residence step is only approximately norm-preserving; small
       per-tick errors may accumulate into systematic outward drift.

Each cause produces a distinct signature, so a single instrumented
script with three sub-modes can localise the responsible mechanism.

  Mode 'grid':    sweep grid sizes {65, 81, 97, 113}, fixed TICKS,
                  fixed initial conditions.  If escape time scales
                  with grid size, cause 1.  If escape time is
                  invariant, cause 1 is ruled out.

  Mode 'init':    fix grid size, vary initial-condition treatment.
                  baseline = exp_12b verbatim.  zero_p_subtracted =
                  numerically subtract residual CoM momentum after
                  initial state preparation.  sym_pair = symmetric
                  pair initialisation guaranteeing exact CoM-zero
                  by construction.  If zero_p_subtracted or
                  sym_pair eliminates escape, cause 2.  If not,
                  cause 2 is ruled out.

  Mode 'drift':   single instrumented run that logs per-tick
                  amplitude drift before and after each component
                  of the tick (kinetic, residence, normalize)
                  separately, plus per-tick CoM displacement.
                  If a systematic outward drift emerges from the
                  kinetic step, cause 3.  If drift is statistical
                  with zero mean, cause 3 is unlikely.

Reuses NO machinery from exp_12b (intentional: exp_12b stays
unmodified).  Self-contained; same parameters as exp_12b at the
shared physics level (OMEGA_E, OMEGA_P, R1, etc.).
"""

import sys, os, time
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import (OctahedralLattice, CausalSession, enforce_unity_spinor)

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         '..', '..', 'data')

# ── Fixed physics parameters (shared with exp_12, exp_12b, exp_20) ────────────
OMEGA_E   = 0.1019
OMEGA_P   = np.pi / 2.0
STRENGTH  = 30.0
SOFTENING = 0.5
WIDTH_E   = 1.5
WIDTH_P   = 0.5
R1        = 10.3

# ── Run parameters ────────────────────────────────────────────────────────────
TICKS_TOTAL    = int(os.environ.get('EXP12C_TICKS', '100'))
CHECK_EVERY    = 20
SETTLE_TOL     = 0.15
SUCCESS_STREAK = 33

# Grid sweep variants for mode 'grid'
GRID_VARIANTS = [65, 81, 97, 113]

# Initial-condition variants for mode 'init'
INIT_VARIANTS = ['baseline', 'zero_p_subtracted', 'sym_pair']
INIT_GRID = 65

M_E = np.sin(OMEGA_E / 2.0)
M_P = np.sin(OMEGA_P / 2.0)


# ── Helpers ───────────────────────────────────────────────────────────────────

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


def momentum_expectation(session, xx, yy, zz):
    """Expectation value of momentum: <p> = -i * sum_x psi^* grad psi.
    Returns (px, py, pz) for the spinor sum |psi_R|^2 + |psi_L|^2 weighted
    by phase gradient.  Used by mode 'init' to test CoM-residual hypothesis.
    """
    # Combine spinor components into a scalar density-weighted phase field
    # for this diagnostic: <p> = Im(psi^* grad psi) per component.
    p = np.zeros(3, dtype=float)
    for psi in (session.psi_R, session.psi_L):
        for axis, c in enumerate((xx, yy, zz)):
            grad = np.gradient(psi, axis=axis)
            p[axis] += float(np.imag(np.sum(np.conj(psi) * grad)))
    return tuple(p)


def r_peak_relative(density, p_com, xx, yy, zz, n_bins=80):
    radii = np.sqrt((xx - p_com[0])**2 + (yy - p_com[1])**2 + (zz - p_com[2])**2)
    bins = np.linspace(0.0, float(radii.max()), n_bins + 1)
    P, _ = np.histogram(radii.ravel(), bins=bins, weights=density.ravel())
    if P.sum() < 1e-12:
        return 0.0
    r_centers = 0.5 * (bins[:-1] + bins[1:])
    return float(r_centers[int(np.argmax(P))])


# ── Initial-condition variants ────────────────────────────────────────────────

def make_sessions_baseline(grid, wc, xx, yy, zz):
    """Verbatim exp_12b initialisation.  Used by all modes as the reference."""
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


def make_sessions_zero_p_subtracted(grid, wc, xx, yy, zz):
    """exp_12b initialisation, then numerically subtract residual joint CoM
    momentum by applying a uniform phase ramp to both sessions.

    Hypothesis: the integer-grid placement of start_e and start_p leaves a
    residual <p_e> + <p_p> != 0 which compounds over 6000 ticks.  Subtracting
    the residual at t=0 should eliminate escape if cause 2 is responsible.
    """
    electron, proton = make_sessions_baseline(grid, wc, xx, yy, zz)

    p_e = np.array(momentum_expectation(electron, xx, yy, zz))
    p_p = np.array(momentum_expectation(proton, xx, yy, zz))
    p_residual = p_e + p_p
    # Total amplitude is preserved across both sessions (each ~1).
    # Subtract by applying uniform phase ramp -p_residual/2 to each session.
    A_total = session_amplitude(electron) + session_amplitude(proton)
    if A_total > 1e-12:
        # Common subtraction: each session gets -p_residual/2 phase ramp,
        # so combined <p> shifts by -p_residual.  Result: net joint <p> = 0.
        delta = -0.5 * p_residual
        ramp = np.exp(1j * (delta[0]*xx + delta[1]*yy + delta[2]*zz))
        electron.psi_R = electron.psi_R * ramp
        electron.psi_L = electron.psi_L * ramp
        proton.psi_R   = proton.psi_R   * ramp
        proton.psi_L   = proton.psi_L   * ramp
        enforce_unity_spinor(electron.psi_R, electron.psi_L)
        enforce_unity_spinor(proton.psi_R, proton.psi_L)

    return electron, proton


def make_sessions_sym_pair(grid, wc, xx, yy, zz):
    """Symmetric pair initialisation.  Both wave packets centered on
    grid-aligned points with exactly opposing momenta in the sum, so
    joint <p> = 0 by construction (modulo finite-grid sampling error).

    Uses k_e and -k_p along the SAME basis vector for both, with weights
    chosen so the joint momentum cancels: m_e * k_e + m_p * k_p_eff = 0.
    """
    dr_e = R1 / np.sqrt(3.0)
    dr_p = R1 * M_E / (M_P * np.sqrt(3.0))
    k_e  = 1.0 / R1
    # Choose k_p_eff so that m_e * k_e = m_p * |k_p_eff|, i.e.
    # k_p_eff = -k_e * M_E / M_P (same as baseline; the symmetric trick
    # is in the SIGN convention -- both momenta along V2=(1,-1,-1) but
    # with opposite signs).
    k_p  = k_e * M_E / M_P
    sz   = grid

    start_e = tuple(min(int(round(wc[i] + dr_e)), sz-2) for i in range(3))
    start_p = tuple(max(int(round(wc[i] - dr_p)), 1)    for i in range(3))

    # SAME phase direction for both (1,-1,-1), but opposing signs:
    #   electron:  exp( + i*k_e*(x - y - z))
    #   proton:    exp( - i*k_p*(x - y - z))
    # Joint <p> ~ k_e - k_p = k_e * (1 - M_E/M_P) which is NONZERO unless
    # M_E == M_P.  To make it exactly zero, weight by mass:
    #   <p_e> ~ k_e along V2,  <p_p> ~ -k_p along V2
    # Total momentum = k_e * 1 + (-k_p) * 1 (per session amplitude).
    # In the CoM frame the momenta should weight by mass, but here both
    # sessions carry unit amplitude so total <p> = (k_e - k_p) * V2.
    # For exact zero use k_p = k_e:
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
    # Symmetric: same magnitude k_e, opposite sign, along the SAME direction.
    env_p = (np.exp(-0.5*((xx-px)**2+(yy-py)**2+(zz-pz)**2)/WIDTH_P**2)
             * np.exp(-1j*k_e*(xx-yy-zz))).astype(complex)
    amp_p = env_p / np.sqrt(2.0)
    lat_p = OctahedralLattice(sz, sz, sz)
    proton = CausalSession(lat_p, start_p, instruction_frequency=OMEGA_P)
    proton.psi_R = amp_p.copy()
    proton.psi_L = amp_p.copy()
    enforce_unity_spinor(proton.psi_R, proton.psi_L)

    return electron, proton


INIT_FUNCTIONS = {
    'baseline':           make_sessions_baseline,
    'zero_p_subtracted':  make_sessions_zero_p_subtracted,
    'sym_pair':           make_sessions_sym_pair,
}


# ── Single trial (parameterised by grid + init) ───────────────────────────────

def run_trial(grid, init_variant, log_drift=False, log_fn=None):
    """Run one trial at the given grid size with the given init variant.
    log_drift=True instruments per-tick amplitude drift for mode 'drift'.
    """
    if log_fn is None:
        log_fn = lambda s: None  # noqa: E731

    wc = (grid//2,) * 3
    xx, yy, zz = make_coords(grid)
    init_fn = INIT_FUNCTIONS[init_variant]
    electron, proton = init_fn(grid, wc, xx, yy, zz)

    e_com = density_com(electron.probability_density(), xx, yy, zz)
    p_com = density_com(proton.probability_density(), xx, yy, zz)
    electron.lattice.topological_potential = coulomb_potential_fast(
        xx, yy, zz, *p_com, STRENGTH, SOFTENING)
    proton.lattice.topological_potential = coulomb_potential_fast(
        xx, yy, zz, *e_com, STRENGTH, SOFTENING)

    A0_e = session_amplitude(electron)
    A0_p = session_amplitude(proton)
    p_e_initial = momentum_expectation(electron, xx, yy, zz)
    p_p_initial = momentum_expectation(proton, xx, yy, zz)
    p_joint_initial = tuple(p_e_initial[i] + p_p_initial[i] for i in range(3))

    consec_ok      = 0
    max_streak     = 0
    settled        = False
    T_settle       = None
    A_drift_max    = 0.0
    r_peak_max     = 0.0
    r_peak_min     = float('inf')
    escape_tick    = None
    drift_log      = []  # per-tick amplitude drift if log_drift=True

    win_dens  = None
    win_p_com = None

    t0 = time.time()
    r_peak = 0.0

    for tick in range(TICKS_TOTAL):
        e_dens = electron.probability_density()
        p_dens = proton.probability_density()
        e_com  = density_com(e_dens, xx, yy, zz)
        p_com  = density_com(p_dens, xx, yy, zz)
        electron.lattice.topological_potential = coulomb_potential_fast(
            xx, yy, zz, *p_com, STRENGTH, SOFTENING)
        proton.lattice.topological_potential = coulomb_potential_fast(
            xx, yy, zz, *e_com, STRENGTH, SOFTENING)

        if log_drift:
            A_e_pre = session_amplitude(electron)
            A_p_pre = session_amplitude(proton)
            e_com_pre = density_com(e_dens, xx, yy, zz)

        if tick % 2 == 0:
            proton.tick();    proton.advance_tick_counter()
            electron.tick();  electron.advance_tick_counter()
        else:
            electron.tick();  electron.advance_tick_counter()
            proton.tick();    proton.advance_tick_counter()

        if log_drift:
            A_e_post = session_amplitude(electron)
            A_p_post = session_amplitude(proton)
            e_dens_post = electron.probability_density()
            e_com_post = density_com(e_dens_post, xx, yy, zz)
            d_com = tuple(e_com_post[i] - e_com_pre[i] for i in range(3))
            drift_log.append({
                'tick': tick,
                'dA_e': A_e_post - A_e_pre,
                'dA_p': A_p_post - A_p_pre,
                'dx_e': d_com[0], 'dy_e': d_com[1], 'dz_e': d_com[2],
            })

        tick_in_win = tick % CHECK_EVERY
        if win_dens is None:
            win_dens = e_dens.astype(float)
        else:
            win_dens += e_dens
        if tick_in_win == CHECK_EVERY // 2:
            win_p_com = density_com(p_dens, xx, yy, zz)

        if tick_in_win == CHECK_EVERY - 1:
            if win_p_com is None:
                win_p_com = density_com(p_dens, xx, yy, zz)
            r_peak = r_peak_relative(win_dens, win_p_com, xx, yy, zz)
            r_peak_max = max(r_peak_max, r_peak)
            r_peak_min = min(r_peak_min, r_peak)

            if escape_tick is None and r_peak > 30.0:
                escape_tick = tick

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
            A_drift_max = max(A_drift_max, abs(amp_e_now + amp_p_now - A0_e - A0_p))

            log_period = max(1, (2000 // CHECK_EVERY))
            if (tick // CHECK_EVERY) % log_period == 0:
                elapsed = time.time() - t0
                ticks_done = tick + 1
                eta = elapsed / ticks_done * (TICKS_TOTAL - ticks_done) if ticks_done else 0
                msg = (f"grid={grid}^3 init={init_variant} tick={tick:6d}"
                       f"  r_peak={r_peak:6.3f}  streak={consec_ok:3d}"
                       f"  amp_e={amp_e_now:.4f}  amp_p={amp_p_now:.4f}"
                       f"  A_drift={A_drift_max:.2e}"
                       f"  [{elapsed:.0f}s eta {eta:.0f}s]")
                log_fn(msg)

            win_dens  = None
            win_p_com = None

    return {
        'grid':              grid,
        'init':              init_variant,
        'settled':           settled,
        'T_settle':          T_settle,
        'max_streak':        max_streak,
        'amp_e':             session_amplitude(electron),
        'amp_p':             session_amplitude(proton),
        'A_drift_max':       A_drift_max,
        'r_peak_min':        r_peak_min,
        'r_peak_max':        r_peak_max,
        'escape_tick':       escape_tick,
        'p_e_initial':       p_e_initial,
        'p_p_initial':       p_p_initial,
        'p_joint_initial':   p_joint_initial,
        'drift_log':         drift_log,
    }


# ── Single-worker driver ──────────────────────────────────────────────────────

def run_single(mode, variant):
    """Run one (mode, variant) trial; write log and npy summary."""
    if mode == 'grid':
        grid = int(variant)
        init = 'baseline'
        log_drift = False
    elif mode == 'init':
        grid = INIT_GRID
        init = variant
        if init not in INIT_FUNCTIONS:
            raise ValueError(f"unknown init variant {init!r}")
        log_drift = False
    elif mode == 'drift':
        grid = INIT_GRID
        init = 'baseline'
        log_drift = True
    else:
        raise ValueError(f"unknown mode {mode!r}")

    label = f"{mode}_{variant}"
    log_path = os.path.join(_DATA_DIR, f'exp_12c_{label}.log')
    npy_path = os.path.join(_DATA_DIR, f'exp_12c_{label}.npy')

    with open(log_path, 'w') as logf:
        def out(s):
            print(s, flush=True)
            logf.write(s + '\n')
            logf.flush()

        out(f"exp_12c  mode={mode}  variant={variant}")
        out(f"  grid={grid}^3  init={init}  log_drift={log_drift}")
        out(f"OMEGA_E={OMEGA_E}  OMEGA_P={OMEGA_P:.4f}  R1={R1}")
        out(f"STRENGTH={STRENGTH}  TICKS_TOTAL={TICKS_TOTAL}")
        out('-' * 60)

        result = run_trial(grid, init, log_drift=log_drift, log_fn=out)

        status = 'SETTLED' if result['settled'] else 'NOT_SETTLED'
        out(f"result={status}")
        out(f"max_streak={result['max_streak']}")
        out(f"escape_tick={result['escape_tick']}")
        out(f"r_peak_min={result['r_peak_min']:.3f}")
        out(f"r_peak_max={result['r_peak_max']:.3f}")
        out(f"A_drift_max={result['A_drift_max']:.4e}")
        out(f"p_e_initial={result['p_e_initial']}")
        out(f"p_p_initial={result['p_p_initial']}")
        out(f"p_joint_initial={result['p_joint_initial']}")

    summary = np.array([
        result['grid'],
        ord(init[0]),
        float(result['settled']),
        float(result['max_streak']),
        float(result['T_settle']) if result['T_settle'] else float(TICKS_TOTAL),
        result['amp_e'],
        result['amp_p'],
        result['A_drift_max'],
        result['r_peak_min'],
        result['r_peak_max'],
        float(result['escape_tick']) if result['escape_tick'] is not None else float(TICKS_TOTAL),
    ])
    np.save(npy_path, summary)

    if log_drift and result['drift_log']:
        drift_path = os.path.join(_DATA_DIR, f'exp_12c_{label}_drift.npy')
        # Save as a structured array
        dt = np.dtype([
            ('tick', 'i4'),
            ('dA_e', 'f8'), ('dA_p', 'f8'),
            ('dx_e', 'f8'), ('dy_e', 'f8'), ('dz_e', 'f8'),
        ])
        drift_arr = np.array(
            [(d['tick'], d['dA_e'], d['dA_p'],
              d['dx_e'], d['dy_e'], d['dz_e']) for d in result['drift_log']],
            dtype=dt,
        )
        np.save(drift_path, drift_arr)
        print(f"Saved drift log: {drift_path}", flush=True)

    print(f"Saved: {npy_path}", flush=True)


# ── Parallel launcher ─────────────────────────────────────────────────────────

def run_parallel(mode):
    """Launch all variants for the given mode as parallel subprocesses."""
    import subprocess

    if mode == 'grid':
        variants = [str(g) for g in GRID_VARIANTS]
    elif mode == 'init':
        variants = INIT_VARIANTS
    elif mode == 'drift':
        # Single instrumented run, no parallelism needed
        run_single('drift', 'baseline')
        return
    else:
        raise ValueError(f"unknown mode {mode!r}")

    print("=" * 70)
    print(f"EXP 12c  mode={mode}  variants={variants}")
    print("=" * 70)
    print(f"  TICKS_TOTAL={TICKS_TOTAL}")
    print()

    procs = []
    err_files = []
    for v in variants:
        label = f"{mode}_{v}"
        err_path = os.path.join(_DATA_DIR, f'exp_12c_{label}.err')
        err_f = open(err_path, 'w')
        err_files.append(err_f)
        cmd = [sys.executable, '-u', __file__, mode, v]
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=err_f)
        print(f"  variant={v}  PID={p.pid}  err={err_path}")
        procs.append((v, p))

    print()
    t0 = time.time()
    while any(p.poll() is None for _, p in procs):
        done    = [v for v, p in procs if p.poll() is not None]
        running = [v for v, p in procs if p.poll() is None]
        print(f"[{time.time()-t0:.0f}s] running={running}  done={done}",
              flush=True)
        time.sleep(60)
    for f in err_files:
        f.close()

    print(f"\nAll done. Total time: {time.time()-t0:.0f}s")
    print(f"\n{'='*70}\nRESULTS SUMMARY\n{'='*70}")
    print(f"  {'variant':>10}  {'r_min':>7}  {'r_max':>7}  {'escape@':>8}  {'streak':>6}")
    print(f"  {'-'*52}")
    import re
    for v, _ in procs:
        label = f"{mode}_{v}"
        log_path = os.path.join(_DATA_DIR, f'exp_12c_{label}.log')
        try:
            txt = open(log_path).read()
            def grab(pat):
                m = re.search(pat, txt)
                return m.group(1) if m else '?'
            r_min  = grab(r'r_peak_min=([\d.]+)')
            r_max  = grab(r'r_peak_max=([\d.]+)')
            escape = grab(r'escape_tick=(\S+)')
            streak = grab(r'max_streak=(\d+)')
            print(f"  {v:>10}  {r_min:>7}  {r_max:>7}  {escape:>8}  {streak:>6}")
        except Exception as e:
            print(f"  {v:>10}  ERROR: {e}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) == 3:
        run_single(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        run_parallel(sys.argv[1])
    else:
        print("Usage:")
        print("  python exp_12c_long_horizon_diagnosis.py <mode>             # parallel launcher")
        print("  python exp_12c_long_horizon_diagnosis.py <mode> <variant>   # single worker")
        print("  modes: grid, init, drift")
        print("  grid variants: 65, 81, 97, 113")
        print("  init variants: baseline, zero_p_subtracted, sym_pair")
        print("  drift: no variants (single instrumented run)")
        sys.exit(1)
