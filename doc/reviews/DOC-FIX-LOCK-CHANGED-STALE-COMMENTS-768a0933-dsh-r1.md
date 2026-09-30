# DOC-FIX-LOCK-CHANGED-STALE-COMMENTS 独立非作者 Review（DeepSeek Harness）

**decision: approved_with_conditions**（0×P0、0×P1、2×P2、6×P3、4×P4）

**审查方式声明**：严格只读静态审查，未修改任何文件、未执行任何 git/构建/测试命令（`pwsh` 两次被沙箱拒绝：`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`，含一次按规则的单次提权重试，仍被拒）。为不采信 Owner 自述，我独立读取了 Git 元数据（只读）：
- 提交链（`G:\CODEX\New Manga\.git\worktrees\DOC-FIX-STALE-COMMENTS-zcode\logs\HEAD`）：`4ed3c044`(release/reset) → `74022cdc`(claim) → `65f0facb`(fix: 两处注释) → `1dd30dc7`(handoff) → `768a0933`(evidence: whitespace-only normalization)
- 分支 ref（`.git\refs\heads\agent\zcode\DOC-FIX-LOCK-CHANGED-STALE-COMMENTS`）= `768a0933a002af881722567bdd8691c03a08e81b`

**reviewed_head = `768a0933a002af881722567bdd8691c03a08e81b`**（分支 tip；与派发口径一致）。凡需 `git diff --name-status` / blob hash / 工作区洁净度的比对项一律标 `not_verified`，并给出可由 Integrator 一条命令闭合的条件。

---

## Findings

### P2-1 — M2-TA3-A 的字节级 provenance 锚定在本 Task 后失效，且 Task/Handoff 的「不受影响」表述未限定
- **文件:行**：`verification/M2-TA3-A/raw/00-provenance.txt:16-18`；被影响的表述 `doc/tasks/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS.md:29`、`doc/handoffs/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS-zcode-delivery-20260930.md:21`
- **触发条件**：`00-provenance.txt:18` 以 `f1b5976de517290a294b7ea3b0c804e59c87f45b610ed9d8f4a047ce8c4850d9` 钉住 `experiments/M2-TA3-A/run_smoke.py` 的 **sha256**，`:16` 明确「`sha256sum -c` on this file (comments ignored) must report all lines OK there」；`M2-TA3-A.md:131,138` 记录「重建为 sha256sum -c 格式（15/15 OK）」并在集成时复跑。本 Task 改动了 `run_smoke.py:273` 的**字节**（注释仍是字节）。
- **影响**：`co_code` 全等只保证**指令流等价**，与**字节哈希**无关——在 main/tip 上按该 manifest 复算将出现 `run_smoke.py: FAILED`（15/15 → 14/15），而仓库没有任何登记说明这一预期失效。Task:29「M2-TA3-A 的既有证据由其 provenance（dc2b9aca 锚定）继续可追溯，**不受注释演进影响**」与 Handoff:21 同口径表述，会被集成方读成「锚定仍成立」，实际上是「历史锚点可识别、但 manifest 自检在 tip 上不再全绿」。
- **缓解（我核实过的限定条件）**：`:13-15` 把验证环境限定为 **M2-TA3-A 交付 worktree**；若该 worktree 仍完好且未改，15/15 在那里仍成立。因此这是 **main/tip 层面的自检退化**，不是历史证据被推翻。
- **建议**：(a) 在本 Task **允许路径**内新增 provenance 附注（如 `verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/00-provenance-note.txt`），写实新 sha256 与「dc2b9aca 行为锚点不变、字节锚点被本 Task 有意演进、`sha256sum -c` 需在 TA3-A 交付 worktree 复算」；(b) 把 Task:29 / Handoff:21 改为「provenance 的 dc2b9aca pin 仍为有效历史标识；**字节级自检不再对 tip 全绿**」；(c) 由 Integrator 在 `verification/DIAG-...-001`/`M2-TA3-A.md`（非 Owner 可写路径）加一行收口注。若 Integrator 确认该 manifest 的预期环境**仅为** TA3-A 交付 worktree、不需要 tip 级复算，本项降为 P3（仅需措辞限定 + 附注）。

