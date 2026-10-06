# M2-UI-SHELL-ENV-1 — 非作者独立 Review（Antigravity / agy-review-1）

- Reviewer: Antigravity（agy），非作者，只读复核 + 运行验证命令，未修改任何被审文件
- 日期: 2026-10-07
- Base commit: `76379af2ff6a33ada947a015fe1404f499d6fa2d`（与 Task frontmatter `base_commit: 76379af2` 一致）
- 分支: `main`（common dir 为主 `.git`，非 linked worktree），与 Task `branch: main（直落 main）` 一致
- 被审对象:
  - `tests/ui_shell/conftest.py`（未提交修改）
  - `doc/tasks/M2-UI-SHELL-ENV-1.md`（新建 Task 文档）
- 复跑环境: `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe`，pytest 9.1.1，PySide6 6.11.2

---

## 1. 逐项核实结论

### 1.1 conftest.py 改动面（最小性）

**结论：通过。**

`git diff tests/ui_shell/conftest.py` 全部改动只有：

1. 模块 docstring 新增一段说明（M2-UI-SHELL-ENV-1、RHI(D3D) 后端在窗口 surface 非交互时丢弃 `QTest.mouseClick` 合成投递、software 后端保留 Windows 平台+字体库、setdefault 保留外部覆盖）；
2. 新增 `import os` 与 `os.environ.setdefault("QT_QUICK_BACKEND", "software")`；
3. `import helpers  # noqa: F401` → `import helpers  # noqa: E402`（import 因插入 env 设置不再位于文件顶部，noqa code 的配套修正）。

无其他任何改动。不触碰 fixture 逻辑、不触碰产品代码，**最小且不改变产品行为**。

### 1.2 env 设置时序（任何 Qt 导入与 QGuiApplication 创建之前）

**结论：通过。**

- conftest.py 模块级本身不导入 PySide6；`QGuiApplication` 只在 session fixture `qapp` 函数体内导入（conftest.py:29），远晚于第 18–20 行的 `import os` + `os.environ.setdefault`。
- 无根目录 conftest.py、无 `tests/conftest.py`（find 核实），pytest 加载顺序保证 `tests/ui_shell/conftest.py` 先于同目录测试模块导入；测试文件 `test_repair13_import_entry.py` 的模块级 `from PySide6...` 导入发生在 env 设置之后。
- 环境 pip list 中无 pytest-qt 等会在 conftest 之前导入 PySide6 的插件（仅 pytest 9.1.1）。
- 行为级反证：实验 b 中显式 `QT_QUICK_BACKEND=rhi` 未被 setdefault 覆盖（复现 2 failed），证明该 env 变量在 Qt Quick 后端选择前确实由进程环境生效。

### 1.3 setdefault 语义（允许外部覆盖）

**结论：通过。** 实验 b 直接证明：显式 `QT_QUICK_BACKEND=rhi` 下 setdefault 不生效（若覆盖则会走 software 并 5 passed，实际 2 failed）。显式 `QT_QUICK_BACKEND=software` 亦兼容（实验 c，5 passed）。

### 1.4 零漂移声称

**结论：全部证实。**

- `git log -1 -- tests/ui_shell/test_repair13_import_entry.py` = `6fe7455d`（2026-09-25, "integrate: T3.2.1-REPAIR-13 reviewed slice"），且 `git diff 6fe7455d -- tests/ui_shell/test_repair13_import_entry.py` 为空 → 测试文件自 6fe7455d 未变。
- `git log --since="2026-10-01" -- src/ui/qml` 输出为空 → src/ui/qml 2026-10-01 以来零 commit。
- `requirements.txt:1` = `PySide6_Essentials==6.11.2`；环境实际 `PySide6.__version__` = 6.11.2 → pin 一致。

### 1.5 对照实验复现（我自己的复跑，非引用作者数据）

| # | 命令（原样） | 结果 | 与 Task 声称对照 |
|---|---|---|---|
| a | `unset QT_QUICK_BACKEND && python -m pytest tests/ui_shell/test_repair13_import_entry.py -q` | `5 passed in 1.97s` | 一致（setdefault 生效） |
| b | `QT_QUICK_BACKEND=rhi python -m pytest tests/ui_shell/test_repair13_import_entry.py -q` | `2 failed, 3 passed in 2.31s`，失败例 = `test_current_chapter_alias_follows_row_click`、`test_import_entry_enabled_after_row_click` | **强于声称**：本会话直接复现两例失败，失败例清单与 Task 完全一致 |
| c | `QT_QUICK_BACKEND=software python -m pytest tests/ui_shell/test_repair13_import_entry.py -q` | `5 passed in 2.01s` | 一致，显式覆盖兼容 |
| d（补充） | `QT_QPA_PLATFORM=offscreen python -m pytest tests/ui_shell/test_repair13_import_entry.py -q` | `5 passed in 1.63s` | 复现 Task 定性事实中的 offscreen 对照 |

失败输出特征与 Task 定性一致：`btnImport ... .isEnabled` 为 False（`QTest.mouseClick` 合成投递后章节行未响应、`currentChapterId` 停留空），而 stderr 的 QML `TypeError: Cannot read property ... of null` 群在三组（含全过组）均出现，确属非断言失败主因的噪声，与 Task 文档描述吻合。

