---
id: GATE3-SETTINGS-SHORTCUT-1
title: 闭合条件 3 最后一个 ⚠️ 格（设置空间不吞全局快捷键）
kind: fix
governance_version: 3
status: done
disposition: "条件 3 矩阵『设置/快捷键』格 ⚠️：只有『settings 不是 Space 入口』一条，未证明快捷键仍生效"
approval: DSH 2026-11-15
suggested_owner: DSH
owner: DSH
reviewer: reviewer-g3dc（DSH 子 agent，独立上下文，未参与实现；2026-11-17 复核）
depends_on:
  - GATE3-SIDECAR-COVERAGE-1
base_commit: 411dada59
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 89b36c3f2
delivery_head: 89b36c3f2
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
- [x] **AC2 用户行为级测试**：新增 `SettingsSpaceShortcutTests.ConsoleSpace_DoesNotSwallowGlobalShortcuts`（Ctrl+D3 进 Console → 断言 `State.CurrentSpace == SpaceId.Console`；从 Console 按 Ctrl+K → 断言被处理且 `IsPaletteOpen`；Esc 关闭；Ctrl+D2 回 Studio 并断言空间）。 <<MET>>
- [x] **AC3 判别力实测**：把 `ConsoleWorkspaceView.TryHandleKey` 临时改为 `=> true`（吞所有键）→ 测试**变红**（`:64`）；按字节还原 → SHA 一致、该源文件 git status 为空、重建后通过（`PROBE` 残留 0）。 <<MET>>
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

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果（2026-11-17 复测） | 证据 |
|---|---|---|---|---|
| AC2 | `--filter SettingsSpaceShortcutTests` | 无夹具 | **1 passed / 0 skipped / EXIT=0** | EV-G3SS-01 |
| AC3 | 改 `TryHandleKey => true` 重跑 | 同上 | **1 failed（:64）/ EXIT=1**，还原后 SHA 一致、源文件 git status 为空 | EV-G3SS-01 |
| AC5 | App.Tests 全量无夹具 + 权威 `test.ps1` | 同上；test.ps1 带 sidecar 夹具 | **962 / 0 / 11 / 973**（无夹具）；**1591/1639、48 skipped、EXIT=0**（test.ps1） | EV-G3SS-02/03/04 |

## 依赖、风险与阻塞

- **风险 R1**：`Ctrl+K` 会打开命令面板，遮住后续按键 → 测试里先 `Esc` 关闭再断言空间切换（已处理）。
- **风险 R2**：`Ctrl+D3` / `Ctrl+D2` 是 Space 切换快捷键，若被改绑，测试会失效并给出明确消息（已写断言消息）。
- **风险 R3（本轮实测新增）**：探针注入后若用 `--no-build` 跑全量，会用到带补丁的旧二进制，制造 3 条假失败（含本卡测试）。**探针之后必须重建**；本轮已按此执行并复确认。

## 交付与运行记录

