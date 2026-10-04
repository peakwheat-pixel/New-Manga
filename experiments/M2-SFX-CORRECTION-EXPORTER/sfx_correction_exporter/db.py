"""SQLite 只读铁律（AC5）。

镜像 src/infrastructure/sqlite/connection.py:367-374 的 open_readonly 语义
（URI mode=ro + PRAGMA query_only=ON；本 Task 零 src，故在包内自持同语义实现，
不 import src 连接层以避免拖入迁移器副作用）。
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


def open_readonly(db_path: str | Path) -> sqlite3.Connection:
    """以 URI mode=ro 打开库；库不存在必须失败（不静默创建）。"""
    path = Path(db_path)
    if not path.exists():
        raise FileNotFoundError(f"SQLite 库不存在（只读模式不创建）: {path}")
    uri = f"file:{path.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    return conn
