# TASK-017：Translation 与上下文输出协议实验

纯 stdlib 实现（Python 3.12，pytest），无网络依赖；真实 Provider 层
NOT_RUN（未配置付费端点，任务禁止自行配置）。

## 运行

```bash
cd experiments/TASK-017
python -m pytest test_protocol.py -q      # 15 例协议测试
python run_experiment.py                  # 全场景，写 results.json（退出码 0=全过）
```

## 结构

- `protocol.py`：Context Group 请求构造（D06 §84：预算截断先丢上下文页、
  Region 永不截断）、RegionID 响应校验（missing/duplicate/out-of-range/
  malformed/empty 分类，D06 §56 retryable 判定）、术语一致性命中检查。
- `mock_provider.py`：OpenAI 兼容 `/v1/chat/completions` mock（线程内 HTTP），
  可编程故障（malformed/empty/drop/dup/extra/503/401/延迟），记录每个请求
  payload 供 §57 输入不变性验证。
- `samples.py`：日/韩混合文本、双页上下文、术语表（先輩/倒す/마법）。
- `test_protocol.py`：20 例（含故障注入、预算截断、显式 fallback 链、
  时延/Token 测量，以及 Review R-001/R-002/R-003 的回归 5 例）。
- `run_experiment.py`：S1~S8 场景机读结果 → `results.json`。
- **`results.json` 的 `latency_ms` 是易变字段**（运行期测量值，每次复跑都会
  不同）：比对"与提交版本一致"时必须排除该字段；可指纹化的确定性证据是
  `kind` / `retryable` / `payload_hash` / `context_truncated_pages` / `match`
  等其余字段（Review R-101）。

## 结论速览（详见 ../../doc/research/TASK-017.md）

- RegionID 契约可在 mock 层完整校验：5 类违约全部正确分类且判定为可重试；
- D06 §57 输入不变性：重试前后 payload hash 一致（S2，payloads_identical=true）；
- D06 §54：客户端按构造单端点，无自动跨 Provider fallback；显式链 provenance
  可记录（S8）；
- 预算截断只丢上下文页（S1/S 截断用例）；
- 真实端点层 NOT_RUN：术语一致性/质量的模型评分无法声称。
