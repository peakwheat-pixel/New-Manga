from tests.fea10.test_prepared_run import workspace
from tests.core.test_fea00a_pipeline_seam import _new_workspace
from domain.tasks.models import PipelineRunStatus, PipelineScope, PipelineTaskStatus, ScopeType


def test_new_retry_freezes_current_context_but_same_key_replays_unchanged():
    core, page, region = _new_workspace(workspace('retry-context'))
    try:
        pipeline = core.pipeline
        parent = pipeline.create_run('reocr_single', PipelineScope(ScopeType.PAGE, selected_ids=(page,)))
        pipeline.plan_run(parent.run_id)
        parent.status = PipelineRunStatus.COMPLETED_WITH_FAILURES
        parent.tasks[0].status = PipelineTaskStatus.FAILED
        pipeline._persist(parent)
        old_settings = parent.settings_snapshot
        core.editing.set_region_type(region, 'sfx', current_global_sfx_policy='skip')
        live_revision = pipeline._catalog.current(region).current_revisions['region']
        core.pipeline_defaults.save_settings_section('ocr', {'script': 'chinese'})
        child, created = pipeline.accept_retry_failed_targets(parent.run_id, 'retry-a')
        assert created and child.source_run_id == parent.run_id
        assert {target.page_id for target in child.targets} == {page}
        assert child.targets[0].snapshot.regions[0].current_revisions['region'] == live_revision
        assert child.settings_snapshot['ocr']['script'] == 'chinese'
        core.pipeline_defaults.save_settings_section('ocr', {'script': 'korean'})
        replay, created = pipeline.accept_retry_failed_targets(parent.run_id, 'retry-a')
        assert not created and replay.run_id == child.run_id
        assert replay.settings_snapshot['ocr']['script'] == 'chinese'
        assert parent.settings_snapshot == old_settings
    finally: core.conn.close()


def test_neighbour_context_is_pinned_and_pre_accept_change_is_stale():
    import json
    import pytest
    from application.importing.images.ports import ImportSource
    from domain.regions.entities import BBox, RegionGeometry
    from domain.tasks.models import PipelineError
    from tests.core.test_fea00a_pipeline_seam import _png, _prepare_ocr
    core, page, region = _new_workspace(workspace('neighbour-pin'))
    try:
        chapter = core.pipeline._catalog.current(page).chapter_id
        second_page = core.importer.import_files(chapter, [ImportSource(filename='neighbor.png', data_provider=_png)], duplicate_policy='import_as_new').imported[0].page
        neighbor = core.editing.create_region(second_page.page_id, RegionGeometry(bbox=BBox(1, 1, 6, 6)), reading_order=1).region_id
        for target in (region, neighbor):
            _, step, _, result = _prepare_ocr(core, target)
            assert core.pipeline.commit_step_result(step.step_run_id, result).status == 'committed'
        core.pipeline_defaults.save_provider_binding('translate', 'm2ac1-mock-translate')
        scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
        preview = core.pipeline.prepare_run('retranslate_region', scope)
        row = core.conn.execute('SELECT text_json FROM regions WHERE region_id=?', (neighbor,)).fetchone()
        text = json.loads(row[0]); text['ocr_text'] = 'changed neighbour'
        with core.conn: core.conn.execute('UPDATE regions SET text_json=? WHERE region_id=?', (json.dumps(text), neighbor))
        with pytest.raises(PipelineError, match='RUN_STALE_PREVIEW'):
            core.pipeline.accept_prepared_run(preview, scope, idempotency_key='stale-neighbor')
        accepted_preview = core.pipeline.prepare_run('retranslate_region', scope)
        run, _ = core.pipeline.accept_prepared_run(accepted_preview, scope, idempotency_key='frozen-neighbor')
        context = run.targets[0].snapshot.metadata['context_pages'][0]
        assert context['text'] == 'changed neighbour'
        text['ocr_text'] = 'newer neighbour'
        with core.conn: core.conn.execute('UPDATE regions SET text_json=? WHERE region_id=?', (json.dumps(text), neighbor))
        core.pipeline.plan_run(run.run_id)
        task = run.tasks[0]; unit = next(item for item in task.units if item.step_type == 'translate')
        step = core.pipeline.record_step_attempt(task.task_id, 'translate')
        result = core.pipeline._executor.execute(step, unit, run)
        assert result.outputs['provenance']['payloadDigestSend'] == accepted_preview['redactedPayloadPreview']['requests'][0]['payloadDigestPreview']
        assert run.targets[0].snapshot.metadata['context_pages'][0]['text'] == 'changed neighbour'
    finally: core.conn.close()


def test_preview_and_real_transport_body_use_same_builder_and_pinned_config():
    import json
    from dataclasses import replace
    from tests.core.test_fea00a_pipeline_seam import _prepare_ocr
    from infrastructure.providers.registry import ProviderDescriptor
    from infrastructure.providers.translation_openai import OpenAiTranslationProvider
    from infrastructure.providers.openai_client import OpenAiCompatibleClient, OpenAiCompatibleConfig
    from application.tasks.store import snapshot_digest
    from ports.network.transport import TransportOutcome, TransportResponse

    core, _, region = _new_workspace(workspace('canonical-request'))
    try:
        _, ocr, _, ocr_result = _prepare_ocr(core, region)
        assert core.pipeline.commit_step_result(ocr.step_run_id, ocr_result).status == 'committed'
        calls = []
        class Transport:
            def send(self, request, profile):
                calls.append(request)
                body = {'choices': [{'message': {'content': json.dumps({'translations': [
                    {'region_id': region, 'translated_text': 'translated'}]})}}]}
                return TransportOutcome(TransportResponse(status=200, body=json.dumps(body).encode()))
        config = OpenAiCompatibleConfig('fea10-remote', 'openai-compatible', base_url='https://fixture.invalid/v1', model='pinned-model')
        provider = OpenAiTranslationProvider(config, OpenAiCompatibleClient(config, Transport()), provider_id='fea10-remote')
        core.providers.registry.register(ProviderDescriptor('fea10-remote', 'openai-compatible', frozenset({'translation'})), lambda: provider)
        core.pipeline_defaults.save_provider_binding('translate', 'fea10-remote')
        scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
        prepared = core.pipeline.prepare_run('retranslate_region', scope)
        assert calls == []
        expected = prepared['redactedPayloadPreview']['requests'][0]['payloadDigestPreview']
        run, _ = core.pipeline.accept_prepared_run(prepared, scope, idempotency_key='canonical')
        # Simulate runtime defaults/instance changes after acceptance.
        provider.config = replace(config, base_url='https://changed.invalid/v1', model='changed-model')
        core.pipeline.plan_run(run.run_id)
        task = run.tasks[0]
        unit = next(item for item in task.units if item.step_type == 'translate')
        step = core.pipeline.record_step_attempt(task.task_id, 'translate')
        result = core.pipeline._executor.execute(step, unit, run)
        assert len(calls) == 1
        body = json.loads(calls[0].body)
        actual = snapshot_digest({'endpoint': calls[0].url, 'model': body['model'], 'body': body})
        assert body['model'] == 'pinned-model'
        assert calls[0].url == 'https://fixture.invalid/v1/chat/completions'
        assert expected == actual == result.outputs['provenance']['payloadDigestPreview'] == result.outputs['provenance']['payloadDigestSend']
        assert expected != prepared['preparedDigest']
        assert core.pipeline.commit_step_result(step.step_run_id, result).status == 'committed'
        assert core.pipeline.get_run_snapshot(run.run_id, fresh=True).step_runs[-1].status.value == 'completed'
    finally: core.conn.close()
