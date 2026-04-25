# EM derivation from the lattice — attempt

*Written 2026-04-25 as a working pass. The goal is to see how far we
can push a lattice derivation of Maxwell's equations parallel to the
gravity derivation in Section 7. The result: the matter-side coupling
is genuinely derived; the field-side dynamics requires postulating a
gauge action that is consistent with — but not strictly forced by — the
existing tick rule. Honest assessment at the end.*

---

## 0. What we are trying to do, and what would count as success

Section 7 of the paper derives Newton's law of gravity from the lattice
tick rule end-to-end:

1. The hop probability $p_\text{hop} = \cos^2(\delta\phi/2)$ with
   $\delta\phi = \omega + V$.
2. Weak-field expansion gives $p_\text{hop} \approx p_0 - m\,V$.
3. Equilibrium gives $\rho_\text{clock} \propto \exp(m\,V)$.
4. Linearising and applying the lattice Laplacian gives Poisson's
   equation $\nabla^2\phi_\text{Newton} = 4\pi G \rho$.

Every step uses only the existing tick rule. No new field is
introduced.

We want a parallel for EM. A plausible parallel would be:

1. The hop probability with Peierls substitution
   $\delta p \to \delta p + \mathbf{A}\cdot\mathbf{v}$.
2. Some weak-field expansion.
3. Some equilibrium-like condition.
4. A reduction to Maxwell's equations.

The reasonable hope is that this parallel works. The actual finding,
worked through below, is that it works on the matter side but not on
the gauge side. The gauge field's own dynamics is not forced by the
existing tick rule — it has to be postulated, and the postulate is
the standard Wilson action. With that postulate, Maxwell falls out.
Without it, only half the story does.

---

## 1. Setting: U(1) link variables

The lattice tick rule already includes Peierls substitution: when a
session hops from $\mathbf{x}$ to $\mathbf{x}+a\hat{\mu}$, its phase
acquires a factor $\exp(i a A_\mu(\mathbf{x}))$ in addition to the
Zitterbewegung phase $\delta\phi$. This is in
`CausalSession._kinetic_hop` (see CLAUDE.md, line on Peierls
substitution).

The natural object is the link variable

$$
U_\mu(\mathbf{x}) = e^{i\,a\,A_\mu(\mathbf{x})} \in U(1).
$$

$U_\mu(\mathbf{x})$ lives on the link from $\mathbf{x}$ to
$\mathbf{x}+a\hat{\mu}$, and acts on a session hopping along that link
by phase rotation. Two structural facts:

- **U(1) is forced by the matter content.** Each session has a U(1)
  phase. The relative phase between sessions at adjacent nodes is
  naturally a U(1) element. Any other gauge group would be
  inconsistent with the matter side.
- **Link variables are forced by the hop structure.** The hop is the
  basic operation on the lattice; the link variable is the most general
  U(1)-valued object that can act on a hop without violating locality.

These two facts mean the existence of a U(1) link variable is not
postulated — it is the most general gauge structure consistent with
the framework.

What *is* postulated, eventually, is that $A_\mu$ has its own
dynamics. We come back to this.

---

## 2. Gauge covariance of the tick rule (clean derivation)

Under a local U(1) gauge transformation $\Lambda(\mathbf{x})$:

$$
\psi(\mathbf{x}) \to e^{i\Lambda(\mathbf{x})} \psi(\mathbf{x}),
\qquad
A_\mu(\mathbf{x}) \to A_\mu(\mathbf{x}) + \partial_\mu \Lambda(\mathbf{x}).
$$

The link variable transforms as

$$
U_\mu(\mathbf{x}) \to e^{i\Lambda(\mathbf{x}+a\hat{\mu})} U_\mu(\mathbf{x}) e^{-i\Lambda(\mathbf{x})},
$$

which one can check directly from the definition $U_\mu = e^{iaA_\mu}$
in the small-$a$ limit using $a\,\partial_\mu \Lambda \approx
\Lambda(\mathbf{x}+a\hat{\mu}) - \Lambda(\mathbf{x})$.

