---
task_id: P02PRE-R0S5
reviewer: DeepSeek Harness
author: Codex /root
base_commit: cddff58469b56e181019a8ddfeade80684bc7eb9
reviewed_head: cddff58469b56e181019a8ddfeade80684bc7eb9（工作区未提交冻结件；未做 Git 核验）
decision: changes_requested
---

# Review R2：P02PRE-R0S5（Round 1 整改后的独立复核）

> 本 Review 为**纯静态文档审查**：只读取文本，未执行任何命令/脚本，未启动 runner 或 shell，未调用 API，未运行测试或 P02PRE 查询，未检查宿主状态，除本文件外未修改任何对象。
> 我**不**声称核验过任何 bytes/SHA-256、Git HEAD/tree/branch/worktree/index、OS/Registry/WER/profile/token/ACL/path 状态，也不声称能证明“本轮零 host 查询”。相关项一律记 `NOT_VERIFIED`。

## 审阅对象与依据

| 对象 | 读取程度 |
|---|---|
| `doc/tasks/P02PRE-R0S5.md` | 全文（82 行） |
| `verification/P02/p02-readonly-preflight-r0s5-manifest-20261011.md` | 全文（70 行） |
| `verification/P02/codex-p02pre-r0s5-delivery-20261011.md` | 全文（31 行） |
| Round 1 报告 | `verification/P02/dsh-p02pre-r0s5-review-20261011.md` 全文 |
| 对账依据 | r6 manifest 全文相关段（L1–164、L235+ 定点）、`p02-readonly-preflight-r0-evidence-20261011.md`（L18–39、L83–139、L231–279）、`doc/STATUS.md`（L1–16）、`doc/REBASELINE_PLAN.md`（L1–31）、`doc/00_INDEX.md`（L1–21）、`doc/tasks/P02.md`（L1–35）、R2 dispatch prompt |
| 存在性核对 | 只读 `glob verification/P02/*r0s5*`、`*r0s4*`（不做 Git/hash 核验） |

## Round 1 findings 逐项处置核对

| Round 1 ID | 级别 | 本轮结论 | 依据 |
|---|---|---|---|
| DSH-R0S5-P2-01（历史 hash 口径） | P2 | **已解决（实质）** | manifest L20/L32/L46 已把集合写成“R0 evidence §`固定文件 hash 前/后对照` 的精确 13 项 = 12 份列名文档 + `.git/index`”，指出 `Get-FileHash` 为历史方法、不证明当前 runner，并明确其**不是** R6 `protected-invariants` 全量清单；Task L50 与 delivery L19 口径一致。12 份文件名与 R0 evidence L235–L246 逐行一致，第 13 项 `.git/index` 对应 L247。遗留一处引用缺陷另记 **DSH-R0S5R2-P3-01**。 |
| DSH-R0S5-P2-02（身份基准与精确 ACL 集） | P2 | **部分解决 → 阻断** | 身份基准已补：manifest L28 写出 r6 期望 user `HOME-MY\49745`、SID `S-1-5-21-2196946971-914346751-4210154634-1001`、非提权、无 thread impersonation，与 r6 L49 一致；28 项计数（12+13+3）与 12 输入根、13 scratch leaf 的逐项枚举与 r6 L74–85、L123–135 **逐条一致**。但 **canary leaf 的根被改到主仓**，使候选集包含受保护/拒绝范围路径，违反本项“No protected/deny path is added”的验收要求，另记 **DSH-R0S5R2-P2-01**。 |
| DSH-R0S5-P3-01（状态机口径） | P3 | **已解决** | Task L5=`status: in_review`；STATUS L3/L7/INDEX L5 记 `in_review / ROUND_2`；PLAN L3/L19 记 Round 2 进行中。四处一致。 |
| DSH-R0S5-P3-02（新增授权标识） | P3 | **已解决** | manifest L5 明写 “the user's newly issued 2026-10-11 authorization for the separate **P02PRE-R0S5** controlled read-only task”，且 “does not extend the earlier registry-risk waiver”；L7–L13 原样保留既有风险/Gate 状态，二者分离清楚。 |
| DSH-R0S5-P3-03（“已证明安全”预设） | P3 | **已解决（治理文本）** | STATUS L7「逐项通过证明和审查……当前尚无已清除的 host getter」、PLAN L5「逐项证明无副作用、并经独立 Review + Codex adjudication 清除……目前尚无 host query 获准」、INDEX L5、P02.md L24 均已改为条件式。Task L26 仍有同类措辞残留，另记 **DSH-R0S5R2-P3-03**。 |
| DSH-R0S5-P3-04（AC 勾选） | P3 | **结构已满足，个别勾选失准** | Task L44–L46（五类分类、final Review/adjudication/集成验证、风险与 Gate 原值）保持 `[ ]`，final 项未被提前勾选，符合要求；L40、L42、L43 的勾选与其陈述相称（L43 属 Owner 自我报告，见末节）。但 L41「候选对象与读取边界只引用 r6 精确登记对象」被勾选，而 canary 根并不等于 r6 登记对象，另记 **DSH-R0S5R2-P3-04**。 |

