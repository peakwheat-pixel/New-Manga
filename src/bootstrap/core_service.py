"""Production Core Service (M2-IPC1).

The host spawns this module -- ``python -m bootstrap.core_service`` -- as the
production Core sidecar process. It assembles the production Core services
(migrations, repositories, managed storage, startup recover_running_runs),
then enters a stdio request loop serving typed commands over JSON-lines.

Transport & Envelope (Contract 1.1 §3, §8, §12; Seam 冻结七条):
  Request:
    {"protocol": "new-manga.core", "version": {"major": 1, "minor": 0},
     "request_id": "<id>", "command": "<cmd>", "payload": {...}}
  Response:
    {"protocol": "new-manga.core", "version": {"major": 1, "minor": 0},
     "request_id": "<id>", "result": {...} | null, "error": ErrorEnvelope | null}

Allowed production commands (M2-IPC1):
  - core.ping: {} -> {"status": "ready", "protocol_version": {"major": 1, "minor": 0}, "capabilities": ["library.list_books"]}
  - ListBooks: {} -> BookSummary[]
  - core.shutdown: {} -> {"status": "stopped"} (then exit 0)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import sqlite3
import sys
from typing import Any, Callable, TextIO

from application.importing.images.ports import DecodedImage
from application.translation.color.service import SourceStyleService
from bootstrap.core_assembly import (
    CoreServices,
    assemble_core_services,
    default_data_root,
)

PROTOCOL_NAME = "new-manga.core"
PROTOCOL_MAJOR = 1
PROTOCOL_MINOR = 0

# Typed error codes per Contract 1.1 §3, §8
E_PROTOCOL_VERSION_UNSUPPORTED = "PROTOCOL_VERSION_UNSUPPORTED"
E_UNKNOWN_COMMAND = "UNKNOWN_COMMAND"
E_LIST_BOOKS_FAILED = "LIST_BOOKS_FAILED"
E_UNKNOWN = "UNKNOWN"


class _PassthroughImageDecoder:
    def decode(self, payload: bytes) -> DecodedImage:
        del payload
        return DecodedImage(width=1, height=1, format="rgb")


class _StubStyleAnalyzer:
    def analyze_pixel_styles(self, image: Any) -> list[Any]:
        del image
        return []


def assemble_production_core(data_root: Path | None = None) -> CoreServices:
    """Assemble production Core services on the given or default data root.

    Runs database migrations, initializes repositories and managed copy layout,
    and runs startup ``recover_running_runs()``. Uses lightweight headless adapters
    so the service starts reliably in headless sidecar environments without
    requiring a display server.
    """
    if data_root is None:
        data_root = default_data_root()

    db_path = data_root / "library.db"
    managed_root = data_root / "managed"

    # Assemble Qt-free Core services with headless stubs
    core = assemble_core_services(
        db_path,
        managed_root,
        image_decoder=_PassthroughImageDecoder(),
        font_catalog=object(),  # type: ignore[arg-type]
        layout_engine=object(),  # type: ignore[arg-type]
        compositor=object(),  # type: ignore[arg-type]
        source_styles=SourceStyleService(_StubStyleAnalyzer()),
    )
    return core


def make_error_envelope(
    code: str,
    category: str,
    message: str,
    retryable: bool = False,
    details: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "code": code,
        "category": category,
        "message": message,
        "retryable": retryable,
    }
    if details is not None:
        envelope["details"] = details
    return envelope


@dataclass(frozen=True)
class BookSummaryDto:
    book_id: str
    title: str
    original_title: str
    is_favorite: bool
    is_archived: bool
    page_count: int
    created_at: str
    updated_at: str


class CoreServiceServer:
    """Stdio JSON-lines RPC server for the production Core."""

    def __init__(
        self,
        core: CoreServices,
        *,
        stdin: TextIO | None = None,
        stdout: TextIO | None = None,
    ) -> None:
        self._core = core
        self._stdin = stdin or sys.stdin
        self._stdout = stdout or sys.stdout

    def handle_ping(self, payload: dict[str, Any]) -> dict[str, Any]:
        del payload
        return {
            "status": "ready",
            "protocol_version": {
                "major": PROTOCOL_MAJOR,
                "minor": PROTOCOL_MINOR,
            },
            "capabilities": ["library.list_books"],
        }

    def handle_list_books(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        del payload
        books = self._core.library.list_books()

        # Query page counts per book from SQLite read-only
        page_counts = self._fetch_page_counts()

        summaries: list[dict[str, Any]] = []
        for book in books:
            dto = BookSummaryDto(
                book_id=book.book_id,
                title=book.title,
                original_title=book.original_title,
                is_favorite=bool(book.is_favorite),
                is_archived=bool(book.is_archived),
                page_count=page_counts.get(book.book_id, 0),
                created_at=book.created_at,
                updated_at=book.updated_at,
            )
            summaries.append(asdict(dto))
        return summaries

    def _fetch_page_counts(self) -> dict[str, int]:
        """Read-only query calculating valid non-deleted page counts per book."""
        rows = self._core.conn.execute(
            """
            SELECT c.book_id, COUNT(p.page_id) AS cnt
            FROM chapters c
            JOIN pages p ON p.chapter_id = c.chapter_id
            WHERE c.deleted_at IS NULL
              AND p.deleted_at IS NULL
              AND p.source_hash IS NOT NULL
              AND p.managed_original_ref IS NOT NULL
              AND p.width IS NOT NULL
              AND p.height IS NOT NULL
            GROUP BY c.book_id
            """
        ).fetchall()
        return {row["book_id"]: int(row["cnt"]) for row in rows}

    def dispatch_request(self, raw_line: str) -> tuple[dict[str, Any], bool]:
        """Dispatch a single raw json request line.

        Returns (response_dict, should_exit).
        """
        try:
            req = json.loads(raw_line)
        except json.JSONDecodeError:
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": None,
                    "result": None,
                    "error": make_error_envelope(
                        code="INVALID_JSON",
                        category="validation",
                        message="Request must be a valid JSON object",
                        retryable=False,
                    ),
                },
                False,
            )

        if not isinstance(req, dict):
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": None,
                    "result": None,
                    "error": make_error_envelope(
                        code="INVALID_REQUEST",
                        category="validation",
                        message="Request must be a JSON object",
                        retryable=False,
                    ),
                },
                False,
            )

        request_id = req.get("request_id")
        protocol = req.get("protocol")
        version = req.get("version")
        command = req.get("command")
        payload = req.get("payload") if isinstance(req.get("payload"), dict) else {}

        # Validate protocol name and version (must be dict with integer major == PROTOCOL_MAJOR)
        is_valid_version = (
            isinstance(version, dict)
            and isinstance(version.get("major"), int)
            and not isinstance(version.get("major"), bool)
            and version.get("major") == PROTOCOL_MAJOR
        )
        if protocol != PROTOCOL_NAME or not is_valid_version:
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": request_id,
                    "result": None,
                    "error": make_error_envelope(
                        code=E_PROTOCOL_VERSION_UNSUPPORTED,
                        category="validation",
                        message="Unsupported protocol or version",
                        retryable=False,
                    ),
                },
                False,
            )

        # Dispatch command
        if command == "core.ping":
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": request_id,
                    "result": self.handle_ping(payload),
                    "error": None,
                },
                False,
            )

        if command == "ListBooks":
            try:
                books = self.handle_list_books(payload)
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": books,
                        "error": None,
                    },
                    False,
                )
            except sqlite3.Error:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_LIST_BOOKS_FAILED,
                            category="internal",
                            message="Failed to query library books",
                            retryable=True,
                        ),
                    },
                    False,
                )
            except Exception:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_UNKNOWN,
                            category="internal",
                            message="Failed to list books",
                            retryable=False,
                        ),
                    },
                    False,
                )

        if command == "core.shutdown":
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": request_id,
                    "result": {"status": "stopped"},
                    "error": None,
                },
                True,
            )

        # Unknown command
        return (
            {
                "protocol": PROTOCOL_NAME,
                "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                "request_id": request_id,
                "result": None,
                "error": make_error_envelope(
                    code=E_UNKNOWN_COMMAND,
                    category="validation",
                    message=f"Unknown command: {command!r}",
                    retryable=False,
                ),
            },
            False,
        )

    def serve_forever(self) -> int:
        """Main stdio loop reading requests line by line."""
        for line in self._stdin:
            line = line.strip()
            if not line:
                continue
            response, should_exit = self.dispatch_request(line)
            self._emit(response)
            if should_exit:
                return 0
        return 0

    def _emit(self, payload: dict[str, Any]) -> None:
        self._stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
        self._stdout.flush()


def main() -> int:
    env_root = os.environ.get("NEWMANGA_DATA_ROOT")
    data_root = Path(env_root) if env_root else default_data_root()
    core = assemble_production_core(data_root)
    try:
        server = CoreServiceServer(core)
        return server.serve_forever()
    finally:
        core.conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
