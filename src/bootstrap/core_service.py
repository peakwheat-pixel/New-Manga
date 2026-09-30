"""Production Core Service (M2-IPC1).

The host spawns this module -- ``python -m bootstrap.core_service`` -- as the
production Core sidecar process. It assembles the production Core services
(migrations, repositories, managed storage, startup recover_running_runs),
then enters a stdio request loop serving typed commands over JSON-lines.

Transport & Envelope (Contract 1.1 §3, §8, §12; Seam 冻结七条):
  Request:
    {"protocol": "new-manga.core", "version": {"major": 1, "minor": 1},
     "request_id": "<id>", "command": "<cmd>", "payload": {...}}
  Response:
    {"protocol": "new-manga.core", "version": {"major": 1, "minor": 1},
     "request_id": "<id>", "result": {...} | null, "error": ErrorEnvelope | null}

Allowed production commands (M2-IPC1 + M2-PROD-DETECT-3):
  - core.ping: {} -> {"status": "ready", "protocol_version": {"major": 1, "minor": 1}, "capabilities": ["library.list_books"]}
  - ListBooks: {} -> BookSummary[]
  - core.shutdown: {} -> {"status": "stopped"} (then exit 0)
  - core.detect: {"page": "<base64 PNG/JPEG>", "width": <int>, "height": <int>}
      -> {"candidates": [{"provider_label", "polygon", "reading_order",
        "confidence", "coordinate_space"}...], "elapsed_ms": <int>}
    (M2-PROD-DETECT-3, protocol minor bump 1.0 -> 1.1: a backwards-compatible
    widening per the M2-FIX-LISTBOOKS contract rev 1.2 §5 precedent -- the
    three pre-existing commands behave byte-identically. The handler resolves
    the SAME detector instance the pipeline ``detect`` step uses (assembly
    wired; never a bypass) and passes the provider output straight through:
    anonymous labels only, no business IDs are invented. A page that fails to
    decode, whose declared width/height do not match the decoded pixels, or
    whose payload exceeds 32 MiB fails with the typed INVALID_REQUEST
    envelope; a detector without usable weights fails with the provider's
    own typed error codes (PROVIDER_NOT_CONFIGURED / PROVIDER_DEPENDENCY_MISSING /
    PROVIDER_FAILED / ...). Verification/tooling surface only -- the product
    UI detect path remains the pipeline (apps/** registers nothing new).
"""

from __future__ import annotations

import base64
from dataclasses import asdict, dataclass
import io
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
from typing import Any, Callable, TextIO

from application.importing.images.ports import DecodedImage
from application.translation.color.service import SourceStyleService
from bootstrap.core_assembly import (
    CoreServices,
    assemble_core_services,
    default_data_root,
)
from ports.detection.ports import DetectionRequest
from ports.providers.errors import ProviderError, ProviderNotConfigured

PROTOCOL_NAME = "new-manga.core"
PROTOCOL_MAJOR = 1
# M2-PROD-DETECT-3: 0 -> 1 (minor bump, core.detect command added; backwards
# compatible widening, see the module docstring).
PROTOCOL_MINOR = 1

# Typed error codes per Contract 1.1 §3, §8
E_PROTOCOL_VERSION_UNSUPPORTED = "PROTOCOL_VERSION_UNSUPPORTED"
E_UNKNOWN_COMMAND = "UNKNOWN_COMMAND"
E_LIST_BOOKS_FAILED = "LIST_BOOKS_FAILED"
E_UNKNOWN = "UNKNOWN"
# M2-PROD-DETECT-3: malformed core.detect payload (bad base64, width/height
# missing or mismatched with the decoded pixels, oversized payload). Same
# literal the dispatch loop already uses for a non-object request.
E_INVALID_REQUEST = "INVALID_REQUEST"

