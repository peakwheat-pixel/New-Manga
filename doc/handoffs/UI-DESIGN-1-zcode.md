---
task_id: UI-DESIGN-1
author: zcode
recipient: Codex
base_commit: c6f975d38842487c16491eea67a01cf134c337f8
delivery_head: PENDING_COMMIT_A
status: draft
---

# Handoff：UI-DESIGN-1 AD-001 四页 UI/UX 设计基线

## 交付结果

- 分支：`agent/zcode/UI-DESIGN-1`（worktree `G:/CODEX/New Manga.workspace/worktrees/UI-DESIGN-1`）。
- 唯一设计交付物：`doc/design/AD001_FOUR_PAGE_UI_BASELINE.md`（新建，10 节 + AC 对照附表）。
- 自检脚本与原始日志：`verification/UI-DESIGN-1/selfcheck.ps1`、`verification/UI-DESIGN-1/selfcheck-output.txt`（等价 bash 生成，头部标注）；阻塞登记 `selfcheck-BLOCKED.md`、`commit-BLOCKED.md`；`resource-manifest.json`。
- 本 Handoff 与 Task 文件（`doc/tasks/UI-DESIGN-1.md`）的交付/证据登记。
- delivery_head：`PENDING_COMMIT_A` —— **交付 commit 因权限层阻塞未产生**（`git add` 被 Owner 直跑与子代理共 2 次拒绝，错误原文与待重放命令见 `verification/UI-DESIGN-1/commit-BLOCKED.md`）。全部交付物已就绪于工作树（零 tracked 修改、零删除）；提交后在 Handoff/Task 中回填实际 SHA。

与 Acceptance Criteria 对照：

| AC | 状态 | 说明 |
|---|---|---|
| AC1 四页覆盖 | PASS（自检） | §2–§5 每页含区域职责/布局结构/组件分解/状态矩阵（loading/empty/error/disabled/progress 五态）/交互清单/键盘与焦点路径；结构由 selfcheck (d) 逐项打勾 |
| AC2 导航 Shell | PASS（自检） | §1 冻结 Rail 形态、四页切换不销毁/不停止任务（依据 08 AC-NAV-003 + P11 §7.1/7.2，非 LEGACY）、最小窗口 1024×680 与伸缩行为 |
| AC3 契约绑定表 | PASS（自检） | §6 表 W1–W29，35 个命令/事件名在对应契约文件逐字命中（selfcheck (a) 原始日志） |
| AC4 wire 缺口表 | PASS（自检） | §7 表 G1–G26（26 条），每条含页面/交互/期望语义/当前缺口/建议后续动作；无 mock/私有路径/绕过 IPC 消解 |
| AC5 边界合规 | PASS（自检） | §9 九条逐项自证（SQLite/路径/模型/大媒体/持久化/事件真值/Secret/源文件/不发明 wire） |
| AC6 设计令牌 | PASS（自检） | §8 色彩/字体/间距/密度/圆角/焦点环/DPI 全为自有取值，显式声明与 LEGACY「参考、非绑定」关系 |
| AC7 非目标 | PASS（自检） | §10 十条不做清单（含不裁决 P18 JA/KO 门槛等发布门槛） |
| AC8 自检可核验 | PASS（等价运行）/ BLOCKED（canonical 脚本执行） | selfcheck.ps1 已交付；Owner 会话中 PowerShell 调用被权限层全部拒绝（6 次，错误原文与经过见 `verification/UI-DESIGN-1/selfcheck-BLOCKED.md`）；四项检查由等价白名单 bash 命令完成并全 PASS，原始输出转录入 `selfcheck-output.txt`（头部如实标注生成方式）。canonical 复跑交 Reviewer | `verification/UI-DESIGN-1/selfcheck-output.txt`、`selfcheck-BLOCKED.md` |
| AC9 交付 | PASS（本 Handoff） | 固定 commit 见 delivery_head；Coordinator 集成待做；独立 Review 待做 |

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC8(a) 契约名逐字命中 | 等价 bash：`grep -nEo "<35 names>" doc/contracts/{M2-C1,M2-RC4}_*.md` + 设计文档同名检索（ps1 被拦，见 BLOCKED 记录） | Windows Git Bash（白名单命令），工作树 @ 交付 commit 前（HEAD=c6f975d38 + 未提交交付物） | PASS（35/35 双侧命中；32 M2-C1 + 3 RC4） | `verification/UI-DESIGN-1/selfcheck-output.txt` (a) 段 |
| AC8(b) 本地链接解析 | 等价 bash：`grep -oE "\]\([^)]+\)" 设计文档 \| sort -u` + `ls` 逐一验证 14 个目标 | 同上 | PASS（14/14 解析；0 外链/0 纯锚点） | 同上 (b) 段 |
| AC8(c) 写入范围 | `git diff --name-only HEAD`（空）+ `git status --porcelain`（3 项 untracked，均允许范围；19 禁触路径零命中） | 同上 | PASS | 同上 (c) 段 |
| AC8(d) 结构打勾 | 等价 bash：`grep -nE "^## \|^### "`（10 节 + 四页×六要素）+ `grep -c` W/G 行数（29/26） | 同上 | PASS | 同上 (d) 段 |
| AC8 canonical 复跑 | `powershell -NoProfile -ExecutionPolicy Bypass -File verification/UI-DESIGN-1/selfcheck.ps1` | Owner 会话权限层（6 次尝试含子代理） | BLOCKED（"No permission client configured for Bash"；复跑交 Reviewer，命令与预期见 selfcheck-BLOCKED.md） | `verification/UI-DESIGN-1/selfcheck-BLOCKED.md` |
| AC1–AC7 人工结构审查 | Owner 依 Task AC 逐项核对设计文档 | 同上 | PASS（Owner 自检；独立 Review 待 Reviewer 执行） | 设计文档「附：AC 对照」+ selfcheck-output.txt (d) |
| 产品代码/契约/依赖改动 | 无（本 Task 为纯文档 Task） | — | N/A | git status 全量在 selfcheck-output.txt |

