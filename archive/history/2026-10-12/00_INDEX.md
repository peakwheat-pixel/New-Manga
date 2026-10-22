# 项目文档索引与 Source of Truth

> Agent 默认读取顺序见 [AGENTS.md](../AGENTS.md)。本索引只解析当前文档分类与恢复指针；历史快照不决定授权。目录分类和 workspace / archive 规则见[工作区治理规则](WORKSPACE_GOVERNANCE.md)。

## 架构文档索引

| 文档 | 分类 | 当前用途 |
|---|---|---|
| [AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md) | `CURRENT` | 唯一目标架构：Windows + React + TypeScript + Tauri/Rust + Python Core + SQLite + Managed Copy。 |
| [01 功能架构](01_FUNCTIONAL_ARCHITECTURE.md)、[04 用户流程](04_USER_FLOW.md) | `CURRENT_REQUIREMENT` | 产品功能/流程意图；不指定桌面技术栈。 |
| [02 技术架构](02_TECHNICAL_ARCHITECTURE_.md)、[05 UI 映射](05_UI_MAPPING.md)、[11 架构地图](11_ARCHITECTURE_MAPS.md) | `LEGACY` / `HISTORICAL` | PySide6/QML 旧生产基线与旧代码地图，仅作迁移参考。 |
| [07 非功能需求](07_NON_FUNCTIONAL_REQUIREMENTS.md)、[08 验收标准](08_ACCEPTANCE_CRITERIA.md) | `MIXED_REQUIREMENTS / LEGACY_TECH_MAPPING` | 产品级要求保留；技术专属旧实现与 Gate 为历史。新架构 Task/contract 映射验收，不继承旧结果。 |
| [13 验收追踪](13_ACCEPTANCE_TRACEABILITY.md) | `HISTORICAL / LEGACY TRACEABILITY` | 保留旧编号、固定 reviewed head 和当时证据映射；产品要求不因旧映射失效，新架构须另建验证证据。 |
| [10 初始接管快照](10_CURRENT_STATE_AND_GAPS.md)、[12 Roadmap](12_ROADMAP.md)、[14 接管验证](14_TAKEOVER_VERIFICATION.md) | `HISTORICAL / NAVIGATION` | 仅作历史索引；当前计划与状态分别看 REBASELINE_PLAN、STATUS。 |

分类规则与工作区/归档路径见[工作区治理规则](WORKSPACE_GOVERNANCE.md)。

## 治理指针（按需读取）

- [Worktree Safety Inventory](WORKTREE_SAFETY_INVENTORY.md)：删除 worktree 或运行 `git worktree prune` 前必读。
- [2026-10-12 Cleanup Manifest](../verification/PROJECT-GOVERNANCE-20261012/cleanup-manifest.md) 与[366 条 worktree 盘点](../verification/PROJECT-GOVERNANCE-20261012/worktree-inventory.md)：本轮治理证据；不作为当前产品 Task 或架构授权。

## 2026-10-12 当前状态与恢复指针：H1 P2-1 仍 OPEN；ZCode 证据闭合 Task 已阻塞

当前阻塞中的 Task=`tasks/P02PRE-R1H-R6-ZCODE-H1.md`，状态=`in_review / DSH_REVIEW_CHANGES_REQUESTED`；Owner/Coordinator=`Codex /root`；Reviewer=`DeepSeek Harness`，session=`session-2e6e238c-1814-40b9-b0c6-b253f102296a`，verdict=`CHANGES_REQUESTED (0/0/1/6)`；Adjudicator=`Codex /root`。ZCode 已执行 P2-1 closure Task：CLI session=`sess_c297a288-813f-4dfa-92f1-bae7d37d05b8`，内置 Agent session=`agent_8886fd38-6ba0-41d4-a084-6ee8cf40dc8d`，最终=`blocked / P2-1 OPEN`。Codex 独立复核 15 项输入 pins 与两个 status span 重建；2 项部分候选可定位，13 项仍无合格 raw source，因此 H1 review acceptance 与 X6 继续 blocked。当前 checkpoint=`../verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt6-zcode-handoff-20261012.md`。

无 READY 子 Task。P2-1 Task=`tasks/P02PRE-R1H-P2-1-EVIDENCE-CLOSURE.md`，状态=`blocked / EXECUTED_20261012 / BLOCKED_P2_1_OPEN`；Owner=ZCode，branch=`agent/zcode/P02PRE-R1H-P2-1-EVIDENCE-CLOSURE` @ `343895fb5f0329c0c07a7104ec321b698f967607`，worktree=`C:\Users\49745\.codex\worktrees\p2-p2-1-zcode\New Manga`。报告=`C:\Users\49745\.codex\worktrees\p2-p2-1-zcode\New Manga\verification\P02\zcode-p02pre-r1h-p2-1-evidence-closure-report-20261012.md`（27065 / `DA3C419658AE6FD8FB42A93488666A622FF80DAAD5A565A5E92E0B2615C6AE43`）；Handoff=`...\zcode-p02pre-r1h-p2-1-evidence-closure-handoff-20261012.md`。若继续追查仓库外 CLI harness forensic 输出，需先由用户授权扩大只读范围；X6 不创建。

H1 v2=`PRE_RUN_PASS`（24 checks：23 PASS、1 NOT_VERIFIED，后者为按设计未访问的 `.tmp.driveupload` scope）；attempt1 四文件 pins 与 v2 JSON 引用均匹配，protected file 前后 hash 一致。Live=`main@343895fb5f0329c0c07a7104ec321b698f967607` / tree=`e12bd627c307d4bf3c851dc09d0b82f97c86ec63`，index SHA=`C5CA88842173A8FE4B9C6B6B675528347EECBDC73F85600ABA06F11E3A692B68`；固定 Git 2.52.0.windows.1，受控 status=`1237 NUL / 85373 bytes / D3042D8DE60C33C23B950ABB8B8FD26E6CF8F2A5AAFBF76E0EE12B0793026100`（2026-10-12T13:31:59Z，排除 path 未访问）。较上一 Codex 样本 `1227 / 84670 / EC915022…` 多 10 个本轮 ZCode CLI dispatch 日志；更早历史差异仍 `UNKNOWN / NOT_VERIFIED`，详见 `STATUS.md` 与 H1 Task。

DSH CLI=`0.2.0-rc.2`，无附件探测回答“收到”、exit=0；正式 Review exit=0，报告 SHA-256=`6AAD7750AFABCCD5B159C69F40EF49149E3D3EBB1CA6613CD0FD91FDCB960C19`。Codex verification SHA-256=`7B823A05313DA2B053C76B81744667BF041B8FD9AF0933F1162DCDADFB372515`；adjudication SHA-256=`9D4B95DA5263B0C52A3621748E875760CAAADF153ED5C39BDA5955520DF57232`。ZCode P2-1 报告确认 13 项 raw source 缺失，DSH focused Review=`BLOCKED / NOT_DISPATCHED`；Codex 接受整体 `BLOCKED / P2-1 OPEN`，两项 status span 只作为部分候选。X6 Task not created. Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`。Gate 原值与 waiver 未变。

### 历史索引快照：ZCode handoff 前 H1 接手包 READY（已由上方取代）

唯一待接手 Task=P02PRE-R1H-R6-ZCODE-H1，status=ready / AWAITING_ZCODE_CONVERSATION。ZCode 对话统筹，通过内置 Agent dispatch 调用 Codex 执行、DeepSeek Harness 独立 Review、不同的 Codex Agent adjudicate；尚未创建 ZCode session 或派发 Agent。交接说明=../verification/P02/zcode-p02pre-r1h-round6-attempt6-handoff-20261012.md；可直接粘贴提示词=../verification/P02/zcode-p02pre-r1h-round6-attempt6-resume-prompt-20261012.md；当前 checkpoint=../verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt6-zcode-handoff-20261012.md。

冻结上游 A6 Task=tasks/P02PRE-R1H-R6-EXEC-A6.md；DSH R2 与 Codex adjudication 已完成，无未解决 P0/P1/P2；Codex Parser/selfcheck=PASS_WITH_EVIDENCE（0 Parser errors、73 assertions）。final pre-run=PRE_RUN_NOT_VERIFIED：上一轮输出被截断，四个作者目标与七个 Review/adjudication 目标当前 absent/unignored。H1 禁止执行器与任何 profile/registry/ACL 写操作；后续 X6 必须单独 Task，Build Gate 仍 BLOCKED。

Live=main@343895fb5f0329c0c07a7104ec321b698f967607 / tree=e12bd627c307d4bf3c851dc09d0b82f97c86ec63；handoff 写入前 status=1129 NUL / 78702 bytes，文档完成后=1133 NUL / 78983 bytes / D06C76A33DA159D6A03539F432AED35A1D2383C004463C799BC3DC6FCE0F9550。ZCode 接手时必须重核 Live Git。Gate 维持 UNPROVABLE / NOT_SATISFIED / APPROVED / WAIVED_BY_OWNER / AUTHORIZED_WITH_EXCEPTION；Windows Sandbox 不触碰；不关机。

### 历史索引快照：A6 Parser/selfcheck 完成；final pre-run ACTIVE（已由上方取代）

P02 当前 Active Task=`P02PRE-R1H-R6-EXEC-A6`，状态=`in_progress / CODEX_FINAL_PRE_RUN_ACTIVE`；代码 Owner=Antigravity、非作者 Reviewer=DeepSeek Harness、Integrator/Adjudicator=Codex `/root`。ZCode 不承担当前 Task。DSH R2=`APPROVED_STATIC_CONTENT`、Codex adjudication=`ACCEPTED_STATIC_CONTENT_WITH_LIMITATIONS`，无阻塞 P0/P1/P2；Codex Parser/selfcheck=`PASS_WITH_EVIDENCE`（0 Parser errors、73 assertions）。当前只读 final pre-run 尚未判定；A6 Task 禁止调用 executor，后续 X6 必须单独释放。

唯一 DAG=`REBASELINE_PLAN.md`；唯一运行状态=`STATUS.md`；Task=`tasks/P02PRE-R1H-R6-EXEC-A6.md`；恢复点=`../verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt6-parser-pass-20261012.md`。Review adjudication=`../verification/P02/codex-p02pre-r1h-attempt6-r2-review-adjudication-20261012.md`；Parser/selfcheck evidence=`../verification/P02/codex-p02pre-r1h-attempt6-integration-verify-20261012.json`。Live=`main@343895fb5f0329c0c07a7104ec321b698f967607` / tree=`e12bd627c307d4bf3c851dc09d0b82f97c86ec63`；既有未提交工作区内容保留。

Gate 保持 `UNPROVABLE / NOT_SATISFIED / APPROVED / WAIVED_BY_OWNER / AUTHORIZED_WITH_EXCEPTION`；Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`。Windows Sandbox 不触碰；不关机。

### 历史索引快照：ZCode 派发失败后等待外部派发（已由上方取代）

