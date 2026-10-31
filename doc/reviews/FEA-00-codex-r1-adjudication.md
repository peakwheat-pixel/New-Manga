---
document_id: FEA-00-codex-r1-adjudication
kind: dsh_adjudication
adjudicator: DSH（Lead / Architect / Integrator）
adjudicated_review: doc/reviews/FEA-00-codex-r1.md
adjudicated_review_sha256: f2fd02e0dcff49337c9251315aef3f3480446f98e567b594c63e2eee17693ba2
reviewer: Codex（未参与被审交付物编写）
author_of_reviewed_artifacts: DSH
base_commit: 1180cdba79e4d610521dde13f0c8a458220f9d90
decision: accepted_all_with_revisions
review_status: ADDRESSED_PENDING_R2
captured_at: 2026-10-31T20:35:00+08:00
---

# FEA-00 Codex 独立 Review r1 处置（DSH adjudication）

**结论：R-01–R-07 全部接受（7/7，其中 R-05 为"结论接受、成因表述修正"）；已按裁定修订被审文档，等待 Codex 对**新 hash**复审。本处置**不是批准**，不释放任何实现 Task。**

Codex r1 判 `changes_requested`：1×P0（R-01）、3×P1（R-02/R-03/R-04）、3×P2（R-05/R-06/R-07）。DSH 对每一 P0/P1 都独立回到代码与冻结契约复核，未直接采信。

## 1. 逐项处置

| ID | 级别 | 判定 | DSH 独立核验（代码/契约证据） | 修订动作 | 状态 |
|---|---|---|---|---|---|
| **R-01** | P0 | **接受** | `M2-C1:764` 原文："**无法安全拆分**共享关系或发现**未列明**的目标外引用时，预检整体失败"；`:752` 条件是"关系图、目标外引用…**不一致**"；`:768` 要求"仅删除清单所列文件，**不递归清空共享根**"。因此可安全拆分的共享引用**不是**阻断条件。我原 PD-08 写成"目标外引用/关系图/共享源在预检阶段即冲突"=**无条件扩大**，与 `M2-C1` 及 AD-003 §3.7"共享源默认保留"直接矛盾 | PD-08 重写为三态：可安全拆分→允许删除自有内容与清单内文件、保留共享物理文件与其他项目绑定；只有"无法安全拆分/不一致/未列明"才整批 fail-closed。并显式声明"原文件是否删除只由 D 流程决定"；AD-003 §3.7 同步补一条同义约束；§2 基线表注明冲突条件 | **fixed**（ADJ-001 r2、AD-003 r2） |
| **R-02** | P1 | **接受** | `M2-C1:684-695` 单条 payload 为 `{book_id, confirm_permanent_delete}`；`:723` 明示"单条命令维持…单个 `book_id` 请求形状，**绝不接受数组**"；`confirmed_book_ids/confirm_count` 属批量。我的 PD-02 只写批量三字段绑定，单条无映射；§2 表把"目标覆盖全部 Book 行"放在单条/批量同一行，易误读 | PD-02 拆为**单条/批量分别绑定**（单条：`book_id` + `inventory_digest`，禁止批量字段；批量：有序三字段 + digest）；§2 行注明全库保护**仅批量**适用，单条按其既有确认语义不变 | **fixed** |
| **R-03** | P1 | **接受** | 本轮机械复算：ADJ-001 头部 5 个 Markdown 目标相对 `doc/contracts/` 解析 **5/5 不存在**（`AD-002…`、`AD-003…`、`contracts/M2-C1…`、`reviews/…`×2）。原因是 ADJ-001 位于 `doc/contracts/` 却按 `doc/` 视角写路径；且 ADJ-001 未在 `$staticFiles`，检查器不校验其内链 | 修正全部相对路径；把 `doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md` 纳入 `$staticFiles`，从此其链接纳入校验 | **fixed**（`check.ps1` r2） |
| **R-04** | P1 | **接受** | 我承认 r2 复核"新规则有判别力且无误报"只能覆盖当时一对样本。Codex 的反例成立：整行正则会对"…为 React + TypeScript；该表述已被取代"这类**合法历史说明**误报；全文 `-like` 又可被正文无关提及满足 | **撤销整行正则扫描**；改为仅校验 4 个**显式断言面**（AD-002 哨兵行 / AD-003 哨兵行 / `00_INDEX` 机器字段 / AGENTS 产品边界行）+ 双指针存在性；在脚本注释与 `00_INDEX` 中写明"正文陈旧表述属审查事项，不属正则事项"；按 `09_COLLABORATION §4.4` 补做受影响全集、基线与 5 例边界样本（见 §5） | **fixed**（`check.ps1` r2 + 基线矩阵 + 5/5 样本） |
| **R-05** | P2 | **结论接受，成因表述修正** | 核验：`trash.py:119/188` 确有页级 `soft_delete_pages`/`restore_batch`；`library/service.py:97-100` `delete_book` 走 `book.soft_delete()`；V2 `LibraryViewModel.cs:793-796,1214-1224` 对回收站读取/恢复/永久删除**全部**返回"能力待接入"。故我原文两处说法各有问题：ADJ-001 说"V2 只有不可逆硬删"——V2 连硬删都不可达；AD-003 说"软删命令不存在"——**命令**确实不存在，但**服务层**存在 | 用**四层现状表**（Core 命令 / 应用服务 / Host 接口 / V2 UI）替换单句结论，明确"服务层已有实现、命令面与接线缺失、用户当前无可用删除路径"；§8 未实现项同步 | **fixed** |
| **R-06** | P2 | **接受** | 核验被审方案：`L631/L633` 已把 `FEA-04b` 列为 FEA-06 依赖，依赖图 `L662 P04b --> P6`、`L910` 再述。我在 r2 复核 §3.3 写"FEA-06 仍无设计依赖"**是错的** | 在 r2 复核文件**追加**"更正记录"（不改写原文）：依赖已声明，但四页设计与 Gate 尚未完成 | **fixed**（追加更正） |
| **R-07** | P2 | **接受** | AD-003 §7 原写"AD-002…均**未修改**"又在下一行写"对 AD-002 追加横幅"，自相矛盾。CRLF/LF 口径说明成立（工作树 CRLF、blob LF，`core.autocrlf=true`）；我确实没有"变更前工作树字节"的独立基线 | §7 改为**三口径**：①文件已变更（hash 已变）；②原正文与历史哨兵逐字保留（仅追加）；③变更前工作树原始字节无独立基线，只能声明"正文内容未改" | **fixed** |

