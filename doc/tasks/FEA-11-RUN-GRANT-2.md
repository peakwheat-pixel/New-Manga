---
id: FEA-11-RUN-GRANT-2
title: Host→Core source 身份通道（version + 容器成员 locator/ordinal）与长 Run 授权续期（proposed 占位）
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡：scope 尚未冻结，不得释放实施；来源 `FEA-11-RUN-GRANT-1` closeout L-G12（version 通道 + 多成员容器仅首成员可授权）与 r3 R3-02（AcceptRun→seam 委托行覆盖残差）；须先独立 scope review（是否需 UNFREEZE C-16/C-17），由 DSH 裁决
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11-RUN-GRANT-1
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
out_of_scope:
  - 生产实现/Host/Core/App 代码、契约/schema/依赖字节、真实用户数据、push —— 本卡为占位，未冻结
---

# FEA-11-RUN-GRANT-2：Host→Core source 身份通道（占位）

> **状态：`proposed` 占位卡；scope 未冻结，不得实施。** 由 DSH 在 `FEA-11-RUN-GRANT-1` closeout 时登记为候选（L-G12 / R3-02）。

## 来源与目标（草案）

- **来源 1（L-G12① version 通道）**：`source_list_scan_targets` DTO 无 `version_id`，冷启动 `SourceScanTarget.Version` 固定 `"1"`；而 C-16 v1.3 §2.4 要求 `scope.version == binding.accepted_source_version` → 生产 Host 铸出的 grant 通常 version 不匹配 → 授权 typed `SOURCE_ACCESS_DENIED`、不 dispatch（fail-closed）。
- **来源 2（L-G12② 容器成员 entry 通道）**：Host 对 zip/cbz/pdf 只铸容器单 entry（locator=容器名、ordinal=0），Core 按成员 `source_entries` 匹配 → 多成员归档仅 `ordinal=0` 页可授权。
- **来源 3（R3-02）**：`HostRuntime.AcceptRunAsync` → `AuthorizePreparedRunForAcceptAsync` 的委托行本身未被判别性测试覆盖（seam 逻辑已覆盖）。
- **来源 4（L-G1）**：单 grant ≤300s；长 Run 需定期重铸/重绑（本卡候选）。
- **目标（草案）**：为 Host 提供 Core 权威的 source/version/entry 身份通道，使生产 referenced Run 在窗口内对 image/folder/多成员容器均可用；并评估长 Run 续期方案（或继续明示 limitation）。

## 候选 Scope（待 scope review 冻结）

- In（草案）：Host 源身份缓存（如从 `ScanSourceSync` 结果/枚举扩展获取 `version_id` 与成员 locator/ordinal）、Core 侧对应只读通道（可能需 C-17 DTO 扩展或 C-16 命令扩展 → 评估 UNFREEZE）、Host/Core 测试与 L-G12 边界扩展。
- Out（草案）：UI/通知/扫描实现重写/删除/GC；真实用户数据；push；未评估 UNFREEZE 前不得改契约字节。

## 依赖与下一步

- 依赖：`FEA-11-RUN-GRANT-1`（done，`a11ded0d3`）。
- **必须先做独立 scope review**（核验 C-17 §5.2 DTO / C-16 v1.3 §2.4 / C-06 是否足够；是否需 UNFREEZE；最小写域与 AC 草案），由 DSH 裁决后冻结释放。
- 若 scope review 判 BLOCKED（需 UNFREEZE 或 Host 通道不可行），登记 limitation 并回退候选。
