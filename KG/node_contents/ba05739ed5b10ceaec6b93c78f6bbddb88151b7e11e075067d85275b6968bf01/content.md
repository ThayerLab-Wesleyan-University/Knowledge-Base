# DeepDriveMD

**Verified in original document:** 2026-09-21

## What it is

**DeepDriveMD** is not best understood as a small Python library analogous to `numpy` or `MDAnalysis`.

It is an **adaptive molecular-simulation workflow / software ecosystem** that couples:

- molecular dynamics simulation;
- data preprocessing;
- deep-learning representation learning;
- inference / clustering / selection;
- new simulation launches.

Its central research idea is that ML can identify undersampled or interesting regions of conformational space and then drive new simulations toward those regions.

There are multiple repositories / generations of the project, including the DeepDriveMD organization, the file-based `DeepDriveMD-pipeline`, and a Ramanathan Lab implementation using Colmena.

## Core job

Conceptually:

```text
run MD simulations
       ↓
collect simulation data
       ↓
learn latent representation
       ↓
identify interesting / under-sampled states
       ↓
launch new MD from selected states
       ↓
repeat
```

So the important difference from a passive trajectory-analysis package is that DeepDriveMD closes the loop.

## ML component

DeepDriveMD workflows have used autoencoder-type latent models, notably:

- convolutional VAEs in relevant workflows;
- adversarial autoencoders in pipeline variants;
- clustering / inference on learned latent spaces.

The older/file-based pipeline documentation contains separate environments for components such as:

- OpenMM;
- PyTorch adversarial autoencoders;
- Keras CVAE;
- RAPIDS DBSCAN.

The more recent Ramanathan Lab repository exposes an OpenMM + CVAE workflow.

## MD component

Depending on version/workflow, DeepDriveMD has been coupled to engines such as:

- OpenMM;
- NAMD in prior large-scale work.

It is designed around high-performance / adaptive simulation rather than merely reading an existing trajectory once.

## Why contact maps matter here

DeepDriveMD-related work has used learned latent representations of molecular conformations, including contact-map-based representations through associated `mdlearn` workflows.

That makes it highly relevant to the proposed idea of treating residue-pair matrices as image-like neural inputs.

## What DeepDriveMD does **not** fundamentally mean

It is not:

- simply a trajectory parser;
- a generic residue-level force-field energy decomposition library;
- a single canonical `pip install` package with one narrow API;
- primarily a package for testing WT-vs-mutant classification;
- primarily a general kinetic-theory library like deeptime.

Its core contribution is **adaptive sampling driven by deep learning**.

## Relationship to SAWNERGY

DeepDriveMD strongly overlaps with:

> MD → representation learning → use learned representation for scientific decision-making.

But the specific goal is different.

SAWNERGY, as currently envisioned, would be more like:

```text
MD trajectory
    ↓
physics-aware residue-pair tensor
    ↓
spatial + temporal encoder
    ↓
dynamical representation
    ↓
test mutation / allostery hypotheses
```

whereas DeepDriveMD's central loop is:

```text
MD
↓
ML latent space
↓
select new starting points
↓
more MD
```

A future SAWNERGY could actually *use* DeepDriveMD-like adaptive sampling, but it would not make sense to reinvent the entire orchestration system for a one-year thesis.

## Links

- Project website: https://deepdrivemd.github.io/
- GitHub organization: https://github.com/DeepDriveMD
- File-based pipeline: https://github.com/DeepDriveMD/DeepDriveMD-pipeline
- Ramanathan Lab implementation: https://github.com/ramanathanlab/deepdrivemd
- Original DeepDriveMD paper/preprint: https://arxiv.org/abs/1909.07817
