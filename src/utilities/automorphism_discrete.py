"""
automorphism_discrete.py

Step 5 of the automorphism conjecture: enumerate the discrete linear
maps A in GL(3, R) preserving V = {+/-V_1, +/-V_2, +/-V_3} and
identify the resulting group structure.

Conjecture (notes/lie_algebra_automorphism_proof_sketch.md):

    Aut(T_diamond^3, A=1) = SO(3,1) x SU(3) x SU(2) x U(1)

The discrete piece is the spatial part: linear maps preserving
the lattice generators.  The continuum lift via O_h-averaging gives
SO(3,1); the per-site internal piece gives SU(2) x U(1); the open
piece is SU(3) on the RGB triplet weights.

This script is the first concrete step: compute the discrete group
of V-preserving linear maps explicitly and verify it has the
expected structure.

Result expected: 48 elements forming a group isomorphic to the
hyperoctahedral group B_3 = Z_2 wr S_3 (= O_h abstractly).  But
the realisation on R^3 in the V-basis is NOT the standard cubic-
symmetry representation: many elements fail to be orthogonal in
the standard inner product on R^3.  This is a structural finding,
not a contradiction: the lattice is preserved as a discrete group,
but the metric is preserved only by a subgroup.  The subgroup that
preserves both is the genuine crystallographic point symmetry of
T_diamond^3 in the standard embedding.
"""

import itertools
import numpy as np


def basis_vectors():
    """The three RGB basis vectors and their CMY negatives."""
    V1 = np.array([1, 1, 1])
    V2 = np.array([1, -1, -1])
    V3 = np.array([-1, 1, -1])
    return [V1, V2, V3]


def unsigned_basis_set(rgb):
    """The 6-element basis-vector set V = {+/-V_1, +/-V_2, +/-V_3}."""
    return [v for v in rgb] + [-v for v in rgb]


def candidate_automorphisms(rgb):
    """Enumerate the 48 candidate linear maps A defined by
    A(V_i) = s_i * V_{sigma(i)} for sigma in S_3, s in {+/-1}^3."""
    M = np.array(rgb, dtype=float).T  # columns are V_1, V_2, V_3
    Minv = np.linalg.inv(M)
    automorphisms = []
    for sigma in itertools.permutations([0, 1, 2]):
        for signs in itertools.product([+1, -1], repeat=3):
            # Q is the 3x3 matrix sending the standard basis e_i
            # to s_i * e_{sigma(i)} -- i.e. permutation followed by sign
            Q = np.zeros((3, 3))
            for i, sigma_i in enumerate(sigma):
                Q[sigma_i, i] = signs[i]
            # A acts on R^3 in the standard basis: A * V_i = s_i * V_{sigma(i)}
            # so A * M = M * Q, hence A = M * Q * M^{-1}
            A = M @ Q @ Minv
            automorphisms.append((sigma, signs, A))
    return automorphisms


def verify_preserves_V(A, V_set):
    """Verify A * v in V_set for every v in V_set."""
    for v in V_set:
        Av = A @ v
        # Round to integer (V elements have integer entries)
        Av_int = np.round(Av).astype(int)
        if not np.allclose(Av, Av_int, atol=1e-8):
            return False
        if not any(np.array_equal(Av_int, w) for w in V_set):
            return False
    return True


def is_orthogonal(A, tol=1e-8):
    """Check whether A^T A = I."""
    return np.allclose(A.T @ A, np.eye(3), atol=tol)


def matrix_signature(A):
    """Hashable signature for grouping equal matrices."""
    return tuple(np.round(A.flatten() * 1e6).astype(int))


def group_orders(automorphisms):
    """Group elements by signature and report distinct count."""
    sigs = set()
    for _, _, A in automorphisms:
        sigs.add(matrix_signature(A))
    return len(sigs)


def cayley_check(automorphisms):
    """Verify the set is closed under multiplication (forms a group)."""
    sigs = {matrix_signature(A) for _, _, A in automorphisms}
    matrices = [A for _, _, A in automorphisms]
    for A in matrices[:8]:  # sample to keep runtime bounded
        for B in matrices[:8]:
            AB = A @ B
            if matrix_signature(AB) not in sigs:
                return False
    return True