## Findings（本轮新增）

| ID | 级别 | 文件/行 | 触发与影响 | 证据 | 建议 |
|---|---|---|---|---|---|
| **DSH-R0S5R2-P2-01** | **P2** | manifest L42（并涉 L30、L44）；Task L53/L55 | manifest §`Exact ACL object set` 第 3 组把三个 canary leaf 写成 **主仓**路径 `G:\CODEX\New Manga\verification\P02\tmp\{smoke-readonly-probe,lpac-write-control,lpac-write-deny-control}\`。r6 把 “3 canary 规则”绑定在 scratch `G:\CODEX\P02-scratch-build-source`，R0 历史 ACL 取证也全部落在 scratch 内。后果：（a）把**主仓（r6 明确列为 protected/deny scope）**加入“28 项 ACL 候选”，直接违反 Round 1 P2-02 的 “No protected/deny path is added”；（b）与 manifest 自身 L30「no protected/deny-scope host path」及 L44「No ACL query is authorized for `G:\CODEX\New Manga`」**自相矛盾**；（c）Task L53「ACL 候选严格等于 manifest 28 个对象」会把该错误根路径带进后续执行 scope：一旦 runner gate 被解除，可能在主仓 `verification\P02\tmp\` 做描述符读取，甚至按 L142 的正向 canary 语义在受保护目录内创建 `p02-lpac-write-canary-20261010.bin`。当前 runner 仍未清除，故尚无即时 host 后果，但该对象集在修正前不得作为执行依据。 | r6 L35「scratch \| `G:\CODEX\P02-scratch-build-source`；… 13 exact leaf + 3 canary 规则」；r6 L115 §`Scratch 写入、ACL 与输入/输出`；r6 L141–143 三条 canary 均为 scratch 区段内的仓库相对路径；r6 L157 记 canary 文件为 `verification/P02/tmp/lpac-write-control/p02-lpac-write-canary-20261010.bin`；r6 L87 明列主仓及各 worktree 为 protected/deny scope；R0 evidence L114–L116、L117 三条 canary 与 canary 文件均以 `G:\CODEX\P02-scratch-build-source\...` 精确路径查询，L136 汇总亦在该语境下。 | 把该组三行改回 scratch 根：`G:\CODEX\P02-scratch-build-source\verification\P02\tmp\...`（与 L41 的 13 leaf 同根），并在该组显式标注“相对于 r6 scratch clone”；同时保持 L44 对主仓/工作树/其它 clone 的 ACL 禁止不变。修正后需就新 head 再复核，不沿用本轮判断。 |
| DSH-R0S5R2-P3-01 | P3 | manifest L20 | 引用 “R0 evidence §`实际命令`”，但 R0 evidence **不存在**该段落。历史 `Get-FileHash` 记录实际位于 R0 evidence §`实际执行调用与结果`（L18 起，L29 为 `Get-FileHash -LiteralPath -Algorithm SHA256` 行），r6 L229 亦有“实际命令”记录。属 Round 2 新增的可追溯性缺陷，易使后续轮次找不到对账位置。 | grep R0 evidence 无 `实际命令` 命中；该文件标题仅 `## 实际执行调用与结果`（L18）；r6 L229 为 `实际命令：…Get-FileHash…`。 | 将引用改为 R0 evidence §`实际执行调用与结果`（或 `L18–L29`），如确欲指向 r6 侧记录则写 `r6 L229`，不要指向不存在的段落名。 |
| DSH-R0S5R2-P3-02 | P3 | Task L71（与 L34 对照） | 「Task 文件写入所有权」只列 `verification/P02/dsh-p02pre-r0s5-review-20261011.md`（Round 1 报告），未包含 L34 已登记的 Round 2 报告路径 `dsh-p02pre-r0s5-review-r2-20261011.md`。Reviewer 本轮写入路径仅由 L34 的交付登记与 manifest L64 的 `*r0s5*` 通配覆盖，职责清单未同步，属授权路径表述不精确（不构成扩权）。 | Task L34 登记两份 Review（含 r2 路径与 prompt/log）；L71 仅列 Round 1 文件名；`glob` 显示 `dsh-p02pre-r0s5-review-r2-20261011.prompt.md` 与 `.stdout.md` 已存在，而 L71 未提。 | 在 L71 的 Reviewer 清单中并列 Round 1/Round 2 两个精确文件名（可按 round 编号分列），或改为写明“`verification/P02/dsh-p02pre-r0s5-review*r2*-20261011.md` 等本 Task 登记的 Review 交付路径”。 |
| DSH-R0S5R2-P3-03 | P3 | Task L26（与 L43、L75 对照） | 目标句仍写「审查并执行**一切已证明安全的**只读候选，**再由**非作者 Reviewer Review、Codex adjudicate」，字面预设存在“已获证明安全”的候选，且语序上像“先执行、后 Review”。Task L43/L75 与 manifest L50/L56 的现行口径是“无任何 getter 已清除；先经独立 Review + Codex adjudication 才可执行”。属 Round 1 P3-03 在 Task 正文的同类残留（治理文本已改）。 | Task L26 vs L43、L75；manifest L50「No current-host getter/query … has yet been independently cleared」、L56「no P02PRE host/OS/registry/WER/profile/token/ACL/path/environment/hash query is permitted」。 | 将 L26 改为与 L75 同序同谓词，例如「先核对精确执行边界，仅在逐项取得无副作用证据并经非作者 Review 与 Codex adjudication 清除后，才执行相应只读候选；当前无候选获准」。 |
| DSH-R0S5R2-P3-04 | P3 | Task L41 | AC L41「候选对象与读取边界**只引用 r6 精确登记对象**；Profile 路径不猜测，不扩大 registry view、环境变量、文件集合或输入」被勾选 `[x]`，但 canary 三行并非 r6 登记的 scratch 对象（见 DSH-R0S5R2-P2-01），该勾选与其内容不符；AC 状态与交付事实的映射因此再度失准。 | Task L41 `[x]`；manifest L42；r6 L35/L141–143；R0 evidence L114–L116。 | 修正 DSH-R0S5R2-P2-01 后重新裁定 L41 的勾选状态；在 adjudication 中逐项记录 AC 状态与依据（含被 P2 影响的项暂记“待修订后确认”）。 |

