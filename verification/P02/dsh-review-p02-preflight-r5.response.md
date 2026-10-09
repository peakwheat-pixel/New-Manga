# P02 Codex-only Isolation（R5 候选）— DeepSeek Harness 独立只读 exact-head Review

## 0. 审查对象与只读声明

| 项目 | 值 | 核验方式 |
|---|---|---|
| reviewed HEAD | `844aec282416111310d9a9efcac5bc9e0c6eb451` | `git rev-parse HEAD` |
| reviewed tree | `79ec85adc5aabcd3e93d6a7d08bb8986fdfed16b` | `git rev-parse 'HEAD^{tree}'` |
| base / parent | `92dc7361194f1db8fdf7aff3a15a3d234ae56678`（单父，`rev-list --count`=1） | `git log -1 --format=%P` |
| review branch / worktree | `review/deepseek/P02-preflight-r5-844aec28` / 本 checkout | `git rev-parse --abbrev-ref HEAD` |
| commit | `docs(P02): record refreshed stage-1 preflight`，`2026-10-10 03:37:39 +08:00` | `git log -1` |
| checkout 状态 | 干净（`git status --porcelain -uall` 空）；本 Review 未改文件、未切 commit | 复查前后一致 |
| exact path set | **23**（4 M = `doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P02.md`；19 A = `verification/P02/**`） | `git diff --name-status/--shortstat`（`+1133 / −10`） |

**未运行/无法复现（如实标注，不推断 PASS）**：本 review shell 内 `Get-CimInstance`/`Get-AppxPackage` 全部返回“拒绝访问” → `InstallState=1`、WSB AppX identity、RAM/disk/cores 的 **live 复测 = NOT_RUN**；`wsb --version` / `wsb list --raw` **刻意 NOT_RUN**（避免触碰 WSB 服务，属 admission 时职责）；Sandbox / clone / Smoke / build / runner / Vitest / GUI / 产品测试一律 **NOT_RUN**（越权与禁令）。作者 worktree 捕获时的 17 条 dirty 路径、`-r4.stdout.md` “空文件”、`R5 start checkpoint EOF was normalized` 三项 **UNKNOWN/不可复现**。

## 1. 裁决

**`APPROVED_WITH_CONDITIONS`** — `P0 / P1 / P2 / P3 = 0 / 0 / 1 / 10`

| ID | 级别 | 一句话 |
|---|---|---|
| **F-01** | **P2** | observations R3 公布摘要 `68f60207…` / `21,923 bytes` 与提交产物不可复现（该值是作者 worktree 的 CRLF 混行尾字节流哈希） |
| F-02 | P3 | “冻结提案把虚拟化条件定义为 `VirtualizationFirmwareEnabled`”属溯源误述（提案只写 “BIOS virtualization”，从未命名该 CIM 字段或两个 SLAT/VT-x 字段） |
| F-03 | P3 | r3 XML “2,609 bytes” 缺 “canonical（CRLF→LF）” 限定（检出 blob 为 2,631 bytes；此前 R6 DSH 已登记同类措辞问题） |
| F-04 | P3 | frozen inputs TSV 6 行 `expectedBytes` 空却 `sizeMatch="True"`，与新观测的 `size_match=null` 并存且未互相注明 |
| F-05 | P3 | 当前状态段删除 P05 已记录的 “DSH exact-head Review BLOCKED 后故障转移” 溯源与证据链接 |
| F-06 | P3 | root 保护 manifest 自身的冻结 head=`549a6544…` 未在新状态段说明（live root=`ceffb747…`） |
| F-07 | P3 | 两个新 checkpoint 的时间字段早于其内容所述事件（03:21 记录 03:30 结果；03:27:31 记录 03:30:19 采集） |
| F-08 | P3 | `condition-review.md:11` 声称 Index 已引用授权锚点，实际 `doc/00_INDEX.md` 未引用（O-1 闭合残差） |
| F-09 | P3 | `@oai/sky` 被写成 `03:29:16Z`，把本地 +08 时间误标为 UTC |
| F-10 | P3 | R10 erratum 为 Integrator 定向纠错（prompt 内已含答案），独立性弱但可审计；`codex-preflight-r5-validation.md:34` 称 `-r4.stdout.md` 为空，作者 worktree 现为 14,802 B |
| F-11 | P3 | `git diff --check 92dc7361..844aec28` **EXIT=2**（1 条 EOF 空行，已被披露）+ 多处连续空行噪声 |

