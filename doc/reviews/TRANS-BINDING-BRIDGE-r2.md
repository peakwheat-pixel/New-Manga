---
task: TRANS-BINDING-BRIDGE
reviewer: independent sub-agent (r2, read-only, not involved in r1)
reviewer_kind: subagent
reviewer_agent: agent-4（由 lead 派发；独立上下文；未参与实现，未参与 r1）
verdict: approved
date: 2026-11-14
reviewed_head: 659bb3053
base_commit: 3a1183681
worktree_head_at_review: 65425a24f
scope: read-only
---

# Review：TRANS-BINDING-BRIDGE（L1-T-A）r2 修复面复核

> **结论：`approved`。** 只核 r1 修复面，不重做全量审查。r1 的 **P1-1（scope 无视）与 P1-2（反向半写）在其实指缺陷上均已真实关闭**：scope 分流有代码、有判别测试、有回退探针；`KeyError` 反向路径已进回滚白名单并有必红测试。无 P0/P1 遗留。发现 2 项 P2（`sqlite3.Error` 未纳入回滚白名单；证据文本的计数与「四条反向判别」表述不准确）与 1 项 T-C 携带风险（scoped 绑定的显示面与执行面可能不一致），均不阻断收口。**在 R-6 已裁决的 global-only 语义下，本卡可以收口。**

## 0. 审查范围、身份与方法

- **审查者身份**：`agent-4`，由 lead 派发的独立上下文子 agent；只读；未参与 `TRANS-BINDING-BRIDGE` 的实现或返修，也未参与 r1。仓库内唯一新增文件是本报告。
- **reviewed_head 固定为 `659bb3053`**（父 `3a1183681`），只审查该提交的修复面；不重做 r1 对 `94b8f33f5` 的全量审查。
- **复核期间 worktree HEAD 前移**：复核开始时 HEAD 已是 `65425a24f`（`trans: record T-A r1 findings, repair and R-6 adjudication`，仅新增 r1 报告 + task 返修记录）。已核对 `git diff --name-only 659bb3053 65425a24f -- src tests apps` 为空；即实跑所在工作树与 `reviewed_head` 的**源码/测试完全一致**。本报告结论只对 `659bb3053` 有效。
- **方法**：逐行读代码 + 行号核对；用 `git show 3a1183681:src/bootstrap/settings_commands.py` 在**进程内**把父提交的 `_bindings_set`/`_bindings_clear`/`_write_with_rollback` 重新绑定到类上做回退探针（不写仓库）；用真实 `assemble_production_core` + `CoreServiceServer` 做 SQLite 例外探针；实跑定向、全量、四门禁。临时探针与日志均在 `%TEMP%`。

## 1. 逐项结论

| # | 复核项 | 结论 | 一句话证据 |
|---|---|---|---|
| 1 | scope 分流的取证是否成立 | **PASS** | 四个执行读取点与 `pipeline.py`/`pipeline_defaults.py` 全部逐行核实；run 快照只有扁平 step 槽，`_p15_settings_snapshot` 只被显示/保护面消费（§2） |
| 2 | 分流实现是否正确 | **PASS** | `writes_flat_slot`/`clears_flat_slot` 仅在 `scope["kind"] == "global"` 时为真；非 global 只写 P15 JSON 行，不触碰扁平槽（§3） |
| 3 | 新增 7 例测试的判别力 | **PASS（4/7 对本提交敏感，3/7 为既有 OSError 路径回归钉）** | 回退 scope 分流：`3 failed, 11 passed`；回退 `KeyError` 白名单：`1 failed, 13 passed`（§4） |
| 4 | 捕获范围是否合理 | **PASS（选型合理但非穷尽，残留 P2）** | JSON store 异常族全覆盖；SQLite 侧 `sqlite3.Error` 未捕获，实测可留下「镜像新值 / JSON 旧值」且不尝试回滚（§5） |
| 5 | 实测 | **PASS** | 定向 115 passed；全量 3558 passed / 10 skipped / 0 failed（308.99s）；四门禁 EXIT=0（§6） |
| 6 | 零越界与证据可复制性 | **PASS** | `apps/**`、`src/ports/**`、`core_service.py` 自 `94b8f33f5` 起 0 改动；无新 wire；gates 日志命令按原文重跑均 EXIT=0（§7） |

## 2. 第 1 项：scope 分流取证核实

