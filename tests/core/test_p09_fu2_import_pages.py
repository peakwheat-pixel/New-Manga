from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
from pathlib import Path
import sys
import uuid

import pytest
from PIL import Image

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.importing.images.sorting import IMAGE_EXTENSIONS, natural_sort_key
from application.resource_channel.dto import (
    ALLOWED_SCOPE_CLASSES,
    TypedResourceChannelError,
)
from bootstrap.core_service import (
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    assemble_production_core,
)
from infrastructure.resource_channel.handle_resolver import HandleVerifiedFileReader
from infrastructure.resource_channel.import_source_refs import ImportSourceGrantRegistry
from infrastructure.resource_channel.scope import ScopeRoots
from tests.import_formats.test_document_import import encrypted_pdf, minimal_pdf

SESSION_ID = "p09-fu2-test-host-session"
SIGNING_KEY = bytes(range(32))
NOW = 1_800_000_000.0


def _png(width: int = 23, height: int = 17, color=(20, 80, 160, 255)) -> bytes:
    output = io.BytesIO()
    Image.new("RGBA", (width, height), color).save(output, format="PNG")
    return output.getvalue()


def _signed_fields(
    grant_id: str,
    session_id: str,
    source_path: Path,
    source_kind: str,
    scope_identity: list[int] | None,
    entries: list[dict],
    expires_at: float,
) -> dict:
    return {
        "grant_id": grant_id,
        "session_id": session_id,
        "scope_class": "user-source",
        "operation": "ImportPages",
        "access": "read-only",
        "source_path": str(source_path),
        "source_kind": source_kind,
        "scope_identity": scope_identity,
        "entries": entries,
        "expires_at": f"{expires_at:.6f}",
    }


def _signature(fields: dict, key: bytes = SIGNING_KEY) -> str:
    raw = json.dumps(
        fields, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return base64.urlsafe_b64encode(
        hmac.new(key, raw, hashlib.sha256).digest()
    ).decode().rstrip("=")


def _facts(path: Path) -> dict:
    reader = HandleVerifiedFileReader(path.parent, limit=sys.maxsize)
    facts = reader.capture_facts(path.name)
    return {
        "volume_serial": facts.volume_serial,
        "file_index": facts.file_index,
        "size": facts.size,
        "sha256": facts.sha256,
    }


def _register_source(
    server: CoreServiceServer,
    source_path: Path,
    *,
    source_kind: str = "file",
    selected_paths: list[Path] | None = None,
    facts_paths: dict[Path, Path] | None = None,
    expires_at: float = NOW + 120,
    session_id: str = SESSION_ID,
    scope_class: str = "user-source",
    operation: str = "ImportPages",
    access: str = "read-only",
) -> dict:
    source_path = source_path.absolute()
    if selected_paths is None:
        selected_paths = [source_path] if source_kind == "file" else []
    selected_paths = [path.absolute() for path in selected_paths]
    if source_kind == "directory":
        selected_paths.sort(key=lambda path: natural_sort_key(path.name))
        info = source_path.stat()
        scope_identity = [int(info.st_dev), int(info.st_ino)]
    else:
        scope_identity = None
    entries = [
        {
            "path": str(path),
            "facts": _facts((facts_paths or {}).get(path, path)),
        }
        for path in selected_paths
    ]
    grant_id = uuid.uuid4().hex
    fields = _signed_fields(
        grant_id, session_id, source_path, source_kind, scope_identity, entries,
        expires_at,
    )
    signature = _signature(fields)
    server._register_import_source({
        "grant_id": grant_id,
        "session_id": session_id,
        "scope_class": scope_class,
        "operation": operation,
        "access": access,
        "source_path": str(source_path),
        "source_kind": source_kind,
        "scope_identity": scope_identity,
        "entries": entries,
        "expires_at": expires_at,
        "signing_key": base64.urlsafe_b64encode(SIGNING_KEY).decode().rstrip("="),
        "signature": signature,
    })
    return {"grant_id": grant_id, "host_signature": signature}


def _core(tmp_path: Path, *, cancelled=None):
    core = assemble_production_core(tmp_path / "data")
    with core.conn:
        core.conn.execute(
            "INSERT INTO books (book_id,title,author,description,created_at,updated_at)"
            " VALUES ('book','測試 Manga','Author','',?,?)",
            ("2026-10-16T00:00:00+00:00", "2026-10-16T00:00:00+00:00"),
        )
        core.conn.execute(
            "INSERT INTO chapters (chapter_id,book_id,title,chapter_number,sort_order,"
            "chapter_type,reading_direction,created_at,updated_at)"
            " VALUES ('chapter','book','第 1 話','1',0,'paged','rtl',?,?)",
            ("2026-10-16T00:00:00+00:00", "2026-10-16T00:00:00+00:00"),
        )
    core.import_source_refs = ImportSourceGrantRegistry(clock=lambda: NOW)
    server = CoreServiceServer(
        core, stdin=io.StringIO(), stdout=io.StringIO(),
        import_cancelled=cancelled,
    )
    return core, server


def _request(server: CoreServiceServer, payload: dict) -> dict:
    raw = json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": uuid.uuid4().hex,
        "command": "ImportPages",
        "payload": payload,
    }, ensure_ascii=False)
    return server.dispatch_request(raw)[0]


