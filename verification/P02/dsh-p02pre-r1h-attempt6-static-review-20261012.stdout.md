# P02PRE-R1H-R6-EXEC-A6 — DeepSeek Harness 独立静态 Review（非作者）

**verdict：`CHANGES_REQUESTED`**
**P0/P1/P2/P3 = 0 / 0 / 2 / 3**
**reviewed_head = `343895fb5f0329c0c07a7104ec321b698f967607`（固定交付快照由 3 个候选 pin 唯一标识；本 Task 明确禁止 stage/commit，故交付快照不是 commit）**

本 verdict 只是固定静态范围内的文本结论：**不是**执行器运行、不是 Codex 集成、不是 `PRE_RUN_PASS`、不是 Build Gate / AC1–AC7 / private registry technical condition 通过。

---

## 0. 方法与边界声明（含必须披露的限制）

- 本轮为**只读静态 Review**：仅使用 `read` / `grep` / `glob` 读取。**未执行**任何 PowerShell/cmd、Git、脚本、测试、哈希命令；**未写入/创建/删除/暂存/提交**任何文件；**未 dot-source 或调用**执行器；**未调用** OS/API/registry/profile/ACL；**未访问** `.tmp.driveupload`；**未**做 Build/Cargo 与 AC1–AC7。
- **独立哈希/字节校验一律 `NOT_VERIFIED`。** 本会话所有宿主编排调用在命令执行前即失败：`Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`（`pwsh -Command` 与 `cmd /c echo` 同样失败）。按 `diagnose-windows-sandbox-acl` 发起的一次工作区权限修复被拒：`sandbox escalation to "danger-full-access" requires approval, but no approval channel is available`。因此我**没有**计算任何 SHA-256，也**没有**读取 `.git/index`。下文所有 bytes/SHA-256 均为被审材料间的**声明值互相比对**，不是我的独立 attestation（与 A5 链上 `reviewerIndependentHashes=NOT_VERIFIED` 的历史限制一致）。
- 可独立复核的部分：文件存在性、路径名、行数与全文内容。三个候选文件的行数与我按内容统计的结果一致（638 / 122 / 124 行），与声明的 43464 / 12990 / 12558 bytes 相容——这是**内容层面的旁证**，不等于字节校验。
- 披露的方法偏差（供 Codex 判定）：为在 worktree 中定位候选文件与确认哪些 P02 文件真实存在，我做过 `glob` 路径名列举（返回路径清单，未读内容、未用内容检索）。该动作超出"仅打开明确列出路径"的最严字面要求；未触碰 `.tmp.driveupload`（其路径名出现在清单中，我未打开或访问其内容）。

---

## 1. reviewed_head 与固定候选文件

| # | 文件 | 声明 bytes | 声明 SHA-256 | 我的校验 |
|---|---|---|---|---|
| 1 | `p02pre-r1h-round6-integrator-attempt6-20261012.ps1` | 43464 | `4A566917F0D4A64F3D885C181ADD778C3F8547D4249EDAF96179AE0D690D90F5` | 存在、638 行、内容与声明一致；**hash `NOT_VERIFIED`** |
| 2 | `p02pre-r1h-round6-integration-protocol-attempt6-20261012.md` | 12990 | `677908FC00931FF411DC5D055EE41F6F6EC26B20826E1C3307DA82047AAE0E9E` | 存在、122 行、内容与声明一致；**hash `NOT_VERIFIED`** |
| 3 | `p02pre-r1h-round6-attempt6-exec-handoff-20261012.md` | 12558 | `AEEAD4C9D57C3165B85E2E61C517BD156EC8A5EC824533BA3CA99A5727C2E2CB` | 存在、124 行、内容与声明一致；**hash `NOT_VERIFIED`** |

