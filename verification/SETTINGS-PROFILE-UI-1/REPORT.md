# SETTINGS-PROFILE-UI-1 验证报告（设置页 profile 管理 UI：provider / network / bindings）

- Task：`doc/tasks/SETTINGS-PROFILE-UI-1.md`（team task-45）
- Branch / worktree：`task/SETTINGS-PROFILE-UI-1` / `G:/CODEX/New Manga.workspace/worktrees/SETTINGS-PROFILE-UI-1`
- Base：`327aa8526`（DSH 指定当前 HEAD；卡面 `dde7f50ee` 为前一次集成点）
- 未改 Python Core / 协议 / Host 契约 / 旧壳；未 push / gc / prune；未显示/记录任何 credential secret；未伪造 test 诊断结果。

## 1. 结论

| AC | 结论 | 证据 |
|---|---|---|
| AC1 provider profile 表单 | **MET** | 设置页新增「Provider Profile 管理」卡：列表（display_name · provider_id · capabilities · enabled）+ 新建/编辑/删除表单（display_name、provider_id、capabilities 复选、endpoint、model、network_profile、enabled，按 P15 schema）；成功/失败 typed 提示（`SETTINGS_CONFLICT`/`SETTINGS_ITEM_NOT_FOUND`/`SETTINGS_INVALID_INPUT`/`TLS_CONFIRMATION_REQUIRED`…）；空态文案。 |
| AC2 network profile 表单 | **MET** | 「Network Profile 管理」卡：列表 + CRUD（display_name、mode=Direct/System/HTTP/HTTPS/SOCKS5、proxy_endpoint、verify_tls、确认关闭 TLS 校验、fallback）+「测试网络」显示 Core 真实 6 段诊断（status/failed_stage/stages）+「解析网络」显示 `network_profile_id/mode/source`；不可用时明确显示「不可用」，不伪造 pass。 |
| AC3 绑定/默认 | **MET** | 「Provider 绑定（slot）」卡：scope（global/book/chapter）+ capability（OCR/Translation/Inpaint/Detection/Rendering）+ provider profile → `settings_provider_bindings_set/clear/resolve`；Network Profile 卡内「设为默认/清除默认」→ `settings_network_profile_default_set/clear`。 |
| AC4 测试 | **MET** | 10 项 headless（CRUD 精确参数、typed 错误、空态、test/resolve 渲染、TLS 确认、bindings 各 scope、页面接线、payload 契约）+ 真机截图 2 张（provider 表单 / network 表单，含滚动可达性）。 |
| AC5 回归/门禁 | **MET** | `scripts/test.ps1` **210/210 passed, 0 skipped**（coreclient 61 / host 55 / app 94）；vitest **60 files / 567 tests**；pytest **3F/2772P/9S**（与基线同一组 3 失败，0 新增）；`check.ps1 -TaskPath` PASS；15 条 64-hex pin；Handoff 含 Record Decision。 |

## 2. UI 结构（SettingsPage 右侧，凭据卡之后）

```
Provider Profile 管理
  [列表]  空态：尚无 provider profile。填写下面的表单后点「新建」…
  显示名称 / Provider 类型 / 能力(OCR,Translation,Inpaint,Detection,Rendering) / Endpoint / 模型 /
  绑定的 network profile / 启用          [新建] [新建并保存|保存修改] [删除] [刷新]   ← 状态行

Network Profile 管理
  [列表]  空态：尚无 network profile…
  显示名称 / 模式(Direct/System/HTTP/HTTPS/SOCKS5) / 代理地址 / 校验 TLS /确认关闭 TLS 校验 / 代理失败回退直连
  [新建] [新建并保存|保存修改] [删除] [刷新] [设为默认] [清除默认]
  provider 选择 + [测试网络] [解析网络] → 诊断结果 / 解析结果文本

Provider 绑定（slot）
  Scope 类型(global/book/chapter + id) / 能力 / Provider profile
  [绑定] [清除绑定] [解析当前绑定] [刷新 provider 列表]   状态行 + 解析结果
```

全部调用走 `IHostController` 新 seam：`ListProviderProfilesAsync` / `SaveProviderProfileAsync` / `DeleteProviderProfileAsync` / `ListNetworkProfilesAsync` / `SaveNetworkProfileAsync` / `DeleteNetworkProfileAsync` / `SetNetworkDefaultAsync` / `TestNetworkProfileAsync` / `ResolveNetworkProfileAsync` / `SetProviderBindingAsync` / `ClearProviderBindingAsync` / `ResolveProviderBindingAsync`；生产实现转 `HostCommandDispatcher` 既有命令（未新增/修改 Host 命令）。

## 3. Record Decision

