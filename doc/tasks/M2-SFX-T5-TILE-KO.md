---
id: M2-SFX-T5-TILE-KO
title: "SFX KO tile 化生产分支（T5-TILE）：tile_ov128 冻结口径落地+路由阈值+性能双档实测+KO 域验收"
kind: feature
status: in_review
owner_claim: ZCode 2026-10-06 @worktree M2-SFX-T5-TILE-KO-zcode（base=a3b0f537=main 收口 tip 含 T4 v2b pin 终态；授权=user ruling 2026-10-05「三件都同意」tile 化立项）
delivery: ZCode 2026-10-06（AC1-AC5 全 PASS：AC3 逐位复现 v2b 35/56+48/135、chiqui7 56/56+41/135，BJ letterbox 零变化逐位；r1 P3-2 闭合；delivery head=24ae2765，docs commit 随后）
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

## 交付记录（Owner=ZCode，2026-10-06）

**结果：AC1-AC5 全 PASS。生产 `SfxDetectionProvider.detect` 新增 KO 长条页 tile 路由分支（宽≤690 且 aspect≥8.0 → tile_ov128 冻结口径），AC3 逐位复现 T3 评测矩阵（v2b 35/56+48/135、chiqui7 56/56+41/135，逐页 bit_parity=True），BJ 考卷 letterbox 路径 preds 逐位一致=零变化实证，T4 承接项 r1 P3-2（tile 冻结参数运行期断言）闭合。status owner_claim→in_review 停写，待 DSH 非作者 r1 Review。**

| AC | 判定 | 核心证据 |
|---|---|---|
| AC1 tile 分支 | **PASS** | `detection_sfx.py` tile 路由+冻结口径常量（1024/128/0.5，KO-TILE §3 逐字）+路由阈值 fail-fast 常量化（690/8.0，登记 KO 域观测依据 T3 raw page_size：宽 600/690、aspect 30.7-145.6 vs 普通页 ~1.4）+`NEWMANGA_SFX_TILE` on/off 开关+5 覆盖 env 非法值命名变量 fail-fast 先于权重解析。commit `98338691` |
| AC2 性能双档 | **PASS** | CPU 生产 EP v2b：4 页 3.36-17.96s，均值 10.46s/页（合计 41.82s）；GPU DML（onnxruntime-directml 1.24.4，RTX 5070 Ti）：v2b 均值 1.08s/页、chiqui7 均值 1.27s/页；warm-up+计测协议。部署形态终选=用户呈报项。commit `24ae2765`，表见 [tile-deploy-report §1](../../verification/M2-SFX-T5-TILE-KO/tile-deploy-report.md) |
| AC3 KO 域验收 | **PASS** | 生产 tile 分支（CPU 生产 EP，conf 0.5）：v2b（生产 pin 原样零重指）ko-tile **35/56**+ko-npd **48/135**、chiqui7（sha d87389af 先验断言→进程内重指→finally 恢复）**56/56**+**41/135**——逐页 `bit_parity_vs_t3_raw=True`（T3 raw 写盘精度 xyxy 0.1/conf 4 位+match_gt 全精度 matched 复算双证）；BJ pre-bj17/pre-bj18 chiqui7 letterbox 重跑 preds 与 T3 raw 逐位一致。`raw/parity-{v2b,chiqui7}.json`+`parity-run.log` |
| AC4 契约与测试 | **PASS** | contracts/apps 零 diff（RegionCandidate 输出面不变）；单测先红（`raw/test-red-before-impl.log` ImportError）后绿 70/70（+32 用例）；全量回归 **1812 passed+1 skipped+1 failed（test_catalog 既有 BASELINE_FAILURE）=main 基线一致**（1812=1780+32）。commit `c9880955` |
| AC5 文档 | **PASS** | 本回填+[部署记录](../../verification/M2-SFX-T5-TILE-KO/tile-deploy-report.md)+[Handoff](../handoffs/M2-SFX-T5-TILE-KO-zcode-20261006.md)；**r1 P3-2 闭合**=`_assert_tile_caliber`（typed ProviderInvalidOutput，非 assert 语句不可被 -O 剥除；校验非空/首锚点 0/步长或页底锚点/末锚点覆盖页底/非退化；`_tile_ys` 每调用断言+单测 5 面） |

**偏差与限制登记**：①测试初版两处设计错（fail-fast 漏 setenv；端到端页 aspect 2.97 低于路由下限未触发 tile）在实现完成前修正，红证据 log 为首次全量红（collection error），未伪造过程证据；②GPU 档=呈报数据，生产引擎冻结 CPU EP 不动，启用 GPU 属用户部署形态终选+后续 Task；③ORT DML 会话部分节点未分配 preferred EP warning 如实登记（deploy report §1）；④宽≠600/690 KO 形页按常量阈值参数化=KO-TILE §9 既有缺口，未扩大授权面。

**偏差登记（DSH r1 条件闭合，r1=approved_with_conditions 0×P0/P1/P2、3×P3、4×P4，报告 doc/reviews/M2-SFX-T5-TILE-KO-aa5095cc-dsh-r1.md）**：
- **P3-1 AC3 硬门语义硬化（返修实改）**：`verify_tile_parity.py` KO 段硬断言原只消费 matched 总数（bit_parity 字段只记录不断言）——已并入 `assert all(bit_parity_vs_t3_raw)` 并把 `bit_reproduction` 拆为 `matched_reproduction`/`preds_bit_equal` 两字段。**本轮入库 parity 产物 8 个 KO 页 flag 全 true（DSH 独立逐页对 T3 raw 交叉核验过），不重跑**；脚本强化后下次重跑生效。
- **P3-2 路由生效面登记**：路由按**页面形状全局生效**（宽≤690 且 aspect≥8.0），不绑定 KO 书域——任何满足形状的页（含非 KO 长条页）默认走 tile，代价约 20×（CPU 均值 10.46s/页 vs letterbox 0.3-0.5s/页）。跨域长条页代价评估与阈值复标留后续候选 Task。
- **P3-3 degenerate 负例补齐（返修实改）**：`_assert_tile_caliber` 的 degenerate 分支（`tile_h<=0`）为防御性代码——在 tile_h>0 且 first-anchor/step 检查通过时 `_tile_ys` 输出不可达；合成负例 `[0], page_h=0, tile_h=0` 单测覆盖，注释明示「常量冻结本身由 `test_tile_constants_are_frozen` 承担、运行期门只发现序列构造漂移」。
- **errata（P4-1/P4-2/P4-4）**：①`c9880955` 提交信息「22 例」应读作 **32 个收集项**（13 函数含 ×20 参数化；与 +32/1812 算术一致）；②交付链首环前另有 `217f3383`（Task 合同 base_commit 更新，doc-only，编排侧 cherry-pick）；③`NEWMANGA_SFX_TILE=off` 不短路其余 4 个几何/阈值 env（off+非法值仍 fail-fast=与「anywhere 非法即 ValueError」口径自洽）。

**交付链**：`c11a2a9d` claim → `98338691` impl → `c9880955` test → `24ae2765` verify → docs commit（本提交）。下一环=DSH 非作者 r1 Review（指令见 Handoff）。
