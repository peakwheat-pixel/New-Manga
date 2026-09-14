---
task_id: TASK-003
author: DeepSeek Harness
recipient: Codex
base_commit: 9472df5c44a1bad24cda639201b0824a9ea5eecc
delivery_head: 6caefe1201428ad9cf0636173567c8cc0b7aba80
status: awaiting_review
supersedes: doc/handoffs/TASK-003-588383f.md
---

# Handoff：TASK-003 复审修订（R-001～R-010）

交付日期：2026-09-14（Asia/Shanghai）。本轮只处理 Codex 首次 Review（`f56bef4`，decision=`changes_requested`，P1×7 / P2×3）的 R-001～R-010；未实现功能、未改产品要求、未合并 master。Owner 为 DeepSeek Harness，Reviewer 为 Codex——**本 Handoff 不是自我批准**。

## 固定审查对象

- `base_commit = 9472df5c44a1bad24cda639201b0824a9ea5eecc`
- `reviewed_head = 6caefe1201428ad9cf0636173567c8cc0b7aba80`（**取代**首次交付 head `588383f`）
- 首次 Review 报告：`doc/reviews/TASK-003-588383f.md`（commit `f56bef4`）
- 作者分支：`agent/deepseek/TASK-003-verification-spec`；工作区 `G:/CODEX/New Manga.worktrees/TASK-003-deepseek`

## 提交链

~~~text
9472df5 docs: authorize TASK-003 verification design        （基线）
fe87c53 docs: bind TASK-003 execution baseline
588383f docs(TASK-003): add acceptance and fixture spec, close F-08   （首次交付，已被 Review 拒绝）
c55ec27 docs(TASK-003): hand off 588383f for review         （首次元数据）
f56bef4 docs(review): request changes for TASK-003 588383f  （Codex Review，不在作者分支）
6caefe1 docs(TASK-003): address review findings R-001..R-010（本次内容交付 = reviewed_head）
~~~

本次内容改动 4 个文件（`+332/−141`）：验收规范、Fixture 清单、D13、验证脚本。D02/D04/D11 的 F-08 状态边**未再改动**（`git diff 9472df5 6caefe1 -- D02 D04 D11` = 3 行新增、0 行删除）。

## Finding 处置

