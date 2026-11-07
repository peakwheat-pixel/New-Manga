# FEA-12-CORE-C04B-RESIDUAL-2：C-04b v1.2 + M2-C1 rev 2.15 — 证据（EV）

> 本 EV 只陈述**实改/实跑**事实。本卡是**契约 UNFREEZE 卡**：只改 C-04b/M2-C1 的**措辞与谓词文字** + 冻结记录/矩阵/载体，
> **不改任何规则、字段名、错误码、能力、wire minor、`PROTOCOL_MINOR`、schema、依赖**；**R-1 的代码实现不在本卡**（归
> `FEA-12-CORE-C04B-RESIDUAL-3`）。**不得**写「8 项 residual 全部关闭 / R-1 已修复」。

- Task：`doc/tasks/FEA-12-CORE-C04B-RESIDUAL-2.md`（`base_commit=d91d9b6cc`；`status` 由 Lead 维护）
- 载体：`doc/reviews/CONTRACT-UNFREEZE-2026-11-08-C04B-RESIDUAL.md`
- 依据：`doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md`（§2 八项事实、§3.3 UNFREEZE 行/句与 pin 口径）；
  上游登记 `doc/plan/FEA-CONTRACT-FROZEN-C04b.md` §4A `R-1…R-8`（由 `FEA-12-CORE-C04B-RESIDUAL-1` 建立）
- 环境：Windows 11 / PowerShell 7 / Python 3.14；无新依赖；无 schema/wire 变更

## 1. 最终字节与 pin

| 项 | 实测值 |
|---|---|
| C-04b `doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md`（v1.2） | SHA-256 `4b304c0c315fe8ec4ae86544590919329c27234ead2b3ad9357b2e99a2d54e52`；blob `a30e4080116d01512977eca40de1c43ea7244a64` |
| M2-C1 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（rev 2.15） | SHA-256 `a82a7fc1e2c8dafeda977c26b68f140e9cecd8061f88692d4624858fc5046e0e`；blob `cb8eeb21279ff3dd23ad7c1cec6c171b211592e9` |
| 冻结记录 pin（C-04b） | `FEA-CONTRACT-FROZEN-C04b.md` §1 = 同上（v1.2 行；v1.1/v1.0 历史 pin 保留） |
| M2-C1 登记 | 冻结记录 §1B/§4C + 载体 §7 三处 = 同上（**M2-C1 不在 18 pin 映射，0/18 机械 pin**） |
| `verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**（C-04b 新值；其余 **17 实测不变**） |

## 2. 变更清单（文字级）

**C-04b v1.2（`git diff --numstat` = 26 插入 / 15 删除）**：状态行/日期行（v1.2）；§0 新增 v1.2 摘要块（v1.1 摘要
标题降为 `###`）；**R-1** §0 第 1 条 + §2.1 DTO 补 `media_artifacts.book_id = 本书`；**R-3** 删 `separate/detached`
+ 写死 representative 规则（阅读序首个 lineage-visible region current，否则首个 artifact current pointer；仅展示、不进 digest）；**R-8** §0 第 4 条 + §2.2 manifest 补单条取值；
**R-4** §1 表现状表 6 处行号 → 节名；**R-2** §2.0 末段改「不得在同一请求内混用两种 digest 语义」；**R-5** §2.2
校验顺序「预览 `book_ids`」→「**请求** `book_ids`」、§2.2 首次确认补单条来源 `inventoryDigests[bookId]`；§6 变更记录 v1.2。

**M2-C1 rev 2.15（`git diff --numstat` = 11 插入 / 7 删除）**：`:18` 新增 rev 2.15 段（2.14 原文保留）；`:30` history
增 `2.15` 行；§5.11.1a 标题 `rev 2.14`→`rev 2.14/2.15`；§5.13 标题 `C-04b v1.1`→`v1.2` + rev；来源行补单条
`inventoryDigests[bookId]`；校验顺序行「预览」→「请求」；retry 行标注「集合级仅批量」；`:953` 删 `separate/detached`；
`:954` 补成员谓词 `media_artifacts.book_id = 本书` + representative 规则。