- Handoff：本卡为测试+文档卡，无独立 Handoff；交付记录见本卡与 `verification/GATE3-SETTINGS-SHORTCUT-1/`。
- Review：`doc/reviews/GATE3-SETTINGS-SHORTCUT-1-INDEPENDENT-REVIEW-2026-11-17.md` —— 复核者 `reviewer-g3dc`（DSH 子 agent，独立上下文，未参与实现），reviewed_head `89b36c3f2`，decision **`ACCEPTED_WITH_FINDINGS`**（P0=0 / P1=0 / P2=2 / P3=2）。两条 P2 已在本轮处置：① AC5 更正理由改为「其后新增 11 个用例」（原写「不同源」不成立）；② 条件 3 矩阵 §5 的「2 个 ⚠️ 格」已加 2026-11-17 更正段，与 §9.1「⚠️ 格：0」一致。
- 实际测试：见上表（2026-11-17 复测，head `24c573d1b`；被审 head `89b36c3f2`）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|
| EV-G3SS-01 | AC2/AC3 定向测试 + 判别力探针 | verification/GATE3-SETTINGS-SHORTCUT-1/ac2-ac3-2026-11-17.log | 1ef6a2ebd | cfa29e0fd1726ec347d6b0f1d05070bf4a09f3077217369637d1397158d5ee39 | CANONICAL | BLOB |
| EV-G3SS-02 | AC5 权威 test.ps1 | verification/GATE3-SETTINGS-SHORTCUT-1/ac5-testps1-2026-11-17.log | 1ef6a2ebd | 9302e21932d977557cf7b4828dad3390d6945a05448034bfd618c80c3c63ffd2 | CANONICAL | BLOB |
| EV-G3SS-03 | AC5 分项目计数 | verification/GATE3-SETTINGS-SHORTCUT-1/ac5-testps1-summary-2026-11-17.json | 1ef6a2ebd | ed1c19c3d626296aeae2f6c55ffc1407aa496838421200e989aa7e63f8e5ce49 | CANONICAL | BLOB |
| EV-G3SS-04 | AC5 无夹具 App.Tests | verification/GATE3-SETTINGS-SHORTCUT-1/ac5-app-nofixture-2026-11-17.log | 1ef6a2ebd | f8d8afcdb8580f181c4dd2f99e0cf6405806e7153113a05d3870c0e4eb5494f7 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/GATE3-SETTINGS-SHORTCUT-1/ | NOT_APPLICABLE | — | — | 4 个证据文件已逐行登记于 Canonical Evidence；无迁移/归档/删除；workspace 临时运行目录不入库 |

## Closeout Record

- Closeout date / DSH：2026-11-15 立卡；2026-11-17 由 DSH 补终态材料（本轮）。
- canonical_evidence_status：`complete`；resource_closeout_status：`complete`。
- 删除、迁移、归档数量/字节数：0。
- **实测（2026-11-17，head `24c573d1b`，集成提交 `1ef6a2ebd`）**：
  - 定向测试 `SettingsSpaceShortcutTests` → **1 passed / 0 failed / 0 skipped，EXIT=0**；
  - 判别力探针（`ConsoleWorkspaceView.TryHandleKey => true`）→ **1 failed**，失败消息 `Ctrl+K did not open the command palette from Settings`（`SettingsSpaceShortcutTests.cs:64`），**EXIT=1**；按字节还原后源文件 sha256 与注入前一致（`5227fce8…`）、`git status -- <源文件>` 为空；重建后复测 **1 passed，EXIT=0**；
  - 权威 `test.ps1` → **TEST PASS 1591/1639 passed, 48 skipped, EXIT=0**（App 969/0/4/973；Host 364/0/44/408；CoreClient 258/0/0/258）；
  - 无夹具 App.Tests → **962 passed / 0 failed / 11 skipped / 973 total，EXIT=0**。
- **数字更正（如实登记）**：本卡 AC5 原先写的 `951 / 0 / 11 / 962` 是**时点读数**；本轮实测为 **962 / 0 / 11 / 973**。
  更正理由只有一条：**该读数之后仓库新增了 11 个运行时用例**（总数 962→973、通过 951→962、skip 仍 11、failed 0），不是口径错误、也不是回归。
  （原写式 `951+0+11=962` 本身自洽；`GATE3` 独立复核 r1 的 P2-① 已据此更正。）
- **结论**：条件 3 矩阵的**最后一个 ⚠️ 格**已由 `SettingsSpaceShortcutTests.ConsoleSpace_DoesNotSwallowGlobalShortcuts`（FQN）固定住，且**判别力经探针实测**（吞键即变红）。
  ⇒ **矩阵内 ❌ 与 ⚠️ 格均已清零。**
- **边界**：这**不等于**条件 3 MET —— 仍有带夹具 skip（Host 44 + App 4，均 opt-in/需真实 IPC）、§0 未纳范围的 GUI 流程（回收站/命令面板之外的源恢复/沉浸等）、以及真机走查。
- 未关闭项：见上。