| Finding | 处置 | 证据 |
|---|---|---|
| R-001 P1 | **fixed** | 方法规范删除全部可变结果：§8 三张表不再有"当前结果"列，原"当前状态"小节整体移除；新增"结果真值的唯一位置"规则（只由 D13 或绑定 commit 的 Handoff/Review 维护）；§1 冲突条款收窄为"验收目标与优先级以 D08、质量数值以 D07/D08、产品范围与用户流程按索引归 D01/D04/D05" |
| R-002 P1 | **fixed** | `ACG-SYNC` 结果改为单一合法枚举 `NOT_RUN`；契约批准（`b1b3f5d..885c9a9`、集成 `7927169`）移入证据，并明确"D08 §67 要求正式实现满足契约 §2～§10 并通过 §11 向量后 Gate 才可通过"；脚本拒绝任何非枚举结果与 `PASS（契约层）` 复合值 |
| R-003 P1 | **fixed** | 新增 7 个全局规范标识（`ACG-AUTOTEST`§68、`ACG-UITEST`§69、`ACG-VISUAL`§70、`ACG-BENCH`§71、`ACG-DATASAFE`§72、`ACG-RELEASECHECK`§73、`ACG-READY`§76）与 7 个扩展标识（`ACG-EXT-IMPORT/PLUGIN/FONT/SAKURA/DETECT/CONTRACT/NFR`）；§74/§75 明确列为非验收项并给出理由；标识总数 24，规范与 D13 两表逐行一致 |
| R-004 P1 | **fixed** | §6.1 每项计时起止事件表；§6.2 单调时钟 + P95/P50 固定为 nearest-rank（N=20→第19/10个，N=5→第5/3个）；§6.3 异常样本规则（原样保留、仅环境异常可 `excluded` 并补跑、不足则 `NOT_RUN`、禁止重跑覆盖）；§6.5 冷启动专用规则（不套用通用预热、逐样本冷状态、无法重置缓存记 `BLOCKED`） |
| R-005 P1 | **fixed** | §8.5 逐字列出 D08 §53 全部 13 步：启动 → 默认书架 → 创建 Book → 创建 Chapter → 导入 Page → 进入工作台 → 执行至少一个 Mock / Local Pipeline → 保存 → 阅读 → 导出 → 关闭 → 再启动 → 数据仍存在；脚本逐词校验 |
| R-006 P1 | **fixed** | §9 的 AC-CAP 行改为显式路由 `AC-CAP-001→DS-E`、`002→DS-B2`、`003→DS-C`、`004→DS-D`；Manifest 新增 `DS-B2`（≥1000 Page，对应 AC-CAP-002 的 1000 Page Chapter，区别于 D07 §99 的 500 Page DS-B）；脚本校验四条路由与四个数据集均存在 |
| R-007 P1 | **fixed** | Manifest 全部 20 项状态改为 `missing`（未取得），Hash 全部 `NOT_AVAILABLE`；新增来源类型规则（generated / acquired）与 `available` 三条件（许可非待定 + 真实 64 位 SHA256 + 可复现生成方式）；脚本拒绝 `available + 待定许可`、拒绝非 SHA256 的 available、拒绝 missing/planned 携带 Hash |
| R-008 P2 | **fixed** | 脚本改为**逐行解析**两张权威表的 `ACG-*` 行：分别拒绝规范与 D13 内的重复行、要求两集合完全一致、要求每个标识在 D13 恰好一行；不再使用 `Select-Object -Unique` 掩盖重复 |
| R-009 P2 | **fixed** | F-08 护栏同时统计新增行与删除行：三文件相对基线必须 **0 删除**、恰好 3 新增且全部匹配授权状态边；已用合成样本验证检测有效（见下） |
| R-010 P2 | **fixed** | 删除 `ACG-PRIVACY` 中未经批准的"首次使用提示"，仅保留 D08 §57 已定义的"Provider 设置页说明上传给远程 Provider 的数据类型"；脚本拒绝该短语回归 |

## 验证证据

环境：Windows `10.0.26200`、PowerShell `7.6.6`、Git `2.52.0.windows.1`。

| 检查 | 命令 | 环境 / commit | 结果 |
|---|---|---|---|
| 交付验证脚本 | `pwsh -NoProfile -File ./verification/TASK-003/verify.ps1` | `6caefe1`（干净工作区） | **PASS，退出码 0**，12 条输出 |
| 空白错误 | `git diff --check 9472df5 6caefe1 --` | 同上 | PASS，退出码 0 |
| 工作区洁净 | `git status --short --branch` | 同上 | PASS，仅分支行 |
| 变更范围 | `git diff --name-status 9472df5 6caefe1` | 同上 | 9 路径，全部在 allowed_paths；D08/AGENTS/STATUS 未改 |
| F-08 增量 | `git diff 9472df5 6caefe1 -- D02 D04 D11` | 同上 | 3 新增、**0 删除**，全部为 `Blocked → Cancelled` |

脚本实际输出（12 条）：

~~~text
PASS: changed paths authorized; TASK-001/002 unchanged; other 24 tasks frozen
PASS: D08 unchanged; all 185 AC IDs, priorities and titles intact and unique
PASS: 24 unique ACG identifiers (10 topic + 7 global + 7 extension), rows unique in both tables
PASS: every ACG row carries exactly one legal result enum value
PASS: method spec keeps no result copy; result truth stays in D13 / commit-bound reports
PASS: fixture manifest fields/states, 20 rows, hash discipline and licence rule (0 available)
PASS: AC-CAP-001..004 each route to an existing dataset (DS-E/DS-B2/DS-C/DS-D)
PASS: ACG-SMOKE documents the full D08 §53 flow including restart persistence
PASS: F-08 is exactly one added edge per file in D02/D04/D11, with no deletions
PASS: result enum, full performance protocol, UNAPPROVED_THRESHOLD and scope discipline intact
PASS: 532 local links and all code fences valid
PASS: git diff --check; owner-authored guards only, independent Review still required
~~~

