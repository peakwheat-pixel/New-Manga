"""AC5：CLI（--help/selfcheck EXIT=0）+ SQLite 只读铁律 + 空库 CORRECTIONS_EMPTY 路径。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from sfx_correction_exporter import fixture

PKG_DIR = Path(__file__).resolve().parents[1]


def _run_cli(args, cwd=None):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PKG_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "sfx_correction_exporter", *args],
        capture_output=True, text=True, env=env, cwd=cwd or str(PKG_DIR),
    )


def test_help_exit_zero():
    r = _run_cli(["--help"])
    assert r.returncode == 0, r.stderr
    assert "selfcheck" in r.stdout and "export" in r.stdout


def test_selfcheck_exit_zero():
    r = _run_cli(["selfcheck"])
    assert r.returncode == 0, r.stdout + r.stderr
    assert "SELFCHECK PASS" in r.stdout


def test_export_fixture_smoke_exit_zero(tmp_path):
    fx = fixture.build_fixture_db(tmp_path / "fx")
    out = tmp_path / "sfx-corrections"
    summary_out = tmp_path / "summary.json"
    r = _run_cli([
        "export", "--db", str(fx["db_path"]),
        "--out", str(out),
        "--summary-out", str(summary_out),
    ])
    assert r.returncode == 0, r.stdout + r.stderr
    summary = json.loads(summary_out.read_text(encoding="utf-8"))
    assert summary["corrections_empty"] is False
    assert summary["db_readonly"] is True
    assert (out / "manifest.json").exists()


def test_export_empty_db_corrections_empty_expected(tmp_path):
    """真库冒烟同路径：有 schema 无 region 事实 → EXIT=0 + corrections_empty=true。"""
    db = fixture.build_empty_db(tmp_path / "empty" / "library.db")
    out = tmp_path / "out"
    summary_out = tmp_path / "summary.json"
    r = _run_cli([
        "export", "--db", str(db), "--out", str(out),
        "--summary-out", str(summary_out),
    ])
    assert r.returncode == 0, r.stdout + r.stderr
    summary = json.loads(summary_out.read_text(encoding="utf-8"))
    assert summary["corrections_empty"] is True
    assert summary["scan"]["regions_scanned"] == 0
    assert summary["scan"]["events_total"] == 0


def test_db_missing_fails_closed(tmp_path):
    r = _run_cli(["export", "--db", str(tmp_path / "nope.db")])
    assert r.returncode != 0  # mode=ro 下库不存在必须失败，不得静默创建


def test_readonly_enforcement_programmatic(tmp_path):
    """只读铁律：mode=ro URI + PRAGMA query_only；写尝试必须抛错。"""
    import sqlite3

    from sfx_correction_exporter.db import open_readonly
    fx = fixture.build_fixture_db(tmp_path / "fx")
    conn = open_readonly(fx["db_path"])
    try:
        assert conn.execute("PRAGMA query_only").fetchone()[0] == 1
        with pytest.raises(sqlite3.Error):
            conn.execute("UPDATE regions SET region_type='sfx'")
        with pytest.raises(sqlite3.Error):
            conn.execute("DELETE FROM region_revisions")
    finally:
        conn.close()
