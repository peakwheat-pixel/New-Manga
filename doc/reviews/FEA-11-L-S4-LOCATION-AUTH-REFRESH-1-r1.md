---
task: FEA-11-L-S4-LOCATION-AUTH-REFRESH-1
title: FEA-11-L-S4-LOCATION-AUTH-REFRESH-1 实现 Review r1（A：location auth 原地刷新；零契约）
reviewer: fresh subagent（独立上下文；未参与本卡实现、返修或 scope review；只读被审 head）
session: b2276971-3e32-4310-9650-741777ad8644
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立实现 Review（fresh context / read-only / 非作者 / 非实现或返修参与者）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 0ebb234bf
reviewed_head_note: 实现/测试事实取 `0ebb234bfd505ed72a351395b56c9a63303d5274`（实现 `6dd36aad7` + 测试 `0ebb234bf`）；证据事实取其后的文档/证据 head `4e8bda6e1`。评审期间共享 `main` 前进到 `9dc1cb0cd`（L-S1 closeout，docs-only），`src/**`/`tests/**`/`apps/**`/契约零 diff；本报告按 `0ebb234bf` 实现字节与 `4e8bda6e1` 证据字节判定。
verdict: approved
verdict_note: P0 = 0 / P1 = 0 / P2 = 0 / P3 = 7（全部非阻断；无功能性缺陷证据）。AC-LS4-1…8 均 MET，其中 AC-LS4-4 的 folder 子项、AC-LS4-3 的 D-2 路径口径带 P3 证据/口径附注。
---

# FEA-11-L-S4-LOCATION-AUTH-REFRESH-1：独立实现 Review r1

> **结论先行。**
>
> 1. **verdict：`approved`。P0 = 0 / P1 = 0 / P2 = 0 / P3 = 7（全部非阻断）。**
> 2. **单点实现成立**：全 `src/**` 只有 `SqliteLibraryRepository.refresh_source_location_auth`（`src/infrastructure/sqlite/library.py:2293-2339`）含原地 auth UPDATE；`src/application/sources/service.py` 的旧内联 UPDATE 已删除；`src/application/importing/referenced/runtime.py` 无 `UPDATE source_locations`。生产调用者为页单元（`library.py:2655`）、D-2 独立写单元（`library.py:2353`）与 apply 面（`service.py:516`）三处；`source_sync.py` 未改、无第二份 SQL。恢复第二份内联 SQL 的破坏点 B4 实测 RED（`sql_sites` 2）。
> 3. **语义成立**：apply 与 import 两条写路径在「live grant + 同 `(content_digest, volume_serial, file_id)` + current 行」时刷新 `registry_id/authorization_generation/last_verified_at`；不新增 location 行、不改 `source_id`/身份键/`observed_at`/`is_current`/binding；同 registry 代次不倒退、跨 registry 允许 1、同值幂等、审计时间非空 ISO；刷新在调用方事务内（页单元 / `BEGIN IMMEDIATE`），D-2 skip 路径为显式登记的单行独立写单元。
> 4. **负例成立**：撤销 grant 后 apply 路径 typed 失败、skip 路径零写；identity 不符（错 digest/volume/file、同 digest 拷贝）零写；scan 零写。**不**自动放行、**不**自动重新授权。folder 身份键（L-S4-2）仍未修，只保证刷新复用写入时同一算法；folder 错键的显式负例未见专门用例（P3，非功能缺陷）。
> 5. **独立实跑成立**：定向 **26 passed**、全量 **3317 passed / 10 skipped**、`verify_pins` **18/18**、`check.ps1`（默认 + `-TaskPath`）**PASS(3 warnings)×2**、API inventory **EXIT=0**、scope 自有链 **changed=21 / 7 代码测试，全 ALLOWED，zero-drift 空，`PROTOCOL_MINOR=3`**；破坏性复跑 **7/7 RED_AS_EXPECTED + 7/7 字节级恢复（sha256 MATCH）+ 恢复后复绿 + 三文件 `git status` CLEAN**。证据树 11 个文件与交付 7 个文件的 sha256 均与 `RESOURCE-MANIFEST.json` 一致。
> 6. **不夸大**：本卡只兑现「重授权/重新注册时原地刷新事实」，**不**表示「只读切片已可恢复」或零交互自愈；L-S4-1（缺触发器，零交互恢复需 C-16 v1.5 另卡）与 L-S4-2（folder 身份键）原文保留；撤销后不自动放行。D-2 使整源 skip 在 live grant + 同 identity 时写一次单行条件刷新，已显式登记。
> 7. **P3 均非阻断**：主要是 D-2 路径口径需 Lead 确认（`import_as_new` 零页 outcome 也被刷新）、folder 负例缺专门用例、撤销 apply 用例未断言 operation 行、import 复用用例只数 current 行、「Never raises」docstring 与 DB 异常语义不符、证据清单/scope 日志的簿记口径、以及全量 .NET 不在本卡隔离 head 上跑。逐条见 §8。

---

## 0. 审查基线、环境与并发披露

