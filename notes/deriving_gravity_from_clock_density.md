# Deriving Gravity from the Clock Density Field

*Date: 2026-04-04*

---

## The Situation

The same five-step programme that derives the Dirac equation from the
bipartite tick rule must be applied to the clock density field to derive
gravity. The two derivations are structurally parallel.

| Step | Dirac | Gravity |
|------|-------|---------|
| 1 | Two-tick master equation | Continuity equation from tick() |
| 2 | Taylor expand hop operator | Taylor expand density evolution |
| 3 | Identify continuum PDE | Identify Poisson equation |
| 4 | Identify gamma matrices | Identify gravitational potential φ |
| 5 | Clifford algebra check | Poisson → Einstein field equations |
| 6 | O_h averaging (cancels algebraically) | Isotropy (cancels algebraically) |

Steps 1–3 are mechanical. Step 4 has one honest gap (see below).
Steps 5–6 require formal work but the path is clear.

---

## Step 1: The Starting Point

From `exp_07`, the discrete conservation of clock count at every tick
implies the continuity equation in the continuum limit:

    ∂ρ_clock/∂t + ∇·J_clock = 0

This is the lattice analogue of the Dirac two-tick master equation.
It is numerically confirmed to 10⁻¹⁵ (machine precision) and the
finite-difference residual is consistent with O(a²) truncation error.

The clock density field evolves under the topological potential:

    V(x) = -STRENGTH / (r + SOFTENING)

The phase advance at each node is:

    δφ(x) = ω + V(x,y,z)

---

## Step 2: Taylor Expand the Density Evolution

The clock density at node x evolves by receiving contributions from
all six neighbours via the hop operator. Expanding ρ(x + a·v) around x:

    ρ(x + a·v) = ρ(x) + a(v·∇)ρ + (a²/2)(v·∇)²ρ + O(a³)

Summing over ALL SIX basis vectors (both RGB and CMY):

    sum_{ALL} v = sum_{RGB} v + sum_{CMY} v
                = (1,1,-1) + (-1,-1,1) = 0

**The first-order terms cancel exactly because CMY = -RGB.**

The second-order terms survive:

    sum_{ALL} v_i v_j = sum_{RGB} v_i v_j + sum_{CMY} v_i v_j = 6δ_ij

(Both sublattices contribute the same frame condition sum, giving 2×3δ_ij.)

So to leading order in a:

    ⟨ρ⟩(x) = ρ(x) + (a²/6) ∇²ρ + O(a⁴)

The update rule for clock density is therefore:

    ρ(x, t+1) - ρ(x, t) = (a²/6) ∇²ρ + S(x)

where S(x) is the session source term — nonzero where mass is present.

**Key point:** The isotropy of the Laplacian falls out automatically from
the frame condition sum_{ALL} v_i v_j = 6δ_ij. There is no directional
asymmetry to average away. This is the gravitational analogue of the
Dirac result: both are geometric consequences of the bipartite frame
condition.

---

## Step 3: The Continuum Limit — Poisson's Equation

Dividing by the tick duration τ and taking a→0, τ→0 with D = a²/(6τ) fixed:

    ∂ρ_clock/∂t = D ∇²ρ_clock + S(x)

where D = a²/6 is the clock diffusion coefficient and S(x) is the
session source density (mass distribution).

In the static limit ∂ρ/∂t = 0:

    ∇²ρ_clock = -S(x)/D

This IS Poisson's equation. The gravitational potential φ = f(ρ_clock)
satisfies:

    ∇²φ = 4πG ρ_mass

if f is chosen appropriately. The weak-field identification is:

    φ ∝ log(ρ_clock / ρ̄)

which gives ∇²φ ∝ ∇²(ρ - ρ̄)/ρ̄ in the weak-field expansion, reproducing
Poisson's equation to leading order.

---

## Step 4: The Geodesic Equation (Newton's Law)

In the Dirac case, Step 4 identifies the gamma matrices from the first-order
gradient terms. In the gravity case, Step 4 identifies the force law.

Acceleration of a session is differential Zitterbewegung across a packet's
width. The phase advance δφ(x) = ω + V(x) varies spatially. The packet
steers toward lower V — toward higher clock density — because hops toward
nodes with lower phase cost are favoured. In the continuum limit:

    ẍ = -∇V = -∇φ

This is Newton's law of gravitation.