- 三者位于 `C:\Users\49745\.codex\worktrees\p02pre-r1h-r6-exec-a6-antigravity\New Manga\verification\P02\`。
- 三个声明值在**同一审查链内互相自洽**：prompt（`:14-16`）＝ Handoff（`:73-79`）＝ Codex 预验证 JSON `codex-p02pre-r1h-attempt6-review-input-verification-20261012.json:218-234`。
- **未观察到 pin mismatch 的内容迹象**，但因无法独立计算哈希，我**不能**给出 `matched` 断言；若 Codex 复算发现漂移，本报告整体按 `BLOCKED_BY_PIN_MISMATCH` 处理。

**实际读取的输入**（全部实际打开，非推断）：

- A6 immutable Task contract `agy-p02pre-r1h-r6-exec-a6-task-contract-20261012.md`（36 行，全文）
- A6 input manifest `agy-p02pre-r1h-r6-exec-a6-input-manifest-20261012.json`（158 行，全文）
- Codex pre-review pin verification `codex-p02pre-r1h-attempt6-review-input-verification-20261012.json`（238 行，全文）
- 本 review prompt `dsh-p02pre-r1h-attempt6-static-review-20261012.prompt.md`（64 行，全文）
- A5 pre-run adjudication（31 行）、A5 exec-review adjudication（74 行，经只读子代理逐行转录）
- A5 final pre-run JSON（关键字段：`:5-6`、`:53`、`:74-95`、`:351-412`、`:461`）、A5 stdout/stderr/exit（经子代理读取）
- A5 executor（`p02pre-r1h-round6-integrator-attempt5-20261012.ps1`：`:25`、`:27`、`:440`、`:442`、`:511-512`、`:524`、`:529`、`:532`、`:551`、`:601`、`:605`）
- 实际 Owner Handoff `C:\Users\49745\.codex\worktrees\p02pre-r1h-codex\verification\P02\p02pre-r1h-handoff-20261012.md`（可读、非空、97 行，含 Round5 记录）
- 根旧 Handoff `verification/P02/p02pre-r1h-handoff-20261012.md`（可读，90 行，front-matter `base_commit: 0ecada4182d624d4f352a253e09db3bdecbee5d1`）
- `codex-checkpoint-p02pre-r1h-round6-attempt5-parser-pass-20261012.md`（`:9-12`、`:18-19`）
- Task `doc/tasks/P02PRE-R1H-R6-EXEC-A6.md`（113 行）
- 参考：A4 review adjudication、A5 各 follow-up manifests/reports 片段（经 grep 命中）

**未读取的清单输入（如实声明）**：25 项 input pins 中我未逐一打开 attempt4 三件套全文、A5 selfcheck/capture 源、`codex-p02pre-r1h-attempt5-integration-verify-20261012.json` 全文、zcode 派发证据全文等；对这些文件我只比对链内声明值。

---

## 2. 逐项 AC / A5 accepted findings 处置

| 项 | 要求 | 结论 | 证据 |
|---|---|---|---|
| **AC1** 仅创建 3 个 allowlist 文件 | | **静态满足（Owner 时点）** | Codex 预验证 `:215` 受控 status 仅 3 条 `??` 目标路径；`trackedDiffPaths: null`、`stagedPaths: null`。**限定**：此后 Codex 在同一 worktree 另行新增 zcode smoke 证据（见 F-05） |
| **AC2** 最小改动、独立命名、`CreateNew`、不覆盖 A5 证据 | | **部分满足（见 F-03）** | 执行器对 A5 的 10 处最小改动**逐处核实为真**（`:1`、`:25`、`:34`、`:440`、`:512`、`:524`、`:532`、`:551`、`:605`、`:623`，与 Handoff `:26-36` 完全一致）；`:463`、`:493` 为 `FileMode::CreateNew` + `FileShare::None`；A5 outputTargets 11 项历史记录 `absent: true` |
| **AC3** pin 实际 Owner Handoff、分离 immutable contract、`checkpointIncludedInInputPins=true` + checkpoint 入 pins、继承源可 pin | | **未满足（见 F-01/F-02/F-04）** | Handoff pin 修复为真；contract/Task 分离为真；`checkpointIncludedInInputPins` **缺失**；根旧 Handoff 未在 manifest |
| **AC4** 源码 Parser/内存断言 vs runtime 证据分离 | | **满足** | 协议 `:85-87`；执行器 `:48` 初始 `parser/selfcheck/capability = NOT_RUN`；Handoff `:62` |
| **AC5** SDDL 逐字 / 不重建 malformed helper / `.tmp.driveupload` `NOT_VERIFIED` | | **满足** | 执行器 `:27` ＝ 协议 `:90` 逐字相同；A5 JSON `:461` 原文保留；协议 `:95` |
| **AC6** pre-write snapshot / disposition vs process exit / "helper invocation" | | **满足** | 协议 `:36`、`:45`、`:46`、`:93`；执行器 `:49-52` |
| **AC7** immutable exact-input package 供 DSH 审查 | | **部分满足（见 F-01/F-02）** | 25/25 输入具备声明 MATCH；但清单仍缺 2 项可 pin 性声明/条目 |
| **AC8** 交付 branch/HEAD、三路径 diff、Handoff、AC 结果、Parser-only 结果、`git diff --check` 结果、blocker | | **部分满足（见 F-03）** | Handoff 交付了分支/HEAD/三路径/pin 表；Parser/`git diff --check` 只有声明，无独立可审日志 |

### A5 accepted findings 九项逐条

| finding | 状态 | 依据 |
|---|---|---|
| **P1-1** Handoff pin 无来源且同时是写入源 | **resolved** | 执行器 `:25` `$HandoffHash='E13C7148…'`、`:440` `9505`；`:512/:524/:532/:551/:605` 均 9505；协议 `:21`、`:117` 明确 pin 实际 Owner Handoff 路径与字节；manifest `:148-153` 作为显式只读输入（除本报告 F-02 的清单完备性问题外）。A5 的 3551/`700B79F3…` 已完全移除（A5 执行器对照 `:25/:440`） |
| **P1-2** immutable review contract 与 mutable Task status 分离 | **resolved** | 契约快照 `agy-…-task-contract-20261012.md` 独立存在（36 行）；可变 Task `doc/tasks/P02PRE-R1H-R6-EXEC-A6.md` **不在** 25 项 pins 中；协议 `:116` 明确分离 |
| **P2-1** fail-stop 后未观测状态不得声称未变 | **resolved** | 协议 `:47` 逐字要求；执行器 `:53` `metadataLimits = '… NOT_VERIFIED.'`、`:52` `nativeInteropLimit` |
| **P2-2** 源码 Parser/内存断言 vs runtime 证据 | **resolved** | 协议 `:85-87`；执行器 `:48`、`:567-581`、`:593-594`；Handoff `:62`。**限定**：`0 errors / 73 PASS` 是 A5 阶段的事实（parser-pass checkpoint `:18`），A6 Handoff `:47` 表述为"在运行前完成"尚可接受，但其**自身**的 Parser 声明无独立日志（见 F-03） |
| **P2-3** 继承源与 root 旧 Handoff 可被 pin 与复核 | **partial** | A4 executor/protocol/handoff、A5 executor/protocol/handoff、实际 Owner Handoff 均在 manifest 内并声明 MATCH；**root 旧 Handoff 不在 manifest**（见 F-02） |
| **P3-1** observed/expected SDDL 逐字 | **resolved** | 协议 `:90`；执行器 `:27`；A5 JSON `:301` `destinationAclMatchesFrozenSddl: true` |
| **P3-2** 不重建 malformed helper argv/stderr/exit、`.tmp.driveupload` `NOT_VERIFIED` | **resolved** | A5 JSON `:461` 原文保留（"Two read-only root-status helper attempts passed a leading ASCII space … whether Git inspected the excluded subtree is NOT_VERIFIED."）；协议 `:93-95` |
| **P3-3** `checkpointIncludedInInputPins=true` 明确且 checkpoint 真正入 pin | **unresolved（阻断，F-01）** | 协议 `:115` 只是声明该字段"explicitly declares"；manifest 全文**无** `checkpointIncludedInInputPins`；Handoff `:51` 与 `:64` 却断言"输入清单显式设置 `checkpointIncludedInInputPins=true`" |
| **P3-4** pre-write snapshot / disposition vs exit / helper invocation | **resolved** | 协议 `:36`、`:45-46`、`:93`；执行器 `:623-630` |

---

## 3. Findings

### F-01 — P2（阻断）：`checkpointIncludedInInputPins=true` 未落地，且交付物两处断言其为真

- **文件/行**：`agy-p02pre-r1h-r6-exec-a6-input-manifest-20261012.json`（全文，无该字段）；`p02pre-r1h-round6-integration-protocol-attempt6-20261012.md:115`；`p02pre-r1h-round6-attempt6-exec-handoff-20261012.md:51` 与 `:64`
- **触发与影响**：immutable A6 Task contract `:23` 逐字要求 "Set `checkpointIncludedInInputPins=true` and include the pinned checkpoint"；A5 accepted finding P3-3 的 required treatment 逐字为 "A6 manifest must set `checkpointIncludedInInputPins=true` and include the checkpoint pin"（A5 pre-run adjudication `:18`）。协议 `:115` 声称 pin manifest metadata **declares** 该布尔，但 manifest 实际没有该字段（对整个 `verification/P02` 的内容检索中，命中该字符串的 A6 产物只有协议、Handoff 与 Owner 响应，manifest 不在其中）。Handoff `:51`/`:64` 进一步把它列为已完成的修复与 `PASS_WITH_EVIDENCE`，形成**虚假闭合**。
- **证据**：manifest 顶层仅 `generatedUtc / inputs / baseCommit / task / owner`（`:1-158`）；其 25 项 inputs 中**确已包含** rolling checkpoint（`:107-111` `codex-checkpoint-p02pre-r1h-round6-attempt5-parser-pass-20261012.md`，5428 bytes / `638A02A9…`，Codex 记录 MATCH）——即"包含 checkpoint pin"的实质已达成，缺的只是被明确要求的布尔声明。
- **建议（最小修正）**：在 A6 input manifest metadata 增加 `"checkpointIncludedInInputPins": true`（并自洽说明含哪一项），或若 Codex 认为该项应始终为 `false`，则同步改写协议 `:115` 与 Handoff `:51`/`:64` 的断言。**不得**用"未运行即未变"或"实质已包含"替代显式声明。
- **是否阻断**：**是**。按冻结 release condition（协议 `:120`，A5 protocol `:108` 的同一规则）"Any unresolved P0/P1/P2 finding means `CHANGES_REQUESTED`"；A5 链上同类缺失字段（`checkpointIncludedInInputPins`）曾被本审查方按 P2 记录并由 Codex 以"后续 manifest 必须有该字段"闭合（`p02pre-r1h-attempt5-exec-review-adjudication-20261012.md` P2-002），A6 不应回退。

### F-02 — P2（阻断）：root 旧 Owner Handoff 仍未进入 immutable input manifest / pins

- **文件/行**：`verification/P02/p02pre-r1h-round6-integration-protocol-attempt6-20261012.md:117`（"…root old handoff… are pinned and reviewable"）；`agy-p02pre-r1h-r6-exec-a6-input-manifest-20261012.json:3-153`（25 项不含该路径）；`codex-p02pre-r1h-attempt6-review-input-verification-20261012.json:9-209`（25 项同样不含）
- **触发与影响**：A5 accepted finding **P2-3** 为 `ACCEPTED IN PART`，required treatment 明确 "A6 must pin required inherited sources"，其中点名的就有 "root old Handoff"（A5 pre-run adjudication `:15`，`:11` 亦要求把实际 Owner Handoff 作为独立 Review 输入）。A6 执行器确实在代码中校验该文件（`:442` `8651` / `394CCF80…`，`:529`、`:601` 复检），协议 `:117` 也声称它已 pin 且可复核；但该路径**不在**任何 A6 input manifest 或 pin 集合里，本 prompt 的"必读来源"也未列出它。因此该继承输入仍停留在"代码内有常量、清单外无 provenance"，与 P2-3 要求的"可被独立复核"存在缺口。
- **证据**：实际文件存在且可读（`G:\CODEX\New Manga\verification\P02\p02pre-r1h-handoff-20261012.md`，90 行，front-matter `base_commit: 0ecada4182…`），其 pin 值 `8651 / 394CCF80E58017798CA2994C0505F2F5B5BB571143D21C655CEFC77B6173520F` 与 A5 执行器 `:442`、A5 final pre-run JSON `:117`（8651 / `394CCF80…`）一致——即**值本身可信**，缺的是把它纳入 exact input package。
- **建议**：在 A6 input manifest 与 Codex pin verification 中补入该路径及其 bytes/SHA-256（与执行器 `:442` 常量逐字一致），或明确记录它为何被排除并撤回协议 `:117` 的"pinned and reviewable"表述。
- **是否阻断**：**是**（P2 未解决即 `CHANGES_REQUESTED`）。

### F-03 — P3：AC2/AC8 的三处文本声明与可审证据不符

- **文件/行**：`p02pre-r1h-round6-attempt6-exec-handoff-20261012.md:38`、`:45`、`:59-60`、`:66-68`
  1. `:38` 称"其余 629 行…全部保持**逐字节继承**"——与同文 `:26-36` 自述的 10 行改动、以及我核实到的 10 处差异在字面上冲突（数值上也自相矛盾：639 − 10 ≠ 629 行"逐字节继承"的表述边界不清）。
  2. `:45`/`:59` 把 AC2 记为 `PASS_WITH_EVIDENCE`，并称"输出文件全部使用 attempt6 独立命名"——但执行器 `:11-20` 的 8 个输出路径与 A5/A4 **完全相同**（`p02pre-r1h-selfcheck-round6-stage-20261012.ps1`、`…round5-recovery…`、`…round6-handoff…`、`…round6-execution…`、`…selfcheck-round6-…json`、`…engine-preflight-round6-…json`），只有 schema 串标了 `attempt6`（`:34`）。真正被"独立命名"的只是任务三件套。就本 AC 的字面（"使用独立 attempt6 文件名"）而言为**未满足**；安全性实际由 `CreateNew`（`:463`、`:493`）与 A5 侧 11 项 `absent: true` 历史快照保障，不构成覆盖 A5 证据的风险。
  3. `:66-68` 的 Parser `0 errors`、`git diff --check` 0 errors 只以文字声称，**没有**提供独立可审的原始 stdout/stderr/exit 文件；本 prompt `:47` 也要求"不能把声明自动当作证据"。
- **建议**：把 `:38` 改为与 `:26-36` 一致的精确表述；把 AC2 的结论改为"输出路径继承 A5，覆盖安全由 `CreateNew` + A5 `absent` 历史快照保障，attempt6 独立命名仅适用于任务三件套"；为 Parser 与 `git diff --check` 结论补交可审原始输出，或明确标为 Owner 声明（`NOT_VERIFIED`）。
- **是否阻断**：否（不改变执行安全边界，`CreateNew` 语义未被放松）。

### F-04 — P3：Handoff 自引用 pin 表不完整，且未声明与 immutable contract 的关系

- **文件/行**：`p02pre-r1h-round6-attempt6-exec-handoff-20261012.md:71-79`
- **触发与影响**：`交付文件 Pins 汇总` 只给出第 1、2 个文件的 bytes + SHA-256；对**自身**（第 3 个文件，12558 bytes / `AEEAD4C9…`）**未列 hash**。该值只存在于同链的 prompt `:16` 与 Codex JSON `:229-233`。另外 Handoff 未说明 immutable contract 快照（`agy-…-task-contract-20261012.md`，3553 bytes / `D4D8978D…`）与自身、与可变 Task 的关系——该路径同样不在 25 项 input pins 中，也未在 Handoff pins 表中出现。
- **建议**：补齐第 3 个文件自身 pin；显式记录 review-contract 快照 pin 及其"不在 input pins / 独立于可变 Task"的定位（与协议 `:116` 一致）。
- **是否阻断**：否。

### F-05 — P3：A6 worktree 存在非 allowlist 的 Codex 残留，影响 Handoff/预验证状态陈述的时效性

- **文件/行**：`p02pre-r1h-round6-attempt6-exec-handoff-20261012.md:19`、`:59`；`codex-p02pre-r1h-attempt6-review-input-verification-20261012.json:215`
- **触发与影响**：Handoff `:19`/`:59` 称 worktree"仅且仅创建 3 个 allowlist 文件"、AC1 `PASS_WITH_EVIDENCE`；Codex 预验证 `:215`（08:31:52 UTC）当时确实只有 3 条 `??`。但 Task 自身 `:112` 记录 Codex 随后在同一固定 worktree 写入多个 zcode smoke 证据文件；我在 worktree 的路径名清单中亦看到 `verification\P02\zcode-dispatch-r1.*`、`zcode-task.prompt.md` 等 A6 worktree 内既有 P02 文件。这些新增文件在 Owner 时点不存在，故不是 Owner 的 AC 违规，但交付物与预验证陈述**已不再是当前 worktree 状态的完整描述**；执行器的 `AssertDelta` 与状态多重集断言对 status **多重集精确匹配**（`:411-432`），任何此类残留都会让未来 pre-run 的状态基线停在 `NOT_VERIFIED`/需重新裁定。
- **建议**：由 Codex 记录这些残留的作者/性质并在 attempt6 final pre-run 前明确 status 基线口径；Handoff 与预验证的状态陈述加"截至该时点"的限定。
- **是否阻断**：否。

---

## 4. Architecture 与 Verification 结论

**Architecture（静态）**：attempt6 相对 attempt5 的改动**确实是最小的**——我逐处核实了 Handoff `:26-36` 自述的 10 处差异，执行器在 `:25/:440/:512/:524/:532/:551/:605` 把 Owner Handoff 的 `3551 / 700B79F3…` 换成 `9505 / E13C7148…`（与真实文件一致），并更新 `:1`/`:34`/`:623` 的 attempt 标识；`$IndexHash='C5CA8884…'`（`:26`）与 A5 一致且与 A5 pre-run JSON `:53`、parser-pass checkpoint `:9` 记录相同，**未漂移**。写入边界未被扩大：8 个写路径、单一 `File.Replace`（`:543`，`$ReplaceCalls++` 仅在 `:542`）、`CreateNew` + `FileShare.None`（`:463`、`:493`）、child 白名单（`:277-278`）、Git 上下文变量清除与 fail-stop（`:286-296`）、`.tmp.driveupload` 的 `AssertChain` 拒绝（`:87`）与 `ReadStatus` 的最终独立 pathspec（`:390`）均按预期继承，未发现"以 attempt6 之名放松隔离"的修改。SDDL 常量（`:27`）与协议 `:90` 逐字相同，且与 A5 执行器 `:27` 逐字相同。

**Verification（静态）**：`NOT_RUN` 项目——attempt6 执行器调用、`File.Replace`、runtime `selfcheckEvidence`、`engineEvidence`、capability 子进程、Git 子进程、capture/getter、profile/registry/ACL API、Build/Cargo、system AC1–AC7，全部 `NOT_RUN`；`PRE_RUN_PASS` 尚未取得（该状态是 A5 侧 `PRE_RUN_BLOCKED` 的后续边界）。Gate 状态未被本次交付改动：`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、`technical condition unmet; user explicitly accepted residual risk`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、system AC1–AC7=`BLOCKED / NOT_RUN`。

