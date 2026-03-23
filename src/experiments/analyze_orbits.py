"""
analyze_orbits.py
Analyzes the saved orbit_n1_grid65.npy and orbit_n2_grid65.npy files.

Place this in the same directory as the .npy files and run:
    python analyze_orbits.py

Shows:
  - Distance vs time for each orbit
  - Orbital period from FFT and zero-crossings
  - Energy estimate from mean radius
  - Diagnosis of what went wrong / right
"""

import numpy as np
import sys
import os

STRENGTH  = 30.0
SOFTENING = 0.5
R1_TARGET = 10.3

def load_orbit(n):
    fname = f'orbit_n{n}_grid65.npy'
    if not os.path.exists(fname):
        fname = f'orbit_n{n}.npy'
    if not os.path.exists(fname):
        print(f"  {fname} not found")
        return None
    return np.load(fname)

def period_fft(dists):
    sig = np.array(dists) - np.mean(dists)
    n   = len(sig)
    nf  = 1
    while nf < 4*n: nf *= 2
    spec = np.abs(np.fft.rfft(sig, n=nf))
    spec[:3] = 0
    pk = np.argmax(spec)
    if spec[pk] < np.std(spec)*2: return None
    return nf / pk if pk > 0 else None

def period_zc(dists, min_zc=4):
    m  = np.mean(dists)
    zc = [i for i in range(len(dists)-1)
          if (dists[i]-m)*(dists[i+1]-m) < 0]
    if len(zc) < min_zc: return None
    return 2.0*np.mean([zc[i+1]-zc[i] for i in range(len(zc)-1)])

def analyze(dists, n):
    print(f"\n  n={n} orbit analysis ({len(dists)} ticks):")
    print(f"  r_start  = {dists[0]:.3f}")
    print(f"  r_mean   = {np.mean(dists):.3f}  (target: {n**2 * R1_TARGET:.1f})")
    print(f"  r_min    = {min(dists):.3f}")
    print(f"  r_max    = {max(dists):.3f}")
    print(f"  r_range  = {max(dists)-min(dists):.3f}")

    # Phase analysis: first 100 ticks vs last 100 ticks
    early = dists[:100]; late = dists[-100:]
    print(f"  r_mean early (t=0..99)   = {np.mean(early):.3f}")
    print(f"  r_mean late  (t=300..399) = {np.mean(late):.3f}")
    drifting = np.mean(late) - np.mean(early)
    print(f"  Drift: {drifting:+.3f}  "
          f"({'escaping' if drifting > 1 else 'falling in' if drifting < -1 else 'stable'})")

    # Period
    T_zc  = period_zc(dists)
    T_fft = period_fft(dists)
    print(f"  T_orb (zero-cross) = {T_zc:.2f}" if T_zc else "  T_orb (zero-cross) = not detected")
    print(f"  T_orb (FFT)        = {T_fft:.2f}" if T_fft else "  T_orb (FFT)        = not detected")

    # Energy
    E = -STRENGTH / (np.mean(dists) + SOFTENING)
    print(f"  E_n = {E:.6f}")

    # ASCII distance plot
    print(f"\n  Distance vs time (every 10 ticks):")
    print(f"  {'t':>5}  {'r':>7}  chart")
    r_max_plot = max(dists)
    for i in range(0, len(dists), 10):
        bar = '█' * int(dists[i]/r_max_plot * 40)
        target_bar = int(n**2 * R1_TARGET / r_max_plot * 40)
        line = list(' ' * 42)
        for j in range(len(bar)): line[j] = '█'
        line[target_bar] = '|'  # target radius marker
        print(f"  {i:>5}  {dists[i]:>7.3f}  {''.join(line)}")

    return E, T_zc or T_fft

print("=" * 60)
print("ORBIT ANALYSIS")
print("=" * 60)
print("(| marks the target Bohr radius)")

energies = {}
for n in [1, 2, 3]:
    d = load_orbit(n)
    if d is not None:
        E, T = analyze(d, n)
        energies[n] = (E, T, np.mean(d))

print("\n" + "=" * 60)
print("BOHR SPECTRUM SUMMARY")
print("=" * 60)
if len(energies) >= 2:
    E1, T1, r1 = energies[1]
    print(f"\n  n=1 baseline: r_mean={r1:.2f}  E_1={E1:.6f}")
    print()
    print(f"  {'n':>3}  {'r_mean':>8}  {'r/r1':>7}  {'n^2':>5}  "
          f"{'E/E1':>10}  {'1/n^2':>10}  Bohr?")
    print("  " + "-"*55)
    for n, (E, T, r) in sorted(energies.items()):
        rr   = r / r1
        Er   = E / E1
        pred = 1/n**2
        ok   = abs(Er - pred)/pred < 0.15
        print(f"  {n:>3}  {r:>8.3f}  {rr:>7.3f}  {n**2:>5}  "
              f"{Er:>10.6f}  {pred:>10.6f}  {'YES' if ok else 'no'}")

print("\nDiagnosis:")
if 1 in energies and 2 in energies:
    r1 = energies[1][2]; r2 = energies[2][2]
    if r2/r1 > 3.0:
        print("  n=2 orbit is at larger radius than n=1 -- Bohr scaling plausible.")
        print("  Check E ratio above.")
    elif abs(r2 - r1) < 5:
        print("  Both orbits converged to similar radius -- single basin.")
        print("  Fix: increase STRENGTH or decrease K_TANG for n=1.")
    else:
        print(f"  r_2/r_1 = {r2/r1:.3f}  (Bohr predicts 4.0)")
        print("  Partial separation -- need more ticks or stronger well.")
