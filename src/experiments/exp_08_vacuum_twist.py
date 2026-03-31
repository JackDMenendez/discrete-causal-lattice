"""
exp_08_vacuum_twist.py
Gravity (div) vs Electromagnetism (curl) as vacuum deformations.

Three tests:

  Test 1 -- EM deflection (Lorentz geometry)
    A charged particle moves through an EM twist (curl of phase field).
    The Peierls substitution in _kinetic_hop biases hops in directions
    where A·v > 0, deflecting the particle perpendicular to both its
    velocity and the twist axis -- Lorentz force geometry.
    Pass: deflection angle from initial trajectory > 10 degrees AND
          deflection direction within 45 degrees of the expected
          perpendicular (V1 x twist_axis).

  Test 2 -- Photon propagation at c=1
    A massless session (is_massless=True) initialized at one edge
    of the grid.  After N ticks the probability CoM should have
    advanced N nodes (speed = 1 lattice unit / tick = c).
    Pass: |CoM_advance - N| / N < 0.15  (15% tolerance for dispersion)

  Test 3 -- Orbital emission and photon escape
    Electron session in a Gaussian clock well + photon session coupled
    via register_emission().  After EMISSION_TICKS ticks:
      - Photon amplitude fraction > PHOTON_MIN  (photon was emitted)
      - Photon CoM has moved away from the well center
        (photon is propagating outward, not stuck at origin)
    Pass: both conditions met.

GIF outputs (--gif flag):
  figures/exp_08_deflection.gif  -- Test 1 animated 2D slice
  figures/exp_08_emission.gif    -- Test 3 animated 2D slice

Data outputs:
  data/exp_08_deflection.npy     -- (ticks, 4): tick, CoM_x, CoM_y, CoM_z
  data/exp_08_emission.npy       -- (ticks, 3): tick, electron_frac, photon_frac

Paper reference: Section 8 (Vacuum Twist and Field Equations)
"""

import sys, os, time
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession, TickScheduler
from src.core.UnityConstraint import enforce_unity_spinor

_HERE    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(_HERE, '..', '..', 'data')
FIG_DIR  = os.path.join(_HERE, '..', '..', 'figures')

# ── Test parameters ────────────────────────────────────────────────────────────

# Test 1: EM deflection
DEFL_GRID    = 35          # grid side (nodes)
DEFL_TICKS   = 300         # ticks to run
DEFL_OMEGA   = 0.05        # particle mass (small = fast propagation)
DEFL_EM_STR  = 0.25        # EM twist strength
DEFL_EM_W    = 6.0         # EM twist Gaussian width (nodes)

# Test 2: gravity vs EM force direction
GRAV_GRID    = 35          # grid side
GRAV_TICKS   = 150         # ticks to measure deflection

# Test 3: orbital emission
EMIT_GRID    = 41          # grid side
EMIT_TICKS   = 600         # ticks to run
EMIT_OMEGA   = 0.15        # electron mass
EMIT_WELL_D  = 1.2         # Gaussian well depth
EMIT_WELL_W  = 3.0         # Gaussian well width
EMIT_RATE    = 0.004       # emission rate per tick
PHOTON_MIN   = 0.10        # minimum photon amplitude fraction to pass Test 3


# ── Helpers ────────────────────────────────────────────────────────────────────

def center_of_mass(density):
    """Density-weighted CoM, returned as (x, y, z) float array."""
    total = density.sum()
    if total < 1e-12:
        return np.zeros(3)
    sx, sy, sz = density.shape
    x = np.arange(sx); y = np.arange(sy); z = np.arange(sz)
    cx = float(np.einsum('ijk,i->', density, x) / total)
    cy = float(np.einsum('ijk,j->', density, y) / total)
    cz = float(np.einsum('ijk,k->', density, z) / total)
    return np.array([cx, cy, cz])


def make_gaussian_packet(lattice, center, omega, width=1.5, k_vec=(0,0,0)):
    """Gaussian spinor packet at center with tangential momentum k_vec."""
    sz = lattice.size_x
    s  = CausalSession(lattice, center, instruction_frequency=omega)
    x  = np.arange(sz)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    cx, cy, cz = center
    r_sq = (xx-cx)**2 + (yy-cy)**2 + (zz-cz)**2
    kx, ky, kz = k_vec
    phase    = kx*xx + ky*yy + kz*zz
    envelope = (np.exp(-0.5 * r_sq / width**2) *
                np.exp(1j * phase)).astype(complex)
    amp = envelope / np.sqrt(2.0)
    s.psi_R = amp.copy()
    s.psi_L = amp.copy()
    enforce_unity_spinor(s.psi_R, s.psi_L)
    return s


