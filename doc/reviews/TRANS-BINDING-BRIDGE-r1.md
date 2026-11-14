---
task: TRANS-BINDING-BRIDGE
reviewer: independent sub-agent (r1, read-only)
reviewer_kind: subagent
reviewer_agent: agent-3（由 lead 派发；独立上下文，未参与实现）
verdict: changes_requested
date: 2026-11-14
reviewed_head: 94b8f33f5
base_commit: d38c624f7
scope: read-only
---

# Review：TRANS-BINDING-BRIDGE（L1-T-A）r1

> **结论：P1 未闭合，判 `changes_requested`。** 桥的核心方向真实成立：`settings["providers"]["profiles"]` 确实在 SQLite `pipeline_defaults.settings_json`，`PROVIDER_NOT_CONFIGURED` 确实来自 `_chain` 读 `run.provider_binding_snapshot[step]`；双写、键集、AC2、AC4、AC5、AC7、AC8 均通过自跑复核；**AC3 按卡面文字判 PASS（不判 PARTIAL）**。但发现两个 P1：① 能力绑定的镜像**完全忽略 scope**，book/chapter 的 set/clear 会覆盖或清空全局 step binding，能把本卡要修的 `PROVIDER_NOT_CONFIGURED` 重新制造出来（实测）；② AC3 的**反向路径（store 失败 → 回滚镜像）没有任何测试**，且 `_write_with_rollback` 的异常白名单漏掉 `KeyError`，实测会留下「镜像新值 + JSON 旧值」的半写。另有 6 项 P2（R-003…R-008）。

## 0. 范围、身份与复核方法

- 复核对象：`94b8f33f5`（父 `d38c624f7`），6 文件 +860/−19；只读，未参与实现，未修改任何既有文件。
- 复核期间 lead 追加了 `3a1183681`（仅 `doc/tasks/TRANS-BINDING-BRIDGE.md` +33，交付记录/DSH 裁决），已 `git diff 94b8f33f5 3a1183681` 确认**无代码变化**；本报告的 `reviewed_head` 仍固定为 `94b8f33f5`。复核时工作区已 clean，HEAD 为 `3a1183681`。
- 方法：逐行读代码 + 行号核对；在 `%TEMP%` 的一次性临时数据目录里直接装配 `assemble_production_core` / `CoreServiceServer` 做只读探针（不写仓库）；实际运行 pytest、四门禁；用临时 pytest 插件把镜像 no-op 后重跑新增 7 例，验证判别力。
- 仓库内唯一新增文件是本报告；临时探针/日志均在 `%TEMP%`。

## 1. 逐项结论

| # | 复核项 | 结论 | 关键证据 |
|---|---|---|---|
| 1 | 两条取证结论是否真实 | **PASS** | §2；`schema.py:431-437`、`pipeline.py:1766-1786`、`handlers.py:1266-1274` 均逐行核对成立 |
| 2 | profiles 与 `provider_bindings[step]` 双写、键集与 runtime 一致 | **PASS（全局路径）** | §3；六处接线；`_openai_config`/`_slot_enabled`/`_network_profile_for`/`_registry_target_for_step` 所需键全部在镜像中；实测 `_apply_profile_bindings` 产出 alias，`freeze_run_snapshots` 产出 `execution` |
| 3 | AC2 无密钥泄漏 | **PASS** | §4；新增代码只有 `credential_ref`；全 diff 搜索 `api_key/apikey/secret/password/bearer` 仅命中注释与断言；落盘另有 `_redact` 兜底 |
| 4 | AC3 原子性 | **PASS（按卡面 AC3 文字，不判 PARTIAL）** | §5；禁止方向结构上排除；反向窗口为已披露 limitation，但存在 R-002 的实现漏洞 |
| 5 | 7 例判别测试真实性 | **PASS（6/7 有判别力）；AC3 反向无测试 → R-002** | §6；no-op 实测 `6 failed, 1 passed`；两例 AC3 测试都只覆盖 mirror-first 方向 |
| 6 | `BindProfileCredential`/`ClearProfileCredential` 接线是否越权 | **PASS（必要，非越权）** | §7；`credential_ref` 是 runtime profile 形状的一部分；不接则镜像永久保留 `None` |
| 7 | 零契约面 | **PASS** | §8；`apps/**` 零改动；handler map 未增；`core_service.py` 未改；inventory EXIT=0（80+6=87）；pins 18/18 |
| 8 | 实跑测试/门禁 | **PASS（带一处证据标签错误）** | §9；全量 `3551 passed / 10 skipped / 0 failed`；定向 `108 passed`；四门禁绿 |
| 9 | 新问题（脏数据/删除同步/enabled=false） | **部分 PASS + 新发现** | §10；删除同步 OK；`enabled=false` 被正确忽略但需重启；镜像写失败本身不留脏数据，**rollback 再失败会留**；另发现 scope 与无回填两问题 |

