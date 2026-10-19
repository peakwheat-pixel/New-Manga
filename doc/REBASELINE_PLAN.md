# Project Rebaseline Plan —唯一DAG；运行见[STATUS](STATUS.md)。2026-10-15恢复完整产品路线；P22-REBASE-1已集成。范围与裁决见[REPORT](../verification/PROJECT-ROADMAP-RELEASE/REPORT.md)。
|节点/目标|依赖|状态|
|---|---|---|
|P01 台账 / P03 SFX入口 / P05 契约注记|—|done|
|P02 WebView|P08|限定关闭|
|P04 并发验收|P22|done|
|P06 GC补证|—|**done**（集成 d3342895）|
|P08 产品范围|—|done|
|ARCH-DOC-REBASELINE|P08|ready / integrated（AC7 消费者裁决待做）|
|P09 导入Core|P08/DOC|closed_with_limitations（集成 c6a7339f；AC3 由下项回补）|
|P09-AC3-DELETE-1|P09|closed_with_limitations（R3 changes_requested；HARDEN-1 接手）|
|P10 凭据通道 / P11 长任务契约|P08|**done**（c46c0df0 / ceca5721）|
|P12 书架导入|P09/UI/C1/FU2|**done**（集成 465e3001e）|
|P13 后台恢复|P09/P11/P13-C1|**done**（集成 8d7cad13）|
|P14 工作台|P13/UI|**done**（集成 2dc14cdd1）|
|P15 设置/Core/host|P15-C1/P10/UI|done（含 FU、HOST-1/2）|
|P16 阅读导出Core|P08/P13/C1|**done**（集成 e1be3082）|
|P17 阅读导出UI|P16/DOC/UI|**done**（集成 f18b7fe8f）|
|P15-C1 设置面契约|P10|**done**（集成 f07221313）|
|P18 JA/KO质量|P10/P13/DOC|closed_with_limitations（AC2门槛、AC5阻塞）|
|P19 四页安全E2E|P12/14/15/17/18/P04|closed_with_limitations（4c860d882）|
|P20 Windows发布|P19/P03/P06/DOC|ready|
|P20-MEM-OPT-1|P20|closed（AC1 完成；AC2 经调阈值消解）|
|P20-ISOLATION-1|P20|in_review|
|P20-AC4-FPS-1|P20|closed_with_limitations（AC3 PASS；AC5 依裁决）|
|GOV-DEBT-CLEANUP-1|P19/P20|blocked（待用户裁决）|
|GOV-DEBT-CLEANUP-2|—|ready|
|P20-CLOSE-BOUND-1|P20-ISOLATION-1|closed_with_limitations（R6）|
|P20-CLOSE-BOUND-HARDEN-1|P20-CLOSE-BOUND-1|closed_with_limitations|
|P09-AC3-DELETE-HARDEN-1|P09-AC3-DELETE-1|closed_with_limitations（未集成）|
|P09-PREVIEW-LIFECYCLE-RECLAIM-1|P09-AC3-DELETE-HARDEN-1|closed_with_limitations（AC6 未满足；未集成）|
|RUST-ENV-BASELINE-1|P20-CLOSE-BOUND-1|proposed|
|P07 交互补缺 / P21 旧栈归档|P02 / P20+另授权|proposed（均可选）|
|P22 响应归属|P22-REBASE-1|已集成；P04 不放行，H1/P2-1/13 与 BC-AC5 缺项保留。已完成见各节点行。|
READY 节点：ARCH-DOC-REBASELINE、P20、GOV-DEBT-CLEANUP-2。`in_review`：HARDEN-2。done：**33 项**。
