"""C-16 v1.1 (R1-I005): resolve-side Secret-G claim + fresh-grant semantics.

Component tests (no Host IPC): a fresh grant carrying ``secret_ref`` is the
only way a cache-miss encrypted referenced resolve can obtain the password.
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
import uuid

import pytest

from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.secrets import MAGIC
from infrastructure.resource_channel.source_read_refs import SourceReadGrantRegistry

PASSWORD = b"correct horse battery staple"
TOKEN = "t" * 32


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _protect(plaintext: bytes) -> bytes:
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
    buffer = ctypes.create_string_buffer(plaintext, len(plaintext))
    in_blob = DATA_BLOB(len(plaintext), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char)))
    out = DATA_BLOB()
    if not crypt32.CryptProtectData(
        ctypes.byref(in_blob), None, None, None, None, 0x1, ctypes.byref(out)
    ):
        raise OSError("CryptProtectData failed")
    try:
        return ctypes.string_at(out.pbData, out.cbData)
    finally:
        kernel32.LocalFree(out.pbData)


class _Env:
    def __init__(self, tmp_path: Path, now: float = 1000.0) -> None:
        self.now = now
        self.registry = SourceReadGrantRegistry(clock=lambda: self.now)
        self.source = tmp_path / "movie.cbz"
        self.source.write_bytes(b"encrypted archive bytes")
        self.secret_dir = tmp_path / "host" / "source-secrets"
        self.secret_dir.mkdir(parents=True)
        self.token = TOKEN
        self.secret_path = self.secret_dir / f"{TOKEN}.bin"
        self.secret_path.write_bytes(MAGIC + _protect(PASSWORD))

    def payload(self, *, with_secret: bool = True, entry_key: str = "entry-1",
                expires_in: float = 100.0) -> dict:
        info = self.source.stat()
        payload = dict(
            grant_id="grant-" + uuid.uuid4().hex,
            session_id="session",
            operation="source-read",
            scope_class="user-source",
            registry_id="registry",
            generation=1,
            expires_at=self.now + 100,
            budget=dict(max_bytes=1024, max_decode_bytes=1024, max_entries=10),
            scope=dict(
                source_id="source-1",
                version="version-1",
                rendition=dict(decoder="cbz", scale=1, params_digest="0" * 64),
                entries=[dict(
                    entry_key=entry_key,
                    entry_id=None,
                    locator=self.source.name,
                    ordinal=0,
                    path=str(self.source),
                    facts=dict(
                        volume_serial=info.st_dev % (2**53),
                        file_id=info.st_ino % (2**53),
                        size=info.st_size,
                        sha256=hashlib.sha256(self.source.read_bytes()).hexdigest(),
                    ),
                )],
            ),
        )
        if with_secret:
            payload["secret_ref"] = {
                "token": self.token,
                "path": str(self.secret_path),
                "expires_at": min(self.now + expires_in, self.now + 100),
            }
        fields = {k: v for k, v in payload.items()
                  if k not in ("signing_key", "signature")}
        fields["expires_at"] = f'{payload["expires_at"]:.6f}'
        key = b"x" * 32
        payload["signing_key"] = _b64(key)
        payload["signature"] = _b64(
            hmac.new(key, json.dumps(fields, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode(),
                     hashlib.sha256).digest()
        )
        return payload

    def register(self, **kwargs) -> dict:
        payload = self.payload(**kwargs)
        self.registry.register(payload)
        return payload


def _claim(env: _Env, entry_key: str = "entry-1"):
    return env.registry.claim_secret_for_binding(
        "source-1", "version-1", entry_key
    )


def test_claim_reads_dpapi_secret_and_deletes_file(tmp_path):
    env = _Env(tmp_path)
    env.register()
    assert _claim(env) == PASSWORD
    assert not env.secret_path.exists()


def test_claim_without_secret_grant_is_plain_source(tmp_path):
    env = _Env(tmp_path)
    env.register(with_secret=False)
    assert _claim(env) is None


def test_claim_rejects_replay(tmp_path):
    env = _Env(tmp_path)
    env.register()
    assert _claim(env) == PASSWORD
    with pytest.raises(SourceImportError) as caught:
        _claim(env)
    assert caught.value.code in {"SOURCE_ACCESS_DENIED", "SOURCE_PASSWORD_REQUIRED"}


def test_claim_requires_exactly_one_secret_grant(tmp_path):
    env = _Env(tmp_path)
    env.register()
    env.register()
    with pytest.raises(SourceImportError) as caught:
        _claim(env)
    assert caught.value.code == "SOURCE_ACCESS_DENIED"


def test_claim_scope_mismatch_is_plain_source(tmp_path):
    env = _Env(tmp_path)
    env.register(entry_key="other-entry")
    assert _claim(env) is None


def test_claim_expired_secret_ref_is_typed(tmp_path):
    env = _Env(tmp_path)
    env.register(expires_in=-1)  # signed, but already past
    with pytest.raises(SourceImportError) as caught:
        _claim(env)
    assert caught.value.code in {"SOURCE_PASSWORD_REQUIRED", "SOURCE_GRANT_EXPIRED"}


def test_claim_rejects_secret_outside_host_directory(tmp_path):
    env = _Env(tmp_path)
    other = tmp_path / f"{env.token}.bin"
    other.write_bytes(MAGIC + _protect(PASSWORD))
    env.secret_path = other
    env.register()
    with pytest.raises(SourceImportError) as caught:
        _claim(env)
    assert caught.value.code == "SOURCE_PASSWORD_REQUIRED"


def test_claim_follows_grant_revocation(tmp_path):
    env = _Env(tmp_path)
    payload = env.register()
    env.registry.revoke_grants("registry", 2, [payload["grant_id"]])
    with pytest.raises(SourceImportError) as caught:
        _claim(env)
    assert caught.value.code == "SOURCE_GRANT_REVOKED"