**记录/矩阵**：冻结记录 §1 pin + §1B v1.2 行 + §2 条件 7（复核前 ⏳）+ 新增 §4C + §4A「v1.2 状态更新」append-only
+ §5 变更记录 v1.2；矩阵状态行补 C-04b v1.2、第 4 行 → `FROZEN v1.2`。

## 3. 零漂移（实测，见 `logs/`）

| 检查 | 结果 | 日志 |
|---|---|---|
| 契约面（除本卡两契约/两记录） | **零 diff** | `logs/other-contracts-drift.log` |
| `src/**`、`apps/**`、`tests/**` | **零 diff** | `logs/code-drift.log` |
| 无新命令/字段/错误码/能力/wire minor/`PROTOCOL_MINOR`/schema/依赖 | 人工核对 §2 清单无新增项 | 本 EV §2 |

## 4. 门禁（实跑）

| 项 | 命令 | 结果 | 日志 |
|---|---|---|---|
| pins | `verify_pins.ps1` | **PASS (all 18)** | `logs/pins.log` |
| check（默认） | `check.ps1` | **PASS (3 warnings)** | `logs/check.log` |
| check（-TaskPath） | `check.ps1 -TaskPath doc/tasks/FEA-12-CORE-C04B-RESIDUAL-2.md` | **PASS (3 warnings)** | `logs/check-taskpath.log` |
| 指纹 | `Get-FileHash` + `git hash-object` | 与预期全等 | `logs/sha-check.log` |
| diff 规模 | `git diff --numstat` | C-04b `26/15`、M2-C1 `20/16` | `logs/diffstat.log` |
| diff 全文 | `git diff` | 见 `unfreeze.diff` | `unfreeze.diff` |
| 全量 pytest/.NET | — | **NOT_RUN**（纯文档；零 `src/**`/`tests/**`/`apps/**` 改动） | — |

## 5. 独立 byte-level 复核

- **r1 `changes_requested`（P0=0/P1=2/P2=1/P3=4）** → 返修 → **r2 `changes_requested`（P0=0/P1=1/P2=2/P3=2）** → 再返修（P1-1 artifact pointer 规则）；**r3 待派**（`doc/reviews/FEA-12-CORE-C04B-RESIDUAL-2-r3.md`；reviewer = fresh subagent、未参与起草；
  只读两契约 + 记录 + 矩阵 + 载体；结论与 P0/P1/P2/P3 见该报告与冻结记录 §2 条件 7 / §4C）。

## 6. 不构成什么

- **不构成** R-1 的**代码**修复：`library.py:1178-1190` 仍为 page/chapter join → **L-3 仍有效**、**未修**（归 RESIDUAL-3）；因此 **R-1 侧契约与实现当前不一致**（这是 RESIDUAL-3 的存在理由），**不得**说「本包全部文字与实现一致」。
- **不构成**「8 项 residual 全部关闭」：R-6 已闭合、R-7 已由 rev 2.15 banner/history 落地、R-1/R-2/R-3/R-4/R-5/R-8 的
  契约文字已改，但 R-1 代码未改。
- **不构成**任何规则/字段/错误码/能力/wire/schema 变更；不构成删除协议语义变更；不构成 push 授权（Lead 统一）。

## 7. 复现（repo root；工作树含未提交 UNFREEZE 包时）

```powershell
(Get-FileHash -Algorithm SHA256 doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md).Hash
(Get-FileHash -Algorithm SHA256 doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md).Hash
git hash-object doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md
git diff --numstat -- doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
pwsh -NoProfile -File tools/governance/verify_pins.ps1
pwsh -NoProfile -File tools/governance/check.ps1
```
