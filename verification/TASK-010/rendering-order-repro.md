# TASK-010 移交项取证：tests/rendering 全量顺序依赖（REPRODUCED）

- 取证人：ZCode（TASK-010 作者，受派执行取证；不改任何业务代码）
- 工作路径：`G:/CODEX/New Manga.worktrees/TASK-010-zcode`，分支 `agent/zcode/TASK-010-translation-context`，取证开始时 HEAD=`0f5ab2dfa422af155a9dff34f21ae7e0eebf907e`，`git status` 干净
- reviewed_head：`cd76d30fdc561eb8f22a849eeb5989473957dc5b`（存在）；历史报告基线：`2bdfd6f82b67a550c0550ee930d49bdb12656322`（存在）
- 取证日期：2026-09-16

## 结论

**状态：REPRODUCED（100% 复现，根因定位）**

最小失败集合仅 **3 个测试、约 0.3 秒**：

```bash
PYTHONPATH=src "G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe" -m pytest \
  "experiments/TASK-004/test_smoke.py::test_qml_engine_loads_min_qml" \
  "tests/rendering/test_layout.py::TestFontAvailability::test_installed_font_is_reported_available" \
  "tests/rendering/test_source_style.py::TestPixelAnalyzer::test_two_horizontal_lines_estimate_size_and_direction" \
  -q
# → 2 failed, 1 passed（连续 3 次一致）
```

**根因**：`experiments/TASK-004/test_smoke.py::test_qml_engine_loads_min_qml[offscreen]` 用 `monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")` 后创建 `QGuiApplication`。teardown 恢复的只是环境变量；**QGuiApplication 是进程级单例，一旦以 offscreen 平台插件创建就存活到进程结束**。此后任何复用该单例的测试都在 offscreen 平台下运行，其字体数据库与 Windows 原生平台不同：中文字符串回退到 `Sans Serif` 且字形度量异常：

- `test_installed_font_is_reported_available`：`layout("正常")` → `font_available=False, resolved_family='Sans Serif'`（tests/rendering/test_layout.py:147）
- `test_two_horizontal_lines_estimate_size_and_direction`：`make_text_image` 的中文墨迹投影方向误判为 `VERTICAL`（期望 HORIZONTAL）（tests/rendering/test_source_style.py:85）

**触发条件是 pytest 命令形态，不是环境瞬态**：无参数 `pytest -q` 从 rootdir 递归收集，字母序 `experiments/ < tests/`，smoke 套件先执行并占坑 QApplication → rendering 失败。`pytest tests ...` 形态不收集 `experiments/`，因此全过。**此前 Reviewer 7 种方式与 Codex 复验均未复现，因为都用的是带 `tests` 参数的形态**。

## 环境与现场

