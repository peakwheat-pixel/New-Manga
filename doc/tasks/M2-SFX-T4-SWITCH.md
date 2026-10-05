---
id: M2-SFX-T4-SWITCH
title: "SFX 生产切换 V2B（T4）：G7 翻译链深层补证（硬前置先行）+权重通道与 pin 替换+SHA 门反向验证+回退语义出证"
kind: feature
status: ready
owner_claim: —
approval: user_ruling_2026-10-05_三件都同意（切换v2b/tile化立项/G7补证硬前置）
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
depends_on: [M2-SFX-GATE-T3]
base_commit: 5166ba7f
branch: agent/zcode/M2-SFX-T4-SWITCH
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-T4-SWITCH-zcode
review_events: []
created: 2026-10-05
---

# Task: M2-SFX-T4-SWITCH — SFX 生产切换 V2B

## 背景与授权

T3 正式评测门（done @merge `27817412`）逐门判定：**v2b（best.onnx `944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d`）=唯一通过全部定资格硬门（G1/G2/G5/G8）的切换候选**；G7=条件性 PASS（翻译链深层调用补证列为部署前置）。用户 2026-10-05 裁决「三件都同意」：①切换 v2b ②KO tile 化立项（另立 [M2-SFX-T5-TILE-KO](M2-SFX-T5-TILE-KO.md)，depends_on 本 Task）③**G7 补证=切换硬前置**。

现役生产 pin（切换对象）：`SFX_WEIGHTS_SHA256=d87389af…b646`（chiqui7/yolo11-manga-seg ONNX，`detection_sfx.py:110-112`）、`SFX_HF_REPO/SFX_HF_REVISION=chiqui7@7f5f5c04…`（:107-108）。回退语义=T3 §7.4（pin 单值恢复+chiqui7 权重在位）。

**执行顺序硬约束：AC1（G7 补证）未 PASS 前不得动任何 src/权重通道（fail-fast 停点）。**

## 验收条件

- **AC1 G7 翻译链深层补证（硬前置，先行）**：以 v2b 权重**进程内重指**（零 src，沿 T0/V2/T3 冒烟方式）跑一次 BJ06 型 `policy=translate` 端到端冒烟（run_qualification 级深层调用，先例=M2-SFX-E2E-MATERIAL BJ06 8/8）：EXIT=0+检测→翻译链契约合法（fail-closed 保持，0 候选=合法空输入）+vs chiqui7 同链对照**新增故障=0**（框集差异 directional）。产物落 `verification/M2-SFX-T4-SWITCH/raw/`。**AC1 FAIL 即停止，不进入 AC2，Task 转呈报等裁决。**
- **AC2 权重通道与 pin 替换（src 变更，本 Task 授权面）**：v2b best.onnx 进入生产权重通道（按 M2-SFX-PROD-1 随包机制核对在位路径与 sha 校验链；权重本体 gitignored 不入库，随包/资源通道按既有机制）；`SFX_WEIGHTS_SHA256` 单值替换为 `944e8114…`；`SFX_HF_REPO`/`SFX_HF_REVISION` 来源字段处置=**本地发布通道登记**（V2 报告 §7.2.3 方案：v2b 为本地训练产物非 HF 发布，字段语义改为登记性指向+部署记录留源链 base .pt→best.pt→best.onnx sha 全链，T3 §4.8-2 已验链）；ns 通道/打包面按 PROD-1 先例处理（若 NSIS 随包验证在本环境不可行，如实登记 NOT_RUN+原因，不得声称）。
- **AC3 SHA 门反向验证复跑（DSH r2 转承接项）**：新 pin 在位后，复跑一次「外来权重按生产 pin 加载被 `PROVIDER_FAILED` 拒跑」反向验证（T0/V2 同款），EXIT 语义与断言与先例一致。
- **AC4 回退语义出证**：回退方案实测——pin 恢复 `d87389af…`+chiqui7 权重文件在位+`_build_engine` 冒烟 EXIT=0（证明回退路径真实可行，非纸面方案）；出证后恢复新 pin 终态。
- **AC5 文档与登记**：部署记录（switch report）+G8 checklist 刷新（densho810 报告义务窗口 2026-11-02 时点核查项+许可登记义务三项沿 T3 §4.8-4）+Task 回填+Handoff；STATUS/PLAN 由集成轮收口。

## 纪律与限制

- 允许路径：`src/infrastructure/providers/detection_sfx.py`（仅 pin 常量与来源字段段）、权重资源通道（gitignored/资源目录）、`packaging/**`（仅当随包机制需要）、`tests/**`（仅当 pin 相关断言需同步，逐条声明）、`doc/tasks/M2-SFX-T4-SWITCH.md`、`doc/handoffs/`、`verification/M2-SFX-T4-SWITCH/**`、`experiments/M2-SFX-T4-SWITCH/**`（冒烟/验证脚本）。
- 禁区：`contracts/**`（wire 零变化）、`src/**` 其余文件、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`apps/**`（pin 断言若涉及另行走停等登记）。
- directional 纪律沿 T3（禁用「显著」、FAIL 如实）；AI 产物不得入 Git（权重/数据 gitignored）。
- 考卷/评测资产只读：本 Task 不做任何模型质量评测（T3 已判定），仅部署验证。
