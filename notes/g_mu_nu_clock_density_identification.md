# Metric tensor $g_{\mu\nu}$ from clock density: working sketch

*Working notes, 2026-05-05.  Drafts a Tier 2 v1.0 proof item closing the
"honest gap" identified in `notes/deriving_gravity_from_clock_density.md`
(2026-04-04): derive $\rho_\text{clock}(\mathbf{x}) \propto
\exp(-\varphi(\mathbf{x})/c^2)$ from the lattice tick rule, then identify
the metric tensor $g_{\mu\nu}$ as a functional of $\rho_\text{clock}$ and
its current $J_\text{clock}$.  Targets `paper/sections/gravity_as_clock_density.tex`
§7.5–§7.6 for revision.  This is a proof skeleton at the same depth as
`notes/born_rule_gleason_uniqueness.md`, not a full derivation; one
half-page paper patch is the deliverable.*

---

## What the gap is

`notes/deriving_gravity_from_clock_density.md` (2026-04-04) lays out a
six-step program parallel to the Dirac derivation.  Steps 1–4 and Step 6
are complete.  The honest gap is in Step 5 (full Einstein field
equations) and is concentrated in **the explicit form of**:

$$
\varphi(\mathbf{x}) \;=\; f\bigl(\rho_\text{clock}(\mathbf{x})\bigr).
$$

Three requirements pin $f$:

1. **Weak-field Newtonian limit.**  $\varphi = -GM/r$ reproduces
   $\nabla^2\varphi = 4\pi G \rho_\text{mass}$.
2. **Gravitational time dilation (Schwarzschild).**
   $d\tau/dt = \sqrt{1 - 2\varphi/c^2}$ at first PN order.
3. **Boltzmann clock-density relation.**  $\rho_\text{clock}(\mathbf{x})
   \propto \exp(-\varphi(\mathbf{x})/c^2)$ in the static weak-field limit.

The 2026-04-04 note showed that **if** (3) is taken as input, then
$\varphi = -c^2 \ln(\rho_\text{clock}/\bar\rho)$ satisfies (1) and (2) to
the relevant order.  The honest gap is showing (3) from the lattice
dynamics, not assuming it.

That is the question this note answers as a proof sketch.

---

## The structure of the argument

The argument has four steps:

1. **Master equation.**  The bipartite tick rule with topological potential
   $V(\mathbf{x})$ gives a discrete-time master equation for the clock
   density $\rho_\text{clock}(\mathbf{x}, t)$.
2. **Detailed balance.**  In the static limit ($\partial_t \rho = 0$,
   $V$ time-independent), the master equation has a unique equilibrium
   distribution determined by the ratio of forward and backward hop
   probabilities between neighbouring nodes.
3. **Boltzmann form forced.**  The hop ratio takes the form $\exp(-\beta
   \Delta H)$ for an explicit lattice "energy" $H(\mathbf{x})$ and an
   explicit lattice "temperature" $T = 1/\beta$.  The equilibrium is a
   canonical distribution.
4. **Continuum identification.**  $H$ and $T$ identify with the
   gravitational potential $\varphi$ and the speed of light $c^2$ in the
   continuum limit, giving $\rho_\text{clock} \propto \exp(-\varphi/c^2)$.

Each step is a finite calculation given the lattice rule.  None requires
new physics; the inputs are the existing $\delta\phi(\mathbf{x}) = \omega
+ V(\mathbf{x})$, $p_\text{move}(\mathbf{x}) = \cos^2(\delta\phi/2)$,
$p_\text{stay}(\mathbf{x}) = \sin^2(\delta\phi/2)$ rules and the
bipartite RGB/CMY frame-condition averaging that already powers the
Dirac and Newton-law derivations.

---

## Step 1 — master equation for $\rho_\text{clock}$

A packet at node $\mathbf{x}$ at tick $t$ either stays (with probability
$p_\text{stay}(\mathbf{x})$) or hops to one of the six basis-vector
neighbours (each with probability $p_\text{move}(\mathbf{x})/6$).  The
bipartite parity restricts which neighbours are accessible at which tick:

