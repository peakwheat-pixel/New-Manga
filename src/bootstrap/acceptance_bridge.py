"""M2-AC1 acceptance stdio bridge (doc/tasks/M2-AC1.md).

The Tauri host spawns this module — ``python -m bootstrap.acceptance_bridge``
— as a second Core sidecar in the explicit test startup configuration only
(``M2AC1_TEST_MODE=1``); production launches never see it. It assembles the
REAL production Core stack (``bootstrap.core_assembly.assemble_core_services``
with the Qt adapters and ``mock_local_providers=True``) and serves a small
JSON-lines method set that drives the frozen acceptance loop:

    Mock/Local pipeline  ->  SQLite result persistence  ->  process restart
    ->  restore from the persisted state  ->  Reader pages  ->  PNG export.

Every method returns deterministic content digests (sha256 of stored bytes)
and never embeds per-run ids (run/page/region uuids), so two independent
acceptance runs must produce identical summaries (AC1/AC6). The loop uses
only production persistence paths: pipeline state lives in the v3 pipeline
tables, generated pages in the managed-copy artifact storage, reading
progress in the v4 reading table — no schema was added for this Task.

Wire (v1, same shape as the resource-channel control bridge):
  request  {"id": <int>, "method": "<name>", "params": {...}}
  response {"id": <int>, "result": {...}} | {"id": <int>, "error": {"code": "..."}}

This bridge is acceptance-only infrastructure: it must never be imported by
production assembly, and the Tauri host registers its commands only in test
mode.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import sys
import zlib

from application.export.service import (
    ExportFormat,
    ExportPage,
    ExportRequest,
    OverwritePolicy,
    StalePolicy,
)
from application.importing.images.ports import ImportSource
from application.reading.service import ReadingMode, ReadingService
from bootstrap.core_assembly import CoreServices, assemble_core_services
from domain.regions.entities import BBox, RegionGeometry, RegionOrigin
from domain.tasks.models import CommandType, PipelineScope
from infrastructure.rendering.locator import SqlitePageArtifactLocator
from infrastructure.resource_channel.catalog_store import ResourceCatalogStore
from ports.repositories.artifacts import ArtifactType

BRIDGE_SERVICE_NAME = "m2-ac1-acceptance"

#: The frozen acceptance fixture: page size and per-page deterministic
#: pattern. Bytes derive from the page index only (no clock, no randomness),
#: so the managed original of a given page is byte-identical across runs.
FIXTURE_PAGE_WIDTH = 240
FIXTURE_PAGE_HEIGHT = 320
FIXTURE_PAGE_COUNT = 2

#: Resource ids the bridge catalogs for the m2res protocol. The revision
#: fingerprint of each entry is the translated artifact revision id, so a
#: re-run after a new pipeline execution is a different revision.
RESOURCE_ID_TEMPLATE = "m2ac1-page-{index}"

#: Stable typed error codes (wire-level; never carry OS paths).
E_NOT_SEEDED = "AC1_NOT_SEEDED"
E_SEED_CONFLICT = "AC1_SEED_CONFLICT"
E_PIPELINE_FAILED = "AC1_PIPELINE_FAILED"
E_PAGE_OUT_OF_RANGE = "AC1_PAGE_OUT_OF_RANGE"
E_UNKNOWN_METHOD = "AC1_UNKNOWN_METHOD"
E_BRIDGE_MISCONFIGURED = "AC1_BRIDGE_MISCONFIGURED"


# ---------------------------------------------------------------------------
# deterministic fixture synthesis (pure stdlib PNG encoding)
# ---------------------------------------------------------------------------


def _fixture_pixel(page_index: int, x: int, y: int) -> tuple[int, int, int]:
    """A deterministic per-page colour field with a fixed inner block.

    The base colour is an injective function of the page index so the two
    fixture pages differ from each other (Reader page-turn evidence must be
    able to distinguish them), and the fixed inner block is identical on
    every page so the pattern is recognisable.
    """
    base_r = (37 * page_index + 11) % 256
    base_g = (71 * page_index + 23) % 256
    base_b = (113 * page_index + 5) % 256
    block_x0 = FIXTURE_PAGE_WIDTH // 4
    block_x1 = FIXTURE_PAGE_WIDTH - block_x0
    block_y0 = FIXTURE_PAGE_HEIGHT // 4
    block_y1 = FIXTURE_PAGE_HEIGHT - block_y0
    if block_x0 <= x < block_x1 and block_y0 <= y < block_y1:
        return (255 - base_r, 255 - base_g, 255 - base_b)
    return (base_r, base_g, base_b)


def _png_chunk(tag: bytes, payload: bytes) -> bytes:
    return (
        len(payload).to_bytes(4, "big")
        + tag
        + payload
        + zlib.crc32(tag + payload).to_bytes(4, "big")
    )


def _fixture_region_geometry(width: int, height: int) -> RegionGeometry:
    """The fixed quarter-inset box the seeded Region covers on every page."""
    inset_x = width // 4
    inset_y = height // 4
    bbox = BBox(inset_x, inset_y, width - 2 * inset_x, height - 2 * inset_y)
    polygon = (
        (float(inset_x), float(inset_y)),
        (float(width - inset_x), float(inset_y)),
        (float(width - inset_x), float(height - inset_y)),
        (float(inset_x), float(height - inset_y)),
    )
    return RegionGeometry(bbox=bbox, polygon=polygon)


def synthetic_page_png(page_index: int) -> bytes:
    """Encode one deterministic fixture page as a truecolor PNG."""
    ihdr = (
        FIXTURE_PAGE_WIDTH.to_bytes(4, "big")
        + FIXTURE_PAGE_HEIGHT.to_bytes(4, "big")
        + bytes((8, 2, 0, 0, 0))  # 8-bit depth, truecolor RGB
    )
    raw = bytearray()
    for y in range(FIXTURE_PAGE_HEIGHT):
        raw.append(0)  # filter type: None per scanline
        for x in range(FIXTURE_PAGE_WIDTH):
            raw.extend(_fixture_pixel(page_index, x, y))
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _png_chunk(b"IEND", b"")
    )


def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


# ---------------------------------------------------------------------------
# acceptance assembly (Qt adapters + mock-local providers)
# ---------------------------------------------------------------------------


@dataclass
class AcceptanceState:
    """Everything the bridge needs across one process lifetime."""

    core: CoreServices
    book_id: str
    chapter_id: str


def assemble_acceptance_core(db_path: str | Path, managed_root: str | Path) -> CoreServices:
    """The production Core assembly + Qt adapters + Mock/Local providers.

    Shared by the stdio bridge and ``tests/m2_acceptance`` so the pytest
    suite exercises exactly the assembly the desktop E2E runs. Requires
    PySide6 (the production imaging/rendering adapters); sets the offscreen
    platform so a headless process can render text deterministically.
    """
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QGuiApplication

    if QGuiApplication.instance() is None:
        QGuiApplication(["m2-ac1-acceptance"])
    from application.translation.color.service import SourceStyleService
    from infrastructure.importing import QtImageDecoder
    from infrastructure.rendering.font_catalog import QtFontCatalog
    from infrastructure.rendering.pixel_source_style import PixelSourceStyleAnalyzer
    from infrastructure.rendering.qt_compositor import QtImageCompositor
    from infrastructure.rendering.qt_layout import QtTextLayoutEngine

    font_catalog = QtFontCatalog()
    return assemble_core_services(
        db_path,
        managed_root,
        image_decoder=QtImageDecoder(),
        font_catalog=font_catalog,
        layout_engine=QtTextLayoutEngine(font_catalog),
        compositor=QtImageCompositor(),
        source_styles=SourceStyleService(PixelSourceStyleAnalyzer()),
        mock_local_providers=True,
    )


# ---------------------------------------------------------------------------
# the bridge
# ---------------------------------------------------------------------------


class AcceptanceBridge:
    """Serves the M2-AC1 loop against one assembled Core stack."""

    def __init__(
        self,
        state: AcceptanceState | None = None,
        *,
        data_root: Path | None = None,
        catalog_db: Path | None = None,
        stdin=None,
        stdout=None,
    ) -> None:
        self._state = state
        self._data_root = data_root
        self._catalog_db = catalog_db
        self._stdin = stdin or sys.stdin
        self._stdout = stdout or sys.stdout

    # ------------------------------------------------------------- helpers

    def _require_state(self) -> AcceptanceState:
        if self._state is None:
            raise BridgeError(E_BRIDGE_MISCONFIGURED, "core not assembled")
        return self._state

    def _locator(self) -> SqlitePageArtifactLocator:
        return SqlitePageArtifactLocator(self._require_state().core.conn)

    def _pages(self) -> list:
        state = self._require_state()
        return state.core.repository.list_pages(state.chapter_id)

    def _translated_revision(self, page_id: str):
        return self._locator().locate_current(page_id, ArtifactType.TRANSLATED)

    def _managed_absolute(self, managed_path: str) -> Path:
        return Path(self._require_state().core.storage.absolute_path(managed_path))

    # ------------------------------------------------------------- methods

    def method_ping(self, params: dict) -> dict:
        state = self._require_state()
        return {
            "pong": True,
            "service": BRIDGE_SERVICE_NAME,
            "pid": os.getpid(),
            "data_root": str(state.core.data_root),
        }

    def method_status(self, params: dict) -> dict:
        """Which loop phase applies to this data root (AC3 phase decision)."""
        try:
            state = self._require_state()
        except BridgeError:
            return {"phase": "empty"}
        pages = self._pages()
        restored = [
            {
                "index": index,
                "resource_id": RESOURCE_ID_TEMPLATE.format(index=index),
                "revision": (
                    located[1].artifact_revision_id
                    if (located := self._translated_revision(page.page_id)) is not None
                    else None
                ),
            }
            for index, page in enumerate(pages)
        ]
        complete = bool(pages) and all(entry["revision"] for entry in restored)
        if not complete:
            return {"phase": "empty"}
        run_status = self._latest_run_status()
        return {
            "phase": "restore",
            "page_count": len(pages),
            "run_status": run_status,
            "pages": restored,
        }

    def method_seed_fixture(self, params: dict) -> dict:
        """Synthetic Book/Chapter/pages through the REAL import path (AC1).

        Each page also gets one Region through the production
        ``RegionEditingService`` write path (the same seam the detect step's
        ``region_creator`` uses), so the pipeline plan starts at ``ocr`` —
        the designed region-level chain — instead of relying on the
        detect-then-backfill flow.
        """
        state = self._require_state()
        if self._pages():
            raise BridgeError(
                E_SEED_CONFLICT, "this data root already contains a seeded chapter"
            )
        book = state.core.library.create_book("M2-AC1 Acceptance Fixture")
        chapter = state.core.library.create_chapter(book.book_id, "Fixture Chapter")
        sources = [
            ImportSource(
                filename=f"fixture-page-{index + 1}.png",
                data_provider=lambda index=index: synthetic_page_png(index),
            )
            for index in range(FIXTURE_PAGE_COUNT)
        ]
        report = state.core.importer.import_files(chapter.chapter_id, sources)
        if report.failed or len(report.imported) != FIXTURE_PAGE_COUNT:
            raise BridgeError(
                E_BRIDGE_MISCONFIGURED,
                f"fixture import failed: {len(report.failed)} failed",
            )
        for index, page in enumerate(state.core.repository.list_pages(chapter.chapter_id)):
            state.core.editing.create_region(
                page.page_id,
                _fixture_region_geometry(page.width or FIXTURE_PAGE_WIDTH, page.height or FIXTURE_PAGE_HEIGHT),
                reading_order=1,
                # MACHINE, same origin the detect step's region_creator uses:
                # this is a harness-fabricated fixture region, not a user
                # edit, so USER would misrepresent its provenance (F-013).
                origin=RegionOrigin.MACHINE,
            )
        state.book_id = book.book_id
        state.chapter_id = chapter.chapter_id
        return {
            "page_count": len(report.imported),
            "fixture_shas": [
                sha256_hex(synthetic_page_png(index))
                for index in range(FIXTURE_PAGE_COUNT)
            ],
        }

    def method_run_pipeline(self, params: dict) -> dict:
        """The Mock/Local pipeline through the production run seam (AC1).

        The seeded fixture always carries Regions, so the planner plans the
        designed region-level chain (starting at ``ocr``) and a single
        plan/execute pair completes the run. The ``resume_blocked`` branch
        below is kept as a fail-closed safety net for the region-less case;
        it is NOT exercised by the released acceptance evidence (DSH r1
        F-007), and the region-less detect→backfill chain has a known
        production planner gap (Handoff §风险与遗留) that must not be
        reported as covered by this Task. Both phases are the production
        service API — no planner logic is reimplemented here.
        """
        state = self._require_state()
        pages = self._pages()
        if not pages:
            raise BridgeError(E_NOT_SEEDED, "seed the fixture before running the pipeline")
        bindings = {
            "ocr": "m2ac1-mock-ocr",
            "translate": "m2ac1-mock-translate",
        }
        for step_type, provider_id in bindings.items():
            state.core.pipeline_defaults.save_provider_binding(step_type, provider_id)
        run = state.core.pipeline.create_run(
            CommandType.TRANSLATE_ALL,
            PipelineScope("chapter", chapter_id=state.chapter_id),
        )
        state.core.pipeline.plan_run(run.run_id)
        finished = state.core.pipeline.execute_run(run.run_id)
        if finished.status == "blocked":
            state.core.pipeline.plan_run(run.run_id, mode="resume_blocked")
            finished = state.core.pipeline.execute_run(run.run_id)
        if finished.status != "completed":
            raise BridgeError(
                E_PIPELINE_FAILED,
                json.dumps({"status": finished.status}, sort_keys=True),
            )
        return {
            "status": finished.status,
            "command": CommandType.TRANSLATE_ALL.value,
            "providers": dict(bindings),
        }

    def method_saved_summary(self, params: dict) -> dict:
        """Re-read the persisted result from SQLite + managed files (AC2)."""
        state = self._require_state()
        pages = self._pages()
        saved = []
        for index, page in enumerate(pages):
            located = self._translated_revision(page.page_id)
            if located is None:
                raise BridgeError(E_NOT_SEEDED, f"page {index} has no translated revision")
            record, revision = located
            payload = self._managed_absolute(revision.managed_path).read_bytes()
            if sha256_hex(payload) != revision.file_hash:
                raise BridgeError(
                    E_BRIDGE_MISCONFIGURED, f"page {index} digest mismatch on re-read"
                )
            saved.append(
                {
                    "index": index,
                    "sha256": revision.file_hash,
                    "size": len(payload),
                }
            )
        run_status = self._latest_run_status()
        if run_status != "completed":
            raise BridgeError(E_PIPELINE_FAILED, f"latest run status is {run_status!r}")
        return {
            "run_status": run_status,
            "pages": saved,
            "providers": self._bound_providers(),
        }

    def method_catalog_pages(self, params: dict) -> dict:
        """Publish translated pages into the m2res catalog authority (AC2/AC4)."""
        state = self._require_state()
        if self._catalog_db is None:
            raise BridgeError(E_BRIDGE_MISCONFIGURED, "catalog db path not configured")
        catalog = ResourceCatalogStore(self._catalog_db)
        try:
            cataloged = []
            for index, page in enumerate(self._pages()):
                located = self._translated_revision(page.page_id)
                if located is None:
                    raise BridgeError(E_NOT_SEEDED, f"page {index} has no translated revision")
                revision = located[1]
                rel_path = Path(revision.managed_path).as_posix()
                catalog.upsert(
                    RESOURCE_ID_TEMPLATE.format(index=index),
                    "managed-read-only",
                    rel_path,
                )
                cataloged.append(
                    {
                        "index": index,
                        "resource_id": RESOURCE_ID_TEMPLATE.format(index=index),
                        "revision": revision.artifact_revision_id,
                    }
                )
        finally:
            catalog.close()
        return {"pages": cataloged}

    def method_reader_pages(self, params: dict) -> dict:
        """The reader view of the RESTORED result (AC4; no pipeline rerun)."""
        state = self._require_state()
        reader_pages = state.core.reader_catalog.list_pages(state.chapter_id)
        if not reader_pages:
            raise BridgeError(E_NOT_SEEDED, "the chapter has no reader pages")
        pages = []
        for index, reader_page in enumerate(reader_pages):
            if reader_page.translated_path is None:
                raise BridgeError(E_NOT_SEEDED, f"reader page {index} has no translated image")
            pages.append(
                {
                    "index": index,
                    "page_id": reader_page.page_id,
                    "filename": reader_page.filename,
                    "resource_id": RESOURCE_ID_TEMPLATE.format(index=index),
                    "revision": reader_page.translated_revision_id,
                }
            )
        return {"book_id": state.book_id, "chapter_id": state.chapter_id, "pages": pages}

    def method_record_reading(self, params: dict) -> dict:
        """Persist real reading progress for the visited pages (AC4)."""
        state = self._require_state()
        visited = params.get("visited")
        if not isinstance(visited, list) or not visited:
            raise BridgeError(E_BRIDGE_MISCONFIGURED, "visited must be a non-empty list")
        reading: ReadingService = state.core.reading
        reader_pages = state.core.reader_catalog.list_pages(state.chapter_id)
        reading.open(
            state.book_id,
            state.chapter_id,
            reader_pages,
            mode=ReadingMode.TRANSLATED,
        )
        for index in sorted(int(value) for value in visited):
            if not 0 <= index < len(reader_pages):
                raise BridgeError(E_PAGE_OUT_OF_RANGE, f"page index {index} out of range")
            reading.jump_to_page(index)
            reading.add_time(1)
        page_index = reading.page_index
        reading.close()
        return {
            "visited": visited,
            "final_page_index": page_index,
            "page_count": len(reader_pages),
        }

    def method_export_page(self, params: dict) -> dict:
        """Single-page PNG export from the restored Reader state (AC5)."""
        state = self._require_state()
        page_index = int(params.get("page_index", 0))
        reader_pages = state.core.reader_catalog.list_pages(state.chapter_id)
        if not 0 <= page_index < len(reader_pages):
            raise BridgeError(E_PAGE_OUT_OF_RANGE, f"page index {page_index} out of range")
        reader_page = reader_pages[page_index]
        exports_dir = state.core.data_root / "exports"
        exports_dir.mkdir(parents=True, exist_ok=True)
        output_path = exports_dir / f"m2ac1-export-page-{page_index + 1}.png"

        def source_bytes() -> bytes:
            return Path(reader_page.original_path).read_bytes()

        def translated_bytes() -> bytes:
            return Path(reader_page.translated_path).read_bytes()

        result = state.core.export_service.export(
            ExportRequest(
                book_id=state.book_id,
                chapter_id=state.chapter_id,
                format=ExportFormat.SINGLE_IMAGE,
                output_path=output_path,
                pages=(
                    ExportPage(
                        page_id=reader_page.page_id,
                        filename=reader_page.filename,
                        source_provider=source_bytes,
                        translated_provider=translated_bytes,
                        translated_revision_id=reader_page.translated_revision_id,
                        current_translated_revision_id=(
                            reader_page.current_translated_revision_id
                        ),
                    ),
                ),
                mode="translated",
                overwrite_policy=OverwritePolicy.OVERWRITE,
                stale_policy=StalePolicy.ABORT,
            )
        )
        payload = output_path.read_bytes()
        return {
            "export_id": result.export_id,
            "page_index": page_index,
            "sha256": sha256_hex(payload),
            "size": len(payload),
            "output_path": output_path.name,
        }

    # ------------------------------------------------------------- storage

    def _latest_run_status(self) -> str | None:
        row = self._require_state().core.conn.execute(
            "SELECT status FROM pipeline_runs ORDER BY rowid DESC LIMIT 1"
        )
        record = row.fetchone()
        return record["status"] if record is not None else None

    def _bound_providers(self) -> dict:
        defaults = self._require_state().core.pipeline_defaults.read()
        return {
            step: binding
            for step, binding in defaults.provider_bindings.items()
            if isinstance(binding, str)
        }

    # -------------------------------------------------------------- serving

    def _dispatch(self, request: dict) -> dict:
        method = request.get("method", "")
        if method == "shutdown":
            return {"result": {"bye": True}}
        params = request.get("params") or {}
        handler = {
            "ping": self.method_ping,
            "status": self.method_status,
            "seed_fixture": self.method_seed_fixture,
            "run_pipeline": self.method_run_pipeline,
            "saved_summary": self.method_saved_summary,
            "catalog_pages": self.method_catalog_pages,
            "reader_pages": self.method_reader_pages,
            "record_reading": self.method_record_reading,
            "export_page": self.method_export_page,
        }.get(method)
        if handler is None:
            return {"error": {"code": E_UNKNOWN_METHOD}}
        try:
            return {"result": handler(params)}
        except BridgeError as error:
            return {"error": {"code": error.code, "detail": error.detail}}

    def serve_forever(self) -> int:
        for line in self._stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                self._emit({"id": None, "error": {"code": E_BRIDGE_MISCONFIGURED}})
                continue
            response = self._dispatch(request)
            response["id"] = request.get("id")
            if request.get("method") == "shutdown":
                self._emit(response)
                return 0
            self._emit(response)
        return 0

    def _emit(self, payload: dict) -> None:
        self._stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
        self._stdout.flush()


class BridgeError(Exception):
    """A typed acceptance failure; the wire carries code + detail only."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def main() -> int:
    data_root = Path(
        os.environ.get("NEWMANGA_DATA_ROOT")
        or (Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "New Manga")
    )
    db_path = data_root / "library.db"
    managed_root = data_root / "managed"
    catalog_db = os.environ.get("M2RC2_CATALOG_DB")
    state: AcceptanceState | None = None
    if os.environ.get("M2AC1_TEST_MODE") == "1":
        core = assemble_acceptance_core(db_path, managed_root)
        # a fresh data root has no book/chapter ids until seeded; recover them
        # after a restart so restore methods work without re-running anything
        book = core.repository.list_books()
        chapter = (
            core.repository.list_chapters(book[0].book_id) if book else []
        )
        state = AcceptanceState(
            core=core,
            book_id=book[0].book_id if book else "",
            chapter_id=chapter[0].chapter_id if chapter else "",
        )
    server = AcceptanceBridge(
        state,
        data_root=data_root,
        catalog_db=Path(catalog_db) if catalog_db else None,
    )
    return server.serve_forever()


if __name__ == "__main__":
    raise SystemExit(main())
