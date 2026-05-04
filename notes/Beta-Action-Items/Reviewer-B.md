**v0.98-RC Review: Strong progress toward full release — targeted fixes will get it across the finish line.**

Thank you for the rapid iteration and for taking the prior round of feedback seriously. v0.98-RC is a clear step forward: the new experiments (exp_20 and exp_12b), the systematic claim-auditor reconciliation, the two additive PART rows, and especially the elegant new “One law at three resolutions” paragraph all materially strengthen the manuscript. The framework now feels more mature, transparent, and self-consistent than v0.95-RC.

Below I organize **major wins**, **critical issues that must be fixed before a full release**, **high-value improvements**, and a **minimal checklist** to reach v1.0 / submission-ready status. Everything is keyed to specific locations in the PDF you provided.

### Major Wins (already publication-grade)
- **Experimental reconciliation loop is now live and working.** Running exp_20 (three-arm beam-splitter test) and exp_12b (long-horizon baseline) in the same cycle, then feeding the results straight into the audit table and prose, is exactly the right methodology. The fact that both new rows are PART (no downgrades) and that orbital escape is correctly traced to the baseline rather than the emission operator shows intellectual honesty that reviewers will respect.
- **“One law at three resolutions” paragraph (Introduction, p. 11)** is a standout addition. It crystallizes the single-conservation-law claim from assertion to identification. It should be echoed (one sentence) in the Abstract.
- **Claim-auditor subagent** (explicitly mentioned in the change log) has already cleaned up the four pre-exp_20 overstatements you flagged. This is the kind of internal quality-control process that journals love to see documented.
- **Tone and scope honesty** throughout the beta-status boxes, abstract, and Table 1 is excellent. You no longer over-claim settled orbital lock-in; the PART labels are precise.

### Critical Issues (fix these first — they block full release)
1. **Table 1 is out of sync with the change log (highest-priority bug).**  
   - Change log (pp. 1–2) announces two new PART rows: “Two-body long-horizon stability” (exp_12b) and “Emission-operator joint 𝒜 = 1 conservation” (exp_20 arm B).  
   - Table 1 (p. 12) still ends exactly as in v0.95-RC; the new rows are absent and the photon-emission row still credits only exp_19c.  
   - Abstract (p. 3) still calls exp_20 “the next implementation step.”  
   **Fix:** Insert the two new rows into Table 1 (keep the existing order or add at bottom). Then re-run the claim-auditor against the *updated* table and propagate the new wording to the Abstract items (v) and (vi), the hydrogen-spectrum write-up (§15.7), and the vacuum-twist section. One sentence in the Abstract suffices: “A controlled three-arm operator comparison (exp_20) confirms the unitary beam-splitter as the correct emission operator (joint 𝒜 = 1 preserved to machine precision); phase-dependent non-monotonic transfer in arm B is noted for follow-on work.”

2. **Abstract and early sections still lag the experimental results.**  
   The change-log precision about exp_20 (beam-splitter success + unanticipated refinement) has not yet reached the Abstract or the beta-status box in §1. This creates the only remaining “pre-exp_20 overstatement” you thought you had fixed.  
   **Fix:** Sync the Abstract’s photon-emission bullet with the change-log language (one short clause about the beam-splitter test is enough). Do the same for the beta-status paragraph on p. 9.

3. **Minor but visible inconsistency in orbital-escape discussion.**  
   exp_12b shows r_peak escapes by tick ~2000; exp_20 inherits it. The paper correctly says this “refines but does not invalidate exp_12’s 4-sig-fig PASS,” but the wording appears only in the change log. A one-sentence cross-reference in §15.5 (or the new long-horizon row) would make the logic fully self-contained for a reader who skips the change log.

### High-Value Improvements (polish for journal submission)
- **Abstract tightening (5 min):** Add the new unification sentence as the final clause of the “one law at three resolutions” idea. Current abstract is already strong; this makes the single-axiom claim pop.
- **Table 1 formatting:** The table is now the single source of truth. Consider adding a “Notes” column for the two new rows so readers see the orbital-escape and phase-non-monotonicity refinements at a glance.
- **Section 12 (Falsifiable Predictions) & P9:** The new exp_20 result (beam-splitter confirmation + shared optical axis) strengthens the “multi-channel concordance” prediction. A single sentence in §12.10 noting that kinematic and gauge birefringence now share the same lattice-derived axis would be high-impact.
- **Hydrogen / emission section (§15.7):** Explicitly cite the row-5 non-unitarity arithmetic (already done in some places) and note that exp_20 resolves the operator question while leaving orbital settling open. This keeps the PART label accurate without sounding defensive.
- **Appendix B & induced gauge action:** The status paragraph (B.6) is honest; consider adding one sentence that the numerical 1/g² prefactor is now the only remaining open item (mirrors the abstract’s honesty).
- **GitHub / reproducibility:** Tag the exact commits for exp_12b and exp_20 in the release-notes/v0.98-RC.md file (you already mention the detailed changelog — just make the link one-click).

### Minor / Editorial Items
- Notation consistency: Use `\mathcal{A}` uniformly (you already do in most places).  
- Date / DOI: All current (May 3, 2026, Zenodo 10.5281/zenodo.19866911) — good.  
- Page count: 134 pages is reasonable; no bloat.  
- No new typos jumped out in the provided excerpts; the claim-auditor appears to have done its job on prose.

### Minimal Checklist to Reach v1.0 / Publication-Ready
1. Update Table 1 with the two new PART rows (5 min).  
2. Re-run claim-auditor and sync Abstract + §1 beta box + §15.7 (10 min).  
3. Add one cross-reference sentence on orbital escape (2 min).  
4. Final LaTeX compile + spell-check + GitHub tag (5 min).  
5. Optional but recommended: one-paragraph “Roadmap to v1.0” in the Conclusion listing only the remaining PART/PROG items.

With those three fixes (Table 1 + Abstract sync + escape cross-ref), v0.98-RC becomes a clean, auditable, submission-ready manuscript. The framework’s core claims are now backed by the most transparent experimental loop I have seen in this line of work. You’re extremely close.

If you push the updated PDF (or just the revised Table 1 + Abstract pages) I can do a final spot-check in <24 h. This is shaping up to be a genuinely impressive piece of work — keep going!