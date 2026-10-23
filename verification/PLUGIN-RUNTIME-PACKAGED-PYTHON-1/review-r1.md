# PLUGIN-RUNTIME-PACKAGED-PYTHON-1 独立 Review r1

- Reviewer：`reviewer-settings-a`（非实现者）
- 审查头：**`9a22f5f8bb00df44fd58ca16c6c971e0546693c8`**
- 实现 commit：**`d8bab54df1e958db2ce743e74d652f8f6e0a0425`**；base：`2b965c1b9`
- 结论：**changes_requested**。`_hook_interpreter` 的 frozen 解析顺序与 fail-closed 语义基本正确，但 **build 工具链接错了产物**：实际 Tauri 打包使用的是 `packaging/m2ac5/build_sidecar.ps1` 生成的 `core-sidecar/core-sidecar`，而本 Task 只改了 legacy QML 的 `packaging/build.ps1`，复制目标 `$OutputDir/core-sidecar/python` 不会进入 Tauri 包；同时只复制 `python.exe` + `DLLs`/`Lib`，缺少 `python3.dll`、`python314.dll`、`vcruntime` 与根目录 `.pyd` 扩展，复制出的解释器实际无法启动。打包能力尚未闭环。

## 1. P1 findings

### P1-1（阻塞）— 复制目标不是实际 Tauri 产物，Python 运行时不会进入安装包

