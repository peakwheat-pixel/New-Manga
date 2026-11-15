---
id: AC-DOC-CLOSE-1
title: 闭合 DOC 类 blocked AC（第 1 批）并归因集成复验先存失败
kind: governance
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: doc-close-review（独立上下文子 agent，APPROVED_WITH_LIMITATIONS）
integration_commit: c1f9d966b
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1 `V11R-C-RESEARCH-1` AC5 改判**：用 `delivery_head: ba59a6c0d` 证明「0 个生产文件」， <<MET>>
      改判 `verified` 并把核验日志入库。
- [x] **AC2 `GOV-RESIDUAL` AC7 如实归因**：实跑三命令（`test_residual_runtime_identity.py` / <<MET>>
      `check.ps1` / `git diff --check`）并记录真实 EXIT；若失败，**保持 `blocked`** 并写明
      失败项、期望值与实得值、以及是否本轮引入。
- [x] **AC3 不引入新缺陷**：本轮新增证据文件不得让任何卡的 `-TaskPath` 多出错误 <<MET>>
      （若新增文件放在某卡 `evidence_dir` 会触发「未登记文件」，须移到本卡证据目录或登记）。
- [x] **AC4 技术债登记**：把集成复验暴露的仓库级声明错误（167 处）如实登记，供后续立卡。 <<MET>>
- [x] **AC5 不回归**：全局 `check.ps1` PASS；`verify_pins` 18/18；`api_inventory` 1/80/6=87； <<MET>>
      `verify_final.py` 计数从 188 verified / 66 blocked 变为 189 / 65。
- [x] **AC6 独立复核**：固定 head 交独立上下文 Review。 <<MET>>

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

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-ADC-01 | AC1/AC2/AC3/AC4 证据总述（WORKTREE_ENV=Windows11+pwsh7+Python3.14） | verification/AC-DOC-CLOSE-1/README.md | c1f9d966b | 40f11617bc5b01e59e4355e52969f37bca9d2fa7dbf51a139e32b6511011e33b | CANONICAL | WORKTREE |
| EV-ADC-02 | AC1 V11R-C-RESEARCH 核验（0 生产文件）（WORKTREE_ENV=Windows11+pwsh7+Python3.14） | verification/AC-DOC-CLOSE-1/v11r-c-research-ac5-verify.log | c1f9d966b | 6ae8aa2888bbe0b6ac9ec3572483c6d98c724eb79dfdafabc5aa59668eef3898 | CANONICAL | WORKTREE |
| EV-ADC-03 | AC2 集成复验实测（3 failures / EXIT=1）（WORKTREE_ENV=Windows11+pwsh7+Python3.14） | verification/AC-DOC-CLOSE-1/gov-residual-integration-reverify.log | c1f9d966b | 1fb49a6a874e9867244ba27b7455a02d6697b051d822fa7b2f28ebf0ab7d4417 | CANONICAL | WORKTREE |
| EV-ADC-04 | AC4 声明错误分布（167 = 160 + 7 裁定身份）（WORKTREE_ENV=Windows11+pwsh7+Python3.14） | verification/AC-DOC-CLOSE-1/decl-error-distribution.log | c1f9d966b | 86138fe483aa46e3c3fbdc92c5e5a2c03907ec95ba653e181c95061adee21d37 | CANONICAL | WORKTREE |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/AC-DOC-CLOSE-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-15，DSH；实现 commit `c1f9d966b`。
- **结果**：
  - `V11R-C-RESEARCH-1` AC5 改判 `verified`（`delivery_head: ba59a6c0d` = 10 doc / 0 生产文件）；
  - `GOV-RESIDUAL` AC7 **保持 `blocked`**，理由更新为实测失败（`Ran 12 / FAILED 3 / EXIT=1`）+ 先存归因；
  - 新登记技术债：**160 处可清理 + 7 处裁定身份保留**（r1 P2-1 修正口径）。
- **独立复核**：`doc-close-review` verdict **APPROVED_WITH_LIMITATIONS**（0/0/1/5）：
  - P2-1（167 中 7 条是裁定身份，清理口径应为 160+7）→ README §4 与 AC7 注释均已改为该口径；
  - P3-1（「7→6」基线段落）→ 复核确认父提交即 6，7 只是中途瞬态，已在本 Closeout 澄清；
  - P3-2（TASK_LEDGER 三指标过期）→ 收口时重跑 `task_ledger.py --write`；
  - P3-3（`verify_final` EXIT=1 未披露）→ README §5 已补披露（8 条先存 numstat FAIL）；
  - P3-4/P3-5 记录在证据文档。
- **计数**：`verified 188 → 189`、`blocked 66 → 65`。
- **门禁**：`check.ps1` PASS (3 warnings)｜`verify_pins.ps1` PASS (18/18)｜
  `generate_api_inventory.py --check` OK (1/80/6=87)。
- **未关闭项（不淡化）**：
  1. `GOV-RESIDUAL` AC7 仍需先清理 **160 处**历史声明错误（保留 7 处裁定身份）才能通过；
  2. `V11R-C-RESEARCH-1` 仍有 4 条先存 `-TaskPath` 错误（缺 canonical evidence/integration_commit/
     Resource Manifest、EVIDENCE_BASIS_HEADER_INVALID），该卡是 lifecycle v2 且 frontmatter 不完整；
  3. `GOV-RESIDUAL` 仍有 6 条先存 `-TaskPath` 错误；
  4. 本卡自身 `-TaskPath` 因 DAG 未登记而 FAIL（表外卡既有边界，标 `done` 后消解）。
