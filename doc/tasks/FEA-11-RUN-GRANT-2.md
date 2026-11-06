---
id: FEA-11-RUN-GRANT-2
title: 容器成员 entry 授权通道（C-16 v1.4 + Core 多 entry 注册/匹配 + Host 铸 N 项；proposed，待依赖）
kind: implementation
governance_version: 3
status: proposed
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；scope review `doc/reviews/FEA-11-RUN-GRANT-2-scope-r1.md` 已评估 2B（READY-WITH-UNFREEZE，仅 C-16 v1.4）；DSH 裁决：与 2A 拆分、契约先行（`FEA-11-RUN-GRANT-2B-PREREQ-1`）；**依赖 2A + PREREQ done 后才释放实现**；本卡当前为 proposed（scope 已评估、未冻结实施）
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11-RUN-GRANT-2A
  - FEA-11-RUN-GRANT-2B-PREREQ-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-RUN-GRANT-2
allowed_paths:
  - doc/tasks/FEA-11-RUN-GRANT-2.md
  - doc/reviews/FEA-11-RUN-GRANT-2-*.md
  - doc/handoffs/FEA-11-RUN-GRANT-2-*.md
  - verification/FEA-11-RUN-GRANT-2/**
  - src/infrastructure/resource_channel/source_read_refs.py
  - src/bootstrap/core_service.py
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - tests/core/test_host_control.py
  - tests/fea11/test_source_run_grant.py
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs
out_of_scope:
  - 2A（Host 版本通道）与 2C（长 Run 续期）；L-G1/L-G2/L-G9/L-G10（另卡/保留）
  - C-17/C-06/M2-C1 及其他 16 份契约字节（仅 PREREQ 的 C-16 v1.4）
  - Run wire/`CORE_PROTOCOL_MINOR`/新错误码/schema/依赖；UI/App；真实用户数据；push
---

# FEA-11-RUN-GRANT-2：容器成员 entry 授权通道（proposed，待 2A + PREREQ）

> **状态：`proposed`（scope 已由 review 评估；实施释放依赖 `FEA-11-RUN-GRANT-2A` done + `FEA-11-RUN-GRANT-2B-PREREQ-1`（C-16 v1.4）done）。** 当前不得开工。

## 来源

- `FEA-11-RUN-GRANT-1` L-G12②：Host 对 zip/cbz/pdf 只铸容器单 entry（locator=容器名、ordinal=0），Core 按成员 `source_entries` 匹配 → 多成员容器仅首成员可授权。
- scope review `doc/reviews/FEA-11-RUN-GRANT-2-scope-r1.md`：2B 需 **C-16 v1.4 UNFREEZE**（容器 entries 1..N）+ Core 注册/匹配实现 + Host 按 Core 权威 locator/ordinal 铸 N 项；≥3 成员真实 zip/cbz IPC；`max_entries`/64 上限 typed。

## In（草案，待释放时按卡冻结）

| # | 项 | 要点 |
|---|---|---|
| J-1 | Core 注册/匹配 | `_parse_scope` 接受容器 1..N（逐项校验：locator 安全、ordinal 唯一、path 同一容器、facts=容器身份、预算上限）；匹配沿用 `entry_key OR locator OR ordinal` + facts；任一不匹配整体 typed 零写；`_bindings` 语义不变 |
| J-2 | Host 铸 N 项 | 成员 locator/ordinal 必须来自 Core 权威扫描响应（2A 缓存）；容器保持容器 path/facts；超 `max_entries`/64 grant 上限 → typed，不截断 |
| J-3 | 测试/证据 | ≥3 成员真实 zip/cbz：每成员页 authorize+resolve；删/错一项 typed `SOURCE_ACCESS_DENIED`；零越权；判别性破坏点；EV/Manifest |
| J-4 | 门禁 | 全量 pytest/.NET 不降；pins 18/18（C16 v1.4）；check/API/scope；全量跑后恢复 FEA-09 |

## Out

- 2A 版本通道（已完成的前提）；长 Run 续期；加密源；Core 重启；L-R11 gate；UI/App；契约（PREREQ 已冻结）；schema/依赖；真实用户数据；push。

## Acceptance Criteria（草案，释放时冻结）

- AC-J1 容器 ≥3 成员真实 IPC：每个成员页均可 `AuthorizeSourceReadForRun` 绑定并 `resolve_page_resource`；不可读到未授权成员。
- AC-J2 fail-closed：N 项中任一项 locator/facts/ordinal 不符或 entry 不在 version → 整体 typed、零映射写入；容器替换/generation 漂移/撤销/过期 typed。
- AC-J3 上限：超过 `max_entries` 或 64 grant 上限 → typed，不截断；≥65 成员容器有明确用例。
- AC-J4 managed/旧路径零回归；零漂移（pins 18/18、Run wire/minor/schema/依赖零改动）；全量门禁不降；EV/Handoff 不夸大。

## 依赖与下一步

1. 先完成 `FEA-11-RUN-GRANT-2A`（Host 版本通道）与 `FEA-11-RUN-GRANT-2B-PREREQ-1`（C-16 v1.4）。
2. 两者 done 后由 DSH 复核本卡 scope 是否仍成立（如 Core/Host 形状变化），再冻结/释放实施。
