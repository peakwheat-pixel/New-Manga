"""Reader export use case (TASK-015; D03 §31, D04 §37, D06 §96~97).

One service covers all five formats (single_image / zip / cbz / pdf /
text, AC-EXPORT-001) with, per D05 §51:

- scope and order: the caller passes pages already in export order;
- output path and file naming: full target path in, archive entry names
  derived from page filenames (sanitized, order-prefixed);
- overwrite policy: overwrite / skip / auto-rename;
- stale handling: translated exports refuse stale or missing renders
  unless the caller explicitly continues with the existing versions
  (D06 §97 — never silently pretend output is current).

Durability contract (失败或取消不得破坏既有目标文件和源文件):

- the output is written to a temp file in the target directory and moved
  into place with ``os.replace`` as the final step, so an existing target
  survives any failure or cancellation;
- page sources are only ever read; source files are never written;
- every terminal state (completed / skipped / cancelled / failed) is
  recorded in the export history (D03 §31, AC-EXPORT-002).
"""

from __future__ import annotations

import hashlib
import os
import tempfile
import uuid
import zipfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from domain.books.entities import utc_now

from application.export.ports import HistoryDocumentStore, JsonHistoryDocumentStore, PdfComposer


class ExportFormat(str, Enum):
    """D03 §31 export types."""

    SINGLE_IMAGE = "single_image"
    ZIP = "zip"
    CBZ = "cbz"
    PDF = "pdf"
    TEXT = "text"


class OverwritePolicy(str, Enum):
    """D05 §51 覆盖策略."""

    OVERWRITE = "overwrite"
    SKIP = "skip"
    AUTO_RENAME = "auto_rename"


class StalePolicy(str, Enum):
    """D06 §97: refuse stale/missing renders, or continue explicitly."""

    ABORT = "abort"
    CONTINUE = "continue"


class ExportStatus(str, Enum):
    COMPLETED = "completed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    FAILED = "failed"


class ExportError(Exception):
    """Base class for export failures surfaced to the UI."""


class ExportValidationError(ExportError):
    """Request is not exportable (empty scope, wrong page count…)."""


class StaleExportError(ExportError):
    """Translated export hits stale/missing renders (D06 §97).

    The UI must prompt 先重渲染 or 明确继续导出现有版本; continuing is
    expressed by ``stale_policy=CONTINUE`` on the retried request.
    """

    def __init__(self, stale_page_ids: Sequence[str], missing_page_ids: Sequence[str]) -> None:
        self.stale_page_ids = tuple(stale_page_ids)
        self.missing_page_ids = tuple(missing_page_ids)
        parts = []
        if self.missing_page_ids:
            parts.append(f"缺少译图的页: {', '.join(self.missing_page_ids)}")
        if self.stale_page_ids:
            parts.append(f"译图不是最新渲染结果的页: {', '.join(self.stale_page_ids)}")
        super().__init__(
            "部分页面不是最新渲染结果（" + "；".join(parts) + "）；可先重新渲染，或明确继续导出现有版本"
        )


class ExportCancelledError(ExportError):
    """The caller's cancel predicate fired; nothing was published."""


class PdfUnavailableError(ExportError):
    """PDF export requested but no composer is wired in."""


@dataclass(frozen=True)
class ExportPage:
    """One page in export scope.

    Providers are lazy so bytes are only read for pages actually exported;
    ``translated_revision_id`` vs ``current_translated_revision_id`` drives
    the stale check exactly like the reader (D06 §97).
    """

    page_id: str
    filename: str
    source_provider: Callable[[], bytes]
    translated_provider: Callable[[], bytes] | None = None
    translated_revision_id: str | None = None
    current_translated_revision_id: str | None = None
    text: str = ""

    @property
    def stale(self) -> bool:
        return bool(
            self.translated_provider
            and self.translated_revision_id
            and self.current_translated_revision_id
            and self.translated_revision_id != self.current_translated_revision_id
        )

    def provider_for(self, mode: str) -> Callable[[], bytes]:
        """Bytes provider for the mode, falling back to the original when
        the translated render is absent (only reachable with CONTINUE)."""
        if mode == "translated" and self.translated_provider is not None:
            return self.translated_provider
        return self.source_provider


@dataclass(frozen=True)
class ExportRequest:
    book_id: str
    chapter_id: str
    format: ExportFormat
    output_path: Path
    pages: tuple[ExportPage, ...]
    mode: str = "original"
    overwrite_policy: OverwritePolicy = OverwritePolicy.OVERWRITE
    stale_policy: StalePolicy = StalePolicy.ABORT
    pipeline_run_id: str | None = None
    render_profile_snapshot: dict | None = None
    #: Polled between stages and between pages; returning True cancels.
    cancel: Callable[[], bool] | None = None


