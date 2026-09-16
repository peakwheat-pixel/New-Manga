from pathlib import Path

from application.reading.service import PageView, ReadingService, ReadingMode


def test_progress_and_duration_survive_restart_and_are_mode_specific(tmp_path: Path):
    state = tmp_path / "reader.json"
    pages = [
        PageView("p1", "original-1.png", "translated-1.png", "r1", "r1"),
        PageView("p2", "original-2.png", "translated-2.png", "r2", "r2"),
    ]
    service = ReadingService(state)
    service.open("book", "chapter", pages, mode=ReadingMode.ORIGINAL, direction="rtl")
    service.record_progress(1, 12.5)
    service.close()
    service.open("book", "chapter", pages, mode=ReadingMode.TRANSLATED, direction="ltr")
    assert service.progress.page_index == 0
    service.record_progress(0, 3.25)
    service.close()

    restarted = ReadingService(state)
    restarted.open("book", "chapter", pages, mode=ReadingMode.ORIGINAL, direction="rtl")
    assert restarted.progress.page_index == 1
    assert restarted.progress.duration_seconds == 12.5
    assert restarted.direction == "rtl"
    restarted.open("book", "chapter", pages, mode=ReadingMode.TRANSLATED, direction="ltr")
    assert restarted.progress.page_index == 0
    assert restarted.progress.duration_seconds == 3.25
    assert restarted.direction == "ltr"


def test_stale_translation_is_explicit_and_missing_translation_falls_back(tmp_path: Path):
    pages = [
        PageView("p1", "original.png", "translated.png", "old", "new"),
        PageView("p2", "original-2.png", None, None, None),
    ]
    service = ReadingService(tmp_path / "reader.json")
    service.open("b", "c", pages, mode=ReadingMode.TRANSLATED, direction="ltr")
    assert service.current.source_path == "translated.png"
    assert service.current.stale is True
    assert "stale" in service.current.status_message.lower()
    service.next_page()
    assert service.current.source_path == "original-2.png"
    assert "missing" in service.current.status_message.lower()

