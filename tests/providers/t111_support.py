"""Shared T1.1.1 seam-test support: sample pages, weights location, case runner.

The four sample pages are generated with the same geometry as the released
evaluation harness (doc/research/T1.1.1-detector-evaluation.md §7.2), so the
automated seam checks here stay comparable with that 22/22 evidence run.
No third-party art is used.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import sqlite3
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from infrastructure.filesystem.managed_storage import ManagedFileStorage
from infrastructure.pipeline.assembly import build_production_pipeline
from infrastructure.providers.handlers import HandlerDependencies, ProductionHandlers
from infrastructure.providers.registry import ProviderRegistry
from infrastructure.providers.retry import RetryPolicy
from infrastructure.providers.step_writes import ArtifactStepWriter, RegionStepWriter
from infrastructure.sqlite.connection import open_database
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.regions import SqliteRegionRepository
from infrastructure.sqlite.schema import default_migrations
from ports.inpaint.ports import ImageFrame

NOW = "2026-01-01T00:00:00+00:00"
WEIGHTS_FILENAME = "fast_base-688a8b34.pt"
JP_FONT = "C:/Windows/Fonts/msgothic.ttc"
LAT_FONT = "C:/Windows/Fonts/arial.ttf"


def locate_doctr_weights() -> Path | None:
    """Find the pinned weights without ever downloading them."""
    env = os.environ.get("NEW_MANGA_DOCTR_WEIGHTS")
    candidates = []
    if env:
        candidates.append(Path(env))
    candidates.append(Path.home() / ".cache" / "doctr" / "models" / WEIGHTS_FILENAME)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def detector_device() -> str:
    return os.environ.get("NEW_MANGA_DOCTR_DEVICE", "cpu")


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def _page(width: int, height: int):
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    for i in range(0, width, 60):
        draw.line([(i, 0), (i, height)], fill=(230, 230, 230), width=1)
    draw.rectangle([0, height - 40, width, height], fill=(210, 210, 210))
    return img, draw


def _bubble(draw, cx, cy, rx, ry, text, font, vertical=False):
    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill="white", outline="black", width=4)
    lines = text.splitlines()
    if vertical:
        col_w = font.size + 6
        start_x = cx + (len(lines) - 1) * col_w // 2
        for li, line in enumerate(lines):
            x = start_x - li * col_w
            total_h = len(line) * (font.size + 4)
            y = cy - total_h // 2
            for ch in line:
                draw.text((x, y), ch, fill="black", font=font, anchor="ma")
                y += font.size + 4
    else:
        line_h = font.size + 8
        total_h = len(lines) * line_h
        y = cy - total_h // 2
        for line in lines:
            w = draw.textlength(line, font=font)
            draw.text((cx - w / 2, y), line, fill="black", font=font)
            y += line_h
    return (cx - rx, cy - ry, cx + rx, cy + ry)


def make_seam_sample(name: str) -> tuple[Image.Image, list[tuple[int, int, int, int]]]:
    """One sample page plus its ground-truth bubble bboxes."""
    if name == "jp-horizontal":
        img, draw = _page(900, 1300)
        f = _font(JP_FONT, 44)
        boxes = [
            _bubble(draw, 450, 300, 240, 130, "これは\nテストです", f),
            _bubble(draw, 300, 750, 200, 110, "こんにちは", _font(JP_FONT, 42)),
            _bubble(draw, 620, 1050, 220, 120, "検出の\n確認", _font(JP_FONT, 42)),
        ]
    elif name == "jp-vertical":
        img, draw = _page(820, 1200)
        boxes = [
            _bubble(draw, 560, 350, 190, 200, "これは\nたてがき", _font(JP_FONT, 40), vertical=True),
            _bubble(draw, 320, 830, 190, 160, "にほんご", _font(JP_FONT, 40), vertical=True),
        ]
    elif name == "la-horizontal":
        img, draw = _page(880, 1240)
        boxes = [
            _bubble(draw, 440, 320, 250, 120, "This is a\nspeech bubble", _font(LAT_FONT, 40)),
            _bubble(draw, 420, 760, 230, 120, "Detect me\nplease", _font(LAT_FONT, 40)),
        ]
    elif name == "no-text":
        img, draw = _page(800, 1100)
        draw.ellipse([100, 100, 400, 400], fill=(240, 240, 240), outline=(180, 180, 180), width=3)
        draw.rectangle([420, 600, 720, 900], fill=(225, 225, 225), outline=(170, 170, 170), width=3)
        boxes = []
    else:
        raise ValueError(name)
    return img, boxes


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


class _GeometrySource:
    def polygon(self, region_id: str):
        return ((1, 1), (2, 2), (3, 3))

    def boxes(self, region_id: str):
        return ()


class ManagedPngPageImageSource:
    """Mirrors the production frame contract: raw rgb32 (BGRA) pixels of the
    managed copy — what ``bootstrap.app``'s ``page_frame`` really returns."""

    def __init__(self, storage: ManagedFileStorage, managed_ref: str, width: int, height: int):
        self._path = Path(storage.absolute_path(managed_ref))
        self._width = width
        self._height = height

    def page_frame(self, page_id: str) -> ImageFrame:
        import numpy

        rgb = numpy.asarray(Image.open(self._path).convert("RGB"), dtype=numpy.uint8)
        bgra = numpy.dstack(
            (rgb[:, :, ::-1], numpy.full((self._height, self._width, 1), 255, dtype=numpy.uint8))
        )
        return ImageFrame(
            width=self._width,
            height=self._height,
            mode="rgb32",
            data=bgra.tobytes(),
        )

    def region_crop(self, page_id: str, region_id: str):
        raise AssertionError("detect seam must not need a region crop")

    def page_png(self, page_id: str) -> bytes:
        return self._path.read_bytes()