## 2. 授权与范围依据（Codex r1 §「治理指针及越权」要求 DSH 提供）

Codex 指出"仅凭工作区无法独立核验 DSH 修改指针的授权记录，请 DSH 随处置提供"。以下为可核对的依据：

**用户 2026-10-31 授权原文（第 2 轮任务指令）**：

> 本次授权 DSH 修改为正式记录和裁定所必需的权威文档及治理指针，具体范围应先列明并遵守项目生命周期规则。保留其他人的未提交内容。
> ……本轮不得修改生产代码，不得释放或激活任何实现 Task，不得 push。

**DSH 在动手前声明的写入范围（8 项）与执行结果**：

| # | 文件 | 声明的依据 | 实际 |
|---|---|---|---|
| 1 | `doc/AD-003_…`（新建） | 用户决定 1/2/3；AD-002 `Decision authority: User` | 已建，本轮 r2 修订 |
| 2 | `doc/contracts/ADJ-001_…`（新建） | 用户决定 4/5/6；`M2-C1 §5.11` | 已建，本轮 r2 修订 |
| 3 | `doc/reviews/FEA-00-dsh-r2-technical-recheck.md`（新建） | 用户"一"（技术复核，非独立 Review） | 已建，本轮追加更正 |
| 4 | `doc/AD-002_…`（**仅追加**横幅） | 取代范围必须可发现 | `git diff --stat`：**5 insertions / 0 deletions** |
| 5 | `doc/00_INDEX.md` | 治理指针（含修正一处过期 React 架构行） | 已改 |
| 6 | `AGENTS.md` | 产品边界指针 | 已改（他人 Antigravity 裁决改动保留） |
| 7 | `doc/STATUS.md` | 运行状态指针（预算内） | 已改（2555/3200 B） |
| 8 | `tools/governance/check.ps1` | 用户"二"要求协调哨兵与检查器 | 已改，本轮 r2 重构 |

未越界项核验：`git status` 中 `doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md`（`2f925cca…`）、需求文档、`M2-C1`（`dfcd47ca…`）、V11R/Region 契约、`REBASELINE_PLAN`、`TASK_LEDGER`、`doc/tasks/**`、`verification/**`、生产代码**均未修改**；未创建/激活 Task；未 push。他人未提交改动（`.orchestrator/*`、`09_COLLABORATION`、`AI_COORDINATION`、`GOVERNANCE_TAKEOVER`、`V11R_PROGRAM`、`EXECUTION_DIRECTIVE_AD002_V2`、`AD-002` 之外的旧改动）原样保留。

**一处我主动披露的偏差**：checker 的**第一次**扩展（r1）在书面定义"受影响全集"之前就落地了，只保留了前后运行结果；违反 `09_COLLABORATION §4.4` 的"先定义全集再改"顺序。已在基线矩阵 §4 记为过程偏差，并通过**撤销正则扫描、收敛为断言面**把变更面缩到可枚举范围。Codex 若认为该偏差本身需要独立裁定，请在 r2 中明确指出。

## 3. 未采纳 / 保留意见

无"不采纳"项。两点保留：

