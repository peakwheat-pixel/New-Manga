"""FEA-11 apply/relink/repoint/resync (C-17 §6 single atomic unit).

One plan = one SQLite business transaction: re-read every CAS guard →
source rows/new version + entries → old bindings superseded + new bindings →
pages/tombstones/manual revision migration + lineage → operation receipt +
pending publications → plan applied → COMMIT. A failure of the last item
rolls the whole batch back with zero published generations. Host durable
authorization is verified BEFORE dispatch reaches this face (the wire layer
only exposes apply through the host-control channel).
"""

from __future__ import annotations

import json
import threading
import time
import uuid

from application.importing.referenced.errors import SourceImportError
from application.sources.errors import SourceSyncError, stale
from application.sources.model import (
    authorization_digest_of,
    canonical_bytes,
    digest_of,
    identity_digest_of,
    now_millis,
    request_digest_of,
    validate_apply_request,
)

#: Command → allowed plan kind (C-17 §5.1: RelinkSource only relink etc.).
COMMAND_KIND_GATE = {
    "ApplySourceSyncPlan": "resync",
    "RelinkSource": "relink",
    "RepointSource": "repoint",
    "ResyncSource": "resync",
}


def _invalid(message: str) -> SourceSyncError:
    return SourceSyncError("INVALID_REQUEST", message)


