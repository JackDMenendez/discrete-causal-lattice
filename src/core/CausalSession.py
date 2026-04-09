"""
CausalSession.py
A particle as a persistent probability flux on T^3_diamond.

The bipartite Dirac spinor model:

  STRUCTURE:
    psi_R : amplitude on RGB sublattice (right-handed component)
    psi_L : amplitude on CMY sublattice (left-handed component)

    The bipartite lattice IS the Dirac structure.  RGB/CMY are psi_R/psi_L.
    Spin-1/2 follows from the two-sublattice structure, not as a postulate.

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
      (two uses: probability conservation every tick; wavefunction projection
       after amplitude transfer -- see UnityConstraint.py for full taxonomy)

  SPECIAL CASES:
    Massless (delta_phi=0): cos=1, sin=0 -> full swap per tick (photon)
    Max mass (delta_phi=pi): cos=0, sin=1 -> stays in place

  MOMENTUM:
    Phase-alignment weighting biases the kinetic hop toward aligned neighbors,
    giving net drift.  Inertia scales with omega (1/(1+omega) damping).
    Inertia is the stability of the phase gradient against perturbation;
    heavier particles (larger omega) resist gradient changes more.

  ZITTERBEWEGUNG:
    Amplitude trades between psi_R and psi_L each tick for massive particles.
    At rest: symmetric trading with zero net CoM drift.
    With momentum: asymmetric trading gives net drift at velocity
      v = (c/2) sin(omega) sin(theta)
    where theta is the phase gradient per lattice edge.
    ZB rate = omega/pi ticks; ZB IS the rest mass oscillation (not a separate effect).

  BORN RULE CONNECTION:
    probability_density() = |psi_R|^2 + |psi_L|^2 is the Born probability.
    This is the path-counting identity: for a massless flat-lattice session,
    probability at (x,y,z) after N ticks = P(N,x,y,z) / 6^N, where P is the
    number of distinct N-step paths that reach (x,y,z).  A=1 is the
    normalisation identity sum_x P(N,x) = 6^N.  The Born rule is a tautology,
    not a postulate.  See paper/sections/born_rule_from_paths.tex.

  EMISSION / ABSORPTION (exp_19, exp_20):
    tick(normalize=False) skips per-session A=1 enforcement, allowing the
    caller to manage amplitude across a session group.  See UnityConstraint.py
    for the full taxonomy of A=1 uses (conservation vs projection).

DOCUMENTATION CONVENTION:
  Every non-trivial line of physics code should say what it IS in the theory,
  not just what it does in the program.  Name the mathematical object, cite
  the paper equation where one exists, and state the correspondence explicitly:
  "this IS X" when exact, "this approximates X" in the continuum limit.
  The structure factor comment in _kinetic_hop is the canonical template for
  this convention -- see that method for a worked example.

Paper references:
  Section 3  -- causal_sessions.tex   (Dirac spinor, bipartite tick rule)
  Section 4  -- emergent_kinematics.tex (continuum limit, Dirac derivation)
  Section X  -- born_rule_from_paths.tex (Born rule as path-counting identity)
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
        # in the hot _kinetic_hop path.  Each entry is a 5-tuple:
        #   ((dx,dy,dz), nb_src, nb_dst, out_src, out_dst)
        # (dx,dy,dz): direction vector -- used by _kinetic_hop for Peierls A·v
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

        CONTINUUM LIMIT CONNECTION -- THE STRUCTURE FACTOR:
        In the Dirac derivation (paper Section 4, eq. structure_factor) the
        hop operator over the RGB sublattice is written in Fourier space as:

            H_RGB(k) = (1/3) * sum_{v in RGB} exp(i k.v)

        For a plane wave psi(x) = exp(i k.x), the phase advance in direction v is:

            delta_p(x) = phi(x+v) - phi(x)
                       = angle(psi(x+v)) - angle(psi(x))
                       = k.v                              (exact for a plane wave)

        So  exp(i * delta_p)  evaluated at each node IS exp(i k.v) -- the
        summand of the structure factor evaluated in position space.

        Summing exp(i*delta_p) * source over all RGB directions and dividing by
        n_vec=3 is the position-space implementation of H_RGB(k) applied to psi.

        The Taylor expansion of H_RGB(k) near k=0:
            H_RGB(k) ≈ 1 + (i/3)(1,1,-1).k - (1/6) k^T M k + O(k^3)
        is what the continuum limit recovers.  In position space:
            - the constant 1    -> the identity (no hop, amplitude stays)
            - the (i/3)(1,1,-1).k term -> (i/3)(1,1,-1).grad  (directional derivative)
            - the quadratic k^T M k -> -(1/6) Laplacian (after RGB+CMY cancellation)
        Combined with the cos/sin(delta_phi/2) mass terms in tick(), the full
        Dirac operator (i gamma^mu d_mu - m) emerges in the continuum limit.

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
        precomputed_slices : list of ((dx,dy,dz), nb_src, nb_dst, out_src, out_dst)

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
            delta_p = nb_phase - local_phase   # k.v in position space -- summand of structure factor H_RGB(k)
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
            # exp(i*delta_p) = exp(i k.v): the summand of structure factor H_RGB(k)
            # evaluated at each node in position space.
            # Summing w_i * exp(i*delta_p) * source over all v in RGB gives the
            # position-space action of H_RGB(k) on psi -- what the Taylor expansion
            # approximates as  1 + (i/3)(1,1,-1).k - (1/6)k^T M k + O(k^3).
            emission = source * phase_corr * w_i
            # Shift emission to destination via slice: no np.roll, no mask array
            result[out_dst] += emission[out_src]

        return result

    # ── The Dirac tick ─────────────────────────────────────────────────────────

    def tick(self, normalize=True):
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

        normalize=True (default): enforce per-session A=1 after the tick.
            Standard use for all standalone sessions and exp_19 v4+.
        normalize=False: skip per-session normalization. The caller is
            responsible for enforcing A=1.  Use cases:
              - joint_normalize() across a bound session group
              - Manual amplitude transfer followed by enforce_unity_spinor
                on each session individually (exp_19 v1/v2/v3 architecture)
            See UnityConstraint.py for the full taxonomy of A=1 uses.

        Paper reference: Section 3 (Dirac tick rule, bipartite structure)
        """
        tick_parity = self.tick_counter % 2

        # ── The discrete Hamiltonian: H = omega + V(x)  [Lie algebra element]
        # omega is the rest-mass generator in u(1).
        # V is the topological potential (Coulomb, gravitational, EM, etc.).
        # Their sum is the local phase cost per tick -- the discrete H evaluated
        # at every lattice node simultaneously.
        # Paper: eq. (phase_mismatch)  delta_phi = omega + V
        delta_phi = (self.phase_rotor.omega
                     + self.lattice.topological_potential)        # H(x) -- shape (X,Y,Z)

        # ── The evolution operator: U = exp(i H)  [Lie group element]
        # Exponentiation from the Lie algebra u(1) to the group U(1).
        # cos(delta_phi/2) and sin(delta_phi/2) are the matrix elements of the
        # SU(2) rotation exp(i delta_phi/2 * sigma_x) that mixes the two spinor
        # components.  This is the discrete Schrodinger equation: psi -> U psi.
        # In the continuum limit a->0: U = exp(-iHa) -> 1 - iHa, recovering
        # i d/dt psi = H psi.  The Schrodinger equation is not postulated --
        # it is the definition of exponentiation from the algebra to the group.
        # Paper: eq. (rotor_advance)  r_{n+1} = exp(i omega) * r_n
        cos_half  = np.cos(delta_phi / 2.0)   # kinetic coefficient  -- cos(H/2)
        sin_half  = np.sin(delta_phi / 2.0)   # mass/potential coeff -- sin(H/2)

        if self.is_massless:
            # omega=0 -> delta_phi=V -> cos=1, sin=0 for flat lattice.
            # Pure kinetic hop: the evolution operator has no diagonal (mass) term.
            # Chirality is preserved: psi_R and psi_L never mix directly.
            # This is the photon (massless session): propagates at c=1 node/tick.
            # Even tick: psi_L -> psi_R via RGB; psi_L unchanged.
            # Odd tick:  psi_R -> psi_L via CMY; psi_R unchanged.
            if tick_parity == 0:
                new_psi_R = self._kinetic_hop(self.psi_L, self._rgb_slices)  # kinetic: momentum operator p
                new_psi_L = self.psi_L
            else:
                new_psi_L = self._kinetic_hop(self.psi_R, self._cmy_slices)  # kinetic: momentum operator p
                new_psi_R = self.psi_R
        else:
            # Massive particle: both spinor components updated each tick.
            #
            # ── Kinetic term: cos(H/2) * hop(opposite component)
            #    This is the discrete momentum operator p acting on psi.
            #    hop() shifts amplitude to neighbouring nodes weighted by
            #    the local phase gradient (momentum).  The cross-component
            #    structure (psi_L feeds psi_R and vice versa) is the origin
            #    of Zitterbewegung: the two sublattice components trade
            #    amplitude every tick at the ZB frequency omega/pi.
            #
            # ── Mass term: i*sin(H/2) * (same component in place)
            #    This is the discrete rest-energy + potential term m*psi + V*psi.
            #    No spatial hop: amplitude rotates in phase at each node.
            #    At omega=pi/2: sin=cos=1/sqrt(2), equal kinetic and mass terms.
            #    At omega->pi:  sin->1, cos->0, particle freezes (infinite mass).
            #
            # Together: new_psi = U * psi = exp(i H/2 sigma_x) * psi
            # = [cos(H/2) * kinetic + i*sin(H/2) * identity] applied to spinor.
            # Simultaneous update of both components averages RGB and CMY,
            # giving zero net CoM drift at zero momentum (V1+V2+V3+CMY = 0).
            hop_R = self._kinetic_hop(self.psi_L, self._rgb_slices)  # kinetic: p acting on psi_L
            hop_L = self._kinetic_hop(self.psi_R, self._cmy_slices)  # kinetic: p acting on psi_R
            new_psi_R = cos_half * hop_R      + 1j * sin_half * self.psi_R  # U*psi_R: kinetic + mass
            new_psi_L = cos_half * hop_L      + 1j * sin_half * self.psi_L  # U*psi_L: kinetic + mass
            #           ^-- kinetic term (p)       ^-- mass/potential term (m+V)
            #               cos(H/2) * hop             i*sin(H/2) * in-place

        # ── A=1 constraint: |r| = 1  [U(1) group manifold condition]
        # Enforces the session onto the unit circle after each evolution step.
        # This is NOT a normalisation convention -- it is the statement that the
        # session persists with unit probability (the particle exists after the tick).
        # In Lie group language: the rotor stays on U(1), it never rescales.
        if normalize:
            enforce_unity_spinor(new_psi_R, new_psi_L)
        self.psi_R = new_psi_R
        self.psi_L = new_psi_L

    def probability_density(self) -> np.ndarray:
        """
        Total probability density: |psi_R|^2 + |psi_L|^2.

        This is the Born probability at each lattice node.  For a massless
        session on a flat lattice, it equals the path-count fraction
        P(N, x, y, z) / 6^N: the fraction of all N-step paths from the
        origin that reach node (x,y,z).  A=1 is the statement that this
        fraction sums to one -- the Born rule as a counting identity.
        See paper/sections/born_rule_from_paths.tex.
        """
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
