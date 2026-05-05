# Clock-Density Photon Decoherence: Working Hypothesis

*Notes from off-keyboard thinking, 2026-05-04. Standalone note;
indexed as follow-on #15 in `follow_on_implications.md`. Not paper
text — this is hypothesis scaffolding for a future calculation.*

---

## The Hypothesis

Local clock-density gradients $\nabla\rho_\phi(x)$ modify the phase
evolution and decoherence rate of EM wave packets, leading to:

- **(a) Timing jitter:** small but systematic stochastic fluctuations
  in pulse arrival times *beyond* the deterministic Shapiro / geodesic
  delay.
- **(b) Environment-dependent decoherence:** a coherence-loss profile
  with explicit dependence on the *spatial structure* of $\rho_\phi$
  along the photon's path, distinct from QFT-in-curved-spacetime
  expectations and from environmental phase scrambling
  (`exp_04`-style).

Both are downstream of the same primary effect: photon phase advance
per tick is sensitive to the local clock-fluid environment, and that
environment has spatial structure (deterministic gradients) and
finite-N fluctuations (stochastic).

---

## Math Sketch (Schematic)

### Phase evolution

For a photon session $\psi_\gamma$ with bare instruction frequency
$\omega_\gamma$, let the *effective* phase advance per tick be:

$$
\dot\phi(x, t) = \omega_\gamma + \delta\omega(\rho_\phi(x, t))
$$

where $\delta\omega$ is a perturbation set by the local clock-fluid
density.  The simplest ansatz (proportional coupling) is:

$$
\delta\omega = \alpha \cdot \rho_\phi(x, t)
$$

with $\alpha$ a coupling constant to be determined.  For
deterministic $\rho_\phi$ this gives gravitational redshift /
Shapiro-like effects (already captured analytically in the
clock-density-gravity programme, exp_02 PASS).

### Stochastic component

Decompose $\rho_\phi = \langle\rho_\phi\rangle + \delta\rho_\phi$
where $\delta\rho_\phi$ is the finite-$N$ session-density
fluctuation.  Assume $\langle\delta\rho_\phi\rangle = 0$ and the
two-point correlator:

$$
G(x_1, t_1; x_2, t_2)
\;=\;
\langle \delta\rho_\phi(x_1, t_1)\,\delta\rho_\phi(x_2, t_2) \rangle
$$

Then the photon phase accumulates a stochastic contribution along
its world-line $\Gamma$:

$$
\delta\phi_\Gamma
\;=\;
\alpha \int_\Gamma \delta\rho_\phi(x(s), t(s))\, ds.
$$

Mean is zero; variance is:

$$
\langle (\delta\phi_\Gamma)^2 \rangle
\;=\;
\alpha^2 \int_\Gamma \int_\Gamma G(x_1, t_1; x_2, t_2)\, ds_1\, ds_2.
$$

### Timing jitter from phase variance

For a wave packet centred at $\omega_\gamma$, phase variance maps to
arrival-time variance through

$$
\sigma_t \;\sim\; \frac{\sqrt{\langle (\delta\phi_\Gamma)^2 \rangle}}{\omega_\gamma}.
$$

If $G$ is short-ranged with correlation length $\ell_c$ (probably
related to the lattice spacing $a$), the integral simplifies in the
diffusive regime:

$$
\langle (\delta\phi_\Gamma)^2 \rangle \;\sim\; \alpha^2 \cdot \langle\delta\rho_\phi^2\rangle \cdot \ell_c \cdot L
$$

so timing jitter scales as $\sqrt{L}$ (random-walk scaling) rather
than $\propto L$ (which would indicate a deterministic detuning).

### Decoherence kernel

For two coherent path branches $\Gamma_1$ and $\Gamma_2$ in a
superposition, the relative phase variance:

$$
\langle (\delta\phi_1 - \delta\phi_2)^2 \rangle
\;=\;
\langle\delta\phi_1^2\rangle + \langle\delta\phi_2^2\rangle
- 2\langle\delta\phi_1\,\delta\phi_2\rangle
$$

