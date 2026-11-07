# FEA-11-L-R11-GATE-UNIFY-PREREQ-1：C-16 v1.7（§2.4「无 publication 行」口径澄清）— 证据（EV）

> 本 EV 只陈述**实跑**事实；未跑项目逐项标注。本卡是**契约 UNFREEZE 卡**：只改 C-16 §2.4 的口径句 +
> 冻结记录/矩阵/载体，**不实现** L-R11（实现归 `FEA-11-L-R11-GATE-UNIFY-1`）。**不得**把本卡写成
> 「L-R11 已修复 / C-17 §3.3 已实现 / 读面行为已改变」。

- Task：`doc/tasks/FEA-11-L-R11-GATE-UNIFY-PREREQ-1.md`（`base_commit=3945e1f5c`；`status` 由 Lead 维护）
- 载体：`doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-L-R11.md`
- 依据：独立 scope review `doc/reviews/L-R11-GATE-UNIFY-scope-r1.md`（session `5aa2c0cf…`，recommended，
  方案 C，**1/18 pin**）；C-17 §3.3（`:171-173`，零字节）；RENDITION-1 `:159`（L-R11 登记）
- 分支/环境：main；Windows 11 / PowerShell 7 / Python 3.14；未建 worktree；无新依赖；无 schema/wire 变更

## 1. 最终字节与 pin

| 项 | 值 |
|---|---|
| 契约文件 | `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`（v1.6 → **v1.7**） |
| 工作树 SHA-256（`verify_pins.ps1` 口径） | `67286eeca8cb2109f35445c6b925b03053c483293b1bdb19e56efdc9965b657d` |
| git hash-object（blob id） | `3cd9d2fbf79bd37b3fc35e1895efa1c75d2fc232` |
| blob 内容 SHA-256（LF 原始字节） | `67286eeca8cb2109f35445c6b925b03053c483293b1bdb19e56efdc9965b657d` |
| 冻结记录 pin | `FEA-CONTRACT-FROZEN-C16.md` §1 = 同上（三口径一致） |
| `verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**（C16 新值 `67286eec…`；其余 17 实测不变） |

## 2. 变更范围（byte-level）

`git diff --stat`（HEAD `07a7d746a` → 工作树）：

| 文件 | 变更 |
|---|---|
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` | **13 行变更（7+/6−）**：§2.4 per-page 授权匹配括注（`:90`）、§2.4 兼容句（`:93`）、§0 版本面行、头部状态/载体链接/日期、§10 冻结条件 ⑨ + 变更记录 v1.7 |
| `doc/plan/FEA-CONTRACT-FROZEN-C16.md` | 25 行变更：pin/版本/blob/§1B v1.6/v1.7 行/§2 条件 9/§11 重冻记录 |
| `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md` | 4 行变更：状态行 C-16 v1.6→v1.7；第 16 行 `FROZEN v1.7` + 复核 ⏳ + 下游实现卡 |
| 载体/卡/EV/日志 | 新增 |

**零漂移（实测）**：C-17/C-06/C-15/C-07/M2-C1 及其它 17 份契约 blob 零改动；`src/**`、`apps/**`、`tests/**`、
`tools/**`、`doc/contracts/**` 零 diff；无新错误码/命令/能力/wire 字段/TTL/`PROTOCOL_MINOR`/schema/依赖。

## 3. 语义（本卡改动内容）

- **§2.4 per-page 授权匹配**：由「无 publication 行按既有 open 处理」改为「**旧未参与同步且无 publication 行的
  v7 binding 按既有 open；新同步 binding 缺 publication 行属于损坏，fail-closed（C-17 §3.3），不得当作 legacy
  放行**」——与 C-17 §3.3 **语义一致**（按 scope review §7.2 `:290` 建议措辞；检测机制经 C-17 §3.3 引用；
  非逐字复制，措辞差异见复核 r1 P3-02）。
- **§2.4 兼容句**：由「两读面既有差异不属于本命令语义」改为「两读面判定由 **L-R11** 统一为同一谓词（本命令沿用，
  不引入第三套 gate 判定）」。
- 不改 wire 字段/命令集/能力/错误闭集/TTL/撤销语义/`PROTOCOL_MINOR=3`；C-17 零字节（它已冻结正确语义）。

## 4. 门禁（实跑）

| 项 | 命令 | 结果 | 日志 |
|---|---|---|---|
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (all 18)** | `logs/pins.log` |
| check（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)** | `logs/check.log` |
| check（-TaskPath） | 同上 + `-TaskPath doc/tasks/FEA-11-L-R11-GATE-UNIFY-PREREQ-1.md` | **PASS (3 warnings)** | `logs/check-taskpath.log` |
| diff | `git diff --stat`（3 文档） | 3 files / 29 insertions / 13 deletions | `logs/unfreeze-diffstat.log`、`unfreeze.diff` |
| 全量 pytest/.NET | — | **NOT_RUN**（契约-only；不碰 `src/**`/`tests/**`/`apps/**`；实现卡门禁承担运行时回归） | — |

## 5. 独立 byte-level 复核

- **r1 `approved`（P0=0 / P1=0 / P2=0 / P3=7，均非阻断）**：`doc/reviews/FEA-11-L-R11-GATE-UNIFY-PREREQ-1-r1.md`
  （reviewer = fresh subagent，独立上下文，未参与 C-16 v1.7 起草/前轮复核；session
  `9bc4c117-e171-48b6-8f13-582845d2e12f`；reviewed_head `07a7d746a`；reviewed worktree SHA-256 `67286eec…`）。
  核对：字节三口径一致；diff 仅 5 个允许 hunk（7+/6−）；18 契约 blob 仅 C-16 变化（其余 17/17 与 HEAD 相同）；
  pins 18/18；check PASS×2；`git diff --check` 0；语义方向成立；记录/矩阵一致；未夸大。
- **P3 处置**：P3-01 提交隔离 → 已执行（本 UNFREEZE 提交只 stage 本包）；P3-02 EV「逐字一致」→ 本 EV 已改
  「语义一致」；P3-05 卡面元数据（§11/AC 范围/base_commit）→ 已修；P3-06 载体 §3 完成式 → 已加「契约目标语义」
  限定；P3-07 `unfreeze.diff` 为 CRLF 快照 → 与实时 diff **CRLF 归一化后逐字节相同**（归一化 SHA-256
  `8ed9b80ee11ef0c82fe60985f68f48d834dc86e2dea6f45187d825a016226c55`），内容等价。P3-03（C-16 §0 `:17`
  范围歧义）与 P3-04（§10 ⑨ 完成式）**保持现状**（改字节需新 pin/复核），登记后续 UNFREEZE 候选。

## 6. 不构成什么

- **不构成** L-R11 实现或任何读面行为改变；**不构成**「C-17 §3.3 已实现」；**不构成** L-R11 关闭。
- **不构成**对其它 17 份契约的修改；不构成 wire/能力/错误码变更；不构成 push 授权（Lead 统一）。
- 契约就绪 ≠ 实现/产品可用：`FEA-11-L-R11-GATE-UNIFY-1` 仍需独立实现与 Review。

## 7. 复现（repo root；工作树含未提交 UNFREEZE 包时）

```powershell
git status --porcelain
git diff --stat -- doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md doc/plan/FEA-CONTRACT-FROZEN-C16.md doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
(Get-FileHash -Algorithm SHA256 doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md).Hash
git hash-object doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md
pwsh -NoProfile -File tools/governance/verify_pins.ps1
pwsh -NoProfile -File tools/governance/check.ps1
```
