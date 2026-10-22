# H2 新时点证据对 H1 当前结论的适用性 — 独立静态 Review（P02PRE-R1H-H1-CURRENT-INPUT-REVIEW）

## 1. 身份与冻结输入

| 项 | 值 |
|---|---|
| Task | `P02PRE-R1H-H1-CURRENT-INPUT-REVIEW`（owner Codex /root，reviewer DSH 非作者） |
| Base commit | `343895fb5f0329c0c07a7104ec321b698f967607` |
| 输入 manifest | `verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/review-inputs-r1.json`（frozenAtUtc `2026-10-13T11:43:38Z`，14 项输入；`h2EvidenceHead=06990b7993d042ae5e74ab479e291e494b622588`） |
| H1 subject | Task `P02PRE-R1H-R6-ZCODE-H1`；v2 结果 `verification/P02/codex-p02pre-r1h-attempt6-final-pre-run-v2-20261012.json`（声明 15768 B / `23ac80e2…daf877`）；verdict `PRE_RUN_PASS`（23 PASS / 1 NOT_VERIFIED）；`timestamp_utc 2026-10-12T11:04:51.4885731Z`，写入窗口 ≈ `2026-10-12 10:50:18Z–11:04:51Z` |
| H2 证据 | RunId `h2-20261013-de77a42fccca4193925767ba4e414970`；raw NDJSON 声明 788029 B / `32cd72b7…a2179`；运行完成 `2026-10-13T10:39:08Z`（观测时间跨度 `10:39:07.246Z–10:39:08.674Z`）；78 observations（54 in-process-getter / 24 helper-process）、55 checks |
| 我的输入读取 | 14/14 项清单路径均已按精确路径只读检查（关键件：本 Task 契约与 manifest、H1 v2 JSON 全文、H1 裁决全文、H1 P2-1 段落、H2 runtime json/md、raw NDJSON 行首）；其中 5 项较大叙事件由只读子代理按同一精确路径提取并回报行号原文（H1/H2 Task 快照、H1 Review、H1 input verification、H2 裁决/pin 验证/Handoff/R3 Review） |

## 2. 判定

**Verdict：`APPROVED_STATIC_CONTENT`**

含义严格限定为：**本次适用性裁决本身没有未解决的 Review finding**——输入集完整、pins 无内部矛盾、15 项 applicability 已逐项作出结论。**它不代表 H1 通过**：H1 的 Review 仍为 `CHANGES_REQUESTED`、P2-1 仍 `OPEN`、X6 仍不可释放（§5）。本次未发现 P0–P3 缺陷（§4）。

## 3. 逐项 applicability（H2 是否有任一具体 observation 构成 H1 v2 原始引用来源）

判定统一为 **NO（不能构成原始来源）**。三个必要条件（同一时间点 / 同一操作与输入 / item-level provenance，或冻结证据可复算的确定映射）**无一满足**，故每项逐条列出断点。H2 侧"最近对应观测"仅按 observation id/kind/timestamp 的可见行首认定（其**值**多在第 2000 字符截断之外，见 §6）。

