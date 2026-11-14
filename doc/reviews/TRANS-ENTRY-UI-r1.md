---
task: TRANS-ENTRY-UI
task_id: TRANS-ENTRY-UI
reviewer: independent sub-agent (r1, read-only)
reviewer_agent: agent-7（lead 派发；独立上下文；未参与本卡实现与返修）
reviewer_kind: subagent
author: DSH（实施会话）
base_commit: 38cadcde6
reviewed_head: ff1778246
verdict: changes_requested
decision: changes_requested
date: 2026-11-14
scope: read-only
---

# Review：TRANS-ENTRY-UI（L1-T-C）r1

> **结论：`changes_requested`。本卡不能收口。** 0 个 P0、**3 个 P1**、6 个 P2。
> 文案本身（四类互不相同、402/404 不编造区分）与零契约面是达标的；问题集中在**文案接线的位置不对**与**AC5 的登记与仓库事实不符**：
> 1. **P1-1**：空章判定被放在所有失败码之前，且 `list_chapter_pages` 在 Host 未就绪/读取失败时**返回空列表而不是异常**——于是 `HOST_NOT_READY`（读取直接返回空），以及任何发生在空页/读失败章节上的其他失败（`HOST_READ_ONLY`、执行期 `PROVIDER_AUTH_FAILED` 等），都会被显示成「本章没有可处理的页面」。这不是"降级"，是**反向误诊**。
> 2. **P1-2**：四类文案只接在 `WorkbenchViewModel.StartRunAsync` 的**启动拒绝**路径；而 401/403、429、4xx 是在**执行期**才出现的，用户实际看到它们的两个面（Fluent 批次矩阵 `ErrorCell`、V2 Studio drawer）仍是**裸错误码**。地图画对了，但没画在错误发生的地方。
> 3. **P1-3**：证据 README 写「设置页当前没有按书/章配置 provider 的入口」——**不成立**：仓库里仍随包发布的设置页 `Pages.cs:1141` 就有 `ProviderBindingsSection`（scope = global/**book**/**chapter**），且其说明文案写着「运行链会按槽位解析 provider」，正好与前置约束 3（scoped 不驱动执行）相反；卡面要求的「当前仅全局绑定驱动执行」标注不存在。
>
> **三点口径速答**：**402/404 不区分——可以接受**（文案如实、wire 证据成立）；**AC3「不拦、只换文案」——方向可以接受、当前实现不可以**；**AC1 fail-open——方向可以接受、fail-open 场景的失败文案不可以**。详见 §5。

## 0. 审查者、固定点与方法

- **身份**：`agent-7`，lead 派发的独立上下文子 agent；只读复核；**未参与** `TRANS-ENTRY-UI` 的实现或返修。仓库内唯一新增文件是本报告；未 commit / 未 push / 未 checkout / 未改任何既有文件。
- **固定点**：`reviewed_head = ff1778246`（父 = `38cadcde6`，即本卡的释放提交）。只对该 head 有效。
- **复核期间的仓库事实（如实记录）**：
  - 我开始时 HEAD = `ff1778246`，工作树有 `M doc/tasks/TRANS-ENTRY-UI.md`（lead 尚未提交的交付记录 + 裁决）。复核过程中 lead 提交了 `a9591dc1b`（**纯文档**，`doc/tasks/TRANS-ENTRY-UI.md` +22 行，内容即交付记录与三条 DSH 裁决）；代码与测试与 `ff1778246` 相同。本报告仍按要求只审 `ff1778246`，`a9591dc1b` 的文档内容作为「交付记录」一并核对。
  - 跑 `NewManga.CoreClient.Tests` 时，既有测试 `WireLogSourceRedactionTests.PersistedNdjsonContainsOnlyRewrittenBytes` 向 `verification/FEA-09/logs/wire-redacted.ndjson` **追加了 1 行**（时间戳 `2026-11-14T11:45:02Z`）。这是**测试自身的证据写入副作用**，不是我对既有文件的编辑；我未回滚、未改写该文件。除此之外工作树无其他变化。
- **方法**：逐行读 `ff1778246` 的 diff、其调用链与生产语义；对照 Core 的 wire 错误面（401/403、429、其他 4xx）与绑定解析链；实跑三套 `dotnet test` 与四类门禁。**未做**任何代码改动，因此"第一版硬门导致 13 红"这一历史无法复跑（记 `NOT_RUN`，见 2.2）。
- **视角声明**：Architecture = executed（入口门/错误面/绑定执行面/wire 诚实性）；Verification = executed（见 §4）。Standards/Spec 未单独成轴（模板允许可选）。

## 1. 逐项结论

