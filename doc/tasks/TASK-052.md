---
id: TASK-052
title: 命令失败可见化（§11 P-4：commandError 上屏，最小可见 + provisional）
kind: bugfix
status: ready
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: 窗口内独立子对话（approved_subagent；T1 后由 Codex/DSH/Qoder post-hoc）
depends_on: [TASK-050]
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
branch: agent/zcode/TASK-052-command-error-surface
worktree: G:/CODEX/New Manga.worktrees/TASK-052-zcode
integration_commit: null
---

# TASK-052：命令失败可见化（§11 P-4，P1；最小可见 + provisional）

**READY（2026-09-19，ZCode 全权窗口 W5）**：Owner=`ZCode`、Reviewer=**独立子对话**、base=`8bf8da3`。**前置：TASK-050 已集成**。开工先 `git merge master`。

## 来源与目标

来源＝§11 第 4 项（P1）：`commandError` 共 13 处，**全部**在 `src/ui/viewmodels/workbench/viewmodel.py`（定义 + emit），`src/ui/qml/**` **0 命中** ⇒ `runCrashed`、`PipelineError`、`ProviderNotConfigured`、"已有任务在运行"等全部对用户静默——它是 P-1/P-2/P-3 的**可见性放大器**。

**目标**：让命令失败**对用户可见且可复制**。本切片按用户裁定做**最小可见**实现，并标注为 **provisional**：TASK-047（Qoder 设计门）产出并集成后，由后续设计切片收敛视觉与信息层级。

## Acceptance Criteria

- [ ] **AC ①（VM 状态）**：workbench VM 暴露可绑定的最近错误状态（property + notify）与"清空/已读"入口；emit 路径集中（不得在 13 处各写一套 UI 逻辑）。
- [ ] **AC ②（QML 最小消费者）**：在**工作台页面**内新增一个最小可见元素（状态条/文本 + 复制/关闭），并带 `objectName` 以便契约测试定位；**只改 `src/ui/qml/workbench/**`**，不得改 reader/bookshelf 等其他页面。
- [ ] **AC ③（可诊断性）**：错误文本包含可执行的诊断信息（错误码/阶段），并能一键复制（供用户反馈）。
- [ ] **AC ④（断言）**：VM 级用例覆盖三类真实失败（无 provider 绑定 / 无 Region / worker 崩溃）后状态可见；QML 契约级用例断言该元素在失败后可见、成功后/清空后不可见（机器可验证，不靠"码面推导"）。
- [ ] **AC ⑤（provisional 声明）**：在源码注释与 Handoff 中明确标注"最小实现、待 TASK-047 设计收敛后调整"，并在 Task 内记录该局限。
- [ ] **AC ⑥（不回归 + 判别力）**：新断言对修前失败；`tests/workbench/**`、`tests/ui_shell/**`、`tests/reading_export/**` 既有 QML 契约断言逐条不变；全仓 passed 不减少；≥5 次逐次记录（不设 `QT_QPA_PLATFORM`）。
- [ ] **AC ⑦** Handoff + `verification/TASK-052/**` + 独立子对话 Review + 集成 + STATUS 台账行。

## 允许修改范围

- `src/ui/viewmodels/workbench/**`
- `src/ui/qml/workbench/**`（**仅工作台页面**）
- `tests/workbench/**`、`tests/core/**`、`tests/ui_shell/**`（仅当需要契约断言）
- 本 Task、Handoff、`verification/TASK-052/**`、`doc/STATUS.md`（台账行）

## 禁止范围

- 不得改 `src/ui/qml/` 其他页面、Schema/migration、`requirements.txt`、`AGENTS.md`、其他 Task；不得放宽既有断言或新增 skip；不 push。
- 不得只留 TODO 而无机器化断言；不得把错误吞咽改为"弹窗阻塞"（保持非阻塞可见）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC ④ VM 三类失败 | `pytest tests/workbench -q`（planned） | venv + 真 SQLite | NOT_RUN | 无 |
| AC ④ QML 契约 | `pytest tests/ui_shell tests/reading_export -q`（planned） | 同上 | NOT_RUN | 无 |
| AC ⑥ 全仓 | `pytest -q -rs` ×5（planned） | 不设 `QT_QPA_PLATFORM` | NOT_RUN | 无 |

## 依赖、风险与阻塞

- 硬依赖：TASK-050（P-3）——否则失败码场景难以端到端复现；VM 级用例可用注入方式构造。
- 风险：与 TASK-047（Qoder 设计，窗口外）在**呈现层**冲突 → 本切片按最小可见交付并在 T1 交接包里标注"待设计收敛"。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际测试：尚无（`ready`，前置 TASK-050）。
- **最近状态（当前，唯一）**：2026-09-19 由 Codex 依 §11 复核结论开立为 `ready`（窗口 W5，provisional 呈现）。**实施尚未开始。**
