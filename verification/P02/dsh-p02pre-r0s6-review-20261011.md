# P02PRE-R0S6 独立静态 Review（非作者 Reviewer：DeepSeek Harness）

## 0. 结论

**CHANGES_REQUESTED**

- Findings 计数：**P0 = 0 / P1 = 0 / P2 = 4 / P3 = 6**
- 无越权、无 runner 释放、无 `UNPROVABLE → PASS` 转换、无 Gate/Build Barrier 解除。核心安全立场正确且严格。
- P2 全部是**文档精确性/绑定完整性**问题，可用措辞与一行级补充修复，不改变冻结范围、不需要新主机证据。
- 本 Review 是纯静态文档判断，**不是主机证据，不是 Gate PASS，不解除 Build Barrier**。

结论摘要：Task 与 manifest 忠实保留用户裁决（`private_registry_absence=UNPROVABLE`、`Owner Risk Acceptance=APPROVED`、`Gate Disposition=WAIVED_BY_OWNER`、`Technical Gate=NOT_SATISFIED`），并正确坚持“本轮不放行任何 runner/query”。需要修改的是：`p02pre-r0s6-*` 前缀式表述、R0 evidence 对象集未按 SHA 绑定、Reviewer dispatch runner 未被纳入“零 runner”口径、以及交付产物清单与既有 dispatch 产物集合不一致（含已存在报告路径的覆盖语义缺失）。

---

## 1. Review 对象与静态核对范围

实际读取（全部只读、无写入）：

1. `doc/tasks/P02PRE-R0S6.md`
2. `verification/P02/p02pre-r0s6-manifest-20261011.md`
3. `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md`（被引用的 source pin）
4. `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-review-20261011.md`
5. `verification/P02/codex-p02-owner-risk-waiver-manifest-r6-adjudication-20261011.md`
6. `verification/P02/codex-p02pre-r0s5-adjudication-20261011.md`
7. `verification/P02/codex-p02pre-r0s5-verification-20261011.md`
8. `verification/P02/codex-checkpoint-p02pre-r0s5-20261011.md`
9. **扩展读取（已披露）**：`verification/P02/p02-readonly-preflight-r0-evidence-20261011.md` —— 因为 Task L53 与 manifest §4.4 明确把“R0 evidence 的 13 项 hash 集合”作为冻结对象，必须核对该引用是否可解析、内容是否为 12 列名文档 + `.git/index`。
10. **只读文件枚举（不读内容）**：`verification/P02/*preflight*`、`verification/P02/*r0*`、`verification/P02/dsh-p02pre-r0s6-*`、`verification/P02/p02pre-r0s6-*`，用于确认引用对象是否存在、以及交付产物路径现状。

未执行任何 shell/Git/hash/API/host/OS/registry/WER/profile/token/ACL/path/environment/process 查询；未运行代码、构建、Cargo 或 AC；未修改任何文件。

---

## 2. 授权忠实性核对（逐项）

| 用户授权原文要点 | Task/manifest 落点 | 判定 |
|---|---|---|
| 仅批准受控只读取证阶段；不是新豁免、不是 Gate PASS | Task L22、L26、L74；manifest L5、L12–13、L46、L56 | ✅ 一致，未扩大 |
| 保持 `private_registry_absence=UNPROVABLE` | Task L26、L63；manifest L7、L13、L55 | ✅ 一致 |
| 保持 `Owner Risk Acceptance=APPROVED` | Task L26；manifest L9 | ✅ 一致 |
| 保持 `Gate Disposition=WAIVED_BY_OWNER` | Task L26；manifest L10 | ✅ 一致（manifest L11 另带原文句） |
| 允许“按 r6 核实身份/SID/token、profile/目标路径 metadata、只读 ACL、TEMP/cache/scratch 与 protected path 解析、protected hash、WER/T0 getter” | Task §“冻结的只读查询边界” L50–L55；manifest §4 | ✅ 全部逐项覆盖为**候选**，且逐项拒绝放行 |
| 安全性不确定就不执行，标 `NOT_SAFE_FOR_R0`，继续其他项 | Task L22、L40、L48；manifest L5、L27–28、L36、L38 | ✅ 严格执行 |
| 禁止 Create/Delete profile、registry 写、ACL 改、profile 创建删除、Windows feature、build/Cargo、AC1–AC7、主动写 protected path、未证明只读的 API | Task L59–L63；manifest L46 | ✅ 逐项覆盖 |
| 五态分类 + 非作者 Review + Codex adjudication | Task L39–L42；manifest §6 | ✅ 结构与用词一致；“未执行≠FAILED”明确写入（manifest L55、Task L41） |
| 不得解除 Build Barrier | Task L26、L44、L63；manifest L12、L56 | ✅ 一致 |