### P2-2 — AC2 的核心「机器证据」不可复现：Handoff 声称的探针脚本并不存在，日志无环境头/EXIT
- **文件:行**：`verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/raw/ac2-bytecode-probe.log:1-3`（全文 3 行）；矛盾表述 `doc/handoffs/...-delivery-20260930.md:46`「见 ac2 log 头部内嵌脚本」、`:61`「字节码探针脚本内嵌于 …/ac2-bytecode-probe.log 头部」
- **触发条件**：任何复核者按 Handoff:61 的复现指令去 log 头部找探针脚本。
- **影响**：①**不存在内嵌脚本**——我以 `co_code`/`BYTECODE-PROBE` 全仓 grep 检索，探针源码在仓库中零命中（仅本 log 与文档提及），故 `objects=37/15`、`ALL-EQUAL` 无法被独立复算，取证方式（改前 blob 如何取得，`git show 4ed3c044:path` 还是副本？）也未记录；②该 log 无 shell/解释器头、无 EXIT 码、无 py_compile 独立输出，与同 Task 的 `ac1-*.log:1,37`、`ac2-acceptance-regression.log:1,4`、`ac4-scope-proof.log:1-13` 的取证规格不一致；按本仓证据纪律（REVIEW 模板 §验证 Q-009「判别力 artefact 缺失即记 NOT_RUN」），AC2 的②项应视为**不可复现证据**而非 executed。
- **方法盲区（复核点 (4) 的实质）**：`co_code` 全等**不能**支撑「零逻辑变化」的一般命题——`co_consts`（字符串/数字字面量、**docstring**、默认参数）、`co_names`、`co_varnames`、`co_freevars/co_cellvars`、`co_exceptiontable`、`co_linetable/co_firstlineno` 全在比较之外，而其中 `co_consts` 的变化可等价于行为变化（`return "completed"` → `return "failed"`：co_code 逐字节相同）。**本 Task 恰好命中该盲区**：`acceptance_bridge.py` 的改动就是 `method_run_pipeline` 的 docstring ⇒ `co_consts[0]` **必然改变**；两个文件各净 +2 行（AC1 两处 hunk：`-1/+3` 与 `-3/+5`）⇒ 其后所有 code object 的 `co_firstlineno`/`co_linetable` 也改变。即：探针只比较了「无论如何都必须相等」的那一维，而把「按设计必然变化」的那一维排除在外。
- **建议**：把探针源码 + 解释器/venv 头 + 命令 + `EXIT=0` 原样入库；并把产出措辞从「零逻辑变化的机器证据」改为「**指令流（co_code）零变化**」，或让探针同时输出 `co_consts/co_names/co_varnames` 的差异摘要并显式声明 docstring 属预期差异。AC1（人工 diff）已提供本 Task 的真正充分证明，故本项不阻塞，但必须闭合措辞与可复算性。

### P3-1 — Task 自身 `status` 与其交付记录互相矛盾；`delivery_head` 仍为 null
- **文件:行**：`doc/tasks/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS.md:5`（`status: in_progress`）、`:16`（`delivery_head: null`）对 `:67`「`in_progress → in_review`」、Handoff frontmatter `status: delivered_awaiting_review`
- **触发条件**：按 frontmatter 读取 Task 状态的任何 Agent/脚本。
- **影响**：路由/门禁口径不一（本 Task 的交付物**就是**文档，元数据失实尤其刺眼）；`delivery_head` 未填 `768a0933`，而该 commit 由 Owner 自己创建（reflog:5）。
- **建议**：`status: in_review`、`delivery_head: 768a0933`（若 Owner 认为 Review 期间应保持 `in_progress`，则须删改 `:67` 的转态声明，二者取一）。