**AC 逐条**：AC1 **PARTIAL**（全局路径 PASS；scoped binding 镜像不忠实 → R-001；「同一事务」不成立、「同一 seam」成立）；AC2 PASS；AC3 PASS；AC4 PASS；AC5 PASS；AC6 PASS（但见 R-002）；AC7 PASS；AC8 PASS（文档口径正确，见 R-008）。

## 2. 取证核实（复核项 1）

| 实现者声称 | 独立核对 | 结果 |
|---|---|---|
| `settings["providers"]["profiles"]` 在 SQLite `pipeline_defaults` 表 `settings_json` 列（`schema.py:431-437`、`pipeline.py:1766-1786`），不是独立 JSON 文件 | DDL 实际为 `CREATE TABLE pipeline_defaults (... settings_json TEXT NOT NULL, provider_bindings_json TEXT NOT NULL ...)`（`src/infrastructure/sqlite/schema.py:431-437`）；`set_defaults` 以 `INSERT ... ON CONFLICT DO UPDATE` 写 `settings_json`（`src/infrastructure/sqlite/pipeline.py:1766-1786`）；全仓 grep 无 `pipeline_defaults.json`/`settings.json` 旁路，`ProviderRuntime` 由 `_load_pipeline_settings(conn)` 读该列（`core_assembly.py:770-784`、`:1421-1423`） | **成立** |
| `PROVIDER_NOT_CONFIGURED` 的直接来源是 `_chain` 读 `run.provider_binding_snapshot[step]`（`handlers.py:1266-1274`），故只镜像 profiles 不够 | `_chain` 原文即 `binding = run.provider_binding_snapshot.get(step_type)`；`chain_from_binding(None) is None` → 抛 `ProviderNotConfigured`（实测其 `error_code == "PROVIDER_NOT_CONFIGURED"`）；快照来自 `pipeline_defaults.provider_bindings_json`（`pipeline.py:1808`、`application/tasks/service.py:303`） | **成立** |
| P15 profile/binding 存 JSON 文件（`core_assembly.py:1943-1945`） | `JsonProviderProfileStore(data_root/"settings")`、`JsonProviderCapabilityBindingStore(data_root/"settings")` 原文成立；写盘为 `json_profile_stores.py` 的 tmp+`os.replace` | **成立** |
| legacy QML 已有同投影（`viewmodel.py:453-475`、`:405`、`:52-57`） | 三处行号均核对成立：`:52-57` capability→step、`:405` `save_provider_binding`、`:453-475` profile 键集 | **成立** |
| 其它被引用行号（`runtime.py:182-193/195-206/252-271/324-347/418-467`、`core_assembly.py:1421-1423`） | 逐段核对成立 | **成立** |

没有发现取证造假。唯一需要补注的是：`gates-final.log` 的 `HEAD=d38c624f7` 是**父提交**，门禁是在提交前的 dirty 工作树上跑的（见 R-004）。

## 3. 双写与键集（复核项 2）

- 接线共六处，全部 mirror-first（`src/bootstrap/settings_commands.py`）：
  - `_profiles_create`（`:654-664`）、`_profiles_update`（`:692-703`）、`_profiles_delete`（`:716-725`）；
  - `_bindings_set`（`:741-756`）、`_bindings_clear`（`:767-778`）；
  - `BindProfileCredential`（`:369-387`）、`ClearProfileCredential`（`:420-429`）。
