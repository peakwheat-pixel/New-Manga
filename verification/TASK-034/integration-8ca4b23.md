# TASK-034 集成验证：`8ca4b23`（尾项切片 AC ① 第 2 步 + R-01；本 Task 至此全部 AC 完成）

## 固定对象

| 项目 | 值 |
|---|---|
| base commit | `b34b27e2bc7c1dbd4c3b15a91f08e158d966f365`（本 Task 固定 base；本切片 diff base 为已集成 `34823b9`） |
| 切片 diff base | `34823b9`（AC ②③④⑤ 的集成元数据提交） |
| reviewed head（delivery） | `002889e` |
| 元数据 / 分支 head | `132e776` |
| Review 报告 commit | `55a69de` → [`doc/reviews/TASK-034-002889e.md`](../../doc/reviews/TASK-034-002889e.md)（Reviewer=Codex，**非作者**；decision=`approved`，四轴均 `executed`、不跨轴排名） |
| 同一 commit 含 | [AC ① 裁决](TASK-034-ac1-route-policy-ruling.md) 的**勘误**（裁决方文本措辞更正） |
| implementation merge / integration commit | `8ca4b232397b182fabdfd1aa3798ff23409d85d6`（merge，parents `55a69de` + `132e776`） |
| 环境 | Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；`PYTHONDONTWRITEBYTECODE=1`；全部 `-p no:cacheprovider` |

## 复验结果（master `8ca4b23`，Reviewer 独立重跑）

| # | 命令 | 退出码 | passed | skipped | 结果 | skip 原因 |
|---:|---|---:|---:|---:|---|---|
| 1 | `…python.exe -m pytest tests/providers tests/core tests/reading_export -q -p no:cacheprovider -rs` | 0 | **217** | **0** | `217 passed` | 无 |
| 2 | `…python.exe -m pytest tests/reading_export tests/editing -q -p no:cacheprovider`（R-01 顺序 A） | 0 | **91** | **0** | `91 passed`（修复前该顺序为 2 collection errors / exit 2） | 无 |
| 3 | `…python.exe -m pytest tests/editing tests/reading_export -q -p no:cacheprovider`（R-01 顺序 B） | 0 | **91** | **0** | `91 passed` | 无 |
| 4 | `…python.exe -m pytest tests/providers/test_route_policy_settings.py tests/providers/test_handlers_pipeline.py -q` | 0 | **35** | **0** | `35 passed`（AC ① 矩阵 22 + 运行调用点 13） | 无 |
| 5 | **全仓**（见下「全仓串跑记录与一处未捕获失败」） | — | **706** | **6** | 14 次串跑中 **13 次** `706 passed, 6 skipped` / exit 0；**1 次** `1 failed, 705 passed, 6 skipped` / exit 1（用例名未捕获） | 6 条 skip 全为既有 `tests/network` 的 `openssl unavailable` |
| 6 | 决策不变性（Reviewer 独立探针，以 `b34b27e` 字面量重建旧默认） | 0 | — | — | **PASS** 彩色 webtoon / 高复杂度 = `blocked↔blocked`；线稿 / 普通 = `route:edge-bleed↔route:edge-bleed`（四组 `decision`+`route` 前后一致） | — |
| 7 | AC-INPAINT-004 正面要求 | 0 | — | — | **PASS** 显式 `color_route=brushnet` → `allowed` 含 brushnet 且无重复；候选理由由 `not in the configured route policy` 变为 `not implemented: …` | — |
| 8 | 单入口 / 无残留 | — | — | — | **PASS** `rg "_route_policy" src/` = **0**；`rg "from conftest import" tests/` = 0（仅 docstring 文本）；`handlers.py` 无遗留 `ROUTE_*`；`STEP_INPAINT`/`Mapping`/`Any` 仍在用 | — |
| 9 | 边界 | — | — | — | **PASS** 切片 17 路径；`src/` **恰为批准 3 文件**；`schema\|requirements\|pyproject\|AGENTS\|src/ui/` 命中 **0**；`rg "handlers" src/infrastructure/providers/runtime.py` = 0（无环） | — |

## 全仓串跑记录与一处未捕获失败（如实登记，不掩盖、不归因）

**现象**：集成后我在 master 上共执行**全仓串跑 14 次**：**13 次** `706 passed, 6 skipped`（exit 0）；**1 次** `1 failed, 705 passed, 6 skipped`（exit 1）——**该次的失败用例名未被捕获**（我第一次只截取了末两行）。随后 11 次连续串跑 + 2 次并发/高争用复跑（含复刻原始争用形态）**均未复现**。

**为什么不构成本切片缺陷（三条证据）**：