#: M2-PROD-DETECT-3: upper bound for one core.detect page, enforced on the
#: DECODED image bytes. The base64-text guard below is derived from it (4
#: base64 chars per 3 bytes) so an oversized request is rejected before any
#: decoding work. One manga page as PNG is a few MiB; 32 MiB leaves generous
#: headroom while keeping a hostile payload from pinning the sidecar.
MAX_DETECT_PAGE_BYTES = 32 * 1024 * 1024
_MAX_DETECT_PAGE_B64_CHARS = ((MAX_DETECT_PAGE_BYTES + 2) // 3) * 4


class DetectRequestError(ValueError):
    """A core.detect payload violates the request contract (INVALID_REQUEST)."""



class _PassthroughImageDecoder:
    def decode(self, payload: bytes) -> DecodedImage:
        del payload
        # mime_type keeps the stub's original "rgb" semantics under the image
        # type, matching the frozen DecodedImage contract (no format= field).
        return DecodedImage(width=1, height=1, mime_type="image/rgb")


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
    # M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN (frozen None channel): None means
    # unknown/missing data (the production COUNT predicate yields no row for
    # this book); a counted value stays an int -- a KNOWN 0 must remain
    # expressible and distinguishable from None after serialization.
    page_count: int | None
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
                # GROUP BY returns rows only for books with >=1 qualifying
                # page: a SQL miss (no chapters / no qualifying pages) is
                # unknown data -> None, never a plausible-looking 0.
                page_count=page_counts.get(book.book_id),
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

    # ------------------------------------------------------------------
    # core.detect (M2-PROD-DETECT-3)
    # ------------------------------------------------------------------

    def handle_detect(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Detect text regions on one page; the provider output passes through.

        The detector is the SAME instance the pipeline ``detect`` step uses --
        the one ``assemble_core_services`` wired into the production handlers
        (manga/doctr backend selection + weights resolution, or the mock
        provider behind ``mock_local_providers``). This handler never builds
        its own provider and never touches the registry directly, so the
        assembly semantics (in-bundle weights fallback, backend env, mock
        mode) are shared verbatim.

        Request validation (typed INVALID_REQUEST, fail-closed before any
        provider is touched):
          - ``page`` must be a base64-encoded PNG/JPEG image;
          - ``width``/``height`` must be positive ints matching the decoded
            pixel size;
          - the decoded payload must not exceed ``MAX_DETECT_PAGE_BYTES``.

        The providers behind ``ports.detection`` consume a RAW pixel buffer
        (rgb24/rgb32, never an encoded file -- their ``_validate_request``
        byte-count gate is the second-line defense and stays untouched), so
        this handler decodes the image (Pillow, a transformers dependency
        already in the frozen closure) into raw RGB bytes. Failure shapes:
          - no detector wired at assembly -> ``PROVIDER_NOT_CONFIGURED`` (the
            same capability-gap slot the pipeline detect step uses);
          - the provider raises -> its typed ``ProviderError.error_code``
            passes through verbatim (e.g. the detect-time
            ``PROVIDER_NOT_CONFIGURED`` of a weights-less install -- ruling 5
            of M2-PROD-DETECT-2).

        The result is a straight passthrough: candidates keep the provider's
        anonymous ``provider_label`` (no business ID is invented), plus the
        result-level ``coordinate_space``; ``elapsed_ms`` is THIS handler's
        wall-clock (decode + detect), so probes can compare it against the
        provider-internal timing.
        """
        page_b64 = payload.get("page")
        if not isinstance(page_b64, str) or not page_b64:
            raise DetectRequestError(
                "core.detect requires 'page': a base64-encoded PNG/JPEG image"
            )
        width = payload.get("width")
        height = payload.get("height")
        for name, value in (("width", width), ("height", height)):
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise DetectRequestError(
                    f"core.detect requires '{name}': a positive int"
                )
        if len(page_b64) > _MAX_DETECT_PAGE_B64_CHARS:
            raise DetectRequestError(
                f"core.detect page exceeds the {MAX_DETECT_PAGE_BYTES} byte limit"
            )
        try:
            encoded = base64.b64decode(page_b64, validate=True)
        except (ValueError, TypeError) as error:
            raise DetectRequestError(
                "core.detect 'page' is not valid base64"
            ) from error
        if len(encoded) > MAX_DETECT_PAGE_BYTES:
            raise DetectRequestError(
                f"core.detect page exceeds the {MAX_DETECT_PAGE_BYTES} byte limit"
            )

        # Pillow is lazy for the same reason the ML stack is: module import
        # (and therefore process startup) stays free of heavy dependencies.
        try:
            from PIL import Image
        except ImportError as error:  # pragma: no cover - closure gap, not a test path
            raise ProviderNotConfigured(
                "no image decoder is available in this build (Pillow missing)",
                stage="core.detect",
            ) from error
        try:
            with Image.open(io.BytesIO(encoded)) as image:
                rgb = image.convert("RGB")
                actual_width, actual_height = rgb.size
                if actual_width != width or actual_height != height:
                    raise DetectRequestError(
                        "core.detect width/height do not match the decoded "
                        f"image ({actual_width}x{actual_height} != "
                        f"{width}x{height})"
                    )
                frame = rgb.tobytes()
        except DetectRequestError:
            raise
        except Exception as error:  # noqa: BLE001 - any decode failure is a bad request
            raise DetectRequestError(
                "core.detect 'page' is not a decodable PNG/JPEG image"
            ) from error

        detector = getattr(self._core, "detector", None)
        if detector is None:
            # Same capability-gap slot as the pipeline detect step
            # (handlers.handle_detect): fail closed at NOT_CONFIGURED, never
            # fabricate output.
            raise ProviderNotConfigured(
                "no detection provider is wired at assembly", stage="core.detect"
            )

        request = DetectionRequest(
            # The protocol command name as the page identifier: DetectionRequest
            # requires one (ports contract), the providers only carry it
            # through into DetectionResult provenance, and no Region row is
            # written on this surface -- so a stable constant beats a per-run
            # value (mock determinism keeps holding).
            page_id="core.detect",
            image_bytes=frame,
            width=width,
            height=height,
        )
        started = time.perf_counter()
        result = detector.detect(request)
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return {
            "candidates": [
                {
                    "provider_label": candidate.provider_label,
                    "polygon": [
                        [float(x), float(y)] for x, y in candidate.polygon
                    ],
                    "reading_order": candidate.reading_order,
                    "confidence": candidate.confidence,
                    "coordinate_space": result.coordinate_space,
                }
                for candidate in result.candidates
            ],
            "elapsed_ms": elapsed_ms,
        }

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

        # M2-PROD-DETECT-3: real inference over the assembled detector. The
        # three commands above are untouched; this branch only widens the
        # surface (protocol minor bump, see the module docstring).
        if command == "core.detect":
            try:
                detect_result = self.handle_detect(payload)
            except DetectRequestError as error:
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=E_INVALID_REQUEST,
                            category="validation",
                            message=str(error),
                            retryable=False,
                        ),
                    },
                    False,
                )
            except ProviderError as error:
                # Typed provider failure passthrough: the provider's own
                # error_code (PROVIDER_NOT_CONFIGURED, PROVIDER_DEPENDENCY_MISSING,
                # PROVIDER_FAILED, INVALID_INPUT, ...) stays stable on the wire,
                # with its own retryability ruling.
                return (
                    {
                        "protocol": PROTOCOL_NAME,
                        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                        "request_id": request_id,
                        "result": None,
                        "error": make_error_envelope(
                            code=error.error_code,
                            category="internal",
                            message=str(error)[:500],
                            retryable=bool(error.retryable),
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
                            message="Detection failed",
                            retryable=False,
                        ),
                    },
                    False,
                )
            return (
                {
                    "protocol": PROTOCOL_NAME,
                    "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                    "request_id": request_id,
                    "result": detect_result,
                    "error": None,
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
