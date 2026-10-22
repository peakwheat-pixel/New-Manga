# P02PRE-R0S4 Round 2 独立 Review（非作者 Reviewer：DeepSeek Harness）

## 0. Metadata

| 字段 | 值 |
|---|---|
| Review ID | `P02PRE-R0S4-REVIEW-R2-20261011-DSH-02` |
| 轮次 | Round 2（针对 Round 1 `CHANGES_REQUESTED` 后的修订件） |
| 受审 Task | `doc/tasks/P02PRE-R0S4.md`（`status: in_review`；Owner 声明 7414 bytes / `E466DAB6347CB5D64049D1D270EDC5C6AF44E50CA1E1C390F1FC03CA76E92F4C`） |
| 受审 Manifest | `verification/P02/p02-readonly-preflight-r0s4-manifest-20261011.md`（11747 bytes / `08987CA4C26407CBAD6DD5BA69FA3A0EF842B9BE713E5129CF180C67F21288DC`） |
| 受审 Delivery | `verification/P02/codex-p02pre-r0s4-delivery-20261011.md`（6368 bytes / `BA3CF37516CCB28ACBAC3F9CE1BCCB7671CF1F93BFB39C99662A6A129C7CF05F`） |
| Round 1 报告（冻结） | `verification/P02/dsh-p02pre-r0s4-review-20261011.md`（31986 bytes / `DA84336B6CABC6A2FC7F83EBEDD458CB3C2FFF702C8D012625E72FA8581EED6F`） |
| Round 1 prompt（冻结） | `verification/P02/dsh-p02pre-r0s4-review-20261011.prompt.md`（2850 bytes / `5AF18EC2B153D52B6D0F2D4AB8C74154AF89EE20C1456E9207FD94BCE953D752`） |
| 安全依据（相关段落） | `p02-readonly-preflight-r0s2-review-20261011.md`、`codex-p02pre-r0s2-adjudication-20261011.md`、`codex-p02pre-r0s3-adjudication-20261011.md`、`p02-owner-risk-waiver-execution-manifest-r6-20261011.md`、`p02-readonly-preflight-r0-evidence-20261011.md`、`p02-readonly-preflight-r0s1-evidence-20261011.md` |
| Owner / Author / Integrator / Adjudicator | Codex `/root`（未参与本 Review） |
| Reviewer | DeepSeek Harness（非作者；未编写 Task / manifest / delivery / 任何 r6、R0、R0S1、R0S2、R0S3、R0S4 对象） |
| Repo / branch / 声明基线 | `G:/CODEX/New Manga` / `main` / `cddff58469b56e181019a8ddfeade80684bc7eb9`（tree 声明 `c25d051a4b9a0bd9773b50170e100f575ea19f2b`） |
| 审查方式 | 纯只读文档审查（`read` / `glob` / `grep`）。**未**运行任何 shell、Git、OS/Registry/WER/path/ACL/environment/hash 查询，**未**启动 runner，**未**执行 Build/Cargo/AC，**未**修改除本文件外的任何对象 |
| **Review 决策** | **`APPROVED`** |
| Finding 计数 | **P0=0；P1=0；P2=0；P3=3（均为新观测，非阻断）** |
| Round 1 findings 状态 | P1-01、P2-01…P2-05、P3-01…P3-06 **全部已在工件层面处置**；无未关闭的 P0/P1/P2 |
| Gate 效力 | **无**。不授权执行、不放行 P02PRE / Technical Gate / Build Gate / Hard Build Barrier / AC1–AC7，不改变 Owner waiver |

> **核心判断**：Round 1 的全部 P1/P2 已通过最小文档修订关闭，且修订方向是**信息更完整、边界更保守**，未出现弱化、扩权或 Gate 表述变更。安全停止方向（`STOP_BEFORE_HOST_QUERY`、零 host 查询、不换 shell、不运行 getter）保持正确，应原样保留。仍未关闭的仅是 3 项 P3 文档精化，以及一项**必须在 Codex adjudication 完成的 pin 绑定义务**（属治理前置，不是 Review 缺陷）。

---

## 1. Reviewed paths 与 pins 的独立核验限制（**NOT_VERIFIED**）

### 1.1 Reviewed paths

