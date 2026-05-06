"""
automorphism_direct_product.py

Step 5 sub-step: verify the direct-product structure of the
conjecture by computing pairwise commutators of the proposed
generators on the per-site amplitude space C^2 = (psi_R, psi_L).

The conjecture (notes/lie_algebra_automorphism_proof_sketch.md):

    Aut(T_diamond, A=1) = SO(3,1) x SU(3) x SU(2) x U(1)

For this to be a direct product, the four factors must commute
pairwise as Lie subalgebras of the full Aut.  Equivalently:

  [so(3,1), su(2)] = 0   in the framework's automorphism algebra
  [so(3,1), u(1)] = 0
  [su(2), u(1)] = 0
  [so(3,1), su(3)] = 0   (with SU(3) requiring a structural addition)
  [su(2), su(3)] = 0
  [u(1), su(3)] = 0

This script focuses on the established factors (SO(3,1), SU(2),
U(1)) all acting on the same per-site C^2 amplitude (psi_R, psi_L).
SU(3) is excluded: it requires a per-site C^3 internal extension
(see automorphism_rgb_su3.py) that is not yet in the framework, so
its commutators with the existing factors are trivially zero on the
extended structure but cannot be verified on the existing C^2.

Generators on C^2 = (psi_R, psi_L):

  Lorentz rotations:  J_a = (1/2) sigma_a  (Hermitian; same as SU(2))
  Lorentz boosts:     K_a = (i/2) sigma_a  (anti-Hermitian)
  Per-site SU(2):     T_a = (1/2) sigma_a  (Hermitian)
  Per-site U(1):      Q   = (i) I          (anti-Hermitian)

The deliverable: explicitly compute pairwise commutators and
identify whether the per-site SU(2) is genuinely a direct factor
or coincides with the Lorentz rotation subgroup.

Expected finding: T_a = J_a as matrices.  The "per-site SU(2)" of
the conjecture (acting on (psi_R, psi_L) by 2x2 unitary matrices) is
NOT independent of SO(3,1) -- it IS the Lorentz rotation subgroup.
Therefore the conjecture's "SO(3,1) x SU(2)" is structurally wrong:
the two factors overlap in SU(2)-rotation, so they are not in direct
product as written.

This parallels the SU(3) finding: standard-model SU(2)_W is a
separate gauge symmetry on a per-site isospin doublet, requiring
the framework to be extended with an additional per-site C^2
internal index (analogous to the per-site C^3 colour index for
SU(3)).  Without this extension, the framework's existing structure
gives only SO(3,1) x U(1) (dim 7).
"""

import itertools
import numpy as np
import sympy as sp
from sympy import I, Matrix, eye, sqrt, simplify, Rational


def pauli_matrices():
    """The three Pauli matrices."""
    sigma_x = Matrix([[0, 1], [1, 0]])
    sigma_y = Matrix([[0, -I], [I, 0]])
    sigma_z = Matrix([[1, 0], [0, -1]])
    return [sigma_x, sigma_y, sigma_z]


def lorentz_generators():
    """Rotation and boost generators of so(3,1) on a 2-component Weyl
    spinor.  Standard convention:
       J_a = (1/2) sigma_a  (rotations: Hermitian)
       K_a = (i/2) sigma_a  (boosts: anti-Hermitian, in this rep)
    """
    sigma = pauli_matrices()
    J = [Rational(1, 2) * s for s in sigma]
    K = [Rational(1, 2) * I * s for s in sigma]
    return J, K


def su2_internal_generators():
    """Per-site SU(2) generators on (psi_R, psi_L) per the proof
    sketch's identification: T_a = (1/2) sigma_a."""
    sigma = pauli_matrices()
    return [Rational(1, 2) * s for s in sigma]


def u1_internal_generator():
    """Per-site U(1) phase rotation generator: Q = i * I."""
    return I * eye(2)


def commutator(A, B):
    """Lie bracket [A, B] = A B - B A."""
    return simplify(A @ B - B @ A)


def is_zero(M):
    """Whether a matrix is identically zero."""
    return all(simplify(e) == 0 for e in M)