**是否阻止 Codex 记录独立 Smoke admission：是，需先处置 F-01。** 依据 r9 自身验收条款（`codex-scratch-build-process-isolation-scope-delta-r1.md:151`：“reports `APPROVED`（no unresolved P0/P1/P2; nonblocking P3s must be explicitly dispositioned）before Smoke admission”）——F-01 为未处置 P2，P3 亦须逐条显式 disposition。本 Review **本身不产生** Smoke admission，也不是 Smoke admission。

## 2. 独立复现结果（本轮实测，非采信）

| # | 核验项 | 结果 | 证据/命令 |
|---|---|---|---|
| 1 | live root 保护清单 | **203/203，missing/extra/mismatch=0/0/0，staged=0**（live root `main@ceffb747…`） | `git -C "G:/CODEX/New Manga" status --porcelain -uall -z` 逐条 size+SHA-256 复算 |
| 2 | manifest 配方摘要 | 复现 `3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2` | `json.dumps(entries,sort_keys=True,separators=(',',':'))` |
| 3 | 20 输入 pins | **20/20 hash + 14/14 已登记 size 全部 live 匹配**；6 条未登记 size 保持 `null` | 逐文件 `Get-FileHash` 等价复算（~347 MB 全量） |
| 4 | 12 HostFolder 根 | **12/12** 存在状态匹配；分类 `1 Scratch RW + 9 Smoke RO + 2 Build-only RO`；根级 reparse=0 | `os.path.exists/stat` |
| 5 | r3 XML | canonical LF=**2,609 B / `9af44513…`**；11 mappings；**10 RO + 1 RW**；无 `LogonCommand`；raw=2,631 B | 直接解析 + `sha256` |
| 6 | source pins | `7ce3c40c…` 存在且为 live main 祖先；3 个 blob 的 LF/CRLF SHA-256 **逐项复现** | `git show <commit>:<path>` |
| 7 | 阈值 | 16/16 为 true；对照 frozen 提案（`proposal-r1.md:64,78,122`：总 RAM≥4 GiB、available≥4096 MiB、≥2 cores、C:/G: 各≥1 GiB）全部满足 | 值复算：31.647 GiB / 16,778 MiB / 16 / 329.615·1,299.432 GiB |
| 8 | gate 字段 | observations R3 与 4 份状态文档完全一致：Stage1 PASS / 完整 preflight `BLOCKED / INCOMPLETE` / Smoke `NOT_ADMITTED` / Build Gate `BLOCKED` / build `NOT_AUTHORIZED / NOT_RUN` / AC1–AC7 `BLOCKED / NOT_RUN` / Barrier `EFFECTIVE` | `observations-r3.json:505-512` vs `STATUS:9`、`Plan:7`、`INDEX:5`、`P02.md:91,93` |
| 9 | 路线校验器 | `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` **EXIT=0**（196 节点/105 祖先/21 planned 无环/链接/governance），打印 `live HEAD=844aec28` | 本轮实跑 |
| 10 | 新增行本地链接 | 15 个 md、**27/27 local、0 missing** | 仅对 diff 的 `+` 行解析 |
| 11 | 授权边界 | 23 路径 **0 outside** `{4 个授权文档段 ∪ verification/P02/**}`；`candidate ∩ root dirty = ∅`；AC 列表、front matter（owner/reviewer/integrator/depends_on/status）、依赖图均未变 | `git diff --name-status` + live root dirty 交集 |
| 12 | R9 C-01..C-06 闭合（base 复核） | C-01：r2 JSON 恰 6 条 `size_match=null`、20/14/6；C-03：12 根 `mapping_domain` 齐备；C-02：7 路径枚举；C-04：`scope-delta:85,127` + `r4-start:7` 授权锚点；C-05：`smoke-admission-r1.md:20-24`；C-06：滞后登记 | `git show 92dc7361:…` 逐项 |
| 13 | erratum 准确性 | E-1 复现 **2 A + 5 M、`+152/−21`**；E-2 复现 r9 正式响应 `:5/:50` = `P3=6, NOTE=1`、`:57-91` = C-01..C-06 每项 P3 → **O-3 撤回正确，无需 crosswalk**；最终仍 `APPROVED` | `git diff 083d2b47..92dc7361`；`dsh-review-p02-preflight-r4.response.md:5,50,57-91` |
| 14 | 越界表述扫描 | 4 份状态文档中**无** “隔离已证明 / Smoke PASS / Build PASS / AC PASS” 表述；“Stage-1 PASS 不等于完整隔离证据”明示（`STATUS:9`） | `grep` + 全文 diff |

