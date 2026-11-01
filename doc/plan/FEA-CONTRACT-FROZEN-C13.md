# C13 草稿与保护契约（D04） · 冻结记录

**契约**：`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md`
**冻结时间**：2026-11-01
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：[用户裁决记录 2026-11-01](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md)（**U-03=B** draft owner 模型）+ [Gate 阻塞口径裁定 v2](GATE-CLOSURE-RULING-2026-11-01.md)

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md` |
| 版本 | **v5** |
| sha256（冻结后最终字节） | `d2cb8de4dd79fb490e3e5c12a6aaad3e1a0bb294c217a79f083ecfeab683837c` |

**冻结语义**：条款字节自本记录起不得改动；修订须走 UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`）+ 重新独立复核 + 重新冻结。

## 1B. 冻结字节 vs 复核字节

| 项 | 值 |
|---|---|
| 最后一次独立复核 | r4 approved（FEA-C13-r4） |
| 复核后到冻结的改动 | U-03 段 + §9 条件 2 改写（状态标注型，语义未变）+ 状态行 |
| 处置 | **需补极窄复核** |

**为什么必须有这一节**：冻结条件①是「独立复核通过」，若冻结字节 ≠ 复核字节，该条件在证据上不覆盖被冻内容。本节的目的是把差异显式化，而不是掩盖它。

## 2. 冻结条件逐条核验（4/4）

| # | C-13 §9 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核通过（上下文独立） | ✅ | r1（2 P1）→ r2（2 P1）→ r3（1 P1）→ r4 [approved](../reviews/FEA-C13-r4.md)（P0×0 / P1×0 / P2×4 已修） |
| 2 | **U-03 用户裁决**（SC-D03 的 draft owner 模型） | ✅ | 用户裁决 **B（draft owner）**——与草案起草口径一致，无需改 SC-D03 |
| 3 | C-01b 已冻结 | ✅ | [FEA-CONTRACT-FROZEN-C01b](FEA-CONTRACT-FROZEN-C01b.md) |
| 4 | `check.ps1` PASS | ✅ | PASS（3 persistent warnings） |

## 3. 覆盖的 D04 六项（方案 §13.2 `:767`）

| # | D04「必须冻结的内容」 | 承载条款 |
|---|---|---|
| 1 | edit token/journal | SC-D04（edit token 幂等键）+ SC-D05（journal 持久检查点） |
| 2 | Draft/Protection 版本 | SC-D01（Draft 11 字段）+ **SC-D12**（`protectionDigest` = 三锁 + manual 位） |
| 3 | candidate-only prepare | SC-D06（活跃草稿）+ SC-D07（`RegionCandidate`） |
| 4 | 统一事务 live apply | SC-D08（全 Region 同事务 + 乐观并发校验） |
| 5 | 锁定样式白名单 | SC-D09（三锁 × 三域）+ SC-D10（`TextStyle` 真实 6 键） |
| 6 | 旧非幂等写兼容 | SC-D11（统一去重键 + 过渡期客观判据） |

## 4. 关键实现铁律（来自复核）

1. **SC-D10 白名单 = `TextStyle` 的 6 个 snake_case 字段**（`entities.py:204-212`）；**扩键必须先改 `TextStyle` 定义再 UNFREEZE**，不得先放行再补字段。
2. **SC-D12 的 `protectionDigest` 只含保护状态位**（三锁 + `text_json` 的 manual 位）；修订漂移由 SC-D08 的 `BaseRevisionId` 承担。拒绝走既有 `LOCK_CHANGED` 路径；**实现需把 manual 位纳入快照比对**（实现 Task 的 AC，不改 `ports.py` 契约）。
3. **SC-D03 的 draft owner（U-03=B）**：主窗与浮窗共享 `DraftId`、单一串行 patch 队列、文本冲突禁止自动合并、跨 Session 只读或显式转移。
4. **不新增任何错误码**（`STALE_PROTECTION` 已在 v3 撤销）；不修改 C-04b。

