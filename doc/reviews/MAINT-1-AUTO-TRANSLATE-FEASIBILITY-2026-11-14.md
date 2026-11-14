# 自动翻译功能：可行性与契约面评估（MAINT-1）

- 评估日期：2026-11-14
- 评估范围：`G:\CODEX\New Manga`（Windows / Avalonia / Python Core / AD-002）
- 评估方式：**只读**静态审查 + 引用既有证据；**未**修改 `src/**`、`apps/**`、`tests/**`、`doc/plan/**`、`doc/contracts/**`；**未**发起任何真实网络调用；**未**执行 git 写操作。
- 唯一产出：本文件。
- 结论证据口径：源码 `文件:行` 优先；运行事实引用已有 `verification/**`（本评估不重复跑）。

---

## 0. 结论先行

**条件可行 —— 而且是最便宜的一类可行：零冻结契约改动、零 UNFREEZE、零 pin 变更。**

一句话理由：从「UI 按钮」到「真实模型」的**运行时链路已经存在并在 wire 上可用**，自动翻译就是 `StartRun(command=translate_all|translate_selected|translate_single)`（`src/bootstrap/core_service.py:397-401, 6692-6715`；`apps/desktop-avalonia/.../WorkbenchViewModel.cs:13-14, 157-204`），且已用真实 provider 跑通过（`verification/REAL-TRANSLATE-PROVIDER-1/REPORT.md:43-48`：真实 HTTP 429 → `PROVIDER_RATE_LIMITED`，`PROVIDER_NOT_CONFIGURED` 为 0）。真正的缺口不在 wire，而在**配置桥**：Settings 里保存的 Provider profile / 能力绑定（P15 JSON store）**从不写入** Run 运行期读取的 `pipeline_defaults.settings["providers"]` 镜像，因此 `translate` 步骤拿不到 binding，会停在 `PROVIDER_NOT_CONFIGURED`。

三个必须补齐的条件（都不是契约问题）：

