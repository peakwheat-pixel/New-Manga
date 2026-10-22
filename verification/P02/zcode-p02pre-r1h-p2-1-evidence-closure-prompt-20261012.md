# ZCode 内置 Agent dispatch：P02 H1 P2-1 evidence closure

请在 ZCode 对话中使用**内置 Agent dispatch**，执行任务 `P02PRE-R1H-P2-1-EVIDENCE-CLOSURE`。本文件是待派发的 immutable prompt；Codex 尚未、也不能从当前任务调用 ZCode CLI。收到后请由 ZCode 启动 Agent 并记录实际 session ID，不要把本文件或 Task 登记误报为已派发。

## 目标

只读追溯 H1 v2 final pre-run 的 15 个 generic `checks[].evidence` pointers，寻找符合要求的 item-level raw source，或能从冻结输入中确定性复核的精确 source span。不能找到全部 15 项时，交付 `BLOCKED / P2-1 OPEN` 报告；不得用 JSON observed 值、作者声明、聊天记录或无原始采集内容的 summary/template 充当 raw evidence。

## 执行位置与角色

- Project root：`G:\CODEX\New Manga`
- ZCode Owner worktree：`C:\Users\49745\.codex\worktrees\p2-p2-1-zcode\New Manga`
- Branch：`agent/zcode/P02PRE-R1H-P2-1-EVIDENCE-CLOSURE`
- Base/head at dispatch preparation：`343895fb5f0329c0c07a7104ec321b698f967607`
- Task：`doc/tasks/P02PRE-R1H-P2-1-EVIDENCE-CLOSURE.md`（size 5617 / SHA-256 `35FDFBBB966F9A3D684E079415519AF8819094494F13A7505396992EFA77E844`）
- Owner=ZCode；Reviewer=DeepSeek Harness（不得自审）；Integrator/Adjudicator=Codex `/root`。
- 只读查找源材料；任何新报告、Task 更新或 exact-byte source copy 只写入 Owner worktree 的 Task allowlist 路径。

## 15 项待追溯列表

| v2 JSON line | check id | 当前 generic evidence label |
|---:|---|---|
| 172 | `tools` | `collection A` |
| 180 | `a-identity` | `collection A` |
| 188 | `b-registry-wer-localdumps` | `collection A` |
| 196 | `b-profile-moniker` | `collection A` |
| 204 | `c-temp-paths` | `collection A` |
| 244 | `e-root-refs` | `collection B` |
| 252 | `e-owner-refs` | `collection B` |
| 260 | `e-agy-refs` | `collection B` |
| 268 | `e-root-status` | `collection B` |
| 276 | `e-owner-status` | `collection B` |
| 284 | `e-agy-status` | `collection B` |
| 292 | `e-root-index-hash` | `collection B` |
| 300 | `f-protected-file-pin` | `collection B` |
| 324 | `h-targets-initial` | `v2 precheck` |
| 348 | `h-targets-final-prewrite` | `write script guard` |

## 冻结输入 pins

以下 13 项是 DSH H1 Review 的原始 frozen input set。复核当前仍冻结的输入 size/SHA-256；任意异常差异即停止并报告。唯一例外是 H1 Task：原输入的历史 pin 由 Codex verification artifact 记录，当前 Task 已追加后续状态，不能与旧 hash 比较；核对 verification artifact 中其 pre/post 记录，并把 current-vs-historical 区别写入报告。不得修改任何输入。

