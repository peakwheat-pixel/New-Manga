# P02PRE-R1H-R6-EXEC-A5 follow-up #1 独立静态 Review（非作者）

## 0. 结论

**Verdict：`CHANGES_REQUESTED`**

**Findings 计数（本轮新增）：P0 = 0，P1 = 0，P2 = 3，P3 = 2。**

依据：executor 本体的写入/边界/子进程内容未发现 P0/P1 级执行安全缺陷（Q1 内容层面通过）；但 follow-up manifest 自身 15 项 input pins 中，至少 2 项（`doc/tasks/P02PRE-R1H-R6-EXEC-A5.md`、`p02pre-r1h-round6-integration-protocol-attempt5-20261012.md`）的 `bytes/sha256` 与同一 review 链上其他冻结 manifest / Handoff 明显不一致，"12/12 MATCH" 记录因此不可复核；另 checkpoint reference 无法经只读文本通道读取。attempt5 protocol §7（`:108`）明文 "Any unresolved P0/P1/**P2** finding means `CHANGES_REQUESTED`"，故按该 Task 自己的放行规则不能给出 `APPROVED_STATIC_CONTENT`。

**本 verdict 不授权执行。** attempt5 executor、`File.Replace`、parser/selfcheck、final pre-run 一律仍为 `NOT_RUN`；仍需 Codex adjudication、Parser/selfcheck、逐项 final pre-run 通过。

---

## 1. 方法与边界声明（含偏差）

- 仅使用**只读文本读取**通道（`read` / `read_image` 未用）；**未执行**任何 shell/PowerShell 命令、**未运行**脚本或测试、**未计算** hash、**未读取** `.git/index`、**未写入/创建/修改**任何文件、**未触碰** `.tmp.driveupload`、**未**做 ACL/权限操作、**未**访问任何 OS/API。
- **需要披露的方法偏差（自行记录，供 Codex 判定是否为 deviation）**：为定位 follow-up manifest 的文件路径，我使用了一次工作区只读**路径名模式查找**工具（按 Task ID 与 `*pins*` 文件名模式），其返回值为文件路径清单（34 条 `*pins*` 路径）。该操作不读取文件内容、不做内容检索（未使用 grep/rg）、不调用外部程序；但按本 Task 早期 A4 review 对 "只读工具限制" 的从严解释，这属于**目录级路径枚举**，我如实标记为 `WITH_DEVIATION`，不声称为 PASS。
- 本次结论仅为**静态内容/记录一致性**判断，不构成执行证据、`PRE_RUN_PASS`、Gate 或 AC PASS。

---

## 2. 逐问核验

### Q1 — attempt5 executor 相对 attempt4 的变更面（内容层面：成立）

两份 executor 均为 **638 行**。我按 `1–70`、`71–400`、`401–638` 三段逐行对照，差异**恰为 6 处**，与 Handoff `:7` 与初轮 review Q1 一致：

| # | attempt5 路径:行 | attempt4 原文 → attempt5 现值 | 类别 |
|---|---|---|---|
| 1 | `p02pre-r1h-round6-integrator-attempt5-20261012.ps1:1` | `attempt 4` / `attempt4 review` → `attempt 5` / `attempt5 review` | attempt label/header |
| 2 | `...attempt5-20261012.ps1:34` | `schema = 'P02PRE-R1H-round6-attempt4'` → `...attempt5'` | schema |
| 3 | `...attempt5-20261012.ps1:26` | `$IndexHash = 214767403C469B15…08F3B89C` → `C5CA88842173A8FE…3A692B68` | root index pin |
| 4 | `...attempt5-20261012.ps1:366` | root `expectedHead` `cddff584…bc7eb9` → `343895fb…f967607` | root HEAD pin |
| 5 | `...attempt5-20261012.ps1:367` | root `expectedTree` `c25d051a…a19f2b` → `e12bd627…86ec63` | root tree pin |
| 6 | `...attempt5-20261012.ps1:623` | 注释 `The attempt4 FAILURE phase…` → `The attempt5 FAILURE phase…` | failure label |

