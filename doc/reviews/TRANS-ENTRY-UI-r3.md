---
task: TRANS-ENTRY-UI
task_id: TRANS-ENTRY-UI
reviewer: independent sub-agent (r3, read-only, not involved in r1/r2)
reviewer_agent: agent-9（lead 派发；独立上下文；未参与本卡实现、返修及 r1/r2 复核）
reviewer_kind: subagent
author: DSH（实施会话）
base_commit: fdda639a1
reviewed_head: 6803ed9dc
verdict: approved
decision: approved
date: 2026-11-14
scope: read-only
---

# Review：TRANS-ENTRY-UI（L1-T-C）r3 — 只核 r2 未关闭的 P1-2 及连带项

> **结论：`approved`。P1-2 已真实关闭；本卡可以收口。**
> r2 指认的三处执行期用户可见面（Fluent 矩阵 `ErrorCell`、Studio drawer step 行、drawer 详情行）现在都经过同一个映射；`ErrorCode is null` 仍显示「无错误码」而**没有**落入 `ForCode(null)` 的「未配置 Provider」句子；未知码保留原码。两条新增 `ErrorCell_*` 测试经回退实验证明会红。
> 仍有一处 **P2**：本 commit 实际修改的 `DrawerDetail` 行**没有测试**（全仓引用 0；回退成裸码后 8/8 全绿），而提交信息却写 "drawer and grid surfaces finally have coverage"——drawer 面并未被覆盖。这属于测试/证据完整性，不是 P1；按仓库「P0/P1 未解决不可批准」的门槛不阻断批准，但应在收口记录中处置（最好补 1 条 `DrawerDetail` 测试，或更正该表述）。

## 0. 审查者、固定点与方法

- **身份**：`agent-9`，lead 派发的独立上下文子 agent；**只读**；未参与本卡实现、返修、r1/r2 复核。仓库内唯一新增文件是本报告。
- **固定点**：`reviewed_head = 6803ed9dc`（父 `fdda639a1`）；复核开始时 `HEAD = 6803ed9dc4db5f8238901f351f3c4658cecd6718`，工作树干净（`git status --porcelain` 空）。
- **范围**：只核 r2 未关闭的 P1-2 及其连带项（drawer 详情行、测试、UI Markdown、AC5/README 数字、四件套、边界）。**P1-1、P1-3 按 r2 结论不再重核**。
- **方法**：逐行读 `6803ed9dc` 的 diff 与调用链；用**临时改源码 → 跑滤镜用例 → 还原 → SHA-256 核对**测量测试判别力；实跑 App.Tests 全量与四件套门禁。
- **只读自证**：临时改动 2 个源码文件（各 1 行），均已按备份还原；SHA-256 与改前一致（见 §2.4），`git status` 恢复为空。为防 r2 踩过的 MSBuild「已最新」假红，还原后把 `StudioBatchViewModel.cs` 的 mtime 置新并重建；**内容哈希未变**。

## 1. 逐项结论

| # | 复核项 | 结论 | 一句话证据 |
|---|---|---|---|
| 1 | `DrawerDetail` 是否经 `ForCode` 且 null 仍显示「无错误码」 | **PASS** | `StudioBatchViewModel.cs:620-622` 使用 `row.ErrorCode is null ? "无错误码" : ForCode(row.ErrorCode)`；null 分支在 `ForCode(null)` 之前，渲染链 `StudioBatchControls.cs:438, 464, 578` 未变 |
| 2 | `ErrorCell` 与 drawer step 行是否未被本轮破坏、未知码保留原码 | **PASS** | 本 commit 未触碰 `FluentRunProjection.cs` / `StudioBatchControls.cs`；`ErrorCell` 仍 `IsNullOrWhiteSpace → Missing` 否则 `ForCode`；step 行仍 `ForCode`；`TranslateErrorText.cs:60` 的兜底保留 `code.Trim()` |
| 3 | UI 文本是否还有 Markdown `**` 残留 | **PASS** | `apps/desktop-avalonia/src/**/*.cs` 的 21 处 `**` 中 20 处是注释、1 处是生成 Markdown 文档的字符串（非 Avalonia UI）；`*.axaml` 0 处；`ProviderBindingsSection.cs:86` 已改「【当前仅全局绑定驱动执行】」 |
| 4 | 新增 `ErrorCell_*` 两例是否真的保护展示面 | **PASS（两例判别力成立；drawer 面仍有 P2 缺口）** | 把 `ErrorCell` 回退成裸码 → `ErrorCell_MapsExecutionTimeCodeToReadableSentence` 红（1 failed / 7 passed，EXIT=1）；未知码例断言 `Contains("SOMETHING_NEW")`，验证保留原码。但把 `DrawerDetail` 回退成裸码 → 8/8 全绿（见 §2.4） |
| 5 | 文档一致性：任务卡 AC5、README 数字 | **PASS（AC5 与 923 已改；另有 P3 残留）** | `doc/tasks/TRANS-ENTRY-UI.md:54` 已写「设置页**确实有** book/chapter 绑定入口」；`verification/TRANS-ENTRY-UI/README.md:59` 已写 `923 passed / 0 failed / 11 skipped (934)`，与实测一致 |
| 6 | 实测 App.Tests 与四件套 | **PASS** | App.Tests **923/0/11（934）**，6 m 18 s，EXIT=0；`check.ps1` 默认与本卡均 `PASS (3 warnings)`；`verify_pins` `PASS (all 18)`；`generate_api_inventory --check` `1/80/6=87`，EXIT=0 |
| 7 | 零越界 | **PASS（实质无越界；字面清单多 1 个复核报告）** | diff 仅 6 文件；除题面三组外唯一文件是 `doc/reviews/TRANS-ENTRY-UI-r2.md`（new），在任务卡 `allowed_paths:25` 的 `doc/reviews/TRANS-ENTRY-UI-*.md` 内；无 Python `src/**`、无 contracts、无 `IHostController` 改动 |

