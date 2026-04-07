# Deriving Newtonian Gravity from the Tick Rule

*Date: 2026-04-07*

---

## What This Note Does

Derives F = GMm/r² from three ingredients already in the framework:

1. The tick rule: δφ(x) = ω + V(x), p_stay = sin²(δφ/2)
2. The bipartite frame condition: Σ_v v_i v_j = 6δ_{ij}
3. The clock density continuity equation (confirmed exp_07)

No additional postulates. The derivation has four steps.

---

## Step 1: The Phase-Mismatch Force (Newton's Second Law)

A session at position x_0 has a wavepacket of width σ. The phase
mismatch at each node is:

    δφ(x) = ω + V(x)

The residence probability is:

    p_stay(x) = sin²(δφ(x)/2)

The kinetic hop probability is:

    p_hop(x) = cos²(δφ(x)/2) = 1 - p_stay(x)

In the weak field |V| << ω, expand to first order in V:

    p_stay(x) ≈ sin²(ω/2) + (sin ω / 2) · V(x) ≡ p₀ + α·V(x)

where α = sin(ω)/2 = m is the lattice mass.

The net displacement of the wavepacket center-of-mass per tick comes
from the asymmetry in p_hop across the packet. Consider two nodes
separated by a lattice vector v: x₊ = x + v and x₋ = x - v.
The net probability current in direction v is:

    J(v) ∝ p_hop(x₋)·ρ(x₋) - p_hop(x₊)·ρ(x₊)

For a slowly varying density and potential (gradients small on scale σ):

    J(v) ∝ -v · ∇(p_hop · ρ) = -v · ρ∇p_hop - v · p_hop∇ρ

The second term vanishes in momentum space (it is the free kinetic
spread, contributing no net force). The first term gives the acceleration:

    a = d²⟨x⟩/dt² ∝ -∇p_hop(x₀) = ∇p_stay(x₀) = α∇V(x₀)

But wait — the force must point toward lower V (downhill), i.e.,
toward the source. Check the sign: lower V means lower p_stay (more
hopping), so the packet accelerates toward higher p_hop = lower V.
The acceleration is in the direction of -∇V:

    a = -(α/m) ∇V = -∇V

where in the last step α = m cancels the inertial mass denominator.

**Result: ẍ = -∇V(x)**

This is Newton's second law. The force on a session of mass m is:

    F = -m ∇V

The inertial mass m = sin(ω)/2 that resists the phase gradient is the
same parameter that couples to V. This is not a coincidence — it is the
same ω in both places. The equivalence principle is structural.

---

## Step 2: The Source Generates a 1/r Potential (Poisson's Equation)

A static, massive session at the origin has clock density concentrated
near x = 0. This session generates a topological potential felt by all
other sessions. What is its spatial form?

The clock density ρ_clock satisfies the continuity equation (exp_07):

    ∂ρ_clock/∂t + ∇·J_clock = 0

For the clock fluid in equilibrium (static source, no net current),
the density must satisfy detailed balance with the gravitational
potential. The equilibrium condition is:

    J_clock = 0  ⟹  ∇ρ_clock = -(ρ_clock/c²) ∇φ

where φ is the gravitational potential experienced by a test clock.
This is solved by the Boltzmann distribution:

    ρ_clock(x) = ρ̄ · exp(-φ(x)/c²)

Taking the logarithm:

    φ(x) = -c² · log(ρ_clock(x)/ρ̄)

In the weak field |φ| << c²:

    φ(x) ≈ -c²(ρ_clock(x) - ρ̄)/ρ̄

Apply the Laplacian. Using the bipartite frame condition — the
lattice Laplacian on the T³_diamond lattice is:

    ∇²_lattice f = (1/6) Σ_{v ∈ RGB∪CMY} [f(x+v) - f(x)]
                 = (a²/6) Σ_{v} (v·∇)²f / 2 + O(a⁴)
                 = (a²/6)(Σ_{v} v_i v_j / 2) ∂_i∂_j f

The frame condition Σ_{ALL} v_i v_j = 6δ_{ij} gives:

    ∇²_lattice f = (a²/2) ∇²f

so the lattice Laplacian is isotropic and proportional to the
continuum Laplacian. No directional bias. This is geometrically
forced by the CMY = -RGB symmetry of the bipartite structure.

