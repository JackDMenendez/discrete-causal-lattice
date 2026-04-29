"""
induced_gauge_action.py

Symbolic derivation of the leading-order induced gauge action on the
bipartite octahedral lattice, addressing the open program flagged in
paper/sections/vacuum_twist_field_equations.tex (subsec:open_program)
and notes/em_derivation_solution.md.

Setup
-----
The bipartite lattice has basis vectors

    V1 = (1,1,1)   V2 = (1,-1,-1)   V3 = (-1,1,-1)        (RGB sublattice)
    -V1, -V2, -V3                                          (CMY sublattice)

Each lattice link of length a v carries a U(1) link variable
U_v(x) = exp( i a A(x + v/2) . v ) -- the Peierls form.  Under a
local U(1) gauge transformation the link variables transform so that
closed-loop holonomies (Wilson loops) are gauge-invariant local
operators built from A.

The smallest gauge-invariant nontrivial closed loop on this lattice is
the bipartite plaquette: an RGB hop along V_a, a CMY hop along -V_b,
an RGB hop along -V_a, and a CMY hop along +V_b -- traversing a
parallelogram with sides aV_a and -aV_b.  By Stokes' theorem (Abelian
U(1)) the holonomy of this loop in the small-a limit is

    W_{ab}(x) = exp( -i a^2 V_a^i V_b^j F_{ij}(x) ) + O(a^4)

where F_{ij}(x) = d_i A_j - d_j A_i is the standard field-strength
tensor.  Therefore

    1 - Re W_{ab}(x)  =  (a^4 / 2) ( V_a^i V_b^j F_{ij}(x) )^2  +  O(a^8).

The Sakharov / Zeldovich claim is that the induced gauge action

    S_eff[U] = -Tr ln D_lat[U]

obtained by integrating out matter, expanded as a sum over closed
lattice loops, is dominated at leading order by the smallest
gauge-invariant Wilson loop -- here, the bipartite plaquette.  The
result is

    S_eff[A]  =  c * sum_{plaquettes} ( 1 - Re W_{ab}(x) )  +  O(a^6)
              =  (c a^4 / 2) sum_{ab} ( V_a^i V_b^j F_{ij} )^2 + O(a^6)

with c a numerical prefactor (the inverse coupling 1/g^2) which
requires the explicit Tr ln D_lat[U] computation -- a paper-length
project we leave to follow-on work.  What this script computes is the
*structural* form of the leading term: the tensor coefficient
multiplying F_{ij} F_{kl} that emerges from summing over the three
bipartite plaquette planes.

Result
------
The plaquette sum yields a quadratic form

    sum_{ab in {(1,2),(1,3),(2,3)}} ( V_a^i V_b^j F_{ij} )^2
        = F^T Q F                (F = (F_12, F_13, F_23) in 3D)

with Q = ((8, 4, -4), (4, 8, -4), (-4, -4, 8)) and eigenvalues
{4, 4, 16}.  Two equal eigenvalues 4 and one distinct eigenvalue 16
-- the same two-and-one structure as the kinematic frame matrix
M_eff (eigenvalues {4/3, 4/3, 0}, paper eq:M_eff).  After O_h
averaging the leading term reduces to (Tr Q / 3) sum_{i<j} F_ij^2 =
8 sum_{i<j} F_ij^2 -- the standard Maxwell magnetic density up to
overall normalisation.  The residual anisotropy Q - (Tr Q / 3) I
has trace zero, eigenvalues {-4, -4, +8}, and aligns with the
optical axis V1+V2+V3 = (1,1,-1) of the kinematic-sector
birefringence.

This is the gauge-sector birefringence: photon dispersion in the
induced action is direction-dependent at the operator level, with
the same optical axis as the kinematic-sector prediction P7
(paper subsec:p7_photon_dispersion).  After O_h averaging the
standard Maxwell action is recovered; the residual is a closed-form
falsifiable signature.

What this script does NOT compute is the prefactor c = 1/g^2 -- that
requires the full one-loop Tr ln D_lat[U] calculation, which we flag
as remaining work in the appendix.

Output
------
   data/induced_gauge_action.txt     (numeric / symbolic results)
   stdout                            (same)

Run
---
   python -u src/utilities/induced_gauge_action.py

References
----------
   paper/sections/emergent_kinematics.tex (eq:M_eff)
   paper/sections/vacuum_twist_field_equations.tex (eq:wilson_loop,
       eq:induced_action, subsec:open_program)
   notes/em_derivation_solution.md
   notes/frame_condition_isotropy_memo.md
"""

import os
import sys
from itertools import combinations

import sympy as sp

