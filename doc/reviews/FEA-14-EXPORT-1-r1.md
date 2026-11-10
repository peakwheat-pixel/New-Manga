---
task_id: FEA-14-EXPORT-1
reviewer: fresh 独立上下文子 agent（由 Lead 派发；未参与本卡实现/返修）
reviewer_kind: subagent
author: dsh
base_commit: 30af54a3c
reviewed_head: 863d1b4f5
decision: changes_requested
---

# Review：FEA-14-EXPORT-1（导出收口切片，r1）

## 0. 审查对象、环境与范围

- 仓库 `G:\CODEX\New Manga`，`main`；**HEAD = `863d1b4f5015cd823e92dc36f3118b06bd732a42`**。审查开始 `2026-11-10T10:38:43+08:00`、结束 `10:55:31+08:00` 两次实测 `git status --short` 均 **clean**，HEAD 不变。
- 被审范围：`git diff 30af54a3c..863d1b4f5` = **20 个文件**（实现提交 `3b2ae8ff5` 的 20 文件 + allowed_paths 补提 `863d1b4f5` 只改卡面的 3 行，合计仍 20 个不同文件；Lead 描述为 21，实测 20，见 R-007）。卡面 `base_commit: 5459c9220` 为卡冻结点，实现基线 `30af54a3c` 为其下一提交；本报告以 Lead 指定 `30af54a3c` 为 diff base。
- 只读纪律：仅写本文件；未改源码/测试/契约/卡面/证据，未 commit/push。探针脚本与日志只写仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-EXPORT-1-r1\`。
- 关键被审文件：Core `src/application/export/service.py`、`src/bootstrap/core_service.py`；Host `HostController.cs`、`ImportExportContracts.cs`（`ExportPathPolicy`）、`ImportExportPanels.cs`、`ReaderWorkbenchPages.cs`；测试 `tests/reading_export/test_export.py`、`ImportExportUiTests.cs`、m2 acceptance；证据 `verification/FEA-14-EXPORT-1/`。

## 1. 结论

**`changes_requested`。**

| 计数 | 值 |
|---|---|
| P0 | **0** |
| P1 | **1**（R-001：Core 导出运行器未按 AUTO_RENAME 发布；既有目标可被覆盖、任务卡在 publishing） |
| P2 | **3**（R-002 Host 接线无集成测试/AC2 声称过高；R-003 AC4 完成数/完成文件证据缺口；R-004 Host 策略→mint TOCTOU） |
| P3 | **5**（AC3 当前页未定位回退；m2 acceptance 改显式 OVERWRITE 与 pytest 日志先失败后通过；完成态路径重复；证据 provenance；AC1 mtime/策略边界） |

## 2. Findings

| ID | 级别 | 位置 | 事实与影响 | 证据 | 建议 |
|---|---|---|---|---|---|
| R-001 | **P1** | `src/application/export/service.py:461-473`（AUTO_RENAME resolve）、`:826-838`（运行器 `publish_temp` lambda）、`:975-1000`（`_publish_and_mark`）、`:364-370`（result path）；`src/infrastructure/export/target_refs.py:86-90,192-200` | **Core 导出运行器没有按 AUTO_RENAME 的新路径发布**：`_export()` 把 `_resolve_target()` 返回的重命名路径 `name (1).ext` 作为 `publish_temp(temp, target.path)` 第二参数传入，但运行器 lambda 忽略该参数、仍用 `start()` 捕获的**原 target** 调 `_publish_and_mark` → `target.publish()`。当 target ref 的 `replace_existing=true` 且原目标存在时，`AUTO_RENAME` 在 `_export` 内已改名为 `(1)`，但发布仍写回原路径，**覆盖既有用户文件**；同时 `ExportResult.output_path` 指向未创建的 `(1)` 路径，运行器 `_run` 判定输出不存在而停在 `publishing`，history `output_path` 指向不存在的文件。实测（仓外探针，见 §5）默认 AUTO_RENAME + `ResolvedExportTarget(target, replace_existing=True)` → 原 target 字节被覆盖为 ZIP、`book (1).zip` 不存在、job 状态 `publishing`。该 ref 形态可由 `HostIssuer.MintExportGrant` 在 mint 时目标已存在产生（`HostIssuer.cs:453-467`）；Host `ExportPathPolicy` 与 `MintExportGrant` 之间存在 TOCTOU 窗口（R-004），因此「第二层防护」在当前实现中不成立。 | 探针 `probe_runner_autorename.py` 输出：`status: publishing`、`target bytes: PK…`、`renamed exists: False`、history `output_path=…\book (1).zip`；代码行如右列 | 运行器 `_publish_and_mark` 必须发布到 `_target`/`_ResolvedTarget.path`（把 rename 结果传入并更新 publication_intent），或由 Host 侧强制 mint `replace_existing=false` 并在 mint 处二次校验；补一条 runner 级测试：既有目标 + AUTO_RENAME → 旧 bytes 不变、`(1)` 文件存在、状态 completed；再加 TOCTOU/并发负例 |
| R-002 | **P2** | 卡 `:84`（AC2）；`docs` 证据；`apps/desktop-avalonia/tests/NewManga.App.Tests/ImportExportUiTests.cs:574-635`；`NewManga.Host.Tests/ExportE2ETests.cs:147` | **AC2「Host 测试覆盖（含路径已存在/不存在两分支）」名不副实**：`ExportPathPolicyTests` 只测 `ExportPathPolicy` 纯 helper；没有任何测试构造真实 `HostController.StartExportAsync` 断言「先 policy 后 grants」的接线。`ExportE2ETests` 直接调用 `runtime.Grants.StartExportAsync(request, target)`（绕过 HostController），且 `NEWMANGA_EXPORT_SIDECAR_DIR`/`NEWMANGA_EXPORT_DATA_ROOT` 均未设置 → 4 项 E2E skip（README 已如实记 NOT_RUN）。后果：以后删除/调换 HostController 中 policy 调用，现有测试全绿，AC2 的 Host 冲突计划无回归保护。 | 实测 env 两变量为空；`ExportE2ETests` 直接 grants；测试目录仅 helper 3 项；卡 AC2 `<<MET>>` | 补 HostController 级测试（fake grant client/记录 target path，断言发下去的是 `NextFreeExportPath` 结果且不存在）；或把 AC2 明确降为「helper 层 MET + E2E NOT_RUN」并删除卡面「Host 测试覆盖」措辞 |
| R-003 | **P2** | 卡 `:86`（AC4）；`tests/reading_export/test_export.py:313-328`；`src/application/export/service.py:946-948`、`ImportExportContracts.cs:313-315` | **AC4 证据只覆盖「取消不发布」**，未覆盖 AC 原文的「已完成文件保留且报告完成数」：`test_cancel_before_replace_publishes_nothing` 断言旧 target bytes 不变、无 `cancelled (1).zip`、history=cancelled；但既不构造「取消前已有若干 completed 文件/页」场景，也不断言 `completed_pages`/typed 完成数（`_run` 取消路径只写 status=cancelled，UI `SnapshotStatus` 只显示「已取消（未发布文件）」）。后果：AC4 的「完成数」子项没有任何测试/实现证据，卡面仍标 MET。 | 测试 `:313-328`；cancel UI 文案 `ImportExportContracts.cs:313-315`；`service.py:946-948` 仅 status/error_code | 补取消中途（已处理 N 页/已有成功文件）的断言：`completed_pages` 保留且可读回、既有 completed 文件不被删除；或在卡面/README 明确 AC4 只要求「不发布/既有目标不变」并降级措辞 |
| R-004 | **P2** | `HostController.cs:1839-1844`；`HostIssuer.cs:453-467` | **Host 策略→mint 的 TOCTOU**：`ExportPathPolicy.NextFreeExportPath` 选出的自由路径在 `grants.StartExportAsync` 内由 `MintExportGrant` 再次 `File.Exists(target)` 决定 `replace_existing`；两者之间文件若被创建，mint 得到 `replace_existing=true`，Core 在 R-001 的 runner 缺陷下会覆盖该文件。即使 R-001 修复，Host 也应保证「我选定的自由路径」以 `replace_existing=false` 送到 Core（或 mint 时对 policy 结果二次校验）。当前 README `:42` 的「极端并发下 Core 的 target-ref 校验会 typed 拒绝（不覆盖）」对该窗口不成立。 | 代码顺序 + `HostIssuer.cs:453-467`；探针 R-001 复现 | Host 侧把「已选自由路径」以显式 `replace_existing=false` 语义 mint（例如 `MintExportGrant` 增参数/二次校验 target 不存在），或在 HostController 内 policy+grant 原子化；补并发/TOCTOU 测试 |
| R-005 | P3 | `src/application/export/service.py:462-472`、`ImportExportPanels.cs:462-503` | **AC3 当前页在未翻译/未定位时静默回退整章**：`SelectedPageIds()` 仅当 `_currentPageId` 在 `_translated` 中才返回当前页，否则返回整章；UI 标签显示「当前页（未定位）」但无「已回退整章」提示，导出请求范围与用户点选的「当前页」语义不一致。已选页回退有提示与测试；当前页未定位分支无测试。 | `ImportExportPanels.cs:462-473,490-503`；现有 UI 测试 `:420-484` 只覆盖 current 已知/已选页回退 | 在「当前页未定位」时显式提示并/或把选择切到整章（像已选页一样），补该分支 UI 测试 |
| R-006 | P3 | `verification/FEA-14-EXPORT-1/logs/pytest-full.log:317-318,364,365-468,514`；`tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py:342-354,369`；README `:25` | **m2 acceptance 由默认 OVERWRITE 改为显式 OVERWRITE，且全量 pytest 日志含一次失败**：日志第一次全量 run 在 m2 test 因 `scope["overwrite_policy"] == "overwrite"` 失败（`assert 'auto_rename' == 'overwrite'`，1 failed/3475 passed，EXIT=1，`:317-318,364`），随后「final full run」显式 OVERWRITE 后 3476/0/10 EXIT 0（`:365-468,514`）。README 只列最终数字，未说明先失败及 m2 测试被改；默认策略在 acceptance 层不再被验证（仅单元测试覆盖）。 | 日志原文；m2 test 差异 | 在 README/证据说明中如实记录第一次失败→m2 测试改显式 OVERWRITE→重跑通过；或增加一条默认 AUTO_RENAME 的 acceptance 断言，避免「改测试适配实现」削弱原证据 |
| R-007 | P3 | `verification/FEA-14-EXPORT-1/README.md:4`；logs 头部；`doc/tasks/FEA-14-EXPORT-1.md:13,17,118-124` | **证据 provenance/一致性瑕疵**：README 写「Base 5459c9220；实现头部 30af54a3c（工作树，提交见卡面 delivery_head）」，但实际实现头是 `863d1b4f5`、diff base 是 `30af54a3c`、卡面 `base_commit=5459c9220` 且 `delivery_head:null`/Canonical Evidence commit 列 `-`；全部日志记录的 `HEAD=30af54a3c`（提交前父提交，无法证明 commit 内容）；`gates-check.log` 的 STATUS/PLAN 字节数（3184/6826）与最终树（3181/6857）不同；Lead 说 21 文件、实测 20。 | 文件/日志实测；`git diff --name-only` 20 | 统一并写实 README 的 base/impl/head；日志在交付 head 重生成或附「父 HEAD + 提交哈希 + diff」；更新卡面 `delivery_head`/Canonical commit；如证据仍用父 HEAD 日志，注明被测树=提交内容 |
| R-008 | P3 | `ImportExportPanels.cs:744-768`；`ImportExportContracts.cs:299-305` | **完成态输出路径重复显示**：`SnapshotStatus` 已完成分支已返回 `…：{OutputPath}{sha}{pages}`；`UpdateFromSnapshot` 又追加 `\n输出：{OutputPath}`，UI 显示两次路径。无测试断言；不影响正确性。 | 代码两处；现有测试未断言完成态文本 | 删除追加或仅在 `SnapshotStatus` 不含路径时追加；补一条完成态文本断言 |
| R-009 | P3 | `tests/reading_export/test_export.py:204-216`；`ImportExportUiTests.cs:592-635` | **AC1/策略边界断言不足**：AC1 声称旧文件「字节/mtime 不变」，Core/Host 测试只断言 bytes；`ExportPathPolicyTests` 未覆盖大小写异构路径、symlink、9999 上限；无 runner 级 auto-rename 测试（R-001 的缺口根因之一）。 | 测试代码；探针 | 增加 mtime 断言；补 case/symlink/边界测试；补 runner 级测试（见 R-001/R-004） |

## 3. AC 逐项（不把未实测项记 PASS）

| AC | 状态 | 依据 |
|---|---|---|
| AC1 默认不覆盖 | **PARTIAL（R-001）** | 直接 `ExportService.export` 路径：默认 `AUTO_RENAME`（`service.py:169`）、`core_service.handle_start_export` 显式 AUTO_RENAME（`:5922`）、`_next_free_name` 命名 `name (n).ext`（`:707-714`）、`test_default_policy_never_replaces_an_existing_target` 通过（旧 bytes 不变、completed、`default (1).zip`）。**但 wire 运行器 `P16ExportRuntime` 路径在 target ref `replace_existing=true` 时不按重命名发布（R-001 探针：旧 target 被覆盖、`(1)` 不存在、状态 publishing）**，故 AC1 的「默认永不覆盖」在 runner 路径不成立；mtime 亦未断言（R-009） |
| AC2 Host 冲突计划 | **PARTIAL** | Host 代码顺序正确（`HostController.cs:1843` policy → grants）；`ExportPathPolicy` 行为 helper 测试覆盖（自由/existing/二次冲突/目录）；但无 HostController 接线测试、E2E env 未设置且 `ExportE2ETests` 绕过 HostController → 卡面「Host 测试覆盖」与 `<<MET>>` 过高（README 已注 helper/NOT_RUN） |
| AC3 scope 三档与顺序预览 | **MET（带 limitation）** | `ExportPanel` 三档（`ImportExportPanels.cs:368-387`）、默认整章、顺序预览（`:506-511`）、当前页 id 由 `ReaderPage` 传入（`ReaderWorkbenchPages.cs:2104-2110`）；UI 测试 3 项（`ImportExportUiTests.cs:420-484`）全绿；已选页回退提示/整章有测试；当前页未定位静默回退为 P3/R-005 |
| AC4 取消保留成功文件 | **PARTIAL** | `test_cancel_before_replace_publishes_nothing` 覆盖旧 target bytes、无新文件、history cancelled；未覆盖「报告完成数」/已有完成文件保留（R-003）；卡面 AC4 `<<MET>>` 高于证据 |
| AC5 零 wire/零 DDL/旧签名 | **MET** | diff 无 `IHostController.cs`/`schema.py`；`--check` EXIT 0（1/54/6=61）；`verify_pins` 18/18；无 src/apps 签名面变化 |
| AC6 门禁与证据 | **MET（P3 残余）** | check 默认/TaskPath PASS、pins 18/18、API EXIT 0、定向/全量 App+pytest 全绿（见 §5）；NOT_RUN（真实 Host+Core E2E、真实 UI、多选）已声明；日志 provenance/首次失败见 R-006/R-007 |

## 4. 范围与越界

- `git diff --name-status 30af54a3c 863d1b4f5` 20 文件，逐项与卡面 `allowed_paths`（`:21-42`）匹配 **OUT=0**；禁止目录命中 0。
- 无 `IHostController.cs`/`schema.py`/其它契约字节改动；`verify_pins` 18/18、API 61 不变。
- 无 `doc/plan/**`、`doc/contracts/**` 改动；`src/**` 仅 `src/application/export/service.py`、`src/bootstrap/core_service.py`（均在 allowed）。
- 结论：**无越界**；本审查写域仅本文件。

## 5. 门禁与实测（命令 + 时点 + EXIT）

| # | 命令 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `dotnet test .../NewManga.App.Tests.csproj --filter "FullyQualifiedName~ImportExportUiTests\|~PdfExportUiTests\|~ExportStalePolicyTests\|~ExportPathPolicyTests"` | 10:44:46 → 10:44:50 | **26 通过 / 0 失败**（与 `dotnet-export-tests.log` 一致） | **0** |
| 2 | `python -m pytest tests/reading_export tests/core/test_p16_reader_export.py tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py -q` | 10:44:01 → 10:44:35 | **176 passed** | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/check.ps1` | 10:45:00 → 10:45:02 | PASS（3 warnings：11 非终态 / STATUS 3181 B·31 L / PLAN 6857 B·64 L） | **0** |
| 3b | `... check.ps1 -TaskPath doc/tasks/FEA-14-EXPORT-1.md` | 10:45:00 → 10:45:02 | PASS（同上） | **0** |
| 4 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 10:45:03 | **PIN AUDIT: PASS (all 18)** | **0** |
| 5 | `python tools/generate_api_inventory.py --check` | 10:45:03 | `OK: rendered counts match`；**1/54/6 = 61** | **0** |
| 6 | `dotnet test .../NewManga.App.Tests.csproj`（全量） | 10:46:08 → 10:52:07（5 m 55 s） | **864 通过 / 0 失败 / 11 跳过 / 875 总计** | **0** |
| 7 | `python -m pytest -q`（全量） | 10:46:08 → 10:51:27（5 m 16 s） | **3476 passed / 10 skipped** | **0** |
| 8 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 10:38:43 / 10:55:31 | 两次均 **clean**；HEAD 均 `863d1b4f5…` | — |
| 9 | 独立探针 `python ...\probe_runner_autorename.py`（R-001） | 10:53 前后 | `status: publishing`；`target bytes` 被覆盖为 ZIP；`book (1).zip` 不存在；history output_path 指向不存在的 `(1)` 路径 | 0（探针自身） |

> 探针在仓外构造 `ExportService` + `P16ExportRuntime` + `ResolvedExportTarget(path, replace_existing=True)`，默认 `AUTO_RENAME`；不是产品调用链的端到端测试，但复现了 `P16ExportRuntime` 的发布路径行为（日志 `G:\CODEX\New Manga.workspace\temp\FEA-14-EXPORT-1-r1\probe-runner-autorename.log`）。

## 6. 证据复核

| 证据 | 核对 | 判定 |
|---|---|---|
| `dotnet-export-tests.log` | 26/0，EXIT 0；HEAD=`30af54a3c`（提交前父提交）；本审查重跑 26/0 | 可复现（provenance P3） |
| `dotnet-app-tests.log` | 864/0/11，EXIT 0；本审查重跑 864/0/11 | 可复现 |
| `pytest-full.log` | 首次 1 failed/3475 passed EXIT=1（m2 `overwrite_policy` 断言），随后「final full run」3476/0/10 EXIT=0；本审查全量 3476/0/10 | 最终可复现；先失败/重跑未在 README 说明（R-006） |
| `gates-check.log` | PASS/EXIT 0；STATUS/PLAN 字节数 3184/6826，与最终树 3181/6857 不同 | PASS 有效，provenance 需刷新（R-007） |
| `gates-pins.log` / `api-inventory.log` | 18/18 EXIT 0；`--check` 61 EXIT 0；本审查重跑一致 | 可复现 |
| `README.md` | AC/PASS/EXIT 数值与日志大体一致；base/实现头描述错误；AC2 helper/NOT_RUN 已如实；AC4 措辞窄于卡面 | 基本如实，需同步 |
| 卡面 Canonical Evidence | 7 个 sha256 与当前文件逐一匹配（实测） | 字节匹配；`commit` 列 `-` 待填 |
| NOT_RUN | 真实 Host+Core E2E env 两变量实测为空 → ExportE2ETests skip；真实 UI/多选未做 | 如实，不冒充 PASS |

## 7. NOT_RUN 声明

- **真实 Host + Core sidecar 导出 E2E**：`NEWMANGA_EXPORT_SIDECAR_DIR`/`NEWMANGA_EXPORT_DATA_ROOT` 实测为空 → `ExportE2ETests` skip（本审查未取得 Host.Tests 日志；仅 App.Tests 日志存在）。AC2 端到端层未验证。
- **真实 UI 交互/截图**：无被审查交互会话；仅 headless 测试。
- **阅读器多选**：无多选机制，「已选页」回退整章（已有提示/测试）。
- **HostController 级 policy 集成测试**：不存在（R-002）。
- **Core runner 级 AUTO_RENAME 测试**：不存在（R-001 探针为仓外一次验证，非仓库测试）。
- **并发/TOCTOU 压测**：未做（R-004）。
- **全量 Host.Tests**：未运行（本卡证据只含 App.Tests）；Host E2E 为 skip。

## 8. 处置建议（按优先级）

1. **R-001（P1，阻塞）**：修 `P16ExportRuntime` 的发布路径——`_publish_and_mark` 必须使用 `_export` 传入的重命名目标（或 `_resolved_target.path`）并更新 publication_intent/history；Host 侧强制 `replace_existing=false`；补「既有目标 + AUTO_RENAME」runner 测试（旧 bytes 不变、`(1)` 存在、completed）。
2. **R-004（P2）**：Host policy→mint 原子化/二次校验；补 TOCTOU 负例；修正 README 的「typed 拒绝」表述。
3. **R-002/R-003（P2）**：补 HostController 接线测试；补 AC4 完成数/完成文件断言或改 AC 措辞；同步卡面 AC2/AC4 的 `<<MET>>` 与 README。
4. **P3**：R-005 当前页未定位提示；R-006 m2 acceptance/日志说明；R-007 统一 README base/head、刷新日志/填 delivery_head/Canonical commit；R-008 完成态路径去重；R-009 mtime/边界测试。
5. 修后重跑本报告 §5 门禁并在新 head 重做 r2。

## 9. 审查者声明

本报告由未参与 FEA-14-EXPORT-1 实现/返修的独立上下文子 agent 出具；只读审查，唯一写入为本文件。PASS 均基于本审查实测或逐行静态核对；未实测项已在 §7 记 NOT_RUN；R-001 的仓外探针仅用于验证 runner 发布路径，不被当作产品 E2E PASS。
