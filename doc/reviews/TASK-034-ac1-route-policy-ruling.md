---
task_id: TASK-034
kind: ac1-adjudication
author_of_request: DeepSeek Harness
adjudicator: Codex（非作者）
base_commit: b34b27e2bc7c1dbd4c3b15a91f08e158d966f365
request_artifact: verification/TASK-034/route-policy-decision-request.md（提交时 src/ 零改动）
decision: ruled
---

# TASK-034 AC ① 裁决：`inpaint.route_policy` 规范语义（R-1～R-7 + `src/` 范围变更）

裁决依据：请求文件 [verification/TASK-034/route-policy-decision-request.md](../../verification/TASK-034/route-policy-decision-request.md)（作者只读探针 12 例）、D08 AC-INPAINT-004、[doc/research/TASK-018.md](../research/TASK-018.md) §6、`RoutePolicy` 自身默认值（我实测），以及仓库既有 fail-closed 口径。

## 裁决前的独立核对（Codex 实测，非作者自述）

| 核对项 | 结果 |
|---|---|
| `src/` 是否真的一字未改 | **是**：`git diff --name-only b34b27e 8ca99d4 -- src/` 为空 |
| 两处解析是否真读同一键 | **是**：`runtime.py:421` 读根 `settings["inpaint"]["route_policy"]`；`handlers.py:617` 的调用方 `handlers.py:441` 先做 `self._section(run.settings_snapshot, "inpaint")` → 同为 `inpaint.route_policy` |
| `RoutePolicy` 自身默认值 | `router.py:291-294` = `allowed=("simple-fill","edge-bleed")`、`fallback=()`、`color_route=None`、`requirements={}` —— **即 `runtime.DEFAULT_ROUTE_POLICY` 才是那个偏离者**，不是 handlers |
| 第三份字面量是否仍在 | **是**：`handlers.py:732-752` 的 `build_production_handlers(route_policy: RoutePolicy \| None = None)` 另建一份 |
| 默认策略是否含未验证模型 | **是**：`runtime.py:73-78` 的 `color_route="brushnet"`、`allowed` 含 `brushnet` |
| `src/ui/**` 是否有写入路径 | **无**：`rg "route_policy" src/ui/` 0 命中 → 用户只能靠设置文件显式配置 |

## 逐条裁决

| 规则 | 裁决 | 说明 |
|---|---|---|
| **R-1** 设置段/键缺失 | **认可** | 返回调用方显式传入的 `default`：装配传 `DEFAULT_ROUTE_POLICY`、运行传 `deps.route_policy`。这是**唯一**被允许的"两处不同"，必须写成显式参数并附理由注释，不得退化为隐藏分支 |
| **R-2** `route_policy` 非 mapping | **认可（两处一致报错）** | 由共享解析器抛 `ProviderInputError("inpaint.route_policy must be a mapping", stage="inpaint")`。理由：静默忽略用户写错的策略 = 用户以为限制生效而实际未生效（与 F-1 同类"静默 no-op"反模式）；且规划层取值域外已是 fail-closed（TASK-032 R-03 已 accepted）。**必须**在 Handoff 与 STATUS 明确记录：装配路径由"静默回落"变为"启动期即报配置错误"——这是本轮唯一会让应用启动失败的语义变化，用户需要知道 |
| **R-3** `allowed_routes` 缺失/为空 | **认可** | 取 `default.allowed_routes`。生产装配下 `default` 就是 `DEFAULT_ROUTE_POLICY`，故与现状等价，只是消除了"常量 vs 注入默认"这条隐藏规则 |
| **R-4** `fallback_routes` 缺失 | **冻结为 `()`** | 两侧现状一致，无分歧 |
| **R-5** `requirements` 缺失 | **冻结**：缺省 → `{}`；条目值沿用 `bool(value)`。**本轮不收紧**非 bool 值（与 R-7 一并另立） | 收紧会引入新的行为变更，超出"统一语义"的范围 |
| **R-6** `color_route` 缺省/空白 | **采纳 Option B，并加重对齐要求**（详见下节） | 这是本次裁决的核心 |
| **R-7** 输入校验（`allowed_routes` 为字符串时逐字符展开；`requirements` 非 bool 强制转换） | **本次冻结 + 登记为后续项** | 建议由未来的"设置输入校验"切片统一处理（含拒绝非 bool、拒绝非序列字符串）。**不**在本 Task 内扩张；登记在 [TASK-034](../tasks/TASK-034.md) 与 [STATUS](../STATUS.md) |

