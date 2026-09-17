---
id: TASK-034
title: 测试与分层硬化（route policy 收敛 / 架构守卫 / flaky 诊断）
kind: maintenance
status: proposed
approval: pending_user_review
suggested_owner: ZCode
owner: null
reviewer: null
depends_on: [TASK-019]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-034：测试与分层硬化（T-2 / T-4 / flaky 诊断）

**PROPOSED（未释放）**：需用户批准释放；未释放前不得实施。本 Task 只做**测试与结构硬化**，不改变任何产品行为。

## 来源与目标

- 来源：TASK-019 尾项切片 Review [`doc/reviews/TASK-019-ab26601.md`](../reviews/TASK-019-ab26601.md) 的 **T-2**（`runtime.py` 与 `handlers.py` 的重复 `_route_policy`）与 **T-4**（架构守卫的强度与位置）；**T-1**（flaky 登记）见 [STATUS](../STATUS.md)「已知 flaky 测试（跟踪条目）」。
- 目标：消除设置契约"同一输入两种解释"的漂移面、把分层守卫加固为 AST 版并放到更合适的位置、给两个已登记 flaky 用例加有界诊断——**全部不改变生产行为**。

## Acceptance Criteria

- [ ] `route_policy` 只有**一处**解析入口（建议 `application/translation/inpaint/router.py` 的 `RoutePolicy.from_settings(settings, default=…)`），`runtime.py` 与 `handlers.py` 都调用它；缺字段/非法类型的解释唯一且有测试锁定（当前不一致：非 mapping 时 runtime 回落默认、handlers 抛 `INVALID_INPUT`；`color_route` 缺省时 runtime 用 `brushnet`、handlers 用 `None`）。
- [ ] 架构守卫迁入 `tests/core/`，改用 AST 扫描（覆盖 `importlib.import_module("infrastructure…")` 等动态形式），并保留"修前树应报 offenders、修后树为 0"的判别力证据。
- [ ] 两个已登记 flaky 用例（`test_reader_webtoon_swaps_in_vertical_viewer`、`test_start_export_stale_abort_surfaces_failure`）加入**有界**诊断（如 `pump_until` 超时 + 失败时输出事件轨迹），**不放宽任何断言、不新增 skip**。
- [ ] 回归：`tests/providers`、`tests/core`、`tests/reading_export` 与全仓套件通过数不减少；全仓串跑至少 5 次，记录 flaky 是否仍复现（若仍复现，按同一口径登记并给出证据）。
- [ ] 交付 Handoff、实际测试/审阅记录与未完成项，经**非作者**独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

- `src/application/translation/inpaint/**`（新增 `from_settings`；不改变既有判定语义）
- `src/infrastructure/providers/runtime.py`、`src/infrastructure/providers/handlers.py`（改为调用单一入口）
- `tests/providers/**`、`tests/core/**`、`tests/reading_export/**`
- `doc/tasks/TASK-034.md`、`doc/handoffs/TASK-034-*.md`、`verification/TASK-034/**`

## 禁止范围

- 不得修改依赖清单、Schema/migration、pipeline seam 本体、`AGENTS.md`、生产数据、其他 Task。
- 不得改变任何路由判定或 provider 就绪语义（**纯收敛**：只允许把两处不一致统一为**已在文档中声明**的行为，并补测试）；如认为需要改变行为，先在 Task 中提出并由 Codex 裁决。
- 不得放宽/删除既有断言，不得新增 skip 掩盖失败，不得把 flaky 当作通过。

## 测试要求

- `python -m pytest tests/providers tests/core tests/reading_export -q`；全仓 `python -m pytest -q` 至少 5 次串跑并**逐次记录**结果。
- 分列 passed/skipped 与 skip 原因；`tests/network` 的 `openssl unavailable` 属既有环境 skip。
- 记录 commit、OS/依赖、命令、退出码与证据路径。

## 依赖、风险与阻塞

硬依赖：[TASK-019](TASK-019.md)（provider 集成层与尾项切片）已集成 `done`。

阻塞：**未获用户释放**。风险：`route_policy` 收敛若改变任一处行为，即属行为变更 → 必须回到"先裁决再改"；flaky 诊断可能仍不能根除顺序敏感（此时只需给出可复现证据并保留登记）。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际执行/测试：尚无（`proposed`，未释放）。
- 最近状态：2026-09-17 由 Codex 依 TASK-019 尾项切片 Review 的 T-2/T-4 与 STATUS 的 flaky 条目创建为 `proposed`。
