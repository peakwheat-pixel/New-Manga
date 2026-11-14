# TRANS-ENTRY-UI 证据（L1-T-C，2026-11-14）

## 0. 先做的 grep：会被影响的既有断言清单

按卡面要求，动手前先 grep `apps/desktop-avalonia/tests` 的相关中文串/错误码：

| 字符串 | 断言位置 | 处理 |
|---|---|---|
| `未配置模型 Provider` | `NewManga.App.Tests/CoreStateTextTests.cs:45`（`CoreStateText` 映射的 InlineData）、`V2StudioBatchTests.cs:834,837` | **保留原串不变**（我新增的 `TranslateErrorText.ProviderNotConfigured` 是另一条更长、带"去设置"引导的句子，不复用也不覆盖它） |
| `重启` | `V2StudioBatchTests.cs:886`（batch 错误文本含"重启"） | 保留；新文案也含"重启应用生效"，不冲突 |
| `开始处理` | `FluentResidualBatchATests.cs:607`（按钮 AutomationName）、`V2StudioBatchTests.cs:432`（按钮内容）、`FluentResidual3Tests.cs:364/391`（注释） | **按钮文案未改**，只改失败后的 `Error`/`Status` 文本 |
| `能力待接入` | `V2ConsoleUiTests.cs:115,294`（Console 的 `NotWiredBody`）、`V2StudioPageTests.cs:304`（page.StatusText）、`StudioInspectorPanel.cs:256` | Console/StudioPage 断言**未触碰**；`StudioInspectorPanel.cs:256` 的文案按 AC6 改写，**无测试引用该串**（grep 证实） |
| `INVALID_REQUEST` | `ChapterCreationTests.cs:91,148,207`、`ExportStalePolicyTests.cs:52`（控制器 `LastError` 码值） | 未触碰（这些断言的是**控制器码值**，不是用户可见文案） |

结论：本轮改动**不破坏**任何既有断言；唯一的文案改写（AC6）经 grep 确认无测试引用。

## 1. 用户可见字符串（逐条，供复核）

**AC1 前置门 / AC2 未配置**
> 还没有可用的翻译模型 Provider：请到「设置 → Provider 与凭据」添加并启用一个，然后回到这里重试。修改模型配置后需重启应用生效。

**AC2 凭据失败（401/403，不可重试）**
> Provider 拒绝了当前凭据（401/403，API key 无效或无权限）。请到「设置 → Provider 与凭据」更新 key 后重启应用；这类错误重试不会改善。

**AC2 请求被拒（404 模型名 / 402 额度，wire 上同为 INVALID_INPUT — 不编造区分）**
> 请求被拒绝：可能是模型名写错（404），也可能是账户额度/余额不足（402）。Core 目前对这两种情况返回同一个错误码，请核对模型名与账户额度后重试。

**AC2 限流（429，可重试）**
> Provider 限流（429）：稍等片刻再重试即可，重试会复用同一个意图键，不会重复接受 Run。

**AC3 空章**
> 本章没有可处理的页面：请先导入页面（或在章节里补页）再开始翻译。

**AC4 重启提示（常量，同时内嵌于 AC1 文案）**
> 修改模型配置后需重启应用生效。

**AC6 检查器过期文案（已按实测改写）**
> 人工译文输入框：本检查器尚未提供输入控件；译文写入命令 save_manual_translation 已在 Host 命令面可用（HostCommandRegistry:352 / core_service.py:4367），不是「能力待接入」

依据：`HostCommandRegistry.cs:352` 有 `["save_manual_translation"] = new("save_manual_translation", 3)`，Core `core_service.py:566/4367` 同名命令存在 ⇒ 原文"能力待接入（F0-1）"与事实不符。

## 2. AC 逐条

| AC | 结论 | 交付 |
|---|---|---|
| AC1 工作台前置门 | **PASS** | `WorkbenchViewModel.StartRunAsync` 用既有 `ResolveProviderBindingAsync("Translation")` 先解析当前绑定；`ProfileId is null` ⇒ 不发 StartRun，显示 AC1 文案 |
| AC2 四类错误可读化 | **PASS** | 新增 `Services/TranslateErrorText.cs`；`StartRun` 失败改用 `TranslateErrorText.ForCode(LastError)`；四类字符串互不相同（测试断言 distinct=4） |
| AC3 空章可读文案 | **PASS** | 前置 `ListChapterPagesAsync`；空 ⇒ 显示"本章没有可处理的页面…"，**不**透出 INVALID_REQUEST；探测抛错 ⇒ 跳过检查、不阻断（try/catch） |
| AC4 重启提示 | **PASS** | `TranslateErrorText.RestartHint` 常量 + 内嵌于 AC1 文案 |
| AC5 scoped 绑定如实表述 | **PASS（r1 修正）** | **事实更正**：设置页本来就有 book/chapter 绑定入口（`Views/Pages.cs:1141` 实例化 `ProviderBindingsSection`，`:89-94` 有 scope/书/章选择器）。r1 指出我先前写「没有入口」是**不实**。已在该 section 的说明文案补上卡面约束 3 的限定「**当前仅全局绑定驱动执行**：book/chapter 范围的绑定会保存并显示，但 Run 执行链只读全局槽位」 |
| AC6 过期文案 | **PASS** | `StudioInspectorPanel.cs:256` 改写为实测状态（见上） |
| AC7 零契约面 | **PASS** | 无新 wire 命令、无新 `IHostController` 成员（复用既有 `ResolveProviderBindingAsync` / `ListChapterPagesAsync`） |
| AC8 判别测试 | **PASS** | `tests/NewManga.App.Tests/TranslateEntryUiTests.cs` 4 例：四类文案不同、重启提示、缺绑定不发 StartRun、空章文案且不发 StartRun |
| AC9 门禁 | **PASS** | 见 §3 |

