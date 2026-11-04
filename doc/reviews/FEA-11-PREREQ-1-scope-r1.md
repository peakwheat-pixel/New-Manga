---
task_id: FEA-11-PREREQ-1
reviewer: Codex（用户直接委任；全新上下文，未参与本前置卡建卡）
reviewer_kind: agent
author: DSH（范围与 Task 建卡责任方）
base_commit: d1341945ba781ee465a654d5340f2a2c9373318b
reviewed_head: d1341945ba781ee465a654d5340f2a2c9373318b
decision: approved
review_type: scope
date: 2026-11-04
---

# FEA-11-PREREQ-1 Scope Review r1

## 身份、来源与审查边界

- 来源：用户在本独立 Codex 会话直接委任；主审未参与本卡建卡、实现或返修。本报告不代替 DSH 的 Appointment 登记与 findings 处置。
- 工作区：`G:/CODEX/New Manga`，`main`，Git common directory `.git`；开始时工作区 clean。`base_commit=reviewed_head` 表示审查当前卡片快照及来源，不表示存在生产实现 diff。
- 主审采用 code-review 的 Standards/Spec 两视角；辅助 Reviewer 均为 `fork_turns=none` 的独立只读上下文，未写文件、未参与实现。来源/子任务 ID：`/root/scope_standards`（Standards，session `01a1a6bb-413e-7d12-9cfc-78d1e2c6bb2b`）、`/root/scope_spec`（Spec，session `01a1a6bb-72af-7113-ab1c-1d3eda154f5b`）。主审 session `01a1a6ba-8156-7fa3-b5e4-5114e9f89eda`；主审重新核对所采纳发现并签发本报告；辅助结果不另构成项目 Appointment。
- 唯一写域：本报告。未修改 Task、STATUS/PLAN、生产代码、测试、证据、冻结契约；未 commit/push。
- 依据：当前 AD-002/AD-003 架构边界、STATUS/REBASELINE_PLAN、rolling checkpoint 当前记录；本前置卡全文；FEA-11 修订卡与 scope-r1（重点 S11-001…007）；提案 §8.1–8.4、§12.1、§15.5–15.6；C-14 v3、C-15 v1.1 §1/§3.2/§4.2/§5–6、C-16 v1.1 §0/§4、C-05 v1.2 §3.2、C-13 SC-D07/08；M2-C1 rev 2.12 §1/§3.2/§4 请求应答语义；`verify_pins.ps1`、`schema.py`/`migrator.py` 相关迁移机制及生产 resolve 窄接缝。协作协议按 §4/§5.1/§6、Review 模板核对。
- 索引核查：`doc/plan/FEA-CONTRACT-INDEX.md` 和 `doc/contracts/FEA-CONTRACT-INDEX.md` 均不存在；现有登记面为 `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`。未扫描历史 Task/证据全集；未打开无当前任务引用的 verification 资料。

## 结论

**approved（Scope）：P0=0 / P1=0 / P2=4。**

Architecture：本卡已经承载 S11-001 要求的 DDL/状态/命令前置，并把 S11-002…007 涉及的身份、CAS、lineage、双确认与资源版本选择纳入拟冻结面；未发现必须改变既有冻结语义的范围要求。没有因“契约正文尚未产生”而把 proposed 卡误判为缺失实现。

Verification：本轮为范围静态审查，治理检查与现有 17 pins 实测通过。P2 为可局部修正的验收/登记/流程清晰度问题，不构成架构重开；其中 AC 语法必须在进入 REVIEW 状态前修正。建议 DSH 在范围冻结/Appointment 登记时一并处置。

**可以交 DSH 冻结本前置卡的工作范围并任命契约起草 Owner；不能据此冻结尚不存在的 C-17 正文，不能释放 FEA-11 生产实施。** 正文与最终字节独立 Review、DSH 冻结集成及 PREREQ done 均仍待后续执行。

## Standards（executed）

既有 17 个 pin 对象全部保留、生产写域为空、证据目录在 allowed_paths 中；符合本前置的文档/契约性质。发现 S11P-001、S11P-002 两项 P2。代码 smell baseline 为 N/A（无生产代码变更）。`M2-C1` **不在** `verify_pins.ps1:6–13` 的 17 项集合中，因此其经授权的窄增量与 AC-P7“既有 17 契约字节不改”并无实质矛盾；`:34/:89` 的“例外”措辞可顺手澄清，不能据此报冻结字节冲突。

