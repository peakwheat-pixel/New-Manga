# C15 Source 存储契约 · 冻结记录

**契约**：`doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md`
**冻结时间**：2026-11-03（v1.0）/ 2026-11-04（v1.1）
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：FEA-09-PREREQ-1；独立复核 r7 **approved**（[FEA-09-PREREQ-1-r7](../reviews/FEA-09-PREREQ-1-r7.md)，reviewed_head `220979ba81f37e857f241049535caef7246c97b1`）；冻结自草案 v5

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` |
| 冻结版本 | **v1.1**（2026-11-04 UNFREEZE 重冻；v1.0 历史） |
| sha256（v1.1 冻结后最终字节，verify_pins 口径） | `d8c0a3bcfc21229bff8f6feb6853866cdea7dc902b76f1ae45b0d374ce6579d6` |
| git hash-object（v1.1 blob id） | `a0286bac06aa89587a6a7cbcf08461aae8add865` |
| blob 内容 sha256（LF 原始字节） | `6da686178f4d2e739906938e2bbcfbb57c9d59f3836e17c80c8764b477cd91bc` |

**冻结语义**：条款字节自本记录起不得改动；修订须走 UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`）+ 重新独立复核 + 重新冻结。

## 1A. pin 口径

- 工作树原始字节 SHA-256 = `Get-FileHash -Algorithm SHA256`（`tools/governance/verify_pins.ps1` 使用口径）；
- blob 口径 = `git hash-object` 得到 blob id，`git cat-file blob <id>` 原始字节 SHA-256；
- 三口径在本轮复核字节与冻结字节上均一致（仅换行/LF 策略不改变内容时亦应一致；不一致须在 §1B 说明）。

## 1B. 冻结字节 vs 复核字节

| 项 | 值 |
|---|---|
| r7 复核字节（草案 v5，工作树 SHA-256） | `fa912075f487701083eab662b7f89b9e8d8897024c9a832d9812ce5c87802090` |
| 冻结字节（工作树 SHA-256） | `6da686178f4d2e739906938e2bbcfbb57c9d59f3836e17c80c8764b477cd91bc` |
| 差异 | **仅状态行**（草案 v5 → FROZEN v1.0）与冻结记录链接；**条款字节 = 复核字节** |
| 处置 | 符合冻结纪律（最后元数据编辑在复核后、冻结提交不含条款修改） |

## 2. 冻结条件逐条核验

| # | 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | C-05 v1.1/C-06 v1.1 UNFREEZE 与 C-15/C-16 同批独立复核 approved（P0/P1=0） | ✅ | [r7](../reviews/FEA-09-PREREQ-1-r7.md) |
| 2 | v7 DDL/迁移/回退/旧写者门禁内存实测 | ✅ | `verification/FEA-09-PREREQ-1/logs/ddl-validation.log` |
| 3 | `check.ps1` PASS、`verify_pins.ps1` **17/17** | ✅ | `verification/FEA-09-PREREQ-1/logs/check.log`、`pins.log` |
| 4 | 冻结记录含 §1A pin 口径与 §1B 复核字节差异 | ✅ | 本记录 |

## 3. 依赖与后果

- **上游**：C-01b/C-05 v1.1/C-06 v1.1/C-14 已冻结；G-CONTRACT 关闭裁定 §3.3 的 DDL 前置由本契约落地。
- **下游**：FEA-09（depends_on 本 Task）只实施本契约冻结的精确 DDL；FEA-11 的 source_sync_plans/source_operations 预留 v8+。
- **不构成**：实现授权、DB 迁移已执行、产品 AC 已达成。

## 4. 不构成什么

不构成实现授权；不冻结 FEA-11/12/13 表结构；不改变 C-01b/C-05/C-06/C-14 已冻结语义（C-05/C-06 的 v1.1 由独立 UNFREEZE 载体承载）；不构成远端 push 授权。

## 5. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-03 | 建立：C-15 v1.0 冻结（来自草案 v5），记录三种指纹、条件核验与边界 | DSH；FEA-09-PREREQ-1；r7 approved |
## 6. v1.1 UNFREEZE 重冻（2026-11-04）

| 项 | 值 |
|---|---|
| 载体 | `doc/reviews/CONTRACT-UNFREEZE-2026-11-04.md` |
| 语义修订提交（复核字节） | `ed570681b57e1343cb8c477f5dd7d23200a2dab4` + 补正 `a9276fbaeeb7dd9fa85569910dfe314ee45bbff0` |
| 已提交字节独立复核 | ZCode `sess_1517188b…`（P1×1/P2×1）→ 补正 → ZCode `sess_f155bf21…` **approved P0/P1/P2=0** |
| 复核字节 sha256 | `6b93a3683c85771c897ee56531287f8e16f284020d5af7185fbf14e4774c02f9` |
| 冻结字节 sha256 | `d8c0a3bcfc21229bff8f6feb6853866cdea7dc902b76f1ae45b0d374ce6579d6`（**仅状态行**差异） |
| 历史 pin（保留） | v1.0 `6da686178f4d…` |
| 修订内容 | 正尺寸迁移基线、union 守恒断言、V 行可观察、§4.4 只读投影、reader 恢复算法与 M2-C1 §6.3 offset 引用 |