**保留值核对**：Task L30 的 base HEAD `cddff584…` / tree `c25d051a…` 与 R6 L6、R6 adjudication L9 一致；Task L32 的 R6 SHA `626E000A…09DE` 与 manifest L17、R6 review L37、R6 adjudication L11 一致（本 Review 未复算 hash，见 §8 边界）。

**对象/数量核对（与 R6 原文逐条比对，全部正确）**：

- 12 个输入 roots：R6 L74–L85 表 12 行 ✅（注意：第 12 行是 scratch source root，R6 自身在 L36/L162 也把它计入“12 输入根”，这是 R6 的既有措辞，不构成本轮新缺陷）。
- 13 个 scratch output leaves：R6 L123–L135 共 13 行 ✅。
- 3 个 canary leaves：R6 L141–L143 ✅。
- 章节名引用：§`允许读取路径`(L68)、§`TEMP/cache 与新 Unicode 环境块`(L89)、§`Scratch 写入、ACL 与输入/输出`(L115)、§`固定身份、Profile 与 API 参数`(L45) 均逐字存在 ✅。
- scratch 基线 HEAD `7ce3c40c…` / tree `ce8056b8…` / private common-dir / 无 remote / 无 alternates：manifest L36 与 R6 L117 一致 ✅。
- 身份 `HOME-MY\49745` / `S-1-5-21-…-1001`：manifest L32 与 R6 L49 一致；moniker/SID 采用“继承 R6 原文”而不重述，避免转录漂移 ✅（R6 L50–L51 原文完好）。
- R0 evidence 13 项：实读 `p02-readonly-preflight-r0-evidence-20261011.md` L235–L247，确为 **12 份文档 + `.git/index`** ✅（对象集引用是准确的，但缺 SHA 绑定，见 P2-02）。

---

## 3. runner / wrapper 安全前提核对（本轮最关键项）

**结论：完全正确，未落入用户明确禁止的方法。**

- Task L48 明确：“`exec_command`/PowerShell runner 的外层 executable、argv、startup/profile/history、wrapper、临时/日志路径与子进程行为仍无无副作用证据；因此通过它调用的候选方法均保持 `NOT_SAFE_FOR_R0`，**不得在同一未闭合 runner 中“先启动再观察”**。”
- manifest L25 明确 `login=false` 与同进程 inline 命令**不能**证明 launcher/argv/profile/history/wrapper/cache/temp/log/child 边界；L26 明确禁止“启动当前 runner 只为观察是否产生 child 或写 history/log/temp”。
- manifest §4 末句：“Because no host query is released, no inline script or getter parameter list is authorized for execution.”

因此：**依赖当前 runner 的任何 getter 均应为 `NOT_SAFE_FOR_R0`**，本文件处理正确；我作为 Reviewer **不批准**任何“先启动再观察”的验证路径，也**不批准**基于 `login=false`、命令行体、getter 名称或“看起来只读”的任何放行。

---

## 4. 逐候选方法边界核对

