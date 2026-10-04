"""fixture 库构造器（测试+冒烟共用）：生产冻结 DDL（v1–v4）+ 混合 revision 链。

fixture schema 与生产完全同构：直接执行 src/infrastructure/sqlite/schema.py 的
MIGRATION_V1..V4 SQL（只读导入，零 src 修改）并登记 schema_migrations。
链形态按生产写路径构造：全快照 revision、origin ∈ {machine,user,restored}、
restored_from_revision_id 溯源（service.py:550-572 restore 语义）。

14 个 region 的场景矩阵与期望见 tests/test_scanner.py 模块 docstring。
"""

from __future__ import annotations

import json
from pathlib import Path

from sfx_correction_exporter import REPO_ROOT

BOOK_ID = "bk-fixture"
CHAPTER_ID = "ch-fixture"
PAGE_MAIN = "pg1"
PAGE_BJ13 = "pgBJ13"
USER_LIBRARY_LICENSE = {
    "license_class": "user_library_source",
    "redistributable": False,
    "source_url": "",
    "registered": True,
    "registered_per": "user_ruling_2026-10-04_训练质量效率优先_许可降权备案: 全备案不阻断",
    "blocking": False,
}


def repo_cases_json() -> Path | None:
    p = REPO_ROOT / "test_assets" / "comic_golden_suite" / "manifests" / "cases.json"
    return p if p.exists() else None


def load_cases_index() -> dict[str, dict]:
    path = repo_cases_json()
    if path is None:
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {c["case_id"]: c for c in raw.get("cases", [])}


# ---------------------------------------------------------------------------
# snapshot 构造（镜像 src/domain/regions/entities.py:267-288 snapshot_state 字段集）
# ---------------------------------------------------------------------------

def _text(edited: str = "", edited_confirmed: bool = False, manual_edited: bool = False) -> dict:
    return {
        "ocr_text": "",
        "machine_translation": "",
        "edited_translation": edited,
        "final_translation": "",
        "final_source": "",
        "edited_confirmed": edited_confirmed,
        "manual_edited": manual_edited,
        "translation_locked": False,
    }


def _style() -> dict:
    return {
        "font_family": "",
        "font_size": None,
        "text_color": "",
        "stroke_color": "",
        "stroke_width": 0.0,
        "auto_font_size_enabled": True,
    }


def snap(
    region_type: str,
    geometry: dict,
    reading_order: int = 1,
    sfx_policy: str = "skip",
    text: dict | None = None,
) -> dict:
    return {
        "region_type": region_type,
        "reading_order": reading_order,
        "geometry": geometry,
        "text": text or _text(),
        "style": _style(),
        "sfx_policy": sfx_policy,
        "region_locked": 0,
        "translation_locked": 0,
        "inpaint_locked": 0,
    }


def geom(x0: int, y0: int, x1: int, y1: int, polygon: list | None = None) -> dict:
    return {
        "bbox": [x0, y0, x1, y1],
        "polygon": polygon if polygon is not None else [[x0, y0], [x1, y0], [x1, y1], [x0, y1]],
    }


# ---------------------------------------------------------------------------
# schema 与行写入
# ---------------------------------------------------------------------------

def apply_production_schema(conn) -> None:
    """执行生产冻结迁移 SQL（v1–v4）并登记 schema_migrations。"""
    from infrastructure.sqlite.schema import default_migrations

    for m in default_migrations():
        conn.executescript(m.sql)
        conn.execute(
            "INSERT INTO schema_migrations (schema_version, migration_name, applied_at, checksum)"
            " VALUES (?, ?, ?, ?)",
            (m.schema_version, m.migration_name, "2026-10-04T00:00:00Z", m.checksum),
        )
    conn.commit()


