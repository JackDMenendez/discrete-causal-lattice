# exp_20: Emission Operator Comparison + Clock Fluid Density Connection

*Working notes, 2026-05-01. Extends `lattice_operation_algebra.md`.
Recovery file in case the conversation context is lost.*

> **Scaffolding for follow-on paper #13** in `notes/follow_on_implications.md`
> ("Operation Algebra of the Discrete Causal Lattice"). The exp_20
> arms A/B/C design is for the main paper; the path-algebra
> reformulation and the inside/outside split are the follow-on's
> mathematical core.

---

## What this file captures

A discussion that started from "we are missing some math unique to A=1
that looks like balanced nuclear chemistry equations" and ended at
three connected results:

1. The lattice operation algebra (tag-balance bookkeeping) — see
   `lattice_operation_algebra.md`.
2. A redesign of `exp_20` as a controlled comparison of three emission
   operators (rows 5, 6, 7 of the algebra).
3. An identification of $\mathcal{A}_\text{joint}(x)$ with the clock
   fluid density $\rho_\phi(x)$ at field-density resolution, which
   subsumes "energy conservation" into "joint amplitude conservation."

---

## The bug the algebra found

`exp_19c`'s amplitude drain (algebra row 5):

$$\psi_e' = (1-m)\,\psi_e, \quad \psi_\gamma' = \psi_\gamma + m\,\psi_e$$

is *not* amplitude-conserving even before `enforce_unity_spinor`
touches it. With $\psi_\gamma = 0$ initially:

$$\lVert\psi_e'\rVert^2 + \lVert\psi_\gamma'\rVert^2
  = (1 - 2m + 2m^2)\,\lVert\psi_e\rVert^2$$

Equals $\lVert\psi_e\rVert^2$ only at $m=0$ or $m=1$. At every other
rate the operation *destroys* joint amplitude at $O(m)$ per tick. Over
6000 ticks at $m=10^{-3}$ this compounds substantially.

The corrected form is the pointwise beam splitter (algebra row 6):

$$\psi_e'(x) = \cos\theta(x)\,\psi_e(x), \quad
  \psi_\gamma'(x) = \psi_\gamma(x) + \sin\theta(x)\,\psi_e(x)$$

which preserves $\lVert\psi_e\rVert^2 + \lVert\psi_\gamma\rVert^2$
exactly, by $\cos^2 + \sin^2 = 1$. Joint A=1 is enforced *by the operator's
unitarity* rather than by post-hoc renormalisation.

This means `enforce_unity_spinor` in its current form is the latent
bug that killed `exp_15`, `exp_19` v4, and (probably) `exp_19c`. It
sets per-session amplitude back to 1 every tick, which masks all the
amplitude that the drain was supposed to redistribute.

---

## exp_20 design

Three parallel arms on the `exp_12` two-body foundation (live proton,
mean-field Coulomb update, alternating tick order). Same parameters
across arms; only the emission operator differs.

| Arm | Operator | Algebra row | Hypothesis |
|-----|----------|:---:|------------|
| A (control) | $\psi_e \mathrel{-}= m\psi_e;\ \psi_\gamma \mathrel{+}= m\psi_e$, per-session `enforce_unity_spinor` | 5 + 2 | Reproduces `exp_19c`: photon doesn't grow, no settle |
| B (treatment) | $\psi_e(x) \mathrel{*}= \cos\theta(x);\ \psi_\gamma(x) \mathrel{+}= \sin\theta(x)\,\psi_e(x)$, **joint** A=1 enforcement (no per-session renorm of e or γ during emission) | 6 | Photon amplitude grows; electron orbit settles |
| C (alternative) | $\psi_e \mathrel{*}= e^{-i\alpha};\ \psi_\gamma \mathrel{*}= e^{+i\alpha}$ | 7 | Reproduces `exp_19` v5: amplitudes preserved but photon doesn't grow as observable |

### Falsification matrix

- **A and B both fail** → emission mechanism is something else
  entirely; algebra is wrong about row 6 being the fix.
- **A fails, B succeeds** → joint A=1 with unitary transfer is
  the correct emission physics, and `enforce_unity_spinor`-per-session
  was the latent bug across `exp_15`, `exp_19`, `exp_19c`.
