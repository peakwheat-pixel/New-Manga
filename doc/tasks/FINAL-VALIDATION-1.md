---
id: FINAL-VALIDATION-1
title: 终验与发布重建——按新 spec 重建侧车 + 重打包 + 许可复验 + 全量回归
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: null
reviewer: dsh
depends_on: [CORE-SLIM-2, RELEASE-PACKAGE-1]
base_commit: 78784afaf
branch: task/FINAL-VALIDATION-1
worktree: G:/CODEX/New Manga.workspace/worktrees/FINAL-VALIDATION-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FINAL-VALIDATION-1
allowed_paths:
  - doc/tasks/FINAL-VALIDATION-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - scripts/**
  - packaging/**
  - verification/FINAL-VALIDATION-1/**
  - G:/CODEX/New Manga.workspace/task-envs/FINAL-VALIDATION-1/**
  - G:/CODEX/New Manga.workspace/worktrees/FINAL-VALIDATION-1/**
---

# FINAL-VALIDATION-1：终验与发布重建

## 目标

把「新架构 + 新 Core 闭包」真正装成一个可运行发布件并全量复核。

## Acceptance Criteria

- [x] **AC1 侧车重建**：用新 spec（`packaging/m2ac5/core_sidecar.spec`，无 Qt/无 torch）重建 `core_service`/`host_bridge` 等 entry，记录体积表；启动/协议 smoke 通过。→ **MET**：构建 37.1s exit=0；整包 828.6 MiB / **Core 运行时 186.3 MiB（不含 models）**；Qt 0 / torch 栈 0；能力 smoke **7/7 PASS**（`sidecar-meter`… 见 `sidecar-measure.json`、`capability-smoke.json`）。
- [x] **AC2 重打包**：`apps/desktop-avalonia/scripts/package.ps1` 产出安装包（含 Core 侧车与模型分发策略），体积 ≤2GB（含基础模型）/≤150MB（不含模型）；包内许可三件套逐字节一致。→ **MET**：base zip **97.75 MB ≤150**（sidecar 186.31 MiB 内含、模型分离策略）；models zip **690.94 MB ≤2 GB**（sidecar 828.59 MiB + models 642.3 MiB 内含）；许可三件套两包均逐字节一致。
- [x] **AC3 全量回归**：`scripts/test.ps1` 全绿；pytest 相对基线 3F/2739P/9S 无新增失败；旧壳 vitest 60/567 不变；`command_allowlist` parity 快照 `--check` 零漂移。→ **MET**：test.ps1 **102/102**；pytest **3F/2739P/9S（0 新增）**；vitest **60/60 文件 567/567 用例**；parity `--check` **PASS（66 命令零漂移）**。
- [x] **AC4 安装 smoke**：安装→启动→窗口→退出无残留（复用 RELEASE-PACKAGE-1 的 `install-smoke.ps1`，新包复跑）。→ **MET**：base 与 models 两包均 PASS（窗口句柄出现 / console 0 / exit 0 / 残留进程 0 / 安装目录已删除 / sidecar_bundled=true / models_bundled 按变体）。
- [x] **AC5 收尾文档**：AD-002 标记 S0–S5 完成；`DISPLAY-PERF-DECISION-1` 关闭；产出 `MANUAL_VERIFY.md` 最新版（真机 5 项）。→ **MET**：AD-002 §8 标题改「已全部完成」+ §8.1 完成表；DISPLAY-PERF-DECISION-1 `status: done` + Closeout Record；`apps/desktop-avalonia/docs/MANUAL_VERIFY.md` 最新版（NOT_RUN by agent）。
- [x] **AC6 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。→ **MET**：`check.ps1 -TaskPath` PASS；pin 见下；`doc/handoffs/FINAL-VALIDATION-1-handoff.md`。

## 允许修改范围

`apps/desktop-avalonia/**`、`scripts/**`、`packaging/**`、本卡、STATUS/PLAN/LEDGER、`verification/FINAL-VALIDATION-1/**`、workspace。

## 禁止范围

不改协议/命令语义/Host 契约；不删除能力；不 push；不 gc/prune；不伪造成安装成功。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `packaging/m2ac5/build_sidecar.ps1 -Force` + `measure_bundle.py` + `capability_smoke.py`（无标签副本） | build venv | **PASS**：37.1s；186.3 MiB（不含模型）；smoke 7/7 | `sidecar-build.log`、`sidecar-measure.json`、`capability-smoke.json` |
| AC2 | `apps/desktop-avalonia/scripts/package.ps1`（base 与 `-WithModels`）+ 逐字节许可比对 | 干净 out 目录 | **PASS**：97.75 MB / 690.94 MB；许可一致 | `package-facts.json`、`package-summary-{base,models}.json` |
| AC4 | `install-smoke.ps1`（base 与 models 包） | 隔离安装目录 | **PASS**：窗口/exit0/无残留/sidecar_bundled | `install-smoke.json`、`install-smoke-models.json` |
| AC3 | `python -m pytest -q` | dev env | **PASS**：3F/2739P/9S（0 新增） | `pytest.log` |
| AC3 | `pwsh -File apps/desktop-avalonia/scripts/test.ps1 -SidecarDirectory <副本>` | .NET 9 | **PASS**：102/102 | `scripts-test.log` |
| AC3 | `npm install && npx vitest run`（旧壳前端） | node/npm | **PASS**：60/60 文件、567/567 用例 | `vitest.log` |
| AC3 | `python apps/desktop-avalonia/scripts/extract-command-surface.py --check` | — | **PASS**：66 命令零漂移 | `parity-check.log` |
| AC6 | `pwsh -File tools/governance/check.ps1 -TaskPath doc/tasks/FINAL-VALIDATION-1.md` | — | PASS | 见 Handoff |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/FINAL-VALIDATION-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/FINAL-VALIDATION-1 | `out/`（base 97.75MB + models 690.94MB 两包，sha256 见 `verification/FINAL-VALIDATION-1/package-facts.json`）、`sidecar-copy/`、`install*/`（smoke 后已卸载） | 构建/打包/安装 smoke 均引用该 task-env；包件为发布候选，关闭时按裁决保留或归档 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
