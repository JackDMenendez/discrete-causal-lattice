# lattice_harmonics.md
# Harmonics in the T^3_diamond Lattice

## Core Idea
Harmonics arise wherever a wave is confined or where two frequencies
must be commensurate for constructive interference to persist.
In the A=1 bipartite lattice, there are at least four distinct
harmonic structures, each with a physical interpretation.

---

## 1. The Zitterbewegung Mass Spectrum

The mass term p_stay = sin^2(omega/2) is periodic in omega with period 2*pi.
This means omega and omega + 2*pi*n produce identical p_stay for all integers n.

Allowed mass values are:
  m_n ~ sin^2(omega_0/2 + n*pi)  for n = 0, 1, 2, ...

The mass spectrum is DISCRETE and PERIODIC in the frequency domain.
A particle with omega_0 = pi/6 has the same mass as one with omega_0 = pi/6 + 2*pi.
This is a geometric quantization of mass -- no Higgs mechanism needed.

Implication: the observed particle masses should correspond to
specific rational multiples of 2*pi that minimize some stability criterion.
The lightest stable particle has the smallest omega that is not zero.

---

## 2. The Vacuum Carrier Frequency

The bipartite tick alternates RGB/CMY at every tick.
This is a built-in oscillation at omega_vacuum = pi per tick (period = 2 ticks).

A particle with internal frequency omega propagating through the vacuum
sees its amplitude modulated by the carrier:
  effective_amplitude(t) ~ psi(t) * cos(omega_vacuum * t - omega * t)
                         = psi(t) * cos((pi - omega) * t)

RESONANCE CONDITION: omega = pi (beat frequency = 0)
At resonance the particle is perfectly phase-matched with the vacuum carrier.
Near resonance: slow beating, stable propagation.
Far from resonance: rapid phase mismatch, incoherence, decay.

This suggests a PREFERRED MASS at omega = pi:
  p_stay = sin^2(pi/2) = 1  -- maximum mass (always stays)
  This is the maximally inertial state.

And a MASSLESS STATE at omega = 0:
  p_stay = sin^2(0) = 0  -- photon (never stays)

The first excited resonance would be at omega = pi/2:
  p_stay = sin^2(pi/4) = 0.5  -- intermediate mass

---

## 3. Standing Waves and the Bohr Quantization

A wave packet in a clock-density well oscillates with orbital frequency:
  omega_orb = f(well_depth, well_width, particle_mass)

For a stable orbit: the Zitterbewegung frequency must be commensurate
with the orbital frequency:
  omega_zitt / omega_orb = p/q  (rational ratio)

This is the Bohr-Sommerfeld quantization condition, derived from
lattice resonance rather than postulated.

For hydrogen-like system:
  E_n ~ -1/n^2  means  omega_orb_n ~ 1/n^2 * omega_fundamental

Stable orbits occur when:
  omega_zitt = n^2 * omega_orb_fundamental

The energy levels are proportional to 1/n^2 IF the orbital frequency
scales as 1/n^2 with orbit size -- which follows from the 1/r^2
clock density gradient of a point mass.

TESTABLE PREDICTION:
  Simulate a particle (omega_zitt) in a Gaussian clock density well.
  Measure the orbital frequency omega_orb as a function of orbit radius.
  The stable radii should satisfy omega_zitt / omega_orb = integer.
  The ratio of stable energies should be 1 : 1/4 : 1/9 : ...

---

## 4. Path Length Resonances and the de Broglie Relation

From exp_06: the path count P(N, dx, dy, dz) has discrete structure.
For a given displacement, only certain hop counts N produce large P.
These are the resonant propagation lengths.

The de Broglie wavelength lambda = h / p maps to:
  lambda_lattice = 2*pi / k_momentum

where k_momentum is the phase gradient encoding momentum.

For a wave to be self-reinforcing (stable particle), it must satisfy:
  N * lambda_lattice = integer * (lattice_circumference)

This is the Wilson-Sommerfeld quantization condition in lattice form.
The allowed momenta are:
  k_n = 2*pi*n / (circumference_in_lattice_hops)

---

## 5. Crystal Analogy: Brillouin Zones

The diagonal FCC-like basis vectors of T^3_diamond generate a reciprocal
lattice in momentum space. The first Brillouin zone of an FCC lattice
is a truncated octahedron -- the same shape as the causal cone.

Allowed phonon (photon) wavevectors are confined to this zone.
The zone boundaries are where Bragg reflection occurs:
  2 * d * sin(theta) = n * lambda  (Bragg condition)

In the lattice: wavevectors at the zone boundary experience
total constructive-destructive interference -- they become standing waves.
These are the lattice's natural resonant frequencies.

The photon dispersion relation in the lattice should be:
  omega(k) = c * |k|  for |k| << pi/a  (linear -- massless)
  omega(k) = c * sin(|k|*a/2) / (a/2)  near zone boundary (nonlinear)

The nonlinearity near the zone boundary is a FALSIFIABLE PREDICTION:
photon group velocity decreases near the Planck scale.

---

## 6. Temporal Harmonics: The Tick Spectrum

The TickScheduler processes n sessions per macro-tick.
The macro-tick has a characteristic frequency omega_macro = 1/n.
Sessions with internal frequencies that are rational multiples of
omega_macro will be in resonance with the scheduler.

This is a CLOCK SYNCHRONIZATION problem -- the same mathematics
as frequency locking in coupled oscillators (Kuramoto model).
Particles with incommensurate frequencies may undergo frequency
pulling toward the nearest rational multiple of omega_macro.

This could be the mechanism behind:
  - Particle decay: omega drifts away from resonance -> p_stay decreases -> decay
  - Particle stability: omega locks to a rational multiple -> stable resonance
  - The integer charge quantization of EM: charge = winding number of
    phase resonance with the vacuum carrier frequency

