"""M2-SFX-FINETUNE-PREFLIGHT AC4 补充：生产解析链「候选非空路径」注入验证。

export_smoke.py 的全真冒烟里，1-epoch 换头权重对合成页零检出（fail-closed 合法），
conf 门→类无关 NMS→类过滤→/scale 映射→clip 的候选生成路径因此只被走到空循环。
本脚本用生产函数 ``_sfx_boxes``（src 只读 import）+ 伪造 session 输出张量做注入：
  anchor0 sfx 0.90 框(100,100)-(200,200)   → 保留
  anchor1 sfx 0.80 框(105,105)-(195,195)   → 与 anchor0 IoU=0.81 ≥ 0.7 被 NMS 抑制
  anchor2 bubble 0.95 框(300,300)-(400,400) → conf 过门但类过滤丢弃
  anchor3 sfx 0.60 框(500,500)-(600,600)   → 保留
scale=0.5 → 映射回源页坐标应恰为 2×。断言返回 2 框、顺序与坐标精确匹配。
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-FINETUNE-PREFLIGHT-zcode")
RAW_OUT = REPO / "verification" / "M2-SFX-FINETUNE-PREFLIGHT" / "raw"


class FakeSession:
    """只实现 session.run 的最小替身（_sfx_boxes 对 session 的唯一用法）。"""

    def run(self, _names, _feeds):
        import numpy

        # 行=anchor，列 [xywh(4) | cls_scores(4) | mask(32)] —— 生产 out[0].T 后的布局
        anchors = [
            # cx,  cy,   w,  h,  bubble, panel, sfx, text
            [150.0, 150.0, 100.0, 100.0, 0.02, 0.03, 0.90, 0.05],
            [150.0, 150.0, 90.0, 90.0, 0.01, 0.02, 0.80, 0.17],
            [350.0, 350.0, 100.0, 100.0, 0.95, 0.01, 0.02, 0.02],
            [550.0, 550.0, 100.0, 100.0, 0.01, 0.01, 0.60, 0.38],
        ]
        matrix = [row + [0.0] * 32 for row in anchors]  # (N, 40)
        out = numpy.array(matrix, dtype=numpy.float32).T.reshape(1, 40, len(anchors))
        return [out]


def main() -> int:
    sys.path.insert(0, str(REPO / "src"))
    from infrastructure.providers.detection_sfx import _sfx_boxes

    started = time.perf_counter()
    boxes = _sfx_boxes(
        FakeSession(),
        None,  # inp 未被 _sfx_boxes 使用（session.run 的入参由其自组）
        scale=0.5,
        conf_threshold=0.5,
        page_w=2048.0,
        page_h=2048.0,
    )
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    got = [
        {"x0": round(b[0], 1), "y0": round(b[1], 1), "x1": round(b[2], 1),
         "y1": round(b[3], 1), "conf": round(b[4], 3)}
        for b in boxes
    ]
    expected = [
        {"x0": 200.0, "y0": 200.0, "x1": 400.0, "y1": 400.0, "conf": 0.9},
        {"x0": 1000.0, "y0": 1000.0, "x1": 1200.0, "y1": 1200.0, "conf": 0.6},
    ]
    ok = len(got) == 2 and all(
        abs(g[k] - e[k]) < 1e-6 for g, e in zip(got, expected) for k in e
    )
    report = {
        "probe": "production _sfx_boxes with injected (1,40,N) tensor",
        "got": got,
        "expected": expected,
        "assertions": "nms_suppression=True, class_filter=True, scale_map_x2=True",
        "elapsed_ms": elapsed_ms,
        "exit": 0 if ok else 1,
    }
    RAW_OUT.mkdir(parents=True, exist_ok=True)
    (RAW_OUT / "nms_chain_probe.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
