---
id: E9-PATH-CARRIER-STUDY-1
title: E-9 修复载体可行性核实（补齐 Codex 的 4 条前置条件）
kind: evidence
governance_version: 3
status: done
disposition: "Codex 无法读代码，仅给有条件意见；DSH 补齐证据后结论：独立列优于塞进 AuthorizationJson"
approval: DSH 2026-11-15
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - E9-RECOVERY-PATH-FIX-1
base_commit: 419d74887
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/E9-PATH-CARRIER-STUDY-1
allowed_paths:
  - doc/tasks/E9-PATH-CARRIER-STUDY-1.md
  - doc/reviews/E9-PATH-CARRIER-STUDY-1-*.md
  - doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/E9-PATH-CARRIER-STUDY-1/**
---

# E9-PATH-CARRIER-STUDY-1

## 背景

Codex 被要求裁决"journal（A）vs Core plan（B）"。其所有命令因 Windows 740 无法启动，
**未读到任何代码**，故**诚实拒绝**签发正式裁决，只给"倾向 A"的有条件意见 + 4 项待核实条件。

本卡由 DSH 补齐这 4 项（DSH 有文件访问权）。

## 核实结论

| 项 | 结论 |
|---|---|
| `AuthorizationJson` 载体 | journal 表列 `authorization_json TEXT`（`schema.py:808`），**Host 内部持久化，非 wire** |
| `RequestDigest` 范围 | `sha256({operation_id, plan_id, plan_digest, kind})` —— **不含** authorization 结构 |
| `minted.AuthorizationDigest` | `sha256(canonical(authorizations[]))` —— 外层字段**不在**范围 |
| **`Authorize()` 的 `AuthorizationDigest`** | **`Sha256Hex(整个 JSON)`** —— **加外层字段会变** |
| `AuthorizationDigest` 校验点 | **全仓无**（只写不验） |
| `JournalEntry.Kind` | 存在且参与 `RequestDigest`，但**不能**证明历史记录存过路径（认同 Codex 判断） |

## ★ 关键发现

两个写入点对 `AuthorizationDigest` 用了**不同定义**（`:425` 用 minter 的、`:152` 用整 JSON 的 sha256）。
这是既有不一致，本卡不修，但**决定了 A 的实施方式**。

## 结论

A **可行**，但"塞进 `authorizationJson`"会改变 `:152` 的摘要语义。
**更小风险的等价方案**：journal 表**新增独立列** `container_path TEXT NULL` ——
完全不碰既有 JSON、摘要与消费者。

**未实施**，待 DSH 冻结范围。

## 未做

- 未改任何代码。
- 未验证 CBZ/PDF/image 恢复的其它阻塞点。
