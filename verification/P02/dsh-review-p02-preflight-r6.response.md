# P02 Codex-only Isolation（R6 修复增量）— DeepSeek Harness 独立只读 exact-head Review

## 0. 审查对象与只读声明

| 项目 | 值 | 核验方式 |
|---|---|---|
| reviewed HEAD | `c85a041c514f3c0dd1c355a2d09f064dbc64e749` | `git rev-parse HEAD` |
| reviewed tree | `b67e3e02186a8009c46da0dba819003b04acfec1` | `git rev-parse 'HEAD^{tree}'` |
| base / parent | `844aec282416111310d9a9efcac5bc9e0c6eb451`（单父，`rev-list --count HEAD^..HEAD`=1） | `git log -1 --format=%P` |
| review branch / worktree | `review/deepseek/P02-preflight-r6-c85a041c` / 本 checkout | `git rev-parse --abbrev-ref HEAD` |
| owner branch | `codex/P02-process-isolation`（同一 commit，owner worktree `p02-process-isolation-plan`） | `git branch --contains HEAD` |
| commit | `docs(P02): disposition R5 preflight review findings`，`2026-10-10T03:57:23+08:00` | `git log -1 --format=%cI` |
| checkout 状态 | 审查开始时**干净**（`git status --porcelain -uall` 为空）；本次仅用工作区内临时 scratch 文件做字节测量，测后删除、0 残留；写入本 Review response 后唯一未跟踪文件即该 response 自身 | 审查前后各一次 |
| delta | **18 路径 / +249 −34**：4 个授权 current-status 文档（M）+ 14 个 `verification/P02/**`（9 A / 5 M） | `git diff --name-status/--stat` |

**未运行/不可复现（如实标注，不推断 PASS）**：clone 创建、Sandbox 启动、`wsb --version|list --raw`、Smoke、Build、runner、Vitest、GUI/WebView、产品验收全部 **NOT_RUN**；live CIM/AppX/WSB 宿主机复测 **NOT_RUN**（不是本 Review 范围）。原始进程 stderr/stdout **未读取**、未作为推理或 Review 证据。

## 1. 裁决

**`APPROVED`** — 针对 R5 全部 finding 的增量处置：`P0 / P1 / P2 / P3 = 0 / 0 / 0 / 0`（本轮未新增 finding；F-01 已关闭，F-02..F-11 每条均已显式 disposition 并经独立复核）。第 6 节记录 3 项 **reviewer-recorded 精度事项**，明确不构成 finding、不阻断后续准入。

**F-01（P2）= CLOSED。** **每个 P3（F-02..F-11）均有显式 disposition。** **本 Review 允许 Codex 另立独立的 Smoke admission checkpoint**（满足 r9 验收条款：`APPROVED`、无未解决 P0/P1/P2、P3 全部 disposition）；该 checkpoint 只是记录 `ADMITTED`，任何 `wsb start` 之前仍须完成第 7 节列出的全部 pre-start 检查。

## 2. 增量范围与授权边界

