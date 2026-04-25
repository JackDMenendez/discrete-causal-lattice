# Paper Completion Todo List
## Geometry First: Quantum Mechanics, Gravity, and the Origin of the Standard Model from a Single Conservation Law

**Date:** April 25, 2026  
**Version:** Working Paper 0.9  
**Status:** 90% Complete - Major theoretical derivations done, experiments validated

---

## 🔥 Critical Missing Sections (STUB Status)

### 1. Complete the Predictions Section (MOST IMPORTANT)
**File:** `paper/sections/predictions.tex`  
**Status:** STUB - only outlines exist  
**Required:** Write falsifiable predictions with numerical specificity  

**Key Predictions from `notes/falsifiable_predictions.md`:**

#### Prediction 1: Discrete 1/r² Corrections
- **Claim:** Exact path count P(N, dx, dy, dz) deviates from Gaussian at small N
- **Implication:** Calculable correction to standard 1/r² falloff
- **Crossover Scale:**
  - Planck calibration: ~10 Planck lengths (unmeasurable)
  - Compton calibration: ~10 Compton wavelengths (~10^-11 m)
- **Measurable via:** Precision hydrogen spectroscopy, Casimir effect
- **Status:** Needs `count_paths()` implementation for numbers

#### Prediction 2: Minimum Time Dilation Quantum
- **Claim:** One extra clock = one tick_duration of scheduler overhead
- **Formula:** δt_min = tick_duration_s for chosen calibration
- **Current Tech:** Optical atomic clocks ~10^-18 fractional sensitivity at mm separation
- **Scales:**
  - Planck: δt_min = 5.4×10^-44 s (unmeasurable)
  - Compton: δt_min = ~8×10^-21 s (possibly within reach)
- **Status:** Needs calibration table completion

#### Prediction 3: Octahedral Anisotropy
- **Claim:** 6 preferred axes break perfect isotropy at sub-crossover scales
- **Observable as:** Directional correlations in CMB or atomic clock comparisons
- **Status:** Speculative, needs theoretical development

#### Prediction 4: Decay Rate Clock-Density Correction
- **Claim:** Particle decay timing-dependent beyond special relativity
- **Prediction:** Additional correction term in decay rates near massive objects
- **Measurable via:** Precision lifetime measurements in different gravitational potentials
- **Status:** Needs tick_scheduler decay model

### 2. Complete Phase Propagation Section
**File:** `paper/sections/phase_propagation.tex`  
**Status:** STUB after subsection 5.2  
**Required:** Write remaining subsections on phase dynamics

### 3. Complete Lattice Harmonics Section
**File:** `paper/sections/lattice_harmonics.tex`  
**Status:** STUB - references `notes/lattice_harmonics.md`  
**Required:** Write prose connecting exp_09 results to theory

### 4. Complete Tick Scheduler Section
**File:** `paper/sections/tick_scheduler.tex`  
**Status:** STUB after basic description  
**Required:** Write detailed scheduler mechanics

### 5. Complete Vacuum Twist Field Equations
**File:** `paper/sections/vacuum_twist_field_equations.tex`  
**Status:** STUB after subsection 7.4  
**Required:** Write remaining field theory development

### 6. Complete Interference Section
**File:** `paper/sections/interference.tex`  
**Status:** PARTIAL - figure exists, prose stub  
**Required:** Write Huygens lantern interference theory

---

## 📊 Missing Theoretical Results (Audit Table STUBs)

### 7. Complete Theoretical Derivations
**File:** `paper/sections/audit_table.tex` (lines 103, 108, 125)  
**Required Derivations:**
- Photon emission as A=1 necessity
- Bekenstein-Hawking entropy derivation
- Scheduler saturation at Planck density

---

## 🖼️ Figure and Visualization Tasks

### 8. Verify All Figures Exist and Are Referenced
**Present Figures:**
- causal_cone_screen.pdf/.png
- dirac_cones_doublepane.pdf/.png
- exp_00_cone_structure.pdf
- exp_03_lanterns.pdf/.png
- exp_08_deflection.gif, exp_08_emission.gif
- exp_12_twobody_scan.pdf
- lattice_drawio.png
- exp_harmonic_hires.pdf/.png

**Check:** All .tex files in `figures/` directory reference existing images

### 9. Create Missing Figures
- Phase rotor diagram (referenced but may need updating)
- Any figures referenced in STUB sections

---

## 🔧 Build and Compilation

### 10. Fix Paper Build System
**Issue:** `makefile.mak` missing, build scripts failing  
**Required:** Fix build.cmd/build.sh to work with current directory structure  
**Goal:** Successfully compile main.pdf

### 11. Update Paper Version and Status
**Current:** "Working Paper -- Version 0.9"  
**Required:** Update to final version when complete  
**Remove:** DOI placeholder when publishing

---

## 📚 Bibliography and References

### 12. Complete Bibliography
**File:** `paper/paper-bib/references.bib`  
**Required:** Verify all citations in paper have entries  
**Add:** Any missing references for new content

---

## ✅ Final Validation Tasks

### 13. Cross-Reference Validation
- Ensure all section references (\ref{}) point to existing labels
- Verify experiment citations match actual exp_XX names
- Check figure references match existing files

### 14. Content Consistency Check
- Verify all experiments cited in paper match PASS status in audit table
- Ensure theoretical claims match experimental results
- Cross-reference with CLAUDE.md status updates

### 15. Final Read-Through and Proofreading
- Grammar and clarity check
- Mathematical notation consistency
- Figure captions and table formatting

---

## 🎯 Priority Order

**Immediate (Blockers):** 1, 10  
**High:** 2, 3, 4, 5, 6  
**Medium:** 7, 8, 9, 11, 12  
**Low:** 13, 14, 15

---

## 📋 Key Notes Files for Reference

**Essential for Predictions Section:**
- `notes/falsifiable_predictions.md` - Specific falsifiable predictions with numbers
- `notes/follow_on_implications.md` - Future paper ideas and implications
- `notes/shortcomings_of_quantum_mathematics.md` - What the lattice framework fixes

**Useful Background Notes:**
- `notes/the_theme_of_the_paper.md` - Core reframing of QM axioms
- `notes/conservation_of_probability.md` - THE central claim: A=1 is the only conservation law
- `notes/deriving_dirac_from_hamiltonian.md` - 6-step continuum limit program
- `notes/deriving_dirac_the_significance.md` - Why the derivation changes everything
- `notes/lattice_harmonics.md` - For lattice harmonics section
- `notes/vacuum_twist_field_equations.md` - For vacuum twist section

---

## 📈 Current Completion Status

- ✅ **Major Theoretical Results:** All completed (Dirac derivation, A=1 conservation, etc.)
- ✅ **Experiments:** All 19 experiments PASS with comprehensive documentation
- ✅ **Core Paper Structure:** Main sections written with prose
- ❌ **Predictions Section:** STUB (most critical missing piece)
- ❌ **Build System:** Broken (immediate blocker)
- ✅ **Figures:** Most exist, need verification
- ✅ **Bibliography:** Needs final check

**Overall:** Paper is ~90% complete. Main remaining work is writing the predictions section and fixing the build system.</content>
<parameter name="filePath">c:\dev\dcl\PAPER_COMPLETION_TODO_PRINTABLE.md