---

## 5. 未运行 / 不可验证 / 剩余风险

- **未运行**：上节"Verification"全部 `NOT_RUN`；A6 的 final pre-run 亦未开始。
- **不可验证（`NOT_VERIFIED`）**：我的独立 bytes/SHA-256（全部，受 `SetNamedSecurityInfoW Win32 5` 阻断，且无 approval channel）；`.git/index`（未读取）；Git refs/HEAD/tree 的实时解析；root 与 Owner 的受控 status 原始字节与多重集；`.tmp.driveupload` 的访问范围；Owner 侧 Parser `0 errors` 与 `git diff --check` 结论；manifest 中 25 项的真实匹配性（我只比对了链内声明值自洽）。
- **A5 侧遗留（非 A6 缺陷，但影响后续）**：A5 `stdout.log` 为非 UTF-8（ANSI/GBK）的 `whoami` 原始输出，read 通道无法逐字读取；其内容不含英文失败行，真实失败判定在 JSON blocker 与 stderr.log。A5 `.exit` 内容为 `2`，与 `PRE_RUN_BLOCKED` / `STOP_BEFORE_EXECUTOR` 一致。
- **剩余风险**：本次静态 Review **不**能把 private registry technical condition、Build Gate、AC1–AC7 或任何 Gate 视为通过；`APPROVED_STATIC_CONTENT` 本身也不等于执行授权，何况本轮为 `CHANGES_REQUESTED`。

