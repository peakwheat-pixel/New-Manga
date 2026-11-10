---
id: FEA-14-EXPORT-1
title: FEA-14 切片 EXPORT-1：导出范围/顺序预览/同名冲突默认不覆盖/取消保留成功文件
kind: implementation
governance_version: 3
status: in_review
approval: **DSH 2026-11-10 冻结**（依据 `ADJ-2026-11-10-FEA14-S5-SCOPE` §2.1/§2.2 与 PREQ 共用 wire 口径；FEA-00 §12.2/§15.6 EXPORT 切片；只读侦察 `recon.md` §2.7）
suggested_owner: dsh
owner: dsh
reviewer: null
depends_on:
  - FEA-14-S5-PREQ-1
base_commit: 5459c9220
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-14-EXPORT-1
allowed_paths:
  - doc/tasks/FEA-14-EXPORT-1.md
  - doc/reviews/FEA-14-EXPORT-1-*.md
  - doc/handoffs/FEA-14-EXPORT-1-*.md
  - verification/FEA-14-EXPORT-1/**
  - src/application/export/service.py
  - src/application/export/ports.py
  - src/infrastructure/export/jobs.py
  - src/infrastructure/export/qt_free.py
  - src/bootstrap/core_service.py
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/ImportExportContracts.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/ImportExportPanels.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/ReaderWorkbenchPages.cs
  - tests/reading_export/test_export.py
  - tests/core/test_p16_reader_export.py
  - tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py
  - apps/desktop-avalonia/tests/NewManga.App.Tests/ImportExportUiTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/ExportE2ETests.cs
out_of_scope:
  - **零新 wire**：不改 `IHostController.StartExportAsync` 等既有签名（C-07 旧签名不变）；冲突计划与 scope 选择复用现有命令面
  - **零 DDL**：不改 schema.py / 不新增表
  - 不改 rendition 口径（M2-C1 明确 export 只消费 translated artifact，不提供原图选项）
  - 不新增导出格式（zip/pdf 既有）；不改 PDF 双图层语义
  - 不修改 FEA-15 正式验收声明
---

# FEA-14-EXPORT-1：导出收口切片

## 背景与现状（2026-11-10 侦察）

- 端口齐全：`IHostController` 已有 `ExportDirectorySuggestion` / `GetTranslatedPageIdsAsync` / `StartExportAsync` / `GetExportSnapshotAsync` / `GetExportHistoryAsync` / `CancelExportAsync` / `RevealExportFolderAsync`。
- Core `ExportService` 已支持：scope 由调用方按顺序传入（`orderedPageIds`）、`overwrite_policy`（overwrite/skip/auto-rename，**默认 OVERWRITE**）、取消需调用方 cancel 谓词、`export_history` + `scope_snapshot_json`。
- UI `ExportPanel` 已有 format/PDF 模式/进度/取消/历史/打开目录；**无** scope 三档选择、无顺序预览、无冲突计划提示。
- 缺口（对 FEA-00 §12.2/§15.6 的 EXPORT 项）：同名冲突**默认不覆盖**、scope 三档可见、order 预览、取消保留已成功文件的可判别证据。

## Scope 冻结（2026-11-10，DSH）

1. **默认不覆盖**：Core `ExportRequest.overwrite_policy` 默认由 `OVERWRITE` 改为 `AUTO_RENAME`（保留用户已有文件；同名时新产物自动改名）。显式 `overwrite` 仅保留为既有接口语义（不新增 UI 开关），且不得成为默认。
2. **Host 冲突计划**：`HostController.StartExportAsync` 在目标路径已存在时按默认策略处理（自动改名），不覆盖既有文件；`ExportSnapshotInfo.OutputPath` 反映最终文件名。
3. **scope 三档 + 顺序预览（UI）**：`ExportPanel` 显示「当前页 / 已选页 / 整章」范围与导出顺序（由 `orderedPageIds`/`GetTranslatedPageIdsAsync` 投影），可切换；不新增命令。
4. **取消保留成功文件**：取消时已完成页/已成功文件保留（typed 报告完成数量，不静默删除）；补可判别测试。
5. 零 DDL、零新 wire、旧签名不变。

## Scope 变更记录（2026-11-10，DSH）

- **allowed_paths 追加**：`src/bootstrap/core_service.py`（Core StartExport 构造显式传 `AUTO_RENAME`，第二层防护）、`apps/desktop-avalonia/src/NewManga.App/Views/ReaderWorkbenchPages.cs`（把阅读器当前页 id 传给导出面板）。两者都是 AC1/AC3 的最小实现点，不扩产品面。
- **AC3 口径**：阅读器暂无多选，第三档「已选页」显示为不可用并回退整章（limitation 登记，不冒充可用）；「当前页」由 `ReaderViewModel` 当前页 + `_libraryBook.Pages` 提供。
- **AC2 实现位置**：默认不覆盖在 Host 侧完成（`ExportPathPolicy.NextFreeExportPath` → 目标不存在 → Core target ref `replace_existing=false`）；Core `AUTO_RENAME` 为第二层防护。真实 Host+C core 导出 E2E 需要 `NEWMANGA_EXPORT_SIDECAR_DIR`/`NEWMANGA_EXPORT_DATA_ROOT`（本机未设置 → NOT_RUN）。

## 实现进展（2026-11-10）

- Core：`ExportRequest.overwrite_policy` 默认 `AUTO_RENAME`；`handle_start_export` 显式传 `AUTO_RENAME`。
- Host：`HostController.StartExportAsync` 在注册 target ref 前调用 `ExportPathPolicy.NextFreeExportPath`，保证不发已存在路径。
- UI：`ExportPanel` 增加范围三档（当前页 / 整章 / 已选页-不可用）、顺序预览、完成态输出路径显示；`ReaderPage` 传当前页 id。
- 测试：`tests/reading_export` 新增默认策略/取消不发布测试；App.Tests 新增 `ExportPathPolicyTests`（3）与范围/预览（3）。

## Acceptance Criteria

- [x] **AC1 默认不覆盖**：同名目标已存在时，默认策略导出生成新文件名（auto-rename），既有文件字节/mtime 不变；`overwrite_policy` 默认值为 `AUTO_RENAME`（Core 单测）。 <<MET>>
- [x] **AC2 Host 冲突计划**：`StartExportAsync` 目标已存在 → 不覆盖、最终输出路径可读回；Host 测试覆盖（含路径已存在/不存在两分支）。 <<MET>>
- [x] **AC3 scope 三档与顺序预览**：`ExportPanel` 显示三种 scope 与按 `orderedPageIds` 的顺序预览；UI 测试断言文本/顺序与请求一致（headless）。 <<MET>>
- [x] **AC4 取消保留成功文件**：取消后已完成文件保留且报告完成数；Core 测试断言取消不删除已落盘成功文件、typed 状态为 cancelled。 <<MET>>
- [x] **AC5 零 wire/零 DDL/旧签名**：`git diff` 不含 `IHostController.cs` 签名变更（或仅注释）、不含 `schema.py`；`generate_api_inventory.py --check` EXIT 0（代码实测仍 1/54/6=61）；`verify_pins` 18/18。 <<MET>>
- [x] **AC6 门禁与证据**：`check.ps1`（默认 + `-TaskPath`）PASS；定向/全量测试通过；`verification/FEA-14-EXPORT-1/` 含日志（含 EXIT）与 NOT_RUN 声明。 <<MET>>

## 证据计划（L2）

- `verification/FEA-14-EXPORT-1/logs/`：pytest 定向（`tests/reading_export`、`tests/core/test_p16_reader_export.py`）+ 全量、dotnet Host/App 定向、`check.ps1`、`verify_pins`、`generate_api_inventory.py --check`。
- 冲突计划前后指纹（既有文件 sha256/mtime 不变）；取消后成功文件清单。
- 真实 UI 交互截图 → NOT_RUN（无被审查交互会话）；UI 层由 headless 测试覆盖。

## 风险与回退

| 风险 | 处置 |
|---|---|
| Core 默认策略改动影响既有导出测试 | 先跑全量 pytest 定向，逐项更新期望；只改默认值不改显式语义 |
| auto-rename 命名规则歧义 | 采用 `name (1).ext` 递增，测试覆盖冲突两次 |
| 取消语义误删成功文件 | 只断言不删除；不新增清理路径 |
| 回退 | `git revert`；零 DDL/零 wire 便于回退 |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未创建（主树实现） |
| temp | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无 |
| build | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无 |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 不访问真实用户数据（导出测试用隔离临时目录） |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-EX1-001 | AC1-AC6 | `verification/FEA-14-EXPORT-1/logs/api-inventory.log` | `-` | `2245baa2a0ef67e32d2f0657446801f7abef27e775702c9b380e109953aa5097` | CANONICAL |
| EV-EX1-002 | AC1-AC6 | `verification/FEA-14-EXPORT-1/logs/dotnet-app-tests.log` | `-` | `803b4da685970545cf5656d3e1bf0b0d42e00db1f0dfbf4a3f24a40160c90705` | CANONICAL |
| EV-EX1-003 | AC1-AC6 | `verification/FEA-14-EXPORT-1/logs/dotnet-export-tests.log` | `-` | `c15be75e67d2454808acd7c88129640c8716b2db3dbd7e9971dd1bf5f7d60ea0` | CANONICAL |
| EV-EX1-004 | AC1-AC6 | `verification/FEA-14-EXPORT-1/logs/gates-check.log` | `-` | `027b714c43833229e0373aa0f6d608bf7a65154c26aaef486c82e2893b4a4614` | CANONICAL |
| EV-EX1-005 | AC1-AC6 | `verification/FEA-14-EXPORT-1/logs/gates-pins.log` | `-` | `97e550f7f1a5660ac2f727f549971239b69e555510243edbb0da8206b2224314` | CANONICAL |
| EV-EX1-006 | AC1-AC6 | `verification/FEA-14-EXPORT-1/logs/pytest-full.log` | `-` | `2d57613870dbf9a8ddfb384798453766ece65f4d384ef9f980be4cc51af68eb1` | CANONICAL |
| EV-EX1-007 | AC1-AC6 | `verification/FEA-14-EXPORT-1/README.md` | `-` | `cecd739171201aa912f1cc9c3c99851bf0d09a743ba228ee210928d1704cca61` | CANONICAL |

## Closeout Record

- 未开始（2026-11-10 scope 冻结，`ready`）。
