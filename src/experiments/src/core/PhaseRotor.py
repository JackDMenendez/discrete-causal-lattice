"""
PhaseRotor.py
The U(1) Internal Clock: the particle's phase state keeper.

The PhaseRotor is the internal oscillator of a CausalSession.
Its frequency omega is the particle's instruction overhead -- rest mass.
Its current phase encodes the particle's internal time coordinate.

A high-frequency rotor (heavy particle) has high phase stability:
it resists redirection (inertia). A low-frequency rotor (light particle)
is easily scattered by minor potential gradients.

Paper reference: Section 3 (Phase Rotor, mass as instruction overhead)
"""

import numpy as np


class PhaseRotor:
    """
    U(1) internal clock for a CausalSession.

    The rotor lives on the complex unit circle: r = 1 always (A=1).
    Phase advances by omega at every tick.
    """

    def __init__(self, frequency: float):
        """
        Parameters
        ----------
        frequency : omega -- instruction overhead, encoding rest mass.
                    Higher omega = heavier particle = greater phase stability.
        """
        self.omega = frequency          # Instruction frequency (rest mass)
        self.phase = 0.0                # Current phase angle (radians)

    @property
    def amplitude(self) -> complex:
        """
        The rotor state as a unit complex number.
        Always on the unit circle: |amplitude| = 1 (enforces A=1 locally).
        """
        return np.exp(1j * self.phase)

    def advance(self):
        """
        Advance the rotor by one tick.
        Phase increments by omega, wrapping at 2*pi.
        """
        self.phase = (self.phase + self.omega) % (2 * np.pi)

    def phase_cost(self, local_potential: float) -> float:
        """
        The discrete Hamiltonian evaluated at a node:
        H(x,y,z) = omega + V(x,y,z)

        This is the phase transition cost for hopping into a node
        with topological potential V(x,y,z).

        Paper reference: Section 5 (discrete Hamiltonian as phase routing matrix)
        """
        return self.omega + local_potential

    def phase_shift(self, local_potential: float) -> complex:
        """
        Returns the unitary phase factor for a hop into a node
        with the given local potential.
        exp(i * H(x,y,z))
        """
        return np.exp(1j * self.phase_cost(local_potential))
