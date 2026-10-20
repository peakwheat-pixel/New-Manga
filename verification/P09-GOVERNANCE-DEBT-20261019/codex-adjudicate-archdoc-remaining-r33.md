# ARCH-DOC-REBASELINE 剩余 AC 裁定（r33）

日期：2026-10-20  
裁定者：Codex（Lead / Architect / Integrator）  
对象：`ARCH-DOC-REBASELINE` AC4–AC6、P18 消费状态、P16/P17 格式 Gate 与跨 Task 等待登记  
范围：只新增本文件。未修改 Task、STATUS、Plan、协作规则、代码、测试或既有证据；未调用 `coordinator-lease.py`，未执行 Git 写命令。

## 裁定摘要

1. **AC5：判 `PARTIAL`，不判 `MET`。** 实测覆盖了绝大多数 NFR 项并保留原阈值；但 AC5 原 Gate 要求 Win11、Win10 22H2 与 Intel i5/8GB 无独显档。当前只有一台 Win11、RTX 5070 Ti 机器，`CUDA_VISIBLE_DEVICES` 屏蔽验证不等同于实际无独显硬件档，也没有 Win10 实测。该硬条件缺失使 AC5 不能整体 `MET`。WPR/GPUView 在原报告 §3.2 是“提议使用”，AC5 的冻结 AC 与已列验收阈值未将其定为强制工具；改用脚本级测量本身不构成失败，但须保留方法差异。撕裂项仍是 `LIMITATION/UNOBSERVED`，不能算通过。
2. **AC6：判 `PARTIAL`。** 五格式往返证据通过；`SEC-FMT-001..005` 与 CBZ/PDF 外部阅读器验证缺失。结构合法性校验可补充格式内部一致性证据，不能代替独立阅读器互操作验证，也不能替代恶意输入安全测试。
3. **P16/P17 前置 Gate 曾被违反，但不因此自动撤销其各自 Task 的 `done`。** AC6 报告 §4 明确要求安全测试及外部阅读器验证在消费前完成，而 P16 的 `P16-FMT-PIN` 引用了该报告、P16/P17 随后完成。应把这是次序/前置 Gate 偏差登记为遗留，并由新 Task 完成尚缺的验收；除非发现 P16/P17 自身冻结 AC 或交付存在具体失败，不追溯重开其状态。它们的 `done` 只证明自身 Task AC 达成，不证明未运行的 AC6 前置测试已通过。
4. **P18 不自动重开。** `ImportPages` 实现及其测试只解除一个技术前置，不代表 P18 的端到端实验已重跑。原 AC 明确不重新获取 Manga109；真实素材、真值与模型端点及另外两项运行缺口仍需确认。P18 AC2 的产品发布门槛须用户决定。若继续，应先取得门槛裁决、素材/模型/端点可用性与安全授权，再冻结一项窄范围的 P18 补测 Task；否则维持 `closed_with_limitations`。
5. **AC4：消费者实测为 `PARTIAL`，不是 `MET`。** 已确认旧阻塞后来解除，但没有修复后重跑的证据。原 P18 运行确实执行过但失败在导入/检测前置，故“完全没有任何运行”不准确；“修复后新链路未验证”是未运行部分。若要按限制终止，必须保留未完成状态并由有权者明确接受限制，不能把 limitation 改写成 PASS 或补勾。
6. **需要跨 Task 等待登记，但不直接修改协作协议。** Plan 已有 `depends_on` DAG，可表达已知前置；Task 的 `depends_on`/阻塞段可表达等待原因。当前没有强制的反向消费者检查或“被依赖 Task 完成后唤醒所有等待方”闭环。建议未来治理 Task 以 Plan 的 DAG 为索引、Task 的依赖/阻塞与证据为详情，增加关闭时登记未决等待、完成时反查等待消费者的检查项；`STATUS` 继续只指向当前运行状态，不充当全量登记表。

## 1. AC5：NFR 实测是否足以判 MET

### 判定：`PARTIAL`

`verification/ARCH-DOC-REBASELINE/ac5-measured-baseline-20261020.md` 将 P20 实测按 AC5 映射逐项对齐，结果包括冷启动、内存、交互延迟、帧率、打包分发、GPU 屏蔽降级与故障隔离；原阈值未降低。撕裂未观察并已明示 `LIMITATION`。因此该文件把 AC5 从“没有消费方实测证据”推进到“多数子项有证据、少数环境/观察条件未满足”，但不足以支持整项 `MET`。

本裁定将偏差分开处理：

