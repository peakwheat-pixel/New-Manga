---
id: GOV-PIN-LINEAGE-1
title: 历史 evidence pin 的 lineage 补注
kind: governance
governance_version: 2
status: proposed
approval: codex_r20_followup_not_yet_released
suggested_owner: codex
owner: codex
reviewer: Antigravity
depends_on: [GOV-SOURCE-RECORDS-1]
base_commit: 3539d8d75
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-PIN-LINEAGE-1
---

# GOV-PIN-LINEAGE-1：历史 evidence pin 的 lineage 补注

## 来源与目标

`GOV-SOURCE-RECORDS-1` 发现两个已 `done` 的 Task 检查器报 `Evidence SHA-256 不匹配`：

| Task | 失配的 pin | 真实原因 |
|---|---|---|
| `EXPORT-REVEAL-1` | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | 契约后来演进至 **rev 2.11** |
| `P15` | `apps/desktop/frontend/src/settings/SettingsPage.test.tsx` | 后续提交 `528c6289c` 修改过 |

Codex r20 §2.2 裁定：

> 两处已知失配都发生在 pin 所指文件提交之后。**原 pin 表达的是特定 Task 交付时、
> 特定提交中的字节事实。重算并覆盖原值会把「后来内容」替换成「当时证据」，
> 破坏历史可追溯性。**
>
> 对这两项及**另外 5 个受同机制影响的已 done Task**，默认处置统一为：
> **保留原 evidence_id、原 commit、原 SHA-256；追加清晰的 pin lineage / supersession 说明**，
> 记录后续变更提交及现有内容不再匹配的原因。

## Acceptance Criteria

- [ ] **AC1 识别受影响范围**：找出**全部**受同机制影响的 pin（r20 说是 7 个 Task 中的 7 处，
  但须独立核实精确清单与数量）。判据：pin 所指路径在该 Task 的交付 commit **之后**
  被其它提交修改过，导致当前磁盘内容与 pin 不符。
  **须区分**「时间性失配（内容被合法修改）」与「行尾性失配（CRLF 转换）」——
  后者已在 `GOV-EOL-PIN-1` 处理过，处置方式不同。
- [ ] **AC2 追出后续变更提交**：对每个受影响的 pin，用 `git log` 找出是哪个提交修改了该路径，
  并记录该提交的 hash 与日期。
- [ ] **AC3 追加 lineage 而非重算**：在对应 Task 的 Canonical Evidence 表旁（**不改表内六列**）
  追加 lineage 说明，包含：原 pin 的 commit、当前内容的实际 hash、导致失配的后续提交、
  以及「原 pin 有效，当前内容已演进」的明确结论。
  **不得**用当前内容覆盖原 sha256。
- [ ] **AC4 检查器配合**：检查器当前对所有 `Evidence SHA-256 不匹配` 一律报 error。
  请判断应如何表达「已声明的 lineage 失配」——
  （a）检查器识别 lineage 注记后降级为 warning；
  （b）引入新的 evidence class；
  （c）不改检查器，接受这些 Task 永远红。
  **给出你的选择与理由**，并说明对既有 4 个已 PASS 的 Task 是否有影响。
- [ ] **AC5 交付与 Review**：生成 Handoff；由 Antigravity 对固定 delivery head 独立 Review。
  Review 必须核对：**没有一处 pin 被重算覆盖**。

## 允许修改范围

- 受影响 Task 的 Canonical Evidence 表**旁**（追加说明，不改表内六列）。
- `tools/governance/check.ps1`（仅当 AC4 选择 a 或 b）。
- `verification/GOV-PIN-LINEAGE-1/`。
- 本 Task 自身文件、Handoff、Review。

## 禁止事项

- **不得重算或覆盖任何历史 pin**。
- 不改 Task 的 status、AC、Closeout Record。
- 不把失配说成「已修复」——它是「已解释」。
- 不改证据文件内容。

## 测试与验证

```powershell
pwsh -NoProfile -File tools/governance/check.ps1
git log --oneline -- <受影响路径>
```

## Canonical Evidence

交付时登记受影响 pin 清单、后续变更提交追查记录、lineage 注记 diff、Handoff、Review。

## Resource Manifest

本 Task 只追加说明文字，不处置资源。

## Closeout Record

- 状态：`proposed`。授权来源：Codex r20 §2.2。
