"""Shared helpers for the workbench suite (TASK-013).

Injects ``src`` into sys.path (same convention as tests/ui_shell) and
provides the fake page/region catalogs the WorkbenchViewModel consumes
through its duck-typed seams, plus the deterministic pipeline assembly
from TASK-011's in-memory store.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
SRC_ROOT = THIS_DIR.parents[1] / "src"
for entry in (str(THIS_DIR), str(SRC_ROOT)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from application.tasks.service import PipelineService  # noqa: E402
from application.tasks.store import (  # noqa: E402
    InMemoryPipelineStore,
    InMemorySnapshotProvider,
    InMemoryTargetCatalog,
)
from application.translation.pipeline.executor import (  # noqa: E402
    DeterministicStepExecutor,
)


# ----------------------------------------------------------------------
# page/region fakes matching the domain entity attribute surface
# ----------------------------------------------------------------------


@dataclass
class FakePage:
    page_id: str
    chapter_id: str
    sort_order: int
    source_filename: str
    page_locked: bool = False
    managed_original_ref: str = ""
    # T1.1.2: production Page carries a positive pixel extent; defaulted here
    # so every existing positional call site keeps working. Left at 0 the
    # viewmodel must refuse to draw rather than collapse a box to the origin.
    width: int = 0
    height: int = 0


@dataclass
class FakeRegion:
    region_id: str
    page_id: str
    reading_order: int = 0
    region_type: str = "speech"
    ocr_text: str = ""
    machine_translation: str = ""
    edited_translation: str = ""
    final_translation: str = ""
    translation_locked: bool = False
    geometry: object = None  # T1.1.2: a RegionGeometry, as the overlay needs


class FakePageCatalog:
    def __init__(self, pages: list[FakePage], image_urls: dict | None = None) -> None:
        self.pages = pages
        self.image_urls = dict(image_urls or {})
        # expose image_url only when the test registered URLs, mirroring an
        # optional resolver on the production catalog seam
        if self.image_urls:
            self.image_url = lambda page_id, mode: self.image_urls.get(
                (page_id, mode), ""
            )

    def list_pages(self, chapter_id: str) -> list[FakePage]:
        return [
            page
            for page in self.pages
            if page.chapter_id == chapter_id and not getattr(page, "deleted", False)
        ]


class FakeRegionCatalog:
    def __init__(self, regions: list[FakeRegion]) -> None:
        self.regions = regions

    def list_regions(self, page_id: str) -> list[FakeRegion]:
        return [
            region
            for region in self.regions
            if region.page_id == page_id
        ]

    def get_region(self, region_id: str) -> FakeRegion | None:
        return next(
            (region for region in self.regions if region.region_id == region_id),
            None,
        )


class FakeEditor:
    """Records save_manual_translation calls (dirty-guard save path)."""

    def __init__(self) -> None:
        self.saved: list[tuple[str, str]] = []

    def save_manual_translation(self, region_id: str, text: str) -> None:
        self.saved.append((region_id, text))


class FakeRegionWriter:
    """Records create/delete calls through the T1.1.2 writer seams."""

    def __init__(self) -> None:
        self.created: list[tuple[str, object]] = []
        self.deleted: list[str] = []

    def create_region(self, page_id: str, geometry) -> FakeRegion:
        region = FakeRegion(f"r-created-{len(self.created) + 1}", page_id)
        region.geometry = geometry
        self.created.append((page_id, geometry))
        return region

    def delete_region(self, region_id: str) -> None:
        self.deleted.append(region_id)


class FakeNavigation:
    """NavigationViewModel surface used for the D05 §3.1 badge."""

    def __init__(self) -> None:
        self.activity: tuple[bool, str] = (False, "")

    def setWorkbenchActivity(self, running: bool, badge: str = "") -> None:
        self.activity = (running, badge)


# ----------------------------------------------------------------------
# pipeline assembly (TASK-011 in-memory stack)
# ----------------------------------------------------------------------


def make_pipeline(
    pages: list[tuple[str, int]] | None = None,
    *,
    chapter_id: str = "chapter-1",
    executor: DeterministicStepExecutor | None = None,
) -> tuple[PipelineService, InMemoryTargetCatalog]:
    """PipelineService over an InMemoryTargetCatalog with one region per
    page — the minimum for progress projections."""

    catalog = InMemoryTargetCatalog()
    from domain.tasks.models import RegionSnapshot

    for page_id, order in pages or [
        (f"p{index}", index) for index in range(1, 41)
    ]:
        catalog.add_page(
            page_id,
            book_id="book-1",
            chapter_id=chapter_id,
            page_order=order,
            regions=(
                RegionSnapshot(
                    region_id=f"{page_id}-r1",
                    page_id=page_id,
                ),
            ),
        )
    service = PipelineService(
        catalog,
        store=InMemoryPipelineStore(),
        snapshots=InMemorySnapshotProvider(),
        executor=executor or DeterministicStepExecutor(),
    )
    return service, catalog


def make_vm(service: PipelineService, *, pages=None, regions=None, editor=None,
            navigation=None, image_urls=None, creator=None, deleter=None):
    """WorkbenchViewModel wired to fakes; page catalog defaults to the 40
    FakePages matching make_pipeline's catalog entries."""

    from ui.viewmodels.workbench import WorkbenchViewModel

    if pages is None:
        pages = [
            FakePage(page_id, "chapter-1", order, f"{order:03d}.jpg")
            for page_id, order in [
                (f"p{index}", index) for index in range(1, 41)
            ]
        ]
    catalog = FakePageCatalog(pages, image_urls)
    return WorkbenchViewModel(
        pipeline=service,
        page_catalog=catalog,
        region_catalog=FakeRegionCatalog(regions or []),
        translation_editor=editor or FakeEditor(),
        navigation=navigation,
        region_creator=creator,
        region_deleter=deleter,
    )


def wait_until(qapp, predicate, timeout_ms: int = 5000) -> bool:
    """Pump the event loop until predicate() is true (worker completion)."""

    from time import monotonic, sleep

    deadline = monotonic() + timeout_ms / 1000
    while monotonic() < deadline:
        qapp.processEvents()
        if predicate():
            return True
        sleep(0.01)
    return False


def pages_list(count: int) -> list[tuple[str, int]]:
    """[(p1,1) ... (pN,N)] — page ids shared by catalog and pipeline."""

    return [(f"p{index}", index) for index in range(1, count + 1)]


def fail_first_region_step(page_ids, step: str = "ocr") -> set:
    """DeterministicStepExecutor fail keys for make_pipeline's catalogs:
    every fake page carries one region, so a unit's target_id is the
    region id ``{page_id}-r1`` (TASK-011 planner semantics)."""

    return {(f"{page_id}-r1", step) for page_id in page_ids}
