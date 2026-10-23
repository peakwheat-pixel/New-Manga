# PLUGIN-RUNTIME-1 独立 Review r2（r1 处置复核）

- Reviewer：`reviewer-settings-a`（非实现者）
- 审查头：**`288763857e05dd5980c07a20728e1b4dc3d657f6`**
- 实现链：`c7934429`（base）→ `a80cfd0b`（实现）→ `d603fd51`（docs pin）→ `7253286f`（r1 修复）→ `28876385`（r2 evidence/handoff pin）
- 结论：**changes_requested**。P1-2、P1-3 的状态字段、P2 的大部分项已闭环；但 **P1-1 的“诚实降级”没有落实到 Task 目标/非目标与设计 §4.3，仍保留“无文件/网络/模型访问/任意路径不可访问”的过度承诺**。另有 4 项 P2（前端残留 `plugin_root`、输出上限按字符且先缓存后检查、`test_frozen_runtime_contract` 声称的双源校验实际未改、Task 正文/Closeout 仍为 in_progress/未开始）。

## 1. P1-1 复核：代码/UI/Handoff 诚实，但 Task/Design 仍过度承诺（未闭环）

已修正的部分：

- `manifest.py` / `service.py` 文档明确“trusted local code / no OS sandbox / malicious plugin can read files and sockets”；`PluginSettingsPanel.tsx:414-416` 写明“受信任的本地代码……本版本不做操作系统级沙箱”；Handoff `:56` 同样明确。
- 子进程最小 env、`-I`、cwd、无 Core env/无法 import Core 模块、输出上限测试已加（`test_plugin_runtime.py`）。
- 安全降级本身可接受：`permissions: []` 现在表示“Core 不授予能力句柄”，不再声称 OS 隔离；恶意插件仍可读文件/联网已在 UI/Handoff/代码注释中说明。

但 **Task 与 Design 仍保留旧的安全承诺**：