| 实施者断言 | 独立核对 | 结论 |
|---|---|---|
| `handlers._chain` 读 `run.provider_binding_snapshot.get(step_type)`，行号 `handlers.py:1267` | 原文 `src/infrastructure/providers/handlers.py:1267` 即 `binding = run.provider_binding_snapshot.get(step_type)`；`chain_from_binding(None) is None` 后抛 `ProviderNotConfigured`（`:1268-1273`） | **成立** |
| 同读取点 `executor.py:27` | 原文 `binding: Any = run.provider_binding_snapshot.get(unit.step_type)` | **成立** |
| 同读取点 `projection.py:285` | 原文 `binding = run.provider_binding_snapshot.get(step.step_type)` | **成立** |
| 同读取点 `service.py:797` | 原文 `binding = run.provider_binding_snapshot.get(step_type)` | **成立** |
| `pipeline_defaults.provider_bindings` 是 `{step: profile_id}` 扁平表，无 scope 维度（`pipeline_defaults.py:62-103`） | `save_provider_binding`（`:62-84`）与 `clear_provider_binding`（`:86-103`）都只做 `bindings[step_type] = binding` / 按 step 删除；`PipelineDefaults` 只有 `settings/provider_bindings/constraint_snapshot_ref/context_policy` 四个字段（`:28-35`），无 scope | **成立**（精确说：`:62-103` 是扁平表的 service 方法，物理表在 `pipeline.py`） |
| `pipeline.py:1766-1786` 写单行 `provider_bindings_json` | 原文 `set_defaults` 以单条 `INSERT ... ON CONFLICT(defaults_id) DO UPDATE` 写 `settings_json, provider_bindings_json, ...`，`provider_bindings_json` 是整个扁平映射的 JSON | **成立** |
| run 快照无 per-book step 槽；P15 的 book/chapter 解析只进 `_p15_settings_snapshot` 供 resolve 显示（`core_service.py:6707-6709`；构建 `settings_commands.py:589-627`） | `core_service.py:6707-6709` 原文把 `prepare_run_snapshot(scope, overrides)` 整个塞进 `P15_SNAPSHOT_KEY`（字面量 `_p15_settings_snapshot`）；`prepare_run_snapshot`（`settings_commands.py:589-627`）用 `_scope_context(scope)` + `_resolve_current_binding(..., book_id, chapter_id)` 解析 scope，结果只在该嵌套键的 `provider_profiles` 下。全仓 grep `_p15_settings_snapshot` 的消费点只有 `settings_commands.py:578/801/823/852/1330`：network profile 受保护 run 检查、`bindings_resolve`、`run_snapshot_get`、`resolve_overrides`、provider profile 受保护 run 检查；`registry.freeze_run_snapshots`（`registry.py:357-366`）按扁平 step 遍历，嵌套键因没有 provider id 被跳过，不会变成 step 绑定 | **成立**（精确说：不只是 resolve 显示，还有 run 快照展示与受保护 run 保护面；**都不在执行链**） |

**结论：取证没有造假，结论正确。** 执行链只认 `provider_binding_snapshot[step]` 这一扁平槽；book/chapter scope 在当前 run 快照结构里没有独立 step 槽。唯一用词偏差是把 `_p15_settings_snapshot` 的用途写成「供 resolve 显示」——实际还包括 `settings_provider_run_snapshot_get` 展示与受保护 run 引用检查；不影响「不驱动执行」的结论。

## 3. 第 2 项：分流实现

代码（当前工作树行号，与 `659bb3053` 相同）：

- `_bindings_set`（`src/bootstrap/settings_commands.py:727-764`）：
  - `writes_flat_slot = scope["kind"] == "global"`（`:752`）；
  - `write()` 内 `if writes_flat_slot: mirror.bind_capability(...)`（`:757-758`），随后**无条件** `self._binding_store().save_bindings(rows)`（`:759`）；
  - `before = mirror.snapshot()`（`:742`）与回滚 `mirror.restore(before)`（`:762`）保留。
- `_bindings_clear`（`:766-791`）：
  - `clears_flat_slot = scope["kind"] == "global"`（`:781`）；
  - `if clears_flat_slot: mirror.clear_capability(...)`（`:784-785`），随后保存 P15 rows（`:786`）。
