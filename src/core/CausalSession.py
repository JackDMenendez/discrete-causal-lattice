"""
CausalSession.py
The Quantum Lantern: a particle as a persistent probability flux.

The bipartite Dirac spinor model:

  STRUCTURE:
    psi_R : amplitude on RGB sublattice (right-handed component)
    psi_L : amplitude on CMY sublattice (left-handed component)

    The bipartite lattice IS the Dirac structure.  RGB/CMY are psi_R/psi_L.

  DIRAC TICK RULE:
    Even tick (RGB active):
      new_psi_R = cos(delta_phi/2) * kinetic_hop(psi_L, RGB_VECTORS)
                + 1j * sin(delta_phi/2) * psi_R

    Odd tick (CMY active):
      new_psi_L = cos(delta_phi/2) * kinetic_hop(psi_R, CMY_VECTORS)
                + 1j * sin(delta_phi/2) * psi_L

    - Kinetic term hops the OPPOSITE component across the active sublattice
    - Mass term rotates each component IN PLACE (no hop, just phase rotation)
    - A=1: sum(|psi_R|^2 + |psi_L|^2) = 1 enforced after each tick

  SPECIAL CASES:
    Massless (delta_phi=0): cos=1, sin=0 -> full swap per tick (photon)
    Max mass (delta_phi=pi): cos=0, sin=1 -> stays in place

  MOMENTUM:
    Phase-alignment weighting biases the kinetic hop toward aligned neighbors,
    giving net drift.  Inertia scales with omega (1/(1+omega) damping).

  ZITTERBEWEGUNG:
    Now appears as amplitude trading between psi_R and psi_L each tick,
    rather than p_stay at a single site.  More physically accurate.

Paper reference: Section 3 (Dirac Spinor, Bipartite Tick Rule)
"""

import numpy as np
from typing import Tuple
from .OctahedralLattice import (OctahedralLattice, COORDINATION_NUMBER,
                                 SUBLATTICE_SIZE, active_vectors,
                                 ALL_VECTORS, RGB_VECTORS, CMY_VECTORS)
from .PhaseRotor import PhaseRotor
from .UnityConstraint import enforce_unity, enforce_unity_spinor


def _precompute_shift_slices(shape, vectors):
    """
    For each direction vector (dx, dy, dz), compute 4 slice-tuples:
      nb_src, nb_dst  -- for  nb_buf[nb_dst] = source[nb_src]
      out_src, out_dst -- for  result[out_dst] += emission[out_src]

    These replace triple np.roll chains and boundary masks, giving the
    same physics with zero temporary array allocation for the shift.
    """
    sx, sy, sz = shape

    def axis_slices(d, n):
        """Return (nb_src, nb_dst) for one axis."""
        if d > 0:
            return slice(d, n),  slice(0, n - d)
        elif d < 0:
            return slice(0, n + d), slice(-d, n)
        else:
            return slice(None), slice(None)

    slices = []
    for (dx, dy, dz) in vectors:
        x_nb_src, x_nb_dst = axis_slices(dx, sx)
        y_nb_src, y_nb_dst = axis_slices(dy, sy)
        z_nb_src, z_nb_dst = axis_slices(dz, sz)
        # Output slices are the exact reverse of the neighbor lookup slices:
        #   emission at source site lands at destination site.
        nb_src  = (x_nb_src, y_nb_src, z_nb_src)
        nb_dst  = (x_nb_dst, y_nb_dst, z_nb_dst)
        out_src = nb_dst   # emission pulled from interior (no wrap)
        out_dst = nb_src   # lands at displaced positions
        # Store direction vector alongside slices so _kinetic_hop can apply
        # the Peierls EM phase  A·v  without a separate vector lookup.
        slices.append(((dx, dy, dz), nb_src, nb_dst, out_src, out_dst))
    return slices


