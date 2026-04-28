#!/usr/bin/env bash
# Launch a settled exp_19c photon-emission sweep across all EMISSION_RATES.
#
# Usage:
#   ./run_exp19c_sweep.sh                # default: TICKS=6000 (~5-6 h per rate)
#   EXP19C_TICKS=2000 ./run_exp19c_sweep.sh   # shorter (still > SUCCESS_STREAK=33)
#
# The script:
#   - cds to the repo root
#   - activates the project virtualenv (.venv-ucrt64)
#   - exports EXP19C_TICKS so the python module honours the override
#   - launches src/experiments/exp_19c_photon_emission.py in run_parallel mode
#     (one subprocess per rate, all 5 rates in parallel)
#   - tees combined stdout/stderr to data/exp_19c_sweep_<timestamp>.log
#   - per-rate logs go to data/exp_19c_rate_*.log as before
#
# Background it with `nohup ./run_exp19c_sweep.sh &` if you want to log out.
# Each rate uses one CPU core (numpy is single-threaded for this workload);
# 5 parallel rates therefore want ~5 cores free.

set -euo pipefail

cd "$(dirname "$0")"

: "${EXP19C_TICKS:=6000}"
export EXP19C_TICKS

VENV_PY=".venv-ucrt64/bin/python.exe"
if [[ ! -x "$VENV_PY" ]]; then
    echo "run_exp19c_sweep.sh: $VENV_PY not found; create the venv first" >&2
    echo "  (e.g. ./build.sh env)" >&2
    exit 1
fi

mkdir -p data
ts="$(date +%Y%m%d_%H%M%S)"
sweep_log="data/exp_19c_sweep_${ts}.log"

echo "exp_19c sweep launcher"
echo "  TICKS_TOTAL = $EXP19C_TICKS"
echo "  combined log: $sweep_log"
echo "  per-rate logs: data/exp_19c_rate_*.log"
echo

exec "$VENV_PY" -u src/experiments/exp_19c_photon_emission.py 2>&1 | tee "$sweep_log"
