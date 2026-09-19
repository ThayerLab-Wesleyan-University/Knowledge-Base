"""One-provider structured output adapter, with one shared request/retry budget."""
from __future__ import annotations

import json
import os
import time

import httpx

from utility_scripts.contracts import (
    KBError, RELATIONSHIP_RESPONSE, SUMMARY_RESPONSE, digest,
    validate_relationship, validate_summary,
)


class OpenAI:
    def __init__(self, root, config, *, transport=None, sleep=time.sleep):
        key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key:
            raise KBError("Set OPENAI_API_KEY before ingestion; dry-run and rebuild need no key.")
        self.config = config
        self.prompts = {task: (root / "prompts" / f"{task}-{config[task + '_prompt_version']}.txt").read_text()
                        for task in ("summary", "relationship")}
        self.client = httpx.Client(
            headers={"Authorization": f"Bearer {key}"},
            timeout=config["request_timeout_seconds"], transport=transport,
            follow_redirects=False,
        )
        self.requests = 0
        self.sleep = sleep

    def close(self):
        self.client.close()

    def provenance(self, task):
        return {"provider": self.config["provider"], "model": self.config["model"],
                "prompt_version": self.config[task + "_prompt_version"],
                "prompt_sha256": digest(self.prompts[task].encode()),
                "settings": {k: self.config[k] for k in ("temperature", "max_output_tokens")}}

    def _request(self, task, payload, schema, validator):
        correction = ""
        for attempt in range(3):
            if self.requests >= self.config["max_api_requests"]:
                raise KBError("API request budget exhausted; nothing has been published.")
            body = {
                "model": self.config["model"], "store": False,
                "instructions": self.prompts[task] + correction,
                "input": json.dumps(payload, ensure_ascii=False),
                "temperature": self.config["temperature"],
                "max_output_tokens": self.config["max_output_tokens"],
                "text": {"format": {"type": "json_schema", "name": task,
                                     "strict": True, "schema": schema}},
            }
            # UTF-8 bytes provide a conservative upper bound for byte-level tokens;
            # reserve additional room for protocol framing. No truncation or token API.
            bound = len(json.dumps(body, ensure_ascii=False).encode()) + 8192
            if bound + self.config["max_output_tokens"] > self.config["model_context_tokens"]:
                raise KBError("Request exceeds the model context budget; reduce the input size.")
            self.requests += 1
            try:
                response = self.client.post("https://api.openai.com/v1/responses", json=body)
                if response.status_code in (408, 409, 429) or response.status_code >= 500:
                    raise KBError(f"Transient provider error (HTTP {response.status_code}).")
                if response.status_code != 200:
                    # Never include provider bodies: they may echo submitted text.
                    raise PermissionError(f"Provider rejected request (HTTP {response.status_code}); check key, model, and quota.")
                data = response.json()
                if not isinstance(data, dict):
                    raise KBError("Provider returned an invalid response envelope.")
                if data.get("status") != "completed":
                    raise KBError("Provider did not complete the response; check output limits.")
                texts = [part["text"] for item in data.get("output", [])
                         if item.get("type") == "message"
                         for part in item.get("content", []) if part.get("type") == "output_text"]
                if len(texts) != 1:
                    raise KBError("Provider refused or returned no single structured output.")
                return validator(json.loads(texts[0]))
            except PermissionError as exc:
                raise KBError(str(exc)) from exc
            except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError, KBError) as exc:
                if attempt == 2:
                    raise KBError(f"{task.capitalize()} failed after 3 attempts; no batch published.") from exc
                correction = "\nThe prior attempt failed transport or local validation. Recheck the required schema, word count, keyword uniqueness, and supplied IDs."
                self.sleep(2 ** attempt)
        raise AssertionError("unreachable")

    def summarize(self, title_hint, content):
        return self._request("summary", {"filename_stem": title_hint, "document": content},
                             SUMMARY_RESPONSE, validate_summary)

    def relate(self, a, b):
        keys = ("document_id", "title", "summary", "keywords")
        payload = {"source": {k: a[k] for k in keys}, "target": {k: b[k] for k in keys}}
        return self._request("relationship", payload, RELATIONSHIP_RESPONSE,
                             lambda value: validate_relationship(value, a["document_id"], b["document_id"]))
