---
task_id: PLUGIN-RUNTIME-PACKAGED-PYTHON-1
author: dsh（Lead / Owner）
recipient: reviewer-settings-a（独立 Review）
base_commit: 2b965c1b9de25c3dd73e24724aa99fcb5b8b599a
delivery_head: fdc0dfa3dbcc17f9028ff0cfbb79b67b617de583
status: done
authorization: 用户 2026-10-23「1234都授权」
---

# Handoff — PLUGIN-RUNTIME-PACKAGED-PYTHON-1（打包环境 Hook 解释器）

## 1. 交付摘要

- `service.py::_hook_interpreter`：packaged 解析顺序 → `NEWMANGA_PLUGIN_PYTHON`（存在且为文件）→ sidecar 同级 `python.exe/python3.exe/python3` → sidecar 同级 `python/python.exe`；全部缺失或 env 路径无效 → `PLUGIN_HOOK_UNAVAILABLE`（**不回退系统 Python**）。source 运行仍返回 `sys.executable`。
- 真实交付路径 `packaging/m2ac5/build_sidecar.ps1`：**默认**把完整运行时复制到 `<bundle>/python/`（见 §5 的 r2 修复）；`packaging/build.ps1` 仅为 legacy PySide6 构建，复用同一 helper。
- 测试：frozen 模拟六例（source / env 覆盖 / env 缺失 / 同级 / python 子目录 / 全缺失）。

## 2. 验证

| 命令 | 结果 |
|---|---|
| 定向 pytest（packaged-python + sandbox + runtime） | **46 passed** |
| 全量 pytest | `core-pytest.log` |
| `packaging/build.ps1` 语法 | PS-PARSE-OK |

## 3. 已知边界（如实）

- 未执行完整 PyInstaller 构建/产物冒烟（需要打包环境）；`-BundlePythonRuntime` 仅脚本逻辑 + 语法校验。
- 打包产物的 GUI 端到端验证留给候选 1（GUI 冒烟）/发布验证。

## 4. 推荐下一步

Review approved 后 closeout，进入候选 1（GUI 端到端沙箱冒烟）。

## 5. Review r1 处置（changes_requested）

- **P1-1 真实产物**：改 `packaging/m2ac5/build_sidecar.ps1`（Tauri 打包的 sidecar 目录）。r2 追加修复：**增量短路路径也执行复制**（bundle 已有但缺 `python/python.exe` 时不再被 `target exists, skipping` 跳过）；**默认自动捆绑**（缺省从构建解释器 `sys.base_prefix` 解析完整运行时，`-SkipPythonRuntime` 仅 debug）；`packaging/build.ps1`（legacy）复用同一 helper 且复制在 `artifact-manifest.sha256` 之前。
- **P1-2 完整运行时**：共享 helper `packaging/bundle_python_runtime.ps1` 复制 `python.exe`、`python3*.dll`、`vcruntime*.dll`、根 `*.pyd`、`DLLs/`、`Lib/`（排除 `site-packages`/`test`/`idlelib`/`tkinter`/`turtledemo`），复制后立即用最小 PATH 跑 `python.exe -I -c "import socket, ssl, sqlite3, json, hashlib"`，失败即 throw（fail-closed）。
- **P1-3 AC4 实证**：真实 `build_sidecar.ps1` 增量路径（`build-sidecar-incremental.log`：bundle 无 python → 复制后存在，exit 0）+ PyInstaller -Force 全量路径（`build-sidecar-force.log`：重建后 `python/python.exe` 存在，exit 0）+ 真实 bundle 解析/沙箱 Hook（`real-bundle-verify.log`：`real-bundle-sandbox-hook-ok`）+ 幂等复跑（`build-sidecar-incremental-2.log`）；另有 helper 独立验证 `bundled-runtime-verify.log`。
- **P2**：STATUS 统一 `in_review`；Task 两个 Closeout 标题合并；artifact manifest 覆盖随包解释器；复制在构建收尾前；`_hook_interpreter` 注释标注 env 仅打包启动器使用（P3）。
- **仍剩余**：完整 PyInstaller 产物冒烟（需要打包环境）与 GUI 端到端，留给候选 1/发布验证。

## 6. Closeout（2026-10-23）

- Review r3 **approved**（`verification/PLUGIN-RUNTIME-PACKAGED-PYTHON-1/review-r3.md`，审查头 `a1f05450`）。
- P2 已修：STATUS 更新、Task legacy 区分、默认运行时解析失败改为 throw（fail-closed）、force 日志注明工作区录制、真实 sidecar 侧 `plugin-python.sha256`（1009 files）随包、Handoff 旧描述清理、verify 脚本 CI 传参说明。
- 已知边界：NSIS/Tauri 安装包与 GUI 内 Hook 冒烟留给候选 1（GUI 端到端）。
