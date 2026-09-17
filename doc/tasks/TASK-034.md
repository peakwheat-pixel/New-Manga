---
id: TASK-034
title: 测试与分层硬化（route policy 收敛 / 架构守卫 / flaky 诊断）
kind: maintenance
status: in_progress
approval: approved_by_user
suggested_owner: ZCode
owner: DeepSeek Harness
reviewer: Codex
depends_on: [TASK-019]
base_commit: b34b27e2bc7c1dbd4c3b15a91f08e158d966f365
branch: agent/deepseek/TASK-034-test-layer-hardening
worktree: G:/CODEX/New Manga.worktrees/TASK-034-deepseek
integration_commit: null
---

# TASK-034：测试与分层硬化（T-2 / T-4 / flaky 诊断 / TASK-035 R-02）

**READY（2026-09-17 用户批准释放）**：Owner=`DeepSeek Harness`、Reviewer=`Codex`（**非作者**——Reviewer 不得与 Owner 同体）、base=`b34b27e`（释放时 master HEAD）、branch/worktree 见顶部元数据（已创建并同步到本次释放提交）。Owner 开始实施前，在本任务分支把 `status` 改为 `in_progress`。

**Owner 指派说明**：`suggested_owner` 原为 ZCode，本次由 Codex 指派给 **DeepSeek Harness**——理由：本 Task 属测试与结构硬化（DSH 职责含"测试、Bug 分析"），且 ZCode 的窗口授权已于 2026-09-17 撤销、当前不在线；同批次的 TASK-032/TASK-035 亦由 DSH 承接、Codex 非作者 Review。**Reviewer 随之定为 `Codex`**（非作者）。

**本 Task 只做测试与结构硬化，不改变任何产品行为。**

## 释放前核对（Codex 实测，非作者自述；master `b34b27e`）

| 项 | 状态 | 实测证据 |
|---|---|---|
| **T-2** `route_policy` 两份解析 | **仍在** | `src/infrastructure/providers/runtime.py:421 def _route_policy(settings)` 读根 `settings["inpaint"]["route_policy"]`，非 mapping → 回落 `DEFAULT_ROUTE_POLICY`（`color_route="brushnet"`、`allowed_routes=("simple-fill","edge-bleed")`）；`src/infrastructure/providers/handlers.py:617 def _route_policy(self, settings)` 的调用方 `:440` 先做 `self._section(run.settings_snapshot, "inpaint")`，故两者**实际解析同一 `inpaint.route_policy` 键**，分歧在：非 mapping 时回落 vs 抛 `ProviderInputError`、`color_route` 缺省 → `"brushnet"` vs `None`、`allowed_routes` 缺省 → 常量 vs `self.deps.route_policy` |
| **T-4** 架构守卫强度/位置 | **仍在** | `tests/providers/test_ports_contract.py:181-197` 为**行前缀扫描**（`stripped.startswith(("from infrastructure", "import infrastructure"))`），不覆盖 `importlib.import_module("infrastructure…")`；迁移目标已存在：`tests/core/test_architecture.py` 已有 **AST 版** `find_forbidden_imports`（`:17`，含 `ast.Import`/`ast.ImportFrom`） |
| 两个已登记 flaky | **仍在** | `tests/reading_export/test_qml_contract.py:211::test_reader_webtoon_swaps_in_vertical_viewer`、`tests/reading_export/test_viewmodels.py:236::test_start_export_stale_abort_surfaces_failure`（STATUS「已知 flaky 测试（跟踪条目）」） |
| TASK-035 **R-02** | **仍在** | `tests/providers/**` 4 个用例裸 `from conftest import …`；`pytest tests/providers tests/editing` → 4 collection errors、反向顺序 137 passed（TASK-035 Review 与集成均独立复现；两目录不在 TASK-035 允许路径） |
| 依赖 TASK-019 | **done** | 主体 `integration=3755af9`、尾项切片 `integration=9a5486a` |

**关键前置（必须先裁决，否则 AC ① 无法落地）**：`inpaint.route_policy` 的**设置语义在仓库内没有任何声明**——`rg "allowed_routes|color_route|brushnet" doc/` 仅命中 TASK-018 的研究/Task 文件，`doc/contracts/**`（3 份）与 D03/D06/D08 **均无**该设置契约。因此 AC ① 的"统一为**已在文档中声明**的行为"目前**没有可用锚点**。Owner **不得**自行选择一种解释并声称"文档已声明"；须按 AC ① 的裁决流程处理。

## 来源与目标

- 来源：TASK-019 尾项切片 Review [`doc/reviews/TASK-019-ab26601.md`](../reviews/TASK-019-ab26601.md) 的 **T-2**、**T-4**；**T-1** 与 [TASK-035 R-02](TASK-035.md) 见 [STATUS](../STATUS.md)「已知 flaky 测试（跟踪条目）」与 [`doc/reviews/TASK-035-6ddd955.md`](../reviews/TASK-035-6ddd955.md)。
- 目标：消除设置契约"同一输入两种解释"的漂移面、把分层守卫加固为 AST 版并放到更合适的位置、给两个已登记 flaky 用例加有界诊断、消除 `tests/providers` 的 `conftest` 收集顺序脆弱性——**全部不改变生产行为**。

## Acceptance Criteria