| 项 | 值 | 来源 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 实测 |
| 被审实现 head | **`0ebb234bfd505ed72a351395b56c9a63303d5274`**（`0ebb234bf`） | 任务书 + `git cat-file` |
| 实现提交 / 测试提交 | `6dd36aad7` / `0ebb234bf` | `git log` |
| 证据 head | **`4e8bda6e1`**（最终治理 gate re-run；docs/evidence-only） | `git show --stat` |
| 评审开始时 HEAD | `4e8bda6e1` | 实测 |
| 评审结束时 HEAD | `9dc1cb0cd`（L-S1 closeout，docs-only） | 实测 |
| 工作树 | 评审开始时仅 `?? doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-r1.md`；评审期间该文件被并发会话提交，另有 **`M doc/handoffs/DSH-PROGRESS-2026-11-07.md`**（非本 Review 产物）。**本 Review 未改这些字节。** | `git status --porcelain=v1` |
| 实现/测试字节 | 工作树 7 个交付文件的 sha256 与 `0ebb234bf` / `RESOURCE-MANIFEST.json` 逐字节一致；`git diff 0ebb234bf -- src tests` 为空 | `Get-FileHash`、`git diff` |
| `4e8bda6e1..9dc1cb0cd` | 只有 L-S1 文档/证据提交；`src/**`、`tests/**`、`apps/**`、`doc/plan/**`、`doc/contracts/**` 零 diff | `git diff --name-status` |
| Python / pytest | CPython 3.14.6 / pytest 9.1.1 | 实测 |
| 任务允许写入 | 仅本报告 | 任务书硬约束 |
| 未跑项 | 全量 `dotnet test`（本 Review 未重跑；核验 Lead 证据日志）；真实 IPC 注入（本卡 Host 零改动，未要求） | 见 §5 |

**并发披露（必须）**：本卡与 L-S1 共用 `main` 工作树。评审期间另一会话把 L-S1 review 入库并提交 `9dc1cb0cd`，同时修改 `doc/handoffs/DSH-PROGRESS-2026-11-07.md`（本报告落盘时仍为 `M`）。上述 `M`/提交**不是本 Review 产物**；本 Review 在仓库内唯一新增字节是本报告文件。`9dc1cb0cd` 不含 `src/**`/`tests/**`/`apps/**` 变化，故对本卡判定无影响；但严格意义上「在 `4e8bda6e1` 上重跑门禁」应改述为「在 `4e8bda6e1` 的实现/测试字节 + 当前 docs head 上重跑」。见 §5.6。

---

## 1. A：单点实现（AC-LS4-1）— PASS

### 1.1 生产代码唯一 SQL

`git grep -n "UPDATE source_locations SET registry_id" 0ebb234bf -- src`：

| 命中 | 说明 |
|---|---|
| `src/infrastructure/sqlite/library.py:2325` | `refresh_source_location_auth` 的 UPDATE 首行；唯一原地刷新实现 |
| `service.py` / `runtime.py` | **0 命中**；旧 `service.py:504-515` 内联 UPDATE 已删除 |

`src/**` 中另有两条 `UPDATE source_locations`，但都只写 `is_current`，不是 auth 原地刷新：
- `library.py:2358` `supersede_source_location`（`SET is_current = 0`）；
- `service.py:742` `_ensure_target_version` 的 supersede 路径（`SET is_current = 0`）。

**结论**：生产实现单点成立。`commit_source_location_auth_refresh`（`library.py:2341-2353`）只是薄包装，内部调用唯一实现，不含第二份 SQL；`source_sync.py` 未改（`git diff 6dd36aad7^..0ebb234bf -- src/infrastructure/sqlite/source_sync.py` 为空），也无 refresh 方法。

### 1.2 调用点（≥3）与判别

| 调用点 | 位置 | 作用 |
|---|---|---|
| 页单元刷新 | `library.py:2655`（`commit_referenced_page_unit` 内，`with self._conn` 事务） | import 复用路径第一页单元内刷新 |
| D-2 独立写单元 | `library.py:2353`（`commit_source_location_auth_refresh` 的 `with self._conn`） | skip / 零页路径的单行条件刷新 |
| apply 面 | `service.py:516`（`_execute_decisions`，`BEGIN IMMEDIATE` 内） | relink / 同 identity resync / repoint |
| import 侧构造 | `runtime.py:466-468`, `:640-659`, `:661-699` | 计算 payload 并调用上述入口 |

`tests/fea11/test_source_relink.py::test_refresh_source_location_auth_is_the_single_implementation`（`:270-303`）实测全 `src/**` `sql_sites == 1`、生产调用点 `>=3`、`service.py`/`runtime.py` 无残留 UPDATE。**独立破坏 B4**（恢复第二份内联 SQL）→ 该用例 RED，输出 `['src/application/sources/service.py:520', 'src/infrastructure/sqlite/library.py:2325']`、`assert 2 == 1`；恢复后绿。

### 1.3 全仓口径说明（P3，非违规）

仓库内还有 **Host 测试夹具**以 Python 字符串直接执行 `UPDATE source_locations SET registry_id`：
- `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11ScanIpcTests.cs:300`、`:768`；
- `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs:1088`。

这些是 fixture-only 的测试对齐 SQL（注释明确「Aligns the isolated fixture」），不是生产实现，也不在 `src/**`。因此：
- **「生产唯一实现」成立**；
- 若把 AC-LS4-1 的「全仓」按字面读成「所有 tracked 文件」，则**不成立**（Host 测试字符串也算 SQL 文本）。卡/EV/Handoff 的措辞是「全 `src/**` 唯一」，与实测一致，无需改实现；建议 closeout 保持「生产 `src/**`」限定，避免被误读为全仓。

---

## 2. B：语义正确（C-15 既有条款）— PASS

### 2.1 契约依据

