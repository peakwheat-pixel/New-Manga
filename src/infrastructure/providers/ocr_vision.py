"""OpenAI-compatible Vision OCR adapter (D06 §7.1/§7.2, TASK-016 discipline).

The adapter asks for a strict JSON envelope and then validates it. Two rules
from TASK-016 survive into production:

- the model never assigns a business RegionID: recognised items carry a
  provider-local label (``vision-<n>``) and the caller maps them onto the
  Region it asked about;
- a malformed envelope is a retryable ``PROVIDER_INVALID_OUTPUT``, never a
  partially trusted result.

Without a configured ``base_url``/``model`` (and, for hosted endpoints, a
resolvable credential) the adapter is Not-Ready at the registry level, and a
direct call fails closed with ``PROVIDER_NOT_CONFIGURED``.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field

from infrastructure.providers.openai_client import (
    OpenAiCompatibleClient,
    OpenAiCompatibleConfig,
)
from ports.ocr.ports import (
    OcrLine,
    OcrRequest,
    OcrResult,
    SCRIPT_CHINESE,
    SCRIPT_JAPANESE,
    SCRIPT_KOREAN,
    SCRIPT_LATIN,
)
from ports.providers.errors import ProviderInputError, ProviderInvalidOutput

PROVIDER_VISION_OCR = "openai-vision-ocr"

VISION_SYSTEM_PROMPT = (
    "You are an OCR engine. Read every text region of the supplied image and "
    "answer with a single JSON object of the form "
    '{"regions":[{"index":0,"text":"...","polygon":[[x,y],...],'
    '"confidence":0.0}]}. Use image-local pixel coordinates, keep the natural '
    "reading order, and never invent text that is not visible."
)


@dataclass
class VisionOcrProvider:
    """Detection+recognition over an OpenAI-compatible vision endpoint."""

    config: OpenAiCompatibleConfig
    client: OpenAiCompatibleClient
    provider_id: str = PROVIDER_VISION_OCR
    provider_type: str = "openai-compatible-vision"
    languages: frozenset[str] = frozenset(
        {SCRIPT_JAPANESE, SCRIPT_KOREAN, SCRIPT_CHINESE, SCRIPT_LATIN}
    )
    needs_detection: bool = True
    options: tuple[tuple[str, str], ...] = field(default=())

    def __post_init__(self) -> None:
        if not self.provider_id:
            raise ValueError("provider_id is required")

    @property
    def model(self) -> str:
        return self.config.model

    def recognize(self, request: OcrRequest) -> OcrResult:
        if request.script not in self.languages:
            raise ProviderInputError(
                f"{self.provider_id} declares no support for {request.script!r}",
                provider_id=self.provider_id,
                stage="ocr",
            )
        if not request.image_bytes:
            raise ProviderInputError(
                "no image bytes were supplied for the region crop",
                provider_id=self.provider_id,
                stage="ocr",
            )
        completion = self.client.complete(
            user_text=(
                "Recognise the text in this image crop and answer with the JSON "
                "object described in the system prompt."
            ),
            system_prompt=VISION_SYSTEM_PROMPT,
            image_bytes=request.image_bytes,
            options=dict(self.options) or None,
            stage="ocr",
        )
        lines = parse_vision_regions(completion.raw_text, self.provider_id)
        text = "\n".join(line.text for line in lines)
        confidences = [line.confidence for line in lines if line.confidence is not None]
        return OcrResult(
            region_id=request.region_id,
            text=text,
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model=self.model,
            confidence=(sum(confidences) / len(confidences) if confidences else None),
            script=request.script,
            direction=request.direction,
            lines=lines,
            options=request.options,
            elapsed_ms=completion.elapsed_ms,
        )


def parse_vision_regions(raw_text: str, provider_id: str = PROVIDER_VISION_OCR) -> tuple[OcrLine, ...]:
    """Validate the vision envelope; provider-local labels only (TASK-016)."""
    try:
        data = json.loads(raw_text)
    except (ValueError, TypeError) as error:
        raise ProviderInvalidOutput(
            f"vision OCR answer is not valid JSON: {error}",
            provider_id=provider_id,
            stage="ocr",
        ) from error
    if not isinstance(data, dict) or not isinstance(data.get("regions"), list):
        raise ProviderInvalidOutput(
            "vision OCR answer has no regions[]", provider_id=provider_id, stage="ocr"
        )
    lines: list[OcrLine] = []
    for index, item in enumerate(data["regions"]):
        if not isinstance(item, dict):
            raise ProviderInvalidOutput(
                f"vision region {index} is not an object",
                provider_id=provider_id,
                stage="ocr",
            )
        text = item.get("text")
        if not isinstance(text, str):
            raise ProviderInvalidOutput(
                f"vision region {index} carries no string text",
                provider_id=provider_id,
                stage="ocr",
            )
        confidence = item.get("confidence")
        if confidence is not None:
            try:
                confidence = float(confidence)
            except (TypeError, ValueError):
                confidence = None
        lines.append(
            OcrLine(
                text=text,
                confidence=confidence,
                polygon=_polygon_of(item.get("polygon"), provider_id),
            )
        )
    return tuple(lines)


def _polygon_of(raw: object, provider_id: str) -> tuple[tuple[float, float], ...]:
    if raw is None:
        return ()
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise ProviderInvalidOutput(
            f"vision polygon is not a list: {raw!r}", provider_id=provider_id, stage="ocr"
        )
    points: list[tuple[float, float]] = []
    for point in raw:
        if not isinstance(point, Sequence) or len(point) < 2:
            raise ProviderInvalidOutput(
                f"vision polygon point is malformed: {point!r}",
                provider_id=provider_id,
                stage="ocr",
            )
        try:
            points.append((float(point[0]), float(point[1])))
        except (TypeError, ValueError):
            raise ProviderInvalidOutput(
                f"vision polygon point is not numeric: {point!r}",
                provider_id=provider_id,
                stage="ocr",
            ) from None
    return tuple(points)
