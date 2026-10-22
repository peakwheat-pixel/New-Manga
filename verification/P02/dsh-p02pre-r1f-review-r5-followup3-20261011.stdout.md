# P02PRE-R1F Review Round 5 follow-up #3 — DeepSeek Harness 独立只读复核

## Decision

`APPROVED`

## counts

`P0/P1/P2/P3 = 0 / 0 / 0 / 0`

结论摘要：follow-up #2 的 F1（条件性 P2）已被“**同一路径在失败尝试之后被成功 retry 创建**”的时序证据合理消除；F2（静态保护路径数）经我独立逐行清点，`72 keys / 72 unique / 0 duplicates` 正确且三处表述一致。Task/manifest/adjudication 的 release 顺序、R8 目标名、单次 `CreateNew` 边界与 Gate 措辞均自洽，owner waiver 未被误写为 Technical Gate PASS、build 放行或 AC PASS。本 Review **不授权** R8、capture、Build/Cargo、AC1–AC7，也不代表任何 Gate PASS。

---

## 1. exact pins 核对（仅字面一致性，未复算）

| pin | 记录值 | 在本轮 8 文件内的交叉引用 | 结论 |
|---|---|---|---|
| #1 Task | `21292 / 0AD1C9D2…BF202` | adjudication L10 | 一致 |
| #2 manifest | `21114 / FC1EF72A…2CD53` | adjudication L10 | 一致 |
| #3 script | `65533 / 6B7556C7…40CD1` | adjudication L10；manifest L17；pin #4 内部 `sourceBytes/sourceSha256`（JSON L5–L6）；script L684 自我保护项 | 一致 |
| #4 followupfix2 self-check | `2308 / 1696B781…2CF1E2` | adjudication L10；manifest L17 | 一致 |
| #5 本 adjudication | `4950 / EBBF2696…575B` | 报告自身 L10 引用候选 pins | 自洽 |
| #6 prior review stdout | `15009 / C66500FC…D36B7` | adjudication L8 | 一致 |
| #7 wrapper attempt1 | `1179 / CABB770B…D9703` | adjudication L16；manifest L16；Task L93 | 一致 |
| #8 followupfix self-check | `2307 / FE2277D0…4F237C` | adjudication L16（`Length=2307`、`Get-FileHash=FE2277…`）；Task L38 | 一致 |

**边界**：本轮禁止执行命令，我**没有**用 `Get-FileHash`/`Get-Item` 复算任何 bytes/SHA。上表只是“8 份 pinned 文档相互引用是否字面一致”，独立复算仍为 `UNPROVEN`，须由 Codex 按 Task L42 完成。

附带一项正向发现：8 个 pinned 输入**全部**出现在冻结 script 的 protected 键内（Task L678、manifest L683、script L684、#4 L723、#8 L722、#7 L716、#6 L725、#5 L728），因此 R8 前的 pre-run baseline 重验会覆盖本轮 Review 的全部输入字节。

## 2. F1（条件性 P2：protected 清单含“未创建”目标）判定

**判定：`CLEARED`（前提被后发证据取代），但保留 pre/post 未被证明的边界。**

可复现的时序链（全部位于 pin 内）：

1. pin #7 记录 `Timestamp=2026-10-11 09:18:13 UTC`，分类 `HARNESS_FAILURE / CHILD_NOT_STARTED`（`FileName or extension is too long`），并说明“The unique self-check result target `p02pre-r1f-r5-followupfix-selfcheck-20261011.json` **was not created**”——该句是**针对当次尝试**的时序陈述；同一段末尾明确声明 “Retry will stream source bytes through redirected stdin after starting the child, then retain the attempt-2 result at the unique target”。
2. pin #8 就位于该唯一目标：`createdUtc=2026-10-11T09:18:56.9404062Z`（失败尝试后约 43 秒）、`phase=R5_FOLLOWUPFIX_ISOLATED_SELFCHECK`、`childExitCode=0`、`parseResult=PARSE_OK`、`selfCheckResult=PASS`、`captureScriptInvoked/hostGetterInvoked/registryOrAclWriteInvoked=false`。
3. adjudication L16 的 `Test-Path=true` / `Get-Item Length=2307, LastWriteTimeUtc=2026-10-11 09:18:56` / `Get-FileHash=FE2277…` 与 pin #8 的 `2307 bytes / FE2277D0…` 完全对齐。

