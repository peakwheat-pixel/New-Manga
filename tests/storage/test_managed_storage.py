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


class TestR010ReparseWalk:
    """TASK-061 R-010: a *root-internal* junction resolves back inside the
    root, so the containment check alone lets a tampered reference reach a
    sibling chapter's protected original through the link.  The removal
    point must walk the unresolved path and refuse any reparse point.
    Discriminating: on the pre-fix tree the traversal is granted and the
    protected file is gone."""

    def test_refuses_a_root_internal_junction_and_spares_the_target(
        self, tmp_path
    ):
        import subprocess

        storage = ManagedFileStorage(tmp_path / "managed")
        storage.ensure_layout()
        protected_rel = "books/book-1/chapters/chapter-1/original/keep.png"
        protected = tmp_path / "managed" / Path(*protected_rel.split("/"))
        protected.parent.mkdir(parents=True)
        protected.write_bytes(b"PROTECTED ORIGINAL")

        # mklink /J needs no privileges on NTFS; it creates a directory
        # junction (reparse point).  Limitation (declared): this covers the
        # directory-junction form only; file symlinks require developer
        # mode/privilege and are not exercised here.
        twin = tmp_path / "managed" / "books" / "book-twin"
        made = subprocess.run(
            # junction target: the book-1 directory (original's parents[2])
            ["cmd", "/c", "mklink", "/J", str(twin), str(protected.parent.parents[2])],
            capture_output=True,  # no text: mklink output is GBK on this box
        )
        assert made.returncode == 0, made.stderr

        with pytest.raises(ImmutablePathViolation):
            storage.remove_managed(
                "books/book-twin/chapters/chapter-1/original/keep.png"
            )

        assert protected.is_file(), (
            "the root-internal junction deleted the protected original"
        )


class TestR011DotSegmentIsAlive:
    """TASK-061 R-011: ``PurePosixPath('a/./b').parts`` drops the ``.``,
    so ``'.' in parts`` was a dead condition.  The lexical check now reads
    the raw split segments, and a ``.`` component is a typed refusal.
    Discriminating: on the pre-fix tree the dotted path lexes clean and
    the file is removed."""

    def test_refuses_a_dot_segment_and_spares_the_file(self, tmp_path):
        storage = ManagedFileStorage(tmp_path / "managed")
        storage.ensure_layout()
        target = tmp_path / "managed" / "books" / "keep.png"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"KEEP")

        with pytest.raises(ImmutablePathViolation):
            storage.remove_managed("books/./keep.png")

        assert target.is_file(), "the dotted path lexed clean and deleted the file"

    def test_refuses_an_empty_middle_segment(self, tmp_path):
        storage = ManagedFileStorage(tmp_path / "managed")
        storage.ensure_layout()
        target = tmp_path / "managed" / "books" / "keep2.png"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"KEEP")

        with pytest.raises(ImmutablePathViolation):
            storage.remove_managed("books//keep2.png")

        assert target.is_file()