## 5. 依赖与后果

- **上游**：C-01b 已冻结（`regions`/`region_revisions` 表结构、三锁列、composite FK 均不变）。
- **下游**：
  - **D04 现在有承载契约** → `G-DELETE-CONTRACT` 对 D04 的覆盖完成（Draft/保护面）；
  - 但 Gate **不自动关闭**：D06（C-08）未冻、D05 剩余子面（重定位/同步、容器页映射）**无承载条款**；
  - **C-09 条件③（两 Gate 关闭）仍不满足** → C-09 继续 blocked。
- **实现**：FEA-03（草稿与保护协调）的释放条件 = 本单冻结 + C-11 建卡 + 独立 Review。

## 6. 已知限制（冻结时登记）

- **L-1**：SC-D12 的 `protectionDigest` 是**编辑层**摘要，**不接入删除 preflight**；C-04b 的 book 级聚合对「计数不变而分布变」不敏感（见 [C-04b 冻结记录 §4A L-1](FEA-CONTRACT-FROZEN-C04b.md)）。删除线若需逐 Region 检测，须走 C-04b 的 UNFREEZE。
- **L-2**：`auto_font_size_enabled` 与 `font_size` 的联动语义不在本契约（属于 `TextStyle` 自身行为）。
- **L-3**：防抖间隔（300–500ms）是方案举例值，**具体值待 FEA-03 用真实输入实测**。

## 7. 不构成什么

- **不构成**实现授权；**不构成** Gate 关闭；**不构成**远端 push 授权。

## 1A. pin 修正记录（2026-11-01，**保留原值**）

| 项 | 值 |
|---|---|
| 原 pin（**错误口径**） | `035a89a41cc75fcace9fc6ca96648a40ba3e19b6f50331efbc074c3dea7d9b29` |
| 修正后 pin（最终字节） | `d2cb8de4dd79fb490e3e5c12a6aaad3e1a0bb294c217a79f083ecfeab683837c` |
| 差异范围 | 冻结提交内**同时含 U-03 段改写 + §9 条件 2 改写**（属状态标注型条款行，语义未变；来源＝U-03=B 用户裁决） |

**为什么保留原值**：pin 是证据，不能静默替换。原值可独立复现（还原本次冻结动作后重算即得），因此证明冻结前的确切字节；修正后的值才是后续校验基准。

**冻结字节 = 复核字节？** 见 §1B。

**纪律（自本记录起）**：
1. pin **必须在冻结动作全部完成后**计算（含状态行、U-03 等元数据改动）；
2. 冻结后任何字节改动（含状态行）都必须**重算 pin 或走 UNFREEZE**；
3. 建议同时记录 worktree sha256 与 `git cat-file blob`（LF）sha256 双口径；
4. **冻结提交本身不得含条款编辑**——最后处置必须在冻结**之前**的独立提交完成并经复核。


**为什么保留原值**：pin 是证据，不能静默替换。原值证明「条款内容与冻结前一致」（状态行是元数据，条款字节未动）；修正后的值才是后续校验的基准。

**纪律（自本记录起）**：① pin **必须在冻结动作全部完成后**计算（含状态行、U-03 等元数据改动）；② 冻结后任何字节改动（含状态行）都必须**重算 pin 或走 UNFREEZE**；③ 建议同时记录 worktree sha256 与 `git cat-file blob`（LF）sha256 双口径。
## 8. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin（v5）、条件 4/4、D04 六项覆盖表、4 条实现铁律、3 条已知限制 | DSH |
| 2026-11-01 | pin 修正：原 pin 指向冻结前草案（状态行改动前），改为最终字节 `d2cb8de4dd79fb490e3e5c12a6aaad3e1a0bb294c217a79f083ecfeab683837c`；新增 §1A 修正记录与纪律（见上） | DSH |
