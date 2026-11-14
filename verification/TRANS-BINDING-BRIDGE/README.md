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
| **AC6 判别测试** | **PASS** | **18 例**（7 首版 + 3 scope 分流 + 8 反向/异常族）；含「写入 profile+binding 后 runtime 侧读得到」与「镜像失败/回滚不留半写」 | `tests/core/test_trans_binding_bridge.py` |
| **AC7 门禁** | **PASS** | 定向 **119 passed**（18 bridge + 101 既有 P15）；全量 pytest 见 §3；四门禁 EXIT=0 | `logs/pytest-full.log`、`logs/gates-final.log` |
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

- 定向：`pytest -q tests/core/test_trans_binding_bridge.py tests/core/test_p15_core_settings.py` → **119 passed**（18 bridge + 101 P15）
- 全量：`logs/pytest-full.log`
- 门禁：`logs/gates-final.log` —— 每节首行即**完整可复制命令**（工作目录 = 仓库根）：`pwsh -NoProfile -File tools/governance/check.ps1` / `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/TRANS-BINDING-BRIDGE.md` / `pwsh -NoProfile -File tools/governance/verify_pins.ps1` / `C:\Python314\python.exe tools/generate_api_inventory.py --check`

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
## 6. r1 复核处置（`doc/reviews/TRANS-BINDING-BRIDGE-r1.md`，reviewed_head `94b8f33f5`）

### 6.1 P1-1：binding 镜像必须按 scope 分流（已修）

**scope 语义取证（文件:行）**：

| 事实 | 证据 |
|---|---|
| 执行链只读**扁平**的 step 槽：`handlers._chain` 读 `run.provider_binding_snapshot.get(step_type)` | `src/infrastructure/providers/handlers.py:1267`；同样读取点 `src/infrastructure/pipeline/executor.py:27`、`src/application/tasks/projection.py:285`、`src/application/tasks/service.py:797` |
| run 快照里**没有 per-book step 槽**：P15 的 book/chapter 解析结果被塞进 `provider_binding_snapshot[_p15_settings_snapshot]`，仅供 `settings_provider_bindings_resolve` 显示 | `src/bootstrap/core_service.py:6707-6709`；构建 `src/bootstrap/settings_commands.py:589-627`（`prepare_run_snapshot` 用 `_scope_context(scope)` + `_resolve_current_binding(capability, book_id=…, chapter_id=…)`） |
| `provider_bindings` 是 `{step: profile_id}` 的扁平表，没有 scope 维度 | `src/application/settings/pipeline_defaults.py:62-103`；`src/infrastructure/sqlite/pipeline.py:1766-1786` |

**结论**：能表达「谁在跑」的只有全局扁平槽，所以**只有 global scope 的 P15 绑定可以写它**；book/chapter scope 的写入与清除一律不碰扁平槽（否则 book 绑定会劫持全局执行链、clear 一个无关/空 scope 会抹掉全局配置）。

**改动**：`src/bootstrap/settings_commands.py` 的 `_bindings_set` / `_bindings_clear` 增加 `writes_flat_slot` / `clears_flat_slot = scope["kind"] == "global"` 判定；非 global 只写 P15 JSON 行。

**新增判别测试**：
- `test_book_scoped_binding_does_not_overwrite_the_global_step`（global=A → book=B，扁平槽仍为 A，且 P15 resolve 对该书返回 B）
- `test_clearing_a_book_scope_never_clears_the_global_step`
- `test_clearing_a_chapter_scope_never_clears_the_global_step`

### 6.2 P1-2：AC3 反向窗口（已修 + 已登记）

**捕获范围与选型原则**（不做无脑 `except Exception`）：`_write_with_rollback` 现捕获
`(BindingValidationError, KeyError, OSError, TypeError, ValueError)` —— 这正好是两个协作者**实际会抛出**的异常族：

| 异常 | 来源 |
|---|---|
| `BindingValidationError` | pipeline-defaults seam 自身校验（`application/settings/errors.py`） |
| `KeyError` | `JsonProviderProfileStore.update_profile` 对缺失行显式抛（`src/infrastructure/settings/json_profile_stores.py:162-164`） |
| `OSError` | JSON 读/写/`os.replace`（`json_profile_stores.py:32-40`） |
| `sqlite3.Error` | **r2 R2-001**：镜像唯一持久化是 SQLite（`pipeline_defaults` 行，`pipeline.py:1766-1786`）；SQLite 写失败与 `OSError` 同类（存储不可写），必须回滚并转 typed，不是编程错误 |
| `ValueError` | `ProfileFileFormatError`（`json_profile_stores.py:28`，ValueError 子类）/ `json.JSONDecodeError` / dataclass 校验 |
| `TypeError` | JSON 序列化异常值的防御 |

其余（`AttributeError`/`NameError`/`RuntimeError` …）属编程错误，**故意不捕获**，让其保持响亮，而不是被转成业务级 `SETTINGS_UNAVAILABLE`。

