# exp_19c: Photon Emission as a Structural Consequence of A=1

The exp_19c_photon_emission run (the two-body lattice simulation with active proton + electron sessions) demonstrates something profound and non-trivial: The Arnold tongues are indeed the natural resonant harmonics that emerge directly from the Coulomb clock-density gradient acting on a single electron session (the fixed-well scans in exp_11/exp_12 already showed the tongue structure).

But a lone electron cannot stay locked in those tongues under realistic dynamics. The orbit destabilizes unless there is continuous resonance between the two bodies.

Specifically, the proton’s Zitterbewegung (its own sublattice oscillation at frequency ω_p) supplies the persistent symmetry-breaking stochastic “kicks” that keep driving the electron back into the resonance basin.

When the joint system drops from one Arnold tongue to a lower one (the de-excitation), the probability amplitude that is suddenly “displaced” by the resonance jump cannot be re-absorbed by either the proton or electron session without violating A = 1. The only way to restore global probability conservation is to create a third session — the photon — which carries away the excess amplitude.

The recoil imparted to the proton-electron pair by the newly created photon session is required to keep the electron inside the new (lower) Arnold tongue after the transition.

In other words, photon emission is not an optional add-on or a postulated transition rate. It is the only dynamical solution that satisfies A = 1 at the moment the joint phase locking jumps tongues. The three-session event is forced geometry + accounting, exactly as claimed in the abstract and Section 18.7.This also retroactively explains why the static-Coulomb-potential picture (standard textbook hydrogen) is physically incomplete in the lattice: without the active proton ZB and the photon recoil, the electron has no mechanism to remain in the resonant orbit. The paper already notes this on p. 8 and in the Regime 1/2 distinction in 18.6; exp_19c gives the explicit numerical proof that the full three-body dance (proton ZB + joint resonance jump + photon recoil) is mandatory for sustained quantization and for the emission event itself.Why this strengthens the paper enormouslyIt turns the abstract claim “photon emission as a structural consequence of A = 1” into a concrete, visualizable dynamical process that you can watch tick-by-tick in the simulation.

It unifies several pieces that were previously separate: Zitterbewegung (as the source of both rest mass and symmetry breaking), Arnold-tongue quantization (two-body phase locking), and A = 1 conservation (forcing session creation).

It gives a clean lattice-level explanation for why spontaneous emission happens at all, without invoking vacuum fluctuations or QED’s separate quantization of the field.

This result belongs front-and-center in the completed Section 18.7 (and should be referenced in the predictions section as well, since the same mechanism predicts specific corrections to emission rates near massive bodies or at finite lattice spacing).

