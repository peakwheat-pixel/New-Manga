"""FEA-11 source-sync data model (C-17 §1/§5 DTO shapes and digests).

Canonical JSON (``canonical-json/1``), the four digest formulas, the frozen
scalar validators (ID/H/T/N/I/G) and the closed-shape validation helpers for
every C-17 §5.2 DTO. Validation is fail-closed: unknown fields, missing
fields, duplicate keys, wrong types and unknown enum values are
``INVALID_REQUEST``; no implicit string/number/bool coercion.
"""

from __future__ import annotations

import hashlib
import json
import math
import re

from application.sources.errors import SourceSyncError

# ---------------------------------------------------------------------------
# Scalar validators (C-17 §5 type table)
# ---------------------------------------------------------------------------

#: ID = non-empty string(1..128) without path/control characters.
_ID_RE = re.compile(r"^[^\x00-\x1f\x7f\\/]{1,128}$")
#: H = lowercase 64-hex.
_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
#: RFC3339 UTC timestamp with millisecond precision.
_T_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$"
)
#: Safe opaque ids the Host mints for journal file names (C-17 §3.2).
_SAFE_OPAQUE_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")

#: Message/body budget (8 MiB UTF-8, C-17 §5).
MAX_BODY_BYTES = 8 * 1024 * 1024
#: Collection cap (C-17 §5); project_ids additionally 1..20 unique sorted.
MAX_ARRAY_ITEMS = 10_000
MAX_PROJECT_IDS = 20

KINDS = ("relink", "repoint", "resync")
SCOPES = ("current", "all")
STATES = ("draft", "previewed", "confirmed", "applied", "stale")
STALE_REASONS = (
    "expired", "source", "binding", "authorization", "scope",
    "manual", "decision", "cancelled",
)
OPERATION_STATES = (
    "started", "host-authorized", "core-committed", "acknowledged",
    "failed", "recovered",
)
PUBLICATION_RELATIONS = (
    "same_content", "changed", "repoint", "added", "missing",
)
CLASSIFICATIONS = ("unchanged", "added", "missing", "changed", "ambiguous")
DIFF_EVIDENCE = (
    "direct", "unique_pixel", "duplicate_group", "missing_old",
    "incomparable", "none",
)
ACTIONS = ("keep", "add", "tombstone", "bind", "defer")
CAPABILITY_NAMES = (
    "scan", "plan", "apply", "relink", "repoint", "resync", "operation",
)
#: C-17 §4 capability strings advertised by core.ping.
CORE_CAPABILITY_STRINGS = tuple(
    f"source.sync.{name}/1" for name in CAPABILITY_NAMES
)


def _invalid(message: str) -> SourceSyncError:
    return SourceSyncError("INVALID_REQUEST", message)


def valid_id(value: object, *, field: str = "id") -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise _invalid(f"{field} is not a valid id")
    return value


def valid_hex64(value: object, *, field: str = "digest") -> str:
    if not isinstance(value, str) or not _HEX64_RE.fullmatch(value):
        raise _invalid(f"{field} is not a lowercase sha256 hex digest")
    return value


def valid_timestamp(value: object, *, field: str = "timestamp") -> str:
    if not isinstance(value, str) or not _T_RE.fullmatch(value):
        raise _invalid(f"{field} is not an RFC3339 millisecond timestamp")
    return value


def valid_opaque(value: object, *, field: str = "opaque id") -> str:
    if not isinstance(value, str) or not _SAFE_OPAQUE_RE.fullmatch(value):
        raise _invalid(f"{field} is not a safe opaque id")
    return value


