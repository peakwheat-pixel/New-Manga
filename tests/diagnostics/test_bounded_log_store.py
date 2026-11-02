"""BoundedLogStore: rotation and retention bounds (TASK-055 AC 2).

These are the regression guards for the retention invariant: the store
never exceeds ``max_files`` files, each file never exceeds the per-file
byte cap, and pruning always removes the *oldest* file. As new
capability there is no pre-fix tree to discriminate against (declared
not-applicable in the Task AC 5); these assertions pin the bounds so a
future edit cannot silently make retention unbounded."""

from __future__ import annotations

import threading
from pathlib import Path

from infrastructure.filesystem.bounded_log_store import BoundedLogStore

_T = "2026-09-19T02:00:00.123456"


def _store(tmp_path: Path, *, max_files=3, max_bytes=200) -> BoundedLogStore:
    return BoundedLogStore(
        tmp_path, max_files=max_files, max_bytes_per_file=max_bytes
    )


def test_append_creates_file_and_grows_within_cap(tmp_path):
    store = _store(tmp_path)
    store.append("line-1", timestamp=_T)
    store.append("line-2", timestamp=_T)
    files = store.files()
    assert len(files) == 1
    assert files[0].read_text(encoding="utf-8") == "line-1\nline-2\n"


def test_write_creates_one_file_per_report(tmp_path):
    store = _store(tmp_path)

    first = store.write('{"report": 1}', timestamp=_T)
    second = store.write('{"report": 2}', timestamp=_T)

    assert first != second
    assert [path.read_text(encoding="utf-8") for path in store.files()] == [
        '{"report": 1}\n',
        '{"report": 2}\n',
    ]


def test_rotation_when_current_file_exceeds_byte_cap(tmp_path):
    store = _store(tmp_path, max_bytes=12)
    store.append("0123456789", timestamp=_T)  # 11 bytes incl newline
    store.append("0123456789", timestamp=_T)  # would exceed -> rotate
    files = store.files()
    assert len(files) == 2
    assert files[0].read_text(encoding="utf-8") == "0123456789\n"
    assert files[1].stat().st_size <= 12


def test_pruning_removes_the_oldest_file_beyond_max_files(tmp_path):
    store = _store(tmp_path, max_files=3, max_bytes=12)
    for i in range(6):
        store.append(f"data-{i}-012345", timestamp=_T)
    files = store.files()
    assert len(files) == 3
    # the three oldest generations are gone; the newest survives
    assert "data-5" in files[-1].read_text(encoding="utf-8")
    assert "data-0-" not in "".join(p.read_text(encoding="utf-8") for p in files)


def test_total_bytes_is_bounded_after_many_rotations(tmp_path):
    store = _store(tmp_path, max_files=3, max_bytes=50)
    for i in range(30):
        store.append(f"payload-{i:02d}-0123456789012345", timestamp=_T)
    assert store.total_bytes() <= 3 * 50 + len("payload-29-0123456789012345\n")


def test_files_are_ordered_oldest_first_by_name(tmp_path):
    store = _store(tmp_path, max_bytes=12)
    store.append("first", timestamp="2026-09-19T02:00:00.000001")
    store.append("second", timestamp="2026-09-19T02:00:01.000001")
    names = [path.name for path in store.files()]
    assert names == sorted(names)
    assert len(names) == 2


def test_concurrent_append_keeps_every_line(tmp_path):
    store = _store(tmp_path, max_files=10, max_bytes=1_000_000)
    per_thread, threads = 50, []

    def worker(offset: int) -> None:
        for i in range(per_thread):
            store.append(f"t{offset}-{i}", timestamp=_T)

    for offset in range(4):
        thread = threading.Thread(target=worker, args=(offset,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

    total_lines = sum(
        len(path.read_text(encoding="utf-8").splitlines()) for path in store.files()
    )
    assert total_lines == 4 * per_thread


def test_bounds_are_validated(tmp_path):
    import pytest

    with pytest.raises(ValueError):
        BoundedLogStore(tmp_path, max_files=0)
    with pytest.raises(ValueError):
        BoundedLogStore(tmp_path, max_bytes_per_file=0)
