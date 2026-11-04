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


def _remote_translation_provider(core, region, *, provider_id, model='pinned-model',
                                 base_url='https://fixture.invalid/v1', credential_ref=None,
                                 credential_resolver=None, options=()):
    import json as _json
    from infrastructure.providers.registry import ProviderDescriptor
    from infrastructure.providers.translation_openai import OpenAiTranslationProvider
    from infrastructure.providers.openai_client import OpenAiCompatibleClient, OpenAiCompatibleConfig
    from ports.network.transport import TransportOutcome, TransportResponse
    calls = []

    class Transport:
        def send(self, request, profile):
            calls.append(request)
            body = {'choices': [{'message': {'content': _json.dumps({'translations': [
                {'region_id': region, 'translated_text': 'translated'}]})}}]}
            return TransportOutcome(TransportResponse(status=200, body=_json.dumps(body).encode()))

    config = OpenAiCompatibleConfig(provider_id, 'openai-compatible', base_url=base_url,
                                    model=model, credential_ref=credential_ref)
    provider = OpenAiTranslationProvider(
        config, OpenAiCompatibleClient(config, Transport(), credential_resolver=credential_resolver),
        provider_id=provider_id, options=options)
    core.providers.registry.register(
        ProviderDescriptor(provider_id, 'openai-compatible', frozenset({'translation'})), lambda: provider)
    core.pipeline_defaults.save_provider_binding('translate', provider_id)
    return provider, calls


def test_unsupported_provider_type_prepare_fails_closed_but_start_run_survives():
    from infrastructure.providers.registry import ProviderDescriptor

    class LegacyTranslationProvider:
        provider_id = 'fea10-legacy'
        provider_type = 'docTR-blob'
        model = 'legacy-model'
        target_language = ''
        options = ()

        def translate(self, payload):
            raise AssertionError('not reached')

    core, _, region = _new_workspace(workspace('ac2-unsupported-type'))
    try:
        core.providers.registry.register(
            ProviderDescriptor('fea10-legacy', 'docTR-blob', frozenset({'translation'})),
            LegacyTranslationProvider)
        core.pipeline_defaults.save_provider_binding('translate', 'fea10-legacy')
        scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
        # Prepare must fail closed: an ID-only binding is not a replayable snapshot.
        with pytest.raises(PipelineError) as caught:
            core.pipeline.prepare_run('retranslate_region', scope)
        assert caught.value.code == 'RUN_SNAPSHOT_INCOMPLETE'
        assert core.pipeline._store.list_ids() == ()
        # The released StartRun path keeps working for the same legacy binding.
        run = core.pipeline.create_run('retranslate_region', scope)
        assert run.provider_binding_snapshot.get('translate')
        assert 'execution' not in (
            run.provider_binding_snapshot['translate']
            if isinstance(run.provider_binding_snapshot['translate'], dict) else {})
    finally: core.conn.close()


def test_incomplete_remote_config_fails_closed_at_prepare():
    core, _, region = _new_workspace(workspace('ac2-incomplete-model'))
    try:
        _remote_translation_provider(core, region, provider_id='fea10-nomodel', model='')
        scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
        with pytest.raises(PipelineError) as caught:
            core.pipeline.prepare_run('retranslate_region', scope)
        assert caught.value.code == 'RUN_SNAPSHOT_INCOMPLETE'
        assert core.pipeline._store.list_ids() == ()
    finally: core.conn.close()


def test_snapshot_carries_no_authentication_material_and_rejects_smuggling():
    from tests.core.test_fea00a_pipeline_seam import _prepare_ocr
    core, _, region = _new_workspace(workspace('ac2-sensitive-surface'))
    try:
        _, ocr_step, _, ocr_result = _prepare_ocr(core, region)
        assert core.pipeline.commit_step_result(ocr_step.step_run_id, ocr_result).status == 'committed'
        runs_before = set(core.pipeline._store.list_ids())
        secret = 'SUPER-SECRET-TOKEN-VALUE'
        provider, _ = _remote_translation_provider(
            core, region, provider_id='fea10-cred', credential_ref='vault:opaque-ref',
            credential_resolver=lambda ref: secret, options=(('temperature', '0.5'),))
        scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
        prepared = core.pipeline.prepare_run('retranslate_region', scope)
        serialized = json.dumps(prepared, ensure_ascii=False, default=str)
        assert secret not in serialized
        execution = prepared['providerBindingSnapshot']['translate']['execution']
        assert execution['credential_ref'] == 'vault:opaque-ref'
        assert 'authorization' not in serialized.lower()
        # Authentication material smuggled through run overrides is rejected outright.
        with pytest.raises(PipelineError) as caught:
            core.pipeline.prepare_run(
                'retranslate_region', scope, overrides={'translate': {'token': secret}})
        assert caught.value.code == 'RUN_SNAPSHOT_INCOMPLETE'
        # Options outside the frozen replay whitelist never reach a candidate.
        provider.options = (('undocumented_key', '1'),)
        with pytest.raises(PipelineError) as caught:
            core.pipeline.prepare_run('retranslate_region', scope)
        assert caught.value.code == 'RUN_SNAPSHOT_INCOMPLETE'
        assert set(core.pipeline._store.list_ids()) == runs_before
    finally: core.conn.close()
