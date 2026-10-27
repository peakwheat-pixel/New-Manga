---
id: RUN-STORE-CACHE-RACE-FIX-1
title: 修复 SqlitePipelineStore 共享缓存跨线程对象替换竞态
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: sandbox-verify
owner: sandbox-verify
reviewer: dsh
depends_on: []
base_commit: 97de0fa99
branch: task/RUN-STORE-CACHE-RACE-FIX-1
worktree: G:/CODEX/New Manga.workspace/worktrees/RUN-STORE-CACHE-RACE-FIX-1
integration_commit: 2980608e0
delivery_head: dadcf72b9d0feaf786e660d23ef28a63244060bf
canonical_evidence_status: complete
resource_closeout_status: complete
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
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS（`check-taskpath.log`）；证据 64-hex sha256 pin 见 `## Canonical Evidence`（commit 列=包含该文件的交付/证据提交）；Handoff `doc/handoffs/RUN-STORE-CACHE-RACE-FIX-1-handoff.md`；Record Decision（缓存/归属模型、影响面、回退开关、限制）见 `REPORT.md` §8。<<MET>>

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

| ID | AC/场景 | path | commit | sha256 (64-hex) | 类型 |
|---|---|---|---|---|---|
| EV-REPORT | AC1–AC5 总报告（含 Record Decision） | verification/RUN-STORE-CACHE-RACE-FIX-1/REPORT.md | 8ef319b9aadc5bac30a73eb5599b5b0e9c053602 | c0285723e3ad6e6be92d58780ce5437e1d1df869a68bdc40823c4d66d392f232 | CANONICAL |
| EV-AB-MATRIX | AC3 修复前/后 A/B 矩阵 | verification/RUN-STORE-CACHE-RACE-FIX-1/ab-matrix.json | e35238075 | e2966644877429ffe6b1c6a186a4d2202a1a4578f40043a1268209a5eb8fd9e3 | CANONICAL |
| EV-SRC-DIFF | AC1/AC2 源码 diff（base→delivery） | verification/RUN-STORE-CACHE-RACE-FIX-1/src-changes-vs-base.patch | e35238075 | d95791215a511eab6d95f27dc9c251f147df3b4f7cee597a0fbc5705c4aa31bf | SOURCE_PIN |
| EV-RESOURCE-MANIFEST | AC5 资源清单 | verification/RUN-STORE-CACHE-RACE-FIX-1/resource-manifest.json | 8ef319b9aadc5bac30a73eb5599b5b0e9c053602 | eedad51b70f339f32825713997de26050d7a2c692e711fe648790f0af92d62ad | SOURCE_PIN |
| EV-CHECK-TASKPATH | AC5 治理门禁日志 | verification/RUN-STORE-CACHE-RACE-FIX-1/check-taskpath.log | e35238075 | 507142f9f823e4526b8a4e8ff5aebd391140f391cda1702fae1e181145abdc27 | CANONICAL |
| EV-TOOL-REPRO | AC3 并发复现/判别工具 | verification/RUN-STORE-CACHE-RACE-FIX-1/tools/repro_scheduler.py | e35238075 | 59c000cebbb9d34e040d1500a7c56c2c694c00f8d9b4325e971bab6587d535e1 | CANONICAL |
| EV-DOTNET-SUMMARY | AC4 Avalonia 177/177 摘要 | verification/RUN-STORE-CACHE-RACE-FIX-1/test/avalonia-summary.json | e35238075 | f13df036b8593d60777b313f1d9da417152604061932823c16b05db319f7c452 | CANONICAL |
| EV-DOTNET-LOG | AC4 dotnet test 日志 | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/dotnet-test.log | e35238075 | b18a59399deaba0bc59f9662a725faa27ae5cb7dfb66a996f971917509780729 | CANONICAL |
| EV-FLAKY-RERUNS | AC4 既有 flaky 复跑证明 | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/flaky-plugin-sandbox-reruns.log | e35238075 | 89a4f4456f2a7e4aaccf8891d5e50a57fa57b91298c974fb62f226ff058cdca8 | CANONICAL |
| EV-SANDBOX-MODULE | AC4 沙箱模块复跑（flake 说明） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/post-fix-plugin-sandbox-module.log | e35238075 | b5e2f3f6ce2b9999a7512b3626939b62209e8291f046b2cc85875bbd04d4bede | CANONICAL |
| EV-PREFIX-PYTEST-FULL | AC4 pre-fix base 同机全量基线 | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/pre-fix-pytest-full-baseline.log | e35238075 | 92eb673d3b1b61e62b273ba1d2528dd13344f3d9e748f229ad1bd3b9f234d277 | CANONICAL |
| EV-POSTFIX-PYTEST-FULL | AC4 post-fix 全量回归 | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/post-fix-pytest-full.log | e35238075 | 2b78a6d3a9c7f2bcf24fc15e40d055329f09f7f61fc4312738d377099630acb9 | CANONICAL |
| EV-POSTFIX-PYTEST-RUNA | AC4 辅助运行（flake 未触发） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/post-fix-pytest-full-runA-aux.log | e35238075 | f424d4b62fdac0150d611c90f8f6b2e5481179e21caae1a32ccf35dae9716509 | CANONICAL |
| EV-PREFIX-UNIT | AC1/AC2 单测（修复前 6F/1P） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/pre-fix-pytest-unit.log | e35238075 | dd8e1c285415a619759c521e5c92e1258ab188b1fcb9ed1489053064e6e94c80 | CANONICAL |
| EV-POSTFIX-UNIT | AC1/AC2 单测（修复后 7P） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/post-fix-pytest-unit.log | e35238075 | 76647283294b446393c65aede3e16c96a3c64ccf563a063ad62ba32e0dfe43e9 | CANONICAL |
| EV-PREFIX-CONC | AC3 并发 pytest（修复前 FAIL） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/pre-fix-pytest-concurrency.log | e35238075 | ca7797ee9e666a6b52959a425dfd72d4ed2ea3c90abb59a5f4ae566392cb9b39 | CANONICAL |
| EV-POSTFIX-CONC | AC3 并发 pytest（修复后 PASS） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/post-fix-pytest-concurrency.log | e35238075 | 5c97a8cbf525bf887cd41e06c978cc28e3c8b961f8149025d90c9adb4a32dfe3 | CANONICAL |
| EV-PREFIX-REPRO-LOG | AC3 端到端判别（EXIT=1） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/pre-fix-repro-projection-fresh.log | e35238075 | d74472342d27603b239e9346f16324573bf320c67bd5e5ce7ed4d06c0ea3b1f7 | CANONICAL |
| EV-POSTFIX-REPRO-LOG | AC3 端到端判别（EXIT=0） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/post-fix-repro-projection-fresh.log | e35238075 | b54414aa745ba8de85ef1e0376aae779a3c7ab1e8191120657c3f7fb352ad603 | CANONICAL |
| EV-PREFIX-CACHED-LOG | AC3 cached 对照（EXIT=0） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/pre-fix-repro-cached-control.log | e35238075 | 67bf3dfb4e46bff5db4d9a0a97cc0c1a63cc90fca474f477c1f394c2454aad5c | CANONICAL |
| EV-POSTFIX-CACHED-LOG | AC3 cached 对照（EXIT=0） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/post-fix-repro-cached-control.log | e35238075 | 14416b1b90ac31d529a94dff23e5d41a38e463928cda076845d74363660569dd | CANONICAL |
| EV-POSTFIX-NOPOLL-LOG | AC3 不轮询对照（EXIT=0） | verification/RUN-STORE-CACHE-RACE-FIX-1/logs/post-fix-repro-nopoll-control.log | e35238075 | 251f5b6d14089dcfb7dc8f080b80f32629154cde2d0ea211b4b8dafb32c2c54a | CANONICAL |
| EV-PREFIX-REPRO | AC3 修复前原始结果（FAIL） | verification/RUN-STORE-CACHE-RACE-FIX-1/repro/pre-fix-projection-fresh.json | e35238075 | baafefb30877d29f11fdde7d77fe25a48191ad4334c69287b231493682f9220d | CANONICAL |
| EV-POSTFIX-REPRO | AC3 修复后原始结果（PASS） | verification/RUN-STORE-CACHE-RACE-FIX-1/repro/post-fix-projection-fresh.json | e35238075 | c6edf38d5d1959c0a88f7b5e679b4dc41b9c26dc110344243bca1b63d3c0fc34 | CANONICAL |
| EV-PREFIX-CACHED | AC3 修复前 cached 对照 | verification/RUN-STORE-CACHE-RACE-FIX-1/repro/pre-fix-cached-control.json | e35238075 | 4534904b7ad3cdbaea2fbd3c086d37f638d71dc446b6573a6ec5faedfdbd9ac2 | CANONICAL |
| EV-POSTFIX-CACHED | AC3 修复后 cached 对照 | verification/RUN-STORE-CACHE-RACE-FIX-1/repro/post-fix-cached-control.json | e35238075 | 6f8c8840ba59d8d4361787bd4a39944dfc54a7ba62e5580866c6a4bc9bcecfe4 | CANONICAL |