| # | 路径 | 读取程度 |
|---|---|---|
| 1 | `doc/tasks/P02PRE-R0S4.md` | 全文（86 行；Round 1 为 78 行） |
| 2 | `verification/P02/p02-readonly-preflight-r0s4-manifest-20261011.md` | 全文（71 行；Round 1 为 49 行） |
| 3 | `verification/P02/codex-p02pre-r0s4-delivery-20261011.md` | 全文（45 行；Round 1 为 35 行） |
| 4 | `verification/P02/dsh-p02pre-r0s4-review-20261011.md`（Round 1 报告） | 全文（268 行），用于逐项对照 findings 关闭情况 |
| 5 | `verification/P02/dsh-p02pre-r0s4-review-r2-20261011.prompt.md` | 全文（作为本派发的桌面对应件读取） |
| 6 | `verification/P02/p02-readonly-preflight-r0-evidence-20261011.md` | 定点读取：L8、L29、L123–L137、L231–L233、L249、L258、L265、L272（用于核对历史 PASS_WITH_EVIDENCE 的对象与时点引用是否准确） |
| 7 | `verification/P02/p02-readonly-preflight-r0s1-evidence-20261011.md` | 定点读取：L7–L9（用于排除“13 项 hash”指向歧义） |
| 8 | 安全依据 4 件（r6 manifest、R0S2 Review、R0S2/R0S3 adjudication） | 相关段落（全文已在 Round 1 读取，本轮复核关键行） |

以 `glob verification/P02/*r0s4*` 确认当前 R0S4 对象集：`p02-readonly-preflight-r0s4-manifest-20261011.md`、`codex-p02pre-r0s4-delivery-20261011.md`、`dsh-p02pre-r0s4-review-20261011.md`、`dsh-p02pre-r0s4-review-20261011.prompt.md`、`dsh-p02pre-r0s4-review-r2-20261011.prompt.md`。`codex-p02pre-r0s4-adjudication-20261011.md` 与 `codex-checkpoint-p02pre-r0s4-20261011.md` **仍不存在**（Task L35/L36 已登记路径，属 adjudication 阶段待交付；见新观测 R0S4-R2-P3-03）。

### 1.2 Pins 的核对能力与限制

| Pin 对象 | Owner 声明 | 本 Reviewer 能力 |
|---|---|---|
| Task | 7414 bytes / `E466DAB6…92F4C` | **NOT_VERIFIED**（无法复算） |
| Manifest | 11747 bytes / `08987CA4…1288DC` | **NOT_VERIFIED**（无法复算） |
| Delivery | 6368 bytes / `BA3CF375…7CF05F` | **NOT_VERIFIED**（无法复算） |
| Round 1 报告 | 31986 bytes / `DA84336B…1EED6F` | **NOT_VERIFIED**（无法复算） |
| Round 1 prompt | 2850 bytes / `5AF18EC2…53D752` | **NOT_VERIFIED**（无法复算） |

- 本派发**禁止** shell / Git / OS / path / ACL / environment / hash 查询与 runner 启动，故上述 bytes 与 SHA-256 **一律仅作为 Owner 输入记录**，本文**不声称独立核验**，也**不主张不匹配**。
- 我读取的是工作区当前字节，**不能证明**它与“Codex 复算 pin 时的那份字节”逐字节一致；该绑定只能由 Codex 在 adjudication/checkpoint 中完成（Task L46 已把“Round 2 与最终对象 hashes 绑定”列入 AC）。
- 派发输入的字节与工作区 `*-review-r2-20261011.prompt.md` 文件的一致性同样 **NOT_VERIFIED**。
- 本次 Reviewer 无法自算本报告 digest；须由 Codex 归档时独立复算并绑定（沿 R0S2 adjudication L8 的既有做法）。

### 1.3 未执行（NOT_RUN）声明

任何 shell/进程启动、`git` 任何子命令（含 `status`／`rev-parse`／`rev-parse HEAD^{tree}`／`branch`／`worktree`）、文件 hash、`.git/index` 读取、OS/Registry/WER/profile/token/ACL/path/TEMP/cache/scratch 查询、外部网页抓取、Build/Cargo/AC —— 全部 `NOT_RUN`。本 Review 唯一的写操作是**创建本文** `verification/P02/dsh-p02pre-r0s4-review-r2-20261011.md`。

---

## 2. Round 1 findings 逐项处置核对

### 2.1 P1-01：artifact 级 bytes/SHA pin 绑定

**判定：工件层面已按要求补齐“可绑定”的载体；Exercised 绑定本身属 adjudication 义务，尚未完成（非 Review 缺陷）。**

