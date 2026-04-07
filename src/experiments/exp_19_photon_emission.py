"""
exp_19_photon_emission.py
Positive control: does a photon session stabilize the two-body orbit?

Tests one specific claim: amplitude transfer from the electron session
to a photon session via joint normalization provides the dissipation
needed for the electron to settle onto the n=1 Arnold tongue attractor.

The two-body system (exp_16, exp_18) is demonstrably metastable without
dissipation -- three numerical hypotheses tested and eliminated. This
experiment tests whether photon emission is the missing mechanism.

Design:
  Phase 1 (TICKS_SETTLE): exp_12 initialization, no emission.
    Confirm orbit is in the expected metastable state before adding
    the photon session. Abort if system is already unstable.

  Phase 2 (TICKS_EMIT): switch on amplitude transfer to photon session
    at rate EMISSION_RATE. Monitor whether r_peak converges to R1 and
    stays there.

  Sweep: repeat for each EMISSION_RATE in EMISSION_RATES.
    If stabilization occurs across a range of rates rather than at one
    specific tuned value, that is a stronger result.

Honest limitations:
  - EMISSION_RATE is a free parameter. The formal derivation from the
    continuum limit Dirac matrix element is not yet complete.
  - Success criterion is defined before running: streak >= 3x the best
    two-session result (streak=11), sustained across multiple epochs.
  - If stabilization only occurs at one specific emission rate, that
    is a weaker result and will be reported as such.

Paper reference: Section on photon emission as A=1 necessity.
"""

import sys, os, time
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import (OctahedralLattice, CausalSession, enforce_unity_spinor)

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         '..', '..', 'data')

# ── Fixed parameters (from exp_12, exp_16) ────────────────────────────────────
OMEGA_E   = 0.1019
OMEGA_P   = np.pi / 2.0
STRENGTH  = 30.0
SOFTENING = 0.5
WIDTH_E   = 1.5
WIDTH_P   = 0.5
R1        = 10.3
GRID      = 65

# ── Run parameters ────────────────────────────────────────────────────────────
TICKS_SETTLE  = 3000    # Phase 1: confirm metastable state
TICKS_EMIT    = 15000   # Phase 2: emission active
CHECK_EVERY   = 50      # ticks between stability checks
SETTLE_TOL    = 0.15    # r_peak within 15% of R1

# Success criterion: streak >= 3x best two-session result (streak=11)
SUCCESS_STREAK = 33

# Emission rate sweep -- explicitly phenomenological
EMISSION_RATES = [0.001, 0.003, 0.005, 0.007, 0.010]

M_E = np.sin(OMEGA_E / 2.0)
M_P = np.sin(OMEGA_P / 2.0)


# ── Joint normalization ───────────────────────────────────────────────────────

def joint_normalize(*sessions):
    """
    Normalize sessions jointly: sum(|psi_R|^2 + |psi_L|^2) = 1
    across all sessions combined.
    Modifies in place. Replaces per-session enforce_unity_spinor
    for bound session groups.
    """
    total_norm = np.sqrt(sum(
        np.sum(np.abs(s.psi_R)**2 + np.abs(s.psi_L)**2)
        for s in sessions
    ))
    if total_norm < 1e-12:
        raise RuntimeError("Joint norm collapsed to zero.")
    for s in sessions:
        s.psi_R /= total_norm
        s.psi_L /= total_norm


def transfer_amplitude(source, target, fraction):
    """
    Transfer a fraction of source amplitude to target via phase-matched
    addition. Uses the source's tangential phase gradient as the
    transfer direction -- the orbital momentum the photon carries away.

    fraction is the emission rate per tick (free parameter).
    Does not normalize -- call joint_normalize after.
    """
    if fraction <= 0:
        return
    # Phase-matched transfer: photon gets the tangential gradient
    # of the electron's phase field
    grad = source.phase_gradient_field()   # (3, X, Y, Z)
    tang_mag = np.sqrt(np.sum(grad**2, axis=0))
    tang_phase = np.where(tang_mag > 1e-9,
                          np.arctan2(grad[1], grad[0]),
                          0.0)
    phase_factor = np.exp(1j * tang_phase)

    # Transfer amplitude
    transfer_R = fraction * source.psi_R * phase_factor
    transfer_L = fraction * source.psi_L * phase_factor

    source.psi_R -= transfer_R
    source.psi_L -= transfer_L
    target.psi_R += transfer_R
    target.psi_L += transfer_L


