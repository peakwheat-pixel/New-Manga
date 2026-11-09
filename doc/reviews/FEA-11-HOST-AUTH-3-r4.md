# FEA-11-HOST-AUTH-3 实现 Review r4（独立上下文只读子代理 · 终审）

| 项 | 值 |
|---|---|
| 审查者 | 独立上下文 fresh subagent（父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`）；**未参与** FEA-11-HOST-AUTH-1/2/3 的实现、返修、证据生成或卡面起草 |
| reviewer_kind | `subagent`（DSH 派发；只读被审 head；仅写本文件） |
| 模式 | 只读 + 允许的实测：read/grep、只读 git、`check.ps1`/`verify_pins.ps1`/`generate_api_inventory.py --check`、聚焦 pytest、程序集字符串探测。**未重跑** `crash-ack.ps1`（会向 `verification/…/crash/<run-id>/` 写新产物，越出单文件写权限）；未改生产源码/测试/契约；未 commit/push |
| 被审 head | **`c20145bf2`**（`main`，01:10:08）；base `e9ab2ef7c`；r3 被审 head `0bcf9ba70` |
| r3 → r4 增量 | `git diff --stat e9ab2ef7c..c20145bf2` = **81 files, +3617 / −71**；其中 `Fea11HostAuthIpcTests.cs`（+31，01:09:12）、卡面/README、05 个 crash 归档目录、fresh-build 日志 |
| **verdict** | **`changes_requested`** |
| **CLEARED FOR DONE** | **否**（1 项 blocking：R-r2-03） |

## 0. 一句话结论

r3 的 P1（.NET 全量陈旧 `--no-build` 证据）**已闭合**：8 份日志均为 fresh build（无 `--no-build`），合计 **1811 passed / 0 failed / 109 skipped**，Host.Tests **312 passed / 74 skipped**，程序集已含 `page_bindings`/`PageBindingsAsync` 与 `Recovery_RefusesAMultiBaselineJournal`。崩溃反例**已实测**（`CHECK negative_typed_refusal=1 code=SOURCE_ACCESS_DENIED`、`CRASH_POINT=NEGATIVE_PASS`、EXIT 0），`R-r1-04` 的 baseline≠1 拒绝与「source 不符」limitation 均落地。但 **`R-r2-03` 仍 OPEN**：归档 wirelog 第 5/21 行仍有 **2 条明文 `signature`**（43 字符，`signing_key` 已脱敏），卡面与 README **0 处**提及 signature/C-16，AC-H3-2 仍以「脱敏 0 命中」记 `<<MET>>`。故不能判 approved。

## 1. 门禁与实测（本轮亲自执行，2026-11-10 01:10–01:24 +08:00）

| 项 | 命令 / 对象 | 结果 |
|---|---|---|
| 聚焦 pytest | `python -m pytest tests/fea11 tests/core/test_core_service.py -q` | `245 passed, 9 warnings in 13.10s`；**EXIT=0** |
| 治理（指定卡） | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-HOST-AUTH-3.md` | `Governance check: PASS (3 warnings)`；**EXIT=0** |
| 契约 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，`C17 cdeee4872e29`；**EXIT=0** |
| API 清单 | `python tools/generate_api_inventory.py --check` | **EXIT=0**（无 diff） |
| 工作树 | `git status --porcelain` | 空（本文件写入前） |
| diff 范围 | 81 路径逐条比对卡面 19 条 `allowed_paths` + 3 条 glob | **全部 81 路径 ⊆ allowed_paths**；`HostCommandRegistry|HostCommandDispatcher|source_read_refs|sources/runtime|sqlite/source_sync|sources/ports|FEA-C07|契约载体` 命中 **0** |
| C-17 字节 | `git diff --stat e9ab2ef7c..c20145bf2 -- doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md doc/contracts/FEA-CONTRACT-FROZEN-C17.md doc/reviews/CONTRACT-UNFREEZE-2026-11-09-C17.md` | **空**（C-17 与 17 份 pin 零变化） |
| 全量 .NET | `logs/dotnet-full-console.log`（`dotnet build -c Debug -t:Rebuild + dotnet test`，01:01:12 起） | App 838/11、Appearance 21/0、ApplicationCore 31/0、CoreClient 167/24、DesignSystem 117/0、**Host 312/74**、Presentation 72/0、ThemeEngine 253/0 → **1811 / 0 / 109** |
| 程序集新鲜度 | `NewManga.Host.Tests.dll`（Debug 01:01:37）字符串探测 | `page_bindings`/`PageBindingsAsync`/`Recovery_RefusesAMultiBaselineJournal` 均 **存在**；Release 程序集（01:09:14）另含 `NEWMANGA_FEA11_CRASH_NEGATIVE`/`rejected_code` → 01:09 的负例改动已被 fresh 编译 |

