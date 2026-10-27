---
id: SCHEDULER-THREAD-DIAG-1
title: 调度线程 detect 卡 running 诊断（只诊断）
kind: research
governance_version: 3
status: done
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: baseline-scout
owner: baseline-scout
reviewer: dsh
depends_on: []
base_commit: 97de0fa99
branch: task/SCHEDULER-THREAD-DIAG-1
worktree: G:/CODEX/New Manga.workspace/worktrees/SCHEDULER-THREAD-DIAG-1
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/SCHEDULER-THREAD-DIAG-1
allowed_paths:
  - doc/tasks/SCHEDULER-THREAD-DIAG-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/SCHEDULER-THREAD-DIAG-1/**
  - G:/CODEX/New Manga.workspace/task-envs/SCHEDULER-THREAD-DIAG-1/**
  - G:/CODEX/New Manga.workspace/worktrees/SCHEDULER-THREAD-DIAG-1/**
---

# SCHEDULER-THREAD-DIAG-1：调度线程内 detect StepRun 卡 running 诊断（只诊断）

## 背景

CORE-PIPELINE-FIX-1 报告可复现异常：经 `python -m bootstrap.core_service` **调度线程**执行同一 Run 时，detect StepRun 卡 `running`、下游 regionless ocr 报 `INVALID_INPUT`；进程内直接 `execute_run` 正常。疑 `ThreadRoutedConnection`/`write_in_current_transaction` 事务路径。

## Acceptance Criteria

- [x] **AC1 最小复现**：按报告路径稳定复现（`core_service` 同拓扑：装配 + `CoreServiceServer` + 真实 `core-run-scheduler` 线程），给出线程 / 连接路由 / 事务状态信息；触发条件唯一收敛为 `GetTaskProjection(fresh=True)` 轮询。 <<MET>>
- [x] **AC2 根因**：判定为 **共享可变缓存的跨线程对象替换**（`SqlitePipelineStore._cache` + `refresh()`），非事务可见性/连接路由/调度线程未 commit；给出因果链、对象身份、DB 快照与 A/B 对照。 <<MET>>
- [x] **AC3 影响面**：已发布 frozen sidecar（`2b36bfeb…4ec519b`）实测同样复现（projection 轮询触发、snapshot 轮询不触发）→ 缺陷存在于 shipped binary；当前 Avalonia GUI 仅接线 `library_get_task_projection`、尚无轮询调用点，判定为 latent 缺陷，投影轮询落地前必须修复。 <<MET>>
- [x] **AC4 建议**：最小修复=视图读取不再改写执行缓存（`refresh()` 返回独立读取、不替换 `_cache`），加固=整 run JSON 写加 owner/CAS；建议新 Task `RUN-STORE-CACHE-RACE-FIX-1`（不改 Core 语义）。 <<MET>>
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff/证据入库；`src/**` 零改动。 <<MET>>

## 允许修改范围

`verification/SCHEDULER-THREAD-DIAG-1/**`、本卡、STATUS/PLAN/LEDGER、workspace。**只读**产品源码/Core。

## 禁止范围

不改 Python Core 语义/产品源码/协议/旧壳、不 push、不 gc/prune；不伪造复现。

## 诊断结论摘要

`SqlitePipelineStore` 把 `PipelineRun` 缓存在跨线程共享的普通 dict（`_cache`）里；`GetTaskProjection` → `get_task_projection(fresh=True)` → `store.refresh()` 读取 DB 后执行 `self._cache[run_id] = run`，把执行线程正在使用的对象替换成克隆。于是：

1. `commit_step_result → _find_step → store.get()` 拿到克隆，detect 的 commit 与 `_backfill_detected_regions` 只作用于克隆；
2. 执行线程 `execute_run` 的局部 `run` 未回填 → 下一个 unit 仍是 regionless `ocr` → `INVALID_INPUT: step 'ocr' requires a Region target`；
3. 旧对象随后 `_persist` 把提交前状态整体写回 `run_json`（last-writer-wins）→ 已提交 `completed` 回退为 `running`（"卡 running"观感）。

连接路由正确（同 facade、每线程独立 sqlite 连接，调度线程事务 `applied`）；问题在缓存对象而非事务。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EV-REPORT | AC1–AC5 | verification/SCHEDULER-THREAD-DIAG-1/REPORT.md | | 9de6fe6be96653277a0317585c2d7709c08285146738aaee3bf18d04fecdf393 | CANONICAL |
| EV-DIAGNOSIS | AC1–AC4 | verification/SCHEDULER-THREAD-DIAG-1/diagnosis.json | | c34de96baa886414549c5cc709a59add8655308bff47a47a8305534ba37e55cc | CANONICAL |
| EV-SOURCE-FRESH | AC1/AC2 | verification/SCHEDULER-THREAD-DIAG-1/source-projection-fresh.json | | 1a1cca22050d72a0d8689edf5847e598d68921b25e94da0581df2d64a2915103 | CANONICAL |
| EV-SOURCE-CACHED | AC1/AC2 | verification/SCHEDULER-THREAD-DIAG-1/source-projection-cached.json | | 0858e97642f660b290e128b1be8a6d50d7955610ab82b2d27b0d63b3a2abd1f9 | CANONICAL |
| EV-SOURCE-NOPOLL | AC1/AC2 | verification/SCHEDULER-THREAD-DIAG-1/source-no-poll.json | | 76c65709fe6ec38735446398467bb93def53b21f69b2681fd24b1ba3346faf1b | CANONICAL |
| EV-FROZEN-PROJECTION | AC3 | verification/SCHEDULER-THREAD-DIAG-1/frozen-projection-polling.json | | b0ca7f23fc2dca4a66e5b86291ee17fa9ac958edf76154c82e91c029c5548144 | CANONICAL |
| EV-FROZEN-SNAPSHOT | AC3 | verification/SCHEDULER-THREAD-DIAG-1/frozen-snapshot-only.json | | 5bf5514800a354297e326d2b61f27e68ce3dfa0afeeac852713616344cde2ecb | CANONICAL |
| EV-FROZEN-LOG-P | AC3 | verification/SCHEDULER-THREAD-DIAG-1/logs/frozen-projection-polling.log | | 061641afc5011d37ffed5a59a67b45a36ecb27a93da046484f5b4e1ee0117c86 | CANONICAL |
| EV-FROZEN-LOG-S | AC3 | verification/SCHEDULER-THREAD-DIAG-1/logs/frozen-snapshot-only.log | | 5dac321d14e142f9386360219a5981b5bcc86ed898c872bc6a2858598045c206 | CANONICAL |
| EV-TOOL-REPRO | AC1/AC2 | verification/SCHEDULER-THREAD-DIAG-1/tools/repro_scheduler.py | | 46ce6be3eba52244970c6b4ad5b0b28d66d4b88ce8cc16bf795db0a46610b159 | SOURCE_PIN |
| EV-TOOL-FROZEN | AC3 | verification/SCHEDULER-THREAD-DIAG-1/tools/probe_frozen.py | | 38408b392f9a1173e78e897cfe744dd6ce156b896642eb6977d2bcbd955c3e81 | SOURCE_PIN |
| EV-TOOL-DIAGNOSIS | AC4 | verification/SCHEDULER-THREAD-DIAG-1/tools/build_diagnosis.py | | 186192ff1d9a8236004c252eab101f3f197d37b09a0d709a27afbb01c9d4d215 | SOURCE_PIN |
| EV-RESOURCE-MANIFEST | AC5 | verification/SCHEDULER-THREAD-DIAG-1/resource-manifest.json | | 62ef2e6710ff7b0e79a8adc7bbd42c56a87043392dd83a5bf530793a6f619162 | SOURCE_PIN |
| EV-CHECK-TASKPATH | AC5 | verification/SCHEDULER-THREAD-DIAG-1/check-taskpath.log | | 9116d93dd8248cf86ba92089ac477aa6aa1607bd82cda0e475d850a6fc5a1854 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/SCHEDULER-THREAD-DIAG-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/SCHEDULER-THREAD-DIAG-1 | verification/SCHEDULER-THREAD-DIAG-1/resource-manifest.json | task-env 仅本次数据根/日志/脚本（已 pin 13 项 artifact）；`src/**` 零改动；无删除/迁移/归档；frozen 包与 BOOK-FIXTURE 原件零修改 |

## 交付与运行记录

- Owner：`baseline-scout`（DSH 委派，team task-38）；只诊断，**未改任何产品源码**（诊断探针仅在 task-env，运行时 monkeypatch 采集仪表）。
- 复现稳定性：source 模式 `projection-fresh` 3/3 次复现（detect 卡 running + regionless ocr INVALID_INPUT）；`projection-cached` / `no-poll` 对照 2/2 干净。frozen sidecar：projection 轮询复现、snapshot 轮询干净。
- 关键文件：`tool repro_scheduler.py`（source 同拓扑复现）、`tools/probe_frozen.py`（已发布 sidecar 复测）、`tools/build_diagnosis.py`（A/B 汇总）。
- 建议下一步：新释放 `RUN-STORE-CACHE-RACE-FIX-1`（Core-only 小改 + 并发回归测试）；在修复前，`RELEASE-REPACK-1` 重打包不得视为已消除该缺陷。

## Closeout Record

- Closeout date / DSH：待关闭时填写；Owner 交付日期 2026-10-27。
- canonical_evidence_status：`complete`（13 行 sha256 pin，commit 列留空）。
- resource_closeout_status：`pending`（task-env 保留引用；关闭时复核 `resource-manifest.json`）。
- 删除、迁移、归档数量/字节数：本 Task 无删除/迁移/归档。
- 未关闭项及保留原因：修复实施属新 Task（建议 `RUN-STORE-CACHE-RACE-FIX-1`），本卡不实施。
- 当前指针清理：关闭时由 DSH 更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS（根因明确，latent 生产缺陷）

- 复现稳定性：source 同拓扑 GetTaskProjection(fresh=True) 每 100ms 轮询 → **3/3 复现**；resh=False/不轮询 → 2/2 干净；**frozen sidecar 2b36bfeb… 实测同样复现**（shipped binary 含竞态）。
- 根因：SqlitePipelineStore._cache 跨线程共享可变 dict；efresh() 读 DB 后替换 _cache[run_id] 为克隆 → 执行线程提交只落克隆、xecute_run 局部对象未回填（regionless ocr → INVALID_INPUT）、旧对象随后整份回写导致 StepRun 回退 running（last-writer-wins）。代码点 core_service.py:3236 → service.py:1394/1531/1454 → sqlite/pipeline.py:415。
- 影响面：GUI 当前无 viewmodel 轮询调用点（不触发），但 Host 集成测试/诊断工具会触发 → **latent 生产缺陷，重打包不能视为已修**。
- 建议已立项：RUN-STORE-CACHE-RACE-FIX-1（视图读与执行缓存分离 + owner/CAS 加固 + 并发回归）。
- 集成：ae7fe3334。


