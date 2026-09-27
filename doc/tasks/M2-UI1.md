---
id: M2-UI1
title: React Feature Parity & Visual Contract
kind: design
status: done
approval: approved_by_user_2026-09-25
suggested_owner: Qoder
owner: Qoder
reviewer: Codex
final_reviewer: Antigravity
depends_on: [M2-D1]
base_commit: 6a68fdeb92d8a1c7903166a8076d6260bf8fa79a
delivery_head: 23a5ac00acc7f11bc7dc8c5eaec207957784fd9b
reviewed_head: 784ce1831adc791882383681a743984c4b847d0b
review_commit: 83a795b6717b8f4aed2d84cba3405e09a232ebd5
branch: agent/qoder/M2-UI1-react-parity-visual-contract
worktree: G:/CODEX/New Manga.worktrees/M2-UI1-qoder
integration_commit: 5242f64882d2189e177fff19a75ad16630693566
---

# M2-UI1 — React Feature Parity & Visual Contract

## 来源与目标

按 [AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md) 的增量 parity 约束，对现有 `src/ui/qml/**` 的 25 个 `.qml` 文件逐一建立未来 React 的行为与视觉迁移契约。参考 Design F / Graphite Atelier、`Tokens.qml`、[05 UI Mapping](../05_UI_MAPPING.md)、[User Flow](../04_USER_FLOW.md) 和真实 QML 行为；文档与代码不一致时列出证据，不以目标图推断已实现。`src/ui/qml/**` 另有 `qmldir`，须作为 token 注册依赖纳入盘点但不计入 25 个 `.qml` 文件。

## Acceptance Criteria

- [x] **UI1-AC1**：Feature Parity Matrix 对 25 个 `.qml` 文件逐个定位页面/组件、可见功能、输入/状态/输出、用户流程、对应测试及未验证项；四个一级页面齐全。
- [x] **UI1-AC2**：React Component Map 说明现有 QML→拟议 React 组件与边界、状态来源和调用关系；不给 React 直接 SQLite/业务权威。
- [x] **UI1-AC3**：Design Token Migration Map 对 `Tokens.qml`、Design F 色彩/排版/间距/尺寸/状态语义逐项映射；区分实际生产值、文档目标与需裁决差异。
- [x] **UI1-AC4**：Visual Regression Baseline 有固定基线 commit、视图/状态/尺寸/字体/平台/截图或可复现采集步骤、比较与验收口径；不可执行截图项记 `NOT_RUN`，不虚构基线图。
- [x] **UI1-AC5**：明确未来逐功能 parity Gate：实现、测试、行为/视觉验证、Release 决定完成前 QML 保留。无生产 React/Tauri 或 QML 改动。

## 允许修改范围

- `doc/tasks/M2-UI1.md`、`doc/design/M2-UI1_REACT_FEATURE_PARITY_VISUAL_CONTRACT.md`（拟新增）、`doc/handoffs/M2-UI1-*.md`（只新增本 Task Handoff）、`verification/M2-UI1/**`（只新增盘点、截图、清单与验证证据）。

共享规划/索引仅 Codex 更新。所有 `src/**` 和现有需求/设计文件只读；文档漂移交 Codex 决定后续修订范围。

## 禁止范围

不实现 React/Tauri/IPC，不修改 QML、Tokens、生产代码/测试、Schema、打包或 T3.2.1；不决定仍未授权的 React UI 实现 Owner 分配或新增产品功能。

## 测试要求

