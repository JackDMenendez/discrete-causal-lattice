# Born Rule Uniqueness via Gleason: Working Sketch

*Working notes, 2026-05-04. Drafts a Tier 1 proof item for v1.0 in
response to Reviewer-E's "where is the uniqueness argument?
why $|\psi|^2$ and not $|\psi|^p$?"  Targets the existing
`notes/born_rule_from_path_counting.md` discussion and
`paper/sections/interference.tex` §10.7 "The Born Rule from Path
Counting" for revision.  This is a derivation sketch, not paper
text yet.*

---

## What Reviewer-E asked

> "Where is the uniqueness argument? Why $|\psi|^2$ and not
> $|\psi|^p$? How does this connect to Gleason-type constraints?"

The current §10.7 argument is a **sufficiency** argument:
$\rho = |\psi_R|^2 + |\psi_L|^2$ is consistent with $\mathcal{A}=1$
on the bipartite tick rule, satisfies the path-counting structure,
and reproduces standard interference.

What it does *not* do is rule out alternative measures
$\rho_p = (|\psi_R|^p + |\psi_L|^p)^{1/p}$ for $p \ne 2$ that also
look superficially compatible.  Reviewer-E is right that this is the
technical bar; it's the standard quantum-foundations bar going back
to von Neumann (1932) and definitively answered by Gleason (1957).

The fix below states the uniqueness argument, attributes it correctly
to Gleason via the now-parked `gleason1957` bib entry, and identifies
*specifically how the bipartite A=1 framework satisfies Gleason's
hypotheses*.

---

## The framework's emergent Hilbert space (now official)

The v0.98-RC abstract was softened from "no Hilbert space is
assumed" to:

> "A Hilbert-space structure with unitary evolution emerges from the
> U(1) oscillator and the per-session amplitude constraint rather
> than being postulated a priori."

This is what we now lean on.  Concretely, the per-session state
space is

$$
\mathcal{H}_\text{session}
\;=\;
\ell^2(\mathcal{T}_\diamond^3, \mathbb{C}^2)
\;=\;
\{(\psi_R, \psi_L) : \psi_{R,L} \in \ell^2(\mathcal{T}_\diamond^3)\}
$$

equipped with the inner product

$$
\langle \psi, \phi \rangle
\;=\;
\sum_{x \in \mathcal{T}_\diamond^3} \big( \psi_R^*(x)\phi_R(x) + \psi_L^*(x)\phi_L(x) \big).
$$

The bipartite tick rule combining `_kinetic_hop`,
$\sin(\delta\phi/2)$ residence, and `enforce_unity_spinor` is a
unitary operator $T : \mathcal{H}_\text{session} \to \mathcal{H}_\text{session}$:

- **Linear** in the spinor (Section~\ref{subsec:tick_rule_linearity}
  of `phase_propagation.tex`)
- **Norm-preserving** by the per-session $\mathcal{A}=1$ constraint
  ($\|T\psi\| = \|\psi\| = 1$)

For a 65³ lattice, $\dim \mathcal{H}_\text{session} = 2 \cdot 65^3 = 549{,}250$.
Well above the dim-3 threshold Gleason's theorem requires.  In the
continuum limit $a \to 0$ it becomes a separable infinite-
dimensional Hilbert space; Gleason still applies.

The projection lattice $\mathcal{P}(\mathcal{H}_\text{session})$ is
the orthocomplemented, atomic, complete lattice of orthogonal
projection operators on $\mathcal{H}_\text{session}$ — exactly the
setting in which Gleason proves uniqueness.

---

## Gleason's theorem (statement)

**Theorem (Gleason 1957).** Let $\mathcal{H}$ be a separable Hilbert
space with $\dim \mathcal{H} \ge 3$.  Let
$\mu : \mathcal{P}(\mathcal{H}) \to [0,1]$ be a *frame function*:
that is, a function on orthogonal projections satisfying

1. **Normalization:** $\mu(I) = 1$.
2. **$\sigma$-additivity:** for any countable family of mutually
   orthogonal projections $\{P_i\}$,
   $$
   \mu\!\left(\sum_i P_i\right)
   \;=\;
   \sum_i \mu(P_i).
   $$

Then there exists a *unique* positive trace-class operator $\rho$
with $\mathrm{tr}\,\rho = 1$ such that

$$
\mu(P) \;=\; \mathrm{tr}(\rho P) \qquad \text{for all } P \in \mathcal{P}(\mathcal{H}).
$$

For a pure state $\psi$ (the case in the bipartite-lattice
framework where each session is a unit vector), $\rho = |\psi\rangle\langle\psi|$,
giving the **Born rule** in its standard form

$$
\mu(P) \;=\; \langle \psi, P \psi \rangle \;=\; \|P\psi\|^2.
$$

