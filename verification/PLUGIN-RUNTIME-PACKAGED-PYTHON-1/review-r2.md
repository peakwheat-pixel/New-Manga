# PLUGIN-RUNTIME-PACKAGED-PYTHON-1 独立 Review r2（r1 修复复核）

- Reviewer：`reviewer-settings-a`（非实现者）
- 审查头：**`9e79153aec9d28fa6a9d8cfb572afc7a15943b01`**
- 实现链：`2b965c1b`（base）→ `d8bab54d` → `9a22f5f8` → `bc72d883`（r1 修复）→ `df057c78` → `9e79153a`
- 结论：**changes_requested**。完整运行时复制（P1-2）和 helper/verify 证据（P1-3 的局部）已改善，但**真实打包路径仍未闭环**：`build_sidecar.ps1` 的增量短路会在复制 Python 之前 `exit 0`，实际 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar` 仍没有 `python/python.exe`；现有所有调用点也都没有传 `-BundlePythonRuntime`。`bundled-runtime-verify.log` 只验证了 helper 的临时目录复制，没有验证真实 build_sidecar 路径。

## 1. P1 findings

### P1-1（阻塞）— `build_sidecar.ps1` 增量路径在复制 Python 之前 exit 0

`packaging/m2ac5/build_sidecar.ps1` 的早期短路仍存在：

```powershell
$existingBundle = Join-Path $repoRoot "apps/desktop/src-tauri/target/core-sidecar/core-sidecar"
if (-not $Force -and (Test-Path -LiteralPath $existingBundle -PathType Container)) {
    Write-Host "build_sidecar: target exists, skipping (use -Force to rebuild)"
    ...
    exit 0
}
```

新增的 `Copy-PluginPythonRuntime` 调用在文件末尾（PyInstaller 构建、完整性检查、weights 之后），因此**任何已存在 bundle 的常规增量构建都不会执行 Python 复制**。独立复现：

```text
BEFORE: False
build_sidecar: target exists, skipping (use -Force to rebuild)
EXIT=0
AFTER: False
```

即使用户显式传 `-BundlePythonRuntime C:\Python314`，只要没加 `-Force`，脚本仍退出 0 且目标 bundle 没有 `python/python.exe`。这与“真实产物已注入 Python”的交付结论冲突。

建议：把 `Copy-PluginPythonRuntime` 移到增量短路**之前**（或在短路分支内执行），并让“是否已捆绑”成为短路条件的一部分；增量/全量两条路径都必须覆盖。

### P1-2（阻塞）— 现有打包调用点没有传 `-BundlePythonRuntime`，实际安装包不会带 Python

仓库里现有 `build_sidecar.ps1` 调用点：

- `verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/build_sidecar_logged.ps1`：`build_sidecar.ps1 -Force`（无 `-BundlePythonRuntime`）
- `verification/P19/rebuild-and-verify.ps1`：`build_sidecar.ps1 -Force`（无参数）
- `packaging/m2ac5/build_sidecar.ps1` 的 usage 注释也未加入该参数

`build_sidecar.ps1` 的 `$BundlePythonRuntime` 默认为空；不传就完全不复制。因此即使 `-Force` 全量构建，现有打包命令也不会产生 `<bundle>/python/`。真实 bundle 当前检查结果：

```text
apps/desktop/src-tauri/target/core-sidecar/core-sidecar/python/python.exe
→ False
```

`verify_bundled_python.ps1` 复制到临时 `OutDir`（`G:\CODEX\New Manga.workspace\tmp\pkg-python-verify2`），不是实际 Tauri bundle；它证明 helper 可用，不证明真实 build 产物已带 Python。需要把 `-BundlePythonRuntime` 接入实际发布/打包入口（或把 bundle 目录作为默认运行时来源），否则安装包仍会 frozen fail-closed。

### P1-3（阻塞，证据链）— AC4 验证没有走 `build_sidecar.ps1`

`bundled-runtime-verify.log` 证明：

- `Copy-PluginPythonRuntime` 可复制并 smoke；
- frozen `_hook_interpreter` 解析到临时 `<sidecar>/python/python.exe`；
- 该临时解释器可在真实 AppContainer 执行 hook。

但它**没有调用 `packaging/m2ac5/build_sidecar.ps1`**，也没有验证“真实 bundle + `-BundlePythonRuntime` + 增量/`-Force`”路径。Task AC4 写“`build.ps1 -BundlePythonRuntime` 复制”，实际证据是 helper 临时目录，不能证明 P1-1/P1-2 的 build 路径。建议增加一个测试/脚本：在临时 `core-sidecar` bundle 上调用 `build_sidecar.ps1 -BundlePythonRuntime ...`（含已存在 bundle 的增量分支），然后检查 `<bundle>/python/python.exe` 与 smoke。

## 2. r1 已闭环部分

- **完整运行时复制**：`packaging/bundle_python_runtime.ps1` 现在复制 `python.exe`、`python3*.dll`、`vcruntime*.dll`、根 `*.pyd`、`DLLs/`、`Lib/`（排除 site-packages）；最小 PATH smoke import `socket/ssl/sqlite3/json/hashlib` 通过。独立日志 `bundled-runtime-verify.log` 的 `bundled-runtime-ok` 与 `bundled-sandbox-hook-ok` 真实执行。
- **frozen 解析**：`_hook_interpreter` 顺序与 fail-closed 不变；verify 的 `frozen-resolution-ok` 指向临时 `<sidecar>/python/python.exe`。
- **build.ps1（legacy）**：已改用共享 helper，复制在 `artifact-manifest.sha256` 之前；但目标 `$OutputDir/core-sidecar` 仍不是实际 Tauri bundle（见 P2-2）。

## 3. 独立验证

| 检查 | 结果 |
|---|---|
| 定向 pytest（packaged+sandbox+runtime） | **46 passed** |
| 全量 pytest | **2672 passed / 9 skipped / 3 既有失败**（与交付说明一致） |
| `check.ps1` | PASS（4 warnings：STATUS/REBASELINE 预算、2 非终态） |
| `bundled-runtime-verify.log` | exit 0；helper 临时复制 + 最小 PATH smoke + frozen 解析 + AppContainer Hook 通过 |
| 实际 Tauri bundle | `<bundle>/python/python.exe` = **False** |
| 增量路径探针 | `build_sidecar.ps1 -SkipWeights -BundlePythonRuntime C:\Python314` 无 `-Force` → exit 0、`target exists, skipping`、复制前后均 False |

## 4. P2 / P3

1. **Task 文案仍混用旧路径**：Task `:32` 仍写“`packaging/build.ps1` 复制到输出目录 `python/`”；`:51` AC4 仍写“`build.ps1 -BundlePythonRuntime`”，实际主要实现是 `build_sidecar.ps1`。建议区分 legacy 与真实 sidecar。
2. **`packaging/build.ps1`（legacy）目标仍是 `$OutputDir/core-sidecar/python`**，不是 Tauri 的 `target/core-sidecar/core-sidecar`；若这个脚本仍可能用于交付，应同步修正或明确标注 legacy 不产安装包。
3. **Handoff 旧段落仍保留**：`:16` 仍说 `packaging/build.ps1` 复制到 `core-sidecar/python/`；虽然 `:38-41` 已补 r1 修复说明，但新旧两套描述并存，容易误读。
4. **`verify_bundled_python.ps1` 默认 `C:\Python314`**：机器相关；证据日志已固定路径，但应允许 CI 指定；已提供 `-PythonRuntime` 参数。
5. **P3**：`Copy-PluginPythonRuntime` 排除 `Lib/site-packages` 的边界已在注释说明；若未来插件依赖第三方包需显式 allowlist。`NEWMANGA_PLUGIN_PYTHON` 仍是显式 override，注释已标“仅打包启动器使用”。

## 5. 结论

**changes_requested。**

- P1-2（完整运行时）和 helper/verify 本身已修好，但 **P1-1/P1-2 的真实 build 路径仍缺失**：增量短路跳过复制，现有打包调用点不传参数，实际 Tauri bundle 没有 Python；P1-3 验证也未覆盖 `build_sidecar.ps1`。
- 修复建议顺序：
  1. 把 `Copy-PluginPythonRuntime` 放到增量短路前/短路分支内；
  2. 在实际发布打包入口（或 build_sidecar 默认路径）传入/使用 `-BundlePythonRuntime`；
  3. 用**真实或临时 `core-sidecar` bundle** 调用 `build_sidecar.ps1` 做增量+`-Force` 两种路径验证，检查 `python/python.exe` 与 smoke；
  4. 更新 Task/Handoff/证据，再复审 r3。
- 在 P1-1/P1-2 修复前，不能 closeout，也不能进入候选 1（GUI 冒烟）。