- 18 路径全部落在 `{doc/00_INDEX.md、doc/REBASELINE_PLAN.md、doc/STATUS.md、doc/tasks/P02.md 的当前状态段} ∪ verification/P02/**`，**0 越界**。
- 4 个文档的 hunk 严格限于当前段：INDEX `@@ -3,4 +3` 与 `@@ -7,0 +5`；STATUS 4 个 hunk（第 3、5、7、9 行）；PLAN 3 个 hunk（第 3、7、11 行）；P02.md 3 个 hunk（第 85、88、91 行，位于 `Codex Scratch Isolation Preflight checkpoint` 段内）。
- 精确 18 路径：M `doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P02.md`；M `verification/P02/codex-checkpoint-p02-preflight-r4-condition-review.md`、`…-r5-start.md`、`codex-preflight-r5-validation.md`、`codex-scratch-build-preflight-observations-r3.json`、`codex-scratch-build-preflight-r3.md`；A `verification/P02/codex-checkpoint-p02-preflight-r5-delivery.md`、`…-r5-repair-validation.md`、`…-r5-review-findings-start.md`、`codex-preflight-r5-review-disposition.md`、`dsh-review-p02-preflight-r5.exit.txt`、`…r5.mount.txt`、`…r5.prompt.md`、`…r5.response.md`、`…r5.session.json`。
- **产品源码、测试、依赖、共享契约（`doc/contracts/**`）、Task AC 列表、Owner allowlist、front matter（owner/reviewer/integrator/depends_on/status）、依赖图均未变更**；本 delta 不含任何 `doc/contracts/**`、`src/**`、测试或包管理文件。
- 新增行本地链接：**38/38 可解析，0 broken**。另有 10 条 broken 链接只出现在 STATUS/PLAN 的**未改动历史快照段**（`../reviews/...` 等），属 delta 之外既有状态，不计入本 Review。
- `doc/tasks/P02.md` front matter 在本 delta 中**未被修改**，实测仍为 `status: in_progress`、`owner: Antigravity`、`reviewer: DeepSeek Harness`、`integrator: Codex`、`depends_on: [P08, M2-RESOLVE-DEBOUNCE-1, M2-REGION-DEBOUNCE-1]`、`base_commit`/`scope_contract_sha256`/`integration_commit` 原值。这与当前状态段声明的 “Codex-only isolation 子任务 Owner=Codex、非作者 Reviewer=DeepSeek Harness、Integrator=Codex” 不冲突：后者是父 Task 下子任务的口径，父 Task 冻结 front matter 按授权不重冻结。**无 finding。**

## 3. F-01 复算（P2 关闭）

对提交产物直接做字节级复算（`git cat-file blob` + 工作区内 scratch 文件 SHA-256）：

| 口径 | bytes | SHA-256 | git blob |
|---|---|---|---|
| HEAD 提交 canonical LF（`codex-scratch-build-preflight-observations-r3.json`） | **21,705** | `39c484f52fcb1c3e040b5ffdbab62b50e13d2b45c41d9d93d59221bd0fbbb74c` | `63888f852bbe0692834b6b29e31484fb90f02c16` |
| base `844aec28` 提交 blob（对照 prior F-01 基线） | 21,405 | `b08bc36e0d0e50d5d9e40811fe0b22495fe8a11b06d41869de6acb92cef4f902` | `efc8dcce274a42f219d50dc118c39f4f09764673` |
| 本 checkout 工作区文件（`core.autocrlf=true`） | 22,226 | `425002a453e95460d4ca6abdf49747d461908bb565bef2c0421514d63770cea7` | — |

- 公布值 **21,705 / `39c484f5…` 与提交 blob 逐一吻合**，并与 4 处引用一致：`codex-scratch-build-preflight-r3.md:6`、`codex-preflight-r5-validation.md:6`、`codex-preflight-r5-review-disposition.md:11`、`codex-checkpoint-p02-preflight-r5-repair-validation.md:8`。
- **未改动任何实测值**：该 JSON 的 delta 为 **3 insertions / 1 deletion**，仅新增 `config.bytes_basis` 与 notes 第 5 条（前一条 notes 行仅追加逗号）；其余全部字节（阈值、pins、尺寸、CIM/WSB、RAM/disk、root manifest 字段）与 base blob 完全相同。
- **EOF 混行尾已消除**：提交 blob 为纯 LF（含 CR=False，末尾为 LF）；工作区检出 CR=521、LF=521、22,226=21,705+521，即均匀 CRLF，`LF 规范化后的工作区内容 == 提交 blob`。
- 四份 current-status 文档与当前 `codex-scratch-build-preflight-r3.md`、`codex-preflight-r5-validation.md`、`codex-preflight-r5-review-disposition.md`、`codex-checkpoint-p02-preflight-r5-{delivery,repair-validation}.md` 中**已无** `68f60207`/`21,923`/`200859ac`/`b08bc36e` 残留；历史 Review response 内的旧值引用属正确保留。

## 4. F-02..F-11 逐项复核

