"""
lattice_calibrator.py
Maps lattice node spacing to physical units and generates
numerical predictions for experimental verification.

The single choice of node spacing determines every prediction
the framework makes. This module makes that mapping explicit
and derives the observable consequences.

Paper reference: Section 9 (calibration table, falsifiable predictions)
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


# ── Fundamental physical constants ───────────────────────────────────────────

SPEED_OF_LIGHT      = 2.99792458e8       # m/s
PLANCK_LENGTH       = 1.616255e-35       # m
PLANCK_TIME         = 5.391247e-44       # s
PLANCK_ENERGY       = 1.956e9            # J
HBAR                = 1.054571817e-34    # J·s
ELECTRON_MASS       = 9.1093837015e-31   # kg
BOHR_RADIUS         = 5.29177210903e-11  # m
COMPTON_WAVELENGTH  = 2.42631023867e-12  # m  (electron)
GRAVITATIONAL_CONST = 6.67430e-11        # m^3 kg^-1 s^-2


@dataclass
class LatticeCalibration:
    """
    A complete calibration of the octahedral lattice to physical units.

    node_spacing_m  : physical length of one lattice edge (meters)
    tick_duration_s : physical duration of one tick (seconds)

    All predictions are derived from these two numbers alone.
    """
    name: str
    node_spacing_m: float
    tick_duration_s: float

    @property
    def emergent_speed_limit(self) -> float:
        """
        c_lattice = node_spacing / tick_duration.
        Must equal SPEED_OF_LIGHT for a valid calibration.
        Paper reference: Section 2 (emergence of c)
        """
        return self.node_spacing_m / self.tick_duration_s

    @property
    def speed_limit_error(self) -> float:
        """Fractional deviation of emergent c from physical c."""
        return abs(self.emergent_speed_limit - SPEED_OF_LIGHT) / SPEED_OF_LIGHT

    @property
    def minimum_time_dilation_quantum(self) -> float:
        """
        The minimum gravitational time dilation increment:
        one extra clock = one extra tick_duration of scheduler overhead.

        delta_t_min = tick_duration_s

        Current optical atomic clock sensitivity: ~1e-18 fractional.
        If tick_duration_s > ~1e-18 seconds, this may be measurable.

        Paper reference: Section 9 (Prediction 2)
        """
        return self.tick_duration_s

    @property
    def discrete_correction_scale_m(self) -> float:
        """
        The physical scale at which discrete path-count corrections
        to 1/r^2 become significant (order 1%).
        This is approximately 10 * node_spacing.

        Paper reference: Section 9 (Prediction 1)
        """
        return 10.0 * self.node_spacing_m

    def summary(self) -> str:
        lines = [
            f"Calibration: {self.name}",
            f"  Node spacing      : {self.node_spacing_m:.3e} m",
            f"  Tick duration     : {self.tick_duration_s:.3e} s",
            f"  Emergent c        : {self.emergent_speed_limit:.6e} m/s",
            f"  Speed limit error : {self.speed_limit_error:.2e}",
            f"  Min time dilation : {self.minimum_time_dilation_quantum:.3e} s",
            f"  Discrete correction scale: {self.discrete_correction_scale_m:.3e} m",
        ]
        return "\n".join(lines)


# ── Standard calibration presets ─────────────────────────────────────────────

PLANCK_CALIBRATION = LatticeCalibration(
    name="Planck Scale",
    node_spacing_m=PLANCK_LENGTH,
    tick_duration_s=PLANCK_TIME,
)

COMPTON_CALIBRATION = LatticeCalibration(
    name="Electron Compton Wavelength",
    node_spacing_m=COMPTON_WAVELENGTH,
    tick_duration_s=COMPTON_WAVELENGTH / SPEED_OF_LIGHT,
)

BOHR_CALIBRATION = LatticeCalibration(
    name="Bohr Radius",
    node_spacing_m=BOHR_RADIUS,
    tick_duration_s=BOHR_RADIUS / SPEED_OF_LIGHT,
)


def print_calibration_table():
    """
    Prints the calibration comparison table for the paper.
    Populates the stub table in predictions.tex.
    """
    calibrations = [PLANCK_CALIBRATION, COMPTON_CALIBRATION, BOHR_CALIBRATION]
    print(f"\n{'Calibration':<25} {'Node spacing (m)':<20} "
          f"{'Min dilation (s)':<20} {'Correction scale (m)':<22} {'c error'}")
    print("-" * 100)
    for cal in calibrations:
        print(f"{cal.name:<25} {cal.node_spacing_m:<20.3e} "
              f"{cal.minimum_time_dilation_quantum:<20.3e} "
              f"{cal.discrete_correction_scale_m:<22.3e} "
              f"{cal.speed_limit_error:.2e}")


if __name__ == "__main__":
    print_calibration_table()