| 项 | 值 |
|---|---|
| OS | Windows 11 10.0.26200（platform.win32_ver），x64，Git Bash |
| Python | 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-005-py312/Scripts/python.exe`） |
| pytest | 9.1.1（无第三方 pytest 插件：pip 相关项仅 iniconfig 2.3.0 / packaging 26.3 / pluggy 1.6.0） |
| PySide6 | 6.11.2（PySide6_Essentials 6.11.2） |
| Qt 平台 | 默认 Windows 原生（未设置 QT_QPA_PLATFORM；offscreen 仅出现在被测 monkeypatch 内） |
| 环境变量 | 仅 `PYTHONPATH=src`；无其他定制 |
| 临时 worktree | `G:/CODEX/New Manga.worktrees/_tmp-repro-base` @ `2bdfd6f82b67a550c0550ee930d49bdb12656322`，`git status --short` 干净（本报告提交后删除） |

## 实验矩阵（TASK-010 worktree @ `0f5ab2d`，全部 `PYTHONPATH=src python -m pytest`）

| # | 命令 | 结果 | 退出码 | 证明 |
|---|---|---|---|---|
| A1 | `pytest tests -q -rs` | 328 passed | 0 | 带 `tests` 参数全过 |
| A2 | `pytest tests/rendering -q` | 56 passed | 0 | rendering 单独全过 |
| A3 | `pytest -q`（**无 args，历史形态**） | 2 failed, 329 passed | 1 | 历史失败复现 |
| A4 | `pytest tests --collect-only -q` | 328 collected | — | |
| A5 | `pytest --collect-only -q`（无 args） | **331 collected** | — | 多收的 3 个 = `experiments/TASK-004/test_smoke.py`（3 项），且收集顺序在所有 tests/ 之前 |
| E1 | 最小三件套（见结论） | 2 failed, 1 passed | 1 | 最小指认 |
| E1×3 | 同上重复 3 次 | 3 次均 2 failed, 1 passed | — | 100% 复现 |
| E2 | 顺序反转（rendering 两例在前，smoke 在后） | 3 passed | 0 | 顺序敏感：QApplication 被谁先创建决定结果 |
| E3 | 对照：`test_smoke.py::test_import_pyside6`（不创建 QApplication）在前 + 失败例 | 2 passed | 0 | 排除 experiments 文件本身因素，锁定 `test_qml_engine_loads_min_qml` |
| E4 | `pytest experiments/TASK-004 -q` | 3 passed | 0 | smoke 自身在 offscreen 下正常，无自身缺陷 |

## base `2bdfd6f` 干净临时 worktree 复刻（证明早于 TASK-010）

worktree `_tmp-repro-base`，HEAD=`2bdfd6f82b67a550c0550ee930d49bdb12656322`，`git status --short` 无输出：

| # | 命令 | 结果 | 退出码 |
|---|---|---|---|
| B1 | `python -m pytest -q`（无 args，与历史首次观察同一形态） | **2 failed, 251 passed**（与原 author-verification 记录逐字一致） | 1 |
| B2 | 最小三件套 | 2 failed, 1 passed | 1 |

B1 失败 traceback 与 TASK-010 worktree 上一致（关键断言）：

```text
tests\rendering\test_layout.py:147: AssertionError
E       AssertionError: assert False is True
E        +  where False = LayoutResult(..., font_available=False,
           resolved_family='Sans Serif').font_available

tests\rendering\test_source_style.py:85: AssertionError
E       AssertionError: assert <TextDirection.VERTICAL: 'vertical'> is <TextDirection.HORIZONTAL: 'horizontal'>
```

## 对历史全部观察的一致解释

| 历史观察 | 解释 |
|---|---|
| 全量偶见 `2 failed`（rendering 两例），单独跑 rendering 全过 | 仅当无 args 形态把 experiments 排进 rendering 之前时失败 |
| 收集数 331 vs 328（差 3） | 无 args 多收 `experiments/TASK-004/test_smoke.py` 3 项；非环境瞬态 |
| base 干净树同样 `2 failed, 251 passed` | experiments/ 在 base 已存在（TASK-004），与 TASK-010 新增代码无关 |
| Reviewer/Codex 均未复现 | 其验证命令均带 `tests` 参数，不收集 experiments/ |
| 原 author-verification 中"瞬态"表述 | **不成立，予以修正**：是两种命令形态的系统差异，可 100% 稳定复现 |

## 已做/未做的修改

- 本取证只读业务代码（唯一新文件为本报告）；未修改 `src/**`、`tests/**`、`experiments/**`、pytest 配置；TASK-010 worktree 未切换分支。
- 临时 worktree `_tmp-repro-base` 仅为取证建立，其 git status 与命令输出已在本报告版本化，报告提交后删除。

## 处置建议（超出本取证范围，交 Codex 决策）

1. 短期：验证/Review 约定统一使用 `pytest tests ...` 形态（或加 `pytest.ini` 限定 `testpaths`），避免无 args 收集 experiments；不属本 Task 白名单，需 Codex 另行安排。
2. 根治方向（二选一，需 Codex 授权范围）：`experiments/TASK-004/test_smoke.py` 改用 `QGuiApplication` 之外的进程隔离方式（如 subprocess）避免进程级 QApplication 占坑；或将 experiments 移出 pytest 收集路径。两者都涉及非本 Task 文件，未执行。
3. `test_two_horizontal_lines_estimate_size_and_direction` 的方向误判是字体回退的下游表现，修复平台占坑问题后应随之消失，无需单独修 analyzer。
