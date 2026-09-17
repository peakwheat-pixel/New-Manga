# TASK-019 尾项切片取证：`ab26601`（Standards S-1 / S-2）

- Task：TASK-019「集成已验证的检测/OCR/翻译/修复 Provider」尾项切片（分层修正）
- 作者（本切片）：Codex ／ Reviewer：DeepSeek Harness（**非作者**）
- 固定 base：`36242fb`（代码基线；分支起点为 `0389eb4` = 含 post-hoc Standards 附录的 master）
- 交付 head：`ab26601`；分支 `agent/deepseek/TASK-019-provider-integration`；worktree `G:/CODEX/New Manga.worktrees/TASK-019-deepseek`
- 已集成基线：TASK-019 主体 `integration_commit=3755af9`（Review `doc/reviews/TASK-019-726baf5.md` approved）——**不因本切片失效**

## 1. 动因

`doc/reviews/TASK-019-standards-addendum.md` 的 Standards 轴发现 **S-1**：`src/application/translation/inpaint/step.py` 反向依赖 `infrastructure.providers.inpaint_router` / `inpaint_routes`，违反 `doc/02_TECHNICAL_ARCHITECTURE_.md` §架构方向（`QML/UI → Application → Domain/Ports → Infrastructure Adapters`，"禁止反向依赖"），且全仓 `src/application/**` 仅此一处。S-2（同根因）：路由**策略**与适配器同住 `infrastructure/providers/`。

## 2. 修正（纯搬迁 + 导入改向，零行为变更）

| 变化 | 内容 |
|---|---|
| **新增** `src/application/translation/inpaint/route_catalog.py` | 路由**声明与门控**从 `infrastructure/providers/inpaint_routes.py` 迁入：`RouteRecord`、`ROUTE_TABLE`、`route_record`、`provider_id_for_route`、`route_gate`、`describe_routes`、`learned_routes_declared`（逐字搬迁，仅补模块 docstring） |
| **迁移** `inpaint_router.py` → `src/application/translation/inpaint/router.py` | `git mv`（保留历史），唯一内容改动是 `route_gate` 的导入目标改指 `application.translation.inpaint.route_catalog` |
| **新增** `src/application/translation/inpaint/protection.py` | 非目标像素保护**规则** `protected_pixel_violations`（TASK-018 硬规则）迁入 application；适配器侧的 `require_non_target_protection` 留在 infrastructure 并改为从 application 导入该规则（方向合法） |
| **收敛** `src/infrastructure/providers/inpaint_routes.py` | 只保留光栅实现与 provider（`simple_fill`/`edge_bleed`/`SimpleFillProvider`/`EdgeBleedProvider`/`provider_for_route`/`run_routes`）；删除已迁出的 158 行；导入其需要的规则与门控 |
| **改向** `step.py` | 三个 application 内导入替代原 infrastructure 导入 → **该文件不再 import infrastructure** |
| **改向** `handlers.py`、`runtime.py` | 策略/声明改从 application 导入（infrastructure → application，合法方向）；适配器导入不变 |
| **测试** | `test_inpaint.py`、`test_handlers_pipeline.py` 的导入路径同步；`test_ports_contract.py` **新增架构回归守卫** |

## 3. 验证（作者执行；Reviewer 需独立复跑）

环境：Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2）；`PYTHONDONTWRITEBYTECODE=1`；CWD = 分支 worktree 根。

| # | 命令 / 步骤 | 退出码 | passed | skipped | 结果 |
|---|---|---:|---:|---:|---|
| 1 | `python -m pytest tests/providers -q -p no:cacheprovider -rs` | 0 | **111** | **0** | 110 → 111（新增分层守卫），**无减少** |
| 2 | `python -m pytest tests/pipeline tests/core tests/storage -q -p no:cacheprovider -rs` | 0 | **78** | **0** | 与修正前一致 |
| 3 | `python -m pytest -q -p no:cacheprovider -rs`（全仓，共 5 次） | 0（4 次）/ 1（1 次） | **641** | **6** | 4 次 `641 passed, 6 skipped`（640 → 641，+1 守卫）；**另 1 次出现 `1 failed, 640 passed, 6 skipped`，失败用例名未被捕获**（输出被过滤）。见 §3.1 的 flaky 说明 |
| 4 | **S-1 断言**：扫描 `src/application/**` 是否 `from/import infrastructure` | — | — | — | **0 命中**（修正前：`step.py` 2 处） |
| 5 | **S-2 断言**：`rg -n "inpaint_router" src tests` | — | — | — | **0 命中**（旧模块已不存在） |
| 6 | **判别力**：`git show 726baf5:src/application/translation/inpaint/step.py \| grep "^from infrastructure"` | — | — | — | 修正前确有 `from infrastructure.providers.inpaint_router import (` 与 `from infrastructure.providers.inpaint_routes import (` → 新增守卫在旧代码上必然失败 |
| 7 | **独立装配复验**（作者自写脚本，`%TEMP%`）：`bootstrap.app.assemble_services` + `providers.status()` | 0 | — | — | 装配成功；12 个 Provider；四条学习型路线仍 `not_ready/PROVIDER_NOT_IMPLEMENTED`；GPU `unavailable` |

**skip 原因**：命令 1、2 均 `0 skipped`；命令 3 的 6 项均为 `openssl unavailable`（既有）。

### 3.1 关于那次偶发失败（如实登记）

- 现象：5 次全仓运行中有 1 次 `1 failed, 640 passed, 6 skipped`，**未捕获到用例名**；其后 4 次全绿。
- 已知同源项：`tests/reading_export/test_qml_contract.py::test_reader_webtoon_swaps_in_vertical_viewer` 是**仓库已登记的低频顺序敏感 flaky**（TASK-017/018 期间由独立 Reviewer 与 Codex 各观察过一次；见 STATUS 的 flaky 移交项）。本次单独复跑该文件 8 次**均通过**（8 passed），与该 flaky"只在全仓串跑时偶发"的特征一致。
- 与本切片的关系：本切片只改 `src/application/translation/inpaint/**`、`src/infrastructure/providers/**` 与 `tests/providers/**`，**未触碰** `tests/reading_export` 或被其覆盖的代码路径；无法证明也不主张二者有因果关系。
- 因此本切片不把该次失败记为通过，也不归因于本切片；**Reviewer 复跑时若复现，请按同一口径登记**。

## 4. 行为不变性

- 本切片为**纯搬迁 + 导入改向**：`router.py` 仅改 1 行导入；迁出代码逐字保留（`route_catalog.py`/`protection.py` 内容与迁移前一致，仅补 docstring）；`inpaint_routes.py` 只删已迁出的定义。
- 证据：全仓测试数 640 → **641**（唯一增量是新增守卫），既有 640 项全部仍通过；`tests/providers` 除 +1 外逐项不变；装配复验的 Provider 状态集合与修正前完全一致。
- 未改依赖清单、Schema、pipeline seam 本体、`AGENTS.md`、其他 Task；本切片改动全部在 TASK-019 允许路径内（`src/application/translation/inpaint/**`、`src/infrastructure/providers/**`、`tests/providers/**`、`verification/TASK-019/**`、`doc/tasks/TASK-019.md`、`doc/handoffs/TASK-019-*.md`）。
- 未 push、未合并 master。
