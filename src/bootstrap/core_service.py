"""Production Core Service (M2-IPC1).

The host spawns this module -- ``python -m bootstrap.core_service`` -- as the
production Core sidecar process. It assembles the production Core services
(migrations, repositories, managed storage, startup recover_running_runs),
then enters a stdio request loop serving typed commands over JSON-lines.

Transport & Envelope (Contract 1.1 §3, §8, §12; Seam 冻结七条):
  Request:
    {"protocol": "new-manga.core", "version": {"major": 1, "minor": 3+},
     "request_id": "<id>", "command": "<cmd>", "payload": {...}}
  Response:
    {"protocol": "new-manga.core", "version": {"major": 1, "minor": 3+},
     "request_id": "<id>", "result": {...} | null, "error": ErrorEnvelope | null}

Allowed production commands (M2-IPC1 + M2-PROD-DETECT-3 + M2-SETTINGS-IPC-CHANNEL
  + M2-REGION-RETYPE-CORE):
  - core.ping: {} -> {"status": "ready", "protocol_version": {"major": 1, "minor": 3+}, "capabilities": ["library.list_books"]}
  - ListBooks: {} -> BookSummary[]
  - core.shutdown: {} -> {"status": "stopped"} (then exit 0)
  - core.detect: {"page": "<base64 PNG/JPEG>", "width": <int>, "height": <int>}
      -> {"candidates": [{"provider_label", "polygon", "reading_order",
        "confidence", "coordinate_space"}...], "elapsed_ms": <int>}
    (M2-PROD-DETECT-3, protocol minor bump 1.0 -> 1.1: a backwards-compatible
    widening per the M2-FIX-LISTBOOKS contract rev 1.2 §5 precedent -- the
    three pre-existing commands keep their command semantics (payloads,
    results, error codes) unchanged; the envelope protocol minor moves 0 -> 1
    with the bump. The handler resolves
    the SAME detector instance the pipeline ``detect`` step uses (assembly
    wired; never a bypass) and passes the provider output straight through:
    anonymous labels only, no business IDs are invented. A page that fails to
    decode, whose declared width/height do not match the decoded pixels, or
    whose payload exceeds 32 MiB fails with the typed INVALID_REQUEST
    envelope; a detector without usable weights fails with the provider's
    own typed error codes (PROVIDER_NOT_CONFIGURED / PROVIDER_DEPENDENCY_MISSING /
    PROVIDER_FAILED / ...). Verification/tooling surface only -- the product
    UI detect path remains the pipeline (apps/** registers nothing new).
  - settings.get: {} | {"section": "<name>"}
      -> {"settings": {...}} | {"settings": {"<name>": {...} | null}}
    (M2-SETTINGS-IPC-CHANNEL, protocol minor bump 1.1 -> 2: same
    backwards-compatible widening precedent -- every pre-existing command
    keeps its payload/result/error codes; only the envelope version moves.
    Full form returns the ``PipelineDefaults.settings`` projection; the
    by-section form returns that one section, JSON ``null`` when unset --
    the frozen None channel stays distinguishable from an empty object.
    Contract: M2-C1 rev 1.3 §5.3.)
  - settings.update_section: {"section": "<name>", "values": {...}}
      -> {"settings": {...}}  (the full updated projection)
    (M2-SETTINGS-IPC-CHANNEL. Upsert via ``PipelineDefaultsService.
    save_settings_section`` -- the same channel/row as the ``ocr.script``
    key. Write-side validation is typed fail-closed BEFORE any persistence
    (M2-SFX-ENTRY r1 R4 lesson: a write path without validation lets an
    illegal value reach the store and become an unrecoverable startup
    block at the next assembly): ``section`` must be a non-empty string,
    ``values`` a JSON object, and ``settings["sfx"]["policy"]`` -- the
    first validation instance -- must be one of skip/translate/manual.
    Everything else passes through; a failure never reaches the store.
    Contract: M2-C1 rev 1.3 §5.3.)
  - set_region_type: {"region_id": "<id>", "new_region_type": <RegionType>,
      "expected_revision"?: <int>} -> the post-retype effective state
      {"region_id", "revision_no", "region_type", "sfx_policy"}
    (M2-REGION-RETYPE-CORE, protocol minor bump 2 -> 3: the same
    backwards-compatible widening precedent -- every pre-existing command
    keeps its payload/result/error codes. The retype is ONE new revision
    through the existing commit seam, origin always user, review_state
    UNREVIEWED; the snapshot delta is region_type + sfx_policy ONLY. EV-8
    (RULED): retype-to-sfx re-snapshots sfx_policy from the GLOBAL
    sfx.policy configuration at retype time; every non-sfx target is forced
    SKIP. Error semantics reuse the existing typed literals only:
    INVALID_REQUEST (validation) / INPUT_REVISION_CHANGED (conflict, the
    explicit optimistic guard C4) / TARGET_NOT_FOUND (not_found) / UNKNOWN
    (internal); wire codes are SCREAMING_SNAKE_CASE. Contract: M2-C1
    rev 1.4 §5.4.)
  - list_regions: {"page_id": "<id>"} -> {"regions": RegionListSummary[],
    "page_size": {"width", "height"} | null}
    (M2-REGION-RETYPE-CORE; read face widened ADDITIVELY by
    M2-WORKBENCH-REACT-1, contract rev 1.5 -- optional per-row normalized
    "geometry" + optional wrapper "page_size" projection, zero new commands,
    protocol minor stays 3. The five-field minimal read DTO -- region_id /
    region_type / sfx_policy / origin / revision_no -- rides verbatim in
    reading_order ascending, from the revision the current pointer targets;
    no TEXT or ANNOTATION semantics (geometry rides since rev 1.5 as the
    display-geometry channel, the normalized reverse of the stored pixels).
    A page with no rows (unknown page_id included) reads as
    {"regions": [], "page_size": null}, NOT an error -- the existing
    list_regions semantics (contract §5.4 footnote a). Errors:
    INVALID_REQUEST (payload) / UNKNOWN (internal) only.)
"""

from __future__ import annotations

import base64
from dataclasses import asdict, dataclass
import io
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
from typing import Any, Callable, TextIO

from application.editing.errors import (
    GuardStatus,
    RegionNotFound,
    RegionRevisionChanged,
    RegionRevisionNotFound,
)
from application.importing.images.ports import DecodedImage
from application.settings.errors import BindingValidationError
from application.translation.color.service import SourceStyleService
from bootstrap.core_assembly import (
    CoreServices,
    assemble_core_services,
    default_data_root,
)
from domain.regions.entities import RegionType, SfxPolicy
from infrastructure.importing import SUPPORTED_IMAGE_SUFFIXES
from infrastructure.rendering.pillow_rendering import (
    PillowFontCatalog,
    PillowImageCompositor,
    PillowTextLayoutEngine,
    decode_nmfr_frame,
)
from infrastructure.resource_channel.catalog_store import (
    PreviewOrigin,
    ResourceCatalogStore,
    initialize_namespace,
)
from infrastructure.resource_channel.handle_resolver import (
    acquire_shared_lease,
    resolve_namespace_identity,
    try_acquire_exclusive_lease,
)
from infrastructure.resource_channel.render_preview import (
    ORIGINAL_REVISION,
    RenderPreviewPublisher,
)
from ports.detection.ports import DetectionRequest
from ports.providers.errors import ProviderError, ProviderNotConfigured

