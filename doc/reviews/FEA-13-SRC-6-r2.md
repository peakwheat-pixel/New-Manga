---
task_id: FEA-13-SRC-6
reviewer: DSH 派发的独立上下文子代理（fresh；未参与 FEA-13-SRC-6 实现/返修）
reviewer_kind: subagent
author: dsh
base_commit: 1a8bb1235
reviewed_head: cc042df4b
previous_review: doc/reviews/FEA-13-SRC-6-r1.md
decision: changes_requested
---

# FEA-13-SRC-6 r2 复审（只读）

- **被审 head**：`cc042df4bb33b83343de5a11ead7d0dd0ac78a40`（`main`）
- **base**：`1a8bb1235`；前序 r1（`14b0842e7`，changes_requested：P0=0/P1=5/P2=8/P3=7）
- **审查性质**：只读 r1 复核；仅写本文件。未改源码/测试/契约/卡，未 commit / push。
- **工作树**：写本文件前 `git status --short` 为空。
- **结论**：**`changes_requested`**；**CLEARED FOR DONE：否**。

## 一句话结论

r1 的 3 项 P1 已真正修好（R-002 去 wire、R-004 显式 force、R-005 MA 如实登记），但**修复提交把定向 pytest 门禁打红**（`report["source_access_handoff"]` 已删、测试未同步 → `KeyError`），且**启动补导入缺少 read-only 守卫**（scope §2.4.4 / AC4 明示要求跳过，现在 read-only 模式会写生产 registry）。卡面 AC1/AC4/AC5/AC6 的 `<<MET>>` 仍不能采信。

## r1 findings 逐条判定（20 项）

