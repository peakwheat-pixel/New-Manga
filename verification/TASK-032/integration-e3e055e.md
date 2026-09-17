# TASK-032 集成验证：`e3e055e`

## 固定对象

| 项目 | 值 |
|---|---|
| base commit | `ca17d454edc03bc1b057e9e3fc463c81da652e53` |
| reviewed head（delivery） | `771977c` |
| 元数据 / 分支 head | `ff887db` |
| Review 报告 commit | `f3acd2f` → [`doc/reviews/TASK-032-771977c.md`](../../doc/reviews/TASK-032-771977c.md)（Reviewer=Codex，**非作者**；decision=`approved`） |
| implementation merge / integration commit | `e3e055e`（merge，parents `f3acd2f` + `ff887db`） |
| 环境 | Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；`PYTHONDONTWRITEBYTECODE=1` |

## 复验结果（master `e3e055e`）

| # | 命令 | 退出码 | passed | skipped | 结果 | skip 原因 |
|---:|---|---:|---:|---:|---|---|
| 1 | `…python.exe -m pytest tests/pipeline -q -p no:cacheprovider -rs` | 0 | **60** | **0** | `60 passed` | 无 |
| 2 | `…python.exe -m pytest tests/core tests/storage tests/providers -q -p no:cacheprovider -rs` | 0 | **159** | **0** | `159 passed` | 无 |
| 3 | `…python.exe -m pytest -q -p no:cacheprovider -rs`（全仓） | 0 | **671** | **6** | `671 passed, 6 skipped` | 6 项均为既有 `tests/network` 的 `openssl unavailable` |
| 4 | planner 前置生效核对 | — | — | — | `src/application/tasks/service.py:176` 存在 `if region.region_type != _SFX_REGION_TYPE`；`:402` 由 `_sfx_gate_suppresses(region)` 参与判定 | — |

## 验收结论

- [x] 非作者独立 Review 绑定固定 base/head，四轴（Standards / Spec / Architecture / Verification）均 `executed`，逐轴小结、未跨轴排名；**并行偏差已在报告显式声明**（两条双轴线程仍排队 → 按 §6 第 6 条兜底做两遍相互隔离检查）。
- [x] 集成后三条命令通过且 pass/skip 分列；6 项 skip 均为既有 `openssl unavailable`。
- [x] 判别力（Reviewer 独立复现）：修前 `src/` + 新测试 → **17 failed / 43 passed**，与作者记录一致。
- [x] 白名单：11 个路径全部在允许范围内，禁止路径 0；未改 Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、其他 Task；未 push。
- [x] R-01 已修复：`doc/handoffs/TASK-032-771977c.md` 验证表第 6 行的 `--check` 退出码由错误的 `0` 更正为实测的 `2`，并注明命中项全部来自 `verification/TASK-032/discriminative-prefix.log`（pytest 原始输出捕获的行尾填充空格；源码/测试/文档本身无空白问题）。
- [ ] **F-1 未关闭**：本 Task 只关闭**规划面**；**渲染面仍 open**（R-04，`src/application/rendering/service.py:219/238/347-351` 无 `region_type` 前置）→ 交 [TASK-035](../../doc/tasks/TASK-035.md)（proposed，未释放）。

## Findings 处置

| ID | 级别 | 内容 | 处置 |
|---|---|---|---|
| R-01 | P3 | Handoff 声称 `git diff --check` 退出码 0，实测 2 | **fixed**（更正记录，见上；不改动原始捕获日志） |
| R-02 | P2 | `tests/pipeline` 夹具 `region()` 默认仍为 `translate`（与生产默认漂移） | **deferred** → 交 TASK-035 |
| R-03 | P3 | 取值域外策略在规划阶段抛 `ValueError`（N-3） | **accepted**（fail-closed；Schema `CHECK` 已限定取值域；无需产品决策） |
| R-04 | **P1（既有，非本变更集）** | 渲染层同类缺陷：只按 `sfx_policy` 判定、无 `region_type` 前置 → 普通 `speech` Region 在真实默认 `skip` 下渲染仍被拦 | **登记为 [TASK-035](../../doc/tasks/TASK-035.md)（proposed）**；Reviewer 已实测该形先于本变更集存在（`tests/rendering` 修前/修后均 56 passed） |
| R-05 | P2 | `src/domain/tasks/models.py:182` 的 `RegionSnapshot.sfx_policy` 字段默认仍为 `"translate"` | **登记为 TASK-035** |
