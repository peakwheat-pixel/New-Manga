# FEA-CONTRACT-WRAP-1 收口核验记录

采集时间：2026-11-01（本 Task 收口提交前）
采集者：DSH（Lead / Integrator）
性质：**只读命令的实跑记录**，供复核对照；不替代独立复核。

## 1. 治理命令实跑

| 命令 | 结果 |
|---|---|
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (2 warnings)**，EXIT=0；WARN = 11 个非终态 Task、STATUS 达 80% 预算 |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-CONTRACT-WRAP-1.md` | PASS（同上 2 warnings），EXIT=0 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (all 13)**，EXIT=0；13 个 pin 值自 L-3 Errata 起未变 |

## 2. 预算实测（AC2）

| 文件 | 压缩前 | 压缩后 | 预算/阈值 |
|---|---|---|---|
| `doc/REBASELINE_PLAN.md` | 6777 B / 57 行 | **2257 B / 32 行** | 7000 B / 64 行；80% = 5600 B / 51 行 |
| `doc/PLAN-HISTORY.md` | 4132 B / 41 行 | 9504 B / 79 行 | 无预算；**新增 38 行、删除 0 行**（31 行终态节点原样迁入 + 7 行标题/说明） |
| `doc/STATUS.md` | 3157 B / 32 行 | 3157 B / 32 行 | 3200 B / 45 行；80% = 2560 B / 36 行 |

`git diff --numstat doc/PLAN-HISTORY.md` = `38	0`（**纯新增**，无删改）。

## 3. L-3 Errata 链接与行号核对（AC1 增补判据）

- **链接可解析**：5 个被注记文件（`GATE-CLOSURE-RULING-2026-11-01.md`、`FEA-CONTRACT-FROZEN-C04b.md`、`-C08.md`、`-C09.md`、`-C13.md`）的全部相对链接按文件所在目录解析 → **死链 0**（含 D07 解环改 `../tasks/FEA-D07-UNBLOCK.md` 后的 2 处）。
- **行号正确**：`GATE-CLOSURE-RULING` `:63`= C-09 不会提前解锁、`:111`= C-09 仍 blocked、`:112`= 保持 OPEN；C04b §3、§4；C08 §4 `:55`、§6 `:65`；C13 §5 `:62-63`、§7 `:74`；C09 §5 `:68`、§6 `:74` —— 逐条 `Select-String` 复核一致（追加未改变既有行号）。
- **与裁定 §4 逐行对齐**：裁定 §4 的 5 行处置对象全部有对应注记；**C-08 一行属「裁定表里有、文件里没有」**（该记录全文不含 D07 表述），已在 C-08 §8 注记写明核对结论，并记录「裁定 §4 括注指向落空」而不改裁定正文。

## 4. 冻结字节

`git diff` 于 13 个受 pin 契约文件（12 份 `FEA-C*_DRAFT.md` + `FEA-C07_API_INVENTORY.md`）= 空；`verify_pins.ps1` 13/13。C-13 草案 `:203` 保持原字节。

## 5. 指针一致性

| 权威 | 内容 |
|---|---|
| `doc/STATUS.md` 当前 Task | `FEA-CONTRACT-WRAP-1` `in_progress` |
| `doc/REBASELINE_PLAN.md` 当前 DAG | 含 `FEA-CONTRACT-WRAP-1`（in_progress）、`FEA-C10-DRAFT`（approved，未冻结）、FEA-C14/D06（done） |
| `doc/TASK_LEDGER.md` | 由 `task_ledger.py --write` 重新生成，计数与磁盘一致 |