PROTOCOL_NAME = "new-manga.core"
PROTOCOL_MAJOR = 1
# M2-PROD-DETECT-3: 0 -> 1 (minor bump, core.detect command added; backwards
# compatible widening, see the module docstring).
# M2-SETTINGS-IPC-CHANNEL: 1 -> 2 (minor bump, settings.get /
# settings.update_section commands added; same backwards-compatible widening
# precedent -- pre-existing command semantics unchanged).
# M2-REGION-RETYPE-CORE: 2 -> 3 (minor bump, set_region_type / list_regions
# commands added; same backwards-compatible widening precedent -- pre-existing
# command semantics unchanged. Contract: M2-C1 rev 1.4 §5.4).
# M2-WORKBENCH-REACT-1: NO bump (stays 3). Contract rev 1.5 widens the
# ListRegions read face ADDITIVELY -- an optional per-row "geometry" field and
# an optional "page_size" on the result wrapper -- with zero new commands and
# zero new error semantics. Per §3.2 same-major receivers ignore unknown
# optional fields, so this is compatible widening without a minor bump; the
# module's bump annotations all correspond to "commands added", which this
# revision deliberately has none of.
# M2-RC4-DOMAIN-COMMANDS: 3 -> 4 (three domain commands list_region_revisions
# / restore_region_revision / rerender_page added).
# M2-PAGE-RESOURCE-RESOLVE-1: 4 -> 5 (minor bump, resolve_page_resource
# command added; same backwards-compatible widening precedent -- pre-existing
# command semantics unchanged. Contract: M2-C1 rev 1.7 §5).
# M2-PAGE-NAV-PROJECTION-1: 5 -> 6 (minor bump, list_chapters /
# list_chapter_pages commands added; same backwards-compatible widening
# precedent -- pre-existing command semantics unchanged. Contract: M2-C1
# rev 1.8 §5).
PROTOCOL_MINOR = 6

# Typed error codes per Contract 1.1 §3, §8
E_PROTOCOL_VERSION_UNSUPPORTED = "PROTOCOL_VERSION_UNSUPPORTED"
E_UNKNOWN_COMMAND = "UNKNOWN_COMMAND"
E_LIST_BOOKS_FAILED = "LIST_BOOKS_FAILED"
E_UNKNOWN = "UNKNOWN"
# M2-PROD-DETECT-3: malformed core.detect payload (bad base64, width/height
# missing or mismatched with the decoded pixels, oversized payload). Same
# literal the dispatch loop already uses for a non-object request.
# M2-SETTINGS-IPC-CHANNEL: the SAME existing literal covers the settings
# request validation failures (bad section/values shapes, illegal sfx.policy)
# -- no new error code is invented (contract rev 1.3 §5.3, §8 existing enum).
E_INVALID_REQUEST = "INVALID_REQUEST"
# M2-REGION-RETYPE-CORE: the retype wire reuses the EXISTING typed error
# literals only (contract rev 1.4 §5.4 error mapping table -- zero new error
# semantics). INPUT_REVISION_CHANGED is the code family the guarded machine
# writes already surface (application/editing/errors.py GuardStatus + the
# pipeline's candidate path); TARGET_NOT_FOUND is the §8 table's existing
# not_found row. Footnote c: wire codes are SCREAMING_SNAKE_CASE literals --
# the lowercase GuardStatus enum VALUES ("input_revision_changed") are
# internal guard states and never ride the wire.
E_INPUT_REVISION_CHANGED = "INPUT_REVISION_CHANGED"
E_TARGET_NOT_FOUND = "TARGET_NOT_FOUND"
# M2-PAGE-RESOURCE-RESOLVE-1: dedicated not_found literal for the page
# display image face. TARGET_NOT_FOUND stays the region-face row; this
# command resolves a PAGE's managed original, and its contract row (M2-C1
# rev 1.7 §5) needs to distinguish "page/its original is not available"
# from the region not-found family without overloading the message text.
E_PAGE_NOT_FOUND = "PAGE_NOT_FOUND"

#: M2-PAGE-RESOURCE-RESOLVE-1: managed originals are published byte-for-byte
#: (no transcode) into ``pages/`` under the derived root. The gate reuses the
#: IMPORT/DECODE face's own supported set (``SUPPORTED_IMAGE_SUFFIXES``,
#: derived from the Qt decoder's _MIME_TYPES; DSH r1 PR-06) so the publish
#: gate and the import face share one authority -- a legally imported page
#: (e.g. .tif) can never fail closed as an unsupported format here, while
#: anything the decoder would have rejected still does.
_ORIGINAL_SUFFIXES = SUPPORTED_IMAGE_SUFFIXES

#: M2-SETTINGS-IPC-CHANNEL: the legal ``settings["sfx"]["policy"]`` values
#: (contract rev 1.3 §5.3 write-side validation, first instance). The
#: semantics fact source is M2-SFX-TRANSLATE-ENTRY (default SKIP, re-assemble
#: per region); the value set is the domain enum itself so the wire gate can
#: never drift from what the assembly-time reader accepts.
_SFX_POLICY_VALUES = frozenset(policy.value for policy in SfxPolicy)

#: M2-REGION-RETYPE-CORE: the ``RegionType`` six-value closed set (contract
#: rev 1.4 §5.4 -- zero new enum values; "ignore" is a processing action /
#: filter state, NOT a RegionType). The value set is the domain enum itself
#: so the wire gate can never drift from what the entity layer accepts.
_REGION_TYPE_VALUES = frozenset(
    region_type.value for region_type in RegionType
)

