# Discrete Causal Lattice -- root build
# ----------------------------------------------------------------------------
# Requirements
#   GNU Make >= 4.3   (uses grouped-target `&:` syntax in src/experiments)
#   pdflatex, bibtex  (MiKTeX or TeX Live)
#   Python 3 + venv
#
#   Run from an MSYS2 UCRT64 shell. The stock Windows GNU Make port
#   (3.81, "make for Windows") is too old: it predates `&:` and has weak
#   shell handling. Confirm with: `make --version` -> >= 4.3.
# ----------------------------------------------------------------------------
# Targets
#   all          env -> tests -> paper -> promote          (default)
#   env          create .venv, install requirements
#   tests        run pytest against tests/
#   paper        build main + draft PDFs (3-pass pdflatex + bibtex)
#   promote      copy final PDFs and figures into stage/
#   experiments  delegate to src/experiments/makefile (see WARNING below)
#   clean        remove build/ and stage/
#   clean-env    also remove .venv
#   help         print this list
#
# Parallelism
#   `make -jN` runs targets in parallel where dependencies allow.
#   Useful for the env -> tests -> paper chain. NOT recommended for
#   `experiments` -- some experiments share data files, and most are slow
#   enough that you want serial console output anyway.
#
# Long experiments -- prefer running them one at a time
#   Several experiments run for hours to days (exp_11 ~20h, exp_18 ~4-8h,
#   exp_20 ~43h, etc.). Don't run `make experiments` from root unless you
#   have a cluster. Instead, invoke individual targets:
#       make -C src/experiments exp_12
#       make -C src/experiments quantization_scan
#   See src/experiments/makefile for the full list.
# ----------------------------------------------------------------------------

RELATIVE_PATH :=
include common.mak

# --- Paper ------------------------------------------------------------------
DOC_TITLE := Discrete_Causal_Lattice
DOC_PDF   := $(build_dir)/$(DOC_TITLE).pdf

PAPER_DIR    := paper
PAPER_INPUTS := $(PAPER_DIR)/main.tex \
                $(wildcard $(PAPER_DIR)/sections/*.tex) \
                $(wildcard $(PAPER_DIR)/macros/*.tex) \
                $(wildcard $(PAPER_DIR)/paper-bib/*.bib)

# pdflatex/bibtex run from inside paper/ so relative \input{} and
# \bibdata{} paths resolve. Output goes to ../build/ (= $(build_dir) from root).
PDFLATEX_PAPER := cd $(PAPER_DIR) && $(PDFLATEX) -output-directory=../$(build_dir)
BIBTEX_PAPER   := cd $(PAPER_DIR) && $(BIBTEX) ../$(build_dir)

# --- Promote ----------------------------------------------------------------
# To ship figures alongside the PDF, list them in PROMOTE_FIGS (filenames
# inside figures/). They'll be copied to stage/ via the pattern rule below.
PROMOTE_FIGS :=
PROMOTE_PDF_TARGETS := $(stage_dir)/$(DOC_TITLE).pdf
PROMOTE_FIG_TARGETS := $(addprefix $(stage_dir)/,$(PROMOTE_FIGS))

# --- Tests ------------------------------------------------------------------
TEST_DIR := tests

.PHONY: all help env tests paper promote experiments clean clean-env

all: env tests paper promote
	@echo "================ Build Complete ================"

help:
	@sed -n '1,30p' makefile

# --- Environment ------------------------------------------------------------
$(VENV):
	python -m venv $(VENV)

$(VENV)/touchfile: $(VENV) requirements.txt
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt
	touch $(VENV)/touchfile

env: $(VENV)/touchfile

# --- Tests ------------------------------------------------------------------
tests: $(VENV)/touchfile
	$(PYTHON) -m pytest $(TEST_DIR) -v

# --- Paper ------------------------------------------------------------------
paper: $(DOC_PDF)

$(build_dir) $(stage_dir):
	mkdir -p $@

$(DOC_PDF): $(PAPER_INPUTS) | $(build_dir)
	$(PDFLATEX_PAPER) -jobname=$(DOC_TITLE) main.tex
	$(BIBTEX_PAPER)/$(DOC_TITLE)
	$(PDFLATEX_PAPER) -jobname=$(DOC_TITLE) main.tex
	$(PDFLATEX_PAPER) -jobname=$(DOC_TITLE) main.tex

# --- Promote ----------------------------------------------------------------
promote: $(PROMOTE_PDF_TARGETS) $(PROMOTE_FIG_TARGETS)

$(stage_dir)/$(DOC_TITLE).pdf: $(DOC_PDF) | $(stage_dir)
	cp -v $< $@

$(stage_dir)/%: $(figures_dir)/% | $(stage_dir)
	cp -v $< $@

# --- Experiments ------------------------------------------------------------
# Delegates to src/experiments. The "all" target there runs every experiment
# in EXPERIMENTS, which is hours-to-days of work. Prefer named targets:
#    make -C src/experiments exp_12
experiments:
	@echo "WARNING: 'make experiments' runs every experiment in src/experiments/makefile."
	@echo "         Many take hours; some take days."
	@echo "         Prefer 'make -C src/experiments <target>' for individual runs."
	$(MAKE) -C src/experiments all

# --- Clean ------------------------------------------------------------------
clean:
	-rm -rf $(build_dir) $(stage_dir)
	@echo "================ Clean Complete ================"

clean-env:
	-rm -rf $(VENV)
	@echo "================ clean-env Complete ================"
