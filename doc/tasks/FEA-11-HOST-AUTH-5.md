---
id: FEA-11-HOST-AUTH-5
title: HostRuntime/dispatcher 全链路 e2e（原 FEA-11-HOST-AUTH-2 AC-F4；含 Core 覆盖 seam）
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡：由 `FEA-11-HOST-AUTH-2` Review r1（R1-P2-2）与 DSH 2026-11-08 裁决 re-home；**scope 未冻结，不得实施**；须先独立 scope review
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - FEA-11-HOST-AUTH-2
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-HOST-AUTH-5
allowed_paths:
  - doc/tasks/FEA-11-HOST-AUTH-5.md
  - doc/reviews/FEA-11-HOST-AUTH-5-*.md
  - doc/handoffs/FEA-11-HOST-AUTH-5-*.md
  - verification/FEA-11-HOST-AUTH-5/**
out_of_scope:
  - 未 scope review 前不得实施任何实现
---
# FEA-11-HOST-AUTH-5：HostRuntime/dispatcher 全链路 e2e（占位）

## 来源
`FEA-11-HOST-AUTH-2` 的 **AC-F4**（条件性 HostRuntime e2e）未做 → DSH re-home 到本卡；同时承接 `FEA-11-HOST-AUTH-1` **limitation 1**（HostRuntime e2e）的收窄口径。

## 已核实事实
- 打包 sidecar `core_service.exe` 实测 2026-10-23，**早于 C-17 v1.0**（`HostRuntime.cs:872-909`；`Fea11Scan2HostRuntimeTests.cs:20-24` 已记录），故覆盖 C-17 同步链需 **`HostOptions` 最小 Core 覆盖 seam**（约 4–6 行）。
- 仓内**无** `runtime.Commands.InvokeAsync` 全链路用例（register→scan→plan/preview/confirm→apply→ACK）。

## 验收（草案，待冻结）
- `HostRuntime.StartAsync` Ready（覆盖 seam）；`source.sync.apply/1` 能力存在（缺→**RED**，不得 skip 冒充）；
- 经生产 dispatcher 完成全链路；`Operations.Get(id).State==acknowledged`、gate 开、resolve 新键、源字节守恒、ACK wire 为 fresh；证据须显示测试**实际执行**（不是 skipped）；
- 打包 sidecar 腿单列 `NOT_RUN`（不得写成已覆盖）。
