---
id: TASK-034
title: 测试与分层硬化（route policy 收敛 / 架构守卫 / flaky 诊断）
kind: maintenance
status: done
approval: approved_by_user
suggested_owner: ZCode
owner: DeepSeek Harness
reviewer: Codex
depends_on: [TASK-019]
base_commit: b34b27e2bc7c1dbd4c3b15a91f08e158d966f365
branch: agent/deepseek/TASK-034-test-layer-hardening
worktree: G:/CODEX/New Manga.worktrees/TASK-034-deepseek
integration_commit: 8ca4b232397b182fabdfd1aa3798ff23409d85d6
---

# TASK-034：测试与分层硬化（T-2 / T-4 / flaky 诊断 / TASK-035 R-02）

**状态提示（2026-09-17）**：`status=done`——**AC ①～⑥ 全部完成，两轮均经非作者四轴 Review 并集成**。AC ① 第 1 步裁决请求见 [verification/TASK-034/route-policy-decision-request.md](../../verification/TASK-034/route-policy-decision-request.md)、裁决见 [doc/reviews/TASK-034-ac1-route-policy-ruling.md](../reviews/TASK-034-ac1-route-policy-ruling.md)（含裁决方文本勘误）、第 2 步实现 + 强制项 R-01 见 [verification/TASK-034/ac1-step2-author-verification.md](../../verification/TASK-034/ac1-step2-author-verification.md) 与 [Handoff](../handoffs/TASK-034-002889e.md)。上一轮（AC ②③④⑤）集成 `b6051e5` / 元数据 `34823b9`；本轮尾项切片 delivery head **`002889e`**、Review `55a69de`、**integration `8ca4b23`**（复验 [integration-8ca4b23.md](../../verification/TASK-034/integration-8ca4b23.md)）。

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

- [x] **AC ①（T-2）`route_policy` 语义唯一**。分两步，**顺序不可颠倒**：
      1. **先裁决**：**已完成（第 1 步）**——[裁决请求](../../verification/TASK-034/route-policy-decision-request.md) 列出两处解析的全部 12 类可观测分歧（含非 mapping、键缺失、`color_route` 缺省/空白、`allowed_routes` 缺省/空/字符串、`requirements` 缺省/非 bool、`fallback_routes`、"常量 vs 注入默认"）与各自当前行为，提出唯一规范解释（R-1～R-6；R-6 给出 A/B 两案，推荐 **Option B：默认不指定彩色路线**）与迁移影响（含 `src/` 三文件范围变更申请）。只读探针证据：[`route-policy-divergences.txt`](../../verification/TASK-034/route-policy-divergences.txt)（6 例 SAME / 6 例 DIVERGES）。**`src/` 未改，两处调用点行为未变。** Codex 已裁决：[doc/reviews/TASK-034-ac1-route-policy-ruling.md](../reviews/TASK-034-ac1-route-policy-ruling.md)（R-1～R-7，批准 3 文件 `src/` 范围）。
      2. **后收敛**：**已完成（第 2 步）**——`RoutePolicy.from_settings(settings, *, default)` 成为唯一入口（R-1 显式默认 / R-2 两处一致报错 / R-3 取 `default.allowed_routes` / R-4·R-5 冻结 / R-6 Option B）；两处私有 `_route_policy` 删除；`build_production_handlers` 第三份字面量改为复用 `DEFAULT_ROUTE_POLICY`；`DEFAULT_ROUTE_POLICY` 对齐 `allowed=("simple-fill","edge-bleed")`、`color_route=None`、`requirements={}`。测试：12 类输入矩阵 + 两处调用点各一条回归 + Option B/R-2 可观测变化 + 四组合决策不变性（[`ac1-step2-author-verification.md`](../../verification/TASK-034/ac1-step2-author-verification.md) §2/§3）。