注：实验 b 复现本身即证明"失败绑定默认渲染后端"这一决定性对照成立。至于根因子定性"锁屏/断连显示导致 surface 非交互"，Reviewer 无法从进程内独立观测会话显示状态，只能确认本复跑发生在与作者同一工作会话环境且结果一致；该子定性合理但不构成 approve 的必要前提（处置正确性由后端对照关系独立支撑）。

### 1.6 Task 文档范围冻结 vs 实际 diff

**结论：一致。**

`git status --short` 实际输出：

```
 M tests/ui_shell/conftest.py
?? doc/tasks/M2-UI-SHELL-ENV-1.md
?? verification/M2-TEST-CATALOG-DRIFT-CLEAR-1/raw/agy-review-1.err
?? verification/M2-UI-SHELL-ENV-1/
```

- 代码改动仅 conftest.py 一个文件；Task 文档为唯一新建 doc；verification 目录为证据留档（含作者 `full-pytest-1.log` 与本报告）。
- `M2-TEST-CATALOG-DRIFT-CLEAR-1/raw/agy-review-1.err` 是上一 Task 的历史 verification 留档杂物，不属本 Task，也不触碰任何测试/产品代码，不违反范围冻结。
- 零 src/ui、零 QML、零其他测试文件、零契约改动 → 与 Task "范围（冻结）" 声明逐条相符。

### 1.7 offscreen vs software 的选择依据

**结论：通过。** Task 定性事实记录 offscreen 下 5 passed（我已复现），但 conftest 原 docstring 的既有约束（offscreen 平台无字体数据库、QML Controls 文本布局异常；Windows 是产品边界）仍然有效。software 后端只固定 Quick 渲染后端、保留 Windows QPA 平台与字体库，是侵入性最小的确定性方案，符合原约束。

### 1.8 作者全量证据核对（未独立复跑全量）

作者留档 `verification/M2-UI-SHELL-ENV-1/raw/full-pytest-1.log` 结尾：

```
1862 passed, 1 skipped, 3 warnings in 103.22s (0:01:43)
EXIT=0
```

与 Task 验收 Gate 3 数字（1862 passed + 1 skipped + 0 failed）一致。本轮 Review 未复跑全量（成本考量），Gate 3 数字以作者日志为准、Gate 1 已由我独立复现。

---

## 2. 复跑证据原样摘录

```
$ unset QT_QUICK_BACKEND && '.../python.exe' -m pytest tests/ui_shell/test_repair13_import_entry.py -q
...(QML TypeError 噪声 stderr，略)...
                                                                    [100%]
5 passed in 1.97s

$ QT_QUICK_BACKEND=rhi '.../python.exe' -m pytest tests/ui_shell/test_repair13_import_entry.py -q
E        +  where False = <built-in method isEnabled of PySide6.QtQuick.QQuickItem ...name="btnImport" ...>()
tests\ui_shell\test_repair13_import_entry.py:163: AssertionError
FAILED tests/ui_shell/test_repair13_import_entry.py::test_current_chapter_alias_follows_row_click
FAILED tests/ui_shell/test_repair13_import_entry.py::test_import_entry_enabled_after_row_click
2 failed, 3 passed in 2.31s

$ QT_QUICK_BACKEND=software '.../python.exe' -m pytest tests/ui_shell/test_repair13_import_entry.py -q
                                                                    [100%]
5 passed in 2.01s

$ QT_QPA_PLATFORM=offscreen '.../python.exe' -m pytest tests/ui_shell/test_repair13_import_entry.py -q
                                                                    [100%]
5 passed in 1.63s
```

---

## 3. Findings（分级）

- **P0–P2：无。** 未发现阻塞、正确性或范围违规问题。
- **P3：无。**
- **P4-1（风格，无实际影响）**：`tests/ui_shell/conftest.py:22` 的 `import helpers  # noqa: E402` 丢掉了原 F401 压制。helpers 为纯副作用导入（sys.path 注入），若未来引入 flake8/ruff，F401（unused import）会与 E402 同时出现；建议届时统一为 `# noqa: E402, F401`。当前仓库无任何 lint 配置（无 pyproject.toml/setup.cfg/.flake8/ruff.toml，已核实），无实际影响，不阻塞。
- **P4-2（证据边界说明）**：根因子定性"会话窗口 surface 非交互（锁屏/断连显示）"无法由 Reviewer 从进程内独立观测证实；本 Review 复现并确认的是"失败绑定 QT_QUICK_BACKEND=RHI、software/offscreen 转绿"的决定性对照，处置正确性不依赖该子定性。
- **P4-3（工作区杂物）**：`verification/M2-TEST-CATALOG-DRIFT-CLEAR-1/raw/agy-review-1.err` 为上一 Task 遗留 untracked 留档，与本 Task 无关，建议集成时（Codex）顺手确认是否纳入留档或清理。

---

## 4. Verdict

**approve**

理由：改动最小（单文件、5 行级）、不改变产品行为、env 设置时序正确（先于任何 PySide6 导入与 QGuiApplication 创建）、setdefault 语义经行为级反证确认、范围冻结声明与实际 diff 逐条相符、零漂移声称全部证实、决定性对照（RHI 2 failed / software 5 passed / offscreen 5 passed）由 Reviewer 独立复现。P4 各项均为非阻塞备注。

建议集成（Codex）时可引用本报告与 `full-pytest-1.log` 完成 Gate 4，随后按 Task 完成定义更新 STATUS 基线数字（2 failed 清零）。
