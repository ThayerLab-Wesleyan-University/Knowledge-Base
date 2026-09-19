"""Versioned contracts shared by API validation and persistent storage."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator


class KBError(Exception):
    """An actionable failure safe to show without document contents or secrets."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise KBError(f"Cannot read valid JSON: {path.name}") from exc


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def object_schema(properties):
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


TEXT = {"type": "string", "minLength": 1}
ID = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
SUMMARY_RESPONSE = object_schema({
    "sufficient": {"type": "boolean"}, "title": {"type": "string"},
    "summary": {"type": "string"},
    "keywords": {"type": "array", "items": {"type": "string"}},
})
RELATIONSHIP_RESPONSE = object_schema({
    "source": TEXT, "target": TEXT, "related": {"type": "boolean"}, "rationale": TEXT,
})
GENERATION = object_schema({
    "provider": TEXT, "model": TEXT, "prompt_version": TEXT, "prompt_sha256": ID,
    "settings": object_schema({"temperature": {"type": "number"},
                               "max_output_tokens": {"type": "integer", "minimum": 1}}),
})
METADATA = object_schema({
    "schema_version": {"const": 1}, "document_id": ID, "source_filename": TEXT,
    "source_type": {"enum": ["pdf", "md"]}, "source_path": TEXT, "content_path": TEXT,
    "content_sha256": ID, "title": TEXT, "summary": TEXT,
    "keywords": {"type": "array", "items": TEXT, "minItems": 10, "maxItems": 10},
    "created_at": TEXT, "generation": GENERATION,
    "extraction": object_schema({"tool": TEXT, "version": TEXT}),
})
EDGE = object_schema({
    "source": ID, "target": ID, "relation_type": {"const": "topical_similarity"},
    "rationale": TEXT, "inferred_by": {"const": "llm"},
    "generation": GENERATION, "created_at": TEXT,
})
RELATIONSHIPS = object_schema({
    "schema_version": {"const": 1}, "edges": {"type": "array", "items": EDGE},
})


def validate_schema(value, schema, label):
    # Do not interpolate jsonschema error messages: they may contain source text.
    error = next(Draft202012Validator(schema).iter_errors(value), None)
    if error:
        field = ".".join(map(str, error.absolute_path)) or "root"
        raise KBError(f"Invalid {label}: field {field} violates {error.validator}.")


def safe_text(text: str, label: str):
    if not text.strip() or re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]", text):
        raise KBError(f"Invalid or empty {label}.")


def validate_summary(value):
    validate_schema(value, SUMMARY_RESPONSE, "summary response")
    if not value["sufficient"]:
        raise KBError("Insufficient document content for a grounded summary and ten keywords.")
    safe_text(value["summary"], "summary")
    word_count = len(value["summary"].split())
    if word_count != 100:
        raise KBError(f"Summary must contain exactly 100 whitespace-separated words; received {word_count}.")
    words = value["keywords"]
    if len(words) != 10 or len({w.strip().casefold() for w in words}) != 10:
        raise KBError("Keywords must contain exactly 10 distinct strings.")
    for word in words:
        safe_text(word, "keyword")
    value["keywords"] = [w.strip() for w in words]
    return value


def timestamp(value):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.utcoffset() is None or dt.utcoffset().total_seconds() != 0:
            raise ValueError
    except (ValueError, TypeError) as exc:
        raise KBError("Record timestamp must be UTC ISO 8601.") from exc


def validate_metadata(value):
    validate_schema(value, METADATA, "metadata")
    validate_summary({"sufficient": True, "title": value["title"],
                      "summary": value["summary"], "keywords": value["keywords"][:]})
    safe_text(value["title"], "title")
    timestamp(value["created_at"])
    doc_id = value["document_id"]
    if value["content_path"] != f"KG/node_contents/{doc_id}/content.md":
        raise KBError("Invalid canonical content path.")
    if value["source_path"] != f"sources/{doc_id}/original.{value['source_type']}":
        raise KBError("Invalid canonical source path.")


def validate_relationship(value, source, target):
    validate_schema(value, RELATIONSHIP_RESPONSE, "relationship response")
    if (value["source"], value["target"]) != (source, target):
        raise KBError("Relationship response must use the supplied IDs in order.")
    safe_text(value["rationale"], "relationship rationale")
    return value


def validate_edges(envelope, records):
    validate_schema(envelope, RELATIONSHIPS, "relationships")
    seen = set()
    for edge in envelope["edges"]:
        a, b = edge["source"], edge["target"]
        if a >= b or a not in records or b not in records or (a, b) in seen:
            raise KBError("Edges must be unique, ordered pairs of distinct existing document IDs.")
        seen.add((a, b))
        safe_text(edge["rationale"], "edge rationale")
        timestamp(edge["created_at"])


def load_config(root: Path):
    cfg = read_json(root / "config/ingestion.json")
    integers = ("model_context_tokens", "max_output_tokens", "max_file_bytes",
                "max_extracted_input_tokens", "max_new_documents", "max_api_requests",
                "request_timeout_seconds", "max_pdf_pages", "max_pdf_page_stream_bytes")
    props = {k: {"type": "integer", "minimum": 1} for k in integers}
    props.update({"schema_version": {"const": 1}, "provider": {"const": "openai"},
                  "model": TEXT, "temperature": {"type": "number", "minimum": 0, "maximum": 2},
                  "summary_prompt_version": {"type": "string", "pattern": "^v[0-9]+$"},
                  "relationship_prompt_version": {"type": "string", "pattern": "^v[0-9]+$"}})
    validate_schema(cfg, object_schema(props), "configuration")
    # Verified model limits; new models require an explicit reviewed profile.
    profiles = {"gpt-4.1-mini": (1047576, 32768),
                "gpt-4.1-mini-2025-04-14": (1047576, 32768)}
    if cfg["model"] not in profiles:
        raise KBError("Unsupported model profile; add reviewed limits in contracts.py before switching.")
    context, output = profiles[cfg["model"]]
    if cfg["model_context_tokens"] > context or cfg["max_output_tokens"] > output:
        raise KBError("Configured token limits exceed the selected model profile.")
    if cfg["max_extracted_input_tokens"] + cfg["max_output_tokens"] + 8192 > cfg["model_context_tokens"]:
        raise KBError("Input/output limits leave insufficient context for prompts and schemas.")
    for task in ("summary", "relationship"):
        path = root / "prompts" / f"{task}-{cfg[task + '_prompt_version']}.txt"
        if not path.is_file() or path.is_symlink() or not path.read_text().strip():
            raise KBError(f"Missing or invalid {task} prompt.")
    return cfg
