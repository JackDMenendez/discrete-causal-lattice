
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

EXPERIMENTS := quantization_scan $(EXP_00) $(EXP_01)

NPY_FILES := $(data_dir)/quantization_scan_n1.npy $(data_dir)/quantization_scan_n2.npy

FIG_FILES := $(figures_dir)/quantization_scan.pdf $(figures_dir)/$(EXP_00_FIG)

PROMOTE_FILES := $(addprefix $(stage_dir)/,$(notdir $(FIG_FILES))) $(addprefix $(stage_dir)/,$(notdir $(NPY_FILES)))

.PHONY: clean all audit promote assemble test setup quantization_scan $(EXPERIMENTS)

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

$(figures_dir)/quantization_scan.pdf: $(PLOT_SCAN_SRC) $(data_dir)/quantization_scan_n2.npy
	@echo "Plotting quantization scan"
	$(PYTHON) $(PLOT_SCAN_SRC) --datadir $(data_dir) --out $(figures_dir)/quantization_scan.pdf

$(data_dir)/quantization_scan_n2.npy : $(data_dir)/quantization_scan_n1.npy
	@echo "Quantization scan phase 2 (n=2, ~20 hrs)"
	$(PYTHON) $(QUANTIZATION_SCAN_SRC) --n2 --datadir $(data_dir) > $(data_dir)/quantization_scan_n2_log.txt

$(data_dir)/quantization_scan_n1.npy : $(QUANTIZATION_SCAN_SRC) $(VENV)/touchfile
	@echo "Quantization scan phase 1 (n=1, ~20 hrs)"
	$(PYTHON) $(QUANTIZATION_SCAN_SRC) --datadir $(data_dir) > $(data_dir)/quantization_scan_n1_log.txt

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
