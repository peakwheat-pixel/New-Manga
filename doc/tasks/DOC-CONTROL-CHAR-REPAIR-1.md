---
id: DOC-CONTROL-CHAR-REPAIR-1
title: 修复 doc/tasks/** 的 C 风格转义控制字符损坏（65 文件 / 113 处）
kind: governance
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: ctrlchar-review-r3（独立上下文子 agent，APPROVED；r1/r2 为 CHANGES_REQUESTED）
integration_commit: 501264d09
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1 全量清点与判定**：113 处逐处判定，给出「位置 → 替换值 → 判定依据」；自动验证（还原后 token 在仓库词表或 git commit 可解析）覆盖 ≥80%，其余逐条人工判定。 <<MET>>
      结果：AUTO 102/113 = 90.3%、MANUAL 11；逐处判定表见 `verification/DOC-CONTROL-CHAR-REPAIR-1/`。
- [x] **AC2 零残留**：修复后 `doc/tasks/**` 的 `[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]` 命中数为 **0**。 <<MET>>
- [x] **AC3 语义保真**：只替换控制符所在字节，其余字节逐字不变；`git diff` 行数 == 受影响行数，且每行的差异仅为该控制符。 <<MET>>
      独立复核 r3 已做**全量逐字节重构**（637/637 文件与最终树吻合，未受影响行 100% 相同）。
- [x] **AC4 可 grep 性**：修复后 `grep -r "verification"` / `"apps/"` / `"frozen"` / `"vitest"` 在 `doc/tasks/` 下均能命中此前丢失的行。 <<MET>>
- [x] **AC5 无回归**：`check.ps1` PASS(3 warnings)｜`verify_pins.ps1` 18/18｜`generate_api_inventory.py --check` 1/80/6=87；AC 注释里的定位符（`verify_locators.py`）418/418 不受影响。 <<MET>>
- [x] **AC6 不可唯一判定项登记**：无法唯一判定 0 处（113/113 均有明确依据）；并新增完备性反查（`0x00` 候选集须含数字 `0`，用 `git cat-file -t` 反证错误值不是对象）。 <<MET>>
- [x] **AC7 独立复核**：三轮上下文独立复核（r1 CHANGES_REQUESTED→r2 CHANGES_REQUESTED→**r3 APPROVED**，P0/P1/P2/P3=0/0/0/3），被审 head `501264d09`；报告在 workspace 派生产物区，不入 Git。 <<MET>>

## 允许修改范围

见 frontmatter `allowed_paths`。要点：**只改 `doc/tasks/**` 中控制字符所在的那些字节**。

## 禁止范围

- **不得**改任何 AC 正文、`status`、frontmatter、注释内容；
- **不得**改 `src/**`、`tests/**`、`tools/**`、`verification/**`、`doc/` 下其它目录；
- **不得**借机重排、格式化或改写任何句子；
- **不得**对无法唯一判定的位置做猜测性替换。

## 判定方法

**损坏规律（独立复核 r1 确证）**：把**转义字母原位替换成对应控制字节**——
`v→0x0B`、`a→0x07`、`b→0x08`、`f→0x0C`、`e→0x1B`、**`0→0x00`**（数字零，不是字母 e）。

1. **映射**：`0x0B→v`、`0x07→a`、`0x08→b`、`0x0C→f`、`0x1B→e`、`0x00→0`；
2. **自动验证**：把候选替入后，取该位置的 ASCII token，检查它是否在
   （a）仓库文本 token 集合，或（b）`git cat-file -t` 可解析的 commit hash 中；
3. **人工判定**：自动验证不通过的 11 处逐条读上下文定夺；另 2 处「原文是两字节 `\a`」（`GOV-EVIDENCE-DIR-SWEEP-1.md:48/:56`，还原后路径 token 命中词表，故表中标 AUTO）；
4. **完备性反查（r1 后补）**：对 `0x00` 候选集必须包含数字 `0`，并用 `git cat-file -t`
   反证「错误值不是对象」（如 `e752fbad` 不是 commit，而 `0e752fbad` 是）。

> **r1 复核纠正**：初版把 `0x00` 映射成 `e`（以及 3 处判为删除），10 处全部判错。
> 复核以 `git cat-file -t` 证明正确值是 `0`；已全部修正，卡内映射同步改正。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| 零残留 | 扫描脚本 | 0 命中 |
| 差异最小 | `git diff --numstat` 逐文件 | 只含受影响行 |
| 可 grep | `Select-String -Path doc/tasks/*.md -Pattern "verification\|apps/\|frozen\|vitest"` | 命中 |
| 四件套 | check / pins / inventory | PASS / 18-18 / 1-80-6=87 |
| AC 定位符 | `verify_locators.py` | 全量行内命中 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-DCC-01 | AC1/AC2/AC3 证据总述 | verification/DOC-CONTROL-CHAR-REPAIR-1/README.md | 501264d09 | dcf814c7c772362d2479e55ac9a0430c7b331bf79b754b3ab27060fd17ea5173 | CANONICAL | BLOB |
| EV-DCC-02 | AC1 逐处判定表（113 行） | verification/DOC-CONTROL-CHAR-REPAIR-1/control-char-inventory.md | 501264d09 | a97b809d019432076ae7357fe12265ea0ab44b92410a02c27adc5407ee5b4947 | CANONICAL | BLOB |
| EV-DCC-03 | AC1 机器可读判定日志 | verification/DOC-CONTROL-CHAR-REPAIR-1/verify-final.log | 501264d09 | 9791df83435184c441765ff09a52640a60f7affbaa7e39a04dfa902cb0230c9a | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/DOC-CONTROL-CHAR-REPAIR-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-15，DSH（Lead / Architect / Integrator）；integration commit `501264d09`
  （实现 `9a0651e6e` + r1 返修 `93db15541` + r2 返修 `501264d09`）。
- **结果**：`doc/tasks/**` **65 文件 / 113 处**控制字符全部修复，**零残留**；
  判定表 113 行齐备，**AUTO 102（90.3%）/ MANUAL 11**。
- **独立复核三轮**（全部上下文独立 subagent）：
  - r1 `CHANGES_REQUESTED`（P0/P1/P2/P3=0/1/3/4）—— 抓出 **10 处 `0x00` 全部判错**
    （正确值是数字 `0` 而非 `e`，`git cat-file -t` 决定性证明）；
  - r2 `CHANGES_REQUESTED`（0/1/2/3）—— 抓出**入库判定表仍是初版**（树已对、证据表未跟上）、
    以及一次 edit 误删 AC1/AC2 换行导致 AC2 从门禁可见集消失；
  - r3 **APPROVED**（0/0/0/3）—— 全量逐字节重构 637/637 文件吻合，确认树未回退。
- **门禁**：`check.ps1` PASS (3 warnings)｜`verify_pins.ps1` PASS (18/18)｜
  `generate_api_inventory.py --check` OK (1/80/6=87)｜AC 注释定位符 418/418。
- **未关闭项（不淡化）**：
  1. `doc/tasks` 仍有**同类但不同族**的损坏未修——**33 个 TAB**（`\tsc`、`\test.ps1`、`\tokens.json` 等）、
     **20 个 CR**（如 `SCHEDULER-THREAD-DIAG-1.md:105` 的 `；\refresh()`）、**VT 断词**
     （`FEA-09.md:322/325`、`IMPORT-TRIAGE-1.md:47`）。本卡范围仅
     `[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]` 这一族，**不声称「所有词已恢复」**；需另立 Task。
  2. `doc/tasks/**` 之外（`doc/reviews/**`、`verification/**`）是否同类损坏**未排查**。
  3. 3 个文件在 git 中仍显示 binary（其 HEAD blob 含控制符），修复后工作区为合法 UTF-8。
  4. 覆盖率口径：说明见 README §2；严格「排除整个本任务证据目录」口径下为 86.7–88.5%，仍 ≥80%。
  5. 本卡为 out-of-plan Task（未登记 `REBASELINE_PLAN` DAG），故 `check.ps1 -TaskPath` 在标 `done` 前会报
     「当前 DAG 未登记非终态 Task」——标 `done` 后不再触发（同 `GOV-CHECKER-HISTORICAL-AC-EXEMPT-1`）。
