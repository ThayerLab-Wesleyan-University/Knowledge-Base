# i-gRINN

**Verified in original document:** 2026-09-21

These need to be separated because the original **gRINN** and the current **i-gRINN** are related but not the same software deployment.

## What it is

**i-gRINN** is the redesigned, current generation of the gRINN concept.

It is primarily a **web server / web application**, not simply a Python package.

It supports:

- GROMACS trajectory analysis;
- PDB structural ensembles;
- standard amino acids;
- small-molecule ligands;
- non-standard residues.

## Pairwise energy decomposition

For trajectory mode, users provide appropriate GROMACS structure/topology/trajectory files.

The system automates residue-pair energy calculations by driving GROMACS rerun machinery.

## Frame-by-frame analysis

The new system extends the analysis beyond only ensemble averages and includes frame-wise interaction-energy/network information.

## Network analysis

For each frame / representation, protein energy networks can be built and network metrics calculated, including:

- degree;
- betweenness centrality;
- closeness centrality.

## Output

The paper states that outputs are written in CSV format, which is particularly relevant for downstream custom ML.

## Interactive dashboard

The web system provides:

- interaction-energy matrix visualization;
- pairwise-energy views;
- network-analysis views;
- integrated 3D structural visualization.

## Natural-language querying

i-gRINN includes an LLM-powered interface that lets users ask questions about computed results in natural language, with biological interpretation grounded in sources such as UniProt and PubMed.

This is an *analysis/query interface*, not a neural representation-learning model for protein dynamics.

## Local deployment

The publication also describes a Docker-based local deployment path, removing some web-server upload/trajectory-size restrictions and allowing sensitive or larger datasets to remain local.

## What gRINN/i-gRINN do **not** do

Their central scientific goal is not:

- CNN representation learning;
- recurrent neural modeling;
- VAMPNet learning;
- self-supervised future-state prediction;
- mutation classification.

They produce physically meaningful residue-level energetic information and network analyses.

## Relationship to SAWNERGY

This is arguably the **closest overlap with SAWNERGY's pairwise-energy preprocessing**.

If SAWNERGY's contribution were only:

> “compute residue-by-residue electrostatic and vdW interaction energies from an MD trajectory,”

then that idea already exists very clearly in gRINN/i-gRINN.

The possible SAWNERGY distinction would instead be:

```text
force-field residue-pair energies
        +
other relation channels (distance, H-bond, contact, ...)
        +
full time-resolved tensor representation
        +
neural spatial/temporal learning
        +
careful biological validation
```

## Links

- Current web service: https://grinn.bio-cloud.site
- 2026 paper (Oxford Academic): https://academic.oup.com/nar/article/54/W1/W279/8695327
- Open-access PMC article: https://pmc.ncbi.nlm.nih.gov/articles/PMC13355066/
- DOI: https://doi.org/10.1093/nar/gkag516
