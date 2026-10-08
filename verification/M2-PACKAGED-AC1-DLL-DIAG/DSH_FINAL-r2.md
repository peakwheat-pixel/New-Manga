**r1 返修完成（实跑项仍全为 NOT_RUN）。**

**改动路径（仅 Task 自有文件）**
- `verification/M2-PACKAGED-AC1-DLL-DIAG/probe/run_dll_diag_probe.ps1`
  - R1：步骤 1 **fail-closed**——installer 缺失或 SHA256 与固定 pin 不一致时 `Say FAIL_CLOSED` 后 `throw`（非零退出），不再打印后继续。
  - R2：默认 **static-read-only，不启动任何 exe**；复制改为 copy-only `robocopy /E`（**无 `/MIR`、无 PURGE**，源树只读）；复制 exit≥8，或 lab 内 `acceptance_bridge.exe`/`Qt6Gui.dll`/`Qt6Core.dll`/`pyside6.abi3.dll`/`shiboken6.abi3.dll` 缺失或 SHA256 不一致→**立即停止**；仅"复制成功+lab 内已核验"才运行**自有 lab 副本**，绝不从原 bundle 启动。
- `verification/M2-PACKAGED-AC1-DLL-DIAG/REPORT.md`、`dll-closure-matrix.json`、`doc/handoffs/M2-PACKAGED-AC1-DLL-DIAG-20261008-dsh.md`
  - R3：具体 **Win32 错误码 = UNKNOWN**（原日志无 `GetLastError`），删除"126/ERROR_MOD_NOT_FOUND 高置信"；明确"DLL 未出现在枚举的构建树"**不证明**安装态缺失、**不证明**加载失败；新增矩阵作用域声明，C1–C5/C8–C10 判定降为"仅在该扫描树如此"。
  - Handoff 已引用固定 draft head `f0ad317c77c1ca35f156e8fd8c0d3f73502cdd50`，`delivery_head` 仍为 null（无 git，未提交、未实测），并附本轮变更记录。
- `doc/tasks/M2-PACKAGED-AC1-DLL-DIAG.md`：追加 r1 返修运行记录（未改 status）。

**结果**：本轮仍无 shell（`SetNamedSecurityInfoW failed (Win32 5)`），按 r1 指示未再重复权限尝试 → 复现运行、installer hash 复测、`git diff --check`、产品零差量机器证明**全部 NOT_RUN**；r1 原始最终回答与 `raw/exec-20261008-dsh-notrun.log` 原文保留未改。

**仍 UNKNOWN**：具体未解析 DLL/导出符号、Win32 错误码、安装态 `_internal` 完整性、运行期搜索路径、符号级错配；连"依赖解析失败"类别也仅 medium 推断。未改 Plan/STATUS/索引，未改 src/apps/tests/packaging，未新增依赖，未置 done。

**下一步**：Codex 实跑 probe（先静态，再 `-CopyBundle` 隔离复现）并记录新 head 与独立验证；修复须另开冻结 Task，建议 allowed_paths 仅 `packaging/m2ac5/**`。