@pytest.mark.parametrize(
    "core_now,expiry_seconds,expected_error",
    [
        pytest.param(NOW + 0.1, 299.0, None, id="inside-window"),
        pytest.param(NOW, 299.0, None, id="clock-equals-host-build"),
        pytest.param(NOW - 0.25, 299.0, None, id="clock-slightly-before-host-build"),
        pytest.param(NOW + 299.0, 299.0, "REF_EXPIRED", id="actually-expired"),
        pytest.param(NOW, 300.001, "REF_EXPIRED", id="actually-over-300-second-window"),
    ],
)
def test_import_grant_registration_ttl_boundary(
    tmp_path, core_now: float, expiry_seconds: float, expected_error: str | None,
):
    core, server = _core(tmp_path)
    source = tmp_path / "source.png"
    source.write_bytes(_png())
    core.import_source_refs._clock = lambda: core_now
    try:
        if expected_error is None:
            ref = _register_source(server, source, expires_at=NOW + expiry_seconds)
            assert ref["grant_id"]
            assert ref["host_signature"]
        else:
            with pytest.raises(TypedResourceChannelError) as error:
                _register_source(server, source, expires_at=NOW + expiry_seconds)
            assert error.value.code == expected_error
    finally:
        server.close()
        core.conn.close()


def _file_snapshot(core) -> dict[str, str]:
    root = core.storage.root
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*") if path.is_file()
    }


def test_stdio_import_pages_runtime_response_and_import_report(tmp_path, capsys):
    core, server = _core(tmp_path)
    source = tmp_path / "選択した 🇯🇵" / "한국어 (第 １ 頁).png"
    source.parent.mkdir()
    source_bytes = _png(31, 19)
    source.write_bytes(source_bytes)
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    ref = _register_source(server, source)
    request = {
        "chapter_id": "chapter",
        "sources": [ref],
    }
    raw = json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": "stdio-importpages-proof",
        "command": "ImportPages",
        "payload": request,
    }, ensure_ascii=False)
    server._stdin = io.StringIO(raw + "\n")
    server._stdout = io.StringIO()
    try:
        exit_code = server.serve_forever()
        response_line = server._stdout.getvalue().strip()
        response = json.loads(response_line)
        print("protocol=2.3")
        print("command=ImportPages")
        print("request_payload=" + json.dumps({
            "chapter_id": "chapter",
            "sources": [{"grant_id": ref["grant_id"], "host_signature": "<test-signature-redacted>"}],
        }, ensure_ascii=False))
        print("core_stdout=" + response_line)
        print(f"serve_exit_code={exit_code}")
        assert exit_code == 0
        assert response["error"] is None
        assert response["version"] == {"major": 2, "minor": 3}
        report = response["result"]
        assert report["duplicate_policy"] == "skip"
        assert report["cancelled"] is False
        file_result = report["sources"][0]["files"][0]
        page_result = file_result["pages"][0]
        assert file_result["filename"] == source.name
        assert file_result["source_sha256"] == source_hash
        assert file_result["outcome"] == "imported"
        assert page_result == {
            "page_index": 1,
            "outcome": "imported",
            "page_id": page_result["page_id"],
            "source_order": 1,
            "sort_order": 1,
            "sha256": source_hash,
            "width": 31,
            "height": 19,
            "duplicate": False,
            "error": None,
            "side_effects": "page_committed",
        }
        page = core.repository.get_page(page_result["page_id"])
        assert page is not None
        managed = Path(core.storage.absolute_path(page.managed_original_ref))
        assert managed.read_bytes() == source_bytes
        assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    finally:
        server.close()
        core.conn.close()
    captured = capsys.readouterr().out
    assert "UNKNOWN_COMMAND" not in captured
    print(captured, end="")


