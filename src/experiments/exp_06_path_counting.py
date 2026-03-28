"""
exp_06_path_counting.py
Audit: Discrete path count deviations from 1/r^2 -- the falsifiable prediction.

Generates specific numerical predictions that differ from standard QM/GR
at small hop counts, and converges to the continuous prediction at large N.

Paper reference: Section 9 (falsifiable predictions)
"""

import sys, os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utilities.path_counter import (
    count_paths, gaussian_prediction, discrete_correction, path_count_shell
)
from src.utilities.lattice_calibrator import (
    PLANCK_CALIBRATION, COMPTON_CALIBRATION, BOHR_CALIBRATION,
    print_calibration_table, SPEED_OF_LIGHT
)


def run_path_counting_audit():
    print("=" * 65)
    print("EXPERIMENT 06: Discrete Path Count -- Falsifiable Predictions")
    print("=" * 65)

    # ── Part 1: Verify count_paths against known values ──────────────
    print("\n[Part 1] Verifying exact path counts against known values...")

    known = [
        # (n_hops, dx, dy, dz, expected)
        (0, 0, 0, 0, 1),    # Origin: exactly 1 path
        (1, 1, 0, 0, 1),    # One hop right: exactly 1 path
        (1, 0, 0, 0, 0),    # Parity violation: 0 paths
        (2, 0, 0, 0, 6),    # Two hops, back to origin: 6 paths (+x-x, -x+x, +y-y, ...)
        (2, 2, 0, 0, 1),    # Two hops right: exactly 1 path
        (2, 1, 1, 0, 2),    # Two hops diagonal: 2 paths (+x+y or +y+x)
        (3, 1, 0, 0, 15),   # Three hops to (1,0,0): 15 paths
    ]

    all_passed = True
    for n, dx, dy, dz, expected in known:
        result = count_paths(n, dx, dy, dz)
        status = "PASS" if result == expected else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"  count_paths({n}, {dx}, {dy}, {dz}) = {result:6d}  "
              f"(expected {expected:6d})  [{status}]")

    # ── Part 2: Total path count verification (must equal 6^N) ───────
    print("\n[Part 2] Total paths from origin must equal 6^N...")
    for n in range(1, 7):
        shell = path_count_shell(n)
        total = sum(shell.values())
        expected_total = 6**n
        status = "PASS" if total == expected_total else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"  N={n}: total paths = {total:8d}, 6^N = {expected_total:8d}  [{status}]")

    # ── Part 3: Discrete corrections at small N ───────────────────────
    print("\n[Part 3] Discrete correction factors (the falsifiable prediction)...")
    print(f"\n  {'N hops':<8} {'count_paths(N,1,0,0)':<24} "
          f"{'Gaussian':<18} {'Correction %':<15} {'CLT regime?'}")
    print("  " + "-" * 75)

    crossover_n = None
    for n in range(1, 52, 2):
        exact  = count_paths(n, 1, 0, 0)
        if exact == 0:
            continue
        corr   = discrete_correction(n, 1, 0, 0) * 100
        in_clt = (n > 1) and abs(corr) < 1.0   # exclude N=1 trivial case
        if in_clt and crossover_n is None:
            crossover_n = n
        if n <= 19:   # print first 10 rows as before
            print(f"  {n:<8d} {exact:<24d} {gaussian_prediction(n,1,0,0):<18.6f} "
                  f"{corr:<+15.2f} {'YES' if in_clt else 'no'}")

    # ── Part 4: Physical scale of the crossover ───────────────────────
    print("\n[Part 4] Physical scale of discrete corrections by calibration...")
    print_calibration_table()

    if crossover_n is not None:
        print(f"\n  CLT crossover (correction < 1%) at N = {crossover_n} hops")
        print(f"\n  {'Calibration':<28} {'Crossover scale':<22} {'Experimental access'}")
        print("  " + "-" * 70)

        calibrations = [
            (PLANCK_CALIBRATION,  "optical clocks: ~1e-18 m"),
            (COMPTON_CALIBRATION, "hydrogen spectroscopy: ~1e-11 m"),
            (BOHR_CALIBRATION,    "atomic force microscopy: ~1e-10 m"),
        ]

        for cal, instrument in calibrations:
            scale = crossover_n * cal.node_spacing_m
            print(f"  {cal.name:<28} {scale:<22.3e} {instrument}")

    # ── Summary ───────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    if all_passed:
        print("[AUDIT PASSED] All path count verifications correct.")
        print("Discrete corrections are calculable and non-zero at small N.")
        print("These are genuine numerical predictions of the A=1 framework.")
    else:
        print("[AUDIT FAILED] Path count verification errors found.")

    return all_passed


if __name__ == "__main__":
    import sys
    sys.exit(0 if run_path_counting_audit() else 1)