def run_seam_case(provider, work_root: Path, sample_name: str) -> dict:
    """Wire the real detector through the production seam and run one page.

    Returns the raw facts the 22 parametrized checks assert on.
    """
    from application.editing.service import RegionEditingService
    from application.tasks.service import PipelineService
    from domain.regions.entities import BBox, RegionGeometry, RegionOrigin
    from domain.tasks.models import CommandType, PipelineScope, ScopeType
    from ports.detection.ports import DetectionRequest, DetectionResult, RegionCandidate

    img, ground_truth = make_seam_sample(sample_name)
    width, height = img.width, img.height

    root = work_root / f"seam-{sample_name}"
    root.mkdir(parents=True, exist_ok=True)
    sample_png = root / f"{sample_name}.png"
    img.save(sample_png, format="PNG")

    conn, _ = open_database(
        root / "library.db",
        latest_known_schema_version=max(
            migration.schema_version for migration in default_migrations()
        ),
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
        ("book-1", "Book", NOW, NOW),
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES (?, ?, ?, ?, ?)",
        ("chapter-1", "book-1", "Chapter", NOW, NOW),
    )
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, source_filename, source_order,"
        " sort_order, source_hash, source_size_bytes, width, height,"
        " managed_original_ref, created_at, updated_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "page-1", "chapter-1", sample_png.name, 0, 0,
            sha256(sample_png), sample_png.stat().st_size, width, height,
            "original/" + sample_png.name, NOW, NOW,
        ),
    )
    conn.commit()
    storage = ManagedFileStorage(root / "managed")
    storage.ensure_layout()
    managed_path = Path(storage.absolute_path("original/" + sample_png.name))
    managed_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(sample_png, managed_path)

    editing = RegionEditingService(SqliteRegionRepository(conn))
    created: list[dict] = []

    def region_creator(page_id, polygon, reading_order, provenance):
        xs = [int(round(x)) for x, _ in polygon]
        ys = [int(round(y)) for _, y in polygon]
        region = editing.create_region(
            page_id,
            RegionGeometry(
                bbox=BBox(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)),
                polygon=tuple((int(round(x)), int(round(y))) for x, y in polygon),
            ),
            reading_order=reading_order,
            origin=RegionOrigin.MACHINE,
        )
        created.append({"region_id": region.region_id, "polygon": [list(map(float, p)) for p in polygon]})
        return region.region_id

    image_source = ManagedPngPageImageSource(storage, "original/" + sample_png.name, width, height)
    handlers = ProductionHandlers(
        HandlerDependencies(
            registry=ProviderRegistry(),
            regions=SqliteRegionRepository(conn),
            region_writer=RegionStepWriter(conn, SqliteRegionRepository(conn)),
            artifacts=ArtifactStepWriter(conn, storage),
            images=image_source,
            geometry=_GeometrySource(),
            retry_policy=RetryPolicy(max_attempts=1, backoff_seconds=0),
            detector=provider,
            region_creator=region_creator,
        )
    )
    service = build_production_pipeline(
        conn,
        handlers=handlers.as_mapping(),
        settings={"ocr": {"script": "japanese"}},
    )

    managed_files = [p for p in (root / "managed").rglob("*") if p.is_file()]
    hashes_before = {str(p): sha256(p) for p in managed_files}
    sample_before = sha256(sample_png)

    run = service.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1"),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    hashes_after = {str(p): sha256(p) for p in managed_files}
    sample_after = sha256(sample_png)

    detect_step = executed.step_runs[0]
    regions_repo = SqliteRegionRepository(conn)
    db_regions = regions_repo.list_regions("page-1")
    revisions = conn.execute(
        "SELECT region_id, revision_no, origin FROM region_revisions ORDER BY region_id, revision_no"
    ).fetchall()

    hits = 0
    for cand in created:
        xs = [p[0] for p in cand["polygon"]]
        ys = [p[1] for p in cand["polygon"]]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        if any(g[0] <= cx <= g[2] and g[1] <= cy <= g[3] for g in ground_truth):
            hits += 1
    in_bounds = all(
        0 <= p[0] <= width and 0 <= p[1] <= height for cand in created for p in cand["polygon"]
    )
    later = [(step.step_type, step.error_code) for step in executed.step_runs[1:]]

    case = {
        "sample": sample_name,
        "detect_status": str(detect_step.status),
        "detect_error_code": detect_step.error_code,
        "created_count": len(created),
        "db_region_count": len(db_regions),
        "revision_count": len(revisions),
        "origins": {row[2] for row in revisions},
        "in_bounds": in_bounds,
        "hits": hits,
        "ground_truth_bubbles": len(ground_truth),
        "sources_unchanged": hashes_before == hashes_after and sample_before == sample_after,
        "later_steps": later,
        "run_status": str(executed.status),
    }
    conn.close()
    return case


