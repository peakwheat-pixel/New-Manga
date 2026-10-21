---
id: GOV-BROAD-ROOT-PRESERVATION-DESIGN-1
title: 五个广域根整体保护的精确保全解释设计
kind: design
governance_version: 3
status: done
approval: user_broad_roots_preserve_all_20261021_design_only
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness
latest_review: verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/review-dsh-r3.md
reviewed_head: 232e3a5896644446acf3c4e0a0d5edc1a9490616
depends_on: [GOV-RESIDUAL-24-DECISION-1]
base_commit: 3d0a36ac04d30eba0906e70218ef9491c5b9ffbc
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 232e3a5896644446acf3c4e0a0d5edc1a9490616
delivery_head: e33a51b4df4856b9bdfe2dd8e57b84f1c395a797
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1
allowed_paths:
  - doc/tasks/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1.md
  - verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1
  - doc/handoffs/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/tasks/README.md
  - verification/GIT-MAINLINE-CONVERGENCE-1/checkpoint.md
---

# GOV-BROAD-ROOT-PRESERVATION-DESIGN-1

## 用户裁决与冻结范围

2026-10-21用户选择：继续整体保护（推荐）；由Codex另冻精确保全解释设计，DeepSeek独审。对象仅已审清单的5根：New Manga.workspace本身及task-envs/worktrees/review-scratch/temp；对应SEC-FIX-PATH-ECHO-1和WORKSPACE-CONSOLIDATION-1的6记录/12广域错误，原字节/旧pin不改。r212禁令/父blocked保留；本Task只设计，不授权实现或清理。

按需读取当前guard的路径解析/身份验证/注册/Markdown扫描/消费链，以及remove_worktrees.py和consolidate.py相关调用、现有29/80测试组织及事故回放入口。交付精确来源身份绑定、source/destination双保护、与既有pin/NDJSON例外分离、失败关闭策略、覆盖所有调用者的最小改动位置和未来测试门槛。可做内存模型检验但不得冒称真实工具已实施；不得写tools代码/配置或历史源。

## Acceptance Criteria

- [x] **AC1** 用户选择、5根/6记录/12错误/两源SHA及固定引用清晰，当前源字节/status保全。 <<MET>>
- [x] **AC2** 设计只允许精确保全解释且新增whole-root保护，异常/漂移继续拒绝；source/destination、EVIDENCE_PIN/prose/JSON隔离与alias/realpath考虑齐全，3入口共同生效，不缩小保护。 <<MET>>
- [x] **AC3** 提供最小后续实现范围、正反测试矩阵/109回归和双15回放要求，模型结果与NOT_RUN分离，DeepSeek固定head独审。 <<MET>>
- [x] **AC4** Codex只读集成复验、实际EV注册/治理check、Handoff/资源核销完整；正式仍24错误、99/137、父blocked/禁令不变。 <<MET>>

## 禁止与验证

