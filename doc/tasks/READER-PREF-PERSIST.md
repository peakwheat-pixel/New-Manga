---
id: READER-PREF-PERSIST
title: 阅读偏好持久化闭环（单双页/方向/缩放接到 SaveReadingPreferences）
kind: implementation
governance_version: 3
status: in_progress
disposition: "既有缺陷 E-4（doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md）；DSH 2026-11-14 释放"
approval: DSH 2026-11-14（Gate 条件 3 相邻缺口，范围冻结）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - MAINT-1-RELEASE-MONITOR
base_commit: eebfedf6d
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/READER-PREF-PERSIST
allowed_paths:
  - doc/tasks/READER-PREF-PERSIST.md
  - doc/reviews/READER-PREF-PERSIST-*.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/READER-PREF-PERSIST/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/ReaderViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/Fluent/ReaderPageView.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
---

# READER-PREF-PERSIST：阅读偏好持久化闭环

## 来源与目标

**用户可见缺陷（E-4）**：阅读器里的「单页 / 双页」「反向翻页」「放大 / 缩小 / 适合页面」只改 ViewModel
内存状态，**没有任何 UI 控件调用 `SaveReadingPreferencesAsync`**（全仓生产路径 grep 零命中），
因此用户改完设置、重启或重开书后回到 Core 里的旧值 —— "改了却保存不下来"。

- 缺陷登记：`doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md` E-4。
- 既有能力（不需要新增契约）：`ReaderViewModel.SaveReadingPreferencesAsync`
  （`ReaderViewModel.cs:175`，已实现 partial patch：只发与 `_appliedPreferences` 不同的字段）；
  `ReaderViewModel.ApplyReadingPreferencesAsync`（`:146`，已由 `LoadAsync:273` 调用）；
  Host/Core 侧 `SaveReadingPreferences` / `GetReadingPreferences` 命令均已冻结存在。
- **一个可观察交付结果**：用户在阅读器里切换单双页、反转方向、调整缩放后，这些偏好**落库**；
  退出重进同一本书时按上次的设置呈现；保存失败时界面明确提示且不假装已保存。

## Acceptance Criteria

- [ ] **AC1 单双页持久化**：点击「单页 / 双页」后偏好落库；重开该书 `ApplyReadingPreferencesAsync`
      读回同一 `double_page` 值。
- [ ] **AC2 方向持久化**：点击「反向翻页」（工具栏与浮动工具条两处入口）后方向落库；重开读回一致。
- [ ] **AC3 缩放持久化**：放大/缩小/适合页面后 `zoom` 落库；重开读回一致。
- [ ] **AC4 判别测试**：断言控件路径确实产生了 `ReadingPreferencesPatch` 并交给 Host
      （`FakeHostController.LastSavedPreferences`），且**删除保存接入口后测试变红**。
- [ ] **AC5 失败可见**：保存返回 false 时给出可见文案，且不改写 `_appliedPreferences`
      （不得让失败的写入被当成已生效）。
- [ ] **AC6 不做过量写入**：连续操作（例如连点放大）不得产生等量的 wire 调用；
      须有合并/防抖策略，且该策略有测试或可复现的手工证据说明。
- [ ] **AC7 契约零变化**：不新增/修改 wire 命令、DTO、Core 代码；`generate_api_inventory.py --check`
      仍 `1/80/6=87`，`verify_pins.ps1` 18/18。
- [ ] **AC8 不回归**：`App.Tests` 全量 0 failed 且 skip 不增加；`ReaderVisibleControlsTests` /
      `ReaderReadingPreferencesTests` / `ShelfChapterReorderTests` 全绿。

## 允许修改范围

见 frontmatter `allowed_paths`。核心在 `ReaderPageView.cs`（控件回调接线）与
`ReaderViewModel.cs`（若需 async 包装或防抖）；`HostController.cs` 仅在确有必要时动（例如错误码）。

## 禁止范围

- **不得**新增或修改 wire 命令、DTO、Core/`src/**` 代码；偏好命令已冻结存在。
- **不得**改变偏好语义（字段含义、默认值、partial-patch 规则）。
- **不得**改动书签面板、整书进度、reset 确认的既有行为（已由 `MAINT-2-C1-BATCH-1` AC1 交付）。
- **不得**新增 skip/xfail 或放宽既有断言。
- 范围扩大须先由 DSH 登记。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2/AC3 | `.NET` 测试：控件操作 → `LastSavedPreferences` 断言 | `NewManga.App.Tests`（无夹具） | NOT_RUN | 无 |
| AC4 判别力 | 删掉保存接入口后重跑，断言变红（记录后还原） | 同上 | NOT_RUN | 无 |
| AC5 失败可见 | `.NET` 测试：`SaveReadingPreferencesResult=false` → 文案 + `_appliedPreferences` 不变 | 同上 | NOT_RUN | 无 |
| AC6 写入量 | 测试或手工：连点 N 次后 wire 调用次数 < N | 同上 | NOT_RUN | 无 |
| AC7 契约 | `python tools/generate_api_inventory.py --check`；`verify_pins.ps1` | 仓库根 | NOT_RUN | 无 |
| AC8 不回归 | `dotnet test tests/NewManga.App.Tests` | 仓库根 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- **硬依赖**：`MAINT-1-RELEASE-MONITOR`（伞形哨位）。
- **风险 R1**：`SaveReadingPreferencesAsync` 依赖 `_appliedPreferences` 做 diff；若保存失败后不回滚
  该快照，后续保存会以为"已经存过"而跳过。AC5 必须覆盖。
- **风险 R2**：缩放连续点击会产生多次调用；不做合并会打满 wire。AC6 要求有策略。
- **风险 R3**：`ReaderPageView` 的按钮回调是同步 `Action`，接入 async 保存需避免
  `async void` 吞异常（用 `_ = ...` 时必须把失败转成可见状态）。
- **环境**：真实 sidecar（2026-10-23）早于 `SaveReadingPreferences` 命令时，集成测试不可跑
  （见 E-2）；本卡默认用 `FakeHostController` 的无夹具测试，并在 NOT_RUN 时如实标注。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文）。
- 实际测试：尚无。
- 后续记录日期、commit、环境、结果、遗留项；最终由 DSH 填 `integration_commit` 并改 done。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | 待填 | NOT_APPLICABLE | — | — | 实现期按实际登记 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待填。
- 当前指针清理：待关闭时更新 STATUS / Plan / TASK_LEDGER / rolling checkpoint。
