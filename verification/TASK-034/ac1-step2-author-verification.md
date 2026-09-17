# TASK-034 尾项切片取证：AC ① 第 2 步 + R-01（`002889e`）

- Task：TASK-034「测试与分层硬化」尾项切片（AC ① 第 2 步：`inpaint.route_policy` 收敛；强制项 R-01）
- Owner／作者：DeepSeek Harness ／ Reviewer：Codex（**非作者**）
- 固定 base：`b34b27e`；分支起点 `34823b9`（= master，已集成 AC ②③④⑤：集成 `b6051e5`、元数据 `34823b9`）
- 交付 head：`002889e`（先 `git merge master` 快进到 `34823b9`，再实施）
- 裁决依据：[`doc/reviews/TASK-034-ac1-route-policy-ruling.md`](../../doc/reviews/TASK-034-ac1-route-policy-ruling.md)（R-1～R-7 + 3 文件 `src/` 范围批准）与 [R-01 Review](../../doc/reviews/TASK-034-f83a33e.md)

## 1. 实施（3 个已批准的 `src/` 文件 + 测试）

| 文件 | 改动 |
|---|---|
| `src/application/translation/inpaint/router.py` | **新增唯一入口** `RoutePolicy.from_settings(settings, *, default)`：R-1 段/键缺失 → 返回 `default`（显式参数）；R-2 取值存在但非 mapping → `ProviderInputError("inpaint.route_policy must be a mapping", stage="inpaint")`；R-3 `allowed_routes` 缺失/空 → `default.allowed_routes`；R-4 `fallback_routes` → `()`；R-5 `requirements` → `{}`（保留 `bool(value)` 强制）；R-6 Option B：`color_route` 缺失/空白 → `None`，显式指定仍生效并由 `__post_init__` 并入 `allowed_routes` |
| `src/infrastructure/providers/runtime.py` | 删除私有 `_route_policy`；装配改调 `RoutePolicy.from_settings(settings, default=DEFAULT_ROUTE_POLICY)`；`DEFAULT_ROUTE_POLICY` 按裁决对齐：`allowed=("simple-fill","edge-bleed")`、`fallback=()`、`color_route=None`、`requirements={}`（与 `RoutePolicy` 自身默认 + TASK-018 `default_eligible` 集合一致） |
| `src/infrastructure/providers/handlers.py` | 删除私有 `_route_policy` 方法；`handle_inpaint` 改调 `RoutePolicy.from_settings(run.settings_snapshot, default=self.deps.route_policy)`（**输入形状统一为 root settings**，与装配路径同形）；`build_production_handlers` 的**第三份字面量**改为复用 `DEFAULT_ROUTE_POLICY`（runtime 不 import handlers，无环） |

**未改动**（裁决禁止项，已复核）：路由判定算法（`decide_route`/`acceptable_routes`/`preferred_route_order`/`route_gate`/`RouterFeatures`）、Schema/migration、依赖清单、seam 本体、`AGENTS.md`、`src/ui/**`、其他 Task。`src/` 改动**恰好 3 个文件**（`git diff --name-only 34823b9..HEAD -- src` 只列这 3 个）。

## 2. AC ① 测试矩阵（裁决后的 12 类输入 + 调用点回归）

新增 `tests/providers/test_route_policy_settings.py`（22 例）：请求文件 §2 的 12 类输入逐条锁定。

