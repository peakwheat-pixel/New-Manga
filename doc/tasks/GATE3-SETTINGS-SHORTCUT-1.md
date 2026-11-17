---
id: GATE3-SETTINGS-SHORTCUT-1
title: 闭合条件 3 最后一个 ⚠️ 格（设置空间不吞全局快捷键）
kind: fix
governance_version: 3
status: in_review
disposition: "条件 3 矩阵『设置/快捷键』格 ⚠️：只有『settings 不是 Space 入口』一条，未证明快捷键仍生效"
approval: DSH 2026-11-15
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - GATE3-SIDECAR-COVERAGE-1
base_commit: 411dada59
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/GATE3-SETTINGS-SHORTCUT-1
allowed_paths:
  - doc/tasks/GATE3-SETTINGS-SHORTCUT-1.md
  - doc/reviews/GATE3-SETTINGS-SHORTCUT-1-*.md
  - doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md
  - doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/GATE3-SETTINGS-SHORTCUT-1/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
---

# GATE3-SETTINGS-SHORTCUT-1：设置空间不吞全局快捷键

## 背景

条件 3 矩阵（`MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md` §3）"设置 / 快捷键"格是**最后一个 ⚠️**：
证据只有 `ConsoleSpaceUsesWorkbenchConsoleAndSettingsRemainANonSpaceEntry`，它证明的是
"设置不是 Space 入口"，**不是**"在设置页时快捷键仍然生效"。两件事不能互替。

## 代码事实（先读，不猜）

`AppShellViewModel.HandleKey` 的路由是 **"workspace 先否决，再 shell KeyMap"**：

```csharp
var workspace = State.GetWorkspace(State.CurrentSpace);
if (workspace is not null && workspace.TryHandleKey(e, State))
{
    e.Handled = true;
    return true;            // <-- 短路，不再走 HandleKeyCore
}
if (HandleKeyCore(e.Key, e.KeyModifiers, isTextInputFocused)) { ... }
```

各 workspace 适配器的 `TryHandleKey`：

| 适配器 | 空间 | 返回值 |
|---|---|---|
| `LibraryWorkspaceAdapter` | Library | `false`（不吞） |
| **`ConsoleWorkspaceView`** | **Console（设置所在）** | **`false`（不吞）** |
| `StudioWorkspaceAdapter` | Studio | 有选择性地处理 Studio 键（R-17） |

⇒ **代码上，Console 空间不吞任何键，全局快捷键应当生效。** 本卡用测试把这一点固定住。

## Acceptance Criteria

- [x] **AC1 代码事实**：记录 `ConsoleWorkspaceView.TryHandleKey => false` 与 `HandleKey` 的短路结构（上文）。 <<MET>>
- [x] **AC2 用户行为级测试**：新增 `SettingsSpaceShortcutTests.ConsoleSpace_DoesNotSwallowGlobalShortcuts`：
      用 `Ctrl+D3` 进入 Console → 断言 `State.CurrentSpace == SpaceId.Console`；
      **从 Console 按 `Ctrl+K`** → 断言被处理且 `IsPaletteOpen`；`Esc` 关闭；
      `Ctrl+D2` 回到 Studio 并断言空间。 <<MET>>
- [x] **AC3 判别力实测**：把 `ConsoleWorkspaceView.TryHandleKey` 临时改为 `=> true`（吞所有键）→
      测试**变红**；还原 → 通过。已实测，未留残留（`PROBE` 计数 0）。 <<MET>>
- [x] **AC4 更新矩阵**：该格 **⚠️ → ✅**，附 FQN。 <<MET>>
- [x] **AC5 不回归**：无夹具 App.Tests **962 / 0 / 11 / 973**（新增 1 个测试；**skip 仍 11，未新增**）；权威 `test.ps1` 全量 **1591/1639、48 skipped、EXIT=0**（App 969/0/4/973、Host 364/0/44/408、CoreClient 258/0/0/258）。 <<MET>>
- [x] **AC6 不虚报**：未发现产品缺陷（设置空间不吞键）；条件 3 仍不判 MET（见 §边界）。 <<MET>>

## 允许修改范围

见 frontmatter（只新增测试文件 + 文档）。

## 禁止范围

- 不得修改 `WorkspaceAdapters.cs` 的语义（除非发现真实缺陷，需先登记）。
- 不得新增 skip/xfail、不得放宽既有断言。
- 不得声称条件 3 MET。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC2 | `--filter SettingsSpaceShortcutTests` | 无夹具 | **1 passed / 0 skipped** | 实测 |
| AC3 | 改 `TryHandleKey => true` 重跑 | 同上 | **1 failed** | 实测 |
| AC5 | App.Tests 全量无夹具 | 同上 | **951 / 0 / 11 / 962** | 实测 |

## 依赖、风险与阻塞

- **风险 R1**：`Ctrl+K` 会打开命令面板，遮住后续按键 → 测试里先 `Esc` 关闭再断言空间切换（已处理）。
- **风险 R2**：`Ctrl+D3` / `Ctrl+D2` 是 Space 切换快捷键，若被改绑，测试会失效并给出明确消息（已写断言消息）。

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
- **结论**：条件 3 矩阵的**最后一个 ⚠️ 格**已由
  `SettingsSpaceShortcutTests.ConsoleSpace_DoesNotSwallowGlobalShortcuts` 固定住；
  **判别力实测**（把 `ConsoleWorkspaceView.TryHandleKey` 改成 `=> true`）会使其变红。
  ⇒ **矩阵内 ❌ 与 ⚠️ 格均已清零。**
- **边界**：这**不等于**条件 3 MET —— 仍有带夹具 skip（Host 44 + App 4，均 opt-in/需真实 IPC）、
  §0 未纳范围的 GUI 流程（回收站/命令面板之外的源恢复/沉浸等）、以及真机走查。
- 未关闭项：见上。
