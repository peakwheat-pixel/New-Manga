---
id: FEA-14-EDIT-1
title: FEA-14 切片 EDIT-1：问题标记（复用 PREQ 预冻结 wire P16–P20）
kind: implementation
governance_version: 3
status: in_review
approval: **DSH 2026-11-10 冻结**（`ADJ-2026-11-10-FEA14-S5-SCOPE` §2.1/§2.2；PREQ-1 wire 预冻结 EDIT P16–P20；DDL v10 计划 §2.3）
suggested_owner: dsh
owner: dsh
reviewer: null
depends_on:
  - FEA-14-S5-PREQ-1
base_commit: 68a9e2e74
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-14-EDIT-1
allowed_paths:
  - doc/tasks/FEA-14-EDIT-1.md
  - doc/reviews/FEA-14-EDIT-1-*.md
  - doc/handoffs/FEA-14-EDIT-1-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/plan/FEA-C07_API_INVENTORY.md
  - doc/plan/FEA-CONTRACT-FROZEN-C07.md
  - doc/reviews/CONTRACT-UNFREEZE-*.md
  - verification/FEA-14-EDIT-1/**
  - src/domain/editing/**
  - src/application/editing/**
  - src/infrastructure/sqlite/issue_markers.py
  - src/infrastructure/sqlite/schema.py
  - src/bootstrap/core_assembly.py
  - src/bootstrap/core_service.py
  - apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/IssueMarkerPortTests.cs
  - tests/storage/test_issue_markers.py
  - tests/core/test_issue_marker_wire.py
  - tests/storage/test_fonts.py
  - tests/storage/test_upgrade_schema_data.py
  - tests/fea09/test_v7_migration.py
  - tests/fea11/test_source_gate_unify.py
out_of_scope:
  - 不做批量解决/批量删除命令（PREQ：批量由 UI 循环或后续批量命令）
  - 不做标记列表分页/跨书聚合/时间范围过滤（P16 仅 `book_id,state?`）
  - 不做 EDIT-2/EDIT-3 的多选动作与受控样式重渲染（复用既有 Draft 端口，另卡）
  - 不改冻结契约字节（C-07 统计/成员表按实现落地更新，pin 重算须记录）
  - 不修改 FEA-15 正式验收声明
  - 标记不是受保护内容：删除标记物理删除且不触碰漫画/页/进度/人工修改（ADJ-001 不适用）
---

# FEA-14-EDIT-1：问题标记

## 背景（PREQ 预冻结 wire P16–P20）

FEA-14 S5 EDIT 切片需要「问题标记」数据面：列出/新建/解决/重开/删除整页或位置标记（PREQ §5/§8 P16–P20，minor 3）。现有编辑域只有 Draft/Region 渲染能力，无问题标记实体与持久化。侦察确认无既有 `issue_markers` 表/服务，DDL v10 计划 §2.3 已给出目标表形状。

## Scope 冻结（2026-11-10，DSH）

1. Core 数据面：schema **v13** additive 新表 `issue_markers`（`marker_id` PK、`book_id`、`chapter_id`、`page_id`、`position_x/position_y`（可空，整页标记为空）、`kind`、`note`（可空）、`state`（open/resolved）、`created_at`、`resolved_at`（可空））+ 索引 `(book_id, state)`、`(page_id)`；v1–v12 迁移字节不变。
2. 领域/服务：`IssueMarkerService`（列标记：默认 `state=open`，可按 `state` 过滤；新建：校验书/章/页归属与位置成对；解决/重开：状态迁移幂等；删除：物理删除，不影响漫画/页/进度/人工修改）。
3. wire：P16–P20 按 PREQ §8 形状（`book_id,state?` / `book_id,chapter_id,page_id,position?,kind,note?` / `marker_id`）；错误一律 typed（`TARGET_NOT_FOUND/not_found`、`INVALID_REQUEST/validation`）。
4. Host：`IHostController` +5 方法（additive，旧签名不变）+ DTO（`IssueMarkerInfo`/`IssueMarkerPosition`）+ HostRuntime/CoreServiceClient/HostController/NullHostController/Fake。
5. 契约：按 C-07 冻结记录流程 UNFREEZE 统计（`IHostController` 69→74、合计 76→81）并把 P16–P20 并入正式成员表、重算 pin。
6. 证据：定向 pytest、v13 回归、App.Tests、`check.ps1`/`verify_pins`/API inventory、v1–v12 迁移字节比对。

## 裁决（PREQ 歧义，DSH 2026-11-10）

- PREQ §8 P16/P17 的 `position?` 未给形状：裁决为**相对页面坐标对象** `{"x": number, "y": number}`（0–1 相对值，须成对出现；整页标记省略 `position`）。键名与可选性不变，属形状细化，不改 PREQ 键集。
- `state` 取值 `open`/`resolved`；P16 缺省 `open`，`state="resolved"` 返回已解决；其他值 → `INVALID_REQUEST`。
- `kind` 为自由短字符串（UI 预置集合留 EDIT-2），空串拒绝；`note` 可空。
- 删除为**物理删除**：标记是用户工作产物而非受保护内容，ADJ-001 的彻底删除披露不适用；删除只影响标记行。

## Acceptance Criteria

- [x] **AC1 数据面/v13**：`issue_markers` additive 建表 + 两索引 + 位置成对/0–1 的 DB CHECK；v1–v12 迁移 NAME/SQL 逐字节不变；旧库升级行级无损；repository 五路径（insert/get/list/update/delete）一致。 <<MET>>
- [x] **AC2 P16 列表**：按 `book_id` + 可选 `state` 列标记；默认仅 open；排序稳定（`created_at` + `marker_id`）；响应含 PREQ 字段（`position` 仅位置标记出现、`resolved_at` 仅已解决出现）。 <<MET>>
- [x] **AC3 P17 新建**：校验书/章/页存在且归属一致；`position` 成对且 0–1（bool/字符串/越界拒绝）；成功返回 `marker_id` 且 `state=open`、`created_at` 有值。 <<MET>>
- [x] **AC4 P18–P20 状态/删除**：resolve/reopen 状态迁移与 `resolved_at` 语义（重复操作幂等）；delete 物理删除后不可见、不影响书/章/页/其他数据。 <<MET>>
- [x] **AC5 契约/门禁**：C-07 UNFREEZE **v1.7**（74/81）成员表逐行 = 脚本 stdout（`ALL_MATCH: True`）、pin `bb775912…`；`--check` EXIT 0；`verify_pins` 18/18。 <<MET>>
- [x] **AC6 证据**：定向 pytest/回归/App.Tests 通过；`verification/FEA-14-EDIT-1/` 日志含 EXIT；NOT_RUN 如实登记。 <<MET>>

## 实现说明（2026-11-10）

- **wire 形状**：P16 `book_id,state?` → `markers[{marker_id,chapter_id,page_id,position?,kind,note,state,created_at,resolved_at?}]`；P17 `book_id,chapter_id,page_id,kind,note?,position?` → `marker_id`；P18/19/20 `marker_id` → `resolved/reopened/deleted=true`。`position` 为 `{"x":number,"y":number}`（0–1 相对坐标，成对），空/半对/越界/bool → `INVALID_REQUEST`。
- **typed 错误**：书/章/页/标记不存在（含章不属于书、页不属于章、undefined 状态）→ `TARGET_NOT_FOUND/not_found`；字段形状/类型/位置→ `INVALID_REQUEST/validation`。无 `UNKNOWN/internal` 逃逸路径（service 只抛 `IssueMarkerError`）。
- **数据面**：schema **v13** 仅新增 `issue_markers` 表 + `idx_issue_markers_book_state`/`idx_issue_markers_page`；表级 CHECK 保证位置成对且 0–1；v1–v12 迁移字节不变。
- **删除语义**：标记是用户工作产物、非受保护内容（ADJ-001 不适用），P20 物理删行；测试断言书/章/页行数不变。
- **C-07**：UNFREEZE v1.7（69→74 / 76→81），成员表按脚本 stdout 重建（74+4 行），S5 计划节只剩 AI-1 P21–P25；pin `bb775912…`。
- **Host**：`IHostController` 5 方法 + DTO（`IssueMarkerInfo`/`IssueMarkerPosition`）在 HostController/NullHostController/HostRuntime/CoreServiceClient/Fake 六处一致；NullHost 降级返回空/false/null 不抛。

## 证据计划（L2）

`verification/FEA-14-EDIT-1/`：`logs/`（pytest 定向/全量、App.Tests、pins/api、v13 回归）、NOT_RUN、复现命令。

## 风险与回退

| 风险 | 处置 |
|---|---|
| 标记误删漫画/页/进度 | 标记表独立；删除只删标记行；测试断言其他表不变 |
| 无效归属（章/页不属于书） | 创建前校验归属，typed 拒绝 |
| 迁移风险 | v13 additive + pre_migration 备份 + 失败即停 |
| 旧行无损 | v13 只加新表 + 索引；升级前后业务行 count 对比 |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| temp | `G:\CODEX\New Manga.workspace\FEA-14-EDIT-1\`（隔离数据根） | NOT_APPLICABLE | — | — | 仓外，不提交 |
| user-data | `%APPDATA%\com.newmanga.desktop` | NOT_APPLICABLE | — | — | 只读；测试用隔离根 |
| build | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 复用现有环境 |
| worktree | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 主树实现 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-ED-001 | EDIT-1 | `verification/FEA-14-EDIT-1/logs/dotnet-app-tests.log` | `-` | `3ef45722b341164fafdf50570c025f197d58a22163119bbcbdb380e52bf6093d` | CANONICAL |
| EV-ED-002 | EDIT-1 | `verification/FEA-14-EDIT-1/logs/pins-api.log` | `-` | `0068c8348a18b0f7a4ebfe2a95acb6c9d8543d02e5e60aafd87917133a0872ee` | CANONICAL |
| EV-ED-003 | EDIT-1 | `verification/FEA-14-EDIT-1/logs/pytest-edit.log` | `-` | `fe154f3c3011d909e19e2c6d733562fc983ad8f390878cfe4e365ff04b1d32c1` | CANONICAL |
| EV-ED-004 | EDIT-1 | `verification/FEA-14-EDIT-1/logs/regression-v13.log` | `-` | `c6de17db08c49b950de1747cab26d0d85006adf4853b4ea575d07d0ef8d7dc17` | CANONICAL |
| EV-ED-005 | EDIT-1 | `verification/FEA-14-EDIT-1/README.md` | `-` | `713a19f60851638e651c92f6d7b477b26881b6074ae7829788ac8e50518576b1` | CANONICAL |

## Closeout Record

- 2026-11-10 scope 冻结（`ready`）→ 实现（schema v13 + `IssueMarkerService` + wire P16–P20 + Host 六处 + C-07 v1.7）→ **r1 独立复核待派发**。未 push。