- `doc/tasks/PLUGIN-RUNTIME-1.md:42`：`permissions: []` 首发“本期只加载无权限插件（**无文件/网络/模型访问**）”。
- `doc/tasks/PLUGIN-RUNTIME-1.md:73`：明确不做项仍写“插件直接访问 DB/Repository/**任意路径**”。
- `doc/design/SETTINGS_SECTION_C_SCHEMAS.md:192`：C-3 首发限制仍写“只支持 `permissions: []` 的插件（**无文件/网络/模型访问**）”，`:285` 仍写“首版可先只支持‘纯计算’插件（无文件/网络）”。
- 这与 UI/Handoff/代码的诚实降级直接矛盾；Task 是后续 Owner 的契约，仍会让读者误以为插件无法读写文件/联网。**P1-1 不能说“已如实”**。建议：更新 Task 目标/非目标，并给 Design §4.3 加显式“实现降级说明/被 Task 覆盖”的注记（或修订设计），至少不能保留上述绝对安全表述。

## 2. P1-2/P1-3 复核

- **P1-2 fixed**：`_ALLOWED_KEYS` 白名单 + `set(raw) - _ALLOWED_KEYS` 拒绝；`test_manifest_rejections_are_typed` 新增 `acme-unknown-key`；插件目录/manifest 符号链接有 `is_symlink()` / `resolve().is_relative_to(root)` 检查。
- **P1-3 状态字段 fixed**：Task `:4`、STATUS `:7`、TASK_LEDGER `:34`、Handoff `:7` 均为 `in_review`；Handoff `delivery_head: 7253286f`，范围 `c7934429..7253286f`。
- **但 Task 正文/Closeout 未同步**：Task `:33` 仍写“**in_progress**”；Task `:109` 仍写“Closeout：未开始（proposed）”，而 Handoff `:58` 声称已改为“待 Review approved 后 closeout”。属于 P2 文档不一致，需随 P1-3 收尾。

## 3. P2 findings

1. **前端 `plugin_root` 残留**：Core `plugins.list` 已移除绝对路径，wire 测试也断言不存在；但 `client.ts:518-520` 的 `PluginsSnapshot` 仍要求 `plugin_root: string`，`normalizePluginsSnapshot` 仍读取它，`PluginSettingsPanel.test.tsx` 的 fake snapshot 仍塞 `"G:/data/plugins"`。虽然运行时归一化为空、未显示，但契约仍是“前端期望绝对路径”，应删除字段/测试数据，避免下一轮又把路径加回来。
2. **输出上限不是字节上限，且先缓存后检查**：`service.py:321-327` 用 `len(completed.stdout or "")` 判断 256KB；Python `len(str)` 是字符数，UTF-8 中文输出 100000 字符 = 约 300KB 仍可通过。且 `subprocess.run(capture_output=True)` 会先把全部 stdout/stderr 读入内存，之后才检查，无法防止超大输出耗尽 Core 内存；stderr 完全无上限。建议 `Popen` 流式读取并在字节数超限时立即终止，stdout/stderr 都设上限。
3. **`test_frozen_runtime_contract` 的“双源校验”实际未改**：当前文件仍只 `expected_schema = max(m.schema_version for m in default_migrations())` 后回读 `application_metadata`，没有查询 `schema_migrations` 的 max；`7253286f` 的改动文件列表也不含该测试（只改了 `tests/infrastructure/test_plugin_runtime.py` 与 `tests/core/test_core_plugin_wire.py`）。这与 Handoff/用户所称“双源校验”不符；建议真正加 `schema_migrations` 断言或修正 Handoff 描述。`test_v6_tables_start_empty_and_are_indexed` 已正确新增。
4. **状态驱动审计仍有额外 `load_ok` 边界**：`_write_state` 写 `manifest_json` 时使用 dict 顺序（未 `sort_keys`），而 `_manifest_fingerprint` 使用 `sort_keys=True`；启用插件后下一次 `list_plugins` 会因字符串不等再写一条 `load_ok`。虽然只多一条、不是重复列表循环，但与“load 事件只在 manifest 状态变化时写”不完全一致。建议 `_write_state` 复用 `_manifest_fingerprint`，并补“启用后连续 list 不新增 load_ok”的测试。
5. **`schema_ref` 仅输入标记**：`run_hook` 注入 `schema_ref=nm-plugin-hook/1`，但没有对 payload/结果做 versioned schema 校验；`before_*` override 也无 schema 校验。设计 §4.4/D3 的“versioned JSON schema”只完成了一半，建议在 Task/Handoff 明确“本期只注入 schema_ref，不校验 payload/结果”，或补校验。
6. **打开目录未做 GUI 验证**：`main.rs:812` 已改为 `NEWMANGA_DATA_ROOT` → `LOCALAPPDATA/New Manga` + `plugins`，路径逻辑与 Core 一致，方向正确；但 GUI 烟测没有实际点击“打开插件目录”验证，且 `LOCALAPPDATA` 缺失时 Tauri 报错而 Core 会回退 `Path.home()`（边界不一致）。补一次点击验证即可，非阻塞。
7. **Task Closeout 文案/正文状态**：见 P1-3 末尾；另 Task 证据行仍统一标 `AC1-AC6`，而 AC6b 明确 NOT_RUN，若要精确可拆成 `AC1-AC6a`/`AC6b`。

## 4. 独立验证

| 检查 | 结果 |
|---|---|
| 定向 pytest（runtime + core wire） | **30 passed** |
| 全量 pytest | **2639 passed / 9 skipped / 3 failed**（与交付说明一致：detector 权重 2 + workbench 时序 1，均与本改动无关） |
| vitest | **45 files / 434 tests passed** |
| `tsc --noEmit` | exit 0 |
| `check.ps1` | PASS（3 warnings；3 个非终态 Task，含 `PLUGIN-RUNTIME-SANDBOX-1` proposed） |
| v6 | schema=6；`plugin_state=0`、`plugin_events=0`；两索引存在；新测试覆盖 |
| 安全 | 未知字段现在被拒绝；目录/manifest symlink 校验存在；子进程 env/sys.path/import Core 测试通过；`permissions: []` 插件仍可读插件根外文件（已按 trusted code 诚实声明，不再作为隐藏漏洞） |
| Rust cargo | 证据日志 153 passed / 1 ignored / 12 filtered；Reviewer 本机仍因 `M2RC1_PYTHON` 未设置无法完整复跑（13 个 packaged/并发测试），未计为产品失败 |
| GUI | 12 开、默认关、拒绝原因、逐插件启用、审计；无 Hook 审计（AC6b 已正确标 NOT_RUN） |

## 5. 结论与下一步

**changes_requested。** 安全代码边界已按事实降级、P1-2/P1-3 状态字段与 P2 大部分项已修；但 Task/Design 仍保留“无文件/网络/模型访问/任意路径不可访问”的旧承诺，属于 P1 文档契约阻塞，不能 approve。

建议：

1. 修 Task `:42`、`:73`、Design `§4.3`/`:285` 的过度承诺，写清“trusted code + zero granted capabilities，无 OS 沙箱”；
2. 修 Task 正文 `:33` 和 Closeout `:109`，使其与 `in_review`/“待 Review approved”一致；
3. 删除前端 `plugin_root` 字段/测试数据，修正 `test_frozen_runtime_contract` 的双源校验（或改 Handoff 描述），并补输出字节上限/启用后审计不重复的测试；
4. 复审 r3 通过后再 closeout，随后进入 PLUGIN-RUNTIME-2 或先释放 `PLUGIN-RUNTIME-SANDBOX-1`。