- `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:204`：重授权/重新注册**原地更新** `registry_id/authorization_generation/last_verified_at`，不新建重复 location；移动/改名产生新物理身份时先 `is_current=0` 再插入新行；跨 Registry 命中同一物理身份同样复用并原地更新。
- 同文件 `:233`（源复用规则 v3）：按 `(content_digest, volume_serial, file_id)` 查 location；命中复用 source/version/entries 并原地更新三列；旧 binding 的 `authorization_generation` 允许 ≤ 当前 Host generation。
- `doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:169`、`:186`：不能自动恢复撤销的授权、不能自动重新授权；`:228`：只读枚举零 DB 写。

本卡是 **conformance**（兑现既有条款），不改契约字节；`verify_pins` 18/18 与 scope 的 `doc/plan/**` 零 diff 共同证明。

### 2.2 刷新 SQL 语义（`library.py:2324-2339`）

```sql
UPDATE source_locations SET registry_id = ?, authorization_generation = ?,
       last_verified_at = ?
 WHERE source_id = ? AND content_digest = ? AND volume_serial = ?
   AND file_id = ? AND is_current = 1
   AND (registry_id <> ? OR authorization_generation <= ?)
   AND (registry_id <> ? OR authorization_generation <> ? OR last_verified_at IS NOT ?)
```

| 不变量 | 实现/实测 |
|---|---|
| 同 identity 才写 | `source_id + content_digest + volume_serial + file_id` 四键 + `is_current=1`；错 digest/volume/file 均 0 行（`test_refresh_source_location_auth_fail_closed_guards`） |
| 不新增 location 行 | 只 UPDATE；无 INSERT；页单元 reuse 走 `insert_source=False`，apply 同 identity 不 supersede；测试行数 1 |
| 不改 `source_id`/身份键/`observed_at`/`is_current`/`size_bytes` | SET 只列三列；测试逐列断言；SQL 无其他 SET |
| 不改 binding | 无 `page_bindings` 写入；relink 测试断言 binding 行逐列不变；import 第二 project 生成新 binding，旧 binding 不动 |
| generation 单调 | 同 registry 只允许 `new >= current`（`authorization_generation <= ?`）；同 registry 15→14 实测 0；跨 registry 允许 1（新注册） |
| 幂等 | 同三值（含同一 `last_verified_at`）第二次 UPDATE 被 `last_verified_at IS NOT ?` 守卫挡为 0；`rowcount == 0` 且快照不变 |
| 审计 | `last_verified_at` 由调用方传入，非空、ISO 可解析（`+00:00` 或 `Z`）；不写日志/路径/secret |
| 事务中立 | 方法自身**不** `with self._conn`、不 commit/rollback；页单元在调用方事务内，apply 在 `BEGIN IMMEDIATE` 内 |
| 越权改 binding | 否；旧 binding `authorization_generation` 保持 1，不抬到新代次（relink 跨 registry / 同 registry 1→2 两例） |

### 2.3 两条写路径的接线

**apply（`service.py:497-516`）**：
- `_location_auth_refresh`（`:938-986`）只在 `grant is not None`、`target["status"]=="ok"`、`target digest == location digest`、`grant facts volume/file == location 行` 时返回 payload；
- payload 取 **current location 行自身**的身份键（不重新推导），避免 folder 身份键二次算法（L-S4-2 保持 out）；
- 在 `_ensure_target_version` 可能 supersede 之前取 payload；changed container/copy 因 digest/identity 不符返回 `None`，保留既有 supersede+insert；
- 刷新在 `BEGIN IMMEDIATE` 内、`_verify_live_authorization` 两次复核之间；失败整个 apply 回滚；
- 覆盖 relink（同 container、跨/同 registry）与同 identity resync/repoint；relink 既有 5 例全绿。

**import（`runtime.py:398-415`, `:462-468`, `:571`, `:602-613`）**：
- 复用路径（`existing_source_id is not None`）的 payload 使用 `scanned.container_digest` + `_volume_serial/_file_id(resolved)`，即**首次写入的同一算法/同一来源**；
- 第一页页单元（`first_page`）携带 `auth_refresh`，与 page/binding 同事务；失败页面单元回滚刷新；
- 整源 skip：在 `progress.outcome="skipped"` 前调用 `_refresh_skipped_source_auth`（一次性条件写）；
- 全页已引用的零页 outcome（`import_as_new`）：循环后 `committed_pages == 0 and outcome == "skipped"` 时同样调用一次；
- 无页单元时 `commit_source_location_auth_refresh` 用独立单行写单元（显式行为变化，见 P3-01/05）。

### 2.4 审计/时间格式

- import：`_utc_now()` → `datetime.now(timezone.utc).isoformat(timespec="milliseconds")`（`+00:00`）；
- apply：`now_millis()` → `Z` 后缀；
- 两格式均被测试 `datetime.fromisoformat` 解析；`last_verified_at` 非空。格式不统一是 P3 簿记项，不影响审计可读性。

---

## 3. C：负例 / fail-closed（AC-LS4-4）— PASS（核心），folder 子项 P3

### 3.1 撤销后不刷新、不自动放行

| 场景 | 实测 |
|---|---|
| apply：plan 确认后、apply 前撤销 grant | `test_revoked_grant_never_refreshes_and_never_publishes`：typed `SOURCE_GRANT_REVOKED`/`SOURCE_ACCESS_DENIED`；location/binding 逐字节不变；location 行数 1；**不产生自动授权** |
| import skip：plan 后、start 前撤销 | `test_revoked_grant_never_refreshes_on_a_skip_path`：receipt 仍 `completed` / `skipped`；location 行 `tuple()` 全等；registry 仍 `reg-1`、`last_verified_at` 仍 `NULL` |
| import 页单元路径撤销 | 代码在 `runtime.py:420-425` 先 `_access.resolve`，失败即 failed typed，未进入页单元；无刷新。该路径未单独设撤销用例（见 P3-03 的相邻口径） |
| 扫描 | scan/枚举只读；Core 测试 14 表快照不变 |