class SourceSyncService:
    """The single-writer apply face; one serialized business transaction."""

    def __init__(
        self,
        *,
        store,
        scanner,
        planner,
        access,
        repository,
        pdf_open=None,
        clock=time.time,
    ) -> None:
        self._store = store
        self._scanner = scanner
        self._planner = planner
        self._access = access
        self._repository = repository
        self._pdf_open = pdf_open
        self._clock = clock
        self._write_lock = threading.RLock()

    # ---------------------------------------------------------------- api
    def apply(self, command: str, payload: dict) -> dict:
        expected_kind = COMMAND_KIND_GATE.get(command)
        if expected_kind is None:
            raise _invalid("unknown source sync apply command")
        request = validate_apply_request(payload)
        kind = self._require_plan_kind(request)
        if kind != expected_kind:
            raise SourceSyncError(
                "SOURCE_SYNC_STATE_CONFLICT",
                "operation kind does not match the command",
            )
        operation_id = request["operation_id"]
        authorization = request["authorization"]
        request_digest = request_digest_of(
            operation_id, request["plan_id"], request["plan_digest"], kind
        )
        self._verify_authorization_shape(operation_id, request_digest, authorization)

        with self._write_lock:
            replay = self._replay_or_conflict(operation_id, request_digest)
            if replay is not None:
                return replay
            existing_plan_op = self._store.find_operation_by_plan(
                request["plan_id"]
            )
            if existing_plan_op is not None and existing_plan_op[
                "operation_id"
            ] != operation_id:
                raise SourceSyncError(
                    "SOURCE_OPERATION_CONFLICT",
                    "plan already has another operation",
                )
            return self._apply_transaction(
                request, kind, request_digest, authorization
            )

    # ----------------------------------------------------------- helpers
    def _require_plan_kind(self, request: dict) -> str:
        row = self._store.get_plan(request["plan_id"])
        if row is None:
            raise stale("cancelled", "source sync plan was not found")
        if row["plan_digest"] != request["plan_digest"]:
            raise stale("decision", "plan digest does not match")
        return row["kind"]

    @staticmethod
    def _verify_authorization_shape(
        operation_id: str, request_digest: str, authorization: dict
    ) -> None:
        if authorization["operation_id"] != operation_id:
            raise _invalid("authorization operation id mismatch")
        if authorization["request_digest"] != request_digest:
            raise _invalid("authorization request digest mismatch")
        recomputed = authorization_digest_of(authorization["authorizations"])
        if recomputed != authorization["authorization_digest"]:
            raise SourceSyncError(
                "REF_SIGNATURE_INVALID",
                "authorization digest does not match the authorization base",
            )

    def _replay_or_conflict(
        self, operation_id: str, request_digest: str
    ) -> dict | None:
        """Same id + same request digest returns the original outcome; a
        different digest is a hard conflict (C-17 §1)."""
        existing = self._store.find_operation(operation_id)
        if existing is None:
            return None
        if existing["request_digest"] != request_digest:
            raise SourceSyncError(
                "SOURCE_OPERATION_CONFLICT",
                "operation id is bound to a different request",
            )
        return self._dispatch_dto(existing)

    def _dispatch_dto(self, operation: dict) -> dict:
        return {
            "operation_id": operation["operation_id"],
            "request_digest": operation["request_digest"],
            "accepted": True,
            "state": operation["state"],
        }

    # ---------------------------------------------------- authorization
    def _verify_live_authorization(
        self, request: dict, authorization: dict, body: dict
    ) -> dict:
        """Live-grant verification inside/around the apply transaction.

        Checks every registry's expected generation **equals** the plan
        baseline (C-17 §6.1 row 3), the physical identity matches the
        authorized roots, and returns the grant to lease the container with.
        """
        baseline = {
            item["registry_id"]: item for item in body["authorizations"]
        }
        live = {
            item["registry_id"]: item
            for item in authorization["authorizations"]
        }
        if set(baseline) != set(live):
            raise stale("authorization", "authorization registries changed")
        for registry_id, expected in baseline.items():
            current = live[registry_id]
            if (
                current["generation"] != expected["generation"]
                or current["identity_digest"] != expected["identity_digest"]
            ):
                raise stale("authorization", "authorization baseline drifted")
        primary = None
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
            matching = live.get(grant.registry_id)
            if (
                matching is None
                or int(grant.generation) != matching["generation"]
                or identity != matching["identity_digest"]
            ):
                raise stale(
                    "authorization",
                    "live grant does not match the authorization baseline",
                )
            if primary is None:
                primary = grant
        return {"primary_grant": primary}

    # ------------------------------------------------------------ commit
    def _apply_transaction(
        self, request: dict, kind: str, request_digest: str, authorization: dict
    ) -> dict:
        operation_id = request["operation_id"]
        plan_id = request["plan_id"]
        conn = self._store._conn  # noqa: SLF001 - the store owns the conn

        # Lease + strong container re-verification BEFORE BEGIN IMMEDIATE —
        # source reads/decodes stay outside the DB transaction (C-17 §6.2).
        lease = getattr(self._access, "commit_guard", None)
        guard = (
            lease(request["grant_ids"][0])
            if lease is not None and request["grant_ids"]
            else _null_guard()
        )
        with guard:
            plan_row = self._planner.take_confirmed(plan_id)
            body = json.loads(plan_row["body_json"])
            if plan_row["plan_digest"] != request["plan_digest"]:
                raise stale("decision", "plan digest drifted before apply")
            self._verify_live_authorization(request, authorization, body)
            self._verify_target_lease(request, body)
            conn.execute("BEGIN IMMEDIATE")
            try:
                # Re-read everything inside the transaction (§6.1).
                plan = self._planner.take_confirmed(plan_id)
                body = json.loads(plan["body_json"])
                self._verify_live_authorization(request, authorization, body)
                self._verify_cas(body)
                # The operation row is the FK target of publications/gates and
                # receipt rows; it must exist before the business writes
                # (C-17 §3.2 host-authorized → core-committed inside one txn).
                self._store.insert_operation(
                    operation_id=operation_id,
                    plan_id=plan_id,
                    plan_digest=plan["plan_digest"],
                    kind=kind,
                    request_digest=request_digest,
                    authorization_digest=authorization["authorization_digest"],
                    authorization_json=canonical_bytes(
                        authorization
                    ).decode("utf-8"),
                    host_receipt_id=authorization["host_receipt_id"],
                    now=now_millis(),
                )
                receipt = self._execute_decisions(
                    body, request, authorization, operation_id, kind
                )
                now = receipt["committed_at"]
                commit_digest = digest_of(receipt)
                self._store.commit_operation(
                    operation_id,
                    commit_receipt_json=canonical_bytes(receipt).decode(
                        "utf-8"
                    ),
                    commit_digest=commit_digest,
                    now=now,
                )
                self._store.mark_applied(plan_id, now)
                # R-008 (FEA-11 r1): re-verify the live authorization and the
                # lease right before COMMIT — a revocation during the
                # transaction must not publish a new generation (C-17 §6.1).
                self._verify_live_authorization(request, authorization, body)
                conn.commit()
            except BaseException:
                conn.rollback()
                raise
        # C-16 §3.1 / C-17 §7.2: a synced binding must be readable through the
        # operation's grant. bind_imported_entry is the frozen grant→binding
        # map; the sync face is the second producer besides import.
        self._bind_operation_grant(body, request, receipt)
        return {
            "operation_id": operation_id,
            "request_digest": request_digest,
            "accepted": True,
            "state": "core-committed",
        }

    def _bind_operation_grant(
        self, body: dict, request: dict, receipt: dict
    ) -> None:
        """R-003 (FEA-11 r1): every healthy binding the operation produced (or
        kept) must be readable through the operation's grant — including the
        pages an ``add`` decision created (their page ids come from the
        receipt, not from ``target_page_id``)."""
        bind = getattr(self._access, "bind_imported_entry", None)
        grant_id = request["grant_ids"][0] if request["grant_ids"] else None
        if bind is None or grant_id is None:
            return
        for binding in receipt.get("bindings", []):
            if binding["status"] != "healthy":
                continue
            try:
                bind(
                    grant_id,
                    binding["source_id"],
                    binding["version_id"],
                    binding["entry_id"],
                )
            except SourceImportError as error:
                # A kept page keeps the grant it was imported with; the
                # operation grant scopes the target version only. A different
                # version is therefore expected here and stays fail-closed
                # through the kept page's own grant.
                if binding["version_id"] != self._target_version(body):
                    continue
                raise SourceSyncError(error.code, str(error)) from error

    @staticmethod
    def _target_version(body: dict) -> str | None:
        target = body.get("target") or {}
        return target.get("version_id")

    def _verify_target_lease(self, request: dict, body: dict) -> None:
        """Re-scan the container under the lease and prove the target
        observation still holds (mtime/size are never proof of sameness)."""
        target = body["target"]
        if target["status"] == "missing":
            if request["grant_ids"]:
                raise _invalid("a missing source takes no read grants")
            for decision in body["decisions"]:
                if decision["action"] not in ("tombstone", "defer"):
                    raise SourceSyncError(
                        "SOURCE_SYNC_STATE_CONFLICT",
                        "a missing source may only tombstone or defer",
                    )
            return
        if not request["grant_ids"]:
            raise _invalid("a non-missing source requires read grants")
        from application.importing.referenced.scanner import scan_source

        try:
            grant = self._access.resolve(request["grant_ids"][0])
            scanned = scan_source(grant, pdf_open=self._pdf_open)
        except SourceImportError as error:
            raise SourceSyncError(error.code, str(error)) from error
        if scanned.status != "ok":
            raise stale("source", "target container is no longer readable")
        if scanned.container_digest != target["content_digest"]:
            raise stale("source", "target container changed since the plan")

    def _verify_cas(self, body: dict) -> None:
        """Re-read every §6.1 baseline inside the transaction.

        The reference-set digest covers the WHOLE source (every sharing
        project, C-17 §5.3), so the recheck must use the same universe as the
        scan that froze the plan (r2 P1-1 regression: comparing the scoped
        set made every shared-source apply stale)."""
        references = self._store.list_source_references(body["source_id"])
        if self._store.reference_set_digest(references) != body[
            "reference_set_digest"
        ]:
            raise stale(
                "binding", "the frozen reference set changed since the plan"
            )
        for base in body["bases"]:
            row = self._store.current_binding_of_page(base["page_id"])
            if (
                row is None
                or row["binding_id"] != base["binding_id"]
                or int(row["binding_version"]) != base["binding_version"]
                or row["entry_id"] != base["entry_id"]
                or row["accepted_source_version"] != base["version_id"]
                or row["source_id"] != base["source_id"]
            ):
                raise stale("binding", "page binding drifted since the plan")
            # CAS reads the physical page row, not a UI visibility view
            # (C-17 §6.2 baseline: the V(p,t) projection is a read concern).
            page_row = self._store._conn.execute(  # noqa: SLF001
                "SELECT page_id, chapter_id, deleted_at, source_order,"
                " sort_order FROM pages WHERE page_id = ?",
                (base["page_id"],),
            ).fetchone()
            if page_row is None:
                raise stale("binding", "reference page disappeared")
            if page_row["chapter_id"] != base["chapter_id"]:
                raise stale("binding", "page ownership drifted since the plan")
            if (
                int(page_row["source_order"]) != int(base["source_order"])
                or int(page_row["sort_order"]) != int(base["sort_order"])
            ):
                raise stale("binding", "page order drifted since the plan")
            deleted_now = page_row["deleted_at"] is not None
            if deleted_now != base["deleted"]:
                raise stale("binding", "page delete state drifted since the plan")
            regions = self._store.regions_manual_projection(base["page_id"])
            if self._store.manual_digest(regions) != base["manual_digest"]:
                raise stale("manual", "manual region baseline drifted")
            if self._store.protection_digest(regions) != base[
                "protection_digest"
            ]:
                raise stale("manual", "protection baseline drifted")
            if self._store.drafts_digest(
                self._store.drafts_projection([base["page_id"]])
            ) != base["drafts_digest"]:
                raise stale("manual", "draft baseline drifted")
            if self._store.runs_digest(
                self._store.run_projection([base["page_id"]])
            ) != base["runs_digest"]:
                raise stale("manual", "run baseline drifted")
        for base_source in body["base_sources"]:
            version = self._store.get_source_version_row(
                base_source["source_id"], base_source["version_id"]
            )
            if version is None or version["content_digest"] != base_source[
                "content_digest"
            ]:
                raise stale(
                    "source", "source version drifted since the plan"
                )

    # --------------------------------------------------------- execution
    def _execute_decisions(
        self,
        body: dict,
        request: dict,
        authorization: dict,
        operation_id: str,
        kind: str,
    ) -> dict:
        store = self._store
        now = now_millis()
        target = body["target"]
        same_container = (
            body["base_sources"]
            and body["base_sources"][0]["content_digest"]
            == target["content_digest"]
        )
        grant = None
        if request["grant_ids"]:
            try:
                grant = self._access.resolve(request["grant_ids"][0])
            except SourceImportError as error:
                raise SourceSyncError(error.code, str(error)) from error
        generation = (
            int(grant.generation) if grant is not None else authorization[
                "authorizations"
            ][0]["generation"]
        )

        # --- relink guard: same physical file, content unchanged (C-17
        # §5.3: a changed container refuses relink and needs a resync plan).
        if kind == "relink" and not same_container:
            raise SourceSyncError(
                "SOURCE_SYNC_STATE_CONFLICT",
                "relink requires unchanged content; create a resync plan",
            )
        # R-006 (FEA-11 r1): relink means the SAME physical file was renamed or
        # moved. Identical bytes in a new file (a copy) have a new physical
        # identity and must go through repoint/resync.
        if kind == "relink" and grant is not None:
            location = store.get_source_location_current(body["source_id"])
            facts = getattr(grant, "container_facts", None)
            if location is not None and facts is not None:
                from application.importing.referenced.identity import (
                    normalize_identity,
                )

                expected = normalize_identity(
                    location["volume_serial"], location["file_id"]
                )
                observed = normalize_identity(
                    facts.volume_serial,
                    facts.file_id,
                )
                if observed != expected:
                    raise SourceSyncError(
                        "SOURCE_SYNC_STATE_CONFLICT",
                        "relink requires the same physical file; a copy needs "
                        "repoint or resync",
                    )

        # --- new container version (and possibly a new location row).
        new_version_id = None
        if not same_container and target["status"] == "ok":
            new_version_id = self._ensure_target_version(
                body, target, grant, now
            )
        if kind == "relink" and grant is not None:
            location = store.get_source_location_current(body["source_id"])
            if location is not None:
                store._conn.execute(
                    "UPDATE source_locations SET registry_id = ?,"
                    " authorization_generation = ?, last_verified_at = ?"
                    " WHERE location_id = ?",
                    (
                        grant.registry_id, int(grant.generation), now,
                        location["location_id"],
                    ),
                )

        diff_by_item = {item["item_id"]: item for item in body["diff"]}
        entries_by_id: dict[str, dict] = {}
        if new_version_id is not None:
            for entry in store.list_entries_of_version(new_version_id):
                entries_by_id[entry["entry_id"]] = entry
        old_entries_by_id: dict[str, dict] = {}
        for base_source in body["base_sources"]:
            for entry in store.list_entries_of_version(
                base_source["version_id"]
            ):
                old_entries_by_id[entry["entry_id"]] = entry

        bindings: list[dict] = []
        captured_pages: set[str] = set()

        for decision in body["decisions"]:
            item = diff_by_item[decision["item_id"]]
            action = decision["action"]
            if action == "defer":
                continue
            if action == "tombstone":
                binding = store.current_binding_of_page(item["page_id"])
                if binding is None:
                    raise stale("binding", "tombstone page lost its binding")
                store.mark_binding_missing(binding["binding_id"], now)
                bindings.append(
                    {
                        "page_id": item["page_id"],
                        "binding_id": binding["binding_id"],
                        "binding_version": int(binding["binding_version"]),
                        "source_id": binding["source_id"],
                        "version_id": binding["accepted_source_version"],
                        "entry_id": binding["entry_id"],
                        "status": "missing",
                    }
                )
                continue
            if action == "add":
                new_entry = entries_by_id.get(item["new_entry_id"])
                if new_entry is None:
                    raise stale("source", "added entry vanished from target")
                chapter = self._repository.get_chapter(
                    decision["target_chapter_id"]
                )
                if chapter is None:
                    raise _invalid("add decision targets an unknown chapter")
                page_id = uuid.uuid4().hex
                store.insert_page(
                    {
                        "page_id": page_id,
                        "chapter_id": chapter.chapter_id,
                        "source_filename": _basename(new_entry["locator"]),
                        "source_order": decision["new_source_order"],
                        "sort_order": decision["new_sort_order"],
                        "source_hash": new_entry["content_digest"],
                        "source_size_bytes": new_entry["size_bytes"],
                        "width": None,
                        "height": None,
                        "managed_original_ref": None,
                        "page_locked": 0,
                        "review_state": None,
                        "overall_status": None,
                        "created_at": now,
                        "updated_at": now,
                        "deleted_at": None,
                        "source_mode": "referenced",
                        "integrity_status": "complete",
                    }
                )
                binding_id = f"pb-{uuid.uuid4().hex}"
                store.insert_binding(
                    {
                        "binding_id": binding_id,
                        "page_id": page_id,
                        "project_id": chapter.book_id,
                        "binding_version": 1,
                        "source_id": body["source_id"],
                        "entry_id": new_entry["entry_id"],
                        "accepted_source_version": new_version_id,
                        "status": "healthy",
                        "previous_binding_id": None,
                        "authorization_generation": generation,
                        "authorized_at": now,
                        "verified_digest": new_entry["content_digest"],
                        "created_at": now,
                        "updated_at": now,
                    }
                )
                store.insert_publication(
                    binding_id=binding_id,
                    operation_id=operation_id,
                    previous_binding_id=None,
                    relation="added",
                )
                bindings.append(
                    {
                        "page_id": page_id,
                        "binding_id": binding_id,
                        "binding_version": 1,
                        "source_id": body["source_id"],
                        "version_id": new_version_id,
                        "entry_id": new_entry["entry_id"],
                        "status": "healthy",
                    }
                )
                continue
            # keep / bind: publish a new binding generation on the same page.
            page_id = decision["target_page_id"] or item["page_id"]
            old_binding = store.current_binding_of_page(page_id)
            if old_binding is None:
                raise stale("binding", "kept page lost its binding")
            if same_container and action in ("keep", "bind"):
                bindings.append(
                    {
                        "page_id": page_id,
                        "binding_id": old_binding["binding_id"],
                        "binding_version": int(old_binding["binding_version"]),
                        "source_id": old_binding["source_id"],
                        "version_id": old_binding["accepted_source_version"],
                        "entry_id": old_binding["entry_id"],
                        "status": old_binding["status"],
                    }
                )
                continue
            new_entry = entries_by_id.get(item["new_entry_id"])
            if new_entry is None:
                raise stale("source", "bound entry vanished from target")
            relation = _publication_relation(
                item,
                new_entry,
                old_entries_by_id.get(item["old_entry_id"]),
            )
            self._capture_lineage(page_id, old_binding, operation_id, now)
            captured_pages.add(page_id)
            store.supersede_binding(old_binding["binding_id"], now)
            binding_id = f"pb-{uuid.uuid4().hex}"
            store.insert_binding(
                {
                    "binding_id": binding_id,
                    "page_id": page_id,
                    "project_id": old_binding["project_id"],
                    "binding_version": int(old_binding["binding_version"]) + 1,
                    "source_id": body["source_id"],
                    "entry_id": new_entry["entry_id"],
                    "accepted_source_version": new_version_id
                    or old_binding["accepted_source_version"],
                    "status": "healthy",
                    "previous_binding_id": old_binding["binding_id"],
                    "authorization_generation": generation,
                    "authorized_at": now,
                    "verified_digest": new_entry["content_digest"],
                    "created_at": now,
                    "updated_at": now,
                }
            )
            store.insert_publication(
                binding_id=binding_id,
                operation_id=operation_id,
                previous_binding_id=old_binding["binding_id"],
                relation=relation,
            )
            if action == "bind" and decision["migrate_revision_ids"]:
                self._migrate_revisions(
                    page_id,
                    binding_id,
                    decision["migrate_revision_ids"],
                    operation_id,
                    now,
                )
            bindings.append(
                {
                    "page_id": page_id,
                    "binding_id": binding_id,
                    "binding_version": int(old_binding["binding_version"]) + 1,
                    "source_id": body["source_id"],
                    "version_id": new_version_id
                    or old_binding["accepted_source_version"],
                    "entry_id": new_entry["entry_id"],
                    "status": "healthy",
                }
            )
        bindings.sort(key=lambda row: row["page_id"])
        return {
            "operation_id": operation_id,
            "plan_id": body["plan_id"],
            "plan_digest": body["plan_id"] and _plan_digest_of_body(body),
            "request_digest": request_digest_of(
                operation_id, body["plan_id"], _plan_digest_of_body(body),
                body["kind"],
            ),
            "bindings": bindings,
            "committed_at": now,
        }

    def _ensure_target_version(
        self, body: dict, target: dict, grant, now: str
    ) -> str:
        store = self._store
        existing = store.get_source_version_row(
            body["source_id"], target["version_id"]
        )
        if existing is not None:
            return existing["version_id"]
        # A different physical identity needs its own location row (repoint /
        # replaced container); an unchanged physical file keeps the location.
        location = store.get_source_location_current(body["source_id"])
        location_id = location["location_id"]
        if grant is not None:
            facts = (
                grant.container_facts
                if grant.container_facts is not None
                else (
                    grant.folder_entries[0][1] if grant.folder_entries else None
                )
            )
            if facts is not None and (
                facts.sha256 != location["content_digest"]
                or int(facts.volume_serial) != int(location["volume_serial"])
                or int(facts.file_id) != int(location["file_id"])
            ):
                new_location_id = f"sl-{uuid.uuid4().hex}"
                # The partial unique index keeps exactly one current location:
                # clear the old current row BEFORE inserting the replacement.
                store._conn.execute(
                    "UPDATE source_locations SET is_current = 0"
                    " WHERE location_id = ?",
                    (location_id,),
                )
                store.insert_source_location_row(
                    {
                        "location_id": new_location_id,
                        "source_id": body["source_id"],
                        "registry_id": grant.registry_id,
                        "authorization_generation": int(grant.generation),
                        "content_digest": facts.sha256,
                        "volume_serial": int(facts.volume_serial),
                        "file_id": int(facts.file_id),
                        "size_bytes": int(facts.size),
                        "mtime_hint": None,
                        "observed_at": now,
                        "created_at": now,
                    }
                )
                location_id = new_location_id
        store.insert_source_version_row(
            {
                "version_id": target["version_id"],
                "source_id": body["source_id"],
                "location_id": location_id,
                "content_digest": target["content_digest"],
                "size_bytes": _grant_size(grant),
                "observed_at": now,
                "created_at": now,
            }
        )
        scan = self._scanner.take_live_scan(body["scan_id"])
        entries = scan.candidate_entries or _entries_from_target(target)
        rows = []
        for entry in entries:
            row = dict(entry)
            row["version_id"] = target["version_id"]
            rows.append(row)
        store.insert_source_entry_rows(rows)
        return target["version_id"]

    def _capture_lineage(
        self, page_id: str, old_binding: dict, operation_id: str, now: str
    ) -> None:
        """First-switch lineage capture (C-17 §7.1): the current revision is
        snapshotted onto the old binding (captured_v7); every other
        historical revision becomes legacy_unverified (read-diagnosis only).
        Rows with existing lineage keep their attribution."""
        conn = self._store._conn  # noqa: SLF001 - store-owned conn
        regions = conn.execute(
            "SELECT region_id, current_revision_id FROM regions"
            " WHERE page_id = ? ORDER BY region_id",
            (page_id,),
        ).fetchall()
        for region in regions:
            revisions = conn.execute(
                "SELECT region_revision_id FROM region_revisions"
                " WHERE region_id = ? ORDER BY revision_no",
                (region["region_id"],),
            ).fetchall()
            existing = self._store.lineage_exists_for_regions(
                [region["region_id"]]
            )
            if existing:
                # Already captured natively/migrated: attribution is frozen.
                for revision in revisions:
                    row = self._store.lineage_of_revision(
                        revision["region_revision_id"]
                    )
                    if row is None:
                        self._store.insert_lineage(
                            revision_id=revision["region_revision_id"],
                            region_id=region["region_id"],
                            binding_id=None,
                            provenance="legacy_unverified",
                        )
                continue
            for revision in revisions:
                current = (
                    revision["region_revision_id"] == region["current_revision_id"]
                )
                self._store.insert_lineage(
                    revision_id=revision["region_revision_id"],
                    region_id=region["region_id"],
                    binding_id=old_binding["binding_id"] if current else None,
                    provenance="captured_v7" if current else "legacy_unverified",
                    operation_id=operation_id if current else None,
                    now=now,
                )

    def _migrate_revisions(
        self,
        page_id: str,
        new_binding_id: str,
        revision_ids: list[str],
        operation_id: str,
        now: str,
    ) -> None:
        """Manual revision migration (C-17 §7.1): new region + new revision
        per migrated old current revision; the old rows are never moved or
        overwritten. A base-revision mismatch aborts the whole batch."""
        conn = self._store._conn  # noqa: SLF001 - store-owned conn
        for revision_id in revision_ids:
            revision = self._store.get_revision(revision_id)
            if revision is None:
                raise SourceSyncError(
                    "STALE_BASE_REVISION",
                    "migrated revision does not exist",
                )
            region = self._store.get_region(revision["region_id"])
            if region is None or region["page_id"] != page_id:
                raise _invalid("migrated revision belongs to another page")
            if region["current_revision_id"] != revision_id:
                raise SourceSyncError(
                    "STALE_BASE_REVISION",
                    "migrated revision is no longer the region current",
                )
            if self._store.lineage_of_revision(revision_id) is None:
                self._store.insert_lineage(
                    revision_id=revision_id,
                    region_id=region["region_id"],
                    binding_id=None,
                    provenance="legacy_unverified",
                )
            new_region_id = uuid.uuid4().hex
            new_revision_id = uuid.uuid4().hex
            conn.execute(
                "INSERT INTO regions (region_id, page_id, region_type,"
                " reading_order, geometry_json, text_json, style_json,"
                " sfx_policy, region_locked, translation_locked,"
                " inpaint_locked, current_revision_id, created_at,"
                " updated_at, deleted_at)"
                " SELECT ?, page_id, region_type, reading_order,"
                " geometry_json, text_json, style_json, sfx_policy,"
                " region_locked, translation_locked, inpaint_locked, NULL,"
                " ?, ?, NULL FROM regions WHERE region_id = ?",
                (new_region_id, now, now, region["region_id"]),
            )
            self._store.insert_migrated_revision(
                revision_id=new_revision_id,
                region_id=new_region_id,
                revision_no=1,
                snapshot_json=revision["snapshot_json"],
                now=now,
            )
            self._store.set_region_current_revision(
                new_region_id, new_revision_id, now
            )
            self._store.insert_lineage(
                revision_id=new_revision_id,
                region_id=new_region_id,
                binding_id=new_binding_id,
                provenance="migrated",
                from_revision_id=revision_id,
                operation_id=operation_id,
                now=now,
            )