| # | 输入（`inpaint.route_policy`） | 裁决后语义 | 用例 |
|---|---|---|---|
| 1 | 段/键缺失（`settings={}`、`{"inpaint": {}}`） | 返回传入的 `default`（**同一对象**） | `test_missing_section_or_key_returns_the_explicit_default` |
| 1b | `inpaint` 段本身非 mapping | 视同缺失 → `default` | 同上 |
| 1c | 两处调用点只有 `default` 不同 | 显式参数：`custom` 原样返回、`allowed_routes=[]` 回落到 `custom.allowed_routes` | `test_the_default_parameter_is_what_distinguishes_the_two_call_sites` |
| 2 | 非 mapping（`"simple-fill"`/`[]`/`42`/tuple） | **两处一致抛** `ProviderInputError`（`INVALID_INPUT`，消息含 `must be a mapping`） | `test_non_mapping_route_policy_raises_the_same_typed_error` |
| 2b | 装配路径同上 | `build_provider_runtime` 直接抛（不再静默回落） | `test_runtime_assembly_reports_a_malformed_policy_instead_of_ignoring_it` |
| 3 | `{}`（空 mapping） | `default.allowed_routes` / `()` / `None` / `{}` | `test_empty_mapping_uses_the_default_template` |
| 4 | `allowed_routes=[edge-bleed]`、`[]` | 非空即采用；空 → `default.allowed_routes` | `test_allowed_routes_missing_or_empty_falls_back_to_the_default` |
| 5 | `color_route=flux-fill`（无 allowed） | 显式生效：`color=flux-fill` 且并入 allowed（**基线保留**）；已在 allowed 时不重复 | `test_explicit_color_route_is_honoured_and_added_to_allowed_routes` |
| 6 | `color_route=""` / `None` | Option B：`None`，且 `brushnet` 不在 allowed | `test_blank_color_route_means_no_color_route_configured` |
| 7 | 仅 `requirements`；`fallback_routes` 缺失 | `requirements` 保留、`fallback=()`；`bool("false")→True` 保持（R-5/R-7 冻结） | `test_fallback_routes_and_requirements_defaults_are_frozen` |
| 8 | `allowed_routes="simple-fill"`（字符串） | 保持逐字符展开（R-7 冻结，本次不收紧） | `test_allowed_routes_as_string_keeps_the_frozen_char_expansion` |
| 9 | 默认策略本身 | `DEFAULT_ROUTE_POLICY == RoutePolicy()`，allowed=两条基线、color=None、requirements={} | `test_default_policy_matches_the_type_default_and_the_eligible_set` |
| 10 | **装配调用点回归** | 4 组输入下 `runtime.route_policy == from_settings(..., default=DEFAULT)`；`status()["route_policy"]` 为 Option B 值 | `test_runtime_call_site_uses_the_shared_parser` |
| 11 | **运行调用点回归**（真实 SQLite + seam） | Run 级 `allowed_routes=[edge-bleed]` 被逐字采用：`step.output["route"] == edge-bleed`、`provenance["router_allowed_routes"] == ["edge-bleed"]`、`router_color_route_selected is False` | `test_handlers_pipeline.py::test_run_settings_route_policy_goes_through_the_shared_parser` |
| 12 | **运行调用点 R-2** | Run 级策略非 mapping → 该 Step `FAILED` / `INVALID_INPUT`，且未写出 clean artifact | `test_handlers_pipeline.py::test_run_settings_malformed_route_policy_fails_the_step_loudly` |
| 13 | 显式配置彩色路线后路由可用 | 配置的 `brushnet` 被策略接受（候选理由不是 "not in the configured route policy"），仍因无实现而 BLOCKED（TASK-018 R-007） | `test_configured_policy_is_reported_and_used_by_the_router` |

## 3. Option B 与 R-2 的可观测变化（必须记录）

**证据文件**：[`ac1-decision-invariance.txt`](ac1-decision-invariance.txt)（只读探针；裁决前的 `DEFAULT_ROUTE_POLICY` 在探针内按 `b34b27e` 的字面量重建，因为它已从 `src/` 移除）。

1. **`runtime.status()["route_policy"]`**：
   - 裁决前（历史值，TASK-019 Review V11）：`allowed=[brushnet, edge-bleed, simple-fill]`、`color_route="brushnet"`、`requirements={"brushnet": False, "flux-fill": False}`；
   - 裁决后（实测）：`allowed=('simple-fill','edge-bleed')`、`color_route=None`、`requirements={}`。
   这是**记录刷新**（Option B 的预期结果），已由 `test_runtime_call_site_uses_the_shared_parser` 锁定。
2. **彩色/复杂场景的候选理由**：`brushnet` 由 `not implemented: no learned runtime/weights in this build` 变为 `not in the configured route policy`；其余候选（`flux-fill`/`aot-gan`/`manga-lama`）理由不变；`edge-bleed` 仍为 `not acceptable for a colored/complex scene`。已由 `test_ruled_default_only_changes_the_reason_and_the_allowed_set` 锁定。
3. **R-2（装配路径由"静默回落"变为"启动期报配置错误"）**：这是本轮唯一可能让应用启动失败的语义变化，已在 Handoff 显式登记（裁决第 R-2 行要求），并由 `test_runtime_assembly_reports_a_malformed_policy_instead_of_ignoring_it` + 运行路径回归锁定。

### 四种特征组合的决策不变性（实测，含一处与裁决措辞的差异）

| 特征组合 | 裁决前（`b34b27e` 默认） | 裁决后（Option B 默认） | 决策是否变化 |
|---|---|---|---|
| 彩色 webtoon（0.2 / color / high） | **BLOCKED**（route=None） | **BLOCKED**（route=None） | 未变 |
| 高复杂度背景（0.4 / high） | **BLOCKED**（route=None） | **BLOCKED**（route=None） | 未变 |
| 线稿（0.4 / lineart） | **RUN → `edge-bleed`** | **RUN → `edge-bleed`** | 未变 |
| 普通区域（0.4 / speech bubble） | **RUN → `edge-bleed`** | **RUN → `edge-bleed`** | 未变 |

**与裁决措辞的差异（如实登记，不自行接受、不粉饰）**：裁决第 62 行写"四种特征组合…在裁决前后**均 `BLOCKED`**"。实测只有**彩色 webtoon** 与**高复杂度**两组为 BLOCKED；**线稿**与**普通**两组在两侧都选择依赖无关基线 `edge-bleed`（因此是 RUN，不是 BLOCKED）。**实质要求（"选中哪条路线"未变）对四组全部成立**，四组 `decision` 与 `route` 均逐项相同；差异仅存在于裁决的**措辞**层面。已由 `test_ruled_default_does_not_change_which_route_is_chosen`（四组参数化）与 `test_ruled_default_only_changes_the_reason_and_the_allowed_set` 锁定，请 Reviewer 按此口径核对；若裁决方认为"线稿/普通也必须 BLOCKED"，那将是**判定算法**层面的变更（本切片明确禁止改动），需另立裁决。

