<!-- markdownlint-disable MD022 MD024 MD032 MD047 MD060 -->
# Memo: Frame Condition and Isotropy — RESOLVED

**Date:** 2026-04-26 (opened) / 2026-04-27 (resolved)
**Status:** Closed. Verdict: **possibility 3 with sharper structure.** The lattice is birefringent with optical axis along $\mathbf{V}_1+\mathbf{V}_2+\mathbf{V}_3 = (1,1,-1)$.
**Trigger:** Reviewer critique asked for explicit Taylor-expansion details
for the 1/r² recovery and the frame-condition proof. Started preparing a
SymPy-driven appendix; surfaced a correctness issue instead.

## TL;DR

The **frame condition** as stated in the paper

$$
\sum_{\mathbf{v}\in\text{RGB}} \mathbf{v}\mathbf{v}^T = 3\,\mathbb{I}_{3\times 3}
$$

(asserted in the abstract, conclusion, and parts of §6) is **mathematically
false** for the basis vectors used in the paper. The off-diagonal entries
are not zero. §6 itself acknowledges this in lines 217–228, then
contradicts that acknowledgement on line 247. The abstract and
conclusion still carry the wrong form.

A first attempt at recovering isotropy via the bipartite (two-tick)
propagator does **not** make the off-diagonal cross terms vanish either.
Either the dispersion's eigenvalues do (untested), the
`enforce_unity_spinor` renormalisation does, or isotropy emerges only by
the $O_h$ symmetry-averaging argument the paper already gives separately.

## What we verified with SymPy

### 1. The frame matrix is not diagonal

For the basis $\mathbf{V}_1=(1,1,1)$, $\mathbf{V}_2=(1,-1,-1)$,
$\mathbf{V}_3=(-1,1,-1)$:

$$
M_\text{RGB} = \sum_{\mathbf{v}\in\text{RGB}} \mathbf{v}\mathbf{v}^T
= \begin{pmatrix} 3 & -1 & 1 \\ -1 & 3 & 1 \\ 1 & 1 & 3 \end{pmatrix}
$$

