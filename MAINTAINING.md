# Maintaining the knowledge base

## Local setup

Use Python 3.12 on macOS or Linux. Run these commands from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m utility_scripts.ingest ingest --dry-run
python -m utility_scripts.ingest validate
```

The virtual environment isolates installed packages from system Python. `requirements.txt` locks runtime dependencies; `requirements-dev.txt` adds the offline test tools. No API key is required for tests, dry-run, validation, or rebuild. Tests use synthetic research text and generate their own PDF fixtures and temporary local Git remotes; they do not send documents anywhere.

## Commands

| Command | Effect |
| --- | --- |
| `python -m utility_scripts.ingest ingest --dry-run` | Validate/discover the full queue, extract input text, report duplicates and request bounds; no API calls or repository writes. |
| `python -m utility_scripts.ingest ingest` | Process intake and apply a fully validated batch to the local checkout; no Git commit or push. |
| `python -m utility_scripts.ingest rebuild` | Regenerate GraphML, PNG, and the README block from stored records, without API calls; also initializes an empty collection. |
| `python -m utility_scripts.ingest validate` | Check record schemas, source/content hashes, edges, GraphML, PNG presence, and generated README links. |
| `python -m utility_scripts.ingest ingest --publish` | Ingest from a clean, current `main` checkout and publish one complete commit to `origin/main`; intended for disposable CI checkouts. |

All commands accept `--root /path/to/Knowledge-Base`. Rebuild also accepts `--dry-run`. Normal local ingestion deliberately leaves changes uncommitted so they can be reviewed. Do not run `--publish` after a local ingestion: publication requires a clean checkout containing the pending intake files.

For local API use, set `OPENAI_API_KEY` in the environment. In Bash, this reads it without echoing it or placing its value in shell history:

```bash
read -r -s -p 'OpenAI API key: ' OPENAI_API_KEY
printf '\n'
export OPENAI_API_KEY
python -m utility_scripts.ingest ingest
unset OPENAI_API_KEY
```

GitHub Actions is the normal processing environment: lab members only upload or push documents. Local execution is for development and troubleshooting. `.env` files are ignored by Git but are not loaded automatically; prefer the shell environment for a local test.

Never put the key in configuration, prompts, commits, or intake. Requests send extracted Markdown for summarization and pairs of summaries/keywords for relationship inference. The Responses API adapter uses structured JSON output and `store: false`; this setting is not a claim that all provider retention is disabled. Confirm the lab's account and data-sharing requirements before submitting restricted material.

## Configuration and cost controls

Settings live in [config/ingestion.json](config/ingestion.json). Prompt versions refer to [prompts/](prompts/); preserve older prompt files when introducing a new version. Metadata records the version, prompt hash, provider, model, settings, and extraction tool. Updating configuration does not regenerate existing summaries or relationships. Summary prompt `v2` requests an array of exactly 100 non-whitespace word strings through the structured-output schema. The adapter validates the array and joins it with spaces; stored summaries remain plain text. This avoids relying on the model to count prose words. Unreadable or insufficient content can return a null array and is rejected without inventing a summary. Prompt `v1` remains available for provenance and legacy configuration, but retains the less reliable prose-counting approach.

| Setting | Default | Meaning |
| --- | --- | --- |
| `provider` | `openai` | Only implemented provider; no silent fallback. |
| `model` | `gpt-4.1-mini-2025-04-14` | Explicit model snapshot; the alias `gpt-4.1-mini` is also supported. |
| `model_context_tokens` | 1,047,576 | Checked against the model profile. |
| `max_output_tokens` | 2,048 | Per-response output cap. |
| `temperature` | 0 | Generation setting, not a guarantee of deterministic model output. |
| `max_file_bytes` | 20,971,520 | Maximum original file size (20 MiB). |
| `max_extracted_input_tokens` | 100,000 | Conservative token upper bound: one token per UTF-8 byte of extracted text. |
| `max_new_documents` | 10 | Maximum distinct new sources in one batch. |
| `max_api_requests` | 300 | Batch-wide attempt cap, including retries. |
| `request_timeout_seconds` | 60 | HTTP transport timeout. |
| `max_pdf_pages` | 300 | Reject longer PDFs before extraction. |
| `max_pdf_page_stream_bytes` | 10,000,000 | Reject oversized decompressed page streams. |

The input bound intentionally overestimates token counts and may reject a document that would fit the model. It avoids tokenizer downloads and paid token-count calls. Each complete request is checked against the model context limit with an 8,192-token framing reserve; inputs are never silently truncated. New model families require a reviewed profile and adapter compatibility check in `utility_scripts/contracts.py`, not just a config rename.

For `n` stored documents and `m` new documents, a successful batch needs at least `m + n*m + m*(m-1)/2` requests: `m` summaries, `n*m` old/new pairs, and one comparison for each unordered new/new pair. Preflight reserves three attempts for every request. A batch that cannot fit this worst-case count is rejected before API work. For example, one new document with 100 existing documents needs up to 303 attempts, exceeding the default budget. Increase the budget deliberately or plan a future candidate-selection strategy as the collection grows. These are request counts, not dollar estimates; configure account-level spending limits separately.

## Permanent records and derived outputs

- `sources/<document_id>/original.pdf` or `original.md` stores exact original bytes. The ID is their full SHA-256 digest.
- `KG/node_contents/<document_id>/content.md` stores extracted or submitted text. `metadata.json` stores its hash, title, summary, keywords, timestamp, and provenance.
- `KG/relationships.json` stores accepted, canonical unordered pairs and their inference provenance. No edge between two existing documents represents a previously evaluated negative decision under the original ingestion settings; rebuild never reevaluates it.
- `KG/KG.graphml`, `KG/KG.png`, and the marked README section are derived outputs. Rebuild these from the permanent records. Stable ordering and a fixed graph-layout seed make repeated rendering reproducible in the same dependency/runtime environment; PNG bytes may differ across operating systems or library versions. The generated README image URL includes `?v=<PNG SHA-256>` so changed images receive a new cache key; identical image bytes keep the same URL. If an organization-profile README embeds the image separately, update its image URL with the same query value when refreshing that profile; this pipeline only manages this repository’s README.

The source archive and record directories must agree. Restore missing records from Git rather than treating a partial collection as new. Do not edit hashes to hide changed source bytes. Version merging, human review queues, and bulk re-inference remain outside v0.1.

For a summary/keyword correction, edit the matching metadata record while keeping the summary at exactly 100 whitespace-separated words and exactly 10 distinct keywords. For an erroneous connection, edit its rationale or remove its entry from `relationships.json`. Describe the human correction in the Git commit/PR; preserve the original generation provenance. Then run `rebuild`, `validate`, and the tests, review the generated changes, and commit the correction and derived outputs together. The existing provider provenance describes the original generation, not human verification.

## Publication, failures, and recovery

The ingestion action runs after intake changes land on `main`, or through manual dispatch on `main`. It serializes ingestion jobs, checks out current `main`, runs offline tests, and processes the entire queue. It uses only `GITHUB_TOKEN` for Git publication and exposes the OpenAI secret only to the ingestion step. Pull-request validation has read-only permissions and no provider secrets.

All extraction and API work happens before applying a staged result. Ordinary local write failures roll back applied files. Process termination or hardware failure during local writes is not a multi-file filesystem transaction: use Git to inspect/recover the last committed state. In CI, nothing becomes public until one complete commit is pushed. A rejected push leaves the remote collection and intake unchanged; the disposable runner may retain staged output until it is discarded.

Publication uses a separate temporary Git index and a commit object with the original base as its parent. It never stages unrelated files, moves the local branch, or force-pushes. It checks remote `main` before publication; a concurrent branch update also causes the normal push to reject the divergent commit. Because the local branch is intentionally unchanged, discard a successful CI checkout rather than continuing normal development in it. If a network failure makes the push result uncertain, inspect remote `main` before retrying; an already-published batch will have no remaining intake.

| Failure | Next step |
| --- | --- |
| Missing key, HTTP 401/403, or model rejection | Correct the Actions secret/model access, then manually run ingestion on `main`. |
| Rate limit, timeout, or service failure | At most three attempts are made per operation. Logs show a sanitized reason for each failed attempt and retain the final reason. Wait for recovery, then rerun. |
| Exhausted credits or billing quota | Recognized billing-quota errors stop immediately without retries. Check credits and project limits before another run. |
| Invalid summary or relationship after retries | Read the validation reason (including the actual summary word count). Repair attempts receive the previous output and specific feedback. Review the input for readability and sufficient substance before retrying. No malformed record is saved. |
| Scanned, encrypted, corrupt, or textless PDF page | Submit a permitted text-based copy or a self-contained Markdown version. Blank pages also require cleanup in v0.1. |
| Limit exceeded | Reduce the pending batch or adjust the relevant limit after checking model limits and cost. |
| `main` advanced or branch rules rejected the push | Retry from latest `main`; resolve publication policy with the repository administrator. |
| Broken derived graph/README | Run `rebuild` and `validate`, review, and commit the repaired outputs. |
| Corrupt/missing persistent record | Restore the complete record and original source from Git before retrying. |

Failed unpublished batches can incur repeated API costs when retried. Completed batches and duplicate-only submissions do not repeat LLM work. File renaming does not change identity; editing bytes does.

## Implementation references

The adapter follows [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs); model limits come from the [GPT-4.1 mini model documentation](https://developers.openai.com/api/docs/models/gpt-4.1-mini). PDF text extraction uses [pypdf's layout mode](https://pypdf.readthedocs.io/en/stable/user/extract-text.html), falling back to standard text extraction when layout mode returns no text (for example, covers whose text is inside a Form XObject). The extraction provenance records whether this fallback was used. Pages empty in both modes still fail; no OCR is performed. Workflow behavior follows [GitHub Actions concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency) and [workflow events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows). Pushes using `GITHUB_TOKEN` do not ordinarily start another workflow run, so generated commits are validated before publication.

## Manual document deletion

Use **Actions → Delete document → Run workflow** on `main`, providing the full 64-character `document_id` from metadata. The workflow is manual-only and needs `contents: write`, but no OpenAI secret. It shares the ingestion concurrency group, checks out the latest `main`, runs offline tests, previews the deletion in its logs, then publishes one commit. Branch protection must permit the bot's push, as for ingestion; a rejected push leaves the remote collection unchanged.

Deletion removes the selected content, metadata, archived original, and incident relationships. It validates and rebuilds GraphML, PNG, and README before applying the change. Unknown or malformed IDs fail without modifying the collection. Other documents and pending intake files are preserved. Re-uploading a deleted source can recreate the node. This is removal from the current collection, not an erasure of Git history.

For local inspection, run `python -m utility_scripts.delete_node --document-id FULL_DOCUMENT_ID --dry-run`. Without `--dry-run`, this changes local files; `--publish` is intended only for a clean disposable CI checkout. If publication fails because `main` advanced, rerun the workflow from the latest `main`. Restore an accidentally deleted document by re-uploading its original from Git history, or revert the deletion commit through the normal review process.
