# TASK-010 rendering 顺序依赖修复验证

日期：2026-09-16（Asia/Shanghai）

## 修复范围

授权范围仅包含 `experiments/**` 与 pytest 收集配置：

- `pytest.ini`：默认 pytest 收集路径限定为 `tests`，无参数运行不再递归收集 `experiments`。
- `experiments/TASK-004/test_smoke.py`：offscreen QML smoke 改在子进程执行，避免测试进程内创建进程级 `QGuiApplication` 后污染后续 Windows rendering 测试。

未修改 `src/**`、`tests/**`、其他 Task 或依赖清单。

## Red → Green

修复前，最小集合在主线 `014231f` 上为 `2 failed, 1 passed`：

```text
experiments/TASK-004/test_smoke.py::test_qml_engine_loads_min_qml
tests/rendering/test_layout.py::TestFontAvailability::test_installed_font_is_reported_available
tests/rendering/test_source_style.py::TestPixelAnalyzer::test_two_horizontal_lines_estimate_size_and_direction
```

修复后使用 Python 3.12.3、默认 Windows Qt 平台（父进程未设置 offscreen）：

| 命令 | 结果 |
|---|---|
| 上述最小三件套 | **3 passed** |
| `PYTHONPATH=src python -m pytest experiments/TASK-004 -q` | **3 passed** |
| `PYTHONPATH=src python -m pytest --collect-only -q` | **374 tests collected** |
| `PYTHONPATH=src python -m pytest -q -rs` | **368 passed, 6 skipped** |

6 个 skip 均为 `openssl unavailable`。pytest 默认收集已排除 `experiments/TASK-004`；实验仍可通过显式路径单独运行。未修改 `tests/rendering`。