Now consider the matter tick rule. A simplified form suffices:

$$
\psi(\mathbf{x}+a\hat{\mu}) = U_\mu(\mathbf{x})\,\cdot\,(\text{tick}\,\psi)(\mathbf{x}).
$$

Under the gauge transformation:

$$
\begin{aligned}
\psi'(\mathbf{x}+a\hat{\mu})
&= U'_\mu(\mathbf{x}) \cdot (\text{tick}\,\psi')(\mathbf{x}) \\
&= e^{i\Lambda(\mathbf{x}+a\hat{\mu})} U_\mu(\mathbf{x}) e^{-i\Lambda(\mathbf{x})} \cdot e^{i\Lambda(\mathbf{x})} (\text{tick}\,\psi)(\mathbf{x}) \\
&= e^{i\Lambda(\mathbf{x}+a\hat{\mu})} \cdot U_\mu(\mathbf{x})(\text{tick}\,\psi)(\mathbf{x}) \\
&= e^{i\Lambda(\mathbf{x}+a\hat{\mu})} \cdot \psi(\mathbf{x}+a\hat{\mu}).
\end{aligned}
$$

So the new $\psi$ at $\mathbf{x}+a\hat{\mu}$ rotates by the local
$\Lambda$ at that node. The tick rule is gauge covariant by
construction; gauge invariance of physical observables ($|\psi|^2$,
phase differences, and so on) follows automatically.

**Status: derived.** Gauge covariance of the matter sector falls out
of the existing Peierls-substituted tick rule, with no extra
assumptions.

---

## 3. The plaquette is $F_{\mu\nu}$ (clean derivation)

Consider the smallest non-trivial closed loop on the lattice: a
plaquette in the $(\mu, \nu)$ plane, going around
$\mathbf{x} \to \mathbf{x}+a\hat{\mu} \to \mathbf{x}+a\hat{\mu}+a\hat{\nu} \to \mathbf{x}+a\hat{\nu} \to \mathbf{x}$.
The U(1) holonomy around this loop is the Wilson loop

$$
W_{\mu\nu}(\mathbf{x}) =
U_\mu(\mathbf{x})\,U_\nu(\mathbf{x}+a\hat{\mu})\,U_\mu^*(\mathbf{x}+a\hat{\nu})\,U_\nu^*(\mathbf{x}).
$$

Expanding for small $a$ and using
$A_\mu(\mathbf{x}+a\hat{\nu}) \approx A_\mu(\mathbf{x}) + a\,\partial_\nu A_\mu(\mathbf{x})$:

$$
\log W_{\mu\nu} \approx i\,a^2 \bigl(\partial_\mu A_\nu - \partial_\nu A_\mu\bigr) = i\,a^2\,F_{\mu\nu}(\mathbf{x}).
$$

So the plaquette holonomy IS the field strength tensor times the
plaquette area, in the continuum limit:

$$
\boxed{\;W_{\mu\nu}(\mathbf{x}) \;\xrightarrow{a \to 0}\; e^{i a^2 F_{\mu\nu}(\mathbf{x})}\;}
$$

$W_{\mu\nu}$ is gauge invariant: the corner gauge transformations
cancel pairwise around the loop. Therefore $F_{\mu\nu}$ is gauge
invariant in the continuum limit — without postulating it.

**Status: derived.** $F_{\mu\nu}$ emerges as the smallest non-trivial
gauge-invariant lattice operator built from link variables.

---

## 4. Coupling to bipartite matter and the Dirac current (mostly derived)

The bipartite tick rule with Peierls substitution couples matter to
the gauge field. To extract the matter current, expand the lattice
Dirac action around a smooth matter configuration.

The lattice Dirac operator with Peierls links is

