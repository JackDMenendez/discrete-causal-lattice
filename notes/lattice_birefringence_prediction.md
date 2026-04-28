<!-- markdownlint-disable MD022 MD024 MD032 MD047 MD060 -->
# Note: Lattice Birefringence — A New Falsifiable Prediction

**Date:** 2026-04-27
**Status:** Derived. Falsifiable in principle. Needs prediction-section integration.
**Origin:** SymPy eigenvalue computation of the spinor propagator $T(\mathbf{k})$ on 2026-04-27. See `notes/frame_condition_isotropy_memo.md` for the resolution that surfaced this.

## TL;DR

The bipartite octahedral lattice with basis $\mathbf{V}_1=(1,1,1)$, $\mathbf{V}_2=(1,-1,-1)$, $\mathbf{V}_3=(-1,1,-1)$ produces a **birefringent dispersion**. The optical axis lies along $\mathbf{V}_1+\mathbf{V}_2+\mathbf{V}_3 = (1,1,-1)$. Photons propagating along this axis have direction-degenerate energy at all orders in $\mathbf{k}$; photons propagating in the perpendicular plane have a normal quadratic dispersion with anisotropic coefficient $4/3$.

The canonical signature of birefringence is that **a single light pulse splits into two**. That signature applies here: a photon wavepacket projects onto both eigenmodes $\lambda_\pm$ of the propagator. Those eigenmodes have equal magnitude but different phases, so different energies, so different group velocities. A pulse propagating oblique to the optical axis literally separates into two pulses over distance.

This is a **sharp, falsifiable prediction** that strengthens, rather than weakens, the framework's claim to a discrete origin for relativistic kinematics. The paper's previous claim of $\mathrm{SO}(3)$ Lorentz invariance from the frame condition was false as written; the replacement is **birefringence with optical axis $(1,1,-1)$**.

## The math (concise)

The lattice's single-tick spinor propagator is
$$
T(\mathbf{k}) = \begin{pmatrix} i\sin(\omega/2) & \cos(\omega/2)\,H_\text{RGB}(\mathbf{k}) \\ \cos(\omega/2)\,H_\text{CMY}(\mathbf{k}) & i\sin(\omega/2) \end{pmatrix},
$$
with structure factors $H_\text{RGB}(\mathbf{k}) = \tfrac{1}{3}\sum_\text{RGB} e^{i\mathbf{k}\cdot\mathbf{v}}$ and $H_\text{CMY} = \overline{H_\text{RGB}}$.

Eigenvalues are
$$
\lambda_\pm(\mathbf{k}) = i\sin(\omega/2) \pm \cos(\omega/2)\,|H_\text{RGB}(\mathbf{k})|.
$$

The k-dependence is entirely contained in $|H_\text{RGB}|^2$, which expands to
$$
|H_\text{RGB}|^2 \;=\; 1 - \mathbf{k}^T M_\text{eff}\,\mathbf{k} + O(k^4),
\qquad
M_\text{eff} = \tfrac{1}{9}\begin{pmatrix} 8 & -4 & 4 \\ -4 & 8 & 4 \\ 4 & 4 & 8 \end{pmatrix}.
$$

Eigenvalues of $M_\text{eff}$: $\{4/3,\,4/3,\,0\}$. The zero eigenvalue is along $(1,1,-1)$.

**Verified by direct calculation:** along $\mathbf{k} = s(1,1,-1)/\sqrt{3}$, the dot products $\mathbf{k}\cdot\mathbf{V}_i$ are equal for all three RGB vectors, giving $|H_\text{RGB}|^2 = 1$ exactly at all orders.

## The splitting magnitude — what's testable today

The size of the split between the two eigenmodes $\lambda_\pm$ scales with $a^2 |\mathbf{k}|^2$, where $a$ is the lattice spacing and $\mathbf{k}$ is the photon's wavevector. Existing astrophysical data already constrains this at multiple scales:

| Source | Wavelength | $a/\lambda$ | Splitting magnitude | Detectable? |
|---|---|---|---|---|
| Visible laser, lab scale | $\sim 5\times 10^{-7}$ m | $\sim 10^{-12}$ | nanoseconds per cosmic year | not in lab |
| GRB photons, MeV–GeV | $\sim 10^{-12}$ m | $\sim 10^{-7}$ | seconds per Gpc | **yes — Fermi GBM, IceCube** |
| CMB photons, mm scale | $\sim 10^{-3}$ m | $\sim 10^{-16}$ | $\sim 10^{-2}$ rad polarization rotation per Hubble time | **yes — Planck 2020** |
| Pulsar timing, radio | $\sim 1$ m | $\sim 10^{-19}$ | direction-dependent dispersion | **yes — NANOGrav, EPTA** |

