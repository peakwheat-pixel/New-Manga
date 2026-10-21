---
id: GOV-DEBT-CLEANUP-2
title: 治理债逐项事实核对与资源证据闭环
kind: governance
governance_version: 2
status: closed_with_limitations
approval: user_decisions_recorded_2026-10-19; codex_scope_release_approved
suggested_owner: dsh
owner: dsh
reviewer: Antigravity
depends_on: []
base_commit: 75da8281b28c7c11f92518c63d4669b5cf3973e6
branch: agent/deepseek/GOV-DEBT-CLEANUP-2-governance-facts
worktree: G:\CODEX\New Manga.workspace\worktrees\GOV-DEBT-CLEANUP-2
integration_commit: 2636301fe5d6c33535f873aeb776c3e4beb5dd2d
delivery_head: e63d9324766db0d381bad24b3fc60a58048430e1
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/GOV-DEBT-CLEANUP-2
allowed_paths:
  - doc/tasks/
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/handoffs/
  - doc/reviews/
  - verification/GOV-DEBT-CLEANUP-2/
---

# GOV-DEBT-CLEANUP-2：治理债逐项事实核对与资源证据闭环

## 来源与目标

按用户 2026-10-19 四项裁决和 Codex 的第二轮逐项裁定，形成可复核的事实记录、资源 Manifest 补录及明确的阻塞标注。原始证据、历史 pin、未完成 AC、Task 状态和资源内容保持可追溯。本 Task 不是对历史验收或集成的追认。

主要只读来源：
- `verification/P09-GOVERNANCE-DEBT-20261019/user-decisions-20261019.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/codex-debt-ruling.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/codex-debt-ruling-r2.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/round5-eol-repin-record.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/sha-mismatch-evidence-chain.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/dangling-dag-facts.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/p02-ac3-branch-evidence-inventory.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/worktree-closeout-facts.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/evidence-dir-classification.md`
- `verification/P09-GOVERNANCE-DEBT-20261019/missing-manifest-resource-facts.md`
- `doc/09_COLLABORATION.md` §4.1 / §4.2 / §5；`doc/templates/TASK.md`。

## Acceptance Criteria

