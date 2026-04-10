"""
exp_19_photon_emission.py  (v5)
Positive control: does a photon session stabilize the two-body orbit?

Tests one specific claim: momentum-selective PHASE ROTATION at the
electron's outer-orbit, outward-moving wavepacket provides genuine
A=1-compatible dissipation needed to lock onto the n=1 Arnold tongue.

v4 failure analysis:
  v4 used amplitude transfer (electron.psi -= mask * psi; photon.psi += ...).
  This is NOT A=1-compatible: enforce_unity_spinor (called inside tick())
  renormalizes to unit amplitude every tick, cancelling the drain entirely.
  Diagnostic: amp_e=1.0000 at every checkpoint -- drain had zero net effect.
  The orbit was only perturbed in shape, not guided: high rates caused chaos
  (r_peak swings 15→55→8) but never stabilization.

v5 fix -- phase-rotation drain (genuinely A=1-compatible):
  Instead of removing amplitude, we ROTATE the phase of outer-orbit,
  outward-moving components toward inward.  Phase rotations preserve
  |psi|^2 exactly, so enforce_unity_spinor has nothing to undo.

  Physical interpretation:
    The outer-orbit outward-moving wavepacket is the part that, if
    unchecked, causes the orbit to expand.  Rotating its phase toward
    the inward direction (by angle mask radians) reduces its net outward
    momentum contribution without changing total probability.  The photon
    absorbs the conjugate phase rotation, carrying away the excess outward
    phase coherence.

  Each tick:
    1. electron and proton tick (per-session A=1).
    2. photon ticks (per-session A=1, massless propagation).
    3. Compute r_hat(x) from proton CoM.
    4. v_r(x) = grad(phi_e) . r_hat  (radial velocity, >0 = outward).
    5. mask(x) = rate * max(0, r-R1)/R1 * max(0, v_r) / v_r_max
       [zero at r<=R1 and for inward-moving nodes]
    6. rot(x) = exp(-i * mask(x))       [unit-amplitude by construction]
    7. electron.psi_R *= rot             [rotate outward phase toward inward]
       electron.psi_L *= rot
       photon.psi_R   *= conj(rot)      [photon absorbs conjugate phase]
       photon.psi_L   *= conj(rot)
       [No enforce_unity_spinor needed -- phases don't change norms]

  No Phase 1 settle period (v4 lesson: orbit degrades before emission starts).

  Sweep: repeat for each EMISSION_RATE in EMISSION_RATES.

Honest limitations:
  - EMISSION_RATE is a free parameter (formal derivation pending).
  - Success criterion: streak >= SUCCESS_STREAK.
  - If only one rate stabilizes, that is a weaker result.

Paper reference: Section on photon emission as A=1 necessity.
"""

import sys, os, time
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import (OctahedralLattice, CausalSession, enforce_unity_spinor)
from src.core.UnityConstraint import enforce_joint_unity

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
# PERFORMANCE NOTE (2026-04-09):
#   tick() costs ~3.3s on GRID=65^3.  Bottleneck is _kinetic_hop: two
#   np.angle (arctan2) + np.exp(1j*delta_p) calls per direction per tick.
#   Full fix: numba JIT on _kinetic_hop (see notes below).
#   Interim: TICKS_TOTAL=6000 for a ~5.5-hour probe run.  Increase to
#   18000 once the JIT fix is in place or use a nightly batch.
TICKS_TOTAL   = 6000    # interim: ~5.5 hrs/worker @3.3s/tick; raise to 18000 after JIT fix
CHECK_EVERY   = 50      # ticks between stability checks
SETTLE_TOL    = 0.15    # r_peak within 15% of R1

# Success criterion: streak >= 3x best two-session result (streak=11)
SUCCESS_STREAK = 33

# Outer-orbit emission rate sweep
# mask(x) = rate * max(0, r-R1)/R1 * max(0, v_r)/v_r_max
# Zero at r<=R1 and for inward-moving nodes; active only outside+outward.
EMISSION_RATES = [0.001, 0.005, 0.010, 0.020, 0.050]

M_E = np.sin(OMEGA_E / 2.0)
M_P = np.sin(OMEGA_P / 2.0)


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_coords(grid):
    """
    Precompute integer coordinate grids once.
    Returns (xx, yy, zz) each of shape (grid, grid, grid).
    Pass these to coulomb_potential_fast and radial_field_fast to avoid
    rebuilding meshgrid every tick.
    """
    x = np.arange(grid, dtype=float)
    return np.meshgrid(x, x, x, indexing='ij')


def coulomb_potential_fast(xx, yy, zz, cx, cy, cz, strength, softening):
    """Coulomb potential using precomputed coordinate grids (no meshgrid)."""
    r = np.sqrt((xx-cx)**2 + (yy-cy)**2 + (zz-cz)**2)
    return -strength / (r + softening)