- Task L46 AC 新增「Reviewer 的所有 P0/P1/P2 findings 已关闭；P3 逐项处置，Round 2 与最终对象 hashes 绑定」；Task L33/L34 登记两轮 Review 与两轮 dispatch prompt 路径；Task L66–L70 新增“Task 文件写入所有权”，明确 Codex 拥有 Task/manifest/delivery/adjudication/checkpoint/两轮 dispatch prompt-log 与治理文件，Round 1 Reviewer 仅写 Round 1 报告、Round 2 Reviewer 仅写 Round 2 报告。
- Delivery L43–L45 新增「非作者 Review Round 1」小节，登记 DSH version=`0.2.0-rc.2`、availability probe `exit=0`、Review session=`session-e11c835e-8ebb-49d7-8d38-47183462779f`、dispatch exit=`0`、Round 1 结论与 P0/P1/P2/P3 计数，并明确“不能将该 Round 1 当作最终 Review”。
- **仍未完成的部分（不构成本轮 finding，但必须执行）**：Task/manifest/delivery 与两轮 Review 的实际 bytes + SHA-256 尚未写入任何版本化对象（工件内仍无 pins 段；adjudication/checkpoint 未创建）。这是 Round 1 建议的“由 Codex 在 adjudication/checkpoint 登记”动作，属 adjudication 阶段职责，因此 **R0S4-P1-01 在“可执行的下一步”层面已关闭，在“绑定已完成”层面仍为待办**。

### 2.2 P2-01：P02PRE host query 与 orchestration Git 命令的区分

**判定：已解决，且披露完整度超过 Round 1 要求。**

