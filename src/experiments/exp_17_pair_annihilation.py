"""
exp_17_pair_annihilation.py
Pair annihilation efficiency at omega = pi/2.

Physics
-------
The harmonic landscape has a 2:1 fixed point at omega = pi/2 where f_zitt = f_beat.
At this frequency a session spends equal time on both sublattices (psi_R ~ psi_L),
and the particle is its own vacuum reflection.  This is the natural frequency for
particle-antiparticle annihilation.

The experiment tests the prediction from notes/harmonic_landscape_A_structure.md:

  Prediction: When two sessions with omega = pi/2 and swapped chirality (psi_R <-> psi_L)
  interact via the TickScheduler pairwise coupling, the composite overlap density
  undergoes COHERENT oscillation at f ~ 0.25 cycles/tick before collapsing.
  At other omega values (e.g. pi/3) there is no shared mode and the density
  spreads incoherently.

The chirality swap (psi_R <-> psi_L) is the bipartite analog of charge conjugation.
RGB <-> CMY reverses chirality; at omega = pi/2 the two sessions are the closest the
A=1 framework comes to a particle-antiparticle pair without explicit antisymmetrisation.

Experimental design
-------------------
Two sessions are initialised at the SAME spatial centre with OPPOSITE chirality:
  Session A: psi_R dominant (ψ_R = amp, ψ_L = 0, then normalised)
  Session B: psi_L dominant (ψ_R = 0,   ψ_L = amp, then normalised)

Both sessions are registered with a TickScheduler and evolved via scheduler.advance().
The TickScheduler's _apply_pairwise_interactions mixes phases at nodes where both
sessions have significant amplitude -- this IS the interaction mechanism.

Two coupling strengths are tested:
  weak   (coupling=0.1): default observer/decoherence coupling
  strong (coupling=0.9): composite-particle binding strength

Three trials per coupling level:
  Trial 1: omega = pi/2, chirality-swapped      [annihilation candidate]
  Trial 2: omega = pi/3, chirality-swapped      [control: no shared mode]
  Trial 3: omega = pi/2, same chirality         [control: no C-conjugate]

Measurement
-----------
At each tick:
  1. overlap_density  = total |psi|^2 in sphere of radius R_OVL around centre
  2. total_density    = total |psi|^2 on full grid (both sessions)
  3. overlap_fraction = overlap_density / total_density

The overlap_fraction removes the dispersal envelope, leaving only the oscillatory
component.  A coherent annihilation signal appears as a persistent peak in the
FFT of the detrended overlap_fraction at f ~ f_zitt = omega/(2*pi).

Saved: data/exp_17_pair_annihilation.npy
  columns: trial_id, coupling_label, omega, chirality_swap,
           peak_f, peak_power, coherence_score
"""

import sys, os, time
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession, enforce_unity_spinor
from src.core.TickScheduler import TickScheduler, ShuffleScheme
from scipy.fft import rfft, rfftfreq

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
os.makedirs(_DATA_DIR, exist_ok=True)

# ── Parameters ────────────────────────────────────────────────────────────────
GRID    = 33            # small grid -- sessions overlap at centre
TICKS   = 2048          # power of 2 for clean FFT (4x for better freq resolution)
BURN_IN = 32            # discard initial transient
WIDTH   = 1.5           # wavepacket width (nodes)
R_OVL   = 6.0           # overlap sphere radius (nodes)

OMEGA_ANNIHILATE = np.pi / 2.0   # 2:1 fixed point: f_zitt = f_beat = 0.25
OMEGA_CONTROL    = np.pi / 3.0   # 3:1: f_zitt=1/6, f_beat=1/3 -- no shared mode

