# Project Rebaseline Plan

唯一DAG；运行见[STATUS](STATUS.md)。2026-10-15恢复完整产品路线；P22-REBASE-1已集成。

|节点/目标|依赖|状态|
|---|---|---|
|P01 台账|—|done|
|P02 WebView|P08|限定关闭|
|P03 SFX入口|—|done|
|P04 并发验收|P22|done|
|P05 契约注记|—|done|
|P06 GC补证|—|proposed|
|P07 交互补缺|P02|proposed|
|P08 产品范围|—|done|
|ARCH-DOC-REBASELINE|P08|ready / integrated（AC7 消费者裁决待做）|
|P09 导入Core|P08/DOC|proposed（待用户选定首发格式）|
|P10 凭据通道|P08|**ready**（2026-10-15 释放待认领）|
|P11 长任务契约|P08|**done**（集成 ceca5721）|
|P12 书架导入|P09/UI|proposed|
|P13 后台恢复|P09/P11|proposed（P11 契约已冻结可消费）|
|P14 工作台|P13/UI|proposed|
|P15 设置维护|P10/P13*/UI|proposed|
|P16 阅读导出Core|P08/P13/DOC|proposed|
|P17 阅读导出UI|P16/DOC/UI|proposed|
|P18 JA/KO质量|P10/P13/DOC|proposed|
|P19 四页安全E2E|P12/14/15/17/18/P04|proposed|
|P20 Windows发布|P19/P03/P06/DOC|proposed|
|P21 旧栈归档|P20+另授权|可选proposed|
|P22 响应归属|P22-REBASE-1|切片已集成|

本轮：[PROJECT-ROADMAP-RELEASE](tasks/PROJECT-ROADMAP-RELEASE.md) done；[P22-REBASE-1](tasks/P22-REBASE-1.md) done（集成4e5c71d9）；[P04](tasks/P04.md) done（集成 7bfcf16a）。[ARCH-DOC-REBASELINE](tasks/ARCH-DOC-REBASELINE.md) `ready / integrated`（交付 `70208144`、R1 Review `79ed01fd`、集成 merge `4227e8b5`），待 AC7 消费者裁决。[P11](tasks/P11.md) **done**：交付 `c7922ae1`、Review `09797eab`、集成 `ceca5721`。
DOC=[架构映射Task](tasks/ARCH-DOC-REBASELINE.md)已集成但未关闭；UI=四页分别经ZCode设计审查；P13*仅备份停写。详细范围/Gate见[本轮裁决](../verification/PROJECT-ROADMAP-RELEASE/REPORT.md)，为本Plan持续冻结的Gate输入，Task关闭不撤销引用；状态仍只在本Plan。
P02新时点链与P22-REBASE-1已集成；P04前置满足但不自动放行，仍待独立释放授权；旧H1/P2-1/13项缺失、BC-AC5 PARTIAL及产品backlog保留。
READY 节点：ARCH-DOC-REBASELINE、P10。ARCH-DOC-REBASELINE 的 AC7 待 P09/P18/P20/P16/P17 冻结后裁决；P09 释放需先由用户选定首发输入格式与最小目标。