| 候选方法 | 依赖面 | 文档处理 | 判定 |
|---|---|---|---|
| `WindowsIdentity.GetCurrent(false/true)`、`WindowsPrincipal.IsInRole` | 同进程 .NET/BCL + 进程 token；不产生子进程，但模块加载/JIT/provider 初始化边界无静态证据 | Task L50 列为候选且 L48 全局拒绝；manifest L27 明确“名称本身不构成预批准” | ✅ 分类正确（`NOT_SAFE_FOR_R0`）；manifest L32 另明确 role 结果不能替代拿不到的 token elevation/impersonation 字段 → 无 `UNPROVABLE→PASS` 风险 |
| `Get-Item -LiteralPath` | PowerShell FileSystem provider（managed，无外部 exe），但 provider/pwsh 启动边界未闭合 | Task L51 列为候选；manifest §4.2 “No current `Get-Item` … call is released” | ✅ 正确 |
| `Get-Acl -LiteralPath` | PowerShell Security provider + SDDL 转换；可能触发模块/类型加载 | Task L51 列为候选；manifest §4.2 同句拒绝；L27 明确 “identity/ACL getters can involve API/provider/runtime behavior” | ✅ 正确，措辞为 “can involve” 属恰当保留 |
| environment/path/hash getter | 同进程 BCL/cmdlet；`Get-FileHash` 只读但读文件内容 | Task L52–L53；manifest §4.3–§4.4 全部未放行 | ✅ 正确 |
| **Git plumbing（`rev-parse HEAD`、`HEAD^{tree}`、common-dir、remote/alternates）** | **需要 external `git(.exe)`** → 外部可执行 + config/helper 边界 | Task L54 列为候选、L48 点明“Git plumbing 依赖 external executable”；manifest L27、L36 明确未放行 | ✅ **用户特别要求核实的这一点结论正确**：Git plumbing 确需外部可执行，不能仅凭 `--no-optional-locks` 认定无副作用（R6 L158 同结论） |
| WER/T0 getter | registry provider / 目录枚举 / T0 顺序未冻结 | Task L48、L62；manifest §4.3、L38 未放行 | ✅ 正确 |

**重要正向确认**：manifest L32 与 R6 review L54/L57/L63 一致地保留了 `profile_folder_no_create_contract=UNPROVABLE`、M8 Getter 三项 `NOT_RESOLVED/BLOCKED`、`t0_bootstrap_safe_order=NOT_RESOLVED/BLOCKED`，没有被本轮的“只读”名义重新包装为已解决。

---

## 5. 写授权 / 通配符 / 产物核对

**用户要求的“无 `p02pre-r0s6-*` 通配符写入权”**：

- manifest §5（L42）与 Task L69 的正式写入清单均为**精确文件枚举**，无 `*` 通配符 ✅。R6 源文件 `p02-owner-risk-waiver-execution-manifest-r6-20261011.md` **不在**任何写入清单内，其 SHA 绑定不会被本 Task 破坏 ✅。
- Reviewer 写入边界正确：Task L70 明确“Reviewer 不执行 host query、不修改其他文件”，与用户本轮指令一致 ✅。
- **但** Task L34 出现 `verification/P02/p02pre-r0s6-* 前缀` 的表述（见 P2-01），以及产物清单与既有 dispatch 产物集合不一致（见 P2-04）。

---

## 6. Findings

### P2-01 — Task 使用 `p02pre-r0s6-*` 前缀式表述，形成通配符漂移面
- **级别**：P2
- **文件/章节**：`doc/tasks/P02PRE-R0S6.md` L34（“最终 evidence、adjudication、verification、checkpoint 使用 `verification/P02/p02pre-r0s6-*` 前缀”）
- **问题**：用户本轮明确要求核实“没有 `p02pre-r0s6-*` 等通配符写入权”。正式写入清单（L69/manifest §5）确实精确无通配符，但 L34 在正文里以 `*` 描述命名约定，且未标注“仅命名约定、不构成写入授权”。
- **影响**：后续可被引用为“前缀范围内的路径均可写”，与本 Task 自己的“无通配符输出路径”承诺冲突；也与 R6 体系“exact path only”的严格度不一致。
- **最小修正建议**：把 L34 改为枚举精确文件名（manifest / delivery / adjudication / verification / checkpoint / review 等），或保留前缀仅作命名说明并追加一句：“该前缀仅描述命名约定，写入权限以 §Owner 允许写入的精确文件清单为准，无任何通配符授权。”