---

## 6. 放行判定与下一步（供 Codex adjudication）

- 按冻结 release condition（A6 协议 `:120`），F-01、F-02 两项未解决 P2 使本轮**必须** `CHANGES_REQUESTED`，并**阻止**后续 Codex Parser / 纯内存自检、attempt6 final pre-run 与执行器调用。
- **最小修正路径（建议由 Antigravity 在固定 worktree、仅三文件 allowlist 内完成）**：
  1. 在 `agy-p02pre-r1h-r6-exec-a6-input-manifest-20261012.json` 顶层加入 `"checkpointIncludedInInputPins": true`，并在同一 manifest 的 `inputs[]` 补入 `G:\CODEX\New Manga\verification\P02\p02pre-r1h-handoff-20261012.md`（8651 / `394CCF80E58017798CA2994C0505F2F5B5BB571143D21C655CEFC77B6173520F`），使其与执行器 `:442` 常量一致；若该 manifest 属 Codex 独占路径，则由 Codex 修正并在 Task/checkpoint 记录。
  2. 修正 Handoff `:38`、`:45`（或 `:59`）、`:64` 的表述，并在 `:71-79` 补齐自身 pin。
  3. 补交 Parser 与 `git diff --check` 的可审原始输出，或标为 `NOT_VERIFIED`。
- **需要 Codex 明确裁决的一点**：F-01 的字段缺失按 A5 先例计为 P2（阻断），本轮据此给出 `CHANGES_REQUESTED`；若 Codex 认定该字段对 A6 仅属文档完备性、不影响执行安全，则应显式记录降级理由并同步协议 `:115`/Handoff 的断言，不能保留"已设置为 true"的既成表述。
- **无需下一步操作**的条件不存在：本 Task 硬依赖链（DSH Review → Codex adjudication → Codex Parser/内存验证 → final pre-run）仍在，按当前证据停在"Review 报告待 adjudication"这一边界，执行器、`File.Replace`、Build/Cargo 与 AC1–AC7 一律保持 `NOT_RUN`。
