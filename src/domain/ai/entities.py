"""AI domain: prompt templates (FEA-14-AI-1, PREQ AI P21-P25).

Builtin templates are Core code constants (read-only, never stored); only
user-authored templates live in ``prompt_templates``. A reference row records
what points at a template, so P23 can reassign before the soft delete.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BuiltinPromptTemplate:
    """A read-only template shipped by the Core (never persisted)."""

    template_id: str
    name: str
    body: str
    version: int = 1


@dataclass
class PromptTemplate:
    """One user-authored template row from ``prompt_templates`` (schema v14)."""

    template_id: str
    name: str
    body: str
    version: int
    created_at: str
    updated_at: str
    deleted_at: str | None = None


@dataclass(frozen=True)
class PromptTemplateReference:
    """One durable pointer at a template (translation/task/rule)."""

    template_id: str
    kind: str
    owner_id: str
    label: str = ""
