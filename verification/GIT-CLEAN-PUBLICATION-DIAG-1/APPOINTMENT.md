# 新 head 的独立 Review Appointment

2026-10-24 / Codex 任命；状态 `APPOINTED_PENDING_EXECUTION`。本记录不代表审查已执行或通过。

- Task：GIT-CLEAN-PUBLICATION-DIAG-1。
- Owner/Author：Codex；独立 Reviewer：DeepSeek Harness，不得自审。
- Recovery：`G:/CODEX/New Manga.workspace/task-envs/GIT-CLEAN-PUBLICATION-DIAG-1/source`，branch `codex/git-clean-publication-diag-1`。
- base_commit：`e34a90d001cce1fa966aec7d2b032bb5ad1cf148`；reviewed_head 必须为 `fed1a9cf3295e5e05f7ffd363ac1075bd22e90b1`，不可沿用父 Review。
- Scope：诊断结论、默认并发失败/四个单进程对照、SOURCE_PIN DB、`_grant` 局部诊断字段及 mock、冻结包和 packaged 实际结果。源码只读；共享协议、生产 registry、真实系统 ACL 不在修改范围。
- 唯一 Reviewer 写入：`G:/CODEX/New Manga/verification/GIT-CLEAN-PUBLICATION-DIAG-1/dsh-review-r1.md`，不得修改 Task 状态、候选或原始证据。
- Deliverables：按项目 REVIEW 模板引用本 Task、RESULT、Canonical Evidence，绑定以上精确 head，明确产品并发/环境归因/packaged 边界，给出独立 decision。
- Verification：先核对源码差分恰两文件与 mock 证据 SHA；固定输入的默认并发为父 e34 baseline，mock 在补丁工作树实测并以源码 SHA 绑定本 head。Core 同条件全套失败已达两次，不盲重跑；未跑或无法排除项保留 BLOCKED/NOT_RUN。不得把 isolated 通过冒充默认并发通过，不得把 mock returncode=5 冒充旧机器真实错误码。
- Gate：父 Task 仍 `in_review`、DSH r1 blocked；父交付 e34 不变。只有本诊断证据冻结后才可启动此次独审；任何再次改 head，重新 Appointment。未 push、未置 done、无 main 集成授权。

可直接转发：在上述隔离仓库对固定 `fed1a9cf3295e5e05f7ffd363ac1075bd22e90b1` 做只读独立 Review。先读主仓 GIT-CLEAN-PUBLICATION-DIAG-1 Task、RESULT、Canonical Evidence 与本 Appointment，逐项核验诊断和失败边界；唯一写 dsh-review-r1.md。不改系统 ACL、主线、候选、Task 状态或远端，不重复超过上限的 Core 失败，不清理。源 main 349e61faf、父候选 e34 与本诊断 head 是不同角色，旧 Review 不适用于本 head。
