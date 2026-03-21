"""
exp_01_inertia.py
Audit: Inertia as U(1) phase-gradient persistence.

A CausalSession initialized with nonzero momentum (phase gradient)
should propagate in a straight line indefinitely on a flat lattice.
Deviation from straight-line propagation should require a potential gradient.

Expected result: packet center-of-mass moves at constant velocity.
Paper reference: Section 3 (inertia as phase gradient persistence)
Status: STUB
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession, TickScheduler, ShuffleScheme


def run_inertia_audit():
    print("--- EXPERIMENT 01: Inertia as Phase Gradient Persistence ---")

    # TODO: initialize session with nonzero momentum in x-direction
    # TODO: run on flat lattice (zero potential everywhere)
    # TODO: measure center-of-mass position each tick
    # TODO: verify linear trajectory to within unity_residual tolerance
    # TODO: visualize with visualizer.plot_spacetime_history()

    raise NotImplementedError


if __name__ == "__main__":
    run_inertia_audit()
