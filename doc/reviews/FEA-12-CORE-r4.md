---
task_id: FEA-12-CORE
reviewer: dsh-fea12-core-r4 (fresh subagent)
reviewer_kind: subagent
review_session_id: 2395c6a5-ce18-458e-b36e-37026605c622
parent_agent_id: session-8db9dae5-49df-4d09-ac62-696f0805a95c
base_commit: 32ef1dc31
reviewed_head: 51e139eff
decision: approved
---

# Review r4：FEA-12-CORE（r3 changes_requested 最小返修窄面复审）

> 审查身份：独立上下文 fresh subagent，未参与 FEA-12-CORE 的实现、r1/r2/r3 返修、r3 Review 或 UNFREEZE 提案/复核。会话 `2395c6a5-ce18-458e-b36e-37026605c622`，父会话 `session-8db9dae5-49df-4d09-ac62-696f0805a95c`。
> 审查范围：`base_commit=32ef1dc31` → `reviewed_head=51e139eff`；重点为 r4 三个提交 `44718d3c9`（源码/测试/证据）、`a4c04d03c`（卡/Handoff）、`51e139eff`（head 定稿），以及它们相对 UNFREEZE `fc9833479` 的契约基线。`744daa51b` 是 r3 Review 落盘的 Lead 提交，不是 r4 实现提交，已单独区分。
> 审查方式：只读仓库；全部复跑、变异、探针和报告写在仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-core-r4\`；未 commit/push/stash，未改仓库受跟踪文件；审查结束 `git status --porcelain` 为空。

## 0. 结论摘要

**P0=0，P1=0，P2=0；P3-1 残留 2 处卡面措辞 + 若干 stale r3 标签（非阻断）。decision: approved。**

r3 的两个 blocking finding 已真实关闭，且不是测试空转：

- **P1-1（hidden region current 变化无仓库判别测试）**：新增 `test_preview_hidden_region_current_change_is_stale`。测试把 hidden region current 从 `rr1` 改为 `rr2`（代表值仍为 `null`），断言 `currentRegionRevisionIds` 变为 `["rr2"]`、digest 变化；旧 digest 单条确认返回 `BOOK_DELETE_STALE_PREVIEW`，全表快照与受管文件字节零变化，新 digest 删除成功。我做了“禁用 hidden 纳入绑定”的仓外变异，该测试精确失败（`[] != ['rr1']`）。
- **P2-1（corrupt manifest 错误分类）**：repository 新增 `get_cleanup_manifest_state`，区分 `missing` / `corrupt` / `ok`；单条 corrupt → `BOOK_DELETE_STALE_PREVIEW`，批量 corrupt → 顶层 STALE + `items` 标注，行缺失仍 `BOOK_NOT_FOUND`。新增 `test_retry_corrupt_manifest_is_stale_both_shapes`。我做了“corrupt 退回 missing”的仓外变异，该测试精确失败（`BOOK_NOT_FOUND != BOOK_DELETE_STALE_PREVIEW`）。

**独立复跑**：相关组 **1116 passed**、全量 **3164 passed / 10 skipped**、定向 **56 passed**、`check.ps1 -TaskPath`/全量 check **PASS (3 warnings)**、pins **18/18 PASS**；golden 证据向量独立重算 **0 mismatch**、isolation 探针重放 **pass=true**；apps 零 diff；未 push；工作树 clean。

**唯一未完全闭合的是 P3-1 文档精度**：`doc/tasks/FEA-12-CORE.md:133` 仍写 “preview wire minor 12”，`:141` 仍写 “集合级 digest 始终按请求顺序重拼接校验”；另有 record §4/§5、Handoff 标题/§4/§8、卡 §交付记录 的 stale “r3” 标签。它们不影响运行时、测试或 AC 判定，但应在 `done` closeout 前更正（最小返修点见 §8）。

**AC 建议**：**AC4 恢复 MET；AC5 恢复 MET**；AC1–AC3、AC6–AC10、AC11、AC12 维持 MET。若 Lead 采纳本 Review，可进入 done closeout：**AC4/AC5 恢复 MET、delivery_head=51e139eff**；closeout 时同步更新卡 frontmatter 的 `delivery_head`/`integration_commit`（当前仍是旧值 `3da210518`）与 STATUS/PLAN 指针。

## 1. 审查对象与独立性

- 开始时 `HEAD=51e139efff6a7610d27e7bb1289596a3f1eb623d`，与 `reviewed_head` 一致；`git status --porcelain` 为空。
- r3 head `32ef1dc31` 之后共有 4 个提交；其中 3 个是 r4 实现/交付提交，1 个是 r3 Review 落盘：
  - `744daa51b`（Lead）：`doc/reviews/FEA-12-CORE-r3.md`、冻结记录 r7 文案、STATUS/PLAN 对齐 `in_review`；**不是 r4 实现提交**，不计入 r4 allowed_paths 结论。
  - `44718d3c9`（r4 主提交）：源码 3 文件、测试 2 文件、`verification/FEA-12-CORE/**` 证据/日志；共 25 files。
  - `a4c04d03c`（r4 文档）：`doc/tasks/FEA-12-CORE.md`、`doc/handoffs/FEA-12-CORE-core-py.md`。
  - `51e139eff`（r4 head 定稿）：仅 `doc/tasks/FEA-12-CORE.md` 一行 Handoff 证据 pin。
- 契约基线：UNFREEZE `fc9833479`；实测 C-04b v1.1 sha256 `acc8f0e03d42fd574837cc556e9fa546ba355d7f45a5eefc7bd7b9fe8c16968f`、M2-C1 rev 2.14 sha256 `701093b5282228fdc791843146bf9459338e6ac1829ce3a801c72470fc938b7f`，与卡面/冻结记录一致；`verify_pins.ps1` 18/18 PASS。
- 只读手段：源码/测试/证据阅读；`pytest`（`-p no:cacheprovider`）；`check.ps1`；`verify_pins.ps1`；仓外 golden 独立重算；仓外 isolation 探针重放；仓外 `src+tests` 副本上的 2 项变异。未修改仓库、未 commit/push、未操作用户数据/真实回收站。

## 2. r3 findings 核销

| r3 ID | 级别 | 核销结论 | 独立依据 |
|---|---|---|---|
| **P1-1** hidden current 变化缺仓库判别测试、卡/记录不实 | **P1** | **已关闭** | `tests/core/test_core_delete_preview_commands.py::test_preview_hidden_region_current_change_is_stale` 真实存在；hidden `rr1→rr2`、代表值 null、旧 digest STALE、全表/文件零变化、新 digest 成功；变异 A 精确失败。卡 AC4/AC5、记录 §2.8/§8、Handoff §3 均如实引用新测试，不再称旧 visibility 测试覆盖该反例。 |
| **P2-1** corrupt `targets_json` 被分类为 `BOOK_NOT_FOUND` | **P2** | **已关闭** | `get_cleanup_manifest_state` 区分 `missing`/`corrupt`/`ok`；单条/批量 corrupt → 顶层 `BOOK_DELETE_STALE_PREVIEW`，items 标注，零副作用；行缺失仍 `BOOK_NOT_FOUND`。`test_retry_corrupt_manifest_is_stale_both_shapes` 覆盖单条/批量/恢复 payload 后重试；变异 B 精确失败。 |
| **P3-1** 文档精度（minor 12 / 旧测试名 / preview 键 / 重拼接 / tests 3 文件 / Handoff fea12 / docstring reading-order） | P3 | **部分关闭（非阻断残留）** | 旧测试名、preview 键、tests 文件数、Handoff `tests/fea12`、两个 docstring 已更正；但 `doc/tasks/FEA-12-CORE.md:133` 仍写 “preview wire minor 12”，`:141` 仍写“集合级 digest 始终按请求顺序重拼接校验”。详见 §8。 |
| **P3-2** golden 测试自指 | P3 | **已关闭** | `test_preview_digest_golden_vector_and_title_independence` 已钉死单书 `sha256:19b2ad3fede758694a31db631072954f38be46901c05f7d48991aa889aa05d72` 与集合 `sha256:1ecf951b0366c0580c5f03dc032285fa77eaa5bccaf14c6e775592312b5aeaf0`；canonical/字段漂移会直接失败。证据 JSON 的冻结向量 `bb0005fd…`/`c1029be8…` 未变，独立重算一致。 |
| **P3-3** EV-A-GATES pin 语义 | P3 | **已关闭** | 卡 `EV-FEA12CORE-A-GATES` pin 改为 `44718d3c9`，并注明 “evidence commit pin；最终 head 行只在后续 docs/head-pin 提交追加，不改证据字节”。实测 `gates-core-py.log` 在 `44718d3c9` 与 HEAD 的 blob 相同；`51e139eff` 只改卡一行，未再改证据。 |
| **P3-4** 冻结记录 r7 仍“确认中” | P3 | **已关闭（Lead 提交）** | `744daa51b` 已更新 `doc/plan/FEA-CONTRACT-FROZEN-C04b.md`：r7 窄面 APPROVE、条件 1 为 ✅；pins 18/18 保持。 |
| **P3-5** STATUS/PLAN 指针 | P3 | **closeout 待办** | 当前 STATUS/PLAN 仍写 “r3 changes_requested → r4 最小返修中”，是 r4 Review 前的真实状态；Lead 在 r4 处置/closeout 时更新。 |
| **P3-6** `tamper_or_missing` 测试名误导 | P3 | **已关闭** | 已更名 `test_delete_books_retry_manifest_tamper_is_stale_and_missing_is_book_not_found`；步骤 (5) 明确断言 missing → `BOOK_DELETE_BATCH_PREFLIGHT_FAILED` + item `BOOK_NOT_FOUND`。 |

**P0：无。**

## 3. P1/P2 逐项核验（不只看卡面）

### 3.1 P1-1：hidden region current 变化 → 旧 digest STALE

测试 `tests/core/test_core_delete_preview_commands.py:352`（文件当前行）：

1. `_seed_lineage_hidden_region` 构造 FK 完整的 v7 binding 链（`bind-old` superseded + `bind-new` 的 `changed` publication），使 `rr1` 被 lineage guard 判为不可见；首次预览断言 `currentRevisionId is None` 且 `currentRegionRevisionIds == ["rr1"]`。
2. 插入 `rr2`（同 `bind-old` lineage）并更新 `regions.current_revision_id = 'rr2'`；第二次预览断言代表值仍 `None`、`currentRegionRevisionIds == ["rr2"]`、`new_digest != old_digest`。
3. 用旧 digest 发起单条 `PermanentlyDeleteBook`（minor=10）：断言 `BOOK_DELETE_STALE_PREVIEW`；`_table_rows(core.conn)` 全表快照前后相等；受管文件字节前后相等；`books` 行仍为 1。
4. 用新 digest 再次确认：成功，`books` 行为 0，受管文件消失。

测试不是空转：若 hidden current 不进入绑定集合，第 1 步 `[] != ['rr1']` 失败；若 hidden current 变化不改变 digest，第 3 步旧 digest 会被接受或 `new_digest != old_digest` 失败；若旧 digest 确认有副作用，全表/文件断言失败。仓外变异 A 已确认第一点。

卡/记录/Handoff 引用核查：

- 卡 `AC4`/`AC5` 均明确写出 `test_preview_hidden_region_current_change_is_stale` 的判别内容（hidden current 变化 → 旧 digest STALE、全表/文件零副作用、新 digest 成功）。
- 记录 §2.8 判别测试段落包含 “隐藏 current 变化”，§8 第 3a 行明确列出新测试；Handoff §3 AC4 行与 `§1b` 明确写出新测试。未再出现“旧 `test_preview_current_revision_uses_lineage_visibility` 已覆盖 hidden current 变化”的不实表述；该旧测试现在只承担 “hidden current 进入绑定集、代表值为 null” 的断言。

**结论：P1-1 关闭。**

### 3.2 P2-1：corrupt manifest 分类

源码：

- `SqliteLibraryRepository.get_cleanup_manifest_state(book_id) -> (status, data)`：行不存在 → `("missing", None)`；`json.loads` 失败（`JSONDecodeError`/`TypeError`）→ `("corrupt", None)`；合法 dict/list → `("ok", data)`；其他 JSON 标量 → `("corrupt", None)`。`get_cleanup_manifest_data` 只在 `ok` 时返回 data，保持既有调用面的 None 语义。
- `CoreServiceServer._delete_target_state`：Book 行存在 → `book`；manifest `ok` → `retry`；`corrupt` → `corrupt`；否则 `missing`。
- 单条 `handle_permanently_delete_book`：`missing` → `BOOK_NOT_FOUND`；`corrupt` → `BOOK_DELETE_STALE_PREVIEW`（category conflict，零副作用），且发生在任何写/清理之前。
- 批量 `handle_permanently_delete_books`：先收集 states；`corrupt` 优先于 `missing`，返回 `_stale_preview_error(book_ids, corrupt)`，顶层 `BOOK_DELETE_STALE_PREVIEW`，items 仅 corrupt 项标 `BOOK_DELETE_STALE_PREVIEW`，其余 `None`；发生在 `_collect_delete_targets`/事务/清理之前。
- 行缺失语义保持：单条 `BOOK_NOT_FOUND`；批量 `BOOK_DELETE_BATCH_PREFLIGHT_FAILED` + item `BOOK_NOT_FOUND`（renamed test 步骤 5 断言）。

测试 `test_retry_corrupt_manifest_is_stale_both_shapes`：

- 先用拒绝 `cleanup_book_files` 的方式制造 `BOOK_DELETE_CLEANUP_PENDING`（Book 行已删、manifest 保留、受管文件保留）。
- 把 `targets_json` 改成 `'{corrupt-json'`；单条确认断言 `BOOK_DELETE_STALE_PREVIEW`/`conflict`、受管文件仍在、`get_cleanup_manifest_state == "corrupt"`。
- 批量确认断言顶层 STALE、items 精确为 `[{book_id: b1, status: not_started, error_code: BOOK_DELETE_STALE_PREVIEW}]`、manifest 行仍为 1、受管文件仍在。
- 恢复 `good_json` 后批量 retry 成功、文件删除。

**结论：P2-1 关闭。**

## 4. AC 判定建议

| AC | 建议 | 依据 |
|---|---|---|
| AC1 软删 | **MET（维持）** | r4 未改 A 流程；相关组/全量通过；既有 AC1 证据保持。 |
| AC2 恢复 | **MET（维持）** | r4 未改恢复流程；相关组/全量通过。 |
| AC3 回收站读取面 | **MET（维持）** | r4 未改投影；相关组/全量通过。 |
| **AC4 只读预览** | **可恢复 MET** | 两个 current 数组完整披露（hidden current 进入绑定集）；`currentRevisionId` 仅展示且移出 digest v2；hidden current 变化判别测试真实存在；golden 字面量钉死且证据向量独立重算一致；只读/无路径/无堆栈既有测试通过。 |
| **AC5 专门确认绑定** | **可恢复 MET** | 单条/批量形状分支、保序 pending 子集、原集合 digest 原样回传、mixed 拒绝、篡改检测、corrupt→STALE（单条/批量）、missing→NOT_FOUND 均有仓库测试；r4 新增 corrupt 判别测试并经变异反证；hidden current 变化也由 P1 测试覆盖。 |
| AC6 单事务/回滚 | **MET（维持）** | r4 未改事务路径；全量/相关组通过。 |
| AC7 保护披露/边界 | **MET（维持）** | r4 未改披露口径；相关组通过。 |
| AC8 共享引用/原文件 | **MET（维持）** | r4 未改 PD-08；isolation 重放通过。 |
| AC9 C-17 子图 | **MET（维持）** | r4 未改 X1 删除；相关组通过。 |
| AC10 统一 ProtectionPolicy | **MET（维持）** | r4 未改 policy；相关组通过。 |
| AC11 Host 命令桥 | **MET（维持）** | preview minor 保持 11；apps 零 diff；Host registry/client 既有常量与 r1/r2 证据保持。 |
| AC12 隔离与禁令 | **MET（维持）** | isolation 重放 `pass=true`、`drive_path_hits=[]`、`data_root_under_workspace_temp=true`、`sentinel_unchanged=true`、src 256 文件零 Windows 回收站 API。 |

> AC4/AC5 当前卡面仍是 `<<PARTIAL...>>` 流程状态；本 Review 的结论是 **可恢复 MET**，由 Lead 在 r4 处置/closeout 中定稿，而不是把 PARTIAL 永久保留。

## 5. 独立复跑

| 场景 | 命令 | EXIT | 结果 | 证据 |
|---|---|---|---|---|
| r4 新测试 | `pytest tests/core/test_core_delete_preview_commands.py::test_preview_hidden_region_current_change_is_stale tests/core/test_core_delete_commands.py::test_retry_corrupt_manifest_is_stale_both_shapes -q` | 0 | **2 passed** | 本次运行 |
| 相关组 | `C:/Python314/python.exe -m pytest tests/core tests/storage tests/maintenance tests/fea12 -q -p no:warnings --tb=no -p no:cacheprovider` | 0 | **1116 passed in 86.93s**（与卡面一致） | `...\review-core-r4\pytest-related.log` |
| 全量 pytest | `C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no -p no:cacheprovider` | 0 | **3164 passed, 10 skipped in 237.67s**（与卡面一致；无新增失败/skip） | `...\review-core-r4\pytest-full.log` |
| 定向删除/预览 | `pytest tests/core/test_core_delete_preview_commands.py tests/core/test_core_delete_commands.py -q -p no:cacheprovider` | 0 | **56 passed**（15 preview + 41 delete） | `...\review-core-r4\pytest-targeted.log` |
| 治理 check（TaskPath） | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-CORE.md` | 0 | **PASS (3 warnings)**（非终态 Task 计数、STATUS/PLAN 预算 80%，均既有全仓告警） | `...\review-core-r4\check-task.log` |
| 治理 check（全量） | `pwsh -NoProfile -File tools/governance/check.ps1` | 0 | **PASS (3 warnings)** | `...\review-core-r4\check-full.log` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 0 | **PIN AUDIT: PASS (all 18)**；C-04b `acc8f0e0…`、M2-C1 `701093b5…` | `...\review-core-r4\verify_pins.log` |
| golden 独立重算 | 从证据 JSON 的 `canonical_payload` 以冻结规则重算；集合按请求顺序拼接逐书 hex 重算 | 0 | 单书 `bb0005fd…`、集合 `c1029be8…` 均匹配；`all_match=true`、`recompute_failures=0` | `...\review-core-r4\replay_golden.py`、`golden-replay.log` |
| isolation 重放 | 复制探针到仓外、仅改 `REPO`/`EVIDENCE` 输出路径后运行 | 0 | `pass=true`、`drive_path_hits=[]`、`data_root_under_workspace_temp=true`、`sentinel_unchanged=true`、`static.pass=true`、src 256 文件 | `...\review-core-r4\isolation_replay.py`、`isolation-replay.log`、`isolation-replay.json` |
| .NET | 未重跑 | — | apps 零 diff；引用 r3 集成实跑 `1405 passed / 0 failed / 80 skipped` | `verification/FEA-12-CORE/logs/core-host-dotnet-full-1.log`、`-2.log` |

补充核对：

- `git diff --name-only 32ef1dc31..51e139eff -- apps/` 为空；`src/infrastructure/sqlite/schema.py`、`migrator.py`、`requirements*.txt` 零 diff。
- `git ls-remote origin refs/heads/main` = `b1c1f5a56840988e149c18375f6e414bf5c7fbda` ≠ `51e139eff`；未 push。
- `git status --porcelain` 为空；仓外产物均在 `review-core-r4`。
- 证据 pin blob 抽查：`core-py-implementation-record.md`/`gates-core-py.log`/`core-py-check.log`/golden JSON 在 `44718d3c9` 与 HEAD 相同；Handoff 在 `a4c04d03c` 与 HEAD 相同。

## 6. 变异 / 反证

变异在仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-core-r4\mutant\` 的 `src+tests` 副本上进行（非仓库工作树）；基线 2 条 r4 测试先全部通过，再逐项注入：

| 变异 | 注入点 | 实际失败 | 结论 |
|---|---|---|---|
| **M-A** 禁用 hidden region 纳入绑定 | 仓外副本 `src/bootstrap/core_service.py` `_finalize_delete_inventory`：对 `region_current_pointers` 增加 `lineage_guard.is_region_readable` 过滤 | `test_preview_hidden_region_current_change_is_stale` 在首次预览断言失败：`assert [] == ['rr1']`（`...\mutant-A-hidden.log`） | P1 测试对 “hidden current 必须进入绑定集” 有判别力；精确覆盖 Codex OVERTURN 3a 反例 |
| **M-B** corrupt 退回 missing | 仓外副本 `src/bootstrap/core_service.py` `_delete_target_state`：删除 `manifest_status == "corrupt"` 分支，统一返回 `missing` | `test_retry_corrupt_manifest_is_stale_both_shapes` 在单条断言失败：`'BOOK_NOT_FOUND' != 'BOOK_DELETE_STALE_PREVIEW'`（`...\mutant-B-corrupt.log`） | P2 测试对 corrupt 分类有判别力，不是重命名/自指断言 |

变异副本在实验后已恢复为仓库源码内容；仓库未被修改。日志：`mutant-baseline.log`、`mutant-A-hidden.log`、`mutant-B-corrupt.log`（均在仓外 `review-core-r4`）。

## 7. 范围 / 冻结 / 纪律核对

- **r4 路径**：`44718d3c9` 只含 `src/{application/library/service.py,bootstrap/core_service.py,infrastructure/sqlite/library.py}`、`tests/core/test_core_delete_commands.py`、`tests/core/test_core_delete_preview_commands.py`、`verification/FEA-12-CORE/**`；`a4c04d03c` 只含 `doc/tasks/FEA-12-CORE.md`、`doc/handoffs/FEA-12-CORE-core-py.md`；`51e139eff` 只含 `doc/tasks/FEA-12-CORE.md` 一行。全部在 CORE `allowed_paths` 内。
- **禁改路径**：r4 三提交未含 `doc/plan/**`、`doc/contracts/**`、`doc/reviews/**`、STATUS/PLAN/LEDGER、`apps/**`；`git diff --name-only 744daa51b..51e139eff -- apps/` 为空。注意 `git diff 32ef1dc31..51e139eff` 中出现的 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/plan/FEA-CONTRACT-FROZEN-C04b.md`、`doc/reviews/FEA-12-CORE-r3.md` 来自 Lead 的 `744daa51b`（r3 Review 落盘），不是 r4 实现者提交。
- **冻结**：C-04b v1.1 `acc8f0e0…`、M2-C1 rev 2.14 `701093b5…` 字节匹配；pins 18/18；UNFREEZE `fc9833479` 是 HEAD 祖先；`doc/plan`/`doc/contracts` 在 r4 三提交零 diff。
- **schema/依赖**：`schema.py`、`migrator.py`、requirements 零 diff；manifest 复用 `targets_json`，无 DDL。
- **FEA-09/FEA-11 写域**：r4 未改 `tests/fea12/**`、`verification/FEA-09/**`、FEA-11 文件；相关组/全量通过。
- **未 push**：远端 main 仍为 `b1c1f5a56840988e149c18375f6e414bf5c7fbda`。
- **工作树**：审查结束 `git status --porcelain` 为空；全部复跑/变异/报告在仓外 `review-core-r4`。

## 8. P3-1 残留与 closeout 最小返修点

**级别：P3（非阻断；不影响运行时/AC 判定），但当前卡面与冻结契约/记录存在事实冲突，建议在 done closeout 前更正。**

1. **`doc/tasks/FEA-12-CORE.md:133`**：仍写 “preview wire minor 12。”  
   **最小修改**：改为 “preview wire minor **11**（C-04b v1.1 不 bump）。”  
   依据：C-04b v1.1/M2-C1 rev 2.14、卡 `:197`、记录 `:55`、Handoff `:84` 均写 11；apps 零 diff。
2. **`doc/tasks/FEA-12-CORE.md:141`**：仍写 “集合级 digest **始终**按请求顺序重拼接校验（纯 pending 与混合均不跳过）”。  
   **最小修改**：改为 “live 首次按请求顺序重算集合级 digest；retry 时 `inventory_digest` **原样回传** manifest 的 `original_collection_digest`，逐书按 manifest 值校验；mixed live+retry 拒绝”。  
   依据：记录 §2.8 `:95`、Handoff §2 `:65`、实际 `core_service.py` retry 分支均为“原样回传”，不是按子集重拼接。
3. **stale “r3” 标签（P3 清理，可选但建议同批）**：
   - `verification/FEA-12-CORE/core-py-implementation-record.md:141` AC5 行仍写 “r3 修复后证据齐备（待 r3 Review/Lead 定稿）”，应改为 r4；
   - 同记录 `:150`/`:154` “r3 复跑” 含 r4 数字，改为 “r4 复跑”；
   - `doc/handoffs/FEA-12-CORE-core-py.md:3` “分片 A **r3**”、`:95` “门禁实跑（r3；…）”、`:143` “r3 复审就绪声明”、`:149` “r3 复审就绪” 应改为 r4 或明确为 r3 历史段；
   - `doc/tasks/FEA-12-CORE.md:110` “分片 A **r3** 实跑” 与紧随其后的 r4 数字不一致，建议改 “r4 实跑”。
4. **closeout 指针**：卡 frontmatter 仍是 `delivery_head: 3da210518`、`integration_commit: 3da210518`、`canonical_evidence_status: pending`、`resource_closeout_status: pending`；若批准，Lead 应更新为 `delivery_head: 51e139eff`（integration 按实际集成提交）、Evidence 状态与 STATUS/PLAN 指针。STATUS/PLAN 当前仍写 “r3 changes_requested → r4 最小返修中”，属于 closeout 待办，不是 r4 实现缺陷。

## 9. 残余风险（不改变 decision）

1. **.NET 未重跑**：apps 零 diff，preview minor 保持 11，引用 r3 集成记录 `1405/0/80`；本次未重新执行 .NET 全量。
2. **真实 Windows 回收站/D 流程**：范围冻结 NOT_RUN，零 OS API；AC12 只验证隔离与静态禁令。
3. **`preflight_permanent_delete` 的 manifest 读取**：该 repository 方法仍通过 `get_cleanup_manifest_data` 判断 “无 Book 行 + 无 manifest → NOT_FOUND”；单条/批量命令在调用它之前已用 `get_cleanup_manifest_state` 拦截 `corrupt`，因此当前命令面不会把 corrupt 误报为 NOT_FOUND。若未来新增绕过 `_delete_target_state` 的直接调用，需要同步改用 `get_cleanup_manifest_state`。本次不判 finding。
4. **P3-1 卡面残留**：见 §8；不影响代码、测试与 AC4/AC5，但应在 closeout 前修正，避免卡面与冻结契约/pins 记录冲突。
5. **UI unknown 字段 fail-closed**：FEA-12-UI 未实现；Host dispatcher 对 preview 结果原始 `JsonElement` 透传，旧 Core 缺字段时 UI 侧 fail-closed 规则留给 UI 卡。

## 10. 自审声明

- 我未参与 FEA-12-CORE 的任何实现、返修、r1/r2/r3 复核、分片设计或 UNFREEZE 提案/复核；本报告仅针对 `reviewed_head=51e139eff`。
- 审查期间只读仓库：未 commit、未 push、未 stash、未修改受跟踪文件；`git status` 最终为空。
- 全部复跑/变异/探针/报告写在仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-core-r4\`；变异在仓外 `src+tests` 副本进行。
- 未覆盖：真实 Windows 回收站/D 流程（范围外）、完整 .NET 重跑（apps 零 diff，引用集成记录）、FEA-12-UI（未实现）、全量源码逐行审计（聚焦 r4 diff 与调用链）。

## 11. 最终结论

**DECISION: approved（P0=0 / P1=0 / P2=0；P3-1 文档残留 2 处 + stale r3 标签，非阻断但 closeout 前应更正）。**

r3 的两个 blocking finding 已通过真实测试与变异反证关闭：hidden current 变化进入 CI 判别（P1-1），corrupt manifest 单条/批量均映射 `BOOK_DELETE_STALE_PREVIEW` 而行缺失仍 `BOOK_NOT_FOUND`（P2-1）。独立复跑 1116/3164/10/56、check PASS、pins 18/18、golden/isolation 均一致；apps 零 diff、未 push、工作树 clean。

**可进入 done closeout：AC4/AC5 恢复 MET、delivery_head=51e139eff。** Lead 在 closeout 时：①更正 §8 的两处卡面措辞（minor 11、retry 原样回传）及 stale r3 标签；②把卡 frontmatter 的 `delivery_head`/`integration_commit` 更新为实际集成 head；③同步 STATUS/PLAN 指针。

CORE-R4-REVIEW: APPROVE (P0/P1/P2=0; P3-1 residual: card:133 minor 12 + card:141 重拼接 + stale r3 labels; AC4/AC5 MET; delivery_head=51e139eff)
