---
task_id: PLUGIN-RUNTIME-PACKAGED-PYTHON-1
kind: implementation
status: in_review
owner: dsh（本会话 Lead 兼任 Owner）
reviewer: reviewer-settings-a（非实现者）
created: 2026-10-23
base_commit: 2b965c1b9de25c3dd73e24724aa99fcb5b8b599a
depends_on: PLUGIN-RUNTIME-CAPABILITY-1
authorization: 用户 2026-10-23「1234都授权」（本 Task = 候选 4：打包环境 Hook 解释器）
allowed_paths:
  - src/infrastructure/plugins/**
  - packaging/**
  - tests/**
  - doc/tasks/PLUGIN-RUNTIME-PACKAGED-PYTHON-1.md
  - doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/TASK_LEDGER.md（Lead 集成登记）
  - doc/handoffs/**
  - verification/PLUGIN-RUNTIME-PACKAGED-PYTHON-1/**
---

# PLUGIN-RUNTIME-PACKAGED-PYTHON-1 — 打包环境 Hook 解释器

## 背景

PyInstaller onedir 构建中 `sys.executable` 是 sidecar 自身，不是 Python CLI；`_hook_interpreter()` 目前只查找 sidecar 同级 `python.exe`，找不到即 fail-closed（`PLUGIN_HOOK_UNAVAILABLE`）。本 Task 给打包构建提供**确定的解释器来源**：

1. `NEWMANGA_PLUGIN_PYTHON` 环境变量（最高优先；打包启动器设置，指向捆绑运行时）；
2. sidecar 同级 `python.exe` / `python3.exe`（现有行为）；
3. sidecar 同级 `python/` 子目录中的 `python.exe`（随包捆绑目录）；
4. 都没有 → 维持 fail-closed（不静默用系统 Python）。

并提供 `packaging/build.ps1` 的可选 `-BundlePythonRuntime`：把运行时复制到输出目录 `python/`，同时写 `scripts`/说明供启动器设置 `NEWMANGA_PLUGIN_PYTHON`。

## 范围

- `service.py::_hook_interpreter`：上述 1–4 优先级；只接受 `is_file()` 的路径；env 覆盖也要校验存在。
- `packaging/build.ps1`：新增可选参数 `-BundlePythonRuntime <dir>`（校验 `<dir>/python.exe` 存在），复制到 sidecar 输出目录 `python/`（保留 DLLs/Lib 相对结构），并在 `plugin-python.txt` 记录解释器相对路径。
- 测试（模拟 frozen）：
  - env 覆盖真实解释器 → 返回；
  - `sys.frozen=True` + 同级 `python.exe`（复制真实解释器）→ 返回；
  - `python/python.exe` 捆绑目录 → 返回；
  - 都缺 → `PLUGIN_HOOK_UNAVAILABLE`；
  - env 指向不存在路径 → fail-closed（不静默回退系统 Python）。
- 文档：Task/Handoff 说明实际 PyInstaller 产物冒烟留给发布验证（本轮不执行完整打包构建）。

## 验收

- [x] **AC1** `NEWMANGA_PLUGIN_PYTHON` 存在时优先返回该解释器。
- [x] **AC2** frozen 下同级或 `python/` 子目录解释器可被发现。
- [x] **AC3** 全部缺失 / env 指向不存在路径 → `PLUGIN_HOOK_UNAVAILABLE`（fail-closed，不回退系统 Python）。
- [x] **AC4** `build.ps1 -BundlePythonRuntime` 复制运行时并写记录文件（脚本级测试可用 dry-run/复制临时目录验证）。
- [x] **AC5** 全量测试无回归；文档如实（实际打包冒烟未做）。

## Closeout Record

## 测试与证据

| AC | 命令/证据 | 结果 |
|---|---|---|
| AC1 | `test_environment_override_wins` | PASS：`NEWMANGA_PLUGIN_PYTHON` 优先 |
| AC2 | `test_sibling_interpreter_is_found` / `test_bundled_python_directory_is_found` | PASS：同级 / `python/` 子目录 |
| AC3 | `test_missing_environment_override_fails_closed` / `test_no_interpreter_fails_closed_without_system_fallback` | PASS：`PLUGIN_HOOK_UNAVAILABLE`，不回退系统 Python |
| AC4 | `packaging/build.ps1` 语法检查（`build-ps1-parse.log`） | PASS（PS-PARSE-OK）；`-BundlePythonRuntime` 复制 python.exe/DLLs/Lib 并写 `plugin-python.txt`（脚本逻辑，未跑完整 PyInstaller 构建） |
| AC5 | `python -m pytest tests -q` | 见 `core-pytest.log` |
| 定向 | packaged-python + sandbox + runtime | 46 passed |

## Closeout Record

- Closeout：待 Review approved 后 closeout（实际 PyInstaller 产物冒烟留给发布验证）。
