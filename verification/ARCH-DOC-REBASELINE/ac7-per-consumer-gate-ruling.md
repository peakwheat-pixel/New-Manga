# ARCH-DOC-REBASELINE AC7 逐消费者 Gate 裁决

- 裁决角色：**DeepSeek Harness（dsh）**——本 Task 的 **Reviewer（非 Owner）**；Owner 为 Antigravity
- 授权来源：用户裁决（2026-10-18）"授权 dsh 直接完成 DOC AC7 并激活 P20"；Coordinator=dsh, epoch 7
- 被审固定 head：`integration_commit 4227e8b509e3a42736229b93df4bd9eec548153d`（已用 `git merge-base --is-ancestor` 验证为 main 祖先）
- 前置：`dsh-review-r1.md`（`decision: approved_with_conditions`，AC1–AC6 证据形态与范围合规通过；AC7 消费方裁决待做）

## 1. AC7 的三项构成与结论

| AC7 构成 | 结论 | 依据 |
|---|---|---|
| 固定 head 非作者 Review | **PASS** | `verification/ARCH-DOC-REBASELINE/dsh-review-r1.md`：Reviewer=DSH ≠ Owner=Antigravity，固定 `base_commit=4ef92f3d…`，逐 AC 判定并记录条件 |
| Codex 集成 | **PASS** | `integration_commit 4227e8b5…` 已是 main 祖先（本轮实测 exit 0） |
| **逐消费者 Gate 裁决** | **完成（本节）** | 见 §2 |

## 2. 逐消费者裁决（AC1–3→P09、AC4→P18、AC5→P20、AC6→P16/P17）

裁决口径（按 AC7 原文"可按消费者拆独立已审交付但须另行冻结"）：本 Task 交付的是**映射与证据 Gate 定义**，不是消费者自身的实测结论。因此逐消费者裁决只回答两件事：**该消费者所需的映射是否已就位、其证据 Gate 是否已明确**；消费者是否通过须由其自身 Task 自证。

| 消费者 | 消费 AC | 映射证据（存在且已 pin） | 消费者须自证的内容 | 裁决 |
|---|---|---|---|---|
| **P09** | AC1–AC3 | `ac1-coverage-and-sources.md`、`ac2-cross-document-consistency.md`、`ac3-four-pages-and-deferred.md` | 01–08 覆盖/跨文档一致/四页设计的**产品侧**结论（本 Task 维持 Owner 的 PARTIAL，未决项已逐条列出） | **接受（附条件）**：未决项须在 P09 的 Gate 前闭环；不得以本 Task 的映射替代设计审查 |
| **P18** | AC4 | `ac4-p18-quality-and-responsibility.md` | JA/KO、无字页、质量 AC 的**真实样本/真值/阈值/version/device/model/endpoint** 证据；**旧结果不继承** | **接受**：责任矩阵与阈值保留已明确，P18 须自行产出实测证据 |
| **P20** | AC5 | `ac5-p20-nfr-stack-rebaseline.md`（6 个 NFR 领域：冷启动 ≤2.0s、空闲驻留 ≤350MB、交互 ≤50ms/60FPS、打包与卸载、无 GPU 优雅降级、故障隔离与自愈） | 新二进制的**端到端实测**：整棵进程树 Working Set/Private Bytes、WPR 采样、CSV 时序与内存曲线 | **接受**：阈值**未放宽**，逐项映射与风险防范明确；P20 发布 Gate 须自证实测（**本裁决不构成 P20 的验收通过**） |
| **P16 / P17** | AC6 | `ac6-p08-fmt-traceability.md` | PNG/ZIP/CBZ/PDF/文本转录的长期验收追踪 | **接受（附条件）**：消费者在**消费对应格式契约前**须确认 AC6 追踪项仍有效 |

## 3. 结论与限制

- **AC7 完成**：三项构成全部达成，逐消费者裁决如上。
- **本 Task 不得据此标 `done`**：AC1–AC3 仍为 PARTIAL、AC4–AC6 的实测部分仍为 NOT_RUN（属消费者责任），按 AC7 原文"某项未完成不标整 Task done"。本 Task 保持 `ready`；其映射交付已可被消费者引用。
- **本裁决的边界**：不替任何消费者作出其自身验收结论；不放宽任何阈值；不修改产品代码、Schema、依赖或模型。
- **对 P20 的直接含义**：P20 可被激活（其消费的 AC5 映射已就位），但 P20 的发布 Gate 须**自行**完成 NFR 实测与既有发布 Gate（`bundle==resource` + 启动 smoke，本轮已实测通过）。