pin 口径：sha256 为 **提交内 blob 字节**（与全新 checkout 落盘字节一致）；commit 列指向包含该文件的交付/证据提交（集成 commit 由 DSH 填写）。

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
## Review（DSH 集成复核，2026-10-27）— PASS（前后对照实证）

- AC1：SqlitePipelineStore.refresh() 改为独立视图读、**绝不替换 _cache**（fresh 轮询保留未降级）；InMemoryPipelineStore.refresh() 返回 detached 结构克隆。
- AC2：un_json 写入前 owner/修订 CAS（_write_revision + _check_write_revision，put 与事务内同一守卫），旧快照抛 STALE_RUN_SNAPSHOT；无 Schema/协议/Host 变更。
- AC3 端到端（真实 scheduler 线程 + 100ms projection-fresh + 私有数据根）：修复前 **FAIL**（8/8 StepRun 卡 running、8 个 regionless INVALID_INPUT、8/8 任务 failed，EXIT=1）→ 修复后 **PASS**（0 卡 running、0 regionless、completed 17 / failed 3、5 任务 completed，与 cached/不轮询对照逐项一致，EXIT=0）；pytest 并发用例修复前 FAIL → 后 PASS（3/3）。
- 回归：DSH 复跑 	est.ps1 **177/177**；-k "projection or scheduler or concurrent" **72 passed / 2 skipped**；实现方全量 pytest pre-fix **4F/2752P/9S** → post-fix **4F/2760P/9S**（失败集合相同、+8 新用例、0 新增；第 4 项为既有 flaky plugin_sandbox）。
- AC5：check.ps1 -TaskPath PASS；26 条 64-hex pin（口径=提交 blob）；Handoff + Record Decision。
- 遗留：frozen sidecar 未重打包（→ RELEASE-REPACK-2）；CAS 为单进程/store 实例内存态（前提单 Core 独占 data root）；run_json 仍整份写、无字段级合并。
- 集成：2980608e0。