$$
D_\text{lat}\psi(\mathbf{x}) = \frac{1}{2a} \sum_\mu \gamma^\mu \bigl[U_\mu(\mathbf{x})\psi(\mathbf{x}+a\hat{\mu}) - U_\mu^*(\mathbf{x}-a\hat{\mu})\psi(\mathbf{x}-a\hat{\mu})\bigr],
$$

where the $\gamma^\mu$ matrices are the ones derived in Section 6.4
from the bipartite RGB/CMY structure. (This is the compact
representation; the actual tick rule decomposes the same operator into
the alternating RGB/CMY hops — they are equivalent in the continuum
limit. See Kogut and Susskind 1975.)

Varying the matter action $S_\text{matter} = \sum_\mathbf{x} a^4\,\bar\psi(\mathbf{x}) D_\text{lat}\psi(\mathbf{x})$
with respect to $A_\mu$, using $\delta U_\mu = i\,a\,U_\mu\,\delta A_\mu$:

$$
\frac{\delta S_\text{matter}}{\delta A_\mu(\mathbf{x})} = a^4 \cdot \bar\psi(\mathbf{x}) \gamma^\mu \psi(\mathbf{x}) + O(a),
$$

which in the continuum limit is the Dirac current

$$
\boxed{\;J^\mu(\mathbf{x}) = \bar\psi(\mathbf{x}) \gamma^\mu \psi(\mathbf{x}).\;}
$$

**Status: derived modulo the equivalence between the alternating
bipartite tick rule and the compact lattice Dirac operator.** The
equivalence is standard staggered-fermion territory (Kogut–Susskind);
the paper's existing Dirac derivation in Section 6.4 already takes the
two as equivalent in the continuum limit. The matter current is
forced by the bipartite structure; it is not postulated.

---

## 5. Vacuum dynamics for $A_\mu$ — where it gets harder

We now have:

- A gauge-covariant tick rule for matter.
- A gauge-invariant field strength $F_{\mu\nu}$.
- A matter current $J^\mu$ with the Dirac form.

To get Maxwell's equations $\partial_\nu F^{\nu\mu} = J^\mu$, we need
an equation of motion for $A_\mu$ itself. This requires an *action*
for the gauge field.

**This is the gap.** The existing framework specifies the matter
dynamics through the tick rule but does not specify a dynamics for
$A_\mu$. The Peierls phase appears in the tick rule as an
*externally specified* topological background — the framework currently
treats $A_\mu$ as given, not as a dynamical variable with its own
equations of motion.

To close the gap, one must postulate a gauge action. The natural
choice — and the one that produces standard QED in the continuum
limit — is the Wilson action

$$
S_\text{gauge} = \frac{1}{g^2} \sum_\text{plaquettes} \bigl(1 - \mathrm{Re}\,W_{\mu\nu}\bigr).
$$

For small lattice fields:

$$
1 - \mathrm{Re}\,W_{\mu\nu} \approx 1 - \cos(a^2 F_{\mu\nu}) \approx \frac{a^4}{2} F_{\mu\nu}F^{\mu\nu},
$$

so in the continuum limit

$$
S_\text{gauge} \to \frac{1}{2 g^2} \int d^4x\, F_{\mu\nu}F^{\mu\nu},
$$

the standard Maxwell action (up to a sign convention). Varying
$S_\text{gauge} + S_\text{matter}$ with respect to $A_\mu$ gives

$$
\partial_\nu F^{\nu\mu} = J^\mu,
$$

which is the inhomogeneous Maxwell equation. The homogeneous one
$\partial_{[\rho} F_{\mu\nu]} = 0$ is automatic from
$F_{\mu\nu} = \partial_\mu A_\nu - \partial_\nu A_\mu$.

**Status of the gauge action:** In standard lattice gauge theory the
Wilson action is justified by:
(i) locality (sum over local lattice elements);
(ii) gauge invariance (built from Wilson loops);
(iii) lowest non-trivial order (smallest loop is the plaquette);
(iv) reflection positivity and hermiticity (forces the specific form).

