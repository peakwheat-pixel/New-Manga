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

        references = self._store.list_source_references(source_id, project_ids)
        # scope guards (C-17 §5.3): current → exactly one project; all → the
        # frozen reference set's distinct books must equal project_ids.
        books = sorted({row["project"] for row in references})
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
                    candidate_entries = _candidate_entries(
                        source_id, version_id, scanned.entries, now
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
                    target = _observation_ok(
                        source_id,
                        version_id,
                        digest,
                        resolved["authorizations"][0]["identity_digest"],
                        [
                            _entry_evidence(entry) for entry in candidate_entries
                        ],
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
            "reference_set_digest": self._store.reference_set_digest(references),
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
    source_id: str, version_id: str, scanned_entries, now: str
) -> list[dict]:
    from application.importing.referenced.model import stable_sort_key

    rows: list[dict] = []
    for ordinal, item in enumerate(scanned_entries):
        rows.append(
            {
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
            }
        )
    return rows


def _entry_evidence(entry: dict) -> dict:
    pixel = None
    if entry.get("pixel_digest"):
        pixel = {
            "algorithm": entry.get("pixel_digest_algorithm")
            or "pixel-digest/1",
            "decoder": entry.get("decoder_name") or "referenced-import/1",
            "decoder_version": entry.get("decoder_version") or "1",
            "params_digest": _params_digest(entry),
            "width": int(entry.get("width") or 0),
            "height": int(entry.get("height") or 0),
            "orientation": int(entry.get("orientation") or 1),
            "pixel_digest": entry["pixel_digest"],
        }
    reason = None
    if entry.get("content_digest") is None:
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


def _params_digest(entry: dict) -> str:
    import hashlib
    import json

    return hashlib.sha256(
        json.dumps(
            entry.get("decoder_params_json") or "{}",
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


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
