# FEA-14-EXPORT-1 证据索引（导出收口切片）

- Task：`FEA-14-EXPORT-1`（导出范围/顺序预览/同名冲突默认不覆盖/取消保护）
- Base：`5459c9220`（PREQ-1 收口）；实现提交：`3b2ae8ff5`；r1 处置提交：见 `git log`（本 README 随修复提交）
- 契约：**零新 wire / 零 DDL**；`IHostController` 旧签名不变；C-07 v1.2 pin 生效
- 日期：2026-11-10

## 结论状态（r1 处置后）

| AC | 判别 | 结果 |
|---|---|---|
| AC1 默认不覆盖 | 同名目标存在 → 默认 auto-rename，旧文件字节/mtime 不变；`overwrite_policy` 默认 `AUTO_RENAME`；**runner 路径同样不覆盖** | **MET**：`test_default_policy_never_replaces_an_existing_target`（含 mtime）、`test_runtime_publishes_the_auto_renamed_path_without_touching_the_minted_target`（R-001：P16 runner 发布到 `(1)` 路径，旧 target 保持 `OLD`）、`test_overwrite_policy_replaces_existing_target`（显式覆盖语义） |
| AC2 Host 冲突计划 | Host 在注册 target ref 前 auto-rename，永不发已存在路径；最终路径可读回 | **MET（helper + 源码顺序测试）**：`ExportPathPolicyTests`（4，含自由/已存在/二次冲突/目录同名）+ `HostStartExportResolvesTheNameBeforeMintingTheTargetRef`（源码断言 policy 先于 mint）；完整 Host+C core E2E **NOT_RUN**（需环境变量，本机未设置）；UI 完成态显示实际 `OutputPath`（不重复） |
| AC3 scope 三档与顺序预览 | 三档可见 + 顺序预览与请求一致 | **MET（带 limitation）**：`Reader_ExportScopeSelector_ShowsThreeScopesAndOrderPreview`、`Reader_ExportCurrentPageScope_SendsOnlyTheLoadedPage`、`Reader_ExportSelectionScope_FallsBackToChapterWithNotice`；「已选页」在阅读器无多选 → 不可用并回退整章；当前页未定位时提示回退（R-005） |
| AC4 取消保护 | 取消不发布新文件、不改既有目标、history/snapshot 为 cancelled | **MET**：`test_cancel_before_replace_publishes_nothing`（auto-rename 目标不创建、旧文件字节不变、history=cancelled）。口径说明（r1 R-003）：导出是**单文件原子发布**，不存在「部分成功文件」，故判据为「不产生/不破坏文件 + typed cancelled」 |
| AC5 零 wire/零 DDL/旧签名 | 无 `IHostController` 签名变更、无 schema 变更；`--check` EXIT 0（1/54/6=61）；pins 18/18 | **MET**：`logs/api-inventory.log` EXIT 0；`logs/gates-pins.log` PASS (all 18)；`git diff` 无 `IHostController.cs`/`schema.py` |
| AC6 门禁与证据 | `check.ps1`（默认 + TaskPath）PASS；定向/全量测试 0 failed；证据含 EXIT + NOT_RUN | **MET**：`logs/gates-check.log` PASS；定向 27/0；App.Tests 全量 **865/0/11**；pytest 全量 **3477/0/10** |

## r1 处置记录（2026-11-10，对 `863d1b4f5` 的 changes_requested）

