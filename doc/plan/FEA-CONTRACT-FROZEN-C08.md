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
| 版本 | **v4**（r8 复核 approved） |
| sha256（冻结后最终字节） | `37586fb2bfd2a2725d2851ca4db6f12533679eea18f22358f9ae144441bc78a9` |

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
- **D06 现在有承载契约** → `G-DELETE-CONTRACT` 的 D06 覆盖完成（D04=C-13、D05=C-06、D07=C-04b 亦有）。
- **Gate 仍不自动关闭**：D05 的剩余子面（重定位/同步、容器页映射）**无承载条款**；C-09 条件③（两 Gate 关闭）**仍不满足**。
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
| 差异原因 | 冻结动作本身把状态行从 `DRAFT` 改为 `FROZEN`，而原 pin 在**该改动之前**计算 → pin 指向冻结前的草案字节，未覆盖最终文件 |

**为什么保留原值**：pin 是证据，不能静默替换。原值证明「条款内容与冻结前一致」（状态行是元数据，条款字节未动）；修正后的值才是后续校验的基准。

**纪律（自本记录起）**：① pin **必须在冻结动作全部完成后**计算（含状态行、U-03 等元数据改动）；② 冻结后任何字节改动（含状态行）都必须**重算 pin 或走 UNFREEZE**；③ 建议同时记录 worktree sha256 与 `git cat-file blob`（LF）sha256 双口径。
## 7. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin（v4）、条件 5/5、协议注册块②、依赖与后果、2 条已知限制 | DSH |
| 2026-11-01 | pin 修正：原 pin 指向冻结前草案（状态行改动前），改为最终字节 `37586fb2bfd2a2725d2851ca4db6f12533679eea18f22358f9ae144441bc78a9`；新增 §1A 修正记录与纪律（见上） | DSH |
