---
id: FEA-11-HOST-AUTH-4
title: Host 完成语义收尾（原 HOST-AUTH-1 limitation 6/7/8/9 + Review P3-1…8/10）
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡：由 `FEA-11-HOST-AUTH-2` Review r1（R1-P2-1/5）与 DSH 2026-11-08 裁决 re-home；**scope 未冻结，不得实施**；须先独立 scope review
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
evidence_dir: verification/FEA-11-HOST-AUTH-4
allowed_paths:
  - doc/tasks/FEA-11-HOST-AUTH-4.md
  - doc/reviews/FEA-11-HOST-AUTH-4-*.md
  - doc/handoffs/FEA-11-HOST-AUTH-4-*.md
  - verification/FEA-11-HOST-AUTH-4/**
out_of_scope:
  - 未 scope review 前不得实施任何实现
---
# FEA-11-HOST-AUTH-4：Host 完成语义收尾（占位）

## 来源（逐项）
- `FEA-11-HOST-AUTH-1` limitation **6**（输入规则）、**7**（Registry atomicity）、**8**（分类精度）、**9**（capability reason）。
- `FEA-11-HOST-AUTH-2` Review r1 的 P3：**P3-1** `AuthorizationDigest` 双口径统一；**P3-2** `RequestDigest` 守卫判别测试；**P3-3** state 竞争守卫测试（含 `MarkFailed` 并发）；**P3-4** receipt 矩阵补 `plan_digest`/`commit.*`；**P3-5** 重发 receipt 整体相等断言；**P3-6** `AuthorizationAfter` 亚毫秒窗口；**P3-7** 「generation > baseline」不可达分支标注；**P3-8** gated fixture 质量（超时/清理/帧计数/python 路径）；**P3-10** 错 digest 覆盖 coordinator journal 交互。

## 验收（草案，待冻结）
- 每项 1 条可判别断言或明确「不可构造 + 契约预留」标注；
- 门禁不降（pytest ≥3390、.NET passed 不减、pins 18/18、check PASS）；
- 不得借本卡改契约字节（如需 UNFREEZE 另立载体）。
