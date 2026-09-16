---
task_id: TASK-017
author: ZCode
recipient: ZCode 子 agent（窗口 Review）、后续实现 Task
base_commit: 348a48e
delivery_head: 见提交历史（本文件之后以文档提交追加）
status: in_review
---

# Handoff：TASK-017 Translation 与上下文输出协议实验

## 交付内容（均在白名单内）

- `experiments/TASK-017/`：protocol.py（Context Group 请求构造 + RegionID
  响应校验 + retryable 分类）、mock_provider.py（OpenAI 兼容 mock，脚本化故障
  注入 + 请求记录）、samples.py（日/韩样本与术语表）、test_protocol.py（15 例）、
  run_experiment.py（S1~S8 → results.json）、README.md。
- `doc/research/TASK-017.md`：实验报告（方法/结果/结论/NOT_RUN）。
- `verification/TASK-017/author-verification.md`：精确命令、退出码、passed/
  skipped 分列。

## 关键结果

- RegionID 契约 5 类违约（malformed/missing/duplicate/extra/empty）全部正确
  分类且判定 retryable（D06 §56.1）；401 判定 NOT_RETRYABLE（§56.2）。
- D06 §57：重试前后 payload SHA-256 一致（S2，payloads_identical=true）。
- D06 §54：单端点客户端按构造无自动跨 Provider fallback；显式链 provenance
  记录备选名（S8）。
- 预算截断（§84）：40 Region 全保留，仅上下文页截断并登记 truncated 清单。
- 术语一致性：mock 规则翻译命中 3/3（可复现方法已就绪）。

## 实际测试

| 命令（CWD=experiments/TASK-017） | 退出码 | 结果 |
|---|---:|---|
| `python -m pytest test_protocol.py -q` | 0 | 15 passed, 0 skipped |
| `python run_experiment.py` | 0 | S1~S8 全 match → results.json |
| `PYTHONPATH=src python -m pytest tests -q`（全仓） | 0 | 536 passed, 0 skipped |

## NOT_RUN（诚实清单）

真实远程 Provider、真实 Sakura 实例、真实模型质量评分——付费端点未配置且
任务禁止自行配置；恢复条件与同一样本复跑方法见 research 报告 §4 与
verification NOT_RUN 表。

## 已知问题移交（非本实验引入）

- `tests/reading_export/test_qml_contract.py` 存在低频顺序依赖 flaky（子 agent
  全仓复跑首跑 1 failed、复跑与 master 基线均 536 passed；TASK-015 期间已修复
  一轮，残余偶发与 Qt 焦点/窗口时序相关）。移交 Codex/后续切片跟踪，不阻塞
  本实验结论。

## 对后续 Task 的移交

- Translate Step（生产）落地时建议直接采用 protocol.py 的违约分类与
  retryable 集合；retry provenance 可用 payload hash 落库。
- AC-TRANS 协议类验收可引用本实验分类器作为规格输入（需 Codex 裁量）。

## 下一接收者

ZCode 子 agent 窗口内 Review（approved_subagent / changes_requested）；期满后
外部 post-hoc 复审。