def valid_int(value: object, minimum: int, maximum: int, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise _invalid(f"{field} is not an integer")
    if not minimum <= value <= maximum:
        raise _invalid(f"{field} is out of range")
    return value


def valid_enum(value: object, options, *, field: str) -> str:
    if not isinstance(value, str) or value not in options:
        raise _invalid(f"{field} is not one of the allowed values")
    return value


def valid_bool(value: object, *, field: str) -> bool:
    if not isinstance(value, bool):
        raise _invalid(f"{field} is not a boolean")
    return value


def valid_str(
    value: object, *, field: str, minimum: int = 1, maximum: int = 4096
) -> str:
    if not isinstance(value, str) or not minimum <= len(value) <= maximum:
        raise _invalid(f"{field} is not a valid string")
    return value


def require_fields(
    payload: object,
    required: dict[str, object],
    *,
    context: str,
) -> dict:
    """Closed-shape object check: exactly ``required`` keys, none missing.

    ``required`` maps field name -> value; the value is returned unchanged for
    further typed validation. Unknown/missing fields are INVALID_REQUEST.
    """
    if not isinstance(payload, dict):
        raise _invalid(f"{context} must be an object")
    keys = set(payload)
    expected = set(required)
    if keys != expected:
        raise _invalid(f"{context} fields do not match the closed shape")
    return payload


def valid_string_array(
    value: object, *, field: str, unique: bool = False, sort_check: bool = False
) -> list[str]:
    if not isinstance(value, list) or not value or len(value) > MAX_ARRAY_ITEMS:
        raise _invalid(f"{field} must be a non-empty array")
    items = [valid_id(item, field=f"{field} item") for item in value]
    if unique and len(set(items)) != len(items):
        raise _invalid(f"{field} must be unique")
    if sort_check and items != sorted(items):
        raise _invalid(f"{field} must be sorted")
    return items


def valid_project_ids(value: object, *, field: str = "project_ids") -> list[str]:
    if not isinstance(value, list) or not 1 <= len(value) <= MAX_PROJECT_IDS:
        raise _invalid(f"{field} must hold 1..{MAX_PROJECT_IDS} items")
    items = [valid_id(item, field=f"{field} item") for item in value]
    if len(set(items)) != len(items):
        raise _invalid(f"{field} must be unique")
    if items != sorted(items):
        raise _invalid(f"{field} must be sorted by id")
    return items


# ---------------------------------------------------------------------------
# canonical-json/1 and digests
# ---------------------------------------------------------------------------

def _check_canonical_value(value: object, *, field: str = "$") -> None:
    """Reject floats/NaN and non-finite numbers anywhere in the tree."""
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        raise _invalid(f"{field}: floats are not allowed in canonical-json/1")
    if isinstance(value, list):
        if len(value) > MAX_ARRAY_ITEMS:
            raise _invalid(f"{field}: array exceeds the collection cap")
        for index, item in enumerate(value):
            _check_canonical_value(item, field=f"{field}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise _invalid(f"{field}: object keys must be strings")
            _check_canonical_value(item, field=f"{field}.{key}")
        return
    raise _invalid(f"{field}: unsupported canonical-json/1 value")


def canonical_bytes(value: object) -> bytes:
    """canonical-json/1 serialization (C-17 §1).

    UTF-8, object keys sorted by Unicode code point, no whitespace, raw
    strings un-normalized, only int/bool/null/string/array/object (no
    floats). Control characters escape as lowercase ``\\u00xx`` (Python's
    json emits exactly that with ``ensure_ascii=False``).
    """
    _check_canonical_value(value)
    try:
        text = json.dumps(
            value, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        )
    except (TypeError, ValueError) as error:
        raise _invalid("value is not canonical-json/1 serializable") from error
    encoded = text.encode("utf-8")
    if len(encoded) > MAX_BODY_BYTES:
        raise SourceSyncError(
            "SOURCE_BUDGET_EXCEEDED", "canonical body exceeds the 8 MiB budget"
        )
    return encoded


def canonical_text(value: object) -> str:
    return canonical_bytes(value).decode("utf-8")


def digest_of(value: object) -> str:
    """sha256 over canonical-json/1 bytes (lowercase hex)."""
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def plan_digest_of(body: dict) -> str:
    return digest_of(body)


def request_digest_of(
    operation_id: str, plan_id: str, plan_digest: str, kind: str
) -> str:
    """C-17 §1: sha256(canonical({operation_id,plan_id,plan_digest,kind}))."""
    return digest_of(
        {
            "operation_id": operation_id,
            "plan_id": plan_id,
            "plan_digest": plan_digest,
            "kind": kind,
        }
    )


def authorization_digest_of(authorizations: list[dict]) -> str:
    """C-17 §5.2: sha256(canonical(authorizations sorted by registry_id))."""
    ordered = sorted(
        authorizations, key=lambda item: item["registry_id"]
    )
    return digest_of(ordered)


def identity_digest_of(
    content_digest: str, volume_serial: int, file_id: int, size_bytes: int
) -> str:
    """C-17 §5.2: sha256(canonical({content_digest,volume_serial,file_id,
    size_bytes})) — the facts always come from a signed grant, never from
    caller JSON."""
    return digest_of(
        {
            "content_digest": content_digest,
            "volume_serial": volume_serial,
            "file_id": file_id,
            "size_bytes": size_bytes,
        }
    )


def reference_set_digest_of(references: list[dict]) -> str:
    """Digest over the frozen reference set rows.

    Each row is ``{project,page,binding,version,status,deleted}`` (C-17 §5.3)
    sorted by (project,page).
    """
    ordered = sorted(references, key=lambda item: (item["project"], item["page"]))
    return digest_of(ordered)


def manual_digest_of(regions: list[dict]) -> str:
    """C-17 §6.1: hash of the per-region current manual projection.

    ``regions`` items carry
    ``{region_id,current_revision_id,revision_no,geometry_json,text_json,
    style_json,deleted_at}`` already sorted by region_id.
    """
    ordered = sorted(regions, key=lambda item: item["region_id"])
    return digest_of(ordered)


def run_input_digest_of(run_rows: list[dict]) -> str:
    """Projection digest over the in-flight/accepted run rows bound to the
    plan's pages (each row {run_id,target_page_id,status}; sorted)."""
    ordered = sorted(
        run_rows, key=lambda item: (item["run_id"], item["target_page_id"])
    )
    return digest_of(ordered)


# ---------------------------------------------------------------------------
# §5.2 DTO validation helpers
# ---------------------------------------------------------------------------

def validate_source_base(value: object, *, field: str = "SourceBase") -> dict:
    payload = require_fields(
        value,
        {"source_id": None, "version_id": None, "content_digest": None},
        context=field,
    )
    return {
        "source_id": valid_id(payload["source_id"], field=f"{field}.source_id"),
        "version_id": valid_id(payload["version_id"], field=f"{field}.version_id"),
        "content_digest": valid_hex64(
            payload["content_digest"], field=f"{field}.content_digest"
        ),
    }


def validate_authorization_base(
    value: object, *, field: str = "AuthorizationBase"
) -> dict:
    payload = require_fields(
        value,
        {"registry_id": None, "generation": None, "identity_digest": None},
        context=field,
    )
    return {
        "registry_id": valid_id(payload["registry_id"], field=f"{field}.registry_id"),
        "generation": valid_int(
            payload["generation"], 1, 2**53 - 1, field=f"{field}.generation"
        ),
        "identity_digest": valid_hex64(
            payload["identity_digest"], field=f"{field}.identity_digest"
        ),
    }


def validate_missing_observation(
    value: object, *, field: str = "MissingObservation"
) -> dict:
    payload = require_fields(
        value,
        {
            "source_id": None, "registry_id": None, "generation": None,
            "expected_identity_digest": None, "observed_at": None,
        },
        context=field,
    )
    return {
        "source_id": valid_id(payload["source_id"], field=f"{field}.source_id"),
        "registry_id": valid_id(payload["registry_id"], field=f"{field}.registry_id"),
        "generation": valid_int(
            payload["generation"], 1, 2**53 - 1, field=f"{field}.generation"
        ),
        "expected_identity_digest": valid_hex64(
            payload["expected_identity_digest"],
            field=f"{field}.expected_identity_digest",
        ),
        "observed_at": valid_timestamp(
            payload["observed_at"], field=f"{field}.observed_at"
        ),
    }


def validate_page_base(value: object, *, field: str = "PageBase") -> dict:
    keys = {
        "page_id", "project_id", "chapter_id", "binding_id", "binding_version",
        "source_id", "version_id", "entry_id", "source_order", "sort_order",
        "deleted", "manual_digest", "protection_digest", "drafts_digest",
        "runs_digest",
    }
    payload = require_fields(value, {key: None for key in keys}, context=field)
    signed = 2**53 - 1
    return {
        "page_id": valid_id(payload["page_id"], field=f"{field}.page_id"),
        "project_id": valid_id(payload["project_id"], field=f"{field}.project_id"),
        "chapter_id": valid_id(payload["chapter_id"], field=f"{field}.chapter_id"),
        "binding_id": valid_id(payload["binding_id"], field=f"{field}.binding_id"),
        "binding_version": valid_int(
            payload["binding_version"], 1, signed, field=f"{field}.binding_version"
        ),
        "source_id": valid_id(payload["source_id"], field=f"{field}.source_id"),
        "version_id": valid_id(payload["version_id"], field=f"{field}.version_id"),
        "entry_id": valid_id(payload["entry_id"], field=f"{field}.entry_id"),
        "source_order": valid_int(
            payload["source_order"], -signed, signed,
            field=f"{field}.source_order",
        ),
        "sort_order": valid_int(
            payload["sort_order"], -signed, signed, field=f"{field}.sort_order"
        ),
        "deleted": valid_bool(payload["deleted"], field=f"{field}.deleted"),
        "manual_digest": valid_hex64(
            payload["manual_digest"], field=f"{field}.manual_digest"
        ),
        "protection_digest": valid_hex64(
            payload["protection_digest"], field=f"{field}.protection_digest"
        ),
        "drafts_digest": valid_hex64(
            payload["drafts_digest"], field=f"{field}.drafts_digest"
        ),
        "runs_digest": valid_hex64(
            payload["runs_digest"], field=f"{field}.runs_digest"
        ),
    }


def validate_entry_evidence(value: object, *, field: str = "EntryEvidence") -> dict:
    payload = require_fields(
        value,
        {
            "entry_id", "locator", "ordinal", "content_digest_kind",
            "content_digest", "pixel", "reason",
        },
        context=field,
    )
    result = {
        "entry_id": valid_id(payload["entry_id"], field=f"{field}.entry_id"),
        "locator": valid_str(payload["locator"], field=f"{field}.locator"),
        "ordinal": valid_int(
            payload["ordinal"], 0, 2**53 - 1, field=f"{field}.ordinal"
        ),
        "content_digest_kind": valid_enum(
            payload["content_digest_kind"], ("encoded", "page-identity"),
            field=f"{field}.content_digest_kind",
        ),
        "content_digest": None,
        "pixel": None,
        "reason": None,
    }
    if payload["content_digest"] is not None:
        result["content_digest"] = valid_hex64(
            payload["content_digest"], field=f"{field}.content_digest"
        )
    if payload["pixel"] is not None:
        result["pixel"] = validate_pixel_profile(
            payload["pixel"], field=f"{field}.pixel"
        )
    if payload["reason"] is not None:
        result["reason"] = valid_enum(
            payload["reason"],
            ("encrypted", "unsupported", "missing_evidence", "incomparable"),
            field=f"{field}.reason",
        )
    return result


def _valid_orientation(value: object, *, field: str) -> int:
    if isinstance(value, bool) or value not in (1, 3, 6, 8):
        raise _invalid(f"{field} must be one of 1/3/6/8")
    return value


def validate_pixel_profile(value: object, *, field: str = "PixelProfile") -> dict:
    payload = require_fields(
        value,
        {
            "algorithm", "decoder", "decoder_version", "params_digest",
            "width", "height", "orientation", "pixel_digest",
        },
        context=field,
    )
    signed = 2**53 - 1
    return {
        "algorithm": valid_enum(
            payload["algorithm"], ("pixel-digest/1",),
            field=f"{field}.algorithm",
        ),
        "decoder": valid_id(payload["decoder"], field=f"{field}.decoder"),
        "decoder_version": valid_id(
            payload["decoder_version"], field=f"{field}.decoder_version"
        ),
        "params_digest": valid_hex64(
            payload["params_digest"], field=f"{field}.params_digest"
        ),
        "width": valid_int(payload["width"], 1, signed, field=f"{field}.width"),
        "height": valid_int(payload["height"], 1, signed, field=f"{field}.height"),
        "orientation": _valid_orientation(
            payload["orientation"], field=f"{field}.orientation"
        ),
        "pixel_digest": valid_hex64(
            payload["pixel_digest"], field=f"{field}.pixel_digest"
        ),
    }


def validate_source_observation(
    value: object, *, field: str = "SourceObservation"
) -> dict:
    payload = require_fields(
        value,
        {
            "source_id", "version_id", "content_digest", "identity_digest",
            "entries", "status", "reason_code",
        },
        context=field,
    )
    result = {
        "source_id": valid_id(payload["source_id"], field=f"{field}.source_id"),
        "version_id": None,
        "content_digest": None,
        "identity_digest": None,
        "entries": [],
        "status": valid_enum(
            payload["status"], ("ok", "missing", "encrypted", "unsupported"),
            field=f"{field}.status",
        ),
        "reason_code": None,
    }
    if payload["version_id"] is not None:
        result["version_id"] = valid_id(
            payload["version_id"], field=f"{field}.version_id"
        )
    if payload["content_digest"] is not None:
        result["content_digest"] = valid_hex64(
            payload["content_digest"], field=f"{field}.content_digest"
        )
    if payload["identity_digest"] is not None:
        result["identity_digest"] = valid_hex64(
            payload["identity_digest"], field=f"{field}.identity_digest"
        )
    if not isinstance(payload["entries"], list) or len(payload["entries"]) > MAX_ARRAY_ITEMS:
        raise _invalid(f"{field}.entries must be an array within the cap")
    result["entries"] = [
        validate_entry_evidence(item, field=f"{field}.entries[{index}]")
        for index, item in enumerate(payload["entries"])
    ]
    ordinals = [item["ordinal"] for item in result["entries"]]
    if ordinals != sorted(ordinals):
        raise _invalid(f"{field}.entries must be sorted by ordinal")
    if payload["reason_code"] is not None:
        result["reason_code"] = valid_str(
            payload["reason_code"], field=f"{field}.reason_code", maximum=128
        )
    status = result["status"]
    if status == "ok" and (
        result["version_id"] is None
        or result["content_digest"] is None
        or result["identity_digest"] is None
        or result["reason_code"] is not None
    ):
        raise _invalid(f"{field}: ok requires version/content/identity and no reason")
    if status == "missing" and (
        result["version_id"] is not None
        or result["content_digest"] is not None
        or result["identity_digest"] is not None
        or result["entries"]
        or result["reason_code"] != "SOURCE_ENTRY_MISSING"
    ):
        raise _invalid(f"{field}: missing requires empty evidence fields")
    return result


def validate_diff_item(value: object, *, field: str = "DiffItem") -> dict:
    payload = require_fields(
        value,
        {
            "item_id", "classification", "page_id", "old_entry_id",
            "new_entry_id", "evidence",
        },
        context=field,
    )
    result = {
        "item_id": valid_id(payload["item_id"], field=f"{field}.item_id"),
        "classification": valid_enum(
            payload["classification"], CLASSIFICATIONS,
            field=f"{field}.classification",
        ),
        "page_id": None,
        "old_entry_id": None,
        "new_entry_id": None,
        "evidence": valid_enum(
            payload["evidence"], DIFF_EVIDENCE, field=f"{field}.evidence"
        ),
    }
    for key in ("page_id", "old_entry_id", "new_entry_id"):
        if payload[key] is not None:
            result[key] = valid_id(payload[key], field=f"{field}.{key}")
    classification = result["classification"]
    if classification == "added":
        if result["page_id"] is not None or result["old_entry_id"] is not None \
                or result["new_entry_id"] is None:
            raise _invalid(f"{field}: added requires old null / new non-null")
    elif classification == "missing":
        if result["page_id"] is not None or result["new_entry_id"] is not None \
                or result["old_entry_id"] is None:
            raise _invalid(f"{field}: missing requires new null / old non-null")
    else:
        if result["old_entry_id"] is None or result["new_entry_id"] is None:
            raise _invalid(f"{field}: {classification} requires both entries")
    if classification == "unchanged" and result["evidence"] not in (
        "direct", "unique_pixel"
    ):
        raise _invalid(f"{field}: unchanged requires direct/unique_pixel")
    if result["evidence"] in ("duplicate_group", "missing_old", "incomparable") \
            and classification != "ambiguous":
        raise _invalid(
            f"{field}: duplicate/missing_old/incomparable must be ambiguous"
        )
    return result


def validate_totals(value: object, *, field: str = "Totals") -> dict:
    payload = require_fields(
        value,
        {"unchanged", "added", "missing", "changed", "ambiguous"},
        context=field,
    )
    result = {}
    for key in ("unchanged", "added", "missing", "changed", "ambiguous"):
        result[key] = valid_int(
            payload[key], 0, 2**53 - 1, field=f"{field}.{key}"
        )
    return result


def validate_decision(value: object, *, field: str = "Decision") -> dict:
    payload = require_fields(
        value,
        {
            "item_id", "action", "target_page_id", "target_chapter_id",
            "new_source_order", "new_sort_order", "migrate_revision_ids",
        },
        context=field,
    )
    signed = 2**53 - 1
    result = {
        "item_id": valid_id(payload["item_id"], field=f"{field}.item_id"),
        "action": valid_enum(
            payload["action"], ACTIONS, field=f"{field}.action"
        ),
        "target_page_id": None,
        "target_chapter_id": None,
        "new_source_order": None,
        "new_sort_order": None,
        "migrate_revision_ids": [],
    }
    if payload["target_page_id"] is not None:
        result["target_page_id"] = valid_id(
            payload["target_page_id"], field=f"{field}.target_page_id"
        )
    if payload["target_chapter_id"] is not None:
        result["target_chapter_id"] = valid_id(
            payload["target_chapter_id"], field=f"{field}.target_chapter_id"
        )
    for key in ("new_source_order", "new_sort_order"):
        if payload[key] is not None:
            result[key] = valid_int(
                payload[key], -signed, signed, field=f"{field}.{key}"
            )
    raw_migrate = payload["migrate_revision_ids"]
    if not isinstance(raw_migrate, list) or len(raw_migrate) > MAX_ARRAY_ITEMS:
        raise _invalid(f"{field}.migrate_revision_ids must be an array")
    result["migrate_revision_ids"] = [
        valid_id(item, field=f"{field}.migrate_revision_ids item")
        for item in raw_migrate
    ]
    action = result["action"]
    if action == "add":
        if result["target_page_id"] is not None \
                or result["target_chapter_id"] is None \
                or result["new_source_order"] is None \
                or result["new_sort_order"] is None:
            raise _invalid(f"{field}: add requires chapter and new order")
    elif action in ("bind", "keep", "tombstone"):
        if result["target_page_id"] is None or result["target_chapter_id"] is not None:
            raise _invalid(f"{field}: {action} requires target_page only")
    else:  # defer
        if any(
            result[key] is not None
            for key in (
                "target_page_id", "target_chapter_id",
                "new_source_order", "new_sort_order",
            )
        ) or result["migrate_revision_ids"]:
            raise _invalid(f"{field}: defer carries no migration targets")
    if action not in ("bind",) and result["migrate_revision_ids"]:
        raise _invalid(f"{field}: migrate_revision_ids only on bind")
    return result


def validate_confirmation(value: object, *, field: str = "Confirmation") -> dict:
    payload = require_fields(
        value,
        {"kind", "project_ids", "reference_set_digest", "resync_content"},
        context=field,
    )
    return {
        "kind": valid_enum(payload["kind"], KINDS, field=f"{field}.kind"),
        "project_ids": valid_project_ids(
            payload["project_ids"], field=f"{field}.project_ids"
        ),
        "reference_set_digest": valid_hex64(
            payload["reference_set_digest"],
            field=f"{field}.reference_set_digest",
        ),
        "resync_content": valid_bool(
            payload["resync_content"], field=f"{field}.resync_content"
        ),
    }


def validate_host_authorization(
    value: object, *, field: str = "HostAuthorization"
) -> dict:
    payload = require_fields(
        value,
        {
            "host_receipt_id", "operation_id", "request_digest",
            "authorization_digest", "authorizations", "authorized_at",
        },
        context=field,
    )
    authorizations = payload["authorizations"]
    if not isinstance(authorizations, list) or not authorizations:
        raise _invalid(f"{field}.authorizations must be a non-empty array")
    parsed = [
        validate_authorization_base(
            item, field=f"{field}.authorizations[{index}]"
        )
        for index, item in enumerate(authorizations)
    ]
    seen = {item["registry_id"] for item in parsed}
    if len(seen) != len(parsed):
        raise _invalid(f"{field}.authorizations must be unique per registry")
    return {
        "host_receipt_id": valid_opaque(
            payload["host_receipt_id"], field=f"{field}.host_receipt_id"
        ),
        "operation_id": valid_id(
            payload["operation_id"], field=f"{field}.operation_id"
        ),
        "request_digest": valid_hex64(
            payload["request_digest"], field=f"{field}.request_digest"
        ),
        "authorization_digest": valid_hex64(
            payload["authorization_digest"],
            field=f"{field}.authorization_digest",
        ),
        "authorizations": parsed,
        "authorized_at": valid_timestamp(
            payload["authorized_at"], field=f"{field}.authorized_at"
        ),
    }


def validate_plan_body(value: object, *, field: str = "PlanBody") -> dict:
    """Full closed-shape validation of a PlanBody (C-17 §5.2).

    Returns the validated body (identical structure, typed-checked). The
    caller computes/compares plan_digest over ``canonical_bytes(body)``.
    """
    keys = {
        "format", "plan_id", "scan_id", "source_id", "kind", "project_ids",
        "scope", "base_sources", "authorizations", "missing", "bases",
        "target", "reference_set_digest", "diff", "totals", "decisions",
        "confirmation",
    }
    payload = require_fields(value, {key: None for key in keys}, context=field)
    body = {
        "format": valid_enum(
            payload["format"], ("source-sync-plan/1",), field=f"{field}.format"
        ),
        "plan_id": valid_id(payload["plan_id"], field=f"{field}.plan_id"),
        "scan_id": valid_id(payload["scan_id"], field=f"{field}.scan_id"),
        "source_id": valid_id(payload["source_id"], field=f"{field}.source_id"),
        "kind": valid_enum(payload["kind"], KINDS, field=f"{field}.kind"),
        "project_ids": valid_project_ids(
            payload["project_ids"], field=f"{field}.project_ids"
        ),
        "scope": valid_enum(payload["scope"], SCOPES, field=f"{field}.scope"),
        "base_sources": [],
        "authorizations": [],
        "missing": [],
        "bases": [],
        "target": validate_source_observation(
            payload["target"], field=f"{field}.target"
        ),
        "reference_set_digest": valid_hex64(
            payload["reference_set_digest"],
            field=f"{field}.reference_set_digest",
        ),
        "diff": [],
        "totals": validate_totals(payload["totals"], field=f"{field}.totals"),
        "decisions": [],
        "confirmation": validate_confirmation(
            payload["confirmation"], field=f"{field}.confirmation"
        ),
    }
    base_sources = payload["base_sources"]
    if not isinstance(base_sources, list) or not base_sources:
        raise _invalid(f"{field}.base_sources must be a non-empty array")
    body["base_sources"] = [
        validate_source_base(item, field=f"{field}.base_sources[{i}]")
        for i, item in enumerate(base_sources)
    ]
    authorizations = payload["authorizations"]
    if not isinstance(authorizations, list):
        raise _invalid(f"{field}.authorizations must be an array")
    body["authorizations"] = [
        validate_authorization_base(
            item, field=f"{field}.authorizations[{i}]"
        )
        for i, item in enumerate(authorizations)
    ]
    missing = payload["missing"]
    if not isinstance(missing, list):
        raise _invalid(f"{field}.missing must be an array")
    body["missing"] = [
        validate_missing_observation(item, field=f"{field}.missing[{i}]")
        for i, item in enumerate(missing)
    ]
    if [item["source_id"] for item in body["missing"]] != sorted(
        item["source_id"] for item in body["missing"]
    ) or len({item["source_id"] for item in body["missing"]}) != len(
        body["missing"]
    ):
        raise _invalid(f"{field}.missing must be sorted and unique by source_id")
    bases = payload["bases"]
    if not isinstance(bases, list):
        raise _invalid(f"{field}.bases must be an array")
    body["bases"] = [
        validate_page_base(item, field=f"{field}.bases[{i}]")
        for i, item in enumerate(bases)
    ]
    base_order = [(item["project_id"], item["page_id"]) for item in body["bases"]]
    if base_order != sorted(base_order) or len(set(base_order)) != len(base_order):
        raise _invalid(f"{field}.bases must be sorted and unique by (project,page)")
    diff = payload["diff"]
    if not isinstance(diff, list):
        raise _invalid(f"{field}.diff must be an array")
    body["diff"] = [
        validate_diff_item(item, field=f"{field}.diff[{i}]")
        for i, item in enumerate(diff)
    ]
    diff_ids = [item["item_id"] for item in body["diff"]]
    if diff_ids != sorted(diff_ids) or len(set(diff_ids)) != len(diff_ids):
        raise _invalid(f"{field}.diff must be sorted and unique by item_id")
    decisions = payload["decisions"]
    if not isinstance(decisions, list):
        raise _invalid(f"{field}.decisions must be an array")
    body["decisions"] = [
        validate_decision(item, field=f"{field}.decisions[{i}]")
        for i, item in enumerate(decisions)
    ]
    decision_ids = [item["item_id"] for item in body["decisions"]]
    if decision_ids != sorted(decision_ids) or len(set(decision_ids)) != len(
        decision_ids
    ):
        raise _invalid(
            f"{field}.decisions must be sorted and unique by item_id"
        )
    if decision_ids != diff_ids:
        raise _invalid(f"{field}.decisions must map 1:1 onto diff")
    _validate_plan_cross_rules(body, field=field)
    return body


def _validate_plan_cross_rules(body: dict, *, field: str) -> None:
    """C-17 §5.3 combinational guards that only need the body itself."""
    totals = body["totals"]
    counts = {"unchanged": 0, "added": 0, "missing": 0, "changed": 0, "ambiguous": 0}
    for item in body["diff"]:
        counts[item["classification"]] += 1
    if counts != totals:
        raise _invalid(f"{field}.totals must equal the diff classification counts")
    scope = body["scope"]
    if scope == "current" and len(body["project_ids"]) != 1:
        raise _invalid(f"{field}: scope=current needs exactly one project")
    confirmation = body["confirmation"]
    if (
        confirmation["kind"] != body["kind"]
        or confirmation["project_ids"] != body["project_ids"]
        or confirmation["reference_set_digest"] != body["reference_set_digest"]
    ):
        raise _invalid(f"{field}: confirmation must match kind/scope/reference set")
    if body["kind"] == "repoint" and any(
        item["classification"] in ("changed",) for item in body["diff"]
    ) and not confirmation["resync_content"]:
        raise _invalid(f"{field}: repoint with changed content needs resync_content")
    by_item = {item["item_id"]: item for item in body["diff"]}
    for decision in body["decisions"]:
        diff_item = by_item[decision["item_id"]]
        classification = diff_item["classification"]
        action = decision["action"]
        if classification == "ambiguous" and action in ("keep", "add"):
            raise _invalid(
                f"{field}: ambiguous items cannot be auto keep/add"
            )
        if classification != "ambiguous" and action == "defer":
            raise _invalid(f"{field}: only ambiguous items may defer")
        if classification in ("missing",) and action not in ("tombstone", "defer"):
            raise _invalid(f"{field}: missing items may only tombstone or defer")
        if classification == "added" and action != "add":
            raise _invalid(f"{field}: added items must add")
        if classification == "unchanged" and action not in ("keep", "bind"):
            raise _invalid(f"{field}: unchanged items keep or bind")
        if action in ("keep", "bind", "tombstone") and decision["target_page_id"] \
                != diff_item["page_id"]:
            raise _invalid(f"{field}: decision target must match the diff page")
        if decision["migrate_revision_ids"] and classification not in (
            "changed", "ambiguous"
        ):
            raise _invalid(
                f"{field}: migrate_revision_ids only on changed/ambiguous bind"
            )


def validate_apply_request(value: object, *, field: str = "ApplyRequest") -> dict:
    payload = require_fields(
        value,
        {
            "operation_id", "plan_id", "plan_digest", "grant_ids",
            "authorization",
        },
        context=field,
    )
    return {
        "operation_id": valid_id(
            payload["operation_id"], field=f"{field}.operation_id"
        ),
        "plan_id": valid_id(payload["plan_id"], field=f"{field}.plan_id"),
        "plan_digest": valid_hex64(
            payload["plan_digest"], field=f"{field}.plan_digest"
        ),
        "grant_ids": valid_string_array(
            payload["grant_ids"], field=f"{field}.grant_ids", unique=True
        ),
        "authorization": validate_host_authorization(
            payload["authorization"], field=f"{field}.authorization"
        ),
    }


def validate_completion_request(
    value: object, *, field: str = "CompletionRequest"
) -> dict:
    payload = require_fields(
        value,
        {
            "operation_id", "request_digest", "commit_digest",
            "host_receipt_id", "authorization", "grant_ids",
        },
        context=field,
    )
    return {
        "operation_id": valid_id(
            payload["operation_id"], field=f"{field}.operation_id"
        ),
        "request_digest": valid_hex64(
            payload["request_digest"], field=f"{field}.request_digest"
        ),
        "commit_digest": valid_hex64(
            payload["commit_digest"], field=f"{field}.commit_digest"
        ),
        "host_receipt_id": valid_opaque(
            payload["host_receipt_id"], field=f"{field}.host_receipt_id"
        ),
        "authorization": validate_host_authorization(
            payload["authorization"], field=f"{field}.authorization"
        ),
        "grant_ids": valid_string_array(
            payload["grant_ids"], field=f"{field}.grant_ids", unique=True
        ),
    }


def now_millis() -> str:
    """RFC3339 UTC millisecond timestamp (the T format, Z suffix)."""
    from datetime import datetime, timezone

    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def ttl_seconds(timestamp: str) -> float:
    """Seconds from now until a T timestamp (negative when already past)."""
    from datetime import datetime, timezone

    moment = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
        tzinfo=timezone.utc
    )
    now = datetime.now(timezone.utc)
    return (moment - now).total_seconds()


def is_finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )
