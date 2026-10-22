# DeepSeek Harness 独立只读 Review — P02PRE-R1F / R1F-R7 cohort #9（fixreview8）

## verdict

`CHANGES_REQUESTED`（P0/P1/P2/P3 = **0 / 1 / 1 / 1**）

- 本轮 Task 指定的 cohort #7 两项 P3 修复、exit path integration 记录、cohort #8 `NOT_DISPATCHED / NOT_REVIEWED` 事实、Gate/PowerShell 表述，经文本级核对**均正确且一致**。
- 但存在 3 项缺陷：(1) cohort #9 的预留目标已实际落盘，与 manifest/Acceptance Criteria/Release procedure 的 "PLANNED / 尚未生成 / 不存在" 记录直接冲突；(2) 本轮 stdout/stderr 正被追加写入规范证据文件，构成自我引用与不可重跑的证据完整性风险；(3) checkpoint 及 INDEX/README 的 status 快照已过期，与当前冻结值冲突。

严格说明：以下是**纯文本检查**。本轮未运行任何命令、Git、hash/API、host getter、profile、registry、ACL、capture、Build/Cargo 或 AC1–AC7；未创建/编辑/删除任何仓库文件（仅使用读取类工具 read/grep/glob）。

## Findings

### F8-1（P1）cohort #9 预留目标已存在，文档仍记 `PLANNED / pending`

- 路径/行：
  - `verification/P02/p02pre-r1f-manifest-20261011.md:114-118`（五行 `PLANNED | ... | pending | pending`）
  - `doc/tasks/P02PRE-R1F.md:54`（cohort #9 五项登记为待派发）
  - `verification/P02/codex-checkpoint-p02pre-r1f-20261011.md:17,46-47`（"确认五个输出 targets 不存在"，用 `CreateNew`）
  - `doc/REBASELINE_PLAN.md:42`（"确认 cohort #9 输出目标不存在 … 输出必须按精确路径 `CreateNew`"）
- 证据（观察）：`glob` 与 `read` 显示下列文件**已实际存在**：
  - `dsh-p02pre-r1f-r5-followup7-fixreview8-20261011.prompt.md`（存在，内容即本轮委托，1–51 行）
  - `dsh-p02pre-r1f-r5-followup7-fixreview8-20261011.stdout.md`（存在，读取时 0 行）
  - `dsh-p02pre-r1f-r5-followup7-fixreview8-20261011.stderr.log`（存在，48 行，正在增长）
  - `dsh-p02pre-r1f-r5-followup7-fixreview8-20261011.exit`（尚未出现）
- 判定：这不是"审查者臆测"，而是当前已发生的状态漂移。`CreateNew` 语义下面向**已存在**目标创建会直接失败；若 cohort #9 失败需重派，沿用同一路径将无法以 `CreateNew` 落盘。
- 最小修复：由 Codex（非本 Reviewer）在 adjudication 时据实把 #9 已生成项从 `PLANNED/pending` 更新为实际 `FROZEN + bytes/SHA-256`（含 stdout/stderr 最终 pin），并把 `.exit` 保留为待返回项；同时在 Task/checkpoint/Plan 把"输出目标不存在"改为"目标已创建、exit 待落盘"。不要删除或覆盖既有文件。

### F8-2（P2）本轮 stdout/stderr 追加写入规范证据文件 → 自我引用与证据完整性风险

- 路径/行：
  - `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview8-20261011.stdout.md`（0 行，读取时仍在写入）
  - `verification/P02/dsh-p02pre-r1f-r5-followup7-fixreview8-20261011.stderr.log:1-48`（内含本 reviewer 的逐步 reasoning 文本，包括对 findings 的草拟过程）
  - 对照：`...fixreview7-20261011.stdout.md` / `.stderr.log` 均为 **0 bytes**（cohort #8 未启动）；`...fixreview6-20261011.stdout.md:1-4` 为 JSONL 事件流、stderr 为 0。
- 判定（观察）：R1F 治理记录一贯把 stdout/stderr 定义为**进程结束后冻结的原始字节**（见 manifest:69、`fixreview6-adjudication:9` 的 `3 bytes / 13BF7B…`）。本轮却是"实时追加 + 自读自证"：reviewer 的推理既被写入被审证据文件，又被同一 session 读取。后果：(a) 证据文件在冻结前持续变化，bytes/SHA 无法在审查期确定；(b) reviewer 报告与证据文件互相引用，削弱"原始输出"的中立性；(c) 若进程异常终止，会留下与 cohort #8 空流同型的"半截证据"，且因 F8-1 无法再用 `CreateNew` 重派同名目标。
- 最小修复建议（供 Codex 判断，不替其裁定）：把每轮 DSH 的 stdout/stderr 落到**非规范临时目标**，进程结束后再以 `CreateNew` 复制/冻结到 manifest 登记的精确路径；或在 adjudication 中显式声明"stdout/stderr 为流式捕获、以进程结束时刻为冻结点"，并记录冻结时 bytes/SHA。至少在最终 adjudication 中记录冻结时点。

