---
task: FEA-11-SCAN-2
review: scope-r1（独立只读）
reviewer: 独立上下文 fresh subagent（未参与 FEA-11-SCAN-2 的实现；本会话只做 scope review，不参与实现/返修；派发父会话 session-8db9dae5-49df-4d09-ac62-696f0805a95c）
session: subagent-of-session-8db9dae5-49df-4d09-ac62-696f0805a95c（子会话 ID 以 DSH 派发记录为准）
date: 2026-11-06
verdict: READY-WITH-UNFREEZE
repo: G:\CODEX\New Manga
repo_head: c5d30e4ca730b7a602ed1bb3ed382fedb6c59e11
head: c5d30e4ca730b7a602ed1bb3ed382fedb6c59e11
head_note: main；工作区 clean；origin/main..HEAD=957（仅本地远端跟踪引用，未 fetch，不等同实时远端）；未 push
code_baseline: c5d30e4ca（apps/src/tests 与 Codex 决策基线 e54dc5129 无差异；e54dc5129..c5d30e4ca 仅 PLAN/STATUS/TASK_LEDGER/本卡 4 个文档）
---

# FEA-11-SCAN-2 scope review（r1）

> **结论：`SCAN-2-SCOPE: READY-WITH-UNFREEZE`。**
>
> 推荐 **B1**：Core 新增只读枚举命令 + Host 用持久 registry 核验授权、解析路径并铸造新会话 grant；**必须**做 C-17 v1.1 UNFREEZE/独立复核/重冻（pin #18 重算，仍 18 份），**不需要** schema/migration，**不需要** M2-C1 增量，**不建议** B2。
>
> 除契约外还有两个**必须先由 DSH 裁决**的事实级问题（不解决则 AC 不可达或会重复犯错）：
> 1. **S-1（阻断本卡“启动前缺失→missing”AC）**：生产引用导入把**文件本身**注册为 registry root；`SourceAccessRegistry.Load()` 对每个 root 重验身份，文件被删除/替换时整个 registry 抛 `SOURCE_REGISTRY_UNAVAILABLE`，不是 `missing`。SCAN-1 的 missing 证据用的是“父目录 root”fixture，未覆盖生产形状。
> 2. **S-2（必须由本卡修正）**：App 侧用 `StableSourceId(path)`（文件）或 `registry_id`（folder）注册扫描目标，而 Core 新源的真实 `source_id` 是 `src-<uuid>`（Core 自生成）；C-16 receipt **不返回** `source_id`。因此 SCAN-1 的“导入完成后注册”生产路径**没有经过真实 Core 判别**，in-session 也会以错误 `source_id` 扫描失败。B1 必须以 Core 枚举的 `source_id` 为唯一权威，并废弃 App 侧推导。
>
> 本次只读：未修改仓库、未 commit/push、未运行 pytest/.NET；执行了 Git 只读核验、`verify_pins.ps1`（18/18 PASS）、`check.ps1 -TaskPath`（PASS，3 个既有 warning）与定向文档/代码阅读。

---

## 0. 回答索引（对应任务要求的 8 问）

| # | 问题 | 本报告节 |
|---|---|---|
| 1 | B1 可行性（Core 事实 / Host registry / DTO 逐项） | §1 |
| 2 | B2 对比与 B1/B2/BLOCKED 裁决 | §2 |
| 3 | 范围冻结建议（In/Out、与 SCAN-1 边界、WATCH-1） | §3 |
| 4 | AC 草案与判别性测试 | §4 |
| 5 | 契约/UNFREEZE | §5 |
| 6 | 写域 allowed_paths 与禁止项 | §6 |
| 7 | 风险/limitation | §7 |
| 8 | `SCAN-2-SCOPE` 裁决与 DSH 下一步 | §8 |

---

## 1. B1 可行性（逐项 file:line 证据）

### 1.1 Core 是否已拥有冷启动枚举所需的业务目标事实

**结论：业务事实已存在，枚举命令不存在。**

| 事实 | 是否存在 | 证据（file:line） | 说明 |
|---|---|---|---|
| `source_id` / `source_kind` | **已存在** | `src/infrastructure/sqlite/schema.py:619-626` | `sources(source_id PK, source_kind IN image/folder/zip/cbz/pdf, deleted_at)`；Core 业务权威真值 |
| 当前 location 的 `registry_id` / `authorization_generation` | **已存在** | `src/infrastructure/sqlite/schema.py:629-645`（`source_locations`）；写入 `src/infrastructure/sqlite/library.py:2276-2291`；读取 `src/infrastructure/sqlite/source_sync.py:656-665` | 导入时由 grant 的 `(registry_id, generation)` 写入；每个 source 仅一个 `is_current=1` |
| 物理 identity facts（content_digest/volume/file_id/size） | **已存在** | `schema.py:632-638`；identity 公式 `src/application/sources/model.py:255-268` | 可计算 `identity_digest`；正是 C-17 §5.3 `MissingObservation.expected_identity_digest` 所需的已记录基线 |
| `project_ids`（引用该 source 的 book 集合） | **已存在** | `page_bindings(project_id, page_id, status, ...)` `schema.py:698-724`；整源引用集合查询 `source_sync.py:427-463` | 只取 `status <> 'superseded'`，含软删页（C-17 §5.3 冻结引用集合口径） |
| 扫描所需“旧版本/条目”基线 | **已存在** | `source_sync.py:644-654`（latest version）、`:667-678`（entries） | 枚举本身不需要返回；scan 内部使用 |
| 枚举命令 / 对应 capability / DTO / 错误闭集 | **不存在** | `src/bootstrap/core_service.py:355-371`（既有 host-control/app 命令白名单，无枚举名）；`:6345-6370`（app 面只路由 `_SOURCE_SYNC_APP_COMMANDS`）；`:7414-7429`（未知命令 UNKNOWN_COMMAND） | 必须新增 Core 只读命令；需 C-17 v1.1 登记命令 + DTO + 错误闭集 + capability |
| Core 路径 / locator（绝对路径） | **设计上不存在** | C-15 I-6 `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:21`；`source_locations` 无路径列 `schema.py:629-645`；`source_entries.locator` 仅容器内相对 `schema.py:671` | **B1 不得由 Core 返回路径**；路径只能来自 Host registry（见 1.2） |
| Core 是否按 grant 的 `scope.source_id` 建源 | **否（关键反例 S-2）** | `src/application/importing/referenced/runtime.py:457-471`（`source_id = existing_source_id or f"src-{uuid.uuid4().hex}"`）；`:761-793`（binding 用该 `source_id`）；`:70-82`、`:289-305`（receipt item 无 `source_id`）；C-16 receipt 冻结形状 `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:127-139` | App 的 `StableSourceId` / folder `registry_id` **不是** Core `source_id`；C-16 receipt 也不返回它 |

**Corollary（S-2 证据链）**：

- App 注册（文件）：`apps/desktop-avalonia/src/NewManga.App/Services/SourceImportModels.cs:761-802`，`sourceId = StableSourceId(path)`（`:786`），实现 `:920-924`（`src-` + 路径 sha256 前 16 hex）。
- App 注册（folder）：同文件 `:777-782` 取 `registry_id`；grant scope 也用 `registry_id`（`:805-816`）。
- 真实 Core 导入：`runtime.py:470` 生成随机 `src-<uuid>`；binding `:783`；`GetImportReceipt` `:289-305` 不含 `source_id`；C-16 冻结 receipt `:127-139` 不含 `source_id`。
- 唯一通过的真实 IPC 证据 `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11ScanIpcTests.cs:31-74` 用的是 **seed 脚本**返回的 `source_id`（`:33`），不是 App 的注册路径；注册目标 `:74` 直接使用该 seed id。
- App 侧测试 `Fea11ScanRegistrationTests`（同文件 `:450-481`）只断言注册结构（`:469` 期望 `StableSourceId`），**没有**任何真实 Core 判别。

