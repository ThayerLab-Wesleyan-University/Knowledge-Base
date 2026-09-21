# MDAnalysis

**Verified in original document:** 2026-09-21

## What it is

**MDAnalysis** is a mature, general-purpose **Python library for reading, manipulating, selecting, transforming, and analyzing molecular simulation trajectories**.

It is not primarily an ML package. Its central abstraction is an MD system (`Universe`) containing topology information, atom groups, and one or more trajectory frames. Coordinates, velocities, and forces can be exposed as NumPy-compatible data, and analyses can be performed frame by frame.

MDAnalysis supports trajectories from many simulation ecosystems, including AMBER, GROMACS, NAMD, CHARMM, LAMMPS, and others.

As of the latest stable documentation checked here, MDAnalysis 2.10.0 is the stable release; development documentation for 2.11.0-dev0 also exists.

## Core job

Conceptually:

```text
topology + trajectory
        ↓
    MDAnalysis
        ↓
 atom selections / coordinates / transformations / analyses
        ↓
 NumPy arrays / result objects / derived trajectories
```

Its value is that it gives Python code direct, convenient access to trajectory data without writing one-off parsers for every MD format.

## Important capabilities

### Trajectory I/O

MDAnalysis can:

- open supported topology and coordinate/trajectory formats;
- iterate over frames;
- access coordinates;
- access velocities or forces when the file format contains them;
- select arbitrary atom groups;
- modify / transform frames on the fly;
- write trajectories and structures back out.

A typical model is:

```python
import MDAnalysis as mda

u = mda.Universe("topology", "trajectory")

protein = u.select_atoms("protein")

for ts in u.trajectory:
    xyz = protein.positions
```

### Selection system

It provides a rich atom-selection language, so an analysis can target:

- protein;
- backbone;
- C-alpha atoms;
- a residue range;
- particular atom names;
- ligand atoms;
- spatial selections;
- etc.

### Structural and geometric analysis

The `MDAnalysis.analysis` ecosystem includes modules for areas such as:

- atomic and pairwise distances;
- contacts;
- RMSD and RMSF;
- structural alignment;
- dihedral analysis;
- DSSP / secondary structure;
- density analysis;
- diffusion maps;
- PCA;
- hydrogen-bond analysis;
- water dynamics;
- ensemble comparison;
- covariance-related analysis;
- dielectric analysis;
- and additional specialized analyses.

The exact set evolves between releases, so the API documentation is the authoritative list.

### Parallel analysis

Modern MDAnalysis analysis classes support parallel backends for some analyses, including multiprocessing where supported.

### Extensibility

A major feature is that users can define their own frame-wise analysis classes and operate directly on atom groups and NumPy arrays.

That makes it an excellent *infrastructure layer* underneath custom scientific code.

## What MDAnalysis does **not** fundamentally do

MDAnalysis is **not**:

- a deep-learning framework for MD;
- a VAMPNet / time-lagged neural dynamics package;
- a force-field pairwise residue energy decomposition engine comparable to gRINN/i-gRINN or CPPTRAJ pairwise-energy workflows;
- an automatic residue-pair multichannel tensor generator specifically designed for CNNs;
- a complete MD→ML→adaptive-simulation system.

You can build all sorts of ML pipelines *on top of* MDAnalysis, but MDAnalysis itself is primarily about trajectory access and analysis.

## Relationship to SAWNERGY

MDAnalysis overlaps strongly with the proposed **geometric preprocessing** side of SAWNERGY.

It could plausibly provide:

```text
trajectory
   ↓
residue distances
contacts
H-bond geometry
torsions
secondary structure
SASA-related analyses / geometry
RMSD/RMSF
coordinates
...
```

What it does **not** give you as a central ready-made abstraction is:

```text
T × C × N × N
```

where the channels are deliberately chosen physics-aware residue-pair quantities such as:

- distance;
- electrostatic interaction energy;
- vdW interaction energy;
- H-bond relation;
- contact state;
- etc.,

combined with a temporal neural-learning interface.

So MDAnalysis can replace a lot of custom trajectory plumbing, but not the entire proposed scientific layer.

## Links

- Homepage: https://www.mdanalysis.org/
- Documentation: https://docs.mdanalysis.org/
- User guide: https://userguide.mdanalysis.org/
- Source code: https://github.com/MDAnalysis/mdanalysis
- PyPI: https://pypi.org/project/MDAnalysis/
- Analysis-module index: https://docs.mdanalysis.org/stable/documentation_pages/analysis_modules.html
