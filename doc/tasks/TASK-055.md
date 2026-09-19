---
id: TASK-055
title: TASK-021 冻结子集①：日志与诊断
kind: implementation
status: done
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: 窗口内独立子对话（approved_subagent；T1 后由 Codex/DSH/Qoder post-hoc）
depends_on: [TASK-021]
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
branch: agent/zcode/TASK-055-diagnostics
worktree: G:/CODEX/New Manga.worktrees/TASK-055-zcode
integration_commit: 0493ea9
---

# TASK-055：日志与诊断（TASK-021 冻结子集①，优先子集）

**READY（2026-09-19，ZCode 全权窗口 W8）**：Owner=`ZCode`、Reviewer=**独立子对话**、base=`8bf8da3`。无前置（TASK-021 的 trash 子集已集成）。

## 来源与目标

来源＝[TASK-021](TASK-021.md) 的冻结子集之一（备份恢复 / 缓存·版本·模型清理 / **日志与诊断**）；既有材料：`src/infrastructure/network/diagnostics.py`。

**目标**：交付**可用的日志/诊断能力**（不引入新依赖）：可导出诊断包（应用版本、Schema 版本、设置摘要、最近错误、环境与路径摘要，**凭据零泄漏**），并有界地保留。

## Acceptance Criteria

- [x] **AC ①（诊断包）**：一键导出诊断信息（脱敏；**不得包含凭据/密钥/用户源文件内容**），字段清单在 Task/Handoff 写明。
- [x] **AC ②（日志边界）**：日志落盘位置、大小/数量上限与轮转/截断策略明确并实现（不得无限增长）。
- [x] **AC ③（错误可见面联动）**：与 TASK-052 的错误状态**不冲突**（同一错误码口径；若需要引用则复用，不另造）。
- [x] **AC ④（白名单按实际结构收紧）**：开工前用 `rg` 核实真实路径后再动手；**草案路径不存在时以实际结构为准并在 Task 内记录**（TASK-021 的白名单曾出现草案路径全不存在的情况）。
- [x] **AC ⑤（不回归 + 判别力）**：新用例对修前失败（或说明不适用）；全仓 passed 不减少；≥5 次逐次记录（不设 `QT_QPA_PLATFORM`）。
- [x] **AC ⑥** Handoff + `verification/TASK-055/**` + 独立子对话 Review + 集成 + STATUS 台账行。

## 允许修改范围

- `src/application/**`、`src/infrastructure/**`（诊断/日志相关；**待按实际结构收紧**）
- `tests/**`（对应目录）
- 本 Task、Handoff、`verification/TASK-055/**`、`doc/STATUS.md`（台账行）

## 禁止范围

- 不得新增依赖（`requirements.txt` 零改动）；不得改 Schema/migration（确需 → BLOCKED）；不得改 `AGENTS.md`/其他 Task；不得放宽断言或新增 skip；不 push。

## 交付与运行记录

- Handoff：[TASK-055-7f13e53.md](../handoffs/TASK-055-7f13e53.md)。Review：尚无（待窗口独立子对话 Review）。实际测试：新套件 19 例 + 全仓 ×5（870/0，=851 基线 + 19 新用例）+ 相邻面 storage/core 72/0，全部入库 `verification/TASK-055/`。
- **集成完成（2026-09-19，当前）**：首轮独立子对话 Review `changes_requested`（R-001 P1：to_dict 丢字段）→ 修订 `c175657` 修复（R-001/R-002/R-004/R-007）→ 复审 `approved_subagent`（[TASK-055-c175657](../reviews/TASK-055-c175657.md)，固定被审 `60d1d55`）→ ZCode 按窗口授权代行集成 `0493ea9`（--no-ff，其上已含并行会话 TASK-048），集成后 master 复跑定向 19/0、全仓 873/0 ×2。装配接线与 QML 入口 NOT_RUN（见 Handoff）。历史：2026-09-19 ZCode 实现（AC ④ 白名单收紧记录：实际落地 `src/application/maintenance/diagnostics.py` + `src/infrastructure/filesystem/bounded_log_store.py` + `tests/diagnostics/**`；零新依赖、零 Schema）。实现提交 `7f13e53`。**装配接线与 QML 入口不在本切片**（bootstrap 未触碰；QML 受 TASK-047 门约束），生产可达登记 NOT_RUN、待装配切片注入。`base=8bf8da3`（开工已 merge master `aaef5f2`，含 TASK-046/TASK-054）。

> **2026-09-19 记录补齐（Qoder 后置复审 Q-011）**：本 Task 的 AC 勾选此前遗漏（`status: done` 而方框仍为 `[ ]`），已按 Review/集成记录补齐；达成情况以 [Review](../reviews/) 与 `verification/TASK-055/**` 为准。

> **2026-09-19 未落点登记（后置复审 Q-006，P2）**：`src/application/maintenance/diagnostics.py` 的 docstring 承诺「每个值入报前过脱敏屏」，实现只对 `settings_summary`/`environment_paths` 调 `redact_value`；`app_version`/`platform_python`/`database_path` 与 `recent_errors.message` **裸传**，且合成键 `{occurred_at} {source}` 结构上不可能命中 `_SENSITIVE_KEY`（测试用良性 `a.png` 掩盖）。**诊断包会外发，属隐私面** ⇒ 建议开小切片：要么把 `recent_errors` 也过屏并补含路径/令牌子串的用例，要么删除该不变式措辞。
