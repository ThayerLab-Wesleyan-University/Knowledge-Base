"""Canonical record loading and optimistic, rollback-capable file updates."""
from __future__ import annotations

import os
from pathlib import Path

from utility_scripts.contracts import (
    KBError, digest, read_json, validate_edges, validate_metadata,
)


def checked_path(root, relative):
    path = root / relative
    if path.is_absolute() and not path.is_relative_to(root):
        raise KBError("Path escapes the repository.")
    for part in (path, *path.parents):
        if part == root:
            break
        if part.is_symlink():
            raise KBError("Symlinks are not supported in pipeline-owned paths.")
    if not path.resolve().is_relative_to(root.resolve()):
        raise KBError("Path escapes the repository.")
    return path


def load_collection(root):
    records = {}
    directory = checked_path(root, "KG/node_contents")
    if directory.exists():
        for entry in sorted(directory.iterdir()):
            checked_path(root, entry.relative_to(root))
            if not entry.is_dir():
                raise KBError("Unexpected file in KG/node_contents; expected document directories.")
            meta = read_json(checked_path(root, entry.relative_to(root) / "metadata.json"))
            validate_metadata(meta)
            doc_id = meta["document_id"]
            if entry.name != doc_id:
                raise KBError("Document directory does not match its ID.")
            if {p.name for p in entry.iterdir()} != {"metadata.json", "content.md"}:
                raise KBError("Document bundle must contain content.md and metadata.json only.")
            for key, expected in (("source_path", doc_id), ("content_path", meta["content_sha256"])):
                path = checked_path(root, meta[key])
                if not path.is_file() or digest(path.read_bytes()) != expected:
                    raise KBError(f"Missing or modified {key} for document {doc_id}.")
            records[doc_id] = meta
    sources = checked_path(root, "sources")
    if sources.exists():
        if {p.name for p in sources.iterdir()} != set(records):
            raise KBError("Archived sources and document records disagree; repair before ingestion.")
        for doc_id, record in records.items():
            folder = checked_path(root, f"sources/{doc_id}")
            if {p.name for p in folder.iterdir()} != {Path(record["source_path"]).name}:
                raise KBError("Archive must contain exactly one original source per document.")
    relation_path = checked_path(root, "KG/relationships.json")
    if relation_path.exists():
        relationships = read_json(relation_path)
    elif records:
        raise KBError("Existing collection is missing KG/relationships.json; restore it from Git.")
    else:
        relationships = {"schema_version": 1, "edges": []}
    validate_edges(relationships, records)
    return records, relationships


def snapshot(root, extra=()):
    """Include inputs/config as guards so edits made during API work are not lost."""
    result = {}
    for rel in ("README.md", "KG/node_contents", "sources", "KG/relationships.json",
                "KG/KG.graphml", "KG/KG.png", "pdf", "markdown", "config", "prompts", *extra):
        path = checked_path(root, rel)
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                checked_path(root, child.relative_to(root))
                if child.is_file():
                    result[child.relative_to(root).as_posix()] = child.read_bytes()
        elif path.is_file():
            result[rel] = path.read_bytes()
    return result


def atomic_write(path, data):
    import tempfile
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".kb-write-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def apply_changes(root, before, updates, removals):
    if snapshot(root) != before:
        raise KBError("Repository inputs or outputs changed during ingestion; retry without concurrent edits.")
    changed = sorted(path for path, data in updates.items() if before.get(path) != data)
    paths = changed + sorted(removals)
    for rel in paths:
        checked_path(root, rel)
    applied = []
    try:
        for rel in changed:
            applied.append(rel)
            atomic_write(root / rel, updates[rel])
        for rel in sorted(removals):
            applied.append(rel)
            (root / rel).unlink()
    except Exception:
        # Ordinary I/O failures roll back. Process termination is handled by Git:
        # a fresh checkout restores the intake and last committed collection.
        for rel in reversed(applied):
            if rel in before:
                atomic_write(root / rel, before[rel])
            else:
                (root / rel).unlink(missing_ok=True)
        # Remove only newly created empty output directories.
        for rel in sorted({str(Path(p).parent) for p in applied}, reverse=True):
            path = root / rel
            while path != root and path.is_dir() and not any(path.iterdir()):
                path.rmdir()
                path = path.parent
        raise
    return sorted(paths)
