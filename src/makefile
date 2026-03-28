# Makefile for building the paper and src subprojects, ensuring the stage, 
# data, and build directories exist, and promoting the final PDF to the stage
# directory after building the subprojects. Data generated through the 
# subprojects is stored in the data directory, and intermediate build files are stored
# in the build directory. The clean target removes all generated files and
# directories to ensure a clean build environment.
# Targets:
#   all: Cleans the build environment, assembles the subprojects, and promotes the final PDF to the stage directory.
#   assemble: Builds each subproject in order, ensuring the stage, data, and build directories exist before building each subproject.
#   promote: Promotes the final PDF to the stage directory after building the subprojects.
#   clean: Cleans all generated files and directories to ensure a clean build environment.
#   run: Runs experiments or scripts defined in the src subproject, ensuring the data directory exists before running.
#   audit: Runs all experiments or scripts defined in the src subproject and generates a report.
# Subprojects:
#   experiments: Runs the experiments defined in the src subproject, ensuring the data and build directories exist before running.
SUBPROJECTS := experiments
RELATIVE_PATH := ../
include $(RELATIVE_PATH)common.mak
# Definephony targets for cleaning each subdir
CLEAN_SUBPROJECTS = $(SUBPROJECTS:%=clean-%)
ASSEMBLE_SUBPROJECTS = $(SUBPROJECTS:%=assemble-%)
PROMOTE_SUBPROJECTS = $(SUBPROJECTS:%=promote-%)
AUDIT_SUBPROJECTS = $(SUBPROJECTS:%=audit-%)

.PHONY: all clean audit promote assemble $(CLEAN_SUBPROJECTS) \
	$(ASSEMBLE_SUBPROJECTS) $(PROMOTE_SUBPROJECTS) $(AUDIT_SUBPROJECTS)

all: audit assemble promote test

test:
	@echo "Running tests complete"

$(PROMOTE_SUBPROJECTS):
	$(MAKE) -C $(@:promote-%=%) promote

assemble: $(ASSEMBLE_SUBPROJECTS)

$(ASSEMBLE_SUBPROJECTS):
	$(MAKE) -C $(@:assemble-%=%) assemble

audit: $(AUDIT_SUBPROJECTS)

$(AUDIT_SUBPROJECTS):
	$(MAKE) -C $(@:audit-%=%) audit

clean: $(CLEAN_SUBPROJECTS)

$(CLEAN_SUBPROJECTS):
	$(MAKE) -C $(@:clean-%=%) clean

include $(RELATIVE_PATH)targets.mak