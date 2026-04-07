"""
probe_stability_worker.py

Parameterized stability probe. Called with command-line arguments:
    python probe_stability_worker.py <k_init> <update_every> <run_id>

Runs a two-body hydrogen stability test:
  k_init       -- electron phase gradient (e.g. 0.097)
  update_every -- how often to recompute Coulomb CoM (1=every tick, 5=every 5 ticks)
  run_id       -- label for output files (e.g. "k0.097_lag1")

Output: data/probe_stability_<run_id>.log  (printed per-window)
        data/probe_stability_<run_id>.npy  (r_pdf_series array)
"""
import sys, os, numpy as np, time
sys.path.append('d:/sandbox/jackd/repos/physics/Papers/discrete-causal-lattice')
from src.core import OctahedralLattice, CausalSession, enforce_unity_spinor

# ── CLI args ──────────────────────────────────────────────────────────────────
if len(sys.argv) != 4:
    print('Usage: probe_stability_worker.py <k_init> <update_every> <run_id>')
    sys.exit(1)

K_INIT       = float(sys.argv[1])
UPDATE_EVERY = int(sys.argv[2])
RUN_ID       = sys.argv[3]

# ── Fixed parameters ──────────────────────────────────────────────────────────
OMEGA_E=0.1019; OMEGA_P=np.pi/2; STRENGTH=30.0; SOFTENING=0.5
WIDTH_E=1.5; WIDTH_P=0.5; R1=10.3
M_E=np.sin(OMEGA_E)/2; M_P=np.sin(OMEGA_P)/2
R_E_COM=R1; R_P_COM=R1*M_E/M_P
GRID=65; wc=(GRID//2,GRID//2,GRID//2)
TICKS=5000; CHECK_EVERY=50

DATA_DIR = 'd:/sandbox/jackd/repos/physics/Papers/discrete-causal-lattice/data'
LOG_FILE = os.path.join(DATA_DIR, f'probe_stability_{RUN_ID}.log')
NPY_FILE = os.path.join(DATA_DIR, f'probe_stability_{RUN_ID}.npy')

# ── Helpers ───────────────────────────────────────────────────────────────────
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

def coul(grid,cx,cy,cz):
    x=np.arange(grid,dtype=float); xx,yy,zz=np.meshgrid(x,x,x,indexing='ij')
    return -STRENGTH/(np.sqrt((xx-cx)**2+(yy-cy)**2+(zz-cz)**2)+SOFTENING)

# ── Initialization ────────────────────────────────────────────────────────────
sz=GRID; dr_e=R_E_COM/np.sqrt(3); dr_p=R_P_COM/np.sqrt(3)
se=tuple(min(int(round(wc[i]+dr_e)),sz-2) for i in range(3))
sp=tuple(max(int(round(wc[i]-dr_p)),1) for i in range(3))
kp=K_INIT*M_E/M_P
x=np.arange(sz); xx,yy,zz=np.meshgrid(x,x,x,indexing='ij')
sx,sy,sz_=se
ee=(np.exp(-0.5*((xx-sx)**2+(yy-sy)**2+(zz-sz_)**2)/WIDTH_E**2)
    *np.exp(1j*K_INIT*(xx-yy-zz)))/np.sqrt(2.)
le=OctahedralLattice(GRID,GRID,GRID); el=CausalSession(le,se,instruction_frequency=OMEGA_E)
el.psi_R=ee.copy(); el.psi_L=ee.copy(); enforce_unity_spinor(el.psi_R,el.psi_L)

px,py,pz=sp
pe=(np.exp(-0.5*((xx-px)**2+(yy-py)**2+(zz-pz)**2)/WIDTH_P**2)
    *np.exp(1j*kp*(-xx+yy+zz)))/np.sqrt(2.)
lp=OctahedralLattice(GRID,GRID,GRID); pr=CausalSession(lp,sp,instruction_frequency=OMEGA_P)
pr.psi_R=pe.copy(); pr.psi_L=pe.copy(); enforce_unity_spinor(pr.psi_R,pr.psi_L)

# Initial potentials
ec=dc(el.probability_density()); pc=dc(pr.probability_density())
el.lattice.topological_potential=coul(GRID,*pc)
pr.lattice.topological_potential=coul(GRID,*ec)

# ── Run ───────────────────────────────────────────────────────────────────────
with open(LOG_FILE, 'w') as log:
    def out(s): print(s, flush=True); log.write(s+'\n'); log.flush()

    out(f'run_id={RUN_ID}  k_init={K_INIT:.4f}  update_every={UPDATE_EVERY}')
    out(f'R1={R1}  stable_window=[{R1*0.80:.1f},{R1*1.20:.1f}]  escape>{2*R1:.1f}')
    out(f'{"tick":>6}  {"r_pdf_win":>10}  {"r_com_inst":>11}  {"status":>8}')
    out('-'*48)

    win_dens=None; win_count=0; win_p_com=None
    cached_ec=ec; cached_pc=pc   # cached CoM for lag test
    t0=time.time(); r_pdf_series=[]; first_escape=-1; ok_streak=0; max_ok_streak=0

    for tick in range(TICKS):
        # Update Coulomb potential every UPDATE_EVERY ticks
        if tick % UPDATE_EVERY == 0:
            cached_ec=dc(el.probability_density())
            cached_pc=dc(pr.probability_density())
            el.lattice.topological_potential=coul(GRID,*cached_pc)
            pr.lattice.topological_potential=coul(GRID,*cached_ec)

        if tick%2==0: pr.tick(); pr.advance_tick_counter(); el.tick(); el.advance_tick_counter()
        else:         el.tick(); el.advance_tick_counter(); pr.tick(); pr.advance_tick_counter()

        # Windowed density accumulation
        e_dens=el.probability_density()
        if win_dens is None: win_dens=e_dens.astype(float)
        else: win_dens+=e_dens
        win_count+=1
        if win_count==CHECK_EVERY//2:
            win_p_com=dc(pr.probability_density())

        if (tick+1)%CHECK_EVERY==0:
            if win_p_com is None: win_p_com=dc(pr.probability_density())
            r_pdf=r_peak_rel(win_dens, win_p_com)
            ec2=dc(el.probability_density()); pc2=dc(pr.probability_density())
            r_com=float(np.sqrt(sum((ec2[i]-pc2[i])**2 for i in range(3))))
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

np.save(NPY_FILE, np.array(r_pdf_series))
print(f'Saved: {NPY_FILE}')
