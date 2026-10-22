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

Review B1 fixes the declaration source: the provider instance is the wrong
place to read ``requires_gpu`` / ``supports_cpu_fallback`` (real providers do
not repeat them), so the handlers read the registry's ``ProviderDescriptor``;
the doubles below therefore declare those flags on the descriptor only, and
the real-``DeviceManager`` regression tests prove the CPU fallback is actually
reachable. The device-manager side of the same contract lives in
``tests/providers/test_devices.py``; the write face in
``tests/core/test_settings_b1_sections.py``.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from infrastructure.devices.manager import DeviceManager
from infrastructure.providers import handlers as handlers_module
from infrastructure.providers.handlers import (
    HandlerDependencies,
    ProductionHandlers,
)
from infrastructure.providers.models import ModelManager
from infrastructure.providers.registry import ProviderDescriptor, ProviderRegistry
from infrastructure.providers.retry import RetryPolicy
from infrastructure.providers.runtime import ProviderRuntime
from ports.providers.errors import DeviceUnavailable, ProviderUnavailable
from ports.providers.profiles import CAPABILITY_OCR

from providers_helpers import FakeOcrProvider
from tests.providers.env_sim import gpu_state


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
    """A provider instance with NO capability flags of its own (review B1).

    Real providers (``MangaOcrProvider`` / ``PaddleKoreanOcrProvider`` ...) do
    not repeat ``requires_gpu`` / ``supports_cpu_fallback`` on the instance;
    those declarations live on the registry's ``ProviderDescriptor``. The
    doubles here mirror that production shape on purpose: a test that stuffs
    the flags onto the instance proves nothing about the real data source.
    """

    def echo(self) -> str:
        return "called"