| ID | 作者 disposition | 我的独立复核 | 结论 |
|---|---|---|---|
| F-02 P3 | FIXED | 冻结提案只有 “BIOS virtualization”（`codex-scratch-build-process-isolation-proposal-r1.md:64,78`），对该文件检索 `VirtualizationFirmwareEnabled|VMMonitorModeExtensions|SecondLevelAddressTranslation` **0 命中**；`r3.md:12` 已改为“提案仅要求 BIOS virtualization / 两个 SLAT 字段是观测且未被设为 Gate”。 | 接受 |
| F-03 P3 | FIXED | XML **提交 blob=2,609 B / `9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d`**，工作区 CRLF=2,631 B（实测一致）；JSON 新增 `bytes_basis="canonical LF bytes after CRLF normalization"`（`:475`），`r3.md:17`、`STATUS:7`、`P02.md:88` 均标注 canonical LF。 | 接受 |
| F-04 P3 | ACCEPTED_WITH_EXPLICIT_LIMIT | 冻结 TSV 第 4、5、18、19、20、21 行确为 `expectedBytes` 空 + legacy `sizeMatch="True"`（恰 6 行）；JSON 记录 6× `"size_match": null`、`size_not_registered: 6`、`registered_size_matches: 14`、`hash_matches: 20`，并新增 notes 第 5 条；`r3.md:15` 明示 legacy `True` 不作为尺寸通过依据。**限制成立**：冻结 TSV 保持原样（历史输入证据）不改写，gate 口径按 14/14 + 6 null 计。 | 接受（限制显式） |
| F-05 P3 | FIXED | `STATUS:3`、`INDEX:3` 恢复 “P05 … DSH exact-head Review BLOCKED 后故障转移” 并链接 `verification/P05/dsh-review-blocked-checkpoint-5288db42.md`（文件存在；其 `:6` verdict=`BLOCKED`、`:19` Reviewer 故障转移至 Antigravity，陈述与链接均成立）。 | 接受 |
| F-06 P3 | FIXED | `codex-process-isolation-root-start-manifest.json:5` = `549a6544f0be1eec66c09ece393fd1a409f10bf3`；`observations:28` = live `ceffb7479cb1f79bd3b620afdaf6e9eaa0ae6d50`。冻结 HEAD 已在 INDEX:5、STATUS:7、PLAN:7、P02.md:89 四处写明（原缺陷即缺冻结 HEAD），实质已修。 | 接受（见 N1） |
| F-07 P3 | FIXED | `codex-checkpoint-p02-preflight-r4-condition-review.md:3` 现为“初始记录时间 03:21；本次追加更新时间 03:53:17”；`codex-checkpoint-p02-preflight-r5-start.md:3` 现为“Start time 03:27:31 … last updated 03:53:17 after the 03:30:19 capture”。时间字段不再早于所述事件。 | 接受 |
| F-08 P3 | FIXED | `INDEX:5` 新增 `[R9 start checkpoint](../verification/P02/codex-checkpoint-p02-preflight-r4-start.md#L7)`（目标存在）；`r4-condition-review.md:11` 明确披露“Index 在 844aec28 尚缺引用，已作为 R5 F-08 修复项补入”。 | 接受 |
| F-09 P3 | FIXED | `observations:480` `ui_helper.captured_at="2026-10-09T19:29:16.092Z"`；`r3.md:13` 同时给出 UTC 原值与 `2026-10-10 03:29:16.092 +08:00` 本地换算（UTC+8 换算正确）。 | 接受 |
| F-10 P3 | ACCEPTED_WITH_EXPLICIT_LIMIT | `codex-preflight-r5-validation.md:34` 已撤回“空 stdout”说法，改述为进程专用文件 14,802 B / SHA-256 `21e563b1d5a3f9f061e6e9c26b386dec51e7356b82cdcfd2e9979adefcd3a09b`、排除且不作为正式证据。作者 worktree 元数据：`dsh-review-p02-preflight-r4.stdout.md`=14,802 B、`…stderr.txt`=34,140 B（14,802 唯一对应 stdout）；该文件**未入库**（`git ls-tree` 无对应 blob），content 按契约未读。erratum 结果的独立复核见 prior R5 response §2 #13（2A+5M、O-3 撤回）。**限制成立**：该值与哈希不可由仓库产物复现，属作者 worktree 观测，不影响任何结论。 | 接受（限制显式） |
| F-11 P3 | FIXED_WITH_INHERITED_LIMIT | `git diff --check 844aec28..c85a041c` = **EXIT=0**（新修复 delta 干净）；`git diff --check 92dc7361..c85a041c` = **EXIT=2**，全范围**仅 1 条** warning：`dsh-review-p02-preflight-r4-condition-closure.prompt.md:47: new blank line at EOF`，该不可变 prompt 未被改动（blob `21c1acaefa43e6e4293dbcef42099ad367717c37` / 4,409 B / LF SHA-256 `6f018fd5d7a82591fdb109d5e0defef96e706ae01cba94992b43d58bea06c9e5`，`844aec28` 与 HEAD 同一 blob）。当前段连续空行：INDEX/STATUS/P02.md max run=2，**已无 3 连空行**。 | 接受（见 N2、N3） |

