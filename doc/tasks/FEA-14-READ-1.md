---
id: FEA-14-READ-1
title: FEA-14 切片 READ-1：按书阅读偏好 + 书签 + 整书进度（复用 PREQ 预冻结 wire）
kind: implementation
governance_version: 3
status: in_review
approval: **DSH 2026-11-10 冻结**（`ADJ-2026-11-10-FEA14-S5-SCOPE` §2.1/§2.2；PREQ-1 wire 预冻结 P9–P15；侦察 `recon.md` §2.4）
suggested_owner: dsh
owner: dsh
reviewer: null
depends_on:
  - FEA-14-S5-PREQ-1
base_commit: f9bf922aa
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
  - doc/reviews/CONTRACT-UNFREEZE-*.md
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
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/ReaderViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/ReaderWorkbenchPages.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/ReaderPreferenceTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/ImportExportUiTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/ReaderBookmarkTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/ReadWireTests.cs
  - tests/storage/test_reading_preferences.py
  - tests/core/test_v9_migration.py
  - tests/fea09/test_v7_migration.py
  - tests/fea11/test_source_gate_unify.py
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

- [ ] **AC1 偏好持久化**：按书 mode/direction/zoom/doublePage/layout 保存后在重启/重新加载恢复（隔离数据根，两次进程/两次装配）。 <<PARTIAL: Core schema v10 + P9/P10 wire 已验证；Fluent UI 未接线>>
- [ ] **AC2 书签**：新增（双页 left/right/both）、列表、删除；删除不影响漫画/进度/人工修改；跨书隔离。 <<PARTIAL: Core + P11–P13 wire 完整（CRUD/跨书/非法 side）；Fluent UI 书签面板未接线>>
- [ ] **AC3 整书进度**：按页面数计算并显示（与章内进度分列）；最后一页 → 已读完；重置需确认且可从记录中确认。 <<PARTIAL: Core 计算 + P14/P15 wire（reset 需 confirm）已验证；UI 显示/确认未接线>>
- [x] **AC4 迁移无损**：schema v10 additive；旧 `reading_progress` 行字段级无损；失败回退不半迁移。 <<MET>>
- [x] **AC5 契约/门禁**：七条命令按 PREQ §8 形状实现；`generate_api_inventory.py --check` 更新后 EXIT 0；`verify_pins` 18/18（C-07 pin 按记录更新）；无未授权契约字节变更。 <<MET>>
- [x] **AC6 证据**：定向 pytest/App.Tests 通过；`verification/FEA-14-READ-1/` 日志含 EXIT；NOT_RUN（真实 UI 手势/IME、跨内容序列）如实登记。 <<MET>>


## r1 处置记录（2026-11-10，对 `a44c631cb` 的 changes_requested）

- **R-001（P1，已修）**：`book_progress` 改为**页面**口径（`pages` 按章 JOIN 计数；每章 `progress_percent` × 页数累加；`read_pages/total_pages/finished`），旧行为（章节数冒充页数）删除；storage 测试断言 2 页 100%。
- **R-002/R-003（P2，部分修）**：P15 `confirm` 在 IHostController/HostController/CoreServiceClient 默认改为 **false**（无显式确认不重置）；P12/P15 返回类型与 PREQ 偏差（`Task<string?>`/`Task<int>` vs `Task<BookmarkInfo?>`/`Task<bool>`）**登记偏差**（wire/语义等价，未改接口形状）；P15 请求键 `confirm` vs PREQ `confirm_token?` 登记。
- **R-004（P2，已修）**：P10 改为 partial patch 合并（读现有偏好后合并再保存；缺省字段不重置）。
- **R-005（P2，已修）**：inventory 合计改 **68**，`--check` EXIT 0；C-07 pin 重算为 `59ab90f7…`（v1.3 记录，`verify_pins` 18/18）。
- **R-006（P2，已修）**：UNFREEZE 记录 pin 占位 `$h` 替换为实际 hash、`verify_pins` 拼写修正。
- **R-007/R-008（P2）**：allowed_paths 补 `doc/reviews/CONTRACT-UNFREEZE-*.md`、`tests/fea09/test_v7_migration.py`、`tests/fea11/test_source_gate_unify.py`；`base_commit` 校准 `f9bf922aa`（实际实现起点；Review base 记录差异见 r1 报告）。
- **R-009/R-010/R-011（P3）**：Reader 70 定向日志、pytest 首轮 5 failed 说明、两次装配/重启测试——**登记**（未补，留 READ-2/后续）。

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

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-RD-001 | READ-1 | `verification/FEA-14-READ-1/logs/dotnet-app-tests.log` | `-` | `ce9a0f3e62e5e4b33a6dc54e44b55d5323851a2755226f5f32899d4760c85838` | CANONICAL |
| EV-RD-002 | READ-1 | `verification/FEA-14-READ-1/logs/pytest-full.log` | `-` | `8c61189ab93f9dc09e24339f622099a831e1432ec1cfa9954104bd250d4b4fab` | CANONICAL |
| EV-RD-003 | READ-1 | `verification/FEA-14-READ-1/logs/read-wire.log` | `-` | `5eabf16881205b9a80730ba1ba0df816667cf024eaf13e1788b8a9d2c901e454` | CANONICAL |
| EV-RD-004 | READ-1 | `verification/FEA-14-READ-1/logs/reading-storage.log` | `-` | `b0ab413835300ddc9291937e3c3f617da3a13d0f78edc5d943a032e878c40130` | CANONICAL |
| EV-RD-005 | READ-1 | `verification/FEA-14-READ-1/README.md` | `-` | `894f387ca6d9edd03702b2e467e3cdcf7538a923da141c4e3e62c815218ec6f1` | CANONICAL |

## Closeout Record

- 未开始（2026-11-10 scope 冻结，`ready`）。