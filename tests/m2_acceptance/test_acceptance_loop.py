"""M2-AC1 Core acceptance suite (doc/tasks/M2-AC1.md, 测试要求 row 1).

Drives the deterministic acceptance loop through the SAME production
assembly the desktop E2E uses (``bootstrap.acceptance_bridge``), without the
Tauri host: Mock/Local pipeline -> SQLite persistence -> re-assembly from
the same data root (the pytest-level stand-in for the real process restart
the E2E performs) -> reader restore -> PNG export.

The suite shares the acceptance venv's PySide6 requirement with the product
Qt adapters; every Qt-dependent probe skips explicitly (S-01: never a
module-level importorskip).
"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.acceptance_bridge import (  # noqa: E402
    FIXTURE_PAGE_COUNT,
    AcceptanceBridge,
    AcceptanceState,
    assemble_acceptance_core,
    sha256_hex,
    synthetic_page_png,
)


class _LoopHarness:
    """The bridge + a fresh dispatch helper over one data root."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.core = assemble_acceptance_core(
            root / "library.db", root / "managed"
        )
        self.state = AcceptanceState(core=self.core, book_id="", chapter_id="")
        self.bridge = AcceptanceBridge(
            self.state, data_root=root, catalog_db=root / "catalog.sqlite"
        )

    def call(self, method: str, params: dict | None = None) -> dict:
        response = self.bridge._dispatch(
            {"id": 1, "method": method, "params": params or {}}
        )
        if "error" in response:
            raise AssertionError(f"{method} failed: {response['error']}")
        return response["result"]

    def close(self) -> None:
        self.core.conn.close()

    def reassemble(self) -> "_LoopHarness":
        """A brand-new Core assembly over the same data root on disk — the
        same persisted state a relaunched process would find."""
        self.close()
        reassembled = _LoopHarness(self.root)
        books = reassembled.core.repository.list_books()
        chapters = (
            reassembled.core.repository.list_chapters(books[0].book_id)
            if books
            else []
        )
        # mutate the existing state object in place: the bridge already holds
        # this reference, mirroring the bridge main()'s recovery of ids from
        # the persisted library
        reassembled.state.book_id = books[0].book_id if books else ""
        reassembled.state.chapter_id = chapters[0].chapter_id if chapters else ""
        return reassembled


@pytest.fixture
def qapp():
    pytest.importorskip("PySide6")
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QGuiApplication

    if QGuiApplication.instance() is None:
        app = QGuiApplication(["m2-ac1-tests"])
        yield app
        app.quit()
    else:
        yield QGuiApplication.instance()


def test_synthetic_fixture_is_deterministic_and_pages_differ() -> None:
    first = synthetic_page_png(0)
    again = synthetic_page_png(0)
    second = synthetic_page_png(1)
    assert first == again, "the same page index must encode byte-identically"
    assert first != second, "distinct fixture pages must differ"
    for page_bytes in (first, second):
        assert page_bytes.startswith(b"\x89PNG\r\n\x1a\n")
        assert len(page_bytes) > 0


def test_production_registry_never_gains_mock_provider_ids(qapp) -> None:
    """The Mock/Local ids exist only behind the explicit assembly flag: the
    production assembly must never be able to bind or resolve them."""
    import tempfile

    from application.translation.color.service import SourceStyleService
    from bootstrap.core_assembly import assemble_core_services

    class _StubAnalyzer:
        def analyze(self, original_png: bytes, box):  # pragma: no cover
            raise AssertionError("the registry probe does not render")

    class _Marker:
        pass

    prod_root = Path(tempfile.mkdtemp(prefix="m2ac1-prod-registry-"))
    core = assemble_core_services(
        prod_root / "library.db",
        prod_root / "managed",
        image_decoder=_Marker(),
        font_catalog=_Marker(),
        layout_engine=_Marker(),
        compositor=_Marker(),
        source_styles=SourceStyleService(_StubAnalyzer()),
    )
    try:
        ids = {
            descriptor.provider_id for descriptor in core.providers.registry.descriptors()
        }
        assert not any(provider_id.startswith("m2ac1-") for provider_id in ids), (
            "the production assembly must never register the acceptance mock ids"
        )
    finally:
        core.conn.close()

    mock_root = Path(tempfile.mkdtemp(prefix="m2ac1-mock-registry-"))
    mock_core = assemble_acceptance_core(
        mock_root / "library.db", mock_root / "managed"
    )
    try:
        ids = {
            descriptor.provider_id for descriptor in mock_core.providers.registry.descriptors()
        }
        assert {"m2ac1-mock-ocr", "m2ac1-mock-translate"} <= ids
    finally:
        mock_core.conn.close()


