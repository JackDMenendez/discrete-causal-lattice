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
        self._emission_pairs = []   # [(electron_idx, photon_idx, rate), ...]
        self._emission_weights = {} # electron_idx -> current amplitude weight [0,1]

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
                              for (e, p, _) in self._emission_pairs}

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
                          rate: float = 0.003):
        """
        Register an electron-photon emission pair.

        Each macro-tick, a fraction `rate` of the electron's amplitude is
        transferred to the photon session.  The pair shares a joint A=1
        constraint: their combined amplitude is renormalized to 1 after
        each transfer.  This means amplitude genuinely moves from electron
        to photon (energy is transferred, not just phase information).

        The photon session should be initialized with a small seed amplitude
        (e.g. 1e-3) at the electron's starting location so enforce_unity_spinor
        does not divide by zero; the joint renormalization then sets the
        initial split correctly.

        Physical meaning: the electron decays by emitting a photon.  The
        photon's massless tick rule propagates the emitted amplitude away
        at c=1, removing it from the orbital region.  Over time the electron's
        remaining amplitude concentrates where emission is slowest -- the
        stable orbital radius.

        Parameters
        ----------
        electron_idx : session index (from register_session)
        photon_idx   : session index of the massless photon session
        rate         : amplitude fraction transferred per macro-tick
                       (~0.001 -- 0.01; larger = faster decay)
        """
        self._emission_pairs.append((electron_idx, photon_idx, float(rate)))
        self._emission_weights[electron_idx] = 1.0  # starts at full amplitude

    def emission_weight(self, electron_idx: int) -> float:
        """
        Current amplitude weight of an emission-coupled electron session.

        The electron's psi field stays A=1 at all times (its internal
        probability distribution is always normalized).  The weight tracks
        what fraction of the original amplitude the electron retains.
        It decays as (1 - rate)^tick, starting at 1.0.

        Use this weight when accumulating the electron PDF in experiments:
          weighted_density = electron.probability_density() * weight^2

        The weight^2 factor converts amplitude weight to probability weight,
        consistent with Born rule interpretation.
        """
        return self._emission_weights.get(electron_idx, 1.0)

    def _apply_emission_pairs(self):
        """
        Dissipative emission: decay the electron's effective amplitude weight
        by (1 - rate) each tick, and steer the photon session's phase toward
        the electron's current phase (so the photon carries the emitted
        phase information outward).

        The electron psi field remains A=1 throughout -- it always represents
        a valid probability distribution.  The weight tracks the fraction of
        the original amplitude the electron retains.  The photon accumulates
        the emitted phase field and propagates it outward at c=1.

        Physical picture: the electron's orbital phase imprints onto the
        photon field each tick.  The photon's massless bipartite tick then
        carries that phase away from the orbital region.  The electron's
        effective amplitude (weight) decays, modelling energy loss to radiation.
        Stable orbits lose amplitude slowly (coherent phase → constructive
        photon emission); unstable trajectories lose amplitude quickly.
        """
        for (e_idx, p_idx, rate) in self._emission_pairs:
            se = self.sessions[e_idx]
            sp = self.sessions[p_idx]

            # Decay the electron's amplitude weight
            self._emission_weights[e_idx] *= (1.0 - rate)

            # Imprint electron phase onto photon at every node where the
            # electron has significant amplitude.  The photon's own tick()
            # then propagates this phase outward.
            amp_e = np.sqrt(np.abs(se.psi_R)**2 + np.abs(se.psi_L)**2)
            mask  = amp_e > 1e-9
            if np.any(mask):
                # Mix photon phase toward electron phase at emission sites,
                # weighted by rate.  This is the phase imprint.
                phase_e_R = np.where(mask, np.angle(se.psi_R), 0.0)
                phase_p_R = np.where(mask, np.angle(sp.psi_R), 0.0)
                delta_phase = rate * (phase_e_R - phase_p_R)
                rot = np.where(mask, np.exp(1j * delta_phase), 1.0 + 0j)
                sp.psi_R = sp.psi_R * rot
                sp.psi_L = sp.psi_L * rot

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
