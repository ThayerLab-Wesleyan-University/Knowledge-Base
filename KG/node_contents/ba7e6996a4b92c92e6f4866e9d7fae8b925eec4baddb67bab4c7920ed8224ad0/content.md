## Page 1

SAWNERGY                                                                                        RESEARCH PIPELINE

 SAWNERGY: Refined End-to-End
 Research Pipeline



 1. Expand SAWNERGY's MD Feature Extraction

 Extend SAWNERGY so that it can extract a richer set of raw, residue-level features from molecular
 dynamics trajectories.

 Potential features include:

    • Residue-residue distances
    • van der Waals interaction energies
    • Electrostatic interaction energies
    • Hydrogen bonds
    • Bonded interactions
    • Bond lengths
    • Bond angles
    • Dihedral/torsional angles
    • Contact maps
    • Residue center-of-mass positions
    • Protein-DNA interaction features
    • Protein-ligand interaction features
    • Other physically meaningful residue-wise quantities available through CPPTRAJ or related tools

 The objective is to transform every MD frame into a structured representation containing substantially
 more information than coordinates alone.


 2. Define the Frame Representation

 Represent each simulation frame as a collection of residue-residue interaction matrices.

 A natural representation is a multi-channel tensor:
                                                  Xt ∈  RN×N×C,

 where:

    • N  is the number of residues/nodes,
    • C is the number of interaction or geometric feature channels.

 Example channels could include:
                                   Xt  =  {Dt,  EvdW  , Eelec, Ht, Ct,  At, …}.
                                                  t       t

 Possible representation strategies:






Refined End-to-End Research Pipeline                                                                                1

## Page 2

SAWNERGY                                                                                               RESEARCH PIPELINE


 Option A — Multi-channel matrices
 Treat each physical quantity as a separate           channel.N×N

 This naturally supports CNN-style encoders.

 Option B — Dynamic graphs
 Treat residues as nodes and residue-residue quantities as edge features.

 Each frame becomes:
                                              Gt  =  (V,  Et, Xt,  Efeatures).
                                                                     t

 This naturally supports GNN encoders and may better reflect the underlying molecular structure.

 Option C — Hybrid representation
 Use graph structure for residue connectivity while separately retaining dense interaction matrices when
 useful.

 This is likely the most expressive approach but also the most complex.


 3. Pretrain a Frame-Level Autoencoder

 Before modeling entire trajectories, train an autoencoder that learns how to represent an individual MD
 frame.

 The model has the form:
                                                   X    Ef   h   Df  X^  ,
                                                      t       t         t

 where:

    • Xt is the raw frame representation,
    • ht is the learned frame embedding,
    • X^t is the reconstructed frame.

 Possible frame encoders:

 Option A — CNN Autoencoder
 Appropriate if frames are represented primarily as dense multi-channel residue-residue matrices.

 Option B — Graph Autoencoder
 Appropriate if frames are represented as residue interaction graphs.

 Option C — Graph/CNN hybrid
 Use graph operations for topology-sensitive information and convolutions for dense pairwise matrices.

 The purpose of this stage is to reduce each high-dimensional frame to:
                                                         ht ∈  Rdf ,

 where     preserves the physically meaningful state of the system at time  .ht        t







Refined End-to-End Research Pipeline                                                                                        2

## Page 3

SAWNERGY                                                                                           RESEARCH PIPELINE

 4. Build a Trajectory-Level Sequence Autoencoder

 Given a trajectory:

                                                   X1,X2,   …   ,XT  ,

 first encode each frame:

                                                    ht  = Ef(Xt).

 The resulting sequence

                                                    h1,h2,  …   ,hT

 is passed to a temporal encoder:
                                               (h  ,…  , h  )  Etrajz    ,
                                                 1        T          traj

 where
                                                      ztraj∈  Rdz

 is a single embedding representing the complete MD trajectory.

 Possible temporal encoders:

 Option A — LSTM
 A natural first implementation for recurrent sequence compression.

 Option B — GRU
 Similar to the LSTM but simpler and potentially easier to train.

 Option C — Transformer / temporal attention model
 Potentially more appropriate for very long trajectories because it avoids compressing all temporal
 information through recurrent state transitions.

 Option D — Hierarchical temporal encoder
 Encode short trajectory windows first and subsequently encode the resulting window-level embeddings
 into one trajectory-level vector.

 This may be preferable for extremely long MD trajectories.


 5. Reconstruct the Entire Trajectory From the Trajectory
 Embedding

 The trajectory decoder should reconstruct the sequence of frame embeddings:

                                                        ^   ^        ^
                                               ztraj →  h1,h2,  …   ,hT.

 The pretrained frame decoder then reconstructs the physical frames:
                                                      ^   Df   ^
                                                      ht      Xt.




