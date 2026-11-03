"""FEA-09 AC-4: password short-lived references and encrypted sources.

Covers the C-16 §3 flow: plan never consumes passwords (encrypted preview is
structural), start reads the one-shot DPAPI secret (real CryptProtectData on
Windows), wrong/absent passwords are typed failures, retries succeed with a
fresh token, and the secret file is destroyed on every path. Password
literals must never surface in errors or receipts.
"""

from __future__ import annotations

import ctypes
import sys
import time
from ctypes import wintypes

import pytest

from support import (
    FakeSourceReadAccess,
    build_runtime,
    png_bytes,
    write_zip,
)
from tests.fea09.zip_fixtures import make_zipcrypto_zip
from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.secrets import MAGIC, read_secret

OP = "op-0000000000000001"
OP2 = "op-0000000000000002"
PASSWORD = b"correct horse battery staple"


def _wait_terminal(runtime, operation_id, timeout=10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        receipt = runtime.receipt(operation_id)
        if receipt["state"] in {"completed", "cancelled", "failed"}:
            return receipt
        time.sleep(0.01)
    return runtime.receipt(operation_id)


# ------------------------------------------------------------ DPAPI helpers
def _protect(plaintext: bytes) -> bytes:
    """CryptProtectData CurrentUser (test-side counterpart of the Host)."""
    if sys.platform != "win32":
        pytest.skip("DPAPI round-trip requires Windows")
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [
            ("cbData", wintypes.DWORD),
            ("pbData", ctypes.POINTER(ctypes.c_char)),
        ]

    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    crypt32.CryptProtectData.argtypes = [
        ctypes.POINTER(DATA_BLOB), ctypes.c_wchar_p, ctypes.c_void_p,
        ctypes.c_void_p, ctypes.c_void_p,
        wintypes.DWORD, ctypes.POINTER(DATA_BLOB),
    ]
    crypt32.CryptProtectData.restype = wintypes.BOOL
    kernel32.LocalFree.argtypes = [wintypes.HLOCAL]
    kernel32.LocalFree.restype = wintypes.HLOCAL
    src = ctypes.create_string_buffer(plaintext, len(plaintext))
    in_blob = DATA_BLOB()
    in_blob.cbData = len(plaintext)
    in_blob.pbData = ctypes.cast(src, ctypes.POINTER(ctypes.c_char))
    out_blob = DATA_BLOB()
    if not crypt32.CryptProtectData(
        ctypes.byref(in_blob), None, None, None, None, 0, ctypes.byref(out_blob)
    ):
        raise OSError("CryptProtectData failed")
    try:
        return ctypes.string_at(out_blob.pbData, out_blob.cbData)
    finally:
        kernel32.LocalFree(out_blob.pbData)


def _write_secret(path, plaintext: bytes) -> dict:
    path.write_bytes(MAGIC + _protect(plaintext))
    return {"token": "x" * 22, "path": str(path), "expires_at": 1e12}


# ----------------------------------------------------------------- secrets
def test_secret_roundtrip_and_file_destroyed(tmp_path):
    secret_path = tmp_path / "host" / "source-secrets" / "tok1.bin"
    secret_path.parent.mkdir(parents=True)
    ref = _write_secret(secret_path, PASSWORD)

    assert read_secret(ref) == PASSWORD
    assert not secret_path.exists()  # zero-filled + deleted after read


def test_secret_missing_file_required(tmp_path):
    ref = {
        "token": "x" * 22,
        "path": str(tmp_path / "gone.bin"),
        "expires_at": 1e12,
    }
    with pytest.raises(SourceImportError) as caught:
        read_secret(ref)
    assert caught.value.code == "SOURCE_PASSWORD_REQUIRED"


def test_secret_bad_payload_invalid_and_destroyed(tmp_path):
    secret_path = tmp_path / "bad.bin"
    secret_path.write_bytes(b"NOTMAGIC" + _protect(b"whatever"))
    ref = {"token": "x" * 22, "path": str(secret_path), "expires_at": 1e12}

    with pytest.raises(SourceImportError) as caught:
        read_secret(ref)
    assert caught.value.code == "SOURCE_PASSWORD_INVALID"
    assert not secret_path.exists()  # destroyed on the failure path too


def test_secret_malformed_ref_required(tmp_path):
    with pytest.raises(SourceImportError) as caught:
        read_secret({"token": "x" * 22})
    assert caught.value.code == "SOURCE_PASSWORD_REQUIRED"
    with pytest.raises(SourceImportError) as caught:
        read_secret({"path": "relative/path.bin"})
    assert caught.value.code == "SOURCE_PASSWORD_REQUIRED"


# ------------------------------------------------------ encrypted zip flow
def _locked_zip(tmp_path, name="locked.cbz"):
    payload_a = png_bytes(3, 3)
    payload_b = png_bytes(3, 3, (0, 255, 0))
    blob = make_zipcrypto_zip(
        [("001.png", payload_a), ("002.png", payload_b)],
        PASSWORD.decode(),
    )
    path = tmp_path / name
    path.write_bytes(blob)
    return path, payload_a, payload_b


def test_encrypted_plan_is_structural_only(tmp_path, repo, book_chapter):
    path, _a, _b = _locked_zip(tmp_path)
    access = FakeSourceReadAccess()
    access.add_file("g-cbz-0000000000001", "cbz", path)
    runtime = build_runtime(repo, access)

    plan = runtime._planner.plan(
        chapter_id="c1", grants=["g-cbz-0000000000001"], duplicate_policy="skip"
    )
    source = plan["sources"][0]
    assert source["status"] == "encrypted"
    assert source["will_import"] is None
    record = runtime._planner._plans[plan["plan_id"]]
    assert record.sources[0].container_digest  # container-level digest frozen
    for page in record.sources[0].pages:
        assert page["content_digest"] is None  # no plaintext digests pre-password


def test_encrypted_import_with_secret_succeeds(tmp_path, repo, book_chapter):
    path, payload_a, _b = _locked_zip(tmp_path)
    access = FakeSourceReadAccess()
    access.add_file("g-cbz-0000000000002", "cbz", path)
    runtime = build_runtime(repo, access)

    secret_path = tmp_path / "host" / "source-secrets" / "tok2.bin"
    secret_path.parent.mkdir(parents=True)
    ref = _write_secret(secret_path, PASSWORD)

    plan = runtime._planner.plan(
        chapter_id="c1", grants=["g-cbz-0000000000002"], duplicate_policy="skip"
    )
    runtime.start(
        chapter_id="c1", plan_id=plan["plan_id"], plan_digest=plan["plan_digest"],
        grants=["g-cbz-0000000000002"], duplicate_policy="skip",
        operation_id=OP, secret_ref=ref,
    )
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "completed"
    assert receipt["totals"]["imported_pages"] == 2
    pages = repo.list_pages("c1")
    assert len(pages) == 2
    import hashlib

    assert pages[0].source_hash == hashlib.sha256(payload_a).hexdigest()
    assert not secret_path.exists()  # consumed exactly once
    # the receipt never carries the password or its encodings
    import json

    blob = json.dumps(receipt)
    assert PASSWORD.decode() not in blob
    assert PASSWORD.hex() not in blob


def test_encrypted_import_without_secret_requires_password(
    tmp_path, repo, book_chapter
):
    path, _a, _b = _locked_zip(tmp_path)
    access = FakeSourceReadAccess()
    access.add_file("g-cbz-0000000000003", "cbz", path)
    runtime = build_runtime(repo, access)

    plan = runtime._planner.plan(
        chapter_id="c1", grants=["g-cbz-0000000000003"], duplicate_policy="skip"
    )
    runtime.start(
        chapter_id="c1", plan_id=plan["plan_id"], plan_digest=plan["plan_digest"],
        grants=["g-cbz-0000000000003"], duplicate_policy="skip", operation_id=OP,
    )
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "failed"
    item = receipt["items"][0]
    assert item["reason_code"] == "SOURCE_PASSWORD_REQUIRED"
    assert repo.list_pages("c1") == []


def test_encrypted_import_wrong_password_then_retry_succeeds(
    tmp_path, repo, book_chapter
):
    """错密失败 → 新 token 重试成功（C-16 §3 每次重试新文件）。"""
    path, _a, _b = _locked_zip(tmp_path)
    access = FakeSourceReadAccess()
    access.add_file("g-cbz-0000000000004", "cbz", path)
    runtime = build_runtime(repo, access)

    secrets_dir = tmp_path / "host" / "source-secrets"
    secrets_dir.mkdir(parents=True)
    bad = _write_secret(secrets_dir / "tok-bad.bin", b"wr0ng password")
    plan1 = runtime._planner.plan(
        chapter_id="c1", grants=["g-cbz-0000000000004"], duplicate_policy="skip"
    )
    runtime.start(
        chapter_id="c1", plan_id=plan1["plan_id"], plan_digest=plan1["plan_digest"],
        grants=["g-cbz-0000000000004"], duplicate_policy="skip",
        operation_id=OP, secret_ref=bad,
    )
    first = _wait_terminal(runtime, OP)
    assert first["state"] == "failed"
    assert first["items"][0]["reason_code"] == "SOURCE_PASSWORD_INVALID"

    # retry with a fresh token carrying the right password
    good = _write_secret(secrets_dir / "tok-good.bin", PASSWORD)
    plan2 = runtime._planner.plan(
        chapter_id="c1", grants=["g-cbz-0000000000004"], duplicate_policy="skip"
    )
    runtime.start(
        chapter_id="c1", plan_id=plan2["plan_id"], plan_digest=plan2["plan_digest"],
        grants=["g-cbz-0000000000004"], duplicate_policy="skip",
        operation_id=OP2, secret_ref=good,
    )
    second = _wait_terminal(runtime, OP2)
    assert second["state"] == "completed"
    assert second["totals"]["imported_pages"] == 2
    assert len(repo.list_pages("c1")) == 2


def test_password_failures_lock_after_three_attempts(tmp_path, repo, book_chapter):
    """连续失败 ≥3 次 → 该 source 失败并允许跳过（C-16 §3）。"""
    path, _a, _b = _locked_zip(tmp_path)
    access = FakeSourceReadAccess()
    access.add_file("g-cbz-0000000000005", "cbz", path)
    runtime = build_runtime(repo, access)
    secrets_dir = tmp_path / "host" / "source-secrets"
    secrets_dir.mkdir(parents=True)

    for attempt in range(3):
        bad = _write_secret(
            secrets_dir / f"tok-bad-{attempt}.bin", b"wr0ng password"
        )
        plan = runtime._planner.plan(
            chapter_id="c1", grants=["g-cbz-0000000000005"], duplicate_policy="skip"
        )
        runtime.start(
            chapter_id="c1", plan_id=plan["plan_id"],
            plan_digest=plan["plan_digest"],
            grants=["g-cbz-0000000000005"], duplicate_policy="skip",
            operation_id=f"op-00000000000000{attempt + 3:02d}", secret_ref=bad,
        )
        receipt = _wait_terminal(runtime, f"op-00000000000000{attempt + 3:02d}")
        assert receipt["items"][0]["reason_code"] == "SOURCE_PASSWORD_INVALID"

    good = _write_secret(secrets_dir / "tok-good2.bin", PASSWORD)
    plan = runtime._planner.plan(
        chapter_id="c1", grants=["g-cbz-0000000000005"], duplicate_policy="skip"
    )
    runtime.start(
        chapter_id="c1", plan_id=plan["plan_id"], plan_digest=plan["plan_digest"],
        grants=["g-cbz-0000000000005"], duplicate_policy="skip",
        operation_id="op-0000000000000101", secret_ref=good,
    )
    locked = _wait_terminal(runtime, "op-0000000000000101")
    assert locked["state"] == "failed"
    assert locked["items"][0]["reason_code"] == "SOURCE_PASSWORD_INVALID"
    assert repo.list_pages("c1") == []


def test_error_messages_never_leak_password(tmp_path):
    """SourceImportError 消息不携带密码及其可逆编码。"""
    path, _a, _b = _locked_zip(tmp_path)
    secret_path = tmp_path / "bad2.bin"
    # wrong-password secret for the real archive
    secret_path.write_bytes(MAGIC + _protect(b"definitely-wrong"))
    access = FakeSourceReadAccess()
    access.add_file("g-cbez-000000000006", "cbz", path)

    from support import build_planner
    from application.importing.referenced.scanner import scan_source
    from support import build_pdf_open

    try:
        scan_source(
            access.resolve("g-cbez-000000000006"),
            pdf_open=build_pdf_open(),
            password=b"definitely-wrong",
        )
    except SourceImportError as error:
        message = str(error)
        assert "definitely-wrong" not in message
        assert b"definitely-wrong".hex() not in message
        assert error.code == "SOURCE_PASSWORD_INVALID"
    else:
        raise AssertionError("wrong password must fail typed")
