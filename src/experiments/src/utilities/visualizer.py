"""
visualizer.py
Shared plotting utilities for all A=1 experiments.

All figures follow the same academic style conventions.
Each plot function saves a high-resolution PNG for the paper
and returns the matplotlib figure for interactive use.

Paper reference: figures throughout
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List

# ── Global style ─────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", font_scale=1.2)
plt.rcParams['font.family'] = 'serif'
DPI = 300


def plot_probability_density_3d_slice(
    psi_sq: np.ndarray,
    slice_axis: str = 'z',
    slice_index: Optional[int] = None,
    title: str = "Probability Density",
    filename: Optional[str] = None,
) -> plt.Figure:
    """
    Plots a 2D slice of a 3D probability density |psi|^2.

    Parameters
    ----------
    psi_sq      : 3D array of shape (Nx, Ny, Nz)
    slice_axis  : 'x', 'y', or 'z' -- which axis to slice along
    slice_index : index along slice_axis; defaults to center
    title       : figure title
    filename    : if provided, saves the figure to this path
    """
    # TODO: implement 2D slice visualization
    raise NotImplementedError


def plot_causal_cone(
    reachable_nodes: List,
    n_ticks: int,
    filename: Optional[str] = None,
) -> plt.Figure:
    """
    Visualizes the expanding octahedral causal cone.
    Used by exp_00_causal_cone.py.
    """
    # TODO: implement 3D octahedral cone visualization
    raise NotImplementedError


def plot_interference_pattern(
    wall_pattern: np.ndarray,
    field_2d: Optional[np.ndarray] = None,
    slit_positions: Optional[List[int]] = None,
    title: str = "Interference Pattern",
    filename: Optional[str] = None,
) -> plt.Figure:
    """
    Two-panel interference figure: 2D field heatmap + back-wall distribution.
    Used by exp_03_interference.py.
    """
    # TODO: implement interference visualization
    raise NotImplementedError


def plot_spacetime_history(
    density_history: np.ndarray,
    time_snapshots: Optional[List] = None,
    potential: Optional[np.ndarray] = None,
    title: str = "Spacetime History",
    filename: Optional[str] = None,
) -> plt.Figure:
    """
    Two-panel figure: spacetime heatmap + spatial snapshots.
    Used by exp_01_inertia.py and exp_02_gravity_clock_density.py.
    """
    # TODO: implement spacetime history visualization
    raise NotImplementedError


def plot_clock_density_field(
    clock_density: np.ndarray,
    title: str = "Clock Density Field",
    filename: Optional[str] = None,
) -> plt.Figure:
    """
    Visualizes the clock density distribution V(x,y,z).
    Used by exp_02_gravity_clock_density.py.
    """
    # TODO: implement clock density visualization
    raise NotImplementedError


def plot_discrete_vs_gaussian(
    n_hops_range: List[int],
    corrections: List[float],
    title: str = "Discrete Path Count vs Gaussian Prediction",
    filename: Optional[str] = None,
) -> plt.Figure:
    """
    Plots the discrete correction factor as a function of hop count.
    The falsifiable prediction plot. Used by exp_06_path_counting.py.
    Paper reference: Section 9 (Figure: discrete corrections)
    """
    # TODO: implement discrete vs Gaussian correction plot
    raise NotImplementedError
