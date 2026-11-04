"""C-16 v1.1 I005 P1: encrypted PDF resolve passes the Secret-G to PDFium.

The r1-rework review found the PDF resolve path consumed the one-shot password
and then failed with ENCRYPTED because the raster port had no password seam.
This test imports a real R2/RC4 encrypted PDF, resolves it on a cache MISS via
a fresh Secret-G, and proves the rendition is produced and the token consumed.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from pathlib import Path
import time
import uuid

import pytest

from application.importing.referenced.errors import SourceImportError
from infrastructure.importing import PdfiumDocumentRaster
from infrastructure.resource_channel.source_read_refs import SourceReadGrantRegistry
from support import FakeSourceReadAccess, build_runtime, capture_facts

from tests.fea09.test_i005_encrypted_resolve import (
    _b64,
    _build_server,
    _write_secret,
    _wait_terminal,
)

PASSWORD = b"secret"
OP = "op-0000000000000101"


def _encrypted_pdf_bytes() -> bytes:
    from tests.import_formats.test_document_import import encrypted_pdf

    return encrypted_pdf()


def _import_encrypted_pdf(tmp_path, repo) -> str:
    path = tmp_path / "locked.pdf"
    path.write_bytes(_encrypted_pdf_bytes())
    access = FakeSourceReadAccess()
    access.add_file("g-pdf-000000000001", "pdf", path)
    runtime = build_runtime(repo, access)
    secrets = tmp_path / "host" / "source-secrets"
    secrets.mkdir(parents=True)
    ref = _write_secret(secrets / ("p" * 32 + ".bin"), PASSWORD)
    plan = runtime._planner.plan(
        chapter_id="c1", grants=["g-pdf-000000000001"], duplicate_policy="skip"
    )
    runtime.start(
        chapter_id="c1", plan_id=plan["plan_id"], plan_digest=plan["plan_digest"],
        grants=["g-pdf-000000000001"], duplicate_policy="skip",
        operation_id=OP, secret_ref=ref,
    )
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "completed"
    return repo.list_pages("c1")[0].page_id


def _pdf_grant_payload(path: Path, binding: dict, entry: dict, *,
                       token: str, secret_path: Path) -> dict:
    facts = capture_facts(path)
    now = time.time()
    payload = {
        "grant_id": "grant-" + uuid.uuid4().hex,
        "session_id": "session-pdf",
        "operation": "source-read",
        "scope_class": "user-source",
        "registry_id": "registry-pdf",
        "generation": 1,
        "expires_at": now + 120,
        "budget": {"max_bytes": 8 * 1024 * 1024,
                   "max_decode_bytes": 8 * 1024 * 1024, "max_entries": 100},
        "scope": {
            "source_id": binding["source_id"],
            "version": binding["accepted_source_version"],
            "rendition": {"decoder": "pdf", "scale": 1,
                          "params_digest": "0" * 64},
            "entries": [{
                "entry_key": binding["entry_id"],
                "entry_id": None,
                "locator": entry["locator"],
                "ordinal": int(entry["ordinal"]),
                "path": str(path),
                "facts": {"volume_serial": facts.volume_serial,
                          "file_id": facts.file_id,
                          "size": facts.size, "sha256": facts.sha256},
            }],
        },
        "secret_ref": {"token": token, "path": str(secret_path),
                       "expires_at": now + 60},
    }
    fields = {k: v for k, v in payload.items()
              if k not in ("signing_key", "signature")}
    fields["expires_at"] = f'{payload["expires_at"]:.6f}'
    key = b"p" * 32
    payload["signing_key"] = _b64(key)
    payload["signature"] = _b64(
        hmac.new(key, json.dumps(fields, sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=False).encode(),
                 hashlib.sha256).digest()
    )
    return payload


def test_encrypted_pdf_resolve_uses_secret_and_pdfium_password(
    tmp_path, repo, book_chapter
):
    page_id = _import_encrypted_pdf(tmp_path, repo)
    binding = repo.get_page_binding(page_id)
    assert binding is not None
    entries = repo.list_source_entries(binding["accepted_source_version"])
    entry = next(item for item in entries if item["entry_id"] == binding["entry_id"])
    path = next(tmp_path.glob("locked.pdf"))
    secrets = tmp_path / "host" / "source-secrets"
    token = "q" * 32
    secret_path = secrets / f"{token}.bin"
    _write_secret(secret_path, PASSWORD)

    registry = SourceReadGrantRegistry()
    grant = _pdf_grant_payload(path, binding, entry, token=token,
                               secret_path=secret_path)
    registry.register(grant)
    registry.bind_imported_entry(
        grant["grant_id"], binding["source_id"],
        binding["accepted_source_version"], binding["entry_id"],
    )
    server, cache, derived = _build_server(tmp_path, repo, registry,
                                           FakeSourceReadAccess())
    server._core.document_raster = PdfiumDocumentRaster()
    response = server.handle_resolve_page_resource({"page_id": page_id})
    assert response["resource_id"].startswith("page-rendition-v2-")
    assert not secret_path.exists(), "one-shot secret must be consumed"
    assert list(derived.rglob("*.png")), "PDF rendition must be published"
    # cache hit needs no new Secret-G (grant consumed, Auth only)
    second = server.handle_resolve_page_resource({"page_id": page_id})
    assert second["resource_id"] == response["resource_id"]


def test_encrypted_pdf_resolve_without_secret_is_required(
    tmp_path, repo, book_chapter
):
    page_id = _import_encrypted_pdf(tmp_path, repo)
    binding = repo.get_page_binding(page_id)
    entries = repo.list_source_entries(binding["accepted_source_version"])
    entry = next(item for item in entries if item["entry_id"] == binding["entry_id"])
    path = next(tmp_path.glob("locked.pdf"))
    registry = SourceReadGrantRegistry()
    payload = _pdf_grant_payload(path, binding, entry,
                                 token="z" * 32,
                                 secret_path=tmp_path / "missing.bin")
    payload.pop("secret_ref")
    fields = {k: v for k, v in payload.items()
              if k not in ("signing_key", "signature")}
    fields["expires_at"] = f'{payload["expires_at"]:.6f}'
    key = b"p" * 32
    payload["signing_key"] = _b64(key)
    payload["signature"] = _b64(
        hmac.new(key, json.dumps(fields, sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=False).encode(),
                 hashlib.sha256).digest()
    )
    registry.register(payload)
    registry.bind_imported_entry(
        payload["grant_id"], binding["source_id"],
        binding["accepted_source_version"], binding["entry_id"],
    )
    server, cache, derived = _build_server(tmp_path, repo, registry,
                                           FakeSourceReadAccess())
    server._core.document_raster = PdfiumDocumentRaster()
    with pytest.raises(SourceImportError) as caught:
        server.handle_resolve_page_resource({"page_id": page_id})
    assert caught.value.code == "SOURCE_PASSWORD_REQUIRED"
