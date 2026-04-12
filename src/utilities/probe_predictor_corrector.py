"""
probe_predictor_corrector.py

Tests whether the mean-field CoM update scheme is causing the orbital instability
by comparing three Coulomb update schemes run in parallel:

  Scheme A (current): potential set from CoM BEFORE the tick
      V(t) = Coulomb(CoM(t))  applied during tick t
      This is what exp_12, exp_16, exp_18 all use.

  Scheme B (post-tick): potential set from CoM AFTER the previous tick
      V(t) = Coulomb(CoM(t-1))  -- half-tick less lag than scheme A in practice
      Same data, different timing: set potential immediately after ticking.

  Scheme C (midpoint average): potential is average of before and after CoM
      V(t) = Coulomb( (CoM(t) + CoM(t-1)) / 2 )
      Predictor-corrector: uses the midpoint of the previous step.

All three run at k=K_BOHR, TICKS=5000, same initialization.
If scheme A's instability is numerical lag, B or C should show meaningfully
better max_ok_streak or later first_escape.
If all three are similar, the instability is physical (not numerical lag).

Output: data/probe_pc_scheme_{A,B,C}.log and .npy
"""
import sys, os, numpy as np, time, subprocess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.core import OctahedralLattice, CausalSession, enforce_unity_spinor

