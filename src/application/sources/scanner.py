"""FEA-11 source scan → diff (C-17 §5 ScanSourceSync).

Combines the live source-read grant (lease + digest strong verification, no
cache substitution), the FEA-09 five-kind scanner and the C-15 §3.2 matcher
into the frozen ``Scan`` DTO, and keeps the scan alive in-process for the
TTL window so ``PlanSourceSync`` can prove the body matches a live scan.
Scans never write to the database.
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field

from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.scanner import scan_source
from application.sources.errors import SourceSyncError, stale
from application.sources.matcher import match_entries
from application.sources.model import (
    identity_digest_of,
    now_millis,
    valid_id,
    valid_enum,
    valid_project_ids,
    valid_string_array,
    validate_missing_observation,
)

#: Scan TTL (C-17 §5.3: scan/plan TTL both ≤ 300s).
SCAN_TTL_SECONDS = 300.0

#: Frozen pixel-profile contract (FEA-11-MATCH-1 card C1–C9; C-17 §5.2
#: ``PixelProfile``). The values are contract-level constants: a decoder or
#: Pillow upgrade must change them explicitly, never silently reuse an old
#: digest as "comparable".
PIXEL_PROFILE_ALGORITHM = "pixel-digest/1"
#: ``decoder``/``decoder_version`` are contract IDs (C-17 §5: no path
#: characters), so the legacy ``referenced-import/1`` default cannot be used
#: verbatim — the version lives in its own field (pending DSH adjudication).
PIXEL_DECODER_NAME = "referenced-import"
PIXEL_DECODER_VERSION = "1"
PIXEL_PILLOW_VERSION = "12.3.0"  # requirements.txt pins pillow==12.3.0
PIXEL_PARAMS: dict = {
    "alpha": "opaque-only",
    "color_management": "none",
    "exif_transpose": True,
    "frame": 0,
    "mode": "RGB",
    "pillow_version": PIXEL_PILLOW_VERSION,
    "profile": "fea11-match-rgb/1",
}


# ---------------------------------------------------------------------------
# FEA-11-SCAN-2 B1 (C-17 v1.1 §5.1/§5.2): read-only cold-start enumeration
# ---------------------------------------------------------------------------

#: C-17 v1.1 §5.3 / §5.1 enumerate bounds: silent truncation is forbidden.
SCAN_TARGETS_MAX = 10000
SCAN_TARGETS_MAX_BYTES = 8 * 1024 * 1024
#: C-17 §5 project_ids bound (P3-4): a >20-project shared source is skipped,
#: never truncated and never "current-fallbacked".
SCAN_TARGETS_MAX_PROJECT_IDS = 20
#: The five frozen FEA-09 source kinds; an unknown/widened value fails closed
#: (typed skip) instead of being guessed (P3-3).
KNOWN_SOURCE_KINDS = frozenset({"image", "folder", "zip", "cbz", "pdf"})


def _valid_scan_location_facts(candidate: dict) -> bool:
    """C-17 v1.1: the complete location facts must be present and well-formed."""
    registry_id = candidate.get("registry_id")
    generation = candidate.get("generation")
    content_digest = candidate.get("content_digest")
    volume_serial = candidate.get("volume_serial")
    file_id = candidate.get("file_id")
    size_bytes = candidate.get("size_bytes")
    return (
        isinstance(registry_id, str)
        and bool(registry_id)
        and type(generation) is int
        and generation >= 1
        and isinstance(content_digest, str)
        and len(content_digest) == 64
        and all(ch in "0123456789abcdef" for ch in content_digest)
        and type(volume_serial) is int
        and volume_serial >= 0
        and type(file_id) is int
        and file_id >= 0
        and type(size_bytes) is int
        and size_bytes >= 0
    )


def list_scan_targets(
    store,
    *,
    max_targets: int = SCAN_TARGETS_MAX,
    max_bytes: int = SCAN_TARGETS_MAX_BYTES,
) -> dict:
    """C-17 v1.1 §5.1: read-only ``ScanTargets`` enumeration (zero writes).

    ``store.list_scan_target_candidates()`` is a SELECT-level projection; this
    function only validates/computes ``identity_digest`` (from the frozen
    ``identity_digest_of`` location facts) and type-skips damaged or
    out-of-bound targets.  Skip counts are logged (stderr) — the DTO stays the
    frozen ``{targets: ScanTarget[]}`` shape, no fabricated identity and no
    truncation:

    * missing/invalid current location facts -> skip (never invent identity);
    * unknown ``source_kind`` -> fail-closed skip (never guess);
    * ``project_ids`` distinct count > 20 -> skip (never truncate/current);
    * target count > 10000 or projected JSON > 8MiB -> typed
      ``SOURCE_BUDGET_EXCEEDED`` (never silently truncate).
    """
    import json as _json
    import sys as _sys

    skipped = {
        "missing_location_facts": 0,
        "unknown_source_kind": 0,
        "project_ids_over_limit": 0,
    }
    targets: dict[str, dict] = {}
    for candidate in store.list_scan_target_candidates():
        source_id = candidate.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            skipped["missing_location_facts"] += 1
            continue
        source_kind = candidate.get("source_kind")
        if source_kind not in KNOWN_SOURCE_KINDS:
            skipped["unknown_source_kind"] += 1
            continue
        if not _valid_scan_location_facts(candidate):
            skipped["missing_location_facts"] += 1
            continue
        project_ids = sorted(
            {
                project_id
                for project_id in (candidate.get("project_ids") or [])
                if isinstance(project_id, str) and project_id
            }
        )
        if len(project_ids) > SCAN_TARGETS_MAX_PROJECT_IDS:
            skipped["project_ids_over_limit"] += 1
            continue
        if len(targets) + 1 > max_targets:
            raise SourceSyncError(
                "SOURCE_BUDGET_EXCEEDED",
                "scan target enumeration budget exceeded",
            )
        if source_id in targets:
            # Defensive uniqueness: the first (authoritative) candidate wins.
            continue
        targets[source_id] = {
            "source_id": source_id,
            "registry_id": candidate["registry_id"],
            "generation": candidate["generation"],
            "source_kind": source_kind,
            "identity_digest": identity_digest_of(
                candidate["content_digest"],
                candidate["volume_serial"],
                candidate["file_id"],
                candidate["size_bytes"],
            ),
            "project_ids": project_ids,
        }
    ordered = [targets[source_id] for source_id in sorted(targets)]
    if (
        skipped["missing_location_facts"]
        or skipped["unknown_source_kind"]
        or skipped["project_ids_over_limit"]
    ):
        print(
            "[core.source_list_scan_targets] skipped"
            f" missing_location_facts={skipped['missing_location_facts']}"
            f" unknown_source_kind={skipped['unknown_source_kind']}"
            f" project_ids_over_limit={skipped['project_ids_over_limit']}",
            file=_sys.stderr,
        )
    result = {"targets": ordered}
    encoded = _json.dumps(result, separators=(",", ":"), ensure_ascii=False)
    if len(encoded.encode("utf-8")) > max_bytes:
        raise SourceSyncError(
            "SOURCE_BUDGET_EXCEEDED", "scan target enumeration budget exceeded"
        )
    return result


def canonical_pixel_params_json() -> str:
    """The frozen decoder params as canonical JSON (C8)."""
    import json

    return json.dumps(
        PIXEL_PARAMS,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )



def _invalid(message: str) -> SourceSyncError:
    return SourceSyncError("INVALID_REQUEST", message)


@dataclass
class _LiveScan:
    scan_id: str
    expires_at: float
    result: dict
    #: Candidate ids the Core assigned for the new container version; the
    #: apply transaction inserts exactly these rows (never Host-forged).
    candidate_version: dict | None = None
    candidate_entries: list[dict] = field(default_factory=list)
    old_version_id: str | None = None
    same_container: bool = False
    observed_at: str = ""


class SourceScanner:
    """ScanSourceSync application face (host-control only on the wire)."""

    def __init__(self, *, store, access, pdf_open=None, clock=time.time) -> None:
        self._store = store
        self._access = access
        self._pdf_open = pdf_open
        self._clock = clock
        self._lock = threading.RLock()
        self._scans: dict[str, _LiveScan] = {}

    # ------------------------------------------------------------- public
    def scan(self, payload: dict) -> dict:
        request = self._validate(payload)
        source_id = request["source_id"]
        project_ids = request["project_ids"]
        scope = request["scope"]
        grant_ids = request["grant_ids"]
        missing = request["missing"]

        location = self._store.get_source_location_current(source_id)
        if location is None:
            if grant_ids:
                # C-17 §5.3/§8: the live authorization check precedes business
                # lookups, so a revoked/expired grant reports its own typed
                # error instead of a generic missing-location result.
                self._resolve_grants(source_id, grant_ids, {})
            raise SourceSyncError(
                "SOURCE_OPERATION_NOT_FOUND",
                "source has no current location",
            )
        old_version_row = self._store.latest_source_version(source_id)

        # R-007 (FEA-11 r1): the frozen reference set is whole-source; the
        # selected projects only bound the decision scope. The digest universe
        # must cover every book referencing the source (scope=all equality is
        # checked against that whole set).
        full_references = self._store.list_source_references(source_id)
        references = [
            row for row in full_references if row["project"] in project_ids
        ]
        # scope guards (C-17 §5.3): current → exactly one project; all → the
        # frozen reference set's distinct books must equal project_ids.
        books = sorted({row["project"] for row in full_references})
        if scope == "current":
            if len(project_ids) != 1:
                raise _invalid("scope=current needs exactly one project")
            if project_ids[0] not in books and books:
                raise stale(
                    "scope",
                    "project holds no reference of this source",
                )
        else:
            if books != project_ids:
                raise stale(
                    "scope",
                    "project set does not match the frozen reference set",
                )

        missing_by_source = {item["source_id"]: item for item in missing}
        observed_missing = source_id in missing_by_source
        authorizations: list[dict] = []
        target: dict
        candidate_version: dict | None = None
        candidate_entries: list[dict] = []
        same_container = False
        new_entries: list[dict] = []

        if observed_missing:
            # Host-only MissingObservation path (C-17 §5.3): the Core
            # cross-checks registry/generation/identity against its own rows
            # for every missing source; no grant may be required and no new
            # content may be published later.
            self._verify_missing_observation(
                missing_by_source[source_id], location
            )
            if grant_ids:
                raise _invalid("a missing source takes no read grants")
            target = {
                "source_id": source_id,
                "version_id": None,
                "content_digest": None,
                "identity_digest": None,
                "entries": [],
                "status": "missing",
                "reason_code": "SOURCE_ENTRY_MISSING",
            }
            authorizations.append(
                {
                    "registry_id": missing_by_source[source_id]["registry_id"],
                    "generation": missing_by_source[source_id]["generation"],
                    "identity_digest": missing_by_source[source_id][
                        "expected_identity_digest"
                    ],
                }
            )
            old_entries = (
                self._store.list_entries_of_version(old_version_row["version_id"])
                if old_version_row is not None
                else []
            )
        else:
            if not grant_ids:
                raise _invalid("a non-missing source requires read grants")
            resolved = self._resolve_grants(source_id, grant_ids, location)
            authorizations = resolved["authorizations"]
            scanned = scan_source(resolved["resolved"], pdf_open=self._pdf_open)
            if scanned.status not in {"ok"}:
                # Encrypted/unsupported containers support limited diagnosis
                # only (C-17 §5.3): no confirmation of content change.
                reason = scanned.reason_code or "SOURCE_FORMAT_UNSUPPORTED"
                target = {
                    "source_id": source_id,
                    "version_id": None,
                    "content_digest": None,
                    "identity_digest": None,
                    "entries": [],
                    "status": scanned.status,
                    "reason_code": reason,
                }
                old_entries = []
            else:
                digest = scanned.container_digest
                same_container = (
                    old_version_row is not None
                    and old_version_row["content_digest"] == digest
                )
                if same_container:
                    # Direct continuation: reuse the committed version and
                    # its entry ids (decoder observation upgrades never
                    # resync, C-17 §6.1).
                    new_entries = self._store.list_entries_of_version(
                        old_version_row["version_id"]
                    )
                    candidate_version = None
                    target = _observation_ok(
                        source_id,
                        old_version_row["version_id"],
                        digest,
                        resolved["authorizations"][0]["identity_digest"],
                        new_entries,
                    )
                else:
                    version_id = f"sv-{uuid.uuid4().hex}"
                    now = now_millis()
                    # C12: the pixel profile is only extracted on the changed
                    # container path; same-container scans reuse committed
                    # rows and never re-decode (C-17 §6.1 observation-only).
                    profiles = _extract_pixel_profiles(
                        resolved["resolved"], scanned.entries
                    )
                    candidate_entries = _candidate_entries(
                        source_id, version_id, scanned.entries, now, profiles
                    )
                    candidate_version = {
                        "version_id": version_id,
                        "source_id": source_id,
                        "content_digest": digest,
                        "size_bytes": _container_size(resolved["resolved"]),
                        "observed_at": now,
                        "created_at": now,
                    }
                    new_entries = candidate_entries
                    # ``_observation_ok`` converts rows to EntryEvidence once;
                    # passing pre-built evidence would silently drop the
                    # pixel profile on the second conversion.
                    target = _observation_ok(
                        source_id,
                        version_id,
                        digest,
                        resolved["authorizations"][0]["identity_digest"],
                        candidate_entries,
                    )
                old_entries = (
                    self._store.list_entries_of_version(
                        old_version_row["version_id"]
                    )
                    if old_version_row is not None
                    else []
                )

        matched = match_entries(
            old_entries, new_entries, same_container=same_container
        )
        page_of_entry = {
            row["entry_id"]: row for row in references
        }
        diff: list[dict] = []
        for item in matched.items:
            if item.old_entry is not None:
                reference = page_of_entry.get(item.old_entry["entry_id"])
                page_id = reference["page"] if reference else None
            else:
                page_id = None
            # C-17 §3.2 decision contract: an unchanged entry that no page is
            # bound to is not a page-level difference (there is no page to
            # keep); leaving it in the diff would make the 1:1 decisions
            # contract unsatisfiable. Real containers routinely carry unused
            # members, so this filter is the honest page-level projection.
            if page_id is None and item.classification in ("unchanged", "missing"):
                # R-005: an unused member disappearing is not a page-level
                # difference either; a null-page missing item would make the
                # frozen PlanBody contract unsatisfiable.
                continue
            diff.append(
                {
                    "item_id": item.item_id,
                    "classification": item.classification,
                    "page_id": page_id,
                    "old_entry_id": (
                        item.old_entry["entry_id"] if item.old_entry else None
                    ),
                    "new_entry_id": (
                        item.new_entry["entry_id"] if item.new_entry else None
                    ),
                    "evidence": item.evidence,
                }
            )
        diff.sort(key=lambda row: row["item_id"])
        for index, row in enumerate(diff):
            row["item_id"] = f"di-{index:06d}"

        bases = []
        for row in references:
            bases.append(self._page_base(row))
        bases.sort(key=lambda item: (item["project_id"], item["page_id"]))

        totals = {
            key: sum(1 for row in diff if row["classification"] == key)
            for key in ("unchanged", "added", "missing", "changed", "ambiguous")
        }
        scan_id = f"sc-{uuid.uuid4().hex}"
        now = self._clock()
        result = {
            "scan_id": scan_id,
            "expires_at": _ttl_timestamp(now + SCAN_TTL_SECONDS),
            "source": target,
            "base_sources": [
                {
                    "source_id": source_id,
                    "version_id": (
                        old_version_row["version_id"]
                        if old_version_row is not None
                        else location["content_digest"][:64]
                    ),
                    "content_digest": location["content_digest"],
                }
            ],
            "authorizations": authorizations,
            "missing": [
                missing_by_source[key] for key in sorted(missing_by_source)
            ],
            "bases": bases,
            "reference_set_digest": self._store.reference_set_digest(
                full_references
            ),
            "diff": diff,
            "totals": totals,
        }
        record = _LiveScan(
            scan_id=scan_id,
            expires_at=now + SCAN_TTL_SECONDS,
            result=result,
            candidate_version=candidate_version,
            candidate_entries=candidate_entries,
            old_version_id=(
                old_version_row["version_id"] if old_version_row else None
            ),
            same_container=same_container,
            observed_at=now_millis(),
        )
        with self._lock:
            self._gc_locked()
            self._scans[scan_id] = record
        return result

    def take_live_scan(self, scan_id: str) -> _LiveScan:
        with self._lock:
            record = self._scans.get(scan_id)
            if record is None or record.expires_at <= self._clock():
                raise stale("expired", "source scan is not live")
            return record

    # ----------------------------------------------------------- helpers
    def _validate(self, payload: dict) -> dict:
        if not isinstance(payload, dict):
            raise _invalid("scan payload must be an object")
        keys = {
            "source_id", "project_ids", "scope", "kind", "grant_ids", "missing",
        }
        if set(payload) != keys:
            raise _invalid("scan payload fields do not match the closed shape")
        return {
            "source_id": valid_id(payload["source_id"], field="source_id"),
            "project_ids": valid_project_ids(payload["project_ids"]),
            "scope": valid_enum(payload["scope"], ("current", "all"), field="scope"),
            "kind": valid_enum(
                payload["kind"], ("relink", "repoint", "resync"), field="kind"
            ),
            "grant_ids": (
                []
                if payload["grant_ids"] == []
                else valid_string_array(
                    payload["grant_ids"], field="grant_ids", unique=True
                )
            ),
            "missing": [
                validate_missing_observation(item)
                for item in payload["missing"]
            ],
        }

    def _resolve_grants(
        self, source_id: str, grant_ids: list[str], location: dict
    ) -> dict:
        """Resolve every grant live and pin the authorization baseline.

        The grant covers the *target* container (which may be the same bytes
        as the recorded location — direct continuation — or a changed /
        repointed container); the recorded location rows stay the §6.1
        SourceVersion CAS baseline the apply transaction re-reads."""
        authorizations: list[dict] = []
        resolved = None
        for grant_id in grant_ids:
            try:
                grant = self._access.resolve(grant_id)
            except SourceImportError as error:
                raise SourceSyncError(error.code, str(error)) from error
            if resolved is None:
                resolved = grant
        if resolved is None:  # pragma: no cover - validated non-empty
            raise _invalid("no grants supplied")
        facts = (
            resolved.container_facts
            if resolved.container_facts is not None
            else (
                resolved.folder_entries[0][1]
                if resolved.folder_entries
                else None
            )
        )
        if facts is None:
            raise SourceSyncError(
                "SOURCE_ACCESS_DENIED", "grant carries no physical identity"
            )
        identity = identity_digest_of(
            facts.sha256,
            int(facts.volume_serial),
            int(facts.file_id),
            int(facts.size),
        )
        authorizations.append(
            {
                "registry_id": resolved.registry_id,
                "generation": resolved.generation,
                "identity_digest": identity,
            }
        )
        del location
        return {"resolved": resolved, "authorizations": authorizations}

    def _verify_missing_observation(
        self, observation: dict, location: dict
    ) -> None:
        """Cross-check the Host's missing observation against the Core's own
        location rows (registry/generation/identity per C-17 §5.3)."""
        expected_identity = identity_digest_of(
            location["content_digest"],
            int(location["volume_serial"]),
            int(location["file_id"]),
            int(location["size_bytes"]),
        )
        if (
            observation["registry_id"] != location["registry_id"]
            or observation["generation"]
            != int(location["authorization_generation"])
            or observation["expected_identity_digest"] != expected_identity
        ):
            raise stale(
                "authorization",
                "missing observation does not match the recorded source",
            )

    def _page_base(self, reference: dict) -> dict:
        row = self._store.page_base_row(reference["page"])
        if row is None:
            raise stale("binding", "reference page has no current binding")
        regions = self._store.regions_manual_projection(reference["page"])
        runs = self._store.run_projection([reference["page"]])
        drafts = self._store.drafts_projection([reference["page"]])
        return {
            "page_id": row["page_id"],
            "project_id": row["project_id"],
            "chapter_id": row["chapter_id"],
            "binding_id": row["binding_id"],
            "binding_version": int(row["binding_version"]),
            "source_id": row["source_id"],
            "version_id": row["version_id"],
            "entry_id": row["entry_id"],
            "source_order": int(row["source_order"] or 0),
            "sort_order": int(row["sort_order"] or 0),
            "deleted": bool(row["deleted"]),
            "manual_digest": self._store.manual_digest(regions),
            "protection_digest": self._store.protection_digest(regions),
            "drafts_digest": self._store.drafts_digest(drafts),
            "runs_digest": self._store.runs_digest(runs),
        }

    def _gc_locked(self) -> None:
        now = self._clock()
        for key in [
            key for key, record in self._scans.items()
            if record.expires_at <= now
        ]:
            self._scans.pop(key, None)


def _ttl_timestamp(moment: float) -> str:
    from datetime import datetime, timezone

    return (
        datetime.fromtimestamp(moment, tz=timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _container_size(resolved) -> int:
    if resolved.container_facts is not None:
        return int(resolved.container_facts.size)
    return sum(facts.size for _path, facts in resolved.folder_entries)


def _candidate_entries(
    source_id: str, version_id: str, scanned_entries, now: str,
    profiles: list[tuple[dict | None, str | None]] | None = None,
) -> list[dict]:
    from application.importing.referenced.model import stable_sort_key

    rows: list[dict] = []
    for ordinal, item in enumerate(scanned_entries):
        pixel, reason = (
            profiles[ordinal] if profiles is not None else (None, None)
        )
        row = {
            "source_id": source_id,
            "version_id": version_id,
            "entry_id": f"se-{uuid.uuid4().hex}",
            "locator": item.locator,
            "ordinal": ordinal,
            "stable_sort_key": stable_sort_key(item.locator, ordinal),
            "content_digest_kind": item.content_digest_kind,
            "content_digest": item.content_digest,
            "encoded_digest": (
                item.content_digest
                if item.content_digest_kind == "encoded" and item.content_digest
                else None
            ),
            "pixel_digest": None,
            "pixel_digest_algorithm": None,
            "size_bytes": item.size_bytes,
            "mime_type": None,
            "width": None,
            "height": None,
            "orientation": None,
            "decoder_name": "",
            "decoder_version": "",
            "decoder_params_json": "{}",
            "created_at": now,
            # Diagnostic only (never persisted): why this entry carries no
            # complete pixel profile, projected as EntryEvidence.reason (C10).
            "pixel_reason": reason,
        }
        if pixel is not None:
            row.update(pixel)
            row["pixel_reason"] = None
        rows.append(row)
    return rows


def _entry_evidence(entry: dict) -> dict:
    pixel = None
    reason = entry.get("pixel_reason")
    if entry.get("pixel_digest"):
        params_digest = _params_digest(entry)
        if params_digest is None:
            # The stored params are not a canonical JSON object: the profile is
            # not comparable and must never be disguised as "{}" (C8).
            reason = "incomparable"
        else:
            pixel = {
                "algorithm": entry.get("pixel_digest_algorithm")
                or PIXEL_PROFILE_ALGORITHM,
                "decoder": entry.get("decoder_name") or PIXEL_DECODER_NAME,
                "decoder_version": (
                    entry.get("decoder_version") or PIXEL_DECODER_VERSION
                ),
                "params_digest": params_digest,
                "width": int(entry.get("width") or 0),
                "height": int(entry.get("height") or 0),
                "orientation": int(entry.get("orientation") or 1),
                "pixel_digest": entry["pixel_digest"],
            }
            reason = None
    elif reason is None and entry.get("content_digest") is None:
        reason = "missing_evidence"
    return {
        "entry_id": entry["entry_id"],
        "locator": entry["locator"],
        "ordinal": int(entry["ordinal"]),
        "content_digest_kind": entry.get("content_digest_kind") or "encoded",
        "content_digest": entry.get("content_digest"),
        "pixel": pixel,
        "reason": reason,
    }


def _params_digest(entry: dict) -> str | None:
    """sha256 over the **canonical JSON object** of the decoder params (C8).

    The v7 scanner hashed the raw JSON *string literal* (double encoding);
    a profile digest must be computed from the object so key order and
    whitespace do not change comparability.  Unparseable params return
    ``None`` — the caller degrades honestly instead of pretending ``{}``.
    """
    import hashlib
    import json

    value = entry.get("decoder_params_json")
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, ValueError):
            return None
    if value is None or not isinstance(value, dict):
        # C8: decoder params are a JSON object; anything else cannot be
        # compared as a profile (never disguised as ``{}``).
        return None
    try:
        canonical = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError):
        return None
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# AC-M1: pixel profile extraction (C1–C10; PDF is out of scope, L-M1)
# ---------------------------------------------------------------------------


def _reason_for_import_error(error) -> str | None:
    """C10 mapping for the *entry profile* failure; None means re-raise.

    Only profile-extraction failures may be degraded.  Grant/lease/identity
    and container failures stay typed rejections (C11) — never a catch-all.
    """
    code = getattr(error, "code", "")
    if code in ("SOURCE_PASSWORD_REQUIRED", "SOURCE_PASSWORD_INVALID"):
        return "encrypted"
    if code in ("SOURCE_FORMAT_UNSUPPORTED", "SOURCE_BUDGET_EXCEEDED"):
        return "unsupported"
    return None


def _extract_pixel_profiles(resolved, entries) -> list[tuple[dict | None, str | None]]:
    return [_extract_pixel_profile(resolved, entry) for entry in entries]


def _extract_pixel_profile(
    resolved, entry
) -> tuple[dict | None, str | None]:
    """Return ``(pixel_columns, reason)`` for one scanned entry.

    Bytes are read through the strict verified-read path only (C2); the
    decode follows C1/C4/C5/C6 and the digest follows C7.  Any failure that
    is allowed to degrade produces ``pixel=None`` + a C10 reason; other
    errors propagate as typed rejections.
    """
    from application.importing.referenced.errors import SourceImportError

    if resolved.source_kind == "pdf":
        # L-M1: no document-raster seam / raw-RGB port in this slice.
        return None, "unsupported"
    if entry.content_digest is None:
        return None, "missing_evidence"
    from application.importing.referenced.reader import read_entry_bytes

    try:
        raw = read_entry_bytes(resolved, entry)
    except SourceImportError as error:
        reason = _reason_for_import_error(error)
        if reason is None:
            raise
        return None, reason
    return _decode_pixel_profile(raw, resolved)


def _decode_pixel_profile(
    raw: bytes, resolved
) -> tuple[dict | None, str | None]:
    """Decode one entry's bytes into the frozen ``pixel-digest/1`` columns."""
    import hashlib
    import io

    from application.importing.referenced.errors import SourceImportError
    from application.importing.referenced.reader import check_decode_budget

    try:
        from PIL import Image, ImageOps
    except ImportError:  # pragma: no cover - Pillow is a pinned dependency
        return None, "unsupported"
    try:
        # Header-only open first; the budget is checked before the pixel
        # buffer is allocated (reader.py R1-I007 same-source semantics, C3).
        image = Image.open(io.BytesIO(raw))
        try:
            check_decode_budget(
                resolved, int(image.size[0]), int(image.size[1])
            )
            image.load()
            exif_orientation = _exif_orientation(image)
            if exif_orientation is None:
                return None, "unsupported"
            normalised = ImageOps.exif_transpose(image)
            columns = _rgb_pixel_columns(normalised)
        finally:
            try:
                image.close()
            except Exception:  # pragma: no cover - closing never raises
                pass
    except SourceImportError:
        # Decode-budget refusal for this entry is a per-entry degradation (C3).
        return None, "unsupported"
    except Exception:  # noqa: BLE001 - corrupt/unsupported entry, typed degrade
        return None, "unsupported"
    if columns is None:
        return None, "unsupported"
    h = hashlib.sha256()
    h.update(f"{columns[0]}x{columns[1]}".encode("ascii"))
    h.update(b"\x00")
    h.update(columns[2])
    return (
        {
            "pixel_digest": h.hexdigest(),
            "pixel_digest_algorithm": PIXEL_PROFILE_ALGORITHM,
            "width": columns[0],
            "height": columns[1],
            "orientation": 1,
            "decoder_name": PIXEL_DECODER_NAME,
            "decoder_version": PIXEL_DECODER_VERSION,
            "decoder_params_json": canonical_pixel_params_json(),
        },
        None,
    )


