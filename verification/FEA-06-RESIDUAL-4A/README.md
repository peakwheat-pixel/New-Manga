# FEA-06-RESIDUAL-4A 证据索引（C-07 additive UNFREEZE 前置）

- Task：`FEA-06-RESIDUAL-4A`（契约前置卡；`status: proposed`，未释放）
- base：`4cb24ed20556f85bbbe8c4a0ff9d34b6dbfcf65a`（main）
- 日期：2026-11-14
- 授权：[RO-1 重开裁决](../../doc/reviews/MAINT-1-RO-1-REOPEN-RESIDUAL-4-2026-11-14.md)（用户 2026-11-14 指令撤销 Q7 `OUT`，固定走 C-07 additive UNFREEZE）+ DSH 2026-11-14 对本卡两条口径的裁决（统计不提前翻转；授权一次 `task_ledger.py --write`）
- 日志生成口径：全部日志在**同一工作树、提交前**生成；产品字节（`src/**`、`apps/**`、`tests/**`）零改动，故日志与提交后字节等价。日志头行记录生成时 HEAD 与 `git status --short`。

## 结论状态

| AC | 判别 | 结果 |
|---|---|---|
| AC1 规格冻结 | 规格 v1 覆盖两层/字段/布局/交互/空态失败态/a11y + 可判别断言 | **PARTIAL**：规格 v1 已写入卡面 §「对照内容规格 v1（冻结候选）」，字段名/返回类型与 inventory 计划节逐字一致；「冻结」以独立 scope review 通过为准 |
| AC2 inventory 更新 | 计划节锁死名称/返回类型/#80；正式成员表 = 脚本 stdout 逐行一致 | **PARTIAL**：新增「RO-1 计划追加」节；成员表与 stdout **`ALL_MATCH: True`**（三接口全等），统计仍 `79 / 86` = 代码实测；80/87 翻转归 4B（v1.10，DSH 裁决口径） |
| AC3 pin 重算 | 新 pin 写入冻结记录 §1 置顶、前一 pin 原值保留、§1B/§2/§3/§5 同步 | **PARTIAL**：pin `8ccaba05…` → `91e51ab7…`；v1.8 原值保留于「前一 pin（v1.8，保留原值）」行；§1B 记为「独立复核 pending」 |
| AC4 载体 | 结构对齐同型先例 | **PARTIAL**：`doc/reviews/CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md` 已落盘，§6 复核记录为 `pending` |
| AC5 独立字节级复核 | 由 DSH 另派未参与写作的上下文 | **MET**：r1 `changes_requested`（P0=0/P1=2，记录层；`doc/reviews/FEA-06-RESIDUAL-4A-r1.md`）→ 处置（不触 inventory 字节）→ **r2 `approved`**（P0/P1=0；P2=2/P3=5 不阻断；`doc/reviews/FEA-06-RESIDUAL-4A-r2.md`，被审 head `756ab29e2`），C-07 v1.9 **已重冻** |
| AC6 门禁四件套 | 四项原始输出 + EXIT | **PARTIAL**：四项全 `EXIT=0`；台账经 DSH 授权重生成一次；零越界按卡面逐文件核对 |

## pin（完整 64 位）

| 项 | 值 |
|---|---|
| 前 pin（v1.8，本提交后作为「前一 pin」保留） | `8ccaba05cbc21eec04a366f8bfa2be2dea4515ba90e6d5aab95b11a7c47f0509` |
| 后 pin（v1.9） | `91e51ab74da201b99b6704e49fca96e93657d869dcc1e9523661dbb299c6d750` |
| 旧 pin 可复现性 | `git show 4cb24ed20:doc/plan/FEA-C07_API_INVENTORY.md`（v1.9 的父提交，**不可用 `HEAD`**——提交后 HEAD 指向新 pin）→ CRLF→LF 归一后 SHA-256 = `8ccaba05…` ✅ |
| 冻结记录声明 = 工作树 SHA-256 | `True`（`logs/pin-before-after.log` 的 `pin_matches_file`） |
| 文件字节变化 | `git diff --numstat` = **+18 / −2**（LF，13,040 B） |

## 门禁四件套（原始输出：`logs/gates-2026-11-14.log`）

| # | 命令 | 结果 |
|---|---|---|
| 1 | `pwsh -NoProfile -File tools/governance/check.ps1` | `Governance check: PASS (3 warnings)` / **EXIT=0** |
| 2 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-06-RESIDUAL-4A.md` | `Governance check: PASS (3 warnings)` / **EXIT=0** |
| 3 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`；C07=`91e51ab74da2` / **EXIT=0** |
| 4 | `python tools/generate_api_inventory.py --check` | `OK: rendered counts match FEA-C07 doc`；`1/79/6 = 86` / **EXIT=0** |