因此“**capture 必然因 ABSENT 停止**”不再是可推出的结论：ABSENT 断言有时序作用域（09:18:13），且同路径已在 09:18:56 由 retry 产物补齐；script 的 `Get-FileRecord`→`ABSENT`（L254–L256）触发 `invalidHashCount`（L795）→`stopReason`（L848）→`throw`（L888）这条链路在当前主机状态下不会被该路径必然触发。

**仍不能证明的部分（须在 pre-run 重验）**：

- 该存在性是**单次点观测**，不能证明 capture 前后字节不变；L795/L848/L888 意味着 capture 时刻任何一条非 `PRESENT`（或 hash 漂移）仍会计满 `invalidHashCount` 并消耗唯一一次 `CreateNew`。adjudication L16（“This point-in-time observation is not the pre/post baseline and must be repeated before capture; absent or changed hash means stop”）、L22（“all 72 protected paths and their hashes”）、Task L38/L46 与 manifest L57 都已写明该要求，**表述充分**。
- pin #8 的 `sourceBytes=65530 / sourceSha256=3B143481…32A3` 与冻结 script（`65533 / 6B7556C7…`）**不同**，即它是较早候选的历史 self-check，不能作为“冻结字节可解析”的证据；冻结字节的自检证据是 pin #4（`65533 / 6B7556C7…`、7 个纯函数 PASS）。adjudication L16 对此已有明示（“its source pin is an older candidate”）。

## 3. F2（静态保护路径计数）判定

**判定：`CORRECTED / VERIFIED`——`72 keys / 72 unique / 0 duplicates` 正确。**

我独立逐行清点冻结 script 的两个 `$Result.protectedHashes` 数组（全文仅此两处 `foreach ($key in @(`，见 L669、L732；`grep` 确认无第三个同类清单）：

| 数组 | 行范围 | 字面量数 | 唯一数 |
|---|---|---|---|
| 数组 1 | L669 开 → L729 闭，键 L670–L728 | **59** | 59 |
| 数组 2 | L732 开 → L746 闭，键 L733–L745 | **13** | 13 |
| 合计 | — | **72** | **72**（0 duplicates，两数组无交集：`r8` 仅在数组 2，`r1/r2/r3/r5/followup/followup2/r4-*` 分布不重叠） |

三处文档表述与我的清点一致：Task L38 `72/72 unique`、manifest L17 `72 keys / 72 unique / 0 duplicates`、adjudication L17 `2 blocks / 72 keys / 72 unique / 0 duplicates`。旧 `p02pre-r1f-r5-followup2-adjudication-20261011.md` L21 的 `63` 属历史记录，adjudication L17 已明确 supersede，Task 未再残留 `63`。script 内**没有**硬编码期望计数（`protectedHashes` 仅出现在 L32/L579/L730/L747/L783），故“计数更正”不改变字节，与 adjudication L21“No script code was changed”一致。

旁证一致性（非本轮要求，顺手核对）：`inputRoots` 12 条（L646–L659，11 字面量 + `$Scratch`）、`outputLeaves` 13 条（L661）、`canaryLeaves` 3 条（L663）、`werDirs` 3 条（L665）、环境变量 35 个（L629）——与 manifest L8 的 `12 / 13 / 3 / 35` 逐项吻合；L446 的 `.git\HEAD/.git\index/.git\config` 是 `gitMetadata` 记录，不属于 protected 计数。

## 4. 顺序与边界检查