| 项 | 决定 | 依据 |
|---|---|---|
| 字段/schema | 严格按 P15：capabilities ∈ CAPABILITY_NAMES；mode ∈ Direct/System/HTTP/HTTPS/SOCKS5；provider update 不带 provider_id（Core 保留原类型）；network create 的 verify_tls/fallback 可选、update 必填、关闭 TLS 需 confirm | `src/bootstrap/settings_commands.py` 校验分支 |
| payload 构造 | App 层 `SettingsProfilePayload` 显式构造，键与 `HostCommandDispatcher` 完全一致（NULL 显式传递；binding scope 只含 kind[/book_id|chapter_id]）；headless payload 契约测试钉住 | dispatcher `WriteCorePayload` |
| 空态/不可用 | 列表为空显示空态文案；test/resolve 在 Host/Core 不可用或无结果时显示「不可用」，**绝不伪造 passed** | 卡面「不得伪造 test 诊断结果」 |
| 错误呈现 | `SETTINGS_*`/`TLS_CONFIRMATION_REQUIRED` 映射为中文 typed 提示，不向 UI 抛异常 | AC1/AC2 typed 提示 |
| 绑定 UI | scope 三种；book/chapter 需填 id（本地校验后仍由 Core 复核存在性）；绑定结果只显示 profile_id/source | AC3 |
| 页面可达性 | 新增卡片后设置页整体超过窗口高度 → 内容行改为 `ScrollViewer`（否则 provider/network/bindings 会被裁掉；真机截图发现并修复） | AC4 真机截图 |
| 测试边界 | UI 用 `FakeHostController` 记录参数，不写真实 `%APPDATA%`；network test 的诊断文本来自脚本化 Host 结果（真实链路已由 NS-WIRE-B2 对冻结 sidecar 验证） | 卡面环境要求 |
| 并行 flake | App.Tests 中既有 `ShellCommandCatalog.WriteEvidence` 在同进程并发写同一证据文件时偶发 `File.Create` 冲突（与本卡无关，单独重跑/标准 gate 均通过），如实记录 | 全量复跑验证 |

## 4. 实现摘要（全部 `apps/desktop-avalonia/**`）

| 文件 | 改动 |
|---|---|
| `Services/SettingsProfileContracts.cs`（新） | capability/mode 常量、Provider/Network profile 记录、scope、typed result、15 条命令 payload 构造、`SETTINGS_*` 映射。 |
| `Services/IHostController.cs` | 新增 12 个 profile/binding/default/test/resolve 方法。 |
| `Services/HostController.cs` | 实现：profile list 解析（`profiles[]`、`credential_state`、`tls_verification_state`）、CRUD、default、test 诊断解析（6 stage）、resolve、binding set/clear/resolve；错误映射为 typed 结果。 |
| `Services/NullHostController.cs` | 设计时路径：空列表 + HOST_NOT_READY。 |
| `Views/ProfileSections.cs`（新） | `ProviderProfileSection` / `NetworkProfileSection` / `ProviderBindingsSection` 三个卡片（列表、表单、空态、typed 状态、错误与诊断展示）。 |
| `Views/Pages.cs` | SettingsPage 嵌入三卡 + `RefreshProfilesAsync()`；内容行改 `ScrollViewer`。 |
| `Views/MainWindow.axaml.cs` | Host 就绪与进入设置页时刷新 profile 列表。 |
| `tests/NewManga.App.Tests/SettingsProfileUiTests.cs`（新，10 项） | CRUD 参数/空态/typed 错误/test-resolve 渲染/TLS 确认/bindings scope/页面接线/payload 契约。 |
| `tests/NewManga.App.Tests/FakeHostController.cs` | 脚本化 profile 端口（记录每次调用的精确参数，默认完成并更新可见列表）。 |

## 5. 验证证据