### P2-02 — “R0 evidence 固定 13 项”未按路径/bytes/SHA 绑定
- **级别**：P2
- **文件/章节**：Task L53；manifest §4.4（L35）
- **问题**：两处都以“R0 evidence 的 13 项（12 列名文档 + `.git/index`）”作为冻结对象，但均未给出该对象的**路径、bytes、SHA-256**。实际对象是 `verification/P02/p02-readonly-preflight-r0-evidence-20261011.md`（本 Review 已核对 L235–L247，内容确为 12 文档 + `.git/index`，与描述相符）。该文件是未提交工作区文档，可被后续追加修改，因此“12 列名文档”的身份并未被 SHA 固定。
- **影响**：一旦未来放行该项 hash 复核，执行者必须自行推断对象集合；集合成员可能随该文件被编辑而漂移，违反本 Task 与 R6 的“exact object + SHA pin”原则，也使事后无法判定“复算了同一集合”。
- **最小修正建议**：在 manifest §4.4 与 Task L53 引用 `verification/P02/p02-readonly-preflight-r0-evidence-20261011.md` 的精确路径 + bytes + SHA-256，并明确“写入以该 SHA 绑定的表格为准”；若该文件尚未冻结，则改为“对象集未冻结 → 该子项为 `UNPROVABLE`，不进入未来放行候选”。

### P2-03 — Reviewer dispatch runner 未被纳入“零 runner”口径
- **级别**：P2
- **文件/章节**：Task L48/L69/L70；manifest §3、§5
- **问题**：文档宣布“当前任何 runner 的 invocation 无副作用均未证明”，并据此把全部 host getter 判为 `NOT_SAFE_FOR_R0`；但同一 Task 的交付路径依赖一次 DSH dispatch（外部 CLI + 会话/日志/mount 写入），其 launcher/argv/profile/cache/log/子进程边界同样未冻结（R0S5 verification L11–L15 记录了 `dsh headless` + `mount_session.py` 的实际调用）。文档没有把这次 dispatch 明确排除在“P02PRE host query”之外，也没有声明其副作用不作为 R0 证据。
- **影响**：这是最容易被反方引用的内部不一致（“既然 runner 不可信，为何用 runner 取得 Review”）。若不在文中划清，会使 L48 的严格声明被削弱，也可能让未来某轮以“dispatch 都能用”为由扩大放行。
- **最小修正建议**：在 manifest §3 与 Task L48 后补一句：“本 Task 为取得非作者静态 Review 而进行的 DSH/CLI dispatch 属于治理传输动作，不属于本 manifest 的 R0 host query 范围；其会话/日志/mount 副作用不作为任何 R0 证据，也不构成任何 getter 的 invocation 无副作用证据。”

### P2-04 — 交付产物清单与既有 dispatch 产物集合不一致，且缺少 create/overwrite 语义
- **级别**：P2
- **文件/章节**：Task L69；manifest §5（L42）
- **问题**：三处具体缺口：
  1. 清单包含 `…review-20261011.stderr.log`、`.exit`、`.mount.json`，但**没有 `…review-20261011.stdout.md`**；R0S5 及其后续轮次把 dispatch stdout 作为受控产物并 pin 了 bytes/SHA（R0S5 verification L15、L42）。缺失该路径意味着 raw stdout 要么写到未授权路径，要么链式证据断失。
  2. 授权名 `.mount.json` 与前序实际产物扩展名不一致（工作区观察到 `.mount.log`、`.mount.txt`、`.mount.exit`、`.mount.md` 等）。
  3. 清单未规定报告路径的 create/overwrite 语义；只读枚举显示 `verification/P02/dsh-p02pre-r0s6-review-20261011.md` **已存在于工作区**（本轮未读取其内容）。R6 体系对证据文件强制 `CREATE_NEW`、禁止覆盖/追加，而本 Task 对“原样保存 Review”未声明同类规则。
- **影响**：可能出现 (a) 授权范围外的实际写入，或 (b) 覆盖既有同名产物造成证据丢失；两种都与“exact path / no clobber”原则冲突，且属于不可逆操作。
- **最小修正建议**：按实际 dispatch 产物补齐/对齐清单（增加 `…stdout.md`，把 `.mount.json` 改为工具真实写入名或删除该项）；并增加一句：报告路径若已存在，须先记录其 bytes/SHA 并保留，采用 `CREATE_NEW` 或先保留副本，禁止覆盖、追加、重试。