def _add_book_chapter_page(conn, page_id: str, image_path: Path, source_filename: str) -> None:
    from PIL import Image

    with Image.open(image_path) as im:
        w, h = im.size
    exists = conn.execute(
        "SELECT 1 FROM books WHERE book_id = ?", (BOOK_ID,)
    ).fetchone()
    if not exists:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (BOOK_ID, "fixture book", "2026-10-04T00:00:00Z", "2026-10-04T00:00:00Z"),
        )
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, sort_order, created_at, updated_at)"
            " VALUES (?, ?, ?, 1, ?, ?)",
            (CHAPTER_ID, BOOK_ID, "fixture chapter", "2026-10-04T00:00:00Z", "2026-10-04T00:00:00Z"),
        )
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at,"
        " source_filename, source_order, width, height, managed_original_ref)"
        " VALUES (?, ?, 1, ?, ?, ?, 0, ?, ?, ?)",
        (page_id, CHAPTER_ID, "2026-10-04T00:00:00Z", "2026-10-04T00:00:00Z",
         source_filename, w, h, image_path.as_posix()),
    )


def _add_region(
    conn,
    region_id: str,
    page_id: str,
    chain: list[tuple[str, dict, str, str | None]],
    deleted_at: str | None = None,
) -> None:
    """chain: [(origin, snapshot, review_state, restored_from_revision_no|None), ...]"""
    rev_ids: list[str] = []
    for i, (origin, snapshot, review_state, restored_from_no) in enumerate(chain, start=1):
        rev_id = f"{region_id}-r{i:03d}"
        rev_ids.append(rev_id)
        conn.execute(
            "INSERT INTO region_revisions (region_revision_id, region_id, revision_no,"
            " snapshot_json, origin, review_state, is_pinned, restored_from_revision_id, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)",
            (
                rev_id, region_id, i, json.dumps(snapshot, ensure_ascii=False),
                origin, review_state,
                f"{region_id}-r{restored_from_no:03d}" if restored_from_no else None,
                "2026-10-04T00:00:0Z"[:19] + f"{i:02d}Z",
            ),
        )
    last = chain[-1][1]
    conn.execute(
        "INSERT INTO regions (region_id, page_id, region_type, reading_order, geometry_json,"
        " text_json, style_json, sfx_policy, region_locked, translation_locked, inpaint_locked,"
        " current_revision_id, created_at, updated_at, deleted_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, ?, ?, ?, ?)",
        (
            region_id, page_id, last["region_type"], last["reading_order"],
            json.dumps(last["geometry"], ensure_ascii=False),
            json.dumps(last["text"], ensure_ascii=False),
            json.dumps(last["style"], ensure_ascii=False),
            last["sfx_policy"], rev_ids[-1],
            "2026-10-04T00:00:00Z", "2026-10-04T00:00:00Z", deleted_at,
        ),
    )


def write_tiny_png(path: Path, width: int = 64, height: int = 48) -> Path:
    from PIL import Image

    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (width, height), (250, 250, 250)).save(path, format="PNG")
    return path


# ---------------------------------------------------------------------------
# 场景矩阵（链定义；期望断言在 tests/）
# ---------------------------------------------------------------------------

