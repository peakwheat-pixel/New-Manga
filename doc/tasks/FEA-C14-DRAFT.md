---
id: FEA-C14-DRAFT
title: C-14 起草（D05 剩余范围：重定位/同步 + 容器页映射 + 缓存边界缺失子面）
kind: contract
governance_version: 3
status: done
approval: user_ruling_2026-11-01_C14_new_contract
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-GOV-11
base_commit: 5add23956
branch: null
worktree: null
integration_commit: ff432e97c
delivery_head: e35f37603
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-C14
allowed_paths:
  - doc/tasks/FEA-C14-DRAFT.md
  - doc/plan/FEA-C14_SOURCE_RELOCATION_DRAFT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C14.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/**
  - doc/reviews/FEA-C14-*.md
  - verification/FEA-C14/**
---

# FEA-C14-DRAFT：C-14 起草（D05 剩余范围）

## 来源

用户 2026-11-01 裁决：**新建 C-14 承载 D05 剩余范围，保留 C-06 的冻结字节**。

`G-CONTRACT` 的关闭条件 = D05 的**全部**「必须冻结」项都有承载契约。D05 共五项（FEA-00 §13.2 `:768`）：

| # | D05 必须冻结 | 已有承载 | 状态 |
|---|---|---|---|
| 1 | 持久身份与授权分离 | **C-06**（`identityFacts` + `grant`） | ✅ 已冻结 |
| 2 | scope / version / lease | **C-06**（grant `scope{sourceId,version,entry,rendition}`）+ **C-01b**（SC-25/29/31 的 lease） | ✅ 已冻结 |
| 3 | **重定位 / 同步** | **无** | ❌ **本 Task 目标** |
| 4 | **容器页映射** | **无**（C-06 只到 entry 授权，未定义容器内页 ↔ `PageId` 的映射与身份） | ❌ **本 Task 目标** |
| 5 | 缓存边界 / 资源上限 | **部分**（逐条见下） | ⚠ **部分** |

**第 5 项逐条证明**（用户 2026-11-01 要求：不能只写「留给 C-09」——C-09 自身要求两 Gate 先关闭，会形成循环）：

| 子面 | 承载条款 | 状态 |
|---|---|---|
| **单次读取预算**（字节/解码尺寸上限，超限拒绝不截断） | **C-06 `:64`** 第 7 条 `budget{maxBytes,maxDecodeBytes}` | ✅ 已冻结 |
| **可再生产物定义 + cache key**（含 `SourceVersion`/entry/decoder 版本/参数） | **C-01b SC-02** | ✅ 已冻结 |
| **缓存 vs 非缓存边界**（处理结果/人工版本/恢复文件不得按缓存清理） | **C-01b SC-03** | ✅ 已冻结 |
| **两通道隔离**（`user-source` 不得进 derived-cache grant） | **C-01b SC-20** + **C-06 `:65`** | ✅ 已冻结 |
| **淘汰策略**（何时清、清多少、顺序、LRU 还是别的） | 无 | ❌ **C-14 覆盖** |
| **持久化**（缓存是否跨会话保留、存放位置、崩溃后一致性） | 无 | ❌ **C-14 覆盖** |
| **全局资源上限**（总缓存字节上限、并发解码数、与其它任务的配额关系） | 无 | ❌ **C-14 覆盖** |

**因此 C-14 覆盖第 3、4 项 + 第 5 项的三个缺失子面**；第 1/2 项与第 5 项已承载的四个子面**引用 C-06/C-01b，不复写**（避免双权威）。

## 验收标准

- [x] **AC1 覆盖矩阵**：`doc/plan/FEA-C14_SOURCE_RELOCATION_DRAFT.md` 的首节含上表（D05 原始要求 → 已有条款 → 缺失条款 → 验收方式），并与 C-06 冻结记录的「D05 授权面子集」表述**无冲突**。 <<MET>>
- [x] **AC2 重定位/同步条款**：定义 relink（改名/移动）与 repoint（改引用目标）两种操作、`source_sync_plans` 的 diff → 预览 → 确认 → 应用语义、`page_bindings` 的 generation 与 `acceptedSourceVersion`、失败/冲突路径（方案 `:432`/`:459`/`:461`）。 <<MET>>
- [x] **AC3 容器页映射条款**：定义 `source_entries` 的 locator（PDF 页码 / ZIP 成员名）与**永久身份**的区分、稳定排序键、encoded/pixel digest、容器内容变更时的健康判定（方案 `:419`/`:461`）。 <<MET>>
- [x] **AC4 跨契约一致性**：与 C-01b（SC-21/22 源表、**SC-02/SC-03/SC-20 缓存条款**）、C-06（grant scope + per-request 预算）、C-04b（删除 preflight 的源引用）逐条对表，无冲突。 <<MET>>
- [x] **AC5 缓存边界条款**：定义淘汰策略（触发条件/清理顺序/上限）、持久化（跨会话/位置/崩溃一致性）、全局资源上限（总字节/并发解码数）；**不得与 C-01b SC-02/SC-03/SC-20 冲突**。 <<MET>>
- [x] **AC6 独立复核**：r1 `changes_requested`（5 P1 + 4 P2）→ r2 `approved`（`doc/reviews/FEA-C14-r2.md`，P0/P1 = 0）后由 DSH 冻结。 <<MET>>

## 禁止范围

- **不改 C-06 冻结字节**（用户明确要求保留）；若发现 C-06 与本节冲突 → 走 `CONTRACT-UNFREEZE-C06-<DATE>.md`。
- 不改代码、不动用户数据、不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 覆盖矩阵 vs C-06 冻结记录对表 | 文档 | NOT_RUN（本收口不重跑条款级对照） | r1→r2 复核链（`doc/reviews/FEA-C14-r1.md` / `-r2.md`） |
| AC2 | 条款 vs 方案 `:432`/`:459`/`:461` | 文档 | NOT_RUN（本收口不重跑条款级对照） | 同上 |
| AC3 | 条款 vs 方案 `:419` 与 `schema.py` source 表 | 文档 | NOT_RUN（本收口不重跑条款级对照） | 同上 |
| AC4 | 四契约交叉对表 | 文档 | NOT_RUN（本收口不重跑条款级对照） | 同上 |
| AC5 | 缓存边界条款 vs C-01b SC-02/03/20 | 文档 | NOT_RUN（本收口不重跑条款级对照） | 同上 |
| AC6 | 独立复核 `approved`（P0/P1 = 0） | 只读 | PASS | `doc/reviews/FEA-C14-r2.md` frontmatter：`approved` / 0 / 0；r1 为 `changes_requested`（5 P1 / 4 P2，已在 v2/v3 处置） |

> AC1–AC5 的**条款级语义验证**由 C-14 的 r1（发现 5 P1 / 4 P2）→ r2（9 处处置 `approved`）复核链完成，属本轮之前的历史证据；**本收口没有重跑这些文档对照**，故按红线保留 `NOT_RUN`。本收口实际执行的是证据复算、AC6 事实更正与治理检查。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-C14-R1 | AC1–AC5 | `doc/reviews/FEA-C14-r1.md` | `172eae3c8` | `b91014b36609bc3fad52ed07db6d50ec1dd5469f6c6101976c91fdeab67abe66` | CANONICAL |
| E-C14-R2 | AC1–AC6 | `doc/reviews/FEA-C14-r2.md` | `e35f37603` | `69ff58bf599bf5c468c49d624919f04881a67b913e0af4daf3e19bb4c42ca70a` | CANONICAL |
| E-C14-FROZEN | AC6 | `doc/plan/FEA-CONTRACT-FROZEN-C14.md` | `e35f37603` | `a34d0f2a8fc84a5b74694efc51d5ca6f95f215bbc57249cb319764bf16ee8ae7` | CANONICAL |
| E-RES-C14 | Res/Closeout | `verification/FEA-C14/closeout-note.md` | `-` | `8cf2deb6b198a8f4072eb3dcfa0ea232dfe517f999f71e61bf62f1225f475907` | CANONICAL |

## Resource Manifest

文档 Task：仓库内无 worktree、无 task-env、无构建产物。仓外一次性脚本与 D06 共用同一批残留（`G:\CODEX\New Manga.workspace\tmp\`，本线相关 3 项：`fix_c14_r1.py` / `fix_c14_r2.py` / `c14_sha.txt`），逐项 sha256 见共享清单 `verification/FEA-D06-GAP/workspace-tmp-manifest.md`（第 18–20 行），处置 `PRESERVE_UNKNOWN`（原地保留，不删除：删掉会降低冻结字节可复现性）。

**偏离登记**：用户口头要求「Resource Manifest 用纯文本、不建表」；但 `check.ps1` 对 `done` Task 只接受非空 6 列表或 `verification/**` 单个 JSON，「纯文本无表」不可满足。故保留纯文本说明 + 真实表格（不虚构路径/哈希）；如需纯文本口径须另立 governance Task 改检查器。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | - | NOT_APPLICABLE | - | - | 仓库内无 worktree/task-env/artifact/build/temp；未访问用户数据 |
| temp-scripts | ..\New Manga.workspace\tmp | PRESERVE_UNKNOWN | ..\New Manga.workspace\tmp | verification/FEA-D06-GAP/workspace-tmp-manifest.md | 共享清单 32 项（本线 3 项）；无进程占用、不在 git 跟踪内；delete/move/migrate/archive 均为 0 |

## Closeout Record

- 2026-11-01 / DSH：C-14 冻结于 `e35f37603`（v3，r2 approved）；`G-CONTRACT` 据此关闭。AC1–AC6 全部 `<<MET>>`。
- 收口（2026-11-01）：`status: in_review` → 待独立复核 `doc/reviews/FEA-C14-CLOSEOUT-r1.md`；`delivery_head` = `e35f37603`（契约冻结/交付提交）；`integration_commit` 与 `resource_closeout_status: complete` 在复核通过后的 `done` 提交回填。
- **事实更正**：原 AC6 写「r1 `approved`」与事实不符（r1 为 `changes_requested`：5 P1 + 4 P2；r2 才 `approved`），本收口更正为 r1→r2 链并在此留痕（不改变结论与冻结字节）。
- 证据口径：4 条 Canonical Evidence 的 path/commit/sha256 已逐项实核（worktree 与对应 commit blob 同 hash）；`E-RES-C14` 为仓内说明文件，按 worktree sha256 校验（`-` commit，符合 `check.ps1` 规则）。
- 未跑项：AC1–AC5 的条款级对照本收口未重跑，保持 `NOT_RUN`；未运行任何程序测试（纯文档 Task）。
- 资源：仓库内无资源；仓库外 3 项纳入共享清单 `PRESERVE_UNKNOWN`；未访问用户数据。
- 边界：不构成实现授权；不构成远端 push 授权；不改变任何冻结契约字节（`verify_pins.ps1` 13/13）。
- 收口（2026-11-01）：R1 [approved](../reviews/FEA-C14-CLOSEOUT-r1.md)（P0/P1 = 0；P2×6 非阻断）；`status: done`、`integration_commit: ff432e97c`、`resource_closeout_status: complete` 为**纯元数据回填**（未改 AC / 证据表 / 资源清单正文）；P2 技术债登记于 `doc/checkpoints/AUTONOMOUS-2026-11-01.md`。
