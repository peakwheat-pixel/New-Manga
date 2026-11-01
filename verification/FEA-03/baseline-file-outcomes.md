# FEA-03 Python 基线逐项 outcome

运行命令：
python -m pytest tests/editing tests/domain tests/infrastructure tests/core/test_region_write_commands.py tests/core/test_region_batch_locking.py -q

环境结果：BLOCKED，CPython 3.14 报 No module named pytest；pytest 没有 collection，因此没有测试 passed/failed/skipped 计数，也没有逐文件修前/修后差异可计算。当前也没有本次改动前的 pytest 日志，不能补造 pre-change baseline。

| 路径 | 修前 outcome | 修后 outcome | 判定 / 理由 |
|---|---|---|---|
| tests/editing/ | NOT_RUN | BLOCKED | pytest 不可导入，无法 collection。 |
| tests/domain/ | N/A（该目录由 FEA-03 新建） | BLOCKED | 新增测试未收集；Task v6 明确不计入基线目录。 |
| tests/infrastructure/ | NOT_RUN | BLOCKED | pytest 不可导入，无法 collection。 |
| tests/core/test_region_write_commands.py | NOT_RUN | BLOCKED | pytest 不可导入，无法 collection。 |
| tests/core/test_region_batch_locking.py | NOT_RUN | BLOCKED | pytest 不可导入，无法 collection。 |

通过率：0 passed、0 failed、0 skipped；这是命令未能启动测试的结果，不能解释为测试通过。