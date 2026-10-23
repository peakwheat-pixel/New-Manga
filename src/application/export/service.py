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
import json
import os
import tempfile
import threading
import uuid
import zipfile
from collections.abc import Callable, Sequence
from contextlib import nullcontext
from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path
from typing import ContextManager

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
    rendered_from_revision_id: str | None = None
    current_source_revision_id: str | None = None
    regions: tuple[dict, ...] = ()
    sha256: str | None = None
    artifact_id: str | None = None
    artifact_revision_id: str | None = None
    source_run_id: str | None = None

    @property
    def stale(self) -> bool:
        if self.translated_provider is None:
            return False
        if self.rendered_from_revision_id and self.current_source_revision_id:
            if self.rendered_from_revision_id != self.current_source_revision_id:
                return True
        if self.translated_revision_id and self.current_translated_revision_id:
            if self.translated_revision_id != self.current_translated_revision_id:
                return True
        return False

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
    export_id: str | None = None
    format_options: dict | None = None
    text_content: bytes | None = None
    book_metadata: dict | None = None
    chapter_metadata: dict | None = None
    lineage: tuple[dict, ...] = ()
    on_page_complete: Callable[[str], None] | None = None
    before_publish: Callable[[], None] | None = None
    target_context: Callable[[], ContextManager] | None = None
    publish_temp: Callable[[Path, Path], None] | None = None
    image_encoder: Callable[[bytes], bytes] | None = None
    text_content_factory: Callable[[dict], bytes] | None = None
    hooks_prepared: bool = False


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
        plugins=None,
    ) -> None:
        self._plugins = plugins
        self._store = history_store
        self._pdf_composer = pdf_composer

    # ------------------------------------------------------------------
    # execution
    # ------------------------------------------------------------------

    def prepare_request(self, request: ExportRequest) -> ExportRequest:
        if request.hooks_prepared:
            return request
        if self._plugins is not None:
            def validate(candidate):
                if not isinstance(candidate["format_options"], dict):
                    raise ValueError("format_options must be an object")
                options = candidate["format_options"]
                allowed = {
                    ExportFormat.ZIP: ("compression", ("standard", "fast", "store")),
                    ExportFormat.PDF: ("pdf_content", ("image_only", "searchable_dual_layer")),
                    ExportFormat.TEXT: ("text_representation", ("txt", "json", "markdown")),
                }.get(request.format)
                if options and (allowed is None or set(options) != {allowed[0]}
                                or options[allowed[0]] not in allowed[1]):
                    raise ValueError("unsupported format options")
                try:
                    self._validate(replace(request, **candidate))
                except ExportError as error:
                    raise ValueError(str(error)) from error
            values = self._plugins.apply_input("before_export", {
                "run_id": request.pipeline_run_id,
                "page_ids": [page.page_id for page in request.pages],
                "input": {"format_options": request.format_options or {}},
            }, validate)
            request = replace(request, **values)
        if request.text_content_factory is not None:
            request = replace(request, text_content=request.text_content_factory(request.format_options or {}))
        return replace(request, hooks_prepared=True)

    def export(self, request: ExportRequest) -> ExportResult:
        request = self.prepare_request(request)
        result = self._export(request)
        if self._plugins is not None:
            self._plugins.run_hook("after_export", {
                "run_id": request.pipeline_run_id, "export_id": result.export_id,
                "status": result.status.value, "page_ids": list(result.page_ids),
            })
        return result

    def _export(self, request: ExportRequest) -> ExportResult:
        self._validate(request)
        stale_ids, missing_ids = self._stale_scope(request)
        if request.stale_policy is StalePolicy.ABORT and (stale_ids or missing_ids):
            raise StaleExportError(stale_ids, missing_ids)

        created_at = utc_now()
        export_id = request.export_id or f"exp-{uuid.uuid4().hex[:12]}"
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
            with request.target_context() if request.target_context else nullcontext():
                temp_path = _new_temp(target.path)
                file_hash = self._write_content(temp_path, request)
                self._check_cancel(request)
                if request.before_publish is not None:
                    request.before_publish()
                if request.publish_temp is None:
                    os.replace(temp_path, target.path)
                else:
                    request.publish_temp(temp_path, target.path)
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
        # The completed record must carry the stale/missing pages CONTINUE
        # actually shipped (D03 §31 lineage): the in-memory result already
        # holds them, so they fold into the persisted scope snapshot here.
        self._record(
            request,
            result,
            created_at,
            scope=_scope_snapshot(
                request,
                included_stale_page_ids=result.included_stale_page_ids,
                included_missing_page_ids=result.included_missing_page_ids,
            ),
        )
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
        compression_name = (request.format_options or {}).get("compression", "standard")
        # Preserve the pre-P16 CBZ behavior for callers outside the Core wire.
        if request.export_id is None and request.format is ExportFormat.CBZ:
            compression = zipfile.ZIP_STORED
        else:
            compression = zipfile.ZIP_STORED if compression_name == "store" else zipfile.ZIP_DEFLATED
        compresslevel = 1 if compression_name == "fast" else None
        with zipfile.ZipFile(temp, "w", compression=compression, compresslevel=compresslevel) as archive:
            for order, page in enumerate(request.pages, start=1):
                self._check_cancel(request)
                entry = f"{order:04d}_{_safe_entry_name(page.filename)}"
                # UTF-8 filenames are the zipfile default flag; Unicode
                # page names round-trip (Unicode 文件名 requirement).
                archive.writestr(entry, page.provider_for(request.mode)())
                if request.on_page_complete is not None:
                    request.on_page_complete(page.page_id)
            if request.export_id is not None and request.format is ExportFormat.ZIP:
                manifest = {
                    "pages": [
                        {"page_id": page.page_id, "order": i,
                         "filename": f"{i:04d}_{_safe_entry_name(page.filename)}",
                         "sha256": page.sha256}
                        for i, page in enumerate(request.pages, start=1)
                    ],
                    "lineage": list(request.lineage),
                }
                archive.writestr(
                    "manifest.json",
                    json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"),
                )
            elif request.export_id is not None and request.format is ExportFormat.CBZ:
                archive.writestr("ComicInfo.xml", _comic_info_xml(request).encode("utf-8"))

    def _build_payload(self, request: ExportRequest) -> bytes:
        if request.format is ExportFormat.SINGLE_IMAGE:
            payload = request.pages[0].provider_for(request.mode)()
            if request.on_page_complete is not None:
                request.on_page_complete(request.pages[0].page_id)
            return request.image_encoder(payload) if request.image_encoder else payload
        if request.format is ExportFormat.TEXT:
            if request.on_page_complete is not None:
                for page in request.pages:
                    request.on_page_complete(page.page_id)
            if request.text_content is not None:
                return request.text_content
            blocks = [
                f"【{page.filename}】\n{page.text}".rstrip() for page in request.pages
            ]
            return ("\n\n".join(blocks) + "\n").encode("utf-8")
        if request.format is ExportFormat.PDF:
            if self._pdf_composer is None:
                raise PdfUnavailableError(
                    "PDF export requires a PdfComposer (e.g. pdf_qt.QtImagePdfComposer)"
                )
            images = []
            for page in request.pages:
                images.append(page.provider_for(request.mode)())
                if request.on_page_complete is not None:
                    request.on_page_complete(page.page_id)
            if (request.format_options or {}).get("pdf_content") == "searchable_dual_layer":
                compose_searchable = getattr(self._pdf_composer, "compose_searchable", None)
                if compose_searchable is None:
                    raise PdfUnavailableError("searchable PDF composer is unavailable")
                return compose_searchable(images, [page.regions for page in request.pages])
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