def session_amplitude(session):
    """Total probability in one session."""
    return float(np.sum(
        np.abs(session.psi_R)**2 + np.abs(session.psi_L)**2
    ))


# ── Helpers (from exp_12/exp_16) ──────────────────────────────────────────────

def coulomb_potential(grid, cx, cy, cz, strength, softening):
    x = np.arange(grid)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    r = np.sqrt((xx-cx)**2 + (yy-cy)**2 + (zz-cz)**2)
    return -strength / (r + softening)


def density_com(density):
    total = float(density.sum())
    if total < 1e-12:
        return (0.0, 0.0, 0.0)
    x = np.arange(density.shape[0])
    cx = float(np.einsum('ijk,i->', density, x) / total)
    cy = float(np.einsum('ijk,j->', density,
                          np.arange(density.shape[1])) / total)
    cz = float(np.einsum('ijk,k->', density,
                          np.arange(density.shape[2])) / total)
    return (cx, cy, cz)


def make_sessions(grid, wc):
    """exp_12 initialization: two-body CoM frame, k_init=1/R1."""
    dr_e = R1 / np.sqrt(3.0)
    dr_p = R1 * M_E / (M_P * np.sqrt(3.0))
    k_e  = 1.0 / R1
    k_p  = k_e * M_E / M_P
    sz   = grid

    start_e = tuple(min(int(round(wc[i] + dr_e)), sz-2) for i in range(3))
    start_p = tuple(max(int(round(wc[i] - dr_p)), 1)    for i in range(3))

    x = np.arange(sz)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')

    sx, sy, sz_ = start_e
    env_e = (np.exp(-0.5*((xx-sx)**2+(yy-sy)**2+(zz-sz_)**2)/WIDTH_E**2)
             * np.exp(1j*k_e*(xx-yy-zz))).astype(complex)
    amp_e = env_e / np.sqrt(2.0)
    lat_e = OctahedralLattice(sz, sz, sz)
    electron = CausalSession(lat_e, start_e,
                              instruction_frequency=OMEGA_E)
    electron.psi_R = amp_e.copy()
    electron.psi_L = amp_e.copy()
    enforce_unity_spinor(electron.psi_R, electron.psi_L)

    px, py, pz = start_p
    env_p = (np.exp(-0.5*((xx-px)**2+(yy-py)**2+(zz-pz)**2)/WIDTH_P**2)
             * np.exp(1j*k_p*(-xx+yy+zz))).astype(complex)
    amp_p = env_p / np.sqrt(2.0)
    lat_p = OctahedralLattice(sz, sz, sz)
    proton = CausalSession(lat_p, start_p,
                            instruction_frequency=OMEGA_P)
    proton.psi_R = amp_p.copy()
    proton.psi_L = amp_p.copy()
    enforce_unity_spinor(proton.psi_R, proton.psi_L)

    # Photon session: massless, initialized at near-zero amplitude
    # Frequency set by expected transition energy: omega_E * (1 - 1/4)
    omega_photon = OMEGA_E * 0.75   # n=2 -> n=1 transition proxy
    lat_g = OctahedralLattice(sz, sz, sz)
    photon = CausalSession(lat_g, wc,
                            instruction_frequency=omega_photon,
                            is_massless=True)
    photon.psi_R *= 1e-6
    photon.psi_L *= 1e-6

    return electron, proton, photon, start_e, start_p