## 2. 逐项证据

### 2.1 `DrawerDetail` 已接映射，null 不落 fallback

`apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Studio/StudioBatchViewModel.cs`：

```csharp
// :618 注释：Null keeps its "无错误码" wording instead of the ForCode fallback.
// :620-622
public string DrawerDetail => _drawerRow is { } row
    ? $"{row.StateLabel} · {(row.ErrorCode is null ? "无错误码" : NewManga.App.Services.TranslateErrorText.ForCode(row.ErrorCode))} · steps {row.Row.Steps.Count}"
    : string.Empty;
```

- `TranslateErrorText.ForCode` 对 null/空白返回 `ProviderNotConfigured`（`TranslateErrorText.cs:49-52`）；由于 ternary 先判 `row.ErrorCode is null`，null 时**不会**调用 `ForCode(null)`，显示的是「无错误码」。
- 渲染链未变：`StudioBatchControls.cs:438` 绑定 `DrawerDetail` → `:464` 加入 drawer 列 → `:578` 实例化 `StudioBatchDrawerControl`。用户选中失败页时看到的是可读句，不再是裸码。
- **边界 P3**：只判 `is null`，未判空白；`RunJson.ReadString`（`RunContracts.cs:584-594`）对 `"error_code": ""` 会原样返回空串，此时 `ForCode("")` 会显示「还没有可用的翻译模型 Provider」——把非 provider 失败说成未配置。见 R3-P3-1。
- **测试缺口 P2**：全仓测试对 `DrawerDetail` / `StudioBatchDrawerControl` 的引用为 **0**；见 §2.4 的回退实验。提交信息却写 drawer 与 grid 都获得覆盖，drawer 部分不实。见 R3-P2-1。

### 2.2 `ErrorCell` 与 drawer step 行未被本轮改动

`6803ed9dc` 只改了 `StudioBatchViewModel.cs` / `ProviderBindingsSection.cs` / `TranslateEntryUiTests.cs`，**未触碰** `FluentRunProjection.cs` 或 `StudioBatchControls.cs`。现状：

```csharp
// FluentRunProjection.cs:264-266
public string ErrorCell => string.IsNullOrWhiteSpace(ErrorCode)
    ? FluentRunProjection.Missing
    : NewManga.App.Services.TranslateErrorText.ForCode(ErrorCode);
```

```csharp
// StudioBatchControls.cs:450（drawer step 行）
StudioUi.Text(step.ErrorCode is null ? string.Empty
    : NewManga.App.Services.TranslateErrorText.ForCode(step.ErrorCode), "meta")
```

未知码由 `ForCode` 兜底保留原码：

```csharp
// TranslateErrorText.cs:60
_ => $"{code.Trim()}（未识别的错误码，请连同此码反馈）",
```

⇒ 两者未被本轮破坏；`EMPTY_TARGET_SELECTION`、`HOST_NOT_READY` 等未知码仍带原码可诊断。`ErrorCell` 对空串/空白返回 `Missing`，比 drawer 行更稳。

### 2.3 UI 文案的 Markdown 残留

命令（工作目录 `G:\CODEX\New Manga`）：