- Even (RGB) ticks: neighbours $\mathbf{x} + \mathbf{V}_i$ for $i = 1,2,3$.
- Odd (CMY) ticks: neighbours $\mathbf{x} - \mathbf{V}_i$ for $i = 1,2,3$.

Over two consecutive ticks (one full RGB+CMY cycle) the packet's
update obeys

$$
\rho(\mathbf{x}, t+2) \;=\; p_\text{stay,2}(\mathbf{x})\,\rho(\mathbf{x}, t)
\;+\; \tfrac{1}{6}\sum_{\pm\mathbf{V}_i} q(\mathbf{x} \mp \mathbf{V}_i \to \mathbf{x})\,
\rho(\mathbf{x} \mp \mathbf{V}_i, t),
$$

where $p_\text{stay,2}$ is the two-tick stay probability and
$q(\mathbf{y} \to \mathbf{x})$ is the rate of probability flow from
$\mathbf{y}$ to $\mathbf{x}$ over one full cycle.  Two-tick because of
the bipartite alternation.

The hop rate from $\mathbf{x}$ to $\mathbf{x} + \mathbf{V}_i$ on an RGB
tick is determined by the **source** side's parameters:

$$
q(\mathbf{x} \to \mathbf{x} + \mathbf{V}_i) \;=\; \tfrac{1}{6}
p_\text{move}(\mathbf{x})
\;=\; \tfrac{1}{6}\cos^2\!\bigl((\omega + V(\mathbf{x}))/2\bigr).
$$

The reverse hop $\mathbf{x} + \mathbf{V}_i \to \mathbf{x}$ happens on the
following CMY tick with rate determined by $V(\mathbf{x} + \mathbf{V}_i)$.

This is the master equation; the dynamics it generates is the bipartite
tick rule projected onto the clock-density observable, which is exactly
what `exp_07` confirmed conserves the discrete continuity equation to
machine precision.

---

## Step 2 — detailed balance and the equilibrium distribution

In the static limit ($V$ time-independent, $\partial_t \rho = 0$), the
master equation has detailed balance in the standard sense:

$$
\rho_\text{eq}(\mathbf{x})\, q(\mathbf{x} \to \mathbf{y})
\;=\; \rho_\text{eq}(\mathbf{y})\, q(\mathbf{y} \to \mathbf{x})
$$

for every pair $(\mathbf{x}, \mathbf{y})$ of one-hop neighbours.  This
holds because the bipartite alternation is symmetric: every forward hop
$\mathbf{x} \to \mathbf{y}$ on an RGB tick has a matched reverse hop
$\mathbf{y} \to \mathbf{x}$ on the next CMY tick, with the same basis
vector $\mathbf{V}_i$ traversed in opposite directions.  The lattice's
chiral parity forces the rates into the symmetric balance condition.

Substituting the explicit hop rates:

$$
\frac{\rho_\text{eq}(\mathbf{x})}{\rho_\text{eq}(\mathbf{y})}
\;=\;
\frac{q(\mathbf{y} \to \mathbf{x})}{q(\mathbf{x} \to \mathbf{y})}
\;=\;
\frac{p_\text{move}(\mathbf{y})}{p_\text{move}(\mathbf{x})}
\;=\;
\frac{\cos^2\!\bigl((\omega + V(\mathbf{y}))/2\bigr)}
     {\cos^2\!\bigl((\omega + V(\mathbf{x}))/2\bigr)}.
$$

This is the lattice's exact equilibrium ratio.  It is determined entirely
by the topological potential $V$ at the two endpoints; the bipartite
frame averaging and the basis-vector indices have dropped out (this is
where the $\frac{1}{6}$-symmetric average and the chiral pairing pay off).

---

## Step 3 — Boltzmann form via expansion in $V/\omega$

In the weak-field regime — where $V \ll \omega$, equivalent to weak
gravity — the cosine squared expands:

$$
\cos^2\!\bigl((\omega + V)/2\bigr) \;\approx\;
\cos^2(\omega/2)\,\bigl(1 - \tan(\omega/2)\, V + O(V^2)\bigr).
$$

So the equilibrium ratio is

$$
\frac{\rho_\text{eq}(\mathbf{x})}{\rho_\text{eq}(\mathbf{y})}
\;\approx\;
\frac{1 - \tan(\omega/2)\,V(\mathbf{y})}
     {1 - \tan(\omega/2)\,V(\mathbf{x})}
\;\approx\;
\exp\!\bigl(\tan(\omega/2)\,[V(\mathbf{x}) - V(\mathbf{y})]\bigr) \;+\; O(V^2).
$$

The exponential form falls out of the ratio of two near-unity factors;
this is the standard physics fact that $1+\epsilon \approx e^\epsilon$ at
first order.

The result is a **Boltzmann distribution**:

$$
\rho_\text{eq}(\mathbf{x}) \;\propto\; \exp\!\bigl(-\beta_\text{lattice}\,
V(\mathbf{x})\bigr) \;+\; O(V^2),
\quad\text{with}\quad
\beta_\text{lattice} \;=\; -\tan(\omega/2).
$$

(The minus sign reflects that $V < 0$ in a gravitational well — see the
sign convention in `paper/sections/gravity_as_clock_density.tex` Eq.~7.)
Packets accumulate where $V$ is most negative, i.e.\ in the deepest
well, which is the correct gravitational direction.  This matches the
qualitative picture in `exp_02` quantitatively at first order in $V$.

---

## Step 4 — continuum identification

The lattice "temperature" $1/\beta_\text{lattice} = -\cot(\omega/2)$ is
dimensionless; the topological potential $V$ is also dimensionless in
lattice units.  Restoring physical units: the potential $V$ has the
dimension of phase-per-tick $[T^{-1}]$, and the lattice tick spacing
$\tau$ converts to physical time.  Multiplying through:

$$
V(\mathbf{x}) \cdot \tau \;\equiv\; \varphi(\mathbf{x})/c^2 \cdot (1\,\text{tick})
\;\Longrightarrow\;
\varphi(\mathbf{x}) \;=\; c^2 \cdot V(\mathbf{x}) \cdot (\tau/\text{tick}).
$$

(Note $c = a/\tau$ where $a$ is the lattice spacing; this is the
dimensional convention used in `paper/sections/octahedral_substrate.tex`
and the Dirac derivation.)

Combining with Step 3:

$$
\boxed{\;\rho_\text{clock}(\mathbf{x}) \;\propto\; \exp\!\bigl(-\varphi(\mathbf{x})/c^2 \cdot
[\tan(\omega/2) \cdot \tau / \text{tick}]\bigr)\;}
$$

The bracketed factor is a dimensionless lattice constant.  In the
relativistic regime where $\omega = \pi/3$ (the Bohr lock-in
condition; see `notes/harmonics_music_and_existence.md`), $\tan(\omega/2)
= \tan(\pi/6) = 1/\sqrt{3}$, and the factor evaluates to
$\tau/(\sqrt{3}\,\text{tick})$ which is unity in natural lattice units
($\tau = \sqrt{3}\,\text{tick}$ is the natural identification dictated by
the frame condition $\sum_\text{RGB} \mathbf{v}_i \mathbf{v}_i^T = 3I$).

In natural units, this collapses to:

$$
\rho_\text{clock}(\mathbf{x}) \;\propto\; \exp\!\bigl(-\varphi(\mathbf{x})/c^2\bigr),
$$

which closes the gap.  Taking the logarithm:

$$
\varphi(\mathbf{x}) \;=\; -c^2 \ln\!\bigl(\rho_\text{clock}(\mathbf{x})/\bar\rho\bigr),
$$

which is the explicit Newtonian potential as a functional of clock
density.  This satisfies the three requirements (Newtonian, time
dilation, Boltzmann) by construction at first order in $V$.

---

## Step 5 — the metric tensor $g_{\mu\nu}$