## 2. 终审重点逐条判定

| 项 | 判定 | 依据 |
|---|---|---|
| **R-r3-01** .NET 全量 fresh build | **FIXED** | 8 份 `dotnet-*.log` 头均为 `# command: dotnet test … (fresh build)`、时间 01:05:58–01:07:18，**无 `(no-build)`**；`dotnet-full-console.log` 01:01:12 起 `-t:Rebuild + dotnet test`，8 项目汇总 **1811/0/109**，Host.Tests **312/74** 与要求一致；dll 01:01:15–01:01:37，晚于生产源码（`CoreServiceClient.cs` 00:44:09、`SourceOperationCoordinator.cs` 00:33:14）且二进制含 r3 新增符号。**残余 P3**：全量构建起点 01:01:12 早于 head（01:10:08）；其后仅 `Fea11HostAuthIpcTests.cs`（01:09:12，测试文件）变更，已由 01:09:14 Release 编译 + 负例实跑覆盖；卡 `:77` 仍写 **1810**，与 README 与 `dotnet-full-console.log` 的 **1811** 不一致 |
| **R-r2-01①** 崩溃反例 | **FIXED** | `logs/crash-driver-negative.log`（01:09:29，EXIT 0）：`CRASH_POINT phase=replace source_replaced=1 other=source-v1.zip` → Release fresh build（含负例分支）→ 1 test 通过 → `CHECK negative_typed_refusal=1 code=SOURCE_ACCESS_DENIED` → `CRASH_POINT=NEGATIVE_PASS`；源码 `Fea11HostAuthIpcTests.cs:@277-305` 为真实 `RecoverAsync` + 捕获 typed code + 写 `negative.json`，非常量断言。残余 P3：`negative.json` 未归档进 `verification/`（驱动在归档前 return），仅控制台日志可追溯 |
| **R-r2-03** wirelog 明文 signature | **OPEN** | 5 份归档 wirelog **各 2 条**明文 `\"signature\":\"<43 字符>\"`（`588f…` 第 5/21 行，`signing_key` 已 `[REDACTED]`，`[REDACTED]` 13 处）；`doc/tasks/FEA-11-HOST-AUTH-3.md` 与 `verification/…/README.md` 对 `signature`/`C-16`/`签名` 检索命中 **0**，未登记「C-16 §7 既有边界」limitation；卡 `:73` 仍写「脱敏 0 命中」并记 `<<MET>>` |
| **R-r1-04** 多 baseline / source 不符 | **FIXED**（残余 P3） | `SourceOperationCoordinator.cs:249-255` `baselines.Count != 1` → typed `SOURCE_ACCESS_DENIED`（含零/多 baseline），`:272-280` 恰好 1 个 readable root 否则 deny；`Fea11HostAuthTests.cs:1013-1025` `Recovery_RefusesAMultiBaselineJournal`（baselineCount:2）；卡 `:66` 已把「冻结矩阵 source 不符」登记为冻结面 limitation。残余 P3：卡 `:74` 的 AC-H3-3 矩阵文本（6 例）未加入 multi-baseline/multi-root 两例，与实际实现/测试不同步 |
| **R-r1-05** README 逐项 | **OPEN** | README `:9-18` 仍是单列「结果」表，无逐项「命令/时间/head/EXIT」；冻结 §4.1 的 `kill.json`/`db_before`/`db_after`/`frames.txt`/`sha256.txt` 在 5 个 `crash/<run-id>/` 中**均不存在**（实际只有 park/recover/pids×2/library.db/wirelog） |
| **R-r1-12** lifecycle | **OPEN** | `e9ab2ef7c..c20145bf2` 内 `doc/STATUS.md`/`doc/REBASELINE_PLAN.md`/`doc/TASK_LEDGER.md` **零提交**（最后仍为实现轮 `7e2d0c241`/`bfa5016c7`），无 DSH lifecycle 认领 |
| **正例 10 CHECK / 归档产物** | **PASS** | `logs/crash-driver-attempt12.log`：10 个 `CHECK`（commit_digest_match、distinct_host_pid、distinct_core_session、source_sha256_unchanged、rows_unchanged、gates_open、second_call_idempotent、fresh_grant、page_bindings_fields_unchanged、journal_present）**全 =1**，`CRASH_POINT=PASS`，EXIT 0；`crash/host-auth-crash-588f…/` 6 件产物齐全。残余 P3：`crash/4a18…`、`crash/8e633d…`（01:08:24/01:08:42，park 含 `source_path`）为**无 driver 日志、无任何文档引用**的孤儿归档 |

