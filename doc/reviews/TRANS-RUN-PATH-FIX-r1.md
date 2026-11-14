---
task: TRANS-RUN-PATH-FIX
task_id: TRANS-RUN-PATH-FIX
reviewer: independent sub-agent (r1, read-only)
reviewer_agent: agent-6（由 lead 派发；独立上下文；未参与本卡实现/返修）
reviewer_kind: subagent
author: DSH（实施会话）
base_commit: f8a6185f9
reviewed_head: 652d7e7d0
verdict: approved
decision: approved
date: 2026-11-14
scope: read-only
---

# Review：TRANS-RUN-PATH-FIX（L1-T-B）r1

> **结论：`approved`。诊断成立并**推翻**既有记录；AC2 是零 wire 变更的最小可诊断性修复；AC3 语义正确；无 P0/P1；本卡**可以收口**。**
> 只发现 **4 项 P2（记录/证据文本准确性，不阻断）** 与 **4 项 P3（措辞与引用漂移）**，见 §5。
> 收口建议：closeout 前顺手更正 P2-1、P2-2 两处会被后续 Agent 当作基线的表述（纯文档，不需要重开范围、不需要动代码）。

## 0. 审查者、固定点与方法

- **身份**：`agent-6`，lead 派发的独立上下文子 agent；**只读**；**未参与** `TRANS-RUN-PATH-FIX` 的实现或返修。仓库内唯一新增文件是本报告；未 commit / 未 push / 未 checkout / 未改任何既有文件。
- **固定点**：`reviewed_head=652d7e7d0`（父 `c9cb3eeab`，pair 父 `64312e009`），只对该 head 有效。
- **复核期间的仓库事实（如实记录）**：
  - 复核开始时 HEAD = `652d7e7d0`；复核过程中 lead 推进了一个**纯文档**提交 `4b48d7ae1`（`doc/tasks/TRANS-RUN-PATH-FIX.md` +21 行，即交付记录与 DSH 裁决），`652d7e7d0` 仍是其祖先（`git merge-base --is-ancestor 652d7e7d0 HEAD` → 0）。本报告仍按指定的 `652d7e7d0` 审查；`4b48d7ae1` 的文档内容作为「交付记录」一并核对（P2-1 正出在这里）。
  - 工作树在我开始复核时只有 `M doc/tasks/TRANS-RUN-PATH-FIX.md`；该文件随后被 lead 提交。**当前**唯一 dirty 项是 `M verification/FEA-09/logs/wire-redacted.ndjson`（+1 行），这是跑 `.NET` 测试时既有证据写入器的**副作用**，不在本卡 diff 内，我未触碰。
- **方法**：逐行读 diff / 调用链 / 契约点；用 `assemble_production_core` + `CoreServiceServer` 直跑生产 Core；用冻结 **0.1.1 打包 sidecar**（`G:\CODEX\New Manga.workspace\artifacts\release\NewManga-0.1.1-win-x64\core-sidecar\core_service.exe`，2026-10-29 构建，**早于 AC2**）作「变更前」对照跑 stdio；在 `%TEMP%` 的 `src` 副本上做回退敏感性实验（仓库文件零改动）；实跑四类门禁与受影响 .NET 项目。
- **视角声明**：Architecture = executed（契约面/分层/错误面/wire 字节）；Verification = executed（逐项实跑）；Standards/Spec 未单独成轴（模板允许可选）。

## 1. 逐项结论