The GR correction — the geodesic equation — requires going to second order
in V/c². This is the post-Newtonian expansion. The first correction is:

    ẍ = -∇φ (1 + 2φ/c²) + O(φ²/c⁴)

recovering the Schwarzschild correction to the geodesic.

---

## Step 5: From Poisson to Einstein

The static Poisson equation is the weak-field, slow-motion limit. The
full clock fluid equations (continuity + momentum):

    ∂ρ/∂t + ∇·J = 0
    ∂J/∂t + (J·∇)J = -(c²/ρ)∇ρ + (V(ρ) - J)/τ

define a stress-energy tensor T^{μν} = f(ρ_clock, J_clock). In the
continuum limit a→0, τ→0 with c = a/τ fixed, these reduce to the
Einstein field equations:

    G_{μν} = 8πG T_{μν}

with the spacetime metric identified as g_{μν} = f(ρ_clock, J_clock).

The explicit derivation of the metric functional f is the main open
problem — see "The Honest Gap" below.

---

## Step 6: Symmetry

Unlike the Dirac case, gravity does not require a separate symmetry
averaging step. Because both RGB and CMY sublattices contribute to the
clock density evolution — the full-tick Laplacian — the first-order
directional asymmetry already cancels algebraically at Step 2:

    sum_{ALL} v = 0

The isotropic Laplacian falls out without invoking O_h averaging.
This is actually simpler than the Dirac case.

---

## The Honest Gap

The missing piece is the explicit form of:

    φ = f(ρ_clock)

The functional form must satisfy three requirements simultaneously:

1. **Weak field:** φ = -GM/r reproduces Poisson's equation
2. **Time dilation:** dτ/dt = √(1 - 2φ/c²) matches Schwarzschild
3. **Clock density relation:** ρ_clock ∝ e^{-φ/c²} in weak field

Requirement 3 is plausible from the clock fluid picture: regions of
high gravitational potential have fewer clocks per unit volume because
clocks drift toward lower potential (denser clock regions). So:

    ρ_clock(x) = ρ̄ · exp(-φ(x)/c²)

Taking the logarithm:

    φ(x) = -c² · log(ρ_clock(x) / ρ̄)

This gives Poisson in the weak field:

    ∇²φ = -c²/ρ̄ · ∇²ρ ≈ -(c²/ρ̄) · (-S/D) = c²S/(ρ̄D) ∝ 4πG ρ_mass ✓

And reproduces gravitational time dilation:

    dτ/dt = ρ_clock(x)/ρ̄ = exp(-φ/c²) ≈ √(1 - 2φ/c²) for small φ/c² ✓

**The gap:** this relation needs to be derived from the lattice dynamics,
not assumed. The derivation requires showing that the clock density
equilibrium distribution in the presence of a mass source takes the
Boltzmann form ρ ∝ exp(-φ/c²). This follows if the clock fluid satisfies
detailed balance with the gravitational potential acting as an energy
functional — a thermodynamic argument that needs to be made precise.

---

## What exp_16 Adds

The proton mass sweep tests the gravity-quantum boundary: whether the
recoil dynamics of an active nucleus are necessary for orbital stability.
The recoil rate is set by the proton's clock density (its ω parameter).
If heavier protons produce longer settling times monotonically, the
symmetry-breaking mechanism is confirmed as gravitational in origin.

---

## Status

| Step | Task | Status |
|------|------|--------|
| 1 | Continuity equation from tick() | DONE (exp_07, §7.4) |
| 2 | Taylor expand density evolution | DONE (this note) |
| 3 | Poisson equation in static limit | DONE (§8.6) |
| 4 | Geodesic equation / Newton's law | DONE (exp_02, §7.2) |
| 5 | Full Einstein field equations | PARTIAL (§8.6, metric f not derived) |
| 6 | Isotropy (algebraic cancellation) | DONE (this note) |
| GAP | Derive ρ_clock ∝ exp(-φ/c²) from lattice dynamics | NOT DONE |
| 7 | Write formal proof for paper | NOT DONE |

---

## The Payoff

**Without this derivation:**
> "Clock density gradients produce gravitational-like attraction."

**With this derivation:**
> "Gravity is the continuum limit of clock density conservation on
> the bipartite lattice. The Einstein field equations emerge from
> the clock fluid equations by the same Taylor expansion that produces
> the Dirac equation from the tick rule. The gravitational potential
> is the logarithm of the clock density contrast — a consequence of
> the lattice dynamics, not a postulate."

That is the same upgrade the Dirac derivation gave to the kinematics.
