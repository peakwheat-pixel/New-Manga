---
id: SEC-01-REMOTE-VISIBILITY-1
title: AUDIT-11-INC-001 私有素材远端可见性只读调查
kind: research
governance_version: 3
status: done
resume_status: done
approval: user_authorized_2026-11-14 (所有任务交 DSH、自动裁决/规划、全部授权、无需用户介入)
suggested_owner: DSH
owner: DSH
reviewer: "DSH auto-adjudication (2026-11-14 owner directive); independent sub-agent review optional"
depends_on: []
base_commit: 5bb62ad69206cd454c4239404ddf11fa835bc74f
branch: main
worktree: G:/CODEX/New Manga
integration_commit: de79702b96f99e663442da3a2158c88d98385962
delivery_head: de79702b96f99e663442da3a2158c88d98385962
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/SEC-01-REMOTE-VISIBILITY-1
allowed_paths:
  - verification/SEC-01-REMOTE-VISIBILITY-1/**
  - doc/tasks/SEC-01-REMOTE-VISIBILITY-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# SEC-01-REMOTE-VISIBILITY-1：AUDIT-11-INC-001 私有素材远端可见性只读调查

## 来源与目标

NEW-MANGA-V1-FULL-AUDIT 的 R1 整改项 SEC-01（`reports/12_REMEDIATION_PLAN.md`）：`AUDIT-11-INC-001` 记录本地 reflog 与提交祖先关系支持“私有素材对象可能随历史 main push 进入公开仓库”的高置信推论，但当前远端可见性未知。本 Task 只做**只读**核验：固定远端元数据、以只读方式查询远端是否可访问相关对象/提交，记录方法、时间、结果与限制；不做删除、历史改写、补救、传播素材或下载私有素材内容。

## Acceptance Criteria

- [x] **AC1**：固定仓库与远端元数据（`git remote -v`、branch、HEAD、相关本地对象/提交清单），记录命令、时间、generated HEAD、EXIT 与证据路径。 <<MET>>
- [x] **AC2**：以只读、不下载私有素材内容的方式查询远端可见性（HTTP/只读 API/公开页面），记录请求目标、时间、状态、结果与不可用方法；不得 push、删除、改写历史或上传材料。 <<MET>>
- [x] **AC3**：对照 `AUDIT-11-INC-001` 本地证据给出结论：远端可见 / 不可见 / 仍未知（若证据不足则 unknown），不推断未验证事实；任何补救动作不在本 Task 授权内。 <<MET>>
- [x] **AC4**：证据 pin、四项治理门禁与资源 closeout 完成，Task 由 DSH 自动裁决并记录 limitation；未执行项标 NOT_RUN。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| SEC01-REPORT-1 | AC1-3 | `verification/SEC-01-REMOTE-VISIBILITY-1/REPORT.md` | `de79702b96f99e663442da3a2158c88d98385962` | `8B237E93132F30648638957185D3DEA22C31AFD1DFA62229DEFCF78EB2E2876D` | CANONICAL | BLOB |
| SEC01-LSREMOTE-LOG-1 | AC1 | `verification/SEC-01-REMOTE-VISIBILITY-1/logs/git-ls-remote.log` | `de79702b96f99e663442da3a2158c88d98385962` | `C88470317D26B499C835A36C35F5244C3C1E505B25C31423415ADE025CBF3AAF` | CANONICAL | BLOB |
| SEC01-API-PROBE-LOG-1 | AC2 | `verification/SEC-01-REMOTE-VISIBILITY-1/logs/github-api-probe.log` | `de79702b96f99e663442da3a2158c88d98385962` | `54F87A28BCB468049617A3D4D2B5C942637BEBE4137451551782C9EB5FF97D18` | CANONICAL | BLOB |
| SEC01-API-PROBE2-LOG-1 | AC2 | `verification/SEC-01-REMOTE-VISIBILITY-1/logs/github-api-probe2.log` | `de79702b96f99e663442da3a2158c88d98385962` | `218CA7286129BAA6A6D3D5CA358C5963AE496201390BDFCE3398FFC5A44E3F98` | CANONICAL | BLOB |
| SEC01-API-PROBE-JSON-1 | AC2 | `verification/SEC-01-REMOTE-VISIBILITY-1/evidence/github-api-probe.json` | `de79702b96f99e663442da3a2158c88d98385962` | `20DE11B666937FE688B9DE40B6527669CB8D8F7EEF9B9970744AE55965674144` | CANONICAL | BLOB |
| SEC01-API-PROBE2-JSON-1 | AC2 | `verification/SEC-01-REMOTE-VISIBILITY-1/evidence/github-api-probe2.json` | `de79702b96f99e663442da3a2158c88d98385962` | `7A937341DE6A799BB1A91E8CDEE37C9A18BF97BD431C9A99E004E6C87E0A8F1D` | CANONICAL | BLOB |

## 允许修改范围

- `verification/SEC-01-REMOTE-VISIBILITY-1/**`（证据/log/JSON）
- 本 Task 卡、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

## 禁止范围

产品源码、既有测试、契约、Schema、依赖、真实用户数据、历史证据、远端写操作（push/删除/改写/上传）、下载或传播私有素材内容。

## 测试要求

无产品测试；只读命令与网络查询需保存原始输出、EXIT、时间与限制。若网络不可用或远端拒绝匿名查询，记录 BLOCKED/NOT_RUN，不伪称已核验。

## 交付与证据

- `verification/SEC-01-REMOTE-VISIBILITY-1/REPORT.md`：方法、时间、结果、结论（可见/不可见/unknown）与限制。
- `verification/SEC-01-REMOTE-VISIBILITY-1/logs/`、`evidence/`：原始输出与 JSON 元数据。
- Task 卡、STATUS、REBASELINE_PLAN、TASK_LEDGER 同步。

## 已知阻塞

需要网络访问与远端匿名可访问性；若远端为私有或需凭据，记录为 BLOCKED 并保留证据边界。