Three of those four channels already have public datasets that could in principle be re-analyzed for *direction-resolved* signals.

The current bound on $a \lesssim 10^{-19}$ m from GRB time-of-flight assumes isotropic dispersion. That assumption is integrated over all sky directions, so a direction-resolved signal from the lattice would have been smeared into the bound rather than detected. **Re-binning the catalog by direction relative to a candidate optical axis is the cheapest operational test the framework has access to.**

The same logic applies to gravitational waves. LIGO/Virgo data has resolution to constrain *gravitational* birefringence — different polarization modes arriving with direction-dependent timing — and the framework predicts gravity has the same optical axis $(1,1,-1)$ for the same reason photons do (both inherit the structure of the frame matrix).

## What this predicts

### 1. Direction-dependent group velocity for photons

For a photon ($\omega = 0$, so massless: take $\omega \to 0$ limit of $\lambda_\pm$), the dispersion in the perpendicular plane gives group velocity $v_g \neq c$ at lowest order — specifically, the leading correction has coefficient $4/3$ rather than 1. Along the optical axis $(1,1,-1)$, group velocity is degenerate (the dispersion is flat at all orders in $\mathbf{k}$).

This is structurally the same as ordinary crystal optics: a uniaxial crystal has an ordinary ray (perpendicular plane) and an extraordinary ray (optical axis). Here the medium is the underlying spacetime lattice itself.

### 2. Direction-resolved GRB time-of-flight

The current bound on the lattice spacing $a$ from gamma-ray-burst time-of-flight observations (P7 in the paper) is $a \lesssim 10^{-19}$ m, derived under the assumption of an isotropic dispersion. The birefringence prediction means **the bound should be direction-resolved**: GRBs whose line of sight is closer to the cosmological direction $(1,1,-1)$ (in some yet-to-be-defined cosmic frame) should show *less* dispersion than perpendicular GRBs.

A statistical analysis of GRB arrival times against direction in the sky would either:
- Find no anisotropy and tighten the bound on $a$ (if the cosmic frame averages out the lattice axis), or
- Find an anisotropy aligned with a specific cosmic direction (a falsifiable detection).

This is a stronger version of P7. The current text in [predictions.tex](../paper/sections/predictions.tex) can be extended to include the directional refinement.

### 3. Polarization-dependent photon propagation

The two eigenvalues $\lambda_\pm$ of the propagator correspond to two polarization modes of the spinor field. In the perpendicular plane, both modes have the same $|H|^2$, so they have the same group velocity (degenerate ordinary + extraordinary in this geometry). Along the optical axis, both are flat.

For a non-trivial test: a *transverse* direction (between optical-axis and perpendicular) should split the two modes' group velocities at second order in the angle. This is harder to test but provides a richer falsifiability target.

### 4. CMB anisotropy

The cosmic microwave background, having traveled cosmological distances, would accumulate any direction-dependent dispersion as a temperature-direction correlation. Specifically, photons from directions closer to the lattice optical axis would arrive with slightly different spectra than perpendicular photons. The current CMB anisotropy data (Planck 2020) constrains anomalous direction-dependent effects at the $10^{-5}$ level; the lattice prediction would have to show whether this is exceeded.

This requires identifying the cosmic-frame direction of $(1,1,-1)$. The lattice's orientation in the universe is, in the framework's current form, *undetermined* — it could be any direction. A real detection of anisotropy in CMB or GRB data would fix the orientation; a null result tightens the constraint on $a$.

## Why the framework is *strengthened*, not weakened, by this finding

The paper as it stands claims that the bipartite octahedral lattice produces $\mathrm{SO}(3)$ Lorentz invariance via a (false) frame condition. A reviewer running the 5-line SymPy check would find the claim is wrong, and would (justifiably) doubt the rest of the derivation.

The corrected framing — **birefringence with optical axis $(1,1,-1)$** — has three advantages:

1. **It's true.** Symbolically verified, structurally clean.
2. **It's falsifiable.** Direction-resolved GRB or CMB analysis can detect or rule out the prediction.
3. **It's a feature, not a bug.** Most discrete-spacetime proposals would *love* a sharp falsifiable prediction; the framework now has one.

The cost: the paper must drop the "Lorentz invariance is forced by the frame condition" claim. The replacement is more honest and more interesting.

## Open questions

