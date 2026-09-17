# TASK-034 AC ① 第 1 步：`inpaint.route_policy` 设置语义裁决请求

- Task：TASK-034（测试与分层硬化）／AC ①（T-2：`route_policy` 语义唯一）
- 请求人（Owner／作者）：DeepSeek Harness ／ 裁决人：**Codex**（非作者）
- 固定 base：`b34b27e`（代码基线）；本文件提交时 `src/` **一字未改**（见 §6）
- 证据：本目录 [`route-policy-divergences.txt`](route-policy-divergences.txt)（只读探针，**调用**现有两处实现，未改行为）

> **请求裁决的事项**：`inpaint.route_policy` 设置键的规范语义。仓库内**没有**任何权威声明可作锚点（`rg "allowed_routes|color_route|brushnet" doc/` 仅命中 TASK-018 的研究/Task 与 TASK-019/034 的 Review/Task 文本；`doc/contracts/**`、D01–D08 均无该设置契约）。因此按 Task 要求：**先列全可观测分歧、提出唯一规范解释与迁移影响，交 Codex 裁决；裁决前不改 `src/`、不改变任一调用点的可观测行为。**

## 1. 现状：同一键路径，两份实现

| 项 | `src/infrastructure/providers/runtime.py:421 _route_policy(settings)` | `src/infrastructure/providers/handlers.py:617 _route_policy(self, settings)` |
|---|---|---|
| 入参 | **根 settings**（`settings["inpaint"]["route_policy"]`） | **`inpaint` 段**（调用方 `handlers.py:441-442` 先 `self._section(run.settings_snapshot, "inpaint")`） |
| 键路径（实际） | `inpaint.route_policy` | `inpaint.route_policy`（同一键） |
| 何时执行 | 装配时一次：`build_provider_runtime` → `ProviderRuntime.route_policy`（`runtime.py:414`） | 每次 Inpaint 步骤：`handle_inpaint`（`handlers.py:442`） |
| 结果去向 | `ProviderRuntime.route_policy`；`runtime.status()["route_policy"]`；并作为 `build_production_handlers(route_policy=…)` 传入 `HandlerDependencies.route_policy`（bootstrap 装配） | 该 Step 的 `RouterDecision`（`RouterFeatures` → `RoutePolicy.decide`）与 provenance |
| 兜底来源 | 模块常量 `DEFAULT_ROUTE_POLICY`（`runtime.py:73`） | `self.deps.route_policy`（`handlers.py:620/627`，生产装配时 = 上面的 `ProviderRuntime.route_policy`） |

两者默认模板本身**也不相同**（实测）：

```text
runtime DEFAULT_ROUTE_POLICY = allowed=('simple-fill','edge-bleed','brushnet') fallback=() color='brushnet' requirements={'brushnet': False, 'flux-fill': False}
HandlerDependencies default  = allowed=('simple-fill','edge-bleed')             fallback=() color=None      requirements={}
（`build_production_handlers` 的 `RoutePolicy | None = None` 缺省还另建一份
  allowed=('simple-fill','edge-bleed') color='brushnet' requirements={'brushnet': False, 'flux-fill': False}，
  见 handlers.py:732-752 —— 即**第三份**字面量）
```

## 2. 全部可观测分歧（探针实测，逐例）

`SAME` = 同一输入下两处结果完全一致；`DIVERGES` = 结果不同。完整输出见 [`route-policy-divergences.txt`](route-policy-divergences.txt)。