---

## Experimental Program (exp_09)

### Part A: Zitterbewegung Frequency Scan
Sweep omega from 0 to 2*pi.
For each omega, measure:
  - p_stay (mass)
  - propagation coherence length (stability)
  - interference contrast with a reference packet

Expected: stability peaks at omega = 0, pi/3, pi/2, 2pi/3, pi, ...
(rational multiples of pi)

### Part B: Orbital Resonance
Place a test particle (varying omega) in a Gaussian clock-density well.
Measure:
  - Orbital period T_orb as function of orbit radius r
  - Stable orbit radii (where packet maintains coherence over many orbits)
  - Energy of stable orbits E_n

Expected: E_n proportional to 1/n^2 if the system is hydrogen-like.
If confirmed: this is the Bohr spectrum from lattice geometry.

### Part C: Brillouin Zone Signature
Initialize a photon (omega=0, is_massless=True) with varying k.
Measure group velocity d(omega)/dk as a function of |k|.
Expected:
  - Linear dispersion for small k (v_group = c)
  - Nonlinear dispersion near zone boundary k ~ pi/a
  - Zero group velocity at zone boundary (standing wave)

### Part D: Temporal Locking
Register multiple sessions with incommensurate frequencies.
Run TickScheduler for many ticks.
Measure whether frequencies drift toward rational multiples of each other.
Expected: Kuramoto-like synchronization in the clock ensemble.

---

## Connection to Known Physics

| Lattice harmonic          | Known physics analog         | Section  |
|---------------------------|------------------------------|----------|
| sin^2(omega/2) periodicity| Mass quantization            | 3        |
| Vacuum carrier pi/tick    | Zitterbewegung resonance     | 3        |
| Orbital commensurability  | Bohr-Sommerfeld quantization | 9        |
| Path length resonance     | de Broglie relation          | 9        |
| Brillouin zone boundary   | Photon dispersion at Planck  | 9        |
| Temporal locking          | Charge quantization (?)      | 4        |

---

## Open Questions

1. Do the stable omega values (resonances with vacuum carrier)
   match the observed particle mass ratios?
   electron : muon : tau ~ 1 : 207 : 3477
   Is there a harmonic series that fits?

2. Does the orbital resonance condition reproduce the hydrogen
   spectrum to the precision of the Rydberg constant?

3. Is temporal frequency locking the mechanism behind
   integer electric charge quantization?

4. The FCC Brillouin zone is a truncated octahedron.
   Is this why the causal cone has octahedral symmetry?
   (I.e., is the causal cone the real-space dual of the
   momentum-space Brillouin zone?)

---

## exp_10 Results (Current Status)

### What works:
- Genuine orbital motion confirmed: packets orbit Coulomb well
  with measurable period (~87-94 ticks at r=4)
- Orbital period decreases with omega as predicted
- Quantization condition omega * T / (2*pi) = n finds n=1 and n=2 states
- The n=1 state at omega/pi~0.021, T~87
- The n=2 state at omega/pi~0.059, T~69

### What needs work:
- To test E_n ~ 1/n^2, need n=1 and n=2 for the SAME particle (same omega)
  at different orbit radii (r_1, r_2 = 2*r_1)
- Current approach varies omega -- this conflates mass with quantum number
- Correct approach: fix omega, vary initial radius, find resonant radii r_n
  where the SAME particle has T_orb satisfying omega * T_orb_n = 2*pi*n

### Revised Plan:
  Fix omega (e.g. omega=0.05)
  Sweep initial radius from r=3 to r=12
  For each radius: measure T_orb
  Find radii where omega * T_orb / (2*pi) is closest to integer n
  Those are the Bohr radii a_n
  Measure energies at those radii: E ~ -strength/(a_n + softening)
  Check: E_n / E_1 ~ 1/n^2

### Force Law Note:
- The 1/r^2 fit gives alpha ~ -0.05 (nearly flat) rather than 2.0
- This is because the Zitterbewegung spreading dominates over the
  Coulomb attraction at these packet sizes
- Need narrower packets (width=1.0) and larger strength for cleaner force law

---

## Hydrogen Spectrum: Theoretical Issue Found (exp_10)

### The Quantization Mismatch
The Bohr-Sommerfeld condition we implemented is:
    omega_zitt * T_orb = 2*pi*n

But with Keplerian orbits (T_orb ~ r^(3/2)):
    This gives r_n ~ n^(2/3), NOT n^2

The Bohr model uses de Broglie quantization:
    n * lambda_deBroglie = 2 * pi * r_n
    => p * r_n = n * hbar
    => m*v*r_n = n*hbar  (angular momentum quantization)
    
This gives r_n ~ n^2 because lambda ~ 1/p and orbital v ~ 1/sqrt(r).

### The Lattice Version of Angular Momentum Quantization
In the A=1 framework, angular momentum should be:
    L = r_orb * p_tangential = r_orb * (k_V2 * hbar_lattice)
    
Quantization: L = n * hbar_lattice
    => k_V2 = n / r_orb
    
So to find Bohr levels, sweep BOTH r0 and k_V2 such that k_V2*r_orb = n.
For n=1: k=1/r; for n=2: k=2/r -- try different (r,k) combinations.
For each that satisfies k*r~n: measure energy E.
Check E_n ~ 1/n^2.

### Next Experiment
Fix omega (mass). 
For n=1: try (r=5, k=0.2), (r=6, k=0.167), (r=8, k=0.125) -- all k*r~1
For n=2: try (r=5, k=0.4), (r=6, k=0.333), (r=8, k=0.25) -- all k*r~2
For each group: measure the stable orbit and its energy.
Compare E(n=1) vs E(n=2): should be 4:1 ratio.
