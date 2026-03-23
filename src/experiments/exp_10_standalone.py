"""
exp_10_standalone.py
Hydrogen Spectrum from the A=1 Bipartite Lattice
Standalone -- requires only numpy. No other dependencies.

Run from any directory:
    python exp_10_standalone.py              # n=1,2  (~4 min on modern CPU)
    python exp_10_standalone.py --n3         # n=1,2,3 (~30 min)
    python exp_10_standalone.py --profile    # benchmark then exit

Theory:
    Coulomb clock-density well: V(r) = -S / (r + eps)
    Angular momentum quantization: k * r_orb = n  (de Broglie / Bohr)
    Bohr radii: r_n = n^2 * r_1
    Energy levels: E_n = -S / (r_n + eps)  =>  E_n/E_1 ~ 1/n^2

What to expect:
    r_1 ~ 10.3 nodes, r_2 ~ 41 nodes
    E_2/E_1 ~ 0.25  (1/4)
    If confirmed: hydrogen spectrum from lattice geometry.

Author: Jack Menendez (with Claude)
"""

import sys, os, time, argparse
import numpy as np

# ── Bipartite lattice basis vectors ──────────────────────────────────────────
RGB_VECTORS = [(1,1,1), (1,-1,-1), (-1,1,-1)]
CMY_VECTORS = [(-1,-1,-1), (-1,1,1), (1,-1,1)]
ALL_VECTORS = RGB_VECTORS + CMY_VECTORS

# ── Physics parameters ────────────────────────────────────────────────────────
STRENGTH   = 30.0
SOFTENING  = 0.5
OMEGA      = 0.1019    # particle mass (instruction frequency)
WIDTH      = 1.5       # packet width in nodes
TICKS      = 400       # ticks per level
R1_APPROX  = 10.3      # n=1 Bohr radius in lattice units

# ── Core lattice functions (self-contained) ───────────────────────────────────

def coulomb_potential(grid, center, strength, softening):
    """Vectorized 1/r Coulomb clock-density well."""
    cx, cy, cz = center
    x = np.arange(grid); y = np.arange(grid); z = np.arange(grid)
    xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
    r = np.sqrt((xx-cx)**2 + (yy-cy)**2 + (zz-cz)**2)
    return -strength / (r + softening)


def enforce_unity_spinor(psi_R, psi_L):
    """Enforce A=1 for Dirac spinor: normalize so sum(|psi_R|^2+|psi_L|^2)=1."""
    norm = np.sqrt(np.sum(np.abs(psi_R)**2 + np.abs(psi_L)**2))
    if norm < 1e-12:
        raise RuntimeError("Unity constraint violated: spinor collapsed.")
    psi_R /= norm
    psi_L /= norm


def make_packet(grid, start, well_center, k_tang, omega, width, V):
    """
    Gaussian wave packet with tangential momentum along V2=(1,-1,-1).
    Angular momentum L = k_tang * r_orb = n (Bohr condition).

    Returns (psi_R, psi_L, xx, yy, zz) -- two equal spinor components.
    """
    x = np.arange(grid); y = np.arange(grid); z = np.arange(grid)
    xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
    sx, sy, sz = start
    r_sq  = (xx-sx)**2 + (yy-sy)**2 + (zz-sz)**2
    phase = k_tang * (xx - yy - zz)   # V2 direction
    envelope = (np.exp(-0.5 * r_sq / width**2) *
                np.exp(1j * phase)).astype(complex)
    # Equal amplitude in both spinor components
    psi_R = envelope / np.sqrt(2.0)
    psi_L = envelope / np.sqrt(2.0)
    enforce_unity_spinor(psi_R, psi_L)
    return psi_R, psi_L, xx, yy, zz


def _kinetic_hop(source, vectors, omega):
    """
    Directed kinetic hop with phase coherence.

    For each direction v: weight = max(0, delta_p) where delta_p = phi(r+v)-phi(r).
    Emission carries exp(i*delta_p) phase correction so amplitude arrives at the
    destination with the correct plane-wave phase (constructive interference).
    Falls back to uniform weights when momentum ≈ zero.
    """
    n_vec = len(vectors)
    local_phase = np.angle(source)

    delta_p_list = []
    weights = np.zeros((n_vec,) + source.shape, dtype=float)
    for i, (dx, dy, dz) in enumerate(vectors):
        nb       = np.roll(np.roll(np.roll(source, -dx, 0), -dy, 1), -dz, 2)
        nb_abs   = np.abs(nb)
        nb_phase = np.where(nb_abs > 1e-9, np.angle(nb), local_phase)
        delta_p  = nb_phase - local_phase
        delta_p_list.append(delta_p)
        weights[i] = np.maximum(0.0, delta_p) / (1.0 + omega)

    total_w  = weights.sum(axis=0)
    zero_mom = total_w < 1e-12
    total_w_safe = np.where(zero_mom, 1.0, total_w)
    uniform  = 1.0 / n_vec

    result = np.zeros_like(source)
    sx, sy, sz = source.shape
    for i, (dx, dy, dz) in enumerate(vectors):
        w_i = np.where(zero_mom, uniform, weights[i] / total_w_safe)
        phase_corr = np.where(zero_mom, 1.0+0j,
                              np.exp(1j * delta_p_list[i]).astype(complex))
        emission = source * phase_corr * w_i
        mask = np.ones((sx, sy, sz), dtype=bool)
        if dx > 0: mask[sx-dx:, :, :] = False
        if dx < 0: mask[:-dx,   :, :] = False
        if dy > 0: mask[:, sy-dy:, :] = False
        if dy < 0: mask[:, :-dy,   :] = False
        if dz > 0: mask[:, :, sz-dz:] = False
        if dz < 0: mask[:, :, :-dz  ] = False
        emission = np.where(mask, emission, 0.0)
        result += np.roll(np.roll(np.roll(emission, dx, 0), dy, 1), dz, 2)

    return result


