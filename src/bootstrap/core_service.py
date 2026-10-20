"""Production Core Service (M2-IPC1).

The host spawns this module -- ``python -m bootstrap.core_service`` -- as the
production Core sidecar process. It assembles the production Core services
(migrations, repositories, managed storage, startup recover_running_runs),
then acquires the persistent Run scheduler lease and enters a stdio request
loop serving typed commands and best-effort lifecycle events over JSON-lines.

Transport & Envelope (M2-C1 rev 2.1 §3, §5, §6.3, §8, §10.3, §12):
  Request:
    {"protocol": "new-manga.core", "version": {"major": 2, "minor": 1},
     "request_id": "<id>", "command": "<cmd>", "payload": {...}}
  Response:
    {"protocol": "new-manga.core", "version": {"major": 2, "minor": 1},
     "request_id": "<id>", "result": {...} | null, "error": ErrorEnvelope | null}

Allowed production commands (M2-IPC1 + existing command slices + P13-C1):
  - core.ping: {} -> {"status": "ready", "protocol_version": {"major": 2, "minor": 1}, "capabilities": ["library.list_books"]}
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
import hashlib
import hmac
from dataclasses import asdict, dataclass
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, TextIO

from application.editing.errors import (
    GuardStatus,
    RegionNotFound,
    RegionRevisionChanged,
    RegionRevisionNotFound,
)
from application.importing.documents.ports import DocumentDecodeError
from application.importing.images.ports import DecodedImage, ImportSource
from application.importing.images.service import DuplicatePolicy
from application.library.errors import BookNotFound
from application.resource_channel.dto import TypedResourceChannelError
from application.settings.errors import BindingValidationError
from application.export import ExportFormat, ExportPage, ExportRequest, P16ExportRuntime, StalePolicy
from application.export.service import OverwritePolicy
from application.translation.color.service import SourceStyleService
from bootstrap.core_assembly import (
    CoreServices,
    assemble_core_services,
    default_data_root,
)
from domain.regions.entities import RegionType, SfxPolicy
from domain.tasks.models import COMMAND_CATALOG, CommandType, PipelineError, PipelineScope, ScopeType
from infrastructure.importing import QtImageDecoder, SUPPORTED_IMAGE_SUFFIXES
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
    restore_namespace_lock,
)
from infrastructure.resource_channel.handle_resolver import (
    acquire_shared_lease,
    read_lock_binding_if_any,
    resolve_namespace_identity,
    try_acquire_exclusive_lease,
)
from infrastructure.resource_channel.render_preview import (
    ORIGINAL_REVISION,
    RenderPreviewPublisher,
)
from infrastructure.export.qt_free import encode_png
from infrastructure.export.target_refs import ExportTargetRefError
from ports.detection.ports import DetectionRequest
from ports.providers.errors import ProviderError, ProviderNotConfigured
from bootstrap.settings_commands import P15_SNAPSHOT_KEY, P15SettingsCommands, SettingsSurfaceError

PROTOCOL_NAME = "new-manga.core"
PROTOCOL_MAJOR = 2
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
# P16-C1 rev 2.1 added Reader/Export; P12-C1 rev 2.2 adds ImportPages.
# P15-C1 rev 2.7 adds settings commands at minor 7. Keep the existing command
# surface at 2.3; the dispatcher projects minor 7 only for the new P15 wire.
PROTOCOL_MINOR = 3
_P15_PROTOCOL_MINOR = 7
_CREATE_PROTOCOL_MINOR = 8
_DELETE_PROTOCOL_MINOR = 10
_CREATE_COMMANDS = frozenset({"CreateBook", "CreateChapter"})
_DELETE_COMMANDS = frozenset({"PermanentlyDeleteBook", "PermanentlyDeleteBooks"})
_CREATE_FIELDS = {
    "CreateBook": (("title", True),),
    "CreateChapter": (("book_id", True), ("title", True), ("chapter_number", False)),
}
# HOST-ISSUER-1-C1 rev 2.3 adds an independent host-owned stdio control envelope.
_HOST_CONTROL_COMMANDS = frozenset({
    "OpenHostSession", "RegisterImportSource", "RevokeImportSource",
    "RegisterExportTarget", "RevokeExportTarget", "CloseHostSession",
})
_RUN_COMMANDS = frozenset({
    "StartRun", "ControlRun", "ResumeBlockedRun", "GetRunSnapshot",
    "GetTaskProjection", "RetryFailedTargets",
})
_P15_SETTINGS_COMMANDS = frozenset({
    "settings_provider_profiles_list",
    "settings_provider_profiles_create",
    "settings_provider_profiles_update",
    "settings_provider_profiles_delete",
    "settings_provider_bindings_set",
    "settings_provider_bindings_clear",
    "settings_provider_bindings_resolve",
    "settings_provider_run_snapshot_get",
    "settings_resolve_overrides",
    "settings_network_profiles_list",
    "settings_network_profiles_create",
    "settings_network_profiles_update",
    "settings_network_profiles_delete",
    "settings_network_profile_default_set",
    "settings_network_profile_default_clear",
    "settings_network_profile_resolve",
    "settings_network_profiles_test",
    "BindProfileCredential",
    "ClearProfileCredential",
})

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


_SETTINGS_OS_PATH = re.compile(
    r"(?:[A-Z]:[\\/]|\\\\[^\\/\s]+[\\/]|(?<![/:])//[^/\s]+/|"
    r"(?<![\w/:])/(?!/)[^\s\"']+|~[/\\]|"
    r"%(?:USERPROFILE|HOMEDRIVE|HOMEPATH|APPDATA|LOCALAPPDATA|HOME)%|\$HOME|"
    r"(?:^|[\\/])Users[\\/][^\\/]+[\\/])",
    re.IGNORECASE,
)
_SETTINGS_PATH_REDACTED = "[redacted]"


def _settings_path_field(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", key.casefold())
    return (
        normalized.endswith(("path", "directory", "folder", "filename"))
        or normalized in {"dir", "file", "cwd", "root", "executable"}
    )


def _project_settings_value(value: Any, key: str | None = None) -> Any:
    """Redact path fields and OS paths from IPC output without changing storage."""
    if (
        key is not None
        and _settings_path_field(key)
        and isinstance(value, (str, dict, list))
        and value
    ):
        return _SETTINGS_PATH_REDACTED
    if isinstance(value, dict):
        return {
            (_SETTINGS_PATH_REDACTED if _SETTINGS_OS_PATH.search(name) else name):
            _project_settings_value(item, name)
            for name, item in value.items()
        }
    if isinstance(value, list):
        return [_project_settings_value(item) for item in value]
    if isinstance(value, str) and _SETTINGS_OS_PATH.search(value):
        return _SETTINGS_PATH_REDACTED
    return value


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


class P16WireError(Exception):
    def __init__(self, code: str, category: str, message: str, *, details=None) -> None:
        super().__init__(message)
        self.code, self.category, self.details = code, category, details



class _PassthroughImageDecoder:
    """Legacy test double; production assembly uses ``QtImageDecoder``."""

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
    and leaves startup recovery to the Core scheduler after it owns the
    database-wide lease. Image decoding is lazy, so assembly remains headless
    while imports use the declared Qt image runtime.
    """
    if data_root is None:
        data_root = default_data_root()

    db_path = data_root / "library.db"
    managed_root = data_root / "managed"

    # The decoder loads Qt lazily on image decode, after the headless sidecar assembles.
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
        image_decoder=QtImageDecoder(),
        font_catalog=catalog,
        layout_engine=PillowTextLayoutEngine(catalog),
        compositor=PillowImageCompositor(catalog),
        source_styles=SourceStyleService(_StubStyleAnalyzer()),
        content_decoder=decode_nmfr_frame,
        original_page_reader=read_original_page,
        recover_runs_on_assembly=False,
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


def _sha256_file_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _export_ref_error_envelope(code: str) -> dict[str, Any]:
    categories = {
        "REF_MALFORMED": "validation", "REF_SIGNATURE_INVALID": "validation",
        "REF_SCOPE_DENIED": "validation", "REF_UNKNOWN_ID": "not_found",
        "REF_EXPIRED": "conflict", "REF_REVOKED": "conflict",
        "REF_ALREADY_CONSUMED": "conflict",
    }
    return make_error_envelope(
        code, categories.get(code, "validation"),
        "Export target reference was rejected", retryable=False,
    )


_IMPORT_ERROR_CATEGORIES = {
    "SOURCE_READ_FAILED": "unavailable",
    "INVALID_IMAGE": "validation",
    "INVALID_DOCUMENT": "validation",
    "ENCRYPTED": "validation",
    "UNSUPPORTED_FORMAT": "validation",
    "MISSING_DEPENDENCY": "unavailable",
    "COPY_FAILED": "internal",
    "INVALID_REQUEST": "validation",
    "TARGET_NOT_FOUND": "not_found",
    "REF_MALFORMED": "validation",
    "REF_SIGNATURE_INVALID": "validation",
    "REF_SCOPE_DENIED": "validation",
    "REF_OUT_OF_SCOPE": "validation",
    "REF_REPARSE_POINT": "validation",
    "REF_EXPIRED": "conflict",
    "REF_REVOKED": "conflict",
    "REF_ALREADY_CONSUMED": "conflict",
    "REF_UNKNOWN_ID": "not_found",
    "REF_NOT_FOUND": "not_found",
    "FILE_IDENTITY_CHANGED": "conflict",
    "FILE_SIZE_CHANGED": "conflict",
    "CONTENT_DIGEST_MISMATCH": "conflict",
    "UNKNOWN": "unknown",
}


def _import_item_error(code: str) -> dict[str, Any]:
    category = _IMPORT_ERROR_CATEGORIES.get(code, "unknown")
    retryable: bool | str = True if code in {
        "SOURCE_READ_FAILED", "MISSING_DEPENDENCY", "COPY_FAILED"
    } else False if category != "unknown" else "unknown"
    return {
        "code": code,
        "category": category,
        "message": "Import item could not be processed",
        "retryable": retryable,
    }


def _import_ref_error_envelope(code: str) -> dict[str, Any]:
    category = _IMPORT_ERROR_CATEGORIES.get(code, "unknown")
    return make_error_envelope(
        code, category, "Import source reference was rejected", retryable=False
    )


def _import_page_result(
    page_index: int,
    outcome: str,
    *,
    page=None,
    sha256: str | None = None,
    width: int | None = None,
    height: int | None = None,
    duplicate: bool = False,
    error: dict[str, Any] | None = None,
    side_effects: str = "none",
) -> dict[str, Any]:
    return {
        "page_index": page_index,
        "outcome": outcome,
        "page_id": page.page_id if page is not None else None,
        "source_order": page.source_order if page is not None else None,
        "sort_order": page.sort_order if page is not None else None,
        "sha256": page.source_hash if page is not None else sha256,
        "width": page.width if page is not None else width,
        "height": page.height if page is not None else height,
        "duplicate": bool(duplicate),
        "error": error,
        "side_effects": side_effects,
    }


def _document_import_page_index(filename: str, source_filename: str) -> int | None:
    prefix = f"{Path(source_filename).stem}-page-"
    name = Path(filename).name
    if not name.startswith(prefix) or not name.lower().endswith(".png"):
        return None
    suffix = name[len(prefix):-4]
    return int(suffix) if suffix.isdigit() else None