## Spec（executed）

目标 `:45–52` 与 AC-P1…P8 覆盖所需安全边界；未见 P0/P1。发现 S11P-003 的派发时机歧义；主审另提出 S11P-004 的验证矩阵精化。现有 FEA-11 ready 硬前置仍有效，不将“可能提前安排范围审查”描述成已经越权实施。

## Findings

全部 `open`，交 DSH 处置；P0、P1 均无。

### S11P-001 · P2 · AC 缺少 lifecycle v3 的勾选框

**位置**：`doc/tasks/FEA-11-PREREQ-1.md:64–71`；依据协作协议 §4.3、`tools/governance/check.ps1:813–818`。

八项 AC 都以 `- **AC-P…` 开头。检查器在 `in_review/approved/done/closed_with_limitations` 只匹配带 `[ ]/[x]` 的 AC；本轮按相同正则只读核对为 **0 条**，普通 AC 标题为 **8 条**。目前 proposed 下 check PASS 不代表后续 REVIEW 门禁可过。

**建议**：改为 `- [ ] **AC-P1…` 至 P8，保留当前 `<<PARTIAL: …>>`；达成后再同步 `[x]` 与 `<<MET>>`。不改检查器来迁就卡片。此项修订须早于进入 REVIEW；没有改变本卡安全范围或验收目标，列 P2。

### S11P-002 · P2 · 拟写索引不存在，现有冻结矩阵未列入写域

**位置**：Task `:26/:56–60/:70`；现有 `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` 的 C-15/C-16 登记行；`verify_pins.ps1:6–13`。

允许创建新 INDEX 本身合法，但卡片既未把它列为交付物，也未说明其与现有 FREEZE_MATRIX 的关系；Owner 可能交付 C-17 与第 18 项 pin，却留下既有冻结矩阵缺项，或另造第二份登记权威。现有矩阵又不在本卡允许写域内。

**建议**：优先以 `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` 替换 allowed_paths 中的虚拟 INDEX，并补入交付/AC-P7；由 DSH 单点追加 C-17 记录，保留历史行。若 DSH 确需新 INDEX，先在本卡说明用途、权威关系、维护人及具体交付，不默认为已有文件。当前 pin map/冻结矩阵未登记 C-17，未发现 ID 冲突；C-17 仍只是可供 DSH 确认的新 ID，不由本审查预占。

### S11P-003 · P2 · 下游 scope-r2 的触发点“approved”有双重含义

**位置**：Task `:7/:39/:90`；对照 `doc/tasks/FEA-11.md:7` 的 done Gate、STATUS 的冻结→scope-r2 顺序。

`:90` 写“FEA-11 的 scope-r2 在本 Task approved 后派发”，而 `:7` 也用 approved 表示本轮 scope approved。两者都早于或可能早于 PREREQ 集成 done，易在没有最终 C-17 基线时启动 scope-r2。现有 ready 条件仍要求 done，因此不是 Gate 已被绕过。

**建议精确替换**：

> 本卡 Scope Review approved 后，由 DSH 冻结工作范围并 Appointment 契约起草；本卡契约最终字节独立 Review approved、DSH 冻结集成并 done 后，固定 C-17/pin 基线，再派发 FEA-11 scope-r2；scope-r2 approved 且 DSH 完成 ready/Appointment 登记后才允许 FEA-11 实施。

### S11P-004 · P2 · “冻结决议可执行”的完成证据宜从通用评审表细化为可判定产物

**位置**：Task `:52/:64–69/:77–82`。

当前 AC 已要求“可执行/可断言”，因此不是范围漏项；但矩阵多数只列“契约/评审记录”，AC-P1 的实际迁移验证全部指向 FEA-11 实施后，`:52` 的旧证据缺失降级又没有明确 AC 映射。不同交付者可能对何时足够冻结采用不同口径。

**建议**：补一个契约关闭清单，作为 AC-P1…P6/EV 的索引，逐项绑定条款、决定人、输入样例和唯一预期结果；不要求本卡编写生产实现或完整生产测试。至少包括：

