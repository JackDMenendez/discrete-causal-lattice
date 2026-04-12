"""
probe_exp18_stability.py

Diagnostic: does the exp_12 two-body initialization produce a genuinely stable
orbit, or a metastable transient?

Runs the exp_12 best case (k=0.0970, K_BOHR) for 5000 ticks with g=0,
reporting r_pdf (windowed 50-tick average, relative to live proton CoM) and
instantaneous electron-proton CoM separation every 50 ticks.

Also checks:
- Does r_pdf stay within 20% of R1 throughout? (stability criterion)
- When does it first exceed 2*R1? (escape tick)
- Is there any window where r_pdf < R1 * 0.5? (collapse to proton)

If the orbit is genuinely stable, r_pdf should fluctuate near R1 indefinitely.
If metastable, it will drift outward and eventually escape.
"""
import sys, os, numpy as np, time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.core import OctahedralLattice, CausalSession, enforce_unity_spinor

OMEGA_E=0.1019; OMEGA_P=np.pi/2; STRENGTH=30.0; SOFTENING=0.5
WIDTH_E=1.5; WIDTH_P=0.5; R1=10.3
M_E=np.sin(OMEGA_E)/2; M_P=np.sin(OMEGA_P)/2
K_BOHR=1.0/R1; R_E_COM=R1; R_P_COM=R1*M_E/M_P
GRID=65; wc=(GRID//2,GRID//2,GRID//2)
TICKS=100000; CHECK_EVERY=50

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

def coul(g,cx,cy,cz):
    x=np.arange(g,dtype=float); xx,yy,zz=np.meshgrid(x,x,x,indexing='ij')
    return -STRENGTH/(np.sqrt((xx-cx)**2+(yy-cy)**2+(zz-cz)**2)+SOFTENING)

# Init (identical to exp_18)
sz=GRID; dr_e=R_E_COM/np.sqrt(3); dr_p=R_P_COM/np.sqrt(3)
se=tuple(min(int(round(wc[i]+dr_e)),sz-2) for i in range(3))
sp=tuple(max(int(round(wc[i]-dr_p)),1) for i in range(3))
kp=K_BOHR*M_E/M_P; x=np.arange(sz); xx,yy,zz=np.meshgrid(x,x,x,indexing='ij')
sx,sy,sz_=se
ee=(np.exp(-0.5*((xx-sx)**2+(yy-sy)**2+(zz-sz_)**2)/WIDTH_E**2)*np.exp(1j*K_BOHR*(xx-yy-zz)))/np.sqrt(2.)
le=OctahedralLattice(GRID,GRID,GRID); el=CausalSession(le,se,instruction_frequency=OMEGA_E)
el.psi_R=ee.copy(); el.psi_L=ee.copy(); enforce_unity_spinor(el.psi_R,el.psi_L)
px,py,pz=sp
pe=(np.exp(-0.5*((xx-px)**2+(yy-py)**2+(zz-pz)**2)/WIDTH_P**2)*np.exp(1j*kp*(-xx+yy+zz)))/np.sqrt(2.)
lp=OctahedralLattice(GRID,GRID,GRID); pr=CausalSession(lp,sp,instruction_frequency=OMEGA_P)
pr.psi_R=pe.copy(); pr.psi_L=pe.copy(); enforce_unity_spinor(pr.psi_R,pr.psi_L)

ec=dc(el.probability_density()); pc=dc(pr.probability_density())
el.lattice.topological_potential=coul(GRID,*pc)
pr.lattice.topological_potential=coul(GRID,*ec)

print(f'R1={R1}  stable_window=[{R1*0.80:.1f},{R1*1.20:.1f}]  escape>{2*R1:.1f}')
print(f'{"tick":>6}  {"r_pdf_win":>10}  {"r_com_inst":>11}  {"status":>12}')
print('-'*50, flush=True)

win_dens=None; win_count=0; win_p_com=None
t0=time.time()
r_pdf_series=[]
first_escape=-1

for tick in range(TICKS):
    ec=dc(el.probability_density()); pc=dc(pr.probability_density())
    el.lattice.topological_potential=coul(GRID,*pc)
    pr.lattice.topological_potential=coul(GRID,*ec)
    if tick%2==0: pr.tick(); pr.advance_tick_counter(); el.tick(); el.advance_tick_counter()
    else:         el.tick(); el.advance_tick_counter(); pr.tick(); pr.advance_tick_counter()

    e_dens=el.probability_density()
    if win_dens is None: win_dens=e_dens.astype(float)
    else: win_dens += e_dens
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
        if status=='ESCAPE' and first_escape<0: first_escape=tick+1
        print(f'{tick+1:6d}  {r_pdf:10.2f}  {r_com:11.2f}  {status:>12}  [{time.time()-t0:.0f}s]', flush=True)

        win_dens=None; win_count=0; win_p_com=None

print()
print(f'First escape tick: {first_escape if first_escape>0 else f">{ TICKS}"}')
stable_windows=sum(1 for r in r_pdf_series if abs(r-R1)/R1<0.20)
print(f'Windows within 20% of R1: {stable_windows}/{len(r_pdf_series)}')
print(f'r_pdf min={min(r_pdf_series):.2f}  max={max(r_pdf_series):.2f}  mean={np.mean(r_pdf_series):.2f}')
_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
_NPY = os.path.join(_DATA_DIR, 'probe_exp18_stability.npy')
np.save(_NPY, np.array(r_pdf_series))
print(f'Saved: {_NPY}')
