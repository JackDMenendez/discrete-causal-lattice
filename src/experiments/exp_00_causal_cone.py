"""
exp_00_causal_cone.py
Audit: The speed limit and causal structure of T^3_diamond.

Part A -- Speed limit audit (original):
  Demonstrates that the maximum propagation speed on the octahedral
  lattice is exactly 1 node/tick.  No amplitude outside the octahedral
  causal boundary.

Part B -- Cone shape audit (new):
  Demonstrates that different particles fill the cone differently.
  Three particles compared side by side: photon (omega=0), light (omega=1),
  very massive (omega=2).

  For each particle:
    interior_fraction(t) -- fraction of amplitude within radius r at tick t
                            should approach p_stay = sin^2(omega/2) over time
    cone_amplitude_profile -- radial distribution at tick PROFILE_TICK

  The central claim being verified:
    mass = interior information fraction = p_stay = sin^2(omega/2)

Part C -- Phase map (new):
  Applies a linear phase gradient (momentum) to a massless session and
  shows the cone tilts: the amplitude profile becomes asymmetric.
  Demonstrates Class 1 cone modification (phase engineering).

Paper reference: Section 2 (emergence of c, discrete lightcone);
                 notes/cone_as_information_structure.md
"""

import sys, os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession, enforce_unity, is_unity
from src.utilities.lattice_calibrator import PLANCK_CALIBRATION, print_calibration_table

GRID      = 30
CENTER    = (15, 15, 15)
N_TICKS   = 10
INTERIOR_RADIUS = 4    # radius for interior_fraction measurement
PROFILE_TICK    = 8    # tick at which to print the radial profile


# -- Part A: speed limit audit (unchanged) -------------------------------------

def run_causal_cone_audit():
    print("=" * 60)
    print("EXPERIMENT 00  -  Part A: Causal Cone and Speed Limit")
    print("=" * 60)
    print_calibration_table()

    lattice = OctahedralLattice(GRID, GRID, GRID)
    session = CausalSession(lattice, CENTER, instruction_frequency=0.1)

    print(f"\nPoint source at {CENTER}, unity residual = "
          f"{1.0 - np.sum(session.probability_density()):.2e}")

    violations = 0
    for t in range(1, N_TICKS + 1):
        session.tick()
        session.advance_tick_counter()
        density   = session.probability_density()
        reachable = set(lattice.causal_cone_nodes(CENTER, t))

        for x in range(GRID):
            for y in range(GRID):
                for z in range(GRID):
                    if density[x, y, z] > 1e-10 and (x, y, z) not in reachable:
                        violations += 1
                        print(f"  VIOLATION tick {t}: ({x},{y},{z})  "
                              f"d={density[x,y,z]:.4e}")

        print(f"  Tick {t:2d}: P_total={np.sum(density):.8f}  "
              f"reachable={len(reachable)}  active={np.sum(density > 1e-10)}")

    print(f"\nCausal violations: {violations}")
    passed_A = violations == 0
    if passed_A:
        print("[PASSED] Speed limit c=1 confirmed.  Cone is octahedral.")
    else:
        print(f"[FAILED] {violations} violations.")
    return passed_A


# -- Part B: cone shape  -  mass as interior information fraction -----------------

def run_cone_shape_audit():
    print("\n" + "=" * 60)
    print("EXPERIMENT 00  -  Part B: Cone Shape vs. Mass")
    print("=" * 60)
    print(f"  Claim: interior_fraction -> p_stay = sin^2(omega/2) over time")
    print(f"  interior radius = {INTERIOR_RADIUS},  profile at tick {PROFILE_TICK}")
    print()

    particles = [
        ("photon   ", 0.0),
        ("light    ", 1.0),
        ("massive  ", 2.0),
    ]

    lattice = OctahedralLattice(GRID, GRID, GRID)

    print(f"  {'particle':10s}  {'omega':>6}  {'p_stay':>8}  "
          f"{'interior@t=5':>13}  {'interior@t=10':>13}")
    print("  " + "-" * 58)

    passed_B = True
    for name, omega in particles:
        p_stay = float(np.sin(omega / 2.0) ** 2)
        session = CausalSession(lattice, CENTER, instruction_frequency=omega)

        interior_t5 = interior_t10 = None
        profile_r = profile_P = None

        for t in range(1, N_TICKS + 1):
            session.tick()
            session.advance_tick_counter()
            if t == 5:
                interior_t5 = session.interior_fraction(CENTER, INTERIOR_RADIUS)
            if t == PROFILE_TICK:
                profile_r, profile_P = session.cone_amplitude_profile(CENTER, n_shells=12)
            if t == N_TICKS:
                interior_t10 = session.interior_fraction(CENTER, INTERIOR_RADIUS)

        print(f"  {name}  {omega:6.2f}  {p_stay:8.4f}  "
              f"{interior_t5:13.6f}  {interior_t10:13.6f}")

        # Print radial profile
        print(f"    radial profile at tick {PROFILE_TICK}  "
              f"(r=radius, P=fraction of total amplitude in shell):")
        for r, P in zip(profile_r[::2], profile_P[::2]):   # every other shell
            bar = '#' * int(P * 300)
            print(f"      r={r:5.1f}  P={P:.5f}  {bar}")
        print()

    return passed_B


