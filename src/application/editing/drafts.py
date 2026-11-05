"""Application orchestration for C-13 drafts, candidates and protected apply."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import threading
import uuid
from typing import Any, Callable, Mapping, Sequence

from application.editing.errors import DraftError
from application.editing.ports import (
    RegionCommitStatus,
    RegionProtectionGuard,
    RegionRepository,
    RegionRevisionCommitter,
    RevisionLineage,
)
from application.editing.region_canvas import RegionCanvasError, page_geometry_to_normalized
from application.sources.lineage import LineageVerificationError
from domain.drafts.entities import Draft, DraftLease, DraftStatus, EditToken, RegionCandidate
from domain.regions.entities import (
    Region,
    RegionGeometry,
    RegionOrigin,
    RegionRevision,
    ReviewState,
    TextStyle,
)

_STYLE_KEYS = frozenset(TextStyle.__dataclass_fields__)
_TEXT_KEYS = frozenset({
    "ocr_text", "machine_translation", "edited_translation", "final_translation",
    "final_source", "edited_confirmed",
})
_ORIGIN_VALUES = frozenset(item.value for item in RegionOrigin)
_FLUSH_TRIGGERS = frozenset({
    "page_change", "workspace_switch", "exit", "window_close", "run_submit"
})


@dataclass
class _CandidateData:
    candidate: RegionCandidate
    staged_region: Region
    content_digest: str
    protection_digest: str
    draft_id: str | None
    draft_sequence: int | None


class DraftProtectionService:
    """Serial in-memory draft owner/patch/candidate registry over production ports."""

    def __init__(
        self,
        repository: RegionRepository,
        committer: RegionRevisionCommitter,
        connection: Any,
        journal: Any,
        *,
        debounce_seconds: float = 0.4,
        token_ttl_seconds: int = 900,
        lineage_binding: Callable[[str], str | None] | None = None,
    ) -> None:
        self._repository = repository
        self._committer = committer
        self._connection = connection
        self._journal = journal
        # FEA-11-LINEAGE-1 AC1 (r1 P0-1c): drafts apply is a revision write
        # path; every applied revision registers native lineage in the same
        # transaction as the draft's atomic region batch (C-17 §7.1).
        self._lineage_binding = lineage_binding
        self.debounce_seconds = debounce_seconds
        self.token_ttl_seconds = token_ttl_seconds
        self._lock = threading.RLock()
        self._drafts: dict[str, Draft] = {}
        self._target_by_session: dict[tuple[str, str, str], str] = {}
        self._owners: dict[tuple[str, str], str] = {}
        self._tokens: dict[str, EditToken] = {}
        self._candidates: dict[str, _CandidateData] = {}
        self._timers: dict[str, threading.Timer] = {}
        self._fail_closed = False
        for draft, intent in journal.load_drafts():
            self._drafts[draft.draft_id] = draft
            target = self._target_key(draft.page_id, draft.region_id)
            self._target_by_session[(draft.session_id, *target)] = draft.draft_id
            if draft.status is not DraftStatus.DISCARDED:
                self._owners.setdefault(target, draft.session_id)
            if intent:
                self._recover_commit_intent(draft, intent)
        journal.cleanup_receipts()

    @property
    def journal(self) -> Any:
        return self._journal

    @property
    def fail_closed(self) -> bool:
        return self._fail_closed

    def open_draft(
        self,
        session_id: str,
        page_id: str,
        region_id: str | None,
        *,
        base_revision_id: str | None,
        page_binding_version: int,
    ) -> DraftLease:
        if not session_id or not page_id:
            raise DraftError("DRAFT_INVALID", "SessionId and PageId are required")
        target = self._target_key(page_id, region_id)
        target_session_key = (session_id, *target)
        with self._lock:
            owner = self._owners.get(target)
            if owner is None:
                self._owners[target] = session_id
                owner = session_id
            if owner != session_id:
                owner_draft_id = self._target_by_session.get((owner, *target))
                if owner_draft_id is None:
                    raise DraftError("DRAFT_READ_ONLY", "another Session owns this Region")
                return DraftLease(deepcopy(self._drafts[owner_draft_id]), False, None)
            draft_id = self._target_by_session.get(target_session_key)
            if draft_id is None:
                draft = Draft(
                    draft_id=uuid.uuid4().hex,
                    session_id=session_id,
                    page_id=page_id,
                    region_id=region_id,
                    base_revision_id=base_revision_id,
                    page_binding_version=page_binding_version,
                )
                self._drafts[draft.draft_id] = draft
                self._target_by_session[target_session_key] = draft.draft_id
                # AC16: edit-open registers the active Draft before returning
                # its lease. Keep the in-memory draft editable if persistence
                # is unavailable, but prevent apply until the journal recovers.
                try:
                    self._journal.write_draft(draft)
                except Exception:
                    draft.status = DraftStatus.CONFLICTED
                    self._fail_closed = True
            else:
                draft = self._drafts[draft_id]
                if draft.page_binding_version != page_binding_version:
                    draft.status = DraftStatus.CONFLICTED
                    raise DraftError(
                        "DRAFT_BINDING_CHANGED", "PageBindingVersion changed",
                        details={"DraftId": draft.draft_id},
                    )
            token = self.issue_edit_token(draft.draft_id)
            return DraftLease(deepcopy(draft), True, token)

    def get_draft(self, draft_id: str) -> Draft:
        with self._lock:
            draft = self._drafts.get(draft_id)
            if draft is None:
                raise DraftError("DRAFT_NOT_FOUND", "draft does not exist")
            return deepcopy(draft)

    def list_drafts(self, *, session_id: str | None = None) -> list[Draft]:
        with self._lock:
            return [
                deepcopy(draft) for draft in self._drafts.values()
                if session_id is None or draft.session_id == session_id
            ]

    def patch_draft(
        self, draft_id: str, session_id: str, patch: Mapping[str, Any], *,
        undo_cursor: int | None = None, schedule_flush: bool = True,
    ) -> Draft:
        with self._lock:
            draft = self._require_owned_draft(draft_id, session_id)
            target = self._target_key(draft.page_id, draft.region_id)
            if self._owners.get(target) != session_id:
                raise DraftError("DRAFT_READ_ONLY", "Session no longer owns this draft")
            incoming_text = patch.get("text") if isinstance(patch, Mapping) else None
            if incoming_text is not None:
                if not isinstance(incoming_text, Mapping):
                    raise DraftError("DRAFT_PATCH_INVALID", "text patch must be an object")
                self._detect_text_conflict(draft, incoming_text)
            draft.apply_patch(patch, undo_cursor=undo_cursor)
            if draft.status is not DraftStatus.CONFLICTED:
                draft.status = DraftStatus.ACTIVE
            if schedule_flush:
                self._schedule_flush(draft_id)
            return deepcopy(draft)

    def resolve_text_conflict(
        self, draft_id: str, session_id: str, replacement_text: str
    ) -> Draft:
        with self._lock:
            draft = self._require_owned_draft(draft_id, session_id)
            target = self._target_key(draft.page_id, draft.region_id)
            if self._owners.get(target) != session_id:
                raise DraftError("DRAFT_READ_ONLY", "Session no longer owns this draft")
            text_patch = dict(draft.patch.get("text", {}))
            text_patch["edited_translation"] = replacement_text
            draft.patch["text"] = text_patch
            draft.draft_sequence += 1
            draft.saved_at = _utc_now()
            draft.status = DraftStatus.ACTIVE
            self._schedule_flush(draft_id)
            return deepcopy(draft)

    def transfer_owner(
        self, page_id: str, region_id: str | None, *, from_session_id: str,
        to_session_id: str,
    ) -> None:
        if not to_session_id:
            raise DraftError("DRAFT_INVALID", "target SessionId is required")
        target = self._target_key(page_id, region_id)
        with self._lock:
            if self._owners.get(target) != from_session_id:
                raise DraftError("DRAFT_OWNER_CHANGED", "owner transfer source is not current")
            self._owners[target] = to_session_id

    def discard_draft(self, draft_id: str, session_id: str) -> None:
        with self._lock:
            draft = self._require_owned_draft(draft_id, session_id)
            timer = self._timers.pop(draft_id, None)
            if timer is not None:
                timer.cancel()
            draft.status = DraftStatus.DISCARDED
            self._journal.delete_receipts(draft_id)
            self._journal.delete_draft(draft_id)
            self._drafts.pop(draft_id, None)
            target = self._target_key(draft.page_id, draft.region_id)
            self._target_by_session.pop((session_id, *target), None)
            if self._owners.get(target) == session_id:
                if self._owners.get(target) == draft.session_id:
                    self._owners.pop(target, None)
            for candidate_id, data in tuple(self._candidates.items()):
                if data.draft_id == draft_id:
                    self._candidates.pop(candidate_id, None)

    def end_session(self, session_id: str) -> None:
        with self._lock:
            ending = [d for d in self._drafts.values() if d.session_id == session_id]
            # A clean Session end first attempts the mandated exit flush. If it
            # fails, leave the in-memory draft and journal intact for retry.
            for draft in ending:
                self.flush_draft(draft.draft_id)
            for draft in ending:
                timer = self._timers.pop(draft.draft_id, None)
                if timer is not None:
                    timer.cancel()
                self._journal.delete_draft(draft.draft_id)
                target = self._target_key(draft.page_id, draft.region_id)
                self._target_by_session.pop((session_id, *target), None)
                if self._owners.get(target) == session_id:
                    self._owners.pop(target, None)
                self._drafts.pop(draft.draft_id, None)
                for candidate_id, data in tuple(self._candidates.items()):
                    if data.draft_id == draft.draft_id:
                        self._candidates.pop(candidate_id, None)
            for token_id, token in tuple(self._tokens.items()):
                if token.session_id == session_id:
                    self._tokens.pop(token_id, None)

    def discard_orphans(self, active_session_ids: set[str]) -> list[str]:
        discarded: list[str] = []
        with self._lock:
            for draft_id, draft in list(self._drafts.items()):
                if draft.session_id in active_session_ids:
                    continue
                draft.status = DraftStatus.DISCARDED
                timer = self._timers.pop(draft_id, None)
                if timer is not None:
                    timer.cancel()
                # A discarded orphan must not keep the target owned or the draft
                # cached, otherwise a new Session can never reopen the page
                # (permanent DRAFT_TEXT_CONFLICT) and the journal leaks files.
                self._journal.delete_receipts(draft_id)
                self._journal.delete_draft(draft_id)
                target = self._target_key(draft.page_id, draft.region_id)
                if self._owners.get(target) == draft.session_id:
                    self._owners.pop(target, None)
                self._target_by_session.pop((draft.session_id, *target), None)
                for candidate_id, data in tuple(self._candidates.items()):
                    if data.draft_id == draft_id:
                        self._candidates.pop(candidate_id, None)
                for token_id, token in tuple(self._tokens.items()):
                    if token.draft_id == draft_id:
                        self._tokens.pop(token_id, None)
                discarded.append(draft_id)
        return discarded

    def issue_edit_token(self, draft_id: str, *, ttl_seconds: int | None = None) -> EditToken:
        with self._lock:
            draft = self._drafts.get(draft_id)
            if draft is None:
                raise DraftError("DRAFT_NOT_FOUND", "draft does not exist")
            ttl = self.token_ttl_seconds if ttl_seconds is None else ttl_seconds
            issued = datetime.now(timezone.utc)
            token = EditToken(
                token_id=uuid.uuid4().hex,
                draft_id=draft.draft_id,
                draft_sequence=draft.draft_sequence,
                session_id=draft.session_id,
                issued_at=issued.isoformat(timespec="microseconds"),
                expires_at=(issued + timedelta(seconds=ttl)).isoformat(timespec="microseconds"),
            )
            self._tokens[token.token_id] = token
            return token

    def prepare_candidate(
        self,
        region_id: str,
        patch: Mapping[str, Any],
        *,
        origin: str,
        draft_id: str | None = None,
        base_revision_id: str | None = None,
    ) -> RegionCandidate:
        if origin not in _ORIGIN_VALUES:
            raise DraftError("DRAFT_CANDIDATE_INVALID", "origin is not allowed")
        if not isinstance(patch, Mapping):
            raise DraftError("DRAFT_PATCH_INVALID", "candidate patch must be an object")
        style = patch.get("style", {})
        if not isinstance(style, Mapping):
            raise DraftError("DRAFT_PATCH_INVALID", "style patch must be an object")
        forbidden = sorted(set(style) - _STYLE_KEYS)
        if forbidden:
            key = forbidden[0]
            raise DraftError(
                "STYLE_KEY_NOT_ALLOWED", f"style key is not allowed: {key}",
                details={"key": key},
            )
        region = self._repository.get_region(region_id)
        if region is None or region.deleted:
            raise DraftError("TARGET_NOT_FOUND", "Region does not exist")
        actual_base = region.current_revision_id
        expected_base = actual_base if base_revision_id is None else base_revision_id
        if not actual_base or expected_base != actual_base:
            raise DraftError("STALE_BASE_REVISION", "candidate BaseRevisionId is stale")
        text_patch = patch.get("text", {})
        geometry_patch = patch.get("geometry")
        has_any = bool(text_patch) or geometry_patch is not None or bool(style)
        if region.region_locked and has_any:
            raise DraftError("LOCK_CHANGED", "region_locked rejects every editable domain")
        if text_patch and not isinstance(text_patch, Mapping):
            raise DraftError("DRAFT_PATCH_INVALID", "text patch must be an object")
        if text_patch and (region.translation_locked or region.text.translation_locked):
            raise DraftError("LOCK_CHANGED", "translation_locked rejects text changes")
        unknown_text = sorted(set(text_patch) - _TEXT_KEYS) if isinstance(text_patch, Mapping) else []
        if unknown_text:
            raise DraftError(
                "DRAFT_PATCH_INVALID", "unsupported text key: " + unknown_text[0],
                details={"key": unknown_text[0]},
            )
        staged = deepcopy(region)
        self._apply_candidate_patch(staged, patch)
        candidate = RegionCandidate(
            candidate_id=uuid.uuid4().hex,
            region_id=region_id,
            base_revision_id=expected_base,
            origin=origin,
        )
        content_digest = self._content_digest(staged.region_id, staged.snapshot_state())
        data = _CandidateData(
            candidate=candidate,
            staged_region=staged,
            content_digest=content_digest,
            protection_digest=protection_digest(region),
            draft_id=draft_id,
            draft_sequence=(self._drafts[draft_id].draft_sequence if draft_id in self._drafts else None),
        )
        with self._lock:
            self._candidates[candidate.candidate_id] = data
        return candidate

    def discard_candidate(self, candidate_id: str) -> None:
        with self._lock:
            self._candidates.pop(candidate_id, None)

    def apply_candidates(
        self, token: EditToken | Mapping[str, Any], candidate_ids: Sequence[str] = ()
    ) -> dict[str, str]:
        edit_token = token if isinstance(token, EditToken) else _token_from_json(token)
        with self._lock:
            if self._fail_closed:
                raise DraftError("DRAFT_JOURNAL_UNWRITABLE", "draft writes are fail-closed")
            if edit_token.is_expired():
                raise DraftError("EDIT_TOKEN_EXPIRED", "edit token has expired")
            draft_for_receipt = self._drafts.get(edit_token.draft_id)
            receipt_sequence = (
                draft_for_receipt.draft_sequence
                if draft_for_receipt is not None
                else edit_token.draft_sequence
            )
            receipt = self._journal.read_receipt(
                edit_token.draft_id, receipt_sequence
            )
            data = [self._candidates.get(candidate_id) for candidate_id in candidate_ids]
            if receipt is not None:
                if not candidate_ids:
                    if receipt.get("tokenId") == edit_token.token_id:
                        return dict(receipt.get("revisionIds", {}))
                    raise DraftError("EDIT_TOKEN_REUSED", "receipt replay token does not match")
                if any(item is None for item in data):
                    if all(item is None for item in data) and receipt.get("tokenId") == edit_token.token_id:
                        return dict(receipt.get("revisionIds", {}))
                    raise DraftError("EDIT_TOKEN_REUSED", "receipt replay lacks matching content")
                request_digests = {
                    item.candidate.region_id: item.content_digest for item in data if item is not None
                }
                if request_digests and request_digests != receipt.get("contentDigests", {}):
                    raise DraftError("EDIT_TOKEN_REUSED", "token was reused with different content")
                return dict(receipt.get("revisionIds", {}))
            issued = self._tokens.get(edit_token.token_id)
            if issued != edit_token:
                raise DraftError("EDIT_TOKEN_INVALID", "edit token is unknown to this Core session")
            draft = self._drafts.get(edit_token.draft_id)
            if draft is None or draft.session_id != edit_token.session_id:
                raise DraftError("DRAFT_NOT_FOUND", "token draft is not active")
            if draft.status in (DraftStatus.CONFLICTED, DraftStatus.DISCARDED):
                raise DraftError(
                    "DRAFT_CANDIDATE_INVALID", "conflicted or discarded draft cannot be applied"
                )
            if draft.draft_sequence < edit_token.draft_sequence:
                raise DraftError("EDIT_TOKEN_REUSED", "token sequence does not match the draft")
            if not candidate_ids or any(item is None for item in data):
                raise DraftError("DRAFT_CANDIDATE_NOT_FOUND", "candidate registry entry is missing")
            candidate_data = [item for item in data if item is not None]
            if any(
                item.draft_id is not None and item.draft_id != draft.draft_id
                for item in candidate_data
            ):
                raise DraftError("DRAFT_CANDIDATE_INVALID", "candidate belongs to another draft")
            if any(
                item.draft_sequence is not None and item.draft_sequence < edit_token.draft_sequence
                for item in candidate_data
            ):
                raise DraftError("DRAFT_CANDIDATE_INVALID", "candidate sequence differs from token")
            if draft.region_id is not None and any(
                item.candidate.region_id != draft.region_id for item in candidate_data
            ):
                raise DraftError("DRAFT_CANDIDATE_INVALID", "candidate RegionId differs from draft")
            if draft.region_id is None and any(
                item.staged_region.page_id != draft.page_id for item in candidate_data
            ):
                raise DraftError("DRAFT_CANDIDATE_INVALID", "candidate PageId differs from draft")
            if draft.region_id is not None and any(
                self._owners.get(self._target_key(item.staged_region.page_id, item.candidate.region_id))
                != draft.session_id for item in candidate_data
            ):
                raise DraftError("DRAFT_READ_ONLY", "Session no longer owns the target Region")
            region_ids = [item.candidate.region_id for item in candidate_data]
            if len(set(region_ids)) != len(region_ids):
                raise DraftError("DRAFT_CANDIDATE_INVALID", "duplicate RegionId in one apply")
            content_digests = {
                item.candidate.region_id: item.content_digest for item in candidate_data
            }
            expected_revision_ids = {region_id: uuid.uuid4().hex for region_id in region_ids}
            intent = {
                "tokenId": edit_token.token_id,
                "DraftId": draft.draft_id,
                "DraftSequence": draft.draft_sequence,
                "expectedRevisionIds": expected_revision_ids,
                "contentDigests": content_digests,
                "startedAt": _utc_now(),
            }
            try:
                self._journal.write_draft(draft, commit_intent=intent)
            except Exception as error:
                raise _journal_error(error) from error
            db_committed = False
            try:
                updates = []
                guards = []
                lineage_by_region: dict[str, RevisionLineage] = {}
                for item in candidate_data:
                    region_id = item.candidate.region_id
                    staged = deepcopy(item.staged_region)
                    staged.current_revision_id = expected_revision_ids[region_id]
                    revision = RegionRevision(
                        region_revision_id=expected_revision_ids[region_id],
                        region_id=region_id,
                        revision_no=0,
                        snapshot=staged.snapshot_state(),
                        origin=RegionOrigin(item.candidate.origin),
                        review_state=ReviewState.NEEDS_REVIEW,
                    )
                    updates.append((staged, revision, None))
                    guards.append(RegionProtectionGuard(
                        region_id=region_id,
                        base_revision_id=item.candidate.base_revision_id,
                        protection_digest=item.protection_digest,
                    ))
                    lineage = self._lineage_for(staged.page_id)
                    if lineage is not None:
                        lineage_by_region[region_id] = lineage
                try:
                    result = self._committer.commit_region_batch_guarded(
                        updated_regions=updates,
                        protection_guards=guards,
                        lineage_by_region=lineage_by_region or None,
                    )
                except LineageVerificationError as error:
                    # FEA-11-LINEAGE-1: C-17 §7.1 typed refusal — a draft
                    # captured against a stale/other binding must never flush
                    # old coordinates into the current binding. Zero write.
                    raise DraftError(error.code, error.detail) from error
                if result.status is RegionCommitStatus.STALE_BASE_REVISION:
                    raise DraftError("STALE_BASE_REVISION", "BaseRevisionId changed before apply")
                if result.status is RegionCommitStatus.LOCK_CHANGED:
                    raise DraftError("LOCK_CHANGED", "protectionDigest changed before apply")
                if result.status is not RegionCommitStatus.APPLIED:
                    raise DraftError(
                        "DRAFT_APPLY_FAILED", "atomic Region apply failed",
                        details={"status": result.status.value, "detail": result.detail},
                    )
                db_committed = True
                receipt_data = {
                    "tokenId": edit_token.token_id,
                    "DraftId": draft.draft_id,
                    "DraftSequence": receipt_sequence,
                    "revisionIds": dict(result.revision_ids or expected_revision_ids),
                    "contentDigests": content_digests,
                    "committedAt": _utc_now(),
                }
                try:
                    self._journal.write_receipt(receipt_data)
                except Exception as error:
                    self._fail_closed = True
                    raise DraftError(
                        "DRAFT_JOURNAL_UNWRITABLE", "commit receipt write failed; apply is fail-closed",
                        cause_code=getattr(error, "code", None),
                    ) from error
                draft.status = DraftStatus.FLUSHED
                draft.saved_at = _utc_now()
                try:
                    self._journal.write_draft(draft)
                except Exception as error:
                    self._fail_closed = True
                    raise DraftError(
                        "DRAFT_JOURNAL_UNWRITABLE", "commit intent could not be cleared",
                        cause_code=getattr(error, "code", None),
                    ) from error
                for item in candidate_data:
                    self._candidates.pop(item.candidate.candidate_id, None)
                return dict(receipt_data["revisionIds"])
            except DraftError:
                if not db_committed:
                    try:
                        self._journal.write_draft(draft)
                    except Exception as error:
                        self._fail_closed = True
                        raise DraftError(
                            "DRAFT_JOURNAL_UNWRITABLE", "failed to clear unsuccessful commit intent",
                            cause_code=getattr(error, "code", None),
                        )
                raise
            except Exception as error:
                if not db_committed:
                    try:
                        self._journal.write_draft(draft)
                    except Exception as clear_error:
                        self._fail_closed = True
                        raise DraftError(
                            "DRAFT_JOURNAL_UNWRITABLE", "failed to clear unsuccessful commit intent",
                            cause_code=getattr(clear_error, "code", None),
                        ) from clear_error
                raise DraftError("DRAFT_APPLY_FAILED", "atomic Region apply failed") from error

    def flush_draft(self, draft_id: str) -> Draft:
        with self._lock:
            draft = self._drafts.get(draft_id)
            if draft is None:
                raise DraftError("DRAFT_NOT_FOUND", "draft does not exist")
            try:
                if draft.region_id is not None and draft.base_revision_id is None:
                    region = self._repository.get_region(draft.region_id)
                    if region is None or region.deleted:
                        raise DraftError("TARGET_NOT_FOUND", "draft Region is not available")
                    draft.base_revision_id = region.current_revision_id
                self._journal.write_draft(draft)
            except Exception as error:
                draft.status = DraftStatus.CONFLICTED
                draft.saved_at = _utc_now()
                raise DraftError(
                    "DRAFT_FLUSH_FAILED", "draft remains in memory but could not be persisted",
                    details={"DraftId": draft_id},
                    cause_code=getattr(error, "code", "DRAFT_JOURNAL_UNWRITABLE"),
                ) from error
            draft.status = DraftStatus.FLUSHED
            draft.saved_at = _utc_now()
            return deepcopy(draft)

    def force_flush(self, draft_id: str, trigger: str) -> Draft:
        if trigger not in _FLUSH_TRIGGERS:
            raise DraftError("DRAFT_FLUSH_TRIGGER_INVALID", "unknown forced flush trigger")
        timer = self._timers.pop(draft_id, None)
        if timer is not None:
            timer.cancel()
        return self.flush_draft(draft_id)

    def flush_pending(self, *, trigger: str) -> list[Draft]:
        if trigger not in _FLUSH_TRIGGERS:
            raise DraftError("DRAFT_FLUSH_TRIGGER_INVALID", "unknown forced flush trigger")
        with self._lock:
            draft_ids = list(self._drafts)
        return [self.force_flush(draft_id, trigger) for draft_id in draft_ids]

    def protection_digest(self, region_id: str) -> str:
        region = self._repository.get_region(region_id)
        if region is None or region.deleted:
            raise DraftError("TARGET_NOT_FOUND", "Region does not exist")
        return protection_digest(region)

    def _lineage_for(self, page_id: str) -> RevisionLineage | None:
        """FEA-11-LINEAGE-1 AC1: the native lineage row of an applied draft
        revision (resolved from the page's current binding at apply time)."""
        if self._lineage_binding is None:
            return None
        binding_id = self._lineage_binding(page_id)
        if not binding_id:
            return None
        return RevisionLineage(binding_id=binding_id, provenance="native")

    def _apply_candidate_patch(self, region: Region, patch: Mapping[str, Any]) -> None:
        geometry = patch.get("geometry")
        if geometry is not None:
            if isinstance(geometry, RegionGeometry):
                region.geometry = deepcopy(geometry)
            elif isinstance(geometry, Mapping):
                region.geometry = RegionGeometry.from_jsonable(dict(geometry))
            else:
                raise DraftError("DRAFT_PATCH_INVALID", "geometry must be an object")
        text_patch = patch.get("text", {})
        if text_patch:
            values = dict(text_patch)
            if "edited_translation" in values:
                region.text.save_manual_translation(str(values.pop("edited_translation")))
            confirmed = values.pop("edited_confirmed", None)
            for key, value in values.items():
                setattr(region.text, key, value)
            if confirmed is True:
                region.text.confirm_edited_translation()
            elif confirmed is False:
                region.text.edited_confirmed = False
            region.text.refresh_final()
        style = patch.get("style", {})
        for key, value in style.items():
            setattr(region.style, key, value)

    def _content_digest(self, region_id: str, snapshot: Mapping[str, Any]) -> str:
        page_id_row = self._connection.execute(
            "SELECT page_id FROM regions WHERE region_id = ?", (region_id,)
        ).fetchone()
        if page_id_row is None:
            raise DraftError("TARGET_NOT_FOUND", "Region page is missing")
        size = self._connection.execute(
            "SELECT width, height FROM pages WHERE page_id = ?", (page_id_row["page_id"],)
        ).fetchone()
        if size is None or not size["width"] or not size["height"]:
            raise DraftError("PAGE_SIZE_UNAVAILABLE", "page extent is unavailable")
        try:
            geometry = page_geometry_to_normalized(
                RegionGeometry.from_jsonable(snapshot["geometry"]),
                int(size["width"]), int(size["height"]),
            )
        except RegionCanvasError as error:
            raise DraftError("PAGE_SIZE_UNAVAILABLE", "page extent is unavailable") from error
        style = {key: snapshot["style"][key] for key in sorted(_STYLE_KEYS)}
        content = {
            "text_json": snapshot["text"],
            "geometry": geometry,
            "style_json": style,
        }
        canonical = json.dumps(
            content, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    def _recover_commit_intent(self, draft: Draft, intent: Mapping[str, Any]) -> None:
        try:
            receipt = self._journal.read_receipt(draft.draft_id, draft.draft_sequence)
            if receipt is not None:
                self._journal.write_draft(draft)
                return
            expected = intent["expectedRevisionIds"]
            digests = intent["contentDigests"]
            recovered: dict[str, str] = {}
            for region_id, revision_id in expected.items():
                region = self._repository.get_region(region_id)
                if region is None or region.current_revision_id != revision_id:
                    self._journal.write_draft(draft)
                    return
                revision = self._repository.revision_by_id(revision_id)
                if revision is None or revision.region_id != region_id:
                    self._journal.write_draft(draft)
                    return
                if self._content_digest(region_id, revision.snapshot) != digests.get(region_id):
                    self._journal.write_draft(draft)
                    return
                recovered[region_id] = revision_id
            receipt_data = {
                "tokenId": intent["tokenId"],
                "DraftId": draft.draft_id,
                "DraftSequence": draft.draft_sequence,
                "revisionIds": recovered,
                "contentDigests": dict(digests),
                "committedAt": _utc_now(),
            }
            self._journal.write_receipt(receipt_data)
            self._journal.write_draft(draft)
        except Exception as error:
            self._fail_closed = True
            raise DraftError(
                "DRAFT_JOURNAL_UNWRITABLE", "commit intent recovery failed closed",
                cause_code=getattr(error, "code", None),
            ) from error

    def _detect_text_conflict(
        self, owner_draft: Draft, incoming: Mapping[str, Any]
    ) -> None:
        target = self._target_key(owner_draft.page_id, owner_draft.region_id)
        for draft in self._drafts.values():
            if draft.draft_id == owner_draft.draft_id:
                continue
            if draft.status is DraftStatus.DISCARDED:
                continue
            if self._target_key(draft.page_id, draft.region_id) != target:
                continue
            previous = draft.patch.get("text")
            if draft.session_id != owner_draft.session_id and previous and dict(previous) != dict(incoming):
                draft.status = DraftStatus.CONFLICTED
                owner_draft.status = DraftStatus.CONFLICTED
                raise DraftError(
                    "DRAFT_TEXT_CONFLICT", "text changes conflict across Sessions",
                    details={"draftIds": [draft.draft_id, owner_draft.draft_id]},
                )

    def _schedule_flush(self, draft_id: str) -> None:
        previous = self._timers.pop(draft_id, None)
        if previous is not None:
            previous.cancel()
        timer = threading.Timer(self.debounce_seconds, self._debounced_flush, args=(draft_id,))
        timer.daemon = True
        self._timers[draft_id] = timer
        timer.start()

    def _debounced_flush(self, draft_id: str) -> None:
        try:
            self.flush_draft(draft_id)
        except DraftError:
            pass
        finally:
            with self._lock:
                self._timers.pop(draft_id, None)

    def _require_owned_draft(self, draft_id: str, session_id: str) -> Draft:
        draft = self._drafts.get(draft_id)
        if draft is None:
            raise DraftError("DRAFT_NOT_FOUND", "draft does not exist")
        if draft.session_id != session_id:
            raise DraftError("DRAFT_READ_ONLY", "Session does not own this draft")
        return draft

    @staticmethod
    def _target_key(page_id: str, region_id: str | None) -> tuple[str, str]:
        return (page_id, region_id if region_id is not None else "@page")


def protection_digest(region: Region) -> str:
    protection = {
        "region_locked": bool(region.region_locked),
        "translation_locked": bool(region.translation_locked),
        "inpaint_locked": bool(region.inpaint_locked),
        "text_translation_locked": bool(region.text.translation_locked),
        "manual_edited": bool(region.text.manual_edited),
    }
    return hashlib.sha256(
        json.dumps(protection, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _token_from_json(data: Mapping[str, Any]) -> EditToken:
    try:
        sequence = data["DraftSequence"]
        if isinstance(sequence, bool) or not isinstance(sequence, int):
            raise ValueError("DraftSequence must be an integer")
        token = EditToken(
            token_id=str(data["tokenId"]),
            draft_id=str(data["DraftId"]),
            draft_sequence=sequence,
            session_id=str(data["SessionId"]),
            issued_at=str(data["issuedAt"]),
            expires_at=str(data["expiresAt"]),
        )
        expiry = datetime.fromisoformat(token.expires_at.replace("Z", "+00:00"))
        if expiry.tzinfo is None:
            raise ValueError("expiresAt must include a timezone")
        return token
    except (KeyError, TypeError, ValueError) as error:
        raise DraftError("EDIT_TOKEN_INVALID", "edit token is malformed") from error

def _journal_error(error: Exception) -> DraftError:
    return DraftError(
        getattr(error, "code", "DRAFT_JOURNAL_UNWRITABLE"),
        "draft journal operation failed",
        cause_code=getattr(error, "code", None),
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")