| 检查项 | 结论 | 证据 |
|---|---|---|
| release 顺序：follow-up #3 `APPROVED` + Codex pin/range adjudication → PS 5.1 parser R8（同一冻结 bytes、parse-only）→ 独立 Codex pre-run adjudication（身份/SID、roots/refs、status/index、输出目标 absent、72 条 protected 存在性与 hash）→ 单次 capture | `PASS`（文字自洽，无矛盾句） | Task L25/L34/L42/L43/L46/L65–L69；manifest L17/L57；adjudication L22 |
| R8 artifact 名 | `PASS` | Task L34/L43/L98 = `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json` = script L733（protected 数组 2） |
| exact argv | `PASS` | Task L68 与 manifest L27 逐字一致（`-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File verification/P02/p02pre-r1f-capture.ps1`） |
| owner waiver 未被误写 | `PASS` | Task L38/L51、manifest L53、adjudication L23 均保留 `private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`；无任何 waiver→PASS 或 build/AC 放行措辞 |
| self-check 未被当作 Gate PASS | `PASS` | manifest L17/L22、Task L38/L94、pin #4 自身三字段 `false` |
| 唯一 `CreateNew` 且不重试/不清理 | `PASS`（静态） | script L15、L874（`CreateNew/Write/None`）、L888；Task L71；manifest L30/L31 |
| follow-up #3 状态措辞 | 非实质差异 | Task L97 `ACTIVE / DISPATCH_PENDING` vs manifest L17 `READY / DISPATCH_PENDING` |

## 5. 非阻塞观察（范围内，不计为 finding）

1. **manifest L57 覆盖性措辞偏宽**：该句称 “R8, all Review Round 5 artifacts, review-fix self-checks and adjudications are protected by the capture inventory”，但冻结清单只含 initial/r2/r3/r4(-retry/-followup)/r5(-followup/-followup2) 的 Review 四件与 adjudication，**不含** follow-up #3 的 prompt/stdout/stderr/exit（它们按 Task L55/L97 属本轮可写并在 capture 前存在）。按“冻结时刻”读法该句成立（R8 路径 L733 说明清单是前瞻 capture 时刻的），故属歧义而非事实错误；且 Task L42 已要求 Codex 独立 pin follow-up #3 的 bytes/SHA，pre-run 又会覆盖全部 72 条。**最小修复（文档级）**：把该句收窄为 “…through follow-up #2…”，或注明 follow-up #3 artifacts 由 Codex pin adjudication 覆盖、不在冻结 capture inventory 内。**不要**把它们加进 script——改动字节会使 pin #4 与本轮 Review 失效。
2. **manifest L47 要求的 note 计数**：script L840 的“仅 symlink 跳过”分支只陈述理由、不含 `$repoSymlinkSkipCount`（“两者皆非零”分支含计数）。按 manifest L41 每仓 2148 个 staging 候选，实际应走含计数分支，materiality≈0；与 follow-up #2 非阻塞观察 #1 同一项，仍未处理（可选文档收窄）。
3. **pin #7 声明的 retry 机制未被结果artifact 直接见证**：pin #7 写 “stream source bytes through redirected stdin”，而 pin #4/#8 的 `childArguments` 只列 `-EncodedCommand`，无 stdin/input 字段（`stdin` 在三份 md 中零命中）。不影响 pin #4 的 source-pin 一致结论，属证据粒度问题。
4. **manifest 缺 pin #8 的 pin 行**：manifest 对 `r5-selfcheck`（L11）、`r5-selfcheck-retry`（L12）、`r5-reviewfix-selfcheck`（L14）、`r5-followupfix2-selfcheck`（L17）均给 bytes/SHA，唯独没有 `p02pre-r1f-r5-followupfix-selfcheck-20261011.json`（`2307 / FE2277D0…`）；F1 的存在性证据目前只在 adjudication L16 与 Task L38。可顺手补一行（纯文档，不改字节）。

## 6. 阅读范围（含越界披露）

**读毕（仅 pinned 8 份）**：#1 Task 全 99 行；#2 manifest 全 57 行；#3 script 全 889 行（分段读毕 L1–L889）；#4、#8 JSON 各 42 行；#5 adjudication 全 23 行；#6 stdout 全 97 行；#7 wrapper-attempt1 全 11 行。另对 #1/#2/#3 做**内容检索**（`grep`）以清点 protected 字面量与 `63`/`stdin`/Review 路径引用。

