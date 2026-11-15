---
id: SIDECAR-SCHEMA-STALE-1
title: 测试夹具 sidecar 落后 8 个 schema 版本（v6 vs v14）—— prepare-sidecar 默认取已退役 Tauri 产物且副本不刷新（原诊断误指产品包，已勘误）
kind: defect
governance_version: 3
status: closed_with_limitations
suggested_owner: DSH
owner: DSH
reviewer: 未派（本卡为缺陷核实与登记卡；修复与复核由后续卡承接）
depends_on: []
approval: 用户 2026-11-15「全部授权」；目标 B「Release Gate 可独立完成部分」
base_commit: 69fed50bc
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/SIDECAR-SCHEMA-STALE-1
canonical_evidence_status: complete
resource_closeout_status: complete
allowed_paths:
  - doc/tasks/SIDECAR-SCHEMA-STALE-1.md
  - apps/desktop-avalonia/build/sidecar/**
  - packaging/**
  - doc/TASK_LEDGER.md
  - verification/SIDECAR-SCHEMA-STALE-1/**
---

# SIDECAR-SCHEMA-STALE-1：测试夹具 sidecar 的 schema 版本严重落后

> ## ⚠️ 勘误（2026-11-16，依据独立复核 r1 的 P0-1）
>
> **本卡初版的诊断方向是错的，必须更正。**
>
> 初版断言：「`package.ps1` 产出的安装包内含过时 sidecar，用户安装后程序启动即 fail-closed，产品不可用。」
>
> **这个断言不成立。** 独立复核（`doc/reviews/SIDECAR-SCHEMA-STALE-1-r1.md`，CHANGES_REQUESTED）查明：
>
> - 变更前 release `NewManga-e2c9fd058` 内 sidecar 的 `schema.pyc` 与新构建 bundle **字节完全相同**
>   （`sha256 f1058b07…`，`co_names` 含 V1..V14，`default_migrations` 14 条）⇒ **产品包一直是 v14**；
> - 尺寸也对得上：835.25 − 43.56 = 791.69 MiB（旧 release 1,024 文件 / 791.69 MiB）；
> - 卡面点名的 `NewManga-0.2.0-dev-win-x64-models` 实测内嵌 **v14** sidecar（直接反证）；
> - 我自己引用的 B1 失败日志 L72 就写着失败的 sidecar 是
>   **`HOST-CORECLIENT-1\sidecar-copy`**，不是 bundle。
>
> **v6 的真实实体是「测试夹具副本」**：`test.ps1` 的 `SidecarDirectory` 默认指向
> `workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy`，
> 而 `prepare-sidecar.ps1:16` 的默认 `-Source` 指向**已退役的 Tauri 路径**
> `apps/desktop/src-tauri/target/release/resources/core-sidecar`（2026-10-23 的产物）。
> V6 加于 10/23 15:01、V7 加于 11/03 ⇒ 那个 legacy 产物**必然只到 v6**。
>
> **真缺陷因此重新定义为**：
> 1. `prepare-sidecar.ps1` 默认从**已退役的 Tauri 产物**取 sidecar；
> 2. `test.ps1` 的夹具副本「**存在即不刷新**」，导致过期副本被长期使用。
>
> 这两条已于 2026-11-16 修复（见 §修复）。**产品包从未损坏这一结论不因本卡而改变。**



## 怎么发现的

`RELEASE-PACKAGE-1` AC6 要求「`scripts/test.ps1` 全绿」。补跑后 **3 failed**，
全部停在 `core.ping` **握手阶段**，stderr：

```
RuntimeError: database schema v14 is newer than this application knows (v6); refusing to run
```

## 核实（不是猜测）

### 源码侧的 schema 版本

`src/infrastructure/sqlite/schema.py`：

```
SCHEMA_VERSION_V1 = 1
...
SCHEMA_VERSION_V14 = 14
```

且 `default_migrations()` 返回 **V1 … V14 共 14 条迁移**。

`core_assembly.py:1179`：

```python
latest_known = max(migration.schema_version for migration in migrations)
```

⇒ **源码认识的最新 schema = v14**。

### sidecar bundle 侧

`apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar/core_service.exe`
（构建时间 **2026-11-15 03:16**，400 KB 的 launcher）—— 运行时只认识到 **v6**。

### 结论

**sidecar bundle 落后源码 8 个 schema 迁移版本（v6 → v14）。**

## 影响（这才是重点）

这不是"测试环境脏了"，是**打包产物不可用**：

`apps/desktop-avalonia/scripts/package.ps1` 产出的安装包
（如 `NewManga-0.2.0-dev-win-x64-models`）**内含这个 v6 的 sidecar**。
用户安装后，若数据根是 v14 schema（当前源码迁移后的状态），

⇒ **sidecar 启动即 fail-closed 拒绝运行，产品无法启动。**

| Gate | 影响 |
|---|---|
| A（四件套） | **不受影响**（不跑 sidecar，30 skipped） |
| **B 条件 4（安装矩阵）** | **直接影响** —— 包不可用 |
| B 条件 5（翻译质量） | 间接（`translate` 命令需 sidecar） |
| C/D | 不涉及 |

## 为什么之前没被发现

四件套口径（`NewManga.CoreClient.Tests` 单独跑）**跳过全部 30 个 sidecar 测试**，
所以一直 203/0/30 全绿。只有 `scripts/test.ps1`（配夹具、0 skipped）才暴露出来。

⇒ **这是一个"门禁盲区"**：日常门禁跑不到真实 sidecar，导致 bundle 过期不被发现。

## 修复方向

| 方案 | 做法 | 代价 |
|---|---|---|
| **A（推荐）** | 用 `packaging/m2ac5/build_sidecar.ps1` + `core_sidecar.spec` 重建 sidecar bundle | 构建耗时（约 800 MB / 1000+ 文件）；产物 git-ignored |
| B | 若短期无法重建，至少在 `package.ps1` 里加**schema 版本一致性校验**，打包时对比 sidecar 认识的版本与源码最新版本，不一致则失败 | 小；但不能让包可用 |

**建议 A + B 都做**：先 B（防止再发出坏包），再 A（真正修复）。

## Acceptance Criteria

- [x] **AC1 版本对照已核实（勘误后口径）**：源码 schema.py 确实 SCHEMA_VERSION_V1..V14、default_migrations() 14 条；**但原「bundle 认 v6」的判断错误** —— v6 的实体是测试夹具副本，产品 bundle 变更前已是 v14（r1 复核以 .pyc sha256 f1058b07… 证明） <<MET>>
- [x] **AC2 影响面判定（勘误后口径）**：**产品包不受影响**（从未损坏）；受影响的是 scripts/test.ps1 的全部 sidecar 测试（夹具用 legacy v6 副本，握手必败） <<MET>>
- [x] **AC3 门禁盲区记录**：说明"四件套跳过 sidecar 测试"导致未被发现。 <<MET>>
- [x] **AC4 打包加一致性校验**：`package.ps1` 在打包前比对 sidecar schema 版本与源码最新版本，不一致则失败并给出明确指示。 <!-- 实施于 package.ps1：读 bundle 的 build-manifest.json，缺失则拒绝打包；存在则比对 manifest.schema_version 与源码 schema.py 的 SCHEMA_VERSION_V<n> 最大值，不等则拒绝。两个场景实测：① 无 manifest → EXIT=1「cannot prove which schema it understands」；② manifest 声明 v6 而源码 v14 → EXIT=1「built against schema v6 but the source tree is at v14 ... Rebuild the bundle」。build_sidecar.ps1 已改为构建时写入该 manifest。 --> <<MET>>
- [x] **AC5 重建或登记**：重建 sidecar bundle（或明确登记为需专门构建轮次，附操作步骤）。 <!-- 2026-11-16 DSH：已用 build venv（Python 3.14.6 + PyInstaller 6.22.3）执行 packaging/m2ac5/build_sidecar.ps1 -Force 重建成功，bundle 835.3MB，build-manifest.json 写入 schema_version=14；package.ps1 安全阀由拒绝转为放行（sidecar schema check: v14 == source v14）；test.ps1 重跑后 schema v14/v6 错误归零。详见 workspace/tasks/SIDECAR-SCHEMA-STALE-1/rebuild-report-v2.md。**重要限制**：test.ps1 仍有 **5 failed / 251 passed**（schema 错误已归零，但新 bundle 暴露了 5 个全新类别失败：INVALID_REQUEST / pending 超时等），与 schema 无关，需独立诊断，本卡不宣称 test 全绿。 --> <<MET>>
- [ ] **AC6 独立复核**：固定 head 交独立上下文 Review。 <<BLOCKED: 待 AC4/AC5 实施后一并送审>>

## 禁止范围

- 不得为让测试变绿而修改 `schema.py` 的版本常量；
- 不得让 sidecar 绕过 schema 版本校验（那是正确的防御）；
- 不得把 v14 数据库降级到 v6（会丢数据）。

## 说明

本卡发现的缺陷**比 B1 的任何一条都严重**：其他都是文档/证据缺口，这条是
**交付物实际不可用**。优先级应高于继续清 B1。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-SSS-01 | AC1/AC2/AC3 版本对照与影响面证据 | verification/SIDECAR-SCHEMA-STALE-1/version-check.log | 4f786190c | cee05df9c31944d9165c898a33da24ca31f1b7ebb212574584a2fe0750d5f219 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/SIDECAR-SCHEMA-STALE-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-16，DSH（核实与登记；修复未做）。
- **缺陷**：sidecar bundle 落后源码 **8 个 schema 迁移版本**（bundle 认 v6，源码已 v14）。
- **影响**：package.ps1 产出的安装包内含该 v6 sidecar ⇒ 面对 v14 数据根时
  **启动即 fail-closed，产品不可用**。Gate 条件 4（安装矩阵）直接受影响。
- **为什么之前没发现**：四件套口径跳过全部 30 个 sidecar 测试（0 skipped 只在
  scripts/test.ps1 里出现），形成**门禁盲区**。
- **本卡只做核实与登记**，AC4（打包加一致性校验）与 AC5（重建 bundle）标 BLOCKED，
  属独立实施轮次。**状态 closed_with_limitations 即"已定位但未修复"**。

## 修复（2026-11-16，回应 r1 复核 P0-2）

r1 复核指出：本卡前三轮提交只改 package.ps1 / uild_sidecar.ps1 / 卡面，
**没有修真正的缺陷**（测试夹具的选取与刷新逻辑），实质修复只是对 workspace 副本的手工替换，不可复现。

已按复核建议补齐两处：

| 文件 | 改动 |
|---|---|
| pps/desktop-avalonia/scripts/prepare-sidecar.ps1:16 | 默认 -Source 从**已退役的 Tauri 路径** pps/desktop/src-tauri/target/release/resources/core-sidecar 改为 Avalonia 构建产物 uild/sidecar/core-sidecar/core-sidecar；新增 NEWMANGA_SIDECAR_SOURCE 覆盖 |
| pps/desktop-avalonia/scripts/test.ps1:39-73 | 夹具副本不再「存在即用」：读 uild-manifest.json 比对 schema_version 与 git_head，缺失/不等则**先删除再重建**（删除是必要的 —— 
obocopy /E 叠加会让 _internal 混杂，导致 Failed to import encodings module） |

### 实测（把夹具 manifest 伪造成 v6/旧 head）

`
sidecar fixture: refreshing ...sidecar-copy (fixture schema v6 != build bundle v14)
刷新后 git_head: f7d273d9a  schema: 14
`

自动刷新生效，无需手工干预。

## 仍未达成（不掩盖）

scripts/test.ps1 **仍未全绿**：schema/管道/encodings 三类错误已归零，但仍有
**5 failed / 251 passed**（INVALID_REQUEST、pending 超时等），
判断为新 bundle 与 v14 源码对齐后暴露的**测试期望过时**问题，需独立诊断。
本卡**不宣称 test 全绿**。

### 组 C 已精确定位（2026-11-16，读源码得出，非推断）

`RunBindingFixTests.ModelsBuild_BookRun_WithInjectedBindings_OcrNoLongerProviderNotConfigured`（`RunBindingFixTests.cs:347`）：

| 行 | 断言 | 实测 |
|---|---|---|
| `:401` | `Assert.Equal("completed_with_failures", terminal)` | 通过 |
| `:408` | `Assert.DoesNotContain("failed", ocrStates)` | 通过（OCR 成功） |
| `:410` | `Assert.True(byType.TryGetValue("color", out colorStates))` | 通过（有 color 步骤） |
| `:411` | `Assert.Contains("failed", colorStates)` | **失败** —— `colorStates` 全是 `"pending"` |

测试意图（源码注原文）：OCR 成功 → chain 前进到 color → color 因 **stub analyzer 失败**而 `failed`。
实测：整条 run 确实 `completed_with_failures`、OCR 确实无 failed，**但 color 不是 failed 而是 pending**。

**三种待区分的假设**（下轮处理，本轮不下结论）：
a) chain 根本没跑到 color；b) color 跑了但失败没被写成 `failed`；c) 投影层把 `failed` 映射成 `pending`。

区分手段就在测试里：`:386` 会把 `library.db` 复制到 evidence，`:383-385` 指出
`verification/RUN-BINDING-FIX-1/tools/check_run_binding.py` 断言精确的 per-step error codes。
⇒ 下一步读那份 `library.db` 与 `check_run_binding.py`，**而不是继续从 stderr 推断**。

### 组 B 仍未定位

`CommandWiringB1/B2Tests` 的 `[INVALID_REQUEST]`：测试在 `Run()` 循环里调用，异常不带命令名。
本轮尝试插入临时诊断（打印 `name`）时，脚本锚点不匹配未生效，**未能在本轮定位**。
下一步需按实际缩进重新插入诊断，或直接在 `HostCommandDispatcher.InvokeAsync` 抛异常时附带命令名。

### 组 B / 组 C 全部定性（2026-11-16 续，均来自读证据）

**组 C = 测试期望过时**。读权威账本 step_runs（最新 
un-binding-models-library.db）：

| step_type | status | error_code | count |
|---|---|---|---|
| color | **completed** | — | 3 |
| detect | completed | — | 8 |
| ocr | completed | — | 3 |
| 	erm_extract | completed | — | 3 |
| 	ranslate | **failed** | PROVIDER_NOT_CONFIGURED | 3 |

color 全部成功，真正失败的是 	ranslate。测试 :411 断言 color 必 failed，
其注释「chain still stops at color」已不成立；投影层显示 pending 是因为
测试自己注释所述的「earlier stages stay pending」（已被越过），与账本自洽。



#### ⚠️ 组 B 的定性已撤销（2026-11-16，本人自查推翻）

下方「组 B = settings 域命令返回 UNKNOWN_COMMAND」的结论**是错的**，原因在我自己的 probe：
我发的是**点号** settings.network_profiles_create，而 core 注册的是**下划线**
settings_network_profiles_create。点号被拒是正确行为，不是缺陷。

用正确格式重跑（probe_b1_fixed.py）B1 前 6 条全部正常，含第 6 条 settings_network_profiles_create = ok。

三条反证推翻「settings 未挂载」的推断：
- core_service.py:471-491 的 _P15_SETTINGS_COMMANDS 含 19 个 settings 命令；
- core_service.py:1252 有 self._p15_settings = P15SettingsCommands(core)；
- HostCommandRegistry.cs:311 映射正确（下划线）、HostCommandDispatcher.cs:704-711 payload 构造正确。

另更正：capabilities 只有 17 个是**能力声明**（如 library.list_books），
**不等于命令面**（66 条快照），两者不能互相证明。

**组 B 当前仍未定位**：确定的是失败发生在 Host 侧到 core 之间，
应读 HostCommandDispatcher.InvokeAsync 里 INVALID_REQUEST 的抛出点与判定条件。

**组 B = settings 域命令返回 UNKNOWN_COMMAND**。按 B1 顺序实测：

`
[1] backup.create              ok
[2] backup.delete              ok
[3] cleanup.retry_pending      ok
[4] plugins.audit_list         ok
[5] plugins.set_plugin_enabled PLUGIN_NOT_FOUND（符合预期）
[6] settings.network_profiles_create  UNKNOWN_COMMAND  ← 失败点
`

**矛盾**：settings_commands.py:127/150、core_service.py:482 都注册了该命令，
但 core.ping 的 capabilities **只有 17 个、不含任何 settings/network 命令**。
⇒ 生产组装可能未挂 settings 域（或挂的表与 known-command 列表不一致），需读
ssemble_production_core / ssemble_core_services 确认。

影响面：B1 的 13 条里有 **7 条是 settings 命令**，全部同一域；B2 大概率同理。

**为什么从未暴露**：测试夹具此前一直用 2026-10-23 legacy v6 副本，握手即失败，
根本没跑到这些命令。

### 组 B 排除记录（2026-11-16 续，读代码 + 实测）

已**排除**的四条（都不成立）：
1. 不是产品缺陷 —— _P15_SETTINGS_COMMANDS 含 19 个 settings 命令、P15SettingsCommands 已实例化；
2. 不是命令名格式错 —— 下划线格式实测 ok；
3. 不是 registry 映射错 —— HostCommandRegistry.cs:311 正确；
4. 不是 WriteOptionalBool 的 bug —— HostCommandDispatcher.cs:1435 遇 null **return（不写）**，
   实现正确。（我曾误以为它写 null，实为我的 probe 自己传了 null，绕过 dispatcher 直发 core。）

**已确证**：[INVALID_REQUEST] 来自 CoreProtocol.cs:131
ase($"[{code}] {message ?? "core operation failed"}") —— 即 **core 响应里的 rror.code**，
message 为 null 所以显示默认串。

**关键缺口**：CoreOperationException 只保留 code，core 的 rror.details
（通常含 phase / ction / message_key，如 SETTINGS_INVALID_INPUT）**在异常消息里丢失**。
⇒ 下一步应从 **wire 层抓 core 的原始 error 对象**（含 details），而不是从异常 message 猜。

### 组 B 诊断的第 5 次失效（2026-11-16 续，必须记录）

为从 **wire 层**抓 core 原始 rror.details（WireFrame.ResponseLine，WireLog.cs:9-18），
我用脚本在 CommandWiringB1Tests.cs 的 Run() 第一条语句处插入诊断块。**做错了**：

原代码：
`csharp
var result = await context.Dispatcher.InvokeAsync(name, Args(argsJson));
Assert.Equal(HostCommandStatus.Implemented, result.Status);   // 断言在后
`
我替换为：
`csharp
try {{ var r = await context.Dispatcher.InvokeAsync(...); return r.Value; }}  // return 在断言之前
catch (Exception diagEx) {{ ...Console.WriteLine...; throw; }}
`
=> **断言被完全跳过，测试"通过"了。**

发现方式：插入后跑测试，EXIT=1 但**没有 TEMP-DIAG 输出、日志里也没有失败详情** ——
这个"太干净"的结果本身是信号。已 git checkout 撤销，确认断言顺序完好（:131-133）。

**纪律**：观测行为不得改变被观测对象。加日志不能改控制流。
正确做法是**零侵入**：打开 WireLogPath 跑完读 NDJSON，或只在测试末尾统一 dump frames。

**组 B 本轮零进展。**

### 组 B 定位完成（2026-11-16 续，零侵入读 wire log）

**方法**：SidecarFixture.cs:312 一直在配 WireLogPath，	est.ps1 每次跑自动写 NDJSON
（vidence-rerun/wire/commands-ns-b1-core-service.ndjson，831,949 B / 576 帧）。
前 6 轮手搓 probe 连败 5 次；这轮只读该文件，一轮定位。

**结果**：576 帧里只有 **4 帧**含 INVALID_REQUEST，全是同一条命令：

请求：
`json
{"command":"PermanentlyDeleteBook","version":{"major":2,"minor":10},
 "payload":{"book_id":"38075dfb...","confirm_permanent_delete":true}}
`
响应（**无 message、无 details**）：
`json
{"result":null,"error":{"code":"INVALID_REQUEST","category":"validation","retryable":false}}
`

同 log 里其它 typed error 都带诊断（PLUGIN_NOT_FOUND 有 message、
TARGET_NOT_FOUND 有 message+details）⇒ **这条错误本身不带诊断信息**，
正是 CoreOperationException.Message 只能显示 [INVALID_REQUEST] core operation failed 的原因。

**命令频次**：B1 的 13 条 + CreateBook + PermanentlyDeleteBook 各跑 36 次，
**只有 PermanentlyDeleteBook 被拒**。

**下一步（纯代码对比）**：读 HostCommandDispatcher.cs 里 library_delete_book_permanently
的 payload 构造 + core 侧 PermanentlyDeleteBook 的必需字段校验，找出少写/写错的字段。

### 组 B 根因确定（2026-11-16 续）—— 测试未传 inventory_digest

**完整因果链（全部代码证据）**：

1. **测试的调用**（CommandWiringB1Tests.cs:236-238）：
   `csharp
   var deletedBook = await Run("library_delete_book_permanently",
       $"{{\"payload\":{{\"book_id\":\"{bookId}\",\"confirm_permanent_delete\":true}}}}");
   `
   **没有 inventory_digest。**

2. **dispatcher 的构造**（HostCommandDispatcher.cs:619-638）注释原文：
   > additive digest passthrough only -- never synthesized or enforced here (the Core stays
   > the semantic authority) ... Optional: a legacy caller that omits it is still forwarded
   > unchanged (**the new Core fail-closes with INVALID_REQUEST**)
   => **这是有意的设计**，不是 bug。

3. **wire log 实证**（帧 #527/#543/#559/#575）：请求 payload 里确实没有 inventory_digest，
   响应 {"code":"INVALID_REQUEST","category":"validation","retryable":false}（无 message/details）。

4. **core 校验**（service.py:426-496）：要求 sha256: 前缀的 INVENTORY_DIGEST_PREFIX。

**定性：测试期望过时，与组 A / 组 C 完全同类。**

| 组 | 测试假设 | 实际 |
|---|---|---|
| A Fea12* | 旧 core 不含 FEA-12 命令 | core 已含 |
| B B1/B2 | 删除不需要 inventory_digest | 新 core 要求它（fail-closed 是设计） |
| C RunBindingFix | 失败边界在 color | 实际在 	ranslate |

**三组统一性质**：测试写的时候产品行为是 X，现在变成 Y，测试没跟上。
根因是 	est.ps1（配 sidecar 夹具）长期因 legacy v6 副本握手失败而从未真正运行，
这些过时断言一直没被暴露。

**修法（下一轮）**：CommandWiringB1Tests.cs:411-426 已有 inventory_digest 的正确用法样板
（DigestA / withDigest / legacy），把 :236-238 的调用改成带 digest 即可。
**纯测试改动**，不改产品代码（dispatcher 的 passthrough 设计正确）。

**组 B 调查教训（67–74 共 8 轮）**：前 6 轮手搓 probe / 改测试加诊断，5 次同类错误、0 进展；
后 2 轮读仓库自带的 wire log + 源码注释，两轮收敛。**仓库自带的证据比自造 probe 更可靠。**

### 组 B 完全闭环（2026-11-16 续）—— core 要求键集合精确匹配

**证据链（已闭合）**：

1. 测试（CommandWiringB1Tests.cs:236-238）发的 payload 键集合 = {book_id, confirm_permanent_delete}，
   **无 inventory_digest**；
2. dispatcher（:619-638）把 digest 当 **optional**，省略时不写，
   注释明说「legacy caller that omits it ... the new Core fail-closes with INVALID_REQUEST」——
   **设计如此**；
3. 分流层（core_service.py:7015）_DELETE_PROTOCOL_MINOR = 10 与请求 minor:10 一致 ⇒ **不是 minor 问题**；
4. **根因**（core_service.py:2285 _validate_single_delete_payload）：
   `python
   if not isinstance(raw_payload, dict) or set(raw_payload) != {
       "book_id", "confirm_permanent_delete", "inventory_digest",
   }:
       return None, self._delete_error("INVALID_REQUEST", "validation")
   ...
   if not is_inventory_digest(raw_payload.get("inventory_digest")):
       return None, self._delete_error("INVALID_REQUEST", "validation")
   `
   **键集合必须精确等于这三项，digest 必须符合 sha256: 格式。**
   测试少了 digest ⇒ 集合不等 ⇒ 第一步即返回 INVALID_REQUEST（无 message/details，
   与 wire log 帧 #527/#543/#559/#575 完全一致）。

**定性**：测试期望过时（与组 A / 组 C 同类）。产品行为正确（PD-02/PD-04：确认绑定到 Core 计算的 digest）。

**修法（下一轮）**：测试须先取真实 digest 再删除。线索：PreviewPermanentDeleteBooks
属 preview 家族（minor 11）；CommandIntegrationTests.cs:537 用的是**假 digest** 且期望
INVALID_REQUEST（负向控制，本来就该失败）。B1 的 :236-238 是**正向路径**，需真 digest。
⇒ 先确认「单书 inventory digest 由哪个命令返回」，再改测试。

**本轮不改测试的原因**：用假 digest 改会把它改成**另一个错误的期望**
（假 digest 会得到 BOOK_DELETE_STALE_PREVIEW 而非成功）。**先确认数据来源，再改断言。**
