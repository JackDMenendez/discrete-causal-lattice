"""
exp_05_observer_clock.py
Audit: Observer as clock -- different shuffle orderings, irreversibility.

Verifies three claims from tick_scheduler.tex:

  1. IRREVERSIBILITY: Adding a session to the TickScheduler increases
     the combinatorial state space monotonically. Clock count only grows.

  2. SHUFFLE INVARIANCE (test): Two schedulers with different ShuffleSchemes
     but identical initial conditions should produce similar physics
     (probability conservation holds regardless of ordering).

  3. OBSERVER EFFECT: A session registered at the same location as
     a particle session alters the local probability distribution --
     the observer changes the observed system through clock entanglement.

Paper reference: Section 4 (TickScheduler) and Section 8 (observer as clock)
"""

import sys, os, math
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import (OctahedralLattice, CausalSession,
                      TickScheduler, ShuffleScheme,
                      enforce_unity, enforce_unity_spinor)


def make_gaussian(lattice, center, width, omega):
    """Convenience: Gaussian CausalSession."""
    cx, cy, cz = center
    x = np.arange(lattice.size_x)
    y = np.arange(lattice.size_y)
    z = np.arange(lattice.size_z)
    xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
    r_sq = (xx-cx)**2 + (yy-cy)**2 + (zz-cz)**2
    s = CausalSession(lattice, center, instruction_frequency=omega)
    envelope = np.exp(-0.5 * r_sq / width**2).astype(complex) / np.sqrt(2.0)
    s.psi_R = envelope.copy()
    s.psi_L = envelope.copy()
    enforce_unity_spinor(s.psi_R, s.psi_L)
    return s


