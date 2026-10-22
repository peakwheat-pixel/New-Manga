"""Per-section write validation for ``settings.update_section``.

The settings page opens its previously disabled categories in batches. Batch A
(``doc/design/SETTINGS_SECTION_SCHEMAS.md`` §3.1-§3.4) freezes the key set and
the value domains of ``ocr`` / ``translate`` / ``inpaint`` / ``typeset``;
batch B-1 (§4.1-§4.2) adds ``model_gpu`` and ``tasks``. This
module is the Core-side gate that runs BEFORE
``PipelineDefaultsService.save_settings_section`` persists anything (design
§2.2/§3.5, the M2-SFX-ENTRY r1 R4 fail-closed discipline: a value that would
fail the assembly-time reader must be rejected on write so it can never become
an unrecoverable startup block).

Contract:

- a known section accepts ONLY its whitelisted keys and returns the normalized
  values (same keys, JSON types converted to their Python canonical form);
- an illegal key or value raises :class:`SettingsSectionError` (a ``ValueError``
  subclass) naming the section, the field and the accepted domain;
- an unknown section returns ``None`` -- the historical pass-through for
  sections whose schema is not frozen yet stays in place (design §3.5).

The module is deliberately standard-library only: bootstrap wiring, not a
second settings store, and no import from infrastructure.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

__all__ = ["SettingsSectionError", "validate_settings_section"]


class SettingsSectionError(ValueError):
    """A settings section write violates the frozen batch-A schema.

    The message names the section, the offending field and the accepted
    domain; the Core dispatch layer projects it to ``INVALID_REQUEST``
    (``validation``) before any persistence happens.
    """


@dataclass(frozen=True)
class _Rule:
    """One value-domain rule (kind-based; ranges are inclusive)."""

    kind: str  # enum | int | float | nullable_float | color | bool
    allowed: frozenset[str] = frozenset()
    minimum: float = 0.0
    maximum: float = 0.0


_OCR_RULES: dict[str, _Rule] = {
    "script": _Rule(
        "enum", frozenset({"japanese", "korean", "chinese", "latin"})
    ),
    "direction": _Rule("enum", frozenset({"horizontal", "vertical"})),
}

_TRANSLATE_RULES: dict[str, _Rule] = {
    "context_pages": _Rule("int", minimum=1, maximum=5),
    "context_token_budget": _Rule("int", minimum=200, maximum=8000),
}

_INPAINT_RULES: dict[str, _Rule] = {
    "preferred_quality": _Rule("enum", frozenset({"fast", "balanced", "quality"})),
    "background_complexity": _Rule("enum", frozenset({"low", "medium", "high"})),
    "dilate_radius": _Rule("int", minimum=0, maximum=10),
    "erode_radius": _Rule("int", minimum=0, maximum=10),
}

_TYPESET_RULES: dict[str, _Rule] = {
    "text_color": _Rule("color"),
    "stroke_enabled": _Rule("bool"),
    "stroke_color": _Rule("color"),
    "stroke_width": _Rule("float", minimum=0.0, maximum=20.0),
    "line_spacing": _Rule("float", minimum=1.0, maximum=3.0),
    # ``right`` is rejected: neither compositor implements it yet (review M2).
    "text_align": _Rule("enum", frozenset({"left", "center"})),
    "text_direction": _Rule(
        "enum", frozenset({"auto", "horizontal", "vertical"})
    ),
    "auto_font_size": _Rule("bool"),
    "font_size_offset": _Rule("int", minimum=-5, maximum=5),
    "manual_font_size": _Rule("nullable_float", minimum=1.0, maximum=500.0),
}

#: Batch B-1 (design §4.1): the Run-time device preference and the user half of
#: the D06 §82 CPU-fallback decision. ``auto`` is the historical behaviour.
_MODEL_GPU_RULES: dict[str, _Rule] = {
    "device_preference": _Rule("enum", frozenset({"auto", "cpu", "gpu"})),
    "allow_cpu_fallback": _Rule("bool"),
}

#: Batch B-1 (design §4.2): the per-Run retry policy. Bounds match the retry
#: contract ("1-3 attempts"): a larger value is not a user-facing capability.
_TASKS_RULES: dict[str, _Rule] = {
    "retry_max_attempts": _Rule("int", minimum=1, maximum=3),
    "retry_backoff_seconds": _Rule("float", minimum=0.1, maximum=30.0),
}

#: Frozen sections. Unknown names are NOT listed here: they stay on the
#: pre-existing pass-through (design §3.5, backwards compatibility).
_SECTIONS: dict[str, dict[str, _Rule]] = {
    "ocr": _OCR_RULES,
    "translate": _TRANSLATE_RULES,
    "inpaint": _INPAINT_RULES,
    "typeset": _TYPESET_RULES,
    "model_gpu": _MODEL_GPU_RULES,
    "tasks": _TASKS_RULES,
}

_HEX_DIGITS = frozenset("0123456789abcdefABCDEF")


def validate_settings_section(
    section: str, values: Mapping[str, Any]
) -> dict[str, Any] | None:
    """Validate one section write and return its normalized values.

    ``None`` means "section not frozen in a settings batch": the caller keeps
    the historical whole-section upsert unchanged. A known section either
    returns every key normalized, or raises :class:`SettingsSectionError`;
    there is no partial acceptance.
    """
    rules = _SECTIONS.get(section)
    if rules is None:
        return None
    normalized: dict[str, Any] = {}
    for key, value in values.items():
        rule = rules.get(key)
        if rule is None:
            raise SettingsSectionError(
                f"settings.update_section {section} does not accept key "
                f"{key!r}; allowed keys: {sorted(rules)}"
            )
        normalized[key] = _normalize(section, key, rule, value)
    if section == "typeset":
        _validate_typeset_cross_fields(normalized)
    return normalized


def _validate_typeset_cross_fields(normalized: Mapping[str, Any]) -> None:
    """Cross-field rule for ``typeset`` (review r1 M1).

    The section is replaced as a whole, so an omitted ``manual_font_size`` is
    null after the write. ``auto_font_size=False`` without a manual size makes
    ``resolve_font_size`` raise for every region (render fail-closed); reject
    that combination on write instead of storing a render-blocking setting.
    """
    if (
        normalized.get("auto_font_size") is False
        and normalized.get("manual_font_size") is None
    ):
        raise SettingsSectionError(
            "settings.update_section typeset.manual_font_size is required "
            "when typeset.auto_font_size is false"
        )


def _normalize(section: str, key: str, rule: _Rule, value: Any) -> Any:
    if rule.kind == "enum":
        if not isinstance(value, str) or value not in rule.allowed:
            _reject(section, key, rule)
        return value
    if rule.kind == "color":
        if not _is_hex_color(value):
            _reject(section, key, rule)
        return value
    if rule.kind == "bool":
        # bool is not interchangeable with int on this face either: the field
        # means a real JSON boolean, not 0/1.
        if not isinstance(value, bool):
            _reject(section, key, rule)
        return value
    if rule.kind == "int":
        # ``bool`` is an ``int`` subclass; a JSON true/false is NOT an integer
        # setting and must be rejected instead of silently stored as 1/0.
        if isinstance(value, bool) or not isinstance(value, int):
            _reject(section, key, rule)
        if not rule.minimum <= value <= rule.maximum:
            _reject(section, key, rule)
        return value
    if rule.kind in ("float", "nullable_float"):
        if value is None and rule.kind == "nullable_float":
            return None
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            _reject(section, key, rule)
        number = float(value)
        if not rule.minimum <= number <= rule.maximum:
            _reject(section, key, rule)
        return number
    raise AssertionError(f"unhandled rule kind {rule.kind!r}")  # pragma: no cover


def _is_hex_color(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 7
        and value.startswith("#")
        and all(digit in _HEX_DIGITS for digit in value[1:])
    )


def _reject(section: str, key: str, rule: _Rule) -> None:
    raise SettingsSectionError(
        f"settings.update_section {section}.{key} must be "
        f"{_expected_text(rule)}"
    )


def _expected_text(rule: _Rule) -> str:
    if rule.kind == "enum":
        return f"one of {sorted(rule.allowed)}"
    if rule.kind == "color":
        return "a #RRGGBB colour string"
    if rule.kind == "bool":
        return "a boolean"
    if rule.kind == "int":
        return f"an integer within {_range_text(rule)}"
    if rule.kind == "float":
        return f"a number within {_range_text(rule)}"
    if rule.kind == "nullable_float":
        return f"null or a number within {_range_text(rule)}"
    raise AssertionError(f"unhandled rule kind {rule.kind!r}")  # pragma: no cover


def _range_text(rule: _Rule) -> str:
    return f"{rule.minimum:g}..{rule.maximum:g}"
