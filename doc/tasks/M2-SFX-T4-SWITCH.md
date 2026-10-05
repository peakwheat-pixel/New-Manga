---
id: M2-SFX-T4-SWITCH
title: "SFX 生产切换 V2B（T4）：G7 翻译链深层补证（硬前置先行）+权重通道与 pin 替换+SHA 门反向验证+回退语义出证"
kind: feature
status: in_review
owner_claim: ZCode 2026-10-05（用户裁决「三件都同意」授权面认领；base=3d4f20f1）
delivery: ZCode 2026-10-06（AC1-AC5 全 PASS，AC1 硬前置先行遵守；delivery head 见交付记录；转 in_review 停写）
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

## 交付记录（Owner=ZCode，2026-10-06）

**结果：AC1-AC5 全 PASS。生产 pin 已切换 v2b（`944e8114…`），G7 补证闭合（自此可记部署就绪），回退路径实测可用。**

| AC | 判定 | 核心证据 |
|---|---|---|
| AC1 G7 翻译链深层补证（硬前置先行） | **PASS** | BJ06 policy=translate 端到端（run_qualification 级）：v2b 臂 EXIT=0（detect 14 region=5 sfx+9 speech → OCR/translate 14/14 落库 → export OK）+chiqui7 对照臂 EXIT=0（17 region，speech 9/9 两臂逐项一致）；`g7-compare.json` verdict **new_failure_count=0**；SHA 门先证 FIRED→重指→finally 恢复（pin_restored=True）。commit `5d5ab592`（先于任何 src 变更） |
| AC2 权重通道与 pin 替换 | **PASS** | pin 单值→944e8114；来源字段=本地发布通道登记（`local-release:sfx-train-v2/v2b` + best.pt 上游锚，注释含全链 sha 1f0fd609→c22f0175→944e8114）；部署副本 weights-v2b/（只读复制，chiqui7 原件未动）；build_sidecar 完整构建 EXIT=0+bundle 权重独立复算逐字；冻结探针 3/3 PASS（FV-1 conf 0.9047 directional）；contracts 零 diff；NSIS 安装器层 NOT_RUN 如实登记（授权面=随包机制，下一发布轮 cleanstart 复验）。commit `5d835e44` |
| AC3 SHA 门反向验证 | **PASS** | 外来 chiqui7 onnx 按新 pin 加载→`PROVIDER_FAILED` 拒跑（gate fired 先于 runtime import）；v2b 部署文件全装载链 OK（imgsz=1024 metadata_parsed）。commit `d631f7ec` |
| AC4 回退语义实测 | **PASS** | pin 临时恢复 d87389af+chiqui7 权重在位→`_build_engine` EXIT=0；chiqui7 文件全程只读；出证后 git checkout 恢复新 pin 终态（AC3 复跑确认）。commit `d631f7ec` |
| AC5 文档与登记 | **PASS** | switch-report（部署记录+G8 checklist 刷新：densho810 窗口 2026-11-02 在册未逾期+许可登记义务三项）+回归锚迁移+Task/Handoff 回填。AC5 commit |

**tests 修改（允许路径逐条声明，唯一文件 `tests/providers/test_detection_sfx.py`）**：①`REAL_WEIGHTS` weights/→weights-v2b/；②真实权重复现锚 chiqui7 payload（conf 0.9313）→v2b 锚 JSON（conf 0.9047，`extract_v2b_anchor.py` 与测试同调用路径提取，与冻结探针 FV-1 跨环境一致）；③新增锚-pin 一致性运行期断言；④REAL_SKIP 文本更新。**回归终态=1780 passed+1 skipped+1 failed（test_catalog 既有 BASELINE_FAILURE）=main 基线一致**（pin 切换后首跑 3 个真实权重测试被 SHA 门 fail-closed 拒跑=预期连带，锚迁移后全绿）。

**偏差登记**：①AC1 冒烟 venv=`M2-TA3-B-ocr`（run_qualification 需 PySide6+manga_ocr，先例同款；任务书所述 FINETUNE venv 用于 AC3/AC4）；②Owner 执行中断续接一次（子 agent 600s 监控超时×2+配额耗尽终止，AC1 后半由编排会话代行 Owner 接管完成——Owner=ZCode 同一作者身份，非作者 Review 约束不受影响）。

**交付 head**：AC5 commit（见 branch tip）；详细部署指引与 NOT_RUN 清单见 [switch-report](../verification/M2-SFX-T4-SWITCH/switch-report.md) 与 [Handoff](../handoffs/M2-SFX-T4-SWITCH-zcode-20261006.md)。
