# ThayerLab Knowledge Base

A shared record of our publications, theses, methods, research notes, and relevant external literature. Use the knowledge graph to find documents and explore connections across the lab's work.

## Knowledge graph

Each node represents a submitted document. Connections are **LLM-inferred topical similarities**, not verified citations, causal relationships, or scientific conclusions. Short titles appear beneath each node; the IDs inside the circles match the full document titles and links in the table below.

<!-- KG:START -->

![ThayerLab document knowledge graph](KG/rendered/2f3a4f7fb312671064212d3acbafb794ecf4af91422379465c514259e74c57d4.png)

**4 documents · 4 LLM-inferred connections**

### Documents

| Node | Document | Original source | Keywords | Connected documents |
| --- | --- | --- | --- | --- |
| D1 | [Guidance in Diffusion Models for Target-Aware Molecular Generation](KG/node_contents/0189f29a1668f2dccc3adbd7eb3a23c6794df9c12fbe8a99a11e55a2ed4e02d9/content.md) ([summary](KG/node_contents/0189f29a1668f2dccc3adbd7eb3a23c6794df9c12fbe8a99a11e55a2ed4e02d9/metadata.json)) | [PDF](sources/0189f29a1668f2dccc3adbd7eb3a23c6794df9c12fbe8a99a11e55a2ed4e02d9/original.pdf) | diffusion models, molecular generation, target-aware generation, binding affinity, surrogate model, TargetDiff, PolyGen2D, graph neural networks, SE\(3\)-equivariance, molecular docking | [Structure-Based Drug Design: Test Research Note](KG/node_contents/1c0c3d6795f6aea9b2785bf8a8a6a9bcbfcdff45ed139372d29d82bb324b7300/content.md) |
| D2 | [SAWNERGY: A Python framework for dynamic residue-interaction networks and walk-based embeddings from molecular dynamics simulations](KG/node_contents/0c23bcd66b19b204436d471c34cf5e8e4e0f6b374d0202aed8be6998ff4f06be/content.md) ([summary](KG/node_contents/0c23bcd66b19b204436d471c34cf5e8e4e0f6b374d0202aed8be6998ff4f06be/metadata.json)) | [MD](sources/0c23bcd66b19b204436d471c34cf5e8e4e0f6b374d0202aed8be6998ff4f06be/original.md) | SAWNERGY, molecular dynamics, residue interaction networks, DeepWalk, skip-gram embeddings, electrostatic interactions, van der Waals interactions, random walks, self-avoiding walks, Zarr compression | [Structure-Based Drug Design: Test Research Note](KG/node_contents/1c0c3d6795f6aea9b2785bf8a8a6a9bcbfcdff45ed139372d29d82bb324b7300/content.md), [Spatiotemporal graph neural networks reveal conformational binding signature in protein dynamics](KG/node_contents/20ddb9cdf632136cc63dc7f0caa0b86e07c42cb6fb098a88c2c9cc5f33baeefc/content.md) |
| D3 | [Structure-Based Drug Design: Test Research Note](KG/node_contents/1c0c3d6795f6aea9b2785bf8a8a6a9bcbfcdff45ed139372d29d82bb324b7300/content.md) ([summary](KG/node_contents/1c0c3d6795f6aea9b2785bf8a8a6a9bcbfcdff45ed139372d29d82bb324b7300/metadata.json)) | [MD](sources/1c0c3d6795f6aea9b2785bf8a8a6a9bcbfcdff45ed139372d29d82bb324b7300/original.md) | structure-based drug design, molecular docking, protein-ligand interactions, binding pocket, computational study, molecular dynamics simulations, binding affinity estimation, ligand library, protein conformations, validation and reproducibility | [Guidance in Diffusion Models for Target-Aware Molecular Generation](KG/node_contents/0189f29a1668f2dccc3adbd7eb3a23c6794df9c12fbe8a99a11e55a2ed4e02d9/content.md), [SAWNERGY: A Python framework for dynamic residue-interaction networks and walk-based embeddings from molecular dynamics simulations](KG/node_contents/0c23bcd66b19b204436d471c34cf5e8e4e0f6b374d0202aed8be6998ff4f06be/content.md), [Spatiotemporal graph neural networks reveal conformational binding signature in protein dynamics](KG/node_contents/20ddb9cdf632136cc63dc7f0caa0b86e07c42cb6fb098a88c2c9cc5f33baeefc/content.md) |
| D4 | [Spatiotemporal graph neural networks reveal conformational binding signature in protein dynamics](KG/node_contents/20ddb9cdf632136cc63dc7f0caa0b86e07c42cb6fb098a88c2c9cc5f33baeefc/content.md) ([summary](KG/node_contents/20ddb9cdf632136cc63dc7f0caa0b86e07c42cb6fb098a88c2c9cc5f33baeefc/metadata.json)) | [PDF](sources/20ddb9cdf632136cc63dc7f0caa0b86e07c42cb6fb098a88c2c9cc5f33baeefc/original.pdf) | GISTnet-MD, graph neural networks, molecular dynamics, protein conformational dynamics, contrastive learning, explainable AI, integrated gradients, allostery, T4-Lysozyme, Adenosine A2A receptor | [SAWNERGY: A Python framework for dynamic residue-interaction networks and walk-based embeddings from molecular dynamics simulations](KG/node_contents/0c23bcd66b19b204436d471c34cf5e8e4e0f6b374d0202aed8be6998ff4f06be/content.md), [Structure-Based Drug Design: Test Research Note](KG/node_contents/1c0c3d6795f6aea9b2785bf8a8a6a9bcbfcdff45ed139372d29d82bb324b7300/content.md) |