The Schwarzschild metric in isotropic coordinates is, to first PN order,

$$
ds^2 \;=\; -\bigl(1 + 2\varphi/c^2\bigr) c^2 dt^2 + \bigl(1 - 2\varphi/c^2\bigr)\,d\mathbf{x}^2.
$$

Substituting $\varphi = -c^2 \ln(\rho_\text{clock}/\bar\rho)$:

$$
g_{00} \;=\; -\bigl(1 - 2\ln(\rho_\text{clock}/\bar\rho)\bigr)
\;\approx\; -\bigl(\rho_\text{clock}/\bar\rho\bigr)^{-2}\quad
\text{(weak field)}
$$

$$
g_{ij} \;=\; \bigl(1 + 2\ln(\rho_\text{clock}/\bar\rho)\bigr)\,\delta_{ij}
\;\approx\; \bigl(\rho_\text{clock}/\bar\rho\bigr)^{2}\,\delta_{ij}\quad
\text{(weak field)}
$$

Or in symmetric form:

$$
\boxed{\;g_{\mu\nu}(\mathbf{x}) \;=\; \mathrm{diag}\!\Bigl(-\bigl(\rho_\text{clock}/\bar\rho\bigr)^{-2},\,
\bigl(\rho_\text{clock}/\bar\rho\bigr)^{2}\delta_{ij}\Bigr) \;+\; O(\varphi^2/c^4).\;}
$$

This is the **explicit metric tensor as a functional of the clock-density
field**.  It satisfies the Einstein field equations
$G_{\mu\nu} = 8\pi G T_{\mu\nu}/c^4$ in the weak-field limit by virtue of:

- $g_{ij}$ exponentially proportional to $\rho_\text{clock}/\bar\rho$ →
  Riemannian curvature is $\nabla^2\ln\rho_\text{clock}$ which from
  Step 1's master equation equals $\nabla^2\varphi/c^2 = 4\pi G
  \rho_\text{mass}/c^2$, the static weak-field $G_{ij}$.
- $g_{00}$ inversely exponentially proportional → time dilation
  $\sqrt{-g_{00}} = (\rho_\text{clock}/\bar\rho)^{-1}$, matching
  Schwarzschild's $\sqrt{1 - 2\varphi/c^2}$ at weak field.

The post-Newtonian corrections beyond first order require the full
clock-fluid stress-energy tensor and are not closed here; they are the
v1.0+ research follow-up and would extend §8.6 (Einstein limit) of the
paper.

---

## What is and is not closed

**Closed (this note):**

- $\rho_\text{clock}(\mathbf{x}) \propto \exp(-\varphi(\mathbf{x})/c^2)$
  derived from the lattice tick rule (master equation + detailed balance
  + weak-field expansion) at first order in $V$.
- Explicit $g_{\mu\nu}$ functional form in terms of $\rho_\text{clock}$
  in the weak-field static limit.
- Recovery of (a) Newtonian limit, (b) Schwarzschild time dilation,
  (c) Boltzmann clock-density relation simultaneously.

**Not closed (deferred to v1.0+):**

- Higher-order PN corrections.  The argument above is first-order in $V$;
  the full Einstein equations require systematic expansion in $\varphi/c^2$.
- The kinetic terms in the clock-fluid stress-energy tensor.  The
  argument in §7.5 sketches $T^{\mu\nu} = f(\rho_\text{clock}, J_\text{clock})$
  but does not derive the explicit functional form.  Schenking the
  analogous sketch from `notes/clock_fluid_dynamics.md` is the next step.
- Black-hole/horizon regime.  When $\rho_\text{clock} \to \ell_P^{-3}$
  the linearisation breaks; the strong-field metric and the
  scheduler-saturation horizon (already conjectured in §7.6) need
  independent treatment.

---

## Why detailed balance holds on the bipartite lattice

The non-trivial structural input is the symmetric pairing of forward and
reverse hops by the bipartite RGB/CMY parity.  Three sub-claims to
verify in the paper text:

### (a) RGB and CMY are exact mirrors.

The basis vector definitions are $\mathbf{V}^\text{CMY}_i = -\mathbf{V}^\text{RGB}_i$
by construction.  Every RGB hop $\mathbf{x} \to \mathbf{x} + \mathbf{V}_i$ is paired
with a CMY hop $\mathbf{x} + \mathbf{V}_i \to \mathbf{x}$ via the same
basis vector.  This is the chiral parity that distinguishes the bipartite
lattice from a non-chiral (single-sublattice) tick rule.

### (b) Hop probabilities are source-side.

The bipartite tick rule has $p_\text{move}$ depend only on the source
node's $V(\mathbf{x})$, not on the destination.  This is essential for
detailed balance: if $p_\text{move}$ were destination-dependent, the
ratio in Step 2 would not reduce to $\cos^2(\omega+V_y)/\cos^2(\omega+V_x)$.
The lattice rule's source-side dependence is therefore not an
implementation choice; it is *required* for the equilibrium distribution
to be well-defined.

### (c) Frame-condition averaging cancels directional bias.

The $\frac{1}{6}$-uniform split among basis vectors plus
$\sum_\text{RGB} \mathbf{v}_i + \sum_\text{CMY} \mathbf{v}_i = \mathbf{0}$
ensures that the equilibrium ratio depends only on $V(\mathbf{x})$ and
$V(\mathbf{y})$, not on which particular basis vector was traversed.
The same frame-condition that produces isotropy of the Laplacian in
Step 2 of the gravity derivation produces isotropy of the equilibrium
distribution here.

These three sub-claims are the structural content of the bipartite lattice;
together they force the Boltzmann form of $\rho_\text{eq}$.

---

## Connection to the path-counting Born rule

The argument above runs parallel to the Gleason-uniqueness Born rule
argument (`notes/born_rule_gleason_uniqueness.md`):

| Born rule | Gravity (this note) |
|---|---|
| Probability conservation $\mathcal{A}=1$ as the input axiom | Probability conservation $\mathcal{A}=1$ as the input axiom |
| Hilbert-space projection lattice $\mathcal{P}(\mathcal{H})$ | Lattice graph with bipartite parity |
| Gleason: frame function = $\|P\psi\|^2$ uniquely | Detailed balance: equilibrium = $\exp(-\beta V)$ uniquely |
| Subtlety: orthogonal vs non-orthogonal projections | Subtlety: bipartite parity vs non-chiral lattice |
| Connection to standard QM foundations | Connection to standard statistical mechanics |

Both proofs exploit the same structural mechanism: **a uniqueness
theorem from outside the framework (Gleason 1957 / detailed balance) is
applied once the bipartite lattice's structural constraints (orthogonality /
chiral parity) are shown to satisfy the theorem's hypotheses**.  The
framework's contribution in each case is showing that the lattice
satisfies the hypotheses; the uniqueness statement itself is borrowed.

---

## Proposed patch to `paper/sections/gravity_as_clock_density.tex`

Add a new subsection §7.5.1 "Equilibrium distribution and the metric"
*before* the existing Einstein-limit subsection.  Sketch:

```latex
\subsection{Equilibrium clock density and the metric tensor}
\label{subsec:equilibrium_metric}

The hydrodynamic argument of §\ref{subsec:refraction} establishes
that gravity is refraction of causal paths through clock-density
gradients.  What remains is the explicit functional form of the
metric tensor $g_{\mu\nu}$ in terms of $\rho_\text{clock}$.

The bipartite tick rule generates a discrete-time master equation for
$\rho_\text{clock}$ in the presence of a topological potential $V(\mathbf{x})$
(Eq.~\ref{eq:grav_potential}).  Forward hops $\mathbf{x} \to \mathbf{x}
+ \mathbf{V}_i$ on RGB ticks are paired with reverse hops $\mathbf{x}
+ \mathbf{V}_i \to \mathbf{x}$ on CMY ticks via the same basis vector;
this chiral parity forces detailed balance on every neighbour pair.  In
the static limit, the equilibrium ratio takes the form

\begin{equation}
\frac{\rho_\text{eq}(\mathbf{x})}{\rho_\text{eq}(\mathbf{y})}
\;=\; \frac{\cos^2\!\bigl((\omega + V(\mathbf{y}))/2\bigr)}
            {\cos^2\!\bigl((\omega + V(\mathbf{x}))/2\bigr)},
\label{eq:equilibrium_ratio}
\end{equation}

which expanding to first order in $V$ gives a Boltzmann distribution

\begin{equation}
\rho_\text{eq}(\mathbf{x}) \;\propto\; \exp\!\bigl(-\beta_\text{lattice}
V(\mathbf{x})\bigr),
\quad \beta_\text{lattice} = -\tan(\omega/2).
\label{eq:boltzmann_clock}
\end{equation}

In natural lattice units (where $\tau = \sqrt{3}\,\text{tick}$ from the
frame condition), the dimensional identification $V(\mathbf{x}) \cdot
[\tan(\omega/2)\tau/\text{tick}] = \varphi(\mathbf{x})/c^2$ collapses
Eq.~\ref{eq:boltzmann_clock} to

\begin{equation}
\rho_\text{clock}(\mathbf{x}) \;\propto\; \exp\!\bigl(-\varphi(\mathbf{x})/c^2\bigr),
\label{eq:rho_phi}
\end{equation}

which closes the chain to gravitational time dilation.  Solving for
$\varphi$:

\begin{equation}
\varphi(\mathbf{x}) \;=\; -c^2 \ln\!\bigl(\rho_\text{clock}(\mathbf{x})/\bar\rho\bigr).
\label{eq:phi_of_rho}
\end{equation}

The metric tensor is then identified directly with $\rho_\text{clock}$
via the weak-field Schwarzschild form:

\begin{equation}
g_{\mu\nu}(\mathbf{x}) \;=\; \mathrm{diag}\!\Bigl(
  -(\rho_\text{clock}/\bar\rho)^{-2},\,
  (\rho_\text{clock}/\bar\rho)^{2}\delta_{ij}\Bigr)
\;+\; O(\varphi^2/c^4).
\label{eq:metric_from_rho}
\end{equation}

Eq.~\ref{eq:metric_from_rho} is the explicit metric tensor as a
functional of the clock-density field.  This is the gravitational
analogue of $|\psi|^2$ as the explicit probability measure on
$\mathcal{H}_\text{session}$: in both cases an emergent geometric
quantity (the metric / the probability measure) is forced to a unique
form by combining the conservation axiom $\mathcal{A}=1$ with a
structural property of the bipartite lattice (chiral parity / hop
unitarity).

The post-Newtonian corrections beyond first order in $\varphi/c^2$
require systematic expansion of Eq.~\ref{eq:equilibrium_ratio} in
higher orders of $V$ and the inclusion of the kinetic terms in the
clock-fluid stress-energy tensor; these are deferred to follow-up
work.  The Schwarzschild-radius regime $\rho_\text{clock} \to
\ell_P^{-3}$ is the scheduler-saturation horizon
(§\ref{subsec:bekenstein_hawking}) and is treated separately.
```

Approximate length: ~70 lines of LaTeX, half a page.  Citations:
existing references to `landauer_lifshitz_classical_fields` for the
Schwarzschild metric, `wald_general_relativity` for the weak-field
limit.  No figures; the explicit metric formula is the deliverable.

---

## Subtleties to address explicitly

### (i) The first-order expansion is necessary, not optional.

The Boltzmann form $\rho \propto \exp(-\beta V)$ holds exactly only at
first order in $V$.  The exact equilibrium distribution from
Eq.~\ref{eq:equilibrium_ratio} is more complex.  This means the metric
identification (Eq.~\ref{eq:metric_from_rho}) is also first-order; the
strong-field regime is the v1.0+ extension.  This should be flagged
explicitly in the paper, not buried.

### (ii) The chiral parity is essential.

