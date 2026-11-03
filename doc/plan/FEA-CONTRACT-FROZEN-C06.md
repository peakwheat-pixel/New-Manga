# C06 授权面（registry + source-read grant） · 冻结记录

**契约**：`doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md`
**冻结时间**：2026-11-01
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：[Gate 阻塞口径裁定 v2](GATE-CLOSURE-RULING-2026-11-01.md)（[复核 approved](../reviews/GATE-CLOSURE-RULING-r2.md)）+ [冻结矩阵](FEA-CONTRACT_FREEZE_MATRIX.md)

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md` |
| sha256（v1.1 冻结后最终字节，verify_pins 口径） | `8faa8cd139f2e9c599dcd34063a5ac1a85941ecac287fcd693eb43d2109b2003` |
| git hash-object（v1.1 blob id） | `93a3390972cfb2ceeaa3ddd00a1b23f6b2cf804f` |
| blob 内容 sha256（LF 原始字节） | `8faa8cd139f2e9c599dcd34063a5ac1a85941ecac287fcd693eb43d2109b2003` |

**冻结语义**：条款字节自本记录起不得改动；修订须走 UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`）+ 重新独立复核 + 重新冻结。

## 1B. 冻结字节 vs 复核字节

| 项 | 值 |
|---|---|
| 最后一次独立复核 | r3 approved（FEA-GOV-6-c05-c06-r3） |
| 复核后到冻结的改动 | 条件③ 文本扩展（分担归属）+ 状态行 |
| 处置 | **已补复核**（[FEA-CONTRACT-BYTES-r1](../reviews/FEA-CONTRACT-BYTES-r1.md)：差异方向在复核建议内、无越界新增） |

| **v1.1 复核（2026-11-03）** | r7 approved（`doc/reviews/FEA-09-PREREQ-1-r7.md`） |
| **v1.1 复核字节** | `a779a7c1691b4414dcf99fd4452f837516f07accb44f9a9b263262c860fa9eb4`（工作树 SHA-256，草案 v1.1） |
| **v1.1 冻结字节** | `8faa8cd139f2e9c599dcd34063a5ac1a85941ecac287fcd693eb43d2109b2003`（仅状态行由 UNFREEZE 草案改为 FROZEN v1.1；条款字节=复核字节） |
| **v1.0 pin（历史，保留）** | `b798dd8a9b3839ac0c8e18e19dd3d515080075db53d83726e18cf76343beaef8` |
**为什么必须有这一节**：冻结条件①是「独立复核通过」，若冻结字节 ≠ 复核字节，该条件在证据上不覆盖被冻内容。本节的目的是把差异显式化，而不是掩盖它。

## 2. 冻结条件逐条核验

| # | C-06 §5 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核通过 | ✅ | r1（5 P1）→ r2（1 P1）→ r3 [approved](../reviews/FEA-GOV-6-c05-c06-r3.md)；Gate 口径修订后 [再次确认](../reviews/GATE-CLOSURE-RULING-r2.md) |
| 2 | C-01b 已冻结（SC-21/SC-22 由本单落地） | ✅ | [FEA-CONTRACT-FROZEN-C01b](FEA-CONTRACT-FROZEN-C01b.md) |
| 3 | `G-CONTRACT` **不阻塞本单** | ✅ | [裁定 v2](GATE-CLOSURE-RULING-2026-11-01.md) R-1′：Gate 保持 OPEN；本单只承载 D05 的**授权面子集** |
| 4 | wire 版本 DSH 批准（v1.1 minor） | ✅ | 裁定 R-3（仅新增命令，`ImportPages` 语义不变；兼容性依赖旧端 fail-closed） |
| 5 | `check.ps1` PASS | ✅ | PASS（3 persistent warnings） |

## 3. 依赖与后果

- **上游**：C-01b 已冻结。
- **D05 覆盖度**：C-06 只承载 D05 的**授权面**（`SourceAccessRegistry` + source-read grant + 9 条安全约束）。D05 的 lease / 重定位·同步 / 容器页映射 / 缓存边界由 C-01b、C-09 及后续契约分担——**`G-CONTRACT` 保持 OPEN** 直至这些落地。
- **下游**：Source 线实现（FEA-08/09/11/12/13）仍 blocked（Gate 未关 + 需经 C-11 建卡 + 独立 Review）。
- **实现前必须**：wire v1.1 的字节修订（`docs`/协议文档）由实现 Task 承载，且旧端 fail-closed 行为须纳入负向对照。

## 4. 不构成什么

- **不构成**实现授权。**不构成** Gate 关闭（`G-DELETE-CONTRACT` / `G-CONTRACT` 均**保持 OPEN**）。
- **不构成**远端 push 授权。

## 5. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin、条件核验、依赖与后果 | DSH |

| 2026-11-03 | **UNFREEZE v1.1 重冻**：Host 铸造型发放/四维 scope/双侧 Verify/撤销通道（[载体](../reviews/CONTRACT-UNFREEZE-2026-11-03.md)）；r7 approved；新 pin `8faa8cd139f2e9c599dcd34063a5ac1a85941ecac287fcd693eb43d2109b2003`；保留 v1.0 pin 于 §1B | DSH；FEA-09-PREREQ-1 |