**结论**：撤销语义不变；刷新不是授权决定，不能凭旧 registry/generation 自动放行。

### 3.2 identity 不符 / 无 live grant → 零写

| 场景 | 实测 |
|---|---|
| 错 digest / 错 volume / 错 file（直接调用唯一实现） | `test_refresh_source_location_auth_fail_closed_guards`：三次均 `rowcount 0`；控制组同 identity 为 1；快照不变 |
| 同 digest 拷贝（新物理文件，apply repoint） | `test_identical_copy_never_refreshes_the_recorded_location`：location 行 `tuple()` 全等、registry 仍 `reg-1`、lvt 仍 `NULL`、行数 1 |
| 无 live grant / revoked | 见 3.1；`SourceReadGrantRegistry.resolve` typed 失败 |
| identity 与 current 行不符 | SQL 四键 + `is_current=1` 返回 0；不静默改行 |

### 3.3 D-2 整源 skip 的范围

调用条件（`runtime.py:398-415`）：`source.status=="ok"`、`already_referenced`、`will_import==0`、`duplicate_policy=="skip"`；`_refresh_skipped_source_auth` 内再 `resolve` live grant，按 plan digest + live volume/file 找 source，SQL 再校验 identity/current/generation。撤销/非 live grant → 0；无页/version/entry/binding 写。测试 `test_whole_source_skip_refreshes_location_auth_once` 断言 `imported_pages=0/skipped_sources=1`、页/版本/位置计数不变；`test_all_pages_already_referenced_import_as_new_still_refreshes` 覆盖 `import_as_new` 零页 outcome。

**保留点**：
- **folder 错键 → 0 行** 的专门用例不存在。现有 `test_refresh_source_location_auth_fail_closed_guards` 用错 digest/volume/file 覆盖了**通用 identity 守卫**，但没有 folder grant / 首成员 facts 与 location 行不一致的路径；Handoff/EV 的「已有测试」「测试覆盖」措辞过强。行为本身仍由同一 SQL 守卫覆盖，未发现功能缺陷（P3-02）。
- 撤销 apply 用例未断言 `source_operations` 无行；EV 写「无 operation 行」超出该用例实际断言（事务回滚保证，但证据未落）（P3-03）。

---

## 4. D：独立实跑与破坏性复跑

### 4.1 定向 / 全量 / 门禁

