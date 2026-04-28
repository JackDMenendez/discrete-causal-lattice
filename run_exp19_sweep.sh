#!/usr/bin/env bash
# Launch a settled exp_19 (v5 phase-rotation drain) sweep across all
# EMISSION_RATES.
#
# Usage:
#   ./run_exp19_sweep.sh                # default: TICKS=6000 (~5-6 h per rate)
#   EXP19_TICKS=2000 ./run_exp19_sweep.sh   # shorter
#
# This is the v5 phase-rotation-drain mechanism (A=1-compatible by
# construction). It is independent of exp_19c (Coulomb drain + recoil);
# running both simultaneously gives two independent verifications of the
# same claim.
#
# Per-rate logs land at data/exp_19_rate_*.log; combined stdout tees to
# data/exp_19_sweep_<timestamp>.log.

set -euo pipefail

cd "$(dirname "$0")"

: "${EXP19_TICKS:=6000}"
export EXP19_TICKS

VENV_PY=".venv-ucrt64/bin/python.exe"
if [[ ! -x "$VENV_PY" ]]; then
    echo "run_exp19_sweep.sh: $VENV_PY not found; create the venv first" >&2
    echo "  (e.g. ./build.sh env)" >&2
    exit 1
fi

mkdir -p data
ts="$(date +%Y%m%d_%H%M%S)"
sweep_log="data/exp_19_sweep_${ts}.log"

echo "exp_19 v5 sweep launcher"
echo "  TICKS_TOTAL = $EXP19_TICKS"
echo "  combined log: $sweep_log"
echo "  per-rate logs: data/exp_19_rate_*.log"
echo

exec "$VENV_PY" -u src/experiments/exp_19_photon_emission.py 2>&1 | tee "$sweep_log"
