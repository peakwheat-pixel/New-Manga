---
task_id: FEA-13-SRC-6
reviewer: DSH 派发的独立上下文子代理（fresh；未参与 FEA-13-SRC-6 实现/返修）
reviewer_kind: subagent
author: dsh
base_commit: 1a8bb1235
reviewed_head: 14b0842e7
decision: changes_requested
---

# Review：FEA-13-SRC-6（SC-B01 ④ 源授权元数据入包 · C-09 SC-B07 ④）

- **被审 head**：`14b0842e75f260cf97e499edb6f02773dcf16c96`（`main`）
- **base**：`1a8bb1235`（卡面 `base_commit` 仍写 `07545adf1`，见 R-018）
- **审查性质**：只读实现 Review；仅写本文件。未改源码/测试/契约/卡，未 commit / push。
- **审查时工作树**：写本文件前 `git status --short` 为空。写报告期间出现并发产物 `?? verification/FEA-13-SRC-6/logs/pytest-full.log`（01:57:55 创建，`python -m pytest -q` full，EXIT 0；非本 Review 写入，未采信为审查证据）。
- **结论**：**`changes_requested`**（5×P1；AC3–AC6 均未达到卡面声称的完整 MET）

## 范围与依据

- 卡：`doc/tasks/FEA-13-SRC-6.md`（14 allowed_paths / 6 AC，全部 `<<MET>>`）；scope：`doc/reviews/FEA-13-SRC-6-scope-r1.md`（READY-TO-FREEZE）。
- 契约：C-09 `SC-B01`/`SC-B01a`/`SC-B07 ④`；C-06/C-17 声称零改动；C-15 为设计输入。
- diff：`git diff 1a8bb1235..14b0842e7`（20 files，+1227/−39）；被审 3 commits：`f85c6ddb3`（Core）、`868e62f18`（Host）、`14b0842e7`（证据/卡面）。
- 未审：真实跨机 DPAPI（本机不可构造，`NOT_RUN` 口径正确）；未重跑全量 Host 319 例（仅复核日志）。

## Architecture

- 四段交接（Host registry 密文 → Core 只读复制 → 包内 `extras/source-access/` → Core restore 后 handoff → Host 解密合并）与 scope §2.1 一致；Core 路径确实不解密/不解析（`nmbak.py` 无新增 DPAPI 调用）。
- **但 `backup.restore` 结果新增了 `source_access_handoff` 字段**（`nmbak.py:438`；`core_service.py:3211` 直接 `return report` 作为 wire `result`），与冻结 scope「不改 `backup.restore` 出参；Host 用 `backup_id` 推导 handoff 路径」及 AC6「0 新 wire」直接冲突（R-002）。
- **启动补导入未接线**：`HostRuntime.ImportPendingSourceAccessHandoffs()`（`HostRuntime.cs:440`）无任何调用点；`HostRuntime.cs:1271` 创建 `Registry` 后没有补导入。冻结 scope §2.4.4 / AC3/AC4 的「Host 启动补导入 + read-only 跳过」实际不存在（R-001）。
- Host 合并只新增缺失 `registry_id`、`Save` 原子替换、失败 live 零写，主路径正确；receipt 位置/语义与 scope 有偏差（R-004、R-007）。
- 无 DDL、无新命令、无新错误码；`HostErrorCodes.cs`、`CoreServiceClient.cs`、`restore_plan.py`、`doc/plan/**` 零改动。

## Spec（AC 判定）

