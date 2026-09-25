---
id: M2-UI1
title: React Feature Parity & Visual Contract
kind: design
status: changes_requested
approval: approved_by_user_2026-09-25
suggested_owner: Qoder
owner: Qoder
reviewer: Codex
depends_on: [M2-D1]
base_commit: 6a68fdeb92d8a1c7903166a8076d6260bf8fa79a
branch: agent/qoder/M2-UI1-react-parity-visual-contract
worktree: G:/CODEX/New Manga.worktrees/M2-UI1-qoder
integration_commit: null
---

# M2-UI1 — React Feature Parity & Visual Contract

## 来源与目标

按 [AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md) 的增量 parity 约束，对现有 `src/ui/qml/**` 的 25 个 `.qml` 文件逐一建立未来 React 的行为与视觉迁移契约。参考 Design F / Graphite Atelier、`Tokens.qml`、[05 UI Mapping](../05_UI_MAPPING.md)、[User Flow](../04_USER_FLOW.md) 和真实 QML 行为；文档与代码不一致时列出证据，不以目标图推断已实现。`src/ui/qml/**` 另有 `qmldir`，须作为 token 注册依赖纳入盘点但不计入 25 个 `.qml` 文件。

## Acceptance Criteria

- [ ] **UI1-AC1**：Feature Parity Matrix 对 25 个 `.qml` 文件逐个定位页面/组件、可见功能、输入/状态/输出、用户流程、对应测试及未验证项；四个一级页面齐全。
- [ ] **UI1-AC2**：React Component Map 说明现有 QML→拟议 React 组件与边界、状态来源和调用关系；不给 React 直接 SQLite/业务权威。
- [ ] **UI1-AC3**：Design Token Migration Map 对 `Tokens.qml`、Design F 色彩/排版/间距/尺寸/状态语义逐项映射；区分实际生产值、文档目标与需裁决差异。
- [ ] **UI1-AC4**：Visual Regression Baseline 有固定基线 commit、视图/状态/尺寸/字体/平台/截图或可复现采集步骤、比较与验收口径；不可执行截图项记 `NOT_RUN`，不虚构基线图。
- [ ] **UI1-AC5**：明确未来逐功能 parity Gate：实现、测试、行为/视觉验证、Release 决定完成前 QML 保留。无生产 React/Tauri 或 QML 改动。

## 允许修改范围

- `doc/tasks/M2-UI1.md`、`doc/design/M2-UI1_REACT_FEATURE_PARITY_VISUAL_CONTRACT.md`（拟新增）、`doc/handoffs/M2-UI1-*.md`（只新增本 Task Handoff）、`verification/M2-UI1/**`（只新增盘点、截图、清单与验证证据）。

共享规划/索引仅 Codex 更新。所有 `src/**` 和现有需求/设计文件只读；文档漂移交 Codex 决定后续修订范围。

## 禁止范围

不实现 React/Tauri/IPC，不修改 QML、Tokens、生产代码/测试、Schema、打包或 T3.2.1；不决定仍未授权的 React UI 实现 Owner 分配或新增产品功能。

## 测试要求

| 场景/AC | 计划命令或步骤 | 环境 | 当前结果 | 证据 |
|---|---|---|---|---|
| AC1 | executed：`rg --files src/ui/qml -g '*.qml'` + 矩阵核对 | 固定基线 `6a68fdeb` | inventory PASS：25 项；矩阵核对有 Review finding R-003，Task 未获批 | `verification/M2-UI1/qml-inventory.txt`；[Review](../reviews/M2-UI1-8031173.md) |
| AC2/3 | executed：逐组件核对 QML、Tokens、05 UI Mapping、User Flow 与 Design F | 只读源码和文档 | 作者 Handoff 报 PASS；独立 Review `changes_requested`（R-001、R-003、R-004） | [Handoff](../handoffs/M2-UI1-8031173.md)；[Review](../reviews/M2-UI1-8031173.md) |
| AC4 | executed：Windows GUI 采集；核对基线、NOT_RUN 与逐帧证据 | Windows 11 10.0.26200；base `6a68fdeb` / capture HEAD `5d989ba` | 14 帧中 13 可用、1 降级；采集脚本 `EXIT=1`（焦点断言），焦点环按 `NOT_RUN` 处理 | `verification/M2-UI1/baseline-6a68fde/{manifest.md,capture.log,attempt1-capture.log,attempt2-capture.log}` |
| AC5 / 写集合 | executed：`git diff --name-only 5d989ba 80311732`；`git diff --check 5d989ba 80311732` | Qoder author branch；固定 Delivery | PASS：作者写集合越界 0；`diff --check` exit 0；生产 QML/React/Tauri 零修改 | [Handoff](../handoffs/M2-UI1-8031173.md)；[Review](../reviews/M2-UI1-8031173.md) |

## 依赖、风险与阻塞

硬依赖 M2-D1=`done`。与 I1/I2/R1 可并行；UI1 只定义迁移契约，不释放生产 React/Tauri。当前 React UI 实现 Owner 的历史待决项不由本设计 Task 自动裁决。固定 Delivery/Handoff 后经 Codex 非作者 Review/集成才 `done`。

## 交付与运行记录

- 固定代码基线 `6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`。开工核对 worktree/branch/HEAD/common directory、注册提交与干净状态。
- Handoff：[M2-UI1-8031173](../handoffs/M2-UI1-8031173.md)，Delivery `80311732` 的后继 Task/Handoff head=`0cdbec2`。Review：[M2-UI1-8031173](../reviews/M2-UI1-8031173.md)，`changes_requested`；integration commit 尚无。

## Codex 非作者 Review（2026-09-25）

- 固定代码基线：`6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`；产品 Delivery：`80311732c3224c7054ad4bc2ba8ba0bee7f2f765`；复核 Handoff 的 reviewed_head：`0cdbec22643e5ef5578582d8f982f337b535139c`。
- Review：[M2-UI1-8031173](../reviews/M2-UI1-8031173.md)，结论 `changes_requested`；未集成。
- Findings：R-001 状态语义映射把页级与 PipelineRun 级 `blocked` 混用（P1）；R-002 §60 目标文件缺失数应复核（P2）；R-003 工作台命令转发计数未与调用面吻合（P2）；R-004 色彩/状态令牌计数不一致（P2）。
- Review 验证：25 项 QML 清单、3 行源码抽查、11 项 C 冲突及 6 项 D 差异逐条裁决、14 帧 manifest 哈希/日志核对、NOT_RUN 诚实性、作者写集合越界 0；产品测试套件由作者标为 `NOT_RUN`，Reviewer 未运行。
- 返修仅限授权设计/任务/Handoff/verification 路径；不改现有需求契约正文、`src/**`、`tests/**`。Qoder 新 head 与更新 Handoff 后交 Codex 复审。