**未变更项（逐行一致，仅列可定位锚点）**：Owner pining `:7` `$Owner`、`:365` Owner branch `agent/codex/P02PRE-R1H`、`:366/:367` Owner HEAD `c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d` / tree `96e7273ddd5fd27bee567bba27f19453cabe0842`、`:373` Owner parent `dd5d2e3bc8e0702da9d059131f6364a997897661`；路径/输出表 `:11–21`；四个候选 hash `:22–25`；ACL SDDL `:27` 与 `:437/:539` 断言；子进程 allowlist `:277–278`、Git argv `:346`、两个 validation child `:574`、`:583–584`；写入边界 `:463`、`:493`（`CreateNew`）与唯一 `:543` 三参数 `[IO.File]::Replace`（`$ReplaceCalls++` 在 `:542`）；全部执行/失败逻辑 `:480–638`。

结论：**Owner pins、算法、路径、ACL、子进程、API、写入边界在内容层面未变**。注意：这是**逐行内容比对**结论，**不是**字节/SHA-256 结论（见 Q3、§3 F-01）。

### Q2 — protocol 修复项、名称一致性与 attempt4 root 残留

- **`` `r`n `` 字面量**：当前 `p02pre-r1h-round6-integration-protocol-attempt5-20261012.md` 的 author 区（`:5`、`:8`、`:9`、`:10`）及全文 108 行中**不存在** `` `r`n `` 字面量；attempt5 executor `:1–2` 头部注释亦无。该修复在**当前冻结文本中已就位**。但修订前文本不在 `inputs[]` 内，故"修复了哪一处"无法由我做字面 diff。
- **`APPROVED_STATIC_CONTENT` 名称一致性（成立）**：protocol `:107–108` 现写明 "the independent static-review verdict is `APPROVED_STATIC_CONTENT`"；全文已**不再出现** `APPROVED_STATIC_PROTOCOL`（旧串仅存于不可改的 attempt4 protocol `:107`）。Task `doc/tasks/P02PRE-R1H-R6-EXEC-A5.md:62`、初轮报告 `codex-subagent-…attempt5-exec-review-20261012.md:12/35`、postpins `:5` 均用同一名称。
- **准入/执行边界一致性（基本一致，1 处口径不一致）**：protocol `:108` = Codex pin 复算 + adjudication + 独立 final pre-run `PRE_RUN_PASS` 才可执行；Task `:24`、`:33–34`、Handoff `:12`（"Review、adjudication、parser/selfcheck、final pre-run and execution remain pending"）均与之一致，且**均未**把静态批准当作执行授权。**不一致点**：protocol `:108` 的阻断集合是 `P0/P1/P2`，而 Task AC3（`:32`）只写 "任何 P0/P1 或未解决的执行安全 finding 都阻止执行"。
- **attempt4 root baseline 残留**：attempt5 executor / protocol / Handoff 中**未发现** `cddff584…`、`c25d051a…`、`214767…` 作为有效 pin。旧值仅出现在 `doc/tasks/P02PRE-R1H-R6-EXEC-A5.md:22` 与 `doc/tasks/P02PRE-R1H-R6-EXEC-A4.md:93` 的**历史叙述**（明确描述 A4 已在只读 pre-run 停住的原因），非绑定 pin，判定为**有意的历史记录，不构成残留基线**。attempt5 protocol `:16` 也只用文字描述该 precondition BLOCKED，未沿用旧 hash。

### Q3 — 记录准确性 / 自洽性 / 明显不一致（**发现实质问题**）

**`checkpointIncludedInInputPins=false` 与 checkpoint reference 自洽（成立）**：follow-up manifest `:6` = `false`、`:7` = `checkpointReference`；`:22–98` 的 15 项 `inputs[]` 中**不含**任何 checkpoint 路径 → metadata 与 pin 列表自洽。初轮 pre-pins（`codex-p02pre-r1h-attempt5-exec-review-pins-20261012.json:6`）同为 `false`，其 12 项 `inputs[]`（`:14–27`）同样不含 checkpoint → 亦自洽。

**Task 对初轮 review 的记录：技术结论准确，但继承了 postpins 的内部矛盾。**

- 准确项：Task `:62` 的 `APPROVED_STATIC_CONTENT`、`P0/P1/P2/P3=0/0/2/3`、`execution remains NOT_RUN`、`DSH independent hashes=NOT_VERIFIED`，均与初轮报告 §1/§3/§4 及 postpins `:5–13` 一致；Task `:30–37` 的 AC 复选框全部 `[ ]`，与 NOT_RUN 状态一致。
- 措辞问题：`:62` 把两个 P2 概括为 "P2 metadata closure"，**低估了 P2-001**（它是 pin/hash 独立校验缺口 + root ACL/streams 复核项，不只是 metadata）。
- 未支持项：`:62` 记 `Codex pre/post inputs=12/12 MATCH`，但该记录（postpins `:13` 与各行 `match: true`）**至少 2 行与同一 review 的 pre-pins 值互相矛盾**。

**明显不一致（无需 hash 即可判定，逐项精确 pin）**：

| 路径 | 初轮 pre-pins（input #13） | 初轮 postpins（input #15） | follow-up manifest（本轮 input #1/#8） | Handoff（input #9） |
|---|---|---|---|---|
| `doc/tasks/P02PRE-R1H-R6-EXEC-A5.md` | `:15` **9073 / `7FCFF7A1…D3FE`** | `:22–27` **7637 / `696D2E69…2F971`**，`match:true` | `:24–27` **9073 / `7FCFF7A1…D3FE`** | — |
| `…integration-protocol-attempt5-20261012.md` | `:22` **11641 / `0E80C831…6AF3`** | `:77–84` **11503 / `3BA69EA4…763C`**，`match:true` | `:59–61` **11641 / `0E80C831…6AF3`** | `:11` **11503 / `3BA69EA4…763C`** |

即：同一路径在同一 review 链上存在**两套互斥的 bytes/SHA-256 冻结值**；postpins 的 `expected`/`actual` 自行相等并记 `match:true`，但其 `expected` 与 pre-pins 清单不符，因此 `codexPrePostPins: "12/12 MATCH"`（postpins `:13`、Task `:62`）**无法复核**。其余 10 项（含 attempt5 executor `43464 / 9B52BEA5…AA10`、Handoff `2283 / 2E328677…6F15`）在三处取值一致。可归因的两种解释（**我无法独立区分**）：(a) Codex 在初轮 review 后按 P2-002/P3-003 修订了 pre-pins 与 protocol，pre-pins 被更新为"修订后字节"，而 Handoff `:11` 与 postpins 保留旧值未同步；(b) pre-pins / follow-up manifest 这两项 pin 本身取错。无论 (a)/(b)，冻结证据链存在未闭合矛盾。

**另**：follow-up manifest `:99` `executionEvidence="NOT_RUN"`、`:111` scope 与 protocol §1/§6、executor `:34` `state='NOT_RUN'` 一致，未把计划/静态项写成 PASS。

### Q4 — 初轮 findings 的 disposition（逐项）

| 初轮 ID | Disposition | 依据（精确路径:行 / pin） |
|---|---|---|
| **P2-001**（无法 hash；要求 Codex 复算 12 输入 + attempt5 三件套 + `.git/index` 并记 MATCH，另只读复核 root 路径链 ACL/streams） | **部分解决（未闭合）** | Codex 侧记录存在：`codex-p02pre-r1h-attempt5-exec-postpins-20261012.json:13` `12/12 MATCH`、`:20–116` 逐行 `match:true`；但其中 `:22–27`、`:77–84` 与 `codex-p02pre-r1h-attempt5-exec-review-pins-20261012.json:15`、`:22` 矛盾（见 Q3），故 MATCH 不可复核。`.git/index` 只在 postpins `:18` `liveBase.indexSha256` 与 follow-up manifest `:12` 作**声明**，`inputs[]` 内无独立 `.git/index` 读取证据；P2-001 要求的 root 路径链 ACL/streams 只读复核在 pin 集内**无证据**。本轮 15 项 follow-up pins 的 Codex MATCH 记录尚不存在（属待生成的 follow-up1 postpins）。**不混同**：DSH 侧（初轮与本轮）独立 hash 均为 `NOT_VERIFIED`（环境性 Win32 5 限制），既不能证明也不能否证 pin；Codex 的 `12/12` 是另一侧证据，二者不可互相替代，且该 `12/12` 目前自身有 2 行矛盾。 |
| **P2-002**（pins metadata 缺 `checkpointIncludedInInputPins`，要求与 `inputs[]` 自洽） | **已解决（文本层面）** | `codex-p02pre-r1h-attempt5-exec-review-pins-20261012.json:6` 现有 `"checkpointIncludedInInputPins": false`，`:14–27` 12 项 inputs 不含 checkpoint；follow-up manifest `:6`/`:22–98` 同构自洽。**保留限定**：初轮报告 `:30` 以 `:1-39` 引该文件（当时被引为**无**该字段），现文件为 41 行且含该字段；该文件是否在 review 后被编辑无法由 pin 集判定，属 provenance 保留项（不改变"当前文本已满足要求"的结论）。 |
| **P3-001**（Task 结果表残留 `NOT_RUN/待生成`，需 Review 落地后回填） | **已解决** | `doc/tasks/P02PRE-R1H-R6-EXEC-A5.md:62` 已回填初轮 static review 行（verdict/计数/NOT_VERIFIED/12-12 与证据文件）；`:63–66` 保持 `NOT_RUN`，与 parser/selfcheck、final pre-run、executor、post-run review 的实际未运行状态一致，未虚报。 |
| **P3-002**（protocol 写 "DeepSeek Harness **CLI**" 与派发口径歧义，要求记录实际通道/模型） | **部分解决（非阻塞）** | protocol `:6` 仍写 "DeepSeek Harness CLI (non-author; static review only)"。postpins `:4` 已记 `dshCliVersion: "0.2.0-rc.2"`，与 `doc/09_COLLABORATION.md:159`（真实 DSH CLI 派发口径）相容；但 `reviewer_model`、session ID、`web_visibility` 均未记录（对照 attempt4 adjudication `:7` "reviewer model was not reported"，及协作协议 `:163` 要求记录版本/worktree/session 并在不可见时标 `web_visibility=unverified`）。 |
| **P3-003**（protocol `:107` 原文 `APPROVED_STATIC_PROTOCOL` 不是本 Task 可出具的 verdict） | **已解决（文本层面），但引出新口径缺口** | 当前 `…protocol-attempt5-20261012.md:107–108` 已改为 `APPROVED_STATIC_CONTENT` + Codex pin recheck/adjudication + 独立 `PRE_RUN_PASS`，全文无 `APPROVED_STATIC_PROTOCOL`。**但** `:108` 的阻断集合（P0/P1/P2）与 Task `:32` AC3（P0/P1）不一致，且初轮 review 是在 2 个 P2 未闭合的情况下给出 `APPROVED_STATIC_CONTENT`——按 `:108` 字面应为 `CHANGES_REQUESTED`（见 §3 F-02）。 |

### Q5 — Gate / AC 状态（按 manifest 原值，不做任何提升）

依 follow-up manifest `gateState`（`:100–110`）与 `:99`，原样记录：`private_registry_absence=UNPROVABLE`；`TechnicalGate=NOT_SATISFIED`；`OwnerRiskAcceptance=APPROVED`；`GateDisposition=WAIVED_BY_OWNER`；`BuildAuthorization=AUTHORIZED_WITH_EXCEPTION`；`BuildGate=BLOCKED`；`HardBuildBarrier=EFFECTIVE`；`BuildCargo=NOT_RUN`；`SystemAC1toAC7=BLOCKED / NOT_RUN`；`executionEvidence=NOT_RUN`。与 protocol `:88–96`、executor `:40–47`、Task `:70` 取值一致（executor `:44` 另含精确原文 `technical condition unmet; user explicitly accepted residual risk`；manifest `gateState` 未列该句，属子集，不构成矛盾）。**本 Review 不解除任何 Gate、不把任何项写成 PASS。**

---

## 3. 本轮 Findings

| ID | 级别 | 精确 pin 路径 / 行 | 影响 | 要求修正 |
|---|---|---|---|---|
| **F-01** | **P2** | `verification/P02/codex-p02pre-r1h-attempt5-exec-review-followup1-pins-20261012.json:24–27`（A5 Task `9073/7FCFF7A1…`）与 `:59–61`（protocol `11641/0E80C831…`）；对照 `codex-p02pre-r1h-attempt5-exec-postpins-20261012.json:22–27`（`7637/696D2E69…`）、`:77–84`（`11503/3BA69EA4…`）、`:13`（`12/12 MATCH`）；`codex-p02pre-r1h-attempt5-exec-review-pins-20261012.json:15`、`:22`；`p02pre-r1h-round6-attempt5-exec-handoff-20261012.md:11` | 同一 review 链上同路径出现两套互斥 bytes/SHA-256；postpins 的 `expected` 与 pre-pins 不符却记 `match:true`，使 `12/12 MATCH`（Task `:62`）不可复核，直接冲击 Task AC1 的"逐路径 diff 与 SHA-256"要求 | Codex 用同一批次只读复算重跑一遍，明确区分"review 时字节"与"修订后字节"，并把 Handoff `:11`、postpins 相应行的旧值标注为 `SUPERSEDED` 或修正；在 follow-up1 adjudication 中给出唯一一套权威 pin |
| **F-02** | **P2** | `…protocol-attempt5-20261012.md:108` vs `doc/tasks/P02PRE-R1H-R6-EXEC-A5.md:32`（AC3）vs 初轮报告 `:12/35`（2 个 P2 未闭合仍给 `APPROVED_STATIC_CONTENT`） | 放行规则口径不一致：protocol 要求 unresolved P2 ⇒ `CHANGES_REQUESTED`，Task AC3 只列 P0/P1；导致"当前状态是否已满足静态放行"事后不可判定，并可能被读成静态 Gate 已放行 | 明确统一阻断集合（建议以 protocol `:108` 的 P0/P1/P2 为准），并在 adjudication 中对 2 个 P2 逐项标注 `RESOLVED / SUPERSEDED / OPEN` |
| **F-03** | **P2** | `verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt5-review-findings-20261012.md`（由 follow-up manifest `:7` 作 `checkpointReference`，Task `:48` 指定为本轮 findings 的 rolling checkpoint） | 该 `.md` **无法通过只读文本通道读取**（读取工具判定为 binary）。因 `checkpointIncludedInInputPins=false`，它不影响 pin 集正确性；但它是本轮 disposition 的指定记录载体，其内容与 finding 处置**完全未核实**。原因（编码/内容）我未独立判定，也未尝试其他通道 | 由 Codex 确认该文件编码与内容；若确为不可读文本，请在可读位置（Task/adjudication）重述 disposition 记录 |
| **F-04** | **P3** | `doc/tasks/P02PRE-R1H-R6-EXEC-A5.md:46`（初轮 review 证据目标含 `…exec-review-20261012.prompt.md`、`dsh-…stdout.jsonl`、`.stderr.log`、`.exit`）vs follow-up manifest `:22–98`（仅列入 pre-pins、report md、postpins） | 初轮 raw transcript（stderr 记录其 `SetNamedSecurityInfoW Win32 5` 过程）未纳入本轮 pin 集；初轮报告 `:39` 的"未使用 grep/search、无越界读取/写入"等方法学声明**无法从被审 pin 集复核**（对照 attempt4 曾因 transcript 发现 grep deviation） | 在 adjudication 中把初轮 prompt/stdout/stderr/exit 一并 pin 或明确记为未纳入并说明理由 |
| **F-05** | **P3** | `…protocol-attempt5-20261012.md:6`（"DeepSeek Harness **CLI**"）；`codex-p02pre-r1h-attempt5-exec-postpins-20261012.json:4`（仅有 `dshCliVersion`） | 通道口径歧义仅部分闭合：记录到 CLI 版本，但缺 reviewer model / session ID / `web_visibility`（`doc/09_COLLABORATION.md:159/163`） | 在 adjudication 中补记通道与模型可得性（不可得时记 `reviewer_model=UNKNOWN`、`web_visibility=unverified`） |