def test_full_loop_pipeline_save_restore_reader_export(qapp, tmp_path: Path) -> None:
    """AC1→AC5 at the Core level: the whole loop over one data root with a
    real re-assembly between save and restore."""
    harness = _LoopHarness(tmp_path / "root")
    try:
        seed = harness.call("seed_fixture")
        assert seed["page_count"] == FIXTURE_PAGE_COUNT

        run = harness.call("run_pipeline")
        assert run["status"] == "completed"
        assert run["providers"] == {
            "ocr": "m2ac1-mock-ocr",
            "translate": "m2ac1-mock-translate",
        }

        saved = harness.call("saved_summary")
        assert saved["run_status"] == "completed"
        assert [page["index"] for page in saved["pages"]] == [0, 1]
        assert all(page["sha256"] and page["size"] > 0 for page in saved["pages"])

        cataloged = harness.call("catalog_pages")
        assert [entry["resource_id"] for entry in cataloged["pages"]] == [
            "m2ac1-page-0",
            "m2ac1-page-1",
        ]

        restored = harness.reassemble()
        status = restored.call("status")
        assert status["phase"] == "restore"
        assert status["run_status"] == "completed"
        assert status["page_count"] == FIXTURE_PAGE_COUNT

        reader = restored.call("reader_pages")
        assert len(reader["pages"]) == FIXTURE_PAGE_COUNT
        assert all(page["revision"] for page in reader["pages"])

        reading = restored.call("record_reading", {"visited": [0, 1]})
        assert reading["visited"] == [0, 1]
        assert reading["page_count"] == FIXTURE_PAGE_COUNT

        exported = restored.call("export_page", {"page_index": 1})
        assert exported["sha256"] == saved["pages"][1]["sha256"], (
            "the exported PNG must be the persisted translated page, byte for byte"
        )

        _assert_png_pixels_match(
            restored.core.data_root / "exports" / exported["output_path"],
            restored,
            page_index=1,
        )
        restored.close()
    finally:
        try:
            harness.close()
        except Exception:
            pass


def _assert_png_pixels_match(exported_path: Path, harness: _LoopHarness, page_index: int) -> None:
    """AC5 pixel check: the export decodes to exactly the Reader's page."""
    from PySide6.QtGui import QImage

    reader_page = harness.core.reader_catalog.list_pages(harness.state.chapter_id)[page_index]
    assert reader_page.translated_path is not None

    def pixel_digest(path: str | Path) -> str:
        image = QImage(str(path)).convertToFormat(QImage.Format.Format_RGB32)
        assert not image.isNull(), f"PNG did not decode: {path}"
        return sha256_hex(bytes(image.constBits()))

    assert pixel_digest(exported_path) == pixel_digest(reader_page.translated_path), (
        "the exported PNG pixels must equal the Reader's displayed page"
    )


def test_two_independent_runs_produce_identical_summaries(qapp, tmp_path: Path) -> None:
    """AC1/AC6: two independent data roots must yield identical result
    summaries (content digests only; no per-run ids in the summary)."""
    summaries = []
    for run_index in range(2):
        harness = _LoopHarness(tmp_path / f"run-{run_index}")
        try:
            harness.call("seed_fixture")
            harness.call("run_pipeline")
            summaries.append(harness.call("saved_summary"))
        finally:
            harness.close()
    assert summaries[0] == summaries[1], (
        "two independent deterministic runs must produce identical summaries"
    )
