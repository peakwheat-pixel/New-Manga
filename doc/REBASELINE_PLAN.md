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
|P07 交互补缺|P02|proposed|
|P08 产品范围|—|done|
|ARCH-DOC-REBASELINE|P08|ready / integrated（AC7 消费者裁决待做）|
|P09 导入Core|P08/DOC|closed_with_limitations（集成 c6a7339f；AC3 受限）|
|P10 凭据通道|P08|**done**（集成 c46c0df0）|
|P11 长任务契约|P08|**done**（集成 ceca5721）|
|P12 书架导入|P09/UI/C1/FU2|proposed（Core 已接通；待 UI 设计 + host issuer）|
|P13 后台恢复|P09/P11/P13-C1|**done**（集成 8d7cad13）|
|P14 工作台|P13/UI|proposed|
|P15 设置维护|P10/P13*/UI|proposed|
|P16 阅读导出Core|P08/P13/C1|**done**（集成 e1be3082）|
|P17 阅读导出UI|P16/DOC/UI|proposed|
|P18 JA/KO质量|P10/P13/DOC|closed_with_limitations（AC2 待用户门槛；AC5 待解阻）|
|P19 四页安全E2E|P12/14/15/17/18/P04|proposed|
|P20 Windows发布|P19/P03/P06/DOC|proposed|
|P21 旧栈归档|P20+另授权|可选proposed|
|P22 响应归属|P22-REBASE-1|切片已集成|

本轮完成：PROJECT-ROADMAP-RELEASE、P22-REBASE-1、P04、P06、P10、P11、P09、P09-FU1、P13、P13-C1、P16、P16-C1 均已 done；P18 closed_with_limitations（AC2 待用户门槛、AC5 待解阻）；详见 [STATUS](STATUS.md) 与各 Task。ARCH-DOC-REBASELINE `ready / integrated`，待 AC7 消费者裁决。
DOC=[架构映射Task](tasks/ARCH-DOC-REBASELINE.md)已集成但未关闭；UI=四页分别经ZCode设计审查；P13*仅备份停写。详细范围/Gate见[本轮裁决](../verification/PROJECT-ROADMAP-RELEASE/REPORT.md)，为本Plan持续冻结的Gate输入，Task关闭不撤销引用；状态仍只在本Plan。
P02新时点链与P22-REBASE-1已集成；P04前置满足但不自动放行，仍待独立释放授权；旧H1/P2-1/13项缺失、BC-AC5 PARTIAL及产品backlog保留。
READY 节点：ARCH-DOC-REBASELINE、HOST-ISSUER-1-C1。C1 冻结 host→Core grant 注册通道后再恢复 HOST-ISSUER-1。
