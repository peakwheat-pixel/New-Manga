# C04b 删除协议字段与码表 · 冻结记录

**契约**：`doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md`
**冻结时间**：2026-11-01；**v1.1 UNFREEZE 重冻：2026-11-05**（载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md`；触发 Codex 裁决 OVERTURN 3a/4；授权链：用户 2026-11-05「裁决交 codex/zcode」）
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：[Gate 阻塞口径裁定 v2](GATE-CLOSURE-RULING-2026-11-01.md)（[复核 approved](../reviews/GATE-CLOSURE-RULING-r2.md)）+ [冻结矩阵](FEA-CONTRACT_FREEZE_MATRIX.md)

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md` |
| sha256（v1.1，2026-11-05 重冻） | `acc8f0e03d42fd574837cc556e9fa546ba355d7f45a5eefc7bd7b9fe8c16968f` |

历史：v1.0 的 sha256 为 `694ce5bc8c8bcb21f45858e57a110d3b5c02ec48f487980d9119a122cd419947`（2026-11-01 冻结，已被 v1.1 取代，仅供追溯）。

**冻结语义**：条款字节自本记录起不得改动；修订须走 UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`）+ 重新独立复核 + 重新冻结。

## 1B. 冻结字节 vs 复核字节

| 项 | 值 |
|---|---|
| 最后一次独立复核（v1.0） | r3 approved（FEA-GOV-5-c04b-r3） |
| 复核后到 v1.0 冻结的改动 | 仅状态行 + 变更记录 |
| **v1.1 UNFREEZE 复核** | 七轮 fresh subagent 复核（r1–r6 为 CHANGES 迭代、r7 窄面 APPROVE；无 P0 残留）：r1 `...\unfreeze-review\CONTRACT-UNFREEZE-2026-11-05-review.md`（P0-1/P0-2）；r2 `...\unfreeze-review-r2\...-review-r2.md`（P0-2/minor/manifest）；r3 最终字节 `...\unfreeze-final-review\...final-review.md`（2×P0；session `d3c34714…`；快照 `snapshot-2139`）；r4 新字节 `...\unfreeze-final-review-r2\...final-review-r4.md`（0×P0+5×P1+10×P2；session `79b03393…`；报告 sha256 `b6bd2693…`）；r5 新字节 `...\unfreeze-final-review-r3\...final-review-r5.md`（0×P0+2×P1+10×P2；session `6a22e682…`；报告 sha256 `02b30b52…`）；r6 `...\unfreeze-final-review-r4\...final-review-r6.md`（0×P0+1×P1（记录真实性）+8×P2；session `1ece323d…`；报告 sha256 `924847b9…`）；**r7 窄面 `...\unfreeze-final-review-r5\...final-review-r7.md`（0×P0+0×P1，2×P2 记录精度不阻断；session `14e8baef…`；报告 sha256 `8af2d4f1…`）→ APPROVE**。**结论：C-04b `acc8f0e0…` 与 M2-C1 `701093b5…` 为最终冻结字节；8 项 P2 residual 转后续文档卡；UNFREEZE commit `fc9833479`。** |
| **v1.1 冻结处置** | r6 判 CHANGES（仅 P1-E 记录真实性 + 8×P2）→ 路径 A：C-04b/M2-C1 字节不变，本记录/载体改为如实 residual → **r7 窄面 APPROVE（session `14e8baef…`，报告 sha256 `8af2d4f1…`）→ 已重冻（UNFREEZE commit `fc9833479`）**；本节与 §4B 已补记 r7 reviewer/session/hash 与最终 sha。 |

> **注意**：若 v1.1 最终字节复核未通过，本记录的 sha 行必须回退，不得以未复核字节作为 v1.1 pin。

**为什么必须有这一节**：冻结条件①是「独立复核通过」，若冻结字节 ≠ 复核字节，该条件在证据上不覆盖被冻内容。本节的目的是把差异显式化，而不是掩盖它。

## 2. 冻结条件逐条核验

| # | C-04b §5 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核通过 | ✅ | v1.0：r1→r2→r3 approved；**v1.1：r1–r6 CHANGES 迭代（P0 已清；r6：0×P0+1×P1+8×P2，报告 sha256 `924847b9…`）→ 路径 A 记录修正 → r7 窄面 APPROVE（0×P0+0×P1，报告 sha256 `8af2d4f1…`，session `14e8baef…`）→ ✅** |
| 2 | C-01b 已冻结（语义先行） | ✅ | [FEA-CONTRACT-FROZEN-C01b](FEA-CONTRACT-FROZEN-C01b.md) |
| 3 | `G-DELETE-CONTRACT` **不阻塞本单** | ✅ | [裁定 v2](GATE-CLOSURE-RULING-2026-11-01.md) R-1′：Gate 保持 OPEN；本单只承载 D07 |
| 4 | DSH 批准协议 minor `2.11` | ✅ | 裁定 R-3（新增 1 命令 + 2 码；兼容性**依赖旧端 fail-closed**，不依赖旧端接受新码） |
| 5 | M2-C1 扩展**方案**已冻结在 §2.4 | ✅ | §2.4 列 4 个扩展点；**字节修订**是释放前置（见 §4） |
| 6 | `check.ps1` PASS | ✅ | PASS（3 persistent warnings） |

## 3. 依赖与后果

- **上游**：C-01b 已冻结（SC-30/31/33 的协议层落地）。
- **下游**：C-09（删除/备份/迁移）仍 blocked —— 其条件②「两 Gate 关闭」**不满足**（Gate 保持 OPEN）。
- **释放实现前必须完成**（裁定 R-2′）：M2-C1 §5.11.3 表 + 两个 ErrorView 的**字节修订**由**独立 Task**（**不得并入任何删除实现 Task**）完成并复核，复核须含**负向对照**：未扩 M2-C1 时新码必须被 host 投影拒绝。
- **本裁定不新增运行时保证**：`PermanentlyDeleteBookErrorView` 与两新码在 `apps/**`+`src/**` 0 命中，host 投影未接线——"新码不能用"是**契约纪律**，靠该独立 Task 的 AC 与 Review 落实。

## 4. 不构成什么

- **不构成**实现授权。**不构成** Gate 关闭（`G-DELETE-CONTRACT` / `G-CONTRACT` 均**保持 OPEN**）。
- **不构成**远端 push 授权。

## 4B. v1.1 修订与复核记录（2026-11-05，UNFREEZE）

- **修订内容**（详见 C-04b §0 与载体）：current 全量披露/绑定（`currentRegionRevisionIds`/`currentArtifactRevisionIds`，canonical v2）；retry 保序 pending 子集 + manifest JSON 持久化 + 两级强校验 + mixed 拒绝；preview minor 保持 11。
- **触发与复现**：Codex 裁决 `doc/reviews/DSH-DECISIONS-2026-11-05-codex.md`；复现证据 `G:\CODEX\New Manga.workspace\FEA-11\codex-adjudication\run-43e38c334dbb48439f82519792fbb34e\current-pointer-probe.json`（非首个 current 变化旧 digest 仍删除成功）与 `FAKE_DIGEST` 混合 retry 删除存活书。
- **复核**：五轮复核均 CHANGES（r1/r2/r3/r4/r5，见 §1B），无 P0 残留。r3 P0 与 r4/r5 的 P1/P2 处置：
  - **P0-1（单条形状）**：C-04b/M2-C1 已按形状分支——单条 `inventory_digest` = 该 book 逐书 digest（首次=当前重算；retry=manifest 值）；批量才用集合级 digest（首次=当前重算集合；retry=manifest `original_collection_digest`）。
  - **P0-2（exact-match vs retry 子集）**：校验顺序行已重写为形状/retry 分支：首次确认批量键集合与顺序必须与预览 `book_ids` 完全一致；retry 必须为**保序 pending 子集**，两者不再冲突。
  - P1-1（r3）→ r4 指出未真正改 → r5 指出仍残留 → 本轮已逐处落实：M2-C1 `:136` rev 2.14、`:922/:930/:934` 全部改节名引用（含代码块内 `bookIds` 注释）、§5.13 标题 rev 2.14；r6 逐行验证。
  - r4 P1-A：同上；r5 复核确认 `:922/:934/:791` 已修、`:930`（代码块内 `C-04b :41`）与 `:136`（rev 2.13）残留——本轮已修。
  - r4 P1-B（首确认/retry 时效）：C-04b `:67`、M2-C1 `:816` 已限定「首次确认」，retry 不适用（PD-07 manifest 校验）；r5 确认 CLOSED。
  - r4 P1-C（失败分类扫描）：carrier §5-5 已改 INVALID_REQUEST；A3 `:38`、C-04b `:72`、M2-C1 `:813` 的「键集合→STALE」与括号倒置本轮已统一为「缺/多 key→INVALID_REQUEST；键集合/顺序/子集/值→STALE」。
  - r4 P1-D：C-04b §0 摘要已按单条/批量分支；r5 确认 CLOSED。
  - r4 P1-E / r6 P1-E：记录真实性。r6 指出 C-04b 字节零改动但本记录仍称 P2「已处理」；本轮按**路径 A**：C-04b/M2-C1 不变，本记录/载体改为**如实登记 residual（8 项 P2 转后续卡、不阻断）**；删去「已处理/已修复」断言；§4A L-1/L-2 重编号；§5 sha 与最终字节一致（r7 确认）。
  - P1-2：§5.13 已补「缺省=unknown / UI 阻止确认 / `[]` 才表示无 current」（r4 复核确认）。
  - P1-3：§3.2 / §5 command catalog / §11 / §12 已补 rev 2.14 说明（r4/r5 复核确认 8 个修订区落地）。
  - P1-4：失败分类单一映射（r4 指出载体仍相反 → 本轮统一）：字段缺失/格式/`inventory_digests` 缺 key 或多 key → `INVALID_REQUEST`；键集合/顺序/子集/值/集合 digest/manifest 缺失损坏/重算不一致 → `BOOK_DELETE_STALE_PREVIEW`；无 Book 行且无 manifest → `BOOK_NOT_FOUND`。
  - P1-5：`inventory_inputs` 定义为 A2 canonical v2 自包含 14 键可复算对象；retry 时从 inputs 重算逐书 digest 与持久化值比对，不一致即篡改 → fail-closed；`batch_id`=uuidv4；retry 不得改写批次字段。
  - P1-6：载体 B4 与 §4 统一为「Host generic passthrough 不补 null；缺省=unknown；UI fail-closed」（r4/r5 复核确认）。
- **r7 最终字节 sha（冻结字节）**：C-04b `acc8f0e03d42fd574837cc556e9fa546ba355d7f45a5eefc7bd7b9fe8c16968f`、M2-C1 `701093b5282228fdc791843146bf9459338e6ac1829ce3a801c72470fc938b7f`（r7 报告 `8af2d4f1…` 与 `FINAL-SHA-r7.txt` 记录；r6 报告 `924847b9…` 为上一轮）。**r7 APPROVE 已重冻（UNFREEZE commit `fc9833479`）**；CORE r3 返修代码另起 commit。
- **附带影响**：ADJ-2026-11-05 §2.2 OUT「不改 C-04b 正文」由本 UNFREEZE 例外覆盖，性质为**推定**（依据：用户 2026-11-05「裁决交给 codex 或 zcode」+ Codex 裁决要求正式 UNFREEZE）。**回问条件**：若用户后续明确表示 UNFREEZE 不属其授权范围，本 v1.1 立即回退到 v1.0 字节（pin `694ce5bc…`），删除线保护缺陷回退为已知 limitation（PD-04 不满足），CORE 返修代码/证据不得合入。18 pins 数量不变，M2-C1 同提交 rev 2.14。

## 4A. 已知限制（冻结后发现）

> **v1.1 residual（r6 复核登记，不阻断重冻，转后续卡）**：①artifact 成员谓词补 `media_artifacts.book_id=本书`；②C-04b §2.0「单一字段」措辞；③载体 A1 separate/detached 与代表值排序；④C-04b §1 表 M2-C1 行号指针（v1.0 历史引用）；⑤首确认「预览 book_ids」与单条 `inventoryDigests[book_id]` 来源措辞；⑥r1–r3 报告 sha 记录；⑦M2-C1 banner/history 批量限定；⑧单条 manifest 批次字段。以上不改变 v1.1 保护语义，登记为后续文档修订。

- **L-1（v1.0 原始记录，保留）**：book 级聚合 digest 对「计数不变而分布变」（A 区加锁 + B 区解锁）不敏感；**region 级指针**不进 book 级 `currentRevisionId`。这是 `inventory_digest` 的粒度局限，**本契约冻结时已知**。C-13 的 `protectionDigest` 是**编辑层**的逐 Region 摘要，不替代本契约的 book 级 digest，也不接入删除 preflight。若删除线实现需要逐 Region 检测，须走本契约的 **UNFREEZE** + 协议扩展。
- **L-2（v1.1 状态更新）**：v1.1 已把**全部 region/artifact 的 current 指针**纳入 canonical v2（消除 L-1 的「region 级指针不进 digest」部分），但 **lock/pin 的逐 region 分布**仍以聚合计数表达，分布变化不进 digest；若删除线需要逐 Region 锁分布绑定，须再次 UNFREEZE（逐 region lock 数组）。v1.1 不声称消除该剩余限制。



## 5. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin、条件核验、依赖与后果 | DSH |
| 2026-11-05 | **v1.1 UNFREEZE 重冻（r7 APPROVE）**：current 全量披露/绑定（canonical v2）、retry 保序 pending 子集 + manifest + 两级强校验 + mixed 拒绝；单条/批量形状分支（r3 P0-1/P0-2）；§3.2/§5/§11/§12 同步；sha 与最终字节一致（§1 v1.1 行 = C-04b `acc8f0e0…`；r7 报告 `8af2d4f1…`；UNFREEZE commit `fc9833479`）；依据 Codex 裁决 OVERTURN 与用户授权（ADJ 例外，见 §4B） | DSH |

## 6. Errata 注记（2026-11-01 追加；**原文保留**）

按 [关闭裁定 §4](GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md) 的 Errata 表，本记录的以下**冻结时状态描述**已被取代，原文保留不改：

- §3 第 3 条「**下游**：C-09（删除/备份/迁移）仍 blocked —— 其条件②「两 Gate 关闭」**不满足**（Gate 保持 OPEN）」：该句为**冻结当时**（2026-11-01 早段）状态；此后走 [D07 解环](../tasks/FEA-D07-UNBLOCK.md) 与 [C-09 v5 冻结](FEA-CONTRACT-FROZEN-C09.md)，两 Gate 于 2026-11-01 **CLOSED**。
- §4「**不构成** Gate 关闭（`G-DELETE-CONTRACT` / `G-CONTRACT` 均**保持 OPEN**）」：同上，为冻结时状态；现行两 Gate 均 **CLOSED**（[关闭裁定](GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md)）。
- 其余内容（§1 冻结字节 pin、§1B、§2 条件核验、§4A L-1、§5 变更记录）**不受本 Errata 影响**；C-04b 草案字节未改（pin `694ce5bc…`）。**v1.1 更新（2026-11-05）**：上述「草案字节未改」仅描述 v1.0 历史状态；v1.1 经 UNFREEZE 已改字节，现行 pin 见 §1（v1.1 行）。
