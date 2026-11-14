# SETTINGS-ERROR-STATE-1 证据

卡面：`doc/tasks/SETTINGS-ERROR-STATE-1.md`。基线 `418801499`。

## 1. 开卡前的实现核实（按纪律先核实现）

矩阵 `MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md` §3 当时把「错误态 / 设置」标为**唯一完全无覆盖**格。
核实现后结论是：**实现早已存在，缺的只是测试**。

| 层 | 既有实现 | 位置 |
|---|---|---|
| VM | `LoadAsync` try/catch → `State = FluentPageState.Error`、`Error = "设置读取失败（{类型}），可以重试。"` | `SettingsViewModel.cs:139-171` |
| View | `State == Error` → `_stateHost.Child = FluentUi.Banner(StatusKind.Failed, "设置错误", Error, "重试", …)` | `SettingsPageView.cs:690/698-701` |

⇒ 本卡**零生产代码改动**，只补判别测试并改判矩阵。

## 2. 改动

| 位置 | 改动 |
|---|---|
| 新增 `apps/desktop-avalonia/tests/NewManga.App.Tests/SettingsErrorStateTests.cs` | 3 个测试：AC1 VM 级、AC2 视图级、以及一个**对照测试**（健康加载不得出现"设置错误"banner，防止 AC2 因错误而假通过） |
| `FakeHostController.cs` | 新增 `SettingsLoadFailure` 开关（设置列举方法按需抛异常）——**测试替身扩展，非生产代码** |
| `doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md` | §3「错误态 / 设置」由 ❌ 改 ✅（带测试名 + 文件:行）；§5 结论由"唯一无覆盖 1 格"改为"**0 格**" |
| `doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md` §15 | 同步（GUI 层 13/13 有覆盖、无覆盖格清零） |

## 3. 测试与判别力

| 项 | 结果 |
|---|---|
| 定向 | `SettingsErrorStateTests` **3 passed** |
| **AC3 判别力实测** | 把 `LoadAsync` 的 catch 临时改为吞异常（`Status = "PROBE swallowed " + ex.GetType().Name`）后重跑 → **2 failed / 1 passed**；失败信息 `Expected: Error / Actual: Loading`；对照测试 `HealthyLoad_DoesNotShowTheErrorBanner` **正确保持绿**（它不依赖失败态）。随后 `git checkout -- <file>` 还原，`git diff --stat -- apps/desktop-avalonia/src` 归零，再跑回 3 passed |
| 全量 | `App.Tests` **950 / 0 / 11 / 961**（本卡前 947/0/11/958；**skip 未增加**） |
| 零生产改动 | `git diff --stat -- apps/desktop-avalonia/src` = **0** |

## 4. 第一次探针失败（自登记）

第一次用 PowerShell 的 `.Replace()` 做探针，字符串里含 `$"..."` 被 PowerShell 插值，替换未生效、测试仍全绿 ——
若就此收工，"判别力已验证"会是**假结论**。改用 Python 精确替换后，第一次又因删掉 `ex` 引用导致
`CS0168` 编译失败（同样不是"变红"）。第三次才得到真实的 2 failed / 1 passed。
**登记原因**：这类"探针没生效却被当成已验证"的风险，与上一轮 `GATE3-COVERAGE-MATRIX` 的
"源码推断代替实测"是同一类错误。

## 5. 边界

- 只覆盖"设置读取失败"这一条失败路径；`SettingsViewModel` 另有若干失败路径（外观保存失败、
  coordinator 未注入、只读拒绝）**未**逐条补测试。
- 视图级断言依赖"设置错误"banner 文案与"重试"按钮内容；若文案改变，测试会变红（这是期望的，
  但需同步更新矩阵措辞）。
