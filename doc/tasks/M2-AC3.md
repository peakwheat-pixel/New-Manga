---
id: M2-AC3
title: Provider Fail-closed Acceptance (unconfigured / network failure / partial failure)
kind: acceptance
status: in_progress
release_state: M2_AC3_PROVIDER_FAIL_CLOSED_RELEASED
approval: approved_by_user_2026-09-28_m2ac3_release
execution_approval: approved_by_user_2026-09-28_m2ac3_release
claimed_by: ZCode
claimed_at: 2026-09-28
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
integrator: Codex（新会话以 Codex 身份执行，保持 Owner≠Integrator）
depends_on: [M2-AC2]
base_commit: 319c5e4b94fab4e43c8ec8c797c6545915ed7efa
branch: agent/zcode/M2-AC3-provider-fail-closed
worktree: G:/CODEX/New Manga.worktrees/M2-AC3-zcode
delivery_head: null
review: null
integration_merge: null
dispatch_state: CLAIMED_BY_OWNER_ZCODE_2026-09-28
---

# M2-AC3 — Provider Fail-closed Acceptance

## 来源与目标

来源：[Rebaseline Plan](../REBASELINE_PLAN.md) M2 Acceptance Backlog 第 3 行（用户批准释放 2026-09-28）。对应 [AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md) 的产品承诺：**Provider 未配置、网络失败、部分失败时，命令计划与页面状态必须 fail-closed**——不产出半成品成果、typed 错误可诊断、可恢复、源文件零风险。

验收形态与 M2-AC2 相同：纯 Python Core 层验收模块（`tests/m2_acceptance/` 新增），复用 M2-AC1/M2-AC2 的真实装配手法（production assembly、临时 data root、真实 SQLite、真实文件系统），**不扩 IPC 命令面、不走 test-mode bridge**。矩阵化验收：每个承诺一个场景族，先证明语义存在，再证明破坏被拒绝/检出。

代码事实锚点（起草时核对，Owner 实现时如发现措辞与实际语义不符，按 M2-AC2 先例在 Handoff 中澄清并经 Review 确认后修订 AC）：typed 契约错误 = `PipelineError(code, detail)`（`src/domain/tasks/models.py:150`，稳定 TASK-002 error code）；provider 缺配置 = `ProviderNotConfigured` / `ProviderUnavailable`（`src/infrastructure/providers/registry.py:246-253`）；taxonomy slot = `PROVIDER_NOT_CONFIGURED`（`src/infrastructure/providers/handlers.py:234`）；run 终态 = `RunStatus.COMPLETED_WITH_FAILURES`（`src/domain/tasks/models.py:96`）；provider 未配置时剩余 units 的处理语义见 `src/application/tasks/service.py:351` 附近。

Owner=ZCode；非作者 Reviewer=DeepSeek Harness；Integrator=Codex（**新会话以 Codex 身份执行**，保持 Owner≠Integrator）。

## Acceptance Criteria

- [ ] **AC1 — Provider 未配置 fail-closed：** 空 registry / provider 未就绪时，pipeline 执行不产出任何半成品成果（无 revision、无 artifact 文件、无 StepResult 半成品落库）；失败以 typed 错误呈现（`PROVIDER_NOT_CONFIGURED` taxonomy 或 `ProviderNotConfigured`/`PipelineError`），错误信息可诊断（能区分"未配置"与其他失败）；页/run 状态如实，不得伪造成成功。
- [ ] **AC2 — 网络失败 fail-closed 与既有成果保护：** provider 运行中失败（transport/请求错误）时，失败以 typed 错误呈现且可诊断；**既有成果零损坏**——失败前已存在的人工修改、revision、pinned 标记、current 指针全部保持（复用 M2-AC2 断言口径）；无半成品 revision/artifact 留库。
- [ ] **AC3 — 部分失败边界如实：** 多页/多 region 的 run 中部分成功部分失败时，run 终态如实（如 `COMPLETED_WITH_FAILURES`），成功页与失败页边界可查询、失败页无伪造成果；成功页成果完整可用；失败原因按页可诊断。
- [ ] **AC4 — 源文件零风险：** 上述全部失败场景中，用户源文件字节与 mtime 全程不变（Core 对源目录零写入），managed copy 无部分写入（字节与源一致）。
- [ ] **AC5 — 可恢复：** 失败后同一 data root 重新装配（进程重启等价），状态一致可查询；失败 run 可被重试/恢复路径触达（如 `recover_running_runs` 语义、剩余 units 可重试），重试成功后不留重复或悬空成果。
- [ ] **AC6 — 证据纪律：** 所有命令记录 shell、解释器、固定 HEAD、EXIT；`FAIL`/`BLOCKED`/`NOT_RUN` 分开报告；提交 Handoff 与 delivery head；`git diff --check <base>..<delivery-head>` exit 0。

## 允许修改范围

- `tests/m2_acceptance/` 新增文件（建议 `test_provider_fail_closed.py`，可附共享 helper，不修改既有 `test_acceptance_loop.py` / `test_data_integrity.py`）
- `doc/tasks/M2-AC3.md`、`verification/M2-AC3/**`、`doc/handoffs/M2-AC3-*.md`

## 禁止范围

- `src/**`、`apps/**`、`doc/contracts/**`：**纯验收 Task，产品代码零改动**。发现缺陷（如半成品落库、错误被吞、状态伪造、源文件被触碰）时如实记录为 FAIL/BLOCKED 证据并停在该场景，由后续修复 Task 处理——验收不通过本身就是合法交付结果。
- SQLite schema/migration、依赖、打包、Legacy PySide6/QML、IPC 命令面扩展、既有验收套件的行为修改。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1–AC5 各场景族 | planned：`$py -m pytest tests/m2_acceptance/test_provider_fail_closed.py -v` | production assembly + 临时 data root + 固定 HEAD（worktree 根目录；`$py`=`G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe`） | NOT_RUN | 无 |
| 回归：m2_acceptance 既有套件 | planned：`$py -m pytest tests/m2_acceptance -q` | 同上（预期 15 passed + 新增） | NOT_RUN | 无 |
| 范围与空白 | planned：`git diff --check <base>..<delivery-head>` | 同上 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- depends_on=[M2-AC2]（已 `done` @ integration `9d3c1db5`）：复用其装配手法、断言口径与 `m2_acceptance` 套件；无硬阻塞。
- 风险：provider 失败注入手法（mock provider 抛错 vs 断网）由 Owner 按装配 adapter-injection 先例选择，须保证判别力（先证明语义存在）；headless 不可达的读面（如 Qt 层错误呈现）如实 NOT_RUN 并登记后续 E2E slice。
- 未定契约：无——验收只消费现有 production seam，不新增契约。

## 交付与运行记录

- Handoff：尚无（`doc/handoffs/M2-AC3-<short-head>.md`）。
- Review：尚无（DeepSeek Harness 非作者）。
- 实际测试：尚无。
- 交付后由 Integrator（新会话代行 Codex）集成：复跑验收命令、核对 allowed paths、merge 进 main、置 `done` 并填 `integration_merge`。
