"""R1-I007 P2: bound the decompressed member size before archive.read."""

from __future__ import annotations

import zipfile
from types import SimpleNamespace

import pytest

from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.identity import normalize_identity
from application.importing.referenced.reader import read_entry_bytes
from support import png_bytes


def _resolved(path, max_decode):
    info = path.stat()
    import hashlib

    return SimpleNamespace(
        source_kind="cbz",
        container_path=str(path),
        container_facts=SimpleNamespace(
            volume_serial=normalize_identity(info.st_dev, info.st_ino)[0],
            file_id=normalize_identity(info.st_dev, info.st_ino)[1],
            size=info.st_size,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        ),
        folder_root=None,
        folder_entries=(),
        budget=SimpleNamespace(
            max_bytes=8 * 1024 * 1024,
            max_decode_bytes=max_decode,
            max_entries=100,
        ),
    )


def _entry(ordinal=0, locator="001.png"):
    return SimpleNamespace(ordinal=ordinal, locator=locator)


def test_zip_member_over_decode_budget_is_refused_before_read(tmp_path):
    archive = tmp_path / "bomb.cbz"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("001.png", png_bytes(64, 64))
    resolved = _resolved(archive, max_decode=16)
    with pytest.raises(SourceImportError) as caught:
        read_entry_bytes(resolved, _entry())
    assert caught.value.code == "SOURCE_BUDGET_EXCEEDED"


def test_zip_member_within_budget_reads(tmp_path):
    archive = tmp_path / "ok.cbz"
    payload = png_bytes(2, 2)
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("001.png", payload)
    resolved = _resolved(archive, max_decode=1024 * 1024)
    assert read_entry_bytes(resolved, _entry()) == payload
