---
id: FEA-03
title: FEA-03 草稿与保护协调（draft journal / edit token + receipt / candidate-only / 统一 apply / 锁白名单 / protectionDigest）
kind: implementation
governance_version: 3
status: proposed
approval: dsh_ruling_2026-11-01_GOAL_Q1_Q3
suggested_owner: codex
owner: codex
reviewer: fea03-scope-reviewer
depends_on:
  - FEA-00A-IMPL-1
  - FEA-01-FREEZE-1
base_commit: 106299b50
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
review_appointment: "doc/reviews/FEA-03-scope-r1.md（reviewer fea03-scope-reviewer，DSH fresh 独立上下文派发）"
evidence_dir: verification/FEA-03
allowed_paths:
  - doc/tasks/FEA-03.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/**
  - doc/handoffs/FEA-03-*.md
  - src/application/editing/**
  - src/domain/regions/**
  - src/domain/drafts/**
  - src/infrastructure/sqlite/**
  - src/infrastructure/filesystem/**
  - src/bootstrap/core_assembly.py
  - src/bootstrap/core_service.py
  - apps/desktop-avalonia/src/NewManga.ApplicationCore/**
  - apps/desktop-avalonia/tests/**
  - tests/editing/**
  - tests/domain/**
  - tests/infrastructure/**
  - tests/core/test_region_write_commands.py
  - tests/core/test_region_batch_locking.py
  - verification/FEA-03/**
---

# FEA-03 草稿与保护协调（范围冻结 v2，待独立复核）

## 来源与授权

1. 方案 §12.1 `:641`（交付 Core draft journal / edit token / **commit receipt** / 保护 epoch / 应用草稿缓冲）；§15.6 `:923`（写域、L2 高风险、出口 draft ACK / 单 owner / 独立 patch undo 与 revision restore）。
2. **契约**：[C-13 冻结 v5](../plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md)（pin `d2cb8de4…`，SC-D01…SC-D12）；[C-01b](../plan/FEA-CONTRACT-FROZEN-C01b.md)（表/三锁/复合 FK）；[C-04b](../plan/FEA-CONTRACT-FROZEN-C04b.md)、[C-08](../plan/FEA-CONTRACT-FROZEN-C08.md)（本卡均**不触**）；[C-05](../plan/FEA-CONTRACT-FROZEN-C05.md)（活跃草稿不进 `S`）。
3. **用户裁决** U-03=B（draft owner）。
4. **DSH 裁决**（[GOAL-PROGRESS](../checkpoints/GOAL-PROGRESS-2026-11-01.md) Q-1/Q-2/Q-3）+ **v2 处置裁决**（Q-6…Q-10，下述）。
5. 范围冻结复核 r1 [`FEA-03-scope-r1`](../reviews/FEA-03-scope-r1.md) `changes_requested`（P0×1 / P1×7 / P2×11）→ 本版逐条处置。

## DSH 裁决落盘（含 v2 处置裁决）

| # | 裁决 | 内容 |
|---|---|---|
| Q-1 | 释放 FEA-03 | 依赖已满足；Codex 为预期实现者 → 裁决交 DSH |
| Q-2 | **文件 journal** | `<data-root>/drafts/<DraftId>.json`；temp + `os.replace` 原子写；**不新增 schema 表**、不改 `schema.py`/migrations |
| Q-3 | 两切片 | CORE（Python）先验收；BRIDGE（C#）同 Task 内**收窄**（见 Q-8） |
| **Q-6** | **旧路径语义不变（处置 P0-01）** | **不改** `V11R_REGION_WRITE_CONTRACT` C073 的 append-only/非幂等语义；SC-D11 的"最终去重键"**仅约束新 token 路径的回放**，不适用于旧路径。契约内部口径差异登记 `FOLLOW-UP-FEA03-1`（需时走 `CONTRACT-UNFREEZE`） |
| **Q-7** | **commit receipt 落盘（处置 P1-03）** | `<data-root>/drafts/<DraftId>.receipt.json`，含 `{tokenId, DraftId, DraftSequence, revisionId, committedAt}`；与 journal 同目录、独立文件 |
| **Q-8** | **BRIDGE 收窄（处置 P1-04/P1-07）** | AC12 收敛为「ApplicationCore 本地草稿缓冲 + 可注入 seam（**不接线** Host/IPC/CoreClient）」；wire 接线与错误码映射由 `FEA-04` 承担；本卡**不新增/不透传 wire 码** → L-2 N/A 成立 |
| **Q-9** | **manual 位口径（处置 P1-05⑤）** | `protectionDigest` 的 manual 位取 `RegionText.manual_edited`（`src/domain/regions/entities.py`）；C-13 `:173` 的引用歧义登记 `FOLLOW-UP-FEA03-2`（需时 UNFREEZE 澄清），本卡以 `manual_edited` 实现并在 Handoff 声明 |
| **Q-10** | **几何/样式按域合并（处置 P1-05③）** | 文本冲突 `conflicted` 禁止自动合并（已断言）；几何/样式按域合并 = **同一去重键下后到覆盖**，须断言"文本未变、几何/样式被更新"且不产生新 revision |

## 冻结设计规则

### R-DRAFT（草稿模型）
- **R-DRAFT-1**：11 字段严格按 SC-D01；`DraftSequence` 从 0 起、每次 patch +1。`PageBindingVersion` 为**调用方注入的不透明整数**（不读 `page_bindings`——该表尚不存在，L-1 边界），本卡只透传与回读。
- **R-DRAFT-2**：输入先进共享内存缓冲；防抖间隔由**实现 Task 实测**后写入 Handoff（C-13 已知限制 L-3），测量方法 = 记录真实输入事件间隔分布（p50/p95）+ 证据文件；强制 flush 触发点 = 切页 / 切工作面 / 退出 / 窗口关闭 / Run 提交前。
- **R-DRAFT-3**：flush 失败（磁盘满/IO 错）→ 不丢内存缓冲，草稿置 `conflicted` 并抛结构化错误（`DRAFT_FLUSH_FAILED`）；**UI 提示由 `FEA-04` 承载（deferral）**，本卡只保证错误可诊断。
- **R-DRAFT-4**（U-03=B）：`(SessionId, RegionId)` 定 owner；同 Session 主画布与浮窗共享 `DraftId`；单串行 patch 队列；跨 Session 只读或显式转移；文本冲突禁止自动合并。

### R-JOURNAL / R-RECEIPT（Q-2、Q-7）
- **R-JOURNAL-1**：`<data-root>/drafts/` 为 **app-owned 目录**：只新建/替换本应用自己的 `*.json`，不读取/改写用户既有文件；内容 = `{DraftId, DraftSequence, patch, savedAt, status, SessionId, PageId, RegionId, BaseRevisionId, PageBindingVersion, undoCursor}`。
- **R-JOURNAL-2**：写序 = 写 `*.tmp` → flush + fsync 文件 → `os.replace` → fsync 目录；掉电可丢窗口 = 最后一次未 fsync 的 patch（≤ 防抖间隔）；启动时清理残留 `*.tmp`，**不得**把 `*.tmp` 当作草稿。
- **R-JOURNAL-3**：journal 与 revision 表分离；重启可读 → 恢复 `active` 且**不自动提交**；损坏/不可读 → 丢弃并提示，不阻塞启动。
- **R-JOURNAL-4（只读与单写者）**：Host 处于只读策略（`ReadOnlyUntilParity`/自检失败/旧壳）时，journal 写 **fail-closed**（拒绝并返回只读错误），内存草稿仍可编辑并提示不可持久化；同一 data-root 仅允许一个 Core 写者（Host 全局单实例保证），第二写者启动即 fail-closed 并记录。
- **R-JOURNAL-5**：孤儿草稿（无活跃 Session）→ `discarded`；Session 结束清理其 journal；清理不得删除 receipt。
- **R-RECEIPT-1**：commit receipt 持久化 `{tokenId, DraftId, DraftSequence, revisionId, committedAt}`；用于**跨重启**的 token 幂等。
- **R-RECEIPT-2**：同一 `(DraftId, DraftSequence)` 重放 → 读 receipt 返回同一 `revisionId`，**不产生第二个 revision**；同 token 但内容摘要不同 → 拒绝（`EDIT_TOKEN_REUSED`），不写 revision。

### R-TOKEN / R-CAND / R-APPLY
- **R-TOKEN-1**：token `{tokenId, DraftId, DraftSequence, SessionId, issuedAt, expiresAt}`；过期提交 → `EDIT_TOKEN_EXPIRED`（不静默接受）。
- **R-CAND-1**：prepare 只产 `RegionCandidate{candidateId, RegionId, BaseRevisionId, origin}`，`origin ∈ {machine,user,imported,restored}`（`schema.py:256-257` 为唯一真源）；绝不写 `current_revision_id`。
- **R-CAND-2（候选生命周期）**：`RegionCandidate` 仅存**内存**（Core 会话内），随 apply/discard/会话结束失效；**跨重启不找回**（如需跨重启，须走新契约/UNFREEZE，本卡不做）；跨命令通过 Core 会话内的 candidate registry 找回。
- **R-APPLY-1**：一次 apply 的全部 Region 变更在**同一 SQLite 事务**内；逐 Region 校验 `BaseRevisionId` 仍是当前值，否则整体回滚并返回 `STALE_BASE_REVISION`；**必须复用/扩展现有 `commit_region_batch` seam**（`src/application/editing/ports.py:83`、`src/infrastructure/sqlite/regions.py:288`，已含 `BEGIN IMMEDIATE` + `expected_current_checks`），禁止另开写路径。
- **R-APPLY-2（优先级）**：stale base 检查**先于**去重判断：`BaseRevisionId` 不匹配 → `STALE_BASE_REVISION`（即使内容命中 receipt 也不返回旧 revision）。

### R-LOCK / R-STYLE / R-DIGEST
- **R-LOCK-1**：三锁语义同 SC-D09；**candidate 生成与 apply 两条路径都检查**；`inpaint_locked` 不对 `style_json` 断言。
- **R-STYLE-1**：`style_json` 可写键 = `TextStyle` 6 个 snake_case 字段；白名单外键拒绝 `STYLE_KEY_NOT_ALLOWED`，**错误必须列出违规键名**；扩键须先改 `TextStyle` 再 UNFREEZE。
- **R-DIGEST-1**：`protectionDigest` = 三锁 + `manual_edited` 位（Q-9）；派生摘要、不加 schema 列、不加错误码；拒绝走 `LOCK_CHANGED`；manual 位纳入快照比对。

### R-LEGACY（Q-6）
- **R-LEGACY-1**：旧路径（`src/application/editing/service.py` 用户保存路径）**语义不变**：append-only、非幂等、不静默去重（C073 优先）。
- **R-LEGACY-2**：新 token 路径的回放判据 = receipt（同 `(DraftId, DraftSequence)` → 同 revision）；内容摘要 canonical = `sha256(稳定 JSON)`，字段集 = `{text_json, geometry(normalized), style_json(6 键)}`，数值统一 `repr` 归一化、键排序；该摘要**只用于新路径的跨重启重放判定与新路径内部一致性**，不改变旧路径行为。
- **R-LEGACY-3**：过渡期结束判据 = ①全仓 `rg "save_manual_translation\(" src apps` 无调用方直接走旧路径（排除定义与 tests）；②新路径写入点清单与 UI 实际写入点一一对应（由 `FEA-04`/`FEA-06` 提供证据，本卡只登记清单）；③独立复核通过。

## 范围（写域）

- **CORE（Python）**：`src/application/editing/**`、`src/domain/regions/**`、`src/domain/drafts/**`（新建草稿实体）、`src/infrastructure/sqlite/**`（**除 `schema.py` 与 `migrations/`**，由正文约束）、`src/infrastructure/filesystem/**`（journal/receipt 适配器）、`src/bootstrap/core_assembly.py`（接线）、`src/bootstrap/core_service.py`（仅 data-root 注入）。
- **BRIDGE（C#，收窄）**：`apps/desktop-avalonia/src/NewManga.ApplicationCore/**` + `apps/desktop-avalonia/tests/**`（仅 ApplicationCore 测试）；**不接线** Host/IPC/CoreClient。
- **测试**：`tests/editing/**`、`tests/domain/**`、`tests/infrastructure/**`、`tests/core/test_region_write_commands.py`、`tests/core/test_region_batch_locking.py`。
- **证据**：`verification/FEA-03/**`。
- **治理**：本卡、`STATUS`、`REBASELINE_PLAN`、`TASK_LEDGER`、`doc/checkpoints/**`、`doc/handoffs/FEA-03-*.md`。
- **不改**：`schema.py`/`migrations`（L-1）、`apps/**` 其它面、冻结契约字节、`G-DELETE-IMPL`、其它 Task、用户数据；不 push；不新增依赖。

## 交付项映射（处置 P2-09）

| 方案交付项 | 本卡承载 | 说明 |
|---|---|---|
| draft journal | R-JOURNAL-1…5、AC5 | 文件 journal（Q-2） |
| edit token | R-TOKEN-1、AC4 | 幂等 + 过期 |
| commit receipt | R-RECEIPT-1…2、AC15 | Q-7 新增 |
| 保护 epoch | R-DIGEST-1、AC10 | 等同 SC-D12 digest；无独立 epoch 表 |
| 应用草稿缓冲 | AC12（BRIDGE 收窄） | 不接线 |
| draft ACK | R-TOKEN-1 的 receipt 确认、AC4/AC15 | 不新增 wire 码（Q-8） |
| 独立 patch undo | `undoCursor` 字段 + AC1 | undo 栈不持久化（SC-D01） |
| revision restore | 既有 C045 路径 | 本卡不重实现，只回归（AC13） |

## 验收标准（冻结版）

- [ ] **AC1 草稿字段与序号**：11 字段齐全；`DraftSequence` 0→N 单调；同 Session 主窗/浮窗同 `DraftId`（SC-D01）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC2 flush 节奏与失败语义**：5 个强制 flush 点逐一断言；防抖值由实现实测写入 Handoff（测量方法与证据）；注入 flush 失败 → 缓冲未丢、`conflicted`、`DRAFT_FLUSH_FAILED`（UI 提示 deferral 到 FEA-04）（SC-D02）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC3 draft owner**：同 Session 共享 DraftId + 单串行队列；跨 Session 只读/显式转移；文本冲突双方 `conflicted`；几何/样式按域合并 = 同键后到覆盖且不产生新 revision（Q-10）（SC-D03）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC4 edit token 幂等/过期**：同 `(DraftId, DraftSequence)` 重复提交 → 1 revision、同 `revisionId`；过期 → `EDIT_TOKEN_EXPIRED`（SC-D04）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC5 journal 崩溃恢复与原子性**：CRASH-A（写 tmp 前）→ 旧 journal 完整；CRASH-B（tmp 写完、rename 前）→ 旧 journal 完整、`*.tmp` 启动清理；CRASH-C（rename 后）→ 新 journal 完整；恢复后 `active` 且无 revision；损坏 journal → 丢弃提示（SC-D05、R-JOURNAL-2/3）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC6 candidate-only prepare**：prepare 后 `current_revision_id` 不变；candidate 四字段；翻译产物先成 candidate；candidate 仅内存、跨命令可找回、跨重启不找回（R-CAND-2）（SC-D06/D07）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC7 统一事务 apply**：复用 `commit_region_batch`；3 Region 第 3 个 stale → 前 2 个不生效；独立连接提交前不可见；stale 先于去重（R-APPLY-2）（SC-D08）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC8 三锁 × 三域**：`region_locked` 全拒；`translation_locked` text 拒/geometry+style 允；`inpaint_locked` 不对 style 断言；candidate 与 apply 两路径同样检查（SC-D09）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC9 style 白名单**：`customFoo` → `STYLE_KEY_NOT_ALLOWED`**且错误含键名**；`translation_locked` 下 `font_size` 允许、`text_json` 拒绝；`text_color` 允许（SC-D10）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC10 protectionDigest**：三锁 + `manual_edited`；candidate 后改保护位 → apply 拒绝 `LOCK_CHANGED`；不加 schema 列/错误码（SC-D12、Q-9）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC11 旧路径语义不变**：旧路径两次同文保存仍产生 2 个 revision（C073 行为保持）；新路径同 token 重放只 1 个；旧→新 / 新→旧两种顺序断言（Q-6、R-LEGACY-1/2）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC12 BRIDGE 收窄**：ApplicationCore 本地草稿缓冲（11 字段投影）+ 可注入 seam；单串行 patch 队列 + flush 触发；**不接线** Host/IPC；CORE 先通过验收，BRIDGE 完成后 Task 才可提交复核（Q-8）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC13 回归**：基线 `python -m pytest tests/editing tests/infrastructure tests/core/test_region_write_commands.py tests/core/test_region_batch_locking.py -q` 逐文件 outcome 对照；新增测试文件在 Handoff 登记。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC14 独立复核**：范围复核 r2 `approved`（P0/P1=0）；实现复核 `doc/reviews/FEA-03-r1.md` approved（P0/P1=0）（含 Review Appointment 记录）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC15 commit receipt 跨重启幂等**：重启后用同一 token 重放 → 同 `revisionId`、无第二个 revision；同 token 不同内容 → `EDIT_TOKEN_REUSED` 拒绝；receipt 清理不影响 journal（R-RECEIPT-1/2）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC16 活跃草稿登记与清理**：`edit-open` 登记 `active`；Session 结束无残留 journal；孤儿草稿 `discarded`；清理不删 receipt（SC-D06、R-JOURNAL-5）。 <<PARTIAL: 范围冻结；实现未开始>>

## L 前置适用性判定

| 保留项 | 判定 | 依据与再触发 |
|---|---|---|
| **L-1** 四表 DDL | **NOT_APPLICABLE** | 文件 journal 不建表；不改 `schema.py`/migrations；`PageBindingVersion` 为注入的不透明整数，不读 `page_bindings`。再触发：新增表/列/索引/迁移 → `blocked` |
| **L-2** M2-C1 字节修订 | **NOT_APPLICABLE** | 新错误码（`EDIT_TOKEN_EXPIRED`/`STYLE_KEY_NOT_ALLOWED`/`STALE_BASE_REVISION`/`EDIT_TOKEN_REUSED`/`DRAFT_FLUSH_FAILED`）仅在 Core 内部结构化返回；BRIDGE 收窄为不接线（Q-8），不改 `allowedRunErrorCodes`（**注：该白名单当前在代码中不存在，仅 doc 计划项，本卡不创建**）。再触发：向 Host/IPC 透传新码 → `blocked`，先完成 M2-C1 独立修订 |
| **L-5** 整库恢复锁 | **NOT_APPLICABLE** | 不触备份/恢复。再触发：触恢复/维护互斥 → `blocked` |

## 测试矩阵（V1–V21，planned；CORE 全部从真实 Core 服务执行）

| # | 场景 | 期望 | 对应 AC |
|---|---|---|---|
| V1 | 新建草稿 + 3 patch | 11 字段；序号 0→3 | AC1 |
| V2 | 主窗/浮窗同 Session | 同 DraftId | AC1 |
| V3 | 5 个 flush 触发点 | 各点触发持久化 | AC2 |
| V4 | flush 失败注入 | 缓冲未丢；`conflicted`；`DRAFT_FLUSH_FAILED` | AC2 |
| V5 | 两会话同 Region | 非 owner 只读；转移后原 owner 只读 | AC3 |
| V6 | 文本冲突 | 双方 `conflicted`；不自动合并 | AC3 |
| V7 | 几何/样式同键后到覆盖 | 文本未变、几何/样式更新、无新 revision | AC3 |
| V8 | 同 token 重放 ×2 | 1 revision；同 revisionId | AC4 |
| V9 | 过期 token | `EDIT_TOKEN_EXPIRED`；无 revision | AC4 |
| V10 | CRASH-A/B/C（tmp 前 / rename 前 / rename 后） | 旧 or 新 journal 完整；`*.tmp` 清理 | AC5 |
| V11 | 损坏 journal | 丢弃提示；不阻塞启动 | AC5 |
| V12 | prepare → current_revision_id | 不变；candidate 四字段 | AC6 |
| V13 | 翻译产物 vs 活跃草稿 | 产物为 candidate；现在变 | AC6 |
| V14 | 3 Region apply 第 3 个 stale | 全回滚；独立连接不可见 | AC7 |
| V15 | 三锁 × 三域矩阵 | 同 SC-D09 | AC8 |
| V16 | style 白名单 | 拒绝含键名；真实键允许 | AC9 |
| V17 | candidate 后改保护位 | `LOCK_CHANGED` | AC10 |
| V18 | 旧路径同文两次 | 2 revision（语义不变） | AC11 |
| V19 | 旧→新 / 新→旧 | 各自期望固定；无意外双写 | AC11 |
| V20 | 重启后 token 重放 / 同 token 不同内容 | 同 revisionId / `EDIT_TOKEN_REUSED` | AC15 |
| V21 | Session 结束 / 孤儿草稿 | 无残留 journal；`discarded`；receipt 保留 | AC16 |

## 禁止范围

- 不改冻结契约字节（15 份 pin）；不改 `schema.py`/migrations；不新增 wire 码/白名单；**不触 C-04b（删除保护）与 C-08（PreparedRun/candidate store）**。
- 不改 `apps/**` 其它面（仅 `NewManga.ApplicationCore` 与对应测试）；不接线 Host/IPC/CoreClient。
- 不动用户数据、不 push、不合并 main。
- 不顺手修 FEA-04/07/10/12；不释放其它 Task。
- 不降低既有测试断言来「通过」。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

实现尚未开始。开始时按 `Workspace Governance` 在 `G:\CODEX\New Manga.workspace\` 建 task-env/worktree（分支 `feat/fea-03`）并补齐本表。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | - | NOT_APPLICABLE | - | - | 范围冻结阶段；未访问用户数据 |
| build/temp（未来） | - | PENDING | ..\New Manga.workspace\ | - | 实现开始前补齐 |

## Closeout Record

- 2026-11-01：DSH 裁决释放（GOAL Q-1）；范围冻结 v1（`106299b50`）。
- 2026-11-01：范围复核 r1 `changes_requested`（P0×1 / P1×7 / P2×11）；v2 逐条处置：Q-6（旧路径语义不变）、Q-7（commit receipt）、Q-8（BRIDGE 收窄）、Q-9（manual 位）、Q-10（几何/样式按域合并）；写域补 bootstrap/filesystem/domain.drafts；V1–V21 覆盖全部 AC。
- 2026-11-01：`proposed`，派独立复核 r2；**通过前不 ready、不派实现**。