P02 当前 Owner=ZCode；唯一 READY 子 Task=P02PRE-R1H-R6-EXEC-A6，dispatch state=AWAITING_EXTERNAL_DISPATCH；非作者 Reviewer=DeepSeek Harness，Integrator/Adjudicator=Codex /root。Task=tasks/P02PRE-R1H-R6-EXEC-A6.md；唯一 DAG=REBASELINE_PLAN.md；运行状态=STATUS.md；滚动恢复点=../verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt6-zcode-dispatch-20261012.md。

A5 final pre-run=PRE_RUN_BLOCKED / OWNER_HANDOFF_PIN_MISMATCH；A5 executor=NOT_RUN。独立 DSH Review=CHANGES_REQUESTED (0/2/3/4)，Codex adjudication 已完成。P02 中仍开放的 Antigravity 父 Task 已转给 ZCode；closed/done 的 R1G/A4 历史 Owner 不改写。

ZCode branch=agent/zcode/P02PRE-R1H-R6-EXEC-A6，worktree=C:\Users\49745\.codex\worktrees\p02pre-r1h-attempt6-zcode\New Manga，base=343895fb5f0329c0c07a7104ec321b698f967607。CLI dispatch exit=1，provider config 缺失且未启动 Agent session；记录=../verification/P02/zcode-p02pre-r1h-exec-a6-dispatch-20261012.md。A6 只负责新 attempt6 executor/protocol/Handoff；独立 Review 和 Codex adjudication、PS7 Parser/纯内存验证、final pre-run 及单次执行仍是后续独立 Gate。

Gate 保持 UNPROVABLE / NOT_SATISFIED / APPROVED / WAIVED_BY_OWNER / AUTHORIZED_WITH_EXCEPTION；Build Gate=BLOCKED、Hard Build Barrier=EFFECTIVE、Build/Cargo=NOT_RUN、AC1–AC7=BLOCKED / NOT_RUN。持续授权不是测试或 Gate PASS；Windows Sandbox 不触碰；不关机。

### 历史索引快照：attempt5 baseline repair ACTIVE（已由上方取代）

当前唯一 Active 产品 Task=`P02PRE-R1H`，当前子 Task=`P02PRE-R1H-R6-EXEC-A5`（Codex Owner / DeepSeek Harness 非作者 Reviewer / Codex Integrator）。唯一任务图见 [`REBASELINE_PLAN`](REBASELINE_PLAN.md)；运行状态见 [`STATUS`](STATUS.md)；当前 Task=`[EXEC-A5](tasks/P02PRE-R1H-R6-EXEC-A5.md)`。

- A4 owner=`Antigravity`，最终 HEAD=`c7c7879e8ae90ad23b29d9d8cc6ea97e3eff5427`；DSH=`APPROVED_STATIC_CONTENT (0/0/0/4)`；16/16 pins 匹配；Codex adjudication 接受内容结论并记录方法偏差。
- A4 精确集成 commit=`343895fb5f0329c0c07a7104ec321b698f967607`。Codex integration verify=`PASS_WITH_EVIDENCE`：PS7.6.6 parser 零错误，纯内存 selfcheck 73 assertions PASS，受控 diff hygiene PASS；未调用 executor、Replace、OS/API、Build/Cargo 或系统 AC。
- attempt4 final pre-run 被 frozen ref/index mismatch 阻止，`P02PRE-R1H-R6-EXEC-A4`=`BLOCKED / NOT_RUN`；细节与 recovery=`../verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt4-baseline-blocked-20261012.md`。A5 只修复新的冻结基线，经非作者 Review/adjudication 后继续。
- Live=`main@343895fb5f0329c0c07a7104ec321b698f967607` / tree=`e12bd627c307d4bf3c851dc09d0b82f97c86ec63`；受控 status=`1057 NUL / 72007 bytes / SHA-256 A4DBE55D880A0B0EE62551C1254A19918C7CC0F1E9ABAE4515A86EA970F0E534`，index SHA=`C5CA88842173A8FE4B9C6B6B675528347EECBDC73F85600ABA06F11E3A692B68`。状态来源见 `STATUS`。
- Gate 保持 `UNPROVABLE / NOT_SATISFIED / APPROVED / WAIVED_BY_OWNER / AUTHORIZED_WITH_EXCEPTION`；Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`。Windows Sandbox 不触碰；用户已取消完成后关机。

### 历史索引快照：attempt4 精确集成 ACTIVE（已由上方取代）

## 2026-10-12 历史状态与恢复指针：attempt4 精确集成 ACTIVE

用户已撤销任务完成后关机的要求；任务结束不关机。用户此前持续授权仍有效，但不自动构成测试或 Gate PASS。Windows Sandbox 不查询/安装/启用/启动。

- 唯一任务 DAG：[`REBASELINE_PLAN.md`](REBASELINE_PLAN.md)，含中文 Mermaid 图。
- 当前唯一 Active 产品 Task：[`P02PRE-R1H`](tasks/P02PRE-R1H.md)；活动子 Task：[`P02PRE-R1H-R6-A4`](tasks/P02PRE-R1H-R6-A4.md)，独立 Review 已通过并由 Codex adjudicate，Task=`approved`，Codex 集成 ACTIVE。
- attempt3 独立 Review=`CHANGES_REQUESTED`，Codex adjudication 已完成：[`adjudication`](../verification/P02/p02pre-r1h-integration-protocol-review-adjudication-round6-attempt3-20261012.md)。
- attempt4 Owner=`Antigravity`，Reviewer=`DeepSeek Harness`，Integrator/Adjudicator=`Codex`；Owner final HEAD=`c7c7879e8ae90ad23b29d9d8cc6ea97e3eff5427`，tree=`e12bd627c307d4bf3c851dc09d0b82f97c86ec63`，fixed worktree=`C:/Users/49745/.codex/worktrees/p02pre-r1h-r6-attempt4-antigravity`。
- DSH=`APPROVED_STATIC_CONTENT`（0/0/0/4）；Codex pre/post pins=`16/16 MATCH`。Codex adjudication 记录四次只读 grep 方法偏差及非阻断 P3：[`attempt4 adjudication`](../verification/P02/p02pre-r1h-attempt4-review-adjudication-20261012.md)。Review report SHA-256=`8F124B4C5A404AEED295CE3FE599738A14C4386780466A963F021B88E68274A3`。
- 当前恢复点：[`attempt4 rolling checkpoint`](../verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt4-owner-active-20261012.md)。
- Gate 保持：`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner waiver=`APPROVED / WAIVED_BY_OWNER`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`；Build/Cargo 与系统 AC1–AC7=`NOT_RUN`。
- 精确集成与 Codex PS7.6.6 parser/selfcheck 复跑尚待完成；attempt4 executor、Replace、OS/API、Build/Cargo、system AC 均未运行。
### 历史索引快照：Round6执行器修正 ACTIVE（已由上方取代）

Active Task=P02PRE-R1H；阶段=R6_EXECUTOR_REMEDIATION / ACTIVE。协议attempt2静态Review与Codex adjudication已完成；执行前编排检查两次均未写入集成文件，原因与证据边界见Task。Round6 selfcheck仍NOT_RUN；Round5 AC2真实FAILED保留。Reviewer=/root/p02_r1h_remediation_review；Integrator=/root。

唯一DAG=REBASELINE_PLAN.md；Task=tasks/P02PRE-R1H.md；manifest=../verification/P02/p02pre-r1h-manifest-20261012.md。协议attempt2报告=../verification/P02/codex-subagent-p02pre-r1h-integration-protocol-review-round6-attempt2-20261012.md；Codex裁决=../verification/P02/p02pre-r1h-integration-protocol-review-adjudication-round6-attempt2-20261012.md。当前checkpoint=../verification/P02/codex-checkpoint-p02pre-r1h-round6-executor-remediation-active-20261012.md。Live main=cddff58469b56e181019a8ddfeade80684bc7eb9。Gate原值见STATUS.md。Windows Sandbox不触碰；用户授权全部任务完成后关机，当前不关机。

### 历史索引快照：Round6 Review pins重建 ACTIVE（已由上方取代）

## 2026-10-12 历史状态与恢复指针：Round5 已集成；Round6 Review pins重建 ACTIVE

Active Task=`P02PRE-R1H`。Round5 static code Review=`APPROVED_STATIC_CONTENT`；integration protocol Review R2=`APPROVED_STATIC_PROTOCOL`；单次Replace=`PASS_WITH_EVIDENCE`。Round5 parser=`PASS`、selfcheck/AC2=`FAILED`、engine preflight=`PASS`、AC4=`BLOCKED_BY_AC2`。Round6 Owner delivery=`c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d`。Review attempt1因派发后Task pin漂移=`BLOCKED_BY_MISSING_EVIDENCE`；attempt2初始pins文件生成错误为JSON `null`，未派发并已保留。当前重建有效pins后再Review。Owner=`/root/p02_r1h_codex_owner`，Reviewer=`/root/p02_r1h_remediation_review`，Integrator=`/root`。

唯一DAG=`REBASELINE_PLAN.md`；Task=`tasks/P02PRE-R1H.md`；manifest=`../verification/P02/p02pre-r1h-manifest-20261012.md`；Round5 execution/failure evidence保留；Review attempt1 prompt/pins/report保留；无效attempt2 r2 pins/prompt保留；有效attempt2 r3 pins/prompt待生成；latest checkpoint=`../verification/P02/codex-checkpoint-p02pre-r1h-round6-review-r3-freeze-active-20261012.md`。

Round5 execution boundary S3=`989 records / 66127 bytes / SHA-256 0E34A1B0A609F2771EE25CA74A3B88287F2C4410F816F4F17DB691053B02378A`；此为历史验证快照。当前Round6状态及新增审查/失败生成证据见最新checkpoint。Git status使用受控NUL porcelain-v2，独立包含`:(exclude).tmp.driveupload`，exit=0/stderr=0。main HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9` / tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；index SHA-256=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`。Gate原值见`STATUS.md`；Windows Sandbox不触碰。

## 2026-10-11 历史状态与恢复指针：R1F capture fail-stop；follow-up #4 ACTIVE（已由上方取代）

## 2026-10-11 历史状态与恢复指针：R1F capture fail-stop；follow-up #4 ACTIVE（已由上方取代）

P02 是唯一 Active 产品 Task；当前 Active 子 Task=`P02PRE-R1F`，步骤=`R1G manifest 历史 pin 文案修复 / DSH follow-up #4 独立复审`。R1F one-shot 已执行并在 Windows PowerShell 5.1 `Get-FileHash` prehash command resolution 处 fail-stop，exit=1；不得重跑。post-run Review=`CHANGES_REQUESTED (0/0/2/2)`；文档 follow-up #2=`CHANGES_REQUESTED (0/0/0/1)`，Codex 已接受其唯一 P3 并修复历史 pin 标签；follow-up #3=`DISPATCH_TIMEOUT / NOT_A_REVIEW`，无报告/裁决且旧 session 不复用。原 finding dispositions 见 [`R1F adjudication`](../verification/P02/p02pre-r1f-postrun-adjudication-20261011.md)、follow-up #2 adjudication 和 #3 failure record。`P02PRE-R1G`=`READY`，依赖 R1F 收口，Owner=Antigravity、Reviewer=DeepSeek Harness；R1G 选定 PowerShell 7.6.6 并将 command/module capability preflight 置于 capture 前，能力仍未验证。

