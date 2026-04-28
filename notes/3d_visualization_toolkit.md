<!-- markdownlint-disable MD022 MD024 MD032 MD047 MD060 -->
# Note: A 3D Visualization Toolkit for the Framework

**Date:** 2026-04-27
**Status:** Action seed. Each item below is a candidate figure. The frame-matrix ellipsoid (2026-04-27) is the first concrete instance and proved out the value.

## Why this matters

The framework is irreducibly three-dimensional. The lattice is 3D, the bipartite RGB/CMY structure is 3D, the causal cone is 3D (an expanding octahedron, not a sphere), the frame matrix is 3D, and every experiment runs on a 65³ grid. Most existing visualizations project to 2D and lose geometric content. The frame-matrix ellipsoid figure made visible an anisotropy aligned with $\mathbf{V}_1 + \mathbf{V}_2 + \mathbf{V}_3$ that had been hiding inside the linear algebra for the entire writing of the paper — the eigenvalues are $\{4, 4, 1\}$, the long axis lies exactly along the RGB-basis sum, and reading the matrix as a 3D shape reframes how the anisotropy must be addressed in the paper.

There is no reason to expect this is the only thing hiding. Several other places in the framework are intrinsically 3D and should be rendered as 3D figures.

## What to build

A small `src/utilities/visualize_3d.py` module that wraps matplotlib's 3D backend (and, where higher quality matters, plotly or mayavi) into a handful of reusable functions:

- `render_quadratic_form(M, level, ax)` — draws the level set $k^T M k = c$ as a surface, with eigenvalues / principal axes annotated. The frame-matrix figure is the prototype.
- `render_lattice_neighborhood(center, radius)` — draws the bipartite RGB/CMY structure as colored nodes with edges, optionally labelled with basis vectors.
- `render_causal_cone(N_ticks)` — draws the expanding octahedron at successive ticks, with each shell's path-count integers as colored densities.
- `render_volume_isosurface(rho, level, ax)` — draws an isosurface of a 3D scalar field (e.g. $\rho_\text{clock}$, $|\psi|^2$). Takes the .npy arrays the experiments already produce.
- `render_orbit_animation(traj_p, traj_e, frames)` — animates two-body orbital trajectories with the electron PDF rendered as volumetric mist around the proton.
- `render_phase_field(psi_R, psi_L, slab)` — for a 2D slice through the lattice, render the spinor field as colored arrows with amplitude and phase.

Each function takes the same kind of array the experiments already write to `data/*.npy`, so wiring them in costs only the call site. Output goes to `figures/*.png` and `figures/*.pdf` for paper inclusion, and optionally to `figures/*.html` for interactive plotly versions.

## Candidate figures with high "hiding" potential

In rough order of expected leverage:

1. **The Brillouin zone for the bipartite octahedral lattice.** Currently nowhere in the paper as a 3D figure. The folded zone of the bipartite structure should make the photon dispersion (P7 in `predictions.tex`) visualizable as cones in the corners. Comparison to graphene (which the dirac_cones figure currently does in 2D) should be 3D for honesty.

2. **The two-tick propagator's eigenvalue surfaces.** Plot $|\lambda_\pm(\mathbf{k})|$ as a 3D surface over the Brillouin zone. If the surface is spherical (isotropic), possibility 1 in the frame-condition memo is correct and the paper's claim survives. If the surface is a tilted ellipsoid (matching the frame matrix), the anisotropy is real at the operator level and the paper needs a different argument.

3. **The clock-density field around a mass source.** $\rho_\text{clock}(\mathbf{x})$ on the 3D grid for a Coulomb / gravitational well. Show the saturation level set $\rho = \ell_P^{-3}$ as an isosurface — the event horizon as a 3D shell. Connects to §7.5 / §7.6 and the Moore's-law uncertainty seed (`notes/clock_density_uncertainty_and_entropy.md`).

4. **The virtual-session cloud around a proton.** Source at center, virtual session amplitude as a volumetric density falling off with $\exp(-\phi/c^2)$. This is the figure the virtual-session note (`notes/virtual_sessions_as_gradient_field.md`) really needs to make the picture concrete.

5. **The exp_19 / exp_19c orbital dynamics.** Three sessions (proton, electron, photon), each with a 3D probability distribution evolving over time. The current scalar `r_peak` time series tells us nothing about *what's actually wrong* when the orbit fails to lock. A 3D animation of $|\psi_e|^2(\mathbf{x}, t)$ would tell us in seconds whether the electron PDF is bouncing, spreading, shelling, or doing something stranger.

6. **The 6 basis vectors as a 3D bipartite scaffold.** RGB and CMY coloured arrows from origin, edges showing the same-sublattice exclusion forbidding certain hops. Forms the foundation for any teaching figure of the lattice.

7. **The harmonic landscape with $k$ added.** Currently 2D in $(f, \omega)$ with Arnold tongues. Adding a third axis $|\mathbf{k}|$ would let us see the tongue *cones* (Dirac cones) extending into momentum space. The dirac_cones_doublepane figure currently shows a 2D projection of this; the 3D version is more honest.

8. **The path-count distributions.** $P(N, a, b, c)$ as integer values on the 3D causal cone for fixed $N$. Shows the deviation from the central limit theorem Gaussian at small $N$ — exactly the falsifiable regime in P1 of `predictions.tex`. Currently presented as scalar tables; visualizing the actual 3D distribution would make discrete corrections visible as bumps and depressions on the cone.

## Cost estimate

For the toolkit module + the first three figures (Brillouin zone, eigenvalue surfaces, clock-density saturation): roughly one focused day. The frame-matrix figure took about an hour from "let's do it" to "saved and the eigenvalues taught me something" — the toolkit just removes the per-figure boilerplate.

For the full set of 8 figures: probably a week, but each one is independent and incremental, so it can be paced. Most of them double as paper figures and as teaching figures for talks.

## Implementation hints

- matplotlib 3D is acceptable for static figures. Mathtext doesn't support `\begin{pmatrix}` — keep math expressions simple, put the matrix in the caption rather than the title.
- For volumetric data on a 65³ grid, use `marching_cubes` from `scikit-image` or `mayavi.mlab.contour3d`. matplotlib's `voxels` is too slow for grids that large.
- Plotly is the right choice for any figure that benefits from rotation / zoom (most of these). Static export via kaleido produces clean PDFs.
- Save both an `.html` (interactive) and `.pdf` (paper) version when feasible. The interactive versions can be linked from the Code & Data appendix.

## Connection to existing infrastructure

- The Code & Data appendix already lists `src/utilities/` as a place where reproducibility scripts live. The visualization toolkit fits there naturally.
- Each figure-generating script should mirror `frame_matrix_visualization.py`'s structure: deterministic inputs, both `.png` and `.pdf` output, captured numerical output to `data/`. That keeps the appendix's reproducibility claim intact.
- The `figures/` directory is the natural target. Existing figures use a mix of formats; staying with `.pdf` + `.png` + optional `.html` keeps the conventions clean.
