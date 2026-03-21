SUBPROJECTS := paper

.PHONY: all $(SUBPROJECTS) clean

all: $(SUBPROJECTS)

$(SUBPROJECTS):
	$(MAKE) -C $@

clean:
	for d in $(SUBPROJECTS); do \
		$(MAKE) -C $$d clean; \
	done