Refined End-to-End Research Pipeline                                                                                    3

## Page 4

SAWNERGY                                                                                              RESEARCH PIPELINE


 Therefore:

                                       (X1,  …,   XT  ) →  ztraj →  (X^1, …,X^T    ).

 After frame-level pretraining, jointly fine-tune:

    • the frame encoder,
    • trajectory encoder,
    • trajectory decoder,
    • frame decoder.

 This allows frame representations to adapt to information that is important at the trajectory level.


 6. Use a DNA-Weighted Reconstruction Objective

 Do not restrict the representation exclusively to protein-DNA interactions.

 The model should observe the entire molecular system because the biological effect may propagate
 through an allosteric pathway such as:

                       ligand binding     →   local structural changes     →   protein dynamics
                            →   DNA-binding domain         →   protein-DNA interactions.

 Instead, reconstruct the entire system while assigning greater importance to errors involving DNA
 interactions.

 For example:

                                         Lrecon =  λglobalLglobal +  λDNALDNA,

 with

                                                     λDNA   >  λglobal.

 Possible experiments:

 Option A — Whole-system reconstruction
 Use uniform reconstruction loss everywhere.

 This provides a baseline.

 Option B — DNA-only representation
 Train using only protein-DNA interactions.

 This tests whether global protein dynamics actually contribute useful information.

 Option C — Whole-system representation with DNA-weighted loss
 Use the entire system but penalize protein-DNA reconstruction errors more heavily.

 This is the preferred initial formulation.










Refined End-to-End Research Pipeline                                                                                       4

## Page 5

SAWNERGY                                                                                             RESEARCH PIPELINE

 7. Ensure the Trajectory Latent Space Represents Biological
 Similarity

 Reconstruction alone does not guarantee that Euclidean or cosine distance in trajectory latent space
 corresponds to biological similarity.

 Initially, train the model purely with reconstruction and test whether meaningful dynamical states emerge
 naturally.

 If necessary, introduce an additional metric-learning objective:

                                         L  =  Lreconstruction+  λmetricLmetric.

 Possible approaches:

 Option A — Pure unsupervised reconstruction
 Allow latent geometry to emerge naturally.

 This should be tested first.

 Option B — Contrastive learning
 Encourage trajectories representing biologically similar systems to have similar embeddings.

 For example:

                                                     zWT1   ≈ zWT2.

 Option C — Triplet loss
 Construct triplets such as:

                                                (WT1,   WT2,    mutant)

 and explicitly enforce:

                                         d(zWT1,   zWT2)  <  d(zWT1,   zmutant).

 Option D — Supervised or semi-supervised metric learning
 Use available biological labels, mutation identities, functional measurements, or known rescue behavior
 when available.


 8. Train the Trajectory Encoder on a Large MD Corpus

 Train the trajectory representation model on as many suitable MD simulations as possible.

 The training corpus could include:

    • WT p53 trajectories
    • Y220C trajectories
    • Other p53 mutants
    • Ligand-bound systems
    • Apo systems
    • Different conformational states




Refined End-to-End Research Pipeline                                                                                     5

## Page 6