| ID | r1 级别 | r2 判定 | 依据（本 head 实测） |
|---|---|---|---|
| R-001 启动补导入接线 | P1 | **PARTIAL** | 已接线：`HostRuntime.cs:1283-1293` 在 `Registry` 创建后调用 `ImportPendingSourceAccessHandoffs()`，内层 `catch (Exception)` 只记 warn 不阻断启动（符合）。**但缺 `Policy.WritesAllowed` 守卫**：`_policy` 在 `:897` 已按模式解析，read-only 时 `WritesAllowed=false`，`:1288` 仍无条件导入 → `ImportRestoredSnapshot`→`Save` 写 live registry。见 N-002。 |
| R-002 wire 出参 | P1 | **FIXED** | `nmbak.py:436` 只调用 `_write_source_access_handoff(...)`，不再赋 `report[...]`；`git diff 1a8bb1235..cc042df4b -- src/infrastructure/sqlite/nmbak.py` 中 `report` 仅剩注释行，**0 新增/删除键**；`src/bootstrap/core_service.py` 不在 diff。**但**测试未同步 → N-001。 |
| R-003 AC5 分类 | P1 | **PARTIAL** | 分类已实现：`CryptographicException→dpapi_unprotectable`、`NotSupportedException→registry_version_unsupported`、其余→`registry_corrupt`（`SourceAccessRegistry.cs:230-242`）；`NMSAR2` 有测试 `UnsupportedSnapshotVersionIsRejectedDistinctly`。**缺口**：DPAPI 用例（`ForeignDpapiSnapshotIsRejectedWithZeroWrites`）仍只断言 Code，不断言 `Reason=dpapi_unprotectable`；`registry_corrupt` 无任何测试（截断测试走 sha 前置 → `handoff_corrupt`）；identity 负例仍缺。 |
| R-004 receipt 阻断显式再恢复 | P1 | **FIXED** | `TryImportFromHandoff(..., bool force=false)`；显式路径 `HostRuntime.ImportSourceAccessHandoff`（`:430-431`）传 `force: true`；启动扫描 `TryImportPending` 不传 force → 仍受 receipt 保护；新测试 `ExplicitForceReimportsAfterAReceipt`。残余（非阻断）：测试未覆盖「导入→`Reset(true)`→显式 restore 重新 imported」，只验证 receipt 被绕过后 `Unchanged=1`。 |
| R-005 MA 变异如实登记 | P1 | **FIXED** | `README.md:34` 改「**无效（NOT RED，EXIT 0）**」并写明不得据此声称判别力；`mutations/MA-*.log` 记 `DLL_EXISTS=True`、`EXIT=0`、1 passed（变异未被执行/不可判别），与原假 RED 不同，属如实登记。 |
| R-006 幂等语义 | P2 | **PARTIAL** | 同代次 → `Unchanged`（`SourceAccessRegistry.cs:265-271`），revoked（live 或候选）→ `Conflicts`（`:260-263`），且有测试断言 `Unchanged=1/Conflicts=0`。**但**「同代次但 roots 不同」也计 `unchanged`，而 scope §2.4 合并表要求「generation/roots/revoked_at 任一不同 → conflict」。见 N-003。 |
| R-007 receipt 位置/私有 ACL | P2 | **OPEN** | receipt 仍写 `<backup_root>/restore-handoff/<id>/import-receipt.json`（`SourceAccessRestore.cs:33,165-172`），未迁 `<DataRoot>/host/source-access/imports/`，无 `SourceSecurity.PrivateDirectory`。 |
| R-008 AC1「grep DPAPI = 0」 | P2 | **OPEN** | 卡面 AC1（`doc/tasks/FEA-13-SRC-6.md:85`）仍写 `grep CryptProtectData\|CryptUnprotectData src/ = 0` 且 `<<MET>>`；`rg` 实测仍 4 命中（`src/application/importing/referenced/secrets.py`，非本卡引入）。未修口径、未如实登记。 |
| R-009 handoff.json 写失败未 typed | P2 | **OPEN** | `nmbak.py` 中 `(handoff_root / "handoff.json").write_text(...)` 仍在 `try/except OSError` 之外（copy/digest 在 try 内），写失败 → 裸 `OSError` → `E_UNKNOWN` 而非 `BACKUP_RESTORE_INCOMPLETE`。 |
| R-010 rejected 不写 receipt | P2 | **OPEN** | `WriteReceipt` 仅在成功分支（`:125`）；`rejected`（含 `dpapi_unprotectable`、`handoff_corrupt`）不写 receipt → 每次启动重试并重记日志。 |
| R-011 变异「复原后绿」 | P2 | **OPEN** | `mutations/` 仍只有 3 条 RED/无效运行，无任何「还原 → 全绿」日志与 `EXIT=0` 复原证据（AC6 明示要求）。 |
| R-012 测试缺口 | P2 | **PARTIAL** | 新增 2 个 Host 测试（force 重导入、NMSAR2）。仍无：`Authorize` 成功、第二 DataRoot 完整 restore+import e2e（`RestoreBackupAsync` 集成，含「导入拒绝不反向失败」）、read-only 零写、identity（`SOURCE_REGISTRY_UNAVAILABLE`）、`dpapi_unprotectable`/`registry_corrupt` reason 断言、live 新代次冲突、包内 revoked 导入为 revoked、空 live 首次导入恰好一次、AC3 重复导入字节/mtime。 |
| R-013 reparse 祖先检查 | P3 | **OPEN** | `_crosses_reparse_point(directory, Path(SOURCE_ACCESS_FILE))` 仍从 `host/source-access` 目录起算，未检 `data_root/host`、`host/source-access` 目录自身为 junction。 |
| R-014 排序 | P3 | **OPEN** | `TryImportPending` 仍 `OrderBy(item => item, StringComparer.Ordinal)`（目录名），未按 `handoff.json.created_at`。 |
| R-015 死 API `Contains` | P3 | **OPEN** | `SourceAccessRegistry.Contains` 仍存在且无调用点（`rg` 0 命中）。 |
| R-016 Host 导入无 catch-all | P3 | **OPEN** | `RestoreBackupAsync`（`:409-419`）仍直接调用 `ImportSourceAccessHandoff`，无 try/catch；`TryImportFromHandoff` 的 catch 仍未覆盖 `ArgumentException`/`SecurityException` 等。 |
| R-017 handoff 无清理 | P3 | **OPEN** | 全仓无删除/轮转 `restore-handoff/**` 的路径。 |
| R-018 base/STATUS 同步 | P3 | **PARTIAL** | 卡面 `base_commit: 1a8bb1235` 已改对；`doc/STATUS.md:7` 仍写「**in_progress**（Core 侧已落；**Host 导入待补**）」，与 head（Host 导入 + 接线均已落）不符。 |
| R-019 卡面登记生命周期豁免 | P3 | **OPEN** | 卡面 allowed_paths 未补生命周期指针豁免说明。 |
| R-020 member 校验 / AC2(a) 字节断言 | P3 | **OPEN** | `SourceAccessRestore` 只校验 `Member` 非空，未校验 `== extras/source-access/registry.v1.dat`；`test_unreadable_registry_fails_the_create` 仍只断言无 `.nmbak`，未断言 registry 字节不变。 |

