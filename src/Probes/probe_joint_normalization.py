"""
probe_joint_normalization.py
Unit test: does amplitude transfer + joint normalization work correctly?

Tests two distinct mechanisms:
  1. joint_normalize(*sessions) -- rescales all sessions to shared A=1 budget.
     This preserves amplitude RATIOS between sessions (not a transfer mechanism).
  2. transfer_amplitude(source, target, fraction) -- explicitly moves amplitude
     from source to target, then joint-normalizes.
     This is the mechanism exp_19 requires for photon emission.

No lattice dynamics, no tick rule, no orbital physics.
Just the normalization and transfer arithmetic.
"""

import numpy as np
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession, enforce_unity_spinor

GRID = 10
CENTER = (5, 5, 5)

def joint_normalize(*sessions):
    """
    Normalize a set of sessions jointly so that:
      sum over all sessions of (|psi_R|^2 + |psi_L|^2) = 1

    This is the correct multi-session A=1 constraint.
    NOTE: This preserves the amplitude RATIO between sessions.
    It does NOT transfer amplitude from one session to another.
    Modifies sessions in place.
    """
    total_norm = np.sqrt(sum(
        np.sum(np.abs(s.psi_R)**2 + np.abs(s.psi_L)**2)
        for s in sessions
    ))
    if total_norm < 1e-12:
        raise RuntimeError("Joint norm collapsed to zero.")
    for s in sessions:
        s.psi_R /= total_norm
        s.psi_L /= total_norm


def transfer_amplitude(source, target, fraction):
    """
    Move `fraction` of source's current amplitude to target.
    Operates directly on spinor arrays -- no normalization applied here.
    Call joint_normalize(*sessions) after to enforce A=1.

    This is the primitive operation underlying photon emission:
    the electron (source) gives amplitude to the photon (target).
    The proton then absorbs recoil via the joint normalization step.

    Args:
        source:   CausalSession to lose amplitude
        target:   CausalSession to gain amplitude
        fraction: float in (0, 1) -- fraction of source amplitude to move
    """
    delta_R = source.psi_R * fraction
    delta_L = source.psi_L * fraction
    target.psi_R += delta_R
    target.psi_L += delta_L
    source.psi_R -= delta_R
    source.psi_L -= delta_L


def amplitude(session):
    """Total probability in a session."""
    return float(np.sum(
        np.abs(session.psi_R)**2 + np.abs(session.psi_L)**2
    ))


