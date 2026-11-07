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
| sha256（**v1.2**，2026-11-08 重冻） | `4b304c0c315fe8ec4ae86544590919329c27234ead2b3ad9357b2e99a2d54e52` |
| git hash-object（v1.2 blob id） | `a30e4080116d01512977eca40de1c43ea7244a64` |
| 历史 pin（保留） | v1.1 `acc8f0e03d42fd574837cc556e9fa546ba355d7f45a5eefc7bd7b9fe8c16968f`；v1.0 `694ce5bc8c8bcb21f45858e57a110d3b5c02ec48f487980d9119a122cd419947` |

历史：v1.0 的 sha256 为 `694ce5bc8c8bcb21f45858e57a110d3b5c02ec48f487980d9119a122cd419947`（2026-11-01 冻结，已被 v1.1 取代，仅供追溯）。

**冻结语义**：条款字节自本记录起不得改动；修订须走 UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`）+ 重新独立复核 + 重新冻结。

## 1B. 冻结字节 vs 复核字节

| 项 | 值 |
|---|---|
| 最后一次独立复核（v1.0） | r3 approved（FEA-GOV-5-c04b-r3） |
| 复核后到 v1.0 冻结的改动 | 仅状态行 + 变更记录 |
| **v1.1 UNFREEZE 复核** | 七轮 fresh subagent 复核（r1–r6 为 CHANGES 迭代、r7 窄面 APPROVE；无 P0 残留）：r1 `...\unfreeze-review\CONTRACT-UNFREEZE-2026-11-05-review.md`（P0-1/P0-2）；r2 `...\unfreeze-review-r2\...-review-r2.md`（P0-2/minor/manifest）；r3 最终字节 `...\unfreeze-final-review\...final-review.md`（2×P0；session `d3c34714…`；快照 `snapshot-2139`）；r4 新字节 `...\unfreeze-final-review-r2\...final-review-r4.md`（0×P0+5×P1+10×P2；session `79b03393…`；报告 sha256 `b6bd2693…`）；r5 新字节 `...\unfreeze-final-review-r3\...final-review-r5.md`（0×P0+2×P1+10×P2；session `6a22e682…`；报告 sha256 `02b30b52…`）；r6 `...\unfreeze-final-review-r4\...final-review-r6.md`（0×P0+1×P1（记录真实性）+8×P2；session `1ece323d…`；报告 sha256 `924847b9…`）；**r7 窄面 `...\unfreeze-final-review-r5\...final-review-r7.md`（0×P0+0×P1，2×P2 记录精度不阻断；session `14e8baef…`；报告 sha256 `8af2d4f1…`）→ APPROVE**。**结论：C-04b `acc8f0e0…` 与 M2-C1 `701093b5…` 为最终冻结字节；8 项 P2 residual 转后续文档卡；UNFREEZE commit `fc9833479`。** |
| **v1.1 冻结处置** | r6 判 CHANGES（仅 P1-E 记录真实性 + 8×P2）→ 路径 A：C-04b/M2-C1 字节不变，本记录/载体改为如实 residual → **r7 窄面 APPROVE（session `14e8baef…`，报告 sha256 `8af2d4f1…`）→ 已重冻（UNFREEZE commit `fc9833479`）**；本节与 §4B 已补记 r7 reviewer/session/hash 与最终 sha。 |

| **v1.2（2026-11-08，UNFREEZE）** | 契约债务清偿（R-1/R-2/R-3/R-4/R-5/R-8 的**措辞与谓词文字**）：C-04b → **v1.2** `4b304c0c…`（blob `a30e4080…`）；M2-C1 → **rev 2.15** `a82a7fc1…`（blob `cb8eeb21…`，**0/18 机械 pin**，手工登记）；独立 byte-level 复核链：r1 `changes_requested`（P1=2）→ 返修 → r2 `changes_requested`（P1=1）→ 再返修 → **r3 `approved`（P0=0/P1=0/P2=3/P3=4）**；**不改**任何规则/字段名/错误码/语义；载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-08-C04B-RESIDUAL.md`。 |

> **注意**：若 v1.1 最终字节复核未通过，本记录的 sha 行必须回退，不得以未复核字节作为 v1.1 pin。

**为什么必须有这一节**：冻结条件①是「独立复核通过」，若冻结字节 ≠ 复核字节，该条件在证据上不覆盖被冻内容。本节的目的是把差异显式化，而不是掩盖它。