### Connections

All connections below are LLM-inferred topical similarities.

| Document | Related document | Rationale |
| --- | --- | --- |
| [Guidance in Diffusion Models for Target-Aware Molecular Generation](KG/node_contents/0189f29a1668f2dccc3adbd7eb3a23c6794df9c12fbe8a99a11e55a2ed4e02d9/content.md) | [Structure-Based Drug Design: Test Research Note](KG/node_contents/1c0c3d6795f6aea9b2785bf8a8a6a9bcbfcdff45ed139372d29d82bb324b7300/content.md) | Both documents focus on molecular docking and binding affinity in the context of drug design, with the source using docking scores to guide molecular generation and the target employing docking and protein-ligand interactions to prioritize compounds in structure-based drug design. This shared use of docking and binding affinity estimation provides a specific scientific connection. |
| [SAWNERGY: A Python framework for dynamic residue-interaction networks and walk-based embeddings from molecular dynamics simulations](KG/node_contents/0c23bcd66b19b204436d471c34cf5e8e4e0f6b374d0202aed8be6998ff4f06be/content.md) | [Structure-Based Drug Design: Test Research Note](KG/node_contents/1c0c3d6795f6aea9b2785bf8a8a6a9bcbfcdff45ed139372d29d82bb324b7300/content.md) | Both documents involve molecular dynamics simulations and analysis of protein interactions; the source focuses on residue interaction networks and embeddings from MD trajectories, while the target applies MD simulations to study protein-ligand complexes in structure-based drug design, indicating a shared scientific system and method relevant to protein dynamics and interactions. |
| [SAWNERGY: A Python framework for dynamic residue-interaction networks and walk-based embeddings from molecular dynamics simulations](KG/node_contents/0c23bcd66b19b204436d471c34cf5e8e4e0f6b374d0202aed8be6998ff4f06be/content.md) | [Spatiotemporal graph neural networks reveal conformational binding signature in protein dynamics](KG/node_contents/20ddb9cdf632136cc63dc7f0caa0b86e07c42cb6fb098a88c2c9cc5f33baeefc/content.md) | Both documents focus on analyzing protein dynamics from molecular dynamics simulations using graph-based representations of residue interactions. The source uses residue interaction networks and random walk embeddings, while the target employs spatiotemporal graph neural networks to identify functional conformational signatures, indicating a shared research topic and methodological approach in protein dynamics analysis. |
| [Structure-Based Drug Design: Test Research Note](KG/node_contents/1c0c3d6795f6aea9b2785bf8a8a6a9bcbfcdff45ed139372d29d82bb324b7300/content.md) | [Spatiotemporal graph neural networks reveal conformational binding signature in protein dynamics](KG/node_contents/20ddb9cdf632136cc63dc7f0caa0b86e07c42cb6fb098a88c2c9cc5f33baeefc/content.md) | Both documents focus on protein-ligand interactions and utilize molecular dynamics simulations to study protein conformations and binding events. The source discusses structure-based drug design and computational analysis of protein-ligand complexes, while the target presents a deep learning framework analyzing protein conformational dynamics from molecular dynamics data, relevant for drug design. This shared focus on protein dynamics and binding signatures establishes a specific scientific connection. |
<!-- KG:END -->

## How lab members use this collection

**Browse:** find a title or keyword in the document table, then follow its document link to read the Markdown text. The **summary** link opens the 100-word summary, ten keywords, and generation details. Use **Original source** to check the original PDF or Markdown. Follow **Connected documents** or the connection table to explore related work and read why the model linked it. The image itself is an overview; the clickable links are below it.