These are reasonable physical postulates and they uniquely fix the
action up to coupling. But they are postulates, not consequences of
the existing tick rule. The framework currently does not derive
$A_\mu$'s dynamics from anything more fundamental.

**Possible escape route (research program, not a derivation):**
If one defines the lattice path integral as a sum over session
histories weighted by their tick-rule probabilities, then integrating
out the matter sessions induces an effective action for $A_\mu$. The
leading term in the small-$a$ expansion of the induced action *is* the
Wilson form, by the standard argument that any gauge-invariant local
term must be built from plaquettes. So the Wilson action is induced,
not added. Whether this argument can be made rigorous within the
framework is a research question.

---

## 6. Maxwell, with the gauge action assumed

With the Wilson action assumed, the full system is:

- **Matter:** lattice Dirac operator with Peierls links (existing).
- **Gauge field:** Wilson action (postulated).
- **Coupling:** Peierls substitution (existing).

In the continuum limit, varying the action gives:

$$
\boxed{\;\partial_\nu F^{\nu\mu} = J^\mu, \qquad
\partial_{[\rho} F_{\mu\nu]} = 0.\;}
$$

These are Maxwell's equations.

Special cases:

- **No matter ($J^\mu = 0$):** $\Box A^\mu - \partial^\mu(\partial \cdot A) = 0$.
  In Lorenz gauge $\partial \cdot A = 0$, this is the photon wave
  equation $\Box A^\mu = 0$. Lattice photon dispersion (exp_09)
  confirms this in the long-wavelength limit.

- **Static matter ($\partial_t = 0$):** $\nabla \cdot \mathbf{E} = \rho$,
  $\nabla \times \mathbf{B} = \mathbf{J}$. Coulomb's law and
  Biot–Savart.

- **Plane-wave $A_\mu$:** transverse photons with two polarisation
  states (the two RGB/CMY chiralities). Spin-1, masslessness, and
  gauge invariance are all structural consequences of the
  derivation, not postulated.

---

## 7. Why this is asymmetric with the gravity derivation

Section 7 derives Newton from the existing tick rule alone. No new
field is introduced; clock density is already a feature of the
multi-session tick scheduler.

The EM derivation here introduces the link variable $A_\mu$. That
variable is consistent with the existing Peierls phase in the tick
rule, but it is not currently treated as dynamical. To get the
*equation of motion* for $A_\mu$, we must postulate a gauge action.
The Wilson action is the natural postulate, and the standard
arguments (locality, gauge invariance, minimality) uniquely fix it,
but those arguments are external to the tick rule.

The asymmetry is real and worth being honest about.

A way to state it: gravity in this framework is a *derived effective
theory* of clock density on the existing tick rule. EM in this
framework is a *separately postulated gauge theory* whose matter
coupling is forced by the existing tick rule, but whose gauge
dynamics is added by hand.

The unification claim of the paper is that both arise from the same
phase-field substrate. That claim is supported by the fact that the
matter coupling on both sides comes from the bipartite tick rule —
gravitational mass and electric charge are both expressions of the
same Zitterbewegung structure. But the *field equations* on each
side are derived from different sources: gravity from clock density,
EM from a postulated gauge action.

---

## 8. The vacuum twist field equation in the older notes — does it survive?

The older notes/vacuum_twist_field_equations.md proposes a unified
scalar equation

$$
\Box\phi - \sin^2(\phi/2)\,\phi = J_\text{grav} + J_\text{em}
$$

with $J_\text{em} = \varepsilon^{\mu\nu\rho\sigma}\partial_\nu F_{\rho\sigma}$.

There are two problems with this as written:

1. $\varepsilon^{\mu\nu\rho\sigma}\partial_\nu F_{\rho\sigma}$ vanishes
   identically when $F$ is the curl of $A$ (Bianchi identity). So the
   EM source term as stated is identically zero in standard EM.
