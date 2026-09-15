"""Local image import: managed copy, decode validation, dedup, interruption
protection, Unicode paths (AC-IMPORT-001~005, D07 §37~39)."""

import hashlib

import pytest

pytest.importorskip("PySide6", reason="real PNG decode via Qt")

from application.importing.images.service import DuplicatePolicy
from application.importing.images.sorting import collect_image_files, natural_sort_key

import helpers
from helpers import make_corrupt_png, make_png, make_source


def _sha256_file(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture()
def chapter(library, book):
    return library.create_chapter(book.book_id, "第1话", chapter_type="paged")


def test_managed_copy_records_all_fields(import_use_case, chapter):
    # AC-IMPORT-001: copy + filename + source order + sort order + hash + w/h.
    use_case, store, sink = import_use_case()
    png_a, png_b = make_png(3, 2), make_png(5, 7, with_alpha=False)

    report = use_case.import_files(
        chapter.chapter_id,
        [make_source("002_b.png", png_b), make_source("001_a.png", png_a)],
    )

    assert [imported.filename for imported in report.imported] == ["002_b.png", "001_a.png"]
    first, second = (imported.page for imported in report.imported)
    assert (first.source_order, first.sort_order) == (1, 1)
    assert (second.source_order, second.sort_order) == (2, 2)
    assert first.source_hash == hashlib.sha256(png_b).hexdigest()
    assert first.source_filename == "002_b.png"
    assert (first.width, first.height) == (5, 7)
    assert (second.width, second.height) == (3, 2)
    # Managed copy exists verbatim and the page references it.
    for imported in report.imported:
        original = png_b if imported.page.source_order == 1 else png_a
        assert store.stored[imported.page.managed_original_ref] == original


def test_source_file_hash_untouched(import_use_case, chapter, tmp_path):
    # AC-IMPORT-002: source bytes are only read, never written; the hash is
    # identical before import and after it (and stays so afterwards).
    source_dir = tmp_path / "USER原図"
    source_dir.mkdir()
    source = source_dir / "scan_001.png"
    source.write_bytes(make_png(6, 4))
    hash_before = _sha256_file(source)

    use_case, store, sink = import_use_case()
    report = use_case.import_files(
        chapter.chapter_id,
        [make_source(source.name, source.read_bytes())],
    )
    assert len(report.imported) == 1
    page = report.imported[0].page

    assert _sha256_file(source) == hash_before
    assert page.source_hash == hash_before
    # Our managed copy holds the same bytes; the user file was never touched.
    assert store.stored[page.managed_original_ref] == source.read_bytes()
    assert _sha256_file(source) == hash_before


def test_copy_failure_leaves_no_orphan_page(import_use_case, chapter):
    # AC-IMPORT-003: copy interrupted → no page in the sink.
    use_case, store, sink = import_use_case(fail_on={"broken.png"})
    report = use_case.import_files(
        chapter.chapter_id,
        [make_source("good.png", make_png()), make_source("broken.png", make_png(2, 2))],
    )
    assert [f.filename for f in report.failed] == ["broken.png"]
    assert report.failed[0].reason == "COPY_FAILED"
    assert [i.filename for i in report.imported] == ["good.png"]
    assert len(sink.pages) == 1
    assert sink.pages[0].managed_original_ref in store.stored


def test_corrupt_image_rejected_without_page(import_use_case, chapter):
    use_case, store, sink = import_use_case()
    report = use_case.import_files(chapter.chapter_id, [make_source("truncated.png", make_corrupt_png())])
    assert report.imported == ()
    assert report.failed[0].reason == "INVALID_IMAGE"
    assert store.stored == {} and sink.pages == []


def test_transparent_png_imports(import_use_case, chapter):
    # RGBA with alpha channel decodes and records dimensions.
    use_case, store, sink = import_use_case()
    report = use_case.import_files(chapter.chapter_id, [make_source("alpha.png", make_png(8, 5, with_alpha=True))])
    page = report.imported[0].page
    assert (page.width, page.height) == (8, 5)


def test_unicode_paths_and_filenames(import_use_case, chapter, tmp_path):
    # AC-IMPORT-004: 中文/日本語/한국어/emoji/空格/括号.
    names = [
        "第１話/スキャン 001.png",
        "회차/페이지 (2).png",
        "章节/插画 🎨 (最终).png",
        "中文 文件 (括号)/图-１.png",
    ]
    sources = []
    for index, name in enumerate(names):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(make_png(2 + index, 2))
        sources.append(make_source(target.name, target.read_bytes()))

    use_case, store, sink = import_use_case()
    report = use_case.import_files(chapter.chapter_id, sources)
    assert len(report.imported) == 4
    for imported in report.imported:
        assert imported.page.managed_original_ref in store.stored


def test_duplicate_detection_by_hash(import_use_case, chapter):
    # AC-IMPORT-005: same image again is detected via source_hash.
    use_case, store, sink = import_use_case()
    same_bytes = make_png(4, 4)

    first = use_case.import_files(chapter.chapter_id, [make_source("a.png", same_bytes)])
    second = use_case.import_files(chapter.chapter_id, [make_source("b_same.png", same_bytes)])
    assert len(first.imported) == 1
    assert second.skipped_duplicates == ("b_same.png",)
    assert second.imported == ()
    assert len(sink.pages) == 1

    # UI policy can instead import it as a new page.
    third = use_case.import_files(
        chapter.chapter_id,
        [make_source("c_same.png", same_bytes)],
        duplicate_policy=DuplicatePolicy.IMPORT_AS_NEW,
    )
    assert len(third.imported) == 1
    assert len(sink.pages) == 2


def test_cancellation_keeps_committed_pages_only(import_use_case, chapter):
    use_case, store, sink = import_use_case()
    # Distinct widths keep the bytes (and thus hashes) unique per file.
    sources = [make_source(f"{i:02d}.png", make_png(i + 1, 2)) for i in range(1, 5)]
    seen = {"count": 0}

    def cancel_after_two() -> bool:
        seen["count"] += 1
        return seen["count"] > 2

    report = use_case.import_files(chapter.chapter_id, sources, cancelled=cancel_after_two)
    assert report.cancelled is True
    assert len(report.imported) == 2
    assert report.pending_after_cancel == ("03.png", "04.png")
    assert len(sink.pages) == 2
    # No page exists without its managed copy.
    for page in sink.pages:
        assert page.managed_original_ref in store.stored


def test_folder_collection_uses_natural_order(tmp_path):
    (tmp_path / "page10.png").write_bytes(b"stub-not-decoded-here")
    (tmp_path / "page2.jpg").write_bytes(b"stub")
    (tmp_path / "notes.txt").write_bytes(b"ignore me")
    collected = collect_image_files(tmp_path)
    assert [p.name for p in collected] == ["page2.jpg", "page10.png"]
    assert natural_sort_key("第2页.png") < natural_sort_key("第10页.png")
    with pytest.raises(NotADirectoryError):
        collect_image_files(tmp_path / "missing")