- 全文件没有第二条 binding 镜像写入路径；legacy QML 的 `save_provider_binding`（`ui/viewmodels/settings/viewmodel.py:405`）不在 Core P15 命令面内，也未在本提交中改动。

行为核对：

- **global set**：镜像写扁平槽 + P15 rows 双写（与 r1 前一致）。
- **book/chapter set**：只写 P15 rows；扁平槽保持原值。测试 `test_book_scoped_binding_does_not_overwrite_the_global_step` 断言 global=A → book=B 后 `provider_bindings["translate"] == A`，并断言 P15 rows 有 book 行、`bindings_resolve(book)` 返回 B。
- **book/chapter clear**：只重写 P15 rows（移除该 scope 行，global 行原样保留）；扁平槽完全不动。两个 clear 测试分别覆盖「清一个没有绑定的 book scope」和「清一个 chapter scope」，均断言 global 槽仍在。
- **失败路径**：非 global 的 `save_bindings` 失败时 `mirror.restore(before)` 是无害的 no-op 级恢复（镜像本就未变），typed 失败仍成立。

结论：**实现正确，非 global 完全不碰扁平槽。** 这正是 r1 R-001 要求的最小修复；book/chapter 绑定从「错误地劫持全局」变为「只存在于 P15 行、不驱动执行」，后者已由 DSH R-6 裁决为已知限制，不是本实现的越界。

## 4. 第 3 项：新增 7 例测试的判别力（实测回退）

### 4.1 回退方法

用临时 pytest 插件（`%TEMP%\r2-probe\r2_revert_scope.py` / `r2_revert_rollback.py`）从 `git show 3a1183681:src/bootstrap/settings_commands.py` 取出父提交方法源码，编译后**在进程内**重绑定到 `P15SettingsCommands`；仓库文件未改。

### 4.2 结果

| 回退对象 | 命令 | 结果 | 结论 |
|---|---|---|---|
| 仅回退 P1-1（父提交 `_bindings_set`/`_bindings_clear`，即 scope 分流 OFF） | `python -m pytest -q -p r2_revert_scope tests/core/test_trans_binding_bridge.py` | **3 failed, 11 passed in 2.53s**，EXIT=1 | 3 个 scope 测试**必然变红**：`test_book_scoped_binding_does_not_overwrite_the_global_step`（断言 `book scope hijacked the global step`）、`test_clearing_a_book_scope_never_clears_the_global_step`、`test_clearing_a_chapter_scope_never_clears_the_global_step`（后两条均在 `translate` 断言处 `KeyError`） |
| 仅回退 P1-2 的异常白名单（父提交 `_write_with_rollback`，即 `KeyError` 捕获 OFF） | `python -m pytest -q -p r2_revert_rollback tests/core/test_trans_binding_bridge.py` | **1 failed, 13 passed in 1.58s**，EXIT=1 | 只有 `test_store_update_failure_rolls_the_mirror_back` 变红：`assert 'https://new.example.test/v1' == 'https://old.example.test/v1'`（`tests/core/test_trans_binding_bridge.py:381`）；另 3 条 OSError 反向测试仍绿 |

### 4.3 判断

- **3 个 scope 测试**：对 `659bb3053` 的 scope 分流是强判别；回退即红，且失败原因正是 r1 描述的劫持/清空。
- **`KeyError` 反向测试**：对白名单扩展是强判别；回退后错误码仍是 `SETTINGS_UNAVAILABLE`（Core 外层兜底，`core_service.py:7319-7323`），但镜像**未回滚**，所以第 381 行断言必红——该测试确实锁住了「回滚」而不是只锁「typed 错误」。
- **另外 3 条 OSError 反向测试**（`add_profile` / `delete_profile` / `save_bindings`）：在父提交的白名单下**已经会通过**（OSError 原本就被捕获），因此它们不是 `659bb3053` 的判别测试，而是 AC3 mirror-first + rollback 的**回归钉**；若把回滚机制整体移除，它们会红。把它们称作「四条反向判别测试」不准确（见 R2-002）。
- 7 例全部走真实 `CoreServiceServer` + `assemble_production_core`，没有 stub 被测 seam；测试文件无 skip/xfail、无削弱既有断言（本提交对测试文件是 **168 行纯新增**）。

结论：**新增测试有真实判别力，但覆盖构成应如实写成「4 条对本修复敏感 + 3 条 OSError 回归钉」**。