- `packaging/build.ps1` 的 PyInstaller spec 是 `packaging/new_manga.spec`，entry 为 `src/bootstrap/app.py`，输出为 `$OutputDir/NewManga/NewManga.exe`（legacy PySide6 onedir）。
- 实际新架构桌面包由 `packaging/m2ac5/build_sidecar.ps1` 构建：`--distpath apps/desktop/src-tauri/target/core-sidecar`，bundle 为 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar`，Tauri `apps/desktop/src-tauri/tauri.conf.json:31` 将 `target/core-sidecar/core-sidecar` 作为 `resources/core-sidecar` 打包。
- 本 Task 在 `packaging/build.ps1:166` 把运行时复制到 `$OutputDir/core-sidecar/python`——这是 `$OutputDir/NewManga` 的**兄弟目录**，不是 Tauri 资源目录，也不会被 Tauri 安装包携带；`m2ac5/build_sidecar.ps1` 完全未改。
- 结果：即使 `-BundlePythonRuntime` 执行成功，最终安装包中也没有 `python/python.exe`；`_hook_interpreter` 在 frozen 下仍会 fail-closed，打包插件完全不可用。

建议：改 `packaging/m2ac5/build_sidecar.ps1`（或在 Tauri 资源构建链中）把运行时复制到实际 bundle 的 `python/`（例如 `<bundle>/python/python.exe` 或 `_internal/python/`），并由 Tauri 资源机制打包；`packaging/build.ps1` 若要保留，应明确 legacy 用途或删除该参数。

### P1-2（阻塞）— 复制范围不完整，解释器无法启动

`packaging/build.ps1:166-174` 只复制：

- `python.exe`
- `DLLs/`（若存在）
- `Lib/`（若存在）

但本机 Python 3.14 运行时根目录实际包含：

- `python3.dll`
- `python314.dll`
- `vcruntime140.dll` / `vcruntime140_1.dll`
- 根目录的 `_socket.pyd`、`_ssl.pyd`、`_sqlite3.pyd` 等扩展模块

这些都不在复制清单内。独立探针：把 `C:\Python314\python.exe` 单独复制到空目录，在仅 `System32` 的 PATH 下执行，退出码 **`-1073741515`（0xC0000135，DLL not found）**，无法启动。即使不启动，缺少 `_socket.pyd` 也会导致 `network` capability 插件无法 import socket。

建议：复制完整可重定位运行时（至少 `python.exe`、`python3.dll`、`pythonXY.dll`、`vcruntime140*.dll`、根目录 `.pyd`、`DLLs/`、`Lib/`），并在临时目录执行 `python.exe -I -c "import socket, sqlite3, ssl"` 验证；不能只校验 `python.exe` 存在。

### P1-3（阻塞，文档/交付一致性）— AC4 实际没有验证复制，Task/Handoff 却按“复制逻辑完成”交付

- Task AC4 写“`build.ps1 -BundlePythonRuntime` 复制运行时并写记录文件（脚本级测试可用 dry-run/复制临时目录验证）”，但证据只有 `build-ps1-parse.log` 的 **PS-PARSE-OK**，没有执行复制、没有检查目标目录、没有校验运行时能启动。
- Task/Handoff 声明“实际 PyInstaller 产物冒烟留给发布验证”，这本身合理；但当前连**脚本级复制**都没有验证，且 P1-1/P1-2 表明复制逻辑本身不可用，不能按 AC4 通过。

建议：增加真实临时目录复制测试（用 `BundlePythonRuntime=C:\Python314` 或测试 fixture），断言目标 `python/python.exe`、`python3.dll`、`python314.dll`、`vcruntime*`、`DLLs`/`Lib` 均存在，并执行一次最小 import smoke；同时修正目标路径（P1-1）。

## 2. 解析器/fail-closed 核验（通过，不含打包）

`src/infrastructure/plugins/service.py::_hook_interpreter`：

- source 非 frozen → `sys.executable`；
- frozen 下顺序：`NEWMANGA_PLUGIN_PYTHON`（必须是 `is_file()`）→ sidecar 同级 `python.exe/python3.exe/python3` → sidecar 的 `python/python.exe|python3.exe`；
- env 指向不存在路径 → `PluginError("PLUGIN_HOOK_UNAVAILABLE")`，不会静默回退系统 Python；
- 全部缺失 → `PLUGIN_HOOK_UNAVAILABLE`。

6 个 frozen 模拟测试覆盖 source/env 覆盖/env 无效/同级/python 子目录/全缺失，真实分支执行；`service._invoke_sandboxed` 将解析结果传给 `prepare_plugin(interpreter=...)` 与 `run(..., interpreter=...)`，沙箱 ACL 跟着实际解释器走，这一层一致。

## 3. 独立验证

| 检查 | 结果 |
|---|---|
| 定向 pytest（packaged+sandbox+runtime） | **46 passed** |
| 全量 pytest | **2672 passed / 9 skipped / 3 既有失败**（与交付说明一致） |
| `build.ps1` 语法 | `build-ps1-parse.log` 为 PS-PARSE-OK |
| `check.ps1` | PASS（4 warnings：STATUS/REBASELINE 预算、2 非终态） |
| 不完整解释器探针 | 单独复制 `python.exe` 启动 → **`-1073741515`（0xC0000135）** |
| 实际 Tauri 资源 | `tauri.conf.json` 打包 `target/core-sidecar/core-sidecar`；本 Task 目标 `$OutputDir/core-sidecar/python` 不在其中 |

## 4. P2 / P3

1. **STATUS 仍 `in_progress`**：`doc/STATUS.md:7` 与 Task `:4`/Handoff `:7`/TASK_LEDGER `:33` 的 `in_review` 不一致；closeout 前统一。
2. **Task 仍有两个 `## Closeout Record`**（`:54`/`:67`），合并。
3. **`artifact-manifest.sha256` 在复制前生成**：`build.ps1:147` 先生成 manifest，`:160` 才复制 Python 运行时，manifest 不含随包解释器；若以后真的用该脚本，完整性清单会漏项。
4. **复制逻辑在 `try/finally` 之外**：`build.ps1:160` 位于构建收尾之后；复制失败时构建已打印成功信息，可能留下半成品；建议移入构建流程并在失败时清理。
5. **frozen 测试只复制 `python.exe`**：`test_sibling_interpreter_is_found` / `test_bundled_python_directory_is_found` 只把 `sys.executable` 复制到目标，验证的是路径解析而非可启动运行时；P1-2 正说明这两件事不同。
6. **`NEWMANGA_PLUGIN_PYTHON` 未由任何启动器/Rust 代码实际设置**：`plugin-python.txt` 只是建议，`apps/desktop/src-tauri` 没有设置该 env；若依赖 env 优先，应在 Tauri 启动 core_service 时注入；否则必须确保 `python/python.exe` fallback 路径正确（P1-1）。
7. **P3**：`NEWMANGA_PLUGIN_PYTHON` 仅校验 `is_file()`，可指向任意可执行文件；这是显式 override，风险由启动器/环境控制，建议文档标注“仅打包启动器使用，不读取用户可控配置”。

## 5. 结论

**changes_requested。**

- 解析器逻辑（P1-1 原 r1 的 fail-closed）本身正确，但**打包交付没有闭环**：改错构建脚本/目标目录，且运行时复制不完整，实际打包后既不会携带 Python，也无法启动。
- 在修复 P1-1/P1-2 并补一个真实临时目录复制 + 启动 smoke 前，不能 closeout，也不能进入候选 1（GUI 冒烟）。
- 修复建议顺序：先改 `packaging/m2ac5/build_sidecar.ps1` 目标，再补完整运行时复制与启动测试，最后更新 Task/Handoff/STATUS（in_review、单一 Closeout、AC4 证据）。
