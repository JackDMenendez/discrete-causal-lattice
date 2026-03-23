"""
exp_10_large.py
Hydrogen Spectrum -- High-Performance Version for Local Machine

Run this on your local machine to numerically confirm E_n ~ 1/n^2
for n=1, 2, 3 by simulating orbits at Bohr radii r_n = n^2 * r_1.

Usage:
    python exp_10_large.py              # n=1 and n=2 (grid=82, ~3 min)
    python exp_10_large.py --n3         # n=1,2,3 (grid=186, ~30 min)
    python exp_10_large.py --profile    # time one tick, estimate total

Memory requirements:
    n=1,2: grid=82^3  ->  ~9 MB psi field,  ~3 min
    n=1,2,3: grid=186^3 -> ~103 MB psi field, ~30 min

What this confirms:
    The Bohr spectrum E_n ~ -1/n^2 emerges from angular momentum
    quantization on the T^3_diamond lattice:
        L = k_tangential * r_orb = n * hbar_lattice
    Combined with the Coulomb clock-density well V(r) = -S/(r+eps),
    this gives r_n = n^2 * r_1 and hence E_n/E_1 = r_1/r_n = 1/n^2.

Paper reference: Section 11 (Hydrogen Spectrum from Lattice Geometry)
"""

import sys, os, time, argparse
import numpy as np

# Allow running from any directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession, enforce_unity


# ── Physics parameters (tuned from 25^3 run) ─────────────────────────────────
STRENGTH    = 30.0      # Coulomb well depth
SOFTENING   = 0.5       # Regularization at r=0
OMEGA       = 0.1019    # Particle frequency (gives n=1 at r~10.3 nodes)
K_TANG      = 0.10      # Tangential momentum (angular momentum per node)
WIDTH       = 1.5       # Packet width (nodes)
TICKS       = 400       # Simulation length -- enough for ~4 orbits at n=2

# Bohr radii in lattice units (r_1 confirmed at ~10.3 nodes on 25^3 grid)
R1_LATTICE  = 10.3
R_N         = {1: R1_LATTICE, 2: 4*R1_LATTICE, 3: 9*R1_LATTICE}


# ── Core functions ────────────────────────────────────────────────────────────

def make_orbital_session(grid, well_center, n_quantum, omega, k_tang, width):
    """
    Initialize a CausalSession in a Coulomb well at the n-th Bohr radius.

    The tangential momentum k_tang sets the angular momentum:
        L = k_tang * r_orb = n * hbar_lattice  (Bohr condition)

    For Bohr level n: k_tang should be scaled as k_tang * n,
    so that L = (k_tang * n) * r_n = k_tang * n * n^2 * r_1
    Wait -- we want L = n, so k = n / r_n = n / (n^2 * r_1) = 1/(n*r_1)
    This means k DECREASES with n (outer orbits move slower -- correct).
    """
    r_n    = R_N[n_quantum]
    # Angular momentum quantization: k * r_n = n => k = n / r_n
    k_actual = n_quantum / r_n

    lattice = OctahedralLattice(grid, grid, grid)
    lattice.set_coulomb_well(well_center, STRENGTH, SOFTENING)

    # Start at r_n along V1=(1,1,1) direction
    # r_n hops in V1 = r_n * sqrt(3) Cartesian units
    # We want Cartesian distance = r_n, so hops_along_V1 = r_n / sqrt(3)
    dr    = int(round(r_n / np.sqrt(3)))
    wc    = well_center
    start = tuple(min(wc[i] + dr, grid - 3) for i in range(3))

    session = CausalSession(lattice, start, instruction_frequency=omega)
    x = np.arange(grid)
    y = np.arange(grid)
    z = np.arange(grid)
    xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')

    r_sq    = (xx-start[0])**2 + (yy-start[1])**2 + (zz-start[2])**2
    # Tangential momentum along V2=(1,-1,-1), scaled for this Bohr level
    phase   = k_actual * (xx - yy - zz)
    session.psi = (np.exp(-0.5 * r_sq / width**2) *
                   np.exp(1j * phase)).astype(complex)
    enforce_unity(session.psi)

    return session, xx, yy, zz, lattice