def _exif_orientation(image) -> int | None:
    """The EXIF orientation tag, or None when it must not be guessed (C4).

    Missing tag = 1 (normal).  Anything outside 1..8 — including the invalid
    0/9 and non-integer values — is refused instead of being normalised with
    an arbitrary rotation (C4/L-M7).
    """
    try:
        exif = image.getexif()
        orientation = exif.get(0x0112, 1)
    except Exception:  # noqa: BLE001 - unreadable EXIF is not guessable
        return None
    if isinstance(orientation, bool) or not isinstance(orientation, int):
        return None
    if orientation not in (1, 2, 3, 4, 5, 6, 7, 8):
        return None
    return orientation


def _rgb_pixel_columns(image) -> tuple[int, int, bytes] | None:
    """``(width, height, tightly-packed RGB bytes)`` or None if unsupported.

    First version requires an opaque 8-bit RGB raster (C6/L-M7): a non-fully
    opaque alpha channel (RGBA or palette transparency) yields no profile.
    """
    try:
        if image.mode == "RGB":
            rgb = image
        elif image.mode == "RGBA":
            if _alpha_min(image) < 255:
                return None
            rgb = image.convert("RGB")
        else:
            if "transparency" in getattr(image, "info", {}):
                return None
            if "A" in image.getbands():
                rgba = image.convert("RGBA")
                if _alpha_min(rgba) < 255:
                    return None
                rgb = rgba.convert("RGB")
            else:
                rgb = image.convert("RGB")
        width, height = rgb.size
        if rgb.mode != "RGB" or width <= 0 or height <= 0:
            return None
        pixels = rgb.tobytes()
        if len(pixels) != width * height * 3:
            return None
        return int(width), int(height), pixels
    except Exception:  # noqa: BLE001 - unsupported colour model
        return None


def _alpha_min(image) -> int:
    try:
        return int(image.getchannel("A").getextrema()[0])
    except Exception:  # noqa: BLE001 - no readable alpha plane
        return 0


def _observation_ok(
    source_id: str,
    version_id: str,
    content_digest: str,
    identity_digest: str,
    entries: list,
) -> dict:
    if entries and "locator" in entries[0] and "content_digest_kind" in entries[0]:
        entry_items = [_entry_evidence(entry) for entry in entries]
    else:
        entry_items = entries
    return {
        "source_id": source_id,
        "version_id": version_id,
        "content_digest": content_digest,
        "identity_digest": identity_digest,
        "entries": entry_items,
        "status": "ok",
        "reason_code": None,
    }