#: M2-PROD-DETECT-3: upper bound for one core.detect page, enforced on the
#: base64-decoded FILE bytes; a separate pixel-count cap (below) bounds the
#: decoded RGB buffer. The base64-text guard below is derived from it (4
#: base64 chars per 3 bytes) so an oversized request is rejected before any
#: decoding work. One manga page as PNG is a few MiB; 32 MiB leaves generous
#: headroom while keeping a hostile payload from pinning the sidecar.
MAX_DETECT_PAGE_BYTES = 32 * 1024 * 1024
_MAX_DETECT_PAGE_B64_CHARS = ((MAX_DETECT_PAGE_BYTES + 2) // 3) * 4

#: M2-PROD-DETECT-3 integration (DSH r1 R10): the byte cap above bounds the
#: encoded file only -- a highly compressed PNG can decode to a far larger
#: RGB buffer. The decoded pixel count is capped at the 32 MiB RGB24
#: equivalent (file cap / 3) BEFORE any convert/tobytes allocation; this is
#: deliberately tighter than Pillow's DecompressionBomb default (89.5 M px)
#: to stay aligned with the 32 MiB primary limit. A real 900x1300 page is
#: ~1.2 M px, roughly 9x headroom.
MAX_DETECT_PIXELS = MAX_DETECT_PAGE_BYTES // 3

#: M2-PROD-DETECT-3 integration (DSH r1 R11): the documented PNG/JPEG page
#: surface is enforced fail-closed -- Pillow also decodes BMP/TIFF/WEBP/multi-
#: frame GIF, and those must not ride this face.
_DETECT_PAGE_FORMATS = frozenset({"PNG", "JPEG"})

# M2-PROD-DETECT-3 integration (DSH r1 R1): provider error TEXT never rides
# the IPC line -- real provider messages embed local absolute paths (weights
# directories), which Contract §8 forbids on the wire. The envelope carries
# the stable error_code plus one fixed safe phrase; the full original detail
# goes to stderr only. INVALID_INPUT is the one pass-through (parameter-level
# byte-count/frame-size text, no paths by construction -- pinned by tests).
_PROVIDER_SAFE_MESSAGES: dict[str, str] = {
    "PROVIDER_NOT_CONFIGURED": (
        "detector is not configured; install weights or set "
        "NEWMANGA_DETECTOR_WEIGHTS (see stderr for details)"
    ),
    "PROVIDER_DEPENDENCY_MISSING": (
        "a detector dependency is missing (see stderr for details)"
    ),
    "PROVIDER_FAILED": "detector failed (see stderr for details)",
    "PROVIDER_UNAVAILABLE": "detector is unavailable (see stderr for details)",
}
_PROVIDER_SAFE_DEFAULT = "detector failed (see stderr for details)"

# M2-PROD-DETECT-3 integration (DSH r1 R14, Proposal-level annotation): §8
# category for provider errors. The provider's own input gate polices OUR
# request shape -> validation; every other provider failure is internal.
# Final taxonomy alignment stays registered in the contract Revision history
# (same-source item as M2-IPC1 r2 P3-4).
_PROVIDER_ERROR_CATEGORY: dict[str, str] = {"INVALID_INPUT": "validation"}


class DetectRequestError(ValueError):
    """A core.detect payload violates the request contract (INVALID_REQUEST)."""


class SettingsRequestError(ValueError):
    """A settings.get/update_section payload violates the request contract
    (INVALID_REQUEST; M2-SETTINGS-IPC-CHANNEL, contract rev 1.3 §5.3)."""


class RegionRequestError(ValueError):
    """A set_region_type/list_regions payload violates the request contract
    (INVALID_REQUEST; M2-REGION-RETYPE-CORE, contract rev 1.4 §5.4 -- the
    §5.3 write-side fail-closed discipline applies to these commands too)."""


class RegionConflictError(ValueError):
    """An explicit optimistic expectation failed on set_region_type
    (INPUT_REVISION_CHANGED, contract rev 1.4 §5.4 C4 -- the same code
    family the guarded machine writes surface; C4: zero write on
    rejection)."""


class RegionLookupError(ValueError):
    """A set_region_type target does not exist or is soft-deleted (C7) --
    mapped to the existing TARGET_NOT_FOUND/not_found row; carries only the
    region_id so no raw exception text rides the wire (§8)."""

    def __init__(self, region_id: str) -> None:
        super().__init__("region not found")
        self.region_id = region_id


class RenderCommandError(ValueError):
    def __init__(self, code: str, category: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.category = category



class _PassthroughImageDecoder:
    def decode(self, payload: bytes) -> DecodedImage:
        del payload
        # mime_type keeps the stub's original "rgb" semantics under the image
        # type, matching the frozen DecodedImage contract (no format= field).
        return DecodedImage(width=1, height=1, mime_type="image/rgb")


class _StubStyleAnalyzer:
    def analyze_pixel_styles(self, image: Any) -> list[Any]:
        del image
        return []


def assemble_production_core(data_root: Path | None = None) -> CoreServices:
    """Assemble production Core services on the given or default data root.

    Runs database migrations, initializes repositories and managed copy layout,
    and runs startup ``recover_running_runs()``. Uses lightweight headless adapters
    so the service starts reliably in headless sidecar environments without
    requiring a display server.
    """
    if data_root is None:
        data_root = default_data_root()

    db_path = data_root / "library.db"
    managed_root = data_root / "managed"

    # Assemble Qt-free Core services with real headless rendering adapters.
    catalog = PillowFontCatalog()
    assembled: dict[str, CoreServices] = {}

    def read_original_page(page_id: str) -> bytes | None:
        # Normal imports write their immutable source to Page.managed_original_ref
        # (Managed Copy), without necessarily creating an ORIGINAL media artifact.
        # Resolve it at use time through the assembled Core repositories/storage;
        # no path or new business identity is exposed on the wire.
        current = assembled.get("core")
        if current is None:
            return None
        page = current.repository.get_page(page_id)
        if page is None or not page.managed_original_ref:
            return None
        managed_root = current.storage.root.resolve()
        path = Path(current.storage.absolute_path(page.managed_original_ref)).resolve()
        try:
            path.relative_to(managed_root)
        except ValueError as error:
            raise ValueError("managed original escaped the Managed Copy root") from error
        if not path.is_file():
            return None
        return path.read_bytes()

    core = assemble_core_services(
        db_path,
        managed_root,
        image_decoder=_PassthroughImageDecoder(),
        font_catalog=catalog,
        layout_engine=PillowTextLayoutEngine(catalog),
        compositor=PillowImageCompositor(catalog),
        source_styles=SourceStyleService(_StubStyleAnalyzer()),
        content_decoder=decode_nmfr_frame,
        original_page_reader=read_original_page,
    )
    assembled["core"] = core
    return core


def make_error_envelope(
    code: str,
    category: str,
    message: str,
    retryable: bool = False,
    details: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "code": code,
        "category": category,
        "message": message,
        "retryable": retryable,
    }
    if details is not None:
        envelope["details"] = details
    return envelope


@dataclass(frozen=True)
class BookSummaryDto:
    book_id: str
    title: str
    original_title: str
    is_favorite: bool
    is_archived: bool
    # M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN (frozen None channel): None means
    # unknown/missing data (the production COUNT predicate yields no row for
    # this book); a counted value stays an int -- a KNOWN 0 must remain
    # expressible and distinguishable from None after serialization.
    page_count: int | None
    created_at: str
    updated_at: str


class CoreServiceServer:
    """Stdio JSON-lines RPC server for the production Core."""

    def __init__(
        self,
        core: CoreServices,
        *,
        stdin: TextIO | None = None,
        stdout: TextIO | None = None,
        render_previews: RenderPreviewPublisher | None = None,
        producer_root: Path | None = None,
    ) -> None:
        self._core = core
        self._stdin = stdin or sys.stdin
        self._stdout = stdout or sys.stdout
        # M2-DERIVED-GC-2: the canonical data root this Core owns (its
        # producer identity for preview origin registration). None keeps the
        # legacy behaviour -- previews publish catalog-only, never reclaimable.
        self._producer_root = str(producer_root.resolve()) if producer_root else None
        self._render_previews = render_previews

    def handle_ping(self, payload: dict[str, Any]) -> dict[str, Any]:
        del payload
        return {
            "status": "ready",
            "protocol_version": {
                "major": PROTOCOL_MAJOR,
                "minor": PROTOCOL_MINOR,
            },
            "capabilities": ["library.list_books"],
        }

    def handle_list_books(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        del payload
        books = self._core.library.list_books()

        # Query page counts per book from SQLite read-only
        page_counts = self._fetch_page_counts()

        summaries: list[dict[str, Any]] = []
        for book in books:
            dto = BookSummaryDto(
                book_id=book.book_id,
                title=book.title,
                original_title=book.original_title,
                is_favorite=bool(book.is_favorite),
                is_archived=bool(book.is_archived),
                # GROUP BY returns rows only for books with >=1 qualifying
                # page: a SQL miss (no chapters / no qualifying pages) is
                # unknown data -> None, never a plausible-looking 0.
                page_count=page_counts.get(book.book_id),
                created_at=book.created_at,
                updated_at=book.updated_at,
            )
            summaries.append(asdict(dto))
        return summaries

    def _fetch_page_counts(self) -> dict[str, int]:
        """Read-only query calculating valid non-deleted page counts per book."""
        rows = self._core.conn.execute(
            """
            SELECT c.book_id, COUNT(p.page_id) AS cnt
            FROM chapters c
            JOIN pages p ON p.chapter_id = c.chapter_id
            WHERE c.deleted_at IS NULL
              AND p.deleted_at IS NULL
              AND p.source_hash IS NOT NULL
              AND p.managed_original_ref IS NOT NULL
              AND p.width IS NOT NULL
              AND p.height IS NOT NULL
            GROUP BY c.book_id
            """
        ).fetchall()
        return {row["book_id"]: int(row["cnt"]) for row in rows}

    # ------------------------------------------------------------------
    # core.detect (M2-PROD-DETECT-3)
    # ------------------------------------------------------------------

    def handle_detect(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Detect text regions on one page; the provider output passes through.

        The detector is the SAME instance the pipeline ``detect`` step uses --
        the one ``assemble_core_services`` wired into the production handlers
        (manga/doctr backend selection + weights resolution, or the mock
        provider behind ``mock_local_providers``). This handler never builds
        its own provider and never touches the registry directly, so the
        assembly semantics (in-bundle weights fallback, backend env, mock
        mode) are shared verbatim.

        Request validation (typed INVALID_REQUEST, fail-closed before any
        provider is touched):
          - ``page`` must be a base64-encoded PNG/JPEG image (format
            whitelist enforced fail-closed after the header sniff);
          - ``width``/``height`` must be positive ints matching the decoded
            pixel size;
          - the decoded payload must not exceed ``MAX_DETECT_PAGE_BYTES``
            (file bytes) nor ``MAX_DETECT_PIXELS`` (decoded RGB buffer).

        The providers behind ``ports.detection`` consume a RAW pixel buffer
        (rgb24/rgb32, never an encoded file -- their ``_validate_request``
        byte-count gate is the second-line defense and stays untouched), so
        this handler decodes the image (Pillow, a transformers dependency
        already in the frozen closure) into raw RGB bytes. Failure shapes:
          - no detector wired at assembly -> ``PROVIDER_NOT_CONFIGURED`` (the
            same capability-gap slot the pipeline detect step uses);
          - the provider raises -> its typed ``ProviderError.error_code``
            passes through verbatim (e.g. the detect-time
            ``PROVIDER_NOT_CONFIGURED`` of a weights-less install -- ruling 5
            of M2-PROD-DETECT-2).

        The result is a straight passthrough: candidates keep the provider's
        anonymous ``provider_label`` (no business ID is invented), plus the
        result-level ``coordinate_space``; ``elapsed_ms`` is THIS handler's
        detect-only wall-clock (the timer starts after decoding, so it
        includes the provider's first model load) -- probes compare it
        against the provider-internal timing on that same basis.
        """
        page_b64 = payload.get("page")
        if not isinstance(page_b64, str) or not page_b64:
            raise DetectRequestError(
                "core.detect requires 'page': a base64-encoded PNG/JPEG image"
            )
        width = payload.get("width")
        height = payload.get("height")
        for name, value in (("width", width), ("height", height)):
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise DetectRequestError(
                    f"core.detect requires '{name}': a positive int"
                )
        if len(page_b64) > _MAX_DETECT_PAGE_B64_CHARS:
            raise DetectRequestError(
                f"core.detect page exceeds the {MAX_DETECT_PAGE_BYTES} byte limit"
            )
        try:
            encoded = base64.b64decode(page_b64, validate=True)
        except (ValueError, TypeError) as error:
            raise DetectRequestError(
                "core.detect 'page' is not valid base64"
            ) from error
        if len(encoded) > MAX_DETECT_PAGE_BYTES:
            raise DetectRequestError(
                f"core.detect page exceeds the {MAX_DETECT_PAGE_BYTES} byte limit"
            )

        # Pillow is lazy for the same reason the ML stack is: module import
        # (and therefore process startup) stays free of heavy dependencies.
        try:
            from PIL import Image
        except ImportError as error:  # pragma: no cover - closure gap, not a test path
            raise ProviderNotConfigured(
                "no image decoder is available in this build (Pillow missing)",
                stage="core.detect",
            ) from error
        try:
            with Image.open(io.BytesIO(encoded)) as image:
                # R11 (DSH r1): enforce the documented PNG/JPEG surface,
                # fail-closed -- Pillow happily decodes BMP/TIFF/WEBP/GIF
                # too, and those must not ride this face.
                if image.format not in _DETECT_PAGE_FORMATS:
                    raise DetectRequestError(
                        "core.detect 'page' must be a PNG or JPEG image "
                        f"(got {image.format or 'unknown'})"
                    )
                # R10 (DSH r1): the byte cap bounds the encoded file only;
                # cap the DECODED pixel count before any convert/tobytes
                # allocation (32 MiB RGB24 equivalent, see MAX_DETECT_PIXELS).
                if image.width * image.height > MAX_DETECT_PIXELS:
                    raise DetectRequestError(
                        "core.detect page exceeds the pixel limit "
                        f"({image.width}x{image.height} = "
                        f"{image.width * image.height} px > "
                        f"{MAX_DETECT_PIXELS} px)"
                    )
                rgb = image.convert("RGB")
                actual_width, actual_height = rgb.size
                if actual_width != width or actual_height != height:
                    raise DetectRequestError(
                        "core.detect width/height do not match the decoded "
                        f"image ({actual_width}x{actual_height} != "
                        f"{width}x{height})"
                    )
                frame = rgb.tobytes()
        except DetectRequestError:
            raise
        except Exception as error:  # noqa: BLE001 - any decode failure is a bad request
            raise DetectRequestError(
                "core.detect 'page' is not a decodable PNG/JPEG image"
            ) from error

        detector = getattr(self._core, "detector", None)
        if detector is None:
            # Same capability-gap slot as the pipeline detect step
            # (handlers.handle_detect): fail closed at NOT_CONFIGURED, never
            # fabricate output.
            raise ProviderNotConfigured(
                "no detection provider is wired at assembly", stage="core.detect"
            )

        request = DetectionRequest(
            # The protocol command name as the page identifier: DetectionRequest
            # requires one (ports contract), the providers only carry it
            # through into DetectionResult provenance, and no Region row is
            # written on this surface -- so a stable constant beats a per-run
            # value (mock determinism keeps holding).
            page_id="core.detect",
            image_bytes=frame,
            width=width,
            height=height,
        )
        started = time.perf_counter()
        result = detector.detect(request)
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return {
            "candidates": [
                {
                    "provider_label": candidate.provider_label,
                    "polygon": [
                        [float(x), float(y)] for x, y in candidate.polygon
                    ],
                    "reading_order": candidate.reading_order,
                    "confidence": candidate.confidence,
                    "coordinate_space": result.coordinate_space,
                }
                for candidate in result.candidates
            ],
            "elapsed_ms": elapsed_ms,
        }

    # ------------------------------------------------------------------
    # settings.get / settings.update_section (M2-SETTINGS-IPC-CHANNEL)
    # ------------------------------------------------------------------

    def handle_settings_get(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Read the persisted pipeline settings (contract rev 1.3 §5.3).

        Full form (no ``section``): ``{"settings": <projection>}``. The
        by-section form returns that one section; an unset section reads as
        JSON ``null`` -- the frozen None channel (unknown/never written)
        stays distinguishable from a written empty object, mirroring the
        M2-FIX-LISTBOOKS ``page_count`` precedent. Reading never writes.
        """
        section = payload.get("section")
        settings = dict(self._core.pipeline_defaults.read().settings)
        if section is None:
            return {"settings": settings}
        if not isinstance(section, str) or not section.strip():
            raise SettingsRequestError(
                "settings.get 'section' must be a non-empty string when present"
            )
        return {"settings": {section: settings.get(section)}}

    def handle_settings_update_section(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Upsert one settings section (contract rev 1.3 §5.3).

        Validation is WRITE-SIDE and typed fail-closed (M2-SFX-ENTRY r1 R4
        lesson): a value that would fail the assembly-time reader must be
        rejected here, BEFORE any persistence, so an illegal write can never
        become an unrecoverable startup block. Shapes:
          - ``section``: non-empty string (upsert target);
          - ``values``: JSON object (the whole section is replaced);
          - ``settings["sfx"]["policy"]``: the first value-domain gate --
            one of skip/translate/manual (M2-SFX-TRANSLATE-ENTRY; default
            SKIP stays the assembly reader's concern, not rewritten here).
        Every other section/key passes through. The result is the full
        updated projection, so one round trip re-syncs the caller.
        """
        section = payload.get("section")
        values = payload.get("values")
        if not isinstance(section, str) or not section.strip():
            raise SettingsRequestError(
                "settings.update_section requires 'section': a non-empty string"
            )
        if not isinstance(values, dict):
            raise SettingsRequestError(
                "settings.update_section requires 'values': a JSON object"
            )
        if section == "sfx" and "policy" in values:
            policy = values["policy"]
            if not (isinstance(policy, str) and policy in _SFX_POLICY_VALUES):
                raise SettingsRequestError(
                    "settings.update_section sfx.policy must be one of "
                    f"{sorted(_SFX_POLICY_VALUES)}"
                )
        try:
            defaults = self._core.pipeline_defaults.save_settings_section(
                section, values
            )
        except BindingValidationError as error:
            # the service's own structural guard; same typed surface as the
            # pre-validation above (INVALID_REQUEST, never a raw ValueError)
            raise SettingsRequestError(str(error)) from error
        return {"settings": dict(defaults.settings)}

    # ------------------------------------------------------------------
    # set_region_type / list_regions (M2-REGION-RETYPE-CORE)
    # ------------------------------------------------------------------

    def _global_sfx_policy_value(self) -> str:
        """The CURRENT global ``sfx.policy`` configuration value -- the EV-8
        re-snapshot source for retype-to-sfx (contract rev 1.4 §5.4). Read
        fresh at retype time; an unset section keeps the domain default
        SKIP (M2-SFX-TRANSLATE-ENTRY)."""
        settings = self._core.pipeline_defaults.read().settings
        sfx_section = settings.get("sfx")
        if sfx_section is None:
            return SfxPolicy.SKIP.value
        if not isinstance(sfx_section, dict):
            # corrupted store shape: internal failure, not a bad request --
            # the assembly-time reader fail-fasts on the same shape.
            raise RuntimeError("sfx settings section is not an object")
        policy_value = sfx_section.get("policy", SfxPolicy.SKIP.value)
        if policy_value not in _SFX_POLICY_VALUES:
            raise RuntimeError(
                f"sfx.policy value {policy_value!r} is not one of"
                f" {sorted(_SFX_POLICY_VALUES)}"
            )
        return policy_value

    def handle_set_region_type(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Retype one region (contract rev 1.4 §5.4).

        Validation is WRITE-SIDE and typed fail-closed BEFORE any
        persistence (the §5.3 discipline): ``region_id`` a non-empty string,
        ``new_region_type`` inside the RegionType six-value closed set,
        ``expected_revision`` (when present) a real integer (JSON booleans
        are NOT integers on this face). Error semantics reuse the existing
        typed literals only: the optimistic guard (C4) maps to
        INPUT_REVISION_CHANGED/conflict, an unknown or soft-deleted
        region_id to TARGET_NOT_FOUND/not_found, and everything Core-side
        unclassified falls through to UNKNOWN/internal in dispatch. The
        result is the post-retype effective state -- one round trip, no
        second query (§5.3 settings_update_section precedent)."""
        region_id = payload.get("region_id")
        if not isinstance(region_id, str) or not region_id:
            raise RegionRequestError(
                "set_region_type requires 'region_id': a non-empty string"
            )
        new_region_type = payload.get("new_region_type")
        if not (
            isinstance(new_region_type, str)
            and new_region_type in _REGION_TYPE_VALUES
        ):
            raise RegionRequestError(
                "set_region_type requires 'new_region_type': one of"
                f" {sorted(_REGION_TYPE_VALUES)}"
            )
        expected_revision = payload.get("expected_revision")
        if expected_revision is not None and (
            not isinstance(expected_revision, int)
            or isinstance(expected_revision, bool)
        ):
            raise RegionRequestError(
                "set_region_type 'expected_revision' must be an integer"
                " when present"
            )

        try:
            outcome = self._core.editing.set_region_type(
                region_id,
                new_region_type,
                current_global_sfx_policy=self._global_sfx_policy_value(),
                expected_revision_no=expected_revision,
            )
        except RegionNotFound as error:
            # C7: the region does not exist or is soft-deleted. The typed
            # TARGET_NOT_FOUND carries a fixed safe phrase (§8: no paths,
            # no raw exception text).
            raise RegionLookupError(region_id) from error
        if outcome.status is GuardStatus.INPUT_REVISION_CHANGED:
            # C4: the explicit optimistic expectation failed; the region
            # state is untouched (zero write).
            raise RegionConflictError(
                "region revision changed since it was read"
            )
        if outcome.status is not GuardStatus.APPLIED:
            # a USER write carries no lock expectation, so LOCK_CHANGED is
            # an internal invariant breach here -- fall through to
            # UNKNOWN/internal instead of inventing a wire semantics.
            raise RuntimeError(
                f"set_region_type commit failed: {outcome.detail}"
            )

        # One round trip: read back the effective state from the same
        # authoritative region object (already updated in place by the
        # commit seam).
        region = self._core.editing.get_region(region_id)
        return {
            "region_id": region_id,
            "revision_no": outcome.revision_no,
            "region_type": region.region_type.value,
            "sfx_policy": region.sfx_policy.value,
        }

    def handle_list_regions(self, payload: dict[str, Any]) -> dict[str, Any]:
        """The RegionListSummary read channel (contract rev 1.4 §5.4, read
        face widened additively by rev 1.5 / M2-WORKBENCH-REACT-1):
        ``{"regions": [...], "page_size": {"width", "height"} | null}`` in
        reading_order ascending. A page with no rows -- unknown page_id
        included -- is an EMPTY LIST, not an error (footnote a: no page
        existence check, the existing list_regions semantics); an unknown
        page reads ``page_size: null`` (the frozen-None channel precedent of
        §5.3, distinguishable from a zero extent). ``page_size`` is the
        page's pixel-size projection the RegionOverlay letterbox math
        consumes ("size only from the projection", M2-UI1 §2.2); the per-row
        optional ``geometry`` is the normalized reverse mapping owned by
        ``application/editing/region_canvas.py``. Zero protocol bump: no new
        command, purely optional fields (rev 1.5 additive widening)."""
        page_id = payload.get("page_id")
        if not isinstance(page_id, str) or not page_id:
            raise RegionRequestError(
                "list_regions requires 'page_id': a non-empty string"
            )
        page = self._core.repository.get_page(page_id)
        page_size = (
            {"width": page.width, "height": page.height} if page else None
        )
        return {
            "regions": self._core.editing.list_region_summaries(
                page_id,
                page_size=(page.width, page.height) if page else None,
            ),
            "page_size": page_size,
        }

    def handle_list_region_revisions(self, payload: dict[str, Any]) -> dict[str, Any]:
        region_id = payload.get("region_id")
        if not isinstance(region_id, str) or not region_id:
            raise RegionRequestError(
                "list_region_revisions requires 'region_id': a non-empty string"
            )
        try:
            return self._core.editing.list_revision_summaries(region_id)
        except RegionNotFound as error:
            raise RegionLookupError(region_id) from error

    def handle_restore_region_revision(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        region_id = payload.get("region_id")
        revision_no = payload.get("revision_no")
        expected_revision = payload.get("expected_revision")
        if not isinstance(region_id, str) or not region_id:
            raise RegionRequestError(
                "restore_region_revision requires 'region_id': a non-empty string"
            )
        if not self._is_positive_integer(revision_no):
            raise RegionRequestError(
                "restore_region_revision requires positive integer 'revision_no'"
            )
        if not self._is_positive_integer(expected_revision):
            raise RegionRequestError(
                "restore_region_revision requires positive integer 'expected_revision'"
            )
        try:
            region, committed_no = self._core.editing.restore_revision_with_number(
                region_id,
                revision_no,
                expected_revision_no=expected_revision,
            )
        except RegionNotFound as error:
            raise RegionLookupError(region_id) from error
        except RegionRevisionNotFound as error:
            raise RegionLookupError(region_id) from error
        except RegionRevisionChanged as error:
            raise RegionConflictError(
                "region revision changed since it was read"
            ) from error
        return {
            "region_id": region_id,
            "revision_no": committed_no,
            "region_type": region.region_type.value,
            "sfx_policy": region.sfx_policy.value,
        }

    def handle_rerender_page(self, payload: dict[str, Any]) -> dict[str, Any]:
        page_id = payload.get("page_id")
        if not isinstance(page_id, str) or not page_id:
            raise RegionRequestError(
                "rerender_page requires 'page_id': a non-empty string"
            )
        if self._core.repository.get_page(page_id) is None:
            raise RegionLookupError(page_id)
        outcome = self._core.render.rerender_page(page_id)
        if outcome.status != "committed":
            code = outcome.error_code or E_UNKNOWN
            if code == "COMPOSITION_BASE_CHANGED":
                code = E_INPUT_REVISION_CHANGED
            elif outcome.status == "write_failed":
                code = "ARTIFACT_WRITE_FAILED"
            # M2-CATEGORY-CLARIFY-1 (RC4-10): required-input missing is an
            # AVAILABILITY failure (data not there), not a "target does not
            # exist" one -- §8 taxonomy, category never frozen before.
            category = "conflict" if code == E_INPUT_REVISION_CHANGED else (
                "not_found" if code == E_TARGET_NOT_FOUND else (
                    "unavailable" if code == "MISSING_REQUIRED_INPUT" else "internal"
                )
            )
            message = {
                "MISSING_REQUIRED_INPUT": "required render input is missing",
                E_TARGET_NOT_FOUND: "page not found",
                E_INPUT_REVISION_CHANGED: "render input changed; retry the operation",
                "ARTIFACT_WRITE_FAILED": "render output could not be saved",
            }.get(code, "page rerender failed")
            print(
                f"[core.rerender_page] code={code} detail={outcome.detail or ''}",
                file=sys.stderr,
            )
            raise RenderCommandError(code, category, message)

        preview = None
        preview_error = None
        try:
            if self._render_previews is None or outcome.managed_path is None:
                raise RuntimeError("preview publisher is not configured")
            origin = self._resolve_preview_origin(outcome)
            preview = self._render_previews.publish(
                self._core.storage.absolute_path(outcome.managed_path),
                f"rev-{outcome.revision_no}",
                origin=origin,
            )
        except Exception as error:
            print(f"[core.rerender_page] preview publish failed: {error!r}", file=sys.stderr)
            preview_error = "PREVIEW_UNAVAILABLE"

        return {
            "page_id": page_id,
            "artifact_id": outcome.artifact_id,
            "revision_no": outcome.revision_no,
            "reports": [
                {
                    "region_id": report.region_id,
                    "status": report.status,
                    "skip_reason": report.skip_reason,
                    "font_substituted": report.font_substituted,
                }
                for report in outcome.reports
            ],
            "preview": preview,
            "preview_error": preview_error,
        }

    def _resolve_preview_origin(self, outcome: Any) -> PreviewOrigin | None:
        """M2-DERIVED-GC-2 (design §2.1): bind this render outcome to its
        exact source revision BEFORE the publish transaction.

        Within this very request, the revision list of
        ``outcome.artifact_id`` must yield EXACTLY ONE row matching both
        ``revision_no`` and ``outcome.managed_path`` verbatim, and the
        artifact must be a TRANSLATED product artifact. Zero matches /
        multiple matches / any mismatch / a producer root that is not
        configured raise -- the caller maps that to the frozen
        PREVIEW_UNAVAILABLE fail-closed semantics (the Managed commit itself
        is NOT rolled back). The stored identity is the row's
        artifact_revision_id: revision_no is per-artifact and reusable after
        purges, never a global id."""

        if self._producer_root is None:
            return None
        conn = self._core.conn
        try:
            artifact = conn.execute(
                "SELECT artifact_type, current_revision_id FROM media_artifacts"
                " WHERE artifact_id = ?",
                (outcome.artifact_id,),
            ).fetchone()
            if artifact is None or artifact["artifact_type"] != "translated":
                raise RuntimeError("preview origin: artifact missing or not TRANSLATED")
            matching = conn.execute(
                "SELECT artifact_revision_id FROM artifact_revisions"
                " WHERE artifact_id = ? AND revision_no = ? AND managed_path = ?",
                (outcome.artifact_id, outcome.revision_no, outcome.managed_path),
            ).fetchall()
        except Exception as error:
            raise RuntimeError(f"preview origin: source lookup failed: {error!r}") from error
        if len(matching) != 1:
            raise RuntimeError(
                "preview origin: expected exactly one matching source revision,"
                f" found {len(matching)}"
            )
        return PreviewOrigin(
            producer_root=self._producer_root,
            artifact_id=outcome.artifact_id,
            artifact_revision_id=matching[0]["artifact_revision_id"],
            managed_rel_path=outcome.managed_path,
        )

    def handle_list_chapters(self, payload: dict[str, Any]) -> dict[str, Any]:
        """M2-PAGE-NAV-PROJECTION-1 (contract M2-C1 rev 1.8 §5): the chapter
        navigation read face -- one book's chapters in the user's current
        ``sort_order`` (D03 AC-PAGE-001; the repository query already orders).
        Read-only projection: an unknown book id yields an EMPTY list (the
        list_regions P3-4 precedent -- a missing parent is empty data, not
        an error), and the summary rows carry no Reader/display semantics.
        """
        book_id = payload.get("book_id")
        if not isinstance(book_id, str) or not book_id:
            raise RegionRequestError(
                "list_chapters requires 'book_id': a non-empty string"
            )
        chapters = self._core.repository.list_chapters(book_id)
        return {
            "chapters": [
                {
                    "chapter_id": chapter.chapter_id,
                    "title": chapter.title,
                    "chapter_number": chapter.chapter_number,
                    "sort_order": chapter.sort_order,
                }
                for chapter in chapters
            ]
        }

    def handle_list_chapter_pages(self, payload: dict[str, Any]) -> dict[str, Any]:
        """M2-PAGE-NAV-PROJECTION-1 (contract M2-C1 rev 1.8 §5): one
        chapter's committed pages in the user's current ``sort_order``
        (D03 AC-PAGE-001). Navigation summary rows only -- the managed
        original ref, pixel dimensions and lock state stay behind the
        channel; the page IMAGE itself is fetched downstream via
        resolve_page_resource -> issue_resource_url.
        """
        chapter_id = payload.get("chapter_id")
        if not isinstance(chapter_id, str) or not chapter_id:
            raise RegionRequestError(
                "list_chapter_pages requires 'chapter_id': a non-empty string"
            )
        pages = self._core.repository.list_pages(chapter_id)
        return {
            "pages": [
                {
                    "page_id": page.page_id,
                    "source_filename": page.source_filename,
                    "sort_order": page.sort_order,
                }
                for page in pages
            ]
        }

    def handle_resolve_page_resource(self, payload: dict[str, Any]) -> dict[str, Any]:
        """M2-PAGE-RESOURCE-RESOLVE-1: page_id -> servable resource catalog key.

        The managed original is immutable, so the resource key is
        deterministic (``page-original-{page_id}``): the first resolve
        publishes the file byte-for-byte into the derived read-only root
        (same channel the RC-4 preview publisher uses) and every later
        resolve is a catalog lookup returning the same key -- idempotent,
        no duplicate derived artifacts.
        """
        page_id = payload.get("page_id")
        if not isinstance(page_id, str) or not page_id:
            raise RegionRequestError(
                "resolve_page_resource requires 'page_id': a non-empty string"
            )
        if self._render_previews is None:
            raise RuntimeError("resource catalog is not configured")
        page = self._core.repository.get_page(page_id)
        if page is None or not page.managed_original_ref:
            raise RegionLookupError(page_id)
        # Same seam as the assembly-time read_original_page closure: the
        # managed original is resolved at use time, must stay inside the
        # Managed Copy root, and no path or new business identity rides
        # the wire (only the opaque catalog key).
        managed_root = self._core.storage.root.resolve()
        source = Path(self._core.storage.absolute_path(page.managed_original_ref)).resolve()
        try:
            source.relative_to(managed_root)
        except ValueError as error:
            raise RuntimeError("managed original escaped the Managed Copy root") from error
        suffix = source.suffix.lower()
        if suffix not in _ORIGINAL_SUFFIXES:
            raise RuntimeError(f"unsupported managed original format: {suffix!r}")
        if not source.is_file():
            raise RegionLookupError(page_id)
        resource_id = f"page-original-{page.page_id}"
        entry = self._render_previews.lookup(resource_id)
        if entry is not None and self._render_previews.artifact_exists(entry.rel_path):
            # Catalog hit on a LIVE artifact: the managed original is
            # immutable, so the first publish wins and later resolves are
            # lookups (idempotent key). DSH r1 PR-07 adds the artifact
            # probe: a wiped derived root self-heals by re-publishing
            # under the same deterministic key instead of returning a
            # key whose file is gone forever.
            return {"resource_id": resource_id, "revision": ORIGINAL_REVISION}
        return self._render_previews.publish_original(source, resource_id, suffix)

    @staticmethod
    def _is_positive_integer(value: Any) -> bool:
        return isinstance(value, int) and not isinstance(value, bool) and value > 0

    def dispatch_request(self, raw_line: str) -> tuple[dict[str, Any], bool]:
        """Dispatch a single raw json request line.

        Returns (response_dict, should_exit).
        """
        try:
            req = json.loads(raw_line)
        except json.JSONDecodeError:
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": None,
                    "result": None,
                    "error": make_error_envelope(
                        code="INVALID_JSON",
                        category="validation",
                        message="Request must be a valid JSON object",
                        retryable=False,
                    ),
                },
                False,
            )

        if not isinstance(req, dict):
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": None,
                    "result": None,
                    "error": make_error_envelope(
                        code="INVALID_REQUEST",
                        category="validation",
                        message="Request must be a JSON object",
                        retryable=False,
                    ),
                },
                False,
            )

        request_id = req.get("request_id")
        protocol = req.get("protocol")
        version = req.get("version")
        command = req.get("command")
        payload = req.get("payload") if isinstance(req.get("payload"), dict) else {}

        # Validate protocol name and version (must be dict with integer major == PROTOCOL_MAJOR)
        is_valid_version = (
            isinstance(version, dict)
            and isinstance(version.get("major"), int)
            and not isinstance(version.get("major"), bool)
            and version.get("major") == PROTOCOL_MAJOR
        )
        if protocol != PROTOCOL_NAME or not is_valid_version:
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": request_id,
                    "result": None,
                    "error": make_error_envelope(
                        code=E_PROTOCOL_VERSION_UNSUPPORTED,
                        category="validation",
                        message="Unsupported protocol or version",
                        retryable=False,
                    ),
                },
                False,
            )

        # Dispatch command
        if command == "core.ping":
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": request_id,
                    "result": self.handle_ping(payload),
                    "error": None,
                },
                False,
            )

        if command == "ListBooks":
            try:
                books = self.handle_list_books(payload)
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": books,
                        "error": None,
                    },
                    False,
                )
            except sqlite3.Error:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_LIST_BOOKS_FAILED,
                            category="internal",
                            message="Failed to query library books",
                            retryable=True,
                        ),
                    },
                    False,
                )
            except Exception:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_UNKNOWN,
                            category="internal",
                            message="Failed to list books",
                            retryable=False,
                        ),
                    },
                    False,
                )

        # M2-PROD-DETECT-3: real inference over the assembled detector. The
        # three commands above are untouched; this branch only widens the
        # surface (protocol minor bump, see the module docstring).
        if command == "core.detect":
            try:
                detect_result = self.handle_detect(payload)
            except DetectRequestError as error:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_INVALID_REQUEST,
                            category="validation",
                            message=str(error),
                            retryable=False,
                        ),
                    },
                    False,
                )
            except ProviderError as error:
                # Typed provider failure, wire-sanitized (DSH r1 R1): the
                # provider's own error_code (PROVIDER_NOT_CONFIGURED,
                # PROVIDER_DEPENDENCY_MISSING, PROVIDER_FAILED, INVALID_INPUT,
                # ...) and its retryability ruling stay stable on the wire,
                # but real provider MESSAGE text embeds local absolute paths
                # (weights directories) and Contract §8 forbids paths on the
                # wire -- so the envelope carries a fixed safe phrase and the
                # full original detail goes to stderr only. INVALID_INPUT is
                # the single pass-through (parameter-level byte-count/frame
                # text, no paths by construction; pinned by tests).
                if error.error_code == "INVALID_INPUT":
                    message = str(error)[:500]
                else:
                    message = _PROVIDER_SAFE_MESSAGES.get(
                        error.error_code, _PROVIDER_SAFE_DEFAULT
                    )
                print(
                    f"core.detect provider error [{error.error_code}]: "
                    f"{error}",
                    file=sys.stderr,
                    flush=True,
                )
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=error.error_code,
                            # R14 (DSH r1): provider input-gate errors police
                            # our request shape -> validation; the rest are
                            # internal (Proposal-level mapping, contract
                            # Revision history annotation).
                            category=_PROVIDER_ERROR_CATEGORY.get(
                                error.error_code, "internal"
                            ),
                            message=message,
                            retryable=bool(error.retryable),
                        ),
                    },
                    False,
                )
            except Exception:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_UNKNOWN,
                            category="internal",
                            message="Detection failed",
                            retryable=False,
                        ),
                    },
                    False,
                )
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": request_id,
                    "result": detect_result,
                    "error": None,
                },
                False,
            )

        # M2-SETTINGS-IPC-CHANNEL: the settings read/write pair. The seven
        # commands above are untouched; these branches only widen the
        # surface (protocol minor bump, see the module docstring). Write-side
        # validation lives in the handler (typed INVALID_REQUEST BEFORE any
        # persistence); persistence failures surface as UNKNOWN/internal.
        if command in ("settings.get", "settings.update_section"):
            try:
                if command == "settings.get":
                    result = self.handle_settings_get(payload)
                else:
                    result = self.handle_settings_update_section(payload)
            except SettingsRequestError as error:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_INVALID_REQUEST,
                            category="validation",
                            message=str(error),
                            retryable=False,
                        ),
                    },
                    False,
                )
            except Exception:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_UNKNOWN,
                            category="internal",
                            message="Settings operation failed",
                            retryable=False,
                        ),
                    },
                    False,
                )
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": request_id,
                    "result": result,
                    "error": None,
                },
                False,
            )

        # M2-REGION-RETYPE-CORE: the region retype write + read pair. The
        # commands above are untouched; these branches only widen the
        # surface (protocol minor bump, see the module docstring). Request
        # validation is typed fail-closed BEFORE any persistence (the §5.3
        # discipline); error semantics reuse the existing typed literals
        # only (contract rev 1.4 §5.4 mapping table).
        if command in (
            "set_region_type",
            "list_regions",
            "list_region_revisions",
            "restore_region_revision",
        ):
            try:
                if command == "set_region_type":
                    result = self.handle_set_region_type(payload)
                elif command == "list_region_revisions":
                    result = self.handle_list_region_revisions(payload)
                elif command == "restore_region_revision":
                    result = self.handle_restore_region_revision(payload)
                else:
                    result = self.handle_list_regions(payload)
            except RegionRequestError as error:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_INVALID_REQUEST,
                            category="validation",
                            message=str(error),
                            retryable=False,
                        ),
                    },
                    False,
                )
            except RegionConflictError as error:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_INPUT_REVISION_CHANGED,
                            category="conflict",
                            message=str(error),
                            retryable=False,
                        ),
                    },
                    False,
                )
            except RegionLookupError:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_TARGET_NOT_FOUND,
                            category="not_found",
                            message="region not found",
                            retryable=False,
                        ),
                    },
                    False,
                )
            except Exception:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_UNKNOWN,
                            category="internal",
                            message={
                                "set_region_type": "Region retype failed",
                                "restore_region_revision": "Region restore failed",
                            }.get(command, "Region read failed"),
                            retryable=False,
                        ),
                    },
                    False,
                )
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": request_id,
                    "result": result,
                    "error": None,
                },
                False,
            )

        if command == "rerender_page":
            try:
                result = self.handle_rerender_page(payload)
            except RegionRequestError as error:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_INVALID_REQUEST,
                            category="validation",
                            message=str(error),
                            retryable=False,
                        ),
                    },
                    False,
                )
            except RegionLookupError:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_TARGET_NOT_FOUND,
                            category="not_found",
                            message="page not found",
                            retryable=False,
                        ),
                    },
                    False,
                )
            except RenderCommandError as error:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=error.code,
                            category=error.category,
                            message=str(error),
                            retryable=False,
                        ),
                    },
                    False,
                )
            except Exception:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_UNKNOWN,
                            category="internal",
                            message="page rerender failed",
                            retryable=False,
                        ),
                    },
                    False,
                )
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": request_id,
                    "result": result,
                    "error": None,
                },
                False,
            )

        if command in ("list_chapters", "list_chapter_pages"):
            # M2-PAGE-NAV-PROJECTION-1: read-only navigation projections.
            # Unknown parent ids are EMPTY data (P3-4 precedent), so the
            # only error face here is the payload validation row.
            try:
                if command == "list_chapters":
                    result = self.handle_list_chapters(payload)
                else:
                    result = self.handle_list_chapter_pages(payload)
            except RegionRequestError as error:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_INVALID_REQUEST,
                            category="validation",
                            message=str(error),
                            retryable=False,
                        ),
                    },
                    False,
                )
            except Exception:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_UNKNOWN,
                            category="internal",
                            message="page navigation projection failed",
                            retryable=False,
                        ),
                    },
                    False,
                )
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": request_id,
                    "result": result,
                    "error": None,
                },
                False,
            )

        # M2-PAGE-RESOURCE-RESOLVE-1: page -> servable resource key. Read
        # face of the display image; publishes the immutable managed original
        # into the derived read-only root under a deterministic catalog key.
        if command == "resolve_page_resource":
            try:
                result = self.handle_resolve_page_resource(payload)
            except RegionRequestError as error:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_INVALID_REQUEST,
                            category="validation",
                            message=str(error),
                            retryable=False,
                        ),
                    },
                    False,
                )
            except RegionLookupError:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_PAGE_NOT_FOUND,
                            category="not_found",
                            message="page or its managed original is not available",
                            retryable=False,
                        ),
                    },
                    False,
                )
            except OSError as error:
                print(
                    f"[core.resolve_page_resource] publish failed: {error!r}",
                    file=sys.stderr,
                )
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code="ARTIFACT_WRITE_FAILED",
                            category="internal",
                            message="page resource could not be published",
                            retryable=True,
                        ),
                    },
                    False,
                )
            except Exception:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_UNKNOWN,
                            category="internal",
                            message="page resource resolve failed",
                            retryable=False,
                        ),
                    },
                    False,
                )
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": request_id,
                    "result": result,
                    "error": None,
                },
                False,
            )

        if command == "core.shutdown":
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": request_id,
                    "result": {"status": "stopped"},
                    "error": None,
                },
                True,
            )

        # Unknown command
        return (
            {
                "protocol": PROTOCOL_NAME,
                "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                "request_id": request_id,
                "result": None,
                "error": make_error_envelope(
                    code=E_UNKNOWN_COMMAND,
                    category="validation",
                    message=f"Unknown command: {command!r}",
                    retryable=False,
                ),
            },
            False,
        )

    def serve_forever(self) -> int:
        """Main stdio loop reading requests line by line."""
        for line in self._stdin:
            line = line.strip()
            if not line:
                continue
            response, should_exit = self.dispatch_request(line)
            self._emit(response)
            if should_exit:
                return 0
        return 0

    def _emit(self, payload: dict[str, Any]) -> None:
        self._stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
        self._stdout.flush()


