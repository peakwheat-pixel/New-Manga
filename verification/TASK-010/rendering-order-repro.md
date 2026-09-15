# TASK-010 rendering 顺序依赖最小复现记录

日期：2026-09-15（Asia/Shanghai）  
固定被审范围：`2cceb1e..cd76d30`  
当前集成：`a225790d5eaf90227249039255bb554307f5b2cc9`

状态：**NOT_REPRODUCED**

作者曾报告 base `2bdfd6f` 全量出现 `tests/rendering/test_source_style.py::TestPixelAnalyzer` 两例失败，而单独运行 rendering 通过。Reviewer 已按 7 种方式复核，均未复现；Codex 在集成后的主线再次执行最小顺序探针，也未复现。因此本次不修改 `tests/rendering` 或 `tests/knowledge`，也不创建独立分析 Task。

## 集成后最小探针

解释器为 TASK-010 集成验证使用的 Python 3.12.3 环境：

| 命令 | 结果 |
|---|---|
| `python -m pytest tests/rendering -q` | **56 passed** |
| `python -m pytest tests/knowledge tests/rendering -q` | **134 passed** |
| `python -m pytest tests/rendering tests/knowledge -q` | **134 passed** |
| `python -m pytest tests/rendering/test_source_style.py::TestPixelAnalyzer -q` | **5 passed** |

## 后续证据要求

请原报告者提供可直接运行的最小复现，至少包括：完整命令与参数、测试收集顺序、失败测试及完整断言输出、Windows/Python/pytest/Qt 环境、`PYTHONPATH`/插件配置，以及最好能指向干净 base commit。收到前不改变测试套件；收到后由 Codex 再决定是否需要独立分析。
