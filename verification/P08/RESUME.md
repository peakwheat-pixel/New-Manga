# P08 可恢复检查点

时间：2026-10-08 21:47（Asia/Shanghai）；Agent=Codex；TaskStatus=changes_requested；ExecutionState=ACTIVE（文档finding修订中）。

## 固定范围与Review工作区

仓库=`G:/CODEX/New Manga`；Owner branch/worktree=`main` / `G:/CODEX/New Manga`；common-dir=`G:/CODEX/New Manga/.git`。当前root HEAD=`80f1dacd9f6d6cbf4fe182576a5adf22b9734ef2`，这是首轮Review结果checkpoint；当前未提交的修订文件仅在P08/Plan/验证允许范围。P08原始base=`ab2f813c0ce311a6712002cafd852b9e7a258380`；首轮固定范围交付及DSH `reviewed_head`=`490f9bd9637de0812a3ef3d9bbfa754868d5c15f`，见[Handoff](../../doc/handoffs/P08-490f9bd9.md)。

独立Reviewer=DeepSeek Harness。首轮Review worktree=`G:/CODEX/New Manga.worktrees/P08-dsh-review-490f9bd`，detached HEAD=`490f9bd9637de0812a3ef3d9bbfa754868d5c15f`，status clean，common-dir与主仓一致。正式DSH CLI=`dsh --profile headless --json`，session=`session-f663b6eb-7648-4750-b84d-41becd54737b`，已挂载该精确worktree。正式结论=`changes_requested`：0 P0、4 P1、6 P2、5 P3观察；完整报告及SHA256见[Review报告](review-dsh-490f9bd.md)。DSH内部PowerShell无法启动（SetNamedSecurityInfoW Win32 5），因此其shell检查=`NOT_RUN`；DSH退出码=0。Codex已在固定head复跑三项文档检查，均EXIT=0；日志见[validation.log](validation.log)。

## 已完成

- D1–D7已确认；范围、193条D08验收映射、AC-SMOKE与12个总Gate、P09–P20建议切片均在固定head交付。Review报告指出验收真值对账、新架构/legacy基线边界、UI窗口AC实现路由、依赖/路径和证据准确性需修订。
- 首轮固定review worktree仍为`490f9bd...`且clean；其原报告和旧验证证据保持原样。本轮作者修订只改`verification/P08/**`、`doc/tasks/P08.md`与权威Plan/派生路线验证文件，不改生产代码或D08/D04/AD-001/Doc13源文件。
- DSH通路探测：`dsh --version`=`0.1.7-rc.2`；项目目录探测输出`收到`、EXIT=0。正式Review已派发，session如上。
- 原始首轮验证仍作为历史保留；Codex精确head验证、shell/interpreter路径与版本、工作区、HEAD和EXIT已追加在[validation.log](validation.log)。产品pytest/cargo/vitest/GUI/build/model仍为`NOT_RUN`。

## 当前工作点与下一步

当前：P1-2/3/4、P2-2/3/4/5/6的文档处置已写入工作树；P2-1在`bde69d3e`修正。P1-1需在修订提交后于精确新head上最后复跑并把环境头/EXIT写入日志和Task测试表。此次工作树验证（root HEAD=`80f1dacd...`＋上述未提交文档）`verify_scope.py`、`verify_plan.py`和`git diff --check`均EXIT=0，但不是新固定head的正式Review证据。下一步补Handoff/R2 Review prompt，提交修订交付，在全新clean linked worktree以新DSH session复审；保持P08=`changes_requested`，不释放P09–P20。AD-001要求另行授权Architecture Documentation Rebaseline Task；D08当前仍是Legacy production baseline，stack-specific AC不能直接作为Tauri新架构PASS。该文档重基线Task未登记，须在P09开发释放前完成AC-DOC门、在P18/P20或发布使用stack-specific AC前完成映射。

正式Review之前需核实当前Git状态。原主工作区中归原作者的dirty文件：`.qoder-credits/report.json`（modified）、`.qoder-credits/通路探测__8602db50.canvas.tsx`（untracked）、`verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/antigravity-dispatch.json`（untracked）、`verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/antigravity-dispatch.stderr.log`（untracked）。不得stage、覆盖、stash或清理；提交时只显式stage本Task路径。

## 验证与边界

范围/路线检查（在新固定head上复跑并记录shell、Python、worktree和HEAD）：

```powershell
python -X utf8 verification/P08/verify_scope.py
python -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py
git diff --check
```

产品能力与产品验收结果仍为`NOT_RUN`。P18质量真值/阈值/样本/版本须在资格方案实验Task前独立冻结；用户D1–D7不重问。Task只有新head正式Review findings闭合、Codex集成检查通过后才能`done`；P08完成后再依据权威Plan检查P01–P07及后继依赖，分别登记正式Task。
