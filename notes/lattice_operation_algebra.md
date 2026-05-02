# Lattice Operation Algebra: Tag-Balance Bookkeeping

*Working notes, 2026-05-01. Companion to `conservation_of_probability.md`
and `photon_emission_from_A1.md`.*

> **Scaffolding for follow-on paper #13** in `notes/follow_on_implications.md`
> ("Operation Algebra of the Discrete Causal Lattice"). Kept in back
> pocket while the main paper focuses on Geometry First. Used internally
> for experiment design (exp_20) and bug analysis (exp_19c row-5
> non-unitarity). Arithmetic-level results may flow into the main
> paper as short observations; the full algebraic apparatus is the
> follow-on.

---

## Why This Exists

`Q` (eigenvalues `{4, 4, 16}`, gauge sector) and the kinematic ellipsoid
(eigenvalues `{4, 4, 1}`) are tensors on the *calibrated lattice* —
properties of the substrate at rest, expressed as quadratic forms whose
eigenstructure encodes anisotropy.

This file proposes the analogous structure for *operations* — the discrete
events that act on tagged session bundles. The intent is the same as
balanced nuclear-chemistry equations: a column for each conserved
quantity, a row for each elementary operation, balance rules per column.
Forbidden processes are those for which no balanced row exists.

The motivation is concrete: `exp_19c` is broken because its amplitude
drain plus per-session `enforce_unity_spinor` violates joint-amplitude
balance, but the framework has no formal language to say so. Once the
tags are written down, the bug becomes a type error.

---

## Tag Columns

| Tag | Definition | Status in code |
|-----|------------|----------------|
| `A_joint(x)` | Field density: $\mathcal{A}_\text{joint}(x) = \sum_i \lVert\psi_i(x)\rVert^2$ at each lattice point. Budget $\int \mathcal{A}_\text{joint}\,dx$ is the scalar integral. See `exp_20_emission_operator_and_clock_fluid.md` for the field-density form's connection to $\rho_\phi$ (clock fluid). | **Not enforced** |
| `A_session` | $\lVert \psi_i \rVert^2$ for one session (integral) | Enforced by `enforce_unity_spinor` per session per tick |
| `N` | Number of sessions in the bundle | Set at script start; emission/annihilation would mutate it |
| `π` | Joint (tick parity, active sublattice). RGB-active on even ticks; CMY-active on odd. Flips together. | Tracked by `tick_counter`; alternation is the kinetic structure |
| `χ_i` | Chirality balance $\lVert \psi_R \rVert^2 - \lVert \psi_L \rVert^2$ for session $i$ | Not tracked; emerges from initial conditions and dynamics |
| `p_i` | Linear momentum proxy: CoM drift rate of session $i$ | Computed *ad hoc* by `density_com` for Coulomb mean-field |

`A_joint = N` whenever every session is at unit amplitude; the two are
distinct only across operations that move amplitude *between* sessions.

`χ` is included as a candidate tag because the bipartite tick rule
swaps R/L roles every tick; its conservation law (if any) is an open
question — see notes at the bottom.

---

## Operation Rows

Symbol legend for the table:

- `=` preserved exactly
- `↻` cyclically advances (e.g. parity flips)
- `→` transferred between sessions (joint sum preserved, individual not)
- `↑N` increases session count by N (and similarly `↓N`)
- `±` modified
- `0` not applicable to this operation
- `✗` violated by this operation as currently coded

