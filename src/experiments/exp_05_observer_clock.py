"""
exp_05_observer_clock.py
Audit: Observer as clock -- different observers, different outcomes.

Two observer sessions are registered with different ShuffleSchemes.
The experiment verifies that the combinatorial clock ordering
determines the observed quantum outcome, and that adding observers
is irreversible (entropy increases monotonically with clock count).

Paper reference: Section 8 (observer as clock, irreversibility)
Status: STUB
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.core import OctahedralLattice, CausalSession, TickScheduler, ShuffleScheme


def run_observer_clock_audit():
    print("--- EXPERIMENT 05: Observer as Clock ---")

    # TODO: initialize identical particle sessions
    # TODO: register observer A with RANDOM shuffle
    # TODO: register observer B with PRIORITY shuffle
    # TODO: run both schedulers from identical initial conditions
    # TODO: compare observed outcomes -- do different clock orderings
    #       produce different local measurement results?
    # TODO: verify that combinatorial_state_space_size() grows
    #       monotonically as sessions are added (arrow of time)
    # TODO: attempt to "un-add" an observer -- verify irreversibility

    raise NotImplementedError


if __name__ == "__main__":
    run_observer_clock_audit()
