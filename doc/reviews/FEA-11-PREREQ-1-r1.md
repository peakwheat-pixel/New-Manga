# FEA-11-PREREQ-1 契约最终字节独立 Review（C-17，r1）

- 审查者：**ZCode 全新上下文**（session `sess_ec2aaf7b-c0cd-4c1c-8696-436c55733bf3`；未参与 C-17 起草/收尾/返修）。
- reviewed_head：`69d7c31ee60318c6f8a042c60c3f749a0ffda6a6`；工作区 clean；只读（未写任何仓库文件，本报告由 DSH 依据其最终回复归档）。
- 结论：**approved（P0=0 / P1=0 / P2=6）**。

# FEA-11-PREREQ-1 契约最终字节独立 Review（C-17）

## 身份、来源与边界

- **审查者**：ZCode，全新上下文（本会话），未参与 C-17 起草、收尾或返修；按 Appointment 由 DSH 派发。
- **reviewed_head**：`69d7c31ee60318c6f8a042c60c3f749a0ffda6a6`——与审查开始时 `git rev-parse HEAD` 一致；工作区 clean（`## main`，零未提交/未 staged）。
- **只读声明**：未修改任何生产代码/测试/证据/契约/Task，未 commit/push，未写任何仓库文件；本报告为唯一产出（正文交付，DSH 归档）。
- 依据：C-17 草案 9 章、FROZEN-C17 DRAFT、Task 卡 AC-P1…P8、Appointment、PREREQ scope-r1、FEA-11 scope-r1（**注：FEA-11 实为 AC11-1…10 共 10 个 AC**，任务书"12 AC"系笔误，按实际 10 项核对）；上游 C-14 v3、C-15 v1.1、C-16 v1.1、C-05 v1.2、C-13、M2-C1 rev 2.12（§3/§4/§5.7/§8/§12）、FEA-00 提案 §8/§15.5–15.6、冻结矩阵、生产 `schema.py`/`migrator.py`/`referenced/runtime.py`/`core_service.py` 代码事实。

## 结论

**approved（P0=0 / P1=0 / P2=6）。** C-17 提案在 DDL/状态机/命令面/CAS/lineage/resolve 六个冻结面上完整、自洽、可断言；与 C-14/C-15/C-16/C-05/C-13/M2-C1 冻结语义无字节冲突，无需 UNFREEZE 任何既有契约；M2-C1“无增量”决定成立；pins 17→18 由 DSH 单点的流程合规且可执行。6 项 P2 均为文档显式性/边界补注/证据判别力问题，不构成架构重开。**建议 DSH 在处置 P2 后进入冻结（pins 18）并随后派发 FEA-11 scope-r2。**

## Findings（全部 open，交 DSH 处置）

### R17-1 · P2 · STALE_BASE_REVISION 的 retryable 投影与冻结 FEA-05 wire 契约不一致
**位置**：C-17 §8 `:373`；`doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md:59`（FROZEN v1.0，2026-11-02）；M2-C1 §8 `:1183`。
**问题**：C-17 投影为 `conflict | true`；FEA-05（drafts_apply 面）冻结为 `conflict | false`。M2-C1 §8 明确 retryable 是命令级投影、不得推广为同一 code 的全局映射，故**不构成对冻结字节的违反**；但同一 code 在两面并存不同 retryable，Host/UI 若按 code 缓存重试语义会混淆。
**建议**：冻结前在 C-17 §8 或冻结记录注明差异理由（“重新 prepare/确认后可重试”与“同请求原样重发不可重试”两种口径），或统一为 false。

### R17-2 · P2 · scope=all 与 project_ids 1..20 上限的组合边界未定义
**位置**：C-17 §5 类型段 `:207`（project_ids 1..20）、§5.3 `:269`（"all时等于冻结引用集合book去重值"）。
**问题**：单源被 >20 个 book 引用时，all 范围的 Scan/PlanBody 无法合法构造（触发 INVALID_REQUEST 数组上限），契约未规定该场景产品语义（拒绝并要求分批？上限提升？）。行为是 fail-closed 可预期的，但边界缺一句话。
**建议**：冻结前补明确（推荐：超限 typed 拒绝并指引分批，不静默截断）；这是唯一建议在 scope-r2 前落定的 P2。