### P3-2 — Handoff 提交链表与真实链路不符（独立反证）
- **文件:行**：`doc/handoffs/...-delivery-20260930.md:6`（`delivery_head: 74022cdc + 本 Handoff 文档提交`）、`:25-29`（表内**仅列** `74022cdc | claim`）、`:29`「实现与证据为 claim 之上的**工作区状态**」
- **触发条件**：集成方按 Handoff 核对交付 commit。
- **影响**：reflog（只读，独立证据）显示 `74022cdc` 之后依次有 `65f0facb`（实现+证据已提交）、`1dd30dc7`（handoff）、`768a0933`（证据归一化）——即 Handoff 文档提交时实现早**已入库**，「工作区状态」与提交链表均失实/不完整（与 DIAG-002 r2 的 N-2 同类，当时由集成方收口）。
- **建议**：集成交接时按 reflog 写实三段链（含 tip `768a0933`），并说明证据捕获时点（各 log 头记 `worktree @ 74022cdc`）与提交时点的差异。

### P3-3 — AC4 证据未枚举实际变更文件，且混用「已提交 range」与「工作区 range」
- **文件:行**：`verification/.../raw/ac4-scope-proof.log:5-7`（`git diff --name-status 4ed3c044..HEAD` 只列出 1 条 doc 文件）、`:12-13`（grep 过滤后 `EXIT=1`）
- **触发条件**：复核「产品面仅 2 个目标文件」。
- **影响**：AC4 的正面枚举实际只覆盖 claim commit；产品/证据文件当时的未提交状态由日志自己的注（`product files staged separately`）承认。唯一支撑「无越界」的是**过滤后的** grep 退出码，看不到完整文件清单，等于让 Reviewer 以 AC1 代替 AC4。
- **建议**：补录未过滤的 `git diff --name-status 4ed3c044`（工作区态）+ `git status --porcelain`；我静态侧可做到的旁证是：`verification/DOC-FIX-.../` 下确有且仅有 5 个文件（无多余产物）、`doc/reviews/DOC-FIX*` 零命中（与「Review 尚无」一致）。

### P3-4 — 同类第三处过时注释未登记：`run_smoke.py:303`
- **文件:行**：`experiments/M2-TA3-A/run_smoke.py:303`（`# Known planner gap: region-less backfill chain (M2-AC1 handoff).`）
- **触发条件**：读者在同一文件同一函数内自上而下阅读（`:273-275` 已改、`:303` 未改）。
- **影响**：文件内同时存在「gap 已 FIXED」与「Known planner gap」（现在时），且 M2-TA3-A L-7（`M2-TA3-A.md:125`）登记的 ①②③ 分别是 `:273`、`generated_at_utc`、`--keep-scratch`——**`:303` 不在登记内**，DIAG-002 AC4（`DIAG-M2-LOCK-CHANGED-REPRO-002.md:45`）也只登记了两处。即「两处」口径漏了同类的第三处。
- **建议**：不在本 head 修（冻结范围 + M2-TA3-A 证据锚定面），但**必须在集成记录登记为 L-7 ④**；注意 `:305` 的字符串字面量 `"defect:known-planner-gap-lock-changed"` 是证据键，**不得改名**（只可修注释措辞）。

### P3-5 — 新注释重用曾被 DSH 判为易误导的「page-level chain」措辞
- **文件:行**：`experiments/M2-TA3-A/run_smoke.py:273`（`(real detect; page-level chain; …)`）；先例 `doc/reviews/M2-TA3-A-dc2b9aca-dsh-r1.md:40-43`（P2-2「整页链」易被误读为 Run1 覆盖全部 region）、闭合要求见 `doc/reviews/M2-TA3-A-c522729e-dsh-r2.md:20`（须补「region 级步骤只作用于 primary region」句）
- **触发条件**：读者据该注释判断 Run1 覆盖面。
- **影响**：`PAGE_SELECTION` 标签提供了部分消歧，但「page-level chain」正是 r1 已判定的高估触发词，新注释未附 primary-region 限定。属文本正确性/AC3 范畴的**低危**回归。
- **建议**：改为中性描述（如 `real detect; page-scope run`）或补「region-level steps act on primary region only（Run2 covers the rest）」。

