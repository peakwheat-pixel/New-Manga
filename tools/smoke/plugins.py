"""TOOL-SOFTWARE-SMOKE-1: headless software checks replacing manual GUI smoke.

Usage (from the repository root):

    python -m tools.smoke.plugins
    python -m tools.smoke.plugins --json verification/TOOL-SOFTWARE-SMOKE-1/smoke-report.json
    python -m tools.smoke.plugins --only core,wire
    python -m tools.smoke.plugins --skip packaged
    python -m tools.smoke.plugins --list-checks

Exit codes: 0 = PASS (explicit skips allowed), 1 = FAIL or BLOCKED, 2 = usage
or tool error. No GUI, no mouse and no screenshots are used.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

from tools.smoke import model, report, util
from tools.smoke.model import LayerResult, RunOptions
from tools.smoke.checks import core, frontend, packaged, wire

#: Ordered layer registry. The order is the execution order too.
LAYERS: tuple[tuple[str, str, object], ...] = (
    ("core", "Core 沙箱层", core),
    ("wire", "Wire 层", wire),
    ("frontend", "前端层", frontend),
    ("packaged", "打包层", packaged),
)
_LAYER_NAMES = {layer_id: name for layer_id, name, _module in LAYERS}
_LAYER_IDS = tuple(layer_id for layer_id, _name, _module in LAYERS)


class _UsageError(ValueError):
    pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.smoke.plugins",
        description="Headless software smoke checks (plugin/sandbox/wire/frontend/bundle).",
    )
    parser.add_argument(
        "--only",
        metavar="LAYERS",
        help=f"只运行指定层（逗号分隔：{', '.join(_LAYER_IDS)}）",
    )
    parser.add_argument(
        "--skip",
        metavar="LAYERS",
        help="显式跳过指定层（逗号分隔）；显式跳过不算失败",
    )
    parser.add_argument(
        "--json",
        metavar="PATH",
        help="把机器可读 JSON 报告写到 PATH；PATH 为 - 时输出到 stdout",
    )
    parser.add_argument(
        "--keep-artifacts",
        action="store_true",
        help="保留本次运行的临时目录（默认清理）",
    )
    parser.add_argument(
        "--repack",
        action="store_true",
        help="打包层额外复用 verify_bundled_python.ps1（会复制完整 Python 运行时）",
    )
    parser.add_argument(
        "--list-checks",
        action="store_true",
        help="只列出层与检查项 ID，不执行检查",
    )
    parser.add_argument("--verbose", action="store_true", help="保留更多控制台细节")
    return parser


def select_layers(only: str | None, skip: str | None) -> list[str]:
    """Resolve the selected layer ids; explicit skips are removed last."""

    selected = list(_LAYER_IDS)
    if only is not None:
        selected = _parse_layer_list(only)
    if skip is not None:
        for layer_id in _parse_layer_list(skip):
            if layer_id in selected:
                selected.remove(layer_id)
    return selected


def _parse_layer_list(value: str) -> list[str]:
    items = [item.strip() for item in value.split(",") if item.strip()]
    if not items:
        raise _UsageError("层列表为空")
    unknown = [item for item in items if item not in _LAYER_IDS]
    if unknown:
        raise _UsageError(
            f"未知层：{', '.join(unknown)}；可选：{', '.join(_LAYER_IDS)}"
        )
    return items


def _list_checks() -> None:
    for layer_id, name, module in LAYERS:
        for check in module.CHECKS:
            print(f"{layer_id}\t{check.id}\t{check.name}")


def _configure_output() -> None:
    """Keep piped/redirected output UTF-8 so evidence logs are readable."""

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def main(argv: list[str] | None = None) -> int:
    _configure_output()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        selected = select_layers(args.only, args.skip)
    except _UsageError as error:
        parser.print_usage(sys.stderr)
        print(f"错误：{error}", file=sys.stderr)
        return 2

    if args.list_checks:
        _list_checks()
        return 0

    run_root = util.make_run_root()
    options = RunOptions(run_root=run_root, repack=args.repack, verbose=args.verbose)
    started_at = util.now_iso()
    started = time.perf_counter()
    layers: list[LayerResult] = []
    keep_artifacts = bool(args.keep_artifacts)
    try:
        for layer_id, name, module in LAYERS:
            if layer_id not in selected:
                layers.append(
                    LayerResult(
                        id=layer_id,
                        name=name,
                        skipped=True,
                        skip_reason="显式跳过",
                    )
                )
                continue
            layer_started = time.perf_counter()
            checks = module.run(options)
            layers.append(
                LayerResult(
                    id=layer_id,
                    name=name,
                    checks=checks,
                    duration_ms=int((time.perf_counter() - layer_started) * 1000),
                )
            )
    except Exception as error:  # noqa: BLE001 - tool error, never a silent pass
        print(
            f"工具内部错误：{type(error).__name__}: {error}",
            file=sys.stderr,
        )
        return 2
    finally:
        if not keep_artifacts:
            util.remove_tree(run_root)

    duration_ms = int((time.perf_counter() - started) * 1000)
    payload = report.build_report(
        layers,
        started_at=started_at,
        duration_ms=duration_ms,
        command=sys.argv[1:] if argv is None else argv,
        repack=args.repack,
    )
    json_path: Path | None = None
    if args.json and args.json != "-":
        json_path = Path(args.json)
        report.write_json(json_path, payload)
    elif args.json == "-":
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        sys.stderr.write(report.render_summary(payload) + "\n")
        return model.exit_code(layers)

    print(report.render_summary(payload, json_path=json_path))
    if keep_artifacts:
        print(f"临时产物：{run_root}")
    return model.exit_code(layers)


if __name__ == "__main__":
    raise SystemExit(main())
