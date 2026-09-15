"""Rerender use cases (D06 §23/§41/§47, §85, TASK-002 §8.1/§8.2).

Runs the real stack: SQLite artifacts + managed storage + Qt layout and
composition. Region persistence uses the in-memory repository (the
service only needs the RegionRepository protocol).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import rendering_helpers  # noqa: F401  (sys.path injection)
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "editing"))
from region_helpers import InMemoryRegionRepository  # noqa: E402

from application.rendering.service import RenderService, RenderStatus
from application.translation.color.service import SourceStyleService
from domain.regions.entities import BBox, Region, RegionGeometry
from infrastructure.filesystem.managed_storage import ManagedFileStorage
from infrastructure.rendering.font_catalog import QtFontCatalog
from infrastructure.rendering.locator import SqlitePageArtifactLocator
from infrastructure.rendering.pixel_source_style import PixelSourceStyleAnalyzer
from infrastructure.rendering.qt_compositor import QtImageCompositor
from infrastructure.rendering.qt_layout import QtTextLayoutEngine
from infrastructure.sqlite.artifacts import SqliteArtifactRepository
from ports.repositories.artifacts import (
    ArtifactType,
    ContentProvider,
    NewArtifact,
    PendingArtifactCommit,
)

# --- image helpers -------------------------------------------------------


def png_with_text(
    width: int, height: int, lines: list[tuple[int, int, str]], fill: str = "#FFFFFF"
) -> bytes:
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QFont, QImage, QPainter

    image = QImage(width, height, QImage.Format_ARGB32)
    image.fill(fill)
    painter = QPainter(image)
    font = QFont("Microsoft YaHei")
    font.setPixelSize(22)
    painter.setFont(font)
    painter.setPen("#111111")
    for x, y, text in lines:
        painter.drawText(x, y, text)
    painter.end()
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


def ink_count(png: bytes, box: tuple[int, int, int, int]) -> int:
    from PySide6.QtGui import QImage

    image = QImage.fromData(png)
    x, y, w, h = box
    count = 0
    for row in range(y, min(y + h, image.height())):
        for col in range(x, min(x + w, image.width())):
            color = image.pixelColor(col, row)
            if (color.red(), color.green(), color.blue()) != (255, 255, 255):
                count += 1
    return count


def region_box_equal(a: bytes, b: bytes, box: tuple[int, int, int, int]) -> bool:
    from PySide6.QtGui import QImage

    image_a, image_b = QImage.fromData(a), QImage.fromData(b)
    x, y, w, h = box
    for row in range(y, min(y + h, image_a.height())):
        for col in range(x, min(x + w, image_a.width())):
            if image_a.pixel(col, row) != image_b.pixel(col, row):
                return False
    return True


# --- fixtures ------------------------------------------------------------


@pytest.fixture()
def stack(qapp, tmp_path):
    from infrastructure.sqlite.connection import open_database
    from infrastructure.sqlite.migrator import MigrationRunner
    from infrastructure.sqlite.schema import default_migrations

    conn, _ = open_database(
        tmp_path / "app.db",
        latest_known_schema_version=default_migrations()[-1].schema_version,
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    storage = ManagedFileStorage(tmp_path / "storage")
    storage.ensure_layout()

    artifacts = SqliteArtifactRepository(conn, storage)
    locator = SqlitePageArtifactLocator(conn)
    catalog = QtFontCatalog()
    service = RenderService(
        region_repo=InMemoryRegionRepository(),
        locator=locator,
        artifacts=artifacts,
        storage=storage,
        layout_engine=QtTextLayoutEngine(catalog),
        compositor=QtImageCompositor(),
        source_styles=SourceStyleService(PixelSourceStyleAnalyzer()),
        font_catalog=catalog,
    )
    yield {
        "conn": conn,
        "storage": storage,
        "artifacts": artifacts,
        "locator": locator,
        "service": service,
    }
    conn.close()


def seed_page(stack) -> dict[str, str]:
    import uuid

    conn = stack["conn"]
    ids = {
        "book_id": uuid.uuid4().hex,
        "chapter_id": uuid.uuid4().hex,
        "page_id": uuid.uuid4().hex,
    }
    now = "2026-01-01T00:00:00"
    with conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES (?, 'b', ?, ?)",
            (ids["book_id"], now, now),
        )
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
            " VALUES (?, ?, 'c', ?, ?)",
            (ids["chapter_id"], ids["book_id"], now, now),
        )
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at)"
            " VALUES (?, ?, 0, ?, ?)",
            (ids["page_id"], ids["chapter_id"], now, now),
        )
    return ids


def commit_artifact(stack, page_ids, artifact_type: ArtifactType, content: bytes):
    artifacts = stack["artifacts"]
    record = artifacts.create_artifact(
        NewArtifact(
            book_id=page_ids["book_id"],
            chapter_id=page_ids["chapter_id"],
            page_id=page_ids["page_id"],
            artifact_type=artifact_type,
        )
    )
    outcome = artifacts.commit_revision(
        PendingArtifactCommit(
            artifact_id=record.artifact_id,
            content_provider=ContentProvider(payload=content),
            mime_type="image/png",
            expected_current_revision_id=None,
            file_suffix=".png",
        )
    )
    assert outcome.status.value == "committed", outcome.detail
    return record, outcome.revision


def make_region(
    repo,
    page_id,
    *,
    region_id: str | None = None,
    bbox=(40, 30, 220, 120),
    final: str = "你好世界",
    sfx: str = "translate",
):
    region = Region(
        region_id=region_id or f"region-{len(repo.regions) + 1}",
        page_id=page_id,
        geometry=RegionGeometry(bbox=BBox(*bbox)),
    )
    region.sfx_policy = sfx
    if final:
        region.text.machine_translation = final
        region.text.refresh_final()
    repo.add_region(region)
    return region


@pytest.fixture()
def clean_png() -> bytes:
    return png_with_text(400, 260, [(60, 120, "原文气泡文字")])


def read_managed(stack, relative_path: str) -> bytes:
    return Path(stack["storage"].absolute_path(relative_path)).read_bytes()


# --- page rerender -------------------------------------------------------


class TestRerenderPage:
    def test_renders_and_commits_new_translated_revision(self, stack, clean_png) -> None:
        ids = seed_page(stack)
        commit_artifact(stack, ids, ArtifactType.CLEAN, clean_png)
        region = make_region(stack["service"]._region_repo, ids["page_id"])

        outcome = stack["service"].rerender_page(ids["page_id"])

        assert outcome.status is RenderStatus.COMMITTED
        assert outcome.revision_no == 1
        assert outcome.reports[0].region_id == region.region_id
        assert outcome.reports[0].final_font_size is not None
        rendered = read_managed(stack, outcome.managed_path)
        assert ink_count(rendered, (40, 30, 220, 120)) > 30
        provenance = json.loads(outcome.provenance_json)
        assert provenance["regions"][region.region_id]["final_font_size"] > 0
        assert provenance["ai_invoked"] is False

    def test_missing_clean_is_blocked_not_auto_inpainted(self, stack) -> None:
        ids = seed_page(stack)
        make_region(stack["service"]._region_repo, ids["page_id"])

        outcome = stack["service"].rerender_page(ids["page_id"])

        assert outcome.status is RenderStatus.BLOCKED
        assert outcome.error_code == "MISSING_REQUIRED_INPUT"
        assert "missing_clean_artifact" in (outcome.detail or "")
        assert (
            stack["locator"].locate_current(ids["page_id"], ArtifactType.TRANSLATED)
            is None
        )

    def test_sfx_skip_regions_follow_policy_gate(self, stack, clean_png) -> None:
        ids = seed_page(stack)
        commit_artifact(stack, ids, ArtifactType.CLEAN, clean_png)
        repo = stack["service"]._region_repo
        normal = make_region(repo, ids["page_id"], region_id="r-normal", final="正文")
        sfx_skip = make_region(
            repo, ids["page_id"], region_id="r-sfx", bbox=(150, 20, 100, 100),
            final="ドン!", sfx="skip",
        )

        outcome = stack["service"].rerender_page(ids["page_id"])

        assert outcome.status is RenderStatus.COMMITTED
        by_id = {report.region_id: report for report in outcome.reports}
        assert by_id[sfx_skip.region_id].status == "skipped"
        assert by_id[sfx_skip.region_id].skip_reason == "skip_policy"
        assert by_id[normal.region_id].status == "rendered"
        rendered = read_managed(stack, outcome.managed_path)
        # SFX box is pixel-identical to the clean base (nothing was drawn)
        assert region_box_equal(rendered, clean_png, (150, 20, 100, 100))

    def test_empty_final_translation_regions_are_skipped(self, stack, clean_png) -> None:
        ids = seed_page(stack)
        commit_artifact(stack, ids, ArtifactType.CLEAN, clean_png)
        region = make_region(stack["service"]._region_repo, ids["page_id"], final="")

        outcome = stack["service"].rerender_page(ids["page_id"])

        assert outcome.status is RenderStatus.COMMITTED
        assert outcome.reports[0].status == "skipped"
        assert outcome.reports[0].skip_reason == "empty_final"

    def test_stale_expectation_conflicts_and_keeps_current(self, stack, clean_png) -> None:
        """§8.2 COMPOSITION_BASE_CHANGED: a second writer commits between
        our read and our commit → compare-and-write rejects, the current
        pointer stays on their revision."""
        ids = seed_page(stack)
        commit_artifact(stack, ids, ArtifactType.CLEAN, clean_png)
        make_region(stack["service"]._region_repo, ids["page_id"])
        first = stack["service"].rerender_page(ids["page_id"])
        assert first.status is RenderStatus.COMMITTED

        service = stack["service"]
        real_compositor = service._compositor
        artifacts = stack["artifacts"]

        class RacingCompositor:
            def compose_page(self, base_png, ops):
                # another writer wins the race while we are composing
                current = artifacts.get_current_revision(first.artifact_id)
                outcome = artifacts.commit_revision(
                    PendingArtifactCommit(
                        artifact_id=first.artifact_id,
                        content_provider=ContentProvider(payload=clean_png),
                        mime_type="image/png",
                        expected_current_revision_id=current.artifact_revision_id,
                        file_suffix=".png",
                    )
                )
                assert outcome.status.value == "committed"
                return real_compositor.compose_page(base_png, ops)

            def compose_region(self, *args):
                return real_compositor.compose_region(*args)

        service._compositor = RacingCompositor()
        outcome = service.rerender_page(ids["page_id"])
        assert outcome.status is RenderStatus.CONFLICT
        assert outcome.error_code == "INPUT_REVISION_CHANGED"
        record, revision = stack["locator"].locate_current(
            ids["page_id"], ArtifactType.TRANSLATED
        )
        assert revision.revision_no == 2  # the racing writer's revision stays

    def test_compositor_failure_keeps_old_current(self, stack, clean_png) -> None:
        ids = seed_page(stack)
        commit_artifact(stack, ids, ArtifactType.CLEAN, clean_png)
        make_region(stack["service"]._region_repo, ids["page_id"])
        first = stack["service"].rerender_page(ids["page_id"])
        assert first.status is RenderStatus.COMMITTED

        class ExplodingCompositor:
            def compose_page(self, base_png, ops):
                raise OSError("disk full during composition")

            def compose_region(self, *args):
                raise OSError("disk full during composition")

        stack["service"]._compositor = ExplodingCompositor()
        second = stack["service"].rerender_page(ids["page_id"])
        assert second.status is RenderStatus.WRITE_FAILED
        assert second.error_code == "ARTIFACT_WRITE_FAILED"
        _, revision = stack["locator"].locate_current(
            ids["page_id"], ArtifactType.TRANSLATED
        )
        assert revision.revision_no == 1

    def test_render_never_touches_ai_ports(self, stack, clean_png) -> None:
        """AC-RENDER-001: rerender must not invoke OCR/Translation/Inpaint.

        Every injected port is wrapped in an AI spy; the whole rerender
        path must complete without a single AI-flavoured call, and the
        service must hold no provider reference at all.
        """
        ids = seed_page(stack)
        commit_artifact(stack, ids, ArtifactType.CLEAN, clean_png)
        make_region(stack["service"]._region_repo, ids["page_id"])
        service = stack["service"]

        calls: list[str] = []

        def spy(name, inner):
            class Spy:
                def ocr(self, *a):
                    calls.append(name + ":ocr")

                def translate(self, *a):
                    calls.append(name + ":translate")

                def inpaint(self, *a):
                    calls.append(name + ":inpaint")

                def __getattr__(self, attr):
                    return getattr(inner, attr)

            return Spy()

        service._layout_engine = spy("layout", service._layout_engine)
        service._compositor = spy("compositor", service._compositor)
        service._source_styles = spy("style", service._source_styles)

        outcome = service.rerender_page(ids["page_id"])
        assert outcome.status is RenderStatus.COMMITTED
        assert calls == []
        for attribute in vars(service):
            assert "provider" not in attribute.lower(), attribute


# --- single-region rerender ----------------------------------------------


class TestRerenderRegion:
    def test_region_composition_keeps_neighbours(self, stack, clean_png) -> None:
        ids = seed_page(stack)
        commit_artifact(stack, ids, ArtifactType.CLEAN, clean_png)
        repo = stack["service"]._region_repo
        make_region(repo, ids["page_id"], region_id="r-a", bbox=(20, 20, 150, 100), final="邻居")
        target = make_region(
            repo, ids["page_id"], region_id="r-b", bbox=(200, 20, 150, 100), final="目标译文"
        )
        page = stack["service"].rerender_page(ids["page_id"])
        assert page.status is RenderStatus.COMMITTED
        before = read_managed(stack, page.managed_path)

        # the user updates the target's translation, then rerenders only it
        target.text.machine_translation = "改后的新译文"
        target.text.refresh_final()
        outcome = stack["service"].rerender_region("r-b")

        assert outcome.status is RenderStatus.COMMITTED
        after = read_managed(stack, outcome.managed_path)
        assert region_box_equal(before, after, (20, 20, 150, 100))
        assert not region_box_equal(before, after, (200, 20, 150, 100))

    def test_region_revision_conflict_blocks_composition(self, stack, clean_png) -> None:
        """§8.2: the region's current revision must still match at commit
        time; otherwise nothing is written (COMPOSITION_BASE_CHANGED)."""
        ids = seed_page(stack)
        commit_artifact(stack, ids, ArtifactType.CLEAN, clean_png)
        target = make_region(
            stack["service"]._region_repo, ids["page_id"], region_id="r-x", final="旧"
        )
        page = stack["service"].rerender_page(ids["page_id"])
        assert page.status is RenderStatus.COMMITTED

        real_compositor = stack["service"]._compositor
        service = stack["service"]

        class RegionMutatingCompositor:
            """Simulates another writer saving the region between the
            render's snapshot and its commit."""

            def compose_page(self, base_png, ops):
                return real_compositor.compose_page(base_png, ops)

            def compose_region(self, base_png, clean_png, box, op):
                stored = service._region_repo.get_region("r-x")
                stored.current_revision_id = "rev-moved-on"
                service._region_repo.update_region(stored)
                return real_compositor.compose_region(base_png, clean_png, box, op)

        service._compositor = RegionMutatingCompositor()
        outcome = service.rerender_region("r-x")
        assert outcome.status is RenderStatus.CONFLICT
        assert outcome.error_code == "COMPOSITION_BASE_CHANGED"
        _, revision = stack["locator"].locate_current(
            ids["page_id"], ArtifactType.TRANSLATED
        )
        assert revision.revision_no == 1  # old current kept

    def test_missing_final_translation_is_blocked(self, stack, clean_png) -> None:
        ids = seed_page(stack)
        commit_artifact(stack, ids, ArtifactType.CLEAN, clean_png)
        region = make_region(
            stack["service"]._region_repo, ids["page_id"], region_id="r-empty", final=""
        )

        outcome = stack["service"].rerender_region("r-empty")

        assert outcome.status is RenderStatus.BLOCKED
        assert outcome.error_code == "MISSING_REQUIRED_INPUT"

    def test_manual_sfx_requires_explicit_flag(self, stack, clean_png) -> None:
        ids = seed_page(stack)
        commit_artifact(stack, ids, ArtifactType.CLEAN, clean_png)
        make_region(
            stack["service"]._region_repo,
            ids["page_id"],
            region_id="r-sfx",
            final="拟声词",
            sfx="manual",
        )

        blocked = stack["service"].rerender_region("r-sfx")
        assert blocked.status is RenderStatus.BLOCKED
        assert "skip_policy" in (blocked.detail or "")

        allowed = stack["service"].rerender_region("r-sfx", allow_manual_sfx=True)
        assert allowed.status is RenderStatus.COMMITTED