### 护栏负向测试（针对 R-007/R-008/R-009 的护栏有效性）

以合成样本验证检测逻辑（未修改任何被审文件）：

| 场景 | 输入 | 期望 | 实测 |
|---|---|---|---|
| F-08 删除检测 | 真实 diff + 注入 1 条 `-    Running --> Completed` | 检出 1 条删除 | 1 ✓（无注入时为 0） |
| available + 待定许可 | `acquired / 待定 … available` | 拒绝 | `REJECT: unconfirmed licence` ✓ |
| available + 无 Hash | `… NOT_AVAILABLE … available` | 拒绝 | `REJECT: not a real SHA256` ✓ |
| available + 短 Hash | `… deadbeef … available` | 拒绝 | `REJECT: not a real SHA256` ✓ |
| available + 真 SHA256 | 64 位小写十六进制 | 接受 | `ACCEPT` ✓ |
| ACG 复合结果值 | `PASS（契约层）：…` | 拒绝 | 被枚举检查拒绝 ✓ |
| 规范结果列（首列/中间列/末列） | `\| 当前结果 \|`、`\| a \| b \| 当前结果 \|` | 全部拒绝 | 三者均命中 ✓（散文提及与正常表不误报） |

**该脚本由 Owner 编写，是回归护栏，不构成独立批准。**

## 未完成项

| 项 | 状态 | 原因 |
|---|---|---|
| 产品 / 应用端到端测试 | `N/A` | 仓库无应用源码与可执行产物 |
| 性能与容量实测 | `NOT_RUN` | 无实现、无 ENV-B/ENV-D 基准数据 |
| 模型质量评估 | `BLOCKED` | 素材 20 项全部 `missing`、阈值 `UNAPPROVED_THRESHOLD` 未获批 |
| 素材生成与 Hash 登记 | `NOT_RUN` | 属后续已授权 Task |
| Mermaid 渲染校验 | `NOT_RUN` | 仅围栏结构检查 |
| D08 §68～§76 的实际覆盖验证 | `NOT_RUN` | 标识与路由已建立；实际测试属 TASK-022/026/027 |
| 独立复审与集成 | 待 Codex | `integration_commit` 仍为空，Task 不得 done |

## 风险与遗留

- 24 个 `ACG-*` 标识是**新增的稳定标识层**，本身不是产品 AC，也没有独立 P0/P1；阻塞性仍由 D08 对应章节决定（§72/§76 的阻塞项已在规范 §8.3 注明）。
- `AC-CAP-002` 需要 ≥1000 Page 的 Chapter，而 D07 §99 的 Dataset B 只有 500 Page；本轮以新增 `DS-B2` 解决，未修改 D07/D08 的任何数值。
- 素材仍全部未取得；在素材与许可确认前，依赖真实素材的质量结论只能记 `BLOCKED`/`NOT_RUN`。
- 首次 Review 的实际修订内容（F-08）已经通过，本轮未再触碰该三处状态边。

## 接收与复现

唯一 Git common directory：`G:/CODEX/New Manga/.git`；Owner worktree `G:/CODEX/New Manga.worktrees/TASK-003-deepseek`。

~~~powershell
git diff --stat 9472df5 6caefe1
git diff --check 9472df5 6caefe1 --
pwsh -NoProfile -File ./verification/TASK-003/verify.ps1
~~~

复审需覆盖 R-001～R-010 的 disposition、单一权威边界（D08 / 方法规范 / D13 / Fixture）、`ACG-*` 标识与执行路由的完整性、性能协议（estimator/计时边界/异常样本/冷启动）、Fixture 生命周期与许可防线、护栏的负向能力，以及 F-08 是否仍为"仅一条状态边且无删除"。P0/P1 未解决不得批准；P2 必须记录 disposition。
