"""
exp_12d_grid_independence_k_scan.py
Validate exp_12's k-scan resonance result across grid sizes.

Background.  exp_12 reports k_min = 0.0970 vs k_Bohr = 0.0971 (four
significant figures, matching the Bohr-radius condition omega*R_1 = pi/3).
That measurement is at GRID=65^3.

exp_12c (2026-05-05) established that the bare two-body orbit
escapes by tick ~140 on grids >= 81^3, while remaining apparently
stable for ~2000 ticks on 65^3.  The 65^3 "stability" is a
finite-volume artefact: boundary conditions reflect/wrap outgoing
flow back into the well, confining the wave packet near R_1.

The question this experiment answers: is the k_min = 0.0970
resonance itself grid-dependent?  If the lock-in attractor is
grid-independent, k_min should be the same on 65, 81, 97, and
113^3.  If the lock-in is also a confinement effect, k_min may
shift or the resonance may disappear at larger grids.

Implementation.  For each grid size in {65, 81, 97, 113}, sweep k
across a window centred on k_Bohr_fixed = 1/R_1 = 0.09709,
running short-duration trials (~200 ticks) so the measurement
window stays within the stable-orbit phase even on large grids.

  k window: K_VALUES = [0.085, 0.090, 0.092, 0.094, 0.096, 0.0971,
                        0.099, 0.101, 0.103, 0.106]
  ticks:    BURN_IN = 50, MEAS_WINDOW = ticks 50-150 (100-tick
            average of r_peak)
  per-grid: 10 k values, sequential per worker
  parallel: 4 workers, one per grid

For each (grid, k) we record the time-averaged r_peak over the
measurement window.  k_min for the grid is the k value minimising
|r_peak - R_1|.

Per-tick cost scales as N^3.  Wall-clock estimate:
  65^3:  100 ticks * 0.05 s/tick = 5 s/k * 10 k = 50 s
  81^3:  ~100 s
  97^3:  ~170 s
  113^3: ~270 s
  parallel max: ~5 min

Self-contained; no modifications to exp_12, exp_12b, exp_12c, or
any other prior experiment.
"""

import sys, os, time
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import (OctahedralLattice, CausalSession, enforce_unity_spinor)

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         '..', '..', 'data')

# ── Fixed physics parameters ──────────────────────────────────────────────────
OMEGA_E   = 0.1019
OMEGA_P   = np.pi / 2.0
STRENGTH  = 30.0
SOFTENING = 0.5
WIDTH_E   = 1.5
WIDTH_P   = 0.5
R1        = 10.3
K_BOHR    = 1.0 / R1   # = 0.09709...

# ── Run parameters ────────────────────────────────────────────────────────────
TICKS_TOTAL    = int(os.environ.get('EXP12D_TICKS', '200'))
BURN_IN        = int(os.environ.get('EXP12D_BURN', '50'))
CHECK_EVERY    = 10  # tighter than exp_12b's 20 since the run is shorter

# k values to scan around K_BOHR ≈ 0.0971
K_VALUES = [0.085, 0.090, 0.092, 0.094, 0.096, 0.0971, 0.099, 0.101, 0.103, 0.106]

# Grid sizes to sweep
GRID_VARIANTS = [65, 81, 97, 113]

M_E = np.sin(OMEGA_E / 2.0)
M_P = np.sin(OMEGA_P / 2.0)


# ── Helpers (mirror of exp_12c, exp_12b) ──────────────────────────────────────

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


def r_peak_relative(density, p_com, xx, yy, zz, n_bins=80):
    radii = np.sqrt((xx - p_com[0])**2 + (yy - p_com[1])**2 + (zz - p_com[2])**2)
    bins = np.linspace(0.0, float(radii.max()), n_bins + 1)
    P, _ = np.histogram(radii.ravel(), bins=bins, weights=density.ravel())
    if P.sum() < 1e-12:
        return 0.0
    r_centers = 0.5 * (bins[:-1] + bins[1:])
    return float(r_centers[int(np.argmax(P))])


