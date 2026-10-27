---
id: RUN-STORE-CACHE-RACE-FIX-1
title: 修复 SqlitePipelineStore 共享缓存跨线程对象替换竞态
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: sandbox-verify
owner: sandbox-verify
reviewer: dsh
depends_on: []
base_commit: 97de0fa99
branch: task/RUN-STORE-CACHE-RACE-FIX-1
worktree: G:/CODEX/New Manga.workspace/worktrees/RUN-STORE-CACHE-RACE-FIX-1
integration_commit: null
delivery_head: dadcf72b9d0feaf786e660d23ef28a63244060bf
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/RUN-STORE-CACHE-RACE-FIX-1
allowed_paths:
  - doc/tasks/RUN-STORE-CACHE-RACE-FIX-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - src/**
  - tests/**
  - doc/handoffs/RUN-STORE-CACHE-RACE-FIX-1-handoff.md
  - verification/RUN-STORE-CACHE-RACE-FIX-1/**
  - G:/CODEX/New Manga.workspace/task-envs/RUN-STORE-CACHE-RACE-FIX-1/**
  - G:/CODEX/New Manga.workspace/worktrees/RUN-STORE-CACHE-RACE-FIX-1/**
---

# RUN-STORE-CACHE-RACE-FIX-1：修复共享缓存跨线程对象替换竞态

## 背景（SCHEDULER-THREAD-DIAG-1 实证）

`SqlitePipelineStore._cache` 是跨线程共享可变 dict；`GetTaskProjection(fresh=True)` → `store.refresh()` 读 DB 后把 `_cache[run_id]` 替换为**新克隆**，执行线程接着用克隆提交（detect completed+backfill 只落克隆），`execute_run` 局部 run 未回填 → regionless ocr 报 `INVALID_INPUT`；旧对象随后整份 `_persist` 回写（last-writer-wins）→ 已提交 StepRun 回退 `running`。

复现：执行线程 + 100ms `GetTaskProjection(fresh=True)` 轮询 → 3/3 复现；frozen sidecar `2b36bfeb…` 同样复现。**GUI 当前不轮询故未触发，但属 latent 生产缺陷，重打包不能视为已修。**

## Acceptance Criteria

- [x] **AC1 最小修复**：`SqlitePipelineStore.refresh()` 只返回 `_read_run()` 的独立视图对象，不再 pop/替换 `_cache[run_id]`；`InMemoryPipelineStore.refresh()` 返回 `_detached_run()` 结构克隆；`GetTaskProjection(fresh=True)` 轮询保留、未降级；无 Core 语义/协议变更。单测 7 项：修复前 6F/1P → 修复后 7P。<<MET>>
- [x] **AC2 写入加固**：`run_json` 写入前 owner/修订 CAS（`_write_revision` + `_check_write_revision()`，`put`/`write_in_current_transaction` 同一守卫）；旧快照抛 `STALE_RUN_SNAPSHOT` 而非静默覆盖；无 Schema 变更。单测覆盖 stale 拒绝（put/事务内）与 owner 连续写接受。<<MET>>
- [x] **AC3 并发回归**：`tools/repro_scheduler.py`（真实 scheduler 线程 + 100 ms `projection-fresh` 轮询）：修复前 FAIL（8 卡 running、8 regionless INVALID_INPUT、8/8 任务 failed，EXIT=1）→ 修复后 PASS（0/0，与 cached/不轮询对照逐项一致，EXIT=0）；pytest 并发用例 `test_projection_fresh_polling_does_not_corrupt_execution` 修复前 FAIL → 修复后 PASS（3/3 重复）。精确满足「0 卡 running、0 regionless INVALID_INPUT」。<<MET>>
- [x] **AC4 回归**：同机同时段全量 A/B：pre-fix base **4F/2752P/9S/1 deselected** vs post-fix **4F/2760P/9S**，失败集合完全相同、0 新增（+8 = 本卡新增用例）；第 4 项为既有 flaky `test_sandbox_job_kills_grandchildren`（base 同跑同样失败，同树 6 次 pass/fail 交替）；辅助运行 3F/2761P/9S 与历史基线一致。`apps/desktop-avalonia/scripts/test.ps1` → **177/177 passed, 0 skipped**。<<MET>>
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS（`check-taskpath.log`）；证据 64-hex sha256 pin 见 `## Canonical Evidence`（commit 列 `-`，由 DSH 集成时按需补）；Handoff `doc/handoffs/RUN-STORE-CACHE-RACE-FIX-1-handoff.md`；Record Decision（缓存/归属模型、影响面、回退开关、限制）见 `REPORT.md` §8。<<MET>>

## 允许修改范围

**范围修正（owner 记录，供 DSH 复核）**：AC2/AC3 明确要求新增回归测试，原 `allowed_paths` 未含 `tests/**`；Handoff 按《协作协议》§5 固定写入 `doc/handoffs/RUN-STORE-CACHE-RACE-FIX-1-handoff.md`。两项已补入本卡 front matter，生产语义范围未扩大。

`src/**`（sqlite pipeline store / projection 读取 / 相关测试）、本卡、STATUS/PLAN/LEDGER、`verification/RUN-STORE-CACHE-RACE-FIX-1/**`、workspace。

## 禁止范围

不改协议/Host 契约/旧壳、不 push、不 gc/prune；不得用"禁用 fresh 轮询"绕过；不得放宽并发/输入校验。

## 实现摘要

| 文件 | 改动 |
|---|---|
| `src/infrastructure/sqlite/pipeline.py` | AC1：`refresh()`（L669）只返回独立视图，不再替换 `_cache`；AC2：`_write_revision`、`_adopt_revision()`（L627）、`_check_write_revision()`（L632）、`_write_run()` 写前 CAS（L429）与成功后递增（L529），过期快照抛 `STALE_RUN_SNAPSHOT`。 |
| `src/application/tasks/store.py` | AC1：`_detached_run()`（L386）结构克隆 + `InMemoryPipelineStore.refresh()`（L434）返回独立视图。 |
| `tests/pipeline/test_run_store_cache_race.py` | 新增 7 项 AC1/AC2 单测（视图独立、cache 不替换、stale 写入拒绝、owner 连续写接受）。 |
| `tests/pipeline/test_regionless_rebinding.py` | 新增 AC3 并发用例（SlowDetector/SlowOcr + 10 ms 投影轮询 + SQLite store + detect→回填→ocr 链）。 |

## Canonical Evidence

| ID | AC/场景 | 路径 | commit | sha256 (64-hex) | 类型 |
|---|---|---|---|---|---|
| EV-REPORT | AC1–AC5 总报告（含 Record Decision） | verification/RUN-STORE-CACHE-RACE-FIX-1/REPORT.md | - | afeeba14a0713b47a91e5f9c92e68df6e87b54c83231a748b3c33b929e8a8e07 | CANONICAL |
| EV-AB-MATRIX | AC3 修复前/后 A/B 矩阵 | verification/RUN-STORE-CACHE-RACE-FIX-1/ab-matrix.json | - | b73f34c5dcd577ab791a6e18b8b53b6ac7bc13fe854141dd8af517e821f221e1 | CANONICAL |
| EV-SRC-DIFF | AC1/AC2 源码 diff（base→delivery） | verification/RUN-STORE-CACHE-RACE-FIX-1/src-changes-vs-base.patch | - | 15fef9b9dadbe6c90f5c9f3af2de71033406cfa61ba707d1b4ba52a29b8bd77d | SOURCE_PIN |
| EV-RESOURCE-MANIFEST | AC5 资源清单 | verification/RUN-STORE-CACHE-RACE-FIX-1/resource-manifest.json | - | 05f33568397e8d4d888e63def8fd088d8edf1e45d07d1597645553d4da8b453c | SOURCE_PIN |
| EV-CHECK-TASKPATH | AC5 治理门禁日志 | verification/RUN-STORE-CACHE-RACE-FIX-1/check-taskpath.log | - | c4c135b87da18e2c5a79af06a4047be93b819ee029217c1bc547e5293d726fda | CANONICAL |
| EV-TOOL-REPRO | AC3 并发复现/判别工具 | verification/RUN-STORE-CACHE-RACE-FIX-1/tools/repro_scheduler.py | - | 59c000cebbb9d34e040d1500a7c56c2c694c00f8d9b4325e971bab6587d535e1 | CANONICAL |
| EV-DOTNET-SUMMARY | AC4 Avalonia 177/177 摘要 | verification/RUN-STORE-CACHE-RACE-FIX-1/test/avalonia-summary.json | - | 4293d4eeb35e6fb283211eec14378742872b5bd4df80d5a7f201d959fe551832 | CANONICAL |
| EV-DOTNET-LOG | AC4 dotnet test 日志 | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/dotnet-test.log | - | 5333ff6863c34621ad6fabd1a62e4e67236ccd5e401feafc0cdda737cebaac70 | CANONICAL |
| EV-FLAKY-RERUNS | AC4 既有 flaky 复跑证明 | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/flaky-plugin-sandbox-reruns.log | - | 4b059d0fdd2d6bf02c6f71ee432b5d052e3cdd6cc1982ba4f7f2070d30e876b1 | CANONICAL |
| EV-SANDBOX-MODULE | AC4 沙箱模块复跑（flake 说明） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/post-fix-plugin-sandbox-module.log | - | d60afa45b48821d7858b1cd2904e61eb3bc80483f0bee173c71ce3464a321ebc | CANONICAL |
| EV-PREFIX-PYTEST-FULL | AC4 pre-fix base 同机全量基线 | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/pre-fix-pytest-full-baseline.log | - | fbff48856fa5b72526056c7cb8790e54c03518bbaf4e41a60e1b412a801a1f7d | CANONICAL |
| EV-POSTFIX-PYTEST-FULL | AC4 post-fix 全量回归 | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/post-fix-pytest-full.log | - | ee24a106930454644f88944b1fbbe124446cce4ccb70c634f650f6ecbd390630 | CANONICAL |
| EV-POSTFIX-PYTEST-RUNA | AC4 辅助运行（flake 未触发） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/post-fix-pytest-full-runA-aux.log | - | 681bd5aa8a4ceb29328ce1f2238fefc94540e407e64cb7c94959f37d97d9c846 | CANONICAL |
| EV-PREFIX-UNIT | AC1/AC2 单测（修复前 6F/1P） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/pre-fix-pytest-unit.log | - | 4944442d5661f32551545dd10043626b1b8d88c9659af5ede41634353bb9ba22 | CANONICAL |
| EV-POSTFIX-UNIT | AC1/AC2 单测（修复后 7P） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/post-fix-pytest-unit.log | - | d9ff2a122f258d133172dc81be20188113edee731b271f6e5121ae9f47e4598e | CANONICAL |
| EV-PREFIX-CONC | AC3 并发 pytest（修复前 FAIL） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/pre-fix-pytest-concurrency.log | - | a386f21d7e71b1383cdc17311c780ee3c6cb6b19d865e008cab1ea8c590db272 | CANONICAL |
| EV-POSTFIX-CONC | AC3 并发 pytest（修复后 PASS） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/post-fix-pytest-concurrency.log | - | a46b728d2bc7651525fa75f0aeb46e6185b36f058f0be31d771e37823b61e124 | CANONICAL |
| EV-PREFIX-REPRO-LOG | AC3 端到端判别（EXIT=1） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/pre-fix-repro-projection-fresh.log | - | 494c5f97b18b6998f9abbbd3240d783de711adc47c2a46d19371b32f6246c4c6 | CANONICAL |
| EV-POSTFIX-REPRO-LOG | AC3 端到端判别（EXIT=0） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/post-fix-repro-projection-fresh.log | - | 61b1e0d0f9ab7d51baedc9d2c8d66f090aa027a6caea202210b9c5a45c5ca070 | CANONICAL |
| EV-PREFIX-CACHED-LOG | AC3 cached 对照（EXIT=0） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/pre-fix-repro-cached-control.log | - | f41783672d50652ce3b133b2c1b93133f6cb6432abc929c1b203a5855968f63d | CANONICAL |
| EV-POSTFIX-CACHED-LOG | AC3 cached 对照（EXIT=0） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/post-fix-repro-cached-control.log | - | f2233bfc14dee9860b7cc8fa823a116f08b7dbfa095df3650275839b50332be5 | CANONICAL |
| EV-POSTFIX-NOPOLL-LOG | AC3 不轮询对照（EXIT=0） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/post-fix-repro-nopoll-control.log | - | dbf1665c837e7b0bc86c8c8c58cb8733857fa8a629a57c46f002511fe7cce91e | CANONICAL |
| EV-PREFIX-REPRO | AC3 修复前原始结果（FAIL） | verification/RUN-STORE-CACHE-RACE-FIX-1/repro/pre-fix-projection-fresh.json | - | 1d0cbbf5f414aa75d441084cdea63e25deef10f7b3adc3783ccd53f06cfeecdc | CANONICAL |
| EV-POSTFIX-REPRO | AC3 修复后原始结果（PASS） | verification/RUN-STORE-CACHE-RACE-FIX-1/repro/post-fix-projection-fresh.json | - | 0f2869a87634909857e90a6545311ed7890ae820efd84b35b87985e011e5151d | CANONICAL |
| EV-PREFIX-CACHED | AC3 修复前 cached 对照 | verification/RUN-STORE-CACHE-RACE-FIX-1/repro/pre-fix-cached-control.json | - | b8adbc8dc4107ab3a8c07b63c5c46f09de7a4b4c2548745f8c20e58e060baaf5 | CANONICAL |
| EV-POSTFIX-CACHED | AC3 修复后 cached 对照 | verification/RUN-STORE-CACHE-RACE-FIX-1/repro/post-fix-cached-control.json | - | 5dd9ae79e2567a216527bdf6079eb3617d5c4cb4a246bed0cc2666813ee9d27b | CANONICAL |

pin 口径：sha256 为 worktree 字节（commit 列 `-`；交付提交见 front matter `delivery_head`，集成 commit 由 DSH 填写）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/RUN-STORE-CACHE-RACE-FIX-1 | PRESERVE_REFERENCED | 同左 | verification/RUN-STORE-CACHE-RACE-FIX-1/resource-manifest.json | task-env 仅本 Task 数据根/日志/脚本；fixture 与 models 只读（原件零修改）；无删除/迁移/归档 |

## 交付与运行记录

- Owner：`sandbox-verify`（DSH 委派，team task-39）；实现提交 **dadcf72b9d0feaf786e660d23ef28a63244060bf**（分支 `task/RUN-STORE-CACHE-RACE-FIX-1`，基于 HEAD `9ef53f24d`）；本卡、Handoff、证据为后续文档提交。
- **生命周期说明**：本 Task 仍在 Plan 的 READY DAG 中，按 `check.ps1` 规则保持 `status: ready`（READY DAG 只允许 ready）；交付已完成（`delivery_head` 已固定、`canonical_evidence_status: complete`），`in_review` 由 DSH 在移出 READY DAG 时推进。
- 交付内容：`src/**` 2 文件（+91/−8）、`tests/**` 2 文件（新增 7 项 + 并发 1 项）、本卡、Handoff、`verification/RUN-STORE-CACHE-RACE-FIX-1/**` 证据。
- 回归命令与结果：`python -m pytest tests -q` 同机 A/B（pre-fix base 4F/2752P/9S/1 deselected → post-fix 4F/2760P/9S，失败集合同、0 新增）；`pwsh -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <私有>` → 177/177。
- 复验环境：BOOK-FIXTURE-1 `isolated-data` 私有副本 + FINAL-VALIDATION-1 models（只读）+ 独立 `NEWMANGA_EVIDENCE_DIR`；未触碰用户真实数据根。
- 未 push、未 gc/prune；临时 pre-fix worktree（base 判别证据）按 Worktree Safety Inventory 规则保留于 task-env（不删除、不 prune），关闭时由 DSH 按 Task 资源处置。

## Closeout Record

- Closeout date / DSH：待关闭时填写；Owner 交付日期 2026-10-27。
- canonical_evidence_status：`complete`（Canonical Evidence 表 sha256 pin；manifest 与 check log 的 pin 在本文件生成时回填）。
- resource_closeout_status：`pending`（task-env 保留引用；关闭时按 `resource-manifest.json` 复核）。
- 删除、迁移、归档：本 Task 无删除/迁移/归档；临时 pre-fix worktree 保留引用（待 DSH closeout 处置）。
- 未关闭项：① frozen sidecar 重打包属发布步骤；② 修订 CAS 为单进程/单 store 实例内存态（限制见 REPORT §8）；详见 Handoff 遗留。
- Review：待 DSH 指定独立 Reviewer（owner 为实现者，不得自审）。