## 3. Findings 证据位置

- **F-01（P2）**：`verification/P02/codex-scratch-build-preflight-r3.md:6`（公布 `68f60207…`、`21,923 bytes`）与 `verification/P02/codex-preflight-r5-validation.md:6`（重复同值）。本轮复算：提交 blob（LF）=**21,405 B / `b08bc36e0d0e50d5d9e40811fe0b22495fe8a11b06d41869de6acb92cef4f902`**，blob id `efc8dcce274a42f219d50dc118c39f4f09764673`；本 exact-head checkout 原始字节=**21,924 B / `200859ac75830f3065c0fdd576b1ddf9dc32b69aed27aa516a2efe115131765a`**；作者 worktree=21,923 B / `68f60207…`（**仅此值吻合**，其文件尾为 `]\r\n}\n`，518 组 CRLF、EOF 为裸 LF）。三者 LF 规范化内容**完全相同**，故**未改变任何实测值**；缺陷是“公布摘要不可由仓库产物复现”（`core.autocrlf=true`）。建议：改公布 canonical LF 摘要/大小（`b08bc36e…` / 21,405）或明确定义 worktree 摘要口径，并消除该文件 EOF 混行尾。
- **F-02（P3）**：`codex-scratch-build-preflight-r3.md:12` vs `codex-scratch-build-process-isolation-proposal-r1.md:64,78`（仅 “BIOS virtualization”；全文件对 `VirtualizationFirmwareEnabled|VMMonitorModeExtensions|SecondLevelAddressTranslation` **0 命中**）；两字段 false 见 `observations-r3.json:116-117`，仅 R3 报告披露。
- **F-03（P3）**：`STATUS:7`、`Plan:7`、`P02.md:88`、`codex-scratch-build-preflight-r3.md:17`、`observations-r3.json:473-476`；canonical 约定此前写于 `dsh-review-p02-preflight-r4-condition-closure.response.md:102`，同类措辞已被 `dsh-review-process-isolation-r6.response.md:66` 记为不精确。
- **F-04（P3）**：`codex-scratch-build-preflight-inputs-r1.tsv:4,5,18,19,20,21`（`expectedBytes` 空、`sizeMatch="True"`）vs `observations-r3.json:265-471`（`size_match=null`，`:470` `size_not_registered: 6`）。
- **F-05（P3）**：`doc/STATUS.md:3`、`doc/00_INDEX.md:3`（新文本）与 base 文本对比（`git show 92dc7361:doc/STATUS.md` / `:doc/00_INDEX.md` 第 3 行原含 “（DSH exact-head Review BLOCKED 后故障转移）” 及 P05 证据链接）。
- **F-06（P3）**：`verification/P02/codex-process-isolation-root-start-manifest.json:5`（`head=549a6544…`）vs `observations-r3.json:28`（`ceffb747…`）；新状态段 `STATUS:7`、`Plan:7`、`INDEX:5`、`P02.md:89`。我已 live 复现 203/203，实质成立。
- **F-07（P3）**：`codex-checkpoint-p02-preflight-r4-condition-review.md:3` vs `:27`；`codex-checkpoint-p02-preflight-r5-start.md:3` vs `:9`；可对照 `codex-checkpoint-p02-preflight-r4-start.md:15` 的“日期化追加段”先例。
- **F-08（P3）**：`codex-checkpoint-p02-preflight-r4-condition-review.md:11` vs 事实：仅 `STATUS:5`、`Plan:7`、`P02.md:85` 引用 `codex-checkpoint-p02-preflight-r4-start.md` / authorization basis，`doc/00_INDEX.md` 无命中。
- **F-09（P3）**：`codex-scratch-build-preflight-r3.md:13` vs `observations-r3.json:479`（`2026-10-09T19:29:16.092Z` UTC = 03:29:16 **+08**）。
- **F-10（P3）**：`dsh-review-p02-preflight-r4-condition-closure-correction.prompt.md`（876 B，`.exit.txt`=0；prompt 内已给出 2A+5M 与撤回 O-3 的答案）；`codex-preflight-r5-validation.md:34` vs 作者 worktree `dsh-review-p02-preflight-r4.stdout.md`=14,802 B（erratum 亦引 14,802 B）。
- **F-11（P3）**：`git diff --check 92dc7361..844aec28` → `dsh-review-p02-preflight-r4-condition-closure.prompt.md:47: new blank line at EOF`（EXIT=2，已在 `codex-preflight-r5-validation.md:9` 披露；该 prompt SHA-256 复现为 `d732a51950d2428fb7b95587b90ac2ad0236d0505ab8aeb88e0968653eeb25ed`，尾部 `\n\r\n`）；连续空行：`00_INDEX.md:6-8(3)`、`STATUS.md:10-12(3)`、`REBASELINE_PLAN.md:10-12,20-22(3)`。

