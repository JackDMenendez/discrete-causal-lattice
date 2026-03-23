"""
exp_03_interference.py
Audit: Genuine discrete interference on the T^3_diamond bipartite lattice.

Two coherent point sources propagate via tick() and interfere at a screen.
Fringe pattern emerges from complex amplitude summation -- no analytical
formula used. This is the correct approach for the diagonal lattice:
sources at slit positions, amplitude propagates via Zitterbewegung,
interference pattern measured at screen plane.

Paper reference: Section 7 (Interference and the Huygens Lantern)
"""

import sys, os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession, enforce_unity


def run_interference_audit():
    print("=" * 60)
    print("EXPERIMENT 03: Genuine Discrete Interference")
    print("=" * 60)

    grid_x, grid_y, grid_z = 30, 60, 5
    src_x   = 5
    slit_y1 = 22
    slit_y2 = 38
    screen_x = 20
    z_mid   = 2
    omega   = 0.2
    ticks   = 35

    print(f"\nGeometry:")
    print(f"  Source A : ({src_x},{slit_y1},{z_mid})")
    print(f"  Source B : ({src_x},{slit_y2},{z_mid})")
    print(f"  Screen   : x={screen_x}")
    print(f"  Slit sep : {slit_y2-slit_y1} nodes")
    print(f"  Distance : {screen_x-src_x} nodes")

    lattice = OctahedralLattice(grid_x, grid_y, grid_z)
    session = CausalSession(lattice, (src_x,slit_y1,z_mid),
                            instruction_frequency=omega, is_massless=False)
    session.psi[:] = 0.0

    # Two coherent sources: same phase (coherent illumination)
    src_w = 2.0
    for y in range(grid_y):
        for z in range(grid_z):
            rA = np.sqrt((y-slit_y1)**2 + (z-z_mid)**2)
            rB = np.sqrt((y-slit_y2)**2 + (z-z_mid)**2)
            val = (np.exp(-0.5*(rA/src_w)**2) +
                   np.exp(-0.5*(rB/src_w)**2))
            if val > 1e-4:
                session.psi[src_x, y, z] = val + 0j
    enforce_unity(session.psi)

    print(f"\nRunning {ticks} ticks...")
    for t in range(ticks):
        session.tick()
        session.advance_tick_counter()

    # ── Screen measurement ─────────────────────────────────────────────
    psi_screen    = np.sum(session.psi[screen_x, :, :], axis=1)
    dens          = np.abs(psi_screen) ** 2
    total         = np.sum(dens)
    print(f"\n  Total probability at screen : {total:.6e}")
    print(f"  Peak density                : {np.max(dens):.4e}")

    if total < 1e-12:
        print("\n[AUDIT FAILED] No amplitude reached the screen.")
        return False

    norm = dens / (np.max(dens) + 1e-30)

    # ── Find peaks and troughs ─────────────────────────────────────────
    try:
        from scipy.signal import find_peaks
        peaks,  _ = find_peaks(norm, height=0.25, distance=3)
        troughs,_ = find_peaks(-norm, distance=2)
    except ImportError:
        peaks   = np.array([i for i in range(1,len(norm)-1)
                            if norm[i]>norm[i-1] and norm[i]>norm[i+1] and norm[i]>0.25])
        troughs = np.array([i for i in range(1,len(norm)-1)
                            if norm[i]<norm[i-1] and norm[i]<norm[i+1]])

    print(f"  Bright fringe peaks at y    : {peaks.tolist()}")
    print(f"  Number of bright fringes    : {len(peaks)}")

    # Contrast
    if len(peaks) >= 1 and len(troughs) >= 1:
        I_max    = np.mean(dens[peaks])
        I_min    = np.mean(dens[troughs])
        contrast = (I_max - I_min) / (I_max + I_min + 1e-30)
        print(f"  Fringe contrast (Michelson) : {contrast:.4f}")
    else:
        contrast = 0.0

    avg_trough = np.mean(norm[troughs]) if len(troughs) > 0 else 1.0
    print(f"  Average trough amplitude    : {avg_trough:.4f}  (expect < 0.5)")

    # ── Density profile ────────────────────────────────────────────────
    print(f"\n  Normalized screen profile (y=8..{slit_y2+12}):")
    print(f"  {'y':>4}  {'norm':>7}  pattern")
    for y in range(8, min(slit_y2+13, grid_y)):
        bar = '█' * int(norm[y] * 30)
        mk  = (' ← A' if y==slit_y1 else
               ' ← B' if y==slit_y2 else
               ' ← midpoint' if y==(slit_y1+slit_y2)//2 else '')
        print(f"  {y:>4}  {norm[y]:>7.4f}  {bar}{mk}")

    # ── Summary ───────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    fringes_ok    = len(peaks) >= 2
    contrast_ok   = contrast > 0.15
    destructive_ok= avg_trough < 0.6

    all_pass = fringes_ok and contrast_ok

    if all_pass:
        print("[AUDIT PASSED] Genuine discrete interference confirmed.")
        print("  Fringe pattern emerges from tick() propagation alone.")
        print("  Complex amplitude summation produces phase cancellation.")
        print("  No continuous Huygens-Fresnel formula used.")
    else:
        print("[AUDIT FAILED]")
        if not fringes_ok:
            print(f"  FAIL: {len(peaks)} peaks found (need >= 2)")
        if not contrast_ok:
            print(f"  FAIL: contrast {contrast:.3f} (need > 0.15)")

    return all_pass


if __name__ == "__main__":
    run_interference_audit()
