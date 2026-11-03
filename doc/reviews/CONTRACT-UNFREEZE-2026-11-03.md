# CONTRACT-UNFREEZE-2026-11-03 — C-05 / C-06 v1.1

状态：**UNFREEZE 草案 / 待独立复核后重冻**
日期：2026-11-03
发起人：DSH（Lead / Architect / Integrator）
依据：C-05/C-06 冻结记录自身纪律（「修订须走 UNFREEZE 载体 + 重新独立复核 + 重新冻结」）；[FEA-09-PREREQ-1 契约复核 r1](../reviews/FEA-09-PREREQ-1-r1.md)（changes_requested；R1-001 C-05 冲突、R1-002/R1-003 C-06 方向/四维 scope/即时撤销）；[FEA-09 scope-r1](../reviews/FEA-09-scope-r1.md)（Source 生产实现前置）；AGENTS.md（DSH 在上下文独立复核下可冻结/重冻）。

**本载体不构成实现授权，也不改变任何冻结前已交付的历史证据；它只登记本轮对两份冻结契约的最小语义扩展。**

## 1. 变更对象

| 契约 | 当前冻结版本 | 旧 pin（sha256，工作树字节） | 目标版本 | 新 pin |
|---|---|---|---|---|
| C-05 页可见性谓词 | v1.0（2026-11-01） | `b34db88768790a982c00d6b78a9649c24047e15d2ba86e3c0bf6a5a293ec8d25` | **v1.1** | 重冻后写入 FROZEN-C05 §1，并保留旧 pin 于历史 |
| C-06 授权面 | v1.0（2026-11-01） | `b798dd8a9b3839ac0c8e18e19dd3d515080075db53d83726e18cf76343beaef8` | **v1.1** | 重冻后写入 FROZEN-C06 §1，并保留旧 pin 于历史 |

## 2. 变更内容（精确范围）

### 2.1 C-05 v1.1

- 新增 **§3.1 模式分派与 referenced 页分支**：总可见性按 `source_mode` 分派 —— `V = (managed ∧ V_artifact) ∨ (referenced ∧ V_ref)`；`V_artifact`（原 P1–P5）**字节/语义均不变且仅限 managed**；`V_ref` 使用 `integrity_status='complete'` + healthy `page_bindings` + `verified_digest` 一致，不使用 artifact/revision。referenced 页即使存在 valid artifact 也不得经 artifact 分支可见（防止绕过完整性分支）。
- 新增 **§3.2 三谓词拆分**：`is_complete_page`（数据完整性）、`V`（数据库可见性）、`R`（当前可读性/资源授权）分开；读取层不得把 `V` 当 `R`。
- §2 数据模型事实追加 `pages.source_mode/integrity_status`（C-15 v7 列）。
- §3.2 失败语义追加 referenced 行（incomplete/binding 非 healthy → 不可见；授权撤销/失联 → `V` 仍真但读取 typed 失败）。
- 变更记录追加 v1.1 行。

**不改**：managed/derived 分支 P1–P5、`VISIBLE_TYPES`、`S(p,t)` active runs 语义、C-05 冻结条件（仍要求独立复核 + check PASS）。

### 2.2 C-06 v1.1

- **§2.2**：明确现有传输无 Core→Host RPC；Host 在 dispatch 前按 Registry **铸造** source-read grant（语义申请方仍为 Core，授予方唯一为 Host）；grant 字段扩为四维 `scope{sourceId, version, entry[], rendition}` + `entries[{entryKey, entryId?, locator, ordinal, path, facts}]` + `budget{maxBytes,maxDecodeBytes,maxEntries}` + `secretRef` + `signingKey/signature`；新增「撤销/失联」行：Host 持久化 generation+1 → 推送 `RevokeSourceReadGrant` → Core 立即废止 + 下一提交边界停止 + ACK → Host 收 ACK 才返回成功；Core EOF/transport 失败 → 全部 grant 失效。
- **§2.3**：`RequestSourceRead` 明确为 Host 铸造型（非 Core→Host wire）；`VerifySourceRead` 拆为 Host 铸造时 scope→授权根解析 + Core 读取前/commit 前本地校验；**新增** `RevokeSourceReadGrant`（Host→Core，`{registryId, generation, grantIds[]}` → ACK）。
- **§3**：新增安全约束 10（即时撤销/失联 fail-closed，不得以 TTL 代替）与 11（commit 前确认）。
- 变更记录追加 v1.1 行。