唯一 DAG=`REBASELINE_PLAN.md`；R1F Task=`tasks/P02PRE-R1F.md`；R1G Task=`tasks/P02PRE-R1G.md`；当前 recovery point=`../verification/P02/codex-checkpoint-p02pre-r1f-postrun-20261011.md`。Live HEAD=`main@cddff58469b56e181019a8ddfeade80684bc7eb9` / tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；当前受控 status=`820 NUL / 53254 bytes / 436EE5F37E78A514309CEFBD33FF7CAD244A8A3C884E79C9C39919CCF6FE537F`，exit=0/stderr=0，pathspec 排除 `.tmp.driveupload`。与前一有效 checkpoint 相比 `+101 records / +5975 bytes`；较 818 快照新加 #3 failure record 和 #4 prompt placeholder；更早快照的文件级归因仍按 Plan 标为未知。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`；准确风险裁决见 [`STATUS`](STATUS.md)。

## 2026-10-11 历史状态与恢复指针：P02PRE-R1F cohort #11 已 adjudicate；final pre-run ACTIVE（已由上方取代）

P02 是唯一 Active 产品 Task，当前 Active 子 Task=`P02PRE-R1F`，步骤=`final pre-run ACTIVE`。cohort #8/fixreview7=`NOT_DISPATCHED / NOT_REVIEWED`；#9/fixreview8=`CHANGES_REQUESTED (0/1/1/1)`，F8-1–F8-4 已 adjudicate；#10/fixreview9=`CHANGES_REQUESTED (0/0/0/1)`，F9-1 已修复且原 verdict 保留；#11/fixreview10=`APPROVED (0/0/0/0)`，Codex 已 adjudicate 且 15/15 frozen source pins 匹配。Reviewer sandbox `Win32 5` 限制及 checkpoint target wording 的集成修正均有记录。当前 status=`719 NUL / 47279 bytes / SHA-256 5CB2B903F79F85E5A0203B527E69D63D43C43456E6BA52116DD50AC44C5932A8`，较 #10 checkpoint 增加 5 条/393 bytes；更早旧 checkpoint 差异=`UNKNOWN / NOT_VERIFIED`。Capture=`BLOCKED / NOT_RUN`。唯一 DAG=`REBASELINE_PLAN.md`，Task=`tasks/P02PRE-R1F.md`，恢复点=`../verification/P02/codex-checkpoint-p02pre-r1f-20261011.md`。

Live Git=`main@cddff58469b56e181019a8ddfeade80684bc7eb9` / tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；受控 status=`719 NUL / 47279 bytes / SHA-256 5CB2B903F79F85E5A0203B527E69D63D43C43456E6BA52116DD50AC44C5932A8`，pathspec 排除 `.tmp.driveupload`。Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`；风险状态见 [`STATUS`](STATUS.md)。

## 2026-10-11 历史状态与恢复指针：P02PRE-R1F R5 独立 Review 执行中（已由上方取代）

唯一 Active 产品 Task=P02；Active 子 Task=`P02PRE-R1F`。Review Round 5 follow-up #1=`CHANGES_REQUESTED (0/0/0/4)`，Codex adjudicate 并修复 F1–F4；当前候选 PS 5.1 isolated self-check=`PASS_WITH_EVIDENCE`（7 个纯函数、0 output、未调用 capture/getter/write）。Follow-up #2=`ACTIVE / DISPATCHED`，DSH session=`session-ead06978-467a-4a44-8ef7-7326c4224dee` 已核实并挂载。parser R8 尚未运行；capture=`BLOCKED / NOT_RUN`。Task 见 [P02PRE-R1F](tasks/P02PRE-R1F.md)，唯一 DAG 见 [REBASELINE_PLAN](REBASELINE_PLAN.md)，恢复点=`../verification/P02/codex-checkpoint-p02pre-r1f-20261011.md`。

Live Git=`main@cddff58469b56e181019a8ddfeade80684bc7eb9` / tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；受控 status=`712 NUL records / 45224 bytes / SHA-256 046EC5469C60928972A729670A9DA287072CD702442D7E9425166221720E0979`，pathspec 排除 `.tmp.driveupload`。Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`；风险状态与用户 waiver 见 [`STATUS`](STATUS.md)。

## 2026-10-11 历史状态与恢复指针：P02PRE-R1F Round 2 Review 执行中（已由上方取代）

唯一 Active 产品 Task=P02，Active 子 Task=`P02PRE-R1F`；Owner/Author/Integrator/Adjudicator=`Codex /root`，非作者 Reviewer=`DeepSeek Harness`。R1 已作为 partial safe-stop 关闭且不重跑；R1F Round 1 Review=`CHANGES_REQUESTED (0/1/2/2)`，Codex 已修复 F1–F5。Round 2 exact Task/manifest/script 已冻结并由 DeepSeek Harness 只读复审；R4 parser 绑定旧 script，最终 R5 parser 必须在 Round 2 `APPROVED` 后运行。唯一 capture 仍 `BLOCKED / NOT_RUN`。详细交付/pins 见 [P02PRE-R1F Task](tasks/P02PRE-R1F.md)；唯一恢复点=`../verification/P02/codex-checkpoint-p02pre-r1f-20261011.md`。

Live Git=`main@cddff58469b56e181019a8ddfeade80684bc7eb9` / tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；受控 status=`712 NUL records / 45224 bytes / SHA-256 046EC5469C60928972A729670A9DA287072CD702442D7E9425166221720E0979`，pathspec 排除 `.tmp.driveupload`。Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`；风险状态与用户 waiver 见 [`STATUS`](STATUS.md)。

## 2026-10-11 旧索引状态：P02PRE-R1 pre-run capture 已 adjudicate（已由上方取代）

唯一 Active 产品 Task=P02；当前 Active 子 Task=`P02PRE-R1`。DSH Round 1/2/3 均=`CHANGES_REQUESTED`（`0/2/6/3`、`0/0/3/2`、`0/0/1/2`）；R3 关闭前两轮所有 findings。Round 4 全量 Review=`CHANGES_REQUESTED`（`0/0/0/1`），19 项历史 findings 全部关闭，唯一 manifest finding 已修正；hash-bound parser evidence 已生成。第一次窄复核的 P3-PIN-1 被 Codex 三种本机 SHA-256 方法与 JSON 三处字段证据否定，原 Reviewer 正在作第二次极窄确认，session=`session-a98bffe4-310e-4726-8125-830ca5d0f02c`，本机等待进程=`14413`。Task=`tasks/P02PRE-R1.md`；文件 pins、Review/parse/adjudication 和唯一 recovery point 见 Task 与 checkpoint。

Live Git=`main@cddff58469b56e181019a8ddfeade80684bc7eb9` / tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；受控 status=`712 NUL records / 45224 bytes / SHA-256 046EC5469C60928972A729670A9DA287072CD702442D7E9425166221720E0979`，pathspec 排除 `.tmp.driveupload`。Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`；风险状态与用户 waiver 见 [`STATUS`](STATUS.md)。

风险/Gate 原值：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。R0 结束、不重做 runner/source 静态研究。Windows Sandbox 不查询、安装、启用或启动。

## 2026-10-11 11:27 Asia/Shanghai 最新状态与恢复指针

唯一 Active 产品 Task=P02；最新 P02PRE 子 Task=`P02PRE-R0S6`，最终=`blocked / NOT_SAFE_FOR_R0`。DSH R1=`CHANGES_REQUESTED`（0/0/4/6），Codex 已修订；非作者 R2=`APPROVED`（0/0/0/0）；Codex adjudication 与文档集成核验完成。没有 host getter 获准。Task=`tasks/P02PRE-R0S6.md`；manifest=`../verification/P02/p02pre-r0s6-manifest-20261011.md`；delivery、Review、adjudication、verification 与 checkpoint 路径见 Task。本次用户仅批准受控只读取证，不授权后续 runner/source-contract 审查、主动测试或写操作。

最后核实的 Live Git=`main`、HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`、tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；此前工作区 dirty、`main...origin/main [ahead 1365]`；记录的 `.git/index` SHA=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`。status 未紧邻 pre-hash，故 index side effect=`NOT_VERIFIED`；本次收尾未重新核验 Git。

五态：历史 R0 固定对象/时点局部证据=`PASS_WITH_EVIDENCE`；本轮 host `FAILED=∅`；当前身份、profile/path、ACL、TEMP/cache/scratch、protected hashes、WER/T0、private registry=`UNPROVABLE`；LPAC/canary/child/write closure/stop-cleanup=`REQUIRES_ACTIVE_TEST`；当前 runner 及依赖 getter=`NOT_SAFE_FOR_R0`。风险/Gate 原值不变：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；P02PRE/Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。Windows Sandbox 不查询、安装、启用或启动。唯一任务图=`REBASELINE_PLAN.md`；当前状态与恢复点见 `STATUS.md`、`../verification/P02/p02pre-r0s6-checkpoint-20261011.md`。

## 2026-10-11 最新状态与恢复指针（10:57 Asia/Shanghai）

唯一 Active 产品 Task=P02；最新 P02PRE 子任务=`P02PRE-R0S5`，当前=`blocked / NOT_SAFE_FOR_R0`（静态文档审结，host query 未运行）。Task=`tasks/P02PRE-R0S5.md`；manifest=`../verification/P02/p02-readonly-preflight-r0s5-manifest-20261011.md`；Owner delivery=`../verification/P02/codex-p02pre-r0s5-delivery-20261011.md`；Round 1/2/3 Review=`../verification/P02/dsh-p02pre-r0s5-review-20261011.md`、`../verification/P02/dsh-p02pre-r0s5-review-r2-20261011.md`、`../verification/P02/dsh-p02pre-r0s5-review-r3-20261011.md`（分别 `0/0/2/4`、`0/0/1/4`、`0/0/0/1 approved`）；adjudication、verification、checkpoint 均见 Task。当前 runner/getters 仍未证明无副作用。

本次用户裁决只允许 r6 exact-object controlled read-only preflight，不是新 waiver、Gate PASS 或 Build Barrier 解除。风险原值与整体状态保持：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；P02PRE/Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。Windows Sandbox 不查询、安装、启用或启动。

当前任务 DAG 与中文 Mermaid 图见 [REBASELINE_PLAN](REBASELINE_PLAN.md)；Live 状态与 R0S5 recovery 在 [STATUS](STATUS.md) 和 `../verification/P02/codex-checkpoint-p02pre-r0s5-20261011.md`。

