# C08 Run 快照 · 冻结记录

**契约**：`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md`
**冻结时间**：2026-11-01
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：[Gate 阻塞口径裁定 v7](GATE-CLOSURE-RULING-2026-11-01.md)（R-4 + [r8 复核](../reviews/GATE-CLOSURE-RULING-r8.md) pproved）+ [冻结矩阵](FEA-CONTRACT_FREEZE_MATRIX.md)

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md` |
| 版本 | **v5**（D06 四项已补；v6 正文；r10 核查后重冻） |
| sha256（冻结后最终字节） | `b509271cc56fbbb219e4d30c040f1df80018dc9fe5dca20dc8268dd988db38e5` |

## 1B. 冻结字节 vs 复核字节

| 项 | 值 |
|---|---|
| 最后一次独立复核 | **r10**：核查 6 项中 5 项通过；契约正文无需再改，仅记录/载体需同步（本轮已改） |
| 复核后到冻结的改动 | 前置（b）`:1119` 例外 + 变更记录 + 状态行 |
| 处置 | **已补复核**（[FEA-CONTRACT-BYTES-r1](../reviews/FEA-CONTRACT-BYTES-r1.md)）；v5 的 D06 四项经 r9（changes_requested → v6 处置）→ **r10 认定正文通过**；剩余为记录同步（本轮完成） |

**为什么必须有这一节**：冻结条件①是「独立复核通过」，若冻结字节 ≠ 复核字节，该条件在证据上不覆盖被冻内容。本节的目的是把差异显式化，而不是掩盖它。

## 2. 冻结条件逐条核验（5/5）

| # | C-08 §5 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核通过 | ✅ | r1（3 P1）→ r2 [approved](../reviews/FEA-GOV-7-r2.md)；R-4 处置后 [r8 复核](../reviews/GATE-CLOSURE-RULING-r8.md) pproved |
| 2 | C-01b 已冻结（顺序） | ✅ | [FEA-CONTRACT-FROZEN-C01b](FEA-CONTRACT-FROZEN-C01b.md) |
| 3 | 前置（a）C-05 与 C-04b 已冻结 | ✅ | [C05](FEA-CONTRACT-FROZEN-C05.md)、[C04b](FEA-CONTRACT-FROZEN-C04b.md) |
| 4 | 前置（b）协议注册（**R-4 降级为释放前置**） | ✅ | 方案已冻结在 §3；M2-C1 字节修订由独立 Task 在释放 Run 实现前完成 + 负向对照（host 白名单降级） |
| 5 | `check.ps1` PASS | ✅ | PASS（3 persistent warnings） |

## 3. 协议注册（块②，释放前置）

| 项 | 内容 |
|---|---|
| M2-C1 §5.5 | 命令表追加 PrepareRun/AcceptRun 两行 |
| 3 个新码 | RUN_STALE_PREVIEW(conflict/false) / RUN_PREVIEW_EXPIRED(conflict/false) / RUN_SNAPSHOT_INCOMPLETE(unavailable/true) |
| §8 | 新增「Proposed（未观察）」小节 3 行 + :1119 retryable 证据规则例外 + :1122 taxonomy 例外 |
| **host 投影层** | 新增 `allowedRunErrorCodes` 白名单：未注册码 → `category=unknown` + 安全短消息、**不重写 `code`**、不作 UI 分支依据 |
| wire 版本 | **minor 2.12**（DSH 批准） |
| 与 C-04b 共用 Task | **块②**（块①= C-04b 删除章节增量）；两段独立提交、AC 分包、上限 5 提交 |

**负向对照**：未扩 M2-C1 时，3 个新码必须被 host 投影**降级为 category=unknown**（不是拒绝——删除线有封闭 ErrorView，Run 线没有）。

## 4. 依赖与后果

- **上游**：C-01b、C-05、C-04b 均已冻结。
- **D06 覆盖状态（2026-11-01，v5 更新）**：本契约现覆盖 D06 六项声明**全部**——①preview 与发送同源 SC-R01 ②不可变内容 pin SC-R02 ③控制 pending 状态 SC-R06 ④真实完成口径 SC-R07 ⑤retry 快照来源 SC-R08 ⑥断线 receipt SC-R09。D06 条件**以 AC8 的完整覆盖检查为准**。
- **Gate 仍不自动关闭**：D06 已由本契约覆盖；`G-DELETE-CONTRACT` 的关闭须经 AC8 完整覆盖检查 + AC9 裁定（C-09 已解环并冻结，不再构成阻塞）。
- **实现**：FEA-03/FEA-13（Run 快照相关）释放需前置（b）完成 + C-11 建卡 + 独立 Review。

## 5. 已知限制

- **L-1**：preparedDigest 的 canonical JSON 定义已冻结，但**逐字段 wire 编码**留给块② Task。
- **L-2**：防抖/过期（≤10 分钟）为建议值，待实现实测。

## 6. 不构成什么

- 不构成实现授权；不构成 Gate 关闭；不构成远端 push 授权。

## 1A. pin 修正记录（2026-11-01，**保留原值**）

| 项 | 值 |
|---|---|
| 原 pin（**错误口径**） | `5864a098109212b8db9060253196738dcae2aff6bc646ab296a521677b6120e6` |
| 修正后 pin（最终字节） | `37586fb2bfd2a2725d2851ca4db6f12533679eea18f22358f9ae144441bc78a9` |
| 差异范围 | 冻结提交内**同时含前置（b）的 `:1119` retryable 证据规则例外 + 变更记录改写**（来源＝裁定 r7/r8 的复核建议） |

**为什么保留原值**：pin 是证据，不能静默替换。原值可独立复现（还原本次冻结动作后重算即得），因此证明冻结前的确切字节；修正后的值才是后续校验基准。

**冻结后补充（2026-11-01，FEA-D06-GAP）**：按 [CONTRACT-UNFREEZE-C08-2026-11-01](../reviews/CONTRACT-UNFREEZE-C08-2026-11-01.md) 新增 SC-R06…SC-R09 四项（D06 声明范围的剩余四项：控制 pending 状态 / 真实完成口径 / retry 快照来源 / 断线 receipt）。这是**冻结后的条款新增**，走 UNFREEZE 载体而非仅重算 pin；pin 已更新为 `2e7a5f2b…`。

**冻结字节 = 复核字节？** 见 §1B。

**纪律（自本记录起）**：
1. pin **必须在冻结动作全部完成后**计算（含状态行、U-03 等元数据改动）；
2. 冻结后任何字节改动（含状态行）都必须**重算 pin 或走 UNFREEZE**；
3. 建议同时记录 worktree sha256 与 `git cat-file blob`（LF）sha256 双口径；
4. **冻结提交本身不得含条款编辑**——最后处置必须在冻结**之前**的独立提交完成并经复核。



| 2026-11-01 | 冻结后补充（FEA-D06-GAP）：新增 SC-R06…SC-R09 四项，走 UNFREEZE 载体；pin 更新 | DSH |
## 7. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin（v4）、条件 5/5、协议注册块②、依赖与后果、2 条已知限制 | DSH |
| 2026-11-01 | pin 修正：原 pin 指向冻结前草案（状态行改动前），改为最终字节 `37586fb2bfd2a2725d2851ca4db6f12533679eea18f22358f9ae144441bc78a9`；新增 §1A 修正记录与纪律（见上） | DSH |