SAWNERGY                                                                                            RESEARCH PIPELINE


    • Potentially external p53 MD datasets
    • Potentially broader protein MD datasets during representation pretraining

 Possible training strategies:

 Option A — p53-only training
 Produces a highly specialized representation.

 Option B — Broad protein pretraining followed by p53 fine-tuning
 Could allow the model to learn general principles of protein dynamics before specializing.

 Option C — Self-supervised pretraining on large MD datasets
 Use reconstruction, masked-frame prediction, temporal prediction, or related self-supervised objectives
 before training the final trajectory autoencoder.


 9. Construct a Wild-Type Dynamical Reference

 Do not represent wild-type dynamics using one simulation alone.

 Run or collect multiple independent WT trajectories:
                                                 zWT,  zWT,  …   ,zWT  .
                                                  1     2           n

 These embeddings define a WT dynamical distribution or manifold.

 Possible WT reference representations:

 Option A — Mean WT embedding
                                                           1   n
                                                 μWT   =     ∑    ziWT.
                                                           n  i=1

 Then use:

                                               DWT   (z) =  ∥z  − μWT∥.

 Option B — Cosine similarity to the WT centroid
 Useful if vector direction is more meaningful than magnitude.

 Option C — Mahalanobis distance
 Estimate WT covariance:

                                                          ΣWT

 and compute:

                                    DWT   (z) =     (z −  μWT  )T Σ−1   (z −  μWT).
                                                                    WT

 This accounts for dimensions in which natural WT trajectories vary substantially.








Refined End-to-End Research Pipeline                                                                                    6

## Page 7

SAWNERGY                                                                                              RESEARCH PIPELINE


 Option D — Learned WT density
 Fit a model such as:

    • Gaussian mixture model,
    • normalizing flow,
    • kernel density estimator,
    • one-class model

 to the distribution of WT trajectory embeddings.

 This allows the model to represent a potentially multimodal WT dynamical landscape.


 10. Establish the Untreated Y220C Baseline

 Generate multiple untreated Y220C trajectories and embed them:
                                                   zY220C,  …  , zY220C.
                                                    1             m

 Measure their distance from the WT distribution.

 This establishes the baseline dynamical deviation caused by Y220C.

 The model should demonstrate that, statistically:
                                             DWT(zY220C)      >  DWT(zWT      )

 before the representation is used as a rescue metric.

 This is a critical validation step.


 11. Curate an Initial Y220C-Binding Molecule Set

 Construct an initial compound dataset containing molecules known or predicted to bind to the Y220C
 pocket.

 Possible sources include:

    • experimentally validated Y220C binders,
    • known p53 stabilizers,
    • literature compounds,
    • docking-screen hits,
    • chemically diverse analogues,
    • intentionally weak or inactive compounds as negative controls.

 For every compound    , construct and simulate:mi

                                                      Y220C    +  mi.

 Where computationally feasible, perform multiple independent MD replicates per compound.










Refined End-to-End Research Pipeline                                                                                       7

## Page 8

SAWNERGY                                                                                            RESEARCH PIPELINE

 12. Compute an MD-Based Dynamical Rescue Score

 For every compound:
                                         mi  →   MD   →   X(i)  →  Etraj →   zi.


 Measure how close the compound-treated Y220C trajectory is to the WT dynamical distribution.

 A simple score could be:

                                                   Si =  −DWT    (zi).

 A more interpretable normalized rescue score is:

                                              R   =  1 −     DWT   (zi)   .
                                                 i        DWT   (zY220C)

 Interpretation:

    • Ri ≈  0: little or no rescue
    • Ri >  0: dynamics moved toward WT
    • Ri →   1: strong restoration toward WT
    • Ri <  0: compound moved dynamics farther away from WT

 If multiple Y220C reference simulations exist, use their mean or expected WT distance rather than a
 single baseline trajectory.


 13. Validate That the Rescue Score Is Biologically Meaningful

 Before using the score for molecular optimization, test whether it corresponds to known biology.

 Possible validation criteria include:

    • Known rescuing compounds should score better than inactive molecules.
    • Strong binders should not necessarily score highly unless they actually restore WT-like dynamics.
    • WT trajectories should score as WT-like.
    • Untreated Y220C should consistently score poorly.
    • Known functional measurements should correlate with the learned score when available.
    • DNA-binding behavior should improve as the score improves.
    • Relevant structural and interaction features should move toward WT values.

 This is arguably the most important scientific validation in the entire pipeline.


 14. Train a Molecular Surrogate Scoring Model

 The MD simulations produce a dataset:
                                                 D  =  {(mi,  Ri)}N    .
                                                                    i=1

 Train a neural network:

                                                     fθ(mi)   ≈  Ri.




Refined End-to-End Research Pipeline                                                                                     8

## Page 9