**Contribute regularly:** add publications and theses when available, and write self-contained research notes for methods, project decisions, analyses, and results that would otherwise stay in personal notes. Include a clear title, author(s), date, project, research question, methods, findings or current status, limitations, and source links where relevant. Distinguish completed results from planned work. Submit relevant external papers only when sharing the full text is permitted; otherwise submit a substantive Markdown reading note with a link to the original.

This collection covers the material lab members submit; it does not automatically discover all lab work. The lab should backfill existing materials and add new work as it develops. Check source documents before relying on generated summaries or connections.

### Add a document through GitHub

1. Open the [PDF intake](pdf/) for a text-based `.pdf`, or the [Markdown intake](markdown/) for a UTF-8 `.md` document.
2. Use **Add file → Upload files** (or **Create new file** for a Markdown note). Place each document directly in the intake directory, without subfolders. Use a descriptive filename such as `2026-project-methods.md`; do not replace either intake `README.md`.
3. Commit your submission to a new branch and open a pull request. After the lab reviews it, merge into `main`. Members with permission may submit directly to `main` if lab policy allows.
4. Open [Actions → Ingest documents](https://github.com/ThayerLab-Wesleyan-University/Knowledge-Base/actions/workflows/ingest.yml). After a successful run, return here to find your document and its connections.

The workflow preserves the original file, stores the Markdown and metadata, and removes the intake copy only in the same commit that publishes the complete results. Identical files are deduplicated even if renamed. Revised file contents create a new node; editions and PDF/Markdown versions are not automatically merged.

Submit only material permitted to be stored in this repository and processed by OpenAI. Do not upload credentials, restricted lab data, or documents you cannot redistribute. Scanned/encrypted PDFs, local image/file dependencies in Markdown, and automatic OCR are unsupported. PDF extraction is text-only and can lose mathematical notation, figures, and table structure; always consult the original for these.

### Delete a document through GitHub

1. In the document table above, open the document's metadata link and copy its full `document_id` (64 characters). Do not use the image label such as `D1`; those labels can change.
2. Open [Actions → Delete document](https://github.com/ThayerLab-Wesleyan-University/Knowledge-Base/actions/workflows/delete-document.yml), select **Run workflow**, and choose **main**.
3. Paste the document ID and run the workflow. This requires repository permission to run Actions.

The action deletes that document's content, metadata, archived original, and all its connections, then updates the graph image and README in one commit. It runs only when manually requested and makes no LLM/API calls. Other documents and queued submissions are preserved. Deleted files remain in Git history; uploading the same document again recreates its node.

### Add a document from your computer

```bash
git clone git@github.com:ThayerLab-Wesleyan-University/Knowledge-Base.git
cd Knowledge-Base
git switch -c add-research-note
cp /path/to/research-note.md markdown/research-note.md
git add markdown/research-note.md
git commit -m "Add research note"
git push -u origin add-research-note
```

Open a pull request for that branch on GitHub. Lab members do not need Python or an API key to contribute through GitHub once a maintainer has enabled automation.

### If a submission fails

Read the failed action's error. Fix or replace the problematic intake file through a new commit; the remote intake files remain in place when a batch fails. A failed document blocks that whole batch. Maintainers can retry transient errors with **Actions → Ingest documents → Run workflow → main**. If `main` advanced during processing, rerun against the latest branch. Do not manually empty the intake directories.

For an incorrect summary or connection, open an issue with the document link and the proposed correction. Generated tables are overwritten on rebuild, so maintainers should correct the stored metadata or relationship record and rebuild the graph. Do not edit the archived source or extracted text in place; submit a corrected document as a new version.

## Maintainer setup

The implementation and offline tests are included. **Before the first automated ingestion**, a maintainer must:

1. Add an OpenAI API key with access to the configured model as the repository Actions secret **`OPENAI_API_KEY`**.
2. Review [config/ingestion.json](config/ingestion.json), including the model and request limits. The initial adapter uses the explicit snapshot `gpt-4.1-mini-2025-04-14`; Gemini is deferred.
3. Enable GitHub Actions and ensure repository rules permit the ingestion workflow to publish its generated commit to `main` with `contents: write`. If branch rules prohibit bot pushes, direct publication will fail safely; a PR-based publication workflow must be implemented before enabling ingestion under those rules.
4. Merge this implementation, submit one permitted document, and verify its source archive, summary, and graph links after the action succeeds.

Each new document is compared with all existing documents, so API usage grows with the collection. Defaults limit a batch to 10 new documents, 20 MiB per file, and 300 API requests including retries. The full operational setup, limits, local commands, and recovery procedure are in [MAINTAINING.md](MAINTAINING.md). The design and acceptance criteria are in [ROADMAP.md](ROADMAP.md).
