---
id: FEA-00A-IMPL-1
title: FEA-00a 数据安全修复（prepare 与 seam 分离；region + artifact 零变化）
kind: implementation
governance_version: 3
status: proposed
approval: user_ruling_2026-11-01_D1_D4
suggested_owner: codex
owner: codex
reviewer: c01b-reviewer
depends_on:
  - FEA-00A-PREP-1
base_commit: 6b8469a80
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-00A-IMPL-1
allowed_paths:
  - doc/tasks/FEA-00A-IMPL-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/**
  - doc/reviews/FEA-00A-IMPL-*.md
  - doc/reviews/ADJ-2026-11-01-FEA-DECISIONS.md
  - doc/handoffs/FEA-00A-IMPL-*.md
  - src/infrastructure/providers/**
  - src/infrastructure/sqlite/pipeline.py
  - src/application/tasks/**
  - tests/**
  - verification/FEA-00A-IMPL-1/**
---

# FEA-00a 数据安全修复（范围已冻结，待独立复核 → ready → Codex 实现）

## 来源

1. 方案 §15.5 硬验收（候选 `FEA-00a`：seam 失败/冲突/暂停/取消/崩溃时 `regions.text_json`、`current_revision_id`、`region_revisions` 行数三处零变化）。
2. 只读评估 [`FEA-00A_PREP.md`](../plan/FEA-00A_PREP.md)（缺口 G1–G7、A1–A7 断言、V1–V8 矩阵）+ 独立复核 [`FEA-00A-PREP-r1`](../reviews/FEA-00A-PREP-r1.md) `approved`（P0/P1=0，P2×6 已处置）。
3. **用户 2026-11-01 裁决 D1–D4**（[ADJ U-13](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md)）：D1=②、D2=②、D3=①、D4=L2 + 真实生产 assembly。

## 用户裁决落盘（本卡范围的唯一依据）

| # | 用户裁决 | 对本卡的约束 |
|---|---|---|
| **D1** | **② 一起修**：region 与 artifact（`media_artifacts.current_revision_id`、`publish` 的 `artifact_revisions` 行/落盘文件）同类缺陷一并修 | AC6 生效；覆盖 `handlers.py` 的 `adopt_current` 调用点与 `publish` 的 prepare 写面 |
| **D2** | **② 允许改** `src/application/tasks/service.py`；**必要情况下允许重新设计构件** | 写域含 `src/application/tasks/**`；任何构件重设计须在 Handoff 逐项写明理由、影响面与回退，且**不得扩张到 FEA-10 的其它功能** |
| **D3** | **① 复用** `step_result_candidates`（不新增 schema、不建迁移） | 禁改 `schema.py` / migrations；`prepared`/`abandoned` 语义与清理归属按评估 §4.2 落实 |
| **D4** | **L2 自动化 + 真实生产 assembly 跑一遍** | V1–V8 全部从真实生产 assembly 执行 prepare；不得用 fake executor 代跑 |

## 范围（写域，workspace-relative）

- **Python Core（唯一实现面）**：`src/infrastructure/providers/**`（`step_writes.py` region 与 artifact 写面、`handlers.py` adopt 调用点及必要上下文）、`src/infrastructure/sqlite/pipeline.py`（`commit_step` seam）、`src/application/tasks/**`（D2=② 授权的最小改动：token 解析、失败候选记录、staged 行清理归属）。
- **测试**：`tests/**` 中与本卡相关的测试文件（含评估 G7 的 8 个 blast-radius 文件）。
- **治理与证据**：本卡、`STATUS`、`REBASELINE_PLAN`、`TASK_LEDGER`、`doc/checkpoints/**`、`doc/reviews/FEA-00A-IMPL-*`、`doc/handoffs/FEA-00A-IMPL-*`、`verification/FEA-00A-IMPL-1/**`。
- **不改**：任何 `schema.py`/迁移帧（D3=①）、Avalonia 侧（`apps/**`）、冻结契约字节（15 份 pin）、`G-DELETE-IMPL` 状态、其它 Task、用户数据。
- **不新增依赖、不改构建配置、不 push**。

## 验收标准（冻结版）

- [ ] **AC1 三处零变化**：revision 冲突 / Lock 冲突 / `STALE_RUN_SNAPSHOT` / DB 失败 / pause / cancel / prepare 后崩溃重启 7 类注入下，`regions.text_json`、`regions.current_revision_id`、`region_revisions` 行数与 prepare 前完全相同（A1、V1–V6）。 <<PARTIAL: 范围冻结；L2 注入测试待实现执行>>
- [ ] **AC2 候选可诊断**：失败候选可在 `step_result_candidates` 查询（`reason`/`status`/`base_revision_id`/`payload_json` 正确）；`prepared` 与失败候选的语义、清理归属、`abandoned` 扫除点按评估 §4.2 落实（A2）。 <<PARTIAL: 范围冻结；待实现>>
- [ ] **AC3 成功同事务**：revision 行 + `text_json` + 指针 CAS + 候选 `resolved` 在同一事务提交；无「text 已变而指针未变」或反向的可观察中间态（A3、V7）。 <<PARTIAL: 范围冻结；待实现>>
- [ ] **AC4 prepare 不触 live**：结构/grep 断言 `step_writes.py` prepare 路径无 `UPDATE regions`/`media_artifacts`/`INSERT region_revisions`；token = prepare 预生成的真实 revision id（A4、§4.1）。 <<PARTIAL: 范围冻结；待实现>>
- [ ] **AC5 重启可判定**：prepare 后崩溃/重启，live 三处不变；`prepared` 行可识别为未完成并可重试或清理（A5、V6）。 <<PARTIAL: 范围冻结；待实现>>
- [ ] **AC6（D1=②）artifact 零变化**：`media_artifacts.current_revision_id` 与 `publish` 的 `artifact_revisions` 行/落盘文件同样先 staging，seam 成功时同事务 adopt（含 `handlers.py:962` 调用点，A6）。 <<PARTIAL: 范围冻结；待实现>>
- [ ] **AC7 §15.6 出口**：①关闭新写入入口（修复后 prepare 路径无 live 写，结构断言覆盖）；②旧库只读核验三处一致性与候选可读，**保留备份与候选不删除**，证据入 `verification/`（A7）。 <<PARTIAL: 范围冻结；待实现>>
- [ ] **AC8 回归与真实 assembly**：评估 G7 的 8 个 blast-radius 测试文件 outcome 逐项对照（是否本应保持 live 语义）；全部 V1–V8 从真实生产 assembly 执行 prepare，不得用 fake executor（D4）。 <<PARTIAL: 范围冻结；待实现>>
- [ ] **AC9 D2=② 改动登记**：若改动 `src/application/tasks/**`，Handoff 须逐项列出「为什么必须改 / 不改的替代方案 / 影响面 / 回退方式」；构件重设计须附前后接口对照。 <<PARTIAL: 范围冻结；待实现>>
- [ ] **AC10 独立复核**：范围冻结复核 `doc/reviews/FEA-00A-IMPL-scope-r1.md` 判 `approved`（P0/P1=0）；实现复核 `doc/reviews/FEA-00A-IMPL-r1.md` 判 `approved`（P0/P1=0）。 <<PARTIAL: 范围复核待派发；实现复核在交付后>>

## L 前置适用性判定（按实际写域，不机械复制）

| 保留项 | 是否触及 | 判定 | 再触发条件 |
|---|---|---|---|
| **L-1** 四表 DDL 未冻 | 否——D3=① 复用既有 `step_result_candidates`，不新增表/列/迁移 | **NOT_APPLICABLE**（本卡） | 若实现需要改 `schema.py`/migrations/新增暂存表 → 立即 `blocked`，先完成 L-1 前置 |
| **L-2** M2-C1 字节修订 | 否——不新增/修改 wire 码表与白名单；复用既有 `StepResult.revision_updates` 通道 | **NOT_APPLICABLE**（本卡） | 若引入新错误码或改 host 投影白名单 → `blocked`，先完成 M2-C1 独立字节修订 |
| **L-5** 整库恢复独占锁 | 否——不触备份/恢复/维护窗口 | **NOT_APPLICABLE**（本卡） | 若触及恢复或维护互斥 → `blocked`，按 L-5 四步序列补 AC |

> `doc/plan/FEA-C11_IMPL_PREREQS.md` §0 禁则适用：不适用不等于豁免。

## 测试矩阵（冻结版，全部 planned）

| # | 注入 | 期望 | 证据目标 |
|---|---|---|---|
| V1 | seam 前 revision 冲突（`input_revision_changed`） | AC1 + AC2；无 live 写 | `verification/FEA-00A-IMPL-1/` |
| V2 | Lock 冲突（`lock_changed`） | AC1 + AC2 | 同上 |
| V3 | `STALE_RUN_SNAPSHOT` | AC1；Run 不半写 | 同上 |
| V4 | DB 失败（seam 事务抛错） | AC1；整体回滚 | 同上 |
| V5 | pause / cancel（prepare 后、seam 前） | AC1；候选保留可诊断 | 同上 |
| V6 | prepare 后进程崩溃 + 重启 | AC1 + AC5 | 同上 |
| V7 | 成功路径 | AC3；三处与 Run receipt 同事务一致 | 同上 |
| V8 | 并发：两个 prepare 同 region | V1 语义 + 不互相污染 | 同上 |
| V9 | artifact 指针（D1=②） | AC6；失败零推进、成功同事务 adopt | 同上 |

计划命令：`python -m pytest tests/... -q`（具体文件与用例名在实现后冻结）+ 真实生产 assembly 执行脚本；结果须分列 passed/failed/skipped 并逐项记录 skip 原因。

## 禁止范围

- 不改冻结契约字节（15 份 pin）；不改 `G-DELETE-IMPL` 状态；不动用户数据；不 push。
- 不改 schema / 不建迁移（D3=①）。
- 不顺手修 FEA-03/FEA-10 的其它功能；不释放其它实现 Task。
- 不以 fake executor / 桩替代真实生产 assembly。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

实现尚未开始：仓库内无 worktree、无构建产物；实现开始后按 `Workspace Governance` 在 `G:\CODEX\New Manga.workspace\` 建 task-env 并在本表补齐逐项处置。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | - | NOT_APPLICABLE | - | - | 范围冻结阶段；未访问用户数据 |
| build/temp（未来） | - | PENDING | ..\New Manga.workspace\ | - | 实现开始前补齐具体路径与处置 |

## Closeout Record

- 2026-11-01：`proposed`（评估已完成，等用户拍板 D1–D4）。
- 2026-11-01（用户在线裁决 D1–D4）：D1=② region+artifact 一起修；D2=② 允许改 `src/application/tasks/service.py`，必要时可重新设计构件；D3=① 复用 `step_result_candidates`；D4=L2 + 真实生产 assembly。DSH 据此**冻结范围**（写域、AC1–AC10、V1–V9、L 判定），`base_commit: 6b8469a80`。
- 2026-11-01：置 `proposed`（范围冻结稿完成，**未释放**）；派上下文独立复核审查本范围冻结（`doc/reviews/FEA-00A-IMPL-scope-r1.md`）；复核通过前不 `ready`、不派实现。