COUPLING_WEAK   = 0.1   # default observer/decoherence strength
COUPLING_STRONG = 0.9   # composite-particle binding strength


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_session(lat, centre, omega, psi_R_dominant):
    """
    Gaussian wavepacket at rest.
    psi_R_dominant=True:  ψ_R=amp, ψ_L=0  (normalised)
    psi_R_dominant=False: ψ_R=0,   ψ_L=amp (normalised)
    """
    sz = lat.size_x
    x  = np.arange(sz)
    cx, cy, cz = centre
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    env = np.exp(-0.5 * ((xx-cx)**2 + (yy-cy)**2 + (zz-cz)**2) / WIDTH**2)
    amp = env.astype(complex)

    sess = CausalSession(lat, centre, instruction_frequency=omega)
    if psi_R_dominant:
        sess.psi_R = amp.copy()
        sess.psi_L = np.zeros_like(amp)
    else:
        sess.psi_R = np.zeros_like(amp)
        sess.psi_L = amp.copy()
    enforce_unity_spinor(sess.psi_R, sess.psi_L)
    return sess


def sphere_mask(sz, centre, r_ovl):
    cx, cy, cz = centre
    x   = np.arange(sz)
    xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
    return (xx-cx)**2 + (yy-cy)**2 + (zz-cz)**2 <= r_ovl**2


def session_total(sess):
    return float((np.abs(sess.psi_R)**2 + np.abs(sess.psi_L)**2).sum())


def session_overlap(sess, mask):
    return float(((np.abs(sess.psi_R)**2 + np.abs(sess.psi_L)**2) * mask).sum())


# ── Trial runner ──────────────────────────────────────────────────────────────