### R-6 裁决：Option B，并要求 `DEFAULT_ROUTE_POLICY` 与证据对齐

**采纳 Option B**：`color_route = raw.get("color_route") or None`（缺省/空白 → 不指定彩色路线），并同步把默认策略对齐。四条依据：

1. **`RoutePolicy` 自身默认已是 Option B**（`router.py:291-294`）。也就是说 Option B 不是新发明，而是让 `runtime.DEFAULT_ROUTE_POLICY` 回到它自己类型的默认——属于**收敛**，符合本 Task 的"纯硬化"定位。
2. **与 TASK-018 的实测结论直接冲突**：[doc/research/TASK-018.md](../research/TASK-018.md) §6「未验证的大型模型不得设为默认：`flux`、`brushnet-powerpaint` … 只能是候选」，且 §5「`default_eligible` 仅 `simple-fill` 与 `edge-bleed` 为 `True`；四条学习型路线全部为 `False`」。把 `brushnet` 放进**默认** `allowed_routes` 并指定为默认彩色路线，等于把 `default_eligible=false` 的路线写成默认，与该已集成结论不符。
3. **D08 AC-INPAINT-004 的原文是"按已配置策略选择彩色修复能力"**——默认不指定即"未配置"，用户要彩色路线就显式配置（`color_route` 或写进 `allowed_routes`）。Option B 正好落在该措辞上。
4. **无 UI 写入路径**（`rg "route_policy" src/ui/` = 0）：默认值不会被用户在界面上无意覆盖，因此默认值本身就是产品表达——它必须表达"未验证能力不参与"。

**加重对齐要求（Option B 的精确形态）**：`DEFAULT_ROUTE_POLICY` 必须改为与 `RoutePolicy` 默认**及** TASK-018 已记录的 `default_eligible` 集合完全一致：

```text
allowed_routes   = ("simple-fill", "edge-bleed")   # = default_eligible=True 的两条非模型基线
fallback_routes  = ()
color_route      = None                            # 不再默认指定未验证的学习型路线
requirements     = {}                              # 无默认启用项，故无需求条目
```

并据此把 `handlers.py:732-752` 的**第三份字面量**改为复用该常量（消除第三处重复）。

**必须记录的可观测变化（裁决后写进 Handoff）**：

- `runtime.status()["route_policy"]`：`allowed_routes` 去掉 `brushnet`、`color_route` 由 `"brushnet"` 变 `null`（TASK-019 Review V11 记录的值随之更新——这是**记录刷新**，不是回归）。
- Inpaint provenance 的 `router_allowed_routes` 与彩色/复杂场景的候选理由：由 `not implemented: …` 变为 `not in the configured route policy`。
- **必须提供证据证明"选中哪条路线"未变**：四种特征组合（彩色 webtoon / 高复杂度 / 线稿 / 普通）在裁决前后**均 `BLOCKED`**（学习型路线无实现），故本次只改变"理由与 allowed 集合"，不改变决策结果。若任一组合出现决策变化，必须停下来回报，不得自行接受。
- 显式配置 `color_route`（或把它写进 `allowed_routes`）后仍须生效——这是 AC-INPAINT-004 的正面要求，需有测试锁定。

## `src/` 范围变更：批准（限定 3 文件）

批准请求 §5 的 3 个文件，**并限定改动内容**：

