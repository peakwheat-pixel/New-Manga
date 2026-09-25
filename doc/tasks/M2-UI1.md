---
id: M2-UI1
title: React Feature Parity & Visual Contract
kind: design
status: ready
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
| AC1 | planned：`rg --files src/ui/qml -g '*.qml'` 与矩阵逐项比对，确认恰有 25 项并覆盖四页及窗口/共用组件 | 固定基线 | NOT_RUN | `verification/M2-UI1/**` |
| AC2/3 | planned：逐组件核对 QML、Tokens、05 UI Mapping、User Flow 与 Design F 来源，记录行号/冲突 | 只读源码和文档 | NOT_RUN | 设计契约与来源表 |
| AC4/5 | planned：隔离 GUI 采集或给可执行复现步骤；`git diff --name-only <base> <delivery>`、`git diff --check <base> <delivery>` | 与生产环境匹配；固定 Delivery head | NOT_RUN | 截图/环境/原始日志或明确 NOT_RUN |

## 依赖、风险与阻塞

硬依赖 M2-D1=`done`。与 I1/I2/R1 可并行；UI1 只定义迁移契约，不释放生产 React/Tauri。当前 React UI 实现 Owner 的历史待决项不由本设计 Task 自动裁决。固定 Delivery/Handoff 后经 Codex 非作者 Review/集成才 `done`。

## 交付与运行记录

- 固定代码基线 `6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`。开工核对 worktree/branch/HEAD/common directory、注册提交与干净状态。
- Handoff、Review、实际验证、integration commit：尚无；上述验证均 `NOT_RUN`。
