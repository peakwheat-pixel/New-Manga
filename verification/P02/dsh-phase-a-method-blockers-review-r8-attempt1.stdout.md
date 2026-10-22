# P02 memo r8 candidate · 非作者只读 Review（内容层）

## 1. 内容结论

- **内容结论：`APPROVED_WITH_CONDITIONS`（仅文本/引用层）。**
- r8 相对 r7 的唯一实质变更是 `:8`（Task pin 叙述重写）；`:3`、`:9`、`:11`、`:15–:19`、`:21`、`:25`、`:27`、`:29`、`:31`、`:35–:37`、`:39–:53`、`:57` 与 memo r7 逐字一致（文本层逐行比对）。未新增方法、路径、探测或数据读取。
- **要求 1（pin 分层与「本轮」）→ 满足。** `:8` 按轮次分别命名：memo r3 attempt 2=`108405/7521…`、attempt 3=`111260/351E…`（原始行号锚点在该 pin 上核对 `:58–62`、`:68–70`、`:382–386`）、memo r5 Review=`116853/7CCF…`、memo r6 候选形成时=`117485/C11B…`（明标「历史候选快照，不是Review dispatch」）、memo r6 Review=`119770/3BAA…`、memo r7 Review=`123471/5B8A…`，并写「这些是不同历史对象，pin 不互换」。全文不含「本轮」（只读文本检索：`read`/`grep` 命中行均无该词），R7R-P3-01 所指的同段二义已消除。唯一残留为 `:8` 新增的两处指代不精确（见 R8R-P3-01/02）。
- **要求 2（123471 与本轮 126629 不混淆）→ 满足。** `123471/5B8A…` 明确归属「memo r7 Review」；r8 全文不出现 `126629`/`349C…`，即未预写本轮 pin，符合派发约定（本轮权威 pin 由本 Review prompt 固定）。规则「各轮行号只适用于该轮 Review prompt 固定的 Task pin，pin 变化须重核」已明文化且可复用。
- **要求 3（Codex 证据不抬高 DSH binding，链接/历史状态）→ 满足（除 R8R-P3-02 的标签一名两指）。** `:8` 明写「Codex 核验不改变 DSH formal `object_binding=NOT_VERIFIED`」；两个链接文件均存在且内容与归属相符：`r6 adjudication` 复算的是 `119770`-byte 前缀（该文件 `:13`），`r7 adjudication` 复算的是 `123471`-byte 前缀（该文件 `:25`）；117485 的历史定位与 r6 adjudication`:20/:23`、r7 adjudication`:16` 自洽；`r5 attempt 1 adjudication` 链接（`:11`）存在。
- **要求 4（scope/禁令/Gate/evidence state）→ 满足。** `:35–:36` 禁令与 `:41–:51` 11 项 Gate token、`:3`/`:15`/`:37`/`:53`/`:57` evidence state 与 r7 逐字一致，无降级或放宽；未把静态 Review、Codex hash 或用户授权表述为 OS measurement、测试结果、执行许可或 Gate PASS。
- **引文抽查（live 文本观察，非 byte 绑定）**：contract r7 `:115`（§5 含 `GetFileInformationByHandleEx(FileHardLinkInfo)`）、`:156`（§8.1 三项前置 + 独立禁令）、`:177`（精确下一步第 3 条「均无歧义」）；manifest r3 `:20`（23 项、无 ProgramData）、`:22`（T0/T1 次序）、`:26–:28`（CrashDumps + 两条 `%ProgramData%` WER）；`codex-appcontainer-contract-r7-adjudication.md:52`（Resolution：不执行 manifest r3）→ r8 `:19`/`:27`/`:16` 锚点与引文均相符。
- 未发现安全/Gate 越界，未发现 P0/P1/P2。

## 2. P0/P1/P2/P3 数量

| 级别 | 数量 |
|---|---:|
| P0 | 0 |
| P1 | 0 |
| P2 | 0 |
| P3 | 2（均为本轮新增的 `:8` 指代/引用标签精确性，均无 Gate、范围或方法影响） |

## 3. 既有 finding disposition

