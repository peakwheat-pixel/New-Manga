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
  - list_page_region_texts: {"page_id": "<id>", "region_ids"?: ["<id>", ...]}
      -> {"page_id", "page_size": {"width", "height"} | null,
          "regions": RegionTextDetail[]}
    (V11R-F0-2 / closes the V11R-F0-1 GAP-2: the region TEXT read face did
    not exist, so the Studio Page mode had no way to load the four-level text
    of an already-edited page -- only list_regions' minimal five-field DTO and
    the revision summaries existed. This single-page read returns every live
    region of one page with its REAL persisted projection: four-level text,
    the three locks, review_state, origin, current revision number/id,
    is_pinned of the current revision, all pinned revision numbers and the
    normalized geometry -- one round trip, no per-region N+1. The optional
    region_ids filter is strict (every id must be a LIVE region of that page,
    otherwise TARGET_NOT_FOUND, which also rejects a cross-page id). A page
    with no regions reads as an empty list (the frozen C043 precedent, not an
    error); an unknown page reads page_size null and empty regions. Protocol
    minor stays 3 (same Region family, zero bump). Errors: INVALID_REQUEST
    (payload) / TARGET_NOT_FOUND (filtered region unknown or of another
    page) / UNKNOWN (internal) only.)
  - create_region / delete_region / save_region_geometry / merge_regions /
    split_region / reorder_regions / save_manual_translation /
    confirm_region_final / set_region_lock / pin_revision
    (V11R-F0-1 / audit §5.1 F-01: the Region write face the Studio Page mode
    consumes. Additive command surface on the SAME Region family minor (3):
    the Core's version gate enforces the major for this family, the existing
    Region siblings ride minor 3, and zero pre-existing command semantics
    change -- same backwards-compatible widening precedent as the
    cleanup/backup/plugin and RC-4 command families. Request payloads are
    validated typed fail-closed BEFORE any persistence; every write reuses
    the EXISTING ``application.editing.service`` use case (the single new use
    case ``set_locks`` composes the existing domain lock setters through the
    same atomic commit seam and is recorded as a GAP in
    doc/contracts/V11R_REGION_WRITE_CONTRACT.md). Wire geometry is the
    editable normalized point list ``{"points": [[x, y], ...]}`` (0..1; two
    points = rectangle, >=3 = polygon) converted by
    ``application/editing/region_canvas.py``; results project the
    post-write effective state. Error semantics reuse the existing typed
    literals only: INVALID_REQUEST (validation) / INPUT_REVISION_CHANGED
    (the explicit ``expected_revision`` / ``expected_revisions`` optimistic
    guard, ZERO write on conflict) / TARGET_NOT_FOUND (region, page or
    revision not found) / UNKNOWN (internal). Full per-command contract:
    doc/contracts/V11R_REGION_WRITE_CONTRACT.md.)
  - cleanup.preview: {} -> {"targets": [{"relative_path", "size_bytes"}...],
      "total_bytes": <int>, "pending_cleanups": <int>}
    (SETTINGS-OPEN-B-2, design §4.3: the cache/Revision maintenance face
    over the assembly-injected ``CleanupService``. Ordinary
    application-channel commands (settings.get precedent), NOT HostControl
    -- the frozen host-control envelope stays the HOST-ISSUER-1
    grant/session set. The inventory is the rebuildable webtoon tile cache
    under ``<managed_root>/cache/webtoon-tiles``; targets are relative
    paths only, and only paths under a safe cache prefix are ever
    reported. Reading never deletes.)
  - cleanup.run: {} -> {"items": {<relative_path>: {"status",
      "reason"}...}, "removed", "failed", "skipped"}
    (Remove every safe cache target; idempotent -- already-gone files
    report ``ok``. A failed removal is persisted in the shared trash
    manifest's ``pending_cleanups`` ledger before the outcome returns,
    never silently dropped. No user source file, business row, current or
    pinned Revision is addressable: cleanup only hands ``cache/``-prefixed
    relative paths to the controlled remover.)
  - cleanup.retry_pending: {} -> the same outcome projection as cleanup.run
    (TASK-060 Q-007 retry semantics: the never-clean predicate is
    re-checked on every pending entry, only settled entries leave the
    ledger, and an entry that fails again stays pending. A pending list
    that was never written reads as an empty retry -- never an error.)
    Errors for the three faces: payload non-object -> INVALID_REQUEST
    (validation, fail-closed before any filesystem work); an assembly
    without the injected service -> CORE_UNAVAILABLE (unavailable,
    retryable) -- the sidecar keeps serving; anything else -> UNKNOWN
    (internal). Protocol minor stays 3: the envelope version is unchanged
    by this additive command surface (same precedent as the later
    production-only command families).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
from dataclasses import asdict, dataclass
import io
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import sys
import tempfile
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, TextIO

from application.editing.errors import (
    DraftError,
    GuardStatus,
    RegionLimitExceeded,
    RegionNotFound,
    RegionRevisionChanged,
    RegionRevisionNotFound,
)
from application.editing.region_canvas import (
    MAX_GEOMETRY_POINTS,
    MAX_REGION_IDS_PER_BATCH,
    MAX_REGIONS_PER_PAGE,
    MAX_SPLIT_PARTS,
    RegionCanvasError,
    normalized_to_page_geometry,
    page_geometry_to_normalized,
)
from application.editing.service import effective_sfx_policy, region_text_state
from application.sources.lineage import (
    LINEAGE_BINDING_CHANGED,
    LINEAGE_UNVERIFIED,
    LineageVerificationError,
)
from application.importing.documents.ports import DocumentDecodeError
from application.importing.images.ports import DecodedImage, ImportSource
from application.importing.images.service import DuplicatePolicy
from application.library.errors import BookNotFound
from application.library.service import (
    canonical_inventory_payload,
    canonical_payload_digest,
    collection_inventory_digest,
    decode_trash_cursor,
    encode_trash_cursor,
    inventory_digest,
    is_inventory_digest,
    is_valid_idempotency_key,
    normalize_trash_entries,
    shared_file_refs,
)
from application.maintenance.cleanup import CleanupOutcome, CleanupService
from application.maintenance.ports import (
    ProtectionFacts,
    ProtectionPolicy,
    ProtectionScope,
)
from application.resource_channel.dto import (
    E_IDENTITY_CHANGED,
    E_NOT_FOUND,
    E_OUT_OF_SCOPE,
    E_REPARSE,
    E_SCOPE_DENIED,
    TypedResourceChannelError,
)
from application.settings.errors import BindingValidationError
from application.export import ExportFormat, ExportPage, ExportRequest, P16ExportRuntime, StalePolicy
from application.export.service import OverwritePolicy
from application.translation.color.service import SourceStyleService
from bootstrap.core_assembly import (
    CoreServices,
    assemble_core_services,
    default_data_root,
)
from domain.regions.entities import RegionGeometry, RegionType, SfxPolicy
from domain.tasks.models import COMMAND_CATALOG, CommandType, PipelineError, PipelineScope, ScopeType
from infrastructure.importing import PillowImageDecoder, SUPPORTED_IMAGE_SUFFIXES
from infrastructure.resource_channel.source_read_refs import SourceReadGrantRegistry  # noqa: F401 (FEA-09 type re-export)
from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.runtime import ReferencedImportRuntime  # noqa: F401
from infrastructure.providers.handlers import typeset_style_defaults
from infrastructure.rendering.pillow_rendering import (
    PillowFontCatalog,
    PillowImageCompositor,
    PillowTextLayoutEngine,
    decode_nmfr_frame,
)
from infrastructure.rendering.pillow_source_style import PillowSourceStyleAnalyzer
from infrastructure.resource_channel.catalog_store import (
    PreviewOrigin,
    ResourceCatalogStore,
    initialize_namespace,
    rebind_namespace,
    restore_namespace_lock,
    verify_binding_for_root,
)
from infrastructure.resource_channel.handle_resolver import (
    ManagedRootTrust,
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
from infrastructure.sqlite.library import PermanentDeleteBlockedError
from infrastructure.sqlite.nmbak import NmbakBackupError
from infrastructure.sqlite.upgrade_legacy_layout import (
    LegacyLayoutError,
    migrate_legacy_layout,
)
from infrastructure.plugins.service import PluginError
from ports.detection.ports import DetectionRequest
from ports.providers.errors import ProviderError, ProviderNotConfigured
from bootstrap.settings_commands import P15_SNAPSHOT_KEY, P15SettingsCommands, SettingsSurfaceError
from bootstrap.settings_sections import SettingsSectionError, validate_settings_section

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
#: C-04b v1.1 / M2-C1 rev 2.14 §5.13: the read-only deletion-preview command
#: family keeps wire minor 11 (v1.1 only adds response fields; the contract
#: explicitly does NOT bump the target minor).
_PREVIEW_PROTOCOL_MINOR = 11
#: C-09 SC-B06 / M2-C1 §5.14: the recycle-bin command family is an
#: independent family at wire minor 13.
_TRASH_PROTOCOL_MINOR = 13
_CREATE_COMMANDS = frozenset({"CreateBook", "CreateChapter"})
_DELETE_COMMANDS = frozenset({"PermanentlyDeleteBook", "PermanentlyDeleteBooks"})
_PREVIEW_COMMANDS = frozenset({"PreviewPermanentDeleteBooks"})
_TRASH_COMMANDS = frozenset({"MoveToTrash", "RestoreFromTrash", "ListTrash", "PurgeTrash"})
#: M2-C1 §5.14: ``PurgeTrash`` is registered on the frozen wire but the first
#: CORE release does NOT implement it (digest binding needs a separate DSH
#: additive ruling).  It must fail closed with a typed error and never be
#: silently implemented or partially executed.
_UNIMPLEMENTED_COMMANDS = frozenset({"PurgeTrash"})
#: M2-C1 §5.13/§5.14 capability names (host probes ``core.ping`` first).
_FEA12_CAPABILITIES = (
    "library.delete.preview/1",
    "library.trash.read/1",
    "library.trash.write/1",
)
_TRASH_DEFAULT_LIMIT = 50
_TRASH_MAX_LIMIT = 200
_CREATE_FIELDS = {
    "CreateBook": (("title", True),),
    "CreateChapter": (("book_id", True), ("title", True), ("chapter_number", False)),
}
# HOST-ISSUER-1-C1 rev 2.3 adds an independent host-owned stdio control envelope.
# FEA-09 (C-16 §0/§2): the source-read grant pair joins the envelope as an
# additive widening — existing commands keep their frozen semantics.
_HOST_CONTROL_COMMANDS = frozenset({
    "OpenHostSession", "RegisterImportSource", "RevokeImportSource",
    "RegisterExportTarget", "RevokeExportTarget", "CloseHostSession",
    "RegisterSourceReadGrant", "RevokeSourceReadGrant",
    # FEA-11 (C-17 §4): scan/apply/relink/repoint/resync plus the
    # ACK/recovery/failure pair ride the host-control private session.
    "ScanSourceSync", "ApplySourceSyncPlan", "RelinkSource", "RepointSource",
    "ResyncSource", "AcknowledgeSourceOperation",
    "CompleteSourceOperationRecovery", "RecordSourceOperationFailure",
})
#: FEA-11 (C-17 §4/§5.1): the plan lifecycle/query face stays on the
#: ordinary Request/Response channel (protocol minor 3, additive).
_SOURCE_SYNC_APP_COMMANDS = frozenset({
    "source_plan_sync", "source_preview_sync_plan", "source_confirm_sync_plan",
    "source_invalidate_sync_plan", "source_get_operation",
    "source_cancel_operation",
    # FEA-11-SCAN-2 (C-17 v1.1 §5.1): the cold-start read-only target
    # enumeration is an ordinary application-face command (not host-control)
    # with the closed shape ``{}``; it never writes and never registers in the
    # Host C-07 registry.
    "source_list_scan_targets",
})
#: FEA-09 async import face (C-16 §4): ordinary application-channel
#: commands; the protocol minor stays 3 (additive widening precedent).
_REFERENCED_IMPORT_COMMANDS = frozenset({
    "PlanImportReferences", "StartImportReferences",
    "GetImportReceipt", "CancelImport",
})
_RUN_COMMANDS = frozenset({
    "PrepareRun", "AcceptRun",
    "StartRun", "ControlRun", "ResumeBlockedRun", "GetRunSnapshot",
    "GetTaskProjection", "RetryFailedTargets",
})
#: SETTINGS-OPEN-B-2 (design §4.3): the cache/Revision maintenance face.
#: These are ORDINARY application-channel commands (the settings.get
#: precedent), NOT HostControl operations: the host-control envelope is
#: frozen to the HOST-ISSUER-1 grant/session set by contract §5.7, and the
#: Tauri bridge drives every production command over the application
#: envelope. Adding them to ``_HOST_CONTROL_COMMANDS`` would make the
#: application channel refuse them with HOST_ONLY_REQUIRED.
_CLEANUP_COMMANDS = frozenset({
    "cleanup.preview",
    "cleanup.run",
    "cleanup.retry_pending",
})
#: SETTINGS-OPEN-C-2-BACKUP (design §3.4): the backup/restore face. Same
#: ordinary application-channel precedent as cleanup/settings.get -- the
#: frozen host-control envelope is not widened.
_BACKUP_COMMANDS = frozenset({
    "backup.create",
    "backup.list",
    "backup.restore",
    "backup.delete",
})
#: Design §3.4 error taxonomy -> (category, retryable). Anything not listed
#: falls back to ("internal", False).
#: PLUGIN-RUNTIME-1 (design §4.1-§4.4, decisions D1-D6): the local plugin
#: runtime face. Same ordinary application-channel precedent as cleanup and
#: backup -- the frozen host-control envelope is not widened. The commands are
#: additive; protocol minor stays 3.
_PLUGIN_COMMANDS = frozenset({
    "plugins.list",
    "plugins.set_enabled",
    "plugins.set_plugin_enabled",
    "plugins.audit_list",
})
#: Plugin runtime error taxonomy -> (category, retryable).
_PLUGIN_ERROR_RULES: dict[str, tuple[str, bool]] = {
    "INVALID_REQUEST": ("validation", False),
    "PLUGIN_INVALID_REQUEST": ("validation", False),
    "PLUGIN_NOT_FOUND": ("not_found", False),
    "PLUGIN_NOT_LOADED": ("validation", False),
    "PLUGIN_HOOK_UNKNOWN": ("validation", False),
    "PLUGIN_HOOK_TIMEOUT": ("conflict", True),
    "PLUGIN_HOOK_FAILED": ("internal", True),
    "PLUGIN_HOOK_UNAVAILABLE": ("internal", False),
    "PLUGIN_OPERATION_FAILED": ("internal", False),
    "CORE_UNAVAILABLE": ("unavailable", True),
}
_BACKUP_ERROR_RULES: dict[str, tuple[str, bool]] = {
    # Malformed backup payloads are request validation, not internal failures
    # (review r1 P1-4: the fallback used to project them as "internal").
    "INVALID_REQUEST": ("validation", False),
    "BACKUP_CREATE_FAILED": ("internal", "unknown"),
    "BACKUP_DELETE_FAILED": ("internal", False),
    "BACKUP_NOT_FOUND": ("not_found", False),
    "BACKUP_CORRUPT": ("validation", False),
    "BACKUP_RESTORE_BUSY": ("conflict", True),
    "BACKUP_RESTORE_INCOMPLETE": ("conflict", False),
    "BACKUP_RESTORE_REQUIRES_CONFIRMATION": ("validation", False),
}
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
# SETTINGS-OPEN-B-2: an assembly without the cleanup service refuses the
# cleanup faces with the SAME literal the Tauri host already uses for a
# missing Core channel (contract §5.3 line: channel/spawn failure ->
# CORE_UNAVAILABLE), so the panel shows one stable "unavailable" family
# regardless of whether the channel or the injected service is missing.
E_CORE_UNAVAILABLE = "CORE_UNAVAILABLE"

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

#: V11R-F0-1: the Region write face the Studio Page mode consumes (audit
#: §5.1 F-01 -- the commands did not exist on the wire before). Additive to
#: the six registered Region commands (C042-C047); every handler reuses the
#: EXISTING ``application.editing.service`` use cases and only adds the
#: wire-side validation/projection. There is no new envelope semantics: the
#: commands ride the same per-command family minor (3) as their
#: ``set_region_type`` / ``list_regions`` siblings.
_REGION_WRITE_COMMANDS = frozenset({
    "create_region",
    "delete_region",
    "save_region_geometry",
    "merge_regions",
    "split_region",
    "reorder_regions",
    "save_manual_translation",
    "confirm_region_final",
    "set_region_lock",
    "pin_revision",
})

#: V11R-F0-1: the three user locks the ``set_region_lock`` command addresses.
_REGION_LOCK_FIELDS = ("region_locked", "translation_locked", "inpaint_locked")

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

# DETECT-MEMORY-GUARD-1 (SEC-FMT-005 item 1): the pixel cap above is a
# fixed constant, identical on an 8 GB machine and a 64 GB one.
# SEC-FMT-005 also asks that available physical memory be considered.
# This is a BACKSTOP, not the primary criterion: a page at the ceiling
# needs ~32 MB as RGB24 while a healthy host reports gigabytes free, so
# on a normal machine this never fires and the pixel cap remains the
# real constraint. It matters in a container, under memory pressure, or
# on a pathologically small host.
#: Fraction of currently-available physical memory one page may claim.
#: 0.25 leaves the rest for the sidecar, the model, and the OS.
#: The effective rejection line is avail < 16N for an N-pixel page;
#: measured convert() peaks run about 3N-7N, so the ratio keeps more
#: than 2x headroom over the real allocation.
_DETECT_MEMORY_SAFETY_RATIO = 0.25
#: Bytes per pixel used to ESTIMATE the page's allocation need. This is
#: the destination-buffer figure (RGBA = 4, RGB24 = 3), not a peak
#: guarantee: converting an RGBA source keeps the source and target
#: buffers alive together, so the transient peak is roughly 6N-7N for
#: an N-pixel page. The 4 B/px estimate is therefore a lower bound on
#: the peak, and it is the SAFETY RATIO above - not this constant -
#: that covers the difference. Do not read this as a worst-case peak.
_DETECT_BYTES_PER_PIXEL = 4


def _available_physical_bytes() -> int | None:
    """Best-effort available physical memory, or None when unavailable.

    Windows-only by design: the product boundary is Windows single-platform
    (AD-001). Returns None rather than raising so the caller can fall back to
    the fixed pixel cap instead of guessing.
    """
    if sys.platform != "win32":  # pragma: no cover - platform, not logic
        return None
    try:
        import ctypes
        import ctypes.wintypes as wt
    except Exception:  # pragma: no cover - ctypes is stdlib
        return None

    class _MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", wt.DWORD),
            ("dwMemoryLoad", wt.DWORD),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(_MEMORYSTATUSEX)]
        kernel32.GlobalMemoryStatusEx.restype = wt.BOOL
        status = _MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(status)
        if not kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return None
        return int(status.ullAvailPhys)
    except Exception:  # noqa: BLE001 - probe failure must not break detect
        return None


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


class CleanupRequestError(ValueError):
    """A cleanup.* payload violates the request contract (INVALID_REQUEST;
    SETTINGS-OPEN-B-2, design §4.3 -- same fail-closed discipline as the
    settings pair). The three faces take no parameters, so the only shape
    gate is "payload is a JSON object"; the refusal carries a fixed short
    message, never an OS path."""


class CleanupUnavailableError(RuntimeError):
    """No ``CleanupService`` was injected into this Core assembly
    (SETTINGS-OPEN-B-2). The cleanup faces then fail closed with the
    existing ``CORE_UNAVAILABLE`` / ``unavailable`` envelope -- the same
    code family the Tauri host already surfaces for a missing Core channel
    -- instead of crashing the sidecar or pretending an empty cleanup."""


#: Fixed, path-free reasons for the cleanup wire (review-b2 P2-1). An
#: ``OSError`` text may embed an absolute OS path (the managed root) and must
#: never reach the WebView; the panel only needs to know *why* it failed.
_CLEANUP_FAILED_REASON = "remove failed"
_CLEANUP_SKIPPED_REASON = "outside safe cache prefixes"