| # | 输入（`inpaint.route_policy` 的值） | runtime（装配） | handlers（运行） | 分歧 |
|---|---|---|---|---|
| D-1 | 键/section 缺失（`settings={}`、`inpaint={}`） | 回落 `DEFAULT_ROUTE_POLICY` | 回落 `deps.route_policy`（生产 = 同一对象） | **SAME**（仅因生产装配把同一对象传下去） |
| D-2 | 非 mapping（`"simple-fill"`、`[]`） | **静默回落** `DEFAULT_ROUTE_POLICY` | **抛** `ProviderInputError(INVALID_INPUT: inpaint.route_policy must be a mapping)` | **DIVERGES（错误 vs 静默忽略）** |
| D-3 | 空 mapping `{}` | `color='brushnet'`（`__post_init__` 自动并入 allowed） | `color=None` | **DIVERGES（color_route）** |
| D-4 | `allowed_routes=[edge-bleed]`（无 color_route） | `allowed=('edge-bleed','brushnet')`、`color='brushnet'` | `allowed=('edge-bleed',)`、`color=None` | **DIVERGES（allowed_routes + color_route）** |
| D-5 | `allowed_routes=[]` | ← 同 D-1 分支（`allowed or DEFAULT.allowed_routes`） | ← `allowed or deps.allowed_routes` | **DIVERGES（color_route；allowed 在生产装配下相同）** |
| D-6 | `color_route='flux-fill'`（无 allowed_routes） | `allowed=('flux-fill',)`（**两个基线路线被丢弃**） | `allowed=('simple-fill','edge-bleed','brushnet','flux-fill')` | **DIVERGES（allowed_routes 明显不同）** |
| D-7 | 仅 `requirements`（无 allowed/color） | `color='brushnet'` | `color=None` | **DIVERGES（color_route）** |
| D-8 | `color_route=''`（空白） | `color='brushnet'`（falsy → 默认） | `color=None` | **DIVERGES（color_route）** |
| D-9 | `requirements={'brushnet': 'false'}` | `{'brushnet': True}`（`bool("false")`） | `{'brushnet': True}` | **SAME（共有的强制转换陷阱）** |
| D-10 | `allowed_routes='simple-fill'`（字符串） | 逐字符展开 12 项 + `brushnet` | 逐字符展开 12 项 | **SAME（共有的校验缺口），color_route 仍不同** |
| D-11 | `fallback_routes` 缺失/任意 | `()` / `str()` 强制 | 同 | **SAME** |
| D-12 | `deps.route_policy` ≠ 模块常量（例如被显式注入 `allowed=('simple-fill',)`）＋ `route_policy={}` | `DEFAULT.allowed_routes` | `deps.allowed_routes` | **DIVERGES（"常量 vs 注入默认"）** |

## 3. 分歧的可观测影响面

1. **`ProviderRuntime.status()`**（`runtime.py:106-112` 的 `route_policy.__dict__`）：TASK-019 Review V11 实测为 `allowed=[brushnet, edge-bleed, simple-fill]`、`color=brushnet` —— 这是**用户/诊断可见**的配置面。
2. **Inpaint 路由决策与 provenance**：`RouterDecision.candidates[].reason` 与 `provenance.router_allowed_routes` 直接来自所选策略。当允许集合含 `brushnet` 时，彩色/复杂场景的候选理由是 `not implemented: …`；不含时是 `not in the configured route policy`。**在当前环境两条路径都 BLOCKED**（学习型路线无实现，TASK-018 R-007），因此**当前不会改变"选中哪条路线"**，只改变理由与 allowed 集合。
3. **非 mapping 输入（D-2）**：装配路径**静默忽略**用户写错的策略（应用照常启动、按默认策略执行）；运行路径**报 INVALID_INPUT**（该 Step 失败）。同一份配置在启动与执行两个时点给出不同结论。
4. **潜在的未来影响（D-6/D-4）**：`color_route` 一旦被配置而 `allowed_routes` 缺省，两条路径产出的允许集合差异最大（runtime 丢掉基线路线，handlers 保留并追加）；若将来实现 BrushNet/FLUX（TASK-033 方向），这会直接决定"彩色场景是否被允许路由到彩色路线"，以及"基线路线是否仍可用"。

## 4. 提议的唯一规范解释（请 Codex 逐条裁决）

单一入口（AC ① 第 2 步，落地时需 `src/` 范围变更）：