def main() -> int:
    env_root = os.environ.get("NEWMANGA_DATA_ROOT")
    data_root = Path(env_root) if env_root else default_data_root()
    derived_root = Path(os.environ.get("M2RC1_DERIVED_ROOT", data_root / "derived"))
    catalog_db = Path(
        os.environ.get("M2RC2_CATALOG_DB", data_root / "catalog" / "catalog.sqlite")
    )
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    derived_root.mkdir(parents=True, exist_ok=True)

    # M2-DERIVED-GC-2 startup order (design §2.3): namespace protection first
    # -- the fresh-catalog controlled first-bind runs under its own exclusive
    # lock inside initialize_namespace; then the Core tries the exclusive
    # lease for the sweeps. A peer holding a shared lease means BOTH sweeps
    # are skipped this boot and the Core serves normally under a shared
    # lease. serve_forever (and therefore core.ping) is only reached after
    # the protection is held and the sweeps are done.
    if not catalog_db.exists():
        initialize_namespace(catalog_db, derived_root)
    catalog_identity = resolve_namespace_identity(catalog_db)[1]
    exclusive = try_acquire_exclusive_lease(
        derived_root, expected_catalog_identity=catalog_identity
    )
    core = None
    try:
        core = assemble_production_core(data_root)
        if exclusive is not None:
            # The sweeps run under the exclusive lease; the store borrows it
            # (it must not take a second, shared lock for itself).
            gc_store = ResourceCatalogStore(catalog_db, namespace_lease=exclusive)
            try:
                gc_previews = RenderPreviewPublisher(derived_root, gc_store)
                _run_startup_gc(gc_previews)
                _run_retired_preview_gc(
                    gc_previews, gc_store, core.conn,
                    producer_root=str(data_root.resolve()),
                )
            finally:
                gc_store.close()
            # Exclusive -> shared downgrade: no business request happens in
            # between (nothing is served before serve_forever).
            exclusive.release()
        else:
            print(
                "[core.derived_gc] skipped: namespace busy"
                " (a managed peer holds a shared lease)",
                file=sys.stderr,
            )
        shared_lease = acquire_shared_lease(
            derived_root, expected_catalog_identity=resolve_namespace_identity(catalog_db)[1]
        )
        catalog = ResourceCatalogStore(catalog_db, namespace_lease=shared_lease)
        try:
            previews = RenderPreviewPublisher(derived_root, catalog)
            server = CoreServiceServer(
                core,
                render_previews=previews,
                producer_root=data_root.resolve(),
            )
            return server.serve_forever()
        finally:
            catalog.close()
    finally:
        if exclusive is not None and exclusive.held:
            exclusive.release()
        if core is not None:
            core.conn.close()