def _cleanup_outcome_projection(outcome: CleanupOutcome) -> dict[str, Any]:
    """SETTINGS-OPEN-B-2 AC1: the outcome wire projection is the frozen
    ``CleanupOutcome.to_dict()`` shape (relative path -> status/reason) plus
    the three counts the settings panel displays. No OS path, no absolute
    path and no user source file ever appears here: cleanup only addresses
    ``cache/``-prefixed relative paths, and failure reasons are fixed
    path-free sentences (review-b2 P2-1)."""
    items = outcome.to_dict()
    projected: dict[str, dict[str, str]] = {}
    for path, item in items.items():
        status = str(item.get("status", ""))
        projected[str(path)] = {
            "status": status,
            "reason": (
                ""
                if status == "ok"
                else _CLEANUP_FAILED_REASON
                if status == "failed"
                else _CLEANUP_SKIPPED_REASON
            ),
        }
    return {
        "items": projected,
        "removed": outcome.removed,
        "failed": outcome.failed,
        "skipped": outcome.skipped,
    }


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
    """A region-side target does not exist or is soft-deleted (C7) -- mapped
    to the existing TARGET_NOT_FOUND/not_found row; carries only the opaque
    id so no raw exception text rides the wire (§8).

    V11R-F0-1: ``message`` lets the added write commands distinguish
    "region not found" from "page not found" / "region revision not found"
    without inventing a new error code (the frozen TARGET_NOT_FOUND row stays
    the single not_found code). The pre-existing callers keep the historical
    default message verbatim."""

    def __init__(self, region_id: str, message: str = "region not found") -> None:
        super().__init__(message)
        self.region_id = region_id
        self.message = message


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
    """Legacy test double; production assembly uses ``PillowImageDecoder``."""

    def decode(self, payload: bytes) -> DecodedImage:
        del payload
        # mime_type keeps the stub's original "rgb" semantics under the image
        # type, matching the frozen DecodedImage contract (no format= field).
        return DecodedImage(width=1, height=1, mime_type="image/rgb")


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
        # P09-MANAGED-READ-ROOT-TRUST-1: the reference is admitted through the
        # start-up identity snapshot of the managed root and the bytes are read
        # through the verifying handle.  Re-resolving ``storage.root`` here made
        # both sides of the old containment check follow a junction injected
        # above the configured root (R5b P2 reproduction).
        trust = getattr(current, "managed_root_trust", None)
        if trust is None:
            raise ValueError("managed original escaped the Managed Copy root")
        try:
            return trust.read_bytes(page.managed_original_ref)
        except TypedResourceChannelError as error:
            if error.code == E_NOT_FOUND:
                return None
            if error.code in (E_IDENTITY_CHANGED, E_OUT_OF_SCOPE, E_REPARSE, E_SCOPE_DENIED):
                raise ValueError(
                    "managed original escaped the Managed Copy root"
                ) from error
            raise OSError(str(error)) from error

    core = assemble_core_services(
        db_path,
        managed_root,
        image_decoder=PillowImageDecoder(),
        font_catalog=catalog,
        layout_engine=PillowTextLayoutEngine(catalog),
        compositor=PillowImageCompositor(catalog),
        source_styles=SourceStyleService(PillowSourceStyleAnalyzer()),
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


_DRAFT_ERROR_CATEGORY: dict[str, str] = {
    # 17 codes raised by application/editing/drafts.py (FEA-05 §3).
    "DRAFT_INVALID": "validation",
    "DRAFT_PATCH_INVALID": "validation",
    "DRAFT_CANDIDATE_INVALID": "validation",
    "DRAFT_FLUSH_TRIGGER_INVALID": "validation",
    "EDIT_TOKEN_INVALID": "validation",
    "DRAFT_NOT_FOUND": "not_found",
    "DRAFT_CANDIDATE_NOT_FOUND": "not_found",
    "TARGET_NOT_FOUND": "not_found",
    "DRAFT_READ_ONLY": "conflict",
    "DRAFT_OWNER_CHANGED": "conflict",
    "EDIT_TOKEN_EXPIRED": "conflict",
    "EDIT_TOKEN_REUSED": "conflict",
    "STALE_BASE_REVISION": "conflict",
    "LOCK_CHANGED": "conflict",
    "DRAFT_JOURNAL_UNWRITABLE": "unavailable",
    "PAGE_SIZE_UNAVAILABLE": "unavailable",
    "DRAFT_APPLY_FAILED": "internal",
    # FEA-11-LINEAGE-1: a draft applied over a stale/other source binding is a
    # typed C-17 §7.1 conflict, never an internal failure.
    LINEAGE_BINDING_CHANGED: "conflict",
    LINEAGE_UNVERIFIED: "conflict",
    "INTERNAL": "internal",
    "UNKNOWN": "validation",
}

_DRAFT_RETRYABLE = {"PAGE_SIZE_UNAVAILABLE", "DRAFT_JOURNAL_UNWRITABLE", "INTERNAL"}


def _draft_error_envelope(error: "DraftError") -> dict[str, Any]:
    """Map a DraftError to the frozen M2-C1 error envelope (FEA-05 §3)."""
    code = getattr(error, "code", "INTERNAL")
    category = _DRAFT_ERROR_CATEGORY.get(code, "internal")
    details = getattr(error, "details", None) or None
    cause = getattr(error, "cause_code", None)
    if cause:
        details = list(details or []) + [{"causeCode": cause}]
    return make_error_envelope(
        code=code,
        category=category,
        message=str(error) or code,
        retryable=code in _DRAFT_RETRYABLE,
        details=details,
    )


def _lineage_error_envelope(error: "LineageVerificationError") -> dict[str, Any]:
    """FEA-11-LINEAGE-1: typed C-17 §7.1 isolation refusal.

    ``LINEAGE_BINDING_CHANGED`` / ``LINEAGE_UNVERIFIED`` are application-level
    codes raised on the OLD command faces (list_regions / render / edit / Run /
    export). They are deliberately NOT added to the frozen C-17 §8 closed set:
    that table projects C-17 commands only and the old command face is not
    remapped (DSH ruling recorded in the task card). The envelope carries the
    fixed safe phrase; no path, coordinate or raw exception text rides it.
    """
    code = getattr(error, "code", LINEAGE_UNVERIFIED)
    # Diagnosable refusal (r2): one bounded stderr line names the code and the
    # opaque ids only — never coordinates, text or paths.
    print(
        f"[core.lineage] refused: code={code}"
        f" page={getattr(error, 'page_id', '') or ''}"
        f" region={getattr(error, 'region_id', '') or ''}",
        file=sys.stderr,
    )
    return make_error_envelope(
        code,
        getattr(error, "category", "conflict"),
        getattr(error, "safe_message", "source lineage verification failed"),
        retryable=False,
    )


def _require_str(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise DraftError("DRAFT_INVALID", f"{key} must be a non-empty string")
    return value


def _require_int(payload: dict[str, Any], key: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise DraftError("DRAFT_INVALID", f"{key} must be an integer")
    return value


def _require_mapping(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise DraftError("DRAFT_PATCH_INVALID", f"{key} must be an object")
    return value


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


def _source_import_error_envelope(error: SourceImportError) -> dict[str, Any]:
    """FEA-09: map a SourceImportError onto the frozen C-16 §6 table."""
    details = error.details or None
    return make_error_envelope(
        code=error.code,
        category=error.category,
        message=str(error) or error.code,
        retryable=error.retryable,
        details=[details] if isinstance(details, dict) else None,
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
        cleanup: CleanupService | None = None,
    ) -> None:
        self._core = core
        self._p15_settings = P15SettingsCommands(core)
        #: SETTINGS-OPEN-B-2 (design §4.3): the assembly-injected controlled
        #: cleanup use case. ``None`` keeps every existing construction valid
        #: and makes the three cleanup faces fail closed with
        #: CORE_UNAVAILABLE instead of crashing (an assembly that has not
        #: wired the service must not regress start-up). The production
        #: ``main`` passes ``core.cleanup`` explicitly -- there is no
        #: implicit fallback, so a forgotten injection is loud, not silent.
        self._cleanup = cleanup
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
        source_registry = getattr(self._core, "source_read_refs", None)
        if source_registry is not None:
            source_registry.revoke_all_for_session()
        for grant_id, kind in tuple(self._host_grants.items()):
            if kind == "import":
                self._revoke_import_source({"grant_id": grant_id})
            elif kind == "source-read":
                registry = getattr(self._core, "source_read_refs", None)
                if registry is not None:
                    registry.revoke_grant_ids([grant_id])
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
        if command in ("RegisterSourceReadGrant", "RevokeSourceReadGrant"):
            # FEA-09 source-read grant pair (C-16 §2/§7.7): distinct payload
            # shape, so it branches before the Import/Export grant handling.
            if not isinstance(payload, dict):
                return self._host_control_response(
                    request_id, None,
                    _source_import_error_envelope(SourceImportError(
                        "SOURCE_ACCESS_DENIED", "source-read grant payload is malformed"
                    )),
                )
            try:
                if command == "RegisterSourceReadGrant":
                    if payload.get("session_id") != self._host_session_id:
                        raise SourceImportError(
                            "SOURCE_ACCESS_DENIED", "grant session does not match"
                        )
                    result = self._register_source_read_grant(payload)
                else:
                    result = self._revoke_source_read_grant(payload)
            except SourceImportError as caught:
                return self._host_control_response(
                    request_id, None, _source_import_error_envelope(caught)
                )
            except Exception:
                return self._reject_host_control(
                    request_id, "UNKNOWN", "internal", "Host control operation failed"
                )
            if command == "RegisterSourceReadGrant" and isinstance(
                payload.get("grant_id"), str
            ):
                self._host_grants[payload["grant_id"]] = "source-read"
            return self._host_control_response(request_id, result, None)
        if command in (
            "ScanSourceSync", "ApplySourceSyncPlan", "RelinkSource",
            "RepointSource", "ResyncSource", "AcknowledgeSourceOperation",
            "CompleteSourceOperationRecovery", "RecordSourceOperationFailure",
        ):
            # FEA-11 (C-17 §4/§5.1): the source-sync host-control face. The
            # session was verified above; typed failures map through the
            # frozen C-17 §8 table (SourceSyncError carries it).
            if not isinstance(payload, dict):
                return self._host_control_response(
                    request_id, None,
                    make_error_envelope(
                        "INVALID_REQUEST", "validation",
                        "Source sync request is invalid", False,
                    ),
                )
            try:
                result = self._dispatch_source_sync(command, payload)
            except SourceImportError as caught:
                return self._host_control_response(
                    request_id, None, _source_import_error_envelope(caught)
                )
            except Exception:
                return self._host_control_response(
                    request_id, None,
                    make_error_envelope(
                        "SOURCE_SYNC_STORAGE_FAILED", "internal",
                        "Source sync operation failed", True,
                    ),
                )
            return self._host_control_response(request_id, result, None)
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
        capabilities = [
            "library.list_books", "source.read/1", "source.resolve-secret/1",
        ]
        # FEA-12 (M2-C1 rev 2.13 §5.13/§5.14): the delete/trash runtime is
        # assembled with the production library repository + managed storage,
        # so the three frozen capability names are advertised only when that
        # stack exists (the same conditional pattern as the source.sync caps;
        # a minimal hand-built Core must not claim faces it cannot serve).
        # The host MUST probe these before dispatch (missing ->
        # CORE_CAPABILITY_MISSING) instead of probing with the command itself.
        # ``library.trash.write/1`` covers MoveToTrash and RestoreFromTrash
        # only -- PurgeTrash stays unimplemented in this release and fails
        # closed with a typed UNKNOWN_COMMAND.
        if (
            getattr(self._core, "repository", None) is not None
            and getattr(self._core, "storage", None) is not None
        ):
            capabilities.extend(_FEA12_CAPABILITIES)
        # FEA-11 (C-17 §4): the source.sync capabilities are advertised only
        # when the sync stack is actually assembled; the Host probes them
        # before any sync dispatch (CORE_CAPABILITY_MISSING otherwise).
        # C-17 v1.1: ``source.sync.enumerate/1`` joins the ping list ONLY —
        # the Host-side §5.2 Capabilities DTO keeps its frozen 7 items.
        if getattr(self._core, "source_sync", None) is not None:
            capabilities.extend(
                (
                    "source.sync.scan/1", "source.sync.plan/1",
                    "source.sync.apply/1", "source.sync.relink/1",
                    "source.sync.repoint/1", "source.sync.resync/1",
                    "source.sync.operation/1", "source.sync.enumerate/1",
                )
            )
        return {
            "status": "ready",
            "protocol_version": {
                "major": PROTOCOL_MAJOR,
                "minor": PROTOCOL_MINOR,
            },
            "capabilities": capabilities,
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

    # ------------------------------------------------------------------
    # FEA-12: delete preview (PD-01/PD-03) + C flow permanent delete
    # (PD-02/PD-04/PD-05/PD-06/PD-07/PD-08/PD-09) + A flow trash commands
    # ------------------------------------------------------------------

    def _delete_error(
        self,
        code: str,
        category: str,
        retryable: bool | str = False,
        details: dict | None = None,
    ) -> dict[str, Any]:
        error: dict[str, Any] = {
            "code": code,
            "category": category,
            "retryable": retryable,
        }
        if details is not None:
            error["details"] = details
        return error

    def _delete_target_state(
        self, book_id: str, target_book_ids: list[str]
    ) -> tuple[str, dict[str, Any] | None]:
        """``(state, raw_inventory)`` for one target.

        ``book`` — a live Book row exists; ``retry`` — the Book row is gone but
        a committed delete left a readable cleanup manifest (PD-07 retry, no
        new preview is possible); ``corrupt`` — the Book row is gone and the
        manifest row exists but its JSON payload is unreadable (fail closed as
        STALE per C-04b v1.1 §2.2); ``missing`` — neither (BOOK_NOT_FOUND).
        """
        inventory = self._core.repository.book_delete_inventory(
            book_id, target_book_ids, storage=self._core.storage
        )
        if inventory is not None:
            return "book", inventory
        manifest_status, _ = self._core.repository.get_cleanup_manifest_state(
            book_id
        )
        if manifest_status == "ok":
            return "retry", None
        if manifest_status == "corrupt":
            return "corrupt", None
        return "missing", None

    def _derived_cleanup_entries(self, book_id: str) -> list[dict[str, str]]:
        """Catalog preview / page-original derived files the cleanup removes.

        r1 R-001: PD-01/C-04b require ``deletedFiles``/``deletedBytes`` to
        cover *managed/derived* files, and ``cleanup_book_files`` removes two
        derived families besides the managed sweep list:

        * artifact preview resources published into the derived root
          (``RenderPreviewPublisher`` / catalog ``preview-<uuid>`` entries);
        * page-original preview resources (``page-original-<page_id>``).

        The disclosure is computed from the same catalog lookups the cleanup
        path uses, so what is disclosed is exactly what will be removed.  When
        no preview publisher is assembled the derived families are empty (the
        cleanup path then has nothing to remove either).  A catalog read
        failure is NOT swallowed: an incomplete disclosure must surface as the
        retryable ``BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`` instead of
        a silently under-reported inventory (PD-01/PD-03).
        """
        publisher = self._render_previews
        if publisher is None:
            return []
        catalog = getattr(publisher, "_catalog", None)
        derived_root = getattr(publisher, "_root", None)
        if catalog is None or derived_root is None:
            return []
        repository = self._core.repository
        page_ids = repository.list_book_page_ids(book_id)
        if not page_ids:
            manifest = repository.get_cleanup_manifest_data(book_id)
            if manifest:
                page_ids = list(manifest.get("page_ids", []))
        resource_ids: list[str] = list(
            catalog.preview_resource_ids_for_artifacts(
                repository.list_page_artifact_ids(page_ids)
            )
        )
        resource_ids.extend(f"page-original-{page_id}" for page_id in page_ids)
        entries: list[dict[str, str]] = []
        seen: set[str] = set()
        for resource_id in resource_ids:
            if resource_id in seen:
                continue
            seen.add(resource_id)
            entry = catalog.lookup(resource_id)
            rel_path = getattr(entry, "rel_path", None) if entry is not None else None
            if not rel_path:
                continue
            entries.append({"resource_id": resource_id, "rel_path": str(rel_path)})
        return entries

    def _finalize_delete_inventory(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Complete the PD-01 inventory with Core-only facts.

        * ``currentRevisionId``: Lead ruling 2026-11-05 — the first
          *lineage-visible* region current revision in reading order (the
          released FEA-11 read semantics; hidden regions are not "visible"),
          falling back to the first artifact current pointer, else null.
        * ``draftPageCount``: active C-13 drafts over the book's pages.
        * active export runtime probes are folded into the ``BOOK_BUSY``
          facts (an in-flight export has no persistent row yet).
        * ``sharedFileRefs``: managed shared files (opaque hashed id) plus
          shared referenced-source entries.
        * ``deletedFiles``/``deletedBytes``: the managed sweep list **plus the
          catalog preview / page-original derived files** the cleanup removes
          (r1 R-001), de-duplicated by absolute path.

        * C-04b **v1.1** (Codex OVERTURN 3a / CONTRACT-UNFREEZE §A1): the
          *binding* values are the complete current sets —
          ``currentRegionRevisionIds`` (**every** region current, including
          lineage-hidden/separate/detached history; Codex ruling: "lineage
          invisible != this historical protection cannot be deleted") and
          ``currentArtifactRevisionIds`` (every artifact current); both are
          lexicographically sorted + de-duplicated.  ``currentRevisionId``
          stays only as a representative display value (reading order +
          lineage visibility) and is NOT part of digest v2.
        """
        inventory = dict(raw)
        repository = self._core.repository
        current_region_revision_ids: list[str] = []
        seen_region_revisions: set[str] = set()
        for pointer in raw["region_current_pointers"]:
            revision_id = pointer["current_revision_id"]
            if revision_id is None or revision_id in seen_region_revisions:
                continue
            seen_region_revisions.add(revision_id)
            current_region_revision_ids.append(revision_id)
        current_artifact_revision_ids: list[str] = []
        seen_artifact_revisions: set[str] = set()
        for pointer in raw["artifact_current_pointers"]:
            revision_id = pointer["current_revision_id"]
            if revision_id is None or revision_id in seen_artifact_revisions:
                continue
            seen_artifact_revisions.add(revision_id)
            current_artifact_revision_ids.append(revision_id)
        # Contract v1.1 wording is "排序去重": deterministic lexicographic order
        # (the canonical digest sorts the same arrays, so DTO/canonical agree).
        inventory["current_region_revision_ids"] = sorted(
            set(current_region_revision_ids)
        )
        inventory["current_artifact_revision_ids"] = sorted(
            set(current_artifact_revision_ids)
        )
        # Representative display value only (no binding responsibility): the
        # first lineage-visible region current, else the first artifact
        # current, else null (Lead ruling 2026-11-05).
        current_revision_id: str | None = None
        guard = getattr(self._core, "lineage_guard", None)
        for pointer in raw["region_current_pointers"]:
            revision_id = pointer["current_revision_id"]
            if revision_id is None:
                continue
            if guard is not None:
                try:
                    readable = guard.is_region_readable(
                        page_id=pointer["page_id"],
                        region_id=pointer["region_id"],
                        revision_id=revision_id,
                    )
                except Exception:
                    readable = False
                if not readable:
                    continue
            current_revision_id = revision_id
            break
        if current_revision_id is None and current_artifact_revision_ids:
            current_revision_id = current_artifact_revision_ids[0]
        inventory["current_revision_id"] = current_revision_id
        inventory["current_revision_count"] = len(
            raw["region_current_pointers"]
        ) + len(raw["artifact_current_pointers"])
        inventory["pinned_revision_count"] = len(raw["pinned_revision_ids"])
        inventory["active_run_count"] = len(raw["active_run_ids"])
        active_export_count = len(raw["active_export_ids"])
        if self._exports is not None:
            try:
                if self._exports.has_active_exports_for_book(raw["book_id"]):
                    active_export_count += 1
            except Exception:
                active_export_count += 1
        inventory["active_export_count"] = active_export_count
        draft_page_count = 0
        drafts = getattr(self._core, "drafts", None)
        if drafts is not None:
            try:
                page_ids = set(repository.list_book_page_ids(raw["book_id"]))
                draft_page_count = len(
                    {
                        draft.page_id
                        for draft in drafts.list_drafts()
                        if getattr(draft, "status", None) is not None
                        and getattr(draft.status, "value", draft.status) == "active"
                        and getattr(draft, "page_id", None) in page_ids
                    }
                )
            except Exception:
                draft_page_count = 0
        inventory["draft_page_count"] = draft_page_count
        inventory["shared_file_refs"] = shared_file_refs(
            raw["shared_managed_targets"], raw["shared_source_entries"]
        )
        inventory["unsafe_shared_ref_count"] = (
            1 if raw["source_graph_conflict"] else 0
        )
        # r1 R-001: disclose the derived preview/page-original files that the
        # cleanup phase removes (same lookups as ``_collect_delete_targets``).
        deleted_files = int(raw["deleted_files"])
        deleted_bytes = int(raw["deleted_bytes"])
        counted_paths: set[str] = set()
        try:
            for relative_path in raw["cleanup_targets"]:
                absolute = Path(
                    self._core.storage.absolute_path(relative_path)
                )
                counted_paths.add(
                    os.path.normcase(os.path.abspath(str(absolute)))
                )
        except Exception:
            counted_paths = set()
        derived_root = getattr(self._render_previews, "_root", None)
        derived_count = 0
        if derived_root is not None:
            derived_base = os.path.abspath(str(derived_root))
            for entry in self._derived_cleanup_entries(raw["book_id"]):
                absolute = os.path.normcase(
                    os.path.abspath(os.path.join(derived_base, entry["rel_path"]))
                )
                if absolute in counted_paths:
                    continue
                counted_paths.add(absolute)
                derived_count += 1
                deleted_files += 1
                try:
                    deleted_bytes += int(Path(absolute).stat().st_size)
                except OSError:
                    pass
        inventory["deleted_files"] = deleted_files
        inventory["deleted_bytes"] = deleted_bytes
        inventory["derived_cleanup_files"] = derived_count
        return inventory

    @staticmethod
    def _protection_facts(inventory: dict[str, Any]) -> ProtectionFacts:
        return ProtectionFacts(
            lock_count=inventory["lock_count"],
            manual_region_count=inventory["manual_region_count"],
            current_revision_count=inventory.get("current_revision_count", 0),
            pinned_revision_count=inventory.get("pinned_revision_count", 0),
            draft_page_count=inventory.get("draft_page_count", 0),
            active_run_count=inventory.get("active_run_count", 0),
            active_export_count=inventory.get("active_export_count", 0),
            unsafe_shared_ref_count=inventory.get("unsafe_shared_ref_count", 0),
        )

    def _permanent_delete_policy_error(
        self, inventory: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Translate the shared ``ProtectionPolicy`` verdict into the delete
        command's typed error (ADJ-001 PD-01 / PD-08).  Disclosure-only
        facts are not blocks: the digest confirmation above already bound the
        disclosure (PD-02)."""
        verdict = ProtectionPolicy.evaluate(
            ProtectionScope.PERMANENT_DELETE, self._protection_facts(inventory)
        )
        if not verdict.blocked:
            return None
        if verdict.reasons and verdict.reasons[0] == "BOOK_BUSY":
            return self._delete_error("BOOK_BUSY", "conflict")
        return self._delete_error("BOOK_DELETE_CONFLICT", "conflict")

    @staticmethod
    def _preview_item_dto(inventory: dict[str, Any]) -> dict[str, Any]:
        return {
            "bookId": inventory["book_id"],
            "title": inventory["title"],
            "protection": {
                "lockCount": inventory["lock_count"],
                # C-04b v1.1: complete current sets carry the binding; the
                # single value below is display-only.
                "currentRevisionId": inventory["current_revision_id"],
                "currentRegionRevisionIds": list(
                    inventory["current_region_revision_ids"]
                ),
                "currentArtifactRevisionIds": list(
                    inventory["current_artifact_revision_ids"]
                ),
                "pinnedRevisionIds": list(inventory["pinned_revision_ids"]),
                "activeRunIds": list(inventory["active_run_ids"]),
                "draftPageCount": inventory["draft_page_count"],
                "manualRegionCount": inventory["manual_region_count"],
            },
            "contentSummary": {
                "chapters": inventory["chapters"],
                "pages": inventory["pages"],
                "artifacts": inventory["artifacts"],
                "deletedFiles": inventory["deleted_files"],
                "deletedBytes": inventory["deleted_bytes"],
            },
            "sharedFileRefs": [
                {
                    "fileId": ref["fileId"],
                    "otherProjectCount": ref["otherProjectCount"],
                }
                for ref in inventory["shared_file_refs"]
            ],
        }

    def handle_preview_permanent_delete_books(
        self, raw_payload: Any
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        """§5.13 read-only deletion preview: zero side effects (PD-03).

        Rows are only SELECTed; nothing is written, no file is touched and no
        protection state is pre-cleared.  Any DB failure is the typed
        ``BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`` (zero side effects),
        never an empty/fabricated inventory.
        """
        if not isinstance(raw_payload, dict) or set(raw_payload) != {"bookIds"}:
            return None, self._delete_error("INVALID_REQUEST", "validation")
        book_ids = raw_payload.get("bookIds")
        if (
            not isinstance(book_ids, list)
            or not book_ids
            or len(book_ids) > 20
            or len(book_ids) != len(set(book_ids))
            or not all(isinstance(book_id, str) and book_id.strip() for book_id in book_ids)
        ):
            return None, self._delete_error("INVALID_REQUEST", "validation")
        try:
            items: list[dict[str, Any]] = []
            for book_id in book_ids:
                state, raw_inventory = self._delete_target_state(book_id, book_ids)
                if state == "missing":
                    return None, self._delete_error("BOOK_NOT_FOUND", "not_found")
                if state == "retry":
                    # §5.13: a target with no Book row is BOOK_NOT_FOUND; the
                    # PD-07 cleanup retry does not re-run the preview.
                    return None, self._delete_error("BOOK_NOT_FOUND", "not_found")
                items.append(self._finalize_delete_inventory(raw_inventory or {}))
        except Exception:
            return None, self._delete_error(
                "BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE", "unavailable", True
            )
        digests = {
            inventory["book_id"]: inventory_digest(inventory)
            for inventory in items
        }
        return (
            {
                "inventoryDigest": collection_inventory_digest(book_ids, digests),
                "inventoryDigests": digests,
                "computedAt": datetime.now(timezone.utc).isoformat(
                    timespec="milliseconds"
                ),
                "items": [self._preview_item_dto(inventory) for inventory in items],
            },
            None,
        )

    # -- A flow: recycle-bin command surface (C-09 SC-B06) ---------------

    def _validate_trash_write_payload(
        self, raw_payload: Any
    ) -> tuple[list[str] | None, dict[str, Any] | None]:
        if not isinstance(raw_payload, dict) or set(raw_payload) != {
            "entries",
            "idempotency_key",
        }:
            return None, self._delete_error("INVALID_REQUEST", "validation")
        book_ids, error_code = normalize_trash_entries(raw_payload.get("entries"))
        if error_code is not None or book_ids is None:
            return None, self._delete_error(error_code or "INVALID_REQUEST", "validation")
        if not is_valid_idempotency_key(raw_payload.get("idempotency_key")):
            return None, self._delete_error("INVALID_REQUEST", "validation")
        # Task-level idempotency semantics (M2-C1 §5.14 leaves it to the
        # implementing task): the key is required and validated, and a replay
        # is naturally per-item idempotent — an already-moved entry is
        # reported as skipped and an already-restored entry as a conflict,
        # with zero additional side effects.  No hidden cross-process retry
        # cache exists in the first release.
        return book_ids, None

    def handle_move_to_trash(
        self, raw_payload: Any
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        book_ids, error = self._validate_trash_write_payload(raw_payload)
        if error is not None:
            return None, error
        moved: list[dict[str, Any]] = []
        skipped: list[dict[str, Any]] = []
        for book_id in book_ids or []:
            try:
                inventory = self._core.repository.book_delete_inventory(
                    book_id, [book_id]
                )
            except Exception:
                inventory = None
            if inventory is not None:
                # C-09 SC-B04a: the SAME ProtectionPolicy decides all three
                # paths; for soft delete no protection fact blocks (the data
                # is preserved verbatim and restore clears only deleted_at).
                verdict = ProtectionPolicy.evaluate(
                    ProtectionScope.SOFT_DELETE,
                    self._protection_facts(
                        {
                            **inventory,
                            "current_revision_count": 0,
                            "pinned_revision_count": len(
                                inventory["pinned_revision_ids"]
                            ),
                            "active_run_count": len(inventory["active_run_ids"]),
                            "active_export_count": len(inventory["active_export_ids"]),
                            "draft_page_count": 0,
                            "unsafe_shared_ref_count": 0,
                        }
                    ),
                )
                if not verdict.blocked:
                    try:
                        if self._core.repository.move_book_to_trash(book_id):
                            moved.append({"book_id": book_id})
                            continue
                    except sqlite3.Error:
                        pass
            skipped.append(
                {"ref": {"book_id": book_id}, "reason": "TRASH_ENTRY_NOT_FOUND"}
            )
        return {"moved": moved, "skipped": skipped}, None

    def handle_restore_from_trash(
        self, raw_payload: Any
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        book_ids, error = self._validate_trash_write_payload(raw_payload)
        if error is not None:
            return None, error
        restored: list[dict[str, Any]] = []
        conflicts: list[dict[str, Any]] = []
        for book_id in book_ids or []:
            try:
                ok = self._core.repository.restore_book_from_trash(book_id)
            except sqlite3.Error:
                ok = False
            if ok:
                restored.append({"book_id": book_id})
            else:
                conflicts.append(
                    {"ref": {"book_id": book_id}, "reason": "TRASH_ENTRY_NOT_FOUND"}
                )
        return {"restored": restored, "conflicts": conflicts}, None

    def handle_list_trash(
        self, raw_payload: Any
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        if not isinstance(raw_payload, dict) or set(raw_payload) - {"cursor", "limit"}:
            return None, self._delete_error("INVALID_REQUEST", "validation")
        after: tuple[str, str] | None = None
        cursor = raw_payload.get("cursor")
        if cursor is not None:
            after = decode_trash_cursor(cursor)
            if after is None:
                return None, self._delete_error("INVALID_REQUEST", "validation")
        limit = raw_payload.get("limit", _TRASH_DEFAULT_LIMIT)
        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or limit < 1
            or limit > _TRASH_MAX_LIMIT
        ):
            return None, self._delete_error("INVALID_REQUEST", "validation")
        rows = self._core.repository.list_trash_entries(after=after, limit=limit)
        has_next = len(rows) > limit
        page_rows = rows[:limit]
        result: dict[str, Any] = {
            "items": [
                {
                    "bookId": row["book_id"],
                    "title": row["title"],
                    "deletedAt": row["deleted_at"],
                }
                for row in page_rows
            ]
        }
        if has_next and page_rows:
            last = page_rows[-1]
            result["nextCursor"] = encode_trash_cursor(
                last["deleted_at"], last["book_id"]
            )
        return result, None

    def handle_purge_trash(
        self, raw_payload: Any
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        """M2-C1 §5.14: registered on the frozen wire, NOT implemented in the
        first CORE release (digest binding needs a separate DSH additive
        ruling).  Fail closed with the typed unsupported face; never fall
        through to an implicit permanent delete and never a silent success."""
        del raw_payload
        return None, self._delete_error("UNKNOWN_COMMAND", "validation")

    # -- C flow: permanent delete commands --------------------------------

    def _validate_single_delete_payload(
        self, raw_payload: Any
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        if not isinstance(raw_payload, dict) or set(raw_payload) != {
            "book_id",
            "confirm_permanent_delete",
            "inventory_digest",
        }:
            return None, self._delete_error("INVALID_REQUEST", "validation")
        book_id = raw_payload.get("book_id")
        if not isinstance(book_id, str) or not book_id.strip():
            return None, self._delete_error("INVALID_REQUEST", "validation")
        if raw_payload.get("confirm_permanent_delete") is not True:
            return None, self._delete_error("INVALID_REQUEST", "validation")
        if not is_inventory_digest(raw_payload.get("inventory_digest")):
            return None, self._delete_error("INVALID_REQUEST", "validation")
        return raw_payload, None

    def _validate_batch_delete_payload(
        self, raw_payload: Any
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        expected_keys = {
            "book_ids",
            "confirmed_book_ids",
            "confirm_count",
            "confirm_permanent_delete",
            "inventory_digest",
            "inventory_digests",
        }
        if not isinstance(raw_payload, dict) or set(raw_payload) != expected_keys:
            return None, self._delete_error("INVALID_REQUEST", "validation")
        book_ids = raw_payload.get("book_ids")
        confirmed_book_ids = raw_payload.get("confirmed_book_ids")
        confirm_count = raw_payload.get("confirm_count")
        if not isinstance(book_ids, list) or not isinstance(confirmed_book_ids, list):
            return None, self._delete_error("INVALID_REQUEST", "validation")
        if not all(isinstance(book_id, str) and book_id.strip() for book_id in book_ids):
            return None, self._delete_error("INVALID_REQUEST", "validation")
        if len(book_ids) == 0:
            return None, self._delete_error("INVALID_REQUEST", "validation")
        if len(book_ids) > 20:
            return None, self._delete_error(
                "BOOK_DELETE_BATCH_LIMIT_EXCEEDED", "validation"
            )
        if len(book_ids) != len(set(book_ids)):
            return None, self._delete_error("DUPLICATE_BOOK_ID", "validation")
        if type(confirm_count) is not int or confirm_count != len(book_ids):
            return None, self._delete_error("INVALID_REQUEST", "validation")
        if confirmed_book_ids != book_ids:
            return None, self._delete_error("INVALID_REQUEST", "validation")
        if raw_payload.get("confirm_permanent_delete") is not True:
            return None, self._delete_error("INVALID_REQUEST", "validation")
        if not is_inventory_digest(raw_payload.get("inventory_digest")):
            return None, self._delete_error("INVALID_REQUEST", "validation")
        digests = raw_payload.get("inventory_digests")
        if not isinstance(digests, dict) or not all(
            isinstance(key, str) and is_inventory_digest(value)
            for key, value in digests.items()
        ):
            return None, self._delete_error("INVALID_REQUEST", "validation")
        # C-04b v1.1 §2.2: the per-book map's key set must be exactly the
        # request's book_ids; missing/extra keys are a request-shape error
        # (INVALID_REQUEST), not a stale-preview value mismatch.
        if set(digests) != set(book_ids):
            return None, self._delete_error("INVALID_REQUEST", "validation")
        return raw_payload, None

    def _collect_delete_targets(
        self, book_ids: list[str]
    ) -> tuple[dict[str, list[str]], dict[str, list[str]], dict[str, list[str]]]:
        """(targets, page_ids, preview_resource_ids) maps for the delete."""
        repository = self._core.repository
        targets_map = repository.cleanup_targets_for_delete(book_ids)
        page_ids_map: dict[str, list[str]] = {}
        for book_id in book_ids:
            page_ids = repository.list_book_page_ids(book_id)
            if not page_ids:
                manifest = repository.get_cleanup_manifest_data(book_id)
                if manifest:
                    page_ids = manifest.get("page_ids", [])
            page_ids_map[book_id] = list(page_ids)
        preview_ids_map: dict[str, list[str]] = {}
        preview_catalog = getattr(self._render_previews, "_catalog", None)
        if preview_catalog is not None:
            for book_id, page_ids in page_ids_map.items():
                preview_ids_map[book_id] = (
                    preview_catalog.preview_resource_ids_for_artifacts(
                        repository.list_page_artifact_ids(page_ids)
                    )
                )
        return targets_map, page_ids_map, preview_ids_map

    def _cleanup_after_delete(
        self,
        book_ids: list[str],
        targets_map: dict[str, list[str]],
        page_ids_map: dict[str, list[str]],
        preview_ids_map: dict[str, list[str]],
    ) -> tuple[list[dict[str, Any]], bool]:
        repository = self._core.repository
        storage = self._core.storage
        items: list[dict[str, Any]] = []
        has_pending = False
        for book_id in book_ids:
            cleaned = repository.cleanup_book_files(
                book_id,
                targets_map.get(book_id, []),
                storage,
                render_previews=self._render_previews,
                page_ids=page_ids_map.get(book_id, []),
                preview_resource_ids=preview_ids_map.get(book_id, []),
            )
            if cleaned:
                items.append(
                    {"book_id": book_id, "status": "deleted", "error_code": None}
                )
            else:
                has_pending = True
                items.append(
                    {
                        "book_id": book_id,
                        "status": "cleanup_pending",
                        "error_code": None,
                    }
                )
        return items, has_pending

    def handle_permanently_delete_book(
        self, raw_payload: Any
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        """§5.11.1 + §5.11.1a single permanent delete.

        Confirmation is bound to the Core-computed per-book inventory digest
        (PD-02/PD-04); the delete itself is one explicit ``BEGIN IMMEDIATE``
        transaction (PD-05) whose failure leaves everything unchanged
        (PD-06); file cleanup runs only after the DB commit and a refused
        cleanup is retryable via the persisted manifest (PD-07).
        """
        validated, error = self._validate_single_delete_payload(raw_payload)
        if error is not None:
            return None, error
        assert validated is not None
        book_id = validated["book_id"]
        supplied_digest = validated["inventory_digest"]
        repository = self._core.repository
        storage = self._core.storage
        batch_id: str | None = None
        original_book_ids: list[str] = []
        original_collection_digest: str | None = None
        book_inputs: dict[str, Any] = {}
        with self._write_lock:
            try:
                state, raw_inventory = self._delete_target_state(book_id, [book_id])
            except Exception:
                return None, self._delete_error(
                    "BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE",
                    "unavailable",
                    True,
                )
            if state == "missing":
                return None, self._delete_error("BOOK_NOT_FOUND", "not_found")
            if state == "corrupt":
                # C-04b v1.1 §2.2: manifest missing/corrupt/tampered =>
                # BOOK_DELETE_STALE_PREVIEW (zero side effects), never a
                # BOOK_NOT_FOUND masquerade.
                return None, self._delete_error(
                    "BOOK_DELETE_STALE_PREVIEW", "conflict"
                )
            if state == "book":
                try:
                    inventory = self._finalize_delete_inventory(raw_inventory or {})
                except Exception:
                    return None, self._delete_error(
                        "BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE",
                        "unavailable",
                        True,
                    )
                expected_digest = inventory_digest(inventory)
                if supplied_digest != expected_digest:
                    return None, self._delete_error(
                        "BOOK_DELETE_STALE_PREVIEW", "conflict"
                    )
                # C-04b v1.1 §2.2: persist the original batch binding in the
                # manifest (JSON additive) so a later PD-07 retry can validate
                # the original collection digest verbatim.
                batch_id = uuid.uuid4().hex
                original_book_ids = [book_id]
                original_collection_digest = collection_inventory_digest(
                    [book_id], {book_id: expected_digest}
                )
                book_inputs = {book_id: canonical_inventory_payload(inventory)}
                policy_error = self._permanent_delete_policy_error(inventory)
                if policy_error is not None:
                    return None, policy_error
                all_ok, items = repository.preflight_permanent_delete(
                    [book_id], storage=storage, export_runtime=self._exports
                )
                if not all_ok:
                    code = items[0]["error_code"] or "BOOK_DELETE_CONFLICT"
                    category = "not_found" if code == "BOOK_NOT_FOUND" else "conflict"
                    return None, self._delete_error(code, category)
            else:
                # C-04b v1.1 §2.2: a PD-07 retry target has no Book row to
                # re-preview.  The per-book digest confirmed before the commit
                # is persisted in its manifest, re-verified against the
                # persisted canonical binding inputs (tamper detection), and
                # must match the request exactly — never a shape-only pass
                # (Codex OVERTURN 4).
                manifest = repository.get_cleanup_manifest_data(book_id) or {}
                expected_digest = manifest.get("inventory_digest")
                stored_inputs = manifest.get("inventory_inputs")
                if (
                    not is_inventory_digest(expected_digest)
                    or supplied_digest != expected_digest
                    or not isinstance(stored_inputs, dict)
                    or manifest.get("book_id") != book_id
                    or canonical_payload_digest(stored_inputs) != expected_digest
                ):
                    return None, self._delete_error(
                        "BOOK_DELETE_STALE_PREVIEW", "conflict"
                    )
            targets_map, page_ids_map, preview_ids_map = self._collect_delete_targets(
                [book_id]
            )
            try:
                repository.execute_permanent_delete_db(
                    {book_id: targets_map[book_id]},
                    {book_id: page_ids_map.get(book_id, [])},
                    {book_id: preview_ids_map.get(book_id, [])},
                    {book_id: expected_digest},
                    batch_id if state == "book" else None,
                    original_book_ids if state == "book" else None,
                    original_collection_digest if state == "book" else None,
                    book_inputs if state == "book" else None,
                )
            except PermanentDeleteBlockedError as caught:
                return None, self._delete_error(caught.code, "conflict")
            except Exception:
                return None, self._delete_error(
                    "BOOK_DELETE_FAILED", "internal", "unknown"
                )
            result_items, has_pending = self._cleanup_after_delete(
                [book_id], targets_map, page_ids_map, preview_ids_map
            )
            if has_pending:
                return None, self._delete_error(
                    "BOOK_DELETE_CLEANUP_PENDING", "internal", True
                )
            return {"book_id": book_id, "deleted": True}, None

    def handle_permanently_delete_books(
        self, raw_payload: Any
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        """§5.11.1 + §5.11.1a batch permanent delete (two-level digest).

        DB deletion is all-or-nothing in one transaction; the post-commit file
        cleanup reports per book (PD-09) and a refused cleanup stays
        retryable (PD-07)."""
        validated, error = self._validate_batch_delete_payload(raw_payload)
        if error is not None:
            return None, error
        assert validated is not None
        book_ids: list[str] = list(validated["book_ids"])
        supplied_collection_digest = validated["inventory_digest"]
        supplied_digests: dict[str, str] = dict(validated["inventory_digests"])
        repository = self._core.repository
        storage = self._core.storage
        with self._write_lock:
            if repository.is_whole_library(book_ids):
                return None, self._delete_error(
                    "BOOK_DELETE_BATCH_WHOLE_LIBRARY", "conflict"
                )
            try:
                states: dict[str, str] = {}
                inventories: dict[str, dict[str, Any]] = {}
                for book_id in book_ids:
                    state, raw_inventory = self._delete_target_state(book_id, book_ids)
                    states[book_id] = state
                    if state == "book":
                        inventories[book_id] = self._finalize_delete_inventory(
                            raw_inventory or {}
                        )
            except Exception:
                return None, self._delete_error(
                    "BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE",
                    "unavailable",
                    True,
                )
            corrupt = [book_id for book_id in book_ids if states[book_id] == "corrupt"]
            if corrupt:
                return None, self._stale_preview_error(book_ids, corrupt)
            missing = [book_id for book_id in book_ids if states[book_id] == "missing"]
            if missing:
                items = [
                    {
                        "book_id": book_id,
                        "status": "not_started",
                        "error_code": (
                            "BOOK_NOT_FOUND" if states[book_id] == "missing" else None
                        ),
                    }
                    for book_id in book_ids
                ]
                return None, self._delete_error(
                    "BOOK_DELETE_BATCH_PREFLIGHT_FAILED",
                    "conflict",
                    details={
                        "phase": "preflight",
                        "requested_count": len(book_ids),
                        "completed_count": 0,
                        "items": items,
                    },
                )
            retry_ids = [book_id for book_id in book_ids if states[book_id] == "retry"]
            live_ids = [book_id for book_id in book_ids if states[book_id] == "book"]
            # C-04b v1.1 §2.2 (Codex OVERTURN 4): retry is only a pending
            # subset of the original preview; **mixed live+retry is NOT
            # allowed** (the caller must re-preview).  A pure retry passes the
            # manifest's original collection digest through verbatim (never
            # recomputed for the subset); a pure live batch recomputes the
            # per-book digests and the collection digest over the request.
            if retry_ids and live_ids:
                return None, self._stale_preview_error(book_ids, book_ids)
            expected_digests: dict[str, str] = {}
            if retry_ids:
                manifests: dict[str, Any] = {}
                for book_id in retry_ids:
                    manifest = repository.get_cleanup_manifest_data(book_id)
                    if not isinstance(manifest, dict):
                        return None, self._stale_preview_error([book_id], [book_id])
                    manifests[book_id] = manifest
                first = manifests[retry_ids[0]]
                batch_id = first.get("batch_id")
                original_ids = first.get("original_book_ids")
                original_collection = first.get("original_collection_digest")
                if (
                    not isinstance(batch_id, str)
                    or not batch_id
                    or not isinstance(original_ids, list)
                    or not is_inventory_digest(original_collection)
                ):
                    return None, self._stale_preview_error(book_ids, retry_ids)
                pending_set = set(retry_ids)
                ordered_subset = [
                    item for item in original_ids if item in pending_set
                ]
                if ordered_subset != retry_ids or len(original_ids) < len(retry_ids):
                    return None, self._stale_preview_error(book_ids, retry_ids)
                if supplied_collection_digest != original_collection:
                    return None, self._stale_preview_error(book_ids, book_ids)
                for book_id in retry_ids:
                    manifest = manifests[book_id]
                    stored = manifest.get("inventory_digest")
                    inputs = manifest.get("inventory_inputs")
                    if (
                        manifest.get("batch_id") != batch_id
                        or manifest.get("original_book_ids") != original_ids
                        or manifest.get("original_collection_digest")
                        != original_collection
                        or manifest.get("book_id") != book_id
                        or not is_inventory_digest(stored)
                        or supplied_digests[book_id] != stored
                        or not isinstance(inputs, dict)
                        or canonical_payload_digest(inputs) != stored
                    ):
                        return None, self._stale_preview_error(
                            [book_id], [book_id]
                        )
                    expected_digests[book_id] = stored
            else:
                expected_digests = {
                    book_id: inventory_digest(inventories[book_id])
                    for book_id in book_ids
                }
                mismatched = [
                    book_id
                    for book_id in book_ids
                    if supplied_digests[book_id] != expected_digests[book_id]
                ]
                expected_collection = collection_inventory_digest(
                    book_ids, expected_digests
                )
                if mismatched or supplied_collection_digest != expected_collection:
                    return None, self._stale_preview_error(book_ids, mismatched)
            policy_errors: dict[str, str] = {}
            for book_id, inventory in inventories.items():
                policy_error = self._permanent_delete_policy_error(inventory)
                if policy_error is not None:
                    policy_errors[book_id] = policy_error["code"]
            if policy_errors:
                return None, self._delete_error(
                    "BOOK_DELETE_BATCH_PREFLIGHT_FAILED",
                    "conflict",
                    details={
                        "phase": "preflight",
                        "requested_count": len(book_ids),
                        "completed_count": 0,
                        "items": [
                            {
                                "book_id": book_id,
                                "status": "not_started",
                                "error_code": policy_errors.get(book_id),
                            }
                            for book_id in book_ids
                        ],
                    },
                )
            all_ok, items = repository.preflight_permanent_delete(
                book_ids, storage=storage, export_runtime=self._exports
            )
            if not all_ok:
                return None, self._delete_error(
                    "BOOK_DELETE_BATCH_PREFLIGHT_FAILED",
                    "conflict",
                    details={
                        "phase": "preflight",
                        "requested_count": len(book_ids),
                        "completed_count": 0,
                        "items": items,
                    },
                )
            targets_map, page_ids_map, preview_ids_map = self._collect_delete_targets(
                book_ids
            )
            live_batch_id: str | None = None
            live_original_ids: list[str] = []
            live_collection: str | None = None
            live_inputs: dict[str, Any] = {}
            if not retry_ids:
                live_batch_id = uuid.uuid4().hex
                live_original_ids = list(book_ids)
                live_collection = collection_inventory_digest(
                    book_ids, expected_digests
                )
                live_inputs = {
                    book_id: canonical_inventory_payload(inventory)
                    for book_id, inventory in inventories.items()
                }
            try:
                repository.execute_permanent_delete_db(
                    {book_id: targets_map[book_id] for book_id in book_ids},
                    {book_id: page_ids_map.get(book_id, []) for book_id in book_ids},
                    {
                        book_id: preview_ids_map.get(book_id, [])
                        for book_id in book_ids
                    },
                    {book_id: expected_digests[book_id] for book_id in book_ids},
                    live_batch_id,
                    live_original_ids,
                    live_collection,
                    live_inputs,
                )
            except PermanentDeleteBlockedError as caught:
                # r1 R-009: use the code/attribution carried by the write
                # boundary itself (preflight passed, then the state changed).
                # The batch surfaces the typed BOOK_BUSY at the top level and
                # attributes the exact item; the other items stay not_started.
                return None, self._delete_error(
                    caught.code,
                    "conflict",
                    details={
                        "phase": "preflight",
                        "requested_count": len(book_ids),
                        "completed_count": 0,
                        "items": [
                            {
                                "book_id": book_id,
                                "status": "not_started",
                                "error_code": (
                                    caught.code
                                    if book_id == caught.book_id
                                    else None
                                ),
                            }
                            for book_id in book_ids
                        ],
                    },
                )
            except Exception:
                return None, self._delete_error(
                    "BOOK_DELETE_FAILED", "internal", "unknown"
                )
            result_items, has_pending = self._cleanup_after_delete(
                book_ids, targets_map, page_ids_map, preview_ids_map
            )
            completed_count = sum(
                1 for item in result_items if item["status"] == "deleted"
            )
            if has_pending:
                return None, self._delete_error(
                    "BOOK_DELETE_BATCH_CLEANUP_PENDING",
                    "internal",
                    True,
                    details={
                        "phase": "cleanup",
                        "requested_count": len(book_ids),
                        "completed_count": completed_count,
                        "items": result_items,
                    },
                )
            return {
                "requested_count": len(book_ids),
                "completed_count": completed_count,
                "items": result_items,
            }, None

    @staticmethod
    def _stale_preview_error(
        book_ids: list[str], mismatched: list[str]
    ) -> dict[str, Any]:
        mismatch = set(mismatched)
        return {
            "code": "BOOK_DELETE_STALE_PREVIEW",
            "category": "conflict",
            "retryable": False,
            "details": {
                "phase": "preflight",
                "requested_count": len(book_ids),
                "completed_count": 0,
                "items": [
                    {
                        "book_id": book_id,
                        "status": "not_started",
                        "error_code": (
                            "BOOK_DELETE_STALE_PREVIEW"
                            if (not mismatch or book_id in mismatch)
                            else None
                        ),
                    }
                    for book_id in book_ids
                ],
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

                # DETECT-MEMORY-GUARD-1 (SEC-FMT-005 item 1): the pixel cap is
                # a fixed constant; this consults the host. It is a BACKSTOP --
                # on a healthy machine available memory dwarfs the page buffer
                # so this never fires, and the pixel cap above stays the real
                # constraint. A probe failure falls back to the pixel cap (it
                # does NOT fail open past it): the page has already passed the
                # fixed ceiling by the time we get here.
                needed_bytes = (
                    image.width * image.height * _DETECT_BYTES_PER_PIXEL
                )
                avail_bytes = _available_physical_bytes()
                if avail_bytes is not None:
                    budget_bytes = int(avail_bytes * _DETECT_MEMORY_SAFETY_RATIO)
                    if needed_bytes > budget_bytes:
                        avail_mb = avail_bytes / (1024 * 1024)
                        budget_mb = budget_bytes / (1024 * 1024)
                        needed_mb = needed_bytes / (1024 * 1024)
                        raise DetectRequestError(
                            "core.detect page needs more memory than this host "
                            f"can safely spare: {image.width}x{image.height} "
                            f"needs about {needed_mb:.1f} MiB, but only "
                            f"{avail_mb:.1f} MiB is available and the page may "
                            f"claim at most {budget_mb:.1f} MiB "
                            f"({_DETECT_MEMORY_SAFETY_RATIO:.0%} of available). "
                            "Close other applications and retry, reduce the "
                            "page size, or split a tall page into several "
                            "shorter images."
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
            SKIP stays the assembly reader's concern, not rewritten here);
          - the batch-A sections ``ocr`` / ``translate`` / ``inpaint`` /
            ``typeset``: the frozen per-section white-list (SETTINGS-OPEN-A-1,
            design §3.1-§3.4). Unknown keys and illegal values are typed
            ``INVALID_REQUEST`` before any persistence; values are stored
            normalized (JSON types converted).
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
        # SETTINGS-OPEN-A-1 AC1: the four opened batch-A sections are gated by
        # their frozen white-list BEFORE persistence (design §3.5); an unknown
        # section returns None and keeps the historical pass-through.
        try:
            validated = validate_settings_section(section, values)
        except SettingsSectionError as error:
            raise SettingsRequestError(str(error)) from error
        stored = values if validated is None else validated
        try:
            defaults = self._core.pipeline_defaults.save_settings_section(
                section, stored
            )
        except BindingValidationError as error:
            # the service's own structural guard; same typed surface as the
            # pre-validation above (INVALID_REQUEST, never a raw ValueError)
            raise SettingsRequestError(str(error)) from error
        return {"settings": _project_settings_value(dict(defaults.settings))}

    # ------------------------------------------------------------------
    # cleanup.preview / cleanup.run / cleanup.retry_pending
    # (SETTINGS-OPEN-B-2, design §4.3)
    # ------------------------------------------------------------------

    def _require_cleanup(self) -> CleanupService:
        """The injected controlled cleanup use case, or a typed refusal.

        ``None`` means this assembly never wired the service. The refusal
        is CORE_UNAVAILABLE (dispatcher mapping), never an exception that
        escapes the stdio loop.
        """
        service = self._cleanup
        if service is None:
            raise CleanupUnavailableError("cleanup service is not wired")
        return service

    def handle_cleanup_preview(self) -> dict[str, Any]:
        """Read-only pre-flight: which cache files would be removed and how
        many bytes they occupy, plus the persisted pending-failure count.

        The preview only lists targets that pass the same never-clean
        predicate the run face re-checks, so "preview says N" and "run
        touches at most N" can never disagree. Reading never deletes.
        """
        service = self._require_cleanup()
        result = service.preview().to_dict()
        result["pending_cleanups"] = service.pending_cleanup_count()
        return result

    def handle_cleanup_run(self) -> dict[str, Any]:
        """Remove every safe cache target now (idempotent); failed removals
        stay persisted as ``pending_cleanups`` for the retry face."""
        service = self._require_cleanup()
        return _cleanup_outcome_projection(service.run())

    def handle_cleanup_retry_pending(self) -> dict[str, Any]:
        """Retry the persisted pending-removal list; settled entries leave
        the ledger, entries that fail again stay pending."""
        service = self._require_cleanup()
        return _cleanup_outcome_projection(service.retry_pending_cleanups())

    # ------------------------------------------------------------------
    # backup / restore (SETTINGS-OPEN-C-2-BACKUP, design §3.4)
    # ------------------------------------------------------------------

    def _require_backup(self):
        """The assembled ``.nmbak`` service; a Core without one fails closed
        with CORE_UNAVAILABLE instead of crashing the sidecar."""
        service = getattr(self._core, "backup", None)
        if service is None:
            raise NmbakBackupError("CORE_UNAVAILABLE", "backup service is not wired")
        return service

    def handle_backup_create(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Only ``manual`` is exposed: automatic backups have no scheduler
        consumer yet (design §3.2), so a payload asking for another type is
        a malformed request rather than a silent no-op."""
        service = self._require_backup()
        backup_type = payload.get("backup_type", "manual")
        if backup_type != "manual":
            raise NmbakBackupError(
                "INVALID_REQUEST",
                "only backup_type=manual is exposed from the settings panel",
            )
        return service.create("manual", "settings-panel manual backup")

    def handle_backup_list(self) -> list[dict[str, Any]]:
        return self._require_backup().list_backups()

    def handle_backup_restore(self, payload: dict[str, Any]) -> dict[str, Any]:
        service = self._require_backup()
        backup_id = payload.get("backup_id")
        if not isinstance(backup_id, str):
            raise NmbakBackupError("INVALID_REQUEST", "backup_id must be a string")
        if payload.get("confirm_restore") is not True:
            raise NmbakBackupError(
                "BACKUP_RESTORE_REQUIRES_CONFIRMATION", "confirm_restore must be true"
            )
        return service.restore(backup_id, confirm_restore=True)

    def handle_backup_delete(self, payload: dict[str, Any]) -> dict[str, Any]:
        service = self._require_backup()
        backup_id = payload.get("backup_id")
        if not isinstance(backup_id, str):
            raise NmbakBackupError("INVALID_REQUEST", "backup_id must be a string")
        return service.delete(backup_id)


    # ------------------------------------------------------------------
    # local plugin runtime (PLUGIN-RUNTIME-1, design §4.1-§4.4)
    # ------------------------------------------------------------------

    def _require_plugins(self):
        """The assembled plugin runtime; a Core without one fails closed with
        CORE_UNAVAILABLE instead of crashing the sidecar."""
        service = getattr(self._core, "plugins", None)
        if service is None:
            raise PluginError("CORE_UNAVAILABLE", "plugin service is not wired")
        return service

    def handle_plugins_list(self) -> dict[str, Any]:
        return self._require_plugins().list_plugins()

    def handle_plugins_set_enabled(self, payload: dict[str, Any]) -> dict[str, Any]:
        enabled = payload.get("enabled")
        if not isinstance(enabled, bool):
            raise PluginError("PLUGIN_INVALID_REQUEST", "enabled must be a boolean")
        return self._require_plugins().set_global_enabled(enabled)

    def handle_plugins_set_plugin_enabled(self, payload: dict[str, Any]) -> dict[str, Any]:
        plugin_id = payload.get("plugin_id")
        enabled = payload.get("enabled")
        if not isinstance(plugin_id, str) or not isinstance(enabled, bool):
            raise PluginError(
                "PLUGIN_INVALID_REQUEST",
                "plugin_id must be a string and enabled a boolean",
            )
        return self._require_plugins().set_plugin_enabled(plugin_id, enabled)

    def handle_plugins_audit_list(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        limit = payload.get("limit", 50)
        if not isinstance(limit, int) or isinstance(limit, bool):
            raise PluginError("PLUGIN_INVALID_REQUEST", "limit must be an integer")
        return self._require_plugins().audit_list(limit)

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
        # FEA-11-LINEAGE-1: the filtered count is reported (never a silent
        # loss); the region list itself already comes from the guarded service.
        self._log_lineage_hidden("list_regions", page_id)
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

    def handle_list_page_region_texts(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """The RegionTextDetail read channel (V11R-F0-2 / closes GAP-2).

        Studio Page loads ONE page's region list + four-level text in ONE
        round trip. ``list_page_region_texts`` was chosen over a single-region
        ``get_region`` because the page workspace always needs every live
        region of the page: a per-region command would make the first paint
        N+1, while this command is exactly one request.

        Request: ``{"page_id": "<id>", "region_ids"?: ["<id>", ...]}``.
        ``region_ids`` is the optional strict filter: every id must be a LIVE
        region of that page, otherwise TARGET_NOT_FOUND -- this covers
        "unknown region" and "region of another page" (no cross-page read).
        Without the filter all live regions of the page are returned in
        reading_order ascending.

        Result: ``{"page_id", "page_size": {width, height} | null,
        "regions": RegionTextDetail[]}``. Every projected field is the
        persisted value (four-level text, three locks, review_state, origin,
        current revision number/id, is_pinned of the current revision, all
        pinned revision numbers, normalized geometry when the page extent is
        known). A page with no regions -- unknown page_id included -- reads as
        ``regions: []`` (the frozen C043 precedent: empty data, not an
        error); an unknown page additionally reads ``page_size: null``.
        Geometry is never fabricated from a missing extent (``null``).
        """
        page_id = payload.get("page_id")
        if not isinstance(page_id, str) or not page_id:
            raise RegionRequestError(
                "list_page_region_texts requires 'page_id': a non-empty string"
            )
        requested = payload.get("region_ids")
        filter_ids: list[str] | None = None
        if requested is not None:
            if (
                not isinstance(requested, list)
                or not requested
                or any(
                    not isinstance(item, str) or not item
                    for item in requested
                )
                or len(set(requested)) != len(requested)
            ):
                raise RegionRequestError(
                    "list_page_region_texts 'region_ids' must be a non-empty"
                    " list of distinct non-empty region ids when present"
                )
            filter_ids = list(requested)
        page = self._core.repository.get_page(page_id)
        page_size = (
            {"width": page.width, "height": page.height} if page else None
        )
        self._log_lineage_hidden("list_page_region_texts", page_id)
        details = self._core.editing.list_region_details(
            page_id,
            page_size=(page.width, page.height) if page else None,
        )
        if filter_ids is not None:
            by_id = {row["region_id"]: row for row in details}
            for region_id in filter_ids:
                if region_id not in by_id:
                    raise RegionLookupError(region_id)
            requested_set = set(filter_ids)
            details = [
                row for row in details if row["region_id"] in requested_set
            ]
        return {
            "page_id": page_id,
            "page_size": page_size,
            "regions": details,
        }

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
        except RegionLimitExceeded as error:
            # I4/P2-B: an oversized historical snapshot geometry is a validation
            # failure (never UNKNOWN); zero write.
            raise RegionRequestError(
                f"restore_region_revision rejected: {error}"
            ) from error
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

    # ------------------------------------------------------------------
    # Region write face (V11R-F0-1 / audit §5.1 F-01)
    #
    # The six pre-existing Region commands above are untouched. These ten
    # write/read-back commands are the real channels the Studio Page mode
    # needs; every handler reuses the EXISTING application use case (the
    # only new use case is ``set_locks``, recorded as a GAP in
    # doc/contracts/V11R_REGION_WRITE_CONTRACT.md §2.1) and adds wire-side
    # validation + the post-write effective-state projection. Geometry on the
    # wire is the SAME normalized read shape ``list_regions`` projects
    # ({"bbox", "polygon"}), except writes carry the editable point list
    # {"points": [[x, y], ...]} -- application/editing/region_canvas.py owns
    # the single normalized<->page-pixel mapping.
    #
    # Error semantics reuse the existing typed literals only:
    # INVALID_REQUEST (validation) / INPUT_REVISION_CHANGED (conflict, the
    # explicit optimistic guard) / TARGET_NOT_FOUND (not_found) /
    # UNKNOWN (internal). Wire codes stay SCREAMING_SNAKE_CASE.
    # ------------------------------------------------------------------

    @staticmethod
    def _region_write_error(command: str, detail: str) -> RegionRequestError:
        return RegionRequestError(f"{command} {detail}")

    def _region_write_string(self, payload: dict[str, Any], key: str, command: str) -> str:
        value = payload.get(key)
        if not isinstance(value, str) or not value:
            raise self._region_write_error(
                command, f"requires '{key}': a non-empty string"
            )
        return value

    def _region_write_expected_revision(
        self, payload: dict[str, Any], command: str
    ) -> int | None:
        value = payload.get("expected_revision")
        if value is None:
            return None
        if not self._is_positive_integer(value):
            raise self._region_write_error(
                command,
                "'expected_revision' must be a positive integer when present",
            )
        return value

    def _region_write_expected_revisions(
        self, payload: dict[str, Any], command: str
    ) -> dict[str, int] | None:
        """The multi-region optimistic guard (merge / reorder). Coverage of
        exactly the affected region ids is validated by the handler that owns
        the batch (it already knows the live page set)."""
        value = payload.get("expected_revisions")
        if value is None:
            return None
        if not isinstance(value, dict) or not value:
            raise self._region_write_error(
                command, "'expected_revisions' must be a non-empty object"
            )
        expected: dict[str, int] = {}
        for region_id, revision_no in value.items():
            if (
                not isinstance(region_id, str)
                or not region_id
                or not self._is_positive_integer(revision_no)
            ):
                raise self._region_write_error(
                    command,
                    "'expected_revisions' must map non-empty region ids to"
                    " positive revision numbers",
                )
            expected[region_id] = revision_no
        return expected

    @staticmethod
    def _region_write_points(
        raw: Any, command: str, label: str = "geometry"
    ) -> list[tuple[float, float]]:
        """Normalized (0..1) editable point list (``[[x, y], ...]``).

        Two points are an axis-aligned rectangle in any corner order, three
        or more are a polygon ring -- the same contract
        ``normalized_to_page_geometry`` documents. Every rejection happens
        before a ``RegionGeometry`` is built (the region_canvas.py invariant).
        """
        if not isinstance(raw, list) or len(raw) < 2:
            raise RegionRequestError(
                f"{command} '{label}' requires at least two [x, y] points"
            )
        # I2/P2-E: bounded input (the whole batch runs in one write
        # transaction; an unbounded polygon would hold the write lock).
        if len(raw) > MAX_GEOMETRY_POINTS:
            raise RegionRequestError(
                f"{command} '{label}' supports at most"
                f" {MAX_GEOMETRY_POINTS} points"
            )
        points: list[tuple[float, float]] = []
        for item in raw:
            if not isinstance(item, list) or len(item) != 2:
                raise RegionRequestError(
                    f"{command} '{label}' points must be [x, y] pairs"
                )
            x, y = item
            for axis in (x, y):
                if (
                    isinstance(axis, bool)
                    or not isinstance(axis, (int, float))
                    or not math.isfinite(axis)
                    or axis < 0
                    or axis > 1
                ):
                    raise RegionRequestError(
                        f"{command} '{label}' points must be finite normalized"
                        " numbers within [0, 1]"
                    )
            points.append((float(x), float(y)))
        return points

    def _region_write_page_extent(
        self, page_id: str, command: str
    ) -> tuple[int, int]:
        page = self._core.repository.get_page(page_id)
        if page is None:
            raise RegionLookupError(page_id, "page not found")
        return page.width, page.height

    def _region_write_geometry(
        self,
        payload: dict[str, Any],
        page_width: int,
        page_height: int,
        command: str,
        label: str = "geometry",
    ) -> RegionGeometry:
        raw = payload.get(label)
        if not isinstance(raw, dict):
            raise RegionRequestError(
                f"{command} requires '{label}': an object with 'points'"
            )
        try:
            return normalized_to_page_geometry(
                self._region_write_points(raw.get("points"), command, label),
                page_width,
                page_height,
            )
        except RegionCanvasError as error:
            # The typed reason (PAGE_SIZE_UNAVAILABLE / TOO_FEW_POINTS /
            # DEGENERATE_GEOMETRY) is safe to project; no coordinates or
            # paths ride the message.
            raise RegionRequestError(
                f"{command} rejected {label}: {error.code}"
            ) from error

    def _region_write_snapshot(self, region_id: str) -> tuple[Any, Any]:
        """Read back the effective state from the SAME authoritative objects
        the write path just updated (one round trip, no second query path);
        the current pointer is guaranteed to resolve by the service
        invariant, a breach is an internal error (UNKNOWN) rather than a
        fabricated row."""
        region = self._core.editing.get_region(region_id)
        revision = self._core.editing.current_revision(region_id)
        return region, revision

    def handle_create_region(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Create one Region from normalized canvas points.

        Request: {"page_id", "geometry": {"points": [[x, y], ...]},
        "region_type"?: RegionType (default speech),
        "reading_order"?: positive int (default: append)}.
        The first revision + current pointer are created atomically by the
        existing ``RegionEditingService.create_region`` path (TASK-002 §2.1);
        the SFX policy reuses the shared EV-8 rule (only an SFX region carries
        the CURRENT global policy, every other type is forced SKIP).
        Result: {"region_id", "revision_no", "reading_order", "region_type",
        "sfx_policy"}.
        Optimistic lock: none -- creation has no prior revision to guard and
        candidate region ids are server-generated (documented in the
        contract).
        """
        command = "create_region"
        page_id = self._region_write_string(payload, "page_id", command)
        region_type_value = payload.get("region_type", RegionType.SPEECH.value)
        if (
            not isinstance(region_type_value, str)
            or region_type_value not in _REGION_TYPE_VALUES
        ):
            raise self._region_write_error(
                command,
                "'region_type' must be one of " + str(sorted(_REGION_TYPE_VALUES)),
            )
        reading_order = payload.get("reading_order")
        if reading_order is not None and not self._is_positive_integer(reading_order):
            raise self._region_write_error(
                command, "'reading_order' must be a positive integer when present"
            )
        page_width, page_height = self._region_write_page_extent(page_id, command)
        if (
            len(self._core.editing.list_regions(page_id))
            >= MAX_REGIONS_PER_PAGE
        ):
            raise self._region_write_error(
                command,
                f"page already has {MAX_REGIONS_PER_PAGE} live regions"
                " (contract limit)",
            )
        geometry = self._region_write_geometry(
            payload, page_width, page_height, command
        )
        region_type = RegionType(region_type_value)
        region = self._core.editing.create_region(
            page_id,
            geometry,
            region_type=region_type,
            reading_order=reading_order,
            sfx_policy=effective_sfx_policy(
                region_type, self._global_sfx_policy_value()
            ),
        )
        revision = self._core.editing.current_revision(region.region_id)
        return {
            "region_id": region.region_id,
            "revision_no": revision.revision_no,
            "reading_order": region.reading_order,
            "region_type": region.region_type.value,
            "sfx_policy": region.sfx_policy.value,
        }

    def handle_delete_region(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Soft-delete one Region (no revision is created: the deletion only
        stamps ``deleted_at``; current/pinned revisions and history stay
        untouched). Request: {"region_id", "expected_revision"?}.
        Result: {"region_id", "deleted": true}."""
        command = "delete_region"
        region_id = self._region_write_string(payload, "region_id", command)
        expected = self._region_write_expected_revision(payload, command)
        try:
            self._core.editing.delete_region(
                region_id, expected_revision_no=expected
            )
        except RegionNotFound as error:
            raise RegionLookupError(region_id) from error
        except RegionRevisionChanged as error:
            raise RegionConflictError(
                "region revision changed since it was read"
            ) from error
        return {"region_id": region_id, "deleted": True}

    def handle_save_region_geometry(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Persist a geometry edit as ONE new user revision through the atomic
        commit seam (D06 §87). Request: {"region_id", "geometry": {"points"},
        "expected_revision"?}. Result: {"region_id", "revision_no",
        "geometry": normalized read shape}."""
        command = "save_region_geometry"
        region_id = self._region_write_string(payload, "region_id", command)
        expected = self._region_write_expected_revision(payload, command)
        # The region's own page extent, resolved from the persisted row (the
        # caller never supplies pixel sizes; only the projection is returned).
        stored = self._core.editing.get_region(region_id)
        page_width, page_height = self._region_write_page_extent(
            stored.page_id, command
        )
        geometry = self._region_write_geometry(
            payload, page_width, page_height, command
        )
        try:
            outcome = self._core.editing.save_geometry(
                region_id, geometry, expected_revision_no=expected
            )
        except RegionNotFound as error:
            raise RegionLookupError(region_id) from error
        except RegionRevisionChanged as error:
            raise RegionConflictError(
                "region revision changed since it was read"
            ) from error
        if outcome.status is GuardStatus.INPUT_REVISION_CHANGED:
            raise RegionConflictError(
                "region revision changed since it was read"
            )
        if outcome.status is not GuardStatus.APPLIED:
            raise RuntimeError(f"save_region_geometry commit failed: {outcome.detail}")
        region, revision = self._region_write_snapshot(region_id)
        return {
            "region_id": region_id,
            "revision_no": revision.revision_no,
            "geometry": page_geometry_to_normalized(
                region.geometry, page_width, page_height
            ),
        }

    def handle_merge_regions(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Merge >= 2 live Regions of one page into one new Region (D03 §6.4).
        Request: {"page_id", "region_ids": [...], "expected_revisions"?}.
        The sources are soft-deleted and the merged Region starts its own
        revision history (existing use case); every source expectation is
        checked BEFORE the first write. Result: {"region_id", "revision_no",
        "reading_order", "region_type", "sfx_policy", "deleted_region_ids"}.
        """
        command = "merge_regions"
        page_id = self._region_write_string(payload, "page_id", command)
        self._region_write_page_extent(page_id, command)
        raw_ids = payload.get("region_ids")
        if (
            not isinstance(raw_ids, list)
            or len(raw_ids) < 2
            or any(not isinstance(item, str) or not item for item in raw_ids)
            or len(set(raw_ids)) != len(raw_ids)
        ):
            raise self._region_write_error(
                command,
                "requires 'region_ids': at least two distinct non-empty"
                " region ids",
            )
        region_ids = list(raw_ids)
        if len(region_ids) > MAX_REGION_IDS_PER_BATCH:
            raise self._region_write_error(
                command,
                f"'region_ids' supports at most {MAX_REGION_IDS_PER_BATCH} ids",
            )
        expected = self._region_write_expected_revisions(payload, command)
        live_ids = {
            region.region_id for region in self._core.editing.list_regions(page_id)
        }
        for region_id in region_ids:
            if region_id not in live_ids:
                raise RegionLookupError(region_id)
        if expected is not None and set(expected) != set(region_ids):
            raise self._region_write_error(
                command,
                "'expected_revisions' must cover exactly the merged region ids",
            )
        try:
            merged, deleted = self._core.editing.merge_regions(
                page_id, region_ids, expected_revisions=expected
            )
        except RegionNotFound as error:
            raise RegionLookupError(error.region_id) from error
        except RegionRevisionChanged as error:
            raise RegionConflictError(
                "region revision changed since it was read"
            ) from error
        except ValueError as error:
            raise self._region_write_error(command, f"rejected: {error}") from error
        revision = self._core.editing.current_revision(merged.region_id)
        return {
            "region_id": merged.region_id,
            "revision_no": revision.revision_no,
            "reading_order": merged.reading_order,
            "region_type": merged.region_type.value,
            "sfx_policy": merged.sfx_policy.value,
            "deleted_region_ids": list(deleted),
        }

    def handle_split_region(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Split one Region into >= 2 caller-supplied geometries (D03 §6.4 /
        TASK-002). Request: {"region_id", "parts": [[[x, y], ...], ...],
        "expected_revision"?}. The source is soft-deleted and every part
        starts a fresh history; manual protection carries over. Result:
        {"source_region_id", "source_deleted": true, "regions":
        [{"region_id", "revision_no", "reading_order", "region_type"}]}.
        """
        command = "split_region"
        region_id = self._region_write_string(payload, "region_id", command)
        expected = self._region_write_expected_revision(payload, command)
        raw_parts = payload.get("parts")
        if not isinstance(raw_parts, list) or len(raw_parts) < 2:
            raise self._region_write_error(
                command, "requires 'parts': at least two point lists"
            )
        if len(raw_parts) > MAX_SPLIT_PARTS:
            raise self._region_write_error(
                command,
                f"'parts' supports at most {MAX_SPLIT_PARTS} point lists",
            )
        stored = self._core.editing.get_region(region_id)
        page_width, page_height = self._region_write_page_extent(
            stored.page_id, command
        )
        parts = []
        for index, raw_part in enumerate(raw_parts, start=1):
            try:
                parts.append(
                    normalized_to_page_geometry(
                        self._region_write_points(
                            raw_part, command, f"parts[{index}]"
                        ),
                        page_width,
                        page_height,
                    )
                )
            except RegionCanvasError as error:
                raise RegionRequestError(
                    f"{command} rejected parts[{index}]: {error.code}"
                ) from error
        try:
            created = self._core.editing.split_region(
                region_id, parts, expected_revision_no=expected
            )
        except RegionNotFound as error:
            raise RegionLookupError(region_id) from error
        except RegionRevisionChanged as error:
            raise RegionConflictError(
                "region revision changed since it was read"
            ) from error
        except ValueError as error:
            raise self._region_write_error(command, f"rejected: {error}") from error
        regions = []
        for part in created:
            revision = self._core.editing.current_revision(part.region_id)
            regions.append({
                "region_id": part.region_id,
                "revision_no": revision.revision_no,
                "reading_order": part.reading_order,
                "region_type": part.region_type.value,
            })
        return {
            "source_region_id": region_id,
            "source_deleted": True,
            "regions": regions,
        }

    def handle_reorder_regions(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Persist the manual reading order of one page (TASK-028 §3.4).
        Request: {"page_id", "ordered_region_ids": [...],
        "expected_revisions"?}. The list must be the exact permutation of the
        page's live Region ids (fail-closed: a partial list could corrupt the
        reading order). Each changed Region gets one user revision. Result:
        {"page_id", "regions": [{"region_id", "revision_no", "reading_order"}]}.
        """
        command = "reorder_regions"
        page_id = self._region_write_string(payload, "page_id", command)
        self._region_write_page_extent(page_id, command)
        raw_ids = payload.get("ordered_region_ids")
        if (
            not isinstance(raw_ids, list)
            or not raw_ids
            or any(not isinstance(item, str) or not item for item in raw_ids)
            or len(set(raw_ids)) != len(raw_ids)
        ):
            raise self._region_write_error(
                command,
                "requires 'ordered_region_ids': a non-empty list of distinct"
                " non-empty region ids",
            )
        ordered = list(raw_ids)
        if len(ordered) > MAX_REGIONS_PER_PAGE:
            raise self._region_write_error(
                command,
                f"'ordered_region_ids' supports at most"
                f" {MAX_REGIONS_PER_PAGE} ids",
            )
        expected = self._region_write_expected_revisions(payload, command)
        live_ids = {
            region.region_id for region in self._core.editing.list_regions(page_id)
        }
        if set(ordered) != live_ids:
            raise self._region_write_error(
                command,
                "'ordered_region_ids' must be the exact set of the page's live"
                " region ids",
            )
        if expected is not None and set(expected) != set(ordered):
            raise self._region_write_error(
                command,
                "'expected_revisions' must cover exactly the ordered region ids",
            )
        try:
            reordered = self._core.editing.reorder_regions(
                page_id, ordered, expected_revisions=expected
            )
        except RegionNotFound as error:
            raise RegionLookupError(error.region_id) from error
        except RegionRevisionChanged as error:
            raise RegionConflictError(
                "region revision changed since it was read"
            ) from error
        regions = []
        for region in reordered:
            revision = self._core.editing.current_revision(region.region_id)
            regions.append({
                "region_id": region.region_id,
                "revision_no": revision.revision_no,
                "reading_order": region.reading_order,
            })
        return {"page_id": page_id, "regions": regions}

    def handle_save_manual_translation(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Save the user's edited translation (D03 §8.4): arms manual_edited +
        translation_locked and records ONE user revision (review_state
        needs_review until an explicit confirm). Request: {"region_id",
        "edited_translation": str (may be empty), "expected_revision"?}.
        Result: {"region_id", "revision_no", "review_state", "text"} where
        ``text`` is the four-level text projection verbatim.
        """
        command = "save_manual_translation"
        region_id = self._region_write_string(payload, "region_id", command)
        edited = payload.get("edited_translation")
        if not isinstance(edited, str):
            raise self._region_write_error(
                command, "requires 'edited_translation': a string"
            )
        expected = self._region_write_expected_revision(payload, command)
        try:
            revision_no = self._core.editing.save_manual_translation(
                region_id, edited, expected_revision_no=expected
            )
        except RegionNotFound as error:
            raise RegionLookupError(region_id) from error
        except RegionRevisionChanged as error:
            raise RegionConflictError(
                "region revision changed since it was read"
            ) from error
        region, revision = self._region_write_snapshot(region_id)
        return {
            "region_id": region_id,
            "revision_no": revision_no,
            "review_state": revision.review_state.value,
            "text": region_text_state(region),
        }

    def handle_confirm_region_final(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Explicit proofread confirmation (D06 §87): a non-blank edited text
        becomes the confirmed final; otherwise the review state is just
        locked. Request: {"region_id", "expected_revision"?}. Result same
        shape as save_manual_translation with review_state "confirmed"."""
        command = "confirm_region_final"
        region_id = self._region_write_string(payload, "region_id", command)
        expected = self._region_write_expected_revision(payload, command)
        try:
            revision_no = self._core.editing.confirm_final(
                region_id, expected_revision_no=expected
            )
        except RegionNotFound as error:
            raise RegionLookupError(region_id) from error
        except RegionRevisionChanged as error:
            raise RegionConflictError(
                "region revision changed since it was read"
            ) from error
        region, revision = self._region_write_snapshot(region_id)
        return {
            "region_id": region_id,
            "revision_no": revision_no,
            "review_state": revision.review_state.value,
            "text": region_text_state(region),
        }

    def handle_set_region_lock(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Explicitly set one or more of the three user locks (D06 §87): the
        change is ONE user revision through the atomic commit seam (the added
        ``set_locks`` use case composes the existing domain setters).
        Request: {"region_id", "region_locked"?: bool,
        "translation_locked"?: bool, "inpaint_locked"?: bool,
        "expected_revision"?}. Result: {"region_id", "revision_no",
        "review_state", "region_locked", "translation_locked",
        "inpaint_locked"}."""
        command = "set_region_lock"
        region_id = self._region_write_string(payload, "region_id", command)
        expected = self._region_write_expected_revision(payload, command)
        locks: dict[str, bool] = {}
        for field in _REGION_LOCK_FIELDS:
            value = payload.get(field)
            if value is None:
                continue
            if not isinstance(value, bool):
                raise self._region_write_error(
                    command, f"'{field}' must be a boolean when present"
                )
            locks[field] = value
        if not locks:
            raise self._region_write_error(
                command,
                "requires at least one of " + ", ".join(_REGION_LOCK_FIELDS),
            )
        try:
            revision_no = self._core.editing.set_locks(
                region_id, expected_revision_no=expected, **locks
            )
        except RegionNotFound as error:
            raise RegionLookupError(region_id) from error
        except RegionRevisionChanged as error:
            raise RegionConflictError(
                "region revision changed since it was read"
            ) from error
        region, revision = self._region_write_snapshot(region_id)
        return {
            "region_id": region_id,
            "revision_no": revision_no,
            "review_state": revision.review_state.value,
            "region_locked": region.region_locked,
            "translation_locked": region.translation_locked,
            "inpaint_locked": region.inpaint_locked,
        }

    def handle_pin_revision(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Pin/unpin one immutable revision (AC-REV-003). Request:
        {"region_id", "revision_no": positive int, "pinned": bool,
        "expected_revision"?}. Pin touches ``is_pinned`` only -- no revision
        is created and no immutable snapshot is rewritten; the optional
        expectation guards that the CURRENT pointer is still what the caller
        observed. Result: {"region_id", "revision_no", "is_pinned",
        "current_revision_no"}."""
        command = "pin_revision"
        region_id = self._region_write_string(payload, "region_id", command)
        revision_no = payload.get("revision_no")
        if not self._is_positive_integer(revision_no):
            raise self._region_write_error(
                command, "requires positive integer 'revision_no'"
            )
        pinned = payload.get("pinned")
        if not isinstance(pinned, bool):
            raise self._region_write_error(command, "requires boolean 'pinned'")
        expected = self._region_write_expected_revision(payload, command)
        try:
            self._core.editing.set_revision_pinned(
                region_id,
                revision_no,
                pinned,
                expected_revision_no=expected,
            )
        except RegionNotFound as error:
            raise RegionLookupError(region_id) from error
        except RegionRevisionNotFound as error:
            raise RegionLookupError(
                region_id, "region revision not found"
            ) from error
        except RegionRevisionChanged as error:
            raise RegionConflictError(
                "region revision changed since it was read"
            ) from error
        _region, current = self._region_write_snapshot(region_id)
        return {
            "region_id": region_id,
            "revision_no": revision_no,
            "is_pinned": pinned,
            "current_revision_no": current.revision_no,
        }

    # FEA-05-WIRE-1: Draft command surface (C078-C083).
    # Contract: doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md (PENDING).
    def _dispatch_draft_command(self, command: str, payload: dict[str, Any]) -> dict[str, Any]:
        drafts = getattr(self._core, "drafts", None)
        if drafts is None:
            raise DraftError("INTERNAL", "drafts service is not assembled")
        if command == "drafts_open":
            lease = drafts.open_draft(
                _require_str(payload, "sessionId"),
                _require_str(payload, "pageId"),
                payload.get("regionId"),
                base_revision_id=payload.get("baseRevisionId"),
                page_binding_version=_require_int(payload, "pageBindingVersion"),
            )
            return {
                "draft": lease.draft.to_json(),
                "canEdit": bool(lease.can_edit),
                "token": lease.token.to_json() if lease.token is not None else None,
            }
        if command == "drafts_patch":
            draft = drafts.patch_draft(
                _require_str(payload, "draftId"),
                _require_str(payload, "sessionId"),
                _require_mapping(payload, "patch"),
                undo_cursor=payload.get("undoCursor"),
            )
            return {"draft": draft.to_json()}
        if command == "drafts_prepare":
            candidate = drafts.prepare_candidate(
                _require_str(payload, "regionId"),
                _require_mapping(payload, "patch"),
                origin=_require_str(payload, "origin"),
                draft_id=payload.get("draftId"),
                base_revision_id=payload.get("baseRevisionId"),
            )
            return {"candidate": candidate.to_json()}
        if command == "drafts_apply":
            token = payload.get("token")
            if not isinstance(token, dict):
                raise DraftError("EDIT_TOKEN_INVALID", "token must be an EditToken object")
            candidate_ids = payload.get("candidateIds") or []
            if not isinstance(candidate_ids, list):
                raise DraftError("EDIT_TOKEN_INVALID", "candidateIds must be a list")
            return drafts.apply_candidates(token, candidate_ids)
        if command == "drafts_status":
            draft_id = payload.get("draftId")
            session_id = payload.get("sessionId")
            if bool(draft_id) == bool(session_id):
                raise DraftError("DRAFT_INVALID", "exactly one of draftId or sessionId is required")
            if draft_id:
                return {"draft": drafts.get_draft(_require_str(payload, "draftId")).to_json()}
            return {"drafts": [draft.to_json() for draft in drafts.list_drafts(session_id=session_id)]}
        if command == "drafts_discard":
            drafts.discard_draft(_require_str(payload, "draftId"), _require_str(payload, "sessionId"))
            return {"discarded": True}
        raise DraftError("UNKNOWN", f"unknown draft command: {command}")

    def _dispatch_region_write(
        self, command: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Route one of the ten V11R region write commands (additive surface,
        same typed-error envelope as the existing Region family).

        FEA-11 (C-17 §3.3): live edits through a binding whose publication
        gate is still pending are refused (SOURCE_ACCESS_DENIED)."""
        self._refuse_pending_gate_writes(payload)
        if command == "create_region":
            return self.handle_create_region(payload)
        if command == "delete_region":
            return self.handle_delete_region(payload)
        if command == "save_region_geometry":
            return self.handle_save_region_geometry(payload)
        if command == "merge_regions":
            return self.handle_merge_regions(payload)
        if command == "split_region":
            return self.handle_split_region(payload)
        if command == "reorder_regions":
            return self.handle_reorder_regions(payload)
        if command == "save_manual_translation":
            return self.handle_save_manual_translation(payload)
        if command == "confirm_region_final":
            return self.handle_confirm_region_final(payload)
        if command == "set_region_lock":
            return self.handle_set_region_lock(payload)
        return self.handle_pin_revision(payload)

    def handle_rerender_page(self, payload: dict[str, Any]) -> dict[str, Any]:
        page_id = payload.get("page_id")
        if not isinstance(page_id, str) or not page_id:
            raise RegionRequestError(
                "rerender_page requires 'page_id': a non-empty string"
            )
        if self._core.repository.get_page(page_id) is None:
            raise RegionLookupError(page_id)
        # SETTINGS-OPEN-A-1 AC2: a manual page rerender has no Run context, so
        # it applies the CURRENT global ``typeset`` settings immediately (the
        # same derivation the pipeline render step applies to a frozen Run
        # snapshot). Region-persisted values still win (D03 §11.4).
        style_defaults = typeset_style_defaults(
            self._core.pipeline_defaults.read().settings
        )
        outcome = self._core.render.rerender_page(
            page_id, style_defaults=style_defaults
        )
        if outcome.status != "committed":
            code = outcome.error_code or E_UNKNOWN
            if code == "COMPOSITION_BASE_CHANGED":
                code = E_INPUT_REVISION_CHANGED
            elif outcome.status == "write_failed":
                code = "ARTIFACT_WRITE_FAILED"
            # M2-CATEGORY-CLARIFY-1 (RC4-10): required-input missing is an
            # AVAILABILITY failure (data not there), not a "target does not
            # exist" one -- §8 taxonomy, category never frozen before.
            # FEA-11-LINEAGE-1: the C-17 §7.1 isolation refusals are typed
            # conflicts; their fixed safe phrase never includes coordinates or
            # the raw exception text.
            lineage_code = code in (LINEAGE_BINDING_CHANGED, LINEAGE_UNVERIFIED)
            category = "conflict" if (
                code == E_INPUT_REVISION_CHANGED or lineage_code
            ) else (
                "not_found" if code == E_TARGET_NOT_FOUND else (
                    "unavailable" if code == "MISSING_REQUIRED_INPUT" else "internal"
                )
            )
            message = {
                "MISSING_REQUIRED_INPUT": "required render input is missing",
                E_TARGET_NOT_FOUND: "page not found",
                E_INPUT_REVISION_CHANGED: "render input changed; retry the operation",
                "ARTIFACT_WRITE_FAILED": "render output could not be saved",
                LINEAGE_BINDING_CHANGED: (
                    "region coordinates belong to a previous source binding"
                ),
                LINEAGE_UNVERIFIED: (
                    "region coordinates are not verified for the current source"
                ),
            }.get(code, "page rerender failed")
            print(
                f"[core.rerender_page] code={code} detail={outcome.detail or ''}",
                file=sys.stderr,
            )
            raise RenderCommandError(code, category, message)

        # FEA-11-LINEAGE-1 (r2): the page render reports every excluded region
        # in ``reports``; the aggregate count is logged too so the filtering is
        # diagnosable without reading the whole report array.
        lineage_hidden = sum(
            1
            for report in outcome.reports
            if report.skip_reason in (
                LINEAGE_BINDING_CHANGED,
                LINEAGE_UNVERIFIED,
            )
        )
        if lineage_hidden:
            print(
                f"[core.rerender_page] page={page_id}"
                f" lineage_hidden={lineage_hidden}",
                file=sys.stderr,
            )

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
        if page is None:
            raise RegionLookupError(page_id)
        if getattr(page, "source_mode", "managed") == "referenced":
            # C-15 §4.2: referenced pages resolve only through a live
            # source-read grant and publish a decoded/re-encoded rendition —
            # never raw user-source bytes, never an arbitrary-path fallback.
            from application.importing.referenced.resolve import (
                prepare_referenced_rendition,
                render_prepared_rendition,
                resolve_referenced_rendition,
            )

            registry = getattr(self._core, "source_read_refs", None)
            if registry is None:
                raise SourceImportError(
                    "SOURCE_REGISTRY_UNAVAILABLE",
                    "source-read grants are unavailable",
                )
            # FEA-11 (C-17 §3.3): the pending publication gate refuses reads
            # until the Host ACKs the operation (fail-closed, never V-side).
            self._assert_source_sync_gate(page.page_id)
            prepared = prepare_referenced_rendition(
                page.page_id,
                repository=self._core.repository,
                access=registry,
            )
            # FEA-11 (C-17 §7.2): referenced resolves select the
            # binding-scoped v2 resource key; the legacy
            # ``page-rendition-{page_id}`` key (and its published digest)
            # stays immutable — a same-key/different-digest collision is a
            # typed refusal, never a replacement.
            resource_id = self._referenced_resource_id(prepared)
            cache = getattr(self._core, "rendition_cache", None)
            if cache is not None:
                # R1-I008: the constrained rendition cache decides reuse
                # (key/budget/LRU/active refs/crash recovery/digest) BEFORE
                # any decode; the catalog only mirrors the served bytes.

                def _produce() -> bytes:
                    # C-16 v1.1 §3.1: a cache MISS on an encrypted source
                    # consumes the one fresh Secret-G; cache hits never reach
                    # here (no token requested/consumed).
                    password = None
                    claim = getattr(registry, "claim_secret_for_binding", None)
                    if claim is not None:
                        password = claim(
                            prepared["source_id"],
                            prepared["version_id"],
                            prepared["entry_id"],
                            locator=prepared["entry"].locator,
                            ordinal=prepared["entry"].ordinal,
                        )
                    png, _width, _height = render_prepared_rendition(
                        prepared,
                        image_decoder=getattr(self._core, "image_decoder", None),
                        document_raster=getattr(self._core, "document_raster", None),
                        password=password,
                    )
                    return png

                with cache.acquire(
                    source_id=prepared["source_id"],
                    version_id=prepared["version_id"],
                    entry_id=prepared["entry_id"],
                    kind=prepared["rendition_kind"],
                    decoder=prepared["decoder_name"],
                    decoder_version=prepared["decoder_version"],
                    params=prepared["params"],
                    width=prepared["width"],
                    height=prepared["height"],
                    max_decode_bytes=prepared["max_decode_bytes"],
                    produce=_produce,
                ) as png:
                    return self._publish_rendition_bytes(resource_id, png)
            rendition = resolve_referenced_rendition(
                page.page_id,
                repository=self._core.repository,
                access=registry,
                image_decoder=getattr(self._core, "image_decoder", None),
                document_raster=getattr(self._core, "document_raster", None),
            )
            entry = self._render_previews.lookup(resource_id)
            if entry is not None and self._render_previews.artifact_exists(
                entry.rel_path
            ):
                self._record_rendition_cache(page, rendition, entry)
                return {"resource_id": resource_id, "revision": ORIGINAL_REVISION}
            import tempfile

            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(
                    suffix=".png", delete=False
                ) as temp:
                    temp_path = Path(temp.name)
                    temp.write(rendition["png"])
                    temp.flush()
                    os.fsync(temp.fileno())
                published = self._render_previews.publish_original(
                    temp_path, resource_id, ".png"
                )
                # C-17 §7.2: record the cache row against the binding-scoped
                # v2 key, not the legacy page key (lookup would miss it).
                self._record_rendition_cache(
                    page, rendition, None, resource_id=resource_id
                )
                return published
            finally:
                if temp_path is not None:
                    temp_path.unlink(missing_ok=True)
        # C-15 v1.1 §4.2 / C-05 v1.2 R: the eligible current ORIGINAL revision
        # is preferred, then the Page Managed Copy; either fails typed.
        selected_path = None
        selector = getattr(self._core.repository, "get_visible_original_path", None)
        if selector is not None:
            selected_path = selector(page.page_id)
        managed_ref = selected_path or page.managed_original_ref
        if not managed_ref:
            raise RegionLookupError(page_id)
        # The wire gate admits exactly the decode face's suffixes; the suffix is
        # checked BEFORE any read so an unsupported ref stays the documented
        # UNKNOWN/internal anomaly (never PAGE_NOT_FOUND because the file it
        # points at happens to be missing).
        suffix = Path(managed_ref).suffix.lower()
        if suffix not in _ORIGINAL_SUFFIXES:
            raise RuntimeError(f"unsupported managed original format: {suffix!r}")
        # P09-MANAGED-READ-ROOT-TRUST-1: the managed original is admitted through
        # the start-up identity snapshot of the managed root; the bytes that get
        # published are read through the verifying handle, so a junction injected
        # above the configured root after start-up is a typed refusal instead of
        # an outside byte copy (R5b P2).
        trust = getattr(self._core, "managed_root_trust", None)
        if trust is None:
            raise RuntimeError("managed original escaped the Managed Copy root")
        try:
            source_bytes = trust.read_bytes(managed_ref)
        except TypedResourceChannelError as error:
            if error.code == E_NOT_FOUND:
                raise RegionLookupError(page_id) from error
            if error.code in (E_IDENTITY_CHANGED, E_OUT_OF_SCOPE, E_REPARSE, E_SCOPE_DENIED):
                raise RuntimeError(
                    "managed original escaped the Managed Copy root"
                ) from error
            raise RuntimeError("managed original could not be read") from error
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
        temp_source = self._materialise_verified_managed_copy(
            managed_ref, source_bytes
        )
        try:
            return self._render_previews.publish_original(
                temp_source, resource_id, suffix
            )
        finally:
            temp_source.unlink(missing_ok=True)

    def _render_previews_preview_root(self) -> Path | None:
        """Derived-root accessor for read-back checks (same attribute-access
        precedent as the preview catalog pickup above)."""
        return getattr(self._render_previews, "_root", None)

    def _referenced_resource_id(self, prepared: dict) -> str:
        """FEA-11 (C-17 §7.2): the binding-scoped v2 rendition key.

        ``page-rendition-v2-`` + sha256(canonical({page_id,binding_id,
        source_id,version_id,entry_id,verified_digest,rendition_kind,
        decoder_name,decoder_version,params_digest})). A different binding or
        decoder profile necessarily selects a different key; the legacy
        ``page-rendition-{page_id}`` key keeps returning its original digest.
        """
        from application.sources.model import digest_of

        binding = prepared["binding"]
        return "page-rendition-v2-" + digest_of(
            {
                "page_id": binding["page_id"],
                "binding_id": binding["binding_id"],
                "source_id": binding["source_id"],
                "version_id": binding["accepted_source_version"],
                "entry_id": binding["entry_id"],
                "verified_digest": binding.get("verified_digest"),
                "rendition_kind": prepared["rendition_kind"],
                "decoder_name": prepared["decoder_name"],
                "decoder_version": prepared["decoder_version"],
                "params_digest": prepared["params_digest"],
            }
        )

    def _publish_rendition_bytes(self, resource_id: str, png: bytes) -> dict:
        """Mirror one cached rendition into the served catalog (idempotent).

        FEA-11 (C-17 §7.2): a same-key collision with different bytes is a
        typed refusal — an already-published digest is never replaced."""
        entry = self._render_previews.lookup(resource_id)
        if entry is not None and self._render_previews.artifact_exists(
            entry.rel_path
        ):
            root = self._render_previews_preview_root()
            if root is not None:
                try:
                    existing_bytes = (root / entry.rel_path).read_bytes()
                except OSError as error:
                    raise SourceImportError(
                        "SOURCE_REGISTRY_UNAVAILABLE",
                        "published rendition could not be read back",
                    ) from error
                if hashlib.sha256(existing_bytes).hexdigest() != (
                    hashlib.sha256(png).hexdigest()
                ):
                    raise SourceImportError(
                        "SOURCE_ACCESS_DENIED",
                        "resource key is already published with different bytes",
                    )
            return {"resource_id": resource_id, "revision": ORIGINAL_REVISION}
        import tempfile

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
                temp_path = Path(temp.name)
                temp.write(png)
                temp.flush()
                os.fsync(temp.fileno())
            return self._render_previews.publish_original(
                temp_path, resource_id, ".png"
            )
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

    def _record_rendition_cache(
        self, page, rendition, catalog_entry, resource_id: str | None = None
    ) -> None:
        """Record the reproducible rendition observation (C-15 §2.7).

        Derived-only metadata: never user bytes/manual results. A cache write
        failure must not fail resolve (the artifact is already servable); it is
        logged for diagnosis.
        """
        repository = self._core.repository
        upsert = getattr(repository, "upsert_rendition_cache", None)
        if upsert is None or self._render_previews is None:
            return
        resource_id = resource_id or f"page-rendition-{page.page_id}"
        entry = catalog_entry or self._render_previews.lookup(resource_id)
        if entry is None:
            return
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        cache = rendition["cache"]
        try:
            upsert(
                {
                    "cache_key": cache["cache_key"],
                    "source_id": rendition["source_id"],
                    "version_id": rendition["version_id"],
                    "entry_id": rendition["entry_id"],
                    "rendition_kind": cache["rendition_kind"],
                    "decoder_name": cache["decoder_name"],
                    "decoder_version": cache["decoder_version"],
                    "params_digest": cache["params_digest"],
                    "rel_path": entry.rel_path,
                    "size_bytes": cache["size_bytes"],
                    "content_digest": cache["content_digest"],
                    "created_at": now,
                    "last_used_at": now,
                }
            )
        except Exception as error:  # noqa: BLE001 - cache is derived metadata
            print(
                f"[core.resolve_page_resource] rendition cache write failed: {error!r}",
                file=sys.stderr,
            )

    def handle_get_reader_projection(self, payload: dict[str, Any]) -> dict[str, Any]:
        if set(payload) != {"chapter_id", "mode", "start_position"}:
            raise P16WireError("INVALID_REQUEST", "validation", "Reader request is invalid")
        chapter_id, mode, start = payload.get("chapter_id"), payload.get("mode"), payload.get("start_position")
        if not isinstance(chapter_id, str) or not chapter_id or mode not in ("original", "translated") or start not in ("resume", "beginning"):
            raise P16WireError("INVALID_REQUEST", "validation", "Reader request is invalid")
        # FEA-11 (C-17 §3.3): pending publication gates refuse the reader
        # projection for the affected chapter.
        self._refuse_pending_gate_chapter(chapter_id)
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

    def _register_source_read_grant(self, payload: dict[str, Any]) -> dict[str, Any]:
        """FEA-09 RegisterSourceReadGrant (C-16 §2, host-control)."""
        registry = getattr(self._core, "source_read_refs", None)
        if registry is None:
            raise SourceImportError(
                "SOURCE_REGISTRY_UNAVAILABLE", "source-read grants are unavailable"
            )
        registry.register(payload)
        return {"registered": True}

    def _revoke_source_read_grant(self, payload: dict[str, Any]) -> dict[str, Any]:
        """FEA-09 RevokeSourceReadGrant (C-16 §0/§7.7, host-control).

        The Host only reports success to its caller after this ACK; the Core
        kills the grants immediately and running imports stop at the next
        commit-unit boundary (verify_before_commit fails typed).
        """
        registry = getattr(self._core, "source_read_refs", None)
        if registry is None:
            raise SourceImportError(
                "SOURCE_REGISTRY_UNAVAILABLE", "source-read grants are unavailable"
            )
        if (
            not isinstance(payload, dict)
            or set(payload) != {"registry_id", "generation", "grant_ids"}
        ):
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "revocation payload is malformed"
            )
        revoked = registry.revoke_grants(
            payload["registry_id"], payload["generation"], payload["grant_ids"]
        )
        return {"revoked": True, "grants_revoked": revoked}

    def _dispatch_referenced_import(
        self, command: str, raw_payload: object
    ) -> dict[str, Any]:
        """FEA-09 plan/start/receipt/cancel application-channel face."""
        runtime = getattr(self._core, "referenced_import", None)
        if runtime is None or getattr(self._core, "referenced_planner", None) is None:
            raise SourceImportError(
                "CORE_CAPABILITY_MISSING", "referenced import is unavailable"
            )
        if not isinstance(raw_payload, dict):
            raise SourceImportError(
                "SOURCE_OPERATION_CONFLICT", "import request is invalid"
            )
        payload = raw_payload
        if command in {"PlanImportReferences", "StartImportReferences"} and not getattr(self._core, "referenced_import_enabled", True):
            raise SourceImportError("SOURCE_ACCESS_DENIED", "referenced import is disabled")
        if command == "PlanImportReferences":
            required = {"chapter_id", "grants", "duplicate_policy"}
            if set(payload) != required:
                raise SourceImportError(
                    "SOURCE_OPERATION_CONFLICT", "import plan request is invalid"
                )
            return self._core.referenced_planner.plan(
                chapter_id=payload["chapter_id"],
                grants=payload["grants"],
                duplicate_policy=payload["duplicate_policy"],
            )
        if command == "StartImportReferences":
            required = {
                "chapter_id", "plan_id", "plan_digest", "grants",
                "duplicate_policy", "operation_id",
            }
            if not required.issubset(payload) or set(payload) - required - {"secret_ref"}:
                raise SourceImportError(
                    "SOURCE_OPERATION_CONFLICT", "import start request is invalid"
                )
            registry = getattr(self._core, "source_read_refs", None)
            if registry is not None:
                registry.verify_secret_ref(payload["grants"], payload.get("secret_ref"))
            return runtime.start(
                chapter_id=payload["chapter_id"],
                plan_id=payload["plan_id"],
                plan_digest=payload["plan_digest"],
                grants=payload["grants"],
                duplicate_policy=payload["duplicate_policy"],
                operation_id=payload["operation_id"],
                secret_ref=payload.get("secret_ref"),
            )
        if command == "GetImportReceipt":
            if set(payload) != {"operation_id"}:
                raise SourceImportError(
                    "SOURCE_OPERATION_CONFLICT", "receipt request is invalid"
                )
            return runtime.receipt(payload["operation_id"])
        if set(payload) != {"operation_id"}:
            raise SourceImportError(
                "SOURCE_OPERATION_CONFLICT", "cancel request is invalid"
            )
        return runtime.cancel(payload["operation_id"])

    def _dispatch_source_sync(self, command: str, payload: dict[str, Any]) -> dict[str, Any]:
        """FEA-11 (C-17 §5.1): route the source-sync command family."""
        stack = getattr(self._core, "source_sync", None)
        if stack is None:
            raise SourceImportError(
                "CORE_CAPABILITY_MISSING", "source sync is unavailable"
            )
        if command == "ScanSourceSync":
            return stack["scanner"].scan(payload)
        if command in (
            "ApplySourceSyncPlan", "RelinkSource", "RepointSource",
            "ResyncSource",
        ):
            return self._commit_source_sync(stack["service"].apply(command, payload))
        if command == "AcknowledgeSourceOperation":
            return self._commit_source_sync(stack["operations"].acknowledge(payload))
        if command == "CompleteSourceOperationRecovery":
            return self._commit_source_sync(stack["operations"].recover(payload))
        return self._commit_source_sync(stack["operations"].record_failure(payload))

    def _dispatch_source_sync_app(
        self, command: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """FEA-11 plan lifecycle/query face (application channel, minor 3)."""
        stack = getattr(self._core, "source_sync", None)
        if stack is None:
            raise SourceImportError(
                "CORE_CAPABILITY_MISSING", "source sync is unavailable"
            )
        if command == "source_list_scan_targets":
            # C-17 v1.1 §5.1/§5.2: closed shape ``{}``; single SELECT-level
            # projection, zero DB writes, no plan/apply/operation/receipt/
            # grant/journal.  Unknown keys are INVALID_REQUEST.
            if payload != {}:
                raise SourceImportError(
                    "INVALID_REQUEST", "scan target request is invalid"
                )
            from application.sources.scanner import list_scan_targets

            return list_scan_targets(stack["store"])
        if command == "source_plan_sync":
            return self._commit_source_sync(stack["planner"].create(payload))
        if command == "source_preview_sync_plan":
            return self._commit_source_sync(stack["planner"].preview(payload))
        if command == "source_confirm_sync_plan":
            return self._commit_source_sync(stack["planner"].confirm(payload))
        if command == "source_invalidate_sync_plan":
            return self._commit_source_sync(stack["planner"].invalidate(payload))
        if command == "source_get_operation":
            return stack["operations"].get(payload)
        return self._commit_source_sync(stack["operations"].cancel(payload))

    def _commit_source_sync(self, result: dict[str, Any]) -> dict[str, Any]:
        """FEA-11 (C-17 §5.2): plan/operation rows are durable at the command
        boundary. The store writers run inside the receiver's transaction; a
        later ``BEGIN IMMEDIATE`` (apply) must not see an open transaction."""
        repository = getattr(self._core, "repository", None)
        conn = getattr(repository, "_conn", None)
        if conn is not None:
            conn.commit()
        return result

    def _lineage_hidden_region_ids(self, page_id: str) -> frozenset[str]:
        """FEA-11-LINEAGE-1 (C-17 §7.1): the page's live regions that the
        lineage isolation guard excludes from ordinary read faces.

        Used ONLY for diagnostics (r2 requirement: filtering must be visible,
        never a silent loss); the actual filtering happens inside the
        application/render/export services through the SAME guard.
        """
        guard = getattr(self._core, "lineage_guard", None)
        if guard is None:
            return frozenset()
        rows = self._core.conn.execute(
            "SELECT region_id, current_revision_id FROM regions"
            " WHERE page_id = ? AND deleted_at IS NULL",
            (page_id,),
        ).fetchall()
        if not rows:
            return frozenset()
        verdict = guard.page_verdict(
            page_id,
            [(row["region_id"], row["current_revision_id"]) for row in rows],
        )
        return verdict.hidden_region_ids

    def _log_lineage_hidden(self, command: str, page_id: str) -> None:
        hidden = self._lineage_hidden_region_ids(page_id)
        if hidden:
            print(
                f"[core.{command}] page={page_id} lineage_hidden={len(hidden)}",
                file=sys.stderr,
            )

    def _assert_source_sync_gate(self, page_id: str) -> None:
        """FEA-11 (C-17 §3.3): refuse reads/writes through a binding whose
        publication gate is still pending (SOURCE_ACCESS_DENIED). Legacy v7
        bindings without a publication row keep the old rules; a *new sync*
        binding without one is corruption and fails closed."""
        stack = getattr(self._core, "source_sync", None)
        if stack is None:
            return
        store = stack["store"]
        binding = store.current_binding_of_page(page_id)
        if binding is None:
            return
        gate = store.gate_of_binding(binding["binding_id"])
        if gate is None:
            # No publication row: a pre-v8 (legacy) binding. Only bindings
            # created after v8 always carry one — check lineage provenance
            # markers by looking for any publication referencing the page's
            # binding chain (fail-closed for fresh sync bindings).
            previous = store.gate_of_binding(
                binding["previous_binding_id"]
            ) if binding.get("previous_binding_id") else None
            if previous is not None:
                raise SourceImportError(
                    "SOURCE_ACCESS_DENIED",
                    "page binding has no read gate",
                )
            return
        if gate["read_gate"] != "open":
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED",
                "page binding is pending acknowledgement",
            )

    def _assert_source_sync_gates(self, page_ids: list[str]) -> None:
        for page_id in page_ids:
            self._assert_source_sync_gate(page_id)

    def _refuse_pending_gate_writes(self, payload: dict[str, Any]) -> None:
        """Region write face gate: extract the page(s) a write touches and
        refuse when their binding publication gate is pending."""
        stack = getattr(self._core, "source_sync", None)
        if stack is None or not isinstance(payload, dict):
            return
        store = stack["store"]
        page_ids: list[str] = []
        page_id = payload.get("page_id")
        if isinstance(page_id, str) and page_id:
            page_ids.append(page_id)
        region_ids: list[str] = []
        region_id = payload.get("region_id")
        if isinstance(region_id, str) and region_id:
            region_ids.append(region_id)
        raw_region_ids = payload.get("region_ids")
        if isinstance(raw_region_ids, list):
            region_ids.extend(
                item for item in raw_region_ids if isinstance(item, str)
            )
        for candidate in region_ids:
            row = store._conn.execute(  # noqa: SLF001 - store owns the conn
                "SELECT page_id FROM regions WHERE region_id = ?",
                (candidate,),
            ).fetchone()
            if row is not None:
                page_ids.append(row["page_id"])
        pending = store.pending_gate_pages(page_ids)
        if pending:
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED",
                "page binding is pending acknowledgement",
            )

    def _refuse_pending_gate_chapter(self, chapter_id: str) -> None:
        """Reader projection gate: refuse while any page of the chapter is
        still behind a pending publication gate (C-17 §3.3)."""
        stack = getattr(self._core, "source_sync", None)
        if stack is None:
            return
        pages = self._core.repository.list_pages(chapter_id)
        pending = stack["store"].pending_gate_pages(
            [page.page_id for page in pages]
        )
        if pending:
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED",
                "page binding is pending acknowledgement",
            )

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
            # P09-MANAGED-READ-ROOT-TRUST-1: hash and the lazy page providers
            # below go through the frozen-root trust and read through the
            # verifying handle.  The old code resolved the path once, hashed it
            # by name and re-read it by name again in the export job -- three
            # separate resolutions of a reference a junction can redirect.
            actual_hash = self._verified_managed_sha256(page.translated_path)
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
                source_provider=lambda ref=page.original_path: self._read_verified_managed(ref),
                translated_provider=lambda ref=page.translated_path: self._read_verified_managed(ref),
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
        request = ExportRequest(
            book_id=book_id, chapter_id=page_chapter[ordered_ids[0]],
            format=format_value, output_path=target.path, pages=tuple(export_pages),
            mode="translated", overwrite_policy=OverwritePolicy.OVERWRITE,
            stale_policy=StalePolicy.ABORT if stale == "abort" else StalePolicy.CONTINUE,
            format_options=options,
            text_content_factory=(lambda effective: self._text_export_bytes(fmt, effective, text_pages)) if fmt == "text" else None,
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

    @staticmethod
    def _managed_input_unavailable(detail: str) -> P16WireError:
        """One constructor for the stable ``EXPORT_INPUT_UNAVAILABLE`` face."""

        return P16WireError("EXPORT_INPUT_UNAVAILABLE", "unavailable", detail)

    def _managed_root_trust(self) -> ManagedRootTrust:
        """The start-up identity snapshot; fail-closed when it is absent.

        P09-MANAGED-READ-ROOT-TRUST-1: every managed read/compare below is
        admitted through this snapshot.  A Core assembled by
        ``assemble_core_services`` always carries it; a hand-built Core that
        does not is a programming error, and refusing is safer than falling
        back to the resolve-then-compare pattern this task removes.
        """
        trust = getattr(self._core, "managed_root_trust", None)
        if trust is None:
            raise self._managed_input_unavailable("Managed export input is unavailable")
        return trust

    def _checked_managed_path(self, path: str) -> Path:
        # P09-MANAGED-READ-ROOT-TRUST-1: R5b's reproduction point.  The old
        # implementation resolved BOTH the configured root and the candidate,
        # so a junction injected above the root moved both sides together and
        # the containment passed before the outside file was read.  Admission
        # now goes through the frozen root identity + the opened handle's
        # canonical path, and the returned path is the handle's canonical path.
        try:
            verified = self._managed_root_trust().verify_existing(path)
        except TypedResourceChannelError as error:
            raise self._managed_input_unavailable(
                "Managed export input is unavailable"
            ) from error
        return Path(verified)

    def _reader_sha256(self, path: str, expected: str | None) -> str:
        try:
            digest, _size = self._managed_root_trust().digest_of(path)
        except TypedResourceChannelError as error:
            raise self._managed_input_unavailable(
                "Managed export input is unavailable"
            ) from error
        if expected and expected != digest:
            raise self._managed_input_unavailable("Reader input failed integrity verification")
        return digest

    def _read_verified_managed(self, path: str) -> bytes:
        """Provider used by lazy export reads: verify + read, same handle."""

        try:
            return self._managed_root_trust().read_bytes(path)
        except TypedResourceChannelError as error:
            raise self._managed_input_unavailable(
                "Managed export input is unavailable"
            ) from error

    def _verified_managed_sha256(self, path: str) -> str:
        """Digest of a managed file through the verifying handle (no re-open)."""

        try:
            digest, _size = self._managed_root_trust().digest_of(path)
        except TypedResourceChannelError as error:
            raise self._managed_input_unavailable(
                "A translated input is unavailable"
            ) from error
        return digest

    def _materialise_verified_managed_copy(self, ref: str, payload: bytes) -> Path:
        """Write already-verified bytes to a private temp file.

        The preview publisher copies its source by NAME.  Handing it the
        managed path would reintroduce a check-then-open window; handing it a
        file we just created closes it (the bytes are ours, not a resolution
        of the managed reference).
        """

        suffix = Path(ref).suffix
        handle = tempfile.NamedTemporaryFile(
            prefix="p09-verified-", suffix=suffix, delete=False
        )
        try:
            with handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        except BaseException:
            Path(handle.name).unlink(missing_ok=True)
            raise
        return Path(handle.name)

    def _export_regions(self, page_id: str) -> list[dict]:
        rows = self._core.conn.execute(
            "SELECT region_id, reading_order, geometry_json, text_json,"
            " current_revision_id FROM regions"
            " WHERE page_id = ? AND deleted_at IS NULL ORDER BY reading_order, region_id",
            (page_id,),
        ).fetchall()
        # FEA-11-LINEAGE-1 (C-17 §7.1): the export text face is an ordinary
        # read path — regions whose current revision is not proven for the
        # page's current binding are excluded (old coordinates/text never ride
        # the new image's export).
        guard = getattr(self._core, "lineage_guard", None)
        hidden: frozenset[str] = frozenset()
        if guard is not None and rows:
            verdict = guard.page_verdict(
                page_id,
                [
                    (row["region_id"], row["current_revision_id"])
                    for row in rows
                ],
            )
            hidden = verdict.hidden_region_ids
        result = []
        for row in rows:
            if row["region_id"] in hidden:
                continue
            geometry, text = json.loads(row["geometry_json"]), json.loads(row["text_json"])
            result.append({
                "region_id": row["region_id"], "reading_order": row["reading_order"],
                "geometry": geometry, "ocr_text": text.get("ocr_text", ""),
                "translated_text": text.get("final_translation") or text.get("machine_translation", ""),
            })
        if hidden:
            # r2: the export text face reports the filtered count instead of
            # silently returning a shorter page.
            print(
                f"[core.export_text] page={page_id} lineage_hidden={len(hidden)}",
                file=sys.stderr,
            )
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
        # P09-MANAGED-READ-ROOT-TRUST-1: the managed side is a PURE LEXICAL
        # comparison against the frozen canonical root.  Resolving the managed
        # references here let a junction injected above the configured root move
        # the "protected" set onto the outside tree, so the real managed
        # originals stopped matching and could be overwritten by an export.
        # The user-selected target keeps its single resolve() -- it is not
        # managed data and has no frozen identity to compare against.
        trust = getattr(self._core, "managed_root_trust", None)
        target = target.parent.resolve() / target.name
        if trust is None:
            # Fail-closed: without the frozen baseline we cannot prove the
            # target is not a managed file.
            return True
        rows = self._core.conn.execute(
            "SELECT managed_original_ref AS path FROM pages WHERE managed_original_ref IS NOT NULL"
            " UNION ALL SELECT managed_path AS path FROM artifact_revisions"
        ).fetchall()
        normalized_target = os.path.normcase(str(target))
        for row in rows:
            try:
                protected = trust.canonical_of(row["path"])
            except TypedResourceChannelError:
                continue
            if os.path.normcase(protected) == normalized_target:
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
            if command in {"AcceptRun", "StartRun", "ControlRun", "ResumeBlockedRun", "RetryFailedTargets"}:
                if not self._run_owner and not self._serving:
                    self._start_run_scheduler()
                if not self._run_owner:
                    raise PipelineError("INVALID_RUN_TRANSITION", "Run scheduler owner is unavailable")
            if command in {"PrepareRun", "AcceptRun"}:
                if protocol_minor != 12:
                    raise PipelineError("INVALID_REQUEST", "PreparedRun requires wire 2.12")
                if command == "PrepareRun":
                    if not {"command", "scope"} <= set(payload) or set(payload) - {"command", "scope", "overrides"}:
                        raise PipelineError("INVALID_REQUEST", "PrepareRun shape is invalid")
                    if payload["command"] not in COMMAND_CATALOG or not isinstance(payload.get("overrides", {}), dict):
                        raise PipelineError("INVALID_REQUEST", "PrepareRun fields are invalid")
                    # RR-06: the same binding-shape gate StartRun applies; never a Core AttributeError.
                    prepared_overrides = payload.get("overrides", {})
                    if ("provider_bindings" in prepared_overrides
                            and not isinstance(prepared_overrides.get("provider_bindings"), dict)):
                        raise PipelineError("INVALID_REQUEST", "provider_bindings must be an object")
                    # R-004: Prepare carries the same override semantics as StartRun (wire 2.7 only).
                    if "provider_profiles" in prepared_overrides:
                        raise PipelineError("INVALID_REQUEST", "provider profile overrides require Core 2.6")
                    result = self._core.pipeline.prepare_run(
                        payload["command"], self._parse_run_scope(payload["scope"]),
                        overrides=payload.get("overrides", {}),
                    )
                else:
                    prepared = payload.get("prepared_run")
                    if set(payload) != {"prepared_run", "idempotency_key"} or not isinstance(prepared, dict):
                        raise PipelineError("RUN_SNAPSHOT_INCOMPLETE", "PreparedRun is required")
                    run, created = self._core.pipeline.accept_prepared_run(
                        prepared, self._parse_run_scope(prepared.get("scope")),
                        idempotency_key=payload.get("idempotency_key"),
                    )
                    result = {"run_id": run.run_id, "status": "pending" if created else run.status.value}
            elif command == "StartRun":
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
                "RUN_STALE_PREVIEW": "conflict",
                "RUN_PREVIEW_EXPIRED": "conflict",
                "RUN_SNAPSHOT_INCOMPLETE": "unavailable",
                # FEA-11-LINEAGE-1 (C-17 §7.1): a Run whose target region is
                # not proven for the current binding is refused typed.
                LINEAGE_BINDING_CHANGED: "conflict",
                LINEAGE_UNVERIFIED: "conflict",
            }.get(code, "validation")
            message = {
                "INVALID_REQUEST": "Run request is invalid",
                "TARGET_NOT_FOUND": "Requested Run or target was not found",
                "IDEMPOTENCY_KEY_REUSED": "Idempotency key was used for a different request",
                "INVALID_RUN_TRANSITION": "Run operation is not valid in the current state",
                LINEAGE_BINDING_CHANGED: (
                    "region coordinates belong to a previous source binding"
                ),
                LINEAGE_UNVERIFIED: (
                    "region coordinates are not verified for the current source"
                ),
            }.get(code, "Run request could not be accepted")
            response = {
                "protocol": PROTOCOL_NAME,
                "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                "request_id": request_id,
                "result": None,
                "error": make_error_envelope(code, category, message, retryable=code == "RUN_SNAPSHOT_INCOMPLETE"),
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
        if command in {"PrepareRun", "AcceptRun"}:
            response["version"]["minor"] = 12
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
        # SETTINGS-OPEN-B-2: the cleanup faces join the settings pair in the
        # safe-request-id projection -- a rejection must never echo a
        # path-shaped request id back to the caller (SEC-FIX-PATH-ECHO-1
        # precedent; the cleanup projection itself is path-free).
        projected_request_commands = (
            "settings.get",
            "settings.update_section",
            *_CLEANUP_COMMANDS,
        )
        safe_request_id = (
            _project_settings_value(request_id)
            if command in projected_request_commands
            else request_id
        )
        raw_payload = req.get("payload")
        payload = raw_payload if isinstance(raw_payload, dict) else {}

        if req.get("channel") == "host-control":
            if command in projected_request_commands:
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

        if command in _PREVIEW_COMMANDS or command in _TRASH_COMMANDS:
            # FEA-12 (C-04b §2.1 / C-09 SC-B06): the delete-preview family is
            # frozen at wire minor 11 and the recycle-bin family at wire minor
            # 13; both are independent per-command families (the envelope's
            # default minor 3 is untouched by them).
            expected_minor = (
                _PREVIEW_PROTOCOL_MINOR
                if command in _PREVIEW_COMMANDS
                else _TRASH_PROTOCOL_MINOR
            )
            result = None
            error = None
            if protocol != PROTOCOL_NAME or not is_valid_version:
                error = {
                    "code": "PROTOCOL_VERSION_UNSUPPORTED",
                    "category": "validation",
                    "retryable": False,
                }
            elif (
                type(version.get("minor")) is not int
                or version["minor"] != expected_minor
            ):
                error = {
                    "code": "INVALID_REQUEST",
                    "category": "validation",
                    "retryable": False,
                }
            elif command == "PreviewPermanentDeleteBooks":
                result, error = self.handle_preview_permanent_delete_books(raw_payload)
            elif command == "MoveToTrash":
                result, error = self.handle_move_to_trash(raw_payload)
            elif command == "RestoreFromTrash":
                result, error = self.handle_restore_from_trash(raw_payload)
            elif command == "ListTrash":
                result, error = self.handle_list_trash(raw_payload)
            else:
                # PurgeTrash: frozen wire registration only; the first release
                # fails closed with a typed unsupported error (see handler).
                result, error = self.handle_purge_trash(raw_payload)
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": expected_minor},
                    "request_id": request_id if isinstance(request_id, str) else None,
                    "result": result,
                    "error": error,
                },
                False,
            )

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
            except SourceImportError as caught:
                result = None
                error = _source_import_error_envelope(caught)
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

        if command in _REFERENCED_IMPORT_COMMANDS:
            # FEA-09 (C-16 §4): async accept→poll import face. Minor stays 3
            # (additive widening); every typed failure maps through the
            # frozen C-16 §6 table.
            try:
                result = self._dispatch_referenced_import(command, raw_payload)
                error = None
            except SourceImportError as caught:
                result = None
                error = _source_import_error_envelope(caught)
            except Exception:
                result = None
                error = make_error_envelope(
                    "UNKNOWN", "internal", "Referenced import operation failed",
                    retryable=False,
                )
            return ({
                "protocol": PROTOCOL_NAME,
                "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                "request_id": request_id,
                "result": result,
                "error": error,
            }, False)

        if isinstance(command, str) and command in _SOURCE_SYNC_APP_COMMANDS:
            # FEA-11 (C-17 §5.1): plan lifecycle/query face, minor 3 additive.
            # GetSourceSyncCapabilities is Host-local aggregation — the Core
            # deliberately does NOT register it (UNKNOWN_COMMAND per §5.1).
            try:
                if not isinstance(raw_payload, dict):
                    raise SourceImportError(
                        "INVALID_REQUEST", "source sync request is invalid"
                    )
                result = self._dispatch_source_sync_app(command, payload)
                error = None
            except SourceImportError as caught:
                result = None
                error = _source_import_error_envelope(caught)
            except Exception:
                result = None
                error = make_error_envelope(
                    "SOURCE_SYNC_STORAGE_FAILED", "internal",
                    "Source sync operation failed", True,
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
            except SourceImportError as caught:
                # FEA-11: pending publication gates / source-read refusals
                # keep their typed C-16/C-17 projection on this face.
                result = None
                error = _source_import_error_envelope(caught)
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

        # SETTINGS-OPEN-C-2-BACKUP (design §3.4): the ``.nmbak`` backup
        # package face. The payload is typed fail-closed before any
        # filesystem work; failures use the frozen taxonomy
        # (BACKUP_NOT_FOUND / BACKUP_CORRUPT / BACKUP_RESTORE_BUSY /
        # BACKUP_RESTORE_INCOMPLETE / ...). A Core assembled without the
        # service fails closed with CORE_UNAVAILABLE.
        if command in _BACKUP_COMMANDS:
            result = None
            error = None
            try:
                if not isinstance(raw_payload, dict):
                    raise NmbakBackupError(
                        "INVALID_REQUEST",
                        "backup request payload must be a JSON object",
                    )
                if command == "backup.create":
                    result = self.handle_backup_create(raw_payload)
                elif command == "backup.list":
                    result = self.handle_backup_list()
                elif command == "backup.restore":
                    result = self.handle_backup_restore(raw_payload)
                else:
                    result = self.handle_backup_delete(raw_payload)
            except NmbakBackupError as backup_error:
                category, retryable = _BACKUP_ERROR_RULES.get(
                    backup_error.code, ("internal", False)
                )
                error = make_error_envelope(
                    code=backup_error.code,
                    category=category,
                    message=backup_error.detail[:500],
                    retryable=retryable,
                )
            except Exception:
                error = make_error_envelope(
                    code=E_UNKNOWN,
                    category="internal",
                    message="Backup operation failed",
                    retryable=False,
                )
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": safe_request_id,
                    "result": result,
                    "error": error,
                },
                False,
            )


        # PLUGIN-RUNTIME-1 (design §4.1-§4.4): the local plugin runtime face.
        # Payloads are typed fail-closed; a Core assembled without the service
        # fails closed with CORE_UNAVAILABLE. Same application-channel
        # precedent as cleanup/backup -- protocol minor stays 3.
        if command in _PLUGIN_COMMANDS:
            result = None
            error = None
            try:
                if not isinstance(raw_payload, dict):
                    raise PluginError(
                        "PLUGIN_INVALID_REQUEST",
                        "plugin request payload must be a JSON object",
                    )
                if command == "plugins.list":
                    result = self.handle_plugins_list()
                elif command == "plugins.set_enabled":
                    result = self.handle_plugins_set_enabled(raw_payload)
                elif command == "plugins.set_plugin_enabled":
                    result = self.handle_plugins_set_plugin_enabled(raw_payload)
                else:
                    result = self.handle_plugins_audit_list(raw_payload)
            except PluginError as plugin_error:
                category, retryable = _PLUGIN_ERROR_RULES.get(
                    plugin_error.code, ("internal", False)
                )
                error = make_error_envelope(
                    code=plugin_error.code,
                    category=category,
                    message=plugin_error.detail[:500],
                    retryable=retryable,
                )
            except Exception:
                error = make_error_envelope(
                    code=E_UNKNOWN,
                    category="internal",
                    message="Plugin operation failed",
                    retryable=False,
                )
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": safe_request_id,
                    "result": result,
                    "error": error,
                },
                False,
            )

        # SETTINGS-OPEN-B-2 (design §4.3): the cache/Revision maintenance
        # face -- preview / run / retry over the rebuildable webtoon tile
        # cache. Ordinary application-channel commands (settings.get
        # precedent), not HostControl: the frozen host-control envelope stays
        # limited to the HOST-ISSUER-1 grant/session set (contract §5.7).
        # Request shape is typed fail-closed BEFORE any filesystem work; the
        # result is the frozen CleanupPreview/CleanupOutcome projection.
        # A Core assembled without the service fails closed with
        # CORE_UNAVAILABLE instead of crashing the sidecar.
        if command in _CLEANUP_COMMANDS:
            try:
                if not isinstance(raw_payload, dict):
                    raise CleanupRequestError(
                        "cleanup request payload must be a JSON object"
                    )
                if command == "cleanup.preview":
                    result = self.handle_cleanup_preview()
                elif command == "cleanup.run":
                    result = self.handle_cleanup_run()
                else:
                    result = self.handle_cleanup_retry_pending()
            except CleanupRequestError as error:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": safe_request_id,
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
            except CleanupUnavailableError:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": safe_request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_CORE_UNAVAILABLE,
                            category="unavailable",
                            message="Cleanup service is unavailable",
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
                        "request_id": safe_request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_UNKNOWN,
                            category="internal",
                            message="Cleanup operation failed",
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
        # V11R-F0-2: list_page_region_texts joins this Region read branch
        # (same typed envelope: INVALID_REQUEST / TARGET_NOT_FOUND /
        # UNKNOWN; the raw error text never rides the wire).
        # FEA-05-WIRE-1: Draft command surface (C078-C083). Additive
        # widening of the same JSON-lines envelope; no new error semantics
        # beyond the typed DraftError mapping (FEA-05_DRAFT_WIRE_CONTRACT.md §3).
        if command in (
            "drafts_open",
            "drafts_patch",
            "drafts_prepare",
            "drafts_apply",
            "drafts_status",
            "drafts_discard",
        ):
            try:
                result = self._dispatch_draft_command(command, payload)
            except DraftError as error:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": _draft_error_envelope(error),
                    },
                    False,
                )
        if command in (
            "set_region_type",
            "list_regions",
            "list_region_revisions",
            "restore_region_revision",
            "list_page_region_texts",
        ):
            try:
                if command == "set_region_type":
                    result = self.handle_set_region_type(payload)
                elif command == "list_region_revisions":
                    result = self.handle_list_region_revisions(payload)
                elif command == "restore_region_revision":
                    result = self.handle_restore_region_revision(payload)
                elif command == "list_page_region_texts":
                    result = self.handle_list_page_region_texts(payload)
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
            except LineageVerificationError as error:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": _lineage_error_envelope(error),
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

        # V11R-F0-1: the Region write face (audit §5.1 F-01 -- the write
        # commands did not exist on the wire). Additive command surface on the
        # SAME Region family minor (3) as set_region_type/list_regions; the
        # branches above keep their exact semantics. Request validation is
        # typed fail-closed BEFORE any persistence; the typed error literals
        # are the existing ones only (INVALID_REQUEST / INPUT_REVISION_CHANGED
        # / TARGET_NOT_FOUND / UNKNOWN), with SCREAMING_SNAKE_CASE codes.
        if command in _REGION_WRITE_COMMANDS:
            try:
                result = self._dispatch_region_write(command, payload)
            except SourceImportError as caught:
                # FEA-11: pending publication gates refuse live edits with
                # their typed C-17 projection.
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {
                            "major": PROTOCOL_MAJOR,
                            "minor": PROTOCOL_MINOR,
                        },
                        "request_id": request_id,
                        "result": None,
                        "error": _source_import_error_envelope(caught),
                    },
                    False,
                )
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
            except RegionLimitExceeded as error:
                # I3/P2-A/B: bounded inputs (page region cap, vertex cap) are a
                # validation failure, never a conflict/internal error.
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
            except RegionLookupError as error:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_TARGET_NOT_FOUND,
                            category="not_found",
                            message=error.message,
                            retryable=False,
                        ),
                    },
                    False,
                )
            except RegionNotFound:
                # A lookup the service raised before the handler's own
                # projection (e.g. the region row vanished between the
                # validation read and the write) keeps the same typed
                # not_found row; the raw exception text never rides the wire.
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
            except LineageVerificationError as error:
                # FEA-11-LINEAGE-1 (C-17 §7.1): a user edit must never launder
                # old-binding coordinates into a native revision on the
                # current binding — typed refusal with zero write.
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": _lineage_error_envelope(error),
                    },
                    False,
                )
            except Exception:
                # Internal failure: a fixed safe phrase per command family --
                # no raw exception text, paths or user data ride the wire.
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_UNKNOWN,
                            category="internal",
                            message="Region write failed",
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
            except SourceImportError as caught:
                return ({"protocol": PROTOCOL_NAME,
                         "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                         "request_id": request_id, "result": None,
                         "error": _source_import_error_envelope(caught)}, False)
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
        if command in {"PrepareRun", "AcceptRun"}:
            response_minor = 12
        elif command in _CREATE_COMMANDS:
            response_minor = _CREATE_PROTOCOL_MINOR
        elif command in _DELETE_COMMANDS:
            response_minor = _DELETE_PROTOCOL_MINOR
        elif command in _PREVIEW_COMMANDS:
            response_minor = _PREVIEW_PROTOCOL_MINOR
        elif command in _TRASH_COMMANDS:
            response_minor = _TRASH_PROTOCOL_MINOR
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


#: Binding failures that mean "this data root moved" rather than "this catalog is
#: unusable": the binding records the old volume/file identities, so a copied,
#: restored or relocated data root can never match them. Every other namespace
#: error (foreign schema, missing table, unreadable identity) must still abort.
_BINDING_MISMATCH_MARKERS = (
    "different derived root",
    "different catalog identity",
    "namespace binding identity mismatch",
    "namespace lock and catalog bindings differ",
)


def _is_binding_mismatch(error: BaseException) -> bool:
    text = str(error)
    return any(marker in text for marker in _BINDING_MISMATCH_MARKERS)


def _ensure_preview_namespace(catalog_db: Path, derived_root: Path) -> None:
    """Bind (or re-bind after migration) the preview namespace before serving.

    REALUSE-DATA-SAFETY-1 AC1: a data root that was copied, restored from a
    whole-directory backup or moved to a new machine carries a lock/catalog
    binding with the OLD filesystem identities. The frozen initializer refuses
    such a binding, which used to abort the sidecar before it could serve; the
    rebind refreshes only the identities and keeps all catalog rows.

    The self-heal is deliberately narrow: it runs ONLY when the lock is
    readable and its binding agrees with the catalog row, i.e. both halves of
    the binding travelled together (the whole-directory copy/restore case).
    A damaged/unreadable/absent lock or a lock that contradicts the catalog is
    still a typed refusal -- nothing proves it is a migration rather than
    tampering (tests/core/test_core_namespace_bootstrap.py pins that).
    """

    if catalog_db.exists():
        binding = read_lock_binding_if_any(str(derived_root))
        if binding is not None:
            try:
                verify_binding_for_root(binding, catalog_db, derived_root)
                return
            except TypedResourceChannelError as error:
                if not _is_binding_mismatch(error):
                    raise
                _rebind_after_migration(catalog_db, derived_root, error)
                return
        if restore_namespace_lock(catalog_db, derived_root):
            return
    initialize_namespace(catalog_db, derived_root)


def _rebind_after_migration(
    catalog_db: Path, derived_root: Path, error: BaseException
) -> None:
    binding = rebind_namespace(catalog_db, derived_root, reason=str(error))
    print(
        "[core.namespace] data root identity changed ("
        f"{error}); re-bound preview namespace: derived_root={binding.derived_root}",
        file=sys.stderr,
        flush=True,
    )


#: How many automatic packages (first-run / pre-migration / pre-restore) to keep.
_AUTOMATIC_BACKUP_KEEP = 5

#: REALUSE-DATA-SAFETY-1 review M3: a verified package older than this no longer
#: covers data imported since, so start-up rotates a fresh one in.
_AUTOMATIC_BACKUP_REFRESH_HOURS = 24


def _package_age_hours(created_at: object) -> float:
    """Age of a package in hours; unknown/unparsable timestamps count as stale."""

    if not isinstance(created_at, str) or not created_at:
        return math.inf
    try:
        parsed = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except ValueError:
        return math.inf
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - parsed).total_seconds() / 3600.0


def _ensure_automatic_backup(core) -> None:
    """AC2: guarantee a verified ``.nmbak`` keeps covering an existing library.

    A fresh empty library has nothing to protect; a library with books does.
    Failures are reported to stderr and never abort start-up -- an unwritable
    backups directory must not make the product unusable.

    REALUSE-DATA-SAFETY-1 review M3: treating "any verified package exists" as
    full coverage was wrong. After the very first start the library kept growing
    (imports, pipeline output) while no new automatic package was ever created,
    so a data loss would roll back to the cold-start snapshot. Coverage now has
    an age: a package older than ``_AUTOMATIC_BACKUP_REFRESH_HOURS`` is rotated,
    and ``_prune_automatic_backups`` still bounds the total.
    """

    service = getattr(core, "backup", None)
    if service is None:
        return
    try:
        entries = service.list_backups()
        try:
            books = core.conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        except sqlite3.Error:
            return
        if books == 0:
            _prune_automatic_backups(service, entries)
            return
        verified = [entry for entry in entries if entry.get("verified")]
        newest = (
            max(verified, key=lambda entry: str(entry.get("created_at") or ""))
            if verified
            else None
        )
        if newest is None:
            created = service.create(
                "automatic", "first writable start with an existing library"
            )
            print(
                "[core.backup] automatic first-run backup created: "
                f"{created['backup_id']} ({created['size_bytes']} bytes, "
                f"verified={created['verified']})",
                file=sys.stderr,
                flush=True,
            )
            _prune_automatic_backups(service, service.list_backups())
            return
        age_hours = _package_age_hours(newest.get("created_at"))
        if age_hours >= _AUTOMATIC_BACKUP_REFRESH_HOURS:
            created = service.create(
                "automatic",
                f"scheduled rotation: newest verified package is {age_hours:.1f}h old",
            )
            print(
                "[core.backup] automatic rotation backup created: "
                f"{created['backup_id']} ({created['size_bytes']} bytes, "
                f"verified={created['verified']}, previous age {age_hours:.1f}h)",
                file=sys.stderr,
                flush=True,
            )
        _prune_automatic_backups(service, service.list_backups())
    except NmbakBackupError as error:
        print(
            f"[core.backup] automatic backup skipped: {error.code}: {error.detail}",
            file=sys.stderr,
            flush=True,
        )


def _prune_automatic_backups(service, entries) -> None:
    """Keep the newest ``_AUTOMATIC_BACKUP_KEEP`` automatic packages only.

    Manual packages are never pruned: a user-created backup is an explicit
    intent, while the automatic ones exist to bound disk growth.
    """

    automatic = sorted(
        (
            entry
            for entry in entries
            if entry.get("verified")
            and entry.get("backup_type") in ("automatic", "pre_migration", "pre_restore")
        ),
        key=lambda entry: entry.get("created_at") or "",
    )
    excess = len(automatic) - _AUTOMATIC_BACKUP_KEEP
    if excess <= 0:
        return
    for entry in automatic[:excess]:
        try:
            service.delete(entry["backup_id"])
        except NmbakBackupError:
            pass


def main() -> int:
    env_root = os.environ.get("NEWMANGA_DATA_ROOT")
    data_root = Path(env_root) if env_root else default_data_root()
    # UPGRADE-LEGACY-LAYOUT-1: older builds kept the library under <root>/data/.
    # Promote it once, before anything opens the database; a broken legacy file
    # is reported but must not prevent start-up (the current data root is then
    # used as-is).
    try:
        migration = migrate_legacy_layout(data_root)
    except LegacyLayoutError as error:
        # Refusing to continue matters: assemble_production_core would create an
        # empty root library.db on first use, after which the legacy data would
        # never be migrated again (the current layout wins). Exit instead so the
        # Host surfaces the filesystem error and the user data stays intact.
        print(
            f"[core.upgrade] legacy data layout was NOT migrated: {error}",
            file=sys.stderr,
        )
        print(
            "[core.upgrade] refusing to start while legacy data is un-migrated;"
            " fix the filesystem issue and restart",
            file=sys.stderr,
        )
        return 2
    else:
        if migration.migrated:
            print(
                "[core.upgrade] migrated legacy data layout: "
                + ", ".join(migration.copied),
                file=sys.stderr,
            )
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
        # R1-I008: production referenced resolve goes through the constrained
        # rendition cache (budget/LRU/active refs/crash recovery). A cache
        # start-up failure is logged and leaves resolve on its typed legacy
        # path instead of taking the whole Core down.
        try:
            from infrastructure.resource_channel.rendition_cache import (
                RenditionCache,
            )

            core.rendition_cache = RenditionCache(
                data_root=data_root,
                derived_root=derived_root,
                connection=core.conn,
            )
        except Exception as error:  # noqa: BLE001 - derived cache is optional
            print(
                f"[core.rendition_cache] cache unavailable: {error!r}",
                file=sys.stderr,
            )
            core.rendition_cache = None
        # REALUSE-DATA-SAFETY-1 AC2: the Host-side first-run backup only copied
        # the derived catalog, so an existing user library had no rollback
        # point. Keep one verified package before serving; idempotent and never
        # start-up-blocking.
        _ensure_automatic_backup(core)
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
                # SETTINGS-OPEN-B-2: the cleanup faces are served from the
                # assembly-injected CleanupService (tile-cache inventory +
                # ManagedFileStorage remover + the shared trash manifest).
                cleanup=core.cleanup,
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