```python
# src/application/translation/inpaint/router.py
@classmethod
def from_settings(cls, settings: Mapping[str, Any], *, default: "RoutePolicy") -> "RoutePolicy":
    """The ONLY interpretation of the `inpaint.route_policy` setting."""
```

| 规则 | 提议（**规范**） | 现状差异 | 理由 |
|---|---|---|---|
| **R-1** 设置段/键缺失 | 返回 `default` **原样**（显式参数：装配传 `DEFAULT_ROUTE_POLICY`，运行传 `deps.route_policy`） | 现状即如此（D-1） | 两个时点的基线本就不同；**显式参数化**而非隐藏的第二条规则（符合 AC ① 第 2 步"分歧点若需保留必须显式参数化并写出理由"） |
| **R-2** `route_policy` 非 mapping | **两处一致地报错**：`ProviderInputError("inpaint.route_policy must be a mapping", stage="inpaint")`（装配期即为启动期配置错误；运行期即该 Step 失败） | runtime 静默回落（D-2） | 静默忽略用户写错的策略是**更危险**的方向（用户以为自己的限制/选择生效）；运行路径已有该错误类型与消息，可复用。**备选**：两处都回落 + 记录，但会保留"用户配置被无声丢弃" |
| **R-3** `allowed_routes` 缺失/空 | `default.allowed_routes`（运行时即 `deps.route_policy.allowed_routes`） | runtime 用模块常量（D-5/D-12） | 与 handlers 现状一致；生产装配下与常量相同（deps 就是它），仅消除"常量 vs 注入默认"这一条隐藏规则 |
| **R-4** `fallback_routes` 缺失 | `()` | 一致 | 冻结 |
| **R-5** `requirements` 缺失 | `{}`；条目值沿用 `bool(value)` 强制 | 一致（含 D-9 陷阱） | 冻结为"与现状相同"；若要在同一次裁决中收紧（拒绝非 bool），请明确，因为它同样是行为变更 |
| **R-6** `color_route` 缺失/空白 | **需裁决**：见下方 A/B 两案 | 现分歧最大（D-3/4/5/7/8/12） | 该键直接决定 allowed 集合是否含彩色路线 |

### R-6 的两个候选（请择一）

- **Option A（"跟随默认模板"）**：`color_route = raw.get("color_route") or default.color_route`。
  迁移面**最小**：只改运行路径（`None` → `"brushnet"`，因 `RoutePolicy.__post_init__` 会自动把它并入 allowed）。
  代价：`DEFAULT_ROUTE_POLICY.color_route="brushnet"` 意味着**默认就启用一条未实现的学习型路线**；一旦将来实现 BrushNet，彩色场景会在用户未显式点名时被路由到它——与 TASK-018 §6「未验证的大型模型不得设为默认」、TASK-019「不得静默降级/不可用候选明确禁用」的既有口径存在张力。
- **Option B（"默认不指定彩色路线"，**推荐**）**：`color_route = raw.get("color_route") or None`，并把 `DEFAULT_ROUTE_POLICY.color_route` 设为 `None`（`allowed_routes` 相应不再自动含 `brushnet`）。
  迁移面：装配/状态输出变化（`color=None`、allowed 去掉 `brushnet`；TASK-019 Review V11 的记录随之更新）、`build_production_handlers` 的第三份字面量同步；**运行路径行为不变**（今天就是 `None`）。AC-INPAINT-004 不受影响——D08 要求的是"按**已配置**策略选择彩色路线"，显式配置 `color_route`（或把它写进 `allowed_routes`）后即生效。
  理由：默认值应当是"未验证能力不参与"，与仓库既有 fail-closed 口径一致；用户要彩色路线时显式配置即可。

**R-7（可选，建议独立裁决）**：`allowed_routes="simple-fill"`（字符串）与 `requirements` 非 bool 值的强制转换（D-9/D-10）。建议本次**保持现状**（行为不变），另立跟进项，避免把"统一语义"扩张成"输入校验重构"。

## 5. 迁移影响（裁决后 AC ① 第 2 步将触及的 `src/` 范围变更申请）

