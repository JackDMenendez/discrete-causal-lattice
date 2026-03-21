"""
OctahedralLattice.py
The Primal 3D Topology: T^3_diamond

The substrate of the universe modeled as a 3D octahedral lattice.
Each node is a potential causal event. Edges are causal adjacency only.
Space and time are emergent from information propagation, not containers.

Paper reference: Section 2 (The Octahedral Substrate)
"""

import numpy as np
from typing import Tuple, List

# The 6 principal directions of the octahedral lattice.
# These are the only valid causal adjacencies.
OCTAHEDRAL_DIRECTIONS = [
    (+1,  0,  0),  # +x
    (-1,  0,  0),  # -x
    ( 0, +1,  0),  # +y
    ( 0, -1,  0),  # -y
    ( 0,  0, +1),  # +z
    ( 0,  0, -1),  # -z
]

COORDINATION_NUMBER = len(OCTAHEDRAL_DIRECTIONS)  # 6: the natural rest distribution denominator


class OctahedralLattice:
    """
    The discrete 3D causal substrate T^3_diamond.

    Nodes are causal events. Edges are adjacency only.
    The topological_potential V(x,y,z) encodes clock density (gravity).
    Default is 0.0 everywhere (flat vacuum).
    """

    def __init__(self, size_x: int, size_y: int, size_z: int):
        self.size_x = size_x
        self.size_y = size_y
        self.size_z = size_z

        # V(x,y,z): Clock density / topological potential.
        # Higher values = more scheduler load = gravitational time dilation.
        self.topological_potential = np.zeros((size_x, size_y, size_z), dtype=float)

    def topological_neighbors(self, node: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """
        Returns the valid causal neighbors of a node.
        Enforces strict locality: only the 6 octahedral adjacencies are valid.
        Nodes outside the lattice boundary do not exist.
        """
        x, y, z = node
        neighbors = []
        for dx, dy, dz in OCTAHEDRAL_DIRECTIONS:
            nx, ny, nz = x + dx, y + dy, z + dz
            if 0 <= nx < self.size_x and 0 <= ny < self.size_y and 0 <= nz < self.size_z:
                neighbors.append((nx, ny, nz))
        return neighbors

    def set_clock_density_well(self, center: Tuple, width: float, depth: float):
        """
        Creates a Gaussian region of elevated clock density.
        Models a mass: more clocks -> higher scheduler load -> time dilation.

        The potential V(x,y,z) represents the local clock density.
        A region of high clock density accumulates phase faster relative
        to the spatial step, causing refractive bending (gravity).

        Paper reference: Section 6 (Gravity as Clock Density)
        """
        cx, cy, cz = center
        for x in range(self.size_x):
            for y in range(self.size_y):
                for z in range(self.size_z):
                    r_sq = (x - cx)**2 + (y - cy)**2 + (z - cz)**2
                    self.topological_potential[x, y, z] += (
                        depth * np.exp(-0.5 * r_sq / width**2)
                    )

    def clock_density_at(self, node: Tuple[int, int, int]) -> float:
        """
        Returns the local clock density (topological potential) at a node.
        This is the V(x,y,z) term in the discrete Hamiltonian.
        """
        x, y, z = node
        return self.topological_potential[x, y, z]

    def causal_cone_nodes(self, origin: Tuple[int, int, int], n_ticks: int) -> List[Tuple]:
        """
        Returns all nodes reachable from origin in exactly n_ticks hops.
        The causal cone is an expanding octahedron, not a sphere.
        Used by exp_00_causal_cone.py and path_counter.py.

        Uses BFS to enumerate the exact reachable shell at depth n_ticks.
        A node at displacement (dx, dy, dz) is reachable in n_ticks hops
        iff |dx| + |dy| + |dz| <= n_ticks and (|dx|+|dy|+|dz|) has
        the same parity as n_ticks.

        Paper reference: Section 2 (causal cone, speed limit)
        """
        if n_ticks == 0:
            return [origin]

        ox, oy, oz = origin
        reachable = set()

        # BFS: track (node, ticks_remaining)
        # Use the parity+Manhattan distance condition for efficiency
        for dx in range(-n_ticks, n_ticks + 1):
            for dy in range(-n_ticks, n_ticks + 1):
                for dz in range(-n_ticks, n_ticks + 1):
                    manhattan = abs(dx) + abs(dy) + abs(dz)
                    # Reachable iff within cone AND correct parity
                    if manhattan <= n_ticks and (n_ticks - manhattan) % 2 == 0:
                        nx, ny, nz = ox + dx, oy + dy, oz + dz
                        if (0 <= nx < self.size_x and
                                0 <= ny < self.size_y and
                                0 <= nz < self.size_z):
                            reachable.add((nx, ny, nz))

        return list(reachable)
