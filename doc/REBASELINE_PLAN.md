# Project Rebaseline Plan
唯一DAG；运行见[STATUS](STATUS.md)。2026-10-15恢复完整产品路线；P22-REBASE-1已集成。
|节点/目标|依赖|状态|
|---|---|---|
|P01 台账|—|done|
|P02 WebView|P08|限定关闭|
|P03 SFX入口|—|done|
|P04 并发验收|P22|done|
|P05 契约注记|—|done|
|P06 GC补证|—|**done**（集成 d3342895）|
|P08 产品范围|—|done|
|ARCH-DOC-REBASELINE|P08|ready / integrated（AC7 消费者裁决待做）|
|P09 导入Core|P08/DOC|closed_with_limitations（集成 c6a7339f；AC3 由下项回补）|
|P09-AC3-DELETE-1|P09|ready|
|P10 凭据通道|P08|**done**（集成 c46c0df0）|
|P11 长任务契约|P08|**done**（集成 ceca5721）|
|P12 书架导入|P09/UI/C1/FU2|**done**（集成 465e3001e）|
|P13 后台恢复|P09/P11/P13-C1|**done**（集成 8d7cad13）|
|P14 工作台|P13/UI|**done**（集成 2dc14cdd1）|
|P15 设置维护 + Core/host|P15-C1/P10/UI|**全部 done**（P15/FU1/FU2/1A/1B/1C/HOST-1/**HOST-2**）|
|P16 阅读导出Core|P08/P13/C1|**done**（集成 e1be3082）|
|P17 阅读导出UI|P16/DOC/UI|**done**（集成 f18b7fe8f）|
|P15-C1 设置面契约|P10|**done**（集成 f07221313）|
|P18 JA/KO质量|P10/P13/DOC|closed_with_limitations（AC2 待用户门槛；AC5 待解阻）|
|P19 四页安全E2E|P12/14/15/17/18/P04|closed_with_limitations（集成 4c860d882）|
|P20 Windows发布|P19/P03/P06/DOC|ready|
|P20-MEM-OPT-1|P20|closed（AC1 完成；AC2 经调阈值消解）|
|P20-ISOLATION-1|P20|in_review|
|GOV-DEBT-CLEANUP-1|P19/P20|ready（治理债务清理）|
|P20-CLOSE-BOUND-1|P20-ISOLATION-1|in_review（授权第 3 轮）|
|P07 交互补缺 / P21 旧栈归档|P02 / P20+另授权|proposed（均可选）|
|P22 响应归属|P22-REBASE-1|切片已集成（P04 不自动放行；H1/P2-1/13 缺失与 BC-AC5 PARTIAL 保留）|
已完成：ROADMAP-RELEASE、P22-REBASE-1、P04/06/10/11/09/P09-FU1/13/13-C1/16/16-C1、FEAT-IMPORT-MULTI-1；P18/P19 closed_with_limitations。
DOC=[架构映射Task](tasks/ARCH-DOC-REBASELINE.md)已集成未关闭（AC7 已完成）；UI=四页经ZCode设计审查；P13*仅停写；P02/P22-REBASE-1 已集成，P04 不自动放行；H1/P2-1/13 项缺失与 BC-AC5 PARTIAL 保留。范围/Gate 见[本轮裁决](../verification/PROJECT-ROADMAP-RELEASE/REPORT.md)
READY 节点：ARCH-DOC-REBASELINE、P20、P09-AC3-DELETE-1、GOV-DEBT-CLEANUP-1。done：**33 项**；P19 `closed_with_limitations`；DOC AC7 已完成；P20 经授权激活。