- [x] **AC1 — 102 条 SHA mismatch 只读分类与逐行结果。** 对 `sha-mismatch-evidence-chain.md` 的 102 行逐行记录 Task、行号/路径、声称 commit、旧 pin、raw/LF/CRLF 对比、工作区相对 HEAD 状态、分类和当前处置。78 行只记录 `pin_matches_at_commit` 及历史 pin 保留事实，不重钉；13 行只读追溯原始 pin 来源，记录查得来源或标 `BLOCKED_ORIGIN_UNVERIFIED`，不改 pin；11 行保留 dirty 原状，记录只读可得的 diff/stat、归属状态并标 `BLOCKED_PRESERVE_DIRTY`，不从工作区重钉。逐行核对 78 条 EOL-only 记录所含原/新值，不重复重钉。不得写回来源事实文件或历史 Review。
- [x] **AC2 — 29 个非终态 Task 的逐项暂缓记录。** 对 `dangling-dag-facts.md` 的 29 项各写一条只读 adjudication，至少记录 Task ID、现有状态、Plan/STATUS 指涉、tracked 状态、依赖/交付/集成事实及用户裁决。29 项全部记为暂缓且保持原状态与原 AC；10 个未入库文件保持 `UNREGISTERED_UNTRUSTED_SNAPSHOT`，不得 `git add`；本 Task 不把任何一项登记进 Plan。逐项记录不构成继续、取消、替代或历史化决定。
- [x] **AC3 — Plan 预算扩容裁决提案与记录。** 在本 Task evidence_dir 记录用户批准的唯一目标值 `7000 bytes / 64 lines`、当前规则 `2500 bytes / 35 lines`、来源裁决及其适用范围；确认本 Task 未改 Plan 预算值、未改 `tools/governance/check.ps1`，且本 AC 未改变 29 个 Task 对应的 DAG 节点集合。检查器中两个数值的实际修改单列后续治理维护 Task，须独立冻结范围、Review 并验证；该后续 Task 的 `allowed_paths` 必须含 `tools/governance/`。本 Task 若按释放协议登记自身 READY 节点，该单项登记由 Codex 管理，明确不属于 AC3 的 29 项节点登记。
- [x] **AC4 — P02 AC3 的 23 条 pin 只读状态记录。** 对固定分支上存在的 18 条及不存在的 5 条分别记录精确路径、固定 head、可核实的来源/head/hash 和状态；缺失项标 `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED`，保留原引用。分支内容不视为主线 Canonical Evidence 或已集成。不得合并分支、修改 pin、删除引用或把 `integration_status` 记成已证实。
- [x] **AC5 — 13 个 worktree 的只读保留清单。** 逐项记录 `worktree-closeout-facts.md` 已有的存在性、注册、HEAD、branch、dirty/untracked 计数及可取得的引用/安全事实；以 `PRESERVE_UNKNOWN` 或事实支持的保留 disposition 记录，不删除、移动或 prune。P14、P15-C1-FU2 的不可达 HEAD 与所有 dirty/untracked 内容均保留。RUN-IPC-1 未取得逐路径证据时明确标记未知，不推断其与 DONE 交付无关。
- [x] **AC6 — 七个 DONE Task 的 Manifest 事实补录。** 为 `FEAT-CREATE-1`、`FEAT-CREATE-2`、`FEAT-CREATE-3`、`FEAT-CREATE-4`、`FEAT-IMPORT-MULTI-1`、`P19-UI-FIX-1`、`P19-UI-FIX-2` 补齐有来源的 Resource Manifest。只读核实精确注册路径后，将 `FEAT-CREATE-2` frontmatter 的 `worktree: null` 更正为该路径，并在记录中保留原值、核实来源和更正日期；核实不到则不改该字段，标记 `BLOCKED_PATH_UNVERIFIED`。逐项记录实际存在的资源、HEAD/branch、dirty/untracked、引用及进程检查；未核实项保留并标 `PRESERVE_UNKNOWN`。补表和元数据更正均不改变 DONE 状态或任何 AC。
- [ ] **AC7 — 61 个 evidence_dir 文件的只读分类。** 对 `evidence-dir-classification.md` 中 61 项逐文件记录路径、候选分类、内容/AC 绑定核查、是否唯一最终证据及处理结论。只有证实文件是已释放 AC 的唯一最终证据时才可列入对应 Canonical Evidence；其余项仅记录为来源/过程或待核实项，不因文件名作结论。`.gitattributes` 与 `.gitignore` 只记录用途，保持原位且内容不改。不移动、删除或归档任何文件。
- [x] **AC8 — 未完成 AC 保留裁决记录。** 对来源中发现的每项未完成 AC 记录 Task、原文定位、原勾选状态和用户裁决“保留未完成”。不得勾选、删除、转移、改写 AC，或把未完成结论写成 PASS。该 AC 只记录裁决，不修改关联 Task 的 AC。
- [ ] **AC9 — 验证与交接。** DSH 提交逐项结果、canonical evidence、Resource Manifest 和固定 delivery head；Antigravity 对该固定 head 独立 Review；Codex 核对范围、Review、集成后验证和 closeout。保存治理检查与 `-TaskPath doc/tasks/GOV-DEBT-CLEANUP-2.md` 检查的完整命令、环境、stdout、stderr、退出码与时间；若预算上限导致检查失败，如实记 `FAIL/BLOCKED`，不得为通过检查修改规则。不得运行 AC 探针或产品测试。只有所有已释放 AC 有相应证据、独立 Review 通过、Codex 集成及集成后验证完成且资源 Manifest 闭环后才能由 Codex设为 `done`。

## 允许修改范围

- `verification/GOV-DEBT-CLEANUP-2/`：本 Task 逐项 adjudication、只读检查结果、来源 pin 和必要的 Resource Manifest。不得覆盖 `verification/P09-GOVERNANCE-DEBT-20261019/` 下任何现存文件。
- `doc/tasks/`：仅本 Task 文件及 AC6 指明的七个 DONE Task Manifest；其中 `FEAT-CREATE-2` 仅允许按 AC6 有证据的 `worktree` 元数据更正。不得修改这些 Task 的 status 或任何 AC。
- `doc/REBASELINE_PLAN.md`：仅 Codex 按释放生命周期登记/更新本 Task 自身所需的 DAG/READY 记录；不得登记本 Task AC2 所列 29 项或修改预算内容。
- `doc/STATUS.md`：仅 Codex 按释放生命周期记录本 Task 的运行/派发指针，不替换当前 Active Task，除非后续明确调度决定如此。
- `doc/handoffs/`：本 Task Handoff。
- `doc/reviews/`：Antigravity 对固定 delivery head 的独立 Review。

## 禁止范围与不做事项

- 不删 worktree、不移动 worktree、不运行 `git worktree prune`。
- 不合并 P02 AC3 分支或其他分支，不改任何历史/活动 pin，不将分支证据记为已集成。
- 不改任何 Task 状态，不改任何既有 AC 原文或勾选状态。
- 不登记 29 个非终态 Task；10 个未入库 Task 不执行 `git add`。
- 不复制、快照、归档、迁移、重写或删除 `C:/Users/49745/.dsh/storages/workspace.json`；只记录路径、存在性、大小和记录时点，文件本体留在原位。
- 不修改 `tools/governance/check.ps1`，不放宽任何检查规则。
- 不覆盖事实来源，不移动/删除仓外文件，不运行 AC 探针或产品测试。