- **A "succeeds" by `SETTLE_TOL = 0.15` and B doesn't differ from
  A** → the streak metric is measuring proximity to $R_1$, not
  tongue residence. The audit-table observation about predicted
  tongue width 3.3% becomes the headline: rerun under
  `SETTLE_TOL = 0.033` before claiming any settled result.

### Implementation scope

- The pointwise beam splitter is well-defined on the 65³ grid:
  $\lVert\psi_e'(x)\rVert^2 + \lVert\psi_\gamma'(x)\rVert^2 = \lVert\psi_e(x)\rVert^2 + \lVert\psi_\gamma(x)\rVert^2$
  pointwise, so joint A integrates exactly. No subtlety here.
- **Non-trivial change required**: `enforce_unity_spinor` must be
  *replaced* with a joint-amplitude enforcer (or omitted entirely on
  the photon and electron during emission, applied only on the proton).
  This is a real change to the `CausalSession` tick loop or the
  experiment wrapper; not a one-line edit.
- The proton session is unaffected — it should still call
  `enforce_unity_spinor` because no amplitude is leaving it.
- $\theta(x)$ schedule: same Coulomb-driven mask as `exp_19c`
  (excess potential energy above ground state), but with $\theta$
  small enough that the linearised drain rate matches the swept
  emission rates [0.01, 0.05, 0.1, 0.2, 0.5].

### Relation to the original exp_20

The original exp_20 was an Arnold-tongue dual-initialisation scan
(H0 vs H1) that became invalid because it used a fixed Coulomb well
without a live proton. The redesign here absorbs the original
question rather than answering it: if arm B settles, that *is* the
H0/H1-distinguishing result, because the orbit locks into the tongue
under the corrected operator. If you want a clean record, the
predecessor file should be marked superseded rather than deleted.

---

## Connection to clock fluid density (the cool part)

`A_joint` was ambiguous in the first draft of the algebra: rows 9–10
treated it as a count (sessions can be created/destroyed), rows 5–7
treated it as a budget (amplitude redistributed). Those agree only
when each session sits at unit amplitude. The clock-fluid connection
forces the field-density reading, which is the cleaner one.

### Three structural levels

| Level | Quantity | Conservation statement | Status |
|:---:|---|---|---|
| 1 | $\int \lVert\psi_i\rVert^2\,dx = 1$ | Per-session unitarity | Axiom; enforced per tick |
| 2 | $\mathcal{A}_\text{joint}(x) = \sum_i \lVert\psi_i(x)\rVert^2$ | Joint amplitude density (algebra tag) | Preserved by row 6/7, broken by row 5/2 |
| 3 | $\rho_\phi(x) = \sum_i \omega_i\,\lVert\psi_i(x)\rVert^2$ | Local clock-fluid continuity $\partial_t\rho_\phi + \nabla\cdot j_\phi = 0$ | exp_07 PASS; sources gravity |

Level 1 is the axiom. Level 2 is the operation-algebra tag. Level 3
is the continuum field equation that gives gravity.

**The relation:** $\rho_\phi(x)$ is $\mathcal{A}_\text{joint}(x)$
weighted by per-session instruction frequency $\omega_i$ — same
support, same flow, mass-weighted. Levels 2 and 3 are the same
object at different resolutions.

### What this gives for free

- **Photon emission** (row 9): adds amplitude to $\mathcal{A}_\text{joint}$
  at the emission point; adds $\omega_\gamma\cdot\alpha$ to $\rho_\phi$.
  Emission *injects clock fluid density locally* — a gravitational
  signature of emission, in principle observable.
- **Pair annihilation** (row 10): $\mathcal{A}_\text{joint}$ preserved;
  $\rho_\phi$ preserved iff $\sum \omega_\text{out} = \sum \omega_\text{in}$.
  This is $E = mc^2$ in the lattice — and it follows from
  $\mathcal{A}_\text{joint}$ conservation plus the $\omega$-weighting,
  not from a separate energy axiom.
- **The "single conservation law" claim** in `conservation_of_probability.md`
  gets a sharper form: $\mathcal{A}_\text{joint}$ conservation is the
  axiom; $\rho_\phi$ continuity is the same conservation law expressed
  at field-density resolution with mass weights; energy conservation
  is the $\omega$-weighted spatial integral. Three faces of one
  constraint.