- profiles 侧：`ProviderRuntimeMirror.upsert_profile` 把 `provider_type/base_url/model/credential_ref/enabled/options/network_profile_id/proxy_policy/capabilities` 写入 `settings["providers"]["profiles"][profile_id]`（`provider_runtime_mirror.py:66-84`、`:119-124`）。
- binding 侧：`bind_capability/clear_capability` 调用 `save_provider_binding(step, profile_id)` / `clear_provider_binding(step)`（`:135-148`），键为 `detect/ocr/translate/inpaint`（`CAPABILITY_TO_STEP`，`:51-56`）。P15 wire 字面量先经 `CAPABILITY_TO_MODEL` 归一（`settings_commands.py:745`、`:769`），映射正确。
- 键集与 `runtime.py` 读取面一致：`_openai_config` 读 `base_url/model/credential_ref/options`（`:252-271`）；`_slot_enabled` 读 `enabled`（`:195-206`）；`_network_profile_for` 读 `proxy_policy/network_profile_id`（`:324-347`）；`_registry_target_for_step` 读 `provider_type`（`:396-403`）；`capabilities` 为额外诊断字段，runtime 不读。**全部命中，无缺键。**
- 实测（临时目录、真实装配）：写入 profile+binding 后 `_apply_profile_bindings` 返回 `{('p1','translation'): 'openai-compatible-translation'}`；用镜像状态重建 runtime 后 `freeze_run_snapshots` 的 `translate` 条目含 `execution`（`base_url/model/credential_ref` 正确），说明镜像形状可被真实 run 冻结消费。
- 注意：`capabilities` 是多余的镜像键；不构成 AC1 失败，但属于「比 runtime 读取面更宽」的额外形状（P2 级观察，不单列 finding）。

## 4. AC2 无密钥泄漏（复核项 3）

- `profile_mirror_entry` 只输出 `credential_ref` 一个凭据形状键；`credential_ref` 来自 profile 的引用，secret 从未进入 mirror 的签名/参数（`provider_runtime_mirror.py:66-84`）。
- 全 diff（`git diff d38c624f7 94b8f33f5`）搜索 `api_key|apikey|secret|bearer|password|authorization|token`：仅命中 docstring 与测试断言字符串，无任何实际值写入。
- 落盘路径另有 `_redact`（`pipeline.py:1703-1733`）按键名清洗，`api_key/secret/token/password` 键会被整个丢弃。
- 残余观察（不判 FAIL）：镜像原样复制 `profile.option_dict()`；若未来某条 P15 路径允许写入 `options`，其中**值**不会被 `_redact` 清洗（`_redact` 只看键）。当前 P15 create/update 不接收 `options`，legacy QML 也固定 `options=tuple()`，故当前不可达，登录为 P2 级防御性备注。
- 结论：**AC2 PASS。**

## 5. AC3 原子性：三问三答（复核项 4）

### 5.1 「JSON store 写了、镜像没写」是否结构上不可能？

**是——但仅对本卡六条 Core 写路径成立。** 六条路径一律 mirror-first：`mirror.*` 成功后才执行 `store.*`；镜像自身经 `save_settings_section`/`save_provider_binding` 落在**单条 SQLite 事务**（`pipeline.py:1774-1786` 的 `with self._conn`）；JSON store 是 tmp+`os.replace` 原子替换（`json_profile_stores.py:32-38`）。因此 store 只有在镜像已提交后才可能成功，store 写失败时镜像最多处于「已写、待回滚」状态，不可能出现「store 已写、镜像未写」。

必须限定范围：legacy QML `SettingsViewModel.saveProviderProfile` 仍是 **store-first**（`viewmodel.py:254-258`：先 `add_profile/update_profile`，再 `_save_provider_runtime_profile`），它不在本卡六条路径内，仍是「store 写了、镜像没写」的既有缺口。因此「结构上不可能」只能写成「对本卡接线的 Core 命令面成立」；全仓范围并非绝对不可能。此点不单列 finding，仅作为 AC3 的范围限定，不推翻本卡 AC3。

### 5.2 反向窗口（镜像已写、store 失败、回滚再失败）剩下什么保证？

