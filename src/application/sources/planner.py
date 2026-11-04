"""FEA-11 plan lifecycle (C-17 §3.1 plan state machine).

draft → previewed → confirmed → applied, plus the explicit stale transition.
The body/digest are immutable after creation; any decision change needs a
new plan_id. Stale apply writes nothing at all — callers get
SOURCE_PLAN_STALE and must issue an explicit Invalidate for an auditable
stale marker.
"""

from __future__ import annotations

import json
import time

from application.sources.errors import SourceSyncError, stale
from application.sources.model import (
    STALE_REASONS,
    canonical_bytes,
    now_millis,
    plan_digest_of,
    ttl_seconds,
    validate_confirmation,
    validate_plan_body,
    valid_enum,
    valid_hex64,
    valid_id,
)

PLAN_TTL_SECONDS = 300.0


def _invalid(message: str) -> SourceSyncError:
    return SourceSyncError("INVALID_REQUEST", message)


class SourceSyncPlanner:
    """PlanSourceSync / preview / confirm / invalidate application face."""

    def __init__(self, *, store, scanner, clock=time.time) -> None:
        self._store = store
        self._scanner = scanner
        self._clock = clock

    # ------------------------------------------------------------- create
    def create(self, payload: dict) -> dict:
        body = validate_plan_body(payload)
        scan = self._scanner.take_live_scan(body["scan_id"])
        self._assert_matches_scan(body, scan.result)
        digest = plan_digest_of(body)

        existing = self._store.get_plan(body["plan_id"])
        if existing is not None:
            if existing["plan_digest"] != digest:
                raise SourceSyncError(
                    "SOURCE_OPERATION_CONFLICT",
                    "plan id is already bound to a different body",
                )
            return self.plan_dto(existing)

        now = self._clock()
        from datetime import datetime, timezone

        expires = min(
            datetime.fromtimestamp(now + PLAN_TTL_SECONDS, tz=timezone.utc),
            datetime.strptime(scan.result["expires_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
            .replace(tzinfo=timezone.utc),
        ).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        self._store.insert_plan(
            plan_id=body["plan_id"],
            source_id=body["source_id"],
            kind=body["kind"],
            plan_digest=digest,
            body_json=canonical_bytes(body).decode("utf-8"),
            created_at=now_millis(),
            expires_at=expires,
        )
        return self.plan_dto(self._store.get_plan(body["plan_id"]), body=body)

    # ------------------------------------------------------------ preview
    def preview(self, payload: dict) -> dict:
        plan_id = valid_id(payload.get("plan_id"), field="plan_id")
        plan_digest = valid_hex64(payload.get("plan_digest"), field="plan_digest")
        if set(payload) != {"plan_id", "plan_digest"}:
            raise _invalid("preview request fields do not match")
        row = self._require_plan(plan_id, plan_digest)
        if row["state"] == "draft":
            self._store.mark_previewed(plan_id, now_millis())
            row = self._store.get_plan(plan_id)
        elif row["state"] not in ("previewed", "confirmed", "applied"):
            raise stale(row.get("stale_reason") or "cancelled")
        return self.plan_dto(row)

    # ------------------------------------------------------------ confirm
    def confirm(self, payload: dict) -> dict:
        if set(payload) != {"plan_id", "plan_digest", "confirmation"}:
            raise _invalid("confirm request fields do not match")
        plan_id = valid_id(payload["plan_id"], field="plan_id")
        plan_digest = valid_hex64(payload["plan_digest"], field="plan_digest")
        confirmation = validate_confirmation(payload["confirmation"])
        row = self._require_plan(plan_id, plan_digest)
        body = json.loads(row["body_json"])
        if confirmation != body["confirmation"]:
            raise SourceSyncError(
                "SOURCE_SYNC_STATE_CONFLICT",
                "confirmation differs from the plan body",
            )
        self._assert_all_ambiguities_decided(body)
        if row["state"] == "draft":
            raise SourceSyncError(
                "SOURCE_SYNC_STATE_CONFLICT",
                "a draft plan must be previewed before confirmation",
            )
        if row["state"] == "previewed":
            self._store.mark_confirmed(plan_id, now_millis())
            row = self._store.get_plan(plan_id)
        elif row["state"] not in ("confirmed", "applied"):
            raise stale(row.get("stale_reason") or "cancelled")
        return self.plan_dto(row)

    # ---------------------------------------------------------- invalidate
    def invalidate(self, payload: dict) -> dict:
        if set(payload) != {"plan_id", "plan_digest", "reason"}:
            raise _invalid("invalidate request fields do not match")
        plan_id = valid_id(payload["plan_id"], field="plan_id")
        plan_digest = valid_hex64(payload["plan_digest"], field="plan_digest")
        reason = valid_enum(payload["reason"], STALE_REASONS, field="reason")
        row = self._require_plan(plan_id, plan_digest)
        operation = self._store.find_operation_by_plan(plan_id)
        if operation is not None and operation["state"] in (
            "core-committed", "acknowledged", "recovered"
        ):
            raise SourceSyncError(
                "SOURCE_SYNC_STATE_CONFLICT",
                "a committed plan cannot be invalidated",
            )
        self._store.mark_stale(plan_id, reason, now_millis())
        return self.plan_dto(self._store.get_plan(plan_id))

    # -------------------------------------------------------------- take
    def take_confirmed(self, plan_id: str) -> dict:
        """Load the confirmed plan inside the apply transaction."""
        row = self._store.get_plan(plan_id)
        if row is None:
            raise stale("cancelled", "source sync plan was not found")
        if row["state"] == "stale":
            raise stale(row["stale_reason"] or "cancelled")
        if row["state"] == "applied":
            raise stale("applied", "source sync plan was already applied")
        if row["state"] != "confirmed":
            raise SourceSyncError(
                "SOURCE_SYNC_STATE_CONFLICT",
                "only a confirmed plan can be applied",
            )
        if ttl_seconds(row["expires_at"]) <= 0:
            raise stale("expired")
        return row

    # -------------------------------------------------------------- dto
    def plan_dto(self, row: dict, *, body: dict | None = None) -> dict:
        parsed = body or json.loads(row["body_json"])
        return {
            "body": parsed,
            "plan_digest": row["plan_digest"],
            "state": row["state"],
            "created_at": row["created_at"],
            "expires_at": row["expires_at"],
            "previewed_at": row["previewed_at"],
            "confirmed_at": row["confirmed_at"],
            "applied_at": row["applied_at"],
            "stale_reason": row["stale_reason"],
        }

    # ----------------------------------------------------------- helpers
    def _require_plan(self, plan_id: str, plan_digest: str) -> dict:
        row = self._store.get_plan(plan_id)
        if row is None:
            raise SourceSyncError(
                "SOURCE_OPERATION_NOT_FOUND",
                "source sync plan was not found",
            )
        if row["plan_digest"] != plan_digest:
            raise stale("decision", "plan digest does not match")
        return row

    def _assert_matches_scan(self, body: dict, scan: dict) -> None:
        """The plan body must equal the live scan observation (C-17 §5.1:
        body.scan_id live and consistent with the body)."""
        comparable = (
            "source", "base_sources", "authorizations", "missing", "bases",
            "reference_set_digest", "diff", "totals",
        )
        for key in comparable:
            if canonical_bytes(body[key]) != canonical_bytes(scan[key]):
                raise _invalid(f"plan body {key} does not match the live scan")

    @staticmethod
    def _assert_all_ambiguities_decided(body: dict) -> None:
        classifications = {
            item["item_id"]: item["classification"] for item in body["diff"]
        }
        for decision in body["decisions"]:
            if classifications[decision["item_id"]] == "ambiguous":
                if decision["action"] not in ("bind", "defer"):
                    raise SourceSyncError(
                        "SOURCE_SYNC_STATE_CONFLICT",
                        "every ambiguous item needs an explicit bind/defer",
                    )
