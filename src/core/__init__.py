"""
src/core/__init__.py
The A=1 framework core modules.
"""

from .OctahedralLattice import OctahedralLattice, OCTAHEDRAL_DIRECTIONS, COORDINATION_NUMBER
from .PhaseRotor import PhaseRotor
from .UnityConstraint import enforce_unity, unity_residual, is_unity
from .CausalSession import CausalSession
from .TickScheduler import TickScheduler, ShuffleScheme
