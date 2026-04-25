
# Makefile for building the Discrete Causal Lattice paper and src subprojects, ensuring the stage, 
# data, and build directories exist, and promoting the final PDF to the stage directory after building the subprojects. Data generated through the subprojects is stored in the data directory, and intermediate build files are stored
# in the build directory. The clean target removes all generated files and directories to ensure a clean build environment.
# Targets:
#   all: Cleans, assembles, and promotes the final PDF to the stage directory	
#   assemble: Builds each subproject in order, ensuring the stage, data, and build directories
#             exist before building each subproject.
#   promote: Promotes the final PDF and other figures and documents to the stage directory
#            after building the subprojects.
#   clean: Cleans all generated files and directories to ensure a clean build environment
#   audit: Runs experiments or scripts defined in the src subproject and generates a report
# Ouput:
#   The final PDF is promoted to the stage directory
#   The draft PDF with line numbers for review is promoted to the stage directory
#   Any figures or documents generated through the build process are promoted to the stage directory
RELATIVE_PATH := ../

# Now that we have relative paths defined for the stage, data, and build directories, we can 
# include the common makefile
include $(RELATIVE_PATH)common.mak

# Define the document filenames
doc_title := Discrete_Causal_Lattice
draft_title := $(doc_title)_Draft
# Source figures included in the paper and will also be promoted to the stage directory for use by others, and in presentations so that they are included in the release of the paper on GitHub, but these are not all generated through the build process and are source controlled.
figures_to_promote := $(figures)

doc_author := Jack Menendez
doc_date := \today
doc_version := 2.0

# Define the two files that will be generated through the build process, the final PDF 
# and a draft PDF with line numbers for review
doc_filename := $(doc_title).pdf
doc_output := $(build_dir)/$(doc_filename)
draft_filename := $(draft_title).pdf
draft_output := $(build_dir)/$(draft_filename)
documents = $(doc_filename) $(draft_filename)
documents_output := $(addprefix $(build_dir)/,$(documents))
documents_promote := $(addprefix $(stage_dir)/,$(documents))
quantization_scan_filename := Quantization_Scan.pdf
lattice_drawing_filename := lattice.drawio.png
figures := $(lattice_drawing_filename) $(quantization_scan_filename)
figures_input := $(addprefix $(figures_dir)/,$(figures))
figures_promote := $(addprefix $(stage_dir)/,$(figures))
source_promotes := $(documents_output) $(figures_input)
target_promotes := $(documents_promote) $(figures_promote)
sections := sections/*.tex
main_tex := main.tex
macros := macros/*.tex
bib := paper-bib/*.bib
# The source files for the paper, including the main tex file, section tex files, and figure files
inputs := $(main_tex) $(sections) $(figures_input) $(macros) $(bib)

# Define output of the latex pdf command for the prospective PDF and draft PDF.
temp_files := $(build_dir)/*.aux $(build_dir)/*.log $(build_dir)/*.out $(build_dir)/*.toc \
	$(build_dir)/*.lof $(build_dir)/*.lot	

.PHONY: all assemble audit promote clean

all : clean audit assemble promote

audit:
	@echo "audit nothing to do"


promote: $(target_promotes) 

$(target_promotes): $(source_promotes) $(stage_dir)
	@cp -v $^ $(stage_dir)

assemble: audit $(build_dir) $(stage_dir) $(doc_output) $(draft_output)

$(build_dir):
	mkdir -p $(build_dir)

$(stage_dir):
	mkdir -p $(stage_dir)

$(doc_output): $(inputs)
	-rm -f $(doc_output) $(clean_files)
	$(PDFLATEX) -output-directory=$(build_dir) -jobname=$(doc_title) main.tex
	$(BIBTEX) $(build_dir)/$(doc_title).aux
	$(PDFLATEX) -output-directory=$(build_dir) -jobname=$(doc_title) main.tex
	$(PDFLATEX) -output-directory=$(build_dir) -jobname=$(doc_title) main.tex

$(draft_output): $(inputs)
	-rm -f $(draft_output) $(clean_files)
	$(PDFLATEX) -output-directory=$(build_dir) -jobname=$(draft_title) \"\def\linenumberstrue{true}\input{main.tex}\"
	$(BIBTEX) $(build_dir)/$(draft_title).aux
	$(PDFLATEX) -output-directory=$(build_dir) -jobname=$(draft_title) \"\def\linenumberstrue{true}\input{main.tex}\"
	$(PDFLATEX) -output-directory=$(build_dir) -jobname=$(draft_title) \"\def\linenumberstrue{true}\input{main.tex}\"
	
clean:
	-rm -f $(target_promotes) $(temp_files)

include $(RELATIVE_PATH)targets.mak