| # | 复核项 | 结论 | 一句话证据 |
|---|---|---|---|
| 1 | 四类文案互不相同、且不编造 wire 不可区分的东西 | **PASS**（文本层） | `TranslateErrorText.cs:19-38` 五句互异；测试 `TranslateEntryUiTests.cs:46-47` 断言 distinct=4；402/404 同为 `INVALID_INPUT`（`openai_client.py:10-19`）被**合并成一句并明说"同一个错误码"**，没有假装能分辨。但接线面不足 → P1-2 |
| 2 | AC3 空章降级的正确性 | **FAIL**（降级方向对，实现与验证都不对） | 不阻断 = PASS（`WorkbenchViewModel.cs:192-201` 只有赋值、不 `return`；测试 `StartRunRequests` 非空）；**但空章句优先于所有错误码**（`:224-226`），且 Host 在未就绪/读失败时返回**空列表**（`HostController.cs:963-981`）→ 反向误诊；空章测试不断言 VM 输出（`TranslateEntryUiTests.cs:71-85`）。13 红 → 0 红：当前 **0 红**已复现；历史 13 红 `NOT_RUN` |
| 3 | AC1 fail-open 是否让"未配置"漏过 | **PASS（未配置不漏）+ P1（fail-open 文案会错）** | Host 就绪且确实无绑定时 Core 返回 `{"profile_id": null, "source": null}` 的**对象**（`settings_commands.py:794-818`），解析成 `ProviderBindingResult(false, null, …)`（`HostController.cs:1679`）→ `ProfileId is null` 命中，门拦住。`null` 只在 Host 未就绪/命令异常/响应畸形时出现（`HostController.cs:1656-1686`）→ fail-open；但该场景的 StartRun 失败会被 AC3 覆盖成空章句（P1-1） |
| 4 | 既有断言是否被削弱 | **PASS**（且是**"未被触碰"而非"被保住"**） | `ff1778246` 只改 3 个源码文件 + 新增 1 个测试文件 + 证据 README，**未修改任何既有测试**；`未配置模型 Provider`/`重启`/`开始处理`/`能力待接入`/`INVALID_REQUEST` 五类断言逐条在位（§2.4）。注意：这些断言都不在本次被改的 Workbench 失败路径上，旧句 `批量 Run 未启动（…）` 在仓库里**没有任何测试**，所以"没削弱"不能证明"没回归" |
| 5 | AC5 scoped 表述 | **FAIL** | 设置页**有**按书/章配置入口：`Pages.cs:1141` → `ProviderBindingsSection`，scope 下拉含 book/chapter（`ProviderBindingsSection.cs:68,89`），测试明确选过 Book（`SettingsProfileUiTests.cs:408-416`）；页面文案却写「运行链会按槽位解析 provider」（`:86`），且**没有**「当前仅全局绑定驱动执行」。证据 README 的"未提供"登记与事实不符 |
| 6 | AC7 零契约面 | **PASS**（附 1 条口径说明） | `git diff ff1778246^ ff1778246 --name-only` = 4 个 `apps/desktop-avalonia/**` + `verification/TRANS-ENTRY-UI/README.md`（卡面 allowed_paths 允许）；`src/**` **0 改动**；`generate_api_inventory --check` = `1/80/6=87` 且 `OK`；`verify_pins` = **18/18 PASS** |
| 7 | 实测（App / CoreClient / Host / 四门禁） | **PASS** | App **919/0/11（930）**、CoreClient **182/0/26（208）**、Host **321/0/74（395）**，与交付声明一致；`check.ps1`（默认 + TaskPath）、`verify_pins`、`generate_api_inventory --check` 全 `EXIT=0`（§4） |
| 8 | 文案质量（能否看懂 + 可执行下一步） | **PARTIAL** | 未配置 / 401-403 两句好（给出设置路径与重启）；402/404 与 429 两句夹带内部术语（`Core`、`意图键`、`Run`）且 402/404 没给"去哪里核对"；空章句没给导入入口；检查器新文案把 `HostCommandRegistry:352 / core_service.py:4367` 写进用户界面（§2.8、P2-4） |

## 2. 逐项证据

### 2.1 第 1 项：四类文案是否真的可区分、是否编造区分

**四句用户可见字符串**（`Services/TranslateErrorText.cs`）：

| 类 | 行 | 文本 | 可辨别锚点 |
|---|---|---|---|
| 未配置 | `:19-20` | 还没有可用的翻译模型 Provider：请到「设置 → Provider 与凭据」添加并启用一个，然后回到这里重试。修改模型配置后需重启应用生效。 | 「设置 → Provider 与凭据」+ 重启 |
| 401/403 | `:23-24` | Provider 拒绝了当前凭据（401/403，API key 无效或无权限）。请到「设置 → Provider 与凭据」更新 key 后重启应用；这类错误重试不会改善。 | 401/403、不可重试 |
| 404/402 | `:30-31` | 请求被拒绝：可能是模型名写错（404），也可能是账户额度/余额不足（402）。Core 目前对这两种情况返回同一个错误码，请核对模型名与账户额度后重试。 | 并列两种可能 + 明说同码 |
| 429 | `:34-35` | Provider 限流（429）：稍等片刻再重试即可，重试会复用同一个意图键，不会重复接受 Run。 | 429、可重试 |

