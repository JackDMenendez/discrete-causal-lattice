"""Quick probe: does the PDF peak metric see ~R1 during the oscillating exp_18 orbit?"""
import sys, numpy as np, time
sys.path.append('d:/sandbox/jackd/repos/physics/Papers/discrete-causal-lattice')
from src.core import OctahedralLattice, CausalSession, enforce_unity_spinor

OMEGA_E=0.1019; OMEGA_P=np.pi/2; STRENGTH=30.0; SOFTENING=0.5
WIDTH_E=1.5; WIDTH_P=0.5; R1=10.3
M_E=np.sin(OMEGA_E)/2; M_P=np.sin(OMEGA_P)/2
K_BOHR=1.0/R1; R_E_COM=R1; R_P_COM=R1*M_E/M_P
GRID=65; wc=(GRID//2,GRID//2,GRID//2)

def dc(d):
    t=float(d.sum()); x=np.arange(d.shape[0],dtype=float)
    if t<1e-12: return (0.,0.,0.)
    return tuple(float(np.einsum(f'ijk,{c}->',d,x)/t) for c in ['i','j','k'])

def cr(a,b): return float(np.sqrt(sum((a[i]-b[i])**2 for i in range(3))))

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
el.lattice.topological_potential=coul(GRID,*pc); pr.lattice.topological_potential=coul(GRID,*ec)

t0=time.time(); consec=0
print(f't=0  r_com={cr(ec,pc):.2f}  r_pdf={r_peak_rel(el.probability_density(),pc):.2f}  window=[{R1*0.85:.2f},{R1*1.15:.2f}]', flush=True)
for tick in range(1000):
    ec=dc(el.probability_density()); pc=dc(pr.probability_density())
    el.lattice.topological_potential=coul(GRID,*pc); pr.lattice.topological_potential=coul(GRID,*ec)
    if tick%2==0: pr.tick(); pr.advance_tick_counter(); el.tick(); el.advance_tick_counter()
    else:         el.tick(); el.advance_tick_counter(); pr.tick(); pr.advance_tick_counter()
    if (tick+1)%100==0:
        ec2=dc(el.probability_density()); pc2=dc(pr.probability_density())
        r_com=cr(ec2,pc2); r_pdf=r_peak_rel(el.probability_density(),pc2)
        ok=abs(r_pdf-R1)/R1<0.15
        if ok: consec+=1
        else: consec=0
        print(f't={tick+1:4d}  r_com={r_com:.2f}  r_pdf={r_pdf:.2f}  consec={consec}  [{time.time()-t0:.0f}s]', flush=True)
        if consec>=5: print('SETTLED'); break
