---
id: CHAPTER-MANUAL-SORT
title: 章节手动排序闭环（书架拖拽 + 原子持久化 + 缓存失效）
kind: implementation
governance_version: 3
status: in_progress
disposition: "codex 外部裁决 A（2026-11-14）落地；L-L1-2 排序 UI 范围由 C3-3 OUT 提升为本卡；DSH 2026-11-14 释放"
approval: codex 裁决 A + DSH 写入方案裁决 2026-11-14
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - MAINT-1-RELEASE-MONITOR
base_commit: 79606ea4a
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/CHAPTER-MANUAL-SORT
allowed_paths:
  - doc/tasks/CHAPTER-MANUAL-SORT.md
  - doc/reviews/CHAPTER-MANUAL-SORT-*.md
  - doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - doc/TASK_LEDGER.md
  - verification/CHAPTER-MANUAL-SORT/**
  - src/application/library/service.py
  - src/application/library/ports.py
  - src/infrastructure/sqlite/library.py
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/ShelfViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/Fluent/ShelfPageView.cs
  - tests/**
  - apps/desktop-avalonia/tests/**
---

# CHAPTER-MANUAL-SORT：章节手动排序闭环

## 来源与目标

**用户可见缺陷**：用户在书架的章节列表里无法调整章节顺序；已有排序能力没有可见入口。

- codex 裁决 A（`doc/reviews/MAINT-1-EXTERNAL-ADJUDICATION-codex-2026-11-14.md` §裁决 A）：选**手动拖拽排序**；开 1 张卡，含拖拽、持久化、重启回读、空值/重复/新增、失败及并发保护。
- finding `L-L1-2`（`doc/reviews/MAINT-1-LIMITATION-DISPOSITION-MATRIX-2026-11-14.md:40`）：`custom_rank` write-only、P6 排序未实现；拆分为 `IMPL`（读回闭环，**已完成**）+ `C3`（排序 UI，属 `C3-3` OUT 范围）。本卡承接被提升为优先项的"排序 UI"部分。

**一个可观察交付结果**：在书架选中一部作品后，用户可用鼠标拖拽章节调整顺序；松手后顺序立即生效并落库，重启应用后回读仍为新顺序；写入失败时顺序回滚且界面明确报错，绝不显示未落库的顺序。

## 前置事实核实（codex 点名三项，开卡前实测）

| # | 核实项 | 结论 | 证据 |
|---|---|---|---|
| 1 | 写接口与事务边界 | `ReorderChapters` wire 命令**已冻结并全链路存在**；它经 `reorder_chapters_strict` → `reorder_chapters` 写 `sort_order`，后者是**逐章 `update_chapter` 循环，每次独立事务（无原子性）**。`custom_rank` 只有逐章 `UpdateChapterMetadata`，无批量写。 | `src/application/library/service.py:212-224`、`:317-323`；`src/infrastructure/sqlite/library.py:249-263`（`with self._conn`）；`src/bootstrap/core_service.py:5170-5184` |
| 2 | 并发行为 | 无版本号/乐观锁。`reorder_chapters_strict` 仅在**提交时**校验"全覆盖 + 无重复"，故窗口内章节集合变化会以 `INVALID_REQUEST` 失败（fail-safe）；两端同时拖拽为 last-write-wins。 | `src/application/library/service.py:317-323`；`core_service.py:5178-5183` |
| 3 | 书架缓存刷新 | `HostController.ListChaptersAsync` 按书缓存一次，**仅 `CreateChapterAsync` 失效**。若不新增失效点，拖拽后重载会读旧序 → 假成功。 | `apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs:924-942` |

**补充事实**：`sort_order` 就是既有的"显示/阅读顺序"字段 —— `Chapter.reorder()` 注释 "User reordering touches sort_order only; import_order is frozen"（`src/domain/books/entities.py:164-167`）；`create_chapter` 注释 "sort_order is the display/read order and must stay unique"，并按 `max(sort_order)+1` 追加（`service.py:167-171`），故**新增章节天然排在末尾**。`custom_rank` 在当前代码中无任何消费端（UI 全仓仅 `CoreServiceClient` 解析，无读取用于排序）。

## DSH 写入方案裁决

**复用已冻结的 `ReorderChapters` 写 `sort_order`；不为拖拽新增 `custom_rank` 写路径。** 依据 codex 裁决 A 的授权原文"DSH 先确认写入方案及是否需要契约载体，再冻结范围并释放"。

1. `sort_order` 是既有用户排序字段，`ReorderChapters` 是其唯一已冻结写接口，全链路（Core→CoreClient→Host→IHostController）已存在，本卡只缺 UI 与缓存失效。
2. **零 UNFREEZE、零 DTO 扩展、零 wire 命令新增**：`ListChapters` 返回顺序天然 = `sort_order` = 用户顺序，满足 codex "wire 返回顺序冻结为 `sort_order`"。
3. 拖拽直接改 `sort_order` ⇒ 不存在"混合有/无 rank"状态；codex 的 rank 混合排序规则（有 rank 者在前、按 rank 升序、`chapter id` tie-break）在本方案下**不适用**，而非"未实现"。

**偏离登记（不得淡化）**：codex 裁决 A 的字面假设是拖拽写 `custom_rank` 并在消费层做 rank 混合排序。该假设基于"C1-5 读回尚未完成"的旧认知与"需另建批量原子重排命令"的推测；实际 C1-5 已由 `MAINT-2-C1-BATCH-1` AC5 完成（`closed_with_limitations`），且 `ReorderChapters` 命令早已存在。本卡据授权改走 `sort_order`，属**方案偏离但满足裁决意图**（用户手动顺序真正生效、wire 顺序不变、失败不假装成功）。`custom_rank` 保持现状、不新增消费端，在本卡作为已知限制登记，不声称"已实现自定义排序语义"。

## Acceptance Criteria

- [ ] **AC1 原子持久化**：`reorder_chapters` 在同一 SQLite 事务内完成整书 `sort_order` 重写；任何一步失败则全部回滚，DB 中不存在"部分章节已改序"的中间状态。
- [ ] **AC2 判别测试（原子性）**：构造中途失败（注入 `update_chapter` 抛错），断言事务回滚后**全部**章节 `sort_order` 与调用前一致。把实现回退成逐章独立事务后，该测试必须变红。
- [ ] **AC3 缓存失效**：`HostController.ReorderChaptersAsync` 成功返回后，同一 `bookId` 的 `ListChaptersAsync` 必须返回新顺序（不得命中重排前的缓存条目）。
- [ ] **AC4 VM 拖拽语义**：`ShelfViewModel.MoveChapterAsync(fromIndex, toIndex)` 计算目标顺序并调用 `IHostController.ReorderChaptersAsync`；成功则 `Chapters` 集合按结果重排且 `SelectedChapter` 保持在原选中章节；失败则集合顺序**不变**并给出可见错误文案；越界索引不发起调用。
- [ ] **AC5 视图拖拽手势**：书架章节列表支持鼠标拖拽重排（拖拽超过阈值才触发，单击仍为选中章节），拖放结束调用 `MoveChapterAsync`。
- [ ] **AC6 契约零变化**：`ListChapters` 仍按 `sort_order` 返回；wire 命令、字段、DTO 与 `M2-C1`/`C-07` 字节不变（`generate_api_inventory.py --check` 仍 `1/80/6=87`；`verify_pins.ps1` 18/18）。
- [ ] **AC7 新增章节排末尾**：在已有手动顺序的书中新增章节后，新章节位于列表末尾（固定既有 `max+1` 行为，防回归）。
- [ ] **AC8 失败与刷新不假装成功**：重排失败、并发冲突（`INVALID_REQUEST`）或刷新后，UI 不得显示未落库的顺序；错误路径有可见文案。
- [ ] **AC9 并发保护**：同一实例内的重入拖拽（前一次 in-flight 未完成）不得产生交叠写入；被拒绝/失败时 UI 保持已落库顺序。
- [ ] **AC10 不回归**：`App.Tests`、`CoreClient.Tests` 与 Python 相关测试全绿；无新增 skip/xfail、无放宽既有断言。

## 允许修改范围

见 frontmatter `allowed_paths`。要点：

- Core 端：`reorder_chapters` 的事务化（可新增 repo 批量方法或 service 层事务包装）；`ports.py` 如需扩展 port 须同批。
- Host 端：`HostController.ReorderChaptersAsync` 成功后失效对应 `bookId` 缓存。
- UI 端：`ShelfViewModel` 新增 `MoveChapterAsync` 与 in-flight 守卫；`ShelfPageView` 章节列表加拖拽手势。
- 测试与 `verification/CHAPTER-MANUAL-SORT/**`。

## 禁止范围

- **不得**修改 wire 协议/命令/字段/DTO（`M2-C1`、`C-07`）；**不得**改变 `ListChapters` 返回顺序。
- **不得**为拖拽新增或修改 `custom_rank` 的任何写/读/消费路径。
- **不得**修改 `import_order` 语义；**不得**改阅读器章节导航的独立顺序。
- **不得**触碰用户源文件、`Lock`、current/pinned `Revision`；本期不涉及删除路径。
- **不得**新增 skip/xfail、放宽既有断言或降级四件套。
- 范围扩大须先由 DSH 登记并在 PLAN 复评。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 原子性 | `pytest tests/storage/test_chapter_reorder_atomic.py` | Python 3.14 / tmp SQLite | **PASS 5/5** | `verification/CHAPTER-MANUAL-SORT/README.md` §4 |
| AC2 判别力 | 临时回退为逐章事务后重跑，断言变红（记录后还原） | 同上 | **PASS（已实测变红）** | 同上 §5 |
| AC3 缓存失效 | `.NET` 测试：`HostController` 重排后 `ListChaptersAsync` 返回新序 | 需认识 `ReorderChapters` 的 sidecar | **NOT_RUN**：仓库 sidecar 构建于 2026-10-23，命令自 `83e45cfe5`（2026-11-10）才有；重建需 PyInstaller，本环境 PyPI 不可达 | `pending-host-cache-test.cs.txt`（待启用判别测试） |
| AC4/AC9 VM | `dotnet test --filter ShelfChapterReorderTests` | `NewManga.App.Tests` | **PASS 8/8** | `ShelfChapterReorderTests.cs` |
| AC5 手势 | 手工：书架选中作品→拖拽章节→松手→顺序变化 | 真实 GUI | **NOT_RUN**（仅编译级验证；无真机拖拽证据） | — |
| AC6 契约 | `python tools/generate_api_inventory.py --check`；`verify_pins.ps1` | 仓库根 | **PASS**（inventory `1/80/6=87`；pins 18/18） | `four-pieces.log` |
| AC7 新增末尾 | Python 用例：拖拽后新增章节 | tmp SQLite | **PASS** | `test_chapter_created_after_manual_reorder_lands_at_the_end` |
| AC10 不回归 | Python 全量 + `dotnet test` 三项目 | 仓库根 | 见 §7 结论 | `regression.log` |

## 依赖、风险与阻塞

- **硬依赖**：`MAINT-1-RELEASE-MONITOR`（伞形哨位）。
- **风险 R1**：`reorder_chapters` 事务化会改变既有调用方假设；须核 `reorder_chapters_strict` 的唯一调用方（wire handler）与测试库 `tests/library/helpers.py` 的 fake repo 是否实现新方法。
- **风险 R2**：章节项当前是 `Button`，加拖拽易回归"单击选中章节"。须用位移阈值区分，并有测试/手工证据。
- **风险 R3**：并发为 last-write-wins（无乐观锁）。本卡只做同实例 in-flight 守卫与失败可见性，不做跨实例版本协商；该限制在卡面登记，不声称已解决多端并发。
- **风险 R4**：`custom_rank` 仍无消费端。若后续要求 rank 语义，须另开卡并评估与 `sort_order` 的双写一致性。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文，不得由实现会话自审）。
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
- 未关闭项及保留原因：`custom_rank` 无消费端（R4）；跨实例并发不解决（R3）。
- 当前指针清理：待关闭时更新 STATUS / Plan / rolling checkpoint。
