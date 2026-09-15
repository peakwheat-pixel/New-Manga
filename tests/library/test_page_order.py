import pytest

pytest.importorskip("PySide6", reason="real PNG decode via Qt")

"""Page ordering: source_order frozen, sort_order user-owned (AC-PAGE-001)."""

from helpers import make_png, make_source


def test_reorder_pages_keeps_source_order(import_use_case, chapter):
    use_case, store, sink = import_use_case()
    names = ["001.png", "002.png", "003.png"]
    # Distinct widths keep hashes unique so nothing is skipped as duplicate.
    report = use_case.import_files(
        chapter.chapter_id,
        [make_source(name, make_png(index + 1, 2)) for index, name in enumerate(names)],
    )
    pages = {imported.page.source_filename: imported.page for imported in report.imported}
    assert [pages[name].source_order for name in names] == [1, 2, 3]
    assert all(pages[name].sort_order == pages[name].source_order for name in names)

    # User drags 003 to the front: sort_order changes, source_order does not.
    ordered_ids = [pages["003.png"].page_id, pages["001.png"].page_id, pages["002.png"].page_id]
    for position, page_id in enumerate(ordered_ids, start=1):
        pages[name_of(pages, page_id)].reorder(position)

    assert [pages[name].sort_order for name in names] == [2, 3, 1]
    # The original import order survives the drag-and-drop (AC-PAGE-001).
    assert [pages[name].source_order for name in names] == [1, 2, 3]


def name_of(pages, page_id):
    for filename, page in pages.items():
        if page.page_id == page_id:
            return filename
    raise KeyError(page_id)
