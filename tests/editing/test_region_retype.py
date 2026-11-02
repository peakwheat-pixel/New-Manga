"""Region retype write path (M2-REGION-RETYPE-CORE, contract M2-C1 rev 1.4
§5.4): the 11 two-layer assertions C1-C7 / P1-P4 plus the EV-8 re-snapshot
rule, at the RegionEditingService guard layer.

Contract anchors (rev 1.4 §5.4, frozen):
- retype = ONE new revision through the existing commit seam, origin always
  ``user``, review_state ``UNREVIEWED`` (P3-1);
- snapshot delta vs the pre-retype revision = region_type + sfx_policy ONLY
  (text/style/locks/reading_order/geometry untouched — §10 manual-edit
  protection);
- EV-8 (RULED): retyping TO sfx re-snapshots the policy from the GLOBAL
  sfx.policy configuration at retype time; retyping to any NON-sfx type
  forces SKIP (the policy can never leak onto non-SFX regions,
  core_assembly.py:1036-1045 invariant kept cross-path);
- C4 optimistic guard: expected_revision_no mismatch -> typed
  INPUT_REVISION_CHANGED, zero write;
- C7: unknown / soft-deleted region_id -> RegionNotFound (wire maps it to
  TARGET_NOT_FOUND);
- P1-P4: persistence semantics (SQLite reopen, re-detect idempotent reuse,
  restore, re-retype after restore).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.editing.errors import GuardStatus, RegionNotFound
from application.editing.ports import RegionCommitResult, RegionCommitStatus
from application.editing.service import RegionEditingService
from application.translation.context.gate import decide_sfx_translation
from domain.regions.entities import (
    BBox,
    RegionGeometry,
    RegionOrigin,
    RegionType,
    ReviewState,
    SfxPolicy,
)

from region_helpers import InMemoryRegionRepository

# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


def geo(x=0, y=0, w=10, h=10) -> RegionGeometry:
    return RegionGeometry(bbox=BBox(x, y, w, h))


def make_service() -> tuple[RegionEditingService, InMemoryRegionRepository]:
    repo = InMemoryRegionRepository()
    return RegionEditingService(repo), repo


def make_speech_region(service: RegionEditingService, **kwargs):
    return service.create_region("page-1", geo(), **kwargs)


# ---------------------------------------------------------------------------
# C1 — human priority: the user write channel is not blocked by a running
# machine write (the locked-region shape is where the machine write path is
# stalled); the retype commits immediately as a user revision and the
# already-executed machine decision is not retroactively rewritten.
# ---------------------------------------------------------------------------


def test_c1_human_retype_commits_while_machine_write_is_stalled() -> None:
    service, repo = make_service()
    region = make_speech_region(service, origin=RegionOrigin.MACHINE)
    service.apply_ocr_result(region.region_id, "ドキドキ")  # machine pen: rev 2
    # the machine write path is stalled behind the lock (D06 §89 shape)
    region.translation_locked = True
    repo.update_region(region)

    outcome = service.set_region_type(
        region.region_id, "sfx", current_global_sfx_policy=SfxPolicy.SKIP
    )

    assert outcome.status is GuardStatus.APPLIED
    revisions = repo.list_revisions(region.region_id)
    assert revisions[-1].origin is RegionOrigin.USER
    # the already-executed machine decision stays in history untouched
    assert revisions[1].origin is RegionOrigin.MACHINE
    assert revisions[1].snapshot["text"]["ocr_text"] == "ドキドキ"
    # the user write is NOT blocked by the lock and does not clear it
    assert region.translation_locked is True


# ---------------------------------------------------------------------------
# C2 — AI side fail-closed: revision guard (two-layer ①: service guard return)
# ---------------------------------------------------------------------------


def test_c2_machine_write_after_retype_fails_closed_on_stale_revision() -> None:
    service, repo = make_service()
    region = make_speech_region(service)
    stale_revision_id = region.current_revision_id

    service.set_region_type(
        region.region_id, "sfx", current_global_sfx_policy=SfxPolicy.SKIP
    )
    # the state the machine write must not overwrite = the RETYPED state
    retyped_snapshot = dict(region.snapshot_state())

    outcome = service.apply_machine_translation(
        region.region_id, "翻訳",
        expected_current_revision_id=stale_revision_id,
    )
    assert outcome.status is GuardStatus.INPUT_REVISION_CHANGED
    # fail-closed: not one region field was overwritten
    assert region.snapshot_state() == retyped_snapshot
    assert region.region_type is RegionType.SFX


# ---------------------------------------------------------------------------
# C3 — AI side fail-closed: lock guard (two-layer ①: service guard return);
# the stale-revision expectation outranks the lock (D06 §90 order).
# ---------------------------------------------------------------------------


def test_c3_machine_write_after_retype_fails_closed_on_lock() -> None:
    service, repo = make_service()
    region = make_speech_region(service)
    service.set_region_type(
        region.region_id, "sfx", current_global_sfx_policy=SfxPolicy.SKIP
    )
    # the human protection the machine write must respect after the retype
    region.text.translation_locked = True
    repo.update_region(region)
    snapshot = dict(region.snapshot_state())

    outcome = service.apply_machine_translation(region.region_id, "翻訳")

    assert outcome.status is GuardStatus.LOCK_CHANGED
    assert region.snapshot_state() == snapshot

    # D06 §90: a stale expectation outranks the lock judgement
    outcome_stale = service.apply_machine_translation(
        region.region_id, "翻訳",
        expected_current_revision_id="not-the-current-one",
    )
    assert outcome_stale.status is GuardStatus.INPUT_REVISION_CHANGED


# ---------------------------------------------------------------------------
# C4 — explicit optimistic rejection with zero write
# ---------------------------------------------------------------------------


def test_c4_optimistic_expectation_rejected_with_zero_write() -> None:
    service, repo = make_service()
    region = make_speech_region(service)
    revision_count_before = len(repo.list_revisions(region.region_id))

    outcome = service.set_region_type(
        region.region_id, "sfx",
        current_global_sfx_policy=SfxPolicy.SKIP,
        expected_revision_no=999,
    )

    assert outcome.status is GuardStatus.INPUT_REVISION_CHANGED
    assert len(repo.list_revisions(region.region_id)) == revision_count_before
    assert region.region_type is RegionType.SPEECH


def test_c4_optimistic_expectation_matching_passes_through_the_seam() -> None:
    """The matching expectation is re-checked INSIDE the commit seam (the
    same double-check the guarded machine writes get)."""
    service, repo = make_service()
    region = make_speech_region(service)
    current_no = repo.list_revisions(region.region_id)[-1].revision_no

    outcome = service.set_region_type(
        region.region_id, "sfx",
        current_global_sfx_policy=SfxPolicy.SKIP,
        expected_revision_no=current_no,
    )

    assert outcome.status is GuardStatus.APPLIED
    assert outcome.revision_no == current_no + 1


# ---------------------------------------------------------------------------
# C5 — post-retype decisions are taken from the region's own retyped fields
# (gate consumes the region snapshot, gate.py:32-42).
# ---------------------------------------------------------------------------


def test_c5_post_retype_decision_follows_retyped_fields() -> None:
    service, _ = make_service()
    region = make_speech_region(service)

    # speech -> sfx with the global config on translate: the SFX chain opens
    service.set_region_type(
        region.region_id, "sfx", current_global_sfx_policy=SfxPolicy.TRANSLATE
    )
    action = decide_sfx_translation(
        region.region_type.value, region.sfx_policy.value
    )
    assert action.status == "translate"

    # sfx + the forced-SKIP snapshot keeps the original artwork text
    service.set_region_type(
        region.region_id, "sfx", current_global_sfx_policy=SfxPolicy.SKIP
    )
    action = decide_sfx_translation(
        region.region_type.value, region.sfx_policy.value
    )
    assert action.skipped is True

    # sfx -> speech: the region is back on the dialogue chain (the gate
    # consumes the retyped TYPE, so the forced-SKIP snapshot it carried as
    # an sfx region no longer skips anything)
    service.set_region_type(
        region.region_id, "speech", current_global_sfx_policy=SfxPolicy.TRANSLATE
    )
    action = decide_sfx_translation(
        region.region_type.value, region.sfx_policy.value
    )
    assert action.status == "translate"


# ---------------------------------------------------------------------------
# C6 — a human retype over a machine retyped region stacks a user revision;
# the machine pen stays in history and the undo path restores it (restored).
# ---------------------------------------------------------------------------


def test_c6_human_retype_over_machine_pen_keeps_history_and_restores() -> None:
    service, repo = make_service()
    region = make_speech_region(service, origin=RegionOrigin.MACHINE)

    service.set_region_type(
        region.region_id, "sfx", current_global_sfx_policy=SfxPolicy.SKIP
    )
    revisions = repo.list_revisions(region.region_id)
    assert revisions[-1].origin is RegionOrigin.USER
    assert revisions[0].origin is RegionOrigin.MACHINE  # machine pen kept
    assert region.region_type is RegionType.SFX

    # undo = RestoreRegionRevision semantics: a restored revision pointing
    # back at the machine pen — never a second retype
    service.restore_revision(region.region_id, revisions[0].revision_no)
    revisions = repo.list_revisions(region.region_id)
    assert revisions[-1].origin is RegionOrigin.RESTORED
    assert revisions[-1].restored_from_revision_id == revisions[0].region_revision_id
    assert region.region_type is RegionType.SPEECH


# ---------------------------------------------------------------------------
# C7 — unknown / soft-deleted targets
# ---------------------------------------------------------------------------


def test_c7_unknown_region_id_raises_region_not_found() -> None:
    service, _ = make_service()
    with pytest.raises(RegionNotFound):
        service.set_region_type(
            "no-such-region", "sfx", current_global_sfx_policy=SfxPolicy.SKIP
        )


def test_c7_soft_deleted_region_id_raises_region_not_found() -> None:
    service, _ = make_service()
    region = make_speech_region(service)
    service.delete_region(region.region_id)
    with pytest.raises(RegionNotFound):
        service.set_region_type(
            region.region_id, "sfx", current_global_sfx_policy=SfxPolicy.SKIP
        )


# ---------------------------------------------------------------------------
# EV-8 (RULED): retype-to-sfx re-snapshots the GLOBAL config at retype time;
# retype to any non-sfx type forces SKIP.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("global_policy", "expected_policy"),
    [
        (SfxPolicy.TRANSLATE, SfxPolicy.TRANSLATE),
        (SfxPolicy.MANUAL, SfxPolicy.MANUAL),
        (SfxPolicy.SKIP, SfxPolicy.SKIP),
    ],
)
def test_ev8_sfx_retype_re_snapshots_the_global_config(
    global_policy, expected_policy
) -> None:
    service, repo = make_service()
    region = make_speech_region(service)

    service.set_region_type(
        region.region_id, "sfx", current_global_sfx_policy=global_policy
    )

    assert region.sfx_policy is expected_policy
    revision = repo.list_revisions(region.region_id)[-1]
    assert revision.snapshot["sfx_policy"] == expected_policy.value


def test_ev8_non_sfx_retype_forces_skip_even_over_a_translate_snapshot() -> None:
    """The leak-onward invariant: a region created as sfx+translate (the
    global config at creation time) retyped back to speech must land on
    SKIP — the policy can never leak onto non-SFX regions."""
    service, repo = make_service()
    region = make_speech_region(
        service, region_type=RegionType.SFX, sfx_policy=SfxPolicy.TRANSLATE
    )

    service.set_region_type(
        region.region_id, "speech", current_global_sfx_policy=SfxPolicy.TRANSLATE
    )

    assert region.region_type is RegionType.SPEECH
    assert region.sfx_policy is SfxPolicy.SKIP
    revision = repo.list_revisions(region.region_id)[-1]
    assert revision.snapshot["sfx_policy"] == SfxPolicy.SKIP.value


# ---------------------------------------------------------------------------
# write-shape invariants: ONE revision via the commit seam, snapshot delta =
# region_type + sfx_policy ONLY, review_state UNREVIEWED, text protection.
# ---------------------------------------------------------------------------


def test_retype_snapshot_changes_only_type_and_policy() -> None:
    service, repo = make_service()
    region = make_speech_region(service)
    service.apply_ocr_result(region.region_id, "セリフ")
    service.save_manual_translation(region.region_id, "台词")
    before = repo.list_revisions(region.region_id)[-1].snapshot

    service.set_region_type(
        region.region_id, "sfx", current_global_sfx_policy=SfxPolicy.TRANSLATE
    )

    after = repo.list_revisions(region.region_id)[-1].snapshot
    assert set(after.keys()) == set(before.keys())
    for key in after:
        if key == "region_type":
            # the retype IS the type change
            assert after[key] != before[key]
            continue
        if key == "sfx_policy":
            # may or may not change (the retype-time global config can equal
            # the previous revision's value) — no assertion, only recorded
            continue
        assert after[key] == before[key], f"field {key} must survive a retype"
    # the confirmed manual translation is NOT wiped and does NOT fall back
    # to needs-review (the retype never changes text content)
    assert after["text"]["edited_translation"] == "台词"
    assert after["text"]["edited_confirmed"] == before["text"]["edited_confirmed"]


def test_retype_creates_user_revision_with_unreviewed_state() -> None:
    service, repo = make_service()
    region = make_speech_region(service)

    outcome = service.set_region_type(
        region.region_id, "sfx", current_global_sfx_policy=SfxPolicy.SKIP
    )

    revision = repo.list_revisions(region.region_id)[-1]
    assert outcome.revision_no == revision.revision_no
    assert revision.origin is RegionOrigin.USER
    assert revision.review_state is ReviewState.UNREVIEWED


# ---------------------------------------------------------------------------
# AC4 read channel: the RegionListSummary minimal DTO (service side)
# ---------------------------------------------------------------------------


def test_list_region_summaries_minimal_dto_in_reading_order() -> None:
    service, _ = make_service()
    machine_region = service.create_region(
        "page-1", geo(), reading_order=3, origin=RegionOrigin.MACHINE
    )
    first = service.create_region("page-1", geo(), reading_order=1)
    service.set_region_type(
        first.region_id, "sfx", current_global_sfx_policy=SfxPolicy.TRANSLATE
    )

    summaries = service.list_region_summaries("page-1")

    assert [s["region_id"] for s in summaries] == [first.region_id, machine_region.region_id]
    assert summaries[0] == {
        "region_id": first.region_id,
        "region_type": "sfx",
        "sfx_policy": "translate",
        "origin": "user",
        "revision_no": 2,
    }
    # machine-created regions stay distinguishable from human retypes (A7)
    assert summaries[1]["origin"] == "machine"  # created with origin=MACHINE
    # the minimal set: no geometry/text/annotation semantics on the read face
    assert set(summaries[0].keys()) == {
        "region_id", "region_type", "sfx_policy", "origin", "revision_no",
    }


def test_list_region_summaries_empty_for_page_without_regions() -> None:
    service, _ = make_service()
    assert service.list_region_summaries("no-such-page") == []


# ---------------------------------------------------------------------------
# P1 — reopen persistence (SQLite: the process-restart shape)
# ---------------------------------------------------------------------------


def test_p1_reopen_persists_retype_full_state(tmp_path) -> None:
    from infrastructure.sqlite.connection import open_database
    from infrastructure.sqlite.migrator import MigrationRunner
    from infrastructure.sqlite.regions import SqliteRegionRepository
    from infrastructure.sqlite.schema import default_migrations

    db_path = tmp_path / "regions.db"
    conn, _ = open_database(
        db_path,
        latest_known_schema_version=max(
            m.schema_version for m in default_migrations()
        ),
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    now = "2026-01-01T00:00:00.000+00:00"
    with conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-1', 't', ?, ?)",
            (now, now),
        )
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at,"
            " updated_at) VALUES ('chapter-1', 'book-1', 'c', ?, ?)",
            (now, now),
        )
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, sort_order, created_at,"
            " updated_at) VALUES ('page-1', 'chapter-1', 0, ?, ?)",
            (now, now),
        )
    repo = SqliteRegionRepository(conn)
    service = RegionEditingService(repo, committer=repo)
    region = service.create_region("page-1", geo())
    service.set_region_type(
        region.region_id, "sfx", current_global_sfx_policy=SfxPolicy.TRANSLATE
    )
    region_id = region.region_id

    # "restart": fresh connection + fresh service over the same database
    conn.close()
    conn2, _ = open_database(
        db_path,
        latest_known_schema_version=max(
            m.schema_version for m in default_migrations()
        ),
    )
    try:
        repo2 = SqliteRegionRepository(conn2)
        service2 = RegionEditingService(repo2, committer=repo2)

        summaries = service2.list_region_summaries("page-1")
        assert summaries == [
            {
                "region_id": region_id,
                "region_type": "sfx",
                "sfx_policy": "translate",
                "origin": "user",
                "revision_no": 2,
            }
        ]
        revisions = repo2.list_revisions(region_id)
        assert [rev.origin for rev in revisions] == [
            RegionOrigin.USER,
            RegionOrigin.USER,
        ]
    finally:
        conn2.close()


# ---------------------------------------------------------------------------
# P3 — restore recovers the full pre-retype state, history untouched
# ---------------------------------------------------------------------------


def test_p3_restore_recovers_pre_retype_state_and_keeps_history() -> None:
    service, repo = make_service()
    region = make_speech_region(service, origin=RegionOrigin.MACHINE)
    pre_retype_no = repo.list_revisions(region.region_id)[-1].revision_no
    pre_retype_snapshot = dict(repo.list_revisions(region.region_id)[-1].snapshot)

    service.set_region_type(
        region.region_id, "sfx", current_global_sfx_policy=SfxPolicy.TRANSLATE
    )
    service.restore_revision(region.region_id, pre_retype_no)

    revisions = repo.list_revisions(region.region_id)
    assert region.region_type is RegionType.SPEECH
    assert region.sfx_policy is SfxPolicy.SKIP
    assert region.snapshot_state() == pre_retype_snapshot
    assert revisions[-1].origin is RegionOrigin.RESTORED
    # no revision was deleted or rewritten
    assert [rev.revision_no for rev in revisions] == [1, 2, 3]


# ---------------------------------------------------------------------------
# P4 — retype after restore reapplies the EV-8 rule fresh (no residue from
# the undone chain)
# ---------------------------------------------------------------------------


def test_p4_retype_after_restore_reapplies_ev8_with_current_config() -> None:
    service, repo = make_service()
    region = make_speech_region(service)
    pre_retype_no = repo.list_revisions(region.region_id)[-1].revision_no

    # retype under translate, undo, then retype under a CHANGED global config
    service.set_region_type(
        region.region_id, "sfx", current_global_sfx_policy=SfxPolicy.TRANSLATE
    )
    service.restore_revision(region.region_id, pre_retype_no)
    service.set_region_type(
        region.region_id, "sfx", current_global_sfx_policy=SfxPolicy.SKIP
    )

    revisions = repo.list_revisions(region.region_id)
    assert region.region_type is RegionType.SFX
    assert region.sfx_policy is SfxPolicy.SKIP  # the re-retype-time config
    assert revisions[-1].origin is RegionOrigin.USER
    assert revisions[-1].review_state is ReviewState.UNREVIEWED


# ---------------------------------------------------------------------------
# DSH r1 P2-2 / P4-3 — the retype's non-APPLIED seam outcomes are explicit:
# the typed conflict (INPUT_REVISION_CHANGED) stays a conflict OUTCOME, while
# DB_FAILED / LOCK_CHANGED escalate fail-loud (a human retype never degrades
# into a machine-write candidate). The committers below are fakes over the
# REAL seam result protocol (application.editing.ports.RegionCommitResult) —
# the actual persistence-failure reporting path, not a pre-raised exception.
# ---------------------------------------------------------------------------


class _DbFailedCommitter:
    """Reports the seam's genuine persistence-failure status (DB_FAILED),
    exactly how the SQLite seam reports a failed BEGIN IMMEDIATE."""

    def commit_region_revision(
        self, region, revision, *, expected_current_revision_id=None, lock_snapshot=None
    ) -> RegionCommitResult:
        return RegionCommitResult(
            RegionCommitStatus.DB_FAILED,
            detail="simulated persistence failure inside the seam",
        )


class _LockChangedCommitter:
    """Reports the seam's lock-recheck failure (LOCK_CHANGED) — unreachable
    on the user channel in practice (no lock snapshot is passed), so the
    retype path must escalate rather than map it onto a candidate."""

    def commit_region_revision(
        self, region, revision, *, expected_current_revision_id=None, lock_snapshot=None
    ) -> RegionCommitResult:
        return RegionCommitResult(
            RegionCommitStatus.LOCK_CHANGED,
            detail="simulated mid-flight lock change inside the seam",
        )


class _SeamRecheckLostCommitter:
    """Loses the optimistic guard INSIDE the seam (the re-check the matching
    expectation gets): reports INPUT_REVISION_CHANGED with zero write."""

    def commit_region_revision(
        self, region, revision, *, expected_current_revision_id=None, lock_snapshot=None
    ) -> RegionCommitResult:
        return RegionCommitResult(
            RegionCommitStatus.INPUT_REVISION_CHANGED,
            detail=(
                f"expected current {expected_current_revision_id!r},"
                " stored current moved mid-flight"
            ),
        )


def test_r1_p2_2_db_failed_seam_escalates_runtime_error_with_zero_write() -> None:
    service, repo = make_service()
    region = make_speech_region(service)
    revision_count_before = len(repo.list_revisions(region.region_id))
    failing = RegionEditingService(repo, committer=_DbFailedCommitter())

    with pytest.raises(RuntimeError, match="db_failed"):
        failing.set_region_type(
            region.region_id, "sfx", current_global_sfx_policy=SfxPolicy.SKIP
        )

    # the persistence fault never produced a revision or a conflict outcome
    assert len(repo.list_revisions(region.region_id)) == revision_count_before
    assert region.region_type is RegionType.SPEECH


def test_r1_p2_2_lock_changed_seam_escalates_runtime_error_with_zero_write() -> None:
    service, repo = make_service()
    region = make_speech_region(service)
    revision_count_before = len(repo.list_revisions(region.region_id))
    failing = RegionEditingService(repo, committer=_LockChangedCommitter())

    with pytest.raises(RuntimeError, match="lock_changed"):
        failing.set_region_type(
            region.region_id, "sfx", current_global_sfx_policy=SfxPolicy.SKIP
        )

    assert len(repo.list_revisions(region.region_id)) == revision_count_before


def test_r1_p4_3_seam_recheck_loss_is_typed_input_revision_changed_zero_write() -> None:
    """The in-seam optimistic re-check losing (C4 double-check) stays a typed
    conflict OUTCOME — not an exception, not a silent no-op, zero write."""
    service, repo = make_service()
    region = make_speech_region(service)
    current_no = repo.list_revisions(region.region_id)[-1].revision_no
    revision_count_before = len(repo.list_revisions(region.region_id))
    guarded = RegionEditingService(repo, committer=_SeamRecheckLostCommitter())

    outcome = guarded.set_region_type(
        region.region_id, "sfx",
        current_global_sfx_policy=SfxPolicy.SKIP,
        expected_revision_no=current_no,
    )

    assert outcome.status is GuardStatus.INPUT_REVISION_CHANGED
    assert len(repo.list_revisions(region.region_id)) == revision_count_before
    assert region.region_type is RegionType.SPEECH