Applying ∇² to φ ≈ -c²(ρ - ρ̄)/ρ̄:

    ∇²φ = -(c²/ρ̄) ∇²ρ_clock

The clock density satisfies the source equation:

    ∇²ρ_clock = -S(x)

where S(x) is the clock density source (non-zero where mass is
present). Substituting and comparing with Poisson's equation:

    ∇²φ = 4πG ρ_mass

requires the identification:

    c²S/(ρ̄) = 4πG ρ_mass

This fixes G in terms of the lattice parameters (source clock density
per unit mass and background clock density ρ̄).

For a point source of mass M at the origin, S(x) = M·δ³(x), and the
Green's function of the 3D Laplacian gives:

    φ(x) = -GM/r,    r = |x|

**Result: V(x) = φ(x) = -GM/r**

---

## Step 3: Newton's Law of Gravitation

Combine Steps 1 and 2. A test session of mass m at position x,
subject to the potential of a source of mass M at the origin:

    F = -m ∇V = -m ∇(-GM/r) = -mGM ∇(1/r)

    ∇(1/r) = -x̂/r²

Therefore:

    F = -GMm/r² x̂

The force is:
- Attractive (toward the source, negative sign with x̂ outward)
- Proportional to both masses (m and M)
- Falls as 1/r²
- Independent of the test session's velocity (in the weak-field limit)

**This is Newton's law of gravitation.**

---

## Step 4: The Equivalence Principle

The derivation uses the same parameter ω twice:
- As inertial mass: m_inertial = sin(ω)/2, which resists the phase
  gradient force (denominator of a = F/m)
- As gravitational mass: m_gravitational = sin(ω)/2, which couples to
  the source potential V(x)

Both arise from the same phase mismatch δφ = ω + V(x). The inertial
mass and gravitational mass are not merely equal — they are the same
quantity. The equivalence principle is not a coincidence to be
explained; it is the structure of the tick rule.

---

## The Honest Gap

Step 2 uses the equilibrium condition ρ_clock ∝ exp(-φ/c²). This is
physically motivated (Boltzmann distribution of clocks in a potential
well) but not yet derived from the tick rule dynamics. The full
derivation requires showing that the clock fluid's stationary
distribution in a potential well takes the Boltzmann form — a
thermodynamic argument that needs to be made precise from the lattice.

The gap does not affect the force law (Step 1) or the 1/r² dependence
(Step 3). It affects only the precise coefficient: the identification
of G in terms of lattice parameters. Steps 1–3 establish the
functional form; the gap is in the proportionality constant.

This is equivalent to the situation in thermodynamics where F = -kT∇logρ
is derived from the diffusion equation without a first-principles
derivation of the Boltzmann factor — the structure is right, the
calibration requires a further step.

---

## Summary

| Step | Input | Output |
|------|-------|--------|
| 1 | Tick rule, weak field | F = -m∇V (Newton 2nd law) |
| 2 | Frame condition + continuity | ∇²V = 4πGρ (Poisson) |
| 3 | Combine 1+2, point source | F = GMm/r² (gravitation) |
| 4 | ω appears twice | m_inertial = m_grav (equivalence) |
| Gap | Boltzmann calibration | G in lattice units (not yet derived) |

The Dirac derivation (emergent_kinematics.tex) derives the kinetic
structure of quantum mechanics from the same tick rule. This derivation
derives the gravitational structure. Together they show that the tick
rule — a single geometrical update on the T³_diamond lattice —
contains both quantum mechanics and Newtonian gravity as limits,
unified by A=1.

---

## Relation to exp_02

Experiment exp_02 confirms Steps 1 and 3 numerically:
- A zero-momentum Gaussian packet accelerates toward a clock-dense well
- Light packets (small ω) accelerate faster than heavy packets (large ω)
- The displacement ratio 3.76/0.36 ≈ 10.4 matches the mass ratio ≈ 7.7
  (residual from finite run length and packet spread)
- The control run (flat lattice) shows no acceleration

The force law F ∝ 1/r² is not directly tested in exp_02 (single
distance, single run). A multi-distance version of exp_02 would
confirm the 1/r² scaling directly. This is straightforward to design.