SAWNERGY                                                                                              RESEARCH PIPELINE


 The purpose of this model is to approximate the expensive MD-based rescue score without actually
 running an MD simulation.

 Possible molecular representations:

 Option A — Molecular graph + GNN
 Represent:

    • atoms as nodes,
    • bonds as edges,

 and use a molecular GNN.

 This is the preferred initial approach.

 Option B — SMILES transformer
 Represent molecules directly from their SMILES strings using a pretrained chemical language model.

 Option C — Molecular fingerprints
 Use fingerprints such as Morgan fingerprints as input to an MLP or another regression model.

 This provides a simpler baseline.

 Option D — 3D molecular representation
 Use a geometric GNN operating on 3D conformations.

 Potentially more physically informative but substantially more complicated.


 15. Predict Both Rescue Score and Model Uncertainty

 The surrogate should ideally estimate:
                                                          R^(m)

 and uncertainty:

                                                          U(m).

 Possible uncertainty approaches include:

    • Deep ensembles
    • Monte Carlo dropout
    • Bayesian neural networks
    • Evidential regression
    • Ensemble variance

 Uncertainty is important because the surrogate will eventually evaluate molecules outside its original
 training distribution.













Refined End-to-End Research Pipeline                                                                                      9

## Page 10

SAWNERGY                                                                                            RESEARCH PIPELINE

 16. Train or Fine-Tune a Molecular Diffusion Model

 Use a molecular generative model capable of proposing new candidate compounds.

 Possible approaches:

 Option A — Train a diffusion model from scratch
 Likely requires a very large molecular dataset and substantial compute.

 Option B — Start from a pretrained molecular diffusion model
 Fine-tune or condition it for molecules compatible with the Y220C pocket.

 This is likely much more practical.

 Option C — Use another molecular generative model
 The overall SAWNERGY pipeline does not fundamentally depend on diffusion.

 Other possible generators include:

    • autoregressive graph generators,
    • SMILES language models,
    • VAEs,
    • flow models.

 Diffusion is one attractive option rather than a strict requirement.


 17. Guide Molecular Generation Using the Surrogate Rescue
 Model

 Use:

                                                         fθ(m)

 as guidance toward molecules predicted to produce strong WT-like rescue.

 The generative model should not optimize only the predicted rescue score.

 Other constraints should also be considered, such as:

    • Y220C pocket compatibility
    • Chemical validity
    • Synthetic accessibility
    • Molecular stability
    • Drug-likeness
    • Molecular diversity
    • Toxicity or undesirable chemical motifs
    • Binding affinity estimates
    • ADMET-related properties where appropriate

 The optimization target therefore becomes multi-objective rather than simply:

                                                      max   R^(m).
                                                        m



Refined End-to-End Research Pipeline                                                                                    10

## Page 11

SAWNERGY                                                                                           RESEARCH PIPELINE


 18. Select Molecules Using an Active-Learning Acquisition
 Strategy

 Do not simply select the molecules with the highest predicted scores.

 Doing so risks allowing the generator to exploit errors in the surrogate model.

 Instead define an acquisition function combining:
                                      A(m)    =  αR^(m)   + βU(m)    +  γD(m),

 where:
    • R^(m) = predicted rescue
    • U(m) = uncertainty
    • D(m) = chemical diversity or novelty

 Possible selection strategies:

 Option A — Exploitation
 Choose molecules with the highest predicted rescue score.

 Option B — Uncertainty sampling
 Choose molecules for which the scoring model is least certain.

 Option C — Diversity sampling
 Choose chemically diverse molecules to broaden the training distribution.

 Option D — Combined acquisition
 Select a mixture of:

    • high-scoring compounds,
    • uncertain compounds,
    • chemically diverse compounds.

 This is the preferred strategy.


 19. Run MD Simulations on Selected Generated Molecules

 For every selected generated molecule:

                                   mj  →   Y220C + molecule MD         →  zj →   Rj.

 The trajectory encoder therefore acts as the expensive physics-based oracle for the molecular
 optimization system.

 Whenever computationally feasible, use replicate MD simulations so that the rescue score incorporates
 simulation variability rather than relying on one stochastic trajectory.









Refined End-to-End Research Pipeline                                                                                  11

## Page 12

