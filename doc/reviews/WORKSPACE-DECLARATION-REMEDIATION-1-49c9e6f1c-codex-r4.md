---
task: WORKSPACE-DECLARATION-REMEDIATION-1-REVIEW-R4
reviewer: Codex
author: workspace-hardening
base_commit: f0f19596f
reviewed_head: 49c9e6f1c
implementation_head: 2deab2f07
decision: changes_requested
review_mode: read_only
---

## 1. 结论（A–F）

审查按指定的 `49c9e6f1c` / `2deab2f07` 固定提交进行。任务 worktree 当前已前进至 `f541c99`，包含证据修正提交 `a3bc20901` 和后续 Task-only 记录；以下同时标明这些后续变化。

| 项 | 判定 | 结论 |
|---|---|---|
| A. F-01 | 通过 | generalized junction 在 source 与 evidence pin 入口都保留 `DECL_GENERALIZED` 并报 fatal；纯 prose 才 warning。新增测试覆盖两个入口，记录显示未跳过。 |
| B. 快照 | 通过 | 4 个采集点的计数和内容摘要一致；我在只读主工作区复算出相同摘要。前后 audit 命令均有实际 `--out`。 |
| C. TRIAGE | 部分通过 | 6 条 generalized source 不再标为 destination；destination 错误也按 role 分开。仍有同一 role、同一 file+locator 的不同 code 被索引覆盖，导致一条 TRIAGE 分类错误。 |
| D. run_evidence | 通过 | runner 日志记录命令、cwd、parent shell、`shell=False` 和 exit；exit 文件为 `0`。本轮未重跑 runner。 |
| E. 真实性/回归 | 部分通过 | audit、测试、replay 和保护差异的已存证据相互吻合。指定 evidence commit 的 manifest 含两项未提交 `.pyc`；后续 `a3bc20901` 已修正 manifest 并重 pin。 |
| F. 残余与集成 | 残余裁定通过；暂不建议集成 | 76 条仍按 fail-closed 保留，没有为降低错误数放宽；TRIAGE 覆盖错误需修正，且审查锚点需更新到当前分支交付。 |

## 2. Findings

1. **P2 — TRIAGE 仍会覆盖同 role、同 file+locator 的不同 code。**  
   [build_reports.py](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/build_reports.py:128>) 的 `after_index` key 是 `(file, locator, role)`，同 key 后写入的 code 会覆盖先写入的 code。实证是 `doc/tasks/GOV-DEBT-CLEANUP-2.md`：after audit 同时有 `TABLE_ROW_ARITY` 与 `TABLE_SCHEMA_INCOMPLETE`，但 [TRIAGE.md 第 7 行](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/TRIAGE.md:7>) 把旧 `TABLE_ROW_ARITY` 行标成 `after: TABLE_SCHEMA_INCOMPLETE`。建议保留同 role 下的多条状态，并按原 code 或明确的 code 转换规则匹配；增加同 locator 多 code 的回归夹具。

2. **P2 — 指定 evidence commit 的 manifest 不完整；后续提交已修正。**  
   `2deab2f07` 的 `evidence/manifest.sha256` 有 32 行，其中 `__pycache__/build_reports.cpython-314.pyc` 和 `__pycache__/run_evidence.cpython-314.pyc` 不在该 commit 的 Git tree，无法从 pinned commit 复算。`49c9e6f1c` 中的 32 条 evidence pin 本身均通过 SHA-256 核对。后续 `a3bc20901` 移除了两项并更新 runner；当前 `f541c99` 的 32 条 pin 均指向 `a3bc20901` 且匹配，30 行 manifest 也全部可从该 commit 复算。

3. **审查锚点已落后于分支。**  
   当前任务 worktree HEAD 是 `f541c99`，Task 的 `delivery_head` 指向 `a3bc20901`，与请求的 `reviewed_head: 49c9e6f1c` / `implementation_head: 2deab2f07` 不同。集成前应以当前交付重新冻结审查锚点。

## 3. AC1–AC7 判定

