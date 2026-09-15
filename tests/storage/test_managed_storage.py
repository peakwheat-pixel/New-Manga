"""Managed file storage tests: immutability, Unicode paths (D07 §35),
source-file protection (D03 §43-1/§43-7) and temp hygiene (D07 §31)."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from infrastructure.filesystem.managed_storage import (
    ImmutablePathViolation,
    ManagedFileStorage,
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_publish_is_atomic_and_temp_is_consumed(tmp_path):
    storage = ManagedFileStorage(tmp_path / "storage")
    storage.ensure_layout()
    temp = storage.write_temp(b"payload")
    relative = storage.new_revision_relative_path("b1", "c1", "clean", "r1", ".png")

    storage.publish(temp, relative)

    published = Path(storage.absolute_path(relative))
    assert published.read_bytes() == b"payload"
    assert not Path(temp).exists()
    assert list((tmp_path / "storage" / "temp").iterdir()) == []


def test_publish_refuses_to_overwrite_committed_revision(tmp_path):
    storage = ManagedFileStorage(tmp_path / "storage")
    storage.ensure_layout()
    relative = storage.new_revision_relative_path("b1", "c1", "mask", "r1", ".png")
    storage.publish(storage.write_temp(b"first"), relative)

    with pytest.raises(ImmutablePathViolation):
        storage.publish(storage.write_temp(b"second"), relative)

    published = Path(storage.absolute_path(relative))
    assert published.read_bytes() == b"first"


def test_revision_paths_follow_d03_layout(tmp_path):
    """R-101: every artifact type lands in the D03 §18 directory set under
    ``books/{book_id}/chapters/{chapter_id}/``; exports go to the book-level
    ``exports/`` directory; unknown types are rejected."""
    from infrastructure.filesystem.managed_storage import ARTIFACT_TYPE_DIRS

    storage = ManagedFileStorage(tmp_path / "storage")
    legal_dirs = {"original", "masks", "clean", "translated", "thumbnails", "previews", "debug"}

    for artifact_type in ARTIFACT_TYPE_DIRS:
        path = storage.new_revision_relative_path(
            "BOOK1", "CH1", artifact_type, "REV1", ".png"
        )
        parts = path.split("/")
        assert parts[0] == "books", path
        if artifact_type == "export":
            assert path == "books/BOOK1/exports/REV1.png"
            continue
        assert parts[2:4] == ["chapters", "CH1"], path
        assert parts[4] in legal_dirs, f"{artifact_type} -> {parts[4]} not in D03 §18 set"
        assert parts[5] == "REV1.png"

    expected = {
        "original": "original",
        "thumbnail": "thumbnails",
        "mask": "masks",
        "clean": "clean",
        "translated": "translated",
        "render_preview": "previews",
        "detection_overlay": "previews",
        "debug_ocr": "debug",
        "debug_detection": "debug",
    }
    for artifact_type, directory in expected.items():
        path = storage.new_revision_relative_path("B", "C", artifact_type, "R", ".png")
        assert path.split("/")[4] == directory, path

    with pytest.raises(ValueError):
        storage.new_revision_relative_path("B", "C", "sticker", "R", ".png")


def test_unicode_paths_round_trip(tmp_path):
    unicode_root = tmp_path / "漫画库" / "【作品テスト】" / "第１話 🇯🇵"
    storage = ManagedFileStorage(unicode_root)
    storage.ensure_layout()
    relative = storage.new_revision_relative_path(
        "büch-идентификатор", "cháptěř", "translated", "révision-🈶", ".png"
    )
    temp = storage.write_temp("üñíçø∂é".encode())
    storage.publish(temp, relative)
    assert Path(storage.absolute_path(relative)).read_bytes() == "üñíçø∂é".encode()
    assert storage.verify_temp(storage.write_temp(b"x")).size_bytes == 1


def test_source_file_hash_is_untouched_by_storage(tmp_path):
    source = tmp_path / "用户原图" / "scan_001.png"
    source.parent.mkdir(parents=True)
    original = b"original user scan bytes"
    source.write_bytes(original)
    hash_before = _sha256(source.read_bytes())

    storage = ManagedFileStorage(tmp_path / "storage")
    storage.ensure_layout()
    content = source.read_bytes()
    relative = storage.new_revision_relative_path("b1", "c1", "original", "r1", ".png")
    storage.publish(storage.write_temp(content), relative)

    assert source.read_bytes() == original
    assert _sha256(source.read_bytes()) == hash_before


def test_unsafe_path_components_are_rejected(tmp_path):
    storage = ManagedFileStorage(tmp_path / "storage")
    with pytest.raises(ValueError):
        storage.new_revision_relative_path("../escape", "c1", "clean", "r1", ".png")
    with pytest.raises(ValueError):
        storage.new_revision_relative_path("b1", "c1", "clean", "a/b", ".png")
    with pytest.raises(ValueError):
        storage.new_revision_relative_path("", "c1", "clean", "r1", ".png")


def test_verify_temp_reports_integrity(tmp_path):
    storage = ManagedFileStorage(tmp_path / "storage")
    storage.ensure_layout()
    content = b"integrity-check"
    temp = storage.write_temp(content)
    info = storage.verify_temp(temp)
    assert info.sha256 == _sha256(content)
    assert info.size_bytes == len(content)
