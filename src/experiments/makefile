
RELATIVE_PATH:= ../../

include $(RELATIVE_PATH)common.mak

QUANTIZATION_SCAN_SRC := exp_11_quantization_scan.py
PLOT_SCAN_SRC         := plot_quantization_scan.py

EXP_00 := exp_00_causal_cone
EXP_00_SRC := exp_00_causal_cone.py
EXP_00_FIG := exp_00_cone_structure.pdf
EXP_00_LOG := exp_00_causal_cone_log.txt

EXP_01 := exp_01_inertia
EXP_01_SRC := $(EXP_01).py
EXP_01_LOG := $(EXP_01)_log.txt

EXP_HARMONIC     := exp_harmonic_analysis
EXP_HARMONIC_SRC := $(EXP_HARMONIC).py
EXP_HARMONIC_LOG := $(EXP_HARMONIC)_log.txt
EXP_HARMONIC_FIG := exp_harmonic_landscape.pdf

EXP_12 := exp_12_hydrogen_twobody
EXP_12_SRC := $(EXP_12).py
EXP_12_LOG := $(EXP_12)_log.txt
EXP_12_FIG := exp_12_twobody_scan.pdf
EXP_12_NPY := $(data_dir)/exp_12_twobody_scan.npy
PLOT_TWOBODY_SRC := plot_twobody_scan.py

EXP_13 := exp_13_threebody_helium
EXP_13_SRC := $(EXP_13).py
EXP_13_LOG := $(EXP_13)_log.txt
EXP_13_NPY := $(data_dir)/exp_13_threebody.npy

EXPERIMENTS := quantization_scan $(EXP_00) $(EXP_01) $(EXP_12) $(EXP_HARMONIC) $(EXP_13) $(EXP_14)

NPY_FILES := $(data_dir)/quantization_scan_n1.npy $(data_dir)/quantization_scan_n2.npy
NPY_FOCUSED := $(data_dir)/quantization_scan_n1_focused.npy

FIG_FILES := $(figures_dir)/quantization_scan.pdf $(figures_dir)/$(EXP_00_FIG) $(figures_dir)/$(EXP_12_FIG) $(figures_dir)/$(EXP_HARMONIC_FIG)

PROMOTE_FILES := $(addprefix $(stage_dir)/,$(notdir $(FIG_FILES))) $(addprefix $(stage_dir)/,$(notdir $(NPY_FILES)))

.PHONY: clean all audit promote assemble test setup quantization_scan quantization_scan_focused $(EXPERIMENTS)

all: clean audit assemble promote $(data_dir) $(EXPERIMENTS)
	@echo "Build Complete"

assemble:
	@echo "Running experiments complete"

audit: $(EXPERIMENTS)
	@echo "Audit Complete"

promote: $(PROMOTE_FILES)
	@echo "Promote Complete"

$(PROMOTE_FILES): $(stage_dir) $(NPY_FILES) $(FIG_FILES)
	@cp -v $^ $(stage_dir)

# Plot is regenerated whenever n1 or n2 data changes.
# n2 is a long run (~20 hrs); the figure is still valid with n1 alone.
quantization_scan: $(data_dir) $(figures_dir)/quantization_scan.pdf
	@echo "Quantization scan complete"

$(EXP_00): $(EXP_00_SRC) $(data_dir) $(figures_dir) $(EXP_00_FIG)

$(EXP_00_FIG): $(EXP_00_SRC)
	@echo "Running $@"
	$(PYTHON) $< --fig $(figures_dir)/$(EXP_00_FIG) > $(data_dir)/$(EXP_00_LOG)

$(EXP_01): $(data_dir) $(data_dir)/$(EXP_01_LOG)

$(data_dir)/$(EXP_01_LOG): $(EXP_01_SRC) $(VENV)/touchfile
	@echo "Running $@"
	$(PYTHON) $< > $@

$(EXP_12): $(data_dir) $(data_dir)/$(EXP_12_LOG) $(figures_dir)/$(EXP_12_FIG)

