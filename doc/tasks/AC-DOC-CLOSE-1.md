---
id: AC-DOC-CLOSE-1
title: 闭合 DOC 类 blocked AC（第 1 批）并归因集成复验先存失败
kind: governance
governance_version: 3
status: in_progress
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - AC-BLOCKED-CLASSIFY-1
approval: 用户 2026-11-15「全部授权、持续自动推进」；目标 C「AC blocked 项中可归因闭合项」
base_commit: d99c1fba3
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/AC-DOC-CLOSE-1
allowed_paths:
  - doc/tasks/AC-DOC-CLOSE-1.md
  - doc/tasks/V11R-C-RESEARCH-1.md
  - doc/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/AC-DOC-CLOSE-1/**
---

# AC-DOC-CLOSE-1：闭合 DOC 类 blocked（第 1 批）

## 来源

`AC-BLOCKED-CLASSIFY-1` 判定 `DOC` 类 9 条（「需补文档/证据/登记，Agent 可做」）。
本卡执行第 1 批：补核验与集成复验证据，据实改判或如实归因。

## 目标（一个可观察结果）

1 条 `blocked` 因补到硬核验证据而改判 `verified`；
1 条 `blocked` 经实跑集成复验**确认仍失败**，理由更新为实测结果 + **先存缺陷归因**（不掩盖）。
并登记由此发现的仓库级技术债。

## Acceptance Criteria

- [ ] **AC1 `V11R-C-RESEARCH-1` AC5 改判**：用 `delivery_head: ba59a6c0d` 证明「0 个生产文件」，
      改判 `verified` 并把核验日志入库。
- [ ] **AC2 `GOV-RESIDUAL` AC7 如实归因**：实跑三命令（`test_residual_runtime_identity.py` /
      `check.ps1` / `git diff --check`）并记录真实 EXIT；若失败，**保持 `blocked`** 并写明
      失败项、期望值与实得值、以及是否本轮引入。
- [ ] **AC3 不引入新缺陷**：本轮新增证据文件不得让任何卡的 `-TaskPath` 多出错误
      （若新增文件放在某卡 `evidence_dir` 会触发「未登记文件」，须移到本卡证据目录或登记）。
- [ ] **AC4 技术债登记**：把集成复验暴露的仓库级声明错误（167 处）如实登记，供后续立卡。
- [ ] **AC5 不回归**：全局 `check.ps1` PASS；`verify_pins` 18/18；`api_inventory` 1/80/6=87；
      `verify_final.py` 计数从 188 verified / 66 blocked 变为 189 / 65。
- [ ] **AC6 独立复核**：固定 head 交独立上下文 Review。

## 禁止范围

- 不得为让集成复验「通过」而修改 `tools/governance/clean_workspace.py` 的判据或放宽检查；
- 不得修改 `verification/**` 下既有证据文件内容；
- 不得把失败的测试记成通过。

## 测试要求

| 场景 | 命令 | 期望 |
|---|---|---|
| V11R-C-RESEARCH 核验 | `git show --stat ba59a6c0d` | 10 个 doc 文件 / 0 生产文件 |
| 集成复验三命令 | 见 `verification/AC-DOC-CLOSE-1/gov-residual-integration-reverify.log` | 如实记录（当前 test 为 FAILED 3） |
| 四件套 | check / pins / inventory | PASS / 18-18 / 87 |

## 证据

核验日志、集成复验日志、167 处错误分布写入 `verification/AC-DOC-CLOSE-1/`。
