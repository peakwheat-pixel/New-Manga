---
id: M2-DETECT-WEBTOON-DIAG
title: "webtoon 长条漫 ogkalu 0 候选适配器级诊断（建议 A 第一步：先可观测值再定修法）"
kind: diagnosis
status: ready
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
