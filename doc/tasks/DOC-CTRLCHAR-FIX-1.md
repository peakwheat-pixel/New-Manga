---
id: DOC-CTRLCHAR-FIX-1
title: 修复 doc/tasks 控制字符损坏（33 处 TAB 实为被吃掉的字母 t、20 处孤立 CR）
kind: governance
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on: []
approval: 用户 2026-11-15「全部授权」；目标 C「doc/tasks 控制字符损坏修复」
base_commit: 819298e99
branch: main
worktree: G:/CODEX/New Manga
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

- [ ] **AC1 性质核实**：确认 33 处 TAB 是 `t` 而非空白（逐处上下文列出）。
- [ ] **AC2 TAB 修复**：全部还原为 `t`，残留 0。
- [ ] **AC3 孤立 CR 修复**：全部删除，残留 0。
- [ ] **AC4 无意外改动**：`git diff --stat` 增删对称。
- [ ] **AC5 不破坏 pin**：`verify_pins` 仍 18/18；四件套 PASS。
- [ ] **AC6 独立复核**：固定 head 交独立上下文 Review。

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

修复前后统计、diff 抽样、备份位置写入 `verification/DOC-CTRLCHAR-FIX-1/`。
备份保存在 `G:\CODEX\New Manga.workspace\tasks\DOC-CTRLCHAR-FIX-1\pre-fix\`（656 文件）。
