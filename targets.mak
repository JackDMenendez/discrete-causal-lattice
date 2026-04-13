# This file should be included at the end of each makefile.

# targets for building the paper and src subprojects, ensuring the stage, data,
# and build directories exist, and promoting the final PDF to the stage
# directory after building the subprojects. Data generated through the 
# subprojects is stored in the data directory, and intermediate build files are 
# stored in the build directory. The clean target removes all generated files 
# and directories to ensure a clean build environment.
$(stage_dir) $(data_dir) $(build_dir):
	-mkdir -p $@

clean_env:
	@echo "Cleaning virtual environment"
	-$(RM) -rfv $(VENV)
	-$(RM) -rfv *.pyc __pycache__

INFO_SUBPROJECTS = $(SUBPROJECTS:%=info-%)

info: $(INFO_SUBPROJECTS)
	@echo "Relative path: '$(RELATIVE_PATH)' of current directory: '$(CURRENT_DIR)'"

$(INFO_SUBPROJECTS):
	@echo "============ Assembling $(@:assemble-%=%) ============"
	$(MAKE) -C $(@:info-%=%) info
	