**计数**：FIXED **3**（R-002、R-004、R-005）；PARTIAL **5**（R-001、R-003、R-006、R-012、R-018）；OPEN **12**（R-007、R-008、R-009、R-010、R-011、R-013、R-014、R-015、R-016、R-017、R-019、R-020）。

**OPEN 列表**：R-007、R-008、R-009、R-010、R-011、R-013、R-014、R-015、R-016、R-017、R-019、R-020。

## 新增 findings（r2）

| ID | 级别 | 位置 | 触发与影响 | 复现证据 | 建议 |
|---|---|---|---|---|---|
| N-001 | **P0** | `tests/storage/test_nmbak_source_access.py:185`；`verification/FEA-13-SRC-6/logs/*` | 修复提交删除了 `report["source_access_handoff"]`，但该测试仍断言此键 → `KeyError`，**HEAD 定向门禁 RED**；AC6/卡面「0 failed」不成立。同时修复提交新增/提交的证据日志是**修复前**产物（`pytest-src6.log` 01:52 7 passed、`pytest-full.log` 01:57:55 3475 passed、`dotnet-*.Tests.log` Host 319 passed 对应旧 7 测试，HEAD 实为 9 测试），不能作为本 head 的门禁证据 | 实跑 `python -m pytest tests/storage/test_nmbak_source_access.py tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_coverage.py -q` → `1 failed, 35 passed`，**EXIT 1**，失败原文 `KeyError: 'source_access_handoff'`（`tests\storage\test_nmbak_source_access.py:185`）；`dotnet test --filter FullyQualifiedName~SourceAccessRestoreTests` → 9 passed EXIT 0 |
| N-002 | **P1** | `HostRuntime.cs:1283-1293`（接线点） | 启动补导入无 `Policy.WritesAllowed` 守卫。read-only 模式（legacy shell / parity 未达 / self-check 失败）下 `:897` 已置 `WritesAllowed=false`，`:1288` 仍执行导入 → `ImportRestoredSnapshot` 在**只读模式写生产 registry**，直接违反 scope §2.4.4「read-only 模式下跳过自动导入（不写 registry，只记录 pending）」与 AC4「read-only 模式零写」；该 AC 在 README 仍记 PASS | 代码路径 `ImportPendingSourceAccessHandoffs` → `TryImportPending` → `TryImportFromHandoff` → `ImportRestoredSnapshot` → `Save`，全链无 policy 检查；`rg "WritesAllowed"` 在 `SourceAccessRestore.cs`/`SourceAccessRegistry.cs` 0 命中；无 read-only 测试 |
| N-003 | P2 | `SourceAccessRegistry.cs:265-271` | 同 `registry_id`、同 generation 但 **roots 不同** 的候选被计 `unchanged`，而 scope §2.4 合并表要求该情形为 `conflict`（「generation/roots/revoked_at 任一不同 → conflict，保留 live」）。不写 live 本身安全，但 outcome 计数与冻结语义不符，调用方无法区分「完全相同」与「同代次不同内容」 | 代码仅比较 `liveEntry.Generation == entry.Generation` 即 `unchanged++`，无字段相等比较；无对应测试 | 先判字段完全相同 → `unchanged`，否则 `conflict`；补同代次不同 roots 测试 |
| N-004 | P3 | `verification/FEA-13-SRC-6/README.md:16-17` | 证据 README 与卡面 AC 互相矛盾且仍过度声明：AC5 行写「截断 → `handoff_corrupt`」，卡面 AC5 要求「截断 → `registry_corrupt`」；AC6 行仍写「≥3 变异 RED」而同一 README 的 MA 行已登记「无效（NOT RED）」 | README 行 16/17 与 34 自相矛盾；卡面行 89/90 | AC5 行改为实际判据（sha 前置 → `handoff_corrupt`，`registry_corrupt` 未测/未达）；AC6 行改为「2 RED + 1 无效」并登记无复原绿 |

**新增计数**：**P0=1、P1=1、P2=1、P3=1**（合计 4）。

## AC 复核（以本 head 实跑为准）