def seam_checks(case: dict) -> dict[str, bool]:
    """The 22 released checks, one bool each (parametrized below)."""
    if case["sample"] == "no-text":
        code = str(case["detect_error_code"] or "")
        return {"no_text_typed_invalid_input": "INVALID_INPUT" in code}
    later_all_typed = bool(case["later_steps"]) and all(
        error_code for _, error_code in case["later_steps"]
    )
    return {
        "configured_path_ok": case["detect_error_code"] is None,
        "persisted_machine_regions": case["db_region_count"] > 0,
        "machine_origin_revisions": (
            case["revision_count"] >= case["db_region_count"]
            and case["origins"] == {"machine"}
        ),
        "coordinates_in_bounds": case["in_bounds"],
        "hits_ground_truth": case["hits"] > 0,
        "sources_unchanged": case["sources_unchanged"],
        "no_silent_fallback": later_all_typed,
    }


#: sample -> check names, in the released evaluation's order (7 + 7 + 7 + 1).
SEAM_CHECK_MATRIX: list[tuple[str, str]] = [
    *[
        ("jp-horizontal", "configured_path_ok"),
        ("jp-horizontal", "persisted_machine_regions"),
        ("jp-horizontal", "machine_origin_revisions"),
        ("jp-horizontal", "coordinates_in_bounds"),
        ("jp-horizontal", "hits_ground_truth"),
        ("jp-horizontal", "sources_unchanged"),
        ("jp-horizontal", "no_silent_fallback"),
    ],
    *[
        ("jp-vertical", "configured_path_ok"),
        ("jp-vertical", "persisted_machine_regions"),
        ("jp-vertical", "machine_origin_revisions"),
        ("jp-vertical", "coordinates_in_bounds"),
        ("jp-vertical", "hits_ground_truth"),
        ("jp-vertical", "sources_unchanged"),
        ("jp-vertical", "no_silent_fallback"),
    ],
    *[
        ("la-horizontal", "configured_path_ok"),
        ("la-horizontal", "persisted_machine_regions"),
        ("la-horizontal", "machine_origin_revisions"),
        ("la-horizontal", "coordinates_in_bounds"),
        ("la-horizontal", "hits_ground_truth"),
        ("la-horizontal", "sources_unchanged"),
        ("la-horizontal", "no_silent_fallback"),
    ],
    ("no-text", "no_text_typed_invalid_input"),
]

assert len(SEAM_CHECK_MATRIX) == 22