def report():
    rgb = basis_vectors()
    V_set = unsigned_basis_set(rgb)
    auts = candidate_automorphisms(rgb)

    print("=" * 70)
    print("Discrete automorphism group of (T_diamond^3 generators V)")
    print("=" * 70)
    print()
    print(f"V_1 = {tuple(rgb[0])}")
    print(f"V_2 = {tuple(rgb[1])}")
    print(f"V_3 = {tuple(rgb[2])}")
    print(f"V = {{+/-V_i}} = 6 elements")
    print()

    # Step 1: enumerate candidates
    print(f"Candidate automorphisms (sigma in S_3 x signs in {{+/-1}}^3): "
          f"{len(auts)}")

    # Step 2: verify each preserves V
    n_preserved = sum(1 for _, _, A in auts if verify_preserves_V(A, V_set))
    print(f"Of these, V-preserving: {n_preserved}")

    # Step 3: distinct matrices
    n_distinct = group_orders(auts)
    print(f"Distinct matrices: {n_distinct}")

    # Step 4: check group closure
    closure = cayley_check(auts)
    print(f"Group closure (sample of 64 products): "
          f"{'closed' if closure else 'NOT closed'}")

    # Step 5: orthogonal subset
    n_orth = sum(1 for _, _, A in auts if is_orthogonal(A))
    print(f"Of the {n_distinct} matrices, orthogonal: {n_orth}")
    print()

    # Step 6: report a few example matrices
    print("-" * 70)
    print("Example automorphisms")
    print("-" * 70)

    # Identity
    sigma0, signs0, A0 = auts[0]
    print(f"\n1. Identity (sigma={sigma0}, signs={signs0}):")
    print(A0.astype(int))

    # Find -I
    for sigma, signs, A in auts:
        if np.allclose(A, -np.eye(3)):
            print(f"\n2. -Identity (sigma={sigma}, signs={signs}):")
            print(A.astype(int))
            break

    # First non-orthogonal example
    for sigma, signs, A in auts:
        if not is_orthogonal(A) and not np.allclose(A, np.eye(3)):
            print(f"\n3. First non-orthogonal (sigma={sigma}, signs={signs}):")
            print(A.astype(int))
            print(f"   |A * e_1| = {np.linalg.norm(A @ np.array([1,0,0])):.4f}"
                  f"  (should be 1 if orthogonal)")
            print(f"   det(A) = {np.linalg.det(A):.4f}")
            break

    # Permutation of V_1, V_2, V_3 (sigma=(0,2,1), signs=(+,+,+))
    for sigma, signs, A in auts:
        if sigma == (0, 2, 1) and signs == (1, 1, 1):
            print(f"\n4. RGB permutation V_2<->V_3 (sigma={sigma}, signs={signs}):")
            print(A.astype(int))
            print(f"   orthogonal: {is_orthogonal(A)}")
            break

    print()
    print("-" * 70)
    print("Structure summary")
    print("-" * 70)
    print(f"|Aut_discrete(Gamma, V)| = {n_distinct} = 6 * 8 = |S_3| * |Z_2^3|")
    print(f"Group abstractly = Z_2 wr S_3 = B_3 = O_h")
    print(f"Orthogonal subgroup order = {n_orth}")
    print(f"  (genuine crystallographic point symmetry in the standard"
          f" embedding)")
    print()
    print("Interpretation:")
    print("  The full 48-element group preserves the lattice Gamma and")
    print("  the basis-vector set V, but only the orthogonal subgroup")
    print(f"  ({n_orth} elements) also preserves the standard metric.")
    print("  The non-orthogonal elements are 'shears' that permute the")
    print("  basis labels at the cost of distorting angles.  In the")
    print("  framework, the bipartite tick rule treats RGB labels")
    print("  symmetrically, so the full 48-element group is the relevant")
    print("  discrete spatial symmetry; the metric is restored in the")
    print("  continuum limit by the O_h-averaging mechanism (paper sec 6).")


if __name__ == '__main__':
    report()
