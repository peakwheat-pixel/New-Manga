---
task_id: FEA-12-CORE
reviewer: dsh-fea12-core-r3 (fresh subagent; session 0ac9f6c1-fab3-4063-982c-dcfaf53f6f9d)
reviewer_kind: subagent
review_session_id: 0ac9f6c1-fab3-4063-982c-dcfaf53f6f9d
parent_agent_id: session-8db9dae5-49df-4d09-ac62-696f0805a95c
base_commit: e47fd47e
reviewed_head: 32ef1dc31
decision: changes_requested
---

# Review r3：FEA-12-CORE（Codex OVERTURN 3a/4 返修复审）

> 审查身份：独立上下文 fresh subagent；未参与 FEA-12-CORE 的实现、r1/r2/r3 返修、分片 A/B 设计、UNFREEZE 提案/复核，亦未在 r1/r2 Review 中担任审查者。会话 `0ac9f6c1-fab3-4063-982c-dcfaf53f6f9d`，父会话 `session-8db9dae5-49df-4d09-ac62-696f0805a95c`。
> 审查范围：`base_commit=e47fd47e` → `reviewed_head=32ef1dc31`；重点为 r3 自有提交 `41703da92`（实现/测试/证据）、`659c679be`（卡/Handoff）、`32ef1dc31`（最终 head 定稿），以及它们相对 UNFREEZE `fc9833479` 的契约基线。
> 审查方式：只读仓库；全部复跑日志、探针、变异实验与报告写在仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-core-r3\`；未 commit/push/stash，未改仓库受跟踪文件；审查结束时 `git status --porcelain` 为空。

## 0. 结论摘要

**P0=0，P1=1，P2=1，P3=6。decision: changes_requested。**

Codex OVERTURN 的**运行时语义**已真实修复，且不是测试空转：

- **3a（current 全量绑定）**：`currentRegionRevisionIds` 取自 `region_current_pointers` 的**全部 region**（含 lineage-hidden；不按可见性裁剪），`currentArtifactRevisionIds` 取自全部 artifact current；两数组字典序排序去重；`currentRevisionId` 仅展示值且**已移出 digest v2**。非首个 current、hidden current（我用独立探针改 hidden region current）、artifact current 增删改、集合增删都会改变 digest，旧 digest 确认返回 `BOOK_DELETE_STALE_PREVIEW` 且零副作用。golden v2 的 14 键 canonical、单书/集合/重排向量均被我独立复算一致。
- **4（retry 集合级 digest）**：manifest JSON additive 持久化 `batch_id`/`original_book_ids`/`original_collection_digest`/`book_id`/`inventory_digest`/`inventory_inputs`；retry 为原预览有序集合的保序 pending 子集，集合级 `inventory_digest` 原样回传 manifest 值，逐书对 manifest 值校验并用 `inventory_inputs` 重算检测篡改；mixed live+retry 一律 STALE；单条=逐书、批量=集合级的形状分支成立。原 `FAKE_DIGEST` 通过路径已改为拒绝断言。
- **独立复跑**：相关组 **1114 passed**、全量 **3162 passed / 10 skipped**、定向 **54 passed**、`check.ps1 -TaskPath`/全量 check **PASS (3 warnings)**、pins **18/18 PASS**，均与卡面/HANDOFF 一致；golden 与 isolation 探针重放 `all_match/pass = true`。
- **变异反证**：禁用 current 数组绑定 → 3 条 current 绑定测试精确失败；删除 retry 集合级比较 → 3 条 retry 测试精确失败；关闭 `inventory_inputs` 重算 → 篡改测试失败。测试有判别力。

**但当前 head 仍有两个不可批准的缺口**：

1. **P1（门禁证据缺失 + 卡面不实）**：冻结载体 §5-1 明确要求“hidden region current 变化 → 旧 digest STALE 零副作用”的判别测试；卡面 AC4/AC5、实施记录 §2.8/§8、Handoff §3 均声称已覆盖，但仓库内**没有**任何测试修改 hidden region 的 current 后再确认删除。现有 `test_preview_current_revision_uses_lineage_visibility` 只断言 hidden current 进入绑定集合、代表值为 null，不修改 current、不比较 digest、不执行删除。我在仓外探针中确认**运行时行为正确**，故这是“门禁证据/记录真实性”缺口，不是运行时缺陷；但对精确的 Codex OVERTURN 3(a) 反例没有 CI 回归保护，且卡面不能据此自称判别测试齐备。
2. **P2（冻结错误分类偏差）**：`book_cleanup_manifests.targets_json` 是**损坏 JSON**（不是“无 manifest 行”）时，单条 retry 返回 `BOOK_NOT_FOUND`、批量返回 `BOOK_DELETE_BATCH_PREFLIGHT_FAILED`（item=`BOOK_NOT_FOUND`）；UNFREEZE 载体 §A3 与 M2-C1 rev 2.14 §5.11.1a 的单一映射表写明 **manifest 缺失/损坏/篡改 → `BOOK_DELETE_STALE_PREVIEW`**。行为仍是 fail-closed、零副作用，但冻结的 typed 错误分类被偏离；现有测试只覆盖“无 Book 行且无 manifest → BOOK_NOT_FOUND”，未覆盖“行存在但 JSON 损坏”。

**AC 判定建议**：AC4 **可恢复 MET**（披露/只读/golden 均满足；仅需修 P3 文档口径）；**AC5 暂不能定稿 MET**（hidden current 变化缺仓库判别测试；corrupt manifest 分类偏差属于 AC5 的失败分类）；AC1–AC3、AC6–AC10、AC11、AC12 维持 MET。修复 P1/P2（测试为主 + 一处小错误映射 + 文档更正）后，建议以窄面复审确认，再 `done`；**不建议**以 `closed_with_limitations` 收口。

## 1. 审查对象、独立性与方法

- 开始时 `HEAD=32ef1dc315b7030f529f4ff7001f15e5edce8961`（与 `reviewed_head` 一致），`git status` 干净；工作树为 main，未 push。
- r3 自有提交：
  - `41703da92`：26 files，`src/application/library/service.py`、`src/bootstrap/core_service.py`、`src/infrastructure/sqlite/library.py`、两个删除测试文件、`verification/FEA-12-CORE/**`；
  - `659c679be`：任务卡 + Handoff；
  - `32ef1dc31`：任务卡一行证据 pin + `gates-core-py.log` 一行。
- 契约基线：UNFREEZE `fc9833479`；实测 `FEA-C04b_DELETE_PROTOCOL_DRAFT.md` sha256 `acc8f0e03d42…`、`M2-C1_TYPED_IPC_CONTRACT.md` sha256 `701093b52822…`，与卡面/冻结记录一致；`verify_pins.ps1` 18/18 PASS。
- 只读手段：仓库源码/测试/证据阅读；`pytest`（`-p no:cacheprovider`）；`check.ps1`；`verify_pins.ps1`；独立 digest/golden 复算脚本；独立 hidden-current/representative/corrupt-manifest 探针；仓外 `src+tests` 副本上的 3 项变异实验。未修改仓库、未 commit/push、未操作用户数据/真实回收站。

## 2. Codex OVERTURN 核销表

| 裁决 | 冻结要求 | 独立核实（不只看卡面） | 结论 |
|---|---|---|---|
| **3(a) current 仅代表值** | 预览 DTO 增 `currentRegionRevisionIds`（全部 region，含 lineage-hidden/separate/detached，不按可见性裁剪，字典序去重）与 `currentArtifactRevisionIds`（全部 artifact current，字典序去重）；`currentRevisionId` 仅展示且移出 digest v2；非首个/隐藏/artifact current 变化 → 旧 digest STALE 零副作用 | 代码逐 region/artifact 指针收集，`sorted(set(...))`；digest canonical 仅含两数组；hidden current 变化探针（仓外）显示 digest 变化、旧 digest STALE、Book 行保留、新 digest 成功；非首个/artifact/集合增删仓库测试通过；representative 变化（可见→隐藏，集合不变）digest 不变探针通过；golden v2 独立复算一致 | **运行时已闭合**；**hidden current 变化缺仓库判别测试（P1-1）**；representative 排序差异为已登记 residual（P3） |
| **4 混合 retry 绕过集合级 digest** | 集合级始终校验；首次=当前重算（单条逐书；批量集合）；retry=manifest `original_collection_digest` 原样回传 + `book_ids` 保序 pending 子集 + `inventory_digests` 逐项 manifest；mixed 拒绝；单条/批量形状分支；FAKE_DIGEST 转红 | 代码对 retry_ids 先取 manifest、校验同 `batch_id`/`original_book_ids`/`original_collection_digest`、保序子集、逐书 manifest 值、`inventory_inputs` 重算；mixed 在任何写前拒绝；`test_core_delete_commands.py` 原 FAKE 用例已改为 STALE 断言；变异 B（删除集合级比较）使 3 条 retry 测试失败 | **运行时已闭合**；corrupt manifest 分类偏差（P2-1） |
| **裁决 2 措辞更正** | M2-C1 rev 2.13 实为 166 insertions / 2 deletions，不得称“纯 additive/既有行零变化” | 卡「Codex 裁决与返修计划」、记录、Handoff 均已改为 166/2；M2-C1 rev 2.14 字节哈希匹配 | **核销** |
| **b/c 确认** | `pinnedRevisionIds` 两类 `is_pinned=1` 并集；`deletedFiles/Bytes` 含 catalog 派生文件口径 | 代码/测试未改该口径；r2 R-001 派生披露测试仍通过；golden derived 3 files/46 B 复算一致 | **核销（维持）** |

## 3. AC1–AC12 判定

| AC | 建议 | 依据/说明 |
|---|---|---|
| AC1 软删 | **MET** | r3 未改 A 流程；全量/相关组通过；`core-py-ac1` 证据与隔离探针 |
| AC2 恢复 | **MET** | 同上；r2 R-007 domain 接线保持 |
| AC3 回收站读取面 | **MET** | r3 未改投影；全量通过 |
| **AC4 只读预览** | **MET** | 两个 current 数组逐项返回（hidden 探针确认集合含 hidden current；representative 仅展示）；`currentRevisionId` 不在 digest；golden v2 独立复算一致；预览只读/无路径/无堆栈测试通过；catalog 派生披露保持。仅需修 P3 文档口径（如 `test_preview_current_revision_uses_lineage_visibility` 被误称为“hidden current 变化”测试） |
| **AC5 专门确认绑定** | **暂不能定稿 MET（PARTIAL）** | 非首个/artifact current 变化、单条/批量形状、key 覆盖、保序子集、原集合 digest、mixed 拒绝、篡改检测、纯 pending 幂等均通过仓库测试与我的变异反证；但：①hidden current 变化的仓库判别测试缺失（P1-1）；②corrupt manifest 的错误分类偏离冻结映射（P2-1）。行为层面 hidden 变化已由我的探针验证正确，修 P1/P2 后可恢复 MET |
| AC6 单事务/回滚 | **MET** | manifest 与删除同事务；AC6 注入异常后无 manifest、无行变化；全量通过 |
| AC7 保护披露/边界 | **MET** | r3 未改披露口径；测试通过 |
| AC8 共享引用/原文件 | **MET** | r3 未改 PD-08；隔离探针通过 |
| AC9 C-17 子图 | **MET** | r3 未改 X1 删除；测试通过 |
| AC10 统一 ProtectionPolicy | **MET** | r3 未改 policy；相关组通过 |
| AC11 Host 命令桥 | **MET（维持）** | preview minor 仍 11；Host registry/client 常量已是 11（`HostCommandRegistry.cs`、`CoreServiceClient.cs`），dispatcher 返回原始 `JsonElement`，新字段 additive 透传无需 apps 改动；r3 apps 零 diff；Host 侧 r1/r2 证据保持 |
| AC12 隔离与禁令 | **MET** | isolation 探针重放 `pass=true`、`drive_path_hits=[]`、`data_root_under_workspace_temp=true`、哨兵不变；无真实回收站 API |

> AC4/AC5 的 `<<PARTIAL...>>` 当前是流程状态；本 Review 的结论是 **AC4 可定稿 MET、AC5 需先闭合 P1-1/P2-1 的证据与分类**，而不是把 PARTIAL 永久保留。

## 4. Findings

| ID | 级别 | 位置 | 触发与影响 | 复现证据 | 建议/状态 |
|---|---|---|---|---|---|
| **P1-1** | **P1** | `doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md:62`（§5-1）；`doc/tasks/FEA-12-CORE.md:73,74,193`；`verification/FEA-12-CORE/core-py-implementation-record.md:67-68,202`；`doc/handoffs/FEA-12-CORE-core-py.md:79`；实际测试 `tests/core/test_core_delete_preview_commands.py:267-339` | 冻结载体要求 hidden region current 变化 → 旧 digest STALE 的判别回归；卡面/记录/Handoff 却把它列为已覆盖。现有 hidden 测试只断言 `currentRegionRevisionIds=["rr1"]` 与 representative=null，**不修改 current**；因此该精确反例没有 CI 回归保护，卡面证据不实。运行时行为经我探针确认正确 | `probe_hidden_current.py`（仓外）：hidden guard 下 representative=null，set=`["rr1"]`；插入 `rr2` 并更新 current 后 set=`["rr2"]`、digest 变化；旧 digest → `BOOK_DELETE_STALE_PREVIEW`、books=1；新 digest 删除成功。仓库 grep 无 hidden-current-change 用例 | **最小返修（测试/文档，不改生产代码）**：新增 `test_preview_hidden_region_current_change_is_stale`（复用现有 lineage/publication fixture）：首次预览后插入 `rr2` 并更新 hidden region `current_revision_id`；断言 set 变为 `["rr2"]`、representative 仍 null、digest 变化；旧 digest 单条删除 → STALE、books/文件不变；新 digest 删除成功。同步改卡/记录/Handoff，不再声称该判别已存在。状态 open |
| **P2-1** | **P2** | `doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md:38`；`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:819`；`src/bootstrap/core_service.py:2404-2416`（单条）、`:2518-2561`（批量）；`src/infrastructure/sqlite/library.py:1056-1057`；`core_service.py:1739,2362-2363,2484-2505` | manifest 行存在但 `targets_json` 为损坏 JSON 时，`get_cleanup_manifest_data` 返回 None → `_delete_target_state` 判为 `missing` → 单条 `BOOK_NOT_FOUND`、批量 `BOOK_DELETE_BATCH_PREFLIGHT_FAILED`（item BOOK_NOT_FOUND）；冻结映射表写明 manifest 缺失/损坏/篡改 → `BOOK_DELETE_STALE_PREVIEW`。影响客户端按 STALE 重新预览 vs NOT_FOUND 的分支；无数据破坏 | `probe_corrupt_manifest.py`（仓外）：损坏 JSON 后 single=`BOOK_NOT_FOUND`、batch preflight item=`BOOK_NOT_FOUND`；恢复 manifest 后 single retry 成功；零副作用 | **最小返修**：在 repository 层区分“行不存在”与“JSON 解析失败”（如返回 sentinel/抛 typed 异常），将损坏 manifest 映射为 `BOOK_DELETE_STALE_PREVIEW`（单条与批量 items 标注），并补 `test_retry_corrupt_manifest_is_stale_both_shapes`；保留“无 Book 行且无 manifest → BOOK_NOT_FOUND”既有语义。若 Lead 认为 BOOK_NOT_FOUND 才是预期，必须改冻结映射并走契约流程，不能在实现里静默偏离。状态 open |
| P3-1 | P3 | `verification/FEA-12-CORE/core-py-implementation-record.md:202,203,179,141,190`；`verification/FEA-12-CORE/logs/gates-core-py.log:114`；`doc/handoffs/FEA-12-CORE-core-py.md:27`；`src/application/library/service.py:286`；`src/bootstrap/core_service.py:1815` | 记录/证据精度：①`:202` 写 “preview minor 12”（实际 11）；②`:202/:203` 引用已改名测试 `test_delete_books_mixed_retry_batch_validates_live_per_book_digest`；③`:179` 写 manifest 在 `targets_json` 内新增 **`preview` 键**（实际是顶层 `batch_id/...` 键）；④`:141` 写 “集合级重拼接”（实际 retry 原样回传原集合 digest）；⑤日志写 “tests 3 文件”（实际 2：delete_commands、delete_preview_commands）；⑥Handoff 把未改动的 `tests/fea12/test_core_delete_protection.py` 列入 `41703da92`；⑦`service.py` docstring 写 “every lineage-visible region current”（实际全部 region）；⑧`core_service.py` docstring 写 arrays “in reading order”（实际字典序，仅 representative 用阅读序） | r3 commit numstat 与源码逐项对照 | 在同一最小 r4 内更正；不影响运行时 |
| P3-2 | P3 | `tests/core/test_core_delete_preview_commands.py:382-407` | “golden vector” 测试用 `canonical_inventory_payload` 重新计算期望值，是自指自洽；canonical 算法漂移会同时改变 actual/expected 而通过。真正的 golden 字面量只在仓外探针/证据 JSON 中被检查 | 阅读 `_expected_digest`；我的独立复算见 §5 | 可在测试中钉一个/两个 golden 字面量（如从证据 JSON 读取或硬编码 `sha256:bb0005fd…`），使 AC4 “golden 可复算” 进入 CI |
| P3-3 | P3 | `doc/tasks/FEA-12-CORE.md:234` vs `verification/FEA-12-CORE/logs/gates-core-py.log:9` | `EV-FEA12CORE-A-GATES` pin 为 `41703da92`，但最终 head `32ef1dc31` 又修改了该日志（补 r3 提交行），pin commit 的 blob 与 HEAD 不同；证据 pin 语义不清 | `git show 32ef1dc31` | 把 pin 改为 `32ef1dc31`，或注明“evidence commit + final append”；EV-A-HANDOFF pin `659c679be` 正确 |
| P3-4 | P3 | `doc/plan/FEA-CONTRACT-FROZEN-C04b.md:27,38` | 冻结记录仍写 r7 “确认中/⏳”，而 r7 报告已 APPROVE（`...unfreeze-final-review-r5\...-r7.md:6`）且 `fc9833479` 已重冻；r7 报告 N2 已知。pins 18/18 仍通过，不影响 C-04b/M2-C1 字节 | r7 报告 + 冻结记录 | Lead 在后续文档收口时更新条件 1 为 ✅；不属于 r3 代码 finding |
| P3-5 | P3 | `doc/STATUS.md:7,10`、`doc/REBASELINE_PLAN.md:17` | STATUS/Plan 仍写 CORE `changes_requested`，任务卡 frontmatter 为 `in_review`；`check.ps1` 不比较两者，故 PASS。closeout 时需统一 | 文本对照 | Lead 在 r3 Review 处置/closeout 时更新指针 |
| P3-6 | P3 | `tests/core/test_core_delete_commands.py:1663` | 测试名 `..._manifest_tamper_or_missing_is_stale` 与步骤 (5) 的 `BOOK_NOT_FOUND` 期望不一致（missing 归 NOT_FOUND，corrupt 才应 STALE）；名称会误导读者把 missing 当 STALE | 测试第 (5) 步 | 与 P2-1 一并改名/补 corrupt 断言 |

**P0：无。**

## 5. 独立复跑（全部只读；日志在仓外）

| 场景 | 命令 | EXIT | 结果 | 证据 |
|---|---|---|---|---|
| 相关组 | `C:/Python314/python.exe -m pytest tests/core tests/storage tests/maintenance tests/fea12 -q -p no:warnings --tb=no -p no:cacheprovider` | 0 | **1114 passed in 97.51s**（与卡面 1114 一致） | `G:\CODEX\New Manga.workspace\FEA-12\review-core-r3\pytest-related.log` |
| 全量 pytest | `C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no -p no:cacheprovider` | 0 | **3162 passed, 10 skipped in 273.90s**（与卡面一致；无新增 skip/失败） | `...\review-core-r3\pytest-full.log` |
| 定向删除/预览 | `pytest tests/core/test_core_delete_preview_commands.py tests/core/test_core_delete_commands.py -q -p no:cacheprovider` | 0 | **54 passed**（14 preview + 40 delete） | `...\review-core-r3\pytest-targeted.log` |
| 治理 check（TaskPath） | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-CORE.md` | 0 | **PASS (3 warnings)**（非终态 Task 计数、STATUS/PLAN 预算 80%） | `...\review-core-r3\check-task.log` |
| 治理 check（全量） | `pwsh -NoProfile -File tools/governance/check.ps1` | 0 | **PASS (3 warnings)** | `...\review-core-r3\check-full.log` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 0 | **PIN AUDIT: PASS (all 18)**；C04b `acc8f0e03d42` | `...\review-core-r3\verify_pins.log` |
| golden v2 独立复算 | 从证据 JSON 的 `canonical_payload` 以冻结规则重算；并重放探针到仓外输出 | 0 | 单书 `bb0005fd…`、集合 `c1029be8…`、book-empty `acf170f8…`、重排 `78d2f14c…` 全匹配；14 键与契约一致；两数组任一变化均改变 digest；`currentRevisionId` 不在 canonical | `...\review-core-r3\verify_golden.py`、`golden-recompute.log`、`golden-replay.json/.log` |
| isolation 重放 | 复制探针到仓外、只改输出路径 | 0 | `pass=true`、`drive_path_hits=[]`、`data_root_under_workspace_temp=true`、`sentinel_unchanged=true` | `...\review-core-r3\core_py_isolation_scan_replay.py`、`isolation-replay.json/.log` |
| .NET | 未重跑 | — | 引用 r1/r2 集成实跑 `1405 passed / 0 failed / 80 skipped`（我核对 `core-host-dotnet-full-1/2.log` 的“已通过”行求和 = 1405/0/80）；r3 对 `apps/**` 零 diff，且 preview minor 保持 11，故不重跑 | `verification/FEA-12-CORE/logs/core-host-dotnet-full-1.log`、`-2.log` |

补充探针（仓外）：

- **hidden current**：`probe_hidden_current.py` → representative=None，set=`["rr1"]`；改 current 后 set=`["rr2"]`、digest 变化；旧 digest STALE、books=1；新 digest 删除成功。
- **representative 不入 digest**：`probe_representative.py` → 可见/隐藏两种 guard 下 representative 从 `rr1` 变 `null`，集合不变，digest 相等。
- **corrupt manifest**：`probe_corrupt_manifest.py` → single `BOOK_NOT_FOUND`、batch preflight item `BOOK_NOT_FOUND`；零副作用；恢复后 retry 成功（P2-1 依据）。

## 6. 变异/反证

变异在仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-core-r3\mutant\` 的 `src+tests` 副本上进行（非仓库工作树）；先跑基线 6 条定向测试全部通过，再逐项注入：

| 变异 | 注入点 | 预期/实际失败 | 结论 |
|---|---|---|---|
| **M-A** 禁用 current 集合绑定 | `src/application/library/service.py` `canonical_inventory_payload`：用 `currentRevisionId` 代表值替换两个数组 | `test_preview_binds_non_first_region_current`、`test_preview_binds_artifact_current_set`、`test_preview_binds_region_current_add_and_remove` 全部失败（断言 digest 未变） | 3 条 current 绑定测试有判别力；也说明 hidden-only 回归若无专门用例不会被现有集合测试单独锁定 |
| **M-B** 恢复 retry 跳过集合级比较 | `src/bootstrap/core_service.py`：注释掉 `supplied_collection_digest != original_collection` 分支 | `test_delete_books_retry_collection_digest_is_always_validated`、`test_delete_books_batch_cleanup_pending_then_explicit_retry`、`test_delete_books_retry_manifest_tamper_or_missing_is_stale` 失败（FAKE/错误集合值被接受） | retry 集合校验测试有判别力 |
| **M-C** 关闭篡改重算 | `src/bootstrap/core_service.py`：注释掉两处 `canonical_payload_digest(inputs) != stored/expected_digest` | `test_delete_books_retry_manifest_tamper_or_missing_is_stale` 失败（篡改 inputs 被接受） | `inventory_inputs` 重算检测有判别力 |

以上变异日志：`mutant-A.log`、`mutant-B.log`、`mutant-C.log`（仓外）；仓库未被修改。

## 7. 范围 / 冻结 / 纪律核对

- **r3 路径**：`41703da92` 仅 `src/{application/library/service.py,bootstrap/core_service.py,infrastructure/sqlite/library.py}`、两个删除测试、`verification/FEA-12-CORE/**`；`659c679be` 仅 `doc/tasks/FEA-12-CORE.md`、`doc/handoffs/FEA-12-CORE-core-py.md`；`32ef1dc31` 仅卡一行 + gates log 一行。全部在 `allowed_paths` 内。
- **禁改路径**：r3 未含 `doc/plan/**`、`doc/contracts/**`、`doc/reviews/**`、STATUS/Plan/Ledger、`apps/**`；`git diff --name-only 5dfada827 32ef1dc31 -- apps` 为空。
- **冻结**：相对 `604a2d343`，`doc/plan/doc/contracts` 仅 UNFREEZE 的 C-04b、冻结记录、M2-C1 三文件变化，carrier 新增；其余 16 份 pinned 契约字节零 diff；`verify_pins.ps1` 18/18；C-04b/M2-C1 sha 实测匹配。
- **C-17/schema/migrator**：`src/infrastructure/sqlite/schema.py`、`migrator.py`、C-17 相关契约在 r3 区间零 diff；manifest 复用 `targets_json`，无 DDL。
- **依赖**：`pyproject.toml`/requirements 零 diff；无新依赖。
- **FEA-09**：r3 区间 `verification/FEA-09/**` 零 diff；未跑 .NET，故无需恢复。
- **未 push**：`git ls-remote origin refs/heads/main` = `b1c1f5a56840988e149c18375f6e414bf5c7fbda` ≠ `32ef1dc31`；本地 main 领先，未发现 push。
- **工作树**：审查结束 `git status --porcelain` 为空；仓外产物均在 `review-core-r3`。

## 8. 残余风险（不改变本次 decision，但应如实登记）

1. **artifact 成员谓词**：`list_book_artifact_current_pointers` 通过 page/chapter join 取本书 page 上的 artifact，而不是 `media_artifacts.book_id=本书`；这是 UNFREEZE 冻结记录 §4A residual ①，未在 r3 修；正常数据无影响，损坏行可能多绑定/少绑定。建议后续文档卡处理。
2. **代表值排序**：hidden/无可见 region 时 representative 取字典序最小 artifact current，而载体 A1 写“首个 artifact current”（阅读序）；仅展示、不参与 digest，属 residual ③。
3. **L-2**：lock/pin 的逐 region 分布仍以聚合计数表达，分布变化不进 digest；已登记，不阻断。
4. **manifest 篡改面**：r3 只对 inventory 字段（digest/inputs）做重算；`managed_targets`/`page_ids`/`preview_resource_ids` 仍是 manifest 原始数据，若本地 DB 被篡改可影响清理目标（`remove_managed` 的路径包含检查仍是一层防线）。属既有 manifest 信任模型，非 r3 新增。
5. **.NET 未重跑**：引用 1405/0/80 集成记录 + apps 零 diff；未验证真实 Windows 回收站（范围冻结，D 流程 NOT_RUN）。
6. **corrupt manifest 分类**（P2-1）与 **hidden 回归测试**（P1-1）是本次两个 blocking 项。
7. **UI unknown 字段 fail-closed**：FEA-12-UI 未实现（proposed），本卡 AC11 不含 UI；Host dispatcher 对 preview 结果做原始 `JsonElement` 透传，旧 Core 缺字段时 UI 侧必须 fail-closed 的规则留给 UI 卡。
8. **冻结记录 r7 文案**（P3-4）与 STATUS/Plan 指针（P3-5）属 Lead 文档收口。

## 9. done vs closed_with_limitations 意见

**建议现在不要 `done`，也不要 `closed_with_limitations`。**

- P1-1 是冻结载体 §5-1 的返回门禁；P2-1 是冻结错误分类表；两者都应在 r3 内以**最小 r4** 修复：
  1) 新增 hidden current change → STALE 的判别测试（无生产代码改动）；
  2) 区分 corrupt manifest 并映射 STALE（小改 repository/service），补 single/batch 测试；
  3) 更正 P3-1/P3-2/P3-3/P3-6 的卡/记录/Handoff/测试名/日志口径。
- 修复后建议对**新 head 做窄面复审**（可只审 P1/P2 关闭 + 上述测试 + 文档差异），再按 r3 结果更新 `delivery_head`/`integration_commit`/AC4/AC5 并 closeout。
- 若 Lead 选择 `closed_with_limitations`，需把未覆盖的 hidden 回归与 corrupt manifest 分类写成明确 residual 并说明为何允许偏离冻结映射；这会让 AC5 的“两级/失败分类”保持不完整。我不建议。

## 10. 自审声明

- 我未参与 FEA-12-CORE 的任何实现、返修、分片设计、r1/r2 复核或 UNFREEZE 提案/复核；本报告仅针对 `reviewed_head=32ef1dc31`。
- 审查期间只读仓库：未 commit、未 push、未 stash、未修改受跟踪文件；`git status` 最终为空。
- 全部复跑/探针/变异/报告写在仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-core-r3\`；变异在仓外 `src+tests` 副本进行。
- 未覆盖：真实 Windows 回收站/D 流程（范围外）、完整 .NET 重跑（apps 零 diff，引用集成记录）、FEA-12-UI（未实现）、全量源码逐行审计（聚焦 r3 diff 与调用链）。

## 11. 最终结论

**DECISION: changes_requested（P0=0 / P1=1 / P2=1 / P3=6）。** Codex OVERTURN 3a/4 的**运行时修复真实且可判别**：current 全量绑定、digest v2/golden、retry 保序 pending 子集/原集合 digest/mixed 拒绝/manifest 篡改检测均经独立复跑与变异反证成立，1114/3162/18/18/check PASS 与卡面一致；AC4 可恢复 MET，AC1–AC3/AC6–AC10/AC11/AC12 维持 MET。阻止 closeout 的是：①hidden current 变化缺冻结要求的仓库判别测试且卡面/记录不实声称已覆盖（P1-1）；②损坏 manifest 被分类为 `BOOK_NOT_FOUND` 而非冻结映射的 `BOOK_DELETE_STALE_PREVIEW`（P2-1）；另有 6 项 P3 文档/证据精度问题。按最小 r4（测试 + corrupt 映射 + 文档更正）修复后做窄面复审，AC5 即可恢复 MET 并进入 `done`；不建议以 `closed_with_limitations` 收口。
