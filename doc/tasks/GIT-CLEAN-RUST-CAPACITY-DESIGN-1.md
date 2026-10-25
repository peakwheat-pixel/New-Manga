---
id: GIT-CLEAN-RUST-CAPACITY-DESIGN-1
title: Rust真实容量注入与残余测试收紧设计
kind: design
governance_version: 3
status: ready
approval: dsh_takeover_continues_2026-10-25
suggested_owner: ZCode
owner: ZCode
reviewer: ZCode
depends_on: []
base_commit: 1829a38a41587a0d680001a40d206886afb0911d
branch: codex/git-clean-rust-capacity-design-1
worktree: G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-CAPACITY-DESIGN-1/source
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GIT-CLEAN-RUST-CAPACITY-DESIGN-1
allowed_paths:
  - doc/tasks/GIT-CLEAN-RUST-CAPACITY-DESIGN-1.md
  - verification/GIT-CLEAN-RUST-CAPACITY-DESIGN-1/**
  - G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-CAPACITY-DESIGN-1/**
---

# GIT-CLEAN-RUST-CAPACITY-DESIGN-1

## 来源与目标

用户目标“完成push”、持续auto及ZCode归属；DSH Rust r2在1829a38给blocked，R2-F01..05须处理。Codex释放本设计切片；输入是独立artifact及Review，不要求先集成，depends_on为空。父publication及Rust Task保持in_review/blocked，不改AC、不批准集成。当前只交可核查设计，冻结可实现的下一实施范围；不能用设计代替真实32峰值。

## Acceptance Criteria

- [ ] **AC1**：根据实际spawn/round_trip/Drop/cancel/reaper/holder/track代码画清资源与时序链，逐分支说明为什么当前20真实pipe峰0、32目标需要何种故障前提，引用具体行/符号。 <<PARTIAL: planned，尚无设计交付>>
- [ ] **AC2**：提出不改生产语义的可实现注入方案，区分真实worker/管道、test-only观察或调度、人工阻塞替身，明确accepted/refused/holder及32边界证据、120s+30s预算、清理与停止条件；若结构性不可达则给可证伪机制与对照，保留AC3 BLOCKED，不自动改AC。 <<PARTIAL: planned，方案真实性待审>>
- [ ] **AC3**：R2-F02..05各给最小修订及有意义测试计划：精确timeout/unfinished硬断言；guard正常/异常收尾和Arc所有权；实际线程join账本与tasklist状态；fail-closed直接分支/owner mismatch。覆盖所有调用者与不改变生产的证明。 <<PARTIAL: planned，未实施>>
- [ ] **AC4**：独立新head只增加DESIGN/HANDOFF与来源说明，产品源码/依赖零改动；Codex冻结SHA并新Appointment DSH独审，输出可释放或BLOCKED的明确裁决。 <<PARTIAL: 无新head/Review>>

## 允许修改范围

只写隔离source中拟议 `verification/GIT-CLEAN-RUST-CAPACITY-DESIGN-1/DESIGN.md`、HANDOFF.md及主仓本Task/自己的checkpoint。可以在workspace存静态分析说明，不运行Rust/真实Core/压力测试，不改任何产品或测试源码，不能实施未审设计。CLI edit缺Bash permission client，不探测已拒绝命令，Codex代提交。新文件必须UTF8、无密钥/用户数据。

## 禁止范围

不push、不done、不集成、不改源main/父候选/1829及旧证据/系统ACL；不改生产MAX32、锁/背压、holder、kill/reap/join/taskkill预算、Schema/契约/依赖；不把假worker/人为延迟凑32写成真实生产饱和；不清理/GC/prune，不派其他Agent，不自审。用户push目标以通过现有Gate为条件，未豁免blocked Review；该目标不授权传播私有素材或改写main。

## 测试要求

planned：静态核对代码调用链、设计反例、输入head/source SHA、diff确认仅设计文档；实际压力NOT_RUN，不重复当前或旧失败。新head必须新Appointment独审。独审若建议实施，Codex先另冻实施Task；不能自动执行设计中的命令。

## 依赖、风险与阻塞

当前生产没有被证明有缺陷。可接受设计结论是可实现的test-only方案，或有代码证据支持的结构性不可达及需由Codex/用户裁定的明确问题。后者不会解除父Gate。ZCode上轮CLI末尾HTTP429，但已产文件；本轮只执行一个明确切片，失败留日志不自动换yolo/改配置。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| IN-01 | source/scope | G:/CODEX/New Manga/verification/GIT-CLEAN-RUST-ISOLATION-1/r2/dsh-review-r2.md | - | a0bba91a300baa3543ceb9e7140c94d93e7860ae999c36b2d1ef7b21a8ac3829 | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| isolated-repo/task-env | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-CAPACITY-DESIGN-1 | PRESERVE_REFERENCED | — | base1829a38 | 新独立repo无remote，不清理 |
| source/evidence | Rust r2及冻结包 | PRESERVE_REFERENCED | — | 原Task pins | 只读 |
| dataset/model/user-data | — | NOT_APPLICABLE | — | — | 不使用 |
| agent-output/exchange | G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-RUST-CAPACITY-DESIGN-1/dispatch-zcode-r1 | PRESERVE_REFERENCED | — | 待派发 | 本地CLI |

## 交付与运行记录

## 2026-10-25 DSH 接管确认

DSH 接任 Lead / Architect / Integrator（见 `doc/GOVERNANCE_TAKEOVER_2026-10-25.md`）。原 Codex 释放的 ready 状态、冻结范围、base `1829a38` 与 ZCode Owner 维持不变；Reviewer 由 DeepSeek Harness 改派 **Antigravity**（历史时点记录，已被下节二次改派取代）。原 `approval` 文字保留为历史事实，当前授权依据为 DSH 接管连续性，不新增范围、不新增推送门槛。

## Reviewer 二次改派（2026-10-25）

- **改派**：frontmatter `reviewer` 由 `Antigravity` 改为 `ZCode`。上一节「Reviewer 改派 **Antigravity**（ZCode 是未来实现作者，不能自审）」保留为历史时点记录，当前归属以本节为准。STATUS 与 REBASELINE_PLAN 同步。
- **依据**：用户 2026-10-25 明令本项目**停用 Antigravity / agy**。保留 `Reviewer=Antigravity` 会成为指向已停用 Agent 的死指针，后续任何 Appointment 都会卡死。
- **遗留冲突（如实登记，不隐瞒）**：本 Task `owner` 同为 `ZCode`，与「Owner 与 Reviewer 必须不同」冲突。本次改派只清除死指针，**不授权自审**：
  - 本 Task 本会话不认领、不派发、不产生新 head；
  - 若将来复活，独立审查必须由未参与实现的 Agent 执行（候选：Codex，或记 `reviewer_unavailable` 等待可用 Reviewer），新 head 另建 `APPOINTMENT.md` 绑定精确 base/head 与唯一 Review 写路径；
  - 备选方案「改 Owner 为 Codex」未被采用：该 Task 是本轮被明确绕开的环境线，不应重新拉回实施队列。

本 Task 仍是设计切片：只允许设计文档与来源说明，不实施、不改产品或测试源码、不运行压力。设计若确认 32 饱和在不变生产语义下不可达，须给可证伪机制与证据要求，保留 AC3 BLOCKED，交 DSH 裁决；不得以假 worker、人工延迟或修改生产 MAX/锁/背压来凑 32。当前不因本 Task 存在而阻塞干净快照 push 的独立审查。