### F8-3（P3）checkpoint 与 INDEX/README 的 status 快照与当前冻结值冲突

- 路径/行：
  - `verification/P02/codex-checkpoint-p02pre-r1f-20261011.md:25`：`699 NUL / 45722 bytes / SHA-256 200F57D2…`
  - `doc/00_INDEX.md:7`：`693 NUL / 45270 bytes / SHA-256 BDEDFC9F…`
  - `doc/tasks/README.md:7`：`693 NUL / 45270 bytes / SHA-256 BDEDFC9F…`
  - 各文件自身"当前"段落：`STATUS:5,7`、`REBASELINE_PLAN:5,11`、`P02.md:24`、上个 grep 的 `00_INDEX.md:5`、`README.md:5` 均为 `704 / 46110 / 4055D234…`
- 判定（观察）：同一份文档内部，当前段与紧随其后的 Live Git 段给出**不同**快照。checkpoint 是被 Task/STATUS/Index/README/Plan 共同指定的唯一 recovery point，其 Live Git 段却停留在 cohort #7 派发后状态。算术可佐证其过期：`699 + 5（cohort #8 prompt/stdout/stderr/exit/adjudication = 6332+0+0+49+2785）= 704`，`45722 + 9166 ≈ 44888` 量级与 `46110` 相符（此为推理，非复算）。所有文档均声明"final pre-run 需重采"，故不构成发布阻塞。
- 最小修复：把 checkpoint:25 与 INDEX:7/README:7 的当前快照行更新为 `704 / 46110 / 4055D234…`，或显式标注为"cohort #7 派发后、#8 artifacts 前"的历史比较点。
- 附带观察（同属 P3 文本级，未单列 ID）：`doc/tasks/P02PRE-R1F.md:113` "当前 host capture | **Above one-time command** |" 的指代对象在本表内不存在（命令只在 manifest:59 与 Task:79 出现），此处行文为 dangling reference。doc 内其它位置（`:57`、manifest:57-59）均完整正确。

## 逐项核对结论（对应委托 1–8）

1. **cohort #7 原 findings**：Task:113 已要求"最新 R1F-R7 cohort Review=`APPROVED` 且 Codex adjudication 通过后，仍需 final pre-run adjudication 明确释放"，不再依赖 cohort #6 approval（F7-1 已修复）；STATUS:9 已将 #9 精确路径指向 `manifest/checkpoint` 并写明"pins 待建立后登记"，未声称 DAG 已列出（F7-2 已修复）。
2. **exit path integration**：`fixreview6-20261011.exit` 与少日期 sidecar `fixreview6.exit` 均存在、内容均为 `0`（按 pin 为 3 bytes / `13BF7B30…` / raw `30 0D 0A`）；Task:52、manifest:106-107（`FROZEN / NONCANONICAL` 单独标记）、checkpoint:35 三处均区分、保留、可追溯；Task:66 写入范围显式含该 sidecar 且注明"保留，不覆盖/删除"。文本一致。
3. **cohort #8 事实**：Task:53（AC 未勾选 `[ ]`）、manifest:109-113、checkpoint:9、`fixreview7-adjudication:7,11-13` 一致记为 `NOT_DISPATCHED / NOT_REVIEWED`：`FileNotFoundError (WinError 2)` 发生在进程创建前；stdout/stderr 为 0 字节启动器目标（非 reviewer 输出）；`.exit`（49 bytes / `5F9C0A8B…`，内容 `NOT_STARTED: WinError 2 before process creation`）明确标注为 Codex dispatch marker、非 CLI exit；无 DSH session/verdict。
4. **恢复路径**：Task:54、Plan:13,30,42、STATUS:9,13、Index:5、README:5、P02.md:24、checkpoint:17,44-48、manifest:63,114-118 一致指向 cohort #9/fixreview8 为唯一下一 READY；Owner=`Codex /root`、Reviewer=`DeepSeek Harness`、基线=`main@cddff58469b56e181019a8ddfeade80684bc7eb9`；五个精确目标路径在 Task/manifest/checkpoint 完全一致；新的 DSH 调用使用 `dsh.ps1` shim 且明确不复用 cohort #8 targets（checkpoint:9,17,47）。注：实际已非"未派发"，见 F8-1。
5. **manifest 结构**：checklist 表 `71-118` 行为连续单一 Markdown 表（`71-72` 表头+分隔，`73-113` 冻结项，`114-118` PLANNED），无空行中断；#1–#7 规范项为 `FROZEN` 并带 pins；#7 sidecar 单列 `FROZEN / NONCANONICAL`；#8 仅记 dispatch failure（`EMPTY_TARGET / NOT_DISPATCHED`、`CODEX DISPATCH MARKER, NOT CLI EXIT`、`NOT_REVIEWED`），未写成 review；#9 五项为 `PLANNED/pending`（该标签本身即 F8-1 的对象）。
6. **当前状态与历史不确定性**：唯一 Active 产品 Task=`P02`、Active 子 Task=`P02PRE-R1F`（STATUS:5、checkpoint:7、Plan:5 一致）；cohort #7 原 verdict `CHANGES_REQUESTED (0/0/0/2)` 在 Task:40,52、STATUS:5、manifest:124 完整保留；#8 无 verdict；#9 为下一 READY。`760/48780→688/44882` 在 Plan:5、STATUS:5,7、checkpoint:25、Index:5、README:5 均为 `UNKNOWN / NOT_VERIFIED` 且不推断归属；旧 checkpoint 活动区块逐字差异在 checkpoint:13 保持 `NOT_VERIFIED`。受控 status 关键字面一致为 `704/46110/4055D234…` 并排除 `.tmp.driveupload`——仅 checkpoint:25/Index:7/README:7 例外（F8-3）。
7. **Gate 与 boundary**：Task:62、manifest:53、Plan:17、STATUS:11、checkpoint:42、两处 adjudication 尾段一致保持 `private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、原句 `technical condition unmet; user explicitly accepted residual risk`，以及 Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`。各文档明确 Review/waiver/parse 均不解除 gate。
8. **PowerShell**：Task:33,36、manifest:27、checkpoint:19、Plan:19 一致：R8 为 Windows PowerShell 5.1.26100.9549 parse-only=`PARSE_OK`、`captureScriptInvoked=false`；PS 7.6.6 仅为补充 `Parser::ParseFile` syntax observation，不证明运行期兼容、不切换 reviewed executor contract。R8 JSON 全文核对内部自洽（source pin `67582/5A3FE118…` 与 Task/manifest 一致；`stderr` 空；`exitCode=0`；stdout 中 `captureScriptInvoked:false`）。