| 偏差 | 是否阻止 AC5 整体 MET | 理由 |
|---|---|---|
| 缺 Win10 22H2 环境 | 是 | 原 Gate §3.1 明确要求 Win11 与 Win10 22H2 两套环境。只有 Win11 不能证明跨系统要求。 |
| 缺 Intel i5/8GB 无独显硬件档 | 是 | 原 Gate 要求该档位。RTX 5070 Ti 上通过 `CUDA_VISIBLE_DEVICES` 屏蔽 CUDA 验证的是软件降级路径，不等价于低配/无独显整机上的性能、可用性与兼容性。 |
| 未用 WPR/GPUView | 否，依当前证据 | 原 Gate §3.2 将其表述为提议工具；冻结 AC5 关注测量结果与阈值。脚本计时方法差异应保留在证据中，除非上游规范证明 WPR 是强制项，否则不把工具替换单独判 FAIL。 |
| 撕裂未观察 | 是，作为未完成子项 | “无可见撕裂”仍未知。沿用 r32 的原则：`UNOBSERVED` 是限制，不是 PASS。 |

“6/7 NFR PASS”可以作为领域计数摘要，但不能覆盖明确要求的环境矩阵和撕裂观察。建议给 AC5 标 `PARTIAL`，并在 Task 的 AC 证据状态中分别列出各子项；本文件本身不修改 AC 勾选或 Task 状态。若用户明确选择接受这些缺项并停止验证，可将 Task 按协作协议走 `closed_with_limitations`；在用户选择前不能据此关闭。

## 2. AC6：状态、SEC-FMT 测试责任与外部验证

### 2.1 状态：`PARTIAL`

`verification/ARCH-DOC-REBASELINE/ac6-measured-run-20261020.md` 证明 PNG、ZIP（多压缩方式）、CBZ、PDF（image-only/searchable dual-layer）及文本导出往返测试通过；文件列出的测试覆盖页序、哈希、血统与 PDF 文本。该证据满足导出往返这一部分。

同一报告也核实：`tests/**` 中没有 `SEC-FMT-001..005` 对应测试，且没有外部标准阅读器验证记录。AC6 的长期格式追踪表和契约已建立，不等于安全和互操作验收已经执行。因此 AC6 整体只能判 `PARTIAL`，不能 `MET`。

### 2.2 `SEC-FMT-001..005` 的责任与立项

五项是实现/验证要求，不应再只留在 AC6 报告的规范表里。当前没有 Task 的 AC 明确承接，亦没有执行者。**应立即登记一个新的格式安全验收 Task（建议 ID：`P16-FMT-SEC-1`，具体 ID 由 Codex 检查 Plan 冲突后冻结）**，依赖 P16/P17 现有交付和本裁定；该 Task 先做只读威胁/实现可测性盘点，再在明确授权范围内为五项安全要求补实现与负向测试，覆盖 ZIP/CBZ 路径穿越、CBZ XML 实体、伪装图片、Windows 长路径/Unicode、超大图片资源保护。不要把这项实施悄悄追加进 ARCH-DOC-REBASELINE 的原范围：该 Task 原 allowlist 不含产品实现，且已关闭的消费者不能凭裁定自动获得新实现授权。

安全 Task 应由 **Antigravity** 负责通用编程实现；由 **Codex 或 DeepSeek Harness** 中非作者担任独立 Reviewer，最终由 Codex 集成。释放前要核实每条 SEC 要求与目标架构/现有实现的适用边界，冻结 `allowed_paths`、基线、测试夹具和安全负向验收标准。若盘点发现某项原报告要求与冻结架构冲突，先作为产品/架构裁决提出，不自行降级或删除要求。

### 2.3 外部阅读器检查与结构校验的关系

文件内部校验（例如 ZIP central directory/CRC、CBZ 条目路径和图片可解码性、PDF parser 对 xref/page tree 的解析）是有价值的**自动结构校验**，也可先作为无需 GUI 的补充证据。但它不能证明 Adobe Acrobat、CDisplayEx 或其他标准阅读器实际接受导出的文件、正确解释 ComicInfo/页面顺序/字体或显示 searchable text。因此它不能替代 AC6 报告 §4.2 明文要求的“至少一种外部标准阅读器兼容性验证”。

外部验证应由新的格式验收 Task 承接，优先使用一台现成且许可允许的标准阅读器；Task 记录版本、平台、文件 hash、打开/导航/文本查询结果与原始证据。当前记录称本机未装阅读器，故不在本裁定中擅自安装。若后续客观上无法取得阅读器，必须由有权者裁决将该要求改为限制项；结构检查只能作为部分证据，不能作为等价替代。

## 3. AC6 与 P16/P17 前置 Gate 的关系

### 判定：原 Gate 有明确前置语义，且发生了次序偏差；不自动撤销 P16/P17 `done`