def _scope_snapshot(
    request: ExportRequest,
    *,
    included_stale_page_ids: tuple[str, ...] | list[str] = (),
    included_missing_page_ids: tuple[str, ...] | list[str] = (),
) -> str:
    import json

    snapshot = {
        "page_ids": [page.page_id for page in request.pages],
        "filenames": [page.filename for page in request.pages],
        "mode": request.mode,
        "overwrite_policy": request.overwrite_policy.value,
        "stale_policy": request.stale_policy.value,
        # Which stale/missing pages CONTINUE shipped (M2-FIX-EXPORT-LINEAGE
        # plan A); empty for scopes that never continued past a refusal.
        "included_stale_page_ids": list(included_stale_page_ids),
        "included_missing_page_ids": list(included_missing_page_ids),
    }
    if request.export_id is not None:
        snapshot.update({
            "chapter_ids": list(request.chapter_metadata.get("chapter_ids", ())) if request.chapter_metadata else [request.chapter_id],
            "format_options": request.format_options or {},
            "lineage": list(request.lineage),
        })
    return json.dumps(snapshot, ensure_ascii=False)


def _parse_scope(snapshot_json: str) -> dict:
    import json

    try:
        value = json.loads(snapshot_json)
    except ValueError as error:
        raise ExportError(f"corrupt export scope snapshot: {error}") from error
    if not isinstance(value, dict) or not isinstance(value.get("page_ids"), list):
        raise ExportError("corrupt export scope snapshot")
    # Rows written before included ids were persisted (and refusals) carry
    # neither key: default to an empty list, never crash or fabricate.
    # A non-list value means the snapshot is corrupt, not empty.
    for key in ("included_stale_page_ids", "included_missing_page_ids"):
        included = value.setdefault(key, [])
        if not isinstance(included, list):
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


