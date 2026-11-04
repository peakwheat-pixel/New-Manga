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


def test_prepared_settings_filter_non_execution_sections_and_reject_unknown_execution_keys():
    core, _, region = _new_workspace(workspace('snapshot-safety'))
    try:
        # R-001/RR-01: a settings page outside the execution surface is removed, not copied.
        core.pipeline_defaults.save_settings_section('untyped', {'unregistered': 'value'})
        preview, _ = prepare(core, region)
        assert preview['preparedDigest'].startswith('sha256:')
        assert 'untyped' not in preview['settingsSnapshot']
        # R-001: legitimate frozen settings keys are replayable (typeset surface).
        core.pipeline_defaults.save_settings_section(
            'typeset', {'stroke_enabled': True, 'auto_font_size': True})
        preview, _ = prepare(core, region)
        assert preview['settingsSnapshot']['typeset']['stroke_enabled'] is True
        # An unknown key inside an execution section still fails closed before any candidate.
        scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
        with pytest.raises(PipelineError, match='RUN_SNAPSHOT_INCOMPLETE'):
            core.pipeline.prepare_run('ocr_region', scope, overrides={'settings': {'typeset': {'undocumented': 1}}})
        assert core.pipeline._store.list_ids() == ()
    finally:
        core.conn.close()


def test_nested_authentication_material_cannot_enter_a_prepared_run():
    # RR-01: nested/unknown authentication keys must be rejected, never persisted with a Run.
    core, _, region = _new_workspace(workspace('rr01-auth'))
    try:
        scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
        for overrides in (
            {'settings': {'ocr': {'headers': 'Bearer leak'}}},
            {'settings': {'untyped': {'headers': 'leak'}}},
            {'translate': {'token': 'leak'}},
        ):
            with pytest.raises(PipelineError, match='RUN_SNAPSHOT_INCOMPLETE'):
                core.pipeline.prepare_run('ocr_region', scope, overrides=overrides)
        preview = core.pipeline.prepare_run(
            'ocr_region', scope, overrides={'settings': {'untyped': {'value': 1}}})
        assert 'untyped' not in preview['settingsSnapshot']
        run, _ = core.pipeline.accept_prepared_run(preview, scope, idempotency_key='rr01')
        assert 'untyped' not in run.settings_snapshot
    finally:
        core.conn.close()

def test_glossary_term_named_token_is_not_treated_as_authentication_material():
    # R-014: user content words must not be rejected by the authentication-key scan.
    core, _, region = _new_workspace(workspace('glossary-token'))
    try:
        scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
        preview = core.pipeline.prepare_run(
            'ocr_region', scope,
            overrides={'settings': {'translate': {'glossary': [{'term': 'token', 'translation': '令牌'}]}}})
        assert preview['preparedDigest'].startswith('sha256:')
        # Endpoint authentication smuggled through provider bindings is still refused.
        with pytest.raises(PipelineError, match='RUN_SNAPSHOT_INCOMPLETE'):
            core.pipeline.prepare_run(
                'ocr_region', scope,
                overrides={'provider_bindings': {'ocr': {'id': 'manga-ocr', 'token': 'leak'}}})
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


def test_mapping_binding_shapes_stay_available_at_plan():
    # R-002: every frozen binding shape (provider_id / provider_profile_id / id) must be replayable.
    from infrastructure.providers.registry import ProviderDescriptor
    for shape in ('id', 'provider_profile_id'):
        core, _, region = _new_workspace(workspace('mapping-' + shape))
        try:
            _remote_translation_provider(core, region, provider_id='fea10-mapping')
            core.pipeline_defaults.save_provider_binding('translate', {shape: 'fea10-mapping'})
            scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
            preview = core.pipeline.prepare_run('retranslate_region', scope)
            binding = preview['providerBindingSnapshot']['translate']
            assert binding['provider_id'] == 'fea10-mapping'
            # R-002: planning readiness must resolve the same shape instead of KeyError->unavailable.
            assert core.providers.registry.run_binding_available('translate', binding) is True
            run, created = core.pipeline.accept_prepared_run(
                preview, scope, idempotency_key='mapping-' + shape)
            assert created
        finally:
            core.conn.close()


