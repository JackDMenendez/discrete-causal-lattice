"""
Probe: does time-averaged electron density (last 1000 ticks of 3000) peak near R1?
Uses same parameters as exp_18 to validate the settle criterion.
"""
import sys, numpy as np, time
sys.path.append('d:/sandbox/jackd/repos/physics/Papers/discrete-causal-lattice')
from src.core import OctahedralLattice, CausalSession, enforce_unity_spinor

OMEGA_E=0.1019; OMEGA_P=np.pi/2; STRENGTH=30.0; SOFTENING=0.5
WIDTH_E=1.5; WIDTH_P=0.5; R1=10.3
M_E=np.sin(OMEGA_E)/2; M_P=np.sin(OMEGA_P)/2
K_BOHR=1.0/R1; R_E_COM=R1; R_P_COM=R1*M_E/M_P
GRID=65; wc=(GRID//2,GRID//2,GRID//2)
TICKS_SETTLE=3000; TICKS_AVG=1000

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

# Initialization (same as exp_18)
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

# Initial potentials
ec=dc(el.probability_density()); pc=dc(pr.probability_density())
el.lattice.topological_potential=coul(GRID,*pc)
pr.lattice.topological_potential=coul(GRID,*ec)

# Run TICKS_SETTLE, accumulating density over last TICKS_AVG
acc_dens=None; acc_count=0; acc_p_com=None
t0=time.time()

for tick in range(TICKS_SETTLE):
    ec=dc(el.probability_density()); pc=dc(pr.probability_density())
    el.lattice.topological_potential=coul(GRID,*pc)
    pr.lattice.topological_potential=coul(GRID,*ec)
    if tick%2==0: pr.tick(); pr.advance_tick_counter(); el.tick(); el.advance_tick_counter()
    else:         el.tick(); el.advance_tick_counter(); pr.tick(); pr.advance_tick_counter()

    if tick >= TICKS_SETTLE - TICKS_AVG:
        e_dens=el.probability_density()
        if acc_dens is None: acc_dens=e_dens.astype(float)
        else: acc_dens += e_dens
        acc_count+=1
        if acc_count == TICKS_AVG//2:
            acc_p_com = dc(pr.probability_density())

    if (tick+1)%500==0:
        elapsed=time.time()-t0
        # Also show instantaneous r_pdf for comparison
        inst_dens=el.probability_density(); inst_pc=dc(pr.probability_density())
        r_inst=r_peak_rel(inst_dens, inst_pc)
        print(f't={tick+1:4d}  r_pdf_instant={r_inst:.2f}  acc_count={acc_count}  [{elapsed:.0f}s]', flush=True)

# Final settle check
if acc_p_com is None: acc_p_com=dc(pr.probability_density())
r_avg = r_peak_rel(acc_dens, acc_p_com)
settled = abs(r_avg - R1)/R1 < 0.20
print(f'\nSETTLE CHECK: r_avg_pdf={r_avg:.3f}  R1={R1}  error={abs(r_avg-R1)/R1*100:.1f}%  settled={settled}', flush=True)
print(f'Total time: {time.time()-t0:.0f}s')
