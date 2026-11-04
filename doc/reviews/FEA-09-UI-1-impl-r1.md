<!-- FEA-09-UI-1 implementation review r1 (Codex independent) -->
# FEA-09-UI-1 实现 Review r1（Codex 独立）

- Reviewer：Codex 全新上下文（/root）；未参与实现/返修；只读，未改仓库/commit/push。
- reviewed_head：`e40c0f74bb13c75d724661420bd72f06e2d2518e`（parent `1a5894282`）。
- 结论：changes_requested，P0=0 / P1=5 / P2=2（R1–R7）。
- DSH 处置：`doc/reviews/FEA-09-UI-1-impl-r1-adjudication.md`。

---

verdict: **changes_requested**
reviewed_head: `e40c0f74bb13c75d724661420bd72f06e2d2518e`
parent: `1a5894282b8b6e459b6292f762816bcfad5ac720`
Reviewer：Codex，全新上下文 `/root`，未参与实现或返修；辅助只读审查来源：`/root/standards`、`/root/spec`。
分级汇总：**P0=0 / P1=5 / P2=2**。全程未修改文件、commit 或 push；结束时工作树干净。

以下源码路径均相对于 `apps/desktop-avalonia/`。

**Standards：范围、架构与恢复性**

- **R1 · P1：异常路径遗留密码 token / Secret-G。**
  `src/NewManga.App/Services/SourceImportModels.cs:615` 创建文件，`:667` 才登记 `_activeSecret`。
  Start 被拒绝或取消时，`:672` 的清理因上下文为空失效；`:633–635` 早退同样遗漏。违反 C-16 §3。
  最小修复：创建即登记清理上下文；所有未 accepted 出口统一删除文件并撤销 Secret-G，补失败负测。

- **R2 · P1：receipt 暂时失败导致运行中操作失去取消入口。**
  `ImportDockViewModel.cs:384–387` 遇到一次 null 即退出，`:335–337` 随即解除运行状态。
  Core 可能仍在提交，但取消按钮禁用，关闭可丢弃 operation，重新预览也被放行。
  最小修复：保留 operation 与“状态未知”的活动状态，允许恢复轮询/取消；确认终态后再释放。

- **R3 · P1：folder 接线超出最小 payload 适配，包含未经冻结的业务规则。**
  `SourceImportModels.cs:733–809,852–900,956–959` 自行递归枚举、排序、生成 source identity，并直接调用 Registry 授权。
  这超出 Appointment IN-6 的 pass-through；递归还未排除 reparse 目录，可能循环或遍历越界后才被 Host 拒绝。
  最小修复：交 DSH 裁决并冻结所需 Host 接缝；当前范围内限制该路径，避免自行补授权/枚举语义。
  Handoff 虽披露逐文件 grant，却声称“行为等价”；缺少证明，且当前选择入口仅产生 `IsFolder:false`。

- **R6 · P2：逐项提交边界未显示。**
  `Views/V2/Library/ImportDockView.axaml:143–158` 只绑定名称和 outcome，没有绑定 VM 已生成的 `CountsText`。
  最小修复：显示每项已提交/待处理页数，并验证真实控件文本。

- **R7 · P2：整源跳过显示为“跳过 0”。**
  `ImportDockViewModel.cs:435` 只显示 `SkippedPages`；C-16 整源跳过允许仅 `SkippedSources=1`。
  最小修复：分别显示跳过页数和源数，补整源已引用场景。

**Spec：C-16 与验收证据**

- **R4 · P1：AC-4 缺少真实 UI→production controller→IPC 闭环。**
  `Fea09UiImportIpcTests.cs:110–122` 直接构造 coordinator，并手写 HostLocal 路由；未经过 HostController、VM/View。
  IPC 是真实子进程，但只能证明编排层；13 个 VM/View 测试使用 fake，不能拼接为真实 UI 证据。
  源变化仅有 fake stale；取消测试 `:358` 允许 Completed，没有确定性部分提交后取消及真实重试去重。
  最小修复：补隔离 fixture 下真实控制器与 VM/View 观察，覆盖上述场景；第五例只是审计，不是第五个业务场景。

- **R5 · P1：多加密源共用一个一次性 token。**
  `SourceImportModels.cs:615–641` 为整个多选 plan 仅创建一个 token。
  Core `runtime.py:347–349,421–422,673` 每源读取密码，`secrets.py:153–154` 首次读取即删除；第二个加密源将失败。
  最小修复：在现有契约内拒绝或拆分多加密源，每次独立确认并创建 token；不得扩展 Core wire。

C-16 其余核验：密码分支重新 plan 后使用相同 grants 启动；`secret_ref` payload 仅含元数据；AES typed unsupported 有真实 IPC 证据；显示计数主要来自 receipt。
密码证据扫描：本次扫描本 Task 六个 evidence 文件，对正确/错误/UI 探针及编码形式 **0 命中**。
但原审计仅取 `RequestLine`，不能证明响应、全部日志、Registry 和异常分支均零泄漏；R1 仍阻断 AC-2。

| 核验项 | verdict |
|---|---|
| Scope | **PARTIAL**：源码/测试路径合规；PLAN/STATUS/LEDGER 三个例外已登记为 DSH 集成文件；R3 未满足语义边界 |
| 冻结面/旧路径 | **PASS（静态）**：C-05/C-15/C-16/C-07、FEA-08/09 closeout、组合根及其他页面未改；旧 ImportPages 主体保留 |
| App 接口 | **PASS（接口）/PARTIAL（编排）**：独立 `ISourceImportController` 与能力探测正确；R2/R3 阻断整体认可 |
| AC-1 | **PARTIAL**：普通 plan/confirm 有 IPC；源变化拒绝尚无真实 UI/IPC 证明 |
| AC-2 | **PARTIAL**：单加密源重试/AES 有证据；R1/R5 未满足 |
| AC-3 | **PARTIAL**：receipt 投影存在；R2、取消与重试证据缺口未满足 |
| AC-4 | **未满足**：见 R4 |
| AC-5 | **静态符合，运行验证 NOT_RUN**：FEA-06 evidence diff 为空；测试数量采用交付记录；未 push 为交付声明 |

门禁实际复跑：C-07 `--check` **PASS**（54/1/6）；governance **PASS，3 warnings**；冻结 pins **17/17 PASS**；Task EV 哈希 **7/7 一致**。
交付记录：build 0/0、全量 1313/0/63、IPC 5/5；Owner 的治理失败已由当前提交修正，本次复跑确认。
**NOT_RUN**：build、全量 .NET、13 个 UI 测试、真实 IPC 门禁；它们会写产物或覆盖 canonical evidence，不符合本次只读限制。
范围外高风险：既有测试复跑覆盖 FEA-09 canonical evidence 的问题已被 Handoff 披露，本次未触发；未新增其他已确认范围外回归。

推荐下一步：交 DSH 处置本报告并释放返修，保持当前 Task 未关闭。
可直接转发：**“ZCode：按本报告 R1–R7 返修 FEA-09-UI-1；R3 先由 DSH 冻结接缝范围。补真实 UI/IPC 判别证据，提交新 head 后交全新上下文 Codex 复审；不得改冻结契约或 push。”**