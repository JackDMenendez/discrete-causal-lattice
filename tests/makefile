
RELATIVE_PATH := ../

include $(RELATIVE_PATH)common.mak

TEST_SRCS := test_octahedral_lattice.py \
             test_phase_oscillator.py \
             test_unity_constraint.py \
             test_causal_session.py \
             test_tick_scheduler.py \
             test_composite_causal_session.py

LOG := $(RELATIVE_PATH)data/tests.log

.PHONY: all test clean

all: test

test: $(VENV)/touchfile
	@echo "Running unit tests"
	$(PYTHON) -m pytest $(TEST_SRCS) -v 2>&1 | tee $(LOG)
	@echo "Tests complete -- see $(LOG)"

clean:
	@echo "Tests clean complete"

include $(RELATIVE_PATH)targets.mak
