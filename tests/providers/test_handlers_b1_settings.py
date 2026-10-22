"""Batch-B1 Run-time consumers: retry policy and model/GPU preference.

SETTINGS-OPEN-B-1 AC2/AC3 (``doc/design/SETTINGS_SECTION_SCHEMAS.md``
§4.1-§4.2). Three seams, one frozen Run snapshot as the source:

- ``ProductionHandlers._retry_policy_for_run``: the ``tasks`` section becomes
  the per-Run ``RetryPolicy``; an absent section/key keeps the assembled
  policy (identity for a wholly unset section, so the pre-B-1 behaviour is
  preserved);
- the two ``run_chain`` call sites (OCR, translate) pass that per-Run policy
  instead of ``deps.retry_policy``;
- the ``heavy_runner`` call site forwards the ``model_gpu`` preference to the
  runtime: ``auto`` sends ``preferred_device=None`` (no device planning), an
  explicit ``cpu`` / ``gpu`` sends the value, and the D06 §82 fallback pair
  (user switch AND provider declaration) rides along.

The device-manager side of the same contract lives in
``tests/providers/test_devices.py``; the write face in
``tests/core/test_settings_b1_sections.py``.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from infrastructure.providers import handlers as handlers_module
from infrastructure.providers.handlers import (
    HandlerDependencies,
    ProductionHandlers,
)
from infrastructure.providers.models import ModelManager
from infrastructure.providers.registry import ProviderDescriptor, ProviderRegistry
from infrastructure.providers.retry import RetryPolicy
from infrastructure.providers.runtime import ProviderRuntime
from ports.providers.errors import ProviderUnavailable
from ports.providers.profiles import CAPABILITY_OCR

from providers_helpers import FakeOcrProvider


# ---------------------------------------------------------------------------
# doubles
# ---------------------------------------------------------------------------


def _handlers(
    *,
    retry_policy: RetryPolicy | None = None,
    heavy_runner=None,
    registry=None,
    images=None,
    regions=None,
    region_writer=None,
) -> ProductionHandlers:
    return ProductionHandlers(
        HandlerDependencies(
            registry=registry,
            regions=regions,
            region_writer=region_writer,
            artifacts=None,
            images=images,
            geometry=None,
            retry_policy=retry_policy if retry_policy is not None else RetryPolicy(),
            heavy_runner=heavy_runner,
        )
    )


def _run(settings_snapshot: dict, **extra) -> SimpleNamespace:
    return SimpleNamespace(settings_snapshot=settings_snapshot, **extra)


class _RetryAfterSentinel:
    """Stands in for the runtime's Retry-After consumer (must be preserved)."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self) -> str | None:
        self.calls += 1
        return None


