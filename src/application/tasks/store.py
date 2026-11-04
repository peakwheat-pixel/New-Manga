"""Small injectable storage seams for the TASK-011 scheduler.

This module intentionally does not add a database table or modify shared
Ports.  The in-memory implementation is a deterministic contract adapter;
the application service depends on the Protocols so a later persistence
slice can supply the same operations without changing scheduling semantics.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace, fields, is_dataclass
from enum import Enum
import hashlib
import json
import threading
from typing import Any, Callable, Mapping, Protocol, Sequence

from domain.tasks.models import (
    LockSnapshot,
    PipelineError,
    PipelineRun,
    PipelineScope,
    RegionSnapshot,
    StageState,
    TargetSnapshot,
    TargetType,
    freeze_snapshot,
)


@dataclass(frozen=True)
class CatalogCommit:
    status: str
    detail: str = ""


@dataclass(frozen=True)
class FrozenRunSnapshots:
    settings: Mapping[str, Any]
    provider_bindings: Mapping[str, Any]
    constraint_snapshot_ref: str | None
    context_policy: Mapping[str, Any]


def snapshot_value(value: Any) -> Any:
    """JSON value of the existing immutable records, preserving array order."""
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {item.name: snapshot_value(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Mapping):
        return {key: snapshot_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [snapshot_value(item) for item in value]
    return value


def snapshot_digest(value: Any) -> str:
    encoded = json.dumps(snapshot_value(value), ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def prepared_quartet(run: PipelineRun) -> dict[str, Any]:
    return snapshot_value({
        "requestedTargets": [target.snapshot for target in run.targets],
        "settingsSnapshot": run.settings_snapshot,
        "providerBindingSnapshot": run.provider_binding_snapshot,
        "constraintSnapshotRef": run.constraint_snapshot_ref,
    })


def validate_prepared_snapshots(run: PipelineRun) -> None:
    """Explicit replay fields for the new prepared path; unknown execution fields fail closed.

    The whitelist mirrors the frozen settings surface (``bootstrap.settings_sections``) for the
    execution-relevant sections. Sections that do not participate in Run replay
    (``providers``/``network``/other settings pages) are filtered, not rejected: they are already
    redacted by the snapshot builder and must not make a legitimate user configuration unusable.
    """
    settings_fields = {
        "ocr": {"script", "direction"},
        "translate": {"context_pages", "context_token_budget", "glossary", "target_language"},
        "detect": {"empty_detection_policy"},
        "tasks": {"retry_max_attempts", "retry_backoff_seconds"},
        "model_gpu": {"device_preference", "allow_cpu_fallback"},
        "sfx": {"policy"},
        "typeset": {"font_family", "font_size", "font_size_offset", "manual_font_size", "text_color",
                    "stroke_enabled", "stroke_color", "stroke_width", "line_spacing", "text_align",
                    "text_direction", "auto_font_size", "auto_font_size_enabled"},
        "inpaint": {"dilate_radius", "erode_radius", "is_speech_bubble", "is_solid_background",
                    "is_lineart", "has_screentone", "is_color_webtoon", "structure_crossing_mask",
                    "preferred_quality", "background_complexity"},
    }
    for section, values in run.settings_snapshot.items():
        if not isinstance(values, Mapping):
            raise PipelineError("RUN_SNAPSHOT_INCOMPLETE", "settings snapshot is not replay-safe")
        replay_keys = settings_fields.get(section)
        if replay_keys is None:
            continue  # Non-execution settings sections never enter Run replay (ADJ §2.2).
        if set(values) - replay_keys:
            raise PipelineError("RUN_SNAPSHOT_INCOMPLETE", "settings contain unsupported replay fields")
    binding_fields = {"provider_id", "provider_profile_id", "id", "enabled", "available",
                      "fallback", "execution", "execution_digest", "frozen_fallbacks"}
    for value in run.provider_binding_snapshot.values():
        if not isinstance(value, Mapping) or set(value) - binding_fields:
            raise PipelineError("RUN_SNAPSHOT_INCOMPLETE", "provider binding is not snapshot-safe")
        if "execution" not in value:
            raise PipelineError("RUN_SNAPSHOT_INCOMPLETE", "provider has no complete replay configuration")
        validate_provider_execution(value["execution"])
        if snapshot_digest(value["execution"]) != value.get("execution_digest"):
            raise PipelineError("RUN_SNAPSHOT_INCOMPLETE", "provider replay digest differs")
        for fallback in value.get("frozen_fallbacks", {}).values():
            if not isinstance(fallback, Mapping) or "execution" not in fallback:
                raise PipelineError(
                    "RUN_SNAPSHOT_INCOMPLETE", "fallback provider has no complete replay configuration")
            validate_provider_execution(fallback["execution"])
            if snapshot_digest(fallback["execution"]) != fallback.get("execution_digest"):
                raise PipelineError("RUN_SNAPSHOT_INCOMPLETE", "fallback replay digest differs")


def validate_provider_execution(value: Any) -> None:
    """Closed typed replay schema. Errors never echo rejected values."""
    from urllib.parse import urlsplit
    import math

    def reject():
        raise PipelineError("RUN_SNAPSHOT_INCOMPLETE", "provider replay configuration is incomplete or unsafe")

    required = {"provider_id", "provider_type", "base_url", "model", "credential_ref", "timeout_seconds",
                "extra_options", "network_profile", "target_language", "options", "adapter_version"}
    if not isinstance(value, Mapping) or set(value) != required:
        reject()
    for key in ("provider_id", "provider_type", "base_url", "model", "target_language", "adapter_version"):
        if not isinstance(value[key], str):
            reject()
    if not value["provider_id"] or not value["model"]:
        reject()
    if value["credential_ref"] is not None and not isinstance(value["credential_ref"], str):
        reject()
    for options in (value["options"], value["extra_options"]):
        if not isinstance(options, (tuple, list)):
            reject()
        seen = set()
        for item in options:
            if not isinstance(item, (tuple, list)) or len(item) != 2:
                reject()
            key, option = item
            if not isinstance(key, str) or key in seen:
                reject()
            seen.add(key)
            if key not in {"temperature", "top_p", "max_tokens", "max_completion_tokens", "seed",
                           "frequency_penalty", "presence_penalty", "stop"}:
                reject()
            if key == "stop":
                if not isinstance(option, str) and not (
                    isinstance(option, (tuple, list)) and all(isinstance(s, str) for s in option)):
                    reject()
            else:
                try:
                    if isinstance(option, bool) or not math.isfinite(float(option)):
                        reject()
                except (ValueError, TypeError):
                    reject()
    if value["adapter_version"] == "mock-local-v1":
        if value["provider_type"] != "mock-local" or value["base_url"] or value["credential_ref"] is not None:
            reject()
        return
    if isinstance(value["adapter_version"], str) and value["adapter_version"].startswith("local:"):
        # R-004/R-005: a pure-local inference provider has no endpoint, credential or network
        # profile; its replay identity is (provider_type, model, adapter_version).
        if (not value["provider_type"].startswith("local-") or value["provider_type"] in {
                "local-sakura", "local-simple-fill", "local-edge-bleed", "local-diffusion"}
                or value["base_url"] or value["credential_ref"] is not None
                or value["network_profile"] is not None):
            reject()
        return
    if value["adapter_version"] != "openai-compatible-v1" or value["provider_type"] not in {
        "openai-compatible", "openai-compatible-vision", "local-sakura"
    }:
        reject()
    def safe_url(raw):
        if not isinstance(raw, str):
            reject()
        try:
            url = urlsplit(raw)
            if url.scheme not in {"http", "https", "socks5", "socks5h"} or not url.hostname or url.username or url.password or url.query or url.fragment:
                reject()
        except ValueError:
            reject()
    safe_url(value["base_url"])
    if not isinstance(value["timeout_seconds"], (int, float)) or not math.isfinite(value["timeout_seconds"]) or value["timeout_seconds"] <= 0:
        reject()
    profile = value["network_profile"]
    fields = {"network_profile_id", "name", "mode", "http_proxy", "https_proxy", "socks5_proxy", "username",
              "credential_ref", "inherit_system", "timeout_seconds", "verify_tls",
              "allow_proxy_failure_direct_fallback", "created_at", "updated_at", "bypass_hosts"}
    if not isinstance(profile, Mapping) or set(profile) != fields:
        reject()
    for key in ("http_proxy", "https_proxy", "socks5_proxy"):
        if profile[key]:
            safe_url(profile[key])
    validate_prepared_overrides(value)


_AUTH_MATERIAL_KEYS = frozenset({
    "token", "password", "api_key", "apikey", "authorization", "secret", "access_token",
    "refresh_token", "bearer", "headers", "signing_key", "host_session_credential",
})


def _reject_auth_keys(mapping: Mapping[str, Any], *, deep: bool) -> None:
    for key, item in mapping.items():
        if str(key).lower() in _AUTH_MATERIAL_KEYS:
            raise PipelineError("RUN_SNAPSHOT_INCOMPLETE", "authentication material cannot be snapshotted")
        if deep and isinstance(item, Mapping):
            _reject_auth_keys(item, deep=True)


def validate_prepared_overrides(value: Any) -> None:
    """Reject authentication material where an override can actually carry it (R-014).

    ``overrides.provider_bindings`` is checked recursively (endpoint credentials live there);
    settings sections are checked one level deep only, so user content such as a glossary term
    named ``token`` is legitimate data and does not fail the Prepare.
    """
    if not isinstance(value, Mapping):
        return
    bindings = value.get("provider_bindings")
    if isinstance(bindings, Mapping):
        _reject_auth_keys(bindings, deep=True)
    settings = value.get("settings")
    if isinstance(settings, Mapping):
        for section in settings.values():
            if isinstance(section, Mapping):
                _reject_auth_keys(section, deep=False)
    for key, item in value.items():
        if str(key).lower() in _AUTH_MATERIAL_KEYS:
            raise PipelineError("RUN_SNAPSHOT_INCOMPLETE", "authentication material cannot be snapshotted")
        if key not in ("provider_bindings", "settings") and isinstance(item, Mapping):
            _reject_auth_keys(item, deep=False)


@dataclass(frozen=True)
class IdempotencyRecord:
    idempotency_key: str
    request_fingerprint: str
    run_id: str
    operation_type: str


class TargetCatalog(Protocol):
    def expand(self, scope: PipelineScope) -> tuple[TargetSnapshot, ...]: ...

    def current(self, target_id: str) -> TargetSnapshot: ...

    def commit_step(
        self,
        *,
        target_id: str,
        expected_revisions: Mapping[str, str | None],
        expected_lock: LockSnapshot,
        stage_updates: Mapping[str, StageState],
        revision_updates: Mapping[str, str],
        persist: Callable[[], None] | None = None,
        run_id: str | None = None,
        step_run_id: str | None = None,
        pause_requested: bool = False,
        cancel_requested: bool = False,
    ) -> CatalogCommit: ...


class SnapshotProvider(Protocol):
    def freeze(
        self,
        run_id: str,
        *,
        overrides: Mapping[str, Any] | None = None,
    ) -> FrozenRunSnapshots: ...


class PipelineStore(Protocol):
    def put(self, run_id: str, run: PipelineRun) -> None: ...

    def write_in_current_transaction(self, run: PipelineRun) -> None: ...

    def get(self, run_id: str) -> PipelineRun | None: ...

    def refresh(self, run_id: str) -> PipelineRun | None: ...

    def list_ids(self) -> tuple[str, ...]: ...

    def get_idempotency(self, idempotency_key: str) -> IdempotencyRecord | None: ...

    def accept(
        self, run: PipelineRun, *, idempotency_key: str,
        request_fingerprint: str, operation_type: str,
        validate: Callable[[], None] | None = None,
    ) -> tuple[PipelineRun, bool]: ...

    def accept_restart(
        self, parent: PipelineRun, child: PipelineRun, *,
        idempotency_key: str | None, request_fingerprint: str | None,
    ) -> tuple[PipelineRun, bool]: ...


def _merge(base: Mapping[str, Any], overrides: Mapping[str, Any]) -> dict[str, Any]:
    merged = deepcopy(dict(base))
    for key, value in overrides.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


class InMemoryTargetCatalog:
    """In-memory Book/Chapter/Page/Region target catalog.

    It is intentionally explicit about page and region snapshots so tests can
    mutate a current Revision or Lock between Step start and commit.
    """

    def __init__(self) -> None:
        self._pages: dict[str, TargetSnapshot] = {}

    def add_page(
        self,
        page_id: str,
        *,
        book_id: str,
        chapter_id: str,
        page_order: int = 0,
        lock: LockSnapshot | None = None,
        current_revisions: Mapping[str, str | None] | None = None,
        stage_states: Mapping[str, StageState | str] | None = None,
        regions: Sequence[RegionSnapshot] = (),
        metadata: Mapping[str, Any] | None = None,
    ) -> TargetSnapshot:
        snapshot = TargetSnapshot(
            target_id=page_id,
            page_id=page_id,
            target_type=TargetType.PAGE,
            page_order=page_order,
            book_id=book_id,
            chapter_id=chapter_id,
            lock=lock or LockSnapshot(),
            current_revisions=current_revisions or {},
            stage_states=stage_states or {},
            regions=tuple(regions),
            metadata=metadata or {},
        )
        self._pages[page_id] = snapshot
        return snapshot

    def expand(self, scope: PipelineScope) -> tuple[TargetSnapshot, ...]:
        if scope.scope_type.value == "book":
            book_id = scope.book_id or (scope.selected_ids[0] if scope.selected_ids else None)
            if not book_id:
                raise PipelineError("EMPTY_TARGET_SELECTION", "book_id is required")
            candidates = [p for p in self._pages.values() if p.book_id == book_id]
        elif scope.scope_type.value == "chapter":
            chapter_id = scope.chapter_id or (scope.selected_ids[0] if scope.selected_ids else None)
            if not chapter_id:
                raise PipelineError("EMPTY_TARGET_SELECTION", "chapter_id is required")
            candidates = [p for p in self._pages.values() if p.chapter_id == chapter_id]
        elif scope.scope_type.value in {"page_selection", "page"}:
            if not scope.selected_ids:
                raise PipelineError("EMPTY_TARGET_SELECTION", "page selection is empty")
            candidates = [self._page_or_error(page_id) for page_id in scope.selected_ids]
        elif scope.scope_type.value == "region":
            if not scope.selected_ids:
                raise PipelineError("EMPTY_TARGET_SELECTION", "region selection is empty")
            if len(scope.selected_ids) != 1:
                raise PipelineError("TARGET_NOT_FOUND", "region scope requires one region")
            return (self._region_or_error(scope.selected_ids[0]),)
        else:  # pragma: no cover - ScopeType validates before this point.
            raise PipelineError("TARGET_NOT_FOUND", f"unsupported scope {scope.scope_type}")

        active = []
        for page in candidates:
            if page.deleted:
                if scope.scope_type.value in {"page_selection", "page"}:
                    raise PipelineError("TARGET_DELETED", page.page_id)
                continue
            active.append(self._active_page(page))
        if not active:
            raise PipelineError("EMPTY_TARGET_SELECTION", "scope expands to no active pages")
        return tuple(sorted(active, key=lambda page: (page.page_order, page.page_id)))

    def current(self, target_id: str) -> TargetSnapshot:
        if target_id in self._pages:
            page = self._pages[target_id]
            if page.deleted:
                raise PipelineError("TARGET_DELETED", target_id)
            return self._active_page(page)
        return self._region_or_error(target_id)

    def commit_step(
        self,
        *,
        target_id: str,
        expected_revisions: Mapping[str, str | None],
        expected_lock: LockSnapshot,
        stage_updates: Mapping[str, StageState],
        revision_updates: Mapping[str, str],
        persist: Callable[[], None] | None = None,
        run_id: str | None = None,
        step_run_id: str | None = None,
        pause_requested: bool = False,
        cancel_requested: bool = False,
    ) -> CatalogCommit:
        del run_id, step_run_id
        try:
            current = self.current(target_id)
        except PipelineError as error:
            return CatalogCommit("target_not_found", error.detail)
        if any(current.current_revisions.get(key) != value for key, value in expected_revisions.items()):
            return CatalogCommit("input_revision_changed", "current Revision changed")
        if current.lock != expected_lock:
            return CatalogCommit("lock_changed", "current Lock changed")
        # R-012 (documented adapter divergence): this deterministic test adapter has no prepared
        # candidate transaction, so the scheduler honors a pause/cancel intent at the next boundary
        # (the released semantics the pipeline tests pin). The production SqliteTargetCatalog seam
        # refuses the live write itself; that equivalence is covered by the AC5 pause/cancel fault
        # injection in tests/fea10/test_commit_zero_write.py.

        if current.target_type is TargetType.PAGE:
            updated = replace(
                current,
                current_revisions={**current.current_revisions, **revision_updates},
                stage_states={**current.stage_states, **stage_updates},
            )
            self._pages[current.page_id] = updated
            try:
                if persist is not None:
                    persist()
            except Exception:
                self._pages[current.page_id] = current
                raise
            return CatalogCommit("applied")

        page = self._pages[current.page_id]
        updated_regions = []
        for region in page.regions:
            if region.region_id != current.region_id:
                updated_regions.append(region)
                continue
            updated_regions.append(
                replace(
                    region,
                    current_revisions={**region.current_revisions, **revision_updates},
                    stage_states={**region.stage_states, **stage_updates},
                )
            )
        self._pages[current.page_id] = replace(page, regions=tuple(updated_regions))
        try:
            if persist is not None:
                persist()
        except Exception:
            self._pages[current.page_id] = page
            raise
        return CatalogCommit("applied")

    def update_page(self, page_id: str, **changes: Any) -> None:
        self._pages[page_id] = replace(self._pages[page_id], **changes)

    def update_region(
        self,
        region_id: str,
        *,
        lock: LockSnapshot | None = None,
        current_revisions: Mapping[str, str | None] | None = None,
        stage_states: Mapping[str, StageState | str] | None = None,
    ) -> None:
        page = self._page_for_region(region_id)
        regions = []
        for region in page.regions:
            if region.region_id == region_id:
                regions.append(
                    replace(
                        region,
                        lock=lock or region.lock,
                        current_revisions=current_revisions or region.current_revisions,
                        stage_states=stage_states or region.stage_states,
                    )
                )
            else:
                regions.append(region)
        self._pages[page.page_id] = replace(page, regions=tuple(regions))

    def soft_delete_page(self, page_id: str) -> None:
        self._pages[page_id] = replace(self._pages[page_id], deleted=True)

    def soft_delete_region(self, region_id: str) -> None:
        page = self._page_for_region(region_id)
        self.update_region(region_id, stage_states={"__deleted__": StageState.CANCELLED})
        self._pages[page.page_id] = replace(
            self._pages[page.page_id],
            regions=tuple(
                replace(region, metadata={**region.metadata, "deleted": True})
                if region.region_id == region_id
                else region
                for region in self._pages[page.page_id].regions
            ),
        )

    def _page_or_error(self, page_id: str) -> TargetSnapshot:
        page = self._pages.get(page_id)
        if page is None:
            raise PipelineError("TARGET_NOT_FOUND", page_id)
        return page

    def _page_for_region(self, region_id: str) -> TargetSnapshot:
        for page in self._pages.values():
            if any(region.region_id == region_id for region in page.regions):
                return page
        raise PipelineError("TARGET_NOT_FOUND", region_id)

    def _region_or_error(self, region_id: str) -> TargetSnapshot:
        page = self._page_for_region(region_id)
        if page.deleted:
            raise PipelineError("TARGET_DELETED", region_id)
        region = next(region for region in page.regions if region.region_id == region_id)
        if region.metadata.get("deleted"):
            raise PipelineError("TARGET_DELETED", region_id)
        return TargetSnapshot(
            target_id=region.region_id,
            page_id=page.page_id,
            target_type=TargetType.REGION,
            page_order=page.page_order,
            book_id=page.book_id,
            chapter_id=page.chapter_id,
            region_id=region.region_id,
            lock=LockSnapshot(
                page_locked=page.lock.page_locked,
                region_locked=region.lock.region_locked,
                translation_locked=region.lock.translation_locked,
                inpaint_locked=region.lock.inpaint_locked,
            ),
            manual_edited=region.manual_edited,
            final_confirmed=region.final_confirmed,
            current_revisions=region.current_revisions,
            stage_states=region.stage_states,
            regions=(region,),
            metadata=region.metadata,
        )

    @staticmethod
    def _active_page(page: TargetSnapshot) -> TargetSnapshot:
        active_regions = tuple(
            region for region in page.regions if not region.metadata.get("deleted")
        )
        return replace(page, regions=active_regions)


class InMemorySnapshotProvider:
    def __init__(
        self,
        *,
        settings: Mapping[str, Any] | None = None,
        provider_bindings: Mapping[str, Any] | None = None,
        constraint_snapshot_ref: str | None = None,
        context_policy: Mapping[str, Any] | None = None,
    ) -> None:
        self.settings = deepcopy(dict(settings or {}))
        self.provider_bindings = deepcopy(dict(provider_bindings or {}))
        self.constraint_snapshot_ref = constraint_snapshot_ref
        self.context_policy = deepcopy(dict(context_policy or {}))

    def freeze(
        self,
        run_id: str,
        *,
        overrides: Mapping[str, Any] | None = None,
    ) -> FrozenRunSnapshots:
        overrides = overrides or {}
        settings_overrides = overrides.get("settings")
        if settings_overrides is None:
            settings_overrides = {
                key: value
                for key, value in overrides.items()
                if key not in {"provider_bindings", "context_policy", "provider_profiles"}
            }
        settings = _merge(self.settings, settings_overrides if isinstance(settings_overrides, Mapping) else {})
        provider_bindings = _merge(
            self.provider_bindings,
            overrides.get("provider_bindings", {}),
        )
        context_policy = _merge(
            self.context_policy,
            overrides.get("context_policy", {}),
        )
        return FrozenRunSnapshots(
            settings=freeze_snapshot(settings),
            provider_bindings=freeze_snapshot(provider_bindings),
            constraint_snapshot_ref=self.constraint_snapshot_ref,
            context_policy=freeze_snapshot(context_policy),
        )


def _detached_run(run: PipelineRun) -> PipelineRun:
    """Structural clone for view reads (RUN-STORE-CACHE-RACE-FIX-1 AC1).

    Frozen snapshots (settings/provider/context/candidate payloads and the
    ``PlanUnit`` tuples) are immutable and may be shared; the mutable containers
    the scheduler mutates (tasks/step_runs/candidates/terminal units, a StepRun's
    input/output dicts, a task's step_run_ids list) are copied so a view reader
    can never mutate execution state through the returned object.
    """
    return replace(
        run,
        tasks=[
            replace(task, step_run_ids=list(task.step_run_ids))
            for task in run.tasks
        ],
        step_runs=[
            replace(
                step,
                input_refs=dict(step.input_refs),
                output=dict(step.output),
            )
            for step in run.step_runs
        ],
        candidates=[
            replace(candidate, payload=dict(candidate.payload))
            for candidate in run.candidates
        ],
        terminal_unit_ids=set(run.terminal_unit_ids),
    )


class InMemoryPipelineStore:
    def __init__(self) -> None:
        self._runs: dict[str, PipelineRun] = {}
        self._idempotency: dict[str, IdempotencyRecord] = {}
        self._lock = threading.RLock()

    def put(self, run_id: str, run: PipelineRun) -> None:
        with self._lock:
            self._runs[run_id] = run

    def write_in_current_transaction(self, run: PipelineRun) -> None:
        self.put(run.run_id, run)

    def get(self, run_id: str) -> PipelineRun | None:
        with self._lock:
            return self._runs.get(run_id)

    def refresh(self, run_id: str) -> PipelineRun | None:
        """Return an independent *view* of the stored Run.

        RUN-STORE-CACHE-RACE-FIX-1 (AC1): ``refresh`` / ``get_run_snapshot(fresh=True)``
        is a view read for projections -- it must not hand out (or re-cache) the
        live ``PipelineRun`` object that the scheduler thread is executing, and
        it must not evict/replace it either. The returned copy is detached: a
        caller cannot mutate execution state through it.
        """
        with self._lock:
            run = self._runs.get(run_id)
        return _detached_run(run) if run is not None else None

    def list_ids(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(self._runs)

    def get_idempotency(self, idempotency_key: str) -> IdempotencyRecord | None:
        with self._lock:
            return self._idempotency.get(idempotency_key)

    def accept(
        self, run: PipelineRun, *, idempotency_key: str,
        request_fingerprint: str, operation_type: str,
        validate: Callable[[], None] | None = None,
    ) -> tuple[PipelineRun, bool]:
        with self._lock:
            record = self._idempotency.get(idempotency_key)
            if record is not None:
                if record.request_fingerprint != request_fingerprint:
                    raise PipelineError(
                        "IDEMPOTENCY_KEY_REUSED", "idempotency key fingerprint differs"
                    )
                existing = self._runs.get(record.run_id)
                if existing is None:
                    raise PipelineError("TARGET_NOT_FOUND", "idempotent Run no longer exists")
                return existing, False
            if validate is not None:
                validate()
            self._runs[run.run_id] = run
            self._idempotency[idempotency_key] = IdempotencyRecord(
                idempotency_key, request_fingerprint, run.run_id, operation_type
            )
            return run, True

    def put_many(self, runs: Sequence[PipelineRun]) -> None:
        with self._lock:
            self._runs.update((run.run_id, run) for run in runs)

    def accept_restart(
        self, parent: PipelineRun, child: PipelineRun, *,
        idempotency_key: str | None, request_fingerprint: str | None,
    ) -> tuple[PipelineRun, bool]:
        with self._lock:
            if idempotency_key is not None:
                record = self._idempotency.get(idempotency_key)
                if record is not None:
                    if record.request_fingerprint != request_fingerprint:
                        raise PipelineError(
                            "IDEMPOTENCY_KEY_REUSED", "idempotency key fingerprint differs"
                        )
                    existing = self._runs.get(record.run_id)
                    if existing is None:
                        raise PipelineError("TARGET_NOT_FOUND", "idempotent Run no longer exists")
                    return existing, False
            self.put_many((parent, child))
            if idempotency_key is not None:
                assert request_fingerprint is not None
                self._idempotency[idempotency_key] = IdempotencyRecord(
                    idempotency_key, request_fingerprint, child.run_id, "restart"
                )
            return child, True