| 场景/AC | 计划命令或步骤 | 环境 | 当前结果 | 证据 |
|---|---|---|---|---|
| AC1 | `rg --files src/ui/qml -g '*.qml'` 与矩阵逐项比对，确认恰有 25 项并覆盖四页及窗口/共用组件 | 固定基线 worktree | **PASS**：25 文件 + `theme/qmldir`，四页齐全，矩阵 25 行（§1.1–1.7） | `verification/M2-UI1/qml-inventory.txt`；契约 §0/§1 |
| AC2/3 | 逐组件核对 QML、Tokens、05 UI Mapping、User Flow 与 Design F 来源，记录行号/冲突 | 只读源码和文档 | **PASS**：映射表 + 令牌表逐项落位；冲突 11 条（C-1…C-11）与偏差 D-1…D-6 附行号 | 契约 §2/§3/§7 |
| AC4 | 隔离 GUI 采集：`capture_baseline.py`（派生自 repair-13 probe，+窗口激活/VM 直驱回退）在 src≡base 的工作树实采 14 帧；三次尝试日志全留 | Windows 真平台（禁 offscreen）、venv TASK-012-py312、1280×800@100% dark | **PASS(13/14)**：13 帧有效；焦点环帧存在但降级；§4.3 共 10 项 NOT_RUN（含焦点环，另有 9 类场景未采），未虚构基线图 | `verification/M2-UI1/baseline-6a68fde/**`（manifest + capture.log + 帧 sha256 + attempt1/2 失败日志） |
| AC5 | parity Gate 七步定义 + 本 Task 自身零生产改动：`git diff --name-only <base> <delivery>`、`git diff --check <base> <delivery> -- src tests doc` | 固定 Delivery head | **PASS**：Gate 见契约 §5；写集合仅授权 4 路径，`src/**` 零命中；diff --check 结果见 Handoff | 契约 §5/§8；Handoff 验证表 |

## 依赖、风险与阻塞

硬依赖 M2-D1=`done`。与 I1/I2/R1 可并行；UI1 只定义迁移契约，不释放生产 React/Tauri。当前 React UI 实现 Owner 的历史待决项不由本设计 Task 自动裁决。固定 Delivery/Handoff 后经 Codex 非作者 Review/集成才 `done`。

## 交付与运行记录

- 固定代码基线 `6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`。开工核对：worktree `G:/CODEX/New Manga.worktrees/M2-UI1-qoder`、branch `agent/qoder/M2-UI1-react-parity-visual-contract`、HEAD `5d989ba`、common dir `G:/CODEX/New Manga/.git`、工作区干净——全部一致；`git diff --name-only 6a68fde 5d989ba` 仅 `doc/**`，src 树与 base 逐字节一致。
- 交付物：`doc/design/M2-UI1_REACT_FEATURE_PARITY_VISUAL_CONTRACT.md`（矩阵/映射/令牌/基线/Gate/冲突清单）+ `verification/M2-UI1/**`（盘点、派生采集脚本、基线帧与三次尝试日志）。
- 采集环境事实：本机（非 Sandbox）合成指针事件不触达 TapHandler/MouseArea、`forceActiveFocus` 不生效——tile 选中改由 `vm.selectPage` 直驱（状态等价、已在脚本 docstring 与 manifest 注记），焦点环帧记降级。
- Handoff：`doc/handoffs/M2-UI1-8031173.md`（Delivery `80311732c3224c7054ad4bc2ba8ba0bee7f2f765`）；Review：Codex `doc/reviews/M2-UI1-8031173.md`（decision=**changes_requested**，R-001 P1 + R-002/3/4 P2）。
- **R2 返修（2026-09-25，本轮）**：按 Review 修订契约——R-001 §3.3 重写为页级/Run 级两组状态域，页级 `blocked` 映射记为源契约未定义项留裁决（不擅改 QML、不声称修复已授权），§7 C-4/§1.4 #16/§4.3 同步；R-002 C-2 目标树缺项 11→**21**（附 39/18/21 计数口径与逐项清单）；R-003 新增 §1.4a 命令面枚举=**24 方法/25 站点**（stepPage 双汇入），§1.4 #14 与 §2.2 替换「12」；R-004 令牌计数改 **40 色 + 2 阴影串（×2 主题=42 主题值）、状态 9+7**（§1.7 #25、§2.2、§3 引言、§3.1）。另回填 Review 对 C-9/C-11 的裁决（现状无缺陷/节流在 VM `PROGRESS_REFRESH_MS=250`）并修正 §0 页面文件数（工作台 8）。原始采集日志未覆盖；本轮无重跑采集。
- 返修门禁证据：`verification/M2-UI1/repair-gates-<R2head>.log`（`git diff --name-only/--check 5d989ba..<R2 head>`、base→head `src tests` 零差分）；新 Handoff 见 frontmatter `delivery_head` 同名文件。复审：Codex 按同 base 于 reviewed head 784ce1831adc791882383681a743984c4b847d0b 批准；集成 merge commit 212efa54daee1d57e2c4510c56a022c9b4f65f67。

