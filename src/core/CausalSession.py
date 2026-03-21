"""
CausalSession.py
The Quantum Lantern: a particle as a persistent probability flux.

A CausalSession is the A=1 representation of a particle.
It is not a point; it is a distributed complex amplitude navigating
the OctahedralLattice via unitary tick updates.

The session carries:
  - A complex amplitude field psi(x,y,z): the wave function
  - A PhaseRotor: the internal U(1) clock (mass / instruction frequency)
  - A TickCounter: the session's own discrete time coordinate

Paper reference: Section 3 (Causal Sessions and the Phase Rotor)
"""

import numpy as np
from typing import Tuple
from .OctahedralLattice import OctahedralLattice, COORDINATION_NUMBER
from .PhaseRotor import PhaseRotor
from .UnityConstraint import enforce_unity


class CausalSession:
    """
    A particle as a persistent causal session on T^3_diamond.

    The amplitude field psi is complex. Phase must survive to the
    summation step. |psi|^2 is taken AFTER neighbor summation,
    not before. This is what makes interference possible.
    """

    def __init__(self,
                 lattice: OctahedralLattice,
                 initial_node: Tuple[int, int, int],
                 instruction_frequency: float,
                 momentum: Tuple[float, float, float] = (0.0, 0.0, 0.0)):
        """
        Parameters
        ----------
        lattice               : The substrate T^3_diamond
        initial_node          : Starting causal event (x, y, z)
        instruction_frequency : omega -- the internal clock rate, encoding rest mass
        momentum              : Initial phase gradient encoding velocity direction
        """
        self.lattice = lattice
        self.phase_rotor = PhaseRotor(frequency=instruction_frequency)
        self.tick_counter = 0

        # The wave function: complex amplitude at every lattice node
        self.psi = np.zeros(
            (lattice.size_x, lattice.size_y, lattice.size_z),
            dtype=complex
        )

        # Initialize at the starting node with unity amplitude (A=1)
        x0, y0, z0 = initial_node
        self.psi[x0, y0, z0] = 1.0 + 0j

        # Encode initial momentum as a phase gradient across the packet
        if any(p != 0.0 for p in momentum):
            self._apply_initial_momentum(initial_node, momentum)

        enforce_unity(self.psi)

    def _apply_initial_momentum(self,
                                 center: Tuple[int, int, int],
                                 momentum: Tuple[float, float, float]):
        """
        Stamps the initial momentum as a phase gradient across the packet.
        A particle at rest has uniform phase; a moving particle has a
        phase gradient in the direction of motion.

        For a Gaussian packet centered at (x0,y0,z0) with momentum (kx,ky,kz):
            psi(x,y,z) = envelope(x,y,z) * exp(i*(kx*x + ky*y + kz*z))

        Paper reference: Section 3 (phase gradient as momentum)
        """
        kx, ky, kz = momentum
        size_x, size_y, size_z = self.lattice.size_x, self.lattice.size_y, self.lattice.size_z
        for x in range(size_x):
            for y in range(size_y):
                for z in range(size_z):
                    if np.abs(self.psi[x, y, z]) > 1e-12:
                        self.psi[x, y, z] *= np.exp(1j * (kx*x + ky*y + kz*z))

    def hop_probability_distribution(self, node: Tuple[int, int, int]) -> dict:
        """
        Returns the probability weight for each neighbor of node.

        At rest (zero phase gradient): 1/COORDINATION_NUMBER to each neighbor.
        In motion: asymmetric distribution -- neighbors in the direction of
        the phase gradient receive higher weight.
        Stay-put probability: 1 - sum(neighbor_weights), models thermal rest.

        Paper reference: Section 3 (hop probability, temperature analogy)
        """
        neighbors = self.lattice.topological_neighbors(node)
        x, y, z = node
        current_phase = np.angle(self.psi[x, y, z])

        weights = {}
        for nx, ny, nz in neighbors:
            neighbor_phase = np.angle(self.psi[nx, ny, nz]) if np.abs(self.psi[nx, ny, nz]) > 1e-12 else 0.0
            # Weight by phase alignment: neighbors in-phase get higher weight
            phase_alignment = np.cos(neighbor_phase - current_phase)
            weights[(nx, ny, nz)] = max(0.0, phase_alignment)

        total = sum(weights.values())
        if total < 1e-12:
            # No phase gradient -- uniform distribution (particle at rest)
            uniform = 1.0 / COORDINATION_NUMBER
            return {n: uniform for n in neighbors}

        # Normalize so weights sum to 1
        return {n: w / total for n, w in weights.items()}

    def tick(self):
        """
        The unitary update cycle: advance the session by one causal step.

        Implements Huygens' Lantern in 3D on the octahedral lattice:

          For each active node (x,y,z):
            1. Compute phase transition cost: H(x,y,z) = omega + V(x,y,z)
            2. Emit phase-rotated amplitude to each of the 6 neighbors
               delta_psi[neighbor] += psi[x,y,z] * exp(i * H(x,y,z)) / n_neighbors

          All emissions are accumulated simultaneously (the causal tick).
          Then enforce A=1 (unity constraint).

        This is genuine discrete propagation -- no sqrt() distances,
        no continuous Huygens-Fresnel formula. Interference emerges
        from complex amplitude summation at nodes receiving contributions
        from multiple source nodes.

        |psi|^2 is taken AFTER summation -- this is what makes
        interference possible (signed complex cancellation).

        Paper reference: Section 5 (Phase Propagation, Huygens Lantern)
        """
        size_x = self.lattice.size_x
        size_y = self.lattice.size_y
        size_z = self.lattice.size_z

        # New amplitude field -- all updates are simultaneous (causal tick)
        new_psi = np.zeros((size_x, size_y, size_z), dtype=complex)

        # Threshold: skip nodes with negligible amplitude for efficiency
        active_threshold = 1e-9

        for x in range(size_x):
            for y in range(size_y):
                for z in range(size_z):
                    amp = self.psi[x, y, z]
                    if np.abs(amp) < active_threshold:
                        continue

                    # Discrete Hamiltonian: phase routing cost at this node
                    # H(x,y,z) = instruction_frequency (omega) + clock_density V(x,y,z)
                    phase_cost = self.phase_rotor.phase_cost(
                        self.lattice.clock_density_at((x, y, z))
                    )
                    phase_factor = np.exp(1j * phase_cost)

                    # Emit to all valid causal neighbors
                    neighbors = self.lattice.topological_neighbors((x, y, z))
                    n_neighbors = len(neighbors)

                    if n_neighbors == 0:
                        continue

                    # Each neighbor receives an equal share of the phase-rotated amplitude
                    # This enforces the 1/COORDINATION_NUMBER rest distribution
                    emission = amp * phase_factor / n_neighbors

                    for nx, ny, nz in neighbors:
                        new_psi[nx, ny, nz] += emission

        # Enforce A=1: probability is conserved across the tick
        enforce_unity(new_psi)
        self.psi = new_psi

    def probability_density(self) -> np.ndarray:
        """
        Returns |psi|^2: the observable probability density.
        This is computed AFTER phase summation, not from densities directly.
        """
        return np.abs(self.psi) ** 2

    def advance_tick_counter(self):
        """Increments the session's own tick counter."""
        self.tick_counter += 1
        self.phase_rotor.advance()