`verification/ARCH-DOC-REBASELINE/ac6-p08-fmt-traceability.md` §4.1 明确规定：P16 在实现导入/解析前须依该规范实现五种格式解码器并通过 `SEC-FMT-001..005`；§4.2 规定 P17 在实现导出前须按规范序列化，CBZ/PDF 须经至少一种外部标准阅读器验证。这不是仅靠“完成”一词推测，而是消费者前置 Gate 的明文。

P16 的 Canonical Evidence 行 `P16-FMT-PIN` 将该 AC6 报告固定为消费来源，P16/P17 又已 `done`；现有本轮证据显示安全测试及外部阅读器验证没有完成。故三种解释中，本裁定选择 **(1)：前置 Gate 没有证据证明满足，消费者先行实现/完成，构成 Gate 顺序偏差。** P16 以 `P16-FMT-PIN` pin 了来源，不能据此推导该来源 Gate 已全部通过；它反而证明消费者可追溯到该规范。

不过，`P16` 与 `P17` 的 `done` 是各自独立冻结 Task 的生命周期状态。AC6 的 Gate 偏差不单独证明 P16/P17 自身 AC 失败，也不授权改写 Task 历史或重开终态。处置如下：

- 保持 P16/P17 当前 `done`，将“消费前置 Gate 未满足/未留证”作为可追溯的治理偏差。
- 新格式安全/兼容 Task 验收这些具体缺项，并明确哪些是当前实现的安全缺陷、哪些是缺少验证。
- 若该 Task 发现真实产品行为违反 P16/P17 自身 AC，或需要改动其交付，则另按新缺陷/修复 Task 处理；仅因缺少 AC6 前置证据，不批量撤销两个 done 状态。
- 本裁定不宣称历史次序符合规则，也不将后补测试伪装成实现前已通过。

## 4. P18 是否重开；AC4 的判定

### 4.1 不自动重开 P18

`verification/ARCH-DOC-REBASELINE/ac4-blocking-chain-20261020.md` 证明 `ImportPages` 的实现提交晚于或同日于 P18 关闭，并且当前源码与 packaged-sidecar 测试已有相应分支/调用。这个事实解除 P18 Review 中第一项技术阻塞的现状判断；它不能替代一次新的 P18 真实切片。`verification/P18/run-record.md` 仍是修复前记录，其中 JA/KO 都在导入或检测阶段被挡，OCR、翻译、修复、渲染及 pipeline terminal 未运行。

**本裁定不重开 P18。** 该 Task 已为 `closed_with_limitations`，协作协议 §4 规定终态除新授权外不恢复实施。当前也没有证据确认运行所需真实素材、人工真值、模型权重/服务端点和 JA/KO 端到端依赖全部可用。P18 的 AC2 发布门槛是用户产品取舍；Coordinator/Owner 不能用技术补测替用户决定门槛。重开一个旧 Task 而不先解决这项外部决定会重现阻塞。

若用户希望获得新链质量资格结论，推荐的可执行路径是：

1. 先由用户裁决 P18 AC2 的 JA/KO 发布门槛；不要求用户重复提供已存在的技术事实。
2. 只读核实许可素材仍可访问且不重新获取 Manga109、真值来源可用、检测/OCR/翻译/修复 provider 与 endpoint 可用，并确认 `ImportPages` 在目标构建中的运行条件。
3. 满足前置后另立窄范围补测 Task，继承 P18 的不改产品代码边界；若发现生产修复需要，另立实现 Task。Owner 可由 DeepSeek Harness 承担研究/实验，非作者 Reviewer 独立复核，Codex 集成。
4. 若前置仍不可得，保留 P18 的 `closed_with_limitations` 和原始 AC 状态，不重复跑静态检查伪装成真实实验。

### 4.2 AC4 为何是 PARTIAL

ARCH-DOC-REBASELINE AC4 的核心交付是将 P18 的 JA/KO、无字页和质量要求映射到新链，并明确样本、真值、阈值及 `version/device/model/endpoint` 证据责任；原 AC4 报告完成了这项映射。AC4 的消费者实测仍由 P18 提供，AC7 也把 P18 列为 Gate 消费者。P18 有真实运行记录，但未完成新链端到端实验；后续唯一已知的 `ImportPages` 阻塞虽解除，却没有重测。

故状态应拆开表达：

| 层面 | 裁定 |
|---|---|
| AC4 映射与证据责任定义 | 已有证据支持完成 |
| P18 消费实测 | **PARTIAL**：曾运行，链路未到质量 pipeline；解除 `ImportPages` 后未重测 |
| ARCH-DOC-REBASELINE AC4 总判定 | **PARTIAL**，不 `MET` |

`NOT_RUN` 若表示整个 AC 从未执行，会抹掉 P18 已保存的真实失败运行；`PARTIAL` 能准确反映“有一次实测尝试，但关键新链阶段没有执行”。新增 limitation 可写为：“`ImportPages` 已有实现与测试，但 P18 没有在该实现之后重跑；JA/KO 质量链的终态仍未知。”

