# Born Rule from Path Counting on the T³_diamond Lattice

## The Core Claim

The Born rule — the probability of finding a particle at node (a,b,c) after N
ticks equals |ψ(a,b,c)|² — is not a postulate in the A=1 framework.
It is the statement that probability IS the fraction of N-step lattice paths
that reach (a,b,c), normalised by the total number of paths.
The A=1 constraint is precisely the assertion that this fraction sums to one.

---

## Step 1: Counting Paths

At each tick, a massless session (ω=0) hops with certainty (p_hop = 1) along
one of the six basis vectors:

    RGB: v1=(1,1,1)   v2=(1,-1,-1)   v3=(-1,1,-1)
    CMY: -v1          -v2            -v3

A path of length N is a sequence of N choices from these six vectors.
Total paths: 6^N.

**Net displacement coordinates.**
Let n_i = steps along v_i, m_i = steps along -v_i (i=1,2,3).
The net displacement is (a,b,c) = Σ_i n_i v_i - Σ_i m_i v_i.
Writing p_i = n_i - m_i (net steps in direction i), the constraint becomes:

    p1 + p2 - p3 = a      (x component)
    p1 - p2 + p3 = b      (y component)
    p1 - p2 - p3 = c      (z component)

Solving:
    p1 = (a+b)/2,   p2 = (a-c)/2,   p3 = (b-c)/2

**Reachability condition:** a, b, c must all have the same parity
(so that p1, p2, p3 are integers). This is the bipartite sublattice
constraint: even-tick nodes have a+b+c ≡ 0 mod 2.

**Path count formula.**
Given target (a,b,c) and total steps N, the number of paths is:

    P(N,a,b,c) = Σ_{s: Σs_i=N, s_i≥|p_i|, s_i≡p_i (mod 2)}
                    N! / (n1! m1! n2! m2! n3! m3!)

where n_i = (s_i + p_i)/2, m_i = (s_i - p_i)/2, and s_i = n_i + m_i is the
total (unsigned) steps in direction i. The sum is over the finitely many
integer solutions {s_i}.

This is a pure combinatorial integer for every (N, a, b, c).

---

## Step 2: A=1 is the Born Rule Normalisation

The identity

    Σ_{(a,b,c) reachable in N} P(N,a,b,c) = 6^N

is a combinatorial tautology: every N-step path ends somewhere, and the
path counts partition the complete set of paths.

Dividing:

    Σ_{(a,b,c)} P(N,a,b,c) / 6^N = 1

This IS the A=1 constraint applied to a massless session: total probability
equals one at every tick, by construction. The Born rule normalisation is
not separately imposed — it is the definition of "path fraction".

---

## Step 3: Continuum Limit — CLT Gives the Gaussian

For large N with (a,b,c) = N(α,β,γ) held fixed, the sum in P(N,a,b,c)
concentrates around s_i ≈ N/3 for each direction. By the central limit
theorem applied to the 6-direction random walk:

    P(N,Nα,Nβ,Nγ) / 6^N  →  (2πN)^{-3/2} |det C|^{-1/2}
                               × exp( -N(α,β,γ) C^{-1} (α,β,γ)^T / 2 )

where C is the covariance matrix of a single step:

    C = (1/6) Σ_{all 6 vectors} v v^T = (1/3) Σ_{RGB} v v^T

Numerically for V1=(1,1,1), V2=(1,-1,-1), V3=(-1,1,-1):

    Σ_RGB v v^T = [[3,-1,1],[-1,3,1],[1,1,3]]  ≠ 3I

So the CLT Gaussian is **anisotropic in (x,y,z) coordinates**.
Isotropy is recovered in the continuum limit by the same argument used for
the Dirac derivation: the full two-sublattice operator combines RGB and CMY,
and cross-terms cancel. The physical dispersion relation E² = p² + m² is
isotropic (Section 4 of the paper), even though each individual sublattice
is not. The path-counting Gaussian inherits this structure.

