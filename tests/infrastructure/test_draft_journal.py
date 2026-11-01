from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from domain.drafts.entities import Draft
from infrastructure.filesystem.draft_journal import DraftJournal, DraftJournalError


def make_draft(sequence: int = 0, text: str = "x") -> Draft:
    return Draft(
        draft_id="journal-probe", session_id="session", page_id="page",
        region_id="region", base_revision_id="base", page_binding_version=4,
        draft_sequence=sequence, patch={"text": {"value": text}},
    )


def test_journal_round_trip_and_receipts_are_per_sequence(tmp_path: Path) -> None:
    journal = DraftJournal(tmp_path / "drafts")
    try:
        draft = make_draft()
        journal.write_draft(draft)
        journal.write_receipt({
            "tokenId": "t0", "DraftId": draft.draft_id, "DraftSequence": 0,
            "revisionIds": {"region": "rev-0"}, "contentDigests": {"region": "d0"},
            "committedAt": datetime.now(timezone.utc).isoformat(),
        })
        journal.write_receipt({
            "tokenId": "t1", "DraftId": draft.draft_id, "DraftSequence": 1,
            "revisionIds": {"region": "rev-1"}, "contentDigests": {"region": "d1"},
            "committedAt": datetime.now(timezone.utc).isoformat(),
        })
        assert len(draft.to_json()) == 11
        assert journal.read_receipt(draft.draft_id, 0)["revisionIds"] == {"region": "rev-0"}
        assert journal.read_receipt(draft.draft_id, 1)["revisionIds"] == {"region": "rev-1"}
        restored = journal.load_drafts()
        assert len(restored) == 1
        assert restored[0][0].status.value == "active"
    finally:
        journal.close()


@pytest.mark.parametrize("phase,expected_exit,expected_text", [("A", 70, "old"), ("B", 71, "old"), ("C", 72, "new")])
def test_real_process_crash_a_b_c_keeps_old_or_new_complete_journal(
    tmp_path: Path, phase: str, expected_exit: int, expected_text: str
) -> None:
    worker = Path(__file__).with_name("draft_journal_crash_worker.py")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC_ROOT)
    result = subprocess.run(
        [sys.executable, str(worker), str(tmp_path / "drafts"), phase],
        env=env, capture_output=True, text=True, timeout=20,
    )
    assert result.returncode == expected_exit, result.stderr

    journal = DraftJournal(tmp_path / "drafts")
    try:
        restored = journal.load_drafts()
        assert len(restored) == 1
        assert restored[0][0].patch["text"]["value"] == expected_text
        assert not list((tmp_path / "drafts").glob("*.tmp"))
        assert not list((tmp_path / "drafts" / "receipts").glob("*.tmp"))
    finally:
        journal.close()


def test_corrupt_journal_is_discarded_without_blocking_startup(tmp_path: Path) -> None:
    root = tmp_path / "drafts"
    root.mkdir()
    (root / "broken.json").write_text("{invalid", encoding="utf-8")
    journal = DraftJournal(root)
    try:
        assert journal.load_drafts() == []
        assert not (root / "broken.json").exists()
        assert any("corrupt-journal-discarded" in note for note in journal.recovery_notices)
    finally:
        journal.close()


def test_journal_cleans_orphan_temporary_files_at_startup(tmp_path: Path) -> None:
    root = tmp_path / "drafts"
    (root / "receipts").mkdir(parents=True)
    temp = root / "orphan.tmp"
    receipt_temp = root / "receipts" / "orphan.tmp"
    temp.write_text("partial", encoding="utf-8")
    receipt_temp.write_text("partial", encoding="utf-8")
    journal = DraftJournal(root)
    try:
        assert not temp.exists()
        assert not receipt_temp.exists()
    finally:
        journal.close()


def test_second_writer_is_shared_in_process_and_lock_releases_on_close(tmp_path: Path) -> None:
    # FEA-03: a same-process re-assembly over the same data root shares the
    # writer lock (Core restart in tests). Cross-process exclusivity is covered
    # by test_two_processes_share_one_exclusive_journal_writer.
    root = tmp_path / "drafts"
    first = DraftJournal(root)
    second = DraftJournal(root)
    assert second.available is True
    first.close()
    second.close()
    third = DraftJournal(root)
    third.close()

def test_two_processes_share_one_exclusive_journal_writer(tmp_path: Path) -> None:
    root = tmp_path / "drafts"
    first = DraftJournal(root)
    worker = Path(__file__).with_name("draft_journal_crash_worker.py")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC_ROOT)
    try:
        blocked = subprocess.run(
            [sys.executable, str(worker), str(root), "LOCK"],
            env=env, capture_output=True, text=True, timeout=20,
        )
        assert blocked.returncode == 73, blocked.stderr
    finally:
        first.close()
    acquired = subprocess.run(
        [sys.executable, str(worker), str(root), "LOCK"],
        env=env, capture_output=True, text=True, timeout=20,
    )
    assert acquired.returncode == 0, acquired.stderr


def test_receipt_cleanup_uses_draft_activity_and_does_not_delete_journal(tmp_path: Path) -> None:
    journal = DraftJournal(tmp_path / "drafts")
    try:
        draft = make_draft()
        draft.saved_at = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
        journal.write_draft(draft)
        journal.write_receipt({
            "tokenId": "t", "DraftId": draft.draft_id, "DraftSequence": 0,
            "revisionIds": {"region": "rev"}, "contentDigests": {"region": "digest"},
            "committedAt": datetime.now(timezone.utc).isoformat(),
        })
        removed = journal.cleanup_receipts()
        assert removed == [f"{draft.draft_id}.0.json"]
        assert (journal.root / f"{draft.draft_id}.json").exists()
    finally:
        journal.close()


def test_unwritable_journal_fails_closed_but_keeps_memory_capability(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(DraftJournal, "_probe_writable", lambda _self: (_ for _ in ()).throw(PermissionError()))
    journal = DraftJournal(tmp_path / "drafts")
    try:
        assert journal.available is False
        with pytest.raises(DraftJournalError) as error:
            journal.write_draft(make_draft())
        assert error.value.code == "DRAFT_JOURNAL_UNWRITABLE"
    finally:
        journal.close()
