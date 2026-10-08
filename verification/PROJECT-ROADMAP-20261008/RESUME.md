# 全项目任务规划恢复点

最新工作点：P08 D1–D7已确认；DSH R3对`1ad05d99`返回`changes_requested`，R1的4项P1与R2 N-01..N-06均closed，N-07/N-08由R4独立关闭；R4-01..03修订固定于`af1ddeec`，DSH R5独立Review材料已备妥、待正式派发。报告与恢复状态见[最新恢复点](../P08/RESUME.md)。后继产品实现未释放；下方历史审计与规划材料按各自时间点保留。

**当前位置：P08状态=`in_review`；R4已关闭N-07/N-08，R4-01..03修订于`af1ddeec`，R5 Prompt/Handoff已备妥、待正式派发。P系列完成0/21，in_review 1，proposed / 未释放20。产品实现未释放；R5 Review与Codex集成Gate通过后再按Plan依赖选择下一Task。**

2026-10-08 最新编号裁决：当前21个候选任务沿用 `P01–P21`，状态为 `proposed / 未释放`；仅统一编号，不释放实施、不改原有任务及完成记录。原始审计、台账与历史验证日志保留为固定快照。

最新恢复约束（2026-10-08）：用户已将Qoder剔除本项目，当前未来UI/UX由ZCode主责，fallback_order=zcode,antigravity；恢复时以AGENTS/Plan/STATUS当前名单为准。旧审计报告、台账或共享skill默认候选不能恢复Qoder资格。人员调整基线=`main@5b8aed4d`，后续仅已知治理差量；当前无Active/released产品Task。人员变更检查见`qoder-retirement.log`，原代码审计与验证不重做。

- 时间：2026-10-08（Asia/Shanghai）。协调者：Codex。
- 授权：PLAN_ONLY；用户要求盘点、整体规划、中文图和额度中断恢复。未释放产品实现。
- 仓库：`G:/CODEX/New Manga`；branch=`main`；common-dir=`G:/CODEX/New Manga/.git`。
- 审计 base/head：`e4242ecd419eb0eea098d2f63b40f709aa5caeea`。
- ExecutionState：CHECKPOINTED；本轮规划盘点已完成，这是规划工作记录，不是产品 Task 状态。所有产品候选未释放。
- 既有 dirty：`.qoder-credits/report.json`；`.qoder-credits/通路探测__8602db50.canvas.tsx`；`verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/antigravity-dispatch.json`；同目录 `antigravity-dispatch.stderr.log`。保留，不 stage、不 reset/clean/stash。
- 已完成：Git Reality Check；三路GPT-6.1 Sol high审计与196节点台账；Core/Desktop调用链/产品可达性/Task集成祖先取证；REPORT/中文ROADMAP；Plan当前P01–P21 候选任务依赖/责任方/Gate；Status/Index/短Roadmap新入口；有界规划一致性核对。
- 当前工作点：完整规划已落盘。三审计及台账不再等待；规划一致性PC-01（此恢复点过时）已修订，PC-02（缺validation.log）已实际生成。生产代码零差量。
- 历史步骤（已被顶部P08恢复点取代）：复用报告准备P08完整产品范围、四页parity与验收矩阵，状态为 `proposed / 未释放`（尚未创建正式 Task 文件）。Codex负责范围/契约、ZCode另设计Task、DSH非作者Review；先按下列Git核验，不再全仓审计。产品取舍/Reader解冻待用户裁决，禁止直接实施后继产品候选任务。
- 本轮验证：`python verification/PROJECT-ROADMAP-20261008/verify_plan.py` EXIT=0；196唯一节点与分类/依赖、105新架构祖先、21规划节点/图无循环、局部导航链接、零生产差量、治理diff-check全部PASS，见validation.log。产品pytest/cargo/vitest/GUI/fresh build：NOT_RUN；历史测试仍限定原commit/环境。
- 已知：STATUS 顶部无 Active/released；Runner R-003 未释放；GC-2 设计与实现均已完成，实现集成 `cea610ed`，分发迁移 Gate 仍须遵守；早期设计 checkpoint 中的后继 proposed 已被后续交付取代。
- 恢复安全：恢复前比较 HEAD、branch、dirty 集合与 Plan/Status。相同则 RESUME_SAFE；有漂移记录 DRIFT_DETECTED，先分析，不覆盖。

本轮受控文件：`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`，以及本目录 `REPORT.md`、`ROADMAP.md`、`RESUME.md`、`core-audit.md`、`desktop-audit.md`、`plan-audit.md`、`planning-check.md`、`task-inventory.csv`、`verify_plan.py`、`validation.log`、`usage.json`。仅这些文件属于本轮规划交付。usage.json为本轮local trace统计，不是账户账单或Task事实源。

规划交付commit在本文件之后创建，避免自引用hash。恢复可运行 `git log -3 --oneline -- verification/PROJECT-ROADMAP-20261008` 找到实际交付提交；允许相对审计base出现本轮已知治理/证据差量，不把它自动当未知漂移。commit未出现时按本轮受控dirty集合续存，不推断已提交。不得回滚到审计base。

```powershell
Set-Location 'G:\CODEX\New Manga'
git status --short --branch
git rev-parse HEAD
git rev-parse --path-format=absolute --git-common-dir
Get-Content doc\STATUS.md -TotalCount 35
Get-Content verification\PROJECT-ROADMAP-20261008\RESUME.md
Get-ChildItem verification\PROJECT-ROADMAP-20261008
```

额度耗尽或会话断开不表示任务完成。恢复后直接转发：

> 在 G:/CODEX/New Manga 继续 PROJECT-ROADMAP-20261008 规划盘点。先读取 verification/PROJECT-ROADMAP-20261008/RESUME.md，核验 Live Git 与 doc/STATUS.md、doc/REBASELINE_PLAN.md。复用已落盘审计，不重复全库分析。只完成报告/任务路线图/恢复材料，不启动产品 Task，不覆盖既有 dirty 文件。若证据与检查点漂移，记录后由 Codex 决策。