| 文件 | 允许的改动 |
|---|---|
| `src/application/translation/inpaint/router.py` | 新增 `RoutePolicy.from_settings(settings, *, default)`（唯一入口，含 R-2 的报错语义） |
| `src/infrastructure/providers/runtime.py` | 删除 `_route_policy`，改调 `from_settings(...)`；按上节对齐 `DEFAULT_ROUTE_POLICY` |
| `src/infrastructure/providers/handlers.py` | 删除 `_route_policy` 方法，改调 `from_settings(...)`；`build_production_handlers` 的第三份字面量改为复用共享常量 |

**不得**：改动路由**判定算法**（`decide_route` / `acceptable_routes` / `preferred_route_order` / `route_gate` / `RouterFeatures`）、Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、其他 Task，或 `tests/**` 之外的任何路径。`tests/**` 依 TASK-034 既有允许范围。

## 本裁决附带的强制项（AC ① 第 2 步切片的验收点）

1. 上一节的 3 文件收敛 + 测试矩阵（请求 §5 列表），且**两处调用点各一条回归**；R-2 与 Option B 的可观测变化各有测试锁定。
2. **强制纳入 [R-01](TASK-034-f83a33e.md)**：`tests/reading_export` 仍存在与 AC ④ 同类、同一根因的裸 `conftest` 导入（`test_qml_contract.py:12`、`test_viewmodels.py:13` → `from conftest import requires_pyside6`），可复现 2 个 collection errors。第 2 步切片**必须**一并消除，并按 R-01 要求给出两种参数顺序 + 一个伙伴目录顺序的证据。
3. R-7 保持登记状态，不在该切片内扩张。

## 边界声明

本裁决只决定"唯一解释是什么"，不含实现；`src/` 在收到本裁决前保持冻结（作者已遵守）。裁决不改变任何 AC 的 PASS/BLOCKED 记录：AC ① 在此之前一直是 **BLOCKED（第 2 步未开始）**，本裁决只解除"必须先裁决"这一前置，AC ① 仍未完成。

---

## 裁决勘误（2026-09-17，Codex 自查 + 作者要求裁定）

**勘误对象**：本文「R-6 裁决」小节中"必须记录的可观测变化"的第 3 条，原文写：

> 四种特征组合（彩色 webtoon / 高复杂度 / 线稿 / 普通）在裁决前后**均 `BLOCKED`**（学习型路线无实现），故本次只改变"理由与 allowed 集合"，不改变决策结果。

**该括注有误**。实测：只有**彩色 webtoon** 与**高复杂度**两组为 `BLOCKED`；**线稿**与**普通**两组在裁决前后**都选中依赖无关基线 `edge-bleed`**（即 `RUN`，非 `BLOCKED`）。原因：`preferred_route_order` 末尾固定追加 `ROUTE_EDGE_BLEED` 作为 "dependency-free structural last resort"，而 `acceptable_routes` 对非彩色/非高复杂度场景包含该基线 —— 这条路径与 `allowed_routes` 是否含学习型路线无关。

**裁定**：

1. **实质要求不受影响**。该条真正要求的是"**选中哪条路线**未变"，四组全部成立（`decision` 与 `route` 逐项相同；只有 `brushnet` 的理由由 `not implemented: …` 变为 `not in the configured route policy`）。作者按实测登记**正确**，其"不自行接受、请裁决方裁定"的处理方式**正确**。
2. **不需要任何判定算法变更**。作者在 Handoff 中提出"若裁决方认为线稿/普通也必须 BLOCKED，则属判定算法变更、需另立裁决"——**本裁决方明确不需要**：原文那句话是**措辞失准**，不是对算法提出新要求。`decide_route` / `acceptable_routes` / `preferred_route_order` / `route_gate` / `RouterFeatures` 保持禁止改动。
3. **失败的是本裁决文本，不是切片**。本条不构成切片 finding；作者以参数化测试（`test_ruled_default_does_not_change_which_route_is_chosen`）把四组的 `decision`+`route` 不变性锁定，正是正确的处置。

**教训登记**：裁决文本中的**具体数字/枚举括注**应与可执行证据同等对待 — 本次由作者实测发现并回抛，避免了把一句顺口括注当成规格。
