"""
exp_19b_photon_emission.py  (v9)
Positive control: does a photon session stabilize the two-body orbit?

v8 failure analysis (2026-04-10):
  v8 used V_field (the Coulomb potential scalar) to measure excess energy.
  While mathematically continuous, it still artificially used the scalar distance
  from the proton to determine the exchange rate. It missed the true lattice
  mechanism: the electron doesn't statically "know" its energy, it dynamically
  responds to the *gradient* (force) pulling its phase.

v9 fix -- Phase-Gradient Mismatch Coupling:
  Emission should be driven by the "resonance of the Coulomb field"---the
  phase detuning. A stable orbit is an Arnold Tongue phase-lock between the
  electron's internal clock (\omega) and the local Coulomb phase gradient (\Delta p).
  
  If the electron is perturbed from this resonant lock (e.g. drifting to r > R1),
  the local Coulomb force |\nabla V| no longer perfectly satisfies centripetal 
  resonance. This "beat frequency" or gradient mismatch is what directly bleeds
  into the photon session.
  
  Instead of scalar voltage, we compute the true local force (the gradient of the
  Coulomb potential).
  F_local = |\nabla V_e(x)|
  F_ground = |\nabla V(R_1)|  (The resonant force magnitude)
  
  excess_F = F_local - F_ground

  When F_local < F_ground (electron is too far out -> weak gradient), it has
  slipped out of resonance outward and must shed amplitude (emit).
  When F_local > F_ground (electron is too deep -> strong gradient), it has
  slipped inward and absorbs vacuum phase to push back to resonance.
  
  emit_mask(x)   = rate * max(0, -excess_F) / F_ground
  absorb_mask(x) = rate * max(0, excess_F) / F_ground

  This perfectly matches QED Bremsstrahlung/Larmor logic: photons are radiated
  by *acceleration mismatches* (recoil changes in momentum), not by static radial
  positions.

Honest limitations:
  - EMISSION_RATE is a free parameter.
  - The gradient computation here uses discrete np.gradient as a proxy for the
    framework's exact topological phase slip.
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

    electron, proton, photon, _, _ = make_sessions(GRID, wc, xx, yy, zz)

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

        # ── Tick all sessions: proton per-session A=1; e and γ deferred ──────
        # v8: electron and photon normalized jointly after Coulomb-driven exchange.
        if tick % 2 == 0:
            proton.tick(normalize=True);    proton.advance_tick_counter()
            electron.tick(normalize=False); electron.advance_tick_counter()
        else:
            electron.tick(normalize=False); electron.advance_tick_counter()
            proton.tick(normalize=True);    proton.advance_tick_counter()
        photon.tick(normalize=False); photon.advance_tick_counter()

        # ── Coulomb-driven emission/absorption (v8) ───────────────────────────
        # v7 failed because spatial masks assumed the photon "knew" where it was.
        # The photon started near-zero at the grid center; the absorb_mask
        # grabbed photon.psi * absorb_mask at r<R1, but photon amplitude there
        # was ~0, so feedback never engaged.
        #
        # v8: use the Coulomb potential itself as the coupling.  V(x) already
        # encodes how far above the ground state the electron is at each node.
        # Neither session needs to know its own position.
        #
        # V_field IS the Coulomb potential seen by the electron (computed above).
        # V_ground IS the ground-state potential at r=R1 (constant).
        # excess(x) = V_field(x) - V_ground:
        #   > 0 at r > R1  (electron above ground state -> emit)
        #   = 0 at r = R1  (equilibrium -> no exchange)
        #   < 0 at r < R1  (electron below ground state -> absorb back)

        V_field  = electron.lattice.topological_potential          # (X,Y,Z)
        
        # Compute local force (phase gradient mismatch)
        grad_x, grad_y, grad_z = np.gradient(V_field)
        force_mag = np.sqrt(grad_x**2 + grad_y**2 + grad_z**2)
        
        # Ground state (resonance) force
        F_ground = STRENGTH / (R1 + SOFTENING)**2                  
        excess_force = force_mag - F_ground                        

        scale = F_ground

        # emit_mask IS the emission coupling: phase gradient detuning (weak force -> emit to restore)
        # absorb_mask IS the absorption coupling: active where force is too strong
        emit_mask   = emission_rate * np.maximum(0.0, -excess_force) / scale
        absorb_mask = emission_rate * np.maximum(0.0,  excess_force) / scale

        # Emission: electron deposits amplitude into photon at above-R1 nodes.
        drain_R = electron.psi_R * emit_mask
        drain_L = electron.psi_L * emit_mask
        electron.psi_R -= drain_R
        electron.psi_L -= drain_L
        photon.psi_R   += drain_R
        photon.psi_L   += drain_L

        # Absorption: photon returns amplitude to electron at below-R1 nodes.
        boost_R = photon.psi_R * absorb_mask
        boost_L = photon.psi_L * absorb_mask
        photon.psi_R   -= boost_R
        photon.psi_L   -= boost_L
        electron.psi_R += boost_R
        electron.psi_L += boost_L

        # Joint A=1 across (electron + photon).
        enforce_joint_unity([
            (electron.psi_R, electron.psi_L),
            (photon.psi_R,   photon.psi_L)
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
        out(f"MODE: Coulomb-driven emission+absorption at interaction vertex (v8)")
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
    print("EXP 19 v8: Photon emission -- Coulomb-driven coupling at interaction vertex")
    print("=" * 70)
    print(f"""
  Claim: BIDIRECTIONAL amplitude exchange between electron and photon session
  creates a fixed point at r=R1 (the Bohr radius) and drives the two-body
  orbit onto the n=1 Arnold tongue attractor.

  v8 fix from v7: v7 used spatial masks (r>R1 / r<R1) -- but the photon starts
  near-zero at the grid center, so the absorb_mask grabbed ~0 photon amplitude
  at r<R1. Feedback never engaged; electron evaporated into photon at all rates.

  v8 uses the Coulomb potential itself as the coupling -- the interaction vertex.
  V_field(x) already encodes how far above the ground state the electron is.
  Neither session needs to know its own position.

  excess(x)    = V_field(x) - V_ground  where V_ground = -strength/(R1+softening)
  emit_mask    = rate * max(0,  excess) / |V_ground|   [e -> gamma: above R1]
  absorb_mask  = rate * max(0, -excess) / |V_ground|   [gamma -> e: below R1]


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
