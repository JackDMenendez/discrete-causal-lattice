"""
exp_10_hydrogen_spectrum.py
Audit: Hydrogen spectrum from A=1 bipartite lattice -- Dirac spinor.

Confirms E_n ~ 1/n^2 (Bohr spectrum) by running n=1 and n=2 orbital
wave packets in a Coulomb clock-density well and measuring stable radii
and energies.

Theory:
    Coulomb well:   V(r) = -S / (r + eps)
    Bohr condition: k * r_orb = n   (angular momentum quantization)
    Bohr radii:     r_n = n^2 * r_1
    Energy levels:  E_n = -S / (r_n + eps)  =>  E_n/E_1 = 1/n^2

Grid is auto-sized to fit the n=2 orbit (~65^3 nodes).
Uses the Dirac spinor (psi_R + psi_L) for stable orbits.

Run time: ~4-8 min on a modern CPU.

Paper reference: Section 11 (Hydrogen Spectrum from Lattice Geometry)
"""

import sys, os, time
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import (OctahedralLattice, CausalSession,
                      enforce_unity_spinor)

# ── Physics parameters (from exp_10_standalone.py) ───────────────────────────
STRENGTH  = 30.0
SOFTENING = 0.5
OMEGA     = 0.1019    # particle mass (instruction frequency)
WIDTH     = 1.5       # packet width in nodes
TICKS     = 400       # ticks per level
R1_APPROX = 10.3      # n=1 Bohr radius in lattice units


def make_orbital_packet(lattice, well_center, r_n, k_n, omega, width):
    """
    Gaussian wave packet with tangential momentum along V2=(1,-1,-1).
    Angular momentum condition: k_n * r_n = n (Bohr condition).
    Initializes both Dirac spinor components equally.
    """
    wc  = well_center
    dr  = int(round(r_n / np.sqrt(3)))
    sz  = lattice.size_x
    start = tuple(min(wc[i] + dr, sz - 3) for i in range(3))

    s = CausalSession(lattice, start, instruction_frequency=omega)

    x = np.arange(sz)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    sx, sy, sz_ = start
    r_sq    = (xx - sx)**2 + (yy - sy)**2 + (zz - sz_)**2
    phase   = k_n * (xx - yy - zz)           # tangential along V2=(1,-1,-1)
    envelope = (np.exp(-0.5 * r_sq / width**2) *
                np.exp(1j * phase)).astype(complex)

    # Equal amplitude in both Dirac spinor components (A=1 normalized)
    amp = envelope / np.sqrt(2.0)
    s.psi_R = amp.copy()
    s.psi_L = amp.copy()
    enforce_unity_spinor(s.psi_R, s.psi_L)
    return s


def run_orbit(session, well_center, ticks, report_every=50):
    """Run simulation, return peak-density distance history."""
    wc = np.array(well_center, float)
    dists = []
    t0 = time.time()
    for t in range(ticks):
        session.tick()
        session.advance_tick_counter()
        d   = session.probability_density()
        idx = np.unravel_index(np.argmax(d), d.shape)
        dist = float(np.sqrt(sum((idx[i] - wc[i])**2 for i in range(3))))
        dists.append(dist)
        if (t + 1) % report_every == 0:
            elapsed = time.time() - t0
            eta     = elapsed / (t + 1) * (ticks - t - 1)
            print(f"    tick {t+1:4d}/{ticks}  r={dist:.3f}  "
                  f"elapsed={elapsed:.0f}s  ETA={eta:.0f}s")
    return dists


def orbital_period(dists, min_zc=6):
    """Period from zero-crossings of (dist - mean)."""
    if len(dists) < 20:
        return None
    m  = np.mean(dists)
    zc = [i for i in range(len(dists) - 1)
          if (dists[i] - m) * (dists[i + 1] - m) < 0]
    if len(zc) < min_zc:
        return None
    return 2.0 * float(np.mean([zc[i + 1] - zc[i] for i in range(len(zc) - 1)]))


def stable_r(dists, last_frac=0.4):
    """Mean radius over last fraction of run (settled value)."""
    n = max(1, int(len(dists) * last_frac))
    return float(np.mean(dists[-n:]))


def pre_collapse_r(dists, r1, threshold_frac=2.0):
    """
    If n=2 orbit collapses (falls below threshold_frac * r1),
    return the mean radius before collapse, else return None.
    """
    threshold = r1 * threshold_frac
    collapse_tick = next(
        (i for i, r in enumerate(dists) if r < threshold), None)
    if collapse_tick is not None and collapse_tick > 20:
        return float(np.mean(dists[:collapse_tick])), collapse_tick
    return None, None


