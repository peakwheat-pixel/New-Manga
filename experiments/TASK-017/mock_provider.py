"""OpenAI-compatible mock provider for the TASK-017 protocol experiment.

A threaded ``http.server`` exposing ``POST /v1/chat/completions`` with an
OpenAI-shaped envelope. Deterministic behavior: the "translation" is a
rule transform of the source text (prefix + pseudo-translation), with
glossary terms applied so terminology consistency is machine-checkable.

Fault injection per instance, consumed in order, then falls back to ok:

- ``malformed_json`` / ``empty`` / ``drop:<id>`` / ``dup:<id>`` /
  ``extra:<id>`` — protocol-level output faults
- ``http_503`` / ``http_401`` — transport/auth faults (D06 §56 classes)

Every request payload is recorded so the suite can prove D06 §57 (retry
does not change the input) against the exact bytes.
"""

from __future__ import annotations

import json
import threading
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from protocol import RegionInput, estimate_tokens


def deterministic_translation(region: RegionInput, glossary: dict[str, str]) -> str:
    """Rule translation: glossary terms survive verbatim, the rest is a
    stable pseudo-translation (so glossary consistency is checkable)."""
    text = region.text
    placeholders: dict[str, str] = {}
    for index, (source, target) in enumerate(glossary.items()):
        if source in text:
            token = f"\x00{index}\x00"
            text = text.replace(source, token)
            placeholders[token] = target
    pseudo = "".join(
        chr(0x4E00 + (ord(ch) * 7) % 500) if ord(ch) > 0x2E80 else ch for ch in text
    )
    for token, target in placeholders.items():
        pseudo = pseudo.replace(token, target)
    return f"[T]{pseudo}"


class MockProvider:
    """In-process OpenAI-compatible server with scripted faults."""

    def __init__(
        self,
        faults: list[str] | None = None,
        *,
        name: str = "mock-primary",
        model: str = "mock-chat-1",
        latency_ms: int = 0,
    ) -> None:
        self.name = name
        self.model = model
        self.latency_ms = latency_ms
        self.faults = list(faults or [])
        self.requests: list[dict] = []  # recorded payloads (parsed)
        self.raw_bodies: list[str] = []
        self.lock = threading.Lock()
        self._fault_index = 0
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):  # silence the default stderr spam
                pass

            def do_POST(self):  # noqa: N802 (stdlib naming)
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length).decode("utf-8")
                fault = outer._next_fault()
                with outer.lock:
                    outer.raw_bodies.append(body)
                try:
                    envelope = json.loads(body)
                    content = envelope["messages"][-1]["content"]
                    payload = json.loads(content)
                except Exception:
                    payload = {}
                with outer.lock:
                    outer.requests.append(payload)

                if fault == "http_503":
                    self._respond(503, {"error": {"message": "unavailable"}})
                    return
                if fault == "http_401":
                    self._respond(401, {"error": {"message": "bad key"}})
                    return

                if outer.latency_ms:
                    outer._sleep_ms(outer.latency_ms)
                content_text = outer._complete(payload, fault)
                self._respond(200, {
                    "id": f"chatcmpl-{outer.name}",
                    "object": "chat.completion",
                    "model": outer.model,
                    "choices": [
                        {"index": 0, "message": {"role": "assistant", "content": content_text},
                         "finish_reason": "stop"}
                    ],
                    "usage": {"total_tokens": estimate_tokens(content_text)},
                })

            def _respond(self, status: int, obj: dict) -> None:
                data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.port = self._server.server_address[1]
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    # -- lifecycle ----------------------------------------------------
    def start(self) -> "MockProvider":
        self._thread.start()
        return self

    def stop(self) -> None:
        self._server.shutdown()
        self._server.server_close()

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}/v1"

    # -- behavior ------------------------------------------------------
    def _next_fault(self) -> str:
        with self.lock:
            if self._fault_index < len(self.faults):
                fault = self.faults[self._fault_index]
                self._fault_index += 1
                return fault
        return "ok"

    @staticmethod
    def _sleep_ms(ms: int) -> None:
        import time

        time.sleep(ms / 1000.0)

    def _complete(self, payload: dict, fault: str) -> str:
        regions = payload.get("regions", [])
        glossary = payload.get("glossary", {})
        rows = []
        for item in regions:
            region = RegionInput(item["region_id"], item["text"])
            if fault == f"drop:{region.region_id}":
                continue
            translated = deterministic_translation(region, glossary)
            if fault == f"dup:{region.region_id}":
                rows.append({"region_id": region.region_id, "translated_text": translated})
            rows.append({"region_id": region.region_id, "translated_text": translated})
        if fault == "extra:region-999":
            rows.append({"region_id": "region-999", "translated_text": "[T]越界"})
        if fault == "empty":
            rows = []
        if fault == "malformed_json":
            return "抱歉，我无法输出 JSON。翻译如下：……"
        return json.dumps(
            {"translations": rows, "provider": self.name, "model": self.model},
            ensure_ascii=False,
        )


class ProtocolClient:
    """Minimal OpenAI-compatible client used by the experiment.

    Returns ``(raw_content_or_error, fault_kind)`` where fault_kind uses
    the D06 §56 vocabulary; only the transport errors are produced here —
    protocol-level violations are classified by ``validate_response``.
    """

    def __init__(self, base_url: str, *, timeout: float = 5.0) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def complete(self, request_payload: dict) -> tuple[str, str]:
        import urllib.error
        import urllib.request

        envelope = {
            "model": "mock-chat-1",
            "messages": [
                {"role": "system", "content": "You are a manga translation engine."},
                {"role": "user", "content": json.dumps(request_payload, ensure_ascii=False)},
            ],
            "temperature": 0,
        }
        data = json.dumps(envelope, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            kind = "http_401" if error.code == 401 else "http_5xx" if error.code >= 500 else "http_4xx"
            return "", kind
        except urllib.error.URLError as error:
            return "", "read_timeout" if isinstance(getattr(error, "reason", None), TimeoutError) else "http_5xx"
        content = body["choices"][0]["message"]["content"]
        return content, "ok"


def make_client_factory(base_url: str) -> Callable[[], ProtocolClient]:
    return lambda: ProtocolClient(base_url)
