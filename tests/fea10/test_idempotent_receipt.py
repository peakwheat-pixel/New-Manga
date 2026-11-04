import subprocess
import sys

import pytest

from tests.fea10.test_prepared_run import workspace, prepare
from tests.core.test_fea00a_pipeline_seam import _new_workspace
from domain.tasks.models import PipelineError


def test_committed_ack_loss_replays_before_expiry_or_config_reads():
    core, _, region = _new_workspace(workspace('receipt-replay'))
    try:
        preview, scope = prepare(core, region)
        run, created = core.pipeline.accept_prepared_run(preview, scope, idempotency_key='ack')
        assert created
        preview['expiresAt'] = '2000-01-01T00:00:00+00:00'
        core.pipeline_defaults.save_settings_section('ocr', {'script': 'chinese'})
        replay, created = core.pipeline.accept_prepared_run(preview, scope, idempotency_key='ack')
        assert replay.run_id == run.run_id and not created
        assert len(core.pipeline._store.list_ids()) == 1
        preview['overrides'] = {'ocr': {'script': 'korean'}}
        with pytest.raises(PipelineError, match='IDEMPOTENCY_KEY_REUSED'):
            core.pipeline.accept_prepared_run(preview, scope, idempotency_key='ack')
    finally: core.conn.close()


def test_same_request_correlation_does_not_deduplicate_different_keys():
    core, _, region = _new_workspace(workspace('receipt-two-keys'))
    try:
        preview, scope = prepare(core, region)
        a, _ = core.pipeline.accept_prepared_run(preview, scope, idempotency_key='a')
        b, _ = core.pipeline.accept_prepared_run(preview, scope, idempotency_key='b')
        assert a.run_id != b.run_id and len(core.pipeline._store.list_ids()) == 2
    finally: core.conn.close()


def test_stop_and_start_are_separate_processes_using_same_database():
    root = workspace('receipt-process-restart')
    for action in ('--stop', '--start'):
        command = [sys.executable, 'tests/fea10/support/restart_core.py', '--data-root', str(root), '--db', str(root / 'library.db'), action]
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        assert result.returncode == 0, result.stdout + result.stderr
        assert 'DataRoot=' in result.stdout


def test_restart_receipt_survives_reopening_same_database():
    from tests.core.test_fea00a_pipeline_seam import _assemble
    from domain.tasks.models import PipelineRunStatus
    root = workspace('control-restart-receipt')
    core, _, region = _new_workspace(root)
    preview, scope = prepare(core, region)
    parent, _ = core.pipeline.accept_prepared_run(preview, scope, idempotency_key='restart-parent')
    parent.status = PipelineRunStatus.INTERRUPTED
    core.pipeline._persist(parent)
    child_id = core.pipeline.control_run(parent.run_id, 'restart', idempotency_key='restart-operation').new_run_id
    core.conn.close()
    reopened = _assemble(root)
    try:
        replay = reopened.pipeline.control_run(parent.run_id, 'restart', idempotency_key='restart-operation')
        assert replay.new_run_id == child_id
        assert len(reopened.pipeline._store.list_ids()) == 2
    finally: reopened.conn.close()


def test_same_wire_request_id_different_keys_are_distinct_operations():
    import io
    import json
    from bootstrap.core_service import CoreServiceServer
    core, page, _ = _new_workspace(workspace('wire-correlation'))
    server = CoreServiceServer(core, stdout=io.StringIO())
    try:
        results = []
        for key in ('wire-a', 'wire-b'):
            response, _ = server.dispatch_request(json.dumps({
                'protocol': 'new-manga.core', 'version': {'major': 2, 'minor': 3},
                'request_id': 'same-correlation', 'command': 'StartRun',
                'payload': {'command': 'reocr_single', 'scope': {'kind': 'page', 'page_id': page}, 'idempotency_key': key},
            }))
            assert response['error'] is None
            assert response['request_id'] == 'same-correlation'
            results.append(response['result']['run_id'])
        assert results[0] != results[1]
    finally:
        server.close()
        core.conn.close()
