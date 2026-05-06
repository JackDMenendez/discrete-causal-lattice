"""
exp_12d_outlier_trace.py
Trace the r(t) evolution at the two exp_12d_tight outliers.

Background.  exp_12d_tight (2026-05-05) found two outliers among 40
trials: k=0.101 on 81^3 (r_mean=15.88, std=9.26) and k=0.101 on 113^3
(r_mean=15.76, std=9.43).  Every other configuration had std in
[1.1, 2.9].  The proposed audit row depends on whether these are
tail noise or a secondary instability.

A time-averaged r_mean with std ~9 doesn't distinguish the two
hypotheses:
  - tail noise: orbit has a brief outward excursion then returns to
    ~ R_1; the std reflects the excursion height.
  - secondary instability: orbit lost lock and walked outward; the
    std reflects the rate of escape.

This experiment runs the two outlier configurations with TICKS=200
(matching exp_12d's longer window) and records r_peak at every
check window from tick 0 onward.  The full trace tells us whether r
recovers (tail noise) or grows monotonically (instability).

Implementation.  Identical run-loop and helpers to exp_12d_tight,
parameterised by (grid, k).  Records r_peak at every CHECK_EVERY=10
ticks.  Saves the trace as an npy and prints a summary.

Self-contained; no modifications to prior experiments.
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

TICKS_TOTAL = 200
CHECK_EVERY = 10

# Two outlier configurations from exp_12d_tight
CONFIGS = [(81, 0.101), (113, 0.101)]

M_E = np.sin(OMEGA_E / 2.0)
M_P = np.sin(OMEGA_P / 2.0)


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


def run_trace(grid, k_e):
    """Run one (grid, k) trial and record r_peak at every check window."""
    log_path = os.path.join(_DATA_DIR,
                            f'exp_12d_outlier_trace_{grid}_k{k_e:.4f}.log')
    npy_path = os.path.join(_DATA_DIR,
                            f'exp_12d_outlier_trace_{grid}_k{k_e:.4f}.npy')

    with open(log_path, 'w') as logf:
        def out(s):
            print(s, flush=True)
            logf.write(s + '\n')
            logf.flush()

        out(f"exp_12d_outlier_trace  grid={grid}^3  k={k_e}")
        out(f"TICKS_TOTAL={TICKS_TOTAL}  CHECK_EVERY={CHECK_EVERY}")
        out('-' * 60)

        wc = (grid//2,) * 3
        xx, yy, zz = make_coords(grid)
        electron, proton = make_sessions(grid, wc, xx, yy, zz, k_e)

        e_com = density_com(electron.probability_density(), xx, yy, zz)
        p_com = density_com(proton.probability_density(), xx, yy, zz)
        electron.lattice.topological_potential = coulomb_potential_fast(
            xx, yy, zz, *p_com, STRENGTH, SOFTENING)
        proton.lattice.topological_potential = coulomb_potential_fast(
            xx, yy, zz, *e_com, STRENGTH, SOFTENING)

        trace = []  # list of (tick, r_peak)
        win_dens = None
        win_p_com = None
        t0 = time.time()

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
                trace.append((tick, r_peak))
                out(f"  tick={tick:4d}  r_peak={r_peak:7.3f}  "
                    f"({time.time()-t0:.0f}s)")
                win_dens = None
                win_p_com = None

        out('-' * 60)
        rs = [r for _, r in trace]
        out(f"r_min = {min(rs):.3f}  r_max = {max(rs):.3f}")
        out(f"r at tick 30-119 mean = {np.mean([r for t,r in trace if 30 <= t < 120]):.3f}")
        out(f"r at tick 120-199 mean = {np.mean([r for t,r in trace if 120 <= t < 200]):.3f}")
        out(f"r last 5 windows mean = {np.mean(rs[-5:]):.3f}")

        np.save(npy_path, np.array(trace))
        out(f"Saved: {npy_path}")


def run_parallel():
    import subprocess

    print("=" * 70)
    print(f"EXP 12d outlier trace - 2 configs in parallel")
    print(f"  CONFIGS={CONFIGS}")
    print(f"  TICKS_TOTAL={TICKS_TOTAL}")
    print("=" * 70)

    procs = []
    err_files = []
    for grid, k in CONFIGS:
        err_path = os.path.join(_DATA_DIR,
                                f'exp_12d_outlier_trace_{grid}_k{k:.4f}.err')
        err_f = open(err_path, 'w')
        err_files.append(err_f)
        cmd = [sys.executable, '-u', __file__, str(grid), str(k)]
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=err_f)
        print(f"  grid={grid}  k={k}  PID={p.pid}")
        procs.append((grid, k, p))

    print()
    t0 = time.time()
    while any(p.poll() is None for _, _, p in procs):
        running = [(g, k) for g, k, p in procs if p.poll() is None]
        done    = [(g, k) for g, k, p in procs if p.poll() is not None]
        print(f"[{time.time()-t0:.0f}s] running={running}  done={done}",
              flush=True)
        time.sleep(30)
    for f in err_files:
        f.close()

    print(f"\nAll done. Total time: {time.time()-t0:.0f}s")
    print(f"\n{'='*70}\nTRACE SUMMARIES\n{'='*70}")
    import re
    for grid, k, _ in procs:
        log_path = os.path.join(_DATA_DIR,
                                f'exp_12d_outlier_trace_{grid}_k{k:.4f}.log')
        try:
            txt = open(log_path).read()
            print(f"\n=== grid={grid}  k={k} ===")
            for pat in [r'r_min = \S+ +r_max = \S+',
                        r'r at tick 30-119 mean = \S+',
                        r'r at tick 120-199 mean = \S+',
                        r'r last 5 windows mean = \S+']:
                m = re.search(pat, txt)
                if m:
                    print(f"  {m.group(0)}")
        except Exception as e:
            print(f"  ERROR: {e}")


if __name__ == '__main__':
    if len(sys.argv) == 3:
        run_trace(int(sys.argv[1]), float(sys.argv[2]))
    else:
        run_parallel()