### Prediction this seeds for exp_20

Row 5 (the broken drain) doesn't just violate joint A=1 — it
violates *local* $\rho_\phi$ continuity, because it changes
$\sum_i \lVert\psi_i(x)\rVert^2$ pointwise without a corresponding
flux. So `exp_19c`'s drain isn't just non-unitary; it's
**non-gravitational**: it sources/sinks clock fluid density without
a current.

This means arm A of exp_20 should be detectable as a *clock-fluid
non-conservation event* — measurable by integrating $\rho_\phi$ over
a region around the emission and watching for drift. Arm B (beam
splitter) should be conservative in this measure. Arm C (phase
rotation) should be trivially conservative because each session's
$\lVert\psi_i\rVert^2$ is untouched.

Adding $\rho_\phi$ drift as a diagnostic to the exp_20 metric ties
the experiment directly to the gravity sector and gives a second
falsifier independent of orbit settling.

---

## Path algebra: the natural inner home

**Observation that motivated this section.** $\mathcal{A}_\text{joint}(x)$
isn't only a state quantity — it's a *combinatorial enumeration*. Each
session's amplitude at $x$ is a discrete Feynman sum:

$$\psi_i(x, t) = \sum_{\gamma : x_0 \to x} W(\gamma)\, e^{i\Phi(\gamma)}$$

over admissible bipartite paths $\gamma$ from initial node $x_0$ to $x$
in $t$ steps, with $W(\gamma)$ the product of hop weights
$\cos(\delta\phi/2)$ and residence weights $i\sin(\delta\phi/2)$ along
$\gamma$, and $\Phi(\gamma)$ the accumulated phase. So:

$$\lVert\psi_i(x)\rVert^2 = \sum_{\gamma, \gamma'} W(\gamma)W(\gamma')^*\, e^{i(\Phi(\gamma) - \Phi(\gamma'))}$$

is a sum over path × conjugate-path pairs, and $\mathcal{A}_\text{joint}(x)$
is the further sum over sessions. Triple combinatorial structure:
paths × conjugate paths × sessions.

### Why this changes the algebraic answer

The Fock-space embedding sketched in the prior algebraic discussion is
correct but *external* — it imposes operator algebra on top of states.
The combinatorial structure here is **internal**: the algebra is
already in the path enumeration.

The natural object is the **phase-weighted path algebra of the
bipartite octahedral graph** (notation $\mathbb{C}G$ for graph $G$).
This is a real algebra in the strict sense:

- **Vector space**: formal $\mathbb{C}$-linear combinations of admissible paths.
- **Multiplication**: concatenation when endpoints match, zero otherwise. Associative.
- **Identity**: formal sum of length-0 paths at every node.
- **Relations** (where the lattice physics enters):
  - Bipartite alternation: no two RGB hops in a row, and similarly for CMY.
  - Unitary closure: $\sum_\gamma W(\gamma)W(\gamma)^* = 1$ per session.
  - Discrete Klein-Gordon residence/hop split per tick.

Path algebras of quivers are well-studied territory in representation
theory. Working *inside* the path algebra has a benefit over Fock-space
embedding: everything is built from the lattice itself, not imposed.

### What conservation laws become

| Tag | Path-algebra reformulation | Difficulty to verify |
|-----|----------------------------|----------------------|
| `A_session` | Per-session unitary closure relation | Axiom; verifiable by direct computation |
| `A_joint` (single-session) | Flow conservation theorem on the weighted directed graph defined by hop weights | Standard combinatorial result |
| `π` (parity) | Path-length parity alternates with each hop | **Automatic** from graph bipartiteness |
| `χ` (chirality) | Whether the path algebra has a $\mathbb{Z}_2$-grading respected by multiplication | Checkable; reduces to commutator with R/L assignment operator |
| Winding $(p, q)$ | **Homotopy class of closed paths** around a fixed point | Connects to first homology $H_1$ of the orbit graph |

The last row is the part that matters most. Arnold-tongue locking has
always been a winding-number statement; if the operation algebra
realises it as a homology class of the lattice path algebra, then
**quantization is a topological invariant of the graph, not a
dynamical accident**. That's a stronger version of the framework's
claim than what currently appears in the paper.

### Inside/outside split

For multi-session operations (emission, annihilation), the path
algebra alone isn't enough — those operations change the number of
session factors. The structure is:

- **Inside (single session)**: phase-weighted path algebra.
  Conservation laws → combinatorial invariants of path multiplication.
- **Outside (multi-session)**: Fock-like tensor structure with
  creation/annihilation operators that change the number of
  path-algebra factors.

Full conservation algebra = commutant computed across both layers.
Single-session tags (A_session, χ_i, p_i, single-session winding)
come from path-algebra invariants; multi-session tags
(A_joint integrated, N, joint π) come from the Fock layer.

### Caveats

1. The bipartite octahedral graph is infinite (lattice on $\mathbb{Z}^3$),
   so we work with the *completed* path algebra — a topological
   algebra rather than purely algebraic. Convergence questions appear,
   though per-session unitarity keeps things tame.
2. Path-algebra benefit over operator algebra is *narrow*: it's clean
   for single-session combinatorics, but multi-session structure
   needs Fock layered on top. The split isn't a unification — it's a
   clean separation of concerns.

### Why this is the next direction

Two of the open questions become *finite* computations under the
path-algebra view:

- $\chi$ conservation reduces to a $\mathbb{Z}_2$-grading question on
  the path algebra — checkable by tracking R/L assignments along
  paths and verifying multiplicative closure.
- Winding $(p,q)$ becomes an $H_1$ statement, connecting the lattice
  quantum number to a topological invariant of the orbit graph.

Both are routes to *proving* conservation laws rather than asserting
them, which is what the original "balanced equations" question was
reaching for.

---

## Open questions still on the table

These are imported from `lattice_operation_algebra.md`, sharpened
under the path-algebra view where applicable:

1. **Is $\chi$ (chirality) actually a conserved tag?** Path-algebra
   form: does the bipartite path algebra admit a $\mathbb{Z}_2$-grading
   (R/L paths) that is respected by path concatenation? If yes, $\chi$
   is conserved exactly. If only respected modulo a residual, $\chi$ is
   approximately conserved and the residual is the falsifier.
2. **What is the conserved phase quantum?** Path-algebra form: are the
   Arnold-tongue lock-in ratios $(p,q)$ generators of $H_1$ of the
   orbit graph? If yes, lock-in is a topological invariant; quantization
   is geometric, not dynamical.
3. **Does the algebra forbid anything QM allows?** The earn-your-keep
   test. Under the inside/outside split, this becomes: does the
   commutant $T'_\text{lattice}$ on the path algebra ⊗ Fock structure
   differ from the standard QM commutant? If they coincide, the
   formalism is bookkeeping; if they don't, you have a falsifier.
4. **Does the operation algebra induce its own bilinear form on tag
   space, with eigenstructure analogous to $Q$ (gauge sector,
   eigenvalues {4,4,16}) and the kinematic ellipsoid ({4,4,1})?** A
   parallel operation tensor would be the structural completion of
   the picture (static substrate / dynamic operations / both with
   bilinear forms whose eigenstructures are physical).

---

## Where to pick this up

If the conversation context is lost, recovery path:

1. Read `notes/lattice_operation_algebra.md` for the tag-balance table.
2. Read this file for the exp_20 design, the clock-fluid identification,
   the bug analysis of row 5, and the path-algebra reformulation of
   the conservation question.
3. The audit table at `paper/sections/audit_table.tex:133-140` is the
   authority for `exp_19c` status (PART, 0 recoils, v10 sweeps).
4. Two parallel concrete next steps:
   - **Empirical**: implement arm B of exp_20 — pointwise
     beam-splitter drain with joint A=1 enforcement — and compare
     against arm A (current `exp_19c` operator).
   - **Theoretical**: write down the bipartite path algebra
     explicitly (generators = hops along $\pm V_1, \pm V_2, \pm V_3$
     with bipartite alternation; multiplication = concatenation;
     phase weights from $\delta\phi$). Then check whether (a) it
     admits a $\mathbb{Z}_2$-grading respected by multiplication
     (open question 1), and (b) the Arnold-tongue ratios $(p,q)$
     generate $H_1$ of the orbit subgraph (open question 2). Both
     are finite computations once the algebra is written down.
