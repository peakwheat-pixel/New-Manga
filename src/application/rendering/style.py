"""Render-side text style and font-size resolution (D03 §11, D06 §23).

The domain ``TextStyle`` (TASK-008) is a minimal revision snapshot subset;
the full D03 §11.5 rendering fields live here so this slice never edits
``src/domain``. Resolution is pure computation against a caller-supplied
fit probe — no Qt/sqlite imports in this package (TASK-005 guards).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing only
    from domain.regions.entities import TextStyle

# D06 §8: fallback when the source font size cannot be estimated reliably.
DEFAULT_FALLBACK_FONT_SIZE = 26.0
#: Below this confidence the detected size is treated as unreliable (D06 §8).
RELIABLE_SOURCE_SIZE_CONFIDENCE = 0.5

FONT_SIZE_OFFSET_MIN = -5  # D03 §11.2 / AC-STYLE-002
FONT_SIZE_OFFSET_MAX = 5

# D03 §11.6 default style values (Saber-translator text defaults).
DEFAULT_FONT_FAMILY = "Source Han Sans K Bold"
DEFAULT_TEXT_COLOR = "#000000"
DEFAULT_FILL_COLOR = "#FFFFFF"
DEFAULT_STROKE_COLOR = "#FFFFFF"
DEFAULT_STROKE_WIDTH = 3.0
DEFAULT_LINE_SPACING = 1.0
DEFAULT_TEXT_ALIGN = "start"

#: Only shrink_to_fit is frozen for this slice (D03 §11.3 default).
OVERFLOW_POLICY_SHRINK_TO_FIT = "shrink_to_fit"

#: Fit probe: given a candidate font size, report whether the laid-out
#: text fits the region box. Infrastructure supplies the real metrics.
FitProbe = Callable[[float], bool]

#: Shrink search granularity (px). Smallest allowed font size is 1.0.
_SHRINK_STEP = 0.5
_MIN_FONT_SIZE = 1.0


class StyleResolutionError(ValueError):
    """Diagnosable style failure (missing manual size, unfittable text)."""


class TextDirection(str, Enum):
    """D03 §11.5 ``text_direction``: auto / horizontal / vertical."""

    AUTO = "auto"
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@dataclass(frozen=True)
class RenderTextStyle:
    """Full D03 §11.5 style input for one region render."""

    auto_font_size_enabled: bool = True
    font_size_offset: int = 0
    manual_font_size: float | None = None
    detected_source_font_size: float | None = None
    source_font_size_confidence: float = 0.0
    font_family: str = DEFAULT_FONT_FAMILY
    text_color: str = DEFAULT_TEXT_COLOR
    fill_color: str = DEFAULT_FILL_COLOR
    stroke_enabled: bool = True
    stroke_color: str = DEFAULT_STROKE_COLOR
    stroke_width: float = DEFAULT_STROKE_WIDTH
    line_spacing: float = DEFAULT_LINE_SPACING
    text_align: str = DEFAULT_TEXT_ALIGN
    text_direction: TextDirection = TextDirection.AUTO
    overflow_policy: str = OVERFLOW_POLICY_SHRINK_TO_FIT
    manual_style_edited: bool = False

    def __post_init__(self) -> None:
        if not (FONT_SIZE_OFFSET_MIN <= self.font_size_offset <= FONT_SIZE_OFFSET_MAX):
            raise ValueError(
                f"font_size_offset must be within "
                f"{FONT_SIZE_OFFSET_MIN}..{FONT_SIZE_OFFSET_MAX}, "
                f"got {self.font_size_offset}"
            )
        if self.manual_font_size is not None and self.manual_font_size <= 0:
            raise ValueError(f"manual_font_size must be positive, got {self.manual_font_size}")
        if self.line_spacing <= 0:
            raise ValueError(f"line_spacing must be positive, got {self.line_spacing}")
        if self.stroke_width < 0:
            raise ValueError(f"stroke_width must be >= 0, got {self.stroke_width}")
        object.__setattr__(
            self, "text_direction", TextDirection(self.text_direction)
        )

    @classmethod
    def from_domain(cls, domain_style: "TextStyle") -> "RenderTextStyle":
        """Merge the TASK-008 minimal snapshot; absent fields keep D03 §11.6
        defaults. A stored ``font_size`` acts as the manual size."""
        return cls(
            font_family=domain_style.font_family or DEFAULT_FONT_FAMILY,
            text_color=domain_style.text_color or DEFAULT_TEXT_COLOR,
            stroke_color=domain_style.stroke_color or DEFAULT_STROKE_COLOR,
            stroke_width=domain_style.stroke_width,
            auto_font_size_enabled=domain_style.auto_font_size_enabled,
            manual_font_size=(
                float(domain_style.font_size)
                if domain_style.font_size is not None
                else None
            ),
        )


@dataclass(frozen=True)
class FontSizeResolution:
    """Outcome of the D03 §11.1 chain, recorded per region in provenance."""

    base_font_size: float
    final_font_size: float
    font_size_offset: int
    used_fallback: bool
    shrunk: bool
    auto: bool


def resolve_font_size(
    style: RenderTextStyle, fits: FitProbe
) -> FontSizeResolution:
    """Resolve ``final_font_size`` (AC-STYLE-001..005).

    auto path: detected (reliable) → fallback 26 → +offset → shrink-to-fit.
    Auto never enlarges above the candidate (AC-STYLE-004); manual mode
    keeps the user size verbatim, explicitly allowed to break the limits
    (AC-STYLE-005, D03 §11.3).
    """
    if not style.auto_font_size_enabled:
        if style.manual_font_size is None:
            raise StyleResolutionError(
                "auto_font_size_enabled=False requires a manual_font_size"
            )
        return FontSizeResolution(
            base_font_size=style.manual_font_size,
            final_font_size=style.manual_font_size,
            font_size_offset=0,
            used_fallback=False,
            shrunk=False,
            auto=False,
        )

    detected = style.detected_source_font_size
    reliable = (
        detected is not None
        and style.source_font_size_confidence >= RELIABLE_SOURCE_SIZE_CONFIDENCE
    )
    base = float(detected) if reliable else DEFAULT_FALLBACK_FONT_SIZE
    candidate = max(_MIN_FONT_SIZE, base + style.font_size_offset)

    if fits(candidate):
        final = candidate
    else:
        if style.overflow_policy != OVERFLOW_POLICY_SHRINK_TO_FIT:
            raise StyleResolutionError(
                f"unsupported overflow_policy: {style.overflow_policy!r}"
            )
        if not fits(_MIN_FONT_SIZE):
            raise StyleResolutionError(
                "text cannot fit the region even at the minimum font size"
            )
        final = _largest_fitting_size(candidate, fits)
    return FontSizeResolution(
        base_font_size=base,
        final_font_size=final,
        font_size_offset=style.font_size_offset,
        used_fallback=not reliable,
        shrunk=final < candidate,
        auto=True,
    )


def _largest_fitting_size(candidate: float, fits: FitProbe) -> float:
    """Largest size in [1.0, candidate] that fits, searched on the 0.5 grid
    from the candidate downward (shrink never enlarges, AC-STYLE-003/004)."""
    size = candidate
    while size > _MIN_FONT_SIZE:
        if fits(size):
            return size
        size = max(_MIN_FONT_SIZE, size - _SHRINK_STEP)
    return _MIN_FONT_SIZE