def test_untyped_fallback_fails_closed_with_frozen_error_code():
    # R-003: an unregistered/untyped fallback must raise RUN_SNAPSHOT_INCOMPLETE, never TypeError.
    from infrastructure.providers.registry import ProviderDescriptor

    class LegacyTranslationProvider:
        provider_id = 'fea10-legacy'
        provider_type = 'docTR-blob'
        model = 'legacy-model'

        def translate(self, payload):
            raise AssertionError('not reached')

    core, _, region = _new_workspace(workspace('ac2-fallback'))
    try:
        _remote_translation_provider(core, region, provider_id='fea10-primary')
        core.providers.registry.register(
            ProviderDescriptor('fea10-legacy', 'docTR-blob', frozenset({'translation'})),
            LegacyTranslationProvider)
        core.pipeline_defaults.save_provider_binding(
            'translate', {'provider_id': 'fea10-primary', 'fallback': ['fea10-legacy']})
        scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
        with pytest.raises(PipelineError) as caught:
            core.pipeline.prepare_run('retranslate_region', scope)
        assert caught.value.code == 'RUN_SNAPSHOT_INCOMPLETE'
        assert core.pipeline._store.list_ids() == ()
    finally:
        core.conn.close()


def test_default_local_ocr_binding_is_typed_replayable():
    # R-004/R-005: the Host default {"ocr": "manga-ocr"} must be preparable on a production registry.
    from infrastructure.providers.registry import ProviderDescriptor

    class LocalOcr:
        provider_id = 'manga-ocr'
        provider_type = 'local-manga-ocr'
        model = 'manga-ocr-v1'
        options = ()

        def recognize(self, request):
            raise AssertionError('not reached')

    core, _, region = _new_workspace(workspace('local-typed'))
    try:
        core.providers.registry.register(
            ProviderDescriptor('manga-ocr', 'local-manga-ocr', frozenset({'ocr'})), LocalOcr)
        core.pipeline_defaults.save_provider_binding('ocr', 'manga-ocr')
        scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
        preview = core.pipeline.prepare_run('ocr_region', scope)
        execution = preview['providerBindingSnapshot']['ocr']['execution']
        assert execution['provider_type'] == 'local-manga-ocr'
        assert execution['model'] == 'manga-ocr-v1'
        assert execution['adapter_version'] == 'local:local-manga-ocr:v1'
        run, created = core.pipeline.accept_prepared_run(preview, scope, idempotency_key='local-typed')
        assert created and run.provider_binding_snapshot['ocr']['execution']['model'] == 'manga-ocr-v1'
    finally:
        core.conn.close()


def test_nested_auth_material_in_defaults_and_glossary_values_is_rejected():
    # FR-01: arbitrary nested authentication keys are rejected, including defaults/glossary values.
    core, _, region = _new_workspace(workspace('fr01-nested'))
    try:
        scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
        with pytest.raises(PipelineError, match='RUN_SNAPSHOT_INCOMPLETE'):
            core.pipeline.prepare_run('ocr_region', scope, overrides={
                'settings': {'translate': {'glossary': {'nested': {'headers': {'authorization': 'x'}}}}}})
        # A mapping glossary with a term literally named "token" stays legal.
        preview = core.pipeline.prepare_run('ocr_region', scope, overrides={
            'settings': {'translate': {'glossary': {'token': '令牌', 'normal': 'ordinary'}}}})
        assert preview['settingsSnapshot']['translate']['glossary']['token'] == '令牌'
    finally:
        core.conn.close()


def test_local_primary_freezes_its_fallback_chain():
    # FR-03: a local typed primary freezes its declared fallback chain or fails closed.
    from infrastructure.providers.registry import ProviderDescriptor

    class LocalOcr:
        provider_id = 'manga-ocr'
        provider_type = 'local-manga-ocr'
        model = 'manga-ocr-v1'

        def recognize(self, request):
            raise AssertionError('not reached')

    core, _, region = _new_workspace(workspace('fr03-local-fallback'))
    try:
        core.providers.registry.register(
            ProviderDescriptor('manga-ocr', 'local-manga-ocr', frozenset({'ocr'})), LocalOcr)
        core.providers.registry.register(
            ProviderDescriptor('manga-ocr-backup', 'docTR-blob', frozenset({'ocr'})), LocalOcr)
        core.pipeline_defaults.save_provider_binding(
            'ocr', {'provider_id': 'manga-ocr', 'fallback': ['manga-ocr-backup']})
        scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
        with pytest.raises(PipelineError, match='RUN_SNAPSHOT_INCOMPLETE'):
            core.pipeline.prepare_run('ocr_region', scope)
    finally:
        core.conn.close()


def test_illegal_execution_section_shape_is_rejected():
    # FR-07: an execution section with a non-mapping shape fails with a typed incomplete error.
    core, _, region = _new_workspace(workspace('fr07-shape'))
    try:
        scope = PipelineScope(ScopeType.REGION, selected_ids=(region,))
        with pytest.raises(PipelineError, match='RUN_SNAPSHOT_INCOMPLETE'):
            core.pipeline.prepare_run(
                'ocr_region', scope, overrides={'settings': {'typeset': ['not', 'a', 'mapping']}})
    finally:
        core.conn.close()