| # | Operation | A_joint | A_session | N | π | χ | p |
|---|-----------|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | Tick (full step: hop + residence + spinor combine) | = | = | = | ↻ | ± | ± |
| 2 | `enforce_unity_spinor` (per session) | ✗ | = | = | = | = | = |
| 3 | Phase rotation $e^{-i\alpha}$ (uniform, single session) | = | = | = | = | = | = |
| 4 | Coulomb potential refresh (mean-field from other CoM) | = | = | = | = | = | = |
| 5 | Drain as written: $\psi_e \mathrel{-}= m\psi_e;\ \psi_\gamma \mathrel{+}= m\psi_e$ | ✗ | ✗ | = | = | = | ± |
| 6 | Drain (beam-splitter): $\psi_e \mathrel{*}= \cos\theta;\ \psi_\gamma \mathrel{+}= \sin\theta\,\psi_e$ | = | → | = | = | ± | ± |
| 7 | Phase-rotation drain (`exp_19` v5): $\psi_e \mathrel{*}= e^{-i\alpha};\ \psi_\gamma \mathrel{*}= e^{+i\alpha}$ | = | = | = | = | = | ± |
| 8 | Recoil kick (theoretical, stubbed in `exp_19c`) | = | = | = | = | = | → |
| 9 | Session creation (emission spawns new session at lock-in) | = | → | ↑1 | depends on $\omega_\gamma$ | ± | ± |
| 10 | Pair annihilation $e + p \to 2\gamma$ | = | → | ↓0 | depends | balance to 0 | balance to 0 |

### Reading the table

Row 1 (tick) is the *closed* operation: every tag balances. This is the
A=1 axiom realised — the tick rule was constructed so per-session
amplitude is exact, parity alternates, and CoM/chirality drift in
allowed ways.

Row 2 is the source of the joint-A=1 bug. `enforce_unity_spinor`
preserves per-session amplitude but **violates joint A** whenever a
session was below unit amplitude (it adds amplitude that didn't come
from anywhere). For a single closed session that never loses amplitude,
the violation is zero by construction. Once any operation can change
per-session amplitude, the violation is real.

Row 5 (the drain as currently written in `exp_19c`) has a concrete
arithmetic problem:

$$\lVert\psi_e'\rVert^2 + \lVert\psi_\gamma'\rVert^2
  = (1-m)^2\lVert\psi_e\rVert^2 + m^2\lVert\psi_e\rVert^2 + \lVert\psi_\gamma\rVert^2 + 2\,\mathrm{Re}\langle m\psi_e, \psi_\gamma\rangle.$$

For $\psi_\gamma = 0$ this is $(1 - 2m + 2m^2)\lVert\psi_e\rVert^2$,
which equals $\lVert\psi_e\rVert^2$ only at $m=0$ or $m=1$. The drain
*destroys* joint amplitude at every other rate. Per-tick error is
$O(m)$ for small $m$; over 6000 ticks at $m=10^{-3}$ this compounds.

Row 6 is the corrected version: a unitary 2-mode rotation (beam
splitter) preserves joint amplitude exactly. This is what the operation
*should* be if "amplitude transfer" is the intended physics.

Row 7 (`exp_19` v5) is amplitude-conserving for a different reason —
each session is rotated by a unit-modulus phase, so per-session and
joint amplitude are both untouched. But it transfers *phase coherence*,
not amplitude — the photon's $\lVert\psi_\gamma\rVert^2$ never grows.
If "emission" requires the photon to gain amplitude, v5 is conservative
to a fault: it doesn't actually emit anything observable as amplitude.

Rows 9 and 10 are theoretical — the framework asserts session creation
at lock-in and pair annihilation as A=1 necessities, but no operation
in the codebase realises them. The table positions them as constraints
that any future implementation must satisfy.

---

## Worked Examples

### Bare two-body orbit (no emission)

State: $\{e, p\}$, both with $\lVert\psi\rVert^2 = 1$, joint $A = 2$,
$N = 2$, $\pi$ alternating with global tick.

Per-tick operation: row 1 applied to each session, row 4 (Coulomb
refresh) applied between them. Both tags balance every column.

**Conserved every tick:** `A_joint = 2`, `N = 2`, `π` alternates, each
`A_session = 1`. CoM may drift; chirality may oscillate.

This is what `exp_12` gets right and what the bare two-session limit of
`exp_19c` (with `emission_rate = 0`) reproduces — and `exp_19c`'s
"baseline" `max_streak = 11` is the same baseline as `exp_19c` with
emission, indicating the emission machinery is inert. The table makes
this auditable: rows 5 and 7 don't actually grow `A_session` for the
photon, so there is no observable emission.

### Emission as session creation (theoretical)

$$\{e\}\ [A_e = 1]\ \longrightarrow\ \{e', \gamma\}\ [A_{e'} = 1-\alpha,\ A_\gamma = \alpha].$$

