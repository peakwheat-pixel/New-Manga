"""Provider readiness and fail-closed resolution (AC-OPTIONAL-001/002)."""

from __future__ import annotations

import importlib.util

import pytest

from infrastructure.providers.dependencies import (
    KIND_MODULE,
    Requirement,
    evaluate_requirements,
    probe_endpoint,
    probe_module,
    probe_weight,
)
from infrastructure.providers.registry import ProviderDescriptor, ProviderRegistry
from infrastructure.providers.runtime import build_provider_registry
from ports.providers.errors import (
    ProviderDependencyMissing,
    ProviderDisabled,
    ProviderError,
    ProviderNotConfigured,
    ProviderNotImplemented,
    ProviderState,
)
from ports.providers.profiles import CAPABILITY_INPAINT, CAPABILITY_OCR, CAPABILITY_TRANSLATION


def test_missing_optional_runtime_is_reported_not_raised() -> None:
    probe = probe_module("definitely_absent_task019_module")
    assert probe.satisfied is False
    assert probe.state == "missing"
    assert "not installed" in probe.detail


def test_requirement_probes_cover_module_weight_and_endpoint(tmp_path) -> None:
    weight = tmp_path / "weights.bin"
    weight.write_bytes(b"1234")
    assert probe_weight(weight).satisfied is True
    assert probe_weight(tmp_path / "absent.bin").satisfied is False
    empty = tmp_path / "empty.bin"
    empty.write_bytes(b"")
    assert probe_weight(empty).satisfied is False
    assert probe_endpoint("", "m").satisfied is False
    assert probe_endpoint("http://x/v1", "").satisfied is False
    assert probe_endpoint("http://x/v1", "m").satisfied is True

    probes = evaluate_requirements(
        (Requirement(KIND_MODULE, "definitely_absent_task019_module"),),
        credential_resolver=None,
    )
    assert probes[0].satisfied is False


def test_real_environment_reports_optional_providers_as_not_ready() -> None:
    """AC-OPTIONAL-001/002: absent runtimes must not crash the assembly."""
    registry, models = build_provider_registry(settings={})
    statuses = {status.provider_id: status for status in registry.statuses()}

    for provider_id in ("manga-ocr", "paddleocr-korean"):
        status = statuses[provider_id]
        assert status.ready is False
        assert status.state == ProviderState.MISSING_DEPENDENCY
        assert status.error_code == ProviderDependencyMissing.error_code
        assert status.missing_requirements
        with pytest.raises(ProviderDependencyMissing):
            registry.resolve(CAPABILITY_OCR, provider_id)

    for provider_id in ("openai-vision-ocr", "openai-compatible-translation"):
        status = statuses[provider_id]
        assert status.ready is False
        assert status.state == ProviderState.NOT_CONFIGURED
        with pytest.raises(ProviderNotConfigured):
            registry.resolve(
                CAPABILITY_OCR if provider_id == "openai-vision-ocr" else CAPABILITY_TRANSLATION,
                provider_id,
            )

    # Dependency-free routes are ready; learned routes never are (R-007).
    assert statuses["inpaint-simple-fill"].ready is True
    assert statuses["inpaint-edge-bleed"].ready is True
    for provider_id in (
        "inpaint-manga-lama",
        "inpaint-aot-gan",
        "inpaint-brushnet",
        "inpaint-flux-fill",
    ):
        status = statuses[provider_id]
        assert status.ready is False
        assert status.error_code == ProviderNotImplemented.error_code
        with pytest.raises(ProviderNotImplemented):
            registry.resolve(CAPABILITY_INPAINT, provider_id)
    assert models.states() == ()


def test_disabled_profile_and_unknown_provider_fail_closed() -> None:
    registry = ProviderRegistry()
    registry.register(
        ProviderDescriptor(
            provider_id="local-thing",
            provider_type="local-thing",
            capabilities=frozenset({CAPABILITY_OCR}),
        ),
        lambda: object(),
    )
    assert registry.status("local-thing").ready is True
    registry.set_enabled("local-thing", False)
    status = registry.status("local-thing")
    assert status.state == ProviderState.DISABLED
    with pytest.raises(ProviderDisabled):
        registry.resolve(CAPABILITY_OCR, "local-thing")

    unknown = registry.status("never-registered")
    assert unknown.state == ProviderState.UNKNOWN
    with pytest.raises(ProviderError):
        registry.resolve(CAPABILITY_OCR, "never-registered")
    with pytest.raises(ProviderNotConfigured):
        registry.resolve(CAPABILITY_TRANSLATION, "local-thing")


def test_binding_resolution_honours_snapshot_flags_and_shape() -> None:
    registry = ProviderRegistry()
    registry.register(
        ProviderDescriptor(
            provider_id="ocr-a",
            provider_type="local",
            capabilities=frozenset({CAPABILITY_OCR}),
        ),
        lambda: "instance-a",
    )
    assert registry.resolve_binding(CAPABILITY_OCR, "ocr-a") == "instance-a"
    assert (
        registry.resolve_binding(CAPABILITY_OCR, {"provider_id": "ocr-a"}) == "instance-a"
    )
    with pytest.raises(ProviderError):
        registry.resolve_binding(CAPABILITY_OCR, {"provider_id": "ocr-a", "enabled": False})
    with pytest.raises(ProviderNotConfigured):
        registry.resolve_binding(CAPABILITY_OCR, None)
    with pytest.raises(ProviderNotConfigured):
        registry.resolve_binding(CAPABILITY_OCR, {"unrelated": "x"})


def test_sakura_readiness_follows_its_profile_configuration() -> None:
    """Configured == Ready is a configuration fact, not a reachability claim."""
    unconfigured, _ = build_provider_registry(settings={})
    assert unconfigured.status("sakura-local").state == ProviderState.NOT_CONFIGURED

    configured, _ = build_provider_registry(
        settings={
            "providers": {
                "profiles": {
                    "sakura-local": {
                        "base_url": "http://127.0.0.1:8080/v1",
                        "model": "sakura",
                    }
                }
            }
        }
    )
    status = configured.status("sakura-local")
    assert status.ready is True
    assert "connection test" in status.detail or status.detail == ""


def test_runtime_exposes_the_sakura_connection_test() -> None:
    from infrastructure.providers.runtime import build_provider_runtime

    runtime = build_provider_runtime(settings={})
    assert runtime.sakura_probe is None  # no transport injected
    assert runtime.sakura_base_url == "http://127.0.0.1:8080/v1"

    with_transport = build_provider_runtime(
        settings={
            "providers": {
                "profiles": {
                    "sakura-local": {
                        "base_url": "http://127.0.0.1:9999/v1",
                        "model": "sakura",
                    }
                }
            }
        },
        transport=object(),  # only used by the probe on demand
    )
    assert with_transport.sakura_probe is not None
    assert with_transport.sakura_base_url == "http://127.0.0.1:9999/v1"


def test_no_model_runtime_is_installed_in_this_environment() -> None:
    """Environment evidence for the registered BLOCKED items."""
    for module in ("torch", "diffusers", "numpy", "paddleocr", "manga_ocr"):
        assert importlib.util.find_spec(module) is None, (
            f"{module} unexpectedly present: the BLOCKED classification in "
            "doc/tasks/TASK-019.md assumes it is absent"
        )