- 保证 1：**typed 失败**——`_write_with_rollback` 把 `BindingValidationError/OSError/ValueError/TypeError` 转成 `SETTINGS_UNAVAILABLE`；`sqlite3.Error` 虽不在白名单，但会被 Core 顶层兜底成 `SETTINGS_UNAVAILABLE`（实测 phase 变成 `settings_resolution`，见 R-005）。
- 保证 2：**尽力回滚**——store 失败时执行 `mirror.remove_profile/upsert_profile/restore`；实测把 `provider_profile_store.add_profile` 改成 `OSError` 后，镜像与 JSON 两侧都为空，错误为 typed `SETTINGS_UNAVAILABLE`，说明常规反向路径是有效的（但无测试覆盖，见 R-002）。
- 保证 3：**读取侧 fail-closed**——`_apply_profile_bindings` 遇到缺失/禁用 profile 不建 alias，`registry.resolve` 不会静默降级到别的 provider。
- 不保证：跨存储原子性；rollback 自身失败后的 residue。实测两种残留：
  - 仅 rollback 失败（create）：SQLite 里多一个**无 binding 的** profile（运行时不可达，属脏数据，非功能错误）；
  - `_write_with_rollback` 漏捕 `KeyError`（update）：镜像已是新 `base_url`，JSON 仍是旧 `base_url`，错误虽为 `SETTINGS_UNAVAILABLE` 但**未回滚**——这正是反向窗口被实现漏洞放大的地方（R-002）。

### 5.3 卡面「同一事务/同一 seam 内」时算 PASS 还是 PARTIAL？

**明确结论：AC3 判 PASS，不判 PARTIAL。** 理由：
1. 卡面 **AC3** 的原文只要求「镜像写入失败必须 typed 失败并回滚，不允许『JSON store 写了、镜像没写』」——这两条对六条 Core 路径均成立；跨库事务不是 AC3 的文字要求。
2. 「同一事务/同一 seam 内」写在 **AC1**，且卡面给了二选一（`同一事务/同一 seam 内`）。本实现选择的是**同一 seam**：同一个 Core 命令处理器内、只经 `PipelineDefaultsService` 一条既有 seam，没有第二套持久化实现。按二选一口径，AC1 的这一子句成立。
3. 若把「同一事务」按字面当硬要求，则 JSON 文件 + SQLite 两存储不可能满足，那就不是本实现的 PARTIAL，而是 AC 本身需要回 DSH 重定义（例如显式改成「mirror-first + best-effort rollback」并接受 residue）。**在现有卡面文字下，不能因此把 AC3 判 PARTIAL；反向窗口是已披露 limitation，不是 AC3 失败。**
4. 但 AC1 仍判 **PARTIAL**，原因不是事务，而是 **R-001 的 scope 不忠实**（见 §11）。

## 6. 判别测试真实性（复核项 5）

- 新增 7 例全部在 `tests/core/test_trans_binding_bridge.py`：AC1 三例（`:92-172`）、Rendering 一例（`:175-189`）、AC2 一例（`:207-227`）、AC3 两例（`:232-270`）。
- 判别力实测：用临时 pytest 插件把 `ProviderRuntimeMirror.upsert_profile/remove_profile/bind_capability/clear_capability` 全部 no-op 后重跑该文件，结果为 **`6 failed, 1 passed in 1.11s`**。红的是 1/2/3/5/6/7；唯一绿的是 `test_rendering_capability_never_invents_a_pipeline_step`（它只做负向断言「没有 render/rendering 键」，镜像 no-op 时自然仍通过）。因此「相关断言必红」对 6 例成立，对第 7 例不成立；README §4 的表述（只指正向镜像测试）没有错，但不应被读成 7/7 判别。
- **AC3 两个方向各一条？不成立。** 两例都是「镜像先失败」：
  - `test_profile_mirror_failure_is_typed_and_leaves_no_half_write`（`:232-252`）monkeypatch `save_settings_section`；
  - `test_binding_mirror_failure_rolls_back_the_binding_rows`（`:255-270`）monkeypatch `save_provider_binding`；名字里的 “rolls back” 实际从未进入 rollback——镜像先抛，JSON store 根本没写。
  - 真正的反向路径（mirror 成功、store 失败、执行 rollback）**零测试**。我用临时探针验证它在 `OSError` 下能正确回滚、在 `KeyError` 下不能（见 R-002）。task 文件与 README 的「AC3 两向 typed 失败且两侧皆空」与事实不符，应改为「mirror-first 方向两例；store-failure 方向未覆盖」。