- [x] **AC ②（T-4）架构守卫加固**：守卫迁入 `tests/core/test_architecture.py` 并**复用/扩展**其 AST 版 `find_forbidden_imports`（新增字面量 `importlib.import_module`/`__import__` 检测）；`tests/providers` 内旧行前缀守卫**已删除**（不留两套，仅留指向注释）。判别力：现树 0、历史树 `726baf5` **2**（`step.py:23,29`）、合成动态导入**新 1 / 旧 0**（[`guard-discriminative.txt`](../../verification/TASK-034/guard-discriminative.txt)）。
- [x] **AC ③（flaky）有界诊断**：两个已登记用例均加**有界**诊断，**未放宽任何断言、未新增 skip、未把 flaky 记为通过**——webtoon 用例引入 `pump_traced`（迭代/耗时轨迹）+ `webtoon_save_diagnostics`（`contentY`/服务端 offset/`Image.status`/对象名），等待预算保持 5/5/2 秒；导出用例把"等 `not vm.running`"改为**等终态信号**（含 `export_diagnostics` 状态轨迹），并新增确定性"半发布窗口"判别测试。**全仓 12 次串跑（诊断前 6 + 后 6）0 失败 → 如实登记"未复现"**，机制根因与候选见 [取证 §2/§5](../../verification/TASK-034/author-verification.md)。
- [x] **AC ④（TASK-035 R-02）`conftest` 脆弱性消除**：共享替身移入唯一命名 `tests/providers/providers_helpers.py` 并显式导入；`pytest tests/providers tests/editing` 与反向顺序**均 136 passed、0 collection errors**（基线顺序 A = 4 collection errors，[`collection-orders-before.txt`](../../verification/TASK-034/collection-orders-before.txt) / [`collection-orders.txt`](../../verification/TASK-034/collection-orders.txt)）。**同根因的强制项 R-01**（`tests/reading_export` 的 `requires_pyside6`）已在本轮尾项切片关闭：移入唯一命名 `reading_export_helpers` 并显式导入，**十种收集顺序全部 exit 0**（修复前六种伙伴目录顺序 exit 2 / 2 errors，[`r01-collection-orders-before.log`](../../verification/TASK-034/r01-collection-orders-before.log) / [`-after.log`](../../verification/TASK-034/r01-collection-orders-after.log)）。
- [x] **AC ⑤ 回归与分列**：mandated 三套件 **217 passed / 0 skipped**（上一轮 193 → 本轮 +24）；`tests/core`+`storage`+`providers` 与 `tests/editing`+`storage`+`pipeline` 均全绿；全仓 **706 passed / 6 skipped ×4 次**（逐次退出码 0，6 条 skip 均为既有 `tests/network` 的 `openssl unavailable`）。逐目录对照（`34823b9 → 002889e`）：providers 110→134、core 18→18、reading_export 65→65、全仓 682→706（[`ac1-step2-counts.txt`](../../verification/TASK-034/ac1-step2-counts.txt)）。
- [x] **AC ⑥** 交付 Handoff、实际测试/审阅记录与未完成项，经**非作者** Review（按协作协议 §6 四轴）与 Codex 集成验证后才能 done。
      → Handoff 与取证已交付；**AC ②③④⑤ 已完成非作者四轴 Review 与集成**（Review `abda60f` approved、integration=`b6051e5`）；**尾项切片（AC ① 第 2 步 + R-01）亦已非作者四轴 Review `approved`（`55a69de`）并集成（`8ca4b23`）** → 本项勾选。

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

