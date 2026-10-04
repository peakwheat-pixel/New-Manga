"""AC1/AC3：生成管线——prompt 循环、每张落盘即证据、fail-closed 状态机。"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from chatgpt_bg import gap as gap_mod
from chatgpt_bg.browser import BGGenerationError, ChatGPTDriver, wait_new_image
from chatgpt_bg.prompts import build_prompt, style_cycle

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_CONSECUTIVE_FAILURES = 3
MAX_RELOAD_RETRY = 1  # 思考卡死 reload 重发次数/张（实测坑④）


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _next_bg_path(bg_dir: Path) -> Path:
    max_i = 0
    for p in bg_dir.glob("bg_*.png"):
        m = re.match(r"bg_(\d+)\.png", p.name)
        if m:
            max_i = max(max_i, int(m.group(1)))
    return bg_dir / f"bg_{max_i + 1:03d}.png"


def generate_backgrounds(
    driver: ChatGPTDriver,
    bg_dir: Path,
    count: int,
    poll_s: int = 5,
    timeout_s: int = 150,
) -> list[Path]:
    """生成 count 张底图入库；返回落盘文件列表。

    fail-closed 状态机（AC3）：
      - 前置登录检查失败 → BGGenerationError(NOT_LOGGED_IN)；
      - 阻塞态（Cloudflare/限额）→ BGGenerationError(BLOCKED)；
      - 单张超时 → reload 重发 MAX_RELOAD_RETRY 次；
      - 连续 MAX_CONSECUTIVE_FAILURES 张失败 → BGGenerationError(CONSECUTIVE_FAILURES)。
    每张成功即落盘+写 manifest（中断只可能"少张数"，绝不产出坏文件——KO-FULLRUN 教训）。
    """
    bg_dir = Path(bg_dir)
    if not driver.is_logged_in():
        raise BGGenerationError(
            "NOT_LOGGED_IN",
            "ChatGPT 未登录。先跑一次人工登录：python -m chatgpt_bg login "
            "（浏览器窗口内完成登录后回车确认，登录态持久化在 profile）",
        )

    written: list[Path] = []
    consecutive_failures = 0
    cycle = style_cycle(start=gap_mod.count_backgrounds(bg_dir))
    produced = 0
    while produced < count:
        if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
            raise BGGenerationError(
                "CONSECUTIVE_FAILURES",
                f"连续 {consecutive_failures} 张失败，停止批量（已落盘 {len(written)} 张）。"
                "人工检查页面状态后可重跑（断点续跑：按 bg_ 编号续编号）",
            )
        _idx, style = next(cycle)
        prompt = build_prompt(style)
        prev_src = driver.latest_image_src()
        try:
            driver.send_prompt(prompt)
        except BGGenerationError:
            raise
        except Exception as e:
            consecutive_failures += 1
            print(f"[bg:{style}] send 失败: {type(e).__name__}: {e}")
            continue

        new_src = None
        for attempt in range(MAX_RELOAD_RETRY + 1):
            try:
                new_src = wait_new_image(driver, prev_src, timeout_s=timeout_s, poll_s=poll_s)
                break
            except TimeoutError:
                if attempt < MAX_RELOAD_RETRY:
                    print(f"[bg:{style}] 等待超时，reload 重发（实测坑④：思考卡死不自愈）")
                    driver.reload()
                    # r2 N7：reload 后复检阻塞态（登录态可能随 reload 丢失）
                    state = driver.blocking_state()
                    if state is not None:
                        code, _, detail = state.partition("：")
                        raise BGGenerationError(code or "BLOCKED", detail or state)
                    # r2 P1-1：reload 重挂载后历史图会拿到全新 blob URL——旧基准作废，
                    # 必须重取，否则"旧图新 URL"会被判为新图静默落盘
                    prev_src = driver.latest_image_src()
                    driver.send_prompt(prompt)
        if new_src is None:
            consecutive_failures += 1
            print(f"[bg:{style}] 重试耗尽仍超时")
            continue

        try:
            png_bytes = driver.fetch_image_bytes(new_src)
        except Exception as e:
            consecutive_failures += 1
            print(f"[bg:{style}] 提取失败: {type(e).__name__}: {e}")
            continue
        if not png_bytes.startswith(PNG_MAGIC):
            consecutive_failures += 1
            print(f"[bg:{style}] 非 PNG 魔数，丢弃")
            continue
        bg_dir.mkdir(parents=True, exist_ok=True)
        out = _next_bg_path(bg_dir)
        # r2 P2-4：PNG 同样原子落盘（tmp+replace），半写不进底图库计数
        out.with_suffix(".png.tmp").write_bytes(png_bytes)
        out.with_suffix(".png.tmp").replace(out)
        try:
            gap_mod.append_manifest(bg_dir, {
            "file": out.name,
            "style": style,
            "prompt": prompt,
            "source": "chatgpt-web-auto",
            "chatgpt_blob_src": new_src,
            "created_at": _now_iso(),
        })
        except Exception as e:
            # manifest 失败：回滚刚落的 PNG（避免"图在册不在"的半写）
            out.unlink(missing_ok=True)
            consecutive_failures += 1
            print(f"[bg:{style}] manifest 写入失败已回滚: {type(e).__name__}: {e}")
            continue
        written.append(out)
        produced += 1
        consecutive_failures = 0
        print(f"[bg:{style}] -> {out.name} ({len(png_bytes) // 1024}KB)")
    return written
