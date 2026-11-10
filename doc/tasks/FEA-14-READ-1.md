---
id: FEA-14-READ-1
title: FEA-14 切片 READ-1：按书阅读偏好 + 书签 + 整书进度（复用 PREQ 预冻结 wire）
kind: implementation
governance_version: 3
status: ready
approval: **DSH 2026-11-10 冻结**（`ADJ-2026-11-10-FEA14-S5-SCOPE` §2.1/§2.2；PREQ-1 wire 预冻结 P9–P15；侦察 `recon.md` §2.4）
suggested_owner: dsh
owner: dsh
reviewer: null
depends_on:
  - FEA-14-S5-PREQ-1
base_commit: e6964bf58
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-14-READ-1
allowed_paths:
  - doc/tasks/FEA-14-READ-1.md
  - doc/reviews/FEA-14-READ-1-*.md
  - doc/handoffs/FEA-14-READ-1-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/FEA-14-READ-1/**
  - doc/plan/FEA-C07_API_INVENTORY.md
  - doc/plan/FEA-CONTRACT-FROZEN-C07.md
  - src/application/reading/service.py
  - src/application/reading/ports.py
  - src/infrastructure/sqlite/schema.py
  - src/infrastructure/sqlite/reading_export.py
  - src/bootstrap/core_assembly.py
  - src/bootstrap/core_service.py
  - apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/ReadCommands.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/ReaderViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/ReaderWorkbenchPages.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/ReaderPreferenceTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/ReaderBookmarkTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/ReadWireTests.cs
  - tests/storage/test_reading_preferences.py
  - tests/core/test_v9_migration.py
  - tests/core/test_read_wire.py
out_of_scope:
  - 不改冻结契约字节（C-07 的 pin 按实现落地更新并记录；不改 C-02/C-03/P15 等）
  - 不实现跨内容连续序列（READ-2，等 LIB 阅读顺序定型）
  - 不实现 OCR 文本搜索（仅诚实空态）
  - 不修改 FEA-15 正式验收声明
---

# FEA-14-READ-1：阅读偏好 + 书签 + 整书进度

## 背景（PREQ 预冻结 wire P9–P15）

`FEA-14-S5-PREQ-1` 已预冻结 READ 命令面：`GetReadingPreferencesAsync` / `SaveReadingPreferencesAsync` / `ListBookmarksAsync` / `CreateBookmarkAsync` / `DeleteBookmarkAsync` / `GetBookReadingProgressAsync` / `ResetReadingProgressAsync`（Host id `reader_*`，minor 3，payload 形状见 `FEA-14-S5-PREQ-1-wire-r1.md` §8）。DDL v10 计划：`reading_preferences`、`reading_bookmarks`、`reading_progress` additive 列（PREQ AC5 计划）。

## Scope 冻结（2026-11-10，DSH）

1. Core：reading preferences/bookmarks service + schema v10 additive migration；book progress 按页面数计算；reset 需 confirm 语义。
2. Host：实现 P9–P15 七条命令（additive；旧签名不变），按 C-07 冻结记录流程更新 inventory 并重算 pin。
3. App：Reader VM/页面使用偏好（重启恢复）；书签新增/删除/列表；整书进度显示；重置需确认。
4. 零产品行为回归：旧 `reading_progress` 行无损迁移；真实用户数据不触碰（测试隔离）。
5. 证据：pytest 定向/全量、App.Tests 定向、`check.ps1`、pins、API inventory。

## Acceptance Criteria

- [ ] **AC1 偏好持久化**：按书 mode/direction/zoom/doublePage/layout 保存后在重启/重新加载恢复（隔离数据根，两次进程/两次装配）。
- [ ] **AC2 书签**：新增（双页 left/right/both）、列表、删除；删除不影响漫画/进度/人工修改；跨书隔离。
- [ ] **AC3 整书进度**：按页面数计算并显示（与章内进度分列）；最后一页 → 已读完；重置需确认且可从记录中确认。
- [ ] **AC4 迁移无损**：schema v10 additive；旧 `reading_progress` 行字段级无损；失败回退不半迁移。
- [ ] **AC5 契约/门禁**：七条命令按 PREQ §8 形状实现；`generate_api_inventory.py --check` 更新后 EXIT 0；`verify_pins` 18/18（C-07 pin 按记录更新）；无未授权契约字节变更。
- [ ] **AC6 证据**：定向 pytest/App.Tests 通过；`verification/FEA-14-READ-1/` 日志含 EXIT；NOT_RUN（真实 UI 手势/IME、跨内容序列）如实登记。

## 证据计划（L2）

`verification/FEA-14-READ-1/`：`logs/`（pytest 定向/全量、App.Tests 定向、门禁、API inventory、pins）、迁移前后行数/字段表、JSON 摘要、NOT_RUN、复现命令。

## 风险与回退

| 风险 | 处置 |
|---|---|
| 迁移触碰用户进度 | pre_migration 备份 + 失败即停 + 隔离根测试；旧行字段比对 |
| 新命令未按 PREQ 形状 | 以 wire-r1 §8 为基线；偏差须记录并回改 |
| C-07 pin 变更复核成本 | 单次 UNFREEZE 已由 PREQ 授权名单；实现卡只做落地更新与 pin 重算 |
| 真实 UI 手势不可测 | NOT_RUN 登记，不冒充 PASS |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| temp | `G:\CODEX\New Manga.workspace\FEA-14-READ-1\`（隔离数据根/迁移副本） | NOT_APPLICABLE | — | — | 仓外，不提交 |
| user-data | `%APPDATA%\com.newmanga.desktop` | NOT_APPLICABLE | — | — | 只读指纹（测试用隔离根） |
| build | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 复用现有 .NET / Python 环境 |
| worktree | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 主树实现 |

## Closeout Record

- 未开始（2026-11-10 scope 冻结，`ready`）。
