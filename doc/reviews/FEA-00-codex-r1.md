---
document_id: FEA-00-codex-r1
kind: independent_review
reviewer: Codex
author: DSH
base_commit: 1180cdba79e4d610521dde13f0c8a458220f9d90
reviewed_head: 1180cdba79e4d610521dde13f0c8a458220f9d90
reviewed_state: uncommitted_worktree_bytes_pinned_below
decision: changes_requested
---

# FEA-00 DSH 权威文档独立 Review r1

## 结论与边界

**CHANGES_REQUESTED：1 项 P0、3 项 P1、3 项 P2；不得据本次 Review 批准或释放实现。** P0 是 ADJ-001 把任何共享源及目标外引用一律定义为永久删除冲突，同时声称保持 M2-C1 现行语义；这会改变既有契约的冲突判定并阻断已确认的共享源场景。按本次用户明确的审查等级要求，将此类未说明的语义改写记为 P0；这里不判断作者意图。

本 Review 仅审 DSH 的下列新增文档、检查器及指针变更，适用对象为**下表固定工作区字节**，不是仅凭 `main` commit 可重建的干净快照。Codex 编写过被 DSH 引用的 Fluent 方案，未编写本次 AD-003、ADJ-001 或 DSH r2；因此本报告对 DSH 交付物独立审查，但**不对 Codex 自己的方案出独立批准**。用户本轮直接要求 Codex Review；项目文档中 DSH 的正式 Appointment 仍记为 `PENDING_APPOINTMENT`，由 DSH 协调程序状态。DSH 是交付物作者，不把其技术复核当作独审。报告不改变任何 Task、Gate 或契约状态。

## 固定范围与证据

| 对象 | SHA-256 |
|---|---|
| `doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md` | `57238c5996c5af309d9b17477b94480389595e6560e11cb02db08d3acc789acc` |
| `doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md` | `6f0c6ba5185765b10792edbd9cb312f81e883877c0b8d4d90b615af5dc3feeaa` |
| `doc/reviews/FEA-00-dsh-r2-technical-recheck.md` | `8974c94ddb7490554919632aaa27f85913f568f95d4b4fd30f2ef09556181e93` |
| `tools/governance/check.ps1` | `083f6618d946bbe15d98d78771864bd0a84da9baa7c80621acf92e56806be76e` |
| `doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md` | `0bd11c76c6a4447ba5f5084d1b427970fc3db7f5eb7d934f5a3e10e0a07d3157` |
| `doc/00_INDEX.md` | `4816d59b23def9d8afb50d79a0cb1ac598674a8819ce91469cd5b0139b9f70bc` |
| `AGENTS.md` | `678bda95e6edace4cb9311ee1eeb825fd66974d372da0e50b866530e125acea0` |
| `doc/STATUS.md` | `e8fe3affdabe315394a53f0d710e5ba16d480650716ea97f541977ade3de4a64` |

源码 `main@1180cdba79e4d610521dde13f0c8a458220f9d90`，Git common dir `.git`。对照的方案 hash 为 `2f925cca7229d17a13943bfd4c297386ae21010f7bf8b61c3ae5169795afa120`，需求 hash 为 `508273c4599f9a0e1e33250f9b4d75660ee72fbd7d0c76f678b7aa7751979808`，M2-C1 hash 为 `dfcd47cabe9831b270fb0a6f985e50ea9e5a34b165f2c776a8f1e34c777bae72`。开始时工作区已有多项 dirty/untracked 内容，均保留；被审对象有未提交内容。没有以 HEAD 代替这些文件的 hash。

## Findings

### R-01 — P0：共享引用被无条件改成全批删除阻断，却称现行契约保持不变

- **事实**：`doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md:16-17,28,65` 声称保持现行语义，PD-08 却规定“目标外引用、关系图、共享源在预检阶段即冲突”并使整批失败。`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:734,752,764` 要求检查目标外引用及关系图，针对**不一致、无法安全拆分或未列明**的目标外引用拒绝；并未规定凡存在可安全保留的目标外引用即冲突。`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md:60,97-99` 和 `doc/design/FLUENT_MANGA_USER_CONCEPT_2026-10-30.md:71,82-83` 支持多项目引用同一源，且其他项目引用的原文件默认保留。
- **反例与影响**：书 A 与 B 合法引用同一外部图片，用户只彻底删除应用中的 A；可安全删除 A 的绑定和自有数据、保留原文件与 B 的绑定。按 PD-08 字面，仅因存在共享源就整批失败；含 A 的其他目标也被阻断。该裁定把“外部原件保留”升级为“应用项目不能删除”，也把冻结契约中有条件的冲突扩大为无条件冲突。
- **建议**：DSH 明确区分可安全拆分的外部共享源、必须保留的共享物理文件与无法安全拆分/未知的关系；维持不一致时 fail-closed。对单条、批量、软删项目仍引用及并发变化分别制定反例与验收，核对是否需要正式修改 M2-C1；不得继续称现文无条件判定只是原语义。
- **状态**：open，交 DSH 裁定。此为文档已写出的语义冲突，不代表生产代码已经按 PD-08 实施。

