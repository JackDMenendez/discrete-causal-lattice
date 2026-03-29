# The A Structure in the Harmonic Landscape

*Observations from hires scan (exp_harmonic_hires.pdf), 2026-03-29*

---

## What Was Seen

In the high-resolution harmonic landscape (150 omega values), a capital-A shape
is visible, symmetrically centered on the 2:1 resonance star (omega=pi/2, f=0.25):

- Two diagonal legs meeting at a crossbar at the 2:1 star
- A broad band sweeping from the bottom-right, narrowing as it moves up and left
  to terminate at the left edge near the top of the A
- Perfect bilateral symmetry about the vertical line f=0.25

---

## Why the A Is Exact

The A is not a visual artifact. It is forced by the spinor structure of the lattice.

The bipartite lattice alternates: RGB hops (psi_R) on even ticks, CMY hops (psi_L)
on odd ticks. The tick-parity alternation runs at f_vacuum = 0.5 cycles/tick.

When psi_R oscillates at f_zitt = omega/(2*pi), psi_L is driven by the
complementary phase from the odd-tick structure and oscillates at:

    f_beat = 0.5 - f_zitt = f_vacuum - f_zitt

This is exact by construction -- f_beat IS the frequency of the left-handed
component when the right-handed component oscillates at f_zitt.

Mirror symmetry: f_beat is the reflection of f_zitt about f = 0.25 = f_vacuum/2.
The mirror plane is the midpoint of the vacuum carrier frequency.

The two diagonals are not independent oscillators. They are a single spinor
written in two components, reflected across the vacuum mirror.

---

## The 2:1 Fixed Point

f_zitt = f_beat has exactly one solution:

    omega/(2*pi) = 0.5 - omega/(2*pi)  =>  omega = pi/2

At the 2:1 fixed point:
- psi_R and psi_L oscillate at the same frequency (both 0.25 cycles/tick)
- The particle is maximally entangled between its spinor components
- This is the qubit operating point (p_stay = 0.5, equal time on both sublattices)
- T2 = 3 ticks at omega=pi/2 vs T2 = 2 ticks for all other omega values in the scan
  -- the coherence enhancement at the fixed point is already in the data

The 2:1 fixed point is the only omega where a particle's zitterbewegung frequency
coincides with its vacuum reflection. It is the fixed point of the mirror transformation.

---

## Physical Interpretation

The A structure is particle-antiparticle symmetry drawn in frequency space.

The vacuum carrier (f=0.5) acts as a mirror plane. Every particle mode (f_zitt)
has a reflection -- f_beat -- at equal distance from the mirror. The A is the
visual signature of that symmetry across all masses simultaneously.

At the 2:1 fixed point, f_zitt = f_beat: the particle and its vacuum reflection
are indistinguishable in frequency. This is the condition for maximum coupling to
the vacuum, and in the A=1 framework, maximum coupling to the vacuum is what
makes a particle maximally coherent.

The broad band at the base of the A (bottom-right, sweeping up-left): this is
f_beat at low omega. As omega->0, f_beat->0.5 (f_vacuum), and the beat frequency
overlaps with the always-bright vacuum carrier band. The band broadens because
at low mass, the particle's beat is nearly indistinguishable from the vacuum itself.

---

## Five Testable Predictions

**Prediction 1: The mirror is exactly at f=0.25**
The A symmetry requires f_vacuum = exactly 0.5 cycles/tick -- not approximately.
If you change the lattice geometry (different bipartite ratio, different connectivity),
the A should persist but recentered on f_vacuum/2 of the new geometry.
The carrier frequency is geometric, not dynamical.

**Prediction 2: The 2:1 is the only self-mirror frequency**
Exactly one omega satisfies f_zitt = f_beat. No other resonance (3:1, 4:1, etc.)
has bilateral symmetry. Confirmed analytically; visually verifiable by comparing
the neighborhood of the 3:1 and 4:1 stars -- they sit at diagonal crossings
(f_2nd meets f_beat), not at self-mirror points.

