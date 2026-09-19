# Markdown intake

Place `.md` submissions directly in this directory, without subfolders. Use self-contained text; local image and file dependencies are unsupported. Reserve the filename `README.md` for these instructions.

Submit only material permitted to be stored in this repository and sent to the configured LLM provider. Once implemented, the ingestion workflow will preserve the document text, generate a summary and keywords, and add the document to the knowledge graph. It will archive the original under `sources/<document_id>/` and remove the intake copy only after successful publication. Failed submissions remain here for retry.

Keep this README; it is excluded from ingestion. See the [project plan](../README.md) for implementation status and the full workflow.