| 输入 | 路径 | bytes | SHA-256 |
|---|---|---:|---|
| v2 JSON | `G:\CODEX\New Manga\verification\P02\codex-p02pre-r1h-attempt6-final-pre-run-v2-20261012.json` | 15768 | `23AC80E2B671ACB616CD89A11FDEE5C0548547F97C8C529B1FC11AF67EDAF877` |
| v2 stdout | `G:\CODEX\New Manga\verification\P02\codex-p02pre-r1h-attempt6-final-pre-run-v2-20261012.stdout.log` | 82455 | `87D03E50ADCF56DD512D97A26EB1964D605E8259AD8AC874E2B6B9DC810394B3` |
| v2 stderr | `G:\CODEX\New Manga\verification\P02\codex-p02pre-r1h-attempt6-final-pre-run-v2-20261012.stderr.log` | 532 | `4476997D2D7278B3F4ADF890E94C553B67411B5AE21BAA85DFB626F8A9CDEC13` |
| v2 exit | `G:\CODEX\New Manga\verification\P02\codex-p02pre-r1h-attempt6-final-pre-run-v2-20261012.exit` | 2 | `9A271F2A916B0B6EE6CECB2426F0B3206EF074578BE55D9BC94F6F3FE3AB86AA` |
| attempt1 JSON | `G:\CODEX\New Manga\verification\P02\codex-p02pre-r1h-attempt6-final-pre-run-20261012.json` | 12984 | `D698E5FB8E322D2D7459D09EA62A02D866C48B8F2B7DF9CDDB47ACC1FE812786` |
| attempt1 stdout | `G:\CODEX\New Manga\verification\P02\codex-p02pre-r1h-attempt6-final-pre-run-20261012.stdout.log` | 3704 | `61A3DD58DFE94DB714ED00115C934623BEE434C0148ABE16DF73ED47A4A5FC77` |
| attempt1 stderr | `G:\CODEX\New Manga\verification\P02\codex-p02pre-r1h-attempt6-final-pre-run-20261012.stderr.log` | 1237 | `990FAAF1A2E35F5D5486EFD36CD4D82BA081F81E42499320D8B689DBB9F42C16` |
| attempt1 exit | `G:\CODEX\New Manga\verification\P02\codex-p02pre-r1h-attempt6-final-pre-run-20261012.exit` | 2 | `9A271F2A916B0B6EE6CECB2426F0B3206EF074578BE55D9BC94F6F3FE3AB86AA` |
| H1 Task as DSH reviewed | `doc/tasks/P02PRE-R1H-R6-ZCODE-H1.md` at review time | 21762 | `13D85D6B46F8904BCBD3AAB07657094D5BD8D9C1DA931449693FC30B2B14C009` |
| frozen A6 Task | `G:\CODEX\New Manga\doc\tasks\P02PRE-R1H-R6-EXEC-A6.md` | 25479 | `43E72628968B0CC37C6F2C5EC897B3534AB558A65F4AD3878B4FDB76F2FBD390` |
| frozen protocol | `C:\Users\49745\.codex\worktrees\p02pre-r1h-r6-exec-a6-antigravity\New Manga\verification\P02\p02pre-r1h-round6-integration-protocol-attempt6-20261012.md` | 14084 | `DDDFDF58C5684B4F9992E09F45D7BB53CEEB733D1DA8277CA103F83CDA244142` |
| frozen Handoff | `C:\Users\49745\.codex\worktrees\p02pre-r1h-r6-exec-a6-antigravity\New Manga\verification\P02\p02pre-r1h-round6-attempt6-exec-handoff-20261012.md` | 13190 | `6F1E908C64ADBEB99AA8E827B1E4B43CA804635B317DB5056514C613A943E949` |
| frozen executor (read-only; never run) | `C:\Users\49745\.codex\worktrees\p02pre-r1h-r6-exec-a6-antigravity\New Manga\verification\P02\p02pre-r1h-round6-integrator-attempt6-20261012.ps1` | 43527 | `1C8D6220E85608977BCDCC27B86E4DC227DBA11F5E7179A09328C142036502EE` |

The H1 Task pin above is the exact historical DSH input. The live H1 Task has since received current-state updates and is **not expected to match** that historical pin. Its original bytes are not available as a separate file in the current root; rely on the Codex input-verification record for the historical pre/post check. Use the DSH response/adjudication for the reviewed finding; do not claim the live H1 file is the old input.

