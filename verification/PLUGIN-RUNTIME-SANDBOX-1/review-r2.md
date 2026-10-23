# PLUGIN-RUNTIME-SANDBOX-1 独立 Review r2（r1 处置复核）

- Reviewer：`reviewer-settings-a`（非实现者）
- 审查头：**`41d7abeb98c0d2903d4a87224e6746872336c104`**
- 实现链：`1a17decf`（base）→ `22f09e90` → `b95a0c7a` → `84a63788`（r1 修复）→ `ac2d3ad0` → `41d7abeb`（canonical 表）
- 结论：**approved**。r1 的 P1-1/P1-2/P1-3 主体已闭环：生产 `core_assembly` 真正注入 AppContainer，真实 `assemble_core_services` 测试通过；sandbox 子进程使用显式 UTF-16 最小环境；UI/Task/Handoff 已改为“只读例外 + 共享容器 + 最小 env + fail-closed”的真实表述。剩余为 P2 文档/防御性加固，不阻塞产品验收。

## 1. r1 P1 复核

### P1-1 生产装配 — fixed

`src/bootstrap/core_assembly.py:1212` 现已实际构造：

```python
plugins = PluginService(
    conn,
    plugin_data_root / "plugins",
    app_version=_APP_VERSION,
    sandbox=AppContainerSandbox(
        anchors=(str(plugin_data_root), str(plugin_data_root.parent)),
    ),
)
```

- `AppContainerSandbox` 不再只是 import；生产路径传入 sandbox。
- `tests/infrastructure/test_plugin_sandbox.py::test_production_assembly_wires_the_sandbox` 走真实 `assemble_core_services`，断言 `core.plugins._sandbox is not None`，并真实执行 sandboxed hook；本次定向 49 passed 通过。
- 解释器改为 `prepare_plugin(interpreter=...)`/`run(interpreter=...)` 惰性设置，装配期不解析；frozen 无 Python 时在 hook 阶段 fail-closed（`_hook_interpreter()` 抛 `PLUGIN_HOOK_UNAVAILABLE`，无沙箱回退）。

### P1-2 最小环境 — fixed

`sandbox.py` 的 `CreateProcessW` 已改传 UTF-16 环境块（`CREATE_UNICODE_ENVIRONMENT`），`_child_environment()` 只保留：

- 固定 `PYTHONIOENCODING=utf-8`、`PYTHONDONTWRITEBYTECODE=1`
- 现有 `SYSTEMROOT`、`SYSTEMDRIVE`、`LOCALAPPDATA`

不再继承 `NEWMANGA_*`/`M2RC1_*`/`DSH_*`/代理/API key 等完整 Core 环境。`test_hook_child_sees_only_the_minimal_environment` 覆盖禁止前缀/代理/凭据；实测通过。

**LOCALAPPDATA 例外可以接受**：它是 AppContainer `CreateProcessW` 启动路径的实测必需变量（去掉会 WinError 203），属于用户目录的通用位置而非 New Manga 私有配置；在 ACL 已阻断实际文件读取的前提下，保留该单一变量合理。建议在 Task/Handoff 明确它是“唯一保留的用户路径变量”，避免被误读为完整用户目录授权。

### P1-3 诚实性 / AC6 — fixed（主文案）

`PluginSettingsPanel.tsx` 安全说明现在明确：

- AppContainer + Job Object；
- `permissions: []` 无网络；
- 只读访问**本插件目录与 Python 运行时**（解释器/DLLs/Lib 与 runner 为只读例外）；
- 插件之间共用同一容器（v1）；
- 环境最小化，应用私有变量/代理/凭据不传递；
- 沙箱失败 fail-closed + 审计。

Task/Handoff/AC6 与实现一致；AC6 UI `vitest panel 8` 已覆盖 policy note。没有把“OS 沙箱”写成“绝对用户文件隔离”的旧承诺。

## 2. 独立验证

| 检查 | 结果 |
|---|---|
| 定向 pytest（sandbox/runtime/wire/core assembly） | **49 passed** |
| 全量 pytest | **2660 passed / 9 skipped / 3 既有失败**（与交付说明一致：detector 权重 2 + workbench 时序 1） |
| vitest | **45 files / 434 tests passed** |
| `tsc --noEmit` | exit 0 |
| `check.ps1` | PASS（4 warnings：STATUS/REBASELINE 预算、2 非终态） |
| 生产装配 | `assemble_core_services` 真实构造 sandbox；sandboxed hook 成功 |
| 安全用例 | 读根外文件 `BLOCKED`、联网 `NET_BLOCKED`、benign、timeout、fail-closed、共享容器、最小 env、输出字节上限、Job 孙进程树杀均通过 |
| 探针 | `probe-appcontainer.log` `{"fs": "BLOCKED:None", "net": "NET_BLOCKED"}` |

## 3. 剩余 P2 / P3（不阻塞）

1. **Task 测试路径写错**：Task `:67` 写“`tests/core/test_core_assembly.py` + `test_production_assembly_wires_the_sandbox`”，但该测试实际在 `tests/infrastructure/test_plugin_sandbox.py`；`tests/core/test_core_assembly.py` 里没有它。建议改为实际文件，避免证据链误读。
2. **STATUS 仍写 r1**：`doc/STATUS.md:7` 仍“r1 修复待复审”，当前已是 r2；建议改“r2 修复待复审/复审中”。
3. **Handoff 描述与代码不完全一致**：Handoff `:51` 称 `core_assembly` 构造 `AppContainerSandbox(interpreter=resolve_hook_interpreter(), ...)`；实际 core_assembly 只传 `anchors`，解释器由 service `prepare_plugin(interpreter=...)` 惰性设置。行为正确，文案应改为“惰性解析”以避免误读。
4. **allowed_paths 仍不覆盖全部改动**：84a/22f 修改了 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`，Task `allowed_paths` 现在只补了 `src/bootstrap/core_assembly.py`，仍没有这些文档；建议标为 Lead 集成或补路径。
5. **UI 对共享容器跨插件读的表述可以更明确**：UI 写了“插件之间共用同一容器（v1）”，但未直说“插件 A 可能读取已授权插件 B 的目录”；Task/Handoff 已把跨插件读列为 v1 威胁模型外。若接受该威胁模型，UI 可加一句“不保证跨插件目录隔离”。
6. **`_invoke` 仍保留无 sandbox 分支**：生产已传 sandbox，但 `PluginService(sandbox=None)` 仍走旧无沙箱 `Popen`。建议对生产装配之外的构造加显式 `allow_unsandboxed=False` 或断言，避免未来新入口漏传 sandbox。
7. **P3**：`_write_all` 仍在 deadline 之前同步写 stdin（plugin payload 极大时可能阻塞）；`ResumeThread` 返回值未检查；`_sid_pointer`/CreatePipe/属性列表失败路径存在句柄/`LocalAlloc` 泄漏。可选加固。

## 4. 结论

**approved。**

- P1-1/P1-2/P1-3 已闭环；生产路径真实沙箱化，最小 env 与 Job 树杀有真实 AppContainer 测试。
- 无新 blocker；P2 主要是 Task/Handoff/STATUS 文案、allowed_paths 与共享容器说明，可在 closeout 前顺手修。
- 建议 closeout 前修 P2-1/2/3/4；P2-5/P2-6/P3 可留后续或 `PLUGIN-RUNTIME-SANDBOX-2`。
- 关闭后下一步：GUI 端到端沙箱冒烟（已知未做）或 per-plugin profile/capability 接线后续。**当前可 approved/closeout。**