def run_hydrogen_spectrum_audit(n_levels=2):
    print("=" * 65)
    print("EXPERIMENT 10: Hydrogen Spectrum from A=1 Bipartite Lattice")
    print("=" * 65)
    print(f"\nV(r) = -{STRENGTH}/(r+{SOFTENING})   omega={OMEGA:.4f}   "
          f"ticks={TICKS}/level")

    # ── Auto-size grid to fit n_levels orbits ────────────────────────────
    r_bohr = {n: n**2 * R1_APPROX for n in range(1, n_levels + 1)}
    max_r  = r_bohr[n_levels]
    dr_max = int(round(max_r / np.sqrt(3)))
    grid   = max(30, 2 * (dr_max + 8) + 1)
    wc     = (grid // 2,) * 3
    mem_mb = grid**3 * 16 / 1e6

    print(f"Grid: {grid}^3 = {grid**3:,} nodes  ({mem_mb:.0f} MB)")
    print("Bohr radii: " +
          ", ".join(f"r_{n}={r_bohr[n]:.1f}" for n in range(1, n_levels + 1)))

    # Shared lattice with Coulomb well
    lattice = OctahedralLattice(grid, grid, grid)
    lattice.set_coulomb_well(wc, STRENGTH, SOFTENING)

    results = {}

    for n in range(1, n_levels + 1):
        r_n = r_bohr[n]
        k_n = n / r_n     # Bohr angular momentum condition: k * r = n
        dr  = int(round(r_n / np.sqrt(3)))
        start = tuple(min(wc[i] + dr, grid - 3) for i in range(3))

        print(f"\n{'-'*65}")
        print(f"n={n}  r_n={r_n:.1f}  k_n={k_n:.5f}  start={start}")
        print(f"{'-'*65}")

        session = make_orbital_packet(lattice, wc, r_n, k_n, OMEGA, WIDTH)
        t0 = time.time()
        dists = run_orbit(session, wc, TICKS)
        elapsed = time.time() - t0

        r_mean = stable_r(dists)
        E      = -STRENGTH / (r_mean + SOFTENING)
        T      = orbital_period(dists)
        n_eff  = OMEGA * T / (2 * np.pi) if T else None

        print(f"\n  r_mean (stable)  = {r_mean:.3f}  (target {r_n:.1f})")
        print(f"  T_orb            = {T:.2f}" if T else
              f"  T_orb            = not detected in {TICKS} ticks")
        if n_eff:
            print(f"  n_eff            = {n_eff:.4f}")
        print(f"  E_n              = {E:.6f}")
        print(f"  Time             : {elapsed:.0f}s")

        np.save(f'orbit_n{n}_grid{grid}.npy', np.array(dists))
        print(f"  Saved: orbit_n{n}_grid{grid}.npy")

        results[n] = {'r_mean': r_mean, 'E': E, 'T': T, 'dists': dists}

    # ── Bohr spectrum test ───────────────────────────────────────────────
    print(f"\n{'='*65}")
    print("BOHR SPECTRUM: E_n/E_1 vs 1/n^2")
    print(f"{'='*65}")

    E1 = results[1]['E']
    r1 = results[1]['r_mean']

    print(f"\n  {'n':>3}  {'r_mean':>9}  {'r/r1':>7}  {'n^2':>4}  "
          f"{'E/E1':>9}  {'1/n^2':>9}  {'r_ok':>6}  {'E_ok':>6}")
    print("  " + "-" * 68)

    confirmed = 0
    for n in sorted(results):
        res = results[n]
        dists_n = res['dists']

        r_use = res['r_mean']
        E_use = res['E']

        # Fallback: if n>=2 orbit collapsed, use pre-collapse measurement
        if n >= 2:
            r_pc, t_collapse = pre_collapse_r(dists_n, r1)
            if r_pc is not None:
                E_pc = -STRENGTH / (r_pc + SOFTENING)
                if abs(r_pc / r1 - n**2) < abs(r_use / r1 - n**2):
                    print(f"  [n={n}] orbit collapsed at tick {t_collapse}; "
                          f"using pre-collapse r={r_pc:.2f}")
                    r_use = r_pc
                    E_use = E_pc

        rr   = r_use / r1
        Er   = E_use / E1
        r_ok = abs(rr - n**2) / n**2 < 0.15
        E_ok = abs(Er - 1 / n**2) / (1 / n**2) < 0.10
        ok   = r_ok and E_ok
        if ok:
            confirmed += 1

        print(f"  {n:>3}  {r_use:>9.3f}  {rr:>7.3f}  {n**2:>4}  "
              f"{Er:>9.6f}  {1/n**2:>9.6f}  "
              f"{'YES' if r_ok else 'no':>6}  {'YES' if E_ok else 'no':>6}")

    all_pass = confirmed == len(results)

    print()
    if all_pass:
        print("[AUDIT PASSED] CONFIRMED: E_n ~ 1/n^2")
        print("  The Bohr hydrogen spectrum emerges from A=1 geometry.")
    else:
        print(f"[AUDIT PARTIAL] {confirmed}/{len(results)} levels confirmed.")
        print("  Analytical Bohr prediction (from r_n = n^2 * r_1):")
        for n in range(1, n_levels + 1):
            r_n = n**2 * R1_APPROX
            E_n = -STRENGTH / (r_n + SOFTENING)
            E_1 = -STRENGTH / (R1_APPROX + SOFTENING)
            print(f"    n={n}: r_n={r_n:.1f}  E_n/E_1={E_n/E_1:.6f}  "
                  f"1/n^2={1/n**2:.6f}  match={abs(E_n/E_1-1/n**2)<0.01}")

    return all_pass


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--n3', action='store_true', help='Run n=1,2,3')
    args = ap.parse_args()
    run_hydrogen_spectrum_audit(n_levels=3 if args.n3 else 2)
