"""AC6：CLI——login / status / generate / check-gap / selfcheck。"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from chatgpt_bg import gap as gap_mod
from chatgpt_bg.browser import BGGenerationError, PlaywrightChatGPTDriver
from chatgpt_bg.pipeline import generate_backgrounds
from chatgpt_bg.prompts import BG_STYLES, build_prompt

PKG_PARENT = Path(__file__).resolve().parents[1]


def _resolve_repo_root() -> Path:
    """主仓根（worktree 安全）：env 覆盖 > git common dir 推断 > 路径回退。"""
    import os
    import subprocess

    env = os.environ.get("CHATGPT_BG_REPO_ROOT")
    if env:
        return Path(env)
    try:
        common = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            capture_output=True, text=True, timeout=10,
            cwd=PKG_PARENT,
        ).stdout.strip()
        if common:
            return Path(common).resolve().parent
    except Exception:
        pass
    return PKG_PARENT.parents[1]


REPO_ROOT = _resolve_repo_root()
# r2 P2-3：路径全部 env 可覆盖（worktree/主仓/换机共享底图库与登录态）
DEFAULT_DATA_ROOT = Path(os.environ.get("CHATGPT_BG_DATA_ROOT") or (REPO_ROOT / "training_data" / "sfx-v1"))
DEFAULT_BG_DIR = DEFAULT_DATA_ROOT / "backgrounds"
DEFAULT_PROFILE_DIR = os.environ.get("CHATGPT_BG_PROFILE") or str(
    REPO_ROOT.parent / "New Manga.task-envs" / "M2-SFX-SYNTH-BG-AUTO" / "chrome-profile")


def _open_driver(args) -> PlaywrightChatGPTDriver:
    return PlaywrightChatGPTDriver(
        user_data_dir=getattr(args, "profile", None) or DEFAULT_PROFILE_DIR,
        headless=getattr(args, "headless", False),
    )


def cmd_login(args: argparse.Namespace) -> int:
    """人工登录一次：打开浏览器窗口，登录完成后回车确认，登录态持久化。"""
    driver = _open_driver(args)
    driver.open_chat()
    if driver.is_logged_in():
        print("[login] 已是登录态，无需操作")
        driver.close()
        return 0
    print("[login] 请在打开的浏览器窗口内完成 ChatGPT 登录。")
    input("[login] 登录完成后回车确认...")
    ok = driver.is_logged_in()
    driver.close()
    print(f"[login] 登录态: {'OK（已持久化 profile）' if ok else '仍未登录——重跑 login 重试'}")
    return 0 if ok else 1


def cmd_status(args: argparse.Namespace) -> int:
    bg_dir = Path(args.bg_dir)
    report = gap_mod.check_gap(bg_dir, int(args.min_backgrounds))
    print(json.dumps({
        "backgrounds_current": report.current,
        "min_backgrounds": report.required,
        "missing": report.missing,
        "has_gap": report.has_gap,
        "bg_dir": str(bg_dir),
        "profile": getattr(args, "profile", None) or DEFAULT_PROFILE_DIR,
    }, ensure_ascii=False))
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    bg_dir = Path(args.bg_dir)
    report = gap_mod.check_gap(bg_dir, int(args.min_backgrounds))
    if report.has_gap:
        print(f"[generate] 缺口：现有 {report.current} < 要求 {report.required}，补 {report.missing} 张")
    count = int(args.count) if args.count else report.missing
    if count <= 0:
        print("[generate] 无缺口且未指定 --count，无事可做")
        return 0
    driver = _open_driver(args)
    try:
        driver.open_chat()
        written = generate_backgrounds(
            driver, bg_dir, count=count,
            poll_s=int(args.poll_s), timeout_s=int(args.timeout_s),
        )
    except BGGenerationError as e:
        print(f"[generate] FAIL-CLOSED [{e.state}] {e.detail}", file=sys.stderr)
        return 4
    except Exception as e:
        # r2 P1-2：环境异常（playwright 缺失/Chrome 不存在/启动失败）同样 fail-closed
        print(f"[generate] FAIL-CLOSED [ENV_ERROR] {type(e).__name__}: {e}", file=sys.stderr)
        print("[generate] 人工处置：检查 playwright 安装与本机 Chrome；重跑 login", file=sys.stderr)
        return 4
    finally:
        driver.close()  # r2 N3：唯一 close 点（幂等），except 分支不再重复
    print(f"[generate] 完成：{len(written)} 张落盘 {bg_dir}")
    return 0


def _auto_generate(args, missing: int) -> None:
    driver = _open_driver(args)
    try:
        driver.open_chat()
        generate_backgrounds(driver, Path(args.bg_dir), count=missing,
                             poll_s=int(args.poll_s) if hasattr(args, "poll_s") else 5,
                             timeout_s=int(args.timeout_s) if hasattr(args, "timeout_s") else 150)
    finally:
        driver.close()


def cmd_check_gap(args: argparse.Namespace) -> int:
    """入口钩子：供数据构建脚本调用。返回码 0=充足，2=已触发生成，3=dry-run 缺口。"""
    bg_dir = Path(args.bg_dir)
    try:
        report, triggered = gap_mod.trigger_if_gap(
            bg_dir, int(args.min_backgrounds),
            generate_fn=lambda n: _auto_generate(args, n),
            dry_run=bool(args.dry_run),
        )
    except BGGenerationError as e:
        # r2 P1-2/P2-8：自动入口失败同样结构化输出（EXIT 4=fail-closed）
        print(json.dumps({"fail_closed": {"state": e.state, "detail": e.detail}},
                         ensure_ascii=False))
        return 4
    except Exception as e:
        # r2 N2：ENV_ERROR（playwright 缺失/Chrome 不存在）同结构化，不再裸 traceback
        print(json.dumps({"fail_closed": {"state": "ENV_ERROR",
                                          "detail": f"{type(e).__name__}: {e}"}},
                         ensure_ascii=False))
        return 4
    print(json.dumps({
        "gap": {"current": report.current, "required": report.required,
                "missing": report.missing, "has_gap": report.has_gap},
        "triggered": triggered, "dry_run": bool(args.dry_run),
    }, ensure_ascii=False))
    if report.has_gap and args.dry_run:
        return 3
    return 2 if triggered else 0


def cmd_selfcheck(_args: argparse.Namespace) -> int:
    checks = []
    checks.append(("prompt_styles_count", len(BG_STYLES) >= 20, f"{len(BG_STYLES)} styles"))
    bad = [s for s in BG_STYLES if "no text" not in build_prompt(s)]
    checks.append(("prompt_constraints", not bad, f"公共约束缺失风格={bad}"))
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        checks.append(("gap_empty", gap_mod.check_gap(d, 5).missing == 5, "空目录缺口=5"))
        from chatgpt_bg.gap import PNG_MAGIC_HEX

        real_png = bytes.fromhex(PNG_MAGIC_HEX) + b"x"
        (d / "bg_001.png").write_bytes(real_png)
        checks.append(("gap_partial", gap_mod.check_gap(d, 5).missing == 4, "1 张缺口=4"))
        rep, fired = gap_mod.trigger_if_gap(d, 1, generate_fn=lambda n: None)
        checks.append(("gap_satisfied", not rep.has_gap and not fired, "足量不触发"))
        rep2, fired2 = gap_mod.trigger_if_gap(d, 5, generate_fn=lambda n: None, dry_run=True)
        checks.append(("gap_dryrun", rep2.has_gap and not fired2, "dry-run 报缺口不触发"))
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        gap_mod.append_manifest(d, {"file": "bg_001.png"})
        gap_mod.append_manifest(d, {"file": "bg_002.png"})
        entries = json.loads((d / "bg_index.json").read_text(encoding="utf-8"))
        checks.append(("manifest_append", [e["file"] for e in entries] == ["bg_001.png", "bg_002.png"],
                       "两次追加有序"))
    all_ok = all(ok for _, ok, _ in checks)
    print(f"selfcheck: {'PASS' if all_ok else 'FAIL'}")
    for name, ok, detail in checks:
        print(f"  [{'OK' if ok else 'NG'}] {name}: {detail}")
    return 0 if all_ok else 1


def build_parser() -> argparse.ArgumentParser:
    # r2 N6/r3 收口：全局参数唯一口径=后置于子命令（argparse 同名参数主/子双份时
    # 子侧 default 会静默覆盖主解析值，故 common 只挂子 parser）
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--bg-dir", default=str(DEFAULT_BG_DIR), help="底图库目录（gitignored 外部树）")
    common.add_argument("--profile", default=None, help="Chrome persistent profile 目录（默认外部树）")
    common.add_argument("--headless", action="store_true", help="无头模式（默认有头：降低风控面+可人工介入）")
    common.add_argument("--min-backgrounds", type=int, default=20, help="底图库余量阈值（缺口触发用）")
    # r3 注意：common 只挂子 parser——同名参数主/子双份时子 default 会覆盖主解析值
    # （argparse 已知行为，--min-backgrounds 0 会被子侧 default 20 静默覆盖）。
    # 代价：全局参数必须写在子命令之后（README 用法示例已按此口径）。
    ap = argparse.ArgumentParser(
        prog="chatgpt_bg",
        description="SFX 合成底图自动 provider（M2-SFX-SYNTH-BG-AUTO）：ChatGPT 网页全自动生成+缺口触发",
    )
    sub = ap.add_subparsers(dest="command")

    sub.add_parser("selfcheck", help="离线自检 EXIT=0", parents=[common]).set_defaults(func=cmd_selfcheck)
    sub.add_parser("login", help="人工登录一次（登录态持久化 profile）", parents=[common]).set_defaults(func=cmd_login)
    sub.add_parser("status", help="底图库余量与缺口报告", parents=[common]).set_defaults(func=cmd_status)

    p_gen = sub.add_parser("generate", aliases=["backgrounds"], help="批量生成（默认补齐缺口；AC1 名 backgrounds 为别名）", parents=[common])
    p_gen.add_argument("--count", type=int, default=0, help="指定张数（默认=缺口数）")
    p_gen.add_argument("--poll-s", type=int, default=5)
    p_gen.add_argument("--timeout-s", type=int, default=150)
    p_gen.set_defaults(func=cmd_generate)

    p_gap = sub.add_parser("check-gap", help="缺口检查钩子（0=充足 2=已触发 3=dry-run 缺口 4=fail-closed）", parents=[common])
    p_gap.add_argument("--dry-run", action="store_true")
    p_gap.set_defaults(func=cmd_check_gap)
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if not getattr(args, "func", None):
        build_parser().print_help()
        return 0
    return int(args.func(args) or 0)


if __name__ == "__main__":
    sys.exit(main())