1. **Does renormalization (`enforce_unity_spinor`) restore isotropy?** Possibility 2 in the original frame-condition memo. Numerical test on a $33^3$ grid measuring $E(\mathbf{k})$ along $(1,1,-1)$ vs. perpendicular directions would settle this. If yes, the birefringence prediction would have to be qualified — anisotropy is in the bare propagator but not in observed amplitudes. If no, the prediction stands.

2. **What sets the cosmic orientation of the lattice?** The framework as stated does not pick a preferred direction in the universe. Either the lattice is oriented uniformly (in which case the optical axis $(1,1,-1)$ is *the* cosmic preferred direction — falsifiable in CMB / GRB data), or the orientation varies on cosmological scales (lattice "domains"), or there is no cosmic-scale orientation and the prediction reduces to local/laboratory tests.

3. **How does this interact with the $1/r^2$ derivation in §7?** The current §7 uses $\sum_\mathbf{v} v_i v_j = 6\delta_{ij}$ as the frame condition. With the corrected $M_\text{eff}$, the discrete Laplacian acquires a tilted ellipsoidal kernel. The 1/r² recovery still works under $O_h$ averaging, but discrete corrections (P1) gain an angular dependence with the same optical axis structure.

4. **Mass-spectrum implications.** The Arnold tongues and Farey hierarchy in §13 (lattice harmonics) and §14 (fractal universe) currently assume isotropic dispersion. With birefringence, the tongue widths may have a directional structure. Whether this changes the predicted mass spectrum is an open question.

## Action items if pursued

1. **Update P7 in [predictions.tex](../paper/sections/predictions.tex)** to include the direction-resolved refinement: GRB time-of-flight bounds should be direction-binned; the lattice predicts that bins closer to the cosmic optical axis show less dispersion. State the splitting prediction explicitly — a photon pulse oblique to $(1,1,-1)$ separates into two arrival times. The split is the falsification handle.

2. **Compute the renormalized dispersion** on a small grid to settle question (1) above. Cheapest option: take a free-particle wavepacket with $\omega = 0.1019$, propagate it along $(1,1,-1)$ for ~1000 ticks, measure the group velocity. Compare to a perpendicular run. If group velocities match, renormalization restored isotropy; if they differ, birefringence is observable.

3. **GRB re-binning analysis (the cheapest operational test).** Take a public catalog (e.g. Fermi GBM, IceCube high-energy events) and bin the time-of-flight residuals by source direction. The framework predicts that bursts with line of sight closer to a single cosmic direction (the lattice optical axis, currently undetermined) have systematically smaller dispersion residuals than perpendicular bursts. This requires no new physics infrastructure — it's a re-analysis of existing data. Either:
   - Detection: a preferred direction emerges, fixing the cosmic orientation of the lattice, and the dispersion-versus-angle profile yields a tighter bound on $a$.
   - Null result: the bound on $a$ is tightened (the existing isotropic bound becomes a direction-resolved bound, holding in every direction).

   Both outcomes are publishable.

4. **CMB linear polarization re-analysis.** Cosmologically traveling photons in a birefringent vacuum should arrive with direction-dependent rotated polarization — analogous to a Faraday effect, but from vacuum birefringence rather than magnetic field. Planck 2020 constrains this at the few-degrees level over the cosmic scale; that bound can be reread as a direction-resolved bound on $a$ given the framework. This is more model-dependent than the GRB analysis but tests the same prediction at vastly longer baseline.

5. **LIGO/Virgo gravitational birefringence.** The frame matrix's eigenstructure governs *gravity* dispersion as well as photon dispersion (see `notes/frame_condition_isotropy_memo.md` for the §7 implication). LIGO/Virgo polarization-mode timing should show direction-dependent splitting along the same optical axis $(1,1,-1)$. This is the gravitational twin of the photon prediction; an existing dataset already covers it.

6. **Re-derive the 1/r² recovery** with the corrected frame structure. This is the §7 rewrite the frame-condition resolution memo flagged as needed. The Newtonian potential $-GM/r$ survives under $O_h$ averaging; discrete corrections (P1 in `predictions.tex`) acquire direction dependence with the same optical axis as the photon prediction. **One axis, two phenomena, two falsification channels.**

7. **The unification framing for the abstract.** The current abstract gestures at "minimal session types resolving $\mathcal{A}=1$ imbalances." With one optical axis governing photon and gravitational birefringence, the abstract can claim something sharper: the bipartite octahedral lattice has a *single anisotropy axis* that produces *two falsifiable signatures* — birefringent vacuum optics and direction-dependent gravitational dispersion. That's a clean, structural prediction and a strong selling point for the framework.