## 1C. v1.1 UNFREEZE 复核报告完整 sha256（R-6 闭合；2026-11-07 实测）

> 本表闭合 §4A **R-6**（原 §1B 只有 r1–r3 路径、r4–r7 只有 8 位前缀）。**§1B 原文保留不改**（历史行文），
> 完整值以本表为准。路径为仓外 workspace（`G:\CODEX\New Manga.workspace\FEA-12\`），sha256 由
> `Get-FileHash -Algorithm SHA256` 实测（base `28a2826af`）。

| 轮次 | 报告（仓外路径） | 大小 | sha256 | reviewer / session |
|---|---|---|---|---|
| r1 | `unfreeze-review\CONTRACT-UNFREEZE-2026-11-05-review.md` | 48,399 B | `600da6aa08d4834733eef947c11913c08ed6506086456d881997529372796a44` | session `004eb6b3-b9cf-431b-8614-d6cd1858c316` |
| r2 | `unfreeze-review-r2\CONTRACT-UNFREEZE-2026-11-05-review-r2.md` | 87,408 B | `2eae498f06ef455c5c3a1e963e3003f0ab917f863158e7dfe41767b479432388` | session 未在报告内暴露 |
| r3 | `unfreeze-final-review\CONTRACT-UNFREEZE-2026-11-05-final-review.md` | 42,856 B | `1b2fa41ec10c8dac7e51203b4d2a1d51f69de042dbdae0296d0fb6632d6f20aa` | session `d3c34714-e1f7-478d-a06d-141a4153b1c6` |
| r4 | `unfreeze-final-review-r2\...-final-review-r4.md` | 33,127 B | `b6bd26937b92c1c799585838f1bec6787cdcbf456a6371fc76c9f823906419d6` | session `79b03393…` |
| r5 | `unfreeze-final-review-r3\...-final-review-r5.md` | 34,683 B | `02b30b5273ffea20da62490509b89d06efc48f1b79dd0a4cb650122ba6bc6ee4` | session `6a22e682…` |
| r6 | `unfreeze-final-review-r4\...-final-review-r6.md` | 30,007 B | `924847b91f4d819a459c10dca9bb7daa0bafff6a7511c8128d24eef32fa7e066` | session `1ece323d…` |
| r7 | `unfreeze-final-review-r5\...-final-review-r7.md` | 17,688 B | `8af2d4f182163215a883f6908b1b17564ced7e470dab29ef719c41131d046424` | session `14e8baef…` |
| 辅助 | `unfreeze-final-review\FINAL-CONFIRM.md` | 1,269 B | `d687ede7c4ab326985bd52de38239a4d52807446dc1c67de910a175f2452a010` | - |

- 上述 r4–r7 完整值与 §1B 已记 8 位前缀一致（`b6bd2693…`/`02b30b52…`/`924847b9…`/`8af2d4f1…`）；
- r2 报告未暴露 reviewer session，如实标注「未在报告内暴露」，不以推测填充；
- 报告字节未改动（只读实测）；本表不改变任何 pin（pin 行在 §1 `:15`，仍 `acc8f0e0…`）。

## 2. 冻结条件逐条核验

| # | C-04b §5 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核通过 | ✅ | v1.0：r1→r2→r3 approved；**v1.1：r1–r6 CHANGES 迭代（P0 已清；r6：0×P0+1×P1+8×P2，报告 sha256 `924847b9…`）→ 路径 A 记录修正 → r7 窄面 APPROVE（0×P0+0×P1，报告 sha256 `8af2d4f1…`，session `14e8baef…`）→ ✅** |
| 2 | C-01b 已冻结（语义先行） | ✅ | [FEA-CONTRACT-FROZEN-C01b](FEA-CONTRACT-FROZEN-C01b.md) |
| 3 | `G-DELETE-CONTRACT` **不阻塞本单** | ✅ | [裁定 v2](GATE-CLOSURE-RULING-2026-11-01.md) R-1′：Gate 保持 OPEN；本单只承载 D07 |
| 4 | DSH 批准协议 minor `2.11` | ✅ | 裁定 R-3（新增 1 命令 + 2 码；兼容性**依赖旧端 fail-closed**，不依赖旧端接受新码） |
| 5 | M2-C1 扩展**方案**已冻结在 §2.4 | ✅ | §2.4 列 4 个扩展点；**字节修订**是释放前置（见 §4） |
| 6 | `check.ps1` PASS | ✅ | PASS（3 persistent warnings） |
| 7 | v1.2：C-04b v1.2 + M2-C1 **rev 2.15** 措辞/谓词同步经独立 byte-level 复核 **r3 `approved`（P0=0/P1=0/P2=3/P3=4；session `98692074-…`）**；`verify_pins` **18/18**（C-04b 新 sha、其余 **17** 不变）；M2-C1 **不在 18 pin 映射**（0/18 机械 pin，sha 手工登记于 §1B/§4C）；无新命令/字段/错误码/能力/`PROTOCOL_MINOR` | ✅ | 报告 `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-2-r3.md`；载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-08-C04B-RESIDUAL.md` §6 |

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
- **复核**：r1–r6 均 CHANGES、r7 窄面 APPROVE（完整报告 sha 见 §1C），无 P0 残留。r3 P0 与 r4/r5 的 P1/P2 处置：
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