## 测试与验证计划

| 场景/AC | 计划步骤 | 结果 | 证据 |
|---|---|---|---|
| AC1–AC8 | 只读逐项对照来源事实与新增记录；检查保留项无写回 | NOT_RUN | `verification/GOV-DEBT-CLEANUP-2/` |
| AC9 全局治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1`，保存 stdout/stderr/exit code | NOT_RUN | `verification/GOV-DEBT-CLEANUP-2/` |
| AC9 Task 检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-DEBT-CLEANUP-2.md`，保存 stdout/stderr/exit code | NOT_RUN | `verification/GOV-DEBT-CLEANUP-2/` |
| AC 探针/产品测试 | 不运行 | NOT_RUN | 不适用 |

## 依赖、风险与阻塞

- 用户四项裁决已记录；被暂缓的 29 个 Task、未完成 AC 和用户文件不得借本 Task 解锁。
- dirty、不可达 HEAD、缺失来源、未知引用或用户数据均保留；不能证明的逐项标记 `BLOCKED_*` / `MISSING_*` 并报告 Codex。
- 检查器预算数值维护是独立后续 Task，不是本 Task 的依赖性写入或隐含授权。

## 交付与运行记录

- Owner：DSH；Reviewer：Antigravity（不得自审）。
- Handoff：`doc/handoffs/GOV-DEBT-CLEANUP-2-<short-head>.md`，引用固定 delivery head。
- Review：`doc/reviews/` 下绑定精确 reviewed head 的 Antigravity Review。
- 实际命令、环境、输出、退出码、阻塞及未跑项逐项记录；不得把 NOT_RUN/BLOCKED 写成 PASS。

## Canonical Evidence

进入 `in_review` 前逐项登记 AC1–AC9 的当前判别力证据。原始事实文件仅作为来源引用，不复制或修改。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| DEBT-AC1 | AC1 | `verification/GOV-DEBT-CLEANUP-2/ac1-sha-rows.md` | `2636301fe` | `6bdc98d5be79e5be7cc002981ef57ad8cba4f2a8c1714202b50cdd260386f3f7` | `CANONICAL` |
| DEBT-AC2 | AC2 | `verification/GOV-DEBT-CLEANUP-2/ac2-deferred-tasks.md` | `2636301fe` | `5f2f410b60a959b9c55f6ea89ea15b033bab1fb4e229739eef8ea9edd1bcfc04` | `CANONICAL` |
| DEBT-AC3 | AC3 | `verification/GOV-DEBT-CLEANUP-2/ac3-budget-decision.md` | `2636301fe` | `0287ac3c083b1226e2598a589e7507c2ebf22f18c979a54f1e71c77e659bbf17` | `CANONICAL` |
| DEBT-AC4 | AC4 | `verification/GOV-DEBT-CLEANUP-2/ac4-p02-ac3-pins.md` | `2636301fe` | `73892ee7faea0c11288fa96aa1f74b832dbba65f8a12a76ad76c5157c7e77ccb` | `CANONICAL` |
| DEBT-AC5 | AC5 | `verification/GOV-DEBT-CLEANUP-2/ac5-worktree-preserve-list.md` | `2636301fe` | `e0c582a6a0f9391febae94511f1d3611d80606a10317a0bf4a729aa8f98d8594` | `CANONICAL` |
| DEBT-AC6 | AC6 | `verification/GOV-DEBT-CLEANUP-2/ac6-manifest-backfill.md` | `2636301fe` | `94d7df55b7d4a88502f9fcb21e6a90e1299c1549cce461c876f740634d2b5000` | `CANONICAL` |
| DEBT-AC7 | AC7 | `verification/GOV-DEBT-CLEANUP-2/ac7-evidence-dir-files.md` | `2636301fe` | `8ec36c265967a7f45443bfb71c4608cd11bafc8a4d119085bbd15b354a7a5393` | `CANONICAL` |
| DEBT-AC8 | AC8 | `verification/GOV-DEBT-CLEANUP-2/ac8-open-acs.md` | `2636301fe` | `fb61c70f2638f2b1b4d1bbdd3ae34ec1dc6bb620aabb4dca81eb25a2b20a4377` | `CANONICAL` |
| DEBT-AC9 | AC9 | `verification/GOV-DEBT-CLEANUP-2/ac9-governance-output.txt` | `2636301fe` | `f2db42f794f8185cc7a0f68cdf78d3a7ce80b2ddddb51151151dcf97a6ccd4a4` | `CANONICAL` |
| DEBT-FINDING | 发现项 | `verification/GOV-DEBT-CLEANUP-2/finding-checker-not-tracked.md` | `2636301fe` | `a7a60f5c5df55bd5c99af0fab3422090f9136524ffb3bb21c93136e4fd05cd8f` | `CANONICAL` |
| DEBT-REVIEW | Review Gate | `doc/reviews/GOV-DEBT-CLEANUP-2-94c8dcdab-antigravity-r2.md` | `2636301fe` | `0af11140083d8ab9c38d80d38ef526a05ba3f8659be06f2513a5f5299e27531a` | `CANONICAL` |

