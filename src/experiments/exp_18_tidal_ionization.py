"""
exp_18_tidal_ionization.py
Quantum Roche limit: gravitational gradient prevents Arnold tongue lock-in.

Physics
-------
The hydrogen atom in the T3d framework is a two-body Arnold tongue attractor.
The joint proton-electron resonance locks onto the n=1 tongue when the
electron's orbital frequency matches the proton's Zitterbewegung frequency
to within the tongue's half-width Delta_omega_tongue.

A gravitational gradient across the orbital diameter introduces a differential
clock-rate shift:

    Delta_omega_tidal = g * R1

where g is the gradient strength (phase units per node) and R1 is the Bohr
radius.  When Delta_omega_tidal exceeds Delta_omega_tongue, the two sessions
experience different effective tick rates; the Arnold tongue lock-in is
prevented or disrupted before it can form.

This is the quantum Roche limit: a minimum orbital separation below which
gravity prevents quantization, not by supplying escape energy but by detuning
the phase-lock mechanism before it can engage.

The free-particle tongue width from exp_harmonic_hires gives a rough upper
bound:
    Delta_omega_free ~ 0.166  (FWHM of f=0.25 column in power map)
    g_crit_estimate  ~ Delta_omega_free / R1 ~ 0.0161 per node

Experimental design (Option 3 -- gradient from tick 0)
-------------------------------------------------------
The seeded orbit (K_BOHR initialization) is NOT a permanently stable state --
it is a transient that passes through the Bohr radius before the system either
locks onto the Arnold tongue attractor or escapes.  We cannot settle first and
then perturb (the base state is too short-lived).

Instead: apply gradient g from tick 0 alongside the Coulomb interaction.
Measure T_escape(g): the tick at which the orbit first exceeds ESCAPE_RADIUS
for N_ESCAPE_CONFIRM consecutive windows.

The prediction:
    T_escape(g=0) sets the baseline escape time.
    T_escape(g>0) < T_escape(g=0): gradient shortens the lifetime.
    At g_crit: T_escape drops sharply (the tongue never forms).

This directly measures whether gradient detuning suppresses Arnold tongue
lock-in -- the mechanism the paper claims is responsible for gravitational
ionization.

g-scan:
    G_VALUES covers 0 (control) to ~5x g_crit_estimate.
    For each g: run TICKS_TOTAL ticks, record T_escape and tidal displacement.

Tidal displacement diagnostic (smoking gun):
    At each window, record x-projections of electron and proton CoM relative
    to system CoM.  Gradient ionization: they diverge in OPPOSITE directions.
    Energy injection: both scatter isotropically.

Saved: data/exp_18_tidal_ionization.npy
  columns: g, escaped (bool), T_escape, x_e_proj_final, x_p_proj_final,
           r_pdf_first_window (orbit quality at start)
"""

import sys, os, time
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession, enforce_unity_spinor

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
os.makedirs(_DATA_DIR, exist_ok=True)

# ── Physical parameters (from exp_12) ─────────────────────────────────────────
OMEGA_E   = 0.1019
OMEGA_P   = np.pi / 2.0
STRENGTH  = 30.0
SOFTENING = 0.5
WIDTH_E   = 1.5
WIDTH_P   = 0.5
R1        = 10.3        # n=1 Bohr radius (exp_12 reference)

M_E = np.sin(OMEGA_E) / 2.0
M_P = np.sin(OMEGA_P) / 2.0
R_E_COM = R1
R_P_COM = R1 * M_E / M_P
K_BOHR  = 1.0 / R1      # 0.09709

# ── Gradient parameters ────────────────────────────────────────────────────────
# Free-particle tongue width estimate from exp_harmonic_hires (FWHM of f=0.25 column)
DELTA_OMEGA_FREE = 0.166    # measured from exp_harmonic_hires power map
G_CRIT_ESTIMATE  = DELTA_OMEGA_FREE / R1   # ~ 0.0161 per node

# Scan: 0 (control) + 6 gradient values spanning 0 to 5x estimate
G_VALUES = np.array([0.0, 0.004, 0.008, 0.012, 0.016, 0.040, 0.080])