def run_trial(trial_id, coupling_label, coupling, omega, swap_chirality, label):
    """
    Run one trial under the TickScheduler with pairwise interaction.
    Returns (peak_f, peak_power, coherence_score, overlap_fraction_series).
    """
    print(f'\n  Trial {trial_id} [{coupling_label}]: {label}')
    print(f'    omega={omega:.4f}  swap={swap_chirality}  coupling={coupling}')

    lat_A = OctahedralLattice(GRID, GRID, GRID)
    lat_B = OctahedralLattice(GRID, GRID, GRID)
    centre = (GRID // 2, GRID // 2, GRID // 2)

    sess_A = make_session(lat_A, centre, omega, psi_R_dominant=True)
    sess_B = make_session(lat_B, centre, omega, psi_R_dominant=(not swap_chirality))

    # Register with TickScheduler -- this enables pairwise interaction
    sched = TickScheduler(shuffle_scheme=ShuffleScheme.SEQUENTIAL)
    idx_A = sched.register_session(sess_A)
    idx_B = sched.register_session(sess_B)
    sched.bind_sessions(idx_A, idx_B, coupling=coupling)

    mask = sphere_mask(GRID, centre, R_OVL)
    series_frac = []
    t0 = time.time()

    for tick in range(TICKS):
        sched.advance()
        if tick >= BURN_IN:
            ov  = session_overlap(sess_A, mask) + session_overlap(sess_B, mask)
            tot = session_total(sess_A) + session_total(sess_B)
            series_frac.append(ov / tot if tot > 1e-12 else 0.0)

    elapsed = time.time() - t0
    series  = np.array(series_frac)

    # Detrend (remove linear dispersal trend) then FFT
    t_idx   = np.arange(len(series), dtype=float)
    trend   = np.polyval(np.polyfit(t_idx, series, 1), t_idx)
    detrended = series - trend

    spectrum  = np.abs(rfft(detrended))**2
    freqs     = rfftfreq(len(series))

    # Ignore DC (index 0)
    peak_idx     = int(np.argmax(spectrum[1:]) + 1)
    peak_f       = float(freqs[peak_idx])
    peak_power   = float(spectrum[peak_idx])
    median_power = float(np.median(spectrum[1:]))
    coherence    = peak_power / median_power if median_power > 0 else 0.0

    # Raw series stats
    zc = int(np.sum(np.diff(np.sign(detrended - detrended.mean())) != 0))

    print(f'    peak_f={peak_f:.4f}  coherence={coherence:.1f}x  '
          f'zero-crossings={zc}/{len(series)//2}  [{elapsed:.0f}s]')
    print(f'    f_zitt={omega/(2*np.pi):.4f}  f_beat={0.5-omega/(2*np.pi):.4f}')

    return peak_f, peak_power, coherence, series


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    print('=' * 70)
    print('EXP 17: Pair annihilation efficiency at omega = pi/2')
    print('=' * 70)
    print(f'  Grid={GRID}^3  TICKS={TICKS}  BURN_IN={BURN_IN}  R_OVL={R_OVL}')
    print(f'  Measurement: overlap_fraction (overlap/total) -- dispersal removed')
    print(f'  Prediction: coherent peak at f~0.25 in Trial 1 only')

    trial_specs = [
        # (omega,             swap,  label)
        (OMEGA_ANNIHILATE, True,  'omega=pi/2, chirality-swapped  [annihilation]'),
        (OMEGA_CONTROL,    True,  'omega=pi/3, chirality-swapped  [control: no shared mode]'),
        (OMEGA_ANNIHILATE, False, 'omega=pi/2, same chirality     [control: no C-conj]'),
    ]

    coupling_levels = [
        ('weak',   COUPLING_WEAK),
        ('strong', COUPLING_STRONG),
    ]

    results    = []
    all_series = {}
    trial_id   = 0

    for coupling_label, coupling in coupling_levels:
        print(f'\n--- Coupling: {coupling_label} ({coupling}) ---')
        for omega, swap, label in trial_specs:
            trial_id += 1
            peak_f, peak_power, coherence, series = run_trial(
                trial_id, coupling_label, coupling, omega, swap, label)
            results.append((trial_id, coupling_label, omega, float(swap),
                            peak_f, peak_power, coherence))
            all_series[trial_id] = series

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print('=' * 70)
    print('RESULT SUMMARY')
    print('=' * 70)
    print(f'  {"ID":<4} {"coupling":<8} {"omega":>7} {"swap":>5} '
          f'{"peak_f":>8} {"coherence":>12}')
    print(f'  {"-"*4} {"-"*8} {"-"*7} {"-"*5} {"-"*8} {"-"*12}')
    for (tid, clabel, omega, swap, peak_f, peak_power, coherence) in results:
        swap_str = 'Y' if swap else 'N'
        print(f'  {tid:<4} {clabel:<8} {omega:>7.4f} {swap_str:>5} '
              f'{peak_f:>8.4f} {coherence:>11.1f}x')

    # Verdict: compare annihilation trial to controls within each coupling level
    print()
    for coupling_label, coupling in coupling_levels:
        level_results = [(r[0], r[4], r[6]) for r in results if r[1] == coupling_label]
        ann_coherence  = level_results[0][2]
        ctrl_coherences = [r[2] for r in level_results[1:]]
        contrast = ann_coherence / max(max(ctrl_coherences), 1.0)
        ann_f    = level_results[0][1]
        f_zitt   = OMEGA_ANNIHILATE / (2 * np.pi)

        if ann_coherence > 10.0 and contrast > 3.0 and abs(ann_f - f_zitt) < 0.05:
            verdict = 'PASS -- coherent annihilation mode at f~f_zitt'
        elif ann_coherence > 5.0 and contrast > 2.0:
            verdict = 'MARGINAL -- weak coherent mode above controls'
        else:
            verdict = 'NO SIGNAL -- annihilation not distinguished from controls'
        print(f'  [{coupling_label}] {verdict}')
        print(f'    ann_coherence={ann_coherence:.1f}x  '
              f'ctrl_max={max(ctrl_coherences):.1f}x  '
              f'contrast={contrast:.1f}x  '
              f'ann_f={ann_f:.4f}  f_zitt={f_zitt:.4f}')

    # ── Save ──────────────────────────────────────────────────────────────────
    out_npy = os.path.join(_DATA_DIR, 'exp_17_pair_annihilation.npy')
    rows = np.array([(r[0], r[2], r[3], r[4], r[5], r[6]) for r in results])
    np.save(out_npy, rows)
    print(f'\nSaved: {out_npy}')
    print('  columns: trial_id, omega, chirality_swap, peak_f, peak_power, coherence')

    out_series = os.path.join(_DATA_DIR, 'exp_17_overlap_series.npy')
    series_arr = np.array([all_series[i+1] for i in range(len(results))])
    np.save(out_series, series_arr)
    print(f'Saved: {out_series}  shape={series_arr.shape}')


if __name__ == '__main__':
    run()