### P3-01 — Task 的状态枚举不完整，与其 AC 声明不自洽
- **级别**：P3
- **文件/章节**：Task L26 与 AC L38
- **问题**：AC L38 要求把“风险/Gate 原值”写入 Task，但 L26 只列了 4 项（`UNPROVABLE`、`APPROVED`、`WAIVED_BY_OWNER`、`NOT_SATISFIED`），漏掉 `Build Authorization=AUTHORIZED_WITH_EXCEPTION` 与必须原样记录的 `technical condition unmet; user explicitly accepted residual risk`（manifest L11 有，Task 无）。
- **影响**：状态枚举在不同文件间出现差集，未来比对“原值是否被改动”时缺少唯一基准。
- **最小修正建议**：把 L26 补齐为与 manifest §1 完全同构的枚举（含 Build Authorization 与原文句），并保留“Build Authorization 枚举不等于 Barrier 解除”的限定语。

### P3-02 — `depends_on: []` 低估了实际依赖
- **级别**：P3
- **文件/章节**：Task front matter L11
- **问题**：本 Task 的冻结对象、分类框架与阻塞理由均来自 R6 manifest / R6 Review / R6 adjudication（P02M10R 链）及 R0S5 链，但 `depends_on` 为空。
- **影响**：Task graph 上看不出“R6 对象变更即失效”的依赖关系，后续可能在不重新绑定的情况下复用本 Task 的结论。
- **最小修正建议**：填为文档级依赖（R6 manifest/Review/adjudication 与 R0S5 adjudication 的精确路径 + SHA），或显式注明“依赖为文档 pin，非 Task 依赖”。

### P3-03 — 未披露 Reviewer 与继承分类的独立性关系
- **级别**：P3
- **文件/章节**：Task L31、L33；manifest §2
- **问题**：非作者 Reviewer 为 DeepSeek Harness，而本 Task 大量**继承** R0S5 的分类与阻塞理由，R0S5 的 Round 1–3 Review 亦由 DeepSeek Harness 出具（R0S5 adjudication L8）。Task/manifest 未声明“本次是对 Codex 所写 R0S6 文档的独立 Review，且不重新裁决 Reviewer 自己先前的 R0S5 结论”。
- **影响**：独立性边界不显式，容易被误读为 Reviewer 在复核自己的产物；R6 review 对自身 M7/M9 产物作了同类披露（R6 review L31），本 Task 缺少对应声明。
- **最小修正建议**：在 Task §“基线、角色和依据”增加一句独立性声明：Reviewer 非本 Task/manifest 作者，仅审 R0S6 文本对 R0S5 分类与 R6 边界的引用忠实性，不重新批准自己此前的 Review 结论。

### P3-04 — 候选 getter 清单缺少逐项 `NOT_SAFE_FOR_R0` 标记
- **级别**：P3
- **文件/章节**：Task §“本 Task 冻结的只读查询边界” L46–L55（尤其 L50–L54）
- **问题**：小节标题为“冻结的只读查询边界”，内部逐条给出具体方法/参数（`WindowsIdentity.GetCurrent(false/true)`、`Get-Item -LiteralPath`、`Get-Acl -LiteralPath`、`rev-parse HEAD`、`HEAD^{tree}`、remote/alternates 等），但 `NOT_SAFE_FOR_R0` 只在章首全局声明一次，逐条无标记。
- **影响**：存在“把候选条目当成已冻结获批子集”的引用漂移风险（与 R0S5 曾出现的 P3 措辞问题同类）。
- **最小修正建议**：小节标题改为“候选只读查询集合（全部未获准）”，并在每个条目末尾追加 `→ 当前分类：NOT_SAFE_FOR_R0`。

