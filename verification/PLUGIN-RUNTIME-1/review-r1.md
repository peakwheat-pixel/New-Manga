# PLUGIN-RUNTIME-1 独立 Review r1

- Reviewer：`reviewer-settings-a`（非实现者）
- 审查头：**`d603fd518065e933117a6b5ce9a4122093369ebc`**
- 实现 commit：**`a80cfd0bb83752534e138b0db7d04bfb2d2782a6`**；base：`c7934429`
- 结论：**changes_requested**。运行时主体、默认禁用、崩溃/超时隔离、迁移 v6、wire/Rust/前端表面大多成立；但 **`permissions: []` 的“无文件/网络访问”没有执行**（普通 `python -I` 子进程仍可任意读文件/联网）、**manifest 未知字段未 fail-closed**、**Task/STATUS/LEDGER 仍为 `in_progress`**，另有 AC6 GUI 证据、绝对路径、打开目录根路径等 P2。安全边界不满足，不能 approved。

## 1. P1 findings

### P1-1（阻塞）— `permissions: []` 未形成安全边界：无权限插件仍可任意读文件/联网

设计 §4.3 / Task AC1 声称首发只支持“无文件/网络/模型访问”的 `permissions: []` 插件；实现只做了 **manifest 层拒绝非空 permissions**，Hook 子进程没有 OS 级沙箱。

代码路径：

- `src/infrastructure/plugins/service.py:280` 用普通 `subprocess.run([interpreter, "-I", runner, entry, hook])` 启动子进程；`-I` 只隔离 `PYTHONPATH`/site，不限制文件系统、网络、进程创建。
- `src/infrastructure/plugins/_hook_runner.py:40-45` 直接 `exec_module(plugin)`，插件代码以当前用户权限运行完整 Python。
- `src/infrastructure/plugins/manifest.py:173` 只拒绝 `permissions` 非空；`permissions: []` 没有对应的 capability enforcement。

独立复现（未改产品代码，临时目录）：

1. 写一个 `permissions: []`、`hooks: ["after_detect"]` 的插件，`after_detect` 对插件根之外的临时 `secret.txt` 执行 `Path(...).read_text()` 并返回。
2. `PluginService.run_hook("after_detect", {})` 返回 `applied: True`、`result: {"leak": "TOP-SECRET"}`；审计写 `hook_invoked`，无 `plugin_error`。

即：一个无权限声明的插件可以直接读取用户文件、写文件、访问网络、启动进程。**“未声明权限 = 不可用”在当前实现中不成立**；`permissions: []` 只是声明约束，不是能力隔离。

建议（任一，不能只改文案）：

1. 给 Hook 子进程加 OS 级沙箱（Windows restricted token/AppContainer/job object，限制文件/网络/子进程），并在文档中明确“首发仍不可信插件”；
2. 或者把本 Task 的范围明确降级为“manifest 仅拒绝带权限插件；无 OS 沙箱，插件代码视为用户信任代码”，同时修正设计/Task/UI 中“无文件/网络/模型访问”的安全承诺，并加安全差距 follow-up；
3. 无论选哪种，增加“试图读插件根外文件/联网必须失败”的隔离测试；当前 24 个测试没有这条。

### P1-2（阻塞）— manifest 未知顶层字段被接受，未 fail-closed

Task AC1 与 §4.2 要求未知字段拒绝；`parse_manifest` 只读取已知字段（`manifest.py:124` `raw = json.loads(...)`，随后 `raw.get`），没有任何 allowed-key 集合校验。

独立复现：在合法 manifest 中加入 `"evil_unknown": true`，`parse_manifest` **正常返回** `PluginManifest(...)`，插件被列为可加载。

影响：未知字段可被未来/恶意 manifest 用来携带未定义语义，且违背 Task 的 fail-closed 声明。建议在 `parse_manifest` 增加 `allowed = {...}` 并拒绝 `set(raw) - allowed`，补一条 manifest 拒绝测试。

### P1-3（阻塞）— Task/STATUS/LEDGER 生命周期仍为 `in_progress`

