# TASK-018 集成验证：`5a9f5c8`（尾项切片 · R-104 关闭）

## 固定对象

| 项目 | 值 |
|---|---|
| base commit | `6f130ade18c6c83a42a40a16e7620af518f55e33`（master） |
| 被审 head（delivery） | `965bcd2308c367d3428f564d68edd68c73ac8545` |
| 元数据 head | `c8c2a8e`（仅新增 Handoff） |
| Review 报告 | [`doc/reviews/TASK-018-965bcd2.md`](../../doc/reviews/TASK-018-965bcd2.md)（decision=`approved`） |
| implementation merge / integration commit | `5a9f5c8`（merge，parents `f190fc8` + `c8c2a8e`） |
| 前次集成基线（仍有效） | `14b92e4`（另见 [integration-14b92e4.md](integration-14b92e4.md)）；首轮 `4d189ce`（[integration-4d189ce.md](integration-4d189ce.md)） |
| 环境 | Windows `10.0.26200`；Python 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-012-py312`）；PySide6 6.11.2；`PYTHONPATH=experiments/TASK-018`、`PYTHONDONTWRITEBYTECODE=1`；未设置 `QT_QPA_PLATFORM` |

## 复验结果（master `5a9f5c8`）

| # | 命令 | 退出码 | passed | skipped | 结果 | skip 原因 |
|---:|---|---:|---:|---:|---|---|
| 1 | `…python.exe -m unittest experiments/TASK-018/test_mask_protocol.py` | 0 | **12** | **0** | `OK`（该文件自首轮起未被改动） | 无 |
| 2 | `…python.exe -m unittest experiments/TASK-018/test_route_gating.py` | 0 | **16** | **0** | `OK`（13 → 16，新增 `StartupAssertionTests` 3 例，**通过数未减少**） | 无 |
| 3 | `…python.exe <副本>/experiments/TASK-018/run_experiment.py --repeat 3` | 0 | N/A | N/A | `{"MEASURED": 10, "BLOCKED": 20}`；`blocked_stage` 20/20 `not_implemented`；保护违规 10/10 为空；保护框 **20 框全 0**；确定性字段与提交 JSON **0 差异** | 进程执行，N/A |
| 4 | **反例（Reviewer 独立复现，CLI 路径）**：临时副本把 `FILLERS` 的 `simple-fill` 条目改名（route 仍声明 `implementation`），执行 `run_experiment.py --repeat 1 --output-dir <temp>` | **1** | N/A | N/A | `RuntimeError: route/FILLERS misconfiguration: simple-fill declare an implementation but have no registered filler; refusing to start`；**写出 PNG = 0**；确认为启动即失败 | N/A |
| 5 | `…python.exe -m pytest -q -p no:cacheprovider`（全仓） | 0 | **530** | **6** | `530 passed, 6 skipped in ~23 s` | 6 项均为 `openssl unavailable`（`tests/network/`） |

命令 3 在 `%TEMP%\task018-int3-150628` 的整目录副本中执行（harness 会把 `results/experiment.json` 写在实验根内）；仓库内 `results/experiment.json` **未被覆盖**：`git diff 6f130ad 5a9f5c8 -- experiments/TASK-018/results/` 为空，工作区干净。该文件工作区为 CRLF、blob 为 LF（`git ls-files --eol` = `i/lf w/crlf`），归一化后逐字节相同。

## 验收结论

- [x] R-104 关闭：`run_experiment.py` 新增 `assert_implementations_registered()` 并在**模块导入期**调用；`implementation` 非 `None` 却未在 `FILLERS` 注册即 `RuntimeError` 拒绝启动（不再出现运行中途 `KeyError` 并留下部分产物的窗口）。
- [x] 反例经 Reviewer 独立复现（CLI 路径，与作者的 import 路径互补）：退出码 1、消息含 `route/FILLERS misconfiguration`、**未写任何 PNG**、输出目录未创建。
- [x] 守卫不误报：真实 harness 正常跑通（10 MEASURED / 20 BLOCKED）。
- [x] 未改动任何已集成 measured 数据：`results/experiment.json` 与 `test_mask_protocol.py` 未被触碰，确定性字段与提交 JSON 0 差异。
- [x] 白名单越界 0；未修改生产 `src/`、`tests/`、Schema、依赖清单、`AGENTS.md`、其他或冻结 Task；未扩展到 TASK-019；未 push。
- [ ] 四条学习型路线的质量/耗时/内存/显存仍 `BLOCKED`；Mask 内部结构损伤量化、真实 OOM、真实漫画样例仍 `NOT_RUN`——**不得视为通过**。

## Findings

| ID | 级别 | 内容 | 状态 |
|---|---|---|---|
| R-201 | P3 | `doc/tasks/TASK-018.md` 只同步了 frontmatter 与优先级声明，自称"唯一"的状态块仍写 `done`/"无未决 Review"并把 R-104 记为 deferred | **closed in integration**（本次收口重写该状态块为最终状态与 `integration_commit=5a9f5c8`） |

观察项（非缺陷）：守卫为单向检查（不覆盖多余的 `FILLERS` 条目或 `implementation=None` 却已注册），与 Reviewer 原建议一致且不会产生伪造成果；`run()` 不做运行期复检。