```
grep -rn '\*\*' apps/desktop-avalonia/src --include=*.cs
grep -rn '\*\*' apps/desktop-avalonia/src --include=*.axaml
```

结果：`*.cs` 21 处、`*.axaml` 0 处。逐条分类：

- 20 处位于 `///` / `//` 注释（如 `FluentRunProjection.cs:143` 的 `**1-based**`、`StudioSelection.cs:31` 的 `**优先于**`），不进入 UI；
- 1 处位于 `NewManga.DesignSystem/Tokens/TokenDictionaryWriter.cs:211` 的 `builder.AppendLine(...)`，它生成的是 token 映射的 **Markdown 文档**，不是 Avalonia 控件文本；
- UI 文本字面量中 `**` 为 **0**。

`ProviderBindingsSection.cs:86` 现为：

```
把某个 provider profile 绑定到 (scope, capability) 槽位；【当前仅全局绑定驱动执行】：book/chapter 范围的绑定会保存并显示，但 Run 执行链只读全局槽位（跨书/跨章按槽位解析尚未接入）。book/chapter 范围用真实书库选择器。
```

`【】` 是普通全角括号，`Ui.Text` 直接赋给 `TextBlock.Text` 也不会产生 Markdown 语法。**P2-1（r2）的星号残留已关闭。**

### 2.4 新增测试的判别力（含回退实验）

新增两例（`TranslateEntryUiTests.cs:125-140`）：

```csharp
[Fact]
public void ErrorCell_MapsExecutionTimeCodeToReadableSentence()
{
    var row = new FluentRunRow("p1", 0, "a.png", StatusKind.Failed, "失败", "failed", "PROVIDER_AUTH_FAILED", "row");
    Assert.Equal(TranslateErrorText.ForCode("PROVIDER_AUTH_FAILED"), row.ErrorCell);
    Assert.DoesNotContain("PROVIDER_AUTH_FAILED", row.ErrorCell, StringComparison.Ordinal);
}

[Fact]
public void ErrorCell_KeepsUnknownCodeForDiagnosis()
{
    var row = new FluentRunRow("p1", 0, "a.png", StatusKind.Failed, "失败", "failed", "SOMETHING_NEW", "row");
    Assert.Contains("SOMETHING_NEW", row.ErrorCell, StringComparison.Ordinal);
}
```

**(a) 回退 `ErrorCell` → 必然变红（实测）。** 把 `ErrorCell` 的 else 分支临时改成 `: ErrorCode!;`，跑：

```
dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests\NewManga.App.Tests.csproj \
  --filter "FullyQualifiedName~TranslateEntryUiTests"
```

结果：

```
[xUnit.net] NewManga.App.Tests.TranslateEntryUiTests.ErrorCell_MapsExecutionTimeCodeToReadableSentence [FAIL]
Assert.Equal() Failure: Strings differ
Expected: "Provider 拒绝了当前凭据（401/403，API key 无效或无权限）…"
Actual:   "PROVIDER_AUTH_FAILED"
失败! - 失败: 1，通过: 7，已跳过: 0，总计: 8        EXIT=1
```

⇒ 只要把 `ErrorCell` 回退成裸码，第一例必红。**判别力成立。** 还原后 SHA-256 `5FDB31722EC608975D5200E870159DC799EF081D0A5078B205E6817603C6D12B`，与改前一致。

**(b) 未知码例确实验证「保留原码」。** `Contains("SOMETHING_NEW")` 在未知码被替换成通用句（丢掉原码）时会红；在 `ErrorCell` 输出裸码时仍绿——这正是有意为之：未知码的正确行为就是保留原码。它不区分「裸码」与「带提示的映射」，因为两者都满足「保留原码」；该断言足以保护诊断信息不被吞。

**(c) 但 drawer 面仍无测试（P2）。** 把 `DrawerDetail` 临时回退成 r2 指认的旧写法：

```csharp
? $"{row.StateLabel} · {row.ErrorCode ?? "无错误码"} · steps {row.Row.Steps.Count}"
```

同一滤镜用例：

```
已通过! - 失败: 0，通过: 8，已跳过: 0，总计: 8        EXIT=0
```

⇒ **本 commit 真正修改的那一行，回退后测试全绿**；全仓对 `DrawerDetail` / `StudioBatchDrawerControl` 的引用为 0。提交信息说 "drawer and grid surfaces finally have coverage" 只对 grid 成立。r2 的 P2-1 最低要求是 ErrorCell 例（「能同时覆盖 drawer 更佳」），故这是 **P2 证据缺口**，不是 P1 未关闭。还原后 SHA-256 `6BC10C30BC6AC0A2F634AC2AF8C54E23D78735FC0A41BB46EE59B9C4D4E4F35B`，与改前一致。