- 另：正向测试断言的是原始 defaults + `_apply_profile_bindings`，未直接调用 `handlers._chain` 或 `_profile_settings`；虽然它断言了 `chain_from_binding(bindings["translate"])` 非 None（足以证明 `_chain` 不会抛 PROVIDER_NOT_CONFIGURED），但不是完整的 handler 级测试。AC6 文字要求「`_profile_settings` 能读到」，该测试没有直接调用 `_profile_settings`；建议补一条（P2 级，不单列）。

## 7. credential 写入接线：必要还是越权？（复核项 6）

**必要，不判越权。** 证据链：
- runtime 的 `_openai_config` 把 `credential_ref` 作为 profile 形状的一部分读取（`runtime.py:263-265`）；`freeze_run_snapshots` 也把它冻结进 `execution`（`registry.py:429-431`）。
- 若 `BindProfileCredential` 不接线：profile 建好后镜像里的 `credential_ref` 永远是创建时的 `None`；即使用户在 vault 里绑定了 key，运行侧仍认为「无凭据」，认证失败——与本卡目标直接冲突。
- 两个命令都是既有 P15 wire 命令，未新增命令/端口；网络 profile 凭据（`kind != CREDENTIAL_KIND_PROVIDER`）保持原路径未动（`settings_commands.py:354-367`、`:410-418`），边界清楚。
- 唯一可争的是「为什么不在 runtime 装配时从 JSON store 读取 credential_ref 来做对齐」——但那会引入第二个跨存储读取点，反而违背 AC4；当前接线是更符合 seam 的解法。

## 8. 零契约面（复核项 7）

