你是本 Task 的独立、非作者 Reviewer（DeepSeek Harness）。请仅基于下面明确列出的冻结输入，对 H2 新时点 evidence 是否影响 H1 当前结论作只读静态 Review。不要修改任何文件，不要运行脚本或命令；不需要重复核验 H2 的 55 checks、78 observations 或全部 JSON Pointers，那些已由 H2 DSH R3 Review 和 Codex adjudication 接受。

项目根目录：G:/CODEX/New Manga
Task：P02PRE-R1H-H1-CURRENT-INPUT-REVIEW
Task contract snapshot：verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/task-contract-r1.md
输入冻结 manifest：verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/review-inputs-r1.json
H1 subject Task snapshot：verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/h1-subject-task-r1.md
H2 Task snapshot：verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/h2-run-task-r1.md

请逐项读取 review-inputs-r1.json 所列的精确路径，尊重每项 SHA-256/bytes pin；不要扫描仓库或读取 manifest 未列出的历史资料。H1 的旧 Review 与 Codex adjudication 记录：v2 为 PRE_RUN_PASS，但 15 个 checks 的 evidence 指针为 collection A/B、v2 precheck、write script guard，无法在当时固定的 13 项 inputs 中解析，因此 P2-1 被接受并保持 OPEN。H1 Review 是 CHANGES_REQUESTED（P2=1，P3=6）。H2 是 2026-10-13 的独立新时点运行，R3 Review 与 Codex adjudication 已 APPROVED；H2 明示 NEW_TIME_EVIDENCE / CANNOT_SUBSTITUTE_V2_TIME_EVIDENCE。

审查问题：H2 的任何具体 observation 能否构成 H1 v2 原始 15 个引用的确定来源？必须同时证明同一时间点、同一操作/输入及 item-level provenance，或给出冻结证据可复算的确定映射。对以下 15 个 H1 IDs 逐项做 applicability 表：tools、a-identity、b-registry-wer-localdumps、b-profile-moniker、c-temp-paths、e-root-refs、e-owner-refs、e-agy-refs、e-root-status、e-owner-status、e-agy-status、e-root-index-hash、f-protected-file-pin、h-targets-initial、h-targets-final-prewrite。引用具体输入路径/字段和限制；相似名称或后来观察不等于同一时点原始来源。

请给出适用于本 Task 的 verdict（APPROVED_STATIC_CONTENT 表示本次适用性裁决没有未解决的 Review finding，不代表 H1 通过；如输入问题则 CHANGES_REQUESTED；无法审查则 BLOCKED）、P0–P3 findings 计数与逐项说明、H1当前 Review状态/P2-1状态/X6 eligibility 的建议、事实依据与审查限制。除非证据明确支持，不得改写 H1 的 PRE_RUN_PASS 或把 P2-1 标为 closed；不要建议重跑 H1 pre-run、H2 collector 或执行 executor 来补证据。