def _run_startup_gc(previews: RenderPreviewPublisher) -> None:
    """M2-DERIVED-GC-1 (RC4-12 first slice, PARTIAL mitigation): one startup
    sweep of the derived read-only root. Orphan files (no catalog row) and
    dead rows (missing file) are equivalent to absence at the failure-CLASS
    level -- see :meth:`RenderPreviewPublisher.collect_orphans` for the
    authoritative typed-code wording. Live files with live rows are never
    touched. Fail-soft: a GC error must not block the service from
    starting.

    M2-DERIVED-GC-2: this sweep now runs ONLY inside the exclusive namespace
    window (the caller holds the lease) -- never outside the protected
    window. The per-run GC stdout/stats wire semantics are unchanged."""
    try:
        stats = previews.collect_orphans()
        print(
            f"[core.derived_gc] orphan_files_removed={stats['orphan_files_removed']}"
            f" dead_rows_removed={stats['dead_rows_removed']}",
            file=sys.stderr,
        )
    except Exception as error:
        print(f"[core.derived_gc] skipped: {error!r}", file=sys.stderr)


def _run_retired_preview_gc(
    publisher: RenderPreviewPublisher,
    store: ResourceCatalogStore,
    product_conn: Any,
    *,
    producer_root: str,
) -> dict[str, int]:
    """M2-DERIVED-GC-2 live-preview sweep (design §2.2/§2.4, exclusive
    namespace window ONLY).

    Candidates are retired=1 origin rows whose catalog shape gate passed;
    each one is re-verified against the PRODUCT database under this
    connection's ``BEGIN IMMEDIATE`` (SELECT-only: current/pinned/source
    identity/hash/size) and deleted by DELETE DISPOSITION on the verifying
    handle BEFORE its catalog+origin metadata is removed in one catalog
    transaction. Any unknown/protected/busy verdict retains the copy. There
    is no TTL, age, count or naming heuristic anywhere in this sweep."""
    stats = {
        "retired_deleted": 0,
        "protected_retained": 0,
        "unknown_skipped": 0,
        "lifecycle_metadata_reclaimed": 0,
    }
    try:
        stats["lifecycle_metadata_reclaimed"] = store.reclaim_orphan_lifecycle_rows()
        candidates = store.retired_preview_candidates(producer_root)
        product_conn.commit()
        product_conn.execute("BEGIN IMMEDIATE")
        try:
            for candidate in candidates:
                verified = _verify_retired_source(product_conn, candidate)
                if verified is None:
                    stats["protected_retained"] += 1
                    continue
                expected_sha256, expected_size = verified
                deleted, reason = publisher.delete_retired_preview_copy(
                    candidate.resource_id,
                    expected_sha256=expected_sha256,
                    expected_size=expected_size,
                )
                if not deleted:
                    stats["unknown_skipped"] += 1
                    print(
                        f"[core.derived_gc] retired copy kept: {reason}",
                        file=sys.stderr,
                    )
                    continue
                store.reclaim_retired_preview_metadata(candidate.resource_id)
                stats["retired_deleted"] += 1
        finally:
            product_conn.rollback()
    except Exception as error:
        print(f"[core.derived_gc] retired sweep skipped: {error!r}", file=sys.stderr)
    return stats


