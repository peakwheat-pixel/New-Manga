"""Machine-readable JSON report and the human-readable Chinese summary."""

from __future__ import annotations

import json
from pathlib import Path
import platform
import sys
from typing import Sequence

from tools.smoke import util
from tools.smoke.model import (
    BLOCKED,
    FAIL,
    SKIP,
    LayerResult,
    overall_status,
)

SCHEMA = "nm-software-smoke/1"


def _counts(layers: Sequence[LayerResult]) -> dict[str, int]:
    checks = [check for layer in layers for check in layer.checks]
    return {
        "layers": len(layers),
        "checks": len(checks),
        "passed": sum(1 for check in checks if check.status == "PASS"),
        "failed": sum(1 for check in checks if check.status == FAIL),
        "skipped": sum(1 for check in checks if check.status == SKIP),
        "blocked": sum(1 for check in checks if check.status == BLOCKED),
    }


def _sanitized_command(command: Sequence[str]) -> list[str]:
    """Keep the report free of host-absolute paths (repo paths stay relative)."""

    sanitized: list[str] = []
    for item in command:
        try:
            path = Path(item)
            if path.is_absolute():
                try:
                    sanitized.append(path.relative_to(util.REPO_ROOT).as_posix())
                except ValueError:
                    sanitized.append("<absolute-path>")
                continue
        except OSError:
            pass
        sanitized.append(item)
    return sanitized


def build_report(
    layers: Sequence[LayerResult],
    *,
    started_at: str,
    duration_ms: int,
    command: Sequence[str],
    repack: bool,
) -> dict:
    counts = _counts(layers)
    status = overall_status(layers)
    return {
        "schema": SCHEMA,
        "generated_at": util.now_iso(),
        "started_at": started_at,
        "duration_ms": duration_ms,
        "status": status,
        "command": _sanitized_command(command),
        "environment": {
            "platform": sys.platform,
            "python": platform.python_version(),
            "repack": repack,
            "screenshots": "disabled",
            "gui": "not_used",
            "mouse": "not_used",
        },
        "summary": {"status": status, **counts},
        "layers": [layer.to_dict() for layer in layers],
    }


def write_json(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def render_summary(report: dict, *, json_path: Path | None = None) -> str:
    summary = report["summary"]
    overall = report["status"]
    total_ms = report["duration_ms"]
    lines = [
        f"NM 软件检查工具 v1 — {overall}（{summary['layers']} 层，"
        f"{summary['checks']} 项检查，{total_ms / 1000:.1f}s）"
    ]
    for layer in report["layers"]:
        status = layer["status"]
        if status == SKIP:
            reason = layer.get("skip_reason") or "显式跳过"
            lines.append(f"  [SKIP] {layer['name']}（{reason}）")
            continue
        lines.append(
            f"  [{status}] {layer['name']}（{len(layer['checks'])} 项，"
            f"{layer['duration_ms'] / 1000:.1f}s）"
        )
        if status in (FAIL, BLOCKED):
            for check in layer["checks"]:
                if check["status"] in (FAIL, BLOCKED):
                    code = check["code"] or "-"
                    lines.append(
                        f"    - {check['id']}（{code}）：{check['message'] or check['name']}"
                    )
    if json_path is not None:
        lines.append(f"报告：{json_path}")
    return "\n".join(lines)