def make_sessions(grid, wc, xx, yy, zz, k_e):
    """exp_12 init style, parameterised by k_e (the electron's phase wavevector
    magnitude).  Proton's k_p is mass-weighted: k_p = k_e * M_E / M_P."""
    dr_e = R1 / np.sqrt(3.0)
    dr_p = R1 * M_E / (M_P * np.sqrt(3.0))
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


# ── Single trial at fixed (grid, k) ───────────────────────────────────────────

def run_single_k(grid, k_e):
    """Run one (grid, k) trial.  Returns time-averaged r_peak measured over
    the post-burn-in window."""
    wc = (grid//2,) * 3
    xx, yy, zz = make_coords(grid)
    electron, proton = make_sessions(grid, wc, xx, yy, zz, k_e)

    e_com = density_com(electron.probability_density(), xx, yy, zz)
    p_com = density_com(proton.probability_density(), xx, yy, zz)
    electron.lattice.topological_potential = coulomb_potential_fast(
        xx, yy, zz, *p_com, STRENGTH, SOFTENING)
    proton.lattice.topological_potential = coulomb_potential_fast(
        xx, yy, zz, *e_com, STRENGTH, SOFTENING)

    r_peak_samples = []  # collected during measurement window
    win_dens = None
    win_p_com = None

    for tick in range(TICKS_TOTAL):
        e_dens = electron.probability_density()
        p_dens = proton.probability_density()
        e_com  = density_com(e_dens, xx, yy, zz)
        p_com  = density_com(p_dens, xx, yy, zz)
        electron.lattice.topological_potential = coulomb_potential_fast(
            xx, yy, zz, *p_com, STRENGTH, SOFTENING)
        proton.lattice.topological_potential = coulomb_potential_fast(
            xx, yy, zz, *e_com, STRENGTH, SOFTENING)

        if tick % 2 == 0:
            proton.tick();    proton.advance_tick_counter()
            electron.tick();  electron.advance_tick_counter()
        else:
            electron.tick();  electron.advance_tick_counter()
            proton.tick();    proton.advance_tick_counter()

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
            if tick >= BURN_IN:
                r_peak_samples.append(r_peak)
            win_dens = None
            win_p_com = None

    if r_peak_samples:
        r_mean = float(np.mean(r_peak_samples))
        r_std  = float(np.std(r_peak_samples))
    else:
        r_mean = 0.0
        r_std  = 0.0

    return {
        'grid':    grid,
        'k':       k_e,
        'r_mean':  r_mean,
        'r_std':   r_std,
        'n_samples': len(r_peak_samples),
    }


# ── Per-grid driver: scan all k values for one grid ───────────────────────────

def run_grid(grid):
    """For one grid, scan all K_VALUES sequentially.  Write log + npy."""
    log_path = os.path.join(_DATA_DIR, f'exp_12d_grid_{grid}.log')
    npy_path = os.path.join(_DATA_DIR, f'exp_12d_grid_{grid}.npy')

    with open(log_path, 'w') as logf:
        def out(s):
            print(s, flush=True)
            logf.write(s + '\n')
            logf.flush()

        out(f"exp_12d  grid={grid}^3  k-scan over {K_VALUES}")
        out(f"OMEGA_E={OMEGA_E}  R1={R1}  K_BOHR={K_BOHR:.5f}")
        out(f"TICKS_TOTAL={TICKS_TOTAL}  BURN_IN={BURN_IN}  CHECK_EVERY={CHECK_EVERY}")
        out('-' * 60)

        results = []
        t0 = time.time()
        for i, k in enumerate(K_VALUES):
            tk = time.time()
            r = run_single_k(grid, k)
            elapsed = time.time() - tk
            out(f"  k={k:.4f}  r_mean={r['r_mean']:.3f}  r_std={r['r_std']:.3f}"
                f"  n={r['n_samples']}  ({elapsed:.0f}s)")
            results.append(r)

        # Identify k_min as the k value minimising |r_mean - R1|
        deltas = [abs(r['r_mean'] - R1) for r in results]
        i_min = int(np.argmin(deltas))
        k_min = results[i_min]['k']
        r_min_at_kmin = results[i_min]['r_mean']

        out('-' * 60)
        out(f"k_min = {k_min:.4f}  (vs K_Bohr = {K_BOHR:.5f})")
        out(f"r_at_k_min = {r_min_at_kmin:.3f}  (vs R_1 = {R1})")
        out(f"|r_at_k_min - R_1| = {abs(r_min_at_kmin - R1):.3f}")
        out(f"total wall-clock: {time.time() - t0:.0f}s")

        summary = np.array([
            [r['k'], r['r_mean'], r['r_std'], r['n_samples']]
            for r in results
        ])
        np.save(npy_path, summary)
        print(f"Saved: {npy_path}", flush=True)


# ── Parallel launcher ─────────────────────────────────────────────────────────

def run_parallel():
    """Launch one subprocess per grid size, all k values per grid sequential."""
    import subprocess

    print("=" * 70)
    print(f"EXP 12d  grid-independence k-scan")
    print(f"  GRID_VARIANTS={GRID_VARIANTS}")
    print(f"  K_VALUES={K_VALUES}")
    print(f"  TICKS_TOTAL={TICKS_TOTAL}  BURN_IN={BURN_IN}")
    print("=" * 70)

    procs = []
    err_files = []
    for grid in GRID_VARIANTS:
        err_path = os.path.join(_DATA_DIR, f'exp_12d_grid_{grid}.err')
        err_f = open(err_path, 'w')
        err_files.append(err_f)
        cmd = [sys.executable, '-u', __file__, str(grid)]
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=err_f)
        print(f"  grid={grid}  PID={p.pid}  err={err_path}")
        procs.append((grid, p))

    print()
    t0 = time.time()
    while any(p.poll() is None for _, p in procs):
        done    = [g for g, p in procs if p.poll() is not None]
        running = [g for g, p in procs if p.poll() is None]
        print(f"[{time.time()-t0:.0f}s] running={running}  done={done}",
              flush=True)
        time.sleep(30)
    for f in err_files:
        f.close()

    print(f"\nAll done. Total time: {time.time()-t0:.0f}s")
    print(f"\n{'='*70}\nRESULTS SUMMARY\n{'='*70}")
    print(f"  {'grid':>5}  {'k_min':>8}  {'r_at_k_min':>12}  {'|r-R1|':>8}")
    print(f"  {'-'*40}")
    import re
    for grid, _ in procs:
        log_path = os.path.join(_DATA_DIR, f'exp_12d_grid_{grid}.log')
        try:
            txt = open(log_path).read()
            def grab(pat, default='?'):
                m = re.search(pat, txt)
                return m.group(1) if m else default
            k_min      = grab(r'k_min = (\S+)')
            r_at_k_min = grab(r'r_at_k_min = (\S+)')
            delta      = grab(r'\|r_at_k_min - R_1\| = (\S+)')
            print(f"  {grid:>5}  {k_min:>8}  {r_at_k_min:>12}  {delta:>8}")
        except Exception as e:
            print(f"  {grid:>5}  ERROR: {e}")

    print()
    print("Interpretation:")
    print(f"  K_BOHR = {K_BOHR:.5f}")
    print(f"  R_1 = {R1}")
    print(f"  If k_min stays near K_BOHR across all grids, the lock-in resonance")
    print(f"  is grid-independent (exp_12's PASS is robust).")
    print(f"  If k_min shifts with grid, the lock-in is partly a confinement effect.")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) == 2:
        run_grid(int(sys.argv[1]))
    else:
        run_parallel()