| Finding | 本 Review 独立判定 |
|---|---|
| R7R-P3-01 · `:8` 同段「本轮」指代两个轮次、未登记 r7 pin | **CLOSED（文本层）**。r8 `:8` 已按 Review 轮次命名全部 pin（含 memo r7 Review=`123471/5B8A…`），全文无「本轮」，规则改为主语明确的「各轮行号只适用于该轮 Review prompt 固定的 Task pin」。 |
| R7R-P3-02 · 「行号锚点仅在 attempt 3 pin 复核」与 Codex 在 116853/119770 复核相抵触 | **CLOSED（文本层）**。r8 `:8` 已把「memo r3 原始行号锚点在该 pin 上核对」与「后续 Codex 在各自派发快照上另作语义锚点核对」分列，删除「仅」的绝对限定；分列本身引出的新指代问题另计 R8R-P3-01，不重开本条。 |
| R6R-P3-01 · 117485 被误称「当前 live」 | **CLOSED（维持）**。r8 `:8` 标为「memo r6 候选形成时的 Task pin……（历史候选快照，不是Review dispatch）」。 |
| R6R-P3-02 · 未登记本轮派发 pin 与优先规则 | **CLOSED（维持）**。r8 `:8` 登记 memo r6 Review=`119770`，并写入「pin 变化须重核」的优先规则。 |
| R6R-P3-03 · 未保留 RV6-P3-01 的拒绝标注 | **CLOSED（维持）**。r8 `:11` 保留 `REJECTED_AS_MISQUOTED` 裁决登记与「该误引不产生 memo 修订义务」。 |
| RV6-P3-01（r5 attempt 1 DSH） | **`REJECTED_AS_MISQUOTED`（维持，不重开）**。r8 只登记该既有裁决，未要求改动 r5/r6 固定对象。 |

## 4. 新增 findings

**R8R-P3-01 · `:8`「memo r6 pin」缩写指代不唯一，且「各自派发快照」列表含非派发快照 117485（P3）**
- 位置：`verification/P02/codex-phase-a-method-blockers-20261010-r8.md:8`。
- 证据：(i) 该段先以「后续 Codex 在各自**派发快照**上另作语义锚点核对」引导列表，列表内却含 `117485`（同句自标「历史候选快照，不是Review dispatch」），引言与被列对象不一致；(ii) 随后「**memo r6 pin** 的 Codex 前缀复算及锚点复核见 r6 adjudication」中，「memo r6 pin」既可读作前文的 `117485`（字面为「memo r6……Task pin」），也可读作最近出现的 `119770`；r6 adjudication `:13` 复算的是 `119770`-byte 前缀，对 `117485` 的锚点检查实际登记在 r5 attempt 1 adjudication `:25`（且非前缀复算）——若按 `117485` 读，指针与「前缀复算」均不成立。
- 影响：不改变任何 Gate、授权、范围或方法；属可溯性/指代精确性，与 R7R-P3-01 要消除的 pin 歧义同类，但由 `:8` 重写新引入。
- 最小修正（仅文本）：把该句改为「memo r6 Review pin（`119770`）的 Codex 前缀复算及锚点复核见 r6 adjudication；`117485` 历史候选快照期间的锚点检查登记于 r5 attempt 1 adjudication」，并把引言「各自派发快照」限定为派发快照，或将 117485 从该列表中移出。

**R8R-P3-02 · 文档内短名「r7 adjudication」一名两指（P3）**
- 位置：`...-r8.md:8`（新链接）与 `...-r8.md:11`、`:19`（既有引用）。
- 证据：(i) `:8` 新增链接标签 `` [`r7 adjudication`] `` 指向 `codex-phase-a-method-blockers-review-r7-attempt1-adjudication.md`（32 行，无 `:52`）；(ii) `:19`「r7 adjudication（:52）」与 `:11`「r7 Codex adjudication SHA-256=`6C585068…`」均指 `codex-appcontainer-contract-r7-adjudication.md`（`:52` 为 Resolution「do not execute manifest r3」），且 `doc/tasks/P02.md:401` 亦以「r7 adjudication」指该契约裁决文件——同一文档内一个短名对应两份不同对象。
- 影响：不构成错误链接（`:8` 链接目标本身正确），但继任 Review 若按 `:19`/Task 既有惯例解析 `:8` 的 `r7 adjudication`，会指向错误裁决文件；不改变 Gate/范围。
- 最小修正（仅文本）：`:8` 链接标签写全，如「memo r7 Review attempt 1 adjudication」（对应写「memo r6 Review attempt 1 adjudication」），把「r7 adjudication」保留给契约 r7 裁决，或反之统一命名。

## 5. formal `object_binding` 限制

- **`object_binding = NOT_VERIFIED`（本 Review 自身）。** 本次为纯只读文本审查：仅使用只读文件读取（`read`/`grep`/`glob`），未运行 shell、PowerShell、Git 或任何 hash 命令，未运行 Windows API、ETW/process observer、OS measurement、profile/ACL/registry/label 操作、probe、测试、Cargo、build 或 Windows Sandbox；未创建、修改、暂存、删除或移动任何文件。
- 派发方提供的 byte/SHA-256 pins（Task `126629/349C…`、memo r8 `11700/1AF192CD…`、r7 裁决 `3874/50442879…`、r7 report `10501/54D4194A…`、memo r7 `11808/14E8BA9A…`、r6 裁决 `4143/341482ED…`、r6 report `11044/451410D4…`、memo r6 `11135/59E49BA5…`、r5 裁决 `3464/CBFFDC1D…`、contract r7 `7FBFFE65…`、manifest r3 `AC45329A…`）在本 Review 中**均为转录值，不构成对象绑定或 hash 复核**；文中对 r8 全文行数/逐行一致性的陈述来自我读取到的 live 文本，不证明其与派发快照的字节对应。
- 明确标为 `NOT_VERIFIED` 的项：所有字节数与 SHA-256；r8 候选文本与 `126629`-byte 派发快照的字节对应；live `doc/tasks/P02.md`、contract r7、manifest r3、各 adjudication 的行号在派发固定字节版本上的可复现性；`r6→r7→r8` 变更范围的完整性（结论来自 live 文本逐行比对）；Git 与工作区状态；CLI exit、session/mount 与 prompt 文件自身身份。
- 本 Review **不是** exact-object / exact-hash Review，**不是** Gate PASS，**不是** Phase A 执行授权，不得被表述为「Review 通过」。

## 6. Gate 边界

- Phase A=`BLOCKED / NOT_RUN`
- private_registry_absence=`UNPROVABLE / BLOCKED`
- profile=`NOT_CREATED`
- ACL/registry=`NOT_MODIFIED`
- scratch ACL/label=`AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`
- OS preflight=`NOT_RUN`
- hook/cache/child closure=`BLOCKED / NOT_VERIFIED`
- Build Gate=`BLOCKED`
- build=`NOT_AUTHORIZED / NOT_RUN`
- Hard Build Barrier=`EFFECTIVE`
- AC1–AC7=`BLOCKED / NOT_RUN`

P02 AC1–AC7 为 `BLOCKED / NOT_RUN`，**不是 failed**。上列 11 项与 r8 `:41–51`、memo r7 `:41–51`、r7/r6 attempt 1 adjudication 同集同值；本 Review 不改变 Task、contract r7、manifest r3 或任何 memo/adjudication 的字节或 pin。

**推荐下一步：** 将 R8R-P3-01/02 交 Codex 做 finding adjudication；若需闭合，最小范围是在**新** memo r9 候选（不改动 r8 固定对象）的 `:8` 采用完整标签（「memo r6 Review pin（119770）」/「memo r7 Review attempt 1 adjudication」）并修正「各自派发快照」引言。R7R-P3-01/02、R6R-P3-01/02/03 维持 CLOSED，RV6-P3-01 维持 `REJECTED_AS_MISQUOTED`，均不重开、不要求改动既有固定对象。在 contract r8 与新 Phase A manifest 经非作者 Review 与 Codex 核验前，Phase A 保持 `BLOCKED / NOT_RUN`，不运行任何测量、测试或 build。

Review 是内容意见，不是 Gate PASS、exact-object binding 或 Phase A 执行授权。