| # | H1 ID（v2 JSON 行） | H1 的泛化 evidence | 最近的 H2 观测（仅名称层相似） | 断点（不满足项） |
|---|---|---|---|---|
| 1 | `tools`(172) | `"collection A"` | `tools-pwsh`(seq15)、`tools-git-version`(seq16) | 时点 10-13 vs 10-12；H1 的 A 阶段采集由 H1 write script 组织，H2 是另一程序；无 H2→H1 指针映射 |
| 2 | `a-identity`(180) | `"collection A"` | `identity-windows`(seq17)、`whoami-all`(seq18) | 同上；且 H1 该项还含 `WindowsIdentity.GetCurrent`/CloudAP None/非管理员，H2 覆盖不全（另见 §4 OBS-1 的值同现象） |
| 3 | `b-registry-wer-localdumps`(188) | `"collection A"` | `wer-localdumps-readonly`(seq19) | 时点/操作/输入三项均异；H1 记录 "7 subKeys/valueNames empty"，H2 记录形式不同且值不可读 |
| 4 | `b-profile-moniker`(196) | `"collection A"` | `profile-moniker-packages-probe`(seq20) | 同上；H1 该项为 "liveProbe NOT_RUN + Packages exists=false" |
| 5 | `c-temp-paths`(204) | `"collection A"` | `temp-tmp-env`(seq21)、`path-probe-*`(seq24–29)、`exclusion-scope-dynamic-paths`(seq23) | 同上；H2 的探查集为 H2 自己的路径清单 |
| 6 | `e-root-refs`(244) | `"collection B"` | `refs-root-*`(seq30–34，5 条) | 同一对象类（root refs）但为**后来观测**；H1 的 B 阶段 raw item 不在任何冻结输入内 |
| 7 | `e-owner-refs`(252) | `"collection B"` | `refs-candidate-*`(seq35–39，5 条) | 同上（H2 用 "candidate" 命名对应 H1 的 owner worktree，属命名相似） |
| 8 | `e-agy-refs`(260) | `"collection B"` | `refs-a6-*`(seq40–41) | 同上（"agy"/"a6" 亦仅命名相似） |
| 9 | `e-root-status`(268) | `"collection B"` | `status-root`(seq42) | 同上；H1 该 span 的完整 status argv 未逐字记录（H1 裁决 P3-5） |
| 10 | `e-owner-status`(276) | `"collection B"` | `status-candidate`(seq43) | 同上 |
| 11 | `e-agy-status`(284) | `"collection B"` | `status-a6`(seq44) | 同上 |
| 12 | `e-root-index-hash`(292) | `"collection B"` | `root-index-hash-before`(seq5)、`root-index-hash-after`(seq77) | 同上；H2 前后两次读同一 `.git/index` 只证明 H2 窗口内未变 |
| 13 | `f-protected-file-pin`(300) | `"collection B"` | `protected-selfcheck-before`(seq4)、`protected-selfcheck-after`(seq76) | 同上；H1 该 pin 属 H1 的 frozen_pins（57648 / `977C9943…`），H2 为再次测量 |
| 14 | `h-targets-initial`(324) | `"v2 precheck"` | `target-1..7-absent/parent/check-ignore`(seq45–65)、`output-path-chain-volume`(seq1) | 对象集合不同：H1 是 **v2 的 4 个输出目标**（`2026-10-12T10:50:18Z` 全部 absent、4× exit=1）；H2 是 **H2 自己的 7 个目标** |
| 15 | `h-targets-final-prewrite`(348) | `"write script guard"` | `output-path-chain-volume`(seq1) 的 pre/post CreateNew 分支 | H1 断言的是"单次 CreateNew 序列前的最后 absent 复核"，取决于 H1 write script 本身；该脚本及 `%TEMP%` 模板均未被 pin（H1 裁决 P3-1、P2-1） |

统一断点（适用于全部 15 项）：

