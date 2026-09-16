# TASK-017 作者验证（实验；实现 head 见 Handoff）

## 环境

- OS：Windows 11（win32 10.0.26200 x64），Git Bash
- 工作路径：`G:/CODEX/New Manga.worktrees/TASK-017-zcode`
- 窗口 base：`348a48e`（解冻时 master HEAD）
- 解释器 A：`G:/CODEX/New Manga.task-envs/TASK-014-py312/Scripts/python.exe`（Python 3.12.3 + pytest 9.1.1）
- 依赖：纯 stdlib + pytest（未改依赖清单；实验不引入第三方包）

## 结果

| # | 精确命令（CWD=experiments/TASK-017） | 退出码 | passed | skipped | 结论 |
|---|---|---:|---:|---:|---|
| V1 | `python -m pytest test_protocol.py -q` | 0 | 15 | 0 | PASS：协议契约 15 例（违约分类 5、传输分类 2、输入不变、预算截断、术语一致性、fallback 链、时延/Token、确定性翻译） |
| V2 | `python run_experiment.py` | 0 | S1~S8 全 match | 0 | PASS：机读 results.json（S2 payloads_identical=true；S8 provenance 记录备选；S3~S7 分类 match） |
| V3 | `PYTHONPATH=src python -m pytest tests -q`（全仓，环境 A） | 0 | 536 | 0 | PASS：实验不触碰生产代码，全仓保持绿色 |
| V4 | `git diff --name-only master` | 0 | — | — | PASS：变更仅在白名单（experiments/TASK-017/**、doc/research/TASK-017.md、doc/tasks/TASK-017.md、doc/handoffs/TASK-017-*.md、verification/TASK-017/**） |

无 PySide6 解释器层无需单独验证：实验不导入 PySide6（V1/V2 在任意 3.12+ 解释器可复跑）。

## AC 对照（任务四条）

1. OpenAI-compatible/本地 Sakura 候选协议检验 + 记录可用 Provider/模型版本：
   mock 层完成协议检验；真实 Provider/模型版本登记 NOT_RUN（见下）。
2. 术语一致性、上下文排序、预算截断、缺失/重复/越界 ID、畸形响应的可复现
   样本与评估：S1（术语 3/3 命中、上下文序）、预算截断用例、S3~S7 违约分类，
   全部可复现（pytest + results.json）。
3. retry/fallback 输入不变、网络策略、远程数据范围：S2（payload hash 一致）、
   S8（显式链）+ D06 §56/§57 的可重试分类已编码（RETRYABLE/NOT_RETRYABLE 集合；
   注意 D06 §55 代理失败语义未在本实验编码，属生产网络栈职责）；远程数据
   范围=仅样本文本，无真实用户数据。
4. Handoff/审阅/未完成项：见 Handoff 与本文件 NOT_RUN 表。

## NOT_RUN / BLOCKED 项（不掩盖）

| 项 | 状态 | 原因与恢复条件 |
|---|---|---|
| 真实 OpenAI-compatible 远程 Provider 协议/时延/成本实测 | NOT_RUN | 未配置付费端点且任务禁止自行配置；恢复条件：用户提供测试端点后按同一样本协议复跑 |
| 真实 Sakura 本地实例验证 | NOT_RUN | 本机未运行 Sakura 服务 |
| 真实模型术语一致性/翻译质量评分 | NOT_RUN | mock 为确定性规则翻译，不能声称模型质量；方法已就绪（glossary_hits + 样本），待真实端点 |