**计数（本轮关注项）：FIXED=3（R-r3-01、R-r2-01①、R-r1-04）/ OPEN=3（R-r2-03、R-r1-05、R-r1-12）；正例 CHECK 全绿。r3 P1 已闭合，r2 唯一未闭合项为 R-r2-03。**

## 3. AC 复核

| AC | r4 判定 | 依据 |
|---|---|---|
| **AC-H3-1** | **MET** | `verify_pins` 18/18（C17 cdeee4872e29）；契约字节 diff 空；不列入清单零命中 |
| **AC-H3-2** | **PARTIAL** | 代码路径与负例齐（245 passed），但「脱敏 0 命中」**不成立**（2 条明文 signature）且未登记 limitation；`<<MET>>` 标注不实（R-r2-03） |
| **AC-H3-3** | **MET** | 拒绝矩阵 typed + 多 baseline/multi-root 拒绝 + source 不符 limitation；残余仅卡面矩阵文本未同步（P3） |
| **AC-H3-4** | **MET** | 正例 10 CHECK 全 =1（真实测量）；反例实测 `SOURCE_ACCESS_DENIED`/`NEGATIVE_PASS`；journal 项为存在性 + OBSERVE（r3 已接受口径） |
| **AC-H3-5** | **MET** | M1 真崩溃驱动 RED（EXIT 12 + `SOURCE_ACCESS_DENIED`）+ M2–M6 日志齐备 |
| **AC-H3-6** | **PARTIAL** | 门禁全绿、diff ⊆ allowed_paths、工作树 clean、.NET/pytest 全量均 fresh；但 AC-H3-2 的「0 命中」属不实表述（R-r2-03），README 证据表不完备（R-r1-05） |

## 4. 结论

- **verdict：`changes_requested`**；**未 CLEARED FOR DONE**。
- **blocking（仅 1 项）**：**R-r2-03** — 归档 wirelog 仍有 2 条明文 `signature`，而卡面/README 未按「C-16 §7 既有边界」登记 limitation，AC-H3-2 仍记「脱敏 0 命中 `<<MET>>`」。处置只需**文档层**（登记 limitation 并修正 AC-H3-2/README 措辞，或对 signature 实施脱敏后重归档），**无需改生产代码**；完成后即可在 r5 判 approved。
- **非 blocking 残余（进入 done 前应收口）**：R-r1-05（README 逐项 + 冻结 §4.1 产物）、R-r1-12（STATUS/REBASELINE/LEDGER lifecycle 认领）、卡 `:77` 的 1810→1811、卡 `:74` 矩阵补两例、两个孤儿 crash 归档去留。
- **口径**：本轮未重跑 `crash-ack.ps1`（写权限约束），AC-H3-4 结论基于归档产物、脚本源码、程序集探测与 attempt12/negative 日志的独立复算，不构成对实现者 PASS 的转述；本报告只写此文件，不构成对任何实现/契约的批准。