def _registry(
    provider,
    *,
    capability: str = CAPABILITY_OCR,
    requires_gpu: bool = False,
    supports_cpu_fallback: bool = False,
) -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register(
        ProviderDescriptor(
            provider_id="fake-provider",
            provider_type="fake",
            capabilities=frozenset({capability}),
            requires_gpu=requires_gpu,
            supports_cpu_fallback=supports_cpu_fallback,
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


@pytest.mark.parametrize("snapshot", [None, "corrupt", [], 7])
def test_non_mapping_snapshot_is_an_absent_tasks_section(snapshot) -> None:
    """Review m1: the documented contract must not crash on a non-mapping
    snapshot (an independent/replayed handler seam can hand one over)."""
    base = RetryPolicy(max_attempts=2, backoff_seconds=0.5)
    handlers = _handlers(retry_policy=base)
    run = SimpleNamespace(settings_snapshot=snapshot)

    assert handlers._retry_policy_for_run(run) is base


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
    provider = _Provider()
    handlers = _handlers(
        heavy_runner=runner,
        registry=_registry(provider, requires_gpu=True, supports_cpu_fallback=True),
    )

    assert _invoke(handlers, _run(snapshot)) == "called"

    assert len(runner.calls) == 1
    forwarded = runner.calls[0]
    assert forwarded["preferred_device"] == expected_preference
    # review B1: the flags come from the DESCRIPTOR, not from the instance
    assert forwarded["requires_gpu"] is True
    assert forwarded["supports_cpu_fallback"] is True
    assert not hasattr(provider, "requires_gpu")
    assert not hasattr(provider, "supports_cpu_fallback")


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
    handlers = _handlers(
        heavy_runner=runner,
        registry=_registry(_Provider(), requires_gpu=True, supports_cpu_fallback=True),
    )

    _invoke(handlers, _run({"model_gpu": model_gpu}))

    assert runner.calls[0]["allow_cpu_fallback"] is expected_allow


def test_non_gpu_provider_ignores_the_device_preference() -> None:
    """Review M3: a remote / CPU-only provider must not fail on a user gpu pick.

    Translation / vision OCR descriptors declare ``requires_gpu=False`` and
    ``supports_cpu_fallback=False``; a Run-wide ``gpu`` preference must not
    turn their calls into ``DeviceUnavailable``.
    """
    runner = _RecordingHeavyRunner()
    handlers = _handlers(
        heavy_runner=runner,
        registry=_registry(_Provider()),  # descriptor requires_gpu=False
    )

    _invoke(handlers, _run({"model_gpu": {"device_preference": "gpu"}}))

    forwarded = runner.calls[0]
    assert forwarded["preferred_device"] is None
    assert forwarded["requires_gpu"] is False


def test_descriptor_flags_win_over_conflicting_instance_attributes() -> None:
    """Review B1: the descriptor is the declaration source of truth."""

    class _InstanceDeclared:
        requires_gpu = True
        supports_cpu_fallback = True

        def echo(self) -> str:
            return "called"

    runner = _RecordingHeavyRunner()
    handlers = _handlers(
        heavy_runner=runner,
        registry=_registry(_InstanceDeclared()),  # descriptor declares False/False
    )

    _invoke(handlers, _run({"model_gpu": {"device_preference": "cpu"}}))

    forwarded = runner.calls[0]
    assert forwarded["requires_gpu"] is False
    assert forwarded["supports_cpu_fallback"] is False


def test_instance_attributes_are_the_fallback_without_a_descriptor() -> None:
    """A registry that cannot answer a descriptor keeps the historical read."""
    provider = _Provider()
    provider.requires_gpu = True
    provider.supports_cpu_fallback = True

    class _RegistryWithoutDescriptor:
        def resolve(self, capability: str, provider_id: str):
            return provider

        def descriptor(self, provider_id: str, *, capability=None):
            return None

    runner = _RecordingHeavyRunner()
    handlers = _handlers(
        heavy_runner=runner, registry=_RegistryWithoutDescriptor()
    )

    _invoke(handlers, _run({"model_gpu": {"device_preference": "gpu"}}))

    forwarded = runner.calls[0]
    assert forwarded["requires_gpu"] is True
    assert forwarded["supports_cpu_fallback"] is True


def test_without_a_heavy_runner_the_provider_is_called_directly() -> None:
    provider = _Provider()
    handlers = _handlers(
        registry=_registry(provider, requires_gpu=True, supports_cpu_fallback=True)
    )

    # No heavy runner assembled: the historical direct call, no device gate.
    assert _invoke(handlers, _run({"model_gpu": {"device_preference": "gpu"}})) == (
        "called"
    )


def test_handle_ocr_forwards_the_descriptor_cpu_support_end_to_end() -> None:
    """The descriptor declaration reaches heavy_runner through the real OCR handler."""
    runner = _RecordingHeavyRunner()
    provider = FakeOcrProvider("こんにちは")  # no supports_cpu_fallback attribute
    registry = _registry(provider, requires_gpu=False, supports_cpu_fallback=True)
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
    assert forwarded["preferred_device"] is None  # review M3: remote/CPU provider
    assert forwarded["allow_cpu_fallback"] is False
    assert forwarded["requires_gpu"] is False
    # review B1: the descriptor flag was forwarded although the instance has
    # no ``supports_cpu_fallback`` attribute at all.
    assert forwarded["supports_cpu_fallback"] is True
    assert not hasattr(provider, "supports_cpu_fallback")


# ---------------------------------------------------------------------------
# review B1 regression: the real device chain must honour the descriptor
# declaration, otherwise ``allow_cpu_fallback`` is an unreachable control for
# every production provider (they declare the flag on ProviderDescriptor only).
# ---------------------------------------------------------------------------


def _device_chain_handlers(
    provider, *, requires_gpu: bool, supports_cpu_fallback: bool
) -> ProductionHandlers:
    """Handlers wired to a REAL DeviceManager through the provider runtime."""
    registry = _registry(
        provider,
        requires_gpu=requires_gpu,
        supports_cpu_fallback=supports_cpu_fallback,
    )
    runtime = ProviderRuntime(
        registry=registry, devices=DeviceManager(), models=ModelManager()
    )
    return _handlers(heavy_runner=runtime.heavy_runner, registry=registry)


def _execute(handlers: ProductionHandlers, calls: list[str], snapshot: dict):
    def call(provider) -> str:
        calls.append("called")
        return "executed"

    return handlers._invoke_provider(
        "fake-provider", CAPABILITY_OCR, call, run=_run(snapshot)
    )


def test_descriptor_cpu_fallback_is_reachable_on_the_real_device_chain() -> None:
    """B1: descriptor True + user allows + no GPU -> the call runs on CPU."""
    calls: list[str] = []
    handlers = _device_chain_handlers(
        _Provider(), requires_gpu=True, supports_cpu_fallback=True
    )
    snapshot = {"model_gpu": {"device_preference": "gpu", "allow_cpu_fallback": True}}

    with gpu_state(available=False):
        assert _execute(handlers, calls, snapshot) == "executed"

    assert calls == ["called"]


def test_descriptor_cpu_fallback_disabled_by_the_user_is_a_typed_refusal() -> None:
    """B1: descriptor True but the user switch is off -> typed refusal, no call."""
    calls: list[str] = []
    handlers = _device_chain_handlers(
        _Provider(), requires_gpu=True, supports_cpu_fallback=True
    )
    snapshot = {"model_gpu": {"device_preference": "gpu", "allow_cpu_fallback": False}}

    with gpu_state(available=False):
        with pytest.raises(DeviceUnavailable):
            _execute(handlers, calls, snapshot)

    assert calls == []


def test_descriptor_without_cpu_support_stays_a_typed_refusal() -> None:
    """B1: descriptor False ANDs with the user switch, which cannot enable it."""
    calls: list[str] = []
    handlers = _device_chain_handlers(
        _Provider(), requires_gpu=True, supports_cpu_fallback=False
    )
    snapshot = {"model_gpu": {"device_preference": "gpu", "allow_cpu_fallback": True}}

    with gpu_state(available=False):
        with pytest.raises(DeviceUnavailable):
            _execute(handlers, calls, snapshot)

    assert calls == []


def test_auto_path_ignores_the_descriptor_gpu_flags() -> None:
    """B1 non-regression: ``auto`` still runs the un-planned historical path."""
    calls: list[str] = []
    handlers = _device_chain_handlers(
        _Provider(), requires_gpu=True, supports_cpu_fallback=True
    )

    with gpu_state(available=False):
        # no model_gpu section -> preferred_device=None -> run_guarded as before
        assert _execute(handlers, calls, {}) == "executed"

    assert calls == ["called"]


def test_handle_ocr_end_to_end_falls_back_on_the_descriptor_declaration() -> None:
    """Review B1 end-to-end: the real OCR handler runs via the CPU fallback.

    ``FakeOcrProvider`` has no ``supports_cpu_fallback`` attribute; only the
    descriptor declares it. With an explicit ``gpu`` preference, no GPU and
    ``allow_cpu_fallback=True`` the OCR step must actually execute instead of
    failing with ``DeviceUnavailable``.
    """
    provider = FakeOcrProvider("こんにちは")
    prepared = SimpleNamespace(
        retranslate_hint=False, revision_no=1, revision_id="rev-ocr-b1"
    )
    registry = _registry(
        provider, requires_gpu=True, supports_cpu_fallback=True
    )
    runtime = ProviderRuntime(
        registry=registry, devices=DeviceManager(), models=ModelManager()
    )
    handlers = _handlers(
        registry=registry,
        heavy_runner=runtime.heavy_runner,
        images=SimpleNamespace(region_crop=lambda page_id, region_id: (b"crop", 4, 3)),
        region_writer=SimpleNamespace(
            prepare_ocr_text=lambda *args, **kwargs: prepared
        ),
    )
    run = _run(
        {"model_gpu": {"device_preference": "gpu", "allow_cpu_fallback": True}},
        provider_binding_snapshot={"ocr": "fake-provider"},
        run_id="run-b1",
    )
    unit = SimpleNamespace(target_id="t1", region_id="r1", page_id="p1", step_type="ocr")

    with gpu_state(available=False):
        result = handlers.handle_ocr(
            SimpleNamespace(step_run_id="sr-b1", input_refs={}), unit, run
        )

    assert result.outputs["ocr_text"] == "こんにちは"
    assert len(provider.requests) == 1
    assert not hasattr(provider, "supports_cpu_fallback")


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