### P3-6 — AC1 证据是「事后归一化副本」，原始捕获未留存
- **文件:行**：`verification/.../raw/ac1-comment-only-diff.log:39`（`provenance note: whitespace-only normalization applied to this generated diff log …`）+ reflog:6 的 `768a0933`（handoff 之后才做的归一化提交）
- **触发条件**：任何要求「原始日志正文不重写」的复核。
- **影响**：与 M2-TA3-A 的 P1-1 处置先例（`M2-TA3-A.md:132`：新增 `00-provenance.txt`、**原始日志正文不重写**）方向相反——此处 raw 被原地改写，原始文本仓库内已无副本；且该改写发生在 Handoff 提交**之后**，Handoff 未提及 tip 含此 commit。归一化本身经披露、且我已用 tip 字节独立复核其内容无欺（见下），故非 P1/P2。
- **建议**：若原始 diff 尚可重现，另存 `ac1-comment-only-diff.raw.log` 并在现文件名后加 `.normalized`；否则在附注中写实「原始捕获已不可得，仅披露」。

### P4-1 — 跨文档行号锚点因净 +2 行而漂移
两文件各净 +2 行，导致 `doc/tasks/DIAG-M2-LOCK-CHANGED-REPRO-002.md:45,87`、`doc/handoffs/DIAG-M2-LOCK-CHANGED-REPRO-002-zcode-delivery-20260930.md:26` 的 `acceptance_bridge.py:338-340`、以及 `doc/reviews/M2-TA3-A-c522729e-dsh-r2.md:23` 引用的 `run_smoke.py:489-491`、`:464` 等行号不再精确。**历史 Review/证据正文不应改写**（本 Task 亦无权改）；建议在集成记录加一行「本 Task 后相关行号整体 +2」的换算注。

### P4-2 — docstring 相邻句的措辞张力（冻结范围内，仅登记）
`src/bootstrap/acceptance_bridge.py:336-337`「kept as a fail-closed safety net for **the region-less case**」与 `:338-341`「The historical **region-less** … gap … was fixed」并置；M2-P1 之后，regionless 不再是 `blocked` 的已证成因（DIAG-002 S1 显示 regionless 链已 COMPLETED）。因 Task 明确要求保留该句，仅作未来触碰时的清理项。

### P4-3 — 事实源文件的 YAML 重复键（上游，非本 Task 引入）
`doc/tasks/DIAG-M2-LOCK-CHANGED-REPRO-002.md:15,17` 有两条 `integration_commit:`（`null` 与 `1faf6c1b`）——正是本 Task 新注释所引的 merge 事实源。严格 YAML 解析器（重复键报错）会读失败。建议 Integrator 顺手清理。

### P4-4 — 导航面残留一句失效陈述
`doc/tasks/README.md:7`「当前无 `in_progress`/`ready` Task」在本 Task 存续期间已不成立；`doc/00_INDEX.md` 不做 Task 枚举（无对应条目不构成缺陷）。按 `doc/09_COLLABORATION.md:54`，导航面由 Codex 负责，故仅提示集成时回填。

---

## 复核六点逐项清单

**（1）AC1 diff 是否全为注释/docstring —— verified（附 1 项 not_verified 子项）**
- verified：`ac1-comment-only-diff.log:7-14` 的 hunk 为 `-1/+3` 行，全部 `#` 注释；`:22-34` 的 hunk 全部位于三引号 docstring 内（含把 `Both phases are the production` 重排到独立行——仍是 docstring 文本）；`:15` 的 `from domain.tasks.models import …` 为 context，未变。**无** import/字符串字面量（docstring 外）/空行重排迹象。
- verified（独立）：我用 tip 文件字节逐行比对了 `+` 侧——`src/bootstrap/acceptance_bridge.py:337-343` 与 `experiments/M2-TA3-A/run_smoke.py:273-275` 与 log 的 `+` 行**逐字一致**，`-` 侧与 DIAG-002 引用的原文一致，证明交付内容与证据自洽（非粘贴造假的典型特征）。
- not_verified：无法执行 `git diff`，故 `index 186e40e2..4f6abfdb` / `160386ba..06d72f9a` 两个 blob hash、以及「除这两处外无其它变更」的 git 级全量确认未由我独立复算（log 为归一化副本，见 P3-6）。闭合条件：Integrator 跑一次 `git diff 4ed3c044 -- <两文件>` 比对。

