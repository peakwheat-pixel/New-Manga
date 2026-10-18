---
id: P20-CLOSE-BOUND-HARDEN-2
title: sidecar worker holder 生命周期与审计边界收口（R4-01 承接）
kind: fix
governance_version: 2
status: ready
approval: user_ruling_20261018_close_harden_1_and_split_harden_2
blocked_by: null
suggested_owner: Antigravity
owner: Antigravity
reviewer: Codex
depends_on: [P20-CLOSE-BOUND-HARDEN-1]
base_commit: 35770fe91ab722b6d6c5e06e1f855c062d15c0a2
branch: null
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/P20-CLOSE-BOUND-HARDEN-2
---

# P20-CLOSE-BOUND-HARDEN-2：worker holder 生命周期与审计边界收口

## 背景（用户裁决 2026-10-18）

`P20-CLOSE-BOUND-HARDEN-1` 经三轮返修（R1fix/R2fix/R3fix）后，R4 复审仍为 `changes_requested`。用户已按 DIR-4 用尽豁免（"最后一次"），裁决：**原 Task 以 `closed_with_limitations` 收口，未闭合项由本 Task 承接**（仿 `P09-AC3-DELETE-1` → `P09-AC3-DELETE-HARDEN-1` 先例）。

来源：`verification/P20-CLOSE-BOUND-HARDEN-1/codex-review-r4.md`。

## 未闭合项（原样承接，不得抹除）

**R4-01（P1，延续 R3-01）** —— 依据 `apps/desktop/src-tauri/src/library_bridge.rs:1527-1569`、`:3630-3647`、`:3665-3682`、`:3787-3804`、`:3822-3839`；审计 `verification/P20-CLOSE-BOUND-1/concurrency-lock-audit.md:26`、`:134-150`：

- registry **连续锁超时**时仍可能丢失对 holder 的保留；
- registry **达到容量饱和**时的行为未定义；
- **holder spawn 失败**路径未覆盖；
- 审计表仍宣称句柄"绝不被 drop"，并把有限 registry/reaping 描述为**完整生命周期保证**（`:113` 的 CloseHandle 行号已修正为 `1857, 1965, 3880, 3886`，但 `:26`、`:134-135`、`:147-150` 的表述仍需按真实语义改写）。

## 验收标准

- **AC1**：registry 连续锁超时路径**不得丢失** holder/handle 保留语义；给出可运行的注入用例。
- **AC2**：registry **容量饱和**有明确定义的行为（拒绝、退避或显式扩容），并有注入用例。
- **AC3**：**holder spawn 失败**路径有覆盖，且失败时句柄处置明确（不泄漏、不误 drop）。
- **AC4**：`concurrency-lock-audit.md` 的**生命周期边界**按修复后真实语义重写；不得再出现"绝不 drop"或"完整生命周期保证"这类超出实现强度的表述；行号与源码一致。
- **AC5**：**AC7 真实交互桌面直跑**（由 Coordinator 在交互式桌面执行；本 Task 只负责脚本正确性，不得自行记 PASS）。
- **AC6**：不回归 —— `P20-CLOSE-BOUND-HARDEN-1` 已通过的 AC8 九项回归（R-008 心跳恢复、R-003 拆环 reap、R-006 错误呈现、`MAX_RETRIES=3`、resilient 9 项、stdio drop、shutdown writes、2 MB pipe overflow）保持通过。
- **AC7**：报告中所有 40 位 SHA 必须能通过 `git cat-file -e` 校验；`sha256` 按**磁盘真实字节**实算（本仓库为 **CRLF 检出**）。

## 边界

- 不改 IPC / 共享契约 / Schema / ACL / 依赖版本；不动 `apps/desktop/frontend/**`。
- 禁止改写历史 pin 以"消除失败"；证据一律追加。
- 禁止编造 commit SHA。

## 交付物

- 修复后的 `library_bridge.rs` 与更新后的审计表
- 上述注入用例的原始日志与退出码
- Handoff（引用实际文件与 commit）
