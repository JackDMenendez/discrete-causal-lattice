"""
UnityConstraint.py
The A=1 Unity Constraint: strict probability conservation.

Every tick, after all amplitude updates are applied, the wave
function must be renormalized to unit probability. This is not
a correction -- it is the foundational axiom of the framework.

A=1 means: the session persists. Probability is conserved.
The universe does not lose or create information in a tick.

Paper reference: Section 5 (Phase Propagation and the Unity Constraint)
"""

import numpy as np


def enforce_unity(psi: np.ndarray) -> np.ndarray:
    """
    Enforce the A=1 unity constraint on a complex amplitude field.

    Normalizes psi in-place so that sum(|psi|^2) = 1.
    If the norm is zero the session has annihilated -- this should
    not occur under valid lattice dynamics and is flagged as an error.

    Parameters
    ----------
    psi : complex ndarray of any shape (1D, 2D, or 3D lattice)

    Returns
    -------
    psi : normalized in-place (also returned for convenience)
    """
    norm = np.sqrt(np.sum(np.abs(psi) ** 2))
    if norm < 1e-12:
        raise RuntimeError(
            "Unity constraint violated: session amplitude collapsed to zero. "
            "Check lattice boundary conditions and Hamiltonian parameters."
        )
    psi /= norm
    return psi


def unity_residual(psi: np.ndarray) -> float:
    """
    Returns the deviation from unity: |sum(|psi|^2) - 1|.
    Used in audit modules to verify conservation at every tick.
    A well-behaved simulation should keep this below 1e-10.
    """
    return abs(np.sum(np.abs(psi) ** 2) - 1.0)


def is_unity(psi: np.ndarray, tolerance: float = 1e-10) -> bool:
    """Returns True if the amplitude field satisfies A=1 within tolerance."""
    return unity_residual(psi) < tolerance


def enforce_unity_spinor(psi_R: np.ndarray, psi_L: np.ndarray):
    """
    Enforce A=1 for a two-component Dirac spinor.

    Normalizes both components in-place so sum(|psi_R|^2 + |psi_L|^2) = 1.
    Modifies arrays in-place and returns (psi_R, psi_L) for convenience.

    Paper reference: Section 3 (Dirac spinor, A=1 unity constraint)
    """
    norm = np.sqrt(np.sum(np.abs(psi_R) ** 2 + np.abs(psi_L) ** 2))
    if norm < 1e-12:
        raise RuntimeError(
            "Unity constraint violated: spinor amplitude collapsed to zero. "
            "Check lattice boundary conditions and Hamiltonian parameters."
        )
    psi_R /= norm
    psi_L /= norm
    return psi_R, psi_L


def unity_residual_spinor(psi_R: np.ndarray, psi_L: np.ndarray) -> float:
    """
    Returns the deviation from unity for a Dirac spinor:
    |sum(|psi_R|^2 + |psi_L|^2) - 1|
    """
    return abs(np.sum(np.abs(psi_R) ** 2 + np.abs(psi_L) ** 2) - 1.0)
