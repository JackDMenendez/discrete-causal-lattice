"""
src/core/__init__.py
The A=1 framework core modules.
"""

from .OctahedralLattice import (OctahedralLattice, RGB_VECTORS, CMY_VECTORS,
                                  ALL_VECTORS, SUBLATTICE_SIZE, COORDINATION_NUMBER,
                                  active_vectors, EVEN_TICK, ODD_TICK)
from .PhaseRotor import PhaseRotor
from .UnityConstraint import (enforce_unity, unity_residual, is_unity,
                               enforce_unity_spinor, unity_residual_spinor)
from .CausalSession import CausalSession
from .TickScheduler import TickScheduler, ShuffleScheme
