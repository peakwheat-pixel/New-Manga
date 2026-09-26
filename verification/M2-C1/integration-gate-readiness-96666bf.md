# M2-C1 Integration Gate 就绪核验 — READY_FOR_INTEGRATION_GATE

日期：2026-09-26（Asia/Shanghai）。执行：Codex，`G:/CODEX/New Manga.worktrees/M2-C1-integration-gate-r3`，共享 Git common-dir=`G:/CODEX/New Manga/.git`。

## 固定输入

| 对象 | SHA |
|---|---|
| base | `7478f72fe6f9872cae29f4fa12888b5e1f2380f1` |
| ZCode Owner Delivery | `7de1cd27e22037d4b76b235c9f11399b0cea9463` |
| Handoff / reviewed_head | `b2377288680569dbee4e2299fd7dfae4de067c54` |
| Contract blob | `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3` |
| Qoder Review | `0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5` |
| DeepSeek Harness r3 Review | `96666bf063c8a514b3f8a58f78453a397dd93f75` |

## 更正先前 blocker 误报

先前未提交的 Gate 核验命令把固定 Handoff SHA 的 `...2299fd7...` 误写为 `...2299df7...`。两个值都是 40 字符；错误 SHA 不存在，因此 `git cat-file` exit 128。正确 SHA 在共享仓库和 DSH r3 standalone clone 都返回 `commit`；共享仓库的 loose object 与 pack、DSH r3 clone 的 pack 中均能定位。并非 Git 对象间歇性丢失。既有历史记录 `verification/M2-C1/review-environment-recovery-7de1cd2-r2.md` 的两处固定 SHA 文本也含同一转置；该历史文件原样保留，r2 worktree 实际 `git rev-parse HEAD` 返回正确 SHA。先前“对象缺失”的判断撤销，保留此纠错说明以供审计。

## Gate 核验

- `git merge-base --is-ancestor <base> master` exit 0；当前集成基线 `master=4ad205ddbd1af4d9d2bf64478a042cf519fdf709`。M2-D1/I1/I2/R1/UI1 已在该 base 之前集成；Owner 的源码证据在 base 中可读。
- `git cat-file -t` 对 Owner、Handoff、Qoder、DSH 均返回 `commit`。`git rev-parse <commit>^` 分别得到 `Owner^=base`、`Handoff^=Owner`、`Qoder^=Handoff`、`DSH^=Handoff`；四次 `git merge-base --is-ancestor` 均 exit 0。
- `git rev-parse <commit>:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 在 Owner、Handoff、Qoder、DSH 四棵树均为固定 blob `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3`，与 adopted source Case A 一致。
- `git diff-tree --no-commit-id --name-only -r`：Owner 仅 Contract 与 `verification/M2-C1/zcode-owner/**`（7 路径）；Handoff 仅指定 Handoff（1 路径）；Qoder 仅其 Review 报告和 `verification/M2-C1/review-qoder-zcode-7de1cd2/**`（8 路径）；DSH 仅其 r3 报告和 `verification/M2-C1/review-dsh-zcode-7de1cd2-r3/**`（16 路径）。全部符合各自授权范围。
- `git diff --check <base> <Handoff>`、`git diff --check <Handoff> <Qoder>`、`git diff --check <Handoff> <DSH>` 均无输出、exit 0；共享仓库 `git fsck --connectivity-only --no-dangling` exit 0。
- Owner worktree HEAD=`Handoff` 且 clean；Qoder worktree HEAD=`Qoder`，仅原有未跟踪 `.qoder-credits/`；DSH r3 standalone clone HEAD=`DSH` 且 clean，其 `git-dir`/`git-common-dir` 均为自身 C: `.git`。原 G: DSH 与 C: r2 现场仍保留。
- 两份正式 Review 报告均 `decision: approved`，均绑定同一固定 `reviewed_head=Handoff`。DSH r3 的 F-001 将 Contract 内 `../../verification/M2-C1/source-trace.md` 断链判为 P3/non-blocking，不要求 Owner 返修，建议由 Codex 集成时补充目标文件而不改 Contract blob；F-002/F-003 亦 non-blocking。Qoder 的产品 runtime 验证范围未被误报为 PASS。

## 判定与集成计划

双 Review Gate 满足；M2-C1 从 `blocked` 解除为 `approved`，Integration Gate=`READY_FOR_INTEGRATION_GATE`。此记录本身不表示 Owner 已集成，也不释放 M2-S1。

Codex 在干净的共享仓库集成分支上采用 Git merge 保留 Owner/Handoff、Qoder 和 DSH 原始 commit identity，再补充 `verification/M2-C1/source-trace.md` 以修复 F-001，并做集成后文档链接、对象 ancestry、Contract blob、授权路径及 `git diff --check` 验证。产品 pytest/GUI/IPC runtime 仍按文档-only Task 记为 `NOT_RUN`。
