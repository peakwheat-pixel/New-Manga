from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from application.editing.drafts import DraftProtectionService
from application.editing.errors import DraftError
from application.editing.service import RegionEditingService
from domain.regions.entities import BBox, RegionGeometry
from infrastructure.filesystem.draft_journal import DraftJournal, DraftJournalError
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.regions import SqliteRegionRepository
from infrastructure.sqlite.schema import default_migrations

NOW = "2026-11-02T00:00:00+00:00"


def seed_page(conn: sqlite3.Connection) -> None:
    with conn:
        conn.execute(
            "INSERT INTO books(book_id,title,created_at,updated_at) VALUES('b','b',?,?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT INTO chapters(chapter_id,book_id,title,created_at,updated_at) VALUES('c','b','c',?,?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT INTO pages(page_id,chapter_id,sort_order,created_at,updated_at,width,height) "
            "VALUES('p','c',0,?,?,800,1200)",
            (NOW, NOW),
        )


def new_region(editing: RegionEditingService):
    return editing.create_region(
        "p", RegionGeometry(bbox=BBox(1, 2, 40, 50))
    )


def main() -> None:
    results: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="fea03-component-") as temporary:
        root = Path(temporary)
        db_path = root / "library.sqlite"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        MigrationRunner(conn, default_migrations()).apply_pending()
        seed_page(conn)
        repository = SqliteRegionRepository(conn)
        editing = RegionEditingService(repository, repository)
        journal = DraftJournal(root / "drafts")
        drafts = DraftProtectionService(repository, repository, conn, journal)

        first, second, third = (new_region(editing) for _ in range(3))
        base = repository.get_region(first.region_id).current_revision_id
        lease = drafts.open_draft(
            "session-1", "p", first.region_id,
            base_revision_id=base, page_binding_version=8,
        )
        record = journal.read_draft_record(lease.draft.draft_id)
        assert record and record["status"] == "active"
        drafts.patch_draft(
            lease.draft.draft_id, "session-1",
            {"text": {"edited_translation": "manual"}}, schedule_flush=False,
        )
        token = drafts.issue_edit_token(lease.draft.draft_id)
        candidate = drafts.prepare_candidate(
            first.region_id, {"text": {"edited_translation": "manual"}},
            origin="user", draft_id=lease.draft.draft_id,
        )
        assert repository.get_region(first.region_id).current_revision_id == base
        applied = drafts.apply_candidates(token, [candidate.candidate_id])
        assert drafts.apply_candidates(token) == applied
        assert conn.execute(
            "SELECT COUNT(*) FROM region_revisions WHERE region_id=?",
            (first.region_id,),
        ).fetchone()[0] == 2
        results["edit_open_and_candidate_only"] = "PASS"
        results["apply_and_receipt_replay"] = "PASS"

        batch = drafts.open_draft(
            "batch-session", "p", None,
            base_revision_id=None, page_binding_version=9,
        )
        candidates = [
            drafts.prepare_candidate(
                region.region_id, {"style": {"text_color": "#123"}},
                origin="user", draft_id=batch.draft.draft_id,
            )
            for region in (first, second, third)
        ]
        before = {
            region.region_id: (
                repository.get_region(region.region_id).current_revision_id,
                len(repository.list_revisions(region.region_id)),
            )
            for region in (first, second)
        }
        editing.apply_ocr_result(third.region_id, "concurrent update")
        try:
            drafts.apply_candidates(
                batch.token, [item.candidate_id for item in candidates]
            )
            raise AssertionError("stale batch unexpectedly applied")
        except DraftError as error:
            assert error.code == "STALE_BASE_REVISION"
        for region in (first, second):
            assert (
                repository.get_region(region.region_id).current_revision_id,
                len(repository.list_revisions(region.region_id)),
            ) == before[region.region_id]
        results["three_region_stale_atomic_rollback"] = "PASS"

        owner_region = new_region(editing)
        owner_base = repository.get_region(owner_region.region_id).current_revision_id
        owner1 = drafts.open_draft(
            "owner-1", "p", owner_region.region_id,
            base_revision_id=owner_base, page_binding_version=1,
        )
        drafts.patch_draft(
            owner1.draft.draft_id, "owner-1",
            {"text": {"edited_translation": "first"}}, schedule_flush=False,
        )
        drafts.transfer_owner(
            "p", owner_region.region_id,
            from_session_id="owner-1", to_session_id="owner-2",
        )
        owner2 = drafts.open_draft(
            "owner-2", "p", owner_region.region_id,
            base_revision_id=owner_base, page_binding_version=1,
        )
        owner_candidate = drafts.prepare_candidate(
            owner_region.region_id, {"style": {"text_color": "#abc"}},
            origin="user", draft_id=owner2.draft.draft_id,
        )
        try:
            drafts.patch_draft(
                owner2.draft.draft_id, "owner-2",
                {"text": {"edited_translation": "second"}}, schedule_flush=False,
            )
            raise AssertionError("text conflict was not detected")
        except DraftError as error:
            assert error.code == "DRAFT_TEXT_CONFLICT"
        try:
            drafts.apply_candidates(owner2.token, [owner_candidate.candidate_id])
            raise AssertionError("conflicted draft unexpectedly applied")
        except DraftError as error:
            assert error.code == "DRAFT_CANDIDATE_INVALID"
        try:
            drafts.resolve_text_conflict(owner1.draft.draft_id, "owner-1", "late")
            raise AssertionError("former owner unexpectedly resolved conflict")
        except DraftError as error:
            assert error.code == "DRAFT_READ_ONLY"
        results["session_conflict_and_owner_gate"] = "PASS"

        recovery_region = new_region(editing)
        recovery_base = repository.get_region(recovery_region.region_id).current_revision_id
        recovery_lease = drafts.open_draft(
            "recovery-session", "p", recovery_region.region_id,
            base_revision_id=recovery_base, page_binding_version=5,
        )
        drafts.patch_draft(
            recovery_lease.draft.draft_id, "recovery-session",
            {"text": {"edited_translation": "intent-recovered"}},
            schedule_flush=False,
        )
        recovery_token = drafts.issue_edit_token(recovery_lease.draft.draft_id)
        recovery_candidate = drafts.prepare_candidate(
            recovery_region.region_id,
            {"text": {"edited_translation": "intent-recovered"}},
            origin="user", draft_id=recovery_lease.draft.draft_id,
        )
        journal.write_receipt = lambda _receipt: (_ for _ in ()).throw(
            DraftJournalError("DRAFT_JOURNAL_UNWRITABLE", "injected receipt failure")
        )
        try:
            drafts.apply_candidates(recovery_token, [recovery_candidate.candidate_id])
            raise AssertionError("receipt failure was not injected")
        except DraftError as error:
            assert error.code == "DRAFT_JOURNAL_UNWRITABLE"
        committed = repository.get_region(recovery_region.region_id).current_revision_id
        assert committed != recovery_base
        assert len(repository.list_revisions(recovery_region.region_id)) == 2
        journal.close()
        conn.close()

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        repository = SqliteRegionRepository(conn)
        journal = DraftJournal(root / "drafts")
        recovered = DraftProtectionService(repository, repository, conn, journal)
        receipt = journal.read_receipt(
            recovery_lease.draft.draft_id, recovery_token.draft_sequence
        )
        assert receipt is not None
        assert receipt["revisionIds"][recovery_region.region_id] == committed
        assert recovered.apply_candidates(recovery_token) == receipt["revisionIds"]
        assert len(repository.list_revisions(recovery_region.region_id)) == 2
        results["receipt_failure_intent_recovery"] = "PASS"
        journal.close()
        conn.close()

    print(json.dumps(results, sort_keys=True))


if __name__ == "__main__":
    main()
