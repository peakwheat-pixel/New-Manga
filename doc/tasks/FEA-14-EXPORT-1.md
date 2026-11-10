---
id: FEA-14-EXPORT-1
title: FEA-14 切片 EXPORT-1：导出范围/顺序预览/同名冲突默认不覆盖/取消保护
kind: implementation
governance_version: 3
status: done
approval: **DSH 2026-11-10 冻结**（依据 `ADJ-2026-11-10-FEA14-S5-SCOPE` §2.1/§2.2 与 PREQ 共用 wire 口径；FEA-00 §12.2/§15.6 EXPORT 切片；只读侦察 `recon.md` §2.7）
suggested_owner: dsh
owner: dsh
reviewer: r3 独立复核 approved（`doc/reviews/FEA-14-EXPORT-1-r3.md`，P0/P1/P2=0；P3=5 登记）
depends_on:
  - FEA-14-S5-PREQ-1
base_commit: 5459c9220
branch: null
worktree: null
integration_commit: 0720686a6
delivery_head: 0720686a6
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-14-EXPORT-1
allowed_paths:
  - doc/tasks/FEA-14-EXPORT-1.md
  - doc/reviews/FEA-14-EXPORT-1-*.md
  - doc/handoffs/FEA-14-EXPORT-1-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/FEA-14-EXPORT-1/**
  - src/application/export/service.py
  - src/application/export/ports.py
  - src/infrastructure/export/jobs.py
  - src/infrastructure/export/qt_free.py
  - src/infrastructure/export/target_refs.py
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
- 缺口（对 FEA-00 §12.2/§15.6 的 EXPORT 项）：同名冲突**默认不覆盖**、scope 三档可见、order 预览、取消决策的可判别证据（取消保护，不产生/不破坏文件）。

## Scope 冻结（2026-11-10，DSH）

1. **默认不覆盖**：Core `ExportRequest.overwrite_policy` 默认由 `OVERWRITE` 改为 `AUTO_RENAME`（保留用户已有文件；同名时新产物自动改名）。显式 `overwrite` 仅保留为既有接口语义（不新增 UI 开关），且不得成为默认。
2. **Host 冲突计划**：`HostController.StartExportAsync` 在目标路径已存在时按默认策略处理（自动改名），不覆盖既有文件；`ExportSnapshotInfo.OutputPath` 反映最终文件名。
3. **scope 三档 + 顺序预览（UI）**：`ExportPanel` 显示「当前页 / 已选页 / 整章」范围与导出顺序（由 `orderedPageIds`/`GetTranslatedPageIdsAsync` 投影），可切换；不新增命令。
4. **取消保护**：取消不发布新文件、既有目标字节/mtime 不变、typed 状态为 cancelled；导出是单文件原子发布，**不存在「部分成功文件」**故不报告完成数量（r2 R2-002 口径）。补可判别测试。
5. 零 DDL、零新 wire、旧签名不变。

## r3 复核与收口（2026-11-10）

- r3：**approved**（P0/P1/P2=0；P3=5），报告 `doc/reviews/FEA-14-EXPORT-1-r3.md`。R2-001/R2-002/R2-005 全部 CLOSED；R2-001 经收口前探针（旧 target 不变、sibling 生成、越界/已存在负例 typed 拒绝）。
- R3-003（证据不一致）已修：定向 29/0 重跑并写入 `logs/dotnet-export-tests.log`；README AC6/门禁表统一 29/867；EV-EX1-003 hash 已刷新。
- R3-002 已修：取消测试增加旧目标 mtime 断言；背景段旧措辞更新。
- R3-001/R3-005 登记：`publish_to` 无父目录句柄（resolve→replace 极小 TOCTOU，已由 resolve/reparse + 发布后校验缓解）；源码顺序断言属脆弱守卫；真实 Host+Core E2E 仍 NOT_RUN。
- 证据：`verification/FEA-14-EXPORT-1/`（README + 7 份日志）；Canonical Evidence 7 行 hash 与文件一致。

## r2 处置记录（2026-11-10，对 `22683068e` 的 approved + P2 残余）

- **R2-001（P2，已修）**：AUTO_RENAME sibling 发布恢复路径安全校验——`ResolvedExportTarget.publish_to`（`src/infrastructure/export/target_refs.py`：authorized parent resolve/reparse、published 父目录一致、不存在/非 symlink、发布后 entry 校验）；`_publish_to` 调用它。
- **R2-002（P2，已修）**：front-matter title 与 Scope §4 改为「取消保护」口径（单文件原子发布无部分成功文件）；AC4/README 一致。
- **R2-005（P3，已补）**：新增当前页未定位提示测试、完成态输出路径去重测试。
- **R2-003/R2-004/R2-006/R2-007（P3）**：TOCTOU 极小窗口、源码断言脆弱性、provenance、E2E NOT_RUN——已登记，不阻断。
- 其它 r1 findings 已在前一轮处置；r2 门禁：定向 dotnet 29/0、pytest 定向 177、全量见证据日志。

## r1 处置记录（2026-11-10，对 `863d1b4f5` 的 changes_requested；报告 `doc/reviews/FEA-14-EXPORT-1-r1.md`）

- **R-001（P1，已修）**：`P16ExportRuntime` 的 `publish_temp` 曾忽略 AUTO_RENAME 解析路径、仍发布到 mint 的 target（旧文件被覆盖）。修复：发布统一走 `_publish_to(resolved, temp, target)`（同父目录 + 目标不存在校验）；AUTO_RENAME 时跳过 mint target-context；新增 runner 级回归测试。
- **R-002（P2，已补）**：新增源码顺序接线测试（policy 先于 mint）；行为由 `ExportPathPolicyTests` 覆盖；真实 Host+Core E2E 仍 NOT_RUN。
- **R-003（P2，口径修正）**：AC4 判据改为「不产生/不破坏文件 + typed cancelled」——单文件原子发布无部分成功文件语义，原「保留成功文件/报告完成数」表述不适用。
- **R-004（P2，缓解）**：R-001 修复后发布落点由 `_resolve_target`（默认 AUTO_RENAME）决定，mint 的 `replace_existing=true` 不再导致覆盖。
- **R-005（P3，已修）**：当前页未定位时提示「已回退为整章导出」。
- **R-006（P2，已说明）**：`pytest-full.log` 保留首轮失败与修复后全量两段；m2_acceptance 测试显式传 `OVERWRITE` 以保其历史证据语义（本卡默认值变更所致）。
- **R-007（P3，已修）**：README 修正 base/实现提交与 logs provenance；**R-008（P3，已修）** 输出路径不重复；**R-009（P3，已补）** mtime 断言 + runner 边界（mint 时 target 存在、`replace_existing=true`）。

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
- [x] **AC4 取消保护**：取消不发布新文件、既有目标字节/mtime 不变、history/snapshot 为 cancelled（单文件原子发布，无「部分成功文件」语义）。 <<MET>>
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
| EV-EX1-002 | AC1-AC6 | `verification/FEA-14-EXPORT-1/logs/dotnet-app-tests.log` | `-` | `f0493b6c09a27f75cb4ebe394247a36b3a9d9b1832d74946480791ecc58925e9` | CANONICAL |
| EV-EX1-003 | AC1-AC6 | `verification/FEA-14-EXPORT-1/logs/dotnet-export-tests.log` | `-` | `9019c2df287ae3bf030218809e9f6769764dac2a0d94ecaa2f6ede4b34c2306a` | CANONICAL |
| EV-EX1-004 | AC1-AC6 | `verification/FEA-14-EXPORT-1/logs/gates-check.log` | `-` | `027b714c43833229e0373aa0f6d608bf7a65154c26aaef486c82e2893b4a4614` | CANONICAL |
| EV-EX1-005 | AC1-AC6 | `verification/FEA-14-EXPORT-1/logs/gates-pins.log` | `-` | `97e550f7f1a5660ac2f727f549971239b69e555510243edbb0da8206b2224314` | CANONICAL |
| EV-EX1-006 | AC1-AC6 | `verification/FEA-14-EXPORT-1/logs/pytest-full.log` | `-` | `58f9593dbc1af403739a231a0127eff278e7383b2955c21126edb8620e42a0f8` | CANONICAL |
| EV-EX1-007 | AC1-AC6 | `verification/FEA-14-EXPORT-1/README.md` | `-` | `02797f4f42ce2f647b0396555bbc7b2b9b5ed32e707503ae6a44ab49b6f3985d` | CANONICAL |

## Closeout Record

- 结论：**完成**（2026-11-10）。3 轮独立复核：r1 changes_requested（P1=1：runner 未按 AUTO_RENAME 路径发布）→ r1 处置 → r2 **approved**（P2 残余：sibling 发布安全校验、AC4 口径）→ r2 处置 → **r3 approved**（P0/P1/P2=0；P3=5 登记）。
- 交付：Core 默认 `AUTO_RENAME` + runner 按解析路径发布（`_publish_to`→`ResolvedExportTarget.publish_to`）；Host `ExportPathPolicy` auto-rename；UI scope 三档/顺序预览/完成态路径/取消保护；零新 wire/零 DDL/旧签名不变。
- 证据：定向 29/0；App.Tests 全量 867/0/11；pytest 全量 3477/0/10；`check.ps1`（默认 + TaskPath）PASS；`verify_pins` 18/18；API `--check` EXIT 0。
- 残余 limitation（不阻断）：真实 Host+Core E2E = NOT_RUN（`NEWMANGA_EXPORT_SIDECAR_DIR`/`NEWMANGA_EXPORT_DATA_ROOT` 未设置）；真实 UI 截图 = NOT_RUN；阅读器多选未实现（已选页档不可用）；`publish_to` resolve→replace 极小 TOCTOU；源码顺序断言脆弱；并发压力未测。
- 零契约字节（C-07/C-02/C-03/P15 未改）；未 push。