class _RecordingHeavyRunner:
    """Records the forwarded keywords, then actually runs the call."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def __call__(self, **kwargs):
        self.calls.append(dict(kwargs))
        return kwargs["call"]()


class _Provider:
    def __init__(
        self,
        *,
        requires_gpu: bool = False,
        supports_cpu_fallback: bool | None = None,
    ) -> None:
        self.requires_gpu = requires_gpu
        self.supports_cpu_fallback = supports_cpu_fallback

    def echo(self) -> str:
        return "called"


def _registry(provider, capability: str = CAPABILITY_OCR) -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register(
        ProviderDescriptor(
            provider_id="fake-provider",
            provider_type="fake",
            capabilities=frozenset({capability}),
        ),
        lambda: provider,
    )
    return registry


# ---------------------------------------------------------------------------
# _retry_policy_for_run: the Run-frozen ``tasks`` section
# ---------------------------------------------------------------------------


def test_no_tasks_section_is_the_assembled_policy_exactly() -> None:
    """Unset section == historical behaviour (same policy object/fields)."""
    sentinel = _RetryAfterSentinel()
    base = RetryPolicy(
        max_attempts=2,
        backoff_seconds=4.5,
        retry_codes=frozenset({"PROVIDER_TIMEOUT"}),
        retry_after_provider=sentinel,
    )
    handlers = _handlers(retry_policy=base)

    for snapshot in ({}, {"tasks": None}, {"tasks": "corrupt"}, {"tasks": {}}):
        policy = handlers._retry_policy_for_run(_run(snapshot))
        assert policy == base
        assert policy.max_attempts == 2
        assert policy.backoff_seconds == 4.5
        assert policy.retry_codes == frozenset({"PROVIDER_TIMEOUT"})
        assert policy.retry_after_provider is sentinel


def test_tasks_section_replaces_both_knobs_and_keeps_the_rest() -> None:
    sentinel = _RetryAfterSentinel()
    base = RetryPolicy(
        max_attempts=3,
        backoff_seconds=1.0,
        retry_codes=frozenset({"PROVIDER_TIMEOUT"}),
        retry_after_provider=sentinel,
    )
    handlers = _handlers(retry_policy=base)

    policy = handlers._retry_policy_for_run(
        _run({"tasks": {"retry_max_attempts": 1, "retry_backoff_seconds": 7.5}})
    )

    assert policy is not base
    assert policy.max_attempts == 1
    assert policy.backoff_seconds == 7.5
    # The UI exposes only the two knobs: everything else is inherited.
    assert policy.retry_codes == base.retry_codes
    assert policy.retry_after_provider is sentinel


@pytest.mark.parametrize(
    "tasks,expected",
    [
        ({"retry_max_attempts": 2}, (2, 6.5)),
        ({"retry_backoff_seconds": 0.5}, (3, 0.5)),
    ],
)
def test_partial_tasks_section_falls_back_per_missing_key(
    tasks: dict, expected: tuple[int, float]
) -> None:
    handlers = _handlers(retry_policy=RetryPolicy(max_attempts=3, backoff_seconds=6.5))
    policy = handlers._retry_policy_for_run(_run({"tasks": tasks}))
    assert (policy.max_attempts, policy.backoff_seconds) == expected


@pytest.mark.parametrize(
    "tasks,expected",
    [
        # out-of-range numbers are clamped into the frozen domain (the same
        # discipline runtime._retry_policy applies to providers.retry)
        ({"retry_max_attempts": 0}, (1, 1.0)),
        ({"retry_max_attempts": 99}, (3, 1.0)),
        ({"retry_backoff_seconds": 0.0}, (3, 0.1)),
        ({"retry_backoff_seconds": 120}, (3, 30.0)),
        # non-numbers are ignored instead of crashing the step
        ({"retry_max_attempts": "2"}, (3, 1.0)),
        ({"retry_max_attempts": True}, (3, 1.0)),
        ({"retry_backoff_seconds": "1"}, (3, 1.0)),
        ({"retry_backoff_seconds": False}, (3, 1.0)),
        ({"retry_max_attempts": None}, (3, 1.0)),
    ],
)
def test_corrupt_tasks_values_are_defensive(
    tasks: dict, expected: tuple[int, float]
) -> None:
    handlers = _handlers(retry_policy=RetryPolicy(max_attempts=3, backoff_seconds=1.0))
    policy = handlers._retry_policy_for_run(_run({"tasks": tasks}))
    assert (policy.max_attempts, policy.backoff_seconds) == expected


# ---------------------------------------------------------------------------
# both run_chain call sites use the per-Run policy
# ---------------------------------------------------------------------------


class _StopDispatch(Exception):
    """Sentinel: the policy was captured, nothing else needs to run."""


class _RecordingRunChain:
    def __init__(self) -> None:
        self.policies: list[RetryPolicy] = []

    def __call__(self, chain, invoke, *, policy=None, payload_hash_provider=None):
        self.policies.append(policy)
        raise _StopDispatch


def _ocr_environment(monkeypatch, handlers: ProductionHandlers) -> _RecordingRunChain:
    recorder = _RecordingRunChain()
    monkeypatch.setattr(handlers_module, "run_chain", recorder)
    handlers.deps.images = SimpleNamespace(
        region_crop=lambda page_id, region_id: (b"crop", 4, 3)
    )
    return recorder


def test_ocr_call_site_uses_the_run_tasks_policy(monkeypatch) -> None:
    base = RetryPolicy(max_attempts=3, backoff_seconds=1.0)
    handlers = _handlers(retry_policy=base)
    recorder = _ocr_environment(monkeypatch, handlers)
    run = _run(
        {"tasks": {"retry_max_attempts": 1, "retry_backoff_seconds": 0.2}},
        provider_binding_snapshot={"ocr": "fake-provider"},
    )
    unit = SimpleNamespace(target_id="t1", region_id="r1", page_id="p1", step_type="ocr")

    with pytest.raises(_StopDispatch):
        handlers.handle_ocr(SimpleNamespace(), unit, run)

    assert len(recorder.policies) == 1
    policy = recorder.policies[0]
    assert policy.max_attempts == 1
    assert policy.backoff_seconds == 0.2
    assert policy is not base


def test_translate_call_site_uses_the_run_tasks_policy(monkeypatch) -> None:
    recorder = _RecordingRunChain()
    monkeypatch.setattr(handlers_module, "run_chain", recorder)
    region = SimpleNamespace(
        region_id="r1",
        deleted=False,
        text=SimpleNamespace(ocr_text="原文"),
        region_type=SimpleNamespace(value="speech"),
    )
    handlers = _handlers(regions=SimpleNamespace(get_region=lambda rid: region))
    base = handlers.deps.retry_policy
    run = _run(
        {"tasks": {"retry_backoff_seconds": 10}},
        provider_binding_snapshot={"translate": "fake-provider"},
        targets=(),
        run_id="run-b1",
    )
    unit = SimpleNamespace(
        target_id="t1", region_id="r1", page_id="p1", step_type="translate"
    )

    with pytest.raises(_StopDispatch):
        handlers.handle_translate(SimpleNamespace(), unit, run)

    assert len(recorder.policies) == 1
    assert recorder.policies[0].backoff_seconds == 10.0
    # clamp/fallback contract: attempts keep the assembled value (3)
    assert recorder.policies[0].max_attempts == base.max_attempts


def test_call_sites_keep_the_assembled_policy_without_a_tasks_section(
    monkeypatch,
) -> None:
    recorder = _RecordingRunChain()
    monkeypatch.setattr(handlers_module, "run_chain", recorder)
    handlers = _handlers()
    handlers.deps.images = SimpleNamespace(
        region_crop=lambda page_id, region_id: (b"crop", 4, 3)
    )
    run = _run({}, provider_binding_snapshot={"ocr": "fake-provider"})
    unit = SimpleNamespace(target_id="t1", region_id="r1", page_id="p1", step_type="ocr")

    with pytest.raises(_StopDispatch):
        handlers.handle_ocr(SimpleNamespace(), unit, run)

    assert recorder.policies[0] is handlers.deps.retry_policy


class _FailingOcrProvider:
    """A retryable provider fault: counts how many attempts it receives."""

    provider_id = "fake-provider"
    provider_type = "fake"
    requires_gpu = False

    def __init__(self) -> None:
        self.attempts = 0

    def recognize(self, request):
        self.attempts += 1
        raise ProviderUnavailable(
            "endpoint unavailable", provider_id=self.provider_id, stage="ocr"
        )


def _ocr_attempts(
    provider: _FailingOcrProvider, *, snapshot: dict, base: RetryPolicy
) -> int:
    handlers = _handlers(
        retry_policy=base,
        registry=_registry(provider),
        images=SimpleNamespace(region_crop=lambda page_id, region_id: (b"crop", 4, 3)),
        region_writer=SimpleNamespace(
            prepare_ocr_text=lambda *args, **kwargs: pytest.fail(
                "a failing provider must not reach the writer"
            )
        ),
    )
    run = _run(
        snapshot,
        provider_binding_snapshot={"ocr": "fake-provider"},
        run_id="run-b1",
    )
    unit = SimpleNamespace(target_id="t1", region_id="r1", page_id="p1", step_type="ocr")

    with pytest.raises(ProviderUnavailable):
        handlers.handle_ocr(SimpleNamespace(step_run_id="s", input_refs={}), unit, run)
    return provider.attempts


def test_retry_loop_keeps_the_assembled_policy_without_a_tasks_section() -> None:
    """AC3 equivalence: unset ``tasks`` -> exactly the historical retry count.

    ``base`` retries once per ``max_attempts``; the unset Run must therefore
    still make 3 attempts, proving the per-Run policy is the assembled one and
    not a differently-built equal-looking object with another loop bound.
    """
    base = RetryPolicy(max_attempts=3, backoff_seconds=0)
    assert _ocr_attempts(_FailingOcrProvider(), snapshot={}, base=base) == 3


@pytest.mark.parametrize("max_attempts,expected", [(1, 1), (2, 2), (3, 3)])
def test_retry_loop_follows_the_run_tasks_section(
    max_attempts: int, expected: int
) -> None:
    base = RetryPolicy(max_attempts=3, backoff_seconds=0)
    snapshot = {"tasks": {"retry_max_attempts": max_attempts}}
    assert (
        _ocr_attempts(_FailingOcrProvider(), snapshot=snapshot, base=base)
        == expected
    )


# ---------------------------------------------------------------------------
# heavy_runner: the model_gpu preference is forwarded from the Run snapshot
# ---------------------------------------------------------------------------


def _invoke(
    handlers: ProductionHandlers, run, *, capability: str = CAPABILITY_OCR
):
    return handlers._invoke_provider(
        "fake-provider", capability, lambda provider: provider.echo(), run=run
    )


@pytest.mark.parametrize(
    "snapshot,expected_preference",
    [
        ({}, None),
        ({"model_gpu": None}, None),
        ({"model_gpu": {}}, None),
        ({"model_gpu": {"device_preference": "auto"}}, None),
        # a corrupted/unknown value must not invent a preference
        ({"model_gpu": {"device_preference": "tpu"}}, None),
        ({"model_gpu": {"device_preference": 1}}, None),
        ({"model_gpu": {"device_preference": "cpu"}}, "cpu"),
        ({"model_gpu": {"device_preference": "gpu"}}, "gpu"),
    ],
)
def test_heavy_runner_forwarded_device_preference(
    snapshot: dict, expected_preference: str | None
) -> None:
    runner = _RecordingHeavyRunner()
    provider = _Provider(requires_gpu=True, supports_cpu_fallback=True)
    handlers = _handlers(heavy_runner=runner, registry=_registry(provider))

    assert _invoke(handlers, _run(snapshot)) == "called"

    assert len(runner.calls) == 1
    forwarded = runner.calls[0]
    assert forwarded["preferred_device"] == expected_preference
    assert forwarded["requires_gpu"] is True
    assert forwarded["supports_cpu_fallback"] is True


@pytest.mark.parametrize(
    "model_gpu,expected_allow",
    [
        ({"device_preference": "gpu"}, True),  # design default
        ({"device_preference": "gpu", "allow_cpu_fallback": False}, False),
        ({"device_preference": "gpu", "allow_cpu_fallback": True}, True),
        # malformed switch -> the conservative design default (allowed)
        ({"device_preference": "gpu", "allow_cpu_fallback": "false"}, True),
        ({"device_preference": "gpu", "allow_cpu_fallback": 0}, True),
    ],
)
def test_heavy_runner_forwarded_cpu_fallback_switch(
    model_gpu: dict, expected_allow: bool
) -> None:
    runner = _RecordingHeavyRunner()
    provider = _Provider(requires_gpu=True, supports_cpu_fallback=True)
    handlers = _handlers(heavy_runner=runner, registry=_registry(provider))

    _invoke(handlers, _run({"model_gpu": model_gpu}))

    assert runner.calls[0]["allow_cpu_fallback"] is expected_allow


def test_heavy_runner_forwards_provider_cpu_support_and_requires_gpu() -> None:
    runner = _RecordingHeavyRunner()
    handlers = _handlers(
        heavy_runner=runner,
        registry=_registry(_Provider(requires_gpu=False, supports_cpu_fallback=False)),
    )

    _invoke(handlers, _run({"model_gpu": {"device_preference": "cpu"}}))

    forwarded = runner.calls[0]
    assert forwarded["requires_gpu"] is False
    assert forwarded["supports_cpu_fallback"] is False


def test_without_a_heavy_runner_the_provider_is_called_directly() -> None:
    provider = _Provider(requires_gpu=True, supports_cpu_fallback=True)
    handlers = _handlers(registry=_registry(provider))

    # No heavy runner assembled: the historical direct call, no device gate.
    assert _invoke(handlers, _run({"model_gpu": {"device_preference": "gpu"}})) == (
        "called"
    )


def test_handle_ocr_forwards_the_run_snapshot_preference_end_to_end(monkeypatch) -> None:
    """The preference reaches heavy_runner through the real OCR handler."""
    runner = _RecordingHeavyRunner()
    provider = FakeOcrProvider("こんにちは")
    registry = _registry(provider)
    prepared = SimpleNamespace(
        retranslate_hint=False, revision_no=1, revision_id="rev-ocr-1"
    )
    region_writer = SimpleNamespace(prepare_ocr_text=lambda *args, **kwargs: prepared)
    handlers = _handlers(
        registry=registry,
        heavy_runner=runner,
        images=SimpleNamespace(region_crop=lambda page_id, region_id: (b"crop", 4, 3)),
        region_writer=region_writer,
    )
    run = _run(
        {"model_gpu": {"device_preference": "cpu", "allow_cpu_fallback": False}},
        provider_binding_snapshot={"ocr": "fake-provider"},
        run_id="run-b1",
    )
    unit = SimpleNamespace(target_id="t1", region_id="r1", page_id="p1", step_type="ocr")

    result = handlers.handle_ocr(
        SimpleNamespace(step_run_id="sr-1", input_refs={}), unit, run
    )

    assert result.outputs["ocr_text"] == "こんにちは"
    assert len(runner.calls) == 1
    forwarded = runner.calls[0]
    assert forwarded["preferred_device"] == "cpu"
    assert forwarded["allow_cpu_fallback"] is False
    assert forwarded["requires_gpu"] is False


# ---------------------------------------------------------------------------
# ProviderRuntime.heavy_runner: auto keeps the historical call shape
# ---------------------------------------------------------------------------


class _RecordingDevices:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def run_guarded(self, **kwargs):
        self.calls.append(dict(kwargs))
        return "executed"


def _runtime(devices) -> ProviderRuntime:
    return ProviderRuntime(
        registry=ProviderRegistry(), devices=devices, models=ModelManager()
    )


def test_runtime_auto_passes_straight_through_to_run_guarded() -> None:
    devices = _RecordingDevices()
    runtime = _runtime(devices)
    sentinel = object()

    assert runtime.heavy_runner(requires_gpu=True, call=sentinel) == "executed"

    assert devices.calls == [{"requires_gpu": True, "call": sentinel}]


def test_runtime_forwards_an_explicit_preference_and_fallback_pair() -> None:
    devices = _RecordingDevices()
    runtime = _runtime(devices)
    sentinel = object()

    assert (
        runtime.heavy_runner(
            requires_gpu=True,
            call=sentinel,
            preferred_device="gpu",
            allow_cpu_fallback=False,
            supports_cpu_fallback=True,
        )
        == "executed"
    )

    assert devices.calls == [
        {
            "requires_gpu": True,
            "call": sentinel,
            "preferred_device": "gpu",
            "allow_cpu_fallback": False,
            "supports_cpu_fallback": True,
        }
    ]