1. **本切片对 `tests/reading_export` 的改动是纯导入管道**：`git diff 34823b9 8ca4b23 -- tests/reading_export/` = 4 文件 `+30/−12`，其中两个测试文件**各仅改 1 行**（导入行），**断言改动 0 行**（`Select-String "^[-+].*assert"` 为空）。改动不可能放宽或改变任何断言。
2. **同族 flaky 早已登记且先于本切片**：STATUS「已知 flaky 测试（跟踪条目）」的两条（`test_qml_contract.py::test_reader_webtoon_swaps_in_vertical_viewer`、`test_viewmodels.py::test_start_export_stale_abort_surfaces_failure`）分别由 TASK-017 R-007 / TASK-019 T-1 登记，并在**多个早于本 Task 的基线**上复现过；本环境"全仓 N passed"本就不是 100% 稳定（该节首行即如此声明）。
3. **隔离复跑无失败**：`pytest tests/reading_export` 单独串跑 **15/15** exit 0（65 passed 每次）；全仓连续 11 次全绿。

**残余不确定性（不辩解）**：失败发生在**我两条工具调用并发执行**的那一批（全仓串跑与"3 条顺序命令"同时跑，约 18.6 s 重叠）——CPU 争用下的时序敏感失败是合理假设，但我**未能用并发复刻复现**（2 次并发复跑均全绿），故该假设**未获证实**；也不能从 1/14 的小样本排除"暴露度略有变化"。**结论：登记为未定性的间歇失败，不得记为通过、不得归因于本切片。**

## 集成结论

- [x] 非作者独立 Review 绑定固定 base/head，四轴（Standards / Spec / Architecture / Verification）均 `executed`、逐轴小结、**未跨轴排名**；**`code-review` 技能要求的并行双轴子代理实际派发但未取得执行槽（第三次同现象）→ 已按 §6 第 6 条兜底做两遍相互隔离检查并在报告显式声明偏差**。
- [x] **AC ① 第 2 步完成**：`RoutePolicy.from_settings(settings, *, default)` 为唯一入口（`rg "_route_policy" src/` = 0）；R-1～R-6 逐条落地且有测试锁定；R-7 正确保持冻结（有测试锁定冻结行为）。
- [x] **强制项 R-01 关闭**：十种收集顺序修复前 6 种 exit 2 / 修复后全部 exit 0；Reviewer 独立复现修复前后；全仓已无裸 `conftest` 导入。
- [x] 裁定并勘误**裁决方文本**的一处措辞失准（"四种组合均 BLOCKED" → 实为两组 BLOCKED + 两组 `RUN edge-bleed`，且**前后一致**）：实质要求"选中路线未变"四组全部成立，**不需要**任何判定算法变更（见 [`doc/reviews/TASK-034-ac1-route-policy-ruling.md`](../../doc/reviews/TASK-034-ac1-route-policy-ruling.md) 勘误节）。
- [x] 边界：切片 17 路径全在允许范围；`src/` 恰为批准的 3 文件；未改 Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、`src/ui/**`、其他 Task；**路由判定算法零改动**；未 push。
- [x] **未把任何 `BLOCKED`/`NOT_RUN` 改记为通过**：真实端点/模型端到端仍 `NOT_RUN`（与本 Task 无关）。
- [x] 全仓偶发失败已**如实登记**（见上节），未记为通过、未归因于本切片。

## Findings 处置

| ID | 级别 | 内容 | 处置 |
|---|---|---|---|
| R-01 | P3（errata） | 裁决方文本"四种组合均 BLOCKED"措辞失准（实测两组 BLOCKED + 两组 RUN 基线，**前后一致**） | **fixed**：裁决文本已加「裁决勘误」节；明确**不需要**算法变更；**不构成切片 finding** |
| R-02 | P3 | `inpaint` **段本身**非 mapping 被当作"键缺失"静默回落（两处调用点一致，非分歧面） | **open（非阻塞）** 并入 **R-07（输入校验）** 后续项 |
| R-03 | P3 | `DEFAULT_ROUTE_POLICY` 定义在 infrastructure `runtime.py` 而其类型 `RoutePolicy` 在 application（**实测无环**） | **open（P3 建议）**：后续可考虑常量随类型落在 application；本切片按裁决不动 |
| R-04 | P3 | R-01 证据（十种顺序）超出裁决要求 | **accepted** |
| R-05 / R-06 | P3 | 生产侧发布顺序（`src/ui/**` 超出范围）／webtoon flaky 未复现 | **deferred（状态不变）** |
| R-07 | P3 | 输入校验（字符串 `allowed_routes` 逐字符展开、非 bool `requirements` 强制） | **本次仍冻结 + 登记**；现已承接 R-02 一并裁决 |

## Task 收口

**AC ①（第 1 步裁决 + 第 2 步收敛）与 AC ②③④⑤⑥ 全部完成并集成** → TASK-034 置 **`done`**。本 Task 未释放或修改任何其他 Task；TASK-033 仍 `proposed`（未释放），TASK-035 保持 `done`。
