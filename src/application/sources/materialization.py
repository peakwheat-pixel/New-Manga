"""C-17 v1.2: read-only plan materialization projection (FEA-11-HOST-AUTH-3).

Why this exists: after the Host+Core process tree dies, the fresh Core has no
source-read grants, and the Host must re-mint a fresh grant to ACK the already
committed operation. The only durable authority for the plan's source version
and entries is the Core's own ``source_sync_plans.body_json`` (the Host-side
identity cache is memory-only). This command returns exactly that subset back
to the Host.

Invariants fixed by the contract (§5.1/§5.3/§8):

* closed shape request ``{"plan_id","plan_digest"}`` -- unknown keys are
  ``INVALID_REQUEST``;
* single SELECT-level projection: **zero writes**, no scan/plan/operation/
  receipt/grant/journal rows;
* known plan with a different digest -> ``SOURCE_PLAN_STALE``;
* unknown plan -> ``SOURCE_PLAN_NOT_FOUND``; unreadable body ->
  ``SOURCE_PLAN_UNAVAILABLE``; over budget -> ``SOURCE_BUDGET_EXCEEDED``;
* ``target.status == "missing"`` -> ``version_id``/``content_digest`` null and
  ``entries`` empty (never fabricated);
* the projection is NOT an authorization: the caller still re-mints a fresh
  grant through the existing C-16 validation path.
"""

from __future__ import annotations

import json

from application.sources.errors import SourceSyncError

FORMAT = "source-sync-plan-materialization/1"
_ALLOWED_KEYS = frozenset({"plan_id", "plan_digest"})
_BUDGET_BYTES = 8 * 1024 * 1024
_MAX_ENTRIES = 10000
_HEX = frozenset("0123456789abcdef")


def _parse(payload: object) -> tuple[str, str]:
    if not isinstance(payload, dict) or set(payload) != _ALLOWED_KEYS:
        raise SourceSyncError(
            "INVALID_REQUEST", "materialization request is invalid"
        )
    plan_id = payload.get("plan_id")
    plan_digest = payload.get("plan_digest")
    if not isinstance(plan_id, str) or not plan_id:
        raise SourceSyncError("INVALID_REQUEST", "plan_id must be a non-empty string")
    if (
        not isinstance(plan_digest, str)
        or len(plan_digest) != 64
        or not set(plan_digest).issubset(_HEX)
    ):
        raise SourceSyncError("INVALID_REQUEST", "plan_digest must be 64 hex chars")
    return plan_id, plan_digest


def _entries_of(target: dict) -> list[dict]:
    raw = target.get("entries")
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise SourceSyncError("SOURCE_PLAN_UNAVAILABLE", "plan entries are unreadable")
    if len(raw) > _MAX_ENTRIES:
        raise SourceSyncError("SOURCE_BUDGET_EXCEEDED", "plan entries exceed the budget")
    projected = []
    for entry in raw:
        if not isinstance(entry, dict):
            raise SourceSyncError(
                "SOURCE_PLAN_UNAVAILABLE", "plan entry is unreadable"
            )
        projected.append(
            {
                "entry_id": entry.get("entry_id"),
                "locator": entry.get("locator"),
                "ordinal": entry.get("ordinal"),
                "content_digest_kind": entry.get("content_digest_kind"),
                "content_digest": entry.get("content_digest"),
            }
        )
    projected.sort(key=lambda item: item.get("ordinal") if item.get("ordinal") is not None else 0)
    ordinals = [item.get("ordinal") for item in projected]
    if len(set(ordinals)) != len(ordinals):
        raise SourceSyncError(
            "SOURCE_PLAN_UNAVAILABLE", "plan entry ordinals are duplicated"
        )
    return projected


def materialize(store, payload: object) -> dict:
    """Project one persisted plan row for Host recovery re-minting."""
    plan_id, plan_digest = _parse(payload)
    row = store.get_plan(plan_id)
    if row is None:
        raise SourceSyncError("SOURCE_PLAN_NOT_FOUND", "plan is not found")
    if str(row.get("plan_digest") or "") != plan_digest:
        raise SourceSyncError(
            "SOURCE_PLAN_STALE", "plan digest no longer matches"
        )
    body_raw = row.get("body_json")
    try:
        body = json.loads(body_raw) if isinstance(body_raw, str) else None
    except (TypeError, ValueError):
        body = None
    if not isinstance(body, dict):
        raise SourceSyncError("SOURCE_PLAN_UNAVAILABLE", "plan body is unreadable")
    target = body.get("target")
    if not isinstance(target, dict):
        raise SourceSyncError("SOURCE_PLAN_UNAVAILABLE", "plan target is unreadable")
    status = target.get("status")
    if status not in {"ok", "missing", "encrypted", "unsupported"}:
        raise SourceSyncError("SOURCE_PLAN_UNAVAILABLE", "plan target status is invalid")
    missing = status == "missing"
    entries = [] if missing else _entries_of(target)
    version_id = None if missing else target.get("version_id")
    content_digest = None if missing else target.get("content_digest")
    if not missing and not isinstance(version_id, str):
        raise SourceSyncError(
            "SOURCE_PLAN_UNAVAILABLE", "plan target version is unreadable"
        )
    result = {
        "format": FORMAT,
        "plan_id": plan_id,
        "plan_digest": plan_digest,
        "kind": body.get("kind"),
        "source_id": body.get("source_id"),
        "version_id": version_id,
        "content_digest": content_digest,
        "entries": entries,
        "reference_set_digest": body.get("reference_set_digest"),
        "state": row.get("state"),
        "expires_at": row.get("expires_at"),
    }
    encoded = json.dumps(result, ensure_ascii=False).encode("utf-8")
    if len(encoded) > _BUDGET_BYTES:
        raise SourceSyncError(
            "SOURCE_BUDGET_EXCEEDED", "plan materialization exceeds the budget"
        )
    return result
