# 治理接管记录：Codex → DeepSeek Harness（2026-10-25）

## 1. 授权与效力

用户于 2026-10-25 正式授权并立即生效：从本次接管起，将 New Manga 项目中原属于 Codex 的全部项目管理与集成权限移交给 DeepSeek Harness（DSH），由 DSH 主持后续工作并完成安全 push。

移交范围：

- 任务释放与范围冻结、Agent 分配；
- 契约与架构裁决；
- Review Appointment、审查处置；
- 集成验证、资源处置裁决；
- Task 生命周期管理；
- 最终 push 权限。

本记录是角色变化的唯一新增授权记录。旧文档中「仅 Codex 可批准/集成/关闭/推送」的身份限制，以本次用户裁决为准；历史署名、冻结 Review、日志、manifest 和 evidence pin 保持原字节。

## 2. 角色变更后的边界

| 角色 | 变更后职责 |
|---|---|
| DeepSeek Harness | Lead / Architect / Integrator；承接上述全部项目管理与集成权限；不得审核自己实现的变更 |
| Codex | 按 DSH 分配的协作 Agent；承担实现、诊断、测试或独立 Review；不再保留项目级审批、否决或最终集成特权 |
| ZCode | 既有职责保留：独立 Feature、长任务、React/Tauri UI/UX 设计及实现主责 |
| Antigravity | 既有职责保留：通用编程实现、测试或基础设施 Task |
| Qoder | 2026-10-08 用户裁决退出本项目，不变 |

独立审查规则：DSH 不得独立审核自己实现的变更；需要独审时，由 DSH 指定未参与实现的 ZCode、Antigravity 或 Codex 担任 Reviewer。Owner 与 Reviewer 必须不同。

## 3. 接管时仓库事实

- 唯一真实仓库：`G:/CODEX/New Manga`。
- branch `main`，HEAD `349e61faff5f93067af5d4ce2d9e394e0d665b8c`。
- Git common directory：`.git`；`git worktree list` 仅 1 个注册 worktree（主 checkout）。
- `origin`：`https://github.com/peakwheat-pixel/New-Manga.git`；远端仅有 `refs/heads/main = 6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`；本地 `main` 未设置上游跟踪。
- 接管前工作区：3 个已跟踪文档存在他人（Codex）在途修改（`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`），另有 20 个未跟踪项（当前 Task 文件与证据、`audit/`、6 个 P04 日志）。按用户要求，他人未提交内容不纳入本次接管提交；其原位内容与归属保留。
- 当前非终态 Task：`GIT-CLEAN-PUBLICATION-1`、`GIT-CLEAN-RUST-ISOLATION-1`、`GIT-CLEAN-RUST-CAPACITY-DESIGN-1`、`GIT-CLEAN-PUBLICATION-DIAG-1`、`GIT-CLEAN-CORE-ENV-2`、`NEW-MANGA-V1-FULL-AUDIT`、`V1-RELEASE-SIGNING-1`。
- 最新关键 Review：父候选 `e34a90d001cce1fa966aec7d2b032bb5ad1cf148` 的 `dsh-review-r1.md`（blocked）；Rust r2 `1829a38a41587a0d680001a40d206886afb0911d` 的 `r2/dsh-review-r2.md`（blocked）。两份 Review 均保持原字节，不改写为通过。

## 4. 本次实际文档变更

| 文件 | 变更性质 |
|---|---|
| `AGENTS.md` | 写明 DSH 为 Lead / Architect / Integrator；Codex 降为协作 Agent；更新角色、集成、自审禁止与 2026-10-25 用户裁决 |
| `doc/09_COLLABORATION.md` | 角色表、任务释放/领取/集成/done 权限、Review Appointment、§5.1 下一任务、§6 集成、§7 推送规则迁移到 DSH；新增独立审查边界 |
| `doc/00_INDEX.md` | Review 结论权威改为 DSH adjudication；新增本接管记录导航 |
| `doc/AI_COORDINATION.md` | Mainline Integrator 与 Knowledge Refresh Owner 迁移到 DSH；新增 2026-10-25 交接记录；历史交接原文保留 |
| `doc/WORKSPACE_GOVERNANCE.md` | worktree 移除条件、远端/push 授权、STATUS/PLAN 预算口径同步 |
| `doc/templates/TASK.md`、`REVIEW.md`、`HANDOFF.md` | 释放、集成、done、Reviewer 指定、收口责任迁移到 DSH |
| `doc/tasks/README.md` | 当前任务导航按接管后事实刷新 |
| `doc/tasks/GIT-CLEAN-PUBLICATION-1.md` 等当前 Task | 追加接管说明、Reviewer 改派与授权依据；不改历史证据字节 |
| `doc/STATUS.md`、`doc/REBASELINE_PLAN.md` | 同步接管后的当前状态、Gate 与 push 条件（在途内容归属见 §3） |

