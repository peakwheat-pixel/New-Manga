# P08 DSH 正式 Review Prompt R4

你是本Task的非作者Reviewer：DeepSeek Harness。只读审查精确delivery head `16fb07a973b36b0b129945bc3a85f9ae51234982`，base=`ab2f813c0ce311a6712002cafd852b9e7a258380`，审查worktree=`G:/CODEX/New Manga.worktrees/P08-dsh-review-16fb07a9-r4`；预期detached、clean、common-dir=`G:/CODEX/New Manga/.git`。先核实实际HEAD、status、worktree根与common-dir，再下结论。不得修改文件、提交、切换HEAD或扩大P08范围。

## 审查依据与范围

审查完整差量 `ab2f813c0ce311a6712002cafd852b9e7a258380..16fb07a973b36b0b129945bc3a85f9ae51234982`。先读`AGENTS.md`、`doc/09_COLLABORATION.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P08.md`、`verification/P08/RESUME.md`、`verification/P08/AC_COVERAGE.md`、`verification/P08/SCOPE_DRAFT.md`、R1/R2/R3正式报告，再核实`doc/04_USER_FLOW.md`、`doc/08_ACCEPTANCE_CRITERIA.md`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`、`doc/13_ACCEPTANCE_TRACEABILITY.md`及相关实现事实。聊天记录不是产品事实来源；D1–D7由用户确认，不重问、不扩写为Review裁决。

## 必须复核的Finding

| ID | 等级 | 必须核实 |
|---|---|---|
| N-07 | P2 | `verification/P08/AC_COVERAGE.md` 的 AC-EXPORT-001 状态列是否完整准确写明D08 AC-EXPORT-001列出单图、ZIP、CBZ、PDF、文本五项；“单图→PNG”是否仅归因用户D1/D2且P16冻结映射，未暗示D08限定PNG。与`doc/08_ACCEPTANCE_CRITERIA.md`原文及同交付`SCOPE_DRAFT.md`交叉核对。 |
| N-08 | P3 | `verification/P08/verify_scope.py` 是否从`doc/handoffs/P08-*.md`动态收集所有P08 Handoff并将其加入`git diff --check`范围，PASS文案与真实范围是否一致；确认当前被审head的R1/R2/R3三份Handoff均被覆盖，并评估新增Handoff时的边界。 |

重新核实R1的4×P1、R1的P2/P3处置及R2 N-01..N-06 closure；重点确认N-01..N-06在R3已独立关闭，本轮没有退化。检查AC逐项对应D08、D1–D7未扩写、D5门槛、12条Legacy PASS口径、§74/75/79 advisory、全库备份、源文件/人工修改/Lock/current/pinned保护、Architecture Documentation Rebaseline前置Gate、允许/禁止路径。识别R3以后的新增问题或遗漏影响范围。

## 只读与验证纪律

- 只读；不修改/生成项目文件，不提交，不切换HEAD。记录实际HEAD、status、worktree路径与common-dir。
- 可运行环境支持的只读检查。若DSH `pwsh` ACL初始化失败（如`SetNamedSecurityInfoW failed (Win32 5)`），将对应检查记为`NOT_RUN`并说明原因；不提权，不将Codex结果计作DSH执行。
- Codex已在该精确head的clean linked worktree运行`python -B -X utf8 verification/P08/verify_scope.py`、`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`、固定base/head的`git diff --check`及受保护路径差量检查；这些仅为Codex证据。产品pytest/cargo/vitest/GUI/build/model为`NOT_RUN`（文档Task）。
- 所有实际Review命令记录原文、环境、结果、EXIT和证据；静态审查不能写成测试PASS。

## 报告与判定

按中文`doc/templates/REVIEW.md`输出完整Review正文并作为最终答复，包括frontmatter、固定base/head、范围、Architecture与Verification结论、逐Finding表、验证矩阵、NOT_RUN/NOT_VERIFIED边界、风险与结论。逐项判定N-07/N-08与旧Finding的`closed`/`open`/`deferred`，不得只凭作者自述关闭。新问题使用唯一ID、级别、具体文件/行、触发、影响、复现证据与建议。decision只能是`pending`、`changes_requested`、`approved`、`blocked`之一；未解决P0/P1、D1–D7/数据保护回退或关键证据缺失时不得批准。不要创建报告文件，Codex会核验并归档你的原样最终报告。
