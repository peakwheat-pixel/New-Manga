# TASK-004 Windows / PySide6 / 打包隔离实验

Owner：ZCode（TASK-004，分支 `agent/zcode/TASK-004-windows-packaging`）。
本目录只做隔离实验，不写生产 `src/`。详细结果与结论见
[doc/research/TASK-004.md](../../doc/research/TASK-004.md)；
原始命令日志见 [verification/TASK-004](../../verification/TASK-004)。

## 内容

| 文件 | 用途 |
|---|---|
| `qml_min/main.py` | 最小 QML 冒烟程序：启动真实 Qt Quick 窗口 → 1.5 s 后自动关闭，stdout 输出 JSON（Qt 版本、platform 插件、qwindows.dll、窗口状态）。开发环境与 PyInstaller 打包两种模式通用。 |
| `qml_min/main.qml` | 最小 QML 窗口（`QtQuick.Controls` + `Window` + `Label`）。 |
| `check_qt_files.py` | 检查 PySide6 安装或 PyInstaller onedir 产物中 Qt6Core/Gui/Qml/Quick DLL、`platforms/qwindows.dll`、`platforms/qoffscreen.dll` 与 QtQuick QML 模块目录是否齐全；缺失即 FAIL。 |
| `test_smoke.py` | pytest 冒烟：PySide6 导入、Qt 基本信息、offscreen 平台下 QML 引擎加载。 |

## 复现（本任务实际使用的隔离方式）

虚拟环境与构建产物全部放在仓库外临时目录 `%TEMP%/task004-zcode/`，
与 TASK-003（DeepSeek）的 worktree、venv、缓存完全隔离：

```bash
TMPROOT="$(cygpath -u "$LOCALAPPDATA")/Temp/task004-zcode"   # 实际 /tmp/task004-zcode
py -3.12 -m venv "$TMPROOT/venv-py312"
"$TMPROOT/venv-py312/Scripts/python.exe" -m pip install PySide6 pytest pyinstaller
py -3.14 -m venv "$TMPROOT/venv-py314"
"$TMPROOT/venv-py314/Scripts/python.exe" -m pip install PySide6 pytest
```

实际安装、运行、构建命令与退出码逐条记录在 `verification/TASK-004/logs/`。

### QML 冒烟（开发模式）

```bash
"$TMPROOT/venv-py312/Scripts/python.exe" experiments/TASK-004/qml_min/main.py
```

预期：stdout 末行 JSON `"result": "PASS"`，退出码 0。

### pytest 冒烟

```bash
"$TMPROOT/venv-py312/Scripts/python.exe" -m pytest experiments/TASK-004/test_smoke.py -v
```

### PyInstaller onedir 构建与启动

```bash
cd "$TMPROOT/build-area"
"$TMPROOT/venv-py312/Scripts/pyinstaller.exe" --noconfirm --onedir \
  --name task004_smoke --add-data "main.qml;." main.py
# 启动（模拟无开发 PATH）：
cmd //c "set PATH=C:\Windows\system32;C:\Windows && dist\task004_smoke\task004_smoke.exe"
```

### Qt 资产检查

```bash
python experiments/TASK-004/check_qt_files.py <venv的site-packages或dist目录> [--layout pyside6|onedir]
```
