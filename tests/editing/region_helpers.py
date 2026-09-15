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