OMEGA_E=0.1019; OMEGA_P=np.pi/2; STRENGTH=30.0; SOFTENING=0.5
WIDTH_E=1.5; WIDTH_P=0.5; R1=10.3
M_E=np.sin(OMEGA_E)/2; M_P=np.sin(OMEGA_P)/2
K_BOHR=1.0/R1; R_E_COM=R1; R_P_COM=R1*M_E/M_P
GRID=65; wc=(GRID//2,GRID//2,GRID//2)
TICKS=5000; CHECK_EVERY=50

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')

def dc(d):
    t=float(d.sum()); x=np.arange(d.shape[0],dtype=float)
    if t<1e-12: return (0.,0.,0.)
    return tuple(float(np.einsum(f'ijk,{c}->',d,x)/t) for c in ['i','j','k'])

def r_peak_rel(e_dens, p_com, n=60):
    g=e_dens.shape[0]; x=np.arange(g,dtype=float)
    xx,yy,zz=np.meshgrid(x,x,x,indexing='ij')
    radii=np.sqrt((xx-p_com[0])**2+(yy-p_com[1])**2+(zz-p_com[2])**2)
    bins=np.linspace(0,float(radii.max()),n+1)
    P,_=np.histogram(radii.ravel(),bins=bins,weights=e_dens.ravel())
    if P.sum()<1e-12: return 0.
    return float((0.5*(bins[:-1]+bins[1:]))[P.argmax()])

def coul(grid, cx, cy, cz):
    x=np.arange(grid,dtype=float); xx,yy,zz=np.meshgrid(x,x,x,indexing='ij')
    return -STRENGTH/(np.sqrt((xx-cx)**2+(yy-cy)**2+(zz-cz)**2)+SOFTENING)

def avg_com(c1, c2):
    return tuple(0.5*(c1[i]+c2[i]) for i in range(3))

def make_sessions():
    sz=GRID; dr_e=R_E_COM/np.sqrt(3); dr_p=R_P_COM/np.sqrt(3)
    se=tuple(min(int(round(wc[i]+dr_e)),sz-2) for i in range(3))
    sp=tuple(max(int(round(wc[i]-dr_p)),1) for i in range(3))
    kp=K_BOHR*M_E/M_P
    x=np.arange(sz); xx,yy,zz=np.meshgrid(x,x,x,indexing='ij')
    sx,sy,sz_=se
    ee=(np.exp(-0.5*((xx-sx)**2+(yy-sy)**2+(zz-sz_)**2)/WIDTH_E**2)
        *np.exp(1j*K_BOHR*(xx-yy-zz)))/np.sqrt(2.)
    le=OctahedralLattice(GRID,GRID,GRID); el=CausalSession(le,se,instruction_frequency=OMEGA_E)
    el.psi_R=ee.copy(); el.psi_L=ee.copy(); enforce_unity_spinor(el.psi_R,el.psi_L)
    px,py,pz=sp
    pe=(np.exp(-0.5*((xx-px)**2+(yy-py)**2+(zz-pz)**2)/WIDTH_P**2)
        *np.exp(1j*kp*(-xx+yy+zz)))/np.sqrt(2.)
    lp=OctahedralLattice(GRID,GRID,GRID); pr=CausalSession(lp,sp,instruction_frequency=OMEGA_P)
    pr.psi_R=pe.copy(); pr.psi_L=pe.copy(); enforce_unity_spinor(pr.psi_R,pr.psi_L)
    ec=dc(el.probability_density()); pc=dc(pr.probability_density())
    el.lattice.topological_potential=coul(GRID,*pc)
    pr.lattice.topological_potential=coul(GRID,*ec)
    return el, pr


def run_scheme(scheme, label):
    """
    scheme: 'A' (pre-tick CoM), 'B' (post-tick CoM), 'C' (midpoint average)
    """
    log_path = os.path.join(DATA_DIR, f'probe_pc_scheme_{label}.log')
    npy_path = os.path.join(DATA_DIR, f'probe_pc_scheme_{label}.npy')

    el, pr = make_sessions()

    with open(log_path, 'w') as log:
        def out(s): print(s, flush=True); log.write(s+'\n'); log.flush()

        out(f'scheme={label}  description: {scheme}')
        out(f'R1={R1}  stable_window=[{R1*0.80:.1f},{R1*1.20:.1f}]  escape>{2*R1:.1f}')
        out(f'{"tick":>6}  {"r_pdf_win":>10}  {"r_com_inst":>11}  {"status":>8}')
        out('-'*48)

        win_dens=None; win_count=0; win_p_com=None
        t0=time.time(); r_pdf_series=[]; first_escape=-1; ok_streak=0; max_ok_streak=0

        # Previous-tick CoM for schemes B and C
        prev_ec = dc(el.probability_density())
        prev_pc = dc(pr.probability_density())

        for tick in range(TICKS):
            # ── Compute potentials according to scheme ────────────────────────
            if scheme == 'A':
                # Current (pre-tick): use CoM right now, before ticking
                cur_ec = dc(el.probability_density())
                cur_pc = dc(pr.probability_density())
                el.lattice.topological_potential = coul(GRID, *cur_pc)
                pr.lattice.topological_potential = coul(GRID, *cur_ec)

            elif scheme == 'B':
                # Post-tick from previous step: potential already set at end of last tick
                # Just tick — potential was set to post-tick CoM at end of last iteration
                pass  # potential set at bottom of loop

            elif scheme == 'C':
                # Midpoint: average of previous post-tick CoM and current pre-tick CoM
                cur_ec = dc(el.probability_density())
                cur_pc = dc(pr.probability_density())
                mid_ec = avg_com(prev_ec, cur_ec)
                mid_pc = avg_com(prev_pc, cur_pc)
                el.lattice.topological_potential = coul(GRID, *mid_pc)
                pr.lattice.topological_potential = coul(GRID, *mid_ec)

            # ── Tick ──────────────────────────────────────────────────────────
            if tick%2==0: pr.tick(); pr.advance_tick_counter(); el.tick(); el.advance_tick_counter()
            else:         el.tick(); el.advance_tick_counter(); pr.tick(); pr.advance_tick_counter()

            # ── Post-tick CoM (for schemes B and C next iteration) ────────────
            post_ec = dc(el.probability_density())
            post_pc = dc(pr.probability_density())

            if scheme == 'B':
                # Set potential from post-tick CoM for next tick
                el.lattice.topological_potential = coul(GRID, *post_pc)
                pr.lattice.topological_potential = coul(GRID, *post_ec)

            prev_ec = post_ec
            prev_pc = post_pc

            # ── Windowed density accumulation ─────────────────────────────────
            e_dens=el.probability_density()
            if win_dens is None: win_dens=e_dens.astype(float)
            else: win_dens+=e_dens
            win_count+=1
            if win_count==CHECK_EVERY//2:
                win_p_com=dc(pr.probability_density())

            if (tick+1)%CHECK_EVERY==0:
                if win_p_com is None: win_p_com=dc(pr.probability_density())
                r_pdf=r_peak_rel(win_dens, win_p_com)
                r_com=float(np.sqrt(sum((post_ec[i]-post_pc[i])**2 for i in range(3))))
                r_pdf_series.append(r_pdf)

                status='OK' if abs(r_pdf-R1)/R1<0.20 else ('ESCAPE' if r_pdf>2*R1 else 'DRIFT')
                if status=='OK': ok_streak+=1; max_ok_streak=max(max_ok_streak,ok_streak)
                else: ok_streak=0
                if status=='ESCAPE' and first_escape<0: first_escape=tick+1

                out(f'{tick+1:6d}  {r_pdf:10.2f}  {r_com:11.2f}  {status:>8}  [{time.time()-t0:.0f}s]')
                win_dens=None; win_count=0; win_p_com=None

        out('')
        out(f'first_escape={first_escape if first_escape>0 else f">{TICKS}"}')
        stable=sum(1 for r in r_pdf_series if abs(r-R1)/R1<0.20)
        out(f'ok_windows={stable}/{len(r_pdf_series)}  max_ok_streak={max_ok_streak}')
        out(f'r_pdf: min={min(r_pdf_series):.2f}  max={max(r_pdf_series):.2f}  mean={np.mean(r_pdf_series):.2f}')

    np.save(npy_path, np.array(r_pdf_series))
    print(f'Saved: {npy_path}', flush=True)


if __name__ == '__main__':
    # Run all three schemes in parallel as subprocesses
    import subprocess

    schemes = [
        ('A', 'pre-tick CoM (current scheme)'),
        ('B', 'post-tick CoM (half-lag reduction)'),
        ('C', 'midpoint average (predictor-corrector)'),
    ]

    # If called with a scheme argument, run that scheme directly
    if len(sys.argv) == 2 and sys.argv[1] in ('A', 'B', 'C'):
        label = sys.argv[1]
        desc  = dict(schemes)[label]
        run_scheme(label, label)
        sys.exit(0)

    # Otherwise launch all three in parallel
    print('Launching 3 parallel scheme tests...', flush=True)
    procs = []
    for label, desc in schemes:
        cmd = [sys.executable, '-u', __file__, label]
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f'  Scheme {label}: PID {p.pid}  ({desc})')
        procs.append((label, desc, p))

    print()
    t0 = time.time()
    while any(p.poll() is None for _, _, p in procs):
        done = [l for l, _, p in procs if p.poll() is not None]
        running = [l for l, _, p in procs if p.poll() is None]
        print(f'[{time.time()-t0:.0f}s] running={running}  done={done}', flush=True)
        time.sleep(120)

    print(f'\nAll done. Total time: {time.time()-t0:.0f}s')
    print()
    print(f'{"Scheme":<8}  {"first_escape":<14}  {"ok_windows":<12}  {"max_streak":<11}  r_pdf range')
    print('-'*70)
    import re
    for label, desc, _ in schemes:
        log_path = os.path.join(DATA_DIR, f'probe_pc_scheme_{label}.log')
        txt = open(log_path).read()
        fe  = re.search(r'first_escape=(\S+)', txt)
        ok  = re.search(r'ok_windows=(\S+)', txt)
        mok = re.search(r'max_ok_streak=(\d+)', txt)
        mn  = re.search(r'r_pdf: min=(\S+)', txt)
        mx  = re.search(r'max=(\S+)', txt)
        print(f'  {label:<6}  {(fe.group(1) if fe else "?"):<14}  '
              f'{(ok.group(1) if ok else "?"):<12}  '
              f'{(mok.group(1) if mok else "?"):<11}  '
              f'[{mn.group(1) if mn else "?"}, {mx.group(1) if mx else "?"}]')
        print(f'         ({desc})')