## 4C. v1.2 UNFREEZE 重冻（2026-11-08）

| 项 | 值 |
|---|---|
| 载体 | `doc/reviews/CONTRACT-UNFREEZE-2026-11-08-C04B-RESIDUAL.md` |
| 触发/授权 | 用户 AUTORUN 指令（2026-11-08：全部授权/自主裁决/不询问用户）；权威 scope review `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md` §3.3；**DSH 裁决（裁决人=DSH）**：按 AUTORUN §2 判据 (b) 立项清偿契约债务；R-1 的代码实现另立 `FEA-12-CORE-C04B-RESIDUAL-3` |
| 修订内容 | **C-04b v1.2**：R-1 artifact 成员谓词补 `media_artifacts.book_id = 本书`（§0 第 1 条 / §2.1 DTO）；R-2 §2.0 改「不得在同一请求内混用两种 digest 语义」；R-3 删无定义术语 `separate/detached` + 写死 representative 规则（阅读序首个 lineage-visible region current，否则首个 artifact current pointer；仅展示、不进 digest）；R-4 §1 表 M2-C1 行号改**节名**；R-5 首确认「**请求** `book_ids`」+ 单条来源 `inventoryDigests[bookId]`；R-8 单条 manifest 批次取值写死。**M2-C1 rev 2.15**：`:18` banner、`:30` history、`:814/:815/:819` 来源与校验措辞、`:953/:954` DTO 注释、`:972` §5.13 PD-01 段、§5.11.1a/§5.13 标题 rev 引用。**仅措辞与谓词文字；规则/字段名/错误码/能力/`PROTOCOL_MINOR`/wire minor 零改动** |
| 独立复核 | r1 `changes_requested`（P0=0/P1=2/P2=1/P3=4）→ 返修 → r2 `changes_requested`（P0=0/P1=1/P2=2/P3=2）→ 再返修 → **r3 `approved`（P0=0/P1=0/P2=3/P3=4；session `98692074-…`；report `FEA-12-CORE-C04B-RESIDUAL-2-r3.md`）**；r3 独立探针三案验证 representative 与实现等价 |
| 冻结字节 sha256 | C-04b `4b304c0c315fe8ec4ae86544590919329c27234ead2b3ad9357b2e99a2d54e52`；M2-C1 `a82a7fc1e2c8dafeda977c26b68f140e9cecd8061f88692d4624858fc5046e0e` |
| 历史 pin（保留） | C-04b v1.1 `acc8f0e0…`；v1.0 `694ce5bc…` |
| 其他 17 pins | 逐字节不变（C-04b 为 18 份中的 **1/18** 重签；M2-C1 不在 `verify_pins` 映射内） |

## 4A. 已知限制（冻结后发现）

> **v1.1 residual 8 项（r6 复核登记，不阻断重冻）**：本表为 **docs-only 记录收口**（`FEA-12-CORE-C04B-RESIDUAL-1`，
> 0 pin）。**C-04b / M2-C1 契约字节未改**：C-04b 仍 `acc8f0e0…`、M2-C1 仍 `701093b5…`（`verify_pins` 18/18）。
> 位置行号以 `base_commit=28a2826af` 为准；「需 UNFREEZE」= 真正把修复写进冻结字节所需的动作（**本卡不做**）。
> 8 项中仅 **R-6 完全闭合**（见 §1C）；R-3/R-4 的 0 pin 部分已在载体 §5F 登记；其余契约正文**未改**。
>
> **v1.2（2026-11-08）状态更新（append-only，不改上表历史）**：**R-2 / R-3 / R-4 / R-5 / R-8** 的**契约文字**已由
> C-04b **v1.2** 修正（M2-C1 **rev 2.15** 同步），见 §4C 与载体；**R-1** 的**契约谓词文字**已补（`media_artifacts.book_id = 本书`），
> 但**代码实现未改**（仍 page/chapter join）→ **契约与实现当前不一致**，该偏差由 **L-3** 继续登记、归 `FEA-12-CORE-C04B-RESIDUAL-3`
> 收敛；**R-6** 已闭合（§1C）；**R-7**（M2-C1 banner/history 批量限定）已由 rev 2.15 的 banner 与 history 落地。
> 上表「现行权威读法」列保留 v1.1 时点的历史读法，**不改写**。