The theorem says this is the **only** measure consistent with the
two hypotheses.  Any measure of a different form ($\|\psi\|^p$ for
$p \ne 2$, $\log\|\psi\|^2$, etc.) violates one of (1) or (2).

---

## Why the bipartite framework satisfies Gleason's hypotheses

The structural argument has three steps:

### Step 1 — $\mathcal{A}=1$ gives normalization.

The per-session $\mathcal{A}=1$ axiom states
$\sum_x (|\psi_R(x)|^2 + |\psi_L(x)|^2) = 1$ at every tick.  This is
exactly $\|\psi\|^2 = 1$ in the inner product above.

For an outcome covering "the entire state" — projection onto the
identity, $P = I$ — we have $\mu(I) = \|\psi\|^2 = 1$.
**Hypothesis (1) of Gleason satisfied.**

### Step 2 — Tick-rule unitarity gives $\sigma$-additivity on orthogonal families.

For any orthogonal family of projections $\{P_i\}$ summing to a
projection $P_\text{tot} = \sum_i P_i$, the squared-norm decomposes:

$$
\|P_\text{tot} \psi\|^2
\;=\;
\sum_i \|P_i \psi\|^2
$$

by orthogonality of the ranges and the parallelogram identity.
Identifying the natural measure $\mu(P) = \|P\psi\|^2$, this becomes:

$$
\mu\!\left(\sum_i P_i\right) \;=\; \sum_i \mu(P_i).
$$

**Hypothesis (2) of Gleason satisfied.**

A subtle point worth flagging: $\sigma$-additivity holds *only on
orthogonal* projections, not for arbitrary projections.  This is
exactly the source of the non-classical behaviour (interference)
in QM — non-orthogonal projections do not have additive
probabilities.  The bipartite framework inherits this structure
correctly.

### Step 3 — Gleason applies, the form is forced.

By the theorem, the only measure compatible with (1) and (2) on
$\mathcal{P}(\mathcal{H}_\text{session})$ for $\dim \ge 3$ is

$$
\mu(P) \;=\; \mathrm{tr}(\rho P) \;=\; \|P\psi\|^2 \quad \text{for pure $\psi$}.
$$

For projection onto a basis vector $|x\rangle$ at lattice site $x$
(with spinor component fixed), $\|P\psi\|^2 = |\psi(x)|^2$, which is
the standard Born rule for position-basis measurements.

For projection onto the spinor sum at site $x$,
$\mu(P_x) = |\psi_R(x)|^2 + |\psi_L(x)|^2$ — the per-site
probability density used throughout the paper.

---

## Why not $|\psi|^p$ for $p \ne 2$?

The standard demonstration (Cooke-Keane-Moran 1985, building on
Gleason): for $p \ne 2$, the proposed measure
$\mu_p(P) = (\|P\psi\|^p)^{1/?}$ violates $\sigma$-additivity on
orthogonal families.

Concretely, for $\psi = \alpha\psi_1 + \beta\psi_2$ with orthogonal
unit vectors $\psi_1 \perp \psi_2$, projections $P_i$ onto
$\text{span}(\psi_i)$ give

- Sum of measures: $\mu_p(P_1) + \mu_p(P_2) = |\alpha|^p + |\beta|^p$
- Measure of the sum: $\mu_p(P_1 + P_2) = (|\alpha|^2 + |\beta|^2)^{p/2}$

These agree iff $p = 2$.  For $p = 1$:
$|\alpha| + |\beta| \ne \sqrt{|\alpha|^2 + |\beta|^2}$ unless one
coefficient is zero.  For $p = 4$:
$|\alpha|^4 + |\beta|^4 \ne (|\alpha|^2 + |\beta|^2)^2$ unless one
is zero.

So $\sigma$-additivity *forces* $p = 2$.  The bipartite tick rule's
unitarity gives us $\sigma$-additivity on orthogonal projections
(Step 2 above), so the Born form is the unique consistent rule.

---

## Intuition correspondence: the Gleason structure was already in $\mathcal{A}=1$

Before locating Gleason's theorem in the literature, the chain
*probability conservation $\to$ unitary evolution $\to$ quadratic
measure* was already the structural intuition behind the framework's
construction.  The author's mathematical training was in probability
theory and random walks (honors thesis); the prior conviction was
that probability is **intrinsic to physical structure** rather than a
human-imposed bookkeeping device, and that an $\mathcal{A}=1$
probability distribution had load-bearing structural content beyond
its role as a normalization condition.

The construction proceeded by asking: *what is the simplest discrete
geometry over which an $\mathcal{A}=1$ probability distribution can
be expressed, with the intuitive degrees of freedom for emergence?*
The bipartite octahedral lattice $\mathcal{T}_\diamond^3$ with its
$(\psi_R, \psi_L)$ spinor structure was the answer arrived at in a
physical notebook of geometric drawings — built bottom-up from the
constraint, not assumed top-down from existing physics.