- **互不相同**：四句文本层 distinct=4（`TranslateEntryUiTests.cs:46-47` 断言），我逐字比对成立。
- **402/404 的诚实性（本项核心）：PASS。** Core 侧总映射表 `src/infrastructure/providers/openai_client.py:10-19`：401/403→`PROVIDER_AUTH_FAILED`，429→`PROVIDER_RATE_LIMITED`，**other 4xx→`INVALID_INPUT`**（`src/ports/providers/errors.py:140-143` 的 `ProviderInputError.error_code = "INVALID_INPUT"`）。也就是说 404（模型名）与 402（额度）在 wire 上确实**同为 `INVALID_INPUT`**，状态码不下发。实现把两者写进**同一句**并明说"Core 对这两种情况返回同一个错误码"——**没有编造区分**，符合卡面「不要骗」的要求。这与"四句可区分"并不矛盾：可区分的是**错误类**（未配置 / 凭据 / 请求被拒 / 限流），不是 402 vs 404。
- **但"用户可见"只在启动拒绝这一处成立（P1-2）。** `TranslateErrorText` 在生产代码里只有两个引用点：`WorkbenchViewModel.cs:176`（前置门）和 `:225-226`（`StartRun` 失败）。而 `PROVIDER_AUTH_FAILED`/`PROVIDER_RATE_LIMITED`/`INVALID_INPUT` 发生在 **Run 执行期**（`StartRun` 只负责受理并返回 `run_id`：`src/bootstrap/core_service.py:6692-6720` → `accept_start_run`；受理路径里没有 provider 调用），因此一般不会成为 `StartRun` 的 `LastError`。用户真正看到这三类码的地方是：
  - Fluent 批次矩阵：`FluentRunProjection.cs:260` `ErrorCell => … ErrorCode` 原样输出，渲染在 `Views/Fluent/WorkbenchPageView.cs:618`；
  - V2 Studio drawer：`StudioBatchViewModel.cs:616-618` `{row.ErrorCode ?? "无错误码"}`；
  - V2 步骤错误映射 `RunStatusMonitor.StepErrorText`（`:344-367`）里**没有** `PROVIDER_AUTH_FAILED`、没有 `INVALID_INPUT`（只有 `PROVIDER_NOT_CONFIGURED`/`PROVIDER_RATE_LIMITED` 两条既有映射）。
  ⇒ 结论：**四类文案可区分、不编造（PASS）**；但 `AUTH`/`429`/`404·402` 三类在**它们实际出现的面上仍是裸码**，AC2 的"用户可见"只完成了一半（P1-2）。

### 2.2 第 2 项：AC3 空章降级是否正确

**（a）探测失败/无数据时不会阻断 `StartRun`：PASS。**
`WorkbenchViewModel.cs:186-201`：探测只写本地 `chapterLooksEmpty`，`catch` 里什么都不做；`:203-229` 继续生成意图键并**照发** `StartRunAsync`。测试 `TranslateEntryUiTests.cs:72-85` 断言 `host.StartRunRequests` 非空，确实不阻断。

**（b）空章时用户确实看到空章文案而非 `INVALID_REQUEST`：FAIL（只在"StartRun 恰好失败"时成立，且会误伤其他失败）。**
失败分支是：

```csharp
Error = chapterLooksEmpty
    ? TranslateErrorText.EmptyChapter
    : TranslateErrorText.ForCode(_host.Snapshot.LastError);   // :224-226
```

问题有两层：

1. **空章优先于所有错误码**，不只是卡面说的「覆盖 `INVALID_REQUEST`」。只要页数看起来是 0，`PROVIDER_AUTH_FAILED`、`PROVIDER_RATE_LIMITED`、`HOST_READ_ONLY`、`HOST_NOT_READY` 全部被替换成「本章没有可处理的页面：请先导入页面…」。
2. **`list_chapter_pages` 没有"未知"态**：`HostController.ListChapterPagesAsync` 在 Host 未就绪时直接 `return Array.Empty<…>()`（`:967-970`），UI 面失败也吞成空列表（`:977-980`）。所以"读不到"= "0 页"。于是：

| 场景 | `chapterLooksEmpty` | `LastError` | 用户实际看到 | 是否事实 |
|---|---|---|---|---|
| 真空章 + Core 拒 `INVALID_REQUEST` | true | `INVALID_REQUEST` | 空章句 | ✅ 卡面目标 |
| **Host 未就绪**（fail-open 的典型场景） | true（空列表） | `HOST_NOT_READY` | 空章句 | ❌ 页可能一页不少 |
| **只读模式** | true（若空） | `HOST_READ_ONLY` | 空章句 | ❌ 与只读无关 |
| 真空章 + 执行期 401 | true | `PROVIDER_AUTH_FAILED` | 空章句 | ❌ 掩盖真实原因 |
| 有页 + 401 | false | `PROVIDER_AUTH_FAILED` | 401/403 句 | ✅（若该码能到 `LastError`，见 P1-2） |

这不是卡面所说的"建议性探测"：**建议性探测的语义应是"探测失败→不提示"，而当前是"探测无数据→给出确定的错误诊断"**。DSH 裁决 R-4② 写「AC1 fail-open 意味着『已配置但 Host 未就绪』会进入 StartRun 并失败（失败文案已可读）」——按上面第 2 行，该表述在当前实现下**不成立**（文案可读，但**是错的**）。这是本卡最需要返修的一点（P1-1）。

**（c）13 红是否真的回到 0 红：当前 0 红成立；历史 13 红 `NOT_RUN`。**
- 当前实跑：App **919 passed / 0 failed / 11 skipped（930）**，0 红成立。
- 历史上"硬门导致 13 红"：仓库里没有留下硬门版本（未提交、无 diff 可回放），我**无法复跑**，记 `NOT_RUN`。机制上完全可信：`FakeHostController.ListChapterPagesAsync` 默认对未登记的章节返回空列表（`FakeHostController.cs:1181-1190`），既有 Fluent 测试的 fake Host 基本都不登记页数据；硬门会把这些 Start 路径全部拦下。**但请注意**：这条自曝恰恰证明"页数为 0 ≠ 章节为空"——实现者把"不拦"改对了，却没有把"别把 0 页当确定诊断"改对。

