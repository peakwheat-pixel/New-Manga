"""OCR capability port (D06 §7, D08 AC-OCR-001/004, TASK-019).

Two distinct abilities share one port because they are resolved by the same
ProviderBinding priority (D06 §7.1):

- ``detection``   — where the text boxes are;
- ``recognition`` — what the text says.

An adapter that only recognises (``manga-ocr``) must declare
``recognition_only = True``: it is only allowed a single Region crop and may
never fabricate detection boxes (TASK-016 conclusion).

The port writes nothing. Region text is persisted through the writing side of
the contract (:class:`OcrTextWriter`), which is the *prepare-only* seam
compatible write path: the pipeline keeps owning the current-Revision flip so
the optimistic write guard of TASK-013 stays intact.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from ports.providers.errors import ProviderInputError

SCRIPT_JAPANESE = "japanese"
SCRIPT_KOREAN = "korean"
SCRIPT_CHINESE = "chinese"
SCRIPT_LATIN = "latin"
ALL_SCRIPTS = frozenset({SCRIPT_JAPANESE, SCRIPT_KOREAN, SCRIPT_CHINESE, SCRIPT_LATIN})

TEXT_DIRECTION_HORIZONTAL = "horizontal"
TEXT_DIRECTION_VERTICAL = "vertical"
ALL_DIRECTIONS = frozenset({TEXT_DIRECTION_HORIZONTAL, TEXT_DIRECTION_VERTICAL})


@dataclass(frozen=True)
class OcrRequest:
    """One region crop to recognise.

    ``image_bytes`` is the encoded crop of exactly one Region. Adapters must
    not widen it to the page: the caller owns geometry.
    """

    region_id: str
    page_id: str
    image_bytes: bytes = field(repr=False, default=b"")
    width: int = 0
    height: int = 0
    script: str = SCRIPT_JAPANESE
    direction: str = TEXT_DIRECTION_HORIZONTAL
    options: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.region_id:
            raise ProviderInputError("ocr request requires a region_id", stage="ocr")
        if self.script not in ALL_SCRIPTS:
            raise ProviderInputError(
                f"unsupported script: {self.script!r}", stage="ocr"
            )
        if self.direction not in ALL_DIRECTIONS:
            raise ProviderInputError(
                f"unsupported text direction: {self.direction!r}", stage="ocr"
            )

    def option_dict(self) -> dict[str, str]:
        return dict(self.options)


@dataclass(frozen=True)
class OcrLine:
    """One recognised line inside the crop, in crop-local coordinates."""

    text: str
    confidence: float | None = None
    polygon: tuple[tuple[float, float], ...] = ()


@dataclass(frozen=True)
class OcrResult:
    region_id: str
    text: str
    provider_id: str = ""
    provider_type: str = ""
    model: str = ""
    confidence: float | None = None
    script: str = ""
    direction: str = ""
    lines: tuple[OcrLine, ...] = ()
    options: tuple[tuple[str, str], ...] = ()
    elapsed_ms: int | None = None

    def provenance(self) -> dict:
        """D06 §7.3 output record: text + confidence + provider provenance."""
        return {
            "provider_id": self.provider_id,
            "provider_type": self.provider_type,
            "model": self.model,
            "confidence": self.confidence,
            "script": self.script,
            "direction": self.direction,
            "options": dict(self.options),
            "line_count": len(self.lines),
            "elapsed_ms": self.elapsed_ms,
        }


class OcrProvider(Protocol):
    """One OCR adapter.

    ``languages`` is the set of scripts the adapter honestly supports;
    ``needs_detection`` is False for recognition-only adapters such as
    ``manga-ocr``.
    """

    provider_id: str
    provider_type: str
    languages: frozenset[str]
    needs_detection: bool

    def recognize(self, request: OcrRequest) -> OcrResult: ...


@dataclass(frozen=True)
class PreparedTextWrite:
    """Outcome of a prepare-only region text write.

    ``revision_id`` is the **new** revision row that the pipeline seam is
    expected to adopt as the current revision; ``changed`` drives the
    AC-OCR-002 "原文已变化，现有译文可能需要重译" hint.
    """

    region_id: str
    revision_id: str
    revision_no: int
    changed: bool = False
    retranslate_hint: bool = False


class OcrTextWriter(Protocol):
    """Persist one OCR result without moving the pipeline-owned pointer."""

    def prepare_ocr_text(
        self,
        region_id: str,
        ocr_text: str,
        *,
        provider_id: str = "",
        model: str = "",
        options: dict[str, str] | None = None,
        source_run_id: str | None = None,
        source_step_run_id: str | None = None,
    ) -> PreparedTextWrite: ...