| # | 复核项 | 结论 | 一句话证据 |
|---|---|---|---|
| 1 | 根因是否成立（折叠点 / 通用文案 / 抛错点 / book vs chapter） | **PASS** | 折叠 `core_service.py:6821-6822` + 文案 `:6837`；生产抛点 `sqlite/pipeline.py:847-848`（记录引用的是同文案的内存孪生 `store.py:420-421`）；同一 Core 内 book scope 接受、空章 chapter scope 必拒，已实跑（§2） |
| 2 | 复现证据链能否重放 | **PASS**（我独立重放；但仓库**未提交**探针脚本与原始输出 → P2-4） | 同一 Host 形状帧打打包 0.1.1 与仓库 head：两边 `INVALID_REQUEST / "Run request is invalid"`，同一 `request_id` 下**响应行逐字节相同**；book-scope 直连形状被接受（拿到 `run_id`）（§3） |
| 3 | AC2 是否越界（wire 字节零变更） | **PASS** | diff 只增加一条 `print(...file=sys.stderr)`；0.1.1（变更前二进制）与 head 对同帧响应**逐字节相同**；`--check` `1/80/6=87`；pins 18/18；`doc/contracts/**` 0 改动（§4） |
| 4 | AC3 实现与解释 | **PASS（附 1 项 P3 测试缺口）** | 默认仍 `{"ocr":"manga-ocr"}`；有 translate 配置才追加；显式 `overrides.provider_bindings` 在 dispatcher 层**完全优先**；关闭口先于 translate 生效；无配置默认 JSON 逐字节不变（§4） |
| 5 | 测试真实性（回退必红？） | **PASS** | Python：副本删掉 print → **2 failed**（控制组 2 passed）；C#：4 例全部引用新成员，回退后**编译失败**（CS0117/CS7036），不可能绿；带冻结 sidecar 实跑 **4 passed / 0 skipped**（§5） |
| 6 | 实测（pytest / dotnet / 四门禁） | **PASS（README 的 Host 数字标错，P2-2）** | pytest **3564 passed / 10 skipped / 0 failed**；CoreClient 182/0/26、Host 351/0/44（**需** sidecar env；无 env 为 321/0/74）、App 915/0/11；四门禁全 EXIT=0（§6） |
| 7 | 零越界 | **PASS** | `git diff c9cb3eeab^ 652d7e7d0 --name-only` = 7 个文件，全部落在 `allowed_paths`；`doc/contracts/**` 0 改动；`doc/**` 0 改动（§3.4） |

## 2. 第 1 项：根因核实

### 2.1 折叠点与通用文案（成立）

`src/bootstrap/core_service.py`（head 行号）：

- `6808` `except PipelineError as error:` → `6809` `code = error.code` → `6821-6822`：
  ```python
  if code in {"EMPTY_TARGET_SELECTION", "TARGET_DELETED"}:
      code = "INVALID_REQUEST" if code == "EMPTY_TARGET_SELECTION" else "TARGET_NOT_FOUND"
  ```
- 文案表 `6836-6847`，其中 `6837` `"INVALID_REQUEST": "Run request is invalid"`；`6853` 用它建 envelope（**不带 details**）。
- `src/domain/tasks/models.py:150-156`：`PipelineError.__str__` = `"<CODE>: <detail>"`。

⇒ 记录里写的 `core_service.py:6810-6811` / 文案 `:6826` 是 **`64312e009`（pair 的父提交）** 的行号（我用 `git show 64312e009:...` 逐行核对过，实际就是 6810-6811 / 6826）；AC2 插入 11 行后整体下移到 **6821-6822 / 6837**。引用本身不算错，但已随修复漂移（P3-2）。

**关键推论成立**：任何 `PipelineError("INVALID_REQUEST", ...)` 与被折叠的 `EMPTY_TARGET_SELECTION` 在 wire 上**完全同形**（code/category/message/retryable 全同，无 details）。我实跑确认了这两种来源的响应 dict 逐字段相同（§3.2 的 C/D 两案），只有 stderr 能区分。

### 2.2 抛错点（结论成立，但记录引用的是生产链之外的孪生实现）

- **生产**：`PipelineService.create_run` → `self._catalog.expand(actual_scope)`（`src/application/tasks/service.py:271`），生产 catalog 是 `SqliteTargetCatalog`（我打印过 `type(core.pipeline._catalog)` = `SqliteTargetCatalog`）。
  - `src/infrastructure/sqlite/pipeline.py:817-832`：book scope `SELECT ... pages p JOIN chapters c ON c.chapter_id = p.chapter_id WHERE c.book_id = ?`；chapter scope `SELECT page_id FROM pages WHERE chapter_id = ?`；`847-848` `if not targets: raise PipelineError("EMPTY_TARGET_SELECTION", "scope expands to no active pages")`。
- **记录引用**：`src/application/tasks/store.py:413-421`（`InMemoryTargetCatalog.expand`，`420-421` 抛同一 code 与**逐字相同**的 detail）。两份实现语义一致（book 跨章 / chapter 只看本章 / 空集抛出）。
- ⇒ 根因结论**不受影响**（同 code、同文案、同语义）；但「真实异常来自 store.py」在**生产路径上不精确**，应指 `sqlite/pipeline.py:847-848`（P2-3）。这也解释了为什么我在生产 Core 上取到的 stderr 正是该 detail。

### 2.3 「book scope 能过、chapter scope 必拒」（与代码一致，并已实跑）

同一个生产 Core、同一本书（C1 无页 / C2 有 1 页）：

| 操作（同一进程内） | 结果 |
|---|---|
| `catalog.expand(book)` | `ok`，targets = `["pg-asym-1"]`（**展开到 C2 的页**） |
| `catalog.expand(chapter=C2)` | `ok`，targets = `["pg-asym-1"]` |
| `catalog.expand(chapter=C1 空章)` | `EMPTY_TARGET_SELECTION: scope expands to no active pages` |
| `StartRun translate_untranslated` + **book** scope + `translate` 绑定（直连探针形状） | **accepted**，`run_id=run-4456…` |
| `StartRun translate_all` + **chapter=C2（有页）** | **accepted**，`run_id=run-3b0c…` |
| `StartRun translate_all` + **chapter=C1（无页）**（Host 形状） | `INVALID_REQUEST / Run request is invalid`；stderr `[core.run] StartRun refused: EMPTY_TARGET_SELECTION: …` |
| `StartRun translate_all` + scope `{"kind":"chapter"}`（形状错） | **同一个** wire envelope；stderr 是另一个原因 `INVALID_REQUEST: scope does not match a frozen PipelineScope variant` |

**结论**：差别来自 **scope 语义**，与 `translate_all` / `translate_untranslated` 的**命令差异无关**——上表第 5 行用的是 Host 的 `translate_all` + chapter scope，只要该章**有页**就被接受。这一点比 README §0.3 的表述更强：命令差异不是变量，scope 是。

### 2.4 记录声称「已排除」的四项，我独立复核

| 被排除项 | 我的验证 |
|---|---|
| 打包/仓库 Core 版本漂移 | **成立**：0.1.1 打包 sidecar 与 head 对同一帧响应**逐字节相同**（§3.3） |
| Host payload 形状错位 | **成立**：dispatcher 构建 `{command, scope, overrides, idempotency_key}`（`HostCommandDispatcher.cs:1477-1539`），同一形状在章有页时被接受（§2.3 第 5 行） |
| 协议 minor 不匹配 | **成立**：minor 3 与 7 结果相同（仓库 Core 与打包 sidecar 各跑一遍，均同 envelope） |
| `provider_profiles` 在 minor 3 被拒 | **成立**：`core_service.py:6702-6703` 只在 overrides 里出现该键时拒绝；App 不注入（`RunStartRequest.Overrides=null` → `RunContracts.StartRun` 不写 overrides），且我「去掉 overrides」实跑结果不变 |

**唯一的诚实保留**：2026-11-12 那次原始失败**没有留档 stderr**（当时运行的 0.1.1 sidecar 根本没有 `[core.run]` 行，见 §3.3 的 stderr 内容），所以这是「唯一存活且可复现的机制」，不是现场日志复放。但这不影响可动作结论：无论那次的具体触发是「选中的章为空」还是别的目标级拒绝，AC2 的可诊断性修复都是正解。

## 3. 第 2、3、7 项：证据链重放与越界

### 3.1 我重放的帧（与 `HostCommandDispatcher` 产出形状一致）

```json
{"protocol":"new-manga.core","version":{"major":2,"minor":3},"request_id":"<id>","command":"StartRun",
 "payload":{"command":"translate_all","scope":{"kind":"chapter","chapter_id":"<cid>"},
            "overrides":{"provider_bindings":{"ocr":"manga-ocr"}},"idempotency_key":"<key>"}}
```

### 3.2 两个 Core、同一形状帧（重放 README §0.1）

| 场景 | 打包 0.1.1 sidecar（stdio） | 仓库 head Core（in-process） |
|---|---|---|
| chapter 空章，minor 3 + overrides | `INVALID_REQUEST` / `Run request is invalid` / validation / `retryable:false` | 同左 |
| chapter 空章，minor 7 + overrides | 同左 | 同左 |
| chapter 空章，minor 3 **无** overrides | 同左 | 同左 |
| stderr | **无** `[core.run]`（0.1.1 无此代码） | `[core.run] StartRun refused: EMPTY_TARGET_SELECTION: EMPTY_TARGET_SELECTION: scope expands to no active pages` |

### 3.3 wire 字节零变更（关键证据）

用**同一个 `request_id`**（`byte-check-2`）分别打打包 0.1.1 与仓库 head，响应行（compact JSON）**逐字节相同**：

```
{"protocol":"new-manga.core","version":{"major":2,"minor":3},"request_id":"byte-check-2","result":null,
 "error":{"code":"INVALID_REQUEST","category":"validation","message":"Run request is invalid","retryable":false}}
```

`dict_equal=true`、`error_envelope_equal=true`、`byte_identical=true`。因为 0.1.1 二进制**构建于 AC2 之前**，这条对照直接证明 AC2 没有改动任何 wire 字节（错误码、文案、category、retryable、结构、version 全同）。

### 3.4 越界检查

```
git diff c9cb3eeab^ 652d7e7d0 --name-only
apps/desktop-avalonia/src/NewManga.CoreClient/Commands/RunBindingDefaults.cs
apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/RunBindingFixTests.cs
src/bootstrap/core_service.py
tests/core/test_trans_run_path_fix.py
verification/TRANS-RUN-PATH-FIX/README.md
verification/TRANS-RUN-PATH-FIX/logs/gates.log
verification/TRANS-RUN-PATH-FIX/logs/pytest-full.log
```

7 个文件全部命中 `allowed_paths`（`apps/desktop-avalonia/src/NewManga.CoreClient/Commands/**`、`apps/desktop-avalonia/tests/**`、`src/bootstrap/**`、`tests/**`、`verification/TRANS-RUN-PATH-FIX/**`）。`doc/contracts/**` = **0** 改动；`doc/**` = **0** 改动；无新 wire 命令、无新 `IHostController` 成员（inventory 计数未变，§6）。

## 4. 第 3、4 项：AC2 与 AC3

### 4.1 AC2（`core_service.py:6810-6820`，head 行号）

```python
print(f"[core.run] {command} refused: {error.code}: {error}", file=sys.stderr)
```

- 位置正确：在 `code` 折叠**之前**执行，所以 `error.code` 保留精确原因；`command` 是该 handler 的 `command` 形参（同函数 `6866` 也在用），`sys` 已导入（`:174`），不会 `NameError`。
- 触发面是**全部** Run 命令的 `PipelineError`（不仅折叠码），对 `IDEMPOTENCY_KEY_REUSED` 等也会打一行——纯 stderr，无副作用。
- **Host 确实捕获 stderr**：`NewManga.CoreClient/Transport/SidecarProcess.cs:421-451` `PumpStderrAsync`（tail 200 行 + append 到 `Spec.StderrLogPath`），所以这行会落进 Host 日志。选型正确。
- **无敏感信息**：run 路径上没有带路径的 `PipelineError` detail（grep `PipelineError(...path` 无命中）；detail 是 code / page_id 一类不透明 id。与既有 `_lineage_error_envelope`（`core_service.py:987-992` 的 `[core.lineage] refused:`）是同一先例。
- **格式瑕疵**：实跑输出是 `[core.run] StartRun refused: EMPTY_TARGET_SELECTION: EMPTY_TARGET_SELECTION: scope expands to no active pages`——code 重复了一次（`{error.code}` 与 `str(error)` 已含 code）。README 写的格式是 `<CODE>: <detail>`，实际是 `<CODE>: <CODE>: <detail>`（P3-1，纯日志可读性）。

### 4.2 AC3（`RunBindingDefaults.cs:42-71` + dispatcher 层）

| 要求 | 结论 | 证据 |
|---|---|---|
| 默认仍 `{"ocr":"manga-ocr"}` | **成立** | `DefaultJson` 未变（`:34`）；`Resolve` 在 `configured == null` 且无 translate 配置时走 `Parse(DefaultJson, ...)`（`:61`），`ResolveJson()` 返回 `GetRawText()` 原字节；既有测试 `RunBindingFixTests.cs:38` 断言 `{"ocr":"manga-ocr"}`，我的 env-clean CoreClient 运行 182 绿 |
| 有 translate 配置时追加 | **成立** | `:55-59`，值用 `JsonSerializer.Serialize` 转义（`:42-43`，不手拼 JSON）；`DefaultJsonWithTranslate` 输出 `{"ocr":"manga-ocr","translate":"<id>"}` |
| 显式 `overrides.provider_bindings` 永远优先 | **成立** | `HostCommandDispatcher.cs:1506` `userBindings is null ? Resolve() : null`；`:1527-1536` 显式绑定写出、默认只在 else 分支 → **不合并、不覆盖**；`RunContracts.cs:431-447` 同语义（PreparedRun 与 StartRun 一致，满足 R-004） |
| `NEWMANGA_RUN_PROVIDER_BINDINGS` 关闭口保留 | **成立** | `:52-71`：只要该 env 存在（含 `""`/`off`/`none`/`disabled`/`0`），**直接返回**，根本不读 translate env；`:80-91` `IsDisabled` |
| 无配置时默认 JSON 逐字节不变 | **成立** | 走 `Parse(DefaultJson)` 原路径；`DefaultJson` 字面量未改动；dispatcher 用 `defaults.Value.WriteTo(writer)`（与修复前同一写法） |

补充（与 DSH R-2 约束一致）：生产代码里 `Resolve()` **没有**传 `translateProviderId`（所以 translate 值只来自 `NEWMANGA_RUN_TRANSLATE_PROVIDER`），`RunContracts.PrepareRunOverrides` 同样是 `Resolve()`——「值来自当前 binding」留给 T-C，与裁决一致，不是本卡越界。

**缺口（P3-4）**：没有「`NEWMANGA_RUN_TRANSLATE_PROVIDER` 已设 + `NEWMANGA_RUN_PROVIDER_BINDINGS=off`」的组合测试。行为由代码直读可保证（早返回），但没被测试钉住。

## 5. 第 5 项：测试真实性（回退必红）

### 5.1 Python（`tests/core/test_trans_run_path_fix.py`，2 例）

非破坏性回退实验：把 `src` 复制到 `%TEMP%\tb-revert\src`、复制测试文件到同一结构的 `tests/core/`，在**副本**里删掉那 11 行 print（仓库文件零改动）：

| 组 | 命令 | 结果 |
|---|---|---|
| 控制组（副本未改） | `python -m pytest -q tests/core/test_trans_run_path_fix.py` | **2 passed**，EXIT=0 |
| 回退组（副本删 print） | 同上 | **2 failed**，EXIT=1。失败断言分别是 `assert "[core.run]" in stderr`（`:83`）与 `assert "scope does not match a frozen PipelineScope variant" in stderr`（`:100`，实际 stderr 为 `''`） |

**必然性论证**：全仓 `[core.run]` 只出现在 `src/bootstrap/core_service.py:6818` 一处（grep 确认），`PipelineError.__str__` 不含该标记，故 print 一旦回退，两条断言必红。**判别力真实**。

### 5.2 C#（`TransRunPathFixTests`，4 例）

- 两例 unit（`:657`、`:668`）直接调用 `ResolveJson(translateProviderId: …)` / `Resolve(translateProviderId: …)`；两例 sidecar（`:677`、`:709`）引用 `RunBindingDefaults.TranslateProviderVariable` 常量。**回退到 `652d7e7d0` 之前的 `RunBindingDefaults` 后，这 4 例连编译都过不去**（新成员/新参数不存在），因此不可能「假绿」。
- 实测：`--filter TransRunPathFixTests`
  - 无 sidecar env → **2 passed / 2 skipped**（`SidecarFactAttribute` 显式 Skip，不是假绿；见 `SidecarFactAttribute.cs:9-17`）；
  - `NEWMANGA_CORECLIENT_SIDECAR_DIR` 指向冻结 0.1.1 → **4 passed / 0 skipped**（与实施者声明一致）。
- 两例 sidecar 用例的判别点是真的：`InjectsTranslate` 断言**出站 frame** 含 `\"provider_bindings\":{\"ocr\":\"manga-ocr\",\"translate\":\"openai-compatible-translation\"}`；`KeepsExplicitUserBindings` 断言出站 frame 只含用户绑定、且 `DoesNotContain("manga-ocr")` / `DoesNotContain("openai-compatible-translation")`——是「流程层优先级」而不是只测常量。

## 6. 第 6 项：实测记录（本审查者实跑，2026-11-14）

| 项 | 命令 | 结果 |
|---|---|---|
| 定向 pytest | `C:\Python314\python.exe -m pytest -q tests/core/test_trans_run_path_fix.py` | **2 passed**，EXIT=0 |
| 全量 pytest（第 3 次、分离流） | `python -m pytest -q` | **3564 passed, 10 skipped, 0 failed**，320.38s，EXIT=0（另两次全量也是 EXIT=0） |
| CoreClient.Tests | `dotnet test …/NewManga.CoreClient.Tests.csproj` | **182 通过 / 0 失败 / 26 跳过**（总 208），EXIT=0 |
| Host.Tests（裸环境） | 同上（无 `NEWMANGA_CORECLIENT_SIDECAR_DIR`） | **321 / 0 / 74**（总 395），EXIT=0 |
| Host.Tests（带冻结 sidecar） | `$env:NEWMANGA_CORECLIENT_SIDECAR_DIR=<0.1.1 core-sidecar>` | **351 / 0 / 44**（总 395），EXIT=0 |
| App.Tests | `dotnet test …/NewManga.App.Tests.csproj` | **915 / 0 / 11**（总 926），EXIT=0 |
| `check.ps1`（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | PASS（3 warnings），EXIT=0 |
| `check.ps1 -TaskPath` | `… -TaskPath doc/tasks/TRANS-RUN-PATH-FIX.md` | PASS（3 warnings），EXIT=0 |
| `verify_pins` | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，EXIT=0 |
| `generate_api_inventory --check` | `python tools/generate_api_inventory.py --check` | `OK: rendered counts match FEA-C07 doc`，IHostController **80** / IRunController **6** / 合计 **87**（1/80/6=87），EXIT=0 |

（`NEWMANGA_CORECLIENT_SIDECAR_DIR` / `NEWMANGA_RUN_TRANSLATE_PROVIDER` / `NEWMANGA_RUN_PROVIDER_BINDINGS` 在裸环境运行前均为空，已逐项确认；未用「设 env 跑全量」的方式制造假红。）

## 7. 第 7 项：越界

见 §3.4。结论：**7 文件全在 `allowed_paths`，`doc/contracts/**` 0 改动，无新契约面**。

## 8. Findings

### P0

无。

### P1

无。

### P2（记录/证据文本准确性，不阻断）

1. **P2-1 交付记录把 AC2 归错提交**。`doc/tasks/TRANS-RUN-PATH-FIX.md`（`4b48d7ae1`）写「**修复（`652d7e7d0`）** — AC2：折叠前把精确原因写 stderr」，但 `git log --oneline -S'[core.run]' -- src/bootstrap/core_service.py` 只命中 **`c9cb3eeab`**（诊断提交，`core_service.py` +11 行）；`652d7e7d0` 的 stat 只有 `RunBindingDefaults.cs` + `RunBindingFixTests.cs` + README。`verification/…/README.md`（在 `c9cb3eeab` 里）反而记对了。属记录串位：读提交信息的人会以为 AC2 在第二个提交里。建议 closeout 时改成「诊断提交携带 AC2 的 stderr 变更 + 回归测试；修复提交只含 AC3」。
2. **P2-2 Host.Tests 基线数字标注错误**。README §2 写「.NET（**不带 sidecar 环境变量**的仓库基线）：… Host.Tests **351 / 0 / 44**」。我实测：无 env = **321 / 0 / 74**；带 0.1.1 sidecar = **351 / 0 / 44**（总数 395 两边相同，差的 30 个是 `SidecarFact` 自跳过）。数字本身是真的，**标签是错的**。CoreClient 182/0/26 与 App 915/0/11 我复现一致（这两项确实是无 env 基线）。
3. **P2-3 AC1 的抛错点引用不是生产实现**。记录写「真实异常来自 `src/application/tasks/store.py:413-421`」；生产 `assemble_production_core` 用的是 `SqliteTargetCatalog`，抛在 `src/infrastructure/sqlite/pipeline.py:847-848`。两者 code 与 detail **逐字相同**，结论不变；但 AC1 要求「文件:行」，指向测试用内存实现会误导后续排障。
4. **P2-4 诊断证据不可逐字重放**。`verification/TRANS-RUN-PATH-FIX/` 只有 `README.md` + `logs/gates.log` + `logs/pytest-full.log`；README §0 描述的探针（Host 形状帧 × 两个 Core、data-root 建书建章）**没有提交脚本，也没有原始输出**。我用 30 行等价脚本独立重放成功（§3），所以是「证据包完整性」而非「结论不可信」。建议把探针与原始 stdout/stderr 落盘（T-C 可复用）。

### P3（措辞/引用漂移）

1. **P3-1** stderr 行重复 code：`refused: EMPTY_TARGET_SELECTION: EMPTY_TARGET_SELECTION: scope expands…`（`{error.code}` + `str(error)`）。改成 `{error.detail}` 或去掉前缀即可；README 的格式串也要同步。
2. **P3-2** 行号引用随修复漂移：`core_service.py:6810-6811` / `:6826`（现为 `6821-6822` / `6837`）；`tests/core/test_trans_run_path_fix.py:7` 的 docstring 同样写旧行号。
3. **P3-3** `WorkbenchViewModel.cs:14,172-176` 应为 `apps/desktop-avalonia/src/NewManga.App/ViewModels/**Fluent**/WorkbenchViewModel.cs`（仓库里有同名文件在 `ViewModels/` 下）。
4. **P3-4** 缺「translate env + `NEWMANGA_RUN_PROVIDER_BINDINGS=off` 同时」的测试；行为由 `Resolve` 的早返回保证，但未被钉住。

### 观察（非缺陷，供 DSH 处置）

- 原始 2026-11-12 失败**无 stderr 留档**（0.1.1 无该行），因此本诊断是「唯一存活且可复现的机制」，不是现场复放。若 T-C 加 Host 前置探测，建议同时把 `[core.run]` 行纳入 Host 持久诊断日志（`SidecarProcess` 已 append 到 `StderrLogPath`，无需改代码）。
- 复核期间 `verification/FEA-09/logs/wire-redacted.ndjson` 被 .NET 测试写入 +1 行（既有证据写入器副作用）；与本卡 diff 无关，我未修改。

## 9. 明确回答两个问题

**① 这个诊断是否推翻了既有记录？——是。**

既有记录（`REAL-TRANSLATE-PROVIDER-1/REPORT.md:75,80`：Host `library_start_run` 返回 `INVALID_REQUEST`，「Core 直连同 payload 可接受」，指向 Host dispatcher 差异）被三条独立证据推翻：
1. **形状合法**：与 Host 完全相同的帧形状，在章**有页**时被同一 Core 接受（§2.3 第 5 行，`translate_all` + chapter + 默认 ocr 绑定 → `run_id`），所以问题不在 payload 形状；
2. **不是版本漂移**：0.1.1 与 head 对同一帧响应**逐字节相同**（§3.3）；
3. **不是 minor/overrides**：minor 3/7、有/无 overrides 结果一致（§3.2）。

真实机制是 **scope 语义**（book 可跨章展开 / chapter 只看本章）+ **`EMPTY_TARGET_SELECTION → INVALID_REQUEST` 折叠** + 通用文案。旧记录说的「同 payload」确实不是同一 payload：探针是 `translate_untranslated` + book scope（`run_translate_probe.py:166,197-208`），Host 是 `translate_all` + chapter scope（`ViewModels/Fluent/WorkbenchViewModel.cs:14,172-176`）；但更精确的说法是——**变量是 scope，不是 command**（§2.3 已证 `translate_all` + 有页章节同样成功）。

**② 本卡能否收口？——可以收口。**

- 无 P0/P1；代码改动零越界、零 wire 字节变更、零新契约面；四门禁与受影响 .NET/全量 pytest 全绿；两边回归测试都有真实判别力（回退必红）。
- AC1 的「先诊断后修」在事实层面成立：诊断结论可独立重放，修复是最小且不越冻结错误面的动作。
- 收口前提只是**文档卫生**：建议 closeout 时顺手改掉 P2-1（AC2 归属提交）与 P2-2（Host 基线数字的 env 标注）——这两条会被下一个 Agent 当作基线读；P2-3/P2-4 建议在 T-C 一起补（生产抛点引用 + 探针/原始输出入库）。这些都是记录层修正，**不需要重开本卡范围，也不需要动代码**。
- 产品债（用户仍看到通用文案；Host 默认 translate 值须来自当前 binding）已按 DSH R-1/R-3 登记进 T-C，本卡不因这两条阻塞。

## 10. 重放方法（供 DSH 复跑）

```powershell
# 0) 冻结 sidecar（变更前二进制，用作 wire 字节对照）
$sidecar = 'G:\CODEX\New Manga.workspace\artifacts\release\NewManga-0.1.1-win-x64\core-sidecar'

# 1) 定向测试
C:\Python314\python.exe -m pytest -q tests/core/test_trans_run_path_fix.py
dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj --filter TransRunPathFixTests
$env:NEWMANGA_CORECLIENT_SIDECAR_DIR=$sidecar
dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj --filter TransRunPathFixTests   # 4/0/0
Remove-Item Env:NEWMANGA_CORECLIENT_SIDECAR_DIR

# 2) 门禁
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/TRANS-RUN-PATH-FIX.md
pwsh -NoProfile -File tools/governance/verify_pins.ps1
C:\Python314\python.exe tools/generate_api_inventory.py --check
```

复现脚本（本审查者用的一次性版本，位于仓库外 `%TEMP%`，未入库）：`tb_review_repro.py`（两 Core × 三帧）、`tb_asym_probe.py`（book/chapter 不对称 + 四处 stderr）、`tb_byte_check2.py`（同 `request_id` 的逐字节对照）。要点：`assemble_production_core(tmp/"data")` 建根 → `core.library.create_book/create_chapter` → 需要页时直接 `INSERT INTO pages(..., source_hash, managed_original_ref, ...)`（与 `tests/pipeline/test_pipeline_production_seam.py:61-66` 同形）→ `CoreServiceServer(core).dispatch_request(json.dumps(frame))`；sidecar 侧用 `CreateBook`/`CreateChapter`（minor **8**）建数据，再发同形 `StartRun`。