## 4. R-01（强制项）：`tests/reading_export` 裸 `conftest` 导入

- **改动**：`requires_pyside6` 与 `_pyside6_available` 移入**唯一命名**的 `tests/reading_export/reading_export_helpers.py`；`test_qml_contract.py` 与 `test_viewmodels.py` 改为 `from reading_export_helpers import requires_pyside6`（与既有的 `make_pages`/`make_service` 等同一导入块）；`conftest.py` 只保留 `qapp` fixture 并从 helper 导入探针。
- **全仓已无裸 conftest 导入**：`grep '^from conftest import|^import conftest' tests/**` → 0 命中。
- **两种参数顺序 + 伙伴目录顺序对照**（[`r01-collection-orders-before.log`](r01-collection-orders-before.log) / [`r01-collection-orders-after.log`](r01-collection-orders-after.log)）：

| # | 命令（`-q -p no:cacheprovider`） | 修复前 | 修复后 |
|---|---|---|---|
| 1 | `pytest tests/reading_export/test_qml_contract.py tests/reading_export/test_viewmodels.py` | exit 0（22 passed） | exit 0（22 passed） |
| 2 | `pytest tests/reading_export/test_viewmodels.py tests/reading_export/test_qml_contract.py`（反向参数顺序） | exit 0（22 passed） | exit 0（22 passed） |
| 3 | `pytest tests/reading_export tests/editing`（伙伴目录在前） | **exit 2 / 2 collection errors** | **exit 0（91 passed）** |
| 4 | `pytest tests/editing tests/reading_export`（反向） | exit 0（91 passed） | exit 0（91 passed） |
| 5 | `pytest tests/reading_export tests/workbench` | **exit 2 / 2 errors** | exit 0（116 passed） |
| 6 | `pytest tests/reading_export tests/rendering` | **exit 2 / 2 errors** | exit 0（128 passed） |
| 7 | `pytest tests/reading_export tests/providers` | **exit 2 / 2 errors** | exit 0（199 passed） |
| 8 | `pytest tests/reading_export tests/knowledge` | **exit 2 / 2 errors** | exit 0（143 passed） |
| 9 | `pytest tests/reading_export tests/library` | **exit 2 / 2 errors** | exit 0（105 passed） |
| 10 | `pytest tests/reading_export`（单独） | exit 0（65 passed） | exit 0（65 passed） |

（修复前的报错为 `ImportError: cannot import name 'requires_pyside6' from 'conftest'`，指向别的目录的 conftest；与 Review R-01 记录的六种伙伴目录全部 exit 2 一致。）

## 5. 回归与分列

| 套件 | 本切片前（`34823b9`） | 本切片后（`002889e`） | 说明 |
|---|---|---|---|
| `tests/providers` | 110 passed | **134 passed** | +24：AC ① 矩阵 22 + 运行调用点回归 2 |
| `tests/core` | 18 passed | 18 passed | 不变 |
| `tests/reading_export` | 65 passed | 65 passed | R-01 为导入重构，无新增/删除用例 |
| mandated 三套件 | 193 passed / 0 skipped | **217 passed / 0 skipped** | 全绿、**0 skip** |
| 全仓 | 682 passed / 6 skipped | **706 passed / 6 skipped** | 3 次串跑一致（[`ac1-step2-full-suite.log`](ac1-step2-full-suite.log) 另含第 4 次带 skip 明细） |

**全仓逐次记录**（`python -m pytest -q -p no:cacheprovider -rs`）：

| # | 退出码 | passed | skipped | 失败 |
|---|---:|---:|---:|---|
| 1 | 0 | 706 | 6 | 无 |
| 2 | 0 | 706 | 6 | 无 |
| 3 | 0 | 706 | 6 | 无 |
| 4（带 `-rs` 明细） | 0 | 706 | 6 | 无 |

**skip 明细（每一轮相同，6 条全为既有环境 skip）**：`tests/network/test_connection_tester.py:106`、`test_transport_tls.py:39`、`:47`、`:62`、`:69`、`:83`，原因均为 `openssl unavailable`。**本切片未新增任何 skip、未放宽任何断言。**

**其他套件回归**：`tests/editing`+`tests/storage`+`tests/pipeline` = 120 passed（[`ac1-step2-counts.txt`](ac1-step2-counts.txt) 记录逐目录前后对照）。

## 6. 边界与合规

- 改动路径：3 个已批准的 `src/` 文件 + `tests/**` + `verification/TASK-034/**`（`git diff --name-only 34823b9..HEAD`）；越界 0；`git diff --check` 退出码 0。
- **未改动**：路由判定算法、Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、`src/ui/**`、其他 Task、R-05（生产侧发布顺序）/R-06/R-07 相关项（R-07 输入校验保持冻结登记）。
- 未 push、未合并 master（仅把 master 快进合入本分支）、未释放任何冻结 Task。
