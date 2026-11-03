"""FEA-09 PlanImportReferences orchestration (C-16 §4/§5).

Builds the frozen preview plan: resolves grants, scans each source, applies
the duplicate policy against existing bindings, freezes the plan digest and
keeps the plan in-process (never persisted, never password-bearing).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import time
import uuid

from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.model import (
    ResolvedSourceRead,
    ScannedSource,
    canonical_json,
)
from application.importing.referenced.scanner import scan_source

DUPLICATE_POLICIES = ("skip", "import_as_new")
PLAN_TTL_SECONDS = 300.0


@dataclass
class PlannedSource:
    grant_id: str
    source_index: int
    source_name: str
    source_kind: str
    status: str  # ok | unsupported | encrypted | error
    reason_code: str | None
    container_digest: str | None
    registry_id: str
    generation: int
    # Ordered page units; `already_referenced` marks entries bound in this
    # project (page-level skip), `unsupported` marks undecodable members.
    pages: list[dict] = field(default_factory=list)
    will_import: int = 0
    already_referenced: bool = False  # source-level: any live binding exists


@dataclass
class PlanRecord:
    plan_id: str
    chapter_id: str
    #: R1-I009: the plan is bound to one project and one duplicate policy;
    #: start re-confirms both (a changed chapter/book or policy is stale).
    book_id: str
    duplicate_policy: str
    plan_digest: str
    expires_at: float
    grant_ids: list[str]
    sources: list[PlannedSource]


class ReferencedImportPlanner:
    """Plan face of the referenced-import orchestration."""

    def __init__(
        self,
        *,
        access,
        repository,
        project_of_chapter,
        pdf_open,
        clock=time.time,
        plan_ttl: float = PLAN_TTL_SECONDS,
    ) -> None:
        self._access = access
        self._repository = repository
        self._project_of_chapter = project_of_chapter
        self._pdf_open = pdf_open
        self._clock = clock
        self._plan_ttl = plan_ttl
        self._plans: dict[str, PlanRecord] = {}

    # ------------------------------------------------------------------ plan
    def plan(
        self, *, chapter_id: str, grants: list[str], duplicate_policy: str
    ) -> dict:
        if (
            not isinstance(chapter_id, str)
            or not chapter_id
            or not isinstance(grants, list)
            or not grants
            or duplicate_policy not in DUPLICATE_POLICIES
        ):
            raise SourceImportError(
                "SOURCE_OPERATION_CONFLICT", "import plan request is invalid"
            )
        if self._repository.get_chapter(chapter_id) is None:
            raise SourceImportError(
                "SOURCE_OPERATION_NOT_FOUND", "import chapter was not found"
            )
        resolved: list[tuple[ResolvedSourceRead, ScannedSource]] = []
        for grant_id in grants:
            if not isinstance(grant_id, str) or not grant_id:
                raise SourceImportError(
                    "SOURCE_OPERATION_CONFLICT", "import plan request is invalid"
                )
            read = self._access.resolve(grant_id)
            resolved.append((read, scan_source(read, pdf_open=self._pdf_open)))

        project_id = self._project_of_chapter(chapter_id)
        if project_id is None:
            raise SourceImportError(
                "SOURCE_PROJECT_MISMATCH", "import chapter has no project"
            )

        sources: list[PlannedSource] = []
        for index, (read, scanned) in enumerate(resolved):
            sources.append(self._plan_source(index, read, scanned, project_id))

        plan_id = f"plan-{uuid.uuid4().hex}"
        now = self._clock()
        digest = self._plan_digest(plan_id, chapter_id, duplicate_policy, sources)
        record = PlanRecord(
            plan_id=plan_id,
            chapter_id=chapter_id,
            book_id=project_id,
            duplicate_policy=duplicate_policy,
            plan_digest=digest,
            expires_at=now + self._plan_ttl,
            grant_ids=list(grants),
            sources=sources,
        )
        self._plans[plan_id] = record
        self._evict_expired(now)
        return self.plan_response(record)

    # ------------------------------------------------------------- internals
    def _plan_source(
        self,
        index: int,
        read: ResolvedSourceRead,
        scanned: ScannedSource,
        project_id: str,
    ) -> PlannedSource:
        source = PlannedSource(
            grant_id=read.grant_id,
            source_index=index,
            source_name=scanned.source_name,
            source_kind=scanned.source_kind,
            status=scanned.status,
            reason_code=scanned.reason_code,
            container_digest=scanned.container_digest,
            registry_id=read.registry_id,
            generation=read.generation,
        )
        if scanned.status != "ok" and scanned.status != "encrypted":
            return source

        existing = None
        if scanned.container_digest is not None:
            existing = self._repository.find_source_by_physical_identity(
                scanned.container_digest, self._source_volume_serial(read),
                self._source_file_id(read),
            )
        entry_ids: dict[int, str] = {}
        if existing is not None:
            source_id = existing["source_id"]
            version = self._repository.get_source_version_by_digest(
                source_id, scanned.container_digest
            )
            if version is not None:
                for row in self._repository.list_source_entries(version["version_id"]):
                    for entry in scanned.entries:
                        if (
                            row["ordinal"] == entry.ordinal
                            and row["locator"] == entry.locator
                        ):
                            entry_ids[entry.ordinal] = row["entry_id"]
            referenced = self._repository.entry_binding_exists_for_source(
                project_id, source_id
            )
            source.already_referenced = referenced

        for entry in scanned.entries:
            unsupported = entry.content_digest is None and not entry.encrypted
            already = False
            entry_id = entry_ids.get(entry.ordinal)
            if entry_id is not None:
                already = (
                    self._repository.find_current_binding_for_entry(
                        project_id, existing["source_id"], entry_id
                    )
                    is not None
                )
            source.pages.append(
                {
                    "locator": entry.locator,
                    "ordinal": entry.ordinal,
                    "size_bytes": entry.size_bytes,
                    "content_digest": entry.content_digest,
                    "content_digest_kind": entry.content_digest_kind,
                    "encrypted": entry.encrypted,
                    "entry_id": entry_id,
                    "source_id": existing["source_id"] if existing else None,
                    "already_referenced": already,
                    "unsupported": unsupported,
                }
            )
        importable = [
            page
            for page in source.pages
            if not page["already_referenced"] and not page["unsupported"]
        ]
        source.will_import = len(importable)
        return source

    def _source_volume_serial(self, read: ResolvedSourceRead) -> int:
        facts = read.container_facts
        if facts is not None:
            return facts.volume_serial
        if read.folder_entries:
            return read.folder_entries[0][1].volume_serial
        return 0

    def _source_file_id(self, read: ResolvedSourceRead) -> int:
        facts = read.container_facts
        if facts is not None:
            return facts.file_id
        if read.folder_entries:
            return read.folder_entries[0][1].file_id
        return 0

    @staticmethod
    def _plan_digest(
        plan_id: str, chapter_id: str, duplicate_policy: str, sources: list[PlannedSource]
    ) -> str:
        payload = {
            "plan_id": plan_id,
            "chapter_id": chapter_id,
            "duplicate_policy": duplicate_policy,
            "sources": [
                {
                    "grant_id": source.grant_id,
                    "registry_id": source.registry_id,
                    "generation": source.generation,
                    "source_kind": source.source_kind,
                    "container_digest": source.container_digest,
                    "entries": (
                        [
                            {
                                "locator": page["locator"],
                                "ordinal": page["ordinal"],
                                "content_digest": page["content_digest"],
                            }
                            for page in source.pages
                        ]
                        if source.status != "encrypted"
                        else None
                    ),
                }
                for source in sources
            ],
        }
        return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()

    def _evict_expired(self, now: float) -> None:
        expired = [
            plan_id
            for plan_id, record in self._plans.items()
            if record.expires_at <= now
        ]
        for plan_id in expired:
            self._plans.pop(plan_id, None)

    # ------------------------------------------------------------- retrieval
    def take_for_start(
        self, *, plan_id: str, plan_digest: str, now: float | None = None
    ) -> PlanRecord:
        record = self._plans.get(plan_id)
        current = self._clock() if now is None else now
        if (
            record is None
            or record.expires_at <= current
            or record.plan_digest != plan_digest
        ):
            raise SourceImportError(
                "SOURCE_PLAN_STALE", "import plan is stale or expired"
            )
        return record

    def consume(self, plan_id: str) -> PlanRecord:
        """Remove a plan after a successful start (single confirmation)."""
        record = self._plans.pop(plan_id, None)
        if record is None:
            raise SourceImportError(
                "SOURCE_PLAN_STALE", "import plan is stale or expired"
            )
        return record

    @staticmethod
    def plan_response(record: PlanRecord) -> dict:
        totals = {"import": 0, "skip": 0, "unsupported": 0, "failed": 0}
        sources = []
        for source in record.sources:
            skip_pages = sum(
                1 for page in source.pages if page["already_referenced"]
            )
            unsupported_pages = sum(
                1 for page in source.pages if page["unsupported"]
            )
            if source.status == "unsupported":
                totals["unsupported"] += 1
            elif source.status == "error":
                totals["failed"] += 1
            elif source.already_referenced and record.duplicate_policy == "skip":
                totals["skip"] += 1
            else:
                totals["import"] += source.will_import
            totals["unsupported"] += unsupported_pages
            sources.append(
                {
                    "source_index": source.source_index,
                    "source_name": source.source_name,
                    "source_kind": source.source_kind,
                    "status": source.status,
                    "reason_code": source.reason_code,
                    "will_import": (
                        None
                        if source.status == "encrypted"
                        else source.will_import
                    ),
                    "already_referenced": source.already_referenced,
                }
            )
        return {
            "plan_id": record.plan_id,
            "plan_digest": record.plan_digest,
            "expires_at": record.expires_at,
            "chapter_id": record.chapter_id,
            "duplicate_policy": record.duplicate_policy,
            "sources": sources,
            "totals": totals,
        }
