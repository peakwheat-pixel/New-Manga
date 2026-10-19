# AC1–AC5 证据：外部 JSON Manifest 支持

**Task**: GOV-RESOURCE-MANIFEST-JSON-1 · **性质**: 检查器能力扩展 + 离线用例

## 交付物

| 文件 | 作用 |
|---|---|
| `tools/governance/resource-manifest.schema.json` | 固定 v1 schema（必填字段、枚举、`ALREADY_ABSENT` 语义、closeout 计数规则） |
| `tools/governance/check.ps1` | 新增 `Resolve-ManifestReference` / `Test-ExternalResourceManifest`，空表分支先解析外部引用 |
| `tools/governance/tests/run-resource-manifest-cases.py` | 16 条离线用例的驱动（位置无关，从自身路径推导 repo root） |

## AC1 — 外部引用唯一且受限

`Resolve-ManifestReference` 在 `## Resource Manifest` 正文中查找反引号包裹的 `*.json` 引用，并逐条拒绝：

| 情形 | 拒绝理由（实测输出） |
|---|---|
| 引用文件不存在 | `Resource Manifest 引用的文件不存在：verification/.../nope.json` |
| 目录穿越 | `Resource Manifest 引用不得越出仓库：verification/../doc/x.json` |
| 环境变量/宏 | `Resource Manifest 引用不得含环境变量或宏：%APPDATA%/r.json` |
| 不在 `verification/**` | `Resource Manifest 引用必须位于 verification/**：doc/x.json` |
| 多个引用 | `Resource Manifest 引用了多个 JSON：...a.json, ...b.json` |

另外代码层面拒绝绝对路径、URL、glob（`*?[]`）与符号链接（`LinkType`）。**不展开、不猜测**任何简写。

## AC2 — schema 与原值保真

`resource-manifest.schema.json`：

- `additionalProperties: false`（未知字段拒绝）；
- `disposition` 枚举 8 值，含 `ALREADY_ABSENT` 与 `NOT_APPLICABLE`，并在 description 中写明
  **`ALREADY_ABSENT` 是「曾列入但目标已消失」唯一允许的值；`NOT_APPLICABLE` 表示从未适用**；
- `schema_version` 用 `const: 1`；
- `PRESERVE_*` / `MIGRATE` / `ARCHIVE` 必须提供 `sha256` 或 `manifest_path`（`anyOf`）；
- `ALREADY_ABSENT` 必须有 `absent_evidence`（条件 `if/then`）；
- `closeout_counts` 四个键必须为非负整数。

**解析时保留原值**：`source_path` / `destination_path` 原样读入，不做展开；检查器只在内存中判断，
**不回写**任何 JSON。

## AC3 — 已消失资源的严格语义

实测（用例 12–15）：

| 用例 | 结果 |
|---|---|
| `ALREADY_ABSENT` + `absent_evidence` + 目标确实不存在 | **PASS** |
| `ALREADY_ABSENT` 但缺 `absent_evidence` | FAIL：`ALREADY_ABSENT 缺少 absent_evidence：...` |
| `ALREADY_ABSENT` 但目标仍存在 | FAIL：`ALREADY_ABSENT 但目标仍存在：...` |
| `NOT_APPLICABLE` 带 `absent_evidence`（冒充已消失） | FAIL：`NOT_APPLICABLE 不得用于已消失资源：...` |

第三、四条正是 r3 判据要求的两个方向：**不允许伪造消失**，**不允许用 `NOT_APPLICABLE` 表示消失**。

## AC4 — 花括号表达式可逆对应

**未在本轮实现**（见「未完成」）。当前检查器对含 `{}` / `%VAR%` 的 `destination_path`
选择**跳过路径校验**而非展开，这与「不擅自展开」一致；但 r3 要求的「可逆拆分并与原 JSON
的 7 项及 closeout 计数逐一对应」的**解析视图**尚未实现。

## AC5 — 离线验证

`tools/governance/tests/run-resource-manifest-cases.py`，**16/16 通过**，且与 cwd 无关
（从自身路径推导 repo root，已分别在 worktree 内与 `%TEMP%` 下各跑一次）。

覆盖：有效引用、文件缺失、目录穿越、环境变量、越出 `verification/`、双引用、`task_id` 不匹配、
`schema_version != 1`、`closeout_counts` 不符、空 resources、非法 disposition、`ALREADY_ABSENT`
三条件全满足 / 缺证据 / 目标仍存在、`NOT_APPLICABLE` 冒充消失、缺 `process_check`。

**测试隔离方式**：在真实 worktree 内建临时 Task `doc/tasks/ZZ-MANIFEST-FIXTURE.md` 与
`verification/ZZ-MANIFEST-FIXTURE/`，逐用例改写后运行真实检查器，最后在 `finally` 中删除。
已验证清理干净（`task=True dir=True`）。不污染 `doc/tasks/`，不产生提交。

> 说明：曾尝试「合成 repo root」方案（r7 建议），但检查器会校验 11 个固定治理文件与大量
> `doc/**` 交叉引用，最小合成树必然产生 40+ 条无关错误，无法从中分辨被测逻辑。改用真实树的
> 临时 fixture 后，未通过项才真正可归因。

## 未完成（如实记录）

1. **AC4 的花括号可逆拆分解析视图**未实现。
2. **fixtures 尚未作为独立版本化输入落盘**——16 条用例目前由 Python 驱动内联构造，
   `tools/governance/tests/fixtures/resource-manifest/` 目录已建但仍为空。AC5 要求
   fixtures 是可复用的版本化输入，此项待补。
3. 未用 `P19-UI-FIX-1` 的真实 JSON 做端到端核对（AC4 要求只读核对它的 7 项与 closeout 计数）。