**因此**：B1 不只是“冷启动覆盖”，还是**修正 SCAN-1 生产身份假设**的必要条件；SCAN-2 的 AC 必须包含“真实完成导入 → 枚举 → target 使用 Core `source_id`”的判别测试（§4 AC-S2-4）。

### 1.2 Host 持久 registry 是否已存在且可恢复

**结论：已存在、可恢复；但只有授权事实，没有 source→project_ids/kind 映射。**

| 事实 | 是否存在 | 证据（file:line） | 说明 |
|---|---|---|---|
| 持久 registry 文件 + DPAPI + 原子替换 + 锁 | **已存在** | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs:13-32`（路径/锁/私有目录）、`:98-139`（Load 解密/校验）、`:141-173`（临时文件 + `Flush(true)` + `File.Replace`）、`:175-199`（命名互斥 + `registry.v1.lock`） | 重启后可恢复；`SourceRegistryTests.cs:21-49` 覆盖 reopen/revoke/corrupt/reset |
| 键 / 代次 / 撤销 | **已存在** | `SourceAuthorization` `:9-10`（`RegistryId, Locator, Generation, ..., RevokedAt, Roots`）；`Register` `:34-52`（generation=1）；`Revoke` `:76-86`（generation+1 + `RevokedAt`） | 授权真值在 Host；Core 只记录 `registry_id/generation` 作为受限读取基线 |
| 每个 root 的物理身份 | **已存在（仅 volume/file id）** | `:8`（`SourceRoot(Root, VolumeSerial, FileId, IdentityVerifiedAt, Readable)`）；`:44-48`（Register 时记录）；Load `:119-128`（逐 root 重验 volume/file id） | **不含** content_digest/size；`Readable` 字段在 Load 中被当作必须为 true（`:125`） |
| `identity_facts`（C-15 §5 规范的字段） | **字段存在但从未写入** | `:10`（`object? IdentityFacts = null`）；`:49`（`Register` 只传 7 个位置参数，IdentityFacts 取默认 null）；C-15 规范 `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:296-304` | **不要依赖** registry 的 `identity_facts` 做身份比对；B1 使用 Core 返回的 `identity_digest` |
| source_id / project_ids / kind 映射 | **不存在** | `SourceAuthorization` 字段列表 `:9-10`；registry 无 source 维表 | B1 的 Core 枚举正是补足这一映射；Host 不建第二套索引 |
| locator → 生产路径 | **已存在（生产 locator=路径）** | `SourceImportModels.cs:214-223`（`RegisterRoot`：`locator = path`，`roots=[path]`）；Host handler `SourceReadCoordinator.cs:235-237`；App 导入 `:805-816` | B1 的 Host 侧可从 registry_id 找到 entry，再以 `locator` 解析路径；**不得**把 locator 直接写日志/状态 |
| registry 缺失 root 的失败语义（S-1） | **实现为整库损坏** | `SourceAccessRegistry.cs:119-128`（每个 root 调 `SourceSecurity.Identity(root.Root)`）；`:132-138`（任意异常 → 复制 corrupt + `SOURCE_REGISTRY_UNAVAILABLE`）；`SourceSecurity.cs:86-103`（缺失路径 → `SOURCE_ACCESS_DENIED`；`:113-118` 打开文件/取身份） | 生产 file-root 被删除/替换 → 整个 registry 不可用；**SCAN-1 的 missing 只在父目录 root fixture 下通过**（`Fea11ScanIpcTests.cs:49-59` 注册 `roots=[root]`，删除的是 `root` 下的 zip） |

### 1.3 卡内示例 DTO 逐字段结论

卡面示例：`ListSourceScanTargets → {source_id, registry_id, generation, identity_facts, project_ids[]}`。

| 字段 | 结论 | 依据 |
|---|---|---|
| `source_id` | **已有事实，需新增命令返回** | `schema.py:619-626`；Core 自生成 `runtime.py:470` |
| `registry_id` | **已有事实，需新增命令返回** | `schema.py:632`；`library.py:2276-2291` |
| `generation` | **已有事实，需新增命令返回** | `schema.py:633`；语义同 C-17 `AuthorizationBase.generation`（`FEA-C17_SOURCE_SYNC_DRAFT.md:238`） |
| `identity_facts` | **建议改为 `identity_digest! H`** | Core 已有 facts 但返回 `identity_digest` 即可满足 `MissingObservation.expected_identity_digest`（C-17 `:239`、`:261`、`:273`；公式 `model.py:255-268`）；避免把 volume/file id 作为 DTO 面扩大暴露 |
| `project_ids[]` | **已有事实，需新增命令返回** | `page_bindings` `schema.py:698-724`；`source_sync.py:427-463` |
| 缺少的 `source_kind` | **必须补** | Host `SourceReadCoordinator.IssueAsync` 要求 `sourceKind ∈ image/folder/zip/cbz/pdf`（`SourceReadCoordinator.cs:44-60`）；路径解析也需要区分 folder/file；`schema.py:621` 可返回 |
| 缺少的“version” | **不是 Core 事实，不需要返回** | scan grant 的 `scope.version` 是 Host 侧 opaque 字符串（`SourceReadCoordinator.cs:86-94`；Core `scanner.py` 不校验 version 与 DB）；SCAN-1 在 App 注册时固定 `"1"`（`SourceImportModels.cs:794-795`），executor 原样传给 `IssueAsync`（`SourceScanScheduler.cs:738-740`），SCAN-2 可沿用并冻结 |

**新增命令的形态建议**（供 C-17 v1.1 使用）：

```text
source_list_scan_targets            （application channel；request 必须恰为空对象 {}）
→ { "targets": [ ScanTarget... ] }
ScanTarget = {
  source_id! ID;
  registry_id! ID;
  generation! G;
  source_kind! "image"|"folder"|"zip"|"cbz"|"pdf";
  identity_digest! H;
  project_ids! ID[1..10000]          // 去重、按 ID 排序；Host 对 >20 的来源 typed skip
}
```

> 卡面示例名 `ListSourceScanTargets` 是 CamelCase；C-17 既有 app 面命令是 lowercase snake（`FEA-C17_SOURCE_SYNC_DRAFT.md:213-227`），建议按 app 面惯例用 `source_list_scan_targets`，并在 Host 侧只做**内部直连**（不登记 `HostCommandRegistry`，无 UI 面）。

### 1.4 明确“已存在 / 需新增命令 / 需 UNFREEZE / 需 schema”

| 类别 | 项 | 结论 |
|---|---|---|
| **已存在** | Core `sources`/`source_locations`/`page_bindings`/`source_versions`/`source_entries`；`identity_digest_of`；Host registry 文件/代次/撤销/root 身份/locator；grant 铸造 `SourceReadCoordinator.IssueAsync`；`ScanSourceSync`；host-control 会话；`source.read/1` + `source.sync.scan/1` 能力 | **直接复用** |
| **需新增 Core 命令** | `source_list_scan_targets` + capability `source.sync.enumerate/1` + closed DTO + 只读查询；**无新错误码**（复用 `INVALID_REQUEST`/`CORE_CAPABILITY_MISSING`/`SOURCE_BUDGET_EXCEEDED`/`SOURCE_SYNC_STORAGE_FAILED`） | **需要** |
| **需 UNFREEZE** | C-17 v1.1（命令/DTO/capability/错误闭集/§9 清单 + pin #18 重算） | **需要**（见 §5） |
| **需 schema/migration** | 无 | **不需要**（v8 已存在；`schema.py:37` `SCHEMA_VERSION_V8`) |
| **需 M2-C1 增量** | 无 | C-17 §0 明确“命令面由 C-17 承载，M2-C1 无增量”（`FEA-C17_SOURCE_SYNC_DRAFT.md:16`） |
| **需改动既有 SCAN-1 行为** | scope 选择（单项目 current / 多项目 all）、status 增加枚举字段、App 注册语义改为“刷新触发” | 需要，但应逐项写入 SCAN-2 卡并更新 SCAN-1 相关测试；不重写扫描算法 |

### 1.5 B1 可行性的两个“但是”

1. **可行的是“枚举 + 对仍存在的源做只读扫描”**；**“启动前源已消失 → missing”在本卡现有 registry 语义下不可达**（S-1）。若 DSH 不接受对 registry 缺失 root 的解释/窄修，则本卡必须把该 AC 降级为 typed `SOURCE_REGISTRY_UNAVAILABLE`，并明确 L-G 仍未关闭。
2. **App 侧现有注册必须废弃或改为“刷新触发”**（S-2）；否则 B1 的枚举 target 与 App 的错误 target 混在同一张表，budget/backoff/status 会被污染，且“会话内导入合并”按错误 `source_id` 去重。

---

## 2. B2 对比与裁决

### 2.1 B2（Host 持久目标索引）的事实分析

| 维度 | B1（Core 只读枚举） | B2（Host 持久目标索引） |
|---|---|---|
| 覆盖**升级前已存在**的书库 | **能**（Core DB 是既有真值） | **不能**：升级前没有索引；首次运行仍为空，除非先做一次 Core 枚举（那就已经是 B1） |
| 与 Core 真实状态核对 | 每次枚举都是当前真值 | 无 Core 查询能力；删除/重指/代次变化只能靠扫描失败猜 |
| 是否形成第二套 Book/Page 库 | 否（只读投影，不持久） | 是高风险：`registry_id/project_ids/kind/version/path` 是 Core 业务事实的副本；需 DPAPI/ACL/版本/迁移/崩溃恢复 |
| 身份权威 | Core `source_id`（唯一权威） | Host 自存 `source_id`；仍无法解决 S-2（首次写入时 App 也不知道 Core `source_id`） |
| 契约变更 | C-17 v1.1（命令 + DTO + capability） | 无 C-17，但需 FEA-00 §8.2 / C-15 §5“Host 不得成为第二套数据库”审查；大概率需新 Host 私有契约/格式评审 |
| 删除/撤销/代次漂移 | 每次枚举按 Core + Host registry 双真值核对 | 本地索引易漂移，需额外核对协议 |
| 最小代价 | 一个 Core 读命令 + 一个 Host 枚举器 + 测试 | 新持久文件 + DPAPI/ACL + 迁移 + 对账 + 测试；且仍不能覆盖旧库 |
| 结论 | **推荐** | **不推荐**；只有在 B1 被独立证明不可行、且 B2 明确“不是 Book/Page 数据库、只做非权威缓存”时才考虑 |

### 2.2 裁决

- **B1 可行**（§1）；B2 **不应**作为本卡主方案。
- **不是 BLOCKED**：B1 的命令面/事实面都有；阻塞点只有 S-1（registry 缺失 root 语义）与 S-2（权威 source_id）两个**需 DSH 裁决/必须修正**的问题。
- 若 DSH 既不接受 S-1 的处理、也不接受降级 AC，则“启动前缺失→missing”这一条应标 **BLOCKED/DEFERRED**，但不阻塞“冷启动枚举 + 对存在源扫描”的主体；此时本卡仍可做 B1，只是 L-G 继续保留。

---

## 3. 范围冻结建议（In / Out、SCAN-1 边界、WATCH-1）

### 3.1 In（按文件/命令/AC 细化）

| # | In 项 | 涉及文件/命令 | 对应 AC |
|---|---|---|---|
| I-1 | Core 新增只读枚举命令 `source_list_scan_targets`（app channel，closed shape）与 capability `source.sync.enumerate/1`；只读 SQL；无新错误码 | `src/bootstrap/core_service.py`；`src/application/sources/enumerator.py`（新）；`src/application/sources/ports.py`；`tests/fea11/test_source_enumerate.py`（新）；`tests/core/test_core_service.py`（capability 精确列表） | AC-S2-1/2 |
| I-2 | Core store 只读查询：仅返回有 `is_current=1` location 且至少 1 条非 superseded binding 的 source；`project_ids` 去重排序；按 `source_id` 排序；≤10000 targets；8 MiB 上限 | `src/infrastructure/sqlite/source_sync.py`；`tests/fea11/test_source_enumerate.py` | AC-S2-2 |
| I-3 | Host 枚举器：Ready 后**异步**调用；单飞/合并；typed 失败/退避/取消；解析/校验 DTO（拒绝路径/重复/未知字段）；状态与脱敏日志 | `NewManga.Host/Sources/SourceScanTargetEnumerator.cs`（新）；`HostOptions.cs`；`HostRuntime.cs`；`SourceScanStatus.cs` | AC-S2-3/8/9 |
| I-4 | Scheduler 目标表以枚举为权威：按 `source_id` upsert、移除不再存在的目标；保留未变目标的 backoff/last 状态；不复位预算游标；单飞 | `SourceScanScheduler.cs`；`SourceScanSchedulerTests.cs` | AC-S2-3/4/8 |
| I-5 | 身份权威：Core `source_id` 为唯一 target key；**废弃** App 侧 `StableSourceId`/folder `registry_id` 注册；导入完成后只触发一次枚举刷新（不再传路径/source_id） | `SourceImportModels.cs`；`HostController.cs`；`NullHostController.cs`；`ImportDockViewModel.cs`；`FakeHostController.cs`；`HostRuntime.cs` | AC-S2-4 |
| I-6 | 授权核验：`registry_id` → registry entry（未撤销、generation 规则、root containment、reparse 拒绝）；可注入纯函数/接口以便矩阵测试；路径只用于铸造 grant，绝不进入 status/log/wire | `SourceScanScheduler.cs`（或新 `SourceScanAuthorization.cs`）；`SourceAccessRegistry.cs`（仅读）；测试 | AC-S2-5 |
| I-7 | 删除/缺失/代次漂移 typed：revoked → `SOURCE_GRANT_REVOKED`；registry 无 entry → `SOURCE_ACCESS_DENIED`；Core generation > registry → typed 拒绝；registry unavailable → 枚举级 `SOURCE_REGISTRY_UNAVAILABLE`；启动前缺失 → 用枚举 `identity_digest` 构造 `MissingObservation`（**条件：S-1 被 DSH 接受**） | `SourceScanScheduler.cs`；`SourceScanStatus.cs`；**条件性** `SourceAccessRegistry.cs`；真实 IPC 测试 | AC-S2-5/7 |
| I-8 | 多项目/共享源：1 个 project → `scope=current`；>1 → `scope=all` 且 `project_ids` 必须等于 Core 冻结引用集合；>20 → typed skip（不截断、不猜） | `SourceScanScheduler.cs`；`scanner.py`（只读，不改）；测试 | AC-S2-6 |
| I-9 | 冷启动首轮：首次成功枚举后**异步**触发一次受预算限制的 tick（复用 SCAN-1 的 8 targets/budget/backoff/单飞），不阻塞 Ready；后续刷新不立即 tick | `HostRuntime.cs`；`SourceScanScheduler.cs`；测试 | AC-S2-3/8 |
| I-10 | 契约/证据/回归：C-17 v1.1 UNFREEZE→独立复核→重冻→pin #18；pins 18/18；check；dotnet/pytest；真实 IPC；0 域外；无新依赖；证据与 Handoff | 见 §5/§6 | AC-S2-1/9 |

### 3.2 Out（明确不做）

| # | Out 项 | 理由/边界 |
|---|---|---|
| O-1 | watcher（`FileSystemWatcher`、hint 通道、overflow 语义） | 属 `FEA-11-WATCH-1`；本卡只核边界，不同时释放；0 watcher 代码 |
| O-2 | 扫描算法/匹配算法重写（`scanner.py`/`matcher.py`/`service.py` 行为） | SCAN-1 已交付；本卡只复用 `ScanSourceSync` |
| O-3 | plan/preview/confirm/apply/relink/repoint/resync/tombstone/删除/GC/清理 | 扫描必须零写；C-17 §3.1/§6 |
| O-4 | Core schema/migration（含 v9） | 无新表/列；v8 已存在 |
| O-5 | 新依赖（Python/NuGet/字体） | 硬边界 |
| O-6 | 通知/attention/UI/设置项/扫描结果持久化 | 后续切片；status 仍为 in-process |
| O-7 | Host 直连 Core DB | AD-002/C-15 硬边界 |
| O-8 | 第二套 Book/Page 库或持久目标索引（B2） | 见 §2；本卡不做 |
| O-9 | 真实用户数据/AppData/外部卷/回收站；push | 硬边界 |
| O-10 | C-16/C-15/C-06/C-09/C-14/M2-C1/ADJ-001/FEA-01 字节；其他 17 个 pins | 除 C-17 v1.1 授权 UNFREEZE 外不动 |
| O-11 | `IHostController.cs`/`RunContracts.cs`/`FEA-C07_API_INVENTORY.md`/C-07 冻结面 | 沿用 SCAN-1 先例：独立 `ISourceImportController`；不改 C-07 |
| O-12 | 自动重新授权/自动 reset registry/自动改写 Core location auth | C-15 §5/C-17：撤销后不自动恢复；需用户显式操作/重新导入 |
| O-13 | `refresh_source_location_auth` 接线、import 侧 auth 刷新、L10 rendition | **不在本卡**；见 §7 S-4/L10；如 DSH 要求冷启动撤销后可恢复，需另立窄卡 |
| O-14 | 大库性能 SLA/benchmark 硬门槛 | 本卡记录测量，不设未标定 SLA；L-E |
| O-15 | 多进程/第二 Host/Core 并发写 | 单实例 Host；只读查询 |

### 3.3 与 FEA-11-SCAN-1 的边界

| 面 | SCAN-1（done） | SCAN-2（本卡） | 边界 |
|---|---|---|---|
| 调度器/单飞/预算/退避/取消 | 已实现 | **复用**，只加枚举刷新与目标替换；不改 tick 语义 | 不重写 |
| 执行器/`ScanSourceSync` | 已实现（scope=current） | 复用；新增 scope 选择规则（1 项目 current，多项目 all） | 不改 Core scanner 算法；只改 payload 选择 |
| 目标来源 | App 导入成功注册（S-2 错误身份） | **Core 枚举为唯一权威**；App 侧改为刷新触发 | SCAN-1 的 App 注册语义被本卡取代；需在卡内明示并更新测试，不修改 SCAN-1 卡/证据 |
| 状态 | `SourceScanStatus`（enabled/interval/paused/targets/recent） | 增加 `enumeration` 子状态（last_attempt/result/error/target_count/skipped_count） | in-process，无 wire；需更新 SCAN-1 测试的构造/断言；不改变 `last_result` 六值 |
| 零写 | 只发 `ScanSourceSync` | 额外一条只读枚举命令；仍不写 Core | wire 白名单需新增枚举名；不得出现 plan/apply/relink/repoint/resync |
| 缺失 baseline | 会话内 `_identityDigests`（首次 ok 前缺失 fail-closed，L-G） | 用枚举 `identity_digest` 作为冷启动 baseline（**条件 S-1**） | 若 S-1 不被接受，L-G 保持 |

### 3.4 WATCH-1（只核边界，不同时释放）

- `FEA-11-WATCH-1` 仍是 `proposed`（`doc/tasks/FEA-11-WATCH-1.md:1-31`）；本卡**不得**引入 `FileSystemWatcher`、hint、事件队列、去抖窗口。
- 本卡交付后 watcher 可复用“枚举后的目标集/单飞/退避/全量重枚举”语义，但 watcher 的 producer/consumer 仍是独立卡；不得在 SCAN-2 顺带实现。
- 若在 SCAN-2 实施中发现必须加 hint 才能满足 AC，应停下报 DSH，不得扩卡。

---

## 4. AC 草案（可验证）与判别性测试

> 命名沿用卡面 `AC-S2-*`；建议 DSH 冻结时保持 10 条以内。每条均要求“判别性”：删掉实现/改坏实现必须变红；不得以 sleep/固定等待代替注入时钟；真实 IPC 用例与 fake-core 用例分列。

| AC | 冻结判定标准 | 判别性测试要求 |
|---|---|---|
| **AC-S2-1 方案、契约与门禁** | B1 为唯一方案；C-17 v1.1 完成 UNFREEZE → 独立上下文复核（P0/P1=0）→ 重冻；`verify_pins.ps1` **18/18 PASS**（C-17 pin 重算，数量仍 18）；`check.ps1` PASS；M2-C1 无增量、C-16/C-15/C-06 字节零 diff；无实现先于重冻 | ① 冻结记录含 reviewed_head/三指纹/复核 session；② 旧 C-17 pin 保留为历史；③ 未授权前 `git diff` 不含 `src/**`/`apps/**` 实现；④ `verify_pins` 输出 18 项且 C17 值等于新字节；⑤ `check.ps1 -TaskPath` PASS |
| **AC-S2-2 Core 枚举命令闭集与只读** | `source_list_scan_targets` 只在 app channel；request 恰 `{}`；result `{targets:[...]}` closed；target 字段 = `source_id/registry_id/generation/source_kind/identity_digest/project_ids`；无路径/文件名/display_name；按 `source_id` 排序唯一、`project_ids` 排序唯一；只含 `is_current=1` location 且 ≥1 非 superseded binding；≤10000/8 MiB，超限 `SOURCE_BUDGET_EXCEEDED` 不截断；缺 stack → `CORE_CAPABILITY_MISSING`；DB 错误 → `SOURCE_SYNC_STORAGE_FAILED`；**Core 业务库零写**；capability 仅 stack 组装时广播 | ① 真实 Core + 真实 v8 库：调用前后 `sources/source_locations/source_versions/source_entries/pages/page_bindings/books/chapters/regions/region_revisions/source_sync_plans/source_operations/source_binding_publications/source_revision_lineage/rendition_cache` 快照全等；② 无 location/无 binding 的 source 不出现在 targets；③ 2 book 共享源 → `project_ids` 恰为两值且有序；④ 未知字段/缺字段/重复 key/路径字符/超大 → 对应 typed 错误；⑤ 空库 → `targets: []`；⑥ capability 断言（`core.ping` 精确列表更新 `tests/core/test_core_service.py:157-164,250-258`） |
| **AC-S2-3 Host 冷启动异步枚举** | Host Ready 后异步枚举；枚举未完成不阻塞 Ready、不阻塞 Host 其他命令；枚举成功后 targets 进入 scheduler；失败 typed 降级（枚举级 code），Host 仍 Ready；重复启动幂等；首次成功枚举后异步触发一次 budget-limited tick（或按 DSH 冻结的时序）；重启后无需用户交互/无需 App 导入 | ① fake enumerator 用 `TaskCompletionSource` 卡住：`StartAsync` 先返回 Ready（`Result.IsReady=true`），枚举完成后 targets 出现；② 枚举失败（fake 注入 `SOURCE_REGISTRY_UNAVAILABLE`）→ Host Ready、status enumeration error、无异常崩溃、退避；③ 注入手动 `TimeProvider`：枚举完成后首 tick 受 budget=4/10 targets 限制（4/4/2），Ready 不被阻塞；④ 无 App 注册路径（测试不调用 `RegisterCompletedScanTargets`）仍得到 targets；⑤ 重启 HostRuntime 两次（同 DataRoot）→ 第二次仍枚举到 |
| **AC-S2-4 权威身份、合并/去重与刷新** | Core `source_id` 是唯一 target key；App 不再产生 `StableSourceId`/folder registry_id target；完成导入只触发枚举刷新；枚举为权威：按 `source_id` upsert，移除不存在的目标，未变目标保留 backoff/last 状态，不复位 budget 游标；重复枚举不增长；in-flight 扫描不被重复触发 | ① 真实 IPC：真实导入（**不是 seed**）→ 真实 Core 枚举 → target `source_id` 等于 Core DB 的 `sources.source_id`，且 **不等于** App 的 `StableSourceId(path)`；② 同一源重复导入/重复枚举 → target 数不变；③ fake enumerator 第二次返回少一个 → 该 target 从 status 消失且不再 scan；④ 枚举返回同一 target 的 path/project 变化 → 状态重置/更新且不重复；⑤ in-flight scan + refresh → 该 source 最多 1 个 `ScanSourceSync` |
| **AC-S2-5 授权与 typed 处置** | registry entry 必须存在、未撤销、generation 规则明确、路径在 root 内且非 reparse、无路径泄露；revoked → `SOURCE_GRANT_REVOKED`；missing entry → `SOURCE_ACCESS_DENIED`；Core generation > registry → typed 拒绝；registry unavailable → 枚举级 typed；不自动 re-auth | ① 纯函数/注入矩阵：`revoked`、`missing entry`、`generation equal/< />`、`root containment`、`reparse`、`locator 非路径`、`多 root 歧义` 全覆盖；② 真实 registry：`Revoke` 后枚举 → 该 target 不产生 `ScanSourceSync`，结果 `denied`/code；③ 状态/日志/异常文本不含隔离路径、`source-` grant id、`host_session`；④ 不自动调用 `source_register_root`/`Authorize` 以外的授权写；⑤ registry reset 后 → 全部 target typed denied，不崩溃、不自动重建 |
| **AC-S2-6 多项目/共享源与 scope 规则** | 1 project → `scope=current`（`project_ids=[p]`）；>1 → `scope=all` 且 `project_ids` 恰等于 Core 冻结引用集合；>20 → typed skip，不截断/不静默丢；`kind=resync` 固定；不改 `ScanSourceSync` 契约字段 | ① Python 集成：一个 source 绑定 2 books → 枚举 `project_ids` 两值；`ScanSourceSync(scope=all, project_ids=两值)` 成功且 `bases` 覆盖两项目；② Host payload 断言：单项目 current、双项目 all；③ 21 项目 → Host typed skip + 无 scan 调用；④ `scope=all` 时故意少/多一个 project → Core `SOURCE_PLAN_STALE(scope)`（真实 Core），证明集合核对有效 |
| **AC-S2-7 缺失/启动前消失与 L-G（条件 AC）** | 对“Host 启动前源已消失”的 target：用枚举 `identity_digest` 构造 `MissingObservation`（`registry_id/generation/expected_identity_digest/observed_at`），`grant_ids=[]`，Core 返回 `status=missing`，Host status=`missing`；不伪造 identity、不 tombstone/删页；**前提：S-1 的 registry 缺失 root 语义由 DSH 裁定并实现**；若未裁定，本 AC 标 BLOCKED 且 L-G 保持 | ① 真实 Core + 真实 **file-root** registry：导入后删除文件 → 重启 Host → 枚举 → 首 tick `missing`（不是 `SOURCE_REGISTRY_UNAVAILABLE`/`error`），wire `ScanSourceSync` 带 `grant_ids=[]` 与 Core 记录的 `expected_identity_digest`；② 反向 mutation：把 baseline 改成 changed 新内容 digest → Core 返回 `SOURCE_PLAN_STALE`/error，测试必须变红；③ 文件恢复后下一次 tick `ok`（file-root 恢复如涉及新 file id，按 S-1 裁定后的语义断言）；④ 若 S-1 未实现：本测试预期显式 `SOURCE_REGISTRY_UNAVAILABLE`，不得写 PASS 为 missing |
| **AC-S2-8 单飞、退避、取消、预算与时序** | 枚举单飞（重叠合并，不排队）；失败指数退避 `min(60×2^n,3600)`、成功清零；`CORE_CAPABILITY_MISSING/HOST_ONLY_REQUIRED/INVALID_REQUEST` → 禁用枚举（不暂停调度器）；Stop/Dispose 取消枚举并 join；枚举不占 scan 预算；首 tick 时序确定；零 sleep | ① fake enumerator `TaskCompletionSource` 卡住 + 并发 refresh → 仅 1 次调用；② 手动时钟：连续失败 4 次 → 60/120/240/480；成功清零；③ Stop 期间枚举挂起 → 无未观察异常、无挂起；④ 10 targets budget=4 → 枚举全部登记、tick 4/4/2；⑤ 枚举失败不影响既有 targets 的 tick；⑥ 无 `Task.Delay`/`Sleep`（代码审查 + fake clock 断言） |
| **AC-S2-9 零写、白名单、隐私、回归与证据** | 冷启动 + 首 tick 的 wire 命令集合精确 = `{OpenHostSession, RegisterSourceReadGrant, source_list_scan_targets, ScanSourceSync, core.ping}`（顺序不敏感），无 plan/preview/confirm/apply/relink/repoint/resync；Core 业务 DB 前后快照全等；Host registry 的 `last_used_at`/generation 允许变化但**不得**宣称“磁盘零写”；状态/日志无路径/grant/session/异常原文；`verify_pins` 18/18；`check.ps1` PASS；dotnet/pytest 全量不减少；0 域外 diff；无新依赖；证据在 `verification/FEA-11-SCAN-2/**` | ① 真实 IPC：wire 精确集合（逐帧解码，不容 `Contains`）；② 14 表 DB 快照前后相等；③ Host registry 文件预期变化与非预期文件零新增（区分 Core 零写与 Host 授权持久化）；④ `InMemoryLog` 断言隔离根路径/`source-`/`host_session`/异常原文零命中；⑤ `dotnet test` 全量 before/after 分列 passed/failed/skipped 并解释 skip/flaky；⑥ `pytest tests` 全量同口径；⑦ `pins.log`/`check.log`/`scope-validation.log`/`changed-files.txt` |

### 4.1 测试矩阵（最小集合）

| 层 | 用例 | 环境 | 关键断言 |
|---|---|---|---|
| Core 单元/集成 | `test_source_enumerate.py` | 真实 v8 库（内存/临时） | 资格过滤、排序/唯一、无路径、空库、超限、未知字段、零写 |
| Core 兼容 | `tests/core/test_core_service.py` | 现有 fake/assembly | capability 精确列表、`PROTOCOL_MINOR` 不变、stack 缺失不广播 |
| Host 单元 | `SourceScanSchedulerTests` + 新枚举器测试 | fake executor/enumerator + 手动时钟 | 单飞/退避/取消/预算/目标替换/状态/脱敏 |
| Host 授权矩阵 | 纯函数/接口测试 | 合成 `SourceAuthorization` | revoked/missing/generation/containment/reparse/多 root 歧义 |
| Host App 接线 | `FakeHostController` + `ImportDockViewModel` | 无 IPC | Completed 只触发刷新；Failed/Cancelled 不触发；不再传 `StableSourceId` |
| 真实 IPC（冷启动） | 新 `Fea11ScanColdStartIpcTests` 或扩展 `Fea11ScanIpcTests` | 真实 Python Core + 真实 zip/folder + 隔离 DataRoot + 新 HostRuntime 两次 | 无 App 注册仍枚举；首 tick 仅 `ScanSourceSync`；DB 零写；wire 集合 |
| 真实 IPC（缺失） | 同上（file-root registry） | 删除文件后重启 | `missing`（条件 S-1）；mutation 变红 |
| 回归 | 全量 dotnet/pytest | 仓库根 | 不减少；skip 解释 |

### 4.2 AC 与卡面草案的映射

卡面 AC-S2-1…5 保留为上位；本报告细化为 AC-S2-1…9。差异：
- 卡面 AC-S2-2 的“与会话导入合并（按 source_id 覆盖）”需按 S-2 改写为“枚举权威 + App 刷新触发”；
- 卡面 AC-S2-3 的“只枚举仍有效/未撤销的 registry/roots”需明确“Core 枚举只返回 Core 事实；Host 在注册前做 registry 授权核验并 typed skip”，不要误写成 Core 过滤授权；
- 卡面 AC-S2-4 的“枚举失败不阻塞启动”需补“首轮 budget-limited tick”的时序；
- 卡面 AC-S2-5 的“pins 18/18”需补“C-17 pin 重算、数量仍 18、独立复核”。

---

## 5. 契约 / UNFREEZE

### 5.1 是否必须

**必须。** 理由：

1. B1 需要一个新的 Core 读命令；C-17 §5.1 的 closed shape 命令表是权威（`FEA-C17_SOURCE_SYNC_DRAFT.md:209-229`），不能在实现里“顺手加”；
2. 需要一个新的 capability 以便 Host 在旧 Core 上 fail-closed，且不以 `UNKNOWN_COMMAND` 探测能力（C-17 §4 `:194-200`；M2-C1 同样禁止）；`core.ping.capabilities` 是 C-17 规定的 additive 字符串列表；
3. 需要登记新 DTO 与错误闭集（C-17 §5.2 `:231-263`、§8 `:346-381`）；即使全部复用既有错误码，也必须在 C-17 的 closed 表/命令行中登记；
4. C-17 是**已冻结 v1.0**（`doc/plan/FEA-CONTRACT-FROZEN-C17.md:11-21`；`verify_pins` C17 pin `86b89ff…`），改字节必须走 UNFREEZE 载体 + 独立复核 + 重冻 + pin 重算；不能直接改草案。

**不需要**：schema/migration、M2-C1 增量、C-16/C-15/C-06 字节、`PROTOCOL_MINOR` 提升、新错误码（建议全部复用）。

### 5.2 需要改的 C-17 字节/节

| 节 | 位置（当前行） | 建议改动 | 影响 |
|---|---|---|---|
| 文档状态/版本 | `:3`、`:10-17` | v0.1 → v1.1；候选冻结版本 v1.1；状态行/冻结链接元数据 | 元数据；须在最终复核后改，避免 pin 失效 |
| §0 版本表 | `:12-16` | 新增/更新 “C-17 v1.1 / 新命令 app 面 minor 3 / M2-C1 无增量 / schema 不变” | 版本面分离 |
| §4 命令版本、能力 | `:190-201` | `core.ping.capabilities` 增加 `source.sync.enumerate/1`；明确 **7 项 `Capabilities` DTO 不变**（`:236` 的 `Capability[恰好7]` 不能改成 8）；新增命令在 app channel | capability/兼容 |
| §5.1 命令表 | `:209-229` | 新增 `source_list_scan_targets` 行（request `{}`；result `ScanTargets`；只读；Host 内部直连，不登记 HostCommandRegistry） | 命令闭集 |
| §5.2 DTO 表 | `:231-263` | 新增 `ScanTarget` / `ScanTargets`；`project_ids` 上限 10000（注意 scan 的 `MAX_PROJECT_IDS=20` 是另一面）；`identity_digest! H`；`source_kind` 枚举 | DTO 闭集 |
| §5.3 组合守卫 | `:265-275` | 排序/唯一/资格/8 MiB/无截断/无路径/无 display_name；数据库错误映射 | 组合守卫 |
| §8 错误闭集 | `:346-381` | **建议零新增码**：复用 `INVALID_REQUEST`、`CORE_CAPABILITY_MISSING`、`SOURCE_BUDGET_EXCEEDED`、`SOURCE_SYNC_STORAGE_FAILED`；若 DSH 认为需要新码，必须只加在 C-17 表并说明 | 错误面 |
| §9 冻结清单 | `:383-398` | P3 增加新命令正/负例；P7 新 pin；P8 零 diff 口径（除 C-17/冻结记录/pin） | 复核清单 |

**不要改**：§1/§2 SQL、§3 状态机、§6 CAS/事务、§7 lineage/resolve（本卡不触碰）；`source_sync_plans`/`source_operations` 等 Schema 不变。

### 5.3 pins 与冻结记录

- C-17 是 `verify_pins.ps1` 的 **#18**（脚本 map `tools/governance/verify_pins.ps1:6-13`；冻结记录 `FEA-CONTRACT-FROZEN-C17.md:15-17` pin `86b89ff…`）。
- 改 C-17 字节 → **只更新 #18 的 pin 值**，数量仍 **18**；其他 17 个 pin 不变；`verify_pins` 必须 18/18 PASS。
- 冻结记录需新增 “§6 v1.1 UNFREEZE 重冻”表（参照 C-16 先例 `FEA-CONTRACT-FROZEN-C16.md:60-70`）：载体、语义提交、reviewed_head、Reviewer 身份/来源/session、复核字节 sha256、冻结字节 sha256、差异（只允许状态行/冻结链接元数据）、历史 pin 保留。
- `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md:39` 当前仍写 C-17 **DRAFT**（与已冻结事实矛盾）；UNFREEZE 时应一并更正为 `FROZEN v1.1`（该文件不在 18 pins 内，但属当前权威矩阵；不得留下“DRAFT vs FROZEN”双口径）。
- **独立复核**：C-17 v1.1 的复核者必须是未参与起草/返修/实现的独立上下文；报告记录 session；P0/P1=0；任何字节变动后重算/重审；`DSH` 不得用同一实现会话自审。

### 5.4 如果 DSH 不走 UNFREEZE（不推荐）

- 只靠 B2 无法覆盖升级前旧库（§2）；
- 或在 Host 里硬编码 Core SQL/直连 DB（违反 AD-002/C-15）；
- 或把命令塞进既有 `ScanSourceSync`/`GetImportReceipt`（改变冻结语义/扩大 C-16 面）。
三种都不应采纳。

---

## 6. 写域（allowed_paths 草案）与禁止项

> 以下为**建议**；最终由 DSH 在 freeze 时写入 frontmatter。**推荐拆成两个卡**（见 §8）：`FEA-11-SCAN-2-PREREQ-1`（契约）与 `FEA-11-SCAN-2`（实现）。若 DSH 坚持单卡，把两组路径合并。

### 6.1 方案 A（推荐）：契约 PREREQ 卡 + 实现卡

**`FEA-11-SCAN-2-PREREQ-1`（kind: design；契约 only）**

```yaml
allowed_paths:
  - doc/tasks/FEA-11-SCAN-2-PREREQ-1.md
  - doc/reviews/FEA-11-SCAN-2-PREREQ-1-*.md
  - doc/reviews/CONTRACT-UNFREEZE-2026-11-06.md
  - doc/handoffs/FEA-11-SCAN-2-PREREQ-1-*.md
  - verification/FEA-11-SCAN-2-PREREQ-1/**
  - doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C17.md
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
```

**`FEA-11-SCAN-2`（kind: implementation）**

```yaml
allowed_paths:
  - doc/tasks/FEA-11-SCAN-2.md
  - doc/reviews/FEA-11-SCAN-2-*.md
  - doc/handoffs/FEA-11-SCAN-2-*.md
  - verification/FEA-11-SCAN-2/**
  # Core
  - src/application/sources/enumerator.py                 # 新增
  - src/application/sources/ports.py
  - src/infrastructure/sqlite/source_sync.py
  - src/bootstrap/core_service.py
  # Host
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanStatus.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanTargetEnumerator.cs   # 新增
  - apps/desktop-avalonia/src/NewManga.Host/HostOptions.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  # S-1 被 DSH 接受时才加：
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs
  # App 身份权威切换
  - apps/desktop-avalonia/src/NewManga.App/Services/SourceImportModels.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ImportDockViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs   # 仅在 bookId 接线需要时
  # Tests
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanSchedulerTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11ScanIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11ScanColdStartTests.cs        # 新增
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Support/Fea11Scan2Fixture.cs      # 新增（如需）
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs
  - tests/fea11/test_source_enumerate.py                 # 新增
  - tests/fea11/test_source_command_parity.py            # 仅当登记 Host binding 时
  - tests/core/test_core_service.py                      # capability 精确列表
```

### 6.2 方案 B（单卡）

把 `FEA-11-SCAN-2-PREREQ-1` 的 7 条契约/审查/证据路径并入 `FEA-11-SCAN-2`；其余同方案 A。**代价**：契约字节与实现字节同一 allowed_paths、同一 base_commit，实现 Reviewer 的 reviewed_head 会包含契约改动；若契约复核返修，实现 base 要重定。**不推荐**，除非 DSH 要最小卡数。

### 6.3 明确禁止

- `src/application/sources/scanner.py`、`service.py`、`matcher.py`、`model.py`（除非 DSH 明确批准一个纯校验器改动；优先放在新 `enumerator.py`）；
- `src/infrastructure/sqlite/schema.py`、`migrator.py`、`library.py`（含 `refresh_source_location_auth` 接线）、`src/application/importing/**`（C-16 receipt 不改）；
- `apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs`、`RunContracts.cs`、`doc/plan/FEA-C07_API_INVENTORY.md`；
- C-16/C-15/C-06/C-09/C-14/C-04b/M2-C1/ADJ-001/FEA-01 任何字节；`verify_pins.ps1`；除 C-17 外的 17 个 pin；
- Host 直连 Core DB；任何第二套 Book/Page 库/持久目标索引；自动 plan/apply/删除/GC/重新授权；
- `FileSystemWatcher`/hint/事件队列；UI/通知/设置项/扫描结果持久化；新依赖；
- 真实用户数据/AppData/外部卷/回收站；push；真实数据写入；删除/放宽测试制造通过；自审。

---

## 7. 风险 / limitation

| # | 风险/限制 | 证据 | 影响 | 处置建议 |
|---|---|---|---|---|
| **S-1（P1，阻塞 missing AC）** | 生产 file-root registry + `Load()` 逐 root 重验身份 → 文件删除/替换使**整个 registry** `SOURCE_REGISTRY_UNAVAILABLE` | `SourceAccessRegistry.cs:119-128,132-138`；`SourceSecurity.cs:86-118`；生产注册 `SourceImportModels.cs:214-223,805-816`；SCAN-1 fixture 用父目录 root `Fea11ScanIpcTests.cs:49-59` | 冷启动“启动前缺失→missing”不可达；甚至同一 registry 的其他源也被拖死；SCAN-1 的 missing 证据只覆盖 fixture 形状 | **DSH 裁决**：① 解释 C-15 §5（`FEA-C15_SOURCE_STORAGE_DRAFT.md:312`）把“缺失 root”视为 unreadable 而非 corrupt，窄修 Host Load（仅影响缺失，身份变更仍 fail-closed），需独立安全复核；或② 接受 AC 降级为 `SOURCE_REGISTRY_UNAVAILABLE`、L-G 保持；或③ 另立 registry-resilience 缺陷卡先修 |
| **S-2（P1，必须修）** | App 注册的 `source_id` 不是 Core `source_id`；C-16 receipt 不含 `source_id` | `SourceImportModels.cs:786,920-924`；`runtime.py:470`；`runtime.py:70-82,289-305`；C-16 `:127-139`；IPC 测试用 seed id `Fea11ScanIpcTests.cs:33,74` | SCAN-1 生产 in-session 目标也会失败；SCAN-2 若沿用会重复同一错误 | SCAN-2 以 Core 枚举为唯一权威；App 只触发刷新；加“真实导入→枚举→target”判别测试（AC-S2-4） |
| **S-3（P2）** | registry `identity_facts` 字段存在但从不写入 | `SourceAccessRegistry.cs:10,49`；C-15 规范 `:296-304` | 不能依赖 registry 做内容身份比对 | B1 使用 Core `identity_digest`；不扩 registry 字段；在卡内注明 |
| **S-4（P2）** | `refresh_source_location_auth` 是死代码；撤销/重注册后 Core location 的 registry/generation 不更新 | `library.py:2293-2310`（无调用者，grep 仅定义）；`runtime.py:457-471` 复用 source 不刷新 location auth | 用户 revoke→re-register/reset 后，Core 仍指向旧 registry_id；冷启动枚举 target 被 Host typed 拒绝，且**只读切片无法恢复**（scan 零写；apply 需先 scan，循环） | 登记 L（撤销后需重新导入+另卡修 import auth 刷新）；本卡 Out；不要宣称“撤销后可恢复扫描” |
| **S-5（P2）** | C-17 冻结矩阵仍写 DRAFT | `FEA-CONTRACT_FREEZE_MATRIX.md:39` vs `FEA-CONTRACT-FROZEN-C17.md:3` | 治理双口径 | UNFREEZE 时一并更正；不新增 pin |
| **S-6（P2）** | 新增 capability 会打破 `core.ping` 精确列表测试 | `tests/core/test_core_service.py:157-164,250-258` | 必须同步测试，否则全量 pytest 变红 | allowed_paths 列入；只新增一行 capability；不得删测试/放宽 |
| **S-7（P2）** | `Capabilities` DTO 冻结为**恰好 7**项 | C-17 `:236` | 若把新 capability 加进该 DTO → 破坏冻结 shape | 新 capability 只进 `core.ping.capabilities`；7 项 DTO 不变；C-17 v1.1 明写 |
| **S-8（P2）** | 大库/8 MiB/10000 targets 未标定；>20 books/source 无法 `scope=all` | C-17 `:207`（8 MiB）、`:269`（20）；`model.py:37-38` | 大库枚举 typed 失败；共享源 >20 项目跳过 | 本卡记录测量（不设 SLA）；>20 typed skip；L-E/L-F |
| **S-9（P3）** | `SourceScanStatus` 为 positional record；新增枚举字段会改构造器 | `SourceScanStatus.cs:12-30,33-43`；`HostRuntime.cs:90-91`；测试 `SourceScanSchedulerTests.cs:775` | SCAN-1 测试需同步 | 只加一个可空子记录 + 更新 `Disabled`/`Snapshot`；不改变 `last_result` 六值 |
| **S-10（P3）** | 真实 IPC/重启测试重、opt-in；可能 flaky | SCAN-1 先例 `Fea11ScanIpcTests.cs:431-440`；全量 flaky 记录 | 不能以 fixture 代替生产形状 | 用 `NEWMANGA_FEA11_SCAN2_IPC=1` opt-in；证据如实分列 skip/flaky；不得写 PASS 未跑项 |
| **L-A** | 冷启动无目标 | SCAN-1 `:222` | 本卡目标 | B1 枚举 + 首 tick 后关闭（旧 Core 无 capability 时仍保留） |
| **L-G** | 首次 ok 前缺失 fail-closed | SCAN-1 `:228` | 本卡目标，**条件 S-1** | 用枚举 `identity_digest`；S-1 未接受则保持 |
| **L-B/L-C/L-D/L-E/L-F** | watcher 缺、状态不持久、无 UI、成本未标定、共享源 bases 单项目 | SCAN-1 `:222-228` | 本卡不解决 L-B/L-C/L-D；L-E 记录；L-F 由 scope=all 关闭 | 不宣称 AC11-1 全绿 |
| **AC11-1** | 仍 PARTIAL（watcher 半边） | `FEA-11.md:103,238` | 本卡 done 后仍 PARTIAL | 卡/Handoff/STATUS 明写；不得回填 MET |
| **L10** | referenced 图源/rendition 缺口 | `FEA-11-LINEAGE-1.md:136` | 本卡不触碰 pipeline/rendition | Out；不得以扫描切片宣称 L10 解决 |
| **Host 授权持久化** | 扫描 tick 会写 registry `last_used_at`/generation | `SourceAccessRegistry.cs:70-72,82-85`；`SourceReadCoordinator.cs:59` | 不能宣称“磁盘零写” | AC-S2-9 分开断言：Core 业务 DB 零写；Host registry 允许授权写；日志/状态仍脱敏 |
| **性能/启动预算** | 枚举查询/首 tick 可能放大启动 IO | 未实测 | 大库用户体验 | 异步 + 单飞 + budget-limited 首 tick；记录测量；保留 L-E |

---

## 8. 裁决与 DSH 下一步

### 8.1 裁决

```
SCAN-2-SCOPE: READY-WITH-UNFREEZE
```

- **B1 可行**：Core 已拥有全部业务事实（source_id/source_kind/registry_id/generation/identity facts/project_ids），Host 持久 registry 已存在且可恢复；只缺一个只读枚举命令与其契约登记。
- **B2 不推荐**：无法覆盖升级前旧库，且会形成 Core 业务事实的第二份副本；只有在 B1 被独立证明不可行且明确非权威缓存时才考虑。
- **UNFREEZE 必须**：C-17 v1.1（命令 + capability + DTO + 错误闭集 + §9 清单）；pin #18 重算，仍 18；M2-C1/C-16/C-15/C-06 零增量；无 schema。
- **条件**：S-1 的 registry 缺失 root 语义必须先由 DSH 裁决；否则 AC-S2-7（启动前缺失→missing）标 BLOCKED，L-G 保持，本卡仍可交付其余 B1 能力。S-2 必须在本卡修正（权威 `source_id`）。

### 8.2 DSH 下一步动作清单（建议顺序）

1. **落盘本报告**：把本文件作为 `doc/reviews/FEA-11-SCAN-2-scope-r1.md` 提交（写域已在本卡 `doc/reviews/FEA-11-SCAN-2-*.md`）；记录 Reviewer 身份/来源/session；逐项登记 findings 处置（S-1…S-10）。
2. **先裁决 S-1/S-2**（scope freeze 前）：
   - S-1：接受“缺失 root = unreadable，不 poison 整库”的 C-15 §5 解释 + Host 窄修（并安排独立安全复核），或接受 AC-S2-7 降级（L-G 保持），或先立 registry-resilience 缺陷卡；三选一并写入卡。
   - S-2：确认“Core 枚举 `source_id` 为唯一权威；App 注册改为刷新触发；不再使用 `StableSourceId`/folder registry_id 作为 target id”。
3. **治理登记**：把 SCAN-2 加入 `REBASELINE_PLAN` 当前 DAG（现在只有叙述行 `:54`，无表行）；STATUS 指向；READY 节点只在 scope 冻结后设置；不重写冻结历史。
4. **契约（推荐独立 PREREQ 卡）**：新建 `FEA-11-SCAN-2-PREREQ-1`（kind: design）→ 写 C-17 v1.1 → UNFREEZE 载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-06.md` → 独立上下文复核（不是契约作者/实现者）→ 重冻（三指纹/冻结记录/§6 v1.1）→ `verify_pins` 18/18 → `check.ps1` PASS → 更正 freeze matrix `:39`。
5. **冻结实现卡**：`FEA-11-SCAN-2` 改 `kind: implementation`；写入 §3 In/Out、§4 AC-S2-1…9、§6 allowed_paths、base_commit（重冻后的 main head）、branch/worktree（DSH 在 workspace 创建）、Owner、上下文独立 Reviewer；`evidence_dir` 显式在 allowed_paths。
6. **释放与实施**：Owner 认领 → 实现（Core 枚举 + Host 枚举器/合并/授权 + App 刷新触发 + 测试）→ 固定 delivery head → Handoff/EV/Resource Manifest → 独立实现 Review → 返修复审 → DSH 集成验证 → closeout。
7. **不释放 WATCH-1**：只核边界；不同时放 watcher；不把 `FileSystemWatcher` 带进 SCAN-2 diff。
8. **口径**：SCAN-2 done 后 **AC11-1 仍 PARTIAL**（watcher 缺）；L10 不解决；L-A 关闭（旧 Core 无 capability 时降级并记录）；L-G 仅在 S-1 被接受时关闭。

### 8.3 是否需要“先拆实现承接卡”

- **推荐拆**：先 `FEA-11-SCAN-2-PREREQ-1`（契约 only），再 `FEA-11-SCAN-2`（实现）。理由：契约字节需要独立复核与重冻；实现 Reviewer 的 reviewed_head 不应包含未冻契约；契约返修不应重定实现 base；这符合 `FEA-11-PREREQ-1 → FEA-11` 与 `FEA-12-PREREQ-1 → FEA-12-CORE` 的先例。
- 若 DSH 坚持单卡：把 §6.2 的契约路径并入 `FEA-11-SCAN-2`，但在卡内设**硬阶段门**：UNFREEZE→独立复核→重冻→pins→check 完成后才允许 `src/**`/`apps/**` 实现提交；契约复核者与实现复核者必须是不同独立上下文。代价是 base_commit 与 review 链更复杂。

---

## 9. 摘要（最后一段）

本次独立 scope review 的结论是 **`SCAN-2-SCOPE: READY-WITH-UNFREEZE`**：B1 在事实层面可行——Core 的 `sources`/`source_locations`/`page_bindings`/`source_versions` 已持有 `source_id`、`source_kind`、`registry_id`、`generation`、identity facts 与 `project_ids`，Host 的 DPAPI registry 也已持久化 `registry_id/generation/revoked/roots/locator`，两者只缺一个“Core 只读枚举命令 + C-17 v1.1 登记”；不需要 schema/migration，不需要 M2-C1/C-16/C-15/C-06 增量，pin #18 重算后仍为 18。B2 因无法覆盖升级前旧库、会复制 Core 业务事实且仍需对账，不推荐。与此同时，本 review 发现两个必须在冻结前由 DSH 裁决的问题：**S-1** 生产 file-root registry 在源文件被删除/替换时会整库 `SOURCE_REGISTRY_UNAVAILABLE`，使“启动前缺失→missing”AC 不可达（SCAN-1 的 missing 证据只覆盖父目录 root fixture）；**S-2** App 用 `StableSourceId`/folder `registry_id` 注册目标，而 Core 新源的真实 `source_id` 是 `src-<uuid>` 且 C-16 receipt 不返回它，SCAN-1 的生产注册路径未经真实 Core 判别（唯一真实 IPC 用的是 seed id）。因此本卡必须以 Core 枚举为唯一身份权威、废弃 App 推导并用“真实导入→枚举→target”判别测试锁死；若 DSH 不接受 S-1 的 registry 缺失语义解释，则 AC-S2-7 应降级为 typed `SOURCE_REGISTRY_UNAVAILABLE` 并保留 L-G，不得把未实现写成 PASS。建议 DSH 先落盘本报告、处置 findings、登记 DAG，然后走“契约 PREREQ（C-17 v1.1 UNFREEZE/独立复核/重冻/pins）→ 实现卡冻结 → 释放”的顺序；WATCH-1 不同时释放，AC11-1 在 SCAN-2 完成后仍为 PARTIAL。


## DSH 处置（Lead，2026-11-06）

- **B1 采纳**（Core 业务目标事实 + Host 持久 registry 核验授权/取 locator/铸新会话 grant；Core 业务真值与 Host 授权真值分离；不建第二套 Book/Page 库）。**B2 不推荐/不采纳**。
- **S-1 取选项②**：生产 file-root 缺失/替换 → typed `SOURCE_REGISTRY_UNAVAILABLE` 视为 fail-closed；**不得**声称"启动前缺失 → missing"；实现卡 AC 该场景降级 typed，L-G 保留；registry resilience 另立后续缺陷卡（本轮不做）。
- **S-2 采纳**：Core 枚举 `source_id`（src-<uuid>）为唯一权威；App 不得用 `StableSourceId`/folder `registry_id` 冒充；实现卡必须含"真实导入 → 枚举 → target.id == Core `sources.source_id`"判别测试。
- **S-4 登记 limitation**：`refresh_source_location_auth` 死代码（撤销/重注册后 Core location auth 不更新），只读切片无法恢复；登记 L-S4。
- **流程**：先建 `FEA-11-SCAN-2-PREREQ-1`（C-17 v1.1 UNFREEZE → 独立 byte-level 复核 → 重冻 → pins 18/18）；再冻结/释放 `FEA-11-SCAN-2` 实现卡；WATCH-1 不同时释放。
- 备注：scope review 原文见 `G:\CODEX\New Manga.workspace\FEA-11\scope-review\FEA-11-SCAN-2-scope-r1.md`；本处置不改写 reviewer 原文。
