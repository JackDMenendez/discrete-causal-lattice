"""
CausalSession.py
The Quantum Lantern: a particle as a persistent probability flux.

The bipartite Zitterbewegung model:

  A PHOTON (delta_phi = 0):
    - p_stay = sin^2(0/2) = 0    -- never stays
    - p_move = cos^2(0/2) = 1    -- always moves
    - Sees only the 3 active sublattice vectors per tick
    - Strictly chiral, moves at c=1 always

  A MASSIVE PARTICLE (delta_phi != 0):
    - p_stay = sin^2(delta_phi/2) > 0   -- sometimes stays (mass/Zitterbewegung)
    - p_move = cos^2(delta_phi/2) / 3   -- distributes to 3 active neighbors
    - BUT: by staying, it is present for BOTH even and odd ticks
    - Therefore it blurs across both sublattices -- sees all 6 vectors
    - This blur IS the superposition of left/right-handed states
    - delta_phi = omega * dt: the internal clock mismatch with the vacuum

  MOMENTUM:
    - A bias in the distribution across the 3 active vectors
    - Encoded as a phase gradient: one vector gets more weight than others
    - Constant bias = constant velocity (Newton 1)

  ACCELERATION:
    - A spatially-varying phase field (gravity or EM) shifts delta_phi
      differently across the wavefront
    - Differential Zitterbewegung across the wavefront steers the packet
    - No force vector needed -- just grad(delta_phi)

  INERTIA (corrected from earlier implementation):
    - High omega = large delta_phi per tick = strong Zitterbewegung
    - Strong Zitterbewegung = more time spent at nucleus = harder to accelerate
    - omega appears in DENOMINATOR of momentum response (see tick())

Paper reference: Section 3 (Causal Sessions, Zitterbewegung, Mass)
"""

import numpy as np
from typing import Tuple
from .OctahedralLattice import (OctahedralLattice, COORDINATION_NUMBER,
                                 SUBLATTICE_SIZE, active_vectors, ALL_VECTORS)
from .PhaseRotor import PhaseRotor
from .UnityConstraint import enforce_unity


