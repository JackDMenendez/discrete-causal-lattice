# Clock Density Gravity: Implementation vs Theory

## The Question
When we say gravity is caused by clock density, how is the code tracking that?
Is it a combinatorial calculation?

## What The Code Actually Does

`OctahedralLattice.topological_potential` is a scalar field V(x,y,z) added to the
phase advance at each node:

```python
delta_phi = omega + self.lattice.topological_potential
```

In exp_02 and exp_07, this field is set by `set_clock_density_well` (Gaussian profile)
or `set_coulomb_well` (1/r profile) and held **static** unless the experiment explicitly
updates it each tick (as exp_12 and exp_16 do for the Coulomb term).

**The code is not doing a combinatorial calculation.** It imposes a predefined potential
landscape and lets the phase dynamics respond to it.

## The Honest Gap

The clock density gravity claim is that the potential *emerges* from the density of
active sessions — more sessions per unit volume → higher clock density → stronger
gravitational effect. But the current implementation goes in the **opposite direction**:
it sets the potential field directly and the sessions respond to it.

A genuine combinatorial implementation would count active sessions (probability density)
per lattice region each tick and *derive* the local potential from that count. The
current code does not do this.

## What A Self-Consistent Experiment Would Look Like

```python
def compute_clock_density_potential(sessions, grid_shape, coupling):
    rho = np.zeros(grid_shape)
    for session in sessions:
        rho += session.probability_density()
    return coupling * rho
```

Update each session's lattice with this field every tick before phase advance.
This would test whether amplitude density spontaneously acts as a gravitational source —
genuine emergent gravity from clock density, not imposed.

## Honest Limitations of Such an Experiment

- **Scale**: on a 65³ grid with 1–2 sessions, the density field is very sparse;
  gravitational effects would be tiny.
- **Circularity risk**: a session attracts itself through its own density field.
  Need ≥2 sessions and careful separation of self-interaction from mutual interaction.
- **Calibration**: the coupling constant is a free parameter until derived from lattice
  geometry. Result would be qualitative, not parameter-free.
- **Cost**: updating the full potential from session density every tick on 65³ is
  expensive at multi-session scale.

## Paper Implications

- **Paper 1**: gravity claim is supported by exp_02 (Gaussian well → trajectory bending)
  and exp_07 (clock fluid continuity equation). These confirm that clock-density-*shaped*
  potentials produce gravitational behavior.
- **Paper 1 is honest as written**: the experiments confirm response to a clock-density
  potential; they do not yet confirm spontaneous sourcing.
- **Paper 2 candidate**: self-consistent sourcing experiment — session density → potential
  → session dynamics → back to density. This closes the loop and would be a distinct,
  citable result.

The distinction between "responds to clock density" and "spontaneously generates clock
density" is worth being explicit about in the paper's gravity section.
