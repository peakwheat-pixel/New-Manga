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
integration_commit: b6051e5b567749b681810e664946fd98da70b1b4
---

# TASK-034：测试与分层硬化（T-2 / T-4 / flaky 诊断 / TASK-035 R-02）

**状态提示（2026-09-17）**：`status=in_review`——**AC ②③④⑤ 已完成并取证**；**AC ① 只交付第 1 步（裁决请求），第 2 步按 Task 要求冻结，`src/` 零改动**，等待 Codex 裁决。证据总表见 [verification/TASK-034/author-verification.md](../../verification/TASK-034/author-verification.md)，裁决请求见 [verification/TASK-034/route-policy-decision-request.md](../../verification/TASK-034/route-policy-decision-request.md)，交付说明见 [Handoff](../handoffs/TASK-034-f83a33e.md)。**AC ① 不得记为达成。**

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

- [~] **AC ①（T-2）`route_policy` 语义唯一**。分两步，**顺序不可颠倒**：
      1. **先裁决**：**已完成（第 1 步）**——[裁决请求](../../verification/TASK-034/route-policy-decision-request.md) 列出两处解析的全部 12 类可观测分歧（含非 mapping、键缺失、`color_route` 缺省/空白、`allowed_routes` 缺省/空/字符串、`requirements` 缺省/非 bool、`fallback_routes`、"常量 vs 注入默认"）与各自当前行为，提出唯一规范解释（R-1～R-6；R-6 给出 A/B 两案，推荐 **Option B：默认不指定彩色路线**）与迁移影响（含 `src/` 三文件范围变更申请）。只读探针证据：[`route-policy-divergences.txt`](../../verification/TASK-034/route-policy-divergences.txt)（6 例 SAME / 6 例 DIVERGES）。**`src/` 未改，两处调用点行为未变。**
      2. **后收敛**：**BLOCKED（等待 Codex 裁决与 `src/` 范围批准）**——裁决前不得改动任一调用点；裁决后申请获批再在 `application/translation/inpaint/router.py` 落地 `RoutePolicy.from_settings(settings, *, default)` 并补"两处调用点各一条回归"。
