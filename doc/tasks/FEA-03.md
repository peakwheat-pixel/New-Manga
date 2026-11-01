---
id: FEA-03
title: FEA-03 草稿与保护协调（draft journal / edit token / candidate-only / 统一 apply / 锁白名单 / protectionDigest）
kind: implementation
governance_version: 3
status: proposed
approval: dsh_ruling_2026-11-01_GOAL_Q1_Q3
suggested_owner: codex
owner: codex
reviewer: c01b-reviewer
depends_on:
  - FEA-00A-IMPL-1
  - FEA-01-FREEZE-1
base_commit: 419d75bbb
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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
  - src/infrastructure/sqlite/**（除 `schema.py` 与 `migrations/`）
  - apps/desktop-avalonia/src/NewManga.ApplicationCore/**
  - apps/desktop-avalonia/tests/**（仅 ApplicationCore 草稿缓冲相关）
  - tests/editing/**
  - tests/domain/**
  - tests/infrastructure/**
  - verification/FEA-03/**
---

# FEA-03 草稿与保护协调（范围冻结 v1，待独立复核）

## 来源与授权

1. 方案 §12.1 `:641`：S1 `FEA-03` 依赖 `FEA-01`、`FEA-00a`；交付 Core draft journal/edit token/commit receipt、保护 epoch、应用草稿缓冲。
2. 方案 §15.6 `:923`：写域 `src/application/`、`src/domain/`、`src/infrastructure/sqlite/`、`NewManga.ApplicationCore/`；L2 高风险；出口「draft ACK、单 owner、独立 patch undo 与 revision restore」。
3. **契约**：[C-13 冻结 v5](../plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md)（pin `d2cb8de4…`，SC-D01…SC-D12）；[C-01b](../plan/FEA-CONTRACT-FROZEN-C01b.md)（表结构/三锁/复合 FK）；[C-04b](../plan/FEA-CONTRACT-FROZEN-C04b.md)（删除保护边界，本卡不改）；[C-08](../plan/FEA-CONTRACT-FROZEN-C08.md)（PreparedRun/candidate store 与本卡 RegionCandidate 同名异物，必须区分）；[C-05](../plan/FEA-CONTRACT-FROZEN-C05.md)（活跃草稿不进 `S`）。
4. **用户裁决**：U-03=B（draft owner 模型，2026-11-01）。
5. **DSH 裁决**（[GOAL-PROGRESS Q-1/Q-2/Q-3](../checkpoints/GOAL-PROGRESS-2026-11-01.md)）：释放本卡；draft journal 采用**文件 journal**；CORE/BRIDGE 两切片。

## DSH 裁决落盘（本卡范围依据）

| # | 裁决 | 内容 |
|---|---|---|
| Q-1 | 释放 FEA-03 | 依赖已满足（FEA-00a done、FEA-01 冻结）；Codex 为预期实现者，按目标规则裁决交 DSH |
| Q-2 | **文件 journal** | `<data-root>/drafts/<DraftId>.json`，temp + 原子 rename 写入；不新增 schema 表、不改 `schema.py`/migrations |
| Q-3 | **两切片** | CORE（Python：journal/token/candidate/apply/locks/digest）必须先通过测试；BRIDGE（C# ApplicationCore 草稿缓冲）同 Task 内后置，不得阻塞 CORE 独立验收 |

## 冻结设计规则

### R-DRAFT（草稿模型与落盘）
- **R-DRAFT-1**：草稿字段严格按 SC-D01 的 **11 个字段**（`DraftId`/`SessionId`/`PageId`/`RegionId?`/`BaseRevisionId?`/`PageBindingVersion`/`DraftSequence`/`patch`/`undoCursor`/`savedAt`/`status`）；`DraftSequence` 从 0 起、每次 patch +1。
- **R-DRAFT-2**：输入先进共享内存缓冲；按防抖间隔持久化（方案举例 300–500ms，具体值由本卡用真实输入实测后冻结，写入 Handoff）；强制 flush 触发点 = 切页 / 切工作面 / 退出 / 窗口关闭 / Run 提交前。
- **R-DRAFT-3**：flush 失败（磁盘满/IO 错）→ 不丢内存缓冲，草稿置 `status=conflicted` 并向上抛结构化错误；重试或显式放弃由调用方决定。
- **R-DRAFT-4**（U-03=B）：按 `(SessionId, RegionId)` 定 owner；同 Session 主画布与浮窗共享同一 `DraftId`；单一串行 patch 队列 + 文本/几何/样式分域版本；跨 Session 默认只读、显式转移；文本冲突禁止自动合并，双方得 `conflicted`。

### R-JOURNAL（文件 journal，Q-2）
- **R-JOURNAL-1**：journal 落在 `<data-root>/drafts/<DraftId>.json`；写入用 temp 文件 + `os.replace` 原子替换；文件内容 = `{DraftId, DraftSequence, patch, savedAt, status, SessionId, PageId, RegionId, BaseRevisionId, PageBindingVersion, undoCursor}`（SC-D05 最小集 + 恢复所需）。
- **R-JOURNAL-2**：journal 与 revision 表分离；journal 不是修订历史；重启后 journal 可读 → 恢复为 `active` 草稿且**不自动提交**；不可读/损坏 → 丢弃并提示，不阻塞启动。
- **R-JOURNAL-3**：孤儿草稿（无活跃 Session）→ `discarded`；Session 结束清理对应 journal。

### R-TOKEN / R-CAND / R-APPLY
- **R-TOKEN-1**：`edit-open` 生成 token `{tokenId, DraftId, DraftSequence, SessionId, issuedAt, expiresAt}`；同一 `(DraftId, DraftSequence)` 重复提交返回同一 `revisionId`，不得产生两个 revision；过期提交拒绝 `EDIT_TOKEN_EXPIRED`。
- **R-CAND-1**：prepare 只产出编辑层 `RegionCandidate{candidateId, RegionId, BaseRevisionId, origin}`，`origin ∈ {machine,user,imported,restored}`（以 `schema.py:256-257` CHECK 为唯一真源）；**绝不写 `current_revision_id`**。
- **R-APPLY-1**：一次 apply 的全部 Region 变更在**同一 SQLite 事务**内；逐 Region 校验 `BaseRevisionId` 仍是当前值，否则整体回滚并返回 `STALE_BASE_REVISION`；提交前对外不可见。

### R-LOCK / R-STYLE / R-DIGEST
- **R-LOCK-1**：三锁语义 = `region_locked`(全拒) / `translation_locked`(text 拒；geometry/style 允) / `inpaint_locked`(仅 inpaint 产物，不对 `style_json` 生效)；**candidate 生成与 apply 两条路径都必须检查**。
- **R-STYLE-1**：`style_json` 可写键 = `TextStyle` 实际 6 个 snake_case 字段（`font_family`/`font_size`/`auto_font_size_enabled`/`text_color`/`stroke_color`/`stroke_width`）；白名单外键拒绝 `STYLE_KEY_NOT_ALLOWED`；扩键必须先改 `TextStyle` 定义再走 UNFREEZE。
- **R-DIGEST-1**：`protectionDigest` 只含保护状态位（三锁 + `text_json` 的 manual 位），派生摘要、不新增 schema 列、不新增错误码；拒绝走既有 `LOCK_CHANGED` 路径；manual 位必须纳入快照比对。

### R-LEGACY
- **R-LEGACY-1**：既有 `src/application/editing/service.py` 用户保存路径在过渡期继续有效；新旧路径不得双写产生两个 revision；最终去重键统一 `(RegionId, BaseRevisionId, 内容摘要)`。
- **R-LEGACY-2**：过渡期结束判据 = ①全仓无调用方直接走旧保存路径；②新路径写入点清单与 UI 实际写入点一一对应；③独立复核通过。三条全满足前不得移除旧路径。

## 验收标准（冻结版）

- [ ] **AC1 草稿字段与序号**：新建草稿断言 11 字段齐全（SC-D01）；`DraftSequence` 从 0 起、每次 patch +1；主画布与浮窗共享同一 `DraftId`。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC2 flush 节奏与失败语义**：防抖间隔实测后冻结；5 个强制 flush 触发点逐一断言；注入 flush 失败 → 缓冲未丢、`status=conflicted`、错误可诊断（SC-D02）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC3 draft owner（U-03=B）**：同 Session 共享 `DraftId` + 单串行 patch 队列；跨 Session 只读/显式转移；文本冲突双方 `conflicted`、不自动合并（SC-D03）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC4 edit token 幂等与过期**：同 `(DraftId, DraftSequence)` 重复提交 → 1 个 revision、两次同 `revisionId`；过期 → `EDIT_TOKEN_EXPIRED` 拒绝（SC-D04）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC5 journal 崩溃恢复**：写 journal → 杀进程 → 重启 → 草稿恢复 `active`、无新 revision；journal 损坏 → 丢弃并提示、不阻塞启动；原子写（temp+rename）断言（SC-D05、R-JOURNAL）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC6 candidate-only prepare**：prepare 后 `current_revision_id` 不变；`RegionCandidate` 四字段齐、`origin` 取值受 CHECK 约束；翻译产物先成为 candidate（SC-D06/D07）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC7 统一事务 apply**：3 Region 中第 3 个 `BaseRevisionId` 过期 → 前 2 个也不生效（整体回滚）；提交前独立连接读不到新值（SC-D08、R-APPLY-1）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC8 三锁 × 三域**：`region_locked=1` 全拒；`translation_locked=1` text 拒/geometry+style 允；`inpaint_locked=1` 不对 `style_json` 断言；candidate 与 apply 两路径同样检查（SC-D09）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC9 style 白名单**：写 `style_json.customFoo` → `STYLE_KEY_NOT_ALLOWED`；`font_size` 在 `translation_locked=1` 下允许、`text_json` 拒绝；真实键 `text_color` 允许（回归）（SC-D10）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC10 protectionDigest**：三锁 + manual 位纳入摘要；candidate 生成后改动保护状态 → apply 拒绝走 `LOCK_CHANGED`；不新增 schema 列/错误码（SC-D12）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC11 旧路径兼容**：旧路径与新路径先后写同一内容 → 只 1 个 revision；去重键为 `(RegionId, BaseRevisionId, 内容摘要)`；旧路径不得产生双写（SC-D11、R-LEGACY）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC12 BRIDGE 切片（ApplicationCore）**：C# 侧草稿缓冲与 Core 协议对接（共享 DraftId、串行 patch 队列、flush 触发）；CORE 切片独立验收通过后才接 BRIDGE（Q-3）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC13 回归**：既有 editing/regions/sqlite 相关测试 outcome 对照（修前/修后/判定/理由）；新增测试文件在 Handoff 逐项登记。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC14 独立复核**：范围冻结复核 `doc/reviews/FEA-03-scope-r1.md` approved（P0/P1=0）；实现复核 `doc/reviews/FEA-03-r1.md` approved（P0/P1=0）。 <<PARTIAL: 范围冻结；待派发>>

## L 前置适用性判定

| 保留项 | 判定 | 再触发条件 |
|---|---|---|
| **L-1** 四表 DDL | **NOT_APPLICABLE**（文件 journal，不触 `source_entries`/`page_bindings`/`source_sync_plans`/`source_operations`；不改 `schema.py`/migrations） | 若实现需新增表/列/索引或迁移 → `blocked`，先完成 L-1 前置或改文件方案 |
| **L-2** M2-C1 字节修订 | **NOT_APPLICABLE**（新错误码仅 Core 内部结构化返回；不新增 wire 码、不改 `allowedRunErrorCodes` 白名单） | 若需把 `EDIT_TOKEN_EXPIRED`/`STYLE_KEY_NOT_ALLOWED`/`STALE_BASE_REVISION` 暴露到 Host/IPC wire → `blocked`，先完成 M2-C1 独立字节修订 |
| **L-5** 整库恢复锁 | **NOT_APPLICABLE**（不触备份/恢复） | 若触恢复/维护互斥 → `blocked`，按 L-5 四步补 AC |

> `doc/plan/FEA-C11_IMPL_PREREQS.md` §0：不适用不等于豁免。

## 测试矩阵（V1–V12，planned）

| # | 场景 | 期望 |
|---|---|---|
| V1 | 新建草稿 + 3 次 patch | 11 字段齐；序号 0→3 单调 |
| V2 | flush 失败注入（只读目录/磁盘满模拟） | 缓冲未丢；`conflicted`；错误结构化 |
| V3 | 两会话同 Region | 非 owner 只读；转移后原 owner 只读 |
| V4 | 同 token 重复提交 ×2 | 1 revision；同 revisionId |
| V5 | 过期 token 提交 | `EDIT_TOKEN_EXPIRED`，无 revision |
| V6 | journal 写入后 kill -9 + 重启 | 草稿 `active`、无 revision；损坏 journal 丢弃提示 |
| V7 | prepare → 检查 current_revision_id | 不变；candidate 四字段正确 |
| V8 | 3 Region apply，第 3 个过期 | 整体回滚；独立连接不可见 |
| V9 | 三锁 × 三域矩阵 | 与 SC-D09 一致 |
| V10 | style 白名单外键 / 真实键 | 拒绝 / 允许 |
| V11 | candidate 后改保护状态 → apply | `LOCK_CHANGED` 拒绝 |
| V12 | 旧路径与新路径同内容 | 1 revision；去重键生效 |

## 禁止范围

- 不改冻结契约字节（15 份 pin）；不改 `schema.py`/migrations；不新增 wire 码/白名单（触发 L-2 须先 blocked）；
- 不改 `apps/**` 其它面（仅 `NewManga.ApplicationCore` 与对应测试）；
- 不动用户数据、不 push、不合并 main；
- 不顺手修 FEA-04/07/10/12 的功能；不释放其它 Task；
- 不降低既有测试断言来「通过」。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

实现尚未开始。开始时按 `Workspace Governance` 在 `G:\CODEX\New Manga.workspace\` 建 task-env/worktree 并补齐本表。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | - | NOT_APPLICABLE | - | - | 范围冻结阶段；未访问用户数据 |
| build/temp（未来） | - | PENDING | ..\New Manga.workspace\ | - | 实现开始前补齐 |

## Closeout Record

- 2026-11-01：DSH 裁决释放（GOAL Q-1）；范围冻结 v1（写域、AC1–AC14、V1–V12、L 判定）；`status: proposed`，待上下文独立复核 r1。