def _plan_digest_of_body(body: dict) -> str:
    from application.sources.model import plan_digest_of

    return plan_digest_of(body)


def _publication_relation(
    item: dict, new_entry: dict, old_entry: dict | None
) -> str:
    """same_content only for direct/unique_pixel evidence with equivalent
    geometry records; anything else cuts coordinate inheritance (C-17 §7.1)."""
    if item["evidence"] == "direct":
        return "same_content"
    if item["evidence"] == "unique_pixel":
        old_geometry = (
            (old_entry.get("width"), old_entry.get("height"))
            if old_entry is not None
            else (None, None)
        )
        new_geometry = (new_entry.get("width"), new_entry.get("height"))
        if old_geometry == new_geometry or old_geometry == (None, None):
            return "same_content"
    return "changed"


def _basename(locator: str) -> str:
    return (locator.rsplit("/", 1)[-1] or "entry")[:255]


def _grant_size(grant) -> int:
    if grant is None:
        return 0
    if grant.container_facts is not None:
        return int(grant.container_facts.size)
    return sum(facts.size for _path, facts in grant.folder_entries)


def _entries_from_target(target: dict) -> list[dict]:
    """Rebuild candidate entry rows from the plan body when the live scan
    record is gone (apply happens within the plan TTL, the scan may have
    expired — the target evidence in the frozen body is authoritative)."""
    rows: list[dict] = []
    for index, entry in enumerate(target["entries"]):
        digest = entry.get("content_digest")
        rows.append(
            {
                "source_id": target["source_id"],
                "version_id": target["version_id"],
                "entry_id": entry["entry_id"],
                "locator": entry["locator"],
                "ordinal": entry["ordinal"],
                "stable_sort_key": f"{index:012d}",
                "content_digest_kind": entry["content_digest_kind"],
                "content_digest": digest,
                "encoded_digest": digest
                if entry["content_digest_kind"] == "encoded"
                else None,
                "pixel_digest": entry["pixel"]["pixel_digest"]
                if entry.get("pixel")
                else None,
                "pixel_digest_algorithm": "pixel-digest/1"
                if entry.get("pixel")
                else None,
                "size_bytes": 0,
                "mime_type": None,
                "width": entry["pixel"]["width"] if entry.get("pixel") else None,
                "height": entry["pixel"]["height"] if entry.get("pixel") else None,
                "orientation": entry["pixel"]["orientation"]
                if entry.get("pixel")
                else None,
                "decoder_name": entry["pixel"]["decoder"]
                if entry.get("pixel")
                else "",
                "decoder_version": entry["pixel"]["decoder_version"]
                if entry.get("pixel")
                else "",
                "decoder_params_json": "{}",
                "created_at": now_millis(),
            }
        )
    return rows


class _null_guard:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False
