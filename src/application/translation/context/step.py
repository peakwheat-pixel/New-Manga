"""Translate Step orchestration (D06 §18, TASK-002 §4).

The step composes frozen constraints + TM matches + a Context Bundle into
a provider request, maps every returned item back onto its primary region,
and refuses out-of-scope output (AC-TRANS-003): context regions are
read-only and unknown/missing mappings fail the step without touching any
current pointer. TM hits are reference text only — nothing here writes a
final translation (AC-TM-004).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType

from application.translation.context.builder import (
    CONTEXT,
    PRIMARY,
    ContextBundle,
    ContextChunk,
)
from application.translation.context.gate import decide_sfx_translation
from application.translation.context.snapshot import EffectiveConstraintSnapshot
from application.translation.knowledge.tm import TmMatch


class OutputMappingError(Exception):
    """Provider output violates the request's target mapping
    (TASK-002 §4 OUTPUT_MAPPING_MISMATCH semantics)."""


@dataclass(frozen=True)
class TargetSlot:
    page_id: str
    region_id: str


@dataclass(frozen=True)
class TranslationRequest:
    """Provider request built by this module — UI never assembles prompts
    (D06 §13)."""

    model: str
    prompt: str
    term_glossary: tuple[dict, ...]
    do_not_translate: frozenset[str]
    tm_references: tuple[dict, ...]
    targets: tuple[TargetSlot, ...]
    options: Mapping = field(default_factory=dict)
    context_provenance: dict = field(default_factory=dict)


@dataclass(frozen=True)
class SkippedTarget:
    region_id: str
    status: str
    reason: str | None


@dataclass(frozen=True)
class TranslateStepResult:
    """D06 §18.2 outputs — machine translations + full provenance."""

    translations: Mapping[str, str]
    skipped: tuple[SkippedTarget, ...]
    model: str
    request_options: Mapping
    context_provenance: dict
    term_provenance: tuple[dict, ...]

    def translation_for(self, region_id: str) -> str | None:
        return self.translations.get(region_id)


def build_provider_request(
    *,
    bundle: ContextBundle,
    snapshot: EffectiveConstraintSnapshot,
    tm_matches: tuple[TmMatch, ...] = (),
    model: str = "",
    options: Mapping | None = None,
    targets: tuple[TargetSlot, ...] | None = None,
) -> TranslationRequest:
    """Compose prompt + glossary + TM references + write targets."""

    primary_ids = {entry.region_id for entry in bundle.primary_entries()}
    if targets is None:
        targets = tuple(
            TargetSlot(entry.page_id, entry.region_id)
            for entry in bundle.primary_entries()
        )
    else:
        unknown = [t for t in targets if t.region_id not in primary_ids]
        if unknown:
            raise OutputMappingError(
                f"targets outside the bundle's write scope: {unknown}"
            )
    glossary = tuple(
        {
            "normalized_key": key,
            "source_term": value.source_term,
            "target_term": value.target_term,
            "locked": value.locked,
        }
        for key, value in snapshot.terminology().items()
    )
    tm_references = tuple(
        {
            "source_text": match.entry.source_text,
            "target_text": match.entry.target_text,
            "match_type": match.match_type,
            "similarity": match.similarity,
        }
        for match in tm_matches
    )
    lines: list[str] = []
    for entry in bundle.entries:
        tag = "TARGET" if entry.role == PRIMARY else "CONTEXT"
        lines.append(f"[{tag}] {entry.text}")
    prompt = "\n".join(lines)
    return TranslationRequest(
        model=model,
        prompt=prompt,
        term_glossary=glossary,
        do_not_translate=frozenset(snapshot.do_not_translate()),
        tm_references=tm_references,
        targets=targets,
        options=dict(options or {}),
        context_provenance=bundle.provenance(),
    )


def map_provider_output(
    request: TranslationRequest, outputs: Mapping[str, str]
) -> dict[str, str]:
    """Every provider item must map onto a requested primary region; unknown,
    duplicate or missing mappings fail the step (TASK-002 §4). Mapping keys
    are region ids, so duplicates cannot occur; unknown keys (e.g. context
    regions) and missing targets raise."""

    expected = {slot.region_id for slot in request.targets}
    unknown = sorted(set(outputs) - expected)
    if unknown:
        raise OutputMappingError(
            f"output outside the write scope (AC-TRANS-003): {unknown}"
        )
    missing = sorted(expected - set(outputs))
    if missing:
        raise OutputMappingError(f"missing output for targets: {missing}")
    return dict(outputs)


def execute_translate_step(
    *,
    bundle: ContextBundle,
    snapshot: EffectiveConstraintSnapshot,
    tm_matches: tuple[TmMatch, ...] = (),
    provider_call: Callable[[TranslationRequest], Mapping[str, str]],
    model: str = "",
    options: Mapping | None = None,
) -> TranslateStepResult:
    """D06 §18: gate SFX regions, translate the rest, map outputs back."""

    translate_entries = []
    skipped: list[SkippedTarget] = []
    for entry in bundle.primary_entries():
        action = decide_sfx_translation(entry.region_type, entry.sfx_policy)
        if action.skipped:
            skipped.append(SkippedTarget(entry.region_id, action.status, action.reason))
        else:
            translate_entries.append(entry)

    translations: dict[str, str] = {}
    if translate_entries:
        gated_bundle = _regroup(bundle, translate_entries)
        request = build_provider_request(
            bundle=gated_bundle,
            snapshot=snapshot,
            tm_matches=tm_matches,
            model=model,
            options=options,
        )
        outputs = provider_call(request)
        translations = map_provider_output(request, outputs)

    return TranslateStepResult(
        translations=MappingProxyType(translations),
        skipped=tuple(skipped),
        model=model,
        request_options=dict(options or {}),
        context_provenance=bundle.provenance(),
        term_provenance=snapshot.provenance(),
    )


def _regroup(bundle: ContextBundle, translate_entries) -> ContextBundle:
    """Bundle narrowed to the translatable primaries; context untouched."""

    keep_ids = {entry.region_id for entry in translate_entries}
    entries = tuple(
        entry
        for entry in bundle.entries
        if entry.role == CONTEXT or entry.region_id in keep_ids
    )
    return replace(
        bundle,
        entries=entries,
        chunks=(ContextChunk(entries),),
    )
