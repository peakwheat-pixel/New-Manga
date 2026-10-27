---
id: FLAKY-PYTEST-1
title: 稳定 3 个既有 flaky 失败
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_round_2_5
suggested_owner: sandbox-verify
owner: sandbox-verify
reviewer: dsh
depends_on: []
base_commit: 13cf26f6c
branch: task/FLAKY-PYTEST-1
worktree: G:/CODEX/New Manga.workspace/worktrees/FLAKY-PYTEST-1
integration_commit: ba4080752
delivery_head: 4b0ac1831928a374ece45317e67933b9e47bc57e
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/FLAKY-PYTEST-1
allowed_paths:
  - doc/tasks/FLAKY-PYTEST-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - src/**
  - tests/**
  - doc/handoffs/FLAKY-PYTEST-1-handoff.md
  - verification/FLAKY-PYTEST-1/**
  - G:/CODEX/New Manga.workspace/task-envs/FLAKY-PYTEST-1/**
  - G:/CODEX/New Manga.workspace/worktrees/FLAKY-PYTEST-1/**
---

# FLAKY-PYTEST-1：稳定 3 个既有 flaky 失败

## 背景
pytest 长期稳定 3F/2772P/9S（如 `test_detection_manga_real` 两项、`test_sandbox_job_kills_grandchildren` 等，具体以当前失败名为准），每轮记录「0 新增」但始终红。需要根治或显式隔离。

## Acceptance Criteria

- [x] **AC1 复现与归因**：以 base `170878dc4` 实测基线 **3F/2772P/9S**：①`test_detection_manga_real.py::test_real_detection_returns_block_candidates` ②同文件 `::test_real_blank_page_yields_zero_candidates` ③`test_workbench_viewmodel.py::test_pause_shows_optimistic_feedback_immediately`。归因：①② = **环境（dev venv 运行时版本缺口）**：本机 transformers 4.48.3 无 `RTDetrV2ForObjectDetection`，而快照为 RT-DETR-v2（config `transformers_version=4.49.0`）、仓库 pin `transformers==5.17.0`，产品默认 ONNX 后端、torch 为可选 fallback；③ = **真 bug**：`WorkbenchViewModel.continueRun()` 错误地按 `run.status is PENDING` 判断是否启动 worker，而 `control_run("continue")` 的契约应答是 `ControlResult(status=PENDING)`、run 实际置 RUNNING+resume 标记 → worker 永不启动。另观测 `test_sandbox_job_kills_grandchildren` 为 OS 异步回收时序 flaky（探针 6/6 孙进程 ~20ms 被杀；基线通过）。证据：`logs/ac1-prefix-*.log`、`logs/ac1-env-probe.log`、`logs/ac1-sandbox-probe.log`。<<MET>>
- [x] **AC2 处置**：真 bug → 修复 `src/ui/viewmodels/workbench/viewmodel.py`（`continueRun` 以控制结果 `PENDING` 作为 worker 准入信号，附根因注释）；环境依赖 → `tests/providers/test_detection_manga_real.py` 增加**机器可判定** skip（`hasattr(transformers,'RTDetrV2ForObjectDetection')`，reason 含实际版本/所需类/requirements pin/修复指引，`-rs` 可见，非静默）；时序 flaky → `tests/infrastructure/test_plugin_sandbox.py` 2 s 固定窗口改为 **20 s 有界等待**（死亡即通过，真实泄漏仍失败）。未改协议/Host/旧壳/持久化语义；未引入无上限重试。<<MET>>
- [x] **AC3 稳定性**：处理后**连续 5 次**全量 `python -m pytest tests -q`（顺序、无并行负载）结果完全一致：**0 failed / 2773 passed / 10 skipped**，EXIT=0（5/5 各带 EXIT 记录，`distinct_results=[[0,2773,10]]`，`consistent=true`）；另 `-rs` 全量运行固化 10 项 skip 集合。证据：`logs/run1..5-pytest.log`、`ac3-five-runs.json`、`logs/run6-skipset.log`。<<MET>>
- [x] **AC4 回归**：`apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <私有>` → **225/225 passed, 0 skipped**（coreclient 40 / host 76 / app 109）；`npx vitest run` → **60 files / 567 tests passed**（frontend tracked 源两树零 diff，主 checkout 安装运行，见 REPORT §5）。证据：`test/avalonia-summary.json`、`logs/ac4-dotnet-test.log`、`logs/ac4-vitest.log`。<<MET>>
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS（`check-taskpath.log`）；证据 64-hex sha256 pin 见 `## Canonical Evidence`（pin 口径=提交内 blob 字节，commit 列=包含该文件的交付/证据提交）；Handoff `doc/handoffs/FLAKY-PYTEST-1-handoff.md`；Record Decision（flaky 政策）见 `REPORT.md` §8。<<MET>>

## 允许修改范围

`src/**`（仅 UI 视图模型控制路径）、`tests/**`（三个失败/观察项测试）、本卡、STATUS/PLAN/LEDGER、`verification/FLAKY-PYTEST-1/**`、workspace。
（卡面修正：原 front matter `  - src/**; tests/**` 为单行合并写法，已拆为两条；并补 `doc/handoffs/FLAKY-PYTEST-1-handoff.md`，与《协作协议》§5 一致，供 DSH 复核。）

## 禁止范围

不改协议/Host 契约/旧壳、不 push、不 gc/prune；不得伪造结果；**不得把任何 API key/secret 写入仓库、日志或证据**。

## 实现摘要

| 文件 | 改动 |
|---|---|
| `src/ui/viewmodels/workbench/viewmodel.py` | `continueRun()` 改用 `result.status is PipelineRunStatus.PENDING` 作为 worker 准入条件（原 `self._run.status` 判定永假）；附 FLAKY-PYTEST-1 根因注释。 |
| `tests/providers/test_detection_manga_real.py` | importorskip 后新增 `hasattr(transformers,"RTDetrV2ForObjectDetection")` 机器可判定 skip（reason 含版本/pin/修复指引，module 级与文件既有风格一致）。 |
| `tests/infrastructure/test_plugin_sandbox.py` | 孙进程回收断言：固定 2 s 窗口 → 20 s 有界等待（含 OS 异步回收依据注释）。 |

## Canonical Evidence

| ID | AC/场景 | 路径 | commit | sha256 (64-hex) | 类型 |
|---|---|---|---|---|---|
| EV-REPORT | AC1–AC5 | verification/FLAKY-PYTEST-1/REPORT.md | 83a44963fbf59acca57f674c68a0159e27f655e0 | df8157239f068f5b70c2076aaf35638b52f3da044cf3e9190761c4cf84028910 | CANONICAL |
| EV-AC3-SUMMARY | AC3 5 次汇总 | verification/FLAKY-PYTEST-1/ac3-five-runs.json | 83a44963fbf59acca57f674c68a0159e27f655e0 | c2ef4aec1c3a2ba230aca1ce38f5cc3f3712d1d00952ab6573df00c2aa8c77b2 | CANONICAL |
| EV-BASELINE | AC1 基线 3F | verification/FLAKY-PYTEST-1/logs/run0-baseline.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | e90b228502cb3f92ff61459a0e8bac40ce4c943f44e5a6eba55746d8498626ed | CANONICAL |
| EV-RUN1 | AC3 run1 | verification/FLAKY-PYTEST-1/logs/run1-pytest.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | d999510a37b27a72dd29c162d85d6f3b870b707868cb938015497d0f05955446 | CANONICAL |
| EV-RUN2 | AC3 run2 | verification/FLAKY-PYTEST-1/logs/run2-pytest.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | 0e86209245a541e422a1e2392f9f4e721ee85b750a7dda67fc997ad9e1958994 | CANONICAL |
| EV-RUN3 | AC3 run3 | verification/FLAKY-PYTEST-1/logs/run3-pytest.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | 1ae342667df2914ca8b825aa07554b1c633cd188c0048c8c67086fc9468b8f54 | CANONICAL |
| EV-RUN4 | AC3 run4 | verification/FLAKY-PYTEST-1/logs/run4-pytest.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | 1ddf3fd28ae61117419c22b8c2d915e95c989d5cde71f3987c54f57c6a85d42d | CANONICAL |
| EV-RUN5 | AC3 run5 | verification/FLAKY-PYTEST-1/logs/run5-pytest.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | 4fbc198d2cfdeb5eea5d3018484a7fe4efcde5f00c052e4b22cc42757e35412f | CANONICAL |
| EV-SKIPSET | AC3 skip 集合 | verification/FLAKY-PYTEST-1/logs/run6-skipset.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | 8c98c0154732e6c818feda3d7ea1828ae04feb72bb42d92975902f8a9b8fddee | CANONICAL |
| EV-PREFIX-DETECTION | AC1 失败 1/2 | verification/FLAKY-PYTEST-1/logs/ac1-prefix-detection.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | d6be9d2990c197cb3feff3ac8d586c782f1825f697da610ac665e787dfd80e7a | CANONICAL |
| EV-PREFIX-WORKBENCH | AC1 失败 3 | verification/FLAKY-PYTEST-1/logs/ac1-prefix-workbench-pause.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | 7c4c741afcc9d3865cfbc83e395dceb5cbee49574325c0727dc26d8114f80e5f | CANONICAL |
| EV-PREFIX-SANDBOX | AC1 观察项 | verification/FLAKY-PYTEST-1/logs/ac1-prefix-sandbox.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | 7279ecbe3c39251320b7d4f4281651191aa07f27aa57b830e6e4453a9b49f693 | CANONICAL |
| EV-ENV-PROBE | AC1 环境事实 | verification/FLAKY-PYTEST-1/logs/ac1-env-probe.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | b265f5906b4d975c13ba5bbdcd3c69a1bd49f300818116c45234a89fe69c08f8 | CANONICAL |
| EV-SANDBOX-PROBE | AC1 时序实测 | verification/FLAKY-PYTEST-1/logs/ac1-sandbox-probe.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | f6295f75004886e95acf10e5eaeb5c937bf9e446c4273e91a592d94d3e3dbca9 | CANONICAL |
| EV-SANDBOX-6X | AC1 单测重跑 | verification/FLAKY-PYTEST-1/logs/ac1-sandbox-single-6x.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | 902c3c6880e2a32c47f67049ecfaebfbd5caa6aa5c31e6dcd2ec4bc4063e88bf | CANONICAL |
| EV-POSTFIX-DETECTION | AC2 处置验证 | verification/FLAKY-PYTEST-1/logs/ac2-postfix-detection.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | 5213988bbdb294fd58adf96086cec90d7648af326195c1fdcbb0389b9d31395e | CANONICAL |
| EV-POSTFIX-WORKBENCH | AC2 处置验证 | verification/FLAKY-PYTEST-1/logs/ac2-postfix-workbench-pause.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | 481ff31494a441089b93508fc962787fbac128992b5afd09e34a1690320aeaac | CANONICAL |
| EV-POSTFIX-SANDBOX | AC2 处置验证 | verification/FLAKY-PYTEST-1/logs/ac2-postfix-sandbox.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | 25ef3e49878a32dec158f1df6834650cf2081e7205de8fa1a69a36bd91b34e57 | CANONICAL |
| EV-DOTNET-LOG | AC4 | verification/FLAKY-PYTEST-1/logs/ac4-dotnet-test.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | 32d08c96daa30d331f950aa6857ff6c20e269d33ddd5f33890ac8d66dfe6db70 | CANONICAL |
| EV-DOTNET-SUMMARY | AC4 | verification/FLAKY-PYTEST-1/test/avalonia-summary.json | 83a44963fbf59acca57f674c68a0159e27f655e0 | 5a83b7a3a5bb6f5ff1067b6e5ca62ecc0ee28d4ef4dbe54a95e8a04ef3f60b53 | CANONICAL |
| EV-VITEST | AC4 | verification/FLAKY-PYTEST-1/logs/ac4-vitest.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | 410bccc4cbd24608c4df0564e178b6e746261a7889d1048e6266d2e64c37a01e | CANONICAL |
| EV-TOOL-RUN5 | AC3 工具 | verification/FLAKY-PYTEST-1/tools/run_five.py | 83a44963fbf59acca57f674c68a0159e27f655e0 | 8d7544b8d22e85acc87726f30c78745aaad77eab5a261a1374dfd40cd3480b48 | CANONICAL |
| EV-TOOL-PROBE | AC1 工具 | verification/FLAKY-PYTEST-1/tools/probe_sandbox_tree.py | 83a44963fbf59acca57f674c68a0159e27f655e0 | d0d640d71620f1012b45e4a892b0a1a1d17d414cc2e2a010f41c78b53290d4fa | CANONICAL |
| EV-SRC-DIFF | AC2 | verification/FLAKY-PYTEST-1/src-changes-vs-base.patch | 83a44963fbf59acca57f674c68a0159e27f655e0 | 6f54bc0ab9e11b235b2f7e0976f39c52d87ea97559752b82b674edc5e55c6bf2 | SOURCE_PIN |
| EV-RESOURCE-MANIFEST | AC5 | verification/FLAKY-PYTEST-1/resource-manifest.json | 83a44963fbf59acca57f674c68a0159e27f655e0 | ec976e53b0b92131155c0f15fd39bfbc91d7bbd51ae38b95a991811c246f4fbb | SOURCE_PIN |
| EV-CHECK-TASKPATH | AC5 | verification/FLAKY-PYTEST-1/check-taskpath.log | 83a44963fbf59acca57f674c68a0159e27f655e0 | 2230fa7d416869ffdda5fbe24d8d41aa7b9a430cb984635b8f801159fb46c318 | CANONICAL |

pin 口径：sha256 为**提交内 blob 字节**（与全新 checkout 落盘字节一致）；commit 列指向包含该文件的交付/证据提交（集成 commit 由 DSH 填写）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/FLAKY-PYTEST-1 | PRESERVE_REFERENCED | 同左 | verification/FLAKY-PYTEST-1/resource-manifest.json | task-env 仅本 Task 日志/证据/脚本与临时 pre-fix worktree；无删除/迁移/归档 |

## 交付与运行记录

- Owner：`sandbox-verify`（DSH 委派，team task-50）；实现提交见 front matter `delivery_head`（分支 `task/FLAKY-PYTEST-1`，基于 HEAD `170878dc4`）；本卡、Handoff、证据为后续文档提交。
- **生命周期说明**：本 Task 仍在 Plan 的 READY DAG 中，按 `check.ps1` 规则保持 `status: ready`；交付已完成（`delivery_head`、`canonical_evidence_status: complete`），`in_review` 由 DSH 在移出 READY DAG 时推进。
- 交付内容：`src/**` 1 文件（+9/−1）、`tests/**` 2 文件（+27/−3）、本卡、Handoff、`verification/FLAKY-PYTEST-1/**` 证据。
- 回归口径：单机顺序 5 次全量 pytest（git head 固定，无并行负载）；test.ps1 225/225；vitest 60/567。
- 复验环境：本机 dev venv（Python 3.14.6，transformers 4.48.3/torch 2.11.0——**低于 requirements pin**，见 Handoff 遗留）；未改动机器环境、未 push、未 gc/prune。
- 临时 pre-fix worktree（base `170878dc4`，用于 AC1 修复前判别证据）按 Worktree Safety Inventory 规则保留于 task-env（不删除、不 prune），关闭时由 DSH 按 Task 资源处置。

## Closeout Record

- Closeout date / DSH：待关闭时填写；Owner 交付日期 2026-10-27。
- canonical_evidence_status：`complete`（上表 sha256 pin；manifest 与 check log 的 pin 在生成时回填）。
- resource_closeout_status：`pending`（task-env 保留引用；关闭时按 `resource-manifest.json` 复核）。
- 删除、迁移、归档：本 Task 无删除/迁移/归档；临时 pre-fix worktree 保留引用（待 DSH closeout 处置）。
- 未关闭项：① 本机 dev venv 落后 requirements pin（transformers/torch；2 个 detection 测试以显式 skip 待真跑）；② sandbox 20 s 上界为经验值；详见 Handoff 遗留。
- Review：待 DSH 指定独立 Reviewer（owner 为实现者，不得自审）。
## Review（DSH 集成复核，2026-10-27）— PASS

- ① detection 两项：环境依赖（dev venv transformers 4.48.3 缺 RTDetrV2，快照需 ≥4.49；requirements pin 5.17.0）→ **机器可判定显式 skip**（reason 含版本/需求/修复指引，-rs 可见），非静默。
- ② workbench 	est_pause_shows_optimistic_feedback_immediately：**真 bug**——VM continueRun 误按 un.status 判 worker 准入，而 control_run("continue") 返回 ControlResult(PENDING) 且 run 置 RUNNING → worker 永不启动；已修（改用 esult.status + 根因注释）。
- ③ sandbox 孙进程测试：OS 异步回收时序 flaky → 2s 固定窗口改 **20s 有界等待**，断言未放宽（探针 6/6 孙进程 ~20ms 被杀）。
- 稳定性：**连续 5 次全量 pytest 0F/2773P/10S、EXIT=0**（219.7/227.8/210.3/204.1/204.3s，distinct=[[0,2773,10]] consistent=true）；-rs 固化 10 项 skip（9 既有 + 1 新增，均机器可判定）。
- AC4：test.ps1 225/225（实现方在干净 worktree）；vitest 60/567 不变。
- 遗留：dev venv 落后 pin（2 个 detection 测试待装 requirements-dev 后真跑，由 DSH 决策）；sandbox 20s 为经验上界。
- 集成：ba4080752。