### R-02 — P1：单条永久删除的专门确认被定义为批量请求形状

- **事实**：`doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md:58-59,75-79` 令确认绑定 `book_ids + confirmed_book_ids + confirm_count`，且将能力描述为给现有删除命令追加 digest。`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:684-695,723-725` 中单条只接受 `book_id` 与 `confirm_permanent_delete`，是 closed shape，明确不接受数组；三字段属于批量命令。
- **反例与影响**：删除单本书时，按 PD-02 照填三字段会被单条 closed-shape 拒绝；如果只添加 `inventory_digest` 又无法满足文字规定的三字段绑定。`doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md:26` 对“全部 Book 行”也未明确只有批量命令受该限制，容易错误限制单条删除。虽然字段及协议标为提案，当前冻结语义仍缺可执行的单条映射。
- **建议**：分别给出单条 `book_id` 与批量有序 ID/数量的确认绑定、命令版本与旧端 fail-closed 行为；单条不接受批量字段，保留批量全库保护的适用范围。要求分别验证单条最后一本、批量全库和 stale digest。
- **状态**：open。

### R-03 — P1：ADJ-001 的权威依据链接全部落到不存在的位置，检查器仍 PASS

- **事实**：`doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md:5-6,8` 的 5 个 Markdown 目标均相对于 `doc/contracts/` 解析：AD-002、AD-003、`contracts/M2-C1...`、两个 `reviews/...` 目标均不存在。正确相对方向分别应回到 `doc/`、本目录 M2-C1 和 `../reviews/`。`tools/governance/check.ps1:169-183,240-256` 的 `$staticFiles` 不含 ADJ-001；它只检查 AD-003 等选中文件的链接目标存在，不递归打开该目标，因此没检查 ADJ 内链。
- **反例与影响**：本次逐条解析得到 5/5 不存在，而实际运行检查器返回 `PASS (2 warnings)`。从 ADJ 无法跳转到被裁定的冻结契约或上游 ADR，后续 Agent 容易依据错误位置或遗漏约束。
- **建议**：修正相对路径；按项目允许的当前权威范围将 ADJ 本身纳入链接验证，并以断链负例和恢复正例验证，避免递归扫描历史目录。
- **状态**：open。

### R-04 — P1：新增架构/指针检查可被普通文本绕过，也会误报历史说明

- **事实**：`tools/governance/check.ps1:264-274` 使用全文子串判断哨兵和 `00_INDEX` 文件名；`:275-290` 对整行直接套正则，没有区分历史、否定或当前断言。`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md:45` 将检查器描述为会把“任何把 React/Tauri 或 PySide6/QML 当作当前架构”的陈旧断言判错；`doc/reviews/FEA-00-dsh-r2-technical-recheck.md:99-100` 只举一对措辞样本和哨兵存在性，不能推出一般的无误报/充分覆盖。
- **只读内存反例**：将索引中的所有 AD-003 目标替换为 `gone.md`，再仅在历史说明中添加字面文件名，现行 `-like` 仍为 `True`；把 AD-003 当前哨兵替换为其他架构并仅在历史说明中添加旧哨兵字符串，检查也仍为 `True`。基于脚本原正则的 Python 内存匹配：`历史记录：当前目标架构为 React + TypeScript；该表述已被取代。` 匹配为冲突；`当前目标架构为 Windows + C#/.NET + Avalonia + Python Core + SQLite + Managed Copy`、`current architecture is Python + PySide6 + QML` 和 `目标架构为 React + Tauri` 均未匹配。正例 `当前目标架构固定为 React + TypeScript` 能匹配。后四项为规则级模拟，并非改写仓库后运行完整检查器。
- **影响**：错误的当前架构或只有无效正文提及的指针可能通过；合法的历史说明可能误报。现有 `PASS` 只能说明本次机械检查通过，不能支持 r2 的一般性“无误报”结论。
- **建议**：明确检查目标为带状态的当前哨兵字段与有效 Markdown 权威链接；定义有限、可执行的陈旧断言语法及历史/否定例外，记录其覆盖边界；以真实 checker 的隔离正负例覆盖现行入口、旧 Managed Copy、英文/中文、历史和缺失指针。先按 `doc/09_COLLABORATION.md:163-177` 核验受影响全集与原基线，再改变既有判定；本轮未做该全集验证。
- **状态**：open。