| ID | residual | 位置（base `28a2826af`） | 当前文本/事实摘要 | 问题 | 性质 | 影响 | 现行权威读法 | 需 UNFREEZE |
|---|---|---|---|---|---|---|---|---|
| R-1 | artifact 成员谓词 | C-04b `:18`、`:53`；M2-C1 `:953-954`；代码 `library.py:1178-1190`、`:1920-1926`、`:1218-1225` | 契约「artifact 谓词=`current_revision_id` 非空」未写 `media_artifacts.book_id=本书`；preview 实现用 page/chapter join，删除路径用 `book_id` | 损坏行（`media_artifacts.book_id` 与 page 所属书不一致）下保护集合可能多/少绑定 | 契约措辞 + 代码行为 | 正常数据无影响；损坏 DB 偏差 | 见 **L-3**；**未修** | C-04b 1/18 + M2-C1 rev + 独立实现卡 |
| R-2 | §2.0「单一字段」 | C-04b `:44` | 「**不得**用单一 `inventory_digest` 字段同时服务两种形状」 | 与 v1.1 §2.0 表 `:41`/`:42` 与 §2.2 `:64`/`:69` 的形状分支字面冲突（v1.0 遗留） | 契约正文（C-04b） | 误读 → fail-closed 拒绝，非静默数据风险 | **以 §2.2 形状分支为准**：单条=逐书值；批量=集合级值 + 逐书 map | C-04b 1/18 |
| R-3 | A1 separate/detached + representative 排序 | 载体 `:16`、`:18`；C-04b `:18`；M2-C1 `:953`；实现 `core_service.py:1904-1930` | `separate/detached` 在契约中**无定义**；「首个 artifact current」未定义排序 | 未来实现者可能误加过滤；代表值来源不明 | 载体 0 pin + 契约正文措辞 | 纯展示字段，不进 digest | `separate/detached` **不是**本契约定义状态、现行不据此裁剪；representative = 无可见 region 时取 `currentArtifactRevisionIds` **字典序最小项**，仅展示、不进 digest | 载体 0；两契约需 C-04b 1/18 + M2-C1 rev |
| R-4 | §1 表 M2-C1 行号指针 | C-04b `:28-32` | `M2-C1 §5.11.1 :685`、`:691-695`、`:733`、`:748`、`:745-760`、`:776-802` | 行号为 v1.0 时点；现行 M2-C1 已漂移（§5.11.1 在 `:746`、§5.11.2 `:823`、§5.11.3 `:838`、§5.11.5 `:875`） | 契约 provenance 元数据 | 审计者可能跳错章节；不影响运行 | **以节名为准**（§5.11.1/§5.11.2/§5.11.3/§5.11.5）；现行行号为 v1.0 历史 | C-04b 1/18 |
| R-5 | 首确认「预览 book_ids」与单条来源 | C-04b `:64`、`:69`；M2-C1 `:814`、`:815`、`:819` | 「与预览 `book_ids` 完全一致」；单条 digest 来源未写；全文 `inventoryDigests[` **零命中** | 预览零副作用不缓存 → 实际校验对象是**请求** `book_ids`；单条应取预览返回的 `inventoryDigests[bookId]` | 契约正文 | 误用集合值 → `BOOK_DELETE_STALE_PREVIEW`/`INVALID_REQUEST`（fail-closed） | 首确认「预览 `book_ids`」读作 **请求 `book_ids`**（预览不缓存；digest 绑定保证一致）；单条取 `inventoryDigests[bookId]`，集合级 `inventoryDigest` 单条**不得**使用 | C-04b 1/18 + M2-C1 rev |
| R-6 | r1–r3 报告 sha 未记 | 冻结记录 §1B（原 `:27`） | r1/r2/r3 只有路径与结论、无 sha256；r4–r7 只有 8 位前缀 | 重冻证据链不完整 | 纯记录（0 pin） | 审计可追溯性 | **已闭合**：r1–r7 完整 sha256 见 **§1C** | 否 |
| R-7 | M2-C1 banner/history 批量限定 | M2-C1 `:18`、`:30` | banner/Revision history 写 retry 规则**未限定「批量」** | 单条读者可能误用集合级/`original_collection_digest` | M2-C1 正文（非规范段） | 误读 → fail-closed 拒绝 | banner/history 的 retry 描述仅适用于**批量**；单条以 §5.11.1a `:815`/`:819` 为准 | M2-C1 rev（**0/18 机械 pin**，需手工记录 sha） |
| R-8 | 单条 manifest 批次字段 | C-04b `:21`、`:71`；实现 `core_service.py:2450-2454`；测试 `test_core_delete_commands.py:1341-1344` | 未区分单条/批量；单条 `original_book_ids`/`original_collection_digest` 取值未写 | 未来实现可能选 null/空数组 | 契约正文（C-04b） | 当前未发布、测试已钉住，无兼容问题 | 单条现行实现：`batch_id`=uuidv4、`original_book_ids=[book_id]`、`original_collection_digest`=对 `[book_id]` 的集合级值；单条 retry **仅校验** `inventory_digest`；契约**未写死** | C-04b 1/18 |

