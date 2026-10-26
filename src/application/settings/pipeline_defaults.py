"""Persistence channel for pipeline defaults (TASK-050 AC ①②).

A run's frozen snapshots (D06 §49) are seeded from the single
``pipeline_defaults`` row. Before TASK-050 there was no application-side
way to change that row — production assembly never injected it, so every
run snapshotted empty settings/bindings and every region command died in
``PROVIDER_NOT_CONFIGURED``. This service is the application read/write
channel over that row; the storage write itself stays in the
infrastructure snapshot provider (bridged at assembly), so no second
persistence implementation is invented here.

Credentials never pass through this surface (AC ④): a binding only
*names* provider profiles, and settings hold plain configuration values;
secrets belong to the platform credential store (D03).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from .errors import BindingValidationError

_PROVIDER_KEYS = ("provider_id", "provider_profile_id", "id")


@dataclass(frozen=True)
class PipelineDefaults:
    """The four persisted pipeline defaults (one ``pipeline_defaults`` row)."""

    settings: Mapping[str, Any]
    provider_bindings: Mapping[str, Any]
    constraint_snapshot_ref: str | None
    context_policy: Mapping[str, Any]


class PipelineDefaultsService:
    """Read/validate/save pipeline defaults (TASK-050 AC ①②).

    ``load``/``save`` are storage bridges injected at assembly — this
    class never imports infrastructure (layering guard). Read-modify-write
    is not transactional across callers; the app has one writer thread
    (TASK-048), so the only interleaving is bounded the same way the
    pipeline store already is.
    """

    def __init__(
        self,
        *,
        load: Callable[[], PipelineDefaults],
        save: Callable[..., None],
        known_steps: frozenset[str],
    ) -> None:
        self._load = load
        self._save = save
        self._known_steps = known_steps

    def read(self) -> PipelineDefaults:
        return self._load()

    def save_provider_binding(self, step_type: str, binding: Any) -> PipelineDefaults:
        """Persist one step → provider binding, validated (AC ②).

        The accepted shapes mirror what the production fallback-chain
        reader understands: a provider id string, or a mapping naming one
        provider (optionally with a fallback list). Anything else must be
        rejected here, not discoverable only at run time.
        """
        if step_type not in self._known_steps:
            raise BindingValidationError(
                f"unknown pipeline step {step_type!r}; known steps: {sorted(self._known_steps)}"
            )
        _validate_binding_shape(step_type, binding)
        defaults = self.read()
        bindings = dict(defaults.provider_bindings)
        bindings[step_type] = binding
        self._save(
            settings=dict(defaults.settings),
            provider_bindings=bindings,
            constraint_snapshot_ref=defaults.constraint_snapshot_ref,
            context_policy=dict(defaults.context_policy),
        )
        return self.read()

    def clear_provider_binding(self, step_type: str) -> PipelineDefaults:
        """Remove one step binding; unknown steps stay a typed error."""
        if step_type not in self._known_steps:
            raise BindingValidationError(
                f"unknown pipeline step {step_type!r}; known steps: {sorted(self._known_steps)}"
            )
        defaults = self.read()
        self._save(
            settings=dict(defaults.settings),
            provider_bindings={
                key: value
                for key, value in defaults.provider_bindings.items()
                if key != step_type
            },
            constraint_snapshot_ref=defaults.constraint_snapshot_ref,
            context_policy=dict(defaults.context_policy),
        )
        return self.read()

    def save_settings_section(self, section: str, values: Mapping[str, Any]) -> PipelineDefaults:
        """Upsert one settings section (e.g. ``{"ocr": {"script": ...}}``)."""
        if not isinstance(section, str) or not section.strip():
            raise BindingValidationError("settings section name must be a non-empty string")
        if not isinstance(values, Mapping):
            raise BindingValidationError("settings section values must be a mapping")
        defaults = self.read()
        settings = dict(defaults.settings)
        settings[section] = dict(values)
        self._save(
            settings=settings,
            provider_bindings=dict(defaults.provider_bindings),
            constraint_snapshot_ref=defaults.constraint_snapshot_ref,
            context_policy=dict(defaults.context_policy),
        )
        return self.read()


def _validate_binding_shape(step_type: str, binding: Any) -> None:
    if isinstance(binding, str):
        if binding.strip():
            return
        raise BindingValidationError(f"binding for step {step_type!r} must not be blank")
    if isinstance(binding, Mapping):
        for key in _PROVIDER_KEYS:
            value = binding.get(key)
            if isinstance(value, str) and value.strip():
                return
        raise BindingValidationError(
            f"binding mapping for step {step_type!r} must name a provider "
            f"via one of {_PROVIDER_KEYS}"
        )
    raise BindingValidationError(
        f"binding for step {step_type!r} must be a provider id string or a mapping"
    )
