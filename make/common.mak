# Get the absolute path of the current Makefile
MKFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))

# Extract the directory of the Makefile
CURRENT_DIR := $(dir $(MKFILE_PATH))
#------------------------------------------------------------------------------
VENV := $(RELATIVE_PATH).venv
# Allow passing arguments to the script
ARGS ?= -u
PYTHON = "$(VENV)/Scripts/python" $(ARGS)
PIP = "$(VENV)/Scripts/pip.exe"
GNU = c:/utils/gnu/bin
TEE = "$(GNU)/tee.exe" -i
# Location of the virtual environment for the project
# The build location for the paper PDF and intermediate build files generated 
# through the build process
build_dir := $(RELATIVE_PATH)build
# The location for staging the final PDF and other figures and documents after 
# building the subprojects, before creating a release in GitHub.
stage_dir := $(RELATIVE_PATH)stage
# The location for storing any data files generated through by the subprojects, used to create 
# figures or tables in the paper. Data files are are tracked in version control since they may 
# contain manually curated data files that are used in the paper, and of use for future research 
# by others.
data_dir := $(RELATIVE_PATH)data

# The source directory for figures used in the paper, which may be promoted to the stage directory for use by others, and in presentations so that they are included in the release of the paper on GitHub, but these are not all generated through the build process and are source controlled.
figures_dir := $(RELATIVE_PATH)figures


# Define the PDFLATEX and BIBTEX commands for building the paper
PDFLATEX = pdflatex -interaction=nonstopmode -halt-on-error -file-line-error
BIBTEX = bibtex

# For substituing spaces in file names, if needed
nullstring :=
space := $(nullstring) $(nullstring)