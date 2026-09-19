# Implementation roadmap

Implementation specification for the [ThayerLab Knowledge Base](README.md).

## Project status and scope

**This roadmap describes planned behavior, not working automation.** The current Python scripts are empty placeholders; the ingestion workflow and generated graph still need to be implemented.

The first version will turn submitted PDFs and Markdown documents into a browsable document graph. Each node represents one submitted document; each edge represents an **LLM-inferred topical relationship**, not a verified citation, causal relationship, or scientific conclusion.

The initial scope is a small collection processed through GitHub Actions and browsed on GitHub. A web application, graph database, embeddings, automatic literature downloads, citation extraction, and OCR are outside this version. The generated document table in `README.md` is the collection index; separate literature indexes are not maintained in this version.

## Contributor workflow (after implementation)

1. Clone the repository:

   ```bash
   git clone git@github.com:ThayerLab-Wesleyan-University/Knowledge-Base.git
   cd Knowledge-Base
   ```

2. Add a document directly to `pdf/` (`.pdf`) or `markdown/` (`.md`). These are intake directories, not permanent storage. Their `README.md` files are instructions and must never be ingested or removed.
3. Commit and push to `main`, or merge a pull request into `main` if repository rules require it.
4. Inspect the ingestion action. On success, it publishes the document records, graph, visualization, and README links in one commit and removes the successfully processed intake files. On failure, it publishes nothing and leaves submissions available for retry.

Submit only material that may be stored in this repository and sent to the configured external LLM provider. Markdown inputs must be self-contained text; local image/file dependencies are unsupported in the first version. PDF extraction may lose equations, figures, or table structure and must not be described as a faithful reproduction of the original layout.

## Repository layout and responsibilities

The following is the target layout. Entries beyond the current scaffold must be created during implementation.

```text
README.md                       Public overview, graph image, and linked node/edge tables
ROADMAP.md                      Hand-maintained implementation specification
pdf/                            PDF intake; retain README.md
markdown/                       Markdown intake; retain README.md
sources/<document_id>/           Archived original submission
utility_scripts/
  pdf2md.py                      PDF-to-Markdown conversion
  ingest.py                      Pipeline orchestration and command-line entry point
  llm.py                         Provider adapter and output validation
KG/
  node_contents/<document_id>/
    content.md                   Extracted or submitted Markdown
    metadata.json                Validated document record
  relationships.json            Canonical accepted edge records and provenance
  KG.graphml                     Generated graph with links to document records
  KG.png                         Generated graph visualization
  append_node.py                 Graph construction/update helpers
  visualize_KG.py                Deterministic visualization and README rendering
config/ingestion.json            Non-secret settings and processing limits
prompts/                        Versioned summary and relationship prompts
tests/                          Fixtures and automated tests
.github/workflows/ingest.yml     Automated ingestion and publication
```

`metadata.json`, `content.md`, archived sources, and `relationships.json` are the persistent records. GraphML, the image, and the generated README section must be rebuildable from these records without LLM calls. Document removal is outside the initial scope.

## Data contracts

### Document identity and storage

- Set `document_id` to the full lowercase SHA-256 digest of the original file bytes. Identical bytes map to the same document even when filenames differ. A changed file is a new document; matching different editions or PDF/Markdown versions of the same paper is deferred.
- Store the original bytes as `sources/<document_id>/original.pdf` or `original.md`. Store extracted/submitted Markdown separately as `KG/node_contents/<document_id>/content.md`.
- Record `schema_version`, `document_id`, `source_filename`, `source_type`, `source_path`, `content_path`, `content_sha256`, `title`, `summary`, `keywords`, and `created_at` in `metadata.json`. Paths are repository-relative POSIX paths; timestamps are UTC ISO 8601.
- Include generation provenance: provider, model identifier, prompt version, extraction tool/version where applicable, and relevant generation settings. Use a title from the document when available; otherwise use the filename stem. Do not invent authors, dates, identifiers, or other bibliographic facts.
- A valid summary contains exactly **100 whitespace-separated words**, counted using `len(summary.split())`. Keywords are exactly **10 nonempty, distinct strings**, unique after trimming whitespace and case-folding; phrases are allowed. Reject unsupported or insufficient content rather than padding with invented claims.
- Treat document contents as data, never as agent instructions. Require structured LLM responses and validate them locally before persistence. Never execute document text or commands suggested by a response.