def radial_field_fast(xx, yy, zz, p_com):
    """
    Radial distance and unit vector from proton CoM.
    Returns (r_field, rx, ry, rz): all shape (GRID,GRID,GRID).
    Uses precomputed coordinate grids (no meshgrid per tick).
    """
    dx = xx - p_com[0]
    dy = yy - p_com[1]
    dz = zz - p_com[2]
    r = np.sqrt(dx**2 + dy**2 + dz**2)
    safe_r = np.where(r < 1e-9, 1.0, r)   # avoid divide-by-zero at CoM
    return r, dx/safe_r, dy/safe_r, dz/safe_r


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
    """Total probability in one session."""
    return float(np.sum(
        np.abs(session.psi_R)**2 + np.abs(session.psi_L)**2
    ))


def make_sessions(grid, wc, xx, yy, zz):
    """exp_12 initialization: two-body CoM frame, k_init=1/R1.
    xx, yy, zz: precomputed coordinate grids from make_coords().
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

    # Photon session: massless, initialized at near-zero amplitude.
    # Will be normalized per-session after each emission.
    omega_photon = OMEGA_E * 0.75   # proxy for n=2->n=1 transition energy
    lat_g = OctahedralLattice(sz, sz, sz)
    photon = CausalSession(lat_g, wc,
                            instruction_frequency=omega_photon,
                            is_massless=True)
    # Start photon near-zero; enforce_unity_spinor after first emission tick
    photon.psi_R *= 1e-6
    photon.psi_L *= 1e-6

    return electron, proton, photon, start_e, start_p


def r_peak_relative(density, p_com, xx, yy, zz, n_bins=80):
    """
    PDF peak of electron density relative to live proton CoM.
    Uses precomputed coordinate grids.
    """
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

    # Precompute coordinate grids ONCE -- eliminates meshgrid from every tick.
    # This is the main performance fix: coulomb_potential and radial_field
    # previously each called np.meshgrid(65,65,65) every tick (~3s/tick).
    xx, yy, zz = make_coords(GRID)

    electron, proton, photon, start_e, start_p = make_sessions(GRID, wc, xx, yy, zz)

    # Initial potentials
    e_com = density_com(electron.probability_density(), xx, yy, zz)
    p_com = density_com(proton.probability_density(), xx, yy, zz)
    electron.lattice.topological_potential = coulomb_potential_fast(
        xx, yy, zz, *p_com, STRENGTH, SOFTENING)
    proton.lattice.topological_potential = coulomb_potential_fast(
        xx, yy, zz, *e_com, STRENGTH, SOFTENING)

    # Tracking
    consec_ok      = 0
    max_streak     = 0
    settled        = False
    T_settle       = None

    # Windowed density accumulation
    win_dens  = None
    win_p_com = None

    t0 = time.time()
    r_peak = 0.0

    for tick in range(TICKS_TOTAL):

        # ── Update Coulomb potentials from live CoM ────────────────────────
        e_dens = electron.probability_density()
        p_dens = proton.probability_density()
        e_com  = density_com(e_dens, xx, yy, zz)
        p_com  = density_com(p_dens, xx, yy, zz)
        electron.lattice.topological_potential = coulomb_potential_fast(
            xx, yy, zz, *p_com, STRENGTH, SOFTENING)
        proton.lattice.topological_potential = coulomb_potential_fast(
            xx, yy, zz, *e_com, STRENGTH, SOFTENING)

        # ── Tick all sessions with Manual A=1 ─────────────────────────────
        # v6 FIX: Turn off normalize for electron & photon so we can jointly apply A=1 later.
        if tick % 2 == 0:
            proton.tick(normalize=True);   proton.advance_tick_counter()
            electron.tick(normalize=False); electron.advance_tick_counter()
        else:
            electron.tick(normalize=False); electron.advance_tick_counter()
            proton.tick(normalize=True);   proton.advance_tick_counter()
        photon.tick(normalize=False); photon.advance_tick_counter()

        # ── Momentum-selective outer-orbit phase drain (active every tick) ──
        # v6: Amplitude transfer + joint normalization.

        # Radial geometry from live proton CoM
        r_field, rx, ry, rz = radial_field_fast(xx, yy, zz, p_com)

        # Radial velocity: phase gradient projected onto r_hat.
        # v_r > 0 = outward-moving; v_r < 0 = inward-moving.
        # grad(phi_e) IS the local de Broglie momentum field of the electron.
        grad = electron.phase_gradient_field()   # (3, X, Y, Z)
        v_r = grad[0]*rx + grad[1]*ry + grad[2]*rz  # (X, Y, Z)
        outward = np.maximum(0.0, v_r)

        # Normalise outward weight so peak = 1
        v_r_max = outward.max()
        if v_r_max < 1e-12:
            outward_norm = outward          # all inward: no drain this tick
        else:
            outward_norm = outward / v_r_max

        # mask(x) IS the amplitude drain fraction.
        # Zero at r<=R1; zero for inward-moving nodes.
        outer_frac = emission_rate * np.maximum(0.0, r_field - R1) / R1
        mask = outer_frac * outward_norm

        # Steal amplitude:
        amp_R_drain = electron.psi_R * mask
        amp_L_drain = electron.psi_L * mask
        
        electron.psi_R -= amp_R_drain
        electron.psi_L -= amp_L_drain
        
        # Photon absorbs the amplitude (it receives the phase implicitly via complex sum)
        photon.psi_R += amp_R_drain
        photon.psi_L += amp_L_drain

        # Apply Joint A=1 onto the joint (electron + photon) state!
        enforce_joint_unity([
            (electron.psi_R, electron.psi_L),
            (photon.psi_R, photon.psi_L)
        ])

        # ── Windowed electron density ──────────────────────────────────────
        tick_in_win = tick % CHECK_EVERY
        if win_dens is None:
            win_dens = e_dens.astype(float)
        else:
            win_dens += e_dens
        if tick_in_win == CHECK_EVERY // 2:
            win_p_com = density_com(p_dens, xx, yy, zz)

        # ── Stability check at end of each window ─────────────────────────
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

            # Progress log every ~2000 ticks
            if (tick // CHECK_EVERY) % (2000 // CHECK_EVERY) == 0 and tick > 0:
                elapsed = time.time() - t0
                remaining = TICKS_TOTAL - tick
                eta = elapsed / tick * remaining if tick > 0 else 0
                amp_e = session_amplitude(electron)
                amp_g = session_amplitude(photon)
                msg = (f"tick={tick:6d}  r_peak={r_peak:6.3f}"
                       f"  streak={consec_ok:3d}"
                       f"  amp_e={amp_e:.4f}"
                       f"  amp_g={amp_g:.6f}"
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
        out(f"TICKS_TOTAL={TICKS_TOTAL}")
        out(f"SUCCESS_STREAK={SUCCESS_STREAK}")
        out(f"MODE: momentum-selective outer-orbit phase rotation (v5, A=1-compatible)")
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
        float(result['T_settle']) if result['T_settle'] else float(TICKS_TOTAL),
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
    print("EXP 19 v5: Photon emission -- momentum-selective phase rotation (A=1-compatible)")
    print("=" * 70)
    print(f"""
  Claim: momentum-selective PHASE ROTATION at the outer-orbit, outward-moving
  wavepacket provides genuine A=1-compatible dissipation that drives the
  two-body orbit onto the n=1 Arnold tongue attractor.

  v5 fix from v4: phase rotation replaces amplitude transfer.
  v4 used psi -= mask*psi; enforce_unity_spinor undid this every tick (amp_e=1
  throughout).  Phase rotation exp(-i*mask) has |rot|=1 so A=1 is preserved
  exactly without renormalization.  Photon absorbs conjugate phase.

  mask(x) = rate * max(0, r-R1)/R1 * max(0, v_r) / v_r_max  [rotation angle, rad]
  rot(x)  = exp(-i * mask(x))  [U(1) field, unit amplitude]
  where v_r = grad(phi_e) . r_hat is the radial momentum of the electron.

  Honest framing:
    - emission_rate is a free parameter (formal derivation pending)
    - success requires streak >= {SUCCESS_STREAK} (3x best two-session result)
    - stabilization at multiple emission rates is stronger evidence

  Parameters:
    OMEGA_E={OMEGA_E}  OMEGA_P={OMEGA_P:.4f}  R1={R1}
    STRENGTH={STRENGTH}  GRID={GRID}^3
    TICKS_TOTAL={TICKS_TOTAL}
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
        done    = [r for r, p in procs if p.poll() is not None]
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
    for rate, _ in procs:
        label = f"{rate:.4f}".replace('.', '_')
        log_path = os.path.join(_DATA_DIR, f'exp_19_rate_{label}.log')
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
  Dissipation mechanism confirmed via outer-orbit selective drain.
  emission_rate is phenomenological pending Fermi Golden Rule derivation.
""")
    elif n_settled == 1:
        print("""
[PARTIAL] Stabilization at exactly one emission rate.
  Weaker result -- possible parameter tuning rather than mechanism.
  Run wider sweep before concluding.
""")
    else:
        print("""
[FAIL] No stabilization across all emission rates.
  Outer-orbit selective drain is insufficient for orbital stabilization.
  Next: investigate whether the drain rate magnitude or spatial profile
  needs adjustment, or whether the photon session architecture is
  fundamentally wrong.
""")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) == 2:
        run_single(float(sys.argv[1]))
    else:
        run_parallel()
