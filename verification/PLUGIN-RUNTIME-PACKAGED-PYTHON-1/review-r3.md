# PLUGIN-RUNTIME-PACKAGED-PYTHON-1 独立 Review r3（r2 修复复核）

- Reviewer：`reviewer-settings-a`（非实现者）
- 审查头：**`a1f05450e2157e79c264a8dadc2f45b5f089f5a1`**
- 实现链：`2b965c1b`（base）→ `d8bab54d` → `9a22f5f8` → `bc72d883` → `df057c78` → `9e79153a` → `cfc737fc`（r2 修复）→ `a1f05450`（pin）
- 结论：**approved**。r2 的两个 P1 已闭环：增量分支现在会复制 Python，默认（不传 `-BundlePythonRuntime`）从构建解释器 `sys.base_prefix` 解析运行时；实际 `core-sidecar/core-sidecar/python/python.exe` 存在并在最小 PATH 下通过 `socket/ssl/sqlite3/json/hashlib` smoke，真实 bundle 的 frozen 解析与 AppContainer Hook 也通过。剩余为 P2/P3 文档、默认失败语义与证据 HEAD 记录。

## 1. r2 P1 复核

### P1-1 增量短路 — fixed

`packaging/m2ac5/build_sidecar.ps1` 的增量分支现在：

```powershell
if (-not $Force -and (Test-Path $existingBundle)) {
    Write-Host "build_sidecar: target exists, skipping PyInstaller (use -Force to rebuild)"
    ...weights...
    if ($BundlePythonRuntime) {
        Copy-PluginPythonRuntime -Bundle $existingBundle -RuntimeDir $BundlePythonRuntime
    }
    exit 0
}
```

本次独立复跑：

```text
pwsh -File packaging/m2ac5/build_sidecar.ps1 -SkipWeights
→ INCR_EXIT=0
→ bundle_python_runtime: OK -> .../core-sidecar/core-sidecar/python
→ PY_EXISTS=True
```

### P1-2 发布入口默认捆绑 — fixed

- `-BundlePythonRuntime` 缺省时，脚本用 `$PythonExe -I -c "import sys; print(sys.base_prefix)"` 解析构建解释器的 base installation（当前 m2ac5 venv → Python312）。
- `-SkipPythonRuntime` 仅显式 debug 关闭；现有 `build_sidecar.ps1 -Force` 调用点无需改参。
- 真实 bundle 检查：`apps/desktop/src-tauri/target/core-sidecar/core-sidecar/python/python.exe` **存在**；最小 PATH smoke 输出 `ACTUAL-BUNDLE-SMOKE-OK`；`_hook_interpreter()` 在模拟 frozen 下解析到该路径。
- `build-sidecar-force.log` 显示 PyInstaller 全量重建后仍 `bundle_python_runtime: OK`，exit 0。

### P1-3 AC4 真实脚本 — fixed

证据链现在包含真实脚本路径：

- `build-sidecar-incremental.log`：真实 bundle 初期无 `python/python.exe` → 增量复制后存在，exit 0；
- `build-sidecar-force.log`：`-Force -SkipWeights` 全量重建 → 复制 + smoke，exit 0；
- `real-bundle-verify.log`：真实 bundle 的 `real-bundle-frozen-resolution-ok` / `real-bundle-hook-interpreter-ok` / `real-bundle-sandbox-hook-ok`；
- `build-sidecar-incremental-2.log`：幂等复跑通过；
- `bundled-runtime-verify.log`：helper 独立最小 PATH smoke + frozen + AppContainer；
- `build-ps1-parse.log`：4 个脚本 PS-PARSE-OK。

## 2. 独立验证

| 检查 | 结果 |
|---|---|
| 定向 pytest（packaged+sandbox+runtime） | **46 passed** |
| 全量 pytest（交付日志） | **2672 passed / 9 skipped / 3 既有失败** |
| `check.ps1` | PASS（4 warnings：STATUS/REBASELINE 预算、2 非终态） |
| 实际 bundle | `python/python.exe` 存在；`ACTUAL-BUNDLE-SMOKE-OK` |
| 增量脚本复跑 | exit 0；`bundle_python_runtime: OK`；目标存在 |
| 实际 frozen 解析 | 返回 `<bundle>/python/python.exe` |
| 真实 bundle AppContainer Hook | `real-bundle-sandbox-hook-ok` |

## 3. P2 / P3 findings

1. **STATUS 仍写 r1**：`doc/STATUS.md:7` 当前 Task 仍“r1 修复待 r2”，实际已 r3；建议改为“r2 修复待 r3/复审中”。属 P2 文档一致性。
2. **Task AC4 文案仍写 `build.ps1`**：Task `:51` 仍“`build.ps1 -BundlePythonRuntime` 复制”，实际执行主体是 `build_sidecar.ps1`；`:32` 也保留旧 `packaging/build.ps1` 描述。建议区分真实 sidecar 与 legacy。
3. **默认解析失败只是 warning**：`build_sidecar.ps1` 中若 `sys.base_prefix` 解析失败或未找到 `python.exe`，当前 `Write-Warning` 后继续，最终可能产出**不带 Python 的 bundle**；默认“自动捆绑”应在非 `-SkipPythonRuntime` 时 throw（fail-closed build），否则应在 Task/Handoff 明确“警告并跳过”。属 P2。
4. **`build-sidecar-force.log` 记录的 HEAD 是 `9e79153a`，不是 r2 修复 commit `cfc737fc`**：日志内容包含 Python bundling，但 HEAD 字段早于修复提交（可能是未提交工作区时录制）。证据 pin 到 `cfc737fc` 时建议注明“工作区改动后录制”或重跑固定 HEAD，以免复核误读。属 P2 证据完整性。
5. **`packaging/build.ps1`（legacy）目标仍是 `$OutputDir/core-sidecar/python`**，不是 Tauri `target/core-sidecar/core-sidecar`；若该脚本仍可能用于交付，需同步修正或明确标注 legacy 不产安装包。属 P2。
6. **实际 Tauri sidecar 没有 `artifact-manifest.sha256` 覆盖**：manifest 逻辑只在 legacy `packaging/build.ps1`；真实 sidecar 由 `build_sidecar.ps1` 构建，没有 sha256 manifest 步骤。若发布要求覆盖随包解释器，应在实际构建路径补 manifest。属 P2。
7. **Handoff 旧段落仍保留**：`:16` 旧“`packaging/build.ps1` 复制到 `core-sidecar/python/`”与 `:38-41` 新说明并存；建议删旧或标废弃。属 P3。
8. **`verify_bundled_python.ps1` 默认 `C:\Python314`**：机器相关；已支持 `-PythonRuntime`，建议 Task/Handoff 给出 CI 用法。属 P3。
9. **未做完整 NSIS/Tauri 安装包 + GUI 内 Hook 冒烟**：Task/Handoff 已如实标注，留给候选 1/发布验证；本轮真实 bundle 级验证可接受。属已知边界。

## 4. 结论

**approved。**

- P1-1/P1-2/P1-3 均已闭环：增量路径真实复制、默认运行时自动解析、真实 bundle 含可启动 Python 并通过 AppContainer Hook；无新 blocker。
- P2 建议 closeout 前顺手修：STATUS r2/r3 文案、Task/Handoff 的 `build.ps1` 旧描述、默认解析失败改为 throw、force 日志 HEAD 说明；其余可留后续。
- 可以 closeout 并进入候选 1（GUI 端到端沙箱冒烟）。**当前 approved。**