| # | 缺口 | 位置 | 性质 |
|---|---|---|---|
| G1 | P15 profile/binding → Run 侧 `settings.providers` 镜像无生产写入方 | `src/infrastructure/providers/runtime.py:182-193`（只读 `settings["providers"]["profiles"]`）vs `src/bootstrap/settings_commands.py:590-670`（只写 JSON profile/binding store） | Core 代码缺口 |
| G2 | Host 默认 StartRun 只注入 `{"ocr":"manga-ocr"}`，无 translate | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/RunBindingDefaults.cs:23` | Host 代码缺口（1 行常量级别）+ 依赖 G1 |
| G3 | Host `library_start_run` 对冻结 Core 曾返回 `INVALID_REQUEST`（隔离根 + REPACK-2 sidecar） | `verification/REAL-TRANSLATE-PROVIDER-1/REPORT.md:75, 80` | 遗留缺陷，未定位 |

---

## 1. Core 侧能力现状：翻译运行时**已实现**，但不是「翻译 service」

### 1.1 `src/application/translation/**` 里有什么、没有什么

目录实地清单（`Get-ChildItem src\application\translation -Recurse -File`）只有：`color/`、`context/`、`inpaint/`、`knowledge/`、`pipeline/`。

- **没有** `translation/service.py` 之类的「翻译一个 region / 一个 Context Group」应用服务；唯一的 `service.py` 是 `src/application/translation/color/service.py`（源样式，不是翻译）。
- **没有** 应用层重试与落库编排。`src/application/translation/pipeline/executor.py:29` 的 `DeterministicStepExecutor` 是**测试用**确定性执行器（文件头 `:1-6` 自述「deliberately boring and dependency-free」），不接 provider。

### 1.2 真正的翻译编排在 application 层存在，但**没有生产调用方**

| 函数 | 位置 | 作用 | 生产调用方 |
|---|---|---|---|
| `execute_translate_step` | `src/application/translation/context/step.py:162-202` | SFX 门控 → 组 Context Bundle → 组装请求 → 调 provider → 输出映射回 primary region（AC-TRANS-003） | **无**（全仓仅 `src/application/translation/context/__init__.py:7` re-export + `tests/knowledge/test_translate_step.py:11`） |
| `build_provider_request` | 同文件 `:81-139` | 组装 `TranslationRequest`（prompt/术语表/TM/`do_not_translate`/`region_types`） | 同上 |
| `map_provider_output` | 同文件 `:142-159` | 越界/缺失输出即失败，不静默修补 | 同上 |

结论：**「按 Context Group 编排翻译」这一个能力在 application 层是完整可用的纯函数，但被生产路径绕过了**。

### 1.3 生产路径：Run 框架 + infrastructure handler（真实落库、真实重试）

翻译在运行时是**Step**，不是独立 service：

| 关注点 | 实现 | 位置 |
|---|---|---|
| 步表注册 | `(STEP_TRANSLATE, self.handle_translate)` | `src/infrastructure/providers/handlers.py:228` |
| 单 region 翻译编排 | `handle_translate`（一个 PlanUnit = 一个 region） | `handlers.py:597-710` |
| 上下文页（前置/后置页文本） | `_context_pages` | `handlers.py:1276-1310` |
| 术语表 | `_glossary` | `handlers.py:1312-1316` |
| provider 链与「未配置」失败 | `_chain` → `ProviderNotConfigured` | `handlers.py:1266-1274` |
| **失败重试** | `run_chain` + `RetryPolicy(max_attempts=3, backoff=1.0s 线性)` | `handlers.py:655-660`；`src/infrastructure/providers/retry.py:26-49`；`fallback.py:101-143` |
| **结果落库** | `region_writer.prepare_machine_translation(...)` | `handlers.py:676-690`；`src/infrastructure/providers/step_writes.py:122` |
| 请求冻结（防中途变更） | `freeze_request` / `translate_frozen` + payload digest 一致性校验 | `handlers.py:639-668`；`src/infrastructure/providers/translation_openai.py:77-107` |

### 1.4 `src/bootstrap/core_service.py` 里的「翻译运行时」

`core_service.py` **没有任何翻译专用 handler**。它在翻译面的角色只有三种：

1. Region 写面：`save_manual_translation`（人工译文保存，**不是**自动翻译）——`core_service.py:4136-4174`，dispatch `:4367`。
2. Run 面：`StartRun` 把 `CommandType` 交给 `application/tasks`（`:6692-6715`）。
3. 设置面：`settings.update_section` 写 `pipeline_defaults`（`:3061-3114`）。

任务规划来自 `src/application/tasks/service.py`：

```text
_COMMAND_STEPS[TRANSLATE_ALL / TRANSLATE_UNTRANSLATED / TRANSLATE_SELECTED /
               TRANSLATE_SINGLE / RETRANSLATE_REGION_FULL] = _FULL_TRANSLATION
_FULL_TRANSLATION = (ocr, color, term_extract, translate, segment, mask_refine, inpaint, render)
_RETRANSLATE_REGION 的步集 = (translate, render)
```
证据：`src/application/tasks/service.py:93-105, 109-128`；SFX 门控步集 `:153-159`。

**Q1 结论**：翻译运行时**已实现**（Run + infrastructure handler + 真实落库 + 真实重试），缺的不是「翻译 service」，而是**把配置接到这个运行时上的那一段**。

---

## 2. wire 面：翻译相关命令清单（区分手动保存 vs 自动翻译）

### 2.1 逐条清单

| 类 | 命令 | 命令族 / per-command minor | 证据 |
|---|---|---|---|
| 手动保存 | `save_manual_translation` | Region 写族，minor **3** | `core_service.py:559-570`（`_REGION_WRITE_COMMANDS`）、`:4367`、`:4136` |
| 手动确认 | `confirm_region_final` | Region 写族，minor **3** | `core_service.py:4176`、`:4369` |
| 文本读面 | `list_page_region_texts`（返回 `translated_text`/四级文本） | Region 读族，minor **3** | `core_service.py:88-105, 7803`；Host `HostCommandRegistry.cs:191, 357` |
| **自动翻译（既有唯一入口）** | `StartRun`，`command ∈ {translate_all, translate_untranslated, translate_selected, translate_single, retranslate_region, retranslate_region_full}` | Run 族：`StartRun` 走 **minor 3**；`PrepareRun/AcceptRun` 走 **12** | `core_service.py:397-401`（`_RUN_COMMANDS`）、`:6695-6696`（`COMMAND_CATALOG` 校验）、`src/domain/tasks/models.py:67-82, 87` |
| 运行投影 | `GetRunSnapshot` / `GetTaskProjection` / `RetryFailedTargets` / `ControlRun` | Run 族，minor 3 | `core_service.py:397-401` |
| Provider 配置（翻译能力相关） | `settings_provider_profiles_*` / `settings_provider_bindings_*` / `BindProfileCredential`（capability `"Translation"`） | P15 族，minor **7** | `core_service.py:472-489`；`src/bootstrap/settings_commands.py:32-39` |

**所以「Host 命令表里翻译相关只有 `save_manual_translation`」这一已知事实，严格说是「翻译**专用**命令只有 `save_manual_translation`」；自动翻译能力实际挂在 `StartRun` 这个通用 Run 命令上，Host 侧绑定为 `["library_start_run"] = new("StartRun", 3)`（`HostCommandRegistry.cs:284`）。**

### 2.2 若要新增「自动翻译」命令：属于哪个族、minor 怎么定

仓库里 per-command minor 的既有判定惯例（逐条可查）：

| 情形 | 先例 | minor 结论 |
|---|---|---|
| 同族**增量命令**、零既有语义变化 | `_REGION_WRITE_COMMANDS` 十命令 + `list_page_region_texts`（`core_service.py:552-570`；`doc/contracts/V11R_REGION_WRITE_CONTRACT.md`） | **不 bump**，沿用该族 minor（Region = 3） |
| 纯**可选字段**扩展、零新命令 | `ListRegions` 1.5 additive widening（`core_service.py:305-311`） | **不 bump** |
| 独立**新命令族** | 删除预览 = 11、回收站 = 13（`core_service.py:328-334`） | **新族新 minor**（`_TRASH_PROTOCOL_MINOR` 等） |
| 「commands added」进入共享面 | `PROTOCOL_MINOR=3` 的历次 bump 注记（`core_service.py:302-323`） | 历史上「加命令 = bump」，但 V11R 起已改为「同族增量不 bump」 |

**判断**：IF 未来确需一条 `translate_*` 命令，**最贴合的形状是「Region 写族 / Run 族的同族增量」→ 沿用 minor 3**；只有把它做成独立命令族（例如带自己的生命周期与错误闭集）才需要新 minor + M2-C1 修订。**但本评估的结论是：不需要新增命令**（见 §4）。

### 2.3 未知命令的既有行为（新增命令必须知道）

`core_service.py:8280-8298`：未知命令返回 typed `UNKNOWN_COMMAND`（category=validation, retryable=false），不做静默降级。冻结旧 Core 遇到新命令按此 fail-closed。

---

## 3. Host 面：注册机制与「加一条命令」的改动清单

### 3.1 注册机制（命令 → minor → 域 → 是否 UI-facing）

三层，全部在 `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/`：

1. **名字数组（域名）**：`HostCommandRegistry.cs:168-192`（`RegionNames`）、`:110-145`（`SettingsNames`）、`:219-233`（`WorkbenchNames`）等；域枚举 `HostCommandModel.cs:5-16`（`Settings/Library/Region/Reader/Resource/Workbench/Drafts/SourceSync`）。
2. **协议绑定（命令 → Core 命令名 + minor）**：`HostCommandRegistry.cs:237-367` 的 `CoreBindings` 字典，`CoreBinding(CoreCommand, Minor)`（`HostCommandModel.cs:36-46`）。例：`["save_manual_translation"] = new("save_manual_translation", 3)`（`:352`）、`["source_resync"] = new("ResyncSource", 3)`（`:251`）。
3. **通道判定（是否 UI-facing / 走哪条通道）**：`BuildCommands()` / `AddDomain()`（`:540-624`）按 `CoreBindings → BridgeBindings → HostLocalBindings` 的顺序决定 `HostCommandChannel`（`CoreService` / `CoreHostControl` / `HostLocal` / `HostBridge`）；`HostLocalBindings`（`:382-393`）是「不走 Core 的 Host 本地动作」，`HostControlBindings`（`:398-408`）是「走 HostControl 私有会话」。
   - **UI-facing 的真正闸门在 App 侧**：`IHostController`（`apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs`）有没有对应方法。命令在 registry 里注册、但 `IHostController` 不暴露 = UI 仍不可用（这正是 `ConsoleViewModel.cs:2595-2603` 反复记录的「注册表里有、IHostController 未暴露」模式）。

### 3.2 「加一条命令」需要改的落点（列举文件与行号）

| # | 落点 | 文件:行 | 备注 |
|---|---|---|---|
| 1 | 域名数组加名字 | `HostCommandRegistry.cs:168-192` 或对应域数组 | 漏加 → `BuildCommands` 里落 NotSupported 兜底分支（`:608-622` 自述「不得依赖本兜底分支」） |
| 2 | `CoreBindings` 加 `<name> → (CoreCommand, minor)` | `HostCommandRegistry.cs:237-367` | 漏加 → 同上兜底 |
| 3 | 若走私有会话：加入 `HostControlBindings` | `HostCommandRegistry.cs:398-408` | 普通应用通道对 host-control 命令返回 `HOST_ONLY_REQUIRED`（`core_service.py:402-409` 注释） |
| 4 | 若属新增增量族：加入对应 `*CommandNames` 集合 | `HostCommandRegistry.cs:442-455 / 462-466 / 528-533` | 一致性测试靠它推导「增量集 = 注册表 − 冻结 66」 |
| 5 | 请求 payload 写入器 | `HostCommandDispatcher.cs:518-...`（`WriteCorePayload` 的 switch） | 例：`library_start_run` 分支 `:547-554` + `WriteStartRunOverrides` `:1470-1477` |
| 6 | Host 运行时门控 | `NewManga.Host/HostRuntime.cs:2385-2394`（`RunCommandPolicy.TriggersStepExecution`）、写权限 `RequireWritesAllowed` | 决定是否要预签发 source-read 授权 |
| 7 | App 端口 | **受 C-07 冻结的三个接口**：`Services/IHostController.cs`、`Services/RunContracts.cs`（`IRunController`）、`IReaderProgressSink` + `HostController` / `NullHostController` + 测试 `FakeHostController` | C-07 v1.10 记录要求四处实现一致（`doc/plan/FEA-CONTRACT-FROZEN-C07.md:54`）；inventory 由 `tools/generate_api_inventory.py:26-29` 生成 |
| 8 | 一致性测试 | `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandParityContractTests.cs:41-130` | 冻结 66 快照不可编辑，新命令必须显式进增量集 |

### 3.3 门控/投影样板（可直接照抄的三处）

| 样板 | 位置 | 学习点 |
|---|---|---|
| `list_page_region_texts`（读面，最近一次落地） | `HostCommandRegistry.cs:191, 357, 462-466`；`core_service.py:88-105, 7803` | 纯读、minor 3、`RegionReadCommandNames` 单元素集合、`--check 80/87` 的一次纯 append |
| `source_resync`（写面 + 私有会话） | `HostCommandRegistry.cs:251, 398-408, 496-497` | 写命令必须进 `HostControlBindings`，并走 Host operation journal |
| `library_start_run`（Run 面 + 授权钩子） | `HostCommandRegistry.cs:284`；`HostCommandDispatcher.cs:547-554, 1470-1477`；`HostRuntime.cs:2385-2394` | **自动翻译应该复用的就是这条**：`overrides.provider_bindings` 的注入位置就在这里 |

---

## 4. 契约面（最关键）

### 4.1 复用既有 Core 调用 + 不新增 wire 命令：**可行，且已被真实运行证明**

可行性的硬证据（不是推断）：

- wire 层：`StartRun` 接受任意 `COMMAND_CATALOG` 成员（`core_service.py:6695-6696`），`translate_all` 在目录内（`src/domain/tasks/models.py:67-82, 87`）。
- 运行层：`verification/REAL-TRANSLATE-PROVIDER-1/REPORT.md:43-46` 记录了 `StartRun translate_untranslated`（book scope）+ `overrides.provider_bindings={ocr: manga-ocr, translate: openai-compatible-translation}` 的真实运行：detect 8 页完成、3 个 translate 目标全部真实 `429 → PROVIDER_RATE_LIMITED`，**`PROVIDER_NOT_CONFIGURED` 计数为 0**。
- 回退层：同一报告 `:54-57` 记录了换成 `identity-translation` 后 translate 22/22 completed。

**所以「能不能跑通」不是问题；「谁来注入 translate binding」才是问题。**

关于「新增 Host 投影」：**也不必新增**。自动翻译需要的进度/状态投影已经存在（`GetRunSnapshot` / `GetTaskProjection` / `RetryFailedTargets`），UI 侧也已有 1s 轮询实现（`apps/.../WorkbenchViewModel.cs:17, 206-210`；`WorkbenchPageView.cs:539-589`）。

### 4.2 若必须新增 wire 命令：逐份判断「是否必须改、为什么」

| 契约 | 冻结版本 / pin | 是否必须改 | 为什么 |
|---|---|---|---|
| **C-16**（Source 读取与导入 wire） | v1.7；`67286eec…`；`doc/plan/FEA-CONTRACT-FROZEN-C16.md:16` | **否（0 字节）** | C-16 的全部条款是 source 读授权/导入 wire：§0 capability、§2.4 `AuthorizeSourceReadForRun`、§2.5 `ReattestSourceLocation`、容器多成员 entry（`:91, 103, 115, 139`）。翻译命令既不改 source ref、不改 grant、不改 Run 的 source 授权前置，因此零冲击。**唯一相关**：自动翻译 Run 仍要过 §2.4 的授权门（这是既有行为，不是新字节） |
| **C-04b**（删除协议字段与码表） | v1.2；`4b304c0c…`；`FEA-CONTRACT-FROZEN-C04b.md:13` | **否（0 字节）** | 全篇是删除预览 / `inventory_digest` / 保护清单 / 回收站，与翻译无交集 |
| **C-07**（API inventory：App→Host 端口面） | v1.10；`498882eb…`；**80 方法 + 4 非方法 = 87**；`FEA-CONTRACT-FROZEN-C07.md:15, 44-45` | **仅当新增端口成员** | C-07 冻结的是 App→Host 端口面，清单覆盖 **`IReaderProgressSink` + `IHostController` + `IRunController`**（`tools/generate_api_inventory.py:26-29`，源文件 `Services/IHostController.cs` 与 `Services/RunContracts.cs`）。复用既有 `IRunController.StartRunAsync`（`RunContracts.cs:368`）→ 0。若为翻译新增如 `StartTranslateAsync`（无论加在哪个接口）→ 必须 UNFREEZE + 重跑 `tools/generate_api_inventory.py --check`（87 → 88）+ 独立字节级复核 + 重冻 |
| **M2-C1**（Typed IPC command catalog） | rev 2.16；`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:18, 30` | **仅当新增 Core wire 命令** | §5 是命令目录；新增命令须新增一行 + 协议/族 minor 决定（§3.2 `:148`）。M2-C1 **不在 18 项机械 pin 里**（`doc/plan/FEA-CONTRACT-FROZEN-C04b.md:18` 自述「0/18 机械 pin，手工登记」），但 rev 2.13/2.16 的先例要求：UNFREEZE 载体 + 独立复核 + 手工登记 |

### 4.3 是否需要 UNFREEZE + pin 影响数量

| 路径 | UNFREEZE 载体 | 机械 pin 影响（`tools/governance/verify_pins.ps1`，共 18 项） | `generate_api_inventory.py --check` |
|---|---|---|---|
| **P0 最小路径**（复用 `StartRun`，配置桥在 Core 内部，UI 用既有端口） | **不需要** | **0/18** | 不变（`1/80/6 = 87`） |
| P1 只加 App 侧新端口（新 `IHostController` / `IRunController` / `IReaderProgressSink` 成员） | C-07 需要 | **1/18**（C-07 重算 pin） | 87 → 88 |
| P2 新增 Core wire 命令 | M2-C1 需要（+ 若同时加端口再叠 C-07） | **0/18 机械**（M2-C1 手工登记）+ 可能的 1/18 | 视 P1 |
| 任何路径 | C-16 / C-04b | **始终 0** | 不变 |

> 纪律依据：`doc/plan/FEA-CONTRACT-FROZEN-C07.md:27`（「条款字节自本记录起不得改动；修订须走 UNFREEZE 载体 + 重新独立复核 + 重新冻结」）；`tools/governance/verify_pins.ps1:6-13`（18 项映射）；`doc/plan/FEA-CONTRACT-FROZEN-C16.md:20`（同语义）。

---

## 5. 设置与凭据面

### 5.1 provider 配置存在哪里

| 数据 | 存储 | 证据 |
|---|---|---|
| Provider profile（`base_url` / `model` / `credential_ref` / `capabilities` / `network_profile_id` / `proxy_policy` / `options` / `enabled`） | `JsonProviderProfileStore` → `<data_root>/settings/*.json`（原子写） | `core_assembly.py:1943`；`src/infrastructure/settings/json_profile_stores.py:62-95` |
| 能力绑定（capability × scope → profile_id） | `JsonProviderCapabilityBindingStore` → `<data_root>/settings/*.json` | `core_assembly.py:1945`；`settings_commands.py:655-682` |
| 网络 profile（代理 / TLS / bypass） | 独立 JSON store + `NetworkProfileService` 危险项门 | `src/application/settings/network.py:50-64`；`settings_commands.py:893-897` |
| **运行期真正读取的配置** | `pipeline_defaults.settings_json` 的 `settings["providers"]["profiles"][<provider_id>]` | `src/infrastructure/providers/runtime.py:182-193`（`_profile_settings` / `_provider_settings`）；`core_assembly.py:1421-1423` |

### 5.2 `credential_ref` 的解析与存储机制

- **命名规则**：`make_credential_ref(kind, name)` → `NewManga/{provider|proxy}/{name}`（`src/ports/providers/credentials.py:25-37`）。数据库/JSON 只存这个 ref 字符串，**不存 secret**。
- **存储**：Windows Credential Manager，`CRED_TYPE_GENERIC`（`src/infrastructure/credentials/windows.py:26, 83, 100-108`）；`SecretValue` 的 `repr/str` 恒为 `<redacted secret>`，比较用 `hmac.compare_digest`（`ports/providers/credentials.py:40-77`）。
- **写入链路**：Host 本地命令 `credential_put` / `credential_clear`（`HostCommandRegistry.cs:390-391`）→ `HostController.PutCredentialAsync`（`HostController.cs:1248-1276`）→ 写 vault 后由 Core `BindProfileCredential` 把 `credential_ref` 绑到 profile（`core_service.py:489`；`settings_commands.py:131, 327-350`）。
- **解析链路**：装配期一次性构造 `_credential_resolver` → `store.resolve_credential(ref).reveal()`，异常一律返回 `None`（`core_assembly.py:803-818`），provider 侧表现为 `MISSING_CREDENTIAL`（`ports/providers/errors.py:109-113`）；网络代理凭据走同一 vault（`core_assembly.py:1419-1425`）。
- **扫描证据**：Host 侧凭据状态只显示「已保存/未保存」，凭据目标列表由 profile 列表推导（`HostController.cs:1185-1232`）。

### 5.3 「模型与设备：待接入」到底缺哪一层

- 设置页分区状态：`"Provider 与凭据"` = **已接线**（`ConsoleViewModel.cs:119`）；`"模型与设备"` = **未接线**（`ConsoleViewModel.cs:121`，理由「设备探测未接入（无 Host 命令）」）。
- 具体文案坐实：`ConsoleViewModel.cs:455-457`「设备与权重：Core 尚未暴露设备/权重状态命令」；`:2591`「设备探测当前只存在于打包元数据（VERSION.json），Host 未暴露设备/模型查询命令」。
- **所以「待接入」= 设备/权重探测层（GPU/CPU、权重是否就绪）缺失，属于 Core 缺少一条只读状态命令；不是 provider 配置缺失。** Provider 的 base_url/model/credential/能力绑定都能在 UI 里配。
- 另有一条真实偏差（本评估新发现，也是 G1 的直接后果）：`ConsoleViewModel.cs:449-453` 的「检测能力」判定只看 profile 列表里有没有 enabled + Detection，**不知道 Run 运行时会不会真的拿到 binding**，因此 UI 的「可以提交」与实际 `PROVIDER_NOT_CONFIGURED` 可能不一致。

### 5.4 运行期 binding 到底怎么来（决定 G1 的存在）

`handle_translate` → `_chain(run, "translate")` → `run.provider_binding_snapshot["translate"]`，缺失即 `ProviderNotConfigured`（`handlers.py:1266-1274`）。

`provider_binding_snapshot` 来自：

1. `StartRun.overrides.provider_bindings`（`core_service.py:6699-6715` → `tasks/service.py:354-398`）；
2. 或 `pipeline_defaults.provider_bindings_json`（`core_assembly.py:1755-1766`）；
3. 冻结时由 `ProviderRegistry.freeze_run_snapshots` 把 profile id 别名解析成 registry 槽（`registry.py:353-452`；`runtime.py:418-459` 的 `_apply_profile_bindings`）。

而 `_apply_profile_bindings` 只认 `settings["providers"]["profiles"]`（`runtime.py:437-459`），**而生产代码里没有任何写入 `settings["providers"]` 的地方**（全仓 `"providers"` 仅出现在 `src/bootstrap/acceptance_bridge.py:386, 417` 的验收桥）。P15 的 profile/binding store 与它完全解耦。

**G1 的一句话表述**：`settings_provider_bindings_set` 把「Translation → profile」写进了 JSON 绑定 store，但 Run 运行时读的是另一本账；两本账之间没有桥。

---

## 6. UI 面：入口现状与建议落点

### 6.1 入口**已经存在**（与「UI 无 provider 调用接线」的已知事实需要修正口径）

| 入口 | 现状 | 证据 |
|---|---|---|
| 工作台 · 批量 · 「开始处理」 | **已接线**：1 次 `StartRunAsync(command=translate_all, scope={kind:"chapter"})`，自持 idempotency key，1s 轮询真实投影 | `WorkbenchPageView.cs:476-480`；`WorkbenchViewModel.cs:13-14, 157-204` |
| Studio · 批次 · 「翻译」 | **已接线**：`StudioBatchActionKind.Translate` → `translate_selected / translate_single / translate_all` → `IRunController` | `StudioBatchViewModel.cs:368, 1087-1164, 1167-1174, 1375-1402` |
| Studio · 「开始处理」空态 | 同上（`StartProcessingAsync`） | `StudioBatchViewModel.cs:1167-1174` |
| 阅读器 | **无翻译入口**：工具条只有 返回/单双页/反向/全屏/书签/缩放 | `ReaderPageView.cs:268-278, 391-396, 410-420` |
| 手动译文输入 | 显示「能力待接入（F0-1 save_manual_translation）」——**这条已过期**，`save_manual_translation` 实际已注册在 Host | `StudioInspectorPanel.cs:256`；对照 `HostCommandRegistry.cs:352` |

也就是说：**用户今天点「开始处理」就已经发出自动翻译请求**，只是它会在 translate 步骤因未绑定 provider 而失败，而失败文案在 Studio 侧已有针对性提示（`StudioBatchViewModel.cs:1138-1142`：「未配置模型 Provider：请到「设置 → Provider 与凭据」…」），工作台侧**没有**这个门（`WorkbenchPageView.cs:476-480` 只有 `IsReadOnly`/空态门）。

### 6.2 最自然的入口（建议）

1. **工作台批量「开始处理」**（`WorkbenchPageView.cs:476-480`）——成本最低、位置最显眼；需要补：provider 未就绪门 + `PROVIDER_*` 文案映射（照抄 `StudioBatchViewModel.cs:1138-1152`）。
2. **Studio 批次「翻译」**（`StudioBatchViewModel.cs:368`）——已有，补齐「translate binding 是否具备」的前置判断。
3. **阅读器工具条**（`ReaderPageView.cs:268-278`）——若产品要「读到哪翻到哪」，在此加「翻译本章」；需要 `ReaderPageViewModel` 新增一个 `StartChapterTranslateAsync` 并接 `IRunController`（与 `ReaderWorkbenchSupport.cs:191` 的 Run 命令白名单对齐）。
4. 冲突/错误横幅位置可复用 `WorkbenchPageView.cs:694-722` 的 `FluentUi.Banner` 模式，但注意其**只支持单个 action**（`:696-699` 注释），provider 引导与「重读草稿」不能挤同一个 Banner。

### 6.3 需要改的 ViewModel

| VM | 改动 | 触契约 |
|---|---|---|
| `WorkbenchViewModel.cs` | provider 就绪门、失败码 → 文案、可选「翻译并渲染」 | 否 |
| `StudioBatchViewModel.cs` | 把 `NeedsProviderSetup` 语义从「错误后置」提到「提交前门」 | 否 |
| `ReaderPageViewModel`（+ `ReaderOverlayViewModel` 若需进度） | 新增翻译本章动作 | 否 |
| `ConsoleViewModel.cs` | 「模型与设备」如要真接线，需要**新 Core 只读命令**（这就是 C-07/M2-C1 才会动的地方；本评估建议不纳入最小路径） | 若做 → C-07 + M2-C1 |

---

## 7. 工作量与拆分建议（4 张卡）

| 卡 | 范围 | 依赖 | 触契约 | 预估改动文件数 | 风险 |
|---|---|---|---|---|---|
| **T-A `TRANS-BINDING-BRIDGE`** | 在 Core 内把 P15 profile / 能力绑定**镜像**进 `pipeline_defaults.settings["providers"]["profiles"]`（含 `base_url/model/credential_ref/network_profile_id/proxy_policy/options/enabled`），写入点挂在 `settings_provider_profiles_create/update/delete`、`settings_provider_bindings_set/clear`（`settings_commands.py:590-682`）；写失败必须 typed fail-closed（沿用 `BindingValidationError` 语义 `core_service.py:3110-3113`） | 无（先行） | **否** | 4–6（`settings_commands.py` / 可能 `runtime.py` / `pipeline_defaults.py` / tests×2） | **中**：写的是持久化配置；写错会导致下次装配期不可自愈；必须补「改配置需重启 Core 才生效」的显式说明 |
| **T-B `TRANS-RUN-PATH-FIX`** | 定位并修 `library_start_run` → 冻结 Core 的 `INVALID_REQUEST` 遗留（`REAL-TRANSLATE-…REPORT.md:75-80`）；`RunBindingDefaults` 从「只注 ocr」改为「默认 ocr + 可配置 translate」（或改为只补缺失键的合并策略，避免覆盖用户 binding） | T-A | **否**（Host 内部 + 既有 wire） | 3–5（`RunBindingDefaults.cs`、`HostCommandDispatcher.cs:1470-1477`、`HostRuntime.cs` 若涉门控、tests） | **中**：会碰到 Run 的 source-read 预授权路径（`HostRuntime.cs:2385-2394`） |
| **T-C `TRANS-ENTRY-UI`** | 工作台「开始处理」补 provider 前置门 + `PROVIDER_*` 文案；Studio 批次「翻译」补前置门；可选阅读器「翻译本章」；把 `StudioInspectorPanel.cs:256` 的过期「能力待接入」文案改正 | T-A、T-B | **否**（复用 `StartRunAsync`） | 5–8 | **低**：只做投影/文案/门控 |
| **T-D（可选）`TRANS-QUALITY`** | `target_language` 接入（当前请求体恒为空，`REAL-TRANSLATE-…REPORT.md:81`）、SFX 文化等效提示回归、长文本/上下文预算与成本上限（当前无 token 计量，见 §8） | T-A | **否** | 3–5 | **中**：影响译文质量，不影响契约 |

> 建议顺序：T-A → T-B → T-C（T-D 可并行或后置）。**最小可用 = T-A + T-B + T-C 的最小门。**

---

## 8. 失败模式（含真实遇到过的）

| 失败模式 | 现在的行为 | 证据 | 评估 |
|---|---|---|---|
| **provider 未授权 403** | `401/403 → PROVIDER_AUTH_FAILED`，**不可重试** | `src/infrastructure/providers/openai_client.py:298-299`；`ports/providers/errors.py:103-106`；`is_retryable` `errors.py:234` | 正确；UI 需要把「key 无效/无权限」与「额度」分开说 |
| **模型名不可用 404（qwen 真实遇到）** | 落入「剩余 4xx → `ProviderInputError`」→ wire 码 **`INVALID_INPUT`**，**不可重试** | `openai_client.py:304-306`；`errors.py:140-143` | **语义错位**：模型不存在被报成「输入非法」。UI 若不特判，用户只会看到 INVALID_INPUT，无法定位到模型名 |
| **402 无余额** | 同上（4xx）→ `INVALID_INPUT` | `openai_client.py:304-306`；`REAL-TRANSLATE-…REPORT.md:14, 27` | 同上；「没钱」被报成「请求非法」 |
| **429 限流** | `PROVIDER_RATE_LIMITED`，**可重试**（真实 429 已留证） | `openai_client.py:300-301`；`REAL-TRANSLATE-…REPORT.md:45` | 正确；但 3 次重试 × 1s 线性退避（`retry.py:29-30, 47-49`）会放大计费/触发更严限流 |
| **超时** | 单请求默认 **60s**（`openai_client.py:81`），`ProviderTimeout` 可重试 | `openai_client.py:333-336`；`ports/providers/errors.py:122-125` | 无「整页/整章总超时」；长章节 × 60s × 3 次可能长时间挂住 |
| **离线 / 网络不可达** | transport 异常 → `ProviderUnavailable`（可重试） | `openai_client.py:330-345` | 正确；离线时 UI 需给出「已知网络问题」而非「内部错误」 |
| **translate 未绑定 provider** | `ProviderNotConfigured` → `PROVIDER_NOT_CONFIGURED` | `handlers.py:1266-1274` | **这是当前最可能撞上的失败**（G1/G2 的直接后果） |
| **长文本** | 每 step 只翻**一个 region**（不整页批），region 文本不截断（`translation_openai.py:113` 注释）；上下文页 1–5 页、token 预算 200–8000 | `handlers.py:625-635`；`settings_sections.py:61-64` | region 级切分降低了单请求体积；但**上下文预算超限时的截断只记录不阻断**（`handlers.py:690-693` 输出 `truncated_context_pages`），质量会静默下降 |
| **SFX** | 三道门：全局 `sfx.policy ∈ {skip,translate,manual}`（`core_service.py:542, 3091-3097`）、region 级 `decide_sfx_translation`（`context/gate.py:15-38`）、prompt 层「文化等效」要求（`translation_openai.py:41-55`） | 同左 | 语义完整；policy=skip 时**不会**报错，只是产出 0 条译文——UI 必须能区分「跳过」与「失败」 |
| **并发** | Run 单 scheduler owner（`core_service.py:6658-6662`）；同批重复提交靠 `idempotency_key`（`WorkbenchViewModel.cs:164-176`）；跨 run 写同一 region 有 `expected_revision` 守卫 → `INPUT_REVISION_CHANGED` | 同左 | 结构安全；但两处入口（工作台 / Studio）各自持 key，同一章节可能发起两个 Run |
| **账单** | **未找到**任何 token/成本计量或配额闸 | 全仓未见配额/成本上限实现 | 风险项：`translate_all` 一章 = 页数 × region 数 次远程调用，无上限 |
| **配置生效时机** | 装配期一次性读 settings 并闭包持有（`core_assembly.py:1421-1423`；`runtime.py:502-548`） | 同左 | 用户改完 Provider 配置后**必须重启**才生效；不做提示会造成「配了也不管用」的错觉 |
| **Host StartRun 兼容** | 隔离根 + REPACK-2 sidecar 下 `library_start_run` 返回 `INVALID_REQUEST`（Core 直连同 payload 可接受） | `REAL-TRANSLATE-…REPORT.md:75, 80` | **未定位**；若在真实数据根复现，则 UI 入口直接不可用 |
| 身份回退 `identity-translation` | EXPERIMENTAL 占位（输入=输出），显式 binding 才能选 | `REAL-TRANSLATE-…REPORT.md:58` | **不可**作为「翻译可用」的证据或默认值 |

---

## 9. 最小可行路径（推荐）

**目标**：用户点一次「开始处理 / 翻译」，真实翻出译文，失败有可读原因；**不动任何冻结字节**。

1. **T-A 配置桥（Core，唯一必做的"新代码"）**
   - 在 `SettingsSurface` 的 profile/binding 写路径成功后，同步写 `pipeline_defaults.settings["providers"]["profiles"]` 镜像；
   - 复用既有 `PipelineDefaultsService.save_settings_section`（`core_service.py:3106-3113` 的同一 seam），**不新增 wire 命令**；
   - 镜像只含 `credential_ref`，**绝不**含 secret（与 `REAL-TRANSLATE-…REPORT.md:36` 的既有纪律一致）；
   - 失败必须 typed fail-closed，不允许半写。
2. **T-B 运行路径收口（Host）**
   - 修 `library_start_run` 的 `INVALID_REQUEST` 遗留；
   - `RunBindingDefaults` 扩展为「默认 ocr +（存在 translate 配置时）translate」，且**用户显式 overrides 永远优先**（保持 `RunBindingDefaults.cs:9-15` 的既有语义）。
3. **T-C 入口与文案（App）**
   - 工作台「开始处理」补 provider 门 + `PROVIDER_NOT_CONFIGURED / PROVIDER_AUTH_FAILED / INVALID_INPUT(模型名) / PROVIDER_RATE_LIMITED` 四类文案；
   - 顺手修正 `StudioInspectorPanel.cs:256` 的过期「能力待接入」。
4. **收尾提示**：配置变更需重启 Core 才生效——在设置页明示（否则用户会认为 T-A 无效）。

**不做**（本路径明确排除）：新 Core wire 命令、新 `IHostController` 成员、「模型与设备」设备探测接线、`Translation` 命令族独立化。

---

## 10. 若走最小路径：需 UNFREEZE 的契约与 pin 数

| 项 | 结论 |
|---|---|
| 需 UNFREEZE 的契约 | **无（0 份）** |
| 需改字节的冻结文档 | **无** |
| `tools/governance/verify_pins.ps1` | **18/18 全部不变**（pin 影响 **0/18**） |
| `python tools/generate_api_inventory.py --check` | **不变**（`1/80/6 = 87`） |
| 独立的"条件" | 仅代码纪律：配置写入必须 fail-closed、不得把 secret 写进 settings、不得在 UI 侧直读文件/数据库（AD-002 边界） |

对照（若产品最终选择了更重的路径）：

| 路径 | 需 UNFREEZE | pin 影响 | `--check` |
|---|---|---|---|
| 最小路径（推荐） | 无 | 0/18 | 87 → 87 |
| + 新 `IHostController` / `IRunController` / `IReaderProgressSink` 成员 | C-07 | **1/18** | 87 → **88** |
| + 新 Core wire 命令 | M2-C1（+ 若加端口再叠 C-07） | 0/18 机械 + 可能 1/18 | 视上 |
| C-16 / C-04b | **永不** | 0/18 | — |

---

## 附录 A：核心证据索引（按问题）

- Q1：`src/application/translation/context/step.py:81, 142, 162`；`src/infrastructure/providers/handlers.py:228, 597, 655, 676, 1266`；`src/infrastructure/providers/step_writes.py:122`；`src/infrastructure/providers/retry.py:26-49`；`src/application/tasks/service.py:93-128`；`src/application/translation/pipeline/executor.py:29`。
- Q2：`src/bootstrap/core_service.py:397-401, 559-570, 4136, 4367, 6692-6715, 8280-8298`；`src/domain/tasks/models.py:67-87`。
- Q3：`HostCommandRegistry.cs:110-192, 219-233, 237-367, 398-408, 442-466, 528-533, 540-624`；`HostCommandModel.cs:5-46`；`HostCommandDispatcher.cs:518-554, 1470-1477`；`HostRuntime.cs:2385-2394`；`CommandParityContractTests.cs:41-130`。
- Q4：`doc/plan/FEA-CONTRACT-FROZEN-C16.md:16, 20, 91-143`；`FEA-CONTRACT-FROZEN-C04b.md:13, 18`；`FEA-CONTRACT-FROZEN-C07.md:15, 27, 44-45, 54`；`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:18, 30, 148`；`tools/governance/verify_pins.ps1:6-13`；`verification/REAL-TRANSLATE-PROVIDER-1/REPORT.md:43-48, 75-80`。
- Q5：`core_assembly.py:803-818, 1421-1423, 1755-1766, 1943-1945`；`json_profile_stores.py:62-95`；`runtime.py:182-193, 418-459, 470-483`；`ports/providers/credentials.py:25-77`；`infrastructure/credentials/windows.py:26, 83, 100-108`；`settings_commands.py:32-39, 131, 327-350, 545-583, 655-682`；`ConsoleViewModel.cs:119-121, 449-457, 2591`。
- Q6：`WorkbenchPageView.cs:476-480, 539-589, 694-722`；`WorkbenchViewModel.cs:13-14, 157-204`；`StudioBatchViewModel.cs:368, 1087-1174, 1375-1402`；`ReaderPageView.cs:268-278, 391-396, 410-420`；`StudioInspectorPanel.cs:256`。
- Q8：`openai_client.py:81, 294-307, 330-345`；`ports/providers/errors.py:103-143, 234`；`retry.py:26-49`；`handlers.py:625-635, 690-693, 1266-1274`；`settings_sections.py:61-64`；`core_service.py:542, 3091-3097, 6658-6662`。

## 附录 B：未找到 / 需进一步确认

1. **Host `library_start_run` 的 `INVALID_REQUEST` 根因**：只有现象与复现上下文（`verification/REAL-TRANSLATE-PROVIDER-1/REPORT.md:75, 80`），**未找到**定位结论或修复卡。需要在真实数据根复现后再定 T-B 的工作量。
2. **成本/配额闸**：全仓**未找到**任何 token 计量、单章预算或账单上限实现。属产品决策空位，不是缺陷。
3. **`settings["providers"]` 镜像的"官方"形状**：目前只有验收桥（`acceptance_bridge.py:386, 417`）与测试用 `settings_update_section` 实际写过；**未找到**冻结的 schema 文档。T-A 落地时应把形状写进 `doc/design/SETTINGS_SECTION_SCHEMAS.md` 一类的设计文档（非冻结契约）。
4. **`ProviderBindingResolver`（`src/application/settings/bindings.py:65-152`）是否应成为正式解析入口**：它有完整的 scope 优先级（task > chapter > book > global），但全仓**无生产构造点**。T-A 若只做「镜像」，这条能力仍闲置；若改用它会改变现有 `overrides.provider_bindings` 语义，需单独裁决。
5. **阅读器「翻译本章」的产品口径**：现有阅读器只有 `original/translated` 两种模式（`core_service.py:4943, 5014`），无「缺译文时自动触发」语义；是否允许在阅读器里发起 Run 属产品决策，本评估不做裁定。

---

## 变更记录

| 日期 | 变更 | 作者 |
|---|---|---|
| 2026-11-14 | 建立：自动翻译可行性 + 契约面评估（只读；结论 = 条件可行，零契约改动） | MAINT-1 调研（独立上下文） |

---

## 10. DSH 补充：既有 `REAL-TRANSLATE-PROVIDER-1` 的直接价值（本评估未覆盖）

评估把 T-A/T-B/T-C 当作必经路径，但仓库里已有一次**更接近完成的装配实验**，值得先说清：

- `verification/REAL-TRANSLATE-PROVIDER-1/REPORT.md` 记录了一次**手工装配 profile + binding + settings 后真跑 translate step** 的验证：3 个目标页全部 `PROVIDER_RATE_LIMITED`（真实 HTTP 429），而 **`PROVIDER_NOT_CONFIGURED` 为 0**。
- 即：**装配链路与 provider 调用链已被证明接通**；AC3 的 `BLOCKED` **唯一**原因是那把 key 没有推理额度（付费 402 / 免费 429），不是功能或装配缺失。
- 本机现有 DeepSeek key **已实测可用**（`model-api-verification.log`：`deepseek-chat`、`valid_protocol=True`）。

**推论（可直接执行）**：用有额度的 key 重跑该 Task 的 AC3，**有可能在不写 T-A/T-B/T-C 任何一行代码的前提下**得到「`completed` 且产出 ≠ 输入」，从而先拿到「Core 侧端到端」证据。

**但有一个必须写清的边界**：该 Task 的运行探针走的是**冻结 Core stdio 直连**，**不经 Host 的 `library_start_run`**；而 G3 恰恰是 Host 路径的遗留缺陷。所以：

| 能证明 | 不能证明 |
|---|---|
| Core 侧：配置 → provider → translate step → 落库 | Host/UI 侧：设置写入 → StartRun 注入 → 真实入口点击 |
| 失败语义（429→`PROVIDER_RATE_LIMITED`）与 identity 回退 | T-A 的「配置桥」是否真的把 P15 镜像进 `settings.providers` |

**建议的推进顺序**：先做这个零代码重跑（成本最低、能立刻把 Gate 条件 5 从「provider 层已验」推进到「Core 端到端已验」），再按 T-A → T-B → T-C 做 Host/UI 面。这样即使 T-B 的 `INVALID_REQUEST` 遗留一时定位不了，也已经有一份可信的「真实翻译产出」证据。