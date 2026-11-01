---
id: FEA-03
title: FEA-03 草稿与保护协调（draft journal / edit token + receipt / candidate-only / 统一 apply / 锁白名单 / protectionDigest）
kind: implementation
governance_version: 3
status: ready
approval: dsh_ruling_2026-11-01_GOAL_Q1_Q11
suggested_owner: codex
owner: codex
reviewer: fea03-scope-reviewer
depends_on:
  - FEA-00A-IMPL-1
  - FEA-01-FREEZE-1
base_commit: dfa70c002
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
review_appointment: "r1…r5 doc/reviews/FEA-03-scope-r1..r5.md（reviewer fea03-scope-reviewer，DSH fresh 独立上下文派发）"
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
  - apps/desktop-avalonia/src/NewManga.ApplicationCore/**
  - apps/desktop-avalonia/tests/**
  - tests/editing/**
  - tests/domain/**
  - tests/infrastructure/**
  - tests/core/test_region_write_commands.py
  - tests/core/test_region_batch_locking.py
  - verification/FEA-03/**
---

# FEA-03 草稿与保护协调（范围冻结 v6，独立复核 r5 approved，ready 交 Codex）

## 来源与授权

1. 方案 §12.1 `:641`（draft journal / edit token / commit receipt / 保护 epoch / 应用草稿缓冲）；§15.6 `:923`。
2. **契约**：[C-13 冻结 v6](../plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md)（pin `8faf1e80…`，SC-D11 经 UNFREEZE）；[C-01b](../plan/FEA-CONTRACT-FROZEN-C01b.md)；[C-04b](../plan/FEA-CONTRACT-FROZEN-C04b.md)、[C-08](../plan/FEA-CONTRACT-FROZEN-C08.md)（均**不触**）；[C-05](../plan/FEA-CONTRACT-FROZEN-C05.md)。
3. **用户裁决** U-03=B。
4. **DSH 裁决**：GOAL Q-1/Q-2/Q-3 + Q-6…Q-11（下述）；v2/v3/v4/v5/v6 处置见 Closeout。
5. 复核：[r1](../reviews/FEA-03-scope-r1.md) `changes_requested`（P0×1/P1×7/P2×11）→ v2；[r2](../reviews/FEA-03-scope-r2.md)（P0×1/P1×5/P2×12）→ v3；[r3](../reviews/FEA-03-scope-r3.md)（P0=0 / P1×4 / P2×12，**UNFREEZE approved**）→ v4/v5；[r4](../reviews/FEA-03-scope-r4.md)（P0=0 / P1×2 / P2×12）→ 本版 v6。

## DSH 裁决落盘

| # | 裁决 | 内容 |
|---|---|---|
| Q-1 | 释放 FEA-03 | 依赖已满足；Codex 为实现者 → 裁决交 DSH |
| Q-2 | 文件 journal | `<data-root>/drafts/<DraftId>.json`；temp + `os.replace` 原子写；不新增 schema、不改 `schema.py`/migrations |
| Q-3 | 两切片 | CORE 先验收；BRIDGE 收窄（Q-8） |
| Q-6 | 旧路径语义不变 | 不改 C073 append-only；SC-D11 的"新旧统一去重键"**不在本卡实施**（见 Q-11） |
| Q-7 | commit receipt | `<data-root>/drafts/receipts/<DraftId>.<DraftSequence>.json`；**多序列**；审计/加速用途，正确性由 R-APPLY-3 兜底 |
| Q-8 | BRIDGE 收窄 | ApplicationCore 本地缓冲 + 可注入 seam，**不接线** Host/IPC/CoreClient；wire 由 FEA-04 承担 |
| Q-9 | manual 位 | `protectionDigest` = 三锁（region 列）+ `text_json.translation_locked`（manual-protection flag，`RegionText.translation_locked`）+ `text_json.manual_edited`；与 C-13 `:173`「text_json 内 manual 标志」一致（`effective_region_locks` 读 `region.text.translation_locked`）；须断言"改任一位 → digest 变化 → apply 拒绝" |
| Q-10 | 几何/样式按域合并 | 文本冲突 `conflicted`（禁止自动合并）；几何/样式同键后到覆盖（草稿缓冲阶段，不产生新 revision） |
| **Q-11** | **SC-D11 适用范围已 UNFREEZE（处置 r2-P0-01）** | C-13 已由 [CONTRACT-UNFREEZE-C13-2026-11-01](../reviews/CONTRACT-UNFREEZE-C13-2026-11-01.md) 修订为 **v6**（r3 复核：UNFREEZE **approved**）：统一去重键限**新 token 路径**；旧路径保持 C073 append-only。本卡按 v6 实现 |

## 冻结设计规则

### R-DRAFT
- **R-DRAFT-1**：11 字段按 SC-D01；`DraftSequence` 0 起、每 patch +1；`PageBindingVersion` 为**调用方注入的不透明整数**（不读 `page_bindings`，L-1 边界）。
- **R-DRAFT-2**：输入先进内存缓冲；防抖间隔由**实现实测**（p50/p95 + 证据文件）写入 Handoff；强制 flush 点 = 切页 / 切工作面 / 退出 / 窗口关闭 / Run 提交前。
- **R-DRAFT-3**：flush 失败 → 不丢缓冲，置 `conflicted` + `DRAFT_FLUSH_FAILED`；UI 提示由 `FEA-04` 承载。
- **R-DRAFT-4**（U-03=B）：`(SessionId, RegionId)` 定 owner；同 Session 共享 `DraftId`；单串行 patch 队列；跨 Session 只读/显式转移；文本冲突禁止自动合并。

### R-JOURNAL / R-RECEIPT
- **R-JOURNAL-1**：`<data-root>/drafts/` 为 app-owned 目录（只新建/替换自己的文件，不读改用户文件）；内容 = 11 字段 + `status`/`savedAt` + `commitIntent?`（intent 与 journal 同一原子写，处置 r5-P2-05）。
- **R-JOURNAL-2**：写序 = `*.tmp` → flush + fsync 文件 → `os.replace` → 目录 fsync **平台降级**（Windows 上目录 fsync 不可用 → 退化为 `os.replace` 后不再 fsync，登记为已知限制，不阻塞）；启动清理 `*.tmp`，不得当作草稿。
- **R-JOURNAL-3**：journal 与 revision 表分离；重启可读 → 恢复 `active` 不自动提交；损坏/不可读 → 丢弃提示、不阻塞启动。
- **R-JOURNAL-4（可写性与单写者）**：**不依赖 Host 只读通道**（Core 无该输入）。判定 = ①data-root 目录不可写（OS 层）→ journal 写 fail-closed（`DRAFT_JOURNAL_UNWRITABLE`），内存草稿可继续编辑并标记不可持久化；②单写者 = `<data-root>/drafts/.lock` 独占文件锁（第二实例启动 fail-closed 并记录）；③Host 只读策略下的 UI 提示由 `FEA-04` 承担（deferral）。
- **R-JOURNAL-5**：孤儿草稿（无活跃 Session）→ `discarded`；Session 结束清理其 journal；清理不删 receipt。
- **R-RECEIPT-1**：每 `(DraftId, DraftSequence)` 一条 receipt 文件（`<data-root>/drafts/receipts/<DraftId>.<DraftSequence>.json`），含 `{tokenId, DraftId, DraftSequence, revisionIds: {regionId: revisionId}, contentDigests: {regionId: digest}, committedAt}`（多 Region 用映射，处置 r3-P1-03/r5-P2-06）；写序 = temp+fsync+`os.replace`，不可解析按缺失处理（r5-P2-08）。
- **R-RECEIPT-2**：同 `(DraftId, DraftSequence)` 重放 → 读 receipt 返回同 `revisionIds`（不新增 revision）；receipt 缺失（崩溃窗口）→ 由 **R-APPLY-3 的 journal intent** 兜底；同 token 但 `contentDigests` 不同 → `EDIT_TOKEN_REUSED`。
- **R-RECEIPT-3（清理）**：receipt 随 Draft 生命周期清理（Draft `discarded`/超过 7 天未活动时删除）；清理不得删除 journal；清理失败不得阻塞。

### R-TOKEN / R-CAND / R-APPLY
- **R-TOKEN-1**：token `{tokenId, DraftId, DraftSequence, SessionId, issuedAt, expiresAt}`；过期 → `EDIT_TOKEN_EXPIRED`。
- **R-CAND-1**：prepare 只产 `RegionCandidate{candidateId, RegionId, BaseRevisionId, origin}`（`origin` 以 `schema.py:256-257` CHECK 为真源）；绝不写 `current_revision_id`。
- **R-CAND-2**：candidate 仅内存（Core 会话内），apply/discard/会话结束失效；**跨重启不找回**；跨命令用 Core 会话 registry 找回。
- **R-APPLY-1**：一次 apply 全部 Region 在**同一 SQLite 事务**内；**复用/扩展 `commit_region_batch`**（`src/application/editing/ports.py:83`、`src/infrastructure/sqlite/regions.py:288`）；保护/digest 检查在事务内（在 `commit_region_batch` 的 `BEGIN IMMEDIATE` 内追加校验回调；**不改既有端口签名、不触 C-13 冻结记录铁律 2 所指的 `ports.py` 冻结面**），避免 TOCTOU。
- **R-APPLY-2（优先级，处置 r2-P1-04/r4-P1-01）**：**重放命中优先于 stale**：先查 receipt（或 intent 恢复）命中 → 返回既有 `revisionIds`（不写、不判 stale）；未命中 → 再按 `BaseRevisionId` 判 stale → `STALE_BASE_REVISION`。**token 过期检查先于 receipt 命中**（SC-D04：过期提交拒绝，不静默接受）。
- **R-APPLY-3（重放兜底，处置 r3-P1-02 / r4-P1-02）**：**不用 DB 内容去重**（`region_revisions` 无 base/内容列；`commit_region_batch` 事务不可从应用层访问）。**journal intent 方案**：apply 前写 `commitIntent{tokenId, DraftId, DraftSequence, expectedRevisionIds: {regionId: revisionId}, contentDigests: {regionId: digest}, startedAt}`（`expectedRevisionIds` = apply **预生成的新 revision id**，由既有 `_build_revision` 事务前生成；**不是** base id）；SQLite 事务提交后写 receipt，**receipt 写失败 → fail-closed 抛错**（进程不得继续写，重启由 intent 恢复）；apply 失败（stale/protection/DB）→ **finally 清 intent**。重启恢复：intent + receipt 都在 → 清 intent；intent 在、receipt 缺 → 逐 Region 判：`regions.current_revision_id == expectedRevisionIds[regionId]` **且**该 revision 的 `contentDigests[regionId]` 匹配 → 视为该 Region 已提交；全部匹配 → 补 receipt；否则清 intent 视为未提交。读 revision 用新增 `RegionRepository.revision_by_id(revision_id)`（写域内，不改既有端口签名）。digest 的 geometry 归一化用 `pages.width/height`（`schema.py:186-194`），取不到 → `PAGE_SIZE_UNAVAILABLE` fail-closed。**只用于新 token 路径**。

### R-LOCK / R-STYLE / R-DIGEST
- **R-LOCK-1**：三锁语义同 SC-D09；candidate 生成与 apply 两路径都检查；`inpaint_locked` 不对 `style_json` 断言。
- **R-STYLE-1**：`style_json` 白名单 = `TextStyle` 6 键；外键 → `STYLE_KEY_NOT_ALLOWED` **且错误含键名**；扩键先改 `TextStyle`。
- **R-DIGEST-1**：`protectionDigest` = 三锁（region 列）+ `text_json.translation_locked` + `text_json.manual_edited`（Q-9）；派生摘要、不加 schema 列/错误码；拒绝走 `LOCK_CHANGED`；检测在事务内（R-APPLY-1 扩展 seam）。注：这是 SC-D12 公式的**分组超集**（SC-D12 只含 region 三锁 + text manual 位；本卡额外把 `manual_edited` 纳入，属收紧而非放宽，不改 SC-D12 语义）。

### R-LEGACY（Q-6、Q-11）
- **R-LEGACY-1**：旧路径（`editing/service.py` 保存路径）**行为完全不变**：append-only、非幂等、不静默去重；本卡不改其实现。
- **R-LEGACY-2**：新路径回放判据 = receipt + journal intent（R-RECEIPT-2、R-APPLY-3）；内容摘要 canonical = `sha256(稳定 JSON)`，字段集 `{text_json, geometry(normalized), style_json(6 键)}`，数值 `repr` 归一化、键排序。
- **R-LEGACY-3**：过渡期结束判据 = ①`rg "save_manual_translation\\(" src apps | rg -v "def save_manual_translation|tests/"` 输出为空；②新写点清单（由 FEA-04/06 提供）；③复核通过。统一去重键按 **C-13 v6** 限新 token 路径（Q-11）；旧路径去重不在本卡实施（`FOLLOW-UP-FEA03-3` 已由 UNFREEZE 载体承接，待后续 Task）。

## 范围（写域）

- **CORE**：`src/application/editing/**`、`src/domain/regions/**`、`src/domain/drafts/**`、`src/infrastructure/sqlite/**`（除 `schema.py`/`migrations/`）、`src/infrastructure/filesystem/**`、`src/bootstrap/core_assembly.py`（仅接线）。
- **BRIDGE（收窄）**：`apps/desktop-avalonia/src/NewManga.ApplicationCore/**` + `apps/desktop-avalonia/tests/**`；**不接线** Host/IPC/CoreClient。
- **测试**：`tests/editing/**`、`tests/domain/**`、`tests/infrastructure/**`、`tests/core/test_region_write_commands.py`、`tests/core/test_region_batch_locking.py`。
- **证据**：`verification/FEA-03/**`；**治理**：本卡、STATUS、PLAN、LEDGER、checkpoints、handoffs。
- **不改**：`schema.py`/migrations、`apps/**` 其它面、冻结契约字节、`G-DELETE-IMPL`、其它 Task、用户数据；不 push；不新增依赖。

## 交付项映射

| 方案交付项 | 本卡承载 | 说明 |
|---|---|---|
| draft journal | R-JOURNAL-1…5、AC5、AC17 | 文件 journal（Q-2） |
| edit token | R-TOKEN-1、AC4 | 幂等 + 过期 |
| commit receipt | R-RECEIPT-1…3、AC15 | 多序列 + 清理（Q-7） |
| 保护 epoch | R-DIGEST-1、AC10 | SC-D12 digest |
| 应用草稿缓冲 | AC12 | BRIDGE 收窄 |
| draft ACK | receipt + R-APPLY-3、AC4/AC15 | 不新增 wire 码 |
| 独立 patch undo | `undoCursor` + AC1 | undo 栈不持久化 |
| revision restore | 既有 C045 路径 | 只回归（AC13） |

## 验收标准（冻结版）

- [ ] **AC1 草稿字段与序号**：11 字段；序号 0→N；主窗/浮窗同 DraftId（SC-D01）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC2 flush 节奏与失败语义**：5 个强制 flush 点；防抖实测（方法与证据）；失败 → 缓冲未丢/`conflicted`/`DRAFT_FLUSH_FAILED`；UI 提示 deferral FEA-04（SC-D02）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC3 draft owner**：同 Session 共享 + 单串行队列；跨 Session 只读/转移；文本冲突双方 `conflicted`；几何/样式同键后到覆盖且草稿阶段不产生新 revision（Q-10）（SC-D03）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC4 edit token 幂等/过期**：同 `(DraftId, DraftSequence)` → **不新增 revision**、返回同 `revisionIds`（含跨重启，见 AC15）；过期 → `EDIT_TOKEN_EXPIRED`（**过期先于 receipt 命中**，SC-D04）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC5 journal 崩溃恢复与原子性**：CRASH-A（tmp 前）→ 旧 journal 完整；CRASH-B（tmp 后 rename 前）→ 旧 journal 完整 + tmp 清理；CRASH-C（rename 后）→ 新 journal 完整；恢复 `active` 无 revision；损坏 → 丢弃提示；注入方式 = 单元级异常注入 + 集成级真实进程 kill 各一（SC-D05、R-JOURNAL-2/3）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC6 candidate-only prepare**：prepare 后指针不变；candidate 四字段；翻译产物先成 candidate；仅内存、跨命令可找回、跨重启不找回（R-CAND-2）（SC-D06/D07）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC7 统一事务 apply**：复用 `commit_region_batch`；保护/digest 检查在事务内；3 Region 第 3 个 stale → 全回滚；独立连接提交前不可见（SC-D08、R-APPLY-1）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC8 三锁 × 三域**：三条锁语义 + candidate/apply 两路径；`inpaint_locked` 不对 style 断言（SC-D09）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC9 style 白名单**：外键 → `STYLE_KEY_NOT_ALLOWED` 含键名；`translation_locked` 下 `font_size` 允许、`text_json` 拒绝；`text_color` 允许（SC-D10）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC10 protectionDigest**：三锁 + `text_json.translation_locked` + `text_json.manual_edited`；改任一位或锁 → digest 变化 → apply 拒绝 `LOCK_CHANGED`；不加列/错误码（SC-D12、Q-9）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC11 旧路径行为不变 + 新路径重放**：旧路径同文两次保存仍 2 revision（C073 保持）；新路径同 token 重放 → receipt 命中返回同 `revisionIds`、不新增；**旧→新（base 刷新为旧写入后的 current）** = 2 revision；**旧→新（base 未刷新）** = stale 拒绝、1 revision；**新→旧** = 2 revision（旧 append）；旧路径回归通过（C-13 v6、Q-6/Q-11、R-LEGACY-1/2）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC12 BRIDGE 收窄**：ApplicationCore 本地草稿缓冲（11 字段投影）+ 可注入 seam + 单串行队列 + flush 触发；不接线 Host/IPC；CORE 通过验收 + BRIDGE 完成后 Task 才可提交复核（Q-8、V24）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC13 回归**：基线 `python -m pytest tests/editing tests/infrastructure tests/core/test_region_write_commands.py tests/core/test_region_batch_locking.py -q` 逐文件 outcome 对照（`tests/domain` 当前不存在，由本卡新建，不计入基线）；新增测试文件 Handoff 登记。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC14 独立复核**：范围复核 r5 `approved`（P0/P1=0）；实现复核 `doc/reviews/FEA-03-r1.md` approved（含 Appointment）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC15 receipt + intent 跨重启幂等**：重启后同 token 重放 → 同 `revisionIds`、无第二 revision（receipt 命中或 R-APPLY-3 intent 兜底）；同 token 不同内容 → `EDIT_TOKEN_REUSED`；多序列各自可命中；receipt 清理不删 journal（R-RECEIPT-1/2/3、R-APPLY-3）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC16 活跃草稿登记与清理**：`edit-open` 登记 active；Session 结束无残留 journal；孤儿 `discarded`；receipt 保留至 Draft 清理（SC-D06、R-JOURNAL-5、R-RECEIPT-3；V25）。 <<PARTIAL: 范围冻结；实现未开始>>
- [ ] **AC17 journal 可写性与单写者**：data-root 不可写 → `DRAFT_JOURNAL_UNWRITABLE` 且内存草稿可编辑；第二实例被 `.lock` fail-closed；释放后第二实例可启动（R-JOURNAL-4、V22/V23）。 <<PARTIAL: 范围冻结；实现未开始>>

## L 前置适用性判定

| 保留项 | 判定 | 再触发 |
|---|---|---|
| **L-1** | **NOT_APPLICABLE**：文件 journal 不建表；不改 schema/migrations；`PageBindingVersion` 注入不透明整数 | 新增表/列/索引/迁移 → `blocked` |
| **L-2** | **NOT_APPLICABLE**：新错误码仅 Core 内部结构化返回（`assemble_production_core` 对象图，非 `CoreServiceServer` 命令面）；BRIDGE 不接线；不改 `allowedRunErrorCodes`（该白名单当前代码不存在） | 若从 `CoreServiceServer` 命令面暴露新码/新增命令 → `blocked`+M2-C1 |
| **L-5** | **NOT_APPLICABLE**：不触备份/恢复 | 触恢复/维护互斥 → `blocked` |

## 测试矩阵（V1–V25，planned）

| # | 场景 | 期望 | AC |
|---|---|---|---|
| V1 | 新建草稿 + 3 patch | 11 字段；序号 0→3 | AC1 |
| V2 | 主窗/浮窗同 Session | 同 DraftId | AC1 |
| V3 | 5 个 flush 触发点 | 各点持久化 | AC2 |
| V4 | flush 失败注入 | 缓冲未丢；`conflicted`；`DRAFT_FLUSH_FAILED` | AC2 |
| V5 | 两会话同 Region | 非 owner 只读；转移后原 owner 只读 | AC3 |
| V6 | 文本冲突 | 双方 `conflicted`；不自动合并 | AC3 |
| V7 | 几何/样式同键后到覆盖 | 文本未变、几何/样式更新、草稿阶段无新 revision | AC3 |
| V8 | 同 token 重放 ×2 | 不新增 revision；同 revisionIds | AC4 |
| V9 | 过期 token | `EDIT_TOKEN_EXPIRED`；无 revision | AC4 |
| V10 | CRASH-A/B/C（单元级异常注入 + 集成级真实进程 kill 各一；CRASH-C 时点 = rename 返回后、目录 fsync 前） | 旧或新 journal 完整；`*.tmp` 清理 | AC5 |
| V11 | 损坏 journal | 丢弃提示；不阻塞启动 | AC5 |
| V12 | prepare → 指针 | 不变；candidate 四字段 | AC6 |
| V13 | 翻译产物 vs 活跃草稿 | 产物为 candidate；指针未变 | AC6 |
| V14 | 3 Region apply 第 3 个 stale | 全回滚；独立连接不可见 | AC7 |
| V15 | 三锁 × 三域 | 同 SC-D09 | AC8 |
| V16 | style 白名单 | 拒绝含键名；真实键允许 | AC9 |
| V17 | 改锁 / 改 manual 位 | `LOCK_CHANGED` 拒绝 | AC10 |
| V18 | 旧路径同文两次 | 2 revision（C073 保持） | AC11 |
| V19 | 旧→新（base 刷新 / 未刷新）、新→旧 | base 刷新 = 2 revision；未刷新 = stale 拒绝 1 revision；新→旧 = 2 revision；旧路径回归通过 | AC11 |
| V20 | 重启后 token 重放（receipt 命中 / intent 兜底 / current 不匹配） | 命中分支：同 revisionIds；兜底分支：补 receipt 并同 revisionIds；不匹配分支：清 intent、视为未提交、重放写第 1 个 revision（不返回旧 id） | AC15 |
| V21 | 同 token 不同内容 / 多序列 / 过期重放 | `EDIT_TOKEN_REUSED`；各序列可命中；过期优先拒绝 | AC15 |
| V22 | data-root 不可写（chmod / ACL 拒绝 或挂载只读） | `DRAFT_JOURNAL_UNWRITABLE`；内存草稿可编辑 | AC17 |
| V23 | 双实例启动（两进程同 data-root；脚本化 spawn） | 第二实例 `.lock` fail-closed；释放后可启动 | AC17 |
| V24 | BRIDGE 草稿缓冲 | 11 字段投影；单串行队列；flush 触发；不接线；执行 `dotnet test apps/desktop-avalonia/tests/NewManga.ApplicationCore.Tests/NewManga.ApplicationCore.Tests.csproj`（或现存工程） | AC12 |
| V25 | 活跃草稿登记 / Session 结束 / 孤儿 / receipt 保留 | `edit-open` 登记 active；Session 结束无残留 journal；孤儿 `discarded`；receipt 按 R-RECEIPT-3 保留 | AC16 |

## 契约 deferral 登记

| 契约条款 | deferral 归属 | 说明 |
|---|---|---|
| C-13 `:94` 导出/删除 preflight 前必须 flush 或提示"有未保存草稿" | `FEA-14-EXPORT`（方案 `:707`/`:953`）+ 删除侧需 `CONTRACT-UNFREEZE-C04b` | 本卡不触 C-04b；只在 journal/草稿层提供可查询的"未保存草稿"状态 |
| C-13 SC-D02 的 UI 提示 | `FEA-04` | 本卡只保证结构化错误 |
| C-13 SC-D11 旧路径统一去重 | `FOLLOW-UP-FEA03-3`（C-13 v6 已承接） | 旧路径 C073 语义不变 |
| SC-D12 manual 位口径 | 本卡按 `text_json.translation_locked` + `manual_edited` 实现 | 不改 C-13 字节 |
## 禁止范围

- 不改冻结契约字节（15 份 pin）；不改 `schema.py`/migrations；不新增 wire 码/白名单；不触 C-04b/C-08。
- 不改 `apps/**` 其它面（仅 ApplicationCore 与对应测试）；不接线 Host/IPC/CoreClient。
- **不改旧保存路径实现**（C073 语义保持）；旧路径去重不在本卡实施（`FOLLOW-UP-FEA03-3`，C-13 v6 已承接）。
- 不动用户数据、不 push、不合并 main；不顺手修 FEA-04/07/10/12；不降低既有测试断言。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

实现尚未开始。开始时按 `Workspace Governance` 建 task-env/worktree（`feat/fea-03`）并补齐本表。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | - | NOT_APPLICABLE | - | - | 范围冻结；未访问用户数据 |
| build/temp（未来） | - | PENDING | ..\New Manga.workspace\ | - | 实现开始前补齐 |

## Closeout Record

- 2026-11-01：DSH 裁决释放（GOAL Q-1）；v1（`106299b50`）→ r1 changes_requested（P0×1/P1×7/P2×11）。
- 2026-11-01：v2（`dfa70c002`）→ r2 changes_requested（P0×1/P1×5/P2×12）。
- 2026-11-01：v3 处置：Q-11（SC-D11 去重键 deferral，解 P0-01）、R-APPLY-3（DB 去重兜底 receipt 崩溃窗口）、R-APPLY-2 重放优先、R-RECEIPT-1/2/3 多序列与清理、R-JOURNAL-4 改 OS 可写性 + 文件锁、Q-9 manual 位映射、AC17/V22/V23、AC12/V24、写域去掉 `core_service.py`。
- 2026-11-01：`proposed`，派独立复核 r3；通过前不 ready。
- 2026-11-01/02：v4：**C-13 经 [CONTRACT-UNFREEZE-C13-2026-11-01](../reviews/CONTRACT-UNFREEZE-C13-2026-11-01.md) 修订为 v6**（SC-D11 统一去重键限新 token 路径；pin `8faf1e80…`）；Q-9 manual 位改为三锁 + `text_json.translation_locked` + `text_json.manual_edited`；AC10/AC11/V19/R-LEGACY-3 按 v6 重写 → 解 r2-P0-01 与 r2-P1-05；范围复核 r3 送审（含 UNFREEZE 载体与 v6 字节）。
- 2026-11-01/02：v5：处置 r3（P0=0、UNFREEZE approved、P1×4/P2×12）——R-APPLY-3 改 journal intent 兜底（不再用 DB 内容去重）；AC11/V19 拆旧→新两子场景；R-RECEIPT-1 改 `revisionIds` 映射；AC16 补 V25；Q-11 标注 UNFREEZE approved。
- 2026-11-01/02：v6：处置 r4（P0=0 / P1×2 / P2×12）——统一 `revisionIds` 语义（AC4/AC15/V8/V20/V21/R-RECEIPT-2/R-LEGACY-2）；R-APPLY-3 强化（intent per-Region digest、current 守卫、失败清 intent、receipt 失败 fail-closed、页尺寸来源）；AC13 基线收窄（`tests/domain` 新建不计基线）；`rg` 排除定义；V10/V22/V23 注入方式；V24 加 .NET 命令；Q-9 digest 超集口径；新增「契约 deferral 登记」。