- [x] **AC ②（T-4）架构守卫加固**：守卫迁入 `tests/core/test_architecture.py` 并**复用/扩展**其 AST 版 `find_forbidden_imports`（新增字面量 `importlib.import_module`/`__import__` 检测）；`tests/providers` 内旧行前缀守卫**已删除**（不留两套，仅留指向注释）。判别力：现树 0、历史树 `726baf5` **2**（`step.py:23,29`）、合成动态导入**新 1 / 旧 0**（[`guard-discriminative.txt`](../../verification/TASK-034/guard-discriminative.txt)）。
- [x] **AC ③（flaky）有界诊断**：两个已登记用例均加**有界**诊断，**未放宽任何断言、未新增 skip、未把 flaky 记为通过**——webtoon 用例引入 `pump_traced`（迭代/耗时轨迹）+ `webtoon_save_diagnostics`（`contentY`/服务端 offset/`Image.status`/对象名），等待预算保持 5/5/2 秒；导出用例把"等 `not vm.running`"改为**等终态信号**（含 `export_diagnostics` 状态轨迹），并新增确定性"半发布窗口"判别测试。**全仓 12 次串跑（诊断前 6 + 后 6）0 失败 → 如实登记"未复现"**，机制根因与候选见 [取证 §2/§5](../../verification/TASK-034/author-verification.md)。
- [x] **AC ④（TASK-035 R-02）`conftest` 脆弱性消除**：共享替身移入唯一命名 `tests/providers/providers_helpers.py` 并显式导入；`pytest tests/providers tests/editing` 与反向顺序**均 136 passed、0 collection errors**（基线顺序 A = 4 collection errors，[`collection-orders-before.txt`](../../verification/TASK-034/collection-orders-before.txt) / [`collection-orders.txt`](../../verification/TASK-034/collection-orders.txt)）。
- [x] **AC ⑤ 回归与分列**：mandated 三套件 **193 passed / 0 skipped**、`tests/core`+`storage`+`providers` **161 passed**；全仓 **682 passed / 6 skipped ×6 次**（逐次退出码 0，6 条 skip 均为既有 `tests/network` 的 `openssl unavailable`）。逐目录对照：providers 111→110（守卫**迁出**所致，无断言语义删除）、core 15→18、reading_export 64→65、净 +3（[`test-counts.txt`](../../verification/TASK-034/test-counts.txt)）。
- [ ] **AC ⑥** 交付 Handoff、实际测试/审阅记录与未完成项，经**非作者** Review（按协作协议 §6 四轴）与 Codex 集成验证后才能 done。
      → Handoff 与取证已交付；**AC ②③④⑤ 已完成非作者四轴 Review 与集成**（Review `approved`、integration=`b6051e5`）。**AC ① 第 2 步与 R-01 未关闭前本 Task 不标记 `done`** → 本项保持未勾选。

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
- 集成：`integration_commit=b6051e5`（merge，parents `abda60f` + `8ca99d4`）；复验 [verification/TASK-034/integration-b6051e5.md](../../verification/TASK-034/integration-b6051e5.md)（master 上 mandated 三套件 **193 passed/0 skipped**、AC ④ 两种顺序 **136/136 passed**、全仓 **682 passed/6 skipped** 全为既有 `openssl unavailable`；`src/` 零改动）。
- **未关闭项（本 Task 不得 `done` 的原因）**：①**AC ① 第 2 步**未开始（裁决已出，可实施）；②**R-01** 必须在第 2 步切片内一并消除（强制，非可选）；③R-05/R-06/R-07 已登记待后续切片。
- 实际执行/测试：
  - 取证总表：[verification/TASK-034/author-verification.md](../../verification/TASK-034/author-verification.md)；AC ① 裁决请求：[route-policy-decision-request.md](../../verification/TASK-034/route-policy-decision-request.md) + [route-policy-divergences.txt](../../verification/TASK-034/route-policy-divergences.txt)；AC ② 判别力：[guard-discriminative.txt](../../verification/TASK-034/guard-discriminative.txt)；AC ④ 前后对照：[collection-orders.txt](../../verification/TASK-034/collection-orders.txt) / [collection-orders-before.txt](../../verification/TASK-034/collection-orders-before.txt)；AC ③⑤ 串跑：[flaky-repro-after.log](../../verification/TASK-034/flaky-repro-after.log)（×6）/ [flaky-repro-before.log](../../verification/TASK-034/flaky-repro-before.log)（×6）；逐目录计数：[test-counts.txt](../../verification/TASK-034/test-counts.txt)；边界：[changed-paths.txt](../../verification/TASK-034/changed-paths.txt)。
  - 命令与结果（`TASK-012-py312`，Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1，`PYTHONDONTWRITEBYTECODE=1`，全部 `-p no:cacheprovider`）：mandated `tests/providers tests/core tests/reading_export` **193 passed / 0 skipped**；`tests/providers tests/editing` 与反向顺序 **136 / 136 passed、0 collection errors**；`tests/core tests/storage tests/providers` **161 passed**；全仓 **682 passed / 6 skipped ×6 次**（诊断前为 681×6；6 条 skip 均为既有 `tests/network` 的 `openssl unavailable`）。逐目录：providers 111→110、core 15→18、reading_export 64→65、全仓 679→682。边界：Owner 改动全在 `tests/**` + 文档允许路径、越界 0；**`src/` 零改动**；`git diff --check b34b27e..HEAD` 退出码 0。
  - 既有两个 flaky：**12 次全仓串跑 0 复现**（如实登记，不记为通过）；诊断已就位，机制根因（N-1 生产侧发布顺序）与候选（N-2）见取证 §2/§5。
- **最近状态（当前，唯一）**：2026-09-17 **AC ②③④⑤ 已 Review `approved` 并集成（`b6051e5`）**；**AC ① 第 1 步已交付、裁决已出（R-1～R-7 + `src/` 三文件范围批准），第 2 步未开始**；整体 `status=in_progress`（**不得 `done`**，见上「未关闭项」）。分支 `agent/deepseek/TASK-034-test-layer-hardening`、worktree `G:/CODEX/New Manga.worktrees/TASK-034-deepseek`、fixed base `b34b27e`、delivery head `f83a33e`（`cff86e4` 开工文档、`f83a33e` 测试硬化与取证）。**未 push、未合并 master；未释放任何冻结 Task。** 越界发现登记（未修改）：**N-1** `src/ui/viewmodels/export/viewmodel.py:380/389`、`:392/398` 先清 `running` 后发布状态/信号（导出 flaky 机制根因，需 `src/ui/**` 范围另立切片）；**N-2** webtoon 保存 flaky 未复现、真实原因未定（三条候选）；**N-3** `inpaint.route_policy` 语义无权威声明 → AC ① 必须先裁决。待 Codex 决定：AC ① R-1～R-7 与 `src/` 三文件范围变更；`tests/providers` 111→110（守卫迁出）的口径确认。
- 历史状态（2026-09-17）：由 Codex 依 TASK-019 尾项切片 Review 的 T-2/T-4 与 STATUS 的 flaky 条目创建为 `proposed`，同日并入 TASK-035 Review 的 R-02；随后用户批准释放为 `ready`（Owner=`DeepSeek Harness`、Reviewer=`Codex`、base=`b34b27e`）。