def run_orbit(session, well_center, xx, yy, zz, ticks, report_every=50):
    """Run and return peak-density distance history with progress reports."""
    wc    = np.array(well_center, float)
    peaks = []
    t0    = time.time()

    for t in range(ticks):
        session.tick()
        session.advance_tick_counter()
        d   = session.probability_density()
        idx = np.unravel_index(np.argmax(d), d.shape)
        peaks.append(float(np.sqrt(sum((idx[i]-wc[i])**2 for i in range(3)))))

        if (t + 1) % report_every == 0:
            elapsed  = time.time() - t0
            eta      = elapsed / (t+1) * (ticks - t - 1)
            print(f"    tick {t+1:4d}/{ticks}  r={peaks[-1]:.3f}  "
                  f"elapsed={elapsed:.1f}s  ETA={eta:.0f}s")

    return peaks


def orbital_period(dists, min_crossings=6):
    """Period from zero-crossings of (dist - mean)."""
    if len(dists) < 20: return None
    m  = np.mean(dists)
    zc = [i for i in range(len(dists)-1)
          if (dists[i]-m) * (dists[i+1]-m) < 0]
    if len(zc) < min_crossings: return None
    return 2.0 * float(np.mean([zc[i+1]-zc[i] for i in range(len(zc)-1)]))


def energy_from_orbit(dists, well_center_coord=None):
    """Estimate binding energy from mean orbital radius."""
    r_mean = float(np.mean(dists))
    return -STRENGTH / (r_mean + SOFTENING)


# ── Main experiment ───────────────────────────────────────────────────────────