**不改**：`SourceAccessRegistry` 归属/持久化原则、旧 `ImportPages` grant 语义、9 条既有安全约束、失败码词表（新增命令错误仍用既有 `SOURCE_*` 词汇）。

## 3. 影响分析

- **下游消费者**：C-05 被导出（FEA-14-EXPORT）与删除预览（C-04b）引用；新分支只增加 referenced 页判定，managed/derived 行为不变。C-06 被 FEA-09/11/12 引用；新命令 additive，不改旧命令/旧 grant 语义。
- **数据/迁移**：无数据迁移；C-05/C-06 是语义契约，不产生 Schema 变化。
- **安全**：新增撤销通道与四维 scope 是收紧方向；Host 仍为唯一授权方；密码/路径/能力约束见 C-15/C-16。
- **旧代码**：`ImportPages`/`ImportSource` 路径零变化；旧 Core 无 `source.read/1` 时 Host 按操作拒绝（C-16 §0），不影响既有导入。
- **证据**：C-05/C-06 的原 v1.0 历史 pin 与复核报告保留原字节；本轮以 UNFREEZE + 重新独立复核取代静默改字节。

## 4. 复核与重冻流程

1. 本载体 + C-05 v1.1 + C-06 v1.1 + C-15 v5 / C-16 v7（最终草案版本）同批交**独立上下文**只读复核（未参与起草；reviewer 不得参与实现）。
2. 复核 `approved` 且 P0/P1=0 后：按 FROZEN 记录纪律，在**冻结提交前**完成最后元数据编辑（状态行改为 FROZEN v1.1），再计算新 pin（工作树字节 + `git cat-file` LF 双口径）。
3. 更新 `FEA-CONTRACT-FROZEN-C05.md` / `FEA-CONTRACT-FROZEN-C06.md`：§1 新 pin、§1B「v1.1 复核字节」、§5 变更记录；旧 pin 保留在历史行。`verify_pins.ps1` 自动读取新 pin（不静默替换历史）。
4. 更新 `FEA-CONTRACT_FREEZE_MATRIX.md` 的 C-05/C-06 版本注记；C-15/C-16 冻结记录同批建立。
5. 复核**不通过**：回退本次字节到 v1.0（git 历史可复现），载体状态改 `rejected` 并保留报告；不得以实现解释补齐后直接冻结。

## 5. 不构成什么

- 不构成实现授权；不证明任何 AC 达成；不改变 C-01b/C-14 与其它冻结契约字节。
- 不覆盖旧 `ImportPages` 语义；不授权 UI/删除/备份实现。
- 不代表 C-15/C-16 已冻结（二者同批复核通过后才各自建立冻结记录）。

## 6. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-03 | 建立 UNFREEZE 载体：C-05 v1.1（referenced 可见性 + 三谓词拆分）、C-06 v1.1（Host 铸造型发放/四维 scope/双侧 Verify/撤销通道）；复核+重冻流程与回退 | DSH；FEA-09-PREREQ-1 契约复核 r1 R1-001/R1-002/R1-003 |
| 2026-11-03 | 处置复核 r2：C-05 改为**模式分派**（managed V 语义保留；referenced 不得经 artifact 绕过）；C-06 修正旧 revision 可见性引用；r1/r2 报告按原字节归档为 `doc/reviews/FEA-09-PREREQ-1-r1.md` / `-r2.md`（供 r3 原文闭环） | `doc/reviews/FEA-09-PREREQ-1-r2.md` R2-001/R2-008/R2-009 |
| 2026-11-03 | 处置复核 r3：同步 C-15/C-16 最终版本引用；修正失败语义章节定位；明确冻结前扩展 `verify_pins.ps1` 覆盖 17 项（不由本载体替代检查） | `doc/reviews/FEA-09-PREREQ-1-r3.md` R3-005/§8 |
| 2026-11-03 | 处置复核 r4：C-15/C-16 定稿版本 v5；冻结前门禁统一 17/17；Task AC-7 登记 17 项与缺记录失败 | `doc/reviews/FEA-09-PREREQ-1-r4.md` R4-004 |
