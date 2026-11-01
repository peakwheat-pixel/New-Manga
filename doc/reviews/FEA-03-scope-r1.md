---
document_id: FEA-03-scope-r1
kind: independent_scope_review
reviewer: fea03-scope-reviewer
reviewer_kind: subagent
reviewer_source: "DSH Agent Teams durable teammate `fea03-scope-reviewer`（role=reviewer，context=fresh，由 Team Lead `lead` 以独立上下文派发；未使用独立 CLI session ID，子任务标识 = teammate target 名 + 本报告 frontmatter；未参与 FEA-03 的起草、范围冻结或实现）"
reviewer_independent: true
reviewed_by_implementer: false
author: dsh
base_commit: 106299b50
reviewed_head: 106299b50
reviewed_head_full: 106299b50f0d04c57d52765893ec9c69bf0ef2e5
repository: G:/CODEX/New Manga
scope: "FEA-03 范围冻结（写域、R-DRAFT/R-JOURNAL/R-TOKEN/R-CAND/R-APPLY/R-LOCK/R-STYLE/R-DIGEST/R-LEGACY、AC1–AC14、V1–V12、L-1/L-2/L-5 判定、禁止范围、治理指针）；不构成实现验收（实现尚未开始）"
decision: changes_requested
verdict: changes_requested
p0_count: 1
p1_count: 7
p2_count: 11
checkps1: "Governance check: PASS (2 warnings)，EXIT=0（2 warnings = 11 个非终态 Task + STATUS 达预算 80%）"
verifypins: "PIN AUDIT: PASS (all 15)，EXIT=0；C13 = d2cb8de4dd79…"
captured_at: 2026-11-01T23:05:44+08:00
captured_by: fea03-scope-reviewer
---

# Review：FEA-03 范围冻结（base/reviewed_head = `106299b50`）

**结论：`changes_requested`（P0 × 1 / P1 × 7 / P2 × 11）。**

本报告**只审范围冻结材料**，不评价实现（实现尚未开始），不构成实现验收。即使后续复核改为 `approved`，也不等于 Task 完成：仍需实现、CORE/BRIDGE 切片验收、独立实现复核、集成与 AC 证据闭环。

判定口径（本报告使用）：

- **P0** = 范围冻结条款与冻结契约/授权直接冲突，或按现文无法在不越权前提下实现，必须重写条款；
- **P1** = 必须在 `ready` 前补齐的覆盖、可验证性、写域或 L 判定缺陷（不补齐则实现/复核口径不可判定）；
- **P2** = 一致性、精度与证据卫生改进，不单独阻断 `ready`。

---

## 0. 复核对象、方法与环境

**被审材料（全部在 `106299b50`）**