## 历史状态与恢复指针（10:09 Asia/Shanghai；已由上方取代）
## 2026-10-11 最新状态与恢复指针（10:09 Asia/Shanghai）

唯一 Active 产品 Task=P02；最新 P02PRE 子任务=P02PRE-R0S4，Task=`blocked / NOT_SAFE_FOR_R0`。DeepSeek Harness Round 2=`APPROVED`（P0/P1/P2/P3=0/0/0/3）；目标机 capture 未运行，因为 runner 启动、profile/cache/history、executable/argv 与 wrapper/temp/log 副作用边界未证。Round 2 的三项 P3 均已由 Codex adjudicate；没有任何 P02PRE 条件记为 FAILED。

R0S4 Task=`tasks/P02PRE-R0S4.md`；manifest=`../verification/P02/p02-readonly-preflight-r0s4-manifest-20261011.md`；Owner delivery=`../verification/P02/codex-p02pre-r0s4-delivery-20261011.md`；Round 1/2 Review 与 prompt、adjudication、integration verification 均从该 Task 链接；rolling recovery=`../verification/P02/codex-checkpoint-p02pre-r0s4-20261011.md`。唯一规划与中文 DAG 见 [REBASELINE_PLAN](REBASELINE_PLAN.md)。

新受控 NUL status=`exit 0 / 569 records / 36542 bytes / stderr empty / SHA-256 0E52E6B4ADACC0AC9C4F29A8FAD402DDAF9A7FB51B21A789FBE57EDE82681E8C`；`.git/index` 前后 hash 均=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`；worktrees=`361`。先前无 pre-hash 的普通 status 仍=`index_side_effect=NOT_VERIFIED`，新快照不追溯补证。Live branch=`main`、HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`、tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`，完整恢复细节见 checkpoint。

风险及 Gate 不变：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。P02PRE=`BLOCKED`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。不得查询、安装、启用或启动 Windows Sandbox。

## 历史状态与恢复指针（08:47 Asia/Shanghai；已由上方取代）

唯一 Active 产品 Task=P02；当前子任务=P02PRE-R0S2，Task/manifest 正由 DeepSeek Harness 做静态 Review；未运行其候选 registry query。只允许审查冻结的 HKLM LocalDumps 两视图只读打开范围；shell startup/profile 若不能证明无副作用，必须 `NOT_SAFE_FOR_R0` 并停止。

R0S1 已完成受限 capture、非作者 Review 与 Codex adjudication：`STOP_UNTRUSTED_OR_UNAVAILABLE_BUILTIN_MODULE`，在任何 G: path 查询前停止；scratch emptiness 仍 `UNPROVABLE`，Get-ChildItem 方法 `NOT_SAFE_FOR_R0`。详情见 [R0S1 Task](tasks/P02PRE-R0S1.md)、[R0S1 evidence](../verification/P02/p02-readonly-preflight-r0s1-evidence-20261011.md)、[R0S1 Review](../verification/P02/p02-readonly-preflight-r0s1-review-20261011.md)、[R0S1 adjudication](../verification/P02/codex-p02pre-r0s1-adjudication-20261011.md)。当前 Task=`tasks/P02PRE-R0S2.md`；manifest=`../verification/P02/p02-readonly-preflight-r0s2-manifest-20261011.md`；唯一规划/DAG=`REBASELINE_PLAN.md`。

风险与 Gate 不变：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。P02PRE=`BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（尚未执行，不是失败）。用户只读授权不构成新 waiver 或 PASS。不得查询、安装、启用或启动 Windows Sandbox。

恢复点=`../verification/P02/codex-checkpoint-p02-readonly-preflight-r0s2-review-20261011.md`（Review 完成后写入；未创建前请从最新 Task/Review logs 与 R0S1 adjudication 核对 Live Git）。

## 历史状态与恢复指针（08:26 Asia/Shanghai；已由上方取代）

唯一 Active 产品验证 Task=P02；当前 Active 子任务=`P02PRE-R0S1`，Owner=`Codex /root`，非作者 Reviewer=`DeepSeek Harness`，Integrator/adjudicator=`Codex /root`。R0 evidence delivery/review/adjudication slice 已完成；DSH Review=`APPROVED_AS_READ_ONLY_EVIDENCE_DELIVERY_ONLY`（0/0/5/6），Codex 接受为有限只读取证并保留各项边界。详见 [P02PRE-R0 Task](tasks/P02PRE-R0.md)、[R0 Review](../verification/P02/p02-readonly-preflight-r0-review-20261011.md)、[R0 adjudication](../verification/P02/codex-p02pre-r0-adjudication-20261011.md)。

R0S1 manifest 经三轮静态顾问（`/root/r0s1_manifest_advisor`，`gpt-6.1-sol / high`）评估为 `SAFE_TO_CAPTURE`，第四次确认 runner 文字一致；仅是静态安全意见，不是数据结果 PASS 或 Gate 放行。pre-query checkpoint 已 pin Task=`8303 bytes / BD73A543B2DBA2A28A38493769B64770C88DB14188D6BBD97189EA903082E2AD` 与 manifest=`22925 bytes / CA293C34473D25E406E72B7DB05AC9364A69544D41214B93857ABAD11FEC6DE3`；安全 status=`523 records`、index 前后 hash 相同。当前仅待冻结 runner 执行，OS query 尚未运行；授权不包括任何写入、profile/API、registry/ACL 操作、build/Cargo、AC1–AC7 或 Windows Sandbox。manifest=`../verification/P02/p02-readonly-preflight-r0s1-manifest-20261011.md`，checkpoint=`../verification/P02/codex-checkpoint-p02-readonly-preflight-r0s1-20261011.md`。

用户风险裁决原值保持：`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；固定原文=`technical condition unmet; user explicitly accepted residual risk`。只读授权不豁免其他要求、不构成 Gate PASS。总体 P02PRE=`BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（未运行，不是失败）。P02M11=`BLOCKED / NOT_VERIFIED`，因 Owner 额度中断且 handoff 未核验。唯一 DAG=`REBASELINE_PLAN.md`。不查询、安装、启用或启动 Windows Sandbox。

## 历史状态与恢复指针（2026-10-10 16:56 UTC；已由上方取代）

唯一 Active 产品验证 Task=P02；当前 Active 子任务=P02M11，由 `/root/p02_gate_feasibility`（ExpertAdvisor）静态综合 M7–M10 证据，Reviewer/Integrator=`Codex /root`。M11 检查当前安全条件下是否存在尚未覆盖的可证执行路线；不运行任何 OS/API 或 Build。M7–M10 的静态完成状态不代表技术 Gate 通过。Task 范围见 [P02 Task](tasks/P02.md)。

M11 Owner 预期只写 `../verification/P02/codex-p02-unwaived-gate-feasibility-20261011.md`；Codex 后续 Review 与 adjudication 分写固定 evidence 文件。当前其余技术 blockers 和 Gate 状态保持不变。

用户风险状态=`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；固定原文=`technical condition unmet; user explicitly accepted residual risk`。waiver 只豁免创建前无副作用证明目标 private registry storage 不存在；不是技术 PASS，不豁免其他执行安全条件或 AC1–AC7。

profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS preflight=`NOT_RUN`；P02PRE=`BLOCKED`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（尚未运行，不是失败）。唯一 DAG=`REBASELINE_PLAN.md`；运行状态=`STATUS.md`；M10 adjudication=`../verification/P02/codex-p02-owner-risk-waiver-manifest-r6-adjudication-20261011.md`；最新 checkpoint=`../verification/P02/codex-checkpoint-p02-manifest-r6-reconciliation-20261011.md`。不查询、安装、启用或启动 Windows Sandbox。

## 历史状态与恢复指针（2026-10-10 16:52 UTC；已由上方取代）

## 历史状态与恢复指针（2026-10-10 16:27 UTC；已由上方取代）

唯一 Active 产品验证 Task=P02；P02M6=`DONE / APPROVED_AS_STATIC_ASSESSMENT_ONLY`，但 `profile_folder_no_side_effect=UNPROVABLE / BLOCKED`。P02M7=`DONE / ACCEPTED_AS_STATIC_RESEARCH_ONLY`，Owner report SHA-256=`BB6A7676B6C48EB84D0D846E26F0E8F817684BDB27D67BD45813DA2D8508FD8A`，Review=`APPROVED`，Codex adjudication 已记录；profile-folder blocker 仍在。P02M8 Owner Delivery=`DONE / NOT_RESOLVED`（SHA-256=`8F9F3E60009F2DD3767DA5A2B45C4582A56ED7EE5E86957705778BE80D295DF6`），M8R=`ACTIVE`，Reviewer=`/root/p02_manifest_reviewer`。P02M9 Owner Delivery=`DONE / NOT_RESOLVED`（SHA-256=`6207483ED6CE62650C346D18D42FC81CD5102C44A028BAF0DE4F131AF60411F3`），M9R=`ACTIVE`，Reviewer=`/root/p02_isolation_advisor`。当前 Active 子任务=`P02M8R + P02M9R`；Integrator=`Codex /root`。

用户风险状态原值=`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；固定句=`technical condition unmet; user explicitly accepted residual risk`。仅豁免创建前无副作用证明目标 private-registry storage 不存在。profile-folder 与其它安全条件仍未满足；profile=`NOT_CREATED`、ACL/registry=`NOT_MODIFIED`、OS preflight=`NOT_RUN`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、AC1–AC7=`BLOCKED / NOT_RUN`（不是失败）。

唯一任务 DAG 见 [REBASELINE_PLAN](REBASELINE_PLAN.md)，运行状态见 [STATUS](STATUS.md)，当前 Task 见 [P02 Task](tasks/P02.md)，M6 adjudication=`../verification/P02/codex-p02-profile-folder-noncreating-contract-adjudication-20261010.md`；M7 adjudication=`../verification/P02/codex-p02-profile-folder-versioned-contract-adjudication-20261010.md`；最新 checkpoint=`../verification/P02/codex-checkpoint-p02-m7-m8-review-m9-20261010.md`。不查询、安装、启用或启动 Windows Sandbox。

## 2026-10-10 最新状态与恢复指针（16:18 UTC）

唯一 Active 产品验证 Task=P02；P02M6 已由非作者 Reviewer 与 Codex adjudicate 为 `DONE / APPROVED_AS_STATIC_ASSESSMENT_ONLY`，结论仍是 `profile_folder_no_side_effect=UNPROVABLE / BLOCKED`。当前 Active 子任务=P02M7（profile-folder 版本化合同只读补查，Owner `/root/p02_isolation_advisor`、Reviewer `/root/orchestration_docs_review`）和 P02M8（zero-capability registry Getter 合同只读补查，Owner `/root/orchestration_docs_review`、Reviewer `/root/p02_manifest_reviewer`）；Integrator 均为 `Codex /root`。两项都不运行 OS/API、不查目标机状态。