1. **R-04 的机器校验边界**：撤销正则后，**正文级**陈旧断言不再被机器发现（例如某个文档在散文里声称旧架构）。这是**有意的取舍**：机器只能可靠校验受控断言面；正文一致性仍靠 Review。已写入 `00_INDEX` 与脚本注释，防止后来者把 PASS 当语义证明。
2. **R-01 的验收深度**：本轮只做了契约文本层面的判定对齐，未实现、未做运行级反例（无 SDK 变更、无生产代码）。"可安全拆分"的判定算法与测试属 FEA-12 契约冻结范围，仍是 `NOT_RUN`。

## 4. 修订后指纹（本批）

| 文档 | SHA-256 | 变化 |
|---|---|---|
| `doc/contracts/ADJ-001_…` | `4ff0a3d25e5dc68de8b6ba16ff56ac86600181e502c8282aae16091e1a65faba` | r2 修订 |
| `doc/AD-003_…` | `17a89d15efc900299f1ddbc8599c401125e6596cb0d7c3a1beab24557f09da14` | r2 修订 |
| `doc/reviews/FEA-00-dsh-r2-technical-recheck.md` | `d0bf89ff045e3c35ff9bf19d16a632a2c6dba78d51b4ae7062610ed366919eb3` | 追加更正 |
| `tools/governance/check.ps1` | `77be514d3693672637100eefdfe15b4d9edfe199d64300ae588f361d43bee76d` | r2 重构 |
| `doc/00_INDEX.md` | `0dc43d2980666f13c32391e193f4b5450294a9e2132475b83d4ba2f05a46e306` | 指针/字段 |
| `doc/AD-002_…` | `0bd11c76c6a4447ba5f5084d1b427970fc3db7f5eb7d934f5a3e10e0a07d3157` | 未变 |
| `AGENTS.md` | `678bda95e6edace4cb9311ee1eeb825fd66974d372da0e50b866530e125acea0` | 未变 |
| `doc/STATUS.md` | `e8fe3affdabe315394a53f0d710e5ba16d480650716ea97f541977ade3de4a64` | 未变 |
| 方案（被复核对象，未改） | `2f925cca7229d17a13943bfd4c297386ae21010f7bf8b61c3ae5169795afa120` | 未变 |
| `M2-C1`（冻结契约，未改） | `dfcd47cabe9831b270fb0a6f985e50ea9e5a34b165f2c776a8f1e34c777bae72` | 未变 |

本文件自身 hash 由交付后外部计算。

## 5. 判别力与基线证据

| 证据 | 位置 | 结果 |
|---|---|---|
| 断言面 5 例边界样本（真实脚本函数抽取） | `G:/CODEX/New Manga.workspace/agent-output/dsh/FEA-00/checker-fixtures.ps1` + `checker-assertion-surface-fixtures.log` | `cases=5 bad=0 RESULT=PASS`（含 R-04 的误报反例 F4 与绕过反例 F5） |
| 受影响全集 + 基线错误矩阵 | `…/FEA-00/checker-change-baseline-matrix.md` | 变更前后 PASS 基线、逐规则影响、过程偏差与未覆盖项 |
| 治理检查器整体运行 | `pwsh -NoProfile -File tools/governance/check.ps1` | 见交付报告（r2 落地后期望 `PASS`；此前 FAIL 全部来自我自己新增文档的断链，已修复） |

## 6. 复审安排与 Gate

| 项 | 状态 |
|---|---|
| 独立 Review 席位 | ZCode `reviewer_unavailable`（无 CLI）；**Codex 已实际执行 r1**（未参与被审交付物编写） |
| r2 复审 | **待发起**：对 §4 的**新 hash** 复审；复审范围 = ADJ-001 r2、AD-003 r2、`check.ps1` r2、`00_INDEX`、`AGENTS`/`STATUS` 指针、本处置文件、（可选）r2 复核更正段 |
| 批准状态 | **未批准**。修订后必须由 Codex 对新 hash 出具结论；DSH 不自审 |
| Gate | `G-ADR` SATISFIED（记录已存在，语义受 r2 修订影响但方向不变）｜`G-DELETE-SEMANTICS` **SATISFIED w/ r2 修订**｜`G-CONTRACT`/`G-DELETE-CONTRACT`/`G-SAFETY`/`G-FRONTEND` **OPEN**｜`G-REVIEW` **ADDRESSED_PENDING_R2**｜`REALUSE-DATA-SAFETY-6` 仍 `ready`（未变） |
| 实现 Task | **未释放、未激活任何实现 Task** |

## 7. 未修改声明

`M2-C1`、V11R/Region 冻结契约、方案原文、需求文档、Task/STATUS 指针语义、历史 Review 与 evidence pin **均未修改**；未运行生产代码、迁移、清理或 push。本文件是**新增**处置记录。