def report():
    print("=" * 70)
    print("Direct-product structure check on per-site C^2 = (psi_R, psi_L)")
    print("=" * 70)
    print()

    J, K = lorentz_generators()
    T = su2_internal_generators()
    Q = u1_internal_generator()

    print("Generators (acting on the C^2 = (psi_R, psi_L) at each site):")
    print()
    print("  Lorentz rotations J_a = (1/2) sigma_a:")
    for a, M in enumerate(J):
        print(f"    J_{a+1} ="); sp.pprint(M); print()

    print("  Lorentz boosts K_a = (i/2) sigma_a:")
    for a, M in enumerate(K):
        print(f"    K_{a+1} ="); sp.pprint(M); print()

    print("  Per-site SU(2) T_a = (1/2) sigma_a (proof sketch):")
    for a, M in enumerate(T):
        print(f"    T_{a+1} ="); sp.pprint(M); print()

    print("  Per-site U(1) Q = i * I:")
    sp.pprint(Q); print()

    # ── Step 1: compare J_a and T_a directly ─────────────────────────────
    print("-" * 70)
    print("Step 1: are the per-site SU(2) generators T_a")
    print("        the same as the Lorentz rotation generators J_a?")
    print("-" * 70)
    print()
    same = all(simplify(J[a] - T[a]) == sp.zeros(2, 2) for a in range(3))
    print(f"  T_1 = J_1?  {simplify(J[0] - T[0]) == sp.zeros(2, 2)}")
    print(f"  T_2 = J_2?  {simplify(J[1] - T[1]) == sp.zeros(2, 2)}")
    print(f"  T_3 = J_3?  {simplify(J[2] - T[2]) == sp.zeros(2, 2)}")
    print()
    if same:
        print("  >>> The per-site SU(2) generators are LITERALLY the same")
        print("      matrices as the Lorentz rotation generators J_a.")
        print("      Per-site SU(2) is NOT a separate factor on C^2 -- ")
        print("      it IS the Lorentz rotation subgroup.")
    print()

    # ── Step 2: verify the Lorentz algebra so(3,1) ───────────────────────
    print("-" * 70)
    print("Step 2: verify so(3,1) commutation relations")
    print("-" * 70)
    print()
    print("  [J_a, J_b] = i epsilon_abc J_c  (rotations close into rotations)")
    eps = lambda a, b, c: 1 if (a, b, c) in [(0, 1, 2), (1, 2, 0), (2, 0, 1)] \
        else -1 if (a, b, c) in [(0, 2, 1), (2, 1, 0), (1, 0, 2)] else 0
    for a, b in itertools.combinations(range(3), 2):
        c_expected = [c for c in range(3) if c != a and c != b][0]
        sign = eps(a, b, c_expected)
        lhs = commutator(J[a], J[b])
        rhs = I * sign * J[c_expected]
        match = simplify(lhs - rhs) == sp.zeros(2, 2)
        print(f"    [J_{a+1}, J_{b+1}] = i*({sign})*J_{c_expected+1}: {match}")
    print()

    print("  [K_a, K_b] = -i epsilon_abc J_c  (boosts close into rotations)")
    for a, b in itertools.combinations(range(3), 2):
        c_expected = [c for c in range(3) if c != a and c != b][0]
        sign = eps(a, b, c_expected)
        lhs = commutator(K[a], K[b])
        rhs = -I * sign * J[c_expected]
        match = simplify(lhs - rhs) == sp.zeros(2, 2)
        print(f"    [K_{a+1}, K_{b+1}] = -i*({sign})*J_{c_expected+1}: {match}")
    print()

    print("  [J_a, K_b] = i epsilon_abc K_c  (rotations rotate boosts)")
    for a in range(3):
        for b in range(3):
            if a == b:
                lhs = commutator(J[a], K[b])
                z = is_zero(lhs)
                print(f"    [J_{a+1}, K_{b+1}] = 0?  {z}")
            else:
                c_expected = [c for c in range(3) if c != a and c != b][0]
                sign = eps(a, b, c_expected)
                lhs = commutator(J[a], K[b])
                rhs = I * sign * K[c_expected]
                match = simplify(lhs - rhs) == sp.zeros(2, 2)
                print(f"    [J_{a+1}, K_{b+1}] = i*({sign})*K_{c_expected+1}: "
                      f"{match}")
    print()

    # ── Step 3: per-site SU(2) and U(1) commutators ──────────────────────
    print("-" * 70)
    print("Step 3: U(1) phase commutators with SO(3,1) and SU(2)")
    print("-" * 70)
    print()
    print("  U(1) generator Q = i*I commutes with everything (it's central):")
    for a in range(3):
        print(f"    [Q, J_{a+1}] = 0?  {is_zero(commutator(Q, J[a]))}")
    for a in range(3):
        print(f"    [Q, K_{a+1}] = 0?  {is_zero(commutator(Q, K[a]))}")
    print()

    # ── Step 4: structural conclusion ────────────────────────────────────
    print("-" * 70)
    print("Step 4: structural conclusion")
    print("-" * 70)
    print()
    print("On the per-site C^2 = (psi_R, psi_L):")
    print()
    print("  Lorentz so(3,1):  6 generators (3 rotations + 3 boosts).")
    print("    Closed Lie algebra; closes back into itself under [.,.].")
    print()
    print("  Per-site SU(2):   3 generators T_a = J_a.")
    print("    These are the SAME matrices as the Lorentz rotation")
    print("    generators.  As subgroups of GL(2, C), per-site SU(2)")
    print("    is the rotation subgroup of Lorentz, NOT a separate factor.")
    print()
    print("  Per-site U(1):    1 generator Q = i*I.")
    print("    Commutes with everything; central in U(2).")
    print("    Genuine direct factor.")
    print()
    print("Implication for the conjecture:")
    print()
    print("  The proof sketch claimed SO(3,1) x SU(2) x U(1) acts on the")
    print("  framework's existing C^2 as a direct product (dim 6+3+1=10).")
    print("  This is structurally wrong: per-site SU(2) and SO(3,1)")
    print("  overlap exactly in the rotation subgroup, so the direct-")
    print("  product decomposition double-counts the rotations.")
    print()
    print("  Corrected statement: the framework's existing per-site C^2")
    print("  amplitude carries the action of SO(3,1) x U(1) only (dim 7),")
    print("  with the SU(2)_rotation being a subgroup of SO(3,1) and not")
    print("  an independent factor.")
    print()
    print("  For the Standard Model conjecture (SO(3,1) x SU(3) x SU(2)_W")
    print("  x U(1)_Y), both SU(3) and SU(2)_W require structural additions")
    print("  to the framework -- per-site internal C^3 (colour) and C^2")
    print("  (weak isospin) indices respectively.  Neither is a direct")
    print("  continuation of the existing framework structure.")
    print()
    print("  This puts the Standard Model derivation status at:")
    print("  - Established:  SO(3,1) (6) + U(1) (1) = 7 dim")
    print("  - Open (need extensions):  SU(3) (8) + SU(2)_W (3) = 11 dim")
    print("  - Total conjecture:  18 dim")


if __name__ == '__main__':
    report()
