**结论：诊断静态部分完成，执行部分全为 NOT_RUN；具体失败 DLL 仍 UNKNOWN，未自称任何 AC 全 PASS。**

**固定点/状态**
- branch=`agent/deepseek/M2-PACKAGED-AC1-DLL-DIAG`，base=`9063c317937b86bed1f6ff3e2f2c5d224dc10553`，期望 start_head=`24e0ec6e5c6d64a35daad006565919818616b317`。
- **delivery_head 未固定（未提交）**：本会话 shell 完全不可用，`git rev-parse/status/diff --check` 均无法执行。期望 head 未实测。

**执行限制（阻塞根因）**
- 每次 `pwsh` 都在启动前置阶段失败：`SetNamedSecurityInfoW failed (Win32 5): grantWrite(<worktree>)`；`danger-full-access` 升级被拒（无审批通道）。故 AC1/AC2=NOT_RUN，仅用只读文件工具，3 次命令尝试原文见 `raw/exec-20261008-dsh-notrun.log`。

**已写文件（均在 allowed_paths）**
`verification/M2-PACKAGED-AC1-DLL-DIAG/`：`REPORT.md`、`dll-closure-matrix.json`、`raw/exec-20261008-dsh-notrun.log`、`probe/{run_dll_diag_probe.ps1,pe_import_probe.py,README.md}`；`doc/handoffs/M2-PACKAGED-AC1-DLL-DIAG-20261008-dsh.md`；`doc/tasks/M2-PACKAGED-AC1-DLL-DIAG.md` 追加运行记录。未触碰 src/apps/tests/packaging（机器级 diff 证明 NOT_RUN，不作声明）。

**矩阵结论（14 项）**
- **REJECTED**：`Qt6Gui.dll`/`Qt6Core.dll`/`QtGui.pyd` 缺失；`pyside6.abi3.dll`/`shiboken6.abi3.dll` 缺失；MSVC/CRT 未随包；Qt 未进分析图（日志 239–243 触发 `hook-PySide6*`）；构建被 weights EXIT=1 截断（`sidecar-build.log:548-552` COLLECT 成功，EXIT=1 在 :560 由 `Get-FileHash` CommandNotFound 触发）；platform plugin 类根因（traceback 在 `acceptance_bridge.py:173` import 语句，早于 175 行构造）。
- **PROVEN 缺席、影响 UNKNOWN**：`icuin*.dll`、`d3dcompiler_47.dll`、`opengl32sw.dll` 未在 bundle。
- **UNKNOWN**：具体未解析 DLL/符号；安装态 `_internal` 完整性（无清单证据，CS-I1 仅证 4 个 exe）；运行期 DLL 搜索集；其他符号级错配。
- **根因类别**（高置信）：packaged 进程内 `PySide6.QtGui` 依赖链存在 Win32 126 未解析模块；**不从模块名倒推 DLL**。

**AC4 环境差量（PROVEN，日志级）**：PS5.1 `powershell -Force` 全量构 build success、随后 `Copy-MangaWeights` 因 `Get-FileHash` 不可用 EXIT=1（417.3s）；PS7 `pwsh` 无 `-Force` 走 `build_sidecar.ps1:173` 增量短路、只补 weights，EXIT=0（0.8s）→ 已安装 exe 全部来自那次全量构建。

**下一步**
1) Codex 实跑 `probe/run_dll_diag_probe.ps1 -InstallDir <lab install> -CopyBundle`（只写本 Task `lab/raw`，不改系统 PATH），取 `missing_union` + 复现 traceback，再独立审查本诊断；由 Codex 核对变更范围并提交、写定 delivery_head（我无 git 能力）。
2) 修复须**另开冻结 Task**（建议 `M2-PACKAGED-AC1-DLL-CLOSURE-FIX`，待 Codex 创建），建议 allowed_paths 仅 `packaging/m2ac5/**`（给 acceptance 入口补 Qt 闭包 build-time 断言），`src/**` 无证据不开；diagnostic done ≠ runner debt 解锁，仍需 fresh `-Force` 构建 + 固定 installer hash + 完整 26 项 Gate + 非作者 Review。本 Task 未 done、未自审。