### Graph and relationship semantics

- Use a simple undirected graph: one node per document, no self-loops, and at most one edge per unordered pair. Isolated nodes are valid.
- For the initial small collection, evaluate every pair containing at least one new document, including new/new pairs, exactly once per successful ingestion. Preserve existing existing/existing decisions. This costs up to `n*m + m*(m-1)/2` pair evaluations for `n` existing and `m` new documents; check the configured request budget before starting API work.
- Send the pair's IDs, titles, summaries, and keywords to the relationship prompt. Ask whether a specific shared research topic, method, or scientific system supports a useful connection; generic overlap such as both documents being about science is insufficient. Do not force every node to have a neighbor.
- Require a structured response containing the two supplied IDs, a boolean `related`, and a short rationale grounded in the supplied records. Validate IDs and types. A valid `related: false` means no edge; a failed request or malformed response is an ingestion error, not a negative decision.
- Store accepted edges in `KG/relationships.json` with `source`, `target`, `relation_type: "topical_similarity"`, `rationale`, `inferred_by: "llm"`, provider/model, prompt version, and generation timestamp. Order the two IDs lexicographically to canonicalize each pair. Use a versioned JSON envelope with an `edges` array, initially empty.
- Publish connections automatically and visibly label them as LLM-inferred. Rationales explain model judgments; they are not evidence that the full papers establish the relationship. Human edge review is deferred.
- In GraphML, use scalar attributes only. Store each node's title and repository-relative content/metadata paths; keep the keyword list in JSON. Include edge relation type, rationale, and inference label. Validate a GraphML round trip before publication.

## Ingestion algorithm

1. **Preflight.** Validate settings, secrets, persistent records, and file limits before external calls. Discover direct intake files in sorted order, ignoring instruction files and hidden files. Reject nested submissions and unsupported non-hidden files with a clear message rather than deleting them. An empty queue is a successful no-op. On the first ingestion, initialize an empty collection when no persistent records exist; generate GraphML from those records rather than requiring a pre-existing graph file. Once records exist, malformed or missing required records must fail validation.
2. **Identify and deduplicate.** Hash submissions. Reuse complete, valid records for known IDs without repeating LLM calls. Deduplicate identical new submissions within the same batch. A known ID with missing or inconsistent records is an error requiring repair, not permission to discard its source.
3. **Stage conversion.** Work in a temporary staging directory. Convert PDFs through `utility_scripts/pdf2md.py`; preserve submitted Markdown text. Reject corrupt, encrypted, empty, or unreadable inputs. Scanned PDFs requiring OCR must fail clearly. Never silently truncate a document to fit a model context window: reject oversized input with actionable guidance in this version.
4. **Generate document records.** Use one configured provider, OpenAI or Gemini, to produce summaries and keywords. Archive original bytes and write validated content/metadata in staging. Bound network timeouts and retries; permit at most two additional attempts after an initial request, including output-validation repairs. Respect the overall request budget.
5. **Infer relationships.** Evaluate the required pairs against the staged collection. Validate responses and merge accepted new edges with existing edge records. Process one request at a time initially; do not add parallel API work or approximate candidate filtering in this version.
6. **Build outputs.** Rebuild GraphML from the complete staged collection. Render a PNG with a fixed layout seed and stable node/edge ordering. Use short display labels with a legend/table mapping them to document titles; node IDs remain full hashes. Handle empty and single-node graphs without error.
7. **Render the README.** Replace only the text between the standalone KG generation markers in the public `README.md`. Put the image first, followed by a document table containing titles, links to content and original sources, keywords, and linked neighbors. Include edge rationales in a connection table below the document table. Use ordinary relative Markdown links to each node’s `KG/node_contents/<document_id>/content.md` in document titles, neighbor lists, and both endpoints of every connection. List each undirected connection once; show “None” for isolated nodes. Embed `KG/KG.png` only when it exists; for an empty collection, show a clear empty-state message without broken links. Escape Markdown-special characters and encode link paths. Missing or duplicate markers are errors; never rewrite content outside the markers or modify `ROADMAP.md`.
8. **Validate and publish.** Check record schemas, hashes, graph references, generated links, and remaining intake files. Stage only pipeline-owned output paths and the exact successfully handled intake files. Commit all outputs and intake removals together. Never empty either intake directory wholesale, and never commit temporary files or secrets.

