# TASK-004 研究报告：Windows 运行环境与打包路线验证

| 项 | 值 |
|---|---|
| Task | [TASK-004](../tasks/TASK-004.md)（kind: experiment） |
| Owner / Reviewer | ZCode / DeepSeek Harness（非作者独立 Review） |
| 执行日期 | 2026-09-14（Asia/Shanghai） |
| 分支 / worktree | `agent/zcode/TASK-004-windows-packaging` / `G:/CODEX/New Manga.worktrees/TASK-004-zcode` |
| 实验基线 | starting_head `27b3948`，状态提交 `7c80110`（in_progress），内容 head 见 Handoff |
| 性质声明 | 本文全部为 As-Is 实验结果 + Proposal 建议；数值/组合未经 Codex 审核前不构成项目选型 |
| 隔离声明 | 实验仅使用仓库外临时目录 `%LOCALAPPDATA%\Temp\task004-zcode`（Git Bash `/tmp/task004-zcode`）；与 TASK-003（DeepSeek）的 worktree、venv、缓存、输出零共享 |

## 1. 目的与输入

- 回答 [G18](../10_CURRENT_STATE_AND_GAPS.md)：D02 目标技术未固定兼容版本、打包/CI 不存在；先验证 Windows/QML/可选依赖/打包最小路线，再锁依赖。
- 依据：[D02 §1 目标技术栈](../02_TECHNICAL_ARCHITECTURE_.md)（PySide6 + Qt Quick/QML、pytest、PyInstaller onedir、ML 依赖可选）、[D02 §13 运行时拓扑](../02_TECHNICAL_ARCHITECTURE_.md)（单进程桌面、无需本地 HTTP 服务）、[D07 §2 目标平台](../07_NON_FUNCTIONAL_REQUIREMENTS.md)（Windows x64、Win11 主力 / Win10 best effort、非管理员）、[D07 §81~85](../07_NON_FUNCTIONAL_REQUIREMENTS.md)（onedir 优先、干净 Windows 验证、可选依赖不强装、模型缓存独立）、[D07 §107 硬件档位](../07_NON_FUNCTIONAL_REQUIREMENTS.md)。
- 边界：本 Task 不创建生产工程骨架（TASK-005）、不写 `src/`、不安装任何重型 AI 模型。

## 2. 实验环境（As-Is，2026-09-14）

| 项 | 值 |
|---|---|
| OS | Microsoft Windows 11 专业版，Version 10.0.26200（Build 26200），64 位 |
| CPU / RAM | AMD Ryzen 9 7950X3D 16-Core / 33,981,210,624 bytes（32 GB） |
| 架构 | AMD64（Qt `QSysInfo.currentCpuArchitecture()` = `x86_64`，见 pytest 证据） |
| 系统 Python | 3.14.6（`C:\Python314`，另装有 3.10/3.11/3.12/3.14，py launcher 管理） |
| 隔离 venv | `/tmp/task004-zcode/venv-py312`（3.12.3）、`venv-py314`（3.14.0）、`venv-py312-ess`（3.12.3，Essentials-only） |
| pip 源 | 清华镜像 `https://pypi.tuna.tsinghua.edu.cn/simple`（仅分发渠道；wheel 为 PyPI 官方构建） |

按 G18 与 TASK-004「不得把当前机器 Python 版本直接视为项目选型」的要求，系统 Python 3.14.6 仅作为候选之一，选型见 §5。

## 3. 结果总表

结果枚举：PASS / FAIL / BLOCKED / NOT_RUN / N/A。