- **L-1（v1.0 原始记录，保留）**：book 级聚合 digest 对「计数不变而分布变」（A 区加锁 + B 区解锁）不敏感；**region 级指针**不进 book 级 `currentRevisionId`。这是 `inventory_digest` 的粒度局限，**本契约冻结时已知**。C-13 的 `protectionDigest` 是**编辑层**的逐 Region 摘要，不替代本契约的 book 级 digest，也不接入删除 preflight。若删除线实现需要逐 Region 检测，须走本契约的 **UNFREEZE** + 协议扩展。
- **L-2（v1.1 状态更新）**：v1.1 已把**全部 region/artifact 的 current 指针**纳入 canonical v2（消除 L-1 的「region 级指针不进 digest」部分），但 **lock/pin 的逐 region 分布**仍以聚合计数表达，分布变化不进 digest；若删除线需要逐 Region 锁分布绑定，须再次 UNFREEZE（逐 region lock 数组）。v1.1 不声称消除该剩余限制。
- **L-3（2026-11-07，R-1 的 code limitation；源自 `FEA-12-CORE-r3.md:134`，scope review `FEA-12-CORE-C04B-RESIDUAL-scope-r1` 复核）**：`src/infrastructure/sqlite/library.py:1178-1190` 的 `list_book_artifact_current_pointers` 用 **page/chapter join** 取 artifact（`ma JOIN pages p ... JOIN chapters c ... WHERE c.book_id = ?`），**没有** `media_artifacts.book_id = 本书`；而删除路径（`:1920-1926`）与 `list_book_artifact_revision_ids`（`:1218-1225`）使用 `book_id`。当损坏行使 `media_artifacts.book_id` 与其 `page_id` 所属书不一致时，preview 的 current 保护集合与删除集合可能不一致（对某书**多绑定**/对另一书**少绑定**）。原状为「正常数据无影响、**未修**」；**2026-11-08 已由 `FEA-12-CORE-C04B-RESIDUAL-3` 修复**（`library.py` 的 `list_book_artifact_current_pointers` 成员谓词改为 `media_artifacts.book_id = ?`，保留 `current_revision_id` 非空与阅读序 7 键；3 个真实损坏行用例判别，改回 page join 即 RED）。**契约与实现现已一致**（C-04b v1.2 谓词 = 代码谓词）；本条保留为历史记录。


