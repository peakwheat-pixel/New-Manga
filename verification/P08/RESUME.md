# P08 可恢复检查点

时间：2026-10-09 01:04（Asia/Shanghai）；Task=P08；TaskStatus=approved；ExecutionState=ACTIVE；工作点=Codex集成Gate通过，done收口提交待完成。

## 当前权威事实

- 唯一仓库：G:/CODEX/New Manga；branch=main；恢复时以 live HEAD 和 Git 状态为准。
- P08 Task 基线：ab2f813c0ce311a6712002cafd852b9e7a258380。
- R7 固定 delivery / reviewed_head：fe222464616152e9c95208e06c248565f2fd86a6；review base：ecb3b520ce68c2ddcc0c5ec94596e2f50a17f369。
- DSH 正式 R7：decision=approved；native session=session-bf5b0be5-bd1e-41b8-83cc-152c28227485；CLI EXIT=0；DSH 版本=0.1.7-rc.2；session cwd=G:/CODEX/New Manga.worktrees/P08-dsh-review-fe222464-r7。mount_session.py --id 返回 EXIT=0 并挂载到 New Manga workspace；桌面/Web 可见性未核验，保持 unverified。
- canonical 报告=verification/P08/review-dsh-fe222464-r7.md；SHA256=2D8165B95A702B40607840889208C62A1CEC4E89C4A445D0591BE9ED2A719C03。raw JSONL=verification/P08/dsh-r7.stdout.jsonl；SHA256=3260118DCEF50848B986D17ECB72B34F5109E3B09F0C699CC6137153F575447C；stderr=0 bytes；final正文共15668字符，和canonical报告UTF-8字节完全一致。
- DSH 的 pwsh 命令4次均在ACL授予阶段因 SetNamedSecurityInfoW Win32 5 失败，DSH 自身 shell/git/python 结果记 NOT_RUN / NOT_VERIFIED。Codex 实测不得冒称为 DSH 命令级PASS。
- DSH 报告无未解决 P0/P1/P2。R7-01 P3：已在 P08 Task 记录 Task-local approval/status 映射，不改共享协议或Schema；R7-02 P4：固定head与delivery后验证边界已由 Codex Gate 实测并记录；R7-03 P4：Task 尾部历史字面量已从 delivery 后正文移除。R6-01已在547894f59dc2e9ab89812d27efc511d432c6b6a9修复；R5-01/R5-02已由R6独立关闭。
- 精确 R7 worktree=G:/CODEX/New Manga.worktrees/P08-dsh-review-fe222464-r7；detached、clean、HEAD精确等于fe222464616152e9c95208e06c248565f2fd86a6，common-dir=G:/CODEX/New Manga/.git。
- Codex 在精确 R7 worktree 实跑 verify_scope.py EXIT=0、verify_plan.py EXIT=0、git diff --check ecb3b520...fe222464 EXIT=0、git diff --quiet HEAD -- . EXIT=0；protected source/contracts/frozen-spec/inventory 差量为空。主线 metadata 验证器也通过：P08 approved，20项候选仍未释放；193项D08 criteria、AC-SMOKE、12 gates与路线图链接/无环依赖通过。
- 产品 pytest/cargo/vitest/GUI/build/model 均 NOT_RUN；此 Task 是文档与验证器准备，不代表产品实现或产品 Gate 通过。
- P03 是当前推荐下一候选，Plan 标明 PROBE-1、Runner Debt、Guard 前置已完成，建议 Owner=Antigravity、非作者 Reviewer=DeepSeek Harness；它尚未建立正式 Task、没有冻结 allowed_paths/hash，也未释放。按本次关机要求，本检查点完成后不在本轮启动P03。
- 必须原样保护，不暂存、不覆盖、不stash/reset/clean：.qoder-credits/report.json modified；.qoder-credits/通路探测__8602db50.canvas.tsx untracked；verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/antigravity-dispatch.json 与 .stderr.log；verification/P08/dsh-r4.*、dsh-r5.*、dsh-r6.*、dsh-r7.stdout.jsonl、dsh-r7.stderr.log raw outputs。R7 canonical报告是授权的正式证据，可提交。

## 直接恢复指令

1. 检查 live branch、HEAD、common-dir、status 与本文件；保留上述其他作者 dirty/raw。
2. 当前应见 P08=approved，R7 head=fe222464，DSH Review approved。对照 doc/tasks/P08.md、doc/STATUS.md、doc/REBASELINE_PLAN.md 与验证日志。不要重复全库审计，不重派 R7。
3. Task状态metadata与Plan/Status/Index/README/ROADMAP/派生REPORT/RESUME已同步到approved。集成验证结果已通过；确认本 checkpoint 提交仅包含 P08 授权 Task/Handoff/verification 与导航文件、canonical R7 报告，不包含raw或受保护dirty。
4. 将P08收口为done：integration_commit沿用直接集成到main的R7 delivery fe222464；完成AC/依赖图/恢复点；复跑主线两个validator和whitespace检查并提交final checkpoint。R7-02已closed。更新后的RESUME必须包含下一次自动推进提示词。
5. 关闭P08后仅记录P03为下一推荐候选；不要凭此检查点虚构正式Task、工作路径、commit、冻结hash或释放状态。然后按用户授权安排关机。
