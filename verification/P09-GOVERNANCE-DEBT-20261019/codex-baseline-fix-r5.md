# Checker 基线与 GOV-PLAN-BUDGET-1 决定（r5）

## 2.1 决定：A，首次将当前 checker 原样纳入版本控制

`tools/governance/check.ps1` 是待维护对象本身；只入库 SHA-256 指纹无法让给定 HEAD 包含实现，不能形成 checker 的可复现 `base → delivery` diff。DSH 在有效 lease 下将当前文件作为首版提交，不改脚本内容。

- 当前磁盘 SHA-256：`25477A5D0554742526AB83C7CF9453125AD20047788CE17BED78C286D9996466`（275 行均为 LF；添加属性后预期字节内容不变）。
- 同时在 `.gitattributes` 增加 `tools/governance/check.ps1 text eol=lf`。固定 LF 让 Windows checkout 与此 hash 稳定对应；该文件已有 2 个 tracked LF 脚本作项目惯例。
- 建议提交信息：`chore(governance): track checker baseline`。提交只包含 checker 与该属性行。

## 2.2 隔离 worktree

经 `git worktree list --porcelain` 和路径检查，`G:/CODEX/New Manga.workspace/worktrees/GOV-PLAN-BUDGET-1` 不存在；`agent/deepseek/GOV-PLAN-BUDGET-1` 分支也不存在。确认采用这两个名称。必须隔离：主 checkout 有大量既存 dirty/untracked 内容，而 Task 修改共享治理 checker；隔离能让 base/delivery diff 与 DSH 交付边界清晰。先提交 checker 基线，再从该提交创建 worktree；因此 worktree HEAD 确实含 checker。Task 的 `base_commit` 固定为此 checker 基线提交。

## 2.3 `doc/REBASELINE_PLAN.md` 完整替换内容

```markdown
# Project Rebaseline Plan —唯一DAG；运行见[STATUS](STATUS.md)。范围/裁决见[REPORT](../verification/PROJECT-ROADMAP-RELEASE/REPORT.md)。
|节点/目标|依赖|状态|
|---|---|---|
|P01 台账 / P03 SFX入口 / P05 契约注记|—|done|
|P02 WebView|P08|限定关闭|
|P04 并发验收|P22|done|
|P06 GC补证|—|**done**（集成 d3342895）|
|P08 产品范围|—|done|
|ARCH-DOC-REBASELINE|P08|ready / integrated（AC7 消费者裁决待做）|
|P09 导入Core|P08/DOC|closed_with_limitations（集成 c6a7339f；AC3 由下项回补）|
|P09-AC3-DELETE-1|P09|closed_with_limitations（R3 changes_requested；HARDEN-1 接手）|
|P10 凭据通道 / P11 长任务契约|P08|**done**（c46c0df0 / ceca5721）|
|P12 书架导入|P09/UI/C1/FU2|**done**（集成 465e3001e）|
|P13 后台恢复|P09/P11/P13-C1|**done**（集成 8d7cad13）|
|P14 工作台|P13/UI|**done**（集成 2dc14cdd1）|
|P15 设置/Core/host|P15-C1/P10/UI|done（含 FU、HOST-1/2）|
|P16 阅读导出Core|P08/P13/C1|**done**（集成 e1be3082）|
|P17 阅读导出UI|P16/DOC/UI|**done**（集成 f18b7fe8f）|
|P15-C1 设置面契约|P10|**done**（集成 f07221313）|
|P18 JA/KO质量|P10/P13/DOC|closed_with_limitations（AC2门槛、AC5阻塞）|
|P19 四页安全E2E|P12/14/15/17/18/P04|closed_with_limitations（4c860d882）|
|P20 Windows发布|P19/P03/P06/DOC|ready|
|P20-MEM-OPT-1|P20|closed（AC1 完成；AC2 经调阈值消解）|
|P20-ISOLATION-1|P20|in_review|
|P20-AC4-FPS-1|P20|closed_with_limitations（AC3 PASS；AC5 依裁决）|
|GOV-DEBT-CLEANUP-1|P19/P20|blocked（待用户裁决）|
|GOV-DEBT-CLEANUP-2|—|approved（AC6 的 P19-UI-FIX-1 格式债务；AC7 的 61 项归属未结）|
|P20-CLOSE-BOUND-1|P20-ISOLATION-1|closed_with_limitations（R6）|
|P20-CLOSE-BOUND-HARDEN-1|P20-CLOSE-BOUND-1|closed_with_limitations|
|P09-AC3-DELETE-HARDEN-1|P09-AC3-DELETE-1|closed_with_limitations（未集成）|
|P09-PREVIEW-LIFECYCLE-RECLAIM-1|P09-AC3-DELETE-HARDEN-1|closed_with_limitations（AC6 未满足；未集成）|
|GOV-PLAN-BUDGET-1|—|ready|
|RUST-ENV-BASELINE-1（P20-CLOSE-BOUND-1）/ P07交互补缺（P02）/ P21旧栈归档（P20+另授权）|—|proposed（P07/P21可选）|
|P22 响应归属|P22-REBASE-1|已集成；P04 不放行，H1/P2-1/13 与 BC-AC5 缺项保留。已完成见各节点行。|
READY 节点：ARCH-DOC-REBASELINE、P20、GOV-PLAN-BUDGET-1。`in_review`：HARDEN-2。done：**33 项**。
```