Live root=`G:\CODEX\New Manga`，`main@cddff58469b56e181019a8ddfeade80684bc7eb9` / tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；`main...origin/main [ahead 1365]`。用户 waiver 原值为 `private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`，必须记录 `technical condition unmet; user explicitly accepted residual risk`；仅豁免创建前无副作用证明目标 private-registry storage 不存在。profile=`NOT_CREATED`、ACL/registry=`NOT_MODIFIED`、OS preflight=`NOT_RUN`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、AC1–AC7=`BLOCKED / NOT_RUN`（不是失败）。

唯一任务 DAG 见 [REBASELINE_PLAN](REBASELINE_PLAN.md)，运行状态见 [STATUS](STATUS.md)，当前 Task 见 [P02 Task](tasks/P02.md)，M6 adjudication=`../verification/P02/codex-p02-profile-folder-noncreating-contract-adjudication-20261010.md`，恢复见 [P02M7 checkpoint](../verification/P02/codex-checkpoint-p02-profile-folder-versioned-contract-m7-20261010.md)。不查询、安装、启用或启动 Windows Sandbox。

## 2026-10-10 最新状态与恢复指针（16:10 UTC）

唯一 Active 产品验证 Task=P02，唯一 Active 子任务=P02M6（profile-folder path API 创建前无副作用合同评估）。Live root=`G:\CODEX\New Manga`，`main@cddff58469b56e181019a8ddfeade80684bc7eb9` / tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；Git common-dir=`G:/CODEX/New Manga/.git`，登记 worktree=`363`，`main...origin/main [ahead 1365]`。用户未提交文件保留。

用户风险状态仍为 `private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`，须记录 `technical condition unmet; user explicitly accepted residual risk`。只豁免创建前 private-registry absence proof。r5=`28956 bytes / SHA-256 B97FB2115C17476AAE768368B315D438FB8BE4CC2C5072C88FF36A79DAB1D6E1` 已由非作者 Reviewer `APPROVED`（0/0/0/0），并由 Codex adjudicate 为静态文档通过；P02M6 仅研究 profile-folder path getter 的创建前无副作用合同，不运行 OS/API。profile=`NOT_CREATED`、ACL/registry=`NOT_MODIFIED`、OS preflight=`NOT_RUN`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、AC1–AC7=`BLOCKED / NOT_RUN`（不是失败）。P22=`in_review`、未集成；P04=`BLOCKED`、`blocked_by:[P22]`。

唯一任务 DAG 见 [REBASELINE_PLAN](REBASELINE_PLAN.md)，运行状态见 [STATUS](STATUS.md)，当前 Task 见 [P02 Task](tasks/P02.md)，恢复见 [P02 profile-folder contract checkpoint](../verification/P02/codex-checkpoint-p02-profile-folder-contract-m6-20261010.md)。不查询、安装、启用或启动 Windows Sandbox。

## 历史状态与恢复指针（2026-10-10 15:52 UTC；已由上方取代）

当前唯一 Active 产品验证 Task=P02；P02M3 正在审查 r3 manifest。Live root=`G:\CODEX\New Manga`，`main@cddff58469b56e181019a8ddfeade80684bc7eb9` / tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；`main...origin/main [ahead 1365]`，Git common-dir=`G:/CODEX/New Manga/.git`，登记 worktree=`363`。现有未提交用户内容保留；当前 dirty/untracked 项数以最新 rolling checkpoint 实测为准。

用户明确接受的风险状态：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；必须保留 `technical condition unmet; user explicitly accepted residual risk`。该 waiver 仅限创建前无副作用证明 private-registry storage 不存在。r2 Review=`CHANGES_REQUESTED`（0/0/2/0）；Codex 已冻结 r3 exact manifest=`26594 bytes / SHA-256 322524C3E1FDC894B0E09639A61E55D56422B03AC561484D0AE5994FAF3CD03F`，非作者 Reviewer `/root/p02_manifest_reviewer` 复核在途。Hard Build Barrier=`EFFECTIVE`；Build Gate=`BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS preflight=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（未运行，不是失败）。P22=`in_review`，未集成；P04=`BLOCKED`、`blocked_by:[P22]`。

Review interim 已提出 MR2-01 的 residual：raw `git status` 完全相等与新增 canary 冲突；需等固定 r3 的最终 Review 和 Codex 裁决，必要时修订并复审。当前唯一恢复点=`../verification/P02/codex-checkpoint-p02-owner-risk-waiver-manifest-review-r3-20261010.md`。

唯一 DAG 见 [REBASELINE_PLAN](REBASELINE_PLAN.md)，运行状态见 [STATUS](STATUS.md)，当前 Task 见 [P02 Task](tasks/P02.md)，恢复点见 [P02 r3 rolling checkpoint](../verification/P02/codex-checkpoint-p02-owner-risk-waiver-manifest-review-r3-20261010.md)。继续遵守用户决定：不查询、安装、启用或启动 Windows Sandbox。

## 历史状态与恢复指针（2026-10-10 15:31 UTC；已由上方取代）

实时状态：主仓 `main@cddff58469b56e181019a8ddfeade80684bc7eb9` / tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；`main...origin/main [ahead 1365]`；15:31 核验时 `git status --porcelain`=`396` 项，原作者未提交内容保留。唯一 Active 产品验证 Task=P02（`in_progress / ACTIVE`）。用户已批准 Owner 风险例外：`private_registry_absence=UNPROVABLE` 仍为技术事实；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`。manifest r1 已冻结，等待独立 Review；执行前检查尚未进行；Hard Build Barrier=`EFFECTIVE`，Build Gate=`BLOCKED`，profile=`NOT_CREATED`，ACL/registry=`NOT_MODIFIED`，AC1–AC7=`BLOCKED / NOT_RUN`（未运行，不是失败）。P22=`in_review`、未集成；P04=`BLOCKED`、`blocked_by:[P22]`。DAG 见唯一规划事实源 [REBASELINE_PLAN](REBASELINE_PLAN.md)，运行状态见 [STATUS](STATUS.md)；恢复见 [P02 manifest Review checkpoint](../verification/P02/codex-checkpoint-p02-owner-risk-waiver-manifest-review-r1-20261010.md)。

**P02：**本轮最新决定覆盖历史 B，精确保留说明 `technical condition unmet; user explicitly accepted residual risk`；仅豁免创建前无副作用证明目标 private-registry storage 不存在。其他隔离、安全和证据条件均未豁免。当前 `P02M` 正在进行 manifest r1 独立 Review；manifest=`19626 bytes / SHA-256 8DB5B79DD1F4F166455E4769C4B06D0EB0DDE1CEE80822DE7F3137E4B15DD720`；Advisor `/root/p02_isolation_advisor` 报告=`26212 bytes / SHA-256 7A6B6D72C8484611B05DF6AC666A5A9D69A7F582EC21D2EC455D064938CB3C45`，其结论不解除 LPAC registry getter、子进程/写入闭包、WER bootstrap 等阻塞。先前 registry 缺失研究及其 Review/adjudication 仍是原技术结论的证据，未变成 Gate 通过；详情见 [用户决定记录](../verification/P02/codex-p02-human-required-decision-20261010.md)、[P02 Task](tasks/P02.md) 与 [rolling checkpoint](../verification/P02/codex-checkpoint-p02-owner-risk-waiver-manifest-review-r1-20261010.md)。

P02/P04 仍遵守先前用户裁决：允许按本机 Windows 隔离验证方式推进，不要求查询、安装、启用或启动 Windows Sandbox，也不把本机描述为具有 VM 隔离能力；这不豁免数据保护或发布 Gate。较早索引中的 P04 R1 状态保留为历史快照，P04 当前状态以 [STATUS](STATUS.md) 和 [P04 Task](tasks/P04.md) 为准。

P22 R10 Owner Handoff HEAD/tree=`4a707db80499f11e93cee163a9a10bf6392b1a92` / `c6d58a41589c61501fa2c520626ee2b0f263d1a2`；R10 DSH Review=`APPROVED_WITH_CONDITIONS`（0/0/0/1，report SHA=`0ED64E643D5227E0AF3D05E4D5D70DE22614476EBDB57672AC145E0C37232BFA`），Codex adjudication 见 [R10 evidence](../verification/P22/codex-p22-r10-review-adjudication.md)。Handoff-only Review 不批准 P22 integration/Cargo/runtime/AC2；P02 Hard Build Barrier 仍生效，P04 仍 blocked by P22。详见 [P22 Task](tasks/P22.md)。

与前一有效 Checkpoint（14:18 UTC）相比，新增 Owner 对单项技术条件的正式风险接受；这改变了准入处置，但没有改变该项技术事实，也没有产生任何 OS、Build 或 AC Gate 证据。P22/P04 状态未变。详细旧状态见 [此前 rolling checkpoint](../verification/P02/codex-checkpoint-autonomous-orchestration-20261010.md)。

## 前一检查点：2026-10-10 10:02 UTC（已由上方取代）

P02 memo r2 DSH Review（exec session=`29625`）与 P22 R8 Owner 修订（exec session=`95264`）在途；Gate 状态与当前相同。历史详情见 rolling checkpoint。

## 前一检查点：2026-10-10 09:46 UTC（已由上方最新状态取代）

实时状态：主仓 main@cddff58469b56e181019a8ddfeade80684bc7eb9 / tree=c25d051a4b9a0bd9773b50170e100f575ea19f2b；原作者未提交文件保留。唯一 Active 产品验证 Task=P02；P22 为独立修复 Active 切片，P04=BLOCKED、blocked_by:[P22]。任务图以 [REBASELINE_PLAN](REBASELINE_PLAN.md) 为唯一规划事实源，状态以 [STATUS](STATUS.md) 为准。

P02 用户完整授权已记入 [P02 Task](tasks/P02.md)。r7 DSH 内容 Review=`APPROVED`（0/0/0/5），DSH-R6A-01..12 CLOSED；报告 SHA=`C1FADDC2D366286F14473DB68AE72D20FCF946E15DE50E4AFA3E2752998EF705`，Codex adjudication 已记录。Codex 发现 EA-01，另发现 r7 `FileHardLinkInfo` class 与 Microsoft 有效枚举不符；manifest r3 也未冻结 token/security/file-ID API、WER `%ProgramData%` resolver、T0 bootstrap 顺序与 no-child/no-write 方法；Phase A=`BLOCKED / NOT_RUN`，OS observer 候选未证明完整覆盖；详见 [method memo](../verification/P02/codex-phase-a-method-blockers-20261010.md)；DSH 非作者 Review exec session=`85517` 在途。private_registry_absence=`UNPROVABLE / BLOCKED`；profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；OS isolation preflight=`NOT_RUN`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build 与 AC1–AC7=`NOT_RUN / BLOCKED`。不调用 Windows Sandbox。

