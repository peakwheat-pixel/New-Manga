# TRANS-BINDING-BRIDGE 证据索引（L1-T-A，2026-11-14）

- Task：`doc/tasks/TRANS-BINDING-BRIDGE.md`（`in_progress`，base `73a182a61`）
- 环境：Windows；`C:\Python314\python.exe`（pytest 9.1.1）；仓库主工作树

## 0. 取证结论（先取证再改，AC 前置）

| 问题 | 结论 | 证据（文件:行） |
|---|---|---|
| `settings["providers"]["profiles"]` 存在哪 | **SQLite `pipeline_defaults` 表，`settings_json TEXT` 列，单行 `defaults_id = 1`** | DDL `src/infrastructure/sqlite/schema.py:431-437`；写入 `src/infrastructure/sqlite/pipeline.py:1766-1786`（`set_defaults`，落盘前 `_dump(_redact(settings))`） |
| 谁读写这个 section | `PipelineDefaultsService.save_settings_section(section, values)` 做 `settings[section] = values` 的 upsert；Core 侧 seam 在 `src/bootstrap/core_service.py:3106-3113` | `src/application/settings/pipeline_defaults.py:105-120` |
| P15 profile / 能力绑定存在哪 | **JSON 文件**：`JsonProviderProfileStore(data_root/"settings")` 与 `JsonProviderCapabilityBindingStore(data_root/"settings")` | 装配 `src/bootstrap/core_assembly.py:1943-1945`；写入 `src/bootstrap/settings_commands.py:590-682` |
| 为什么 translate 报 PROVIDER_NOT_CONFIGURED | `_chain` 读 **`run.provider_binding_snapshot[step]`**，该快照来自 `pipeline_defaults.provider_bindings_json`；P15 的 binding 只进 JSON store ⇒ **binding 永远到不了 run** | `src/infrastructure/providers/handlers.py:1266-1274`；冻结 `pipeline.py:1788-1806` |
| Runtime 还需要什么 | `_apply_profile_bindings` 用 `settings["providers"]["profiles"][profile_id]` + `provider_bindings[step]` 把用户 profile 投影到固定注册槽并建 alias；`_openai_config` 读 `base_url`/`model`/`credential_ref`/`options`；`_slot_enabled` 读 `enabled`；网络选择读 `proxy_policy`/`network_profile_id` | `src/infrastructure/providers/runtime.py:418-467`、`:252-271`、`:195-206` |
| 是否已有参考实现 | **有**：legacy QML 设置 viewmodel 已做同一投影（profiles 键集 + `save_provider_binding(step, profile_id)`） | `src/ui/viewmodels/settings/viewmodel.py:453-475`（键集）、`:405`（binding）、`:52-57`（capability→step） |
| 缺口 | 该投影只存在于 legacy QML UI；**Core P15 命令面没有任何镜像写入方**，所以 Host/Avalonia 客户端写完配置后运行侧看不到 | 上两行对比 |

**由取证得出的一个关键修正**：AC1 只点名 profiles 镜像，但 `_chain` 的 `PROVIDER_NOT_CONFIGURED` 直接来自 **binding** 缺失。故桥必须写两处（profiles + `provider_bindings[step]`），否则症状不变。两处都走既有 `PipelineDefaultsService` seam，未新增任何 wire 命令/端口成员。

## 1. AC 逐条

