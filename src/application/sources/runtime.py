"""FEA-11 durable operation face (C-17 §3.2/§3.3).

GetSourceOperation / CancelSourceOperation / AcknowledgeSourceOperation /
CompleteSourceOperationRecovery / RecordSourceOperationFailure. The Core
``source_operations`` table is the business receipt authority; every state
moved here is durable across restarts. The ACK path re-verifies the fresh
authorization (same registry, same physical identity, generation ≥ the
committed baseline) and opens every gate of the operation in one
transaction — no partial opens, no replayed destructive OS operations.
"""

from __future__ import annotations

import json
import threading
import time

from application.importing.referenced.errors import SourceImportError
from application.sources.errors import SOURCE_SYNC_ERROR_RULES, SourceSyncError
from application.sources.model import (
    authorization_digest_of,
    identity_digest_of,
    now_millis,
    request_digest_of,
    validate_completion_request,
    valid_enum,
    valid_hex64,
    valid_id,
    valid_string_array,
)

#: C-17 §8: RecordSourceOperationFailure only accepts the closed code set.
FAILURE_CODES = frozenset(SOURCE_SYNC_ERROR_RULES)


def _invalid(message: str) -> SourceSyncError:
    return SourceSyncError("INVALID_REQUEST", message)


class SourceSyncOperations:
    """Durable operation queries and the ACK/recovery transitions."""

    def __init__(self, *, store, access, clock=time.time) -> None:
        self._store = store
        self._access = access
        self._clock = clock
        self._lock = threading.RLock()

    # ------------------------------------------------------------- query
    def get(self, payload: dict) -> dict:
        if not isinstance(payload, dict) or set(payload) != {"operation_id"}:
            raise _invalid("operation query fields do not match")
        operation_id = valid_id(payload["operation_id"], field="operation_id")
        return self.operation_dto(self._require(operation_id))

    def operation_dto(self, row: dict) -> dict:
        receipt = json.loads(row["commit_receipt_json"]) if row[
            "commit_receipt_json"
        ] else None
        return {
            "operation_id": row["operation_id"],
            "plan_id": row["plan_id"],
            "plan_digest": row["plan_digest"],
            "request_digest": row["request_digest"],
            "kind": row["kind"],
            "origin": "core",
            "state": row["state"],
            "commit": receipt,
            "commit_digest": row["commit_digest"],
            "error_code": row["error_code"],
            "retryable": bool(row["retryable"]),
            "acknowledged_at": row["acknowledged_at"],
        }

    # ------------------------------------------------------------- cancel
    def cancel(self, payload: dict) -> dict:
        if not isinstance(payload, dict) or set(payload) != {
            "operation_id", "request_digest",
        }:
            raise _invalid("cancel request fields do not match")
        operation_id = valid_id(payload["operation_id"], field="operation_id")
        request_digest = valid_hex64(
            payload["request_digest"], field="request_digest"
        )
        row = self._store.find_operation(operation_id)
        if row is None:
            # Nothing committed in the Core: the cancel intent lives in the
            # Host journal (C-17 §5.1); the Core stays at zero writes.
            return {
                "operation_id": operation_id,
                "accepted": True,
                "state": "failed",
            }
        if row["request_digest"] != request_digest:
            raise SourceSyncError(
                "SOURCE_OPERATION_CONFLICT",
                "operation id is bound to a different request",
            )
        if row["state"] in ("core-committed", "acknowledged", "recovered"):
            return {
                "operation_id": operation_id,
                "accepted": False,
                "state": row["state"],
            }
        # started/host-authorized without a Core commit: the business
        # transaction never happened (single transaction semantics), so the
        # Core records the pre-commit cancellation explicitly.
        if row["state"] == "failed":
            return {
                "operation_id": operation_id,
                "accepted": True,
                "state": "failed",
            }
        with self._lock:
            conn = self._store._conn  # noqa: SLF001 - store owns the conn
            conn.execute("BEGIN IMMEDIATE")
            try:
                self._store.fail_operation(
                    operation_id,
                    code="SOURCE_SYNC_CANCELLED",
                    retryable=False,
                    now=now_millis(),
                )
                conn.commit()
            except BaseException:
                conn.rollback()
                raise
        return {"operation_id": operation_id, "accepted": True, "state": "failed"}

    # ---------------------------------------------------------------- ack
    def acknowledge(self, payload: dict) -> dict:
        request = validate_completion_request(payload)
        return self._complete(request, recovered=False)

    def recover(self, payload: dict) -> dict:
        request = validate_completion_request(payload)
        return self._complete(request, recovered=True)

    def _complete(self, request: dict, *, recovered: bool) -> dict:
        operation_id = request["operation_id"]
        row = self._require(operation_id)
        if row["request_digest"] != request["request_digest"]:
            raise SourceSyncError(
                "SOURCE_OPERATION_CONFLICT",
                "operation id is bound to a different request",
            )
        if row["commit_digest"] != request["commit_digest"]:
            raise _invalid("commit digest does not match the durable receipt")
        if row["state"] in ("acknowledged", "recovered"):
            # Idempotent replay: return the original receipt; the fresh grant
            # check still runs (revocation affects every later read).
            self._verify_fresh(request, row)
            return self.operation_dto(self._store.find_operation(operation_id))
        if row["state"] == "failed" and not recovered:
            raise SourceSyncError(
                "SOURCE_SYNC_STATE_CONFLICT",
                "a failed operation needs recovery, not acknowledgement",
            )
        if row["state"] not in ("core-committed", "failed"):
            raise SourceSyncError(
                "SOURCE_SYNC_STATE_CONFLICT",
                "operation has no committed receipt to complete",
            )
        self._verify_fresh(request, row)
        with self._lock:
            conn = self._store._conn  # noqa: SLF001 - store owns the conn
            conn.execute("BEGIN IMMEDIATE")
            try:
                now = now_millis()
                opened = self._store.open_gates(operation_id, now)
                if recovered:
                    self._store.recover_operation(operation_id, now)
                else:
                    self._store.acknowledge_operation(operation_id, now)
                conn.commit()
            except BaseException:
                conn.rollback()
                raise
            del opened
        return self.operation_dto(self._store.find_operation(operation_id))

    def _verify_fresh(self, request: dict, row: dict) -> None:
        """ACK/recovery authorization re-verification (C-17 §3.2): same
        registry, same physical identity, not revoked; a fresh generation is
        allowed to be ≥ the committed baseline (C-15 read compatibility)."""
        authorization = request["authorization"]
        if authorization["operation_id"] != row["operation_id"]:
            raise _invalid("authorization operation id mismatch")
        recomputed = authorization_digest_of(authorization["authorizations"])
        if recomputed != authorization["authorization_digest"]:
            raise SourceSyncError(
                "REF_SIGNATURE_INVALID",
                "authorization digest does not match the authorization base",
            )
        committed = json.loads(row["authorization_json"])
        committed_base = {
            item["registry_id"]: item
            for item in committed["authorizations"]
        }
        for item in authorization["authorizations"]:
            baseline = committed_base.get(item["registry_id"])
            if baseline is None:
                raise _invalid("authorization registry is not part of the commit")
            if item["identity_digest"] != baseline["identity_digest"]:
                raise _invalid("authorization identity changed since the commit")
            if item["generation"] < baseline["generation"]:
                raise SourceSyncError(
                    "SOURCE_GRANT_REVOKED",
                    "authorization generation is below the committed baseline",
                )
        if not request["grant_ids"]:
            # Missing-source operations carry no read grants; their receipts
            # only ever open gates, never publish new content.
            if committed["authorizations"]:
                return
            return
        for grant_id in request["grant_ids"]:
            try:
                grant = self._access.resolve(grant_id)
            except SourceImportError as error:
                raise SourceSyncError(error.code, str(error)) from error
            facts = (
                grant.container_facts
                if grant.container_facts is not None
                else (
                    grant.folder_entries[0][1]
                    if grant.folder_entries
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
            matching = {
                item["registry_id"]: item
                for item in authorization["authorizations"]
            }.get(grant.registry_id)
            if (
                matching is None
                or identity != matching["identity_digest"]
                or int(grant.generation) < matching["generation"]
            ):
                raise SourceSyncError(
                    "SOURCE_ACCESS_DENIED",
                    "live grant does not cover the fresh authorization",
                )

    # ------------------------------------------------------------ failure
    def record_failure(self, payload: dict) -> dict:
        if not isinstance(payload, dict) or set(payload) != {
            "operation_id", "request_digest", "code",
        }:
            raise _invalid("failure record fields do not match")
        operation_id = valid_id(payload["operation_id"], field="operation_id")
        request_digest = valid_hex64(
            payload["request_digest"], field="request_digest"
        )
        code = valid_str_code(payload["code"])
        row = self._require(operation_id)
        if row["request_digest"] != request_digest:
            raise SourceSyncError(
                "SOURCE_OPERATION_CONFLICT",
                "operation id is bound to a different request",
            )
        if row["state"] in ("acknowledged", "recovered"):
            raise SourceSyncError(
                "SOURCE_SYNC_STATE_CONFLICT",
                "a completed operation cannot record a failure",
            )
        if row["state"] != "core-committed":
            raise SourceSyncError(
                "SOURCE_SYNC_STATE_CONFLICT",
                "only a committed operation records failures",
            )
        retryable = SOURCE_SYNC_ERROR_RULES.get(code, ("internal", True))[1]
        with self._lock:
            conn = self._store._conn  # noqa: SLF001 - store owns the conn
            conn.execute("BEGIN IMMEDIATE")
            try:
                self._store.fail_operation(
                    operation_id, code=code, retryable=retryable,
                    now=now_millis(),
                )
                conn.commit()
            except BaseException:
                conn.rollback()
                raise
        return self.operation_dto(self._store.find_operation(operation_id))

    # ------------------------------------------------------------ helpers
    def _require(self, operation_id: str) -> dict:
        row = self._store.find_operation(operation_id)
        if row is None:
            raise SourceSyncError(
                "SOURCE_OPERATION_NOT_FOUND",
                "source operation was not found",
            )
        return row


def valid_str_code(value: object) -> str:
    if not isinstance(value, str) or value not in FAILURE_CODES:
        raise _invalid("failure code is not in the closed set")
    return value
