"""Small injectable storage seams for the TASK-011 scheduler.

This module intentionally does not add a database table or modify shared
Ports.  The in-memory implementation is a deterministic contract adapter;
the application service depends on the Protocols so a later persistence
slice can supply the same operations without changing scheduling semantics.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from typing import Any, Mapping, Protocol, Sequence

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

    def get(self, run_id: str) -> PipelineRun | None: ...

    def list_ids(self) -> tuple[str, ...]: ...


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
    ) -> CatalogCommit:
        try:
            current = self.current(target_id)
        except PipelineError as error:
            return CatalogCommit("target_not_found", error.detail)
        if any(current.current_revisions.get(key) != value for key, value in expected_revisions.items()):
            return CatalogCommit("input_revision_changed", "current Revision changed")
        if current.lock != expected_lock:
            return CatalogCommit("lock_changed", "current Lock changed")

        if current.target_type is TargetType.PAGE:
            updated = replace(
                current,
                current_revisions={**current.current_revisions, **revision_updates},
                stage_states={**current.stage_states, **stage_updates},
            )
            self._pages[current.page_id] = updated
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
                if key not in {"provider_bindings", "context_policy"}
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


class InMemoryPipelineStore:
    def __init__(self) -> None:
        self._runs: dict[str, PipelineRun] = {}

    def put(self, run_id: str, run: PipelineRun) -> None:
        self._runs[run_id] = run

    def get(self, run_id: str) -> PipelineRun | None:
        return self._runs.get(run_id)

    def list_ids(self) -> tuple[str, ...]:
        return tuple(self._runs)