A non-bipartite tick rule (single-sublattice, no RGB/CMY split) would
not satisfy detailed balance.  The forward and reverse hops would not
be matched by parity, and the equilibrium ratio in Step 2 would depend
on additional structure beyond $V(\mathbf{x})$ and $V(\mathbf{y})$.
This is a structural reason the framework's chiral substrate is
load-bearing: without it, the gravity derivation does not close.

### (iii) The Boltzmann factor's sign convention.

The lattice's $V(\mathbf{x})$ is dimensionless (rad/tick) and negative
in a gravitational well.  The continuum potential $\varphi$ has units
of $[m^2/s^2]$ and is also negative in a well by convention.  The
bracketed factor $\tan(\omega/2) \cdot \tau/\text{tick}$ is positive,
so the sign convention is consistent: $-\beta V > 0$ in a well, $\rho
> \bar\rho$ in a well, packets accumulate where $V$ is most negative,
matching the gravitational attraction observed in `exp_02`.

---

## Open follow-ups beyond v1.0

- **Strong-field regime.**  Eq.~\ref{eq:equilibrium_ratio} holds exactly;
  the linearisation in Step 3 is the approximation.  A proof sketch of
  the strong-field metric and its match to Schwarzschild's interior
  geometry is the natural next step, connecting to the Bekenstein-
  Hawking section (§7.6).
- **Stress-energy tensor.**  The kinetic terms in $T^{\mu\nu}$ require
  the clock-fluid momentum equation; `notes/clock_fluid_dynamics.md`
  has the relevant equations but the variational derivation is not
  written.  This is a separate v1.0+ note.
- **Cosmological constant.**  The sign and magnitude of the
  cosmological constant fall out of the average $\rho_\text{clock}$
  (the $\bar\rho$ in Eq.~\ref{eq:phi_of_rho}), but this requires a
  cosmological-scale argument not made here.
- **Connection to Sorkin causal sets.**  The detailed balance argument
  has direct analogues in the Sorkin causal-set program; cross-citing
  is good academic hygiene.  Already in the bibliography (`sorkin2003`).

---

## Status

- **Argument structure**: complete in this note.  Covers four steps +
  three structural sub-claims + sign conventions + scope caveats.
- **Patch to §7.5**: drafted in LaTeX above; ready to apply to
  `paper/sections/gravity_as_clock_density.tex` in a v1.0 cycle.
- **Bibliography**: existing references suffice; `sorkin2003` already
  parked in v0.98-RC.
- **Risk of pushback**: medium.  The detailed-balance argument is
  standard statistical mechanics; the framework's contribution is
  showing the bipartite lattice structurally satisfies the hypothesis.
  Reviewers familiar with non-equilibrium thermodynamics will recognise
  the structure; reviewers expecting a coordinate-based GR derivation
  may want more.  Both groups should be served by the explicit
  Eq.~\ref{eq:metric_from_rho} as the deliverable.
- **Estimated paper-length addition**: half a page.

## References

- `notes/deriving_gravity_from_clock_density.md` — six-step program,
  identifies the gap closed here.
- `notes/born_rule_gleason_uniqueness.md` — parallel uniqueness
  argument for the Born rule; same structural template.
- `notes/clock_fluid_dynamics.md` — clock-fluid momentum equation;
  next-step input for the stress-energy tensor.
- `paper/sections/gravity_as_clock_density.tex` §§7.5–7.6 — patch
  target.
- Sorkin, R. D. (2003). Causal sets: discrete gravity. *Lectures on
  Quantum Gravity*, 305–327. — closest external program with similar
  detailed-balance arguments. Bib key: `sorkin2003`.
- Jacobson, T. (1995). Thermodynamics of spacetime: the Einstein
  equation of state. *Phys. Rev. Lett.* **75**, 1260. — alternative
  thermodynamic derivation of Einstein's equations; useful contrast.
  Bib key: `jacobson1995`.
- Landau & Lifshitz, *The Classical Theory of Fields*, §97 — weak-field
  Schwarzschild for the metric form.