## 5. 报告、四份状态段、时间戳、字节口径与 Gate 一致性

- **Gate 值完全一致且未变**（要求 5 逐项核对）：`PRESTART_STAGE_1_PASS`；complete preflight=`BLOCKED / INCOMPLETE`；Smoke=`NOT_ADMITTED`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`；Hard Build Barrier=`EFFECTIVE`。证据：`observations:506-513`（显式含 `smoke: NOT_RUN`）、`disposition:25`、`INDEX:5`、`STATUS:7,9`、`PLAN:7,9`、`P02.md:91`。
- **时间戳诚实**：candidate `844aec28` 提交 03:37:39 → delivery checkpoint 03:38 → R5 Review/disposition 03:53:17（findings-start 与该 disposition 时间一致）→ repair-validation 03:56:58 → 本 commit 03:57:23。各记录时间均不早于其所述事件，且 commit 时间晚于最后一次验证。
- **字节口径**：`r3.md:6` 与 `r5-validation.md:6` 明示“canonical LF”；JSON 对 XML 带 `bytes_basis`；实测 XML 2,609（LF）/2,631（CRLF checkout）与记载一致。
- **授权/恢复链接**：R9 授权锚点（`codex-checkpoint-p02-preflight-r4-start.md#L7`）在 INDEX/STATUS/PLAN/P02.md 均可解析；恢复点新增 `codex-checkpoint-p02-preflight-r5-repair-validation.md`（存在）；P05 故障转移证据链接可解析。新增行链接 38/38 通过。
- **R5 证据留痕的完整性**：本 commit 把 prior R5 的 prompt/response/exit/mount/session 入库（`verification/P02/dsh-review-p02-preflight-r5.*`）。我复核了 `session.json` 的 `prompt_sha256=1a0146d5…` 与提交 prompt 的 LF blob 一致；`response_sha256=f77c3981…` 恰等于**提交 response 的 CRLF 检出序列化**（15,893 B，实测复现），故入库副本与被挂载内容同源、无篡改迹象（详见 N3 的口径说明）。
- delta 声明计数自洽：repair-validation 记“本 checkpoint 前 17 路径、加入后 18 路径”，与实测 18 一致；新增行链接 checkpoint 记 16 条，我按“新增行 link 出现次数”计为 38 条（口径更宽），两者均为 0 broken。

## 6. Reviewer-recorded 精度事项（**非 finding**，不阻断 Smoke admission checkpoint）

