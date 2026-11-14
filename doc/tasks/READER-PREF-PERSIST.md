---
id: READER-PREF-PERSIST
title: 阅读偏好持久化闭环（单双页/方向/缩放接到 SaveReadingPreferences）
kind: implementation
governance_version: 3
status: done
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
integration_commit: 6afab416bf845ce8481b20bae90687fcf2852d7e
delivery_head: 6afab416b
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1 单双页持久化**：点击「单页 / 双页」后偏好落库；重开该书 `ApplyReadingPreferencesAsync`
      读回同一 `double_page` 值。
- [x] **AC2 方向持久化**：点击「反向翻页」（工具栏与浮动工具条两处入口）后方向落库；重开读回一致。
- [x] **AC3 缩放持久化**：放大/缩小/适合页面后 `zoom` 落库；重开读回一致。
- [x] **AC4 判别测试**：断言控件路径确实产生了 `ReadingPreferencesPatch` 并交给 Host
      （`FakeHostController.LastSavedPreferences`），且**删除保存接入口后测试变红**。
- [x] **AC5 失败可见**：保存返回 false 时给出可见文案，且不改写 `_appliedPreferences`
      （不得让失败的写入被当成已生效）。
- [x] **AC6 不做过量写入**：连续操作（例如连点放大）不得产生等量的 wire 调用；
      须有合并/防抖策略，且该策略有测试或可复现的手工证据说明。
- [x] **AC7 契约零变化**：不新增/修改 wire 命令、DTO、Core 代码；`generate_api_inventory.py --check`
      仍 `1/80/6=87`，`verify_pins.ps1` 18/18。
- [x] **AC8 不回归**：`App.Tests` 全量 0 failed 且 skip 不增加；`ReaderVisibleControlsTests` /
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
| AC1/AC2/AC3（VM） | `dotnet test --filter ReaderPreferencePersistenceTests` | 无夹具 | **8 passed** | `verification/READER-PREF-PERSIST/README.md` §4/§7 |
| AC4（View 接线） | `dotnet test --filter ReaderPreferenceWiringTests` | Avalonia headless | **4 passed**；回退按钮接线后实测变红 | 同上 §7 |
| AC5 失败可见 | 同上 VM 套件 | 无夹具 | **2 passed** | 同上 |
| AC6 写入量 | `RapidZoomClicks_CoalesceIntoFewWrites` | 无夹具 | **PASS**（6 连点 → `InRange(1,2)`） | 同上 |
| AC7 契约 | `generate_api_inventory.py --check`；`verify_pins.ps1` | 仓库根 | **PASS**（`1/80/6=87`；18/18） | `four-pieces.log` |
| AC8 不回归 | `dotnet test tests/NewManga.App.Tests` | 无夹具 | **946 / 0 / 11**（本卡前 940/0/11，skip 未增加） | `regression.log` |

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

AC1–AC3 的"重开读回"半边因 E-2（sidecar 过期）为 `NOT_RUN`，下列证据只覆盖已实际执行的部分。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|
| EV-RPP-01 | AC1/AC2/AC3/AC5/AC6 与缺陷事实 | verification/READER-PREF-PERSIST/README.md | 6afab416b | ad16f5153c3798803e105903dbe9ab5a8f1492f10b199e67326fb9a87fea64c8 | CANONICAL | BLOB |
| EV-RPP-02 | AC8 回归 | verification/READER-PREF-PERSIST/regression.log | 6afab416b | a6d2c260d8e387685e0d1b75a0f31ebb0daec000b8c291930d1a7cea73c7c8c1 | CANONICAL | BLOB |
| EV-RPP-03 | AC1/AC5/AC6 VM 与竞态测试 | apps/desktop-avalonia/tests/NewManga.App.Tests/ReaderPreferencePersistenceTests.cs | 6afab416b | 393bae08a85e6281a0a30b7b50515d2f74a7073aa5c3698b82b73d91f6664b14 | CANONICAL | BLOB |
| EV-RPP-04 | AC4 View 级接线测试 | apps/desktop-avalonia/tests/NewManga.App.Tests/ReaderPreferenceWiringTests.cs | 6afab416b | 7a232882d52bbd6d073b8f3ea1d9388d2758776444fbe699868562ed35ca966e | CANONICAL | BLOB |
| EV-RPP-05 | 实现（意图捕获 + 快照语义） | apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/ReaderViewModel.cs | 6afab416b | 3bab1c98e023f4e9e2eaa0679c7f582549db78b55d0ca3b9b9b983c34506e0f4 | CANONICAL | BLOB |
| EV-RPP-06 | r1 复核（REJECT） | doc/reviews/READER-PREF-PERSIST-review-r1.md | 6afab416b | d378c7ff33c673443e0316f6559f4d5d3f3b8cc4d0cb5856b43a759aa5f56e2f | CANONICAL | BLOB |
| EV-RPP-07 | r2 复核（ACCEPT_WITH_LIMITATIONS） | doc/reviews/READER-PREF-PERSIST-review-r2.md | 6afab416b | f8d9fc770740451905bca72e0e7559eddcc292b1b9d7b7617f21280f98a380e2 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | 待填 | NOT_APPLICABLE | — | — | 实现期按实际登记 |

## Closeout Record

- Closeout date / DSH：2026-11-15，DSH（Lead / Architect / Integrator）。
- canonical_evidence_status：`complete`（7 条 BLOB pin，commit `6afab416bf845ce8481b20bae90687fcf2852d7e`）。
- resource_closeout_status：`complete`（无 worktree、无用户数据）。
- 删除、迁移、归档数量/字节数：0。
- 未关闭项及保留原因：
  - **AC1–AC3 的"重开读回"半边 `NOT_RUN`**：本卡证明"控件路径发出了正确的 patch"与"失败不记账"，
    但没有真实 sidecar 做"保存→重启→读回"闭环（E-2：仓库 sidecar 2026-10-23 早于
    `SaveReadingPreferences`；重建需 PyInstaller，本环境 PyPI 不可达）；
  - `DoubleTapped` 与键盘 `+`/`-`/`0` 入口已接线但只有静态核对，无 View 级测试；
  - `_pendingPreferenceIntent` 为单槽：合并窗口内若对两本书都改动，只保证最后一次；
  - 离开阅读器无显式 flush，依赖 80ms 合并窗口内的保存。
- 当前指针清理：STATUS / Plan / TASK_LEDGER / rolling checkpoint 已更新。
- **本卡自身的错误登记**：
  1. 首版（`57f149b02`）在 `_appliedPreferences` 用 await **之后**的当前值写快照，导致"在途改值"永久丢更新
     —— 由 r1 复核 P1-1 实测发现，r2 修复；
  2. 首版 AC4 的测试只调 VM，把 `ReaderPageView` 整体回退到基线仍 17/17 全绿（生产接线零覆盖）
     —— 由 r1 复核 P1-2 实测发现，r2 补 View 级测试；
  3. 首版提交后又留下 4 个未提交文件，复审看到不一致中间态 —— 由 r1 复核 P1-3 指出，已改为单一提交；
  4. r2 后仍残留"意图未带 diff 基线"的漏写窗口（80ms 内切到快照相等的书 → 0 写入）—— r2 复核 P2-1 实测发现，本轮修复。
- **资源**：`G:\CODEX\New Manga.workspace\task-envs\CHAPTER-MANUAL-SORT\hash2.py` 等派生物属前序会话；
  本卡无新增资源。