| AC/场景 | 实际命令/步骤 | 环境 | 结果 | 产物 |
|---|---|---|---|---|
| AC1 空态→创建 | `ProviderSection_EmptyState_ThenCreate_SendsExactDraft` | Avalonia Headless 11.3.22 + FakeHostController | 空态可见；save 参数 (provider_id=openai, display=DeepSeek, capabilities=[OCR,Translation], endpoint, model, network=null, enabled=true) 精确；列表+状态更新 | `settings-profile-ui/provider-create.json` |
| AC1 更新/删除 | `ProviderSection_UpdateAndDelete_SendProfileId` | 同上 | update 带 profile_id=profile-1；delete 记录 id；删除后空态 | `provider-update-delete.json` |
| AC1 typed 错误 | `ProviderSection_TypedError_AndLocalValidation_AreRendered` | 同上 | `SETTINGS_CONFLICT` 中文提示；本地缺 display_name → INVALID_ARGUMENTS 且 0 调用 | `provider-error-feedback.json` |
| AC2 空态→创建/模式规则 | `NetworkSection_EmptyState_Create_SendsExactDraft` | 同上 | HTTPS+proxy endpoint 精确；HTTP 缺 endpoint 本地拒绝 0 调用；Direct 模式 proxy_endpoint=null | `network-create.json` |
| AC2 test/resolve | `NetworkSection_TestAndResolve_RenderCoreResult_AndNeverFabricate` | 同上 | 未 scripted → 「不可用」；Core 结果 → `status=passed`、`ProviderAuth:passed`、`TLS:not_applicable`；resolve 显示 `network_profile_id=network-1 … source=global` | `network-test-resolve.json` |
| AC2 TLS/默认/删除 | `NetworkSection_TlsConfirmationRequired_IsRendered`、`NetworkSection_Delete_And_DefaultSetClear` | 同上 | `TLS_CONFIRMATION_REQUIRED` 提示；default set/clear 与 delete 调用参数正确 | `network-tls-confirmation.json`、`network-default-delete.json` |
| AC3 bindings | `BindingsSection_SetClear_WithGlobalAndBookScopes_SendExactArguments` | 同上 | global(OCR→profile-1)、book(book-1 Translation→profile-1)、clear(book) 参数精确 | `bindings-set-clear.json` |
| AC4 页面接线 | `SettingsPage_WiresAllProfileSections_ToTheController` | 同上 | 三卡均有数据；provider 表单正确回填 network_profile | `settings-wiring.json` |
| AC4 payload 契约 | `PayloadContract_MatchesTheDispatcherKeys` | 无 UI | provider/network/binding/test/resolve/default 键集与 dispatcher 一致；mapper typed | `payload-contract.json` |
| AC4 真机截图 | Debug `NewManga.App.exe`（隔离 `NEWMANGA_DATA_ROOT`）→ 设置页 → 滚动 | Windows 10.0.26300；1278×818 | provider/network 卡片及表单完整可见（修复 ScrollViewer 前被裁切） | `real-app-provider-profile.png`、`real-app-network-profile.png`、`real-app-screenshots.json` |
| AC5 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence` | Windows 10.0.26300 | **210/210**（61/55/94），0 skipped | `test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC5 vitest | `cd apps/desktop/frontend && npm test`（主仓；旧壳未改） | 旧壳未改 | **60 files / 567 tests** | `test/vitest.log` |
| AC5 pytest | `PYTHONPATH=src python -m pytest -q`（worktree，未改 Python） | 未改 Core | **3F/2772P/9S**（同一组 3 失败，0 新增） | `test/pytest.log` |
| AC5 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/SETTINGS-PROFILE-UI-1.md` | 本卡 + 文档提交 | PASS | 任务卡 pin |

## 6. 遗留 / 未关闭项（记录不阻塞）

1. **真实 Host 全链**：本卡 UI 测试用 `FakeHostController`（卡面要求不污染 `%APPDATA%`）；profile CRUD/test/resolve 的真实 Core 链路由 NS-WIRE-B2/NS-WIRE-B1 的冻结 sidecar 测试覆盖，本卡不重复写真实数据根。
2. **真机截图时 Host 未就绪**（Debug 构建无 sidecars）→ 列表为空态；表单、空态、滚动可达性已验证；有真实 profile 时列表/回填逻辑由 headless 覆盖。
3. **provider 类型是自由文本**：provider_id 未做白名单（Core 也不限制），后续可在数据层给出建议列表；endpoint/model 同样自由文本，由 Core 校验 URL/必填。
4. **book/chapter scope 的 id 输入是文本框**：尚未接书籍/章节选择器；后续可与阅读器/书架联动。
5. **network test 的 ProviderAuth 阶段**依赖 provider 配置了凭据；UI 只渲染真实结果，不做额外提示优化。
6. App.Tests 既有 `ShellCommandCatalog.WriteEvidence` 并发写同一文件偶发失败（与本卡无关，单跑/标准 gate 通过），已记录。
7. 需独立 Review（Owner 不自审）。

## 7. 复现

```pwsh
# 1) 全量回归（210 项，含 10 项 profile UI headless）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 `
  -EvidenceDirectory G:\CODEX\New Manga.workspace\task-envs\SETTINGS-PROFILE-UI-1\evidence

# 2) 只看 profile UI 测试
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj `
  -c Debug --filter "FullyQualifiedName~SettingsProfileUiTests"

# 3) 真机截图复现（隔离数据根，不写真实 %APPDATA%）
$env:NEWMANGA_DATA_ROOT='G:\CODEX\New Manga.workspace\task-envs\SETTINGS-PROFILE-UI-1\screenshot-root'
Start-Process apps/desktop-avalonia/src/NewManga.App/bin/Debug/net9.0/NewManga.App.exe
# 设置页 → 向下滚动查看 Provider/Network/Bindings 三卡
```