$(data_dir)/$(EXP_12_LOG): $(EXP_12_SRC) $(VENV)/touchfile
	@echo "Running $@"
	$(PYTHON) $< --datadir $(data_dir) > $@

$(figures_dir)/$(EXP_12_FIG): $(PLOT_TWOBODY_SRC) $(EXP_12_NPY) $(NPY_FOCUSED)
	@echo "Plotting two-body scan comparison"
	$(PYTHON) $(PLOT_TWOBODY_SRC) --datadir $(data_dir) --out $@

EXP_14     := exp_14_helium
EXP_14_SRC := $(EXP_14).py
EXP_14_LOG := $(EXP_14)_log.txt
EXP_14_NPY := $(data_dir)/exp_14_helium.npy

$(EXP_13): $(data_dir) $(data_dir)/$(EXP_13_LOG)

$(data_dir)/$(EXP_13_LOG): $(EXP_13_SRC) $(VENV)/touchfile
	@echo "Running three-body helium-like system"
	$(PYTHON) $< --datadir $(data_dir) > $@

$(EXP_14): $(data_dir) $(data_dir)/$(EXP_14_LOG)

$(data_dir)/$(EXP_14_LOG): $(EXP_14_SRC) $(VENV)/touchfile
	@echo "Running helium two-electron system"
	$(PYTHON) $< --datadir $(data_dir) > $@

$(EXP_HARMONIC): $(data_dir) $(data_dir)/$(EXP_HARMONIC_LOG) $(figures_dir)/$(EXP_HARMONIC_FIG)

$(data_dir)/$(EXP_HARMONIC_LOG): $(EXP_HARMONIC_SRC) $(VENV)/touchfile
	@echo "Running harmonic analysis"
	$(PYTHON) $< --quiet > $@

$(figures_dir)/$(EXP_HARMONIC_FIG): $(EXP_HARMONIC_SRC) $(VENV)/touchfile
	@echo "Plotting harmonic landscape"
	$(PYTHON) $< --fig $@ --quiet > /dev/null

$(figures_dir)/quantization_scan.pdf: $(PLOT_SCAN_SRC) $(data_dir)/quantization_scan_n2.npy
	@echo "Plotting quantization scan"
	$(PYTHON) $(PLOT_SCAN_SRC) --datadir $(data_dir) --out $(figures_dir)/quantization_scan.pdf

$(data_dir)/quantization_scan_n2.npy : $(data_dir)/quantization_scan_n1.npy
	@echo "Quantization scan phase 2 (n=2, ~20 hrs)"
	$(PYTHON) $(QUANTIZATION_SCAN_SRC) --n2 --datadir $(data_dir) > $(data_dir)/quantization_scan_n2_log.txt

$(data_dir)/quantization_scan_n1.npy : $(QUANTIZATION_SCAN_SRC) $(VENV)/touchfile
	@echo "Quantization scan phase 1 (n=1, ~20 hrs)"
	$(PYTHON) $(QUANTIZATION_SCAN_SRC) --datadir $(data_dir) > $(data_dir)/quantization_scan_n1_log.txt

quantization_scan_focused: $(NPY_FOCUSED)
	@echo "Focused quantization scan complete"

$(NPY_FOCUSED) : $(QUANTIZATION_SCAN_SRC) $(VENV)/touchfile
	@echo "Quantization scan focused (n=1, ~2 hrs)"
	$(PYTHON) $(QUANTIZATION_SCAN_SRC) --focused --datadir $(data_dir) > $(data_dir)/quantization_scan_n1_focused_log.txt

# clean does not remove files because it can take days to create them. Therefore through
# strict depenencies we manage building and promoting the files, but we do not remove them 
# with clean. Instead, clean only removes the stage and build directories to ensure a clean 
# staging environment for the final PDF and figures, and a clean build environment for any 
# intermediate files generated through the build process. The data directory is not removed 
# since it may contain manually curated data files that are used in the paper, and of use for 
# future research by others.
clean:
	@echo "Experiments Clean Complete"

include $(RELATIVE_PATH)targets.mak