**(d) 还原与重跑。** 两文件还原后哈希均与改前一致；对 `StudioBatchViewModel.cs` 置新 mtime 以强制重建，滤镜用例在原始源码上 **8/8 通过**；`git status --porcelain` 为空。

### 2.5 文档一致性

| 检查点 | 事实 | 结论 |
|---|---|---|
| 任务卡 AC5 | `doc/tasks/TRANS-ENTRY-UI.md:54` 已写「设置页**确实有** book/chapter 绑定入口（`Views/Pages.cs:1141`）；须在该 section 标注「当前仅全局绑定驱动执行」」 | **PASS** |
| README App.Tests 数字 | `verification/TRANS-ENTRY-UI/README.md:59` = `923 passed / 0 failed / 11 skipped (934 total)`；实测同值 | **PASS** |
| 任务卡旧事实残留 | `doc/tasks/TRANS-ENTRY-UI.md:91` 的交付记录仍写「AC5 设置页无 scoped 入口，登记「未提供」」，与 `:54` 自相矛盾 | **P3（R3-P3-2）** |
| README AC8 例数 | `README.md:53` 仍写 `TranslateEntryUiTests.cs` 4 例；实际 `[Fact]` 已 **8** 例（r1 加了 2、本轮加了 2） | **P3（R3-P3-3）** |
| README §5 P1-2 清单 | `:82-87` 只列 `ErrorCell` 与 step 行，未记本轮补的 drawer 详情行与新测试；「已修」的标题现在为真，但证据不完整 | **P3（R3-P3-3）** |
| 任务卡收口字段 | `reviewer: null`、`delivery_head: null`、AC 全 `[ ]`、Closeout「未关闭」 | 收口时由 DSH 填写，不属本轮代码缺陷 |

### 2.6 实测记录

工作目录 `G:\CODEX\New Manga`；`HEAD = 6803ed9dc`；改前 `git status --porcelain` 为空。

| 场景 | 命令 | 结果 |
|---|---|---|
| App.Tests 全量（未 `--no-build`） | `dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests\NewManga.App.Tests.csproj` | **`失败: 0，通过: 923，已跳过: 11，总计: 934，持续时间: 6 m 18 s`**，`EXIT=0` |
| 治理门禁（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)`，`EXIT=0` |
| 治理门禁（本卡） | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/TRANS-ENTRY-UI.md` | `Governance check: PASS (3 warnings)`，`EXIT=0` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，`EXIT=0` |
| API 清单 | `python tools/generate_api_inventory.py --check` | `OK: rendered counts match FEA-C07 doc`（1/80/6=87），`EXIT=0` |
| 回退 `ErrorCell`（判别力） | 同项目 `--filter "FullyQualifiedName~TranslateEntryUiTests"` | **1 failed / 7 passed**，失败者 `ErrorCell_MapsExecutionTimeCodeToReadableSentence`，`EXIT=1`；已还原，SHA-256 一致 |
| 回退 `DrawerDetail`（缺口证明） | 同上 | **0 failed / 8 passed**，`EXIT=0`；已还原，SHA-256 一致 |
| 还原后滤镜复跑 | 同上 | **8 passed**，`EXIT=0`；源码哈希与改前一致 |

**未跑**：`NewManga.CoreClient.Tests` / `NewManga.Host.Tests`。本轮窄复核只要求 App.Tests；README 中 182/208、321/395 未在本轮重验，按 `NOT_RUN` 记录，不据此加减分。

### 2.7 零越界

```
$ git diff 6803ed9dc^ 6803ed9dc --name-only
apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Studio/StudioBatchViewModel.cs
apps/desktop-avalonia/src/NewManga.App/Views/ProviderBindingsSection.cs
apps/desktop-avalonia/tests/NewManga.App.Tests/TranslateEntryUiTests.cs
doc/reviews/TRANS-ENTRY-UI-r2.md
doc/tasks/TRANS-ENTRY-UI.md
verification/TRANS-ENTRY-UI/README.md
```

- 题面三组：`apps/desktop-avalonia/**`、`doc/tasks/TRANS-ENTRY-UI.md`、`verification/TRANS-ENTRY-UI/**`——**全部命中**。
- 唯一额外文件是 `doc/reviews/TRANS-ENTRY-UI-r2.md`（新增的 r2 复核报告），在任务卡 `allowed_paths:25` 的 `doc/reviews/TRANS-ENTRY-UI-*.md` 内；r2 报告对 r1 报告也采用同一口径（`fdda639a1` 中的 r1 报告不判越界）。⇒ **实质无越界**。
- `src/**`（Python Core）：**0 文件**；`doc/contracts/**`：**0 文件**；`IHostController.cs` / wire 命令表：**未出现**。AC7 的 1/80/6=87 仍成立。

