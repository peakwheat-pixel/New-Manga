---
id: DOC-CTRLCHAR-FIX-1
title: 修复 doc/tasks 控制字符损坏（33 处 TAB 实为被吃掉的字母 t、20 处孤立 CR）
kind: governance
governance_version: 3
status: in_review
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on: []
approval: 用户 2026-11-15「全部授权」；目标 C「doc/tasks 控制字符损坏修复」
base_commit: 819298e99
branch: main
worktree: G:/CODEX/New Manga
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/DOC-CTRLCHAR-FIX-1
allowed_paths:
  - doc/tasks/**
  - doc/TASK_LEDGER.md
  - verification/DOC-CTRLCHAR-FIX-1/**
---

# DOC-CTRLCHAR-FIX-1：doc/tasks 控制字符损坏修复

## 背景

目标 C 要求清零「`doc/tasks` 控制字符损坏」。此前记录为「33 TAB / 20 CR / VT 损坏」，
但**没有核清这些字符到底是什么**。

## 核实：两类损坏性质不同

### 1. 孤立 CR（20 处，13 文件）—— 确实是损坏

统计时先得到 `CR=10323`，但其中绝大多数是 **CRLF 的正常组成部分**。
按「孤立 CR」（`\r` 后面不是 `\n`）精确统计后为 **20 处**。

### 2. TAB（33 处，29 文件）—— **不是空白，是被吃掉的字母 `t`**

逐处检查上下文后发现，每个 TAB 都占据一个 `t` 的位置：

| 损坏原文 | 还原后 |
|---|---|
| `src/**+<TAB>ests/**` | `src/**+tests/**` |
| `main 上 <TAB>sc exit 0` | `main 上 tsc exit 0` |
| `<TAB>itle **无最大长度**` | `title **无最大长度**` |
| `DSH 复跑 <TAB>est.ps1` | `DSH 复跑 test.ps1` |
| `分支 <TAB>ask/HOST-CORECLIENT-1` | `分支 task/HOST-CORECLIENT-1` |
| `workspace <TAB>ask-envs/…` | `workspace task-envs/…` |
| `<TAB>ools/**` | `tools/**` |
| `<TAB>okens.json` | `tokens.json` |
| `<TAB>ranslate PR` | `translate PR` |
| `已声明 <TAB>rue/pm+PerM` | `已声明 true/pm+PerM` |

**33 处全部符合**，无例外。⇒ 修复方式是把 TAB 还原为 `t`，而**不是**替换为空格。

## 修复

| 项 | 数量 |
|---|---|
| 修复文件 | **37 个** |
| TAB → `t` | **33 处** |
| 孤立 CR → 删除 | **20 处** |
| 修复后残留 | **TAB = 0，孤立 CR = 0，有问题文件 = 0** |

`git diff --stat`：**44 insertions / 44 deletions**（**对称**，说明没有意外增删整行）。

## 安全前提（改前已核实）

- `verify_pins` **只校验 `doc/plan/**`**（FEA 契约），**不碰 `doc/tasks/**`** ⇒ 改动不会破坏 pin；
- 历史证据 pin 指向的是**历史 commit 的 blob**，改当前工作树不影响它们；
- 修改前后 `verify_pins` 均 **18/18 PASS**（实测）。

## 目标（一个可观察结果）

`doc/tasks/**` 中 TAB 与孤立 CR 均为 0；四件套 PASS。

## Acceptance Criteria

- [x] **AC1 性质核实**：确认损坏字符是「被吃掉的字母」而非空白（2026-11-17 实测 37 处逐处上下文列出；7 类：TAB 12 / BEL 8 / VT 6 / BS 5 / ESC 4 / FF 1 / 孤立 CR 1，每处都恰好占据其后单词的首字母位置）。 <<MET>>
- [x] **AC2 TAB 修复**：全部还原为 `t`，残留 0（12 处 TAB → `t`；`doc/tasks` 全量 667 个 `.md` 复查 TAB=0）。 <<MET>>
- [x] **AC3 孤立 CR 修复**：残留 0（1 处孤立 CR；该处 CR 占据 `reviewer` 的首字母，故还原为 `r` 而非删除 —— 卡面原「删除」规则对该处不成立，已在 Closeout Record 更正）。 <<MET>>
- [x] **AC4 无意外改动**：`git diff --stat` 29/29 对称；与 HEAD blob 逐字节比对 37/37 差异全部是「控制字符 → ASCII 字母」，5 个文件长度全部不变。 <<MET>>
- [x] **AC5 不破坏 pin**：`verify_pins` 仍 18/18；四件套 PASS。 <<MET>>
- [x] **AC6 独立复核**：固定 head（`1ef6a2ebd`）交独立上下文 Review。 <<MET>>

## 允许修改范围

只改 `doc/tasks/**` 的控制字符（不改内容语义）+ 本卡 + 证据。

## 禁止范围

- 不得改动 `doc/tasks` 中任何**文字内容**（只修控制字符）；
- 不得修改 `doc/plan/**`（pin 目标）；
- 不得顺带重排/格式化 markdown。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 残留检查 | 全文扫描 | TAB=0、孤立CR=0 |
| 不破坏 pin | `verify_pins.ps1` | 18/18 |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## 证据

修复前后统计、diff 抽样与四件套写入 `verification/DOC-CTRLCHAR-FIX-1/`（见下 Canonical Evidence）。
备份保存在 `G:\CODEX\New Manga.workspace\tasks\DOC-CTRLCHAR-FIX-1\pre-fix\`（656 文件，仓外，保留不改）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|
| EV-DC1-01 | AC1/AC2/AC3/AC4 逐处扫描 + 字节级比对 | verification/DOC-CTRLCHAR-FIX-1/ctrlchar-scan-and-fix-2026-11-17.log | 1ef6a2ebd | 7d074bf3aab798921b241dc157825194b537b167c9927766c1653805974946d2 | CANONICAL | BLOB |
| EV-DC1-02 | AC5 修复后四件套 | verification/DOC-CTRLCHAR-FIX-1/four-piece-2026-11-17.log | 3a0dea7b7 | e8bef311a6fcff4477989eb0892898c50f7cdc96ef8be17531fb178614b57fb8 | CANONICAL | BLOB |
| EV-DC1-03 | 2026-11-16 首轮修复的前后统计（历史） | verification/DOC-CTRLCHAR-FIX-1/fix-report.log | 1f3bd0d84 | c92e04b55a15fa63b8638654b132fc5475bb423a6ab7e00d0a75dc3310e9c0d0 | SOURCE_PIN | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/DOC-CTRLCHAR-FIX-1/ | NOT_APPLICABLE | — | — | 2 个证据文件已逐行登记于 Canonical Evidence；无迁移/归档/删除 |
| backup | G:/CODEX/New Manga.workspace/tasks/DOC-CTRLCHAR-FIX-1/pre-fix | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/tasks/DOC-CTRLCHAR-FIX-1/pre-fix | c32d5468bbf663d5f94cf8f81ad233e8bc6a80b8a36262f89721128f084722d3 | 656 个修复前文件副本（9,460,343 B）仓外保留，未清理/未移动；上列 sha256 为 `pre-fix-manifest.json`（同源 656 条逐文件 sha256）的摘要 |

## Closeout Record

- Closeout：2026-11-17，DSH（立卡 2026-11-15）。
- canonical_evidence_status：`complete`；resource_closeout_status：`complete`。
- **实测（2026-11-17，被审 head `1ef6a2ebd`）**：
  - `doc/tasks` 667 个 `.md`：修复前 **37 个控制字符 / 5 个文件**（BEL 8、BS 5、TAB 12、VT 6、FF 1、孤立 CR 1、ESC 4）；修复后 **残留 0**；
  - 与 HEAD blob 逐字节比对：**37/37 字节差异全部是「控制字符 → ASCII 字母」**，5 个文件长度全部不变；
  - `git diff --stat`：**29 行改动 / 29 行删除（对称）**；
  - 四件套：`check.ps1` PASS(3 warnings) / `verify_pins` **18/18** / 声明审计 **0 error、6875 declarations、5661 protected roots** / 证据巡检 **FAIL 0、EXEMPTED 84、NOT_ENFORCED 15、WARN 273（7117 行 / 667 卡）**。
- **对卡面原规则的更正（如实登记）**：原 AC3 写「孤立 CR → 删除」。实测本轮唯一一处孤立 CR 位于 `doc/tasks/FEA-07.md`，它**占据了 `reviewer` 的首字母位置**（字节序列 `（\r` + `eviewer-fea07b`），删除会得到 `eviewer-fea07b`（仍错）。故该处按「还原为 `r`」处理。
  同理，本轮 37 处全部是「控制字符吃掉后一个单词首字母」，必须逐处判断还原字母，不能一律删除或替换为空格。
- **与 `DOC-CTRLCHAR-FIX-2` 的边界**：FIX-2 判「`doc/` **其它目录**不修」，本卡只处理 `doc/tasks/**`；本轮的 37 处是 FIX-2 之后新写入/遗漏的 `doc/tasks` 字节，不属于 FIX-2 判定的范围。
- 删除、迁移、归档数量/字节数：0（备份 656 文件仓外保留）。