---

## 4. 未读取 / 未核实清单与未覆盖风险

**未能读取**
1. `verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt5-review-findings-20261012.md` —— 只读文本通道返回 `binary file`，内容**无法核实**（对应 F-03）。

**部分读取（非 inputs 全文）**
2. `doc/tasks/P02PRE-R1H.md`（65067 bytes）：只精读 A5 相关段 `:262–289`（含 reviewer 引用的 `:287`），其余未重读。
3. `doc/09_COLLABORATION.md`（19131 bytes）：只读 `:140–185`（含 reviewer 引用的 `:157–163`），其余未重读。

**未纳入 pin 集、故未审**
4. attempt2/attempt3 protocol、`p02pre-r1h-round6-attempt4-selfcheck-20261012.ps1`、`p02pre-r1h-selfcheck.ps1`、`p02pre-r1h-capture.ps1`、`doc/STATUS.md`、初轮 prompt/stdout/stderr/exit（见 F-04）。

**未覆盖风险（明确保留）**
5. **无任何字节/SHA-256/`.git/index` 独立校验**：`head`/`tree`/`indexSha256` 归因、8 个写入路径的"当前 absent/unignored"、目标 ACL/streams 均属 `NOT_VERIFIED`。这是结构性（本会话无法 hash）限制，**不是** pin 错误证据，也**不是** pin 正确证据。
6. attempt5 executor 的 native interop / Reflection.Emit ABI / `Marshal.GetLastPInvokeError` 行为、ACL 与 streams 实际状态、进程观察窗口等，按设计仍为 `NOT_VERIFIED`（executor `:49–53` 自述的 race 与 no-timeout 限制原样保留）。
7. `private_registry_absence=UNPROVABLE` 与 Owner 风险接受未被本 Review 改变或重新评估。

---

## 5. 放行边界

- 本报告**不授权**调用 attempt5 executor，**不构成** `PRE_RUN_PASS`，**不构成** Build Gate / AC1–AC7 任何 PASS，**不解除** Hard Build Barrier。
- 放行顺序仍为：Codex 处置 F-01/F-02/F-03（并选择性处置 F-04/F-05）→ 独立复算 follow-up 15 项 pins 与 `.git/index` 并记 MATCH → adjudication → Parser/selfcheck → 逐项 final pre-run → 方可最多调用一次 attempt5 executor；任一不符即停，不重试、不清理、不回滚。
- 本轮 verdict 为 `CHANGES_REQUESTED` 的依据是**记录/pin 证据完整性**（F-01/F-02/F-03），不是 executor 内容缺陷；若 Codex 判定 F-01 属"修订后 pre-pins 被更新、Handoff/postpins 旧值未同步"的纯记录滞后，则应以修正记录 + 复算 MATCH 闭合，而不是直接降级为 PASS。

**推荐下一步（不由我执行）**：由 Codex 对 F-01/F-02/F-03 逐项 adjudicate，并出具 follow-up1 的 `codex-p02pre-r1h-attempt5-exec-review-followup1-postpins-20261012.json`，在**同一批次只读复算**中给出唯一权威 pin 集（含 `.git/index`）与 `MATCH` 记录；在该记录落地前，attempt5 executor 保持 `NOT_RUN`。