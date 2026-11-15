---
id: E7-CONCURRENCY-STATUS-1
title: 精确核实 E-7 并发项的当前状态并更正过时表述
kind: governance
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
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

- [ ] **AC1 逐项核实**：对 E-7 五项各给出①卡面表述②代码文件:行③判定
      （已修/部分/仍开），不得只凭 grep 关键词下结论。
- [ ] **AC2 澄清关键机制**：说明 `SidecarProcess.ExchangeAsync` 本身不加锁、
      独占须由调用方持 lease —— 这是理解 a/b/c 三项的前提。
- [ ] **AC3 对照权威枚举**：以 `PIPE-EXCLUSIVE-TRANSPORT-1.md:123-129` 与 `MAINT-1-EXISTING-FINDINGS-2026-11-14.md:162-168` 的权威 5 项为准，逐条核实其当前状态；**不得**从卡面 `[~]` 行反推清单。（初版曾误判「5 项不准确、实为 3 项」而被 r1 复核推翻，见报告 §4。）
- [ ] **AC4 排序真实剩余工作**：对权威 5 项按风险给出 P1/P2/P3 与建议范围，**必须包含 R-005（取消失步）与 Dispose/StopAsync 在租约外**两项。
- [ ] **AC5 记录自我更正**：如实记录本轮两次误判 —— ①grep 无 `lock` 便判 `HostBridgeClient` 无锁；②把卡面 `[~]` 行当成「5 项」从而错误宣称「实为 3 项」。并归纳可执行纪律。
- [ ] **AC6 不回归**：`check.ps1` PASS；`verify_pins` 18/18；`api_inventory` 1/80/6=87。

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

## 证据

核实报告 `doc/reviews/E7-CONCURRENCY-STATUS-2026-11-16.md`。