### P3-05 — 执行顺序与用户原文顺序相反，且未给出具名解阻路径
- **级别**：P3
- **文件/章节**：Task L24、L39–L42
- **问题**：用户原文顺序为“执行 R0 只读预检 → 分类 → 非作者 Review → Codex adjudication”；本 Task 实现为“冻结 manifest → Review → adjudication → 仅执行获放行项”，虽更保守且被用户“不确定就不执行”条款覆盖，但未显式记录这是有意的收紧；同时 Task 未给出下一轮可审查的 runner 合同化解阻路径，导致结果与 R0S5 结构性同构（零新增证据）。
- **影响**：用户目标“最大限度消除可由只读取证解决的阻塞”实际零推进；若下一轮仍只重复文档冻结，会形成空转。
- **最小修正建议**：加一句“本 Task 有意采用 gate-first 顺序，依据用户授权中‘某项安全性不确定就不执行’条款，不改变授权边界”；并在“当前状态”或下一轮交接处点名唯一解阻方向——冻结可审查 runner 合同（pwsh 可执行文件身份/hash、完整 argv、显式 `-NoProfile -NonInteractive`、module/telemetry/cache/history 抑制、无子进程保证）+ 逐 getter 边界证明，仍须另行 Review 与 adjudication 后才可放行（本轮不执行）。

### P3-06 — manifest 对共享治理文件的写入范围宽于 Task
- **级别**：P3
- **文件/章节**：manifest §5（L42）与 Task L69
- **问题**：Task L69 把 `doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/tasks/P02.md`、`doc/tasks/README.md` 限制为“Task/status/link 摘要”；manifest §5 只写“Owner report writes are limited to these exact repository files”，未携带同样的“仅摘要”限制。
- **影响**：单独读 manifest 会得到比 Task 更宽的治理文件修改权限，两文件不一致。
- **最小修正建议**：manifest §5 增补 Task 的同一限制短语，使两者逐字一致。

---

## 7. 五态分类（Reviewer 静态分类，非主机证据）

> 基线：R6 固定对象范围 + R0S6 manifest 冻结范围。**历史 evidence 仅适用于原对象、原时点**（R0 evidence 采集窗口 `2026-10-10T23:16:33.9414550Z`–`2026-10-10T23:17:30.4412666Z`，另含同轮 NUL Git status 与 `.git/index` 快照），不得外推为当前状态。

| # | P02PRE 剩余条件 | 分类 | 边界说明 |
|---|---|---|---|
| 1 | 历史 R0 快照：PID 12280 的 user/SID/无 thread impersonation、35 项环境变量与词法归一化、12 输入根 leaf metadata/ACL、13 scratch leaf 存在性、3 canary leaf 存在性、evidence root 11 目标 absence、WER 三目录直接子项、12 文档 + `.git/index` 前后 hash | `PASS_WITH_EVIDENCE` | 仅适用于上述对象与该 UTC 窗口；来自 `p02-readonly-preflight-r0-evidence-20261011.md` L235–L268。不覆盖 ancestor/file ID/hardlink/ADS/canonical identity，也不是当前值。 |
| 2 | 当前 user/SID/token/elevation/impersonation | `UNPROVABLE` | 查询方法同时为 `NOT_SAFE_FOR_R0`；条件值与方法安全性分列。 |
| 3 | 当前 profile / 目标路径 metadata、profile-folder pre-create absence | `UNPROVABLE` | 路径未知、不猜测（M7 `profile_folder_no_side_effect=UNPROVABLE / BLOCKED` 未被本轮改变）。 |
| 4 | 当前 12 输入根 / 13 output leaf / 3 canary leaf 的 ACL 与权限状态 | `UNPROVABLE` | 本轮未放行 `Get-Item`/`Get-Acl`；历史 SDDL 不等于当前或有效访问。 |
| 5 | 当前 TEMP/cache/scratch/protected path 解析（canonical） | `UNPROVABLE` | R0 只有词法 `Path.GetFullPath`，明确“不作为 filesystem canonical identity”。 |
| 6 | 当前 protected-file 基线 hash / R6 完整 `protected-invariants` inventory | `UNPROVABLE` | 仅存在 12 文档 + `.git/index` 的历史有限子集；不构成完整 inventory。 |
| 7 | 当前 WER policy/view/destination 与安全 T0 引导顺序 | `UNPROVABLE` | `wer_view_destination_binding`、`t0_bootstrap_safe_order` 仍 `NOT_RESOLVED / BLOCKED`。 |
| 8 | `private_registry_absence` | `UNPROVABLE` | 保持原值；`WAIVED_BY_OWNER` 不使其成为 PASS。 |
| 9 | 两个已存在 scratch leaf（`gen/schemas`、`permissions/autogenerated`）的 empty-or-absent 条件 | `REQUIRES_ACTIVE_TEST` | 需要另行冻结的动态 inventory/行为检查。 |
| 10 | canary 正/负向写行为、真实 LPAC token 读写边界 | `REQUIRES_ACTIVE_TEST` | 只读 ACL ≠ `AccessCheck`/真实写拒绝结果；R0 明确禁止写试探。 |
| 11 | controller/probe 映像、模块、子进程/broker/COM/WER 短命进程、build descendants 的写入强制闭包 | `REQUIRES_ACTIVE_TEST` | 无动态执行证据；`TerminateJobObject` 不构成回滚或闭包。 |
| 12 | 当前可用 runner 及其上的一切 host getter（identity、`Get-Item`、`Get-Acl`、env/path/hash、Git plumbing 含 scratch `rev-parse`、WER/T0） | `NOT_SAFE_FOR_R0` | launcher/argv/startup/profile/history/wrapper/cache/temp/log/子进程边界均未闭合；Git plumbing 另需 external executable。 |
| 13 | 本轮实际失败项 | `FAILED = ∅` | 本 Task 未执行任何 P02PRE host check；**未执行不等于失败**。 |

