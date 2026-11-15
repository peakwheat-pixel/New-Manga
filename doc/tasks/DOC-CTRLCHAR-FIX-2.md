---
id: DOC-CTRLCHAR-FIX-2
title: doc/ 其它目录控制字符 —— 逐处评估后判定「不修」，并记录两次失败的批量尝试
kind: governance
governance_version: 3
status: closed_with_limitations
suggested_owner: DSH
owner: DSH
reviewer: 未派（本卡为评估结论卡，不需实现复核）
depends_on:
  - DOC-CTRLCHAR-FIX-1
canonical_evidence_status: complete
resource_closeout_status: complete
approval: 用户 2026-11-15「全部授权」
base_commit: b631e2b24
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/DOC-CTRLCHAR-FIX-2
allowed_paths:
  - doc/tasks/DOC-CTRLCHAR-FIX-2.md
  - doc/reviews/GOAL-C-DEBT-AUDIT-2026-11-16.md
  - doc/TASK_LEDGER.md
  - verification/DOC-CTRLCHAR-FIX-2/**
---

# DOC-CTRLCHAR-FIX-2：`doc/` 其它目录控制字符评估（判定不修）

## 背景

`DOC-CTRLCHAR-FIX-1` 修的是 `doc/tasks/**`（33 处 TAB 还原为 `t`、20 处孤立 CR 删除）。
`GOAL-C-DEBT-AUDIT-1` 随后发现：**`doc/` 其它目录还有 16 个文件**有控制字符。

本卡评估这 16 个文件能否修。

## 结论：**不修**

四个理由：

### 1. 不阻塞任何 gate

`check.ps1` / `verify_pins` / `api_inventory` **都不扫控制字符**。
这些残余是**文档卫生**问题，不是功能或治理阻塞。

### 2. 性质是混合的，不能批量处理

逐处扫描（`verification/DOC-CTRLCHAR-FIX-2/scan.out`）后，控制字符分三类：

| 类别 | 例子 | 应否替换 |
|---|---|---|
| **字母丢失** | `分支 <TAB>ask/THEME-MACOS` → 应为 `task/` | ✅ 应还原 |
| **git status 输出** | `A<TAB>doc/contracts/M2-C1_T…`（`A`=added，TAB 是 git 原样分隔） | ❌ **不应改** |
| **表格/对齐分隔** | `032bb5ad1cf148<TAB>refs/heads/codex/…` | ❌ 不应改 |

而 `doc/handoffs/GOV-EOL-PIN-1-d19e74ab4.md` 的 6 处 TAB 在 `.gitattributes` 内容里
（`/text eol=lf      <TAB>doc/handoffs/…`），性质也不明。

### 3. 其中一个是 pin 目标

`doc/plan/FEA-CONTRACT-FROZEN-C09.md`（VT=1）在 `verify_pins` 的校验清单内。
改它会直接破坏 pin 审计（18/18 → 17/18），必须先用 git commit 重锚定。

### 4. 我的两次批量尝试都险些造成大范围误改（如实记录）

这是本卡决定不做的主要原因 —— **风险评估结果是不值得**。

#### 失败一：误改 781 个文件（已回滚）

我写了规则 `re.sub(r"\r\n(?=\r?\n)", "\n", text)`，本意是处理 `doc/handoffs/FEA-09-995d80ca5.md`
里的 `<CR><NL><CR><NL>` 空行。

**这条正则在 CRLF 文件里会匹配每一个空行**（空行 = `\r\n\r\n`，第一个 `\r\n` 后面就是 `\r\n`）。

结果：**781 个文件被改**，其中包含 `doc/plan/**`（pin 目标）与 `doc/templates/**`。
`git status` 显示 781 项后我立即 `git checkout -- doc/` 回滚，确认工作区干净、
`verify_pins` 仍 18/18、`doc/tasks` 上轮的修复不受影响（已提交）。

#### 失败二：单文件 106 行可疑改动（已回滚）

改成白名单版本后，`doc/handoffs/UPGRADE-LEGACY-LAYOUT-1-handoff.md` 只该改 1 处
（`CR -> r`），但 `git diff --stat` 显示 **106 行改动**。

原因未查明（可能是该文件混用 CRLF/LF，`read_bytes().decode()` 后写回改变了行尾结构）。
→ 再次全部回滚。

## 留下什么

| 项 | 状态 |
|---|---|
| `doc/tasks/**` 控制字符（33 TAB + 20 孤立 CR） | ✅ **已修**（`1f3bd0d84`，逐处确认全是 `t`） |
| `doc/` 其它 16 个文件 | ❌ **不修**（本卡判定） |
| 扫描脚本（可复现残余清单） | ✅ 保存在 `workspace/tasks/DOC-CTRLCHAR-FIX-2/scan.py` |
| 两次失败的完整记录 | ✅ 本文 §4 |

## Acceptance Criteria

- [x] **AC1 扫描完整**：16 个文件已逐处列出控制字符上下文（`scan.out`）。 <<MET>>
- [x] **AC2 分类**：区分「字母丢失」/「git status 分隔」/「表格分隔」三类。 <<MET>>
- [x] **AC3 pin 目标识别**：`doc/plan/FEA-CONTRACT-FROZEN-C09.md` 标记为禁止修改。 <<MET>>
- [x] **AC4 失败记录**：两次批量尝试（781 文件、106 行）如实记录并说明回滚方式。 <<MET>>
- [x] **AC5 决策理由**：明确「不修」的四条理由，且不是"做不到"而是"不值得"。 <<MET>>
- [x] **AC6 状态完好**：回滚后 `git status` 干净、`verify_pins` 18/18、`doc/tasks` 修复仍在。 <<MET>>

## 禁止范围

- 不得在未见专门裁决的情况下修改 `doc/plan/**`；
- 不得为了"数字好看"而批量替换混合性质的控制字符。

## 说明：为什么状态是 `closed_with_limitations`

本卡的"限制"就是那 16 个文件**没有修**。这不是遗漏，是评估后的决定 ——
写进 Closeout 让后来的读者知道"这里还有残余，且是故意留的"。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-DC2-01 | AC1/AC2 扫描明细（16 文件逐处上下文） | verification/DOC-CTRLCHAR-FIX-2/scan.out | 79c3f324c | 07c0c022d3dfa753ff5bb441edc289d53e3a268a80c67995c9962eac65a60d5a | CANONICAL | BLOB |
| EV-DC2-02 | AC4/AC6 失败记录与回滚后状态 | verification/DOC-CTRLCHAR-FIX-2/eval-report.log | 79c3f324c | 35ce498909f61d620b25bf748458db26729f8128fdf0cb582fa63745780266c3 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/DOC-CTRLCHAR-FIX-2/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-16，DSH。
- **结论：doc/ 其它 16 个文件的控制字符判定为「不修」**，四项理由见正文。
- **两次失败的批量尝试已完整记录**（误改 781 文件 / 单文件 106 行），两次均用
  git checkout -- doc/ 完整回滚，回滚后 git status 干净、erify_pins 18/18、
  doc/tasks 上轮的修复不受影响。
- **保留成果**：扫描脚本（可随时复现残余清单）、16 文件的逐处上下文（scan.out）、
  三类性质分类（字母丢失 / git status 分隔 / 表格分隔）。
- **本卡状态是 closed_with_limitations**：「限制」就是那 16 个文件没修 ——
  这是评估结论，不是遗漏。