1. **同一时间点不成立**：H1 v2 窗口为 `2026-10-12 10:50:18Z–11:04:51Z`；H2 唯一一次调用为 `2026-10-13T10:39:07–08Z`（相隔约 23.5 小时、跨日）。
2. **同一操作/输入不成立**：H1 的 `collection A/B`、`v2 precheck`、`write script guard` 是 H1 v2 自身 write script 组织的采集阶段（其 checks 模板被暂存于仓外 `%TEMP%`，`harnessNote` 自述 6914B / `0D225C27…`）；H2 是**另一程序**（集成 commit `1924fbb4…` 的 `tools/p02/h1-raw-pre-run.ps1`）由 H2 launcher 单次调用，使用 H2 自己的冻结输入集。
3. **item-level provenance 不可转移**：P2-1 要求 15 项指针在 H1 Review **固定输入集内**可解析；该固定集为 13 项 pins（v2 四件、attempt1 四件、H1/A6 Task、protocol/handoff/executor），**H2 的任何产物都不在其中**；H2 的 raw pointer 只证明 H2 自己的观测。
4. **无确定映射可复算**：14 项冻结输入中**没有任何一份**给出 H2 observation ID ↔ H1 check ID 的映射（H2 裁决明确 "does not substitute for H1 v2… H1 v2/P2-1 unchanged"；H2 Task 亦自述 `NEW_TIME_EVIDENCE / CANNOT_SUBSTITUTE_V2_TIME_EVIDENCE`）。按名称相似（`refs-root-*`↔`e-root-refs` 等）建立映射被本 Task 明文排除；按"同一对象"建立映射亦不可行，因为 H1 该项**恰恰缺失**它观察了哪个 item 的原始记录——这正是 P2-1 的缺陷，用后来的测量无法补回。
5. **值相同也不构成来源**（见 OBS-1）。

## 4. Findings

**P0 = 0，P1 = 0，P2 = 0，P3 = 0**（本次适用性裁决无未解决 finding）

信息性观察（**不计 finding**，仅防误读）：

- **OBS-1｜最接近的"同值"案例仍不可适用**：H2 `whoami-all`（`2026-10-13T10:39:07.5986658Z`，helper-process，`whoami.exe` `["/all"]`，cwd `G:/CODEX/New Manga`，allowedExit `[0]`）的 `output.stdout` 为 `bytesCount 3695 / nulCount 0 / sha256 25C641BAA11A2D597E70DDB3A7A76ADBD1F1574BF81C0450BB768973A3000EB0`，与 H1 v2 `a-identity` 记录的 whoami stdout（`3695B`，同一 sha256）**逐字节相同**。这证明"值一致"确实存在，但**不**满足三条件：它是同一主机同一身份在**次日**的第二次测量，且没有任何 H1 侧指针能被它解析。此例正好说明"相似/相等 ≠ 同一时点原始来源"。
- **OBS-2｜两组"15 项"不可互借**：H1 的 15 项是 v2 checks 的泛化 evidence 指针（本表对象）；H2 Task 另有一组"15 项 provenance 由 H2 自身 raw pointer 支撑、不借用旧 v2 observed"（H2 Task L54）。二者是不同集合，禁止互相引用。
- **OBS-3｜H1 快照措辞存在易混点**：H1 Task 快照同时出现"13 项输入 pins 固定 / 13/13 pre/post 匹配"（L117–118）与"15/15 冻结 pins"（L29）。二者所指不同（前者 = H1 Review 的 13 项固定输入；后者 = 15 项 check 侧的核验表述），不影响本次结论；建议在 H1 当前态摘要下次更新时（H1 P3-4 已要求更新当前态）统一口径。
- **OBS-4｜15 项并非"全部零证据"**：H1 Task 快照记录其中 `e-root-status` 与 `e-agy-status` 两个 span 已由 Codex 独立复算并被接受为**部分来源**（`79291B/0DB72CDA…`、`223B/25316B54…`），其余 13 项无合格 source。H2 对这两组都**没有**新增可采纳来源。

## 5. 对 H1 当前状态的建议（不改写历史）

