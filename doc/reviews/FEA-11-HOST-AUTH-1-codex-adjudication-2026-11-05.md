DECISION: A — 接受以 `closed_with_limitations` 终态收口；本裁决不代表技术完成，仓库状态须待 DSH 完成以下 closeout 条件后再更新。

## 依据

r8 的结论是 `approved`，P0/P1/P2 均为 0；AC3 为 `PARTIAL`，AC4 为 `MET（路径层）`。报告明确同意 `closed_with_limitations`、不同意 `done`，并要求保留 limitation，不得改写为 PASS 或进入 READY DAG。[r8 结论](<G:/CODEX/New Manga/doc/reviews/FEA-11-HOST-AUTH-1-r8.md:16>) [AC 判定](<G:/CODEX/New Manga/doc/reviews/FEA-11-HOST-AUTH-1-r8.md:21>) [终态意见](<G:/CODEX/New Manga/doc/reviews/FEA-11-HOST-AUTH-1-r8.md:36>)。这符合生命周期规则：`closed_with_limitations` 是终态但不等于技术完成，须记录替代依据、closure evidence、未完成 AC/Finding 原始状态及分类，且不得进入 READY DAG。[协作协议 §4](<G:/CODEX/New Manga/doc/09_COLLABORATION.md:79>)

有一项 AC3 限制需要在 closeout 明确补充映射：任务卡登记了 ACK 使用 journal 原授权、Host 未在 ACK/recovery 时取得并持久化 fresh authorization 的限制。[任务卡](<G:/CODEX/New Manga/doc/tasks/FEA-11-HOST-AUTH-1.md:79>)当前 `SourceOperationCoordinator` 的 ACK 与 recovery 路径仍从 journal 读取原授权；C-17 则要求 ACK/recovery 使用 fresh grant/authorization，并规定 generation 变化时 Host 取得当前明确授权。[ACK 实现](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs:172>) [recovery 实现](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs:269>) [C-17 冻结记录](<G:/CODEX/New Manga/doc/plan/FEA-CONTRACT-FROZEN-C17.md:3>) [C-17 授权规则](<G:/CODEX/New Manga/doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:169>)。Core 仍会校验授权摘要、提交基线、identity 与 live grants，现有证据未显示 P0/P1 级绕过；但这是 Host 履行冻结流程的 AC3 缺口，r8 十项清单没有明确写出这一行为限制。[Core 校验](<G:/CODEX/New Manga/src/application/sources/runtime.py:182>) [live grant 校验](<G:/CODEX/New Manga/src/application/sources/runtime.py:224>)

## Closeout 条件