| 命令 | 实测 | 与证据对比 |
|---|---|---|
| `pytest tests/core/test_core_scan_target_commands.py tests/fea11/test_source_relink.py tests/fea09/test_import_source.py tests/fea09/test_source_sync_operations.py -q` | **26 passed**（首跑 4.56 s；破坏后复跑 1.23 s），EXIT 0 | 证据 `logs/feature.log` 26 passed / 1.22 s；数字一致 |
| `pytest tests -q` | **3317 passed, 10 skipped, 11 warnings in 261.60 s**，EXIT 0 | 证据 `logs/full-pytest.log` 3317/10 / 245.79 s；数字一致，时长差异为环境负载 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**，EXIT 0 | 一致 |
| `pwsh -NoProfile -File tools/governance/check.ps1`（默认） | **PASS (3 warnings)**，EXIT 0 | 一致；当前非终态 9（L-S1 closeout 后），交付时为 10 |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md` | **PASS (3 warnings)**，EXIT 0 | 一致 |
| `python tools/generate_api_inventory.py --check` | **OK: rendered counts match FEA-C07 doc**，EXIT 0（IHostController 54 / IRunController 6 / IReaderProgressSink 1，合计 61） | 一致 |
| 全量 `dotnet test NewManga.sln -c Release` | **本 Review 未重跑**；核验 `logs/full-dotnet.log`：8 个程序集逐 assembly 汇总 **1570 passed / 0 failed / 92 skipped**，`repo_head=89757f193` | 与 Handoff/EV 数字一致；见 §5.5 的归因 |

**跑后状态**：全量 pytest 未改 `verification/FEA-09/logs/wire-redacted.ndjson`（sha256 `548de629…` 前后一致）；定向/全量后 `git status` 除并发 `M doc/handoffs/DSH-PROGRESS-2026-11-07.md` 外无变化。`FEA-09` 无需恢复。

### 4.2 破坏性复跑（7/7，独立）

- 先对 `src/application/sources/service.py`、`src/application/importing/referenced/runtime.py`、`src/infrastructure/sqlite/library.py` 做**字节备份 + sha256**；
- 复用证据工具 `verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/tools/discrimination.py` 的 `BREAKS` 定义（仅 import，不执行其 `main`，**未写 evidence log**）；
- 逐点替换、跑目标用例、要求 RED，随后按原字节恢复、sha256 复核、再跑目标用例要求绿；最后 `git status` 检查三个文件。

| Case | 破坏点 | 目标用例 | break exit | 恢复 sha256 | 恢复后 |
|---|---|---|---|---|---|
| B1 | apply 面刷新调用禁用 | `tests/fea09/test_source_sync_operations.py::test_resync_same_identity_refreshes_the_location_auth` | 1（`reg-2` 期望 vs `reg-1`） | MATCH | 1 passed |
| B2 | import 页单元不携带刷新 | `tests/fea09/test_import_source.py::test_reimport_into_another_project_refreshes_location_auth_in_place` | 1（`reg-2` vs `reg-1`） | MATCH | 1 passed |
| B3 | 整源 skip D-2 刷新删除 | `tests/fea09/test_import_source.py::test_whole_source_skip_refreshes_location_auth_once` | 1（`reg-2` vs `reg-1`） | MATCH | 1 passed |
| B4 | 恢复第二份内联 SQL | `tests/fea11/test_source_relink.py::test_refresh_source_location_auth_is_the_single_implementation` | 1（`sql_sites` 2） | MATCH | 1 passed |
| B5 | 同 registry 单调守卫移除 | `tests/fea11/test_source_relink.py::test_refresh_source_location_auth_fail_closed_guards` | 1（gen 14 返回 1） | MATCH | 1 passed |
| B6 | identity 三键守卫移除 | 同上 | 1（错 volume 99 返回 1） | MATCH | 1 passed |
| B7 | `is_current` 守卫移除 | 同上 | 1（旧行 `loc-old` 返回 1） | MATCH | 1 passed |

**结果**：`result=PASS breaks=7`，`restored_tree_git_status=CLEAN`；三文件最终 sha256 分别为 `6579f3a5…`（service）、`cf956252…`（runtime）、`9c3714be…`（library），与 `0ebb234bf`/Manifest 一致。全量证据 `logs/discrimination.log` 的 7/7 记录与本轮独立复跑一致；该日志未包含每例恢复后绿输出，但驱动逻辑在恢复后必跑绿，且状态 `RED_AS_EXPECTED` 只在绿时产生，故可信。

---

## 5. E：证据、判别性、scope 与数字一致性

### 5.1 证据树逐文件 sha256（11/11 与 Manifest 一致）

```text
0f4b55dd0fac464f617be575c6eec8a5d6fc97144388dd852c97bf89ee1133a7  changed-files.txt
db12eb842509e8178e1682871f052325f65b2cd0f662bfaf2b433dcac738591b  EV.md
f624c0021cd2a1c05920f043be5c4962c338b5322b50f83e821360a93e0315c1  scope-validation.log
f287dbe155d7da13074b1e185c36a24202719df01147cb72a841811032ac424b  logs/discrimination.log
274e3b8bc5ebcbab242e4f60d50ab33932d05b8b917da9a5e4680dcd68b203b3  logs/feature.log
cdfba8d5daa7adca1e992702462d30bf56fdbb4a921f69b0e52ccef0c4710be2  logs/full-dotnet.log
ebeedde979dd85375229db622cb95fc602b171a884757d381634327db897380b  logs/full-pytest.log
5ba7b13c4ed78ec4f9807fb53cc8f620c66806c64134d9c57215e1688a698553  logs/gates.log
adaf714d23c336aff8b617b2d60b3af2db78fcd8af3e784ddcb7e43d0cefca52  tools/discrimination.py
20a107801e094826773a848629aa18c00d855e7a6114f12a04c3d971f534297d  tools/gen_manifest.py
f5448d87ab1b840fe553183ccacabb94f86ef5bc4b1737a81c2e885ef041f8b5  tools/scope_validation.py
```

7 个交付文件（`runtime.py`、`service.py`、`library.py`、4 个测试文件）的 sha256 与 Manifest `changed_files` 逐项一致：`cf956252…`、`6579f3a5…`、`9c3714be…`、`4cc66d23…`、`5222fa98…`、`f6a4ed0b…`、`de5c9add…`。`RESOURCE-MANIFEST.json` 本身按设计不自列。

### 5.2 scope（本卡自有 commit 链）

本卡自有链：`6dd36aad7`（实现）、`0ebb234bf`（测试）、`9ef295b74`、`8050a62ae`、`54ed1b5f5`、`3f37b74ee`、`4e8bda6e1`（文档/证据）。

| 指标 | 实测 |
|---|---|
| 唯一 changed 文件 | **21** |
| 其中代码/测试 | **7**（3 src + 4 tests） |
| `out_of_scope` | **[]** |
| 冻结面（`apps/**`、`doc/plan/**`、`doc/contracts/**`、schema/migrator/依赖/STATUS/PLAN/LEDGER） | **无命中** |
| `PROTOCOL_MINOR` | **3** |
| 卡 `status` | **仍 `ready`**（未改） |
| 结论 | **PASS** |

`INTERLEAVED` 的 `1ac8cc0b7`/`b56c5a0e6`/`89757f193` 是 L-S1 字节，不在本卡自有链；本卡未把它们计入 scope。`4e8bda6e1..9dc1cb0cd` 的 L-S1 closeout 也不影响本卡 chain。

### 5.3 Handoff / 日志数字

| 项 | Handoff/卡/EV | 实测/日志 | 一致 |
|---|---|---|---|
| 定向 | 26 passed / 1.22 s | 26 passed（本 Review） | 是 |
| 全量 pytest | 3317 / 10 / 245.79 s | 3317 / 10 / 261.60 s | 是（时长差异） |
| 全量 .NET | 1570 / 0 / 92 | 日志逐 assembly 汇总 1570/0/92 | 是 |
| pins | 18/18 | 18/18 | 是 |
| check | PASS(3w)×2 | PASS(3w)×2 | 是 |
| API | EXIT=0 | EXIT=0，counts 61 | 是 |
| scope | changed=21（7 代码测试） | 21 / 7，全 allowed | 是 |
| 判别性 | 7/7 RED + 7/7 restore | 本 Review 7/7 独立复跑 | 是 |

### 5.4 `logs/discrimination.log` 可信性

- 驱动 `tools/discrimination.py` 逐点备份原字节、替换、跑目标、`finally` 恢复、sha256 比较、再跑绿、最后检查三文件 `git status`；日志的 `restore_sha256=MATCH` 与 `status=RED_AS_EXPECTED` 与驱动逻辑一致。
- 本 Review 独立复跑 7/7，全部 RED、恢复 MATCH、绿、三文件 CLEAN；说明该日志不是「只写测试无判别力」的自证。
- 日志未逐例打印恢复后绿的输出，也没有每例原始 sha256 值；这是 **P3 证据完备性**（不影响结论，驱动逻辑与独立复跑已补足）。

### 5.5 全量 .NET 的归因（P3-07）

`logs/full-dotnet.log` 的 `repo_head=89757f193`，是 L-S1 的 docs-only 提交（`0ebb234bf..89757f193 -- apps/` 实测为空；本卡自有提交不触 `apps/**`）。8 个程序集汇总 1570/0/92；基线 1562/0/91。**+8 passed / +1 skipped 来自并发 L-S1 已提交的 Host 测试（`b56c5a0e6`），不归属本卡**。需要精确表述的是：`89757` 的 `apps/**` 字节等于 `0ebb234bf`，而 `0ebb234bf` 本身已包含 L-S1 祖先（`b56c5a0e6`）的 Host 测试；因此这不是「仅含 L-S4 改动的隔离树」，而是「交付树（含并发 L-S1 Host 测试）」。本 Review 未重跑 .NET（Host 零 diff；任务只要求 Python/门禁独立实跑），因此不宣称「独立 .NET 通过」，只确认日志数字、程序集汇总和归因自洽。

### 5.6 并发/时间线（环境披露，不单列 P3）

- 评审开始 HEAD `4e8bda6e1`，结束 `9dc1cb0cd`；期间 L-S1 closeout 提交了 5 个文档/证据文件，未触 `src/**`/`tests/**`/`apps/**`/契约。
- `doc/handoffs/DSH-PROGRESS-2026-11-07.md` 在本 Review 期间被另一会话修改；本 Review 未读入其内容作为结论依据，也未改它。
- 本 Review 的 pytest/check/pins/API 在**当前 worktree** 上跑；7 个交付文件与 `0ebb234bf` 逐字节一致（sha256/`git diff`），故等价于在交付实现/测试字节上跑。
- 全量 pytest 的 `3317` 与证据日志一致；证据日志跑在 `0ebb234bf`（Handoff 声明），本 Review 无法从日志时间戳独立证明当时的 repo_head，但因当前字节与 `0ebb234bf` 相同，结论不变。这是 **P3 证据口径**，不是功能问题。

---

## 6. F：不夸大 / 口径

| 检查 | 结果 |
|---|---|
| 不得写「只读切片已可恢复」 | 卡/EV/Handoff 均明确写「不实现零交互自动恢复」「无写路径介入时仍不恢复」；未出现该夸大表述（AC-LS4-6 只声明「刷新后 Core 枚举跟随」） |
| L-S4-1 保留 | EV §5、Handoff §3、卡「已知 limitation」保留：A 修完仍缺触发器，零交互恢复需 B（C-16 v1.5，1/18 pins） |
| L-S4-2 保留 | 保留：folder 身份键未修；本卡只保证刷新复用写入时同一算法；apply 路径键不一致时 0 行 fail-closed |
| 撤销后不自动放行 | 代码/测试/证据均保留；无自动重新授权/自动恢复 |
| 不宣称 L-R1 全修 | 未出现 |
| D-2 行为变化登记 | EV §5、Handoff §3/§6、卡交付记录均登记「整源 skip 不再绝对零写」；测试覆盖 |
| 零契约 | 0/18 pins；`doc/plan/**`、`doc/contracts/**`、schema/migrator/依赖零 diff；`PROTOCOL_MINOR=3` |

**结论**：主口径成立。P3-02/03 是**证据措辞**层面的夸大（folder「已有测试」、撤销「无 operation 行」），不改变安全/功能结论；建议 closeout 修正措辞或补测试。

---

## 7. AC-LS4-1…8 判定

| AC | 判定 | 依据（本 Review 实测/复核） | 附注 |
|---|---|---|---|
| **AC-LS4-1 单点实现** | **MET** | 全 `src/**` 1 处 `UPDATE source_locations SET registry_id`（`library.py:2325`）；`service.py` 内联已删；`runtime.py` 无；生产调用点 3；B4 RED | Host 测试 fixture 的 SQL 不是生产实现（§1.3） |
| **AC-LS4-2 重导入/relink 刷新** | **MET** | relink 跨 registry：三列刷新、身份/binding/行数不变；同 registry 1→2 跟随且 binding 不抬代次；import 第二 project 页单元内刷新 | import 用例只数 current 行，未数总 location 行（P3-04） |
| **AC-LS4-3 sync apply 刷新（含 D-2）** | **MET** | 同容器 resync 跨 registry 在 `BEGIN IMMEDIATE` 内刷新；整源 skip 一次条件刷新、计数不变；`import_as_new` 全已引用零页刷新；B1/B3 RED | D-2 路径/独立写单元口径需 Lead 确认（P3-01/05） |
| **AC-LS4-4 撤销/负例 fail-closed** | **MET（核心）** | revoked apply typed、零写；revoked import skip 零写；错 digest/volume/file 0；同 digest 拷贝 0；scan 零写；不自动放行 | folder 错键无专门用例；撤销 apply 未断言无 operation 行（P3-02/03） |
| **AC-LS4-5 幂等/单调/审计** | **MET** | 同值 0 + 快照不变；同 registry 15→14 为 0；跨 registry 1 允许；lvt ISO；只写三列；B5 RED | 真实重复导入会更新 lvt（审计写入），与「同 payload 幂等」不矛盾；时间格式两制（P3-06） |
| **AC-LS4-6 枚举闭环** | **MET（Core 面）** | 单点刷新后 `source_list_scan_targets` 返回新 registry/gen；identity/projects 不变；枚举 14 表零写；代次回退被拒 | 无 import/apply→枚举的单条端到端用例；Host 端到端属 B（L-S4-1），本卡不宣称 |
| **AC-LS4-7 零漂移/门禁** | **MET** | pins 18/18；check PASS×2；API EXIT=0；scope 21/7 全 allowed、zero-drift 空、MINOR=3；pytest 3317/10；.NET 1570/0/92（证据日志） | .NET 非本 Review 独立重跑、非隔离 head（P3-07） |
| **AC-LS4-8 不夸大** | **MET** | L-S4-1/L-S4-2/撤销语义保留；无「只读切片已可恢复」/零交互自愈/L-R1 全修；D-2 登记 | 证据措辞有两处 P3 精度问题（P3-02/03） |

---

## 8. Findings（P0/P1/P2 = 0；P3 = 7，全部非阻断）

| ID | 级别 | 位置 | 事实 | 证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| **R1-P3-01** | P3 | `src/application/importing/referenced/runtime.py:602-613`；`tests/fea09/test_import_source.py:221-244`；卡 AC-LS4-3、D-2 | 实现除 `duplicate_policy=="skip"` 的整源 early-return 外，还在 `import_as_new` 的「全页已引用、零页」outcome 上刷新。条件仍是 live grant + 同 identity；已测试/登记，但 D-2 字面只写「整源 skip」，scope review §4.2 的 optional 项也只点名 `runtime.py:396-410` early-return。 | 代码：`progress.committed_pages == 0 and progress.outcome == "skipped"`；测试 `test_all_pages_already_referenced_import_as_new_still_refreshes`；EV/Handoff 明写「全页已引用的零页路径」 | closeout 明确 D-2 覆盖该零页 outcome；若 Lead 认为只允许 `duplicate_policy=="skip"` early-return，则把该分支收窄（并删/改测试）。不需要改 SQL。 | open（非阻断） |
| **R1-P3-02** | P3 | `tests/fea11/test_source_relink.py:383-479`；`tests/fea09/test_source_sync_operations.py:212-235`；Handoff §3、EV §5 | 卡/EV/Handoff 的 AC-LS4-4 写「folder 错键 → 0 行」「已有测试/测试覆盖」，但四个交付测试文件无 folder grant；现有用例只覆盖通用 identity 键（digest/volume/file）与同 digest 拷贝。行为上 folder 错键由同一 SQL 守卫返回 0，未发现功能缺陷。 | `git grep folder` 四文件无命中；`test_refresh_source_location_auth_fail_closed_guards` 用普通行、`test_identical_copy...` 用 repoint 拷贝 | 补一条 folder 首成员 facts 与 location 行不一致的 apply 用例；或把「已有测试」改为「通用 identity 守卫已覆盖，folder 专门用例待补」。 | open（非阻断） |
| **R1-P3-03** | P3 | `tests/fea09/test_source_sync_operations.py:238-305`；EV AC-LS4-4 行 | EV 写撤销 apply「无 operation 行」，用例实际只断言 location/binding 行与 location 行数；未查询 `source_operations`。代码上 revoked 在 `_execute_decisions` 的 resolve 处失败、operation 插入在失败前会回滚，故行为应为零 operation，但证据未锁定。 | 用例 284-305 无 operation 查询；`service.py:249-264` 插入 operation 后调 `_execute_decisions`，失败回滚 | 补 `SELECT COUNT(*) FROM source_operations` 断言；或删除「无 operation 行」措辞。 | open（非阻断） |
| **R1-P3-04** | P3 | `tests/fea09/test_import_source.py:113-149`；`:152-183` | import 复用用例只断言 `len(_current_location(conn))==1`（current 行），未断言 `source_locations` 总行数；若未来 bug 插入 non-current 重复行，该用例不会红。整源 skip 用例名为「once」，但只断言最终状态/计数，未直接计数 SQL 写次数。 | 用例 147、180-182；代码 `insert_source=False` 路径不插 location | import 用例加 `SELECT COUNT(*) FROM source_locations`；「once」用 spy/rowcount/唯一 lvt 或删「once」措辞。 | open（非阻断） |
| **R1-P3-05** | P3 | `src/application/importing/referenced/runtime.py:661-671`；`library.py:2341-2353` | `_refresh_skipped_source_auth` docstring 写「Never raises — the skip stays the outcome」，实际只 catch `SourceImportError`（resolve）；`commit_source_location_auth_refresh` 的 SQLite 错误会向上抛，worker 会把 skip 操作标 failed。功能上 fail-closed 可接受，但 docstring/Handoff 的「skip stays」承诺不成立。 | 代码 680-683；wrapper 2352 `with self._conn` | 明确「resolve 失败不抛；DB 写失败按 fail-closed 上抛」；或 try/except DB 错误并日志，确保 skip 语义。 | open（非阻断） |
| **R1-P3-06** | P3 | `verification/.../RESOURCE-MANIFEST.json:37,181`；`scope-validation.log:3`；`doc/handoffs/...:126-127` | 簿记细节：(a) Manifest `file_count=27` 是重复 commit 条目数，不是唯一文件数（唯一 21）；(b) scope log 的 `--commits` 不含 `3f37b74ee`/`4e8bda6e1`（最终 docs/证据提交），虽均 ALLOWED、本 Review 手工复核通过；(c) `last_verified_at` import `+00:00`、apply `Z` 两种格式；(d) AC-LS4-1「全仓」若按字面含 Host 测试 fixture SQL，则不成立。 | Manifest/scope log；§1.3/§2.4 | closeout 保持「唯一文件数 21/证据树 11」区分；scope 补最终 docs 提交或注明自排除；时间格式可统一；AC 措辞限定「生产 src/**」。 | open（非阻断） |
| **R1-P3-07** | P3 | `logs/full-dotnet.log`；Handoff §2；EV §2 | 全量 .NET 在 `repo_head=89757f193`（L-S1 docs-only；`apps/**` 字节等于 `0ebb234bf`，但 `0ebb234bf` 已含 L-S1 祖先 `b56c5a0e6` 的 Host 测试），不是「仅含 L-S4 改动」的隔离树；1570/0/92 的 +8/+1 归 L-S1，不能作为本卡 Host 增量的独立证明。本卡 Host 零 diff，故无回归结论仍成立；本 Review 未重跑 .NET。 | `git diff 0ebb..89757 -- apps` 为空；日志逐 assembly 汇总；`89757` 为 docs-only | closeout 明写「.NET 数字为交付树（含并发 L-S1 Host 测试）证据，L-S4 不独立重跑」；或 Lead 在干净隔离 head 重跑并记录。 | open（非阻断） |

> 说明：R1-P3-01/02/05 是 **口径/证据** 而非功能缺陷；R1-P3-03/04 是测试强度；R1-P3-06/07 是簿记/归因。均不要求返修实现；closeout 可措辞修正或在后续维护卡补测。

---

## 9. 最终 verdict

**`approved`。P0 = 0 / P1 = 0 / P2 = 0 / P3 = 7（非阻断）。**

- 单点实现（AC-LS4-1）、重导入/relink 刷新（AC-LS4-2）、sync apply/D-2 刷新（AC-LS4-3）、撤销/identity fail-closed（AC-LS4-4 核心）、幂等/单调/审计（AC-LS4-5）、Core 枚举闭环（AC-LS4-6）、零漂移/门禁（AC-LS4-7）、不夸大（AC-LS4-8）均成立。
- 独立实跑：定向 26 passed、全量 3317/10、pins 18/18、check PASS×2、API EXIT=0、scope 21/7 全 allowed；破坏性 7/7 RED + 7/7 字节级恢复 + 恢复后绿 + 三文件 CLEAN。
- 未发现 P0/P1/P2。P3 中 R1-P3-01/02 建议 Lead 在 closeout 明确 D-2 路径口径与 folder 负例措辞；其余为测试强度/证据簿记，不阻断集成。
- **本 Review 不宣称**「只读切片已可恢复」、零交互自愈、L-R1 全修；L-S4-1/L-S4-2 与「撤销后不自动放行」保留。

---

## 10. 真实性声明

1. **唯一仓库写入**：本 Review 只写了 `doc/reviews/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-r1.md` 这个文件。未修改/删除/移动任何生产代码、测试、契约、冻结记录、Task 卡、STATUS、REBASELINE_PLAN、TASK_LEDGER 或 canonical evidence 字节；未执行 `git add`/`git commit`/`git push`。
2. **仓外临时操作**：为独立复跑，在 `%TEMP%` 创建了临时 Python 驱动与字节备份；它们不在仓库内，不作为交付物。复跑时对 3 个源文件做「备份 → 破坏 → 恢复」，7/7 恢复 sha256 MATCH，最终三文件与 `0ebb234bf` 一致；`git status` 三文件 CLEAN。未写 `logs/discrimination.log` 或任何 evidence 文件。
3. **上下文独立**：本 Review 为 fresh subagent，未参与本卡实现、返修、scope review 或前轮审查；只读 `0ebb234bf` 实现/测试字节与 `4e8bda6e1` 证据字节。作者/实现者未参与本报告结论。
4. **并发披露**：评审期间共享 `main` 工作树由另一会话推进：L-S1 review 从 `??` 变为提交 `9dc1cb0cd`，`doc/handoffs/DSH-PROGRESS-2026-11-07.md` 为并发 `M`；这些字节非本 Review 产物。`9dc1cb0cd` 不含 `src/**`/`tests/**`/`apps/**`/契约变化；本 Review 的代码/测试事实仍以 `0ebb234bf` 字节为准。
5. **实跑 vs NOT_RUN**：pytest 定向/全量、pins、check×2、API inventory 均本轮实跑并记录数字；**全量 `dotnet test` 未由本 Review 重跑**，只核验 Lead 证据日志（1570/0/92，repo_head=89757f193）并核对程序集汇总与归因；真实 IPC 注入未跑（本卡 Host 零改动，任务未要求）。
6. **判别力声明**：本 Review 独立复跑了证据工具定义的全部 7 个破坏点（不仅 1–2 个），每例均 RED → 原字节恢复 sha256 MATCH → 恢复后目标用例绿；`logs/discrimination.log` 的 7/7 与独立复跑一致。该日志本身不逐例打印恢复后绿输出/原始 sha，属 P3 证据完备性，不影响判别力结论。
7. **不夸大**：本报告不写「只读切片已可恢复」、不写「零交互自愈」、不写「L-R1 全修」；L-S4-1/L-S4-2 与撤销语义保留；D-2 行为变化明确登记。