@dataclass(frozen=True)
class ExportResult:
    export_id: str
    book_id: str
    chapter_id: str
    format: ExportFormat
    mode: str
    status: ExportStatus
    output_path: Path | None
    page_ids: tuple[str, ...]
    file_hash: str | None
    included_stale_page_ids: tuple[str, ...]
    included_missing_page_ids: tuple[str, ...]
    completed_at: str


@dataclass(frozen=True)
class ExportRecord:
    """D03 §31 ExportHistory row (plus ``detail`` for failures)."""

    export_id: str
    book_id: str
    chapter_id: str
    pipeline_run_id: str | None
    export_type: str
    scope_snapshot_json: str
    output_path: str
    render_profile_snapshot_json: str
    status: str
    file_hash: str
    created_at: str
    completed_at: str
    detail: str = ""


@dataclass
class _ResolvedTarget:
    path: Path
    skipped: bool = False


class ExportService:
    """Executes export requests and maintains the export history."""

    def __init__(
        self,
        history_store: HistoryDocumentStore,
        *,
        pdf_composer: PdfComposer | None = None,
    ) -> None:
        self._store = history_store
        self._pdf_composer = pdf_composer

    # ------------------------------------------------------------------
    # execution
    # ------------------------------------------------------------------

    def export(self, request: ExportRequest) -> ExportResult:
        self._validate(request)
        stale_ids, missing_ids = self._stale_scope(request)
        if request.stale_policy is StalePolicy.ABORT and (stale_ids or missing_ids):
            raise StaleExportError(stale_ids, missing_ids)

        created_at = utc_now()
        export_id = f"exp-{uuid.uuid4().hex[:12]}"
        self._check_cancel(request)

        target = self._resolve_target(request)
        result_kwargs = dict(
            export_id=export_id,
            book_id=request.book_id,
            chapter_id=request.chapter_id,
            format=request.format,
            mode=request.mode,
            page_ids=tuple(page.page_id for page in request.pages),
            included_stale_page_ids=stale_ids,
            included_missing_page_ids=missing_ids,
        )

        if target.skipped:
            # skip policy never touches the existing file.
            if request.overwrite_policy is OverwritePolicy.SKIP:
                result = ExportResult(
                    status=ExportStatus.SKIPPED,
                    output_path=target.path,
                    file_hash=None,
                    completed_at=utc_now(),
                    **result_kwargs,
                )
                self._record(request, result, created_at, scope=None, detail="目标文件已存在，按策略跳过")
                return result

        temp_path: Path | None = None
        try:
            temp_path = _new_temp(target.path)
            file_hash = self._write_content(temp_path, request)
            self._check_cancel(request)
            os.replace(temp_path, target.path)
            temp_path = None
        except ExportCancelledError:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
            result = ExportResult(
                status=ExportStatus.CANCELLED,
                output_path=None,
                file_hash=None,
                completed_at=utc_now(),
                **result_kwargs,
            )
            self._record(request, result, created_at, scope=None, detail="用户取消")
            raise
        except BaseException as error:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
            result = ExportResult(
                status=ExportStatus.FAILED,
                output_path=None,
                file_hash=None,
                completed_at=utc_now(),
                **result_kwargs,
            )
            self._record(request, result, created_at, scope=None, detail=f"{type(error).__name__}: {error}")
            raise

        result = ExportResult(
            status=ExportStatus.COMPLETED,
            output_path=target.path,
            file_hash=file_hash,
            completed_at=utc_now(),
            **result_kwargs,
        )
        self._record(request, result, created_at, scope=_scope_snapshot(request))
        return result

    # ------------------------------------------------------------------
    # history (D03 §31 / AC-EXPORT-002 / D04 §37)
    # ------------------------------------------------------------------

    def history(self) -> list[ExportRecord]:
        """All recorded exports, most recent first."""
        rows = list(self._store.read())
        rows.sort(key=lambda row: str(row.get("created_at", "")), reverse=True)
        return [_record_from_row(row) for row in rows]

    def find_export(self, export_id: str) -> ExportRecord | None:
        for record in self.history():
            if record.export_id == export_id:
                return record
        return None

    def repeat(
        self,
        export_id: str,
        pages_by_id: dict[str, ExportPage],
        *,
        overwrite_policy: OverwritePolicy | None = None,
        stale_policy: StalePolicy | None = None,
        cancel: Callable[[], bool] | None = None,
    ) -> ExportResult:
        """使用相同设置再次导出 (D03 §31 / D04 §37).

        Rebuilds the request from the stored scope snapshot; page bytes
        come fresh from ``pages_by_id`` (providers are never persisted).
        """
        record = self.find_export(export_id)
        if record is None:
            raise ExportError(f"unknown export: {export_id!r}")
        scope = _parse_scope(record.scope_snapshot_json)
        missing = [page_id for page_id in scope["page_ids"] if page_id not in pages_by_id]
        if missing:
            raise ExportError(f"pages missing for repeat: {', '.join(missing)}")
        request = ExportRequest(
            book_id=record.book_id,
            chapter_id=record.chapter_id,
            format=ExportFormat(record.export_type),
            output_path=Path(record.output_path),
            pages=tuple(pages_by_id[page_id] for page_id in scope["page_ids"]),
            mode=scope["mode"],
            overwrite_policy=overwrite_policy or OverwritePolicy(scope["overwrite_policy"]),
            stale_policy=stale_policy or StalePolicy(scope["stale_policy"]),
            pipeline_run_id=record.pipeline_run_id,
            render_profile_snapshot=_parse_optional_object(record.render_profile_snapshot_json),
            cancel=cancel,
        )
        return self.export(request)

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _validate(self, request: ExportRequest) -> None:
        if not request.pages:
            raise ExportValidationError("export scope is empty")
        if request.format is ExportFormat.SINGLE_IMAGE and len(request.pages) != 1:
            raise ExportValidationError("single_image export requires exactly one page")
        if request.mode not in ("original", "translated"):
            raise ExportValidationError(f"unknown export mode: {request.mode!r}")
        for page in request.pages:
            _safe_entry_name(page.filename)

    def _stale_scope(self, request: ExportRequest) -> tuple[tuple[str, ...], tuple[str, ...]]:
        if request.mode != "translated":
            return (), ()
        stale = tuple(page.page_id for page in request.pages if page.stale)
        missing = tuple(
            page.page_id for page in request.pages if page.translated_provider is None
        )
        return stale, missing

    def _resolve_target(self, request: ExportRequest) -> _ResolvedTarget:
        target = Path(request.output_path)
        if not target.name:
            raise ExportValidationError(f"output path has no filename: {target}")
        if target.is_dir():
            raise ExportValidationError(f"output path is a directory: {target}")
        if not target.exists():
            return _ResolvedTarget(target)
        if request.overwrite_policy is OverwritePolicy.SKIP:
            return _ResolvedTarget(target, skipped=True)
        if request.overwrite_policy is OverwritePolicy.AUTO_RENAME:
            return _ResolvedTarget(_next_free_name(target))
        return _ResolvedTarget(target)

    def _write_content(self, temp: Path, request: ExportRequest) -> str:
        """Write export content into ``temp``; return the file's SHA-256."""
        if request.format in (ExportFormat.ZIP, ExportFormat.CBZ):
            self._write_archive(temp, request)
            return _hash_file(temp)
        payload = self._build_payload(request)
        temp.write_bytes(payload)
        return hashlib.sha256(payload).hexdigest()

    def _write_archive(self, temp: Path, request: ExportRequest) -> None:
        compression = (
            zipfile.ZIP_STORED if request.format is ExportFormat.CBZ else zipfile.ZIP_DEFLATED
        )
        with zipfile.ZipFile(temp, "w", compression=compression) as archive:
            for order, page in enumerate(request.pages, start=1):
                self._check_cancel(request)
                entry = f"{order:04d}_{_safe_entry_name(page.filename)}"
                # UTF-8 filenames are the zipfile default flag; Unicode
                # page names round-trip (Unicode 文件名 requirement).
                archive.writestr(entry, page.provider_for(request.mode)())

    def _build_payload(self, request: ExportRequest) -> bytes:
        if request.format is ExportFormat.SINGLE_IMAGE:
            return request.pages[0].provider_for(request.mode)()
        if request.format is ExportFormat.TEXT:
            blocks = [
                f"【{page.filename}】\n{page.text}".rstrip() for page in request.pages
            ]
            return ("\n\n".join(blocks) + "\n").encode("utf-8")
        if request.format is ExportFormat.PDF:
            if self._pdf_composer is None:
                raise PdfUnavailableError(
                    "PDF export requires a PdfComposer (e.g. pdf_qt.QtImagePdfComposer)"
                )
            images = [page.provider_for(request.mode)() for page in request.pages]
            return self._pdf_composer.compose(images)
        raise ExportValidationError(f"unsupported format: {request.format!r}")

    @staticmethod
    def _check_cancel(request: ExportRequest) -> None:
        if request.cancel is not None and request.cancel():
            raise ExportCancelledError("export cancelled by caller")

    def _record(
        self,
        request: ExportRequest,
        result: ExportResult,
        created_at: str,
        *,
        scope: str | None,
        detail: str = "",
    ) -> None:
        """Append one history row; persistence is best-effort in every
        terminal state. A history write failure (e.g. disk full) is
        swallowed: the output file itself is already committed and must
        not be reported as failed, and a missing history row never makes
        an export result wrong (repeat simply cannot replay it)."""
        try:
            rows = self._store.read()
            rows.append(
                {
                    "export_id": result.export_id,
                    "book_id": result.book_id,
                    "chapter_id": result.chapter_id,
                    "pipeline_run_id": request.pipeline_run_id,
                    "export_type": result.format.value,
                    "scope_snapshot_json": scope or _scope_snapshot(request) or "{}",
                    "output_path": str(result.output_path or request.output_path),
                    "render_profile_snapshot_json": _dump_json(
                        request.render_profile_snapshot
                    ),
                    "status": result.status.value,
                    "file_hash": result.file_hash or "",
                    "created_at": created_at,
                    "completed_at": result.completed_at,
                    "detail": detail,
                }
            )
            self._store.write(rows)
        except Exception:
            # best-effort in every state (R-005): never mask the real
            # export outcome, whatever it was.
            return