def _chains() -> dict[str, dict]:
    gA = geom(10, 10, 60, 50)
    gB = geom(70, 10, 120, 50)
    gC0 = geom(130, 10, 180, 50)
    gC1 = geom(130, 10, 180, 50, polygon=[[130, 10], [180, 14], [176, 50], [132, 46]])
    gH = geom(190, 10, 240, 50)
    gI = geom(250, 10, 300, 50)
    gI2 = geom(250, 12, 300, 52, polygon=[[250, 12], [300, 12], [300, 52], [250, 52]])
    gN = geom(20, 20, 50, 40, polygon=[])
    return {
        "rgA": {  # 基本纠错：m(speech) → u(sfx)，存活，partial
            "page": PAGE_MAIN,
            "chain": [
                ("machine", snap("speech", gA), "unreviewed", None),
                ("user", snap("sfx", gA), "unreviewed", None),
            ],
        },
        "rgB": {  # 被撤销纠错：restore 回 r1（speech）
            "page": PAGE_MAIN,
            "chain": [
                ("machine", snap("speech", gB), "unreviewed", None),
                ("user", snap("sfx", gB), "unreviewed", None),
                ("restored", snap("speech", gB), "needs_review", 1),
            ],
        },
        "rgC": {  # 纯几何编辑
            "page": PAGE_MAIN,
            "chain": [
                ("machine", snap("speech", gC0), "unreviewed", None),
                ("user", snap("speech", gC1), "unreviewed", None),
            ],
        },
        "rgD": {  # 纯文本编辑（needs_review 文本先例）
            "page": PAGE_MAIN,
            "chain": [
                ("machine", snap("speech", gB), "unreviewed", None),
                ("user", snap("speech", gB, text=_text("ハチン")), "needs_review", None),
            ],
        },
        "rgE": {  # 机器改标 origin=machine：非纠错事件
            "page": PAGE_MAIN,
            "chain": [
                ("machine", snap("speech", gA), "unreviewed", None),
                ("machine", snap("sfx", gA, sfx_policy="translate"), "unreviewed", None),
            ],
        },
        "rgF": {  # 二次改标取代首次：r2 被改判；r3 sfx→title 非 sfx 向
            "page": PAGE_MAIN,
            "chain": [
                ("machine", snap("speech", gB), "unreviewed", None),
                ("user", snap("sfx", gB), "unreviewed", None),
                ("user", snap("title", gB), "unreviewed", None),
            ],
        },
        "rgG": {  # 撤销后再纠错：r2 撤销(a)；r4 存活
            "page": PAGE_MAIN,
            "chain": [
                ("machine", snap("speech", gC0), "unreviewed", None),
                ("user", snap("sfx", gC0), "unreviewed", None),
                ("restored", snap("speech", gC0), "needs_review", 1),
                ("user", snap("sfx", gC0), "unreviewed", None),
            ],
        },
        "rgH": {  # 用户自建 region 再纠错：complete（首笔 user）
            "page": PAGE_MAIN,
            "chain": [
                ("user", snap("speech", gH), "unreviewed", None),
                ("user", snap("sfx", gH), "unreviewed", None),
            ],
        },
        "rgI": {  # 纠错→用户几何编辑→restore 回 r2（类型 sfx）：r2 存活；complete
            "page": PAGE_MAIN,
            "chain": [
                ("machine", snap("speech", gI), "unreviewed", None),
                ("user", snap("sfx", gI), "unreviewed", None),
                ("user", snap("sfx", gI2), "unreviewed", None),
                ("restored", snap("sfx", gI), "needs_review", 2),
            ],
        },
        "rgJ": {  # 纯 reading_order 编辑
            "page": PAGE_MAIN,
            "chain": [
                ("machine", snap("speech", gB, reading_order=1), "unreviewed", None),
                ("user", snap("speech", gB, reading_order=2), "unreviewed", None),
            ],
        },
        "rgK": {  # 非 sfx 向纠错 sfx→speech：识别层报告、资格层排除
            "page": PAGE_MAIN,
            "chain": [
                ("machine", snap("sfx", gC1, sfx_policy="translate"), "unreviewed", None),
                ("user", snap("speech", gC1), "unreviewed", None),
            ],
        },
        "rgL": {  # 软删除 region：整链跳过
            "page": PAGE_MAIN,
            "deleted_at": "2026-10-04T01:00:00Z",
            "chain": [
                ("machine", snap("speech", gA), "unreviewed", None),
                ("user", snap("sfx", gA), "unreviewed", None),
            ],
        },
        "rgM": {  # BJ13 映射页纠错：challenge + 许可继承
            "page": PAGE_BJ13,
            "chain": [
                ("machine", snap("speech", gB), "unreviewed", None),
                ("user", snap("sfx", gB), "unreviewed", None),
            ],
        },
        "rgN": {  # 纯 bbox region（空 polygon）：回退 bbox 四角
            "page": PAGE_MAIN,
            "chain": [
                ("machine", snap("speech", gN), "unreviewed", None),
                ("user", snap("sfx", gN), "unreviewed", None),
            ],
        },
    }