2. A *scalar* $\phi$ is the wrong object to carry the curl content of
   the gauge field. Curl is intrinsically a vector operation; you
   cannot get $F_{\mu\nu}$ from a single scalar.

The right framework, as the present derivation shows, is:

- A *scalar* clock density $\rho_\text{clock}$ sourcing gravity through
  $\nabla^2 \rho_\text{clock}$ → Newtonian potential.
- A *vector* gauge field $A_\mu$ sourcing EM through $F_{\mu\nu}$ →
  Maxwell.

These are not two source terms for the same field. They are *two
different fields* on the lattice, each with its own equation of
motion, both arising from the bipartite tick rule.

The unification claim survives — both fields arise from the same
substrate, both couple to matter through Zitterbewegung — but the
unified scalar equation in the older note does not. The unification
is at the level of substrate and coupling, not at the level of a
single field equation.

This is worth correcting in the older note if it is to be cited from
the paper.

---

## 9. What the paper section should claim

Based on this attempt, the paper section can defensibly claim:

1. The Peierls-substituted tick rule is U(1)-gauge-covariant (derived,
   §2 above).
2. The lattice plaquette is $F_{\mu\nu}$ in the continuum limit
   (derived, §3 above).
3. The matter current is the Dirac current $\bar\psi\gamma^\mu\psi$,
   with $\gamma^\mu$ from the bipartite RGB/CMY structure (derived,
   §4 above; relies on Section 6.4).
4. With the Wilson gauge action, the continuum limit reproduces
   Maxwell's equations exactly (standard, §5–6 above).

It cannot defensibly claim:

1. That Maxwell's equations are derived from the lattice tick rule
   alone. They are not. They require the additional postulate of the
   Wilson action.
2. That a unified scalar phase field $\phi$ governs both gravity and
   EM. The unification is at the level of substrate, not at the level
   of a single field equation.

What the paper section *should* present is the honest version: a
derivation of the matter side from the tick rule, the gauge action as
the standard postulate of lattice gauge theory, and the unification
claim restricted to substrate/coupling rather than to a single
unified equation.

This is still a substantial unification — it is more than standard QED
+ GR offer, because here both forces share the same matter substrate
(the bipartite Zitterbewegung) and the same coupling mechanism
(Peierls / clock-density gradient). But it is not a single-equation
unification.

The natural route to closing the remaining gap — making the gauge
action *induced* rather than postulated — is the central follow-on
calculation suggested by this derivation. It is well-defined and
tractable, and §10 sets out what would need to be computed. Until it
is, the paper section claims the matter-side derivation honestly and
treats the Wilson action as the standard lattice-gauge postulate,
with the induced-action programme flagged as the path to fully
closing the parallel with the gravity derivation.

---

## 10. Open: the induced-action route — promising program, not yet a resolution

*This section incorporates the assessment of `em_derivation_solution.md`,
which proposed that the induced-action route resolves the gap entirely.
The proposal is structurally correct but overstates what has actually
been computed; this section sets the proposal at the right level —
"the calculation we now know how to do" rather than "the calculation
that is done."*

The natural route to closing the gap is to make the gauge action
*induced* rather than postulated. This is the Sakharov–Zeldovich
program applied to the lattice: integrate out the matter sessions in
a path-integral formulation and check that the leading gauge-invariant
local term in the resulting effective action is the Wilson plaquette.

Structurally, the argument is correct. Schematically:

$$
Z[U] = \sum_\text{$\psi$-histories} P_\text{tick}[\psi, U]
     = \det\bigl(D_\text{lat}[U]\bigr),
\qquad
S_\text{eff}[U] = -\mathrm{Tr}\,\ln D_\text{lat}[U].
$$

Expanding $\mathrm{Tr}\,\ln D_\text{lat}[U]$ as a sum over closed
lattice loops, the leading term is constrained by:

(i) **gauge invariance** — only Wilson loops can appear;
(ii) **locality** — leading terms involve only short loops;
(iii) **minimality** — the smallest non-trivial loop is the plaquette.

So the induced action is dominated, at leading order, by

$$
S_\text{eff}[A] = \frac{1}{g^2_\text{ind}}
    \sum_\text{plaquettes} \bigl(1 - \mathrm{Re}\,W_{\mu\nu}\bigr)
    + (\text{higher-loop corrections}).
$$

In the continuum limit, this *is* the Maxwell action. The argument is
the standard induced-gauge-theory calculation (Adams 2003,
Kogut–Susskind 1975 for the staggered case) and is well-known to
produce the right structural form.

**What this does *not* mean is that the gap is resolved.** Three
concrete gaps remain between the schematic argument and an actual
derivation in the framework.

### Gap A: Constructing a path integral from the stochastic tick rule

The tick rule produces probabilities, not complex amplitudes. The
$Z[U]$ form above presumes complex weights and a coherent measure.
Going from the framework's stochastic dynamics to a path-integral
formulation requires one of:

- the Onsager–Machlup / Martin–Siggia–Rose construction for
  stochastic processes;
- identifying underlying amplitudes whose moduli-squared are the tick
  probabilities;
- using the existing U(1) phase structure to define a sum over phase
  histories directly.

Each of these is a research-level question that has not been settled
in the framework.

### Gap B: The matter determinant has not been computed

The expansion of $\mathrm{Tr}\,\ln D_\text{lat}[U]$ in plaquette
operators is *schematic*. The actual *coefficients* of the resulting
plaquette terms — the induced gauge coupling $1/g^2_\text{ind}$, its
dependence on lattice spacing and matter content, the suppression of
higher-loop terms ($F^4$, $F\cdot\partial^2 F$, $\ldots$) — are
computable but not computed.

In QED this calculation produces the standard $\beta$-function; in
Yang–Mills it produces asymptotic freedom. In this framework, what
does it produce? The leading-term Wilson form is correct *if* the
coefficient comes out positive and finite at leading order. That is
the standard result for a well-defined fermion determinant on a
regular lattice, and it should hold here, but it has not been
verified.

### Gap C: The classical reduction

A path integral gives quantum dynamics; Maxwell's equations are
classical. Going from one to the other requires a saddle-point or
WKB argument. In standard lattice gauge theory this is the
small-coupling expansion.

In a stochastic framework with no obvious $\hbar \to 0$ limit, the
classical reduction is not automatic. The proposal in
`em_derivation_solution.md` collapses this into "$\delta S_\text{eff} = 0$
enforces $\mathcal{A}=1$ globally," but these are different
statements:

- $\mathcal{A}=1$ globally is unitarity (a quantum statement —
  probability is conserved when summed over all histories);
- $\delta S = 0$ is the classical equation of motion (a saddle-point
  statement — the dominant contribution to the path integral).

They happen to coincide in known cases, but the coincidence has to be
*argued*, not asserted. In the present framework that argument has
not been written.

### Status

The right characterisation of the induced-action route is:

- **The structure is correct.** Sakharov–Zeldovich is a real
  phenomenon and the schematic argument captures it.
- **The calculation is well-defined.** Each step of Gaps A–C is a
  tractable research question, not a conceptual mystery.
- **The calculation has not been done.** Treating the induced-action
  argument as a resolution of the gap would overclaim.

The honest bottom line: the gap from §5 is not yet closed, but we now
know exactly how to close it. The matter sector is already in place
to support the calculation; the missing pieces are constructing the
path-integral measure (Gap A), computing the determinant explicitly
(Gap B), and extracting the classical limit (Gap C). This is the
central follow-on calculation suggested by this whole derivation
attempt.

If the calculation works, the gauge action becomes induced rather
than postulated, and the EM derivation rises to the same level as the
gravity derivation. If it produces an unexpected form, that itself is
a falsifiable prediction. Either outcome is a result; the next step
is to do it.