1. **保留 r8 的十项 limitation 原文和顺序**：HostRuntime e2e、ACK/崩溃矩阵、dispatcher retry 命令面、Host plan 预检、receipt/CommitReceipt 核对、输入规则、Registry scope、分类精度、capability reason、R7-P2-01 测试判别力及文档/证据残留。[清单起始](<G:/CODEX/New Manga/doc/reviews/FEA-11-HOST-AUTH-1-r8.md:38>) [第十项](<G:/CODEX/New Manga/doc/reviews/FEA-11-HOST-AUTH-1-r8.md:48>) 保持 AC3 `PARTIAL`；AC4 记录为 **`MET（路径层）**，不得据此声称 P0-1 的全部技术工作已完成。

2. **在不改写 r8 历史报告的前提下记录发现处置**：`R8-P3-01/02/05` 已在后续文档提交 `81c28d3` 中修正；当前卡面历史状态、reviewer r1–r8、STATUS/PLAN 指针已有相应更新，`R7-P2-01` 已注明补测完成。[卡面历史说明](<G:/CODEX/New Manga/doc/tasks/FEA-11-HOST-AUTH-1.md:52>) [reviewer 指针](<G:/CODEX/New Manga/doc/tasks/FEA-11-HOST-AUTH-1.md:10>) [补测说明](<G:/CODEX/New Manga/doc/tasks/FEA-11-HOST-AUTH-1.md:61>) 逐项复核这些修正，并保留 R8-P3-04 的测试判别力残留及 R8-P3-03 的证据残留分类。另在清单附注中明确上述 ACK/recovery fresh authorization 限制如何映射到现有项；**原十项文本保持不变**。

3. **写入正式 closure 记录**，包含裁决人和日期、`closed_with_limitations`、替代依据、closure evidence 的路径与 commit、AC1–AC4 的原始状态、所有未完成 Finding/limitation 的原始分类与当前处置，以及“不同意 done、不得进入 READY DAG”的明确声明。对任务卡现有 P2-7 类限制与 r8 的 `P2=0` 分开记录，不能删除或互相改写。

4. **定稿证据和资源清单**：当前 `verification/FEA-11-HOST-AUTH-1/` 实际只含 `logs/gates.log`，未发现 EV、RESOURCE、DELIVERY 文件；任务卡的两个 closeout 状态仍为 pending。[任务卡状态](<G:/CODEX/New Manga/doc/tasks/FEA-11-HOST-AUTH-1.md:18>) 新增并定稿 `EV.md`、`RESOURCE-MANIFEST.md`、`DELIVERY-MANIFEST.md`，逐项记录路径、commit/head、命令、退出码和资源处置。门禁记录需区分旧 Host.Tests `105` 与 r8 的 `107`，记录全量 .NET `1395/0/78` 的来源，并保留 IPC 首次 `2/3` flake 及后续复跑结果，不能合并成无波动的 PASS。[现有门禁旧计数](<G:/CODEX/New Manga/verification/FEA-11-HOST-AUTH-1/logs/gates.log:13>) [r8 门禁摘要](<G:/CODEX/New Manga/doc/reviews/FEA-11-HOST-AUTH-1-r8.md:25>) [现有 r8 门禁补记](<G:/CODEX/New Manga/verification/FEA-11-HOST-AUTH-1/logs/gates.log:30>) [IPC flake 说明](<G:/CODEX/New Manga/verification/FEA-11-HOST-AUTH-1/logs/gates.log:32>)

5. **收口权威指针并通过治理检查**：更新 Task 状态、STATUS 当前 Task/下一步、PLAN 节点及摘要、TASK_LEDGER 对应行；保持该 Task 为终态且不列入 READY。当前 STATUS 仍写实现→Review→集成，[STATUS](<G:/CODEX/New Manga/doc/STATUS.md:10>) PLAN 摘要仍把 HOST-AUTH-1 列为 ready，[PLAN](<G:/CODEX/New Manga/doc/REBASELINE_PLAN.md:48>) TASK_LEDGER 仍是 `in_progress`。[Ledger](<G:/CODEX/New Manga/doc/TASK_LEDGER.md:41>) 另外，当前只读治理检查因台账计数差异失败：记录数 `512` 对 `515`、非终态数 `13` 对 `16`；修复前不能把检查结果写成 PASS。`verify_pins.ps1` 当前为 18/18 PASS，closeout 后应保持通过。

## 残余风险

AC3 未达到完整 HostRuntime→Core 真实 sidecar e2e、ACK/崩溃矩阵自动化和 dispatcher retry 命令面；receipt 核对、Host plan 预检等也仍在 r8 limitation 范围内。ACK/recovery 使用旧 journal authorization 的流程缺口应作为已接受的 limitation 明确留下，不能被“Core 有校验”或测试矩阵缺失的表述掩盖。FEA-11 上游的 LINEAGE-1 使用约束继续有效；FEA-12 仍只是未冻结的 scope review。

## 独立核查发现

- 当前实际 HEAD 是 `7cc963065fe260fe6fa3314e5717f28c65bcbe4c`，不是请求背景中的 `035468a81`；r8 的 reviewed head 是 `cbd561b4…`。我检查的 HOST-AUTH 实现文件在 r8 reviewed head 之后无代码差异。
- 当前工作区观察到 `doc/tasks/FEA-11-LINEAGE-1.md` 有未提交修改，以及 `verification/FEA-11-LINEAGE-1/logs/gates-r2.log` 未跟踪；均未触碰。LINEAGE-1 卡面为 `in_review`，PLAN 却仍列 `ready`，closeout 更新后续指针时应一并按权威状态核对。[LINEAGE-1 卡面](<G:/CODEX/New Manga/doc/tasks/FEA-11-LINEAGE-1.md:6>) [PLAN 状态](<G:/CODEX/New Manga/doc/REBASELINE_PLAN.md:15>) [Ledger 状态](<G:/CODEX/New Manga/doc/TASK_LEDGER.md:44>)
- 当前任务卡 AC4 仍标 `PARTIAL`，与 r8 的 `MET（路径层）` 不一致；closeout 应按 r8 的窄口径对齐，同时保留 AC3 `PARTIAL`。[任务卡 AC4](<G:/CODEX/New Manga/doc/tasks/FEA-11-HOST-AUTH-1.md:88>) [r8 AC4](<G:/CODEX/New Manga/doc/reviews/FEA-11-HOST-AUTH-1-r8.md:22>)
- 我运行了只读治理检查：TASK_LEDGER 两项计数错误；pin 核验通过 18/18。未运行产品测试，未修改仓库文件。

**推荐下一步：**由 DSH 完成上述 closeout 证据、指针和台账修正后重跑治理检查；LINEAGE-1 继续其 r2 返修，不自动将 FEA-12 提升为 READY。本轮未提供 `-o` 路径，裁决文本在此返回。