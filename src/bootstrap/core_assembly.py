"""Qt-free Python Core service assembly (M2-I1 Core Assembly Seam).

``assemble_core_services`` opens and migrates the SQLite library on a real
data root and builds the Qt-free production stack: repositories, Managed
Copy storage, importers, trash, provider runtime, pipeline (with startup
``recover_running_runs``), diagnostics, legacy JSON import, reading/export
stores and the render service.  It never imports ``PySide6`` or ``src/ui``
at module scope, so it can be imported — and, given adapters, exercised —
in a process without Qt (M2-D1 M2D1-15/21).

Adapter injection (I1-AC4): the Qt implementations of the imaging/rendering
ports — ``QtImageDecoder``, ``QtFontCatalog``, ``QtTextLayoutEngine``,
``QtImageCompositor``, ``PixelSourceStyleAnalyzer`` — are constructed by the
Legacy Qt assembly (``bootstrap.app``) and passed in here; this module never
constructs them or any ``QObject`` viewmodel.  The side-effect order of the
assembly (schema check → migrations → managed layout → provider settings →
``recover_running_runs`` → diagnostics store → legacy JSON import) is the
historical ``bootstrap.app.assemble_services`` order, unchanged.

The pixel helpers below (``_ManagedPageImageSource`` and
``_render_content_decoder``) keep their lazy in-function Qt imports: module
import stays Qt-free, and replacing them with a Qt-free pixel path is a
separately released M2 slice (M2-D1 M2D1-10/23).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import sqlite3

from application.editing.service import RegionEditingService
from application.export import ExportService
from application.importing.documents import ImportDocumentsUseCase
from application.importing.images.ports import ImageDecoder
from application.importing.images.service import ImportImagesUseCase
from application.library.service import LibraryService
from application.maintenance import TrashService
from application.maintenance.diagnostics import BoundedErrorLog, DiagnosticsService
from application.maintenance.trash import _JsonTrashManifest
from application.reading.service import ReadingService
from application.rendering.service import RenderService
from application.tasks.service import PipelineService
from application.translation.color.service import SourceStyleService
from application.translation.knowledge.term_extraction import TermExtractionService
from domain.regions.entities import BBox, RegionGeometry, RegionOrigin
from infrastructure.filesystem.bounded_log_store import BoundedLogStore
from infrastructure.filesystem.managed_storage import ManagedFileStorage
from infrastructure.imaging.webtoon_tiles import TileCache, TiledPageRasterizer
from infrastructure.importing import (
    ManagedCopyStoreAdapter,
    MobiDocumentRaster,
    PdfiumDocumentRaster,
)
from infrastructure.pipeline.assembly import build_production_pipeline
from infrastructure.providers.detection_doctr import (
    DOCTR_WEIGHTS_FILENAME,
    DoctrDetectionProvider,
)
from infrastructure.providers.handlers import (
    RegionMaskGeometry,
    build_production_handlers,
)
from infrastructure.providers.runtime import build_provider_runtime
from infrastructure.providers.step_writes import ArtifactStepWriter, RegionStepWriter
from infrastructure.rendering.locator import SqlitePageArtifactLocator
from ports.rendering.ports import FontCatalog, ImageCompositor, TextLayoutEngine
from infrastructure.sqlite.artifacts import SqliteArtifactRepository
from infrastructure.sqlite.connection import ThreadRoutedConnection, open_database
from infrastructure.sqlite.library import SqliteLibraryRepository
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.reading_export import (
    SqliteExportHistoryStore,
    SqliteReadingProgressStore,
    import_legacy_export_history,
    import_legacy_reading_progress,
)
from infrastructure.sqlite.regions import SqliteRegionRepository
from infrastructure.sqlite.schema import default_migrations
from infrastructure.transport.stdlib import StdlibTransport
from ports.inpaint.ports import ImageFrame
from ports.repositories.artifacts import ArtifactType
from ports.providers.errors import ProviderInputError

_APP_VERSION = "0.1.0"


@dataclass(frozen=True)
class _ProductionDiagnosticsSnapshot:
    database: Path
    data_root: Path
    managed_root: Path
    diagnostics_root: Path
    schema: int
    configured: bool

    def app_version(self) -> str:
        return _APP_VERSION

    def platform_python(self) -> str:
        return platform.python_version()

    def schema_version(self) -> int:
        return self.schema

    def database_path(self) -> str:
        return str(self.database)

    def settings_summary(self) -> dict[str, str]:
        return {
            "pipeline_defaults": "configured" if self.configured else "not-configured"
        }

    def environment_paths(self) -> dict[str, str]:
        return {
            "data_root": str(self.data_root),
            "managed_root": str(self.managed_root),
            "diagnostics_root": str(self.diagnostics_root),
        }


class _BoundedDiagnosticsSink:
    def __init__(self, store: BoundedLogStore) -> None:
        self._store = store

    def write_report(self, payload: bytes, generated_at: str) -> str:
        del generated_at
        timestamp = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        return str(self._store.write(payload.decode("utf-8"), timestamp=timestamp))


class _ManagedPageCatalog:
    """Expose SQLite pages and immutable Managed Copy URLs to the Viewer."""

    def __init__(
        self,
        repository: SqliteLibraryRepository,
        storage: ManagedFileStorage,
        locator: SqlitePageArtifactLocator,
    ) -> None:
        self._repository = repository
        self._storage = storage
        self._locator = locator

    def list_pages(self, chapter_id: str):
        return self._repository.list_pages(chapter_id)

    def image_url(self, page_id: str, mode: str) -> str:
        """Workbench viewer image for one mode (TASK-051 AC ①).

        ``original``/``compare`` both show the immutable Managed Copy —
        compare is the D05 §20.1 side-by-side, whose left pane *is* the
        original (ViewerPanel.qml). ``translated`` is the page's current
        TRANSLATED artifact revision, resolved through the same locator
        the reader uses, so both surfaces show the same revision (AC ②).
        Every failure collapses to "" (the QML empty-state contract);
        :meth:`image_state` carries the typed reason.
        """
        page = self._repository.get_page(page_id)
        if page is None:
            return ""
        if mode == "translated":
            located = self._locator.locate_current(page_id, ArtifactType.TRANSLATED)
            if located is None:
                return ""
            _record, revision = located
            return self._uri_within(revision.managed_path)
        if mode in ("original", "compare"):
            if not page.managed_original_ref:
                return ""
            return self._uri_within(page.managed_original_ref)
        return ""  # unknown mode: not a silent wrong image

    def image_state(self, page_id: str, mode: str) -> str:
        """Typed empty-state channel (TASK-051 AC ③): ``ok``/``missing``/``invalid``.

        ``missing`` = the page or its artifact does not exist yet; ``invalid``
        = a reference exists but escapes the managed root or the file is gone.
        The VM exposes this so "no data" and "broken path" stay
        distinguishable without changing the QML contract (TASK-047-gated).
        """
        page = self._repository.get_page(page_id)
        if page is None:
            return "missing"
        if mode == "translated":
            located = self._locator.locate_current(page_id, ArtifactType.TRANSLATED)
            if located is None:
                return "missing"
            ref: str | None = located[1].managed_path
        else:
            ref = page.managed_original_ref
        if not ref:
            return "missing"
        root = self._storage.root.resolve()
        path = Path(self._storage.absolute_path(ref)).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            return "invalid"
        return "ok" if path.is_file() else "invalid"

    def _uri_within(self, ref: str) -> str:
        root = self._storage.root.resolve()
        path = Path(self._storage.absolute_path(ref)).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            return ""
        return path.as_uri() if path.is_file() else ""


class _ManagedPageImageSource:
    """Pixel access for provider steps (D06 §6/§7 input, D07 §37).

    Only the immutable Managed Copy is read; a missing or undecodable file is a
    typed provider-input failure, never an empty image.
    """

    def __init__(
        self,
        repository: SqliteLibraryRepository,
        storage: ManagedFileStorage,
        regions: SqliteRegionRepository,
    ) -> None:
        self._repository = repository
        self._storage = storage
        self._regions = regions

    def _page_image(self, page_id: str):
        from PySide6.QtGui import QImage

        page = self._repository.get_page(page_id)
        if page is None or not page.managed_original_ref:
            raise ProviderInputError(
                f"page {page_id!r} has no managed original", stage="image-source"
            )
        root = self._storage.root.resolve()
        path = Path(self._storage.absolute_path(page.managed_original_ref)).resolve()
        try:
            path.relative_to(root)
        except ValueError as error:
            raise ProviderInputError(
                f"managed original for {page_id!r} escapes the data root",
                stage="image-source",
            ) from error
        if not path.is_file():
            raise ProviderInputError(
                f"managed original is missing: {path}", stage="image-source"
            )
        image = QImage(str(path))
        if image.isNull():
            raise ProviderInputError(
                f"managed original is not decodable: {path}", stage="image-source"
            )
        return image

    def page_frame(self, page_id: str) -> ImageFrame:
        from PySide6.QtGui import QImage

        image = self._page_image(page_id).convertToFormat(QImage.Format.Format_RGB32)
        width, height = image.width(), image.height()
        return ImageFrame(width, height, "rgb32", bytes(image.constBits()))

    def region_crop(self, page_id: str, region_id: str) -> tuple[bytes, int, int]:
        from PySide6.QtCore import QBuffer, QIODevice, QRect
        from PySide6.QtGui import QImage

        page = self._repository.get_page(page_id)
        if page is None:
            raise ProviderInputError(
                f"page {page_id!r} is not available", stage="image-source"
            )
        region = self._regions.get_region(region_id)
        if region is None:
            raise ProviderInputError(
                f"region {region_id!r} is not available", stage="image-source"
            )
        image = self._page_image(page_id)
        bbox = region.geometry.bbox
        rect = QRect(bbox.x, bbox.y, bbox.width, bbox.height).intersected(
            QRect(0, 0, image.width(), image.height())
        )
        if rect.isEmpty():
            raise ProviderInputError(
                f"region {region_id!r} lies outside the page", stage="image-source"
            )
        crop = image.copy(rect).convertToFormat(QImage.Format.Format_RGB888)
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        if not crop.save(buffer, "PNG"):
            raise ProviderInputError(
                "region crop could not be encoded", stage="image-source"
            )
        return bytes(buffer.data()), crop.width(), crop.height()

    def page_png(self, page_id: str) -> bytes:
        """The whole Managed Copy page as PNG (TASK-033 color step input)."""
        from PySide6.QtCore import QBuffer, QIODevice

        image = self._page_image(page_id)
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        if not image.save(buffer, "PNG"):
            raise ProviderInputError(
                f"page {page_id!r} could not be re-encoded as PNG",
                stage="image-source",
            )
        return bytes(buffer.data())


class _ManagedReaderCatalog:
    """Repository pages in the reader's ``ReaderPage`` contract (TASK-038).

    Originals come straight from the Managed Copy; the translated image is
    the page's current TRANSLATED artifact (empty when the page has none —
    the reader then falls back to the original with an explicit status
    message, D06 §97). OCR text lives on Regions, not on the page, so
    ``text`` stays empty here (translated-export text is a separate seam).
    """

    def __init__(
        self,
        repository: SqliteLibraryRepository,
        storage: ManagedFileStorage,
        locator: SqlitePageArtifactLocator,
    ) -> None:
        self._repository = repository
        self._storage = storage
        self._locator = locator

    def list_pages(self, chapter_id: str) -> list:
        from application.reading.ports import ReaderPage
        from ports.repositories.artifacts import ArtifactType

        rows = []
        for page in self._repository.list_pages(chapter_id):
            original = (
                self._storage.absolute_path(page.managed_original_ref)
                if page.managed_original_ref
                else ""
            )
            translated = ""
            translated_revision = None
            current_revision = None
            located = self._locator.locate_current(
                page.page_id, ArtifactType.TRANSLATED
            )
            if located is not None:
                _record, revision = located
                translated = self._storage.absolute_path(revision.managed_path)
                translated_revision = revision.artifact_revision_id
                current_revision = revision.artifact_revision_id
            rows.append(
                ReaderPage(
                    page_id=page.page_id,
                    filename=page.source_filename,
                    original_path=original,
                    translated_path=translated or None,
                    translated_revision_id=translated_revision,
                    current_translated_revision_id=current_revision,
                )
            )
        return rows


class _RegionGeometrySource:
    """Region geometry as mask primitives (D06 §19 Segment input)."""

    def __init__(self, regions: SqliteRegionRepository) -> None:
        self._regions = regions

    def mask_geometry(self, region_id: str) -> RegionMaskGeometry:
        region = self._regions.get_region(region_id)
        if region is None or region.deleted:
            raise ProviderInputError(
                f"region {region_id!r} is not available", stage="segment"
            )
        bbox = region.geometry.bbox
        boxes = ((bbox.x, bbox.y, bbox.x + bbox.width, bbox.y + bbox.height),)
        return RegionMaskGeometry(boxes=boxes, polygons=(region.geometry.polygon,) if region.geometry.polygon else ())


def _render_content_decoder(relative_path: str, payload: bytes) -> bytes:
    """TASK-033 assembly bridge: pipeline ``NMFR`` containers → PNG.

    Inpaint/Clean revisions are stored in the provider layer's
    ``application/x-newmanga-frame`` container (a deliberate non-shareable
    format, TASK-018); rendering composes on PNG. Payloads that are not
    ``NMFR`` (PNG originals, translated PNGs) pass through unchanged, so this
    is a pure format bridge at the seam — the stored revisions stay untouched.
    """
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QImage

    if not payload.startswith(b"NMFR"):
        return payload
    from infrastructure.providers.step_writes import decode_frame_payload

    header, raw = decode_frame_payload(payload)
    mode = str(header.get("mode", ""))
    width, height = int(header["width"]), int(header["height"])
    if mode != "rgb32":
        raise ProviderInputError(
            f"unsupported frame mode {mode!r} for the render bridge",
            stage="render",
        )
    bytes_per_line = width * 4
    if len(raw) < bytes_per_line * height:
        raise ProviderInputError("frame payload is truncated", stage="render")
    image = QImage(raw, width, height, bytes_per_line, QImage.Format.Format_RGB32)
    if image.isNull():
        raise ProviderInputError(
            "frame payload could not be decoded for rendering", stage="render"
        )
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    if not image.save(buffer, "PNG"):
        raise ProviderInputError(
            "clean frame could not be re-encoded as PNG", stage="render"
        )
    return bytes(buffer.data())


def _load_pipeline_defaults(conn: sqlite3.Connection) -> dict:
    """Read the persisted pipeline defaults row (TASK-050 AC ①).

    Same tolerant decoding as :func:`_load_pipeline_settings`, extended to
    all four columns. An unconfigured (or corrupt) install decodes to
    all-empty values so the assembly keeps passing ``None`` and the
    snapshot provider's bootstrap stays byte-identical.
    """
    empty = {
        "settings": {},
        "provider_bindings": {},
        "constraint_snapshot_ref": None,
        "context_policy": {},
    }
    try:
        row = conn.execute(
            "SELECT settings_json, provider_bindings_json, constraint_snapshot_ref,"
            " context_policy_json FROM pipeline_defaults WHERE defaults_id = 1"
        ).fetchone()
    except sqlite3.Error:
        return dict(empty)  # un-migrated storage: all-empty, never a crash
    if row is None:
        # a fresh database has no defaults row until the snapshot provider
        # seeds one — identical semantics to an explicitly empty row
        return dict(empty)

    def _mapping(raw: object) -> dict:
        if not isinstance(raw, str) or not raw:
            return {}
        try:
            loaded = json.loads(raw)
        except (ValueError, TypeError):
            return {}
        return loaded if isinstance(loaded, dict) else {}

    return {
        "settings": _mapping(row[0]),
        "provider_bindings": _mapping(row[1]),
        "constraint_snapshot_ref": row[2] if isinstance(row[2], str) else None,
        "context_policy": _mapping(row[3]),
    }


def _load_pipeline_settings(conn: sqlite3.Connection) -> dict:
    """Read the persisted pipeline defaults (empty when never configured)."""
    try:
        row = conn.execute(
            "SELECT settings_json FROM pipeline_defaults WHERE defaults_id = 1"
        ).fetchone()
    except sqlite3.Error:
        return {}
    if row is None or not row[0]:
        return {}
    try:
        loaded = json.loads(row[0])
    except (ValueError, TypeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _credential_store() -> "WindowsCredentialStore | None":
    """The production Windows vault, best effort (AC-OPTIONAL-001).

    A vault that cannot be opened must not stop the app from starting:
    ``None`` keeps providers reporting Not-Ready with
    ``MISSING_CREDENTIAL`` and leaves the transport without a proxy
    credential source instead of failing the assembly.
    """
    try:
        from infrastructure.credentials.windows import WindowsCredentialStore

        return WindowsCredentialStore()
    except Exception:
        return None


def _credential_resolver(
    store: "WindowsCredentialStore | None" = None,
) -> Callable[[str], str | None] | None:
    """Resolve provider credentials from the production vault, best effort."""
    if store is None:
        store = _credential_store()
    if store is None:
        return None

    def resolve(ref: str) -> str | None:
        try:
            return store.resolve_credential(ref).reveal()
        except Exception:
            return None

    return resolve


@dataclass
class CoreServices:
    """The Qt-free production stack (M2-I1).

    Everything here is assembled without ``PySide6`` or ``src/ui``; the
    Legacy Qt assembly (``bootstrap.app``) layers the QObject viewmodels on
    top. ``conn`` is the thread-routed SQLite facade exposed so the entry
    can close every per-thread connection before temp-root cleanup — the
    last writer holds the Windows file lock.
    """

    conn: ThreadRoutedConnection
    repository: SqliteLibraryRepository
    storage: ManagedFileStorage
    importer: ImportImagesUseCase
    document_importer: ImportDocumentsUseCase
    trash: TrashService
    reading: ReadingService
    export_service: ExportService
    diagnostics: DiagnosticsService
    library: LibraryService
    pipeline: PipelineService
    pipeline_defaults: "PipelineDefaultsService"
    editing: RegionEditingService
    render: RenderService
    providers: object
    page_catalog: _ManagedPageCatalog
    reader_catalog: _ManagedReaderCatalog
    #: T1.2.1 B-003 (R5): the one vault shared by transport, provider
    #: resolver and the settings stack; ``None`` keeps every consumer in
    #: its best-effort fallback.
    credential_store: "WindowsCredentialStore | None"
    transport: StdlibTransport | None
    data_root: Path
    #: Reader tile factory (Qt-free: stdlib streaming PNG, TASK-020/042);
    #: the cache lives under the managed root.
    tile_factory: Callable[[str], TiledPageRasterizer]


def default_data_root() -> Path:
    root = os.environ.get("NEWMANGA_DATA_ROOT")
    if root:
        return Path(root)
    local_app_data = os.environ.get("LOCALAPPDATA")
    base = Path(local_app_data) if local_app_data else Path.home()
    return base / "New Manga"


def assemble_core_services(
    db_path: str | Path,
    managed_root: str | Path,
    *,
    image_decoder: ImageDecoder,
    font_catalog: FontCatalog,
    layout_engine: TextLayoutEngine,
    compositor: ImageCompositor,
    source_styles: SourceStyleService,
    content_decoder: Callable[[str, bytes], bytes] | None = None,
    mock_local_providers: bool = False,
) -> CoreServices:
    """Open + migrate the SQLite library and build the Qt-free services.

    Refuses to run against a database written by a newer schema (AC-DB-005):
    ``open_database`` reopens it ``query_only`` and this assembly fails fast
    instead of blind-writing.

    Adapter injection (I1-AC4): the imaging/rendering adapters are required
    keyword arguments — this assembly never constructs a Qt implementation
    itself. ``content_decoder`` defaults to the lazy ``NMFR`` bridge, keeping
    the historical production behaviour when the caller does not override.

    ``mock_local_providers`` (M2-AC1): opt-in acceptance mode. When set, the
    deterministic Mock/Local detect/OCR/translation providers are registered
    on the runtime registry and the ``detect`` step uses the mock detector
    instead of the docTR weights path. The default ``False`` keeps the
    production assembly behaviour byte-identical; only the acceptance
    harness (``bootstrap.acceptance_bridge``) may set it.
    """
    migrations = default_migrations()
    latest_known = max(migration.schema_version for migration in migrations)
    conn, opened = open_database(db_path, latest_known_schema_version=latest_known)
    try:
        if not opened.writable:
            raise RuntimeError(
                f"database schema v{opened.schema_version} is newer than this "
                f"application knows (v{latest_known}); refusing to run"
            )
        MigrationRunner(conn, migrations).apply_pending()

        repository = SqliteLibraryRepository(conn)
        storage = ManagedFileStorage(managed_root)
        storage.ensure_layout()
        library = LibraryService(repository)
        regions = SqliteRegionRepository(conn)

        def book_id_for_chapter(chapter_id: str) -> str:
            # Real Chapter→Book lookup for the D03 §18 managed layout; an
            # unknown chapter fails the copy, so no page can be written.
            chapter = repository.get_chapter(chapter_id)
            if chapter is None:
                raise ValueError(f"unknown chapter: {chapter_id!r}")
            return chapter.book_id

        copy_store = ManagedCopyStoreAdapter(storage, book_id_for_chapter)
        importer = ImportImagesUseCase(
            image_decoder,
            copy_store,
            repository,
        )
        # TASK-023 AC ④ / TASK-041 AC ②: document import rides the same
        # Managed Copy store and page sink as image import. PDF goes through
        # PDFium; picture MOBI (user-approved dependency mobi==0.4.1) goes
        # through its own adapter behind the same port. Text-only and
        # DRM-protected MOBI fail typed at the adapter.
        document_importer = ImportDocumentsUseCase(
            PdfiumDocumentRaster(),
            copy_store,
            repository,
            mobi_raster=MobiDocumentRaster(),
        )
        # TASK-021 trash subset: page-level soft delete / batch restore /
        # controlled-only purge. The manifest lives next to the managed data.
        trash = TrashService(
            repository,
            storage,
            _JsonTrashManifest(Path(managed_root) / "trash-manifest.json"),
        )
        # TASK-019: the production Pipeline receives real handlers built from
        # the provider runtime. Nothing is wired when no provider is ready:
        # the step then fails with PROVIDER_UNAVAILABLE / Not-Ready instead of
        # inventing a deterministic placeholder.
        # T1.2.1 R3: the persisted step bindings ride along so a bound
        # settings profile is projected onto its registry slot at assembly.
        # B-003 (R5): the transport shares the same production vault as the
        # providers, so authenticated proxies resolve their credential at
        # send time; a vault that cannot be opened leaves it ``None`` and
        # the app still starts (AC-OPTIONAL-001).
        credential_store = _credential_store()
        transport = StdlibTransport(credential_store=credential_store)
        provider_runtime = build_provider_runtime(
            settings=_load_pipeline_settings(conn),
            provider_bindings=_load_pipeline_defaults(conn)["provider_bindings"],
            transport=transport,
            credential_resolver=_credential_resolver(credential_store),
        )
        # M2-AC1 acceptance mode: the Mock/Local providers join the runtime
        # registry only behind this explicit flag (never in production).
        detector: object
        if mock_local_providers:
            from infrastructure.providers.mock_local import (
                MockLocalDetectionProvider,
                register_mock_local_providers,
            )

            register_mock_local_providers(provider_runtime.registry)
            detector = MockLocalDetectionProvider()
        else:
            # T1.1.1: the selected production detector (docTR fast_base, see
            # doc/research/T1.1.1-detector-evaluation.md) is wired through the
            # application-layer region_creator below. The provider is lazy and
            # strictly offline: weights must exist as a local file (default
            # <data root>/models/detector/, override NEWMANGA_DETECTOR_WEIGHTS)
            # with the pinned SHA-256, or the ``detect`` step fails closed with
            # PROVIDER_NOT_CONFIGURED at run time — the same diagnosable gap as
            # an unwired detector. No download, no fallback.
            detector_weights = Path(
                os.environ.get(
                    "NEWMANGA_DETECTOR_WEIGHTS",
                    str(
                        Path(db_path).resolve().parent
                        / "models"
                        / "detector"
                        / DOCTR_WEIGHTS_FILENAME
                    ),
                )
            )
            detector = DoctrDetectionProvider(
                weights_path=detector_weights,
                device=os.environ.get("NEWMANGA_DETECTOR_DEVICE", "cpu"),
            )
        # TASK-033: the render step needs the application-layer RenderService,
        # assembled here from the existing infrastructure/rendering adapters
        # (no adapter implementation is added or modified). The Qt adapters
        # arrive through the injection seam above; the Legacy Qt assembly
        # constructs them and needs a QGuiApplication instance, which the
        # entry creates before calling this.
        render_service = RenderService(
            region_repo=regions,
            locator=SqlitePageArtifactLocator(conn),
            artifacts=SqliteArtifactRepository(conn, storage),
            storage=storage,
            layout_engine=layout_engine,
            compositor=compositor,
            source_styles=source_styles,
            font_catalog=font_catalog,
            content_decoder=(
                content_decoder if content_decoder is not None
                else _render_content_decoder
            ),
        )
        # TASK-049 AC ②: the one application-layer Region write path —
        # ``RegionEditingService.create_region`` (first revision + pointer in
        # one atomic commit, TASK-002 §2.1) — is also what the ``detect``
        # step's candidates flow through; the handler never writes Regions
        # itself and no second write path is invented.
        editing = RegionEditingService(regions)

        def _create_detected_region(
            page_id: str,
            polygon: tuple[tuple[float, float], ...],
            reading_order: int,
            _provenance: dict,
        ) -> str:
            xs = [int(round(x)) for x, _ in polygon]
            ys = [int(round(y)) for _, y in polygon]
            geometry = RegionGeometry(
                bbox=BBox(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)),
                polygon=tuple((int(round(x)), int(round(y))) for x, y in polygon),
            )
            region = editing.create_region(
                page_id,
                geometry,
                reading_order=reading_order,
                origin=RegionOrigin.MACHINE,
            )
            return region.region_id

        handlers = build_production_handlers(
            registry=provider_runtime.registry,
            regions=regions,
            region_writer=RegionStepWriter(conn, regions),
            artifacts=ArtifactStepWriter(conn, storage),
            images=_ManagedPageImageSource(repository, storage, regions),
            geometry=_RegionGeometrySource(regions),
            retry_policy=provider_runtime.retry_policy,
            heavy_runner=provider_runtime.heavy_runner,
            route_policy=provider_runtime.route_policy,
            source_styles=source_styles,
            terms=TermExtractionService(),
            render_service=render_service,
            detector=detector,
            region_creator=_create_detected_region,
        )
        # TASK-040 AC ①: wire the TASK-039 Clean-availability probe into the
        # production planner. The probe reuses the same read-only page
        # artifact locator the render/reader paths already use — a page is
        # clean-available iff its current Clean revision exists; no second
        # Clean judgement is invented here.
        from ports.repositories.artifacts import ArtifactType

        clean_locator = SqlitePageArtifactLocator(conn)

        def clean_probe(page_id: str) -> bool:
            return (
                clean_locator.locate_current(page_id, ArtifactType.CLEAN)
                is not None
            )

        # TASK-050 AC ①: seed the pipeline's frozen snapshots from the
        # persisted settings storage. All-empty output decodes to ``None``
        # injections, so an unconfigured install keeps the pre-TASK-050
        # bootstrap byte-for-byte; a configured one is re-projected into
        # the same row the snapshots are read from (idempotent, no second
        # settings parse).
        defaults = _load_pipeline_defaults(conn)
        pipeline = build_production_pipeline(
            conn,
            handlers=handlers,
            clean_probe=clean_probe,
            settings=defaults["settings"] or None,
            provider_bindings=defaults["provider_bindings"] or None,
            constraint_snapshot_ref=defaults["constraint_snapshot_ref"],
            context_policy=defaults["context_policy"] or None,
        )
        # TASK-048 AC ③: a run left RUNNING by a previous process (crash,
        # kill) must never look active forever — startup reaps those rows to
        # INTERRUPTED before any ViewModel can observe them.
        pipeline.recover_running_runs()
        # TASK-050 AC ②: the application-layer defaults channel over the
        # same storage row. The save bridge reuses the infrastructure
        # snapshot provider's own persistence (no second writer); the
        # known-step set comes from the handler table itself, so the
        # write face can never accept a step the pipeline would not run.
        from application.settings.pipeline_defaults import (
            PipelineDefaults,
            PipelineDefaultsService,
        )
        from infrastructure.sqlite.pipeline import SqliteSnapshotProvider

        pipeline_defaults = PipelineDefaultsService(
            load=lambda: PipelineDefaults(**_load_pipeline_defaults(conn)),
            save=lambda **kwargs: SqliteSnapshotProvider(conn, **kwargs),
            known_steps=frozenset(handlers),  # build_production_handlers returns the step table already
        )

        # TASK-038 AC ①/③: the reader ViewModel over the same data root —
        # progress and export history live next to the library database, and
        # the tile factory is Python-only (QML never touches files/models).
        # Tiles are a rebuildable cache under the managed root; the byte
        # budget is the TASK-020 R-002 memory ledger in production.
        data_root = Path(db_path).parent
        diagnostics_root = data_root / "diagnostics"
        diagnostics = DiagnosticsService(
            _ProductionDiagnosticsSnapshot(
                database=Path(db_path),
                data_root=data_root,
                managed_root=Path(managed_root),
                diagnostics_root=diagnostics_root,
                schema=latest_known,
                configured=bool(
                    defaults["settings"]
                    or defaults["provider_bindings"]
                    or defaults["constraint_snapshot_ref"]
                    or defaults["context_policy"]
                ),
            ),
            _BoundedDiagnosticsSink(BoundedLogStore(diagnostics_root)),
            BoundedErrorLog(),
        )
        # T3.1.1 (D03 §29, D03 §31, AC-READ-002, AC-EXPORT-002):
        # One-time legacy JSON import into SQLite; SQLite is now the sole
        # write source of truth, legacy JSON files are preserved read-only.
        import_legacy_reading_progress(conn, data_root / "reading_progress.json")
        import_legacy_export_history(conn, data_root / "export_history.json")

        reading = ReadingService(SqliteReadingProgressStore(conn))
        export_service = ExportService(SqliteExportHistoryStore(conn))

        def tile_factory(path: str) -> TiledPageRasterizer:
            return TiledPageRasterizer(
                path,
                cache_dir=Path(managed_root) / "cache" / "webtoon-tiles",
                tile_height=4000,
                # overlap=0 (TASK-046): after TASK-045 F-4 crops the decode
                # window to the content band, an overlap contributes nothing
                # to the stored pixels — it only pushed every tile after the
                # first behind the streaming cursor, forcing a per-tile
                # rewind (O(tiles^2) per sweep). 0 makes the full-page sweep
                # one sequential scan; pixels are byte-identical (AC 1).
                overlap=0,
                prefetch=1,
                cache=TileCache(max_bytes=512 * 1024 * 1024),
            )

        page_catalog = _ManagedPageCatalog(
            repository, storage, SqlitePageArtifactLocator(conn)
        )
        reader_catalog = _ManagedReaderCatalog(
            repository, storage, SqlitePageArtifactLocator(conn)
        )

        return CoreServices(
            conn=conn,
            repository=repository,
            storage=storage,
            importer=importer,
            document_importer=document_importer,
            trash=trash,
            reading=reading,
            export_service=export_service,
            diagnostics=diagnostics,
            library=library,
            pipeline=pipeline,
            pipeline_defaults=pipeline_defaults,
            editing=editing,
            render=render_service,
            providers=provider_runtime,
            page_catalog=page_catalog,
            reader_catalog=reader_catalog,
            credential_store=credential_store,
            transport=transport,
            data_root=data_root,
            tile_factory=tile_factory,
        )
    except Exception:
        conn.close()
        raise