| AC | 判定 | 依据 |
|---|---|---|
| AC1 | 部分通过 | TRIAGE 共 163 行，但同 role/code 覆盖造成上述一行分类错误。 |
| AC2 | 通过 | 本轮改动未削弱 JSON fail-closed 语义；记录显示新增测试通过。 |
| AC3 | 通过 | `_prose_probe` 保留非 prose 的原始 `GuardError`；source 与 evidence junction 测试都断言 `DECL_GENERALIZED` 且不落为 prose warning。见 [clean_workspace.py](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/tools/governance/clean_workspace.py:981>) 和 [测试](<G:/CODEX/New Manga.workspace/worktrees/WORKSPACE-DECLARATION-REMEDIATION-1/verification/WORKSPACE-DECLARATION-REMEDIATION-1/tests/test_declaration_remediation.py:304>)。 |
| AC4 | 通过 | 已存新测试日志记录 23 项通过；既有套件日志记录 80 项通过。本轮未执行测试。 |
| AC5 | 通过 | 测试日志包含 generalized destination 与 evidence junction fatal 案例；实际 audit 的 6 条 source generalized 保持 `DECL_GENERALIZED`。 |
| AC6 | 通过 | `RESIDUAL.md` 的 76 行与 `audit-after.json` 的 76 条错误逐项匹配，核对 code、file、locator、message 无遗漏或多项。 |
| AC7 | 部分通过 | 保存的双 replay、测试、保护差异和 runner 记录一致；指定 `2deab2f07` 的 manifest 有两项无法从该 commit 复算，后续 `a3bc20901` 已修复。 |

## 4. 残余裁定

after audit 为 **1858 declarations / 1264 roots / 76 errors / 236 warnings**，exit `2`。错误分类合计：44 `TABLE_SCHEMA_INCOMPLETE`、1 `TABLE_ROW_ARITY`、6 `DECL_GENERALIZED`、6 `DECL_DESTINATION_GENERALIZED`、1 `DECL_DESTINATION_UNRESOLVED`、6 `DECL_RELATIVE_UNRESOLVED`、1 `DECL_RELATIVE_AMBIGUOUS`、4 `DECL_ENV`、2 `DECL_UNKNOWN_DISPOSITION`、3 `FILE_UNREADABLE`、2 `JSON_PARSE`。

建议维持这 76 条为 fail-closed 残余：表结构、路径身份或文件内容尚未证明安全前继续拒绝；如需处理历史记录，应另行裁定或立项，不在本 Task 中降低错误数。Task 明确不以降数为目标；`protection_delta` 记录 dropped/added 均为 0。

双 replay 的存档日志记录各自 15/15 REJECT、0 删除、18/18 source coverage。base 到当前 evidence commit 的变更路径均在 `allowed_paths` 内，未发现删除路径或历史 Task/verification 路径改动。本轮没有执行 push、GC、prune。由于本地审查无法证明远端从未被直接推送，远端状态不作额外断言。

## 5. 运行证据

本轮只运行只读命令：

- `git status --short --branch`、`git rev-parse`、`git show`、`git diff --name-status`：exit `0`。任务 worktree 干净；主工作区当前有 1245 个 dirty entries。
- `python -B -c` 只读复算扫描快照：exit `0`。主工作区 HEAD 为 `f0f19596f`，tracked/untracked 为 `7416 / 1504`，共 8920 个文件；内容摘要与四个 snapshot points 的 `3187c41a…` 一致，unreadable 为 0。
- `python -B -c` 只读核对 evidence pins、manifest、audit、TRIAGE 和 RESIDUAL：exit `0`。32 条当前 pins 匹配；当前 30 行 manifest 全匹配；指定 `2deab2f07` manifest 缺两项 `.pyc`；76 条 residual 与 audit 逐项一致。
- `git diff --diff-filter=D f0f19596f..a3bc20901 --name-status`：exit `0`，无输出。
- 测试、真实 audit、incident replay、`run_evidence.py`、治理 checker：**NOT_RUN**。本轮仅检查已提交日志和 JSON；不将其表述为本轮实跑。
- push、GC、prune：**NOT_RUN**。

**建议下一步：**在当前分支修正 TRIAGE 同 role 多 code 的匹配并补回归测试，然后以 `a3bc20901` 及其后续提交为新审查锚点重新复核；修正前不进入集成。