@pytest.mark.parametrize(
    "case,expected",
    [
        ("malformed", "REF_MALFORMED"),
        ("signature_invalid", "REF_SIGNATURE_INVALID"),
        ("expired", "REF_EXPIRED"),
        ("unknown_id", "REF_UNKNOWN_ID"),
        ("revoked", "REF_REVOKED"),
        ("already_consumed", "REF_ALREADY_CONSUMED"),
        ("host_session", "REF_SCOPE_DENIED"),
        ("not_found", "REF_NOT_FOUND"),
        ("reparse", "REF_REPARSE_POINT"),
        ("identity_changed", "FILE_IDENTITY_CHANGED"),
        ("size_changed", "FILE_SIZE_CHANGED"),
        ("digest_changed", "CONTENT_DIGEST_MISMATCH"),
    ],
)
def test_import_source_reference_rejections_have_zero_side_effects(
    tmp_path, case: str, expected: str
):
    core, server = _core(tmp_path)
    source = tmp_path / "source.png"
    source_bytes = _png()
    source.write_bytes(source_bytes)
    registry = core.import_source_refs
    protected = None
    if case == "malformed":
        ref = {"grant_id": "short", "host_signature": "bad"}
    elif case == "unknown_id":
        ref = {"grant_id": uuid.uuid4().hex, "host_signature": "A" * 43}
    else:
        if case == "expired":
            ref = _register_source(server, source, expires_at=NOW + 1)
            registry._clock = lambda: NOW + 1
        elif case == "reparse":
            target = tmp_path / "protected.png"
            target.write_bytes(source_bytes)
            protected = hashlib.sha256(target.read_bytes()).hexdigest()
            try:
                source.unlink()
                source.symlink_to(target)
            except OSError as error:
                pytest.skip(f"symlink creation unavailable: {error}")
            ref = _register_source(server, source, facts_paths={source.absolute(): target})
        else:
            ref = _register_source(server, source)
        if case == "signature_invalid":
            last = ref["host_signature"][-1]
            ref["host_signature"] = ref["host_signature"][:-1] + ("A" if last != "A" else "B")
        elif case == "revoked":
            registry.revoke(ref["grant_id"])
        elif case == "host_session":
            registry._session_id = "other-host-session"
        elif case == "not_found":
            source.unlink()
        elif case == "identity_changed":
            source.unlink()
            source.write_bytes(source_bytes)
        elif case == "size_changed":
            source.write_bytes(source_bytes + b"changed-size")
        elif case == "digest_changed":
            changed = bytearray(source_bytes)
            changed[-8] ^= 1
            source.write_bytes(changed)
        elif case == "already_consumed":
            accepted = _request(server, {"chapter_id": "chapter", "sources": [ref]})
            assert accepted["error"] is None
    source_hash_before_request = (
        hashlib.sha256(source.read_bytes()).hexdigest()
        if source.exists() and not source.is_symlink() else None
    )
    before_pages = list(core.repository.list_pages("chapter"))
    before_files = _file_snapshot(core)
    try:
        response = _request(server, {
            "chapter_id": "chapter",
            "sources": [ref],
        })
        assert response["result"] is None
        assert response["error"]["code"] == expected
        assert response["error"]["category"] == {
            "REF_MALFORMED": "validation",
            "REF_SIGNATURE_INVALID": "validation",
            "REF_EXPIRED": "conflict",
            "REF_UNKNOWN_ID": "not_found",
            "REF_REVOKED": "conflict",
            "REF_ALREADY_CONSUMED": "conflict",
            "REF_SCOPE_DENIED": "validation",
            "REF_NOT_FOUND": "not_found",
            "REF_REPARSE_POINT": "validation",
            "FILE_IDENTITY_CHANGED": "conflict",
            "FILE_SIZE_CHANGED": "conflict",
            "CONTENT_DIGEST_MISMATCH": "conflict",
        }[expected]
        error_text = json.dumps(response["error"])
        assert str(source) not in error_text
        assert ref.get("host_signature", "") not in error_text
        assert list(core.repository.list_pages("chapter")) == before_pages
        assert _file_snapshot(core) == before_files
        if source_hash_before_request is not None:
            assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash_before_request
        if protected is not None:
            assert hashlib.sha256((tmp_path / "protected.png").read_bytes()).hexdigest() == protected
    finally:
        server.close()
        core.conn.close()


