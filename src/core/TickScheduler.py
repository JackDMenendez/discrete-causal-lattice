"""
TickScheduler.py
The Combinatorial Clock Scheduler.

Each CausalSession carries its own independent tick counter.
The TickScheduler maintains the collection of all active session
tick counters and determines their processing order.

The shuffling of tick counters is the mechanism by which:
  - Relativity of simultaneity is modeled
  - The observer-as-clock is formalized
  - Particle decay becomes timing-dependent
  - Clock density encodes gravity

Paper reference: Section 4 (The Tick Scheduler)
"""

import numpy as np
import numpy as np
from typing import List, Callable
from enum import Enum


class ShuffleScheme(Enum):
    """
    Enumeration of available tick ordering schemes.
    Different schemes are experimental variables -- the physics
    should be invariant under reordering if the framework is correct.
    (If it isn't, that is also a meaningful result.)
    """
    SEQUENTIAL   = "sequential"    # Process in registration order
    RANDOM       = "random"        # Uniform random shuffle each macro-tick
    PRIORITY     = "priority"      # Process lowest tick counter first
    CLOCK_DENSITY = "clock_density" # Process highest-potential regions first


class TickScheduler:
    """
    Manages the tick counters of all active CausalSessions.

    The scheduler runs one macro-tick per call to advance().
    Each macro-tick: determines processing order, then calls
    session.tick() for each session in that order.

    An observer is simply a new CausalSession registered with
    the scheduler. Its tick counter joins the combinatorial space.
    Measurement is irreversible because tick counters cannot be
    removed once registered.

    Paper reference: Section 4 (observer as clock, irreversibility)
    """

    def __init__(self, shuffle_scheme: ShuffleScheme = ShuffleScheme.RANDOM):
        self.shuffle_scheme = shuffle_scheme
        self.sessions = []          # All registered CausalSessions
        self.macro_tick = 0         # The global scheduler cycle count
        self.rng = np.random.default_rng(seed=42)  # Reproducible audits
        self._bindings  = {}        # (i,j) -> coupling strength  (see bind_sessions)
        self._emission_pairs = []   # [(electron_idx, photon_idx, proton_idx, rate), ...]
        self._emission_weights = {} # electron_idx -> current amplitude weight [0,1]
        self._emission_grid = {}    # electron_idx -> precomputed (xx, yy, zz) node coords
        self.emission_diagnostics = {}  # electron_idx -> list of (tick, k_tang, ramp_std)

    def register_session(self, session) -> int:
        """
        Add a CausalSession to the scheduler.
        Returns the session's registration index.

        Adding an observer session changes the combinatorial clock space.
        This is the formal definition of measurement in the A=1 framework.
        """
        self.sessions.append(session)
        return len(self.sessions) - 1

    def _processing_order(self) -> List[int]:
        """
        Determines the order in which sessions are processed this macro-tick.
        The shuffle scheme is the experimental variable.
        """
        indices = list(range(len(self.sessions)))

        if self.shuffle_scheme == ShuffleScheme.SEQUENTIAL:
            return indices

        elif self.shuffle_scheme == ShuffleScheme.RANDOM:
            self.rng.shuffle(indices)
            return indices

        elif self.shuffle_scheme == ShuffleScheme.PRIORITY:
            # Process lowest tick counter first
            return sorted(indices, key=lambda i: self.sessions[i].tick_counter)

        elif self.shuffle_scheme == ShuffleScheme.CLOCK_DENSITY:
            # TODO: implement clock-density-weighted ordering
            raise NotImplementedError

        return indices

    def advance(self):
        """
        Execute one macro-tick: process all sessions in shuffle order.
        After propagation, apply pairwise interaction at shared nodes:
        sessions with overlapping amplitude exchange phase (entanglement).
        This is the formal mechanism by which observers affect particles.
        """
        order = self._processing_order()
        for i in order:
            session = self.sessions[i]
            session.tick()
            session.advance_tick_counter()

        # Pairwise interaction: sessions sharing a node exchange phase
        if len(self.sessions) > 1:
            self._apply_pairwise_interactions()

        # Emission coupling: transfer amplitude from source to photon session
        if self._emission_pairs:
            self._apply_emission_pairs()

        self.macro_tick += 1

    def _apply_pairwise_interactions(self, threshold: float = 1e-4):
        """
        When two sessions have significant amplitude at the same node,
        their phases are partially mixed -- clock entanglement.

        This is the mechanism of the observer effect: a detector session
        co-located with a particle session scrambles the particle's phase
        locally, which is what collapses the interference pattern.

        The mixing is proportional to the overlap amplitude.
        A=1 is preserved per session after mixing (re-normalize both spinor
        components jointly).

        Binding strength and composite particles
        ----------------------------------------
        The coupling coefficient (currently 0.1) controls how tightly two
        sessions are bound:
          coupling → 0:  free particles  (weak entanglement, observer effect)
          coupling → 1:  bound composite (sessions move as a unit)

        For a neutral composite (neutron, atom), constituent sessions should
        have coupling near 1 AND opposite rgb_cmy_imbalance so that their
        material cones partially cancel in the combined probability density.
        This cone cancellation is the lattice mechanism for why neutral
        composites behave more classically than their charged constituents.

        A future CompositeCausalSession class should encapsulate this:
        it wraps N sessions with specified coupling and computes the effective
        cone half-angle and charge balance of the composite.
        See notes/material_cone_and_composites.md.
        """
        from .UnityConstraint import enforce_unity_spinor
        # Build set of pairs that are emission-coupled -- skip pairwise phase
        # mixing for these, since emission is their explicit coupling mechanism.
        emission_pairs_set = {(min(e, p), max(e, p))
                              for (e, p, _pr, _r) in self._emission_pairs}

        n = len(self.sessions)
        for i in range(n):
            for j in range(i+1, n):
                if (min(i,j), max(i,j)) in emission_pairs_set:
                    continue
                si = self.sessions[i]
                sj = self.sessions[j]
                # Find nodes where both sessions have significant total amplitude
                amp_i = np.sqrt(np.abs(si.psi_R)**2 + np.abs(si.psi_L)**2)
                amp_j = np.sqrt(np.abs(sj.psi_R)**2 + np.abs(sj.psi_L)**2)
                overlap_mask = (amp_i > threshold) & (amp_j > threshold)
                if not np.any(overlap_mask):
                    continue
                # Phase exchange: mix phases at overlap nodes using psi_R as
                # the phase reference (same rotation applied to both components)
                phase_i = np.angle(si.psi_R)
                phase_j = np.angle(sj.psi_R)
                key = (min(i, j), max(i, j))
                coupling_strength = self._bindings.get(key, 0.1)
                coupling = coupling_strength * np.where(overlap_mask, 1.0, 0.0)
                new_phase_i = phase_i + coupling * (phase_j - phase_i)
                new_phase_j = phase_j + coupling * (phase_i - phase_j)
                phase_rot_i = np.where(overlap_mask,
                                       np.exp(1j * (new_phase_i - phase_i)), 1.0+0j)
                phase_rot_j = np.where(overlap_mask,
                                       np.exp(1j * (new_phase_j - phase_j)), 1.0+0j)
                si.psi_R = si.psi_R * phase_rot_i
                si.psi_L = si.psi_L * phase_rot_i
                sj.psi_R = sj.psi_R * phase_rot_j
                sj.psi_L = sj.psi_L * phase_rot_j
                enforce_unity_spinor(si.psi_R, si.psi_L)
                enforce_unity_spinor(sj.psi_R, sj.psi_L)

    def register_emission(self, electron_idx: int, photon_idx: int,
                          proton_idx: int,
                          rate: float = 0.003):
        """
        Register an electron-photon emission pair coupled to a live proton session.

        Each macro-tick the electron loses tangential phase gradient to the
        photon session.  The drain targets only the tangential (orbital) component
        of the electron's phase gradient -- the radial component is preserved so
        the Coulomb attraction continues to act unimpeded.

        The proton session (not a fixed well) is required: exp_12 showed that a
        fixed Coulomb well shifts the N=1 orbital radius by 7.3%.  The proton's
        centre-of-mass is recomputed from its current probability density each
        tick, so the radial geometry tracks nuclear recoil correctly.

        Physical mechanism (radiation reaction):
          1. Compute the proton CoM from its current probability_density().
          2. Compute ∇φ of the electron via phase_gradient_field().
          3. Remove the radial projection (relative to live proton CoM) to
             isolate the tangential gradient.
          4. Compute the orbital plane normal L_hat = ∫(r × ∇φ)·dens dV
             from the electron's current angular momentum -- fully dynamic,
             no hard-coded orbital plane.
          5. Project onto the azimuthal direction φ_hat at each node for a
             signed scalar drain field.
          6. Apply -rate·drain to the electron via apply_phase_map (unitary,
             NOT undone by enforce_unity_spinor which only normalises |psi|²).
          7. Apply +rate·drain to the photon -- massless tick propagates it
             outward at c=1.

        Parameters
        ----------
        electron_idx : session index (from register_session)
        photon_idx   : session index of the massless photon session
        proton_idx   : session index of the nucleus CausalSession
        rate         : tangential phase drain per macro-tick (0.001 -- 0.01)
        """
        self._emission_pairs.append(
            (electron_idx, photon_idx, proton_idx, float(rate)))
        self._emission_weights[electron_idx] = 1.0

        # Precompute node coordinate grids (fixed for the lifetime of the session).
        se = self.sessions[electron_idx]
        n = se.lattice.size_x
        x = np.arange(n)
        xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
        self._emission_grid[electron_idx] = (xx.astype(float),
                                             yy.astype(float),
                                             zz.astype(float))

    def emission_weight(self, electron_idx: int) -> float:
        """Current bookkeeping weight for an emission-coupled electron (legacy)."""
        return self._emission_weights.get(electron_idx, 1.0)

    def _apply_emission_pairs(self):
        """
        Directional tangential phase drain: radiation reaction.

        For each emission pair, drains the electron's orbital (tangential)
        phase gradient and deposits it onto the photon.  The proton CoM is
        recomputed each tick so nuclear recoil is tracked correctly.  The
        orbital plane normal is computed dynamically from the electron's
        angular momentum -- no hard-coded directions.
        """
        for (e_idx, p_idx, pr_idx, rate) in self._emission_pairs:
            se  = self.sessions[e_idx]
            sp  = self.sessions[p_idx]
            spr = self.sessions[pr_idx]

            grad = se.phase_gradient_field()   # (3, X, Y, Z)
            dens = se.probability_density()    # (X, Y, Z)

            # Live proton CoM -- recomputed every tick to track recoil
            pr_dens = spr.probability_density()
            pr_total = float(pr_dens.sum())
            xx, yy, zz = self._emission_grid[e_idx]
            if pr_total > 1e-12:
                cx = float(np.sum(xx * pr_dens) / pr_total)
                cy = float(np.sum(yy * pr_dens) / pr_total)
                cz = float(np.sum(zz * pr_dens) / pr_total)
            else:
                cx = float(xx.mean())
                cy = float(yy.mean())
                cz = float(zz.mean())

            # Radial vectors relative to live proton CoM
            rx = xx - cx;  ry = yy - cy;  rz = zz - cz
            r_mag  = np.sqrt(rx**2 + ry**2 + rz**2)
            r_safe = np.where(r_mag > 0.5, r_mag, 1.0)
            r_hat  = np.stack([rx / r_safe, ry / r_safe, rz / r_safe])
            r_vec  = np.stack([rx, ry, rz])

            # Tangential gradient: remove radial projection
            grad_rad  = np.sum(grad * r_hat, axis=0)
            grad_tang = grad - grad_rad[np.newaxis] * r_hat

            # Orbital plane normal from current angular momentum:
            # L = integral of (r × ∇φ) * dens over the grid.
            L_field = np.stack([
                r_vec[1] * grad[2] - r_vec[2] * grad[1],
                r_vec[2] * grad[0] - r_vec[0] * grad[2],
                r_vec[0] * grad[1] - r_vec[1] * grad[0],
            ])
            L_vec = np.einsum('ixyz,xyz->i', L_field, dens)
            L_mag = float(np.sqrt(np.sum(L_vec**2)))
            if L_mag < 1e-10:
                continue   # no angular momentum -- nothing to drain

            L_hat = L_vec / L_mag

            # Azimuthal unit vector at each node: φ_hat = L_hat × r_hat
            phi_hat = np.stack([
                L_hat[1] * r_hat[2] - L_hat[2] * r_hat[1],
                L_hat[2] * r_hat[0] - L_hat[0] * r_hat[2],
                L_hat[0] * r_hat[1] - L_hat[1] * r_hat[0],
            ])
            phi_mag  = np.sqrt(np.sum(phi_hat**2, axis=0))
            phi_safe = np.where(phi_mag > 1e-9, phi_mag, 1.0)
            phi_hat  = phi_hat / phi_safe[np.newaxis]

            # Density-weighted mean tangential momentum k_tang.
            tang_scalar = np.sum(grad_tang * phi_hat, axis=0)   # (X,Y,Z)
            dens_total  = float(dens.sum())
            if dens_total < 1e-12:
                continue
            k_tang = float(np.sum(tang_scalar * dens)) / dens_total

            # Azimuthal arc-length coordinate in the orbital plane.
            #
            # phi_hat = L_hat × r_hat is perpendicular to r_hat by construction,
            # so r_vec · phi_hat = 0 identically -- wrong for a phase ramp.
            # We need the arc-length coordinate s = r_mag * theta, where theta
            # is the azimuthal angle measured from a fixed in-plane reference.
            #
            # Build an orthonormal frame (e1, e2) in the orbital plane:
            #   e1 = any in-plane direction not parallel to L_hat
            #   e2 = L_hat × e1  (= phi direction at theta=0)
            # Then theta = arctan2(r·e2, r·e1) and s = r_mag * theta.
            # The gradient of s in the phi direction is 1 (correct units: 1/node).
            e1 = np.array([1., 0., 0.])
            if abs(float(np.dot(L_hat, e1))) > 0.9:
                e1 = np.array([0., 1., 0.])
            e1 = e1 - float(np.dot(L_hat, e1)) * L_hat
            e1_norm = float(np.linalg.norm(e1))
            if e1_norm < 1e-10:
                continue
            e1 = e1 / e1_norm
            e2 = np.cross(L_hat, e1)           # second in-plane axis

            x_orb = np.einsum('i,ixyz->xyz', e1, r_vec)   # (X,Y,Z)
            y_orb = np.einsum('i,ixyz->xyz', e2, r_vec)   # (X,Y,Z)
            theta  = np.arctan2(y_orb, x_orb)             # azimuthal angle
            # Arc-length s = r_mag * theta; gradient ds/d(phi) = 1 node
            arc_length = r_mag * theta                     # (X,Y,Z)

            # Phase ramp: reduces tangential wavevector by rate * k_tang.
            # d(phase_ramp)/ds = -rate * k_tang, so kinetic_hop sees
            # delta_p reduced by rate * k_tang in the phi direction.
            phase_ramp = -rate * k_tang * arc_length

            se.apply_phase_map(phase_ramp)    # reduce tangential momentum
            sp.apply_phase_map(-phase_ramp)   # photon carries it away

            # Diagnostics: record k_tang and ramp variation each tick
            if e_idx not in self.emission_diagnostics:
                self.emission_diagnostics[e_idx] = []
            self.emission_diagnostics[e_idx].append(
                (self.macro_tick, float(k_tang), float(phase_ramp.std())))

    def bind_sessions(self, i: int, j: int, coupling: float = 0.9):
        """
        Register a persistent coupling strength between two sessions.

        This controls how tightly two sessions' phases are mixed each macro-tick
        in _apply_pairwise_interactions:

          coupling = 0.0   no interaction          (free particles)
          coupling = 0.1   weak interaction        (default observer/decoherence)
          coupling = 0.9   strong binding          (composite particle constituents)
          coupling = 1.0   perfect phase lock      (fully bound, move as one unit)

        Binding is the mechanism for composite particles.  Two sessions bound
        with coupling → 1 evolve as a unit: their phases lock, their cones
        interfere coherently, and for a neutral pair (opposite rgb_cmy_imbalance)
        their phase gradients cancel — producing a narrower effective cone.

        The phase cancellation (not amplitude cancellation) is what narrows the
        effective material cone of a neutral composite.
        See notes/material_cone_and_composites.md and cone_modification_classes.md.

        Parameters
        ----------
        i, j     : session indices (from register_session)
        coupling : float in [0, 1]
        """
        key = (min(i, j), max(i, j))
        self._bindings[key] = float(np.clip(coupling, 0.0, 1.0))

    def clock_count(self) -> int:
        """Returns the total number of active clocks in the scheduler."""
        return len(self.sessions)

    def combinatorial_state_space_size(self) -> int:
        """
        The number of distinct tick orderings possible given current sessions.
        This grows as clock_count! -- the arrow of time.
        Paper reference: Section 4 (entropy as clock count growth)
        """
        import math
        return math.factorial(self.clock_count())
