---
task_id: GOV-CHECKER-NOTASK-1
adjudicator: ZCode 独立只读 Integrator
session_id: sess_6f299f99-83a7-4d04-a749-dade19f47d9a
initial_turn_id: turn_86c1e7fb-e87d-4284-8044-89c7f0c0fc91
revised_turn_id: turn_1a47074c-48d9-4cb9-8cdf-b09cfeb40409
input_head: 62ab6b735961359b8a29984484033747b221fee4
decision: ACCEPT_REVIEW_AND_AUTHORIZE_CONDITIONAL_CLOSEOUT_V2
---

# 独立 ZCode Integrator 裁决及修订

2026-11-11，独立 ZCode 会话采信 `sess_4edfc1ab-c2eb-4669-836f-aeb99a0a7bd8` 对 `4231469b972d0c2be086c6b077b6150c90a5d3d6` 的 ACCEPT；该会话与实现、释放、基线裁决和本 Integrator 会话均不同。CLI 两轮均 EXIT 0。本记录由 Codex 按 CLI 返回整理。

首轮提出对仓内收口日志使用 SHA-only pin；经指出与用户要求仓内文件必须 pin 实际包含文件的 commit、以及证据与 pin 回填分离冲突，ZCode 撤回该建议，以本 v2 取代首轮收口序列。新 pin 使用 BLOB SHA-256。

## Review 和 findings 处置

- F-1 生命周期自指：Review 已完成，但 AC3 的空窗主树 gate、最终收口仍须实测，未实测不得作为 PASS 入库；按下述候选树实测及分离提交顺序处理。
- F-2 Resource Manifest：卡面已改用真实 `resource-manifest.md`；Integrator 采信保留建议，关闭前须实测目录及三个 clone 存在，完成资源 closeout。
- F-3 预算：Plan 最多 7000 bytes/64 行、STATUS 最多 3200 bytes/45 行；使用短收口文案并实测，超限精简当前文案，不删除历史行、不改阈值。
- F-4 证据目录：最终 done TaskPath 前逐文件核对全部登记；意外文件不得忽略或随意清理。Codex 补核日志记录 13 条 BLOB pin 和当时 10 个目录文件，后续新增项须继续登记。

## v2 收口顺序

1. **R0 裁决提交**：本裁决先单独提交；后续 Task 卡用实际 R0 commit 与其中本文件的 BLOB SHA 回填。
2. **隔离试验**：可在仓外 checkout 构造候选 done 树，验证文案、预算、manifest、Ledger 和四项 gate；标 `ISOLATED`、记录 HEAD/dirty/逐项 EXIT，不能替代主树结果。
3. **G1 主树候选**：STATUS 改为 `- 当前 Task：无（GOV-CHECKER-NOTASK-1 已收口）`；Plan 标 done 且 ACTIVE 无；Task 卡候选状态 done、AC3 MET、closeout 字段 complete、登记 R0，Ledger 重生成。该 dirty 候选只是待测树，尚非提交或最终 PASS。候选树不含新收口日志和对应登记行，以避免自指。主树四项 gate（空窗 default、本卡 TaskPath、pins、API）实际均 EXIT 0 才能把候选结果作为收口依据；失败即保持未提交、修复或停止，不把失败记 PASS。
4. **E 证据提交**：将 G1 完整输出记录到 `verification/GOV-CHECKER-NOTASK-1/closeout-gates-<R0短hash>.log`，日志标明 `HEAD_GENERATED=R0`、dirty 候选树状态、命令、时间与实际 EXIT；只提交该日志作为独立证据提交 E，其余候选变更继续保留。E→P 期间 done 卡会因日志未登记而使 TaskPath 预期失败；若运行，必须如实记录。
5. **P pin 回填与终态提交**：卡面 closeout log 行使用实际 E commit 和该文件 E BLOB SHA；提交剩余收口文件。所有仓内 Canonical Evidence 均有包含该文件的 commit，不使用 `commit: -`。
6. **G2 clean P 复跑**：同一四项门禁重新实测并报告实际 HEAD/EXIT；不再向 evidence_dir 新增未登记文件。若失败，按真实结果修复并形成新的 pin/提交、复跑；无法收敛则停止，保留现场且不得宣称完成。

`integration_commit` 指向 `62ab6b735961359b8a29984484033747b221fee4`：该 main head 已包含实现、证据和 Review，作为本直接 main 交付的集成验证基准；不指向无法预知的最终提交自身。关闭时记录此语义。主 worktree、仓外三个 clone 和六份原始日志 `PRESERVE_REFERENCED`，其余未使用资源 `NOT_APPLICABLE`；删除、迁移、归档均为 0。

本 Integrator 的 plan 会话未实际运行 git、hash、目录枚举或四项 gate；空窗主树 gate 在裁决时为 NOT_RUN。G1 与 G2 必须由执行者实测。R-001 不在本任务范围，后续候选须重新释放；不授权 push。