| AC | 结论 | 交付 | 判别测试 |
|---|---|---|---|
| **AC1 镜像写入** | **PASS** | `src/application/settings/provider_runtime_mirror.py`（镜像键集与 runtime 一致，另带 `capabilities` 供诊断）；`settings_commands.py` 的 profiles create/update/delete、bindings set/clear、BindProfileCredential/ClearProfileCredential 六处接线 | `tests/core/test_trans_binding_bridge.py::test_profile_and_binding_are_mirrored_into_run_settings`（并断言 runtime 投影槽与 alias）、`::test_profile_update_and_delete_keep_the_mirror_in_sync`、`::test_binding_clear_removes_the_mirrored_step_binding` |
| **AC2 只含引用** | **PASS** | 镜像只含 `credential_ref`；secret 从不经过此面 | `::test_mirror_carries_credential_ref_but_never_the_secret`（断言 ref 在、`api_key`/`secret`/`password`/`bearer ` 全不在） |
| **AC3 fail-closed** | **PASS** | **mirror-first + store-after + 失败则 restore**：镜像失败 → 不写 JSON store；store 失败 → 回滚镜像。典型半写（store 已写、镜像未写）在结构上不可能出现 | `::test_profile_mirror_failure_is_typed_and_leaves_no_half_write`、`::test_binding_mirror_failure_rolls_back_the_binding_rows`（typed `SETTINGS_UNAVAILABLE` + 两侧均空） |
| **AC4 复用 seam** | **PASS** | 只经 `PipelineDefaultsService.save_settings_section` / `save_provider_binding` / `clear_provider_binding`；未新增 persistence 实现 | 代码评审面；loader 注入点在 `core_assembly.py:1827-1833` |
| **AC5 不新增契约面** | **PASS** | 无新 wire 命令、无 `IHostController` 成员；`generate_api_inventory --check` 仍 `1/80/6=87`；`verify_pins` 18/18 | `logs/gates-final.log` |
| **AC6 判别测试** | **PASS** | 7 例；含「写入 profile+binding 后 runtime 侧读得到」与「镜像失败不留半写」 | `tests/core/test_trans_binding_bridge.py` |
| **AC7 门禁** | **PASS** | 定向 108 passed（7 新 + 101 既有 P15）；全量 pytest 见 §3；四门禁 EXIT=0 | `logs/pytest-full.log`、`logs/gates-final.log` |
| **AC8 生效时机** | **PASS（文档）** | 见 §2 | `core_assembly.py:1421-1426` |

## 2. AC8 生效时机（供 T-C 的 UI 文案）

`src/bootstrap/core_assembly.py:1421-1426` 在**装配期一次性**闭包 runtime 输入：

```
provider_runtime = build_provider_runtime(
    settings=_load_pipeline_settings(conn),
    provider_bindings=_load_pipeline_defaults(conn)["provider_bindings"],
    ...
)
```

即 **P15 配置变更（profile 字段 / 能力绑定 / credential ref）必须重启 Core 才生效**；运行中的 Run 使用其冻结快照不变。UI 文案应写「配置已保存；重启 Core（或重新连接）后生效」，不得宣称即时生效。

## 3. 测试与门禁（原始输出见 logs/）

- 定向：`pytest -q tests/core/test_trans_binding_bridge.py tests/core/test_p15_core_settings.py` → **108 passed**
- 全量：`logs/pytest-full.log`
- 门禁：`logs/gates-final.log`（`check.ps1` 默认 + 本卡 TaskPath、`verify_pins`、`generate_api_inventory --check`）

## 4. 判别力（实现被回退时测试会红）

用探针把 `ProviderRuntimeMirror.upsert_profile` / `bind_capability` 换成 no-op（模拟回退），同一串 wire 调用后：

```
WITH mirror:    profiles=['5950acb5…']  bindings={'translate': '5950acb5…'}
WITHOUT mirror: profiles=[]             bindings={}
```

即镜像被移除时两处断言都会失败（`test_profile_and_binding_are_mirrored_into_run_settings` 直接红），不是「只断言不抛异常」。

## 5. 未做 / limitation（已登记）

1. **网络 profile 镜像不在本卡**：legacy QML 还镜像 `settings["providers"]["networks"]`（`viewmodel.py:485-520`），本卡按 AC1 只覆盖 provider profiles；`proxy_auth` 凭据绑定的写路径保持原样（`settings_commands.py` 中 `kind != CREDENTIAL_KIND_PROVIDER` 分支）。影响：若用户配置代理并要求 `proxy_policy=profile`，运行侧仍可能看不到 networks 镜像 —— 属既有缺口，需另卡（不得在本卡静默扩面）。
2. **`Rendering` capability 没有 pipeline step**：写入 P15 行但不创建设置 steps（`test_rendering_capability_never_invents_a_pipeline_step`），不臆造步骤。
3. **双写不是跨库事务**：JSON store 与 SQLite `pipeline_defaults` 是两个存储，无法真事务；本卡用「mirror-first + 失败回滚」保证 AC3 禁止的那个方向（store 已写、镜像未写）不出现；反向窗口（镜像已写、store 写失败但回滚本身失败）已尽力回滚并留 typed 失败。
4. **未验证真实 Host↔Core 端到端**：本卡只跑 Core 层；T-B/T-C 接 Host/UI 后需一条真实链路证据。