该 limitation 可作为当前事实与关闭选项记录，但**不能由 Codex 单方将 AC4 勾为完成**。在 P18 补测或用户明确接受该限制并按生命周期作出关闭裁决之前，AC4 仍为未完成 `PARTIAL`；ARCH-DOC-REBASELINE 整体继续 `ready`。这与 r30/r32 对“未观察不得判 PASS、限制关闭不等于技术完成”的处理一致。

## 5. 跨 Task 等待登记机制

### 裁定：增加流程检查有价值；以 Plan DAG 为索引、Task 为事实详情

本次两条链分别是 ARCH-DOC-REBASELINE AC5 等 P20 实测，以及 AC4 等 P18 消费实测。P20 完成后未触发 AC5 回看；P18 关键阻塞解除后未触发 AC4 重测。它们说明目前有 Task 依赖和 Closeout Record，但没有强制的“提供方改变状态后反查消费者”动作。

现有位置的职责：

- **`doc/REBASELINE_PLAN.md`** 是唯一依赖 DAG，可用 `depends_on` 表达 Task 对 Task 的正式前置，亦可反查某节点的下游消费者；它适合作为等待关系的索引，不适合放详细等待原因、触发条件和证据。
- **Task 文件**已有 `depends_on`、阻塞/风险与 Closeout Record，适合记录“我在等哪个 Task/决定/外部资源、解除条件、通知/复核条件”，以及完成时核销哪些消费者。
- **`doc/STATUS.md`** 是当前 Active Task 和运行状态指针，不应变成所有等待边和历史消费者的重复清单。
- 现有协作协议 §5.1 的下一任务建议不是反向等待登记，也不要求 Task 关闭时核验等待它的消费者。

推荐未来治理变更增加两条窄规则：

1. Task 以 `blocked` 或 `closed_with_limitations` 结束、但仍有未满足的下游消费/等待时，在 Task Closeout Record 登记 `waits_for`（Task/外部决定/资源、所等事实、解除条件、触发后的复查责任），并在 Plan 中保留正式依赖边；纯信息性等待不伪装为硬依赖。
2. Task 进入完成/关闭流程时，Codex 依据 Plan DAG 反查其下游 Task 和显式等待登记，逐项记录“已通知/已复查/仍无授权或保持未决”。当被等条件变化时，责任方按登记触发重新评估消费者；不自动重开终态 Task。

规则可以执行，因为 Task ID 和 Plan DAG 已提供机器/人工可查询的关系；但它不是当前已强制机制，且依赖关系反查、关闭触发和状态变化触发的定义需通过单独治理 Task 修改协议/模板或检查器。当前只裁定其必要性与拟放位置，不直接改 `doc/09_COLLABORATION.md`、Task 模板或 Plan。

## 6. 生命周期与范围边界

本裁定不更改 `ARCH-DOC-REBASELINE` 的 7 个 AC 勾选、P18/P16/P17 状态、Plan DAG、STATUS、`done` 计数或任何 Canonical Evidence pin。ARCH-DOC-REBASELINE 当前应继续作为 READY 节点；要正式登记 AC4–AC6 的新状态，须由后续获准的 Codex 集成/closeout 操作按协作协议 §4 更新权威文件、证据 pin 与状态指针，并运行治理检查器。这里的“建议新增 Task”不是已释放 Task，也不授予实现范围。

本轮只新增本文件；保留当前 checkout 中已有的 dirty/untracked 内容，不触碰它们。没有执行测试、治理检查器、协调器或任何 Git 写命令。

## 7. 推荐下一步

**先准备两个独立的后续入口，不自动释放：**

1. **P16-FMT-SEC-1（建议 ID）**：由 Codex 核查名称/冲突并冻结窄范围；Antigravity Owner 实现与验证 `SEC-FMT-001..005`，Codex 或 DeepSeek Harness 非作者 Review。Task 同时记录 P16/P17 前置 Gate 次序偏差和外部阅读器互操作检查；不擅自把结构校验称作互操作通过。
2. **P18 补测决策/Task**：只有在用户决定 AC2 发布门槛，且真实素材、真值、模型/endpoint 和运行依赖确认可用后才释放。由 DeepSeek Harness Owner 执行真实 JA/KO 切片，Codex 或 ZCode 非作者 Review；不重新获取 Manga109，不改产品代码。

在用户裁决 AC2 门槛、并确认是否愿意接受 AC5 环境矩阵与撕裂 limitation 前，不建议将 ARCH-DOC-REBASELINE 改为终态。若用户选择继续而非限项关闭，下一步由 Codex 先做上述只读前置盘点并建立范围冻结的 Task；这是推荐路径，不代表本文件已启动任何 Task。