## 4. 逐项回答 Review 问题

1. **R10 APPROVED + erratum 是否准确闭合 C-01..C-06、纠正计数、撤回 O-3**：**是**（已独立复算）。E-1 的 `2 A + 5 M / +152−21` 成立；E-2 依据的 r9 正式响应确为 `P3=6 / NOTE=1 / C-01..C-06`，故 O-3 撤回正确且不需要 crosswalk；最终 decision 仍 `APPROVED`，未新增阻断。C-01/C-02/C-03/C-04/C-05/C-06 的处置在 base 产物中逐项可见（第 2 节 #12）。唯一过程性保留见 **F-10**（定向纠错的独立性弱，且 `-r4.stdout.md` 为空之说不可复现）。
2. **R5 授权可追溯与 O-1/O-2 闭合**：O-1 **基本闭合**——`STATUS:5`、`Plan:7`、`P02.md:85` 均点名 `codex-checkpoint-p02-preflight-r4-start.md:7` 与 scope-delta r7/r9 basis（`scope-delta:85,127` 原文已核）；残差为 **F-08**（Index 未引用而 checkpoint 声称已引用）。O-2/NOTE-01 **有证据闭合**——erratum E-3 更正为 `NOTE-01`，`codex-checkpoint-p02-preflight-r4-condition-review.md:12` 记录 20/20 逐行比对；本轮我另行复现 20/20 一致。
3. **observations R3 是否准确对应 frozen TSV**：除摘要问题与两处措辞外**准确**。20/20 SHA-256、14/14 已登记 size、6 条 null 比较、12/12 根行、source/EOL pins、r3 XML 2,609 B/`9af44513…`/11 mappings、CIM/WSB 值、RAM/disk 阈值、root manifest live 匹配与零候选交集**均已独立复现**；`aggregator` 两项纠正（porcelain 列语义、`FreeSpace` 字段名）透明记录于 `observations-r3.json:513-518`，**未改动任何实测字节值**（staged=0 与 raw `free_bytes` 均可复核）。残留：**F-01/F-03/F-04/F-09**。
4. **是否越界表述**：**否**。InstallState=1 与 Stage-1 PASS 在 4 份文档中均未被表述为“隔离已证明 / Smoke PASS / Build PASS / 产品验收”；反而显式声明 `Stage-1 PASS 不等于完整隔离证据`（`STATUS:9`）。
5. **23-path 是否严格限定**：**是**（路径与文件类型层面 0 越界，AC/Owner allowlist/依赖图/产品代码与测试/共享契约/Task 状态均未改）；内容层面唯一需要记账的是 **F-05**（P05 溯源精简）与 **F-11**（空行噪声）。
6. **当前状态与恢复指针是否互相一致**：**gate 值完全一致**（第 2 节 #8），四个文档均指向 R3 报告/observations/R5 checkpoint；不一致项为 **F-06/F-07/F-08**（溯源与时间字段层面）。

