# M2-RC1 Review 派发记录（DSH headless，reviewed head f8ce10a2）

- 派发时间：2026-09-27（Owner 交付当日，按用户指令"完成后交 DeepSeek Harness 对固定 head 独立 Review"）
- 派发者：ZCode 会话（协议 §6.1 CLI 路径）
- 派发命令：`dsh --profile headless --json "$(cat %TEMP%\m2rc1-review-prompt.txt)"`
- **exit code：0**
- **session ID**：`session-dec2cbeb-6fc4-445b-acda-3126ba79c5c0`（304 事件）
- 原始 JSONL：`%TEMP%\m2rc1-dsh-review-run.jsonl`

## Review 结果（引自 DSH final 消息）

- 报告：`doc/reviews/M2-RC1-f8ce10a2.md`（346 行，已由 Owner commit `87ddc878` 原字节导入）
- **决定：`changes_requested`**（1×P1 + 4×P2 + 7×P3）
- 环境限制：DSH 沙箱 SHELL_UNAVAILABLE（`SetNamedSecurityInfoW Win32 5`，同 M2-C2/M2-S3）→ 全部复跑 BLOCKED；以主仓 reflog + Owner diff 转录 + 工作区清点 + 逐行阅读替代
- 范围：PASS/间接（41 条交付清单全授权路径、无产物文件、amend 由 reflog 证实；F-11 指出 Handoff"30 文件"与证据 41 条矛盾——P3）
- 证据自洽：PASS（fixture SHA 与两轮结果一致、35 pytest 计数经 .pytest_cache 交叉证实）
- 诚实边界：PASS（S1-B3/B6/B8 NOT_RUN、冷缓存未称达标、无产品级安全宣称）

## Findings 摘要（详情见 review 报告 §编号）

| ID | 级别 | 要点 |
|---|---|---|
| F-01 | **P1（阻断）** | `resource_protocol.rs:439-454` grant 缓存命中时不调 Core resolve，缓存无 TTL/撤销字段 → `issue→fetch→revoke→fetch` 仍 200，违反 T6 立即撤销与 AC3；E-04 与 Rust 单测的调用顺序恰绕过该窗口 |
| F-02 | P2 | 首验后 digest 不再校验，与 Python adapter 语义不一致 |
| F-03 | P2 | `register_catalog`/`probe_*`/`ttl_override` 对 WebView 开放，CSP=null、capabilities 为空 |
| F-04 | P2 | T3 热缓存用 49 KB fixture 证明 ≤25 MiB 目标（量级不足） |
| F-05 | P2 | sidecar 经 `infrastructure/__init__.py:3` 传递性导入产品模块 |
| F-13 | P2 | AC3/AC4 的只读/open-once/读后复核/T2 真实上限/在途 revoke 实际未覆盖 |
| 7×P3 | P3 | 错误码豁免未记录、双实现差异、配额语义混用、缓存无界、文件数矛盾、证据可复现性、测试工程 |

## DSH 建议的修复路径（M2-RC1-FIX）

- 修复 Owner：ZCode；必修 F-01/F-02；准入项 F-04/F-11/F-13；其余逐项 disposition
- 修复后由非作者复核 review 报告 §11 清单再转 approve；随后 Codex 集成
- 可转发指令全文见 DSH final 消息（`%TEMP%\m2rc1-dsh-review-run.jsonl` 的 final 事件）与 `doc/reviews/M2-RC1-f8ce10a2.md` §11
