"""Requirement probes for optional provider runtimes (TASK-018 R-002 style).

A provider is only Ready when its *real* requirements are satisfied. Nothing
here downloads or installs anything, and no requirement is assumed: modules
are probed with ``importlib.util.find_spec``, weights by file existence plus
an optional SHA-256, endpoints by configured non-empty URL/model, credentials
by vault lookup through the caller-supplied resolver.

TASK-019 runs without ``torch``/``diffusers``/``numpy``/``paddleocr``/
``manga_ocr``, so these probes are exactly what turns every learned route into
an honest ``missing_dependency`` instead of a fabricated success.
"""

from __future__ import annotations

import hashlib
import importlib.util
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from ports.providers.errors import (
    MissingCredential,
    ProviderDependencyMissing,
    ProviderNotConfigured,
)

KIND_MODULE = "module"
KIND_WEIGHT = "weight"
KIND_ENDPOINT = "endpoint"
KIND_CREDENTIAL = "credential"
ALL_KINDS = frozenset({KIND_MODULE, KIND_WEIGHT, KIND_ENDPOINT, KIND_CREDENTIAL})

SATISFIED = "satisfied"
MISSING = "missing"


@dataclass(frozen=True)
class Requirement:
    """One declared requirement of a provider descriptor."""

    kind: str
    name: str
    detail: str = ""

    def __post_init__(self) -> None:
        if self.kind not in ALL_KINDS:
            raise ValueError(f"unknown requirement kind: {self.kind!r}")
        if not self.name:
            raise ValueError("requirement name must not be empty")


@dataclass(frozen=True)
class RequirementProbe:
    requirement: Requirement
    satisfied: bool
    detail: str = ""

    @property
    def state(self) -> str:
        return SATISFIED if self.satisfied else MISSING

    def as_dict(self) -> dict:
        return {
            "kind": self.requirement.kind,
            "name": self.requirement.name,
            "state": self.state,
            "detail": self.detail or self.requirement.detail,
        }


def sha256_file(path: str | Path) -> str:
    """Streaming SHA-256 of a file (used for weight verification)."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe_module(name: str) -> RequirementProbe:
    requirement = Requirement(KIND_MODULE, name)
    try:
        satisfied = importlib.util.find_spec(name) is not None
    except (ImportError, ValueError) as error:
        return RequirementProbe(requirement, False, f"probe failed: {error!r}")
    return RequirementProbe(
        requirement,
        satisfied,
        "" if satisfied else f"module {name!r} is not installed",
    )


def probe_weight(
    path: str | Path | None,
    *,
    expected_sha256: str | None = None,
    verify_hash: bool = False,
    name: str = "",
) -> RequirementProbe:
    """Probe a local weight file; hashing is opt-in (it can be very slow).

    AC-MODEL-002: a partial file must not pass. With ``verify_hash`` the
    SHA-256 is compared; without it only presence and non-zero size are
    proven, and that is stated in the detail instead of implied.
    """
    label = name or (str(path) if path else "weights")
    requirement = Requirement(KIND_WEIGHT, label, detail="local model weights")
    if not path:
        return RequirementProbe(requirement, False, "no weights path configured")
    candidate = Path(path)
    if not candidate.is_file():
        return RequirementProbe(requirement, False, f"weights not found: {candidate}")
    if candidate.stat().st_size == 0:
        return RequirementProbe(requirement, False, f"weights are empty: {candidate}")
    if verify_hash and expected_sha256:
        actual = sha256_file(candidate)
        if actual != expected_sha256:
            return RequirementProbe(
                requirement,
                False,
                f"weights hash mismatch: {actual} != {expected_sha256}",
            )
        return RequirementProbe(requirement, True, "weights hash verified")
    return RequirementProbe(
        requirement, True, "weights present (hash not verified in this environment)"
    )


def probe_endpoint(base_url: str, model: str = "") -> RequirementProbe:
    requirement = Requirement(KIND_ENDPOINT, base_url or "endpoint")
    if not base_url or not base_url.strip():
        return RequirementProbe(requirement, False, "no base_url configured")
    if not model or not model.strip():
        return RequirementProbe(
            requirement, False, "no model configured for this endpoint"
        )
    return RequirementProbe(requirement, True, f"endpoint {base_url} / {model}")


def probe_credential(
    credential_ref: str | None,
    resolver: Callable[[str], str | None] | None,
) -> RequirementProbe:
    requirement = Requirement(KIND_CREDENTIAL, credential_ref or "credential")
    if not credential_ref:
        return RequirementProbe(requirement, False, "no credential_ref configured")
    if resolver is None:
        return RequirementProbe(
            requirement, False, "no credential vault available to this assembly"
        )
    try:
        secret = resolver(credential_ref)
    except Exception as error:  # noqa: BLE001 - reported, never raised upward
        return RequirementProbe(requirement, False, f"credential lookup failed: {error!r}")
    if not secret:
        return RequirementProbe(requirement, False, f"credential {credential_ref!r} is empty")
    return RequirementProbe(requirement, True, "credential resolved")


def evaluate_requirements(
    requirements: Iterable[Requirement],
    *,
    credential_resolver: Callable[[str], str | None] | None = None,
) -> tuple[RequirementProbe, ...]:
    """Probe every requirement; order is preserved for stable diagnostics."""
    probes: list[RequirementProbe] = []
    for requirement in requirements:
        if requirement.kind == KIND_MODULE:
            probes.append(probe_module(requirement.name))
        elif requirement.kind == KIND_WEIGHT:
            probes.append(probe_weight(requirement.name, name=requirement.name))
        elif requirement.kind == KIND_ENDPOINT:
            base_url, _, model = requirement.name.partition("|")
            probes.append(probe_endpoint(base_url, model))
        elif requirement.kind == KIND_CREDENTIAL:
            probes.append(probe_credential(requirement.name, credential_resolver))
    return tuple(probes)


def failure_for(probes: Sequence[RequirementProbe], *, provider_id: str = "") -> Exception | None:
    """Map the first missing requirement onto the closed error taxonomy."""
    for probe in probes:
        if probe.satisfied:
            continue
        requirement = probe.requirement
        if requirement.kind == KIND_MODULE and requirement.name in {"torch", "diffusers", "numpy"}:
            return ProviderDependencyMissing(
                probe.detail, provider_id=provider_id, stage="requirements"
            )
        if requirement.kind == KIND_WEIGHT:
            return ProviderDependencyMissing(
                probe.detail, provider_id=provider_id, stage="requirements"
            )
        if requirement.kind == KIND_MODULE:
            return ProviderDependencyMissing(
                probe.detail, provider_id=provider_id, stage="requirements"
            )
        if requirement.kind == KIND_CREDENTIAL:
            return MissingCredential(
                probe.detail, provider_id=provider_id, stage="requirements"
            )
        return ProviderNotConfigured(
            probe.detail, provider_id=provider_id, stage="requirements"
        )
    return None
