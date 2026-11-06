# FEA-11-SCAN-2 分片 A（Core Python）实施记录

> 任务卡：`doc/tasks/FEA-11-SCAN-2.md`（ready，已冻结；base `703d9eb12`）
> 契约：C-17 v1.1，commit `7451bfaaa`，sha256 `aefa0fa5…`（冻结；`source_list_scan_targets` / `ScanTarget`/`ScanTargets` / `source.sync.enumerate/1` 见 §5.1/§5.2/§5.3/§8）
> 分片：**A = Core Python**（本记录）；B = Host/App .NET（`fea12-core-host`，task-18）另记
> 实现者：`fea12-core-py`；本记录随 shard A commit 入库；证据 pin 由 Lead 集成时写入任务卡
> 状态：实现完成、待独立 Review；不 push

## 1. 交付内容（仅本分片 allowed_paths）

| 文件 | 变更 |
|---|---|
| `src/infrastructure/sqlite/source_sync.py` | 新增 `SourceSyncStore.list_scan_target_candidates()`：单次 SELECT 级只读投影（`sources` LEFT JOIN 当前 `source_locations`；`project_ids` 为 `page_bindings` 中该源非 superseded 绑定的 distinct 去重集合）；零写、不建 plan/apply/operation/receipt/grant/journal |
| `src/application/sources/scanner.py` | 新增 `list_scan_targets(store)`：计算 `identity_digest_of(location facts)`、排序/去重、typed skip 计数日志、`SOURCE_BUDGET_EXCEEDED` 预算判定；常量 `SCAN_TARGETS_MAX=10000`、`SCAN_TARGETS_MAX_BYTES=8MiB`、`SCAN_TARGETS_MAX_PROJECT_IDS=20`、`KNOWN_SOURCE_KINDS`（五值） |
| `src/bootstrap/core_service.py` | `_SOURCE_SYNC_APP_COMMANDS` 增加 `source_list_scan_targets`（application 面，非 host-control）；dispatch 强制 closed shape `{}`（未知键/非对象 → `INVALID_REQUEST`/validation，零写）；`core.ping.capabilities` 追加 `source.sync.enumerate/1`（仍只在 ping 列表；Host §5.2 `Capabilities` DTO 固定 7 项不变） |
| `tests/core/test_core_scan_target_commands.py`（新增） | 8 条 Core 侧判别测试（见 §3） |
| `tests/core/test_core_service.py` | 两处 `core.ping.capabilities` 精确列表追加 `source.sync.enumerate/1`（含真实子进程 e2e） |

未触碰：`apps/**`（分片 B 并行）、`tests/fea11/**`、`doc/plan/**`、`doc/contracts/**`、schema/migration/依赖、STATUS/PLAN/LEDGER/reviews、任务卡。

## 2. 冻结语义实现说明

1. **B1 / S-2 权威**：`targets[].source_id` 唯一来自 Core `sources.source_id`（`src-<uuid>`），不接受 Host/App 计算值；`registry_id`/`generation`/`source_kind`/location facts 均来自 Core 当前行。
2. **顺序/唯一**：`targets` 按 `source_id` 升序；返回前对 `source_id` 去重（首条候选优先，防御重复投影）；空数组合法。
3. **identity**：`identity_digest = identity_digest_of(content_digest, volume_serial, file_id, size_bytes)`（`model.py` 冻结函数，直接复用，不另造 canonical 规则）。
4. **closed shape / 只读**：`{}` 之外一律 `INVALID_REQUEST`；实现路径只有 SELECT + 纯计算，无任何 `INSERT/UPDATE/DELETE/COMMIT`，不产生 plan/apply/operation/receipt/grant/journal。
5. **typed skip（不伪造、不截断、不回退 current）**：
   - 当前 `source_locations` 缺失或 location facts 不完整/损坏 → 跳过并计数 `missing_location_facts`；
   - `source_kind` 不在五值冻结集合 → 跳过并计数 `unknown_source_kind`（fail-closed，不猜测）；
   - `project_ids` 去重数 > 20 → 该 target 不进入 `targets`，计数 `project_ids_over_limit`（不截断、不回退 current）；
   - skip 计数写 stderr 结构化行 `[core.source_list_scan_targets] skipped …`；DTO 保持冻结 `{targets:[]}` 形状（契约无 skip 字段，不自行扩 DTO）。
