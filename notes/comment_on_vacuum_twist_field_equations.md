# Vacuum Twist Field Equations — explanatory note

*Written 2026-04-25 as the foundation pass for the eventual paper section.
This note explains what the equation is, why the structure is what it is,
what is genuinely derived, and what is still conjecture.
Distinct from the older `notes/vacuum_twist_field_equations.md`, which is
more of a sketch.*

---

## 1. What the equation actually says

The vacuum twist field equation is a statement that the same phase field
$\phi(\mathbf{x}, t)$ that governs the propagation of every causal session
also governs the long-range vacuum.
Written out:

$$
\Box \phi - \sin^2(\phi/2)\,\phi \;=\; J_\text{grav} + J_\text{em}
$$

with

- $\Box = \partial_t^2 - c^2 \nabla^2$, the d'Alembertian;
- $\sin^2(\phi/2)\,\phi$, the Zitterbewegung self-interaction (mass term);
- $J_\text{grav} = \kappa\,\nabla^2 \rho_\text{clock}$, the gravitational
  source — a *scalar* sourced by the *divergence* of the clock-density
  gradient;
- $J_\text{em} = \varepsilon^{\mu\nu\rho\sigma} \partial_\nu F_{\rho\sigma}$,
  the electromagnetic source — a *vector* sourced by the *curl* of the
  vector potential.

The asymmetry between the two source terms is the whole point.
Gravity is a divergence; electromagnetism is a curl.
They are the two pieces of a Helmholtz decomposition of the phase
gradient field, and the unified equation is what you get when you stop
treating them as independent fields and acknowledge that they are two
ways of deforming the same substrate.

---

## 2. Why the substrate has exactly two ways to deform

Helmholtz's theorem says any sufficiently smooth vector field
$\mathbf{v}(\mathbf{x})$ on $\mathbb{R}^3$ decomposes uniquely into a
gradient part and a curl part:

$$
\mathbf{v} = -\nabla\Phi + \nabla\times\mathbf{A}.
$$

The gradient part has $\nabla\times\mathbf{v} = 0$; the curl part has
$\nabla\cdot\mathbf{v} = 0$.
These are *the* two long-range degrees of freedom of any smooth field on
flat space.
There is no third one, because the Laplacian factors as
$\nabla^2 = \nabla(\nabla\cdot) - \nabla\times(\nabla\times)$ — every
smooth field equation can be split into a "divergence channel" and a
"curl channel" with no remainder.

Apply this to the phase gradient field $\nabla\phi$:

- the divergence $\nabla\cdot(\nabla\phi) = \nabla^2\phi$ tells you where
  phase is being sourced or sunk;
- the curl $\nabla\times(\nabla\phi)$ is identically zero for a smooth
  scalar $\phi$ — but the *vector potential* $\mathbf{A}$ that the lattice
  introduces through the bipartite RGB/CMY structure does have nonzero
  curl, and that curl is what carries electromagnetism.

So the question is not "why does the universe have two long-range forces"
— Helmholtz forced that on us.
The question is: *what physical mechanism populates each channel?*
The answer is the bipartite lattice geometry.

---

## 3. The divergence channel is gravity (well-derived)

The divergence channel is already worked out in
`paper/sections/gravity_as_clock_density.tex` (Section 7), in detail
sufficient to recover Newton.
The argument:

1. A region with more registered sessions has higher
   $\rho_\text{clock}$.
2. The tick rule weights hops by $\cos^2(\delta\phi/2)$ where
   $\delta\phi = \omega + V$, and the weak-field expansion gives
   $p_\text{hop} \approx p_0 - m\,V$.
3. The Boltzmann distribution
   $\rho_\text{clock} \propto \exp(m\,V)$ falls out at equilibrium.
4. Linearising and applying the lattice Laplacian gives Poisson's
   equation $\nabla^2\phi_\text{Newton} = 4\pi G\,\rho_\text{mass}$.

This is a genuine derivation, not a postulate.
The role of $J_\text{grav} = \kappa\,\nabla^2\rho_\text{clock}$ in the
unified equation is to lift Section 7's *static* Poisson result to the
*dynamic* d'Alembertian setting, so that gravitational waves —
not just static potentials — fall out of the same equation.
The lattice analogue of $\kappa$ is computable from the frame condition
$\sum_\mathbf{v} v_i v_j = 6\delta_{ij}$ and the mean clock density,
yielding $\kappa = c^2 / \bar\rho$ in the weak-field limit.

