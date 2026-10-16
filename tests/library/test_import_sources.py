"""Selected-path trust boundary for image/PDF imports (AC-IMPORT-002/004)."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

import pytest

from application.importing.images.sorting import sources_from_selection


def test_folder_selection_reads_only_direct_image_files_in_natural_order(tmp_path):
    root = tmp_path / "漫画 (第一話)"
    root.mkdir()
    (root / "page10.png").write_bytes(b"ten")
    (root / "page2.png").write_bytes(b"two")
    (root / "notes.txt").write_bytes(b"ignored")
    nested = root / "subfolder"
    nested.mkdir()
    (nested / "page1.png").write_bytes(b"not recursive")

    sources = sources_from_selection(root)

    assert [source.filename for source in sources] == ["page2.png", "page10.png"]
    assert [source.read() for source in sources] == [b"two", b"ten"]


def test_explicit_file_selection_is_contained_and_preserves_unicode(tmp_path):
    root = tmp_path / "已选择 🇯🇵"
    root.mkdir()
    selected = root / "한국어 (第 １ 頁).png"
    selected.write_bytes(b"selected")
    sibling = root / "not-selected.png"
    sibling.write_bytes(b"sibling")

    sources = sources_from_selection(root, [selected])

    assert [source.filename for source in sources] == [selected.name]
    assert sources[0].read() == b"selected"

    with pytest.raises(ValueError):
        sources_from_selection(root, [tmp_path / "outside.png"])


@pytest.mark.parametrize(
    "root,selected",
    [
        (Path("relative"), None),
        (Path("."), [Path("relative/page.png")]),
    ],
    ids=["relative-root", "relative-source"],
)
def test_relative_selection_is_rejected(root, selected):
    with pytest.raises(ValueError):
        sources_from_selection(root, selected)


def test_dotdot_traversal_and_other_drive_are_rejected_before_read(tmp_path):
    root = tmp_path / "selected"
    root.mkdir()
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"outside")

    with pytest.raises(ValueError):
        sources_from_selection(root, [root / ".." / "outside.png"])

    other_drive = "Z:" if os.path.normcase(root.drive) != "z:" else "Y:"
    with pytest.raises(ValueError):
        sources_from_selection(root, [Path(other_drive + "\\outside.png")])


def test_selected_symlink_is_rejected_without_reading_target(tmp_path):
    root = tmp_path / "selected"
    target = tmp_path / "outside.png"
    root.mkdir()
    target.write_bytes(b"protected")
    link = root / "link.png"
    try:
        link.symlink_to(target)
    except OSError as error:
        pytest.skip(f"file symlink creation is unavailable: {error}")

    try:
        with pytest.raises(ValueError):
            sources_from_selection(root, [link])
        assert target.read_bytes() == b"protected"
    finally:
        link.unlink(missing_ok=True)


def test_selected_junction_is_rejected(tmp_path):
    root = tmp_path / "selected"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (outside / "page.png").write_bytes(b"protected")
    junction = root / "junction"
    created = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(outside)],
        capture_output=True,
    )
    if created.returncode != 0:
        pytest.skip("directory junction creation is unavailable")

    try:
        with pytest.raises(ValueError):
            sources_from_selection(root, [junction / "page.png"])
        assert (outside / "page.png").read_bytes() == b"protected"
    finally:
        junction.rmdir()


def test_invalid_scope_has_no_import_side_effects(import_use_case, chapter, tmp_path):
    root = tmp_path / "selected"
    root.mkdir()
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"not read")
    use_case, store, sink = import_use_case()

    with pytest.raises(ValueError):
        use_case.import_files(
            chapter.chapter_id,
            sources_from_selection(root, [outside]),
        )

    assert store.stored == {}
    assert sink.pages == []
