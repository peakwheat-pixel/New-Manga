# TASK-040 集成验证：`e1be885`

## 固定对象

| 项目 | 值 |
|---|---|
| base commit | `40d97d5`（Task 固定 base；开工 fast-forward 至 `c5aa664`；分支尾部又 merge master `84bdda7` → `004f00e`） |
| reviewed head（delivery） | `977ef65` |
| 元数据 / 分支 head | `2afabf2` / `9b9c2da`（后者为 merge 后的补充证据） |
| Review 报告 commit | `826bc90` → [`doc/reviews/TASK-040-977ef65.md`](../../doc/reviews/TASK-040-977ef65.md)（Reviewer=Codex，**非作者**；decision=`approved`） |
| integration commit | `e1be885bb3a26f962a6b1ce01a8f220949c6ab03`（merge，parents `826bc90` + `9b9c2da`） |
| 环境 | Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；`PYTHONDONTWRITEBYTECODE=1`；`-p no:cacheprovider` |

## 作者改动范围（已核）

**4 文件 `+121/−5`**：`src/infrastructure/pipeline/assembly.py`（**白名单外，R-01 已授予**）、`src/bootstrap/app.py`、`src/application/tasks/service.py`（**仅 docstring**）、`tests/core/test_bootstrap.py`（+2 例）；另有 `verification/TASK-040/**` 15 个证据文件与 Handoff。**未改 Schema/migration、依赖清单、`AGENTS.md`、其他 Task**；`src`+`tests` 空白检查 `--check` exit 0。

## 复验结果（master `e1be885`，Reviewer 独立重跑）

| # | 命令 / 方法 | 退出码 | 结果 |
|---:|---|---:|---|
| 1 | `pytest tests/core tests/pipeline tests/providers -q -rs` | 0 | **261 passed / 0 skipped** |
| 2 | `pytest -q -rs`（全仓） | 0 | **804 passed / 6 skipped**；6 条全为既有 `tests/network` 的 `openssl unavailable`。作者同口径为 `810 passed / 0 skipped`（其 shell 下 openssl 可用、6 条 network 转通过）⇒ **804+6 = 810，收集总数一致**；相对 master `84bdda7` 的 `802/6` ⇒ **+2 恰为新增 2 例** |
| 3 | **判别力**：`git archive master` 导出树 + 本分支的 `tests/core/test_bootstrap.py` | 1 | **2 failed / 14 deselected**：`test_assemble_services_injects_production_clean_probe` FAILED；`test_production_clean_probe_gates_render_only_planning` FAILED 于 `{'render': 'blocked:missing_clean_artifact'} != {'render': 'run:'}` |
| 4 | `service.py` diff 核对 | — | **仅 docstring**（判定逻辑零改动） |
| 5 | `tests/core` 删除面 | — | **零断言 / 零测试删除**；新增恰为 2 例 |
| 6 | 其他调用方影响 | — | `build_production_pipeline` 另有 2 个测试 helper 调用点（`tests/providers/test_full_chain.py:339`、`test_handlers_pipeline.py:241`）**均不传新参数** ⇒ 默认 `None`、修前装配行为不变 |
| 7 | 白盒先例 | — | 所引 `tests/core/test_bootstrap.py:259`（`..._injects_real_workbench_stack` 读 `_catalog/_store/_snapshots/_executor`）**存在** ⇒ R-02 的同风格依据成立 |

## 结论来源标注

- **独立复跑**：第 1/2/3/4/5/6/7 项（注入、接线断言、生产行为与负例、判别力、纪律核对均我自己跑出）。
- **复用作者证据**：作者 10 份逐次全仓日志（merge 前后各 5）、`pre-fix-discriminating-power.log`（我复跑了**判别力本身**及其失败点）。

## R-01：白名单偏差（`assembly.py`）——本 Review **明示授予**

`PipelineService` 的**物理构造点**在 `src/infrastructure/pipeline/assembly.py::build_production_pipeline`（`app.py:523` 只是调用方）。原白名单只列 `src/bootstrap/app.py`，白名单内注入只剩"跨模块写 `pipeline._clean_probe` 私有属性"一途——比 3 行形参透传更差。授予条件全部满足：**加法式**（新增可选参 + 透传）、**默认保持**（`None` ⇒ 既有 3 个调用点中 2 个不受影响、1 个为本切片有意接线）、**未动 seam 其他语义**（diff 仅形参/透传/docstring）、**F-12 的证据位置本身含该文件**、**作者主动声明偏差并给出回滚路径**。

**流程修正（Codex 自查）**：释放 TASK-040 时把"装配处"指认为 `src/bootstrap/app.py`，未沿到物理构造函数所在文件 ⇒ **释放方核对遗漏**。今后涉及装配/接线的切片，白名单须包含构造函数所在文件（先用 `rg "^def build_"` 定位物理装配点）。

## Findings 处置

| ID | 级别 | 内容 | 处置 |
|---|---|---|---|
| R-01 | P2（程序性） | `assembly.py` 越界（seam 函数新增可选参数） | **granted**（见上；附我方流程修正） |
| R-02 | P3 | 接线断言读私有属性 `_clean_probe`（白盒） | **accepted**：本切片禁止改 `service.py` 逻辑 ⇒ 无法加公开访问器；仓库已有同风格先例（`:259`）；建议后续加只读访问器后改为公开/行为式断言 |
| R-03 | P3 | 口径差（作者 `810/0` vs 我 `804/6`） | **accepted/记录**（总数一致、无屏蔽） |
| R-04 | P3 | 探针每次规划判定多一次只读 DB 查询 | **accepted（观察项）**（规划器本就做 DB 工作；有性能预算时再实测） |

## 集成结论

- [x] 非作者 Review 绑定固定 base/head；**Architecture 与 Verification 两面均覆盖**（口径按 2026-09-18 更新后的 §6；无并行/隔离/偏差声明义务）。
- [x] **AC ② 接线断言**（本切片核心）已实现并独立复现其判别力（修前 2 failed）——"接线漏做"从此不可能悄悄通过。
- [x] 探针**复用既有** `SqlitePageArtifactLocator.locate_current(page_id, CLEAN)`，**未新造第二套 Clean 判定**；负例（无 Clean 的兄弟页仍 `blocked`）由生产路径断言 ⇒ 未做成"永远有 Clean"。
- [x] **F-12 关闭**；TASK-040 置 `done`。
- [x] 6 条 skip 全为既有 `openssl unavailable`；未新增 skip、未放宽/删除断言；未 push；未把 `BLOCKED`/`NOT_RUN` 记为通过。
- [x] 对下游：`build_production_pipeline` 新增**可选** `clean_probe` 参数 ⇒ 其余调用点无需改动；生产 render-only 命令在**存在 current Clean** 时由 `BLOCKED` 转 `RUN`（TASK-039 修复的预期生效）。
