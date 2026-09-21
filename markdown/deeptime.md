# deeptime

**Verified in original document:** 2026-09-21

## What it is

**deeptime** is a general-purpose **time-series and dynamical-modeling Python library**.

It is not MD-specific in the same way as MDAnalysis. Instead, it implements mathematical tools for learning dynamical systems from time-series data.

This is arguably the most important package in this list for the **“next-frame / future-state / time-lagged representation learning”** direction.

## Core job

Given one or more time series,

```text
x0, x1, x2, ..., xT
```

deeptime provides estimators for learning:

- slow collective coordinates;
- state decompositions;
- Markov models;
- Koopman models;
- deep time-lagged representations.

It follows an estimator/model design influenced by scikit-learn, but with model objects that expose kinetic and thermodynamic analyses.

## Major model families

### TICA

**Time-lagged Independent Component Analysis** finds directions with high time-lagged autocorrelation.

Unlike PCA:

```text
PCA  → high variance directions
TICA → slow / persistent directions
```

For MD, this is commonly used to identify slow collective variables before clustering.

### VAMP

The **Variational Approach for Markov Processes** generalizes time-lagged dimensionality reduction and provides objective scores for representations/features.

VAMP can be used to:

- learn slow dynamical coordinates;
- compare feature quality;
- estimate Koopman operators;
- work with nonequilibrium data more generally than reversible TICA assumptions.

### VAMPNet

`deeptime.decomposition.deep.VAMPNet` uses a neural network as the featurizing map and trains it with a VAMP-based objective.

Conceptually:

```text
X_t --------→ neural encoder ----→ z_t
X_(t+τ) ----→ neural encoder ----→ z_(t+τ)

optimize representation for time-lagged dynamical predictiveness
```

This is extremely close in *principle* to the proposed “next-token but frames” intuition, except that it is grounded in dynamical-systems / Koopman / variational theory rather than naive pixel-wise prediction of the literal next frame.

### Markov State Models

deeptime implements MSM estimators and model analyses.

A typical MD workflow is:

```text
features
  ↓
slow coordinates
  ↓
clustering / state assignment
  ↓
transition counts
  ↓
MSM
```

From an MSM, one can derive kinetic / thermodynamic information such as:

- stationary populations;
- implied timescales;
- transition pathways;
- free-energy-related quantities;
- relaxation behavior.

### Hidden Markov Models

HMM tools are provided for latent-state dynamical modeling.

### Koopman models

A Koopman-operator perspective models how observables evolve under the system's dynamics.

### SINDy and general dynamical-system tools

deeptime also includes broader dynamical modeling components beyond biomolecular simulation.

## Inputs and outputs

deeptime generally expects **already featurized time-series arrays**.

It does not care whether a feature vector came from:

- residue distances;
- torsions;
- contact maps;
- pairwise energies;
- neural embeddings;
- experimental signals;
- another domain entirely.

That is simultaneously a strength and a limitation.

## What deeptime does **not** fundamentally do

deeptime is **not**:

- an AMBER trajectory parser;
- a CPPTRAJ replacement;
- a residue-distance calculator;
- a hydrogen-bond analyzer;
- a force-field interaction-energy calculator;
- an MD topology-selection engine.

You typically need something else to produce the input time series.

## Relationship to SAWNERGY

This is where a clean division of labor becomes attractive:

```text
CPPTRAJ / MDAnalysis / SAWNERGY preprocessing
                ↓
physics-aware time series
                ↓
            deeptime
                ↓
TICA / VAMP / VAMPNet / MSM / kinetics
```

For a thesis, it would be wasteful to reimplement TICA, VAMP, MSM estimation, or VAMPNet just to claim ownership of the full stack.

A stronger contribution would be:

1. define the physics-aware residue-pair representation;
2. feed it into established dynamical objectives;
3. benchmark whether it improves representation of p53 mutant dynamics.

## Links

- Documentation: https://deeptime-ml.github.io/latest/
- Source code: https://github.com/deeptime-ml/deeptime
- PyPI: https://pypi.org/project/deeptime/
- VAMPNet API: https://deeptime-ml.github.io/latest/api/generated/deeptime.decomposition.deep.VAMPNet.html
- TICA API: https://deeptime-ml.github.io/latest/api/generated/deeptime.decomposition.TICA.html
- VAMP tutorial: https://deeptime-ml.github.io/trunk/notebooks/vamp.html
