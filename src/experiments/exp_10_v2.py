"""
exp_10_v2.py  -- Hydrogen Spectrum, Corrected Approach

Key insight from previous run:
  With k_tang=0.1, the n=1 stable orbit is NOT at r=10.3 but at r~30.
  The Bohr condition k*r=n with k=0.1 gives r_1 = 1/0.1 = 10,
  but the actual stable radius is larger because the packet spreads.

Revised approach:
  1. Run n=1 with k=0.1 and MEASURE r_stable (don't assume r=10.3)
  2. Predict r_2 = 4 * r_stable
  3. Run n=2 with k=0.05 (half the k, twice the r: k*r = n = 2)
     Wait -- for n=2: k_2 = n/r_2 = 2/(4*r_1) = 1/(2*r_1) = k_1/2
  4. Compare E_2/E_1

The stable radius is self-consistent: whatever radius the n=1 orbit
actually settles at, that IS r_1, and r_2 should be 4x that.

Usage:
    python exp_10_v2.py --profile
    python exp_10_v2.py
"""

import sys, os, time, argparse
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

RGB = [(1,1,1),(1,-1,-1),(-1,1,-1)]
CMY = [(-1,-1,-1),(-1,1,1),(1,-1,1)]
ALL = RGB + CMY

STRENGTH  = 30.0
SOFTENING = 0.5
OMEGA     = 0.1019
WIDTH     = 1.5
TICKS_N1  = 600    # long enough to find stable r
TICKS_N2  = 600


def coulomb(grid, wc, S, eps):
    x=np.arange(grid); y=np.arange(grid); z=np.arange(grid)
    xx,yy,zz=np.meshgrid(x,y,z,indexing='ij')
    r=np.sqrt((xx-wc[0])**2+(yy-wc[1])**2+(zz-wc[2])**2)
    return -S/(r+eps)

def enforce_unity(psi):
    n=np.sqrt(np.sum(np.abs(psi)**2))
    if n<1e-12: raise RuntimeError("collapsed")
    psi/=n; return psi

def make_psi(grid, start, wc, k_tang, width):
    x=np.arange(grid); y=np.arange(grid); z=np.arange(grid)
    xx,yy,zz=np.meshgrid(x,y,z,indexing='ij')
    sx,sy,sz=start
    rr=(xx-sx)**2+(yy-sy)**2+(zz-sz)**2
    ph=k_tang*(xx-yy-zz)
    psi=(np.exp(-0.5*rr/width**2)*np.exp(1j*ph)).astype(complex)
    enforce_unity(psi)
    return psi,xx,yy,zz

def tick(psi,V,omega,tp):
    dphi=omega+V
    ps=np.sin(dphi/2)**2; pm=np.cos(dphi/2)**2
    pf=np.exp(1j*dphi)
    new=psi*np.sqrt(ps)
    lp=np.angle(psi); n_v=len(ALL)
    w=np.zeros((n_v,)+psi.shape,dtype=float)
    for i,(dx,dy,dz) in enumerate(ALL):
        nb=np.roll(np.roll(np.roll(psi,-dx,0),-dy,1),-dz,2)
        na=np.abs(nb)
        np_=np.where(na>1e-9,np.angle(nb),lp)
        w[i]=np.maximum(0,np.cos(np_-lp)/(1+omega))
    tw=w.sum(0); tw=np.where(tw<1e-12,1.0,tw); w/=tw[np.newaxis]
    sx,sy,sz=psi.shape; sp=np.sqrt(pm)
    for i,(dx,dy,dz) in enumerate(ALL):
        em=psi*pf*sp*w[i]
        mk=np.ones((sx,sy,sz),dtype=bool)
        if dx>0: mk[sx-dx:,:,:]=False
        if dx<0: mk[:-dx,:,:]=False
        if dy>0: mk[:,sy-dy:,:]=False
        if dy<0: mk[:,:-dy,:]=False
        if dz>0: mk[:,:,sz-dz:]=False
        if dz<0: mk[:,:,:-dz]=False
        new+=np.roll(np.roll(np.roll(np.where(mk,em,0),dx,0),dy,1),dz,2)
    enforce_unity(new); return new

