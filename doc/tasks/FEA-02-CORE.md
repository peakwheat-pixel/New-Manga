---
id: FEA-02-CORE
title: FEA-02-CORE 共享应用状态与 Run 轮询基础（ApplicationCore 抽取）
kind: implementation
governance_version: 3
status: proposed
approval: user_ruling_2026-11-01_U12
suggested_owner: codex
owner: codex
reviewer: c01b-reviewer
depends_on:
  - FEA-01-FREEZE-1
blocked_by:
  - FEA-01-FREEZE-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-02-CORE
allowed_paths:
  - doc/tasks/FEA-02-CORE.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/**
  - doc/reviews/FEA-02-CORE-*.md
  - apps/desktop-avalonia/src/NewManga.ApplicationCore/**
  - apps/desktop-avalonia/tests/**
  - verification/FEA-02-CORE/**
---

# FEA-02-CORE：共享应用状态与 Run 轮询基础

## 来源与定位

用户 2026-11-01 追加确认（[ADJ 追加裁决](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md) U-12）：**首个实现候选 = `FEA-02-CORE`，由 Codex 承担实现；DSH 负责范围冻结、Review Appointment 与集成。** 选择理由：适合先建立**共享应用状态、意图去重与 Run 轮询基础**；`FEA-03` 额外依赖 `FEA-00a` 数据安全修复，应后置（方案 `:640` 候选依赖）。

**门禁**：FEA-01 稳定端口冻结（[FROZEN v2](../plan/FEA-CONTRACT-FROZEN-FEA01.md)，pin `0370c189…`；任务 `FEA-01-FREEZE-1`）→ 本卡范围冻结 + 独立复核 → `ready` → Codex 实现。

## 范围（范围冻结核心）

- **写域（唯一）**：`apps/desktop-avalonia/src/NewManga.ApplicationCore/**` + `apps/desktop-avalonia/tests/**`（仅与 ApplicationCore 相关的测试文件）。
- **保留 Current 入口**：现有入口/调度路径**不得删除、不得改变行为**；新实现只能作为可替换层接入（方案 §15.6 FEA-02-CORE 的「保留 Current 原入口；不得双调度」）。
- **不写**：`apps/desktop-avalonia/src/NewManga.App/**` 其它目录、`NewManga.CoreClient/**`、`src/**`（Python）、契约文档、其它 Task 文件。
- **共享组合根**：如需改动组合根/DI 注册，必须先在卡内列出精确文件与理由，经 DSH 范围确认后另批提交（不在默认写域内）。

## 验收标准（草案；范围冻结时以用户确认版本为准）

- [ ] **AC1 无 Avalonia 依赖**：`NewManga.ApplicationCore` 不引用 Avalonia 程序集（架构测试/编译期断言：程序集引用清单不含 `Avalonia*`；方案 §15.6 出口「无 Avalonia 引用」）。
- [ ] **AC2 多观察者共享一次轮询**：N 个观察者同时订阅同一 Run/任务状态 → 断言只发生 **1 次**底层轮询（调用计数断言），观察者各自收到同一快照。
- [ ] **AC3 同一意图重试不重复启动**：同一意图键（intent key）在 pending/重试期间的重复请求 → 断言不产生第二个启动（去重命中，返回同一 in-flight 结果）；意图完成后允许新意图。
- [ ] **AC4 请求错误互不串扰**：并发多个请求，其中一个失败（含超时/取消）→ 断言错误只归属该请求（request-scoped error），其它请求结果与状态不受影响，且不污染共享状态缓存。
- [ ] **AC5 保留 Current 入口（非回归）**：现有入口仍可用、行为等价（对照基线测试）；无「双调度」（同一意图不得同时经两条路径启动）。
- [ ] **AC6 L 前置适用性判定**：按**实际写域**逐项判定 L-1/L-2/L-5（见下节），判定结论与再触发条件写入本卡；前置未满足时本卡保持 `proposed/blocked`。
- [ ] **AC7 独立复核**：`doc/reviews/FEA-02-CORE-r1.md` 判 `approved`（P0/P1 = 0）。

## L 前置适用性判定（用户要求：按实际写域判定，不机械复制）

| 保留项 | 本卡写域是否触及 | 判定 | 依据 / 再触发条件 |
|---|---|---|---|
| **L-1** 四表 DDL 未冻 | **否**——本卡只做 Avalonia 侧 ApplicationCore 内存状态/轮询/去重；不访问 SQLite、不定义 schema | **NOT_APPLICABLE**（本卡） | 若实现新增任何 DB/schema 访问 → 立即转 `blocked`，并先完成 L-1 前置（DDL 冻结 + pin） |
| **L-2** M2-C1 字节修订（`TRASH_*` 3 码 + Run 错误码白名单） | **否（边界）**——本卡消费既有 Run 错误语义，但**不新增/不修改 wire 码表，也不实现 host 投影白名单**（属 Host 层）；如需新增错误码 → 属 M2-C1 | **NOT_APPLICABLE**（本卡） | 若实现新增 `RUN_*`/`TRASH_*` 码或改主机白名单 → 转 `blocked`，先完成 M2-C1 独立字节修订 |
| **L-5** 整库恢复独占锁 | **否**——本卡不触及备份/恢复/维护窗口 | **NOT_APPLICABLE**（本卡） | 若实现触及恢复或维护互斥 → 转 `blocked`，先按 L-5 的 4 步序列补 AC |

> 说明：`doc/plan/FEA-C11_IMPL_PREREQS.md` §0 的禁则在此适用——**不适用不等于豁免**；一旦写域扩展到对应范围，立即转 `blocked` 并补前置。

## 首批验收聚焦（用户明确）

无 Avalonia 依赖 · 多个观察者共享一次轮询 · 同一意图重试不重复启动 · 请求错误互不串扰。

## 禁止范围

- 不改任何冻结契约字节（15 份 pin）；不改 `G-DELETE-IMPL` 状态；不动用户数据；不 push。
- 不删除/不改 Current 入口行为；不做双调度。
- 不在本卡内顺手修 `FEA-00a`（数据安全）或其它候选 Task 的问题。

## 测试要求（草案）

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 程序集引用断言/架构测试 | 本地构建 | NOT_RUN | 待实现后填 |
| AC2 | 观察者计数测试（N 观察者 → 1 次轮询） | 单测 | NOT_RUN | 待实现后填 |
| AC3 | 意图去重/重试并发测试 | 单测 | NOT_RUN | 待实现后填 |
| AC4 | 并发错误隔离测试 | 单测 | NOT_RUN | 待实现后填 |
| AC5 | Current 入口基线对照 | 回归 | NOT_RUN | 待实现后填 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

实现 Task（尚未开始）：仓库内无 worktree、无构建产物、无临时产物；开始时须按 `FEA-11` 口径另建 app 构建/temp 目录于 `G:\CODEX\New Manga.workspace\`。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | - | NOT_APPLICABLE | - | - | 尚未开始实现；未访问用户数据 |
| build/temp（未来） | - | PENDING | ..\New Manga.workspace\ | - | 实现开始前须补齐具体路径与处置 |

## Closeout Record

- 范围冻结中（2026-11-01）：卡为 `proposed`；待独立复核范围冻结后置 `ready` 并交 Codex。
