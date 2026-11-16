---
id: GOV-DECLARATION-SCAN-CLEANUP-1
title: 声明扫描债务清理（HIE P22 漂移 + 159 条历史声明 + 绝对计数不变量）—— 解除 GOV-RESIDUAL AC6/AC7 的 BLOCKED
kind: governance
governance_version: 3
status: proposed
approval: 2026-11-16 独立书面裁决（doc/reviews/GOV-RESIDUAL-AC7-ADJUDICATION-2026-11-16.md §2(c) 判为唯一推荐主路径）；待 DSH 三项 Ruling A/B/C
suggested_owner: DSH
owner: null
reviewer: null
depends_on: []
base_commit: 517072586
branch: main
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-DECLARATION-SCAN-CLEANUP-1
allowed_paths:
  - doc/tasks/GOV-DECLARATION-SCAN-CLEANUP-1.md
  - doc/tasks/GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1.md
  - doc/reviews/GOV-DECLARATION-SCAN-CLEANUP-1-*.md
  - doc/handoffs/GOV-DECLARATION-SCAN-CLEANUP-1-handoff.md
  - tools/governance/historical-evidence-interpretation.json
  - tools/governance/clean_workspace.py
  - tools/governance/tests/**
  - tools/governance/residual-runtime-identity.json
  - verification/GOV-DECLARATION-SCAN-CLEANUP-1/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# GOV-DECLARATION-SCAN-CLEANUP-1：声明扫描债务清理

## 来源与目标

`GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` 的 **AC6 / AC7 双 BLOCKED**，
根因经 2026-11-16 独立书面裁决（`doc/reviews/GOV-RESIDUAL-AC7-ADJUDICATION-2026-11-16.md`，
裁决者 `adjudicator-decl`，34943 B，被审 head `517072586`）定位为**三层阻塞**，
且三层**全部在本卡范围之外**，因此必须另立本卡：

| 层 | 内容 | 关键位置 |
|---|---|---|
| **L1** | **冻结政策漂移**：`tools/governance/historical-evidence-interpretation.json` 把 `verification/P22/codex-p22-task-r4-malformed-snapshot-7ebd7d40.md` 绑定为 **untracked**，但提交 `ee755d4bb`（2026-10-22「406-file evidence backlog」）把它入库成 **tracked** ⇒ 产出唯一一条 `SOURCE_DRIFT`；而 `clean_workspace.py:1986-1988` 见 HIE 政策错误就让 residual 层**整段早退**（7 条裁定身份未降级、APPDATA 三根未注册、residual warning = 0） | `historical-evidence-interpretation.json:233-235`；`clean_workspace.py:1986-1988` |
| **L2** | **历史声明债务**：交付后新增 **154** 条声明错误（`errors` 167 = 7 裁定身份 + 154 新增 + 6 交付前既有）；`clean_workspace.py:2172` 的 `len(index.errors) == 7` 因此不成立 ⇒ `ERROR_MISMATCH`，`:2206-2211` 只追加错误、`:2148` 的 `pending_protective` 全丢 | `clean_workspace.py:2172-2173,2148,2206-2211` |
| **L3** | **结构性绝对计数耦合**：`:2172` 的 `len(index.errors) == 7` 与 `:2189` 的 `require(not staged.errors)` 把「residual 层可应用」绑到「全仓错误**恰好** 7 条」。仓库只会继续增长 ⇒ 任何新卡新增一条声明错误都会再次击穿（已实际发生一次）。且与同卡 **AC5 `:50`「不以绝对计数为断言，遵守 r2 口径条款」自相矛盾** | `clean_workspace.py:2172,2189` |

**一个可观察的交付结果**：在**不修改任何历史卡/历史证据/`RESOURCE-MANIFEST.json` 字节**、
**不缩小保护集合**、**不动 7 条 residual 绑定（RRI-01…RRI-07）**的前提下，使
`python -B tools/governance/tests/test_residual_runtime_identity.py` 达到 **12/12 passed / EXIT=0**，
`--audit-declarations` 的 `errors` 归零（`DECL_RESIDUAL_RUNTIME_PRESERVED` warning 恒为 7）、
`protected_roots` 不小于基线 5582，并让保护索引**重新包含真实 APPDATA 的 `catalog`/`data`/`derived` 三根**。

## 前置：DSH 三项 Ruling（未出裁定前不得进入实现）

裁决报告 §2(c) 明确：**不做 Ruling A，后面全白做**。

- **Ruling A（跟踪状态语义）** —— `ee755d4bb` 让 P22 快照 tracked 化，与冻结 HIE 绑定（untracked 形态）冲突。三选一：
  (i) 更新 HIE 绑定到 tracked 形态并**重批** `HISTORICAL_EVIDENCE_DIGEST`（须同时核验 P09/P14 等绑定仍匹配）；
  (ii) 恢复 untracked（`git rm --cached`，保留工作区字节）——与「406-file backlog」的入库决策正面冲突，需说明为何反悔；
  (iii) 重新设计绑定为 **tracking-agnostic**（推荐评估）。
- **Ruling B（159 条历史声明债务分类口径）** —— 逐条归入
  **B1**「历史形态，可由解释层绑定为非声明/已保全」（如 53 条旧式 Canonical Evidence 缺 `path` 列 ⇒ 对应实测
  608 张终态卡中 225 张无 `## Canonical Evidence` 节的结构性历史形态）；
  **B2**「真实缺陷，需修数据但不得毁 pin」（必须先确认该件是否仍被**活 pin** 引用）；
  **B3**「扫描器规则误报，需单独裁定规则」。
  **判定口径必须先冻结再实施**，否则就是「为清零而清零」。
- **Ruling C（持久化不变量是否重写）** —— 是否把 L3 的绝对计数耦合改为**相对不变量**。
  按 `doc/09_COLLABORATION.md` §4.4，必须先在**不动生产**的前提下产出：受影响全集
  （`clean_workspace.py:2172`/`:2189`/`:2191-2195`/`:2840` 的调用面）、代表性/边界样本实测、基线错误矩阵；
  **核验结果与假设不符则假设作废**。若不做 C，清理完成当天 audit 会绿，下一张卡再红（已发生过一次）。

## Acceptance Criteria

- [x] **AC1 Ruling 落盘**：A/B/C 三项各有一份 DSH 书面裁定（落 `doc/reviews/`，署名与依据齐全）；Ruling C 若涉及不变量重写，须附 §4.4 要求的「受影响全集 + 基线错误矩阵」实测。 <!-- verified: 2026-11-16 DSH。**落盘**：`doc/reviews/GOV-DECLARATION-SCAN-CLEANUP-1-RULING-ABC-2026-11-16.md`（署名 DSH / Lead；依据 = `GOV-RESIDUAL-AC7-ADJUDICATION-2026-11-16.md` §2(c) 主路径 + 本轮实测）。**Ruling A = 方案 (i)**：更新 `HIE-O03.expected_tracking` 到 tracked + 重批 `HISTORICAL_EVIDENCE_DIGEST` （`3f4cae13…4b7d` → `5cc68358…aadd`）。否决 (ii) 的理由：`git rm --cached` 会反悔 `ee755d4bb` 的 406 文件入库决策，方向是反的（**应让政策追上事实，而非让事实退回政策**）；否决 (iii) 的理由：去掉/放宽 `expected_tracking` 会把真实的 fail-closed 检查削弱成 fail-open。**字节保留论证**：实测 4 条绑定的 `raw_sha256` 全部仍匹配 ⇒ 改的是治理政策与常量，**不是证据产物**，与裁决报告 §2(a) 否掉的「改历史卡/证据字节」不是同一件事。**Ruling B = 按 error code 冻结三分类**（B1 历史形态 64 / B2 真实缺陷 86 / B3 规则误报 16，合计 166），并写死两条硬约束：先冻结归属表再实施、B2 修数据前须实测是否被**活 pin** 引用（被引用者只登记不修）；未决点 `TABLE_SCHEMA_INCOMPLETE` 归 B1 的解释空间已诚实登记。**Ruling C = 批准重写为「成员不变量」**：保留 `len(removed) == 7`，把 `len(index.errors) == 7` 换成「7 条裁定错误身份必须全部存在」的三元组成员检查，缺任何一条仍 `ERROR_MISMATCH`（**fail-closed 不变**），并删除对全仓错误总数的依赖；`:2189`/`:2191-2195` 两条保持不变（R13 已为其补负例）。**§4.4 两项实测已附**：(a) 受影响调用面 —— 精确形式 `len(index.errors) == 7` 全仓仅 `:2172` 一处，其余 `len(index.errors)` 均为报告/日志，`_apply_residual_runtime_identity` 生产调用点全仓仅 `:2303` 一处；(b) 基线错误矩阵 —— 167 条按 code 分解（`TABLE_SCHEMA_INCOMPLETE` 53 / `DECL_RELATIVE_UNRESOLVED` 27 / `DECL_ENV` 20 / `DECL_GLOB` 16 / `DECL_DESTINATION_UNRESOLVED` 12 / `TABLE_DELIMITER` 10 / `DECL_UNKNOWN_DISPOSITION` 10 / `DECL_TRAVERSAL` 7 / `FILE_UNREADABLE` 4 / 其余 8 / `SOURCE_DRIFT` 1），`declarations=6729`、`protected_roots=5582`、`warnings=721`。**Ruling A 已同轮执行并验证**：`SOURCE_DRIFT` 1→0、`POLICY_INVALID` 0→1→0（发现并消掉 `:1848-1850` 的**硬编码第二真值**）、`ERROR_MISMATCH` 0→1（L3 暴露）、`protected_roots` 5582 未缩小、`verification/**` 与 `doc/tasks/*` 零字节改动。证据 file:verification/GOV-DECLARATION-SCAN-CLEANUP-1/ruling-a-l1-execution-2026-11-16.log。 -->
      Ruling C 若涉及不变量重写，须附 §4.4 要求的「受影响全集 + 基线错误矩阵」实测。
- [ ] **AC2 L1 修复（HIE P22 漂移）**：按 Ruling A 处置后，`--audit-declarations` 不再产出
      `SOURCE_DRIFT`；且 residual 层**不再早退**（`DECL_RESIDUAL_RUNTIME_PRESERVED` warning 数 = 7、
      APPDATA `catalog`/`data`/`derived` 三根重新出现在保护索引中）。
      须核验 P09/P14 等既有绑定未被破坏。
- [ ] **AC3 L2 清理**：159 条逐条给出 disposition（B1/B2/B3 + 依据 + **是否被活 pin 引用**），
      按 B1/B2/B3 分批处置；`errors` 单调下降至 **0**，`protected_roots ≥ 5582`（不得缩小）。
      逐条处置表必须与 `--audit-declarations` 的 JSON 一一对得上。
- [ ] **AC4 L3 不变量**（若 Ruling C 批准重写）：`clean_workspace.py` 的「恰好 7 条」耦合改为相对不变量；
      **补上「保护集合回退」负例**（构造回退触发 `PROTECTION_REGRESSION` 的 fail-closed 用例）——
      该负例同时是 `GOV-RESIDUAL` AC6 的唯一缺口，本 AC 完成即可回填 AC6。
- [ ] **AC5 不碰历史字节（硬约束，可机械核验）**：`git diff` 中**不得**出现 `doc/tasks/*`（除本卡与
      `GOV-RESIDUAL` 卡）、`verification/**` 下历史文件、任何 `RESOURCE-MANIFEST.json` 的字节改动；
      `tools/governance/residual-runtime-identity.json` 的 RRI-01…RRI-07 身份**逐字节不变**。
- [ ] **AC6 集成复验 + 独立复核**：固定 head 交**上下文独立** Reviewer（2026-10-31 口径；作者可派子 agent）；
      回填前后两轮 `--audit-declarations` JSON（baseline/after）；测试日志含命令/EXIT/解释器头
      （`09_COLLABORATION.md:359` 证据纪律）；`check.ps1` PASS、`git diff --check` EXIT=0。
      完成后**回填 `GOV-RESIDUAL` 的 AC6/AC7** 并恢复其 `status`。

## 允许修改范围

见 frontmatter。核心仅两处生产文件：
`tools/governance/historical-evidence-interpretation.json`（政策绑定 + digest）与
`tools/governance/clean_workspace.py`（digest 常量、以及 Ruling C 批准时的不变量代码）。

## 禁止范围

**以下四条是硬禁止，任一违反即整卡作废**（依据：裁决报告 §2(a)/§2(c)、`AGENTS.md:27/:32`、
`doc/09_COLLABORATION.md:112-113/234`、`GOV-RESIDUAL` 卡 `:62-68`）：

1. **禁止**修改任何历史卡、历史证据、`RESOURCE-MANIFEST.json` 的**字节**。
   实测反例：`FEA-11-RENDITION-1.md:198` 的 EV-7 pin 的 `RESOURCE-MANIFEST.json` sha256 **当前完全匹配**，
   改其中 2 条错误即**毁掉活 pin**。
2. **禁止**改 7 条 residual 绑定（`tools/governance/residual-runtime-identity.json:10-190` 的 RRI-01…RRI-07）。
3. **禁止**用「按错误码/前缀/正则整体忽略」的方式清零（本卡前身 `:66` 已禁；且是 r208 失败模式重演）。
4. **禁止**缩小保护集合，**禁止**放宽/删断言让测试变绿（绿洗）。
   实测反例：只放宽 `test_residual_runtime_identity.py:154` 后 `:157` 仍红
   （prod 与屏蔽 residual 层均 `errors=167 / protected=5582`，`assertGreater(5582,5582)=False`）。

## 拆分建议（强烈建议，避免单卡既改政策又改数据）

| 子卡 | 内容 | 规模 |
|---|---|---|
| **A 卡** | Ruling A 的 HIE P22 漂移修复（含 digest 重批 + P09/P14 绑定核验） | 1 天级 |
| **B 卡** | Ruling B 的 159 条分类与处置（B1/B2/B3 分批） | 多天级 |
| **C 卡** | Ruling C 的不变量重写 + 「保护集合回退」负例（顺带解 `GOV-RESIDUAL` AC6） | 3–5 步 |

## 附带发现（本卡不处理，但必须登记，勿丢）

- **R-1（治理缺口，当前生效）**：现 head 的保护索引里**没有** 3 个真实用户数据根，
  `GOV-RESIDUAL` AC3 的保护保证在真实扫描中**未成立**。缓解事实：`clean_workspace.py:2840-2864` 在
  `index.errors` 非空时整体 `REFUSED`（fail-closed，**无数据删除风险**），但治理清理工具当前**完全不可用**。
  产品侧删除保护由另一套 `ProtectionPolicy`（`src/application/maintenance/ports.py:190`、
  `src/bootstrap/core_service.py:2045`）承担，**未验证**其受影响。
- **R-2（可移植性缺陷，独立于 167）**：政策 `historical-evidence-interpretation.json:128-141/:165-178` 与
  `tools/governance/tests/test_residual_runtime_identity.py:29` 把用户路径**硬编码**为
  `C:/Users/49745/...`。换用户/机器时，即便全仓 0 声明错误，`require_present` 也会
  `RESIDUAL_TARGET_MISSING` ⇒ scan 永久红、测试永久红。
  ⇒ **建议单独立小卡**裁决「机器绑定的历史身份如何跨机表达」（在现政策「不展开环境变量/不通配」的禁令下，
  需 DSH 给出新形态，例如「语义路径 + 本机化绑定 + 显式跨机 fail-closed 说明」）。
- **EV-03/EV-04 可复现性疑点（裁决报告 §6）**：冻结证据声称 `errors=7→0`，
  但 `GOV-UNTRACKED-BACKLOG-1.md` 在 `d4ac54525` 与 HEAD 的 blob 完全相同（`576f3a5c…`），
  其 `:141` 的 `CON` 行在当前扫描产生 `DECL_BARE_NAME`，而该规则在 base/delivery 版 scanner 中已存在
  ⇒ 按同一 scanner+字节逻辑交付时也应有该错误，与冻结证据冲突。
  **本卡 phase 0 须用 `git archive d4ac54525` 重建基线复核**。

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC2 | `python tools/governance/clean_workspace.py --audit-declarations --out <dir>` | 仓库 | NOT_RUN | 待填 |
| AC2 | `python -B tools/governance/tests/test_residual_runtime_identity.py` | 仓库 | NOT_RUN | 待填 |
| AC3 | 同上（baseline/after 两轮） | 仓库 | NOT_RUN | 待填 |
| AC4 | 同上 + 新增回退负例 | 仓库 | NOT_RUN | 待填 |
| AC5 | `git diff --name-only` / `git diff --check` | 仓库 | NOT_RUN | 待填 |
| AC6 | `pwsh -NoProfile -File tools/governance/check.ps1` | 仓库 | NOT_RUN | 待填 |