**本轮计数（Round 1 已解决的 finding 不重复计分）：P0 = 0；P1 = 0；P2 = 1；P3 = 4。**

## 安全面与授权面结论

- **无隐藏查询授权**：manifest L50/L54/L56 冻结了 runner 与全部 getter（“no P02PRE host/OS/registry/WER/profile/token/ACL/path/environment/hash query is permitted”），Task L43/L62/L75 与 delivery L13 一致；三件对象的任何语句都未出现“已放行/可运行/绕过 shell gate”的许可。本轮的 runner 状态仍为 `NOT_SAFE_FOR_R0`，方向正确且应原样保留。
- **未把只读授权写成 waiver/Gate PASS/Barrier 放行**：Task L22/L24、manifest L5/L13、delivery L29、STATUS L13、PLAN L5、INDEX L7 逐项维持 `private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、`technical condition unmet; user explicitly accepted residual risk`，并保持 Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`；未发现 build/Cargo/AC1–AC7 或 profile/registry/ACL 写入的授权扩张。
- **五类语义**：manifest L70 的定义与 delivery 表用法一致（历史局部观察 `PASS_WITH_EVIDENCE`、未执行不记 `FAILED`、当前状态 `UNPROVABLE`、动态行为 `REQUIRES_ACTIVE_TEST`、未清除方法 `NOT_SAFE_FOR_R0`），未把历史结果外推为当前证据。
- **唯一实质安全缺口是 DSH-R0S5R2-P2-01**：它是“精确对象集”内的错误路径归属，不是新增执行许可；但因当前零查询冻结，其危害被 runner gate 暂时中和——冻结一旦解除，该错误会直接指向受保护主仓，故必须在任何执行授权之前修正。