### R17-3 · P2 · apply 守卫未显式列"plan 未过期"；§2.1 runner 次序措辞略超代码事实
**位置**：§3.1 `confirmed→apply` 行 `:142`、§3.2 apply 行 `:158`；§2.1 `:118`（“同连接断言/FK check”）。
**问题**：TTL 约束散见 §5.3/§8（expired cause），转移表守卫列未列“未过期”（可推导但不显式）。§2.1“同连接断言/FK check”是对 MigrationRunner 通用次序的概括——实际 `migrator.py` 中 validate 回调仅 v7（`:236`）、`PRAGMA foreign_key_check` 仅 v5（`:222-231`）；v8 为纯新增空表，两者均不需要，无实质影响但宜精确。
**建议**：scope-r2 或冻结记录显式化“apply 守卫含 plan 未过期”。

### R17-4 · P2 · captured_v7/native lineage 行的 operation_id 归属未写明
**位置**：§2 `source_revision_lineage.operation_id`（可 NULL）`:106`；§7.1 `:306`。
**问题**：首次同步捕获事务（captured_v7）是否回填当次 operation_id、native 日常写入留空，契约未一句话定；SQL 允许 NULL，语义无害。
**建议**：补一句（推荐：captured_v7 填当次 operation，native 留空），便于审计查询。

### R17-5 · P2 · examples 脚本四个 old-*-model PASS 判别力弱
**位置**：`validate_examples.py:85-87`；examples.log 对应 4 行。
**问题**：old-draft/old-edit-token/old-prepared-run/old-candidate 四行 PASS 复用同一断言（changed 边排除），未覆盖其文案声称的"preserved as history/draft/candidate"保留语义；CAS 模型 9 行亦为轻量基线模型。脚本 LIMIT 行已诚实声明"production behavior NOT_RUN"，**不构成证据冒充**，但 AC-P5 证据中该部分强度有限（AC-P5 核心由 SQL lineage 负例 6 个 + lineage model 支撑，不受影响）。
**建议**：保留现状，由 FEA-11 生产装配测试补齐（下游清单已有）；冻结记录如实引用即可。

### R17-6 · P2 · GetSourceSyncCapabilities 的 Core 侧行为未写明
**位置**：§5.1 命令表末行 `:227`；validate_wire 编译为 `transport=host-local`。
**问题**：该命令携带 Core wire 名 `source_get_sync_capabilities` 但由 Host 本地聚合实现、Core 不注册；Core 侧收到该名（按 M2-C1 既有未知命令 fail-closed → UNKNOWN_COMMAND）未写明，实现者可能误在 Core 注册。
**建议**：补一句“Core 不注册该名；普通面向 Core 发送按既有未知命令语义拒绝”。

## 逐 AC 判断表

