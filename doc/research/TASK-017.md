# TASK-017 实验报告：Translation 与上下文输出协议

- 执行：ZCode（2026-09-16 窗口授权）
- 环境：Windows 11 / Python 3.12.3（task-envs/TASK-014-py312）/ pytest 9.1.1，纯 stdlib
- 代码：`experiments/TASK-017/`（protocol.py / mock_provider.py / samples.py /
  test_protocol.py / run_experiment.py），机读结果 `results.json`
- 来源：D06 §10~18（Constraint/Context/Translate Step）、§54~57（fallback、retry、
  输入不变）、§84（Context Group）；D08 AC-TRANS/CONSTRAINT/TM/FALLBACK

## 1. 实验问题

1. RegionID 输出协议能否在不依赖具体模型的情况下被机器校验
   （缺失/重复/越界 ID、畸形响应）？
2. D06 §57"retry 不得改变输入"如何在协议层验证？
3. 预算截断（token budget）与 Context Group 分组（D06 §84）的行为边界？
4. D06 §54 默认禁止自动跨 Provider fallback、§56 错误分类是否可落地为
   可执行规则？

## 2. 方法

OpenAI 兼容 mock provider（线程内 HTTP，`/v1/chat/completions`）+
确定性规则翻译（术语表直译 + 伪翻译），故障按脚本注入
（malformed/empty/drop/dup/extra/503/401）。所有请求 payload 被记录，
用 SHA-256 比对重试前后输入。时延以注入延迟（30ms）验证可测量性，
Token 以 CJK 感知近似估算。

## 3. 结果（S1~S8，全部 match；机读见 results.json）

| 场景 | 结果 |
|---|---|
| S1 单页+双页上下文+术语表 | 协议 ok；术语命中 3/3（先輩/倒す/마법）；上下文未截断 |
| S2 retry 输入不变（§57） | 503→ok 两次请求 payload 完全一致（payloads_identical=true，hash=`7c5c50cd…`） |
| S3~S7 协议违约分类 | malformed_json/missing/duplicate/extra/empty 全部分类正确；全部 retryable（D06 §56.1 口径：Provider 输出坏≠本地 InvalidInput） |
| S8 显式 fallback 链（§54） | 主→备仅在显式配置链上发生；provenance 记录备选 Provider 名；客户端按构造单端点，不存在自动 fallback |
| 401 分类 | NOT_RETRYABLE（§56.2 立即失败） |
| 预算截断 | 40 Region 全保留，仅上下文页进入 truncated 清单（§84"输出必须能映射回 Page/Region"可行） |
| 时延/Token 测量 | 注入 30ms 延迟下测量 ≥25ms（可测量）；CJK token 估算可用 |

pytest：`15 passed, 0 skipped`（退出码 0）。

## 4. 结论与适用范围

- **协议层结论（mock 证据，可复现）**：RegionID 契约校验、retry 输入不变、
  显式 fallback、预算截断规则均可在不依赖模型的情况下确定性验证；建议
  生产 Translate Step 落地时直接采用 `protocol.py` 的分类（ok/malformed/
  missing/duplicate/extra/empty）与 retryable 集合。
- **不声称的部分（NOT_RUN）**：真实 OpenAI-compatible 远程 Provider（未配置
  付费端点，任务禁止自行配置）、真实 Sakura 实例、真实模型的术语一致性与
  翻译质量评分。mock 是确定性规则翻译，**不能**替代模型质量评估；质量层
  评估需在配置真实端点后按同一样本协议复跑。
- 对后续 Task 的输入建议：AC-TRANS 的协议类验收（缺失/重复/越界 ID 零容忍）
  可直接引用本实验的分类器；STEP retry 的"相同输入"可用 payload hash 落库
  作为 provenance 字段。