## 实际读取范围与未验证项

**读取（内容级）**：`doc/tasks/P02PRE-R1F.md`（全文 113 行）、`verification/P02/p02pre-r1f-manifest-20261011.md`（全文 159 行）、`codex-checkpoint-p02pre-r1f-20261011.md`（全文 142 行）、`doc/STATUS.md:1-120`、`doc/00_INDEX.md:1-40`、`doc/tasks/README.md:1-40`、`doc/tasks/P02.md:1-45`、`doc/REBASELINE_PLAN.md:1-45`、`p02pre-r1f-parser-…-r8-20261011.json`（全文）、`dsh-…fixreview8-20261011.{prompt.md,stdout.md,stderr.log}`、`dsh-…fixreview7-20261011.{prompt.md,stdout.md,stderr.log,exit}`、`dsh-…fixreview6-20261011.{prompt.md,exit}` 与 `dsh-…fixreview6.exit`、`dsh-…fixreview7-adjudication-…md`、`dsh-…fixreview6-adjudication-…md`、`p02pre-r1f-r5-followup7-fixreview2-adjudication-…md`、`dsh-…fixreview6-20261011.stdout.md:1-80`；另用 grep 定位核对 STATUS/INDEX/README/P02/Plan 与 manifest 相关行。

**未执行/未验证**：
- 未运行任何命令、Git、hash、API、host getter、capture、Build/Cargo、AC1–AC7；未读取任何未提交用户内容。
- **未独立复算任何 byte size 或 SHA-256**。pin 表与文件字节一致性系依据引用这些 pin 的文档（Task:31-36、manifest、checkpoint:31-36、Plan:13）之间的文本吻合；按 `NOT_VERIFIED` 处理独立 hash 校验。
- 未验证 `doc/STATUS.md`/`P02.md`/`Plan` 被截断后的剩余段落；未验证 manifest 声明的 `96 keys / 96 unique`（该清单在 `p02pre-r1f-capture.ps1` 内，未读取）。
- checkpoint:25 的 `699/45722` 与当前 `704/46110` 的差量归因（F8-3 中的 699+5=704）属**推理**，不是复算。

## 边界声明

本 Review 及任何 adjudication 均不释放 capture、Build Gate 或 Hard Build Barrier；cohort #7 原 verdict 与全部 Gate 事实原样保留。本 Reviewer 不替 Codex 裁定 findings、不编辑任何文件、不撰写 `p02pre-r1f-r5-followup7-fixreview8-adjudication-20261011.md`。