## Codex R2 复审与集成

- R2 Review：[M2-UI1-23a5ac0-r2](../reviews/M2-UI1-23a5ac0-r2.md)，decision=approved；固定 base=6a68fdeb92d8a1c7903166a8076d6260bf8fa79a、Delivery=23a5ac00acc7f11bc7dc8c5eaec207957784fd9b、reviewed head=784ce1831adc791882383681a743984c4b847d0b。
- 集成：保留 Qoder 原分支的 --no-ff 合并；integration commit=212efa54daee1d57e2c4510c56a022c9b4f65f67。集成起点 master=5803bd7b9e80ba780e7a7f12078b00b9178e6f86，merge-base=5d989bab6c5c8a24a5112303f95c2b8eea356bdc。
- 集成后核验：diff --check 5803bd7b9e80ba780e7a7f12078b00b9178e6f86..212efa54daee1d57e2c4510c56a022c9b4f65f67 exit 0；diff --quiet 6a68fdeb92d8a1c7903166a8076d6260bf8fa79a..212efa54daee1d57e2c4510c56a022c9b4f65f67 -- src tests exit 0；详细证据见 verification/M2-UI1/integration-212efa5.md。
- AC1–AC5 已完成；AC4 的 NOT_RUN 计数已澄清为与契约 §4.3 一致的 10 项，其中焦点环虽有帧但因采集失败而降级。产品测试套件和 GUI 补采未运行，本集成没有将其记为 PASS。
- 未决风险：页级 blocked 的 React 目标映射仍等用户/契约维护方裁决；C-1/D-6 来源契约修订与 C-5/C-6 后续产品取舍仍按 Review 归属处理。本次不释放 React 实现。
- Master 并行推进同步：merge master a91b8f7ed0916b3beb74dd0b88797e82e2305112 的 Codex sync commit=4f20fc24523dfac672b20c9938917d978bdadb0b；提交图允许 fast-forward，但主 worktree 的 REBASELINE_PLAN.md/STATUS.md 有未提交 M2-I2 更新，本轮保留它们，master fast-forward 待这些修改归档后完成。

## Antigravity 独立复审与最终 Integration Gate（2026-09-25）

- 独立复审：[M2-UI1-23a5ac0](../reviews/M2-UI1-23a5ac0.md)，Antigravity 非作者复审，Review commit=`83a795b6717b8f4aed2d84cba3405e09a232ebd5`，decision=`APPROVED`；R-001～R-004 均闭环。Review 明确不授权 React/Tauri 实现，页级 `blocked` 映射仍为 `DEFERRED / CONTRACT_DECISION_REQUIRED`。
- 本轮开工核对指定 master base=`148981a339d12b45fa9a712b247ed92698349c36`。集成过程中 master 前进到 `d13b0b11c169b50024370d16b6cb9394de9a46f5`（包含较早的 UI1 R2 integration `ac521cf` 与后续治理提交）；Codex 在隔离工作树保留该最新主线，并以最终 Integration merge=`5242f64882d2189e177fff19a75ad16630693566` 合入最新 Review 与治理更新。该 merge 的父提交包含最新 master 与 Review 完整的候选。
- Gate 结果：固定 base→最终 integration merge 的 `git diff --check` exit 0；`src/**` / `tests/**` 零差异；所有改动均在 UI1 交付/证据或 Codex 治理路径；固定 base、Delivery、Handoff、Review 与最新 master 均为 integration merge 祖先；Visual Baseline manifest 的 14/14 个截图 SHA-256 复核匹配（13 个可用、1 个降级）。详见 [`integration-final-83a.md`](../../verification/M2-UI1/integration-final-83a.md)。
- 产品 `pytest` 与 GUI 采集未运行：该交付仅为设计契约、审查与证据，没有产品代码/测试改动；因此不将它们记录为 PASS。复审记录的 9 类未采状态仍为 `NOT_RUN`。
- 集成结论：M2-UI1 AC1–AC5 与最终独立 Review 均满足，Task=`done`；integration commit=`5242f64882d2189e177fff19a75ad16630693566`。M2-C1/M2-S1 与 React/Tauri 生产实现授权不受本结论影响。