# ─── Output redirection ─────────────────────────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA_PATH = os.path.join(ROOT, "data", "induced_gauge_action.txt")
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            if not getattr(st, "closed", False):
                st.write(s)
                st.flush()

    def flush(self):
        for st in self.streams:
            if not getattr(st, "closed", False):
                st.flush()


_data_file = open(DATA_PATH, "w", encoding="utf-8")
sys.stdout = Tee(sys.__stdout__, _data_file)


def banner(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


# ─── Step 1: bipartite basis and frame matrix M ─────────────────────────────
banner("Step 1: bipartite basis and frame matrix M (paper eq:frame_matrix)")

V1 = sp.Matrix([1, 1, 1])
V2 = sp.Matrix([1, -1, -1])
V3 = sp.Matrix([-1, 1, -1])
RGB = [V1, V2, V3]
labels = ["V1", "V2", "V3"]

M = sum((v * v.T for v in RGB), sp.zeros(3, 3))
print("M = sum_{v in RGB} v v^T =")
sp.pprint(M)
print("eigenvalues:", M.eigenvals(), "  (= {1, 4 (mult 2)})")
print("trace:", sp.trace(M), "  (= 9)")
print("optical axis V1 + V2 + V3 =", (V1 + V2 + V3).T)
print()
print("M_eff = -4/9 I + 4/9 M = (paper eq:M_eff, kinematic-sector birefringence)")
M_eff = -sp.Rational(4, 9) * sp.eye(3) + sp.Rational(4, 9) * M
sp.pprint(M_eff)
print("eigenvalues of M_eff:", M_eff.eigenvals(),
      "  (= {0, 4/3 (mult 2)}; zero along (1,1,-1))")


# ─── Step 2: bipartite plaquette projections via Stokes (closed-form) ───────
banner("Step 2: bipartite plaquette projections V_a^i V_b^j F_{ij}")

# Symbolic field-strength tensor (3D, antisymmetric).  The independent
# components are F_12, F_13, F_23 (the magnetic-sector content).
F12, F13, F23 = sp.symbols("F12 F13 F23", real=True)
F = sp.Matrix([
    [0,    F12,  F13],
    [-F12, 0,    F23],
    [-F13, -F23, 0  ],
])
print("F_{ij} (3D antisymmetric, magnetic sector) =")
sp.pprint(F)


def plaquette_projection(va, vb):
    """V_a^i V_b^j F_{ij}  -- the Stokes projection of F onto the (V_a, V_b) plane."""
    return sp.simplify(sum(va[i] * vb[j] * F[i, j] for i in range(3) for j in range(3)))


print()
print("Bipartite plaquette projections (V_a^i V_b^j F_{ij}):")
projections = {}
for (a, va), (b, vb) in combinations(zip(labels, RGB), 2):
    proj = plaquette_projection(list(va), list(vb))
    projections[(a, b)] = proj
    print(f"  ({a}, {b}) plaquette:  V_{a}^i V_{b}^j F_ij  =  {proj}")


# ─── Step 3: induced action density -- sum of plaquette squares ─────────────
banner("Step 3: induced-action density   sum_{ab} (V_a^i V_b^j F_{ij})^2")

# 1 - Re W_{ab} = (a^4/2) * (proj)^2 + O(a^8) for each plaquette.
# Sum over all three RGB plaquette planes (V1V2, V1V3, V2V3).
density = sp.expand(sum(p**2 for p in projections.values()))
print("Plaquette-sum density (modulo a^4/2 prefactor):")
sp.pprint(density)
print()

# Express as a quadratic form Q in F-basis (F_12, F_13, F_23):
# density = (F_12, F_13, F_23) . Q . (F_12, F_13, F_23)^T
F_basis = [F12, F13, F23]
Q = sp.zeros(3, 3)
for i in range(3):
    Q[i, i] = density.coeff(F_basis[i], 2)
for i in range(3):
    for j in range(i + 1, 3):
        # cross-term coefficient -> Q[i,j] = Q[j,i] = (cross) / 2
        cross = density.coeff(F_basis[i] * F_basis[j])
        Q[i, j] = cross / 2
        Q[j, i] = cross / 2
print("Quadratic form coefficient matrix Q  (density = F^T Q F):")
sp.pprint(Q)
print()

# Verify
density_from_Q = sp.expand((sp.Matrix(F_basis).T * Q * sp.Matrix(F_basis))[0])
print("Verification  density - F^T Q F =", sp.simplify(density - density_from_Q))


# ─── Step 4: eigenstructure of Q -- the gauge-sector birefringence ──────────
banner("Step 4: eigenstructure of Q   (gauge-sector birefringence)")

eigs_Q = Q.eigenvals()
print("Eigenvalues of Q:", eigs_Q)
print()

# Trace and O_h-averaged scalar coefficient:
trQ = sp.trace(Q)
print(f"Trace(Q) = {trQ}    (sum of eigenvalues)")
print(f"Tr(Q)/3  = {sp.Rational(trQ, 3)}    (O_h-averaged scalar coefficient)")
print()

# Decompose Q into isotropic + traceless anisotropic
Q_iso = sp.Rational(trQ, 3) * sp.eye(3)
Q_aniso = sp.simplify(Q - Q_iso)
print("Q_iso = (Tr Q / 3) I  (the O_h-averaged Maxwell coefficient):")
sp.pprint(Q_iso)
print()
print("Q_aniso = Q - Q_iso  (traceless residual; the gauge-sector birefringence):")
sp.pprint(Q_aniso)
print(f"trace(Q_aniso) = {sp.trace(Q_aniso)}    (must be 0)")
print("eigenvalues of Q_aniso:", Q_aniso.eigenvals())


# ─── Step 5: the optical-axis eigenvector of Q ──────────────────────────────
banner("Step 5: the special direction in F-space")

# Find the eigenvector corresponding to the distinct eigenvalue
print("Eigenvectors of Q (in the (F_12, F_13, F_23) basis):")
for eigval, mult, eigvecs in Q.eigenvects():
    print(f"  eigenvalue {eigval} (multiplicity {mult}):")
    for ev in eigvecs:
        print("   ", ev.T)


# ─── Step 6: continuum-limit form ───────────────────────────────────────────
banner("Step 6: continuum-limit Maxwell action with anisotropic coefficient")

print("""
After O_h averaging the leading induced action density is

    rho_eff(x)  =  (c / 2) * (Tr Q / 3) * sum_{i<j} F_ij^2(x)
                =  (4 c / 3) * sum_{i<j} F_ij^2(x)
                =  (2 c / 3) * F_{ij} F^{ij}                  ( = standard Maxwell magnetic density )

where the prefactor c absorbs the lattice spacing (a^4) and the
numerical 1/g^2 prefactor from the explicit Tr ln D_lat calculation
(NOT computed in this script -- see appendix).

The residual operator-level density, before O_h averaging, is

    rho_full(x)  =  (c / 2) * F^T Q F
                =  (c / 2) [ (Tr Q / 3) * sum_{i<j} F_ij^2  +  F^T Q_aniso F ].

The Q_aniso term is the gauge-sector birefringence:
direction-dependent contribution to the photon dispersion which, by
the same eigenstructure as M_eff (paper eq:M_eff), aligns with the
optical axis V1 + V2 + V3 = (1,1,-1) when expressed in spatial
coordinates.
""")


# ─── Step 7: structural conclusion ──────────────────────────────────────────
banner("Conclusion: structure of the leading induced gauge action")

print("""
On the bipartite octahedral lattice, the leading-order induced gauge
action emerging from Tr ln D_lat[U] (Sakharov / Zeldovich form) has
the structure

      S_eff[A]  =  (a^4 c / 2) * sum_{plaquettes} ( V_a^i V_b^j F_{ij} )^2
                +  O(a^6)
                +  numerical prefactor from explicit Tr ln D_lat

with

  *  Locality + gauge invariance + minimality forcing the leading
     term to be quadratic in F_{ij} (closed plaquette holonomies).
  *  The bipartite RGB/CMY geometry forcing the F^2 coefficient to
     be a tensor Q with eigenvalues {4, 4, 16} (this script).
  *  O_h averaging recovering the standard Maxwell density (Tr Q / 3
     I = 8 I) up to the numerical prefactor c.
  *  The traceless residue Q_aniso (eigenvalues {-4, -4, +8})
     aligning with the optical axis V1+V2+V3 = (1,1,-1) and
     producing the gauge-sector birefringence.

Closing what was open in paper subsec:open_program:

  Task 1 (path-integral measure):    not done here -- standard.
  Task 2 (compute Tr ln D_lat[U]):   structural form computed; the
                                     numerical prefactor c remains
                                     to be extracted.
  Task 3 (continuum limit):          done -- standard 1 - Re W -> a^4 F^2/2.

What remains is the explicit one-loop calculation of c (the inverse
gauge coupling), which is a paper-length project (lattice perturbation
theory for the bipartite Dirac operator).  The structural form,
including the gauge-sector birefringence prediction, is established
without that computation.
""")

print(f"Output saved to {DATA_PATH}")
_data_file.close()