def run(psi,V,omega,wc,ticks,rep=50):
    peaks=[]
    t0=time.time()
    for t in range(ticks):
        psi=tick(psi,V,omega,t%2)
        d=np.abs(psi)**2
        idx=np.unravel_index(np.argmax(d),d.shape)
        peaks.append(float(np.sqrt(sum((idx[i]-wc[i])**2 for i in range(3)))))
        if (t+1)%rep==0:
            el=time.time()-t0
            eta=el/(t+1)*(ticks-t-1)
            print(f"    tick {t+1:4d}/{ticks}  r={peaks[-1]:.3f}  {el:.0f}s  ETA={eta:.0f}s")
    return peaks,psi

def stable_r(dists, last_frac=0.4):
    """Stable orbit radius = mean of last 40% of ticks."""
    n=int(len(dists)*last_frac)
    return float(np.mean(dists[-n:]))

def run_hydrogen():
    print("="*65)
    print("EXP 10 v2: Hydrogen Spectrum -- Self-Consistent Approach")
    print("="*65)

    # ── Phase 1: find actual n=1 stable radius ────────────────────
    # Use a grid large enough that n=2 will fit (4x the stable r)
    # Start conservative: grid=80, measure r_1, then decide if we need bigger
    grid1 = 80
    wc1   = (grid1//2,)*3
    V1    = coulomb(grid1, wc1, STRENGTH, SOFTENING)

    # n=1: k=0.1, start at r~10 (V1 direction)
    dr1   = 6  # ~10/sqrt(3)
    start1= tuple(min(wc1[i]+dr1,grid1-3) for i in range(3))
    k1    = 0.10

    print(f"\nPhase 1: n=1 orbit  (k={k1}, grid={grid1}^3)")
    print(f"  Start: {start1}  (initial r ~ {np.sqrt(3)*dr1:.1f})")
    psi1,xx1,yy1,zz1 = make_psi(grid1,start1,wc1,k1,WIDTH)
    dists1,_ = run(psi1,V1,OMEGA,wc1,TICKS_N1)
    r1 = stable_r(dists1)
    E1 = -STRENGTH/(r1+SOFTENING)
    np.save('orbit_n1_v2.npy',np.array(dists1))

    print(f"\n  n=1 stable radius: r_1 = {r1:.3f} nodes")
    print(f"  n=1 energy:        E_1 = {E1:.6f}")
    print(f"  Predicted r_2 = 4 * r_1 = {4*r1:.1f} nodes")
    print(f"  Predicted E_2 = E_1/4   = {E1/4:.6f}")

    r2_target = 4.0 * r1
    k2        = 2.0 / r2_target   # L = k*r = n=2

    # Check if r_2 fits in grid1
    dr2 = int(round(r2_target/np.sqrt(3)))
    grid2_needed = 2*(dr2+10)+1
    print(f"\n  k_2 = {k2:.5f}  dr2_hops = {dr2}")
    print(f"  Grid needed for n=2: {grid2_needed}^3  "
          f"({grid2_needed**3:,} nodes, {grid2_needed**3*16/1e6:.0f} MB)")

    if grid2_needed > 250:
        print("  WARNING: very large grid -- may be slow")

    # ── Phase 2: n=2 orbit ────────────────────────────────────────
    grid2 = max(grid1, grid2_needed)
    wc2   = (grid2//2,)*3
    V2    = coulomb(grid2, wc2, STRENGTH, SOFTENING)

    # Rescale n=1 orbit to grid2 if needed
    if grid2 != grid1:
        dr1_g2 = int(round(r1/np.sqrt(3)))
        start1_g2 = tuple(min(wc2[i]+dr1_g2,grid2-3) for i in range(3))
        print(f"\nPhase 1 re-run on grid={grid2}^3 for fair comparison:")
        psi1b,xx1b,yy1b,zz1b = make_psi(grid2,start1_g2,wc2,k1,WIDTH)
        dists1b,_ = run(psi1b,V2,OMEGA,wc2,TICKS_N1)
        r1  = stable_r(dists1b)
        E1  = -STRENGTH/(r1+SOFTENING)
        r2_target = 4*r1
        k2  = 2.0/r2_target
        np.save('orbit_n1_v2b.npy',np.array(dists1b))
        print(f"  r_1 (on grid={grid2}) = {r1:.3f}")

    start2 = tuple(min(wc2[i]+dr2,grid2-3) for i in range(3))
    print(f"\nPhase 2: n=2 orbit  (k={k2:.5f}, grid={grid2}^3)")
    print(f"  Start: {start2}  (initial r ~ {np.sqrt(3)*dr2:.1f})")
    psi2,xx2,yy2,zz2 = make_psi(grid2,start2,wc2,k2,WIDTH)
    dists2,_ = run(psi2,V2,OMEGA,wc2,TICKS_N2)
    r2 = stable_r(dists2)
    E2 = -STRENGTH/(r2+SOFTENING)
    np.save('orbit_n2_v2.npy',np.array(dists2))

    print(f"\n  n=2 stable radius: r_2 = {r2:.3f} nodes")
    print(f"  n=2 energy:        E_2 = {E2:.6f}")

    # ── Bohr test ─────────────────────────────────────────────────
    print("\n"+"="*65)
    print("BOHR SPECTRUM TEST")
    print("="*65)
    rr = r2/r1; Er = E2/E1
    pred_r = 4.0; pred_E = 0.25

    print(f"\n  r_2 / r_1 = {rr:.4f}   (Bohr predicts {pred_r:.4f})")
    print(f"  E_2 / E_1 = {Er:.4f}   (Bohr predicts {pred_E:.4f})")
    r_ok = abs(rr-pred_r)/pred_r < 0.15
    E_ok = abs(Er-pred_E)/pred_E < 0.10

    print()
    if r_ok and E_ok:
        print("╔══════════════════════════════════════════════════╗")
        print("║  CONFIRMED: r_2/r_1 ~ 4  AND  E_2/E_1 ~ 1/4    ║")
        print("║  Bohr hydrogen spectrum from A=1 lattice.        ║")
        print("╚══════════════════════════════════════════════════╝")
    elif r_ok:
        print(f"  r scaling: CONFIRMED (r_2/r_1 = {rr:.3f} ~ 4)")
        print(f"  E scaling: {Er:.4f} vs 0.25 -- off by {abs(Er-0.25)/0.25*100:.0f}%")
        print("  The orbit radii are right but E needs better r_mean measurement.")
    elif E_ok:
        print(f"  E scaling: CONFIRMED (E_2/E_1 = {Er:.4f} ~ 0.25)")
        print(f"  r scaling: {rr:.3f} vs 4.0 -- orbit drifted")
    else:
        print(f"  r_2/r_1 = {rr:.3f}  E_2/E_1 = {Er:.3f}")
        print("  Neither confirmed yet. Check orbit stability in .npy files.")
        print("  Try: python analyze_orbits_v2.py")

def profile():
    print("Profiling...")
    for g in [65,80,100,130,160]:
        wc=(g//2,)*3
        V=coulomb(g,wc,STRENGTH,SOFTENING)
        dr=6; st=tuple(min(wc[i]+dr,g-3) for i in range(3))
        psi,_,_,_=make_psi(g,st,wc,0.1,WIDTH)
        n_t=3; t0=time.time()
        for t in range(n_t): psi=tick(psi,V,OMEGA,t%2)
        ms=(time.time()-t0)/n_t*1000
        eta_n12=ms*TICKS_N1*2/60000
        r2=int(round(4*np.sqrt(3)*6))
        g2=2*(r2+10)+1
        print(f"  grid={g:4d}^3  {g**3*16/1e6:4.0f}MB  {ms:6.0f}ms/tick  "
              f"n=1+2 ~{eta_n12:.0f}min  (n=2 needs grid~{g2})")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument('--profile',action='store_true')
    args=ap.parse_args()
    if args.profile: profile()
    else: run_hydrogen()