6. **预算**：`targets` 超过 10000 或紧凑 JSON 超过 8MiB → `SOURCE_BUDGET_EXCEEDED`（validation、retryable=false），绝不静默截断。
7. **能力**：`source.sync.enumerate/1` 只加入 `core.ping.capabilities`；`GetSourceSyncCapabilities` 仍为 Host 本地聚合（Core 不注册该命令）；不新增 Host C-07 注册项、不新增 UI 命令面。
8. **软删源**：枚举排除 `sources.deleted_at IS NOT NULL`（软删源不进入冷启动扫描目标；判定依据：目标集是“可扫描已注册源”，软删源不应被重新扫描；契约未逐字规定，按 fail-safe 解释实现，供 Review 确认）。

## 3. 测试与判别证据

新增 `tests/core/test_core_scan_target_commands.py`（8 条，全部通过）：

| 测试 | 覆盖 / 判别对象 |
|---|---|
| `test_enumeration_empty_is_legal_and_zero_write` | 空库 → `{"targets":[]}`；14 表快照逐行相等；ping 含 `source.sync.enumerate/1` 且既有 7 项仍在 |
| `test_enumeration_does_not_create_plan_apply_or_journal` | 枚举前后 14 表快照相等；`source_sync_plans`/`source_operations` 均 0 行 |
| `test_enumeration_is_sorted_unique_and_computes_identity` | 双源升序；superseded 绑定不计入 project_ids；软删源排除；`identity_digest` 精确等于冻结函数；键集合恰为 DTO 六字段；重复调用幂等（去排序/去重判别） |
| `test_identity_and_facts_are_recomputed_from_current_location` | current location facts 改变 → generation/identity 跟随重算（伪造/缓存 identity 判别） |
| `test_enumeration_closed_shape_rejects_unknown_keys` | 未知键与非对象 payload → `INVALID_REQUEST`/validation/非重试；零写 |
| `test_typed_skips_missing_facts_unknown_kind_and_project_limit` | 缺 location、`future-kind`（schema CHECK 绕过注入）、21 books 共享源 → 三者均 skip 且 stderr 计数各 1；健康源仍返回；不伪造/不截断 |
| `test_budget_limits_are_typed_and_never_truncate` | 10001 目标 → `SOURCE_BUDGET_EXCEEDED`（typed，无部分 DTO）；字节预算小值覆盖 → 同码 |
| `test_duplicate_candidates_are_deduped_and_sorted` | fake store 重复/乱序候选 → 唯一 + 升序（去重/去排序判别） |

**变异判别**（隔离临时 `src` 副本，仓内源码不变；`logs/core-mutation.log`）：去排序、去去重、放宽 10000 上限、伪造 identity 四种变异均使目标测试转红（`MUTATION_SUMMARY: PASS (all 4 mutations discriminated)`）。

## 4. AC 映射（本分片证据）

| AC | 分片 A 证据 | 状态 |
|---|---|---|
| AC-S2-1 冷启动枚举 | Core 侧：`source_list_scan_targets` 命令/closed shape/只读/空库/排序去重/identity；capability 公告；**真实重启 IPC 与 Host 白名单属分片 B** | Core 侧实现完成；AC 整体待 B 合并后判 |
| AC-S2-2 合并去重 | 与 SCAN-1 目标按 `source_id` 合并属 Host 侧（B）；Core 保证 `source_id` 权威、唯一 | 不在本分片 |
| AC-S2-3 source_id 权威（S-2 判别） | Core 枚举 `source_id` 来自 `sources`（测试断言 `src-<uuid>` 值直达 DTO、registry_id/StableSourceId 不参与）；App 误用 StableSourceId 的转红测试属 B | Core 侧完成 |
| AC-S2-4 registry 授权核验 | Host 持久 registry 匹配/typed skip 属 B；Core 仅提供 `registry_id`/`generation` | 不在本分片 |
| AC-S2-5 启动前缺失（S-1②） | Host file-root/registry 缺失 typed `SOURCE_REGISTRY_UNAVAILABLE` 属 B（Core 枚举不返回路径/secret） | 不在本分片 |
| AC-S2-6 共享源 project_ids 边界 | `test_typed_skips_…`：≤20 正常进入（双 project 用例）；>20 不进入 + `project_ids_over_limit` 计数，不截断/不回退 current | **Core 侧完成** |
| AC-S2-7 预算/单飞/退避/取消 | 枚举自身 10000/8MiB typed 预算；Host 首轮 8 目标/256MiB、单飞/退避/取消属 B | Core 侧预算完成 |
| AC-S2-8 零写/脱敏 | 14 表快照逐行相等、无 plan/journal；缺 location facts 不伪造 identity；DTO/日志无路径/secret/grant（Core 侧静态检查） | **Core 侧完成** |
| AC-S2-9 门禁与回归 | 见 §5（Full pytest 3211/10 ≥ 3203/10；check/pins/API inventory/scope diff PASS）；`pytest tests/fea11` 与 .NET 全量属 B/集成 | 本分片门禁 PASS |