The cross term depends on how spatially separated the paths are
relative to $\ell_c$.  If the paths separate by more than $\ell_c$,
the cross correlation drops to zero and decoherence is set by the
sum of individual variances.  If paths stay within $\ell_c$, the
two branches sample the *same* fluctuations and the cross term
cancels: phase coherence is preserved.

This gives a **distinctive spatial coherence length** $\ell_c$ for
clock-fluid-mediated decoherence — the signature that would
distinguish it from white-noise environmental scrambling (which has
no length scale).

---

## Magnitude — Gated by P7

Per `paper/sections/predictions.tex` §12.8, GRB time-of-flight
constrains $a \le 10^{-19}\,\mathrm{m}$ (Vasileiou 2013).  The
surviving calibration window is $a \in [\ell_P, 10^{-19}]\,\mathrm{m}$.

Ballpark for the timing-jitter signal on an astrophysical baseline
($L \sim 1\,\mathrm{kpc} \sim 3 \times 10^{19}\,\mathrm{m}$),
assuming $\ell_c \sim a$ and $\delta\rho_\phi / \rho_\phi \sim 1$
per cell:

$$
\sigma_t \sim \sqrt{a \cdot L} / c
$$

| Calibration | $a$ (m) | $\sigma_t$ over 1 kpc |
|---|---|---|
| P7 upper bound | $10^{-19}$ | $\sim 6 \,\mathrm{ns}$ — *within pulsar timing precision* |
| Mid-range | $10^{-25}$ | $\sim 6 \,\mathrm{fs}$ |
| Planck | $10^{-35}$ | $\sim 20 \,\mathrm{as}$ — *unmeasurable* |

So the prediction is observable iff $a$ sits near the P7 upper
bound.  Pulsar timing residuals could in principle constrain or
detect this.  A narrower observational window than I expected at
first — the framework's calibration ambiguity becomes a quantitative
predictor here.

**Caveat**: this assumes random-walk scaling and $\ell_c \sim a$.
If $\ell_c \gg a$ (long-range clock-fluid correlations from
collective session dynamics), the scaling changes.  If
$\delta\rho_\phi/\rho_\phi \ll 1$, the prefactor shrinks
proportionally.  Both worth deriving from first principles, not
ansatz.

---

## Distinguishing from Diósi-Penrose-Bassi

Established gravitational decoherence proposals
(Diósi 1987, Penrose 1996, Bassi-Lochan-Satin-Singh-Ulbricht 2017)
predict decoherence rates scaling with mass-distribution
superposition energy $\Delta E_\text{grav}$.  The mass distribution
is the canonical input.

The clock-density hypothesis here predicts:

1. Decoherence rate scales with $\int_\Gamma |\nabla\rho_\phi|^2\, ds$
   along the photon's path, *not* with the absolute mass enclosed.
   A photon traversing a region of high but uniform $\rho_\phi$
   should see *less* decoherence than one passing through a strong
   gradient at lower absolute mass — the opposite of
   Diósi-Penrose.

2. Spatial coherence length $\ell_c$ is a real observable in the
   decoherence kernel.  Diósi-Penrose has no such length scale.

3. Anisotropy: the bipartite optical axis $(1,1,-1)$ may give a
   *direction-dependent* decoherence rate — slower along the axis,
   faster perpendicular (or vice versa, depending on the sign of
   the $\mathbf{Q}$-tensor projection).  Diósi-Penrose is
   isotropic.

These three are the distinguishing falsifiers.  Without them, the
hypothesis collapses into "Diósi-Penrose with relabeled variables"
and has no novel content.

---

## Tests

### Astrophysical (potentially within reach)

- **Pulsar timing residuals.**  Once GR (Shapiro + dispersion +
  intrinsic noise) is subtracted, residual stochastic jitter on
  ms-pulsar arrival times.  NANOGrav, EPTA datasets at ns
  precision.  Look for the $\sqrt{L}$ baseline-length scaling and
  any anisotropy along the optical axis.

