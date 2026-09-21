# mdlearn

**Verified in original document:** 2026-09-21

## What it is

**mdlearn** is directly aimed at **machine learning for molecular dynamics**.

Unlike MDAnalysis, it is not mainly a general trajectory-analysis engine. Its purpose is to provide:

1. preprocessing utilities for common MD-derived ML inputs;
2. PyTorch implementations of representation-learning models;
3. training / inference utilities;
4. visualization and latent-space analysis support.

This makes it one of the closest existing projects to the generic phrase:

> “take MD data, turn it into ML-ready features, and learn a latent representation.”

## Core job

Conceptually:

```text
MD data
   ↓
preprocessing
   ↓
coordinates / contact maps / RMSD / feature arrays
   ↓
PyTorch model
   ↓
latent embedding
```

## Explicitly supported preprocessing

The project's current README lists a preprocessing CLI for:

- **coordinates**;
- **contact maps**;
- **RMSD**.

This is important for SAWNERGY because contact maps already produce an `N × N` residue-relation representation suitable for convolutional models.

## Explicitly supported models

The project documentation / README lists:

- **Quasi-Anharmonic Analysis (QAA)**;
- **Convolutional Variational Autoencoder (CVAE)**;
- **Autoencoder (AE)**;
- **Adversarial Autoencoder (AAE)**.

It uses PyTorch for the neural-network components.

### Autoencoders

An encoder maps the input feature space into a smaller latent space:

```text
x → encoder → z
```

and a decoder reconstructs it:

```text
z → decoder → x̂
```

The latent variable `z` can then be treated as a low-dimensional molecular representation.

### CVAE

The convolutional VAE is especially relevant to contact-map inputs because those can be treated as image-like matrices.

This is one of the clearest overlaps with the CNN version of the proposed SAWNERGY extension.

### Adversarial autoencoder

The AAE regularizes the latent distribution adversarially rather than purely with a VAE KL-divergence objective.

### Quasi-anharmonic analysis

QAA provides a higher-order statistical approach to identifying collective molecular fluctuations beyond a simple harmonic/covariance approximation.

## Visualization / downstream analysis

The package includes utilities for latent-space analysis and visualization, including t-SNE-related workflows. GPU acceleration through RAPIDS may be used for some visualization workloads, although the core package can operate without that acceleration.

## Inputs and outputs

Typical inputs:

- coordinate arrays;
- contact-map arrays;
- arbitrary suitable feature arrays.

Typical outputs:

- trained neural model;
- latent embedding `z`;
- reconstruction / training metrics;
- visualization outputs.

## What mdlearn does **not** fundamentally do

mdlearn does **not**, as its central built-in abstraction:

- compute AMBER/CHARMM/GROMACS force-field pairwise electrostatic and vdW interaction energies for every residue pair;
- build a standardized multichannel physical tensor such as  
  `distance + electrostatics + vdW + H-bond + contact`;
- solve the MD force calculation itself;
- provide a comprehensive general MD trajectory API comparable to MDAnalysis;
- provide the same breadth of kinetic estimators as deeptime;
- automatically distinguish biological signal from simulation leakage.

It is primarily an ML toolbox **after** or alongside MD preprocessing.

## Relationship to SAWNERGY

This is a **major overlap**.

If SAWNERGY's thesis were only:

> “Convert MD trajectories into residue contact maps and use a convolutional autoencoder to learn a latent representation,”

then mdlearn has already implemented the core software concept.

A stronger SAWNERGY distinction would have to come from something such as:

```text
time-resolved multichannel residue-pair physics
    +
predictive / time-lagged representation learning
    +
specific biological validation of mutation-induced nonlocal dynamics
```

rather than generic contact-map autoencoding.

## Links

- Documentation: https://mdlearn.readthedocs.io/en/stable/
- Source code: https://github.com/ramanathanlab/mdlearn
- PyPI: https://pypi.org/project/mdlearn/
- VAE API example: https://mdlearn.readthedocs.io/en/latest/pages/_autosummary/mdlearn.nn.models.vae.model.html
- Ramanathan Lab GitHub organization: https://github.com/ramanathanlab