P22 R5 Handoff fixed HEAD=`7229ef5b2f6925115b91d28900bffe377513f5cd` / tree=`712da4becaff2b5f3519e88261cb515c80b54a1f`，parent=`0e46ec7e8c23a1fc0ba793745f5101813b388ea3`；R4..R5 仅改 Handoff，Codex `git diff --check` EXIT 0。DSH R5 内容结论=APPROVED_WITH_CONDITIONS（4 项非阻断 P3），object_binding=NOT_VERIFIED；Codex 已核验 HEAD/tree/parent、仅 Handoff path 与 diff-check EXIT 0。R6 fixed HEAD=`a61e2979d7808d1efaa15283a7e17bac038b7748`，Codex 核对仅 Handoff path 与 diff-check EXIT 0；DSH R6 Review=`APPROVED_WITH_CONDITIONS`（0/0/0/2），`object_binding=NOT_VERIFIED`；Codex adjudication 见 [R6 evidence](../verification/P22/codex-p22-r6-review-adjudication.md)。Antigravity 原 Owner R7 Handoff-only 修订 exec session=`63652` 在途。P22 未集成，Cargo/runtime=`BLOCKED / NOT_RUN`；P04=`BLOCKED`、`blocked_by:[P22]`。恢复见 [rolling checkpoint](../verification/P02/codex-checkpoint-autonomous-orchestration-20261010.md)。

## 历史快照：2026-10-10 当前授权与恢复点（已由上方更新）

用户已授权本轮 Lead 自动推进，并授权 Codex 按路径级契约进行 P02 AppContainer 隔离预检。r2 exact-object DSH Review=`NOT_VERIFIED`，内容等同 `CHANGES_REQUESTED`（P0/P1/P2/P3=`2/5/8/7`）；r3 DSH Review=`NOT_VERIFIED`、内容=`CHANGES_REQUESTED`（0/3/8/8），Codex 已记录 [r3 finding adjudication](../verification/P02/codex-appcontainer-contract-r3-adjudication.md) 并形成 [r4 contract candidate](../verification/P02/appcontainer-isolation-contract-r4.md)（SHA=`F025A2671FA16EB317C04C457C75BBD6A29D16A753FF146BCAD4AF244A591F49`，Review pending）。公开文档无法确定目标 private registry 在 profile 创建前的精确只读存在性检查；该项=`UNPROVABLE / BLOCKED`，不猜路径、不创建 profile。P02 是唯一 Active 产品验证 Task；profile=`NOT_CREATED`、ACL/registry=`NOT_MODIFIED`、OS preflight=`NOT_RUN`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、build=`NOT_AUTHORIZED / NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`。无需查询、安装、启用或启动 Windows Sandbox。

P04 R3=`CHANGES_REQUESTED`（0/0/3/1）；R4 fixed commit=`faea1a2c9e19f4817fd792290e91324f047529f9` 的 DSH Review=`APPROVED`（0/0/0/4 非阻断 P3）。P22 r1 delivery=`680e3830337a4533ea3625ed8108431067cf26d5` 的非作者 DSH Review=`CHANGES_REQUESTED`（0/1/0/3，report SHA=`07CD89F065AC63EE26D6E38100FC700AFEB4B377F997DF2AA3FED6C0D6D68853`；object binding=`NOT_VERIFIED`），Codex 已通过 Antigravity 原 Owner 会话派发 r2 返修。P04=`BLOCKED`、`blocked_by:[P22]`；AC1/AC2/Cargo=`BLOCKED / NOT_RUN`。全局 DAG 与当前状态以 [REBASELINE_PLAN](REBASELINE_PLAN.md) 为准；滚动恢复见 [P02 orchestration checkpoint](../verification/P02/codex-checkpoint-autonomous-orchestration-20261010.md)。

裁决前 preflight 快照（2026-10-10；以下 Sandbox Feature blocker 已由最新用户裁决取代）：P01/P03/P08/P05=done；P02=in_progress / ACTIVE 为唯一 Active 产品验证 Task，产品范围 r1–r4、AC、Owner allowlist 与行为基线保持冻结。DSH R5 follow-up Review 对真实 D16=999e6adfc229698344c0cbf9bfb6d636fe73fb7c / tree=5da44588cbc791d4cf1d34aa3d20f0316fc320d5=APPROVED；R5-01..05 CLOSED；R5 findings=P0/P1/P2/P3=0/0/0/3、open=3；R5F-01/02=false_positive、R5F-03=deferred（可选 P3）。Fresh preflight D21 evidence Review=APPROVED（P0/P1/P2/P3=0/0/0/4；P3-1..4 修复复审待完成）。Review 后 fresh preflight 的 R2 HostFolder recheck=PASS（11/11 mappings、204,419 records、mismatch=0），12/12 roots、20/20 input hashes、14/14 registered sizes、3/3 EOL pins 与 3/3 hardlinks 均匹配。宿主 10/11 条件 PASS；Windows Sandbox Feature query=UNKNOWN（非提权 PowerShell EXIT=1 / COMException），所以 fresh preflight=BLOCKED（D21 evidence Review=APPROVED；P3-1..4 文档修正复审待完成），wsb start=NOT_RUN。Smoke=NOT_RUN、Build Gate=BLOCKED、build=NOT_AUTHORIZED / NOT_RUN、hook/cache=BLOCKED / NOT_VERIFIED、AC1–AC7=BLOCKED / NOT_RUN、Hard Build Barrier=EFFECTIVE。恢复见 [P02 post-review preflight blocker checkpoint](../verification/P02/codex-checkpoint-p02-post-review-preflight-blocked-r1.md)。

历史观测（2026-10-10 04:11，clone 创建前）：Stage-1 pre-admission=PRESTART_STAGE_1_PASS（16/16），不作为当前准入证据。DSH Review 前的 host、feature、input、EOL、hardlink、UI 与 HostFolder captures 同样已被本次 post-review fresh 检查取代；当前 feature=UNKNOWN 与完整阻断依据见 [P02 blocker checkpoint](../verification/P02/codex-checkpoint-p02-post-review-preflight-blocked-r1.md)。

前次工作快照（r6）：P08/P03/P01=done，唯一Active P02=`in_progress / ACTIVE`；P系列done 3/21、in_progress 1、proposed 17、ready 0。P02范围r1–r4冻结；Owner=Antigravity、Reviewer=DeepSeek Harness、Integrator=Codex。固定Stage A r6=`38672473f93971a4681aef682e5635e64b0bd896` / tree=`2aa967bbf961a0e9e58dd3e1489d74635491e28f` 的DSH正式Review=`approved_with_conditions`（仅Stage A），P0/P1/P2/P3=`0/0/0/4`，open=4；R5-01..06已闭合，R6-01..04为P3条件。r6未集成，`integration_commit: null`；r7已在原Antigravity会话按冻结allowlist返修。AC1–AC6仍BLOCKED；P01 integration=`13e66ec5bf9a2fc59f4e6c5623feb0bde22884c8`；P02行为基线=`241ff3b70b6fc0490ea238efd486cc707f849031`。恢复见[r6 Review后checkpoint](../verification/P02/codex-checkpoint-after-r6-dsh-review.md)、[P02 RESUME](../verification/P02/RESUME.md)和[P02自动推进提示词](../verification/P02/NEXT-AUTOPROGRESS-PROMPT.md)。

2026-10-08人员更新：Qoder已退出本项目。当前角色/接管名单见[协作协议](09_COLLABORATION.md)；未来UI设计/实现归ZCode，历史Qoder署名仅作证据。整体路线与恢复材料已同步，不新增产品释放。

**整体规划入口**：[权威Plan与候选Task](REBASELINE_PLAN.md)、[中文依赖图](../verification/PROJECT-ROADMAP-20261008/ROADMAP.md)、[全项目报告](../verification/PROJECT-ROADMAP-20261008/REPORT.md)、[196节点历史台账](../verification/PROJECT-ROADMAP-20261008/task-inventory.csv)、[恢复点](../verification/PROJECT-ROADMAP-20261008/RESUME.md)。历史审计基线为e4242ecd；P08/P03/P01已完成，P01 post-FF保护复核通过。167项登记完成或文档交付不代表新架构产品完成率。

历史索引快照：P02 Owner转移未集成前的r8/C-2现场保留为历史证据；当前Owner、集成与接单状态以本页首段、Plan、Status和[P02 RESUME](../verification/P02/RESUME.md)为准。P01 D3 Review=`approved`、C1及D7 closeout Gate=`PASS`；C8 formal Review=changes_requested仍为历史证据。P03证据见[P03 RESUME](../verification/P03-PACKAGED-SFX-ENTRY/RESUME.md)。

全任务盘点与 inventory 下方段落是其各自审计时的历史快照，不反映当前总数或授权状态；以本页首段、[Plan](REBASELINE_PLAN.md) 与 [STATUS](STATUS.md) 为当前事实。


全量盘点快照：2026-10-07，审计输入 `main@32f9b932`。[REBASELINE 审计报告与下一步派发指令](../verification/REBASELINE-20261007/REPORT.md)；[全部 190 任务节点的台账与流程图](../verification/REBASELINE-20261007/TASK_GRAPH.md)；[完整 Git/Owner/Reviewer/worktree 参数](../verification/REBASELINE-20261007/inventory.json)。在该审计时间点无 Active、无 released；当前授权仍由 REBASELINE_PLAN / STATUS 决定，下面旧日期正文只作历史记录。

> **2026-09-21 Stage A Rebaseline 生效**：后续 Milestone、Task、依赖、Legacy Mapping 与治理以 [REBASELINE_PLAN](REBASELINE_PLAN.md) 为唯一规划事实源；实时状态只看 [STATUS](STATUS.md)。TASK-001～065 及下方历史台账保留为证据，不再决定当前排期。Worktree 清理必须先看 [WORKTREE_SAFETY_INVENTORY](WORKTREE_SAFETY_INVENTORY.md)。

> **Historical pointer（2026-10-07）**：Codex refresh @main `44421008`；A/B/C done，阈值 0.90 与 BJ13 维持现状已确认。该时点释放 [RC-4](tasks/M2-RC4-DOMAIN-COMMANDS.md)，[契约](contracts/M2-RC4_DOMAIN_COMMANDS.md)、[审计证据](../verification/M2-RC4-DOMAIN-COMMANDS/rebaseline-20261007.md)。当前以 PLAN/STATUS 为准。

> **Architecture Decision / M2 release**：[AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md) 的 React + TypeScript / Tauri / Python Core / SQLite 目标保持。资源通道 runtime 与 command-surface hardening 已由 M2-RC1/RC2 集成；production Core 业务 IPC、产品四页 React shell、打包与完整 Release Gate 仍待后续 Task。

2026-09-20 TASK-059 集成：设计重做 Task 已 `done`，integration=`53ae2e4`，最终 Review [TASK-059-58272ab](reviews/TASK-059-58272ab.md) `approved`。ND-1 选定 **F · Graphite Atelier**（A 色彩/状态色/主题 + B 几何含 `card-w=158px` + A IA；无 C 玻璃/D 顶栏/E 命令面板）；设计已集成但未释放实现 Task，ND-4/5/6/7 待用户裁决。

