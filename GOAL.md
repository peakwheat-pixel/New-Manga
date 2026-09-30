# Active Goal：检测器家族遗留清算（2026-10-01，自治执行模式）

用户 2026-10-01 下发「全自动自治执行模式」指令（完整执行授权，规则：自我规划/推进/执行/验证/总结，停止条件=外部阻塞）。编排会话（代行 Codex）自主设定本轮 Goal：

**Goal：检测器家族遗留技术债清算**——把 M2-PROD-DETECT-1/2 收口后登记的全部遗留 slice 清算完毕，使检测器家族（评估 C4→校准 C1→生产集成 DETECT-1→发布形态 DETECT-2→命令面闭环 DETECT-3）全链无遗留缺口。

## Task 集合

| ID | 内容 | 规模 |
|---|---|---|
| T1 = M2-PROD-DETECT-3 | core_service 新增 `core.detect` 命令（协议 minor bump 1.0→1.1，wadding 扩展）+ frozen 进程内真实 detect 端到端验证 → **闭合 M2-PROD-DETECT-2 AC5 PARTIAL** | 大件（含重建+GATE+探针） |
| T2 = M2-MANGA-WEIGHTS-SOP | manga 权重 fetch/verify 脚本与安装 SOP（对照 fetch_doctr_weights.py；DETECT-1 遗留 slice②/R6） | 小件 |
| T3 = M2-FIX-REGISTRY-READINESS-ENV | test_registry_readiness 环境断言条件化（断言 venv 无 torch 与 T1.1.1 后事实冲突，base 同败；遗留 slice③） | 小件 |

## 执行模式

子 agent Owner（独立 worktree/branch）+ DSH 非作者 Review + 编排会话代行 Codex 集成；T1 与 T2/T3 并行派发（独立子 agent、独立 worktree）。代理裁决全部留痕于各 release evidence；熔断处置按 DETECT-2 先例（半成品 git diff 核实→新 agent 补完成并入自己 commit）。

## 停止条件

三个 Task 全链闭环（done）或遇不可自行解决的外部阻塞；审查发现的产品级取舍（如协议面语义争议）留裁决记录不阻塞其余 Task。
