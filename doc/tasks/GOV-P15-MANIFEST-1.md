---
id: GOV-P15-MANIFEST-1
title: 恢复 P15 缺失的 Resource Manifest
kind: governance
governance_version: 3
status: in_review
approval: codex_r20_followup_not_yet_released
suggested_owner: codex
owner: codex
reviewer: Antigravity
depends_on: [GOV-SOURCE-RECORDS-1]
base_commit: 3539d8d75
branch: null
worktree: null
integration_commit: null
delivery_head: 237c43862be57ce8d84b2932abe2c30b279e6c7c
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-P15-MANIFEST-1
---

# GOV-P15-MANIFEST-1：恢复 P15 缺失的 Resource Manifest

## 来源与目标

检查器对 `P15` 报 `Resource manifest 不存在：verification/P15/resource-manifest.json`。

Codex r20 §2.2 裁定：

> **P15 的已有 Resource Manifest 行明确记录真实 worktree 为 `PRESERVE_REFERENCED`，
> 且 `resource-manifest.json` 被引用为 closeout 清单。因而资源并非不适用；
> 把引用改为 `NOT_APPLICABLE` 会与既有事实矛盾。** 单独恢复。

## Acceptance Criteria

- [x] **AC1 核实被引用的内容**：从 `P15` 的 Resource Manifest 表与 Closeout Record 中 <<MET>>
  提取该 manifest 本应包含的全部字段（至少：worktree 路径、disposition、
  destination、以及 closeout 清单指向的其它资源）。
  **不得凭空发明字段**——只恢复能从既有记录推出的内容。
- [x] **AC2 核实 worktree 实际状态**：检查 <<MET>>
  `G:\CODEX\New Manga.workspace\worktrees\P15*` 是否存在、是否 clean、
  HEAD 是什么。若已不存在，如实记录为「原 worktree 已清理」，
  **不得伪造路径存在性**。
- [x] **AC3 重建 manifest**：在 `verification/P15/resource-manifest.json` 写入恢复的清单， <<MET>>
  格式须与其它 Task 的同类 manifest 一致（先读一个已有的作参照）。
  内容必须与 AC1/AC2 的核实结果一致，**每个 disposition 都有依据**。
- [x] **AC4 交付与 Review**：生成 Handoff；由 Antigravity 对固定 delivery head 独立 Review。 <<MET>>
  Review 必须核对：**重建的每一个字段都能在既有记录中找到依据**，
  且没有为了让检查器变绿而填 `NOT_APPLICABLE`。

## 允许修改范围

- `verification/P15/resource-manifest.json`（新建）。
- `verification/GOV-P15-MANIFEST-1/`。
- 本 Task 自身文件、Handoff、Review。

## 禁止事项

- 不改 `P15.md` 的任何字段（含 `status`、AC、Closeout Record）。
- 不把资源改成 `NOT_APPLICABLE` 来消错。
- 不伪造 worktree 路径的存在性。
- 不改其它 Task 的 manifest。

## 测试与验证

```powershell
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P15.md
```

## Canonical Evidence

交付时登记恢复依据、worktree 实际状态核实、manifest 内容、Handoff、Review。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| P15M-RESTORED | AC3 | `verification/P15/resource-manifest.json` | `237c43862` | `ccdb5fb7d298a41c0ccfec01e62e1fa2782b40581d87451583351d489ebc34e3` | `CANONICAL` |
| P15M-WRITEUP | AC1–AC4 | `verification/GOV-P15-MANIFEST-1/ac1-ac4-manifest-restoration.md` | `237c43862` | `934b747842ff1c15dab1aeef2105bc1a7339077caf998225ccd9b11e9cb21788` | `CANONICAL` |
| P15M-HANDOFF | AC5 | `doc/handoffs/GOV-P15-MANIFEST-1-237c43862.md` | `6eec515a5` | `81e37cd1808cfde9c08eea88d98273b1d9f9ce78b7550502be84ada09e564d31` | `CANONICAL` |

## Resource Manifest

本 Task 自身不处置资源；但须在 closeout 中说明它为何不改变 `P15` 的既有资源结论。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-P15-MANIFEST-1.md` | 只重建一个 JSON 文件 |
| task-env | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-P15-MANIFEST-1.md` | 只重建一个 JSON 文件 |
| dataset | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-P15-MANIFEST-1.md` | 只重建一个 JSON 文件 |
| artifact | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-P15-MANIFEST-1.md` | 只重建一个 JSON 文件 |
| temp | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-P15-MANIFEST-1.md` | 只重建一个 JSON 文件 |
| agent-output | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-P15-MANIFEST-1.md` | 只重建一个 JSON 文件 |
| exchange | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-P15-MANIFEST-1.md` | 只重建一个 JSON 文件 |
| evidence_dir | `verification/GOV-P15-MANIFEST-1/` | `PRESERVE_REFERENCED` | `verification/GOV-P15-MANIFEST-1/` | `934b747842ff1c15dab1aeef2105bc1a7339077caf998225ccd9b11e9cb21788` | 1 份证据 |

## Closeout Record

- 状态：`proposed`。授权来源：Codex r20 §2.2。
