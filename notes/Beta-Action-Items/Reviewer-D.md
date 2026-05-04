The v0.98-RC draft reads like a living research program with an audit trail attached, which is exactly the discipline a foundational claim needs. The audit-table governance, the explicit PASS / PART scoring in the abstract, and the new quantitative reports for exp 20 and exp 12b give a reviewer a clear way to trace prose back to evidence.

### Strengths to preserve

- **Single-axiom framing**: The paragraph that identifies ρ_ϕ(x) = Σ_i ω_i |ψ_i(x)|² as the ω-weighted form of A_joint(x) = Σ_i |ψ_i(x)|² makes the link between probability conservation, mass-energy conservation, and the clock-fluid source for gravity explicit on page 2.
- **Audit-table as authority**: The change log states that four prose sites were reconciled to Table 1 this cycle, and that a claim-auditor subagent enforces that alignment.
- **Honest experiment reporting**: exp 20 arm B preserves joint A = 1 to 8.9×10⁻¹⁶; exp 12b preserves A = 1 to machine precision over 6000 ticks while showing r_peak escape to ~83 by tick ~2000.
- **Falsifiable prediction**: The shared optical axis V1 + V2 + V3 = (1, 1, -1) is named in kinematics, gauge sector, gravity, and atomic-clock channels, and flagged as P9.

### Critical issues for a public v1.0

1. **Front matter is a changelog, not a paper**. Pages 1-2 open with “What changed in v0.98-RC” and push the abstract to page 3, inserting stray page numbers into the flow. Move the full log to an appendix or release notes and restore a standard title → abstract → introduction sequence.

2. **Abstract still overstates two PART rows**. Items (v) and (vi) are correctly qualified as PART in the current text, noting that exp 19c does not exhibit settled orbital lock-in and that the numerical 1/g² prefactor and birefringence test remain open. The surrounding prose must not upgrade these to “derives” or “establishes” elsewhere in the introduction, hydrogen-spectrum section, or vacuum-twist section.

3. **Core notation renders incorrectly**. The PDF extraction shows literal “P i” for summations, spaced “T 3 ⋄” for the lattice, and broken |ψR|2 forms. Define once in Section 2:
   - `$A_{\text{session}} = |\psi_R|^2 + |\psi_L|^2 = 1$`
   - `$A_{\text{joint}}(x) = \sum_i |\psi_i(x)|^2$`
   - `$\rho_{\phi}(x) = \sum_i \omega_i |\psi_i(x)|^2$`
   - `$T^3_{\diamond}$` for the bipartite lattice
   Then replace all variants globally.

4. **PASS / PART is used before it is defined**. The terms appear 30+ times in the abstract and changelog, but the first definition the extraction finds is in the Table 1 caption on page 15. Add a one-sentence legend at first use: PASS = reproduced to stated precision with no open qualifiers; PART = mechanism demonstrated but full quantitative match pending.

5. **Long-horizon scope is easy to misread**. exp 12’s 4-sig-fig PASS is scored on a short k-scan resonance peak; exp 12b shows escape by tick ~2000. State the scoring window explicitly in the main text and in a Table 1 footnote so a reader does not interpret the short-run PASS as long-term stability.

### Recommended changes

**Structure and presentation**
- Replace pages 1-2 with title block, 180-220 word abstract, keywords, and a brief disclaimer. Move the full changelog to Appendix D.
- Add a **Limitations** subsection after the introduction that lists the current PART rows: two-body long-horizon stability, photon emission necessity, emission-operator joint A = 1 conservation, and induced gauge action coefficient.
- Create a one-page Notation table after the contents and use it to standardize A = 1, Ajoint, ρ_ϕ, tick, session, Oh-averaged, RGB/CMY.

**Claim alignment**
- Keep the exact PART wording from the abstract in all four reconciliation sites you flagged: abstract (v) and (vi), introduction mentions, hydrogen spectrum, and vacuum twist field equations.
- For exp 20, separate the two findings in prose: joint A = 1 conservation to machine precision under the beam-splitter arm, and inheritance of orbital escape from the exp 12b baseline.
- For the Standard Model accounting line, move it to Discussion and frame as a reframing: “The Standard Model can be reframed as the minimal accounting required to maintain A = 1”.

**LaTeX and formatting**
- Fix summation symbols, lattice symbol, and norm notation throughout.
- Unify experiment labels: use `exp 12`, `exp 12b`, `exp 19c`, `exp 20` with no extra spaces.
- Regenerate the TOC after moving front matter to remove orphan numbers like the “1”, “Introduction”, “9” sequence seen in extraction.
- Replace raster figure screenshots on pages 52 onward with vector PDFs that include tick count, grid size, and boundary condition in captions.

**Metadata**
- Format ORCID and GitHub as active links: https://orcid.org/0009-0003-1166-307X and https://github.com/JackDMenendez/discrete-causal-lattice.
- Add a Data Availability statement with repo URL, Zenodo DOI, and the exact commit hash used for exp 12b and exp 20.
- Add a license statement (e.g., CC BY 4.0) and 4-6 keywords after the abstract.

### Release checklist for v1.0

- [ ] Move changelog to appendix; abstract ≤220 words
- [ ] Add Notation table and Limitations section
- [ ] Apply global replacements for `$T^3_{\diamond}$`, `$\sum_i$`, `$A_{\text{joint}}$`, `$\rho_{\phi}$`, and `|\psi_R|^2 + |\psi_L|^2 = 1`
- [ ] Verify every mention of exp 19c and exp 20 includes PART qualifier and Table 1 reference
- [ ] Add Table 1 legend and footnote for exp 12 scoring window
- [ ] Fix hyphenation artifacts: operation-algebra, mentions, downgraded
- [ ] Regenerate TOC and cross-references; ensure Table 1 appears before first forward reference
- [ ] Export figures as vector PDFs with full captions
- [ ] Update title block with email, clickable ORCID/GitHub, license, keywords