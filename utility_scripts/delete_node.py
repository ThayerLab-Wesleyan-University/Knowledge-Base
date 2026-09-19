"""Delete one document and rebuild derived outputs, without LLM calls."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import tempfile

from utility_scripts.contracts import KBError
from utility_scripts.ingest import build_outputs, repository_lock
from utility_scripts.publish import publication_base, publish
from utility_scripts.storage import apply_changes, load_collection, snapshot


def run(root, document_id, *, dry_run=False, publish_changes=False):
    root = Path(root).resolve()
    if not re.fullmatch(r"[0-9a-f]{64}", document_id):
        raise KBError("Use the full 64-character lowercase document_id from metadata, not a D-number.")
    if dry_run and publish_changes:
        raise KBError("Dry-run cannot publish changes.")
    with repository_lock(root):
        base = publication_base(root) if publish_changes else None
        before = snapshot(root)
        records, relationships = load_collection(root)
        if document_id not in records:
            raise KBError("Document ID does not exist in this collection; nothing deleted.")
        record = records.pop(document_id)
        edges = relationships["edges"]
        relationships["edges"] = [e for e in edges if document_id not in (e["source"], e["target"])]
        removals = [record["source_path"], record["content_path"],
                    f"KG/node_contents/{document_id}/metadata.json"]
        report = {"document_id": document_id, "title": record["title"],
                  "removed_connections": len(edges) - len(relationships["edges"]),
                  "removed_paths": removals, "dry_run": dry_run}
        if dry_run:
            return report
        with tempfile.TemporaryDirectory(prefix="kb-delete-") as directory:
            stage = Path(directory)
            for rel, data in before.items():
                if rel not in removals:
                    path = stage / rel
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
            build_outputs(stage, records, relationships)
            updates = {rel: (stage / rel).read_bytes() for rel in
                       ("README.md", "KG/relationships.json", "KG/KG.graphml", "KG/KG.png")}
            report["changed_paths"] = apply_changes(
                root, before, updates, removals,
                empty_directories=(f"KG/node_contents/{document_id}", f"sources/{document_id}"))
        if publish_changes:
            report["published_commit"] = publish(
                root, base, report["changed_paths"], message=f"Delete knowledge base document {document_id}")
        return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--document-id", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--publish", action="store_true", help="Publish from a clean disposable main checkout")
    args = parser.parse_args()
    try:
        result = run(args.root, args.document_id, dry_run=args.dry_run, publish_changes=args.publish)
    except (KBError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