**（d）测试是否判别了 AC3：不判别（P2-1）。** `TranslateEntryUiTests.cs:71-85` 的三条断言是：
1. `Assert.Contains("chapter-1", host.ChapterPageCalls)` —— `LoadAsync` 自己就会调 `ListChapterPagesAsync`（`WorkbenchViewModel.cs:521`），所以**即使删掉 StartRun 前的探测**该断言仍通过；
2. `Assert.NotEmpty(host.StartRunRequests)` —— 只证明"没被拦"；
3. `Assert.Contains("本章没有可处理的页面", TranslateErrorText.EmptyChapter)` —— 常量断言自身子串，**没有断言 `vm.Error`**。
   ⇒ 把 `:224-226` 整段回退成旧的 `"批量 Run 未启动（…）"`，这个测试**仍然全绿**。AC8 要求的"空章文案判别测试"没有真正建立判别力（见 P2-1）。

### 2.3 第 3 项：AC1 fail-open 是否让"未配置"漏过

- **Host 就绪且确实没配 provider 时返回什么**：`settings_provider_bindings_resolve`（`src/bootstrap/settings_commands.py:794-818`）在无绑定时返回 `{"profile_id": null, "source": null}`（`_resolve_current_binding` 无匹配 → `None, None`，`:1219-1235`；返回对象而非异常）。Host 侧 `ResolveProviderBindingAsync` 拿到**对象**后返回 `new ProviderBindingResult(false, ReadString(value,"profile_id"), …)`（`HostController.cs:1669-1679`），即 `ProfileId = null`。门条件 `binding is not null && binding.ProfileId is null`（`WorkbenchViewModel.cs:174`）命中 → **不发 StartRun、显示 AC1 文案**。所以"未配置"**不会**从 ready 态漏过。**PASS。**
- **`null` 何时出现**：Host 未就绪（`:1656-1659`）、任意被捕获的 Core/桥/IO/取消异常（`:1681-1686`）、响应不是对象（`:1670-1673`）。把 `null` 当"未配置"确实会误伤"已配置但 Host 未起"的用户；fail-open 的方向**可以接受**，且与 DSH R-2 的口径一致。
- **但 fail-open 的失败文案不诚实**：进入 StartRun 后 Host 回 `HOST_NOT_READY`（`HostController.cs:2732-2735`）；此时 AC3 的探测已先把 `chapterLooksEmpty` 置 true（原因见 2.2），用户看到的是空章句。**fail-open 本身没问题，问题在它的失败出口被 AC3 的错误优先级污染。** 此外 `ForCode(null)` 返回"未配置"（`TranslateErrorText.cs:49-52`）——"未知"被写成"确定未配置"，与 402/404 的诚实口径自相矛盾（P2-2；真实 Host 的 StartRun 失败路径都会 set code，所以目前是潜伏缺陷）。
- **一个额外的合理性问题（P2，不阻断）**：`_resolve_current_binding` 在有 book/chapter 上下文时会优先 book/chapter（`settings_commands.py:1219-1235`；run 快照调用点在 `:610-615`），但门只按 global 解析（不带上下文），这与"book/chapter 不驱动执行"一致；若用户只配了 book 绑定，门判"未配置"是**正确**的。无需改。

### 2.4 第 4 项：既有断言逐条核实（是否保留、是否变弱）

先给硬事实：`ff1778246` 的 diff **未修改任何既有测试文件**（`--name-only` 只有 3 个 `src/NewManga.App` 文件 + 1 个新增测试 + 证据 README）。以下断言逐条在 `ff1778246` 的工作树上核实：

| 断言串 | 位置 | 形态 | 结论 |
|---|---|---|---|
| `未配置模型 Provider` | `CoreStateTextTests.cs:45`（InlineData） | 值相等断言 | 在，未改 |
| `未配置模型 Provider` | `V2StudioBatchTests.cs:834`（`batch.ErrorText` 含）、`:837`（`batch.HeaderLine` 含） | `Contains` | 在，未改 |
| `重启` | `V2StudioBatchTests.cs:886`（只读模式错误文本含"重启"） | `Contains` | 在，未改 |
| `开始处理` | `FluentResidualBatchATests.cs:607`（按钮 AutomationName） | 相等 | 在，未改 |
| `开始处理` | `V2StudioBatchTests.cs:432`（按钮 Content） | 相等 | 在，未改 |
| `能力待接入` | `V2ConsoleUiTests.cs:115,294`（`console.NotWiredBody`） | `Contains` | 在，未改 |
| `能力待接入` | `V2StudioPageTests.cs:304`（`page.StatusText`） | `Contains` | 在，未改 |
| `INVALID_REQUEST` | `ChapterCreationTests.cs:91,148,207`；`ExportStalePolicyTests.cs:52`（`Snapshot.LastError` 码值） | 相等 | 在，未改 |

- 实现者证据 README §0 的 grep 表**逐条属实**，且对 `StudioInspectorPanel.cs:256`「无测试引用该串」的判断也属实（全仓测试没有断言旧检查器文案）。
- **但要补充定性**：上表中与 provider 文案相关的 `未配置模型 Provider`/`重启` 两条属于 **V2 `StudioBatchViewModel`** 的映射（`StudioBatchViewModel.cs:1136-1155`），**不是**本卡改的 `WorkbenchViewModel` 失败路径；而旧句 `批量 Run 未启动（{code}）` 在仓库里**没有任何测试**（全仓 grep 为 0）。因此"既有断言未削弱"成立，但"改动没有引入文案回归"**没有被任何测试保护**——这正是 P2-3 能悄悄发生的原因。

### 2.5 第 5 项：AC5 scoped 表述

**证据链（全部在 `ff1778246` 工作树上，均未被本卡触碰）：**
1. `apps/desktop-avalonia/src/NewManga.App/Views/Pages.cs:1141-1155`：设置页 `SettingsPage` 构造 `Bindings = new ProviderBindingsSection(…)`；`:1451` 把它挂进「绑定」分栏；`Views/MainWindow.axaml.cs:117` 用 `new SettingsPage(settingsViewModel, …, _controller)` 把它作为「设置」页（`--shell=legacy` 的回滚路径仍随包发布）。
2. `Views/ProviderBindingsSection.cs`：`:68` `_scopeKind.ItemsSource = ProfileBindingScope.Kinds.ToList();`（Kinds = global/book/chapter，`SettingsProfileContracts.cs:103`）；`:89` 标签「Scope 类型（global / book / chapter）」；`:104-105` 显示 books/chapters 选择器。**这就是"按书/章配置 provider 的入口"。**
3. `tests/NewManga.App.Tests/SettingsProfileUiTests.cs:404-423`：明确把 scope 切到 `Book` 并断言 `binding.Scope.Kind == Book`、清除也是 Book；`ReaderSelectorUiTests.cs:65-208` 同样覆盖 book/chapter 选择。→ 有测试、有 UI、可操作。
4. **页面文案与事实相反**：`ProviderBindingsSection.cs:86`「把某个 provider profile 绑定到 (scope, capability) 槽位；**运行链会按槽位解析 provider**。book/chapter 范围用真实书库选择器。」——而 Core 的写入面明确写着只有 global 写扁平槽：`src/bootstrap/settings_commands.py:747-753`「只有 global binding 可以写它…book/chapter 只会骑在 run 的 `_p15_settings_snapshot` 上用于展示…写进去会让 book-scoped bind 悄悄劫持全局执行链」，`:782-787` 同理（clear）。执行链只读扁平槽：`src/infrastructure/providers/handlers.py:272,1164,1266`。
5. **卡面要求的标注不存在**：全 `src/**` grep 不到「仅全局」「不驱动执行」「不参与执行」；`ProviderBindingsSection` 与新文案里也没有。

⇒ AC5 的判定条件「若设置页允许按书/章配置 provider，**必须标注**『当前仅全局绑定驱动执行』」在本仓库**被触发**，而实现既没标注、还写了反向暗示；证据 README §2 的「设置页当前没有按书/章配置 provider 的入口（SettingsProfileContracts / 设置页只有全局 profile/binding）」与 `Pages.cs:1141`/`SettingsProfileUiTests.cs:408` 直接冲突。**FAIL（P1-3）。**
（补充精度：当前默认的 Fluent 设置页 `SettingsPageView` 的 Provider 组确实只有 profile/凭据、没有 scope；但"仍随包发布的 legacy 设置页"就是卡面说的"设置页"，且 V2 `ConsoleViewModel` 也有 book/chapter 的 `BindingScopeOptions`（`ConsoleViewModel.cs:1804-1823`）。"未提供"这个登记无论如何都需要改正。）

### 2.6 第 6 项：AC7 零契约面

```
$ git diff ff1778246^ ff1778246 --name-only
apps/desktop-avalonia/src/NewManga.App/Services/TranslateErrorText.cs          (A)
apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/WorkbenchViewModel.cs (M)
apps/desktop-avalonia/src/NewManga.App/Views/V2/Studio/Controls/StudioInspectorPanel.cs (M)
apps/desktop-avalonia/tests/NewManga.App.Tests/TranslateEntryUiTests.cs        (A)
verification/TRANS-ENTRY-UI/README.md                                          (A)
```
- `src/**`（Python Core）：**0 改动**（`git diff … -- src/` 空）。
- 冻结契约字节 / `doc/contracts/**` / `IHostController.cs` / wire 命令表：**0 改动**（文件未出现在 diff；`HostCommandRegistry.cs`、`IHostController.cs` 均未改）。
- `generate_api_inventory --check`：`IReaderProgressSink 1` + `IHostController 80` + `IRunController 6` = **87**，输出 `OK: rendered counts match FEA-C07 doc`，`EXIT=0`。
- `verify_pins`：`PIN AUDIT: PASS (all 18)`，`EXIT=0`。
- **口径说明**：题面写"是否只含 `apps/desktop-avalonia/**`"——严格说**不是**，还含 `verification/TRANS-ENTRY-UI/README.md`；但该路径在本卡 `allowed_paths` 与「证据计划」内，属合规证据文件，**不算越界**。结论仍 **PASS**。

### 2.7 第 7 项：实测数字

| 命令（工作目录 `G:\CODEX\New Manga`） | 结果 | 备注 |
|---|---|---|
| `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo -v q` | **已通过! 失败 0，通过 919，跳过 11，总计 930**（5 m 12 s），`EXIT=0` | 含本卡新增 4 例 |
| `dotnet test …/NewManga.CoreClient.Tests/…` | **失败 0，通过 182，跳过 26，总计 208**（23 s），`EXIT=0` | — |
| `dotnet test …/NewManga.Host.Tests/…` | **失败 0，通过 321，跳过 74，总计 395**（7 s），`EXIT=0` | 无 sidecar env 时的口径，与交付声明一致 |
| `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)`，`EXIT=0` | warnings：7 个非终态 Task；STATUS 3164 B/32 行；PLAN 6989 B/64 行（均与卡无关） |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/TRANS-ENTRY-UI.md` | `PASS (3 warnings)`，`EXIT=0` | — |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，`EXIT=0` | — |
| `python tools/generate_api_inventory.py --check` | `OK: rendered counts match FEA-C07 doc`；`EXIT=0` | 计数 **1/80/6=87** |

三套测试与四门禁的数字**与交付声明逐项一致**；交付声明的"13 红→0 红"中的"0 红"部分被复现，"13 红"部分不可回放（§2.2c）。**注意**：跑 CoreClient 测试追加了 `verification/FEA-09/logs/wire-redacted.ndjson` 一行（§0），这是测试副作用。

### 2.8 第 8 项：文案质量（不只看"互不相同"）

| 文案 | 用户能看懂吗 | 可执行下一步 | 问题 |
|---|---|---|---|
| 未配置 | 是 | 「设置 → Provider 与凭据」添加/启用 + 重启 | 好；路径真实存在（`SettingsViewModel.cs:114`、`SettingsPageView.cs:469`） |
| 401/403 | 是 | 更新 key + 重启；并明说重试无用 | 好 |
| 404/402 | 大概懂"模型名"与"额度" | **只说"请核对"，没说去哪里核对** | 夹带 `Core`（内部组件）；对普通用户 404/402 是陌生码；应补「设置 → Provider 与凭据」改 model、去服务商后台看额度（P2-4） |
| 429 | 懂"限流、稍等再试" | 重试 | 夹带 `意图键`、`Run`，普通用户无意义；未说等多久（P2-4） |
| 空章 | 懂"没页面" | 导入页面 | 没说导入在哪个页面/按钮；且同 VM 已有另一句「本章节暂无页面。」（`WorkbenchViewModel.cs:528-533`），两句并存不统一（P2-4） |
| 重启提示 | 懂 | 重启应用 | 只内嵌在"未配置"与"401/403"句里；设置页本身没有任何"改完要重启"的提示；`RestartHintShort` 声明了却未被任何代码引用（`TranslateErrorText.cs:41`）（P2-5） |
| AC6 检查器文案 | 开发者能懂，用户看不懂 | 无 | 把 `HostCommandRegistry:352 / core_service.py:4367` 与"不是「能力待接入」"这种**评审对话**写进了产品界面（`StudioInspectorPanel.cs:256`）；事实核对是对的（Host `:352`、Core `:4367`、handler `:4136` 均在），但应改成用户语言（P2-4） |

## 3. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| P1-1 | **P1** | `WorkbenchViewModel.cs:192-201, 224-226`；`HostController.cs:963-981` | 空章判定优先于**所有**失败码；而 `ListChapterPagesAsync` 在 Host 未就绪/读取失败时返回**空列表**。→ Host 未就绪，以及发生在空页/读失败章节上的其他失败（`HOST_READ_ONLY`、执行期 `PROVIDER_AUTH_FAILED` 等），都会被显示成「本章没有可处理的页面：请先导入页面…」，用户被引向错误操作；也让 DSH R-4②「失败文案已可读」失真 | 代码路径如上；`HostController.cs:967-970` 未就绪直接返回空；`FakeHostController.cs:1181-1190` 默认空。场景表见 §2.2 | 只在 `LastError ∈ {INVALID_REQUEST, INVALID_INPUT}` 时用空章句覆盖；页数判定改用**已加载的 `Pages`**（`LoadAsync:521-533` 已有），或让探测失败时保持"未知"（不覆盖）；保留"不阻断" | open |
| P1-2 | **P1** | `TranslateErrorText.cs` 仅被 `WorkbenchViewModel.cs:176,226` 引用；`FluentRunProjection.cs:260`；`WorkbenchPageView.cs:618`；`StudioBatchViewModel.cs:616-618`；`RunStatusMonitor.cs:344-367` | AC2 的四类只接到"StartRun 拒绝"路径；而 AUTH/429/4xx 只会在**执行期**出现（StartRun 只受理并返回 `run_id`：`core_service.py:6692-6720`）。用户实际看到裸码的两个面没有接入映射 → AC2"用户可见可区分"只完成一半 | 全仓 `TranslateErrorText` 引用点 grep 只有 2 处；矩阵 `ErrorCell` 原样渲染；`StepErrorText` 无 AUTH/INVALID_INPUT | 在 `FluentRunRow.ErrorCell` 用 `TranslateErrorText.ForCode(...)+"（code）"`（保留码可诊断）；或给 `StepErrorText` 补 AUTH/INVALID_INPUT；Studio drawer 同理。一行级改动 | open |
| P1-3 | **P1** | `Pages.cs:1141-1155,1451`；`ProviderBindingsSection.cs:68,84-99`；`SettingsProfileUiTests.cs:404-423`；`settings_commands.py:747-753,782-787`；证据 README §2 AC5 | 设置页**有** book/chapter 的 provider 绑定入口，却登记为"未提供"；且页面文案「运行链会按槽位解析 provider」与实测前置约束 3（只有 global 驱动执行）相反，卡面要求的「当前仅全局绑定驱动执行」缺失 → 用户会误以为按书配置生效。**本卡的核心风险点之一未处置** | 上述文件逐行可见；`SettingsProfileUiTests` 明确选了 Book | 在 `ProviderBindingsSection`（以及 Console 的 binding scope 提示）加「**当前仅全局绑定驱动执行**；book/chapter 绑定只用于展示/解析预览」；改掉「运行链会按槽位解析 provider」；更正证据 README 的 AC5 说法 | open |
| P2-1 | P2 | `TranslateEntryUiTests.cs:71-85`；`WorkbenchViewModel.cs:521` | 空章测试无判别力：`ChapterPageCalls` 已被 `LoadAsync` 填充；只断言常量包含自身子串；**不检查 `vm.Error`**。把实现回退成旧句，测试仍全绿；也没有 fail-open（resolve=null 放行）测试、没有"有页 + AUTH"映射测试 | 阅读 + 逻辑推演 | 断言 `vm.Error == TranslateErrorText.EmptyChapter`、`DoesNotContain("INVALID_REQUEST")`；计数探测次数（Load 后应 +1 或按建议移除探测）；补 `ResolveProviderBindingAsync → null` 时 `StartRunRequests` 非空的 fail-open 用例 | open |
| P2-2 | P2 | `TranslateErrorText.cs:49-52` | `ForCode(null)` 返回"还没有可用的翻译模型 Provider"，把"未知/无错误码"编造成"未配置"，与 402/404 的诚实原则冲突（真实 Host 失败路径都会 set code，故目前潜伏） | 代码一行 | 改为「启动失败（Host 未返回错误码）：请查看 Host 日志后重试」类文案 | open |
| P2-3 | P2 | `WorkbenchViewModel.cs:226`（替换掉旧句）；`StudioBatchViewModel.cs:1136-1155`；`HostController.cs:2732-2742` | **有页章节**上的非 provider 启动拒绝退化为「未知错误码」：`HOST_READ_ONLY`/`TARGET_NOT_FOUND`/`CANCELLED` 会显示 `XXX（未识别的错误码，请连同此码反馈）`；`HOST_NOT_READY` 则通常先被 AC3 覆盖成空章句（P1-1）——两条路都不可读。同仓 V2 Studio 对 HOST_READ_ONLY/未就绪已有可读句，两个控制面不一致；旧「批量 Run 未启动（code）；可重试…」不再出现且从未被测试保护 | grep + 两处映射对比 | 在 `TranslateErrorText` 补 HOST_READ_ONLY / HOST_NOT_READY / CANCELLED 等启动拒绝码（可复用 Studio 文案口径） | open |
| P2-4 | P2 | `TranslateErrorText.cs:31,35,38`；`StudioInspectorPanel.cs:256` | 文案质量：402/404 句没有"去哪里核对"的路径；429 句夹带 `意图键`/`Run`；空章句没给导入入口；检查器文案把源码 `file:line` 与"不是「能力待接入」"的评审语言写进用户界面 | §2.8 | 用户语言化；402/404 补「设置 → Provider 与凭据」与服务商后台；检查器改成"本页暂不支持直接编辑；请在区域检查器导入/写入人工译文"类表述（源码坐标移到注释） | open |
| P2-5 | P2 | `TranslateErrorText.cs:16,41`；Fluent `SettingsPageView` Provider 组 | AC4 只在"未配置/凭据失败"句里出现重启提示；**设置页**（用户改模型配置的地方）没有提示；`RestartHintShort` 声明后被引用 0 次（死代码） | `src/**` 内「重启」提示共 4 处：`TranslateErrorText` 常量 + 两句 + Studio 只读句；设置页 0 处 | 在设置页 Provider 组常驻一行重启提示；删掉或使用 `RestartHintShort` | open |
| P2-6 | P2 | `verification/TRANS-ENTRY-UI/README.md`；`doc/tasks/TRANS-ENTRY-UI.md` | 证据与流程：证据计划提到 `logs/`，实际只有 README（无原始测试/门禁输出）；README 的 AC5 与 §3 数字口径已核，但"四门禁 EXIT=0"无原始日志；任务卡 AC 复选框在 `ff1778246`/`a9591dc1b` 仍是 `[ ]`，`reviewer` 字段仍是 `null`（未登记本次独立审查）；交付记录 commit 晚于 reviewed head | `git ls-tree` 该目录只有 README；任务文件 AC 行与 front matter | 补 `logs/`（可复制的终端片段，带 EXIT 与 shell 头）；勾 AC 并在 DSH 侧登记 reviewer；README 更正 AC5 | open |

**P0：无。**（没有数据损坏、契约破坏或安全面问题。）

## 4. 验证记录

| 场景 | 命令 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| App.Tests | `dotnet test …/NewManga.App.Tests.csproj --nologo -v q` | win-x64, net9.0；代码 = `ff1778246`（HEAD=`a9591dc1b`，纯文档） | **PASS** 919/0/11（930），5 m 12 s | 本会话原始输出 |
| CoreClient.Tests | `dotnet test …/NewManga.CoreClient.Tests.csproj …` | 同上 | **PASS** 182/0/26（208），23 s | 同上；**副作用**：追加 `verification/FEA-09/logs/wire-redacted.ndjson` 一行 |
| Host.Tests | `dotnet test …/NewManga.Host.Tests.csproj …` | 同上；无 sidecar env | **PASS** 321/0/74（395），7 s | 同上 |
| 治理门禁（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | 同上 | **PASS**（3 warnings），`EXIT=0` | 终端输出 |
| 治理门禁（本卡） | `… check.ps1 -TaskPath doc/tasks/TRANS-ENTRY-UI.md` | 同上 | **PASS**（3 warnings），`EXIT=0` | 终端输出 |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 同上 | **PASS** 18/18，`EXIT=0` | 终端输出 |
| API 清单 | `python tools/generate_api_inventory.py --check` | 同上 | **PASS** `1/80/6=87`，`EXIT=0` | 终端输出 |
| 历史"13 红" | 无法回放（硬门版本未提交） | — | **NOT_RUN** | 机制证据见 §2.2c |
| 真实 Host 未就绪/只读场景的文案 | 静态推导（无 live Core env） | — | **NOT_RUN**（实现路径已读；未做 live 侧测试） | §2.2b 表 |

**证据纪律说明**：上述数字均为本会话实跑；`NOT_RUN` 项已注明原因，未用散文代替。

## 5. 结论、三点口径与返修建议

### 5.1 本卡能否收口

**不能。** 3 个 P1（P1-1 反向误诊、P1-2 AC2 半接线、P1-3 AC5 登记失真且缺关键标注）都落在本卡 AC 的正面要求上，且修复都在本卡 `allowed_paths` 内（`apps/desktop-avalonia/src/NewManga.App/**` 与 `verification/TRANS-ENTRY-UI/**`）。按模板「P0/P1 未解决不可批准」，**不给 approved**。

### 5.2 三点口径逐条回答

1. **AC3 的降级（不拦、只换文案）可接受吗？**
   **方向可以接受，当前实现不可以。** "不阻断"是对的（硬门会误伤、契约也无法区分"空/未知"）；但"探测无数据就给出确定的空章诊断"违反了同一原则。**必须**把空章句限定在 `LastError ∈ {INVALID_REQUEST, INVALID_INPUT}` 的失败上，并用已加载的 `Pages`/或区分"探测成功且为 0"作为依据；探测不可读时保持"未知"，不覆盖原错误。修完后这条口径可被 DSH 接受。
2. **AC1 的 fail-open 可接受吗？**
   **可以接受。** 证据：Host 就绪且没配 provider 时 Core 明确返回 `profile_id=null` 的对象，门会拦住（"未配置"不漏）；`null` 只在未知态出现，把它当"未配置"会误伤"已配置但 Host 未起"的用户，且区分二者要改契约，超出本卡。**前提**是 fail-open 的失败出口文案必须诚实——即先修 P1-1，并修 `ForCode(null)`（P2-2）。修完后 R-2 的口径成立。
3. **402/404 不区分可接受吗？**
   **完全可以接受，而且这是本次实现里最正确的一处。** wire 证据：`openai_client.py:10-19` 的 other-4xx → `INVALID_INPUT`，状态码不下发；文案把两种可能并列并明说"返回同一个错误码"，没有编造。建议只做两处小 polish：把"请核对"落到具体入口（设置/服务商后台），并考虑只对 `INVALID_INPUT` 使用此句（`INVALID_REQUEST` 留给空章/通用拒绝句）。

### 5.3 最小返修清单（建议 r2 前完成）

1. **P1-1**：`WorkbenchViewModel.cs:192-226`——空章覆盖仅限 `INVALID_REQUEST`/`INVALID_INPUT`，依据改用 `Pages`；探测不可读视为未知。
2. **P1-2**：把 `TranslateErrorText.ForCode` 接进执行期错误面（`FluentRunRow.ErrorCell` 至少；`StepErrorText`/Studio drawer 可选），并加一条测试断言"有页 + `PROVIDER_AUTH_FAILED` → 401/403 句"。
3. **P1-3**：`ProviderBindingsSection` 增「当前仅全局绑定驱动执行」并改正「运行链会按槽位解析 provider」；更正 `verification/TRANS-ENTRY-UI/README.md` 的 AC5 表述。
4. **P2-1/2-2**：补空章"用户可见文案"断言、fail-open 放行断言；`ForCode(null)` 改诚实未知句。
5. **P2-3/2-4/2-5**：补 HOST_READ_ONLY/未就绪/取消的启动拒绝文案；文案去内部术语、补路径；设置页常驻重启提示。

### 5.4 复审

修完后在新 head 上重新出 r2（本报告只对 `ff1778246` 有效；`a9591dc1b` 只是文档）。P2 项若 DSH 决定 defer，需在任务卡登记 disposition；**P1 三项不应 defer**。