1. P1：规范 SQL 全文与版本/迁移登记规则；在内存或隔离合成 v7 库执行拟议增量，记录 FK/唯一性/CHECK 负例、失败后 schema 与迁移元数据回滚判据、旧写者拒写判据。真实升级链与全量回归仍归 FEA-11。若 lineage 方案需额外持久表/列，其 DDL 一并列入契约，不能仅写“未来再定”。
2. P2/P4：持久状态转移表（前态、事件、守卫、写入方、持久确认点、后态）；Host durable 授权前后、Core 提交前后、ACK 前后各有恢复/重放的预期；三类代次与人工基线的失配反例、整批最后一项失败的唯一结果。内部函数/锁 API 不冻结。
3. P3：命令/DTO 字段的 required/nullability/type/枚举/范围及未知字段行为，错误 code/category/retryable，能力缺失与旧新 Host×Core 四象限；文档 rev、per-command wire minor、全局默认 minor 分开记录，不预设必须 bump。
4. P5/P6：旧→新 lineage 的读写隔离反例、旧 edit token/Run/draft/candidate 的预期；旧键读取旧摘要、新绑定 resolve/issue 选择新资源的对照样例。将 C-15 §3.2 的 profile 可比/重复组待确认/旧证据缺失且不能按冻结参数重算的降级规则明确挂到 AC 与矩阵。

规范 SQL 的隔离验证脚本可放已允许的 `verification/FEA-11-PREREQ-1/`；临时 DB/输出放 `G:/CODEX/New Manga.workspace/FEA-11-PREREQ-1/`，由后续 Owner/DSH 记录 Resource Manifest。本轮没有创建这些资源或执行未来 SQL。

## 冻结面完整性与既有契约兼容判断

| 面 | 当前卡承载 | 审查判断 / 后续冻结要求 |
|---|---|---|
| DDL、索引、FK、约束、迁移/回滚 | 目标1/8、P1 | 已包含；当前 `default_migrations()` 仅 v1–v7，v8 为下一候选而非已分配版本。遵循现有逐 migration 事务，不宣称整条升级链一次回滚；不得改旧 SQL/checksum |
| plan/operation 与存储归属 | 目标2、P2 | 已包含；Core 管业务持久化，Host 仅管授权/OS 元数据；Host durable authorization 在前。C-14 SC-S04 的双方确认前不可读须有重启后仍有效的门控，不可只靠内存 |
| wire、错误、能力、兼容 | 目标3/4、P3 | 已包含；C-16 §0 存在 additive 默认 minor=3 先例，M2-C1 rev 与协议 minor 并非同一数字。新增 Source 命令自有操作身份，不复用会话内 import receipt，也不把 request_id 当幂等键 |
| CAS、人工基线、事务与原子性 | 目标5、P4 | 已包含；分别定义 SourceVersion/binding_version/Host generation 的比较与事务重读，稳定 lease 持有到提交边界；没有 Host/Core 分布式事务，不以“整批回滚”暗指撤销已持久授权。stale 零业务写与拒绝审计的边界须显式决定 |
| lineage、历史和在途任务 | 目标6、P5 | 已包含；可恢复映射需有实际持久表达，不能只依赖 `previous_binding_id` 自动推导全部区域归属；人工迁移新建 revision，保留 C-13 SC-D07/08 的 BaseRevisionId/统一事务语义 |
| resolve 版本选择 | 目标7、P6 | 已包含；生产代码当前有 `page-rendition-{page_id}`，未来同步需版本选择。C-15 §4.2 的 managed 稳定键不变，referenced 可新增版本选择同时保留旧键/摘要不变；无须当然 UNFREEZE |
| 跨版本证据与降级 | 目标8 | 已包含；引用 C-15 §3.2，避免新文档产生第二套匹配真值。建议按 S11P-004 补 AC/证据映射 |

**additive 的边界**：新建两表及必要 lineage 持久表达正是 C-15 §1 的 v8+ 预留；对同步命令另建 durable 状态机，不改变 C-16 §4 导入的会话内 receipt/逐页提交。新增确认/恢复门控也不得扩大 C-05 的 V 或把 V 当 R。

若起草结果要改变既有 C-14 操作身份/范围、C-15 的 generation `<=` 可读兼容规则/profile 匹配、C-16 导入状态或提交单元、managed 稳定资源键、C-05 可见性，**新 C-17 声明不能覆盖旧冻结条款**。应暂停冲突部分，交 DSH 在单独明确的 UNFREEZE 授权载体与写域下处理；当前卡没有该授权，不能顺手改旧 17 契约。无需为尚未发生的冲突预先扩大写域。