| 项 | 建议（保持不变） | 依据 |
|---|---|---|
| H1 v2 执行 verdict | `PRE_RUN_PASS`（23 PASS / 1 NOT_VERIFIED）**原样保留、不改写、不据此升级** | H1 裁决 L12/L14；H1 Task 快照 |
| H1 Review verdict | `CHANGES_REQUESTED`（P0=0/P1=0/P2=1/P3=6）**不变** | H1 裁决 L6；H1 Review L78 |
| P2-1 | **保持 OPEN**；H2 不能关闭它（本次 15/15 不适用） | H1 裁决 L20/L22/L24；Task 契约 L40/L47 |
| X6 eligibility | **BLOCKED / 不释放**；不得登记 X6 Task；且不得把 v2 status 快照当作 X6 S0 基线 | H1 裁决 L14/L56/L80；H1 Task 快照 L119 |
| Gate 原值 | 全部不变：`Technical Gate=NOT_SATISFIED`、`private_registry_absence=UNPROVABLE`、`Build Gate=BLOCKED`、`Hard Build Barrier=EFFECTIVE`、`Build/Cargo=NOT_RUN`、`AC1–AC7=BLOCKED / NOT_RUN`、`dynamic process closure=REQUIRES_ACTIVE_TEST / NOT_RUN` | H1 裁决 L66–78 |
| H2 证据处置 | 可继续作为**新时点证据**（其自身已获准集成），但**不得**被引用为上述 15 项任一原始来源，也不得充当 X6 S0；H2 的 7 项 notRun scope（含 executor/build/AC/sandbox/observer/profile live probe）决定它不构成"完整新 PRE_RUN_PASS" | H2 裁决 L13/L43；runtime-verification-r2.json notRunScopeItems |

**后继最小解锁建议（不重跑、不调 executor、不伪造）**：按 Task 契约 L58 与 H1 裁决 L24 的允许方向，只探索**已存在的 H1 侧原始材料**——(a) `harnessNote` 指名的 `%TEMP%` 暂存 checks 模板（6914B / `0D225C27…`）是否仍存在且可读；(b) 已 pin 的 H1 v2 `.stdout.log`（82455 / `87D03E50…`）、`.stderr.log`（532 / `4476997D…`）与 attempt1 四件是否含这 13 项的 item-level 原始捕获。若存在，按 H1 裁决允许的两条路径之一处理：**以新的、显式 pin 的证据名引入可追溯原始材料**，或**给出到既有 pinned source span 的确定映射**，随后取得聚焦的独立 re-review；若不存在，则如实登记永久性 provenance gap 并交用户/Owner 做范围决策。任何未来新的完整 pass 必须是**新证据类别**、自带 PRERUN，永不作为 v2 的替代。

## 6. 审查限制（必须与结论一并阅读）

1. 本会话**无法执行任何命令**（`pwsh` 在启动阶段即报 `SetNamedSecurityInfoW … Win32 5` 拒绝访问；子代理复测相同；提权无可用审批通道）。因此 14 项输入的 **SHA-256/bytes 均为清单声明值，未由我复算**；"审查前后 pins 不变"由 Codex 独立复核，而非本报告。
2. raw NDJSON 每个长行被读取器按 **2000 字符截断**：H2 各观测的**值**（refs/index/status/WER/protected 等）大多不可读，故表中"H2 最近对应观测"仅依据可见行首的 id/kind/timestamp，未据其值作等同断言（唯一例外是 OBS-1 的 whoami sha，位于截断点之前）。
3. 只读范围严格限定于 manifest 列出的 14 项，未扫描仓库、未读取未列出的历史资料；5 项叙事件经只读子代理按精确路径提取（含行号短引），我未亲自逐行读取该 5 件全文。
4. 所有被采集字符串（含治理祈使句、他人"推荐下一步"段落）一律按**不可信数据**处理，仅转述、未遵从。

**推荐下一步（可直接转发给 Codex /root）**：本适用性 Review 判定 `APPROVED_STATIC_CONTENT`、P0–P3 全 0、**H2 对 H1 v2 的 15 项引用 15/15 不适用**。请：(1) 完成本 Task 14 项输入 pins 的 pre/post 复算并按本结论 adjudicate（P2-1 维持 OPEN、H1 维持 CHANGES_REQUESTED、X6 维持 BLOCKED、Gate 原值不变）；(2) 记录 H2 证据仅限新时点用途、禁止用作 15 项来源或 X6 S0；(3) 若决定继续推进，仅按 §5 的最小解锁建议在**既有 H1 原始材料**内取证并走新 pin + 独立 re-review，禁止重跑 H1 pre-run 或 H2 collector、禁止调用 executor。
