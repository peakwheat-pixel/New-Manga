# FEA-14-EXPORT-1 证据索引（导出收口切片）

- Task：`FEA-14-EXPORT-1`（导出范围/顺序预览/同名冲突默认不覆盖/取消保留成功文件）
- Base：`5459c9220`（PREQ-1 收口）；实现头部：`30af54a3c`（工作树，提交见卡面 `delivery_head`）
- 契约：**零新 wire / 零 DDL**；`IHostController` 旧签名不变；C-07 v1.2 pin 生效
- 日期：2026-11-10

## 结论状态

| AC | 判别 | 结果 |
|---|---|---|
| AC1 默认不覆盖 | 同名目标存在 → 默认 auto-rename，旧文件字节不变；`overwrite_policy` 默认 `AUTO_RENAME` | **MET**：`test_default_policy_never_replaces_an_existing_target`（Core）+ `test_overwrite_policy_replaces_existing_target` 显式覆盖语义 |
| AC2 Host 冲突计划 | Host 在注册 target ref 前 auto-rename，永不发已存在路径；最终路径可读回 | **MET（helper/单测层）**：`ExportPathPolicyTests`（3）；完整 Host+C core E2E **NOT_RUN**（需 `NEWMANGA_EXPORT_SIDECAR_DIR`/`NEWMANGA_EXPORT_DATA_ROOT`，本机未设置）；UI 完成态显示 `OutputPath` |
| AC3 scope 三档与顺序预览 | 三档可见 + 顺序预览与请求一致 | **MET（带 limitation）**：`Reader_ExportScopeSelector_ShowsThreeScopesAndOrderPreview`、`Reader_ExportCurrentPageScope_SendsOnlyTheLoadedPage`；「已选页」在阅读器无多选 → 不可用并回退整章（limitation） |
| AC4 取消保留成功文件 | 取消不发布新文件、不改既有目标、history=cancelled | **MET**：`test_cancel_before_replace_publishes_nothing`（含 auto-rename 目标不创建、旧文件字节不变） |
| AC5 零 wire/零 DDL/旧签名 | 无 `IHostController` 签名变更、无 schema 变更；`--check` EXIT 0（1/54/6=61）；pins 18/18 | **MET**：`logs/api-inventory.log` EXIT 0；`logs/gates-pins.log` PASS (all 18)；`git status` 无 `IHostController.cs`/`schema.py` 改动 |
| AC6 门禁与证据 | `check.ps1`（默认 + TaskPath）PASS；定向/全量测试 0 failed；证据含 EXIT + NOT_RUN | **MET**：`logs/gates-check.log` PASS；定向 26/0；App.Tests 全量 864/0/11；pytest 全量 3476/0/10 |

## 门禁与证据（本目录）

| 日志 | 内容 | EXIT |
|---|---|---|
| `logs/dotnet-export-tests.log` | App.Tests 定向导出 26 passed / 0 failed（ImportExportUiTests + PdfExportUiTests + ExportStalePolicyTests + ExportPathPolicyTests） | 0 |
| `logs/dotnet-app-tests.log` | App.Tests 全量 **864 passed / 0 failed / 11 skipped**（875 total） | 0 |
| `logs/pytest-full.log` | pytest 全量 **3476 passed / 0 failed / 10 skipped** | 0 |
| `logs/gates-check.log` | `check.ps1` 默认 + `-TaskPath doc/tasks/FEA-14-EXPORT-1.md` PASS（3 warnings） | 0 |
| `logs/gates-pins.log` | `verify_pins` **PIN AUDIT: PASS (all 18)** | 0 |
| `logs/api-inventory.log` | `generate_api_inventory.py --check` EXIT 0（代码实测 1/54/6=61，计划节不计入） | 0 |

## 实现要点

- **Core**（`src/application/export/service.py`）：`ExportRequest.overwrite_policy` 默认 `AUTO_RENAME`（既有 `_next_free_name` 生成 `name (n).ext`）；`src/bootstrap/core_service.py` 的 `handle_start_export` 显式传 `AUTO_RENAME` 作为第二层防护（wire 无 overwrite 字段）。
- **Host**（`HostController.StartExportAsync`）：注册 target ref 前调用 `ExportPathPolicy.NextFreeExportPath`——目标已存在则改名，保证发给 Core 的路径**不存在**（`replace_existing=false`），发布步骤无法覆盖旧字节。`ExportPathPolicy` 在 `ImportExportContracts.cs`（public static，可测试）。
- **UI**（`ExportPanel`）：范围三档（当前页/整章/已选页-不可用）、按 `orderedPageIds` 的顺序预览（`1.p1 → 2.p2`）、完成态把实际输出路径拼入状态文本；`ReaderPage` 通过 `_libraryBook.Pages[CurrentPageIndex].PageId` 传当前页。
- 契约零字节：C-07/C-02/C-03/P15 未改；DDL 未改；旧签名不变。

## NOT_RUN（不得记 PASS）

- **真实 Host + 真实 Core sidecar 导出 E2E**：`NEWMANGA_EXPORT_SIDECAR_DIR` / `NEWMANGA_EXPORT_DATA_ROOT` 未设置 → `ExportE2ETests` 4 项全部 skip（`logs` 中未产生导出 E2E 结果）。AC2 的端到端层未验证，仅 helper/单元层验证。
- **真实 UI 会话截图/人工目视**：无被审查交互会话；UI 由 headless 测试覆盖。
- **阅读器多选**：无多选机制 → 「已选页」档不可用（UI 明示并回退整章）。
- **Core `AUTO_RENAME` 并发窗口**：title 层防护 + Host 预检查已覆盖；极端并发下 Core 的 target-ref 校验会 typed 拒绝（不覆盖），但未做压力测试。

## 复现

```powershell
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --filter "FullyQualifiedName~ImportExportUiTests|FullyQualifiedName~PdfExportUiTests|FullyQualifiedName~ExportStalePolicyTests|FullyQualifiedName~ExportPathPolicyTests"
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj
python -m pytest -q
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-14-EXPORT-1.md
pwsh -NoProfile -File tools/governance/verify_pins.ps1
python tools/generate_api_inventory.py --check
```
