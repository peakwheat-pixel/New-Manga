# P08 可恢复检查点

时间：2026-10-08（Asia/Shanghai）；Owner=Codex；TaskStatus=blocked；ExecutionState=CHECKPOINTED；原因=正式DSH Reviewer未认领/派发，不是用户尚未回答。

仓库G:/CODEX/New Manga；branch=main；common-dir=G:/CODEX/New Manga/.git；Task base=ab2f813c0ce311a6712002cafd852b9e7a258380；本轮输入HEAD=d44cb5cc05820a36804e3e4d1434ad23b1f2ea87。固定范围交付head由下一份Handoff和DSH-REVIEW-PROMPT记录；恢复须实测Live Git，不回退到base。

已完成：D1–D7全部确认，见[SCOPE_DRAFT](SCOPE_DRAFT.md)决策表；193条D08编号AC＋AC-SMOKE＋12总Gate覆盖；新增MOBI/CBZ/PDF/文本验收；P09–P20切片和中文图已同步。全库DB＋Managed Copy备份、模型下载、现行全部P0/P1维护和完整主流程均纳入；基础Reader已解冻，扩展延期明确。产品能力和全部验收结果仍NOT_RUN。

下一确切步骤：对固定范围交付进行DSH非作者正式Review，见[指令](DSH-REVIEW-PROMPT.md)；当前未派发/认领，无正式批准。闭合发现→Codex集成检查→P08 done→另行释放后继Task。P18补充质量真值/阈值在资格方案实验前冻结；禁止将未知指标或未执行结果当PASS。不重复问D1–D7，不重跑全库审计。

恢复核验：git status --short --branch；git rev-parse HEAD；git rev-parse --path-format=absolute --git-common-dir；读取doc/STATUS.md、doc/tasks/P08.md、固定Handoff。若新增产品/规则差量记录DRIFT_DETECTED，分析后继续，不覆盖。

既有dirty归原作者：.qoder-credits/report.json、.qoder-credits/通路探测__8602db50.canvas.tsx，以及Runner Guard的antigravity-dispatch.json/.stderr.log；不stage/clean/reset/stash。

验证：python verification/P08/verify_scope.py；python verification/PROJECT-ROADMAP-20261008/verify_plan.py；git diff --check。结果与被测HEAD见[validation.log](validation.log)。产品pytest/cargo/vitest/GUI/build/模型全部NOT_RUN（本轮只改文档）。

额度耗尽不代表Task完成。恢复后复用审计、决策与交付；故障转移ZCode→Antigravity，Qoder仍退出；Owner不能审自己。checkpoint之后可能有Handoff/验证证据提交，按实际Git续跑，不要求HEAD等于旧记录。