class CausalSession:
    """
    A particle as a persistent causal session on T^3_diamond.

    The is_massless flag determines which tick rule applies:
      True  -> photon: bipartite, p_stay=0, sees 3 vectors
      False -> massive: blurred sublattice, p_stay=sin^2(delta_phi/2)
    """

    def __init__(self,
                 lattice: OctahedralLattice,
                 initial_node: Tuple[int, int, int],
                 instruction_frequency: float,
                 momentum: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                 is_massless: bool = False):
        self.lattice          = lattice
        self.phase_rotor      = PhaseRotor(frequency=instruction_frequency)
        self.tick_counter     = 0
        self.is_massless      = is_massless

        self.psi = np.zeros(
            (lattice.size_x, lattice.size_y, lattice.size_z),
            dtype=complex
        )
        x0, y0, z0 = initial_node
        self.psi[x0, y0, z0] = 1.0 + 0j

        if any(p != 0.0 for p in momentum):
            self._apply_initial_momentum(initial_node, momentum)

        enforce_unity(self.psi)

    def _apply_initial_momentum(self, center, momentum):
        """
        Momentum = phase gradient across the packet.
        The gradient biases the 3-way distribution within each sublattice,
        giving a net drift in the gradient direction.
        """
        kx, ky, kz = momentum
        for x in range(self.lattice.size_x):
            for y in range(self.lattice.size_y):
                for z in range(self.lattice.size_z):
                    if np.abs(self.psi[x, y, z]) > 1e-12:
                        self.psi[x, y, z] *= np.exp(
                            1j * (kx*x + ky*y + kz*z)
                        )

    # ── The core Zitterbewegung amplitude kernel ──────────────────────────────

    @staticmethod
    def zitterbewegung_amplitudes(delta_phi: float) -> Tuple[float, float]:
        """
        Given the phase mismatch delta_phi between the particle's internal
        clock and the vacuum clock, returns:
          p_stay : residence probability  = sin^2(delta_phi / 2)
          p_move : total outgoing probability = cos^2(delta_phi / 2)

        p_stay + p_move = 1  (A=1 conservation)

        For a massless particle: delta_phi = 0 -> p_stay=0, p_move=1
        For maximum mass:        delta_phi = pi -> p_stay=1, p_move=0

        Paper reference: Section 3 (Zitterbewegung kernel, mass from phase mismatch)
        """
        p_stay = np.sin(delta_phi / 2.0) ** 2
        p_move = np.cos(delta_phi / 2.0) ** 2   # = 1 - p_stay
        return p_stay, p_move

    def _delta_phi_at(self, node: Tuple[int, int, int]) -> float:
        """
        Phase mismatch between the particle's internal clock and the
        local vacuum clock (including gravitational and EM contributions).

        delta_phi = omega * dt + V(x,y,z) + A_dot_k

        The gravitational potential V slows the local vacuum clock.
        The EM vector potential A adds a directional phase twist.
        Their sum is the total phase mismatch that determines p_stay.

        Paper reference: Section 8 (unified phase field equation)
        """
        x, y, z = node
        # Base phase mismatch from internal frequency
        base = self.phase_rotor.omega

        # Gravitational contribution (scalar -- clock density)
        grav = self.lattice.clock_density_at(node)

        # EM contribution (vector dot momentum direction)
        # A . k: vector potential projected onto momentum
        A    = self.lattice.vector_potential_at(node)
        k    = np.array([np.real(self.psi[x,y,z]),
                         np.imag(self.psi[x,y,z]), 0.0])
        em   = np.dot(A, k) if np.linalg.norm(k) > 1e-12 else 0.0

        return base + grav + em

    def tick(self):
        """
        The bipartite unitary update cycle -- vectorized implementation.

        For each node: amplitude is split between residence (p_stay)
        and emission to neighbors (p_move), weighted by phase alignment.
        All updates are simultaneous (causal tick). A=1 enforced after.

        Paper reference: Section 3 & 5 (Zitterbewegung tick, bipartite rule)
        """
        tick_parity = self.tick_counter % 2

        # ── Per-node delta_phi and Zitterbewegung amplitudes ──────────
        # delta_phi = omega + V(x,y,z)   (EM contribution simplified for now)
        delta_phi = (self.phase_rotor.omega
                     + self.lattice.topological_potential)       # shape: (X,Y,Z)

        p_stay  = np.sin(delta_phi / 2.0) ** 2                  # shape: (X,Y,Z)
        p_move  = np.cos(delta_phi / 2.0) ** 2                  # shape: (X,Y,Z)
        phase_factor = np.exp(1j * delta_phi)                    # shape: (X,Y,Z)

        # ── Residence: amplitude stays at nucleus ─────────────────────
        new_psi = self.psi * np.sqrt(p_stay)

        # ── Movement: distribute to active neighbors ──────────────────
        if self.is_massless:
            vectors = active_vectors(tick_parity)
        else:
            vectors = ALL_VECTORS

        n_vec = len(vectors)

        # For each neighbor direction, compute phase-alignment weight
        # and accumulate emission into new_psi
        # Weight: cos(neighbor_phase - local_phase) / (1 + omega)
        # (inertia: heavy particles less responsive to gradient)

        local_phase = np.angle(self.psi)          # (X,Y,Z)
        amp_abs     = np.abs(self.psi)            # (X,Y,Z)
        active_mask = amp_abs > 1e-9

        # Compute weights for each direction
        weights = np.zeros((n_vec,) + self.psi.shape, dtype=float)
        for i, (dx, dy, dz) in enumerate(vectors):
            neighbor_psi   = np.roll(np.roll(np.roll(
                self.psi, -dx, axis=0), -dy, axis=1), -dz, axis=2)
            neighbor_abs   = np.abs(neighbor_psi)
            neighbor_phase = np.where(neighbor_abs > 1e-9,
                                      np.angle(neighbor_psi), local_phase)
            delta_p = neighbor_phase - local_phase
            bias    = np.cos(delta_p) / (1.0 + self.phase_rotor.omega)
            weights[i] = np.maximum(0.0, bias)

        # Normalize weights across directions (per node)
        total_w = weights.sum(axis=0)                             # (X,Y,Z)
        uniform = 1.0 / n_vec
        # Where total_w is near zero: use uniform distribution
        total_w = np.where(total_w < 1e-12, 1.0, total_w)
        weights = np.where(weights.sum(axis=0, keepdims=True) < 1e-12,
                           uniform, weights / total_w[np.newaxis])

        # Emit weighted, phase-rotated amplitude to each neighbor
        # Use masked roll to prevent wrap-around at boundaries
        sqrt_p_move = np.sqrt(p_move)
        sx, sy, sz  = self.psi.shape
        for i, (dx, dy, dz) in enumerate(vectors):
            emission = self.psi * phase_factor * sqrt_p_move * weights[i]

            # Build boundary mask: zero out emission that would wrap
            mask = np.ones((sx, sy, sz), dtype=bool)
            if dx > 0: mask[sx-dx:, :, :]  = False
            if dx < 0: mask[:-dx,   :, :]  = False   # -dx is positive
            if dy > 0: mask[:, sy-dy:, :]  = False
            if dy < 0: mask[:, :-dy,   :]  = False
            if dz > 0: mask[:, :, sz-dz:]  = False
            if dz < 0: mask[:, :, :-dz  ]  = False
            emission = np.where(mask, emission, 0.0)

            new_psi += np.roll(np.roll(np.roll(
                emission, dx, axis=0), dy, axis=1), dz, axis=2)

        enforce_unity(new_psi)
        self.psi = new_psi

    def probability_density(self) -> np.ndarray:
        return np.abs(self.psi) ** 2

    def advance_tick_counter(self):
        self.tick_counter += 1
        self.phase_rotor.advance()
