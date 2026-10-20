# ARCH-DOC-REBASELINE 收口裁定（r37）

日期：2026-10-20  
裁定人：Codex（Lead / Architect / Integrator）  
范围：裁决 ARCH-DOC-REBASELINE 的 Gate/消费层拆分、各项 Gate 完成度、P18 限制链。只新增本文件；未修改 Task、STATUS、Plan、既有 verification、代码、测试或治理工具；未调用 `coordinator-lease.py`，未执行 Git 写命令。

## 裁定摘要

1. **选方案 A，但按“7 条 Gate + 1 条消费处置汇总”落结构，不把 7 个消费者的最终技术通过拆成 ARCH-DOC-REBASELINE 的 7 条必过 AC。** Gate Task 必须验收映射、规范和责任；消费者是否通过自己的技术 Gate，由消费者 Task 判定。若消费状态仍要求全部 PASS，本 Task 仍会无期限等待，拆分只会改名。
2. **当前不是 7/7 Gate 全部完成。** AC1–AC5、AC7 的规范/映射/裁决 Gate 已有证据；AC6 的格式追踪和安全要求已定义，但 `SEC-FMT-001..004` 与外部阅读器验证没有当前活动的实现/验收 Task。AC6 的要求有文字，不等于责任已实际分派，故其 Gate 的责任闭环仍缺一项。
3. **消费结果不得反向阻止本 Task 的规范 Gate 被判完成，也不得被改写成 PASS。** 消费处置汇总应允许登记 `MET`、`PARTIAL`、`BLOCKED`、`LIMITATION/UNOBSERVED` 等真实结果；已具名负责人、后续 Task 或经授权接受的限制及证据引用齐备后，消费处置本身即可关闭。
4. **P18 不自动重开、不要求重判通过。** `DETECT-TILING-1` 证明当前检测路径会在解码前拒绝超限 PNG；这保留为能力限制，不证明 JA/KO 端到端质量验证已完成，也不能推出所有可能素材/解码路径永久不可验证。ARCH AC4 消费状态保留 `PARTIAL`，并注明重测未发生；若以后决定停止补测，须记录获授权接受的 limitation，不能补勾 `MET`。
5. Task frontmatter 当前为 **`governance_version: 2`，不是 3**。协作协议 §4.3 的 lifecycle v3 `<<STATUS>>` 标记只适用于 v3 Task；已释放的 v2 Task 不因拆分 AC 自动升级。不得仅为这次结构裁定将它改成 v3。

## 1. 收口结构：7 + 1

建议后续在获得对应 Task 生命周期更新授权时，将原 AC 改写为以下 7 条 Gate AC，加一条消费处置汇总 AC。这里给出的措辞是裁定文本，不是对现有 Task 文件的改写；本轮授权只允许写本裁定文件。

### AC1–AC7-GATE 建议措辞

- **AC1-GATE：** 逐份核验 01–08 的覆盖；为新技术架构、权限边界和 UI 映射指定正式来源；明确 Legacy/Historical 内容、范围边界及其与目标架构的对应关系，并提供可复核引用。该项验收规范与映射是否确立，不验收具体 React 组件渲染或 Tauri IPC 编译。
- **AC2-GATE：** 对领域模型、Pipeline、版本/Revision、受控来源、持久化及错误语义提供逐项跨文档一致性对照；记录新栈 IPC/领域服务集成验证的消费者、Gate 和证据要求。该项不要求消费者集成测试已通过。
- **AC3-GATE：** 正式确立四个一级页面、默认书架、基础 Reader 与延期项，并证明其与 01/04/05/08 一致；明确 React 视觉/交互设计须由 ZCode 的独立设计 Gate 审查，文档映射不能代替设计审查。
- **AC4-GATE：** 将 P18 的 JA/KO、无字页及质量验收项映射到新链；定义真实样本、真值、阈值及 `version/device/model/endpoint` 的证据责任，并明确旧结果不继承、消费者实测由 P18 或其经授权的后续 Task 出具。
- **AC5-GATE：** 逐项映射 P20 的 Tauri/WebView2/Python sidecar/Windows/UI/可选模型 NFR，原要求及阈值不得降低；明确各项测量方法、环境矩阵、证据字段和消费者 Gate。
- **AC6-GATE：** 建立 P08-FMT PNG/ZIP/CBZ/PDF/文本格式的长期追踪表；为导入/导出契约、`SEC-FMT-001..005`、外部阅读器互操作验证逐项指定责任 Task/Owner、前置关系、证据和未满足时可用的限制处置。仅在这些责任均有活动 Task 或经授权的 limitation 接收路径后才算 Gate 达成。
- **AC7-GATE：** 对固定交付 head 完成非作者 Review 与 Codex 集成核验，并对每个消费者给出“映射已就位/未就位、消费者须自证事项、接受/附条件/拒绝”的逐项裁决；不替消费者判定其自身技术结果。

### 汇总 AC-CONSUMPTION-DISPOSITION 建议措辞