| # | 实验 | 环境 | 命令（摘要） | 退出码 | 结果 | 证据 |
|---|---|---|---|---|---|---|
| E1 | 依赖安装：PySide6 6.11.2 + pytest 9.1.1 + PyInstaller 6.22.3 | py312 venv | `pip install` | 0 | PASS | `logs/pip312.log` |
| E2 | 依赖安装：PySide6 6.11.2 + pytest 9.1.1 | py314 venv | `pip install` | 0 | PASS | 后台任务日志（freeze 见 §4.1） |
| E3 | QML 真实窗口启动→1.5 s→关闭 | py312 | `qml_min/main.py` | 0 | PASS | `logs/qml_smoke.log` |
| E4 | QML 真实窗口启动→1.5 s→关闭 | py314 | `qml_min/main.py` | 0 | PASS | `logs/qml_smoke.log` |
| E5 | venv 内 Qt DLL/plugin/QML 模块完整性 | py312 + py314 | `check_qt_files.py --layout pyside6` | 0 | PASS | `logs/qt_assets_pytest.log` |
| E6 | pytest 冒烟（3 项） | py312 / py314 | `pytest test_smoke.py -v` | 0 / 0 | PASS（各 3 passed） | `logs/qt_assets_pytest.log` |
| E7 | PyInstaller onedir 构建 | py312 | `pyinstaller --onedir --add-data main.qml` | 0 | PASS | `logs/pyinstaller_build.log` |
| E8 | onedir 产物 Qt 资产完整性 | 产物目录 | `check_qt_files.py --layout onedir` | 0 | PASS（missing=[]） | `logs/onedir_run.log` |
| E9 | onedir 启动（正常环境） | 产物 exe | `task004_smoke.exe` | 0 | PASS（frozen=true，窗口 visible） | `logs/onedir_run.log` |
| E10 | onedir 启动（清除开发 PATH 模拟） | 产物 exe | `cmd /c set PATH=%SystemRoot%\system32;%SystemRoot%` | 0 | PASS（同上） | `logs/onedir_run.log` |
| E11 | Essentials-only：`PySide6_Essentials`+pytest 支撑 QML | py312-ess venv | 同 E3/E6 | 0 / 0 | PASS | `logs/essentials_only.log` |
| E12 | 干净 Windows 环境验证（另一台机器/VM，无开发工具；D07 §82） | — | — | — | **BLOCKED** | §4.4 |
| E13 | PyInstaller × Python 3.14 组合构建 | — | — | — | NOT_RUN（主推组合已覆盖；升级前需重验） | — |
| E14 | 打包体积裁剪（excludes / Essentials 打包） | — | — | — | NOT_RUN（建议见 §5.4） | — |
| E15 | Win10 兼容矩阵验证（D07 §2.2 best effort） | — | — | — | NOT_RUN（本机仅 Win11） | — |
| E16 | 安装器 / 便携分发 / 自动更新 | — | — | — | NOT_RUN（超出本 Task 最小验证范围） | — |
| E17 | 内嵌自定义字体打包 | — | — | — | NOT_RUN（建议见 §5.3） | — |
| E18 | D07 §3 冷启动 P95 ≤ 3 s 等性能指标 | — | — | — | N/A（无生产应用；目标值仍待 Benchmark） | — |

无 FAIL 项。

## 4. 关键观察（As-Is）

### 4.1 版本矩阵实测

```text
Python 3.12.3 + PySide6 6.11.2 + shiboken6 6.11.2 + pytest 9.1.1 + PyInstaller 6.22.3（hooks-contrib 2026.7）
Python 3.14.0 + PySide6 6.11.2 + shiboken6 6.11.2 + pytest 9.1.1
Python 3.12.3 + PySide6_Essentials 6.11.2 + pytest 9.1.1
```

两组 Python 版本对 PySide6 6.11.2 均有官方 wheel 且全部实验通过。完整 freeze 见
`verification/TASK-004/logs/pip312.log`、`logs/essentials_only.log`。

### 4.2 QML 启动/关闭与插件加载（E3/E4）

`qml_min/main.py` 以默认 `windows` 平台插件启动真实 Qt Quick 窗口：

```json
{"qt_version": "6.11.2", "platform_name": "windows", "qwindows_dll_present": true,
 "window_title": "TASK-004 QML Smoke", "window_visible": true, "result": "PASS"}
```

- `QtQuick.Controls` 的 `Window`/`Label` 正常加载，QML 引擎产生 root object；
- 窗口 `visible=true`，`QTimer.singleShot(1500, close)` 后 `app.quit()`，退出码 0；
- 开发环境下插件与 QML import 路径由 PySide6 包内位置自动解析（`site-packages/PySide6/plugins`、`.../PySide6/qml`），无需手动 `QT_PLUGIN_PATH`。

### 4.3 onedir 打包（E7~E10）

- 构建命令：`pyinstaller --noconfirm --onedir --name task004_smoke --add-data "main.qml;." main.py`，约 28 s 完成；
- 布局为 PyInstaller 6.x 的 `task004_smoke.exe + _internal/`；QML 数据文件落在 `_internal/main.qml`，脚本内 `sys._MEIPASS` 定位成功；
- 产物 Qt 资产完整：`Qt6Core/Gui/Qml/Quick/QuickControls2.dll`、`platforms/qwindows.dll`、`platforms/qoffscreen.dll`、`QtQuick/QtQuick.Controls/QtQuick.Window` 模块全部在位（`_internal/PySide6/` 下），运行时由 PyInstaller hook 自动定位，无需手动环境变量；
- 体积 397 MB / 2,824 文件（PySide6 meta 全量，含 Addons 的 QtWebEngine/3D 等未用模块）；
- 「干净 PATH」模拟：`PATH` 仅剩 `%SystemRoot%\system32;%SystemRoot%` 时仍启动成功且退出码 0，说明包内自带全部所需 DLL 与 CRT，不依赖开发机 Python/venv/开发工具链。

### 4.4 BLOCKED：干净 Windows 环境（E12）

D07 §82 要求发布包在**干净 Windows 环境**验证；TASK-004 AC 亦要求「打包 onedir 在可取得的干净 Windows 环境验证，否则明确 BLOCKED」。当前无法取得另一台机器或还原态 VM：