## 5. 治理工具身份硬编码核查

检查对象：`tools/governance/check.ps1`、`tools/governance/task_ledger.py`、`tools/governance/task_liveness.py`、`tools/governance/audit_tasks.py`、`.orchestrator/agents.json`、`.orchestrator/policy.yaml`、`.orchestrator/runtime.json`、`.orchestrator/governance-write-scope.json`。

结论：**未发现把 Codex 身份硬编码为唯一授权主体的治理工具**。

- `check.ps1` 只校验当前权威指针、相对引用、目标架构哨兵、体量预算、canonical evidence pin 与 lifecycle v3 的 AC 标记；不读取任何 Agent 身份字段，也不要求 Codex 署名。唯一 `codex` 字样是 URL scheme 过滤（`codex://`）。
- `task_ledger.py`、`task_liveness.py`、`audit_tasks.py` 只读取 Task frontmatter、git 可达性与状态计数，不校验 Owner/Reviewer 身份。
- `.orchestrator/agents.json` 与 `policy.yaml` 采用动态角色与 `reviewer_must_not_be_owner` 规则，未固定 Agent 职责；`.orchestrator/runtime.json` 的 active coordinator 已是 `dsh`。
- 因此本次角色迁移不需要修改治理工具代码；仅文档级授权主体需要更新。机器检查结果不能替代 Reviewer/DSH 的语义裁决。

## 6. 治理检查结果

实际执行（2026-10-25，工作区 `G:/CODEX/New Manga`）：

```text
pwsh -NoProfile -File tools/governance/check.ps1
Governance scope: 13 current documents; no historical directory scan.
Task: doc\tasks\GIT-CLEAN-PUBLICATION-1.md
WARN: 存在 7 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：2849 bytes / 30 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6998 bytes / 64 lines
Governance check: PASS (3 warnings)     EXIT=0
```

另对全部 7 个非终态 Task 逐个执行 `-TaskPath`：`GIT-CLEAN-PUBLICATION-1`、
`GIT-CLEAN-RUST-ISOLATION-1`、`GIT-CLEAN-RUST-CAPACITY-DESIGN-1`、
`GIT-CLEAN-PUBLICATION-DIAG-1`、`GIT-CLEAN-CORE-ENV-2`、`NEW-MANGA-V1-FULL-AUDIT`、
`V1-RELEASE-SIGNING-1` 均为 `PASS`（3 warnings；V1-RELEASE-SIGNING-1 为 4 warnings），
exit 0。未发现由角色迁移引入的治理检查失败。

提交边界：本记录与角色/模板文档进入 DSH 接管基线提交；`doc/STATUS.md`、
`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` 与 6 个当前 Task 文件含他人（Codex）
在途未提交内容，按用户要求不纳入该提交，保留原归属与工作区 diff。治理检查在
工作区上通过，不代表这些未提交内容已被提交。

## 7. Push 授权与条件（接管后）

用户授权 DSH 在候选满足既定推送条件并完成独立审查后执行 push，无须再等待 Codex 批准。执行边界：

- 目标：干净源码快照候选 `e34a90d001cce1fa966aec7d2b032bb5ad1cf148`，推送到 `origin` 的**新分支**；不推送 `main`、不设置上游、不 force、不覆盖远端 `main`；
- 材料：169 个私有 JPEG 及其 338 个禁止对象不得出现在推送对象中；源 main 历史与本地对象保持原位；
- 审查：任何新交付 head 重新 Appointment Review；已有 blocked 证据不得改写为通过；
- 记录：远端、目标分支、推送 commit、实际命令结果与远端 SHA 核验写入本次交付记录。

## 8. 未授权事项

本接管不授权：改写 `main` 历史、force push、覆盖远端 `main`、传播私有漫画及其历史对象、修改系统 ACL、删除/清理素材、refs 或 worktree、把 blocked/失败证据改写为通过、无边界新增 Task 或推送门槛。

## 9. 接管签署

- 执行者：DeepSeek Harness（Lead / Architect / Integrator）。
- 生效时间：2026-10-25（Asia/Shanghai）。
- 本记录新增字节；此前历史文件保持原字节。