| 检查 | 命令/方法 | 结果 |
|---|---|---|
| `apps/**` 零改动 | `git diff --name-only d38c624f7 94b8f33f5 -- apps` | 空（PASS） |
| 无新 wire 命令 | `git diff` 的 handler map 无新增；`settings_provider_` 在 `core_service.py` 的出现次数前后都是 8；`core_service.py` 不在 diff 中 | PASS |
| 无新端口成员 | 未改 `ports/**`；`ProviderRuntimeMirror` 只消费既有 `PipelineDefaultsService` 方法 | PASS |
| inventory | `python tools/generate_api_inventory.py --check` | EXIT=0；`IHostController 80`、`IRunController 6`、合计 **87**；`OK: rendered counts match FEA-C07 doc` |
| pins | `pwsh tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，EXIT=0 |

## 9. 实跑记录（复核项 8）

| 场景 | 命令 | 结果 | EXIT |
|---|---|---|---|
| 全量 pytest | `C:\Python314\python.exe -m pytest -q` | **3551 passed, 10 skipped, 11 warnings in 310.36s**（0 failed） | 0 |
| 定向 P15/bridge | `... -m pytest -q tests/core/test_trans_binding_bridge.py tests/core/test_p15_core_settings.py` | **108 passed in 13.39s** | 0 |
| 治理检查（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)` | 0 |
| 治理检查（本卡） | `... check.ps1 -TaskPath 'doc/tasks/TRANS-BINDING-BRIDGE.md'` | `Governance check: PASS (3 warnings)` | 0 |
| 治理检查（证据日志里的写法） | `... check.ps1 -TaskPath TRANS-BINDING-BRIDGE` | **FAIL**：`当前 Task 文件不存在：G:\CODEX\New Manga\TRANS-BINDING-BRIDGE` | 1 |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)` | 0 |
| inventory | `python tools/generate_api_inventory.py --check` | 计数 80+6=87，Check OK | 0 |

全量日志与基线 `3544` 的差值 +7 与新增 7 例一致；没有新增 failed/skip 变化（10 skipped 与基线相同）。本次全量在代码等价的 `3a1183681`（仅 task 文档差异）上运行；diff 已确认代码与 `94b8f33f5` 相同。

## 10. 新问题（复核项 9）

- **镜像写失败会不会留下 SQLite 多余 profile？** 镜像写本身是单事务，失败不留；只有「store 失败 + rollback 再失败」会在 SQLite 留下**未被 binding 引用**的 profile（实测 create：`residual mirror profiles: ['d23c…']`、`json store: []`）。它不可达但属脏数据；update/delete 的同类残留后果更重（见 R-007）。
- **删除 profile 时镜像是否同步删？** 是：`_profiles_delete` 先 `mirror.remove_profile` 再 `store.delete_profile`，store 失败则 `mirror.upsert_profile(existing)` 回滚（`:716-725`）；测试 `test_profile_update_and_delete_keep_the_mirror_in_sync` 覆盖。删除前还有「被 binding / 受保护 run 引用」两道 conflict 检查（`:712-715`），不会留下悬空 binding。
- **`enabled=false` 是否被镜像并被 runtime 正确忽略？** 镜像会写 `enabled: false`（测试 `:133-157` 断言）；runtime 投影 `_apply_profile_bindings` 对 `raw.get("enabled") is False` 直接 `continue`，不建 alias（实测 `disabled aliases: {}`、槽位不存在），因此会 fail-closed，不会静默用别的 provider。注意：运行中的 Core 的 registry alias 是装配期构建的，禁用要**重启 Core 后**才生效（AC8 已说明，T-C 文案须写清）；不重启时旧 alias 仍可解析，禁用不会立即阻断（R-008）。

## 11. Findings

**P0：无。** P1：R-001、R-002；P2：R-003、R-004、R-005、R-006、R-007、R-008。

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-001 | **P1** | `src/bootstrap/settings_commands.py:727-756`、`:758-778` | 能力绑定镜像**忽略 scope**：book/chapter 的 `set` 会把全局 `provider_bindings[step]` 覆盖成该 scope 的 profile；任意 scope 的 `clear` 会**无条件清空**全局 step binding，即使全局/其他 scope 的绑定仍然存在。后果：① 其他 book/chapter 的 Run 被路由到用户并未全局授权的 provider（内容外发到错误端点）；② 清掉后全局绑定仍在 Settings 显示为已配置，但 `_chain` 拿到 `None` → **重新出现 `PROVIDER_NOT_CONFIGURED`**，直接抵消本卡目标。 | 临时数据目录实测：set global=A → mirror `{'translate': A}`；set book=B → mirror `{'translate': B}`（P15 rows 仍有 global A + book B）；clear book → mirror `{}`，而 `settings_provider_bindings_resolve` 仍返回 global A；`chain_from_binding(None) is None` ⇒ `_chain` 会抛 `PROVIDER_NOT_CONFIGURED`。更强：对一个**不存在**的 book scope 执行 clear（P15 rows 完全不变）也会把 mirror 清空。 | 镜像只处理 `scope == {"kind":"global"}`；非全局 set/clear 不得触碰 step binding，或在 clear 后按「global 行仍存在则恢复」重算；补一条 global+book/chapter set/clear 的镜像测试。若产品要求 scoped binding 在运行侧生效，需另卡定义 runtime scope 解析，不能靠全局覆盖冒充。 | open |
| R-002 | **P1** | `src/bootstrap/settings_commands.py:1008-1023`（白名单在 `:1018`）；`src/infrastructure/settings/json_profile_stores.py:162-167`（`update_profile` 会抛 `KeyError`） | AC3 的**反向路径无测试**；且 `_write_with_rollback` 只捕 `BindingValidationError/OSError/ValueError/TypeError`，`JsonProviderProfileStore.update_profile` 的 `KeyError`（profile 在 JSON 中消失）会逃逸：镜像保留新值、JSON 保留旧值，typed 失败由 Core 顶层兜底但**不会执行 rollback**。这正是「镜像已写、store 失败」窗口的实际半写。触发概率低（需 JSON 在 get 与 update 之间被外部改动/恢复），但一旦发生即留下不一致，且测试完全未覆盖该方向。 | 实测 `core.provider_profile_store.update_profile` 抛 `KeyError`：返回 `SETTINGS_UNAVAILABLE`，`mirror base_url=https://second.example.test/v1`、`json store base_url=https://api.example.test/v1`（两侧不一致）。反向正常路径（`OSError`）实测能回滚且两侧皆空。 | 写阶段用更宽的异常边界（至少加入 `KeyError`、`sqlite3.Error`），确保 rollback 一定尝试；补两条测试：`add_profile→OSError`、`update_profile→KeyError`，断言两侧不变 + typed 错误。README/task 的「AC3 两向」改为「mirror-first 两例；store-failure 方向待补」。 | open |
| R-003 | P2 | `src/application/settings/provider_runtime_mirror.py` 全文件；`src/bootstrap/settings_commands.py` 六处接线；早退分支 `:349-350`、`:393-394` | **无回填**：既有 P15 JSON profile（升级前由 Core 命令创建）不会在装配/列表时被补镜像；用户仅重新 `bindings_set` 也只镜像 binding，不镜像 profile。结果：P15 显示已配置、mirror 有 `translate` 但没有该 profile → `_apply_profile_bindings` 无 alias，运行侧仍失败（错误前移为 `ProviderUnavailable`）。更隐蔽：`BindProfileCredential` 在 `profile.credential_ref == credential_ref` 时**提前返回**（`:349-350`），`ClearProfileCredential` 在 ref 为 `None` 时也提前返回（`:393-394`），因此「重新绑定同一个 key」这种最常见的修复动作**不会**补镜像。 | 预置 `provider_profiles.json` + `provider_capability_bindings.json` 后装配：`mirror profiles: []`、`mirror bindings: {}`；`bindings_resolve` 仍返回该 profile；重新 `bindings_set` 后 `mirror profiles` 仍为 `[]`、`mirror bindings: {'translate': pid}`、`runtime aliases: {}`。代码复核确认两个 credential 早退分支都在 `_runtime_mirror` 之前。legacy QML 写入会自行镜像，故影响面主要是 Core P15 路径产生的既有 profile。 | T-C 的首次进入/保存路径应触发 profile upsert（或在 `bindings_set`/credential 写入时先 upsert 所涉 profile 再判断早退）；或加一次一次性 backfill。 | open |
| R-004 | P2 | `verification/TRANS-BINDING-BRIDGE/logs/gates-final.log:11-18`；`tools/governance/check.ps1:2,246-247,294-297` | 证据日志把门禁命令记成 `check.ps1 -TaskPath TRANS-BINDING-BRIDGE`，但脚本把 `TaskPath` 当**文件路径**；按字面重跑会 `FAIL`。日志头 `HEAD=d38c624f7` 是父提交，实际是在提交前的工作树上跑的（这本身可接受，但标签应写清「working tree on d38c624f7」）。 | 同一命令重跑：`-TaskPath TRANS-BINDING-BRIDGE` → EXIT=1；`-TaskPath doc/tasks/TRANS-BINDING-BRIDGE.md` → PASS (3 warnings)、EXIT=0。 | 证据日志改为可复制的真实命令（文件路径），并注明 working-tree 口径；不影响代码，但影响审计可复现性。 | open |
| R-005 | P2 | `src/bootstrap/settings_commands.py:1018` | `sqlite3.Error`（如 `database is locked`/磁盘错误）不在白名单；虽因 mirror-first 不会产生半写，但返回的 typed 错误 phase/action 变成 Core 兜底的 `settings_resolution/contact_support`，与用户操作语境不符，排障信息变差。 | 实测 `save_settings_section` 抛 `sqlite3.OperationalError`：返回 `SETTINGS_UNAVAILABLE`、`phase=settings_resolution`、`action=contact_support`；JSON store 未被写。 | 一并补 `sqlite3.Error`，映射到原 phase；与 R-002 同一处修改。 | open |
| R-006 | P2 | `tests/core/test_trans_binding_bridge.py:232-270`；README §4、task 交付记录 | 7 例中两例都只覆盖 mirror-first，反向 store 失败无测试；`test_binding_mirror_failure_rolls_back_the_binding_rows` 名字暗示 rollback，实际从未执行 rollback。镜像 no-op 时 7 例只有 6 红，`rendering` 例是纯负向断言。 | 临时 no-op 插件：`6 failed, 1 passed in 1.11s`；两例测试的 monkeypatch 目标分别是 `save_settings_section`/`save_provider_binding`。 | 补 store-failure 两例（正常回滚 + `KeyError` 漏洞）；把「两向」措辞改准确；Rendering 例不要算作镜像判别测试。 | open |
| R-007 | P2 | `src/bootstrap/settings_commands.py:716-725`；`registry.py:373`；AC8 | rollback 再失败时残余状态按操作不同：create=多一个无 binding profile（不可达）；update=镜像新值 + JSON 旧值（运行侧可能已用未持久化配置）；delete=镜像缺 profile + JSON 仍在（Settings 显示存在但运行侧不可解析）。README §5.3 只笼统写「尽力回滚」，没有逐操作后果；rollback 再失败无任何监测/修复入口。 | 实测 create + `remove_profile` 抛错：`residual mirror profiles: ['d23c…']`、JSON `[]`、错误 `SETTINGS_UNAVAILABLE`。 | 逐操作记录残余语义；至少在下次写同一 profile 时以 JSON 为准修复镜像（或提供 repair 命令）；AC8/T-C 的运维说明写清「配置写入失败后需重新保存该配置」。 | open |
| R-008 | P2 | `src/infrastructure/providers/runtime.py:418-467`、`:451`；AC8 | `enabled=false` 会被镜像且投影会忽略（正确 fail-closed），但**运行中的 Core** 的 alias/registry 是装配期构建的；不重启的话禁用 profile 仍可被旧 alias 解析，禁用不生效。AC8 已声明「重启生效」，但该条最容易在 T-C 被误写成即时生效。 | 投影实测 `disabled aliases: {}`；装配期闭包见 `core_assembly.py:1421-1423`、`1696-1698`；`build_provider_runtime` 只在该处调用。 | T-C 文案明确「配置/禁用/绑定变更需重启 Core 生效」；如需即时生效，另卡定义 live reload。 | open |

