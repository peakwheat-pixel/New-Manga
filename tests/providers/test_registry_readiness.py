"""Provider readiness and fail-closed resolution (AC-OPTIONAL-001/002)."""

from __future__ import annotations

import importlib.machinery
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
    """AC-OPTIONAL-001/002: absent runtimes must not crash the assembly.

    "Absent" is now forced instead of inferred from the host, so this runs the
    same way on CI and on a workstation that happens to have the runtimes.
    """
    from tests.providers.env_sim import modules_state

    with modules_state(absent=frozenset({"manga_ocr", "paddleocr", "paddle"})):
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


def test_optional_providers_report_ready_when_their_runtimes_are_present() -> None:
    """The side nothing covered: satisfaction, not just absence.

    A registry that reported missing_dependency unconditionally would satisfy
    the absent-side assertions forever. This pins that satisfying the probes
    actually flips the state, so the absent-side test cannot be satisfied by a
    provider that never becomes ready at all.
    """
    from tests.providers.env_sim import modules_state

    # PIL is in the present set because manga-ocr declares (manga_ocr, PIL).
    # Leaving it out made this test pass only on hosts that happen to have PIL.
    present = frozenset({"manga_ocr", "paddleocr", "paddle", "PIL"})
    with modules_state(present=present):
        registry, _ = build_provider_registry(settings={})
        statuses = {status.provider_id: status for status in registry.statuses()}

        for provider_id in ("manga-ocr", "paddleocr-korean"):
            status = statuses[provider_id]
            assert status.ready is True, (
                "%s stayed %s with its requirements satisfied: %s"
                % (provider_id, status.state, status.missing_requirements)
            )
            assert status.state != ProviderState.MISSING_DEPENDENCY
            assert status.missing_requirements == ()
            registry.resolve(CAPABILITY_OCR, provider_id)


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
    """Environment evidence for the registered BLOCKED items.

    Original premise (TASK-019, 2026-09-17): this environment had NO model
    runtime ("no torch/diffusers/numpy, measured"), and TASK-019's BLOCKED
    classifications for weight-dependent quality ACs assume exactly that —
    the assertion loop below freezes that environment evidence so any drift
    would be flagged.

    That premise is INVALIDATED (R-B2: not "superseded and relocated") by
    user-approved requirements changes: T1.1.1 put torch==2.14.0 into
    requirements.txt (M2-PROD-DETECT-1 added transformers==5.17.0 +
    safetensors), so the dev/main venv intentionally carries the ML stack
    and the TASK-019 environment evidence has nothing left to guard here.
    Separately — and with the OPPOSITE direction — release-side ML-closure
    COMPLETENESS is guaranteed independently at BUILD time by
    ``packaging/m2ac5/core_sidecar.spec`` ``_assert_ml_closure`` (it fails
    when the ML modules are MISSING from the frozen PYZ; per-entry warn
    archives, M2-PROD-DETECT-2 GATE evidence). Do not conflate the two:
    that build gate asserts ML PRESENCE in the shipped closure; this test
    asserted ML ABSENCE in the dev environment.

    Conditioning (M2-FIX-REGISTRY-READINESS-ENV, option a): when torch is
    present (the T1.1.1+ main-venv marker), skip with an explicit reason;
    on a torch-free environment the ORIGINAL assertion loop below runs
    verbatim, keeping the full TASK-019-era discrimination power
    (``diffusers``/``paddleocr``/``manga_ocr`` remain unapproved and are
    still asserted absent).

    Known limitations (DSH r1 R-B3/R-B4):

    - the skip gate probes ONLY ``torch`` (the same probe the loop itself
      uses): in a torch-free environment all five modules are still asserted
      verbatim, so a numpy-only environment still FAILS as drift; in an ML
      venv the absent-module facts for the unapproved providers are covered
      by ``test_real_environment_reports_optional_providers_as_not_ready``
      (registry probes) — the narrow gate is intentional, not flakiness;
    - ``importlib.util.find_spec`` is an EXISTENCE probe, not an
      importability probe: a half-installed torch (directory present but
      import broken) also trips the skip. This is the same probe the
      original assertion loop used, so it is a known blind spot inherited
      verbatim, not a regression of this conditioning.
    """
    # Gate intentionally probes only torch (R-B3): see docstring — a
    # torch-free environment keeps all five verbatim assertions.
    if importlib.util.find_spec("torch") is not None:
        pytest.skip(
            "dev venv intentionally carries the ML stack since T1.1.1 "
            "(user-approved requirements: torch==2.14.0, transformers=="
            "5.17.0) — the TASK-019-era 'no model runtime in this "
            "environment' evidence is INVALIDATED, nothing left to guard "
            "here; separately, release-side ML-closure completeness is "
            "independently guaranteed at build time by packaging/m2ac5 "
            "core_sidecar.spec _assert_ml_closure (M2-PROD-DETECT-2), "
            "which is the opposite-direction assertion and must not be "
            "read as this test's replacement"
        )
    for module in ("torch", "diffusers", "numpy", "paddleocr", "manga_ocr"):
        assert importlib.util.find_spec(module) is None, (
            f"{module} unexpectedly present: the BLOCKED classification in "
            "doc/tasks/TASK-019.md assumes it is absent"
        )