## 5. 第 4 项：异常捕获范围

`_write_with_rollback`（`src/bootstrap/settings_commands.py:1021-1046`）当前捕获：

```
(BindingValidationError, KeyError, OSError, TypeError, ValueError)
```

### 5.1 与实际协作者比对

| 异常族 | 实际来源 | 是否覆盖 |
|---|---|---|
| `BindingValidationError` | `PipelineDefaultsService.save_provider_binding/clear_provider_binding` 校验（`application/settings/errors.py:22-28`；`pipeline_defaults.py:70-74`、`:88-91`） | ✅ |
| `KeyError` | `JsonProviderProfileStore.update_profile` 缺失行（`json_profile_stores.py:162-165`）；`_provider_from_json` 读坏数据也可能抛 | ✅（本提交新增） |
| `OSError` | `_atomic_write_json` 的 mkdir/write_text/os.replace（`json_profile_stores.py:32-40`）；文件读写 | ✅ |
| `ValueError` | `ProfileFileFormatError`（`ValueError` 子类，`:28`）；`json.JSONDecodeError`；`UnicodeDecodeError` 等 | ✅ |
| `TypeError` | `json.dumps` 序列化异常值；坏 JSON 行形状 | ✅（防御） |
| **`sqlite3.Error`** | 镜像协作者 `PipelineDefaultsService.save_settings_section/save_provider_binding` 的 `self.read()`/`_save()`（`SqliteSnapshotProvider.set_defaults`，`pipeline.py:1774-1786`；连接 WAL + `busy_timeout`，`connection.py:318-320`） | ❌ **未覆盖** |
| `RuntimeError` | 在本卡这两个协作者（pipeline defaults service、JSON profile stores）中无 `raise RuntimeError` 路径；仓内 RuntimeError 都在别的事务/服务 | 不适用 |
| `AttributeError` / `NameError` | 编程错误；不捕获是合理选型 | 故意不覆盖 |

### 5.2 `sqlite3.Error` 的实际后果（实测）

探针（`%TEMP%\r2-probe\r2_sqlite_probe.py`）真实装配 Core，把 `save_settings_section` 包成「先提交、后抛 `sqlite3.OperationalError`」（模拟 seam 提交后读回失败），再走 `settings_provider_profiles_create`：

```
error: {"code": "SETTINGS_UNAVAILABLE", ... "details": {"phase": "settings_resolution", "action": "contact_support"}}
mirror profile ids: ['98131368781b4d33b561e0b63cf5b038']
json store profile ids: []
```

即：**typed 失败成立，但没有进入 `_write_with_rollback` 的 except，rollback 未尝试；镜像留下新 profile，JSON store 为空**。这是 AC3 反向窗口的一个真实（低概率）残余，且错误 phase 被 Core 外层兜底改成 `settings_resolution`。

同时这也说明实施者的「故意不捕获裸 Exception，让 AttributeError/NameError 响亮」在 **wire 层并不成立**：`core_service.py:7319-7323` 对 P15 命令的任意异常都兜底成 `SETTINGS_UNAVAILABLE`（`phase=settings_resolution`）。因此白名单真正决定的不是「是否响亮」，而是**是否尝试回滚**——这更支持把已知的 `sqlite3.Error` 纳入。

### 5.3 判断

选型**合理但非穷尽**：JSON store 的异常族被完整覆盖，`KeyError` 缺口已按 r1 要求补上；`sqlite3.Error` 是遗漏的真实异常族。鉴于：① 触发需要 SQLite 提交后读回失败/IO 错误，概率低；② r1 将同类 R-005 定为 P2；③ 错误码仍是 typed `SETTINGS_UNAVAILABLE`；④ 即使捕获，回滚也可能因同一 SQLite 故障失败；该项定为 **P2（R2-001），不阻断 P1-2 关闭**。若 DSH 要求 AC3 的异常族穷尽，补 `sqlite3.Error` 一行 + 一条反向测试即可，不需要重开本卡范围。

## 6. 第 5 项：实测

环境：Windows，`C:\Python314\python.exe`（Python 3.14），仓库主工作树 `G:\CODEX\New Manga`，工作树源码与 `659bb3053` 一致（HEAD `65425a24f`，仅 doc 差异）。