2026-09-19 TASK-059 ND-1 用户裁决：候选方向选择 **A 的配色/视觉令牌与 IA + B 的几何比例（控件高度、行高、间距、字号、面板尺寸）**；不继承 B 的章节大卡 IA，也不启用 C 玻璃、D 顶栏或 E 命令面板。组合稿必须重新通过完整一致性审计后才能集成，C/D/E 未被选择。详见 [STATUS](STATUS.md) 当前台账。

2026-09-19 TASK-059 改派：按用户指示，设计重做 Task 的 Owner 由 Qoder 改为 **ZCode**；新的 branch=`agent/zcode/TASK-059-ui-redesign`、worktree=`G:/CODEX/New Manga.worktrees/TASK-059-zcode`，Reviewer 仍为 Codex。原 Qoder 分支/worktree 未实施且仅留档，不再作为开工工作区；AC、授权和范围不变。

以下 2026-09-19 及更早记录均为 **Legacy 历史台账，无排期或释放效力**。

2026-09-19 增量：Qoder 是当时 QML UI/UX 责任方；[TASK-047](tasks/TASK-047.md)（仅设计）被用户否决。该记录只作历史追溯。

状态（2026-09-19 更新）：TASK-001～TASK-021（TASK-021 仅 trash 子集）、TASK-024、TASK-028～TASK-044 已完成并集成；TASK-041 已完成并集成（`7c4fae0`）；TASK-045 已完成并集成（`e2a8f01`）；TASK-046、TASK-048～TASK-056、TASK-058 已完成并集成（**ZCode 全权窗口 2026-09-19 W0–W11**）；TASK-057 交付待集成（分支 `agent/zcode/TASK-057-backup-restore` 冻结于 `50c4b1a`）；TASK-022、TASK-025～TASK-027 仍冻结（proposed）。**角色已恢复初始定位**：Codex=Lead/唯一主线写入与合并责任人、ZCode=独立 Feature、DeepSeek Harness=独立 Review（不得自审）、Qoder=独立 Feature（与 ZCode 同面，可作**非作者** Reviewer）；Review 须覆盖 Architecture+Verification，Standards/Spec 为可选视角。以下为历史细节：TASK-013 生产 Pipeline seam 已按 `integration_commit=49c72fdf` 集成，R-1 已按 `integration_commit=734d5b3` 完成生产 Workbench 装配并验证；TASK-016 已按 `integration_commit=9bf85f5` 完成集成；TASK-018 已完成 Mask/Inpainting 路线独立实验的**三轮**独立 Review 与集成——首轮 `integration_commit=4d189ce`（Review `doc/reviews/TASK-018-6c33e7f.md` approved），修订切片 `integration_commit=14b92e4`（Review `doc/reviews/TASK-018-5063315.md` approved），尾项切片 `integration_commit=5a9f5c8`（Review `doc/reviews/TASK-018-965bcd2.md` approved；R-001～R-007 与 R-101/R-102/R-103/R-104/R-201 全部 closed，无待处理 finding；学习型路线质量与 Mask 内部结构损伤仍 BLOCKED/NOT_RUN）；TASK-015 已按窗口条款收口 `done`（integration=`fa72cee`，Review=`approved_subagent`）；TASK-024 已按窗口条款收口 `done`（仅设计，integration=`61c33e2`，扩展边界设计见 [TASK-024 契约](contracts/extensions.md)，U-1 已取消网页导入；U-2 已选 PDFium via pypdfium2；U-3 已批准本地目录插件首版范围；U-4 已决定 Plugin Agent 不进入首版，二阶段另行裁决；U-5 已批准字体上传上限与许可提示；U-6 已批准 Sakura 监控限于健康探测和就绪状态、不做深度指标），TASK-017 已按窗口条款收口 `done`（integration=`c0cf3a1`，实验报告见 [doc/research/TASK-017.md](research/TASK-017.md)），其尾项修订切片（吸收 Review R-001/R-002/R-003）已由非作者独立 Review（`doc/reviews/TASK-017-971efe6.md` approved）后集成（`integration_commit=d36f724`；R-001/R-002/R-003/R-101 全部 closed；真实端点层仍 NOT_RUN），窗口三项目标（TASK-015/024/017）全部完成；三份外部 post-hoc Review 均 approved，findings 已由 `c7a02bd` 收口。**TASK-019 已完成并集成**（Owner=`DeepSeek Harness`、Reviewer=`Codex`（非作者）、base=`36242fb`、被审 head `726baf5`（元数据 `6c981c2`）、Review `doc/reviews/TASK-019-726baf5.md` approved（F-1～F-7）、`integration_commit=3755af9`；集成后 `tests/providers` 110 passed/0 skipped、`tests/pipeline`+`core`+`storage` 78 passed/0 skipped、全仓 640 passed/6 skipped；**尾项切片（Standards S-1/S-2 分层修正）** 经非作者 Review `doc/reviews/TASK-019-ab26601.md` approved 后以 `integration_commit=9a5486a` 集成，`application → infrastructure` 依赖为 **0** 并有回归守卫，S-1/S-2 已关闭）；TASK-019 的 **AC-RFULL-001 完整链仍 `BLOCKED`**（缺 `color`/`term_extract`/`render` handler），且 Review 登记了**跨 Task P0 缺陷 F-1**（默认 `sfx_policy='skip'` + planner 不看 `region_type` → 真实默认下整链被 `SKIP_POLICY` 跳过，待用户/Codex 裁决后另立 Task）。TASK-020～TASK-023、TASK-025～TASK-027 继续冻结。仓库现状见 [STATUS](STATUS.md)。2026-09-16 23:30 ～ 09-17 08:30（Asia/Shanghai）的 ZCode 全权窗口已于 2026-09-17 按用户指示归还撤销；条款存档见 [STATUS](STATUS.md)「ZCode 全权窗口授权」。【2026-09-17 23:12:28 ～ 2026-09-18 08:50（Asia/Shanghai）第二个 ZCode 全权窗口进展（执行中）】：W1 **TASK-037 已收口 `done`**（integration=`372c3bf`；已定性 flaky `test_reader_webtoon_swaps_in_vertical_viewer` 修复＋TASK-036 R-01 关闭；三份机制探针修正 TASK-036 定性（extent 批次回写 −0.0、timer 有触发但持久化了回写后的 0），Webtoon 用例夹具改 40x1000 高页＋`landed` 落点断言；Review approved_subagent `7c35277`）。W2 **TASK-033 已收口 `done`**（integration=`4d0f932`；完整链收口——`color`/`term_extract`/`render` 三 handler 接入＋渲染侧生产装配（`RenderService` 复用既有适配器＋`content_decoder` NMFR→PNG 桥）＋「单一写者」P0 约束解决（RenderService 为 `translated` 指针唯一写者，render handler `revision_updates={}`，三次 render 指针 `[1,2,3]` 无抖动）；**AC-RFULL-001 口径更新为 BLOCKED（handler 与生产装配面已打通；真实 OCR/翻译/修复能力仍缺）＋逐项解锁条件，未记 PASS**；Review approved_subagent `401d6d7`；遗留 R-001 P2＝`_clean_available` 继承缺陷（render-only 命令跨 run 规划 BLOCKED，planner 在切片路径外未修，移交 Codex）。W3 **TASK-020 已收口 `done`**（integration=`b738200`；Webtoon 分块处理与阅读——新建 `src/infrastructure/imaging/webtoon_tiles.py`（TileGrid 几何/TileCache LRU/TiledPageRasterizer 按需解码），ViewModel opt-in `tile_factory` 接线（未注入时整图路径不变），QML webtoon viewer tiled 分支；一 Page 原则、坐标回映、边界去重、跨会话恢复均有测试；**1600x200000px fixture 像素解码 BLOCKED（Qt PNG handler ≳300MB rgb32 硬限制、setClipRect 无效），几何层 PASS，未记 PASS**；首轮 Review changes_requested（R-001 P1 全页同步解码）修订收口后复审 approved_subagent `40f20e7`）。F-1（跨 Task P0）已全面关闭：规划面 TASK-032（`e3e055e`）＋渲染面 TASK-035（`bd0d030`）。TASK-034（integration `b6051e5`+`8ca4b23`）与 TASK-036（integration `2725324`）此前已集成。**全部窗口集成的 Review 均为 approved_subagent（用户授权的同体审查）——期满后强制 Codex + DeepSeek Harness 外部 post-hoc 复审（可推翻窗口内 done）。**仓库现状见 [STATUS](STATUS.md)。「当前状态」段的历史口径见本行前文与 [12 Roadmap](12_ROADMAP.md)；本行截至 TASK-019/F-1 待裁决为止，其后进展以上述窗口进展为准。【第二轮（同一 T1=08:50）进展】：W5 **TASK-038 已收口 `done`**（integration=`f835ac9`；`assemble_engine` 注册 `readerViewModel`/`exportViewModel`——export 双路径（路径 A=`readerViewModel.exportController`、路径 B=`exportViewModel` 独立窗口随 workbench 章节）写明并以测试锁定；`tile_factory` 注入（TASK-020 分块阅读生产可达）；`ImportDocumentsUseCase` 接线（TASK-023 PDF 可达、MOBI 仍 typed UNSUPPORTED）；新增 `_ManagedReaderCatalog`（Page→ReaderPage，translated 消费当前 artifact）；`test_qml_contract.py:224` 前提变化等价更新；Review approved_subagent `fcf791f`）。W6 **TASK-039 已收口 `done`**（integration=`c8024fe`；planner `_clean_available` 判据叠加可选 `clean_probe`——probe=None 与修前逐字节等价，根因/对照矩阵/判别力留证；**TASK-033 R-001 已关闭**；生产 probe 注入点（bootstrap）白名单外移交；Review approved_subagent `18c9834`）。W7 **TASK-021 自洽子集已收口 `done`**（integration=`5bc17f8`＋修订 `b940497`；Page 级软删除/同 batch 恢复/受控-only 永久删除——`deleted_at` 列本就存在故零 Schema/migration 变更；`remove_managed` 防逃逸；R-001 P2 修订闭环（复审复现验证回归钩子），其余三子集 frozen；Review approved_subagent `a9b4141`+`79ec0d2`）。**第二轮全部 Review 为 approved_subagent（同体审查）——T1 后 Codex + DSH 强制 post-hoc 复审（可推翻）。**第二轮统一证据口径＝powershell.exe（继承 PATH，openssl 可用）+ TASK-012-py312 → 全仓 N passed/0 skipped（基线 770 → 772 → 780 → **787**）。「当前状态」段第一轮口径（截至 TASK-023）保留于本行前文，第二轮进展如上。【2026-09-19 01:10 ～ 09:00（Asia/Shanghai）第三个 ZCode 全权窗口进展】：W0 **TASK-046**（解码面 overlap=0 / rewind 折叠；Qoder 非作者 Review）integration=`2b40085`；W1 **TASK-048**（§11 P-1 跨线程 SQLite + 生产路径端到端测试资产）`be558ca`；W2 **TASK-049**（§11 P-2 区域输入面：detect handler + Region 生产路径）`e94d5af`；W3 **TASK-050**（§11 P-3 非 UI：设置/provider 绑定注入）`21b7301`；W4 **TASK-051**（§11 P-6 工作台三档视图）`65d1e13`；W5 **TASK-052**（§11 P-4 命令失败可见化，provisional）`a1c8171`；W6 **TASK-053**（TASK-044 R-03/R-04）`cd57ee4`；W7 **TASK-054**（TASK-043 R-02 改名）`771dbf7`；W8 **TASK-055**（TASK-021 子集①日志/诊断）`0493ea9`；W9 **TASK-056**（子集②缓存·版本·模型清理）`11517ac`；W11 **TASK-058**（自建切片，§11 P-10 退出排空）`414a8e1`。**W10 TASK-057（子集③备份/恢复）交付未集成**（并行会话，冻结 `50c4b1a`）。窗口内 Review 除 W0（Qoder `approved`，用户把 Reviewer 由 DSH 改派）外**全部为 `approved_subagent`（同体审查）**——按协议不是独立批准，**已排 Codex + Qoder 外部 post-hoc 复审（可推翻；原 DSH 槽位 2026-09-19 按用户指示改派 Qoder）**。收口验证：全仓 **905 passed / 6 skipped（共 911 collected）exit 0**（openssl 可用口径 911/0），与 T0 基线 848 collected 相比 +63 例。第三窗口进展如上。所有路径均相对本文档；保留现有 doc 目录及 02 文件名末尾的下划线。

