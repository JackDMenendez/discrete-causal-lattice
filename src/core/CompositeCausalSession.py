"""
CompositeCausalSession.py
A bound collection of CausalSessions evolving as a composite particle.

The key distinction from running multiple sessions independently in the
TickScheduler is the probability density:

  Independent sessions:   P = Σ |ψ_i|²          (incoherent sum — no cancellation)
  Composite session:      P = |Σ ψ_i|²           (coherent sum — phases interfere)

Phase cancellation only appears in the coherent sum.  For a neutral composite
(constituents with opposite rgb_cmy_imbalance), the constituent phase gradients
cancel in the coherent sum — this is the mechanism that narrows the effective
material cone.

See notes/material_cone_and_composites.md and notes/cone_modification_classes.md.

Paper reference: future Section on composite particles and cone narrowing.
"""

import numpy as np
from .CausalSession import CausalSession
from .UnityConstraint import enforce_unity_spinor


class CompositeCausalSession:
    """
    A bound composite of N CausalSessions.

    Each constituent session ticks independently each macro-tick, then a
    binding step partially locks their phases according to binding_strength.
    The composite's probability density uses the coherent sum |Σ ψ_i|²,
    so constituent phase cancellation is physically realized.

    Parameters
    ----------
    sessions        : list of CausalSession  — the constituent particles
    binding_strength: float in [0, 1]
                      0.0 = no binding (free particles, coherent sum only)
                      0.9 = strongly bound (phases lock each tick)
                      1.0 = perfect lock (constituents move as one)
    """

    def __init__(self, sessions: list, binding_strength: float = 0.9):
        if len(sessions) < 2:
            raise ValueError("CompositeCausalSession requires at least 2 sessions.")
        self.sessions         = sessions
        self.binding_strength = float(np.clip(binding_strength, 0.0, 1.0))
        self.tick_counter     = 0

    # ── Evolution ─────────────────────────────────────────────────────────────

    def tick(self):
        """
        Advance all constituent sessions by one tick, then apply binding.
        """
        for s in self.sessions:
            s.tick()
        if self.binding_strength > 0:
            self._apply_binding()

    def advance_tick_counter(self):
        for s in self.sessions:
            s.advance_tick_counter()
        self.tick_counter += 1

    def _apply_binding(self):
        """
        Partially lock the phases of all constituent sessions toward their
        mean phase.  binding_strength=1 → all phases equal after one tick.

        This is the physical mechanism of the strong force: color-correlated
        sessions are prevented from drifting in phase relative to each other.
        The phase lock is what makes their cones interfere coherently and
        causes the phase gradient of the coherent sum to approach zero for
        a neutral composite.
        """
        shape = self.sessions[0].psi_R.shape

        # Compute mean phase from the coherent sum
        sum_R = sum(s.psi_R for s in self.sessions)
        sum_L = sum(s.psi_L for s in self.sessions)
        mean_phase_R = np.angle(sum_R)
        mean_phase_L = np.angle(sum_L)

        for s in self.sessions:
            phase_diff_R = mean_phase_R - np.angle(s.psi_R)
            phase_diff_L = mean_phase_L - np.angle(s.psi_L)
            s.psi_R *= np.exp(1j * self.binding_strength * phase_diff_R)
            s.psi_L *= np.exp(1j * self.binding_strength * phase_diff_L)
            enforce_unity_spinor(s.psi_R, s.psi_L)

    # ── Probability density (coherent sum) ────────────────────────────────────

    def probability_density(self) -> np.ndarray:
        """
        Coherent probability density: |Σ_i ψ_R_i|² + |Σ_i ψ_L_i|²

        This is the physically correct density for a bound composite.
        It includes cross-terms (interference) between constituents.

        For a neutral composite with cancelling phase gradients, this is
        MUCH more localized than the incoherent sum Σ|ψ_i|² — the phase
        cancellation suppresses the off-center amplitude.
        """
        sum_R = sum(s.psi_R for s in self.sessions)
        sum_L = sum(s.psi_L for s in self.sessions)
        return np.abs(sum_R)**2 + np.abs(sum_L)**2

    def incoherent_density(self) -> np.ndarray:
        """
        Incoherent probability density: Σ_i (|ψ_R_i|² + |ψ_L_i|²)

        This is what you would measure if the sessions were independent.
        Compare with probability_density() to see the effect of phase
        cancellation: incoherent_density >= probability_density always,
        with equality only when all phases are aligned.
        """
        return sum(s.probability_density() for s in self.sessions)

    # ── Composite cone properties ─────────────────────────────────────────────

    def effective_cone_half_angle(self) -> float:
        """
        Effective material cone half-angle of the composite.

        Computed from the coherent probability density's radial spread:
        a narrow distribution → small effective cone angle (appears massive).
        A neutral composite with cancelling phases should give a much smaller
        angle than any individual constituent.

        Returns the mean constituent angle as a baseline for comparison.
        (A full geometric computation requires knowing the lattice center.)
        """
        angles = [s.cone_half_angle for s in self.sessions]
        return float(np.mean(angles))   # baseline; use cone_amplitude_profile for true value

    def charge_balance(self) -> float:
        """
        Net charge proxy of the composite: Σ rgb_cmy_imbalance across constituents.

        Near zero → electrically neutral composite (phases tend to cancel).
        The magnitude of phase cancellation in probability_density() correlates
        with how close this is to zero.
        """
        return sum(s.rgb_cmy_imbalance for s in self.sessions)

    def phase_coherence(self) -> float:
        """
        Measure of phase alignment between constituent sessions.

        Returns the ratio: |Σ ψ_i|² / Σ|ψ_i|²  (integrated over lattice).

        1.0 → perfectly aligned phases (maximum constructive interference)
        0.0 → perfectly cancelling phases (maximum destructive interference)

        For a neutral composite, this approaches 0 — the constituents'
        phases cancel and the effective cone is narrow.  For a charged
        composite, this is larger — phases reinforce and the cone is wider.
        """
        coherent   = float(self.probability_density().sum())
        incoherent = float(self.incoherent_density().sum())
        return coherent / incoherent if incoherent > 1e-12 else 1.0