分类不变量：目标当前值 = `UNPROVABLE`；查询方法 = `NOT_SAFE_FOR_R0`；二者不得互相升格/降格（manifest §6、Task L41 已正确写入）。

---

## 8. 是否存在可获准执行的最小 host query 子集

**结论：本轮不存在可获准的最小 host query 子集（= 空集）。**

理由（基于被审文档的静态判断，非主机测试）：

1. 唯一可用通道是当前 `exec_command(shell="powershell", login=false)` runner；其 launcher/version/argv/profile/history/wrapper/cache/temp/log/子进程边界在本轮文档中**均未闭合**。用户明确禁止“先启动 runner，再观察”的验证方式，我亦不批准该方法。
2. `login=false`、same-process inline 命令体、getter 名称本身均不构成 invocation 无副作用的证明（manifest L25 已正确写明）。
3. Git plumbing 需要 external executable，`--no-optional-locks` 只抑制 Git optional lock，不构成 helper/config/fsmonitor/submodule 的无副作用保证（R6 L158 同结论）。
4. 即便某个 getter 在方法层面看似只读（例如对冻结绝对路径的 `Get-Item -LiteralPath`/`Get-Acl -LiteralPath`），本轮文档也未提供逐方法的 provider/module-load/类型解析/缓存边界静态证据，仍属用户定义的“安全性不确定 → `NOT_SAFE_FOR_R0`”。
5. 即使 Reviewer 愿意放行，本 Task L39–L42 仍要求 Codex 独立 adjudication；而本 Review 已在 P2-03/P2-04 指出 dispatch 口径与产物语义未闭合，也应在放行前修正。

唯一可设想的解阻方向（**本轮不授权、不执行**）：先冻结**可审查的 runner 合同**（可执行文件身份与 hash、完整 argv、显式 `-NoProfile -NonInteractive`、module analysis/telemetry/history/cache 抑制、明确无子进程与无写入路径），再由非作者 Reviewer 逐项审 getter 边界，最后 Codex adjudication。该方向仍需下一轮用户裁决才会被激活。

---

## 9. Build Barrier 与风险/Gate 状态

本轮 Review **不改变**任何状态：

