#!/usr/bin/env python3
"""TASK-059: 从 doc/design/ui-reference.html 导出机器可读令牌副本。

HTML 是唯一视觉真值；本脚本生成 doc/design/tokens-cand-{a..f}.json（六候选）。
两者不一致时以 HTML 为准，重新运行本脚本即可再生成。
用法：python verification/TASK-059/export-tokens.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "doc" / "design" / "ui-reference.html"
OUT = ROOT / "doc" / "design"

CAND_NAMES = {
    "a": "Graphite 石墨（暗色优先工作室）",
    "b": "Atelier 画廊（亮色优先画廊）",
    "c": "Duo 双面+玻璃（画廊×车间 + 局部玻璃）",
    "d": "Vermilion 朱砂（顶栏导航+编辑部印刷网格）",
    "e": "Amber 琥珀（等宽表格+命令面板控制台）",
    "f": "Graphite Atelier（ND-1 组合稿：A 色彩 + B 几何，IA 继承 A）",
}

def parse_block(css: str, selector: str) -> dict:
    """提取精确选择器块内的 --var 值对。"""
    pat = re.compile(re.escape(selector) + r"\s*\{([^}]*)\}")
    m = pat.search(css)
    if not m:
        raise SystemExit(f"selector not found: {selector}")
    pairs = re.findall(r"--([\w-]+)\s*:\s*([^;]+);?", m.group(1))
    return {k: v.strip() for k, v in pairs}

def split_tokens(raw: dict) -> tuple[dict, dict]:
    """拆出色彩令牌与玻璃材质令牌。"""
    color = {k: v for k, v in raw.items() if not k.startswith("glass-")}
    glass = {
        "bg": raw.get("glass-bg", ""),
        "border": raw.get("glass-bd", ""),
        "highlight": raw.get("glass-hi", ""),
    }
    return color, glass

def main() -> int:
    css = HTML.read_text(encoding="utf-8")
    # 密度块选择器与主题块共享前缀，用“不接 [data-mode”的锚定区分
    geom = {}
    for c in "abcdef":
        pat = re.compile(
            r'\[data-cand="' + c + r'"\]\s*\{([^}]*)\}')
        ms = [m for m in pat.finditer(css)
              if "--fs-base" in m.group(1)]
        if not ms:
            raise SystemExit(f"geometry block not found for {c}")
        geom[c] = {k: v.strip() for k, v in
                   re.findall(r"--([\w-]+)\s*:\s*([^;]+);?", ms[0].group(1))}
        # card-w 定义在独立的单属性小方块（不含 --fs-base），单独提取后并入
        # geometry，使 JSON 几何相等断言覆盖 card-w（Review R4-001）
        cs = [m for m in pat.finditer(css)
              if "--card-w" in m.group(1) and "--fs-base" not in m.group(1)]
        if not cs:
            raise SystemExit(f"card-w block not found for {c}")
        geom[c]["card-w"] = re.findall(
            r"--card-w\s*:\s*([^;]+);?", cs[0].group(1))[0].strip()

    for c in "abcdef":
        modes = {}
        for mode in ("dark", "light"):
            raw = parse_block(
                css, f'[data-cand="{c}"][data-mode="{mode}"]')
            color, glass = split_tokens(raw)
            modes[mode] = {"color": color, "glass_material": glass}
        doc = {
            "task": "TASK-059",
            "candidate": c,
            "name": CAND_NAMES[c],
            "source_of_truth": "doc/design/ui-reference.html",
            "note": (
                "本文件为 HTML 视觉参考的机器可读副本，由 "
                "verification/TASK-059/export-tokens.py 生成；"
                "与 HTML 不一致时以 HTML 为准。所有值当前为 HTML/Chromium "
                "呈现，非 Qt 实现值。"
            ),
            "glass": {
                "enabled": c == "c",
                "blur_radius_px": 26 if c == "c" else None,
                "saturation": 1.6 if c == "c" else None,
                "note": (
                    "仅候选 C 启用玻璃材质；blur 22px/saturate 1.5 用于行内"
                    "浮条，26px/1.6 用于工具窗。玻璃承载容器与控件，裸文本"
                    "必须落在 scrim（color-mix 55% panel）上。"
                ) if c == "c" else "非 C 候选不启用玻璃材质。",
            },
            "geometry": geom[c],
            "modes": modes,
        }
        out = OUT / f"tokens-cand-{c}.json"
        out.write_text(
            json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        n = sum(len(m["color"]) for m in modes.values())
        print(f"wrote {out.relative_to(ROOT)} ({n} color tokens x2 modes)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
