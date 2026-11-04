"""C-16 v1.1 (R1-I005) end-to-end: encrypted referenced resolve via fresh grant.

Cache MISS consumes exactly one Host-written DPAPI secret; cache HIT needs no
new secret grant (Auth still required); a MISS without a Secret-G is a typed
SOURCE_PASSWORD_REQUIRED and never leaks the password.
"""

from __future__ import annotations

import base64
import ctypes
from ctypes import wintypes
import hashlib
import hmac
import json
from pathlib import Path
import sys
import time
import uuid

import pytest

from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.secrets import MAGIC
from infrastructure.resource_channel.source_read_refs import SourceReadGrantRegistry
from support import FakeSourceReadAccess, build_runtime, capture_facts, png_bytes
from tests.fea09.zip_fixtures import make_zipcrypto_zip

PASSWORD = b"resolve secret pass"
OP = "op-0000000000000099"


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _protect(plaintext: bytes) -> bytes:
    if sys.platform != "win32":
        pytest.skip("DPAPI round-trip requires Windows")

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD),
                    ("pbData", ctypes.POINTER(ctypes.c_char))]

    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    crypt32.CryptProtectData.argtypes = [
        ctypes.POINTER(DATA_BLOB), ctypes.c_wchar_p, ctypes.c_void_p,
        ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD,
        ctypes.POINTER(DATA_BLOB),
    ]
    crypt32.CryptProtectData.restype = wintypes.BOOL
    kernel32.LocalFree.argtypes = [wintypes.HLOCAL]
    buffer = ctypes.create_string_buffer(plaintext, len(plaintext))
    in_blob = DATA_BLOB(len(plaintext),
                        ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char)))
    out = DATA_BLOB()
    if not crypt32.CryptProtectData(
        ctypes.byref(in_blob), None, None, None, None, 0x1, ctypes.byref(out)
    ):
        raise OSError("CryptProtectData failed")
    try:
        return ctypes.string_at(out.pbData, out.cbData)
    finally:
        kernel32.LocalFree(out.pbData)


def _write_secret(path: Path, password: bytes) -> dict:
    path.write_bytes(MAGIC + _protect(password))
    return {"token": path.stem, "path": str(path),
            "expires_at": time.time() + 60}


