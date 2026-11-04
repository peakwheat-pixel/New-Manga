"""Each failure independently asserts the live/revision/success-receipt boundary."""
import json

import pytest

from tests.fea10.test_prepared_run import workspace
from tests.core.test_fea00a_pipeline_seam import (
    _new_workspace, _prepare_ocr, _region_snapshot, _candidate, _assemble,
)
from domain.tasks.models import PipelineError


@pytest.mark.parametrize('fault', [
    'revision', 'lock', 'manual', 'final', 'stale_run', 'source_lease', 'binding_generation',
    'draft_sequence', 'db', 'pause', 'cancel', 'crash_restart',
])
def test_each_failed_seam_preserves_live_and_success_receipts(fault):
    root = workspace('zero-' + fault)
    core, _, region = _new_workspace(root)
    try:
        run, step, _, result = _prepare_ocr(core, region, running=True)
        candidate_id = result.revision_updates['region']
        if fault == 'revision': core.editing.set_region_type(region, 'sfx', current_global_sfx_policy='skip')
        elif fault == 'lock':
            with core.conn: core.conn.execute('UPDATE regions SET region_locked=1 WHERE region_id=?', (region,))
        elif fault in ('manual', 'final'):
            row = core.conn.execute('SELECT text_json FROM regions WHERE region_id=?', (region,)).fetchone()
            text = json.loads(row[0]); text['manual_edited' if fault == 'manual' else 'edited_confirmed'] = True
            with core.conn: core.conn.execute('UPDATE regions SET text_json=? WHERE region_id=?', (json.dumps(text), region))
        elif fault == 'stale_run':
            def fail(_): raise PipelineError('STALE_RUN_SNAPSHOT', 'injected stale Run')
            core.pipeline._store._check_write_revision = fail
        elif fault == 'source_lease':
            from contextlib import contextmanager
            @contextmanager
            def fail(_):
                raise RuntimeError('source lease expired')
                yield
            core.pipeline._catalog.source_commit_guard = fail
        elif fault in ('binding_generation', 'draft_sequence'):
            core.pipeline._catalog.guard_reader = lambda _: {fault: 'changed'}
        elif fault == 'db':
            core.conn.execute("CREATE TEMP TRIGGER fea10_fail BEFORE INSERT ON region_revisions BEGIN SELECT RAISE(ABORT, 'injected DB failure'); END")
        elif fault in ('pause', 'cancel'): core.pipeline.control_run(run.run_id, 'pause' if fault == 'pause' else 'stop')
        before = _region_snapshot(core, region)
        completed_before = core.conn.execute("SELECT COUNT(*) FROM step_runs WHERE status='completed'").fetchone()[0]
        if fault == 'crash_restart':
            core.conn.close(); core = _assemble(root)
        else:
            outcome = core.pipeline.commit_step_result(step.step_run_id, result)
            assert outcome.status != 'committed'
        assert _region_snapshot(core, region) == before
        assert core.conn.execute("SELECT COUNT(*) FROM step_runs WHERE status='completed'").fetchone()[0] == completed_before
        assert core.pipeline.get_task_projection(run.run_id, fresh=True).completed_page_count == 0
        assert _candidate(core, candidate_id)['status'] == 'abandoned'
    finally: core.conn.close()


def test_success_live_revision_and_run_receipt_share_one_transaction():
    core, _, region = _new_workspace(workspace('commit-success'))
    try:
        run, step, _, result = _prepare_ocr(core, region, running=True)
        trace = []; core.conn.set_trace_callback(trace.append)
        outcome = core.pipeline.commit_step_result(step.step_run_id, result)
        core.conn.set_trace_callback(None)
        assert outcome.status == 'committed'
        assert sum(sql.upper() == 'BEGIN IMMEDIATE' for sql in trace) == 1
        assert sum(sql.upper() == 'COMMIT' for sql in trace) == 1
        assert _region_snapshot(core, region)[1] == result.revision_updates['region']
        assert core.pipeline.get_run_snapshot(run.run_id, fresh=True).step_runs[-1].status.value == 'completed'
    finally: core.conn.close()


@pytest.mark.parametrize('stale_last', [False, True])
def test_editing_multi_region_apply_uses_existing_guarded_batch(stale_last):
    from domain.regions.entities import BBox, RegionGeometry
    from application.editing.errors import DraftError
    core, page, first = _new_workspace(workspace('editing-batch'))
    try:
        ids = [first] + [core.editing.create_region(page, RegionGeometry(bbox=BBox(1, 1, 4, 4)), reading_order=i).region_id
                         for i in (2, 3)]
        lease = core.drafts.open_draft('fea10-edit', page, None, base_revision_id=None, page_binding_version=1)
        candidates = [core.drafts.prepare_candidate(region, {'text': {'edited_translation': 'edited'}},
                      origin='user', draft_id=lease.draft.draft_id) for region in ids]
        if stale_last:
            core.editing.set_region_type(ids[-1], 'sfx', current_global_sfx_policy='skip')
        before = [_region_snapshot(core, region) for region in ids]
        trace = []; core.conn.set_trace_callback(trace.append)
        if stale_last:
            with pytest.raises(DraftError) as caught:
                core.drafts.apply_candidates(lease.token, [item.candidate_id for item in candidates])
            assert caught.value.code == 'STALE_BASE_REVISION'
            assert [_region_snapshot(core, region) for region in ids] == before
        else:
            result = core.drafts.apply_candidates(lease.token, [item.candidate_id for item in candidates])
            assert set(result) == set(ids)
            assert sum(sql.upper() == 'BEGIN IMMEDIATE' for sql in trace) == 1
            assert all(_region_snapshot(core, region)[2] == old[2] + 1 for region, old in zip(ids, before))
        assert core.conn.execute('SELECT COUNT(*) FROM step_result_candidates').fetchone()[0] == 0
    finally:
        core.conn.set_trace_callback(None)
        core.conn.close()


def test_actual_draft_change_after_step_start_blocks_pipeline_commit():
    core, page, region = _new_workspace(workspace('active-draft-guard'))
    try:
        run, step, _, result = _prepare_ocr(core, region, running=True)
        core.drafts.open_draft('new-owner', page, region, base_revision_id=_region_snapshot(core, region)[1], page_binding_version=1)
        before = _region_snapshot(core, region)
        assert core.pipeline.commit_step_result(step.step_run_id, result).status == 'candidate'
        assert _region_snapshot(core, region) == before
        assert core.pipeline.get_task_projection(run.run_id, fresh=True).completed_page_count == 0
    finally: core.conn.close()


def test_edit_token_and_sequence_mismatch_preserves_live_and_candidate():
    from dataclasses import replace
    from application.editing.errors import DraftError
    core, page, region = _new_workspace(workspace('token-sequence'))
    try:
        lease = core.drafts.open_draft('fea10-token', page, region,
            base_revision_id=_region_snapshot(core, region)[1], page_binding_version=1)
        candidate = core.drafts.prepare_candidate(region, {'text': {'edited_translation': 'candidate'}},
                    origin='user', draft_id=lease.draft.draft_id)
        before = _region_snapshot(core, region)
        forged = replace(lease.token, draft_sequence=lease.token.draft_sequence + 1)
        with pytest.raises(DraftError) as caught:
            core.drafts.apply_candidates(forged, [candidate.candidate_id])
        assert caught.value.code == 'EDIT_TOKEN_INVALID'
        assert _region_snapshot(core, region) == before
        assert candidate.candidate_id in core.drafts._candidates
        assert core.conn.execute("SELECT COUNT(*) FROM step_runs WHERE status='completed'").fetchone()[0] == 0
    finally: core.conn.close()