- [ ] **AC ①（T-2）`route_policy` 语义唯一**。分两步，**顺序不可颠倒**：
      1. **先裁决**：在 Task 中列出两处解析的**全部**可观测分歧（至少覆盖：非 mapping 的输入、`route_policy` 键缺失、`color_route` 缺省、`allowed_routes` 缺省、`requirements` 缺省）及其各自当前行为，提出**唯一**的规范解释与迁移影响，提交 Codex 裁决。**裁决前不得改变任一调用点的可观测行为。**
      2. **后收敛**：在 `application/translation/inpaint/router.py` 提供单一入口（建议 `RoutePolicy.from_settings(settings, default=…)`），`runtime.py` 与 `handlers.py` 都调用它；分歧点若需保留，必须**显式参数化**并写出理由。用测试锁定"裁决后的唯一语义"，并为**当前**两处行为各留一条回归（在行为未变时）。
- [ ] **AC ②（T-4）架构守卫加固**：把 `application → infrastructure` 守卫迁入 `tests/core/test_architecture.py` 并复用其 AST 版 `find_forbidden_imports`，覆盖 `importlib.import_module("infrastructure…")` 等动态形式；保留"修前树应报 offenders、修后树为 0"的**判别力**证据。迁移后 `tests/providers` 内的旧守卫须删除或改为调用共享实现（不得留下两套）。
- [ ] **AC ③（flaky）有界诊断**：两个已登记 flaky 用例加入**有界**诊断（如 `pump_until` 超时 + 失败时输出事件轨迹），**不放宽任何断言、不新增 skip、不把 flaky 记为通过**；若诊断后仍复现，按同一口径登记并给出证据。
- [ ] **AC ④（TASK-035 R-02）`conftest` 脆弱性消除**：把 `tests/providers/**` 共享替身移入**唯一命名**的 helper 模块（如 `tests/providers/providers_helpers.py`）并改为显式导入，使 `pytest tests/providers tests/editing` 与反向顺序**均 0 collection errors**；给出两种顺序的实测证据。
- [ ] **AC ⑤ 回归与分列**：`tests/providers`、`tests/core`、`tests/reading_export` 与全仓套件 **passed 不减少**；全仓串跑**至少 5 次**逐次记录 passed/skipped 与退出码。
- [ ] **AC ⑥** 交付 Handoff、实际测试/审阅记录与未完成项，经**非作者** Review（按协作协议 §6 四轴）与 Codex 集成验证后才能 done。

## 允许修改范围

- `tests/**`
- `doc/tasks/TASK-034.md`、`doc/handoffs/TASK-034-*.md`、`verification/TASK-034/**`
- **`src/` 需先申请范围变更**：仅当 AC ① 第 2 步确需改动 `src/application/translation/inpaint/router.py`、`src/infrastructure/providers/runtime.py`、`src/infrastructure/providers/handlers.py` 时，**先在本 Task 提出范围变更并由 Codex 裁决**；裁决前 `src/` 一律按禁止范围处理。

## 禁止范围

- 不得修改依赖清单、Schema/migration、pipeline seam 本体、`AGENTS.md`、生产数据、其他 Task。
- **不得自行改变任何路由判定或 provider 就绪语义**；AC ① 第 1 步未获裁决前，不得把两处不一致"顺手统一"。
- 不得放宽/删除既有断言，不得新增 skip 掩盖失败，不得把 flaky 当作通过。
- 不得释放其他冻结 Task（TASK-020～TASK-023、TASK-025～TASK-027、TASK-033 保持冻结/`proposed`）。

## 测试要求

- `python -m pytest tests/providers tests/core tests/reading_export -q -p no:cacheprovider -rs`。
- 全仓 `python -m pytest -q -p no:cacheprovider -rs` **至少 5 次**串跑并**逐次记录**；分列 passed/skipped 与 skip 原因（`tests/network` 的 `openssl unavailable` 属既有环境 skip）。
- AC ④ 须给出**两种收集顺序**的对照证据；AC ② 须给出判别力证据。
- 记录 commit、OS/依赖、命令、退出码与证据路径。

## 依赖、风险与阻塞

硬依赖：[TASK-019](TASK-019.md)（provider 集成层与尾项切片）已集成 `done`。

阻塞：**已解除**——2026-09-17 用户批准释放（`approval=approved_by_user`）。

风险：
- **AC ① 的裁决依赖**：设置语义未文档化（见上「关键前置」），若 Owner 跳过裁决直接统一，将构成**行为变更**（违反禁止范围）→ 必须先提出、先裁决。
- **flaky 可能无法根除**：顺序/时序敏感可能只降低而不消除（本环境已观测既有 flaky 污染"全仓 N passed"证据）→ 此时只需给出可复现证据并保留登记。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际执行/测试：尚无（`ready`，实施未开始）。
- **最近状态（当前，唯一）**：2026-09-17 由用户批准释放；Codex 登记 `status=ready`、`approval=approved_by_user`、Owner=`DeepSeek Harness`、Reviewer=`Codex`（**非作者**）、base=`b34b27e`（释放时 master HEAD）、branch=`agent/deepseek/TASK-034-test-layer-hardening`、worktree=`G:/CODEX/New Manga.worktrees/TASK-034-deepseek`（已创建并同步到本次释放提交），并完成上表「释放前核对」（T-2 / T-4 / 两个 flaky / TASK-035 R-02 / 依赖均在，且发现 AC ① 缺少已声明的语义锚点 → 已写入「关键前置」要求先裁决）。**实施尚未开始**。
- 历史状态（2026-09-17）：由 Codex 依 TASK-019 尾项切片 Review 的 T-2/T-4 与 STATUS 的 flaky 条目创建为 `proposed`（`approval=pending_user_review`，owner/reviewer/base/branch/worktree 均为空）；同日并入 TASK-035 Review 的 R-02（`tests/providers` conftest 收集顺序脆弱性，转由本 Task 承接）。
