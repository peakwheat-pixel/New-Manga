# GOV-CHECKER-NOTASK-1 证据索引

## 实施前基线

- `baseline_matrix.py`：在仓外 `baseline-blob` 隔离副本运行 checker 的场景生成器；逐场景恢复 STATUS、任务卡和 Ledger 原始字节。
- `baseline-run-eb06df0-blob.log`：生成 HEAD `eb06df0d8e8521d43753823a8ef00166f19121b1`，checker SHA-256 `d1c2f6632c384bbf53a8ea8cc740ea86338f8ee30c5d9b989181978ff5fe765b`，场景前后隔离副本 clean；命令和逐项 EXIT 见日志。脚本对预设基线条件的检查 `HARNESS_EXIT=0`，不是修改后验收。

本次影响面按输入状态划分为：存在可解析当前指针（有效非终态、终态、路径缺失）；无可解析指针（明确空窗、缺行、歧义行）；显式 `-TaskPath`（含 done/pending）。基线分别实测了这些代表输入；额外的重复声明、空窗附路径与其他歧义边界以及变异判别仍待实施后验证，不能据本次样本宣称已穷尽字符串输入。

终态指针样本额外出现历史 evidence 在不同 checkout 字节基准下的 SHA 不匹配和两个未随 Git 携带的 pyc 缺失；pending 样本额外出现未完成卡面的 closeout 错误。两者均在日志中保留，断言分别针对实际输出中的终态指针错误和 integration_commit 错误，不能只凭非零 EXIT 推断该规则有效。

首个隔离副本受 `core.autocrlf=true` 影响，Plan 为 7030 bytes 超过预算；其输出管道也出现中文解码错误。诊断日志保留于仓外 `G:/CODEX/New Manga.workspace/GOV-CHECKER-NOTASK-1/baseline-run-eb06df0.log`，不作为基线通过证据。第二个副本使用 `core.autocrlf=false` 并修正输出编码；两个副本均保留，未清理。

后续实现、反例、变异、独立 Review 和最终门禁均为 NOT_RUN。
