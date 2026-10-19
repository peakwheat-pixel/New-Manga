# Project Rebaseline Plan —唯一DAG；运行见[STATUS](STATUS.md)。范围/裁决见[REPORT](../verification/PROJECT-ROADMAP-RELEASE/REPORT.md)。
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
|GOV-DEBT-CLEANUP-2|—|closed_with_limitations（AC1–AC6/AC8 达成；AC7 仅完成 61 项候选分类，唯一最终证据判定未做；closeout r14）|
|GOV-RESOURCE-MANIFEST-JSON-1|GOV-PLAN-BUDGET-1|done（外部 JSON Manifest 检查器；19/19 用例；集成 3fe78a67c）|
|P19-UI-MANIFEST-VIEW-1|GOV-RESOURCE-MANIFEST-JSON-1|closed_with_limitations（AC1/AC2/AC4/AC5/AC6 达成；AC3 因 4→10 错误清单失败；按 Codex r11 保留修正）|
|GOV-RESOURCE-MANIFEST-SAME-LOCATION-1|GOV-RESOURCE-MANIFEST-JSON-1|done（同源/空/\-\ 目的地语义；32/32 用例；集成 4b545eada；P19 错误 9→4）|
|GOV-UNTRACKED-BACKLOG-1|—|done（1591 个未入库文件的分类与边界化；最小镜像集 3 文件；P1 由 GOV-EOL-PIN-1 修复）|
|GOV-EOL-PIN-1|GOV-UNTRACKED-BACKLOG-1|done（为 hash-pinned 证据固定 LF；renormalize 无字节变化；worktree 复现通过）|
|GOV-EVIDENCE-UNIQUE-1|GOV-DEBT-CLEANUP-2|done（AC 证据覆盖核验；83 AC：3 COVERED / 17 PARTIAL / 19 GAP / 42 N/A；四轮 Review）|
|GOV-SOURCE-RECORDS-1|GOV-EVIDENCE-UNIQUE-1|done（EXPORT-REVEAL-1 补勾 6、P15 补勾 6；AC4 因 ③ BLOCKED 保留未勾；遗留三项已裁定拆专项）|
|GOV-AC-GATE-1|GOV-SOURCE-RECORDS-1|done（v3 AC 门禁；12 夹具；窄 scope 不清算存量；两轮 Review）|
|GOV-PIN-LINEAGE-1|GOV-SOURCE-RECORDS-1|blocked（r27 撤回 r25 的 blob-only 方案；187 个 pin 实为 worktree basis；40 项待诊断）|
|GOV-EVIDENCE-DIR-SWEEP-1|GOV-SOURCE-RECORDS-1|done（19 文件盘点；5 项补登记；0 个 ARCHIVE；两份失败日志保留）|
|GOV-P15-MANIFEST-1|GOV-SOURCE-RECORDS-1|done（P15 manifest 重建；4 资源含 3 个实测 junction；原地集成已验证）|
|P20-CLOSE-BOUND-1|P20-ISOLATION-1|closed_with_limitations（R6）|
|P20-CLOSE-BOUND-HARDEN-1|P20-CLOSE-BOUND-1|closed_with_limitations|
|P09-AC3-DELETE-HARDEN-1|P09-AC3-DELETE-1|closed_with_limitations（未集成）|
|P09-PREVIEW-LIFECYCLE-RECLAIM-1|P09-AC3-DELETE-HARDEN-1|closed_with_limitations（AC6 未满足；未集成）|
|GOV-PLAN-BUDGET-1|—|done|
|RUST-ENV-BASELINE-1（P20-CLOSE-BOUND-1）/ P07交互补缺（P02）/ P21旧栈归档（P20+另授权）|—|proposed（P07/P21可选）|
|P22 响应归属|P22-REBASE-1|已集成；P04 不放行，H1/P2-1/13 与 BC-AC5 缺项保留。已完成见各节点行。|
READY 节点：ARCH-DOC-REBASELINE、P20。blocked：GOV-PIN-LINEAGE-1。in_review：HARDEN-2。done：**41 项**。
