# MD / ML Software Landscape Relevant to SAWNERGY

**Verified:** 2026-09-21

This document describes the software packages and projects discussed in connection with a possible SAWNERGY extension for machine learning on molecular-dynamics (MD) trajectories. It intentionally distinguishes between:

- trajectory-analysis libraries;
- machine-learning libraries;
- dynamical/kinetic modeling libraries;
- residue-interaction-network software;
- generative conformational-modeling software; and
- complete adaptive-simulation workflows.

That distinction matters because several of these tools overlap strongly, but they solve different layers of the overall problem.

---

## Executive comparison

| Project | What it fundamentally is | Reads MD trajectories directly? | Computes structural / residue features? | Computes force-field residue-pair energies? | Includes neural ML? | Explicitly models temporal kinetics? | Most relevant overlap with SAWNERGY |
|---|---|---:|---:|---:|---:|---:|---|
| **MDAnalysis** | General Python MD trajectory-analysis framework | Yes | Yes, extensively | Not as its core force-field energy-decomposition purpose | No built-in deep-learning framework | Limited; analyses exist, but kinetic modeling is not its main purpose | Trajectory I/O, distances, contacts, H-bonds, torsions, DSSP, RMSD/RMSF, transformations |
| **mdlearn** | ML library specifically for MD | Via preprocessing workflow | Coordinates, contact maps, RMSD | No | Yes: AE, CVAE, AAE | Not its main focus | MD → tensors/features → PyTorch latent representations |
| **DeepDriveMD** | Adaptive MD + ML workflow / orchestration system | Through simulation/preprocessing stages | Yes, depending on workflow | Not its defining feature | Yes | Uses learned latent spaces to guide sampling rather than primarily estimating kinetics | End-to-end MD → ML → adaptive simulation loop |
| **deeptime** | General time-series / dynamical-modeling library | Usually expects already-featurized arrays | No MD-specific feature engine | No | Yes: VAMPNets / deep MSM tools | **Yes, strongly** | TICA/VAMP/VAMPNet/MSM/HMM/Koopman models for learned slow dynamics |
| **gRINN / i-gRINN** | Residue interaction energy + protein energy network software | Yes, via GROMACS/NAMD or uploaded GROMACS data | Pairwise energetic relations and network metrics | **Yes** | No scientific deep-learning model; i-gRINN has an LLM interface for querying results | Frame-wise / correlation/network analysis, not learned kinetic models | Force-field-based residue–residue electrostatic/vdW energies and protein energy networks |
| **RinPy** | Residue interaction network analysis package | Supports ensembles / MD-derived structures | **Yes: residue interaction networks** | Not primarily force-field pair-energy decomposition like gRINN | No | Comparative/network analysis rather than learned temporal kinetics | Residue networks, centralities, communities, allosteric communication, state comparison |
| **molearn** | Generative ML for protein conformational spaces | Loads conformational ensembles | Works from protein conformations | Physics can be introduced through OpenMM-based scoring/losses | **Yes** | Primarily conformational-space/generative modeling rather than kinetic estimation | CNN/AE-style latent conformational representations and physics-aware training |
| **enspara** | Scalable ensemble analysis + Markov-state-model toolkit | Yes, commonly via MDTraj-backed workflows | Can cluster coordinates or arbitrary feature arrays | No | Mostly classical/statistical methods, not primarily neural | **Yes** | Clustering, MSMs, TPT, information theory, allosteric analyses |
| **PyEMMA** | Legacy comprehensive MD kinetics toolkit | Yes | Yes: distances, torsions, coordinates, etc. | No | Mostly classical; not a modern deep-learning framework | **Yes, strongly** | TICA/VAMP, clustering, MSMs/HMMs, metastable states, TPT; largely superseded by deeptime |

---

# How these projects fit together

A useful way to understand the ecosystem is that **no single one owns the entire MD→physics→ML→kinetics pipeline**.

A modern pipeline could deliberately combine them:

```text
                         ┌──────────────────────┐
                         │     MD trajectory    │
                         └──────────┬───────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
               MDAnalysis                     CPPTRAJ /
              geometry etc.                   i-gRINN-like
                     │                         energetics
                     │                             │
                     └──────────────┬──────────────┘
                                    │
                         physics-aware features
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
             mdlearn             deeptime            enspara
        AE / CVAE / AAE      VAMP / VAMPNet      MSM / TPT /
          latent space         TICA / MSM        info theory
```

