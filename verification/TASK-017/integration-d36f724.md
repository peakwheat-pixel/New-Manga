# TASK-017 集成验证：`d36f724`（尾项修订切片）

## 固定对象

| 项目 | 值 |
|---|---|
| base commit | `754eb4f87b83816f7dd0e1bb2bcbc17ba18fc731` |
| reviewed head（delivery） | `971efe689f9c8c000eac3a6d97fe1a3c9a0807bb` |
| 元数据 head（作者） | `387bb1e6a9bad2c881fb4992ee7b362b97070235` |
| Review 报告 commit | `e50ba29`（Reviewer 分支 `agent/deepseek/TASK-017-tail-review`）→ [`doc/reviews/TASK-017-971efe6.md`](../../doc/reviews/TASK-017-971efe6.md)（decision=`approved`，P3×1） |
| implementation merge / integration commit | `d36f724`（merge，3 parents：`754eb4f` + `387bb1e` + `e50ba29`） |
| 已集成主体（不因本切片失效） | TASK-017 主体 integration=`c0cf3a1`（ZCode 窗口交付，Review `approved_subagent`）+ post-hoc Review `fb0bc40`（DSH approved，R-101 已关闭） |
| 环境 | Windows `10.0.26200`；Python 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-012-py312`）；`PYTHONDONTWRITEBYTECODE=1`；未设置 `QT_QPA_PLATFORM` |

## 复验结果（master `d36f724`）

| # | 命令（CWD = 仓库根） | 退出码 | passed | skipped | 结果 | skip 原因 |
|---:|---|---:|---:|---:|---|---|
| 1 | `…python.exe -m pytest experiments/TASK-017/test_protocol.py -q` | 0 | **20** | **0** | `20 passed`（15 → 20，新增 R-001/R-002/R-003 回归 5 例） | 无（纯 stdlib + 本机回环 mock，无模型/外网/付费端点） |
| 2 | `…python.exe -m pytest experiments/TASK-017/test_run_experiment_cli.py -q` | 0 | **1** | **0** | `1 passed` | 无 |
| 3 | `…python.exe -m pytest -q -p no:cacheprovider`（全仓） | 0 | **530** | **6** | `530 passed, 6 skipped` | 6 项均为 `openssl unavailable`（`tests/network/`） |

## 验收结论

- [x] Review 由**非作者**（DeepSeek Harness）在独立 linked worktree 中完成，结论 `approved`（P0=0/P1=0/P2=0/P3=1），固定 base/head 与上表一致。
- [x] 三项 open finding 已吸收：R-001 非字符串 `region_id`/`translated_text` 不再崩溃、不再静默造出 `"None"`；R-002 429 显式可重试、其余 4xx 显式声明不可重试；R-003 排序按 `reading_order`（D06 §13）、截断策略与 docstring 一致。
- [x] 判别力已由 Reviewer 独立复现：修复后的测试放在修复前代码上 **5 failed / 15 passed**（非空断言）。
- [x] **已集成 measured 数据未被改写**：`git diff 754eb4f d36f724 -- experiments/TASK-017/results.json` 无输出；复跑（`%TEMP%` 副本内）与提交版本仅 `latency_ms` 一处差异。
- [x] 白名单越界 0；未修改 Schema、共享 Protocol、依赖清单、`AGENTS.md`、生产 `src/`、`tests/`、其他 Task；未 push。
- [ ] 真实 Provider / 真实 Sakura / 真实模型质量评分仍 **NOT_RUN**（未配置付费端点、本机无 Sakura 实例；禁止自行配置）——**不得视为通过**。

## Findings 关闭记录

| ID | 级别 | 内容 | disposition |
|---|---|---|---|
| R-001 | P2（首轮 Review） | 非字符串 `region_id` 触发未分类 `TypeError` | **closed**（`971efe6` 修复 + 回归测试；Reviewer 复核成立） |
| R-002 | P2（首轮 Review） | 429 被判不可重试，与 D06 §56.1 冲突 | **closed**（`http_429` 入 `RETRYABLE`，其余 4xx 显式声明；mock 可端到端触发） |
| R-003 | P2（首轮 Review） | 上下文排序用 `page_id` 字符串序、docstring 与实现不符 | **closed**（`reading_order` + 显式截断策略，payload 结构与 `results.json` 未变） |
| R-101 | P3（本轮 Review，观察） | `results.json` 的 `latency_ms` 为易变字段，使"逐字段一致"比对必然出现 1 处差异 | **closed**（`experiments/TASK-017/README.md` 注明该字段易变、比对应排除，并列出可指纹化的确定性字段；`results.json` 未改动） |

## 未验证项（未因本切片变化）

| 项 | 状态 | 说明 |
|---|---|---|
| 真实 OpenAI-compatible 远程 Provider（端到端） | **NOT_RUN** | 未配置付费端点，且任务禁止自行配置；该 harness 目前也不发送 `Authorization` 头 |
| 真实 Sakura 本地实例 | **NOT_RUN** | 本机未运行 Sakura 服务 |
| 成本 / 时延实测（真实端点） | **NOT_RUN** | 同上 |
| 真实模型的术语一致性与翻译质量评分 | **NOT_RUN** | mock 为确定性规则翻译，不能替代模型质量评估 |
| 生产集成验证 | **N/A** | 实验不代表产品集成；本 Task 不修改 `src/` |
