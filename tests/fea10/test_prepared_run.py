"""FEA-10 two-phase acceptance over the production SQLite assembly."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import uuid

import pytest

from tests.core.test_fea00a_pipeline_seam import _new_workspace
from application.tasks.store import snapshot_digest
from domain.tasks.models import PipelineError, PipelineScope, ScopeType


def workspace(case):
    root = Path('G:/CODEX/New Manga.workspace/FEA-10/fixtures') / (case + '-' + uuid.uuid4().hex)
    root.mkdir(parents=True)
    return root


def prepare(core, region):
    scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
    return core.pipeline.prepare_run('ocr_region', scope), scope


def test_prepare_is_read_only_and_accept_digest_is_exact_quartet():
    core, _, region = _new_workspace(workspace('prepared-quartet'))
    try:
        statements = []
        core.conn.set_trace_callback(statements.append)
        before = core.conn.total_changes
        prepared, scope = prepare(core, region)
        assert core.conn.total_changes == before
        assert not any(sql.lstrip().upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'BEGIN')) for sql in statements)
        assert core.pipeline._store.list_ids() == ()
        quartet = {key: prepared[key] for key in ('requestedTargets', 'settingsSnapshot', 'providerBindingSnapshot', 'constraintSnapshotRef')}
        expected = 'sha256:' + hashlib.sha256(json.dumps(quartet, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        assert prepared['preparedDigest'] == prepared['snapshotDigest'] == expected
        core.conn.set_trace_callback(None)
        run, created = core.pipeline.accept_prepared_run(prepared, scope, idempotency_key='accept-1')
        assert created and run.status.value == 'pending'
        assert len(core.pipeline._store.list_ids()) == 1
    finally:
        core.conn.set_trace_callback(None)
        core.conn.close()


@pytest.mark.parametrize('change,code', [('digest', 'RUN_STALE_PREVIEW'), ('settings', 'RUN_STALE_PREVIEW'),
    ('lock', 'RUN_STALE_PREVIEW'), ('revision', 'RUN_STALE_PREVIEW'), ('expired', 'RUN_PREVIEW_EXPIRED'),
    ('missing', 'RUN_SNAPSHOT_INCOMPLETE')])
def test_invalid_preview_is_rejected_without_writes(change, code):
    core, _, region = _new_workspace(workspace('stale-' + change))
    try:
        prepared, scope = prepare(core, region)
        if change == 'digest': prepared['preparedDigest'] = 'sha256:' + '0' * 64
        elif change == 'settings': core.pipeline_defaults.save_settings_section('ocr', {'script': 'chinese'})
        elif change == 'lock':
            with core.conn: core.conn.execute('UPDATE regions SET region_locked=1 WHERE region_id=?', (region,))
        elif change == 'revision': core.editing.set_region_type(region, 'sfx', current_global_sfx_policy='skip')
        elif change == 'expired': prepared['expiresAt'] = '2000-01-01T00:00:00+00:00'
        else: prepared.pop('settingsSnapshot')
        before = core.conn.total_changes
        with pytest.raises(PipelineError) as caught:
            core.pipeline.accept_prepared_run(prepared, scope, idempotency_key='invalid')
        assert caught.value.code == code
        assert core.conn.total_changes == before
        assert core.pipeline._store.list_ids() == ()
    finally: core.conn.close()


def test_prepared_schema_rejects_unknown_settings_before_candidate_escape():
    core, _, region = _new_workspace(workspace('snapshot-safety'))
    try:
        core.pipeline_defaults.save_settings_section('untyped', {'unregistered': 'value'})
        with pytest.raises(PipelineError, match='RUN_SNAPSHOT_INCOMPLETE'):
            prepare(core, region)
        assert core.pipeline._store.list_ids() == ()
    finally: core.conn.close()
