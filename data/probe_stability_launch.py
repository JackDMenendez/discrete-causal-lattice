"""
probe_stability_launch.py

Launches parallel stability probes across 14 parameter combinations.
Each worker writes its own log and npy to data/.

Parameter space:
  Test 1 -- k-sweep (update_every=1): 10 k values
    k = [0.050, 0.060, 0.070, 0.080, 0.090, 0.097, 0.110, 0.120, 0.140, 0.160]
    Tests whether any initialization finds the Arnold tongue basin.

  Test 2 -- lag test (k=K_BOHR=0.097): 4 update_every values
    update_every = [1, 5, 10, 20]
    Tests whether mean-field update lag drives eccentricity.
    (k=0.097, update_every=1 is shared with Test 1 -- only 3 additional runs)

Total: 13 unique workers. Run with up to 13 parallel processes.
"""
import subprocess, sys, os, time

PYTHON = sys.executable
WORKER = os.path.join(os.path.dirname(__file__), 'probe_stability_worker.py')
K_BOHR = 1.0 / 10.3  # 0.09709

jobs = []

# Test 1: k-sweep, update_every=1
for k in [0.050, 0.060, 0.070, 0.080, 0.090, 0.097, 0.110, 0.120, 0.140, 0.160]:
    run_id = f'k{k:.3f}_lag1'
    jobs.append((k, 1, run_id))

# Test 2: lag test at K_BOHR, update_every > 1
for lag in [5, 10, 20]:
    run_id = f'k{K_BOHR:.3f}_lag{lag}'
    jobs.append((K_BOHR, lag, run_id))

print(f'Launching {len(jobs)} workers (max 13 parallel)...')
print(f'Python: {PYTHON}')
print(f'Worker: {WORKER}')
print()

procs = []
for k, lag, run_id in jobs:
    cmd = [PYTHON, '-u', WORKER, str(k), str(lag), run_id]
    log_path = os.path.join(os.path.dirname(__file__), f'probe_stability_{run_id}.log')
    print(f'  Spawning: k={k:.3f}  lag={lag}  -> {log_path}')
    p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    procs.append((run_id, p))

print(f'\nAll {len(procs)} workers launched. PIDs:')
for run_id, p in procs:
    print(f'  {run_id}: PID {p.pid}')

print('\nMonitor with:')
print('  tail -f data/probe_stability_*.log')
print('  (or check individual files in data/)')
print()

# Wait for all to finish
t0 = time.time()
while True:
    done = [(rid, p) for rid, p in procs if p.poll() is not None]
    running = [(rid, p) for rid, p in procs if p.poll() is None]
    if not running:
        break
    elapsed = time.time() - t0
    print(f'[{elapsed:.0f}s] {len(running)} running, {len(done)} done: '
          + ', '.join(rid for rid, _ in done), flush=True)
    time.sleep(120)

print(f'\nAll workers complete. Total time: {time.time()-t0:.0f}s')
print('Summary (first_escape and max_ok_streak from each log):')
print()

import glob, re
for run_id, _ in jobs:
    log_path = os.path.join(os.path.dirname(__file__), f'probe_stability_{run_id}.log')
    if not os.path.exists(log_path):
        print(f'  {run_id}: log missing'); continue
    with open(log_path) as f:
        lines = f.read()
    fe  = re.search(r'first_escape=(\S+)', lines)
    ok  = re.search(r'ok_windows=(\S+)', lines)
    mok = re.search(r'max_ok_streak=(\d+)', lines)
    mn  = re.search(r'r_pdf: min=(\S+)', lines)
    mx  = re.search(r'max=(\S+)', lines)
    fe_s  = fe.group(1)  if fe  else '?'
    ok_s  = ok.group(1)  if ok  else '?'
    mok_s = mok.group(1) if mok else '?'
    mn_s  = mn.group(1)  if mn  else '?'
    mx_s  = mx.group(1)  if mx  else '?'
    print(f'  {run_id:<22}  escape={fe_s:<8}  ok={ok_s:<10}  '
          f'streak={mok_s:<4}  r_pdf=[{mn_s},{mx_s}]')