def _remove_staging_file(target_path: str, staging_path: str) -> None:
    target = Path(target_path)
    staging = Path(staging_path)
    try:
        if (
            os.path.normcase(str(staging.parent.resolve(strict=True)))
            == os.path.normcase(str(target.parent.resolve(strict=True)))
            and staging.name.startswith(f".{target.name}.")
            and staging.name.endswith(".tmp")
            and staging.is_file()
            and not staging.is_symlink()
        ):
            staging.unlink()
    except OSError:
        return


def _comic_info_xml(request: ExportRequest) -> str:
    import xml.etree.ElementTree as ET

    book = request.book_metadata or {}
    chapter = request.chapter_metadata or {}
    root = ET.Element("ComicInfo")
    for key, value in (
        ("Series", book.get("title")), ("Title", chapter.get("title")),
        ("Number", chapter.get("chapter_number")), ("Writer", book.get("author")),
        ("Summary", book.get("description")),
    ):
        if value:
            ET.SubElement(root, key).text = str(value)
    pages = ET.SubElement(root, "Pages")
    for index, _page in enumerate(request.pages):
        ET.SubElement(pages, "Page", Image=str(index), Type="Story")
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(root, encoding="unicode")


class P16ExportRuntime:
    """Durable progress/event wrapper around the existing atomic exporter."""

    def __init__(self, exporter, history_store, job_store, event_sink=None) -> None:
        self._exporter = exporter
        self._history_store = history_store
        self._job_store = job_store
        self._event_sink = event_sink
        self._lock = threading.RLock()
        self._jobs = list(job_store.read())
        self._cancel: dict[str, threading.Event] = {}
        self._threads: dict[str, threading.Thread] = {}
        changed = False
        for job in self._jobs:
            snapshot = job.get("snapshot", {})
            if snapshot.get("status") in ("pending", "running"):
                intent = job.get("publication_intent")
                recovered = False
                if isinstance(intent, dict):
                    path = Path(str(intent.get("path", "")))
                    expected_hash = intent.get("sha256")
                    try:
                        recovered = bool(path.is_file() and _hash_file(path) == expected_hash)
                    except OSError:
                        recovered = False
                if recovered:
                    output = {
                        "format": job.get("history", {}).get("format", "text"),
                        "output_path": str(path), "sha256": expected_hash,
                    }
                    snapshot.update(status="publishing", current_page_id=None, output=output)
                    job["history"].update(status="publishing", output_path=str(path), sha256=expected_hash)
                else:
                    snapshot.update(status="failed", completed_at=utc_now(), error_code="EXPORT_WRITE_FAILED")
                    job.get("history", {})["status"] = "failed"
                    job["history"]["completed_at"] = snapshot["completed_at"]
                    staging = intent.get("staging_path") if isinstance(intent, dict) else None
                    if staging:
                        _remove_staging_file(job.get("target_path_internal", ""), staging)
                changed = True
        if changed:
            self._job_store.write(self._jobs)

    def start(self, request: ExportRequest, target) -> dict:
        if isinstance(self._exporter, ExportService):
            request = self._exporter.prepare_request(request)
        export_id = request.export_id or f"exp-{uuid.uuid4().hex[:12]}"
        cancel = threading.Event()
        accepted_at = utc_now()
        lineage = list(request.lineage)
        snapshot = {
            "export_id": export_id, "status": "pending", "completed_pages": 0,
            "total_pages": len(request.pages), "current_page_id": None,
            "accepted_at": accepted_at, "completed_at": None, "output": None,
            "lineage": lineage, "error_code": None,
        }
        history = {
            "export_id": export_id, "book_id": request.book_id,
            "chapter_ids": list((request.chapter_metadata or {}).get("chapter_ids", [request.chapter_id])),
            "ordered_page_ids": [page.page_id for page in request.pages],
            "format": "png" if request.format is ExportFormat.SINGLE_IMAGE else request.format.value,
            "format_options": request.format_options or {},
            "created_at": accepted_at, "completed_at": None,
            "output_path": str(target.path), "status": "pending", "sha256": None,
            "lineage": lineage, "stale_policy": request.stale_policy.value,
        }
        with self._lock:
            job = {"snapshot": snapshot, "history": history, "target_path_internal": str(target.path)}
            self._jobs.append(job)
            self._job_store.write(self._jobs)
            self._cancel[export_id] = cancel
            request = replace(
                request, export_id=export_id, cancel=cancel.is_set,
                on_page_complete=lambda page_id: self._page_completed(export_id, page_id),
                before_publish=lambda: self._check_before_publish(cancel),
                target_context=target.hold_parent,
                publish_temp=lambda temp, _target: self._publish_and_mark(export_id, temp, target, cancel),
            )
            thread = threading.Thread(
                target=self._run, args=(export_id, request, cancel),
                name=f"core-export-{export_id}", daemon=True,
            )
            self._threads[export_id] = thread
            thread.start()
        return {
            "export_id": export_id, "status": "pending", "accepted_at": accepted_at,
            "book_id": request.book_id, "chapter_ids": history["chapter_ids"],
            "ordered_page_ids": history["ordered_page_ids"],
            "format": history["format"], "format_options": history["format_options"],
            "lineage": lineage,
        }

    def snapshot(self, export_id: str) -> dict:
        self._reconcile(export_id)
        with self._lock:
            job = self._find(export_id)
            if job is None:
                raise KeyError(export_id)
            return dict(job["snapshot"])

    def cancel(self, export_id: str) -> dict:
        with self._lock:
            job = self._find(export_id)
            if job is None:
                raise KeyError(export_id)
            if job["snapshot"]["status"] in ("pending", "running"):
                event = self._cancel.get(export_id)
                if event is not None:
                    event.set()
            return dict(job["snapshot"])

    def history(self) -> list[dict]:
        with self._lock:
            publishing_ids = [
                job["snapshot"]["export_id"] for job in self._jobs
                if job.get("snapshot", {}).get("status") == "publishing"
            ]
        for export_id in publishing_ids:
            self._reconcile(export_id)
        with self._lock:
            by_id = {job["history"]["export_id"]: dict(job["history"]) for job in self._jobs}
        for row in self._history_store.read():
            export_id = str(row.get("export_id", ""))
            if not export_id or export_id in by_id:
                continue
            try:
                scope = json.loads(row.get("scope_snapshot_json") or "{}")
            except (TypeError, ValueError):
                scope = {}
            by_id[export_id] = {
                "export_id": export_id, "book_id": str(row.get("book_id", "")),
                "book_title": str(scope.get("book_title", "")),
                "chapter_ids": scope.get("chapter_ids", [str(row.get("chapter_id", ""))]),
                "ordered_page_ids": scope.get("page_ids", []),
                "format": "png" if row.get("export_type") == "single_image" else row.get("export_type", "text"),
                "format_options": scope.get("format_options", {}),
                "created_at": row.get("created_at"),
                "completed_at": row.get("completed_at") or None,
                "output_path": row.get("output_path", ""), "status": row.get("status", "failed"),
                "sha256": row.get("file_hash") or None, "lineage": scope.get("lineage", []),
            }
        return sorted(by_id.values(), key=lambda entry: str(entry.get("created_at", "")), reverse=True)

    def has_active_exports_for_book(self, book_id: str) -> bool:
        with self._lock:
            for job in self._jobs:
                history = job.get("history", {})
                if history.get("book_id") == book_id:
                    status = job.get("snapshot", {}).get("status")
                    if status in ("pending", "running", "publishing"):
                        return True
        return False


    def _run(self, export_id: str, request: ExportRequest, cancel: threading.Event) -> None:
        try:
            self._change(export_id, status="running", current_page_id=request.pages[0].page_id)
            result = self._exporter.export(request)
            if result.output_path is None or result.file_hash is None or not result.output_path.is_file():
                self._leave_publishing(export_id, request, result)
                return
            if _hash_file(result.output_path) != result.file_hash:
                self._leave_publishing(export_id, request, result)
                return
            record = next((row for row in self._history_store.read() if row.get("export_id") == export_id), None)
            if not self._history_matches(record, result):
                self._change(
                    export_id, status="publishing", current_page_id=None,
                    output={"format": "png" if request.format is ExportFormat.SINGLE_IMAGE else request.format.value,
                            "output_path": str(result.output_path), "sha256": result.file_hash},
                )
                try:
                    self._ensure_history(request, result)
                except Exception:
                    return
                record = next((row for row in self._history_store.read() if row.get("export_id") == export_id), None)
                if not self._history_matches(record, result):
                    return
            self._change(
                export_id, status="completed", completed_pages=len(request.pages),
                current_page_id=None, completed_at=result.completed_at,
                output={"format": "png" if request.format is ExportFormat.SINGLE_IMAGE else request.format.value,
                        "output_path": str(result.output_path), "sha256": result.file_hash},
                error_code=None,
            )
        except ExportCancelledError:
            self._change(export_id, status="cancelled", current_page_id=None,
                         completed_at=utc_now(), error_code=None)
        except Exception:
            with self._lock:
                job = self._find(export_id)
                if job is not None and job["snapshot"].get("status") == "publishing":
                    return
            self._change(export_id, status="failed", current_page_id=None,
                         completed_at=utc_now(), error_code="EXPORT_WRITE_FAILED")
        finally:
            with self._lock:
                self._cancel.pop(export_id, None)
                self._threads.pop(export_id, None)

    def _page_completed(self, export_id: str, page_id: str) -> None:
        with self._lock:
            job = self._find(export_id)
            if job is None:
                return
            count = min(job["snapshot"]["completed_pages"] + 1, job["snapshot"]["total_pages"])
        current = None
        self._change(export_id, completed_pages=count, current_page_id=current)

    @staticmethod
    def _check_before_publish(cancel: threading.Event) -> None:
        if cancel.is_set():
            raise ExportCancelledError("export cancelled before publication")

    def _publish_and_mark(self, export_id: str, temp: Path, target, cancel: threading.Event) -> None:
        # Serialize the last cancellation check, atomic replace and durable
        # publishing snapshot so CancelExport observes exactly one side of
        # the publication boundary.
        with self._lock:
            if cancel.is_set():
                raise ExportCancelledError("export cancelled before publication")
            job = self._find(export_id)
            if job is None:
                raise RuntimeError("export job disappeared before publication")
            expected_hash = _hash_file(temp)
            job["publication_intent"] = {
                "path": str(target.path), "sha256": expected_hash,
                "staging_path": str(temp),
            }
            self._job_store.write(self._jobs)
            target.publish(temp)
            output = job["history"]
            fmt = output["format"]
            snapshot = job["snapshot"]
            snapshot.update(
                status="publishing", current_page_id=None,
                output={"format": fmt, "output_path": str(target.path), "sha256": expected_hash},
            )
            output["status"] = "publishing"
            output["output_path"] = str(target.path)
            output["sha256"] = snapshot["output"]["sha256"]
            self._job_store.write(self._jobs)
            event = {
                "export_id": export_id, "status": "publishing",
                "completed_pages": snapshot["completed_pages"],
                "total_pages": snapshot["total_pages"],
            }
        if self._event_sink is not None:
            try:
                self._event_sink(event)
            except Exception:
                pass

    def _leave_publishing(self, export_id: str, request: ExportRequest, result: ExportResult) -> None:
        if result.output_path is None or result.file_hash is None:
            return
        self._change(
            export_id, status="publishing", current_page_id=None,
            output={"format": "png" if request.format is ExportFormat.SINGLE_IMAGE else request.format.value,
                    "output_path": str(result.output_path), "sha256": result.file_hash},
        )

    @staticmethod
    def _history_matches(record: dict | None, result: ExportResult) -> bool:
        return bool(
            record is not None and record.get("status") == "completed"
            and record.get("file_hash") == result.file_hash
            and os.path.normcase(str(record.get("output_path", "")))
            == os.path.normcase(str(result.output_path))
        )

    def _change(self, export_id: str, **changes) -> None:
        with self._lock:
            job = self._find(export_id)
            if job is None:
                return
            previous_snapshot = dict(job["snapshot"])
            if isinstance(previous_snapshot.get("output"), dict):
                previous_snapshot["output"] = dict(previous_snapshot["output"])
            previous_history = dict(job["history"])
            job["snapshot"].update(changes)
            job["history"]["status"] = job["snapshot"]["status"]
            job["history"]["completed_at"] = job["snapshot"].get("completed_at")
            output = job["snapshot"].get("output")
            if output:
                job["history"]["output_path"] = output["output_path"]
                job["history"]["sha256"] = output["sha256"]
            try:
                self._job_store.write(self._jobs)
            except Exception:
                job["snapshot"].clear()
                job["snapshot"].update(previous_snapshot)
                job["history"].clear()
                job["history"].update(previous_history)
                raise
            event = {
                "export_id": export_id, "status": job["snapshot"]["status"],
                "completed_pages": job["snapshot"]["completed_pages"],
                "total_pages": job["snapshot"]["total_pages"],
            }
        if self._event_sink is not None:
            try:
                self._event_sink(event)
            except Exception:
                pass

    def _ensure_history(self, request: ExportRequest, result: ExportResult) -> None:
        rows = list(self._history_store.read())
        scope = {
            "page_ids": [page.page_id for page in request.pages],
            "filenames": [page.filename for page in request.pages], "mode": "translated",
            "overwrite_policy": "overwrite", "stale_policy": request.stale_policy.value,
            "chapter_ids": list((request.chapter_metadata or {}).get("chapter_ids", [request.chapter_id])),
            "format_options": request.format_options or {}, "lineage": list(request.lineage),
        }
        rows.append({
            "export_id": result.export_id, "book_id": result.book_id,
            "chapter_id": result.chapter_id, "pipeline_run_id": request.pipeline_run_id,
            "export_type": result.format.value, "scope_snapshot_json": json.dumps(scope, ensure_ascii=False),
            "output_path": str(result.output_path), "render_profile_snapshot_json": "",
            "status": "completed", "file_hash": result.file_hash,
            "created_at": self._find(result.export_id)["history"]["created_at"],
            "completed_at": result.completed_at, "detail": "",
        })
        self._history_store.write(rows)

    def _reconcile(self, export_id: str) -> None:
        with self._lock:
            job = self._find(export_id)
            if job is None or job["snapshot"]["status"] != "publishing":
                return
            output = job["snapshot"].get("output")
            if not output:
                return
            output_path = Path(output.get("output_path", ""))
            expected_hash = output.get("sha256")
        try:
            if not output_path.is_file() or _hash_file(output_path) != expected_hash:
                return
        except OSError:
            return
        rows = list(self._history_store.read())
        existing = next((row for row in rows if row.get("export_id") == export_id and row.get("status") == "completed"), None)
        if not self._history_matches_output(existing, output):
            try:
                self._ensure_history_from_job(job, output)
            except Exception:
                return
            rows = list(self._history_store.read())
            existing = next((row for row in rows if row.get("export_id") == export_id and row.get("status") == "completed"), None)
            if not self._history_matches_output(existing, output):
                return
        self._change(export_id, status="completed", completed_at=existing.get("completed_at"), error_code=None)

    @staticmethod
    def _history_matches_output(record: dict | None, output: dict) -> bool:
        return bool(
            record is not None and record.get("status") == "completed"
            and record.get("file_hash") == output.get("sha256")
            and os.path.normcase(str(record.get("output_path", "")))
            == os.path.normcase(str(output.get("output_path", "")))
        )

    def _ensure_history_from_job(self, job: dict, output: dict) -> None:
        history = job["history"]
        fmt = history["format"]
        scope = {
            "page_ids": history["ordered_page_ids"], "mode": "translated",
            "overwrite_policy": "overwrite", "stale_policy": history.get("stale_policy", "abort"),
            "chapter_ids": history["chapter_ids"], "format_options": history["format_options"],
            "lineage": history["lineage"],
        }
        rows = list(self._history_store.read())
        rows = [row for row in rows if row.get("export_id") != history["export_id"]]
        rows.append({
            "export_id": history["export_id"], "book_id": history["book_id"],
            "chapter_id": history["chapter_ids"][0], "pipeline_run_id": None,
            "export_type": "single_image" if fmt == "png" else fmt,
            "scope_snapshot_json": json.dumps(scope, ensure_ascii=False),
            "output_path": output["output_path"], "render_profile_snapshot_json": "",
            "status": "completed", "file_hash": output["sha256"],
            "created_at": history["created_at"], "completed_at": utc_now(), "detail": "",
        })
        self._history_store.write(rows)

    def _find(self, export_id: str) -> dict | None:
        return next((job for job in self._jobs if job.get("snapshot", {}).get("export_id") == export_id), None)