def _wait_terminal(runtime, operation_id, timeout=10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        receipt = runtime.receipt(operation_id)
        if receipt["state"] in {"completed", "cancelled", "failed"}:
            return receipt
        time.sleep(0.01)
    return runtime.receipt(operation_id)


def _encrypted_zip(tmp_path: Path) -> Path:
    blob = make_zipcrypto_zip(
        [("001.png", png_bytes(3, 3)),
         ("002.png", png_bytes(3, 3, (0, 255, 0)))],
        PASSWORD.decode(),
    )
    path = tmp_path / "locked.cbz"
    path.write_bytes(blob)
    return path


def _import_encrypted(tmp_path, repo) -> str:
    path = _encrypted_zip(tmp_path)
    access = FakeSourceReadAccess()
    access.add_file("g-enc-000000000001", "cbz", path)
    runtime = build_runtime(repo, access)
    secret_dir = tmp_path / "host" / "source-secrets"
    secret_dir.mkdir(parents=True)
    ref = _write_secret(secret_dir / ("i" * 32 + ".bin"), PASSWORD)
    plan = runtime._planner.plan(
        chapter_id="c1", grants=["g-enc-000000000001"], duplicate_policy="skip"
    )
    runtime.start(
        chapter_id="c1", plan_id=plan["plan_id"], plan_digest=plan["plan_digest"],
        grants=["g-enc-000000000001"], duplicate_policy="skip",
        operation_id=OP, secret_ref=ref,
    )
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "completed"
    return repo.list_pages("c1")[0].page_id


def _grant_payload(path: Path, binding: dict, *, registry: SourceReadGrantRegistry,
                   token: str, secret_path: Path) -> dict:
    facts = capture_facts(path)
    now = time.time()
    payload = {
        "grant_id": "grant-" + uuid.uuid4().hex,
        "session_id": "session-1",
        "operation": "source-read",
        "scope_class": "user-source",
        "registry_id": "registry-1",
        "generation": 1,
        "expires_at": now + 120,
        "budget": {"max_bytes": 8 * 1024 * 1024,
                   "max_decode_bytes": 8 * 1024 * 1024, "max_entries": 100},
        "scope": {
            "source_id": binding["source_id"],
            "version": binding["accepted_source_version"],
            "rendition": {"decoder": "cbz", "scale": 1,
                          "params_digest": "0" * 64},
            "entries": [{
                "entry_key": binding["entry_id"],
                "entry_id": None,
                "locator": binding["entry_id"],
                "ordinal": 0,
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
    key = b"z" * 32
    payload["signing_key"] = _b64(key)
    payload["signature"] = _b64(
        hmac.new(key, json.dumps(fields, sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=False).encode(),
                 hashlib.sha256).digest()
    )
    return payload


def _build_server(tmp_path: Path, repo, registry, access):
    from bootstrap.core_service import CoreServiceServer
    from infrastructure.resource_channel.catalog_store import (
        ResourceCatalogStore,
        initialize_namespace,
    )
    from infrastructure.resource_channel.render_preview import RenderPreviewPublisher
    from infrastructure.resource_channel.rendition_cache import RenditionCache
    from types import SimpleNamespace

    catalog_db = tmp_path / "catalog" / "catalog.sqlite"
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    derived = tmp_path / "derived"
    derived.mkdir(parents=True, exist_ok=True)
    initialize_namespace(catalog_db, derived)
    publisher = RenderPreviewPublisher(derived, ResourceCatalogStore(catalog_db))
    cache = RenditionCache(data_root=tmp_path, derived_root=derived,
                           connection=repo._conn)
    server = object.__new__(CoreServiceServer)
    server._core = SimpleNamespace(
        repository=repo,
        source_read_refs=registry,
        rendition_cache=cache,
        image_decoder=None,
        document_raster=None,
        managed_root_trust=None,
    )
    server._render_previews = publisher
    return server, cache, derived


def test_encrypted_resolve_consumes_one_secret_and_cache_hit_needs_none(
    tmp_path, repo, book_chapter
):
    page_id = _import_encrypted(tmp_path, repo)
    binding = repo.get_page_binding(page_id)
    assert binding is not None
    # the encrypted container path: locate it from source_locations is internal;
    # rebuild it from the same fixture directory (only one cbz exists).
    path = next(tmp_path.glob("locked.cbz"))
    secret_dir = tmp_path / "host" / "source-secrets"
    token = "r" * 32
    secret_path = secret_dir / f"{token}.bin"
    ref = _write_secret(secret_path, PASSWORD)

    registry = SourceReadGrantRegistry()
    grant = _grant_payload(path, binding, registry=registry,
                           token=token, secret_path=secret_path)
    registry.register(grant)
    registry.bind_imported_entry(
        grant["grant_id"], binding["source_id"],
        binding["accepted_source_version"], binding["entry_id"],
    )
    access = FakeSourceReadAccess()
    server, cache, derived = _build_server(tmp_path, repo, registry, access)

    response = server.handle_resolve_page_resource({"page_id": page_id})
    assert response["resource_id"].startswith("page-rendition-v2-")
    assert not secret_path.exists()  # one-shot consumed
    published = list(derived.glob("renditions/*"))
    assert published or list(derived.rglob("*.png"))
    # cache hit: no new Secret-G needed (the grant is already consumed).
    second = server.handle_resolve_page_resource({"page_id": page_id})
    assert second["resource_id"] == response["resource_id"]
    assert PASSWORD.decode() not in json.dumps(second)
    assert PASSWORD.hex() not in json.dumps(second)


def test_encrypted_resolve_cache_miss_without_secret_grant_is_required(
    tmp_path, repo, book_chapter
):
    page_id = _import_encrypted(tmp_path, repo)
    binding = repo.get_page_binding(page_id)
    path = next(tmp_path.glob("locked.cbz"))
    registry = SourceReadGrantRegistry()
    # Auth-only grant: no secret_ref => encrypted cache miss must be typed
    # SOURCE_PASSWORD_REQUIRED, never a plain-text decode attempt.
    facts = capture_facts(path)
    now = time.time()
    payload = {
        "grant_id": "grant-" + uuid.uuid4().hex, "session_id": "s", "operation":
        "source-read", "scope_class": "user-source", "registry_id": "registry-1",
        "generation": 1, "expires_at": now + 120,
        "budget": {"max_bytes": 1024 * 1024, "max_decode_bytes": 1024 * 1024,
                   "max_entries": 10},
        "scope": {
            "source_id": binding["source_id"],
            "version": binding["accepted_source_version"],
            "rendition": {"decoder": "cbz", "scale": 1, "params_digest": "0" * 64},
            "entries": [{
                "entry_key": binding["entry_id"], "entry_id": None,
                "locator": binding["entry_id"], "ordinal": 0, "path": str(path),
                "facts": {"volume_serial": facts.volume_serial,
                          "file_id": facts.file_id, "size": facts.size,
                          "sha256": facts.sha256},
            }],
        },
    }
    fields = {k: v for k, v in payload.items()
              if k not in ("signing_key", "signature")}
    fields["expires_at"] = f'{payload["expires_at"]:.6f}'
    key = b"z" * 32
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
    with pytest.raises(SourceImportError) as caught:
        server.handle_resolve_page_resource({"page_id": page_id})
    assert caught.value.code == "SOURCE_PASSWORD_REQUIRED"
