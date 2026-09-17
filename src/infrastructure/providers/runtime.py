"""Provider runtime assembly: descriptors, readiness, models and policies.

One place decides which providers exist in this build, what each of them
requires and how the pipeline reaches them. Everything here is declarative so
that ``ProviderRegistry.status()`` can answer AC-OPTIONAL-002 honestly:

- the optional local runtimes (``manga_ocr``/``paddleocr``/``torch``) are
  probed, never imported at assembly time;
- remote endpoints are configured through ``settings["providers"]["profiles"]``
  — with none configured they are ``not_configured``, not silently mocked;
- the learned inpaint routes are registered with ``implements=False`` so a
  satisfied dependency list still cannot make them runnable (TASK-018 R-007).

The settings contract (documented for the Settings UI slice):

``settings["providers"]["profiles"][provider_id]`` = ``{base_url, model,
credential_ref, enabled, options}``
``settings["providers"]["retry"]`` = ``{max_attempts, backoff_seconds}``
``settings["providers"]["models"][model_id]`` = ``{weights_path, sha256,
size_bytes, source_url, requires_gpu}``
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from infrastructure.devices.manager import DeviceManager
from infrastructure.providers.dependencies import KIND_CREDENTIAL, KIND_ENDPOINT, KIND_MODULE, Requirement
from application.translation.inpaint.router import RoutePolicy
from infrastructure.providers.models import ModelManager, ModelSpec
from infrastructure.providers.ocr_local import (
    PROVIDER_MANGA_OCR,
    PROVIDER_PADDLE_KOREAN,
    MangaOcrProvider,
    PaddleKoreanOcrProvider,
)
from infrastructure.providers.ocr_vision import PROVIDER_VISION_OCR, VisionOcrProvider
from infrastructure.providers.inpaint_routes import (
    EdgeBleedProvider,
    SimpleFillProvider,
)
from infrastructure.providers.openai_client import (
    OpenAiCompatibleClient,
    OpenAiCompatibleConfig,
)
from infrastructure.providers.registry import ProviderDescriptor, ProviderRegistry
from infrastructure.providers.retry import RetryPolicy
from infrastructure.providers.sakura_probe import SakuraProbe
from infrastructure.providers.translation_openai import (
    PROVIDER_OPENAI_TRANSLATION,
    PROVIDER_SAKURA,
    OpenAiTranslationProvider,
    sakura_config,
)
from ports.network.transport import Transport
from ports.providers.profiles import (
    CAPABILITY_DETECTION,
    CAPABILITY_INPAINT,
    CAPABILITY_OCR,
    CAPABILITY_TRANSLATION,
)

PROVIDER_VISION_DETECTION = "openai-vision-detection"
PROVIDER_INPAINT_SIMPLE_FILL = "inpaint-simple-fill"
PROVIDER_INPAINT_EDGE_BLEED = "inpaint-edge-bleed"
PROVIDER_INPAINT_MANGA_LAMA = "inpaint-manga-lama"
PROVIDER_INPAINT_AOT_GAN = "inpaint-aot-gan"
PROVIDER_INPAINT_BRUSHNET = "inpaint-brushnet"
PROVIDER_INPAINT_FLUX = "inpaint-flux-fill"

DEFAULT_ROUTE_POLICY = RoutePolicy(
    allowed_routes=("simple-fill", "edge-bleed"),
    fallback_routes=(),
    color_route="brushnet",
    requirements={"brushnet": False, "flux-fill": False},
)

DEFAULT_RETRY_POLICY = RetryPolicy(max_attempts=2, backoff_seconds=1.0)


@dataclass
class ProviderRuntime:
    """The assembled provider side of the application."""

    registry: ProviderRegistry
    devices: DeviceManager
    models: ModelManager
    transport: Transport | None = None
    credential_resolver: Callable[[str], str | None] | None = None
    retry_policy: RetryPolicy = field(default_factory=lambda: DEFAULT_RETRY_POLICY)
    route_policy: RoutePolicy = field(default_factory=lambda: DEFAULT_ROUTE_POLICY)
    sakura_probe: SakuraProbe | None = None
    sakura_base_url: str = ""

    def readiness_report(self) -> tuple[dict, ...]:
        return self.registry.readiness_report()

    def model_report(self) -> tuple[dict, ...]:
        return tuple(state.as_dict() for state in self.models.states())

    def heavy_runner(self, *, requires_gpu: bool, call):
        return self.devices.run_guarded(requires_gpu=requires_gpu, call=call)

    def status(self) -> dict:
        return {
            "providers": list(self.readiness_report()),
            "models": list(self.model_report()),
            "gpu": self.devices.gpu_info().as_dict(),
            "route_policy": self.route_policy.__dict__,
        }


def _profile_settings(settings: Mapping[str, Any]) -> Mapping[str, Any]:
    providers = settings.get("providers")
    if not isinstance(providers, Mapping):
        return {}
    profiles = providers.get("profiles")
    return profiles if isinstance(profiles, Mapping) else {}


def _provider_settings(settings: Mapping[str, Any], provider_id: str) -> Mapping[str, Any]:
    profile = _profile_settings(settings).get(provider_id)
    return profile if isinstance(profile, Mapping) else {}


def _model_specs(settings: Mapping[str, Any]) -> tuple[ModelSpec, ...]:
    providers = settings.get("providers")
    if not isinstance(providers, Mapping):
        return ()
    models = providers.get("models")
    if not isinstance(models, Mapping):
        return ()
    specs: list[ModelSpec] = []
    for model_id, raw in models.items():
        if not isinstance(raw, Mapping):
            continue
        specs.append(
            ModelSpec(
                model_id=str(model_id),
                provider_id=str(raw.get("provider_id", "")),
                weights_path=str(raw.get("weights_path", "")),
                expected_sha256=str(raw.get("sha256", "")),
                expected_size_bytes=(
                    int(raw["size_bytes"]) if raw.get("size_bytes") is not None else None
                ),
                source_url=str(raw.get("source_url", "")),
                requires_gpu=bool(raw.get("requires_gpu", False)),
            )
        )
    return tuple(specs)


def _retry_policy(settings: Mapping[str, Any]) -> RetryPolicy:
    providers = settings.get("providers")
    raw = providers.get("retry") if isinstance(providers, Mapping) else None
    if not isinstance(raw, Mapping):
        return DEFAULT_RETRY_POLICY
    return RetryPolicy(
        max_attempts=int(raw.get("max_attempts", DEFAULT_RETRY_POLICY.max_attempts)),
        backoff_seconds=float(
            raw.get("backoff_seconds", DEFAULT_RETRY_POLICY.backoff_seconds)
        ),
    )


def _openai_config(
    provider_id: str,
    provider_type: str,
    settings: Mapping[str, Any],
) -> OpenAiCompatibleConfig:
    profile = _provider_settings(settings, provider_id)
    return OpenAiCompatibleConfig(
        provider_id=provider_id,
        provider_type=provider_type,
        base_url=str(profile.get("base_url", "")),
        model=str(profile.get("model", "")),
        credential_ref=(
            str(profile["credential_ref"]) if profile.get("credential_ref") else None
        ),
        extra_options=tuple(
            (str(key), str(value))
            for key, value in dict(profile.get("options", {}) or {}).items()
        ),
    )


def _openai_requirements(
    provider_id: str, settings: Mapping[str, Any]
) -> tuple[Requirement, ...]:
    profile = _provider_settings(settings, provider_id)
    base_url = str(profile.get("base_url", ""))
    model = str(profile.get("model", ""))
    requirements: list[Requirement] = [
        Requirement(KIND_ENDPOINT, f"{base_url}|{model}", detail="remote endpoint")
    ]
    if profile.get("credential_ref"):
        requirements.append(
            Requirement(KIND_CREDENTIAL, str(profile["credential_ref"]))
        )
    return tuple(requirements)


def build_provider_registry(
    *,
    settings: Mapping[str, Any] | None = None,
    transport: Transport | None = None,
    credential_resolver: Callable[[str], str | None] | None = None,
    models: ModelManager | None = None,
) -> tuple[ProviderRegistry, ModelManager]:
    """Register every provider this build knows about."""
    settings = settings or {}
    model_manager = models or ModelManager()
    for spec in _model_specs(settings):
        model_manager.register(spec)

    registry = ProviderRegistry(credential_resolver=credential_resolver)

    def vision_client(provider_id: str, provider_type: str) -> Callable[[], Any]:
        def factory() -> VisionOcrProvider:
            if transport is None:
                raise _no_transport(provider_id)
            config = _openai_config(provider_id, provider_type, settings)
            client = OpenAiCompatibleClient(
                config, transport, credential_resolver=credential_resolver
            )
            return VisionOcrProvider(config=config, client=client)

        return factory

    def translation_factory(
        provider_id: str, provider_type: str, config: OpenAiCompatibleConfig | None = None
    ) -> Callable[[], Any]:
        def factory() -> OpenAiTranslationProvider:
            if transport is None:
                raise _no_transport(provider_id)
            actual = config or _openai_config(provider_id, provider_type, settings)
            client = OpenAiCompatibleClient(
                actual, transport, credential_resolver=credential_resolver
            )
            return OpenAiTranslationProvider(
                config=actual, client=client, provider_id=provider_id, provider_type=provider_type
            )

        return factory

    # -- detection -----------------------------------------------------
    registry.register(
        ProviderDescriptor(
            provider_id=PROVIDER_VISION_DETECTION,
            provider_type="openai-compatible-vision",
            capabilities=frozenset({CAPABILITY_DETECTION}),
            requirements=_openai_requirements(PROVIDER_VISION_DETECTION, settings),
            note="detection port only; no Detect AC is assigned to TASK-019",
        ),
        vision_client(PROVIDER_VISION_DETECTION, "openai-compatible-vision"),
    )

    # -- OCR -----------------------------------------------------------
    registry.register(
        ProviderDescriptor(
            provider_id=PROVIDER_MANGA_OCR,
            provider_type="local-manga-ocr",
            capabilities=frozenset({CAPABILITY_OCR}),
            requirements=(
                Requirement(KIND_MODULE, "manga_ocr"),
                Requirement(KIND_MODULE, "PIL"),
            ),
            requires_gpu=False,
            supports_cpu_fallback=True,
            note="recognition-only candidate; never supplies detection boxes",
        ),
        MangaOcrProvider,
    )
    registry.register(
        ProviderDescriptor(
            provider_id=PROVIDER_PADDLE_KOREAN,
            provider_type="local-paddleocr",
            capabilities=frozenset({CAPABILITY_OCR}),
            requirements=(
                Requirement(KIND_MODULE, "paddleocr"),
                Requirement(KIND_MODULE, "paddle"),
            ),
            requires_gpu=False,
            supports_cpu_fallback=True,
            note="Korean Webtoon route target (D06 §7.2)",
        ),
        PaddleKoreanOcrProvider,
    )
    registry.register(
        ProviderDescriptor(
            provider_id=PROVIDER_VISION_OCR,
            provider_type="openai-compatible-vision",
            capabilities=frozenset({CAPABILITY_OCR}),
            requirements=_openai_requirements(PROVIDER_VISION_OCR, settings),
            note="explicit Vision fallback for art text / low-quality OCR",
        ),
        vision_client(PROVIDER_VISION_OCR, "openai-compatible-vision"),
    )

    # -- translation ---------------------------------------------------
    registry.register(
        ProviderDescriptor(
            provider_id=PROVIDER_OPENAI_TRANSLATION,
            provider_type="openai-compatible",
            capabilities=frozenset({CAPABILITY_TRANSLATION}),
            requirements=_openai_requirements(PROVIDER_OPENAI_TRANSLATION, settings),
        ),
        translation_factory(PROVIDER_OPENAI_TRANSLATION, "openai-compatible"),
    )
    registry.register(
        ProviderDescriptor(
            provider_id=PROVIDER_SAKURA,
            provider_type="local-sakura",
            capabilities=frozenset({CAPABILITY_TRANSLATION}),
            requirements=(
                Requirement(
                    KIND_ENDPOINT,
                    f"{_provider_settings(settings, PROVIDER_SAKURA).get('base_url', '')}|"
                    f"{_provider_settings(settings, PROVIDER_SAKURA).get('model', '')}",
                    detail="local Sakura endpoint (D02 §6.2.2)",
                ),
            ),
            note=(
                "local OpenAI-compatible Sakura server; readiness means "
                "'configured' — reachability is reported by the connection test"
            ),
        ),
        translation_factory(
            PROVIDER_SAKURA,
            "local-sakura",
            config=sakura_config(
                # No implicit default here: an unconfigured profile stays
                # Not-Configured instead of pretending a service is there.
                base_url=str(_provider_settings(settings, PROVIDER_SAKURA).get("base_url", "")),
                model=str(_provider_settings(settings, PROVIDER_SAKURA).get("model", "")),
            ),
        ),
    )

    # -- inpaint -------------------------------------------------------
    registry.register(
        ProviderDescriptor(
            provider_id=PROVIDER_INPAINT_SIMPLE_FILL,
            provider_type="local-simple-fill",
            capabilities=frozenset({CAPABILITY_INPAINT}),
            note="dependency-free baseline route (TASK-018)",
        ),
        SimpleFillProvider,
    )
    registry.register(
        ProviderDescriptor(
            provider_id=PROVIDER_INPAINT_EDGE_BLEED,
            provider_type="local-edge-bleed",
            capabilities=frozenset({CAPABILITY_INPAINT}),
            requires_gpu=False,
            supports_cpu_fallback=True,
            note="structural baseline, not a learned model",
        ),
        EdgeBleedProvider,
    )
    for provider_id, requirement_modules, label in (
        (PROVIDER_INPAINT_MANGA_LAMA, ("torch", "diffusers", "numpy"), "Manga LaMa"),
        (PROVIDER_INPAINT_AOT_GAN, ("torch", "numpy"), "AOT-GAN"),
        (PROVIDER_INPAINT_BRUSHNET, ("torch", "diffusers", "numpy"), "BrushNet/PowerPaint"),
        (PROVIDER_INPAINT_FLUX, ("torch", "diffusers"), "FLUX Fill"),
    ):
        registry.register(
            ProviderDescriptor(
                provider_id=provider_id,
                provider_type="local-diffusion",
                capabilities=frozenset({CAPABILITY_INPAINT}),
                requirements=tuple(Requirement(KIND_MODULE, name) for name in requirement_modules),
                requires_gpu=True,
                supports_cpu_fallback=False,
                heavy_gpu=True,
                implements=False,
                note=f"{label} has no implementation in this build (TASK-018)",
            ),
            None,
        )

    return registry, model_manager


def build_provider_runtime(
    *,
    settings: Mapping[str, Any] | None = None,
    transport: Transport | None = None,
    credential_resolver: Callable[[str], str | None] | None = None,
    devices: DeviceManager | None = None,
) -> ProviderRuntime:
    settings = settings or {}
    registry, models = build_provider_registry(
        settings=settings,
        transport=transport,
        credential_resolver=credential_resolver,
    )
    sakura_profile = _provider_settings(settings, PROVIDER_SAKURA)
    sakura_base_url = str(sakura_profile.get("base_url", "http://127.0.0.1:8080/v1"))
    probe = (
        SakuraProbe(transport=transport, provider_id=PROVIDER_SAKURA)
        if transport is not None
        else None
    )
    runtime = ProviderRuntime(
        registry=registry,
        devices=devices or DeviceManager(),
        models=models,
        transport=transport,
        credential_resolver=credential_resolver,
        retry_policy=_retry_policy(settings),
        route_policy=_route_policy(settings),
        sakura_probe=probe,
        sakura_base_url=sakura_base_url,
    )
    return runtime


def _route_policy(settings: Mapping[str, Any]) -> RoutePolicy:
    inpaint = settings.get("inpaint")
    raw = inpaint.get("route_policy") if isinstance(inpaint, Mapping) else None
    if not isinstance(raw, Mapping):
        return DEFAULT_ROUTE_POLICY
    allowed = tuple(str(route) for route in raw.get("allowed_routes", ()))
    fallbacks = tuple(str(route) for route in raw.get("fallback_routes", ()))
    color_route = raw.get("color_route")
    if color_route and str(color_route) not in allowed:
        allowed = (*allowed, str(color_route))
    return RoutePolicy(
        allowed_routes=allowed or DEFAULT_ROUTE_POLICY.allowed_routes,
        fallback_routes=fallbacks,
        color_route=str(color_route) if color_route else DEFAULT_ROUTE_POLICY.color_route,
        requirements={
            str(route): bool(value)
            for route, value in dict(raw.get("requirements", {})).items()
        },
    )


def _no_transport(provider_id: str):
    from ports.providers.errors import ProviderUnavailable

    return ProviderUnavailable(
        "no network transport was injected into the provider runtime",
        provider_id=provider_id,
        stage="assemble",
    )


__all__ = [
    "DEFAULT_ROUTE_POLICY",
    "DEFAULT_RETRY_POLICY",
    "PROVIDER_INPAINT_AOT_GAN",
    "PROVIDER_INPAINT_BRUSHNET",
    "PROVIDER_INPAINT_EDGE_BLEED",
    "PROVIDER_INPAINT_FLUX",
    "PROVIDER_INPAINT_MANGA_LAMA",
    "PROVIDER_INPAINT_SIMPLE_FILL",
    "PROVIDER_MANGA_OCR",
    "PROVIDER_PADDLE_KOREAN",
    "PROVIDER_SAKURA",
    "PROVIDER_VISION_DETECTION",
    "PROVIDER_VISION_OCR",
    "ProviderRuntime",
    "build_provider_registry",
    "build_provider_runtime",
]