def test_invalid_second_reference_prevents_first_source_import(tmp_path):
    core, server = _core(tmp_path)
    first = tmp_path / "first.png"
    first.write_bytes(_png())
    first_hash = hashlib.sha256(first.read_bytes()).hexdigest()
    ref = _register_source(server, first)
    try:
        response = _request(server, {
            "chapter_id": "chapter",
            "sources": [ref, {"grant_id": "unknown", "host_signature": "A" * 43}],
        })
        assert response["error"]["code"] == "REF_MALFORMED"
        assert response["result"] is None
        assert core.repository.list_pages("chapter") == []
        assert _file_snapshot(core) == {}
        assert hashlib.sha256(first.read_bytes()).hexdigest() == first_hash
    finally:
        server.close()
        core.conn.close()


def test_request_path_fallback_is_rejected_as_malformed_reference(tmp_path):
    core, server = _core(tmp_path)
    source = tmp_path / "path-must-not-authorize.png"
    source_bytes = _png()
    source.write_bytes(source_bytes)
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    try:
        response = _request(server, {
            "chapter_id": "chapter",
            "sources": [{
                "grant_id": uuid.uuid4().hex,
                "host_signature": "A" * 43,
                "path": str(source),
            }],
        })
        assert response["error"]["code"] == "REF_MALFORMED"
        assert str(source) not in json.dumps(response["error"])
        assert core.repository.list_pages("chapter") == []
        assert _file_snapshot(core) == {}
        assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    finally:
        server.close()
        core.conn.close()


def test_directory_grant_rejects_an_outside_child_before_import(tmp_path):
    core, server = _core(tmp_path)
    folder = tmp_path / "selected"
    folder.mkdir()
    outside = tmp_path / "outside.png"
    outside.write_bytes(_png())
    outside_hash = hashlib.sha256(outside.read_bytes()).hexdigest()
    try:
        with pytest.raises(TypedResourceChannelError) as caught:
            _register_source(
                server, folder, source_kind="directory", selected_paths=[outside]
            )
        assert caught.value.code == "REF_OUT_OF_SCOPE"
        assert core.repository.list_pages("chapter") == []
        assert _file_snapshot(core) == {}
        assert hashlib.sha256(outside.read_bytes()).hexdigest() == outside_hash
    finally:
        server.close()
        core.conn.close()


def test_user_source_is_core_only_and_read_only(tmp_path):
    assert "user-source" not in ALLOWED_SCOPE_CLASSES
    with pytest.raises(TypedResourceChannelError) as caught:
        ScopeRoots(tmp_path / "derived", tmp_path / "managed").root_for("user-source")
    assert caught.value.code == "REF_SCOPE_DENIED"
    core, server = _core(tmp_path)
    source = tmp_path / "source.png"
    source.write_bytes(_png())
    try:
        with pytest.raises(TypedResourceChannelError) as caught:
            _register_source(server, source, access="write")
        assert caught.value.code == "REF_SCOPE_DENIED"
        assert core.repository.list_pages("chapter") == []
        assert _file_snapshot(core) == {}
    finally:
        server.close()
        core.conn.close()


