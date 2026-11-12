"""Independent synthetic regression checks for the SFX route contract.

These tests exercise only synthetic candidates and the current source tree. They
do not use model weights, manga images, OCR labels, or translation services.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[3] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.translation.context.gate import decide_sfx_translation
from bootstrap.core_assembly import _detected_region_type
from domain.regions.entities import RegionType
from infrastructure.providers.detection_sfx import MangaSfxParallelDetectionProvider
from ports.detection.ports import DetectionRequest, DetectionResult, RegionCandidate
from ports.providers.errors import ProviderNotConfigured


def _candidate(label: str, reading_order: int = 1) -> RegionCandidate:
    return RegionCandidate(
        polygon=((0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)),
        reading_order=reading_order,
        confidence=0.9,
        provider_label=label,
    )


class _FixedDetector:
    provider_id = "synthetic"
    provider_type = "synthetic"
    model = "synthetic"
    conf_threshold = 0.5

    def __init__(self, candidates: tuple[RegionCandidate, ...]) -> None:
        self.candidates = candidates

    def detect(self, request: DetectionRequest) -> DetectionResult:
        return DetectionResult(
            page_id=request.page_id,
            candidates=self.candidates,
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model=self.model,
        )


class _FailingDetector(_FixedDetector):
    def detect(self, request: DetectionRequest) -> DetectionResult:
        raise ProviderNotConfigured("synthetic SFX weights unavailable", stage="detection")


def _request() -> DetectionRequest:
    return DetectionRequest(page_id="synthetic-page", image_bytes=b"synthetic", width=10, height=10)


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("sfx-1", RegionType.SFX),
        ("sfx-arb-manga-1", RegionType.SFX),
        ("manga-1", RegionType.SPEECH),
        ("unmapped-1", RegionType.SPEECH),
    ],
)
def test_synthetic_detection_label_routes_to_expected_region_type(label, expected):
    assert _detected_region_type(label) is expected


@pytest.mark.parametrize(
    ("policy", "expected_status"),
    [("skip", "skip_policy"), ("manual", "skip_policy"), ("translate", "translate")],
)
def test_sfx_policy_matrix_gates_only_automatic_translation(policy, expected_status):
    decision = decide_sfx_translation("sfx", policy)
    assert decision.status == expected_status
    if policy in {"skip", "manual"}:
        assert decision.reason == "sfx_skip"


def test_typed_sfx_provider_failure_is_observable_and_keeps_primary_route(capsys):
    primary = _FixedDetector((_candidate("manga-1"),))
    composite = MangaSfxParallelDetectionProvider(
        primary=primary,
        sfx=_FailingDetector(()),
    )

    result = composite.detect(_request())

    assert [candidate.provider_label for candidate in result.candidates] == ["manga-1"]
    assert dict(result.options)["sfx_provider_status"] == "degraded: PROVIDER_NOT_CONFIGURED"
    assert "sfx detection degraded" in capsys.readouterr().err
    assert _detected_region_type(result.candidates[0].provider_label) is RegionType.SPEECH


def test_near_duplicate_cross_provider_candidates_are_both_retained():
    """Characterize arbitration cardinality with identical synthetic boxes."""
    result = MangaSfxParallelDetectionProvider(
        primary=_FixedDetector((_candidate("manga-1"),)),
        sfx=_FixedDetector((_candidate("sfx-1"),)),
    ).detect(_request())

    assert [candidate.provider_label for candidate in result.candidates] == [
        "sfx-arb-manga-1",
        "sfx-1",
    ]
    assert result.candidates[0].polygon == result.candidates[1].polygon
    assert all(_detected_region_type(candidate.provider_label) is RegionType.SFX
               for candidate in result.candidates)
