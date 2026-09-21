# molearn

**Verified in original document:** 2026-09-21

## What it is

**molearn** is a Python package for using machine learning to model and generate **protein conformational spaces**.

Its emphasis is not simply classifying MD frames. Instead, it learns a low-dimensional latent representation of an ensemble of protein conformations and can generate new protein conformations from latent-space coordinates.

The project describes itself as streamlining the construction of ML models for conformational data obtained from:

- molecular simulation;
- experiment.

## Core job

Conceptually:

```text
protein conformational ensemble
            ↓
       neural model
            ↓
       latent space z
            ↓
interpolate / sample / analyze z
            ↓
generate protein conformations
```

This is an important distinction from deeptime:

- `deeptime` asks strongly dynamical / kinetic questions;
- `molearn` is centered more on **conformational-space representation and generation**.

## Data handling

The package provides data tools such as:

- `PDBData`;
- `DataAssembler`.

It depends on MDAnalysis for some molecular-data handling.

## Neural models

The documented model stack includes autoencoder-based models.

The work associated with molearn specifically includes convolutional approaches to learning protein conformational spaces.

A typical objective is:

```text
conformation → latent representation → reconstructed conformation
```

Once learned, the latent space can be:

- explored;
- interpolated;
- sampled;
- decoded back into structures.

## Generating structures

The analysis API can generate collections of conformations from latent coordinates.

Generated structures can also be subjected to relaxation / quality assessment depending on the chosen workflow.

## Physics-aware capabilities

This package is especially relevant to the earlier discussion of **physics-informed ML**.

Current documentation includes physics-related components such as:

- `ModifiedForceField`;
- `OpenMMPluginScoreSoftForceField`;
- `OpenmmPluginScore`;
- `OpenmmTorchEnergyMinimizer`;
- OpenMM energy functions;
- `OpenMM_Physics_Trainer`.

This means molearn can incorporate molecular-energy information into model training / scoring rather than treating every geometrically reconstructed conformation as equally acceptable.

That is a direct example of the broader idea:

> use known molecular physics to constrain or regularize neural representation learning.

## Analysis

The toolkit includes methods for evaluating and exploring learned conformational spaces, including:

- generation from latent coordinates;
- structural quality assessment;
- energy-related evaluation;
- conformational-space analysis.

## What molearn does **not** fundamentally do

Its core purpose is not:

- residue-pair force-field energy decomposition across MD;
- building `T × C × N × N` relation tensors;
- Markov-state-model construction;
- VAMP-style slow-mode learning;
- WT/mutant classification;
- time-lagged future-state prediction as its central objective.

The primary emphasis is **generative conformational-space learning**.

## Relationship to SAWNERGY

molearn is important for two reasons.

### 1. It demonstrates that CNN/AE representations of protein conformational spaces are already established

Therefore, simply saying:

> “we use convolution to learn an MD latent space”

is not enough novelty.

### 2. It provides a concrete precedent for physics-aware neural training

If SAWNERGY incorporates known energy constraints or uses physics-based descriptors so that the network does not have to rediscover basic molecular mechanics, molearn is one of the closest conceptual references in this list.

## Links

- Documentation: https://molearn.readthedocs.io/en/latest/
- Source code: https://github.com/Degiacomi-Lab/molearn
- Project/software page: https://degiacomi.org/software/molearn/
- Analysis documentation: https://molearn.readthedocs.io/en/latest/analysis.html
- JOSS software paper: https://joss.theoj.org/papers/10.21105/joss.05523