三条警告均为既有预算/台账提示（`STATUS` 3177 B、`PLAN` 6954 B、8 个非终态 Task），非本卡引入。

## 脚本 stdout 与逐行比对

- `logs/api-inventory.log`：`python tools/generate_api_inventory.py` 全量 stdout（105 行）+ `--check`，两个命令均 `EXIT=0`。stdout 计数：`IReaderProgressSink 1 / IHostController 79（+4 非方法成员）/ IRunController 6 = 86`。
- `logs/member-table-eq-stdout.log`：正式成员表 vs stdout 逐行比对，`IReaderProgressSink ALL_MATCH=True`、`IHostController 83 行 ALL_MATCH=True`、`IRunController ALL_MATCH=True`、`RESULT=PASS`（EXIT=0）。**这是 AC2「逐行一致」的判别证据**；`--check` 只比计数行，不能替代本项（v1.6 起纪律）。
- `logs/pin-before-after.log`：旧/新 pin 复现 + `verify_pins` 原始输出。

## 本提交范围（`git add` 显式路径，未用 `-A`）

| 路径 | 变更 | 说明 |
|---|---|---|
| `doc/tasks/FEA-06-RESIDUAL-4A.md` | 新增 | 本卡（含规格 v1、AC、R-1…R-5、Resource Manifest） |
| `doc/reviews/CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md` | 新增 | UNFREEZE 载体（§1 变更范围 / §2 为什么必须 UNFREEZE / §3 计划节 / §4 门禁 / §5 复核要求 / §6 复核记录 pending / §7 不构成什么） |
| `doc/plan/FEA-C07_API_INVENTORY.md` | +18/−2 | 状态行/生成日期行注记 + 「RO-1 计划追加」节 + §关系 补一条 |
| `doc/plan/FEA-CONTRACT-FROZEN-C07.md` | 改 | §1 pin 链（新行置顶 + v1.8 保留）、§1B、§2 条件 1/3/4、§3、§5 变更行 |
| `doc/TASK_LEDGER.md` | 机械重生成 | `task files 599→600`、`non-terminal 7→8`、`untracked 0`；经 DSH 2026-11-14 显式授权执行一次 `python tools/governance/task_ledger.py --write` |
| `verification/FEA-06-RESIDUAL-4A/**` | 新增 | 本 README + `logs/`（4 份原始证据） |

**范围外（不纳入本提交）**：`tests/fea11/test_source_match.py` 有 DSH 并行的 `custom_rank` 夹具修复（`MAINT-1` DoD §4 事项），本卡不读不改不提交。

## 未做 / NOT_RUN（不得记 PASS）

- **独立字节级复核 NOT_RUN**：AC5 `pending`，须 DSH 另派未参与本卡写作的上下文；本卡不写「复核通过」。
- **统计 80/87 NOT_DONE**：按 DSH 裁决与脚本机制（计数由源码解析）在 4A 不可达，属 4B 落地（pin v1.10）。
- **产品代码 / UI / 测试 NOT_RUN**：`src/**`、`apps/**`、`tests/**` 零改动；「查看对照」面板与端口实现属 `FEA-06-RESIDUAL-4B`。
- **`FEA-06` AC3 NOT_FLIPPED**：仍为 `PARTIAL`，直到 4B 集成验证通过。

## 已知限制（登记，非本卡引入）

- `doc/plan/FEA-C07_API_INVENTORY.md` 在 `.gitattributes` 无 `eol=lf` 规则，而仓库 `core.autocrlf=true`；`git diff` 会提示「LF will be replaced by CRLF」。即 pin 在**本工作树（LF）**可复现，fresh clone 若检出 CRLF 则不可复现。该限制对 v1.8 及更早 pin 同样成立；修法（增 `.gitattributes` 规则）不在本卡 `allowed_paths`，交 DSH。

## 复现

```powershell
python tools/generate_api_inventory.py --check
pwsh -NoProfile -File tools/governance/verify_pins.ps1
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-06-RESIDUAL-4A.md
python tools/governance/task_ledger.py --diff   # 只读核对台账是否与 doc/tasks/*.md 一致
(Get-FileHash -Algorithm SHA256 doc/plan/FEA-C07_API_INVENTORY.md).Hash.ToLower()
```
