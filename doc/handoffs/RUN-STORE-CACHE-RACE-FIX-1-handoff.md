---
task_id: RUN-STORE-CACHE-RACE-FIX-1
author: sandbox-verify
recipient: DeepSeek Harness
base_commit: 97de0fa99
delivery_head: dadcf72b9d0feaf786e660d23ef28a63244060bf
status: in_review
---

# Handoff：RUN-STORE-CACHE-RACE-FIX-1（Core 共享缓存跨线程竞态修复）

## 交付结果

分支 `task/RUN-STORE-CACHE-RACE-FIX-1`，worktree `G:/CODEX/New Manga.workspace/worktrees/RUN-STORE-CACHE-RACE-FIX-1`，基于 HEAD `9ef53f24d`（base `97de0fa99` 为其祖先）。实现提交 `dadcf72b9`；本 Handoff 与证据/卡为后续文档提交。

| AC | 结果 | 交付内容 |
|---|---|---|
| AC1 最小修复 | **MET** | `SqlitePipelineStore.refresh()` 只返回独立视图对象，不再 pop/替换 `_cache[run_id]`；`InMemoryPipelineStore.refresh()` 返回 `_detached_run()` 结构克隆。`fresh=True` 轮询保留，未降级。`src/infrastructure/sqlite/pipeline.py`、`src/application/tasks/store.py` |
| AC2 写入加固 | **MET（含单测）** | 每 Run 修订号 + `_check_write_revision()` CAS；`put`/`write_in_current_transaction` 写前校验，旧快照抛 `STALE_RUN_SNAPSHOT`；无 Schema 变更。测试见 `tests/pipeline/test_run_store_cache_race.py`（4+3 项） |
| AC3 并发回归 | **MET** | `tools/repro_scheduler.py` A/B：修复前 `projection-fresh` FAIL（8 卡 running、8 regionless INVALID_INPUT、8/8 任务 failed，EXIT=1）；修复后 PASS（0/0，17 completed+3 failed，5 任务 completed，EXIT=0）且与 cached/不轮询对照一致。pytest 并发用例 `test_projection_fresh_polling_does_not_corrupt_execution` 修复前 FAIL / 修复后 PASS（3/3 重复） |
| AC4 回归 | **MET** | 同机同时段全量 A/B：pre-fix base **4F/2752P/9S/1 deselected** vs post-fix **4F/2760P/9S**，**失败集合完全相同、0 新增**，通过数 +8 = 本卡新增用例；第 4 项为既有 flaky `test_sandbox_job_kills_grandchildren`（base 同跑同样失败，同树 6 次 pass/fail 交替）。辅助运行 3F/2761P/9S 与历史基线一致。`apps/desktop-avalonia/scripts/test.ps1` → 177/177 passed, 0 skipped |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS（`verification/RUN-STORE-CACHE-RACE-FIX-1/check-taskpath.log`）；64-hex pin 于任务卡；Record Decision（缓存/归属模型）见 `verification/RUN-STORE-CACHE-RACE-FIX-1/REPORT.md` §8 |

