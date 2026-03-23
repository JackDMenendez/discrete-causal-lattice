"""
exp_00_causal_cone.py
Audit: The speed limit and causal structure of T^3_diamond.

Demonstrates that the maximum propagation speed on the octahedral
lattice is exactly 1 node/tick -- the topological unity of causality.
The causal cone expands as an octahedron, not a sphere.

Expected result: no amplitude outside the octahedral causal boundary.
Paper reference: Section 2 (emergence of c, discrete lightcone)
"""

import sys, os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession, enforce_unity, is_unity
from src.utilities.lattice_calibrator import PLANCK_CALIBRATION, print_calibration_table


def run_causal_cone_audit():
    print("--- EXPERIMENT 00: Causal Cone and Speed Limit ---")
    print_calibration_table()

    grid_size   = 30        # Small grid: cone audit doesn't need large space
    n_ticks     = 10        # Run 10 ticks; cone radius must stay <= 10
    center      = (15, 15, 15)
    frequency   = 0.1       # Low instruction overhead

    lattice = OctahedralLattice(grid_size, grid_size, grid_size)

    # Initialize a point source: all amplitude at the center node (A=1)
    session = CausalSession(
        lattice=lattice,
        initial_node=center,
        instruction_frequency=frequency
    )

    print(f"\nInitial state: point source at {center}, unity residual = "
          f"{1.0 - np.sum(session.probability_density()):.2e}")

    # Run ticks and verify causal cone at each step
    violations = 0
    for t in range(1, n_ticks + 1):
        session.tick()
        session.advance_tick_counter()

        density = session.probability_density()

        # The causal cone at tick t: all nodes within Manhattan distance t
        reachable = set(lattice.causal_cone_nodes(center, t))

        # Check for amplitude OUTSIDE the causal cone
        for x in range(grid_size):
            for y in range(grid_size):
                for z in range(grid_size):
                    if density[x, y, z] > 1e-10:
                        if (x, y, z) not in reachable:
                            violations += 1
                            print(f"  VIOLATION at tick {t}: "
                                  f"node ({x},{y},{z}) outside cone, "
                                  f"density = {density[x,y,z]:.4e}")

        total_prob = np.sum(density)
        print(f"  Tick {t:2d}: total probability = {total_prob:.8f}, "
              f"reachable nodes = {len(reachable)}, "
              f"active nodes = {np.sum(density > 1e-10)}")

    print(f"\nCausal violations found: {violations}")

    if violations == 0:
        print("\n[AUDIT PASSED] Causal cone respected -- speed limit c=1 confirmed.")
        print("No amplitude propagated faster than 1 node/tick.")
        print("The causal cone expands as an octahedron, not a sphere.")
    else:
        print(f"\n[AUDIT FAILED] {violations} causal violations detected.")

    return violations == 0


if __name__ == "__main__":
    run_causal_cone_audit()
