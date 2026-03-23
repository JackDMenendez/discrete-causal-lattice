# vacuum_twist_field_equations.md
# The Unified Phase Field Equation and Vacuum Twist

## The Three Regimes of delta_phi

| delta_phi       | p_stay          | p_move          | Physical meaning        |
|-----------------|-----------------|-----------------|-------------------------|
| 0               | 0               | 1               | Photon -- massless       |
| pi/2            | 0.5             | 0.5             | Intermediate mass        |
| pi              | 1               | 0               | Infinite mass/confinement|
| constant uniform| symmetric       | symmetric       | Rest mass only           |
| constant gradient| asymmetric bias | asymmetric bias | Constant velocity        |
| changing gradient| grad changes   | grad changes    | Acceleration / force     |

## Newton's Laws from Phase Geometry

Newton 1 (Inertia):
  Constant phase gradient -> constant momentum bias -> straight-line motion
  No gradient change -> no acceleration
  Emerges from U(1) phase coherence, not postulated

Newton 2 (F = ma):
  F = grad(delta_phi)     -- spatial change in phase mismatch
  m = sin^2(delta_phi/2)  -- residence probability (Zitterbewegung mass)
  a = F/m                 -- phase gradient curvature per unit mass

Newton 3 (Action/Reaction):
  A twist in the vacuum that pushes a particle right
  must curve back on itself -- the source of the field is pushed left
  Emerges from A=1 conservation globally

## Gravity vs Electromagnetism: Two Types of Vacuum Deformation

  GRAVITY:   div(phi) != 0    -- sources and sinks of phase (scalar)
             Clock density well: phase flows TOWARD the well
             Always attractive: divergence has one sign near mass
             Schwarzschild metric emerges in continuum limit

  EM:        curl(phi) != 0   -- rotational twist of phase (vector)
             Electromagnetic vortex: phase WINDS around the source
             Can be attractive or repulsive: curl winds either way
             Two chiralities = two charge signs
             Maxwell's equations emerge in continuum limit

This is why gravity couples to everything (all phase fields have divergence
near mass) while EM only couples to charged particles (only chiral phase
fields have nonzero curl near the source).

## The Unified Phase Field Equation

The vacuum phase field phi(x,y,z,t) satisfies:

  Box(phi) = -sin^2(phi/2) * phi        [Zitterbewegung / mass term]
           + epsilon_munu * d^nu F^mu   [EM curl source -- J_em]
           + kappa * Laplacian(rho_clock) [gravitational div source -- J_grav]

where:
  Box = d^2/dt^2 - c^2 * Laplacian  (d'Alembertian / wave operator)
  F^mu = curl(A)                     (EM field tensor)
  rho_clock                          (clock density field)

For massless field (phi -> 0): reduces to the wave equation -- photon
For massive field with no sources: Klein-Gordon equation
For EM source only: Maxwell's equations in Lorenz gauge
For gravitational source only: linearized Einstein equations (weak field)

## The Klein-Gordon Connection

The mass term -sin^2(phi/2)*phi for small phi reduces to:
  -sin^2(phi/2)*phi ~ -(phi/2)^2 * phi = -(phi^2/4) * phi

This is a phi^3 self-interaction. For small oscillations around phi=0:
  sin^2(phi/2) ~ phi^2/4 ~ (m/hbar)^2 in natural units

So the Zitterbewegung frequency omega = sqrt(4 * sin^2(omega_0/2))
which for small omega_0 gives omega ~ omega_0 = mc^2/hbar
exactly the Compton frequency. Mass encodes the Zitterbewegung rate.

## Differential Equation for the Vacuum Twist

Define the phase gradient vector field k = grad(phi).
The evolution equations are:

  dk/dt = -grad(delta_phi)                 [gradient evolves by curvature]
  d(delta_phi)/dt = -c^2 * div(k) + omega_0^2 * phi  [restoring force]

This is a COUPLED WAVE SYSTEM -- identical structure to Maxwell's equations
(E and B coupled through curls and divergences), which is why Maxwell's
equations are hiding inside the lattice phase dynamics.

Substituting: d^2(phi)/dt^2 = c^2 * Laplacian(phi) - omega_0^2 * phi
This IS the Klein-Gordon equation. Derived from lattice geometry.

## Acceleration as Differential Zitterbewegung

If delta_phi varies across the wavefront:
  Left side of packet: delta_phi_L -> p_stay_L
  Right side of packet: delta_phi_R -> p_stay_R

  p_stay_L != p_stay_R -> differential residence time
  -> Left side lags, right side advances
  -> Packet steers WITHOUT any force vector

Acceleration a proportional to grad(delta_phi) across the packet width.
For gravitational well: delta_phi increases with clock density
-> packets steer toward clock-dense regions
-> This is gravity, derived purely from differential Zitterbewegung

## Fine Structure Constant (revised derivation)

alpha ~ ratio of EM twist amplitude to lattice spacing
      = strength of curl(phi) relative to the Compton wavelength

In natural lattice units at Compton calibration:
  The curl must be weak enough that the EM interaction does not
  break the bipartite structure of the vacuum (it must not turn
  a photon into a massive particle via the twist alone).

The stability threshold: curl(A) < sin^2(pi/2) * (1/lambda_C)
  -> alpha < 1/(4 * pi) * something_geometric

Exact derivation: TODO in exp_08_vacuum_twist.py
This is a cleaner path to alpha than v1.0's Gambler's Ruin.

## Open Questions

1. Does the full nonlinear equation Box(phi) = -sin^2(phi/2)*phi
   have soliton solutions? These would be stable massive particles.

2. Do two interacting solitons reproduce the Coulomb and
   gravitational inverse-square laws in the far field?

3. Is the Dirac equation hidden here?
   The bipartite structure (left/right handedness) suggests yes.
   The two sublattices might be the two spinor components.

4. Does the lattice spontaneously break the RGB/CMY symmetry?
   If so, this could be the Higgs mechanism -- mass from symmetry breaking.
