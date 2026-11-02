"""ReadingService tests (TASK-015).

Covers AC-READ-001/002 (modes + independent progress/duration),
AC-READ-003/004 foundations (paged order + direction validation),
重启继续阅读, 缺译图/stale 提示, webtoon scroll offsets and the
AC-LIB-004 shelf summary — all on the JSON document store.
"""

from __future__ import annotations

import json

from reading_export_helpers import ReaderPage, make_pages, make_reading_service


def test_resume_restores_position_and_duration_after_restart(tmp_path):
    pages = make_pages(tmp_path, count=4)
    first = make_reading_service(tmp_path)
    first.open("book", "chap", pages, direction="rtl")
    first.next_page()
    first.next_page()
    first.add_time(12.5)
    first.close()

    reopened = make_reading_service(tmp_path)  # simulates app restart
    reopened.open("book", "chap", pages, direction="rtl")
    assert reopened.page_index == 2
    assert reopened.page_count == 4
    assert reopened.progress.total_read_seconds == 12.5
    assert reopened.current_page.page_id == "p2"


def test_resume_false_starts_from_beginning_and_becomes_new_position(tmp_path):
    pages = make_pages(tmp_path, count=3)
    first = make_reading_service(tmp_path)
    first.open("book", "chap", pages)
    first.next_page()
    first.next_page()
    first.close()

    # "从章节开头开始" is an explicit user choice: the fresh position at
    # page 1 becomes the position a later resume restores (D04 §36).
    restarted = make_reading_service(tmp_path)
    restarted.open("book", "chap", pages, resume=False)
    assert restarted.page_index == 0
    reopened = make_reading_service(tmp_path)
    reopened.open("book", "chap", pages, resume=True)
    assert reopened.page_index == 0


def test_modes_keep_independent_progress_and_duration(tmp_path):
    pages = make_pages(tmp_path, count=3, translated=True)
    service = make_reading_service(tmp_path)
    service.open("book", "chap", pages, mode="original")
    service.next_page()
    service.add_time(5.0)

    service.set_mode("translated")
    assert service.page_index == 0, "translated mode starts at its own position"
    service.next_page()
    service.add_time(2.0)

    service.set_mode("original")
    assert service.page_index == 1
    assert service.progress.total_read_seconds == 5.0
    service.set_mode("translated")
    assert service.page_index == 1
    assert service.progress.total_read_seconds == 2.0

    # both rows persisted independently
    reopened = make_reading_service(tmp_path)
    reopened.open("book", "chap", pages, mode="translated")
    assert reopened.progress.total_read_seconds == 2.0
    reopened.open("book", "chap", pages, mode="original")
    assert reopened.progress.total_read_seconds == 5.0


def test_unknown_mode_and_empty_pages_rejected(tmp_path):
    pages = make_pages(tmp_path, count=2)
    service = make_reading_service(tmp_path)
    service.open("book", "chap", pages)
    try:
        service.set_mode("compare")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown mode accepted")
    try:
        service.open("book", "other", [], direction="rtl")
    except ValueError:
        pass
    else:
        raise AssertionError("empty chapter accepted")


def test_direction_and_chapter_type_validation(tmp_path):
    pages = make_pages(tmp_path, count=2)
    service = make_reading_service(tmp_path)
    # D03 §4.2: webtoon ⇔ vertical, paged ⇔ rtl/ltr.
    for chapter_type, direction, ok in [
        ("webtoon", "vertical", True),
        ("webtoon", "rtl", False),
        ("paged", "ltr", True),
        ("paged", "vertical", False),
    ]:
        if ok:
            service.open("book", "chap", pages, chapter_type=chapter_type, direction=direction)
        else:
            try:
                service.open("book", "chap", pages, chapter_type=chapter_type, direction=direction)
            except ValueError:
                pass
            else:
                raise AssertionError(f"{chapter_type}/{direction} accepted")


def test_next_previous_respect_bounds(tmp_path):
    pages = make_pages(tmp_path, count=3)
    service = make_reading_service(tmp_path)
    service.open("book", "chap", pages, direction="ltr")
    service.previous_page()
    assert service.page_index == 0, "previous at first page is a no-op"
    service.next_page()
    service.next_page()
    service.next_page()
    assert service.page_index == 2, "next at last page is a no-op"
    service.jump_to_page(0)
    assert service.page_index == 0
    try:
        service.jump_to_page(99)
    except IndexError:
        pass
    else:
        raise AssertionError("out-of-range jump accepted")


def test_missing_translated_shows_original_with_message(tmp_path):
    pages = make_pages(tmp_path, count=2)  # no translated files
    service = make_reading_service(tmp_path)
    service.open("book", "chap", pages, mode="translated")
    path, message = service.resolve_page(service.current_page)
    assert path == pages[0].original_path
    assert "译图缺失" in message
    assert service.missing_translation_page_ids() == ["p0", "p1"]


