---
id: FEA-09-PREREQ-1
title: Source 存储与读取协议契约冻结（C-15 DDL/迁移 + C-16 source-read wire v1.1）
kind: design
governance_version: 3
status: ready
approval: DSH 范围冻结 2026-11-03（依据 FEA-09 scope-r1 changes_requested R1-001/R1-002/R1-006/R1-008/R1-009 与 G-CONTRACT 关闭裁定 §3.3；契约字节须独立复核 approved 后才可冻结）
suggested_owner: dsh
owner: DSH（Lead / Architect / Integrator；契约起草者）
reviewer: 契约独立复核待 Appointment（候选 Codex 独立会话；不得由起草者同一会话/实例自审；复核报告 doc/reviews/FEA-09-PREREQ-1-*.md）
depends_on:
  - FEA-01-FREEZE-1
  - FEA-08
base_commit: 6e274dd94c5b64d8fbc3f9d578363d3c502a2b68
branch: main
worktree: G:\CODEX\New Manga
integration_commit: null
delivery_head: 未开始
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-09-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-09-PREREQ-1.md
  - doc/tasks/FEA-09.md
  - doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md
  - doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md
  - doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md
  - doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C05.md
  - doc/plan/FEA-CONTRACT-FROZEN-C06.md
  - doc/plan/FEA-CONTRACT-FROZEN-C15.md
  - doc/plan/FEA-CONTRACT-FROZEN-C16.md
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
  - tools/governance/verify_pins.ps1
  - doc/reviews/FEA-09-PREREQ-1-*.md
  - doc/reviews/FEA-C15-*.md
  - doc/reviews/FEA-C16-*.md
  - doc/reviews/CONTRACT-UNFREEZE-*.md
  - doc/handoffs/FEA-09-PREREQ-1-*.md
  - verification/FEA-09-PREREQ-1/**
out_of_scope:
  - src/**、apps/**、tests/**（本 Task 零生产代码改动，不实现 FEA-09 运行时行为）
  - 既有冻结契约字节修改（C-01b/C-06/C-07/C-14 等）；必要更新只走 CONTRACT-UNFREEZE 载体（DSH 执行）
  - requirements*.txt、packaging/**、新增 NuGet/Python 依赖
  - 真实用户数据/真实外部卷/AppData 生产根/回收站或原文件操作
  - FEA-09 范围复审（scope-r2）本身；本 Task 只交付其前置
  - push
---

# FEA-09-PREREQ-1：Source 存储与读取协议契约冻结

> 来源：`doc/reviews/FEA-09-scope-r1.md`（Codex，`changes_requested`，P0=0/P1=9/P2=4）的 R1-001/R1-002/R1-006/R1-008/R1-009 与 §5.5 前置顺序；[G-CONTRACT 关闭裁定](../plan/GATE-CONTRACT-CLOSURE-2026-11-01.md) §3.3；C-14 §4「四表 DDL 留给后续存储契约」；C-06 §2.3（Host 授权面命令）。
> 本 Task 是 FEA-09 的**硬前置**：契约冻结且独立复核通过前，FEA-09 不得 `ready`/`in_progress`。

## 事实与边界

- `G-CONTRACT` **CLOSED（2026-11-01）**只代表 D05 契约语义覆盖完成；**Source 表 DDL 仍未冻结**，是任何 Source 生产实现的前置（Gate 关闭裁定 §3.3；AD-003 `:117` 列 7 张表；C-14 `:197` 明示本契约不定义 DDL）。
- C-06 **已冻结**：`SourceAccessRegistry` 为 **Host 私有、持久化、不写 Core DB**；新增 5 条命令（`RegisterSourceRoot` / `ListSourceRoots` / `RevokeSourceRoot` / `RequestSourceRead` / `VerifySourceRead`）按 wire v1.1 minor；旧 `ImportPages` grant 语义不变；备份包内加密、包外不得泄露。
- 现有 Core Schema 迁移链 `v1–v6`（`src/infrastructure/sqlite/schema.py`、`migrator.py`）；**v7 是可预留的下一个版本，但版本号与表结构由 C-15 正式冻结，本卡不预先代替裁定。**
- C-05 页可见性谓词已冻结；C-01b SC-19 要求旧二进制遇新 Schema 必须拒写（`migrator.py` 已有 `SchemaTooNewError`）。
- C-09（删除/备份/迁移）仍 OPEN，与本 Task 的备份衔接只做**交接边界**，不实现备份产品流程（FEA-13）。

## 交付物

1. `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md`：Source 存储契约草案（DDL/迁移/完整性-可见性衔接/跨存储次序）。
2. `doc/plan/FEA-CONTRACT-FROZEN-C15.md`：C-15 冻结记录（冻结字节 SHA-256、条件逐条、边界、不构成什么）。
3. `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`：source-read wire v1.1 协议契约草案。
4. `doc/plan/FEA-CONTRACT-FROZEN-C16.md`：C-16 冻结记录。
5. `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`：追加 C-15/C-16 两行，并更新 C-05/C-06 行（UNFREEZE 重冻注记）；其它行保持原字节。
6. `tools/governance/verify_pins.ps1`：扩展 map 覆盖 C-15/C-16，冻结缺失记录/pin 不匹配失败（预期冻结全集 **17 项**）；任务/证据登记该治理动作。
6. `doc/reviews/FEA-09-PREREQ-1-*.md` / `FEA-C15-*.md` / `FEA-C16-*.md`：独立复核报告（reviewer 只写报告）。
7. `doc/handoffs/FEA-09-PREREQ-1-*.md`：交付 Handoff。
8. `verification/FEA-09-PREREQ-1/**`：只读核验证据（check/vpins 原始日志、冻结 hash、schema 静态对照、路径存在性、零 src/apps diff）。

## 内容要求（C-15）

- **表范围**：`sources`、`source_locations`、`source_versions`、`source_entries`、`page_bindings`，以及 `source_sync_plans`、`source_operations` 的「本轮创建 vs 仅预留」结论（AD-003 `:117` 七表；C-14 SC-S09…S13/SC-S06 只给语义与不变量）。
- **逐表冻结**：列/类型/NOT NULL/默认/CHECK/唯一键/索引/外键、迁移版本与迁移 SQL 边界、旧库升级路径、旧二进制拒写、回滚/降级口径（SC-19/SC-37）。
- **完整性/可见性衔接**：referenced 页如何进入 C-05 可见性谓词；`integrity=incomplete/complete` 与 binding/version 状态的关系；半写行不可见但可恢复（提案 `:893`、`:1026–:1028`）；合法 NULL managed ref 不得被误判为 managed 崩溃半写。
- **五读路径**：`existing_source_hashes`、`max_source_order`、`get_page`、`list_pages`、`handle_resolve_page_resource` + reader projection；迁移守恒判据（旧页 ID/顺序/计数/资源/人工数据/Lock）。
- **Host Registry 实现约束**（C-06 落地条款，可由 C-15 附录或 C-16 承接，但须唯一归属）：`<HostOptions.DataRoot>/host/source-access/registry.v1.dat`；带格式版本 UTF-8 JSON + Windows DPAPI CurrentUser；不持久化短期 grant/session key/lease/密码；`generation`/撤销状态/根身份持久化；重启重验根身份并建新 session，旧 grant 不恢复；同一数据根专用跨进程锁（锁冲突拒绝第二写者）；同目录临时文件 + flush + 原子替换；损坏/解密失败/不确定恢复 fail-closed；持久化失败拒绝签发；备份导出接口与加密要求交 FEA-13，跨机恢复不得自动继承授权。
- **跨存储发布/失败恢复次序**：Host Registry 与 Core binding 之间无跨存储事务；必须冻结「谁先持久化、失败如何回滚/重试」的次序，禁止「Core 已发布 complete binding、Host 授权未可靠持久化」的假成功；给出可执行负测口径。
- 明确与 C-01b/C-05/C-06/C-14 的接口；**不得复写**已冻结语义，只补 DDL/次序/衔接缺口。

## 内容要求（C-16）

- **wire v1.1 additive**：C-06 的 5 条命令；信封与 minor 策略、错误码（至少 `SOURCE_ACCESS_DENIED`）、旧 Host/旧 Core 的 fail-closed 行为（`PROTOCOL_VERSION_UNSUPPORTED` / `CORE_PROTOCOL_MINOR_TOO_OLD`）；不改 major。
- **读取面**：`scope{sourceId, version, entry, rendition}` + `budget{maxBytes, maxDecodeBytes}`；**禁止** `paths[]`；`scope.entry` 与 `EntryId` 的解析/对齐规则（与 C-14 SC-S09 的 `EntryId` 对齐）。
- **密码与加密**：密码只走**短期安全引用**，不进入普通 task/snapshot/Registry/receipt/异常/wire/evidence 日志及其可逆编码（含 `WireLog` UTF-8 hex 路径）；AES ZIP 本轮按 typed unsupported 处理并登记为产品限制；支持的加密子格式限定为 ZipCrypto ZIP/CBZ 与 PDFium 可解密 PDF；不得以测试依赖 pyzipper 冒充生产 AES 能力。
- **plan/receipt/取消**：确认前源变化必须拒绝或更新预览；提交单元与计数口径（文件/容器/页/项目）冻结；已提交保留、未提交不可见；丢 ACK/重试幂等、receipt 可重复查询；Host 发起取消与 Core 实际接受取消分别记录；mock/注入证据不得升级为 Windows 原生取消 PASS。
- **协议载体与冻结字节**：新增 C-16 **新文档**，不修改任何既有冻结文档字节；若 C-07 API inventory 或其它冻结文档需登记新命令，**明确是否必需**并提供 `doc/reviews/CONTRACT-UNFREEZE-<DATE>.md` 载体由 DSH 集成（记录精确路径、理由、影响）；不得用 `doc/contracts/**` 通配授权代替该动作。
- **兼容边界**：旧 `ImportPages` 一次性 grant 与旧命令语义零变化；旧读取端遇未知命令/码保持 fail-closed（作为兼容性依赖显式登记）。

## Acceptance Criteria

- [ ] **AC-1（C-15 冻结）**：C-15 草案完成并经独立复核 `approved`（P0/P1=0）；冻结记录含冻结字节 SHA-256、条件逐条、边界；覆盖 §内容要求（C-15）全部条目（7 表归属、逐表 DDL、迁移 v 版本、完整性与 C-05 衔接、五读路径、Host Registry 约束归属、跨存储次序）。
- [ ] **AC-2（C-16 冻结）**：C-16 草案完成并经独立复核 `approved`（P0/P1=0）；冻结记录完整；覆盖 5 命令、scope/预算、密码短期引用、plan/receipt/取消、旧语义兼容、协议载体与 UNFREEZE 结论。
- [ ] **AC-3（跨存储一致性可判定）**：冻结文本给出 Host/Core 失败恢复次序与可执行负测口径（含「Core complete / Host 未持久化」反例、Host 持久化失败拒绝签发、Registry 损坏 fail-closed）。
- [ ] **AC-4（零生产改动）**：`git diff --name-only` 仅限 allowed_paths；无 `src/**`、`apps/**`、`tests/**` 改动；无依赖/打包变更。
- [ ] **AC-5（治理同步）**：freeze matrix 追加 C-15/C-16 行并更新 C-05/C-06；STATUS/PLAN/checkpoint/`task_ledger.py --write` 同步；FEA-09 的 `depends_on`/`allowed_paths`/AC 引用真实 Task ID；Handoff 记录契约 pin 与复核报告；`verify_pins.ps1` 扩展覆盖 17 项且缺记录/pin 不匹配失败。
- [ ] **AC-6（独立复核纪律）**：复核者未参与起草；报告记录 reviewer 身份/来源、reviewed_head、被审字节 hash、未覆盖项；P0/P1 未解决不得判 approved；不得在同一会话自审。
- [ ] **AC-7（门禁）**：`check.ps1` PASS（既有 3 warnings 允许）、`verify_pins.ps1` **17/17**（扩展 checker 覆盖 C-15/C-16、缺记录失败）、旧 FEA-06 四 PNG 不变、未 push；以上命令行/EXIT/环境逐次入 `verification/FEA-09-PREREQ-1/`。

## 允许修改范围

见 frontmatter `allowed_paths`；契约与冻结记录只允许写入上述精确路径。**C-15/C-16 冻结后其字节不得再改，修订须 UNFREEZE 载体 + 重新独立复核 + 重新冻结。**

## 禁止范围

见 frontmatter `out_of_scope`。特别地：不得以「先写代码再补契约」倒置顺序；不得在 C-15/C-16 中复写或改写既有冻结语义；不得替 FEA-09 实现做范围裁决；不得修改 `doc/contracts/**` 冻结字节。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC-4 零生产改动 | `git diff --name-only 6e274dd94..<head>` 对照 allowed_paths | 仓库根 `G:\CODEX\New Manga` | NOT_RUN（planned） | `verification/FEA-09-PREREQ-1/logs/` |
| AC-5/AC-7 治理门禁 | `pwsh -NoProfile -File tools\governance\check.ps1`；`pwsh -NoProfile -File tools\governance\verify_pins.ps1` | 同上 | NOT_RUN（planned） | 同上 |
| AC-1/AC-2 契约独立复核 | 派发独立上下文 reviewer 只读被审字节；报告入库 | reviewer 未参与起草 | NOT_RUN（planned） | `doc/reviews/FEA-09-PREREQ-1-*.md` |
| AC-3 次序负测口径 | 静态审阅冻结文本 + （若可）隔离参考实现验证 | 不触碰生产库 | NOT_RUN（planned） | 冻结记录/证据日志 |
| 冻结 hash 复算 | 对冻结后文件 `Get-FileHash`/`git hash-object` 与记录比对 | 同上 | NOT_RUN（planned） | `verification/FEA-09-PREREQ-1/frozen-hashes.log` |

## 依赖、风险与阻塞

- `depends_on`：`FEA-01-FREEZE-1`（done）、`FEA-08`（done）。二者为已存在、已集成 Task。
- **硬前置关系**：FEA-09 `depends_on` 本 Task；本 Task 未 done 前 FEA-09 不得 ready/in_progress。
- 风险：①DDL 设计若与未来 FEA-11/12/13 需求冲突，将造成迁移返工——C-15 必须明确「本轮创建 vs 预留」；②Host 私有无跨存储事务，次序定义不清会产生假成功；③DPAPI 在测试环境的隔离注入方式需在契约中给出可测口径；④C-16 若与既有 C-07/C-01b 字节冲突，必须先 UNFREEZE 而不是改写历史；⑤本 Task 属契约工作，不产生产品行为证据，不得把文档完成表述为 Source 能力已实现。
- 阻塞解除标准：C-15/C-16 双冻结 + 独立复核 approved + 门禁 PASS → 本 Task 可 done；随后 FEA-09 提交 scope-r2。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。

## Canonical Evidence

进入 `in_review` 前逐项填写。当前无证据（`proposed/ready` 阶段不预填假 pin）。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | `G:\CODEX\New Manga`（main） | NOT_APPLICABLE | - | - | 复用主工作树，无新建 worktree |
| temp | 无 | NOT_APPLICABLE | - | - | 本 Task 无临时数据 |
| agent-output | `G:\CODEX\New Manga.workspace\FEA-09-PREREQ-1\` | PRESERVE_REFERENCED | 原地（workspace） | 派发/复核原始日志 | 非 Canonical；需要时登记 |

## Closeout Record

- Closeout date / DSH：未开始。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 未关闭项及保留原因：未开始。
- 当前指针清理：未开始。

## 变更记录

| 日期 | 变更 | 依据 |
|---|---|---|
| 2026-11-03 | 建立并冻结范围：C-15（Source 存储 DDL/迁移/跨存储次序）+ C-16（source-read wire v1.1）；owner=DSH，状态 ready | FEA-09 scope-r1 R1-001/R1-002/R1-006/R1-008/R1-009；G-CONTRACT 关闭裁定 §3.3；C-06 冻结记录 §3 |
| 2026-11-03 | 按契约独立复核 r1（changes_requested，P0=0/P1=11/P2=2）扩域：新增 **C-05 v1.1 / C-06 v1.1 UNFREEZE 载体**（`doc/reviews/CONTRACT-UNFREEZE-2026-11-03.md`）与对应冻结记录/矩阵更新；写域增加 C-05/C-06 草案与冻结记录；C-15/C-16 返修 | `doc/reviews/FEA-09-PREREQ-1-r1.md` R1-001/R1-002 等；C-05/C-06 冻结记录「修订须 UNFREEZE」纪律 |
| 2026-11-03 | 按契约复核 r2/r3 返修：C-15 v4/C-16 v4 + C-05/C-06 v1.1；扩展写域至 `tools/governance/verify_pins.ps1`（17 项 pin 覆盖）与 freeze matrix 的 C-05/C-06 重冻注记；r1/r2/r3 报告归档供原文闭环 | `doc/reviews/FEA-09-PREREQ-1-r2.md`、`-r3.md` |
| 2026-11-03 | 按契约复核 r4 收口：C-15/C-16 定稿 **v5**（迁移断言限定、PDF 重复 occurrence 禁用位置锚定、receipt 示例/计数统一）；门禁统一 **17/17**；FEA-09 AC-7 登记 `SOURCE_PROJECT_MISMATCH` 负测；清理 trailing whitespace | `doc/reviews/FEA-09-PREREQ-1-r4.md` R4-001…R4-004 |
| 2026-11-03 | 按契约复核 r5 收口：C-16 **v6**（accepted 取消示例、`planned_pages` 定义与 remaining 公式、C-15 v5 引用统一）；C-15 v5 不变 | `doc/reviews/FEA-09-PREREQ-1-r5.md` R5-001/R5-002 |
| 2026-11-03 | 按契约复核 r6 收口：C-16 **v7**（按页 planned_pages/skipped_pages、整源跳过与部分已引用实例、四类示例完整字段） | `doc/reviews/FEA-09-PREREQ-1-r6.md` R6-001 |
