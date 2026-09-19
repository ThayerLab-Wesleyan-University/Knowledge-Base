# PDF intake

Place `.pdf` submissions directly in this directory, without subfolders. Submit only material permitted to be stored in this repository and sent to the configured LLM provider.

Once implemented, the ingestion workflow will extract Markdown, generate a summary and keywords, and add the document to the knowledge graph. It will archive the original PDF under `sources/<document_id>/` and remove the intake copy only after successful publication. Failed submissions remain here for retry.

Scanned PDFs requiring OCR and encrypted PDFs are unsupported in the first version. Extraction may lose equations, figures, or table structure.

Keep this README; it is excluded from ingestion. See the [project plan](../README.md) for implementation status and the full workflow.
