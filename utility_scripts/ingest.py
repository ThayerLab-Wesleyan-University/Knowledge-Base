"""Run with python -m utility_scripts.ingest {ingest,rebuild,validate}."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import logging
from pathlib import Path
import re
import tempfile

from KG.append_node import build_graph, write_graph
from KG.visualize_KG import render_image, render_readme, split_readme
from utility_scripts.contracts import (
    KBError, digest, json_bytes, load_config, safe_text, validate_edges,
    validate_metadata, validate_relationship, validate_summary,
)
from utility_scripts.llm import OpenAI
from utility_scripts.pdf2md import convert_pdf
from utility_scripts.publish import publication_base, publish
from utility_scripts.storage import apply_changes, checked_path, load_collection, snapshot


LOGGER = logging.getLogger(__name__)


def now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def repository_lock(root):
    # Advisory lock outside the worktree; automatically released on process exit.
    lock = Path(tempfile.gettempdir()) / f"kb-{digest(str(root).encode())}.lock"
    with lock.open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise KBError("Another pipeline process is using this checkout.") from exc
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def discover(root, config):
    inputs = []
    for folder, suffix in (("pdf", ".pdf"), ("markdown", ".md")):
        directory = checked_path(root, folder)
        if not directory.is_dir():
            raise KBError(f"Missing intake directory: {folder}.")
        for path in sorted(directory.iterdir()):
            if path.name.startswith(".") or path.name == "README.md":
                continue
            checked_path(root, path.relative_to(root))
            if not path.is_file() or path.suffix.lower() != suffix:
                raise KBError(f"Unsupported submission in {folder}; use direct {suffix} files only.")
            if path.stat().st_size == 0 or path.stat().st_size > config["max_file_bytes"]:
                raise KBError(f"Submission in {folder} is empty or exceeds max_file_bytes.")
            inputs.append(path)
    return inputs


def markdown_text(data):
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise KBError("Markdown must use UTF-8 encoding.") from exc
    safe_text(text, "Markdown")
    # Local dependencies would break when intake moves to a content-hash directory.
    destinations = re.findall(r"!?\[[^\]]*\]\(\s*<?([^\s)>]+)", text)
    # Footnote definitions contain prose, not reference-link destinations.
    # Inline links inside footnotes are still checked by the scan above.
    destinations += re.findall(r"^\s*\[(?!\^)[^\]]+\]:\s*<?([^\s>]+)", text, re.MULTILINE)
    destinations += re.findall(r"(?:src|href)\s*=\s*['\"]([^'\"]+)", text, re.IGNORECASE)
    if any(not (p.startswith(("https://", "http://", "mailto:", "#"))) for p in destinations):
        raise KBError("Markdown contains local or unsupported links; use self-contained text and HTTPS references.")
    return text


def prepare(root, config, records, paths):
    new = {}
    for path in paths:
        data = path.read_bytes()
        doc_id = digest(data)
        if doc_id in records or doc_id in new:
            LOGGER.info("Reusing document %s", doc_id)
            continue
        LOGGER.info("Extracting document %s", doc_id)
        if path.suffix.lower() == ".pdf":
            content, extraction = convert_pdf(data, config)
            source_type = "pdf"
        else:
            content, extraction = markdown_text(data), {"tool": "utf8-passthrough", "version": "1"}
            source_type = "md"
        if len(content.encode()) > config["max_extracted_input_tokens"]:
            raise KBError(f"Document {doc_id} exceeds the conservative input-token limit; submit a shorter document or review the configured limit.")
        new[doc_id] = {"data": data, "content": content, "source_type": source_type,
                       "filename": path.name, "extraction": extraction}
    if len(new) > config["max_new_documents"]:
        raise KBError("Batch exceeds max_new_documents; reduce the intake queue or review the limit.")
    minimum = len(new) + len(new) * len(records) + len(new) * (len(new) - 1) // 2
    # Reserve all permitted retries, so the planned batch cannot exceed the budget.
    if minimum * 3 > config["max_api_requests"]:
        raise KBError(f"Batch needs up to {minimum * 3} API requests including retries; limit is {config['max_api_requests']}.")
    return new, minimum


def validate_outputs(root, records, relationships):
    import networkx as nx
    graph = build_graph(records, relationships)
    path = checked_path(root, "KG/KG.graphml")
    try:
        saved = nx.read_graphml(path)
    except Exception as exc:
        raise KBError("Missing or invalid GraphML; run rebuild.") from exc
    if saved.is_directed() or saved.is_multigraph() or dict(saved.nodes(data=True)) != dict(graph.nodes(data=True)):
        raise KBError("Graph nodes disagree with stored records; run rebuild.")
    edges = lambda g: {frozenset((a, b)): d for a, b, d in g.edges(data=True)}
    if edges(saved) != edges(graph):
        raise KBError("Graph edges disagree with stored records; run rebuild.")
    image = checked_path(root, "KG/KG.png")
    if not image.is_file() or not image.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
        raise KBError("Missing or invalid graph PNG; run rebuild.")
    versioned = checked_path(root, f"KG/rendered/{digest(image.read_bytes())}.png")
    if not versioned.is_file() or versioned.read_bytes() != image.read_bytes():
        raise KBError("Missing or inconsistent versioned graph PNG; run rebuild.")
    readme = checked_path(root, "README.md").read_bytes().decode("utf-8")
    if render_readme(readme, records, graph, relationships,
                     image_sha256=digest(image.read_bytes())) != readme:
        raise KBError("Generated README does not match the records; run rebuild.")
    for doc_id, attrs in graph.nodes(data=True):
        for key in ("content_path", "metadata_path", "source_path"):
            if not checked_path(root, attrs[key]).is_file():
                raise KBError(f"Graph contains a broken {key} link for {doc_id}.")


def build_outputs(stage, records, relationships):
    (stage / "KG").mkdir(exist_ok=True)
    (stage / "KG/relationships.json").write_bytes(json_bytes(relationships))
    graph = build_graph(records, relationships)
    write_graph(graph, stage / "KG/KG.graphml")
    render_image(graph, stage / "KG/KG.png")
    image_bytes = (stage / "KG/KG.png").read_bytes()
    (stage / "KG/rendered").mkdir(exist_ok=True)
    (stage / f"KG/rendered/{digest(image_bytes)}.png").write_bytes(image_bytes)
    readme = (stage / "README.md").read_bytes().decode("utf-8")
    (stage / "README.md").write_text(render_readme(
        readme, records, graph, relationships, image_sha256=digest((stage / "KG/KG.png").read_bytes())))
    checked_records, checked_edges = load_collection(stage)
    validate_outputs(stage, checked_records, checked_edges)


def derived_changes(stage, before):
    """Publish the current immutable image and remove superseded image files."""
    image_path = f"KG/rendered/{digest((stage / 'KG/KG.png').read_bytes())}.png"
    paths = ["README.md", "KG/relationships.json", "KG/KG.graphml", "KG/KG.png", image_path]
    updates = {rel: (stage / rel).read_bytes() for rel in paths}
    removals = [rel for rel in before
                if re.fullmatch(r"KG/rendered/[0-9a-f]{64}\.png", rel) and rel != image_path]
    return updates, removals


def run(root, command="ingest", *, dry_run=False, publish_changes=False, provider_factory=OpenAI):
    root = Path(root).resolve()
    with repository_lock(root):
        if publish_changes and (command != "ingest" or dry_run):
            raise KBError("--publish is available only for actual ingestion.")
        base = publication_base(root) if publish_changes else None
        before = snapshot(root)
        records, relationships = load_collection(root)
        split_readme((root / "README.md").read_bytes().decode("utf-8"))
        if command == "validate":
            validate_outputs(root, records, relationships)
            return {"documents": len(records), "edges": len(relationships["edges"]), "valid": True}
        paths, new, minimum = [], {}, 0
        if command == "ingest":
            config = load_config(root)
            paths = discover(root, config)
            new, minimum = prepare(root, config, records, paths)
        report = {"documents": len(records), "submissions": len(paths), "new_documents": len(new),
                  "duplicates": len(paths) - len(new), "minimum_api_requests": minimum,
                  "maximum_api_requests": minimum * 3, "changed_paths": []}
        if command == "ingest":
            report["files"] = [p.relative_to(root).as_posix() for p in paths]
            report["limits"] = {k: config[k] for k in ("max_file_bytes", "max_extracted_input_tokens",
                                                      "max_new_documents", "max_api_requests")}
        if dry_run:
            report["dry_run"] = True
            report["planned_action"] = "rebuild graph and README" if command == "rebuild" else "archive new documents, generate records/graph, remove handled intake files" if paths else "none"
            return report
        if command == "ingest" and not paths:
            return report
        removals = [p.relative_to(root).as_posix() for p in paths]
        if command == "ingest" and not new:
            report["changed_paths"] = apply_changes(root, before, {}, removals)
        else:
            with tempfile.TemporaryDirectory(prefix="kb-stage-") as temp:
                stage = Path(temp)
                # Stage just the guarded corpus/configuration, never .git or secrets.
                for rel, data in before.items():
                    dest = stage / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(data)
                if new:
                    provider = provider_factory(root, config)
                    try:
                        for doc_id, item in sorted(new.items()):
                            LOGGER.info("Summarizing document %s", doc_id)
                            try:
                                result = validate_summary(provider.summarize(Path(item["filename"]).stem, item["content"]))
                            except KBError as exc:
                                raise KBError(f"Document {doc_id}: {exc}") from exc
                            title = result["title"].strip()
                            if not title or " ".join(title.casefold().split()) not in " ".join(item["content"].casefold().split()):
                                title = Path(item["filename"]).stem
                            metadata = {
                                "schema_version": 1, "document_id": doc_id,
                                "source_filename": item["filename"], "source_type": item["source_type"],
                                "source_path": f"sources/{doc_id}/original.{item['source_type']}",
                                "content_path": f"KG/node_contents/{doc_id}/content.md",
                                "content_sha256": digest(item["content"].encode()), "title": title,
                                "summary": result["summary"], "keywords": result["keywords"],
                                "created_at": now(), "generation": provider.provenance("summary"),
                                "extraction": item["extraction"],
                            }
                            validate_metadata(metadata)
                            records[doc_id] = metadata
                            files = {metadata["source_path"]: item["data"],
                                     metadata["content_path"]: item["content"].encode(),
                                     f"KG/node_contents/{doc_id}/metadata.json": json_bytes(metadata)}
                            for rel, data in files.items():
                                (stage / rel).parent.mkdir(parents=True, exist_ok=True)
                                (stage / rel).write_bytes(data)
                        ids = sorted(records)
                        for i, a in enumerate(ids):
                            for b in ids[i + 1:]:
                                if a not in new and b not in new:
                                    continue
                                LOGGER.info("Comparing documents %s and %s", a, b)
                                try:
                                    relation = validate_relationship(provider.relate(records[a], records[b]), a, b)
                                except KBError as exc:
                                    raise KBError(f"Pair {a}, {b}: {exc}") from exc
                                if relation["related"]:
                                    relationships["edges"].append({
                                        "source": a, "target": b, "relation_type": "topical_similarity",
                                        "rationale": relation["rationale"], "inferred_by": "llm",
                                        "generation": provider.provenance("relationship"), "created_at": now(),
                                    })
                        report["api_requests"] = provider.requests
                    finally:
                        provider.close()
                relationships["edges"].sort(key=lambda e: (e["source"], e["target"]))
                validate_edges(relationships, records)
                build_outputs(stage, records, relationships)
                updates, obsolete_images = derived_changes(stage, before)
                output_paths = []
                for doc_id in new:
                    output_paths += [records[doc_id]["source_path"], records[doc_id]["content_path"],
                                     f"KG/node_contents/{doc_id}/metadata.json"]
                updates.update({rel: (stage / rel).read_bytes() for rel in output_paths})
                report["changed_paths"] = apply_changes(root, before, updates, removals + obsolete_images)
        report["documents"] = len(records)
        report["edges"] = len(relationships["edges"])
        if publish_changes:
            report["published_commit"] = publish(root, base, report["changed_paths"])
        return report


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    # HTTP logs are unnecessary; report pipeline stages without provider bodies.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("ingest", "rebuild", "validate"))
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root (default: current directory)")
    parser.add_argument("--dry-run", action="store_true", help="Inspect inputs without API calls or repository writes")
    parser.add_argument("--publish", action="store_true", help="Publish to origin/main from a clean disposable CI checkout")
    args = parser.parse_args()
    try:
        result = run(args.root, args.command, dry_run=args.dry_run, publish_changes=args.publish)
    except (KBError, OSError, UnicodeError) as exc:
        # Unexpected OS errors may contain document filenames, but never file bodies.
        print(f"ERROR: {exc}")
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