- **FRB pulse-width broadening.**  Beyond ISM scattering, look for
  a clock-density-gradient component correlated with the
  intervening mass distribution but orthogonal to standard
  scattering predictions.

- **CMB photon decoherence.**  CMB photons traverse $\sim 10^{26}\,\mathrm{m}$;
  random-walk jitter would be $\sim \sqrt{a \cdot 10^{26}}\,\mathrm{m}/c$.
  At $a = 10^{-19}\,\mathrm{m}$: $\sigma_t \sim 100\,\mathrm{ns}$
  per photon — buried under thermal broadening but possibly
  visible in spectral-line cross-correlations.

### Lattice (in our hands)

- **`exp_4b` proposal**: extend `exp_04` to test *correlated*
  environment scrambling (clock-fluid-like spatial structure)
  versus the existing white-noise scrambling.  Specifically:
  - White-noise control: exp_04 baseline with iid random phase
    perturbations at each lattice node
  - Structured environment: phase perturbations sampled from a
    field with prescribed spatial correlation length $\ell_c$
    (Gaussian random field, Matérn covariance, etc.)
  - Compare wave-packet coherence-loss curves
  - Predicted distinction: structured environment shows a
    *plateau* in coherence below paths separated by $< \ell_c$,
    then a knee at the correlation length; white-noise shows
    monotonic exponential decay
  - If the predicted distinction is visible numerically, the
    real-world signature is concrete

---

## Open Questions Before This Becomes a Paper

1. **What sets $\alpha$?** Coupling between photon phase advance
   and local $\rho_\phi$ should be derivable from the bipartite
   tick rule — not a free parameter.  Maybe $\alpha \sim 1$ in
   lattice units (one tick of phase per unit clock-fluid density),
   maybe smaller.  Needs derivation from `_kinetic_hop`'s
   $\delta\phi$-dependent residence term.

2. **What is $\ell_c$?**  Is it the lattice spacing $a$, or longer?
   If sessions are correlated through `TickScheduler` pairwise
   interactions, $\ell_c$ could be much larger than $a$.  Needs
   numerical investigation (or a derivation from the clock-fluid
   continuity equation's Green's function).

3. **Is the prediction actually distinct from Diósi-Penrose at
   leading order?**  Need to show the three distinguishing items
   above survive the calculation rather than being washed out by
   the leading-order coupling looking the same.

4. **Anisotropy claim:**  If the optical axis $(1,1,-1)$ does
   imprint on decoherence rates, this is a NEW falsifier in the P9
   multi-channel concordance basket — sixth observation channel.
   But it requires the calculation actually predicting anisotropy,
   not just allowing it.

---

## Cross-References

- `paper/sections/clock_fluid_dynamics.tex` — defines $\rho_\phi$
- `paper/sections/gravity_as_clock_density.tex` — exp_02 PASS for
  deterministic clock-density gradient effects
- `paper/sections/predictions.tex` §12.8 (P7) — GRB bound on $a$
- `paper/sections/predictions.tex` §12.10 (P9) — multi-channel
  concordance basket (potential 6th channel)
- `src/experiments/exp_04_decoherence.md` — existing white-noise
  decoherence baseline, predecessor to proposed `exp_4b`
- `notes/follow_on_implications.md` #15 — index entry
- `notes/conservation_of_probability.md` — A=1 framework anchor
- `notes/exp_20_emission_operator_and_clock_fluid.md` — joint
  amplitude / clock-fluid identification

---

## Status

- **Idea**: 2026-05-04, off-keyboard
- **Math**: schematic ansatz only; derivation pending
- **Magnitude**: ballpark only; assumes $\ell_c \sim a$ and
  $\delta\rho/\rho \sim 1$ per cell
- **Numerical test**: `exp_4b` proposed but not designed in detail
- **Distinguishing falsifiers**: stated; not yet confirmed by
  calculation
- **Indexed as follow-on**: #15 in `follow_on_implications.md`
