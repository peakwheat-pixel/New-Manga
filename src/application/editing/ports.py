"""Region persistence contract consumed by the editing use cases.

Consumer-side protocol (TASK-008 allowance excludes src/ports and
src/infrastructure); the SQLite adapter lands in a later slice. Fakes in
tests exercise the contract, including simulated restarts.
"""

from __future__ import annotations

from typing import Protocol

from domain.regions.entities import Region, RegionRevision


class RegionRepository(Protocol):
    def add_region(self, region: Region) -> None: ...

    def get_region(self, region_id: str) -> Region | None: ...

    def list_regions(self, page_id: str) -> list[Region]: ...

    def update_region(self, region: Region) -> None: ...

    def soft_delete_region(self, region_id: str) -> None: ...

    def add_revision(self, revision: RegionRevision) -> None: ...

    def list_revisions(self, region_id: str) -> list[RegionRevision]: ...

    def get_revision(
        self, region_id: str, revision_no: int
    ) -> RegionRevision | None: ...
