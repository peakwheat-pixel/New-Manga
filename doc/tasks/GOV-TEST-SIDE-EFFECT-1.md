---
id: GOV-TEST-SIDE-EFFECT-1
title: "测试侧效治理：阅读器 overlay 证据不得写在仓库内（每次全量测试污染工作树）"
kind: governance
governance_version: 3
status: done
approval: dsh_lead_release_2026-11-17_test_side_effect
suggested_owner: DSH
owner: DSH
reviewer: 独立上下文子 agent（未参与实施）
depends_on: [MAINT-1-RELEASE-MONITOR]
base_commit: 46f146730
branch: main
worktree: main
integration_commit: e0b57eaff
delivery_head: e0b57eaff
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/GOV-TEST-SIDE-EFFECT-1
allowed_paths:
  - doc/tasks/GOV-TEST-SIDE-EFFECT-1.md
  - apps/desktop-avalonia/tests/NewManga.App.Tests/ImmersiveReaderVisualEvidenceTests.cs
  - apps/desktop-avalonia/scripts/test.ps1
  - verification/GOV-TEST-SIDE-EFFECT-1/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/handoffs/NEXT-SESSION-STARTER.md
---

# GOV-TEST-SIDE-EFFECT-1：测试侧效治理（overlay 证据写仓）

## 来源与目标

- 来源：STARTER 队列 3 的长期待修项 —— `apps/desktop-avalonia/scripts/test.ps1` 每次运行都会改写
  `verification/READER-OVERLAY-HEADLESS-PNG-1/` 下 2 个文件（`immersive-reader.png`、`render-info.md`），
  导致全量测试后工作树变脏，且**评审者重跑会悄悄覆盖被 pin 的规范证据**。
- 根因（实测）：`apps/desktop-avalonia/tests/NewManga.App.Tests/ImmersiveReaderVisualEvidenceTests.cs:85`
  把输出目录硬编码为 `Path.Combine(root, "verification", "READER-OVERLAY-HEADLESS-PNG-1")`；
  而 `test.ps1` 已经区分「默认写 workspace」与 `-CanonicalEvidence` 写仓库，两套口径不一致。
- 目标：把该测试的输出目录改为**可配置**，默认仍写原位置（保持既有规范证据的再生能力），
  由 `test.ps1` 在非 `-CanonicalEvidence` 时把它指向 workspace 证据目录；**不得削弱任何断言**。

## 范围冻结

- 只改：该测试类的证据输出目录解析 + `test.ps1` 的环境变量传递 + 本卡与三指针。
- 不改：渲染/断言逻辑、测试数量、证据文件格式、`verification/READER-OVERLAY-HEADLESS-PNG-1/` 既有字节。

## Acceptance Criteria

- [x] **AC1 输出目录可配置**：测试类从环境变量（`NEWMANGA_READER_OVERLAY_EVIDENCE_DIR`）读取输出目录，未设置时回落到原仓库路径；断言与「必须真渲染、不得 skip」语义完全不变。 <<MET>>
- [x] **AC2 test.ps1 默认不再写仓**：非 `-CanonicalEvidence` 时 `test.ps1` 把该环境变量指向 workspace 证据根；`-CanonicalEvidence` 时仍指向仓库内规范路径。 <<MET>>
- [x] **AC3 实测无侧效**：运行 `NewManga.App.Tests` 后 `git status --porcelain verification/READER-OVERLAY-HEADLESS-PNG-1` 为空。 <<MET>>
- [x] **AC4 规范证据仍可再生**：`-CanonicalEvidence` 路径下输出目录仍等于仓库内路径（代码路径可读 + 逻辑单测/实测之一）。 <<MET>>

## 测试要求

- 该测试项目仍必须通过（含 overlay 渲染断言）；不新增 skip、不放宽断言。

## 允许修改范围

见 front matter `allowed_paths`。

## 禁止范围

- 不得删除或弱化任何测试断言；不得改动 `verification/READER-OVERLAY-HEADLESS-PNG-1/` 的历史字节；
- 不得把测试改成「找不到目录就跳过」。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-SIDEEFFECT-1 | AC3 | verification/GOV-TEST-SIDE-EFFECT-1/ac3-no-side-effect-2026-11-17.log | - | b74ab84b3caffd342d22773e39a32039f836e5f7335104d5cd9f321aee18a5e6 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-only | — | NOT_APPLICABLE | — | — | 本卡只改仓库内代码与文档，未创建仓外资源 |

## Closeout Record

- **收口时间**：2026-11-17；integration commit `e0b57eaff`。
- **做法**：测试输出目录改为可配置（env `NEWMANGA_READER_OVERLAY_EVIDENCE_DIR`），`test.ps1` 默认指向本次运行证据根，
  `-CanonicalEvidence` 仍指仓库内规范路径；断言、渲染与「不得 skip」语义一行未改。
- **实测**：全量 `test.ps1 -Configuration Debug` → `TEST PASS 1591/1639 passed, 48 skipped`，exit 0；
  跑完后 `git status --porcelain verification/READER-OVERLAY-HEADLESS-PNG-1` 为空。
- **证据**：`verification/GOV-TEST-SIDE-EFFECT-1/ac3-no-side-effect-2026-11-17.log`。