- E10 的 PATH 清除仅模拟「无开发机 PATH/venv」，运行仍在同一台开发机的系统注册表与系统 DLL 环境下，**不能替代**干净环境验证；
- **结果：BLOCKED。解除条件：用户或 Codex 提供干净 Windows 11（及 best-effort Windows 10）虚拟机或物理机；届时用本报告 §5.4 的固定命令重跑 E9/E10 并补 D07 §106 清单。**

## 5. 建议（Proposal，供 Codex 审核后供工程使用）

### 5.1 版本锁定建议

- **主推组合（TASK-005 工程基线）**：Python 3.12（3.12.3 实测；正式锁定时取最新 3.12.x micro）+ PySide6 6.11.2 + pytest 9.1.1 + PyInstaller 6.22.3（dev/打包依赖）。
- 选 3.12 为主锚的理由：项目目标依赖（Pillow、OpenCV、SQLite 生态）对 3.12 的 wheel 成熟度最高；3.14 虽已实测可用（E2/E4 全 PASS），但生态覆盖仍是风险面，列为观察项，切换需重跑本文件全部实验。
- 锁定方式建议：工程建立时生成 `requirements-lock.txt`（`pip freeze` 全量 pin + `--only-binary :all:`），PySide6 只锁 `==` 不用 `~=`，避免 Qt 小版本漂移引入行为变化；PyInstaller/hooks-contrib 随锁文件一起冻结。
- 升级规则建议：任何 PySide6/PyInstaller 大版本变更必须重跑本报告 E3~E10（脚本已入库可复用）。

### 5.2 Core / 可选 ML 依赖分离

- **Core 运行依赖（已验证最小集，E11）**：`PySide6_Essentials`（含 shiboken6；QtQuick/Controls/QML 齐全）即可支撑四页 UI 的技术底座；`PySide6` meta 会额外拉入 `PySide6_Addons`（QtWebEngine、3D 等），四页 UI 无需。
- **dev 依赖**：pytest、PyInstaller（+ hooks-contrib）。
- **可选 ML 依赖**：torch / ONNX Runtime / transformers / manga-ocr / PaddleOCR 等一律作为各 Provider 的 extras（如 `newmanga[ocr-manga]`），由 Provider 延迟 import，缺失时仅禁用该 Provider（D02 §1、D07 §83）；本 Task 未安装任何此类依赖，Core 启动完全不受影响（E3 即证据）。
- 架构守卫在 TASK-005 落地时按 D02 §14 执行（`domain/` 不得 import PySide6/sqlite3/torch 等）。

### 5.3 字体 / Qt 资源 / 运行路径

- 字体：Windows 系统自带字体（微软雅黑等）可满足默认 UI 与中文渲染；如需统一内嵌字体（含日文假名/韩文），以 `--add-data` 随包分发并在启动时 `QFontDatabase.addApplicationFont`（E17 未实验，列为建议而非结论）。
- Qt 资源：platforms/qwindows.dll、QtQuick QML 模块由 PyInstaller hook 自动收集（E8 已验证）；自研 QML/资源统一走 `_MEIPASS` 数据文件或后续 qrc，均与已验证路径兼容。
- 运行路径：exe 所在目录按只读对待（Program Files 场景不可写）；用户数据目录选择（`%APPDATA%`/`%LOCALAPPDATA%`）属工程骨架决策，留给 TASK-005/006；本实验程序零持久化。

### 5.4 打包命令基线（已验证）

```bash
pyinstaller --noconfirm --onedir --name task004_smoke --add-data "main.qml;." main.py
# 启动验证（含无开发 PATH 模拟）：
task004_smoke.exe
cmd /c "set \"PATH=C:\Windows\system32;C:\Windows\" && task004_smoke.exe"
```

体积优化（E14，未验证）：`--exclude-module` 裁掉未用 Qt 模块、直接基于 `PySide6_Essentials` 环境打包、排除 QtWebEngine/3D/Translations；预期显著低于 397 MB。工程化时改用 `.spec` 文件（TASK-005）。

## 6. 复现指引

见 [experiments/TASK-004/README.md](../../experiments/TASK-004/README.md)：隔离 venv 创建、四个实验入口、Qt 资产检查与打包命令；全部原始命令日志在 [verification/TASK-004/logs/](../../verification/TASK-004/logs)。

## 7. 遗留与风险

1. E12 干净环境 BLOCKED（§4.4），发布 Gate（D07 §82/§106）前必须解除。
2. 本机 Python 3.12.3 为 micro 版本，正式锁版时随 3.12.x 最新 micro 重验。
3. PyInstaller hook 与 PySide6 6.11.2 的兼容性已随本次组合验证；任一侧升级必须重跑 E7~E10。
4. 体积与启动耗时均未优化、未测（E14/E18），不代表发布形态。
5. 本报告全部为实验结论，不修改生产 `src/`、根依赖或 Schema；采纳与否由 Codex 在 TASK-005 范围内决策。
