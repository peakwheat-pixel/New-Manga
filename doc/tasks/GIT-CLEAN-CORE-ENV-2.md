---
id: GIT-CLEAN-CORE-ENV-2
title: Core新环境诊断V2至V5范围冻结
kind: research
governance_version: 3
status: proposed
approval: pending_variable_and_environment_freeze
suggested_owner: DeepSeek Harness
owner: null
reviewer: Antigravity
depends_on: []
base_commit: fed1a9cf3295e5e05f7ffd363ac1075bd22e90b1
branch: codex/git-clean-core-env-2
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GIT-CLEAN-CORE-ENV-2
allowed_paths:
  - doc/tasks/GIT-CLEAN-CORE-ENV-2.md
  - verification/GIT-CLEAN-CORE-ENV-2/**
  - G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-CORE-ENV-2/**
---

# GIT-CLEAN-CORE-ENV-2

## 来源与目标

DSH DIAG-1 r1仅给出“Core新环境诊断（V2–V5变量）”标签，当前Task/RESULT/Review没有定义四个变量的取值与环境。Codex决定独立登记本Task，先冻结执行前提，保持proposed，**未释放执行**。不把用户要求“决定是否”推断成盲复跑许可。

## Acceptance Criteria

- [ ] **AC1**：执行前补齐V2/V3/V4/V5的具体变量、控制项、解释器/OS/运行器版本SHA、环境路径、可用性、预期观测、重复预算及停止条件；由Codex登记后才能ready。 <<BLOCKED: V2–V5具体定义与可用环境尚未给出>>
- [ ] **AC2**：在全新有意义变量下获得真实错误码/stderr与PluginService端到端映射证据，区分mock、只读ACL查询与实际grant调用，不回填旧UNKNOWN。 <<BLOCKED: 未释放，禁止任何ACL写入>>
- [ ] **AC3**：仅运行目标参数化用例/新边界测试，保护用户数据；报告实际3组参数与负向对照，不重复已达上限的原条件全套。 <<BLOCKED: 环境与窄运行命令待冻结>>
- [ ] **AC4**：冻结新head/测试输入与SOURCE_PIN，另Appointment独立Review，不沿用fed诊断批准，不自行升级父候选。 <<PARTIAL: 新head/Review均不存在>>

## 允许修改范围与禁止范围

拟议工作空间待Codex创建：G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-CORE-ENV-2/source；不得臆造已有checkout/head。设计只允许本Task/verification登记变量方案；proposed阶段不运行新环境测试或改代码。后续若释放，仅允许隔离副本sandbox诊断/对应测试和本Task产物，不改协议/Schema/依赖或源main。

任何阶段都不push、不done、不改系统ACL（含真实解释器及新路径的/grant、/reset等）、不为刷绿复制旧bundle假称新构建，不用用户真实库、不访问私有漫画、不清理。只读icacls查询不能证明grant失败的真实返回码；模拟returncode不能当真实机器事实。

## 测试要求与释放门槛

planned/NOT_RUN。Owner候选DeepSeek Harness、独立Reviewer Antigravity；变量矩阵和无ACL写入的可执行方案确定后，Codex再分配实际Owner、创建独立仓库并写STATUS/Plan READY。若真实目标Hook必然调用icacls写权限，当前禁令下应BLOCKED，不能执行、假设许可或绕过沙箱。V2–V5标签是待定义项，不在此编造它们原本含义。可先建议只读环境/能力核验，但不能冒充已执行四变量实验。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree/task-env | 尚未创建 | NOT_APPLICABLE | — | — | 未释放执行 |
| source/input | DIAG fed与原三DB pins | PRESERVE_REFERENCED | — | DIAG-50..52/原冻结清单 | 输入只读，不擅自集成 |
| exchange | — | NOT_APPLICABLE | — | — | 未派发 |

## 交付与运行记录

尚无测试/Handoff/新head/Appointment。启动条件为AC1与环境写保护方案冻结，非等待集成Rust Task。新head形成后重新Appointment Antigravity独审（DSH若作为Owner不能自审）。当前下一步仅由Codex补齐变量定义和环境可用性，不存在可直接派发实施的指令。

## 2026-10-25 DSH 接管确认

DSH 接任 Lead / Architect / Integrator（见 `doc/GOVERNANCE_TAKEOVER_2026-10-25.md`）。本 Task 保持 `proposed`，未释放执行；Reviewer 仍为 Antigravity，Owner 候选 DeepSeek Harness 不变。当前无 V2–V5 具体定义、无可执行且不写系统 ACL 的环境方案，因此不得运行、不得盲复跑、不改变 AC。若后续无法在“不修改系统 ACL”约束内取得真实 grant 返回码，本 Task 应保持 BLOCKED 并由 DSH 向用户给出具体可裁决问题，而不是以 mock 或猜测替代。

本 Task 不阻塞干净快照 push 的独立审查；Core 3 组参数失败的环境限制由 DIAG-1 冻结证据说明，不得表述为已通过。
