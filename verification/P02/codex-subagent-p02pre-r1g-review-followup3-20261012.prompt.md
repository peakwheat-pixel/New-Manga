# P02PRE-R1G Review follow-up 3 — 独立复审 R-009/R-010 修复

## 冻结目标

- Task: P02PRE-R1G
- Base: cddff58469b56e181019a8ddfeade80684bc7eb9
- Reviewed branch: agent/antigravity/P02PRE-R1G
- Reviewed HEAD: 946938bd0696dfddd01f87d61fe6723c63ecdc86
- Owner: Antigravity（不是 Reviewer）
- Integrator/Adjudicator: Codex /root
- Review type: 非作者独立静态内容 Review；只审查下面列出的 exact files。

## 只读输入清单

1. G:\CODEX\New Manga\doc\tasks\P02PRE-R1G.md
2. G:\CODEX\New Manga\verification\P02\p02pre-r1g-manifest-20261011.md
3. C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga\verification\P02\p02pre-r1g-capture.ps1
4. C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga\verification\P02\p02pre-r1g-author-selfcheck-20261011.json
5. C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga\verification\P02\p02pre-r1g-antigravity-handoff-20261011.md
6. G:\CODEX\New Manga\verification\P02\codex-subagent-p02pre-r1g-review-followup2-20261012.md
7. G:\CODEX\New Manga\verification\P02\p02pre-r1g-review-followup2-adjudication-20261012.md
8. G:\CODEX\New Manga\verification\P02\antigravity-p02pre-r1g-review-fixes3-20261012.prompt.md
9. G:\CODEX\New Manga\verification\P02\antigravity-p02pre-r1g-review-fixes3-20261012.stdout.json
10. G:\CODEX\New Manga\verification\P02\p02pre-r1g-r009-r010-delivery-adjudication-20261012.md
11. G:\CODEX\New Manga\doc\templates\REVIEW.md

Codex 独立冻结以上 exact input pins 于 verification/P02/codex-p02pre-r1g-review-input-pins-followup3-20261012.json。此文件是 Codex-owned pin manifest；不需要 Reviewer 计算 hashes。只做内容审查。

## Review 范围与验收问题

1. R-009：当任一冻结 WER directory record 为 REPARSE_POINT 或 NOT_DIRECTORY 时，WER phase 和 werQueriedFields 是否立即 FAILED，是否明确记录 stop reason/detail，且是否在进入 protectedHashes / aclStability 前 fail-fast？是否仍保留原 QUERY_ERROR / ACL_QUERY_ERROR 行为，且没有跟随 reparse point 或新增查询？
2. R-010：serialization exception fallback、bounded partial 再超 64 MiB fallback、New-PartialEvidence 是否都使用固定有限 phase map；key 是否覆盖全部阶段且缺失值为 NOT_REACHED；是否保留 underlying/original stop fields、PARTIAL_EVIDENCE 分类且未注入无界 Result/inventory？
3. 修复是否仅限 Task 授权的三文件，是否兼容现有 manifest、Handoff 与 AC？静态证据、作者自检声明与未运行项是否清楚区分？
4. 有没有发现新的 P0/P1/P2/P3 风险、遗漏的边缘情况或会阻断后续 parser/self-check 的代码问题？只报告可由所列冻结输入支持的发现。

## 严格边界

- 只读取上面 11 个 exact files；不可访问其他路径。
- 不运行命令、脚本、测试、parser、自检、preflight、capture 或 getter；不计算 hash。
- 不搜索、glob、grep、枚举目录或调用 sub-agent。
- 不写入或修改任何文件；不要访问、stat、hash 或查询 .tmp.driveupload。
- 只对内容给 verdict；不声称 OS、runtime、AC、Gate 通过。
- 报告必须包含固定 base/head、verdict、P0/P1/P2/P3 计数、每项 finding 的级别/位置/影响/建议、逐项 R-009/R-010 disposition、未验证限制与推荐下一步。
