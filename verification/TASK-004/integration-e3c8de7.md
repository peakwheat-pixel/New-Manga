# TASK-004 集成验证证据

- 被测主线：`e3c8de7ebdf47e38d2f9b298bb1a938948b442bf`
- reviewed head：`181a356cdb91725aa63961d123605ac179074286`
- integration commit：`a501372dd09086e93f86d41937c43cb41e41e563`
- 环境：Windows 11 Pro `10.0.26200` AMD64；PowerShell `7.6.6`；Git `2.52.0.windows.1`
- Runtime：Python `3.12.3` / `3.14.0`；PySide6 `6.11.2`；pytest `9.1.1`；PyInstaller `6.22.3`
- 执行日期：2026-09-14（Asia/Shanghai）

| 检查 | 实际命令 | 结果 |
|---|---|---|
| reviewed head 已集成 | `git merge-base --is-ancestor 181a356 a501372` | PASS；退出码 0 |
| 被审实质内容未被合并改写 | `git diff --exit-code 181a356 a501372 -- experiments/TASK-004 doc/research/TASK-004.md verification/TASK-004` | PASS；退出码 0 |
| merge 拓扑 | `git rev-list --parents -n 1 a501372` | PASS；一个提交及两个 parent |
| pytest 冒烟 | `C:/Users/49745/AppData/Local/Temp/task004-zcode/venv-py312/Scripts/python.exe -m pytest experiments/TASK-004/test_smoke.py -q --disable-warnings`，并设置 `PYTHONDONTWRITEBYTECODE=1` | PASS；退出码 0；`3 passed in 0.17s` |
| Python 3.12 QML | `C:/Users/49745/AppData/Local/Temp/task004-zcode/venv-py312/Scripts/python.exe experiments/TASK-004/qml_min/main.py` | PASS；退出码 0；真实窗口 visible |
| Python 3.14 QML | `C:/Users/49745/AppData/Local/Temp/task004-zcode/venv-py314/Scripts/python.exe experiments/TASK-004/qml_min/main.py` | PASS；退出码 0；真实窗口 visible |
| Essentials-only QML | `C:/Users/49745/AppData/Local/Temp/task004-zcode/venv-py312-ess/Scripts/python.exe experiments/TASK-004/qml_min/main.py` | PASS；退出码 0；真实窗口 visible |
| onedir Qt 资源 | `C:/Users/49745/AppData/Local/Temp/task004-zcode/venv-py312/Scripts/python.exe experiments/TASK-004/check_qt_files.py C:/Users/49745/AppData/Local/Temp/task004-codex-integration-cleanpath/dist/task004_smoke --layout onedir` | PASS；退出码 0；DLL、platform plugins、QtQuick QML 均存在 |
| onedir 仅系统 PATH 启动 | 设置 `PATH=C:\Windows\System32;C:\Windows` 后执行 `C:/Users/49745/AppData/Local/Temp/task004-codex-integration-cleanpath/dist/task004_smoke/task004_smoke.exe` | PASS；退出码 0；`frozen=true`、窗口 visible |
| 集成范围空白检查 | `git diff --check 84795fb e3c8de7 --` | PASS；退出码 0 |

清洁 PATH 重建命令：

~~~powershell
$env:PATH = (($env:PATH -split ';') | Where-Object { $_ -notmatch '[\\/]\.cache[\\/]codex-runtimes' -and $_ -notmatch '[\\/]\.codex[\\/]tmp[\\/]arg0' }) -join ';'
& C:/Users/49745/AppData/Local/Temp/task004-zcode/venv-py312/Scripts/pyinstaller.exe --noconfirm --clean --onedir --name task004_smoke --distpath C:/Users/49745/AppData/Local/Temp/task004-codex-integration-cleanpath/dist --workpath C:/Users/49745/AppData/Local/Temp/task004-codex-integration-cleanpath/build --specpath C:/Users/49745/AppData/Local/Temp/task004-codex-integration-cleanpath/spec --add-data "G:/CODEX/New Manga/experiments/TASK-004/qml_min/main.qml;." G:/CODEX/New Manga/experiments/TASK-004/qml_min/main.py
~~~

结果：PASS，退出码 0。诊断中确认最初的过滤正则没有匹配 Windows 反斜杠，8 个 Codex runtime PATH 条目仍被保留；`Analysis-00.toc` 因而把其中的 ICU/UCRT DLL 收入产物并导致 `QtCore` 加载失败。改用上述 `[\\/]` 路径分隔符表达式后，过滤残留为 0；重建、资源检查和启动全部通过，产物 `_internal` 中不存在 `icuuc.dll`、`icudt78.dll`、`ucrtbase.dll`。

干净 Windows 机器验证：`BLOCKED`（环境不可得），继续作为发布 Gate；本开发机的清洁 PATH 结果不替代该 Gate。
