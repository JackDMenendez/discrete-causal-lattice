# Utilities — A=1 Discrete Causal Lattice

Shared tools used by experiments, figure scripts, and the audit runner.
None of these files contain experimental results; they are infrastructure.

---

## Modules

| Module | Purpose | Used by |
| --- | --- | --- |
| lattice_calibrator.py | Maps lattice node spacing to physical units; derives falsifiable numerical predictions from the single calibration choice | exp_06, paper §9 |
| path_counter.py | Exact combinatorial path counting on T³_diamond; foundation of the discrete 1/r² corrections and CLT convergence test | exp_06 |
| visualizer.py | Shared academic-style plotting utilities; all experiment figures use these conventions | all experiments |
| plot_twobody_scan.py | Comparison figure: fixed-well k-scan (exp_11) vs two-body k-scan (exp_12); shows the 7.3% → 0.01% correction from adding a live proton | exp_12 (via `--fig`), Makefile |
| plot_quantization_scan.py | Spontaneous quantization heatmap figure for exp_11; 2D PDF heatmap + score overlay; the paper figure for Arnold tongue lock-in | exp_11, Makefile |
| dirac_cones_doublepane.py | Double-pane paper figure: raw harmonic landscape (left) + Dirac cone annotations + graphene K-point inset (right); the three 2:1/3:1/4:1 crossings | paper §harmonics |
| dirac_cones_overlay.py | Single-pane overlay: harmonic heatmap + Dirac cone annotations; intermediate between sketch and doublepane | paper §harmonics |
| dirac_cones_sketch.py | Schematic of the three Dirac-like crossings in (f, ω) space; white-background, print-friendly | paper §harmonics |
| exp_03_lanterns.py | Double-slit interference figure (Huygens Lantern): coherent vs decoherent 2D probability density from lattice dynamics alone | paper §interference |
| phase_oscillator_diagram.py | Two-panel U(1) phase oscillator figure: group/algebra geometry (clock hand) + probability geometry (p_hop / p_stay projection) | paper §kinematics |
| probe_exp18_settle.py | Quick diagnostic: does the PDF peak metric detect r~R1 during an oscillating exp_18 orbit? | exp_18 development |
| probe_exp18_settle2.py | Validates the settle criterion: time-averaged electron density (last 1000/3000 ticks) peaks near R1 | exp_18 development |
| probe_exp18_stability.py | 5000-tick stability diagnostic for exp_12 best case (k=0.0970); measures first-escape tick and windows within 20% of R1 | exp_18 development |
| probe_predictor_corrector.py | Three-scheme Coulomb update comparison (before-tick / after-tick / midpoint average) run in parallel; tests whether mean-field lag drives orbital instability | exp_18 development |
| probe_stability_launch.py | Launcher: spawns 13 parallel stability workers across k-sweep (10 values) and update-lag test (4 values) | exp_18 development |
| probe_stability_worker.py | Parameterised worker called by probe_stability_launch; runs one (k_init, update_every) trial and writes log + npy to data/ | exp_18 development |

---

## lattice_calibrator.py

Determines all physical-unit predictions from a single free parameter: the
lattice node spacing `dx`.  Once `dx` is fixed by matching the electron
Compton wavelength, every other prediction follows with no further tuning.

Key outputs:

- `dx`, `dt` in SI units
- Bohr radius in lattice nodes
- Hydrogen ground-state energy in eV
- Table of falsifiable predictions (paper §9)

Paper reference: Section 9 (calibration table).

---

## path_counter.py

Pure combinatorics — no physics assumptions.  Counts the exact number of
N-step paths on T³_diamond from the origin to displacement (dx, dy, dz).

- For large N: converges to Gaussian → standard 1/r² law.
- For small N: discrete deviations are specific, calculable predictions.

Results cached with `lru_cache`; safe to call repeatedly.

Paper reference: Section 9 (falsifiable discrete corrections, exp_06).

---

## visualizer.py

Matplotlib / seaborn wrappers enforcing consistent figure style across all
experiments.  All figures are saved at 300 DPI with serif fonts.

Key functions:

- `plot_probability_density_3d_slice` — 2D slice of |ψ|² at fixed axis
- Further helpers for phase fields, CoM trajectories, and scan heatmaps

---

## plot_twobody_scan.py

Reads `quantization_scan_n1_focused.npy` (exp_11) and
`exp_12_twobody_scan.npy` (exp_12) and produces the side-by-side comparison
figure showing how the live proton shifts k_min from 0.0900 to 0.0970.

```
python src/utilities/plot_twobody_scan.py --datadir data --out figures/exp_12_twobody_scan.pdf
```

Also invoked automatically by exp_12 when run with `--fig`.

---

## plot_quantization_scan.py

Reads `quantization_scan_n1.npy` and optionally `quantization_scan_n2.npy`
(both from exp_11) and produces the Arnold tongue heatmap figure.

```
python src/utilities/plot_quantization_scan.py --datadir data --out figures/quantization_scan.pdf
python src/utilities/plot_quantization_scan.py --n1            # n=1 panel only
python src/utilities/plot_quantization_scan.py --no-heatmap    # score-only fallback
```

---

## dirac_cones_doublepane.py

Double-pane paper figure for the harmonic landscape section.  Reads
`data/exp_harmonic_hires_powermap.npy` (generated by exp_09c).

- Left panel: raw harmonic hires heatmap — warmth IS probability density (A=1)
- Right panel: same heatmap + Dirac cone overlays + graphene K-point inset
- Three crossings: 2:1 (ω=π/2), 3:1 (ω=π/3), 4:1 (ω=π/4)

```
python src/utilities/dirac_cones_doublepane.py
```

Saves: `figures/dirac_cones_doublepane.pdf` + `.png`

---

## dirac_cones_overlay.py

Single-pane overlay of the harmonic heatmap with Dirac cone annotations
and a graphene inset.  Falls back to blank axes if the data file is absent.
Intermediate figure between the sketch and the doublepane.

```
python src/utilities/dirac_cones_overlay.py
```

Saves: `figures/dirac_cones_overlay.pdf` + `.png`

---

## dirac_cones_sketch.py

Schematic of the three Dirac-like crossings in (f, ω) space — no data file
required.  White background, print-friendly; useful before exp_09c has run.

```
python src/utilities/dirac_cones_sketch.py
```

Saves: `figures/dirac_cones_sketch.pdf` + `.png`

---

## exp_03_lanterns.py

Double-slit interference figure (the Huygens Lantern).  Runs lattice
dynamics via `tick()` from two coherent point sources; no analytical formula.

- Left panel: coherent sources — bright interference fringes
- Right panel: decoherent (observer at slit A) — fringes collapse

```
python src/utilities/exp_03_lanterns.py
```

Saves: `figures/exp_03_lanterns.pdf` + `.png`

---

## phase_oscillator_diagram.py

Two-panel figure of the U(1) phase oscillator for the kinematics section.

- Left: group/algebra geometry — oscillator as clock hand on U(1), ω as arc
- Right: probability geometry — δφ/2 projects onto p_hop and p_stay

```
python src/utilities/phase_oscillator_diagram.py
```

Saves: `figures/phase_oscillator_diagram.pdf` + `.png`
