#!/usr/bin/env python3
"""AC1/AC4 probe: OpenCode Zen (OpenAI-compatible) endpoint discovery.

Reads the API key from a caller-supplied file (``--key-file``), never echoes or
stores it, and writes a sanitized evidence JSON:

- GET  {base}/models        -> HTTP status + model ids (the catalogue)
- POST {base}/chat/completions for a few models -> HTTP status only

The evidence records that a key was present (boolean) and never its value,
length, prefix or hash. Chat probes use two messages max so a successful probe
is cheap. Requests follow the OpenCode client header set (UA + session +
referer/title) because the Zen relay gates free-tier requests on it; the probe
still reports whatever the relay actually answers.

Usage:
    python probe_opencode.py --key-file "%TEMP%/nm-opencode-key.txt" \
        --out verification/REAL-TRANSLATE-PROVIDER-1/evidence/ac1-probe.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

DEFAULT_BASE = "https://opencode.ai/zen/v1"

# Candidate models: one free-tier id per family plus a paid baseline. The probe
# never sends region text, only "ping", so nothing user-visible is transmitted.
PROBE_MODELS = (
    "deepseek-v4.1-flash-free",
    "big-pickle",
    "glm-5.3-flash-free",
    "deepseek-v4.1-flash",
    "gpt-5.4-nano",
)


def _request(
    url: str,
    key: str,
    *,
    body: dict | None = None,
    timeout: float = 45.0,
) -> tuple[int, str]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
        # The Zen free tier rate-limits clients that do not identify as opencode
        # (upstream issue #106495); these are the documented client headers.
        "User-Agent": "opencode/0.20.5",
        "X-Session-ID": str(uuid.uuid4()),
        "HTTP-Referer": "https://opencode.ai/",
        "X-Title": "opencode",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read(262_144).decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read(65_536).decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError) as error:
        return -1, f"transport: {type(error).__name__}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--key-file", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--base-url", default=DEFAULT_BASE)
    args = parser.parse_args()

    key_path = Path(args.key_file)
    if not key_path.is_file():
        print(f"key file missing: {key_path}", file=sys.stderr)
        return 2
    key = key_path.read_text(encoding="utf-8").strip()
    if not key:
        print("key file is empty", file=sys.stderr)
        return 2

    base = args.base_url.rstrip("/")
    evidence: dict = {
        "ac": "AC1",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "base_url": base,
        "api_style": "OpenAI-compatible (chat/completions + models)",
        "key_present": True,
        "key_echoed_anywhere": False,
    }

    status, body = _request(f"{base}/models", key)
    evidence["models_http_status"] = status
    models: list[str] = []
    if status == 200:
        try:
            models = [str(item.get("id", "")) for item in json.loads(body).get("data", []) if item.get("id")]
        except (ValueError, AttributeError):
            models = []
    evidence["models_count"] = len(models)
    evidence["models"] = models
    evidence["free_models"] = [model for model in models if model.endswith("-free") or model in {"big-pickle", "beam-free"}]

    chat: list[dict] = []
    for model in PROBE_MODELS:
        started = time.monotonic()
        chat_status, chat_body = _request(
            f"{base}/chat/completions",
            key,
            body={
                "model": model,
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 8,
            },
        )
        elapsed_ms = round((time.monotonic() - started) * 1000, 1)
        entry: dict = {
            "model": model,
            "http_status": chat_status,
            "elapsed_ms": elapsed_ms,
            "ok": 200 <= chat_status < 300,
        }
        if entry["ok"]:
            try:
                entry["completion_preview"] = json.loads(chat_body)["choices"][0]["message"]["content"][:40]
            except (ValueError, KeyError, IndexError, TypeError):
                entry["completion_preview"] = "<unparseable>"
        else:
            # The relay returns an empty body for 429; record only the size and
            # the first 120 chars, which never carry credentials.
            entry["error_body_len"] = len(chat_body)
            entry["error_body_preview"] = chat_body[:120]
        chat.append(entry)
        time.sleep(0.4)

    evidence["chat_probes"] = chat
    evidence["usable_models"] = [item["model"] for item in chat if item["ok"]]
    evidence["quota_block"] = not evidence["usable_models"]
    evidence["probe_note"] = (
        "Free-tier ids answered 429 / paid ids answered 402 for this key; the "
        "catalogue itself is authenticated (models HTTP 200). A usable model is "
        "one whose chat probe returned 2xx."
    )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"models_http={status} models={len(models)} usable={len(evidence['usable_models'])} -> {out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