def _pending_document_pages(pending: list[str]) -> set[int]:
    result: set[int] = set()
    for label in pending:
        match = re.search(r"\(page (\d+)\+\)$", label)
        if match:
            result.add(int(match.group(1)))
    return result


_scheduler_paths_lock = threading.Lock()
_scheduler_paths_owned: set[str] = set()


class _RunSchedulerLease:
    """Kernel-released advisory lease shared by Core instances on one DB."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._file = None
        self._key = str(path.resolve()).casefold()

    def acquire(self) -> bool:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with _scheduler_paths_lock:
            if self._key in _scheduler_paths_owned:
                return False
            handle = self._path.open("a+b")
            try:
                handle.seek(0, os.SEEK_END)
                if handle.tell() == 0:
                    handle.write(b"\0")
                    handle.flush()
                handle.seek(0)
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                handle.close()
                return False
            self._file = handle
            _scheduler_paths_owned.add(self._key)
            return True

    def release(self) -> None:
        handle, self._file = self._file, None
        if handle is None:
            return
        try:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()
            with _scheduler_paths_lock:
                _scheduler_paths_owned.discard(self._key)


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


def _create_validation_details(command: str, payload: Any) -> list[dict[str, str]]:
    if not isinstance(payload, dict):
        return [{"field": "$", "issue": "wrong_type"}]
    fields = dict(_CREATE_FIELDS[command])
    issues: list[dict[str, str]] = []
    for field, value in payload.items():
        if field not in fields:
            issues.append({"field": "$", "issue": "unknown_field"})
        elif field in {"title", "book_id"}:
            if not isinstance(value, str):
                issues.append({"field": field, "issue": "wrong_type"})
            elif not value.strip():
                issues.append({"field": field, "issue": "blank"})
        elif not isinstance(value, str):
            issues.append({"field": field, "issue": "wrong_type"})
    issues.extend(
        {"field": field, "issue": "required"}
        for field, required in _CREATE_FIELDS[command]
        if required and field not in payload
    )
    return issues


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
        import_cancelled: Callable[[], bool] | None = None,
    ) -> None:
        self._core = core
        self._p15_settings = P15SettingsCommands(core)
        self._stdin = stdin or sys.stdin
        self._stdout = stdout or sys.stdout
        # M2-DERIVED-GC-2: the canonical data root this Core owns (its
        # producer identity for preview origin registration). None keeps the
        # legacy behaviour -- previews publish catalog-only, never reclaimable.
        self._producer_root = str(producer_root.resolve()) if producer_root else None
        self._render_previews = render_previews
        self._import_cancelled = import_cancelled or (lambda: False)
        self._write_lock = threading.Lock()
        self._projection_lock = threading.Lock()
        self._projection_cache: dict[str, tuple[float, dict[str, Any]]] = {}
        self._owner_lock = threading.Lock()
        self._serving = False
        self._core_session_id = uuid.uuid4().hex
        self._host_session_id: str | None = None
        self._host_session_credential: str | None = None
        self._host_session_opened = False
        self._host_grants: dict[str, str] = {}
        self._run_owner = False
        self._run_scheduler_stop = threading.Event()
        self._run_scheduler_thread: threading.Thread | None = None
        self._scheduler_lease: _RunSchedulerLease | None = None
        self._exports = None
        if all(getattr(core, name, None) is not None for name in (
            "export_history_store", "export_job_store", "export_target_refs"
        )):
            self._exports = P16ExportRuntime(
                core.export_service, core.export_history_store, core.export_job_store,
                self._emit_export_progress_event,
            )
        pipeline = getattr(self._core, "pipeline", None)
        if pipeline is not None:
            pipeline.require_scheduler_owner()

    def _start_run_scheduler(self) -> None:
        if self._scheduler_lease is not None:
            return
        path = self._core.database_path.with_name(
            self._core.database_path.name + ".run-owner.lock"
        )
        lease = _RunSchedulerLease(path)
        if not lease.acquire():
            self._run_owner = False
            return
        try:
            self._core.pipeline.set_scheduler_owner(True)
            self._core.pipeline.recover_running_runs()
            self._core.pipeline.set_event_sink(self._emit_run_event)
            self._scheduler_lease = lease
            self._run_owner = True
            self._run_scheduler_thread = threading.Thread(
                target=self._run_scheduler_loop,
                name="core-run-scheduler",
                daemon=True,
            )
            self._run_scheduler_thread.start()
        except BaseException:
            self._core.pipeline.set_scheduler_owner(False)
            lease.release()
            raise

    def _run_scheduler_loop(self) -> None:
        try:
            while not self._run_scheduler_stop.is_set():
                try:
                    if self._core.pipeline.run_pending_once():
                        continue
                except Exception as error:
                    print(
                        f"[core.run_scheduler] {type(error).__name__}",
                        file=sys.stderr,
                        flush=True,
                    )
                self._run_scheduler_stop.wait(0.25)
        finally:
            if self._run_scheduler_stop.is_set():
                self._release_scheduler_lease()

    def _release_scheduler_lease(self) -> None:
        with self._owner_lock:
            lease, self._scheduler_lease = self._scheduler_lease, None
            self._core.pipeline.set_scheduler_owner(False)
            if lease is not None:
                lease.release()
            self._run_owner = False

    def _stop_run_scheduler(self) -> None:
        self._run_scheduler_stop.set()
        worker = self._run_scheduler_thread
        if worker is not None:
            worker.join()
        if worker is None or not worker.is_alive():
            self._core.pipeline.set_event_sink(None)
            self._release_scheduler_lease()

    def close(self) -> None:
        """Invalidate host grants and release the scheduler lease."""
        try:
            self._invalidate_host_session()
        finally:
            self._stop_run_scheduler()

    def _host_control_response(
        self, request_id: Any, result: dict[str, Any] | None,
        error: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return {
            "protocol": PROTOCOL_NAME,
            "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
            "request_id": request_id if isinstance(request_id, str) else None,
            "result": result,
            "error": error,
        }

    def _reject_host_control(
        self, request_id: Any, code: str, category: str, message: str,
    ) -> dict[str, Any]:
        return self._host_control_response(
            request_id, None, make_error_envelope(code, category, message)
        )

    @staticmethod
    def _valid_host_credential(value: object) -> bool:
        if not isinstance(value, str) or len(value) not in {43, 44} or not value.isascii():
            return False
        try:
            decoded = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
        except (ValueError, UnicodeError):
            return False
        encoded = base64.urlsafe_b64encode(decoded).decode("ascii")
        return (
            len(decoded) == 32
            and value in {encoded, encoded.rstrip("=")}
        )

    def _invalidate_host_session(self) -> None:
        if self._host_session_credential is None:
            return
        for grant_id, kind in tuple(self._host_grants.items()):
            if kind == "import":
                self._revoke_import_source({"grant_id": grant_id})
            else:
                self._revoke_export_target({"grant_id": grant_id})
        self._host_session_credential = None

    def _dispatch_host_control(self, request: dict[str, Any]) -> dict[str, Any]:
        request_id = request.get("request_id")
        command = request.get("command")
        open_fields = {"protocol", "version", "request_id", "channel", "command", "payload"}
        session_fields = {
            "protocol", "version", "request_id", "channel", "core_session_id",
            "host_session_id", "host_session_credential", "command", "payload",
        }
        if command == "OpenHostSession":
            if set(request) != open_fields:
                return self._reject_host_control(request_id, "INVALID_REQUEST", "validation", "Host control request is invalid")
        elif set(request) - session_fields:
            return self._reject_host_control(request_id, "INVALID_REQUEST", "validation", "Host control request is invalid")

        version = request.get("version")
        if (
            request.get("protocol") != PROTOCOL_NAME
            or not isinstance(version, dict)
            or set(version) != {"major", "minor"}
            or type(version.get("major")) is not int
            or type(version.get("minor")) is not int
            or version.get("minor") not in {PROTOCOL_MINOR, _P15_PROTOCOL_MINOR}
            or not isinstance(request_id, str)
            or not request_id
            or request.get("channel") != "host-control"
            or not isinstance(command, str)
            or command not in _HOST_CONTROL_COMMANDS
            or "payload" not in request
        ):
            return self._reject_host_control(request_id, "INVALID_REQUEST", "validation", "Host control request is invalid")

        payload = request.get("payload")
        if command == "OpenHostSession":
            if self._host_session_opened:
                return self._reject_host_control(request_id, "HOST_SESSION_ALREADY_OPENED", "conflict", "Host session was already opened")
            if (
                not isinstance(payload, dict)
                or set(payload) != {"host_session_id", "host_session_credential"}
                or not isinstance(payload.get("host_session_id"), str)
                or not payload["host_session_id"]
                or not self._valid_host_credential(payload.get("host_session_credential"))
            ):
                return self._reject_host_control(request_id, "INVALID_REQUEST", "validation", "Host session request is invalid")
            self._host_session_id = payload["host_session_id"]
            self._host_session_credential = payload["host_session_credential"]
            self._host_session_opened = True
            return self._host_control_response(
                request_id, {"core_session_id": self._core_session_id}, None
            )

        if "core_session_id" not in request or request.get("core_session_id") != self._core_session_id:
            return self._reject_host_control(request_id, "CORE_SESSION_MISMATCH", "conflict", "Core session does not match")
        if "host_session_id" not in request or self._host_session_credential is None:
            return self._reject_host_control(request_id, "HOST_SESSION_INVALID", "conflict", "Host session is invalid")
        credential = request.get("host_session_credential")
        if (
            not isinstance(credential, str)
            or not hmac.compare_digest(
                credential.encode("utf-8"), self._host_session_credential.encode("utf-8")
            )
            or request.get("host_session_id") != self._host_session_id
        ):
            return self._reject_host_control(request_id, "HOST_SESSION_INVALID", "conflict", "Host session is invalid")

        if command == "CloseHostSession":
            if not isinstance(payload, dict) or payload:
                return self._reject_host_control(request_id, "INVALID_REQUEST", "validation", "Host session request is invalid")
            try:
                self._invalidate_host_session()
            except Exception:
                return self._reject_host_control(request_id, "UNKNOWN", "internal", "Host session could not be closed")
            return self._host_control_response(request_id, {"closed": True}, None)

        if command not in _HOST_CONTROL_COMMANDS - {"OpenHostSession", "CloseHostSession"}:
            return self._reject_host_control(request_id, "INVALID_REQUEST", "validation", "Host control request is invalid")
        is_import = command.endswith("ImportSource")
        is_register = command.startswith("Register")
        if not isinstance(payload, dict):
            envelope = _import_ref_error_envelope("REF_MALFORMED") if is_import else _export_ref_error_envelope("REF_MALFORMED")
            return self._host_control_response(request_id, None, envelope)
        if is_register and "session_id" in payload and payload["session_id"] != self._host_session_id:
            envelope = _import_ref_error_envelope("REF_SCOPE_DENIED") if is_import else _export_ref_error_envelope("REF_SCOPE_DENIED")
            return self._host_control_response(request_id, None, envelope)
        grant_id = payload.get("grant_id")
        if is_register and isinstance(grant_id, str) and grant_id in self._host_grants:
            return self._reject_host_control(request_id, "GRANT_ALREADY_REGISTERED", "conflict", "Grant is already registered")
        if not is_register and set(payload) == {"grant_id"} and isinstance(grant_id, str) and grant_id not in self._host_grants:
            envelope = _import_ref_error_envelope("REF_UNKNOWN_ID") if is_import else _export_ref_error_envelope("REF_UNKNOWN_ID")
            return self._host_control_response(request_id, None, envelope)

        try:
            if command == "RegisterImportSource":
                result = self._register_import_source(payload)
            elif command == "RevokeImportSource":
                result = self._revoke_import_source(payload)
            elif command == "RegisterExportTarget":
                result = self._register_export_target(payload)
            else:
                result = self._revoke_export_target(payload)
        except TypedResourceChannelError as error:
            return self._host_control_response(request_id, None, _import_ref_error_envelope(error.code))
        except ExportTargetRefError as error:
            return self._host_control_response(request_id, None, _export_ref_error_envelope(error.code))
        except Exception:
            return self._reject_host_control(request_id, "UNKNOWN", "internal", "Host control operation failed")

        if is_register and isinstance(grant_id, str):
            self._host_grants[grant_id] = "import" if is_import else "export"
        return self._host_control_response(request_id, result, None)

    def _emit_run_event(self, event_type: str, payload: Any) -> None:
        with self._projection_lock:
            self._projection_cache.pop(str(payload.get("run_id", "")), None)
        self._emit({
            "protocol": PROTOCOL_NAME,
            "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
            "event_id": uuid.uuid4().hex,
            "event_type": event_type,
            "emitted_at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "payload": dict(payload),
        })

    def _emit_export_progress_event(self, payload: dict[str, Any]) -> None:
        self._emit_p16_event("ExportProgressChanged", payload)

    def _emit_p16_event(self, event_type: str, payload: dict[str, Any]) -> None:
        self._emit({
            "protocol": PROTOCOL_NAME,
            "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
            "event_id": uuid.uuid4().hex,
            "event_type": event_type,
            "emitted_at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "payload": payload,
        })

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

    def handle_list_recycle_bin_books(
        self, payload: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """AC1 (R-007): the recycle bin face - every soft-deleted book.

        The set comes from the service's soft-delete query, never from the
        visible list.  The bin is defined by ``deleted`` being true, so an empty
        result means "nothing is soft-deleted" - it never means "nothing is
        visible" and never "the query failed".
        """
        del payload
        books = self._core.library.list_recycle_bin_books()
        page_counts = self._fetch_page_counts()

        summaries: list[dict[str, Any]] = []
        for book in books:
            dto = BookSummaryDto(
                book_id=book.book_id,
                title=book.title,
                original_title=book.original_title,
                is_favorite=bool(book.is_favorite),
                is_archived=bool(book.is_archived),
                # Same frozen None channel as ListBooks: a SQL miss is unknown
                # data, never a plausible-looking 0.
                page_count=page_counts.get(book.book_id),
                created_at=book.created_at,
                updated_at=book.updated_at,
            )
            summaries.append(asdict(dto))
        return summaries

    def handle_create_book(self, payload: dict[str, Any]) -> dict[str, Any]:
        book = self._core.library.create_book(payload["title"])
        return asdict(BookSummaryDto(
            book_id=book.book_id,
            title=book.title,
            original_title=book.original_title,
            is_favorite=book.is_favorite,
            is_archived=book.is_archived,
            page_count=None,
            created_at=book.created_at,
            updated_at=book.updated_at,
        ))

    def handle_create_chapter(self, payload: dict[str, Any]) -> dict[str, Any]:
        chapter = self._core.library.create_chapter(
            payload["book_id"],
            payload["title"],
            chapter_number=payload.get("chapter_number", ""),
        )
        return {
            "chapter_id": chapter.chapter_id,
            "title": chapter.title,
            "chapter_number": chapter.chapter_number,
            "sort_order": chapter.sort_order,
        }

    def handle_permanently_delete_book(
        self, raw_payload: Any
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        if not isinstance(raw_payload, dict):
            return None, {"code": "INVALID_REQUEST", "category": "validation", "retryable": False}
        if set(raw_payload.keys()) != {"book_id", "confirm_permanent_delete"}:
            return None, {"code": "INVALID_REQUEST", "category": "validation", "retryable": False}
        book_id = raw_payload.get("book_id")
        if not isinstance(book_id, str) or not book_id.strip():
            return None, {"code": "INVALID_REQUEST", "category": "validation", "retryable": False}
        if raw_payload.get("confirm_permanent_delete") is not True:
            return None, {"code": "INVALID_REQUEST", "category": "validation", "retryable": False}

        repo = self._core.repository
        storage = self._core.storage

        with self._write_lock:
            all_ok, items = repo.preflight_permanent_delete(
                [book_id], storage=storage, export_runtime=self._exports
            )
            if not all_ok:
                code = items[0]["error_code"] or "BOOK_DELETE_CONFLICT"
                cat = "not_found" if code == "BOOK_NOT_FOUND" else "conflict"
                return None, {"code": code, "category": cat, "retryable": False}

            page_ids = repo.list_book_page_ids(book_id)
            if not page_ids:
                manifest_data = repo.get_cleanup_manifest_data(book_id)
                if manifest_data:
                    page_ids = manifest_data.get("page_ids", [])
            targets = repo.list_book_cleanup_targets(book_id)
            # AC4 (P09-PREVIEW-LIFECYCLE-RECLAIM-1): snapshot publish-style preview
            # keys while the artifact mapping still exists.  Measured in R189: the
            # publish key is preview-<uuid4> with rel_path previews/<key>.png, so it
            # cannot be found by name during cleanup, and preview_lifecycle is only
            # reachable via artifact_id, which the delete below removes.
            # Two databases, two halves (measured R189): media_artifacts is in
            # library.db, preview_lifecycle is in the catalog DB.  Querying the
            # latter from library.db raises "no such table".
            preview_resource_ids: list[str] = []
            preview_catalog = getattr(self._render_previews, "_catalog", None)
            if preview_catalog is not None:
                artifact_ids = repo.list_page_artifact_ids(page_ids)
                preview_resource_ids = preview_catalog.preview_resource_ids_for_artifacts(
                    artifact_ids
                )
            try:
                repo.execute_permanent_delete_db(
                    {book_id: targets},
                    {book_id: page_ids},
                    {book_id: preview_resource_ids},
                )
            except Exception:
                return None, {"code": "BOOK_DELETE_FAILED", "category": "internal", "retryable": "unknown"}

            cleaned = repo.cleanup_book_files(
                book_id,
                targets,
                storage,
                render_previews=self._render_previews,
                page_ids=page_ids,
                preview_resource_ids=preview_resource_ids,
            )
            if cleaned:
                return {"book_id": book_id, "deleted": True}, None
            return None, {"code": "BOOK_DELETE_CLEANUP_PENDING", "category": "internal", "retryable": True}

    def handle_permanently_delete_books(
        self, raw_payload: Any
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        if not isinstance(raw_payload, dict):
            return None, {"code": "INVALID_REQUEST", "category": "validation", "retryable": False}
        expected_keys = {"book_ids", "confirmed_book_ids", "confirm_count", "confirm_permanent_delete"}
        if set(raw_payload.keys()) != expected_keys:
            return None, {"code": "INVALID_REQUEST", "category": "validation", "retryable": False}

        book_ids = raw_payload.get("book_ids")
        confirmed_book_ids = raw_payload.get("confirmed_book_ids")
        confirm_count = raw_payload.get("confirm_count")
        confirm_permanent = raw_payload.get("confirm_permanent_delete")

        if not isinstance(book_ids, list) or not isinstance(confirmed_book_ids, list):
            return None, {"code": "INVALID_REQUEST", "category": "validation", "retryable": False}
        if not all(isinstance(bid, str) and bid.strip() for bid in book_ids):
            return None, {"code": "INVALID_REQUEST", "category": "validation", "retryable": False}
        if len(book_ids) == 0:
            return None, {"code": "INVALID_REQUEST", "category": "validation", "retryable": False}
        if len(book_ids) > 20:
            return None, {"code": "BOOK_DELETE_BATCH_LIMIT_EXCEEDED", "category": "validation", "retryable": False}
        if len(book_ids) != len(set(book_ids)):
            return None, {"code": "DUPLICATE_BOOK_ID", "category": "validation", "retryable": False}

        if type(confirm_count) is not int or confirm_count != len(book_ids):
            return None, {"code": "INVALID_REQUEST", "category": "validation", "retryable": False}
        if confirmed_book_ids != book_ids:
            return None, {"code": "INVALID_REQUEST", "category": "validation", "retryable": False}
        if confirm_permanent is not True:
            return None, {"code": "INVALID_REQUEST", "category": "validation", "retryable": False}

        repo = self._core.repository
        storage = self._core.storage

        with self._write_lock:
            if repo.is_whole_library(book_ids):
                return None, {"code": "BOOK_DELETE_BATCH_WHOLE_LIBRARY", "category": "conflict", "retryable": False}

            all_ok, items = repo.preflight_permanent_delete(
                book_ids, storage=storage, export_runtime=self._exports
            )
            if not all_ok:
                return None, {
                    "code": "BOOK_DELETE_BATCH_PREFLIGHT_FAILED",
                    "category": "conflict",
                    "retryable": False,
                    "details": {
                        "phase": "preflight",
                        "requested_count": len(book_ids),
                        "completed_count": 0,
                        "items": items,
                    },
                }

            book_page_ids_map = {}
            for bid in book_ids:
                pids = repo.list_book_page_ids(bid)
                if not pids:
                    mdata = repo.get_cleanup_manifest_data(bid)
                    if mdata:
                        pids = mdata.get("page_ids", [])
                book_page_ids_map[bid] = pids
            book_targets_map = {bid: repo.list_book_cleanup_targets(bid) for bid in book_ids}
            # AC4: same snapshot as the single-book path, and for the same reason -
            # preview_lifecycle is reached through artifact_id, and the delete below
            # removes media_artifacts.  Measured: without this, the batch path leaks
            # exactly as the single path did.
            preview_ids_map: dict[str, list[str]] = {}
            preview_catalog = getattr(self._render_previews, "_catalog", None)
            if preview_catalog is not None:
                for bid, pids in book_page_ids_map.items():
                    preview_ids_map[bid] = (
                        preview_catalog.preview_resource_ids_for_artifacts(
                            repo.list_page_artifact_ids(pids)
                        )
                    )
            try:
                repo.execute_permanent_delete_db(
                    book_targets_map, book_page_ids_map, preview_ids_map
                )
            except Exception:
                return None, {"code": "BOOK_DELETE_FAILED", "category": "internal", "retryable": "unknown"}

            result_items: list[dict[str, Any]] = []
            completed_count = 0
            has_pending = False
            for bid in book_ids:
                targets = book_targets_map[bid]
                pids = book_page_ids_map.get(bid, [])
                cleaned = repo.cleanup_book_files(
                    bid,
                    targets,
                    storage,
                    render_previews=self._render_previews,
                    page_ids=pids,
                    preview_resource_ids=preview_ids_map.get(bid, []),
                )
                if cleaned:
                    completed_count += 1
                    result_items.append({"book_id": bid, "status": "deleted", "error_code": None})
                else:
                    has_pending = True
                    result_items.append({"book_id": bid, "status": "cleanup_pending", "error_code": None})

            if not has_pending:
                return {
                    "requested_count": len(book_ids),
                    "completed_count": completed_count,
                    "items": result_items,
                }, None

            return None, {
                "code": "BOOK_DELETE_BATCH_CLEANUP_PENDING",
                "category": "internal",
                "retryable": True,
                "details": {
                    "phase": "cleanup",
                    "requested_count": len(book_ids),
                    "completed_count": completed_count,
                    "items": result_items,
                },
            }

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
                # DETECT-TILING-1 (r35): the rejection below already happens
                # BEFORE any pixel decode; what was missing was an actionable
                # message. Tiling is not an option here -- a PNG is a single
                # zlib stream, so cropping cannot avoid the full decode (see
                # verification/DETECT-TILING-1/stage1-decoder-memory.md).
                if image.width * image.height > MAX_DETECT_PIXELS:
                    width_px = image.width
                    height_px = image.height
                    pixels = width_px * height_px
                    # Square-equivalent edge for the current ceiling, so the
                    # caller gets a concrete target instead of a bare number.
                    ceiling_edge = int(MAX_DETECT_PIXELS ** 0.5)
                    raise DetectRequestError(
                        "core.detect page is too large to process safely: "
                        f"{width_px}x{height_px} = {pixels} px exceeds the "
                        f"{MAX_DETECT_PIXELS} px limit "
                        f"({pixels / MAX_DETECT_PIXELS:.2f}x over). "
                        "The page was rejected before any pixel decoding, so "
                        "no page-sized buffer was allocated. "
                        f"Reduce the page to at most {MAX_DETECT_PIXELS} pixels "
                        f"(about {ceiling_edge}x{ceiling_edge}) and retry, or "
                        "split a tall page into several shorter images."
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
            return {"settings": _project_settings_value(settings)}
        if not isinstance(section, str) or not section.strip():
            raise SettingsRequestError(
                "settings.get 'section' must be a non-empty string when present"
            )
        return {"settings": _project_settings_value({section: settings.get(section)})}

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
        return {"settings": _project_settings_value(dict(defaults.settings))}

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

    def _resolve_preview_origin_for_page(self, page: Any) -> PreviewOrigin | None:
        """AC4 (N-003): bind one translated reader page to its source revision.

        The reader path starts from the page rather than from a render outcome,
        so the artifact and its exact revision row are looked up by page plus
        managed path.  Same identity rule as :meth:`_resolve_preview_origin`:
        exactly one matching revision, and the stored identity is that row's
        ``artifact_revision_id``.

        Returns ``None`` when no single row matches.  That is deliberate: the
        caller then publishes with ``origin=None``, which is precisely the
        previous catalog-only behaviour.  A reader must never fail to open
        because an older translated artifact predates this binding.
        """
        if self._producer_root is None:
            return None
        try:
            # Match on identifiers, not on the path: the reader projection
            # exposes an absolute translated path while artifact_revisions
            # stores the managed path relative to the data root, so comparing
            # the two strings never matches and the origin silently stayed
            # None.  This test caught exactly that.
            #
            # F-002 (Codex R1): select managed_path as well.  PreviewOrigin's
            # managed_rel_path must be RELATIVE to producer_root - the GC
            # resolves the source as producer_root / managed_rel_path, so
            # storing the projection's absolute path made every verification
            # miss and the preview still could not be reclaimed even though it
            # now had a lifecycle row.  The revision row is the authority for
            # that relative path; the projection's absolute form is not.
            matching = self._core.conn.execute(
                "SELECT ar.artifact_revision_id, ar.artifact_id, ar.managed_path"
                " FROM artifact_revisions ar"
                " JOIN media_artifacts ma ON ma.artifact_id = ar.artifact_id"
                " WHERE ma.page_id = ? AND ma.artifact_type = 'translated'"
                "   AND ar.artifact_id = ? AND ar.artifact_revision_id = ?",
                (
                    page.page_id,
                    page.translated_artifact_id,
                    page.translated_revision_id,
                ),
            ).fetchall()
        except Exception as error:
            raise RuntimeError(f"preview origin: source lookup failed: {error!r}") from error
        if len(matching) != 1:
            return None
        stored_rel = matching[0]["managed_path"]
        if not isinstance(stored_rel, str) or not stored_rel:
            return None
        return PreviewOrigin(
            producer_root=self._producer_root,
            artifact_id=matching[0]["artifact_id"],
            artifact_revision_id=matching[0]["artifact_revision_id"],
            managed_rel_path=stored_rel,
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

    def handle_get_reader_projection(self, payload: dict[str, Any]) -> dict[str, Any]:
        if set(payload) != {"chapter_id", "mode", "start_position"}:
            raise P16WireError("INVALID_REQUEST", "validation", "Reader request is invalid")
        chapter_id, mode, start = payload.get("chapter_id"), payload.get("mode"), payload.get("start_position")
        if not isinstance(chapter_id, str) or not chapter_id or mode not in ("original", "translated") or start not in ("resume", "beginning"):
            raise P16WireError("INVALID_REQUEST", "validation", "Reader request is invalid")
        chapter = self._core.repository.get_chapter(chapter_id)
        if chapter is None:
            raise P16WireError("TARGET_NOT_FOUND", "not_found", "Reader chapter was not found")
        pages = self._core.reader_catalog.list_pages(chapter_id)
        if not pages or any(page.width_px <= 0 or page.height_px <= 0 for page in pages):
            raise P16WireError("TARGET_NOT_FOUND", "not_found", "Reader pages are unavailable")
        webtoon = chapter.chapter_type.value == "webtoon"
        layout = "webtoon_vertical" if webtoon else chapter.reading_direction.value
        projection_pages = []
        for order, page in enumerate(pages):
            original = self.handle_resolve_page_resource({"page_id": page.page_id})
            translated = None
            if page.translated_path and page.translated_revision_id:
                translated_path = self._checked_managed_path(page.translated_path)
                if self._render_previews is None or not translated_path.is_file():
                    raise P16WireError("EXPORT_INPUT_UNAVAILABLE", "unavailable", "Reader artifact is unavailable")
                # AC4 (N-003): publish WITH an origin so the preview lands in
                # preview_lifecycle and can be reclaimed by reference.  Without
                # it the row is catalog-only - which the publisher itself
                # documents as "never reclaimable" - so every translated read
                # leaked one permanent artifact per page, and the permanent
                # delete could not find any of them because cleanup only knows
                # the deterministic page-original key.  Passes None when no
                # single source revision matches, which keeps the previous
                # behaviour and never blocks the reader from opening.
                translated = self._render_previews.publish(
                    translated_path,
                    page.translated_revision_id,
                    origin=self._resolve_preview_origin_for_page(page),
                )
            projection_pages.append({
                "page_id": page.page_id, "order": order,
                "width_px": page.width_px, "height_px": page.height_px,
                "original": {
                    "resource_ref": original,
                    "artifact_revision_id": page.original_revision_id or page.page_id,
                    "sha256": self._reader_sha256(page.original_path, page.original_sha256),
                },
                "translated": {
                    "resource_ref": translated,
                    "artifact_revision_id": page.translated_revision_id if translated else None,
                    "rendered_from_revision_id": page.rendered_from_revision_id if translated else None,
                    "current_source_revision_id": page.current_source_revision_id if translated else None,
                    "sha256": self._reader_sha256(page.translated_path, page.translated_sha256) if translated else None,
                },
            })
        book_id = chapter.book_id
        saved = self._core.reading.progress_snapshot(book_id, chapter_id, mode)
        first = pages[0].page_id
        initial = {"page_id": first, "scroll_offset_y": 0.0}
        if start == "resume" and saved and saved.get("last_page_id") in {p.page_id for p in pages}:
            initial = {
                "page_id": saved["last_page_id"],
                "scroll_offset_y": saved["scroll_offset_y"] if webtoon else 0.0,
            }
        return {
            "book_id": book_id, "chapter_id": chapter_id, "mode": mode,
            "layout": layout, "pages": projection_pages,
            "saved_progress": saved, "initial_position": initial,
        }

    def handle_save_reading_progress(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = {"chapter_id", "mode", "page_id"}
        if not required.issubset(payload) or set(payload) - required - {"scroll_offset_y", "elapsed_seconds_delta"}:
            raise P16WireError("INVALID_REQUEST", "validation", "Reading progress request is invalid")
        chapter_id, mode, page_id = payload.get("chapter_id"), payload.get("mode"), payload.get("page_id")
        if not all(isinstance(value, str) and value for value in (chapter_id, page_id)) or mode not in ("original", "translated"):
            raise P16WireError("INVALID_REQUEST", "validation", "Reading progress request is invalid")
        chapter = self._core.repository.get_chapter(chapter_id)
        if chapter is None:
            raise P16WireError("TARGET_NOT_FOUND", "not_found", "Reader chapter was not found")
        pages = self._core.reader_catalog.list_pages(chapter_id)
        if not any(page.page_id == page_id for page in pages):
            raise P16WireError("TARGET_NOT_FOUND", "not_found", "Reader page was not found")
        try:
            result = self._core.reading.save_progress_snapshot(
                chapter.book_id, chapter_id, mode, page_id,
                payload.get("scroll_offset_y", 0), payload.get("elapsed_seconds_delta", 0),
                pages, webtoon=chapter.chapter_type.value == "webtoon",
            )
        except (TypeError, ValueError, OverflowError) as error:
            raise P16WireError("INVALID_REQUEST", "validation", "Reading progress values are invalid") from error
        self._emit_p16_event("ReadingProgressChanged", {
            "book_id": chapter.book_id, "chapter_id": chapter_id, "mode": mode,
        })
        return result

    def _register_export_target(self, payload: dict[str, Any]) -> dict[str, Any]:
        fields = {"grant_id", "session_id", "target_path", "format", "replace_existing", "expires_at", "signing_key", "signature"}
        if set(payload) != fields:
            raise ExportTargetRefError("REF_MALFORMED")
        try:
            signing_key = base64.urlsafe_b64decode(payload["signing_key"] + "=" * (-len(payload["signing_key"]) % 4))
            self._core.export_target_refs.register(
                grant_id=payload["grant_id"], session_id=payload["session_id"],
                target_path=payload["target_path"], format=payload["format"],
                replace_existing=payload["replace_existing"], expires_at=payload["expires_at"],
                signing_key=signing_key, signature=payload["signature"],
            )
        except ExportTargetRefError:
            raise
        except Exception as error:
            raise ExportTargetRefError("REF_MALFORMED") from error
        return {"registered": True}

    def _revoke_export_target(self, payload: dict[str, Any]) -> dict[str, Any]:
        if set(payload) != {"grant_id"} or not isinstance(payload.get("grant_id"), str):
            raise ExportTargetRefError("REF_MALFORMED")
        self._core.export_target_refs.revoke(payload["grant_id"])
        return {"revoked": True}

    def _register_import_source(self, payload: dict[str, Any]) -> dict[str, Any]:
        fields = {
            "grant_id", "session_id", "scope_class", "operation", "access",
            "source_path", "source_kind", "scope_identity", "entries",
            "expires_at", "signing_key", "signature",
        }
        if set(payload) != fields:
            raise TypedResourceChannelError("REF_MALFORMED")
        registry = getattr(self._core, "import_source_refs", None)
        if registry is None:
            raise TypedResourceChannelError("REF_SIGNATURE_INVALID")
        try:
            key_text = payload["signing_key"]
            if not isinstance(key_text, str):
                raise ValueError("invalid host key")
            signing_key = base64.urlsafe_b64decode(key_text + "=" * (-len(key_text) % 4))
            registry.register(
                grant_id=payload["grant_id"],
                session_id=payload["session_id"],
                scope_class=payload["scope_class"],
                operation=payload["operation"],
                access=payload["access"],
                source_path=payload["source_path"],
                source_kind=payload["source_kind"],
                scope_identity=payload["scope_identity"],
                entries=payload["entries"],
                expires_at=payload["expires_at"],
                signing_key=signing_key,
                signature=payload["signature"],
            )
        except TypedResourceChannelError:
            raise
        except Exception as error:
            raise TypedResourceChannelError("REF_MALFORMED") from error
        return {"registered": True}

    def _revoke_import_source(self, payload: dict[str, Any]) -> dict[str, Any]:
        if set(payload) != {"grant_id"} or not isinstance(payload.get("grant_id"), str):
            raise TypedResourceChannelError("REF_MALFORMED")
        registry = getattr(self._core, "import_source_refs", None)
        if registry is None:
            raise TypedResourceChannelError("REF_UNKNOWN_ID")
        registry.revoke(payload["grant_id"])
        return {"revoked": True}

    def handle_import_pages(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = {"chapter_id", "sources"}
        if (
            not required.issubset(payload)
            or set(payload) - required - {"duplicate_policy"}
        ):
            raise P16WireError("INVALID_REQUEST", "validation", "Import request is invalid")
        chapter_id = payload["chapter_id"]
        sources = payload["sources"]
        duplicate_policy = payload.get("duplicate_policy", DuplicatePolicy.SKIP)
        if (
            not isinstance(chapter_id, str) or not chapter_id
            or not isinstance(sources, list) or not sources
            or duplicate_policy not in (
                DuplicatePolicy.SKIP, DuplicatePolicy.IMPORT_AS_NEW
            )
        ):
            raise P16WireError("INVALID_REQUEST", "validation", "Import request is invalid")
        if self._core.repository.get_chapter(chapter_id) is None:
            raise P16WireError("TARGET_NOT_FOUND", "not_found", "Import chapter was not found")
        registry = getattr(self._core, "import_source_refs", None)
        if registry is None:
            raise TypedResourceChannelError("REF_SIGNATURE_INVALID")

        selections = registry.resolve_many(sources)
        source_results: list[dict[str, Any]] = []
        cancelled = False
        try:
            for selection in selections:
                file_results = []
                for source_file in selection.files:
                    try:
                        should_cancel = bool(self._import_cancelled())
                    except Exception:
                        should_cancel = True
                    if should_cancel:
                        cancelled = True
                        file_results.append({
                            "filename": source_file.filename,
                            "outcome": "pending",
                            "source_sha256": None,
                            "pages": [],
                            "error": None,
                            "side_effects": "none",
                        })
                        continue
                    result = self._import_one_file(
                        chapter_id, source_file, duplicate_policy
                    )
                    cancelled = cancelled or result.pop("_cancelled")
                    file_results.append(result)
                    source_file.release_data()
                source_results.append({
                    "source_index": selection.source_index,
                    "source_name": selection.source_name,
                    "files": file_results,
                })
        finally:
            for selection in selections:
                selection.close()
        return {
            "chapter_id": chapter_id,
            "duplicate_policy": duplicate_policy,
            "cancelled": cancelled,
            "sources": source_results,
        }

    def _import_one_file(
        self, chapter_id: str, source_file, duplicate_policy: str
    ) -> dict[str, Any]:
        filename = source_file.filename
        is_pdf = Path(filename).suffix.lower() == ".pdf"
        page_ids_before = {
            page.page_id for page in self._core.repository.list_pages(chapter_id)
        }
        existing_hashes = self._core.repository.existing_source_hashes(chapter_id)
        source = ImportSource(filename, source_file.read)
        try:
            if is_pdf:
                report = self._core.document_importer.import_documents(
                    chapter_id, [source], duplicate_policy=duplicate_policy,
                    cancelled=self._import_cancelled,
                )
                return self._pdf_import_result(
                    source_file, report, existing_hashes, duplicate_policy
                )
            report = self._core.importer.import_files(
                chapter_id, [source], duplicate_policy=duplicate_policy,
                cancelled=self._import_cancelled,
            )
            return self._image_import_result(
                source_file, report, existing_hashes
            )
        except Exception:
            committed = [
                page for page in self._core.repository.list_pages(chapter_id)
                if page.page_id not in page_ids_before
                and page.source_filename == filename
            ]
            pages = [
                _import_page_result(
                    index, "imported", page=page,
                    duplicate=page.source_hash in existing_hashes,
                    side_effects="page_committed",
                )
                for index, page in enumerate(
                    sorted(committed, key=lambda item: item.source_order), 1
                )
            ]
            return {
                "filename": filename,
                "outcome": "partial" if pages else "rejected",
                "source_sha256": source_file.facts.sha256 if source_file.data is not None else None,
                "pages": pages,
                "error": _import_item_error("UNKNOWN"),
                "side_effects": "managed_orphan_possible",
                "_cancelled": False,
            }

    def _image_import_result(self, source_file, report, existing_hashes: set[str]) -> dict[str, Any]:
        data = source_file.data
        source_sha = source_file.facts.sha256 if data is not None else None
        imported = list(report.imported)
        failed = list(report.failed)
        skipped = list(report.skipped_duplicates)
        pending = list(report.pending)
        pages = []
        seen_hashes = set(existing_hashes)
        for item in imported:
            page = item.page
            duplicate = page.source_hash in seen_hashes
            seen_hashes.add(page.source_hash)
            pages.append(_import_page_result(
                1, "imported", page=page, duplicate=duplicate,
                side_effects="page_committed",
            ))
        if skipped:
            try:
                decoded = self._core.image_decoder.decode(data) if data is not None else None
            except Exception:
                decoded = None
            pages.append(_import_page_result(
                1, "skipped_duplicate", sha256=source_sha,
                width=decoded.width if decoded else None,
                height=decoded.height if decoded else None,
                duplicate=True,
            ))
        error = _import_item_error(failed[0].reason) if failed else None
        if pending:
            pages.append(_import_page_result(1, "pending"))
        outcome = (
            "imported" if imported and not (failed or pending or skipped)
            else "partial" if imported
            else "skipped" if skipped
            else "pending" if pending
            else "rejected"
        )
        return {
            "filename": source_file.filename,
            "outcome": outcome,
            "source_sha256": source_sha,
            "pages": pages,
            "error": error,
            "side_effects": "listed_pages_committed" if imported else "none",
            "_cancelled": bool(report.cancelled),
        }

    def _pdf_import_result(
        self, source_file, report, existing_hashes: set[str], duplicate_policy: str
    ) -> dict[str, Any]:
        filename = source_file.filename
        data = source_file.data
        source_sha = source_file.facts.sha256 if data is not None else None
        failed = list(report.failed)
        imported = {
            _document_import_page_index(item.filename, filename): item.page
            for item in report.imported
        }
        imported.pop(None, None)
        pending_indexes = _pending_document_pages(list(report.pending))
        pages = []
        rendered_handle = None
        total = 0
        try:
            if data is not None:
                rendered_handle = self._core.document_raster.open(data)
                total = rendered_handle.page_count
            seen_hashes = set(existing_hashes)
            error_index_assigned = False
            for page_index in range(1, total + 1):
                page = imported.get(page_index)
                if page is not None:
                    duplicate = page.source_hash in seen_hashes
                    seen_hashes.add(page.source_hash)
                    pages.append(_import_page_result(
                        page_index, "imported", page=page, duplicate=duplicate,
                        side_effects="page_committed",
                    ))
                    continue
                try:
                    rendered = rendered_handle.render_page(page_index - 1)
                    page_hash = hashlib.sha256(rendered.png).hexdigest()
                    duplicate = page_hash in seen_hashes
                    seen_hashes.add(page_hash)
                except DocumentDecodeError as error:
                    pages.append(_import_page_result(
                        page_index, "rejected", error=_import_item_error(error.reason)
                    ))
                    continue
                if page_index in pending_indexes:
                    pages.append(_import_page_result(page_index, "pending"))
                elif duplicate and duplicate_policy == DuplicatePolicy.SKIP:
                    pages.append(_import_page_result(
                        page_index, "skipped_duplicate", sha256=page_hash,
                        width=rendered.width, height=rendered.height, duplicate=True,
                    ))
                elif failed and not error_index_assigned:
                    pages.append(_import_page_result(
                        page_index, "rejected", sha256=page_hash,
                        width=rendered.width, height=rendered.height,
                        duplicate=duplicate, error=_import_item_error(failed[0].reason),
                    ))
                    error_index_assigned = True
                else:
                    pages.append(_import_page_result(
                        page_index, "rejected", sha256=page_hash,
                        width=rendered.width, height=rendered.height,
                        duplicate=duplicate, error=_import_item_error("UNKNOWN"),
                    ))
        except DocumentDecodeError:
            pages = []
        finally:
            if rendered_handle is not None:
                rendered_handle.close()

        error = _import_item_error(failed[0].reason) if failed else None
        imported_count = sum(page["outcome"] == "imported" for page in pages)
        if pages and all(page["outcome"] == "imported" for page in pages):
            outcome = "imported"
        elif pages and all(page["outcome"] == "skipped_duplicate" for page in pages):
            outcome = "skipped"
        elif pages and all(page["outcome"] == "pending" for page in pages):
            outcome = "pending"
        elif imported_count:
            outcome = "partial"
        elif any(page["outcome"] == "rejected" for page in pages) or error:
            outcome = "rejected"
        elif pages:
            outcome = "partial"
        else:
            outcome = "pending" if report.cancelled else "rejected"
        return {
            "filename": filename,
            "outcome": outcome,
            "source_sha256": source_sha,
            "pages": pages,
            "error": error,
            "side_effects": (
                "listed_pages_committed" if imported_count else "none"
            ),
            "_cancelled": bool(report.cancelled),
        }

    def handle_start_export(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = {"book_id", "chapter_ids", "ordered_page_ids", "format", "format_options", "stale_policy", "target_ref"}
        if set(payload) != required:
            raise P16WireError("INVALID_REQUEST", "validation", "Export request is invalid")
        book_id, chapter_ids, ordered_ids = payload["book_id"], payload["chapter_ids"], payload["ordered_page_ids"]
        fmt, options, stale = payload["format"], payload["format_options"], payload["stale_policy"]
        if (not isinstance(book_id, str) or not book_id or not isinstance(chapter_ids, list) or not chapter_ids
                or not all(isinstance(item, str) and item for item in chapter_ids) or len(set(chapter_ids)) != len(chapter_ids)
                or not isinstance(ordered_ids, list) or not ordered_ids or not all(isinstance(item, str) and item for item in ordered_ids)
                or len(set(ordered_ids)) != len(ordered_ids) or fmt not in ("png", "zip", "cbz", "pdf", "text")
                or stale not in ("abort", "continue_existing")):
            raise P16WireError("INVALID_REQUEST", "validation", "Export request is invalid")
        self._validate_export_options(fmt, options)
        book = self._core.repository.get_book(book_id)
        if book is None:
            raise P16WireError("TARGET_NOT_FOUND", "not_found", "Export target was not found")
        chapters = {}
        pages_by_id = {}
        page_chapter = {}
        for chapter_id in chapter_ids:
            chapter = self._core.repository.get_chapter(chapter_id)
            if chapter is None or chapter.book_id != book_id:
                raise P16WireError("TARGET_NOT_FOUND", "not_found", "Export target was not found")
            chapters[chapter_id] = chapter
            for page in self._core.reader_catalog.list_pages(chapter_id):
                pages_by_id[page.page_id] = page
                page_chapter[page.page_id] = chapter_id
        if any(page_id not in pages_by_id for page_id in ordered_ids):
            raise P16WireError("TARGET_NOT_FOUND", "not_found", "Export page was not found")
        if fmt == "png" and len(ordered_ids) != 1:
            raise P16WireError("INVALID_REQUEST", "validation", "PNG export requires one page")
        selected = [pages_by_id[page_id] for page_id in ordered_ids]
        if any(not page.translated_path or not page.translated_revision_id or not page.translated_artifact_id for page in selected):
            raise P16WireError("EXPORT_INPUT_UNAVAILABLE", "unavailable", "A translated input is unavailable")
        lineage = []
        export_pages = []
        stale_details = []
        text_pages = []
        for order, page in enumerate(selected):
            translated_path = self._checked_managed_path(page.translated_path)
            if not translated_path.is_file():
                raise P16WireError("EXPORT_INPUT_UNAVAILABLE", "unavailable", "A translated input is unavailable")
            actual_hash = _sha256_file_path(translated_path)
            if page.translated_sha256 and actual_hash != page.translated_sha256:
                raise P16WireError("EXPORT_INPUT_UNAVAILABLE", "unavailable", "A translated input failed integrity verification")
            stale_page = bool(page.rendered_from_revision_id and page.current_source_revision_id and page.rendered_from_revision_id != page.current_source_revision_id)
            if stale_page:
                stale_details.append({"page_id": page.page_id, "reason": "stale"})
            regions = self._export_regions(page.page_id)
            item = {
                "page_id": page.page_id, "order": order,
                "source_artifact_id": page.translated_artifact_id,
                "source_artifact_revision_id": page.translated_revision_id,
                "source_sha256": actual_hash,
                "rendered_from_revision_id": page.rendered_from_revision_id,
                "current_source_revision_id": page.current_source_revision_id,
                "source_run_id": page.source_run_id, "stale": stale_page,
            }
            lineage.append(item)
            export_pages.append(ExportPage(
                page_id=page.page_id, filename=page.filename,
                source_provider=lambda p=page: Path(self._checked_managed_path(p.original_path)).read_bytes(),
                translated_provider=lambda p=translated_path: p.read_bytes(),
                translated_revision_id=page.translated_revision_id,
                current_translated_revision_id=page.current_translated_revision_id,
                rendered_from_revision_id=page.rendered_from_revision_id,
                current_source_revision_id=page.current_source_revision_id,
                regions=tuple(regions), sha256=actual_hash,
                artifact_id=page.translated_artifact_id,
                artifact_revision_id=page.translated_revision_id,
                source_run_id=page.source_run_id,
            ))
            text_pages.append({
                "page_id": page.page_id, "order": order, "filename": page.filename,
                "width_px": page.width_px, "height_px": page.height_px,
                "regions": regions,
            })
        target_ref = payload["target_ref"]
        registry = getattr(self._core, "export_target_refs", None)
        if registry is None:
            raise ExportTargetRefError("REF_SIGNATURE_INVALID")
        target = registry.resolve_and_consume(target_ref, fmt)
        if self._is_protected_export_target(target.path):
            raise ExportTargetRefError("REF_SCOPE_DENIED")
        if stale == "abort" and stale_details:
            raise P16WireError("EXPORT_STALE", "conflict", "Translated inputs are stale", details=stale_details)

        first_chapter = chapters[chapter_ids[0]]
        format_value = ExportFormat.SINGLE_IMAGE if fmt == "png" else ExportFormat(fmt)
        text_content = self._text_export_bytes(fmt, options, text_pages) if fmt == "text" else None
        request = ExportRequest(
            book_id=book_id, chapter_id=page_chapter[ordered_ids[0]],
            format=format_value, output_path=target.path, pages=tuple(export_pages),
            mode="translated", overwrite_policy=OverwritePolicy.OVERWRITE,
            stale_policy=StalePolicy.ABORT if stale == "abort" else StalePolicy.CONTINUE,
            format_options=options, text_content=text_content,
            book_metadata={"title": book.title, "author": book.author, "description": book.description},
            chapter_metadata={"title": first_chapter.title, "chapter_number": first_chapter.chapter_number, "chapter_ids": chapter_ids},
            lineage=tuple(lineage), image_encoder=encode_png,
        )
        if self._exports is None:
            raise P16WireError("EXPORT_WRITE_FAILED", "internal", "Export runtime is unavailable")
        try:
            return self._exports.start(request, target)
        except OSError as error:
            raise P16WireError("EXPORT_WRITE_FAILED", "internal", "Export could not be accepted") from error

    @staticmethod
    def _validate_export_options(fmt: str, options: Any) -> None:
        if not isinstance(options, dict):
            raise P16WireError("INVALID_REQUEST", "validation", "Export options are invalid")
        valid = ((fmt in ("png", "cbz") and options == {})
                 or (fmt == "zip" and set(options) == {"compression"} and options.get("compression") in ("standard", "fast", "store"))
                 or (fmt == "pdf" and set(options) == {"pdf_content"} and options.get("pdf_content") in ("image_only", "searchable_dual_layer"))
                 or (fmt == "text" and set(options) == {"text_representation"} and options.get("text_representation") in ("txt", "json", "markdown")))
        if not valid:
            raise P16WireError("INVALID_REQUEST", "validation", "Export options are invalid")

    def _checked_managed_path(self, path: str) -> Path:
        root = self._core.storage.root.resolve()
        resolved = Path(path).resolve()
        try:
            resolved.relative_to(root)
        except ValueError as error:
            raise P16WireError("EXPORT_INPUT_UNAVAILABLE", "unavailable", "Managed export input is unavailable") from error
        return resolved

    def _reader_sha256(self, path: str, expected: str | None) -> str:
        resolved = self._checked_managed_path(path)
        digest = _sha256_file_path(resolved)
        if expected and expected != digest:
            raise P16WireError("EXPORT_INPUT_UNAVAILABLE", "unavailable", "Reader input failed integrity verification")
        return digest

    def _export_regions(self, page_id: str) -> list[dict]:
        rows = self._core.conn.execute(
            "SELECT region_id, reading_order, geometry_json, text_json FROM regions"
            " WHERE page_id = ? AND deleted_at IS NULL ORDER BY reading_order, region_id",
            (page_id,),
        ).fetchall()
        result = []
        for row in rows:
            geometry, text = json.loads(row["geometry_json"]), json.loads(row["text_json"])
            result.append({
                "region_id": row["region_id"], "reading_order": row["reading_order"],
                "geometry": geometry, "ocr_text": text.get("ocr_text", ""),
                "translated_text": text.get("final_translation") or text.get("machine_translation", ""),
            })
        return result

    def _text_export_bytes(self, fmt: str, options: dict, pages: list[dict]) -> bytes:
        rep = options["text_representation"]
        if rep == "json":
            return json.dumps({"pages": pages}, ensure_ascii=False, indent=2).encode("utf-8")
        blocks = []
        for page in pages:
            lines = [f"{region['ocr_text']}\n{region['translated_text']}".strip() for region in page["regions"]]
            body = "\n\n".join(line for line in lines if line)
            blocks.append((f"# {page['filename']}\n\n" + body) if rep == "markdown" else (f"[{page['filename']}]\n" + body))
        return ("\n\n".join(blocks) + "\n").encode("utf-8")

    def _is_protected_export_target(self, target: Path) -> bool:
        root = self._core.storage.root.resolve()
        target = target.parent.resolve() / target.name
        rows = self._core.conn.execute(
            "SELECT managed_original_ref AS path FROM pages WHERE managed_original_ref IS NOT NULL"
            " UNION ALL SELECT managed_path AS path FROM artifact_revisions"
        ).fetchall()
        for row in rows:
            path = Path(self._core.storage.absolute_path(row["path"])).resolve()
            try:
                path.relative_to(root)
            except ValueError:
                continue
            if os.path.normcase(str(path)) == os.path.normcase(str(target)):
                return True
        return False

    @staticmethod
    def _is_positive_integer(value: Any) -> bool:
        return isinstance(value, int) and not isinstance(value, bool) and value > 0

    @staticmethod
    def _required_run_id(payload: dict[str, Any]) -> str:
        value = payload.get("run_id")
        if not isinstance(value, str) or not value:
            raise PipelineError("INVALID_REQUEST", "run_id must be a non-empty string")
        return value

    @staticmethod
    def _parse_run_scope(value: Any) -> PipelineScope:
        if not isinstance(value, dict) or not isinstance(value.get("kind"), str):
            raise PipelineError("INVALID_REQUEST", "scope must be a PipelineScope object")
        kind = value["kind"]
        if kind == "book" and set(value) == {"kind", "book_id"}:
            book_id = value.get("book_id")
            if isinstance(book_id, str) and book_id:
                return PipelineScope(ScopeType.BOOK, book_id=book_id)
        elif kind == "chapter" and set(value) == {"kind", "chapter_id"}:
            chapter_id = value.get("chapter_id")
            if isinstance(chapter_id, str) and chapter_id:
                return PipelineScope(ScopeType.CHAPTER, chapter_id=chapter_id)
        elif kind == "page_selection" and set(value) == {"kind", "page_ids"}:
            page_ids = value.get("page_ids")
            if (
                isinstance(page_ids, list)
                and page_ids
                and all(isinstance(item, str) and item for item in page_ids)
                and len(set(page_ids)) == len(page_ids)
            ):
                return PipelineScope(ScopeType.PAGE_SELECTION, selected_ids=tuple(page_ids))
        elif kind == "page" and set(value) == {"kind", "page_id"}:
            page_id = value.get("page_id")
            if isinstance(page_id, str) and page_id:
                return PipelineScope(ScopeType.PAGE, selected_ids=(page_id,))
        elif kind == "region" and set(value) == {"kind", "region_id"}:
            region_id = value.get("region_id")
            if isinstance(region_id, str) and region_id:
                return PipelineScope(ScopeType.REGION, selected_ids=(region_id,))
        raise PipelineError("INVALID_REQUEST", "scope does not match a frozen PipelineScope variant")

    @staticmethod
    def _scope_to_wire(scope: PipelineScope) -> dict[str, Any]:
        if scope.scope_type is ScopeType.BOOK:
            return {"kind": "book", "book_id": scope.book_id}
        if scope.scope_type is ScopeType.CHAPTER:
            return {"kind": "chapter", "chapter_id": scope.chapter_id}
        if scope.scope_type is ScopeType.PAGE_SELECTION:
            return {"kind": "page_selection", "page_ids": list(scope.selected_ids)}
        if scope.scope_type is ScopeType.PAGE:
            return {"kind": "page", "page_id": scope.selected_ids[0]}
        return {"kind": "region", "region_id": scope.selected_ids[0]}

    @staticmethod
    def _task_projection_to_wire(projection) -> dict[str, Any]:
        return {
            "run_id": projection.run_id,
            "run_status": projection.run_status,
            "run_title": projection.run_title,
            "overall_progress": projection.overall_progress,
            "current_page_id": projection.current_page_id,
            "current_step_type": projection.current_step_type,
            "step_flow": [
                {"type": step_type, "label": label, "state": state}
                for step_type, label, state in projection.step_flow
            ],
            "rows": [
                {
                    "page_id": row.page_id,
                    "page_order": row.page_order,
                    "filename": row.filename,
                    "status": row.status,
                    "is_locked": row.is_locked,
                    "is_pipeline_current": row.is_pipeline_current,
                    "error_code": row.error_code,
                }
                for row in projection.rows
            ],
            "tasks": [
                {
                    "task_id": task.task_id,
                    "page_id": task.page_id,
                    "status": task.status,
                    "error_code": task.error_code,
                    "error_message": task.error_message,
                    "steps": [
                        {
                            "step_run_id": step.step_run_id,
                            "step_type": step.step_type,
                            "status": step.status,
                            "retry_no": step.retry_no,
                            "error_code": step.error_code,
                            "error_message": step.error_message,
                            "provider": step.provider,
                            "model": step.model,
                            "device": step.device,
                        }
                        for step in task.steps
                    ],
                }
                for task in projection.tasks
            ],
            "counts": {
                "total": projection.total_page_count,
                "completed": projection.completed_page_count,
                "failed": projection.failed_page_count,
                "skipped": projection.skipped_page_count,
                "blocked": projection.blocked_page_count,
                "waiting": projection.waiting_page_count,
                "processing": projection.processing_page_count,
            },
            "blocked_reasons": list(projection.blocked_reasons),
            "controls": {
                "can_pause": projection.can_pause,
                "can_stop": projection.can_stop,
                "can_continue": projection.can_continue,
                "can_restart": projection.can_restart,
                "can_abandon": projection.can_abandon,
                "can_retry_failed": projection.can_retry_failed,
            },
            "extra": dict(projection.extra),
        }

    def _cached_task_projection(self, run_id: str) -> dict[str, Any]:
        now = time.monotonic()
        with self._projection_lock:
            cached = self._projection_cache.get(run_id)
            if cached is not None and now - cached[0] < 0.25:
                return cached[1]
        wire = self._task_projection_to_wire(
            self._core.pipeline.get_task_projection(run_id, fresh=True)
        )
        with self._projection_lock:
            self._projection_cache[run_id] = (now, wire)
        return wire

    def _dispatch_run_command(
        self,
        command: str,
        payload: dict[str, Any],
        request_id: Any,
        *,
        payload_is_object: bool,
        protocol_minor: int,
    ) -> tuple[dict[str, Any], bool]:
        try:
            if not payload_is_object:
                raise PipelineError("INVALID_REQUEST", "payload must be a JSON object")
            if command in {"StartRun", "ControlRun", "ResumeBlockedRun", "RetryFailedTargets"}:
                if not self._run_owner and not self._serving:
                    self._start_run_scheduler()
                if not self._run_owner:
                    raise PipelineError("INVALID_RUN_TRANSITION", "Run scheduler owner is unavailable")
            if command == "StartRun":
                raw_command = payload.get("command")
                key = payload.get("idempotency_key")
                if not isinstance(raw_command, str) or raw_command not in COMMAND_CATALOG:
                    raise PipelineError("INVALID_REQUEST", "command is not a frozen PipelineCommand")
                if not isinstance(key, str) or not key:
                    raise PipelineError("INVALID_REQUEST", "idempotency_key is required")
                overrides = payload.get("overrides", {})
                if not isinstance(overrides, dict):
                    raise PipelineError("INVALID_REQUEST", "overrides must be a JSON object")
                if "provider_profiles" in overrides and protocol_minor != _P15_PROTOCOL_MINOR:
                    raise PipelineError("INVALID_REQUEST", "provider profile overrides require Core 2.6")
                scope = self._parse_run_scope(payload.get("scope"))
                snapshot_provider_bindings = None
                if protocol_minor == _P15_PROTOCOL_MINOR:
                    snapshot_provider_bindings = {
                        P15_SNAPSHOT_KEY: self._p15_settings.prepare_run_snapshot(scope, overrides)
                    }
                run, created = self._core.pipeline.accept_start_run(
                    CommandType(raw_command), scope,
                    overrides=overrides,
                    idempotency_key=key,
                    snapshot_provider_bindings=snapshot_provider_bindings,
                )
                result = {
                    "run_id": run.run_id,
                    "status": "pending" if created else run.status.value,
                }
            elif command == "ControlRun":
                run_id = self._required_run_id(payload)
                action = payload.get("action")
                actions = {"pause", "continue", "stop", "restart", "abandon"}
                if not isinstance(action, str) or action not in actions:
                    raise PipelineError("INVALID_REQUEST", "action is not a frozen ControlRun action")
                key = payload.get("idempotency_key")
                if action == "restart":
                    if not isinstance(key, str) or not key:
                        raise PipelineError("INVALID_REQUEST", "restart requires idempotency_key")
                elif "idempotency_key" in payload:
                    raise PipelineError("INVALID_REQUEST", "idempotency_key is only valid for restart")
                controlled = self._core.pipeline.control_run(
                    run_id, action,
                    idempotency_key=key if action == "restart" else None,
                )
                result = {"run_id": controlled.run_id, "status": controlled.status.value}
                if controlled.new_run_id is not None:
                    child = self._core.pipeline.get_run_snapshot(controlled.new_run_id)
                    result["new_run_id"] = child.run_id
                    result["new_run_status"] = child.status.value
            elif command == "ResumeBlockedRun":
                if "idempotency_key" in payload:
                    raise PipelineError("INVALID_REQUEST", "ResumeBlockedRun does not accept idempotency_key")
                run = self._core.pipeline.resume_blocked_run(self._required_run_id(payload))
                result = {"run_id": run.run_id, "status": run.status.value}
            elif command == "GetRunSnapshot":
                run = self._core.pipeline.get_run_snapshot(
                    self._required_run_id(payload),
                    fresh=self._serving and not self._run_owner,
                )
                targets = [
                    {
                        "target_id": target.target_id,
                        "target_type": target.target_type.value,
                        "order": target.target_order,
                    }
                    for target in run.targets
                ]
                result = {
                    "run_id": run.run_id,
                    "command": run.command_type.value,
                    "scope": self._scope_to_wire(run.scope),
                    "status": run.status.value,
                    "targets": targets,
                }
                if run.source_run_id is not None:
                    result["source_run_id"] = run.source_run_id
                if run.retry_reason is not None:
                    result["retry_reason"] = run.retry_reason
            elif command == "GetTaskProjection":
                result = self._cached_task_projection(
                    self._required_run_id(payload)
                )
            else:
                run_id = self._required_run_id(payload)
                key = payload.get("idempotency_key")
                if not isinstance(key, str) or not key:
                    raise PipelineError("INVALID_REQUEST", "idempotency_key is required")
                child, created = self._core.pipeline.accept_retry_failed_targets(run_id, key)
                result = {
                    "run_id": child.run_id,
                    "status": "pending" if created else child.status.value,
                }
            response = {
                "protocol": PROTOCOL_NAME,
                "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                "request_id": request_id,
                "result": result,
                "error": None,
            }
        except SettingsSurfaceError as error:
            code = {
                "validation": E_INVALID_REQUEST,
                "not_found": E_TARGET_NOT_FOUND,
                "conflict": "SETTINGS_CONFLICT",
                "unavailable": "SETTINGS_UNAVAILABLE",
            }[error.category]
            response = {
                "protocol": PROTOCOL_NAME,
                "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                "request_id": request_id,
                "result": None,
                "error": make_error_envelope(
                    code, error.category, error.message_key,
                    retryable=False, details=error.details,
                ),
            }
        except PipelineError as error:
            code = error.code
            if code in {"EMPTY_TARGET_SELECTION", "TARGET_DELETED"}:
                code = "INVALID_REQUEST" if code == "EMPTY_TARGET_SELECTION" else "TARGET_NOT_FOUND"
            category = {
                "INVALID_REQUEST": "validation",
                "TARGET_NOT_FOUND": "not_found",
                "IDEMPOTENCY_KEY_REUSED": "conflict",
                "INVALID_RUN_TRANSITION": "conflict",
            }.get(code, "validation")
            message = {
                "INVALID_REQUEST": "Run request is invalid",
                "TARGET_NOT_FOUND": "Requested Run or target was not found",
                "IDEMPOTENCY_KEY_REUSED": "Idempotency key was used for a different request",
                "INVALID_RUN_TRANSITION": "Run operation is not valid in the current state",
            }.get(code, "Run request could not be accepted")
            response = {
                "protocol": PROTOCOL_NAME,
                "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                "request_id": request_id,
                "result": None,
                "error": make_error_envelope(code, category, message, retryable=False),
            }
        except Exception as error:
            code = getattr(error, "code", "UNKNOWN")
            response = {
                "protocol": PROTOCOL_NAME,
                "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                "request_id": request_id,
                "result": None,
                "error": make_error_envelope(
                    str(code), "internal", "Run operation failed", retryable=False
                ),
            }
        return response, False

    def _dispatch_request(self, raw_line: str) -> tuple[dict[str, Any], bool]:
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
        safe_request_id = (
            _project_settings_value(request_id)
            if command in ("settings.get", "settings.update_section")
            else request_id
        )
        raw_payload = req.get("payload")
        payload = raw_payload if isinstance(raw_payload, dict) else {}

        if req.get("channel") == "host-control":
            if command in ("settings.get", "settings.update_section"):
                req = {**req, "request_id": safe_request_id}
            return self._dispatch_host_control(req), False
        if isinstance(command, str) and command in _HOST_CONTROL_COMMANDS:
            return self._reject_host_control(
                request_id, "HOST_ONLY_REQUIRED", "validation",
                "Host control channel is required",
            ), False

        # Validate protocol name and version (must be dict with integer major == PROTOCOL_MAJOR)
        is_valid_version = (
            isinstance(version, dict)
            and isinstance(version.get("major"), int)
            and not isinstance(version.get("major"), bool)
            and version.get("major") == PROTOCOL_MAJOR
        )
        if command in _CREATE_COMMANDS:
            result = None
            error = None
            if protocol != PROTOCOL_NAME or not is_valid_version:
                error = {
                    "code": "PROTOCOL_VERSION_UNSUPPORTED",
                    "category": "validation",
                    "retryable": False,
                }
            elif type(version.get("minor")) is not int or version["minor"] != _CREATE_PROTOCOL_MINOR:
                error = {
                    "code": "INVALID_REQUEST",
                    "category": "validation",
                    "retryable": False,
                }
            else:
                details = _create_validation_details(command, raw_payload)
                if details:
                    error = {
                        "code": "INVALID_REQUEST",
                        "category": "validation",
                        "retryable": False,
                        "details": details,
                    }
                else:
                    try:
                        result = (
                            self.handle_create_book(raw_payload)
                            if command == "CreateBook"
                            else self.handle_create_chapter(raw_payload)
                        )
                    except BookNotFound:
                        error = {
                            "code": "TARGET_NOT_FOUND",
                            "category": "not_found",
                            "retryable": False,
                        }
                    except sqlite3.Error:
                        error = {
                            "code": "LIBRARY_WRITE_FAILED",
                            "category": "internal",
                            "retryable": "unknown",
                        }
                    except Exception:
                        error = {
                            "code": "UNKNOWN",
                            "category": "unknown",
                            "retryable": "unknown",
                        }
            return ({
                "protocol": PROTOCOL_NAME,
                "version": {"major": PROTOCOL_MAJOR, "minor": _CREATE_PROTOCOL_MINOR},
                "request_id": request_id if isinstance(request_id, str) else None,
                "result": result,
                "error": error,
            }, False)

        elif command in _DELETE_COMMANDS:
            result = None
            error = None
            if protocol != PROTOCOL_NAME or not is_valid_version:
                error = {
                    "code": "PROTOCOL_VERSION_UNSUPPORTED",
                    "category": "validation",
                    "retryable": False,
                }
            elif type(version.get("minor")) is not int or version["minor"] != _DELETE_PROTOCOL_MINOR:
                error = {
                    "code": "INVALID_REQUEST",
                    "category": "validation",
                    "retryable": False,
                }
            else:
                if command == "PermanentlyDeleteBook":
                    result, error = self.handle_permanently_delete_book(raw_payload)
                else:
                    result, error = self.handle_permanently_delete_books(raw_payload)
            return ({
                "protocol": PROTOCOL_NAME,
                "version": {"major": PROTOCOL_MAJOR, "minor": _DELETE_PROTOCOL_MINOR},
                "request_id": request_id if isinstance(request_id, str) else None,
                "result": result,
                "error": error,
            }, False)

        if protocol != PROTOCOL_NAME or not is_valid_version:
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": safe_request_id,
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

        if command == "ImportPages":
            try:
                if not isinstance(raw_payload, dict):
                    raise P16WireError(
                        "INVALID_REQUEST", "validation", "Request payload must be an object"
                    )
                result = self.handle_import_pages(payload)
                error = None
            except P16WireError as caught:
                result = None
                error = make_error_envelope(
                    caught.code, caught.category, str(caught), retryable=False
                )
            except TypedResourceChannelError as caught:
                result = None
                error = _import_ref_error_envelope(caught.code)
            except Exception:
                result = None
                error = make_error_envelope(
                    "UNKNOWN", "internal", "Import operation failed", retryable=False
                )
            return ({
                "protocol": PROTOCOL_NAME,
                "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                "request_id": request_id,
                "result": result,
                "error": error,
            }, False)

        if command in ("GetReaderProjection", "SaveReadingProgress", "StartExport",
                       "GetExportSnapshot", "GetExportHistory", "CancelExport"):
            try:
                if not isinstance(raw_payload, dict):
                    raise P16WireError("INVALID_REQUEST", "validation", "Request payload must be an object")
                if command == "GetReaderProjection":
                    result = self.handle_get_reader_projection(payload)
                elif command == "SaveReadingProgress":
                    result = self.handle_save_reading_progress(payload)
                elif command == "StartExport":
                    result = self.handle_start_export(payload)
                elif command == "GetExportSnapshot":
                    if set(payload) != {"export_id"} or not isinstance(payload.get("export_id"), str) or not payload["export_id"]:
                        raise P16WireError("INVALID_REQUEST", "validation", "Export snapshot request is invalid")
                    if self._exports is None:
                        raise P16WireError("EXPORT_NOT_FOUND", "not_found", "Export was not found")
                    try:
                        result = self._exports.snapshot(payload["export_id"])
                    except KeyError as error:
                        raise P16WireError("EXPORT_NOT_FOUND", "not_found", "Export was not found") from error
                elif command == "CancelExport":
                    if set(payload) != {"export_id"} or not isinstance(payload.get("export_id"), str) or not payload["export_id"]:
                        raise P16WireError("INVALID_REQUEST", "validation", "Export cancel request is invalid")
                    if self._exports is None:
                        raise P16WireError("EXPORT_NOT_FOUND", "not_found", "Export was not found")
                    try:
                        result = self._exports.cancel(payload["export_id"])
                    except KeyError as error:
                        raise P16WireError("EXPORT_NOT_FOUND", "not_found", "Export was not found") from error
                else:
                    if payload:
                        raise P16WireError("INVALID_REQUEST", "validation", "Export history request is invalid")
                    result = {"exports": self._exports.history() if self._exports else []}
                error = None
            except P16WireError as caught:
                result = None
                error = make_error_envelope(caught.code, caught.category, str(caught), retryable=False, details=caught.details)
            except ExportTargetRefError as caught:
                result = None
                error = _export_ref_error_envelope(caught.code)
            except Exception:
                result = None
                error = make_error_envelope("UNKNOWN", "internal", "Reader or export operation failed", retryable=False)
            return ({
                "protocol": PROTOCOL_NAME,
                "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                "request_id": request_id, "result": result, "error": error,
            }, False)

        if isinstance(command, str) and command in _RUN_COMMANDS:
            return self._dispatch_run_command(
                command,
                payload,
                request_id,
                payload_is_object=isinstance(raw_payload, dict),
                protocol_minor=(version.get("minor") if isinstance(version, dict) and type(version.get("minor")) is int else _LEGACY_PROTOCOL_MINOR),
            )

        if isinstance(command, str) and command in _P15_SETTINGS_COMMANDS:
            if version.get("minor") != _P15_PROTOCOL_MINOR:
                error = SettingsSurfaceError(
                    "validation", "settings_resolution", "none", "SETTINGS_INVALID_INPUT"
                )
                return self._p15_settings_error_response(request_id, error), False
            try:
                if not isinstance(raw_payload, dict):
                    raise SettingsSurfaceError(
                        "validation", "settings_resolution", "none", "SETTINGS_INVALID_INPUT"
                    )
                result = self._p15_settings.handle(command, payload)
            except SettingsSurfaceError as error:
                return self._p15_settings_error_response(request_id, error), False
            except Exception:
                error = SettingsSurfaceError(
                    "unavailable", "settings_resolution", "contact_support", "SETTINGS_UNAVAILABLE"
                )
                return self._p15_settings_error_response(request_id, error), False
            return ({
                "protocol": PROTOCOL_NAME,
                "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                "request_id": request_id,
                "result": result,
                "error": None,
            }, False)

        if command == "ListRecycleBinBooks":
            # AC1 (R-007): the recycle bin gets its own read face on the
            # production dispatcher, so the command -> Core -> service route is
            # actually complete rather than the frontend calling a name that
            # nothing answers.
            try:
                recycle_books = self.handle_list_recycle_bin_books(payload)
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": recycle_books,
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
                            message="Failed to query recycle bin books",
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
                            message="Failed to list recycle bin books",
                            retryable=False,
                        ),
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
                        "request_id": safe_request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_INVALID_REQUEST,
                            category="validation",
                            message=_project_settings_value(str(error)),
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
                        "request_id": safe_request_id,
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
                    "request_id": safe_request_id,
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

    def dispatch_request(self, raw_line: str) -> tuple[dict[str, Any], bool]:
        """Keep legacy 2.3 envelopes stable while serving the 2.6 settings face."""
        try:
            request = json.loads(raw_line)
        except (json.JSONDecodeError, TypeError):
            request = {}
        request = request if isinstance(request, dict) else {}
        version = request.get("version")
        requested_minor = version.get("minor") if isinstance(version, dict) else None
        command = request.get("command")
        response, should_exit = self._dispatch_request(raw_line)
        if command in _CREATE_COMMANDS:
            response_minor = _CREATE_PROTOCOL_MINOR
        elif command in _DELETE_COMMANDS:
            response_minor = _DELETE_PROTOCOL_MINOR
        elif command in _P15_SETTINGS_COMMANDS or requested_minor == _P15_PROTOCOL_MINOR:
            response_minor = _P15_PROTOCOL_MINOR
        else:
            response_minor = PROTOCOL_MINOR
        response["version"] = {"major": PROTOCOL_MAJOR, "minor": response_minor}
        result = response.get("result")
        if isinstance(result, dict) and isinstance(result.get("protocol_version"), dict):
            result["protocol_version"] = {
                "major": PROTOCOL_MAJOR,
                "minor": response_minor,
            }
        return response, should_exit

    @staticmethod
    def _p15_settings_error_response(
        request_id: Any, error: SettingsSurfaceError
    ) -> dict[str, Any]:
        code = {
            "validation": E_INVALID_REQUEST,
            "not_found": E_TARGET_NOT_FOUND,
            "conflict": "SETTINGS_CONFLICT",
            "unavailable": "SETTINGS_UNAVAILABLE",
        }[error.category]
        return {
            "protocol": PROTOCOL_NAME,
            "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
            "request_id": request_id if isinstance(request_id, str) else None,
            "result": None,
            "error": make_error_envelope(
                code,
                error.category,
                error.message_key,
                retryable=False,
                details=error.details,
            ),
        }

    def serve_forever(self) -> int:
        """Main stdio loop reading requests line by line."""
        self._serving = True
        self._start_run_scheduler()
        try:
            for line in self._stdin:
                line = line.strip()
                if not line:
                    continue
                response, should_exit = self.dispatch_request(line)
                self._emit(response)
                if should_exit:
                    return 0
            return 0
        finally:
            try:
                self._invalidate_host_session()
            finally:
                self._stop_run_scheduler()
                self._serving = False

    def _emit(self, payload: dict[str, Any]) -> None:
        with self._write_lock:
            self._stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
            self._stdout.flush()


def _ensure_preview_namespace(catalog_db: Path, derived_root: Path) -> None:
    if catalog_db.exists():
        if read_lock_binding_if_any(str(derived_root)) is not None:
            return
        if restore_namespace_lock(catalog_db, derived_root):
            return
    initialize_namespace(catalog_db, derived_root)


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
    # lease for the sweeps. Startup GC is opportunistic; serving still
    # requires a verified shared lease before serve_forever/core.ping.
    _ensure_preview_namespace(catalog_db, derived_root)
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
                    # F-002 (Codex R1): the managed root, NOT the data root.
                    # artifact_revisions.managed_path is relative to the
                    # storage root (data/managed), so joining it against
                    # data_root produced a path that never existed and every
                    # retired-preview verification refused - the previews could
                    # not be reclaimed even once they had a lifecycle row.
                    producer_root=str(core.storage.root),
                )
            finally:
                gc_store.close()
            # Exclusive -> shared downgrade: no business request happens in
            # between (nothing is served before serve_forever).
            exclusive.release()
        else:
            print(
                "[core.derived_gc] skipped: exclusive namespace lease unavailable;"
                " startup sweeps were skipped",
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
                # F-002 (Codex R1): same correction as the retired-preview GC
                # above - managed paths are relative to the storage root.
                producer_root=core.storage.root,
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