**（2）新注释事实正确性 —— verified（含 2 处限定说明）**
- verified：M2-P1 merge=`a174fb9c`（`doc/tasks/M2-P1.md:18` `integration_merge: a174fb9cb5ed…`；`doc/REBASELINE_PLAN.md:64`；`doc/STATUS.md:96`）。DIAG-002 merge=`1faf6c1b`（`DIAG-M2-LOCK-CHANGED-REPRO-002.md:17,91`；`STATUS.md:28`「done @integration 1faf6c1b（parents d69a3e1c+2c13530b）」）。
- verified：「pre-fix anchor reproduces, HEAD does not」准确——S2@`d268a170` = `REPRODUCED`（`DIAG-002.md:43`），S1@HEAD = `NOT_REPRODUCED`（`:42`），且 `d268a170` 确为 M2-P1 merge 的 main 侧 parent（`STATUS.md:96`；`doc/reviews/DIAG-M2-LOCK-CHANGED-REPRO-002-57a83485-dsh-r1.md:22` A2）。新注释**未**引入 DIAG-002 明确保留的推断限定之外的断言（未声称真 docTR 修复前会触发），与 AC3 一致。
- verified：新增的登记出处引用 `(M2-AC1 handoff §风险与遗留)` 成立（`doc/handoffs/M2-AC1-zcode-delivery-20260928.md:98,101` 有该节与对应原文），比旧文的裸 `(Handoff §风险与遗留)` 更精确。
- 限定①：`:341` 的「HEAD does not」在证据层对应 S1 的运行点 `57a83485`（Owner branch head，后集成为 `1faf6c1b`）——措辞为仓库通用简写，可接受，但严格应写锚点语义。限定②：见 P2-1/P3-5。

**（3）保留句「NOT exercised by the released acceptance evidence (DSH r1 F-007)」是否仍真实 —— verified，且不因 gap 修复而改变**
- verified：`src/infrastructure/providers/mock_local.py:46-52` 明示「the released acceptance loop seeds Regions … **the `detect` step never executes** … its detect path is NOT exercised or accepted by the M2-AC1 evidence」；代码侧一致：`acceptance_bridge.py:310-319` 在 seed 阶段即为每页建 Region（`origin=MACHINE`），故 `method_run_pipeline` 走 region 级链（`:333-335`、`:349-363`）。
- verified：DIAG-002 §起草事实（`:36`）同口径「M2-AC1 released 验收 loop 从未执行 detect」。DIAG-002 的 S1 走的是 `assemble_core_services(mock_local_providers=True)`，**不是** released 验收路径，因此「该分支未被已释放验收证据覆盖」这一边界在 M2-P1 修复后**依然成立**。
- 限定：同段落 `:336-337` 的「fail-closed safety net for the region-less case」理由句现在时性偏软（见 P4-2）。