- Manifest L61 现在把两类命令**分列**：`P02PRE host/OS/API/Registry/WER/path/ACL/environment/TEMP/cache/scratch/protected-file hash query 命令：NONE；全部 NOT_RUN`，紧接声明“Owner 对零 host query／未启动子进程的声明是自我报告；DeepSeek Review 无法独立验证，Codex adjudication 必须保留 NOT_VERIFIED 限制”。Round 1 的 L42/L45 矛盾已被消除。
- Manifest L62 给出了**实际组合命令的精确文本**：`git rev-parse --show-toplevel; git branch --show-current; git rev-parse HEAD; git rev-parse HEAD^{tree}; git status --porcelain=v2 -z --untracked-files=all --ignore-submodules=all | Measure-Object -Character; git rev-parse --git-common-dir; git worktree list --porcelain | Measure-Object -Line`，并注明 shell=PowerShell、`login=false`。
- Manifest L63 记录了**可见输出**：root=`G:/CODEX/New Manga`、branch=`main`、HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`、status pipeline character count=`35961`、worktree-list line count=`1083`；并如实登记**缺失项**：status 原始输出未存为独立文件、未单独捕获 process exit code 或 stdout/stderr、合并输出含 `git rev-parse HEAD^{tree}` 的 `fatal ambiguous argument` 错误、精确执行时刻不可恢复；末尾明确「不得把上述信息说成完整 Git status manifest」。
- Manifest L64 与 Delivery L17/L19 完整登记：命令未带 `--no-optional-locks`、无紧邻 `.git/index` pre-hash、`index_side_effect=NOT_VERIFIED`、旧 index hash 不补证、未恢复/覆盖/重跑 index。
- Delivery L17 已删除 Round 1 中“未观察到 Git 错误”的不可支撑表述，改为「不能断言‘未观察到 Git 错误’或把 count 当作 status manifest」；Delivery L19 明确「未保存本轮用户未提交文件清单，因此其当前完整性为 NOT_VERIFIED」——Round 1 指出的“用户未提交状态被以含糊措辞放过”的问题已如实披露。
- Delivery L41 明确不以 `index_side_effect` 未验证项宣称 Git gate 通过。

### 2.3 P2-02：`index_side_effect` 入表 + `NOT_VERIFIED` 定性

**判定：已解决。**

- Manifest 五类表新增行 L52：「本轮治理侧普通 git status 的 index side effect 与用户未提交状态完整性 | 组合命令确已执行；但缺紧邻 index pre-hash，且 raw NUL status/stdout/stderr/exit 未留存；不能重跑以追补历史 pre-hash | 已执行，原始完整性记录不足 | **条件状态=UNPROVABLE** | **方法状态=NOT_VERIFIED（审计属性；不是第六类状态）**」。
- Manifest L65 再次单列「P02PRE 的五类表外完整性属性：本轮 Git index side effect 条件=UNPROVABLE；原始记录属性=NOT_VERIFIED；不得将它写为 FAILED」。
- Delivery 表新增行 L30：「本轮普通 git status 的 index side effect 及用户未提交状态完整性 → 条件=`UNPROVABLE`；原始完整性属性为 `index_side_effect=NOT_VERIFIED`；该属性不是第六类枚举」。
- `FAILED` 行（manifest L53、delivery L31）保持 `∅` 且与本行互不混淆。

### 2.4 P2-03：r6 精确对象逐项登记

**判定：已解决。**

Manifest 新增「r6 精确只读候选与状态」表（L17–L27），并在 L15 前置声明「以下仅登记候选对象用于逐项分类；NOT_RUN 不构成当前读取许可或对象存在性结论」。逐项核对（对象名与 r6 逐字比对）：

| 类别 | manifest 位置 | 与 r6 对照 | 状态与边界 |
|---|---|---|---|
| HKLM + HKCU 两个 `LocalDumps` 键 | L21 | = r6 L66 两键 | `NOT_RUN`；仅历史候选、无本轮许可；方法 `NOT_SAFE_FOR_R0` |
| 三个 WER 目录（`%LOCALAPPDATA%\CrashDumps`、`ReportQueue`、`ReportArchive`） | L22 | = r6 L66 三目录 | `NOT_RUN`；第一项不展开环境变量、不读目录内容 |
| 12 个 r6 只读输入根 | L23 | 逐条等于 r6 L74–L85 | `NOT_RUN`；不递归、不读内容、不查有效访问 |
| 13 个 scratch output leaves | L24 | 逐条等于 r6 L123–L135（计数复核=13） | `NOT_RUN`；不读内容、不验 emptiness、不授予写入 |
| 三个 canary leaves | L25 | = r6 L141–L143；含唯一候选文件 `p02-lpac-write-canary-20261010.bin` | 正向 canary 创建**不属于本 Task**；只读 ACL/拒绝检查方法 `NOT_SAFE_FOR_R0` |
| R0 protected-file hash 历史集合 | L26 | = R0 evidence §「固定文件 hash 前/后对照」（L231–L233、L249） | 历史 `PASS_WITH_EVIDENCE`；本轮 `NOT_RUN`、当前值 `UNPROVABLE` |
| 保护/拒绝范围 | L27 | 与 r6 L87 同义（主仓、linked worktrees、其他 clones、host-wide caches、credentials、用户 manga/library、database、Lock、current/pinned Revision、模型、未列 profile/system 路径） | 禁止读写或扫描；不得据此推断当前文件集合 |

Manifest L29 另声明 TEMP/cache 变量只作为未来候选对照、本轮不采集 host environment、不解析未列变量、不调用 API Temp getter。对象边界现已可逐条对账。

### 2.5 P2-04：禁止项覆盖 Task 全部禁项

**判定：已解决。**

Manifest 新增「禁止项与执行记录」小节（L55–L65），逐类覆盖 Round 1 指出的缺口：

- L57：`CreateAppContainerProfile`、`DeleteAppContainerProfile`、任何 profile create/delete/**getter**；Registry write/create/delete/set/flush；ACL/owner/mandatory label 修改；任何文件/目录 create/write/delete/move/overwrite；对 protected path 做写权限测试。
- L58：尚未证明无副作用的 **API/getter/shell/module/provider/external executable/subprocess/runner/wrapper** 或后台 **cache/history/temp/log** 写入；**提权、service/driver/ETW、network/download、compile/JIT**。
- L59：**Windows feature 或 Windows Sandbox 的查询、安装、启用、启动**；**Build/Cargo、AC1–AC7**。
- L60：超出 r6 exact path/key/read allowlist 的访问；读取 **user manga/library、database、Lock、current/pinned Revision、credentials、model 或 dump** 内容。

与 Task L59–L64 的六条禁止项逐条比对，已无遗漏类别。

### 2.6 P2-05 与 P3-01：`NOT_VERIFIED` 与五类状态的关系、方法否决≠条件失败

**判定：已解决。**

- Manifest L69（分类口径总纲）：「五类枚举用于**条件状态和方法可执行性**；`NOT_VERIFIED` 是原始记录/完整性属性，**不是第六种枚举**。方法为 `NOT_SAFE_FOR_R0` 仅表示本轮没有安全执行该方法，**不表示目标条件已经测试失败**；`NOT_RUN`、`UNPROVABLE`、安全停止也均**不等于** `FAILED`。」——同时关闭 P2-05 与 P3-01。
- Manifest L65 与 Delivery L33 提供同口径的重申；新增的 `index_side_effect` 行（L52）自带“审计属性；不是第六类状态”的括注。
- Task L82（原 L74）「FAILED 只用于实际运行失败；未运行、安全停止、对象缺失和方法不安全不得记为 FAILED」保持未变。

### 2.7 P3-02 / P3-03：两个“13”的区分与历史证据精确引用

**判定：已解决，且经我独立定点核对成立。**

- P3-02：manifest L26 写「R0 protected-file hash 历史集合」，L41 写「R0 protected-file hash 13 项」并加限定「13 项是**文档 hash 子集**」；L24 单列「r6 的 13 个 scratch output leaves」；L71 结论段再次明写「R0 protected-file hash 13 项与 r6 scratch output leaf 13 项是不同对象集合」。
- P3-03：manifest L41 给出精确引用——R0 evidence 的 §「固定文件 hash 前/后对照」+ 文件路径 `verification/P02/p02-readonly-preflight-r0-evidence-20261011.md`。
- **我独立定点核对结果（只读文本，未复算 hash）**：该 evidence 的 §「固定文件 hash 前/后对照」位于 L231–L249，L233 表头为“固定对象／查询前 SHA-256／查询后 SHA-256／结论”，L249 记「主要窗口内固定 13 项 hash 全部一致……`.git/index` 前/后值相同」；L29 记「仅固定 13 项文档与 `.git/index`，查询前/后各一次；13/13 hash 一致。**仅为固定文档子集**，不是 r6 完整动态 protected-invariants inventory/hash」；另有 L135 的“13 个 scratch output leaf：11 个 `ABSENT`，2 个 `PRESENT`”，与 manifest 的区分口径一致。故引用准确，非虚指。
- 逐行核对该表（L235–L247）确认“13 项”的精确构成：`AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/STATUS.md`、`doc/09_COLLABORATION.md`、`doc/tasks/P02.md`、`doc/tasks/P02PRE-R0.md`、checkpoint R0、r6 manifest、r6 manifest review、r6 manifest adjudication、M11 报告 = **12 个文档对象**，另加 `.git/index` 共 13 行。这与 R0S1 evidence L29「仅固定 **13 项文档**与 `.git/index`」的措辞存在一处**计数口径差异**（该处把 `.git/index` 也计入“13 项文档”），但 manifest L41 的「R0 protected-file hash 13 项」与表行总数 13 一致，故 manifest 的“13”本身无歧义；上述差异位于上游 R0S1 evidence，属历史文本的轻微不精确，**不构成本轮 finding、不影响本轮结论**。
- 附带排除一处潜在歧义：R0S1 evidence L7–L9 的 pins 是 Task/manifest/checkpoint pin，**不含**任何 13 项 hash 清单；因此 manifest 把“13 项”归于 R0 evidence 是正确的，没有指向 R0S1 的歧义。

### 2.8 P3-05 / P3-06：自我报告限制与静态来源/编排命令清单

**判定：已解决。**

- P3-05：manifest L61 明文「Owner 对零 host query／未启动子进程的声明是自我报告；DeepSeek Review 无法独立验证，Codex adjudication 必须保留 `NOT_VERIFIED` 限制」；Delivery L45 亦记「Reviewer 未运行 shell/Git/host query，未独立复算 artifact pins 或验证零 host query 声明」。Round 1 要求的“不得读成已证明零查询”已被写入正式载体。
- P3-06：Delivery L13 现已列出静态来源清单（`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/09_COLLABORATION.md`、`doc/tasks/P02.md`、`P02PRE-R0.md`、`P02PRE-R0S2.md`、`P02PRE-R0S3.md`、r6 manifest、R0S2/R0S3 adjudication 及 R0/R0S2 证据），并声明「此为编排与文档核对记录，不是宿主状态或 Git gate evidence」；Delivery L17 的编排 Git 命令与本清单的关系已写清（L17 是该次治理侧 Git 命令，L13 是文档核对范围）。

### 2.9 Round 1 P3-04（治理/checkpoint 缺口）

**判定：部分自然推进，剩余属 adjudication 阶段。**

Round 2 Review 与 Round 2 prompt 已在 Task L34 登记且文件已存在；`adjudication` 与 `checkpoint` 仍未创建，`doc/STATUS.md`／`REBASELINE_PLAN.md`／`00_INDEX.md` 尚未登记 R0S4。按 Task L68 的所有权与 L48 AC，这些属集成阶段待办，**不作为本轮 finding**（见 R0S4-R2-P3-03）。

---

## 3. 授权原值、固定英文文本与安全方向复核

| 检查项 | 证据 | 判定 |
|---|---|---|
| 五值风险原值 | Task L22 = manifest L8 = delivery L35，逐字一致：`private_registry_absence=UNPROVABLE`；`Technical Gate=NOT_SATISFIED`；`Owner Risk Acceptance=APPROVED`；`Gate Disposition=WAIVED_BY_OWNER`；`Build Authorization=AUTHORIZED_WITH_EXCEPTION` | 通过 |
| 固定英文原文 | `technical condition unmet; user explicitly accepted residual risk` 在三处**逐字保留**（大小写、分号、无句号），未翻译、未改写、未省略 | 通过 |
| 不是新 waiver / 不是 Gate PASS | Task L22、manifest L7、delivery L9 | 通过（明确否定） |
| 技术状态与风险接受分列 | manifest L8/L9、delivery L35、Task L22/L77 | 通过 |
| 未改变的安全状态 | `P02PRE=BLOCKED`；`profile=NOT_CREATED`；`ACL/registry=NOT_MODIFIED`；`Build Gate=BLOCKED`；`Hard Build Barrier=EFFECTIVE`；`build/Cargo=NOT_RUN`；`AC1–AC7=BLOCKED / NOT_RUN`（Task L77、manifest L9、delivery L39） | 通过 |
| Windows Sandbox | Task L62/L78、manifest L59、delivery L39 | 通过 |
| runtime 声明 | Task L37 = delivery L8：`gpt-6-luna / max`，未使用/未声称 `gpt-6.1-sol / high` | 通过（文本一致） |
| 安全停止方向 | `STOP_BEFORE_HOST_QUERY` 保持（manifest L33–L35）；R0S2 RP-01 仍为硬前置（Task L75）；未换 shell／未换 runtime／未运行 getter（manifest L61、delivery L15） | **通过，应原样保留** |
| 未把历史授权当新授权 | 全链未引用 R6 旧候选字符串或更早裁决作为授权来源；Round 1 的“历史 PASS 不外推”限制在 manifest L26/L41/L71、delivery L25 中保留 | 通过 |
| 历史 PASS_WITH_EVIDENCE 的时点限制 | manifest L41/L44/L45/L71、delivery L25；明确“历史时点、不外推、不是完整 inventory” | 通过 |
| `FAILED` 语义 | manifest L53、delivery L31：`∅`，且“未执行和安全停止不是失败” | 通过 |

**未覆盖风险（保持不变）**：原始用户裁决文本本身不在受审对象内，本轮只能核对二次记录的一致性；Reviewer 无权从聊天或其他用户授权中引入新授权来源。

---

## 4. 新观测（Round 2 P3，均非阻断）

| ID | 级别 | 对象 / 证据 | 影响 | 建议（最小、可在 adjudication/checkpoint 顺带完成） |
|---|---|---|---|---|
| **R0S4-R2-P3-01** | P3 | manifest L62 记录的实际 status 为 `git status --porcelain=v2 -z --untracked-files=all --ignore-submodules=all`；r6 L158 冻结的未来采集命令为 `--ignore-submodules=none`；manifest L63/L64 已披露输出未留存与 index 未证，但未指出该参数偏差及其方向 | 本轮无 Raw status 可作 P02 证据，故**无实际 Gate 后果**；但该命令若被后续轮次当作“已按 r6 冻结参数执行”的先例引用，会削弱“受保护状态投影必须完整”的口径 | 在 manifest L62/L64 加一句：实际命令相对 r6 L158 的 `--ignore-submodules` 取值不同（`all` 会忽略子模块变更），该差异是**更窄**的观测，不得视为满足 r6 的 status 采集契约 |
| **R0S4-R2-P3-02** | P3 | manifest L62 的管道 `... | Measure-Object -Character`；L63「未单独捕获 process exit code 或 stdout/stderr」 | 组合命令经 PowerShell 输出流合并后只保留字符计数，因此 `35961` 不能被解读为干净 stdout 的字节/字符数；现有措辞已否定“完整 manifest”，但未点明流合并机制 | 补一句“PowerShell 管道合并输出流的计数，不构成 stdout/NUL bytes 或 status 记录数”，进一步封堵误读 |
| **R0S4-R2-P3-03** | P3 | `glob verification/P02/*r0s4*`：`codex-p02pre-r0s4-adjudication-20261011.md` 与 `codex-checkpoint-p02pre-r0s4-20261011.md` 仍不存在；Task L46 AC 未勾选 | 属 `in_review` 阶段的预期缺口，但不完成则 Task 无法进入 done，且 pins 绑定（P1-01 的收敛动作）无处落档 | 由 Codex 在 adjudication 中登记 Task/manifest/delivery/Round 1 报告/Round 1 prompt/Round 2 报告/Round 2 prompt 的 bytes+SHA-256，并在 checkpoint 保留 `index_side_effect=NOT_VERIFIED` 与“零 host query 为自我报告”限制 |

对 R0S4-R2-P3-01 的补充判断：该偏差**不改变**本轮结论。原因是本轮 `status` 自始不被接受为 P02PRE 或 Git gate 证据（manifest L63/L64、delivery L17/L19/L41 三处均如此声明），且 `--ignore-submodules=all` 只可能使观测**更窄**（漏看子模块变更）而非引入虚假内容；因此它是“记录精度”问题，不是“证据被夸大”问题。

---

## 5. 覆盖与未覆盖风险

### 5.1 已覆盖（本轮已核）

- Round 1 全部 findings（P1-01、P2-01…P2-05、P3-01…P3-06）逐条对照修订件的处置位置与文字。
- 授权原值五值 + 固定英文原文的逐字比对（Task / manifest / delivery / r6 / R0S2 / R0S3）。
- `STOP_BEFORE_HOST_QUERY` 的触发链条（R0S2 RP-01 → Task L75 → manifest L33–L35 → delivery L15），以及“未换 shell、未运行 getter”的记录一致性。
- r6 已列对象的逐项落表核对：两 Registry 键、三个 WER 目录、12 个只读输入根、13 个 scratch output leaves、三个 canary leaves、R0 protected-file hash 历史集合、保护/拒绝范围（对象名与 r6 原文逐字比对）。
- Task L59–L64 禁项与 manifest L57–L60 的逐类映射。
- `index_side_effect` 在五类表中的条件=`UNPROVABLE` / 属性=`NOT_VERIFIED` 分列，以及 `FAILED=∅` 的独立性。
- 历史 `PASS_WITH_EVIDENCE` 的时点与对象限制，并经 R0 evidence L231–L249、L29、L135 定点核对引用真实性。
- 用户未提交状态完整性缺口已改记为 `NOT_VERIFIED`（delivery L19），不再以“未观察到错误”带过。

### 5.2 未覆盖 / 未核验（NOT_VERIFIED / NOT_RUN）

| # | 项 | 状态 | 原因 |
|---|---|---|---|
| 1 | Task / manifest / delivery / Round 1 报告 / Round 1 prompt 的 bytes 与 SHA-256 复算 | `NOT_VERIFIED` | 派发禁止 hash/OS/path 查询 |
| 2 | live HEAD / tree / branch / 工作树独立核验 | `NOT_VERIFIED` | 禁止运行 Git；仅确认各文档**文本**基线声明一致 |
| 3 | “零 host query / 未启动子进程 / 未换 shell”的真实性 | `NOT_VERIFIED`（不可验证） | 验证手段本身被禁止（manifest L61 已如实登记） |
| 4 | 该组合 Git 命令的 exit code、stdout/stderr 分流内容、status NUL bytes、精确执行时刻 | `NOT_VERIFIED`（不可追补） | 原始记录未留存（manifest L63） |
| 5 | 用户未提交文件清单与其当前完整性 | `NOT_VERIFIED` | 未保存 status 输出，且禁止读取 `.git/index` |
| 6 | 上游 r6 / R0 evidence / R0S1 evidence / R0S2 / R0S3 对象的 bytes 与 SHA 复算 | `NOT_VERIFIED` | 仅核文本引用一致性 |
| 7 | 派发输入与工作区 prompt 文件的字节一致性 | `NOT_VERIFIED` | 无法证明链路一致 |
| 8 | Microsoft 官方文档原文 | `NOT_FETCHED` | 保持零外部访问，按 r6 引用采用 |
| 9 | 任何 P02PRE host/Registry/WER/path/ACL/environment/hash 状态 | `NOT_RUN`（按设计） | 本轮安全停止，且属禁止范围 |

### 5.3 剩余风险（不因 Round 2 Approve 而消除）

- **private registry technical condition 仍未满足**：`private_registry_absence=UNPROVABLE` 不变；Owner 风险接受只是风险接受，本轮未产生任何技术证据。
- **runner 缺口未解**：`functions.exec_command` / PowerShell 启动、profile、module analysis cache、PSReadLine history、wrapper 与临时文件的副作用边界仍无新证据；在出现新的精确绑定且经独立 Review 的 runner 之前，任何 host 查询仍禁止。
- **索引与用户未提交状态完整性缺口**：`index_side_effect=NOT_VERIFIED`、无紧邻 pre-hash，**不可追补**；用户未提交清单 `NOT_VERIFIED`。
- **绑定尚未落档**：在 adjudication/checkpoint 完成 pins 绑定前，本轮“被审字节 = 被语义审查字节”的链条仍只有 Owner 声明支撑。

---

## 6. 结论与建议的下一动作

**Round 2 Review 决策：`APPROVED`。**

- **未关闭 findings**：**无**。Round 1 的 P1-01 与 P2-01…P2-05 已在工件层面得到实质处置（P1-01 的“绑定动作”按 Round 1 建议本就归属 Codex adjudication，Task L46 已将其列为 AC）；P3-01…P3-06 全部处置完毕，其中 P3-02/P3-03 经我定点比对 R0 evidence 成立。
- **新 findings**：R0S4-R2-P3-01、R0S4-R2-P3-02、R0S4-R2-P3-03，均为 P3、均可由 Codex 在 adjudication/checkpoint 顺带更正，**不要求第三轮 Review**。
- **最终计数**：P0=0；P1=0；P2=0；P3=3（新增）；Round 1 遗留未关闭 = 0。
- **安全方向确认保留**：`STOP_BEFORE_HOST_QUERY` 正确且必要；无需换 shell、无需重跑、无需以任何查询补证。`private_registry_absence=UNPROVABLE`、`Technical Gate=NOT_SATISFIED`、`Owner Risk Acceptance=APPROVED`、`Gate Disposition=WAIVED_BY_OWNER`、`Build Authorization=AUTHORIZED_WITH_EXCEPTION`、`technical condition unmet; user explicitly accepted residual risk`、`P02PRE=BLOCKED`、`Build Gate=BLOCKED`、`Hard Build Barrier=EFFECTIVE`、`build/Cargo=NOT_RUN`、`AC1–AC7=BLOCKED / NOT_RUN` 全部保持。本 Review **不**授权执行、**不**放行任何 Gate、**不**代替 Codex adjudication、**不**改变 waiver。
- **建议的下一动作（唯一）**：由 `Codex /root` 执行 P02PRE-R0S4 的独立 adjudication，并在同一交付中：①登记 Task、manifest、delivery、Round 1 报告、Round 1 prompt 与本 Round 2 报告/ prompt 的 bytes + SHA-256（与其复算值对账）；②处置 R0S4-R2-P3-01/02（`--ignore-submodules` 参数偏差与流合并计数定性）；③在 checkpoint 保留 `index_side_effect=NOT_VERIFIED`、“零 host query = 自我报告、不可独立验证”与用户未提交清单 `NOT_VERIFIED` 三项限制；④补齐 STATUS／REBASELINE_PLAN／00_INDEX 的 R0S4 登记。期间**不得**派发任何 host/Registry/WER/path/ACL/hash 查询，**不得**换 shell 或运行 getter，**不得**创建 profile，**不得**查询/安装/启用/启动 Windows Sandbox，**不得**触碰 Build/Cargo 与 AC1–AC7。

---

## 7. Reviewer 未核验声明与自身副作用

- **Reviewer 自身副作用 = ZERO（除本文件外）**：未启动任何进程或 shell，未运行任何 `git` 子命令，未调用任何 OS/API/Registry/WER/profile/token/path/environment/ACL/hash 查询，未复算任何 bytes/SHA-256，未读取 `.git/index`，未抓取外部网页，未修改、覆盖、删除或移动任何既有文件（Round 1 报告保持原样）。唯一写入为**创建** `verification/P02/dsh-p02pre-r0s4-review-r2-20261011.md`。
- 本轮 Owner 提供的 5 个对象的 bytes/SHA-256 **仅作为输入记录**；我**未**独立复算，也未据此声称已核验，一律记 `NOT_VERIFIED`。
- 我**未**独立核验 HEAD/tree/branch、任一转述 pin、该组合 Git 命令的副作用与输出、用户未提交状态完整性、以及“零 host 查询”声明；上述各项一律标 `NOT_VERIFIED` / `NOT_RUN`，不作推测。
- 本 Review **不**改变 private-registry waiver、Technical Gate、P02PRE 总体状态、Hard Build Barrier、Build Gate、build/Cargo 或 AC1–AC7；**不**授权执行；**不**代替 Codex adjudication；**不**把历史或聊天中的其他授权当作新的授权来源。
- 本文件的 bytes/SHA-256 由 Codex 在归档/绑定阶段独立复算；Reviewer 无法自算，故不在本文件内声明自身 digest。
