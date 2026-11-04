---
id: FEA-11-SCAN-1
title: Source 后台定时扫描与调度（周期性扫描/资源预算/丢 hint 全量重枚举/通知消费）
kind: implementation
governance_version: 3
status: proposed
approval: 待独立 scope review（FEA-11 done 后派发）；承接 FEA-11 AC11-1 的定时扫描/后台调度延期项
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-SCAN-1
allowed_paths:
  - doc/tasks/FEA-11-SCAN-1.md
  - doc/reviews/FEA-11-SCAN-1-*.md
  - doc/handoffs/FEA-11-SCAN-1-*.md
  - verification/FEA-11-SCAN-1/**
  - src/application/sources/scheduler.py
  - src/application/sources/__init__.py
  - src/application/sources/ports.py
  - src/bootstrap/core_assembly.py
  - tests/fea11/test_source_scheduler.py
out_of_scope:
  - FEA-11 的 scan/diff/plan/apply 业务（复用其 service，不在本卡重写）
  - FEA-12/13/14 范围；冻结契约字节；共享组合根；真实用户数据/AppData/外部卷/回收站；push；新依赖
---
# FEA-11-SCAN-1：Source 后台定时扫描与调度

状态：**proposed**（待 FEA-11 done 后独立 scope review）；本卡承接 FEA-11 `AC11-1` 的"定时扫描生产者/后台调度"延期项（DSH 裁决见 `doc/reviews/FEA-11-appointment.md` §3.1）。

## 目标

在 FEA-11 三路（访问前检查、操作前强验证、watcher 消费者）之外，增加：

1. 后台**周期性扫描调度器**：按配置间隔触发（默认如 15 分钟；可配置/可暂停），复用 FEA-11 的 scan/diff 服务，只产生待处理通知/状态，不直接改 binding。
2. **资源预算与退避**：扫描不得阻塞 UI/前台操作；大源/慢磁盘使用限速/分批/退避；连续失败退避；
3. **丢 hint / overflow 兜底**：调度器启动与每周期做全量重枚举（与 watcher 协作去重）；
4. **通知消费**：调度结果进入 FEA-11 的 dirty/needs_attention 状态，由 UI（后续切片）或前台操作消费；通知本身不是唯一真值。

## 依赖

- FEA-11 done（scan/diff/plan/apply 服务、durable operation、notifications 数据结构；若 FEA-11 未冻结通知表，则本卡以 FEA-11 冻结的最小接口为限，不新增表）。
- C-15 §3.2 目录扫描/`SourceScanService`；C-17（若涉及新持久状态需先报 DSH 走契约变更，不得自行扩表）。
- 冻结契约：C-15 v1.1、C-17 v1.0、C-16 v1.1；不得改动其字节。

## Acceptance Criteria（草案，待 scope review 冻结）

- AC-S1 调度器生命周期：启动/暂停/恢复/关闭；间隔可配置（配置来源与默认值由 scope 冻结）；应用启动时可恢复；Core 重启后状态按 durable 事实恢复（不依赖内存）。
- AC-S2 触发与去重：周期触发调用 FEA-11 scan；与 watcher hint/访问前检查并发时去重/合并（同一源同一时刻最多一个扫描操作，durable 保证）；扫描不修改 binding，只更新通知/attention 状态。
- AC-S3 预算与退避：单周期扫描时间/IO 预算可配置；超预算分批并记录；连续失败指数退避；不阻塞前台操作（调度线程/队列与 API 隔离）。
- AC-S4 丢 hint/overflow 兜底：watcher 丢事件/overflow 后，调度器全量重枚举可发现并记录；与 FEA-11 AC11-1 断言衔接。
- AC-S5 通知/诊断：扫描结果产生可读的状态（源/目录/新增/缺失/变化计数与明细）；日志/诊断不泄露路径/凭据；Host/API 可查询最近一次扫描状态（closed shape 由 scope 冻结；如需 wire 命令先报 DSH）。
- AC-S6 证据与范围：真实链路（Core 定时器 + 真实 fixture 目录）测试；pytest/.NET 全量不减少；范围 0 域外；check/pins 通过。

## 验证矩阵（草案）

| AC | 测试/命令 | 证据 |
|---|---|---|
| AC-S1/S2 | `tests/fea11/test_source_scheduler.py`；真实 Core 装配 | `verification/FEA-11-SCAN-1/logs/` |
| AC-S3/S4 | 预算/退避/overflow 注入测试 | 同上 |
| AC-S5 | 通知/诊断查询（真实 IPC 或 seam） | 同上 |
| AC-S6 | 全量回归 + check/pins | EV/Handoff |

## 边界

- 不重写 FEA-11 scan/diff/plan；不新增数据库表（如需新持久状态先报 DSH）；不改 UI（UI 消费后续切片）；不做 FEA-12/13/14。
- 真实扫描 fixture 只用 `G:/CODEX/New Manga.workspace/FEA-11-SCAN-1/` 下合成目录，不碰真实用户数据。

## Closeout Record

- 未开始（proposed；待 FEA-11 done 后 scope review/Appointment）。