| AC | 卡面 | r2 判定 | 理由 |
|---|---|---|---|
| AC1 | MET | **PARTIAL** | 逐字节/manifest sha/size/源字节+mtime 有测试；「grep = 0」仍假（R-008），「无明文」探针用合成 payload（判别力弱，R-012 未变）。 |
| AC2 | MET | **PARTIAL** | (a)(b)(c) 有测试；但 (a) 缺「源 registry 字节不变」断言，(c) Host 侧 `unchanged` 零写无单测（R-020）。 |
| AC3 | MET | **PARTIAL** | Python 侧 handoff 落盘正例；Host 侧 `List()` 正例。仍无 `Authorize` 成功、第二 DataRoot 完整 e2e、`RestoreBackupAsync` 集成（导入拒绝不反向失败）测试（R-012）。 |
| AC4 | MET | **PARTIAL** | receipt 防启动复活、force 显式重导入已实现；`read-only 模式零写` **未实现且现在会被启动接线写入**（N-002）；live 新代次冲突、包内 revoked 导入无测。 |
| AC5 | MET: simulated | **PARTIAL** | 三个 reason 分类已实现；`dpapi_unprotectable` 无断言、`registry_corrupt` 无测试、identity 负例缺失；README 截断 reason 与 AC 不符（N-004）。真实跨机 `NOT_RUN` 口径正确。 |
| AC6 | MET | **NOT MET** | 定向 pytest 门禁 **EXIT 1**（N-001）；提交的证据日志为修复前产物；无「复原后绿」；MA 变异无效（如实登记但 AC 的「≥3 判别变异」未满足）。scope/pin/contract 部分成立（见下）。 |

## 门禁实测（本 head，2026-11-10）

| # | 命令 | 结果 |
|---|---|---|
| G1 | `python -m pytest tests/storage/test_nmbak_source_access.py tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_coverage.py -q` | **FAIL**：`1 failed, 35 passed`，**EXIT 1**（`KeyError: 'source_access_handoff'`，`test_nmbak_source_access.py:185`） |
| G2 | `dotnet test tests/NewManga.Host.Tests/... --filter "FullyQualifiedName~SourceAccessRestoreTests"` | **PASS**：9 passed / 0 failed，**EXIT 0**（新 2 例通过） |
| G3 | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)**，**EXIT 0** |
| G4 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-13-SRC-6.md` | **PASS**，选中本卡，**EXIT 0** |
| G5 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (18/18)**，**EXIT 0**；C09 `dc51226b…`、C17 `cdeee487…` 等均 OK |
| G6 | `git status --short` | 写本文件前**空** |

## 范围 / 契约边界（实测）

- `git diff --name-only 1a8bb1235..cc042df4b` = 30 文件：4 生产/测试（`HostRuntime.cs`、`SourceAccessRegistry.cs`、`SourceAccessRestore.cs`、`SourceAccessRestoreTests.cs`）+ 卡面 + `doc/reviews/FEA-13-SRC-6-r1.md`（glob `doc/reviews/FEA-13-SRC-6-*.md`）+ `nmbak.py` + `test_nmbak_source_access.py` + `verification/FEA-13-SRC-6/**`（16 文件）→ **⊆ 14 allowed_paths**。
- 卡外 3 文件仅 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`，属 scope r1 §2.6 明示的生命周期指针豁免，不判越界。
- `git diff 1a8bb1235..cc042df4b -- doc/contracts doc/plan` = **空**；C-06/C-09/C-17 零字节；18 pins 零变化；0 DDL / 0 新命令 / 0 新错误码 / **0 新 wire**（R-002 已消除）。
- 新增行为均落在既有码：`dpapi_unprotectable` 等 reason 是字符串而非新错误码。

## 结论与下一步

- **Architecture**：四段交接与 DPAPI 边界仍正确；`backup.restore` 出参已回归基线；显式/启动两条导入路径已分开（force vs receipt）。**两处必须修**：read-only 守卫（N-002）与门禁回红（N-001）。
- **Verification**：门禁未能全绿；证据日志滞后于被审代码，不能作为 AC6 的 `<<MET>>` 依据。
- **决定**：对 `cc042df4b` **不可批准**，Task **不得进入 done**。最小收敛路径：
  1. 更新 `test_nmbak_source_access.py`（删/改 `:185` 对已移除 wire 字段的断言，改为断言 handoff 文件 + `report` 形状不变），重跑定向 pytest 至 EXIT 0；
  2. 启动导入加 `if (!Policy.WritesAllowed) { 记录 pending; return; }`（或等价），补 read-only 零写测试；
  3. 重生成并提交本 head 的证据日志（pytest/dotnet 9 例/门禁），移除或明确标注修复前日志；
  4. 可选（不阻断）：R-006 字段相等判定（N-003）、README AC5/AC6 措辞（N-004）、R-007/R-010/R-012 的其余项。
