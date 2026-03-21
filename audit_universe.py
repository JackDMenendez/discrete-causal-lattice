"""
audit_universe.py
Master audit runner for the A=1 discrete causal lattice framework.

Runs all experiments in sequence and reports pass/fail status.
A row in the audit table (audit_table.tex) should only be marked
PASS when the corresponding experiment passes here.

Usage:
    python audit_universe.py           # run all experiments
    python audit_universe.py --list    # list experiments without running
"""

import sys
import traceback


EXPERIMENTS = [
    ("exp_00", "src.experiments.exp_00_causal_cone",       "run_causal_cone_audit"),
    ("exp_01", "src.experiments.exp_01_inertia",           "run_inertia_audit"),
    ("exp_02", "src.experiments.exp_02_gravity_clock_density", "run_gravity_clock_density_audit"),
    ("exp_03", "src.experiments.exp_03_interference",      "run_interference_audit"),
    ("exp_04", "src.experiments.exp_04_decoherence",       "run_decoherence_audit"),
    ("exp_05", "src.experiments.exp_05_observer_clock",    "run_observer_clock_audit"),
    ("exp_06", "src.experiments.exp_06_path_counting",     "run_path_counting_audit"),
]


def run_all():
    results = []
    print("=" * 60)
    print("A=1 DISCRETE CAUSAL LATTICE -- UNIVERSE AUDIT")
    print("=" * 60)

    for exp_id, module_path, function_name in EXPERIMENTS:
        print(f"\n[{exp_id}] {function_name}")
        try:
            import importlib
            module = importlib.import_module(module_path)
            func = getattr(module, function_name)
            func()
            results.append((exp_id, "PASS"))
            print(f"  --> PASS")
        except NotImplementedError:
            results.append((exp_id, "STUB"))
            print(f"  --> STUB (not yet implemented)")
        except Exception as e:
            results.append((exp_id, "FAIL"))
            print(f"  --> FAIL: {e}")
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("AUDIT SUMMARY")
    print("=" * 60)
    for exp_id, status in results:
        print(f"  {exp_id}  {status}")

    passed = sum(1 for _, s in results if s == "PASS")
    total  = len(results)
    print(f"\n{passed}/{total} experiments passing.")
    return passed == total


if __name__ == "__main__":
    if "--list" in sys.argv:
        for exp_id, _, fn in EXPERIMENTS:
            print(f"  {exp_id}  {fn}")
    else:
        success = run_all()
        sys.exit(0 if success else 1)