- **R-001（P1，已修）**：`P16ExportRuntime` 的 `publish_temp` 曾忽略解析后的 AUTO_RENAME 路径、仍用 mint 的 target 发布 → 旧 target 被覆盖。修复：`publish_temp` 把解析路径传给 `_publish_and_mark`；发布统一走 `_publish_to`（同父目录校验 + 目标不存在校验 + `os.replace`）；AUTO_RENAME 时跳过 mint target-context（其发布后校验只认原路径）。新增 runner 级回归测试。
- **R-002（P2，已补）**：新增 `HostStartExportResolvesTheNameBeforeMintingTheTargetRef` 源码顺序断言（policy 先于 mint）；行为由 `ExportPathPolicyTests` 覆盖。真实 Host+C core E2E 仍 NOT_RUN。
- **R-003（P2，口径修正）**：AC4 卡面/证据改为「取消不产生/不破坏文件 + typed cancelled」；单文件导出无「部分成功文件保留」语义，原卡面表述已按此修正。
- **R-004（P2，缓解）**：R-001 修复后发布目标由 `_resolve_target`（默认 AUTO_RENAME）决定，mint 时 `replace_existing=true` 不再导致覆盖；Host policy→mint 的 TOCTOU 影响降为「mint 允许 replace，但发布落点仍不覆盖」。
- **R-005（P3，已修）**：当前页未定位且请求「当前页」时显示「当前页未定位；已回退为整章导出」，不静默。
- **R-006（P2，已说明）**：`pytest-full.log` 保留首轮全量失败记录（m2 测试断言默认 overwrite）与修复后 full run；`m2_acceptance` 测试显式传 `overwrite_policy=OVERWRITE` 以保持其历史证据语义（本卡默认值变更所致）。
- **R-007（P3，已修）**：本 README 修正 base/实现提交；`logs/*` 的 HEAD 头为生成时（提交前）head——提交紧随、代码字节未变；`gates-check.log` 中 STATUS/PLAN 字节数为生成时值。
- **R-008（P3，已修）**：完成态状态文本仅在 `SnapshotStatus` 未含输出路径时追加，避免重复。
- **R-009（P3，已补）**：默认策略测试断言旧文件 mtime 不变；runner 级测试覆盖「mint 时 target 存在、`replace_existing=true`」的 ref 形态。

## 门禁与证据（本目录）

| 日志 | 内容 | EXIT |
|---|---|---|
| `logs/dotnet-export-tests.log` | App.Tests 定向导出 **27 passed / 0 failed**（ImportExportUiTests + PdfExportUiTests + ExportStalePolicyTests + ExportPathPolicyTests） | 0 |
| `logs/dotnet-app-tests.log` | App.Tests 全量 **865 passed / 0 failed / 11 skipped**（876 total） | 0 |
| `logs/pytest-full.log` | pytest 全量 **3477 passed / 0 failed / 10 skipped**（含首轮失败与修复后 full run 两段记录） | 0 |
| `logs/gates-check.log` | `check.ps1` 默认 + `-TaskPath doc/tasks/FEA-14-EXPORT-1.md` PASS（3 warnings） | 0 |
| `logs/gates-pins.log` | `verify_pins` **PIN AUDIT: PASS (all 18)** | 0 |
| `logs/api-inventory.log` | `generate_api_inventory.py --check` EXIT 0（代码实测 1/54/6=61，计划节不计入） | 0 |

## 实现要点（r1 处置后）

- **Core**（`src/application/export/service.py`）：`ExportRequest.overwrite_policy` 默认 `AUTO_RENAME`；`P16ExportRuntime` 发布使用解析后的路径（`_publish_to`，同父目录 + 不存在校验）；AUTO_RENAME 跳过 mint target-context。`src/bootstrap/core_service.py` 的 `handle_start_export` 显式传 `AUTO_RENAME`。
- **Host**（`HostController.StartExportAsync`）：注册 target ref 前调用 `ExportPathPolicy.NextFreeExportPath`——目标已存在则改名，发给 Core 的路径不存在；`ExportPathPolicy` 在 `ImportExportContracts.cs`（public static）。
- **UI**（`ExportPanel`）：范围三档 + 顺序预览 + 完成态实际输出路径（去重）；`ReaderPage` 传当前页 id。
- 契约零字节：C-07/C-02/C-03/P15 未改；DDL 未改；旧签名不变。

## NOT_RUN（不得记 PASS）

- **真实 Host + 真实 Core sidecar 导出 E2E**：`NEWMANGA_EXPORT_SIDECAR_DIR` / `NEWMANGA_EXPORT_DATA_ROOT` 未设置 → `ExportE2ETests` 4 项 skip；AC2 端到端层未验证（helper + 源码顺序 + runner 单测覆盖）。
- **真实 UI 会话截图/人工目视**：无被审查交互会话；UI 由 headless 测试覆盖。
- **阅读器多选**：无多选机制 → 「已选页」档不可用（UI 明示并回退整章）。
- **Core AUTO_RENAME 极端并发压力**：Host 预检查 + Core `_publish_to` 目标不存在校验覆盖常规窗口；未做压力测试。

## 复现

```powershell
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --filter "FullyQualifiedName~ImportExportUiTests|FullyQualifiedName~PdfExportUiTests|FullyQualifiedName~ExportStalePolicyTests|FullyQualifiedName~ExportPathPolicyTests"
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj
python -m pytest -q
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-14-EXPORT-1.md
pwsh -NoProfile -File tools/governance/verify_pins.ps1
python tools/generate_api_inventory.py --check
```
