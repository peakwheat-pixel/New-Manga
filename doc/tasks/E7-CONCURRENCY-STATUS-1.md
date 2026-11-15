---
id: E7-CONCURRENCY-STATUS-1
title: 精确核实 E-7 并发项的当前状态并更正过时表述
kind: governance
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: e7-status-review-r2（独立上下文子 agent，APPROVED_WITH_LIMITATIONS；r1 为 CHANGES_REQUESTED）
integration_commit: 08758dbec
canonical_evidence_status: complete
resource_closeout_status: complete
depends_on:
  - PIPE-EXCLUSIVE-TRANSPORT-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；目标 B 的产品门槛收敛
base_commit: 649e520b7
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/E7-CONCURRENCY-STATUS-1
allowed_paths:
  - doc/tasks/E7-CONCURRENCY-STATUS-1.md
  - doc/reviews/E7-CONCURRENCY-STATUS-2026-11-16.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/E7-CONCURRENCY-STATUS-1/**
---

# E7-CONCURRENCY-STATUS-1：E-7 现状精确核实

## 动机

`PIPE-EXCLUSIVE-TRANSPORT-1`（status `done`）的 AC1/AC2/AC4/AC5 标为 `[~]`（PARTIAL/NOT MET），
此后多份文档沿用「**E-7 仍有 5 项开放、并发安全不可宣称**」的表述，并据此把并发安全列为产品门槛。

但本轮读代码发现：**至少 2 项已修**（`HostBridgeClient` 已用传输层 lease；`SendRawAsync` 已在 `_pipeGate` 内），
卡面 `[~]` 信息**已过时**。在动手修并发代码之前，必须先确认「到底还差什么」——
并发缺陷是「改了看不见」的典型，基于过时信息动手风险很高。

## 目标（一个可观察结果）

一份逐项核实的报告：E-7 五项各自的**代码位置 + 判定**（已修 / 架构未统一 / 设计如此 / 真缺口），
并据此给出按价值排序的真实剩余工作。

## Acceptance Criteria

- [x] **AC1 逐项核实**：对 E-7 五项各给出①卡面表述②代码文件:行③判定 <<MET>>
      （已修/部分/仍开），不得只凭 grep 关键词下结论。
- [x] **AC2 澄清关键机制**：说明 `SidecarProcess.ExchangeAsync` 本身不加锁、 <<MET>>
      独占须由调用方持 lease —— 这是理解 a/b/c 三项的前提。
- [x] **AC3 对照权威枚举**：以 `PIPE-EXCLUSIVE-TRANSPORT-1.md:123-129` 与 `MAINT-1-EXISTING-FINDINGS-2026-11-14.md:162-168` 的权威 5 项为准，逐条核实其当前状态；**不得**从卡面 `[~]` 行反推清单。（初版曾误判「5 项不准确、实为 3 项」而被 r1 复核推翻，见报告 §4。） <<MET>>
- [x] **AC4 排序真实剩余工作**：对权威 5 项按风险给出 P1/P2/P3 与建议范围，**必须包含 R-005（取消失步）与 Dispose/StopAsync 在租约外**两项。 <<MET>>
- [x] **AC5 记录自我更正**：如实记录本轮两次误判 —— ①grep 无 `lock` 便判 `HostBridgeClient` 无锁；②把卡面 `[~]` 行当成「5 项」从而错误宣称「实为 3 项」。并归纳可执行纪律。 <<MET>>
- [x] **AC6 不回归**：`check.ps1` PASS；`verify_pins` 18/18；`api_inventory` 1/80/6=87。 <<MET>>

## 允许修改范围

见 frontmatter `allowed_paths`。**本轮不修改任何 `.cs` 生产代码**（只核实与更正文档）。

## 禁止范围

- 不得为「让状态好看」而把仍开的项写成已修；
- 不得修改 `PIPE-EXCLUSIVE-TRANSPORT-1` 历史卡面（它是当时的真实记录）；
- 不得声称「并发安全已达成」—— 本卡只做状态核实。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-E7S-01 | AC1-AC5 核实报告 | doc/reviews/E7-CONCURRENCY-STATUS-2026-11-16.md | 4f3cad45b | ad1e89d9e537064d2530cbb8bd99ed2aa6654167643772c041f1e70d95b39643 | CANONICAL | BLOB |
| EV-E7S-02 | AC1 代码摘录（.cs 自 base 起未改） | verification/E7-CONCURRENCY-STATUS-1/code-excerpts.txt | 4f3cad45b | c7e4fcb7c7bcab30b4236031fecec748ca0f4052dcc4367f57a0be4d7b2ac839 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/E7-CONCURRENCY-STATUS-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-16，DSH；实现 `f8b7fd7ec`，r1 返修 `08758dbec` + `4f3cad45b`，r2 P3 处置（本提交）。
- **结果**：**权威 5 项全部仍开**，「E-7 仍有 5 项开放、并发安全不可宣称」在本 head 上**准确**。
  初版曾错误宣称「不是 5 项而是 1+1+1」，被 r1 复核推翻并重写。
- **5 项（权威枚举 `PIPE-EXCLUSIVE-TRANSPORT-1.md:123-129` / `MAINT-1:162-168`）**：
  1. `CoreServiceClient` 仍用 `_pipeGate`、`ExchangeAsync` 仍 `public`；
  2. 无 `request_id` 时 fail-open（生产路径 `EnsureResponseBelongsToRequest` 放过）；
  3. R-002 错配无重同步（`:2408-2413` 抛错即 off-by-one）；
  4. **R-005 取消失步**：`SidecarProcess.cs:250-252`/`:310-312` 的 poison 只在超时分支，主动取消不置；
  5. **`Dispose`/`StopAsync` 在租约外**（`CoreServiceClient.cs:2629-2630`）。
- **独立复核两轮**：
  - r1 `CHANGES_REQUESTED`（0/1/3/4）—— 抓出**枚举方向反了**（我用了卡面 `[~]` 行而非权威枚举）、
    d 证据错位（引测试钩子注释论证生产路径）、AC2 误读；确认 a/b/c/e 与「ExchangeAsync 不加锁」准确。
  - r2 **APPROVED_WITH_LIMITATIONS**（0/0/0/2）—— r1 的 P1/P2-01/P2-02/P2-03 全部关闭；
    剩 2 个 P3（证据 head 未同步、§5 缺建议列）已在本收口处置。
- **门禁**：`check.ps1` PASS (3 warnings)｜`verify_pins.ps1` PASS (18/18)｜
  `generate_api_inventory.py --check` OK (1/80/6=87)。
- **本轮未改任何 `.cs`**（只核实与更正文档）。
- **下一轮入口（报告 §5）**：P1 = R-005 与 R-002（统一 poison + 有界 drain），
  P2 = Dispose 纳入租约、`_pipeGate` 统一到 lease，P3 = fail-open 契约判定。
- **自我更正记录**：本轮出现**两类**误判 —— ①grep 无 `lock` 判 `HostBridgeClient` 无锁（实为 lease）；
  ②把卡面 `[~]` 行当「5 项」枚举（实为权威枚举在另一处）。纪律：**复述「N 项」必须先定位定义处逐条对照**。