禁止工具/配置/旧Task/旧Review/旧pin/原始JSON/用户文件变更，禁止按根名称批量忽略错误、扩大到其它广域根或resource disposition、真实清理/迁移/归档/GC/prune/push/reset/stash/ACL/Legacy运行。不新增worktree/env，只用本Taskworkspace输出。实际guard审计/源SHA/status、diff-check/治理check；模型只能标SIMULATION，不替代后续真实测试。产品/构建/工具回归本TaskNOT_RUN。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
|EV-1|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/.gitattributes|e33a51b4df4856b9bdfe2dd8e57b84f1c395a797|705fd4d6451a31d36b3df7de96f83f30ac976c9b4a6d1e51671d8e2f33e2d0da|CANONICAL|
|EV-2|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/binding-specimen.json|e33a51b4df4856b9bdfe2dd8e57b84f1c395a797|95be5dfdc7c1ea0022a29cecd3ccc87fe096d4dadae9a077a33c46c6ccf36ea6|CANONICAL|
|EV-3|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/checkpoint.md|e33a51b4df4856b9bdfe2dd8e57b84f1c395a797|ace9c1e1f102eaeea57cfdec16ace0a8db7e3e12338cef0e279c0a7226647bc2|CANONICAL|
|EV-4|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/design.md|e33a51b4df4856b9bdfe2dd8e57b84f1c395a797|f29d6eaadbc0fb46e48294772c401391b9d57226745e03e04f767f140bc0cf15|CANONICAL|
|EV-5|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/model-proof.json|e33a51b4df4856b9bdfe2dd8e57b84f1c395a797|be39c47baf9bdb989a173f56d83d0b45fe13a4fe4bf7dbfdbc1a7091ec3fb550|CANONICAL|
|EV-6|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/preservation-validation.json|e33a51b4df4856b9bdfe2dd8e57b84f1c395a797|8a742b547351e6e0e47c2aa11c2b3050359c4570de8f973c4f22af095437d5b3|CANONICAL|
|EV-7|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/r1-response.md|e33a51b4df4856b9bdfe2dd8e57b84f1c395a797|acb3d5de2c0cc07ad953a7b4e1dcf55c8672b417fd7ec2b5d3aee4add6d5a1f6|CANONICAL|
|EV-8|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/review-dsh-r1.md|e33a51b4df4856b9bdfe2dd8e57b84f1c395a797|94b28aa611559c45cd790bdd997efd30b3222091de51e1a95b72352899cb2764|CANONICAL|
|EV-9|AC1/AC2/AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/ruling.md|e33a51b4df4856b9bdfe2dd8e57b84f1c395a797|4f9b206ce835fabf029d2a59ff70e3116febbe26302928978090117b4d375f38|CANONICAL|
|EV-10|AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/review-dsh-r2.md|9cfae1352ca97a53cf5b037f7d66d4bb502a3fea|d19b466d33df4bb5310617a23f379a6bcf4dd4bb67c86efd6b910e71a0d15b62|CANONICAL|
|EV-11|AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/review-dsh-r3.md|a5b1a3d77397e109e72a480fec98c914ecec3076|b552adafdfc5be32304af71759a23b49f6ef9f92e93f1c59886df5f20527c6b0|CANONICAL|
|EV-12|AC3/AC4|verification/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1/integration-validation.json|a5b1a3d77397e109e72a480fec98c914ecec3076|fbe26bfb37fe09ac08fcb1a052890fae97684d6638574a81a70b44cd41fc6010|CANONICAL|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/agent-output/codex/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1 | doc/tasks/GOV-BROAD-ROOT-PRESERVATION-DESIGN-1.md | 设计/模型/独审输出保留 |
| worktree/env/build | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | 无新建 |

R1独审3879cb936 changes_requested已记录review-dsh-r1.md；e33a51b4d修订两P1/三P2，处理矩阵r1-response.md；R2须固定新head复审。15覆盖模型重算、warnings254→266；真实仍24。

R2固定1670b34ec：设计P1/P2已关闭，仅Handoff下一Task旧delivery需修；现改为e33a51b4d，设计/模型/绑定7输入未变化。R3只核metadata最终固定head，不延用未批准结论。

## Closeout Record

2026-10-21 / Codex：R1两P1/三P2及R2单metadata问题均关闭，DeepSeek R3固定232e3a5896644446acf3c4e0a0d5edc1a9490616 approved，source交付e33a51b4d。main同点复验正式24完整错误身份不变；两原源和7输入raw/status不变、tools/运行配置未改、policy不存在；10原EV raw=blob=pin且实际注册10/0error。R3快照2477声明/1807根/24errors/254warnings，自有收口EV追加后会增加，不混同历史模型快照。模型仅15覆盖、+12Declaration/+5根/+12warnings和SIMULATION24→12；所有loader/负例/T01-T18/109/双15回放和产品/构建为未来NOT_RUN，不冒称实现已通过。

资源核销：DSH同session-89d9de3e-714e-4a87-b0b0-b60526ec5eae R3已exit0，web_visibility=unverified。本Taskagent-output/设计/模型/三轮Review原位保留，无新worktree/env；99heads/137worktrees、0真实资源删除/迁移/归档/GC/prune/push。Task专项及当前authority治理check、diff-check终检。父blocked/r212禁令不解除，尚未只剩main。

用户5广域根整体保留方向已落地设计；下一建议Codex按Handoff另冻GOV-BROAD-ROOT-PRESERVATION-IMPL-1、DeepSeek独审（拟议，未创建/未释放）。本Task完成只覆盖设计，不给工具实现、policy发布或资源退出授权；7历史身份及其它12项限制继续保留。
