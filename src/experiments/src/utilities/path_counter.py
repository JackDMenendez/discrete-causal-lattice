"""
path_counter.py
Combinatorial path counting on the octahedral lattice.

This is a pure mathematics module -- no physics assumptions.
It counts the exact number of distinct causal paths from an
origin node to a target node in exactly N hops on T^3_diamond.

This count is the foundation of the falsifiable predictions:
  - For large N: path count converges to Gaussian (CLT) -> 1/r^2
  - For small N: discrete deviations from Gaussian are calculable
  - These deviations are specific numerical predictions of the framework

Paper reference: Section 9 (Path Counting and Falsifiable Predictions)
"""

import numpy as np
from functools import lru_cache
from typing import Tuple


@lru_cache(maxsize=None)
def count_paths(n_hops: int, dx: int, dy: int, dz: int) -> int:
    """
    Count the number of distinct paths on the octahedral lattice
    from origin (0,0,0) to displacement (dx, dy, dz) in exactly n_hops steps.

    Each step moves ±1 in exactly one of {x, y, z}.
    Uses the exact multinomial formula -- result is a true integer.

    Let:
      n_px, n_mx = number of +x, -x steps  ->  n_px - n_mx = dx,  n_px + n_mx = sx
      n_py, n_my = number of +y, -y steps  ->  n_py - n_my = dy,  n_py + n_my = sy
      n_pz, n_mz = number of +z, -z steps  ->  n_pz - n_mz = dz,  n_pz + n_mz = sz

    Constraints:
      sx + sy + sz = n_hops
      sx >= |dx|, sy >= |dy|, sz >= |dz|
      (sx - dx) even, (sy - dy) even, (sz - dz) even

    For each valid (sx, sy, sz):
      n_px = (sx + dx) // 2,  n_mx = (sx - dx) // 2   (and similarly for y, z)
      count += n_hops! / (n_px! * n_mx! * n_py! * n_my! * n_pz! * n_mz!)

    Paper reference: Section 9 (exact path count P(N, a, b, c))
    """
    from math import factorial

    # Quick feasibility checks
    manhattan = abs(dx) + abs(dy) + abs(dz)
    if manhattan > n_hops:
        return 0                          # Target outside causal cone
    if (n_hops - manhattan) % 2 != 0:
        return 0                          # Parity mismatch -- unreachable

    total = 0
    full_factorial = factorial(n_hops)

    # Enumerate all valid total-step allocations (sx, sy, sz)
    # sx = total steps in x-direction (both + and -)
    for sx in range(abs(dx), n_hops - abs(dy) - abs(dz) + 1):
        if (sx - dx) % 2 != 0:
            continue                      # n_px must be integer
        remaining_after_x = n_hops - sx

        for sy in range(abs(dy), remaining_after_x - abs(dz) + 1):
            if (sy - dy) % 2 != 0:
                continue                  # n_py must be integer
            sz = remaining_after_x - sy

            if sz < abs(dz):
                continue
            if (sz - dz) % 2 != 0:
                continue                  # n_pz must be integer

            # Recover individual step counts
            n_px = (sx + dx) // 2;  n_mx = (sx - dx) // 2
            n_py = (sy + dy) // 2;  n_my = (sy - dy) // 2
            n_pz = (sz + dz) // 2;  n_mz = (sz - dz) // 2

            # Multinomial coefficient: n_hops! / (n_px! n_mx! n_py! n_my! n_pz! n_mz!)
            denom = (factorial(n_px) * factorial(n_mx) *
                     factorial(n_py) * factorial(n_my) *
                     factorial(n_pz) * factorial(n_mz))
            total += full_factorial // denom

    return total


def path_count_shell(n_hops: int) -> dict:
    """
    Returns a dict mapping (dx, dy, dz) -> path_count for all nodes
    reachable in exactly n_hops steps from origin.

    The set of reachable nodes is the causal cone shell at time n_hops.
    Used to map the discrete amplitude distribution vs the Gaussian prediction.

    Paper reference: Section 9 (causal cone, CLT convergence)
    """
    shell = {}
    for dx in range(-n_hops, n_hops + 1):
        for dy in range(-n_hops, n_hops + 1):
            for dz in range(-n_hops, n_hops + 1):
                manhattan = abs(dx) + abs(dy) + abs(dz)
                if manhattan <= n_hops and (n_hops - manhattan) % 2 == 0:
                    p = count_paths(n_hops, dx, dy, dz)
                    if p > 0:
                        shell[(dx, dy, dz)] = p
    return shell


def gaussian_prediction(n_hops: int, dx: int, dy: int, dz: int) -> float:
    """
    The continuous Gaussian approximation to the path probability
    P(reach dx,dy,dz in n_hops) = count_paths / 6^n_hops.

    Valid for large n_hops (CLT regime). Returns a probability,
    not a density -- comparable directly to count_paths / 6^n_hops.

    Paper reference: Section 9 (CLT bridge, discrete vs continuous)
    """
    if n_hops == 0:
        return 1.0 if (dx == dy == dz == 0) else 0.0

    # Each axis: 1D random walk with step size 1, probability 1/3 per axis
    # Variance per axis per hop = 2/3 (prob 1/3 each of +1, 0, -1 net... 
    # actually on octahedral: each hop changes exactly one axis by ±1
    # So per axis: sigma^2 = n_hops/3
    sigma_sq = n_hops / 3.0
    r_sq = dx**2 + dy**2 + dz**2
    # 3D Gaussian probability (not density): normalized to sum to 1 over integer grid
    # Use the discrete Gaussian normalization
    norm = (2 * np.pi * sigma_sq) ** 1.5
    return np.exp(-r_sq / (2 * sigma_sq)) / norm


def path_probability(n_hops: int, dx: int, dy: int, dz: int) -> float:
    """
    The exact probability of reaching (dx,dy,dz) in n_hops:
    count_paths(n_hops, dx, dy, dz) / 6^n_hops

    This is what gets compared to the Gaussian prediction.
    """
    if n_hops == 0:
        return 1.0 if (dx == dy == dz == 0) else 0.0
    total_paths = 6 ** n_hops
    return count_paths(n_hops, dx, dy, dz) / total_paths


def discrete_correction(n_hops: int, dx: int, dy: int, dz: int) -> float:
    """
    The fractional deviation of the exact path probability from the Gaussian.
    This is the falsifiable prediction: non-zero at small n_hops, vanishes as N->inf.

    correction = (exact_probability - gaussian) / gaussian

    Paper reference: Section 9 (discrete corrections, experimental target)
    """
    exact = path_probability(n_hops, dx, dy, dz)
    # Normalize Gaussian to the same discrete grid
    # Sum Gaussian over all reachable nodes to get normalization factor
    shell = path_count_shell(n_hops)
    gauss_total = sum(gaussian_prediction(n_hops, d[0], d[1], d[2]) for d in shell)
    if gauss_total < 1e-30:
        return 0.0
    gauss_normalized = gaussian_prediction(n_hops, dx, dy, dz) / gauss_total
    if gauss_normalized < 1e-30:
        return 0.0
    return (exact - gauss_normalized) / gauss_normalized
