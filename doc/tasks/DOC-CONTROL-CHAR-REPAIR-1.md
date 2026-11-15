---
id: DOC-CONTROL-CHAR-REPAIR-1
title: 修复 doc/tasks/** 的 C 风格转义控制字符损坏（65 文件 / 113 处）
kind: governance
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - AC-CHECKBOX-AUTHORITY-1
  - GOV-CHECKER-HISTORICAL-AC-EXEMPT-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；由 AC-CHECKBOX-AUTHORITY-1 §7.8 登记
base_commit: 3fd3316ed
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/DOC-CONTROL-CHAR-REPAIR-1
allowed_paths:
  - doc/tasks/DOC-CONTROL-CHAR-REPAIR-1.md
  - doc/tasks/**（仅控制字符位置）
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/DOC-CONTROL-CHAR-REPAIR-1/**
---

# DOC-CONTROL-CHAR-REPAIR-1：修复卡面控制字符损坏

## 来源

`AC-CHECKBOX-AUTHORITY-1` §7.8 登记：`doc/tasks/**` 中 **65 个文件 / 113 处**含 C 风格转义泄漏——
`\v`→`0x0B`、`\a`→`0x07`、`\b`→`0x08`、`\f`→`0x0C`、`\e`→`0x1B`、`\0`→`0x00`，
使 `verification`、`apps`、`frozen` 等词不可 grep（被写成 `erification`、`pps`、`rozen`）。

## 目标（一个可观察结果）

`doc/tasks/**` 中**不再有控制字符**，且所有受影响的词恢复为可 grep 的原文；
**除控制符位置外零字节改动**。

## Acceptance Criteria

- [ ] **AC1 全量清点与判定**：113 处逐处判定，给出「位置 → 替换值 → 判定依据」；
      自动验证（还原后 token 在仓库词表或 git commit 可解析）覆盖 ≥80%，其余逐条人工判定。
- [ ] **AC2 零残留**：修复后 `doc/tasks/**` 的 `[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]` 命中数为 **0**。
- [ ] **AC3 语义保真**：只替换控制符所在字节，其余字节逐字不变；`git diff` 行数 == 受影响行数，
      且每行的差异仅为该控制符。
- [ ] **AC4 可 grep 性**：修复后 `grep -r "verification"` / `"apps/"` / `"frozen"` / `"vitest"` 在
      `doc/tasks/` 下均能命中此前丢失的行。
- [ ] **AC5 无回归**：`check.ps1` PASS(3 warnings)｜`verify_pins.ps1` 18/18｜
      `generate_api_inventory.py --check` 1/80/6=87；AC 注释里的定位符（`verify_locators.py`）不受影响。
- [ ] **AC6 不可唯一判定项登记**：若存在无法唯一判定的位置，保留原样并逐条登记（本轮预期 0）。
- [ ] **AC7 独立复核**：固定 head 交独立上下文 Review，报告落 workspace。

## 允许修改范围

见 frontmatter `allowed_paths`。要点：**只改 `doc/tasks/**` 中控制字符所在的那些字节**。

## 禁止范围

- **不得**改任何 AC 正文、`status`、frontmatter、注释内容；
- **不得**改 `src/**`、`tests/**`、`tools/**`、`verification/**`、`doc/` 下其它目录；
- **不得**借机重排、格式化或改写任何句子；
- **不得**对无法唯一判定的位置做猜测性替换。

## 判定方法

1. **映射**：`0x0B→v`、`0x07→a`、`0x08→b`、`0x0C→f`、`0x1B→e`、`0x00→e`（C 转义）；
2. **自动验证**：把候选替入后，取该位置的 ASCII token，检查它是否在
   （a）仓库文本 token 集合，或（b）`git cat-file -t` 可解析的 commit hash 中；
3. **人工判定**：自动验证不通过的 27 处逐条读上下文定夺，其中含 4 处「应为删除」与 2 处「原文是两字节 `\a`」。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 零残留 | 扫描脚本 | 0 命中 |
| 差异最小 | `git diff --numstat` 逐文件 | 只含受影响行 |
| 可 grep | `Select-String -Path doc/tasks/*.md -Pattern "verification\|apps/\|frozen\|vitest"` | 命中 |
| 四件套 | check / pins / inventory | PASS / 18-18 / 1-80-6=87 |
| AC 定位符 | `verify_locators.py` | 全量行内命中 |

## 证据

结果与逐处判定表写入 `verification/DOC-CONTROL-CHAR-REPAIR-1/`。