- 允许路径外、需 Codex 批准的 3 个文件：
  1. `src/application/translation/inpaint/router.py`：新增 `RoutePolicy.from_settings(settings, *, default)`（唯一入口）。
  2. `src/infrastructure/providers/runtime.py`：删 `_route_policy`，改调 `from_settings(settings, default=DEFAULT_ROUTE_POLICY)`；若选 Option B，`DEFAULT_ROUTE_POLICY.color_route` 置 `None`。
  3. `src/infrastructure/providers/handlers.py`：删 `_route_policy` 方法，改调 `from_settings(self._section(...,'inpaint'), default=self.deps.route_policy)`；`build_production_handlers` 的第三份字面量改为复用 `DEFAULT_ROUTE_POLICY`（消除第三处重复）。
- 测试（`tests/**`，本 Task 允许路径内）：
  - 新入口的单元矩阵（本文件 §2 的 12 例 + 裁决后的期望值）；
  - "两处调用点各一条回归"：装配路径（`build_provider_runtime(settings)` → `runtime.route_policy`）与运行路径（`ProductionHandlers` 对同一 settings 的策略解析）在裁决后的唯一语义下相等（或在 R-1 显式参数处按设计不同）；
  - 若选 Option B，更新 TASK-019/TASK-032 相关断言中依赖 `DEFAULT_ROUTE_POLICY.color_route="brushnet"` 的部分（例如 `tests/providers/test_inpaint.py` 的 `RoutePolicy(... color_route=ROUTE_BRUSHNET ...)` 用例仍显式传入，不受影响；`tests/providers/test_registry_readiness.py::test_runtime_exposes_the_sakura_connection_test` 与 `runtime.status()` 断言需核对）。
- 可观测输出变化（裁决后必须记录在 Handoff）：
  - `runtime.status()["route_policy"]`：Option A 不变；**Option B 变化**（`color_route: null`、`allowed_routes` 少一项）。
  - Inpaint provenance 的 `router_allowed_routes` 与候选理由：随所选 Option 变化；**当前不会改变选中路线**（学习型路线仍无实现，两种 Option 下彩色场景均 BLOCKED）。
  - 非 mapping 配置：R-2 采纳后装配期将**报错而非静默回落**（启动期即暴露配置错误）——这是本轮唯一可能"让应用启动失败"的行为变化，请裁决时明确接受或改选备选。
- 不改：Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、其他 Task；不改变任何路由**判定算法**（`decide_route`/`acceptable_routes`/`route_gate` 均不动）。

## 6. 裁决前的行为冻结（已遵守）

- 本文件提交时 `src/` **零改动**（`git diff --name-only b34b27e..HEAD` 仅含 `doc/tasks/TASK-034.md` 与本目录的取证/请求文件）。
- §2 的 12 例分歧全部由**只读探针**得出：探针只调用现有的 `runtime._route_policy` 与 `ProductionHandlers._route_policy`，未修改、未 monkeypatch 任何生产行为。
- AC ① 第 2 步（收敛实现）**未开始**，等待 Codex 对本文件 §4 的逐条裁决（R-1～R-6 与 R-7 处置意见），以及 §5 的 `src/` 范围变更批准。

## 7. 期望的裁决输出（便于直接回填）

```text
R-1 装配/运行默认来源：认可 / 修改为 …
R-2 非 mapping：报错（两处一致）/ 回落（两处一致）/ 其他 …
R-3 allowed_routes 缺失/空：default.allowed_routes / 其他 …
R-5 requirements 缺失：{} / 其他；是否同时收紧非 bool 值（D-9）：是/否
R-6 color_route 缺失/空白：Option A（跟随默认模板） / Option B（默认 None，推荐） / 其他 …
R-7 输入校验（字符串 allowed_routes、非 bool requirements）：本次冻结 / 一并裁决
src/ 范围变更（router.py / runtime.py / handlers.py 三文件）：批准 / 调整清单
```