**Status: well-derived.**
The structural identification of gravity with the divergence channel is
not in doubt; only its full coupling to the relativistic d'Alembertian
needs to be tightened in Section 9.

---

## 4. The curl channel is electromagnetism (plausible, not yet derived in detail)

The curl channel is where the paper still has work to do.
The conceptual story is clean but the lattice mechanism has not been
written out the way the gravity derivation has.
Here is the story as it stands:

**Why curl?**
A vacuum deformation that does *not* sink or source phase but *winds*
phase around a closed loop carries no net clock-density change.
It does, however, carry orbital angular momentum in the phase field.
The bipartite lattice has exactly two chiralities — RGB winding and CMY
winding, the two sublattices of the $\Tdiamond$ structure — and these
are the two charge signs.
A "positive" charge is a session whose phase winds one way; a "negative"
charge winds the other way.
The two cannot be deformed into each other without crossing a region of
zero amplitude (the sublattice boundary), which is the topological
content of charge conservation.

**Why $F_{\mu\nu}$?**
The lattice analogue of the four-potential $A_\mu$ is the local phase
offset between the RGB and CMY sublattices.
The antisymmetric tensor
$F_{\mu\nu} = \partial_\mu A_\nu - \partial_\nu A_\mu$
is the obstruction to globally aligning the sublattice phases —
exactly what you would expect for an EM field.
$\varepsilon^{\mu\nu\rho\sigma}\partial_\nu F_{\rho\sigma}$ is the
divergence of the dual tensor, which in flat space is the magnetic
charge density (zero in standard EM, hence a constraint not a source).
The non-zero source on the right is the *electric* current, which in the
unified equation appears as the curl-channel source for $\phi$.

**What is genuinely shown:**
- exp_08 demonstrates numerically that EM deflection is tangential
  (curl-like) while gravity deflection is radial (div-like). The
  geometric distinction is visible at the lattice level.
- The Dirac derivation in Section 6.4 already shows that the bipartite
  RGB/CMY structure produces the gamma matrices, which are the
  algebraic substrate of $F_{\mu\nu}$ in standard QFT.

**What is not yet shown:**
- The continuum-limit derivation of Maxwell's equations from the
  bipartite tick rule. The gravity derivation has its parallel: a
  weak-field expansion, a Boltzmann-like equilibrium, a Poisson-like
  reduction. The EM derivation should look the same, but with the
  *curl* of the sublattice offset rather than the *divergence* of the
  clock density.
- The exact relationship between the lattice $F_{\mu\nu}$ and the
  Peierls substitution already present in `CausalSession._kinetic_hop`.
  The hop rule already uses $\mathbf{A}\cdot\mathbf{v}$ as a phase
  shift; this is the substrate, but it has not been promoted to a
  derivation of $\Box A^\mu = J^\mu$.

**Status: plausible and consistent with everything observed, but the
parallel derivation that makes Maxwell's equations a theorem rather
than a postulate is not yet written.**

---

## 5. The mass term and why it looks like sine-Gordon

The $-\sin^2(\phi/2)\,\phi$ term is the Zitterbewegung self-interaction.
For small $\phi$:

$$
\sin^2(\phi/2)\,\phi \approx \frac{\phi^2}{4}\cdot\phi = \frac{\phi^3}{4}.
$$

This is a $\phi^3$ self-interaction — not the standard $\phi^4$ of
spontaneous symmetry breaking, but cubic, which is the signature of an
asymmetric vacuum.
The full nonlinear form $-\sin^2(\phi/2)\,\phi$ is reminiscent of the
sine-Gordon equation, which famously has soliton solutions of fixed
mass.

This is exciting and unfinished.
If the full equation has soliton solutions, those solitons would be
stable, particle-like configurations of the phase field.
Their masses would be determined by the lattice geometry alone — no
free parameters.
The particle spectrum (electron, muon, tau) might fall out as the
soliton spectrum of this equation.

**Status: structurally suggestive.**
The sine-Gordon analogy is real, but no soliton solutions have been
constructed numerically or analytically.
This is one of the most promising follow-on directions for a future
paper.