| 场景 | 命令（工作目录 = 仓库根） | 结果 | EXIT |
|---|---|---|---|
| 定向 | `C:\Python314\python.exe -m pytest -q tests/core/test_trans_binding_bridge.py tests/core/test_p15_core_settings.py` | **115 passed in 12.44s**（14 bridge + 101 收集用例） | 0 |
| 全量 | `C:\Python314\python.exe -m pytest -q` | **3558 passed, 10 skipped, 11 warnings in 308.99s**；0 failed | 0 |
| 治理检查（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)` | 0 |
| 治理检查（本卡） | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/TRANS-BINDING-BRIDGE.md` | `Governance check: PASS (3 warnings)` | 0 |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)` | 0 |
| inventory | `C:\Python314\python.exe tools/generate_api_inventory.py --check` | `OK: rendered counts match FEA-C07 doc`；`IReaderProgressSink 1` + `IHostController 80` + `IRunController 6` = **87** | 0 |

- 全量 10 skipped 与 r1 基线一致；新增 7 例使总数由 3551 → 3558，与提交声明一致。我的 308.99s 与证据日志 319.46s 的差异只是环境波动，计数与 0 failed 相同。
- 证据日志声明的定向 `115 passed`、全量 `3558/10/0` 均**实测复现**。

## 7. 第 6 项：零越界与证据可复制性

| 检查 | 命令/方法 | 结果 |
|---|---|---|
| `apps/**` 0 改动 | `git diff --name-only 94b8f33f5 659bb3053 -- apps` / `git diff --name-only 3a1183681 659bb3053 -- apps` | 均为空 |
| 无新端口成员 | `git diff --name-only 94b8f33f5 659bb3053 -- src/ports` | 空 |
| 无新 wire 命令 / 未改 Core 命令面 | `git diff --name-only 94b8f33f5 659bb3053 -- src/bootstrap/core_service.py src/bootstrap/core_assembly.py`；`grep '"settings_provider_' core_service.py` | 空；`core_service.py` 中 `settings_provider_` 仍是 8 处，`P15SettingsCommands.handle` 的 handler map 无新增（diff 无新增 handler 行） |
| inventory 计数 | 见 §6 | `1/80/6=87`，EXIT=0 |
| gates 日志命令可复制 | 按 `verification/TRANS-BINDING-BRIDGE/logs/gates-final.log` 每节首行原文重跑 | 4 条命令全部 EXIT=0（§6 表格）；r1 指出的 `-TaskPath TRANS-BINDING-BRIDGE` 不可复制问题已消失 |
| 提交文件面 | `git show --name-only 659bb3053` | `src/bootstrap/settings_commands.py`、`tests/core/test_trans_binding_bridge.py`、`verification/.../README.md`、2 个日志；均在 `allowed_paths` 内 |

**证据日志的两点口径说明**（P2，见 R2-002）：

1. `gates-final.log:2` 写 `HEAD=3a1183681 ← 本日志生成时 HEAD；提交随后包含本文件`——这是诚实的：门禁在提交前的 dirty 工作树上跑。我在 `659bb3053` 的等价代码上重跑，全部 EXIT=0，所以可复现性成立；但日志本身不能再被字面理解为「在 659bb3053 上生成」。
2. `logs/pytest-full.log` 只有 pytest 输出，没有命令头与 `EXIT=0` 行；按模板 Q-009 的证据纪律，建议补一行完整命令 + EXIT（不影响本次实测结论）。

## 8. Findings

**P0：无。P1：无（r1 的 R-001/R-002 均已关闭）。**

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R2-001 | P2 | `src/bootstrap/settings_commands.py:1041`；`verification/TRANS-BINDING-BRIDGE/README.md:94` | `sqlite3.Error` 未在 `_write_with_rollback` 白名单；镜像 seam 在提交后读回失败/IO 错误时，rollback 不尝试，留下「镜像新值 / JSON store 旧值」；错误 phase 被 Core 兜底为 `settings_resolution`。实施者的「两个协作者实际会抛的异常族正好这五个」不准确。 | `%TEMP%\r2-probe\r2_sqlite_probe.py`：`SETTINGS_UNAVAILABLE`、`mirror profile ids: ['9813…']`、`json store profile ids: []` | 加 `sqlite3.Error` 并补一条「seam 提交后抛 sqlite3 错误」的反向测试；或明确登记「SQLite 异常跳过 rollback」并在 README 更正「正好」措辞。两者都不需要重开 scope。 | open |
| R2-002 | P2 | `verification/TRANS-BINDING-BRIDGE/README.md:29,30,49,106,112`；`logs/pytest-full.log` 头 | §1 AC6/AC7 仍写「7 例」「定向 108 passed（7 新 + 101）」；§3 仍写 108 passed；实际当前是 14 个 bridge 测试、定向 115 passed。§6.2 把 4 条反向测试统称「判别测试」，但只有 `test_store_update_failure_rolls_the_mirror_back` 对 `659bb3053` 的白名单改动敏感（实测 1 failed / 13 passed）；另 3 条是 OSError 回归钉。全量日志缺命令头 + EXIT。 | §6 实测；§4.2 回退探针 | 把 108 更新为 115、7 例更新为 14；反向表述改为「1 条 KeyError 判别 + 3 条 OSError 回归钉」；full log 补命令与 EXIT。 | open |
| R2-003 | P2（T-C 携带） | `settings_commands.py:801-808`、`:823-830`；R-6 | global-only 后，book/chapter 绑定只存在于 P15 行；`bindings_resolve(book)` 与 `run_snapshot_get` 仍可能展示 book profile，但 `_chain` 实际读 global 槽。T-C/UI 若把这两个面当作「本次 run 实际使用的 provider」会误导用户。 | 代码路径 + r1 R-001/R-6 裁决；测试 `test_book_scoped_binding_does_not_overwrite_the_global_step` 明确断言 book resolve=B 而执行槽=A | 在 T-C 文案/映射里明确「book/chapter 绑定当前不驱动执行」；或在后续卡把 run 快照展示改为以扁平槽为准。不在本卡改代码。 | deferred（R-6 已登记） |

> 不单列的观察：① 3 条 OSError 反向测试是好的回归钉，不应删除，只是不要称作本提交的判别测试；② 本卡未涉及升级迁移——若有安装曾用旧 bug 的 book 绑定写过扁平槽，升级后清 book 不会清该旧槽；本桥尚未发布，当前不构成真实风险，后续发布说明可留意；③ `settings_provider_bindings_clear` 对「有绑定的 book scope」没有单独测试，但逻辑与空 scope 相同，属测试完备性小缺口，不单列 finding。

## 9. 明确回答

1. **P1-1 是否已真实关闭？——是。** 执行链只读扁平 step 槽（四个读取点逐一核实），run 快照无 per-book step 槽；实现只在 global 时写/清扁平槽；回退 scope 分流后 3 条测试必然红（实测 3 failed / 11 passed），证明测试锁住了 r1 的劫持/清空场景。
2. **P1-2 是否已真实关闭？——是（就 r1 所指缺陷而言）。** `KeyError` 已进白名单，update 反向路径实测会回滚镜像并保持两侧一致；回退白名单后该测试必然红（1 failed / 13 passed）。`OSError` 三条反向路径也已有真实断言。**残余**：`sqlite3.Error` 仍会跳过回滚（R2-001，P2），这是异常族穷尽性问题，不是 r1 的 `KeyError` 缺陷复发。
3. **本卡能否收口？——可以。** P0/P1 = 0；定向/全量/四门禁/pins/inventory 全部通过；`apps/**` 与契约面零改动。收口时请：① 把 R2-001 作为 P2 接受或补 `sqlite3.Error` + 测试；② 按 R2-002 更正证据文本；③ 把 R2-003（scoped 绑定不驱动执行的展示面风险）写入 T-C 前置约束。若 DSH 对 AC3 采取「异常族必须穷尽」的更严口径，则先做 R2-001 的一行修复再收口；即便如此，也不需要重做本卡主体。

## 10. 复审说明

- 本报告固定 `reviewed_head: 659bb3053`；复核期间 worktree 前移到 `65425a24f`（仅 r1 报告 + task 记录），已确认 `src/tests/apps` 与该 head 零差异，实测对 `659bb3053` 有效。
- 本报告只覆盖 r1 修复面（scope 分流、反向回滚、7 例测试、异常白名单、实测、零越界）；不重新评价 `94b8f33f5` 的 AC1–AC8、键集、AC2 密钥面等已由 r1 通过的部分。
- 本次复核未发现需要回退/重做修复的证据；若后续 head 再变，本报告自动转为历史记录。
