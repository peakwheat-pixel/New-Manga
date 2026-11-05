---
task_id: FEA-11-AC4-GAPS-1
author: scanner-gaps-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 51e139eff
delivery_head: 95815ff7a
status: in_review
---

# Handoff — FEA-11-AC4-GAPS-1（AC11-4 证据收口，test-only）

- Task：`doc/tasks/FEA-11-AC4-GAPS-1.md`（status: `in_review`；Owner=`scanner-gaps-impl`；Lead=`lead`）
- 交付日期：2026-11-05（Asia/Shanghai）
- 交付基线：`base_commit 51e139eff`（main head `d8049fe6e`）；**未 push**
- 交付实现 commit：`95815ff7a`（**test-only**：`tests/fea11/test_source_sync.py` +18 用例；新增 `tests/fea11/test_source_sync_storage.py` +1 用例）
- 证据/卡面/本 Handoff：`verification/FEA-11-AC4-GAPS-1/**` + `doc/tasks/FEA-11-AC4-GAPS-1.md` + 本文件（同批文档提交；`delivery_head` 仅指向实现提交）
- 环境：Windows / PowerShell 7.6.8 / Python 3.14.6 / pytest 9.1.1；无新依赖、无 schema/migration 改动
- 范围依据：`doc/reviews/SCOPE-ADJ-2026-11-05-zcode.md` C 节；卡内冻结口径 1–5

## 1. 交付结果（逐项对照 AC）

| AC | 结果 | 交付内容 |
|---|---|---|
| AC1 并发 apply | **MET** | AC1-a same-op replay（生产 `ThreadRoutedConnection` facade + 隔离文件 DB，两线程同一 service 实例，两份原 receipt，恰好一次提交）；AC1-b different-op typed（1 成功 + 失败方 typed ∈ {`SOURCE_OPERATION_CONFLICT`,`SOURCE_PLAN_STALE`}，非 `sqlite3.Error`）；AC1-c 双独立 stack/两连接同文件 DB（等价 grant 基线、恰好一次提交、无 `database is locked`、零写复探）；AC1-d 按卡 Out 不写断言 |
| AC2 DB 失败注入 | **MET** | AC2-a `BEFORE INSERT ON page_bindings` `RAISE(ABORT)`（事务中途，p1 已发布后回滚）；AC2-b `BEFORE UPDATE ON source_operations`（最后一步 `commit_operation`）；两者 16 表快照与失败前逐行相等、plan 仍 confirmed、重试成功。AC2-c 经**生产装配 + host-control dispatch** 得到 `SOURCE_SYNC_STORAGE_FAILED`（`internal`/`retryable=true`，不回显注入文本，零业务写）；同 trigger 下直接 service 调用抛原始 `sqlite3.IntegrityError`，证明失败点在 `BEGIN IMMEDIATE` 与 `COMMIT` 之间（**不是** post-commit `_bind_operation_grant`，L3） |
| AC3 第三区域双分支 | **MET** | AC3-a plan 自带过期 migrate revision（`[r1,r2,r3old]`）→ `STALE_BASE_REVISION`，前两项迁移 + binding + lineage 全部回滚（16 表相等、regions=3/region_revisions=4/lineage=0）；AC3-b 现实漂移（rg3 current → `r3new`）→ `SOURCE_PLAN_STALE(cause=manual)`，断言**不是** `STALE_BASE_REVISION`（不宣称走到迁移分支） |
| AC4 漂移矩阵 + 全表零写 | **MET** | G4（`FILE_IDENTITY_CHANGED`）、G4b（`stale(source)`）、G5（`stale(binding)`）、G6（`stale(decision)`）、G7（`stale(authorization)`）、G8（`SOURCE_GRANT_REVOKED`）、G9 manual/protection/draft/Run（`stale(manual)`，漂移打在**最后一个** base 上）、G10 多项目末项（`stale(binding)`，两项目零写）、G11 统一 `_full_snapshot` **16 表**比较集 |
| AC5 证据/范围/门禁 | **PARTIAL** | 门禁与 0 域外 diff 已交付（见 §2）；**独立上下文 Review 与至少一次负向/变异探针尚未执行**，按卡只能 NOT_RUN。`.NET` = **NOT_RUN**（0 C# 文件变更、纯 Python 测试；不得写 PASS） |

AC11-4 是否 MET 由 Lead/Review 判定；本卡未自行宣告。