def _verify_retired_source(product_conn: Any, candidate: Any) -> tuple[str, int] | None:
    """Product-DB verdict for one retired candidate (design §2.4, SELECT
    only). None == UNKNOWN/protected -> retain: a missing artifact, a
    non-TRANSLATED artifact, a missing/aliased revision, a verbatim
    managed-path mismatch, the CURRENT pointer, a pin, or any query error
    is never evidence of absence-of-reference."""
    try:
        artifact = product_conn.execute(
            "SELECT artifact_type, current_revision_id FROM media_artifacts"
            " WHERE artifact_id = ?",
            (candidate.artifact_id,),
        ).fetchone()
        if artifact is None or artifact["artifact_type"] != "translated":
            return None
        revision = product_conn.execute(
            "SELECT artifact_id, managed_path, file_hash, size_bytes, is_pinned"
            " FROM artifact_revisions WHERE artifact_revision_id = ?",
            (candidate.artifact_revision_id,),
        ).fetchone()
        if revision is None or revision["artifact_id"] != candidate.artifact_id:
            return None
        if revision["managed_path"] != candidate.managed_rel_path:
            return None
        if artifact["current_revision_id"] == candidate.artifact_revision_id:
            return None
        if revision["is_pinned"]:
            return None
        return str(revision["file_hash"]), int(revision["size_bytes"])
    except Exception:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
