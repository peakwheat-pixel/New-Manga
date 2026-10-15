# Codex 集成勘误与当前口径

当前唯一结果为本目录 current-summary.json，独立 Review 绑定 4abb8d288e005dc58e3270b12389d33cd7a52ac1，内容集成 38d926026e9032a528ce578dba7290c5ce65356b。旧 i1/i2/RES 汇总、旧 Handoff 和 Review 均原样保留，为历史证据，不作为当前结果。

- DSH-A7-01：canonical Task/STATUS/DAG 经 epoch 3 guarded-write 统一；Owner worktree 中旧 Task 保留为冻结交付，不是主 checkout 的实时状态。
- DSH-A7-02 / r6 F-02：冻结 I2 契约 §2.3 的 I1 失败 node_exit_code=null 为文本勘误；四份原始 execution-metadata.node_exit_code 与 runner.exit_code 均为 1。current-summary 按原始值归一，原文件不改。
- CV-A7-01（P3，Codex deterministic VERIFY）：Owner 派生 rollup 的 EXE SHA 字符串 92AC7B8EFB646FE77DF8245B13C9AF9314BEF415F2F0E007B1CDCEA729BC13FD 存在单字符抄录错误。原始 execution-metadata、Handoff 与实际 EXE 均为 92AC7B8EFB646FE77DF8245B13C9AF9314BEF415B2F0E007B1CDCEA729BC13FD。current-summary 使用实测值；未替换或重建 EXE，旧 Owner 汇总保留。本勘误不改变已审运行结果或验收范围。
- DSH-A7-03：旧 untracked 父 manifest 含 mutable Task，现时 FAIL 原样保留；本次 source-evidence-manifest 排除 Task/STATUS/PLAN/checkpoint/runtime，另落官方 verify 输出，不修改旧清单或声称其 PASS。
- DSH-A7-04：旧 source_head=a8d9219b 是 closeout_base；新汇总明确 closeout_base/source_content_commit/reviewed_head。
- DSH-A7-05：i2 BLOCKED/旧 Handoff/旧 r1 平铺 PASS 均 HISTORICAL；Task 只指向本目录和 a7 当前结果。未移动/删除任何历史文件。
- DSH-A7-06：无采集期端口/进程直接快照，未补造 runner；保留为 P4 限制。

## 范围

本结果仅完成新时点 Workbench harness/证据验收；AC1/2 REAL IPC，AC3 混合 mock，AC4/5 REAL_WEBVIEW_MOCK_IPC，AC6 真 DOM 10/10、token 0 mapped/10 unmapped、alpha 分支未触发。P-01/P-02/P-03 保留 backlog；旧 H1/P2-1 与 13 项缺失记录、BC-AC5=PARTIAL 不变。I1/I2=2/2，未开启 I3。

## 保留资源

Owner worktree、原集成 dirty worktree、该新集成分支/worktree、全部 synthetic env/模型源/构建产物/原始日志均 PRESERVE_REFERENCED；来源未知内容 PRESERVE_UNKNOWN。删除/迁移/归档=0。新分支未合并 main；不触碰 main 的用户 dirty/untracked 或原索引。
