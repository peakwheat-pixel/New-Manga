# M2-AC3 判别力验证 — Mutation 先红记录

目的：证明套件不是空转（vacuous）——两个核心承诺（失败不被吞、typed code 不被替换）在产品缺陷存在时必须变红。两次 mutation 均为临时本地改动，验证后立即还原；产品代码交付零改动。

环境：同 [verification-results.md](verification-results.md)。基线：还原后新套件 8 passed EXIT=0。

## M1 — 状态伪造（吞 FAILED → run 伪造成 COMPLETED）

Mutation（`src/application/tasks/service.py` `_aggregate_run`）：

```bash
sed -i 's/elif PipelineTaskStatus.FAILED in statuses:/elif False and PipelineTaskStatus.FAILED in statuses:/' src/application/tasks/service.py
```

复跑：

```
$ $py -m pytest tests/m2_acceptance/test_provider_fail_closed.py::test_ac2_network_failure_typed_and_existing_results_intact -q
tests\m2_acceptance\test_provider_fail_closed.py:404: AssertionError
=========================== short test summary info ===========================
FAILED tests/m2_acceptance/test_provider_fail_closed.py::test_ac2_network_failure_typed_and_existing_results_intact
1 failed in 1.38s
```

先红达成：run 状态如实性（AC2/AC1/AC3 共同前提）被检出。

## M2 — typed 错误锚点被替换为 generic

Mutation（`src/application/tasks/service.py` `_fail_step`，`step_run.error_code = code` → `step_run.error_code = "STEP_FAILED"`，Python 单行 replace，`assert c.count(old) == 1` 守卫唯一命中）：

```python
old = '''        step_run.status = StepRunStatus.FAILED
        step_run.error_code = code
        step_run.error_detail = detail
        task.status = PipelineTaskStatus.FAILED
        task.error_code = code'''
new = '''        step_run.status = StepRunStatus.FAILED
        step_run.error_code = "STEP_FAILED"
        step_run.error_detail = detail
        task.status = PipelineTaskStatus.FAILED
        task.error_code = code'''
```

复跑：

```
MUTATION M2 APPLIED
$ $py -m pytest tests/m2_acceptance/test_provider_fail_closed.py::test_ac2_network_failure_typed_and_existing_results_intact -q
tests\m2_acceptance\test_provider_fail_closed.py:413: AssertionError
=========================== short test summary info ===========================
FAILED tests/m2_acceptance/test_provider_fail_closed.py::test_ac2_network_failure_typed_and_existing_results_intact
1 failed in 1.40s
```

先红达成：typed 错误可诊断性（AC1/AC2 的 typed 锚点）被检出。

## 还原确认

两次验证后均执行 `git checkout -- src/application/tasks/service.py` 并复核：

```
$ git status --porcelain src/ | wc -l
0
```

Review 提示：Reviewer 可用上述命令在 Owner 分支任意 head 独立复放（复放后务必同样还原）。
