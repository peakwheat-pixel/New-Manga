# FEA-11-HOST-AUTH-3 实现 Review r3（独立上下文只读子代理）

| 项 | 值 |
|---|---|
| 审查者 | 独立上下文 fresh subagent（父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`；本会话 id 未在运行提示中暴露；**未参与** FEA-11-HOST-AUTH-1/2/3 的实现、返修、证据生成或卡面起草） |
| reviewer_kind | `subagent`（DSH 派发；只读被审 head；仅写本文件） |
| 模式 | 只读 + 允许的实测：read/grep/glob、只读 git、`check.ps1`/`verify_pins.ps1`、聚焦 pytest。**未重跑** `crash-ack.ps1`（`:225-242` 会向 `verification/…/crash/<run-id>/` 写新产物，越出本轮单文件写权限）；未改生产源码/测试/契约；未 commit/push |
| 被审 head | **`0bcf9ba70`**（`main`）；r2 被审 head `d303b9a3f`；base `e9ab2ef7c` |
| r2 → r3 增量 | `git diff --stat d303b9a3f..0bcf9ba70` = 25 files, **+521 / −214**；实现侧改动 `CoreServiceClient.cs`、`Fea11HostAuthIpcTests.cs`、`materialization.py`、`test_source_plan_materialization.py`，其余为证据/卡面/工具 |
| 审查输入 | 卡 `doc/tasks/FEA-11-HOST-AUTH-3.md`；r1/r2 报告；scope r2；`verification/FEA-11-HOST-AUTH-3/**`；r2..head diff |
| **verdict** | **`changes_requested`** |
| 计数 | **r1 12 条：FIXED=7 / PARTIAL=4 / OPEN=1**；**r2 7 条：FIXED=1 / PARTIAL=5 / OPEN=1**；**新增：P0=0 / P1=1 / P2=1 / P3=0** |

## 0. 一句话结论

r2 的两项 P1 只闭合了一半：**全量 pytest 证据已在最终代码上重跑（3468/0/10，`pytest-full.log` 00:45:31 起、00:49:55 止，晚于 00:44:09 的源码改动）**，但 **.NET 全量是 `--no-build` 跑的陈旧 Debug 程序集**——`NewManga.Host.Tests.dll` 时间 00:32:26、不含 00:44:28 新增的 `page_bindings`/`PageBindingsAsync` 字符串，`CoreClient.Tests.dll` 仍为 23:46:59，因此「在最终 head 重跑 .NET 1810/0/109」不成立（R-r3-01，P1）。`R-r2-01①` 崩溃反例仍未实现，卡面已**诚实**改为 `<<PARTIAL…NOT_RUN>>`；`page_bindings` 字段级对拍与 `journal_present`+OBSERVE 已落地，attempt12 的 10 个 CHECK 全 =1。`R-r1-11` 严格解析已修；但 `R-r1-04`（source 不符未实现、baselines≠1/多 root 无测试、卡面矩阵未恢复）、`R-r1-12`（无 lifecycle 认领提交）仍开，且 **AC-H3-2 仍记 `<<MET>>`**，而归档 wirelog 仍有 **2 条明文 `signature`**（R-r2-03 未修）。故不能判 approved。

## 1. 门禁与实测（本轮亲自执行，2026-11-10 01:00–01:08 +08:00）

| 项 | 命令 / 对象 | 结果 |
|---|---|---|
| 聚焦 pytest | `python -m pytest tests/fea11 tests/core/test_core_service.py -q` | **`245 passed, 9 warnings in 12.99s`；EXIT=0** |
| 治理（指定卡） | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-HOST-AUTH-3.md` | `Governance check: PASS (3 warnings)`；**EXIT=0** |
| 契约 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **`PIN AUDIT: PASS (all 18)`**，`C17 cdeee4872e29`；**EXIT=0** |
| 崩溃驱动重跑 | `crash-ack.ps1` | **NOT_RUN**（写 `crash/<run-id>/` 越权）；改为静态核验 attempt11/12 日志与归档（§3） |
| 工作树 | `git status --short` | 空（本文件写入前） |
| diff 范围 | `git diff --name-only e9ab2ef7c..0bcf9ba70` | 66 个路径；过滤 C-17/契约/`HostCommandRegistry|HostCommandDispatcher`/`source_read_refs`/`sources/runtime`/`sqlite/source_sync`/`sources/ports` → **0 命中**，diff ⊆ allowed_paths 成立 |
| 全量 pytest 日志 | `logs/pytest-full.log` | **3468 passed / 0 failed / 10 skipped**（00:45:31 起跑，00:49:55 完成；源码 mtime 00:44:09）→ 覆盖最终代码 |
| 全量 .NET 日志 | `logs/dotnet-*.log` | 合计 **1810 passed / 0 failed / 109 skipped**（8 项目，00:54:32–00:55:49），但每个日志头均为 **`(no-build)`**；程序集陈旧 → 见 R-r3-01 |

## 2. r1 findings 逐条判定

| ID | r1 级别 | 判定 | 依据（本轮核验） |
|---|---|---|---|
| **R-r1-01** | P0 | **FIXED** | `crash-ack.ps1:158-223` 的 CHECK 由 `park.json`/`recover.json` 事实计算；PID 树枚举 `:87-118`、kill 后 30s 轮询 `:129-140`；attempt12 产物归档 `crash/588f…/`（park/recover/pids-before 12 PID+1 python/pids-after 0 字节/library.db/wirelog）齐备，`crash-driver-attempt12.log:38-47` **CHECK ×10 全 =1**、`CRASH_POINT=PASS`、**EXIT=0** |
| **R-r1-02** | P1 | **FIXED** | 卡 `:34-36` 已把 `tests/core/test_core_service.py` 列入 allowed_paths 并写扩域理由；diff 无放宽断言 |
| **R-r1-03** | P1 | **PARTIAL** | 已修：`materialization.py:124-127` 对非 missing 且 `target.entries` 非 list → `SOURCE_PLAN_UNAVAILABLE`。**未修**：负例 `test_missing_required_body_field_is_unavailable`（`test_source_plan_materialization.py:189-209`）只参数化 `kind/source_id/reference_set_digest`，**无 entries 缺字段用例**；`:221-228` 的「无绝对路径/secret」断言仍近恒真（`"source-v" not in text or ":\\" not in text`） |
| **R-r1-04** | P1 | **PARTIAL** | 已修：`SourceOperationCoordinator.cs:249-255` `baselines.Count != 1` → typed `SOURCE_ACCESS_DENIED`；`:268-280` 唯一 readable root 校验。**未修**：`material.SourceId` 与 journal/plan 的**不符校验仍未实现**（`:210-213` 只判非空；`:228-243` 只拿 source_id 去 `scan_targets` 匹配 kind）；`Fea11HostAuthTests` 中 `Recovery_Refuses*` 6 例（`:938-1006`）**无 baseline≠1 / 多 root / source 不符**用例；卡 `:74` 拒绝矩阵仍是被改写的 6 例，未恢复冻结矩阵 |
| **R-r1-05** | P1 | **PARTIAL** | `README.md` 状态表仍只有「结果」列，**无逐项命令/时间/head/EXIT**（`:9-17`）；冻结 §4.1 的 `kill.json`/`db_before`/`db_after`/`frames.txt`/`sha256.txt` 未归档；且 README 已过期（见 R-r2-04） |
| **R-r1-06** | P2 | **PARTIAL** | ①「park/recover grant ids 无交集」已真实比较（`crash-ack.ps1:173-178`，attempt12 `fresh_grant=1`）。②冻结的「grant id 不出现在 journal 字节」未执行：`crash-ack.ps1:196-212` 改为 `journal_present`（文件存在）+ `OBSERVE journal_grant_grep=0`，属 OBSERVE 而非断言（attempt11 曾以 `fresh_grant_recorded_in_journal=0` 判 FAIL 后替换，见 R-r3-02）。③实现仍主动把重铸 grants 写回终态 journal（`SourceOperationCoordinator.cs:495`、`:604`），卡 `:75` 只说事实、未给审计理由 |
| **R-r1-07** | P2 | **FIXED** | `PrepareCompletion` 死参数已删（`:315-316`），两调用点不再传参；编译面由崩溃驱动 Release 构建验证 |
| **R-r1-08** | P2 | **FIXED** | `mutations/M1-journal-grant-reuse.log`：真实变异被 `SOURCE_ACCESS_DENIED`（grant not registered）抓住，**EXIT=12**。残余：卡 `:76` M1 措辞仍与日志不符；`mutations/` 仍无变异 diff |
| **R-r1-09** | P2 | **FIXED** | `test_body_budget_over_eight_mebibytes_is_typed`（`:307-340`）改为 **9000 条 × 1100B locator ≈ 9.9MiB**：低于 `_MAX_ENTRIES=10000`（`materialization.py:34`），必然命中 `_BUDGET_BYTES=8MiB`（`:148-152`）；聚焦 pytest 绿 |
| **R-r1-10** | P3 | **FIXED** | `PrepareCompletion`/`MintRecoveryGrantsAsync` 的 XML doc 顺序正确，无双 `<summary>` |
| **R-r1-11** | P3 | **FIXED**（原 OPEN） | `CoreServiceClient.cs:1637-1683` 已改为严格解析：`RequireText`（format/plan_id/plan_digest/kind/source_id/reference_set_digest/state/expires_at 缺失或空白→`Malformed`）、`entries` 必须为数组、每项 `entry_id/locator/content_digest_kind` 非空且 `ordinal` 为数字，否则 `Malformed`；不再 `?? string.Empty`/缺省 `0` |
| **R-r1-12** | P3 | **OPEN** | `doc/STATUS.md`/`doc/REBASELINE_PLAN.md`/`doc/TASK_LEDGER.md` 最后提交仍是实现轮（`7e2d0c241`/`bfa5016c7`），无 DSH lifecycle 认领提交 |

**计数：FIXED=7（R-r1-01/02/07/08/09/10/11）/ PARTIAL=4（R-r1-03/04/05/06）/ OPEN=1（R-r1-12）。**

## 3. r2 findings 逐条判定

| ID | r2 级别 | 判定 | 依据（本轮核验） |
|---|---|---|---|
| **R-r2-01** | P1 | **PARTIAL** | ①崩溃反例（phase 间替换源文件→typed、gates pending）**仍未实现**（全仓库 `CrashPoint` 只有 Park/Recover；`Fea11HostAuthIpcTests` 无替换源文件用例）；卡 `:75` 已**诚实**标 `<<PARTIAL: 崩溃反例未实现（NOT_RUN）>>`，不再记 MET。②`crash-ack.ps1:180-194` 新增 `page_bindings_fields_unchanged`：`check_gate.py --page-bindings` 导出全列，除 `updated_at` 外逐字段比较；归档 `588f…` 的 park/recover 各 2 行，仅 `updated_at` 不同，attempt12 `CHECK page_bindings_fields_unchanged=1`。③`crash-ack.ps1:196-212` 新增 `journal_present` + `OBSERVE`（`NMSOP1` 加密，`op-…v1.dat` 3081B），attempt12 `journal_present=1`；按 r3 口径可接受为「存在性 + OBSERVE」，但不等于冻结的 grant id 字节断言（见 R-r3-02） |
| **R-r2-02** | P1 | **PARTIAL** | pytest 侧已闭合：3468/0/10，日志 00:45:31–00:49:55，晚于源码 00:44:09。.NET 侧**未闭合**：8 份日志均为 `dotnet test … (no-build)`，`NewManga.Host.Tests.dll`（Debug）mtime 00:32:26，**不含** 00:44:28 新增的 `page_bindings`/`PageBindingsAsync` 字符串；`NewManga.CoreClient.Tests.dll` mtime 2026-11-09 23:46:59。故 1810/0/109 不是最终 head 的程序集证据（R-r3-01） |
| **R-r2-03** | P2 | **OPEN** | 归档 wirelog（`crash/588f…/wire-redacted.ndjson`，第 5/21 行附近）仍有 **2 处明文 `"signature":"<43 字符>"`**（`signing_key` 已 `[REDACTED]`）；`secret_ref`/盘符/`/home/`/`/Users/` 均 0 命中。冻结 AC-H3-2 要求 wirelog「0 命中 signature」，卡 `:73` 仍记 `<<MET>>` |
| **R-r2-04** | P2 | **PARTIAL** | 改进：归档 run `588f…` 现由 `crash-driver-attempt12.log:5,48` 精确引用，可追溯。**未修**：README 仍写 attempt10/3461/8 个 CHECK（`:11,17,21`），与卡面 attempt12/3468/10 个 CHECK 冲突；孤立归档 `289e…`（无 driver 日志）仍在；`mutations/` 6 个日志仍无变异 diff |
| **R-r2-05** | P2 | **FIXED** | 8MiB 用例改为 9000×1100B，先过 `_MAX_ENTRIES`（9000≤10000）再命中 `_BUDGET_BYTES`；用例名与实际分支一致 |
| **R-r2-06** | P2 | **PARTIAL** | `journal_present` + OBSERVE 已实现；但仍无 journal 副本/解密断言，卡面未说明「为何必须把重铸 grants 写入终态 journal」，且与同一行「grant_id 不在 journal」的三重防伪表述自相矛盾（R-r3-02） |
| **R-r2-07** | P3 | **PARTIAL** | 卡 `:75` 日志引用已改为 `crash-driver-attempt12.log`；但同句仍写「**驱动 attempt 6**」，README 仍指 attempt10，引用未统一 |

**计数：FIXED=1（R-r2-05）/ PARTIAL=5（R-r2-01/02/04/06/07）/ OPEN=1（R-r2-03）。**

## 4. 新增 findings

| ID | 级别 | 位置 | 问题 | 证据 | 建议 |
|---|---|---|---|---|---|
| **R-r3-01** | **P1** | `logs/dotnet-*.log`；`apps/desktop-avalonia/tests/NewManga.Host.Tests/bin/Debug/net9.0/NewManga.Host.Tests.dll` | **全量 .NET 是 `--no-build` 的陈旧程序集，不能证明最终 head**：8 份日志头均 `(no-build)`；`Host.Tests.dll` 00:32:26 早于 `Fea11HostAuthIpcTests.cs` 00:44:28，二进制内 `page_bindings`/`PageBindingsAsync` 字符串均不存在；`CoreClient.Tests.dll` 仍是 23:46:59。卡 `:77`「全量（在最终 head 重跑）… <<MET>>」不成立 | 日志头 `# command: dotnet test … (no-build)`；dll mtime 与字符串检查；源码 mtime 00:44 | 在 `0bcf9ba70` 上重新 build（勿 `--no-build`）后重跑 8 个 .NET 项目并替换日志；或把 .NET 项标为「按非最终程序集基线」 |
| **R-r3-02** | **P2** | `logs/crash-driver-attempt11.log:46-47`；`tools/crash-ack.ps1:196-212`；`SourceOperationCoordinator.cs:495,604`；卡 `:75` | **冻结 ③ 的判别式被替换而非满足**：attempt11 以 `fresh_grant_recorded_in_journal=0` 判 `CRASH_POINT=FAIL`，attempt12 将该 CHECK 换成 `journal_present=1`（只验文件存在）后 PASS；同时实现把重铸 grants 写入终态 journal（`:495`/`:604`），与卡面同句「三重防伪（… grant_id 不在 journal）」直接矛盾。OBSERVE 说明只解释了「加密导致明文 grep 为 0」，未解释设计上 grants 确实被记录 | attempt11 末尾；attempt12 `CHECK journal_present=1`；源码两处 `GrantIds = string.Join(",", recoveryGrants)`；卡 `:75` | 由 DSH 裁决 AC evidencing 口径（解密后断言 grant 记录/或不记录），卡面同时消除「不在 journal」与实际记录的自相矛盾；不得以「文件存在」替代冻结断言后仍称三重防伪成立 |

**新增计数：P0=0 / P1=1（R-r3-01）/ P2=1（R-r3-02）/ P3=0。**

## 5. AC 逐项判定

| AC | 判定 | 依据 |
|---|---|---|
| **AC-H3-1** 契约与字节不回退 | **MET** | `verify_pins` 18/18（`C17 cdeee4872e29`）；diff 不含「不列入」清单 |
| **AC-H3-2** Core 新命令 | **PARTIAL** | 通道/closed shape/typed 矩阵/排序/零写/entries 缺失代码路径均成立（245 passed）；但**无 entries 缺失负例**（R-r1-03），且归档 wirelog 仍有 **2 条明文 signature**（R-r2-03）→「脱敏 0 命中」不成立，卡面 `<<MET>>` 标注不实 |
| **AC-H3-3** Host 重铸 | **PARTIAL** | completion 用重铸 grants、6 例 typed 拒绝绿、journal 保持 core-committed；但 source 不符未实现、baselines≠1/多 root 无测试、卡面矩阵未恢复（R-r1-04） |
| **AC-H3-4** 真实 kill 恢复一次 | **PARTIAL** | 核心断言由真实测量产生（attempt12 10 CHECK 全 =1、PID 树 12+1、30s 全灭、gate open、行数/源 sha/0 帧、fresh grant 不相交、page_bindings 字段级一致、journal 存在）；**崩溃反例未实现 → NOT_RUN**，卡面已诚实标 PARTIAL；journal ③ 仅 OBSERVE（R-r3-02） |
| **AC-H3-5** 变异判别 | **MET** | M1（真崩溃驱动 RED，EXIT 12 + `SOURCE_ACCESS_DENIED`）与 M2–M6 日志齐备；残余 P3：卡面 M1 措辞陈旧、无变异 diff |
| **AC-H3-6** 门禁/范围/不夸大 | **PARTIAL** | `check.ps1`/pins/工作树/diff ⊆ allowed_paths 成立；pytest 全量覆盖最终代码；但 **.NET 全量为陈旧 `--no-build` 程序集**（R-r3-01），README/§4.1 证据表不完备（R-r1-05/R-r2-04），「在最终 head 重跑」与「不夸大」不成立 |

## 6. 结论

- **verdict：`changes_requested`**。
- **已确认修复**：r1 的 P0 驱动造假与 archive 证据链保持；`R-r1-11` 严格解析；`R-r1-09` 8MiB 分支真实命中；`page_bindings` 字段级对拍与 `journal_present`+OBSERVE 落地；pytest 全量 3468/0/10 覆盖最终代码；聚焦 pytest/`check.ps1`/`verify_pins` 全绿，工作树 clean。
- **阻塞项（按优先级）**：① **R-r3-01/R-r2-02**（.NET 全量 `--no-build` 陈旧程序集，AC-H3-6「最终 head 重跑」不成立）；② **R-r2-01①**（崩溃反例 NOT_RUN，AC-H3-4 仍 PARTIAL）；③ **R-r2-03**（wirelog 2 条明文 signature，AC-H3-2 仍记 MET）；④ **R-r1-04**（source 不符未实现、baselines≠1/多 root 无测试、卡面矩阵未恢复）；⑤ README/卡面引用不一致与 R-r1-12 lifecycle 未认领。
- **口径**：本轮未重跑 `crash-ack.ps1`（写权限约束），AC-H3-4 结论基于归档产物 + 脚本 + 测试源码 + attempt11/12 日志的独立复算，不构成对实现者 PASS 的转述。
- 本报告只写此文件，不构成对任何实现/契约的批准，不改变 `FEA-11-HOST-AUTH-2` 的 `AC-F3 = NOT_APPLICABLE`。
