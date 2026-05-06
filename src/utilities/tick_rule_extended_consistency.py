"""
tick_rule_extended_consistency.py

Step 5 follow-on (#16 question (i)): verify the bipartite tick rule
extends consistently to the proposed C^12 amplitude

    psi in C^2 (chirality) (x) C^2 (isospin) (x) C^3 (colour) = C^12

via the trivial tensor extension.  The natural extension acts as the
existing tick rule on the chirality factor and as the identity on
the isospin and colour factors:

    T_extended = T_chirality (x) I_2 (x) I_3

This script verifies:

(1) T_chirality is unitary on C^2 for the framework's
    cos(delta_phi/2), sin(delta_phi/2) construction.
(2) T_extended on C^12 is unitary (preserves A=1).
(3) T_extended commutes with the global SU(2)_W and SU(3) generators
    that act on the new isospin/colour factors.
(4) The bipartite parity sigma_x (x) I_2 (x) I_3 acts on T_extended
    consistently with the existing chirality-only parity action.

What this answers and what it does NOT answer.

Answered:

- The trivial tensor extension preserves A=1 and the conjecture's
  global direct-product symmetries.  The framework's existing
  tick-rule unitarity (per-tick A=1) carries over to the extended
  amplitude by linearity.
- SU(2)_W and SU(3) act as GLOBAL symmetries of the extended tick
  rule -- the tick rule does not mix isospin or colour components,
  so any constant rotation of those factors commutes with it.

Open (deferred to question (iv) of #16):

- Whether the trivial extension is PHYSICALLY meaningful, or just
  N independent copies of the existing dynamics.  For SU(2)_W and
  SU(3) to be physical gauge symmetries (with non-trivial
  W/Z/photon/gluon dynamics), the framework needs a connection
  field that couples to the matter currents -- the gauge-coupling
  step beyond the global symmetry verified here.
- Whether the SM-chirality coupling (SU(2)_W acts only on
  left-handed components) can be implemented at the lattice level.
  The trivial tensor extension is symmetric in psi_R vs psi_L; the
  SM is not.  This is question (iii) of #16.

This script closes (i) at the level of "the trivial extension does
no harm to the existing framework's invariants" -- which is the
content needed to certify that the structural extension is at least
self-consistent.  Whether it adds physical content beyond the
existing dynamics is a separate question for the follow-on paper.
"""

import itertools
import numpy as np
import sympy as sp
from sympy import I, Matrix, eye, sqrt, simplify, Rational, cos, sin, symbols


def pauli_matrices():
    s_x = Matrix([[0, 1], [1, 0]])
    s_y = Matrix([[0, -I], [I, 0]])
    s_z = Matrix([[1, 0], [0, -1]])
    return [s_x, s_y, s_z]


def gell_mann():
    L1 = Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 0]])
    L2 = Matrix([[0, -I, 0], [I, 0, 0], [0, 0, 0]])
    L3 = Matrix([[1, 0, 0], [0, -1, 0], [0, 0, 0]])
    L4 = Matrix([[0, 0, 1], [0, 0, 0], [1, 0, 0]])
    L5 = Matrix([[0, 0, -I], [0, 0, 0], [I, 0, 0]])
    L6 = Matrix([[0, 0, 0], [0, 0, 1], [0, 1, 0]])
    L7 = Matrix([[0, 0, 0], [0, 0, -I], [0, I, 0]])
    L8 = (Rational(1, 1) / sqrt(3)) * Matrix([[1, 0, 0], [0, 1, 0], [0, 0, -2]])
    return [L1, L2, L3, L4, L5, L6, L7, L8]


def kron(*mats):
    r = mats[0]
    for M in mats[1:]:
        r = sp.kronecker_product(r, M)
    return r


def chirality_tick_operator(delta_phi):
    """The tick-rule chirality operator on C^2 = (psi_R, psi_L).

    From the framework: at each tick the chirality components mix as

        new_psi_R = cos(delta_phi/2) * psi_L + i sin(delta_phi/2) * psi_R
        new_psi_L = cos(delta_phi/2) * psi_R + i sin(delta_phi/2) * psi_L

    This is the local (no-spatial-hop) version of the bipartite
    tick rule -- the spatial hop is a separate operator that
    commutes trivially with the internal extension by construction
    (hop depends on position only, not on internal indices).

    Matrix form on (psi_R, psi_L)^T:

        T = [[i sin(d/2),  cos(d/2)],
             [cos(d/2),    i sin(d/2)]]

    where d = delta_phi.
    """
    c = cos(delta_phi / 2)
    s = sin(delta_phi / 2)
    return Matrix([[I * s, c],
                   [c, I * s]])


def commutator(A, B):
    return simplify(A @ B - B @ A)


def is_zero(M):
    return all(simplify(e) == 0 for e in M)


def is_identity(M, n):
    return simplify(M - eye(n)) == sp.zeros(n, n)