- Handoff：[TASK-034-f83a33e](../handoffs/TASK-034-f83a33e.md)（delivery_head=`f83a33e`）。
- Review（AC ②③④⑤ 部分）：[doc/reviews/TASK-034-f83a33e.md](../reviews/TASK-034-f83a33e.md)（Reviewer=Codex，**非作者**；commit `abda60f`；decision=**`approved`**；四轴 Standards / Spec / Architecture / Verification 均 `executed`、逐轴小结、**未跨轴排名**；**并行偏差已声明**——未取得两条独立 sub-agent 线程，按 §6 第 6 条兜底做两遍相互隔离检查）。Findings：**R-01（P2）**=`tests/reading_export` 裸 `conftest` 导入（与 AC ④ 同根因，六种伙伴目录顺序均 2 collection errors；**既有**缺陷）**deferred 且绑定为 AC ① 第 2 步的强制项**；R-02（P3，AC ⑤ 逐目录计数口径）**accepted**；R-03（P3，webtoon 首处观察窗口）**accepted（已披露）**；R-04（P3，半发布窗口判别测试用合成假对象）**open 非阻塞**；R-05（P3，生产侧发布顺序）与 R-06（P3，flaky 未复现）**deferred**；R-07（P3，`allowed_routes` 为字符串/`requirements` 非 bool 的强制转换）**本次冻结 + 登记**。
- AC ① 裁决（第 1 步产出）：[doc/reviews/TASK-034-ac1-route-policy-ruling.md](../reviews/TASK-034-ac1-route-policy-ruling.md)（R-1 认可、R-2 认可**并须记录装配路径由静默回落变为启动期报错**、R-3 认可、R-4 冻结、R-5 冻结、**R-6 采纳 Option B** 且 `DEFAULT_ROUTE_POLICY` 须对齐 `RoutePolicy` 默认与 TASK-018 的 `default_eligible`、R-7 冻结+登记；**`src/` 三文件范围变更已批准**并限定不改路由判定算法/Schema/依赖/seam）。
- 集成（AC ②③④⑤）：`integration_commit=b6051e5`（merge，parents `abda60f` + `8ca99d4`）；复验 [verification/TASK-034/integration-b6051e5.md](../../verification/TASK-034/integration-b6051e5.md)（master 上 mandated 三套件 **193 passed/0 skipped**、AC ④ 两种顺序 **136/136 passed**、全仓 **682 passed/6 skipped** 全为既有 `openssl unavailable`；`src/` 零改动）。
- Review + 集成（尾项切片 AC ① 第 2 步 + R-01）：Review [doc/reviews/TASK-034-002889e.md](../reviews/TASK-034-002889e.md)（Reviewer=Codex，**非作者**；commit `55a69de`；decision=**`approved`**；四轴均 `executed`、逐轴小结、**不跨轴排名**；**并行偏差已声明**——`code-review` 技能要求的并行双轴子代理已实际派发但未取得执行槽，按 §6 第 6 条兜底两遍相互隔离检查）；`integration_commit=8ca4b23`（merge，parents `55a69de` + `132e776`）；复验 [verification/TASK-034/integration-8ca4b23.md](../../verification/TASK-034/integration-8ca4b23.md)（master 上 mandated 三套件 **217 passed/0 skipped**、R-01 两种顺序 **91/91 passed**、AC ① 聚焦 **35 passed**、`rg "_route_policy" src/` = 0；`src/` 恰为批准 3 文件。**全仓串跑 14 次：13 次 `706 passed/6 skipped`、1 次 1 failed（用例名未捕获，已如实登记为未定性间歇失败，未归因本切片）**）。
- **尾项切片（AC ① 第 2 步 + 强制项 R-01）**：Handoff [TASK-034-002889e](../handoffs/TASK-034-002889e.md)；取证 [verification/TASK-034/ac1-step2-author-verification.md](../../verification/TASK-034/ac1-step2-author-verification.md)；`delivery_head=002889e`（先 `git merge master` 快进到 `34823b9`）。实现：`RoutePolicy.from_settings(settings, *, default)` 唯一入口（R-1 显式默认 / R-2 两处一致报错 / R-3 `default.allowed_routes` / R-4·R-5 冻结 / **R-6 Option B**）、删除两处私有 `_route_policy`、`build_production_handlers` 复用 `DEFAULT_ROUTE_POLICY`、默认策略对齐 `allowed=("simple-fill","edge-bleed")`/`color_route=None`/`requirements={}`；R-01：`requires_pyside6` 移入唯一命名 `tests/reading_export/reading_export_helpers.py` 并显式导入。**未改动**路由判定算法/Schema/依赖/seam/`src/ui/**`/其他 Task；`src/` 改动恰为批准的 3 个文件。
- **必须记录的可观测变化**（[`ac1-decision-invariance.txt`](../../verification/TASK-034/ac1-decision-invariance.txt)）：①`runtime.status()["route_policy"]` 由 `allowed=[brushnet, edge-bleed, simple-fill]`/`color=brushnet` 变为 `allowed=('simple-fill','edge-bleed')`/`color=None`/`requirements={}`（记录刷新）；②彩色场景 `brushnet` 候选理由由 `not implemented: …` 变为 `not in the configured route policy`；③**R-2 是唯一可能让应用启动失败的语义变化**（装配路径由静默回落改为启动期报配置错误）。**决策不变性**：彩色 webtoon、高复杂度两侧均 BLOCKED；线稿、普通两侧均 RUN `edge-bleed`——四组 `decision`/`route` 逐项未变。**⚠ 与裁决措辞差异（已如实登记）**：裁决第 62 行称四种组合"均 BLOCKED"，实测线稿/普通为 RUN `edge-bleed`（实质要求"选中路线未变"成立）；若裁决方要求这两组也 BLOCKED，属**判定算法**变更，需另立裁决。
- **AC ① 第 2 步与强制项 R-01 已关闭**（R-01：十种收集顺序修复前 6 种 exit 2 / 修复后全部 exit 0）。**仓库级后续项（非本 Task 缺陷，已登记）**：**R-02**（`inpaint` 段本身非 mapping 静默回落）与 **R-07**（输入校验收紧，含 R-02）→ 建议合并为一个"设置输入校验"切片；**R-03**（`DEFAULT_ROUTE_POLICY` 跨层归属，P3 建议）；**R-05**（`src/ui/viewmodels/export/viewmodel.py:380/389`、`:392/398` 发布顺序，需 `src/ui/**` 范围另立切片）；**R-06**（webtoon flaky 未复现，诊断已就位）。
- 实际执行/测试（尾项切片 `002889e`）：
  - mandated 三套件 `tests/providers tests/core tests/reading_export` **217 passed / 0 skipped**（上一轮 193 → +24：AC ① 矩阵 22 + 运行调用点回归 2）；全仓 **706 passed / 6 skipped ×4 次**（逐次退出码 0；6 条 skip 全为既有 `tests/network` 的 `openssl unavailable`）；`tests/editing`+`tests/storage`+`tests/pipeline` 120 passed。逐目录（`34823b9 → 002889e`）：providers 110→134、core 18→18、reading_export 65→65、全仓 682→706（[`ac1-step2-counts.txt`](../../verification/TASK-034/ac1-step2-counts.txt)）。
  - AC ① 矩阵：[`test_route_policy_settings.py`](../../tests/providers/test_route_policy_settings.py)（22 例，覆盖 12 类输入 + 默认/配置锁定）；运行调用点回归：`test_handlers_pipeline.py::test_run_settings_route_policy_goes_through_the_shared_parser` 与 `…_malformed_route_policy_fails_the_step_loudly`。
  - R-01 顺序对照：[`r01-collection-orders-before.log`](../../verification/TASK-034/r01-collection-orders-before.log)（修复前六种伙伴目录顺序 exit 2 / 2 errors）→ [`r01-collection-orders-after.log`](../../verification/TASK-034/r01-collection-orders-after.log)（**十种顺序全部 exit 0**）；全仓已无裸 `conftest` 导入。
  - 边界：Owner 改动 = 3 个已批准 `src/` 文件 + `tests/**` + `verification/TASK-034/**`；越界 0；`git diff --check` 退出码 0。