## 我未能独立验证的事项

- 任何输入对象的 **bytes/SHA-256**（含 prompt 给出的三个 r0s5 文件、Round 1 报告、manifest L21 引用的 R0S4 Review/adjudication pin 值），以及 delivery L11 的 session/mount/digest 记述。
- **Live Git 状态**：HEAD/tree/branch/common-dir/worktree 数、`doc/STATUS.md` L5 的 NUL status 记录与 `.git/index` hash、工作区未提交内容的完整性与作者归属。
- **宿主与 OS 事实**：主仓 `verification\P02\tmp\` 与 scratch `verification\P02\tmp\` 三个 canary leaf 在磁盘上的实际存在性/ACL（本轮仅比对文档文本，未读盘）；Registry/WER/profile/token/环境变量状态。
- **“本轮零 host 查询、未启动子进程、未换 shell、未写入被检查对象”**：属 Owner 自我报告（Task L43、delivery L13），记为 `NOT_VERIFIED`；同样无法验证 R0 历史取证本身的真实性，只能核对文档间引用一致性。
- 各 Agent 的 model/effort 声明（Task L36）以及 r6、R0 evidence 是否即为其被引用的冻结版本。

## 结论

**决策：`CHANGES_REQUESTED`（针对工作区当前冻结件的 Round 2 修订；P0/P1/P2/P3 = 0/0/1/4）。**

- Round 1 的 **P2-01、P3-01、P3-02、P3-03 已解决**；**P2-02 仅部分解决**（身份基准与 28 项计数/12+13 枚举齐备，但 canary 根路径错误引入了 protected/deny 路径，验收条件“No protected/deny path is added”未满足）；**P3-04 结构上已满足**（final 类 AC 保持未勾选），但 L41 的勾选因 DSH-R0S5R2-P2-01 失准。
- 阻断项只有一项 **DSH-R0S5R2-P2-01**：把三个 canary leaf 改回 r6 的 scratch 根并在对象集中显式标注相对根，同时不得触碰 L44 对主仓/工作树/其它 clone 的 ACL 禁止。另四项 P3 随之收敛（L20 引用、L26 措辞、L71 所有权清单、L41 勾选状态）。
- **唯一建议的下一步**：由 `Codex /root` 修订上述 manifest 与 Task 文本并重发 Round 3 文档复核；期间**不得**派发任何 host/OS/Registry/WER/profile/token/ACL/path/environment/hash 查询，不得切换 shell 或运行 getter，不得创建/删除 profile，不得查询/安装/启用/启动 Windows Sandbox，不得触碰 Build/Cargo 与 AC1–AC7。修正涉及“精确对象集”实质内容（P2-01），因此**不得**沿用本轮判断，须就新 head 追加一轮 Review。
- 本 Review 不构成 waiver、Gate PASS、Build Barrier 放行或执行授权，不代替 Codex adjudication；`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION` 与 Hard Build Barrier 原值不变。
- 本 Reviewer 自身副作用 = ZERO（除创建本文件外）：未运行命令/Git/hash、未启动进程或 shell、未调用 API 或 P02PRE 查询、未修改任何既有对象、未抓取外部网页。本文件 bytes/SHA-256 由 Codex 在归档阶段独立复算，故不在此声明自身 digest。