**越界披露（必须记录）**：我发起的一次检索把 path 设为仓库根 `G:\CODEX\New Manga`、`include=*.md`，pattern 为 `63 keys|63 unique|63/63|`63``。该检索**越出了“只读 8 个 pin”的边界**，返回了未列文件的匹配行：`doc/REBASELINE_PLAN.md` L5、`doc/STATUS.md` L5/L17/L29、`doc/tasks/P02.md` L24、`verification/P02/codex-checkpoint-p02pre-r1f-20261011.md` L21，其中仍写 `protected-hash keys=63/63 unique`，并把运行状态写作 `R5_FOLLOWUP2_REVIEW_ACTIVE / CLI 仍运行中`。我未用 `read` 打开这些文件、未复算其状态，也**没有**把该发现计入本轮 finding（按本轮“只报告与 8 个输入直接相关的可复现 findings”的约定，它不位于 pinned 输入内）。**范围外观察**：若这些行确实仍然陈旧，则 F2 的 63→72 更正与 follow-up #3 的状态推进似未传导到 Task L55 授权 Codex 更新的治理/导航层；建议 Codex 在 pin adjudication 时顺带独立确认并做治理同步（纯文档，不改候选字节，无需重开本轮 Review）。其余检索（path 限定在 pinned 文件或 `verification/P02/p02pre-r1f-*.md`）均未越界。

**未执行**：没有运行任何命令、脚本、测试、R8、capture、Build/Cargo、AC1–AC7；没有 `Test-Path`/`Get-Item`/`Get-FileHash`/`Get-ChildItem`/`Get-Acl` 或任何 getter；没有读取 `.tmp.driveupload` 内容或元数据（连列举也未做）；没有写入、创建、修改、删除、移动任何项目文件。

**残余未证限制**：(a) 全部 bytes/SHA 未由我复算（`UNPROVEN`）；(b) pin #8 的“当前 PRESENT”是 Codex 记录的单次 host 观测，我无法复现；(c) R1 继承清单（12 input roots / 13 output leaves / 3 canary / 35 env / getter 顺序 / protected 集合与 R1 manifest 的逐项等价）因 R1 manifest 不在授权范围，`UNPROVEN`；(d) self-check 属 Codex 自有产物，不是独立验证；(e) 本 Review 为纯静态，不替代 R8、pre-run adjudication 与 post-run 五态裁定。

## 7. 不授权声明

本 Review 不对 R8、capture、Build/Cargo、AC1–AC7 或任何 Gate 给出批准；`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE` 一律不变。

---

## 推荐下一步（供转发给 Codex /root）

> **Task=`P02PRE-R1F`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。DeepSeek Harness follow-up #3=`APPROVED (0/0/0/0)`（仅覆盖 8 个 pinned 输入），并附 4 项范围内非阻塞观察与 1 项范围外治理同步提示（见 Review）。请作为 Author/Adjudicator 执行：(1) 用 `Get-FileHash`/`Get-Item` 独立复算本轮 8 个 pin 的 bytes/SHA 并记录 pin/range adjudication；(2) 顺手处理纯文档项——manifest L57 覆盖性措辞收窄、可选的 L47 symlink-only note 计数、为 `p02pre-r1f-r5-followupfix-selfcheck-20261011.json`（`2307 / FE2277D0…`）补 pin 行、并在治理同步中核对 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/tasks/P02.md`、`codex-checkpoint-…` 是否仍残留 `63/63 unique` 与 `R5_FOLLOWUP2_REVIEW_ACTIVE`（**不得**改动 capture script 字节，否则 pin #4 与本轮 Review 失效）；(3) 完成上述后，才按 Task L43 对**同一冻结 bytes** 运行 Windows PowerShell 5.1 `ScriptBlock::Create` parse-only，落唯一 `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json`（`captureScriptInvoked=false`）；(4) R8=`PARSE_OK` 后再做独立 pre-run adjudication（身份/SID、roots/refs、status/index、输出目标 absent、全部 72 条 protected 存在性与 hash 重验），唯此才可按 manifest exact argv 运行一次 capture。任何 mismatch 保留原始 partial evidence 并停止，不重试、不清理。

在收到 Codex 的 pin/range adjudication 结果之前，无需其他 Agent 动作。