SAWNERGY                                                                                              RESEARCH PIPELINE

 20. Expand the Molecular Rescue Dataset

 Add the newly evaluated compounds:

                                               Dk+1  =  Dk  ∪  {(mj,  Rj)}.

 The dataset therefore becomes progressively larger and more informative.

 Importantly, the dataset should contain not only successful molecules but also:

    • failures,
    • neutral compounds,
    • surprising compounds,
    • uncertain compounds,
    • chemically diverse molecules.

 Negative information is essential for improving the surrogate.


 21. Retrain or Fine-Tune the Molecular Surrogate

 Using the expanded dataset:

                                                          Dk+1,

 update:

                                                       fθk →   fθk+1.

 The scoring model should become progressively more accurate around chemically promising regions
 explored by the generative model.

 Monitor:

    • predictive error,
    • calibration,
    • uncertainty quality,
    • out-of-distribution performance,
    • ranking performance,
    • correlation with true MD rescue scores.


 22. Update the Generative Model

 Use the improved surrogate model to provide better guidance for the molecular generator.

 Depending on the generative architecture, this may involve:

    • conditional generation,
    • classifier guidance,
    • reinforcement-learning-style optimization,
    • score guidance,
    • fine-tuning on high-performing molecules,




Refined End-to-End Research Pipeline                                                                                      12

## Page 13

SAWNERGY                                                                                        RESEARCH PIPELINE


    • rejection sampling,
    • ranking generated molecules with the surrogate.


 23. Repeat the Closed Active-Learning Loop

 Repeat:

                                     Generate   →  Predict   →  Select  →  MD
                             →   Encode   →  Score  →   Expand dataset     →  Retrain


 until:

    • computational resources are exhausted,
    • improvements plateau,
    • sufficiently strong candidate molecules emerge,
    • or candidates are ready for experimental validation.


 Overall Architecture


 The complete project contains three principal machine-learning systems.

 Model 1 — Molecular Dynamics Representation Model

                                   MD trajectory     →  ztrajectory→  RWT rescue

 Purpose:


     Determine how closely the dynamics of a mutant or ligand-bound system resemble the wild-type
     dynamical state.


 This model includes:

    • frame encoder,
    • temporal encoder,
    • trajectory decoder,
    • frame decoder,
    • WT reference distribution,
    • rescue scoring mechanism.

















Refined End-to-End Research Pipeline                                                                              13

## Page 14

SAWNERGY                                                                                         RESEARCH PIPELINE

 Model 2 — Molecular Rescue Surrogate

                                              molecule   →  R^WT rescue

 Purpose:


     Predict the MD-derived rescue score without running an expensive molecular dynamics
     simulation.


 This model serves as a cheap approximation to the MD oracle.


 Model 3 — Molecular Generator

                               generative model    →   candidate rescue molecules

 Purpose:


     Generate new compounds predicted to move Y220C dynamics toward the WT dynamical state.


 The surrogate model provides guidance, while MD simulations provide the final high-fidelity evaluation.


 Core Scientific Hypothesis

 The central hypothesis of SAWNERGY becomes:


     A learned trajectory-level representation of molecular dynamics can quantify restoration of
     mutant p53 dynamics toward the wild-type dynamical state, and this learned rescue signal
     can subsequently guide the iterative discovery of novel Y220C rescue compounds.


 The most important intermediate question is therefore:


     Does distance from the learned WT trajectory distribution provide a reproducible and
     biologically meaningful measurement of Y220C rescue?


 The generative molecular-design loop should only be trusted after this question has been convincingly
 answered.

















Refined End-to-End Research Pipeline                                                                               14

## Page 15

SAWNERGY                                                                                    RESEARCH PIPELINE

 Final Closed-Loop System

                                 Molecule   →  Y220C MD simulation
                                            →  trajectory representation
                                            →  WT rescue score
                                            →  molecular surrogate training
                                            →  surrogate-guided generation
                                            →  new molecules
                                            →  MD simulation
                                            →  new rescue measurements
                                            →  dataset expansion
                                            →  model improvement
                                            →  ⋯


 The resulting system is an iterative combination of:

 representation learning + molecular dynamics + surrogate modeling + active learning +
 generative molecular design.































































Refined End-to-End Research Pipeline                                                                          15