- `private_registry_absence = UNPROVABLE`（无 PASS）
- Technical Gate = `NOT_SATISFIED`
- Owner Risk Acceptance = `APPROVED`
- Gate Disposition = `WAIVED_BY_OWNER`（唯一豁免仍仅为“创建前 private registry storage absence 无副作用证明”）
- Build Authorization = `AUTHORIZED_WITH_EXCEPTION`（枚举 ≠ Barrier 解除）
- P02PRE = `BLOCKED`；Build Gate = `BLOCKED`；**Hard Build Barrier = `EFFECTIVE`**
- profile = `NOT_CREATED`；ACL/registry = `NOT_MODIFIED`；build/Cargo = `NOT_RUN`；AC1–AC7 = `BLOCKED / NOT_RUN`
- Windows Sandbox：未查询、未安装、未启用、未启动。

---

## 10. 实际 Review 边界（必须与主机证据严格区分）

- 本文件是**静态文档 Review**，不构成任何 host/OS/registry/WER/profile/token/ACL/path/environment/hash 查询结果，不构成 Gate PASS、风险豁免、API 执行许可或 Build Barrier 解除。
- **未**执行 shell/Git/hash/API/registry/WER/profile/token/ACL/path/environment/process 查询；**未**运行代码、构建、Cargo 或 AC1–AC7；**未**修改任何文件，**未**创建任何产物。
- R6 的 `44307 bytes / SHA-256 626E000A…09DE`、R6 Review 的 `23380 bytes / A8C0C124…`、以及 base HEAD/tree 均为**继承引用**，本轮**未复算**（复算需要 hash/Git 查询，已被本轮授权禁止）。
- 未读取 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/tasks/P02.md`、`doc/tasks/README.md`、`dsh-p02pre-r0s6-review-20261011.md`。因此 **AC L38 的治理登记声明、Live Git/branch/tree 与 `.git/index` 现状在本轮为 `NOT_VERIFIED`**，不由本 Review 断言。
- 扩展读取了 `p02-readonly-preflight-r0-evidence-20261011.md`（原因见 §1 第 9 项），以及 4 次只读文件枚举（仅确认路径存在性，不读内容）。除此以外严格限于用户列出的文件。
- Reviewer 独立性声明：本人非 `P02PRE-R0S6.md` 与 `p02pre-r0s6-manifest-20261011.md` 的作者（作者为 Codex）。本人曾出具 R0S5 的 Round 1–3 Review（记录于 R0S5 adjudication L8）；本轮**不重新裁决**自己此前的 R0S5 结论，只审 R0S6 文档对其引用是否忠实。此项也是 P3-03 要求 Task/manifest 显式披露的内容。

---

## 11. 推荐下一步

1. Codex 按 P2-01～P2-04 修正 `doc/tasks/P02PRE-R0S6.md` 与 `verification/P02/p02pre-r0s6-manifest-20261011.md`（纯文档改动，不需 host 查询、不改变冻结范围）；P3 项可选加固。
2. 修正后由 DeepSeek Harness 做一次聚焦复核（仅审 P2 修正与对象绑定），随后由 Codex independent adjudication，并在 delivery 中冻结五态分类（§7 可作为起点，须保留历史证据的时点限定）。
3. **本轮不得**放行任何 getter、runner、profile API、registry/ACL/WER/token/path 查询、build/Cargo 或 AC1–AC7；Build Barrier 保持 `EFFECTIVE`。

**可直接转发给 Codex /root 的下一指令**：

> 请按 `verification/P02/dsh-p02pre-r0s6-review-20261011.md` 中 P2-01～P2-04 修正 `doc/tasks/P02PRE-R0S6.md` 与 `verification/P02/p02pre-r0s6-manifest-20261011.md`：①移除 `p02pre-r0s6-*` 前缀式写入表述或标注其为纯命名约定；②引用 `verification/P02/p02-readonly-preflight-r0-evidence-20261011.md` 的精确路径 + bytes + SHA-256 以绑定 13 项对象集；③补写“DSH dispatch 属治理传输、副作用不作为 R0 证据”条款；④对齐 dispatch 产物清单（补 `stdout.md`、修正 mount 名、规定已存在报告路径的 pin + `CREATE_NEW`/保留语义）。不得执行任何 host query、getter、profile API、build/Cargo 或 AC；保持 `private_registry_absence=UNPROVABLE`、`Gate Disposition=WAIVED_BY_OWNER`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`。修正后先请 DeepSeek Harness 聚焦复核，再由你独立 adjudication。