def report():
    print("=" * 70)
    print("Tick-rule consistency on the extended C^12 amplitude")
    print("=" * 70)
    print()

    # Use a symbolic delta_phi to make the verification general
    dphi = symbols('delta_phi', real=True)

    T = chirality_tick_operator(dphi)
    print("Chirality tick operator T on C^2 (symbolic in delta_phi):")
    sp.pprint(T)
    print()

    # ── Step 1: T is unitary on C^2 ─────────────────────────────────────
    print("-" * 70)
    print("Step 1: T is unitary on C^2 (chirality)")
    print("-" * 70)
    T_dag = T.H
    TT = simplify(T_dag @ T)
    print(f"  T^dag T = I_2:  {is_identity(TT, 2)}")
    print()
    if is_identity(TT, 2):
        print("  T preserves the chirality C^2 norm |psi_R|^2 + |psi_L|^2.")
        print("  This is the per-tick A=1 condition on the existing")
        print("  framework's per-site amplitude.")
    print()

    # ── Step 2: T_extended is unitary on C^12 ────────────────────────────
    print("-" * 70)
    print("Step 2: T_extended = T (x) I_2 (x) I_3 is unitary on C^12")
    print("-" * 70)
    T_ext = kron(T, eye(2), eye(3))
    T_ext_dag = T_ext.H
    TE_TE = simplify(T_ext_dag @ T_ext)
    is_unit_ext = is_identity(TE_TE, 12)
    print(f"  T_ext^dag T_ext = I_12:  {is_unit_ext}")
    print()
    if is_unit_ext:
        print("  T_extended preserves the C^12 norm.  A=1 on the extended")
        print("  amplitude follows from A=1 on the chirality C^2.")
    print()

    # ── Step 3: T_extended commutes with SU(2)_W and SU(3) ──────────────
    print("-" * 70)
    print("Step 3: T_extended commutes with global SU(2)_W and SU(3) generators")
    print("-" * 70)
    print()

    sigma = pauli_matrices()
    GM = gell_mann()

    print("  SU(2)_W generators T_a = I_2 (x) (sigma_a/2) (x) I_3:")
    su2_ok = True
    for a in range(3):
        Ta = kron(eye(2), Rational(1, 2) * sigma[a], eye(3))
        c = commutator(T_ext, Ta)
        ok = is_zero(c)
        print(f"    [T_ext, T_{a+1}] = 0?  {ok}")
        if not ok:
            su2_ok = False
    print()

    print("  SU(3) generators G_a = I_2 (x) I_2 (x) (lambda_a/2):")
    su3_ok = True
    for a in range(8):
        Ga = kron(eye(2), eye(2), Rational(1, 2) * GM[a])
        c = commutator(T_ext, Ga)
        ok = is_zero(c)
        print(f"    [T_ext, G_{a+1}] = 0?  {ok}")
        if not ok:
            su3_ok = False
    print()

    # ── Step 4: bipartite parity on the extended amplitude ──────────────
    print("-" * 70)
    print("Step 4: bipartite parity sigma_x acts on chirality, identity on rest")
    print("-" * 70)
    print()

    P_chir = sigma[0]  # sigma_x: swaps psi_R <-> psi_L
    P_ext = kron(P_chir, eye(2), eye(3))

    # Parity acting on T then T acting on the result vs T acting then parity:
    # for the framework's bipartite alternation, parity sends (even RGB tick) to
    # (odd CMY tick), so PT = TP only if T is parity-symmetric.  The local
    # chirality operator T from above mixes psi_R <-> psi_L symmetrically
    # (c diagonal, c off-diagonal both equal), so PTP = T.

    PTP = simplify(P_ext @ T_ext @ P_ext)
    same = simplify(PTP - T_ext) == sp.zeros(12, 12)
    print(f"  P_ext @ T_ext @ P_ext = T_ext?  {same}")
    if same:
        print("  The bipartite parity is a symmetry of the chirality tick rule")
        print("  on C^2, and the trivial tensor extension preserves this on")
        print("  C^12.  Parity acts only on the chirality factor; the isospin")
        print("  and colour factors are parity-singlets.")
    print()

    # ── Step 5: structural conclusion ───────────────────────────────────
    print("-" * 70)
    print("Step 5: structural conclusion")
    print("-" * 70)
    print()
    all_ok = (is_identity(TT, 2) and is_unit_ext and su2_ok and su3_ok
              and same)
    print(f"  All four checks pass: {all_ok}")
    print()
    print("  The trivial tensor extension")
    print("      T_extended = T_chirality (x) I_2 (x) I_3")
    print("  preserves:")
    print("    - A=1 on C^12 (T_extended unitary)")
    print("    - global SU(2)_W and SU(3) symmetries (commutators vanish)")
    print("    - bipartite parity (P sigma_x P = sigma_x equivalent)")
    print()
    print("  This certifies that the structural extension does no harm to")
    print("  the framework's existing invariants.  It does NOT yet")
    print("  certify that the extension has physical content beyond")
    print("  N = 6 independent copies of the existing dynamics.")
    print()
    print("  Open for #16 question (iv): identify the lattice connection")
    print("  field that couples SU(2)_W and SU(3) gauge transformations")
    print("  to the matter currents non-trivially.  Without that coupling")
    print("  the new factors are global symmetries with trivial gauge")
    print("  fields -- the existence is established but the physics is")
    print("  not.  With a non-trivial coupling, SU(2)_W gives W^+/W^-/Z")
    print("  and SU(3) gives the gluons.")
    print()
    print("  Open for #16 question (iii): align the framework's bipartite")
    print("  RGB/CMY chirality with the SM's left-only coupling of SU(2)_W.")
    print("  The trivial extension is symmetric in psi_R vs psi_L; the")
    print("  SM is not.  This requires the gauge coupling to break the")
    print("  symmetry between psi_R and psi_L when projected onto the")
    print("  SU(2)_W doublet.")


if __name__ == '__main__':
    report()