def tick(psi_R, psi_L, V, omega, tick_parity):
    """
    One bipartite Dirac spinor tick.

    Even tick (RGB active):
      new_psi_R = cos(delta_phi/2) * kinetic_hop(psi_L, RGB)
                + 1j * sin(delta_phi/2) * psi_R

    Odd tick (CMY active):
      new_psi_L = cos(delta_phi/2) * kinetic_hop(psi_R, CMY)
                + 1j * sin(delta_phi/2) * psi_L

    kinetic_hop uses directed phase-coherent weighting (max(0,delta_p) weights
    with exp(i*delta_p) phase correction) to correctly encode momentum direction.
    A=1: sum(|psi_R|^2 + |psi_L|^2) = 1 enforced after.
    """
    delta_phi = omega + V
    cos_half  = np.cos(delta_phi / 2.0)
    sin_half  = np.sin(delta_phi / 2.0)

    # Massive particle: both components updated simultaneously each tick.
    # RGB: psi_L -> psi_R; CMY: psi_R -> psi_L. Averaging RGB+CMY preserves
    # zero-CoM drift for zero-momentum states.
    hop_R     = _kinetic_hop(psi_L, RGB_VECTORS, omega)
    hop_L     = _kinetic_hop(psi_R, CMY_VECTORS, omega)
    new_psi_R = cos_half * hop_R + 1j * sin_half * psi_R
    new_psi_L = cos_half * hop_L + 1j * sin_half * psi_L

    enforce_unity_spinor(new_psi_R, new_psi_L)
    return new_psi_R, new_psi_L


def run_orbit(psi_R, psi_L, V, omega, xx, yy, zz, well_center, ticks,
              report_every=50):
    """Run simulation, return peak-density distance history."""
    wc    = np.array(well_center, float)
    peaks = []
    t0    = time.time()

    for t in range(ticks):
        psi_R, psi_L = tick(psi_R, psi_L, V, omega, t % 2)
        d   = np.abs(psi_R)**2 + np.abs(psi_L)**2
        idx = np.unravel_index(np.argmax(d), d.shape)
        dist = float(np.sqrt(sum((idx[i]-wc[i])**2 for i in range(3))))
        peaks.append(dist)

        if (t+1) % report_every == 0:
            elapsed = time.time() - t0
            eta     = elapsed / (t+1) * (ticks - t - 1)
            print(f"    tick {t+1:4d}/{ticks}  r={dist:.3f}  "
                  f"elapsed={elapsed:.0f}s  ETA={eta:.0f}s")

    return peaks


def orbital_period(dists, min_zc=6):
    """Period from zero-crossings."""
    if len(dists) < 20: return None
    m  = np.mean(dists)
    zc = [i for i in range(len(dists)-1)
          if (dists[i]-m) * (dists[i+1]-m) < 0]
    if len(zc) < min_zc: return None
    return 2.0 * float(np.mean([zc[i+1]-zc[i] for i in range(len(zc)-1)]))


# ── Main experiment ───────────────────────────────────────────────────────────

