---
id: AUDIT09-READER-EMPTY-RETRY-1
title: Reader 已选中零页章节 Retry 后仍提示先选择（AUDIT-09-CAND-001 P3）
kind: implementation
governance_version: 3
status: done
resume_status: done
approval: user_authorized_2026-11-14 (所有任务交 DSH、自动裁决/规划、全部授权、无需用户介入)
suggested_owner: DSH
owner: DSH
reviewer: "DSH auto-adjudication (2026-11-14 owner directive); independent sub-agent review optional"
depends_on: [AUDIT12-PUBLISH-OUTPUT-1]
base_commit: e3569bca3
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 338dc3f9ae92c1a67424c2eec13f38ff51bca94f
delivery_head: 338dc3f9ae92c1a67424c2eec13f38ff51bca94f
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/AUDIT09-READER-EMPTY-RETRY-1
allowed_paths:
  - apps/desktop-avalonia/src/NewManga.App/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - verification/AUDIT09-READER-EMPTY-RETRY-1/**
  - doc/tasks/AUDIT09-READER-EMPTY-RETRY-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# AUDIT09-READER-EMPTY-RETRY-1：Reader 已选中零页章节 Retry 后仍提示先选择（AUDIT-09-CAND-001 P3）

## 来源与目标

`AUDIT-09-CAND-001`（P3，TRIAGED）：合成 UI 测试中，已选中的零页章节在 Retry 后仍提示“先选择章节”；单一路径可见不一致，根因与普遍性未知（见 `audit/V1-FULL-AUDIT/reports/AUDIT-09-UI-UX-2026-11-13.md`）。目标：先隔离复现（fixture 覆盖有页/零页/切换选择/Retry），确认后做窄范围修复；若当前基线不可复现，记录 limitation 并关闭，不伪造修复。

## Acceptance Criteria

- [x] **AC1**：定位 Reader 选择/Retry 状态机与提示逻辑，记录锚点、当前行为与复现条件。 <<MET>>
- [x] **AC2**：在隔离 fixture 中复现（有页、零页、切换选择、Retry）；若不可复现，记录证据与 limitation，不修改产品代码。 <<MET>>
- [x] **AC3**：若复现，做窄范围修复并运行相关 UI/表现层测试（记录命令/EXIT）；真实 GUI 演练为 NOT_RUN。 <<MET>>
- [x] **AC4**：证据 pin、四项门禁、资源 closeout、DSH 自动裁决。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| AUDIT09-VM-1 | AC2 | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ReaderOverlayViewModel.cs` | `338dc3f9ae92c1a67424c2eec13f38ff51bca94f` | `AE9F41C42ABFDCFDB72E2E4E0601BB2BCE8DD57C73289A21FFCA4699BF6937BC` | CANONICAL | BLOB |
| AUDIT09-TEST-1 | AC3 | `apps/desktop-avalonia/tests/NewManga.App.Tests/V2ImmersiveReaderTests.cs` | `338dc3f9ae92c1a67424c2eec13f38ff51bca94f` | `815127539DE3F678589FE2BEEF9079D0C733F22D07DBE5CC0EFEEB9D57D6DA62` | CANONICAL | BLOB |
| AUDIT09-TEST-LOG-1 | AC3 | `verification/AUDIT09-READER-EMPTY-RETRY-1/logs/dotnet-test-reader-retry-fixed.log` | `338dc3f9ae92c1a67424c2eec13f38ff51bca94f` | `7C0937D47970FF5B1EF16058849644AA999F965AA993CBD17890ED065381AA76` | CANONICAL | BLOB |
| AUDIT09-DISCRIMINATING-LOG-1 | AC3 | `verification/AUDIT09-READER-EMPTY-RETRY-1/logs/discriminating-power-old-code.log` | `338dc3f9ae92c1a67424c2eec13f38ff51bca94f` | `00D2CC09B3A18F52148CFADDB6EA3DE193446C3EAB22FF26BE79693926F27B8E` | CANONICAL | BLOB |
| AUDIT09-EVIDENCE-1 | AC4 | `verification/AUDIT09-READER-EMPTY-RETRY-1/evidence/reader-retry.json` | `338dc3f9ae92c1a67424c2eec13f38ff51bca94f` | `33D77FEF9DDEB03E66E74060A08AD2B67CD2ADBAF1619FD65C52E69050CAE11C` | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | doc | verification/AUDIT09-READER-EMPTY-RETRY-1/evidence/reader-retry.json | 主工作区保留 |
| task-env | - | NOT_APPLICABLE | doc | verification/AUDIT09-READER-EMPTY-RETRY-1/evidence/reader-retry.json | 无独立 task-env |
| agent-output | - | NOT_APPLICABLE | doc | verification/AUDIT09-READER-EMPTY-RETRY-1/evidence/reader-retry.json | 无 agent-output |
| artifact | verification/AUDIT09-READER-EMPTY-RETRY-1 | PRESERVE_REFERENCED | doc | verification/AUDIT09-READER-EMPTY-RETRY-1/evidence/reader-retry.json | 测试证据保留 |
| dataset/model/test-material | - | NOT_APPLICABLE | doc | verification/AUDIT09-READER-EMPTY-RETRY-1/evidence/reader-retry.json | 合成 fixture |
| exchange | - | NOT_APPLICABLE | doc | verification/AUDIT09-READER-EMPTY-RETRY-1/evidence/reader-retry.json | 无外部传输 |

## 未执行项

- 真实 GUI Reader 零页 Retry 演练：NOT_RUN（本 Task 用合成 FakeHostController/Avalonia headless 测试；审计截图场景未重现）。
- Avalonia TestHost 阻塞历史（8/8 EXIT 1）未解除；本 Task 的筛选测试实际可运行（4 passed），不据此宣称 TestHost 全量恢复。

## 允许修改范围

- `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/**`（Reader 选择/提示相关表现层）
- `tests/NewManga.Presentation.Avalonia.Tests/**`
- `verification/AUDIT09-READER-EMPTY-RETRY-1/**`
- 本 Task 卡、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

## 禁止范围

Avalonia TestHost 阻塞项不解除；不修改 Host/Core 契约、Schema、依赖、真实用户数据、远端、发布。

## 测试要求

优先使用可运行的隔离 fixture/单测；Avalonia TestHost 已知 8/8 runner EXIT 1、TRX 0（BLOCKED-TESTHOST-ACCESS），不得写成通过；真实 GUI 为 NOT_RUN。