> 另有两项不单列 finding 的观察：① `ProviderRuntimeMirror.profiles()/provider_bindings()` 目前无生产调用者（死读 API）；② `options` 值不经 `_redact` 清洗（当前无写入路径可达，防御性备注）。

## 12. 明确回答：这个桥是否足以让 translate 拿到 binding、消除 `PROVIDER_NOT_CONFIGURED`？

**是——但只到「binding 存在」这一层，且依赖重启。** 分三层说清：

1. **镜像层（本卡）成立**：profile 与 `provider_bindings["translate"]` 都写入 `pipeline_defaults` 后，`chain_from_binding(bindings["translate"])` 非 None，`_chain` 不会再抛 `PROVIDER_NOT_CONFIGURED`；实测 `freeze_run_snapshots` 还能把镜像 profile 冻结成带 `execution` 的 `translate` 绑定（`provider_id/base_url/model/credential_ref` 正确）。就 `_chain` 这一直接来源而言，**该症状可在正确配置后被消除**。
2. **运行层需要重启**：Core 的 registry/alias 在装配期一次性构建（`core_assembly.py:1421-1423`），镜像只写 DB。因此**不重启**时，新 profile 的 alias 不存在，translate 的失败会前移成 `ProviderUnavailable`（`no provider registered as <profile_id>`），而不是被修好；**重启 Core 后** alias/`_apply_profile_bindings` 才会包含该 profile，配合有效 `credential_ref` 和 `enabled=true`，translate 才能真正进入 provider 调用。AC8 的「配置变更需重启 Core 才生效」是准确的，T-C 不能宣称即时生效。
3. **前提条件**：profile 必须已镜像（新写入/更新会触发；仅 re-bind 既有 profile 不会；甚至重新绑定**同一个** credential_ref 也会因早退而不写镜像，见 R-003）、`enabled=true`、credential 已绑定且 vault 中存在；scoped（book/chapter）绑定当前**不能**被正确表达，见 R-001。

所以：**「`PROVIDER_NOT_CONFIGURED` 可被消除 = 是」；「单靠这个桥就能让 translate 真正跑通 = 否」**，后者还需要重启、凭据与全局 scope 的正确使用。

## 13. 结论与复审要求

- **Verdict：`changes_requested`**（R-001 scope 镜像、R-002 反向回滚/测试缺口均未闭合；按模板 P1 未解决不可批准）。
- 该桥的**方向、取证、双写键集、AC2、AC4、AC5、零契约面、全量测试**均已由独立上下文复核通过；不需要推翻重做。
- 返修最小集：① 让 scope 处理忠实（global-only 或按全局行重算）；② 扩宽 `_write_with_rollback` 的异常边界并补 store-failure 两例；③ 更正证据日志命令与「两向」措辞；④ 记录/修复无回填与 rollback 残余语义。修完后需对新 head 重新跑定向+全量+四门禁，并由我或另一独立上下文复审 R-001/R-002。
- 复审时请固定 reviewed head；本报告只对 `94b8f33f5` 有效，`3a1183681` 仅文档差异，不改变结论。