### R-05 — P2：V2 删除能力与现有页级服务的事实口径混淆

- **事实**：`doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md:95` 称 V2 产品面“只有不可逆硬删与回收站列表”、用户可触达硬删；`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md:118` 又称书籍/页级软删与恢复命令不存在。实际 `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs:792-796,1214-1224` 对回收站读取、恢复和永久删除明确返回能力待接入、确认不可执行；而 `src/application/maintenance/trash.py:103-104,119-123,188-193` 已有页级服务层软删与恢复方法，`src/application/library/service.py:97-100` 有书籍服务层软删。`src/bootstrap/core_service.py:4387-4406` 有 Core 命令分发，不能据此推断 V2 可触达。
- **反例与影响**：把 Core/服务层存在误报为 V2 已可调用，会使安全风险、接线任务和验收基线失真；反过来也不能把服务层能力说成完全不存在。
- **建议**：按 Core 命令、应用服务、Host 接口、V2 UI 四层分别列出已存在/未接线/未实现，不宣称产品面硬删或列表已可达；服务行为和真实运行结果另行验证。
- **状态**：open。

### R-06 — P2：DSH r2 将已有设计依赖误记为缺失

- **事实**：`doc/reviews/FEA-00-dsh-r2-technical-recheck.md:87` 说“FEA-06 仍无设计依赖”；其固定被审方案 `doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md:631-633,649-662,908-910,922` 已把四页设计 FEA-04b 列为 FEA-06 的依赖，图中亦有 `P04b --> P6`。四页设计本身未冻结这一事实不变。
- **反例与影响**：依赖未满足与依赖未声明不同；把已有依赖当成缺失会误导 DSH 对 r1 F-04 的处置和后续审查。
- **建议**：保留原技术复核记录，按证据追加或另行记录更正：依赖已声明，设计和 Gate 尚未完成；不要据此批准方案。
- **状态**：open。

### R-07 — P2：AD-003 的 AD-002 字节保留声明自相矛盾

- **事实**：`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md:28,140-143` 一处说 AD-002 未修改，紧接着又说其顶部追加横幅；`doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md:8-11` 确有新增横幅。以 `git show HEAD:doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md` 为基线，移除当前工作树的横幅并将 CRLF 归一成 LF 后，剩余内容与 HEAD blob 一致；实际工作树为 CRLF、Git blob 为 LF，`core.autocrlf=true`。因此能证明正文经行尾归一后一致，**不能仅凭本次证据证明变更前工作树每个原始字节未变**。
- **反例与影响**：把追加过横幅的文件说成“未修改”，或把归一化后的对比说成工作树原字节证明，会误导历史保全审计。
- **建议**：区分“文件已增加状态横幅”“原正文逻辑内容与 HEAD 对照一致”和“原工作树字节是否有可复现基线”；如有变更前 hash，再按同一字节口径验证。不要改写已有冻结历史证据。
- **状态**：open。

## 逐项核验与未决事项