- **最近状态（当前，唯一）**：2026-09-17 **`done`**——AC ①～⑥ 全部完成；两轮均经非作者四轴 Review 并集成（AC ②③④⑤：Review `abda60f` approved → integration `b6051e5`、metadata `34823b9`；尾项切片 AC ① 第 2 步 + R-01：Review `55a69de` approved → integration `8ca4b23`）。分支 `agent/deepseek/TASK-034-test-layer-hardening`、worktree `G:/CODEX/New Manga.worktrees/TASK-034-deepseek`、fixed base `b34b27e`。**未 push；未自行合并 master（仅把 master 快进合入本分支）；未释放任何冻结 Task。** 越界发现登记（未修改）：**N-1**＝R-05（导出 viewmodel 发布顺序，`src/ui/**` 超出允许范围，需另立切片）；**N-2**＝R-06（webtoon flaky 未复现，诊断已就位）；**N-3** 已由裁决与实现**关闭**（`inpaint.route_policy` 语义唯一）；另新增登记 **R-02/R-03/R-07**（输入校验与常量归属，均 P3）。**集成后全仓串跑 14 次：13 次 `706 passed, 6 skipped`、1 次 1 failed（用例名未捕获，已登记为未定性间歇失败）** —— 详见 [integration-8ca4b23.md](../../verification/TASK-034/integration-8ca4b23.md)。
- 历史状态（2026-09-17）：由 Codex 依 TASK-019 尾项切片 Review 的 T-2/T-4 与 STATUS 的 flaky 条目创建为 `proposed`，同日并入 TASK-035 Review 的 R-02；随后用户批准释放为 `ready`（Owner=`DeepSeek Harness`、Reviewer=`Codex`、base=`b34b27e`）。
