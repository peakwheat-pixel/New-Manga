# FEA-11-HOST-AUTH-3 实现 Review r1（独立上下文只读子代理）

| 项 | 值 |
|---|---|
| 审查者 | 独立上下文 fresh subagent（父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`；本会话 id 未在运行提示中暴露；**未参与** FEA-11-HOST-AUTH-1/2/3 的实现、返修、证据生成或卡面起草） |
| reviewer_kind | `subagent`（由 DSH 派发；只读被审 head；仅写本文件） |
| 模式 | 只读 + 允许的实测：read/grep/glob、只读 git、`check.ps1`/`verify_pins.ps1`、聚焦 pytest、**重跑** `crash-ack.ps1`（`NEWMANGA_FEA11_IPC=1`）；未改生产源码/测试/契约，未 commit/push |
| 被审 head | `74e7737d5`；base `e9ab2ef7c`（`main`） |
| 审查输入 | 卡 `doc/tasks/FEA-11-HOST-AUTH-3.md`；scope r2 `doc/reviews/FEA-11-HOST-AUTH-3-scope-r2.md`；ZCode 裁决 `doc/reviews/ADJ-2026-11-09-ZCODE-ARCH-ADJUDICATION.md`；C-17 v1.2 `doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md` + 冻结记录 + 载体；`verification/FEA-11-HOST-AUTH-3/**`；本卡实现 diff |
| **verdict** | **`changes_requested`** |
| 计数 | **P0=1 / P1=4 / P2=4 / P3=3** |

## 0. 一句话结论

Core 面（新命令、closed shape、typed 错误、capability、零写单 SELECT）与 Host 重铸骨架（`MintRecoveryGrantsAsync` + `IssueForRecoveryAsync` + `prepared with { GrantIds }`）**方向正确、聚焦测试全绿**；但 **AC-H3-4 的「实测 PASS」不能由证据支撑**：`crash-ack.ps1` 打印的 `gates_open=1 rows_unchanged=1 second_call_idempotent=1` 是**硬编码字符串常量，脚本从未计算它们**，且冻结 AC 明确要求的 sidecar 死亡证明、DB 前后行数、`read_gate`、源 sha256、二次调用帧数、journal grep **一条都没执行**。加上 `tests/core/test_core_service.py` 越界、AC-H3-2 的负例与零写证据不足、证据目录缺冻结清单产物，本轮不能判 MET。

## 1. 门禁与实测（本轮亲自执行）

| 项 | 命令 / 对象 | 结果 |
|---|---|---|
| 契约 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **`PIN AUDIT: PASS (all 18)`**，`OK C17 cdeee4872e29`；**EXIT=0** |
| C-17 字节 | `Get-FileHash doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md` | `CDEEE4872E29B56C7D67DE65DABD6CA9B31006EECDE61D99B83E29FE5A4FC96C` = 冻结值，**零变化** |
| 治理（指定卡） | `check.ps1 -TaskPath doc/tasks/FEA-11-HOST-AUTH-3.md` | `Governance check: PASS (3 warnings)`；**EXIT=0** |
| 崩溃驱动重跑 | `NEWMANGA_FEA11_IPC=1 pwsh -File verification/FEA-11-HOST-AUTH-3/tools/crash-ack.ps1` | **EXIT=0**，复现同一句 `CRASH_POINT=PASS … gates_open=1 rows_unchanged=1 …`（**但见 P0-1：这些数字未计算**） |
| 崩溃结果独立核验 | 重跑产物 `host-auth-crash-e306873285224db9adf36583277bf322` + data_root | `park.json`=`core-committed`；`recover.json` PID/session 与 park 不同、grant id 不同；DB `source_binding_publications.read_gate=('open',1)`、行数 `pages=1 / page_bindings=2 / source_binding_publications=1`。**功能路径看起来成立**，但脚本本身没做这些断言，且无 `db_before` 可对拍 |
| 聚焦 pytest | `tests/fea11/test_source_plan_materialization.py` + `test_source_command_parity.py` | `17 passed`，EXIT=0 |
| capability 断言 | `tests/core/test_core_service.py -k "dispatch_pure_functions or subprocess"` | `2 passed`，EXIT=0 |
| 全量 pytest | `logs/pytest-full.log:107` | `3461 passed, 10 skipped, 11 warnings in 255.31s`；`# EXIT=0` —— **仅日志复核，未重跑全量**（4m15s，超本 Review 预算） |
| 全量 .NET | `logs/dotnet-*.log`（8 个项目） | 838+21+31+167+117+311+72+253 = **1810 passed**；skip 11+24+74 = **109**；**failed=0**、8 份均 `已通过!` —— 仅日志复核，未重跑全量；Host.Tests `311 passed / 0 failed / 74 skipped` 与日志一致 |
| 工作树 | `git status --short` | 空（本文件写入前；重跑产物只落在 `G:\CODEX\New Manga.workspace\`） |

**结论**：`check.ps1`/`verify_pins`/契约字节/工作树干净 = 成立；pytest 与 .NET 的**统计数字与 EXIT 真实**（我已逐份核对汇总行并作加法校验），但我未重跑全量。

## 2. Findings

| ID | 级别 | 位置 | 问题 | 证据 |
|---|---|---|---|---|
| R-r1-01 | **P0** | `verification/…/tools/crash-ack.ps1:143-146`；`logs/crash-driver-attempt6.log:36` | **AC-H3-4 的 PASS 由硬编码常量构成**：`$passMessage` 直接写死 `gates_open=1 rows_unchanged=1 second_call_idempotent=1`，脚本全文**没有**任何 DB 查询、`read_gate` 统计、行数比较、源 sha256、二次调用帧计数。冻结 AC / scope §4.2 要求的 `Win32_Process` 后代枚举 + 30s 轮询证明「dotnet 子进程与全部 Python Core PID 均消失」**完全未实现**（只用 `$park.HasExited` 证明外层 `dotnet test` 退出）；`park.json` 也缺 `old_python_pids/park.db_counts/source_sha256`。⇒「实测 PASS 三重防伪全过」属**未经计算的断言**，违反「未证实记 NOT_RUN、不得把未跑写成 PASS」 | 脚本 143-146 行为字面常量；重跑同样输出，证明它不随实现行为变化；`verification/` 下无 `crash/<run-id>/`、无 `db_before/db_after`、无 `kill.json`、无 `frames.txt`、无 `sha256.txt` |
| R-r1-02 | **P1** | `git diff --name-only e9ab2ef7c..74e7737d5` 含 `tests/core/test_core_service.py` | **越界**：该路径**不在**卡面 `allowed_paths`（卡 21-40 行共 19 条，无此文件），也不在 scope r2 §2 的 19 条内。派发说明「DSH 已扩 `tests/core/test_core_service.py`，见卡」与卡面字节不符 ⇒ `diff ⊄ allowed_paths`，AC-H3-6 的该项自证不成立 | `Select-String 'tests/core' doc/tasks/FEA-11-HOST-AUTH-3.md` → 0 命中 |
| R-r1-03 | **P1** | `src/application/sources/materialization.py:103-137`；`tests/fea11/test_source_plan_materialization.py` | **AC-H3-2 过度声称**：契约 `:285`/卡面 AC-H3-2 要求「`body_json` 缺 `kind/source_id/entries/reference_set_digest` 或非 JSON → `SOURCE_PLAN_UNAVAILABLE`」，实现只校验 body/target 是 dict 与 `version_id`，`kind/source_id/reference_set_digest` 缺失时**原样返回 `None`**，`target.status=ok` 但无 `entries` 时**静默返回 `[]`**；测试文件**无**上述负例（缺 kind / 缺 source_id / 缺 reference_set_digest / 缺 entries），也无「过期 applied 仍返回」与「脱敏 0 命中」用例（scope r2 §2 第 4 条明确要求这两项） | 实现 `body.get("kind")` 无守卫；grep 测试文件 `expires`/`reference_set_digest` 负例 → 无 |
| R-r1-04 | **P1** | 卡面 AC-H3-3「拒绝矩阵 6 例」 vs scope r2 §3 AC-H3-3 | **AC 语义被实现方改写且未走 r3**：冻结矩阵为「state≠applied；`material.source_id`≠journal；`baselines.Count≠1`；registry 撤销；root 不可读/identity 变；registry root 数≠1」，现卡面改成「state≠applied；无 source/version；kind 缺失；撤销；registry 缺失；mint seam 不可用」，**删掉了 source 不符与 `baselines!=1`**；实现 `MintRecoveryGrantsAsync:265-306` 对多 baseline **逐个 mint**（不判 `Count!=1`），`baselines` 为空时直接返回空 grants，交给 Core 报错而非 typed 拒绝。scope r2 §9 明写「改动 §3 的 AC 语义需重做 r3」 | `SourceOperationCoordinator.cs:265-306`；卡 71 行 vs scope 103 行 |
| R-r1-05 | **P1** | `verification/FEA-11-HOST-AUTH-3/` 目录 | **证据清单缺项**：冻结证据计划要求 `crash/<run-id>/{park.json,recover.json,kill.json,db_before,db_after,frames.txt,sha256.txt}`、脱敏 wirelog、kill 前后 PID 列表、源文件 sha256、`README.md` 状态表（每项 PASS/FAIL/NOT_RUN + 命令/时间/head/EXIT）。实际只有 `logs/`、`mutations/`、`tools/`，**无 crash 目录、无 README.md、无 wirelog、无 DB 导出、无 PID 列表** ⇒ AC-H3-6 证据项不成立 | `Get-ChildItem -Recurse verification/FEA-11-HOST-AUTH-3 -File` 全量列表 |
| R-r1-06 | **P2** | 同 R-r1-01 | 三重防伪 ③「`used_grant_ids` 不出现在任何 journal 文件字节中」**未执行且近乎恒真**：journal 是加密容器（`NMSOP1` 二进制），任何 grant id 都不会以明文出现；同时实现**主动**把重铸 grant id 写回 journal（`PrepareCompletion` 411-413 行、`AcknowledgeAsync` 终态 495 行、`RecoverAsync` 606 行），与冻结 AC ③ 的字面语义（「grant_id 不在 journal」）直接冲突 | 重跑产物 journal `op-*.v1.dat` 为密文；`GrantIds = string.Join(",", recoveryGrants)` |
| R-r1-07 | **P2** | `SourceOperationCoordinator.cs:309-312,411-413,427-430` | `PrepareCompletion` 新增的 `recoveryGrantIds` 形参在**两个调用点都传 null**（`AcknowledgeAsync:449`、`RecoverAsync:562`）⇒ 411-413 的 `GrantIds` 分支为死代码，427-430 的「不得复用」分支永不生效；「terminal record 记录 fresh grants」全靠后续 `with` 覆盖，参数是悬空 API | 两处调用点 |
| R-r1-08 | **P2** | 语料 | **M1 无证据**：卡面 AC-H3-5 以「拒绝矩阵第 6 例（mint seam 不可用→`CORE_UNAVAILABLE`）」替代 M1，但冻结 M1 是「重铸改为复用 journal GrantIds → phase2 typed `SOURCE_ACCESS_DENIED`、gates pending、行数不变」，两者证明的命题不同（前者证明 fail-closed，不证明「复用会被抓」）。`mutations/` 只有 M2–M6 | `ls mutations/` → 5 份 |
| R-r1-09 | **P2** | `Materialization` 零写口径 | AC-H3-2 的「同一 fixture 前后**逐表相等**（契约 §6.2）」实际只对 `_FakeStore` 记录写调用（`test_source_plan_materialization.py:21-42,87-90`），**没有真实 SQLite 逐表对拍**；`SOURCE_BUDGET_EXCEEDED` 的 8MiB 分支也无测试覆盖（只测 entries>10000） | 测试文件通读 |
| R-r1-10 | **P3** | `SourceOperationCoordinator.cs:184-206` | 新 XML doc 被插到旧 `PrepareCompletion` doc 之上，形成**两个连续 `<summary>` 块**挂在 `MintRecoveryGrantsAsync` 前，`PrepareCompletion` 失去自己的 doc —— 注释结构损坏 | 184-206 行 |
| R-r1-11 | **P3** | `CoreServiceClient.cs:1622-1645` | 客户端对缺字段静默降级（`ReadString(...) ?? string.Empty`、ordinal 缺省 0、entries 非数组→空），会把 Core 的协议违规吞成「看起来合法」的对象，与 Host 侧 fail-closed 基调不一致 | 方法体 |
| R-r1-12 | **P3** | `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` | scope r2 §2 第 17-19 条标注「DSH 生命周期（Owner 不得改）」，本卡 `owner: dsh`，实现提交一并改了这三份状态文件。虽在 allowed_paths 内、DSH 双重身份下可解释，但与 r2 字面口径冲突，需在 lifecycle 提交里由 DSH 明确认领 | 三份 diff |

## 3. AC 逐项判定

| AC | 判定 | 依据 |
|---|---|---|
| **AC-H3-1** 契约与字节不回退 | **MET** | `verify_pins` 18/18（`C17 cdeee4872e29`）；`FEA-C17_SOURCE_SYNC_DRAFT.md` SHA-256 = `CDEEE487…FC96C`；diff 不含任何「不列入」清单文件（`HostCommandRegistry.cs`/`HostCommandDispatcher.cs`/`source_read_refs.py`/`runtime.py`/`source_sync.py`/`ports.py`/C-07 inventory/其余 17 契约/`FEA-11-HOST-AUTH-2` 证据） |
| **AC-H3-2** Core 新命令 | **PARTIAL** | 已实现且绿：host-control 注册/分发、closed shape/类型负例、NOT_FOUND/STALE/UNAVAILABLE/BUDGET、ordinal 升序唯一、missing→null+`[]`、capability 仅 ping、`Capabilities` 仍 7 项、零写（fake store）。**不成立**：body 缺 `kind/source_id/reference_set_digest/entries` 未 typed 拒绝且无负例（R-r1-03）、无「过期 applied 仍返回」用例、无脱敏 0 命中证据、零写未做真实逐表对拍（R-r1-09） |
| **AC-H3-3** Host 重铸 | **PARTIAL** | completion 已不再用 journal `GrantIds`（`prepared with { GrantIds = recoveryGrants }`），每 registry `Authorize` 后经 `IssueForRecoveryAsync`→`IssueAsync` mint（TTL 语义未改），6 例 typed 拒绝实测通过、journal 保持 `core-committed` 未 ACK。**不成立**：冻结矩阵被改写并删项、多 baseline 不判 `Count!=1`（R-r1-04）；拒绝路径中 `PrepareCompletion` 已把新 `AuthorizationJson/AuthorizationDigest` 落盘（字节已变），与冻结「journal 授权字节不变」不一致；`recoveryGrantIds` 为死参数（R-r1-07） |
| **AC-H3-4** 真实 kill 恢复一次 | **PARTIAL（不足以判 MET）** | 真实存在 `CRASH_POINT=PASS` 且含派发要求的全部字段，我也**重跑复现 EXIT=0**；独立核验重跑产物：PID/session/grant 三项确实不同、`read_gate=open/0 pending`、行数 1/2/1、`commit_digest` 一致。但冻结 AC 的**可判别性**未建立：Python sidecar 死亡未证明、`gates_open/rows_unchanged/second_call_idempotent` 是常量而非测量（R-r1-01）、无 `db_before` 可对拍、无源 sha256、无二次调用帧计数、三重防伪 ③ 未执行且恒真（R-r1-06）。按冻结口径「未证实 → NOT_RUN」，**不得记 PASS** |
| **AC-H3-5** 变异判别 | **PARTIAL** | M2/M3/M4（pytest `EXIT=1`，`1 failed`）与 M5/M6（dotnet `EXIT=1`，失败栈行号可对）均**真实 RED**；M6 确由「猜 kind」被 `Recovery_RefusesAnUnknownCoreSourceKind` 抓住。**缺口**：M1 无日志、以另一命题替代（R-r1-08） |
| **AC-H3-6** 门禁/范围/不夸大 | **FAIL** | `check.ps1` PASS、`verify_pins` 18/18、全量 pytest `3461/0/10`、8 项目 .NET `1810/0/109` 均真实（我核过汇总行与 EXIT）；但 **`diff ⊄ allowed_paths`**（R-r1-02）、**证据目录缺冻结产物与 README 状态表**（R-r1-05）、`generate_api_inventory --check` 我未复跑（NOT_RUN） |

## 4. 越界与「不得改动」核对

- 改动文件全集 = 卡面 allowed_paths **除** `tests/core/test_core_service.py`（**越界**，R-r1-02）。
- `HostCommandRegistry.cs` / `HostCommandDispatcher.cs`：**零改动**；`src/application/sources/runtime.py`、`src/infrastructure/resource_channel/source_read_refs.py`、`src/infrastructure/sqlite/source_sync.py`、`src/application/sources/ports.py`、`doc/contracts/FEA_C07_API_INVENTORY.md`、C-17 三件套与其余 17 契约：**零改动**（`git diff --name-only` 不含）。
- 新命令只进 `_HOST_CONTROL_COMMANDS`，未进 `_SOURCE_SYNC_APP_COMMANDS`；`Capabilities` DTO 未加第 8 项；**无 schema/migration**。
- 工作树 clean；未发现 push/commit 越权（`main` 上 6 个实现提交，属实现方正常交付）。

## 5. 必须处理（阻塞项）

1. **R-r1-01**：把 AC-H3-4 的断言真正实现（Win32_Process 后代枚举 + 30s 轮询证明 Python 全灭、`db_before/db_after` 行数、`read_gate`、源 sha256、二次调用帧数、journal 对拍），或按冻结纪律把 AC-H3-4 改为 `NOT_RUN/PARTIAL` 并撤回「三重防伪全过」措辞；**不得保留硬编码 PASS 数字**。
2. **R-r1-02**：`tests/core/test_core_service.py` 要么回退，要么由 DSH 以**卡面字节**正式扩入 allowed_paths 并在卡面留痕（当前派发说明与卡面不一致）。
3. **R-r1-03/04**：补齐 AC-H3-2 缺失负例（含「过期 applied 仍返回」、脱敏 0 命中、真实逐表零写）；AC-H3-3 冻结矩阵的删项要么恢复实现，要么按 scope r2 §9 走 r3 重定 AC。
4. **R-r1-05**：补 `verification/.../crash/<run-id>/` 全套 + `README.md` 状态表（逐项 PASS/FAIL/NOT_RUN + 命令/时间/head/EXIT）。

## 6. 结论

- **verdict：`changes_requested`**（P0=1、P1=4、P2=4、P3=3）。
- 实现主体可用（Core 投影与 Host 重铸方向正确、聚焦测试全绿、真实崩溃路径在本机能跑通），但**AC-H3-4 的证据不成立、AC-H3-6 的越界与证据缺项成立**，故 6 条 AC 中 **1 MET / 4 PARTIAL / 1 FAIL**，不能进入集成。
- **复审口径**：修复后按同一 base 重交；若修改 §3 AC 语义或 allowed_paths，需先重做 scope r3。本报告只写此文件，不构成对任何实现/契约的批准。
