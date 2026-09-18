---
id: TASK-051
title: 工作台三档视图解析 translated/compare（§11 P-6）
kind: bugfix
status: done
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: 窗口内独立子对话（approved_subagent；T1 后由 Codex/DSH/Qoder post-hoc）
depends_on: [TASK-013, TASK-038, TASK-050]
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
branch: agent/zcode/TASK-051-workbench-viewer-modes
worktree: G:/CODEX/New Manga.worktrees/TASK-051-zcode
integration_commit: 65d1e13
---

# TASK-051：工作台三档视图（§11 P-6，P1）

**READY（2026-09-19，ZCode 全权窗口 W4）**：Owner=`ZCode`、Reviewer=**独立子对话**、base=`8bf8da3`。**前置：TASK-050 已集成**（端到端演示需要链上前进）。开工先 `git merge master`。

## 来源与目标

来源＝§11 与复核探针：`src/bootstrap/app.py:108-110` 的 `_ManagedPageCatalog.image_url` 在 `mode != "original"` 时**直接返回 `""`**，而该 catalog 于 `app.py:639` 注入 `WorkbenchViewModel`；对照阅读器侧 `_ManagedReaderCatalog` **会**解析页的 current `TRANSLATED` artifact。

实测（复核探针 `codex-p2-p6-probe.txt`）：同一页、同一 Managed Copy —— workbench 的 `translated` / `compare` 恒为 `''`，reader 的 `translated_path` 非空。

**目标**：工作台三档视图（原图 / 译图 / 对比）在数据存在时**能解析出对应图像**，语义与阅读器一致（同一 current revision），不存在时给出可诊断的空态而非静默空白。

## Acceptance Criteria

- [x] **AC ①（解析规则）**：`_ManagedPageCatalog.image_url(page_id, mode)` 支持 `translated`（当前 TRANSLATED revision）与 `compare`（语义须写明并实现：例如并排/叠加所需的两个来源，或明确复用哪两个 artifact）；**必须复用** `SqlitePageArtifactLocator.locate_current(...)` 与既有 Managed Copy 路径校验（根内校验不得绕过）。
- [x] **AC ②（与阅读器一致）**：给出"同页同 revision"的断言证据（workbench 解析出的路径 == reader 解析出的同一 revision 的路径）。
- [x] **AC ③（缺失语义）**：无 translated/compare 数据时返回空态且 VM/QML 能区分"无数据"与"路径非法"（typed/可诊断；不得静默混淆）。
- [x] **AC ④（QML 不改）**：`src/ui/qml/**` 零改动（`ViewerPanel.qml` 既有绑定已就绪）；若确需改 QML → 停下交 Codex 登记范围变更（本窗口按 BLOCKED 处理）。
- [x] **AC ⑤（判别力 + 不回归）**：新用例对修前失败；`tests/core/**`（bootstrap 契约）、`tests/workbench/**` 既有断言逐条不变；全仓 passed 不减少；≥5 次逐次记录（不设 `QT_QPA_PLATFORM`）。
- [x] **AC ⑥** Handoff + `verification/TASK-051/**` + 独立子对话 Review + 集成 + STATUS 台账行。

## 允许修改范围

- `src/bootstrap/app.py`（catalog 解析；**装配点是 `assemble_services`/`assemble_engine`**）
- `src/ui/viewmodels/workbench/**`（仅当需要暴露空态/诊断）
- `tests/workbench/**`、`tests/core/**`
- 本 Task、Handoff、`verification/TASK-051/**`、`doc/STATUS.md`（台账行）

## 禁止范围

- 不得改 `src/ui/qml/**`、Schema/migration、`requirements.txt`、pipeline seam、`AGENTS.md`、其他 Task；不得放宽既有断言或新增 skip；不 push。
- 不得用"临时拼路径"绕过 Managed Copy 根校验（路径必须落在 managed 根内）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC ①② 同一 revision | `pytest tests/core tests/workbench -q -rs` | 真 SQLite + 发布 translated artifact | 87 passed（含 3 新用例；translated 路径==reader 同 revision） | targeted-core-workbench.log |
| AC ⑤ 全仓 | `pytest -q -rs` ×5 | 不设 `QT_QPA_PLATFORM` | 895 passed, 0 skipped, exit 0 ×5 | full-suite-post-fix-run{1..5}.log |

## 依赖、风险与阻塞

- 硬依赖：TASK-038（装配与 catalog 注入）、TASK-050（能产出 translated 的前置链）。
- 风险：`compare` 的**语义未定**（并排 vs 叠加 vs 双图切换）→ 若无法从 D 文档与既有 QML 绑定推出，按 `BLOCKED` 处理并写明需要产品裁决，**不要自创**。

## 交付与运行记录

- Handoff：`doc/handoffs/TASK-051-3cc5cf5.md`。Review：独立子对话（进行中，报告将落 `doc/reviews/TASK-051-3cc5cf5.md`）。实际测试：见上方测试要求表与 `verification/TASK-051/**`。
- **最近状态（当前，唯一）**：2026-09-19 ZCode 于窗口 W4 实现并取证完毕（实现提交 `3cc5cf5`）：compare 语义从 ViewerPanel.qml（D05 §20.1 左右双图）推出（无需产品裁决）；catalog 注入 locator 解析 translated/compare（根内校验不绕过）+ image_state typed 空态 + VM viewerImageStateFor Slot（QML 零改动）；3 新用例、定向 87、全仓 895×5 全绿；判别力=修前树 2 failed（exit 1）+ 双树探针（EMPTY/unavailable ↔ resolved/ok）。独立子对话 Review `approved_subagent`（doc/reviews/TASK-051-3cc5cf5.md，3×P3 不阻断）；integration=`65d1e13`，集成后 master 全仓 895 passed / 0 skipped exit 0。T1 后由 Codex + DSH + Qoder post-hoc 复审（可推翻）。原开立记录：2026-09-19 由 Codex 依 §11 复核结论开立为 `ready`（窗口 W4）。