def _scope_snapshot(request: ExportRequest) -> str:
    import json

    return json.dumps(
        {
            "page_ids": [page.page_id for page in request.pages],
            "filenames": [page.filename for page in request.pages],
            "mode": request.mode,
            "overwrite_policy": request.overwrite_policy.value,
            "stale_policy": request.stale_policy.value,
        },
        ensure_ascii=False,
    )


def _parse_scope(snapshot_json: str) -> dict:
    import json

    try:
        value = json.loads(snapshot_json)
    except ValueError as error:
        raise ExportError(f"corrupt export scope snapshot: {error}") from error
    if not isinstance(value, dict) or not isinstance(value.get("page_ids"), list):
        raise ExportError("corrupt export scope snapshot")
    return value


def _parse_optional_object(snapshot_json: str) -> dict | None:
    import json

    if not snapshot_json:
        return None
    try:
        value = json.loads(snapshot_json)
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


def _dump_json(value: dict | None) -> str:
    import json

    return json.dumps(value, ensure_ascii=False) if value else ""


def _record_from_row(row: dict) -> ExportRecord:
    return ExportRecord(
        export_id=str(row.get("export_id", "")),
        book_id=str(row.get("book_id", "")),
        chapter_id=str(row.get("chapter_id", "")),
        pipeline_run_id=row.get("pipeline_run_id"),
        export_type=str(row.get("export_type", "")),
        scope_snapshot_json=str(row.get("scope_snapshot_json", "")),
        output_path=str(row.get("output_path", "")),
        render_profile_snapshot_json=str(row.get("render_profile_snapshot_json", "")),
        status=str(row.get("status", "")),
        file_hash=str(row.get("file_hash", "")),
        created_at=str(row.get("created_at", "")),
        completed_at=str(row.get("completed_at", "")),
        detail=str(row.get("detail", "")),
    )


def _safe_entry_name(filename: str) -> str:
    """Windows-safe archive entry name (Unicode preserved).

    Strips any directory components (path traversal), rejects empty names
    and replaces characters Windows cannot store in file names, so the
    archive unpacks cleanly on the product platform.
    """
    name = Path(filename).name.strip()
    if not name:
        raise ExportValidationError(f"invalid page filename: {filename!r}")
    cleaned = "".join(
        "_" if char in '<>:"/\\|?*' or ord(char) < 32 else char for char in name
    ).strip()
    if not cleaned:
        raise ExportValidationError(f"invalid page filename: {filename!r}")
    return cleaned


def _new_temp(target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    os.close(fd)
    return Path(name)


def _next_free_name(target: Path) -> Path:
    """First free ``stem (n)`` sibling; Unicode stems are preserved."""
    stem, suffix = target.stem, target.suffix
    for counter in range(1, 10_000):
        candidate = target.with_name(f"{stem} ({counter}){suffix}")
        if not candidate.exists():
            return candidate
    raise ExportError(f"no free auto-rename slot for {target}")


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
