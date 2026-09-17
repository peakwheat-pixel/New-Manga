"""Shared doubles for the provider suite, under a **unique module name**.

TASK-034 AC ④ (TASK-035 R-02): these used to live in ``tests/providers/
conftest.py``, and the test modules imported them with a bare
``from conftest import …``. Because no test directory carries an
``__init__.py``, a single pytest invocation that collects ``tests/editing``
first makes the name ``conftest`` resolve to ``tests/editing/conftest.py`` and
the provider modules fail at collection time:

    pytest tests/providers tests/editing   -> 4 collection errors   (before)
    pytest tests/editing tests/providers   -> 137 passed            (before)

Every shared double now lives here and is imported explicitly, so collection
order no longer matters. Fixtures that pytest injects stay in ``conftest.py``
and import from this module.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ports.inpaint.ports import BooleanMask, ImageFrame  # noqa: E402
from ports.network.transport import (  # noqa: E402
    TransportOutcome,
    TransportRequest,
    TransportResponse,
)


@dataclass
class RecordedCall:
    method: str
    url: str
    headers: dict
    body: bytes | None


@dataclass
class FakeTransport:
    """Stands in for the TASK-009 transport; records every request."""

    responses: dict[str, tuple[int, bytes]] = field(default_factory=dict)
    default: tuple[int, bytes] = (200, b"{}")
    error: Exception | None = None
    calls: list[RecordedCall] = field(default_factory=list)

    def send(self, request: TransportRequest, profile) -> TransportOutcome:
        self.calls.append(
            RecordedCall(request.method, request.url, dict(request.headers), request.body)
        )
        if self.error is not None:
            raise self.error
        status, body = self.responses.get(request.url, self.default)
        if callable(body):  # pragma: no cover - defensive
            body = body(request)
        return TransportOutcome(TransportResponse(status=status, body=body))

    @property
    def urls(self) -> list[str]:
        return [call.url for call in self.calls]


def chat_completion(content: str, *, status: int = 200) -> tuple[int, bytes]:
    payload = {"choices": [{"message": {"role": "assistant", "content": content}}]}
    return status, json.dumps(payload).encode("utf-8")


def frame(
    width: int = 4, height: int = 3, color: tuple[int, int, int] = (200, 200, 200)
) -> ImageFrame:
    """Uniform ``rgb32`` frame (4 bytes/pixel, B,G,R,A order)."""
    pixel = bytes((color[2], color[1], color[0], 255))
    return ImageFrame(width, height, "rgb32", pixel * (width * height))


def mask_from_boxes(
    width: int, height: int, boxes: Sequence[Sequence[int]]
) -> BooleanMask:
    rows = [[False] * width for _ in range(height)]
    for x0, y0, x1, y1 in boxes:
        for y in range(y0, y1):
            for x in range(x0, x1):
                rows[y][x] = True
    return BooleanMask(width, height, tuple(tuple(row) for row in rows))


@dataclass
class FakePageImages:
    """PageImageSource double: fixed frame and crop bytes."""

    page: ImageFrame
    crop: bytes = b"crop-bytes"
    crop_size: tuple[int, int] = (4, 3)
    region_calls: list[tuple[str, str]] = field(default_factory=list)

    def page_frame(self, page_id: str) -> ImageFrame:
        return self.page

    def region_crop(self, page_id: str, region_id: str) -> tuple[bytes, int, int]:
        self.region_calls.append((page_id, region_id))
        return self.crop, self.crop_size[0], self.crop_size[1]


@dataclass
class FakeGeometry:
    boxes: Mapping[str, tuple[tuple[int, int, int, int], ...]] = field(
        default_factory=dict
    )

    def mask_geometry(self, region_id: str):
        from infrastructure.providers.handlers import RegionMaskGeometry

        return RegionMaskGeometry(boxes=self.boxes.get(region_id, ((0, 0, 2, 2),)))


class FakeOcrProvider:
    provider_id = "fake-ocr"
    provider_type = "fake"
    languages = frozenset({"japanese", "korean"})
    needs_detection = False
    requires_gpu = False

    def __init__(self, text: str = "こんにちは") -> None:
        self.text = text
        self.requests: list = []

    def recognize(self, request):
        from ports.ocr.ports import OcrResult

        self.requests.append(request)
        return OcrResult(
            region_id=request.region_id,
            text=self.text,
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model="fake-model",
            confidence=0.5,
            script=request.script,
            direction=request.direction,
            options=request.options,
        )


class FakeTranslationProvider:
    provider_id = "fake-translate"
    provider_type = "fake"
    requires_gpu = False

    def __init__(self, mapping: Callable[[str], str] | None = None) -> None:
        self.mapping = mapping or (lambda text: f"[en]{text}")
        self.payloads: list = []

    def translate(self, payload):
        from ports.translation.ports import TranslationCallResult

        self.payloads.append(payload)
        return TranslationCallResult(
            translations={
                region.region_id: self.mapping(region.text) for region in payload.regions
            },
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model="fake-model",
        )