- `doc/tasks/PLUGIN-RUNTIME-1.md:4`：`status: in_progress`
- `doc/STATUS.md:7`：当前 Task `in_progress`
- `doc/TASK_LEDGER.md:34`：`PLUGIN-RUNTIME-1` `in_progress`
- `doc/handoffs/PLUGIN-RUNTIME-1-a80cfd0b.md:7`：`status: in_review`
- 用户消息也称 Task `in_review`

`check.ps1` PASS 只说明 checker 接受 lifecycle v1，不代表状态一致；Task `Closeout` 仍写“未开始（proposed）”（Task `:105`）。当前无法进入 done/closeout，需先统一 `in_review` 并提交 STATUS/LEDGER/Task，确保工作区干净。

## 2. P2 findings

1. **AC6 GUI 证据不完整**：Task `:65` 将 AC6 勾为“GUI 烟测：安装 → 启用 → **触发一次 Hook** → 审计可查”；但 `gui-smoke.md:36` 只验证发现/拒绝、全局启用、逐插件启用，审计 4 条中无 `hook_invoked`；`gui-smoke.md` 自己写明 Hook 调用/崩溃/超时“由单测覆盖”。Task `:82` 的烟测行也只写“面板发现/拒绝 + 启用 + 审计”。已知流水线接线不在本 Task 范围时，应把 AC6 拆成“run_hook API 实子进程测试”与“GUI 管理面”两项，或明确 AC6 Hook 部分 **NOT_RUN**；当前 `[x]` 不准确。
2. **`plugins.list` 投影绝对 OS 路径**：`service.py:145` 返回 `"plugin_root": str(self._plugin_root)`；`tests/core/test_core_plugin_wire.py` 还断言 `.endswith("plugins")`。这违反三节通用纪律“所有 IPC 不投影 OS 绝对路径”（§1.2）；前端 `PluginsSnapshot.plugin_root` 也未真正使用，建议移除或改为相对标识。
3. **打开插件目录的根路径与 Core 扫描根可能不一致**：`main.rs:815` 的 `plugins_open_directory` 用 Tauri `app_data_dir()/plugins`；Core `core_assembly.py:1396-1401` 扫描的是 `<data_root>/plugins`，而 dev preview 通过 `NEWMANGA_DATA_ROOT` 指定隔离 data root。GUI 烟测只看到“打开插件目录”按钮，没有实际点击验证；若 `app_data_dir` 与 `NEWMANGA_DATA_ROOT` 不同，用户会被带到错误目录，放进去的插件 Core 也不会发现。建议 Core 统一暴露/返回插件根（不投影绝对路径给 renderer 时可由 Tauri 使用同一数据根解析），并补一次 GUI/集成验证。
4. **插件目录 symlink 边界**：`service.py:327` 仅 `candidate.is_dir()`（跟随 symlink），`manifest.json` 也可为 symlink；指向插件根外的目录/文件可能被当作合法插件加载。建议 `resolve()` 后校验仍位于 `plugin_root.resolve()` 内，并拒绝 symlink 插件目录（或明确允许并记录）。
5. **子进程资源边界不足**：`capture_output=True` 无 stdout/stderr 上限；超时只杀直接子进程，插件若启动孙进程、输出巨量内容、耗尽内存/CPU，仍可能影响宿主；建议 job object/进程树终止、输出上限、资源限制。
6. **Hook payload/result 未实现 versioned schema**：设计 §4.4/D3 要求 versioned JSON（`schema_ref` + payload）；当前 `run_hook` 只要求 payload 是 dict，插件结果任意 JSON 即返回，`before_*` 的 override 也没有 schema 校验。属于契约 P2（若后续接线再补，需在 Task/Handoff 明确）。
7. **审计 60s 去重语义**：`service.py:_record_event` 对同 plugin/event/hook/detail 的 60s 内重复事件去重，能避免 `list_plugins` 每次重新发现写重复 `load_ok/load_rejected`，作为 UI 去抖可接受；但它不是“每次加载都记录”的严格 append-only 语义，且审计写入异常被静默吞掉。建议在 Task/Handoff 明确该语义与失败策略。
8. **测试硬编码改动的覆盖面**：`test_schema_migration`/`test_backup_restore`/`test_frozen_runtime_contract` 改为 migration-driven 的方向合理，能避免 v6 后逐处改 5→6；但 `test_frozen_runtime_contract` 用 `default_migrations()` 最新值断言同一来源的 `application_metadata.schema_version`，属于同源回读，不能捕获“迁移列表漏掉 v6/顺序错误”。另没有显式断言 v6 的 `plugin_state/plugin_events` 为空表、CHECK/索引存在（本次实测 schema=6、两表 0 行、索引存在，但未固化成测试）。建议补 v6 专项断言。
9. **Task allowed_paths 未覆盖文档**：`a80cfd0b` 修改了 `doc/STATUS.md`、`doc/TASK_LEDGER.md`、`doc/REBASELINE_PLAN.md`，但 Task `:11-25` 的 allowed_paths 只有 `doc/tasks/PLUGIN-RUNTIME-1.md`、`doc/handoffs/**`、`verification/PLUGIN-RUNTIME-1/**` 等，不包含 STATUS/LEDGER/REBASELINE；属于 P2 范围/证据卫生，建议 Task 明确文档集成由 Lead 负责或在 allowed_paths 补上。
10. **Task Closeout 文案**仍“未开始（proposed）”（`:105`），与 Handoff/用户所称 `in_review` 不一致，随 P1-3 一并修。

