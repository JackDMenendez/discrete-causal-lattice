# Deriving Dirac — Why It Matters

*Conversation note, 2026-03-30.*

---

Dirac didn't derive his equation. He constructed it.

He knew what properties it had to have — first order in space and time, Lorentz covariant, reducing to the Schrödinger equation in the non-relativistic limit — and he invented the mathematical objects (the gamma matrices, the four-component spinor) that satisfy those requirements. It was a remarkable feat of reverse engineering. But the gamma matrices arrived as algebraic necessities, not as things with a geometric meaning. Nobody asked what they *were*, because the construction worked.

The lattice inverts this. The bipartite RGB/CMY structure is geometrically obvious — it is just two interpenetrating sublattices with antiparallel basis vectors. The two-component spinor (psi_R, psi_L) is not a mathematical invention; it is amplitude on the two sublattices. The gamma matrix structure emerges from the Taylor expansion of the tick rule, and the Clifford algebra holds because the RGB vectors form a tight frame — a geometric condition, not an algebraic postulate.

The significance: **if the continuum limit derivation goes through, the Dirac equation stops being a postulate and becomes a theorem**. Not "our model is consistent with the Dirac equation" — the Dirac equation is what you get when you take the continuum limit of amplitude conservation on a bipartite lattice. The question "why does the Dirac equation describe spin-1/2 particles?" then has an answer: because spin-1/2 particles live on bipartite lattices, and the Dirac equation is the continuum description of that bipartite structure.

This also resolves the longstanding puzzle of why the Dirac equation is first-order in both space and time. It's first-order in space because the hop is first-order in the lattice spacing. It's first-order in time because one tick is one update. The mathematical property that Dirac needed to impose as a constraint falls out of the geometry automatically.

The one remaining step — symmetry averaging over the octahedral group O_h to recover full rotational invariance — is standard lattice field theory. It is not a conjecture. The same step is taken in lattice QCD, and the procedure is well understood. It needs to be written out explicitly, but it is not an open question.

The derivation exists as a working document in `notes/deriving_dirac_from_hamiltonian.md`. The paper-quality writeup should go in `emergent_kinematics.tex` as a new subsection following the momentum and force derivations, closing the section by showing that the entire kinematic structure — momentum, inertia, force, and the Dirac equation itself — all follow from the single bipartite tick rule and A=1.

That is what "Geometry First" means in the title.