## 2. 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1–AC4 新增用例 | `python -m pytest tests/fea11/test_source_sync.py tests/fea11/test_source_sync_storage.py -q -p no:cacheprovider` | Python 3.14.6；`95815ff7a` | **PASS**（28 passed；含 5 次重复稳定运行） | `verification/FEA-11-AC4-GAPS-1/logs/fea11-gaps1-tests.log` |
| 相关组 | `python -m pytest tests/fea11 -q -p no:cacheprovider` | 同上 | **PASS**（88 passed；基线 69） | `logs/fea11-tests.log` |
| 全量 | `python -m pytest tests -q -p no:warnings --tb=no` | 同上 | **PASS**（**3183 passed, 10 skipped**；释放日基线 3164/10，+19，skip 不增） | `logs/full-pytest.log`、`logs/baseline-full-pytest.log` |
| 治理门禁 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-AC4-GAPS-1.md`；`... check.ps1`；`... verify_pins.ps1` | 仓库根 | **PASS**；**PASS**；**PASS (18/18)** | `logs/gates.log` |
| 范围 | `git diff --name-only 51e139eff..HEAD -- src/ doc/plan doc/contracts apps` | 同上 | **空（0 域外 diff）** | `logs/scope-diff.log` |
| 负向/变异探针（实现者自检，**非权威**） | `python "G:/CODEX/New Manga.workspace/FEA-11-AC4-GAPS-1/probes/mutation_probe.py"` | 同上；运行时 monkeypatch，不改 `src/**` | 3 项变异 RED（replay 移除 / 逐项 commit / manual+protection CAS 移除）；2 项被更强 CAS 遮蔽（如实登记） | `logs/mutation-probes.log` |
| `.NET` | 未运行 | — | **NOT_RUN**（0 C# diff；禁止写 PASS） | `logs/dotnet-not-run.md` |

未运行项与原因：`.NET` 全量（0 C# 文件变更，纯 Python 测试；本卡不补跑，除非 Lead 另行要求）；真实 IPC/HostRuntime 端到端、逐崩溃点杀进程矩阵、ACK/recovery 自动化属卡内 Out。
实现者自检探针不替代 Review 探针：**Review 必须自行实际运行新增测试并至少做一次负向/变异探针**，否则 AC5 只算 NOT_RUN。

## 3. 接收方式

- 仓库/分支：`G:\CODEX\New Manga`，`main`；base `51e139eff`，实现 head `95815ff7a`（未 push、未建 worktree）。
- 复现：
  1. `python -m pytest tests/fea11 -q -p no:cacheprovider`（期望 88 passed）
  2. `python -m pytest tests -q -p no:warnings --tb=no`（期望 3183 passed / 10 skipped）
  3. `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-AC4-GAPS-1.md`
  4. `pwsh -NoProfile -File tools/governance/verify_pins.ps1`（18/18）
  5. `git diff --name-only 51e139eff..HEAD -- src/ doc/plan doc/contracts apps`（须为空）
- 前置条件：Python 3.14 + 仓库现有依赖（Pillow/pytest 等）；测试使用 `G:/CODEX/New Manga.workspace/FEA-11/fixtures/`（既有 conftest 隔离根）与 pytest `tmp_path`，不触碰真实用户数据/AppData。
- 已批准依赖变化：**无**。
- 接收者下一步具体检查：① 逐条核对 `AC-MATRIX.md` 与测试名；② 独立上下文运行命令并记录 session ID/来源；③ 至少一次负向探针（移除一个 CAS/回滚分支证明用例变红）；④ 判定 AC11-4 是否 MET 并处置 findings。

## 4. 下一任务建议

- Task ID / 标题：**无（本卡尚未 Review/集成，不释放后续实现卡）**；若 Lead 决定，按 ZCode 释放顺序建议进入 `FEA-11-MATCH-1`（需 Lead 另行释放与 Appointment，不在本 Handoff 授权范围）。
- 推荐 Agent / Reviewer：Reviewer 由 DSH 指派**独立上下文**（非本会话/非实现者；fresh subagent 或未参与实现的 ZCode/Codex）。
- 推荐原因与前置依赖：`FEA-11-MATCH-1` 依赖本卡完成 AC11-4 证据收口；本卡当前仅到 in_review。
- Recovery point：`G:\CODEX\New Manga`，`main`；base `51e139eff`，实现 head `95815ff7a`（未 push）；未创建 worktree（**待 DSH 决定是否需要**）。
- 允许修改路径：本卡 `allowed_paths` 不变（`tests/fea11/test_source_sync.py`、`tests/fea11/test_source_sync_storage.py`、`doc/tasks/FEA-11-AC4-GAPS-1.md`、`doc/reviews/FEA-11-AC4-GAPS-1-*.md`、`doc/handoffs/FEA-11-AC4-GAPS-1-*.md`、`verification/FEA-11-AC4-GAPS-1/**`）。
- 禁止范围与新增授权条件：不得改 `src/**`、契约字节、v8 DDL、错误闭集、`tests/fea11/conftest.py`、`tests/core/**`、`doc/plan`、`doc/contracts`、STATUS/PLAN/LEDGER/reviews；不新增依赖/schema；不 push；不写拒绝审计 receipt。
- 交付物：独立 Review 报告（`doc/reviews/FEA-11-AC4-GAPS-1-*.md`，含运行证据与负向探针结果、Reviewer session ID/来源）。
- 验证命令、环境与完成 Gate：同 §3；Gate = Review approved（P0/P1=0）+ DSH 集成验证 + 0 域外 diff + pins 18/18。
- 可直接转发给 Agent 的指令（给 DSH 选用）：见 §6。

## 5. 风险与遗留

- **L1**：生产 Core 请求循环单线程；AC1-c 双连接是 service seam 防御证据，不是端到端 IPC 并发。
- **L2**：`STALE_BASE_REVISION` 只在非 conforming plan 下可达（AC3-a 防御 seam）；现实漂移由 AC3-b 的 manual/protection CAS 拦截。
- **L3**：`_bind_operation_grant`（commit 之后）失败不在事务回滚证据内；AC2-c 注入点严格在事务内并显式证明。
- **L4**：DB 失败用 SQLite trigger 模拟，不等于真实磁盘满/IO 错误；commit-time IO 失败未模拟。
- G12（拒绝审计）按 C-17 §6.2 明文禁止，**非缺口**。
- 已知观察（非缺陷，供 Review 知悉）：AC1-b 的两个「UNIQUE 冲突」类变异会被 plan-state/reference-set CAS 提前遮蔽（见 `logs/mutation-probes.log`），因此该用例的 `not isinstance(..., sqlite3.Error)` 是**前向防御**断言；真正的判别断言是「恰一次提交 + 失败方 typed 闭集 + 16 表零写」。
- 并发装置说明：AC1-a/AC1-b 使用生产 `ThreadRoutedConnection`（每线程独立真实连接）而不是 `:memory:` 单连接——后者跨线程共享同一事务状态（`connection.py` TASK-060 Q-001），会让读/提交互相破坏，不能作为并发证据装置。

## 6. 可直接转发给 Agent 的指令（Review）

```text
你是 FEA-11-AC4-GAPS-1 的独立上下文 Reviewer（未参与实现；不得修改实现）。
仓库：G:\CODEX\New Manga（main；base 51e139eff；实现 head 95815ff7a；未 push）。
任务卡：doc/tasks/FEA-11-AC4-GAPS-1.md（status in_review；AC1–AC4 MET、AC5 PARTIAL）。
必读：卡内 AC1–AC5 与冻结口径 1–5；verification/FEA-11-AC4-GAPS-1/AC-MATRIX.md、EV.md；C-17 §6.1/§6.2/§8（doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md）。
必做：
1. 实际运行：python -m pytest tests/fea11 -q -p no:cacheprovider（期望 88 passed）；
   python -m pytest tests -q -p no:warnings --tb=no（期望 3183 passed/10 skipped）；
   pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-AC4-GAPS-1.md；
   pwsh -NoProfile -File tools/governance/verify_pins.ps1（18/18）；
   git diff --name-only 51e139eff..HEAD -- src/ doc/plan doc/contracts apps（须为空）。
2. 至少一次负向/变异探针：在仓外副本或临时 worktree 移除一个 CAS/回滚分支（例如
   service.py:402-416 的 manual digest 校验，或 _migrate_revisions 的逐项提交），证明对应用例变红；
   记录探针命令与结果（本条缺失则 Review 结论只能写 NOT_RUN）。
3. 核对：AC1 语义是「恰好一次业务提交」（same-op 第二响应可以是原 receipt）；AC2-c 必须是
   wire 级 SOURCE_SYNC_STORAGE_FAILED 且注入点在 BEGIN IMMEDIATE 与 COMMIT 之间（不得用
   post-commit _bind_operation_grant 冒充回滚）；AC3-a/b 分属防御 seam 与现实漂移；
   G4–G11 逐项错误码/cause 与 16 表零写；.NET 必须 NOT_RUN（不得写 PASS）。
4. 输出 doc/reviews/FEA-11-AC4-GAPS-1-r1.md（模板 doc/templates/REVIEW.md），记录 Reviewer 身份/来源
   （session ID）与是否参与实现；给出 P0/P1/P2 findings 与 AC11-4 是否 MET 的建议判定。
禁止：修改 src/**、契约、schema、conftest.py；push；写拒绝审计 receipt。只读实现，不返修。
```
