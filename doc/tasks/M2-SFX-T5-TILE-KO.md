---
id: M2-SFX-T5-TILE-KO
title: "SFX KO tile 化生产分支（T5-TILE）：tile_ov128 冻结口径落地+路由阈值+性能双档实测+KO 域验收"
kind: feature
status: owner_claim
owner_claim: ZCode 2026-10-06 @worktree M2-SFX-T5-TILE-KO-zcode（base=a3b0f537=main 收口 tip 含 T4 v2b pin 终态；授权=user ruling 2026-10-05「三件都同意」tile 化立项）
approval: user_ruling_2026-10-05_三件都同意（tile化立项）
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
depends_on: [M2-SFX-T4-SWITCH]
base_commit: a3b0f537（2026-10-06 T4 收口后解锁；worktree 实建 base）
branch: agent/zcode/M2-SFX-T5-TILE-KO
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-T5-TILE-KO-zcode
review_events: []
created: 2026-10-05
---

# Task: M2-SFX-T5-TILE-KO — SFX KO 长条页 tile 化生产分支

## 背景与授权

T3/T2/KO-TILE 三轮确证：KO 长条页（宽 600/690、aspect 1:31~1:146）在生产整页 letterbox 序列下 SFX 亚像素化，**三方含现役权重全零**——KO 域 SFX 从 0 到有的唯一路径=推理序列 tile 化。冻结口径=KO-TILE 提案 §3（tile_690x1024_overlap128：tile 高 1024/步长 896/末尾补页底锚点/tile 内生产序列本体/页级跨 tile IoU 0.5 conf 降序贪心 NMS），实现蓝本=`experiments/M2-SFX-GATE-T3/eval_gate_t3.py` tile 实现与 `experiments/M2-KO-TILE-CALIB/tile_calib.py`（已过 KO-TILE 参考矩阵逐位复现+36 格复算）。用户 2026-10-05 裁决「三件都同意」立项；**depends_on M2-SFX-T4-SWITCH（同文件 src 变更串行，避免冲突）**。

## 验收条件

- **AC1 tile 分支实现（src 授权面）**：`SfxDetectionProvider.detect` 增加 KO 长条页路由分支——按页宽/aspect 阈值判定（宽≤690 量级长条页走 tile，普通页走 letterbox 原路径**零变化**；阈值定值=实施裁量点，须 fail-fast 常量化+登记依据）；tile 口径逐字=冻结提案（K_TILE_H=1024/OVERLAP=128/NMS_IOU=0.5）；env 覆盖（`NEWMANGA_SFX_TILE_*`，沿 fail-fast 纪律）+关闭开关（默认开启路由，可 env 禁用回 letterbox）。
- **AC2 性能双档实测**：CPU（生产 EP）与 GPU（本机 RTX 5070 Ti）双档 tile 时延实测（4 页 KO 考题 58-112 tiles/页），产出部署形态呈报数据（用户终选部署形态=收口呈报项，不阻塞 Task）。
- **AC3 KO 域验收**：KO 4 页派生 GT 56 框（tile 冻结口径）+非派生 135 框双 GT 复测——生产 tile 分支数字须与 T3 评测矩阵同权重结果一致（v2b 35/56+48/135 逐位复现=实现等价性硬证据；chiqui7 56/56+41/135 同验）；BJ 页回归（letterbox 路径零变化实证：考卷 5 框 chiqui7 pin 重跑逐位一致）。
- **AC4 契约与测试**：RegionCandidate 契约零变化（输出面不变）；单测先红后绿（tile 路由判定/锚点/NMS 合并/fail-fast）；m2_acceptance 相关面回归。
- **AC5 文档**：T4 承接项闭合登记（r1 P3-2 tile 参数运行期 assert 在本 AC1 落地）+部署记录+Task/Handoff。

## 纪律与限制

- 允许路径：`src/infrastructure/providers/detection_sfx.py`（tile 分支）、`src/**` 相关路由/env 段（逐文件声明）、`tests/**`、`doc/tasks/M2-SFX-T5-TILE-KO.md`、`doc/handoffs/`、`verification/M2-SFX-T5-TILE-KO/**`、`experiments/M2-SFX-T5-TILE-KO/**`。
- 禁区：`contracts/**`（RegionCandidate 输出面零变化；若实施中发现须动契约即停等）、`apps/**`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`。
- 覆盖矩阵缺口如实登记（宽≠690/600 的 KO 页参数化未覆盖=KO-TILE §9 已知限制）；相位依赖登记（T4 落地复测偏离 56/56 上界先查相位）。
- 权重=切换后现役（T4-SWITCH 终态 pin），本 Task 不换权重。