# ── Run parameters ────────────────────────────────────────────────────────────
GRID             = 65           # same as exp_12 / exp_16
TICKS_TOTAL      = 2500         # total ticks per run (covers known ~2000 tick lifetime)
CHECK_EVERY      = 50           # ticks per diagnostic window
ESCAPE_RADIUS    = 2.0 * R1     # escape criterion: r_pdf_window > ESCAPE_RADIUS
N_ESCAPE_CONFIRM = 3            # consecutive windows above ESCAPE_RADIUS for escape


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_twobody_ic(lat_e, lat_p, wc, k_e):
    """Exp_12-style two-body initialization in CoM frame."""
    sz   = lat_e.size_x
    dr_e = R_E_COM / np.sqrt(3.0)
    dr_p = R_P_COM / np.sqrt(3.0)
    k_p  = k_e * M_E / M_P

    start_e = tuple(min(int(round(wc[i] + dr_e)), sz - 2) for i in range(3))
    start_p = tuple(max(int(round(wc[i] - dr_p)), 1)      for i in range(3))

    x  = np.arange(sz)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')

    sx, sy, sz_ = start_e
    env_e = (np.exp(-0.5 * ((xx-sx)**2 + (yy-sy)**2 + (zz-sz_)**2) / WIDTH_E**2)
             * np.exp(1j * k_e * (xx - yy - zz)))
    amp_e = env_e.astype(complex) / np.sqrt(2.0)
    electron = CausalSession(lat_e, start_e, instruction_frequency=OMEGA_E)
    electron.psi_R = amp_e.copy()
    electron.psi_L = amp_e.copy()
    enforce_unity_spinor(electron.psi_R, electron.psi_L)

    px, py, pz = start_p
    env_p = (np.exp(-0.5 * ((xx-px)**2 + (yy-py)**2 + (zz-pz)**2) / WIDTH_P**2)
             * np.exp(1j * k_p * (-xx + yy + zz)))
    amp_p = env_p.astype(complex) / np.sqrt(2.0)
    proton = CausalSession(lat_p, start_p, instruction_frequency=OMEGA_P)
    proton.psi_R = amp_p.copy()
    proton.psi_L = amp_p.copy()
    enforce_unity_spinor(proton.psi_R, proton.psi_L)

    return electron, proton


def coulomb_potential(grid, cx, cy, cz):
    x  = np.arange(grid)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    r  = np.sqrt((xx-cx)**2 + (yy-cy)**2 + (zz-cz)**2)
    return -STRENGTH / (r + SOFTENING)


def tidal_potential(grid, g, x_centre):
    """Linear gradient along x: V_tidal = g * (x - x_centre)."""
    x  = np.arange(grid, dtype=float)
    xx, _, _ = np.meshgrid(x, x, x, indexing='ij')
    return g * (xx - x_centre)


def density_com(density):
    total = float(density.sum())
    if total < 1e-12:
        return (0.0, 0.0, 0.0)
    x = np.arange(density.shape[0], dtype=float)
    cx = float(np.einsum('ijk,i->', density, x) / total)
    cy = float(np.einsum('ijk,j->', density, x) / total)
    cz = float(np.einsum('ijk,k->', density, x) / total)
    return (cx, cy, cz)


def system_com(e_com, p_com):
    x = (M_E * e_com[0] + M_P * p_com[0]) / (M_E + M_P)
    y = (M_E * e_com[1] + M_P * p_com[1]) / (M_E + M_P)
    z = (M_E * e_com[2] + M_P * p_com[2]) / (M_E + M_P)
    return (x, y, z)


def r_peak_relative(e_dens, p_com, n_bins=60):
    """
    PDF peak radius of (time-accumulated) electron density relative to proton CoM.
    Uses histogrammed radial distribution so the peak reflects where probability
    is concentrated over the window, not an instantaneous wavepacket position.
    """
    grid  = e_dens.shape[0]
    x     = np.arange(grid, dtype=float)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    radii = np.sqrt((xx - p_com[0])**2 + (yy - p_com[1])**2 + (zz - p_com[2])**2)
    r_max = float(radii.max())
    bins  = np.linspace(0, r_max, n_bins + 1)
    P, _  = np.histogram(radii.ravel(), bins=bins, weights=e_dens.ravel())
    if P.sum() < 1e-12:
        return 0.0
    centers = 0.5 * (bins[:-1] + bins[1:])
    return float(centers[np.argmax(P)])


