"""AC7 校验：9 条真实关联查询必须在真实 Core schema 上可执行且不报错。

用 assemble_production_core 建真实的 Core 数据根（含全部迁移），而不是从
schema.py 里用正则抠 SQL —— 后者会因为语句内的分号而误判。
"""
import sys
import tempfile
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga")
sys.path.insert(0, str(REPO / "src"))

from bootstrap.core_service import assemble_production_core  # noqa: E402

root = Path(tempfile.mkdtemp(prefix="ac7-schema-"))
core = assemble_production_core(root / "data")
try:
    conn = core.conn

    version = conn.execute(
        "SELECT CAST(value_json AS INTEGER) FROM application_metadata"
        " WHERE metadata_key = 'schema_version'"
    ).fetchone()
    print(f"schema_version={version[0] if version else None}")

    queries = {
        "books": "SELECT COUNT(*) FROM books WHERE book_id = ?",
        "chapters": "SELECT COUNT(*) FROM chapters WHERE book_id = ?",
        "reading_progress": "SELECT COUNT(*) FROM reading_progress WHERE book_id = ?",
        "book_tags": "SELECT COUNT(*) FROM book_tags WHERE book_id = ?",
        "media_artifacts": "SELECT COUNT(*) FROM media_artifacts WHERE book_id = ?",
        "pages": (
            "SELECT COUNT(*) FROM pages WHERE chapter_id IN "
            "(SELECT chapter_id FROM chapters WHERE book_id = ?)"
        ),
        "regions": (
            "SELECT COUNT(*) FROM regions WHERE page_id IN ("
            " SELECT p.page_id FROM pages p"
            " JOIN chapters c ON c.chapter_id = p.chapter_id"
            " WHERE c.book_id = ?)"
        ),
        "region_revisions": (
            "SELECT COUNT(*) FROM region_revisions WHERE region_id IN ("
            " SELECT r.region_id FROM regions r"
            " JOIN pages p ON p.page_id = r.page_id"
            " JOIN chapters c ON c.chapter_id = p.chapter_id"
            " WHERE c.book_id = ?)"
        ),
        "artifact_revisions": (
            "SELECT COUNT(*) FROM artifact_revisions WHERE artifact_id IN ("
            " SELECT artifact_id FROM media_artifacts WHERE book_id = ?)"
        ),
    }

    ok = 0
    for name, query in queries.items():
        try:
            rows = conn.execute(query, ("probe-book",)).fetchone()[0]
            print(f"   {name:20s} OK rows={rows}")
            ok += 1
        except Exception as exc:  # noqa: BLE001
            print(f"   {name:20s} FAIL {type(exc).__name__}: {exc}")
    print(f"queries_ok={ok}/{len(queries)}")
finally:
    core.conn.close()
print("done")