def test_stale_translated_flagged_with_message(tmp_path):
    pages = make_pages(tmp_path, count=1)
    stale = ReaderPage(
        page_id=pages[0].page_id,
        filename=pages[0].filename,
        original_path=pages[0].original_path,
        translated_path=str(tmp_path / "t.png"),
        translated_revision_id="rev-old",
        current_translated_revision_id="rev-new",
        text="译文",
    )
    service = make_reading_service(tmp_path)
    service.open("book", "chap", [stale], mode="translated")
    path, message = service.resolve_page(service.current_page)
    assert path == str(tmp_path / "t.png"), "stale render still shown, flagged"
    assert "不是最新渲染" in message
    assert service.stale_page_ids() == ["p0"]
    # original mode has no messages
    service.set_mode("original")
    assert service.status_message == ""


def test_webtoon_scroll_offset_persisted_and_restored(tmp_path):
    pages = make_pages(tmp_path, count=1)
    service = make_reading_service(tmp_path)
    service.open("book", "chap", pages, chapter_type="webtoon", direction="vertical")
    service.save_scroll_offset(1440.0)
    reopened = make_reading_service(tmp_path)
    reopened.open("book", "chap", pages, chapter_type="webtoon", direction="vertical")
    assert reopened.progress.scroll_offset_y == 1440.0


def test_duration_accumulates_across_chapters(tmp_path):
    pages1 = make_pages(tmp_path / "one", count=1)
    pages2 = make_pages(tmp_path / "two", count=1)
    for index, page in enumerate(pages2):
        pages2[index] = ReaderPage(
            page_id=f"q{index}",
            filename=page.filename,
            original_path=page.original_path,
        )
    service = make_reading_service(tmp_path)
    service.open("book", "chap1", pages1)
    service.add_time(3.0)
    service.open("book", "chap2", pages2)
    service.add_time(4.0)
    assert service.book_summary("book")["total_read_seconds"] == 7.0


def test_book_summary_shape_for_ac_lib_004(tmp_path):
    pages1 = make_pages(tmp_path / "one", count=2)
    pages2 = make_pages(tmp_path / "two", count=5)
    for index, page in enumerate(pages2):
        pages2[index] = ReaderPage(
            page_id=f"z{index}",
            filename=page.filename,
            original_path=page.original_path,
        )
    service = make_reading_service(tmp_path)
    assert service.book_summary("book")["has_progress"] is False

    service.open("book", "chap1", pages1, chapter_title="第1话")
    service.next_page()
    service.add_time(60.0)
    service.open("book", "chap2", pages2, chapter_title="第2话")
    service.add_time(30.0)

    summary = service.book_summary("book")
    assert summary["has_progress"] is True
    assert summary["last_chapter_id"] == "chap2"
    assert summary["last_mode"] == "original"
    assert summary["last_read_at"]
    assert summary["total_read_seconds"] == 90.0
    chapters = service.chapter_summaries("book")
    assert [item.chapter_id for item in chapters] == ["chap2", "chap1"]
    assert chapters[1].progress_percent == 100.0  # 2nd of 2 pages
    # JSON-serializable for the future SQLite row swap
    row = json.loads(json.dumps(summary))
    assert {"last_chapter_id", "progress_percent", "last_read_at", "total_read_seconds"} <= set(row)


def test_reordered_pages_keep_position_via_page_id(tmp_path):
    pages = make_pages(tmp_path, count=3)
    service = make_reading_service(tmp_path)
    service.open("book", "chap", pages)
    service.jump_to_page(2)
    reordered = [pages[1], pages[2], pages[0]]
    reopened = make_reading_service(tmp_path)
    reopened.open("book", "chap", reordered)
    assert reopened.current_page.page_id == "p2"


def test_shrunk_chapter_clamps_instead_of_crashing(tmp_path):
    pages = make_pages(tmp_path, count=3)
    service = make_reading_service(tmp_path)
    service.open("book", "chap", pages)
    service.jump_to_page(2)
    reopened = make_reading_service(tmp_path)
    reopened.open("book", "chap", pages[:1])
    assert reopened.page_index == 0


def test_corrupt_store_starts_clean(tmp_path):
    store_file = tmp_path / "progress.json"
    store_file.write_text("{not json", encoding="utf-8")
    service = make_reading_service(tmp_path)
    pages = make_pages(tmp_path, count=1)
    service.open("book", "chap", pages)
    assert service.page_count == 1
    assert json.loads(store_file.read_text(encoding="utf-8"))["progress_entries"]


def test_store_write_failure_keeps_previous_document(tmp_path, monkeypatch):
    pages = make_pages(tmp_path, count=1)
    service = make_reading_service(tmp_path)
    service.open("book", "chap", pages)
    from application.reading import JsonProgressDocumentStore

    good = JsonProgressDocumentStore(tmp_path / "progress.json").read()
    assert good["progress_entries"]

    def broken_write(records):
        raise OSError("disk full")

    monkeypatch.setattr(service._store, "write", broken_write)
    try:
        service.next_page()
    except OSError:
        pass
    else:
        raise AssertionError("write failure swallowed")
    # previous document intact on disk
    assert JsonProgressDocumentStore(tmp_path / "progress.json").read() == good
