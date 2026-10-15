# Project Rebaseline Plan

唯一DAG；运行见[STATUS](STATUS.md)。2026-10-15恢复完整产品路线。

|节点/目标|依赖|状态|
|---|---|---|
|P01 台账|—|done|
|P02 WebView|P08|限定关闭|
|P03 SFX入口|—|done|
|P04 并发验收|P22|blocked|
|P05 契约注记|—|done|
|P06 GC补证|—|proposed|
|P07 交互补缺|P02|proposed|
|P08 产品范围|—|done|
|P09 导入Core|P08/DOC|proposed|
|P10 凭据通道|P08|proposed|
|P11 长任务契约|P08|proposed|
|P12 书架导入|P09/UI|proposed|
|P13 后台恢复|P09/P11|proposed|
|P14 工作台|P13/UI|proposed|
|P15 设置维护|P10/P13*/UI|proposed|
|P16 阅读导出Core|P08/P13|proposed|
|P17 阅读导出UI|P16/UI|proposed|
|P18 JA/KO质量|P10/P13/DOC|proposed|
|P19 四页安全E2E|P12/14/15/17/18/P04|proposed|
|P20 Windows发布|P19/P03/P06/DOC|proposed|
|P21 旧栈归档|P20+另授权|可选proposed|
|P22 响应归属|P22-REBASE-1|in_review来源|

本轮：[PROJECT-ROADMAP-RELEASE](tasks/PROJECT-ROADMAP-RELEASE.md) in_review；[P22-REBASE-1](tasks/P22-REBASE-1.md)拟释放，审查前proposed。
DOC=架构文档Gate未关闭；UI=四页分别经ZCode设计审查；P13*仅备份停写。详细范围/Gate见[本轮裁决](../verification/PROJECT-ROADMAP-RELEASE/REPORT.md)，为本Plan展开表。
P02新时点链已集成；旧H1/P2-1/13项缺失、BC-AC5 PARTIAL及产品backlog保留，不自动放行P22/P04。
READY 节点：无。