class CausalSession:
    """
    A particle as a persistent causal session on T^3_diamond.

    Uses a two-component Dirac spinor (psi_R, psi_L) matching the
    bipartite RGB/CMY sublattice structure.

    The is_massless flag is a performance shortcut for delta_phi=0;
    the physics is identical since cos(0/2)=1 and sin(0/2)=0.
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

        # Two-component Dirac spinor
        shape = (lattice.size_x, lattice.size_y, lattice.size_z)
        self.psi_R = np.zeros(shape, dtype=complex)
        self.psi_L = np.zeros(shape, dtype=complex)

        # Initialize at single node, amplitude split equally between components
        x0, y0, z0 = initial_node
        amp = 1.0 / np.sqrt(2.0)
        self.psi_R[x0, y0, z0] = amp
        self.psi_L[x0, y0, z0] = amp

        if any(p != 0.0 for p in momentum):
            self._apply_initial_momentum(initial_node, momentum)

        enforce_unity_spinor(self.psi_R, self.psi_L)

        # Pre-compute shift slices for all direction vectors to avoid np.roll
        # in the hot _kinetic_hop path.  Each entry is a 4-tuple:
        #   (nb_src, nb_dst, out_src, out_dst)
        # nb:  nb_arr[nb_dst] = source[nb_src]   -- look up neighbor in dir v
        # out: result[out_dst] += emission[out_src] -- shift emission to dest
        self._rgb_slices = _precompute_shift_slices(shape, RGB_VECTORS)
        self._cmy_slices = _precompute_shift_slices(shape, CMY_VECTORS)
        # Reusable neighbor buffer (zeroed at start of each direction)
        self._nb_buf = np.zeros(shape, dtype=complex)

    # ── Backward-compatibility property ───────────────────────────────────────

    @property
    def psi(self) -> np.ndarray:
        """
        Backward-compatible accessor: returns psi_R.
        Use probability_density() for the physically correct total density.
        """
        return self.psi_R

    @psi.setter
    def psi(self, value: np.ndarray):
        """
        Backward-compatible setter: distributes a scalar field equally
        across both spinor components, preserving A=1.

        If value is normalized (sum |psi|^2 = 1), then
        psi_R = psi_L = value / sqrt(2) gives
        sum(|psi_R|^2 + |psi_L|^2) = sum(|psi|^2) = 1.
        """
        amp = value / np.sqrt(2.0)
        self.psi_R = amp.copy().astype(complex)
        self.psi_L = amp.copy().astype(complex)

    # ── Momentum initialization ────────────────────────────────────────────────

    def _apply_initial_momentum(self, center, momentum):
        """
        Momentum = phase gradient across the packet.
        Applied identically to both spinor components.
        """
        kx, ky, kz = momentum
        for x in range(self.lattice.size_x):
            for y in range(self.lattice.size_y):
                for z in range(self.lattice.size_z):
                    if (np.abs(self.psi_R[x, y, z]) > 1e-12 or
                            np.abs(self.psi_L[x, y, z]) > 1e-12):
                        phase = np.exp(1j * (kx*x + ky*y + kz*z))
                        self.psi_R[x, y, z] *= phase
                        self.psi_L[x, y, z] *= phase

    # ── Kinetic hop kernel ─────────────────────────────────────────────────────

    def _kinetic_hop(self, source: np.ndarray,
                     precomputed_slices: list) -> np.ndarray:
        """
        Directed kinetic hop: source amplitude propagates to neighbor sites.

        For each direction v, the phase advance is delta_p = phi(r+v) - phi(r).
        A positive delta_p means the neighbor is AHEAD in phase -- the momentum
        gradient points toward it.  We use delta_p as the directional weight
        (max(0, delta_p), so only momentum-aligned directions receive amplitude)
        and include exp(i*delta_p) as a per-direction phase correction so that
        emitted amplitude arrives at the destination with the correct plane-wave
        phase (i.e. constructive interference is preserved).

        For zero-momentum regions (all delta_p ≈ 0): falls back to uniform
        distribution with no phase correction.  Gravity continues to act via
        the sin/cos(delta_phi/2) mass-term coefficients, which are independent
        of this momentum bias.

        Uses pre-computed shift slices (stored in self._rgb_slices /
        self._cmy_slices) instead of np.roll chains, eliminating ~24 full-grid
        temporary array allocations per call.

        Parameters
        ----------
        source             : complex (X,Y,Z) -- the component being hopped
        precomputed_slices : list of (nb_src, nb_dst, out_src, out_dst)

        Returns
        -------
        result : complex (X,Y,Z) -- accumulated hopped amplitude
        """
        n_vec = len(precomputed_slices)
        local_phase = np.angle(source)
        nb_buf = self._nb_buf          # reuse pre-allocated buffer

        # Peierls EM phase: A·v added to delta_p for each hop direction.
        # Only computed when the lattice has a non-zero vector potential.
        A = self.lattice.vector_potential  # (3, X, Y, Z), always present
        has_em = np.any(A != 0.0)

        # Per-direction phase advance and directed weight
        delta_p_list = []
        weights = np.zeros((n_vec,) + source.shape, dtype=float)
        for i, (vec, nb_src, nb_dst, out_src, out_dst) in enumerate(precomputed_slices):
            dx, dy, dz = vec
            # Look up neighbor via slice: no np.roll, no temporary arrays
            nb_buf[:] = 0.0
            nb_buf[nb_dst] = source[nb_src]
            nb_abs = np.abs(nb_buf)
            nb_phase = np.where(nb_abs > 1e-9, np.angle(nb_buf), local_phase)
            delta_p = nb_phase - local_phase               # phase advance in dir v
            # Peierls substitution: add A·v so the EM vector potential biases
            # the hop direction.  Positive A·v reinforces hops in direction v;
            # negative A·v suppresses them.  For a curl field this produces the
            # Lorentz deflection (perpendicular to both velocity and B-field).
            if has_em:
                delta_p = delta_p + (A[0] * dx + A[1] * dy + A[2] * dz)
            delta_p_list.append(delta_p)
            # Weight = positive phase advance only; inertia damps response to gradient
            weights[i] = np.maximum(0.0, delta_p) / (1.0 + self.phase_rotor.omega)

        # Normalize (fallback: uniform real weights when momentum ≈ zero)
        total_w  = weights.sum(axis=0)
        zero_mom = total_w < 1e-12
        total_w_safe = np.where(zero_mom, 1.0, total_w)
        uniform  = 1.0 / n_vec

        # Emit: per-direction complex weight = (real weight) * exp(i*delta_p)
        # This ensures amplitude arrives at destination with the correct phase.
        result = np.zeros_like(source)
        for i, (vec, nb_src, nb_dst, out_src, out_dst) in enumerate(precomputed_slices):
            w_i = np.where(zero_mom, uniform, weights[i] / total_w_safe)
            # Phase correction: exp(i*delta_p) so emitted amp matches dest wave.
            # For zero-momentum fallback: no correction (exp(i*0)=1).
            phase_corr = np.where(zero_mom, 1.0+0j,
                                  np.exp(1j * delta_p_list[i]).astype(complex))
            emission = source * phase_corr * w_i
            # Shift emission to destination via slice: no np.roll, no mask array
            result[out_dst] += emission[out_src]

        return result

    # ── The Dirac tick ─────────────────────────────────────────────────────────

    def tick(self):
        """
        The bipartite Dirac spinor update cycle.

        Even tick (RGB active):
          new_psi_R = cos(delta_phi/2) * kinetic_hop(psi_L, RGB)
                    + 1j * sin(delta_phi/2) * psi_R
          psi_L     unchanged

        Odd tick (CMY active):
          new_psi_L = cos(delta_phi/2) * kinetic_hop(psi_R, CMY)
                    + 1j * sin(delta_phi/2) * psi_L
          psi_R     unchanged

        A=1 enforced after each tick via joint normalization.

        Paper reference: Section 3 (Dirac tick rule, bipartite structure)
        """
        tick_parity = self.tick_counter % 2

        delta_phi = (self.phase_rotor.omega
                     + self.lattice.topological_potential)       # (X,Y,Z)
        cos_half  = np.cos(delta_phi / 2.0)                      # (X,Y,Z)
        sin_half  = np.sin(delta_phi / 2.0)                      # (X,Y,Z)

        if self.is_massless:
            # Massless photon: strict bipartite alternation (chirality preserved).
            # Even tick: psi_L -> psi_R via RGB; psi_L unchanged.
            # Odd tick:  psi_R -> psi_L via CMY; psi_R unchanged.
            if tick_parity == 0:
                new_psi_R = self._kinetic_hop(self.psi_L, self._rgb_slices)
                new_psi_L = self.psi_L
            else:
                new_psi_L = self._kinetic_hop(self.psi_R, self._cmy_slices)
                new_psi_R = self.psi_R
        else:
            # Massive particle: both components updated simultaneously.
            # RGB hop: psi_L -> psi_R; CMY hop: psi_R -> psi_L.
            # Simultaneous update averages RGB and CMY displacements,
            # giving zero net CoM drift for zero-momentum states (symmetry
            # of V1+V2+V3 + CMY1+CMY2+CMY3 = 0).
            hop_R     = self._kinetic_hop(self.psi_L, self._rgb_slices)
            hop_L     = self._kinetic_hop(self.psi_R, self._cmy_slices)
            new_psi_R = cos_half * hop_R + 1j * sin_half * self.psi_R
            new_psi_L = cos_half * hop_L + 1j * sin_half * self.psi_L

        # A=1: normalize both components jointly
        enforce_unity_spinor(new_psi_R, new_psi_L)
        self.psi_R = new_psi_R
        self.psi_L = new_psi_L

    def probability_density(self) -> np.ndarray:
        """Total probability density: |psi_R|^2 + |psi_L|^2."""
        return np.abs(self.psi_R) ** 2 + np.abs(self.psi_L) ** 2

    # ── Cone measurement ──────────────────────────────────────────────────────

    def cone_amplitude_profile(self, center, n_shells: int = 50):
        """
        Radial amplitude profile: total probability in each shell at distance r
        from center.  Returns (radii, profile) arrays of length n_shells.

        Massless:   profile concentrated near max radius  (wavefront at boundary)
        Massive:    profile peaked near center, tailing off  (amplitude hugs origin)
        Very massive: profile almost entirely in shell 0  (barely moves)

        This is the direct observable of cone shape — the same quantity plotted
        in the quantization scan heatmap, but for a free particle instead of
        an orbital.  Use it to verify that interior_fraction tracks p_stay.
        """
        cx, cy, cz = center
        x = np.arange(self.lattice.size_x)
        xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
        r    = np.sqrt((xx - cx)**2 + (yy - cy)**2 + (zz - cz)**2)
        P    = self.probability_density()
        r_max = float(r.max())
        edges   = np.linspace(0, r_max, n_shells + 1)
        centers = 0.5 * (edges[:-1] + edges[1:])
        profile = np.array([float(P[(r >= edges[i]) & (r < edges[i+1])].sum())
                             for i in range(n_shells)])
        return centers, profile

    def interior_fraction(self, center, radius: float) -> float:
        """
        Fraction of total amplitude inside given radius from center.

        This is the direct measurement of the mass proxy:
          interior_fraction → 1.0  massive  (amplitude hugs center)
          interior_fraction → 0.0  massless (amplitude at boundary)

        After T ticks without interaction, interior_fraction should approach
        p_stay = sin²(ω/2).  This is the empirical check of the claim that
        mass is the fraction of cone information that stays interior.
        """
        cx, cy, cz = center
        x = np.arange(self.lattice.size_x)
        xx, yy, zz = np.meshgrid(x, x, x, indexing='ij')
        r = np.sqrt((xx - cx)**2 + (yy - cy)**2 + (zz - cz)**2)
        return float(self.probability_density()[r <= radius].sum())

    def phase_gradient_field(self) -> np.ndarray:
        """
        The phase gradient field ∇φ — the quantity that drives the kinetic hop.
        Returns a (3, X, Y, Z) array: [∂φ/∂x, ∂φ/∂y, ∂φ/∂z] at each node.

        Interpretation:
          Uniform ∇φ = k  →  free particle with momentum k
          Zero ∇φ         →  no preferred direction, amplitude stays put
          Curl(∇φ) ≠ 0    →  angular momentum / charge winding

        Uses psi_R as the phase reference.  For a composite neutral particle
        whose constituent phases cancel, ∇φ of the COHERENT sum is near zero
        even though each constituent has non-zero ∇φ — that cancellation is
        the phase mechanism of cone narrowing.
        See notes/material_cone_and_composites.md.
        """
        phi = np.angle(self.psi_R)
        return np.stack([np.gradient(phi, axis=0),
                         np.gradient(phi, axis=1),
                         np.gradient(phi, axis=2)], axis=0)

    # ── Cone modification ─────────────────────────────────────────────────────

    def apply_phase_map(self, delta_phase: np.ndarray):
        """
        Apply a spatially varying phase rotation to both spinor components.
        Multiplies psi_R and psi_L by exp(i * delta_phase) at every node.

        A=1 is preserved exactly — phase rotation is unitary, no renormalization
        needed.

        Class 1 cone modification: phase engineering.
        Common uses:
          Linear gradient  np.dot([kx,ky,kz], [xx,yy,zz])  → impose momentum
          Azimuthal phase  m * arctan2(y,x)                 → orbital angular momentum
          Arbitrary array                                    → arbitrary interference

        Parameters
        ----------
        delta_phase : real (X,Y,Z) array — phase advance in radians at each node
        """
        rotation = np.exp(1j * delta_phase).astype(complex)
        self.psi_R *= rotation
        self.psi_L *= rotation

    def impose_sublattice_ratio(self, target_R_fraction: float):
        """
        Redistribute amplitude between psi_R and psi_L toward a target ratio.

        target_R_fraction in [0, 1]:
          0.5  balanced (default for a massive particle)
          1.0  fully right-handed  (Class 2: sublattice selection)
          0.0  fully left-handed   (neutrino-like, CMY-only cone)

        Preserves the spatial distribution of each component; only rescales
        the overall amplitude of each.  A=1 enforced after redistribution.

        Physical cost note: applying this every tick is unphysical — real
        sublattice selection requires doing work against Zitterbewegung, which
        continuously drives psi_R ↔ psi_L oscillation.  Intended for
        initialization or as a controlled forcing term in experiments.
        """
        p_R = float(np.sum(np.abs(self.psi_R) ** 2))
        p_L = float(np.sum(np.abs(self.psi_L) ** 2))
        total = p_R + p_L
        if total < 1e-12:
            return
        scale_R = (np.sqrt(target_R_fraction / (p_R / total))
                   if p_R > 1e-12 else 0.0)
        scale_L = (np.sqrt((1.0 - target_R_fraction) / (p_L / total))
                   if p_L > 1e-12 else 0.0)
        self.psi_R *= scale_R
        self.psi_L *= scale_L
        enforce_unity_spinor(self.psi_R, self.psi_L)

    @property
    def cone_half_angle(self) -> float:
        """
        Material cone half-angle in radians: arcsin(cos(ω/2)) = arcsin(√p_move).

        The material cone is the sub-luminal analogue of the light cone.  Its
        half-angle shrinks as mass (ω) increases:
          - Photon  (ω=0):  θ = π/4  (45°, full light cone)
          - Massive (ω>0):  θ < π/4
          - Max-mass(ω=π):  θ = 0    (no spreading, pure clock)

        For a composite neutral object the constituent cones partially cancel,
        giving an effective cone much narrower than any individual constituent.
        See notes/material_cone_and_composites.md.
        """
        return float(np.arcsin(np.cos(self.phase_rotor.omega / 2.0)))

    @property
    def rgb_cmy_imbalance(self) -> float:
        """
        Charge proxy: Σ|ψ_R|² - Σ|ψ_L|²  ∈ [-1, 1].

        +1  = fully right-handed (RGB-dominant)
        -1  = fully left-handed  (CMY-dominant)
         0  = balanced (neutral)

        For a composite particle, the sum of rgb_cmy_imbalance across all
        constituent sessions is the net charge proxy.

        NOTE: the cone-narrowing mechanism for neutral composites is PHASE
        cancellation, not sublattice amplitude balancing.  When constituent
        phases cancel (Σ ψ_i ≈ 0), the net phase gradient ∇Φ ≈ 0, which
        eliminates the directed hop.  The coherent probability density
        |Σ ψ_i|² must be used (not Σ|ψ_i|²) to observe this effect.
        See notes/material_cone_and_composites.md.
        """
        p_R = float(np.sum(np.abs(self.psi_R) ** 2))
        p_L = float(np.sum(np.abs(self.psi_L) ** 2))
        return p_R - p_L

    def advance_tick_counter(self):
        self.tick_counter += 1
        self.phase_rotor.advance()