def test_unicode_folder_direct_children_natural_order_and_hashes(tmp_path):
    core, server = _core(tmp_path)
    folder = tmp_path / "漫画 日本語 🇯🇵"
    folder.mkdir()
    first = folder / "第 2 頁.png"
    second = folder / "第 10 頁.png"
    first.write_bytes(_png(20, 30, (1, 2, 3, 255)))
    second.write_bytes(_png(40, 50, (4, 5, 6, 255)))
    (folder / "notes.txt").write_text("ignored", encoding="utf-8")
    nested = folder / "subfolder"
    nested.mkdir()
    (nested / "nested.png").write_bytes(_png())
    selected = sorted(
        (path for path in folder.iterdir()
         if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS),
        key=lambda path: natural_sort_key(path.name),
    )
    ref = _register_source(
        server, folder, source_kind="directory", selected_paths=selected
    )
    try:
        response = _request(server, {"chapter_id": "chapter", "sources": [ref]})
        assert response["error"] is None
        source_result = response["result"]["sources"][0]
        assert source_result["source_name"] == folder.name
        files = source_result["files"]
        assert [item["filename"] for item in files] == [path.name for path in selected]
        assert [item["pages"][0]["source_order"] for item in files] == [1, 2]
        assert [item["pages"][0]["width"] for item in files] == [20, 40]
        assert all(item["source_sha256"] for item in files)
        assert all("path" not in json.dumps(item).lower() for item in files)
        assert len(core.repository.list_pages("chapter")) == 2
    finally:
        server.close()
        core.conn.close()


def test_duplicate_skip_and_import_as_new_report_dimensions_and_side_effects(tmp_path):
    core, server = _core(tmp_path)
    source = tmp_path / "duplicate.png"
    source_bytes = _png(29, 37)
    source.write_bytes(source_bytes)
    try:
        first = _request(server, {
            "chapter_id": "chapter",
            "sources": [_register_source(server, source)],
        })
        assert first["error"] is None
        before_files = _file_snapshot(core)
        skipped = _request(server, {
            "chapter_id": "chapter",
            "sources": [_register_source(server, source)],
        })
        skipped_file = skipped["result"]["sources"][0]["files"][0]
        skipped_page = skipped_file["pages"][0]
        assert skipped_file["outcome"] == "skipped"
        assert skipped_page["outcome"] == "skipped_duplicate"
        assert skipped_page["sha256"] == hashlib.sha256(source_bytes).hexdigest()
        assert (skipped_page["width"], skipped_page["height"]) == (29, 37)
        assert skipped_page["duplicate"] is True
        assert skipped_page["side_effects"] == "none"
        assert _file_snapshot(core) == before_files
        assert len(core.repository.list_pages("chapter")) == 1
        imported_new = _request(server, {
            "chapter_id": "chapter",
            "sources": [_register_source(server, source)],
            "duplicate_policy": "import_as_new",
        })
        new_page = imported_new["result"]["sources"][0]["files"][0]["pages"][0]
        assert new_page["outcome"] == "imported"
        assert new_page["duplicate"] is True
        assert new_page["page_id"] != first["result"]["sources"][0]["files"][0]["pages"][0]["page_id"]
        assert len(core.repository.list_pages("chapter")) == 2
    finally:
        server.close()
        core.conn.close()


def test_pdf_import_report_has_source_hash_page_hashes_and_real_page_order(tmp_path):
    core, server = _core(tmp_path)
    source = tmp_path / "話 1.pdf"
    data = minimal_pdf(3)
    source.write_bytes(data)
    try:
        response = _request(server, {
            "chapter_id": "chapter",
            "sources": [_register_source(server, source)],
        })
        assert response["error"] is None
        file_result = response["result"]["sources"][0]["files"][0]
        assert file_result["outcome"] == "imported"
        assert file_result["source_sha256"] == hashlib.sha256(data).hexdigest()
        pages = file_result["pages"]
        assert [page["page_index"] for page in pages] == [1, 2, 3]
        assert [page["source_order"] for page in pages] == [1, 2, 3]
        assert all((page["width"], page["height"]) == (1224, 1584) for page in pages)
        assert all(page["sha256"] != file_result["source_sha256"] for page in pages)
        for page_result in pages:
            page = core.repository.get_page(page_result["page_id"])
            managed = Path(core.storage.absolute_path(page.managed_original_ref))
            assert hashlib.sha256(managed.read_bytes()).hexdigest() == page_result["sha256"]
        assert hashlib.sha256(source.read_bytes()).hexdigest() == hashlib.sha256(data).hexdigest()
    finally:
        server.close()
        core.conn.close()