## 5. 门禁与证据（分片 A 工作树，HEAD 见 shard A commit）

| Gate | 命令 | 结果 | 证据 |
|---|---|---|---|
| G1 Core 单测 | `pytest tests/core -q -p no:cacheprovider` | **956 passed** EXIT 0 | `logs/core-pytest-core.log` |
| G1b fea09 | `pytest tests/fea09 -q -p no:cacheprovider` | **142 passed** EXIT 0 | `logs/core-pytest-fea09.log` |
| G1c 相关组合 | `pytest tests/core tests/fea09 -q -p no:cacheprovider` | **1098 passed** EXIT 0 | `logs/core-pytest-core-fea09.log` |
| G2 全量 Python | `pytest tests -q -p no:cacheprovider --tb=short` | **3211 passed / 10 skipped** EXIT 0（基线 3203/10，+8 新测试，0 回归） | `logs/core-pytest-full.log` |
| G3 治理 check | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-SCAN-2.md` | **PASS (3 warnings)** EXIT 0 | `logs/core-check.log` |
| G4 pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **18/18 PASS** EXIT 0 | `logs/core-pins.log` |
| G5 API inventory | `python tools/generate_api_inventory.py --check` | **PASS** EXIT 0 | `logs/core-api-inventory.log` |
| G6 scope diff | `git diff --name-only 703d9eb12 -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py` | **空（0 文件）** | `logs/core-scope-diff.log` |
| G7 变异判别 | 隔离副本 4 变异 | **PASS（4/4 转红）** | `logs/core-mutation.log` |

全量 3203→3211 的 +8 即本分片新增测试；其余为既有基线，无失败/无跳过新增。`apps/**` 未由本分片修改（分片 B 并行工作；完整 .NET 全量与真实重启 IPC 由 B/集成执行）。

## 6. 残余风险与待 Review 点

1. **软删源排除**：`sources.deleted_at IS NOT NULL` 不进入 targets（§2.8 fail-safe 解释）；若契约意图是“仅注册即可扫描”，需裁决。
2. **skip 可见性**：typed skip 计数仅写 stderr（契约 DTO 无 skip 字段，未扩形状）；Host 无法通过 DTO 感知被跳过原因；若需可观测，须另走 additive 契约。
3. **预算计数语义**：10000 上限按“已接受 targets”计数，被 skip 的候选不计入；8MiB 按紧凑 JSON 估算（`separators=(",",":")`），非 wire 转义后字节。
4. **location facts 损坏注入**：schema CHECK 使常规路径无法产生未知 kind/坏 facts，测试通过 `PRAGMA ignore_check_constraints` 注入；运行时防御为 fail-closed skip。
5. **Host 侧 AC**（AC-S2-1 真实 IPC、AC-S2-2/4/5/7、`tests/fea11`、全量 .NET）不在本分片，未在本记录宣称通过。
6. **pre-existing**：`core.ping.capabilities` 精确列表被本分片 additive 扩 1 项（8 项 source.sync 串）；Host §5.2 `Capabilities` DTO 仍固定 7 项（契约 v1.1 明确），Host 侧适配由 B 验证。
