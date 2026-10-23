"""TOOL-SOFTWARE-SMOKE-1: unit tests for the smoke tool itself.

The slow/full four-layer run is the acceptance evidence, not a pytest case here:
these tests keep the tool's report/selection/CLI logic cheap to verify.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.smoke import model, report  # noqa: E402
from tools.smoke.plugins import LAYERS, main, select_layers  # noqa: E402


def _check(check_id: str, status: str, code: str | None = None) -> model.CheckResult:
    return model.CheckResult(id=check_id, name=check_id, status=status, code=code)


def test_layer_and_overall_status_derivation() -> None:
    passing = model.LayerResult(id="a", name="A", checks=[_check("a1", model.PASS)])
    failing = model.LayerResult(id="b", name="B", checks=[_check("b1", model.FAIL, "X")])
    blocked = model.LayerResult(id="c", name="C", checks=[_check("c1", model.BLOCKED, "Y")])
    skipped = model.LayerResult(id="d", name="D", skipped=True)

    assert passing.status == model.PASS
    assert failing.status == model.FAIL
    assert blocked.status == model.BLOCKED
    assert skipped.status == model.SKIP
    assert model.overall_status([passing, skipped]) == model.PASS
    assert model.overall_status([passing, failing]) == model.FAIL
    assert model.overall_status([passing, blocked]) == model.BLOCKED
    assert model.exit_code([passing, skipped]) == 0
    assert model.exit_code([failing]) == 1
    assert model.exit_code([blocked]) == 1


def test_run_checks_maps_failure_skip_and_unexpected_errors() -> None:
    def ok(_context):
        return {"value": 1}

    def fails(_context):
        raise model.SmokeFailure("CHECK_FAILED", "boom")

    def skips(_context):
        raise model.SmokeSkip("CHECK_SKIPPED", "optional")

    def crashes(_context):
        raise RuntimeError("unexpected")

    entries = [
        (model.CheckSpec("OK", "ok"), ok),
        (model.CheckSpec("FAIL", "fail"), fails),
        (model.CheckSpec("SKIP", "skip"), skips),
        (model.CheckSpec("CRASH", "crash"), crashes),
    ]
    results = model.run_checks(entries, object())
    by_id = {item.id: item for item in results}
    assert by_id["OK"].status == model.PASS and by_id["OK"].detail == {"value": 1}
    assert by_id["FAIL"].status == model.FAIL and by_id["FAIL"].code == "CHECK_FAILED"
    assert by_id["SKIP"].status == model.SKIP and by_id["SKIP"].code == "CHECK_SKIPPED"
    assert by_id["CRASH"].status == model.FAIL
    assert by_id["CRASH"].code == "UNEXPECTED_CHECK_ERROR"


def test_all_blocked_never_reports_pass() -> None:
    specs = (model.CheckSpec("A", "a"), model.CheckSpec("B", "b"))
    results = model.all_blocked(specs, "BLOCKED_ENV", "missing")
    assert [item.status for item in results] == [model.BLOCKED, model.BLOCKED]
    assert {item.code for item in results} == {"BLOCKED_ENV"}


def test_select_layers_only_skip_and_unknown() -> None:
    assert select_layers(None, None) == ["core", "wire", "frontend", "packaged"]
    assert select_layers("wire,core", None) == ["wire", "core"]
    assert select_layers(None, "frontend,packaged") == ["core", "wire"]
    assert select_layers("core,wire", "wire") == ["core"]
    with pytest.raises(ValueError):
        select_layers("nope", None)


def test_report_summary_and_environment_boundaries() -> None:
    layers = [
        model.LayerResult(
            id="core",
            name="Core 沙箱层",
            checks=[_check("CORE-1", model.PASS)],
            duration_ms=12,
        ),
        model.LayerResult(id="frontend", name="前端层", skipped=True, skip_reason="显式跳过"),
    ]
    payload = report.build_report(
        layers,
        started_at="2026-10-23T00:00:00+00:00",
        duration_ms=34,
        command=["--only", "core"],
        repack=False,
    )
    assert payload["schema"] == report.SCHEMA
    assert payload["status"] == model.PASS
    assert payload["summary"] == {
        "status": model.PASS,
        "layers": 2,
        "checks": 1,
        "passed": 1,
        "failed": 0,
        "skipped": 0,
        "blocked": 0,
    }
    assert payload["environment"]["screenshots"] == "disabled"
    assert payload["environment"]["gui"] == "not_used"
    assert payload["environment"]["mouse"] == "not_used"
    summary = report.render_summary(payload)
    assert "PASS" in summary and "Core 沙箱层" in summary


def test_cli_lists_checks_from_module_entry_point() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "tools.smoke.plugins", "--list-checks"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    for layer_id, _name, module in LAYERS:
        for check in module.CHECKS:
            assert f"{layer_id}\t{check.id}\t" in completed.stdout


def test_cli_rejects_unknown_layer() -> None:
    assert main(["--only", "nope"]) == 2


def test_cli_wire_layer_json_report(tmp_path, capsys) -> None:
    json_path = tmp_path / "wire-report.json"
    exit_code = main(["--only", "wire", "--json", str(json_path)])
    assert exit_code == 0
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["schema"] == report.SCHEMA
    assert payload["status"] == model.PASS
    layers = {layer["id"]: layer for layer in payload["layers"]}
    assert layers["wire"]["status"] == model.PASS
    assert layers["core"]["status"] == model.SKIP


def test_cli_json_stdout_mode() -> None:
    # main() writes JSON to stdout and the human summary to stderr.
    exit_code = main(["--only", "wire", "--json", "-"])
    assert exit_code == 0
