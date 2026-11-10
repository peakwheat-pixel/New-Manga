---
task_id: FEA-14-EXPORT-1
reviewer: fresh 独立上下文子 agent（续接 r1/r2；未参与本卡实现/返修）
reviewer_kind: subagent
author: dsh
base_commit: 22683068e
reviewed_head: 0720686a6
decision: approved
---

# Review：FEA-14-EXPORT-1（r2 处置后轻量复核，r3）

## 0. 审查对象与环境

- 仓库 `G:\CODEX\New Manga`，`main`；**HEAD = `0720686a656cafbb35d668100dee07eaf63c4734`**。审查开始 `2026-11-10T11:31:38+08:00`、结束 `11:39:13+08:00`，两次 `git status --short` 均 **clean**，HEAD 不变。
- 增量：`22683068e..0720686a6`，**9 文件**：`src/infrastructure/export/target_refs.py`（新增 `publish_to`）、`src/application/export/service.py`（`_publish_to` sibling 分支改调用）、`ImportExportPanels.cs`（R2-005 回退 SelectedIndex）、`ImportExportUiTests.cs`（2 个新测试）、卡面、README、`logs/dotnet-app-tests.log`、`logs/pytest-full.log`、r2 报告入库。
- 范围：9 文件逐项匹配卡面 allowed_paths **OUT=0**（`target_refs.py` 已在 allowed 新增）；无 `IHostController.cs`/`schema.py`/`doc/contracts/**`/`doc/plan/**` 改动。
- 只读纪律：仅写本文件；未改源码/测试/契约/卡面/证据，未 commit/push。r3 探针与日志只写仓外 `G:\CODEX\New Manga.workspace\temp\FEA-14-EXPORT-1-r3\`。

## 1. 结论

**`approved`**（P0=0 / P1=0 / **P2=0** / **P3=5**；AC4 按新口径为 PARTIAL——mtime/snapshot 未单独断言；其余 AC 见 §4）。

r2 的 P2 残余已实质关闭：R2-001 的 `publish_to` 恢复 resolve/reparse/父目录一致/不存在/非 symlink/发布后 entry 校验，r1 探针与「published 在授权父目录外」负例均实测通过；R2-002 的 title/Scope §4/AC4/README 口径已一致；R2-005 两个新测试真实运行并通过。定向 29/0、全量 App 867/0/11、全量 pytest 3477/0/10、门禁全绿。

## 2. r2 findings 关闭判定

| r2 ID | r2 级别 | r3 判定 | 依据 |
|---|---|---|---|
| R2-001 | P2 | **CLOSED（P3 残余）** | `target_refs.py:92-111` 新增 `publish_to`：`authorized_parent = self.path.parent.resolve(strict=True)` + `_reject_reparse_components`；`published.parent.resolve` 后 `_normalized_path` 与授权父目录一致；`published.exists()/is_symlink()` 拒绝；`os.replace` 后 `_validate_published_entry(published, authorized_parent)`。`service.py:768-780` sibling 分支改为 `target.publish_to(temp, final_path)`，不再自行做弱检查。**仓外探针**：①默认 AUTO_RENAME + mint target 存在 + `replace_existing=True` + `P16ExportRuntime.start` → `status: completed`、旧 target=`OLD-USER-FILE`、`book (1).zip` exists=True、snapshot/history output=`book (1).zip`；②published 位于授权父目录外 → `REF_SCOPE_DENIED`、未创建；③published 已存在 → `REF_SCOPE_DENIED`、旧文件不变。残余：无父目录 handle（resolve→replace 的极小 TOCTOU 已由 R2-003 登记）、resolve 失败抛 OSError 而非 typed REF 码、仓库内无 `publish_to` 负例测试（探针为仓外） |
| R2-002 | P2 | **CLOSED（P3 残余）** | 卡 title（`:3`）与 Scope §4（`:66`）已改「取消保护」；AC4（`:105`）与 README `:15/:22` 同口径；无「完成数」残留表述（仅历史 r1 处置记录 `:81` 保留旧措辞）。残余：卡面「背景与现状」`:59` 仍写旧「取消保留已成功文件」缺口措辞；AC4 声称的 mtime/snapshot 仍无单独断言（R3-001/R3-002） |
| R2-003 | P3 | **CLOSED（登记）** | `publish_to` 的 `exists/is_symlink → os.replace` 仍是检查-替换窗口；README `:24` 已登记「极小 TOCTOU、未压测」，不冒充已消除 |
| R2-004 | P3 | **CLOSED（登记）** | 源码顺序测试 `ImportExportUiTests.cs:634+` 仍依赖精确字符串；README `:25` 已登记脆弱性，可接受为接线守卫 |
| R2-005 | P3 | **CLOSED** | `ImportExportPanels.cs:505-510` 当前页未定位时设 `SelectedIndex=1` + 提示；`ImportExportUiTests.cs:487` 断言回退与「当前页未定位」；`:508` 完成后断言 OutputPath 只出现一次（`CountOccurrences==1`）。定向 dotnet 29/0 实际运行 |
| R2-006 | P3 | **CLOSED（登记）** | README `:26` 记录 logs HEAD 为提交前 head、`delivery_head`/Canonical commit 收口时填；卡面 `Canonical Evidence` 7 行 hash 全部与文件匹配（实测），但 EV-EX1-003 仍指向 27 条日志（见 R3-004） |
| R2-007 | P3 | **CLOSED（登记）** | 真实 Host+Core E2E 仍 NOT_RUN（env 实测为空）；README `:27`/NOT_RUN 节保留 |

## 3. R3 Findings（均为 P3，不阻断）

| ID | 级别 | 位置 | 事实与影响 | 建议 |
|---|---|---|---|---|
| R3-001 | P3 | `src/infrastructure/export/target_refs.py:92-111`；`src/application/export/service.py:768-780` | `publish_to` 恢复了 resolve/reparse/父目录一致/不存在/symlink 拒绝/发布后校验，但**没有像 `hold_parent` 一样持有父目录 handle**：`resolve`→`os.replace` 之间父目录被 junction/symlink 替换的窗口仍存在（R2-003 已登记「极小 TOCTOU」）；`resolve(strict=True)` 在父目录消失时抛 OSError 而非 `REF_SCOPE_DENIED` typed 码；仓库内无 `publish_to` 负例测试（仓外探针已覆盖 outside/existing 两个负例）。 | 如需完全闭合，复用 `hold_parent` 的 Windows 父句柄/不可删除共享或把 OSError 映射为 typed REF_SCOPE_DENIED；把探针的 2 个负例落入 repo 测试（P3） |
| R3-002 | P3 | 卡 `:59`；AC4 `:105`；README `:15`；`tests/reading_export/test_export.py:315-330` | AC4/README 口径已一致，但**测试仍未断言 mtime 与 `P16ExportRuntime` cancelled snapshot**（AC4 文本含二者）；卡面「背景与现状」`:59` 仍写旧「取消保留已成功文件」缺口措辞（非历史 r1 记录）。 | 补 cancel 的 mtime/snapshot 断言；把 `:59` 改为「取消保护」口径 |
| R3-003 | P3 | `verification/FEA-14-EXPORT-1/README.md:17`、`:45-47`；`logs/dotnet-export-tests.log`；卡 `Canonical Evidence` EV-EX1-003 | **证据/README 内部不一致**：README AC6 行仍写「定向 27/0；App 865/0/11」，而同一 README 门禁表已写「29 passed；867/0/11」；`logs/dotnet-export-tests.log` 只有 26/27 两条 run（无 29），卡面 EV-EX1-003 hash 仍对应 27 日志；本审查实测 29/0 通过，但证据文件未刷新。 | 重跑 29 定向并把 `dotnet-export-tests.log` 更新；同步 README AC6 行与 Canonical EV-EX1-003 hash |
| R3-004 | P3 | `doc/tasks/FEA-14-EXPORT-1.md:137-143` | `Canonical Evidence` 的 commit 列仍为 `-`、`delivery_head:null`；logs 头部 HEAD 为生成时（r2 修复前 base）而非最终 head；`gates-check.log`/`gates-pins.log` 仍为旧字节数（README 已注）。 | 收口提交填 `delivery_head`/Canonical commit；在交付 head 重生成 logs 或记录父 HEAD+diff hash |
| R3-005 | P3 | `apps/desktop-avalonia/tests/NewManga.App.Tests/ImportExportUiTests.cs:634+`；`ExportE2ETests.cs:147` | R2-002 源码顺序断言仍为精确字符串匹配；真实 Host+Core E2E 仍 NOT_RUN，且 `ExportE2ETests` 直接调用 `runtime.Grants.StartExportAsync`，即使 env 存在也不覆盖 HostController policy→mint 接线；无 HostController 行为测试。 | 保持 NOT_RUN；另建可注入 grants 的 HostController 行为测试（P3） |

## 4. AC 逐项（r3 后）

| AC | 状态 | 依据 |
|---|---|---|
| AC1 默认不覆盖 | **MET** | direct 测试 + runner 测试 + 仓外探针：旧 target 不变、`(1)` 生成、snapshot/history completed；R2-001 `publish_to` 恢复父目录授权 |
| AC2 Host 冲突计划 | **MET（E2E NOT_RUN）** | Host 源码顺序测试 + `ExportPathPolicyTests` 4 项；真实 Host+C E2E 仍 NOT_RUN（已声明） |
| AC3 scope 三档与顺序预览 | **MET（带 limitation）** | 3 项 UI 测试 + R2-005 当前页未定位提示测试；当前页/已选页/整章与预览一致 |
| AC4 取消保护 | **PARTIAL（P3）** | 取消不发布/旧目标 bytes/history cancelled 有测试；AC4 文本的 mtime 与 snapshot cancelled 未单独断言（R3-002） |
| AC5 零 wire/零 DDL/旧签名 | **MET** | 增量无 `IHostController.cs`/`schema.py`/契约；`--check` 1/54/6=61 EXIT 0；pins 18/18 |
| AC6 门禁与证据 | **MET（P3 provenance）** | 定向 29/0、App 867/0/11、pytest 3477/0/10、check/pins/API 全绿；README AC6 行与 `dotnet-export-tests.log` 仍滞后（R3-003） |

## 5. 门禁实测（命令 + 时点 + EXIT）

| # | 命令 | 时点（+08:00） | 结果 | EXIT |
|---|---|---|---|---|
| 1 | `dotnet test .../NewManga.App.Tests.csproj --filter "FullyQualifiedName~ImportExportUiTests\|~PdfExportUiTests\|~ExportStalePolicyTests\|~ExportPathPolicyTests"` | 11:32:09 → 11:32:18 | **29 通过 / 0 失败** | **0** |
| 2 | `python -m pytest tests/reading_export tests/core/test_p16_reader_export.py tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py -q` | 11:32:19 → 11:32:51 | **177 passed** | **0** |
| 3 | `pwsh -NoProfile -File tools/governance/check.ps1` | 11:33:02 → 11:33:04 | PASS（3 warnings：11 非终态 / STATUS 3181 B·31 L / PLAN 6857 B·64 L） | **0** |
| 3b | `... check.ps1 -TaskPath doc/tasks/FEA-14-EXPORT-1.md` | 11:33:02 → 11:33:04 | PASS（同上） | **0** |
| 4 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 11:33:04 → 11:33:05 | **PIN AUDIT: PASS (all 18)** | **0** |
| 5 | `python tools/generate_api_inventory.py --check` | 11:33:05 | `OK: rendered counts match`；1/54/6 = 61 | **0** |
| 6 | `dotnet test .../NewManga.App.Tests.csproj`（全量） | 11:33:32 → 11:38:34（4 m 59 s） | **867 通过 / 0 失败 / 11 跳过 / 878 总计** | **0** |
| 7 | `python -m pytest -q`（全量） | 11:33:32 → 11:37:54（4 m 20 s） | **3477 passed / 10 skipped** | **0** |
| 8 | `git status --short` + `git rev-parse HEAD`（开始/结束） | 11:31:38 / 11:39:13 | 两次均 **clean**；HEAD 均 `0720686a6…` | — |
| 9 | 仓外探针 `python ...\probe_r3.py`（R2-001 成功 + outside/existing 负例） | 11:33:18 | 成功：completed/旧 target 不变/`(1)` 存在；outside→`REF_SCOPE_DENIED` 且未创建；existing→`REF_SCOPE_DENIED` 且旧文件不变 | 0 |

探针日志：`G:\CODEX\New Manga.workspace\temp\FEA-14-EXPORT-1-r3\probe-r3.log`（脚本 `probe_r3.py`；仓外运行，不改仓库）。

## 6. 范围与证据复核

- 增量 9 文件全部匹配卡面 allowed_paths（OUT=0）：`target_refs.py` 已在 allowed；无 `IHostController.cs`/`schema.py`/契约/DDL 改动；pins 18/18、API 61。
- `Canonical Evidence` 7 个 sha256 与当前文件逐一匹配；但 EV-EX1-003 对应日志仍只有 26/27 两次 run（29 未落日志，R3-003）；`dotnet-app-tests.log` 已含 867、`pytest-full.log` 已含 3477。
- NOT_RUN：真实 Host+Core sidecar E2E（env 为空、ExportE2ETests 绕过 HostController 且 skip）、真实 UI 截图/人工目视、阅读器多选、`publish_to` 并发压力（TOCTOU 已登记）——均如实，不冒充 PASS。

## 7. 处置建议（P3，不阻塞本次 approved）

1. R3-003：重跑 29 定向更新 `logs/dotnet-export-tests.log`，同步 README AC6 行（27/865→29/867）与 Canonical EV-EX1-003 hash。
2. R3-002：补 cancel 的 mtime/snapshot 断言；卡面 `:59` 旧措辞改「取消保护」。
3. R3-001：如要求完全闭合，`publish_to` 增加父目录 handle/把 OSError 映射 typed REF，并把 outside/existing 负例落入 repo 测试。
4. R3-004/R3-005：收口时填 `delivery_head`/Canonical commit、重生成/注明 logs；E2E 保持 NOT_RUN，另建 HostController 行为测试。

## 8. 审查者声明

本报告由未参与 FEA-14-EXPORT-1 实现/返修的独立上下文子 agent 出具（续接 r1/r2；历史报告为本审查者前两轮产出，不构成对实现的参与）。只读审查，唯一写入为本文件；PASS 均基于本次实测或逐行静态核对，未实测项已在 §6 记 NOT_RUN；仓外探针不当作产品 E2E PASS。
