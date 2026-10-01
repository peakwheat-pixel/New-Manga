---
id: M2-DETECT-WEBTOON-DIAG
title: "webtoon 长条漫 ogkalu 0 候选适配器级诊断（建议 A 第一步：先可观测值再定修法）"
kind: diagnosis
status: done  # DSH r1 changes_requested → 返修 R1-R11（含探针 schema v2 重跑，226/193 精确复现）→ r2 approved（可集成）

approval: user_ruling_2026-10-01_all_four
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-TA3-B2]
base_commit: 8e0de8d0
branch: agent/zcode/M2-DETECT-WEBTOON-DIAG
worktree: G:/CODEX/New Manga.worktrees/M2-DETECT-WEBTOON-DIAG-zcode
---

# M2-DETECT-WEBTOON-DIAG：ogkalu 对 webtoon 长条漫 0 候选的适配器级诊断

## 背景（M2-TA3-B2 F1）

TA3-B2 阶段二实证：生产 detect（manga ogkalu RT-DETR-v2）对 webtoon 长条漫返回 **0 候选**（K01/K02/K04/K05/K08/K19 六 case），是全链 Gate FAIL 最大单因。同页实证：docTR（TA3-A，fast_base pin）对 K01 有 15 候选、ogkalu 路径 0 候选（source_sha256 同页 `600ca755…`）。**0 候选的适配器级机制尚无证据**（假设：`RTDetrImageProcessor` 整页重缩放把 690×62133 长条漫压到模型输入尺寸致目标消失；`detection_manga.py:342-348` 无 size 覆盖地把整幅交给 processor）。用户裁决「全部进行」：先诊断补可观测值，再定修法（tiling/分域路由等）。

## 交付（AC）

1. **AC1 可观测值探针**：`experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py`——对 K01（及 K02/K04 抽样）用生产 provider 同构造路径记录：送入 processor 的图像尺寸、processor 重缩放目标尺寸（preprocessor_config.json 的 size/shortest_edge）、模型 raw 输出（logits 形状/最大置信度/top-k 分数分布，含 conf<0.5 的低分检出数）、letterbox/resize 参数；对照一组正常比例漫画页（BJ02）确认探针本身在常规页行为正常。
2. **AC2 结论判定**：0 候选根因判定（整页重缩放目标消失 / 其他），证据落 `verification/M2-DETECT-WEBTOON-DIAG/diagnosis.md`+JSON；若整页重缩放成立，用 K01 裁切成 1024×1024 块实测 ogkalu 检出能力（块级是否恢复候选——tiling 修法的直接可行性证据）。
3. **AC3 修法建议**：基于证据给出修复方案对比（tiling+坐标回映 / per-family 路由到 docTR / processor size 覆盖），含改动面/风险/成本估计——**只建议不实施**，修复另行释放。
4. **AC4 零 src 改动**：全部探针在 experiments（生产 provider 直接 import 构造），发现 src 缺陷只登记。

## 允许修改面 / 禁改面

允许：`experiments/M2-DETECT-WEBTOON-DIAG/**`、`verification/M2-DETECT-WEBTOON-DIAG/**`、`doc/tasks/M2-DETECT-WEBTOON-DIAG.md`、`doc/handoffs/M2-DETECT-WEBTOON-DIAG-*.md`。
禁改：`src/**`、`tests/**`、`requirements.txt`、`packaging/**`、`apps/**`、`doc/contracts/**`、`experiments/M2-TA3-A|B/**`（只读）、`doc/STATUS.md`。

## 纪律

- 权重目录与生产 pin 一致（ogkalu 三文件 sha256）；GPU/CPU 均可（设备登记）；块级实验不落地任何入库权重。
- 诊断结论 directional；修法对比只做静态成本估计+块级实测证据，不做生产代码 prototype。

## 交付记录（2026-10-01，ZCode，续接熔断半成品）

前置说明：接手时探针脚本与 `probe-results.json` 已由熔断前一轮产出（AC1 四页 + K01 块级实验数据已完整落在 JSON 内）；本轮续接完成结果分析、判定文档、修法对比、Handoff 与提交，未重跑探针（JSON 即原始数据，时间戳 2026-10-01T11:43:32Z）。

- **AC1** ✅ `experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py`：生产 provider 逐字节同构造；四页 sha256 对 TA3-B manifest 校验通过；记录 preprocessor config（size 640×640、do_pad=false→无 letterbox）、model_input_shape、raw logits 全分布（含 <0.5）、类内分布；BJ02 对照 10 检出（探针自检 VALID）。
- **AC2** ✅ 判定=**整页重缩放目标消失成立**（K01 690×62133→640×640 垂直 ~97×；三 webtoon 页 raw max 0.167–0.284 全塌陷，BJ02 对照 0.972 正常）；块级实验 K01 70 块（1024²/重叠 128px）0 个 ≥0.5 文本框→**193** 个跨块去重文本框（**合并前口径**，生产 region 为合并后块数；conf max 0.967/mean 0.850，y 覆盖全页）——同一权重同一阈值仅改单次推理的像素预算即恢复，tiling 可行性直接证据。DSH r1 返修（schema v2）复跑复现 226/193 并落盘 pre/post-NMS 全量框坐标与重叠带统计（33 删框中 30 带内/28 跨块 keeper）。证据：[diagnosis.md](../../verification/M2-DETECT-WEBTOON-DIAG/diagnosis.md) + [probe-results.json](../../verification/M2-DETECT-WEBTOON-DIAG/probe-results.json)。
- **AC3** ✅ 修法对比（只建议不实施）：A tiling+坐标回映（推荐主线，契约零变更）> B per-layout 路由 docTR（粒度语义成本未知，留作基线）> C processor size 覆盖（证据不支持，排除）。
- **AC4** ✅ 零 `src/**`/`tests/**` 改动；生产路径缺陷（整页直传 processor 无长条漫处理）已在本文件与 diagnosis.md 登记，修复另行释放。
- Handoff：`doc/handoffs/M2-DETECT-WEBTOON-DIAG-2d6b7bf6.md`（impl head=2d6b7bf6）；Reviewer：DeepSeek Harness（非作者）。

**下一任务建议（移交 Codex 释放裁决）**：修复 Task「webtoon 长条漫 tiling 检测（方案 A）」——Owner ZCode、Reviewer DSH；验收=**5 张 `webtoon_long_strip`（K01/K02/K04/K05/K08）**重跑 qualification：以生产 `provider.detect` region 数计量（region>0 且全链可用，附合并后块数对比），关闭 TA3-B2 F1 的长条漫部分；**K19（1200×1660 无字页，TA3-B F4）不在 tiling 验收面**——其 0 候选是正确行为，需修的是「无字页应空成功而生产 step=failed/INVALID_INPUT」的口径缺陷（r1 返修更正：v1 曾把 ko 六 case 一并写入验收）。释放前需 Codex 在 STATUS 登记范围（含 `src/infrastructure/providers/detection_manga.py` 与检测参数配置的授权修改面）。
