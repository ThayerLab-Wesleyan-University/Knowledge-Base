# PyEMMA

**Verified in original document:** 2026-09-21

## Current status first

**PyEMMA is no longer actively maintained.**

Its GitHub repository explicitly recommends **deeptime** as the modern alternative covering most of its functionality.

PyEMMA nevertheless remains extremely important historically and scientifically because it established one of the most complete Python workflows for converting molecular trajectories into kinetic models.

## What it is

**PyEMMA** stands for **Emma's Markov Model Algorithms**.

It is a Python/C package for:

- MD featurization;
- dimension reduction;
- clustering;
- Markov State Models;
- Hidden Markov Models;
- thermodynamic / kinetic model analysis.

## Typical workflow

```text
MD trajectories
     ↓
featurization
     ↓
TICA / VAMP / PCA
     ↓
clustering
     ↓
discrete trajectories
     ↓
MSM / HMM
     ↓
kinetic / thermodynamic analysis
```

## Featurization

PyEMMA can read common MD trajectory formats and construct molecular features such as:

- Cartesian coordinates;
- atom / residue-pair distances;
- contacts via distance thresholds;
- backbone torsion angles;
- side-chain torsion angles;
- custom features.

Its featurizer supports sine/cosine encoding of torsions, which avoids the discontinuity at `−π / +π`.

## Dimension reduction

### TICA

TICA extracts slowly decorrelating coordinates.

This is one of the canonical MD approaches for identifying slow collective variables.

### VAMP

Modern PyEMMA versions also include VAMP transformations.

### PCA

Conventional variance-based dimensionality reduction is also available.

## Clustering

PyEMMA provides state-space discretization methods including:

- k-means;
- mini-batch k-means;
- regular-space clustering;
- uniform-time clustering.

## Markov State Models

PyEMMA estimates and analyzes discrete-state MSMs.

Capabilities include:

- maximum-likelihood MSMs;
- Bayesian MSMs;
- implied-timescale calculations;
- model validation;
- stationary populations;
- transition matrices.

## Hidden Markov Models

It supports hidden-state kinetic models, including Bayesian variants.

## Metastable-state analysis

PyEMMA includes **PCCA / PCCA+**-style metastable decomposition for grouping microstates into long-lived macrostates.

## Transition Path Theory

It includes reactive-flux / TPT analyses for studying transitions between sets of states.

Typical quantities include:

- committors;
- mean first-passage times;
- transition rates;
- reactive pathways / fluxes.

## Thermodynamic / multi-ensemble modeling

PyEMMA also includes a `thermo` package for thermodynamic estimators and historically supported multi-ensemble modeling workflows.

## What PyEMMA does **not** fundamentally do

PyEMMA is not:

- a force-field residue-pair energy decomposition engine;
- a CNN library for dense residue matrices;
- a modern deep-learning-first toolkit;
- a replacement for CPPTRAJ;
- an actively developed project in 2026.

## Relationship to SAWNERGY

PyEMMA is primarily useful now as:

1. scientific background;
2. a source of canonical workflows / baselines;
3. historical context for TICA/MSM approaches.

For new software, **deeptime is the better dependency / reference**.

A SAWNERGY thesis should almost certainly benchmark against the kind of workflow PyEMMA popularized:

```text
hand-designed molecular features
        ↓
TICA / VAMP
        ↓
clustering
        ↓
MSM / slow dynamics
```

before claiming an advantage for a neural predictive representation.

## Links

- Homepage / docs: https://www.emma-project.org/
- API documentation: https://www.emma-project.org/latest/api/index.html
- Source code: https://github.com/markovmodel/pyemma
- PyPI: https://pypi.org/project/pyEMMA/
- Featurizer API: https://emma-project.org/latest/api/generated/pyemma.coordinates.featurizer.html
- MSM API: https://emma-project.org/latest/api/index_msm.html
- TICA API: https://emma-project.org/latest/api/generated/pyemma.coordinates.tica.html
