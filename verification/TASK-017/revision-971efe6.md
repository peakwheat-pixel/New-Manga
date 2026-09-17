# TASK-017 尾项修订取证：`971efe6`（Review R-001 / R-002 / R-003）

- Task：TASK-017「Translation 与上下文输出协议实验」尾项修订切片
- 作者（本切片）：Codex ／ Reviewer：DeepSeek Harness（**非作者**，独立 Review）
- 固定 base：`754eb4f`（master，含 TASK-018 全部集成）；交付 head：`971efe6`
- 分支 / 工作区：`agent/zcode/TASK-017-translation-protocol-experiment` ／ `G:/CODEX/New Manga.worktrees/TASK-017-zcode`
- 已集成基线：TASK-017 主体 integration=`c0cf3a1`（ZCode 窗口交付）、post-hoc Review `fb0bc40`（DSH approved）——**均不因本切片失效**

## 1. 为什么有这个切片

ZCode 子 agent Review（[`doc/reviews/TASK-017-protocol.md`](../../doc/reviews/TASK-017-protocol.md)）登记 R-001/R-002/R-003 为 **open（"移交生产实现 Task"）**，且 [研究报告](../../doc/research/TASK-017.md) §4 明确写着"生产 Translate Step 引用 `protocol.py` 分类器前**必须先吸收** R-001~R-003"。TASK-019（Provider 集成，未释放）会直接消费该分类器，因此这里先把三项在实验层吸收并补回归测试。

三项在本次修订前**均可在 master 上复现**（见 §3 的"判别力"两行）。

## 2. 三项修正

| ID | 修正内容 |
|---|---|
| R-001 | `validate_response`：非字符串 `region_id` 一律归入 `extra`（新增 `_format_ids()`，非字符串用 `repr` 呈现），不再走到 `', '.join(extra)` 抛 `TypeError`；`translated_text` 非字符串不再被 `str()` 静默转成 `"None"`，改判 `MALFORMED_JSON`（可重试） |
| R-002 | `ProtocolClient.complete`：429 独立分类为 `http_429`；`RETRYABLE` 显式加入 `http_429`（D06 §56.1 点名 RateLimit 可重试）；`NOT_RETRYABLE` 显式声明 `http_4xx`（其余 4xx 为请求侧，不再靠"不在集合里"隐式判定）。`MockProvider` 新增 `http_429` / `http_400` 故障注入 |
| R-003 | `ContextPage` 新增可选 `reading_order`（D06 §13）；排序键 `(_position, reading_order 或 page_id 尾数, page_id)`，不再用 `page_id` 字典序；截断策略改为显式声明的"最近优先保留连续段"（首个不合预算的页及其更远页一并丢弃，`truncated_context_pages` 按最近优先列出），docstring 与实现一致 |

**口径说明（供 TASK-019 采用时对照）**：除 401/403/429 外的 4xx 被显式归为不可重试的请求侧错误；若生产需要区分 408 等边缘状态，应在生产网络栈单独裁决，不要直接照搬本实验集合。

## 3. 验证（作者执行；Reviewer 需独立复跑）

环境：Windows `10.0.26200`；Python 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-012-py312`，pytest 可用）；CWD=`experiments/TASK-017`；`PYTHONDONTWRITEBYTECODE=1`。

| # | 命令 | 退出码 | passed | skipped | 结果 |
|---|---|---:|---:|---:|---|
| 1 | `python -m pytest test_protocol.py -q -p no:cacheprovider` | **0** | **20** | **0** | `20 passed in 7.71s`（**15 → 20**，新增 5 例） |
| 2 | `python -m pytest test_run_experiment_cli.py -q -p no:cacheprovider` | **0** | **1** | **0** | `1 passed` |
| 3 | `python run_experiment.py`（`%TEMP%` 整目录副本内执行） | **0** | — | — | S1~S8 全部通过；`results.json` 与仓库已提交版本**逐字段一致（仅 `latency_ms` 为测量值）** |
| 4 | **判别力**：把修复后的 `test_protocol.py` 放到**修复前**的 `protocol.py`/`mock_provider.py` 副本上运行 | 1 | 15 | 0 | **5 failed**（新增的 5 例在修复前全部失败）→ 证明测试非空断言，三项缺陷此前真实存在 |
| 5 | `git diff --check 754eb4f 971efe6` | **0** | — | — | 无输出 |

**skip 原因**：命令 1、2 均 **`0 skipped`**（纯 stdlib + 本机回环 mock，无模型、无外网、无付费端点）。

**未改动**：`experiments/TASK-017/results.json`（**未被覆盖**，且在副本内复跑后与提交版本一致）、`samples.py`、`test_run_experiment_cli.py`、生产 `src/`、`tests/`、Schema、依赖清单、`AGENTS.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/tasks/README.md`、其他 Task。

## 4. 未完成项（本切片未改变）

| 项 | 状态 | 原因 |
|---|---|---|
| 真实 OpenAI-compatible 远程 Provider | **NOT_RUN** | 未配置付费端点，且任务禁止自行配置 |
| 真实 Sakura 本地实例 | **NOT_RUN** | 本机未运行 Sakura 服务 |
| 真实模型的术语一致性与翻译质量评分 | **NOT_RUN** | mock 是确定性规则翻译，**不能**替代模型质量评估 |

本切片**未新增**任何模型质量、成本或时延数字。

## 5. 边界与合规

- 仅修改 `experiments/TASK-017/{protocol.py,mock_provider.py,test_protocol.py}` 与 `doc/research/TASK-017.md`，全部在 TASK-017 允许路径内。
- 未 push；未把分支合并回 master（交 Reviewer 独立 Review 后由 Codex 集成）。
