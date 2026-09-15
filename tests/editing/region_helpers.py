"""Test helpers for the editing suite: in-memory region repository with
revision history (supports simulated restarts)."""

from __future__ import annotations

import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from domain.regions.entities import Region, RegionRevision  # noqa: E402


class InMemoryRegionRepository:
    def __init__(self) -> None:
        self.regions: dict[str, Region] = {}
        self.revisions: dict[str, dict[int, RegionRevision]] = {}

    def add_region(self, region: Region) -> None:
        self.regions[region.region_id] = region

    def get_region(self, region_id: str):
        return self.regions.get(region_id)

    def list_regions(self, page_id: str):
        return [r for r in self.regions.values() if r.page_id == page_id]

    def update_region(self, region: Region) -> None:
        self.regions[region.region_id] = region

    def soft_delete_region(self, region_id: str) -> None:
        region = self.regions.get(region_id)
        if region:
            region.soft_delete()

    def add_revision(self, revision: RegionRevision) -> None:
        self.revisions.setdefault(revision.region_id, {})[revision.revision_no] = revision

    def list_revisions(self, region_id: str):
        return sorted(self.revisions.get(region_id, {}).values(), key=lambda r: r.revision_no)

    def get_revision(self, region_id: str, revision_no: int):
        return self.revisions.get(region_id, {}).get(revision_no)

    def set_revision_pinned(self, region_id: str, revision_no: int, pinned: bool) -> None:
        """Single-purpose pin update; immutable history is never rewritten."""
        revision = self.revisions.get(region_id, {}).get(revision_no)
        if revision is None:
            raise LookupError(f"revision {revision_no} not found for region {region_id}")
        updated = RegionRevision(
            region_revision_id=revision.region_revision_id,
            region_id=revision.region_id,
            revision_no=revision.revision_no,
            snapshot=revision.snapshot,
            origin=revision.origin,
            review_state=revision.review_state,
            is_pinned=pinned,
            source_run_id=revision.source_run_id,
            source_step_run_id=revision.source_step_run_id,
            restored_from_revision_id=revision.restored_from_revision_id,
            created_at=revision.created_at,
        )
        self.revisions[region_id][revision_no] = updated