## 写域与交付的精确建议

- 保留：Task 本身、C-17 提案/FROZEN 记录、专属 Review/Handoff、`verification/FEA-11-PREREQ-1/**`；这些足以交付契约和隔离验证证据。
- 登记：按 S11P-002 优先补 `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`，删去未决定用途的 INDEX 路径；DSH 负责最终 ID/登记。并非要求改其他历史文档。
- M2-C1：保留当前**条件写权**，在本 Task 的“DSH 范围裁定”明确具体章节/命令/错误与版本策略、批准人/时间/commit；未获明确授权不写。若仅由 C-17 承载新增面而不改 M2-C1，同样记录无增量的决定，避免 `rev 2.13?` 成为默认已批准版本。授权可记录在已允许的 Task 中，当前不缺新的任意授权文件写权。
- pins：`verify_pins.ps1` 已写明 DSH 单点更新，Owner 提供候选条目/指纹，由 DSH 在最终确认 C-17 ID 与源路径后仅追加 map 项；沿用现有 missing-record/missing-contract/no-pin/mismatch 一律失败，不引入“未冻跳过”或改变旧 17 项的 hash basis。17→18 是检查集合扩展，不是改旧 pin。新增缺记录/错误 pin 负测应在隔离副本做。
- 冻结记录至少写明最终语义 commit、实际 reviewed_head、工作树 SHA-256/blob ID/blob SHA-256、复核字节与最终冻结字节的差异（仅允许明确记录的状态元数据差异）。最后一次编辑后复算；pin PASS 不能代替最终条款字节独立 Review。
- 只读引用另列 `read_references` 或正文表即可：`schema.py`、`migrator.py`、referenced import runtime、SourceReadCoordinator/SourceAccessRegistry、`core_service.py` resolve 与 resource catalog 相关接缝。**不应**为契约调研把这些文件加入 allowed_paths；读引用不产生生产写权。
- Handoff/EV/Resource Manifest 已在交付物中。建议 EV 明确覆盖 P1…P8；不新增依赖、不调用真实 AppData/源卷、不复写 FEA-08/09/10 证据。

## 是否拆成更小前置

**不建议再设“只冻两表+命令，其余全部留 impl-design”的硬前置。** 两表字段与状态/恢复、CAS 比较对象、lineage 持久表达、资源版本选择互相约束；移走这些可观察语义会让 DDL/wire 先冻结、随后因实现设计再次开契约。

建议维持一个前置卡，在内部区分交付层次：本卡冻结规范 SQL、跨 Host/Core 可观察状态/存储归属、命令与错误/能力/版本、原子与重放结果、lineage/资源不可变及兼容不变量；FEA-11 的 impl-design 承接类/函数分解、线程/锁/句柄 API、检查代码顺序、SQL repository 组织和生产接线。正式生产迁移、真实杀进程矩阵、真实 IPC/resolve 字节及全量回归都留给 FEA-11。隔离 SQL 验证只证明契约可执行，不宣称产品实现完成。

## 验证与 NOT_RUN

本轮环境：Windows PowerShell 调用 `pwsh -NoProfile`；工作目录 `G:/CODEX/New Manga`；均针对上列 reviewed_head。无 venv/模型/真实用户数据参与。以下为本报告内嵌的只读检查记录，未另写 tracked 证据日志。

