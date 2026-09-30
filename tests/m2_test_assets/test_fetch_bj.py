# -*- coding: utf-8 -*-
"""Offline unit tests for tools/fetch_bj.py (M2-TA2B DSH r1 P2-4 closure).

All network interaction is faked via monkeypatched openers; no test touches the
real densho810.com host or the gitignored asset directories.
"""

import io
import json
import sys
import urllib.error
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from test_assets.comic_golden_suite.tools import fetch_bj


class FakeResponse:
    def __init__(self, url, payload, content_length=None):
        self._stream = io.BytesIO(payload)
        self.url = url
        self.headers = {"Content-Length": str(len(payload)) if content_length is None else content_length}

    def geturl(self):
        return self.url

    def read(self, size=-1):
        return self._stream.read(size)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeOpener:
    def __init__(self, respond):
        self._respond = respond

    def open(self, request, timeout=None):
        return self._respond(request.full_url)


def fake_zip_payload(content=b"PK-fake-pdf-bytes"):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("005bj.pdf", content)
    return buffer.getvalue()


@pytest.fixture()
def isolated_output(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch_bj, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(fetch_bj, "RETRY_ATTEMPTS", 1)
    monkeypatch.setattr(fetch_bj, "TIMEOUT", 1)
    return tmp_path


def test_redirect_to_foreign_host_is_rejected_and_nothing_published(isolated_output, monkeypatch):
    def respond(url):
        raise urllib.error.HTTPError(url, 302, "moved", {"Location": "https://evil.example/steal.zip"}, io.BytesIO(b""))

    monkeypatch.setattr(fetch_bj.urllib.request, "build_opener", lambda handler: FakeOpener(respond))
    destination = isolated_output / "vol05" / "005bj.zip"
    with pytest.raises(OSError, match="download failed"):
        fetch_bj.download_archive("https://densho810.com/free/dl/005bj.zip", destination)
    assert not destination.exists()
    assert list(isolated_output.rglob("*.part")) == []


def test_missing_content_length_is_rejected(isolated_output, monkeypatch):
    def respond(url):
        return FakeResponse(url, fake_zip_payload(), content_length="not-a-number")

    monkeypatch.setattr(fetch_bj.urllib.request, "build_opener", lambda handler: FakeOpener(respond))
    destination = isolated_output / "vol05" / "005bj.zip"
    with pytest.raises(OSError, match="download failed"):
        fetch_bj.download_archive("https://densho810.com/free/dl/005bj.zip", destination)
    assert not destination.exists()
    assert list(isolated_output.rglob("*.part")) == []


def test_oversized_declared_size_is_rejected(isolated_output, monkeypatch):
    # Shrink the limit so the payload itself satisfies the length checks: only the
    # size-cap guard can reject here (removing it would fail with a different message).
    monkeypatch.setattr(fetch_bj, "MAX_ARCHIVE_BYTES", 8)

    def respond(url):
        return FakeResponse(url, b"0123456789ABCDEF", content_length="16")

    monkeypatch.setattr(fetch_bj.urllib.request, "build_opener", lambda handler: FakeOpener(respond))
    destination = isolated_output / "vol05" / "005bj.zip"
    with pytest.raises(OSError, match="outside limits"):
        fetch_bj.download_archive("https://densho810.com/free/dl/005bj.zip", destination)
    assert not destination.exists()


def test_non_zip_payload_is_never_published(isolated_output, monkeypatch):
    def respond(url):
        return FakeResponse(url, b"definitely not a zip file")

    monkeypatch.setattr(fetch_bj.urllib.request, "build_opener", lambda handler: FakeOpener(respond))
    destination = isolated_output / "vol05" / "005bj.zip"
    with pytest.raises(OSError, match="download failed"):
        fetch_bj.download_archive("https://densho810.com/free/dl/005bj.zip", destination)
    assert not destination.exists()
    assert list(isolated_output.rglob("*.part")) == []


def test_valid_payload_publishes_atomically(isolated_output, monkeypatch):
    payload = fake_zip_payload()

    def respond(url):
        return FakeResponse(url, payload)

    monkeypatch.setattr(fetch_bj.urllib.request, "build_opener", lambda handler: FakeOpener(respond))
    destination = isolated_output / "vol05" / "005bj.zip"
    downloaded, reason, digest, size = fetch_bj.download_archive("https://densho810.com/free/dl/005bj.zip", destination)
    assert downloaded and reason == "downloaded"
    assert size == len(payload)
    assert len(digest) == 64 and destination.is_file()
    assert list(isolated_output.rglob("*.part")) == []


def test_extract_pdf_skips_macosx_appledouble_members(tmp_path):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("__MACOSX/._005bj.pdf", b"\x00\x01\x02\x03\x04\x05\x06\x07AppleDouble")
        archive.writestr("005bj.pdf", b"%PDF-real-content")
    archive_path = tmp_path / "005bj.zip"
    archive_path.write_bytes(buffer.getvalue())
    volume_dir = tmp_path / "vol05"
    volume_dir.mkdir()
    filename, digest, size = fetch_bj.extract_pdf(archive_path, volume_dir, 5)
    assert filename == "volume05.pdf"
    assert size == len(b"%PDF-real-content")
    assert [p.name for p in volume_dir.glob("*")] == ["volume05.pdf"]


def test_redirect_guard_rejects_foreign_targets_directly():
    # Drives RedirectGuard itself (DSH r2 N-3): bypassing the guard must turn this red.
    guard = fetch_bj.RedirectGuard()
    request = urllib.request.Request("https://densho810.com/free/dl/005bj.zip")
    with pytest.raises(urllib.error.HTTPError):
        guard.redirect_request(
            request, None, 302, "moved", {"Location": "https://evil.example/x.zip"},
            "https://evil.example/x.zip",
        )
    follow = guard.redirect_request(
        request, None, 302, "moved", {"Location": "https://densho810.com/free/dl/006bj.zip"},
        "https://densho810.com/free/dl/006bj.zip",
    )
    assert follow is not None and follow.full_url.endswith("006bj.zip")


def test_jasrac_volumes_are_refused_by_policy(isolated_output, monkeypatch):
    # main() must refuse volumes 2/7/11 before touching the network or disk.
    for volume in (2, 7, 11):
        with patch.object(sys, "argv", ["fetch_bj.py", "fetch", "--volumes", str(volume)]):
            assert fetch_bj.main() == 2
    assert list(isolated_output.rglob("*")) == []