**（4）字节码探针方法有效性 —— partially_verified / 作为「零逻辑变化」的独立证明 not_verified**
- 有效部分：docstring 与注释都不产生 `co_code` 字节，故 `co_code` 全等与本次改动**相容**；`37+15=52` 与结论行 `BYTECODE-PROBE: ALL-EQUAL` 在 log 内**自洽**（`ac2-bytecode-probe.log:1-3` 与 `Task:34,54`、`Handoff:19,36,46` 三处数字一致）。
- not_verified：探针源码在仓库内**零命中**（全仓 `co_code`/`BYTECODE-PROBE` grep 仅命中该 log 与文档），故对象计数、递归覆盖度、改前 blob 取得方式、失败处理（对象数不等时是否报错）均不可独立复核；log 无环境头/EXIT（见 P2-2）。
- 盲区（明确回答/是否有本 Task 触及）：有，且**已被触及**——`co_consts`（本 Task 的 docstring 即命中此维，`co_consts[0]` 必然变化）、`co_names`/`co_varnames`/`co_freevars`/`co_cellvars`、`co_exceptiontable`、`co_linetable`/`co_firstlineno`（两文件各 +2 行，其后所有 code object 行号信息变化）。因此「co_code 全等 ⇒ 零逻辑变化」不成立；本 Task 的真实充分证明来自 **AC1 的人工可读 diff**（已 verified）与「docstring/注释在语义上惰性」这一论证。

**（5）L-7 ① 处置是否足以维持 M2-TA3-A 证据锚定；②③ 不动是否一致 —— partially_verified（① 的结论需限定），②③ verified**
- ①：**不足**。逻辑等价（指令流）与**字节级 provenance 自检**是两件事：`verification/M2-TA3-A/raw/00-provenance.txt:16,18` 是 sha256 清单，注释改动即令 `run_smoke.py` 行失败（P2-1）。「dc2b9aca 锚定继续可追溯」在**历史标识**意义成立，但「不受注释演进影响」不成立，须限定；建议按 P2-1 加附注。
- ②③：**一致**。二者均为代码行为项（`generated_at_utc` 语义、`--keep-scratch` no-op），与本次注释改动无交集，且 `M2-TA3-A.md:125` 已登记；不改与「最小 docs 修正」范围自洽。
- 附带：L-7 漏登记第三处同类项（`run_smoke.py:303`，见 P3-4）。

**（6）范围审计：ac4 允许路径枚举 vs 实际改动 —— partially_verified**
- verified（静态侧）：产品面两文件改动内容与 AC1 `+` 侧逐字一致；`verification/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS/` 下仅 5 个文件（release 证据 1 + raw 4），无多余产物；`doc/reviews/DOC-FIX*` 零命中（与「尚无 Review」一致）；未发现导航面被越权改写（STATUS:14-15 已是 Codex/集成侧登记，00_INDEX 不枚举 Task）。
- not_verified：无法执行 git，故实际变更集未由我 git 级枚举；且 **ac4 log 自身也没有枚举**（P3-3）。此外 ac4 的 grep 允许清单未含 STATUS/README，若 Codex 后续回填会改变结论——那是 Codex 路径，不属本 Task 越界。

---

## 结论

**Architecture**：无。本变更不触分层/契约/依赖/持久化；无逻辑改动（AC1 已证，`co_code` 探针为旁证而非充分证明）。
**Verification**：AC1 verified（含 tip 字节独立复核）；AC2③ `4 passed EXIT=0` verified（证据规格合规，但为 Owner 运行结果，我未能复跑）；AC2①② **不可复现**（P2-2）；AC3 verified（P2-1/P3-5 为限定）；AC4 partially_verified（P3-3）。无 P0/P1，故**可批准但须附条件**。

**合并前应闭合（2 条 P2）**：①为 `run_smoke.py` 补 provenance 附注并限定 Task:29/Handoff:21 的「不受影响」措辞（P2-1）；②把探针脚本 + venv/EXIT 头入库，并把「零逻辑变化的机器证据」限定为「指令流（co_code）零变化」（P2-2）。**集成记录收口（P3/P4）**：Task `status/delivery_head`、Handoff 提交链、AC4 完整文件枚举、L-7 ④（`:303`）、`page-level chain` 措辞、行号 +2 换算注、DIAG-002 frontmatter 重复键、tasks/README:7。

**集成建议（一句话）**：以 `approved_with_conditions` 交代行 Codex 集成，先把 P2-1/P2-2 两条证据/措辞条件在本 Task 允许路径内闭合（Owner 或集成方均可低成本完成），其余 P3/P4 由集成记录与导航回填一次性收口。