## 接收方式

- 分支：`agent/zcode/UI-DESIGN-1`；worktree：`G:/CODEX/New Manga.workspace/worktrees/UI-DESIGN-1`。
- 复现自检：`powershell -NoProfile -ExecutionPolicy Bypass -File verification/UI-DESIGN-1/selfcheck.ps1`（exit 0 = 全 PASS；重新生成 selfcheck-output.txt）。**Owner 会话中该命令被权限层拒绝（6 次），等价 bash 运行已 PASS，canonical 复跑由 Reviewer 执行**（见 selfcheck-BLOCKED.md）。
- 前置条件：无新增依赖、无 schema、无产品代码改动。
- **待 Coordinator 先行处理**：在权限可用的会话重放提交命令（见 `verification/UI-DESIGN-1/commit-BLOCKED.md`）并回填 delivery_head 与 Canonical Evidence 的 commit 列。
- Codex 集成时需要做的检查：
  1. 指派独立 Reviewer（不得为 zcode）审设计文档与自检日志；
  2. 核对 §6 绑定表引用与 §7 缺口表是否与契约 HEAD 一致（契约自 c6f975d38 起若有新 revision，需重跑 selfcheck 并人工复核新增/变更 wire 是否影响绑定）；
  3. 决定 G1–G26 的契约/host Task 规划（缺口已按「建议后续动作」分类）；
  4. 本设计通过后释放 P12/P14/P15/P17 实现 Task（其范围冻结引用本文档）。

## 下一任务建议（必填）

- Task ID / 标题：UI-DESIGN-1 独立 Review（REVIEW-UI-DESIGN-1，按 [Review 模板](../templates/REVIEW.md)）。
- 推荐 Agent / Reviewer：DeepSeek Harness（独立于 Owner=zcode，未参与本设计；符合「不得审核自己实现的变更」）。
- 推荐原因与前置依赖：本 Task 全部 AC 的独立验收；前置=本 Handoff 的固定 commit。
- Recovery point：仓库 `G:/CODEX/New Manga`，branch `agent/zcode/UI-DESIGN-1`，base `c6f975d38842487c16491eea67a01cf134c337f8`，head=delivery_head（回填后）；无需新 worktree（Review 只读）。
- 允许修改路径：`doc/reviews/`（或项目约定位置）与 `doc/tasks/UI-DESIGN-1.md` 的 Review 登记行。
- 禁止范围与新增授权条件：不改设计文档本身（问题经 Review 记录、由 Owner 在 r1 返修 commit 处理）。
- 交付物：Review 报告（approved / changes_requested + 逐条证据）。
- 验证命令、环境与完成 Gate：阅读 `doc/design/AD001_FOUR_PAGE_UI_BASELINE.md` + 复跑 selfcheck.ps1；Gate=逐 AC 独立判定。
- 可直接转发给 Agent 的指令：「你是 UI-DESIGN-1 的独立 Reviewer。读取 doc/tasks/UI-DESIGN-1.md 的 AC1–AC9，逐项审查 doc/design/AD001_FOUR_PAGE_UI_BASELINE.md；复现 verification/UI-DESIGN-1/selfcheck.ps1 并核对原始日志；特别核验：§6 每条契约引用逐字可检索、§7 缺口未以 mock/私有路径消解、LEGACY 未被单独作为要求依据、§9 边界自证与 AD-001/契约一致。输出 Review 报告（approved / changes_requested），不改设计文档。」

Review 通过后的下一建议（Codex 裁决）：释放 P12/P14/P15/P17 中首个实现 Task（建议 P14 工作台，因其 wire 面最完整——W5–W17 已冻结且有 client 素材；或按 Coordinator 排序）。

## 风险与遗留

- **canonical selfcheck.ps1 未在 Owner 会话执行**：权限层拒绝全部 PowerShell 调用（见 selfcheck-BLOCKED.md）；Reviewer 复跑是权威确认。
- §6 表行号引用基于 c6f975d38 的契约文件；契约后续 revision 会漂移行号（命令名仍可逐字检索）。selfcheck 以名字检索为准，行号仅人读辅助。
- G15（Run 发现）、G17（事件转发面）、G19/G20（导出 host command）直接阻塞 P14/P17 的完整体验；P12 被 G6 阻塞（导入来源选择 command）。建议 Coordinator 优先规划 host/契约 Task。
- 设计令牌为自有取值，未经视觉走查（无 REQUIREMENT 来源要求走查；如用户要求可另释放视觉验证 Task）。
- 无破坏性操作；回退= revert 交付 commit。

## 实验附录（仅实验任务）

不适用（纯设计文档 Task）。
