# C16 Source 读取与导入 wire 协议 · 冻结记录

**契约**：`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`
**冻结时间**：2026-11-03（v1.0）/ 2026-11-04（v1.1）
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：FEA-09-PREREQ-1；独立复核 r7 **approved**（[FEA-09-PREREQ-1-r7](../reviews/FEA-09-PREREQ-1-r7.md)，reviewed_head `220979ba81f37e857f241049535caef7246c97b1`）；冻结自草案 v7

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` |
| 冻结版本 | **v1.1**（2026-11-04 UNFREEZE 重冻；v1.0 历史） |
| sha256（v1.1 冻结后最终字节，verify_pins 口径） | `0b9511a55ea15fafdc2de7d33fb204e5c7e2cf2efed69977ee6dd092f22e5905` |
| git hash-object（v1.1 blob id） | `bd36fc19c0c54df469c7dfe68ee824f6af531b17` |
| blob 内容 sha256（LF 原始字节） | `6e7f8d3d7a81c3588a8db1878579e4b1f4fd5330e4bbbab54e5ff5165afa1b0f` |

**冻结语义**：条款字节自本记录起不得改动；修订须走 UNFREEZE 载体 + 重新独立复核 + 重新冻结。

## 1A. pin 口径

- 工作树原始字节 SHA-256（`verify_pins.ps1` 口径）、`git hash-object` blob id、`git cat-file blob` 原始字节 SHA-256 三口径；
- 上述三者在最终冻结字节上一致；历史 pin 与修正记录不得静默替换。

## 1B. 冻结字节 vs 复核字节

| 项 | 值 |
|---|---|
| r7 复核字节（草案 v7，工作树 SHA-256） | `154c5a5725abf1b00709ac37b65e09718035229a544c761d0826b8b834617cc8` |
| 冻结字节（工作树 SHA-256） | `6e7f8d3d7a81c3588a8db1878579e4b1f4fd5330e4bbbab54e5ff5165afa1b0f` |
| 差异 | **仅状态行**（草案 v7 → FROZEN v1.0）与冻结记录链接；**条款字节 = 复核字节** |
| 处置 | 符合冻结纪律（最后元数据编辑在复核后、冻结提交不含条款修改） |

## 2. 冻结条件逐条核验

| # | 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | C-05 v1.1/C-06 v1.1 UNFREEZE 与 C-15/C-16 同批独立复核 approved（P0/P1=0） | ✅ | [r7](../reviews/FEA-09-PREREQ-1-r7.md) |
| 2 | 方向/四维 scope/撤销 ACK/密码短期引用/WireLog 脱敏/异步状态机条款经独立复核 | ✅ | r7 报告与 C-06 v1.1 载体 |
| 3 | `check.ps1` PASS、`verify_pins.ps1` **17/17** | ✅ | `verification/FEA-09-PREREQ-1/logs/check.log`、`pins.log` |
| 4 | 冻结记录含 §1A pin 口径与 §1B 复核字节差异 | ✅ | 本记录 |

## 3. 依赖与后果

- **上游**：C-06 v1.1（UNFREEZE）是本契约方向/Verify 归属/撤销通道的前提；C-15 v1.0 是存储字段对齐前提。
- **下游**：FEA-09 实现 source-read/导入运行时；FEA-09-UI-1 消费 UI 命令；C-07 冻结字节不变（FEA-09 不新增 IHostController）。
- **不构成**：实现授权、运行时协议已实现、产品 AC 已达成。

## 4. 不构成什么

不构成实现授权；不冻结 UI/FEA-11/12/13；不改变 Core `PROTOCOL_MINOR`；不构成 push 授权。

## 5. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-03 | 建立：C-16 v1.0 冻结（来自草案 v7），记录三种指纹、条件核验与边界 | DSH；FEA-09-PREREQ-1；r7 approved |
## 6. v1.1 UNFREEZE 重冻（2026-11-04）

| 项 | 值 |
|---|---|
| 载体 | `doc/reviews/CONTRACT-UNFREEZE-2026-11-04.md` |
| 语义修订提交（复核字节） | `ed570681b57e1343cb8c477f5dd7d23200a2dab4` + 补正 `a9276fbaeeb7dd9fa85569910dfe314ee45bbff0` |
| 已提交字节独立复核 | ZCode `sess_1517188b…`（首次 P1×1/P2×1）→ 补正 → ZCode `sess_f155bf21…` **approved P0/P1/P2=0** |
| 复核字节 sha256 | `b0adc6538a33d4e64bcc290e297ed1484b2d58aa66eb03cedf346b35cf01b0ee` |
| 冻结字节 sha256 | `0b9511a55ea15fafdc2de7d33fb204e5c7e2cf2efed69977ee6dd092f22e5905`（**仅状态行**差异） |
| 历史 pin（保留） | v1.0 `6e7f8d3d7a81…` |
| 修订内容 | `source.resolve-secret/1` 能力、resolve 加密源 fresh-grant 协议（wire 字节不变）、错误码复用 |
