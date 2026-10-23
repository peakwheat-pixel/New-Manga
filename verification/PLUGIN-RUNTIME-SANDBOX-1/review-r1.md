# PLUGIN-RUNTIME-SANDBOX-1 独立 Review r1

- Reviewer：`reviewer-settings-a`（非实现者）
- 审查头：**`b95a0c7a9ab89b89dd9e6ef865cf8dba31738e63`**
- 实现 commit：**`22f09e9056ad0c581db13eb61532035b032ba4b9`**；base：`1a17decf1`
- 结论：**changes_requested**。AppContainer/ACL/Job 的可行性测试本身真实且通过，但 **生产 `core_assembly` 没有注入 sandbox**，所有真实容器测试都只绕过生产装配直接构造 `PluginService(sandbox=...)`；同时 **`CreateProcessW` 继承完整 Core 环境**，UI/Task 的“环境最小化、不传配置路径、生产 AppContainer 已启用”均不成立。安全边界未落地，不能 approved。

## 1. P1 findings

### P1-1（阻塞）— 生产装配没有注入 AppContainerSandbox，实际仍走无沙箱 `_invoke`

`22f09e90` 在 `src/bootstrap/core_assembly.py:117` 只新增了 `from infrastructure.plugins.sandbox import AppContainerSandbox`；生产装配仍为：

```python
# src/bootstrap/core_assembly.py:1212
plugins = PluginService(conn, Path(db_path).parent / "plugins", app_version=_APP_VERSION)
```

没有 `sandbox=AppContainerSandbox(...)`。全仓库搜索可见 `AppContainerSandbox` 在 `src/**` 只出现在这一行 import，未实例化；`PluginService.__init__` 的 `sandbox` 默认 `None`，因此生产 `_invoke` 继续走早先的无沙箱 `Popen` 分支。

- 6 个 AppContainer 测试全部在 `tests/infrastructure/test_plugin_sandbox.py` 的 `_Runtime` 中直接 `AppContainerSandbox()` 并注入 `PluginService`；没有一条经过 `assemble_core_services`/`build_production_handlers`。
- Task/Handoff/UI 却声明“`core_assembly` 生产装配注入 `AppContainerSandbox(anchors=(data_root, data_root.parent))`”“生产 AppContainer 已启用”。这是核心交付缺失，不是测试问题。
- 影响：实际生产插件仍可任意读写/联网；本 Task 的 AC1/AC2/AC6 在真实产品路径上不成立，且 `_invoke` 的无沙箱旁路就是“fail-closed 无旁路”的反例。

建议：在 `core_assembly` 构造 `AppContainerSandbox(anchors=(data_root, data_root.parent))` 并传给生产 `PluginService`；增加一个经过 `assemble_core_services` 的集成测试，断言 `plugins._sandbox is not None`，且沙箱不可用时 hook 返回 `PLUGIN_HOOK_UNAVAILABLE` 而不是走 `_invoke`。

### P1-2（阻塞）— AppContainer 子进程继承完整 Core 环境，配置路径/凭据仍泄露

`src/infrastructure/plugins/sandbox.py` 的 `CreateProcessW` 把 `lpEnvironment` 设为 `None`（继承父进程环境）；`_invoke_sandboxed`/`run` 没有构造最小 env。`-I` 只隔离 Python 导入，不清空 `os.environ`。

独立复现（真实 AppContainer，临时插件返回 `os.environ`）：

- 插件成功读取到 `NEWMANGA_DATA_ROOT`、`M2RC1_PYTHON`，以及 `DSH_*`、`HTTP_PROXY`/`HTTPS_PROXY`、`USERPROFILE`、`APPDATA`、`PATH` 等整套 Core 环境；`run_hook` 返回 `applied: true`。
- 因此 UI `PluginSettingsPanel.tsx:414-415` 的“Core 不向插件传递数据库/模型/凭据/配置路径”“子进程环境最小化”不成立；Task/Handoff 的“最小 env”也不成立。
- 即使 AppContainer 阻断了文件 ACL，插件仍能拿到配置路径、代理、DSH 会话变量，并可尝试读取/利用；这与 AC6“文案与实际一致”冲突。

建议：`AppContainerSandbox.run` 接受显式 `env`（只保 `SYSTEMROOT`/`PATH`/`PYTHONIOENCODING` 等必要项），用 `CreateProcessW` 的环境块传入；补“沙箱子进程看不到 `NEWMANGA_DATA_ROOT`/`M2RC1_PYTHON`/`DSH_*`/代理”的测试。

### P1-3（阻塞）— Task/Handoff/UI 把“生产已沙箱化”当作事实，实际未接线