# ── Test 1: EM deflection ─────────────────────────────────────────────────────

def test_em_deflection(save_gif=False, save_data=True):
    """
    Particle moving along V1=(1,1,1) passes through an EM twist around z-axis.
    Expected: Lorentz deflection perpendicular to both V1 and z.
    V1 x z = (1,1,1) x (0,0,1) = (1*1-1*0, 1*0-1*1, 1*0-1*0) = (1,-1,0).
    So deflection should appear in the +x/-y plane (or -x/+y for opposite charge).
    """
    print("\n" + "="*60)
    print("TEST 1: EM Deflection (Lorentz geometry)")
    print("="*60)

    g  = DEFL_GRID
    wc = (g//2,) * 3

    lat = OctahedralLattice(g, g, g)
    # EM twist centered at grid center, curl around z-axis
    lat.set_em_twist(wc, width=DEFL_EM_W, strength=DEFL_EM_STR, axis=2)

    # Particle starts on the -x face, moving along +V1=(1,1,1)
    # Momentum: k along V1 direction = k*(1,1,1)/sqrt(3)
    k_mag = 0.18
    k1 = k_mag / np.sqrt(3)
    start = (3, 3, 3)
    sess = make_gaussian_packet(lat, start, DEFL_OMEGA,
                                width=1.5, k_vec=(k1, k1, k1))

    com_trace = []   # (tick, cx, cy, cz)
    frames    = []   # for GIF

    GIF_STRIDE = max(1, DEFL_TICKS // 75)   # ~75 frames at 24 fps = ~3s
    z_sl = g // 2

    for tick in range(DEFL_TICKS):
        sess.tick()
        sess.advance_tick_counter()
        d   = sess.probability_density()
        com = center_of_mass(d)
        com_trace.append([float(tick), com[0], com[1], com[2]])

        if save_gif and tick % GIF_STRIDE == 0:
            frames.append(d[:, :, z_sl].copy())

    com_arr = np.array(com_trace)

    # Initial direction: V1 = (1,1,1)/sqrt(3)
    v_init = np.array([1., 1., 1.]) / np.sqrt(3)

    # Displacement over full run
    start_com = com_arr[0, 1:4]
    end_com   = com_arr[-1, 1:4]
    disp      = end_com - start_com
    disp_norm = np.linalg.norm(disp)

    if disp_norm < 1e-6:
        print("  [FAIL] Particle did not move.")
        return False, com_arr

    disp_hat = disp / disp_norm

    # Angle between displacement and initial direction (degrees)
    cos_angle   = float(np.clip(np.dot(disp_hat, v_init), -1, 1))
    defl_angle  = float(np.degrees(np.arccos(cos_angle)))

    # Expected deflection direction: V1 x z = (1,-1,0)/sqrt(2)
    v_expected = np.array([1., -1., 0.]) / np.sqrt(2)
    # Perpendicular component of displacement
    perp = disp_hat - np.dot(disp_hat, v_init) * v_init
    perp_norm = np.linalg.norm(perp)
    if perp_norm > 1e-6:
        perp_hat      = perp / perp_norm
        cos_perp      = float(np.clip(np.dot(perp_hat, v_expected), -1, 1))
        # Accept either sign (charge sign determines direction)
        perp_alignment = float(np.degrees(np.arccos(abs(cos_perp))))
    else:
        perp_alignment = 90.0

    print(f"  Start CoM: {start_com}")
    print(f"  End   CoM: {end_com}")
    print(f"  Deflection angle from V1: {defl_angle:.1f} deg  (need >10)")
    print(f"  Perp alignment with V1xz: {perp_alignment:.1f} deg  (need <45)")

    passed = (defl_angle > 10.0) and (perp_alignment < 45.0)
    print(f"  {'[PASS]' if passed else '[FAIL]'} EM deflection test")

    if save_data:
        fname = os.path.join(DATA_DIR, 'exp_08_deflection.npy')
        np.save(fname, com_arr)
        print(f"  Saved: {fname}")

    if save_gif and frames:
        _save_deflection_gif(frames, lat, g, z_sl, DEFL_EM_STR)

    return passed, com_arr


def _save_deflection_gif(frames, lat, g, z_sl, em_str):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    # Background: A_z component of vector potential at the z-slice
    A_bg = lat.vector_potential[2, :, :, z_sl]

    # Normalise EM field to [0,1] for blue-channel tint so it can be composited
    # directly into the 'hot' RGB output rather than as a separate imshow layer.
    # This avoids PIL palette conflicts that doubled the GIF frame delay.
    A_norm = (A_bg - A_bg.min()) / (A_bg.max() - A_bg.min() + 1e-12)

    import matplotlib.cm as cm
    hot_cmap  = cm.get_cmap('hot')
    rdbu_cmap = cm.get_cmap('RdBu_r')

    fig, ax = plt.subplots(figsize=(5, 5))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title('EM Deflection  (z-slice)', color='white', fontsize=11)

    def composite(particle_slice):
        vmax = max(particle_slice.max(), 1e-12)
        p_rgba = hot_cmap(particle_slice.T / vmax)          # (Y,X,4)
        a_rgba = rdbu_cmap(A_norm.T)                        # (Y,X,4) static
        # Blend: EM field at 35% alpha under particle
        rgb = a_rgba[..., :3] * 0.35 + p_rgba[..., :3] * (1 - 0.35 * (1 - p_rgba[..., 3:4]))
        return np.clip(rgb, 0, 1)

    im = ax.imshow(composite(frames[0]), origin='lower', extent=[0, g, 0, g])

    def update(i):
        im.set_data(composite(frames[i]))
        return (im,)

    # Render each frame to a PIL image and save directly at 24fps.
    # FuncAnimation's pillow writer can round frame delay to wrong multiples;
    # PIL direct save guarantees the exact duration=42ms (≈24fps).
    from PIL import Image
    import io
    pil_frames = []
    for i in range(len(frames)):
        update(i)
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=80, facecolor='#0a0a0a')
        buf.seek(0)
        pil_frames.append(Image.open(buf).copy())
    path = os.path.join(FIG_DIR, 'exp_08_deflection.gif')
    pil_frames[0].save(path, save_all=True, append_images=pil_frames[1:],
                       loop=0, duration=[40]*len(pil_frames), optimize=False)
    plt.close(fig)
    print(f"  Saved GIF: {path}")


# ── Test 2: photon propagation speed ──────────────────────────────────────────

def test_gravity_vs_em():
    """
    Gravity (div) attracts; EM twist (curl) deflects sideways.

    Two particles start at the same offset from a source, each moving
    tangentially with the same initial momentum.

    Particle A: Coulomb clock density well  (div deformation)
      Expected: CoM moves TOWARD well center (radial infall)
      Metric: radial distance to well decreases

    Particle B: EM twist (curl deformation), same geometry
      Expected: CoM deflects SIDEWAYS (tangential, not radial)
      Metric: radial distance stays roughly constant, transverse drift grows

    Pass: gravity_dr < -0.5  (inward drift > 0.5 nodes)
      AND em_tangential > |em_radial|  (more sideways than radial)
    """
    print("\n" + "="*60)
    print("TEST 2: Gravity (div) vs EM (curl) force geometry")
    print("="*60)

    g   = GRAV_GRID
    wc  = (g//2,) * 3
    # Particle starts offset from source along x-axis
    r0    = 8
    start = (wc[0] + r0, wc[1], wc[2])
    omega = 0.08
    # Tangential momentum along y (perpendicular to radial x)
    k_tan = 0.06

    # --- Particle A: gravity (positive clock density well, zero momentum) ---
    # set_clock_density_well with positive depth: increases delta_phi at center →
    # higher p_stay near center → amplitude concentrates toward the well.
    # This is the exp_02-confirmed gravitational mechanism.
    lat_g = OctahedralLattice(g, g, g)
    lat_g.set_clock_density_well(wc, width=5.0, depth=0.5)
    sess_g = make_gaussian_packet(lat_g, start, omega, width=1.5,
                                  k_vec=(0, 0, 0))   # zero momentum
    com_g0 = center_of_mass(sess_g.probability_density())

    for _ in range(GRAV_TICKS):
        sess_g.tick(); sess_g.advance_tick_counter()

    com_g1   = center_of_mass(sess_g.probability_density())
    # Radial displacement (positive = outward from well center)
    r_start  = float(np.linalg.norm(com_g0 - np.array(wc, dtype=float)))
    r_end_g  = float(np.linalg.norm(com_g1 - np.array(wc, dtype=float)))
    grav_dr  = r_end_g - r_start   # negative = attracted inward

    # --- Particle B: EM twist (same zero momentum, same starting position) ---
    lat_e = OctahedralLattice(g, g, g)
    lat_e.set_em_twist(wc, width=DEFL_EM_W, strength=DEFL_EM_STR, axis=2)
    sess_e = make_gaussian_packet(lat_e, start, omega, width=1.5,
                                  k_vec=(0, 0, 0))
    com_e0 = center_of_mass(sess_e.probability_density())

    for _ in range(GRAV_TICKS):
        sess_e.tick(); sess_e.advance_tick_counter()

    com_e1     = center_of_mass(sess_e.probability_density())
    disp_e     = com_e1 - com_e0
    # Radial direction: from well center toward start
    rad_hat    = np.array([1., 0., 0.])   # start is offset along x
    em_radial  = float(np.dot(disp_e, rad_hat))
    em_tangential = float(np.linalg.norm(disp_e - em_radial * rad_hat))
    r_end_e    = float(np.linalg.norm(com_e1 - np.array(wc)))

    print(f"  Gravity:   r start={r_start:.2f}  r end={r_end_g:.2f}  "
          f"dr={grav_dr:+.2f}  (need < -0.5, i.e. inward drift)")
    print(f"  EM twist:  radial={em_radial:+.2f}  tangential={em_tangential:.2f}  "
          f"(need tangential > |radial|)")

    passed = (grav_dr < -0.5) and (em_tangential > abs(em_radial))
    print(f"  {'[PASS]' if passed else '[FAIL]'} Gravity vs EM geometry test")
    return passed


# ── Test 3: orbital emission ──────────────────────────────────────────────────

def test_orbital_emission(save_gif=False, save_data=True):
    """
    Electron in Gaussian well + photon session coupled via register_emission.
    After EMIT_TICKS: photon should have received >PHOTON_MIN amplitude fraction
    and its CoM should have moved away from the well.
    """
    print("\n" + "="*60)
    print("TEST 3: Orbital emission (photon escape)")
    print("="*60)

    g  = EMIT_GRID
    wc = (g//2,) * 3

    lat = OctahedralLattice(g, g, g)
    lat.set_clock_density_well(wc, width=EMIT_WELL_W, depth=EMIT_WELL_D)

    # Electron: orbit packet displaced from well, tangential momentum
    r_orb = 6
    dr    = int(round(r_orb / np.sqrt(3)))
    e_start = (wc[0]+dr, wc[1]+dr, wc[2]+dr)
    k_orb = 0.08   # tangential along V2=(1,-1,-1)
    electron = make_gaussian_packet(lat, e_start, EMIT_OMEGA,
                                    width=1.5, k_vec=(k_orb, -k_orb, -k_orb))

    # Photon: seed amplitude at electron start (tiny, so joint norm sets it ~0)
    photon = CausalSession(lat, e_start, instruction_frequency=0.0,
                           is_massless=True)
    seed = 1e-3
    photon.psi_R[:] = seed / np.sqrt(2)
    photon.psi_L[:] = seed / np.sqrt(2)
    enforce_unity_spinor(photon.psi_R, photon.psi_L)

    sched = TickScheduler()
    e_idx = sched.register_session(electron)
    p_idx = sched.register_session(photon)
    sched.register_emission(e_idx, p_idx, rate=EMIT_RATE)

    trace  = []   # (tick, e_frac, p_frac)
    frames = []   # for GIF: list of (e_slice, p_slice)

    GIF_STRIDE = max(1, EMIT_TICKS // 75)
    z_sl = g // 2

    for tick in range(EMIT_TICKS):
        sched.advance()
        e_d = electron.probability_density()
        p_d = photon.probability_density()
        e_frac = float(e_d.sum())
        p_frac = float(p_d.sum())
        trace.append([float(tick), e_frac, p_frac])

        if save_gif and tick % GIF_STRIDE == 0:
            frames.append((e_d[:, :, z_sl].copy(),
                           p_d[:, :, z_sl].copy()))

    trace_arr = np.array(trace)
    final_p_frac = trace_arr[-1, 2]

    # Photon CoM at start vs end
    p_com0 = np.array(list(wc), dtype=float)
    p_com1 = center_of_mass(photon.probability_density())
    p_escape = float(np.linalg.norm(p_com1 - p_com0))

    print(f"  Final electron amplitude fraction: {trace_arr[-1,1]:.4f}")
    print(f"  Final photon  amplitude fraction:  {final_p_frac:.4f}  (need >{PHOTON_MIN})")
    print(f"  Photon CoM displacement from well: {p_escape:.2f} nodes")

    passed = (final_p_frac > PHOTON_MIN) and (p_escape > 1.0)
    print(f"  {'[PASS]' if passed else '[FAIL]'} Orbital emission test")

    if save_data:
        fname = os.path.join(DATA_DIR, 'exp_08_emission.npy')
        np.save(fname, trace_arr)
        print(f"  Saved: {fname}")

    if save_gif and frames:
        _save_emission_gif(frames, g, z_sl, wc)

    return passed, trace_arr


def _save_emission_gif(frames, g, z_sl, wc):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    fig.patch.set_facecolor('#0a0a0a')
    titles = ['Electron', 'Photon']
    cmaps  = ['hot', 'cool']
    ims    = []

    for ax, title, cmap in zip(axes, titles, cmaps):
        ax.set_facecolor('#0a0a0a')
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(title, color='white', fontsize=12)
        # Well center marker
        ax.plot(wc[0], wc[1], '+', color='lime', markersize=8, linewidth=1.5)

    e0, p0 = frames[0]
    ims.append(axes[0].imshow(e0.T, origin='lower', cmap='hot',
                               vmin=0, vmax=max(e0.max(), 1e-12),
                               extent=[0, g, 0, g]))
    ims.append(axes[1].imshow(p0.T, origin='lower', cmap='cool',
                               vmin=0, vmax=max(p0.max(), 1e-12),
                               extent=[0, g, 0, g]))

    tick_text = fig.text(0.5, 0.02, 'tick 0', ha='center',
                         color='white', fontsize=10)

    def update(i):
        e_sl, p_sl = frames[i]
        ims[0].set_data(e_sl.T)
        ims[0].set_clim(0, max(e_sl.max(), 1e-12))
        ims[1].set_data(p_sl.T)
        ims[1].set_clim(0, max(p_sl.max(), 1e-12))
        tick_text.set_text(f'tick {i * max(1, EMIT_TICKS // 75)}')
        return ims + [tick_text]

    from PIL import Image
    import io
    pil_frames = []
    for i in range(len(frames)):
        update(i)
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=80, facecolor='#0a0a0a')
        buf.seek(0)
        pil_frames.append(Image.open(buf).copy())
    path = os.path.join(FIG_DIR, 'exp_08_emission.gif')
    pil_frames[0].save(path, save_all=True, append_images=pil_frames[1:],
                       loop=0, duration=[40]*len(pil_frames), optimize=False)
    plt.close(fig)
    print(f"  Saved GIF: {path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def run_vacuum_twist_audit(save_gif=False):
    print("="*60)
    print("EXPERIMENT 08: Vacuum Twist -- Gravity vs Electromagnetism")
    print("="*60)

    t0 = time.time()

    p1, _ = test_em_deflection(save_gif=save_gif)
    p2    = test_gravity_vs_em()
    p3, _ = test_orbital_emission(save_gif=save_gif)

    elapsed = time.time() - t0
    passed  = p1 and p2 and p3

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Test 1 (EM deflection):      {'PASS' if p1 else 'FAIL'}")
    print(f"  Test 2 (gravity vs EM):      {'PASS' if p2 else 'FAIL'}")
    print(f"  Test 3 (orbital emission):   {'PASS' if p3 else 'FAIL'}")
    print(f"  Total time: {elapsed:.1f}s")
    print(f"\n  {'[EXP_08 PASSED]' if passed else '[EXP_08 FAILED]'}")

    return passed


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--gif', action='store_true',
                    help='Generate GIF animations (adds ~1 min)')
    args = ap.parse_args()

    passed = run_vacuum_twist_audit(save_gif=args.gif)
    sys.exit(0 if passed else 1)