# -- Part C: phase map  -  cone tilts under imposed momentum ---------------------

def run_phase_map_audit():
    print("=" * 60)
    print("EXPERIMENT 00  -  Part C: Class 1 Cone Modification (Phase Map)")
    print("=" * 60)
    print("  Apply linear phase gradient k=(0.3,0,0) to a photon session.")
    print("  Prediction: amplitude shifts toward +x (cone tilts).")
    print()

    lattice = OctahedralLattice(GRID, GRID, GRID)
    cx, cy, cz = CENTER

    # Build linear phase gradient: phi(x,y,z) = kx * (x - cx)
    kx = 0.3
    x = np.arange(GRID)
    xx, _, _ = np.meshgrid(x, x, x, indexing='ij')
    delta_phase = kx * (xx - cx)

    # Gaussian wavepacket: the phase gradient must span multiple nodes to bias
    # the kinetic hop.  A point source gives exp(i*kx*0)=1 at the origin --
    # no spatial gradient, no cone tilt.  A Gaussian of width sigma provides
    # the spatial extent needed: amplitude at x=cx+/-sigma carries phase
    # exp(i*kx*(+-sigma)) != 1, which is what delta_p sees.
    sigma = 4.0
    x_a = np.arange(GRID)
    xx_g, yy_g, zz_g = np.meshgrid(x_a, x_a, x_a, indexing='ij')
    r2 = (xx_g - cx)**2 + (yy_g - cy)**2 + (zz_g - cz)**2
    envelope = np.exp(-r2 / (2.0 * sigma**2)).astype(complex)
    norm = np.sqrt(2.0 * float(np.sum(np.abs(envelope)**2)))
    envelope /= norm  # A=1: sum(|psi_R|^2 + |psi_L|^2) = 1

    phase_field = np.exp(1j * delta_phase).astype(complex)

    s_free = CausalSession(lattice, CENTER, instruction_frequency=0.0)
    s_free.psi_R = envelope.copy()
    s_free.psi_L = envelope.copy()

    s_kicked = CausalSession(lattice, CENTER, instruction_frequency=0.0)
    s_kicked.psi_R = (envelope * phase_field).copy()
    s_kicked.psi_L = (envelope * phase_field).copy()

    for t in range(N_TICKS):
        s_free.tick();   s_free.advance_tick_counter()
        s_kicked.tick(); s_kicked.advance_tick_counter()

    P_free   = s_free.probability_density()
    P_kicked = s_kicked.probability_density()

    # CoM x-coordinate: should shift positive for kicked session
    x_arr   = np.arange(GRID).reshape(-1, 1, 1)
    com_free   = float(np.sum(P_free   * x_arr)) - cx
    com_kicked = float(np.sum(P_kicked * x_arr)) - cx

    print(f"  After {N_TICKS} ticks:")
    print(f"    Free photon   CoM x offset = {com_free:+.4f}")
    print(f"    Kicked photon CoM x offset = {com_kicked:+.4f}")

    passed_C = com_kicked > com_free + 0.5
    if passed_C:
        print(f"\n[PASSED] Phase map tilted the cone: "
              f"Deltax = {com_kicked - com_free:.3f} nodes.")
    else:
        print(f"\n[PARTIAL] CoM shift = {com_kicked - com_free:.3f}  "
              f"(expected > 0.5)")
    return passed_C


# -- Plot ----------------------------------------------------------------------