def tick_twobody(electron, proton, g, x_centre, tick_counter):
    """
    One mutual tick with Coulomb + optional tidal potential.
    Tidal potential added on top of Coulomb each tick.
    Tick order alternates to cancel leading-order asymmetry.
    Returns (e_com, p_com) BEFORE the tick.
    """
    e_dens = electron.probability_density()
    p_dens = proton.probability_density()
    e_com  = density_com(e_dens)
    p_com  = density_com(p_dens)
    grid   = electron.lattice.size_x

    coul_e = coulomb_potential(grid, *p_com)
    coul_p = coulomb_potential(grid, *e_com)

    if g != 0.0:
        tid = tidal_potential(grid, g, x_centre)
        electron.lattice.topological_potential = coul_e + tid
        proton.lattice.topological_potential   = coul_p + tid
    else:
        electron.lattice.topological_potential = coul_e
        proton.lattice.topological_potential   = coul_p

    if tick_counter % 2 == 0:
        proton.tick();   proton.advance_tick_counter()
        electron.tick(); electron.advance_tick_counter()
    else:
        electron.tick(); electron.advance_tick_counter()
        proton.tick();   proton.advance_tick_counter()

    return e_com, p_com


# ── Single-g run ─────────────────────────────────────────────────────────────

def run_one_g(g, wc, x_centre):
    """
    Run TICKS_TOTAL ticks with gradient g applied from tick 0.
    Checks for escape every CHECK_EVERY ticks using windowed average density.
    Returns dict with T_escape and tidal displacement diagnostics.
    """
    lat_e = OctahedralLattice(GRID, GRID, GRID)
    lat_p = OctahedralLattice(GRID, GRID, GRID)
    electron, proton = make_twobody_ic(lat_e, lat_p, wc, K_BOHR)

    # Initial potentials
    e_com0 = density_com(electron.probability_density())
    p_com0 = density_com(proton.probability_density())
    electron.lattice.topological_potential = coulomb_potential(GRID, *p_com0)
    proton.lattice.topological_potential   = coulomb_potential(GRID, *e_com0)

    escaped        = False
    T_escape       = -1
    consec_escape  = 0
    x_e_proj_hist  = []
    x_p_proj_hist  = []
    r_pdf_history  = []   # r_pdf per window, for full trajectory record

    # Windowed accumulation
    win_dens  = None
    win_count = 0
    win_p_com = None
    r_pdf_first = None   # orbit quality in first window

    t0 = time.time()
    for tick in range(TICKS_TOTAL):
        e_com, p_com = tick_twobody(electron, proton, g, x_centre, tick)

        # Accumulate density over each CHECK_EVERY window
        e_dens = electron.probability_density()
        if win_dens is None:
            win_dens = e_dens.astype(float)
        else:
            win_dens += e_dens
        win_count += 1
        if win_count == CHECK_EVERY // 2:
            win_p_com = density_com(proton.probability_density())

        if (tick + 1) % CHECK_EVERY == 0:
            if win_p_com is None:
                win_p_com = density_com(proton.probability_density())

            r_pdf   = r_peak_relative(win_dens, win_p_com)
            sys_com = system_com(e_com, p_com)
            r_pdf_history.append(r_pdf)

            # Record r_pdf in first window as orbit quality metric
            if r_pdf_first is None:
                r_pdf_first = r_pdf

            # Tidal displacement: x-projection relative to system CoM
            x_e_proj = float(e_com[0] - sys_com[0])
            x_p_proj = float(p_com[0] - sys_com[0])
            x_e_proj_hist.append(x_e_proj)
            x_p_proj_hist.append(x_p_proj)

            if r_pdf > ESCAPE_RADIUS:
                consec_escape += 1
                if consec_escape >= N_ESCAPE_CONFIRM and not escaped:
                    escaped  = True
                    T_escape = tick + 1
            else:
                consec_escape = 0

            # Reset window accumulator
            win_dens  = None
            win_count = 0
            win_p_com = None

            if escaped:
                break

    elapsed = time.time() - t0
    x_e_final = float(x_e_proj_hist[-1]) if x_e_proj_hist else 0.0
    x_p_final = float(x_p_proj_hist[-1]) if x_p_proj_hist else 0.0

    return dict(g=g, escaped=escaped, T_escape=T_escape,
                x_e_proj=x_e_final, x_p_proj=x_p_final,
                r_pdf_first=r_pdf_first, r_pdf_history=r_pdf_history,
                elapsed=elapsed)


# ── Main ─────────────────────────────────────────────────────────────────────

