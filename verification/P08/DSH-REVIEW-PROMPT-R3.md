# P08 DSH 正式 Review Prompt R3

你是本Task的非作者Reviewer：DeepSeek Harness。请只读审查精确delivery head `1ad05d99c924678f35a2558f6e15b6c548d92f09`，基线为 `ab2f813c0ce311a6712002cafd852b9e7a258380`，工作区应为 `G:/CODEX/New Manga.worktrees/P08-dsh-review-1ad05d9-r3`，detached 且 clean。确认实际HEAD、status和读取到的路径后再下结论；不得修改文件、提交、切换HEAD或扩大P08范围。

## 审查问题

先阅读 `AGENTS.md`、`doc/09_COLLABORATION.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P08.md`、`verification/P08/RESUME.md`，再核实 `doc/04_USER_FLOW.md`、`doc/08_ACCEPTANCE_CRITERIA.md`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`、`doc/13_ACCEPTANCE_TRACEABILITY.md`及相关实现事实。聊天记录不作为产品事实来源；D1–D7已由用户确认，不要重问或重解释为Reviewer裁决。

请针对 `ab2f813c0ce311a6712002cafd852b9e7a258380..1ad05d99c924678f35a2558f6e15b6c548d92f09` 审查完整P08文档交付，并重点逐项复核R2发现及历史finding closure：

| ID | 等级 | 必须核实的修订 |
|---|---|---|
| N-01 | P2 | `SCOPE_DRAFT.md`是否准确写明D04 §37与D08 AC-EXPORT-001都列单图、ZIP、CBZ、PDF、文本，并将用户D1/D2的单图→PNG映射清楚归因于用户决定。 |
| N-02 | P2 | `verify_scope.py`与`verify_plan.py`是否支持`doc/09_COLLABORATION.md`定义的全部九种Task状态；Plan表、Task状态、Mermaid图标签及集成commit断言是否一致，不会在`approved`、`blocked`等合法状态下误报。 |
| N-03 | P3 | `verify_scope.py`的`git diff --check`范围是否覆盖P08 subtree、`doc/tasks/README.md`、P08自有Handoff及`verification/PROJECT-ROADMAP-20261008/**`，且PASS文案没有超出实际覆盖。 |
| N-04 | P3 | 只读路径守卫是否保护`AGENTS.md`与`doc/09_COLLABORATION.md`。 |
| N-05 | P3 | `AC_COVERAGE.md`是否说明§78的`ACG-EXT-DETECT`、`ACG-EXT-CONTRACT`、`ACG-EXT-NFR`继续由doc/13追踪。 |
| N-06 | P3 | `SCOPE_DRAFT.md`是否把现存可复用目录/文件与拟议新增目录分清，尤其准确列出已存在的`src/application/settings/`模块，以及目前不存在的Reader/Export前端子目录。 |

同时回看R1的4项P1、6项P2、5项P3处理，以及R2的其他finding。确认P1与关键门槛没有倒退；AC覆盖仍逐项对应D08、D1–D7没有被扩写、D5门槛未降低、历史12条Legacy PASS没有被误报成新架构PASS、§74/75/79等建议项没有变成独立验收、全库备份及源文件/人工修改/Lock/current/pinned保护仍完整、Architecture Documentation Rebaseline前置Gate仍清晰。检查修改是否超出允许路径、遗漏实际影响路径或虚构实现证据。

## 只读与验证纪律

- 只审查文件；不修改/生成项目文件，不提交，不更改head。记录本worktree的真实HEAD、clean/dirty状态和common-dir。
- 可尝试可用的只读检查；若DSH `pwsh`因ACL初始化失败（例如`SetNamedSecurityInfoW failed (Win32 5)`），将该命令记为`NOT_RUN`并说明原因，不尝试提升权限，也不将Codex结果写成DSH执行结果。
- Codex已经在此精确head的clean worktree运行`python -B -X utf8 verification/P08/verify_scope.py`、`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`、`git diff --check`；记录其为Codex证据，不要声称这些是DSH运行。产品pytest/cargo/vitest/GUI/build/model未运行，因为本Task无产品变更。
- 若运行了任何Review检查，报告原样命令、环境、结果、EXIT和证据；不能用静态阅读代替测试通过声明。

## 报告和判定

用中文按`doc/templates/REVIEW.md`产出完整Review，包括frontmatter、范围依据、Architecture与Verification两面、逐项finding表、审查边界、风险和固定head结论。逐项将N-01..N-06判为`closed`或保留为具体finding；不得仅因作者写了“已修订”就关闭。检查R2 closure是否被回归；新finding用唯一ID、等级、具体文件/行、触发、影响、复现证据与建议描述。没有新问题时明确写明记录范围内未发现问题，不留模板占位项。

decision只能是`pending`、`changes_requested`、`approved`、`blocked`之一。任何未解决P0/P1、D1–D7范围/安全保护回退、或关键验证证据缺失时不可批准。静态审查与未执行检查要如实区分；若范围内Finding仅为可接受的低优先级文档建议，可在解释清楚后判`approved`，但不能把`NOT_RUN`改成PASS。请在最终答复中给出decision和完整报告正文；不需要创建文件。
