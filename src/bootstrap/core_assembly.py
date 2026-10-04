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

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import sqlite3
import sys
from typing import Any

from application.editing.service import RegionEditingService, effective_sfx_policy
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
from domain.regions.entities import (
    BBox,
    RegionGeometry,
    RegionOrigin,
    RegionType,
    SfxPolicy,
)
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
from infrastructure.providers.detection_manga import (
    MANGA_WEIGHTS_DIRNAME,
    MangaDetectionProvider,
)
from infrastructure.providers.detection_sfx import (
    SFX_CONF_THRESHOLD,
    SFX_LABEL_PREFIX,
    SFX_WEIGHTS_FILENAME,
    MangaSfxParallelDetectionProvider,
    SfxDetectionProvider,
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
    #: M2-PROD-DETECT-3: the detection adapter the pipeline ``detect`` step
    #: uses (manga/doctr backend selection + weights resolution, or the mock
    #: provider behind ``mock_local_providers``), exposed so the frozen
    #: command surface's ``core.detect`` resolves the SAME provider instance
    #: instead of building a second one. ``None`` keeps every existing
    #: construction valid and makes ``core.detect`` fail closed with the
    #: typed PROVIDER_NOT_CONFIGURED (same capability-gap slot as the
    #: pipeline step). Provenance object only -- core_service never writes
    #: Regions through it.
    detector: object = None


def _resolve_detector_weights_path(
    override: str | None,
    weights_name: str,
    db_path: Path,
    *,
    env_name: str = "NEWMANGA_DETECTOR_WEIGHTS",
) -> Path:
    """M2-PROD-DETECT-2 (proxy ruling 4, reversible): detector weights lookup.

    Order: env override (the caller names the env — the manga/doctr backends
    keep the released ``NEWMANGA_DETECTOR_WEIGHTS``, the SFX detector passes
    ``NEWMANGA_SFX_WEIGHTS`` so the frozen diagnostic points operators at the
    right override, DSH r1 R9) > data root (existence probe) > frozen
    in-bundle copy (existence probe, PyInstaller ``sys.frozen`` onedir only)
    > the default data-root path.

    Semantics per form (DSH r1 R5/R6 review-fix — ONE failure shape for both
    backends, never an assembly-time crash):

    - **override** (any form): used verbatim, no existence probe — the
      released override contract (M2-PROD-DETECT-1, DSH r1 R7: an *empty*
      value falls through, a non-empty value is taken as-is) and existing
      tests pin the wired provider to the exact override path.
    - **non-frozen** (dev venv / source form): the probes only select paths
      the released lookup would already have chosen, so the result is
      byte-identical to the released behavior — with nothing found anywhere,
      the default data-root path is returned and the lazy provider fails
      closed with the typed ``PROVIDER_NOT_CONFIGURED`` at detect time. No
      bundle probing, no warning output, no error.
    - **frozen** (packaged onedir): the in-bundle copy
      (``Path(sys.executable).parent/models/detector/<name>``) is probed.
      When neither the data root nor the bundle carries the weights the
      lookup writes ONE diagnostic line to stderr (naming the backend's
      weights name and every probed candidate) and returns the default
      data-root path — assembly still succeeds and the lazy provider fails
      closed ``PROVIDER_NOT_CONFIGURED`` at detect time, exactly like the
      doctr backend (identical semantics, R6 fork dissolved). An
      assembly-time crash would take the whole app down (bookshelf, reader,
      everything) for a weights-tree gap (AV quarantine, half-finished
      install, a ``-SkipWeights`` debug artifact) — that blast radius is
      M2-AC3's "assemble, never crash; fail closed at the step" discipline,
      so the packaged-bundle gap degrades to a detect-time typed failure
      with the stderr line pointing operators at the placement options.

    The probes are existence-level only (directory/file ``exists()``); the
    three-file SHA-256 pins are enforced by the provider's own loader
    (``detection_manga`` — imported constants, never duplicated here).
    """
    data_root_candidate = (
        Path(db_path).resolve().parent / "models" / "detector" / weights_name
    )
    if override:
        return Path(override)
    if data_root_candidate.exists():
        return data_root_candidate
    bundle_candidate = (
        Path(sys.executable).resolve().parent / "models" / "detector" / weights_name
    )
    if getattr(sys, "frozen", False):
        if bundle_candidate.exists():
            return bundle_candidate
        probed = [str(data_root_candidate), str(bundle_candidate)]
        # N1 fix (DSH r2): pre-join the candidates BEFORE interpolation — the
        # previous form relied on implicit adjacent-literal concatenation with
        # a bare `" | ".join(probed)` tail, which parses as
        # `("...none exists:  | ").join(probed)` (the separator became a
        # prefix of the whole first literal) and garbled the stderr line.
        probed_str = " | ".join(probed)
        print(
            "WARNING: detector weights not found (weights name "
            f"{weights_name!r}); probed candidates, none exists: {probed_str}"
            "; the detect step will fail closed with PROVIDER_NOT_CONFIGURED "
            "until the weights are placed on the data root or set via "
            f"{env_name}",
            file=sys.stderr,
        )
    return data_root_candidate


def _detected_region_type(provider_label: str) -> RegionType:
    """M2-SFX-PROD-1: dispatch a detected candidate's label to its RegionType.

    The ``sfx-`` prefix (the standalone SFX provider's anonymous label form)
    maps to ``RegionType.SFX`` so the existing SfxPolicy gate (default SKIP)
    takes over automatically; every other label — the manga backends'
    ``manga-<n>`` blocks, the doctr/unmapped placeholders — keeps the
    historical SPEECH default (zero behavior change for the existing
    providers). Module-level so the dispatch matrix is testable without an
    assembled service.
    """
    return (
        RegionType.SFX
        if provider_label.startswith(SFX_LABEL_PREFIX)
        else RegionType.SPEECH
    )


#: M2-SFX-TRANSLATE-ENTRY: the persisted pipeline-settings section/key the
#: assembly-level SFX policy is read from — the same ``pipeline_defaults``
#: row and ``PipelineDefaultsService.save_settings_section`` bridge the
#: ``ocr.script`` key rides (user ruling 4; default SKIP unchanged).
_SFX_SETTINGS_SECTION = "sfx"
_SFX_POLICY_KEY = "policy"
_SFX_POLICY_VALUES = tuple(policy.value for policy in SfxPolicy)


def _sfx_policy_from_settings(settings: Mapping[str, Any]) -> SfxPolicy:
    """The assembly-level SFX policy selector (M2-SFX-TRANSLATE-ENTRY AC1).

    Reads ``settings["sfx"]["policy"]``. An absent section or key keeps the
    historical domain default SKIP — zero behavior change for an
    unconfigured install; precision-first stands until the user explicitly
    opts in. A present-but-invalid value (unknown word, blank, non-string,
    malformed section) raises :class:`ValueError` so the configuration
    error fails the assembly fast the same way an unsupported
    ``NEWMANGA_SFX_DETECTION`` does — never a silent fallback. Values are
    normalized (strip + lower) before validation, mirroring the env-gate
    precedent. Module-level so the selection matrix is testable without an
    assembled service (the ``_detected_region_type`` pattern).
    """
    section = settings.get(_SFX_SETTINGS_SECTION)
    if section is None:
        return SfxPolicy.SKIP
    if not isinstance(section, Mapping):
        raise ValueError(
            f"invalid settings sfx.policy: "
            f"settings[{_SFX_SETTINGS_SECTION!r}] must be a mapping, got "
            f"{type(section).__name__}"
        )
    raw = section.get(_SFX_POLICY_KEY)
    if raw is None:
        return SfxPolicy.SKIP
    if not isinstance(raw, str):
        raise ValueError(
            f"invalid settings sfx.policy: expected a string, got "
            f"{type(raw).__name__}"
        )
    normalized = raw.strip().lower()
    if normalized not in _SFX_POLICY_VALUES:
        raise ValueError(
            f"unsupported settings sfx.policy {raw!r} "
            f"(use {'|'.join(_SFX_POLICY_VALUES)})"
        )
    return SfxPolicy(normalized)


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
        # The acceptance loop seeds Regions up front, so its pipeline plans
        # the region-level chain and never executes ``detect``; the mock
        # detector exists so a region-less page still fails closed at the
        # detect capability gap instead of a missing handler (DSH r1 F-007).
        # M2-SFX-PROD-1 integration fix (DSH r1 R10): the SFX configuration
        # gates are validated OUTSIDE the mock branch — an unsupported
        # NEWMANGA_SFX_DETECTION or an unparseable NEWMANGA_SFX_CONF_THRESHOLD
        # fails the assembly fast in the mock acceptance form too ("fail-fast
        # on configuration errors, never a silent default"). The mock branch
        # itself still does NOT assemble an sfx provider (registered decision:
        # the deterministic mock already stands in for the whole detect
        # surface); `off` skips the whole sfx assembly and keeps the pre-SFX
        # behavior byte-identical.
        sfx_mode = os.environ.get("NEWMANGA_SFX_DETECTION", "on").strip().lower()
        if sfx_mode not in ("on", "off"):
            raise ValueError(
                f"unsupported NEWMANGA_SFX_DETECTION {sfx_mode!r} "
                "(use on|off)"
            )
        # An unparseable NEWMANGA_SFX_CONF_THRESHOLD fails the assembly the
        # same way an unsupported backend env does; the (0, 1] range is the
        # provider's own __post_init__ gate.
        sfx_conf_env = os.environ.get("NEWMANGA_SFX_CONF_THRESHOLD")
        sfx_conf = float(sfx_conf_env) if sfx_conf_env else SFX_CONF_THRESHOLD
        # M2-SFX-TRANSLATE-ENTRY: the sfx_policy applied at region creation
        # is a persisted pipeline-settings key — ``settings["sfx"]["policy"]``
        # on the same ``pipeline_defaults`` row the ``ocr.script`` key rides
        # (written through ``PipelineDefaultsService.save_settings_section``),
        # NOT an env. Read at assembly time, OUTSIDE the mock branch (the
        # DSH r1 R10 placement rule): an illegal value fails the assembly
        # fast here, exactly like the env gates above. Re-assemble
        # semantics: a settings change takes effect on the NEXT assembly —
        # the pipeline-defaults row is the single source of truth, no live
        # reload. The default (absent key) is SKIP: zero behavior change.
        sfx_policy_cfg = _sfx_policy_from_settings(
            _load_pipeline_defaults(conn)["settings"]
        )
        detector: object
        if mock_local_providers:
            from infrastructure.providers.mock_local import (
                MockLocalDetectionProvider,
                register_mock_local_providers,
            )

            register_mock_local_providers(provider_runtime.registry)
            detector = MockLocalDetectionProvider()
        else:
            # M2-PROD-DETECT-1: the production detector backend is selectable
            # via NEWMANGA_DETECTOR_BACKEND — "manga" (default; the C4/C1
            # backed ogkalu RT-DETR-v2 snapshot, proxy ruling recorded in
            # doc/tasks/M2-PROD-DETECT-1.md, reversible) or "doctr" (the
            # T1.1.1 docTR fast_base path, byte-identical to its released
            # behaviour). Both adapters are lazy and strictly offline:
            # weights must exist locally — resolved per backend through the
            # shared lookup in ``_resolve_detector_weights_path``
            # (M2-PROD-DETECT-2, proxy ruling 4): env override
            # (NEWMANGA_DETECTOR_WEIGHTS; directory for manga, file for
            # doctr) > the data root's models/detector/<name> (existence
            # probe) >, in the frozen onedir form only, the copy bundled
            # inside the release (manga ships in-bundle; doctr's weights
            # intentionally do NOT — switching to doctr in the release form
            # keeps the detect-time NOT_CONFIGURED with the pointer to
            # place them on the data root, proxy ruling 3) > the default
            # data-root path. Failure semantics are UNIFORM for both
            # backends (DSH r1 R5/R6 review-fix): nothing found anywhere ->
            # one stderr diagnostic line in the frozen form (listing every
            # probed candidate) and the released detect-time typed
            # PROVIDER_NOT_CONFIGURED — never an assembly-time crash. The
            # non-frozen form keeps the released fail-closed at run time
            # with zero extra output. No download, no silent fallback.
            # Boundary note (DSH r1 R7): an *empty* NEWMANGA_DETECTOR_WEIGHTS
            # falls back to the default path below ("override if override
            # else default"), whereas the pre-Task doctr assembly
            # (``os.environ.get(..., str(default))``) yielded Path("") (the
            # cwd) for the same empty string. Both variants fail closed at
            # detect; the doctr branch now follows this fallback semantics —
            # the only env-boundary difference from the released behaviour.
            backend = os.environ.get("NEWMANGA_DETECTOR_BACKEND", "manga").strip().lower()
            detector_device_env = os.environ.get("NEWMANGA_DETECTOR_DEVICE", "cpu")
            detector_weights_override = os.environ.get("NEWMANGA_DETECTOR_WEIGHTS")
            # M2-PROD-DETECT-2 (proxy ruling 4): the lookup below is shared
            # verbatim by both backends — env override > data root (probed) >
            # frozen in-bundle copy (probed, `sys.frozen` onedir only) > the
            # default data-root path. The in-bundle layer is what makes the
            # RELEASE-form detect chain work (weights ship inside the
            # core-sidecar onedir via the whole-directory Tauri resource);
            # the non-frozen (source venv) form resolves exactly as before.
            if backend == "manga":
                detector_weights = _resolve_detector_weights_path(
                    detector_weights_override, MANGA_WEIGHTS_DIRNAME, db_path
                )
                detector = MangaDetectionProvider(
                    weights_dir=detector_weights,
                    device=detector_device_env,
                )
            elif backend == "doctr":
                # Same lookup, same failure shape (DSH r1 R6 review-fix): the
                # doctr weights intentionally ship OUT of the bundle (ruling
                # 3), but a frozen miss degrades to the SAME stderr warning +
                # detect-time NOT_CONFIGURED as manga — no assembly-time
                # crash for either backend.
                detector_weights = _resolve_detector_weights_path(
                    detector_weights_override, DOCTR_WEIGHTS_FILENAME, db_path
                )
                detector = DoctrDetectionProvider(
                    weights_path=detector_weights,
                    device=detector_device_env,
                )
            else:
                raise ValueError(
                    f"unsupported NEWMANGA_DETECTOR_BACKEND {backend!r} "
                    "(use manga|doctr)"
                )
            # M2-SFX-PROD-1: the standalone SFX detector (chiqui7 ONNX over
            # the onnxruntime lightweight stack) runs BESIDE the selected
            # primary. Default ON (user ruling 3: route A, release-form
            # out-of-the-box); the NEWMANGA_SFX_DETECTION / _CONF_THRESHOLD
            # env gates are validated above, OUTSIDE this branch (DSH r1 R10).
            # The mock acceptance branch above deliberately does NOT get an
            # sfx provider (registered decision): the deterministic mock
            # already stands in for the whole detect surface, so the
            # acceptance loop's seeded-regions flow stays untouched. Weights
            # resolution reuses the shared DETECT-2 lookup verbatim (file
            # semantics, like doctr): env override (NEWMANGA_SFX_WEIGHTS,
            # also named by the frozen diagnostic — DSH r1 R9) > data root
            # (probed) > frozen in-bundle copy (probed, sys.frozen onedir
            # only) > the default data-root path; the lazy provider fails
            # closed typed at detect time when nothing exists.
            if sfx_mode == "on":
                detector = MangaSfxParallelDetectionProvider(
                    primary=detector,
                    sfx=SfxDetectionProvider(
                        weights_path=_resolve_detector_weights_path(
                            os.environ.get("NEWMANGA_SFX_WEIGHTS"),
                            SFX_WEIGHTS_FILENAME,
                            db_path,
                            env_name="NEWMANGA_SFX_WEIGHTS",
                        ),
                        conf_threshold=sfx_conf,
                    ),
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
            # M2-SFX-PROD-1: the candidate's anonymous provider_label; the
            # ``sfx-`` prefix dispatches RegionType.SFX so the existing
            # SfxPolicy gate (default SKIP) takes over automatically. Every
            # other label (manga-<n>, unmapped-<n>, ...) keeps the historical
            # SPEECH default — zero behavior change for the existing backends.
            provider_label: str = "",
        ) -> str:
            xs = [int(round(x)) for x, _ in polygon]
            ys = [int(round(y)) for _, y in polygon]
            geometry = RegionGeometry(
                bbox=BBox(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)),
                polygon=tuple((int(round(x)), int(round(y))) for x, y in polygon),
            )
            region_type = _detected_region_type(provider_label)
            region = editing.create_region(
                page_id,
                geometry,
                region_type=region_type,
                # M2-SFX-TRANSLATE-ENTRY: only SFX-typed candidates carry the
                # configured policy (the translation gate consumes it); every
                # other region type keeps the SKIP default regardless of
                # configuration — the policy can never leak onto non-SFX
                # regions. Shared EV-8 helper (r1 P4-1): same rule the retype
                # path applies, one definition for both write paths.
                sfx_policy=effective_sfx_policy(region_type, sfx_policy_cfg),
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
            # M2-PROD-DETECT-3: expose the pipeline's own detector so
            # core_service's core.detect resolves the same instance.
            detector=detector,
        )
    except Exception:
        conn.close()
        raise