Tag balance:
- `A_joint`: $1 = (1-\alpha) + \alpha$. ✓
- `N`: $1 \to 2$. **`N` is not conserved across this row.** It is the
  defining feature of session creation.
- `π`: depends on the photon's $\omega_\gamma$ initial condition. If
  the photon starts on the same parity as the parent electron, $\pi$ is
  preserved on the joint state.
- `χ`: photon chirality is set at creation; balance is a free
  parameter.
- `p`: must balance for momentum conservation. Sets the photon's
  initial $k$-vector.

The framework's claim is that this row is the *only* one that can
satisfy A=1 when an electron lock-in happens — that splitting amplitude
between $e'$ and $\gamma$ is the unique outcome consistent with the
constraint. The tag table makes the claim falsifiable: any candidate
emission operation must balance every column.

### Pair annihilation (theoretical)

$$\{e, p\}\ [A = 1, 1]\ \longrightarrow\ \{\gamma_1, \gamma_2\}\ [A = 1, 1].$$

- `A_joint`: $2 = 1 + 1$. ✓
- `N`: $2 \to 2$ (different sessions, but count preserved here).
- `χ`: must sum to zero across the photon pair.
- `p`: must balance to the original CoM momentum.

If `χ` cannot be balanced — e.g. two photons can't carry the chirality
charge of the original $e + p$ — then the row is forbidden. This is
where the algebra would *generate* the prediction "annihilation
requires $\geq 2$ photons" rather than postulate it.

---

## Open Questions

1. **Is `χ` actually a conserved tag?** The bipartite tick rule swaps
   R/L every tick, so single-session $\chi$ is not conserved tick-by-tick;
   but a *time-averaged* or *bundle-summed* $\chi$ might be. Need to
   check whether the kinetic hop's R↔L exchange has a conserved
   bilinear form. If it does, $\chi$ is a real charge. If not, drop
   the column.

2. **What is the conserved phase quantum?** Phase rotations $e^{-i\alpha}$
   preserve everything in the table, so phase itself is "free" in this
   accounting. But the Arnold-tongue lock-in is a statement about
   phase *windings* — integer ratios $\omega_e R_1 = p\pi/q$. The
   right tag is probably the winding number $(p, q)$, conserved across
   tick blocks of length $q$. This is the place where the algebra
   would touch the lock-in mechanism.

3. **Does row 9 (session creation) need a sourced amplitude?** The
   table says `A_joint = ✓` because the new photon's amplitude comes
   from the electron's. But if amplitude is *budget-limited* — total
   $A_\text{universe}$ across all sessions in all bundles — then row 9
   is constrained globally, not just per-bundle. The framework's
   stance on this is unclear; CLAUDE.md treats A=1 per-session, the
   notes treat A=1 as the single conservation law. The table forces
   the question.

4. **Does the algebra forbid anything that QM allows?** This is the
   earn-your-keep test. If every row balanceable here is also balanceable
   by standard QM selection rules, the algebra is bookkeeping with
   extra steps. Candidate falsifier: a transition that QM allows on
   energy/angular-momentum/parity grounds but the lattice forbids
   because no $\pi$- or $\chi$-balanced row exists.

---

## How to Use

To analyse a proposed operation:

1. Write it as a map on $\{\psi_i\}_{i=1}^N$.
2. For each tag column, compute the change.
3. If any column has a change inconsistent with its conservation rule
   (`=` should be 0, `↻` should be predictable, `→` should sum to zero),
   the operation is unbalanced.
4. An unbalanced operation either (a) needs a partner operation in the
   same tick to balance it, (b) is a violation of the framework, or
   (c) reveals that the conservation rule itself is wrong.

`exp_19c`'s row 2 + row 5 combination fails (1) because the drain
doesn't preserve `A_joint` and `enforce_unity_spinor` doesn't restore
the missing amplitude — it just sets each session to 1 independently,
hiding the violation.

The corrected operation (row 6) preserves `A_joint` by construction
and does not need `enforce_unity_spinor` to "fix" anything.