## 5. 精确 next action（可转发）

> **Owner/Integrator=Codex**：R5 候选 `844aec28`（tree `79ec85ad`）获 DeepSeek Harness 非作者 exact-head **`APPROVED_WITH_CONDITIONS`**（P0/P1/P2/P3=`0/0/1/10`）。请仅在 r9/r10 授权范围内操作：
> 1. **处置 F-01（P2，必需）**：把 `codex-scratch-build-preflight-r3.md:6` 与 `codex-preflight-r5-validation.md:6` 的 observations R3 摘要改为可复现口径（canonical LF `b08bc36e0d0e50d5d9e40811fe0b22495fe8a11b06d41869de6acb92cef4f902` / 21,405 bytes，或明确 `git blob` 口径），并修正该 JSON 的 EOF 混行尾；**不得重测或改写任何实测值**。
> 2. **逐条 disposition F-02..F-11**（修或显式接受），只改 4 个授权文档的当前段与 `verification/P02/**`；保持所有 gate 值不变（Stage1 PASS、完整 preflight `BLOCKED / INCOMPLETE`、Smoke `NOT_ADMITTED`、Build Gate `BLOCKED`、build `NOT_AUTHORIZED / NOT_RUN`、AC1–AC7 `BLOCKED / NOT_RUN`、Hard Build Barrier 有效）。
> 3. 重跑 `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`、新增行 Markdown 链接、exact path containment、root manifest 203/203 + 零交集、`git diff --check`。
> 4. 冻结**新单提交**（仍基于 `844aec28`），派发 DSH 对该 exact HEAD 做增量 exact-head Review。
> 5. **仅当**该 Review 报 `APPROVED`（无未处置 P0/P1/P2，P3 全部 disposition）后，Codex 才**另立**独立的 Smoke admission checkpoint 并记录 `ADMITTED`；随后完成 clone `--no-hardlinks`、全部映射根递归 manifest/reparse containment、interactive non-elevated shell、`wsb list --raw` 现时空、session/UI/screenshot 绑定后，方可执行一次获准 Smoke。
> 6. 在此之前不得创建 clone、不得 `wsb start`；Build Gate、AC 与 Hard Build Barrier 状态不变。

## 6. 明确 NOT_RUN / UNKNOWN 清单

- live CIM/AppX/WSB 复测（InstallState、AppX identity、RAM/disk/cores、`wsb --version|list --raw`）→ **NOT_RUN**（本 shell 拒绝访问 / 刻意不触碰服务）。
- Sandbox 启动、clone 创建、递归 manifest、reparse 遍历、guest 探针、network 判别、截图/session 绑定、post-run 比对 → **全部 NOT_RUN**（越权）。
- Build / runner / Vitest / GUI / WebView / 产品测试 → **NOT_RUN**。
- 作者 worktree 捕获时 17 条 dirty 路径 → **UNKNOWN**；`-r4.stdout.md` “为空” → **UNKNOWN（当前 14,802 B）**；`R5 start checkpoint EOF was normalized` → **UNKNOWN（提交字节无末尾换行，无法复现该措辞所指状态）**。