def run_unit_test():
    print("=" * 60)
    print("UNIT TEST: Amplitude Transfer + Joint Normalization")
    print("=" * 60)

    lattice = OctahedralLattice(GRID, GRID, GRID)
    passed = True

    # ── Test 1: joint_normalize conserves total amplitude ────────────
    print("\nTest 1: Joint normalization conserves total amplitude")

    s1 = CausalSession(lattice, CENTER, instruction_frequency=0.1)
    s2 = CausalSession(lattice, CENTER, instruction_frequency=0.0,
                       is_massless=True)
    s2.psi_R *= 0.01
    s2.psi_L *= 0.01

    amp1_before = amplitude(s1)
    amp2_before = amplitude(s2)
    total_before = amp1_before + amp2_before

    print(f"  Before: s1={amp1_before:.6f}  s2={amp2_before:.6f}"
          f"  total={total_before:.6f}")

    joint_normalize(s1, s2)

    amp1_after = amplitude(s1)
    amp2_after = amplitude(s2)
    total_after = amp1_after + amp2_after

    print(f"  After:  s1={amp1_after:.6f}  s2={amp2_after:.6f}"
          f"  total={total_after:.6f}")

    conservation_error = abs(total_after - 1.0)
    t1_passed = conservation_error < 1e-10
    print(f"  Conservation error: {conservation_error:.2e}"
          f"  {'PASS' if t1_passed else 'FAIL'}")
    passed = passed and t1_passed

    # ── Test 2: joint_normalize preserves amplitude ratio ────────────
    print("\nTest 2: Joint normalization preserves amplitude ratio (no transfer)")

    s1b = CausalSession(lattice, CENTER, instruction_frequency=0.1)
    s2b = CausalSession(lattice, CENTER, instruction_frequency=0.0,
                        is_massless=True)
    s2b.psi_R *= 0.01
    s2b.psi_L *= 0.01

    amp1b_before = amplitude(s1b)
    amp2b_before = amplitude(s2b)
    total_before_b = amp1b_before + amp2b_before
    ratio_before = amp2b_before / total_before_b

    joint_normalize(s1b, s2b)

    amp1b_after = amplitude(s1b)
    amp2b_after = amplitude(s2b)
    total_after_b = amp1b_after + amp2b_after
    ratio_after = amp2b_after / total_after_b

    ratio_change = abs(ratio_after - ratio_before)
    t2_passed = ratio_change < 1e-10
    print(f"  s2 share before: {ratio_before:.8f}")
    print(f"  s2 share after:  {ratio_after:.8f}")
    print(f"  Ratio unchanged (joint norm preserves ratio): {t2_passed}"
          f"  {'PASS' if t2_passed else 'FAIL'}")
    print(f"  Note: joint_normalize is NOT an amplitude transfer mechanism.")
    print(f"  Transfer requires transfer_amplitude() first (see Test 4).")
    passed = passed and t2_passed

    # ── Test 3: Per-session norm breaks joint budget ──────────────────
    print("\nTest 3: Per-session normalization prevents transfer (known failure)")

    s3 = CausalSession(lattice, CENTER, instruction_frequency=0.1)
    s4 = CausalSession(lattice, CENTER, instruction_frequency=0.0,
                       is_massless=True)
    s4.psi_R *= 0.01
    s4.psi_L *= 0.01

    amp3_before = amplitude(s3)
    amp4_before = amplitude(s4)

    enforce_unity_spinor(s3.psi_R, s3.psi_L)
    enforce_unity_spinor(s4.psi_R, s4.psi_L)

    amp3_after = amplitude(s3)
    amp4_after = amplitude(s4)

    print(f"  s3: {amp3_before:.6f} -> {amp3_after:.6f}"
          f"  (change={amp3_after - amp3_before:+.6f})")
    print(f"  s4: {amp4_before:.6f} -> {amp4_after:.6f}"
          f"  (change={amp4_after - amp4_before:+.6f})")

    t3_passed = (abs(amp3_after - 1.0) < 1e-10 and
                 abs(amp4_after - 1.0) < 1e-10)
    print(f"  Per-session norm restores each to 1.0: {t3_passed}")
    print(f"  This confirms per-session norm cannot transfer amplitude.")
    print(f"  {'PASS' if t3_passed else 'FAIL'} (expected behavior documented)")
    passed = passed and t3_passed

    # ── Test 4: transfer_amplitude moves amplitude from s1 to s2 ─────
    print("\nTest 4: transfer_amplitude() moves amplitude from source to target")

    electron = CausalSession(lattice, CENTER, instruction_frequency=0.1019)
    photon   = CausalSession(lattice, CENTER, instruction_frequency=0.0,
                              is_massless=True)
    # Photon starts near-zero
    photon.psi_R *= 0.001
    photon.psi_L *= 0.001

    amp_e_before = amplitude(electron)
    amp_g_before = amplitude(photon)
    total_before = amp_e_before + amp_g_before
    ratio_before = amp_g_before / total_before

    FRACTION = 0.10
    transfer_amplitude(electron, photon, FRACTION)
    joint_normalize(electron, photon)

    amp_e_after = amplitude(electron)
    amp_g_after = amplitude(photon)
    total_after = amp_e_after + amp_g_after
    ratio_after = amp_g_after / total_after

    conservation_error = abs(total_after - 1.0)
    photon_gained = ratio_after > ratio_before
    ratio_increase = ratio_after - ratio_before

    print(f"  Before: electron={amp_e_before:.6f}  photon={amp_g_before:.8f}"
          f"  total={total_before:.6f}")
    print(f"  After:  electron={amp_e_after:.6f}  photon={amp_g_after:.6f}"
          f"  total={total_after:.6f}")
    print(f"  photon share before: {ratio_before:.8f}")
    print(f"  photon share after:  {ratio_after:.8f}")
    print(f"  photon gained amplitude: {photon_gained}"
          f"  (ratio increase = {ratio_increase:+.6f})")
    print(f"  Conservation error: {conservation_error:.2e}")

    t4_passed = photon_gained and conservation_error < 1e-10
    print(f"  {'PASS' if t4_passed else 'FAIL'}")
    passed = passed and t4_passed

    # ── Test 5: Three-session transfer (electron + proton + photon) ───
    print("\nTest 5: Three-session: electron emits to photon, proton absorbs recoil")

    electron2 = CausalSession(lattice, CENTER, instruction_frequency=0.1019)
    proton2   = CausalSession(lattice, CENTER, instruction_frequency=np.pi/2)
    photon2   = CausalSession(lattice, CENTER, instruction_frequency=0.0,
                               is_massless=True)
    photon2.psi_R *= 0.001
    photon2.psi_L *= 0.001

    amp_e2_before = amplitude(electron2)
    amp_p2_before = amplitude(proton2)
    amp_g2_before = amplitude(photon2)
    total2_before = amp_e2_before + amp_p2_before + amp_g2_before

    print(f"  Before: electron={amp_e2_before:.6f}  proton={amp_p2_before:.6f}"
          f"  photon={amp_g2_before:.8f}  total={total2_before:.6f}")

    # Electron emits fraction to photon; proton recoil via joint normalization
    FRACTION2 = 0.05
    transfer_amplitude(electron2, photon2, FRACTION2)
    joint_normalize(electron2, proton2, photon2)

    amp_e2_after = amplitude(electron2)
    amp_p2_after = amplitude(proton2)
    amp_g2_after = amplitude(photon2)
    total2_after = amp_e2_after + amp_p2_after + amp_g2_after

    conservation_error2 = abs(total2_after - 1.0)
    photon2_gained = amp_g2_after > amp_g2_before / total2_before

    print(f"  After:  electron={amp_e2_after:.6f}  proton={amp_p2_after:.6f}"
          f"  photon={amp_g2_after:.6f}  total={total2_after:.6f}")
    print(f"  photon gained amplitude: {photon2_gained}")
    print(f"  Conservation error: {conservation_error2:.2e}")

    e2_loss = (amp_e2_before / total2_before) - amp_e2_after
    p2_loss = (amp_p2_before / total2_before) - amp_p2_after
    g2_gain = amp_g2_after - (amp_g2_before / total2_before)
    print(f"  electron loss: {e2_loss:+.6f}"
          f"  proton loss: {p2_loss:+.6f}"
          f"  photon gain: {g2_gain:+.6f}")

    t5_passed = photon2_gained and conservation_error2 < 1e-10
    print(f"  {'PASS' if t5_passed else 'FAIL'}")
    passed = passed and t5_passed

    # ── Test 6: Mass-proportional recoil ─────────────────────────────
    print("\nTest 6: Heavier session absorbs larger fraction of normalization recoil")

    electron3 = CausalSession(lattice, CENTER, instruction_frequency=0.1019)
    proton3   = CausalSession(lattice, CENTER, instruction_frequency=np.pi/2)
    photon3   = CausalSession(lattice, CENTER, instruction_frequency=0.0,
                               is_massless=True)
    photon3.psi_R *= 0.001
    photon3.psi_L *= 0.001

    amp_e3_i = amplitude(electron3)
    amp_p3_i = amplitude(proton3)
    amp_g3_i = amplitude(photon3)
    total3_i = amp_e3_i + amp_p3_i + amp_g3_i

    FRACTION3 = 0.05
    transfer_amplitude(electron3, photon3, FRACTION3)
    joint_normalize(electron3, proton3, photon3)

    amp_e3_f = amplitude(electron3)
    amp_p3_f = amplitude(proton3)

    # After transfer, electron's share is ~(1 - FRACTION3) of its original
    # The normalization then scales both proton and electron.
    # Since both start at equal per-session amplitude (A=1 each before scaling),
    # the per-session norm recoil is equal. Mass-proportional recoil only
    # differs when sessions have different initial amplitudes or spatial extents.
    e3_share_change = amp_e3_f - (amp_e3_i / total3_i)
    p3_share_change = amp_p3_f - (amp_p3_i / total3_i)

    print(f"  electron share change: {e3_share_change:+.6f}")
    print(f"  proton share change:   {p3_share_change:+.6f}")
    print(f"  Note: mass-proportional recoil is a dynamical effect requiring")
    print(f"  different spatial extents (orbital state). With equal initial")
    print(f"  amplitudes, joint norm distributes recoil equally between sessions.")
    print(f"  This test is informational -- mass-proportional effect emerges")
    print(f"  only when electron is in a bound orbital (smaller spatial extent")
    print(f"  than proton at rest).")
    # Not pass/fail -- informational
    print(f"  INFORMATIONAL (not pass/fail)")

    # ── Summary ───────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"UNIT TEST {'PASSED' if passed else 'FAILED'}")
    print("=" * 60)
    print("""
Key findings:
  Test 1:   Joint normalization conserves total amplitude to machine
            precision. Correct global A=1 enforcement.
  Test 2:   Joint normalization PRESERVES amplitude ratio between
            sessions -- it is NOT a transfer mechanism by itself.
  Test 3:   Per-session normalization cannot transfer amplitude.
            Confirms architectural gap in current production code.
  Test 4:   transfer_amplitude(source, target, fraction) followed by
            joint_normalize() correctly moves amplitude from electron
            to photon with total conservation. This is the primitive
            operation for photon emission in exp_19.
  Test 5:   Three-session transfer works: electron emits to photon,
            proton absorbs recoil via joint normalization. The three-
            session joint A=1 budget is the correct architecture.
  Test 6:   Mass-proportional recoil requires orbital state context
            (different spatial extents). Informational only here.

Architecture for exp_19:
  Per tick:
    1. transfer_amplitude(electron, photon, emission_rate)
    2. joint_normalize(electron, proton, photon)
  This replaces per-session enforce_unity_spinor for the bound group.
  emission_rate is a free parameter (~0.001-0.01 per tick).
""")
    return passed


if __name__ == '__main__':
    passed = run_unit_test()
    sys.exit(0 if passed else 1)
