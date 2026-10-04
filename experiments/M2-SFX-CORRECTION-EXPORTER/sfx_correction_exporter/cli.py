"""AC5：CLI——selfcheck / export（SQLite 只读铁律；--help EXIT=0）。"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from sfx_correction_exporter import TASK_ID, __version__
from sfx_correction_exporter.db import open_readonly
from sfx_correction_exporter.eligibility import CONSTANTS

SEED_DEFAULT = 20261004  # = T1a splits.SEED_DEFAULT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sfx-correction-exporter",
        description=(
            "T5c 纠错样本导出器：只读扫描 SQLite revision 链的类型纠错事件，"
            "经资格判定后导出 T1a manifest + YOLO seg 双形态（零 src、零生产写路径）。"
        ),
    )
    parser.add_argument("--version", action="version", version=f"{TASK_ID} exporter {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("selfcheck", help="运行内置不变量自检（只读/识别语义/schema 互操作），EXIT=0 即通过")

    pe = sub.add_parser("export", help="执行导出（源库只读；输出写外部树 training_data/sfx-corrections/）")
    pe.add_argument("--db", required=True, help="SQLite 库路径（以 mode=ro 只读打开，不存在即失败）")
    pe.add_argument("--out", default="training_data/sfx-corrections", help="导出输出目录（默认 training_data/sfx-corrections）")
    pe.add_argument("--registry", default=None, help="T1a 已册 manifest 路径（去重+组继承；缺省=空册）")
    pe.add_argument("--cases", default=None, help="cases.json 路径（许可继承+组键映射；缺省=仓库 test_assets）")
    pe.add_argument("--managed-root", default=None, help="相对 managed_original_ref 的解析根")
    pe.add_argument("--seed", type=int, default=SEED_DEFAULT, help="拆分 seed（默认同 T1a 20261004）")
    pe.add_argument(
        "--yolo-scope", choices=("main", "all"), default="main",
        help="YOLO seg 范围（DSH r1 P2-1）：main=仅正集 complete（默认）；"
             "all=正集+辅助集混入（partial 显式 opt-in 才入训练直读树）",
    )
    pe.add_argument("--summary-out", default=None, help="摘要 JSON 输出路径（缺省 <out>/export-summary.json）")
    return parser


def cmd_selfcheck(_args: argparse.Namespace) -> int:
    """六项不变量自检；任一失败打印原因并返非零。"""
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, fn) -> None:
        try:
            detail = fn()
            checks.append((name, True, detail or "ok"))
        except Exception as e:  # noqa: BLE001 — selfcheck 必须把一切失败转 EXIT!=0
            checks.append((name, False, f"{type(e).__name__}: {e}"))

    def _readonly_enforcement() -> str:
        from sfx_correction_exporter import fixture
        import sqlite3

        with tempfile.TemporaryDirectory() as td:
            fx = fixture.build_fixture_db(Path(td))
            conn = open_readonly(fx["db_path"])
            try:
                assert conn.execute("PRAGMA query_only").fetchone()[0] == 1, "query_only 未生效"
                try:
                    conn.execute("UPDATE regions SET region_type='sfx'")
                except sqlite3.Error:
                    return "mode=ro + query_only=ON，写尝试被拒"
                raise AssertionError("只读连接上 UPDATE 竟然成功")
            finally:
                conn.close()

    def _scanner_semantics() -> str:
        from sfx_correction_exporter import fixture
        from sfx_correction_exporter.scanner import scan_corrections

        with tempfile.TemporaryDirectory() as td:
            fx = fixture.build_fixture_db(Path(td))
            conn = open_readonly(fx["db_path"])
            try:
                scan = scan_corrections(conn)
            finally:
                conn.close()
            by = {e.region_id: e for e in scan.events}
            a = by["rgA"]
            assert a.survives and (a.type_before, a.type_after) == ("speech", "sfx")
            assert by["rgB"].undone and not by["rgB"].survives
            assert all(e.region_id != "rgE" for e in scan.events) and scan.machine_type_changes_excluded == 1
            assert scan.regions_skipped_deleted == 1
            non_sfx = [e for e in scan.events if e.survives and not e.sfx_directed]
            assert {e.region_id for e in non_sfx} == {"rgF", "rgK"}
            return f"15-region fixture 矩阵不变量成立（surviving={sum(1 for e in scan.events if e.survives)}）"

    def _schema_interop() -> str:
        from sfx_data_infra.schema import SampleRecord

        rec = SampleRecord.from_dict(
            {
                "sample_id": "sc-1",
                "image": {"path": "a.png", "sha256": "a" * 64, "width": 10, "height": 10},
                "boxes": [{"polygon": [[0, 0], [1, 0], [1, 1], [0, 1]], "cls": "sfx"}],
                "annotation_status": "partial",
                "provenance": {"type": "asset_case"},
                "group": "g",
                "created_at": "2026-10-04T00:00:00Z",
            }
        )
        assert SampleRecord.from_dict(rec.to_dict()).validate() == []
        return "SampleRecord to_dict/from_dict/validate 往返一致"

    def _class_map() -> str:
        from sfx_correction_exporter.export import _sfx_class_map

        m = _sfx_class_map()
        assert [m[i] for i in sorted(m)] == ["bubble", "panel", "sfx", "text"], m
        sfx_id = next(k for k, v in m.items() if v == "sfx")
        return f"SFX_CLASS_MAP={m}（sfx id={sfx_id}，names 顺序逐字锚定）"

    def _dedup() -> str:
        from sfx_data_infra.schema import BoxAnnotation, ImageRef, SampleRecord
        from sfx_data_infra.dedup import find_duplicates

        def mk(sid: str) -> SampleRecord:
            return SampleRecord(
                sample_id=sid,
                image=ImageRef(path="x.png", sha256="b" * 64, width=8, height=8),
                boxes=[BoxAnnotation(polygon=[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]], cls="sfx")],
                annotation_status="partial",
                provenance={"type": "asset_case"},
                group="g",
                created_at="2026-10-04T00:00:00Z",
            )

        report = find_duplicates([mk("p"), mk("q")], image_loader=None)
        assert report.duplicate_of.get("q") == "p"
        return "find_duplicates 精确层级（同图同框）sanity 成立"

    def _manifest_roundtrip() -> str:
        from sfx_data_infra.atomicio import load_manifest, write_manifest
        from sfx_data_infra.schema import BoxAnnotation, ImageRef, SampleRecord

        rec = SampleRecord(
            sample_id="mr-1",
            image=ImageRef(path="x.png", sha256="c" * 64, width=8, height=8),
            boxes=[BoxAnnotation(polygon=[[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]], cls="sfx")],
            annotation_status="partial",
            provenance={"type": "asset_case"},
            group="g",
            created_at="2026-10-04T00:00:00Z",
        )
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "m.json"
            write_manifest(p, [rec])
            _, records = load_manifest(p)
            assert [r.sample_id for r in records] == ["mr-1"]
        return "write_manifest/load_manifest 往返一致（原子写）"

    check("readonly_enforcement", _readonly_enforcement)
    check("scanner_semantics", _scanner_semantics)
    check("schema_interop", _schema_interop)
    check("class_map_anchor", _class_map)
    check("dedup_sanity", _dedup)
    check("manifest_roundtrip", _manifest_roundtrip)

    failed = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    print(f"  rules: {json.dumps(CONSTANTS, ensure_ascii=False, sort_keys=True)}")
    if failed:
        print("SELFCHECK FAIL")
        return 1
    print(f"SELFCHECK PASS ({len(checks)} checks)")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    from sfx_correction_exporter import fixture
    from sfx_correction_exporter.export import run_export

    cases_path = args.cases
    if cases_path is None:
        default_cases = fixture.repo_cases_json()
        cases_path = str(default_cases) if default_cases else None
    try:
        summary = run_export(
            db_path=args.db,
            out_dir=args.out,
            registry_path=args.registry,
            cases_path=cases_path,
            managed_root=args.managed_root,
            seed=args.seed,
            yolo_scope=args.yolo_scope,
            summary_out=args.summary_out,
        )
    except Exception as e:  # noqa: BLE001 — CLI 层 fail-closed
        print(f"EXPORT FAIL: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    if summary["corrections_empty"]:
        print("CORRECTIONS_EMPTY=expected（库内无存活的 sfx 向类型纠错事实）")
    print(
        f"EXPORT OK: events={summary['scan']['events_total']}"
        f" surviving={summary['scan']['events_surviving']}"
        f" main={summary['export']['main_samples']}"
        f" auxiliary={summary['export']['auxiliary_samples']}"
        f" out={summary['export']['out_dir']}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "selfcheck":
        return cmd_selfcheck(args)
    if args.command == "export":
        return cmd_export(args)
    return 2