| 用户要求 | 事实 / 结论 |
|---|---|
| AD-003 取代范围 | `§2:28-38` 明示仅替换新导入默认和当前哨兵，旧 managed 继续读取，AD-002 的技术栈、Host/IPC、grant、安全和许可继续有效；未发现其直接把技术栈或旧数据全部替换的条文。AD-002 历史正文的 `§1:19,28` 必须与新增横幅及 AD-003 一起解释。对原正文的字节证据限制见 R-07。 |
| AD-003 §3 八类边界 | 逐项检查 §3.1–3.8：旧 Managed、新引用、备份、迁移、资源信任根、外部变化、删除授权、回退均有明确条款；备份在 §3.3、回收站及删除授权在 §3.7、迁移在 §3.4、信任根在 §3.5、回退在 §3.8。**待验证假设**：跨设备/SMB/cloud 的身份、持久授权、稳定 lease、Windows 回收站及旧 Schema 拒写能否达到这些语义，本轮未运行原型或迁移。共享源的应用内删除仍与 ADJ-001 冲突，见 R-01；不能把八类都有标题等同于全部下游已验证。 |
| M2-C1 主要保留语义 | ADJ-001 `:16,29-30,62-64` 明确预检成功后同一事务移除 Lock/current/pinned、DB 全有/全无、提交后 cleanup pending 与仅用户显式重试；与 M2-C1 `:733-740,772` 对应。区别是 ADJ-001 的 PD-08 实际扩大冲突，见 R-01；不能据上述对应项认定全契约忠实。 |
| PD-01–PD-10 | 逐条阅读 `ADJ-001:54-67`：PD-01/03 为只读预览，PD-02 确认绑定，PD-04 零提前变化，PD-05/06 原子提交和回滚，PD-07 非后台重试，PD-08 共享引用，PD-09 批量与清理状态，PD-10 软删/自动清理。`ADJ-001:10,56,69-89,98-109` 把新增协议和实现标为 PENDING/NOT_RUN，未发现把 PD 预览/digest 当作已经实现的肯定陈述；但 PD-02 的单条映射和 PD-08 语义有 R-02/R-01。V2 现状陈述另见 R-05。 |
| 治理指针及越权 | 对照 `git diff`：AD-002 增加顶部横幅；INDEX、AGENTS、STATUS 更新入口；检查器扩展。当前 `STATUS:6-8` 仍指向 `REALUSE-DATA-SAFETY-6` ready，未见本轮释放实现 Task 的指针。现有 dirty 内容跨多个更早工作回合，不能仅凭本次状态把所有变更归属于 DSH。用户本轮明确要求审查；对 DSH 当时修改各指针的具体授权记录，本次只凭工作区无法独立核验，**不推断已获或未获授权**，请 DSH 随处置提供其授权和范围依据。未证明的权限争议不冒充 P0 事实。 |

## Verification

| 项 | 方式与结果 |
|---|---|
| 固定指纹与基线 | PowerShell `Get-FileHash -Algorithm SHA256`；`git rev-parse HEAD`、`git branch --show-current`、`git rev-parse --git-common-dir`：**PASS**，结果见上表。 |
| 当前治理检查器 | Windows PowerShell 启动 `pwsh -NoProfile -File tools/governance/check.ps1`：**EXIT 0 / PASS (2 warnings)**，提示 7 个非终态 Task 以及 `REBASELINE_PLAN` 预算达到 80%；没有把 PASS 当作功能或语义验收。 |
| ADJ-001 相对链接 | Python 只读逐行解析 Markdown 相对目标：**5/5 不存在**；见 R-03。 |
| 规则判别力 | 从实际脚本读取正则，以 Python `re` 只读内存匹配代表性中文/英文字符串；以 PowerShell `-like` 对内存中模拟的哨兵/索引替换求值：发现 R-04 所列反例。此为**规则级验证**，不是完整 checker 隔离端到端测试；PowerShell 正则和 Python `re` 并非全部语义等同，所列简单匹配仍须 DSH 用真实 checker 回归。 |
| 冻结正文与范围 | 比较 AD-002 HEAD blob 与当前内容，去新增横幅并归一行尾后相同；实际原始行尾口径限制见 R-07。审查 `git diff`、当前 Task 状态与涉及行；未证明全部未提交变更的作者或先前授权。 |
| 测试证据边界 | 本次用户只允许写本报告，因此未额外保存逐次原始运行日志或判别力 artefact；按 `doc/templates/REVIEW.md:49-53`，上述运行输出仅作本次**观察**，不能冒充仓库中已入库的判别力测试证据。完整 checker 正负例回归、构建、生产测试、迁移、备份恢复、真实磁盘删除及 GUI 均 **NOT_RUN**。未运行迁移，不 push。 |

**Architecture**：R-01 为用户指定 P0，R-02/R-03/R-04 为 P1；其余问题见 R-05–R-07，当前不予批准。**Verification**：完成限定只读静态检查、一次治理检查器运行及内存级反例；缺少可入库的隔离回归证据和运行时验证，不能宣称功能 PASS。

## 交回与复审

交 DSH 对 R-01–R-07 逐项接受或给反证，先处理 P0/P1 并固定修订后的全部权威文档与检查器 hash，再由未参与被审交付物编写的 Reviewer 复审。正式 ADR、契约、方案、Task 和其他人的未提交文件均未由本 Review 修改；不释放任何实现 Task。若修改影响原有检查器判定，先提供受影响全集、基线和代表性正负例；保留历史证据。