Plan 共 2432 UTF-8 bytes / 35 lines（预算 2500 / 35）。保留 `GOV-DEBT-CLEANUP-2` approved 行原文，不登记 29 个暂缓 Task。首行删去的恢复日期及 P22 集成摘要仍可由其指向的 ROADMAP REPORT 与 P22 节点行追溯；RUST/P07/P21 压成同一 DAG 行，逐项依赖、P07/P21 可选性均保留在该行。

`doc/STATUS.md` 追加以下一行（57 UTF-8 bytes；含 LF 共 58 bytes，正好用完当前余量）：

```markdown
- READY：[GOV-PLAN-BUDGET-1](tasks/GOV-PLAN-BUDGET-1.md)
```

## DSH 接下来按此顺序执行

1. 在有效 lease 下确认 checker hash 仍为上述值、确认暂存区变更并行检查既有 `.gitattributes`；不覆盖其他人的改动。仅追加属性行 `tools/governance/check.ps1 text eol=lf`，不改 checker。
2. 执行 `git add -- .gitattributes tools/governance/check.ps1`；检查 `git diff --cached --check` 与 `git diff --cached -- .gitattributes tools/governance/check.ps1`，确保 staged diff 只含该属性行和 checker 原文。用 `git commit --only -m "chore(governance): track checker baseline" -- .gitattributes tools/governance/check.ps1` 提交，避免带入主 checkout 的其他暂存内容。记录 commit，复核 `git show <commit>:tools/governance/check.ps1` 与工作树文件一致、SHA-256 未变。
3. 以刚记录的 checker commit 创建隔离 worktree：`git worktree add -b agent/deepseek/GOV-PLAN-BUDGET-1 "G:/CODEX/New Manga.workspace/worktrees/GOV-PLAN-BUDGET-1" <checker-commit>`。确认 worktree HEAD 含 `tools/governance/check.ps1`，并把该 commit 记为 Task 的 `base_commit`；不要从当前 dirty 主 checkout 复制工作树状态。
4. 按以上 Plan 与 STATUS 片段登记 DAG/READY 指针；从 r4 已裁定范围生成 `doc/tasks/GOV-PLAN-BUDGET-1.md`，固定 Owner DSH、branch/worktree、`base_commit`、允许路径与证据目录。先运行只读 `pwsh -NoProfile -File tools/governance/check.ps1` 核验权威指针与预算；若 STATUS 精确计数超限或出现既有状态漂移，停下报告，不压掉其他内容。
5. 确认 Task 释放信息、worktree HEAD 与 base 一致后，DSH 才在隔离 worktree 执行已释放的预算修改；保留完整 diff、Handoff 与 AC 证据，Reviewer 按 r4 分配独立审查。基线入库和 Task ready 本身不代表交付通过。

## 本次工作区状态对比

动手前相关路径：`?? tools/governance/check.ps1`；r5 目标文件不存在，`.gitattributes`、Plan、STATUS 无本次改动。动手后相关路径：checker 仍为原有 `??`，新增 `?? verification/P09-GOVERNANCE-DEBT-20261019/codex-baseline-fix-r5.md`；其余相关路径未改。本次未执行 Git 写命令。