| 检查 | 实际执行/结果 | 状态 |
|---|---|---|
| Git 基线 | `git branch --show-current` → main；`git rev-parse --git-common-dir` → .git；HEAD 如 frontmatter；开始与写入前 `git status --short`、`git diff --stat` 空 | PASS，EXIT=0 |
| 当前治理 | `pwsh -NoProfile -File tools/governance/check.ps1` → `Governance scope: 15 current documents`；`Task: doc\tasks\FEA-11-PREREQ-1.md`；`Governance check: PASS (2 warnings)` | PASS，EXIT=0 |
| 治理 warnings | 10 个非终态 Task 的活性提醒；REBASELINE_PLAN 达预算 80%（5771 bytes / 55 lines） | 已记录，不据此关闭/改写任务 |
| 当前 pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → C01b/C02/C03/C04b/C05/C06/C07/C08/C09/C10/C11/C12/C13/C14/C15/C16/FEA01 均 OK；`PIN AUDIT: PASS (all 17)` | PASS，EXIT=0；不是未来18项结果 |
| AC 识别 | PowerShell 以内存 regex 复用 checker AC 形状：`v3_checkbox_AC_count=0`、`plain_AC_count=8` | 已验证静态缺口；未改 Task 状态模拟门禁 |
| 索引/提案存在性 | `Test-Path`：plan INDEX=False、contracts INDEX=False、现有 FREEZE_MATRIX=True、C17 draft=False | PASS，EXIT=0；如实记录尚无新正文 |
| v8+ SQL/FK/约束/失败注入 | 尚无新契约 SQL，本轮不编造/执行 | NOT_RUN；后续契约隔离验证 |
| 18 pins/新增 checker 负测 | 尚无 C-17 冻结记录/pin，本轮不改 checker | NOT_RUN |
| pytest/.NET/build/真实 IPC/杀进程/用户流程 | 范围审查不实施生产功能，不生成或复写旧 tracked 证据 | NOT_RUN；归 FEA-11 |
| 新契约最终条款字节 Review/冻结/集成 | 本轮仅审 Task Scope | NOT_RUN；不由本结论替代 |

## 下一步与可转发指令

- **Task / Agent**：DSH 处置本轮 P2、冻结 FEA-11-PREREQ-1 工作范围并 Appointment；建议契约起草 Owner=Codex（新的实施上下文），最终契约 Reviewer 为另一个全新上下文 Codex/ZCode。当前主审及两名辅助 Reviewer 不接本卡实现/返修。
- **Recovery point**：`G:/CODEX/New Manga`，`main`，base/head=`d1341945ba781ee465a654d5340f2a2c9373318b`；新实现 branch/worktree 待 DSH 创建并登记，不能把本报告当作已释放工作区。
- **Scope / Deliverables**：DSH 修改本卡、现有冻结矩阵与其职责内状态/Appointment；起草 Owner 仅按重新冻结的 allowed_paths 交付 C-17、条件授权的 M2-C1 窄增量、专属 EV/Handoff/Resource Manifest。旧 17 契约、生产源码/测试与历史证据不改；pins 由 DSH 单点维护。
- **Verification / Gate**：scope P2 有 disposition；Owner/Reviewer/base/worktree/写域完成登记才释放起草；契约可执行清单、最终字节独立 Review、check/pins 与 DSH 集成完成后 PREREQ done；之后才 FEA-11 scope-r2→ready。新命令/Schema 的产品实现仍待 FEA-11 单独释放。

> 请 DSH 在 G:/CODEX/New Manga（main）接收 doc/reviews/FEA-11-PREREQ-1-scope-r1.md；审查 base/head=d1341945ba781ee465a654d5340f2a2c9373318b，先核对当前 HEAD 与未提交内容。Scope 结论 approved，P0/P1=0、P2=4；请处置 S11P-001…004：补 v3 AC 勾选框，以现有 FREEZE_MATRIX 承载 C-17 登记或明确新索引关系，统一 PREREQ done 后派 FEA-11 scope-r2，精化可执行契约/隔离验证清单。登记最终契约 ID、DSH 对 M2-C1 的窄授权或不修改决定、pins 单点责任及最终字节复核方式；v8 不预占。随后冻结范围并任命新的契约起草 Owner/独立 Reviewer，branch/worktree 待你创建登记。本轮不释放 FEA-11 生产实施，不改旧17契约或FEA-08/09/10证据，不push。交付 C-17/冻结记录/EV/Handoff/Resource Manifest；运行 pwsh -NoProfile -File tools/governance/check.ps1 和 verify_pins.ps1，记录逐项 EXIT/NOT_RUN；契约正文 approved、最终冻结字节/pin固定、DSH集成done后再派全新上下文做FEA-11 scope-r2。

## 交付核对

写入后复核：`git status --short` 仅返回 `?? doc/reviews/FEA-11-PREREQ-1-scope-r1.md`；`git diff --stat` 与 `git diff --cached --stat` 均空；`git rev-parse HEAD` 仍为 `d1341945ba781ee465a654d5340f2a2c9373318b`。再次执行 `check.ps1`，EXIT=0，PASS（同上 2 warnings）。本报告为唯一新增文件，未 commit/push；结论仅适用于 frontmatter 的 reviewed_head。