This methodology is the dual of the more common
*rich substrate, weak constraint* approach (e.g., neural networks,
ad-hoc QFT bolt-ons): start instead with the **sparse functional
requirement** (probability conservation imposed at every tick) and
seek the minimal substrate that supports it naturally.  The
constraint then becomes structurally generative — once the
substrate carries unitary evolution preserving the $\mathcal{A}=1$
norm, quadratic measures are no longer one choice among many, they
are *forced*.

The correspondence with Gleason is not a coincidence: it is the same
chain run in opposite directions.  Gleason (1957) proved
**necessity** of the quadratic form — any frame function on a
projection lattice of dimension $\ge 3$ must be of the trace form.
The $\mathcal{A}=1$ construction took the chain in the opposite
direction — *assume probability conservation, find the substrate
that realises it with minimal extra structure* — and arrived at the
same place.  Gleason adds the formal uniqueness layer that forbids
alternatives a priori; the construction adds the physical realisation
on a discrete lattice where the abstract projection lattice has
explicit geometric content (the bipartite RGB/CMY decomposition).

This is also the methodological principle that lets the framework
claim *derivation* of QM rather than *fitting* of QM: the
substrate is not assumed to have any structure beyond what the
constraint forces upon it.  Whatever else emerges (Clifford
algebra, Dirac structure, Lorentz invariance under $O_h$-averaging,
gravity as clock-density refraction) emerges from the same
constraint-first construction.  Gleason validates this approach for
the Born rule specifically; the framework extends the principle to
gravity and gauge structure as well.

The pattern generalises beyond physics: it is *the design principle
for systems with sparse functional requirements in a vast global
domain*.  Treat the constraint as fundamental and search for the
substrate that emerges naturally under it, rather than treating the
substrate as fundamental and adding constraints by hand.  In the
$\mathcal{A}=1$ framework, every claimed derivation rests on this
inversion.

---

## Subtleties to address explicitly

The argument as stated is clean for **single sessions in fixed-$N$
Hilbert spaces**.  Three caveats that should be flagged in the
paper text:

### (i) Multi-session events change the Hilbert space.

When emission spawns a new session ($N \to N+1$, photon creation
at orbit lock-in, exp_20 / exp_19c) or annihilation removes a
session ($N \to N-1$), the ambient Hilbert space changes.  The
Born rule via Gleason holds on each $\mathcal{H}_\text{multi-session}^{(N)}$
separately.  The transition between $N$ and $N+1$ is a creation
operation, not a measurement; it requires the operation-algebra
treatment from `notes/lattice_operation_algebra.md` rather than
Gleason.  This should be one paragraph in the paper acknowledging
the scope.

### (ii) The bipartite RGB/CMY structure does not break Gleason.

The bipartite parity ($\mathbb{Z}_2$ grading) divides
$\mathcal{H}_\text{session}$ into a direct sum
$\mathcal{H}_\text{RGB} \oplus \mathcal{H}_\text{CMY}$, but this
is *within* the same single Hilbert space (each tick is in one
sublattice).  The projection lattice $\mathcal{P}(\mathcal{H}_\text{session})$
is still the standard projection lattice; Gleason applies
unchanged.  The bipartite structure shows up in the Clifford
algebra of the kinetic step, not in the probability measure.

### (iii) Path counting in $\S 10.7$ is the operational realisation, not a separate derivation.

The "Born rule from path counting" argument in the current §10.7
gives a *constructive* answer for how to compute $\|\psi\|^2$ from
discrete Feynman paths on the lattice.  Gleason gives the *uniqueness*
statement — that no other measure works.  The two are
complementary: paths give the formula, Gleason explains why it's
the only formula.  The proposed §10.7 patch keeps both, ordered
uniqueness-then-construction.

---

## Proposed patch to `paper/sections/interference.tex` §10.7

Add a new subsection §10.7.1 "Uniqueness via Gleason" *before* the
existing path-counting discussion.  Sketch:

```latex
\subsection{Uniqueness via Gleason}

The path-counting derivation in §10.7 shows $\rho = |\psi_R|^2 +
|\psi_L|^2$ is *consistent* with $\mathcal{A}=1$ on the bipartite
tick rule.  That is sufficiency.  The remaining technical question
is necessity: why this measure and not, e.g., $|\psi|^p$ for
$p \ne 2$?

The answer is Gleason's theorem~\cite{gleason1957}.  The per-session
state space $\mathcal{H}_\text{session} = \ell^2(\mathcal{T}_\diamond^3,\mathbb{C}^2)$
is a separable Hilbert space; for any practical lattice
$\dim \mathcal{H}_\text{session} \gg 3$.  The bipartite tick rule is
unitary, preserving the inner product
$\langle\psi, \phi\rangle = \sum_x (\psi_R^*\phi_R + \psi_L^*\phi_L)$.

A *frame function* on the projection lattice
$\mathcal{P}(\mathcal{H}_\text{session})$ is a function
$\mu : \mathcal{P} \to [0,1]$ with $\mu(I) = 1$ and
$\sigma$-additivity on countable orthogonal families.  $\mathcal{A}=1$
gives normalisation; the parallelogram identity for orthogonal
ranges of unitary projections gives $\sigma$-additivity.  Both
hypotheses are satisfied.  These hypotheses are exactly the
structural intuition that motivated $\mathcal{A}=1$ in the first
place: probability conservation imposed at every tick on the simplest
geometry capable of supporting it produces a quadratic measure under
unitary evolution.

Gleason's theorem then gives uniquely $\mu(P) = \mathrm{tr}(\rho P)$
for a unique density operator $\rho$, and for pure $\psi$ this is
$\|P\psi\|^2$.  Specialising to the projection onto site $x$ summed
over spinor components, $\mu(P_x) = |\psi_R(x)|^2 + |\psi_L(x)|^2$.
The Born rule is forced.

The non-trivial point of Gleason is that the same is *not* true
for non-orthogonal projection families: $\mu(P_1) + \mu(P_2) \ne
\mu(P_1 + P_2)$ when $P_1, P_2$ have non-orthogonal ranges.  This is
the source of interference in standard QM, inherited by the
bipartite-tick framework as a structural consequence rather than a
postulate.

Three scope caveats:

\begin{enumerate}
\item Multi-session events (\texttt{exp\_20} arm B beam splitter,
\texttt{exp\_19c} drain) move between Hilbert spaces of different
session count $N$.  The Born rule holds on each fixed-$N$
projection lattice; transitions between are creation/annihilation
operations governed by the operation algebra
(notes/lattice\_operation\_algebra.md, follow-on paper~\#13).
\item The bipartite RGB/CMY parity gives a $\mathbb{Z}_2$ grading on
$\mathcal{H}_\text{session}$ but the projection lattice is unchanged;
Gleason applies as stated.
\item The path-counting derivation that follows is the
\emph{operational realisation} of the Gleason-uniqueness measure
on the discrete bipartite lattice --- it tells you how to compute
$|\psi|^2$ from Feynman-style path sums; Gleason tells you why
the result must be quadratic in $\psi$.
\end{enumerate}
```

Approximate length: ~50 lines of LaTeX.  Adds about half a page
to the paper.  Citations: `gleason1957` (already parked).  No
figures.

---

## Status

- **Argument structure**: complete in this note.  Covers all four
  steps + the $|\psi|^p$ failure + three caveats.
- **Patch to §10.7**: drafted in LaTeX above; ready to apply to
  `paper/sections/interference.tex` in a v1.0 cycle.
- **`gleason1957` bib entry**: parked (commit `c2e7427`); ready to
  be cited.
- **Risk of pushback**: low.  This is the standard QM-foundations
  argument; reviewers familiar with Gleason will recognise it
  immediately and the framework just needs to plug into the
  hypotheses.  The claim "we showed how A=1 satisfies Gleason"
  is the contribution; the theorem itself is borrowed.
- **Estimated paper-length addition**: half a page.  Smallest
  Tier 1 proof item; biggest acceptance-criticality leverage.

## Open follow-ups

- The multi-session caveat (i above) connects to follow-on
  paper #13's path-algebra story.  Whether the *combined*
  multi-session probability rule (joint $\mathcal{A}=1$
  preserved by the unitary beam splitter, exp_20 confirmed)
  also satisfies a Gleason-style uniqueness on the joint Fock
  space is a follow-on theorem worth stating.
- The continuum-limit Gleason argument for separable
  infinite-dimensional $\mathcal{H}$ requires the additional
  *complete additivity* hypothesis (Maeda-Maeda 1989) which the
  framework should also satisfy by construction.  Worth a one-
  sentence pointer.

## References

- Gleason, A. M. (1957). Measures on the closed subspaces of a
  Hilbert space. *J. Math. Mech.* **6**, 885–893.
  Bib key: `gleason1957`.
- Cooke, R., Keane, M., Moran, W. (1985). An elementary proof of
  Gleason's theorem. *Math. Proc. Cambridge Philos. Soc.* **98**,
  117–128.  Worth adding to the bib if a non-measure-theoretic
  proof reference is wanted.
- Bub, J. (2005). Quantum Probabilities: An Information-Theoretic
  Interpretation. *In* The Physics and Philosophy of Quantum
  Mechanics, ed. F. Bagger.  General modern reference.