1. [`doc/tasks/FEA-03.md`](../tasks/FEA-03.md)（范围冻结卡：写域、R-DRAFT…R-LEGACY、AC1–AC14、V1–V12、L 判定、禁止范围）
2. [`doc/checkpoints/GOAL-PROGRESS-2026-11-01.md`](../checkpoints/GOAL-PROGRESS-2026-11-01.md)（Q-1…Q-5 裁决与释放依据）
3. [`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md`](../plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md)（**FROZEN v5**，pin `d2cb8de4…`，SC-D01…SC-D12）与 [`doc/plan/FEA-CONTRACT-FROZEN-C13.md`](../plan/FEA-CONTRACT-FROZEN-C13.md)（冻结记录、实现铁律、已知限制）
4. 相邻契约冻结记录：[C-01b](../plan/FEA-CONTRACT-FROZEN-C01b.md)、[C-04b](../plan/FEA-CONTRACT-FROZEN-C04b.md)、[C-05](../plan/FEA-CONTRACT-FROZEN-C05.md)、[C-08](../plan/FEA-CONTRACT-FROZEN-C08.md)
5. 方案 [`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md`](../design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md) §12.1 `:641`、§15.6 `:923`、§15.7 `:950`、§5.1 状态表 `:237`
6. [`doc/plan/FEA-C11_IMPL_PREREQS.md`](../plan/FEA-C11_IMPL_PREREQS.md)（L-1/L-2/L-5 登记）、[`doc/plan/FEA-00A_PREP.md`](../plan/FEA-00A_PREP.md)（`:129` 的 L-2 触发判断）
7. 只读源码事实：`src/application/editing/{errors,ports,region_canvas,service}.py`、`src/domain/regions/entities.py`、`src/infrastructure/sqlite/{schema,regions}.py`、`src/bootstrap/{core_assembly,core_service}.py`、`apps/desktop-avalonia/src/NewManga.ApplicationCore/**`、`NewManga.Host/{HostRuntime,HostOptions,DataSafety,Coexistence,SingleInstance}.cs`、`NewManga.CoreClient/CoreServiceClient.cs`
8. 相邻冻结契约语义对照：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md`（v1.5 **FROZEN**）、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` §5/§8
9. 治理指针：`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

**环境与只读证据**

- `git rev-parse HEAD` = `106299b50f0d04c57d52765893ec9c69bf0ef2e5`；`git status --porcelain` 为空（main，clean）。
- 释放/冻结提交 `106299b50` 只改 5 个治理文档：`doc/tasks/FEA-03.md`、`doc/checkpoints/GOAL-PROGRESS-2026-11-01.md`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`；未触契约字节、未触源码。
- `pwsh -NoProfile -File tools/governance/check.ps1` → `PASS (2 warnings)`，EXIT=0。
- `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → `PIN AUDIT: PASS (all 15)`，EXIT=0（含 C13 `d2cb8de4dd79…`）。
- 复核期间未修改任何被审文件；未 commit/push；只新增本报告。

**未执行**（按纪律显式声明）

- 未运行 `pytest` / `dotnet test`：范围冻结阶段无实现可测；AC13 的基线命令本身正是本报告指出需补的项（P2-07）。
- 未实测 journal 崩溃/并发/原子性：无实现，只做规格审查（第 2 项给出机制层面的判断依据）。
- 未逐字节重审 C-04b/C-08 正文：本卡不改二者，只读其冻结记录与交叉引用（范围声明见 §12）。

---

## 1. 契约覆盖：SC-D01…SC-D12 是否有对应规则/AC

| 契约条款 | 卡内承载 | 判定 | 缺口 |
|---|---|---|---|
| SC-D01 11 字段 | R-DRAFT-1 `:61`、AC1 `:87`、V1 `:116` | 完整 | V1 未断言“主画布与浮窗共享同一 `DraftId`”（见 P1-06） |
| SC-D02 落盘节奏/flush/UI 提示 | R-DRAFT-2/3 `:62-63`、AC2 `:88`、V2 `:117` | **部分** | C-13 `:51` 的“在 UI 提示”无承载、无 deferral；5 个强制 flush 触发点无对应 V（P1-05/P1-06） |
| SC-D03 draft owner | R-DRAFT-4 `:64`、AC3 `:89`、V3 `:118` | **部分** | C-13 `:62` 允许 geometry/style 按域合并，卡内无对应断言；V3 只测跨 Session 只读/转移（P1-05） |
| SC-D04 edit token 幂等 | R-TOKEN-1 `:72`、AC4 `:90`、V4/V5 `:119-120` | **部分** | 缺 **commit receipt**（方案 §12.1 `:641` 明列交付项）；journal 字段 `:67` 无 `tokenId`/`committedRevisionId`，SC-D04 的幂等无跨重启承载（P1-03） |
| SC-D05 journal 持久检查点 | R-JOURNAL-1/2 `:67-68`、AC5 `:91`、V6 `:121` | 完整（方向） | 原子性断言机制与 fsync/temp 残留未定义（P1-02/P2-08） |
| SC-D06 活跃草稿登记 | R-JOURNAL-2/3 `:68-69`、AC6 `:92`、V7 `:122` | **部分** | “收到 `edit-open`/序号更新后登记 active 草稿”、Session 结束清理、孤儿 `discarded` 只有规则（R-JOURNAL-3），无 AC/V；AC6 只覆盖 candidate-only，V7 未测翻译产物路径（P1-05） |
| SC-D07 RegionCandidate | R-CAND-1 `:73`、AC6 `:92`、V7 `:122` | 完整 | 另：候选存储/生命周期未定义（P2-06） |
| SC-D08 统一事务 apply | R-APPLY-1 `:74`、AC7 `:93`、V8 `:123` | 完整 | 可复用既有 `commit_region_batch`（见 §4）；卡未点明（P2-11） |
| SC-D09 三锁 × 三域 | R-LOCK-1 `:77`、AC8 `:94`、V9 `:124` | 完整 | — |
| SC-D10 6 键白名单 | R-STYLE-1 `:78`、AC9 `:95`、V10 `:125` | **部分** | C-13 `:139` 要求拒绝时“列出该键名”，AC9 未断言（P1-05） |
| SC-D11 旧路径不破坏 | R-LEGACY-1/2 `:82-83`、AC11 `:97`、V12 `:127` | **不成立（P0）** | 去重机制不可判定，且与 `V11R_REGION_WRITE_CONTRACT` 冻结的 append-only 语义冲突（P0-01） |
| SC-D12 protectionDigest | R-DIGEST-1 `:79`、AC10 `:96`、V11 `:126` | **部分** | “manual 位”在 `manual_edited` 与 `text.translation_locked` 之间歧义（P1-05） |

**核对证据（只读）**

- C-13 `SC-D01` 11 字段与卡 R-DRAFT-1 逐字段一致；`SC-D10` 的 6 键与 `src/domain/regions/entities.py:204-212` 完全一致（`font_family`/`font_size`/`text_color`/`stroke_color`/`stroke_width`/`auto_font_size_enabled`）。
- `SC-D07` 的 `origin` 取值域与 `src/infrastructure/sqlite/schema.py:256-257` 的 CHECK 一致；`regions`/`region_revisions` 表与触发器位于 `schema.py:224-249` / `:251-271` / `:275-281`，与 C-13 引用一致。
- `SC-D12` 的真实歧义来源：`RegionText.manual_edited` 与 `RegionText.translation_locked` 是两个独立位（`entities.py:138-139`），`save_manual_translation` 同时置位（`entities.py:172-178`），但 `unlock_translation` 只清后者（`entities.py:187-189`）；C-13 `:173` 引用的 `editing/service.py:128-129` 实际读的是 `region.translation_locked or region.text.translation_locked`（`service.py:119-133`）。卡 R-DIGEST-1 只写“`text_json` 的 manual 位”，实现者可以选错位。

---

## 2. Q-2 文件 journal 方案核查

**满足项（方向正确）**

- SC-D05 的三要素都有落点：持久检查点（R-JOURNAL-1 `:67`）、与 revision 表分离（R-JOURNAL-2 `:68`）、重启恢复为 `active` 且不自动提交（R-JOURNAL-2 `:68`）、损坏丢弃不阻塞启动（R-JOURNAL-2 `:68`）；AC5/V6 覆盖崩溃恢复与损坏两个场景（`:91`/`:121`）。
- 不新增 schema 表、不改 `schema.py`/migrations，与 Q-2 裁决（`GOAL-PROGRESS-2026-11-01.md:30`）一致；对应 L-1 的规避理由成立（但见 §5 的 `PageBindingVersion` 例外）。
- `os.replace` 的方向可用：同卷 NTFS 上替换是原子的，写 temp → rename 的主路径不会暴露半写 JSON。
- R-JOURNAL-3 的“孤儿草稿 `discarded` + Session 结束清理”与 SC-D06 `:90` 一致（但无 AC，见 P1-05）。

**未写清/不可执行项**

1. **`<data-root>/drafts/` 由谁决定、是否在写域内**：数据根解析在 `src/bootstrap/core_service.py:5714-5715`（`NEWMANGA_DATA_ROOT`）与 `src/bootstrap/core_assembly.py:935-941`（`default_data_root()`），两处均**不在**卡的 `allowed_paths`（`:22-37`）；`src/infrastructure/filesystem/**` 也未授权（该目录已存在：`managed_storage.py` 等）。按现文，实现要么把文件 I/O 塞进 `src/infrastructure/sqlite/**`（语义错位），要么改未授权文件（越权）。→ P1-01
2. **与 Host 只读/数据根策略的关系**：Host 在 `ReadOnlyUntilParity` / 旧壳运行 / 自检失败时按 `DataRootPolicy`（`DataSafety.cs:15-24`）拒绝一切用户数据写（`HostRuntime.cs:228-235`、`:455-463`）；而 journal 是 Core 内自动写 data-root 的旁路，卡未定义只读模式下是否还落盘、由谁拦、失败语义是什么。卡的“不动用户数据”（`:133`）与“向 data-root 写 `<DraftId>.json`”也未调和（新建 app-owned 目录是否允许、只创建自己的文件、绝不改写既有文件）。→ P1-02
3. **并发写同一 `DraftId` 的锁策略**：R-DRAFT-4 只到“同 Session 单串行 patch 队列 + 跨 Session 只读/转移”（进程内语义）。Q-2 的依据“跨 Session 一致性由 Core 内单写者保证”只在 checkpoint（`:30`），**未进入卡**；多进程（第二实例/旧壳并存）下没有文件锁、单写者声明或“拒绝第二写者”的行为。→ P1-02
4. **“原子写足以覆盖崩溃”不完整**：卡只写 temp + `os.replace`。`os.replace` 不保证内容持久性（未要求 temp 文件 `fsync` / FlushFileBuffers），掉电可能留下旧 journal 或零长 temp；崩溃残留的 `*.tmp` 需要 journal 扫描时忽略/清理，卡未写恢复口径（“最近一次成功 flush 之前的内容可丢”是否可接受）。→ P1-02（P2-08 补充断言机制）
5. **flush 失败时 `status=conflicted` 的持久性**：R-DRAFT-3 `:63` 要求磁盘满时不丢内存缓冲并置 `conflicted`；此时 journal 写不进去，重启后该状态不可恢复（只能按旧 journal 恢复为 `active`）。卡未说明这是可接受语义（内存态丢失、UI 提示）还是需要额外落点。→ 并入 P1-05 的“提示/状态承载”缺口。

**结论**：文件 journal 方案本身可行，但**路径所有权、只读策略、单写者/并发、持久性口径**四项属于“崩溃恢复契约”的实质部分，必须进入卡面并可被 V 断言，否则 AC5 只覆盖顺利路径。

---

## 3. Q-3 两切片核查

**CORE 侧**

- AC1–AC11 基本都落在 CORE（Python 写域），且 AC7 可复用既有事务 seam：`ports.py:83` 的 `commit_region_batch` 已实现“同一 `BEGIN IMMEDIATE`、逐 Region `expected_current_checks`、任一冲突整批回滚”，SQLite 实现在 `src/infrastructure/sqlite/regions.py:288-…`（`:313` 为 `BEGIN IMMEDIATE`）。→ CORE 的 AC 边界大体可独立判定。
- 但 AC2/AC3/AC10 缺对应 V 行（P1-06），CORE 的“独立验收”缺少完整的机械清单；AC13 回归基线未列（P2-07）。

**BRIDGE 侧（主要问题）**

- 卡 AC12 `:98` 写“C# 侧草稿缓冲与 **Core 协议对接**（共享 DraftId、串行 patch 队列、flush 触发）”。这与写域/禁止范围冲突：
  - `allowed_paths` 只给 `apps/desktop-avalonia/src/NewManga.ApplicationCore/**` 与对应测试（`:32-33`）；禁止范围 `:132` 明确“不改 `apps/**` 其它面（仅 `NewManga.ApplicationCore` 与对应测试）”。
  - `NewManga.ApplicationCore` 的现状是**纯 .NET 内存层，无 Host/IPC/CoreClient 依赖**（`NewManga.ApplicationCore/README.md:3`）；Core 侧的命令分发/错误码在 `src/bootstrap/core_service.py:392-425`，C# 侧 wire 在 `NewManga.CoreClient`/`NewManga.Host`。任何“协议对接”都要触这些未授权文件；若新增 Core 命令，还要改 M2-C1 §5 command catalog（`M2-C1_TYPED_IPC_CONTRACT.md:143-184`）与 §3.2 版本规则（`:120-134`），属 wire 契约修订，卡未授权。
  - 因此 AC12 要么退化为“本地缓冲 + 不接线（仅定义 injectable seam）”（如 FEA-02-CORE 的“本 Task 不接入 Current”先例），要么需要新增写域与 wire 授权；现文两头都不成立。→ P1-04
- **BRIDGE 写域准确性**：`apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/` 真实存在（`IntentCoordinatorTests.cs` 等），因此“ApplicationCore + 对应测试项目”对**本地缓冲**是准确的；对“协议对接”不准确（缺 `NewManga.CoreClient`、`NewManga.Host`、`src/bootstrap/core_service.py`）。→ P1-04
- **独立判定与“诚实状态”**：Q-3（`GOAL-PROGRESS-2026-11-01.md:31`）只规定“CORE 先通过测试，BRIDGE 不得阻塞 CORE 独立验收”；卡内没有定义 CORE 完成而 BRIDGE 未完成时 Task 处于什么状态（`in_progress`？`blocked`？能否只交付 CORE 并在 Handoff 记录 BRIDGE 未接线？AC14 的实现复核是一次还是分两次？）。→ P1-04
- AC12 在 V 矩阵中**没有任何 V 行**（`:116-127`），BRIDGE 完全不可机械验收。→ P1-06（与 P1-04 同源）

---

## 4. 写域完整性

| AC/规则 | 需要改哪里 | 是否在 `allowed_paths` | 判定 |
|---|---|---|---|
| AC7 统一事务 apply | `src/application/editing/`（apply use case）+ `src/infrastructure/sqlite/`（复用/扩展 `commit_region_batch`，`regions.py:288`） | 是（`:29`、`:31`） | 覆盖（但路径条目语法见 P2-01） |
| AC4 新错误码 `EDIT_TOKEN_EXPIRED` | `src/application/editing/errors.py` | 是 | 覆盖；但若进 wire 则需 `core_service.py`（未授权）→ 见 P1-07 |
| AC9 `STYLE_KEY_NOT_ALLOWED` | 同上 | 是 | 覆盖 |
| AC7 `STALE_BASE_REVISION` | 同上 | 是 | 覆盖 |
| R-JOURNAL data-root 解析/注入 | `src/bootstrap/core_assembly.py:935-941`、`src/bootstrap/core_service.py:5714-5715` | **否** | 缺口 → P1-01 |
| journal 文件适配器 | 自然落点 `src/infrastructure/filesystem/**`（已存在） | **否** | 缺口 → P1-01 |
| Draft 领域实体 | 自然落点 `src/domain/{drafts,editing}/**` | **否**（仅 `src/domain/regions/**`） | 缺口 → P1-01 |
| BRIDGE 协议对接 | `NewManga.CoreClient`、`NewManga.Host`、`src/bootstrap/core_service.py`、M2-C1 | **否** | 缺口 → P1-04 |
| 回归测试（若触 wire） | `tests/core/**` | **否**（仅 `tests/{editing,domain,infrastructure}`） | 缺口 → P1-04/P2-07 |
| L-1 依据 `PageBindingVersion` | 若读 `page_bindings` → 四表 DDL 未冻且 **schema 中不存在** | — | 缺口 → P1-01/§5 |

**证据**

- 卡 `allowed_paths`：`doc/tasks/FEA-03.md:22-37`；其中 `:31` 与 `:33` 两条含全角中文括号注解（`src/infrastructure/sqlite/**（除 schema.py 与 migrations/）`、`apps/desktop-avalonia/tests/**（仅 ApplicationCore 草稿缓冲相关）`），**不是合法 glob**，无法机械执行；先例 `FEA-00A-IMPL-1.md:21-35` 全部为纯 glob，约束写正文。→ P2-01
- 反向先例：`FEA-00A-IMPL-1.md:31` 在需要装配接线时明确把 `src/bootstrap/core_assembly.py` 写入 `allowed_paths`；本卡缺同款授权。→ P1-01
- `src/infrastructure/filesystem/` 已存在（`managed_storage.py`、`bounded_log_store.py` 等），journal 文件适配器有自然落点但未授权。→ P1-01
- “AC 要求改但写域不允许”的共 5 项（上述 data-root、journal 适配器、draft 领域路径、BRIDGE 协议面、wire 测试）；“写域允许但 AC 不要求”的只有 `src/domain/regions/**`（draft 实体未必该放这里）与 `doc/checkpoints/**`，不构成额外问题。

---

## 5. L-1 / L-2 / L-5 判定

### L-1（四表 DDL）

- 卡判 **NOT_APPLICABLE**（`:106`），理由“文件 journal，不触 `source_entries`/`page_bindings`/`source_sync_plans`/`source_operations`”。
- 核查：四表在 `src/infrastructure/sqlite/schema.py` 中**没有任何 DDL**（`CREATE TABLE` 清单无这四张；空结果）；`FEA-C14` 冻结记录 `§5` 明说四表表结构未被任何契约冻结（`doc/plan/FEA-CONTRACT-FROZEN-C14.md:64`）。`FEA-C11_IMPL_PREREQS.md:24` 确实把 FEA-03 列为 L-1 的候选 Task 之一。
- **但** SC-D01 的 `PageBindingVersion`（C-13 `:38`）被定义为“与 C-01b 的 `page_bindings` 一致”，而该表当前不存在于 schema。卡 R-DRAFT-1（`:61`）只重复字段名，没有写该值的**来源与语义**（由 Session/Host 不透明注入？读 `page_bindings`？）。若实现选择读表，则 L-1 **不成立**且按 C-11 必须 `blocked`；若选择注入，则需在卡内明写“不读四表、值为调用方提供的不透明乐观版本号”。
- 再触发条件（`:106`“若需新增表/列/索引或迁移 → blocked”）本身可执行，但没有覆盖“读四表”这一情形。→ **P1-01**

### L-2（M2-C1 字节修订）

- 卡判 **NOT_APPLICABLE**（`:107`），理由“新错误码仅 Core 内部结构化返回；不新增 wire 码、不改 `allowedRunErrorCodes` 白名单”。
- 核查：
  - `src/application/editing/errors.py:32-45` 只有 `GuardStatus`（含 `LOCK_CHANGED`），全仓 `src/**` 对 `EDIT_TOKEN_EXPIRED`/`STYLE_KEY_NOT_ALLOWED`/`STALE_BASE_REVISION` **0 命中**；三码只出现在卡与 C-13 正文。→ “新码尚不存在”事实成立。
  - `allowedRunErrorCodes` 在 `src/**` 与 `apps/**` **0 命中**，只出现在 `doc/**`（C-08 冻结记录 §3、C-11 前置登记等，共 10 处（8 个文件））→ 卡把它当作既有白名单来“不改”，与代码事实不符（它是 C-08 前置(b) 的**未落地计划项**）。
  - 真正决定 L-2 是否触发的是“错误码会不会出 Core”。M2-C1 §8 的 `ErrorEnvelope` 仍是 **PROPOSAL**，允许未知 code 原样透传（`M2-C1_TYPED_IPC_CONTRACT.md:1097-1109`）：从“wire 字节”角度，新 code 不一定需要 M2-C1 字节修订；但卡自己在 `:107` 把“暴露到 Host/IPC wire”定义为触发 `blocked` 的条件——而 AC12 的 BRIDGE“与 Core 协议对接”几乎必然要把 apply/token 失败面带到 C#。二者不能同时成立。
  - `FEA-00A_PREP.md:129` 已登记过同一判断：“L-2 若引入 **draft ACK 错误码/白名单** → 触发”；方案 §15.6 的 FEA-03 可观察出口也含 “draft ACK”（`:923`）。卡既没有 draft ACK 的 AC，也没有说明它属于哪一层。→ **P1-07**
- 再触发条件的**字面**是可执行的（blocked + 先做 M2-C1），但它与 AC12 冲突，需在修 AC12 时一并改写。

### L-5（整库恢复锁）

- 卡判 **NOT_APPLICABLE**（`:108`）：不触备份/恢复/维护互斥。核查属实（卡无备份/恢复条目；方案 §15.6 把 FEA-13 作为备份/恢复的 Task）。
- 再触发条件（`:108`）可执行。→ 成立。

---

## 6. AC 可验证性与 V1–V12 覆盖

**AC ↔ V 映射**

| AC | 对应 V | 判定 |
|---|---|---|
| AC1（11 字段、序号、共享 DraftId） | V1 | 部分：V1 未含“主画布+浮窗共享同一 DraftId” |
| AC2（防抖值、5 个强制 flush 点、失败语义） | V2 | 部分：V2 只注入失败；防抖值与 5 个触发点无断言 |
| AC3（同 Session 串行队列、跨 Session、文本冲突） | V3 | 部分：V3 只覆盖跨 Session 只读/转移 |
| AC4（token 幂等/过期） | V4+V5 | 完整 |
| AC5（崩溃恢复/损坏/原子写） | V6 | 部分：原子写如何断言未定义（P2-08） |
| AC6（candidate-only） | V7 | 完整（但 SC-D06 的登记/清理无 V，P1-05） |
| AC7（统一事务） | V8 | 完整 |
| AC8（三锁 × 三域） | V9 | 完整 |
| AC9（白名单） | V10 | 部分：未断言错误列出违规键名 |
| AC10（digest/manual 位） | V11 | 部分：manual 位歧义、各保护位变体未列（P1-05） |
| AC11（旧路径兼容） | V12 | **不可判定**（P0-01） |
| AC12（BRIDGE） | **无** | 不可判定（P1-04/P1-06） |
| AC13（回归） | 无（过程项） | “outcome 对照（修前/修后/判定/理由）”不是机械断言；基线文件/命令未列（P2-07） |
| AC14（独立复核） | 无（过程项） | 可执行（文件+decision），但 reviewer 元数据与本次派发不一致（P2-02） |

**不可机械否证的措辞（需要改成可断言的断言）**

- AC2 `:88` “错误可诊断（SC-D02）”——未定义断言对象（错误类型/码/日志/UI 文案）。
- AC2/V2 “防抖间隔实测后冻结”——未定义测量方法、样本与证据形式（C-13 冻结记录 `§6 L-3` 也把它留给 FEA-03 实测）。
- AC13 `:99` “既有 editing/regions/sqlite 相关测试 outcome 对照”——未列测试文件、命令与基线计数；且真实落点跨 `tests/editing`、`tests/core`（如 `tests/core/test_region_write_commands.py`、`test_region_batch_locking.py`），而 `tests/core/**` 不在写域。
- AC12 `:98` “与 Core 协议对接”——无接口形状、无错误面、无 V。
- AC5 `:91` “原子写（temp+rename）断言”——未定义崩溃注入点（写 temp 前/后、rename 前/后）与 fsync/临时文件清理口径。

→ **P1-06**（覆盖与可判定性），其中 AC11 的具体机制问题见 P0-01。

---

## 7. 边界与禁止范围

**已明确且可执行**

- 不改 `schema.py`/migrations：禁止范围 `:131` + L-1 行 `:106`（但 `:131` 的排除写法依赖 `:31` 的非 glob 注解，见 P2-01）。
- 不改冻结契约字节（15 份 pin）：`:131`；`verify_pins.ps1` 实测 15/15 PASS。
- 不新增 wire 码/白名单：`:131`（但与 AC12 冲突，见 P1-07）。
- 不改 `apps/**` 其它面（仅 `NewManga.ApplicationCore` 与对应测试）：`:132`（但与 AC12 冲突，见 P1-04）。
- 不动用户数据、不 push、不合并 main：`:133`；不顺手修 FEA-04/07/10/12、不释放其它 Task：`:134`；不降低既有测试断言：`:135`。
- 不改 C-04b：来源 `:46` 提到“本卡不改”，SC-D12 的边界也在 C-13 `:183-186`。

**不足**

1. 禁止范围 `:129-135` 没有把 **C-04b（删除保护）** 与 **C-08（PreparedRun / candidate store）** 列为“不触”；二者只出现在“来源”与 R-CAND-1 的区分说明里。建议在禁止范围显式加两条，避免实现者顺手改 C-04b 的删除 preflight 或复用 `step_result_candidates`/C-08 candidate store。→ P2-03
2. “不动用户数据”与 journal 写 `<data-root>/drafts/` 的关系未定义（app-owned 新文件 vs 用户数据只读策略）。→ P1-02
3. R-LEGACY-2 的过渡期判据（`:83`）：①“全仓无调用方直接走旧保存路径”可执行但没给精确命令/基线（`rg` 会命中 wire handler、tests、service 自身）；②“新路径写入点清单与 UI 实际写入点一一对应”需要 UI 落地（FEA-04/06），**在 FEA-03 内不可执行**；③独立复核可执行。判据整体要标注“②由后续 UI Task 提供证据，FEA-03 只登记清单”。→ P2-04

---

## 8. 治理指针与检查器

**一致性核查（`106299b50`）**

| 指针 | 值 | 行号 | 判定 |
|---|---|---|---|
| `doc/STATUS.md` 当前 Task | `[FEA-03](tasks/FEA-03.md) proposed` | `:7` | 与 PLAN/LEDGER 一致（均 proposed） |
| `doc/REBASELINE_PLAN.md` DAG 行 | `FEA-03 … proposed（范围冻结 v1；待上下文独立复核 r1 → ready 交 Codex）` | `:15` | 一致 |
| `doc/REBASELINE_PLAN.md` 当前 DAG 摘要 | `FEA-03（proposed，范围冻结待复核）` | `:29` | 一致 |
| `doc/TASK_LEDGER.md` | `FEA-03` / `proposed` / `own row` | `:46` | 一致 |
| `GOAL-PROGRESS` 头部 | HEAD `419d75bbb`、当前 Task `FEA-C11-PREREQ-1 in_progress` | `:5-6` | 写入时快照（早于释放提交），与 `reviewed_head` 不同属正常历史；但若作为 Q-1 授权证据，建议在复核处置记录中注明“释放提交 = `106299b50`” |

**检查器实测**

- `check.ps1` → `PASS (2 warnings)`，EXIT=0。2 warnings = 11 个非终态 Task（不能证明活性，r38）+ STATUS 达预算 80%（3091 bytes / 31 lines）。
- `verify_pins.ps1` → `PIN AUDIT: PASS (all 15)`，EXIT=0；C13 pin = `d2cb8de4dd79fb…`，与卡 `:46` 的 `d2cb8de4…` 和冻结记录 `§1` 一致。
- **检查器覆盖边界**（实测 grep）：`tools/governance/check.ps1` 对 `allowed_paths`/`reviewer`/`approval`/`depends_on`/`base_commit` **0 处校验**（只校验 status、DAG 成员、evidence、AC 标记、00_INDEX 指针、预算等）。因此本报告的 P2-01（非法 glob）与 P2-02（reviewer 字段）在 `check.ps1 PASS` 下依然存在，不能拿 PASS 当语义证据。

**本次发现的实际漂移**

1. `doc/STATUS.md:11` 仍写“下一候选：`FEA-03`（草稿与保护协调，依赖本卡已满足）”，与 `:7` 的“当前 Task = FEA-03”自相矛盾；释放提交 `106299b50` 只改了 `:7`，没有清理 `:11`。→ P2-10（建议随 r1 处置一并修正为真实下一候选或删除）。
2. `doc/REBASELINE_PLAN.md:10` 把 `FEA-C11-PREREQ-1` 写成 `in_progress`，而 `doc/TASK_LEDGER.md:39` 是 `approved`，卡文件本身也是 `status: approved`（`doc/tasks/FEA-C11-PREREQ-1.md:4`）。→ P2-10（非本卡引入，但属同一治理口径；`check.ps1` 未发现）。
3. `FEA-03` 自身三指针一致且均为 `proposed`，满足“范围冻结待复核”的状态要求。

---

## 9. 可执行性判断

**按现文，Codex 不能直接开工。** CORE 的大部分 AC 有可落地写域（AC7 还能复用既有事务 seam），但下列问题会迫使实现者要么越权，要么自行发明口径：

1. AC11 的“旧路径+去重键”与冻结的 C073 append-only 语义冲突，且去重键/内容摘要/base 语义/与 AC7 的优先级都未定义（P0-01）——这是实现 CORE 时无法绕开的第一问题；
2. journal 的数据根来源、文件适配器落点、Draft 领域模块路径不在写域（P1-01）；
3. journal 的只读策略、单写者/并发、持久性口径未定义（P1-02）；
4. token 幂等的跨重启承载（commit receipt）缺失（P1-03）；
5. BRIDGE 的协议面对写域/禁止范围矛盾，且没有独立验收口径（P1-04）；
6. SC-D06 登记/清理、SC-D02 UI 提示、SC-D10 键名等契约条款没有 AC/V（P1-05）；
7. V 矩阵覆盖不完整，AC2/AC12/AC13 不可机械判定（P1-06）；
8. L-2 的 N/A 与 BRIDGE 错误面冲突（P1-07）。

**建议补齐顺序（全部完成后才可 `ready`）**

1. 先裁决 AC11 机制：在 `(a)` “旧路径保持 C073 append-only，新路径仅对‘同一 base 的回放’返回既有 revision；旧→新/新→旧两种顺序的期望固定下来”与 `(b)` “走 `CONTRACT-UNFREEZE` 改 C073 语义”之间选一；配套定义“内容摘要”canonical（字段集、排序、数值/文本归一化）与 AC7 的 stale 拒绝优先级；补 V 行（旧→新、新→旧、同 token 重放、崩溃后重放）。→ 解 P0-01/P1-03 的一部分。
2. 在 CORE 规则中加 **commit receipt**（持久化落点：journal 同目录或 journal 内字段；含 `tokenId`/`DraftId`/`DraftSequence`/`revisionId`/`committedAt`），并明确幂等的重启边界；补 AC/V。→ 解 P1-03。
3. 明确 journal 的宿主边界：写域（`src/bootstrap/core_assembly.py` 接线 + `src/infrastructure/filesystem/**` 或等价落点）、数据根来源与只读模式行为、单写者/单实例不变量、fsync/temp 残留/并发 flush 口径；补 AC/V。→ 解 P1-01/P1-02。
4. 二选一处理 BRIDGE：或收窄 AC12 为“ApplicationCore 本地缓冲 + 可注入 seam（不接线）”，并声明 wire 接线与错误映射由后续 Task 承担；或补授权（写域 + M2-C1 修订 + L-2 处理）并定义 CORE/BRIDGE 独立验收与 Task 停靠状态。同步决定 AC12 的 V 行。→ 解 P1-04/P1-07。
5. 补 SC-D02/D06/D10/D12 的 AC/V（UI 提示 deferral、活跃草稿登记/Session 清理/孤儿 discarded、错误列出键名、manual 位唯一化），补齐 AC1/AC2/AC3/AC10 的 V 行与 AC2/AC5/AC13 的机械断言。→ 解 P1-05/P1-06。
6. 修正 `allowed_paths` 为纯 glob（注解移入正文），补 reviewer 字段/`reviewer_kind`/来源，清理 STATUS/PLAN 指针漂移，补禁止范围的 C-04b/C-08 两条。→ 解 P2-01/P2-02/P2-03/P2-10。
7. 重新提交范围冻结卡（新 head）→ 重跑本复核（可基于 diff 复审）。

---

## 10. Findings

| 编号 | 级别 | 位置 | 问题 | 建议 | 状态 |
|---|---|---|---|---|---|
| P0-01 | P0 | `doc/tasks/FEA-03.md:82`（R-LEGACY-1）、`:97`（AC11）、`:127`（V12）；对照 `doc/contracts/V11R_REGION_WRITE_CONTRACT.md:146-150`、`:233`、`src/application/editing/service.py:1244` | AC11 要求“旧路径与新路径先后写同一内容 → 只 1 个 revision；去重键 `(RegionId, BaseRevisionId, 内容摘要)`；旧路径不得双写”。严格按字面实现会改动 C073 `save_manual_translation` 的冻结语义（append-only、非幂等、不静默去重，且 `service.py:1244` 明写“同文两次保存产生两个 revision”）；若只做“旧→新”方向，则 SC-D11 的“无论走新 token 还是旧路径都以去重键判幂等”未覆盖。另外“内容摘要”的 canonical 定义、`BaseRevisionId` 在去重键中的比较语义（旧路径写入后 current 已移动）、以及“stale base 但内容命中”时 AC7 的 `STALE_BASE_REVISION` 拒绝与 AC11 去重的优先级都未定义 → AC11 不可机械判定，并有与冻结契约冲突风险 | 二选一并写入卡面：(a) 旧路径语义不变，仅新路径对“同一 base 的回放”返回既有 revision，明确两种顺序的期望与“内容摘要”canonical；(b) 走 `CONTRACT-UNFREEZE` 改 C073。无论哪种，补 V 行（旧→新、新→旧、token 重放、崩溃后重放）并写明与 AC7 的优先级 | open |
| P1-01 | P1 | `doc/tasks/FEA-03.md:22-37`（allowed_paths）、`:55`、`:61`、`:67`、`:106`；`src/bootstrap/core_service.py:5714-5715`、`src/bootstrap/core_assembly.py:935-941`、`src/infrastructure/filesystem/`（存在） | journal 的 `<data-root>` 解析/注入点在 `src/bootstrap/**`（未授权）；journal 文件适配器自然落点 `src/infrastructure/filesystem/**`（未授权）；Draft 领域实体只有 `src/domain/regions/**` 可用；L-1 判 N/A 但 `PageBindingVersion` 的来源未定义，而 `page_bindings` 表在 schema 中不存在（四表 DDL 未冻）→ 实现要么越权，要么自造数据根/模块路径 | 补授权：`src/bootstrap/core_assembly.py`（接线）、`src/bootstrap/core_service.py`（仅 data-root 注入，如需要）；`src/infrastructure/filesystem/**`（journal 适配器）或明确放 `src/application/editing/` 的理由；`src/domain/{drafts,editing}/**` 或明确 draft 实体归属；在 R-DRAFT-1 写清 `PageBindingVersion` 为调用方注入的不透明版本号、不读四表 | open |
| P1-02 | P1 | `doc/tasks/FEA-03.md:67-69`、`:91`、`:133`；`apps/desktop-avalonia/src/NewManga.Host/DataSafety.cs:15-24`、`HostRuntime.cs:228-235`、`Coexistence.cs:28-50`；`GOAL-PROGRESS-2026-11-01.md:30` | journal 写 `<data-root>/drafts/` 与 Host 只读策略（`ReadOnlyUntilParity`/旧壳/自检失败时拒绝一切用户数据写）的关系未定义；与“不动用户数据”未调和；多进程/第二写者的单写者不变量只在 checkpoint（未入卡），无文件锁/拒绝策略；`os.replace` 未含 fsync/掉电持久性口径与崩溃残留 `*.tmp` 的恢复/清理规则；多 Session 并发 flush 同一 DraftId 的串行化未断言 | 在 R-JOURNAL 增加“journal 目录为 app-owned、只新建/替换自己的文件”声明；写明只读模式下 journal 的行为（拒绝/内存态/专用只读根）；写“同一 data-root 仅一个 Core 写者，Host 全局单实例保证；第二写者 fail-closed”；定义掉电可丢窗口与 temp 残留清理；补 V 行（并发 flush 串行、只读模式、掉电窗口） | open |
| P1-03 | P1 | `doc/tasks/FEA-03.md:44`（来源引 §12.1 含 commit receipt）、`:67`、`:72`、`:90`；`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md:641`；`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:74` | 方案 §12.1 明列 FEA-03 交付 **commit receipt**，卡内没有任何 R/AC/V 承载；journal 字段无 `tokenId`/committed revision；SC-D04 的“同 `(DraftId, DraftSequence)` 重复提交返回同一 revisionId”在 Core 重启后就无法满足（无持久 receipt），AC4/V4 只测单会话 | 增加 commit receipt 规则与持久落点（journal 同目录或 journal 字段），明确幂等的会话/重启边界，补 AC/V（重启后用同一 token 重放 → 同 `revisionId`、无第二个 revision；不同内容同 token → 拒绝） | open |
| P1-04 | P1 | `doc/tasks/FEA-03.md:98`（AC12）、`:32-33`（allowed_paths）、`:131-132`（禁止范围）；`apps/desktop-avalonia/src/NewManga.ApplicationCore/README.md:3`；`src/bootstrap/core_service.py:392-425`；`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:120-134`、`:143-184`；`GOAL-PROGRESS-2026-11-01.md:31` | AC12 写“与 Core 协议对接”，但 (a) `ApplicationCore` 现状无 Host/IPC/CoreClient 依赖；(b) 协议面写域（`NewManga.CoreClient`、`NewManga.Host`、`src/bootstrap/core_service.py`、M2-C1 command catalog）不在授权内且被禁止范围排除；(c) AC12 无 V 行；(d) CORE 完成而 BRIDGE 未完成时 Task 的状态、独立验收与是否可分段交付未定义 | 二选一：(a) 收窄 AC12 为“ApplicationCore 本地缓冲 + injectable seam，不接线”，声明 wire/错误映射由后续 Task 承担并给 V 行；(b) 补写域 + wire 契约授权（M2-C1 minor、L-2 处置）并定义两切片独立验收/停靠状态 | open |
| P1-05 | P1 | `doc/tasks/FEA-03.md:79`、`:88`、`:92`、`:95`、`:96`；`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:51`、`:62`、`:88-90`、`:139`、`:173`、`:181`；`src/domain/regions/entities.py:138-139`、`:172-189` | 契约条款覆盖缺口：① SC-D02 的“flush 失败在 UI 提示”无承载/无 deferral（写域无 UI）；② SC-D06 的活跃草稿登记 + Session 结束清理 + 孤儿 `discarded` 只有 R-JOURNAL-3 规则，无 AC/V，AC6 只测 candidate-only、V7 未测“翻译产物先成为 candidate”；③ SC-D03 允许 geometry/style 按域合并，卡未断言；④ SC-D10 要求拒绝时列出违规键名，AC9 未断言；⑤ SC-D12 的“manual 位”在 `RegionText.manual_edited` 与 `RegionText.translation_locked` 之间歧义，C-13 `:173` 引用的 `service.py:128-129` 指向后者而语义更接近前者 | 逐条补 AC/V：UI 提示明确 deferral 与承接 Task；登记/清理加 V（edit-open 登记 active、Session 结束无残留、孤儿 `discarded`）；geometry/style 域合并加断言或明示 deferral；AC9 加“错误含键名”；R-DIGEST-1 明确 manual 位唯一（建议 `manual_edited`，并同步 C-13 的实现铁律口径，必要时走 UNFREEZE 澄清） | open |
| P1-06 | P1 | `doc/tasks/FEA-03.md:87-100`（AC）、`:116-127`（V）、`:99`（AC13） | V1–V12 未覆盖全部 AC：AC1 的共享 DraftId、AC2 的防抖值与 5 个强制 flush 点、AC3 的同 Session 串行队列、AC10 的各保护位变体、AC12 全部、AC13/AC14 过程项均无 V（或只有部分）；AC2“错误可诊断”、AC13“outcome 对照”、AC5“原子写断言”不是机械断言 | 为每条 AC 至少给一行可执行 V（含命令/断言对象）；把 AC2 的防抖值改为“实现 Task 记录测量方法+证据、值写入 Handoff 并由复核确认”；AC13 列基线测试文件/命令/计数；AC5 写明崩溃注入点与期望 | open |
| P1-07 | P1 | `doc/tasks/FEA-03.md:107`（L-2）、`:98`（AC12）；`doc/plan/FEA-00A_PREP.md:129`；`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md:154`、`doc/plan/FEA-CONTRACT-FROZEN-C08.md:45` | L-2 判 N/A 的两处依据不稳固：① `allowedRunErrorCodes` 在 `src/**`/`apps/**` 0 命中（只存在于 doc，是 C-08 前置(b) 的未落地计划项），卡把它当作既有白名单；② 卡把“新错误码暴露到 Host/IPC wire”定义为 `blocked`，而 AC12 的 BRIDGE 几乎必然要把 apply/token 失败面带到 C#；③ `FEA-00A_PREP.md:129` 已把“draft ACK 错误码/白名单”列为 L-2 触发条件，方案 §15.6 出口也含 draft ACK，卡未处理 | 在修 AC12 时同时二选一：(a) 声明 BRIDGE 不新增/不透传新码（映射到既有 `INVALID_REQUEST`/`INPUT_REVISION_CHANGED`/`UNKNOWN`），则 L-2 N/A 可保留并把该映射写入 AC；(b) 若需透传，则按 L-2 先 blocked 并走 M2-C1 独立修订。同时更正 `allowedRunErrorCodes` 的“现状”表述 | open |
| P2-01 | P2 | `doc/tasks/FEA-03.md:31`、`:33`；先例 `doc/tasks/FEA-00A-IMPL-1.md:21-35` | `allowed_paths` 两条含全角中文括号注解（`src/infrastructure/sqlite/**（除 schema.py 与 migrations/）`、`apps/desktop-avalonia/tests/**（仅 ApplicationCore 草稿缓冲相关）`），非合法 glob，写域边界不可机械执行；`check.ps1` 也不校验 allowed_paths | 改为纯 glob（如 `src/infrastructure/sqlite/**` + 正文写“除 schema.py 与 migrations/”），并把 tests 限定写进正文/交付边界 | open |
| P2-02 | P2 | `doc/tasks/FEA-03.md:10`（reviewer）、`:100`（AC14） | `reviewer: c01b-reviewer` 与本次实际派发的 `fea03-scope-reviewer` 不一致；AC14 只写报告路径，未写 `reviewer_kind`/来源/Appointment 记录 | r1 处置后回填实际 reviewer 与来源（本报告 frontmatter 已给），并在 AC14 补“Review Appointment 记录”项 | open |
| P2-03 | P2 | `doc/tasks/FEA-03.md:129-135`、`:46` | 禁止范围未显式列“不触 C-04b（删除保护）/C-08（PreparedRun、candidate store）”；二者仅在来源与 R-CAND-1 区分说明中出现；journal 目录的 app-owned 属性未声明 | 在禁止范围加两条“不触 C-04b/C-08”；在 R-JOURNAL-1 声明 journal 目录为 app 自有、不读取/改写用户既有文件 | open |
| P2-04 | P2 | `doc/tasks/FEA-03.md:83`（R-LEGACY-2） | 过渡期判据 ②“新路径写入点清单与 UI 实际写入点一一对应”在 FEA-03 内不可执行（UI 属 FEA-04/06）；①缺精确 `rg` 命令与基线（会命中 wire handler、tests、service 自身） | 标注 ② 由 UI Task 提供证据、FEA-03 只登记清单；① 给出精确命令与排除项 | open |
| P2-05 | P2 | `doc/tasks/FEA-03.md:62`（R-DRAFT-2）、`:88`（AC2）；`doc/plan/FEA-CONTRACT-FROZEN-C13.md:70` | “具体值由本卡用真实输入实测后冻结”措辞不当（范围冻结卡不实测）；防抖值的测量方法、样本、证据形式未定义（C-13 已知限制 L-3 明确留给 FEA-03 实测） | 改为“由实现 Task 实测并写入 Handoff，复核确认”；写明测量方法（输入事件间隔/分位值/证据文件） | open |
| P2-06 | P2 | `doc/tasks/FEA-03.md:73`（R-CAND-1） | `RegionCandidate` 的存储与生命周期未定义：内存（按 Core 会话）还是文件 journal？prepare 与 apply 跨命令/跨重启如何找回？不得新增 schema 表（L-1）已定，但落点未写 | 明确候选仅内存、随会话/apply 失效，或定义文件落点；补一条跨命令/重启的行为断言或显式限制 | open |
| P2-07 | P2 | `doc/tasks/FEA-03.md:99`（AC13）、`:34-36`（allowed tests） | 回归基线未列具体测试文件/命令；真实相关测试跨 `tests/editing`（7 文件）与 `tests/core`（`test_region_write_commands.py`、`test_region_batch_locking.py` 等），而 `tests/core/**` 不在写域；`tests/domain` 目前不存在（新建需说明） | 列基线清单与命令（`python -m pytest tests/editing tests/infrastructure …`）；若需触 `tests/core`，补写域或声明由 wire Task 承担 | open |
| P2-08 | P2 | `doc/tasks/FEA-03.md:91`（AC5） | “原子写（temp+rename）断言”不可执行：未定义崩溃注入点（temp 写入前/后、rename 前/后）、fsync/掉电模型、temp 残留清理 | 写明注入点与期望（如：rename 前崩溃 → 旧 journal 完整可读；rename 后崩溃 → 新 journal 完整；`*.tmp` 不被当作草稿） | open |
| P2-09 | P2 | `doc/tasks/FEA-03.md:44`、`:98` | 方案 §12.1/§15.6 的交付项到卡内规则的映射未写全：“保护 epoch”是否等同 SC-D12 digest、“draft ACK”归属、 “独立 patch undo 与 revision restore”中 restore 已由既有 C045 承载、undo 只剩 `undoCursor` 字段——均未声明 | 补一张“交付项 → 卡内条款/AC/后续 Task”映射表，避免实现或复核时争议范围 | open |
| P2-10 | P2 | `doc/STATUS.md:7`、`:11`；`doc/REBASELINE_PLAN.md:10`；`doc/TASK_LEDGER.md:39` | STATUS 内部矛盾：`:7` 当前 Task = FEA-03，`:11` 又写“下一候选：FEA-03”；PLAN 把 `FEA-C11-PREREQ-1` 写成 in_progress，而 LEDGER（`:39`）与卡文件均为 approved；`check.ps1` 不校验这些 | 修正 STATUS `:11` 与 PLAN `:10`（或注明漂移原因）；本卡 r1 处置时同步 | open |
| P2-11 | P2 | `doc/tasks/FEA-03.md:93`（AC7） | 卡未指出可复用既有 `commit_region_batch`（`src/application/editing/ports.py:83`、`src/infrastructure/sqlite/regions.py:288`，已含 `BEGIN IMMEDIATE` + `expected_current_checks` 整批回滚），实现者可能重复造事务 seam 或绕过既有约束 | 在 R-APPLY-1/AC7 注明显式复用或扩展该 seam，禁止另开写路径 | open |

---

## 11. 验证记录（实际执行）

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| HEAD 与工作区 | `git rev-parse HEAD`；`git status --porcelain` | `106299b50`，main | PASS（clean） | `106299b50f0d04c57d52765893ec9c69bf0ef2e5`；空输出 |
| 释放提交范围 | `git show --stat 106299b50`；`git show --name-only 106299b50` | `106299b50` | PASS | 仅 5 个 `doc/**` 文件；未触契约/源码 |
| 治理检查器 | `pwsh -NoProfile -File tools/governance/check.ps1` | `106299b50` | PASS（2 warnings） | `Governance check: PASS (2 warnings)` |
| 契约 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `106299b50` | PASS | `PIN AUDIT: PASS (all 15)`；C13 `d2cb8de4dd79` |
| Core 无 draft/journal 概念 | grep 正则 `draft` 与 `journal`（大小写不敏感）over `src/**/*.py` | `106299b50` | PASS（`draft` 0；`journal` 仅 6 处 SQLite WAL/-journal 相关） | `src/infrastructure/sqlite/{connection,upgrade_legacy_layout}.py` 等 |
| 新错误码现状 | grep 三个新码字面量 `EDIT_TOKEN_EXPIRED`、`STYLE_KEY_NOT_ALLOWED`、`STALE_BASE_REVISION`（全仓） | `106299b50` | PASS（`src/**` 0；仅卡与 C-13/review 正文） | `src/application/editing/errors.py:32-45` 只有 `GuardStatus` |
| `allowedRunErrorCodes` 现状 | grep `allowedRunErrorCodes`（`src`/`apps`/`doc`） | `106299b50` | PASS（`src/**`、`apps/**` 0；仅 doc 10 处（8 个文件）） | C-08 冻结记录 `:45`、C-11 前置 `:25` 等 |
| 四表 DDL 现状 | grep `page_bindings`、`source_sync_plans`、`source_operations`；列出 `schema.py` 的 `CREATE TABLE` | `106299b50` | 四表 0 命中（不存在） | `src/infrastructure/sqlite/schema.py`；C-14 冻结记录 `:64` |
| TextStyle 6 键 | 读 `src/domain/regions/entities.py:204-212` | `106299b50` | 与 SC-D10 一致 | 6 个 snake_case 字段 |
| origin CHECK / 三锁列 | 读 `schema.py:224-249`、`:251-271`、`:256-257` | `106299b50` | 与 C-13/C-01b 一致 | `origin IN ('machine','user','imported','restored')` |
| RegionLockSnapshot | 读 `src/application/editing/ports.py:56-63` | `106299b50` | 与 C-13 `:181` 引用一致（只含三锁） | — |
| 旧保存路径 append-only | 读 `src/application/editing/service.py:1232-1258`（docstring `:1244`）；`doc/contracts/V11R_REGION_WRITE_CONTRACT.md:146-150`、`:233` | `106299b50` | 与 AC11 字面冲突 | V11R 契约 v1.5 FROZEN（`:3`） |
| apply 可复用事务 seam | 读 `ports.py:83`、`src/infrastructure/sqlite/regions.py:288`、`:313` | `106299b50` | 可行 | 同一 `BEGIN IMMEDIATE` + `expected_current_checks` |
| data-root 解析点 | 读 `src/bootstrap/core_service.py:5714-5715`、`core_assembly.py:935-941` | `106299b50` | 均在未授权写域 | — |
| Host 只读策略 | 读 `DataSafety.cs:15-24`、`HostRuntime.cs:228-235`、`Coexistence.cs:28-50`、`HostOptions.cs:60-66` | `106299b50` | 只读模式拒绝用户数据写 | — |
| ApplicationCore 现状 | 读 `NewManga.ApplicationCore/{README.md,*.cs}` | `106299b50` | 纯 .NET 内存层，无 IPC/Host 依赖 | `README.md:3` |
| 检查器覆盖边界 | grep `allowed_paths`、`reviewer`、`approval`、`depends_on`、`base_commit` in `tools/governance/check.ps1` | `106299b50` | 0 命中（不校验） | — |
| 指针一致性 | 读 `STATUS.md:7`/`:11`、`REBASELINE_PLAN.md:10`/`:15`/`:29`、`TASK_LEDGER.md:39`/`:46` | `106299b50` | FEA-03 三指针一致；另发现 STATUS/PLAN 漂移（P2-10） | — |
| 运行 pytest / dotnet test | — | — | **NOT_RUN** | 无实现可测；AC13 基线命令本身待补（P2-07） |
| 崩溃/并发/原子性实测 | — | — | **NOT_RUN** | 无实现；本报告只审规格 |
| C-04b/C-08 正文逐字节复核 | — | — | **NOT_RUN** | 非本卡写域；只读冻结记录与交叉引用 |

---

## 12. 边界声明、结论与复审

**边界声明**

- 本 Review **只审范围冻结**（被审 head `106299b50`），不评价实现、不构成实现验收，也不构成 Task 释放或集成结论。
- 本 Review 不修改任何被审文件（卡/STATUS/PLAN/LEDGER/契约/源码），未 commit、未 push；只新增本报告。
- 本 Review 未逐字节复核 C-04b/C-08/C-01b/C-05 正文，只核对其冻结记录与卡内交叉引用；未访问用户数据。
- `check.ps1 PASS` 与 `verify_pins.ps1 PASS` 是机械检查结果，不能替代契约语义或范围判定（本报告已给出两处 PASS 下仍存在的实际缺陷）。

**结论**

**`changes_requested`（P0 × 1 / P1 × 7 / P2 × 11）。**

范围冻结的整体骨架（C-13 条款映射、写域意识、L 前置判定、V 矩阵、禁止范围、治理登记）质量较高，CORE 侧大部分 AC 有明确落点，AC7 还能复用既有的整批事务 seam。但当前版本有 1 个 **P0**（AC11 的旧路径去重与 C073 冻结语义冲突、且去重机制不可判定）与 7 个 **P1**（写域不全、journal 宿主/只读/并发边界、commit receipt 缺失、BRIDGE 范围矛盾、SC-D02/D06/D10/D12 覆盖缺口、V 矩阵不覆盖全部 AC、L-2 与 BRIDGE 错误面冲突），按 §9 顺序修订并重新提交后，方可进入 `ready` 并派 Codex。

**复审口径**

- 修订后以新 head 提交范围冻结卡；本报告的 P0/P1 需逐条 disposition（fixed/deferred with owner/not applicable + 理由），复审可基于 diff 进行，但必须重新确认三条指针与 `check.ps1`/`verify_pins.ps1` 结果。
- 实现复核（AC14 的 `doc/reviews/FEA-03-r1.md`）不在本报告范围；届时需按本报告 §9 的验收口径检查 CORE/BRIDGE 的独立证据。

---

*Reviewer：`fea03-scope-reviewer`（DSH Agent Teams durable teammate，fresh 独立上下文，由 Team Lead `lead` 派发；未参与 FEA-03 的起草/实现/范围冻结）。日期：2026-11-01。*