---

## 6. The four reductions you can do on the unified equation

A useful way to get one's bearings is to ask what the equation reduces
to in each special case:

| Limit | Equation | Recovers |
|---|---|---|
| $\phi \to 0$, $J_\text{em} = 0$ | $\Box\phi = J_\text{grav}$ | wave eqn for $\phi$, sourced by clock-density Laplacian — gravitational waves |
| $\phi \to 0$, $J_\text{grav} = 0$ | $\Box\phi = J_\text{em}$ | Maxwell wave equation in Lorenz gauge — photons |
| $J_\text{em} = J_\text{grav} = 0$ | $\Box\phi - \sin^2(\phi/2)\phi = 0$ | nonlinear Klein–Gordon (sine-Gordon-like) — massive scalar with self-interaction |
| Static, $J_\text{em} = 0$ | $-c^2\nabla^2\phi = \kappa\nabla^2\rho_\text{clock}$ | Poisson equation — Newtonian gravity |
| Static, $J_\text{grav} = 0$, weak | $-c^2\nabla^2 A^\mu = J_\text{em}$ | Coulomb's law / electrostatics |

Each row of this table is a known theory, and the unified equation is
what they all collapse to in their respective limits.
That is the strongest argument that the equation is doing real work —
it is not a postulate that *contains* the known theories as special
cases, it is one equation whose reductions *are* the known theories.

---

## 7. Why the unification matters

In standard physics, the Maxwell equations and the Einstein equations
are independent.
They have different field contents (a vector $A_\mu$ vs. a tensor
$g_{\mu\nu}$), different gauge structures (U(1) vs. diffeomorphisms),
and different reasons to exist (rotational symmetry of charge vs.
general covariance).
That they are both consistent at the same point in spacetime is a
mystery that the standard model leaves unaddressed.

The vacuum twist picture says they are not independent.
They are two channels of one equation, distinguished only by which
geometric operation (curl vs. divergence) is acting on the phase field.
The two long-range forces are not a coincidence — they are the two
fundamental modes of a Helmholtz decomposition, and the lattice
geometry populates both of them.

This is the deepest unification claim in the paper.
It rises or falls on whether Section 9 can produce the EM derivation
parallel to Section 7's gravity derivation.

---

## 8. What needs to land in the paper section

To convert this conceptual story into the paper section, three things
are needed:

1. **The EM derivation parallel to Section 7's gravity derivation.**
   Start from the Peierls substitution in `_kinetic_hop`, expand in
   weak fields, identify the analogue of the Boltzmann distribution
   for the sublattice phase offset, and reduce to Maxwell's equations
   in the Lorenz gauge.
   This is the load-bearing piece that is not yet written.

2. **The explicit unified equation with $\kappa$ pinned down.**
   Both source terms in lattice units, with the gravitational coupling
   and the EM coupling expressed in terms of lattice geometry alone.
   The fine structure constant $\alpha$ should pop out as a ratio of
   the two coupling strengths if the unification is real.

3. **A worked example or two.**
   Either a static joint EM-gravity solution (a charged mass, like the
   Reissner–Nordström solution but in the lattice picture) or a
   propagating example (an EM wave passing through a gravitational
   well, with a calculable lensing correction beyond GR's prediction).

The first item is the hardest.
The second is mostly bookkeeping once the first is in place.
The third is a small numerical experiment that can be added in
parallel.

---

## 9. Honest assessment

The vacuum twist picture is the most ambitious unification claim in
the paper, and also the one with the largest gap between its conceptual
clarity and its mathematical execution.

The conceptual story is clean: Helmholtz forces two channels;
divergence is gravity (derived); curl is electromagnetism (sketched);
mass is Zitterbewegung self-interaction (consistent with the rest of
the framework).

The mathematics is asymmetric: gravity has been derived end-to-end
from the lattice rules; electromagnetism is currently a postulate with
strong supporting evidence from exp_08 and the Dirac derivation, but
without a parallel weak-field-to-Maxwell continuum-limit calculation.

For the paper to do what its title claims, the EM derivation must be
written.
Until then, the paper presents Section 9 as a unification *proposal*
backed by partial derivations and consistent reductions, not as a
fully-derived theorem.
That is honest, defensible, and still a genuine contribution — but it
is worth being clear-eyed about.
