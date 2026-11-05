# FEA-11-AC4-GAPS-1 · Evidence（EV）

- Task：`doc/tasks/FEA-11-AC4-GAPS-1.md`（test-only 验收缺口证据收口）
- Owner：`scanner-gaps-impl`（DSH Agent Teams 成员）；Lead：`lead`
- 基线：`base_commit 51e139eff`；main head `d8049fe6e`
- 交付实现 commit：`95815ff7a`（仅 `tests/fea11/test_source_sync.py`、`tests/fea11/test_source_sync_storage.py`）
- 证据/卡面 commit：本目录与卡面更新的提交（见 `DELIVERY-MANIFEST.json`）
- 环境：Windows / PowerShell 7.6.8 / Python 3.14.6 / pytest 9.1.1；无新依赖

## 1. 命令与结果

| # | 命令 | EXIT | 结果 | 日志 |
|---|---|---|---|---|
| 1 | `python -m pytest tests/fea11 -q -p no:cacheprovider` | 0 | 88 passed（基线 69；+19） | `logs/fea11-tests.log` |
| 2 | `python -m pytest tests/fea11/test_source_sync.py tests/fea11/test_source_sync_storage.py -q -p no:cacheprovider` | 0 | 28 passed | `logs/fea11-gaps1-tests.log` |
| 3 | `python -m pytest tests/fea11/test_source_sync.py tests/fea11/test_source_sync_storage.py -q -p no:cacheprovider` ×5 | 0 | 28 passed ×5（并发用例稳定性） | 本 EV §3 |
| 4 | `python -m pytest tests -q -p no:warnings --tb=no` | 0 | **3183 passed, 10 skipped**（释放日基线 3164/10） | `logs/full-pytest.log` |
| 5 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-AC4-GAPS-1.md` | 0 | Governance check: PASS | `logs/gates.log` |
| 6 | `pwsh -NoProfile -File tools/governance/check.ps1` | 0 | Governance check: PASS | `logs/gates.log` |
| 7 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 0 | PIN AUDIT: PASS (all 18) | `logs/gates.log` |
| 8 | `git diff --name-only 51e139eff..HEAD -- src/ doc/plan doc/contracts apps` | 0 | 空（0 产品/契约 diff） | `logs/scope-diff.log` |
| 9 | 负向/变异探针（实现者自检，非权威） | 0 | 3 项变异验证为 RED，2 项被更强 CAS 遮蔽（如实记录） | `logs/mutation-probes.log` |
| 10 | `.NET` 全量 | NOT_RUN | 0 C# 文件变更、纯 Python 测试；**不得写 PASS** | `logs/dotnet-not-run.md` |

## 2. 基线（释放日实跑，本卡修改前）

- `pytest tests -q -p no:warnings --tb=no` → **3164 passed, 10 skipped in 238.08s**
- `pytest tests/fea11 -q -p no:cacheprovider` → 69 passed
- `check.ps1 -TaskPath doc/tasks/FEA-11-AC4-GAPS-1.md` → PASS（3 warnings：14 个非终态 Task / STATUS 预算 80% / REBASELINE_PLAN 预算 80%）
- `verify_pins.ps1` → PIN AUDIT: PASS (all 18)
- 基线日志：`logs/baseline-full-pytest.log`（改前全量）

## 3. 并发稳定性

`tests/fea11/test_source_sync.py::test_concurrent_*` 与 `...::test_two_connection_stacks_*` 连续 5 次独立进程运行均通过（每次 28 passed），另有 15 次仅并发三例的循环运行通过（`logs/fea11-gaps1-tests.log` 记录其中一次；开发过程中曾用 10/15 次循环确认无 `database is locked` 与无 flake）。
断言的是**不变量**（恰好一次业务提交、失败方 typed、16 表零写），不依赖「谁赢」，不使用 sleep。

## 4. 判别力（负向/变异探针，实现者自检 · 非权威）

脚本：`G:/CODEX/New Manga.workspace/FEA-11-AC4-GAPS-1/probes/mutation_probe.py`
（运行时 monkeypatch，不改 `src/**`；证据：`logs/mutation-probes.log`）

| 探针 | 变异 | 观察 | 结论 |
|---|---|---|---|
| `probe_replay_removed` | 去掉 same-op replay | 第二个 apply 得到 `SOURCE_PLAN_STALE` | AC1-a 的「两份 accepted=true receipt」断言会 RED ✓ |
| `probe_per_item_commit` | 每个 migrate revision 单独 commit | 失败后 regions=5、region_revisions=6（本应 3/4） | AC3-a 的 16 表快照/行数断言会 RED ✓ |
| `probe_manual_cas_removed` | 同时去掉 `manual_digest`/`protection_digest` | 错误码变为 `STALE_BASE_REVISION` | AC3-b/G9 的 `SOURCE_PLAN_STALE(cause=manual)` 断言会 RED ✓ |
| `probe_conflict_precheck_bypass` | 仅去掉 `existing_plan_op` 预检 | 仍 `SOURCE_PLAN_STALE` | 被事务内 plan-state CAS 遮蔽（如实登记） |
| `probe_double_guard_removed` | 再去掉 plan-state 拒绝 | 仍 `SOURCE_PLAN_STALE` | 被引用集合 CAS 遮蔽（如实登记）；AC1-b 的 `not isinstance(..., sqlite3.Error)` 是前向防御断言 |

> 卡 AC5 要求：**独立上下文 Review 必须自行实际运行新增测试并至少做一次负向/变异探针**，否则只算 NOT_RUN。上面的自检不替代 Review 探针。

## 5. Canonical Evidence 存放

- 测试实现：`tests/fea11/test_source_sync.py`、`tests/fea11/test_source_sync_storage.py`（commit `95815ff7a`）
- 证据：本目录（`AC-MATRIX.md`、`EV.md`、`RESOURCE-MANIFEST.json`、`DELIVERY-MANIFEST.json`、`changed-files.txt`、`logs/**`）
- 隔离根（仓外）：`G:/CODEX/New Manga.workspace/FEA-11-AC4-GAPS-1/`（`probes/`、`logs/`）——按 Appointment/工作区治理，不写入仓内
- 未触碰：`FEA-11`、`FEA-11-LINEAGE-1`、`FEA-11-HOST-AUTH-1` 的 tracked 证据/pin；`doc/plan`、`doc/contracts`、`STATUS`、`REBASELINE_PLAN`、`TASK_LEDGER`、`doc/reviews`（DSH 专属）

## 6. 残余 limitation（沿用卡内 L1–L4）

- **L1**：生产 Core 请求循环单线程；AC1-c 双连接测试是 service seam 防御性证据，不是端到端 IPC 并发。
- **L2**：`STALE_BASE_REVISION` 只在非 conforming plan 下可达（AC3-a 防御 seam）；现实漂移由 AC3-b 的 manual/protection CAS 拦截。
- **L3**：`_bind_operation_grant`（commit 之后）失败不在事务回滚证据内；AC2-c 的注入点在事务内，并显式避免 post-commit 冒充。
- **L4**：DB 失败用 SQLite trigger（`RAISE(ABORT)`）模拟，不等于真实磁盘满/IO 错误；commit-time IO 失败未模拟。
- G12（拒绝审计）按 C-17 §6.2 明文禁止，**非缺口**，不登记 limitation。