def test_pdf_duplicate_report_and_import_as_new(tmp_path):
    core, server = _core(tmp_path)
    source = tmp_path / "duplicate.pdf"
    source.write_bytes(minimal_pdf(2))
    try:
        first = _request(server, {
            "chapter_id": "chapter", "sources": [_register_source(server, source)],
        })
        before_files = _file_snapshot(core)
        again = _request(server, {
            "chapter_id": "chapter", "sources": [_register_source(server, source)],
        })
        file_result = again["result"]["sources"][0]["files"][0]
        assert file_result["outcome"] == "skipped"
        assert [page["outcome"] for page in file_result["pages"]] == [
            "skipped_duplicate", "skipped_duplicate"
        ]
        assert all(page["duplicate"] for page in file_result["pages"])
        assert _file_snapshot(core) == before_files
        newer = _request(server, {
            "chapter_id": "chapter",
            "sources": [_register_source(server, source)],
            "duplicate_policy": "import_as_new",
        })
        new_pages = newer["result"]["sources"][0]["files"][0]["pages"]
        assert [page["outcome"] for page in new_pages] == ["imported", "imported"]
        assert all(page["duplicate"] for page in new_pages)
        assert len(core.repository.list_pages("chapter")) == 4
        assert all(
            new["page_id"] != old["page_id"]
            for new, old in zip(new_pages, first["result"]["sources"][0]["files"][0]["pages"])
        )
    finally:
        server.close()
        core.conn.close()


def test_pdf_interruption_reports_committed_page_and_pending_remainder(tmp_path):
    calls = [0]

    def cancel_during_import():
        calls[0] += 1
        return calls[0] >= 6

    core, server = _core(tmp_path, cancelled=cancel_during_import)
    source = tmp_path / "interrupted.pdf"
    data = minimal_pdf(2)
    source.write_bytes(data)
    try:
        response = _request(server, {
            "chapter_id": "chapter", "sources": [_register_source(server, source)],
        })
        report = response["result"]
        file_result = report["sources"][0]["files"][0]
        assert report["cancelled"] is True
        assert file_result["outcome"] == "partial"
        assert [page["outcome"] for page in file_result["pages"]] == [
            "imported", "pending"
        ]
        assert file_result["pages"][0]["side_effects"] == "page_committed"
        assert file_result["pages"][1]["side_effects"] == "none"
        assert len(core.repository.list_pages("chapter")) == 1
        assert hashlib.sha256(source.read_bytes()).hexdigest() == hashlib.sha256(data).hexdigest()
    finally:
        server.close()
        core.conn.close()


@pytest.mark.parametrize(
    "data,expected",
    [
        (b"not an image", "INVALID_IMAGE"),
        (b"%PDF-1.4 damaged", "INVALID_DOCUMENT"),
    ],
)
def test_corrupt_sources_are_rejected_without_managed_or_library_writes(
    tmp_path, data: bytes, expected: str
):
    core, server = _core(tmp_path)
    source = tmp_path / ("damaged.pdf" if data.startswith(b"%PDF") else "damaged.png")
    source.write_bytes(data)
    before = hashlib.sha256(data).hexdigest()
    try:
        response = _request(server, {
            "chapter_id": "chapter", "sources": [_register_source(server, source)],
        })
        file_result = response["result"]["sources"][0]["files"][0]
        assert file_result["outcome"] == "rejected"
        assert file_result["error"]["code"] == expected
        assert file_result["side_effects"] == "none"
        assert core.repository.list_pages("chapter") == []
        assert _file_snapshot(core) == {}
        assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    finally:
        server.close()
        core.conn.close()


def test_encrypted_pdf_is_rejected_before_any_managed_copy_or_page(tmp_path):
    core, server = _core(tmp_path)
    source = tmp_path / "encrypted.pdf"
    data = encrypted_pdf()
    source.write_bytes(data)
    before = hashlib.sha256(data).hexdigest()
    try:
        response = _request(server, {
            "chapter_id": "chapter", "sources": [_register_source(server, source)],
        })
        file_result = response["result"]["sources"][0]["files"][0]
        assert file_result["error"]["code"] == "ENCRYPTED"
        assert file_result["side_effects"] == "none"
        assert core.repository.list_pages("chapter") == []
        assert _file_snapshot(core) == {}
        assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    finally:
        server.close()
        core.conn.close()