## 原始目标文档（已完整检查）

| 证据编号 | 文档 | 权威职责 | 当前性质 |
|---|---|---|---|
| D01 | [01 功能架构](01_FUNCTIONAL_ARCHITECTURE.md) | 产品能力范围、入口、扩展能力 | 产品 To-Be；§5 的旧代码引用不能证明本仓库实现 |
| D02 | [02 技术架构](02_TECHNICAL_ARCHITECTURE_.md) | 旧分层、技术选型、依赖边界、运行拓扑 | `LEGACY` PySide6/QML 生产基线与迁移参考；当前目标只看 AD-001 |
| D03 | [03 数据模型](03_DATA_MODEL.md) | 实体、字段、数据不变量、持久化归属 | 产品数据需求候选；G06～G13 的最小实现契约由 TASK-002 冻结，SQLite 设计见 TASK-028 |
| D04 | [04 用户流程](04_USER_FLOW.md) | 操作意图、用户流程、对象范围 | 产品流程意图；不指定技术栈或自动释放实现任务 |
| D05 | [05 UI 映射](05_UI_MAPPING.md) | Screen、Panel、Window、动作与 ViewModel 映射 | `LEGACY` QML UI 映射；四页产品结构可供当前授权 Task 选择映射 |
| D06 | [06 Pipeline](06_TRANSLATION_PIPELINE.md) | 命令语义、DAG、Lock、失效、重试与进度协议 | 业务要求保留；Qt/UI Thread 接线为 `LEGACY`，新架构实现按当前 Task 映射 |
| D07 | [07 非功能需求](07_NON_FUNCTIONAL_REQUIREMENTS.md) | 性能、容量、可靠性、安全、Windows 与打包 | 产品级要求保留；PySide6/QML/Qt/PyInstaller 专属机制为 `LEGACY` |
| D08 | [08 验收标准](08_ACCEPTANCE_CRITERIA.md) | 验收预期、证据要求与发布 Gate | 产品验收意图保留；旧技术 Gate 和 PASS/NOT_RUN 结果不继承到新架构 |

TASK-001 已将 D03～D08“基于”列表里的历史长文件名改为上表实际文件；这只恢复当前项目导航，不证明与未提供的历史版本逐字一致。原始引用保存在基线 `496b4ed`。

## 接管与执行文档

| 文件 | 用途 / 何时阅读 |
|---|---|
| [AGENTS.md](../AGENTS.md) | 三 Agent 每次进入项目必读入口 |
| [STATUS](STATUS.md) | 当前授权、开发阶段、用户审核记录 |
| [09 协作协议](09_COLLABORATION.md) | 角色、Git、Task/Handoff/Review 生命周期 |
| [10 当前状态与 Gap Analysis](10_CURRENT_STATE_AND_GAPS.md) | 本次盘点、证据指纹、代码与目标差距、审核清单 |
| [11 架构与交互地图](11_ARCHITECTURE_MAPS.md) | 11 类接管基线视图；目标设计仍不得冒充 TASK-005 最小骨架的实际能力 |
| [12 Roadmap](12_ROADMAP.md) | 阶段 Gate、依赖和范围取舍 |
| [13 验收追踪](13_ACCEPTANCE_TRACEABILITY.md) | D08 条目到计划 Task 的映射；不代表已验收 |
| [14 接管验证](14_TAKEOVER_VERIFICATION.md) | 本次文档自检结果、复现命令与验证边界 |
| [接管自检脚本](verify_takeover.ps1) | 仅适用于初始接管快照；TASK-001 已修改文档与授权，其 Hash/冻结断言不再适用于当前工作区 |
| [TASK-001 检查](../verification/TASK-001/verify.ps1) | 验证文档引用、状态枚举、AC 编号/优先级及修改范围 |
| [TASK-002 最小契约](contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md) | G06～G13、R-011 的冻结语义；后续 Schema/Pipeline/UI/测试共同输入 |
| [TASK-028 统一 SQLite 设计](contracts/TASK-028_UNIFIED_SQLITE_PERSISTENCE_DESIGN.md) | TASK-006/007/008 的 SQLite 收敛设计；实现由 TASK-029 承接 |
| [TASK-029 统一 SQLite 实现](tasks/TASK-029.md) | 按 TASK-028 实现 v2 migration、Library/Page/Region adapter 与原子 Revision seam；已集成 |
| [任务目录](tasks/README.md) | 历史 Task 与当前 Task 的证据索引；当前排期以 REBASELINE_PLAN / STATUS 为准 |
| [Task 模板](templates/TASK.md) | 新任务创建 |
| [Handoff 模板](templates/HANDOFF.md) | 实现 / 实验交付、故障中断交接 |
| [Review 模板](templates/REVIEW.md) | 按固定 commit 独立审查和复审；**必须覆盖 Architecture / Verification 两面**；`code-review` 技能的 **Standards / Spec 为可选视角**（2026-09-18 用户决定取消其与 Spec 的"双轴"强制口径与并行/隔离要求）；建议标注各视角 `executed`/`N/A` |

handoffs、reviews、verification 已包含固定提交的真实交付；目录或文件名本身仍不等于审查/验证通过。

## Source of Truth 按问题区分

| 要回答的问题 | 事实来源 | 不能替代它的材料 |
|---|---|---|
| 当前实际做到了什么 | 当前项目 commit 的源代码、迁移、配置与同 commit 测试证据；工作区变化单独说明 | To-Be 图、旧项目能力表、Agent 自述 |
| 产品应该做什么 | D01/D04/D05；冲突提交用户决策并在相关权威文档修订 | 实现中的偶然行为、测试中的猜测 |
| 架构及数据怎么约束 | D02/D03/D06 按职责管理；已冻结缺口以对应 `doc/contracts/` 文件解释 | 任意 Agent 的私有笔记 |
| 什么算达标 | D07/D08 与可复现 verification 记录 | 仅有测试文件或“本地通过”口头描述 |
| 谁在做什么、可改哪里 | STATUS 的阶段授权 + 单个 Task 文件 | 看板截图、聊天中的认领 |
| 交付了什么 | Handoff 中固定 commit、文件与测试结果 | 分支名称本身、作者概述 |
| Review 是否完成 | 独立 Review 报告绑定的 base/head + Codex 集成验证 | 作者自查或对旧 head 的批准 |

不存在“代码永远胜过需求”或“编号越大越权威”的规则。代码回答实际行为，文档回答目标，两者差异记录为 Gap。D08 明确要求冲突先修订设计，不能用测试替代设计决策（D08 L15）。

冲突处理：记录双方文件/章节/行号 → 在 Gap/Task 标明影响 → Codex提出可审查修改 → 产品范围变化由用户决定 → 在权威文档修订并同步受影响图和 AC。当前发现的问题尚未自动裁决。

## 文档维护规则

- 新事实标明 As-Is（代码/测试）、To-Be（目标）、Proposal（本次建议）或 Unknown（无证据）。
- 原始 01～08 已保存在初始基线；后续仅按已授权 Task 修订。接管报告的 SHA256 是修订前指纹，不是当前文件必须保持的值。
- 架构图与矩阵是派生视图；出现实现后补充 source/test 路径与 commit，才能标为代码生成。
- 代码、测试和文档同一 Task 一起交付。涉及未分配的共享文档，先交 Codex协调写权限。
- 同一个结论只维护一个权威位置，其余位置使用链接；STATUS 管阶段，Task 管进度，Review 管审查结论。
## 2026-10-11 14:01 Asia/Shanghai 最新状态与恢复指针

唯一 Active 产品 Task=P02；当前 Active 子 Task=`P02PRE-R1`，Owner=`Codex /root`、非作者 Reviewer=`DeepSeek Harness`、Integrator/adjudicator=`Codex /root`。Task=`tasks/P02PRE-R1.md`；冻结 manifest=`../verification/P02/p02pre-r1-manifest-20261011.md`；capture script=`../verification/P02/p02pre-r1-capture.ps1`。三者已创建且 parser 检查通过；尚未运行宿主 query，当前等待 DSH Review。用户最新授权已登记，R0 阶段结束；`NOT_SAFE_FOR_R0` 不再阻止 R1。

风险与 Gate 保持 `private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`。唯一 DAG=`REBASELINE_PLAN.md`；checkpoint=`../verification/P02/codex-checkpoint-p02pre-r1-20261011.md`（R1 证据 Review/adjudication 后生成）。

## 2026-10-12 最新 P02 状态与恢复指针

当前唯一 Active Task 与 Gate 见 [STATUS](STATUS.md)；唯一项目 DAG 与中文任务图见 [REBASELINE_PLAN](REBASELINE_PLAN.md)；执行范围/路径/hash/AC 定义见 [P02PRE-R1H Task](tasks/P02PRE-R1H.md)。R2协议独立Review、Codex adjudication和只读precheck/S0已完成；stage/recovery已创建，S1精确delta通过。当前仅待一次受审的三参数File.Replace及post-check；集成、AC4重测和后续Gate尚未PASS。rolling恢复点=`../verification/P02/codex-checkpoint-p02pre-r1h-integration-protocol-review-r2-active-20261012.md`；执行证据=`../verification/P02/p02pre-r1h-integration-execution-20261012.json`。当前系统AC1–AC7=`BLOCKED / NOT_RUN`，Build Gate=`BLOCKED`，Hard Build Barrier=`EFFECTIVE`。用户要求全部授权任务安全收口后关机，当前仍在执行。
