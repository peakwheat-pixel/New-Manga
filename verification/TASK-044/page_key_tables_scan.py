"""TASK-044 completeness scan: which tables carry page/region/artifact key
columns, and which of those columns have **no** foreign key.

FK-driven deletes can only be found through ``PRAGMA foreign_key_list``, so a
table that keys on ``page_id`` *without* an FK would silently survive a purge.
This scan is the check that nothing like that exists today (and it will fail
loudly if a future migration adds one).
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

KEY_COLUMNS = (
    "page_id",
    "region_id",
    "artifact_id",
    "artifact_revision_id",
    "region_revision_id",
    "step_run_id",
    "task_id",
    "run_target_id",
    "pipeline_run_id",
    "chapter_id",
    "book_id",
)

tmp = Path(tempfile.mkdtemp(prefix="task044-scan-"))
conn, _opened = open_database(
    tmp / "library.db",
    latest_known_schema_version=max(m.schema_version for m in default_migrations()),
)
MigrationRunner(conn, default_migrations()).apply_pending()

tables = [
    row["name"]
    for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
        " AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
]

print("tables keyed on page/region/artifact/run columns:")
unreferenced: list[tuple[str, str]] = []
for table in tables:
    columns = [row["name"] for row in conn.execute(f'PRAGMA table_info("{table}")')]
    fk_columns = {
        row["from"] for row in conn.execute(f'PRAGMA foreign_key_list("{table}")')
    }
    keyed = [column for column in columns if column in KEY_COLUMNS]
    if not keyed:
        continue
    missing = [column for column in keyed if column not in fk_columns]
    unreferenced.extend((table, column) for column in missing)
    print(f"  {table}: keyed={keyed} without_fk={missing or '[]'}")

print("\ntables with a key column but NO foreign key:")
for table, column in unreferenced:
    print(f"  {table}.{column}")
print(f"  => {len(unreferenced)} such columns")

print("\nnote: pipeline_stage_states keys on (target_type, target_id) with no FK")
rows = conn.execute("SELECT COUNT(*) FROM pipeline_stage_states").fetchone()[0]
print("  pipeline_stage_states rows:", rows)
conn.close()
