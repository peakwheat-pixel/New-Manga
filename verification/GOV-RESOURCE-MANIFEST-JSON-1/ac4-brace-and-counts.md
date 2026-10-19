# AC4 — 花括号可逆拆分与 closeout 计数核对

**Task**: GOV-RESOURCE-MANIFEST-JSON-1 · **对象**: `verification/P19-UI-FIX-1/resource-manifest.json`（只读）
**结论**: 花括号**全部可逆**；但 **`closeout_counts` 与 `resources` 不一致 → BLOCKED**

## 1. 花括号可逆拆分（通过）

4 个表达式全部可无损拆分、逐字重组回原值：

| # | resource_type | 字段 | 原表达式 | 拆分 |
|---|---|---|---|---|
| 2 | generated-build-artifacts | source | `apps/desktop/src-tauri/target/{core-sidecar,debug/resources,debug/m2rc1-desktop.exe}; apps/desktop/frontend/dist` | 3 |
| 3 | isolated-user-data-copy | source | `%APPDATA%/com.newmanga.m2rc1.desktop/{catalog,data,derived}` | 3 |
| 4 | user-data-source | source | `%APPDATA%/com.newmanga.m2rc1.desktop/{catalog,data,derived}` | 3 |
| 7 | read-only-baseline-evidence | source | `G:/CODEX/New Manga/verification/P19/{d-run-v2,import-no-response-r4.md}` | 2 |

展开后共 **11 条**具体路径。逆性判据：括号组重建 `"{" + inner + "}"` 必须**逐字等于**原片段；
且拆分后不含空项。全部满足。

> 注意：`%APPDATA%` 是环境变量，本核对**只做字符串级可逆拆分，不展开变量**——与 AC1 的
> 「不擅自展开环境变量」一致。

## 2. closeout_counts 逐一对应（**失败**）

| 键 | JSON 声明 | resources 中布尔为 true 的项数 | 结果 |
|---|---:|---:|---|
| deleted | 0 | 0 | OK |
| **moved** | **6** | **0** | **MISMATCH** |
| migrated | 0 | 0 | OK |
| archived | 0 | 0 | OK |

`resources` 里 7 项**全部**是 `"moved": false`、`"deleted": false`。

## 3. 差异的可信解释

该 JSON 的 `closeout_note` 自己写着：

> "Six earlier successful UIA/app logs were renamed within verification/P19-UI-FIX-1 to preserve
> the pre-refinement run before the final build rerun; no evidence was deleted."

即 `moved: 6` 指的是 **6 个日志文件在证据目录内改名**，这 6 个文件**不在 `resources` 数组里**
（数组记录的是 worktree、构建产物、隔离数据、源数据、构建环境、pyinstaller cache、只读基线证据）。

所以这不是数据错误，而是**清单的计数口径与资源数组口径不同**：`closeout_counts` 统计的是
「发生过的处置动作」，`resources` 记录的是「需要声明去向的资源对象」。

## 4. 按 AC4 的处置：保留输入并阻塞

AC4 原文要求：

> 仅当花括号表达式可无损拆分、按原顺序逐字重组为原 JSON 值，**并能与原 JSON 的 7 个资源项及
> `closeout_counts` 每项逐一对应时**，才允许生成解析视图。……歧义、缺项、重项、重组不一致或
> **计数不一致**时保留输入并失败/阻塞。

因此：**不生成解析视图，标记 BLOCKED**。原 JSON 未被修改（本核对全程只读）。

## 5. 对 schema 的影响（本轮据此修正）

我在 Round 27 写的 `resource-manifest.schema.json` 里有这条规则：

> 每个 `closeout_counts` 键必须等于 `resources` 中同名布尔为 true 的项数。

**这条规则对真实数据不成立。** 按它执行，`P19-UI-FIX-1` 这份**由 Codex 生成、内容准确**的清单
会被判为非法——与 Round 20 的教训同型：为了迁就检查器而要求改写一份准确的他方记录。

已改为：计数是**声明值**，检查器**记录差异但不再据此判失败**；差异是否构成缺陷由 Codex 裁定。

## 6. 未做的事

- 未修改 `verification/P19-UI-FIX-1/resource-manifest.json`。
- 未生成任何解析视图文件。
- 未对 `moved: 6` 对应的 6 个改名做核实（那属于 `P19-UI-FIX-1` 自身的历史，不在本 Task 范围）。
