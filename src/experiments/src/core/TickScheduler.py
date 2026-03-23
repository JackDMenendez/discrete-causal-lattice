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

        self.macro_tick += 1

    def _apply_pairwise_interactions(self, threshold: float = 1e-4):
        """
        When two sessions have significant amplitude at the same node,
        their phases are partially mixed -- clock entanglement.

        This is the mechanism of the observer effect: a detector session
        co-located with a particle session scrambles the particle's phase
        locally, which is what collapses the interference pattern.

        The mixing is proportional to the overlap amplitude.
        A=1 is preserved per session after mixing (re-normalize).
        """
        from .UnityConstraint import enforce_unity
        n = len(self.sessions)
        for i in range(n):
            for j in range(i+1, n):
                si = self.sessions[i]
                sj = self.sessions[j]
                # Find nodes where both sessions have significant amplitude
                abs_i = np.abs(si.psi)
                abs_j = np.abs(sj.psi)
                overlap_mask = (abs_i > threshold) & (abs_j > threshold)
                if not np.any(overlap_mask):
                    continue
                # Phase exchange: mix phases at overlap nodes
                # This represents the physical interaction (measurement)
                phase_i = np.angle(si.psi)
                phase_j = np.angle(sj.psi)
                # Small perturbation: each session's phase shifts by
                # a fraction of the other's phase (weak coupling)
                coupling = 0.1 * np.where(overlap_mask, 1.0, 0.0)
                new_phase_i = phase_i + coupling * (phase_j - phase_i)
                new_phase_j = phase_j + coupling * (phase_i - phase_j)
                si.psi = np.where(overlap_mask,
                                  abs_i * np.exp(1j * new_phase_i), si.psi)
                sj.psi = np.where(overlap_mask,
                                  abs_j * np.exp(1j * new_phase_j), sj.psi)
                enforce_unity(si.psi)
                enforce_unity(sj.psi)

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