- **AC-CONSUMPTION-DISPOSITION：** 对 AC1–AC6 所列每个消费者逐项登记消费状态、证据引用、负责的消费者 Task/Owner，以及未完成项的后续路径或经授权接受的 limitation；AC7 登记各消费者是否已作出 Gate 裁决。状态可以是 `MET`、`PARTIAL`、`BLOCKED` 或 `LIMITATION/UNOBSERVED`，不得把消费者未通过/未运行改写为 PASS。完成登记、责任可追踪且无未裁决的映射/所有权空洞，即达成此项；它不要求所有消费者技术 AC 最终通过。

采用 7+1 的原因：消费方的成功/失败应保留在其自身 Task；本 Task 只对它们的映射和交接处置负责。7 条独立 `ACn-CONSUMED` 会再次把本 Task 的终态绑定到 P09、P18、P20、P16/P17、ZCode、第二环境和后续格式安全 Task 的执行时点，复现本次问题。以上汇总 AC 仍要求逐消费者可审计，避免用一个总状态掩盖遗漏。

## 2. Gate 层完成度逐项判断

| AC | Gate 层判断 | 消费层未完成事项 / 证据边界 |
|---|---|---|
| **AC1** | **已达成。** 01–08 覆盖、AD-001 正式来源、权限与 UI 映射在报告中建立；报告把组件渲染和 IPC 编译测试明确列为消费验证。 | Tauri IPC Schema 代码级编译、React 组件具体渲染由后续实现 Task 验证。不得因其未测而把 Gate 映射本身判失败。 |
| **AC2** | **已达成。** 六个跨文档维度有逐项对照；新栈集成测试已明确属于 P09 消费验证。 | IPC 与领域服务集成自动化套件尚未跑通，由 P09/对应实现 Gate 负责。 |
| **AC3** | **已达成。** 四页、默认书架、基础 Reader 和延期项有跨文档核验；独立 ZCode 设计 Gate 的责任边界已写明。 | 具体视觉规范、原型和前端设计审查未交付；这不是文档 Gate 的通过条件，但设计 Gate 本身仍须由 ZCode 完成后才可称设计验收通过。 |
| **AC4** | **已达成。** 新链映射、七维证据责任及历史结果不继承原则均已建立，P18 被指定为消费者。 | P18 没有在 `ImportPages` 可用后重跑质量链；现存旧运行不能证明新链质量。状态应继续如实记 `PARTIAL`/未验证。 |
| **AC5** | **已达成。** Stack-specific NFR 映射及阈值/证据 Gate 已明确。 | 现有补充实测为单台 Win11 + RTX 5070 Ti；不能代表 Win10/i5/8GB 无独显环境。双环境证据仍属消费者实测，不能因现有单机数据宣称完全满足。 |
| **AC6** | **部分达成，当前唯一 Gate 责任缺口。** 格式追踪表、前置要求和 `SEC-FMT` 定义存在；但 `SEC-FMT-001..004` 及外部阅读器验证没有活动承接 Task/Owner。不能仅凭 P16/P17 曾被列作消费者，就断言其已接受这项未完成工作；两 Task 已 `done`，且 r33 已指出格式安全要求缺少执行 Task。 | 导出往返测试通过只覆盖部分消费验证。`SEC-FMT-005` 经 DETECT 系列获得部分实现/限制证据，不能代表另外四项安全要求或外部互操作测试已通过。AC6-GATE 在责任 Task/Owner 建立或授权接受这些限制前不得标 `MET`。 |
| **AC7** | **已达成。** 固定 head 非作者 Review、Codex 集成及 P09/P18/P20/P16/P17 逐消费者裁决均有证据。 | 各消费者自身 Gate 的后续结果须进入消费处置汇总，不是 AC7 原裁决的重做理由。 |

**结论：当前 Gate 部分为 6 项达成、AC6 部分达成，不是 7/7。** 因此“规范全写完、只差下游”对 AC1–AC5、AC7 成立，但对 AC6 不完全成立：规范已写，执行责任没有活动落点。这个空洞应通过明确后续 Task/Owner，或由有权者接受具体限制来关闭；不能把它藏进下游等待列表。

## 3. AC6 / `SEC-FMT-005` 与 DETECT 限制的边界

- `DETECT-TILING-1` 的限制包括：真实超限 JPEG 样本不存在；JPEG 分支用合成样本，只支持拒绝路径证据；当前固定像素上限不随物理内存变化；WEBP 不在 `core.detect` 路径。Task 以 `closed_with_limitations` 收口，保留这些限制。
- `DETECT-MEMORY-GUARD-1` 已实现可用物理内存探测和拒绝提示，但其 closeout 仍保留 L1–L7：正常机器上该防御判据不触发、仅单机数据、阈值未调优、转换峰值未直接测量、不得宣传为 OOM 防护完成态等。
- 因此，只能说 `SEC-FMT-005` 的特定内存检查能力已有实现，且受限拒绝路径有证据；不得据此声称超大 PNG 已分块处理、超限页能完成检测，或整个 `SEC-FMT-005` / `SEC-FMT-001..005` 已满足。
- `SEC-FMT-001..004` 与 CBZ/PDF 外部阅读器互操作仍须有可追踪的后续承接，或由有权者逐项接受 limitation。WEBP 不在 `core.detect` 不构成它在其它导入路径已通过安全验收的证据。

