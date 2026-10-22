# P02PRE-R1H-H2-COLLECTOR — R6 Codex adjudication

日期：2026-10-13  
被审精确 identity：code 3e3fcae4a578e68adaa1aed929b69ddbb5c89304；docs/worktree 39ff1d3f94d98165c603c7c0f5e051ebcae3feae。  
DSH verdict：APPROVED_STATIC_CONTENT。DSH exit 0、stderr 0；其 pwsh/Git 复算被 sandbox 拒绝（一次尝试，未绕过）。Codex 独立复算 review manifest 的 19/19 项 SHA-256/byte 全匹配，Owner worktree clean/head 正确。DSH 报告、post-pins、raw JSONL 和 dispatch metadata 均已固定。

## 决定

CHANGES_REQUESTED，进入最小 R7 修订。R5 adjudication 要求的三项修正均已闭合；R2/R3/R4/R5 已审查范围无回归。DSH 报告没有 P0/P1/P2，两个新 P3 属于可低成本修复的测试可靠性缺口。考虑到该 Task 已冻结 exact mapping 的反转判别与稳定自检要求，Codex 将这两个 P3 提升为 R7 必修；不扩大生产 collector 行为或运行范围。

## R7 必修

1. R6-CX-01（DSH P3-1，fallback 分支缺少隔离测试）：现有 r604-fixed-chain-blocked-reason-maps-to-exit-4 的 message 本身匹配 *Fixed path-chain validation failed*，未实际覆盖仅由 BlockedReasons 命中的分支。新增最小纯测试：中性 message + CHECK_FAIL:path-chain-fixed-paths 必须得到 exit 4 / BLOCKED_BY_FAILED_CHECKS；中性 message + unrelated check reason 必须仍为 exit 5 / BLOCKED_EXCEPTION_FAIL_CLOSED。保留现有生产映射、原始 reason 与其它回归断言。
2. R6-CX-02（DSH P3-2，revisionNote 断言范围过宽）：当前 selftest 将 source-review-r3-adjudication 禁止条件作用于整个 collector 文本。改为只提取/检查 revisionNote 赋值内容，同时继续拒绝其自称 R4 repair 并要求引用 R4/R5 adjudication；避免未来无关历史注记使测试误报。

R7 Owner 为 Antigravity，Reviewer 为 DeepSeek Harness。代码修改只限当前 Owner Task allowlist 中的两份脚本；Owner Task/Handoff/新 Parser/selftest logs 可按同一 allowlist 更新。先提交代码，再提交固定 Handoff/Task/logs；PS 7.6.6 Parser 与纯 selftest 必须通过。之后对新 exact code/docs head 做 DSH 非作者静态复审并由 Codex 复核 pins。H2-RUN 继续 proposed；禁止 live collector、registry/WER/ACL/profile 查询、executor、Build/Cargo、AC1–AC7、Sandbox 和 .tmp.driveupload 访问。

## 接受且非阻塞的既有边界

1. null/null classifier input 在生产调用不可达；若意外出现则异常由外层 catch fail-closed，不会被伪装为 absence/PASS。
2. Test-PathAncestorsOrdinary 的可选 LinkTarget 读取异常细节不单独保留；reparse 已先记录并触发链 gate FAIL，仍早于 snapshot/launcher，不解引用或放行。

上述两项沿用 R5 adjudication，不要求 R7 修复或重新裁决。

## 证据

- DSH R6 exact-head report：dsh-source-review-r6.md
- Codex post-review verification：source-review-r6-input-verification.json（19/19）
- DSH raw JSONL/dispatch：G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-COLLECTOR/repair-r6/independent-review/
- Codex independent Parser/selftest：codex-r6-independent-verification.json 与该目录的完整日志