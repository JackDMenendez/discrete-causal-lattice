"""
frame_matrix_visualization.py

Side-by-side 3D rendering of two quadratic forms in k-space:

  Left  panel: M_claimed = 3 * I             -> sphere
  Right panel: M_actual  = sum_{v in RGB} v v^T -> tilted ellipsoid

This figure makes visible what the abstract / conclusion sentence

    "the frame condition sum_{RGB} v_i v_j = 3 delta_ij"

actually claims (the sphere) versus what the basis
V1=(1,1,1), V2=(1,-1,-1), V3=(-1,1,-1) actually yields (the ellipsoid).

The level set drawn in both cases is k^T M k = 3, so the sphere has
radius 1 and the ellipsoid has the same characteristic scale; differences
in shape are pure geometry, not normalization.

Output: figures/frame_matrix_ellipsoid.{png,pdf}

Run:
    python -u src/utilities/frame_matrix_visualization.py
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless render
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registers projection)
from mpl_toolkits.mplot3d.art3d import Line3DCollection

# ─── Frame matrices ──────────────────────────────────────────────────────────
V1 = np.array([1,  1,  1])
V2 = np.array([1, -1, -1])
V3 = np.array([-1, 1, -1])
RGB = np.array([V1, V2, V3])

M_actual  = sum(np.outer(v, v) for v in RGB)
M_claimed = 3 * np.eye(3)

print("M_actual =\n", M_actual)
print("M_claimed =\n", M_claimed)
print()

# Eigendecomposition of the actual frame matrix
eigvals, eigvecs = np.linalg.eigh(M_actual)
order = np.argsort(eigvals)[::-1]   # descending
eigvals = eigvals[order]
eigvecs = eigvecs[:, order]

print("Eigenvalues of M_actual (descending):", eigvals)
print("Sum of eigenvalues (= trace):", eigvals.sum(), "(matches trace =", np.trace(M_actual), ")")
print("Product of eigenvalues (= det):", np.prod(eigvals), "(matches det =", np.linalg.det(M_actual), ")")
print()
print("Principal axes (columns are eigenvectors):")
print(eigvecs)
print()

# ─── Build parametric surfaces ───────────────────────────────────────────────
# Both surfaces are level sets k^T M k = c with c = 3.
C_LEVEL = 3.0

# Unit sphere mesh
N_U, N_V = 60, 60
u = np.linspace(0, 2*np.pi, N_U)
v = np.linspace(0, np.pi,   N_V)
U, V = np.meshgrid(u, v)
sphere_pts = np.stack([
    np.cos(U) * np.sin(V),
    np.sin(U) * np.sin(V),
    np.cos(V),
], axis=-1)  # (N_V, N_U, 3)

# Sphere of radius sqrt(C_LEVEL/3) (so that k^T (3I) k = C_LEVEL)
r_sphere = np.sqrt(C_LEVEL / 3.0)
sphere_xyz = r_sphere * sphere_pts          # k^T M_claimed k = C_LEVEL

# Ellipsoid: parametrize a unit sphere, then map by eigendecomposition.
# k = R diag(1/sqrt(lambda_i)) * sqrt(c) * unit_sphere_point
# satisfies k^T M k = c.
semi_axes = np.sqrt(C_LEVEL / eigvals)  # along principal directions
# Apply diagonal scale, then rotate (eigvecs cols are basis directions)
unit = sphere_pts                                  # (N_V, N_U, 3)
ellip_local  = unit * semi_axes                    # broadcast -> (N_V, N_U, 3)
ellip_xyz    = ellip_local @ eigvecs.T             # rotate

# Color the ellipsoid by signed deviation from a sphere of equal volume,
# so that the eye sees where the bulge is.
sphere_radius_eqvol = (np.prod(semi_axes)) ** (1.0/3)
ellip_r = np.linalg.norm(ellip_xyz, axis=-1)
ellip_dev = ellip_r - sphere_radius_eqvol           # negative = pinched, positive = bulged

# Limits used by both panels for fair comparison
EXTENT = max(r_sphere, semi_axes.max()) * 1.15

# ─── Plot ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(13, 6.0), constrained_layout=True)

# Common helpers
def style_axes(ax, title):
    ax.set_xlim(-EXTENT, EXTENT)
    ax.set_ylim(-EXTENT, EXTENT)
    ax.set_zlim(-EXTENT, EXTENT)
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlabel("$k_1$")
    ax.set_ylabel("$k_2$")
    ax.set_zlabel("$k_3$")
    ax.set_title(title, pad=8)
    # Light grid, neutral background
    ax.xaxis.pane.set_facecolor((1, 1, 1, 0.0))
    ax.yaxis.pane.set_facecolor((1, 1, 1, 0.0))
    ax.zaxis.pane.set_facecolor((1, 1, 1, 0.0))
    ax.view_init(elev=22, azim=35)

def draw_axes_lines(ax):
    """Faint coordinate axes through origin."""
    L = EXTENT * 0.95
    for vec in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
        v = np.array(vec) * L
        ax.plot([-v[0], v[0]], [-v[1], v[1]], [-v[2], v[2]],
                color="0.7", linewidth=0.6, zorder=0)

def draw_basis_vectors(ax):
    """Draw V1, V2, V3 as arrows from origin, plus their CMY mirrors."""
    rgb_colors = ["#d62728", "#2ca02c", "#1f77b4"]   # Red, Green, Blue
    cmy_colors = ["#9bd1ff", "#ffb3b3", "#ffd9b3"]   # mirror, lighter
    # Scale arrows so they fit inside the plot box
    scale = 0.85 * EXTENT / np.linalg.norm(RGB[0])  # all have |v|=sqrt(3)
    for i, v in enumerate(RGB):
        x, y, z = v * scale
        ax.quiver(0, 0, 0, x, y, z, color=rgb_colors[i],
                  linewidth=2.0, arrow_length_ratio=0.10)
    for i, v in enumerate(RGB):
        x, y, z = -v * scale
        ax.quiver(0, 0, 0, x, y, z, color=cmy_colors[i],
                  linewidth=1.5, arrow_length_ratio=0.10, alpha=0.8)

# ─── Left panel: claimed sphere (M = 3I) ─────────────────────────────────────
ax1 = fig.add_subplot(1, 2, 1, projection="3d")
style_axes(ax1, r"Claimed:  $M = 3\,\mathbb{I}$   $\Rightarrow$  sphere")
draw_axes_lines(ax1)
ax1.plot_surface(
    sphere_xyz[..., 0], sphere_xyz[..., 1], sphere_xyz[..., 2],
    color="#cccccc", alpha=0.55, linewidth=0.0, antialiased=True,
)
draw_basis_vectors(ax1)

# ─── Right panel: actual ellipsoid ───────────────────────────────────────────
ax2 = fig.add_subplot(1, 2, 2, projection="3d")
ax2_title = (r"Actual:  eigenvalues $\{4,4,1\}$   $\Rightarrow$  prolate ellipsoid")
style_axes(ax2, ax2_title)
draw_axes_lines(ax2)

# Colormap: blue = pinched (less than equal-volume sphere),
# red = bulged (more than equal-volume sphere). Magnitude uses absolute scale.
norm = plt.Normalize(vmin=-np.abs(ellip_dev).max(),
                     vmax= np.abs(ellip_dev).max())
ellip_colors = plt.cm.RdBu_r(norm(ellip_dev))

ax2.plot_surface(
    ellip_xyz[..., 0], ellip_xyz[..., 1], ellip_xyz[..., 2],
    facecolors=ellip_colors,
    alpha=0.85, linewidth=0.0, antialiased=True,
)
draw_basis_vectors(ax2)

# Annotate principal axes inside the ellipsoid
for i in range(3):
    direction = eigvecs[:, i]
    semi = semi_axes[i]
    a = direction * semi
    ax2.plot([-a[0], a[0]], [-a[1], a[1]], [-a[2], a[2]],
             color="black", linewidth=1.0, alpha=0.55, linestyle="--")
    # Label at the positive endpoint
    ax2.text(a[0]*1.08, a[1]*1.08, a[2]*1.08,
             rf"$\lambda_{{{i+1}}}={eigvals[i]:.3f}$",
             fontsize=8, ha="center", color="black")

# ─── Caption inside the figure ───────────────────────────────────────────────
fig.suptitle(
    r"Frame matrix as a quadratic form in $\mathbf{k}$-space, level set $k^T M\,k = 3$",
    y=1.02, fontsize=11,
)
# Detail caption below both panels
fig.text(
    0.5, -0.04,
    r"$M = \sum_{\mathrm{RGB}} \mathbf{v}\mathbf{v}^T$ for "
    r"$\mathbf{V}_1=(1,1,1),\ \mathbf{V}_2=(1,-1,-1),\ \mathbf{V}_3=(-1,1,-1)$. "
    r"The actual $M$ has off-diagonals $\{-1,+1,+1\}$ and eigenvalues "
    r"$\{4,4,1\}$; the long ellipsoid axis lies along "
    r"$\mathbf{V}_1+\mathbf{V}_2+\mathbf{V}_3=(1,1,-1)$.",
    ha="center", va="top", fontsize=9, wrap=True,
)

# ─── Save ────────────────────────────────────────────────────────────────────
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "..", "figures")
out_dir = os.path.normpath(out_dir)
os.makedirs(out_dir, exist_ok=True)

png = os.path.join(out_dir, "frame_matrix_ellipsoid.png")
pdf = os.path.join(out_dir, "frame_matrix_ellipsoid.pdf")
fig.savefig(png, dpi=180, bbox_inches="tight")
fig.savefig(pdf,            bbox_inches="tight")
print(f"Saved: {png}")
print(f"Saved: {pdf}")

# ─── Also write a small data file with the numerics ──────────────────────────
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "..", "data")
data_dir = os.path.normpath(data_dir)
os.makedirs(data_dir, exist_ok=True)
out_txt = os.path.join(data_dir, "frame_matrix_ellipsoid.txt")
with open(out_txt, "w") as f:
    f.write("# frame_matrix_ellipsoid.py output\n\n")
    f.write("M_actual:\n")
    f.write(np.array2string(M_actual) + "\n\n")
    f.write("Eigenvalues (descending): " + np.array2string(eigvals, precision=6) + "\n")
    f.write("Trace (sum of eigvals): " + f"{np.trace(M_actual):.6f}\n")
    f.write("Det   (prod of eigvals): " + f"{np.linalg.det(M_actual):.6f}\n\n")
    f.write("Eigenvectors (columns):\n")
    f.write(np.array2string(eigvecs, precision=6) + "\n\n")
    f.write("Semi-axes of ellipsoid k^T M k = 3:\n")
    f.write(np.array2string(semi_axes, precision=6) + "\n")
print(f"Saved: {out_txt}")
