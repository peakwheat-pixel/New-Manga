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
  显式 fallback、预算截断规则均可在不依赖模型的情况下确定性验证。生产
  Translate Step 引用 `protocol.py` 分类器前必须先吸收 Review R-001~R-003
  （**已于 2026-09-17 由 §4.1 在实验层吸收，见下**）：
  R-001 非字符串 region_id 防御（EXTRA 分支当前会抛 TypeError）、R-002
  RateLimit(429) 补入 RETRYABLE（D06 §56.1 点名）、R-003 上下文排序以
  D06 §13 reading_order 为准（当前贪心截断 + page_id 字典序）。
- **不声称的部分（NOT_RUN）**：真实 OpenAI-compatible 远程 Provider（未配置
  付费端点，任务禁止自行配置）、真实 Sakura 实例、真实模型的术语一致性与
  翻译质量评分。mock 是确定性规则翻译，**不能**替代模型质量评估；质量层
  评估需在配置真实端点后按同一样本协议复跑。
- 对后续 Task 的输入建议：AC-TRANS 的协议类验收（缺失/重复/越界 ID 零容忍）
  可直接引用本实验的分类器；STEP retry 的"相同输入"可用 payload hash 落库
  作为 provenance 字段。

## 4.1 尾项修订（2026-09-17，Codex）：R-001 / R-002 / R-003 已吸收

Review 登记的"生产复用前必须吸收"三项已在**实验层**修正，并各配一个在修复前必然失败的回归测试（判别力已实测：修复前的代码上 5 个新测试全部 FAILED，修复后全绿）。

| ID | 原问题 | 修正 | 回归测试 |
|---|---|---|---|
| R-001 | 非字符串 `region_id` 走到 `EXTRA_IDS` 分支后 `', '.join(extra)` 抛 `TypeError`，校验器崩溃而非返回结构化报告 | 非字符串 id 直接归入 `extra`（`_format_ids()` 用 `repr` 格式化细节）；并显式处理 `translated_text` 非字符串——不再 `str(None)` 造出字面量 `"None"`，而按 `MALFORMED_JSON`（可重试）分类 | `test_non_string_region_id_is_reported_not_crashed`、`test_non_string_translated_text_is_malformed_not_coerced` |
| R-002 | `ProtocolClient` 把非 401 的 4xx 一律归为 `http_4xx`，该 kind 既不在 `RETRYABLE` 也不在 `NOT_RETRYABLE` → **429 被判不可重试**，与 D06 §56.1 冲突 | 429 独立分类为 `http_429` 并加入 `RETRYABLE`；其余 4xx 显式声明在 `NOT_RETRYABLE`（不再靠"不在集合里"隐式判定）；mock 新增 `http_429`/`http_400` 故障注入以便端到端验证 | `test_rate_limit_is_retryable_and_other_4xx_declared` |
| R-003 | 上下文排序键是 `page_id` 字典序而非 D06 §13 `reading_order`；docstring 声称"最远页先丢"，实现却是逐页试探的贪心，远近与大小不对等 | `ContextPage` 增加可选 `reading_order`，排序键为 `(_position, reading_order 或 page_id 尾数, page_id)`；截断策略改为显式声明的"**最近优先保留连续段**"：从最近页开始累加，首个不合预算的页及其更远页一并丢弃，`truncated_context_pages` 按最近优先列出。payload 结构未变 | `test_context_keeps_the_nearest_contiguous_run`、`test_reading_order_beats_page_id_string_order` |

**口径说明（供 TASK-019 采用时对照）**：4xx 中除 401/403/429 外的其余状态码被显式归为不可重试的请求侧错误；如生产需要区分 408（请求超时）等边缘状态，应在生产网络栈单独裁决，不要直接照搬本实验集合。

**未受影响**：`results.json` 与修复前逐字段一致（仅 `latency_ms` 为测量值）——三项修正只在"非字符串输入 / 429 / 带 token budget 的上下文截断"路径上生效，S1~S8 场景不经过这些路径。测试：`test_protocol.py` **20 passed**（15 → 20，新增 5 例）；`test_run_experiment_cli.py` **1 passed**；`run_experiment.py` 退出码 0。真实端点层仍为 **NOT_RUN**（未配置付费端点/本机无 Sakura 实例），本修订**未新增**任何模型质量或成本数字。
