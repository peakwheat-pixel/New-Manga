---
id: CORE-PIPELINE-FIX-1
title: color analyzer 替换 + 空检测语义（Core 语义小改）
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_run_fix_a_b
suggested_owner: baseline-scout
owner: baseline-scout
reviewer: dsh
depends_on: []
base_commit: ce181ce0b
branch: task/CORE-PIPELINE-FIX-1
worktree: G:/CODEX/New Manga.workspace/worktrees/CORE-PIPELINE-FIX-1
integration_commit: aac638781
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/CORE-PIPELINE-FIX-1
allowed_paths:
  - doc/tasks/CORE-PIPELINE-FIX-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - src/**
  - tests/**
  - verification/CORE-PIPELINE-FIX-1/**
  - G:/CODEX/New Manga.workspace/task-envs/CORE-PIPELINE-FIX-1/**
  - G:/CODEX/New Manga.workspace/worktrees/CORE-PIPELINE-FIX-1/**
---

# CORE-PIPELINE-FIX-1：color analyzer 替换 + 空检测语义（Core 语义小改，已授权）

## 背景

RUN-OCR-DIAG-1 实证两个 Core 侧阻断点：
1. `color` 步骤 `PROVIDER_FAILED: '_StubStyleAnalyzer' object has no attribute 'analyze'`（`core_service.py:654/715` ↔ `application/translation/color/service.py:30`）；仓库内已有 `PillowSourceStyleAnalyzer`。
2. 检测器正常返回 0 候选时被映射为 `INVALID_INPUT`（`handlers.py:296`），导致无文字页整页失败。

## Acceptance Criteria

- [x] **AC1 color analyzer**：`_StubStyleAnalyzer` 已替换为 `PillowSourceStyleAnalyzer`（生产装配注入），`color` 步骤不再 `PROVIDER_FAILED`；analyzer 失败收敛为 typed `PROVIDER_FAILED`。 <<MET>>
- [x] **AC2 空检测语义**：0 候选默认按 completed(0 region) 处理（`detect.empty_detection_policy` 可配，默认 `complete`，`fail` 保留旧契约）；输出含 `empty_detection` 标记 + stderr 行，可观测；错误输入仍按原语义报错。 <<MET>>
- [x] **AC3 同构建复验**：同一 models 目录 + 同一数据根 + 同一请求序列，整书 8 页 Run：`color` 3/3 通过、4–8 页 completed 不再整页失败；逐页状态与耗时见 EV-RUN-PER-PAGE；未到 render 如实记录（止于 translate typed `PROVIDER_NOT_CONFIGURED`）。frozen sidecar 未重打包，已记录。 <<MET>>
- [x] **AC4 单测/回归**：新增 color（装配+处理器）与空检测语义单测；pytest 3F/2753P/9S（失败集合与基线 3F/2739P/9S 完全相同，0 新增）；`scripts/test.ps1` 162/162 全绿；vitest 60 文件/567 用例不变。 <<MET>>
- [x] **AC5 门禁**：`check.ps1 -TaskPath` 见交付记录；64-hex pin、commit 列留空；Handoff 与 Record Decision（理由/影响面/回退开关）见 REPORT §6。 <<MET>>

## 允许修改范围

`src/**`（color 组装点、检测语义及必要的回填语义）、`tests/**`（相关用例）、本卡、STATUS/PLAN/LEDGER、`verification/CORE-PIPELINE-FIX-1/**`、workspace。

## 禁止范围

不改协议/Host 契约、不改旧壳、不 push、不 gc/prune；不得放宽检测/OCR 的输入校验；不得把 0 候选静默当成成功而不留记录（需可观测）。

## 实现摘要

| 文件 | 改动 |
|---|---|
| `src/bootstrap/core_service.py` | 删除 `_StubStyleAnalyzer`；`assemble_production_core()` 注入 `SourceStyleService(PillowSourceStyleAnalyzer())`。 |
| `src/infrastructure/providers/handlers.py` | `handle_color` 将 analyzer 非 typed 异常包装为 `ProviderError`（`PROVIDER_FAILED`）；新增空检测策略常量/解析/stderr 记录，`handle_detect` 0 候选按策略 completed(0 region) 或 `INVALID_INPUT`。 |
| `src/application/tasks/service.py` | `_backfill_detected_regions` 在 `empty_detection` 时退役任务中剩余的 regionless `RUN` 单元（`_cancel_remaining`），页面任务方可 completed。 |
| `tests/**` | 新增 `test_color_handler.py`、`test_core_color_assembly.py`；改写 `test_detect_handler.py`、`test_regionless_rebinding.py`（N3/N3b/F3）并更新 3 处装配测试的 analyzer 注入。 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EV-REPORT | AC1–AC5 | verification/CORE-PIPELINE-FIX-1/REPORT.md | | 06c1955c26a993f3606073f1fd44ee0ed4eac5fb19d15decf96c484bf45d05b5 | CANONICAL |
| EV-RUN-DEFAULT | AC1/AC2/AC3 | verification/CORE-PIPELINE-FIX-1/run-ac3-default.json | | 551faaeeb48c7ea5898e82b37edba311bcd816e545d6654ac1536cd1039de975 | CANONICAL |
| EV-RUN-POLICY-FAIL | AC2/AC3 | verification/CORE-PIPELINE-FIX-1/run-ac3-policy-fail.json | | 2008f3ce02dc77103ebfdbb232a90520d64f12a716476b8b02e2a2aabab22c52 | CANONICAL |
| EV-RUN-PER-PAGE | AC3 | verification/CORE-PIPELINE-FIX-1/runs-per-page.json | | a6e75c62f13cb3d83e2b82f5529cbf8c79269b50d8397b8f7a58729d4ff7e57b | CANONICAL |
| EV-PYTEST | AC4 | verification/CORE-PIPELINE-FIX-1/pytest-full.log | | f1b49986071777cd004d43805791b6cbd8dbf1d561cb8eb59a3ca29f76318937 | CANONICAL |
| EV-VITEST | AC4 | verification/CORE-PIPELINE-FIX-1/vitest.log | | a5a700de36f2e34addd6a7ce4fe9bef2b0a0a941d443a8a44a0148541154ab01 | CANONICAL |
| EV-DOTNET-SUMMARY | AC4 | verification/CORE-PIPELINE-FIX-1/dotnet-summary.json | | c41c35a659c5b134689151293fa42909f637e652e99c9bfdc400aeca82c53d8e | CANONICAL |
| EV-DOTNET-LOG | AC4 | verification/CORE-PIPELINE-FIX-1/dotnet-test.log | | cefa3c06a2cdd62cef562b39e1e801b1661ca7de60938c067becf34606ebee0e | CANONICAL |
| EV-SRC-BASE-DIFF | AC1/AC2 | verification/CORE-PIPELINE-FIX-1/src-changes-vs-base.patch | | 8b6633ef2b57303edd826d0316cbd548e8e19629621d76c31f5db3896012fbaf | SOURCE_PIN |
| EV-SRC-WORKTREE-DIFF | AC1/AC2 | verification/CORE-PIPELINE-FIX-1/src-workingtree.patch | | be1ef1a7f534ccd60e69eaa4add68bb8745f36bf694f1a7bc2cf2bb92c982adb | SOURCE_PIN |
| EV-TOOL-RUN | AC3 | verification/CORE-PIPELINE-FIX-1/tools/verify_inproc.py | | 86b53281991c37ff77acc231ce73f144043b265b459bb0ec820807ba04bc257e | CANONICAL |
| EV-STDIO-ANOMALY | AC3/遗留 | verification/CORE-PIPELINE-FIX-1/run-stdio-scheduler-anomaly.json | | 6c3ae00194576c628e70bfa99a670051363ed19dbe34534545280af3200d5337 | CANONICAL |
| EV-STDIO-ANOMALY-RECHECK | AC3/遗留 | verification/CORE-PIPELINE-FIX-1/run-stdio-scheduler-anomaly-recheck.json | | 300dd70952ac3da804987c3f90bdf411dbb964c0b8e86ca39285fb6fa06d499c | CANONICAL |
| EV-STDIO-ANOMALY-NOPOLL | AC3/遗留 | verification/CORE-PIPELINE-FIX-1/run-stdio-scheduler-anomaly-nopoll.json | | ed00a117cfb1952c2b8f2dce4c5088ec07808cfdd7355cbe4d9d39770199d7f1 | CANONICAL |
| EV-RESOURCE-MANIFEST | AC5 | verification/CORE-PIPELINE-FIX-1/resource-manifest.json | | f3978898023cd3a5f275d16b6e9a9911d6d233442b372093652d7bc9a8edd040 | SOURCE_PIN |
| EV-CHECK-TASKPATH | AC5 | verification/CORE-PIPELINE-FIX-1/check-taskpath.log | | 1d1e36c90b551c9f93631d519517af7e36211b3dfd5f48bfbf399178cf6dd522 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/CORE-PIPELINE-FIX-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/CORE-PIPELINE-FIX-1 | verification/CORE-PIPELINE-FIX-1/resource-manifest.json | task-env 仅本 Task 数据根/日志/脚本（15 项 artifact 已 pin）；无删除/迁移/归档；frozen models 包与 BOOK-FIXTURE 原件零修改 |

## 交付与运行记录

- Owner：`baseline-scout`（DSH 委派，团队 task-35）。
- 交付形态：主仓工作树改动（未提交、未 push），涉及 `src/**` 3 文件 + `tests/**` 6 文件；`verification/CORE-PIPELINE-FIX-1/**` 证据 15 文件。
- **仓库状态提示（必须知悉）**：本 Task 执行期间另一路 `S4-CMD-BATCH-1` 集成把工作树中已完成的 `core_service.py` / `handlers.py`（常量与注入部分）一并提交进 HEAD `ed85c4173`；因此 Task 的完整 diff 应看 `git diff ce181ce0b -- src`（EV-SRC-BASE-DIFF），工作树剩余 diff 见 EV-SRC-WORKTREE-DIFF。未改写历史、未替他人提交。
- 复验环境：models 包 `FINAL-VALIDATION-1/.../core-sidecar/models`（只读）+ BOOK-FIXTURE 私有副本；脚本 `tools/verify_inproc.py`；两次整书（默认策略 / `policy=fail` 对照）+ 8 次逐页隔离运行。
- 回归命令与结果：`python -m pytest tests -q` → 3F/2753P/9S（失败集合同基线）；`apps/desktop-avalonia/scripts/test.ps1` → TEST PASS 162/162；`apps/desktop/frontend` `npx vitest run` → 60/567 pass。
- 遗留：① frozen sidecar 未重打包（发布步骤）；② stdio/调度线程路径异常（独立观察，3 份证据，建议另开诊断 Task）；③ translate 未接入，Run 止于 typed `PROVIDER_NOT_CONFIGURED`。

## Closeout Record

- Closeout date / DSH：待关闭时填写；Owner 交付日期 2026-10-27。
- canonical_evidence_status：`complete`（15 行 sha256 pin，commit 列留空）。
- resource_closeout_status：`pending`（task-env 保留引用；关闭时复核 `resource-manifest.json`）。
- 删除、迁移、归档数量/字节数：本 Task 无删除/迁移/归档。
- 未关闭项及保留原因：frozen 重打包与 stdio 调度异常为独立事项，见交付记录遗留 ①②。
- 当前指针清理：关闭时由 DSH 更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS

- 改动入 main：d85c4173 已含 color 装配注入 + handle_detect 语义 + 相关测试；剩余 src/application/tasks/service.py、handlers 补充、测试与证据由 DSH 提交 $c1。
- DSH 定向复跑 6 个相关测试文件：**73 passed**；实现方全量 pytest **3F/2753P/9S**（失败集合同基线、0 新增）。
- 同构建 8 页复验（frozen core_service.exe 2b36bfeb… 未改，PyInstaller 无法原地补丁，重打包属发布步骤）：pages1–3 detect/ocr/**color 3/3 completed**、term_extract 通过，止于 	ranslate PROVIDER_NOT_CONFIGURED（未到 render）；pages4–8 completed(0 region)；负向 policy=fail 保持旧 INVALID_INPUT。
- 遗留：① translate 未接入（Run 止于此，需 provider slice）；② 可复现独立异常——python -m bootstrap.core_service 调度线程内 detect StepRun 卡 running、下游 regionless ocr 报 INVALID_INPUT（进程内 execute_run 正常）：建议另开诊断 Task；③ 冻结 exe 未重打包（发布步）。
- 集成：aac638781。