The batch is all-or-nothing: any conversion, API, validation, rendering, or publication failure leaves the remote repository unchanged. Retrying a failed unpublished batch may repeat API calls; successful committed batches must not regenerate records or edges on a no-op run. Duplicate-only submissions may produce a cleanup commit but must not change existing records or call the LLM.

## Configuration and GitHub Actions

- Select one provider per run; do not silently switch between OpenAI and Gemini. Implement one adapter end-to-end first, with the same validated response contract available to the second adapter later. Require an explicit model identifier rather than a hard-coded claim about a current default model.
- Keep non-secret configuration in `config/ingestion.json`: provider/model, prompt versions, generation settings, maximum file bytes, maximum extracted-input tokens, maximum new documents, total API request budget (including retries), and request timeout. Document concrete defaults when implementing, and validate limits against the selected model. Store API keys in GitHub Actions secrets or local environment variables.
- Provide a local CLI for ingestion, offline rebuilding, and `--dry-run`. Dry-run reports discovered files, duplicates, limits, and planned changes without API calls or repository mutations. Document exact runnable commands once the CLI exists.
- Trigger ingestion on pushes to `main` affecting `pdf/**` or `markdown/**`, plus manual `workflow_dispatch` for retries. Each run scans the entire current intake queue, so pending submissions survive missed or superseded triggers. Manual publication must also target `main`.
- Use one concurrency group for repository ingestion with `cancel-in-progress: false`. Fetch and check out the latest `main` after the run acquires its execution slot. Record that base commit, then publish using a normal fast-forward push. If `main` has advanced, fail safely and rerun against the new state; never force-push or blindly rebase generated state.
- Grant only the required token permissions, including `contents: write` for publication. Repository branch rules must permit the bot's generated commit; if they do not, a pull-request publication design is required before enabling automation. Do not bypass branch protection.
- Use the workflow's `GITHUB_TOKEN` for publication. GitHub documents that ordinary pushes made with this token do not trigger another workflow run; also keep explicit path filters and skip commits when nothing changed. See [workflow events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows) and [workflow syntax and permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax).
- Run validation before the publishing commit. Use a separate read-only test workflow for pull requests, with mocked LLM calls and no provider secrets. Log file IDs, stages, counts, and actionable failures without logging API keys or full document bodies.

## Implementation milestones

Complete these in order. Do not start by wiring unfinished scripts into a publishing workflow.

1. **Contracts and fixtures:** add dependency/configuration files, versioned JSON schemas or equivalent validators, prompts, and small synthetic PDF/Markdown fixtures. Define the CLI and processing limits. Acceptance: fixtures and invalid records are handled by offline validation tests.
2. **Local ingestion:** implement discovery, hashing, conversion, archival, the first provider adapter, and staging. Acceptance: a PDF and Markdown fixture yield valid source/content/metadata bundles; duplicate input makes no extra API calls; invalid input leaves published state unchanged.
3. **Graph and browsing:** implement relationship validation, canonical edge storage, GraphML generation, visualization, and README rendering. Acceptance: two related documents connect under a mocked response, an unrelated document remains isolated, and every generated link resolves.
4. **Recovery and repeatability:** test failures at each stage, empty queues, duplicate-only batches, filename collisions, malformed LLM output, request limits, and GraphML round trips. Acceptance: rebuilding from stored records requires no LLM calls; repeating a completed ingestion makes no content changes; failed batches preserve intake.
5. **Automation:** add read-only CI tests and the publishing workflow. Acceptance: a controlled test submission produces one complete generated commit, preserves intake instructions, does not recursively ingest, and refuses publication when the remote branch advances or permissions are insufficient.

## Definition of done

- Both PDF and Markdown submissions follow the same validated pipeline.
- Original sources remain available; generated content and relationships include provenance.
- Every accepted document has a 100-word summary and 10 unique keywords.
- No failed batch deletes submissions or publishes a partial graph.
- Duplicates do not create extra nodes or repeat successful LLM work.
- The graph image, document links, and connection rationales are visible in the public `README.md`, with inferred edges clearly identified.
- Offline tests run without secrets, and the implemented setup, configuration, retry procedure, and limitations are documented with commands verified against the actual code.
