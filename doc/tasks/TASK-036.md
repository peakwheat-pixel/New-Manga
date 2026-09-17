---
id: TASK-036
title: 设置输入校验与导出发布顺序硬化（承接 TASK-034 R-02 / R-05 / R-07）
kind: maintenance
status: ready
approval: approved_by_user
suggested_owner: DeepSeek Harness
owner: DeepSeek Harness
reviewer: Codex
depends_on: [TASK-034]
base_commit: edfdcf2fe923c8c6e97d19377c61c4b8bba25abc
branch: agent/deepseek/TASK-036-settings-validation-and-export-order
worktree: G:/CODEX/New Manga.worktrees/TASK-036-deepseek
integration_commit: null
---

# TASK-036：设置输入校验与导出发布顺序硬化

**READY（2026-09-17 用户批准释放）**：Owner=`DeepSeek Harness`、Reviewer=`Codex`（**非作者**）、base=`edfdcf2`（释放时 master HEAD）、branch/worktree 见顶部元数据（已创建并同步到本次释放提交）。Owner 开始实施前，在本任务分支把 `status` 改为 `in_progress`。

本 Task 是 [TASK-034](TASK-034.md) 登记的三项**仓库级遗留**的收口切片；**不改变任何路由判定算法**。

## 来源

| 项 | 来源 | 现状（Codex 释放前实测，master `edfdcf2`） |
|---|---|---|
| **R-02** | TASK-034 Review [R-02](../reviews/TASK-034-002889e.md)（并入原 R-07 冻结项） | `RoutePolicy.from_settings({'inpaint': 'oops'}, default=…)` → **静默返回默认**（`inpaint` **段本身**非 mapping 被当作"键缺失"）。`route_policy` 非 mapping 已是 fail-loud（TASK-034 R-2），**段**类型错误却仍被静默忽略 |
| **R-07a** | [TASK-034 AC ① 裁决](TASK-034-ac1-route-policy-ruling.md) R-7（本次解除冻结） | `allowed_routes='simple-fill'` → **逐字符展开** 11 个单字符 `('s','i','m',…)`；`fallback_routes` 同型 |
| **R-07b** | 同上（D-9 记录的同型陷阱） | `requirements={'brushnet': 'false'}` → `{'brushnet': True}`（`bool("false")` 恒真） |
| **R-05** | TASK-034 Review R-05 / Handoff N-1 | `src/ui/viewmodels/export/viewmodel.py` 的 `_finish`（`:379-389`）与 `_fail`（`:391-398`）**先清 `self._running`，后写 `_status` 并 emit 终态信号** → 观察者可在"标志已清、终态未发布"的**半发布窗口**内读到不一致状态（导出类测试 flaky 的机制根因） |

**判据来源（本轮已在文内固化，无需再裁决）**：R-02/R-07 的目标语义沿用 TASK-034 R-2 已确立的 **fail-closed** 原则——"用户写错的配置不得被无声忽略或无声改写"（该原则已由用户批准的裁决确立）。**若实现中发现与既有文档/测试冲突，先在 Task 中留证并交 Codex 裁决，不得自行放宽。**

## Acceptance Criteria

- [ ] **AC ①（R-02）`inpaint` 段类型错误 fail-loud**：`settings` 中 `inpaint` 键**存在且非 mapping** 时，`from_settings` 抛 `ProviderInputError`，错误信息须明确区分"段类型错误"与既有的"`route_policy` 非 mapping"；装配路径（`build_provider_runtime`）与运行路径（Inpaint Step）**行为一致**，各留一条回归。**不得**把该错误静默降级为"键缺失"。
- [ ] **AC ②（R-07a）序列校验**：`allowed_routes` / `fallback_routes` 必须是**字符串序列**。**字符串本身必须被拒绝**（不得再逐字符展开）；元素非 `str` 亦拒绝。错误须为 `ProviderInputError`（`INVALID_INPUT`），信息指出字段名与期望类型。
- [ ] **AC ③（R-07b）`requirements` 值域**：值必须是真正的 `bool`；`"false"`/`"true"`/`0`/`1` 等**一律拒绝**（不再 `bool()` 强制转换）。空 `requirements` 与全 `bool` 的 `requirements` 行为不变。
- [ ] **AC ④（R-05）导出发布顺序**：`_finish`/`_fail` 改为**先发布终态（`_status` + `changed` + 终态信号 `exportFinished`/`exportFailed`）再清 `self._running`**，使任何观察者在 `running == False` 时必然已能看到终态；`tests/reading_export` 的导出用例等待随之回到**自然的终态等待**（等待预算不得放宽、断言不得放宽/删除）；`test_export_outcome_wait_does_not_accept_the_half_published_state` 按新顺序更新而**不得删除**。
- [ ] **AC ⑤ 冻结解除声明**：本轮**解除 R-07 冻结**，必须同步更新上一轮锁定冻结行为的测试（至少 `test_allowed_routes_as_string_keeps_the_frozen_char_expansion`、`test_fallback_routes_and_requirements_defaults_are_frozen` 中的 `bool("false")` 断言），并在 Handoff 显式说明"冻结已由本 Task 解除"。
- [ ] **AC ⑥ 语义不变性证据**：给出矩阵，证明**合法输入的含义一字未变**（TASK-034 裁决的 R-1～R-6 全部保持），且只有"非法输入"的处理由静默/改写改为报错；对 `from_settings` 的 12 类输入逐条给出前后对照。
- [ ] **AC ⑦ 回归与分列**：`tests/providers`、`tests/core`、`tests/reading_export`、`tests/editing`、全仓套件 **passed 不减少**；全仓串跑**至少 5 次**逐次记录 passed/skipped 与退出码。
- [ ] **AC ⑧** 交付 Handoff、实际测试/审阅记录与未完成项，经**非作者** Review（协作协议 §6 四轴）与 Codex 集成验证后才能 done。

