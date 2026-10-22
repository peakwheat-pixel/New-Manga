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
- [Plan/Status 与历史导航快照](../archive/history/2026-10-12/README.md)：供审计/恢复；当前状态只读活动文件顶部的 current section。

## 2026-10-12 当前状态与恢复指针：H1 P2-1 仍 OPEN；ZCode 证据闭合 Task 已阻塞

当前阻塞中的 Task=`tasks/P02PRE-R1H-R6-ZCODE-H1.md`，状态=`in_review / DSH_REVIEW_CHANGES_REQUESTED`；Owner/Coordinator=`Codex /root`；Reviewer=`DeepSeek Harness`，session=`session-2e6e238c-1814-40b9-b0c6-b253f102296a`，verdict=`CHANGES_REQUESTED (0/0/1/6)`；Adjudicator=`Codex /root`。ZCode 已执行 P2-1 closure Task：CLI session=`sess_c297a288-813f-4dfa-92f1-bae7d37d05b8`，内置 Agent session=`agent_8886fd38-6ba0-41d4-a084-6ee8cf40dc8d`，最终=`blocked / P2-1 OPEN`。Codex 独立复核 15 项输入 pins 与两个 status span 重建；2 项部分候选可定位，13 项仍无合格 raw source，因此 H1 review acceptance 与 X6 继续 blocked。当前 checkpoint=`../verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt6-zcode-handoff-20261012.md`。

无 READY 子 Task。P2-1 Task=`tasks/P02PRE-R1H-P2-1-EVIDENCE-CLOSURE.md`，状态=`blocked / EXECUTED_20261012 / BLOCKED_P2_1_OPEN`；Owner=ZCode，branch=`agent/zcode/P02PRE-R1H-P2-1-EVIDENCE-CLOSURE` @ `343895fb5f0329c0c07a7104ec321b698f967607`，worktree=`C:\Users\49745\.codex\worktrees\p2-p2-1-zcode\New Manga`。报告=`C:\Users\49745\.codex\worktrees\p2-p2-1-zcode\New Manga\verification\P02\zcode-p02pre-r1h-p2-1-evidence-closure-report-20261012.md`（27065 / `DA3C419658AE6FD8FB42A93488666A622FF80DAAD5A565A5E92E0B2615C6AE43`）；Handoff=`...\zcode-p02pre-r1h-p2-1-evidence-closure-handoff-20261012.md`。若继续追查仓库外 CLI harness forensic 输出，需先由用户授权扩大只读范围；X6 不创建。

H1 v2=`PRE_RUN_PASS`（24 checks：23 PASS、1 NOT_VERIFIED，后者为按设计未访问的 `.tmp.driveupload` scope）；attempt1 四文件 pins 与 v2 JSON 引用均匹配，protected file 前后 hash 一致。Live=`main@343895fb5f0329c0c07a7104ec321b698f967607` / tree=`e12bd627c307d4bf3c851dc09d0b82f97c86ec63`，index SHA=`C5CA88842173A8FE4B9C6B6B675528347EECBDC73F85600ABA06F11E3A692B68`；固定 Git 2.52.0.windows.1，受控 status=`1237 NUL / 85373 bytes / D3042D8DE60C33C23B950ABB8B8FD26E6CF8F2A5AAFBF76E0EE12B0793026100`（2026-10-12T13:31:59Z，排除 path 未访问）。较上一 Codex 样本 `1227 / 84670 / EC915022…` 多 10 个本轮 ZCode CLI dispatch 日志；更早历史差异仍 `UNKNOWN / NOT_VERIFIED`，详见 `STATUS.md` 与 H1 Task。

DSH CLI=`0.2.0-rc.2`，无附件探测回答“收到”、exit=0；正式 Review exit=0，报告 SHA-256=`6AAD7750AFABCCD5B159C69F40EF49149E3D3EBB1CA6613CD0FD91FDCB960C19`。Codex verification SHA-256=`7B823A05313DA2B053C76B81744667BF041B8FD9AF0933F1162DCDADFB372515`；adjudication SHA-256=`9D4B95DA5263B0C52A3621748E875760CAAADF153ED5C39BDA5955520DF57232`。ZCode P2-1 报告确认 13 项 raw source 缺失，DSH focused Review=`BLOCKED / NOT_DISPATCHED`；Codex 接受整体 `BLOCKED / P2-1 OPEN`，两项 status span 只作为部分候选。X6 Task not created. Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`。Gate 原值与 waiver 未变。

## 历史快照（ARCHIVE）

本文件压缩前的完整历史导航快照保存在 [2026-10-12 归档副本](../archive/history/2026-10-12/00_INDEX.md)。历史索引不授予当前 Task、DAG 或 Gate 权限；请按需查阅。
