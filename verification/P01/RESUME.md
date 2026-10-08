# P01 恢复点

时间：2026-10-09（Asia/Shanghai）；Task=`P01`；TaskStatus=`ready`；ExecutionState=`CHECKPOINTED`（尚未开始 source Task 写入）。

## 当前权威状态

- P03 正式关闭与 Codex Integration Gate 提交：`826bea12a132c5af2ac0cd1244d00e9170093c71`；P03=`done`。其 16-case snapshot、40/40 targeted tests 与 packaged Gate 28/28 仍绑定 source `d717c049a41544a6d592943a0b0fe1b76a41a050`，未声称在 P03 集成头重跑。
- P01 已基于该 commit 正式释放：base=`826bea12a132c5af2ac0cd1244d00e9170093c71`；branch=`agent/codex/P01-metadata-audit`；worktree=`G:/CODEX/New Manga.worktrees/P01-metadata-audit-codex`；Owner=Codex；非作者Reviewer=DeepSeek Harness；Integrator=Codex；depends_on=`[]`。
- Worktree 初始 HEAD=`826bea12a132c5af2ac0cd1244d00e9170093c71`，创建时干净、common-dir=`G:/CODEX/New Manga/.git`。release metadata commit 是包含本恢复文件的 P01 branch 当前提交；可用 `git -C 'G:/CODEX/New Manga.worktrees/P01-metadata-audit-codex' log -1 --format=%H -- verification/P01/RESUME.md` 解析。恢复后以实际 `git rev-parse HEAD` 与状态文档交叉核验，不猜哈希。
- Root main 的原有用户/Qoder/Agent dirty 与 P03 raw-review evidence 均留在 root checkout，未复制进 P01 worktree、未 stage、未 stash、未覆盖或清理。P03关闭后 root 仍有24个既存 dirty/untracked 项；实际名称以 root `git status --short` 为准。

## P01 冻结范围与已知调查锚点

正式契约见[`doc/tasks/P01.md`](../../doc/tasks/P01.md)。唯一来源 Task：

- `doc/tasks/M2-DERIVED-GC-2.md`：页头 `integration_commit: null`，正文/Plan 与 inventory 记录 `cea610ed`。live Git 中完整对象 `cea610ed3f3349f1d76361d151815445e991f7d7` 为 commit 且为 P01 base 祖先；P01 执行时仍须核对实际集成与 Handoff 证据，再决定是否只修该字段。
- `doc/tasks/M2-PROD-DETECT-3.md`：页头 SHA `8fe5199c44b06e679a2f0e6ee47767032217eb47` 不是可解析的对象；inventory 候选 `8fe5199c6d05d144052141ad02ed054bbaa90645` 是 commit 且为 base 祖先。P01 执行时须继续核对交付/Handoff/集成证据，不得只信 inventory 后覆盖。
- `doc/tasks/M2-SFX-ANNOTATE-R2.md`：`review_events: []`。只按允许范围查独立 Review carrier，并记录 fixed base/head/decision/hash；缺失记`NOT_VERIFIED`。
- `doc/tasks/M2-SFX-SYNTH-BG-AUTO.md`：frontmatter `status: in_review`，含重复且冲突的`integration_commit`声明，正文提及历史 DSH Review。追踪真实独立报告；若集成证据充分，可只纠正重复字段；不得把它置为`done`。

上述是启动前可验证的调查锚点，不代表 P01 最终审计结论或 Review 已批准。R2 challenge 空集及 T2 是否释放是用户裁决，不由 P01 推断；SYNTH 的真实网页登录/冒烟要求也不得冒充通过。未找到 carrier 时如实记`NOT_VERIFIED`，P01 仍可在完整登记边界后完成。

## 验证状态

- 本次已核验：GC2 完整 commit 对象存在且为 base 祖先；DETECT3 错误完整 SHA 不存在，inventory 候选对象存在且为 base 祖先。
- P01 来源 Task/Handoff 与 Review carriers 的完整逐项追溯：`NOT_RUN`。
- 产品 pytest/cargo/vitest、GUI、build：`NOT_RUN`（本 Task 不涉及产品代码）。
- 独立 DSH Review 与 Codex Integration Gate：待 P01 完成时对最终固定 head 执行。
- 目前没有需用户裁决的产品问题阻止 P01 启动；对已知裁决边界保持只记录、不决策。

## 下一条直接指令

先重新阅读仓库 `AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/STATUS.md`、`doc/09_COLLABORATION.md`、`doc/tasks/P01.md` 和本恢复点；核验 main 与 P01 worktree 的真实 branch/HEAD/dirty/common-dir，得到`RESUME_SAFE`或记录`DRIFT_DETECTED`。随后立即在指定 P01 worktree 执行只读取证，按 P01 AC2–AC6 逐项跟踪 Git 对象、Task/Handoff、review carrier 和 SHA；仅在充分证据下修正 GC2/DETECT3 的允许字段。完成后实际派发 DeepSeek Harness 固定 head 非作者 Review，收回并验证真实交付，再运行 Codex Integration Gate、更新权威文档/依赖图/恢复点并自动选择后续可释放 Task。继续保护root dirty、用户数据、Lock、current/pinned Revision及Qoder历史；不push、不发布、不部署、不删除。没有授权下次关机；不要再安排关机。

## 本次 release prompt

见 [`NEXT-AUTOPROGRESS-PROMPT.md`](NEXT-AUTOPROGRESS-PROMPT.md)。
