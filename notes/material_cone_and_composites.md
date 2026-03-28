# Material Cone and Composite Particles

## The Material Cone

Every CausalSession has a *material cone* — the lattice analogue of the light cone,
but for massive particles.  The cone half-angle is set by the residence probability:

    p_move     = cos²(ω/2)             # kinetic fraction per tick
    p_stay     = sin²(ω/2)             # mass fraction per tick
    θ          = arcsin(√p_move)       # material cone half-angle
                = arcsin(cos(ω/2))

Special cases:

- Photon (ω=0):     θ = 45°  — full light cone
- Massive (ω>0):    θ < 45°  — sub-luminal material cone
- Max-mass (ω=π):   θ = 0°   — no spreading, pure clock

The material cone is the region of spacetime reachable by the session's probability
amplitude.  Its 3D cross-section at tick t is the support of the probability density.

### Connection to Bohr orbits

The electron's time-averaged radial PDF P(r) measured in exp_11 is the projection of
the swept material cone onto 3D space.  As the electron orbits, the cone sweeps the
orbital ring.  The ring width Δr satisfies:

    Δr / r_n  ≈  v / c  =  k_n / ω

The Bohr quantization condition k_n = n/r_n is the condition for the cone to close on
itself in phase with the internal Zitterbewegung after n full rotations.  Off-resonance
k values produce cones that walk around the orbit without closing — hence a broad P(r).

Falsifiable: measure Δr from the n=1 PDF in data/quantization_scan_n1_pdf.npy and
compare against k_Bohr/ω = 0.0971/0.1019 ≈ 0.95.  (The ring should be wide for n=1
since v/c is near 1 in lattice units; narrower for larger n.)

---

## Composite Particles and Cone Cancellation

A composite neutral object (neutron, hydrogen atom, rock) is a bound collection of
sessions whose constituent phases cancel, suppressing the net phase gradient that
drives spreading.

### Charge as RGB/CMY imbalance

Charge in the bipartite lattice is an asymmetry between RGB and CMY activity.  A
session's "charge proxy" is the difference in total amplitude between components:

    Q_proxy  =  Σ|ψ_R|² - Σ|ψ_L|²  ∈ [-1, 1]

- Charged particle (electron): Q_proxy ≠ 0, one sublattice dominates
- Neutral composite:           Σ Q_proxy_i = 0  across all constituents

### Cone cancellation mechanism — phase cancellation

The kinetic hop in CausalSession._kinetic_hop is driven by the phase gradient:

    delta_p(r, v)  =  φ(r + v) - φ(r)   -- phase advance in direction v

The hop weight in direction v is proportional to max(0, delta_p), so the session
drifts toward regions of higher phase.  The DIRECTION and RATE of spreading is
entirely determined by ∇φ.

For a composite of N bound sessions, the combined phase field is:

    Φ(r)  =  arg( Σ_i  ψ_i(r) )

For a neutral composite (charge = 0), the constituent phases cancel:

    Σ_i  ψ_i(r)  ≈  small                (destructive interference)
    ∇Φ(r)        ≈  0                     (no net phase gradient)

With no phase gradient, the kinetic hop has no preferred direction.  The
uniform fallback (no directional bias) produces isotropic spreading at the
maximum rate — BUT the combined AMPLITUDE is suppressed by the cancellation,
so the probability barely moves.

The composite appears massive (small cone angle) not because its RGB/CMY hops
balance, but because its constituent phases destructively interfere, eliminating
the gradient that drives directional spreading.

This is the lattice mechanism for the quantum-to-classical transition:

- Individual charged particle:  phase gradient ≠ 0 → directed hop → spreading
- Neutral composite:            phases cancel → ∇Φ ≈ 0 → no directed hop → localized
- Macroscopic neutral object:   ~10^25 cancelling phases → classical worldline

### The magnetic moment exception

The neutron has zero charge but non-zero magnetic moment.  In the lattice:

- Charge cancellation: net Σ Q_proxy = 0  (RGB/CMY balanced)
- Magnetic moment:     non-cancelling SPIN structure of the internal phase gradients

The spin contribution (angular structure of each session's phase gradient) does NOT
cancel in the same way as the translational phase gradient.  This is the distinction
between the EM field (curl of the combined phase gradient, cancels for neutral
composites) and the magnetic moment (curl of the probability current, persists even
after the translational phases cancel).

---

## Design: Where This Fits in the Core Classes

### CausalSession.py — added

`cone_half_angle` (property): returns arcsin(cos(ω/2)) in radians.

`rgb_cmy_imbalance` (property): returns Σ|ψ_R|² - Σ|ψ_L|².
Proxy for net charge.  +1 = fully right-handed; -1 = fully left-handed; 0 = neutral.

### TickScheduler.py — documented

The pairwise interaction already mixes phases between co-located sessions.
For a bound composite, this interaction should be STRONGER (large coupling)
so that the sessions move together.  Currently coupling = 0.1.

Binding strength = coupling coefficient in _apply_pairwise_interactions.
A bound composite has coupling → 1; free particles have coupling → 0.

### CompositeCausalSession — future class

A wrapper around N CausalSessions that:

- Evolves all constituents each tick (in order)
- Enforces binding: re-centers constituents around shared CoM each tick
- Exposes `effective_cone_half_angle()` — net cone after phase cancellation
- Exposes `charge_balance()` — Σ Q_proxy_i (should be ~0 for neutron)
- Exposes `probability_density()` — |Σ ψ_i|² (interference included)
- Exposes `magnetic_moment_proxy()` — Σ r_i × J_i (angular current)

The key distinction: `probability_density()` must use |Σ ψ_i|² (coherent sum),
not Σ |ψ_i|² (incoherent sum).  The phase cancellation only appears in the
coherent sum.  The incoherent sum gives the individual-particle result with no
cancellation.

The effective cone prediction:

- Phase-cancelling neutral composite: θ_eff → 0 as cancellation improves
- Residual θ_eff is the magnetic moment contribution (spin phases don't cancel)

### Experiment (future)

exp_13_composite_cone.py: bind 2 sessions with opposite Q_proxy
(one RGB-dominant, one CMY-dominant).  Measure effective spreading rate
vs. coupling strength using the COHERENT probability density |ψ_1 + ψ_2|².
Prediction: effective θ < either individual θ when coupling is strong.