This is why a new package has to define its novelty carefully.

---

# What is already solved versus what remains potentially distinctive

## Already well solved

### General trajectory access

Use:

- **MDAnalysis**
- MDTraj (not covered in detail here because it was not part of the original comparison)

There is little reason to build another generic trajectory reader.

### Contact maps / coordinates → neural latent space

Use:

- **mdlearn**
- **molearn**
- DeepDriveMD-associated workflows

There is already substantial precedent for convolutional / autoencoder learning from molecular conformations.

### Slow-dynamics / kinetic modeling

Use:

- **deeptime**
- **enspara**
- historically **PyEMMA**

There is little reason to reimplement TICA, VAMP, MSM estimation, or basic kinetic analysis.

### Pairwise force-field residue interaction energies

Use / compare with:

- **gRINN / i-gRINN**
- CPPTRAJ workflows

So residue-wise energetic decomposition is not itself novel.

### Residue-network / allostery analysis

Use / compare with:

- **RinPy**
- gRINN/i-gRINN protein energy networks
- enspara allostery/information-theory analyses

Again, residue interaction networks are a well-established analysis paradigm.

---

# The potentially distinctive SAWNERGY niche

After accounting for the existing ecosystem, the strongest remaining niche is much narrower:

> **Learn time-dependent representations of a protein from multichannel, physically meaningful residue–residue relations, then test whether those representations capture nonlocal mutation-induced dynamical behavior better than standard geometric or kinetic baselines.**

A candidate representation is:

```text
X ∈ R^(T × C × N × N)
```

where `N` is the number of residues and `C` might contain channels such as:

```text
distance
electrostatic interaction energy
van der Waals interaction energy
hydrogen-bond relation
contact state
...
```

plus possibly:

```text
R ∈ R^(T × N × F)
```

for per-residue features such as torsions, secondary structure, solvent accessibility, etc.

The project becomes scientifically interesting only if it rigorously asks whether this representation adds information beyond what existing methods already capture.

---

# Baselines a SAWNERGY thesis should probably include

If SAWNERGY is evaluated as a research thesis, comparisons should include several levels.

## Structural / static baselines

- one frame only;
- starting structure only;
- average contact map;
- average residue-distance matrix;
- average interaction-energy matrix.

## Classical dynamical baselines

Using deeptime / enspara:

- PCA;
- TICA;
- VAMP;
- clustering + MSM;
- implied timescales.

## Existing neural baselines

Using mdlearn / adapted equivalents:

- contact-map convolutional autoencoder;
- contact-map CVAE;
- ordinary autoencoder without time-lagged objective.

## Proposed physics-aware representation

For example:

```text
distance + electrostatics + vdW + H-bond + contact
```

## Proposed temporal objective

For example:

- VAMPNet;
- time-lagged latent prediction;
- another carefully justified future-predictive objective.

---

# The critical novelty test

The strongest question is not:

> Can a neural model classify WT and mutant trajectories?

That can succeed for trivial reasons.

A much stronger question is:

> After controlling for direct mutation-site identity, does a time-lagged model trained on physically enriched residue-relation tensors learn a latent representation that captures nonlocal mutation-induced changes in protein dynamics?

Useful controls include:

- split by independent MD trajectory, never random frames;
- mask the mutated residue;
- mask residues spatially close to the mutation;
- hold out entire mutations;
- compare ordered trajectories with time-shuffled trajectories;
- compare temporal models with time-averaged features;
- compare physical multichannel inputs with contact-map-only inputs;
- compare against TICA/VAMP/MSM baselines.

That is the level at which the project becomes distinct from merely combining existing software.

---

# Short classification of each tool

## Use directly as infrastructure

- **MDAnalysis** — trajectory / geometry / structure handling.
- **deeptime** — time-lagged representation and kinetic methods.
- **enspara** — scalable MSM / ensemble baselines.

## Use as ML baselines / conceptual references

- **mdlearn** — contact-map / coordinate neural representations.
- **molearn** — conformational latent spaces and physics-aware neural training.
- **DeepDriveMD** — learned latent spaces embedded in adaptive MD workflows.

## Use as residue-interaction / allostery baselines

- **gRINN / i-gRINN** — residue-pair force-field energies and protein energy networks.
- **RinPy** — residue interaction network / graph-based allostery analysis.

## Historical reference

- **PyEMMA** — canonical MD kinetics workflow; use deeptime for new development.
