# C16 Source 读取与导入 wire 协议 · 冻结记录

**契约**：`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`
**冻结时间**：2026-11-03（v1.0）/ 2026-11-04（v1.1）/ 2026-11-06（v1.3）/ 2026-11-07（v1.4）
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：FEA-09-PREREQ-1；独立复核 r7 **approved**（[FEA-09-PREREQ-1-r7](../reviews/FEA-09-PREREQ-1-r7.md)，reviewed_head `220979ba81f37e857f241049535caef7246c97b1`）；冻结自草案 v7

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` |
| 冻结版本 | **v1.4**（2026-11-07 UNFREEZE 重冻；v1.0 2026-11-03 / v1.1 2026-11-04 / v1.3 2026-11-06 历史） |
| sha256（v1.4 冻结后最终字节，verify_pins 口径） | `ad25fb3c89bb1749552c3de988369ae93b5e9e7f563ce2530a5d4c65ba2ad8dc` |
| git hash-object（v1.4 blob id） | `b9be0acfa232154510d8453133ef8803b6b8fbbe` |
| blob 内容 sha256（LF 原始字节） | `ad25fb3c89bb1749552c3de988369ae93b5e9e7f563ce2530a5d4c65ba2ad8dc` |

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
| v1.1 冻结字节（历史，保留） | `0b9511a55ea15fafdc2de7d33fb204e5c7e2cf2efed69977ee6dd092f22e5905` |
| v1.3 复核字节（工作树 SHA-256） | `7c355ccb8f826879e34252750c642c8a7b5c138cd5be5b089a7a518bb56519e5`（= v1.3 冻结字节；本次先冻结最终字节再复核，无「复核后改状态行」差异） |
| v1.4 复核字节（工作树 SHA-256） | `ad25fb3c89bb1749552c3de988369ae93b5e9e7f563ce2530a5d4c65ba2ad8dc`（= v1.4 冻结字节；r1 changes_requested（P1×2/P2×4/P3×9）→ 处置 → r2 approved（session `e032ed9a-…`；reviewed_head `a0bafc89e`），见 §8） |

## 2. 冻结条件逐条核验

| # | 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | C-05 v1.1/C-06 v1.1 UNFREEZE 与 C-15/C-16 同批独立复核 approved（P0/P1=0） | ✅ | [r7](../reviews/FEA-09-PREREQ-1-r7.md) |
| 2 | 方向/四维 scope/撤销 ACK/密码短期引用/WireLog 脱敏/异步状态机条款经独立复核 | ✅ | r7 报告与 C-06 v1.1 载体 |
| 3 | `check.ps1` PASS、`verify_pins.ps1` **17/17**（v1.0/v1.1 历史条件；v1.3 为 **18/18**，见第 5 行） | ✅ | `verification/FEA-09-PREREQ-1/logs/check.log`、`pins.log` |
| 4 | 冻结记录含 §1A pin 口径与 §1B 复核字节差异 | ✅ | 本记录 |
| 5 | v1.3：C-06 v1.2 与本契约同批独立 byte-level 复核 **r3 approved（P0=0/P1=0）**；`verify_pins` **18/18**（C16 新值、其余 16 项不变）；Run wire/错误闭集/schema/依赖零改动 | ✅ | 载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C06-C16.md` §6；`verification/FEA-11-RUN-GRANT-1-PREREQ-1/logs/pins.log` |
| 6 | v1.4：容器多成员 entry 语义经独立 byte-level 复核 r1 changes_requested → r2 **approved（P0=0/P1=0/P2=0）**；`verify_pins` **18/18**（C16 新值、其余 **17** 项不变）；wire 字段/命令集/TTL/撤销/错误闭集/Run wire 零改动；C-06/C-17 零改动 | ✅ | 载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16.md` §6；`verification/FEA-11-RUN-GRANT-2B-PREREQ-1/logs/pins.log` |

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

## 7. v1.3 UNFREEZE 重冻（2026-11-06）

| 项 | 值 |
|---|---|
| 载体 | `doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C06-C16.md` |
| 触发/授权 | 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；`FEA-11-RUN-GRANT-1` 权威 scope review **READY-WITH-UNFREEZE**（U-A）+ Codex 第二意见一致（非权威存档） |
| 修订内容 | §0 增 `source.read.run/1` 能力；新增 §2.4 `AuthorizeSourceReadForRun`（Run dispatch 前建立 grant→binding 读授权；closed shape；per-page facts/scope 校验；refused 非空即零绑定写入；零 DB 写；幂等）；**Run wire/错误闭集/TTL/撤销语义零改动**；M2-C1 不改（HostControl 枚举滞后登记 follow-up） |
| 独立复核 | 载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C06-C16.md` §6：r1 `changes_requested` → r2 `changes_requested`（P0=0/P1=0/P2=2/P3=9，登记面）→ 处置 → **r3 `approved`（P0=0/P1=0）**，session `3f908eee…`，reviewed_head `b17d72821` |
| 冻结字节 sha256 | `7c355ccb8f826879e34252750c642c8a7b5c138cd5be5b089a7a518bb56519e5`（工作树 = 复核字节，无差异） |
| 历史 pin（保留） | v1.1 `0b9511a55ea1…`；v1.0 `6e7f8d3d7a81…` |
| 其他 16 pins | 逐字节不变（C-06 与 C-16 为本批重签；v1.3 阶段断言） |

## 8. v1.4 UNFREEZE 重冻（2026-11-07）

| 项 | 值 |
|---|---|
| 载体 | `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16.md` |
| 触发/授权 | 用户 2026-11-06 全授权；`FEA-11-RUN-GRANT-2` 权威 scope review **READY-WITH-UNFREEZE**（2B 仅需 C-16，1 pin）+ Codex 裁决输入（同意 C-16 修订）；DSH 裁决 T-1…T-5 |
| 修订内容 | §2 增「容器源多成员 entry」明文（zip/cbz/pdf `entries[]` 1..N；同容器 path、成员 locator/ordinal 来自 Core 权威、facts=容器身份；逐项校验、任一项不符整 grant typed 拒绝、不截断；匹配 OR+facts、无路径回退）；§0 wire 行澄清；§10 条件/变更记录。**wire 字段/命令集/TTL/撤销/错误闭集/Run wire 零改动**；C-06/C-17 在内的其余 17 pins 零改动 |
| 独立复核 | 载体 §6：r1 `changes_requested`（P0=0/P1=2/P2=4/P3=9；P1-1 = 预算超限错误码、P1-2 = 提交隔离）→ DSH 处置（错误码拆分、计数修正、冻结记录清理、LF 规范化）→ **r2 `approved`（P0=0/P1=0/P2=0/P3=11 非阻断；session `e032ed9a-…`；reviewed_head `a0bafc89e`）** |
| 冻结字节 sha256 | `ad25fb3c89bb1749552c3de988369ae93b5e9e7f563ce2530a5d4c65ba2ad8dc` |
| 历史 pin（保留） | v1.3 `7c355ccb8f82…`；v1.1 `0b9511a55ea1…`；v1.0 `6e7f8d3d7a81…` |
| 其他 17 pins | 逐字节不变（复核断言见载体 §6） |