- **L-4（2026-11-08，`FEA-12-CORE-C04B-RESIDUAL-3` 的 Review R3-002 登记）**：`schema.py` 的 `media_artifacts` 只有 `(page_id, artifact_type)` 索引，`book_id` **无索引**；改成 `WHERE ma.book_id = ?` 后执行计划由索引 `SEARCH` 变为 `SCAN ma`，成本随**全库** artifact 总数增长（实测 6,000 artifacts：0.24→0.43 ms/书；60,000：0.26→5.32 ms/书；批量预览最多 20 书逐书放大）。**非阻塞**（预览为一次性只读路径、绝对量级小）；**2026-11-08 已由 `FEA-12-CORE-C04B-INDEX-L4-1` 修复**（v9 迁移加 `idx_media_artifacts_book(book_id)`；`EXPLAIN` 由 `SCAN ma` → `SEARCH ma USING INDEX`；COUNT/DELETE 走覆盖索引；60k 厚数据集 8.90→4.36 ms/书，旧谓词实测 2.85，仍 1.53×；回滚只走备份）。
- **L-5（2026-11-08，R3-004 登记；pre-existing）**：跨书损坏行（`book_id=A`、页属 B）删除 A 时，DB 行与 `managed_path` 随 `book_id` 删除，但 `preview_lifecycle` 资源枚举仍按 `page_ids` 归属（`list_page_artifact_ids(A 的 page)`），该 artifact 的 preview 缓存文件可能**漏清**。**非本卡引入**；本卡只对齐「preview 集合 vs 删除谓词」。**未修**。


## 5. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin、条件核验、依赖与后果 | DSH |
| 2026-11-05 | **v1.1 UNFREEZE 重冻（r7 APPROVE）**：current 全量披露/绑定（canonical v2）、retry 保序 pending 子集 + manifest + 两级强校验 + mixed 拒绝；单条/批量形状分支（r3 P0-1/P0-2）；§3.2/§5/§11/§12 同步；sha 与最终字节一致（§1 v1.1 行 = C-04b `acc8f0e0…`；r7 报告 `8af2d4f1…`；UNFREEZE commit `fc9833479`）；依据 Codex 裁决 OVERTURN 与用户授权（ADJ 例外，见 §4B） | DSH |
| 2026-11-07 | **docs-only residual 收口（0 pin；`FEA-12-CORE-C04B-RESIDUAL-1`）**：§4A 8 项扩为 `R-1…R-8` 表（位置/性质/影响/权威读法/是否需 UNFREEZE）+ 新增 **L-3**（R-1 artifact 成员谓词代码偏差，未修）；新增 §1C（r1–r7 完整 sha256，闭合 R-6）；§4B「五轮」→「r1–r6 CHANGES + r7 APPROVE」（相邻精度项修正，不计入 8 项 AC）；载体追加 §5F errata。**C-04b/M2-C1 契约字节未改**（`acc8f0e0…`/`701093b5…`，pins 18/18） | DSH |
| 2026-11-08 | **v1.2 UNFREEZE 重冻（契约债务清偿）**：C-04b R-1/R-2/R-3/R-4/R-5/R-8 措辞与谓词文字修正 + M2-C1 rev 2.15 同步；**不改规则/字段名/错误码/语义**；C-04b `acc8f0e0…`→`4b304c0c…`（1/18 pin），M2-C1 `701093b5…`→`a82a7fc1…`（0/18 机械 pin，记录登记）；独立复核 r1/r2 `changes_requested` → r3 **`approved`（P0=0/P1=0/P2=3/P3=4）**；载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-08-C04B-RESIDUAL.md` | DSH |

## 6. Errata 注记（2026-11-01 追加；**原文保留**）

按 [关闭裁定 §4](GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md) 的 Errata 表，本记录的以下**冻结时状态描述**已被取代，原文保留不改：

- §3 第 3 条「**下游**：C-09（删除/备份/迁移）仍 blocked —— 其条件②「两 Gate 关闭」**不满足**（Gate 保持 OPEN）」：该句为**冻结当时**（2026-11-01 早段）状态；此后走 [D07 解环](../tasks/FEA-D07-UNBLOCK.md) 与 [C-09 v5 冻结](FEA-CONTRACT-FROZEN-C09.md)，两 Gate 于 2026-11-01 **CLOSED**。
- §4「**不构成** Gate 关闭（`G-DELETE-CONTRACT` / `G-CONTRACT` 均**保持 OPEN**）」：同上，为冻结时状态；现行两 Gate 均 **CLOSED**（[关闭裁定](GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md)）。
- 其余内容（§1 冻结字节 pin、§1B、§2 条件核验、§4A L-1、§5 变更记录）**不受本 Errata 影响**；C-04b 草案字节未改（pin `694ce5bc…`）。**v1.1 更新（2026-11-05）**：上述「草案字节未改」仅描述 v1.0 历史状态；v1.1 经 UNFREEZE 已改字节，现行 pin 见 §1（v1.1 行）。