## 4. P18 与 ARCH AC4 的裁定

**P18 不自动重开，也不要求改判。** P18 的现有状态 `closed_with_limitations` 和 AC2/AC5 未完成事实继续有效。`ImportPages` 在 P18 关闭后已实现并有调用/测试证据，只能解除旧记录中的一个技术阻塞；它不能代替重跑。

`DETECT-TILING-1` 记录的真实超限 PNG（`2946×4167`）在当前阈值下于解码前被拒绝，P18 的 JA/KO 最小真实切片因而不能用该页走完检测链。PNG 无法通过当前检测器“分块解码”的 limitation 对这个路径是真实限制；它不能证明换用适合的素材、获准调整实验输入、或未来使用不同解码/切片策略仍必然失败。P18 另外还存在产品发布门槛、模型权重/端点、真值等独立前置，不能只看 `ImportPages` 或像素上限推断整个 AC5 永无可能。

ARCH AC4 消费层裁定：

- 现有 P18 真实运行记录证明曾进行运行尝试；`ImportPages` 修复后无重测，不能判 `MET`。
- 保持 AC4 消费状态 **`PARTIAL`**（已执行过旧链尝试，但新链质量结果未验证），并在消费处置登记中加入当前检测输入限制及 P18 的其它独立阻塞。
- 不让 P18 将其 AC5 改成 PASS；也不要求 P18 为迎合 ARCH AC4 而修改已生效的 `closed_with_limitations`。如用户/授权者决定不再重测，应对“新链 JA/KO 质量未验证”明确接受 limitation；ARCH AC4 仍只能记 limitation/未完成，不能补勾为技术通过。
- 若要补测，须先满足 P18 产品门槛、许可素材/真值、模型/端点和可执行输入等前置，再由 Codex 冻结窄范围补测 Task；不得以本裁定自动重开 P18 或扩大 DETECT Task。

## 5. 治理版本与状态标记

当前 `doc/tasks/ARCH-DOC-REBASELINE.md` frontmatter 实值为 `governance_version: 2`。`doc/09_COLLABORATION.md` §4.3 明确 lifecycle v3 标记只对 `governance_version: 3` Task 生效，已释放的 v2 Task 不因该规则升级。故本裁定及拟议的 AC 拆分不要求补 `<<STATUS>>` 标记，也不得借拆分把已释放 Task 静默升级到 v3。

本文件只提供裁定，不改变 Task 状态。实施 7+1 的 AC 改写、建立 AC6 后续责任 Task、同步当前权威指针或对本 Task 作终态关闭，均须由 Codex 按协作协议 §4 的生命周期和授权完成。关闭候选为 **`closed_with_limitations`，不是 `done`**：前提是 AC6 的未承接项已被明确派给活动 Task，或由有权者逐项接受为限制，并完成消费处置登记；在该前提落实前维持现有 `ready`，不宣称本 Task 已完成 Gate 层全部责任闭环。

## 6. 事实来源

- `doc/tasks/ARCH-DOC-REBASELINE.md`：原 AC、v2 frontmatter、AC7 消费者裁决记录。
- `verification/ARCH-DOC-REBASELINE/ac1-ac3-gap-analysis-20261020.md`：AC1–AC3 的混层与责任现状。
- `verification/ARCH-DOC-REBASELINE/ac4-blocking-chain-20261020.md`：P18 旧阻塞解除但未重测。
- `verification/ARCH-DOC-REBASELINE/ac5-measured-baseline-20261020.md`：单机 NFR 实测及双环境缺口。
- `verification/ARCH-DOC-REBASELINE/ac6-measured-run-20261020.md`：格式往返、`SEC-FMT-001..005` 与外部阅读器缺项。
- `verification/ARCH-DOC-REBASELINE/ac7-per-consumer-gate-ruling.md`：固定 head、Review、集成和逐消费者 Gate 裁决。
- `doc/tasks/DETECT-TILING-1.md`、`verification/DETECT-TILING-1/ac2-sec-fmt-005-mapping.md`：SEC-FMT-005 映射与 limitation。
- `doc/tasks/DETECT-MEMORY-GUARD-1.md`：内存探测实现及 closeout 限制 L1–L7。
- `doc/tasks/P18.md`：`closed_with_limitations`、AC2/AC5 未完成、真实运行和阻塞项。
- `verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-archdoc-remaining-r33.md`、`codex-adjudicate-detect-tiling-r34.md`、`codex-adjudicate-tiling-stage2-r35.md`、`codex-adjudicate-tiling-closeout-r36.md`：既有裁定边界和 limitation 处理。
- `doc/09_COLLABORATION.md` §4、§4.3：终态关闭条件与 lifecycle v3 适用范围。