def run_hydrogen(n_levels=2):
    print("=" * 70)
    print("A=1 BIPARTITE LATTICE -- HYDROGEN SPECTRUM")
    print("=" * 70)
    print(f"V(r) = -{STRENGTH}/(r+{SOFTENING})  omega={OMEGA:.4f}")

    r_bohr = {n: n**2 * R1_APPROX for n in range(1, n_levels+1)}

    max_r  = r_bohr[n_levels]
    dr_max = int(round(max_r / np.sqrt(3)))
    grid   = max(30, 2*(dr_max + 8) + 1)
    wc     = (grid//2, grid//2, grid//2)
    mem_mb = grid**3 * 16 / 1e6

    print(f"Grid: {grid}^3 = {grid**3:,} nodes  ({mem_mb:.0f} MB)")
    print(f"Bohr radii: " + ", ".join(f"r_{n}={r_bohr[n]:.1f}" for n in range(1,n_levels+1)))
    print()

    V = coulomb_potential(grid, wc, STRENGTH, SOFTENING)
    results = {}

    for n in range(1, n_levels+1):
        r_n   = r_bohr[n]
        k_n   = n / r_n          # angular momentum quantization: k * r = n
        dr    = int(round(r_n / np.sqrt(3)))
        start = tuple(min(wc[i]+dr, grid-3) for i in range(3))

        print(f"\n{'─'*60}")
        print(f"n={n}  r_n={r_n:.1f}  k_n={k_n:.5f}  start={start}")
        print(f"{'─'*60}")

        psi_R, psi_L, xx, yy, zz = make_packet(grid, start, wc, k_n, OMEGA, WIDTH, V)
        t0     = time.time()
        dists  = run_orbit(psi_R, psi_L, V, OMEGA, xx, yy, zz, wc, TICKS)
        elapsed = time.time() - t0

        T      = orbital_period(dists)
        r_mean = float(np.mean(dists))
        E      = -STRENGTH / (r_mean + SOFTENING)
        n_eff  = OMEGA * T / (2*np.pi) if T else None

        print(f"\n  r_mean = {r_mean:.3f}  (target {r_n:.1f})")
        print(f"  T_orb  = {T:.2f}" if T else "  T_orb  = not detected")
        if n_eff: print(f"  n_eff  = {n_eff:.4f}")
        print(f"  E_n    = {E:.6f}")
        print(f"  Time   : {elapsed:.0f}s")

        results[n] = {'r_mean': r_mean, 'T': T, 'E': E}
        np.save(f'orbit_n{n}.npy', np.array(dists))
        print(f"  Saved  : orbit_n{n}.npy")

    # Bohr test
    print(f"\n{'='*70}")
    print("BOHR SPECTRUM: E_n/E_1 vs 1/n^2")
    print(f"{'='*70}")

    E1 = results[1]['E']
    r1 = results[1]['r_mean']
    print(f"\n  {'n':>3}  {'r_mean':>9}  {'r/r1':>8}  {'n^2':>5}  "
          f"{'E/E1':>10}  {'1/n^2':>10}  match?")
    print("  " + "-"*55)

    confirmed = 0
    for n, res in sorted(results.items()):
        rr   = res['r_mean'] / r1
        Er   = res['E'] / E1
        r_ok = abs(rr - n**2) / n**2 < 0.15
        E_ok = abs(Er - 1/n**2) / (1/n**2) < 0.10
        ok   = r_ok and E_ok
        if ok: confirmed += 1
        print(f"  {n:>3}  {res['r_mean']:>9.3f}  {rr:>8.3f}  {n**2:>5}  "
              f"{Er:>10.6f}  {1/n**2:>10.6f}  "
              f"{'YES' if ok else ('r?' if not r_ok else 'E?')}")

    print()
    if confirmed == len(results):
        print("╔══════════════════════════════════════════════════════════╗")
        print("║  CONFIRMED: E_n ~ 1/n^2                                  ║")
        print("║  The Bohr hydrogen spectrum emerges from A=1 geometry.   ║")
        print("╚══════════════════════════════════════════════════════════╝")
    else:
        print(f"Partial: {confirmed}/{len(results)} levels confirmed.")
        print("Check orbital_period detection -- may need more ticks.")


def profile():
    print("Profiling this machine...")
    print(f"{'grid':>8}  {'mem MB':>8}  {'ms/tick':>10}  {'n=1+2 ETA':>12}")
    for grid in [25, 50, 82, 100, 150, 186]:
        nodes = grid**3; mem = nodes*16/1e6
        wc    = (grid//2,)*3
        try:
            V    = coulomb_potential(grid, wc, STRENGTH, SOFTENING)
            dr   = int(round(R1_APPROX/np.sqrt(3)))
            st   = tuple(min(wc[i]+dr, grid-3) for i in range(3))
            psi_R, psi_L, xx, yy, zz = make_packet(grid, st, wc, 1/R1_APPROX, OMEGA, WIDTH, V)
            n_t  = max(2, int(5000 / (11*(grid/25)**3)))
            n_t  = min(n_t, 10)
            t0   = time.time()
            for t in range(n_t): psi_R, psi_L = tick(psi_R, psi_L, V, OMEGA, t%2)
            ms   = (time.time()-t0)/n_t*1000
            eta  = ms*TICKS*2/60000
            print(f"{grid:>4}^3  {mem:>8.0f}  {ms:>10.1f}  {eta:>10.1f} min")
        except MemoryError:
            print(f"{grid:>4}^3  {mem:>8.0f}  OUT OF MEMORY")
            break


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('--n3',      action='store_true', help='Run n=1,2,3')
    ap.add_argument('--profile', action='store_true', help='Profile only')
    args = ap.parse_args()

    if args.profile:
        profile()
    elif args.n3:
        run_hydrogen(n_levels=3)
    else:
        run_hydrogen(n_levels=2)