## Resource Manifest

所有未知、dirty、独有提交、pinned 或个人数据资源保持原位。不得以本 Manifest 授权物理清理。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task file | `doc/tasks/GOV-DEBT-CLEANUP-2.md` | `NOT_APPLICABLE` | `doc/tasks/GOV-DEBT-CLEANUP-2.md` | `doc/tasks/GOV-DEBT-CLEANUP-2.md` | 本 Task 的容器文档，非被处置资源；自引用哈希无不动点，故不在此表 pin 自身，改由 Closeout Record 记录 ； 本 Task 唯一改动的治理文档；未改生产代码 |
| evidence dir | `verification/GOV-DEBT-CLEANUP-2/` | `PRESERVE_REFERENCED` | `verification/GOV-DEBT-CLEANUP-2/` | `f2db42f794f8185cc7a0f68cdf78d3a7ce80b2ddddb51151151dcf97a6ccd4a4` | 10 份证据，均为 AC 直接产物 |
| task worktree | 不存在 | `NOT_APPLICABLE` | — | `c8aa1df32c5c2250a3f2b1ad33adc5d30153fe489a9d089b7720333d688bba74` | 本 Task 直接在主线交付，无 linked worktree、无 source 分支、无 merge commit |
| gov checker | `tools/governance/check.ps1` | `PRESERVE_REFERENCED` | `tools/governance/check.ps1` | `296266d9e5dec5135e55bbf9bcc9b1d3345ffbf42aa9f5d5485693315bb34e49` | **本 Task 未修改**（仅 AC3 记录预算裁决，实际扩容由 GOV-PLAN-BUDGET-1 执行）|
| agent output | 仓外 agent-output，非本 Task 交付物 | `NOT_APPLICABLE` | — | `c8aa1df32c5c2250a3f2b1ad33adc5d30153fe489a9d089b7720333d688bba74` | codex r14 等派发产物不入库 |

## Closeout Record

- 关闭：2026-10-20。Owner=dsh，Reviewer=Antigravity。裁定：Codex r14。
- 终态：**`closed_with_limitations`**。AC1–AC6、AC8 达成；**AC7 仅完成 61 项候选分类，
  「唯一最终证据」判定未做**；AC9 由本次 closeout 完成。按 r13/r14 口径，未完成 AC 阻断 `done`。
- head 三元组：`reviewed_head=94c8dcdab`、`delivery_head=e63d932476`、
  `integration_source_head=2636301fe`。
- **集成方式：无需 merge。** 本 Task 从首次提交起就在目标主线
  `antigravity/P09-AC3-DELETE-HARDEN-1` 上，不存在独立 source 分支或 linked worktree，
  因此 `integration_commit` 记录为当前集成端点 `2636301fe`，并**明确它不是 merge commit**。
  这与 `GOV-RESOURCE-MANIFEST-JSON-1`、`P19-UI-MANIFEST-VIEW-1`、
  `GOV-RESOURCE-MANIFEST-SAME-LOCATION-1` 的 worktree→merge 拓扑不同，属可解释的执行差异。
- 治理：Task 检查与全局检查均 PASS。
- **本轮最重要的事实**：Review 抓出交付方一次**错误的「更正」**——dsh 曾把 AC1 汇总
  「更正」为 105 行，实测原记录 102 行（78/13/11）本来就正确；错误源于把汇总表自身 3 行
  计入数据行。已撤销并保留错误过程。AC4 的更正（23/18/5 → 25/21/4）则是真错误，经 Review 确认正确。
  **两者不可混为一谈**，本文件与 `ac1-sha-rows.md` 均已分开记录。
- 未关闭项（留债，不放弃）：AC7 的「唯一最终证据」判定 → 后继 Task `GOV-EVIDENCE-UNIQUE-1`
  （Owner: dsh，Reviewer: Antigravity），由 Codex 正式登记并释放。
- 删除 / 迁移 / 归档：**0 项**。
