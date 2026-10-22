# DeepSeek Harness 独立静态 Review：P02PRE-R1H-R6-EXEC-A6

## Reviewer 与固定审查对象

- Task：`P02PRE-R1H-R6-EXEC-A6`
- Author/Owner：Antigravity（reviewer 必须与作者不同）
- Reviewer：DeepSeek Harness
- Adjudicator/Integrator：Codex /root
- Base / reviewed HEAD：`343895fb5f0329c0c07a7104ec321b698f967607`（本 Task 明确禁止 stage/commit；固定交付快照由以下 3 个 SHA-256 唯一标识）
- Worktree：`C:\Users\49745\.codex\worktrees\p02pre-r1h-r6-exec-a6-antigravity\New Manga`

请审查且只审查此三个文件：

1. `verification/P02/p02pre-r1h-round6-integrator-attempt6-20261012.ps1` — 43464 bytes / SHA-256 `4A566917F0D4A64F3D885C181ADD778C3F8547D4249EDAF96179AE0D690D90F5`
2. `verification/P02/p02pre-r1h-round6-integration-protocol-attempt6-20261012.md` — 12990 bytes / SHA-256 `677908FC00931FF411DC5D055EE41F6F6EC26B20826E1C3307DA82047AAE0E9E`
3. `verification/P02/p02pre-r1h-round6-attempt6-exec-handoff-20261012.md` — 12558 bytes / SHA-256 `AEEAD4C9D57C3165B85E2E61C517BD156EC8A5EC824533BA3CA99A5727C2E2CB`

以上 SHA 是 Codex 派发前的精确候选 pin。若你实际观察到字节/哈希不同，报告 `BLOCKED_BY_PIN_MISMATCH`，不要自行选择另一版本。

## 必读来源

只读访问以下固定输入，不要搜索/枚举目录：

- A6 immutable Task contract：`G:\CODEX\New Manga\verification\P02\agy-p02pre-r1h-r6-exec-a6-task-contract-20261012.md`（3553 bytes / SHA-256 `D4D8978D262205DA15096EB088F2A2E7C636D2828D4C9ED4AF8B075C6A32B838`）
- A6 immutable input manifest（25 项 A4/A5/history inputs）：`G:\CODEX\New Manga\verification\P02\agy-p02pre-r1h-r6-exec-a6-input-manifest-20261012.json`（7332 bytes / SHA-256 `475692A0248C69AF9B65731F4832179019553694102B7533105305C49B313813`）
- Codex pre-review pin verification：`G:\CODEX\New Manga\verification\P02\codex-p02pre-r1h-attempt6-review-input-verification-20261012.json`（25/25 输入匹配；文件 SHA-256 `79427602508B8AD42F22482859F9C80EBAB3B2BA88EB7B9E58EBB4C65DB25F07`）。这是 Codex 的验证证据，不等于你的独立 hash attestation。
- A5 accepted-findings adjudication：`G:\CODEX\New Manga\verification\P02\codex-p02pre-r1h-attempt5-prerun-review-adjudication-20261012.md`
- A5 execution-review adjudication：`G:\CODEX\New Manga\verification\P02\p02pre-r1h-attempt5-exec-review-adjudication-20261012.md`
- A5 execution protocol/source/Handoff 与 A4 inherited sources：由上述固定 input manifest 精确列出。特别核对真实 Owner Handoff 的來源 pin：`C:\Users\49745\.codex\worktrees\p02pre-r1h-codex\verification\P02\p02pre-r1h-handoff-20261012.md`，9505 bytes / SHA-256 `E13C7148B79740927692D9282C4F474FEE4AADD50BFBE256509CACA3052786B1`。

当可访问上述文件时，请报告实际读取/复核的输入；无法访问或独立 hash 命令失败时，保留 `NOT_VERIFIED`，不要推断通过。Root worktree 有大量原作者未提交文件；不要写入、暂存、提交或清理任何文件。

## Review 标准与重点

