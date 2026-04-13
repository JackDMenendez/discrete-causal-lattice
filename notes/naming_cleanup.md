# Naming Cleanup — Physics Language vs Programming Language

The current naming mixes physics and software engineering terminology.
The goal is that every name in both the paper and the code should sound
like it belongs in a physics journal, not a software architecture document.

This note catalogs everything that needs changing, with proposed replacements
and the scope of each change (code, paper, or both).

---

## The Central Problem: "session" and "scheduler"

These two words carry the problem almost entirely.

**"session"** is a networking/OS term: a stateful connection between a client
and server, or a user login period.  A particle is not a session.
A particle is a mode, a carrier, an excitation, a state.

**"scheduler"** is an OS term: the kernel subsystem that decides which process
runs next.  The multi-body evolution is not a scheduler.
It is an ensemble, a propagator, a dynamics operator.

Both words import a mental model from computer science that actively misleads
readers about the physics.  "Session creation" sounds like opening a socket.
"Particle creation" is the correct QFT term.

---

## Proposed Replacement: "causal mode"

A particle in this framework is a **causal mode**: a resonant, persistent
probability flux on the lattice that is confined to the causal cone.
"Mode" is standard field-theory language (normal mode, Fourier mode,
vacuum mode).  "Causal" qualifies it as obeying the local propagation
constraint.  Together the term has no programming connotation.

Alternative if "mode" feels too field-theoretic: **"causal state"** or
**"causal carrier"**.  The key point is to drop "session" entirely.

---

## Class Renames (src/core/)

| Current name | Proposed name | Physics rationale |
| --- | --- | --- |
| `CausalSession` | `CausalMode` | A particle is a resonant mode, not a session |
| `CompositeCausalSession` | `BoundState` | Standard QM/QFT term for a composite particle |
| `TickScheduler` | `Ensemble` | A collection of causal modes evolving together; "ensemble" is standard statistical physics |
| `PhaseOscillator` | (keep) | "Oscillator" is physics; U(1) phase oscillator is precise |
| `OctahedralLattice` | (keep) | "Lattice" is physics; the geometry name is accurate |
| `UnityConstraint` (module) | `ProbabilityConservation` | The module implements a conservation law, not a constraint |

`ShuffleScheme` (enum inside `TickScheduler`) → `TickOrdering` or `PropagationOrder`
once `TickScheduler` is renamed.

---

## Method and Property Renames (src/core/)

### CausalSession (→ CausalMode)

| Current | Proposed | Rationale |
| --- | --- | --- |
| `tick()` | `step()` | "Step" is standard in MD, MCMC, lattice QCD; "tick" sounds like a game loop |
| `advance_tick_counter()` | `advance_time()` | "tick counter" is code; "time" is physics |
| `tick_counter` | `time_step` | Same — counter is a software concept |
| `tick_parity` | `sublattice_parity` | The physical meaning is which sublattice is active, not which "tick" we are on |

### TickScheduler (→ Ensemble)

| Current | Proposed | Rationale |
| --- | --- | --- |
| `register(session)` | `add(mode)` or `add_particle(mode)` | Particles are added to an ensemble, not registered |
| `bind_sessions()` | `couple()` or `bind_particles()` | "Sessions" gone; coupling is physics language |
| `advance()` | (keep) | "Advance the ensemble" is natural physics language |

### UnityConstraint (→ ProbabilityConservation)

| Current | Proposed | Rationale |
| --- | --- | --- |
| `enforce_unity_spinor()` | `conserve(psi_R, psi_L)` | "Enforce" is code; "conserve probability" names the physics |
| `enforce_joint_unity()` | `conserve_joint(psi_R, psi_L)` | Same |
| `is_unity()` | `is_conserved()` | "Unity" is mathematical; "conserved" names the physical property |
| `unity_residual()` | `conservation_residual()` | Same |

---

## Paper Terminology (paper/sections/)

These are recurring phrases in the .tex files that need global replacement.

| Current phrase | Proposed replacement | Scope |
| --- | --- | --- |
| "causal session" | "causal mode" | All .tex files (~93 occurrences) |
| "session creation" | "particle creation" | Standard QFT term |
| "session density" | "particle density" | Standard physics term |
| "live proton session" | "dynamical proton" or "active proton" | No programming connotation |
| "the session's state" | "the particle's state" | |
| "tick rule" | "propagation rule" or "lattice step rule" | "Rule" is fine; "tick" is borderline |
| "tick counter" | "time step" or "internal clock count" | |
| "macro-tick" | "global time step" or "composite step" | |
| "scheduler queue" (clock_fluid_dynamics.tex) | "clock density" or "causal event density" | The queue analogy may be worth keeping as a metaphor but not as primary language |
| "computational deadlock" (tick_scheduler.tex stub) | "causal horizon" | Maps correctly to physics |
| "scheduler load" (tick_scheduler.tex stub) | "clock density" | Already the correct physics term used elsewhere |

---

## Section File Renames (paper/sections/)

| Current filename | Proposed filename | Section title |
| --- | --- | --- |
| `causal_sessions.tex` | `causal_modes.tex` | "Causal Modes and the Phase Oscillator" |
| `tick_scheduler.tex` | `many_body_dynamics.tex` | "Many-Body Dynamics and the Arrow of Time" |

The content of `tick_scheduler.tex` (currently a stub) maps to physics topics
(independent clocks, irreversibility, gravitational time dilation, event horizon
as causal saturation) that all sound natural once "scheduler" is removed.

---

## Notes Files (notes/)

Notes are working documents and do not need the same rigor as the paper,
but the following files use "session" as a primary concept and should be
updated when the paper terminology is fixed, to avoid confusion:

- `two_session_bound_state.md` → `two_particle_bound_state.md`
- `photon_emission_from_A1.md` — contains "session creation" throughout
- `conservation_of_probability.md` — contains "session types"
- `cone_interference_and_particle_zoo.md` — "session types" as particle zoo
- `material_cone_and_composites.md` — references CompositeCausalSession directly
- `orbit_stability_and_dissipation.md` — "sessions" throughout
- All notes under `follow_on_implications.md` use "session" as primary vocabulary

---

## What Is NOT a Problem

- `tick` as the **unit of time** (analogous to "lattice spacing" as unit of length)
  is fine when it appears as a unit: "propagates at 1 node/tick", "energy in
  units of ticks⁻¹".  The problem is `tick()` as a method name and "tick counter"
  as a variable name — those sound like game-loop code.

- `OctahedralLattice`, `PhaseOscillator`, `A=1`, all notation in the math.

- Any use of "session" in the context of *explaining the old name* during
  a transition period.

---

## Execution Order

1. Rename the four classes in `src/core/` and update `src/core/__init__.py`
2. Update all experiment files (`src/experiments/`) — they import these classes
3. Update all utility files (`src/utilities/`) — same
4. Update all test files (`tests/`) — same
5. Rename the module file `UnityConstraint.py` → `ProbabilityConservation.py`
6. Global search-and-replace "causal session" → "causal mode" in `paper/sections/`
7. Global replace the other paper phrases in the table above
8. Rename `causal_sessions.tex` and `tick_scheduler.tex`
9. Update `\input{}` references in `paper/main.tex`
10. Update CLAUDE.md and EXPERIMENTS.md references
11. Update notes files

Steps 1–5 together are a significant refactor.  Steps 6–11 are text replacements.
Both are mechanical once the decision on replacement names is confirmed.