1. **N1（F-06 证据单元格措辞偏强）**：disposition F-06 证据栏称 “Current P02 summaries distinguish … frozen HEAD=`549a6544…` from live root HEAD=`ceffb747…`”。实测仅 `doc/tasks/P02.md:89` 同时写出 live 哈希；`INDEX:5`、`STATUS:7`、`PLAN:7` 只写冻结 HEAD + “live 203/203 MATCH”（live 哈希见 `observations:28`）。信息在记录集内完整、F-06 实质已修，仅证据栏表述可再精确；建议下次改动时点名 live 哈希或收窄措辞。
2. **N2（F-11 继承项未在 disposition 内点名）**：`doc/REBASELINE_PLAN.md:18-20` 仍有 3 连空行，该 run 在 `92dc7361:14-16` 与 `844aec28:20-22` 就存在（本 delta 未触碰，`git diff --check` 也不报告），且位于历史快照段而非 current summary，因此 disposition 的“new current-summary blank-line noise is removed”本身无误；只是 F-11 evidence 曾列出 PLAN 的 `20-22(3)`，disposition 未把该继承项一并点名。建议补记 inherited 项（可选）。
3. **N3（复用摘要的字节口径未标注）**：`r5-validation.md:9` 与新增 `codex-checkpoint-p02-preflight-r5-delivery.md:10` 引用的 R10 prompt hash `d732a519…`（4,456 B）是 **CRLF 检出序列化**，提交 blob 为 `6f018fd5…`（4,409 B LF）；同理 `r5.session.json` 内 response 哈希用 CRLF（15,893 B / `f77c3981…`）而 prompt 哈希用 LF。两值都能在默认 `core.autocrlf=true` 检出中精确复现、内容无争议，故仅建议再引用时标注口径（canonical LF 或 checkout 字节）。

## 7. 精确 next action（可转发）

> **Owner/Integrator=Codex**：R6 修复 commit `c85a041c`（tree `b67e3e02`，parent `844aec28`）获 DeepSeek Harness 非作者增量 exact-head **`APPROVED`**（F-01 关闭；F-02..F-11 全部显式 disposition；本轮 P0/P1/P2/P3=`0/0/0/0`）。请仅在既有授权范围内操作：
> 1. 现在可以**另立**独立的 Smoke admission checkpoint 并记录 `Smoke admission=ADMITTED`；此时仍 `build=NOT_AUTHORIZED / NOT_RUN`、Build Gate=`BLOCKED`、AC1–AC7=`BLOCKED / NOT_RUN`、Hard Build Barrier=`EFFECTIVE` 不变。
> 2. `ADMITTED` 之后、任何 `wsb start` 之前，必须在 interactive non-elevated shell 中完成全部 pre-start 检查：fixed clone（`--no-hardlinks`）创建 + clone Git/object-link 校验、映射根递归 manifest/reparse containment、当刻 `wsb list --raw` 为空、session/window/screenshot binding；任一未知或失败即停止并保留状态。
> 3. 仍不得提权、不得改变系统 Feature、不得在 P02 Stage-1 isolation 之外扩大范围。
> 4. 可选（非阻断）：按第 6 节 N1/N2/N3 做一次纯文档精度收尾，并在下一次相同文件的改动中随附。

## 8. 明确 NOT_RUN / UNKNOWN 清单

- clone 创建、递归 manifest/reparse traversal、guest 探针、network 判别、截图/session binding、post-run 比对 → **全部 NOT_RUN**（越权）。
- Sandbox 启动、`wsb --version`、`wsb list --raw` → **NOT_RUN**（刻意不触碰 WSB 服务，属 admission 时职责）。
- Build、runner、Vitest、GUI/真实 WebView、产品测试/验收 → **NOT_RUN**。
- live CIM/AppX/RAM/disk/cores 宿主机复测 → **NOT_RUN**（非本 Review 范围；采信已提交 observations）。
- 原始进程 stderr/stdout → **未读取**；F-10 的 14,802 B 与 `21e563b1…` 仅由文件元数据/作者记录采信，**哈希未复算**（契约禁止读取原始进程输出）。
- 作者 worktree 捕获时 17 条 dirty 路径、`…r4.stdout.md` 内容、`R5 start checkpoint EOF was normalized` 旧措辞所指状态 → **UNKNOWN/不可复现**；本 Review 只对提交产物下结论。