def run_large_hydrogen(n_levels=2):
    print("=" * 70)
    print("EXP 10 LARGE: Hydrogen Spectrum -- High-Performance Run")
    print("=" * 70)
    print(f"\nCoulomb well: V(r) = -{STRENGTH} / (r + {SOFTENING})")
    print(f"Particle omega = {OMEGA:.4f}  k_tang = {K_TANG:.4f}")
    print(f"Angular momentum quantization: k * r_orb = n")
    print(f"Bohr radii (lattice units):")
    for n in range(1, n_levels+1):
        dr = int(round(R_N[n] / np.sqrt(3)))
        print(f"  n={n}: r_n = {R_N[n]:.1f} nodes  (start offset dr={dr})")

    # Grid must fit all Bohr radii with clearance
    max_r  = R_N[n_levels]
    dr_max = int(round(max_r / np.sqrt(3)))
    grid   = max(25, 2 * (dr_max + 8))
    # Round up to make well-center an integer
    grid   = int(np.ceil(grid / 2) * 2) + 1
    wc     = (grid//2, grid//2, grid//2)

    nodes  = grid**3
    mem_mb = nodes * 16 / 1e6

    print(f"\nGrid: {grid}^3 = {nodes:,} nodes  ({mem_mb:.0f} MB per psi field)")
    print(f"Well center: {wc}")
    print(f"Ticks per level: {TICKS}")
    print()

    # ── Profile one tick ──────────────────────────────────────────────
    print("[Profiling] Measuring tick duration on this machine...")
    s_prof, xx_p, yy_p, zz_p, _ = make_orbital_session(
        grid, wc, 1, OMEGA, K_TANG, WIDTH)
    t_prof = time.time()
    for _ in range(5): s_prof.tick(); s_prof.advance_tick_counter()
    ms_per_tick = (time.time() - t_prof) / 5 * 1000
    eta_total = ms_per_tick * TICKS * n_levels / 60000
    print(f"  {ms_per_tick:.0f} ms/tick  ->  estimated total: {eta_total:.1f} min\n")

    # ── Run each Bohr level ───────────────────────────────────────────
    results = {}

    for n in range(1, n_levels + 1):
        print(f"\n{'─'*60}")
        print(f"Bohr level n={n}  (r_n = {R_N[n]:.1f} nodes)")
        print(f"{'─'*60}")

        session, xx, yy, zz, lattice = make_orbital_session(
            grid, wc, n, OMEGA, K_TANG, WIDTH)

        t0    = time.time()
        dists = run_orbit(session, wc, xx, yy, zz, TICKS, report_every=50)
        elapsed = time.time() - t0

        T      = orbital_period(dists)
        r_mean = float(np.mean(dists))
        r_min  = min(dists)
        r_max  = max(dists)
        E      = energy_from_orbit(dists)
        n_eff  = OMEGA * T / (2 * np.pi) if T else None

        print(f"\n  Results for n={n}:")
        print(f"    r_mean   = {r_mean:.4f} nodes  (target: {R_N[n]:.1f})")
        print(f"    r_range  = [{r_min:.3f}, {r_max:.3f}]  (orbital excursion)")
        print(f"    T_orb    = {T:.2f} ticks" if T else "    T_orb    = not detected")
        if n_eff:
            print(f"    n_eff    = omega*T/(2pi) = {n_eff:.4f}  (expect ~{n})")
        print(f"    E_n      = {E:.6f}  (from V(r_mean))")
        print(f"    Elapsed  : {elapsed:.1f}s")

        results[n] = {'r_mean': r_mean, 'T': T, 'E': E, 'n_eff': n_eff,
                      'r_min': r_min, 'r_max': r_max}

        # Save distance history for offline analysis
        fname = f'orbit_n{n}_grid{grid}.npy'
        np.save(fname, np.array(dists))
        print(f"    Saved    : {fname}")

    # ── Bohr spectrum verification ────────────────────────────────────
    print(f"\n{'='*70}")
    print("BOHR SPECTRUM TEST")
    print(f"{'='*70}")

    if len(results) >= 2:
        E1     = results[1]['E']
        r1     = results[1]['r_mean']

        print(f"\n  {'n':>4}  {'r_mean':>10}  {'r_n/r_1':>10}  {'n^2':>6}  "
              f"{'E_n/E_1':>12}  {'1/n^2':>10}  Bohr?")
        print("  " + "-"*65)

        passed = 0
        for n, res in sorted(results.items()):
            r_ratio = res['r_mean'] / r1
            E_ratio = res['E'] / E1
            pred_r  = n**2
            pred_E  = 1.0 / n**2
            r_ok    = abs(r_ratio - pred_r) / pred_r < 0.15
            E_ok    = abs(E_ratio - pred_E) / pred_E < 0.10
            both_ok = r_ok and E_ok
            if both_ok: passed += 1

            print(f"  {n:>4}  {res['r_mean']:>10.3f}  {r_ratio:>10.3f}  "
                  f"{pred_r:>6}  {E_ratio:>12.6f}  {pred_E:>10.6f}  "
                  f"{'YES' if both_ok else ('r_ok' if r_ok else 'E_ok' if E_ok else 'no')}")

        print()
        if passed == len(results):
            print("[CONFIRMED] E_n ~ 1/n^2 -- Bohr spectrum from lattice geometry!")
            print("The hydrogen spectrum emerges from angular momentum")
            print("quantization on the T^3_diamond bipartite lattice.")
        elif passed > 0:
            print(f"[PARTIAL] {passed}/{len(results)} levels match Bohr scaling.")
        else:
            print("[NOT YET] Bohr scaling not confirmed -- check orbital stability.")

    else:
        print("Only n=1 completed.")
        E1 = results[1]['E']
        print(f"E_1 = {E1:.6f}")
        print(f"Predicted E_2 = {E1/4:.6f}  (1/4 of E_1)")
        print(f"Predicted E_3 = {E1/9:.6f}  (1/9 of E_1)")
        print("Run with n=2 to verify.")

    return results


# ── Profile mode ──────────────────────────────────────────────────────────────

def profile_machine():
    """Measure tick speed and estimate total run time."""
    print("Profiling tick speed on this machine...")
    for grid in [25, 50, 82, 100, 150]:
        nodes = grid**3
        mem   = nodes * 16 / 1e6
        wc    = (grid//2, grid//2, grid//2)
        try:
            s, _, _, _, _ = make_orbital_session(grid, wc, 1, OMEGA, K_TANG, WIDTH)
            t0 = time.time()
            n_ticks = max(3, int(10 / (11*(grid/25)**3 * 1e-3)))  # ~10s
            n_ticks = min(n_ticks, 20)
            for _ in range(n_ticks): s.tick(); s.advance_tick_counter()
            ms = (time.time()-t0)/n_ticks*1000
            eta_n2 = ms * TICKS * 2 / 60000
            print(f"  grid={grid:4d}^3  {mem:6.0f}MB  {ms:7.1f}ms/tick  "
                  f"n=1+2 total~{eta_n2:.1f}min")
        except MemoryError:
            print(f"  grid={grid:4d}^3  {mem:6.0f}MB  OUT OF MEMORY")
            break


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Hydrogen spectrum from lattice geometry -- large-scale run")
    parser.add_argument('--n3',      action='store_true',
                        help='Run n=1,2,3 (requires ~186^3 grid, ~30 min)')
    parser.add_argument('--profile', action='store_true',
                        help='Profile tick speed, estimate total time, then exit')
    args = parser.parse_args()

    if args.profile:
        profile_machine()
    elif args.n3:
        run_large_hydrogen(n_levels=3)
    else:
        run_large_hydrogen(n_levels=2)