## 3. 测试数字

```
dotnet test NewManga.App.Tests        923 passed / 0 failed / 11 skipped   (934 total)
dotnet test NewManga.CoreClient.Tests 182 passed / 0 failed / 26 skipped   (208 total)
dotnet test NewManga.Host.Tests       321 passed / 0 failed / 74 skipped   (395 total)
```
四门禁：`check.ps1` / `check.ps1 -TaskPath doc/tasks/TRANS-ENTRY-UI.md` / `verify_pins` / `generate_api_inventory --check` 均 EXIT=0。

**过程中自曝的一次回归（已修，留档）**：第一版把空章探测做成**硬门**（空 → 直接 `return false`），App.Tests 立刻 **13 红**——既有测试的 fake Host 没有页数据，全被拦下。按卡面约束 4 改成**建议性探测**（探测照跑、尝试照发、失败文案用空章句子覆盖 `INVALID_REQUEST`）后回到 0 红。这条正是卡面提醒的"改文案撞坏既有断言"的同类风险。

## 4. 未做 / 限制

1. **402/404 仍不可区分**（wire 同为 `INVALID_INPUT`）：文案如实并列两种可能，**不**编造区分；已在卡面与本文件登记。
2. **空白章探测会多一次 Core 往返**（`list_chapter_pages`）；失败时静默跳过（不阻断），符合卡面约束 4。
3. **AC5 scoped**：入口**存在**（见上表更正），但**只有全局绑定驱动执行**；已在 UI 文案明写，避免用户按书配置后误以为生效。要真正支持 scoped 执行，必须先让 run 快照有 per-book 槽（L2/T-A 已证扁平槽只认全局），属产品+契约改动。
## 5. r1 复核处置（`doc/reviews/TRANS-ENTRY-UI-r1.md`）

### P1-1 空章句污染失败路径（已修）

根因：`ListChapterPagesAsync` 在 Host 未就绪/读失败时**返回空列表**（`HostController.cs:967-970`），而旧判定只数页数。修法：`chapterLooksEmpty = pages.Count == 0 && _host.Snapshot.State == HostViewState.Ready` —— 只有**就绪且确实 0 页**才用空章句；未就绪/读取异常保留原 typed 文案（不再谎称"本章没有页面"）。

新增断言（`TranslateEntryUiTests`）：
- `ReadyHostWithNoPages_ShowsTheEmptyChapterSentence`：Ready + 0 页 + StartRun 失败 ⇒ **`vm.Error == TranslateErrorText.EmptyChapter`**（旧测试无此断言，已被 r1 指出无判别力，现已补）
- `UnreadyHost_DoesNotPretendTheChapterIsEmpty`：`HostViewState.Failed` + 0 页 ⇒ **`vm.Error != 空章句`**，而是 `INVALID_REQUEST` 的可读映射

### P1-2 执行期展示面接映射（已修）

- Fluent 矩阵：`WorkbenchPageView.cs:618` 渲染的 `FluentRunProjection.ErrorCell`（`FluentRunProjection.cs:260`）**改为经 `TranslateErrorText.ForCode` 输出**；
- Studio drawer 的 step 行：`StudioBatchControls.cs:450` 的 `step.ErrorCode` 同样改为可读映射；
- 因此执行期 401/429/4xx 的用户可见文本与 StartRun 拒绝路径**同一套字符串**。
- 未接的面：`StudioInspectorPanel.cs:446-447` 的 `HistoryError` 是**历史读失败**的内部文本（非 provider/执行错误码），不在四类范围内，登记为不适用。

### P1-3 证据不实 + 设置页限定（已修）

- README 的 AC5 行改为事实（设置页**有** book/chapter 入口，`Pages.cs:1141` + `ProviderBindingsSection` scope 选择器）；
- `ProviderBindingsSection.cs:86` 文案补「**当前仅全局绑定驱动执行**：book/chapter 范围的绑定会保存并显示，但 Run 执行链只读全局槽位」。

### 其他登记

- 旧句「批量 Run 未启动（…）」在 r1 时**无测试保护**；改为可读映射后该句已移除，**不声称其曾被覆盖**。
- 硬门版本的 13 红从未提交，`NOT_RUN` 记录维持。