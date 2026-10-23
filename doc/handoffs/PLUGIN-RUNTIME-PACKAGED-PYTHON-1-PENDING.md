---
task_id: PLUGIN-RUNTIME-PACKAGED-PYTHON-1
author: dsh（Lead / Owner）
recipient: reviewer-settings-a（独立 Review）
base_commit: 2b965c1b9de25c3dd73e24724aa99fcb5b8b599a
delivery_head: PLACEHOLDER_PKG_HEAD
status: in_review
authorization: 用户 2026-10-23「1234都授权」
---

# Handoff — PLUGIN-RUNTIME-PACKAGED-PYTHON-1（打包环境 Hook 解释器）

## 1. 交付摘要

- `service.py::_hook_interpreter`：packaged 解析顺序 → `NEWMANGA_PLUGIN_PYTHON`（存在且为文件）→ sidecar 同级 `python.exe/python3.exe/python3` → sidecar 同级 `python/python.exe`；全部缺失或 env 路径无效 → `PLUGIN_HOOK_UNAVAILABLE`（**不回退系统 Python**）。source 运行仍返回 `sys.executable`。
- `packaging/build.ps1`：可选 `-BundlePythonRuntime <dir>`（校验 `python.exe`），复制 `python.exe` + `DLLs`/`Lib` 到输出 `core-sidecar/python/`，写 `plugin-python.txt` 记录解释器与启动器建议。
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