- Task AC6/Handoff/UI 均声明 AppContainer 生产已启用、fail-closed 无旁路；但 P1-1 表明生产无 sandbox，P1-2 表明环境未最小化。
- `PluginSettingsPanel.tsx:414-416` 进一步声称“容器无法读取插件目录之外的**任何文件**”；这与实际 ACL（解释器/DLLs/Lib、runner 文件、共享容器下其他插件目录）以及环境泄露矛盾，属于过度承诺。
- 测试只证明“直接构造 sandbox 的 API 可用”，不能证明“产品路径启用”。在修复 P1-1/P1-2 前，AC6 和诚实性不成立。

## 2. P2 findings

1. **`core_assembly` 超出 allowed_paths**：Task `allowed_paths` 只含 `src/infrastructure/plugins/**`、`tests/**`、Task/Handoff/verification；`22f09e90` 却改了 `src/bootstrap/core_assembly.py`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`。需补 allowed_paths 或由 Lead 明确集成路径。
2. **STATUS 无 active，但 Task/Handoff/LEDGER 为 `in_review`**：`doc/STATUS.md:7` 写“当前 Task：无 active”；`TASK_LEDGER` 与 Task 是 `in_review`；生命周期不一致，closeout 前需统一。
3. **ACL “traverse” 实际是 `(RX)`**：`_traversal_chain` 与 `for anchor in self._anchors: _grant(anchor, "(RX)")` 给数据根/父目录完整读+列目录权限，不是 traverse-only；且生产未注入 anchors（所以“数据根两级 traverse”未验证）。即使在测试无 anchors 下，`tmp_path` 父目录也可被列目录。建议用 `(X)`/`(RX)` 区分，只授必要父级 traverse，并补 anchors 测试。
4. **`AssignProcessToJobObject` 失败未 fail-closed**：`sandbox.py` 中赋值失败只 `TerminateProcess` 并继续，不抛 `SandboxError`；Job 未拥有进程树时超时/关闭不能保证孙进程被杀。建议失败即 `SandboxError`，并补“子进程再 spawn 孙进程，超时后全灭”的真实测试。
5. **`AppContainerSandbox` 默认解释器与 `_hook_interpreter` 可能不一致**：sandbox 的 `_interpreter` 默认 `sys.executable`；生产打包时它是 app exe，而 `_invoke_sandboxed` 传的是 `_hook_interpreter()` 的 sibling python。`_prepare_interpreter` 会授错解释器 ACL，沙箱可能永远失败；生产注入时必须显式传实际解释器。
6. **测试未覆盖生产装配/环境/输出上限/Job 子进程树**：6 个用例真实执行 AppContainer（这点通过），但没有 `assemble_core_services` 集成、没有 env 泄露断言、没有 sandbox 输出超限、没有 Job 树杀测试；有假阳性风险。
7. **Task canonical evidence 只有 3 行**（pytest targeted/full + probe），AC6 的 vitest/panel 和 tsc/cargo 没有 canonical 行；Task 还保留两个 `## Closeout Record` 标题（`:54`/`:69`），属 P3 文档整理。
8. **共享容器跨插件读**：Task 明确“跨插件目录读取不在 v1 威胁模型”，但 UI 声称“插件目录之外任何文件”都不可读；共享 SID + 每插件目录 RX 意味着插件 A 在 B 的目录被授权后可读 B 的代码/文件。若接受此威胁模型，UI 应改为“不保证跨插件隔离”；否则 per-plugin profile。
9. **`_sid_pointer`/CreatePipe/Job/属性列表失败路径的句柄与 LocalAlloc 未释放**；`_write_all` 若 `WriteFile` 返回成功但写入 0 可能死循环；`_prepare_interpreter` 递归 RX 是整个解释器根（含 site-packages），应确认是否必要。属 P3 资源/健壮性。

## 3. 已核验

- 定向 pytest：**37 passed**（含 6 个真实 AppContainer 用例）；全量：**2656 passed / 9 skipped / 3 既有失败**（与交付说明一致）。
- vitest：**45 files / 434 tests passed**；tsc 0；`check.ps1` PASS（4 warnings；STATUS/REBASELINE 预算，2 非终态）。
- `probe-appcontainer.log`：真实 profile + `icacls`，输出 `{"fs": "BLOCKED:None", "net": "NET_BLOCKED"}`。
- 测试中的读取根外文件/联网/benign/timeout/fail-closed/shared container 均真实执行（非 mock）；但都不经过生产 `core_assembly`。
- 独立环境探针：sandbox 子进程可见完整 Core env（P1-2 证据）。

## 4. 建议下一步

1. **先修 P1-1**：生产装配注入 sandbox + 集成测试；确保 `_invoke` 无 sandbox 旁路在生产不可达。
2. **修 P1-2**：显式最小环境；补 env 泄露测试；再修 P1-3 的 UI/Task/Handoff 文案。
3. 修 P2 的 allowed_paths/STATUS/ACL traverse/Job assign fail-closed/解释器一致性；补 Job 树杀、输出上限、生产装配测试。
4. 之后复审 r2；通过后再 closeout，再考虑 GUI 端到端沙箱冒烟或 capability SID 接线。**当前不能 approved/closeout。**