This is what the paper writes correctly in
[emergent_kinematics.tex:217–222](../paper/sections/emergent_kinematics.tex#L217).

Including CMY $= -$RGB simply doubles every entry:

$$
M_\text{ALL} = 2\,M_\text{RGB}
= \begin{pmatrix} 6 & -2 & 2 \\ -2 & 6 & 2 \\ 2 & 2 & 6 \end{pmatrix}
$$

Off-diagonals nonzero in both cases. **Neither sublattice nor the union
satisfies the asserted frame condition.**

### 2. The bipartite two-tick trace is also anisotropic at O(k²)

Using the Fourier-space half-tick matrices

$$
T_\text{even}(\mathbf{k}) =
\begin{pmatrix} i\sin(\omega/2) & \cos(\omega/2)\,H_\text{RGB}(\mathbf{k}) \\
0 & 1 \end{pmatrix},\qquad
T_\text{odd}(\mathbf{k}) =
\begin{pmatrix} 1 & 0 \\
\cos(\omega/2)\,H_\text{CMY}(\mathbf{k}) & i\sin(\omega/2) \end{pmatrix}
$$

with $H_\text{RGB}(\mathbf{k}) = \tfrac{1}{3}\sum_\text{RGB} e^{i\mathbf{k}\cdot\mathbf{v}}$
and $H_\text{CMY}(\mathbf{k}) = \overline{H_\text{RGB}(\mathbf{k})}$,
the full-cycle propagator is $T_\text{cycle} = T_\text{odd}\,T_\text{even}$.

Expanded around $\mathbf{k}=0$ to $O(k^2)$:

$$
\text{tr}\,T_\text{cycle} \approx
\cos^2\!\bigl(\tfrac{\omega}{2}\bigr) + 2i\sin\!\bigl(\tfrac{\omega}{2}\bigr)
-\tfrac{8\cos^2(\omega/2)}{9}\bigl(k_1^2+k_2^2+k_3^2\bigr)
-\tfrac{8\cos^2(\omega/2)}{9}\bigl(-k_1 k_2 + k_1 k_3 + k_2 k_3\bigr)
+ O(k^3)
$$

Diagonal coefficients: all $-8\cos^2(\omega/2)/9$ ✓ (isotropic part).
Off-diagonals: $\{+1,-1,-1\}\cdot 8\cos^2(\omega/2)/9$ ✗ (not zero, not
even all the same sign).

### 3. The cycle propagator is not unitary by itself

$$
\det T_\text{cycle} = -\sin^2(\omega/2)
$$

Not $\pm 1$. Unitarity (and therefore $\mathcal{A}=1$) is restored not by
the linear operator but by `enforce_unity_spinor` applied **after** each
tick. This means the standard dispersion-from-trace analysis is not the
final word — the renormalisation projection sits between consecutive
applications of $T_\text{cycle}$ and could change the effective dispersion
in the continuum limit.

## Where the issue lives in the paper

- **Abstract** ([abstract.tex:18–19](../paper/sections/abstract.tex#L18))
  — states $\sum_\text{RGB}\mathbf{v}_i\mathbf{v}_j^T = 3\delta_{ij}$
  outright. This is the cleanest "wrong sentence" in the paper as it stands.

- **Conclusion** ([conclusion.tex:25–27](../paper/sections/conclusion.tex#L25))
  — same form, in the bullet for the Dirac equation.

- **§6 emergent_kinematics.tex:217–248**
  — Internally inconsistent. Lines 217–222 give the correct $M$ matrix;
  lines 226–228 add a `% NOTE` admitting the earlier draft was wrong; but
  line 247 then says "the frame condition $M_{ij} = 3\delta_{ij}$
  eliminates all off-diagonal contributions," contradicting the matrix
  three pages earlier. The note was added but the consequences weren't
  followed through.

- **§7 gravity_as_clock_density.tex:132–134**
  — The 1/r² derivation invokes "the frame condition
  $\sum_\mathbf{v} v_i v_j = 6\delta_{ij}$ (the same identity used in
  the Dirac derivation)" to get the gradient and Laplacian.
  Same issue — that identity does not hold for the chosen vectors.

## RESOLVED (2026-04-27): the eigenvalue check

The 2026-04-26 memo identified three possibilities. The cheap eigenvalue test on the **single-tick** propagator (corrected from the earlier two-half-tick formulation; per `CausalSession.tick()`, massive-particle update is simultaneous) was run with SymPy. The closed-form result:

The propagator
$$
T(\mathbf{k}) = \begin{pmatrix} i\sin(\omega/2) & \cos(\omega/2)\,H_\text{RGB}(\mathbf{k}) \\ \cos(\omega/2)\,H_\text{CMY}(\mathbf{k}) & i\sin(\omega/2) \end{pmatrix}
$$
has $\text{tr}\,T = 2i\sin(\omega/2)$ (k-independent) and eigenvalues
$$
\lambda_\pm(\mathbf{k}) = i\sin(\omega/2) \pm \cos(\omega/2)\,|H_\text{RGB}(\mathbf{k})|.
$$
The k-dependence enters entirely through $|H_\text{RGB}|^2$:
$$
|H_\text{RGB}(\mathbf{k})|^2 = 1 - \mathbf{k}^T M_\text{eff}\,\mathbf{k} + O(k^4),
$$
with
$$
M_\text{eff} = -\tfrac{4}{9}\,\mathbb{I} + \tfrac{4}{9}\,M
\quad=\quad
\tfrac{1}{9}\begin{pmatrix} 8 & -4 & 4 \\ -4 & 8 & 4 \\ 4 & 4 & 8 \end{pmatrix},
$$
where $M = \sum_{\text{RGB}}\mathbf{v}\mathbf{v}^T$ is the original frame matrix.

**Eigenvalues of $M_\text{eff}$: $\{4/3,\,4/3,\,0\}$.**

The zero eigenvalue lies along $\mathbf{V}_1+\mathbf{V}_2+\mathbf{V}_3 = (1,1,-1)$ — the same direction as $M$'s small eigenvalue (1) and the long axis of the frame ellipsoid.

Verified by direct calculation: setting $\mathbf{k} = s(1,1,-1)/\sqrt{3}$ gives $\mathbf{k}\cdot\mathbf{V}_1 = \mathbf{k}\cdot\mathbf{V}_2 = \mathbf{k}\cdot\mathbf{V}_3 = s/\sqrt{3}$, so $H_\text{RGB} = e^{is/\sqrt{3}}$ and $|H_\text{RGB}|^2 = 1$ **exactly, at all orders in k.** The flat direction is genuine, not a leading-order artifact.

## Verdict

- **Possibility 1 (eigenvalue isotropy): FALSE.** $|\lambda_\pm|^2$ depends on $\mathbf{k}^T M_\text{eff}\,\mathbf{k}$ with $M_\text{eff}$'s eigenvalues $\{4/3, 4/3, 0\}$. Not a function of $|\mathbf{k}|^2$ alone.
- **Possibility 2 (renormalization restores isotropy): NOT YET TESTED, BUT THE CASE IS NOW STRONGER.** The flat direction is exact at all orders, not just leading order. For renormalization to "restore isotropy" it would have to produce direction-dependent corrections that exactly cancel the leading-order anisotropy in some directions and produce an entirely new dispersion in the flat direction. Possible in principle, but requires a careful perturbation theory of the projection $|\psi_R|^2 + |\psi_L|^2 \to 1$ between consecutive ticks.
- **Possibility 3 (genuine anisotropy): CORRECT, with sharper structure than originally framed.** The lattice has $O_h$ symmetry, not $\mathrm{SO}(3)$, at the operator level. The dispersion is **birefringent** — uniaxial, with optical axis along $(1,1,-1)$. Perpendicular plane: dispersion coefficient $4/3$. Along the axis: flat to all orders.

This is a **falsifiable, sharp, structural prediction** rather than a soft "isotropy fails" warning. See `notes/lattice_birefringence_prediction.md` for the prediction's standalone write-up.

## What the paper needs to do (revised)

1. **Drop the false claim** $\sum_\text{RGB}\mathbf{v}_i\mathbf{v}_j^T = 3\delta_{ij}$ from:
   - [abstract.tex:18-19](../paper/sections/abstract.tex#L18)
   - [conclusion.tex:25-27](../paper/sections/conclusion.tex#L25)
   - [emergent_kinematics.tex:247](../paper/sections/emergent_kinematics.tex#L247) (the line that contradicts the matrix three pages earlier)
   - [gravity_as_clock_density.tex:132-134](../paper/sections/gravity_as_clock_density.tex#L132)

2. **Replace with** the correct frame matrix (eigenvalues $\{4,4,1\}$) and the derived dispersion structure (eigenvalues of $M_\text{eff}$: $\{4/3, 4/3, 0\}$). The corresponding figure ([figures/frame_matrix_ellipsoid.png](../figures/frame_matrix_ellipsoid.png)) makes this geometrically explicit.

3. **Rewrite the rotational-invariance argument** in §6. $\mathrm{SO}(3)$ does *not* emerge at the operator level. Choices:
   - **(a) Honest crystallographic framing.** The lattice has $O_h$ symmetry, dispersion is birefringent with optical axis $(1,1,-1)$. $\mathrm{SO}(3)$ is recovered only on $O_h$-averaged observables. This is the cleanest and most defensible.
   - **(b) Renormalization-restored framing.** Argue (or compute) that `enforce_unity_spinor` cancels the anisotropy. Requires possibility (2) to be settled in the affirmative, which is currently unproven.
   - Recommend (a). It's stronger, not weaker — birefringence is a sharp prediction, and the paper gains one rather than losing one.

4. **Add the birefringence prediction** as a refinement of P7 in [predictions.tex](../paper/sections/predictions.tex). Direction-dependent photon group velocity, optical axis $(1,1,-1)$. The current GRB bound $a \lesssim 10^{-19}$ m is consistent with this; a direction-resolved test would be a sharper bound.

5. **Reframe §7's 1/r² derivation.** The $\nabla^2$ in the Laplacian no longer comes from a (false) diagonal $M$. It comes from the *trace* of $M_\text{eff}$ (which is $8/3$, finite) under $O_h$ averaging — the same logical move as in §6 but now made explicitly. Discrete-correction terms (P1) acquire direction dependence with the same optical axis structure.

## Action item still open

Test possibility (2) **numerically**: run a small free-particle simulation on a $33^3$ grid, measure $E(\mathbf{k})$ along several directions including $(1,1,-1)$, see whether the directional dependence persists or is washed out by `enforce_unity_spinor`. If anisotropy persists, the paper rewrite under choice (a) is forced. If isotropy is restored, choice (b) becomes available with numerical justification.

This is a one-day implementation effort and would close the last loose end.

## Reproducer snippet

The SymPy verification of the frame matrix:

```python
import sympy as sp
V1 = sp.Matrix([1,  1,  1])
V2 = sp.Matrix([1, -1, -1])
V3 = sp.Matrix([-1, 1, -1])
RGB = [V1, V2, V3]
M = sum(v * v.T for v in RGB)
print(M.tolist())                  # [[3, -1, 1], [-1, 3, 1], [1, 1, 3]]
print(M.equals(3 * sp.eye(3)))     # False
```

The two-tick trace expansion lives in the conversation transcript; if we
turn this into a real investigation we should drop it as a script in
`src/utilities/derive_continuum_limits.py` so it's reproducible.

## Why this matters

A serious referee will run the 5-line SymPy check above. If they find
the frame condition is false, the paper's central isotropy claim is
read as either careless or incorrect. Best case: we catch and fix it
before submission with a strengthened argument (eigenvalue-based or
$O_h$-symmetry-based). Worst case: we discover the lattice does have
genuine anisotropy at O(k²) and we have to re-frame the Lorentz
invariance claim more carefully (still defensible, but a different
story).

Either way: do not ship v1.0 with the current abstract/conclusion
sentences in their present form.
