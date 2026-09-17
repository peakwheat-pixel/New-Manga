# TASK-019 集成验证：`9a5486a`（尾项切片 · Standards S-1/S-2 分层修正）

## 固定对象

| 项目 | 值 |
|---|---|
| base commit | `36242fb00f9f432ec66cc3c33afc167578d0f341`（代码基线） |
| 切片交付 head | `ab26601`（S-1/S-2 分层修正） |
| 元数据 head（作者） | `b03cf57` |
| Review 报告 commit | `3929d9e` → [`doc/reviews/TASK-019-ab26601.md`](../../doc/reviews/TASK-019-ab26601.md)（Reviewer=DeepSeek Harness，**非作者**；decision=`approved`，T-1～T-4 均 P2 非阻塞） |
| implementation merge / integration commit | `9a5486a`（merge，parents `0389eb4` + `3929d9e`） |
| 主体集成基线（不失效） | `integration_commit=3755af9`（Review `doc/reviews/TASK-019-726baf5.md` approved） |
| 环境 | Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；`PYTHONDONTWRITEBYTECODE=1` |

## 复验结果（master `9a5486a`）

| # | 命令 | 退出码 | passed | skipped | 结果 | skip 原因 |
|---:|---|---:|---:|---:|---|---|
| 1 | `…python.exe -m pytest tests/providers -q -p no:cacheprovider -rs` | 0 | **111** | **0** | `111 passed`（含新增分层守卫） | 无 |
| 2 | `…python.exe -m pytest tests/pipeline tests/core tests/storage -q -p no:cacheprovider -rs` | 0 | **78** | **0** | `78 passed` | 无 |
| 3 | `…python.exe -m pytest -q -p no:cacheprovider -rs`（全仓） | 0 | **641** | **6** | `641 passed, 6 skipped` | 6 项均为既有 `tests/network` 的 `openssl unavailable` |
| 4 | **S-1 断言**（master 树）：扫描 `src/application/**` 是否出现 `from/import infrastructure` | — | — | — | **0 命中** | — |
| 5 | 独立装配复验（Reviewer 与作者各跑一次，见 `doc/reviews/TASK-019-ab26601.md` V11）：`assemble_services` + `providers.status()` | 0 | — | — | 12 个 Provider；四条学习型路线 `not_ready/PROVIDER_NOT_IMPLEMENTED`；GPU `unavailable`；与切片前逐字段一致 | — |

> 命令 3 本次未复现 flaky；该 flaky 的存在与归属见 T-1（Reviewer 已用切片前树对照证明其先于本切片存在）。

## 验收结论

- [x] 非作者独立 Review 已绑定固定 base/head 并 `approved`；Reviewer 用**独立方法**（AST 扫描含动态导入、符号级逐字比对、状态集合对照、修前/修后双向判别力）证实修复真实且零行为变更，未依赖作者自述。
- [x] 集成后三条命令通过且 pass/skip 分列；6 项 skip 均为既有 `openssl unavailable`。
- [x] `application → infrastructure` 依赖在 master 上为 **0**（S-1 消除），并有回归守卫（`tests/providers/test_ports_contract.py::test_application_layer_never_imports_infrastructure`）。
- [x] 未改依赖清单 / Schema / pipeline seam 本体 / `AGENTS.md` / 其他 Task；未 push；**未把任何 `BLOCKED`/`NOT_RUN` 项改记为通过**。
- [ ] AC-RFULL-001 完整链、真实模型质量/成本/时延、真实 Sakura 服务验证：状态不变，仍 `BLOCKED`/`NOT_RUN`。

## Findings 处置（T-1～T-4）

| ID | 级别 | 内容 | 处置 |
|---|---|---|---|
| T-1 | P2 | `tests/reading_export` 存在**低频顺序/时序敏感 flaky**，且**既有登记范围不完整**：原登记仅含 `test_qml_contract.py::test_reader_webtoon_swaps_in_vertical_viewer`（TASK-017 R-007），Reviewer 另观察到 `test_viewmodels.py::test_start_export_stale_abort_surfaces_failure`，并用切片前树（`3755af9`）对照证明其**先于本切片存在** | **已登记**：`doc/STATUS.md` 新增「已知 flaky 测试（跟踪条目）」章节，收录两个用例 id、证据与状态；不在本切片修复（测试基础设施，属后续维护 Task） |
| T-2 | P2 | `runtime.py::_route_policy` 与 `handlers.py::_route_policy` 重复解析同一设置契约，默认值/错误行为不一致（判断项，Duplicated Code） | **deferred**：建议在 `application/translation/inpaint/router.py` 提供单一 `RoutePolicy.from_settings(...)`，两处调用；属代码改动，需另开切片并走非作者 Review，**不阻塞本次集成** |
| T-3 | P2 | 取证文本与最终树不一致：`author-verification.md` 仍把 route 表/Router 记为 infrastructure 所在地；`changed-paths.txt` 是 `6c981c2` 快照；"删除 158 行"是合并 diff 规模 | **已处理（见下）**——`changed-paths.txt` 加快照/迁移说明；"158 行"改写为逐文件 `−149/+9`；`author-verification.md` 保持原样（作者快照），更正集中登记在本表与 [Standards 附录](../../doc/reviews/TASK-019-standards-addendum.md) |
| T-4 | P2 | 分层守卫是行前缀扫描，不含 `importlib.import_module("infrastructure…")` 动态形式；位置在 `tests/providers/` 是受白名单约束的正确选择 | **deferred**：待 `tests/core/` 进入可改范围时迁入并用 AST 版实现；当前实测动态导入 0 处，无现实缺口 |

### T-3 更正表（口径以本表为准）

| 位置 | 原文（快照口径） | 更正 |
|---|---|---|
| `verification/TASK-019/author-verification.md:26` | `src/infrastructure/providers/inpaint_routes.py` / `inpaint_router.py` ＝ route 表 + Router 决策所在地 | 现为：route **声明/门控** → `src/application/translation/inpaint/route_catalog.py`；Router **策略** → `src/application/translation/inpaint/router.py`；`inpaint_routes.py` 只留光栅实现与 provider（迁移 commit `ab26601`） |
| `verification/TASK-019/changed-paths.txt` | `6c981c2` 时刻的路径快照（含 `src/infrastructure/providers/inpaint_router.py`） | 该路径由 `git mv` 迁至 `src/application/translation/inpaint/router.py`；文件头已加说明 |
| `doc/handoffs/TASK-019-ab26601.md`、`verification/TASK-019/layering-fix-ab26601.md` | "删除已迁出的 158 行" | 逐文件实际为 `inpaint_routes.py −149/+9`（净 −140）；"158" 为合并 diff 规模，已按此更正 |