def run():
    print('=' * 70)
    print('EXP 18: Tidal ionization -- quantum Roche limit (gradient from t=0)')
    print('=' * 70)
    print(f'  Grid={GRID}^3  TICKS_TOTAL={TICKS_TOTAL}  CHECK_EVERY={CHECK_EVERY}')
    print(f'  R1={R1}  K_BOHR={K_BOHR:.5f}  ESCAPE_RADIUS={ESCAPE_RADIUS:.1f}')
    print(f'  Delta_omega_free={DELTA_OMEGA_FREE:.4f}')
    print(f'  g_crit_estimate = {G_CRIT_ESTIMATE:.5f} per node')
    print(f'  g values: {G_VALUES}')
    print(f'  Prediction: T_escape(g>0) < T_escape(g=0); drops sharply near g_crit')
    print()

    wc       = (GRID // 2, GRID // 2, GRID // 2)
    x_centre = float(GRID // 2)

    print(f'  {"g":>8}  {"escaped":>8}  {"T_escape":>9}  {"r_pdf_t0":>9}'
          f'  {"x_e_proj":>9}  {"x_p_proj":>9}')
    print('  ' + '-' * 72)

    results   = []
    t_total   = time.time()

    for g in G_VALUES:
        res     = run_one_g(g, wc, x_centre)
        esc_str = 'YES' if res['escaped'] else 'no'
        t_str   = f"{res['T_escape']}" if res['escaped'] else f'>{TICKS_TOTAL}'
        r0_str  = f"{res['r_pdf_first']:.2f}" if res['r_pdf_first'] is not None else '---'
        print(f"  {g:8.4f}  {esc_str:>8}  {t_str:>9}  {r0_str:>9}"
              f"  {res['x_e_proj']:>9.3f}  {res['x_p_proj']:>9.3f}"
              f"  [{res['elapsed']:.0f}s]", flush=True)
        results.append(res)

    total_time = time.time() - t_total

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print('=' * 70)
    print('RESULT SUMMARY')
    print('=' * 70)

    control = results[0]
    if not control['escaped']:
        print(f'  Control (g=0): bound for full {TICKS_TOTAL} ticks. No baseline escape.')
        print('  WARNING: cannot measure T_escape(g>0) < T_escape(g=0) without baseline.')
        print('  Consider increasing TICKS_TOTAL.')
    else:
        print(f'  Control (g=0): escaped at T={control["T_escape"]}')

    print()
    print(f'  {"g":>8}  {"T_escape":>10}  {"tidal signature":>20}')
    print(f'  {"-"*8}  {"-"*10}  {"-"*20}')
    for r in results:
        t_str = f"{r['T_escape']}" if r['escaped'] else f'>{TICKS_TOTAL}'
        if r['escaped']:
            opp    = (r['x_e_proj'] * r['x_p_proj'] < 0)
            sig    = 'OPPOSITE' if opp else 'same-dir'
        else:
            sig = '---'
        print(f"  {r['g']:8.4f}  {t_str:>10}  {sig:>20}")

    # Check for monotonic T_escape decrease
    escaped_results = [(r['g'], r['T_escape']) for r in results if r['escaped']]
    if len(escaped_results) >= 2:
        g_vals   = [e[0] for e in escaped_results]
        t_vals   = [e[1] for e in escaped_results]
        monotone = all(t_vals[i] >= t_vals[i+1] for i in range(len(t_vals)-1))
        print(f'\n  Monotone T_escape decrease with g: {"YES" if monotone else "NO (non-monotone)"}')
        if control['escaped']:
            baseline = control['T_escape']
            for g, t in escaped_results[1:]:
                if t < baseline:
                    print(f'  g={g:.4f}: T_escape={t} < baseline={baseline}  '
                          f'(reduction={baseline-t} ticks)')

    print(f'\n  Total runtime: {total_time:.0f}s ({total_time/3600:.2f} hrs)')

    # ── Save ──────────────────────────────────────────────────────────────────
    out_npy = os.path.join(_DATA_DIR, 'exp_18_tidal_ionization.npy')
    rows = np.array([[r['g'], float(r['escaped']), float(r['T_escape']),
                      r['x_e_proj'], r['x_p_proj'],
                      r['r_pdf_first'] if r['r_pdf_first'] is not None else 0.0]
                     for r in results])
    np.save(out_npy, rows)
    print(f'\nSaved: {out_npy}')
    print('  columns: g, escaped, T_escape, x_e_proj, x_p_proj, r_pdf_first_window')

    # Save full r_pdf trajectories
    max_len = max(len(r['r_pdf_history']) for r in results)
    traj = np.full((len(results), max_len), np.nan)
    for i, r in enumerate(results):
        h = r['r_pdf_history']
        traj[i, :len(h)] = h
    out_traj = os.path.join(_DATA_DIR, 'exp_18_rpdf_trajectories.npy')
    np.save(out_traj, traj)
    print(f'Saved: {out_traj}  shape={traj.shape}  (rows=g_values, cols=windows)')


if __name__ == '__main__':
    run()
