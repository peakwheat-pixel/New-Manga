---
id: M2-DETECT-WEBTOON-TILING
title: "webtoon 长条漫 ogkalu tiling 检测修复（建议 A 第二步：按 DIAG 冻结口径实施，解锁 ko 6 case）"
kind: feature
status: ready
approval: user_ruling_2026-10-01_three_followups_all
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-DETECT-WEBTOON-DIAG, M2-TA3-B2]
base_commit: f534c3e7
branch: agent/zcode/M2-DETECT-WEBTOON-TILING
worktree: G:/CODEX/New Manga.worktrees/M2-DETECT-WEBTOON-TILING-zcode
---

# M2-DETECT-WEBTOON-TILING：长条漫 tiling 检测修复

## 背景（M2-DETECT-WEBTOON-DIAG 定案）

根因已定案：`detection_manga.py` `_detect_text_boxes` 把整页直传 `RTDetrImageProcessor`（size 640×640、无 letterbox），webtoon 长条漫（690×62133）垂直压缩 ~97× 致目标消失（raw max conf 0.204）。决定性证据：同页同权重同阈值 1024² 块级推理 → 193 个合并前文本框（NMS 数据已落盘：30/33 删框在重叠带、IoU mean 0.848）。修复=tiling+坐标回映（方案 A，契约零变更：DetectionRequest/Response 与 MERGE_* 输入不变）。

## 交付（AC）

1. **AC1 tiling 路径**：`detection_manga.py` 内部实现——触发条件按页面高宽比（如 h/w 超阈值启用 tiling，普通页走原路径**零行为变化**）；块尺寸/重叠/NMS IoU 参数**配置化**（env 先例 `NEWMANGA_SFX_CONF_THRESHOLD` 或 settings，Owner 勘察后选型留痕）；块级推理坐标回映+跨块 NMS 去重（DIAG 已验证参数：1024²、重叠 128px、NMS IoU 0.5 可作默认，配合 R5 建议）。
2. **AC2 测试**（先红后绿）：普通页路径零变化（既有检测测试不动全过）；长条漫触发判定单测；坐标回映正确性单测（合成框跨块）；跨块 NMS 去重单测；无权重环境 typed `PROVIDER_DEPENDENCY_MISSING` 保持。
3. **AC3 qualification（DIAG 冻结口径，逐条执行）**：`experiments/M2-DETECT-WEBTOON-TILING/qualify_tiling.py`——**5 张 webtoon_long_strip**（K01/K02/K04/K05/K08，路径见 case-selection.json）经生产 `provider.detect`：**Gate=每张 region 数>0**（生产 region 层级，非合并前文本框；预期同时报告合并后块数）；CPU 延迟预算 K01 ≤25s / K02 ≤10s / K04 ≤15s；**≥2 个阈值点候选数曲线**（0.5 与 0.4 或 0.25）；**690×690 原生尺度块对照组**（≈1.0× 重采样，块数~1.6×，验证分辨率假设）；K19（无字页）确认仍 0 候选（正确行为，本 Task 不修其 INVALID_INPUT 口径——F4 登记为相邻发现）。
4. **AC4 文档**：docstring（tiling 触发/参数/回映/NMS 语义）；Task frontmatter+AC 表回填；handoff（含 DSH review 指引）；发布形态影响评估（无新依赖→闭包/GATE 不涉及，登记确认）。

## 允许修改面

`src/infrastructure/providers/detection_manga.py`、`tests/`（detection 相关）、`experiments/M2-DETECT-WEBTOON-TILING/**`、`verification/M2-DETECT-WEBTOON-TILING/**`、Task/Handoff。

## 禁改面

`src/infrastructure/providers/detection_sfx.py`、`detection_doctr.py`、`src/ports/**`（DetectionRequest/Response 契约零变更）、`src/bootstrap/**`（如配置通道必须动装配则先在 handoff 登记移交集成方）、`doc/contracts/**`、`packaging/**`、`apps/**`、`experiments/M2-TA3-A|B|DETECT-WEBTOON-DIAG/**`（只读）、`doc/STATUS.md`。

## 纪律

- fail-closed 不放宽（tiling 内部失败 typed；普通页零变化）；conf 阈值 0.5 生产默认不变（qualification 的低阈值点仅为曲线数据）。
- 基线不回退：main 530+1skipped 0 failed。
- qualification 用真权重（pin 一致）、CPU 登记；M2-SFX-PROD-1 的 composite 包装不受影响（primary 检测语义增强）。