def build_fixture_db(base_dir: Path) -> dict:
    import sqlite3

    base_dir = Path(base_dir)
    assets = base_dir / "assets"
    pg1_png = write_tiny_png(assets / f"{PAGE_MAIN}.png")
    pg_bj_png = write_tiny_png(assets / "vol03_p0048.png")

    db_path = base_dir / "fixture-library.db"
    conn = sqlite3.connect(db_path)
    try:
        apply_production_schema(conn)
        _add_book_chapter_page(conn, PAGE_MAIN, pg1_png, "page_001.png")
        _add_book_chapter_page(conn, PAGE_BJ13, pg_bj_png, "vol03_p0048.png")
        for rid, spec in _chains().items():
            _add_region(
                conn, rid, spec["page"],
                [
                    (origin, snapshot, review_state, restored_no)
                    for origin, snapshot, review_state, restored_no in spec["chain"]
                ],
                deleted_at=spec.get("deleted_at"),
            )
        conn.commit()
    finally:
        conn.close()
    return {
        "db_path": db_path,
        "assets_dir": assets,
        "page_images": {PAGE_MAIN: pg1_png, PAGE_BJ13: pg_bj_png},
        "book_id": BOOK_ID,
    }


def build_empty_db(path: Path) -> Path:
    """有 schema 无 region 事实的库（真库冒烟同路径：CORRECTIONS_EMPTY=expected）。"""
    import sqlite3

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        apply_production_schema(conn)
    finally:
        conn.close()
    return path


def make_registry_manifest(
    out_dir: Path, group: str, split: str, duplicate_of_fixture: dict | None = None
) -> Path:
    """构造 T1a 格式注册表 manifest（组继承/去重测试用）。

    duplicate_of_fixture 提供时额外放一条与 fixture rgA 样本「同图 sha+同框集合」
    的已册样本（reg-dup-000），用于导出期去重剔除断言。
    """
    import hashlib

    from sfx_data_infra.atomicio import write_manifest
    from sfx_data_infra.schema import BoxAnnotation, ImageRef, SampleRecord

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    now = "2026-10-04T00:00:00Z"
    records: list[SampleRecord] = [
        SampleRecord(
            sample_id="reg-inh-000",
            image=ImageRef(path="registry.png", sha256=hashlib.sha256(b"registry").hexdigest(), width=64, height=48),
            boxes=[BoxAnnotation(polygon=[[1.0, 1.0], [9.0, 1.0], [9.0, 9.0], [1.0, 9.0]], cls="sfx")],
            annotation_status="partial",
            provenance={"type": "asset_case", "source": "registry_fixture"},
            group=group,
            split=split,
            created_at=now,
        )
    ]
    if duplicate_of_fixture is not None:
        pg1 = duplicate_of_fixture["page_images"][PAGE_MAIN]
        from sfx_data_infra.hash import sha256_file

        records.append(
            SampleRecord(
                sample_id="reg-dup-000",
                image=ImageRef(path="dup.png", sha256=sha256_file(pg1), width=64, height=48),
                # 与 rgA settled 几何（gA 四角，float 化后）完全一致 → 精确重复
                boxes=[BoxAnnotation(polygon=[[10.0, 10.0], [60.0, 10.0], [60.0, 50.0], [10.0, 50.0]], cls="sfx")],
                annotation_status="partial",
                provenance={"type": "asset_case", "source": "registry_fixture"},
                group=group,
                split=split,
                created_at=now,
            )
        )
    path = out_dir / "manifest.registry.json"
    write_manifest(path, records, extra={"manifest_set": "registry_fixture", "task": "fixture"})
    return path