## 允许修改范围

- `src/application/translation/inpaint/router.py`（AC ①②③）
- `src/ui/viewmodels/export/viewmodel.py`（AC ④）
- `tests/**`
- `doc/tasks/TASK-036.md`、`doc/handoffs/TASK-036-*.md`、`verification/TASK-036/**`
- **超出以上路径需先申请范围变更并由 Codex 裁决**（例如 AC ①②③ 若确需改动 `src/infrastructure/providers/runtime.py`/`handlers.py`）。

## 禁止范围

- 不得修改路由**判定算法**（`decide_route` / `acceptable_routes` / `preferred_route_order` / `route_gate` / `RouterFeatures`）、`RoutePolicy` 的既有合法语义（TASK-034 裁决 R-1～R-6）、Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、其他 Task。
- 不得放宽/删除既有断言，不得新增 `skip`/`xfail` 掩盖失败。
- **不处理 R-06**（`tests/reading_export` 的 webtoon 保存 flaky：未复现、根因未定）与 **R-03**（`DEFAULT_ROUTE_POLICY` 跨层归属，纯建议）——它们不在本 Task 范围。
- 不得把已登记的 flaky 或未定性间歇失败记为通过；不得释放 TASK-020～TASK-023、TASK-025～TASK-027、TASK-033。
- 不 push。

## 测试要求

- `python -m pytest tests/providers tests/core tests/reading_export tests/editing -q -p no:cacheprovider -rs`
- 全仓 `python -m pytest -q -p no:cacheprovider -rs` **至少 5 次**串跑并**逐次记录**（本环境全仓串跑非 100% 稳定，见 [STATUS](../STATUS.md)「已知 flaky 测试（跟踪条目）」；若复现失败**立即用 `-rf` 记录用例名**并按同一口径登记）。
- AC ④ 须给出"发布顺序改变后，观察者在 `running == False` 时必已见终态"的证据（如断言顺序敏感的用例或定向探针）。
- 分列 passed/skipped 与 skip 原因；记录 commit、OS/依赖、命令、退出码与证据路径。

## 依赖、风险与阻塞

硬依赖：[TASK-034](TASK-034.md) 已集成 `done`（唯一入口 `RoutePolicy.from_settings` 与导出诊断均由该 Task 落地）。

阻塞：**已解除**——2026-09-17 用户批准释放。

风险：
- **校验收紧可能触发现有测试**：若某既有测试依赖"静默/强制转换"的旧行为，须按 AC ⑤ 显式更新并说明，**不得**靠放宽断言绕过。
- **R-05 的发布顺序改动触及 `src/ui/**`**：须确认 `tests/ui_shell`、`tests/workbench`、`tests/reading_export` 均未依赖旧顺序；若发现消费方依赖旧顺序，先在 Task 中留证并交 Codex 裁决。
- R-06 未定性间歇失败可能再次污染"全仓 N passed"证据（已登记，非本 Task 缺陷）。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际执行/测试：尚无（`ready`，实施未开始）。
- **最近状态（当前，唯一）**：2026-09-17 由用户批准释放；Codex 登记 `status=ready`、`approval=approved_by_user`、Owner=`DeepSeek Harness`、Reviewer=`Codex`（**非作者**）、base=`edfdcf2`（释放时 master HEAD）、branch=`agent/deepseek/TASK-036-settings-validation-and-export-order`、worktree=`G:/CODEX/New Manga.worktrees/TASK-036-deepseek`，并完成上表「来源」栏的**释放前实测**（R-02/R-07a/R-07b/R-05 四项现状均在）。**实施尚未开始。**
- 判据说明：R-02/R-07 的目标语义沿用 TASK-034 R-2 已确立的 fail-closed 原则（用户已批准），因此本 Task **无需**先走一次裁决请求；实现中若与既有文档/测试冲突，按上文回抛。
