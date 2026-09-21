# RinPy

**Verified in original document:** 2026-09-21

## What it is

**RinPy** is a modern, pip-installable Python package for constructing and analyzing **Residue Interaction Networks (RINs)** from protein structures and structural ensembles.

It is specifically focused on graph/network representations of proteins.

RinPy should not be confused with gRINN:

- **gRINN/i-gRINN** are explicitly force-field **energy-network** tools;
- **RinPy** is a more general residue-interaction-network analysis framework based on structural interaction networks.

## Core representation

A protein is represented as a graph:

```text
node = residue / nucleotide / ligand
edge = residue-level interaction
edge weight = local interaction strength / affinity
```

Nodes can carry attributes such as:

- chain ID;
- residue number;
- insertion code;
- segment ID;
- Cartesian position.

## Supported inputs / scale

RinPy supports:

- single PDB structures;
- multiple PDB structures;
- large PDB ensembles;
- PDB structures derived from MD trajectories;
- protein–RNA / protein–DNA complexes;
- ligands in the network representation.

## Core analyses

### Centrality

Current built-in analyses include:

- degree centrality;
- closeness centrality;
- betweenness centrality.

Because the network is represented through NetworkX, the implementation can be extended to additional NetworkX centrality measures.

### Community / spectral analysis

RinPy includes graph spectral analysis and community-oriented analysis that can help identify:

- community organization;
- hinge regions;
- coupling between parts of the protein.

### Comparative state analysis

A major component is comparison between two structural/network states.

This can be used to analyze changes such as:

```text
apo vs ligand-bound
WT vs mutant
state A vs state B
```

The package supports analyses related to:

- perturbation propagation;
- community-structure changes;
- allosteric coupling;
- communication efficiency.

### Ligand-binding / allostery use

The associated publication emphasizes using RIN properties to investigate:

- putative allosteric sites;
- functional communication;
- ligand-binding-site behavior.

### Visualization / export

RinPy can export outputs compatible with PyMOL, including structural/network visualization support.

A separate GUI is also available.

### Multiprocessing

The package uses Python multiprocessing to accelerate large analyses.

## What RinPy does **not** fundamentally do

RinPy is not primarily:

- a deep-learning package;
- a CNN/RNN framework;
- a VAMP / MSM package;
- a force-field pair-energy decomposition engine equivalent to i-gRINN;
- a time-lagged predictive representation learner.

Its main abstraction is a **residue interaction network and graph-theoretical analysis**.

## Relationship to SAWNERGY

RinPy overlaps with the idea that:

> residue-level relations can reveal allosteric communication.

However, if SAWNERGY avoids a graph-centric model and instead treats the system as dense multichannel pairwise matrices over time, then the methodological direction differs significantly.

RinPy would still be an excellent **baseline**:

> Do the neural representations reveal anything beyond traditional residue-network centrality / network-comparison methods?

## Links

- Source code: https://github.com/zehrasarica/rinpy
- PyPI: https://pypi.org/project/rinpy/
- 2026 paper: https://pubs.acs.org/doi/10.1021/acs.jcim.6c00004
- DOI: https://doi.org/10.1021/acs.jcim.6c00004