def r_peak_relative(density, p_com, n_bins=80):
    """
    PDF peak of electron density relative to live proton CoM.
    Uses windowed (time-averaged) density -- matches stability probe convention.
    """
    g = density.shape[0]
    x = np.arange(g, dtype=float)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    radii = np.sqrt((xx - p_com[0])**2 + (yy - p_com[1])**2 + (zz - p_com[2])**2)
    bins = np.linspace(0.0, float(radii.max()), n_bins + 1)
    P, _ = np.histogram(radii.ravel(), bins=bins, weights=density.ravel())
    if P.sum() < 1e-12:
        return 0.0
    r_centers = 0.5 * (bins[:-1] + bins[1:])
    return float(r_centers[int(np.argmax(P))])


# ── Single trial ──────────────────────────────────────────────────────────────

def run_trial(emission_rate, log_fn=None):
    """
    Run one emission rate trial.
    Returns dict with stabilization result and diagnostics.
    log_fn: optional callable(str) for per-rate logging in worker mode.
    """
    if log_fn is None:
        log_fn = lambda s: None  # noqa: E731
    wc = (GRID//2,) * 3
    electron, proton, photon, start_e, start_p = make_sessions(GRID, wc)

    # Initial potentials
    e_com = density_com(electron.probability_density())
    p_com = density_com(proton.probability_density())
    electron.lattice.topological_potential = coulomb_potential(
        GRID, *p_com, STRENGTH, SOFTENING)
    proton.lattice.topological_potential = coulomb_potential(
        GRID, *e_com, STRENGTH, SOFTENING)

    # Tracking
    consec_ok      = 0
    max_streak     = 0
    settled        = False
    T_settle       = None
    r_peak_history = []
    amp_e_history  = []
    amp_g_history  = []
    phase          = 1   # 1=settle, 2=emit

    # Windowed density accumulation (matches stability probe convention)
    win_dens   = None
    win_p_com  = None   # proton CoM captured at mid-window

    t0 = time.time()
    r_peak = 0.0  # initialise for progress print before first check

    for tick in range(TICKS_SETTLE + TICKS_EMIT):

        # Update potentials from CoM
        e_dens = electron.probability_density()
        p_dens = proton.probability_density()
        e_com  = density_com(e_dens)
        p_com  = density_com(p_dens)
        electron.lattice.topological_potential = coulomb_potential(
            GRID, *p_com, STRENGTH, SOFTENING)
        proton.lattice.topological_potential = coulomb_potential(
            GRID, *e_com, STRENGTH, SOFTENING)

        # Tick all sessions without internal normalization --
        # normalization is handled below (joint or per-session).
        if tick % 2 == 0:
            proton.tick(normalize=False);   proton.advance_tick_counter()
            electron.tick(normalize=False); electron.advance_tick_counter()
        else:
            electron.tick(normalize=False); electron.advance_tick_counter()
            proton.tick(normalize=False);   proton.advance_tick_counter()
        photon.tick(normalize=False); photon.advance_tick_counter()

        # Normalization: per-session in Phase 1, joint in Phase 2
        if tick >= TICKS_SETTLE:
            phase = 2
            transfer_amplitude(electron, photon, emission_rate)
            joint_normalize(electron, proton, photon)
        else:
            # Phase 1: per-session A=1 (no emission, photon stays near-zero)
            enforce_unity_spinor(electron.psi_R, electron.psi_L)
            enforce_unity_spinor(proton.psi_R,   proton.psi_L)
            # Photon not normalized in Phase 1 -- keeps near-zero amplitude

        # Accumulate windowed electron density
        tick_in_win = tick % CHECK_EVERY
        if win_dens is None:
            win_dens = e_dens.astype(float)
        else:
            win_dens += e_dens
        # Capture proton CoM at mid-window for stable reference
        if tick_in_win == CHECK_EVERY // 2:
            win_p_com = density_com(p_dens)

        # Check stability at end of each window
        if tick_in_win == CHECK_EVERY - 1:
            if win_p_com is None:
                win_p_com = density_com(p_dens)
            r_peak = r_peak_relative(win_dens, win_p_com)
            r_peak_history.append((tick, r_peak, phase))
            amp_e_history.append(session_amplitude(electron))
            amp_g_history.append(session_amplitude(photon))

            if tick >= TICKS_SETTLE and not settled:
                if abs(r_peak - R1) / R1 < SETTLE_TOL:
                    consec_ok += 1
                    max_streak = max(max_streak, consec_ok)
                    if consec_ok >= SUCCESS_STREAK:
                        settled  = True
                        T_settle = tick
                else:
                    consec_ok = 0

            # Progress log every ~2000 ticks
            if (tick // CHECK_EVERY) % (2000 // CHECK_EVERY) == 0 and tick > 0:
                elapsed = time.time() - t0
                remaining = TICKS_SETTLE + TICKS_EMIT - tick
                eta = elapsed / tick * remaining if tick > 0 else 0
                msg = (f"tick={tick:6d}  r_peak={r_peak:6.3f}"
                       f"  streak={consec_ok:3d}  phase={phase}"
                       f"  amp_e={amp_e_history[-1]:.4f}"
                       f"  amp_g={amp_g_history[-1]:.6f}"
                       f"  [{elapsed:.0f}s eta {eta:.0f}s]")
                log_fn(msg)

            # Reset window
            win_dens  = None
            win_p_com = None

    return {
        'emission_rate': emission_rate,
        'settled':       settled,
        'T_settle':      T_settle,
        'max_streak':    max_streak,
        'r_peak_history': r_peak_history,
        'amp_e_history':  amp_e_history,
        'amp_g_history':  amp_g_history,
    }


# ── Single-rate worker (called as subprocess) ─────────────────────────────────

def run_single(rate):
    """
    Run one emission rate trial, write log and npy, print results.
    Called when script is invoked with a rate argument.
    """
    label = f"{rate:.4f}".replace('.', '_')
    log_path = os.path.join(_DATA_DIR, f'exp_19_rate_{label}.log')
    npy_path = os.path.join(_DATA_DIR, f'exp_19_rate_{label}.npy')

    with open(log_path, 'w') as logf:
        def out(s):
            print(s, flush=True)
            logf.write(s + '\n')
            logf.flush()

        out(f"exp_19  emission_rate={rate}")
        out(f"OMEGA_E={OMEGA_E}  OMEGA_P={OMEGA_P:.4f}  R1={R1}")
        out(f"STRENGTH={STRENGTH}  GRID={GRID}^3")
        out(f"TICKS_SETTLE={TICKS_SETTLE}  TICKS_EMIT={TICKS_EMIT}")
        out(f"SUCCESS_STREAK={SUCCESS_STREAK}")
        out('-' * 60)

        result = run_trial(rate, log_fn=out)

        status = 'SETTLED' if result['settled'] else 'NOT_SETTLED'
        out(f"result={status}")
        out(f"max_streak={result['max_streak']}")
        out(f"T_settle={result['T_settle']}")

    summary = np.array([
        result['emission_rate'],
        float(result['settled']),
        float(result['max_streak']),
        float(result['T_settle']) if result['T_settle'] else float(TICKS_SETTLE + TICKS_EMIT),
    ])
    np.save(npy_path, summary)
    print(f"Saved: {npy_path}", flush=True)


# ── Parallel launcher ─────────────────────────────────────────────────────────

def run_parallel():
    """
    Launch all EMISSION_RATES as parallel subprocesses.
    Each writes its own log and npy. Aggregate results when all done.
    """
    import subprocess, re

    print("=" * 70)
    print("EXP 19: Photon emission as dissipation -- orbital stabilization")
    print("=" * 70)
    print(f"""
  Claim: a photon session provides the dissipation needed for the
  two-body system to settle onto the n=1 Arnold tongue attractor.

  Honest framing:
    - emission_rate is a free parameter (formal derivation pending)
    - success requires streak >= {SUCCESS_STREAK} (3x best two-session result)
    - stabilization at multiple emission rates is stronger evidence

  Parameters:
    OMEGA_E={OMEGA_E}  OMEGA_P={OMEGA_P:.4f}  R1={R1}
    STRENGTH={STRENGTH}  GRID={GRID}^3
    TICKS_SETTLE={TICKS_SETTLE}  TICKS_EMIT={TICKS_EMIT}
    EMISSION_RATES={EMISSION_RATES}
""")

    print(f"Launching {len(EMISSION_RATES)} parallel workers...")
    procs = []
    for rate in EMISSION_RATES:
        cmd = [sys.executable, '-u', __file__, str(rate)]
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        print(f"  rate={rate}  PID={p.pid}")
        procs.append((rate, p))

    print()
    t0 = time.time()
    while any(p.poll() is None for _, p in procs):
        done  = [r for r, p in procs if p.poll() is not None]
        running = [r for r, p in procs if p.poll() is None]
        print(f"[{time.time()-t0:.0f}s] running={running}  done={done}",
              flush=True)
        time.sleep(300)

    print(f"\nAll done. Total time: {time.time()-t0:.0f}s")

    # ── Aggregate ─────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("RESULTS SUMMARY")
    print(f"{'='*70}")
    print(f"  {'rate':>8}  {'result':>12}  {'max_streak':>11}  {'T_settle':>10}")
    print(f"  {'-'*50}")

    n_settled = 0
    all_results = []
    for rate, _ in procs:
        label = f"{rate:.4f}".replace('.', '_')
        log_path = os.path.join(_DATA_DIR, f'exp_19_rate_{label}.log')
        npy_path = os.path.join(_DATA_DIR, f'exp_19_rate_{label}.npy')
        try:
            txt = open(log_path).read()
            m_res    = re.search(r'result=(\S+)', txt)
            m_streak = re.search(r'max_streak=(\d+)', txt)
            m_ts     = re.search(r'T_settle=(\S+)', txt)
            result_str = m_res.group(1) if m_res else '?'
            streak     = m_streak.group(1) if m_streak else '?'
            t_settle   = m_ts.group(1) if m_ts else '?'
            if result_str == 'SETTLED':
                n_settled += 1
            print(f"  {rate:8.4f}  {result_str:>12}  {streak:>11}  {t_settle:>10}")
        except Exception as e:
            print(f"  {rate:8.4f}  ERROR reading log: {e}")

    passed = n_settled >= 2

    if passed:
        print(f"""
[PASS] Photon session stabilizes orbit at {n_settled}/{len(EMISSION_RATES)} emission rates.
  Dissipation mechanism confirmed. emission_rate phenomenological
  pending formal derivation from continuum limit matrix element.
""")
    elif n_settled == 1:
        print(f"""
[PARTIAL] Stabilization at exactly one emission rate.
  Weaker result -- possible parameter tuning rather than mechanism.
""")
    else:
        print(f"""
[NOT CONFIRMED] No stabilization at any tested emission rate.
  Either the mechanism is insufficient alone, or rate range needs
  adjustment. Report as negative result.
""")

    # Aggregate npy
    rows = []
    for rate, _ in procs:
        label = f"{rate:.4f}".replace('.', '_')
        npy_path = os.path.join(_DATA_DIR, f'exp_19_rate_{label}.npy')
        try:
            rows.append(np.load(npy_path))
        except Exception:
            rows.append(np.array([rate, 0., 0., float(TICKS_SETTLE + TICKS_EMIT)]))
    out = os.path.join(_DATA_DIR, 'exp_19_photon_emission.npy')
    np.save(out, np.array(rows))
    print(f"Saved aggregate: {out}")
    print("columns: emission_rate, settled, max_streak, T_settle")

    return passed


# ── run_trial needs a log_fn parameter for worker mode ───────────────────────

if __name__ == '__main__':
    if len(sys.argv) == 2:
        # Worker mode: single rate
        rate = float(sys.argv[1])
        run_single(rate)
        sys.exit(0)
    else:
        # Launcher mode: all rates in parallel
        passed = run_parallel()
        sys.exit(0 if passed else 1)