| AC | 判定 | 说明 |
|---|---|---|
| AC1 入包段/加密不可读 | **PARTIAL** | 逐字节、`NMSAR1\0`、manifest sha/size、源字节+mtime 不变均实现并有测试；但 AC 末句「`grep CryptProtectData\|CryptUnprotectData src/` = 0」**不成立**（`src/application/importing/referenced/secrets.py:43,52,70` 有 4 处既有 `CryptUnprotectData`，非本卡引入），且「无明文」断言使用合成 payload，判别力空转（R-008、R-012）。 |
| AC2 缺失/不可读/空边界 | **MET**（带测试缺口） | (a) 读失败 → `BACKUP_CREATE_FAILED`、无包；(b) 缺失 → 无段、restore 无 handoff、Host `not_present`；(c) 空 entries 文件 → 有成员。仅 (c) 的 Host 侧 `unchanged` 零写未单测（R-012）。 |
| AC3 恢复后授权可用 | **PARTIAL** | `List()` 正例有测；`Authorize` 成功、第二 DataRoot overwrite e2e、导入拒绝不反向失败 restore 均无测试。重复导入 `unchanged` 是 **receipt 短路**（`SourceAccessRestore.cs:69-72`）而非合并幂等；合并层同代次相同条目被计为 `Conflicts` 而非 `Unchanged`（R-006、R-012）。 |
| AC4 revoked/代次/冲突 | **PARTIAL** | live revoked 优先、reset+receipt 不复活有单测；live 新代次冲突、包内 revoked 导入为 revoked 无测；**启动 `TryImportPending` 未接线**（生产不执行）；read-only 零写未实现/未测；显式再次 restore 因 receipt 短路无法重新导入（R-001、R-004、R-012）。 |
| AC5 跨机/版本/identity 负例 | **PARTIAL** | simulated DPAPI 拒绝为 `rejected`/`SOURCE_ACCESS_DENIED`/零写，但 Reason = `registry_corrupt_or_unprotectable`，不是 AC 要求的 `dpapi_unprotectable`；`registry_version_unsupported`、`registry_corrupt` 无实现路径，`NMSAR2`/identity 无测试；README 却写「`dpapi_unprotectable` PASS」。真实跨机 `NOT_RUN` 口径正确（R-003）。 |
| AC6 门禁/证据/变异 | **PARTIAL** | 门禁实测全绿；但 diff 含 3 个卡外生命周期文档（scope §2.6 已豁免，P3）；「0 新 wire」假；变异 MA 为**假 RED**（测试 DLL 不存在），三条变异均无「复原后绿」（R-002、R-005、R-011）。 |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-001 | P1 | `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs:440`（定义）/`:1271`（Registry 创建） | 启动补导入 `ImportPendingSourceAccessHandoffs()` 无调用点：Core restore 成功后 Host 崩溃/重启，handoff 永不导入，用户授权不恢复；冻结 scope §2.4.4 与 AC3/AC4 的启动路径缺失，read-only 跳过也无从实现 | `rg -n "ImportPendingSourceAccessHandoffs" apps/desktop-avalonia/src` 仅命中定义；启动块 1260–1294 无调用 | 在 `Registry` 创建成功后、`Policy.WritesAllowed` 为真时调用；失败仅记日志不阻断启动；read-only 只记录 pending | open |
| R-002 | P1 | `src/infrastructure/sqlite/nmbak.py:438`；`src/bootstrap/core_service.py:3211` | `report["source_access_handoff"]` 随 `backup.restore` 的 wire `result` 直接出网，新增出参；违反冻结口径「不改 `backup.restore` 出参」、scope §1.7 U1 与 AC6「0 新 wire 字段」；Host 实际只用 `backup_id` 推导路径，该字段无消费者 | `handle_backup_restore` 返回 `report`；C# 未解析该键；测试 `:185` 直接断言该字段 | 删除该 report 字段（handoff 路径由 `backup_id` + 约定推导），或在卡面/契约走显式裁决后保留并改 AC6 声明 | open |
| R-003 | P1 | `SourceAccessRegistry.cs:216-226,264-267`；`SourceAccessRestore.cs:112-120`；`verification/FEA-13-SRC-6/README.md:16` | AC5 要求的错误分类未实现：DPAPI/版本/结构失败全部折叠为 `registry_corrupt_or_unprotectable`；`registry_version_unsupported`、`registry_corrupt` 无产生路径；`NMSAR2`、identity 负例无测试。README 声称 `dpapi_unprotectable` PASS 与代码不符 | 代码仅两条 rejected reason；测试只断言 Status/Code，未断言 Reason；`rg NMSAR2` 在测试中 0 命中 | 在 `ParseSnapshot` 分层抛出/映射：DPAPI 失败 → `dpapi_unprotectable`，magic/format → `registry_version_unsupported`，长度/JSON/结构 → `registry_corrupt`；补 `NMSAR2`、corrupt（handoff sha 同步）、identity 测试；修正 README | open |
| R-004 | P1 | `SourceAccessRestore.cs:69-72,162-175` | receipt 命中即返回 `unchanged`，且**显式 restore 与启动扫描共用同一入口**：用户导入 → `Reset(true)` → 再次显式 restore 同一包时 receipt 仍在，handoff 不会重新导入。违反 scope §2.4.1「显式 restore 触发时总是重写 receipt，允许再次导入」与 AC4「只有再次显式 restore 才可重新导入」；测试 `:143-151` 只能手工删 receipt 才能触发合并，反证该缺陷 | `TryImportFromHandoff` 先查 receipt；无 `force`/显式路径参数；测试注释「force a real merge by removing it」 | 增加显式路径参数（如 `force: true`）覆盖/重写 receipt；启动扫描保持 receipt 短路；补「导入→reset→再次显式 restore 可重新导入」测试 | open |
| R-005 | P1 | `verification/FEA-13-SRC-6/mutations/MA-live-conflict-overwritten.log` | MA 变异被判 RED 的证据无效：EXIT=1 的原因是 `找不到提供的测试源文件 ... NewManga.Host.Tests.dll`（构建/产物缺失），测试未执行，未证明冲突 guard 被禁用后断言失败；README/卡面据此声称 AC4 变异 RED | 日志原文：`找不到提供的测试源文件 ... NewManga.Host.Tests.dll`，无任何测试失败栈 | 重新构建后重跑 MA，日志须含真实断言失败与 `EXIT=1`；同时补「复原后绿」 | open |
| R-006 | P2 | `SourceAccessRegistry.cs:244-251` | 合并语义与 scope 合并表不一致：`liveEntry.Generation >= entry.Generation` 使「同 id、字段完全相同」也计为 `Conflicts`，`Unchanged` 在真实合并路径几乎恒为 0；重复导入的 `unchanged` 仅由 receipt 短路产生，合并幂等未被证明 | 第二人称测试只走 receipt；无「删 receipt 后完全相同条目 → Unchanged」测试 | 先判「字段完全相同」→ `unchanged`，再判代次/revoked → `conflict`；补同代次相同条目测试 | open |
| R-007 | P2 | `SourceAccessRestore.cs:33,166-168` | receipt 位置与冻结 scope 不符（scope：`<DataRoot>/host/source-access/imports/<backup_id>.json` + `SourceSecurity.PrivateDirectory`）；实际写进 Core 可写的备份树 `<backup_root>/restore-handoff/<id>/import-receipt.json`，未建私有 ACL。反 reset 复活保护依赖 Core 写域内文件，强度低于冻结口径 | 常量 `ReceiptFileName` 写入 handoff 根；无 `PrivateDirectory` 调用 | 回到 Host 私有目录并按 `PrivateDirectory` 建目录；handoff 树只读；或走 scope errata | open |
| R-008 | P2 | `src/application/importing/referenced/secrets.py:6,43,52,70` | AC1「Core 代码库 grep = 0」不成立：4 处既有 `CryptUnprotectData`（密码 secret 功能，非本卡引入）。卡面/README 未核实即宣称 MET；应把断言收窄为 `nmbak.py` 无新增 DPAPI/不解密 source-access | `rg -n "CryptProtectData|CryptUnprotectData" src/` → 4 命中；`git diff` 未触碰该文件 | 修正 AC/证据表述（限定 nmbak 路径），不要求删除既有 secrets 功能 | open |
| R-009 | P2 | `src/infrastructure/sqlite/nmbak.py:489-491` | `handoff.json` 的 `write_text` 在 `try/except OSError` 之外：写失败抛裸 `OSError`，经命令层落到 `E_UNKNOWN`，而不是 scope 要求的 `BACKUP_RESTORE_INCOMPLETE`；`report` 组装同理。DB 已恢复却给出非 typed 错误 | 代码结构：copy/digest 在 try 内，`write_text` 在 try 外 | 把 metadata 写入纳入同一 typed 包装，失败 → `BACKUP_RESTORE_INCOMPLETE`（附 rollback package 信息） | open |
| R-010 | P2 | `SourceAccessRestore.cs:113-135` | 终态 `rejected`（含 `handoff_corrupt`、DPAPI 拒绝）不写 receipt，与 scope §2.4.2「terminal outcome（imported/unchanged/rejected）写 receipt」不符：坏/异机 handoff 每次启动重试并重复日志（R-001 接线后即暴露） | 仅成功分支调用 `WriteReceipt` | rejected 也写 receipt（记录 reason），显式 restore 时按 R-004 重写 | open |
| R-011 | P2 | `verification/FEA-13-SRC-6/mutations/*.log` | 三条变异均只有 RED 运行，无 scope 要求的「复原后绿」；MB/MC 的 RED 真实，MA 为假 RED。证据纪律（Review 模板 Q-009）要求判别力 artefact 完整 | 三份日志只有一条命令头 + EXIT，无恢复后重跑 | 每条变异补「还原 → 全绿」日志与 EXIT=0 | open |
| R-012 | P2 | `SourceAccessRestoreTests.cs`、`test_nmbak_source_access.py` | 测试缺口导致 AC3/AC4/AC5 过度声明：无 `Authorize` 成功、第二 DataRoot e2e、generation-active 冲突、包内 revoked 导入、空候选 `unchanged`、read-only 零写、identity 负例、版本负例、`HostRuntime.RestoreBackupAsync` 集成（导入拒绝不反向失败）；AC3 重复导入未断言 live 字节/mtime 不变 | 7 个 Host `[Fact]` 逐一核对；Python 7 例无 Host 导入 | 逐项补测试；在 AC 未覆盖前不得标 `<<MET>>` | open |
| R-013 | P2 | `src/infrastructure/sqlite/nmbak.py:824-834` | reparse 防护只覆盖 `registry.v1.dat` 文件符号链接 + 该目录下相对路径；`host` / `host/source-access` 目录本身为 junction 时仍会跟随，与 scope「不跟随 symlink/junction」部分不符 | `_crosses_reparse_point(directory, Path("registry.v1.dat"))` 从 `source-access` 目录起算 | 用 `RejectReparseAncestors` 等价逻辑从 `data_root` 逐级检查，或显式检查目录组件 | open |
| R-014 | P3 | `SourceAccessRestore.cs:154` | `TryImportPending` 按目录名（backup_id）排序，scope 要求按 `handoff.json.created_at` 升序；UUID 名无序，导入顺序不可控 | 代码 `OrderBy(item => item, StringComparer.Ordinal)` | 读 manifest `created_at` 排序（坏 manifest 排末尾） | open |
| R-015 | P3 | `SourceAccessRegistry.cs:270-272` | 新增 `public bool Contains(...)` 无任何调用点（死 API，扩大 Host 面） | `rg` 无调用 | 删除或接入实际使用点 | open |
| R-016 | P3 | `HostRuntime.cs:417,425-437` | `RestoreBackupAsync` 直接调用导入，无本地 try/catch；`TryImportFromHandoff` 仅捕获 4 类异常，`ArgumentException`/`SecurityException` 等仍可冒泡，使「导入拒绝绝不反向失败 restore」不是结构性保证；`Registry == null` 时静默跳过无日志 | 调用点无保护；catch 过滤器范围有限 | 在 HostRuntime 包一层 catch-all（除 OOM）并记录；空 Registry 记 warn | open |
| R-017 | P3 | `src/infrastructure/sqlite/nmbak.py:434-441` | 每次成功 restore 都在 `backups/restore-handoff/<id>/` 留下 ≤4 MiB 的段，无清理/轮转；备份轮转不覆盖该目录，长期无界增长（resource manifest 未登记） | 代码无删除路径；scope 未要求回收 | 登记资源处置：随 backup 删除/轮转清理，或写入 Closeout limitation | open |
| R-018 | P3 | `doc/tasks/FEA-13-SRC-6.md:14`；`doc/STATUS.md`（head 内容） | 卡面 `base_commit: 07545adf1` 与本次被审 base `1a8bb1235` 不一致；STATUS 在 Host 提交后仍写「Host 导入待补」，与 head 事实不符 | `git show f85c6ddb3` 已含 Host 代码；卡面未同步 | 更新 base/状态（生命周期写入，DSH） | open |
| R-019 | P3 | diff 中 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` | 三个生命周期指针文件不在卡内 14 allowed_paths；scope r1 §2.6 已明确豁免（先例 RESTORE-4/SCHED-5），故不判越界，但卡面 allowed_paths 未登记该惯例 | `git diff --name-status` | 卡面补一行生命周期豁免说明，避免后续审查歧义 | open |
| R-020 | P3 | `test_nmbak_source_access.py:143-158`、`SourceAccessRestore.cs:93` | AC2(a) 测试未断言源 registry 字节不变；handoff manifest 的 `member` 未校验（仅 sha/size），与 scope「member 固定」不符 | 测试仅断言无 `.nmbak`；代码只查非空 | 补字节不变断言；校验 `member == extras/source-access/registry.v1.dat` | open |

## 验证（本次实测）

| 场景 | 命令 | 结果 | 证据 |
|---|---|---|---|
| 定向 pytest（3 文件） | `python -m pytest tests/storage/test_nmbak_source_access.py tests/storage/test_nmbak_backup.py tests/storage/test_nmbak_coverage.py -q` | **PASS** 36 passed，**EXIT 0** | 实跑 2026-11-10；日志 `pytest-src6.log`（7 passed）、`pytest-nmbak-suite.log`（54 passed）与本次一致 |
| 定向 .NET | `dotnet test ... --filter "FullyQualifiedName~SourceAccessRestoreTests"` | **PASS** 7 passed / 0 failed，**EXIT 0** | 实跑；日志 `dotnet-restore-tests.log` EXIT 0 |
| Host 全量 | 证据日志 `dotnet-host-tests.log` | 319 passed / 0 failed / 74 skipped，EXIT 0 | 未重跑（时间），仅复核日志尾行 |
| `check.ps1` 默认 | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)**，**EXIT 0** | 实跑；与 `gates-check.log` 一致 |
| `check.ps1 -TaskPath` | 同上 + `-TaskPath doc/tasks/FEA-13-SRC-6.md` | **PASS**，选中本卡，**EXIT 0** | 实跑 |
| `verify_pins` | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **18/18 PASS**，**EXIT 0** | 实跑；C06/C09/C17 pins 均 OK |
| `git status --short` | — | 写报告前为空；写后仅 `?? doc/reviews/FEA-13-SRC-6-r1.md` | 实测 |
| 真实跨机 DPAPI | — | **NOT_RUN**（单机无法构造；报告与测试均未记为 PASS，正确） | scope §4.4 |
| 变异 MA | 证据日志 | **无效 RED**（测试 DLL 不存在，测试未执行） | R-005 |
| 变异 MB/MC | 证据日志 | RED（真实断言失败）；无复原后绿 | R-011 |
| AC1 DPAPI grep 探针 | `rg -n "CryptProtectData|CryptUnprotectData" src/` | **4 命中**（既有 `secrets.py`），AC 的「=0」不成立 | R-008 |

## 越界结论

- 生产/测试/证据 diff ⊆ 14 allowed_paths：`SourceAccessRegistry.cs`、`SourceAccessRestore.cs`、`HostRuntime.cs`、`nmbak.py`、`test_nmbak_source_access.py`、卡面、`verification/FEA-13-SRC-6/**`（10 文件）均在列。
- **契约面偏离**：新增 `backup.restore` 出参（R-002），属冻结 scope 明示禁止项；其余 C-06/C-09/C-17 零字节、18 pins 零变化、0 DDL、0 新命令、0 新错误码（`HostErrorCodes.cs`/`CoreServiceClient.cs`/`restore_plan.py` 未改）。
- 3 个 `doc/STATUS.md`/`REBASELINE_PLAN.md`/`TASK_LEDGER.md` 卡外改动由 scope r1 §2.6 明确豁免（生命周期惯例），**不判实现越界**，仅记 R-019。

## 结论与复审

- **Architecture**：四段交接与 DPAPI 边界主设计正确；但启动补导入缺失、wire 出参增量、receipt 语义偏差三处偏离冻结口径。
- **Verification**：门禁实测全绿；AC 证据覆盖不足，AC1/AC3/AC4/AC5/AC6 均不能按卡面 `<<MET>>` 采信；MA 变异证据无效，AC5 错误分类名不副实。
- **决定**：对 `14b0842e7` **不可批准**。修复 R-001–R-005 并补 R-006/R-012 的测试后可复审；R-002 若坚持保留须走 scope/DSH 裁决并修订 AC6。
