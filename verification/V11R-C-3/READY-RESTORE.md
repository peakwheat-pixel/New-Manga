# READY 包字节恢复记录（C-3-I1 #5）

## 背景

C-3 执行（R2/R3/R6）曾把 6 个 ``verification/V11R-C-3-READY/`` 文件原位覆盖，违反“READY 包只新增、
不覆盖原始字节”的约束。C-3-I1 已逐字节恢复。

## 恢复来源

- 恢复基线：``b5f7d88fc``（C-3 执行前、窄复审修复后的 main）。
- 恢复文件（6）：
  - ``DELETION_BATCHES.md``
  - ``DEPENDENCY_GRAPH.md``
  - ``README.md``
  - ``contrast-matrix.json``
  - ``dependency-graph-table.md``
  - ``dependency-graph.json``
- 校验：``git diff b5f7d88fc -- verification/V11R-C-3-READY`` **为空**。

## 执行结果去向

覆盖前的执行态副本保存在 ``verification/V11R-C-3/final/``：

| READY 文件 | 执行态副本 |
|---|---|
| ``DEPENDENCY_GRAPH.md`` | ``final/DEPENDENCY_GRAPH.executed.md`` |
| ``DELETION_BATCHES.md`` | ``final/DELETION_BATCHES.executed.md`` |
| ``README.md`` | ``final/README.executed.md`` |
| ``dependency-graph.json`` | ``final/dependency-graph.executed.json`` |
| ``dependency-graph-table.md`` | ``final/dependency-graph-table.executed.md`` |
| ``contrast-matrix.json`` | ``final/contrast-matrix.executed.json`` |

C-3-I1 之后的新执行证据只写 ``verification/V11R-C-3/**``；两个工具脚本的默认输出也已改到该目录，
避免再次覆盖 READY 包。

## 说明

- ``contrast-matrix.json`` 的 READY 版本恢复为 C-3 执行前的 6 行/7 对；D-1 I3 之后的 0 行/0 对结果在
  ``verification/V11R-D-1/I3/contrast-matrix.json`` 与 ``verification/V11R-C-3/contrast-matrix.json``。
- ``dependency-graph.json`` 的 READY 版本恢复为 C-3 执行前的基线图；C-3 终态零引用图在
  ``verification/V11R-C-3/dependency-graph.json``。
