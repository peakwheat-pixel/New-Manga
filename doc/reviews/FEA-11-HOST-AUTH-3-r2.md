# FEA-11-HOST-AUTH-3 实现 Review r2（独立上下文只读子代理）

| 项 | 值 |
|---|---|
| 审查者 | 独立上下文 fresh subagent（父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`；本会话 id 未在运行提示中暴露；**未参与** FEA-11-HOST-AUTH-1/2/3 的实现、返修、证据生成或卡面起草） |
| reviewer_kind | `subagent`（由 DSH 派发；只读被审 head；仅写本文件） |
| 模式 | 只读 + 允许的实测：read/grep/glob、只读 git、`check.ps1`/`verify_pins.ps1`/`generate_api_inventory.py --check`、聚焦 pytest。**未重跑** `crash-ack.ps1`（该脚本 `:191-208` 会向 `verification/…/crash/<run-id>/` 写新产物，超出本轮「只允许写一个文件」的授权）；未改生产源码/测试/契约；未 commit/push |
| 被审 head | **`d303b9a3f`**（`main`）；r1 被审 head `74e7737d5`；base `e9ab2ef7c` |
| r1 → r2 增量 | `git diff --stat 74e7737d5..d303b9a3f` = 26 files, **+801 / −56**（实现侧仅 `SourceOperationCoordinator.cs` +52/−?、`Fea11HostAuthIpcTests.cs` +35、`materialization.py` +12、`test_source_plan_materialization.py` +154/+112） |
| 审查输入 | 卡 `doc/tasks/FEA-11-HOST-AUTH-3.md`；scope r2 `doc/reviews/FEA-11-HOST-AUTH-3-scope-r2.md`；r1 `doc/reviews/FEA-11-HOST-AUTH-3-r1.md`；C-17 v1.2 冻结记录/载体；`verification/FEA-11-HOST-AUTH-3/**`；base..head 全量 diff |
| **verdict** | **`changes_requested`** |
| 计数 | **r1 12 条：FIXED=5 / PARTIAL=5 / OPEN=2**；**新增：P0=0 / P1=2 / P2=4 / P3=1** |

## 0. 一句话结论

r1 的 **P0（崩溃驱动 PASS 由硬编码常量构成）已实质修复**：`crash-ack.ps1` 的 8 个 `CHECK` 现在从 `park.json`/`recover.json` 的记录事实计算，PID 树枚举 + kill 后 30s 轮询、`db_counts`/`source_sha256`/`gate_open`/`second_call_frames`、`crash/<run-id>/` 归档均已落地，`recover.json` 的每项数值又由真实 Core + 真实 SQLite 查询（`check_gate.py`/`count_bindings.py`/文件 SHA-256/wire 行数）产生；三条聚焦门禁（pytest 245、`check.ps1`、`verify_pins` 18/18）复跑全绿。但**仍不能判 approved**：AC-H3-4 被记 `<<MET>>` 而冻结断言仍有 3 处未证（**缺 crash 反例**、缺 `page_bindings` 字段级一致、③ 的 journal 字节 grep 未执行），AC-H3-2 的 `entries` 缺字段仍静默降级，AC-H3-3 冻结拒绝矩阵的 3 例仍无测试且卡面矩阵未恢复，且**全量 pytest/.NET 证据早于被审 head**。这些都是「可观测、可补证」的缺口，不是方向性返工。

## 1. 门禁与实测（本轮亲自执行，2026-11-10 00:39–00:42 +08:00）

| 项 | 命令 / 对象 | 结果 |
|---|---|---|
| 聚焦 pytest | `python -m pytest tests/fea11 tests/core/test_core_service.py -q` | **`245 passed, 9 warnings in 12.80s`；EXIT=0** |
| 治理（指定卡） | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-HOST-AUTH-3.md` | `Governance check: PASS (3 warnings)`；**EXIT=0**（warnings：12 个非终态 Task / `STATUS.md` 80% / `REBASELINE_PLAN.md` 80%） |
| 契约 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **`PIN AUDIT: PASS (all 18)`**，`C17 cdeee4872e29`；**EXIT=0** |
| C-17 字节 | `Get-FileHash doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md` | `CDEEE4872E29B56C7D67DE65DABD6CA9B31006EECDE61D99B83E29FE5A4FC96C` = 冻结值，零变化 |
| API inventory | `python tools/generate_api_inventory.py --check` | **EXIT=0**（C-07 零增量） |
| 工作树 | `git status --short` | 空（本文件写入前） |
| 崩溃驱动重跑 | `crash-ack.ps1`（`NEWMANGA_FEA11_IPC=1`） | **NOT_RUN** —— 脚本会把新 `crash/<run-id>/` 写进仓库，越出本轮单文件写权限；只做**归档产物静态核验**（§3 R-r1-01） |
| 全量 pytest / 全量 .NET | — | **NOT_RUN**（不重跑；仅日志复核，见新 finding R-r2-02 的时效问题） |
| `git diff --name-only e9ab2ef7c..d303b9a3f` | 25 个路径 | 全部 ⊆ 卡面 allowed_paths（含新增第 20 条 `tests/core/test_core_service.py`），**diff ⊆ allowed_paths 成立** |

## 2. r1 findings 逐条判定

| ID | r1 级别 | 判定 | 依据（本轮核验） |
|---|---|---|---|
| **R-r1-01** | P0 | **FIXED** | `crash-ack.ps1:158-189` 的 8 个 `CHECK` 全部由 `park.json`/`recover.json` 计算（`:160-178`），失败即 `exit 12`；PID 树 `Get-DescendantPids`（`:87-105`）+ 无 python → `exit 11`（`:114-117`）+ kill 后 30s 轮询（`:129-140`，存活 → `exit 11`）真实存在；`park.json` 含 `db_counts`/`source_sha256`/`wire_lines`，`recover.json` 含 `gate_open`/`second_call_frames`/`db_counts`/`source_sha256`；`crash/<run-id>/` 两套归档各含 `park.json`/`recover.json`/`pids-before.txt`/`pids-after.txt`（0 字节=全灭）/`library.db`/`wire-redacted.ndjson`；归档 run `e8e3…` 对应 `logs/crash-driver-attempt10.log` 的 `CHECK ×8 = 1`、`CRASH_POINT=PASS`、**EXIT=0**。残余（P3，已在 §4 记录）：PASS 行仍有 `acknowledge_once=1`/`sidecar_proven_dead=1` 两个字面量（但均已被前置 `exit 10/11` 守卫）、轮询集合不含根 `dotnet test` PID、§4.1 要求的 `kill.json`/`db_before`/`db_after`/`frames.txt`/`sha256.txt` 未单独归档 |
| **R-r1-02** | P1 | **FIXED** | 卡面 `:34-36` 已把 `tests/core/test_core_service.py` 正式列入 allowed_paths 并写明扩域理由（C-17 v1.2 capability 列表断言）；该文件 diff 仅 **2 处期望值追加**（`git diff` 实查），未放宽断言。过程残余：scope r2 §9 规定改 §2 文件集合需重做 r3，本次由 DSH 以卡面字节自行扩域，属流程越权的最小化处置（P3，建议在 lifecycle 提交里认领） |
| **R-r1-03** | P1 | **PARTIAL** | 已修：`materialization.py:105-116` 对 `kind`/`source_id`/`reference_set_digest` 缺失或非字符串 → `SOURCE_PLAN_UNAVAILABLE`；负例 `test_missing_required_body_field_is_unavailable`（`:189-209`）；过期 applied 用例 `:212-218`；无路径/secret 用例 `:221-228`。**未修**：`target.entries` 缺失时 `_entries_of`（`:56-59`）仍静默返回 `[]`，与冻结 AC-H3-2「`body_json` 缺 `kind/source_id/entries/reference_set_digest` … → `SOURCE_PLAN_UNAVAILABLE`」不符，且无 `entries` 缺失负例；`test_projection_carries_no_absolute_path_or_secret` 的断言 `"source-v" not in text or ":\\" not in text` 对默认 fixture 近乎恒真（未注入绝对路径/locator 反例） |
| **R-r1-04** | P1 | **PARTIAL** | 已修：`MintRecoveryGrantsAsync:249-255` 现在 `baselines.Count != 1` → typed `SOURCE_ACCESS_DENIED`；多 readable root → `SOURCE_ACCESS_DENIED`（`:276-280`）。**未修**：冻结矩阵的「`material.source_id` ≠ journal/plan」**未实现**（`:210-213` 只判空）；`baselines!=1`、多 root、identity 漂移三类**均无单测**（`Fea11HostAuthTests` 的 6 例仍是 state/无 source/kind/撤销/registry 缺失/mint seam）；卡面 `:74` 拒绝矩阵仍是被改写的 6 例，未恢复冻结 6 例，按 scope r2 §9 需 r3 |
| **R-r1-05** | P1 | **PARTIAL** | 已修：`README.md` 有状态表，`crash/<run-id>/` 两套产物齐备（park/recover/pids/wirelog/library.db）。**未修**：README 状态表缺 AC-H3-6 要求的**逐项命令/时间/head/退出码**（只有「结果」一列）；冻结 §4.1 的 `kill.json`/`db_before`/`db_after`/`frames.txt`/`sha256.txt` 未归档；归档 run `289e…` **没有任何 driver 日志引用**（`logs/` 中不出现该 run-id），属孤立证据 |
| **R-r1-06** | P2 | **PARTIAL** | ①「park vs recover grant ids 无交集」已**真实比较**（`crash-ack.ps1:173-178`，`fresh_grant` 由 `park.grant_ids`/`recover.grant_ids` 计算）。②「`used_grant_ids` 不出现在任何 journal 文件字节中」**仍未执行**（脚本无 grep，归档也未含 journal 副本）；③实现仍主动把重铸 grants 写回终态 journal（`SourceOperationCoordinator.cs:495`、`:604`），卡面 `:75` 只**陈述**「终态 journal 记录重铸 grants」，未给出理由、未与冻结 AC ③ 对齐 |
| **R-r1-07** | P2 | **FIXED** | `PrepareCompletion` 签名已删死参数（`:315-316`），`:410-414` 的 `GrantIds` 分支已删，两个调用点（`:447`、`:561`）不再传参；`git grep recoveryGrantIds` 仅剩注释，编译面由崩溃驱动的 Release 构建验证 |
| **R-r1-08** | P2 | **FIXED** | `mutations/M1-journal-grant-reuse.log`：真实变异（恢复改为复用 journal grants）在 `CrashPoint_Recover` 阶段被 **`SOURCE_ACCESS_DENIED`「source-read grant is not registered」** 抓住，**EXIT=12**，与冻结 M1 期望一致。残余（P3）：卡面 `:76` 仍写「M1 由拒绝矩阵第 6 例判别」与日志不符；`mutations/` 仍只有失败输出、无变异 diff |
| **R-r1-09** | P2 | **PARTIAL** | 已修：真实 SQLite 逐表指纹对拍（`test_source_plan_materialization.py:231-304`，建真库 + 全表 SHA-256 前后相等）。**未修**：`test_body_budget_over_eight_mebibytes_is_typed`（`:307-340`）用 60000 entries，先命中 `_MAX_ENTRIES=10000` 分支（`materialization.py:62-63`），**8MiB 序列化大小分支（`:144-148`）从未被执行**；用例名与实际走的分支不符 |
| **R-r1-10** | P3 | **FIXED** | `PrepareCompletion` 的 XML doc 已回到方法前（`:299-314`），`MintRecoveryGrantsAsync` 前只剩自己的 doc（`:185-190`），无连续双 `<summary>`。（`RetryFailed` 前 `:612-617` 的双 summary 在 r1 head 即存在，非本卡引入，未计入本轮） |
| **R-r1-11** | P3 | **OPEN** | `CoreServiceClient.GetSourceSyncPlanMaterializedAsync` 仍用 `ReadString(...) ?? string.Empty`、ordinal 缺省 `0`、entries 非数组→空（本轮未改动该文件），缺字段静默降级仍在 |
| **R-r1-12** | P3 | **OPEN** | `doc/STATUS.md`/`doc/REBASELINE_PLAN.md`/`doc/TASK_LEDGER.md` 仍只有实现轮提交，无 DSH lifecycle 认领提交 |

**计数：FIXED=5（R-r1-01/02/07/08/10）/ PARTIAL=5（R-r1-03/04/05/06/09）/ OPEN=2（R-r1-11/12）。**

## 3. 新增 findings

| ID | 级别 | 位置 | 问题 | 证据 | 建议 |
|---|---|---|---|---|---|
| **R-r2-01** | **P1** | 卡 `:75`；`Fea11HostAuthIpcTests.cs:205-316`；`crash-ack.ps1` | **AC-H3-4 被记 `<<MET>>`，但冻结 AC 仍有 3 项未证**：①冻结 AC 要求的**崩溃反例**（phase1→phase2 之间替换源文件 → typed 拒绝、零写、gates pending、退出码≠0；scope §2.2 第 12 条）**在 harness 中不存在**（`Fea11HostAuthIpcTests` 只有 4 个 IPC 用例，全仓库 `CrashPoint` 仅 Park/Recover）；②「`page_bindings` 相关字段与 phase1 导出**逐字节一致**」只做了行数比较（`recover.json.db_counts`），无字段级导出/豁免清单；③三重防伪 ③ 的 journal 字节 grep 未执行且无 journal 副本。⇒ 按冻结「全部满足才算 PASS」不能记 MET | 测试文件用例清单；`park.json`/`recover.json` 字段；`crash-ack.ps1` 无 journal/grep 逻辑 | 补反例 harness（同 IpcFixture，替换 `newZip` 后 recover 必须 typed 拒绝），补 `page_bindings` 字段级导出对拍与 journal grep，或把 AC-H3-4 降级 `PARTIAL` 并撤回 `<<MET>>` |
| **R-r2-02** | **P1** | `logs/dotnet-*.log`（00:18–00:19）；`logs/pytest-full.log`（00:25）；head `d303b9a3f`（00:36） | **全量门禁证据不覆盖被审 head**：`bd1fd467e`（00:32）改了 C#（删死参数 + 单 baseline），`d303b9a3f`（00:36）又新增 2 个 Python 用例，而全量 .NET 日志早于 C# 改动、全量 pytest 日志早于 head；卡面 AC-H3-6 却记 `<<MET>>`（`1810 passed / 0 failed`、`3461 passed`）。本轮实测只覆盖聚焦面（245 passed） | 日志时间 vs 提交时间；`pytest --collect-only` 当前该新增文件收集 **21** 条（全量日志时点更少） | 在 head `d303b9a3f` 上重跑全量 pytest/.NET 并替换日志，或在卡面把全量项标为「按 r1 head 基线、head 仅增量测试」 |
| **R-r2-03** | P2 | `verification/…/crash/<run-id>/wire-redacted.ndjson:5,21` | **AC-H3-2 脱敏 0 命中不成立**：归档 wirelog 中 `"signature":"<32 字符值>"` 出现 **2 次**（`signing_key` 值已 `[REDACTED]`、`path` 已 `[REDACTED]`），而冻结 AC 写明 wirelog「0 命中 … `signature`/`secret_ref`」；绝对路径/`secret_ref` 实测 0 命中 | 本轮 `Select-String` 实查（`G:\`/`C:\`/`secret_ref`=0；`signature`=2） | 把 signature 值纳入脱敏并重导归档 wirelog，或由 DSH 在 AC errata 中明确 signature 非敏感/保留理由 |
| **R-r2-04** | P2 | `README.md`、`crash/<run-id>/`、`logs/crash-driver-attempt*.log` | 证据可追溯性不足：①README 状态表无「命令/时间/head/EXIT」列；②归档 run `289e…` 无对应 driver 日志（该 run 的 park/recover 自洽，但无法证明由脚本产生）；③attempt8 的 PASS run `647e…` **未归档**，归档的 `289e…` 无日志，三者交叉不一致；④M1–M6 仍无变异 diff | `logs/` 全文检索 run-id；`git diff --stat` 归档文件清单 | 以 attempt10 为准统一卡面/README 引用；补 289e 的 driver 日志或删除孤立归档；变异 diff 入 `mutations/` |
| **R-r2-05** | P2 | `tests/fea11/test_source_plan_materialization.py:307-340` | R-r1-09 残余：所谓 8MiB 预算用例用 60000 entries，先被 `_MAX_ENTRIES` 拦截，**8MiB 序列化分支未覆盖**；一旦 `_BUDGET_BYTES` 校验被删/写错，该用例仍 RED 于条目数分支，测不出目标缺陷 | `materialization.py:62-63` 的判定顺序；用例 entries 数 | 用 ≤10000 条、每条 ~900B 的 locator 构造 >8MiB 响应，或单独单测预算函数 |
| **R-r2-06** | P2 | `SourceOperationCoordinator.cs:490-495,600-604`；AC-H3-4 ③ | R-r1-06 残余：三重防伪 ③ 的 journal 字节 grep 仍未实现，归档也无 journal 副本；实现**主动**把重铸 grants 写入终态 journal，卡面只陈述事实、未说明「为何必须记录」以及为何这仍满足冻结 ③ | 源码两处 `GrantIds = string.Join(",", recoveryGrants)`；卡面 `:75` 措辞 | 在卡面写明审计理由（或撤回记录），并实现/明确 ③ 的可判别形式（如：journal 密文 → 用 Host 解密后断言 grant id 存在，而非字节 grep 的恒真断言） |
| **R-r2-07** | P3 | 卡 `:75` | 卡面写「驱动 attempt 6」「日志 `logs/crash-driver-attempt8.log`」，实际归档 PASS 是 attempt10（`e8e3…`）；attempt8 的 PASS run 未归档。证据引用与事实不一致 | attempt8/attempt10 日志与归档 run-id 对照 | 统一为 attempt10 + `crash/<run-id>/` |

**新增计数：P0=0 / P1=2（R-r2-01/R-r2-02）/ P2=4（R-r2-03…06）/ P3=1（R-r2-07）。**

## 4. AC 逐项判定

| AC | 判定 | 依据 |
|---|---|---|
| **AC-H3-1** 契约与字节不回退 | **MET** | `verify_pins` 18/18（`C17 cdeee4872e29`）；C-17 SHA-256 未变；diff 不含「不列入」清单 |
| **AC-H3-2** Core 新命令 | **PARTIAL** | 通道/closed shape/typed 矩阵/升序唯一/missing 目标 null/过期 applied/真实逐表零写均成立（本轮 245 passed 覆盖）；**缺 `entries` 缺失的 typed 拒绝与其负例**（R-r1-03 残余）；**wirelog 脱敏不达 0 命中**（R-r2-03） |
| **AC-H3-3** Host 重铸 | **PARTIAL** | completion 已用重铸 grants、6 例 typed 拒绝绿、journal 保持 `core-committed`；单 baseline 与多 root 已 fail-closed 但**无测试**，冻结矩阵的 source 不符未实现、卡面矩阵未恢复（R-r1-04） |
| **AC-H3-4** 真实 kill 恢复一次 | **PARTIAL** | 核心断言现已**由真实测量产生**（8 CHECK、PID 树 12+1、30s 轮询全灭、gate open、行数/源 sha/0 帧、`fresh_grant` 不相交），真实存在 PASS（attempt10/EXIT 0）；**冻结 AC 的 3 项仍未证**：crash 反例缺失、`page_bindings` 字段级一致缺失、③ journal grep 缺失 ⇒ 不能记 MET（R-r2-01） |
| **AC-H3-5** 变异判别 | **MET** | M1（真崩溃驱动 RED，EXIT 12 + `SOURCE_ACCESS_DENIED`）与 M2–M6 日志齐备；残余 P3：卡面 M1 措辞陈旧、无变异 diff |
| **AC-H3-6** 门禁/范围/不夸大 | **PARTIAL** | `check.ps1`/pins/API inventory/工作树/diff ⊆ allowed_paths 成立；**全量 pytest/.NET 证据早于 head**（R-r2-02）、README 状态表与 §4.1 产物不完备（R-r1-05 残余） |

## 5. 结论

- **verdict：`changes_requested`**。
- **已确认修复**：r1 的 P0 驱动造假已消除（真实计算 + PID 证明 + 归档）；越界扩域已以卡面字节留痕；死参数、注释顺序、M1 证据、真实 SQLite 零写对拍均落地；`check.ps1`/`verify_pins`/聚焦 pytest 全绿，工作树 clean。
- **阻塞项（按优先级）**：① R-r2-01（AC-H3-4 三处冻结断言未证却记 MET）；② R-r2-02（全量门禁证据早于 head）；③ R-r1-03 残余（`entries` 缺字段静默降级）+ R-r2-03（wirelog signature）；④ R-r1-04 残余（冻结拒绝矩阵 3 例无测试 / source 不符未实现 / 卡面矩阵需 r3）。
- **口径**：本轮未重跑 `crash-ack.ps1`（写权限约束），故 AC-H3-4 的结论基于**归档产物 + 脚本 + 测试源码**的独立复算，不构成对实现者 PASS 的转述；如需以「本轮重跑 PASS」结项，应授权写 `verification/.../crash/<run-id>/` 后重跑。
- 本报告只写此文件，不构成对任何实现/契约的批准，不改变 `FEA-11-HOST-AUTH-2` 的 `AC-F3 = NOT_APPLICABLE`。