**反向判别测试**（镜像先写、后写失败；覆盖 store 四条写路径 + 全部捕获族）：
- `test_store_update_failure_rolls_the_mirror_back`（`update_profile` 抛 `KeyError` ← r1 实测的那条）
- `test_store_create_failure_rolls_the_mirror_back`（`add_profile` 抛 `OSError`）
- `test_store_delete_failure_restores_the_mirror`（`delete_profile` 抛 `OSError`）
- `test_store_binding_failure_rolls_the_mirror_back`（`save_bindings` 抛 `OSError`）
- `test_sqlite_write_failure_rolls_the_mirror_back`（**r2 R2-001**：`set_defaults` 抛 `sqlite3.OperationalError`，一次性失败以便回滚可成功）
- `test_store_format_error_rolls_the_mirror_back`（`ValueError` 族：`ProfileFileFormatError`）
- `test_store_type_error_rolls_the_mirror_back`（`TypeError` 族：JSON 序列化失败）

全部断言：typed `SETTINGS_UNAVAILABLE` + 镜像回到调用前值 + 与 JSON 侧一致（详见 §6.3 的逐项回退敏感性矩阵）。

**仍无法保证的反向窗口（如实登记，不含糊）**：

1. **回滚本身失败**：若回滚调用（`mirror.restore` / `upsert_profile(old)`）也抛错（例如同一 SQLite 已不可写），`_write_with_rollback` 会吞掉回滚异常并仍抛 typed 失败 —— 此时留下「镜像新值 / JSON 旧值」，**只能靠下一次成功写入或重启后的人工核对**。没有跨库事务可用。
2. **进程在两次写之间被强杀**：镜像已提交、JSON 未写（或反之）无崩溃恢复标记；两者是不同存储、无 WAL 级协调。
3. **JSON 文件被外部并发改写**：store 是「读-改-原子写」，外部写者会造成丢失更新（既有风险，与本桥无关）。
4. **book/chapter scope 绑定不驱动执行**：扁平槽只接受 global（§6.1）⇒ 仅配置 book-scope 绑定时 `_chain` 仍会 `PROVIDER_NOT_CONFIGURED`。这是当前 run 快照结构的固有限制（无 per-book step 槽），需另卡在 run 快照上加 scope 维度，不在本卡。
### 6.3 捕获族逐项回退敏感性矩阵（r2 R2-002 自查，实测）

方法：把 `_write_with_rollback` 的捕获元组**逐项删掉一个成员**，每次只跑 `tests/core/test_trans_binding_bridge.py`（文件字节逐次从备份还原，还原后 SHA-256 一致）。「红」= 该成员的保证确实被测试覆盖。

| 回退的成员 | 结果 | 变红的用例 |
|---|---|---|
| `KeyError` | **1 failed** | `test_store_update_failure_rolls_the_mirror_back` |
| `OSError` | **3 failed** | `test_store_create_failure_rolls_the_mirror_back`、`test_store_delete_failure_restores_the_mirror`、`test_store_binding_failure_rolls_the_mirror_back` |
| `TypeError` | **1 failed** | `test_store_type_error_rolls_the_mirror_back` |
| `ValueError` | **1 failed** | `test_store_format_error_rolls_the_mirror_back`（`ProfileFileFormatError` 是 ValueError 子类） |
| `sqlite3.Error` | **1 failed** | `test_sqlite_write_failure_rolls_the_mirror_back`（**r2 R2-001**；失败发生在写入提交之后，否则前后值相同、证明不了回滚） |
| `BindingValidationError` | **0 failed（冗余成员，如实登记）** | — |

**关于 `BindingValidationError` 为 0 红的解释（不是漏测）**：`BindingValidationError → SettingsError → ValueError`（`src/application/settings/errors.py:6,22`，运行期 `issubclass(..., ValueError) is True`），所以它**已被 `ValueError` 完全覆盖**，删除后行为不变。保留该成员只为**显式表达意图**（并防止未来有人改基类时静默失去保证），不构成独立保证。相应新增的 `test_seam_validation_error_after_write_rolls_back_the_mirror` 证明的是「镜像已提交、随后 seam 抛错 ⇒ 回滚」这条路径，它由 `ValueError` 分支接住（回退 `ValueError` 时该用例同样变红，见上表第 4 行口径）。

**另一个必须写清的事实**：P15 命令的 dispatch 外层有 catch-all（`src/bootstrap/core_service.py:7317-7324`），任何逃出 `_write_with_rollback` 的异常都会被映射成 `SETTINGS_UNAVAILABLE`。因此**wire 错误码不是判别信号**——本桥测试的判别信号是「镜像是否回到调用前值 + 与 JSON 侧是否一致」，这也是上表用「镜像状态」而非错误码来衡量敏感性的原因。