## 3. 独立验证

| 检查 | 结果 |
|---|---|
| `python -m pytest tests/infrastructure/test_plugin_runtime.py tests/core/test_core_plugin_wire.py -q` | **24 passed** |
| `python -m pytest -q`（全量） | **2633 passed / 9 skipped / 3 failed**；与交付说明一致（detector 权重 2 + workbench 时序 1，均与本次改动无关） |
| `npm --prefix apps/desktop/frontend test` | **45 files / 434 tests passed** |
| `tsc --noEmit` | exit 0 |
| `check.ps1` | PASS（3 warnings：2 非终态、STATUS 预算、lifecycle v1） |
| 迁移 v6 实测 | schema=6；`plugin_state=0` 行、`plugin_events=0` 行；两表 + 两个索引存在 |
| GUI 截图 | 12 分类开放；插件面板默认全局关、拒绝原因可见、逐插件启用、审计 4 条；无 Hook 审计 |
| Rust cargo | 证据日志 `153 passed / 1 ignored / 12 filtered`；Reviewer 独立运行因本机 `M2RC1_PYTHON` 未设置而失败（13 个 packaged/并发测试均因该环境变量），**未作为产品失败计入**；需在带 P02 Python 的环境复核 |
| 安全实测 | `permissions: []` 插件读取插件根外临时文件成功（P1-1）；额外 manifest 字段被接受（P1-2） |

- 未修改产品代码；只新增本 Review 文件。工作区仍只有既有 P04 未跟踪诊断文件。
- 未执行：真实 Run 内 Hook 接线（Task 明确非本 Task 范围）；打包环境解释器捆绑（非本 Task）。

## 4. 建议下一步

1. **先修 P1-1/P1-2**：选择“OS 沙箱”或“明确降级为 trusted code 并删除无访问承诺 + follow-up”，补隔离/未知字段测试；这是安全边界，不是文案问题。
2. **修 P1-3**：Task/STATUS/LEDGER 统一 `in_review`，提交并清工作区；Closeout 文案改为“待 Review approved”。
3. **修 P2**：AC6 证据拆分/NOT_RUN、移除 `plugin_root` 绝对路径、对齐 open-directory 与 Core 数据根、补 symlink/资源/Hook schema/迁移专项测试。
4. 上述完成后复审 r2；通过后再 closeout，并考虑 **PLUGIN-RUNTIME-2（Hook 流水线接线）** 或先补安全沙箱 follow-up。**当前不能 approved/closeout。**