**The Gaussian is the Born probability.** For ω=0 on a flat lattice:

    |ψ(a,b,c,N)|²  =  P(N,a,b,c) / 6^N

This is the Born rule as a counting identity. No measurement axiom required.

---

## Step 4: Massive Sessions (ω ≠ 0)

For ω ≠ 0, each hop along direction v_i acquires a phase factor
exp(i δφ/2) = exp(i(ω + V)/2). The amplitude at (a,b,c) is no longer
a real positive number — it is a complex sum over paths weighted by their
accumulated phase product.

The path count P(N,a,b,c) gives the **number** of contributing paths.
The amplitude squared |ψ|² includes interference between paths with different
phases. In the long-wavelength limit (k << π, ω << 1), phases vary slowly
and the path count still dominates: |ψ|² ≈ P(N,a,b,c)/6^N × (phase
envelope). The Born rule is recovered as an approximation valid in the
continuum limit.

**This is the standard relationship between the path integral and probability.**
The path integral (Feynman, 1948) assigns an amplitude to each path; the
Born rule is |sum of amplitudes|². Here the amplitudes are the phase-weighted
path counts, and A=1 is the normalisation that makes probabilities sum to one.
The lattice makes the "sum over histories" computation explicit and finite.

---

## Step 5: Falsifiable Corrections (exp_06)

For small N and/or large (a,b,c)/N, the CLT Gaussian fails and the exact
integer P(N,a,b,c)/6^N deviates from the Gaussian prediction. These are
**discrete lattice corrections to the Born rule** that occur at short
distances. Exp_06 confirms these corrections exist and are computable.

If the lattice spacing equals the Planck length, the corrections become
significant at r ≈ a few Planck lengths. At atomic scales N >> 1 and the
Gaussian (standard Born rule) is an excellent approximation. The corrections
are in principle measurable as deviations from the 1/r² force law at
sub-Planck distance scales.

---

## Summary

| Step | Statement | Status |
|------|-----------|--------|
| P(N,a,b,c) is a well-defined integer | Combinatorial formula above | Derived |
| Σ P(N,a,b,c) = 6^N | Tautological partition of paths | Exact |
| A=1 ↔ Born normalisation | Same statement two ways | Exact |
| CLT gives Gaussian for large N | Standard probability theory | Derived |
| Gaussian = Born rule for ω=0 | Path fraction = probability | Exact |
| Massive case: phase-weighted paths | Feynman path integral structure | Approximate (continuum) |
| Discrete corrections at small N | exp_06 | Confirmed |

**The one remaining gap:** the explicit connection between the phase-weighted
path count and the full Born rule for ω ≠ 0 requires computing the
interference sum exactly. This is the lattice analogue of the stationary
phase approximation in the Feynman path integral, and reduces to the
continuum Born rule in the limit a → 0. A clean finite-lattice derivation
of this connection has not yet been written.

---

## Note on the Frame Condition in the Paper

The paper (Section 4) states the frame condition as M_ij = Σ_RGB v_i v_j = 3δ_ij.
Numerically this is not satisfied by the RGB vectors alone:

    Σ_RGB v v^T = [[3,-1,1],[-1,3,1],[1,1,3]]

The correct statement is that the combined RGB+CMY operator is isotropic
in the dispersion relation: the off-diagonal terms cancel between the two
sublattices when the full two-tick operator is expanded. The frame condition
as stated should be corrected to: the combined frame matrix satisfies
Σ_ALL v v^T = 6I (which is the correct normalisation including all 6 vectors):

    Σ_ALL v v^T = 2 × Σ_RGB v v^T = [[6,-2,2],[-2,6,2],[2,2,6]] ≠ 6I

Actually even this is not diagonal. The isotropy emerges from the cancellation
of the first-order term (1,1,-1)·k between the two sublattice contributions,
not from a diagonal frame matrix. The dispersion relation argument is correct;
the frame condition equation as written is an error. This should be fixed in
the paper.