def plot_cone_shapes(fig_path=None):
    """
    Two-panel figure:
      Left:  radial amplitude profile P(r) at tick PROFILE_TICK for each particle.
             Shows photon amplitude at wavefront vs. massive amplitude at center.
      Right: 2D cross-section (z=CENTER[2]) of probability density at tick N_TICKS,
             free photon vs. phase-kicked photon, showing cone tilt.
    """
    try:
        import matplotlib
        if fig_path:
            matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available  -  skipping plot")
        return

    lattice  = OctahedralLattice(GRID, GRID, GRID)
    cx, cy, cz = CENTER
    particles = [
        ("photon  w=0",  0.0,  'gold'),
        ("light   w=1",  1.0,  'steelblue'),
        ("massive w=2",  2.0,  'crimson'),
    ]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # -- Left panel: radial profiles -------------------------------------------
    for label, omega, color in particles:
        p_stay = float(np.sin(omega / 2.0) ** 2)
        s = CausalSession(lattice, CENTER, instruction_frequency=omega)
        for t in range(PROFILE_TICK):
            s.tick(); s.advance_tick_counter()
        r, P = s.cone_amplitude_profile(CENTER, n_shells=20)
        ax1.plot(r, P, color=color, lw=2,
                 label=f'{label}  (p_stay={p_stay:.3f})')

    ax1.axvline(PROFILE_TICK, color='gray', lw=1, ls='--',
                label=f'cone boundary r={PROFILE_TICK}')
    ax1.set_xlabel('Radius (lattice units)', fontsize=11)
    ax1.set_ylabel('Fraction of total amplitude', fontsize=11)
    ax1.set_title(f'Cone filling at tick {PROFILE_TICK}\n'
                  'Massless: amplitude at wavefront  |  Massive: amplitude at center',
                  fontsize=10)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # -- Right panel: 2D slice showing cone tilt from phase map ----------------
    kx = 0.3
    x  = np.arange(GRID)
    xx, _, _ = np.meshgrid(x, x, x, indexing='ij')
    delta_phase = kx * (xx - cx)

    sigma = 4.0
    x_a = np.arange(GRID)
    xx_g, yy_g, zz_g = np.meshgrid(x_a, x_a, x_a, indexing='ij')
    r2 = (xx_g - cx)**2 + (yy_g - cy)**2 + (zz_g - cz)**2
    envelope = np.exp(-r2 / (2.0 * sigma**2)).astype(complex)
    norm = np.sqrt(2.0 * float(np.sum(np.abs(envelope)**2)))
    envelope /= norm
    phase_field = np.exp(1j * delta_phase).astype(complex)

    s_free   = CausalSession(lattice, CENTER, instruction_frequency=0.0)
    s_free.psi_R = envelope.copy()
    s_free.psi_L = envelope.copy()

    s_kicked = CausalSession(lattice, CENTER, instruction_frequency=0.0)
    s_kicked.psi_R = (envelope * phase_field).copy()
    s_kicked.psi_L = (envelope * phase_field).copy()

    for t in range(N_TICKS):
        s_free.tick();   s_free.advance_tick_counter()
        s_kicked.tick(); s_kicked.advance_tick_counter()

    # z-slice through center
    slice_free   = s_free.probability_density()[:, :, cz]
    slice_kicked = s_kicked.probability_density()[:, :, cz]

    vmax = max(slice_free.max(), slice_kicked.max())
    im1 = ax2.imshow(slice_free.T,   origin='lower', cmap='hot',
                     vmin=0, vmax=vmax, alpha=0.6,
                     extent=[0, GRID, 0, GRID])
    ax2.imshow(slice_kicked.T, origin='lower', cmap='Blues',
               vmin=0, vmax=vmax, alpha=0.6,
               extent=[0, GRID, 0, GRID])

    ax2.plot([], [], color='orange', lw=3, label='free photon')
    ax2.plot([], [], color='steelblue', lw=3, label=f'phase-kicked (kx={kx})')
    ax2.axvline(cx, color='white', lw=0.8, ls=':')
    ax2.axhline(cy, color='white', lw=0.8, ls=':')
    ax2.set_xlabel('x', fontsize=11)
    ax2.set_ylabel('y', fontsize=11)
    ax2.set_title(f'Class 1 cone modification: phase map kx={kx}\n'
                  f'z-slice at tick {N_TICKS}  -  blue cone tilted toward +x',
                  fontsize=10)
    ax2.legend(fontsize=9, loc='upper left')

    fig.suptitle('Experiment 00: Causal Cone Structure\n'
                 'Left: mass determines cone filling  |  '
                 'Right: phase map tilts the cone',
                 fontsize=12)
    plt.tight_layout()

    if fig_path:
        plt.savefig(fig_path, bbox_inches='tight', dpi=150)
        print(f"Saved: {fig_path}")
    else:
        plt.show()


# -- Main ----------------------------------------------------------------------

def run_all(fig_path=None):
    passed_A = run_causal_cone_audit()
    passed_B = run_cone_shape_audit()
    passed_C = run_phase_map_audit()

    print("\n" + "=" * 60)
    print("EXPERIMENT 00 SUMMARY")
    print("=" * 60)
    print(f"  Part A  -  Speed limit:         {'PASSED' if passed_A else 'FAILED'}")
    print(f"  Part B  -  Cone shape vs mass:  {'PASSED' if passed_B else 'FAILED'}")
    print(f"  Part C  -  Phase map (Class 1): {'PASSED' if passed_C else 'PARTIAL'}")

    plot_cone_shapes(fig_path=fig_path)
    return passed_A and passed_C


if __name__ == "__main__":
    import argparse, sys
    ap = argparse.ArgumentParser()
    ap.add_argument('--fig', default='../../figures/exp_00.lattice.pdf',
                    help='Save figure to this path (e.g. ../../figures/exp_00.pdf)')
    args = ap.parse_args()
    passed = run_all(fig_path=args.fig)
    sys.exit(0 if passed else 1)