**Prediction 3: Coherence peaks at the 2:1 fixed point**
Sessions at omega=pi/2 should show the highest T2 (longest coherence time) of
any mass value. The qubit summary from the harmonic scan already shows T2=3 at
omega=pi/2 vs T2=2 for all others. A finer scan should show T2 peaking there.

**Prediction 4: The A is geometry-dependent, not coupling-dependent**
The hires scan uses free particles (no Coulomb well, no binding energy).
The A appears at STRENGTH=0. The STRENGTH sweep (exp_strength_sweep.py, running)
should confirm the A shape is unchanged while R1 shifts -- purely geometric.

**Prediction 5: Pair annihilation efficiency peaks at the 2:1 fixed point**
At omega=pi/2, f_zitt = f_beat: a particle and its chirality-partner (psi_R dominant
vs psi_L dominant) oscillate at identical frequencies. Maximum frequency overlap =>
maximum destructive interference => most efficient density collapse.

Experiment design (exp_17):
  - Initialize two CausalSessions at the same spatial location
  - Session A: omega=pi/2, psi_R dominant
  - Session B: omega=pi/2, psi_L dominant (exact chirality swap: psi_R <-> psi_L)
  - Let them evolve together under TickScheduler and measure composite density

The annihilation signature is NOT just density collapse.
It is a COHERENT OSCILLATION at f=0.25 cycles/tick BEFORE collapse.

At omega=pi/2, both spinor components of both sessions oscillate at 0.25 cyc/tick
(the shared mode). When they overlap, the composite density beats at that shared
frequency -- constructive then destructive interference -- before the A=1 unity
constraint forces normalization. The pre-collapse oscillation at f=0.25 is the
signature that distinguishes genuine annihilation from simple dispersion.

  Observable: FFT of total density in overlap region
  Signal: peak at f=0.25 with decaying amplitude
  Null result: broadband noise with no coherent peak

Comparison at omega=pi/3:
  - f_zitt = 1/6,  f_beat = 1/3  (different frequencies, no shared mode)
  - No coherent oscillation before spreading
  - Incoherent dispersion, not annihilation
  - FFT of overlap density: no clean peak at any single frequency

This distinction -- coherent oscillation then collapse vs incoherent spreading --
is the experimental fingerprint that the A=1 framework predicts for annihilation
vs scattering. It is directly measurable from the time series of composite density.

Spinor interpretation:
  psi_R <-> psi_L swap is the bipartite analog of charge conjugation (C symmetry).
  RGB sublattice <-> CMY sublattice swap reverses chirality.
  At omega=pi/2, a single session is already maximally self-entangled between
  psi_R and psi_L (equal time on both sublattices, T2 longest here).
  Two sessions with swapped chiralities at this omega are the closest the
  framework comes to a particle-antiparticle pair without explicit antisymmetrization.
  If exp_17 shows coherent collapse specifically at omega=pi/2, the annihilation
  channel is geometrically selected by the bipartite structure -- not imposed.

This closes the loop from the spinor antisymmetry question (exp_13 no-shell-separation)
all the way through to pair annihilation in one experimental chain.

---

## Connection to the STRENGTH sweep

The A structure and the omega*R1 = pi/3 result are independent:
- The A is a free-particle geometric property (STRENGTH=0)
- omega*R1 = pi/3 is a bound-state dynamical property (STRENGTH=30)

If the STRENGTH sweep confirms H0 (standard Bohr scaling, pi/3 only at STRENGTH=30),
the A structure remains unaffected -- it will still be exactly there, since it
doesn't depend on binding at all. The two results are complementary:
- The A: the vacuum has a mirror symmetry and a unique fixed point at omega=pi/2
- omega*R1=pi/3: physical atoms happen to be calibrated to the 3:1 resonance,
  which is the next-most-prominent feature after the 2:1 mirror fixed point

Together they suggest a hierarchy:
  2:1 (omega=pi/2) -- the mirror fixed point, geometric, mass-independent
  3:1 (omega=pi/3) -- the dominant bound state, calibrated to physical hydrogen
  4:1 (omega=pi/4) -- secondary crossing visible in the resonance corridor

This is exactly the hierarchy you would expect from a Farey sequence:
2:1, 3:1, 4:1... with the 2:1 being the fundamental organizing symmetry.
