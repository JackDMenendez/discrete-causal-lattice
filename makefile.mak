SUBPROJECTS := paper
stage_dir := stage

.PHONY: all $(SUBPROJECTS) clean $(stage_dir)

all: $(SUBPROJECTS)

$(SUBPROJECTS): $(stage_dir)/discrete-causal-lattice.pdf
	$(MAKE) -C $@

$(stage_dir)/discrete-causal-lattice.pdf: $(SUBPROJECTS) $(statge_dir)
	-mkdir -p $(stage_dir)
	ln -sf ../paper/build/main.pdf $@

$(stage_dir):
	-mkdir -p $@

clean:
	for d in $(SUBPROJECTS); do \
		$(MAKE) -C $$d clean; \
	done
	-rm -rf $(stage_dir)