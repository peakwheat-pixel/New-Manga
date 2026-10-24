"""T1.1.1 gate: the 22 production-seam checks, automated.

Each check drives the real docTR ``fast_base`` detector through the real
``handle_detect`` seam into real SQLite persistence (machine Regions via
``RegionEditingService.create_region``), over generated manga-style sample
pages with ground-truth bubble bboxes. Skips are explicit and only ever
environmental (weights not fetched / docTR not installed) — never silently
passed.
"""

from __future__ import annotations

import pytest

pytest.importorskip("doctr", reason="docTR (python-doctr) is not installed")

from t111_support import (  # noqa: E402
    SEAM_CHECK_MATRIX,
    detector_device,
    locate_doctr_weights,
    run_seam_case,
    seam_checks,
)

_weights = locate_doctr_weights()
if _weights is None:
    pytest.skip(
        "T1.1.1 weights not fetched: run "
        "python verification/T1.1.1/scripts/fetch_doctr_weights.py "
        "(fast_base-688a8b34.pt) or set NEW_MANGA_DOCTR_WEIGHTS",
        allow_module_level=True,
    )


@pytest.fixture(scope="module")
def seam_cases(tmp_path_factory):
    from infrastructure.providers.detection_doctr import DoctrDetectionProvider

    provider = DoctrDetectionProvider(
        weights_path=_weights, device=detector_device()
    )
    work_root = tmp_path_factory.mktemp("t111-seam")
    cases = {
        name: run_seam_case(provider, work_root, name)
        for name in ("jp-horizontal", "jp-vertical", "la-horizontal", "no-text")
    }
    # facts for the failure message below
    return cases


@pytest.mark.parametrize(
    ["sample", "check"],
    SEAM_CHECK_MATRIX,
    ids=[f"{sample}:{check}" for sample, check in SEAM_CHECK_MATRIX],
)
def test_t111_seam_check(seam_cases, sample: str, check: str) -> None:
    case = seam_cases[sample]
    checks = seam_checks(case)
    assert checks[check], (
        f"{sample}/{check}: detect={case['detect_status']} "
        f"error={case['detect_error_code']} regions={case['db_region_count']} "
        f"revisions={case['revision_count']} origins={case['origins']} "
        f"hits={case['hits']}/{case['ground_truth_bubbles']} "
        f"later={case['later_steps']}"
    )