Read-only review context (not part of the 13 original pins): DSH response `verification/P02/dsh-p02pre-r1h-attempt6-zcode-h1-final-pre-run-review-20261012.response.md` = 14078 / `6AAD7750AFABCCD5B159C69F40EF49149E3D3EBB1CA6613CD0FD91FDCB960C19`; Codex input verification `verification/P02/codex-p02pre-r1h-attempt6-zcode-h1-review-input-verification-20261012.json` = 14002 / `7B823A05313DA2B053C76B81744667BF041B8FD9AF0933F1162DCDADFB372515`; Codex adjudication `verification/P02/codex-p02pre-r1h-attempt6-zcode-h1-review-adjudication-20261012.md` = 7665 / `9D4B95DA5263B0C52A3621748E875760CAAADF153ED5C39BDA5955520DF57232`.

Closure Task pin: `doc/tasks/P02PRE-R1H-P2-1-EVIDENCE-CLOSURE.md` = 5617 / `35FDFBBB966F9A3D684E079415519AF8819094494F13A7505396992EFA77E844`.

## 已知线索（不是 closure 证据）

- DSH 在报告中说明：13 个冻结输入内只有 v2 JSON 自身出现 `collection A` / `collection B` 标签；v2 stdout 有 summary 和 status snapshots，但没有明确的 item-level 原始采集分节。
- 本次 Coordinator 在 `%TEMP%` 检查到的 v2 checks/template/stdout/stderr 暂存物没有新增 item-level capture；stdout/stderr 暂存物与 pinned v2 输出同 hash。相应临时目录为空。请仍做受限只读复核，但不做全盘扫描。
- `e-root-status` 与 `e-agy-status` 可能有 stdout raw status spans；仅在补齐可验证的 source span、命令/时间/来源上下文后才可提 closure candidate。JSON summary 本身不等于 raw evidence。

## 边界

- 不运行或 dot-source frozen executor；不重跑 final pre-run、任何 collection command 或并行任务；不生成替代证据。
- 不改写、覆盖、删除、重命名、stage 或 commit attempt1/v2、A6 Task、protocol、executor、Handoff、DSH Review 或既有 adjudication。
- 不调用 `File.Replace`、ProcessObserver/ProcessSnapshot/native Toolhelp、profile/registry/ACL 写 API、capture、Build/Cargo、AC1–AC7；不查询/安装/启用/启动 Windows Sandbox；不派 Qoder；不调用 ZCode CLI。
- 不访问 `G:\CODEX\New Manga\.tmp.driveupload`。不 reset/clean/stash。只读扫描范围仅限上述 P02 inputs、Agy delivery worktree 的冻结源，以及 `%TEMP%` 里与 P02 attempt6 时段相关的候选目录/文件。
- 若任何 pin 不匹配或无法确定时间/身份/来源，stop and report `BLOCKED / P2-1 OPEN`；不要自行扩大权限或重跑。

## 输出

在 ZCode Owner worktree 仅修改 Task 和 allowlist 下的 evidence 文件。报告路径=`verification/P02/zcode-p02pre-r1h-p2-1-evidence-closure-report-20261012.md`，逐项填 15 行 source map：check ID、合格/不合格、source path、line/JSON Pointer、size/SHA-256、来源时间/身份与理由。若发现合格的仓库外 raw file，先确认对应 recovered-source 目标 absent/unignored，再以 CreateNew 原样复制并复核哈希。

若有任一项没有合格来源，报告必须为 `BLOCKED / P2-1 OPEN`，列出未闭合项，交 Codex 决定是否需要新的授权范围；不得发 DSH review。仅当 15/15 均具备可复核来源后，停在 `CLOSURE_CANDIDATE / AWAITING_CODEX_PIN_VERIFICATION`，由 Codex 验证新 pins 并派 DeepSeek Harness focused independent Review。不得标成 H1 accepted、X6 ready 或 Build Gate pass。
