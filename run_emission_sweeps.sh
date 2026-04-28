#!/usr/bin/env bash
# Launch BOTH exp_19 v5 (phase-rotation drain) and exp_19c v10
# (Coulomb drain + recoil) sweeps in parallel. Together they give two
# independent numerical tests of the joint A=1 + photon-emission claim.
#
# Usage:
#   ./run_emission_sweeps.sh                  # default: 6000 ticks each
#   EXP19_TICKS=4000 EXP19C_TICKS=4000 ./run_emission_sweeps.sh
#
# Resource use (each sweep launches 5 parallel rate-subprocesses):
#   - 10 cores total (5 per sweep), single-threaded numpy per worker
#   - ~1.3 GB resident across all 10 workers
#   - Wall time dominated by the slower of the two (~5-6 h at TICKS=6000)
#
# Outputs:
#   data/exp_19_sweep_<ts>.log      combined stdout, exp_19 v5
#   data/exp_19c_sweep_<ts>.log     combined stdout, exp_19c v10
#   data/exp_19_rate_*.log          per-rate, exp_19 v5
#   data/exp_19c_rate_*.log         per-rate, exp_19c v10
#
# To background it for an overnight run:
#   nohup ./run_emission_sweeps.sh > data/sweeps_$(date +%Y%m%d_%H%M%S).out 2>&1 &

set -euo pipefail

cd "$(dirname "$0")"

: "${EXP19_TICKS:=6000}"
: "${EXP19C_TICKS:=6000}"
export EXP19_TICKS EXP19C_TICKS

echo "Launching both emission sweeps in parallel."
echo "  exp_19 v5  (phase-rotation drain): EXP19_TICKS=$EXP19_TICKS"
echo "  exp_19c v10 (Coulomb drain + recoil): EXP19C_TICKS=$EXP19C_TICKS"
echo

# Launch each sweep in the background; capture PIDs for clean wait.
./run_exp19_sweep.sh  & pid_19=$!
./run_exp19c_sweep.sh & pid_19c=$!

echo "exp_19 v5  PID: $pid_19"
echo "exp_19c v10 PID: $pid_19c"
echo "Tail any data/exp_19*_rate_*.log to monitor."
echo

# Wait for both. Trap SIGINT so Ctrl-C tears them down.
trap 'kill $pid_19 $pid_19c 2>/dev/null; exit 130' INT TERM
wait $pid_19  ; rc_19=$?
wait $pid_19c ; rc_19c=$?

echo
echo "exp_19 v5  exit: $rc_19"
echo "exp_19c v10 exit: $rc_19c"

# Non-zero composite exit if either failed.
[[ $rc_19 -eq 0 && $rc_19c -eq 0 ]]
