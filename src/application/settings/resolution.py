"""Effective-settings resolution across override layers (D03 §28,
D06 §49, D08 AC-SET-001).

The service is a pure function of the override set: global defaults,
book/chapter overrides and the current run's temporary overrides
collapse to one value per key with the winning source attached.
"""

from __future__ import annotations

from .errors import SettingsError
from .models import (
    SCOPE_BOOK,
    SCOPE_CHAPTER,
    SCOPE_GLOBAL,
    SCOPE_TASK,
    EffectiveSetting,
    SettingOverride,
)


class SettingsResolutionService:
    """Resolve ``task > chapter > book > global`` (AC-SET-001)."""

    def resolve(
        self,
        key: str,
        *,
        global_defaults: dict[str, str] | None = None,
        overrides: list[SettingOverride] | tuple[SettingOverride, ...] = (),
        task_overrides: dict[str, str] | None = None,
        book_id: str | None = None,
        chapter_id: str | None = None,
    ) -> EffectiveSetting:
        """Resolve one key for a chapter context.

        ``task_overrides`` are the current run's temporary values; they
        win over everything but only live in the run snapshot (D03 §28).
        """
        if not key:
            raise SettingsError("setting key must not be empty")

        candidates: list[EffectiveSetting] = []

        if task_overrides and key in task_overrides:
            candidates.append(
                EffectiveSetting(
                    key=key, value=task_overrides[key], source_scope_type=SCOPE_TASK
                )
            )

        scope_of: dict[str, str | None] = {
            SCOPE_CHAPTER: chapter_id,
            SCOPE_BOOK: book_id,
        }
        # Later scopes in SCOPE_PRECEDENCE are weaker; iterate the two
        # middle layers most-specific first and keep matching overrides.
        for scope_type in (SCOPE_CHAPTER, SCOPE_BOOK):
            wanted_id = scope_of[scope_type]
            matching = [
                o
                for o in overrides
                if o.scope_type == scope_type and o.key == key and o.scope_id == wanted_id
            ]
            if matching:
                chosen = max(matching, key=lambda o: o.key)  # deterministic
                candidates.append(
                    EffectiveSetting(
                        key=key,
                        value=chosen.value,
                        source_scope_type=scope_type,
                        source_scope_id=chosen.scope_id,
                    )
                )

        defaults = global_defaults or {}
        if key in defaults:
            candidates.append(
                EffectiveSetting(key=key, value=defaults[key], source_scope_type=SCOPE_GLOBAL)
            )

        if not candidates:
            raise SettingsError(f"no value defined for setting {key!r}")
        return candidates[0]  # built most-specific first

    def resolve_all(
        self,
        *,
        global_defaults: dict[str, str],
        overrides: list[SettingOverride] | tuple[SettingOverride, ...] = (),
        task_overrides: dict[str, str] | None = None,
        book_id: str | None = None,
        chapter_id: str | None = None,
    ) -> dict[str, EffectiveSetting]:
        """Resolve every known key (defaults + overridden-only keys)."""
        keys = set(global_defaults)
        keys.update(o.key for o in overrides)
        keys.update(task_overrides or ())
        return {
            key: self.resolve(
                key,
                global_defaults=global_defaults,
                overrides=overrides,
                task_overrides=task_overrides,
                book_id=book_id,
                chapter_id=chapter_id,
            )
            for key in sorted(keys)
        }