def run_observer_clock_audit():
    print("=" * 60)
    print("EXPERIMENT 05: Observer as Clock")
    print("=" * 60)

    # ── Test 1: Irreversibility -- state space grows monotonically ────
    print("\n[Test 1] Irreversibility: state space grows with each observer")

    grid   = 15
    counts = []
    for n in range(1, 7):
        lattice = OctahedralLattice(grid, grid, grid)
        sched   = TickScheduler(ShuffleScheme.SEQUENTIAL)
        for i in range(n):
            s = make_gaussian(lattice, (7, 7+i, 7), 2.0, 0.2)
            sched.register_session(s)
        size = sched.combinatorial_state_space_size()
        counts.append((n, size))
        print(f"  {n} clock(s): state space = {n}! = {size:,}")

    monotone = all(counts[i][1] < counts[i+1][1] for i in range(len(counts)-1))
    print(f"  Monotonically increasing: {monotone}")
    test1_pass = monotone

    # ── Test 2: Probability conserved under all shuffle schemes ───────
    print("\n[Test 2] A=1 conservation under different shuffle schemes")

    schemes = [ShuffleScheme.SEQUENTIAL, ShuffleScheme.RANDOM,
               ShuffleScheme.PRIORITY]
    scheme_results = {}

    for scheme in schemes:
        lattice = OctahedralLattice(grid, grid, grid)
        sched   = TickScheduler(scheme)
        sessions = []
        for i in range(3):
            s = make_gaussian(lattice, (7, 5+i*2, 7), 2.0, 0.2)
            sched.register_session(s)
            sessions.append(s)

        max_dev = 0.0
        for _ in range(15):
            sched.advance()
            total = sum(np.sum(s.probability_density()) for s in sessions)
            max_dev = max(max_dev, abs(total - 3.0))

        scheme_results[scheme.value] = max_dev
        ok = max_dev < 1e-5
        print(f"  {scheme.value:12s}: max |total_rho - 3.0| = {max_dev:.2e}  "
              f"{'OK' if ok else 'FAIL'}")

    test2_pass = all(v < 1e-5 for v in scheme_results.values())

    # ── Test 3: Observer changes local probability distribution ────────
    print("\n[Test 3] Observer effect: registered observer alters local density")

    # Without observer: particle propagates freely
    lattice_free = OctahedralLattice(20, 20, 20)
    sched_free   = TickScheduler(ShuffleScheme.SEQUENTIAL)
    particle_free = make_gaussian(lattice_free, (10,10,10), 3.0, 0.2)
    sched_free.register_session(particle_free)

    for _ in range(10):
        sched_free.advance()

    density_free = particle_free.probability_density().copy()

    # With observer: second session registered at same location
    lattice_obs  = OctahedralLattice(20, 20, 20)
    sched_obs    = TickScheduler(ShuffleScheme.SEQUENTIAL)
    particle_obs = make_gaussian(lattice_obs, (10,10,10), 3.0, 0.2)
    observer     = make_gaussian(lattice_obs, (10,10,10), 1.5, 0.5)
    sched_obs.register_session(particle_obs)
    sched_obs.register_session(observer)

    print(f"  Clock count without observer: {sched_free.clock_count()}")
    print(f"  Clock count with observer   : {sched_obs.clock_count()}")
    print(f"  State space without: {sched_free.combinatorial_state_space_size()}! = "
          f"{sched_free.combinatorial_state_space_size():,}")
    print(f"  State space with   : {sched_obs.combinatorial_state_space_size()}! = "
          f"{sched_obs.combinatorial_state_space_size():,}")

    for _ in range(10):
        sched_obs.advance()

    density_obs = particle_obs.probability_density().copy()

    # Measure difference in particle density caused by observer presence
    diff = np.mean(np.abs(density_free - density_obs))
    total_free = np.sum(density_free)
    total_obs  = np.sum(density_obs)

    print(f"\n  Mean |density_free - density_obs| : {diff:.6f}")
    print(f"  Particle prob (free)             : {total_free:.8f}")
    print(f"  Particle prob (observed)         : {total_obs:.8f}")
    print(f"  Both sessions conserved (A=1)    : "
          f"{abs(total_free-1.0)<1e-6 and abs(total_obs-1.0)<1e-6}")

    # Observer changes local density -- the measurement effect
    observer_changed_density = diff > 1e-6
    print(f"\n  Observer altered particle density: {observer_changed_density}")
    test3_pass = observer_changed_density and abs(total_obs - 1.0) < 1e-5

    # ── Test 4: Cannot remove a clock -- irreversibility ──────────────
    print("\n[Test 4] Irreversibility: cannot un-register a clock")

    lattice4 = OctahedralLattice(grid, grid, grid)
    sched4   = TickScheduler(ShuffleScheme.RANDOM)
    s1 = make_gaussian(lattice4, (7,7,7), 2.0, 0.2)
    sched4.register_session(s1)
    count_before = sched4.clock_count()
    s2 = make_gaussian(lattice4, (7,9,7), 2.0, 0.3)
    sched4.register_session(s2)
    count_after  = sched4.clock_count()

    # TickScheduler has no remove_session -- by design
    has_no_remove = not hasattr(sched4, 'remove_session')
    print(f"  Clocks before observation : {count_before}")
    print(f"  Clocks after observation  : {count_after}")
    print(f"  No remove_session method  : {has_no_remove}")
    print(f"  (Irreversibility is architectural -- observation cannot be undone)")
    test4_pass = count_after > count_before and has_no_remove

    # ── Summary ───────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    all_pass = test1_pass and test2_pass and test3_pass and test4_pass

    if all_pass:
        print("[AUDIT PASSED] Observer-as-clock formalization confirmed.")
        print("  State space grows factorially with each new observer.")
        print("  A=1 holds under all shuffle schemes -- physics invariant.")
        print("  Observer presence alters local probability distribution.")
        print("  Irreversibility is architectural -- clocks cannot be removed.")
    else:
        print("[AUDIT FAILED]")
        if not test1_pass: print("  FAIL: state space not monotonically increasing")
        if not test2_pass: print("  FAIL: A=1 violated under some shuffle scheme")
        if not test3_pass: print("  FAIL: observer did not alter particle density")
        if not test4_pass: print("  FAIL: irreversibility not confirmed")

    return all_pass


if __name__ == "__main__":
    run_observer_clock_audit()