按 immutable A6 contract 的 Acceptance Criteria 审查最小必要改动、协议与交付证据，并逐条处理 A5 adjudication 接受的发现：

- P1-1：实际 Owner Handoff raw-byte pin 的来源、9505 bytes 与 hash 是否准确；它是否只是显式、受控的只读输入。
- P1-2：immutable Review contract 是否与 mutable Task status 分离；pin 集合是否稳定且复核时不会依赖可变状态元数据。
- P2-1：fail-stop 后未采集到的 profile/registry/ACL/system state 是否诚实保持 `NOT_VERIFIED / UNPROVABLE`，没有用“未运行”推断“未变化”。
- P2-2：源码 Parser/纯内存验证与 runtime `selfcheckEvidence`/`engineEvidence` 是否分离；Owner 阶段 runtime 证据是否仍 `NOT_RUN`。
- P2-3：A4/A5 继承 executor、protocol、Handoff、manifest、checkpoints、adjudications 与实际 root Owner Handoff 是否纳入 exact input manifest/pins。
- P3-1：observed/expected SDDL 是否逐字保存；无法验证时是否标 `NOT_VERIFIED`。
- P3-2：缺失的 malformed helper argv/stderr/exit 是否保持缺失而未重建；`.tmp.driveupload` 是否保持 `NOT_VERIFIED` 且没有被访问。
- P3-3：`checkpointIncludedInInputPins=true` 是否明确且该 checkpoint 真正被 hash-pin。
- P3-4：输出 absent check 是否为 pre-write snapshot；Codex disposition 与 OS process exit 是否区分；“helper invocation”措辞是否准确。

再检查：写权限/允许路径是否扩大；PowerShell executor 的参数、异常、输出、身份、路径、ACL、child-process 与一次性执行边界是否被意外放松；协议/脚本/Task contract/Handoff 是否互相矛盾；`git diff --check` 和 Parser 声称是否有相应可审证据。A6 Owner 声称在 PS7.6.6 完成 Parser-only 语法检查，但该结果是否能独立复核须按实际日志分类，不能把声明自动当作证据。

## 严格 Review 执行边界

这是**只读静态 Review**。不得修改任何文件、创建 Review 文件、stage/commit、执行或 dot-source PowerShell/Python/其他脚本、运行任何测试、调用 OS/API/registry/profile/ACL、创建子进程、执行 Build/Cargo 或 AC1–AC7；不得读/访问 `.tmp.driveupload`。不得进行宽泛目录枚举、glob 或发现性搜索；仅打开本提示中明确列出的路径及 manifest 中精确列出的源路径。

## 输出格式

在 stdout 返回完整 Review 报告，不落盘。报告至少包含：

1. `reviewed_head` 与 3 个固定候选文件 hash 的 match/mismatch 结果；实际读取的输入与独立 hashes 的状态（若不能 hash 则写 `NOT_VERIFIED`）。
2. 决策：`APPROVED_STATIC_CONTENT` 或 `CHANGES_REQUESTED`；如无法固定精确交付快照则 `BLOCKED_BY_PIN_MISMATCH`。不得使用其他自创批准态。
3. P0/P1/P2/P3 数量；逐条 finding 表（ID、级别、文件/行、触发与影响、证据、建议、是否阻断）。没有问题时明确写“在本次固定静态范围内未发现问题”，不能留模板行。
4. Architecture 与 Verification 两方面结论；列出未运行项目并标为 `NOT_RUN`。静态 Review 不是运行证明或 Gate。
5. 对上述九项 A5 accepted findings 逐项给出 resolved / unresolved / not verifiable 与证据。
6. 方法偏差、未读取输入、不可验证 claims、剩余风险；严禁把 A6 review 解释为 Build Gate、AC 或 private registry technical condition 通过。

任何未解决 P0/P1/P2 都必须 `CHANGES_REQUESTED` 并阻止下一步 Parser/final-pre-run。只有无未解决 P0/P1/P2，且关键静态证据固定，才可以 `APPROVED_STATIC_CONTENT`。Codex 会独立复核 pins 并作最终 adjudication。