_ABSENT_ALL = {
    module: None for module in ("torch", "diffusers", "numpy", "paddleocr", "manga_ocr")
}
_FAKE_SPEC = importlib.machinery.ModuleSpec("paddleocr", None)


@pytest.mark.parametrize(
    ("spec_map", "expect"),
    [
        pytest.param(
            _ABSENT_ALL,
            "pass",
            id="torch-free-bare-env-runs-verbatim-and-passes",
        ),
        pytest.param(
            _ABSENT_ALL | {"paddleocr": _FAKE_SPEC},
            "fail",
            id="torch-free-paddleocr-drift-fails-with-original-message",
        ),
    ],
)
def test_environment_assertion_discrimination_probe(
    spec_map: dict, expect: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Re-runnable discrimination evidence for the conditioned test (R-B5).

    Stubs ``importlib.util.find_spec`` and drives
    ``test_no_model_runtime_is_installed_in_this_environment`` directly, so
    BOTH conditioning paths stay provable on ANY machine — including ML
    venvs, where the real test would skip and the torch-free branch would
    otherwise never execute:

    - bare torch-free environment -> the verbatim assertion loop runs and
      passes (no skip, no fail);
    - torch-free + a drifted ``paddleocr`` -> the ORIGINAL TASK-019
      AssertionError fires.
    """
    monkeypatch.setattr(
        importlib.util, "find_spec", lambda name: spec_map.get(name)
    )
    if expect == "pass":
        test_no_model_runtime_is_installed_in_this_environment()
    else:
        with pytest.raises(
            AssertionError, match="paddleocr unexpectedly present"
        ):
            test_no_model_runtime_is_installed_in_this_environment()

# ---------------------------------------------------------------------------
# SETTINGS-OPEN-B-1 review B1: ``descriptor()`` is the read-only declaration
# reader used by the handlers (the provider instance does not repeat
# ``requires_gpu`` / ``supports_cpu_fallback`` in production).
# ---------------------------------------------------------------------------


def test_descriptor_returns_the_static_declaration_or_none() -> None:
    descriptor = ProviderDescriptor(
        provider_id="local-ocr",
        provider_type="local",
        capabilities=frozenset({CAPABILITY_OCR}),
        requires_gpu=True,
        supports_cpu_fallback=True,
    )
    registry = ProviderRegistry()
    registry.register(descriptor, lambda: object())

    assert registry.descriptor("local-ocr") is descriptor
    # an unknown id is a lookup miss, never a raise (resolution stays closed)
    assert registry.descriptor("never-registered") is None


def test_descriptor_honours_binding_aliases_per_capability() -> None:
    descriptor = ProviderDescriptor(
        provider_id="local-ocr",
        provider_type="local",
        capabilities=frozenset({CAPABILITY_OCR}),
        requires_gpu=True,
        supports_cpu_fallback=True,
    )
    registry = ProviderRegistry(
        binding_aliases={
            ("user-ocr-profile", CAPABILITY_OCR): "local-ocr",
            ("user-translate-profile", CAPABILITY_TRANSLATION): "local-ocr",
        }
    )
    registry.register(descriptor, lambda: object())

    assert (
        registry.descriptor("user-ocr-profile", capability=CAPABILITY_OCR)
        is descriptor
    )
    # the alias is per capability: the same profile id does not resolve on the
    # wrong capability, and the exact-id lookup only sees registry ids.
    assert (
        registry.descriptor("user-ocr-profile", capability=CAPABILITY_TRANSLATION)
        is None
    )
    assert registry.descriptor("user-ocr-profile") is None