## 3. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R3-P2-1 | **P2** | `TranslateEntryUiTests.cs:125-140`；`StudioBatchViewModel.cs:620-622`；`6803ed9dc` 提交信息 | 新增测试只覆盖 `FluentRunRow.ErrorCell`；本 commit 修改的 `DrawerDetail` 无任何测试（全仓引用 0），回退该行后 8/8 全绿。提交信息却称 "drawer and grid surfaces finally have coverage"——drawer 面未覆盖。修改行的回归无自动化保护，证据表述失实。 | §2.4(c) 的回退实验；`grep DrawerDetail tests` = 0 | 补 1 条 `DrawerDetail` 测试（已知码 → 可读句、null → 「无错误码」），或更正提交/README 的覆盖表述；在收口记录中处置 | open |
| R3-P3-1 | **P3** | `StudioBatchViewModel.cs:621`；`StudioBatchControls.cs:450`；`RunContracts.cs:584-594` | `DrawerDetail` 与 step 行都只判 `is null`；wire 上 `"error_code": ""` 会经 `ReadString` 原样返回空串，`ForCode("")` 落入 `ProviderNotConfigured`，把非 provider 失败说成「未配置 Provider」。 | `ForCode` 的 `IsNullOrWhiteSpace` 分支（`TranslateErrorText.cs:49-52`）；r2 P3-3 已指出 step 行同型问题，本轮新行沿用 | 两处改判 `string.IsNullOrWhiteSpace`；或让 `ForCode` 对空码给独立句 | open（非阻断） |
| R3-P3-2 | **P3** | `doc/tasks/TRANS-ENTRY-UI.md:91` | 交付记录仍写「AC5 设置页无 scoped 入口，登记「未提供」」，与已更正的 AC5（`:54`）矛盾；权威任务卡内仍有一处旧事实。 | 文件逐行 | 收口时在该历史句加更正标注（保留历史，不抹掉） | open（非阻断） |
| R3-P3-3 | **P3** | `verification/TRANS-ENTRY-UI/README.md:53,82-87` | AC8 仍写「4 例」（实际 8 个 `[Fact]`）；§5 P1-2 清单未记 drawer 详情行与本轮新增测试，证据与代码不同步。 | `grep -c "\[Fact\]" TranslateEntryUiTests.cs` = 8；README 逐行 | 收口时同步 AC8 例数与 §5 清单 | open（非阻断） |
| R3-P3-4 | **P3** | `StudioBatchViewModel.cs:82,156` | cell / page 行的 `Tooltip` 仍直接拼接裸 `ErrorCode`；悬停时用户仍可见机器码。r2 已把 Tooltip 标为「可选」，不属 r2 关闭条件。 | 代码逐行；`StudioBatchControls.cs:133,159,226` 绑定 | 可后续统一改 `ForCode` 或 `中文（CODE）` 口径；不阻断 | open（r2 已标可选） |

## 4. 明确回答

1. **P1-2 是否已真实关闭？——是。** r1/r2 指认的三个执行期用户可见面全部接上同一映射；`DrawerDetail` 的 null 分支保留「无错误码」，未落 `ForCode(null)`；`ErrorCell` 与 step 行未被破坏；未知码保留原码；`ErrorCell` 回退实验会使测试变红。r2 要求的最小返修（映射 + 1 条执行期测试）已满足。
2. **本卡能否收口？——可以，`approved`。** 无 P0/P1；四件套与 App.Tests 全绿；边界实质无越界。收口前请 DSH：① 处置 R3-P2-1（最好补 1 条 `DrawerDetail` 测试，或更正「drawer 已覆盖」的表述）；② 登记 R3-P3-1..4 的 disposition；③ 填写任务卡的 `reviewer`、`delivery_head`、AC 勾选与 Closeout。
3. **残留风险**：drawer 详情行仍无自动化回归保护（P2）；空串错误码会把非 provider 失败误述为「未配置」（P3）；Tooltip 仍显示裸码（P3，r2 已标可选）。均不构成 P1。

## 5. 复审边界

本报告只对 `reviewed_head = 6803ed9dc` 有效；head 改变或出现新 Review 后，本文件自动成为历史记录。P1-1、P1-3 未在本轮重核，按 r2 结论保留。