完整报告：`verification/RUN-STORE-CACHE-RACE-FIX-1/REPORT.md`。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1/AC2 单测 | `python -m pytest tests/pipeline/test_run_store_cache_race.py -q` | worktree，pre-fix `9ef53f24d`（tests 覆盖）→ post-fix `dadcf72b9` | pre-fix **6F/1P**（EXIT=1）→ post-fix **7P**（EXIT=0） | `logs/pre-fix-pytest-unit.log`、`logs/post-fix-pytest-unit.log` |
| AC3 端到端 A/B | `python verification/RUN-STORE-CACHE-RACE-FIX-1/tools/repro_scheduler.py scheduler projection-fresh --timeout=75` | 同数据根私有副本 + `assemble_production_core` + 真实 scheduler thread | pre-fix **FAIL**（8 stuck/8 regionless/8 任务 failed，EXIT=1）→ post-fix **PASS**（0/0，17 completed+3 failed，EXIT=0） | `repro/pre-fix-projection-fresh.json`、`repro/post-fix-projection-fresh.json`、`logs/*repro*`、`ab-matrix.json` |
| AC3 并发 pytest | `python -m pytest tests/pipeline/test_regionless_rebinding.py -q -k projection_fresh` | worktree pre/post-fix | pre-fix **FAIL**（run `completed_with_failures`）→ post-fix **PASS**（3/3 重复） | `logs/pre-fix-pytest-concurrency.log`、`logs/post-fix-pytest-concurrency.log` |
| AC4 全量 pytest（同机 A/B） | `python -m pytest tests -q`；baseline：`--ignore=tests/pipeline/test_run_store_cache_race.py -k "not projection_fresh_polling_does_not_corrupt_execution"` | pre-fix base `9ef53f24d` vs post-fix `dadcf72b9` | pre-fix **4F/2752P/9S/1 deselected** → post-fix **4F/2760P/9S**（失败集合完全相同、0 新增，+8 新增用例；EXIT=1 为既有失败集合） | `logs/pre-fix-pytest-full-baseline.log`、`logs/post-fix-pytest-full.log`、`logs/post-fix-pytest-full-runA-aux.log` |
| AC4 flaky 说明 | 同一用例重复 6 次 + 沙箱模块整体复跑 | 同树 `dadcf72b9`（base 亦复现） | pass/fail 交替 → 既有 flaky，与 `PipelineStore` 改动无关 | `logs/flaky-plugin-sandbox-reruns.log`、`logs/post-fix-plugin-sandbox-module.log` |
| AC4 Avalonia | `pwsh -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <私有>` | post-fix worktree 构建 | **177/177 passed, 0 skipped**（EXIT=0） | `test/avalonia-summary.json`、`logs/dotnet-test.log` |
| AC5 门禁 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/RUN-STORE-CACHE-RACE-FIX-1.md` | 分支交付 | PASS（含既有 3 warnings） | `check-taskpath.log` |
| 源码 diff | `git diff 9ef53f24d -- src` | — | 2 files, +91/−8 | `src-changes-vs-base.patch` |

未运行项：`vitest`（本卡未改 `apps/desktop/frontend`，协议/线格式不变，沿用基线 60/567）；frozen sidecar 重打包（发布步骤，见遗留）。

## 接收方式

- 仓库：`G:/CODEX/New Manga`（linked worktree `G:/CODEX/New Manga.workspace/worktrees/RUN-STORE-CACHE-RACE-FIX-1`，分支 `task/RUN-STORE-CACHE-RACE-FIX-1`）。
- 复现命令（含环境变量）：
  - `$env:NEWMANGA_EVIDENCE_DIR="G:/CODEX/New Manga.workspace/task-envs/RUN-STORE-CACHE-RACE-FIX-1/evidence"`；
  - `cd <worktree>`；`python verification/RUN-STORE-CACHE-RACE-FIX-1/tools/repro_scheduler.py scheduler projection-fresh --timeout=75`（退出码 0=PASS）。
  - 该脚本自身按 `--file` 位置解析 repo、从 `BOOK-FIXTURE-1/isolated-data` 复制私有数据根、读取 `FINAL-VALIDATION-1` 的 models（只读），不会触碰用户真实数据根。
- 前置条件：Windows + `python`（3.14.6）、SQLite；Avalonia 回归需 `dotnet` 与 HOST-CORECLIENT-1 sidecar-copy。
- DSH 集成检查建议：① 复核两个源文件的 diff 是否为"仅视图读分离 + 写 CAS"；② 按 §8 限制确认"一个 Core 进程独占 data root"仍成立；③ 全量 pytest 失败集合与基线一致；④ 集成后 frozen sidecar 重打包另立/复用发布 Task。

## 下一任务建议（必填）

- Task ID / 标题：`RELEASE-REPACK-1`（已存在；以 DSH 当前 DAG 为准）把本次 Core 修复重新打包进 frozen sidecar 并更新发布证据；若已关闭则"无需下一步操作"。
- 推荐 Agent / Reviewer：打包 Task 按 DSH 分配；Reviewer 不得为 `sandbox-verify`。
- 推荐原因与前置依赖：`core_service.exe`（`2b36bfeb…4ec519b`）仍含旧缺陷；依赖本卡先完成集成（Core 源码进入 main）。
- Recovery point：仓库 `G:/CODEX/New Manga`；main 集成本卡后的固定 commit（由 DSH 填写）；worktree 待 DSH 创建（若需）。
- 允许修改路径：以该发布 Task 卡为准（`packaging/**`、`VERSION.json`、发布证据目录）。
- 禁止范围与新增授权条件：不改 Core 语义/协议；不 push；PyInstaller 不可原地补丁，必须全量重打包。
- 交付物：新 frozen sidecar + sha256 变更记录 + 同请求复验（本卡 `repro_scheduler.py` 可直接沿用）。
- 验证命令、环境与完成 Gate：见该 Task 卡 AC；至少包含 fresh 轮询场景 0 卡 running / 0 regionless INVALID_INPUT。
- 可直接转发给 Agent 的指令：`按 RELEASE-REPACK-1 卡重打包 frozen sidecar，纳入 RUN-STORE-CACHE-RACE-FIX-1（dadcf72b9）的 Core 修复，并用 verification/RUN-STORE-CACHE-RACE-FIX-1/tools/repro_scheduler.py 复验 projection-fresh 场景。`

## 风险与遗留

1. **frozen sidecar 未重打包**：发布包仍含旧竞态（latent；GUI 当前无投影轮询调用点，故未触发）。
2. 修订 CAS 为**每 store 实例内存态**，前提是单 Core 进程独占 data root（现行产品/协议约束）；跨进程多实例并发写不在本卡范围（见 REPORT §8 限制）。
3. `run_json` 仍整份写；本卡只防旧快照覆盖，不做字段级合并。
4. `fresh=False` 仍读执行缓存对象（协议既定、只读、不写回），并发下可能见执行中内存中间态，属既有行为。
5. 回退：`git revert dadcf72b9` 即回旧行为，无 Schema/数据迁移风险（缺陷会随 fresh 轮询复现）。

DONE 前由 DSH 按任务卡 Canonical Evidence 与 `resource-manifest.json` 收口；本 Handoff 不授予集成、删除或关闭权限。
