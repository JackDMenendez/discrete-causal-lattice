"""
induced_action_ellipsoid.py

Side-by-side 3D rendering of the two anisotropy tensors in the framework:

  Left  panel: M_kinematic = sum_{v in RGB} v v^T    eigenvalues {4, 4, 1}
                                                     -> prolate ellipsoid in k-space
                                                     -> long axis along V1+V2+V3 = (1,1,-1)

  Right panel: Q_gauge      from bipartite plaquette sum  eigenvalues {4, 4, 16}
                                                     -> oblate ellipsoid in B-space
                                                     -> short axis along V1+V2+V3 = (1,1,-1)

The two anisotropies share the same optical axis (1,1,-1) by inheritance from the
bipartite RGB/CMY geometry, but produce dual ellipsoid shapes.  In the kinematic
sector the dispersion is "long" along the axis and "short" perpendicular; in the
gauge sector the photon's effective kinetic-term curvature is "short" along the
axis and "long" perpendicular.  Same geometry, dual phenomenology.

Q is computed as in src/utilities/induced_gauge_action.py and Appendix B of the
paper:

    Q (F-basis)  =  ((8, 4, -4), (4, 8, -4), (-4, -4, 8))
                 with eigenvalues {4, 4, 16}.

The 3D Hodge dual maps F-space (F_12, F_13, F_23) onto B-space (B_1, B_2, B_3)
via F_12 = B_3, F_13 = -B_2, F_23 = B_1.  Substituting, the quadratic form in
B-coordinates carries the same matrix Q (the Hodge dual is a structure-preserving
linear map on antisymmetric 3D tensors), and the eigenvector for eigenvalue 16
becomes (1, 1, -1) in B-space -- the kinematic optical axis.

Output:
    figures/induced_action_ellipsoid.{png,pdf}
    data/induced_action_ellipsoid.txt

Run:
    python -u src/utilities/induced_action_ellipsoid.py

References:
    paper/sections/emergent_kinematics.tex (eq:frame_matrix, eq:M_eff)
    paper/sections/induced_gauge_action.tex (eq:Q_matrix, eq:optical_axis_recovered)
    src/utilities/frame_matrix_visualization.py (style template)
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# ─── Bipartite basis and tensors ────────────────────────────────────────────
V1 = np.array([1,  1,  1])
V2 = np.array([1, -1, -1])
V3 = np.array([-1, 1, -1])
RGB = np.array([V1, V2, V3])

M_kinematic = sum(np.outer(v, v) for v in RGB)
print("M_kinematic =\n", M_kinematic)

Q_gauge = np.array([
    [ 8,  4, -4],
    [ 4,  8, -4],
    [-4, -4,  8],
])
print("Q_gauge =\n", Q_gauge)

# Eigendecompositions (eigh sorts ascending; we want descending principal)
def eigsorted_desc(A):
    w, V = np.linalg.eigh(A)
    order = np.argsort(w)[::-1]
    return w[order], V[:, order]

eigM, vecM = eigsorted_desc(M_kinematic)
eigQ, vecQ = eigsorted_desc(Q_gauge)
print()
print(f"M eigenvalues (desc): {eigM}")
print("M eigenvectors (cols, in k-space):")
print(vecM)
print()
print(f"Q eigenvalues (desc): {eigQ}")
print("Q eigenvectors (cols, in F-basis = (F_12, F_13, F_23)):")
print(vecQ)

# ─── Hodge dual: F-space -> B-space ─────────────────────────────────────────
# F_12 = B_3, F_13 = -B_2, F_23 = B_1   ==>  matrix mapping B -> F is
#     P = ((0, 0, 1), (0, -1, 0), (1, 0, 0))
# and the inverse maps F-eigenvectors to B-eigenvectors.
P = np.array([
    [0, 0, 1],
    [0, -1, 0],
    [1, 0, 0],
], dtype=float)
# Q in B-space: B^T Q' B with Q' = P^T Q P (symbolically Q' = Q because P is
# orthogonal up to sign).
Q_in_B = P.T @ Q_gauge @ P
print()
print("Q in B-space:")
print(Q_in_B)
eigQB, vecQB = eigsorted_desc(Q_in_B)
print(f"Q (B-space) eigenvalues (desc): {eigQB}")
print("Q (B-space) eigenvectors (cols, in B-basis):")
print(vecQB)
print()
# Sanity-check: the eigenvalue-16 eigenvector in B-space should be
# proportional to V1 + V2 + V3 = (1, 1, -1).
optical_axis = (V1 + V2 + V3).astype(float)
optical_axis /= np.linalg.norm(optical_axis)
print(f"Optical axis V1+V2+V3 normalized = {optical_axis}")
ev16_B = vecQB[:, 0]   # largest eigenvalue first; eigenvalue 16 is the largest
ev16_B = ev16_B / np.linalg.norm(ev16_B)
overlap = abs(np.dot(ev16_B, optical_axis))
print(f"|<V1+V2+V3 / |.|, eigvec_lambda=16>| = {overlap:.6f}  (should be 1.0)")

# ─── Build parametric surfaces ──────────────────────────────────────────────
C_LEVEL = 3.0  # same level-set scale as frame_matrix_ellipsoid.py
N_U, N_V = 70, 70
u = np.linspace(0, 2*np.pi, N_U)
v_ang = np.linspace(0, np.pi, N_V)
U, Vang = np.meshgrid(u, v_ang)
unit_sphere = np.stack([
    np.cos(U) * np.sin(Vang),
    np.sin(U) * np.sin(Vang),
    np.cos(Vang),
], axis=-1)  # (N_V, N_U, 3)


def ellipsoid_from_eig(eigvals, eigvecs, c_level=C_LEVEL):
    """Return parametric mesh for the level set x^T M x = c_level given eigendata."""
    semi = np.sqrt(c_level / eigvals)               # semi-axes along principal dirs
    local = unit_sphere * semi                      # broadcast (N_V, N_U, 3)
    return local @ eigvecs.T                        # rotate to global frame


# Kinematic ellipsoid in k-space (M)
M_xyz = ellipsoid_from_eig(eigM, vecM)
M_semi = np.sqrt(C_LEVEL / eigM)

# Gauge ellipsoid in B-space (Q_in_B); eigenvalues are still {4, 4, 16}
Q_xyz = ellipsoid_from_eig(eigQB, vecQB)
Q_semi = np.sqrt(C_LEVEL / eigQB)

# Reference sphere (equal-volume, for a faint comparison surface)
def equal_vol_radius(semi):
    return float(np.prod(semi)) ** (1.0 / 3)

R_M = equal_vol_radius(M_semi)
R_Q = equal_vol_radius(Q_semi)
ref_M = R_M * unit_sphere
ref_Q = R_Q * unit_sphere

# ─── Figure ─────────────────────────────────────────────────────────────────
EXTENT = max(M_semi.max(), 1.05) * 1.20

fig = plt.figure(figsize=(13.5, 6.2), constrained_layout=True)


def style_axes(ax, title, x_label, y_label, z_label):
    ax.set_xlim(-EXTENT, EXTENT)
    ax.set_ylim(-EXTENT, EXTENT)
    ax.set_zlim(-EXTENT, EXTENT)
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_zlabel(z_label)
    ax.set_title(title, pad=10)
    ax.xaxis.pane.set_facecolor((1, 1, 1, 0.0))
    ax.yaxis.pane.set_facecolor((1, 1, 1, 0.0))
    ax.zaxis.pane.set_facecolor((1, 1, 1, 0.0))
    ax.view_init(elev=22, azim=35)


def draw_axes_lines(ax):
    L = EXTENT * 0.95
    for vec in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
        v = np.array(vec) * L
        ax.plot([-v[0], v[0]], [-v[1], v[1]], [-v[2], v[2]],
                color="0.7", linewidth=0.6, zorder=0)


def draw_optical_axis(ax, length, color="black"):
    """Draw V1+V2+V3 = (1,1,-1) as a dashed black line through origin."""
    direction = np.array([1, 1, -1], dtype=float)
    direction /= np.linalg.norm(direction)
    end = direction * length
    ax.plot([-end[0], end[0]], [-end[1], end[1]], [-end[2], end[2]],
            color=color, linewidth=1.5, alpha=0.85, linestyle="--", zorder=10)
    # label the +end
    ax.text(end[0]*1.05, end[1]*1.05, end[2]*1.05,
            r"$\mathbf{V}_1+\mathbf{V}_2+\mathbf{V}_3$",
            fontsize=8, ha="center", color=color)


def draw_ellipsoid(ax, xyz, dev, cmap_name="RdBu_r"):
    norm = plt.Normalize(vmin=-np.abs(dev).max(), vmax=np.abs(dev).max())
    colors = plt.get_cmap(cmap_name)(norm(dev))
    ax.plot_surface(xyz[..., 0], xyz[..., 1], xyz[..., 2],
                    facecolors=colors, alpha=0.85, linewidth=0.0,
                    antialiased=True)


def draw_principal_axes_labels(ax, eigvals, eigvecs, semi):
    for i in range(3):
        direction = eigvecs[:, i]
        a = direction * semi[i]
        ax.plot([-a[0], a[0]], [-a[1], a[1]], [-a[2], a[2]],
                color="black", linewidth=0.9, alpha=0.5, linestyle=":")
        ax.text(a[0]*1.10, a[1]*1.10, a[2]*1.10,
                rf"$\lambda={eigvals[i]:.0f}$",
                fontsize=8, ha="center", color="black")


# ── Left panel: M_kinematic in k-space (prolate, long axis along (1,1,-1)) ──
ax1 = fig.add_subplot(1, 2, 1, projection="3d")
style_axes(
    ax1,
    r"Kinematic sector: $M = \sum_\mathrm{RGB} \mathbf{v}\mathbf{v}^T$"
    "\n"
    r"eigenvalues $\{4,4,1\}$ $\Rightarrow$ prolate ($\mathbf{long}$ axis along $(1,1,-1)$)",
    r"$k_1$", r"$k_2$", r"$k_3$",
)
draw_axes_lines(ax1)
M_r = np.linalg.norm(M_xyz, axis=-1)
M_dev = M_r - R_M
draw_ellipsoid(ax1, M_xyz, M_dev, cmap_name="RdBu_r")
draw_principal_axes_labels(ax1, eigM, vecM, M_semi)
draw_optical_axis(ax1, length=M_semi.max() * 1.15)

# ── Right panel: Q_gauge in B-space (oblate, short axis along (1,1,-1)) ─────
ax2 = fig.add_subplot(1, 2, 2, projection="3d")
style_axes(
    ax2,
    r"Gauge sector: $\mathbf{Q}$ from bipartite plaquette sum (App. B)"
    "\n"
    r"eigenvalues $\{4,4,16\}$ $\Rightarrow$ oblate ($\mathbf{short}$ axis along $(1,1,-1)$)",
    r"$B_1$", r"$B_2$", r"$B_3$",
)
draw_axes_lines(ax2)
Q_r = np.linalg.norm(Q_xyz, axis=-1)
Q_dev = Q_r - R_Q
draw_ellipsoid(ax2, Q_xyz, Q_dev, cmap_name="RdBu_r")
draw_principal_axes_labels(ax2, eigQB, vecQB, Q_semi)
draw_optical_axis(ax2, length=Q_semi.max() * 1.15)

# ─── Captions ───────────────────────────────────────────────────────────────
fig.suptitle(
    r"Dual anisotropy: kinematic ($M$, $k$-space) and gauge sector ($\mathbf{Q}$, $B$-space)"
    "\n"
    r"share the same optical axis $\mathbf{V}_1+\mathbf{V}_2+\mathbf{V}_3=(1,1,-1)$",
    y=1.05, fontsize=11,
)
fig.text(
    0.5, -0.04,
    r"Both surfaces are level sets at $x^T A\,x = 3$.  In the kinematic sector ($A = M$, eigenvalues $\{4,4,1\}$) "
    r"the long ellipsoid axis lies along $(1,1,-1)$: dispersion is $\mathit{flat}$ along the optical axis and "
    r"$\mathit{steep}$ in the perpendicular plane.  In the gauge sector ($A = \mathbf{Q}$, eigenvalues $\{4,4,16\}$) "
    r"the short axis lies along $(1,1,-1)$: the photon kinetic term is $\mathit{steepest}$ along the axis and "
    r"$\mathit{flatter}$ perpendicular -- the dual phenomenology.  Same geometry, dual shapes; one optical axis, "
    r"two falsifiable signatures (P7 plus the gauge-sector birefringence in App.~B).",
    ha="center", va="top", fontsize=8.5, wrap=True,
)

# ─── Save ───────────────────────────────────────────────────────────────────
out_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "..", "..", "figures"))
os.makedirs(out_dir, exist_ok=True)
png = os.path.join(out_dir, "induced_action_ellipsoid.png")
pdf = os.path.join(out_dir, "induced_action_ellipsoid.pdf")
fig.savefig(png, dpi=180, bbox_inches="tight")
fig.savefig(pdf, bbox_inches="tight")
print(f"Saved: {png}")
print(f"Saved: {pdf}")

# ─── Numeric output ─────────────────────────────────────────────────────────
data_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "..", "..", "data"))
os.makedirs(data_dir, exist_ok=True)
out_txt = os.path.join(data_dir, "induced_action_ellipsoid.txt")
with open(out_txt, "w") as f:
    f.write("# induced_action_ellipsoid.py output\n\n")
    f.write("# Kinematic-sector tensor (M) in k-space\n")
    f.write("M =\n" + np.array2string(M_kinematic) + "\n\n")
    f.write(f"M eigenvalues (desc): {eigM}\n")
    f.write("M eigenvectors (cols):\n" + np.array2string(vecM, precision=6) + "\n")
    f.write(f"M semi-axes  (k^T M k = {C_LEVEL:.1f}): {M_semi}\n\n")

    f.write("# Gauge-sector tensor (Q) in F-space\n")
    f.write("Q =\n" + np.array2string(Q_gauge) + "\n\n")
    f.write(f"Q eigenvalues (desc): {eigQ}\n")
    f.write("Q eigenvectors (cols, F-basis):\n" + np.array2string(vecQ, precision=6) + "\n\n")

    f.write("# Hodge dual: F-space -> B-space\n")
    f.write("P (B -> F) =\n" + np.array2string(P) + "\n\n")
    f.write("Q in B-space = P^T Q P =\n" + np.array2string(Q_in_B) + "\n\n")
    f.write(f"Q (B-space) eigenvalues (desc): {eigQB}\n")
    f.write("Q (B-space) eigenvectors (cols, B-basis):\n" + np.array2string(vecQB, precision=6) + "\n")
    f.write(f"Q semi-axes (B^T Q B = {C_LEVEL:.1f}): {Q_semi}\n\n")

    f.write(f"Overlap |<eigvec(lambda=16), V1+V2+V3 / sqrt(3)>| = {overlap:.6f}\n")
    f.write("(Should be 1.0 if the gauge-sector optical axis is exactly (1,1,-1).)\n")

print(f"Saved: {out_txt}")
