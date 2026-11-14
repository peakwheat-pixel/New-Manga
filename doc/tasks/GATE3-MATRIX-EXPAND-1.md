---
id: GATE3-MATRIX-EXPAND-1
title: 条件 3 矩阵扩容 —— 把 §0 未纳的 4 个 GUI 流程纳入评估
kind: evidence
governance_version: 3
status: in_progress
disposition: "条件 3 矩阵 §0 明确说 4 页×13 类不等于整个产品 GUI；回收站/命令面板/源恢复/沉浸未评估"
approval: DSH 2026-11-15
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - GATE3-SETTINGS-SHORTCUT-1
base_commit: 13d295f69
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GATE3-MATRIX-EXPAND-1
allowed_paths:
  - doc/tasks/GATE3-MATRIX-EXPAND-1.md
  - doc/reviews/GATE3-MATRIX-EXPAND-1-*.md
  - doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/GATE3-MATRIX-EXPAND-1/**
---

# GATE3-MATRIX-EXPAND-1：矩阵扩容

## 背景

条件 3 矩阵（`MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md`）的 §3 是 **4 页 × 13 类**，
其 §0 明确声明：**这不等于整个产品 GUI 无缺口**。四个流程被点名但从未评估：

**回收站 / 命令面板 / 源恢复 / 沉浸阅读**。

## 本轮实测（先跑后写，不推断）

| 流程 | 测试类 | 实测（无夹具） |
|---|---|---|
| **回收站** | `TrashUiTests` | **47 passed / 0 failed / 0 skipped** |
| **源恢复** | `SourceRecoveryUiTests` | **18 / 0 / 0** |
| **沉浸阅读** | `V2ImmersiveReaderTests` | **4 / 0 / 0** |
| **F11 沉浸开关** | `F11HotkeyTests` | **9 / 0 / 0** |
| **命令面板（焦点）** | `FluentCommandPaletteFocusTests` | **1 / 0 / 0** |

组合 filter（上列全部）实测 **80 passed / 0 failed / 0 skipped**（比五类之和 79 多 1，
多出的那条来自 `~CommandPalette` 还匹配到的其它类；**不据此外推**）。

**关键点**：这五个类**在无夹具环境即可执行**（0 skipped），不依赖 sidecar —— 所以它们是
**当前就能反复验证**的覆盖，不是"等环境"的空白。

## Acceptance Criteria

- [x] **AC1 实测优先**：所有数字来自 `dotnet test --filter`（见上表），**不用源码 grep 计数**
      —— 我一开始用 grep 得到 44/50/4/9/1=108，与实测 47/18/4/9/1=79 不符，已以实测为准（登记）。
- [x] **AC2 矩阵新增 §10**：按"流程 × 覆盖证据"填写，不动 §3 既有格。
- [x] **AC3 标出仍未覆盖的面**：每个流程列出"测试类覆盖了什么"与"仍缺什么"，
      不得用类名存在替代覆盖判断（例如 `TrashUiTests` 47 个不等于"彻底删除全部语义已验"）。
- [x] **AC4 不虚报**：条件 3 仍不判 MET。
- [x] **AC5 不回归**：无夹具 App.Tests 仍 **951 / 0 / 11 / 962**（本卡只读不写代码）。

## 允许修改范围

见 frontmatter（只更新证据与矩阵）。

## 禁止范围

- 不得声称"4 个流程已全覆盖"。
- 不得把类名/方法数当成覆盖证明。
- 不得声称条件 3 MET。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 五个类各自 `--filter` | 无夹具 | 见上表 | 实测 |
| AC5 | App.Tests 全量 | 同上 | 951/0/11/962 | 实测 |

## 依赖、风险与阻塞

- **风险 R1**：`TrashUiTests` 47 个测试覆盖"软删/恢复/彻底删除"的哪一部分**需要逐条核对方法名**，
  本卡只给了类级数字，**不能**据此说"完整语义已验证"（已写进 AC3）。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：见上表。
- 后续记录日期、commit、环境、结果、遗留项。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | 待填 | NOT_APPLICABLE | — | — | 本卡无新增派生物 |

## Closeout Record

- Closeout date / DSH：2026-11-15，DSH。
- canonical_evidence_status：`complete`。
- resource_closeout_status：`complete`。
- 删除、迁移、归档数量/字节数：0。
- **结论（限定）**：§0 点名的四个流程**都有可执行的无夹具 GUI 测试**，合计 **79–80 个通过 / 0 skip**；
  矩阵新增 §10 记录。
- **未达成**：类级数量**不等于**语义完整覆盖（见 §10.2 的逐流程缺口）；条件 3 仍不判 MET。
- **自登记**：本卡先用源码 `grep` 数出 108 个测试，与实跑 79 不符 —— 又一次"以源码推断代替实测"，
  已改用 `dotnet test` 实测并记入卡面。
