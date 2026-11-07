# FEA-12-CORE-C04B-RESIDUAL-1：C-04b v1.1 residual 8 项记录收口（docs-only，0 pin）— 证据（EV）

> 本 EV 只陈述**实跑/实改**事实。本卡 **docs-only**：只改冻结记录与载体（追加/登记），**不改 C-04b/M2-C1
> 任何契约字节**、不改 `src/**`/`tests/**`/`apps/**`。**不得**写「契约已修复 / 8 项全部关闭」。

- Task：`doc/tasks/FEA-12-CORE-C04B-RESIDUAL-1.md`（`base_commit=28a2826af`；`status` 由 Lead 维护）
- 依据：`doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md`（recommended，docs-only 0 pin；8 项分类
  docs-only 1 / 契约措辞 6 / 代码+契约 1；精确 pin 口径 = C-04b 1/18 + M2-C1 仅记录型，非 2/18）
- 环境：Windows 11 / PowerShell 7 / Python 3.14；无新依赖；无 schema/wire 变更

## 1. 改动内容与位置

| 文件 | 改动 | 说明 |
|---|---|---|
| `doc/plan/FEA-CONTRACT-FROZEN-C04b.md` | +39/−2 行 | **§4A** 一行 residual 扩为 `R-1…R-8` 表（含位置/性质/影响/现行权威读法/需 UNFREEZE）+ 新增 **L-3**（R-1 代码偏差 limitation，未修）；**§1C** 新增（r1–r7 报告完整 sha256，闭合 R-6）；**§4B** 「五轮」→「r1–r6 CHANGES + r7 APPROVE」（相邻精度项，不计入 8 项 AC）；**§5** 变更记录追加 2026-11-07 行 |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md` | +14 行 | **§5F** 追加 errata（R-2/R-3/R-4/R-5/R-7/R-8 的现行权威读法 + R-1 指向 L-3 + R-6 已闭合）；**不改** §1–§5E 正文 |
| 本卡/评审/证据 | 新增 | — |

**零字节证明（实测）**：

| 项 | 实测 sha256 | 冻结记录值 | 一致 |
|---|---|---|---|
| C-04b `doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md` | `acc8f0e03d42fd574837cc556e9fa546ba355d7f45a5eefc7bd7b9fe8c16968f` | 同 | ✅ |
| M2-C1 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | `701093b5282228fdc791843146bf9459338e6ac1829ce3a801c72470fc938b7f` | 同 | ✅ |

- `git diff --name-only`（已跟踪）：仅 `doc/plan/FEA-CONTRACT-FROZEN-C04b.md`、`doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md` +
  Lead 指针（`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`）；**C-04b/M2-C1 契约文件零 diff**；`src/**`、`apps/**`、
  `tests/**` 零 diff。

## 2. AC 证据

- **AC-1（8 项表）**：见 FROZEN-C04b §4A `R-1…R-8`（8 行；位置按 `28a2826af` 行号；性质分类与 scope review §2 一致）。
- **AC-2（R-6/⑥ 闭合）**：FROZEN-C04b §1C 列出 r1–r7 报告绝对路径（仓外 workspace）+ 大小 + **完整 sha256** +
  reviewer/session（r2 session 未暴露，如实标注）；实测值：
  r1 `600da6aa…`（48,399 B）、r2 `2eae498f…`（87,408 B）、r3 `1b2fa41e…`（42,856 B）、r4 `b6bd2693…`（33,127 B）、
  r5 `02b30b52…`（34,683 B）、r6 `924847b9…`（30,007 B）、r7 `8af2d4f1…`（17,688 B）；r4–r7 与 §1B 已记 8 位前缀一致。
- **AC-3（③④ 0 pin 收口）**：载体 §5F 已写 `separate/detached` 无定义/现行不据此裁剪、representative=字典序最小
  artifact revision id（仅展示、不进 digest）、C-04b §1 行号为 v1.0 时点且现行以节名为准。
- **AC-4（① L-3）**：FROZEN-C04b §4A **L-3** 已登记 `library.py:1178-1190`（page/chapter join）vs `:1920-1926`
  （`book_id`）vs `:1218-1225`（`book_id`）；正常数据无影响、损坏行可能多/少绑定、**未修**、修复需 UNFREEZE+实现卡。
- **AC-5（②⑤⑦⑧ 权威读法）**：见 §4A R-2/R-5/R-7/R-8 + 载体 §5F 对应条目（契约字节未改；现行读法/实现取值；规范
  修复待 UNFREEZE）。
- **AC-6（门禁/不夸大）**：见 §3；closeout 记录须明确「仅 ⑥ 完全闭合；③/④ 的 0 pin 部分已登记；其余契约文本未改」。

## 3. 门禁（实跑）

| 项 | 命令 | 结果 | 日志 |
|---|---|---|---|
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (all 18)**（C04b `acc8f0e0…` 仍命中） | `logs/pins.log` |
| check（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)** | `logs/check.log` |
| check（-TaskPath） | 同上 + `-TaskPath doc/tasks/FEA-12-CORE-C04B-RESIDUAL-1.md` | **PASS (3 warnings)** | `logs/check-taskpath.log` |
| 契约 sha 核对 | `Get-FileHash` C-04b/M2-C1 | 与冻结记录一致（见 §1） | `logs/sha-check.log` |
| diff 范围 | `git diff --name-only` / `--stat` | 仅 allowed_paths + Lead 指针；契约字节零 diff | `logs/scope-changed.log`、`logs/scope-stat.log` |
| 全量 pytest/.NET | — | **NOT_RUN**（docs-only；零 `src/**`/`tests/**`/`apps/**` 改动） | — |

## 4. 独立 docs-only Review

- **r1**：`doc/reviews/FEA-12-CORE-C04B-RESIDUAL-1-r1.md`（reviewer = fresh subagent，独立上下文，未参与本卡起草；
  审工作树被审字节）→ 结论待回填（approved/changes_requested 与 P0/P1/P2/P3 见该报告）。
- 复核要求：8 项表与 scope review 一致；§1C sha 实测可复算；L-3 措辞如实（未修）；载体 §5F 不改正文；零字节
  （C-04b/M2-C1 sha 不变、pins 18/18）；不夸大。

## 5. 不构成什么

- **不构成**契约修复：C-04b/M2-C1 字节仍为 `acc8f0e0…`/`701093b5…`；8 项中仅 ⑥ 完全闭合，R-1/R-2/R-3/R-4/R-5/R-7/R-8
  的**规范修复仍待 UNFREEZE（另卡，未建立）**。
- **不构成** ① artifact 成员谓词的修复（L-3 未修；正常数据无影响、损坏行偏差保留）。
- **不构成**删除协议/ADJ-001/Gate 语义变更；不构成实现授权；不构成 push 授权（Lead 统一）。

## 6. 复现（repo root；工作树含未提交 docs 改动时）

```powershell
git diff --name-only
Get-FileHash -Algorithm SHA256 doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md
Get-FileHash -Algorithm SHA256 doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
pwsh -NoProfile -File tools/governance/verify_pins.ps1
pwsh -NoProfile -File tools/governance/check.ps1
```