| AC | 判断 | 关键依据 |
|---|---|---|
| **AC-P1**（DDL/迁移） | **契约侧满足，可随冻结 MET** | 四表 FK 目标全部存在且主键正确（regions:228 / region_revisions:255 / sources:615 / page_bindings:694）；迁移链 1–7 校验和记录于日志且 v8 未被占用（schema.py/migrator.py 无 v8）；隔离验证 25 个 FK/UNIQUE/CHECK 负例 + DDL 中途/元数据后失败整回滚 + **真实 v7 runner** `SchemaTooNewError` 且 trace 断言零写（脚本真实 import 生产 `default_migrations`/`MigrationRunner`/`SchemaTooNewError`）；与 C-15 §1/§8"不创建两表、v8+ 追加"预留一致 |
| **AC-P2**（状态机） | **契约侧满足** | §3.1 plan 六行转移表 + §3.2 operation 十行转移表（Host durable 授权在先、Core 单事务推进、ACK 前 pending gate、fresh 授权重验不重放 CAS）；§3.3 逐崩溃点 10 行恢复表；examples 门控/ACK 中断/重放模型。真实杀进程 NOT_RUN 已诚实归 FEA-11 |
| **AC-P3**（命令面） | **满足** | 15 命令（14 Core + 1 Host-local）closed shape；34 DTO/28 错误与文档表零漂移（`validate_wire` 从文档实时编译并 assert equality）；639 形状负例含 unknown/missing/null/type/enum/integer 边界；能力探测 7 项 additive、四象限、版本面三分（per-command 2.3 / 默认 3 不变 / 文档 rev）与 M2-C1 §3.2 及 C-16 §0 先例一致；不暗用导入 API（独立确认点/durable operation） |
| **AC-P4**（CAS/原子性） | **满足** | §6.1 三类代次 + 三人工基线的比较对象与**事务内重读位置**逐行冻结；读兼容 ≤ 与 apply 等值明确分立（沿 C-15 §3.2/§6）；§6.2 单 plan 单事务原子单元 + “整批最后一项失败唯一结果”+ stale 零写精确基线（连 plan/operation 元数据也不写）；SQL 层整批回滚实证 |
| **AC-P5**（lineage） | **满足（附 R17-4/5）** | `source_revision_lineage` 四 provenance + CHECK 守卫（legacy_unverified⇔binding NULL、migrated⇔from_revision、禁自指）；captured_v7 捕获语义与 same_content-only 可达规则；交错表 7 行覆盖在途 Run/draft/edit token/candidate；未同步页不被误伤（“对本卡涉及的同步页”限定）；C-13 SC-D07/08 引用一致（origin=user 合法、统一事务、BaseRevisionId→STALE_BASE_REVISION） |
| **AC-P6**（resolve） | **满足** | §7.2 `page-rendition-v2-<sha256(...)>` 选择函数含 binding/version/entry/decoder profile；旧键 `page-rendition-{page_id}`/managed 稳定键与已发布摘要不可变、同键摘要冲突 typed 不替换——与 C-15 §4.2 冻结口径逐条一致；examples K0/Kv1/Kv2/D0/D2 对照 + profile 换键实证 |
| **AC-P7**（证据/冻结） | **随本 Review + DSH 冻结闭合** | 本报告 approved；pins 17→18 单点流程、三指纹口径（工作树 SHA-256 与 blob 双列、不混用 hash-object ID）在 FROZEN-C17 §1A 与 run_checks.py 落实；**字节链闭合**：reviewed_head 提交 blob `84fbd2b1` == 候选指纹 == 当前工作树（`cb7c5749…`），四个 EV 哈希逐一相符；21 项 protected 对象（17 冻结契约+M2-C1+schema/migrator/pins 脚本）当前字节与 baseline.json **全部相等**（哈希等价核实零改动）。`verify_pins.ps1`/`check.ps1` 本会话未复跑（见 NOT_RUN），冻结时由 DSH 执行 |
| **AC-P8**（范围） | **满足** | 交付提交 d23cf812e 共 21 文件：15 个 verification/** + 5 个文档全部在 Owner 写域；`REBASELINE_PLAN.md`/`TASK_LEDGER.md` 为 DSH 治理指针同步（ready→in_review、READY 节点清空、ledger 计数），属 Integrator 单点职责、非 Owner 越权；69d7c31e 仅回填 delivery_head 一行；无生产代码/测试/依赖/用户数据变更；隔离 `:memory:` + workspace 重定向（TEMP 未触系统） |

## 一致性与兼容判断（审查重点 2）

- **M2-C1“无增量”成立**：M2-C1 §5 目录与 §12 release boundary 均无“新命令必须登记”排他条款；C-16 v1.0/v1.1 已先例“命令面由子契约承载、M2-C1 不改”；envelope/per-command minor 机制沿用 §3.2（PrepareRun 2.12 先例）；§5.7 三码（HOST_ONLY_REQUIRED/HOST_SESSION_INVALID/CORE_SESSION_MISMATCH）category 与 C-17 §8 一致；错误为 C-17 命令投影不进全局 taxonomy，4 个 SOURCE_SYNC_* 新码随 C-17 登记。**无需 UNFREEZE。**
- **C-14**：SC-S01（三操作分命令+确认语义）、S02（current/all 范围+其他项目不误改）、S03（relink 身份保留）、S04（journal/receipt/同 operationId 幂等/确认前不可读）、S05/S06（diff+digest、PlanBody 超集覆盖 SC-S06 字段）、S07（tombstone/新 binding generation/迁移新建 revision）、S11（顺序不随重排）逐条承载；SC-S08 按其自身条款留 C-04b UNFREEZE 载体，C-17 未碰 ✓。
- **C-15/C-16**：错误三元组经生产 `SOURCE_ERROR_TABLE` 交叉核验（validate_wire 内置）；错误优先级链一致；C-15 §3.2 证据映射不建第二套规则（§7.3 明示）；`_entry_row` 现状（pixel/orientation=None）代码属实（runtime.py:857-863）；`commit_referenced_page_unit` 引用属实（library.py:1865）。
- **C-05 v1.2**：pending gate 落在 R 侧（SOURCE_ACCESS_DENIED），不扩 V、不改 reader wire——与 V/R 拆分及 C-15 §4.2 reader 跳过机制兼容。
- **pins**：Owner 未动 pins 脚本（哈希与 DSH 基线一致）；17→18 由 DSH 在 Review approved 后追加，与 Appointment/协作模式一致。

## 复跑结果与 NOT_RUN（如实）

| 项 | 状态 | 说明 |
|---|---|---|
| 本会话复跑三个 validate 脚本 / check.ps1 / verify_pins.ps1 | **NOT_RUN** | 本会话处于 plan mode，工具门禁拦截一切 Python/pwsh 进程调用（非脚本问题）。以替代核验补强：①脚本源码逐行审查，声称与实现相符（真实 import 生产迁移器、SQL/字段表从契约文档实时读取、trace 零写断言、schema 漂移 assert、生产错误表交叉核对）；②DSH 复跑日志（logs/dsh-*.log：32 passed / examples 全过 / 34 DTO+15 命令+28 错误+639 负例，均 EXIT=0）与 Owner 日志逐字节同源；③四个 EV 哈希与当前工作树逐一相等；④wire-schema SHA-256 与 DSH 运行时重算值一致（`9fed28fa…`）；⑤git blob `84fbd2b1` 三方闭合；⑥21 项 protected 哈希 vs baseline.json 全等 |
| 真实 v7→v8 升级链/杀进程矩阵/真实 IPC/lease/DPAPI/resolve 字节/全量回归 | NOT_RUN | 契约 §9 与 Handoff 已诚实登记，归 FEA-11 |

## 建议

1. **可进入 DSH 冻结**：处置 R17-1/2/3/4/6（均为文档级补注）。若 DSH 选择修改 §5/§7/§8 正文字节，按 FROZEN-C17 §1B“任何条款/SQL/DTO变动需新 head 复审”执行一轮轻量复核；若仅以冻结记录登记差异说明（R17-1/3/4/6）+ 一处正文小修（R17-2），后者需新 head。R17-5 由 FEA-11 承接，无需改契约。
2. **冻结后**：DSH 单点追加 pins 第 18 项 → 18/18 + check PASS → Task done → 派发 FEA-11 scope-r2（全新上下文）。C-17 覆盖 FEA-11 的 AC11-1…10 所需契约面（检测四路/scan 接口、diff/plan、C-15 §3.2 匹配、CAS/零写、lineage/交错、三操作、诊断出口、durable operation/崩溃点、resolve 不可变、迁移守恒），**scope-r2 前无需修订 C-17**（R17-2 除外，建议一并落定）。

**推荐下一步**：DSH 接收本报告并归档（如 `doc/reviews/FEA-11-PREREQ-1-r1.md`），处置 6 项 P2 后回填 FROZEN-C17（reviewed_head=`69d7c31ee`、Reviewer=ZCode 全新上下文）→ 冻结三指纹 → pins 18/18 → Task done → 派发 FEA-11 scope-r2。可转发指令：

```text
请 DSH 在 G:/CODEX/New Manga（main）接收本 Review 报告并归档为 doc/reviews/FEA-11-PREREQ-1-r1.md（reviewed_head=69d7c31ee60318c6f8a042c60c3f749a0ffda6a6；Reviewer=ZCode 全新上下文，未参与起草/收尾；decision=approved，P0=0/P1=0/P2=6）。处置：R17-1（STALE_BASE_REVISION retryable 与 FEA-05 投影差异，注明理由或统一）、R17-2（scope=all 超 20 book 上限边界，建议正文一句话补定）、R17-3（apply 守卫显式列未过期；§2.1 runner 措辞精确化）、R17-4（captured_v7 行 operation_id 归属一句话）、R17-6（source_get_sync_capabilities Core 不注册说明）；R17-5 由 FEA-11 承接。任何 §5/§7/§8 正文字节修改后按 FROZEN-C17 §1B 新 head 轻量复核；仅冻结记录登记差异则按"仅状态元数据差异"处理。随后：最后编辑后复算三指纹（工作树 SHA-256 与 blob 分列）、回填 FROZEN-C17 §1/§1B、单点追加 verify_pins 第 18 项 C17=FEA-C17_SOURCE_SYNC_DRAFT.md（18/18）、运行 check.ps1 记录 EXIT、Task 转 done、更新 PLAN/STATUS，再派发全新上下文执行 FEA-11 scope-r2。本会话受 plan mode 限制未复跑 Python/pwsh 脚本（已以哈希等价核验替代，见报告 NOT_RUN 节），冻结前请 DSH 复跑 validate_contract/validate_examples/validate_wire 与 check/verify_pins 并记录逐项 EXIT。无其他下一步操作。
```